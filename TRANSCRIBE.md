# Audio To Text

If your only goal is "I have an audio file and want text quickly", start with the local fast transcription script in this folder.

## What This Uses

This folder now supports two transcription modes:

- `scripts/transcribe_audio.py`
  - local file upload
  - fastest way to turn a local file into text
  - best for editors cutting subtitles from existing clips
- `scripts/transcribe_recording_url.py`
  - async transcription for a remote audio URL
  - better for large files, OSS-based workflows, and formal batch jobs

## Install

```bash
cd "/Users/jacksun/Documents/知识库/aliyun-isi"
python3 -m pip install -r requirements.txt
```

## Fast Local File To Text

```bash
python3 "/Users/jacksun/Documents/知识库/aliyun-isi/scripts/transcribe_audio.py" "/absolute/path/to/your-audio.wav"
```

Save plain text:

```bash
python3 "/Users/jacksun/Documents/知识库/aliyun-isi/scripts/transcribe_audio.py" "/absolute/path/to/your-audio.wav" --txt-out "/absolute/path/to/result.txt"
```

Save raw JSON too:

```bash
python3 "/Users/jacksun/Documents/知识库/aliyun-isi/scripts/transcribe_audio.py" "/absolute/path/to/your-audio.wav" --txt-out "/absolute/path/to/result.txt" --json-out "/absolute/path/to/result.json"
```

## Remote URL To Text

Use this when the file already lives on OSS or another public HTTPS URL:

```bash
python3 "/Users/jacksun/Documents/知识库/aliyun-isi/scripts/transcribe_recording_url.py" "https://your-bucket.oss-cn-shanghai.aliyuncs.com/demo.wav" --txt-out "/absolute/path/to/result.txt"
```

## Batch A Folder

If you have a whole folder of lesson audio, interviews, or course recordings:

```bash
python3 "/Users/jacksun/Documents/知识库/aliyun-isi/scripts/batch_transcribe_folder.py" "/Users/jacksun/Desktop/Seedance2.0教学_音频"
```

This creates a `转写结果` folder beside the audio files and saves one `.txt` per source file.

By default, batch mode now skips files that already have output results in the target folder. If you really want to run them again, add `--force-rerun`.

## Cheapest Batch Folder

If you want the cheapest local-folder path and already configured OSS + Bailian:

```bash
python3 "/Users/jacksun/Documents/知识库/aliyun-isi/scripts/batch_transcribe_paraformer_folder.py" "/Users/jacksun/Desktop/Seedance2.0教学_音频"
```

This creates a `转写结果-百炼` folder beside the audio files and uploads each file to OSS automatically before running Paraformer.

By default, the temporary OSS object uploaded for each local file is deleted after transcription so it does not keep occupying bucket storage. If you want to keep OSS copies, add `--keep-oss`.

By default, this batch mode also skips files that already have output results. Use `--force-rerun` only when you really want to pay to transcribe them again.

## Cost And Timing Logs

Every transcription job now appends history to:

- `/Users/jacksun/Documents/知识库/aliyun-isi/logs/usage_history.csv`
- `/Users/jacksun/Documents/知识库/aliyun-isi/logs/usage_history.jsonl`

Logged fields include:

- engine
- source path
- audio duration
- task elapsed time
- estimated cost in CNY
- output paths

## AI Video Term Cleanup

Calibration now uses a creator-focused AI video glossary and term map:

- [ai-video-glossary.md](references/ai-video-glossary.md)
- [ai-video-term-map.json](references/ai-video-term-map.json)

This helps clean up terms such as `Seedance 2.0`, `Sora`, `豆包`, `RunningHub`, `分镜图`, and related workflow language.

## Optional Calibration

If you want the current AI to polish a raw transcript into a final manuscript for your creator/editor/director workflow:

```bash
python3 "/Users/jacksun/Documents/知识库/aliyun-isi/scripts/prepare_transcript_calibration.py" "/absolute/path/to/raw.txt"
```

This generates:

- `raw.rough.md`
- `raw.calibration-prompt.md`
- a suggested `raw.final.md` target path

## Defaults

- region: `cn-shanghai`
- sample rate: `16000`
- first channel only: enabled

## Important

- Supported local upload formats in this script: `wav`, `mp3`, `mp4`, `aac`, `opus`
- Phone audio can use `--sample-rate 8000`
- If a stereo file produces duplicated text, keep the default single-channel behavior
- The async URL script expects a file URL reachable by Aliyun. OSS is the safest default.

## Official Context

According to Aliyun's official docs:

- FlashRecognizer accepts local binary upload over HTTPS POST
- required request params include `appkey`, `token`, `format`, and usually `sample_rate`
- local-file upload is the right path when you already have a local audio file and want a fast result

See:

- https://help.aliyun.com/zh/isi/developer-reference/sdk-reference-9
- https://help.aliyun.com/zh/isi/developer-reference/sdk-for-python-3
- https://help.aliyun.com/zh/isi/getting-started/obtain-an-access-token
