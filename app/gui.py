"""PyQt5 GUI for real-time bilingual subtitle display."""

from __future__ import annotations

from typing import Dict, List, Tuple

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.styles import MAIN_STYLESHEET


class PPTSubtitleOverlay(QWidget):
    """Top-most subtitle-only window for PPT fullscreen presentations."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PPT Subtitle Overlay")
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setStyleSheet(
            """
            QWidget {
                background-color: rgba(0, 0, 0, 190);
                border: 2px solid #2E7D32;
                border-radius: 12px;
            }
            QLabel {
                color: #FFFFFF;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(8)

        self.original_label = QLabel("")
        self.original_label.setWordWrap(True)
        self.original_label.setStyleSheet("font-size: 34px; font-weight: 700;")
        layout.addWidget(self.original_label)

        self.translated_label = QLabel("")
        self.translated_label.setWordWrap(True)
        self.translated_label.setStyleSheet("font-size: 30px; color: #B9F6CA;")
        layout.addWidget(self.translated_label)

    def position_for_presentation(self) -> None:
        """Place overlay near the bottom of primary screen."""
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.availableGeometry()
        width = int(geometry.width() * 0.9)
        height = int(geometry.height() * 0.26)
        x = geometry.x() + (geometry.width() - width) // 2
        y = geometry.y() + int(geometry.height() * 0.70)
        self.setGeometry(x, y, width, height)

    def update_subtitles(self, source_text: str, translated_text: str) -> None:
        """Update subtitle text shown in overlay."""
        self.original_label.setText(source_text)
        self.translated_label.setText(translated_text)


class MainWindow(QMainWindow):
    """Main desktop window for subtitle application."""

    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def __init__(self, model_options: List[str], language_options: List[Tuple[str, str]]) -> None:
        super().__init__()
        self.model_options = model_options
        self.language_options = language_options
        self.overlay_window: PPTSubtitleOverlay | None = None
        self.setWindowTitle("Realtime Speech Subtitle Translate")
        self.resize(420, 820)
        self.setMinimumSize(360, 700)
        self.setStyleSheet(MAIN_STYLESHEET)
        self._build_ui()

    def _build_ui(self) -> None:
        container = QWidget(self)
        root_layout = QVBoxLayout(container)
        root_layout.setSpacing(10)
        root_layout.setContentsMargins(14, 14, 14, 14)

        title = QLabel("Realtime Speech Subtitle Translate")
        title.setStyleSheet("font-size: 28px; font-weight: 700;")
        root_layout.addWidget(title)

        controls_layout = QFormLayout()
        controls_layout.setVerticalSpacing(8)
        controls_layout.setHorizontalSpacing(10)
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.model_options)
        controls_layout.addRow("ASR Model", self.model_combo)

        self.source_combo = QComboBox()
        for name, code in self.language_options:
            self.source_combo.addItem(f"{name} ({code})", code)
        controls_layout.addRow("Source Language", self.source_combo)

        self.target_combo = QComboBox()
        for name, code in self.language_options:
            self.target_combo.addItem(f"{name} ({code})", code)
        controls_layout.addRow("Target Language", self.target_combo)

        root_layout.addLayout(controls_layout)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_requested.emit)
        self.stop_button.clicked.connect(self.stop_requested.emit)
        self.ppt_button = QPushButton("PPT 字幕模式")
        self.ppt_button.setObjectName("pptButton")
        self.ppt_button.clicked.connect(self.toggle_ppt_mode)
        button_row = QHBoxLayout()
        button_row.addWidget(self.start_button)
        button_row.addWidget(self.stop_button)
        root_layout.addLayout(button_row)
        root_layout.addWidget(self.ppt_button)

        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("font-size: 20px; color: #81C784;")
        root_layout.addWidget(self.status_label)

        panel = QFrame()
        panel.setObjectName("subtitlePanel")
        panel_layout = QVBoxLayout(panel)

        source_title = QLabel("Original Subtitle")
        source_title.setStyleSheet("font-size: 21px; font-weight: 600;")
        panel_layout.addWidget(source_title)
        self.source_text = QTextEdit()
        self.source_text.setReadOnly(True)
        self.source_text.setStyleSheet("font-size: 36px;")
        panel_layout.addWidget(self.source_text)

        translated_title = QLabel("Translated Subtitle")
        translated_title.setStyleSheet("font-size: 21px; font-weight: 600;")
        panel_layout.addWidget(translated_title)
        self.translated_text = QTextEdit()
        self.translated_text.setReadOnly(True)
        self.translated_text.setStyleSheet("font-size: 32px;")
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
        if self.overlay_window is not None and self.overlay_window.isVisible():
            self.overlay_window.update_subtitles(source_text, translated_text)

    def toggle_ppt_mode(self) -> None:
        """Toggle subtitle-only overlay window for PPT fullscreen mode."""
        if self.overlay_window is None:
            self.overlay_window = PPTSubtitleOverlay()

        if self.overlay_window.isVisible():
            self.overlay_window.hide()
            self.ppt_button.setText("PPT 字幕模式")
            return

        self.overlay_window.position_for_presentation()
        self.overlay_window.update_subtitles(
            self.source_text.toPlainText(),
            self.translated_text.toPlainText(),
        )
        self.overlay_window.show()
        self.overlay_window.raise_()
        self.ppt_button.setText("關閉 PPT 字幕模式")

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

    def closeEvent(self, event) -> None:  # type: ignore[override]
        """Close overlay window with main window."""
        if self.overlay_window is not None:
            self.overlay_window.close()
        super().closeEvent(event)

