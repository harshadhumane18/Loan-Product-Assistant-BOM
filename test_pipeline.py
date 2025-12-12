import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from rag_pipeline.agentic_rag import AgenticRAGPipeline


def test_agentic_rag_pipeline():
    """Test the agentic RAG pipeline."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        print("Please set it before running this test:")
        print("  Windows: set GEMINI_API_KEY=your_key_here")
        print("  Linux/Mac: export GEMINI_API_KEY=your_key_here")
        return False
    
    vector_store_path = os.path.join(
        os.path.dirname(__file__),
        "data",
        "vector_store"
    )
    
    if not os.path.exists(vector_store_path):
        print(f"ERROR: Vector store not found at {vector_store_path}")
        return False
    
    print("=" * 70)
    print("AGENTIC RAG PIPELINE TEST")
    print("=" * 70)
    
    try:
        print("\n[1] Initializing pipeline...")
        pipeline = AgenticRAGPipeline(vector_store_path, api_key)
        print("✓ Pipeline initialized successfully")
        
        print("\n[2] Testing with sample queries...")
        
        test_queries = [
            "What is machine learning?",
            "Explain how neural networks work",
            "xyz"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'-' * 70}")
            print(f"Test {i}: {query}")
            print(f"{'-' * 70}")
            
            result = pipeline.process_query(query)
            
            print(f"Query Type: {result['query_type']}")
            print(f"Clarification Needed: {result['clarification_needed']}")
            print(f"Reasoning Required: {result['reasoning_required']}")
            print(f"Context Retrieved: {result['context_count']} chunks")
            print(f"\nResponse:\n{result['response'][:500]}...")
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_agentic_rag_pipeline()
    sys.exit(0 if success else 1)
