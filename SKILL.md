---
name: aliyun-isi
description: Use this skill when an AI agent needs to help with audio-to-text or text-to-speech workflows for editors, directors, and creators using Alibaba Cloud ISI or Bailian Paraformer. This skill includes smart routing between fastest, cheapest, and least-setup paths, local-file transcription, OSS URL transcription, batch folder transcription, short TTS, long TTS, and local secret-aware execution.
---

# Aliyun ISI

中文名：阿里云语音工具

## Overview

This skill packages Alibaba Cloud speech workflows into an AI-readable integration guide. Use it when building, choosing, or running speech recognition and speech synthesis workflows backed by Aliyun ISI or Bailian Paraformer.

This skill is designed to be portable. Any AI tool that can read this folder should be able to understand the service, choose the right capability, and produce implementation work with sane defaults.

For this knowledge-base copy, the most practical ready-to-run workflows are already implemented for editors and directors:

1. local audio to text
2. remote URL recording transcription
3. short text to speech
4. long text to speech
5. cheapest URL transcription with Bailian Paraformer
6. smart routing that asks a few short questions before choosing
7. cheapest local transcription with automatic OSS upload
8. cheapest local folder batch transcription with automatic OSS upload
9. optional transcript calibration into a final manuscript using the current AI model
10. AI video glossary-aware cleanup for transcript calibration
11. automatic cost and elapsed-time logging for transcription jobs

## Mandatory Intake

Before choosing a transcription path, read [references/editor-intake.md](references/editor-intake.md) and ask the user these short questions unless the answer is already obvious:

1. Is the audio local on disk, or already in OSS / a public URL?
2. Which matters most right now: fastest, cheapest, or least setup?
3. Do you want plain text only, or timestamps / JSON too?
4. After transcription, do you want me to calibrate it into a final manuscript based on your identity as a photographer, editor, director, and AI creator?

If the user does not answer, infer from context and keep moving.

## Quick Start

When this skill is invoked, do the work in this order:

1. Identify the target capability:
   - Short audio ASR: sentence recognition
   - Streaming ASR: real-time speech recognition
   - File transcription: recording file recognition
   - Standard TTS: text up to short-request limits
   - Long-form TTS: long text synthesis
2. Confirm the delivery shape:
   - Backend API only
   - Web or mobile app calling a backend
   - Server-to-server batch job
   - Demo script or proof of concept
3. Gather or infer the minimum config:
   - `ALIYUN_ACCESS_KEY_ID`
   - `ALIYUN_ACCESS_KEY_SECRET`
   - `ALIYUN_NLS_APP_KEY`
   - region or endpoint if the target code needs it
4. Default to a secure architecture:
   - Never put AccessKey secrets in frontend code
   - Frontend/mobile apps should request a short-lived Token from a backend
   - Backend owns credential exchange with Aliyun
5. Deliver production-usable output:
   - env var names
   - API route contract
   - runnable sample code
   - failure handling and format constraints

## Capability Routing

- If the user wants "语音转文字" for live microphone, use real-time ASR.
- If the user wants "上传录音后转写", use recording file recognition.
- If the user wants "把文字读出来", use TTS.
- If the user wants long article or novel playback, use long-text TTS.
- If the user is not sure, read [references/service-matrix.md](references/service-matrix.md) first and choose the narrowest service that matches the scenario.

## Ready Workflows In This Folder

- Fast local audio transcription:
  - [TRANSCRIBE.md](TRANSCRIBE.md)
  - [transcribe_audio.py](scripts/transcribe_audio.py)
- Async remote recording transcription:
  - [TRANSCRIBE.md](TRANSCRIBE.md)
  - [transcribe_recording_url.py](scripts/transcribe_recording_url.py)
- Short text synthesis:
  - [TTS.md](TTS.md)
  - [synthesize_short_text.py](scripts/synthesize_short_text.py)
- Long text synthesis:
  - [TTS.md](TTS.md)
  - [synthesize_long_text.py](scripts/synthesize_long_text.py)
- Cheapest OSS/public URL transcription:
  - [SMART_WORKFLOW.md](SMART_WORKFLOW.md)
  - [transcribe_paraformer_url.py](scripts/transcribe_paraformer_url.py)
- Cheapest local transcription with automatic OSS upload:
  - [SMART_WORKFLOW.md](SMART_WORKFLOW.md)
  - [transcribe_paraformer_local.py](scripts/transcribe_paraformer_local.py)
- Smart routing entry:
  - [SMART_WORKFLOW.md](SMART_WORKFLOW.md)
  - [transcribe_smart.py](scripts/transcribe_smart.py)
- Cheapest local folder batch transcription:
  - [TRANSCRIBE.md](TRANSCRIBE.md)
  - [batch_transcribe_paraformer_folder.py](scripts/batch_transcribe_paraformer_folder.py)
- Transcript calibration:
  - [CALIBRATE.md](CALIBRATE.md)
  - [transcript-calibration.md](references/transcript-calibration.md)
  - [prepare_transcript_calibration.py](scripts/prepare_transcript_calibration.py)
- AI video glossary:
  - [ai-video-glossary.md](references/ai-video-glossary.md)
  - [ai-video-term-map.json](references/ai-video-term-map.json)
- Pricing reference:
  - [PRICING.md](PRICING.md)
  - real-time price lookup for Paraformer, Fun-ASR, Qwen ASR, GUMMY, SenseVoice
  - OSS storage and transfer cost reference
  - per-job cost logging to `logs/usage_history.*`

If the user is a video editor, content creator, or director:

- use fast local transcription for subtitle rough drafts
- use async URL transcription for formal archive or large material transcription
- use Bailian Paraformer for the cheapest URL-based transcription path
- use short TTS for preview narration and pacing tests
- use long TTS for full commentary drafts and course narration demos
- offer optional transcript calibration into a cleaner final manuscript

## Local Config

This knowledge-base copy expects local credentials to live in `.env` in this folder. AI tools may read them locally, but must never echo them back in chat.

Relevant local keys include:

- `ALIYUN_ACCESS_KEY_ID`
- `ALIYUN_ACCESS_KEY_SECRET`
- `ALIYUN_NLS_APP_KEY`
- `ALIYUN_OSS_BUCKET`
- `ALIYUN_OSS_ENDPOINT`
- `BAILIAN_API_KEY`

## Cost Tracking

Every transcription job should append a usage record under:

- `logs/usage_history.csv`
- `logs/usage_history.jsonl`

These logs are used to compare:

- fastest route
- cheapest route
- elapsed time
- estimated cost

For real-time pricing, refer to [PRICING.md](PRICING.md). Key baselines (all pay-as-you-go):

- **Paraformer 录音文件识别**: 0.00008 元/秒（≈ 0.29 元/小时）— cheapest and recommended
- **Fun-ASR 录音文件识别**: 0.00022 元/秒（≈ 0.79 元/小时）
- **Paraformer 实时识别**: 0.00024 元/秒（≈ 0.86 元/小时）
- **GUMMY**: 0.00015 元/秒（≈ 0.54 元/小时）
- **SenseVoice**: 0.0007 元/秒（≈ 2.52 元/小时）
- OSS upload traffic is free; storage is ~0.12 元/GB/month

## Integration Rules

- Prefer official Aliyun SDKs or official API patterns over third-party wrappers.
- Keep auth on the server side unless the official pattern explicitly uses a client Token.
- Treat `AppKey` and `Token` as distinct:
  - `AppKey` identifies the ISI project/application.
  - `Token` is a short-lived credential used by clients or SDK calls.
- If the user only gives AccessKey credentials and no `AppKey`, stop generating final code until the project/AppKey path is accounted for.
- If audio input format is unclear, default to mono, 16-bit PCM, 16 kHz for recognition-oriented examples and explicitly note that the final format must match the selected API's constraints.

## Output Contract

When producing code or setup instructions with this skill, include:

1. What ISI feature is being used and why.
2. Required console-side setup:
   - service activation
   - RAM permission if applicable
   - project creation
   - AppKey retrieval
   - Token flow
3. Required env vars.
4. A backend-first integration path.
5. At least one test or verification step.
6. Common failure points:
   - wrong audio format
   - expired Token
   - missing AppKey
   - frontend secret leakage
   - capability mismatch between scenario and API

## Working Style

- For implementation tasks, read [references/implementation-patterns.md](references/implementation-patterns.md).
- For product/scope questions, read [references/service-matrix.md](references/service-matrix.md).
- For source attribution and official entry points, read [references/official-links.md](references/official-links.md).
- If the runtime is unspecified, prefer Node.js for web backends and Python for batch jobs.
- Keep code snippets small but runnable.
- If the user asks for "开箱即用", generate:
  - `.env.example`
  - direct-use scripts for the requested workflow
  - one verification command
  - a brief explanation of why that route was chosen

## Calibration Rules

If the user wants calibration:

1. Read [references/transcript-calibration.md](references/transcript-calibration.md)
2. Read [references/ai-video-glossary.md](references/ai-video-glossary.md)
3. Apply the term map from `references/ai-video-term-map.json` during rough cleanup when useful
4. Preserve creator tone and domain terms
5. Correct obvious ASR mistakes conservatively
6. Mark uncertain proper nouns as `【待确认】`
7. Produce a final manuscript, not just a raw dump

## Ready Prompts

Example prompts another AI can use directly:

- "Use `aliyun-isi` to add Aliyun TTS to this Node.js backend and expose a `/api/tts` endpoint."
- "Use `aliyun-isi` to design a secure Token issuing backend for a web speech recognition app."
- "Use `aliyun-isi` to compare real-time ASR vs recording-file transcription for this product requirement."
- "Use `aliyun-isi` to troubleshoot why this Aliyun speech integration returns auth or format errors."
- "Use `aliyun-isi` to ask me a few short questions and choose the best transcription path for my current audio."
- "Use `aliyun-isi` to transcribe this audio and then optionally calibrate the manuscript for my editor/director workflow."
