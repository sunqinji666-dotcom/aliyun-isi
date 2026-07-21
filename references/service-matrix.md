# Service Matrix

This file helps an AI choose the correct ISI capability before writing code.

## Recognition

### Sentence Recognition

- Best for short utterances, voice commands, search terms, and short chat turns.
- Use when audio is brief and response speed matters.

### Real-Time Speech Recognition

- Best for live streaming microphone input, meetings, subtitles, and long continuous speech.
- Use when audio arrives as a stream and partial results matter.

### Recording File Recognition

- Best for uploaded recordings and offline transcription flows.
- Use when the entire file already exists before processing.

## Synthesis

### Standard TTS

- Best for short messages, voice prompts, agent replies, and quick playback.
- Use when each synthesis request is short and interactive.

### Long-Text TTS

- Best for articles, chapters, and long-form reading scenarios.
- Use when the input text exceeds normal short TTS request patterns.

## Default Decision Rules

- Live mic + ongoing transcript -> real-time ASR
- Uploaded audio file -> recording file recognition
- Button click saying one short sentence -> standard TTS
- Long article playback -> long-text TTS

## Format Guardrails

According to the official feature/concepts pages, recognition services commonly expect constrained audio formats and are sensitive to channel count, sample rate, and encoding. Unless the user gives a better requirement:

- default recognition examples to mono audio
- default to 16-bit PCM for backend normalization examples
- call out sample-rate validation explicitly

Before finalizing production code, verify the selected API's exact format rules in the official docs.
