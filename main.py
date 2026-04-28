"""Entry point for realtime-speech-subtitle-translate."""

from __future__ import annotations

import logging
import sys

from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

from app.controller import AppController
from app.gui import MainWindow
from config import ASR_MODEL_OPTIONS, LANGUAGE_OPTIONS, AppConfig, configure_logging
from core.translator import ARGOS_PACKAGE_INDEX_URL, Translator

logger = logging.getLogger(__name__)


def _prompt_argos_setup(app: QApplication, translator: Translator) -> None:
    """Ask user how to prepare default Argos en<->zt translation packages."""
    if translator.default_pairs_ready():
        return

    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Information)
    dialog.setWindowTitle("Argos 模型安裝")
    dialog.setText("尚未偵測到預設翻譯模型：英文↔繁體中文 (en↔zt)")
    dialog.setInformativeText(
        "建議先安裝預設模型。\n"
        "可選擇線上安裝，或先手動下載後指定資料夾掃描。\n"
        f"下載索引：{ARGOS_PACKAGE_INDEX_URL}"
    )
    online_button = dialog.addButton("線上安裝（預設）", QMessageBox.AcceptRole)
    manual_button = dialog.addButton("手動資料夾安裝", QMessageBox.ActionRole)
    skip_button = dialog.addButton("略過", QMessageBox.RejectRole)
    dialog.setDefaultButton(online_button)
    dialog.exec_()

    clicked = dialog.clickedButton()
    if clicked == online_button:
        try:
            ok = translator.install_defaults_online()
            if not ok:
                QMessageBox.warning(
                    None,
                    "Argos 安裝結果",
                    "線上安裝未完整成功，請改用手動下載模式。",
                )
        except Exception as exc:
            logger.exception("Online Argos install failed: %s", exc)
            QMessageBox.warning(
                None,
                "Argos 安裝失敗",
                f"線上安裝失敗：{exc}\n可改用手動資料夾安裝。",
            )
        return

    if clicked == manual_button:
        selected_dir = QFileDialog.getExistingDirectory(
            None,
            "請選擇 Argos 模型資料夾（含 .argosmodel）",
            "F:/newproj/model",
        )
        if not selected_dir:
            return
        try:
            count = translator.install_from_directory(selected_dir)
            QMessageBox.information(
                None,
                "Argos 安裝結果",
                f"已從指定目錄安裝 {count} 個模型檔。",
            )
        except Exception as exc:
            logger.exception("Manual Argos install failed: %s", exc)
            QMessageBox.warning(None, "Argos 安裝失敗", f"手動安裝失敗：{exc}")
        return

    if clicked == skip_button:
        logger.info("User skipped Argos model setup.")


def main() -> int:
    """Start the PyQt5 application."""
    configure_logging()
    app_config = AppConfig()
    app = QApplication(sys.argv)
    setup_translator = Translator()
    _prompt_argos_setup(app=app, translator=setup_translator)

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

