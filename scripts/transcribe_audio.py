#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
from aliyun_isi_common import ENV_PATH, FLASH_ENDPOINTS, append_usage_log, app_key, create_token, default_region, estimate_cost, load_env, probe_media_duration_seconds, write_json, write_text


def infer_format(audio_path: Path) -> str:
    suffix = audio_path.suffix.lower().lstrip(".")
    mapping = {
        "wav": "wav",
        "mp3": "mp3",
        "mp4": "mp4",
        "aac": "aac",
        "opus": "opus",
    }
    if suffix not in mapping:
        supported = ", ".join(sorted(mapping))
        raise SystemExit(
            f"Unsupported audio suffix '.{suffix}'. Supported for FlashRecognizer: {supported}"
        )
    return mapping[suffix]


def transcribe(
    audio_path: Path,
    sample_rate: int,
    region: str,
    first_channel_only: bool,
    enable_timestamps: bool,
) -> dict:
    if region not in FLASH_ENDPOINTS:
        raise SystemExit(f"Unsupported region: {region}")

    token, expire_time = create_token(region)
    audio_format = infer_format(audio_path)
    params = {
        "appkey": app_key(),
        "token": token,
        "format": audio_format,
        "sample_rate": sample_rate,
        "enable_inverse_text_normalization": "true",
        "enable_word_level_result": "false",
        "enable_timestamp_alignment": str(enable_timestamps).lower(),
        "first_channel_only": str(first_channel_only).lower(),
    }
    url = f"{FLASH_ENDPOINTS[region]}?{urlencode(params)}"
    with audio_path.open("rb") as f:
        response = requests.post(
            url,
            data=f,
            headers={"Content-Type": "application/octet-stream"},
            timeout=1800,
        )
    response.raise_for_status()
    payload = response.json()
    payload["_meta"] = {
        "token_expire_time": expire_time,
        "audio_path": str(audio_path),
        "region": region,
    }
    return payload


def extract_text(payload: dict) -> str:
    if isinstance(payload.get("flash_result"), dict):
        sentences = payload["flash_result"].get("sentences") or []
        texts = [item.get("text", "").strip() for item in sentences if item.get("text")]
        if texts:
            return "\n".join(texts)
    if "text" in payload and isinstance(payload["text"], str):
        return payload["text"].strip()
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main() -> None:
    load_env(ENV_PATH)

    parser = argparse.ArgumentParser(description="Transcribe a local audio file with Aliyun ISI")
    parser.add_argument("audio_file", help="Path to a local wav/mp3/mp4/aac/opus file")
    parser.add_argument("--sample-rate", type=int, default=16000, help="16000 for non-phone audio, 8000 for phone audio")
    parser.add_argument("--region", default=default_region())
    parser.add_argument("--keep-both-channels", action="store_true", help="Do not force first_channel_only=true")
    parser.add_argument("--timestamps", action="store_true", help="Enable timestamp alignment in the API response")
    parser.add_argument("--json-out", help="Optional output path for raw JSON result")
    parser.add_argument("--txt-out", help="Optional output path for plain text result")
    args = parser.parse_args()

    audio_path = Path(args.audio_file).expanduser().resolve()
    if not audio_path.exists():
        raise SystemExit(f"Audio file not found: {audio_path}")

    started_at = time.time()
    payload = transcribe(
        audio_path=audio_path,
        sample_rate=args.sample_rate,
        region=args.region,
        first_channel_only=not args.keep_both_channels,
        enable_timestamps=args.timestamps,
    )
    text = extract_text(payload)
    duration_seconds = probe_media_duration_seconds(audio_path)
    elapsed_seconds = round(time.time() - started_at, 2)
    payload["_meta"]["duration_seconds"] = duration_seconds
    payload["_meta"]["elapsed_seconds"] = elapsed_seconds
    payload["_meta"]["estimated_cost_cny"] = estimate_cost("isi_flashrecognizer", duration_seconds)

    if args.json_out:
        write_json(args.json_out, payload)
    if args.txt_out:
        write_text(args.txt_out, text + "\n")

    append_usage_log(
        {
            "engine": "isi_flashrecognizer",
            "source_type": "local_file",
            "source_path": str(audio_path),
            "duration_seconds": duration_seconds or "",
            "elapsed_seconds": elapsed_seconds,
            "estimated_cost_cny": payload["_meta"]["estimated_cost_cny"] or "",
            "status": payload.get("status") or "SUCCEEDED",
            "output_text_path": args.txt_out or "",
            "output_json_path": args.json_out or "",
            "oss_object_name": "",
        }
    )

    print(text)


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        print(detail, file=sys.stderr)
        raise
