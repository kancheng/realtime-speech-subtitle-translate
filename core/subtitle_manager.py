"""Subtitle history and export helper."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class SubtitleEntry:
    """Represents one bilingual subtitle item."""

    timestamp: datetime
    source_text: str
    translated_text: str


class SubtitleManager:
    """Manage deduplication, merge rules, and transcript export."""

    def __init__(self, max_history: int = 100) -> None:
        self.max_history = max_history
        self._history: List[SubtitleEntry] = []
        self._last_source: str = ""

    @property
    def history(self) -> List[SubtitleEntry]:
        """Get copy of subtitle history."""
        return list(self._history)

    def add_subtitle(self, source_text: str, translated_text: str) -> Optional[SubtitleEntry]:
        """Add subtitle if valid and not duplicated."""
        source = source_text.strip()
        translated = translated_text.strip()
        if not source:
            return None
        if source == self._last_source:
            return None

        # Basic short sentence merge hook for future extension.
        if self._history and len(source) < 6:
            source = f"{self._history[-1].source_text} {source}".strip()
            translated = f"{self._history[-1].translated_text} {translated}".strip()
            self._history.pop()

        entry = SubtitleEntry(
            timestamp=datetime.now(),
            source_text=source,
            translated_text=translated,
        )
        self._history.append(entry)
        self._last_source = source

        if len(self._history) > self.max_history:
            self._history = self._history[-self.max_history :]

        return entry

    def export_txt(self, output_path: Path) -> Path:
        """Export subtitle history to plain text file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for entry in self._history:
            ts = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"[{ts}] {entry.source_text}")
            lines.append(f"           {entry.translated_text}")
            lines.append("")
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    def export_srt(self, output_path: Path) -> None:
        """Placeholder for future SRT export support."""
        raise NotImplementedError("SRT export is reserved for future versions.")

