"""
Pydantic schemas for pose processing endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ProcessVideoResponse(BaseModel):
    """Response model for video processing endpoint."""
    
    session_id: str = Field(..., description="Unique session identifier")
    keypoints: List[List[List[float]]] = Field(
        ..., 
        description="Extracted keypoints: [frame][joint][x, y, confidence]"
    )
    embedding: List[float] = Field(..., description="Fixed-length embedding vector")
    step_segments: Optional[List] = Field(
        None, 
        description="Placeholder for future step segmentation"
    )
    duration_seconds: float = Field(..., description="Video duration in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "keypoints": [[[0.5, 0.5, 0.9], [0.6, 0.4, 0.95]]],
                "embedding": [0.1, 0.2, 0.3],
                "step_segments": None,
                "duration_seconds": 15.5
            }
        }
