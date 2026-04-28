"""Entry point for realtime-speech-subtitle-translate."""

from __future__ import annotations

import sys

from PyQt5.QtWidgets import QApplication

from app.controller import AppController
from app.gui import MainWindow
from config import ASR_MODEL_OPTIONS, LANGUAGE_OPTIONS, AppConfig, configure_logging


def main() -> int:
    """Start the PyQt5 application."""
    configure_logging()
    app_config = AppConfig()
    app = QApplication(sys.argv)

    window = MainWindow(model_options=list(ASR_MODEL_OPTIONS), language_options=list(LANGUAGE_OPTIONS))
    window.set_defaults(
        model_size=app_config.default_model_size,
        source_lang=app_config.default_source_language,
        target_lang=app_config.default_target_language,
    )
    controller = AppController(config=app_config)

    window.start_requested.connect(
        lambda: controller.start(
            model_size=window.get_selected_options()["model_size"],
            source_lang=window.get_selected_options()["source_lang"],
            target_lang=window.get_selected_options()["target_lang"],
        )
    )
    window.stop_requested.connect(controller.stop)
    controller.subtitle_updated.connect(window.update_subtitles)
    controller.status_updated.connect(window.set_status)
    controller.running_state_changed.connect(window.set_running_state)

    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())

