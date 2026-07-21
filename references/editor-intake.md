# Editor Intake

This file defines the mandatory intake flow for any AI that uses this skill for audio transcription.

## Ask These First

When the user asks to convert audio to text, ask at most these 3 short questions before choosing a path:

1. Is the audio local on disk, or already in OSS / a public URL?
2. Which matters most right now: fastest, cheapest, or least setup?
3. Do you want plain text only, or timestamps / JSON too?

If the user does not answer clearly, infer from the context:

- local files + wants to start immediately -> use ISI FlashRecognizer
- OSS URL + wants lowest cost -> use Bailian Paraformer
- OSS URL + wants pure ISI workflow -> use ISI recording-file recognition
- overnight batch job + lowest ISI cost -> use ISI idle edition

## Routing Rules

- `Fastest and least friction`
  - ISI FlashRecognizer
  - local files are acceptable
  - best default for editors
- `Cheapest`
  - Bailian Paraformer
  - requires OSS/public URL
- `Pure ISI async transcription`
  - ISI recording-file recognition
  - requires OSS/public URL
- `Cheapest inside ISI family`
  - ISI idle edition
  - requires OSS/public URL
  - do not present as a fast path

## Secret Handling

- Local config lives in `.env` in this folder.
- Read keys locally if needed.
- Never echo secrets back to the user.
- If a key has already appeared in chat, recommend rotation after testing.
