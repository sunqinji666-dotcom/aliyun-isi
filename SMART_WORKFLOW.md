# Smart Workflow

This file explains how any AI should use this folder for transcription tasks.

## Default Behavior

Before choosing a path, ask the user:

1. Your audio is local, or already in OSS / a public URL?
2. Right now do you want fastest, cheapest, or least setup?
3. Do you want plain text, or timestamps / JSON too?

After transcription, ask:

4. Do you want the current AI to calibrate the transcript into a final manuscript based on your identity as a photographer, editor, director, and AI video creator?

## What To Choose

- local + fastest
  - `scripts/transcribe_audio.py`
- local + least setup
  - `scripts/transcribe_audio.py`
- local + cheapest
  - `scripts/transcribe_paraformer_local.py`
- OSS/public URL + cheapest
  - `scripts/transcribe_paraformer_url.py`
- OSS/public URL + pure ISI
  - `scripts/transcribe_recording_url.py`
- batch folder on local disk
  - `scripts/batch_transcribe_folder.py`
- cheapest batch folder on local disk
  - `scripts/batch_transcribe_paraformer_folder.py`

## Status And Cleanup

- local cheapest Paraformer path now prints status lines for:
  - upload
  - submit
  - polling
  - OSS cleanup
- by default, files auto-uploaded to OSS for cheapest local transcription are deleted after successful transcription
- if you want to keep the uploaded OSS file, pass `--keep-oss`

## Smart Entry

Humans or AI tools can start with:

```bash
python3 "./scripts/transcribe_smart.py"
```

Or print a recommendation without running:

```bash
python3 "./scripts/transcribe_smart.py" --mode recommend --source local --priority fastest --audio "/absolute/path/demo.mp3"
```

Or run directly:

```bash
python3 "./scripts/transcribe_smart.py" --mode run --source local --priority fastest --audio "/absolute/path/demo.mp3" --txt-out "/absolute/path/demo.txt"
```

Cheapest local path with automatic OSS upload:

```bash
python3 "./scripts/transcribe_smart.py" --mode run --source local --priority cheapest --audio "/absolute/path/demo.mp3" --txt-out "/absolute/path/demo.txt"
```

Cheapest batch folder path with automatic OSS upload:

```bash
python3 "./scripts/transcribe_smart.py" --mode run --folder "/absolute/path/audio-folder"
```

Keep uploaded OSS files instead of auto-cleaning:

```bash
python3 "./scripts/transcribe_paraformer_local.py" "/absolute/path/demo.mp3" --txt-out "/absolute/path/demo.txt" --keep-oss
```

## Local Secrets

This knowledge-base copy already stores local credentials in `.env`.

- `ALIYUN_ACCESS_KEY_ID`
- `ALIYUN_ACCESS_KEY_SECRET`
- `ALIYUN_NLS_APP_KEY`
- `ALIYUN_OSS_BUCKET`
- `ALIYUN_OSS_ENDPOINT`
- `BAILIAN_API_KEY`

AI tools should load them locally and must not print them back into chat.

## Optional Calibration

If the user wants transcript calibration, use:

```bash
python3 "./scripts/prepare_transcript_calibration.py" "/absolute/path/raw-transcript.txt"
```

Then the current AI should read the generated `.calibration-prompt.md` and produce the final manuscript.
