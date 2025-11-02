"""
Configuration Module for DTW and Motion Comparison
Centralized tuning parameters for optimal performance.
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class DTWConfig:
    """Configuration for DTW comparison."""
    
    # Frame sampling
    frame_sample_rate: int = 1  # Process every Nth frame (1=all, 2=every 2nd, etc.)
    # Recommended: 1-2 for precise motion, 3-5 for fast/long sequences
    
    # Temporal smoothing
    smoothing_window: int = 3  # Moving average window size
    # Recommended: 2-3 for responsive, 4-5 for stable
    
    # DTW windowing
    use_window: bool = True  # Enable Sakoe-Chiba windowing
    window_size: int = None  # Auto-calculate if None (15% for >500 frames)
    window_percentage: float = 0.15  # Window as % of sequence length
    
    # FastDTW
    use_fastdtw: bool = False  # Enable FastDTW for sequences >1000 frames
    fastdtw_threshold: int = 1000  # Sequence length to trigger FastDTW
    
    # Stressed joints
    stressed_joint_threshold: float = 0.25  # Default threshold (normalized units)
    custom_thresholds: Dict[str, float] = None  # Per-joint custom thresholds
    
    # Similarity scaling
    similarity_scale: str = "0-1"  # "0-1" or "0-100"
    
    def get_window_size(self, seq_length: int) -> int:
        """Calculate window size for given sequence length."""
        if not self.use_window:
            return None
        if self.window_size is not None:
            return self.window_size
        if seq_length > 500:
            return int(self.window_percentage * seq_length)
        return None  # No window for short sequences
    
    def get_joint_threshold(self, joint_name: str) -> float:
        """Get threshold for specific joint."""
        if self.custom_thresholds and joint_name in self.custom_thresholds:
            return self.custom_thresholds[joint_name]
        return self.stressed_joint_threshold
    
    def scale_similarity(self, similarity: float) -> float:
        """Scale similarity to configured range."""
        if self.similarity_scale == "0-100":
            return 100 * similarity
        return similarity


@dataclass
class VideoProcessingConfig:
    """Configuration for video processing and pose extraction."""
    
    # MoveNet inference
    input_size: int = 256  # Model input size (256 for Thunder, 192 for Lightning)
    confidence_threshold: float = 0.3  # Minimum confidence for keypoint
    
    # Video processing
    max_frames: int = None  # Limit frames per video (None = unlimited)
    target_fps: int = None  # Resample to target FPS (None = use original)
    
    # Normalization
    normalize_by_torso: bool = True  # Use torso-based normalization
    min_torso_length: float = 1e-6  # Minimum torso length to avoid division by zero


# Default configurations
DEFAULT_DTW_CONFIG = DTWConfig()
DEFAULT_VIDEO_CONFIG = VideoProcessingConfig()


# Preset configurations for different use cases
class DTWPresets:
    """Preset configurations for common scenarios."""
    
    @staticmethod
    def precise():
        """High accuracy, slower processing."""
        return DTWConfig(
            frame_sample_rate=1,
            smoothing_window=2,
            use_window=False,
            use_fastdtw=False,
            stressed_joint_threshold=0.20
        )
    
    @staticmethod
    def balanced():
        """Balance between speed and accuracy."""
        return DTWConfig(
            frame_sample_rate=1,
            smoothing_window=3,
            use_window=True,
            window_percentage=0.15,
            use_fastdtw=False,
            stressed_joint_threshold=0.25
        )
    
    @staticmethod
    def fast():
        """Optimized for speed, slight accuracy trade-off."""
        return DTWConfig(
            frame_sample_rate=2,
            smoothing_window=4,
            use_window=True,
            window_percentage=0.10,
            use_fastdtw=True,
            stressed_joint_threshold=0.30
        )
    
    @staticmethod
    def long_sequences():
        """For videos >60 seconds."""
        return DTWConfig(
            frame_sample_rate=3,
            smoothing_window=5,
            use_window=True,
            window_percentage=0.10,
            use_fastdtw=True,
            fastdtw_threshold=500,
            stressed_joint_threshold=0.25
        )


class StressedJointThresholds:
    """Preset thresholds for different joint sensitivity levels."""
    
    @staticmethod
    def strict():
        """Very sensitive - catches minor deviations."""
        return {
            "left_shoulder": 0.15,
            "right_shoulder": 0.15,
            "left_elbow": 0.20,
            "right_elbow": 0.20,
            "left_hip": 0.20,
            "right_hip": 0.20,
            "left_knee": 0.20,
            "right_knee": 0.20,
            "left_ankle": 0.25,
            "right_ankle": 0.25,
        }
    
    @staticmethod
    def moderate():
        """Balanced sensitivity."""
        return {
            "left_shoulder": 0.25,
            "right_shoulder": 0.25,
            "left_elbow": 0.25,
            "right_elbow": 0.25,
            "left_hip": 0.25,
            "right_hip": 0.25,
            "left_knee": 0.30,
            "right_knee": 0.30,
            "left_ankle": 0.35,
            "right_ankle": 0.35,
        }
    
    @staticmethod
    def relaxed():
        """Less sensitive - only major deviations."""
        return {
            "left_shoulder": 0.35,
            "right_shoulder": 0.35,
            "left_elbow": 0.35,
            "right_elbow": 0.35,
            "left_hip": 0.35,
            "right_hip": 0.35,
            "left_knee": 0.40,
            "right_knee": 0.40,
            "left_ankle": 0.45,
            "right_ankle": 0.45,
        }


# Global config (can be modified at runtime)
_global_dtw_config = DEFAULT_DTW_CONFIG
_global_video_config = DEFAULT_VIDEO_CONFIG


def get_dtw_config() -> DTWConfig:
    """Get current DTW configuration."""
    return _global_dtw_config


def set_dtw_config(config: DTWConfig):
    """Set global DTW configuration."""
    global _global_dtw_config
    _global_dtw_config = config


def get_video_config() -> VideoProcessingConfig:
    """Get current video processing configuration."""
    return _global_video_config


def set_video_config(config: VideoProcessingConfig):
    """Set global video processing configuration."""
    global _global_video_config
    _global_video_config = config
