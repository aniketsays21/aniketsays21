import os
import torch
import numpy as np
from typing import Optional, Dict, List
from PIL import Image
import cv2
from loguru import logger

try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False
    logger.warning("Replicate not installed. Cloud-based generation unavailable.")


class VideoGenerator:
    """
    Generate videos from images using AI models
    Supports both local and cloud-based generation
    """

    def __init__(
        self,
        use_local: bool = True,
        replicate_token: Optional[str] = None,
        device: str = "auto"
    ):
        """
        Initialize video generator

        Args:
            use_local: Use local models (True) or cloud APIs (False)
            replicate_token: Replicate API token for cloud generation
            device: "cuda", "cpu", or "auto"
        """
        self.use_local = use_local
        self.replicate_token = replicate_token

        # Set device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"VideoGenerator initialized (local={use_local}, device={self.device})")

        if not use_local and not REPLICATE_AVAILABLE:
            raise ImportError("Replicate not installed. Install with: pip install replicate")

    async def generate_video(
        self,
        model_image_path: str,
        background_path: str,
        action_data: Dict,
        audio_path: Optional[str],
        output_path: str,
        duration: float = 5.0,
        fps: int = 24,
        resolution: tuple = (512, 512)
    ) -> str:
        """
        Generate UGC video

        Args:
            model_image_path: Path to model image
            background_path: Path to background image
            action_data: Action/pose sequence data
            audio_path: Path to audio file (optional)
            output_path: Where to save video
            duration: Video duration in seconds
            fps: Frames per second
            resolution: (width, height)

        Returns:
            Path to generated video
        """
        logger.info(f"Generating video: duration={duration}s, fps={fps}")

        if self.use_local:
            return await self._generate_local(
                model_image_path,
                background_path,
                action_data,
                audio_path,
                output_path,
                duration,
                fps,
                resolution
            )
        else:
            return await self._generate_cloud(
                model_image_path,
                background_path,
                action_data,
                audio_path,
                output_path,
                duration
            )

    async def _generate_local(
        self,
        model_image_path: str,
        background_path: str,
        action_data: Dict,
        audio_path: Optional[str],
        output_path: str,
        duration: float,
        fps: int,
        resolution: tuple
    ) -> str:
        """
        Generate video using local models

        This is a simplified implementation. For production:
        - Use AnimateDiff or MagicAnimate
        - Implement proper pose-guided animation
        - Add motion interpolation
        """
        logger.info("Generating video locally (simplified implementation)")

        # Load images
        model_img = Image.open(model_image_path).convert("RGB")
        background_img = Image.open(background_path).convert("RGB")

        # Resize to target resolution
        model_img = model_img.resize(resolution, Image.Resampling.LANCZOS)
        background_img = background_img.resize(resolution, Image.Resampling.LANCZOS)

        # For now, create a simple composite video
        # TODO: Replace with actual AI model (AnimateDiff/MagicAnimate)
        frames = self._create_simple_animation(
            model_img,
            background_img,
            action_data,
            duration,
            fps
        )

        # Save as video
        self._save_video(frames, output_path, fps, audio_path)

        logger.info(f"Video generated: {output_path}")
        return output_path

    async def _generate_cloud(
        self,
        model_image_path: str,
        background_path: str,
        action_data: Dict,
        audio_path: Optional[str],
        output_path: str,
        duration: float
    ) -> str:
        """
        Generate video using Replicate API
        """
        logger.info("Generating video using Replicate API")

        if not self.replicate_token:
            raise ValueError("Replicate API token required for cloud generation")

        # Initialize Replicate client
        client = replicate.Client(api_token=self.replicate_token)

        # Upload images
        with open(model_image_path, "rb") as f:
            model_image = f.read()

        # Run Stable Video Diffusion or similar model
        # This is an example - adjust based on actual model API
        try:
            output = client.run(
                "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
                input={
                    "image": model_image,
                    "fps": 6,
                    "motion_bucket_id": 127,
                    "cond_aug": 0.02
                }
            )

            # Download result
            import httpx
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(output)
                with open(output_path, "wb") as f:
                    f.write(response.content)

            # Add audio if provided
            if audio_path:
                self._add_audio_to_video(output_path, audio_path, output_path)

            logger.info(f"Cloud video generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Cloud generation failed: {e}")
            raise

    def _create_simple_animation(
        self,
        model_img: Image.Image,
        background_img: Image.Image,
        action_data: Dict,
        duration: float,
        fps: int
    ) -> List[np.ndarray]:
        """
        Create simple animation (placeholder for actual AI model)

        This is a basic implementation. For production:
        - Use actual pose-guided animation
        - Implement smooth motion interpolation
        - Add realistic effects
        """
        num_frames = int(duration * fps)
        frames = []

        # Convert to numpy
        model_np = np.array(model_img)
        bg_np = np.array(background_img)

        # Get action sequence
        action_name = action_data.get("name", "default")

        for i in range(num_frames):
            # Create composite frame
            # Simple implementation: blend model on background with movement

            # Calculate position offset (simple horizontal movement)
            offset_x = int(20 * np.sin(2 * np.pi * i / num_frames))
            offset_y = int(10 * np.cos(2 * np.pi * i / num_frames))

            # Create frame
            frame = bg_np.copy()

            # Simple compositing (in production, use proper alpha blending)
            # This is just a placeholder
            h, w = model_np.shape[:2]
            y_start = max(0, (frame.shape[0] - h) // 2 + offset_y)
            x_start = max(0, (frame.shape[1] - w) // 2 + offset_x)

            y_end = min(frame.shape[0], y_start + h)
            x_end = min(frame.shape[1], x_start + w)

            src_y_end = y_end - y_start
            src_x_end = x_end - x_start

            # Blend
            alpha = 0.8
            frame[y_start:y_end, x_start:x_end] = (
                alpha * model_np[:src_y_end, :src_x_end] +
                (1 - alpha) * frame[y_start:y_end, x_start:x_end]
            ).astype(np.uint8)

            frames.append(frame)

        return frames

    def _save_video(
        self,
        frames: List[np.ndarray],
        output_path: str,
        fps: int,
        audio_path: Optional[str] = None
    ):
        """Save frames as video file"""
        if not frames:
            raise ValueError("No frames to save")

        height, width = frames[0].shape[:2]

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_path = output_path + ".temp.mp4"
        out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))

        for frame in frames:
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)

        out.release()

        # Add audio if provided
        if audio_path and os.path.exists(audio_path):
            self._add_audio_to_video(temp_path, audio_path, output_path)
            os.remove(temp_path)
        else:
            os.rename(temp_path, output_path)

    def _add_audio_to_video(
        self,
        video_path: str,
        audio_path: str,
        output_path: str
    ):
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

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add audio: {e}")
            # Fallback: just copy video without audio
            import shutil
            shutil.copy(video_path, output_path)

        except FileNotFoundError:
            logger.warning("ffmpeg not found. Saving video without audio.")
            import shutil
            shutil.copy(video_path, output_path)


# Convenience function
async def generate_ugc_video(
    model_image: str,
    background: str,
    action: Dict,
    audio: Optional[str],
    output: str,
    **kwargs
) -> str:
    """Quick video generation function"""
    generator = VideoGenerator()
    return await generator.generate_video(
        model_image,
        background,
        action,
        audio,
        output,
        **kwargs
    )
