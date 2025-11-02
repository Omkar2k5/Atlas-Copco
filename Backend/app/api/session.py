"""
Session API Endpoints
Handles session retrieval and listing operations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.session import SessionResponse, SessionListResponse
from app.db.storage import get_storage


router = APIRouter()


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    Retrieve a session by ID.
    
    Returns all session data including keypoints, embeddings, and metadata.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        SessionResponse with complete session data
    """
    storage = get_storage()
    session_data = storage.get_session(session_id)
    
    if session_data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found: {session_id}"
        )
    
    return SessionResponse(**session_data)


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    List all sessions with optional user filtering.
    
    Returns session metadata (without full keypoints to reduce payload size).
    
    Args:
        user_id: Optional user ID filter
        
    Returns:
        SessionListResponse with list of session metadata
    """
    storage = get_storage()
    sessions = storage.list_sessions(user_id=user_id)
    
    return SessionListResponse(sessions=sessions)


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session by ID.
    
    Removes session data from both JSON storage and vector database.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Success message
    """
    storage = get_storage()
    
    # Check if session exists
    if storage.get_session(session_id) is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found: {session_id}"
        )
    
    # Delete from storage
    storage.delete_session(session_id)
    
    # Also delete from vector database
    from app.db.vector_db import get_vector_db
    vector_db = get_vector_db()
    vector_db.delete_embedding(session_id)
    
    return {"message": f"Session {session_id} deleted successfully"}
