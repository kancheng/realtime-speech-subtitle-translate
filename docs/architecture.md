# Architecture

## Overview

系統採用分層與模組化設計，避免把所有邏輯塞在 `main.py`。

- `app/`：GUI 與流程控制
- `core/`：音訊擷取、ASR、翻譯、字幕資料管理、裝置判斷
- `config.py`：全域設定與 logging

## Runtime Flow

1. `AudioCapture` 用 `sounddevice` 接收麥克風資料，寫入 `audio_queue`
2. `AppController._audio_worker` 將音訊累積成 3 秒 chunk，做 RMS 靜音判斷
3. `ASREngine` 呼叫 `faster-whisper` 產生原文字幕
4. `Translator` 用 `argostranslate` 做離線翻譯
5. `SubtitleManager` 去重與保存字幕歷史
6. 透過 Qt signal 更新 `MainWindow` 的原文與翻譯欄位

## Threading Strategy

- 主執行緒：GUI（保持 UI 流暢）
- 背景執行緒：
  - audio worker
  - asr worker
  - translation worker

這種拆分可避免 ASR/翻譯阻塞 UI。

## Extension Points

- `SubtitleManager.export_srt()`：預留 SRT
- `AppController`：可加入 OBS/WebSocket 輸出
- `outputs/`：統一管理 transcript/subtitle 輸出

