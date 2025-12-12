import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
import time
import google.api_core.exceptions 
from dotenv import load_dotenv
    
load_dotenv()

# helper to wrap generate_content with retry/backoff for 429s
def _safe_generate(self, prompt: str, retries: int = 2, backoff: float = 1.5):
    last_exc = None
    for attempt in range(retries + 1):
        try:
            return self.client.generate_content(prompt)
        except google.api_core.exceptions.ResourceExhausted as exc:
            last_exc = exc
            # avoid hammering the free-tier; back off
            sleep_s = backoff ** attempt
            time.sleep(sleep_s)
        except Exception as exc:
            last_exc = exc
            break
    raise last_exc


class RAGState(TypedDict):
    query: str               # original
    working_query: str       # possibly rephrased
    needs_reform: bool
    context: Optional[List[Dict]]
    response: Optional[str]


class VectorStoreManager:
    """Manages FAISS vector store loading and retrieval."""
    
    def __init__(self, vector_store_dir: str, model_name: str = "all-MiniLM-L6-v2"):
        self.vector_store_dir = vector_store_dir
        self.model_name = model_name
        self.embedding_model = SentenceTransformer(model_name, device="cpu")
        self.index = None
        self.metadata = []
        self._load_vector_store()
    
    def _load_vector_store(self):
        """Load FAISS index and metadata."""
        index_path = os.path.join(self.vector_store_dir, "faiss_index.bin")
        metadata_path = os.path.join(self.vector_store_dir, "metadata.jsonl")
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Vector store files not found in {self.vector_store_dir}")
        
        self.index = faiss.read_index(index_path)
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.metadata.append(json.loads(line))
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve top-k similar chunks for the query."""
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)[0]
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                chunk = self.metadata[idx].copy()
                chunk['similarity_score'] = float(1 / (1 + distance))
                results.append(chunk)
        
        return results


class AgenticRAGPipeline:
    def __init__(self, vector_store_dir: str, gemini_api_key: str, model_name: str = "gemini-2.5-flash"):
        self.vector_store = VectorStoreManager(vector_store_dir)
        self.model_name = model_name
        genai.configure(api_key=gemini_api_key)
        self.client = genai.GenerativeModel(model_name)
        self._safe_generate = _safe_generate.__get__(self)
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(RAGState)
        workflow.add_node("analyzer", self._analyzer)
        workflow.add_node("reformer", self._reformer)
        workflow.add_node("retriever", self._retriever)
        workflow.add_node("responder", self._responder)
        workflow.set_entry_point("analyzer")
        workflow.add_conditional_edges(
            "analyzer",
            lambda s: "reform" if s["needs_reform"] else "retrieve",
            {"reform": "reformer", "retrieve": "retriever"},
        )
        workflow.add_edge("reformer", "retriever")
        workflow.add_edge("retriever", "responder")
        workflow.add_edge("responder", END)
        return workflow.compile()

    def _analyzer(self, state: RAGState) -> RAGState:
        q = state["query"].strip()
        # Minimal heuristic: if very short or has no space (likely too terse), reformulate
        needs_reform = (len(q) < 5) or (" " not in q)
        state["needs_reform"] = needs_reform
        state["working_query"] = q
        return state

    def _reformer(self, state: RAGState) -> RAGState:
        q = state["query"]
        prompt = f"""Rewrite this user query to be clear and specific about Bank of Maharashtra loan products. Keep it concise.
Query: "{q}"
Rewritten:"""
        resp = self._safe_generate(prompt)
        rewritten = resp.text.strip() or q
        state["working_query"] = rewritten
        return state

    def _retriever(self, state: RAGState) -> RAGState:
        wq = state["working_query"]
        state["context"] = self.vector_store.retrieve(wq, k=5)
        return state

    def _responder(self, state: RAGState) -> RAGState:
        wq = state["working_query"]
        context = state["context"] or []
        context_text = "\n\n".join([f"[Source {i+1}] {c['content']}" for i, c in enumerate(context)])
        prompt = f"""You are a helpful assistant for Bank of Maharashtra loan products.
Use only the provided context. Give a clear, concise, but descriptive answer (2–4 sentences), and include key comparisons or conditions if relevant.

Context:
{context_text}

User Query: {wq}

Answer with a short, well-structured explanation:"""
        resp = self._safe_generate(prompt)
        state["response"] = resp.text
        return state

    def process_query(self, query: str) -> Dict[str, Any]:
        init: RAGState = {
            "query": query,
            "working_query": query,
            "needs_reform": False,
            "context": None,
            "response": None,
        }
        result = self.graph.invoke(init)
        return {
            "query": result["query"],
            "working_query": result["working_query"],
            "needs_reform": result["needs_reform"],
            "context_count": len(result.get("context", [])) if result.get("context") else 0,
            "response": result.get("response"),
            "context": result.get("context", []) if result.get("context") else [],
        }


# if __name__ == "__main__":
#     vector_store_path = "../data/vector_store"
#     api_key = os.getenv("GEMINI_API_KEY")
    
#     if not api_key:
#         raise ValueError("GEMINI_API_KEY environment variable not set")
    
#     pipeline = AgenticRAGPipeline(vector_store_path, api_key)
    
#     test_queries = [
#         "What is machine learning?",
#         "Explain how neural networks work and why they are effective",
#         "xyz",
#     ]
    
#     for query in test_queries:
#         print(f"\n{'='*60}")
#         print(f"Query: {query}")
#         print(f"{'='*60}")
#         result = pipeline.process_query(query)
#         print(f"Query Type: {result['query_type']}")
#         print(f"Needs Clarification: {result['clarification_needed']}")
#         print(f"Reasoning Required: {result['reasoning_required']}")
#         print(f"Context Retrieved: {result['context_count']}")
#         print(f"\nResponse:\n{result['response']}")


if __name__ == "__main__":
    import os

    vector_store_path = os.path.join(os.path.dirname(__file__), "..", "data", "vector_store")
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("🚨 ERROR: GEMINI_API_KEY environment variable not set.")
        # Optionally exit or prompt for input
        exit(1)
    
    # --- Initialization ---
    try:
        pipeline = AgenticRAGPipeline(vector_store_path, api_key)
        print("--- Loan Product Assistant Initialized ---")
        print("Model: Gemini 2.5 Flash | RAG Backend: FAISS")
        print("Ask a question about Bank of Maharashtra loan products.")
        print("Type 'quit' or 'stop' to exit.\n")
    except Exception as e:
        print(f"Failed to initialize RAG Pipeline: {e}")
        exit(1)
        
    # --- Interactive Loop ---
    while True:
        try:
            # 1. Get User Input
            user_input = input("👤 You: ").strip()
            
            # 2. Check for Exit Commands
            if user_input.lower() in ["quit", "stop", "exit"]:
                print("\n👋 Thank you for using the Loan Product Assistant. Goodbye!")
                break
            
            if not user_input:
                continue # Skip empty input
            
            # 3. Process Query
            # We use the pipeline you built
            result = pipeline.process_query(user_input)
            
            print("\n*** RAG WORKFLOW LOG ***")
            print(f"| Needs Reform: {result.get('needs_reform', False)}")
            print(f"| Working Query: {result.get('working_query', '')}")
            print(f"| Context Chunks Retrieved: {result.get('context_count', 0)}")
            print("*************************")
            print(f"💡 Assistant: {result.get('response', 'No response')}\n")

            # 5. Display Assistant Response
            response_text = result.get('response', 'I am unable to process this request right now.')
            # print(f"💡 Assistant: {response_text}\n")
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\n👋 Thank you for using the Loan Product Assistant. Goodbye!")
            break
        except Exception as e:
            # Handle unexpected errors during the run
            print(f"\n🚨 An error occurred: {e}")
            print("Please try your query again or type 'quit' to exit.\n")
