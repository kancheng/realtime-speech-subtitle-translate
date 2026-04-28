"""faster-whisper wrapper for speech-to-text inference."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
from faster_whisper import WhisperModel

from core.device_utils import WhisperRuntime, get_recommended_runtime

logger = logging.getLogger(__name__)


@dataclass
class ASRResult:
    """Structured ASR output."""

    text: str
    language: Optional[str] = None
    error: Optional[str] = None


class ASREngine:
    """Encapsulates model loading and transcription logic."""

    def __init__(
        self,
        model_size: str = "base",
        runtime: Optional[WhisperRuntime] = None,
        beam_size: int = 5,
    ) -> None:
        self.model_size = model_size
        self.runtime = runtime or get_recommended_runtime()
        self.beam_size = beam_size
        self.model: Optional[WhisperModel] = None
        self._load_model()

    def _load_model(self) -> None:
        """Load faster-whisper model with fallback to CPU if needed."""
        try:
            self.model = WhisperModel(
                self.model_size,
                device=self.runtime.device,
                compute_type=self.runtime.compute_type,
            )
            logger.info(
                "ASR model loaded: size=%s device=%s compute_type=%s",
                self.model_size,
                self.runtime.device,
                self.runtime.compute_type,
            )
        except Exception as exc:
            logger.exception("Failed to load ASR model with requested runtime: %s", exc)
            if self.runtime.device != "cpu":
                logger.warning("Falling back to CPU int8 runtime.")
                self.runtime = WhisperRuntime(
                    device="cpu",
                    compute_type="int8",
                    cuda_available=False,
                )
                self.model = WhisperModel(
                    self.model_size,
                    device=self.runtime.device,
                    compute_type=self.runtime.compute_type,
                )
            else:
                raise RuntimeError(f"Unable to load ASR model: {exc}") from exc

    def transcribe(self, audio_np: np.ndarray, language: str) -> ASRResult:
        """Transcribe an audio chunk and return merged text."""
        if self.model is None:
            return ASRResult(text="", error="ASR model is not initialized.")

        if audio_np is None or audio_np.size == 0:
            return ASRResult(text="", language=language, error="Empty audio input.")

        audio = np.asarray(audio_np, dtype=np.float32).flatten()
        if np.max(np.abs(audio), initial=0.0) < 1e-4:
            return ASRResult(text="", language=language, error="Audio too quiet.")

        try:
            segments, info = self.model.transcribe(
                audio,
                language=language,
                beam_size=self.beam_size,
                vad_filter=True,
            )
            text = " ".join(segment.text.strip() for segment in segments if segment.text).strip()
            if not text:
                return ASRResult(text="", language=language, error="No speech detected.")
            return ASRResult(text=text, language=getattr(info, "language", language))
        except Exception as exc:
            logger.exception("ASR transcription failed: %s", exc)
            return ASRResult(text="", language=language, error=str(exc))

