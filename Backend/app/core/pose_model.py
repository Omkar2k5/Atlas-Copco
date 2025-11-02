"""
Pose Estimation Model Handler using MoveNet Thunder
Extracts keypoints from video frames and normalizes them.
"""

import cv2
import numpy as np
import tensorflow as tf
from typing import List, Tuple, Optional
import os


class PoseModel:
    """Wrapper for MoveNet Thunder pose estimation model."""
    
    def __init__(self):
        """Initialize MoveNet Thunder model."""
        # Load MoveNet model from local SavedModel
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "models"
        )
        
        saved_model_file = os.path.join(model_path, "saved_model.pb")
        if os.path.exists(saved_model_file):
            print(f"Loading MoveNet model from {model_path}")
            self.model = tf.saved_model.load(model_path)
            self.movenet = self.model.signatures['serving_default']
        else:
            # Fallback: try to load from TensorFlow Hub
            print("Loading MoveNet model from TensorFlow Hub...")
            import tensorflow_hub as hub
            model = hub.load("https://tfhub.dev/google/movenet/singlepose/thunder/4")
            self.movenet = model.signatures['serving_default']
        
        self.input_size = 256  # MoveNet Thunder uses 256x256 input
        
    def extract_keypoints(self, video_path: str) -> Tuple[List[List[List[float]]], float]:
        """
        Extract pose keypoints from video using MoveNet.
        
        Args:
            video_path: Path to the input video file
            
        Returns:
            Tuple of (keypoints, duration_seconds)
            keypoints: List[frame][joint][x, y, confidence]
            duration_seconds: Video duration in seconds
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Unable to open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_seconds = frame_count / fps if fps > 0 else 0.0
        
        all_keypoints = []
        frame_skip = 3  # Process every 3rd frame for faster processing
        current_frame = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Skip frames for faster processing
            if current_frame % frame_skip != 0:
                current_frame += 1
                continue
            
            # Preprocess frame for MoveNet
            input_image = self._preprocess_frame(frame)
            
            # Run inference
            outputs = self.movenet(input_image)
            
            # Extract keypoints from output
            # MoveNet output shape: [1, 1, 17, 3] - 17 keypoints with (y, x, confidence)
            keypoints = outputs['output_0'].numpy()[0, 0, :, :]
            
            # Convert to format: [joint][x, y, confidence]
            frame_keypoints = []
            for i in range(17):
                y, x, conf = keypoints[i]
                frame_keypoints.append([float(x), float(y), float(conf)])
            
            all_keypoints.append(frame_keypoints)
            current_frame += 1
        
        cap.release()
        
        # Normalize keypoints relative to torso distance
        normalized_keypoints = self._normalize_keypoints(all_keypoints)
        
        return normalized_keypoints, duration_seconds
    
    def _preprocess_frame(self, frame: np.ndarray) -> tf.Tensor:
        """
        Preprocess frame for MoveNet input.
        
        Args:
            frame: BGR image from OpenCV
            
        Returns:
            Preprocessed tensor ready for MoveNet
        """
        # Resize to model input size
        img = cv2.resize(frame, (self.input_size, self.input_size))
        
        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Convert to tensor and add batch dimension
        img = tf.cast(img, dtype=tf.int32)
        img = tf.expand_dims(img, axis=0)
        
        return img
    
    def _normalize_keypoints(self, keypoints: List[List[List[float]]]) -> List[List[List[float]]]:
        """
        Normalize keypoints relative to torso distance to handle different body sizes.
        
        Args:
            keypoints: Raw keypoints from MoveNet (17 keypoints)
            
        Returns:
            Normalized keypoints
        """
        normalized = []
        
        # MoveNet keypoint indices:
        # 5: left shoulder, 6: right shoulder, 11: left hip, 12: right hip
        for frame_kpts in keypoints:
            if len(frame_kpts) < 13:
                # If not enough keypoints, return as-is
                normalized.append(frame_kpts)
                continue
            
            left_shoulder = np.array(frame_kpts[5][:2])
            right_shoulder = np.array(frame_kpts[6][:2])
            left_hip = np.array(frame_kpts[11][:2])
            right_hip = np.array(frame_kpts[12][:2])
            
            # Calculate torso center and length
            shoulder_center = (left_shoulder + right_shoulder) / 2
            hip_center = (left_hip + right_hip) / 2
            torso_length = np.linalg.norm(shoulder_center - hip_center)
            
            # Avoid division by zero
            if torso_length < 0.01:
                torso_length = 1.0
            
            # Normalize all keypoints
            normalized_frame = []
            for kpt in frame_kpts:
                x, y, conf = kpt
                # Normalize relative to shoulder center and torso length
                norm_x = (x - shoulder_center[0]) / torso_length
                norm_y = (y - shoulder_center[1]) / torso_length
                normalized_frame.append([norm_x, norm_y, conf])
            
            normalized.append(normalized_frame)
        
        return normalized
    
    def get_joint_names(self) -> List[str]:
        """Return list of joint names in MoveNet order (17 keypoints)."""
        return [
            "nose",           # 0
            "left_eye",       # 1
            "right_eye",      # 2
            "left_ear",       # 3
            "right_ear",      # 4
            "left_shoulder",  # 5
            "right_shoulder", # 6
            "left_elbow",     # 7
            "right_elbow",    # 8
            "left_wrist",     # 9
            "right_wrist",    # 10
            "left_hip",       # 11
            "right_hip",      # 12
            "left_knee",      # 13
            "right_knee",     # 14
            "left_ankle",     # 15
            "right_ankle"     # 16
        ]


# Global model instance
_pose_model: Optional[PoseModel] = None


def load_model() -> PoseModel:
    """Load and return the global pose model instance."""
    global _pose_model
    if _pose_model is None:
        _pose_model = PoseModel()
    return _pose_model


def extract_keypoints(video_path: str) -> Tuple[List[List[List[float]]], float]:
    """
    Convenience function to extract keypoints from video.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Tuple of (keypoints, duration_seconds)
    """
    model = load_model()
    return model.extract_keypoints(video_path)
