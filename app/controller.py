"""Application controller orchestrating audio, ASR, and translation workers."""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from queue import Empty, Queue
from typing import Optional

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

from config import AppConfig, TRANSCRIPTS_DIR
from core.asr_engine import ASREngine
from core.audio_capture import AudioCapture
from core.subtitle_manager import SubtitleManager
from core.translator import Translator

logger = logging.getLogger(__name__)


class AppController(QObject):
    """Coordinate background processing and GUI state."""

    subtitle_updated = pyqtSignal(str, str)
    status_updated = pyqtSignal(str)
    running_state_changed = pyqtSignal(bool)

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.config = config
        self.audio_queue: Queue[np.ndarray] = Queue()
        self.asr_input_queue: Queue[np.ndarray] = Queue()
        self.text_queue: Queue[str] = Queue()
        self.audio_capture = AudioCapture(
            audio_queue=self.audio_queue,
            sample_rate=self.config.sample_rate,
            channels=self.config.channels,
        )
        self.translator = Translator()
        self.subtitle_manager = SubtitleManager(max_history=self.config.subtitle_history_limit)
        self.asr_engine: Optional[ASREngine] = None
        self._running = False
        self._audio_thread: Optional[threading.Thread] = None
        self._asr_thread: Optional[threading.Thread] = None
        self._translation_thread: Optional[threading.Thread] = None
        self._source_lang = self.config.default_source_language
        self._target_lang = self.config.default_target_language
        self._silence_finalize_samples = int(
            self.config.sample_rate * self.config.silence_finalize_seconds
        )
        self._min_sentence_samples = int(self.config.sample_rate * self.config.min_sentence_seconds)
        self._max_sentence_samples = int(self.config.sample_rate * self.config.max_sentence_seconds)

    @property
    def running(self) -> bool:
        """Return True while workers are active."""
        return self._running

    def start(self, model_size: str, source_lang: str, target_lang: str) -> None:
        """Start capture and worker threads."""
        if self._running:
            self.status_updated.emit("Already running.")
            return

        self._source_lang = source_lang
        self._target_lang = target_lang
        self.audio_queue = Queue()
        self.asr_input_queue = Queue()
        self.text_queue = Queue()
        self.audio_capture = AudioCapture(
            audio_queue=self.audio_queue,
            sample_rate=self.config.sample_rate,
            channels=self.config.channels,
        )

        try:
            self.asr_engine = ASREngine(model_size=model_size, beam_size=self.config.beam_size)
        except Exception as exc:
            logger.exception("Unable to initialize ASR engine: %s", exc)
            self.status_updated.emit(f"ASR model init failed: {exc}")
            return

        try:
            self.audio_capture.start_capture()
        except Exception as exc:
            self.status_updated.emit(str(exc))
            return

        self._running = True
        self.running_state_changed.emit(True)
        self.status_updated.emit("Listening...")

        self._audio_thread = threading.Thread(target=self._audio_worker, daemon=True)
        self._asr_thread = threading.Thread(target=self._asr_worker, daemon=True)
        self._translation_thread = threading.Thread(target=self._translation_worker, daemon=True)
        self._audio_thread.start()
        self._asr_thread.start()
        self._translation_thread.start()

    def stop(self) -> None:
        """Stop capture and worker threads safely."""
        if not self._running:
            self.status_updated.emit("Already stopped.")
            return

        self._running = False
        self.audio_capture.stop_capture()

        for thread in (self._audio_thread, self._asr_thread, self._translation_thread):
            if thread and thread.is_alive():
                thread.join(timeout=1.5)

        self.running_state_changed.emit(False)
        self.status_updated.emit("Stopped.")
        self._export_transcript()

    def _audio_worker(self) -> None:
        """Collect raw audio and emit sentence-level chunks for ASR."""
        sentence_buffer = np.array([], dtype=np.float32)
        speech_started = False
        silence_samples = 0

        def finalize_sentence() -> None:
            nonlocal sentence_buffer, speech_started, silence_samples
            if sentence_buffer.size >= self._min_sentence_samples:
                self.asr_input_queue.put(sentence_buffer.copy())
            sentence_buffer = np.array([], dtype=np.float32)
            speech_started = False
            silence_samples = 0

        while self._running:
            try:
                data = self.audio_queue.get(timeout=0.2)
            except Empty:
                continue

            data = np.asarray(data, dtype=np.float32).reshape(-1)
            if data.size == 0:
                continue

            rms = float(np.sqrt(np.mean(np.square(data))))
            is_speech = rms >= self.config.rms_threshold

            if is_speech:
                speech_started = True
                silence_samples = 0
                sentence_buffer = np.concatenate([sentence_buffer, data])
            elif speech_started:
                sentence_buffer = np.concatenate([sentence_buffer, data])
                silence_samples += data.size

            if not speech_started:
                continue

            if sentence_buffer.size >= self._max_sentence_samples:
                finalize_sentence()
                continue

            if silence_samples >= self._silence_finalize_samples:
                finalize_sentence()

        # Flush remaining audio when worker stops.
        if sentence_buffer.size >= self._min_sentence_samples:
            self.asr_input_queue.put(sentence_buffer.copy())

    def _asr_worker(self) -> None:
        """Run speech recognition for each audio chunk."""
        while self._running:
            try:
                audio = self.asr_input_queue.get(timeout=0.3)
            except Empty:
                continue

            if self.asr_engine is None:
                continue
            result = self.asr_engine.transcribe(audio, language=self._source_lang)
            if result.error:
                logger.debug("ASR skipped: %s", result.error)
                continue
            # Show source subtitle immediately to reduce perceived latency.
            self.subtitle_updated.emit(result.text, "Translating...")
            self.status_updated.emit("Recognized. Translating...")
            self.text_queue.put(result.text)

    def _translation_worker(self) -> None:
        """Translate ASR text and update GUI signals."""
        while self._running:
            try:
                source_text = self.text_queue.get(timeout=0.3)
            except Empty:
                continue

            source_text = source_text.strip()
            if not source_text:
                continue
            translated = self.translator.translate(source_text, self._source_lang, self._target_lang)
            entry = self.subtitle_manager.add_subtitle(source_text, translated)
            if entry:
                self.subtitle_updated.emit(entry.source_text, entry.translated_text)
                self.status_updated.emit("Live")

    def _export_transcript(self) -> None:
        """Write transcript output when processing stops."""
        if not self.subtitle_manager.history:
            return
        TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = TRANSCRIPTS_DIR / "latest_transcript.txt"
        self.subtitle_manager.export_txt(output_path=Path(output_path))
        logger.info("Transcript exported: %s", output_path)

