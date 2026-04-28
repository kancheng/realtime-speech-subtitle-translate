"""PyQt5 GUI for real-time bilingual subtitle display."""

from __future__ import annotations

from typing import Dict, List, Tuple

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.styles import MAIN_STYLESHEET


class MainWindow(QMainWindow):
    """Main desktop window for subtitle application."""

    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def __init__(self, model_options: List[str], language_options: List[Tuple[str, str]]) -> None:
        super().__init__()
        self.model_options = model_options
        self.language_options = language_options
        self.setWindowTitle("Realtime Speech Subtitle Translate")
        self.resize(980, 700)
        self.setStyleSheet(MAIN_STYLESHEET)
        self._build_ui()

    def _build_ui(self) -> None:
        container = QWidget(self)
        root_layout = QVBoxLayout(container)
        root_layout.setSpacing(12)

        title = QLabel("Realtime Speech Subtitle Translate")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        root_layout.addWidget(title)

        controls_layout = QHBoxLayout()

        self.model_combo = QComboBox()
        self.model_combo.addItems(self.model_options)
        controls_layout.addWidget(QLabel("ASR Model:"))
        controls_layout.addWidget(self.model_combo)

        self.source_combo = QComboBox()
        for name, code in self.language_options:
            self.source_combo.addItem(f"{name} ({code})", code)
        controls_layout.addWidget(QLabel("Source Language:"))
        controls_layout.addWidget(self.source_combo)

        self.target_combo = QComboBox()
        for name, code in self.language_options:
            self.target_combo.addItem(f"{name} ({code})", code)
        controls_layout.addWidget(QLabel("Target Language:"))
        controls_layout.addWidget(self.target_combo)

        root_layout.addLayout(controls_layout)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_requested.emit)
        self.stop_button.clicked.connect(self.stop_requested.emit)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        root_layout.addLayout(button_layout)

        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("font-size: 14px; color: #90CAF9;")
        root_layout.addWidget(self.status_label)

        panel = QFrame()
        panel.setObjectName("subtitlePanel")
        panel_layout = QVBoxLayout(panel)

        source_title = QLabel("Original Subtitle")
        source_title.setStyleSheet("font-size: 17px; font-weight: 600;")
        panel_layout.addWidget(source_title)
        self.source_text = QTextEdit()
        self.source_text.setReadOnly(True)
        self.source_text.setStyleSheet("font-size: 28px;")
        panel_layout.addWidget(self.source_text)

        translated_title = QLabel("Translated Subtitle")
        translated_title.setStyleSheet("font-size: 16px; font-weight: 600;")
        panel_layout.addWidget(translated_title)
        self.translated_text = QTextEdit()
        self.translated_text.setReadOnly(True)
        self.translated_text.setStyleSheet("font-size: 22px;")
        panel_layout.addWidget(self.translated_text)

        root_layout.addWidget(panel)
        self.setCentralWidget(container)

    def set_running_state(self, running: bool) -> None:
        """Update button state for running/stopped modes."""
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(running)

    def set_status(self, text: str) -> None:
        """Show status message."""
        self.status_label.setText(f"Status: {text}")

    def update_subtitles(self, source_text: str, translated_text: str) -> None:
        """Refresh subtitle text areas."""
        self.source_text.setPlainText(source_text)
        self.translated_text.setPlainText(translated_text)

    def get_selected_options(self) -> Dict[str, str]:
        """Get current dropdown selections."""
        return {
            "model_size": self.model_combo.currentText(),
            "source_lang": self.source_combo.currentData(),
            "target_lang": self.target_combo.currentData(),
        }

    def set_defaults(self, model_size: str, source_lang: str, target_lang: str) -> None:
        """Set default dropdown values."""
        model_index = self.model_combo.findText(model_size)
        if model_index >= 0:
            self.model_combo.setCurrentIndex(model_index)

        source_index = self.source_combo.findData(source_lang)
        if source_index >= 0:
            self.source_combo.setCurrentIndex(source_index)

        target_index = self.target_combo.findData(target_lang)
        if target_index >= 0:
            self.target_combo.setCurrentIndex(target_index)

