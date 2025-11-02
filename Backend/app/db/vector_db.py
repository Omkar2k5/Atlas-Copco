"""
Vector Database Module using ChromaDB
Stores and retrieves pose embeddings with metadata.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import os


class VectorDatabase:
    """ChromaDB wrapper for pose embedding storage."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB client and collection.
        
        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = persist_directory
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with new API (v0.4+)
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="poses",
            metadata={"description": "Human pose embeddings for motion analysis"}
        )
    
    def insert_embedding(
        self,
        session_id: str,
        embedding: List[float],
        metadata: Dict
    ) -> None:
        """
        Insert a pose embedding into the database.
        
        Args:
            session_id: Unique session identifier
            embedding: Pose embedding vector
            metadata: Additional metadata (user, timestamp, duration, etc.)
        """
        self.collection.add(
            embeddings=[embedding],
            ids=[session_id],
            metadatas=[metadata]
        )
        # PersistentClient automatically persists
    
    def query_embedding(
        self,
        embedding: List[float],
        n_results: int = 5
    ) -> Dict:
        """
        Query similar embeddings from the database.
        
        Args:
            embedding: Query embedding vector
            n_results: Number of results to return
            
        Returns:
            Query results with ids, distances, and metadatas
        """
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )
        
        return results
    
    def get_embedding(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve embedding and metadata by session ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with embedding and metadata, or None if not found
        """
        try:
            result = self.collection.get(
                ids=[session_id],
                include=["embeddings", "metadatas"]
            )
            
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "embedding": result["embeddings"][0],
                    "metadata": result["metadatas"][0]
                }
            return None
        except Exception:
            return None
    
    def delete_embedding(self, session_id: str) -> None:
        """
        Delete an embedding by session ID.
        
        Args:
            session_id: Session identifier
        """
        self.collection.delete(ids=[session_id])
        # PersistentClient automatically persists
    
    def count(self) -> int:
        """Return the number of embeddings in the collection."""
        return self.collection.count()


# Global database instance
_vector_db: Optional[VectorDatabase] = None


def get_vector_db() -> VectorDatabase:
    """Get or create the global vector database instance."""
    global _vector_db
    if _vector_db is None:
        _vector_db = VectorDatabase()
    return _vector_db
