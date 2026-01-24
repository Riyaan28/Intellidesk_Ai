"""
Embeddings & Similarity Module
Vector embeddings for semantic search and deduplication
"""

import google.generativeai as genai
import numpy as np
from typing import List, Dict, Tuple
import faiss
import pickle
import os
from .ai_config import (
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL,
    VECTOR_DB_PATH,
    EMBEDDING_DIMENSION,
    SIMILARITY_THRESHOLD
)

genai.configure(api_key=GEMINI_API_KEY)


class EmbeddingService:
    """
    Handles vector embeddings and similarity search
    Uses Gemini Embeddings + FAISS for fast similarity search
    """
    
    def __init__(self):
        self.embedding_model = GEMINI_EMBEDDING_MODEL
        self.dimension = EMBEDDING_DIMENSION
        self.index = None
        self.metadata = []  # Store ticket IDs and info
        self._initialize_index()
    
    def _initialize_index(self):
        """
        Initialize or load FAISS index
        """
        index_path = f"{VECTOR_DB_PATH}/faiss.index"
        metadata_path = f"{VECTOR_DB_PATH}/metadata.pkl"
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            # Load existing index
            self.index = faiss.read_index(index_path)
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            # Create new index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
            os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for text using Gemini
        
        Args:
            text: Input text
            
        Returns:
            numpy array of embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            embedding = np.array(result['embedding'], dtype=np.float32)
            
            # Ensure correct dimension
            if len(embedding) != self.dimension:
                # Pad or truncate
                if len(embedding) < self.dimension:
                    embedding = np.pad(embedding, (0, self.dimension - len(embedding)))
                else:
                    embedding = embedding[:self.dimension]
            
            return embedding
            
        except Exception as e:
            # Return zero vector on error
            print(f"Embedding error: {e}")
            return np.zeros(self.dimension, dtype=np.float32)
    
    def add_ticket(self, ticket_id: str, subject: str, body: str, resolution: str = "") -> None:
        """
        Add a ticket to the vector database
        
        Args:
            ticket_id: Unique ticket identifier
            subject: Ticket subject
            body: Ticket body/description
            resolution: Resolution text (if resolved)
        """
        # Combine text for embedding
        text = f"{subject} {body} {resolution}"
        embedding = self.get_embedding(text)
        
        # Add to index
        self.index.add(np.array([embedding]))
        
        # Add metadata
        self.metadata.append({
            'ticket_id': ticket_id,
            'subject': subject,
            'body': body,
            'resolution': resolution
        })
        
        # Save index
        self._save_index()
    
    def search_similar(
        self,
        subject: str,
        body: str,
        top_k: int = 5,
        threshold: float = SIMILARITY_THRESHOLD
    ) -> List[Dict]:
        """
        Search for similar tickets
        
        Args:
            subject: Query subject
            body: Query body
            top_k: Number of results to return
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar tickets with similarity scores
        """
        if self.index.ntotal == 0:
            return []
        
        # Get query embedding
        query_text = f"{subject} {body}"
        query_embedding = self.get_embedding(query_text)
        
        # Search
        distances, indices = self.index.search(np.array([query_embedding]), top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                # Convert L2 distance to similarity score (0-1)
                similarity = 1 / (1 + dist)
                
                if similarity >= threshold:
                    result = self.metadata[idx].copy()
                    result['similarity'] = float(similarity)
                    results.append(result)
        
        return results
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts
        
        Returns:
            Similarity score (0-1)
        """
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        
        # Cosine similarity
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    
    def _save_index(self):
        """
        Save FAISS index and metadata to disk
        """
        os.makedirs(VECTOR_DB_PATH, exist_ok=True)
        
        index_path = f"{VECTOR_DB_PATH}/faiss.index"
        metadata_path = f"{VECTOR_DB_PATH}/metadata.pkl"
        
        faiss.write_index(self.index, index_path)
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def get_stats(self) -> Dict:
        """
        Get vector database statistics
        """
        return {
            'total_tickets': self.index.ntotal,
            'dimension': self.dimension,
            'metadata_count': len(self.metadata)
        }


# Singleton instance
embedding_service = EmbeddingService()
