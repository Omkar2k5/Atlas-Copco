"""
Embedding Generation Module
Converts variable-length keypoint sequences into fixed-length vector embeddings.
"""

import numpy as np
from typing import List


def calculate_joint_angles(keypoints: List[List[List[float]]]) -> np.ndarray:
    """
    Calculate joint angles for each frame.
    
    Args:
        keypoints: List[frame][joint][x, y, confidence]
        
    Returns:
        Array of shape (num_frames, num_angles) containing joint angles
    """
    angles_per_frame = []
    
    for frame_kpts in keypoints:
        frame_angles = []
        
        # Convert to numpy for easier computation
        kpts = np.array(frame_kpts)[:, :2]  # Take only x, y
        
        # Define joint triplets for angle calculation (parent, joint, child)
        # MoveNet indices (17 keypoints)
        angle_triplets = [
            # Arms
            (5, 7, 9),    # left shoulder, elbow, wrist
            (6, 8, 10),   # right shoulder, elbow, wrist
            # Legs
            (11, 13, 15), # left hip, knee, ankle
            (12, 14, 16), # right hip, knee, ankle
            # Torso
            (5, 11, 13),  # left shoulder, hip, knee
            (6, 12, 14),  # right shoulder, hip, knee
            # Neck/Shoulder
            (0, 5, 7),    # nose, left shoulder, left elbow
            (0, 6, 8),    # nose, right shoulder, right elbow
        ]
        
        for p1_idx, p2_idx, p3_idx in angle_triplets:
            p1, p2, p3 = kpts[p1_idx], kpts[p2_idx], kpts[p3_idx]
            
            # Calculate vectors
            v1 = p1 - p2
            v2 = p3 - p2
            
            # Calculate angle using dot product
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
            angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
            frame_angles.append(angle)
        
        angles_per_frame.append(frame_angles)
    
    return np.array(angles_per_frame)


def calculate_velocity_features(keypoints: List[List[List[float]]]) -> np.ndarray:
    """
    Calculate velocity features (frame-to-frame movement).
    
    Args:
        keypoints: List[frame][joint][x, y, confidence]
        
    Returns:
        Velocity features array
    """
    kpts_array = np.array(keypoints)[:, :, :2]  # (frames, joints, 2)
    
    # Calculate frame-to-frame differences
    velocities = np.diff(kpts_array, axis=0)
    
    # Calculate velocity magnitude per joint
    velocity_magnitudes = np.linalg.norm(velocities, axis=2)  # (frames-1, joints)
    
    return velocity_magnitudes


def sequence_to_embedding(keypoints: List[List[List[float]]]) -> List[float]:
    """
    Convert variable-length keypoint sequence to fixed-length embedding vector.
    
    Strategy:
    1. Calculate joint angles for each frame
    2. Calculate velocity features
    3. Compute statistical features (mean, std, min, max) across time
    4. Flatten into single embedding vector
    
    Args:
        keypoints: List[frame][joint][x, y, confidence]
        
    Returns:
        Fixed-length embedding vector as list
    """
    if not keypoints or len(keypoints) == 0:
        # Return zero embedding if no keypoints
        return [0.0] * 256
    
    # Calculate joint angles
    angles = calculate_joint_angles(keypoints)  # (num_frames, num_angles)
    
    # Calculate velocity features
    velocities = calculate_velocity_features(keypoints)  # (num_frames-1, num_joints)
    
    # Statistical aggregation
    features = []
    
    # Angle statistics
    if angles.shape[0] > 0:
        features.extend(np.mean(angles, axis=0).tolist())
        features.extend(np.std(angles, axis=0).tolist())
        features.extend(np.min(angles, axis=0).tolist())
        features.extend(np.max(angles, axis=0).tolist())
    
    # Velocity statistics
    if velocities.shape[0] > 0:
        features.extend(np.mean(velocities, axis=0).tolist())
        features.extend(np.std(velocities, axis=0).tolist())
    
    # Positional statistics (using raw keypoints)
    kpts_array = np.array(keypoints)[:, :, :2]  # (frames, joints, 2)
    features.extend(np.mean(kpts_array, axis=0).flatten().tolist())
    features.extend(np.std(kpts_array, axis=0).flatten().tolist())
    
    # Pad or truncate to fixed size (256 dimensions)
    target_size = 256
    if len(features) < target_size:
        features.extend([0.0] * (target_size - len(features)))
    else:
        features = features[:target_size]
    
    return features


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        Similarity score between 0 and 1
    """
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = dot_product / (norm1 * norm2)
    
    # Convert from [-1, 1] to [0, 1]
    return (similarity + 1.0) / 2.0
