# Calibration

After transcription, the current AI should ask:

`要不要我按你“摄影、剪辑、导演、AI 视频创作”的身份，把这份转写稿校准成可直接使用的最终文稿？`

If the answer is yes:

1. Read [references/transcript-calibration.md](references/transcript-calibration.md)
2. Read [references/ai-video-glossary.md](references/ai-video-glossary.md)
3. Read the raw transcript file
4. Produce:
   - a cleaned rough draft
   - a calibrated final manuscript
   - a short list of uncertain terms if any

## Suggested Output Files

- raw transcript:
  - `name.txt`
- cleaned rough draft:
  - `name.rough.md`
- final calibrated manuscript:
  - `name.final.md`
- optional calibration prompt bundle for another AI:
  - `name.calibration-prompt.md`

## Automation Boundary

This folder includes a helper script that prepares a calibration package, but the semantic calibration itself should be done by the currently running AI model.
