"""
Base Video Generator - Abstract interface for all video generation models.
This allows easy swapping between different AI models (Wan2.1, SVD, AnimateDiff, etc.)
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import os


class VideoModelType(Enum):
    """Supported video generation models"""
    WAN21 = "wan2.1"           # Free, local - Alibaba's Wan 2.1
    SVD = "svd"                 # Paid, cloud - Stable Video Diffusion
    ANIMATEDIFF = "animatediff" # Free, local - AnimateDiff
    KLING = "kling"             # Paid, API - Kling AI
    PLACEHOLDER = "placeholder" # Simple placeholder for testing


@dataclass
class VideoGenerationConfig:
    """Configuration for video generation"""
    model_image_path: str
    background_path: str
    action_type: str
    action_data: Dict[str, Any]
    output_path: str
    duration: float = 5.0
    fps: int = 24
    resolution: tuple = (512, 512)
    audio_path: Optional[str] = None

    # Model-specific options
    guidance_scale: float = 7.5
    num_inference_steps: int = 25
    motion_bucket_id: int = 127
    seed: Optional[int] = None


@dataclass
class VideoGenerationResult:
    """Result of video generation"""
    success: bool
    output_path: Optional[str] = None
    duration: float = 0.0
    error_message: Optional[str] = None
    model_used: str = ""
    generation_time: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseVideoGenerator(ABC):
    """
    Abstract base class for video generators.
    Implement this interface to add support for new AI models.
    """

    def __init__(self, device: str = "auto"):
        """
        Initialize the generator.

        Args:
            device: "cuda", "cpu", or "auto"
        """
        self.device = self._resolve_device(device)
        self.model_loaded = False
        self.model_name = "base"

    def _resolve_device(self, device: str) -> str:
        """Resolve device string to actual device"""
        if device == "auto":
            try:
                import torch
                return "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return device

    @abstractmethod
    async def load_model(self) -> bool:
        """
        Load the AI model into memory.
        Returns True if successful.
        """
        pass

    @abstractmethod
    async def generate(self, config: VideoGenerationConfig) -> VideoGenerationResult:
        """
        Generate video based on configuration.

        Args:
            config: VideoGenerationConfig with all parameters

        Returns:
            VideoGenerationResult with output path or error
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            Dict with model name, type, requirements, etc.
        """
        pass

    def unload_model(self) -> None:
        """Release model from memory (optional override)"""
        self.model_loaded = False

    def is_available(self) -> bool:
        """Check if this model is available to use"""
        return True

    def get_requirements(self) -> Dict[str, Any]:
        """Get system requirements for this model"""
        return {
            "gpu_required": False,
            "vram_gb": 0,
            "disk_gb": 0,
            "internet_required": False
        }


def get_video_generator(model_type: VideoModelType, **kwargs) -> BaseVideoGenerator:
    """
    Factory function to get the appropriate video generator.

    Args:
        model_type: Which model to use
        **kwargs: Additional arguments passed to generator

    Returns:
        Instance of the appropriate generator
    """
    from .wan21_generator import Wan21Generator
    from .placeholder_generator import PlaceholderGenerator

    generators = {
        VideoModelType.WAN21: Wan21Generator,
        VideoModelType.PLACEHOLDER: PlaceholderGenerator,
        # Future: Add more generators here
        # VideoModelType.SVD: SVDGenerator,
        # VideoModelType.ANIMATEDIFF: AnimateDiffGenerator,
    }

    generator_class = generators.get(model_type)
    if generator_class is None:
        raise ValueError(f"Unknown model type: {model_type}")

    return generator_class(**kwargs)
