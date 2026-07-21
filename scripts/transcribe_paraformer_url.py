#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time

import requests

from aliyun_isi_common import append_usage_log, env, estimate_cost, load_env, write_json, write_text


def submit_task(file_url: str, api_key: str, speaker_count: int = 0) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }
    params = {"language_hints": ["zh", "en"]}
    if speaker_count and speaker_count > 0:
        params["speaker_count"] = speaker_count
    payload = {
        "model": "paraformer-v2",
        "input": {"file_urls": [file_url]},
        "parameters": params,
    }
    response = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription",
        headers=headers,
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["output"]["task_id"]


def poll_task(task_id: str, api_key: str, poll_interval: int) -> dict:
    headers = {"Authorization": f"Bearer {api_key}"}
    while True:
        response = requests.get(
            f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
            headers=headers,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        status = data.get("output", {}).get("task_status")
        if status in {"SUCCEEDED", "FAILED", "CANCELED"}:
            return data
        time.sleep(poll_interval)


def fetch_result_text(task_payload: dict) -> str:
    results = task_payload.get("output", {}).get("results") or []
    if not results:
        return json.dumps(task_payload, ensure_ascii=False, indent=2)
    transcription_url = results[0].get("transcription_url")
    if not transcription_url:
        return json.dumps(task_payload, ensure_ascii=False, indent=2)
    response = requests.get(transcription_url, timeout=120)
    response.raise_for_status()
    data = response.json()
    
    # Check if speaker diarization is enabled
    sentences = data.get("transcripts", [{}])[0].get("sentences", [])
    if sentences and any("speaker_id" in s for s in sentences):
        # Format with speaker labels
        lines = []
        current_speaker = None
        current_text = ""
        for s in sentences:
            speaker = s.get("speaker_id", "Unknown")
            text = s.get("text", "").strip()
            if speaker != current_speaker:
                if current_text:
                    lines.append(current_text)
                current_speaker = speaker
                current_text = f"[说话人{speaker}] {text}"
            else:
                current_text += text
        if current_text:
            lines.append(current_text)
        return "\n\n".join(lines)
    
    # Fallback: plain text
    transcripts = data.get("transcripts") or []
    texts = [item.get("text", "").strip() for item in transcripts if item.get("text")]
    if texts:
        return "\n".join(texts)
    return json.dumps(data, ensure_ascii=False, indent=2)


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Transcribe an OSS/public URL with Bailian Paraformer")
    parser.add_argument("file_url", help="Public or signed OSS URL for the audio file")
    parser.add_argument("--poll-interval", type=int, default=2)
    parser.add_argument("--speaker-count", type=int, default=0, help="Number of speakers for diarization (0=off, 2-10=on)")
    parser.add_argument("--txt-out", help="Optional output path for plain text")
    parser.add_argument("--json-out", help="Optional output path for task JSON")
    args = parser.parse_args()

    api_key = env("BAILIAN_API_KEY")
    started_at = time.time()
    task_id = submit_task(args.file_url, api_key, speaker_count=args.speaker_count)
    payload = poll_task(task_id, api_key, args.poll_interval)
    text = fetch_result_text(payload)
    duration_seconds = None
    if isinstance(payload.get("usage", {}).get("duration"), (int, float)):
        duration_seconds = round(float(payload["usage"]["duration"]), 3)
    elapsed_seconds = round(time.time() - started_at, 2)
    payload["_meta"] = {
        "duration_seconds": duration_seconds,
        "elapsed_seconds": elapsed_seconds,
        "estimated_cost_cny": estimate_cost("bailian_paraformer", duration_seconds),
        "source_url": args.file_url,
    }

    write_json(args.json_out, payload)
    write_text(args.txt_out, text + "\n")
    append_usage_log(
        {
            "engine": "bailian_paraformer",
            "source_type": "remote_url",
            "source_path": args.file_url,
            "duration_seconds": duration_seconds or "",
            "elapsed_seconds": elapsed_seconds,
            "estimated_cost_cny": payload["_meta"]["estimated_cost_cny"] or "",
            "status": payload.get("output", {}).get("task_status", ""),
            "output_text_path": args.txt_out or "",
            "output_json_path": args.json_out or "",
            "oss_object_name": "",
        }
    )
    print(text)


if __name__ == "__main__":
    main()
