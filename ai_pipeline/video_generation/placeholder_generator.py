"""
Placeholder Video Generator - Simple implementation for testing the pipeline.
Creates basic composite videos without AI, useful for testing the full flow.
"""

import os
import time
import numpy as np
from PIL import Image
import cv2
from typing import Dict, Any
from loguru import logger

from .base_generator import (
    BaseVideoGenerator,
    VideoGenerationConfig,
    VideoGenerationResult,
    VideoModelType
)


class PlaceholderGenerator(BaseVideoGenerator):
    """
    Placeholder video generator for testing.
    Creates simple composite animations without actual AI models.
    """

    def __init__(self, device: str = "cpu"):
        super().__init__(device)
        self.model_name = "placeholder"

    async def load_model(self) -> bool:
        """No model to load for placeholder"""
        self.model_loaded = True
        logger.info("Placeholder generator ready (no model needed)")
        return True

    async def generate(self, config: VideoGenerationConfig) -> VideoGenerationResult:
        """
        Generate a simple placeholder video.
        Composites model image on background with basic motion.
        """
        start_time = time.time()
        logger.info(f"Generating placeholder video: {config.duration}s @ {config.fps}fps")

        try:
            # Load images
            model_img = Image.open(config.model_image_path).convert("RGB")
            background_img = Image.open(config.background_path).convert("RGB")

            # Resize to target resolution
            width, height = config.resolution
            model_img = model_img.resize((width, height), Image.Resampling.LANCZOS)
            background_img = background_img.resize((width, height), Image.Resampling.LANCZOS)

            # Generate frames
            frames = self._create_animation(
                model_img,
                background_img,
                config.action_type,
                config.duration,
                config.fps
            )

            # Ensure output directory exists
            os.makedirs(os.path.dirname(config.output_path), exist_ok=True)

            # Save video
            self._save_video(frames, config.output_path, config.fps, config.audio_path)

            generation_time = time.time() - start_time
            logger.info(f"Placeholder video generated in {generation_time:.2f}s")

            return VideoGenerationResult(
                success=True,
                output_path=config.output_path,
                duration=config.duration,
                model_used=self.model_name,
                generation_time=generation_time,
                metadata={
                    "frames": len(frames),
                    "resolution": config.resolution,
                    "action": config.action_type
                }
            )

        except Exception as e:
            logger.error(f"Placeholder generation failed: {e}")
            return VideoGenerationResult(
                success=False,
                error_message=str(e),
                model_used=self.model_name,
                generation_time=time.time() - start_time
            )

    def _create_animation(
        self,
        model_img: Image.Image,
        background_img: Image.Image,
        action_type: str,
        duration: float,
        fps: int
    ) -> list:
        """Create simple animation frames"""
        num_frames = int(duration * fps)
        frames = []

        model_np = np.array(model_img)
        bg_np = np.array(background_img)

        # Different animation based on action type
        for i in range(num_frames):
            progress = i / num_frames
            frame = self._composite_frame(model_np, bg_np, action_type, progress)
            frames.append(frame)

        return frames

    def _composite_frame(
        self,
        model_np: np.ndarray,
        bg_np: np.ndarray,
        action_type: str,
        progress: float
    ) -> np.ndarray:
        """Create a single composite frame with action-based motion"""
        frame = bg_np.copy()
        h, w = model_np.shape[:2]

        # Base position (center)
        base_x = (frame.shape[1] - w) // 2
        base_y = (frame.shape[0] - h) // 2

        # Apply action-specific motion
        if action_type in ["talking", "nodding"]:
            # Subtle vertical bob
            offset_y = int(5 * np.sin(2 * np.pi * progress * 3))
            offset_x = 0
        elif action_type in ["waving", "thumbsup"]:
            # Horizontal wave motion
            offset_x = int(15 * np.sin(2 * np.pi * progress * 2))
            offset_y = int(5 * np.sin(2 * np.pi * progress * 4))
        elif action_type in ["presenting", "unboxing"]:
            # Forward lean motion
            offset_x = int(10 * np.sin(2 * np.pi * progress))
            offset_y = int(-10 * (1 - np.cos(2 * np.pi * progress)) / 2)
        elif action_type in ["excited"]:
            # Bouncy motion
            offset_x = int(10 * np.sin(2 * np.pi * progress * 4))
            offset_y = int(15 * abs(np.sin(2 * np.pi * progress * 3)))
        elif action_type in ["thinking"]:
            # Slow sway
            offset_x = int(8 * np.sin(2 * np.pi * progress * 0.5))
            offset_y = int(3 * np.cos(2 * np.pi * progress * 0.5))
        else:
            # Default gentle motion
            offset_x = int(10 * np.sin(2 * np.pi * progress))
            offset_y = int(5 * np.cos(2 * np.pi * progress))

        # Calculate final position
        x_start = max(0, base_x + offset_x)
        y_start = max(0, base_y + offset_y)
        x_end = min(frame.shape[1], x_start + w)
        y_end = min(frame.shape[0], y_start + h)

        src_x_end = x_end - x_start
        src_y_end = y_end - y_start

        # Simple alpha blending
        alpha = 0.85
        frame[y_start:y_end, x_start:x_end] = (
            alpha * model_np[:src_y_end, :src_x_end] +
            (1 - alpha) * frame[y_start:y_end, x_start:x_end]
        ).astype(np.uint8)

        return frame

    def _save_video(
        self,
        frames: list,
        output_path: str,
        fps: int,
        audio_path: str = None
    ) -> None:
        """Save frames as video file"""
        if not frames:
            raise ValueError("No frames to save")

        height, width = frames[0].shape[:2]

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_path = output_path + ".temp.mp4"
        out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))

        for frame in frames:
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)

        out.release()

        # Add audio if provided
        if audio_path and os.path.exists(audio_path):
            self._add_audio(temp_path, audio_path, output_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
        else:
            os.rename(temp_path, output_path)

    def _add_audio(self, video_path: str, audio_path: str, output_path: str) -> None:
        """Add audio to video using ffmpeg"""
        import subprocess

        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info("Audio added to video")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(f"Could not add audio: {e}. Saving video without audio.")
            import shutil
            shutil.copy(video_path, output_path)

    def get_model_info(self) -> Dict[str, Any]:
        """Get placeholder model info"""
        return {
            "name": "Placeholder Generator",
            "type": VideoModelType.PLACEHOLDER.value,
            "description": "Simple composite animation for testing",
            "version": "1.0.0",
            "free": True,
            "local": True,
            "quality": "low",
            "speed": "fast"
        }

    def get_requirements(self) -> Dict[str, Any]:
        """Minimal requirements"""
        return {
            "gpu_required": False,
            "vram_gb": 0,
            "disk_gb": 0.1,
            "internet_required": False
        }
