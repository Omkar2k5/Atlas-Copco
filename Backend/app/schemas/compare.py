"""
Pydantic schemas for comparison endpoints.
"""

from pydantic import BaseModel, Field
from typing import List


class CompareRequest(BaseModel):
    """Request model for comparing two sessions."""
    
    session_id_reference: str = Field(..., description="Reference session ID")
    session_id_user: str = Field(..., description="User session ID to compare")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id_reference": "123e4567-e89b-12d3-a456-426614174000",
                "session_id_user": "987f6543-e21c-45d6-b789-123456789abc"
            }
        }


class CompareResponse(BaseModel):
    """Response model for comparison results."""
    
    similarity_score: float = Field(
        ..., 
        description="Cosine similarity between embeddings (0-1)",
        ge=0.0,
        le=1.0
    )
    time_difference_seconds: float = Field(
        ..., 
        description="Time difference: user_duration - reference_duration"
    )
    movement_deviation_vector: List[float] = Field(
        ..., 
        description="Per-joint deviation scores"
    )
    stressed_joints: List[str] = Field(
        ..., 
        description="Joints exceeding deviation or ergonomic thresholds"
    )
    recommended_improvements: List[str] = Field(
        ..., 
        description="Actionable recommendations based on analysis"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "similarity_score": 0.85,
                "time_difference_seconds": -2.3,
                "movement_deviation_vector": [0.1, 0.2, 0.15],
                "stressed_joints": ["left_shoulder", "neck"],
                "recommended_improvements": [
                    "Keep your head aligned with your spine to reduce neck strain",
                    "Relax your left shoulder - avoid unnecessary elevation"
                ]
            }
        }
