#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time

import requests

from aliyun_isi_common import ASYNC_TTS_ENDPOINTS, app_key, create_token, default_region, download_binary, load_env, write_json


def submit_long_tts(
    text: str,
    voice: str,
    audio_format: str,
    sample_rate: int,
    region: str,
    speech_rate: int,
    pitch_rate: int,
    volume: int,
    enable_subtitle: bool,
) -> dict:
    token, expire_time = create_token(region)
    body = {
        "header": {
            "appkey": app_key(),
            "token": token,
        },
        "context": {
            "device_id": "codex-local",
        },
        "payload": {
            "enable_notify": False,
            "tts_request": {
                "voice": voice,
                "sample_rate": sample_rate,
                "format": audio_format,
                "text": text,
                "enable_subtitle": enable_subtitle,
                "speech_rate": speech_rate,
                "pitch_rate": pitch_rate,
                "volume": volume,
            },
        },
    }
    response = requests.post(
        ASYNC_TTS_ENDPOINTS[region],
        json=body,
        headers={"Content-Type": "application/json"},
        timeout=180,
    )
    response.raise_for_status()
    payload = response.json()
    payload["_meta"] = {"token_expire_time": expire_time, "region": region}
    return payload


def poll_long_tts(region: str, task_id: str, interval: int) -> dict:
    token, _expire_time = create_token(region)
    response = None
    while True:
        response = requests.get(
            ASYNC_TTS_ENDPOINTS[region],
            params={
                "appkey": app_key(),
                "task_id": task_id,
                "token": token,
            },
            timeout=180,
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data") or {}
        audio_address = data.get("audio_address")
        if audio_address:
            return payload
        time.sleep(interval)


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Synthesize long text to audio with Aliyun ISI async REST API")
    parser.add_argument("text", help="Text to synthesize. Suitable for long-form scripts and articles.")
    parser.add_argument("--voice", default="xiaoyun")
    parser.add_argument("--format", choices=["pcm", "wav", "mp3"], default="wav")
    parser.add_argument("--sample-rate", choices=[8000, 16000], type=int, default=16000)
    parser.add_argument("--speech-rate", type=int, default=0)
    parser.add_argument("--pitch-rate", type=int, default=0)
    parser.add_argument("--volume", type=int, default=50)
    parser.add_argument("--region", default=default_region())
    parser.add_argument("--enable-subtitle", action="store_true")
    parser.add_argument("--poll-interval", type=int, default=10)
    parser.add_argument("--download-to", help="Optional local path to save the generated audio file")
    parser.add_argument("--json-out", help="Optional output path for raw JSON result")
    args = parser.parse_args()

    if args.region not in ASYNC_TTS_ENDPOINTS:
        raise SystemExit(f"Unsupported region: {args.region}")

    submit_payload = submit_long_tts(
        text=args.text,
        voice=args.voice,
        audio_format=args.format,
        sample_rate=args.sample_rate,
        region=args.region,
        speech_rate=args.speech_rate,
        pitch_rate=args.pitch_rate,
        volume=args.volume,
        enable_subtitle=args.enable_subtitle,
    )
    task_id = (submit_payload.get("data") or {}).get("task_id")
    if not task_id:
        raise SystemExit(f"Failed to obtain task_id: {json.dumps(submit_payload, ensure_ascii=False)}")

    result_payload = poll_long_tts(args.region, task_id, args.poll_interval)
    write_json(args.json_out, result_payload)

    audio_address = (result_payload.get("data") or {}).get("audio_address")
    if args.download_to and audio_address:
        download_binary(audio_address, args.download_to)

    print(json.dumps(result_payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
