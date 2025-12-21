"""
Video Generation Module

This module provides a modular video generation system with swappable AI models.

Supported Models:
- PLACEHOLDER: Simple composite animation (no GPU needed, for testing)
- WAN21: Alibaba's Wan 2.1 (free, local, requires GPU)
- SVD: Stable Video Diffusion (paid, cloud via Replicate)
- ANIMATEDIFF: AnimateDiff (free, local)

Usage:
    from ai_pipeline.video_generation import get_video_generator, VideoModelType

    # Get a generator
    generator = get_video_generator(VideoModelType.WAN21)
    await generator.load_model()

    # Generate video
    result = await generator.generate(config)

To add a new model:
    1. Create a new file: my_generator.py
    2. Inherit from BaseVideoGenerator
    3. Implement: load_model(), generate(), get_model_info()
    4. Register in base_generator.py's get_video_generator()
"""

from .base_generator import (
    BaseVideoGenerator,
    VideoGenerationConfig,
    VideoGenerationResult,
    VideoModelType,
    get_video_generator
)

from .placeholder_generator import PlaceholderGenerator
from .wan21_generator import Wan21Generator

__all__ = [
    # Base classes
    "BaseVideoGenerator",
    "VideoGenerationConfig",
    "VideoGenerationResult",
    "VideoModelType",
    # Factory
    "get_video_generator",
    # Generators
    "PlaceholderGenerator",
    "Wan21Generator",
]
