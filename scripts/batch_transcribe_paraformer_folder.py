#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


SUPPORTED_SUFFIXES = {".wav", ".mp3", ".mp4", ".aac", ".opus", ".m4a"}


def iter_audio_files(folder: Path) -> list[Path]:
    return [
        path
        for path in sorted(folder.iterdir())
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch transcribe a folder of local audio files with Bailian Paraformer via automatic OSS upload"
    )
    parser.add_argument("folder", help="Folder containing audio files")
    parser.add_argument(
        "--out-dir",
        help="Output directory for txt/json files. Defaults to a sibling folder named 转写结果-百炼",
    )
    parser.add_argument("--json", action="store_true", help="Also save raw JSON result for each file")
    parser.add_argument("--object-prefix", default="codex-upload")
    parser.add_argument("--keep-oss", action="store_true", help="Keep uploaded temporary OSS objects after transcription")
    parser.add_argument("--force-rerun", action="store_true", help="Re-transcribe even if output files already exist")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.exists() or not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder}")

    files = iter_audio_files(folder)
    if not files:
        raise SystemExit(f"No supported audio files found in: {folder}")

    out_dir = (
        Path(args.out_dir).expanduser().resolve()
        if args.out_dir
        else folder / "转写结果-百炼"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    script_path = Path(__file__).resolve().parent / "transcribe_paraformer_local.py"
    failures: list[str] = []
    batch_started_at = time.time()

    for index, audio_file in enumerate(files, start=1):
        stem = audio_file.stem
        txt_out = out_dir / f"{stem}.txt"
        json_out = out_dir / f"{stem}.json"
        if not args.force_rerun:
            has_txt = txt_out.exists()
            has_json = (not args.json) or json_out.exists()
            if has_txt and has_json:
                print(f"[{index}/{len(files)}] 跳过已完成: {audio_file.name}")
                continue
        print(f"[{index}/{len(files)}] 转写中: {audio_file.name}")
        cmd = [
            sys.executable,
            str(script_path),
            str(audio_file),
            "--object-prefix",
            args.object_prefix,
            "--txt-out",
            str(txt_out),
        ]
        if args.keep_oss:
            cmd.append("--keep-oss")
        if args.json:
            cmd.extend(["--json-out", str(json_out)])

        result = subprocess.run(cmd, text=True)
        if result.returncode != 0:
            failures.append(audio_file.name)

    print()
    print(f"完成: {len(files) - len(failures)}/{len(files)}")
    print(f"输出目录: {out_dir}")
    print(f"总耗时秒数: {round(time.time() - batch_started_at, 2)}")
    if failures:
        print("失败文件:")
        for name in failures:
            print(f"- {name}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
