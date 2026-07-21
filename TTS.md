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
cd "/Users/jacksun/Documents/知识库/aliyun-isi"
python3 -m pip install -r requirements.txt
```

## Short TTS

Output a short line as wav:

```bash
python3 "/Users/jacksun/Documents/知识库/aliyun-isi/scripts/synthesize_short_text.py" "这是一个临时旁白样音。" --out "/Users/jacksun/Documents/preview.wav"
```

Common knobs:

```bash
python3 "/Users/jacksun/Documents/知识库/aliyun-isi/scripts/synthesize_short_text.py" "请看下一条镜头转场。" --out "/Users/jacksun/Documents/preview.mp3" --format mp3 --voice xiaoyun --speech-rate 50 --pitch-rate 20
```

## Long TTS

Generate long-form speech and download the final file:

```bash
python3 "/Users/jacksun/Documents/知识库/aliyun-isi/scripts/synthesize_long_text.py" "这里放你的长文案内容" --download-to "/Users/jacksun/Documents/long-voice.wav" --json-out "/Users/jacksun/Documents/long-voice.json"
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
