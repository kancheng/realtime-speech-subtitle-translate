# Usage Guide

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## GUI Controls

- **ASR Model**：`tiny/base/small/medium`
- **Source Language**：來源語言
- **Target Language**：翻譯目標語言
- **Start**：開始收音與背景辨識/翻譯
- **Stop**：停止所有背景流程並輸出 transcript

## Recommended First Test

1. `ASR Model` 選 `base`
2. `Source Language` 選 `en`
3. `Target Language` 選 `zh`
4. 按 `Start` 後對麥克風說英文
5. 觀察原文字幕是否更新
6. 若已安裝 en->zh Argos 包，翻譯字幕會同步更新

## Output Files

- `outputs/transcripts/latest_transcript.txt`

## Troubleshooting

- 無法啟動麥克風：檢查系統音訊權限與裝置占用
- 翻譯顯示 package not installed：安裝對應 Argos 語言包
- 辨識不到聲音：提高說話音量或降低 RMS threshold

