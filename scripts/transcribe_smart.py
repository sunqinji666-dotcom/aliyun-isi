#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
ENV_PATH = ROOT / ".env"


def load_env(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() not in os.environ:
            os.environ[key.strip()] = value.strip()


def ask(prompt: str, default: str) -> str:
    value = input(f"{prompt} [{default}]: ").strip()
    return value or default


def run(cmd: list[str]) -> int:
    print("Running:")
    print(" ".join(cmd))
    return subprocess.run(cmd).returncode


def build_local_cmd(audio_path: str, sample_rate: int, txt_out: str | None, json_out: str | None) -> list[str]:
    cmd = [sys.executable, str(SCRIPTS / "transcribe_audio.py"), audio_path, "--sample-rate", str(sample_rate)]
    if txt_out:
        cmd.extend(["--txt-out", txt_out])
    if json_out:
        cmd.extend(["--json-out", json_out])
    return cmd


def build_paraformer_cmd(file_url: str, txt_out: str | None, json_out: str | None) -> list[str]:
    cmd = [sys.executable, str(SCRIPTS / "transcribe_paraformer_url.py"), file_url]
    if txt_out:
        cmd.extend(["--txt-out", txt_out])
    if json_out:
        cmd.extend(["--json-out", json_out])
    return cmd


def build_paraformer_local_cmd(audio_path: str, txt_out: str | None, json_out: str | None) -> list[str]:
    cmd = [sys.executable, str(SCRIPTS / "transcribe_paraformer_local.py"), audio_path]
    if txt_out:
        cmd.extend(["--txt-out", txt_out])
    if json_out:
        cmd.extend(["--json-out", json_out])
    return cmd


def build_paraformer_folder_cmd(folder_path: str, json_out: bool) -> list[str]:
    cmd = [sys.executable, str(SCRIPTS / "batch_transcribe_paraformer_folder.py"), folder_path]
    if json_out:
        cmd.append("--json")
    return cmd


def build_isi_url_cmd(file_url: str, txt_out: str | None, json_out: str | None) -> list[str]:
    cmd = [sys.executable, str(SCRIPTS / "transcribe_recording_url.py"), file_url]
    if txt_out:
        cmd.extend(["--txt-out", txt_out])
    if json_out:
        cmd.extend(["--json-out", json_out])
    return cmd


def main() -> None:
    load_env(ENV_PATH)
    parser = argparse.ArgumentParser(description="Smart transcription router for editor workflows")
    parser.add_argument("--mode", choices=["interactive", "recommend", "run"], default="interactive")
    parser.add_argument("--source", choices=["local", "url"])
    parser.add_argument("--priority", choices=["fastest", "cheapest", "least-setup"])
    parser.add_argument("--audio")
    parser.add_argument("--folder")
    parser.add_argument("--file-url")
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--txt-out")
    parser.add_argument("--json-out")
    args = parser.parse_args()

    if args.folder:
        recommendation = "Use Bailian Paraformer batch transcription with automatic OSS upload"
        cmd = build_paraformer_folder_cmd(args.folder, bool(args.json_out))
        print(recommendation)
        if args.mode == "run":
            raise SystemExit(run(cmd))
        print("Suggested command:")
        print(" ".join(cmd))
        return

    source = args.source or ask("Audio source: local or url", "local")
    priority = args.priority or ask("Priority: fastest, cheapest, or least-setup", "least-setup")

    if source == "local":
        audio = args.audio or ask("Local audio path", "")
        if priority in {"fastest", "least-setup"}:
            recommendation = "Use ISI FlashRecognizer via transcribe_audio.py"
            cmd = build_local_cmd(audio, args.sample_rate, args.txt_out, args.json_out)
        else:
            recommendation = "Use Bailian Paraformer via automatic OSS upload"
            cmd = build_paraformer_local_cmd(audio, args.txt_out, args.json_out)
    else:
        file_url = args.file_url or ask("OSS/public file URL", "")
        if priority == "cheapest":
            recommendation = "Use Bailian Paraformer"
            cmd = build_paraformer_cmd(file_url, args.txt_out, args.json_out)
        elif priority == "fastest":
            recommendation = "Use ISI recording-file recognition"
            cmd = build_isi_url_cmd(file_url, args.txt_out, args.json_out)
        else:
            recommendation = "Use Bailian Paraformer if cost matters, or ISI recording-file recognition if staying in ISI"
            cmd = build_paraformer_cmd(file_url, args.txt_out, args.json_out)

    print(recommendation)
    if args.mode == "run" and cmd:
        raise SystemExit(run(cmd))
    if cmd:
        print("Suggested command:")
        print(" ".join(cmd))


if __name__ == "__main__":
    main()
