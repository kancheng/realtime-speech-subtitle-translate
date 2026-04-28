"""Device detection helpers for faster-whisper runtime selection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WhisperRuntime:
    """Represents runtime configuration for faster-whisper."""

    device: str
    compute_type: str
    cuda_available: bool


def is_cuda_available() -> bool:
    """Return True if CUDA appears to be available in the environment."""
    try:
        import torch  # type: ignore

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def get_recommended_runtime() -> WhisperRuntime:
    """Get recommended faster-whisper device and compute type."""
    if is_cuda_available():
        return WhisperRuntime(device="cuda", compute_type="float16", cuda_available=True)
    return WhisperRuntime(device="cpu", compute_type="int8", cuda_available=False)

