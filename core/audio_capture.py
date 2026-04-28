"""Microphone capture component built on sounddevice."""

from __future__ import annotations

import logging
import threading
from queue import Queue
from typing import Callable, Optional

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)


class AudioCapture:
    """Capture microphone input and push float32 samples to a queue."""

    def __init__(
        self,
        audio_queue: Queue[np.ndarray],
        sample_rate: int = 16000,
        channels: int = 1,
        callback: Optional[Callable[[np.ndarray], None]] = None,
    ) -> None:
        self.audio_queue = audio_queue
        self.sample_rate = sample_rate
        self.channels = channels
        self.callback = callback
        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()
        self._running = False

    @property
    def running(self) -> bool:
        """Return current capture state."""
        return self._running

    def _on_audio(self, indata, frames, time_info, status) -> None:
        """Sounddevice stream callback."""
        if status:
            logger.warning("Audio input status: %s", status)
        if not self._running:
            return

        data = np.asarray(indata, dtype=np.float32).copy()
        if self.channels > 1:
            data = data.mean(axis=1, keepdims=True).astype(np.float32)
        data = data.reshape(-1)
        self.audio_queue.put(data)
        if self.callback:
            self.callback(data)

    def start_capture(self) -> None:
        """Start capturing audio from default input device."""
        with self._lock:
            if self._running:
                logger.info("Audio capture already running; ignoring duplicate start.")
                return

            try:
                self._stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype="float32",
                    callback=self._on_audio,
                    blocksize=0,
                )
                self._stream.start()
                self._running = True
                logger.info("Audio capture started.")
            except Exception as exc:
                logger.exception("Unable to start microphone capture: %s", exc)
                self._stream = None
                raise RuntimeError(f"Unable to start microphone capture: {exc}") from exc

    def stop_capture(self) -> None:
        """Stop microphone capture safely."""
        with self._lock:
            if not self._running:
                logger.info("Audio capture is not running; stop ignored.")
                return

            self._running = False
            if self._stream is not None:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception as exc:
                    logger.warning("Error while stopping audio stream: %s", exc)
                finally:
                    self._stream = None
            logger.info("Audio capture stopped.")

