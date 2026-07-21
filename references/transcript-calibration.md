# Transcript Calibration

Use this file when the user wants the raw transcript turned into a polished final manuscript.

## User Identity Defaults

Unless the user overrides it, calibrate for this working identity:

- photographer
- video editor
- director
- AI video creator

This means the final manuscript should preserve practical workflow language, production terms, prompt engineering terms, and creator-style spoken rhythm.

## Calibration Goals

1. Fix obvious ASR mistakes without over-rewriting.
2. Preserve the speaker's meaning, tone, and sales/teaching intent.
3. Keep creator jargon that fits AI video, directing, editing, prompting, shot design, storyboard, and production workflow.
4. Break long ASR walls of text into readable paragraphs.
5. Upgrade punctuation and sentence boundaries.
6. If a term is uncertain, mark it as `【待确认】` instead of hallucinating.

## What To Correct

- product names that were likely misheard
- AI tool names
- film/editing terms
- storyboard or directing terms
- prompt/template/workflow references
- obvious punctuation and paragraphing issues

## What Not To Do

- do not rewrite into stiff formal prose unless requested
- do not remove the creator's personality
- do not invent facts, tools, or URLs
- do not silently replace uncertain proper nouns with guesses

## Final Output Shape

When the user wants calibration, produce:

1. `粗转写稿`
2. `校准终稿`
3. `术语待确认`

If the transcript is already good, still produce a lightly cleaned final manuscript.
