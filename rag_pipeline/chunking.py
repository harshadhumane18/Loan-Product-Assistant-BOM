import json
import os
from pathlib import Path
from typing import List, Dict
import re


class RecursiveChunker:
    """
    Recursive chunking strategy that preserves semantic boundaries.
    Splits by sentences first, then paragraphs, then fixed size if needed.
    """
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """
        Args:
            chunk_size: Target chunk size in characters
            overlap: Character overlap between chunks for context preservation
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex patterns."""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]
    
    def split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Recursively chunk text while preserving semantic boundaries.
        Strategy: Sentences -> Paragraphs -> Fixed size
        """
        if not text or len(text) <= self.chunk_size:
            return [text] if text else []
        
        chunks = []
        current_chunk = ""
        
        sentences = self.split_into_sentences(text)
        
        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                if len(sentence) > self.chunk_size:
                    long_chunks = self._chunk_long_sentence(sentence)
                    chunks.extend(long_chunks)
                    current_chunk = ""
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        chunks = self._add_overlap(chunks)
        return chunks
    
    def _chunk_long_sentence(self, text: str) -> List[str]:
        """Chunk very long sentences by fixed size."""
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunks.append(text[i:i + self.chunk_size])
        return chunks
    
    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """Add overlap between consecutive chunks for context preservation."""
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = [chunks[0]]
        
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            curr_chunk = chunks[i]
            
            overlap_text = prev_chunk[-self.overlap:] if len(prev_chunk) >= self.overlap else prev_chunk
            combined = overlap_text + " " + curr_chunk
            overlapped_chunks.append(combined)
        
        return overlapped_chunks


class JSONLChunkingPipeline:
    """Pipeline to chunk JSONL documents for RAG."""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunker = RecursiveChunker(chunk_size=chunk_size, overlap=overlap)
    
    def process_jsonl_file(self, file_path: str) -> List[Dict]:
        """
        Process a JSONL file and return chunks with metadata.
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            List of chunk dictionaries with metadata
        """
        chunks_with_metadata = []
        chunk_id = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num} in {file_path}: {e}")
                    continue
                
                content = record.get('content', '')
                if not content:
                    continue
                
                text_chunks = self.chunker.chunk_text(content)
                
                for chunk_idx, chunk_text in enumerate(text_chunks):
                    chunk_metadata = {
                        'chunk_id': f"{Path(file_path).stem}_chunk_{chunk_id}",
                        'original_file': record.get('file_name', Path(file_path).name),
                        'section_index': record.get('section_index', 0),
                        'chunk_index': chunk_idx,
                        'content': chunk_text,
                        'scraped_date': record.get('scraped_date', ''),
                        'original_id': record.get('id', '')
                    }
                    chunks_with_metadata.append(chunk_metadata)
                    chunk_id += 1
        
        return chunks_with_metadata
    
    def process_directory(self, input_dir: str, output_dir: str) -> None:
        """
        Process all JSONL files in a directory and save chunks.
        
        Args:
            input_dir: Directory containing JSONL files
            output_dir: Directory to save chunked data
        """
        os.makedirs(output_dir, exist_ok=True)
        
        jsonl_files = list(Path(input_dir).glob('*.jsonl'))
        total_chunks = 0
        
        print(f"Processing {len(jsonl_files)} JSONL files...")
        
        for jsonl_file in sorted(jsonl_files):
            print(f"  Chunking: {jsonl_file.name}")
            chunks = self.process_jsonl_file(str(jsonl_file))
            
            output_file = Path(output_dir) / f"chunks_{jsonl_file.stem}.jsonl"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for chunk in chunks:
                    f.write(json.dumps(chunk) + '\n')
            
            total_chunks += len(chunks)
            print(f"    Generated {len(chunks)} chunks")
        
        print(f"\nTotal chunks generated: {total_chunks}")
        print(f"Chunks saved to: {output_dir}")


if __name__ == "__main__":
    input_directory = "../data/processed_data"
    output_directory = "../data/chunks"
    
    pipeline = JSONLChunkingPipeline(chunk_size=512, overlap=50)
    pipeline.process_directory(input_directory, output_directory)
