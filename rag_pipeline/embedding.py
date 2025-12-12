import json
import os
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import faiss
from sentence_transformers import SentenceTransformer
import pickle


class EmbeddingPipeline:
    """
    Embedding pipeline using Sentence Transformers and FAISS.
    Uses 'all-MiniLM-L6-v2' model: lightweight (22M params), fast, excellent for RAG.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        """
        Initialize embedding model.
        
        Args:
            model_name: Sentence Transformers model to use
            device: 'cpu' or 'cuda' for GPU acceleration
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.model_name = model_name
        print(f"Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Embed a list of texts using the model.
        
        Args:
            texts: List of text strings to embed
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of embeddings (n_texts, embedding_dim)
        """
        print(f"Embedding {len(texts)} texts with batch size {batch_size}...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings
    
    def create_faiss_index(self, embeddings: np.ndarray, use_gpu: bool = False) -> faiss.Index:
        """
        Create FAISS index from embeddings.
        Uses IVF (Inverted File) for scalable similarity search.
        
        Args:
            embeddings: Numpy array of embeddings
            use_gpu: Whether to use GPU (requires faiss-gpu)
            
        Returns:
            FAISS index object
        """
        print(f"Creating FAISS index for {len(embeddings)} embeddings...")
        
        embeddings = embeddings.astype('float32')
        
        n_embeddings = len(embeddings)
        embedding_dim = embeddings.shape[1]
        
        if n_embeddings < 100:
            index = faiss.IndexFlatL2(embedding_dim)
        else:
            n_clusters = min(int(np.sqrt(n_embeddings)), 100)
            quantizer = faiss.IndexFlatL2(embedding_dim)
            index = faiss.IndexIVFFlat(quantizer, embedding_dim, n_clusters)
            index.train(embeddings)
        
        index.add(embeddings)
        
        print(f"FAISS index created with {index.ntotal} vectors")
        return index


class FAISSVectorStore:
    """Manages FAISS vector store with metadata."""
    
    def __init__(self, embedding_pipeline: EmbeddingPipeline):
        self.embedding_pipeline = embedding_pipeline
        self.index = None
        self.metadata = []
        self.id_to_metadata = {}
    
    def add_chunks(self, chunks: List[Dict]) -> None:
        """
        Add chunks to the vector store.
        
        Args:
            chunks: List of chunk dictionaries with 'content' key
        """
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.embedding_pipeline.embed_texts(texts)
        
        if self.index is None:
            self.index = self.embedding_pipeline.create_faiss_index(embeddings)
        else:
            embeddings = embeddings.astype('float32')
            self.index.add(embeddings)
        
        for idx, chunk in enumerate(chunks):
            chunk_id = chunk.get('chunk_id', f"chunk_{len(self.metadata)}")
            self.id_to_metadata[len(self.metadata)] = chunk_id
            self.metadata.append(chunk)
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Search for similar chunks.
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List of (chunk_metadata, distance) tuples
        """
        if self.index is None:
            raise ValueError("Vector store is empty. Add chunks first.")
        
        query_embedding = self.embedding_pipeline.embed_texts([query])[0]
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                results.append((self.metadata[idx], float(distance)))
        
        return results
    
    def save(self, save_dir: str) -> None:
        """
        Save FAISS index and metadata.
        
        Args:
            save_dir: Directory to save index and metadata
        """
        os.makedirs(save_dir, exist_ok=True)
        
        if self.index is None:
            raise ValueError("No index to save")
        
        index_path = os.path.join(save_dir, "faiss_index.bin")
        metadata_path = os.path.join(save_dir, "metadata.jsonl")
        config_path = os.path.join(save_dir, "config.json")
        
        faiss.write_index(self.index, index_path)
        print(f"FAISS index saved to: {index_path}")
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            for metadata in self.metadata:
                f.write(json.dumps(metadata) + '\n')
        print(f"Metadata saved to: {metadata_path}")
        
        config = {
            'model_name': self.embedding_pipeline.model_name,
            'embedding_dim': self.embedding_pipeline.embedding_dim,
            'num_vectors': self.index.ntotal,
            'num_chunks': len(self.metadata)
        }
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Config saved to: {config_path}")
    
    @staticmethod
    def load(save_dir: str, embedding_pipeline: EmbeddingPipeline) -> 'FAISSVectorStore':
        """
        Load FAISS index and metadata.
        
        Args:
            save_dir: Directory containing saved index and metadata
            embedding_pipeline: EmbeddingPipeline instance
            
        Returns:
            Loaded FAISSVectorStore instance
        """
        vector_store = FAISSVectorStore(embedding_pipeline)
        
        index_path = os.path.join(save_dir, "faiss_index.bin")
        metadata_path = os.path.join(save_dir, "metadata.jsonl")
        
        vector_store.index = faiss.read_index(index_path)
        print(f"FAISS index loaded from: {index_path}")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            for line in f:
                metadata = json.loads(line)
                vector_store.metadata.append(metadata)
        print(f"Metadata loaded: {len(vector_store.metadata)} chunks")
        
        return vector_store


class EmbeddingPipelineExecutor:
    """Main executor for the embedding pipeline."""
    
    def __init__(self, chunks_dir: str, output_dir: str, model_name: str = "all-MiniLM-L6-v2"):
        """
        Args:
            chunks_dir: Directory containing chunked JSONL files
            output_dir: Directory to save FAISS index and metadata
            model_name: Sentence Transformers model name
        """
        self.chunks_dir = chunks_dir
        self.output_dir = output_dir
        self.embedding_pipeline = EmbeddingPipeline(model_name=model_name)
        self.vector_store = FAISSVectorStore(self.embedding_pipeline)
    
    def load_chunks_from_directory(self) -> List[Dict]:
        """Load all chunks from JSONL files in chunks directory."""
        all_chunks = []
        chunk_files = list(Path(self.chunks_dir).glob('chunks_*.jsonl'))
        
        print(f"Loading chunks from {len(chunk_files)} files...")
        
        for chunk_file in sorted(chunk_files):
            with open(chunk_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        chunk = json.loads(line)
                        all_chunks.append(chunk)
        
        print(f"Total chunks loaded: {len(all_chunks)}")
        return all_chunks
    
    def execute(self) -> None:
        """Execute the complete embedding pipeline."""
        print("=" * 60)
        print("RAG EMBEDDING PIPELINE")
        print("=" * 60)
        
        chunks = self.load_chunks_from_directory()
        
        if not chunks:
            print("No chunks found. Run chunking.py first.")
            return
        
        self.vector_store.add_chunks(chunks)
        self.vector_store.save(self.output_dir)
        
        print("\n" + "=" * 60)
        print("EMBEDDING PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Vector store saved to: {self.output_dir}")
        print(f"Total chunks embedded: {len(chunks)}")
        print(f"Embedding model: {self.embedding_pipeline.model_name}")
        print(f"Embedding dimension: {self.embedding_pipeline.embedding_dim}")


if __name__ == "__main__":
    chunks_directory = "../data/chunks"
    output_directory = "../data/vector_store"
    
    executor = EmbeddingPipelineExecutor(
        chunks_dir=chunks_directory,
        output_dir=output_directory,
        model_name="all-MiniLM-L6-v2"
    )
    executor.execute()
