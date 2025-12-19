import os
import torch
import numpy as np
from typing import Optional
from scipy.io.wavfile import write as write_wav
from loguru import logger

# Import Bark (will be installed via requirements)
try:
    from bark import SAMPLE_RATE, generate_audio, preload_models
    from bark.generation import SUPPORTED_LANGS
    BARK_AVAILABLE = True
except ImportError:
    logger.warning("Bark not installed. Voice synthesis will not work.")
    BARK_AVAILABLE = False


class BarkSynthesizer:
    """
    Voice synthesis using Bark by Suno AI
    Supports emotional control and natural speech generation
    """

    # Voice presets with emotional characteristics
    VOICE_PRESETS = {
        "neutral": "v2/en_speaker_6",
        "happy": "v2/en_speaker_3",
        "sad": "v2/en_speaker_7",
        "excited": "v2/en_speaker_9",
        "calm": "v2/en_speaker_1",
        "angry": "v2/en_speaker_8",
        "surprised": "v2/en_speaker_5"
    }

    # Emotional prompts to enhance generation
    EMOTION_PROMPTS = {
        "neutral": "",
        "happy": " [laughs]",
        "sad": " [sighs]",
        "excited": "!",
        "calm": "...",
        "angry": "!",
        "surprised": "!"
    }

    def __init__(self, model_size: str = "small", device: str = "auto"):
        """
        Initialize Bark synthesizer

        Args:
            model_size: "small" or "large" (small is faster, large is higher quality)
            device: "cuda", "cpu", or "auto"
        """
        if not BARK_AVAILABLE:
            raise ImportError("Bark is not installed. Install with: pip install git+https://github.com/suno-ai/bark.git")

        # Set device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"Initializing Bark on {self.device}")

        # Preload models (this may take a while on first run)
        preload_models(
            text_use_small=model_size == "small",
            coarse_use_small=model_size == "small",
            fine_use_gpu=self.device == "cuda",
            codec_use_gpu=self.device == "cuda"
        )

        logger.info("Bark models loaded successfully")

    def synthesize(
        self,
        text: str,
        emotion: str = "neutral",
        output_path: Optional[str] = None,
        voice_preset: Optional[str] = None
    ) -> str:
        """
        Synthesize speech from text

        Args:
            text: Text to synthesize
            emotion: Emotion type (neutral, happy, sad, excited, calm, angry, surprised)
            output_path: Path to save audio file (will auto-generate if None)
            voice_preset: Custom voice preset or use emotion-based preset

        Returns:
            Path to generated audio file
        """
        logger.info(f"Synthesizing text with emotion: {emotion}")

        # Get voice preset
        if voice_preset is None:
            voice_preset = self.VOICE_PRESETS.get(emotion, self.VOICE_PRESETS["neutral"])

        # Enhance text with emotional cues
        enhanced_text = self._enhance_text_with_emotion(text, emotion)

        # Generate audio
        audio_array = generate_audio(
            enhanced_text,
            history_prompt=voice_preset
        )

        # Generate output path if not provided
        if output_path is None:
            output_path = f"output_{hash(text) % 100000}.wav"

        # Save audio
        write_wav(output_path, SAMPLE_RATE, audio_array)
        logger.info(f"Audio saved to: {output_path}")

        return output_path

    def _enhance_text_with_emotion(self, text: str, emotion: str) -> str:
        """
        Enhance text with emotional cues for better synthesis

        Bark supports special tokens:
        - [laughter]
        - [laughs]
        - [sighs]
        - [music]
        - [gasps]
        - [clears throat]
        - — or ... for hesitations
        - ♪ for song lyrics
        """
        enhanced = text

        # Add emotional modifiers
        emotion_mod = self.EMOTION_PROMPTS.get(emotion, "")
        if emotion_mod:
            # Add at strategic points (end of sentences)
            enhanced = enhanced.replace(". ", f".{emotion_mod} ")
            if not enhanced.endswith(emotion_mod):
                enhanced += emotion_mod

        # Add natural pauses
        if emotion == "calm":
            enhanced = enhanced.replace(", ", "... ")
        elif emotion == "excited":
            enhanced = enhanced.replace(". ", "! ")

        return enhanced

    def clone_voice(
        self,
        sample_audio_path: str,
        text: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Clone voice from sample audio (experimental)

        Note: Bark has limited voice cloning. For better results,
        use Coqui TTS or other specialized models.

        Args:
            sample_audio_path: Path to sample audio file
            text: Text to synthesize
            output_path: Output path

        Returns:
            Path to generated audio
        """
        logger.warning("Voice cloning in Bark is limited. Consider using Coqui TTS for better results.")

        # For now, just use a neutral voice
        # TODO: Implement actual voice cloning using Bark's history prompts
        return self.synthesize(text, emotion="neutral", output_path=output_path)


# Convenience function
def synthesize_speech(
    text: str,
    emotion: str = "neutral",
    output_path: Optional[str] = None,
    model_size: str = "small"
) -> str:
    """
    Quick speech synthesis function

    Args:
        text: Text to synthesize
        emotion: Emotion type
        output_path: Output file path
        model_size: "small" or "large"

    Returns:
        Path to generated audio file
    """
    synthesizer = BarkSynthesizer(model_size=model_size)
    return synthesizer.synthesize(text, emotion, output_path)


# Example usage
if __name__ == "__main__":
    # Test synthesis
    synthesizer = BarkSynthesizer()

    test_texts = [
        ("This product is amazing! You're going to love it.", "excited"),
        ("Check out this incredible new gadget.", "happy"),
        ("This is a high-quality, premium product.", "calm"),
    ]

    for text, emotion in test_texts:
        output = synthesizer.synthesize(text, emotion=emotion)
        print(f"Generated: {output}")
