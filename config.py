"""Global configuration for the realtime subtitle application."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
TRANSCRIPTS_DIR = OUTPUTS_DIR / "transcripts"
SUBTITLES_DIR = OUTPUTS_DIR / "subtitles"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure console logging format used by the application."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
    )


@dataclass(frozen=True)
class AppConfig:
    """Immutable runtime configuration shared across components."""

    default_model_size: str = "base"
    default_source_language: str = "en"
    default_target_language: str = "zh"
    sample_rate: int = 16000
    channels: int = 1
    chunk_duration_seconds: float = 3.0
    rms_threshold: float = 0.008
    subtitle_history_limit: int = 100
    beam_size: int = 5


ASR_MODEL_OPTIONS = ("tiny", "base", "small", "medium")
LANGUAGE_OPTIONS = (
    ("English", "en"),
    ("Chinese", "zh"),
    ("Japanese", "ja"),
    ("Korean", "ko"),
    ("French", "fr"),
    ("German", "de"),
    ("Spanish", "es"),
)

