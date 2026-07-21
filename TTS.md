# Text To Speech

This folder now supports two synthesis modes:

- `scripts/synthesize_short_text.py`
  - short text
  - faster turnaround
  - good for temp narration, scratch voice-over, demo lines, preview playback
- `scripts/synthesize_long_text.py`
  - long text
  - async polling workflow
  - good for full narration drafts, articles, course scripts, and long-form reading

## Install

```bash
cd "."
python3 -m pip install -r requirements.txt
```

## Short TTS

Output a short line as wav:

```bash
python3 "./scripts/synthesize_short_text.py" "这是一个临时旁白样音。" --out "/path/to/output.wav"
```

Common knobs:

```bash
python3 "./scripts/synthesize_short_text.py" "请看下一条镜头转场。" --out "/path/to/output.mp3" --format mp3 --voice xiaoyun --speech-rate 50 --pitch-rate 20
```

## Long TTS

Generate long-form speech and download the final file:

```bash
python3 "./scripts/synthesize_long_text.py" "这里放你的长文案内容" --download-to "/path/to/output.wav" --json-out "/path/to/output.json"
```

## Best Use For Editors And Directors

- short TTS:
  - trial voice for rough cut
  - temporary narration before final dubbing
  - pacing tests for trailer or promo edits
- long TTS:
  - course narration draft
  - article-to-audio preview
  - long commentary scratch track

## Official Context

- Python short/real-time TTS SDK:
  - https://help.aliyun.com/zh/isi/developer-reference/sdk-for-python-1
- Long-text async REST API:
  - https://help.aliyun.com/zh/isi/developer-reference/restful-api
