#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aliyun_isi_common import ENV_PATH, WS_TTS_ENDPOINTS, app_key, create_token, default_region, load_env


class FileSpeechSynthesizer:
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self._file = output_path.open("wb")
        self._error_message: str | None = None

    def on_metainfo(self, message: str, *args) -> None:
        if message:
            print(f"metainfo: {message}", file=sys.stderr)

    def on_data(self, data: bytes, *args) -> None:
        self._file.write(data)

    def on_completed(self, message: str, *args) -> None:
        if message:
            print(f"completed: {message}", file=sys.stderr)

    def on_error(self, message: str, *args) -> None:
        self._error_message = message

    def on_close(self, *args) -> None:
        try:
            self._file.close()
        except OSError:
            pass

    @property
    def error_message(self) -> str | None:
        return self._error_message


def main() -> None:
    load_env(ENV_PATH)
    parser = argparse.ArgumentParser(description="Synthesize short text to audio with Aliyun ISI")
    parser.add_argument("text", help="Text to synthesize. Prefer <=300 UTF-8 chars for short TTS.")
    parser.add_argument("--out", required=True, help="Output audio file path, for example ./demo.wav")
    parser.add_argument("--voice", default="xiaoyun")
    parser.add_argument("--format", choices=["pcm", "wav", "mp3"], default="wav")
    parser.add_argument("--sample-rate", choices=[8000, 16000], type=int, default=16000)
    parser.add_argument("--volume", type=int, default=50)
    parser.add_argument("--speech-rate", type=int, default=0)
    parser.add_argument("--pitch-rate", type=int, default=0)
    parser.add_argument("--region", default=default_region())
    parser.add_argument("--enable-subtitle", action="store_true", help="Request subtitle timestamps in metainfo callbacks")
    args = parser.parse_args()

    if args.region not in WS_TTS_ENDPOINTS:
        raise SystemExit(f"Unsupported region: {args.region}")

    try:
        import nls  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "Missing official Aliyun NLS Python SDK. Run `python3 -m pip install -r requirements.txt` in this folder first."
        ) from exc

    token, _expire_time = create_token(args.region)
    output_path = Path(args.out).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sink = FileSpeechSynthesizer(output_path)

    synthesizer = nls.NlsSpeechSynthesizer(
        url=WS_TTS_ENDPOINTS[args.region],
        token=token,
        appkey=app_key(),
        on_metainfo=sink.on_metainfo,
        on_data=sink.on_data,
        on_completed=sink.on_completed,
        on_error=sink.on_error,
        on_close=sink.on_close,
        callback_args=["short-tts"],
    )

    result = synthesizer.start(
        args.text,
        voice=args.voice,
        aformat=args.format,
        sample_rate=args.sample_rate,
        volume=args.volume,
        speech_rate=args.speech_rate,
        pitch_rate=args.pitch_rate,
        ex={"enable_subtitle": args.enable_subtitle},
    )

    if sink.error_message:
        raise SystemExit(f"TTS failed: {sink.error_message}")

    print(json.dumps({"result": result, "output_file": str(output_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
