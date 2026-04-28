# realtime-speech-subtitle-translate

A fully local, real-time speech-to-text and translation system that generates bilingual subtitles from live audio using Whisper-based ASR and offline translation.

## 1. 專案介紹

`realtime-speech-subtitle-translate` 是一個完全離線、完全免費的本機字幕工具。  
程式會即時收取麥克風音訊，使用 `faster-whisper` 做語音辨識，再用 `Argos Translate` 做離線翻譯，最後在 PyQt5 GUI 顯示雙語字幕。

## 2. 功能特色

- 本機端即時語音辨識（無需 API 金鑰）
- 本機端離線翻譯（Argos Translate）
- 雙語字幕即時顯示（原文 + 翻譯）
- 支援 CPU 模式，且可自動偵測 CUDA
- 模組化架構，方便擴充 OBS/SRT/WebSocket

## 3. 系統架構

```text
Microphone
-> Audio Capture (sounddevice)
-> ASR (faster-whisper)
-> Original Subtitle
-> Translation (Argos Translate)
-> Translated Subtitle
-> PyQt5 GUI
```

更多細節請參考 `docs/architecture.md`。

## 4. 安裝方式

### 環境需求

- Python 3.10 或 3.11
- Windows 10/11（本專案以 Windows 優先）

### 建立虛擬環境並安裝

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```

## 5. 執行方式

```bash
python main.py
```

操作流程：

1. 選擇 ASR 模型
2. 選擇來源語言與目標語言
3. 按 `Start`
4. 對麥克風說話
5. 觀看原文與翻譯字幕
6. 按 `Stop` 安全停止

## 6. 如何安裝 Argos Translate 語言模型

啟動程式時，若偵測到預設翻譯模型不存在，會先詢問你安裝方式：

- 預設語言對：`en -> zt` 與 `zt -> en`（英文 <-> 繁體中文）
- 預設選項：線上安裝（自動從 Argos package index 下載）
- 替代選項：手動指定資料夾，掃描並安裝 `*.argosmodel`

Argos package index：<https://www.argosopentech.com/argospm/index/>

### 方式 A：使用 Argos GUI/CLI 工具

可到 [Argos Translate 官方專案](https://github.com/argosopentech/argos-translate) 或 [Argos Package Index](https://www.argosopentech.com/argospm/index/) 下載語言模型後安裝。

### 方式 B：Python 腳本（手動執行）

```python
import argostranslate.package

available = argostranslate.package.get_available_packages()
package_to_install = next(
    p for p in available if p.from_code == "en" and p.to_code == "zt"
)
download_path = package_to_install.download()
argostranslate.package.install_from_path(download_path)
```

若未安裝對應語言包，GUI 會顯示：

`Translation package not installed for en to zt.`

## 7. CPU 模式說明

- 預設可在 CPU 上執行
- `faster-whisper` 在 CPU 下使用 `int8`
- 若沒有 GPU，也能完成整體流程

## 8. GPU 模式說明

- 若偵測到 CUDA，會自動使用 `device=cuda` 與 `compute_type=float16`
- 若 GPU 初始化失敗，會自動退回 CPU `int8`

## 9. 常見問題

- **Q: 按 Start 沒有字幕？**  
  A: 先確認麥克風權限、輸入裝置、以及語音音量是否高於 RMS 門檻。

- **Q: 只有原文沒有翻譯？**  
  A: 通常是尚未安裝對應 Argos 語言包。

- **Q: 沒有 NVIDIA GPU 可以用嗎？**  
  A: 可以，CPU 模式是完整支援的。

- **Q: 會把音訊上傳雲端嗎？**  
  A: 不會，所有處理都在本機端完成。

## 10. 未來 Roadmap

- SRT 輸出
- OBS 即時字幕輸出
- WebSocket 字幕推送
- 字幕緩衝與斷句策略優化
- 多語翻譯擴充與品質調校

