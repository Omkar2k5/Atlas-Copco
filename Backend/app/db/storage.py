"""
Local JSON Storage Module
Stores session metadata including keypoints and computed data.
"""

import json
import os
from typing import Dict, Optional, List
from datetime import datetime
import uuid


class SessionStorage:
    """Local JSON file-based storage for session data."""
    
    def __init__(self, storage_dir: str = "./session_data"):
        """
        Initialize session storage.
        
        Args:
            storage_dir: Directory to store session JSON files
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def _get_session_path(self, session_id: str) -> str:
        """Get the file path for a session."""
        return os.path.join(self.storage_dir, f"{session_id}.json")
    
    def create_session(
        self,
        keypoints: List[List[List[float]]],
        embedding: List[float],
        duration_seconds: float,
        video_path: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Create a new session and store its data.
        
        Args:
            keypoints: Extracted keypoints
            embedding: Computed embedding vector
            duration_seconds: Video duration
            video_path: Original video path
            user_id: Optional user identifier
            
        Returns:
            Generated session_id
        """
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "video_path": video_path,
            "duration_seconds": duration_seconds,
            "keypoints": keypoints,
            "embedding": embedding,
            "step_segments": None  # Placeholder for future implementation
        }
        
        session_path = self._get_session_path(session_id)
        with open(session_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve session data by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data dictionary or None if not found
        """
        session_path = self._get_session_path(session_id)
        
        if not os.path.exists(session_path):
            return None
        
        try:
            with open(session_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def update_session(self, session_id: str, updates: Dict) -> bool:
        """
        Update session data with new information.
        
        Args:
            session_id: Session identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        session_data = self.get_session(session_id)
        
        if session_data is None:
            return False
        
        session_data.update(updates)
        
        session_path = self._get_session_path(session_id)
        with open(session_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        session_path = self._get_session_path(session_id)
        
        if os.path.exists(session_path):
            os.remove(session_path)
            return True
        return False
    
    def list_sessions(self, user_id: Optional[str] = None) -> List[Dict]:
        """
        List all sessions, optionally filtered by user.
        
        Args:
            user_id: Optional user filter
            
        Returns:
            List of session metadata (without full keypoints)
        """
        sessions = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                session_id = filename[:-5]  # Remove .json extension
                session_data = self.get_session(session_id)
                
                if session_data:
                    # Filter by user if specified
                    if user_id is None or session_data.get("user_id") == user_id:
                        # Return metadata only (exclude large keypoints array)
                        sessions.append({
                            "session_id": session_data["session_id"],
                            "timestamp": session_data["timestamp"],
                            "user_id": session_data.get("user_id"),
                            "duration_seconds": session_data["duration_seconds"]
                        })
        
        return sessions


# Global storage instance
_storage: Optional[SessionStorage] = None


def get_storage() -> SessionStorage:
    """Get or create the global session storage instance."""
    global _storage
    if _storage is None:
        _storage = SessionStorage()
    return _storage
