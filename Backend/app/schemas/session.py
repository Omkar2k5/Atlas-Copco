"""
Pydantic schemas for session management endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SessionResponse(BaseModel):
    """Response model for session retrieval."""
    
    session_id: str = Field(..., description="Unique session identifier")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    video_path: Optional[str] = Field(None, description="Original video path")
    duration_seconds: float = Field(..., description="Video duration in seconds")
    keypoints: List[List[List[float]]] = Field(
        ..., 
        description="Extracted keypoints"
    )
    embedding: List[float] = Field(..., description="Computed embedding vector")
    step_segments: Optional[List] = Field(
        None, 
        description="Placeholder for step segmentation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-15T10:30:00.000Z",
                "user_id": "user123",
                "video_path": "/uploads/video.mp4",
                "duration_seconds": 15.5,
                "keypoints": [[[0.5, 0.5, 0.9]]],
                "embedding": [0.1, 0.2, 0.3],
                "step_segments": None
            }
        }


class SessionListResponse(BaseModel):
    """Response model for listing sessions."""
    
    sessions: List[dict] = Field(..., description="List of session metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sessions": [
                    {
                        "session_id": "123e4567-e89b-12d3-a456-426614174000",
                        "timestamp": "2024-01-15T10:30:00.000Z",
                        "user_id": "user123",
                        "duration_seconds": 15.5
                    }
                ]
            }
        }
