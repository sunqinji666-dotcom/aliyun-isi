#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from aliyun_isi_common import FILETRANS_DOMAINS, append_usage_log, app_key, default_region, env, estimate_cost, load_env, write_json, write_text


STATUS_SUCCESS = "SUCCESS"
STATUS_SUCCESS_WITH_NO_VALID_FRAGMENT = "SUCCESS_WITH_NO_VALID_FRAGMENT"
STATUS_RUNNING = "RUNNING"
STATUS_QUEUEING = "QUEUEING"


def build_client(region: str) -> AcsClient:
    ak_id = env("ALIYUN_ACCESS_KEY_ID")
    ak_secret = env("ALIYUN_ACCESS_KEY_SECRET")
    return AcsClient(ak_id, ak_secret, region)


def submit_task(
    client: AcsClient,
    region: str,
    file_link: str,
    auto_split: bool,
    enable_words: bool,
) -> str:
    request = CommonRequest()
    request.set_domain(FILETRANS_DOMAINS[region])
    request.set_version("2018-08-17")
    request.set_product("nls-filetrans")
    request.set_action_name("SubmitTask")
    request.set_method("POST")
    task = {
        "appkey": app_key(),
        "file_link": file_link,
        "version": "4.0",
        "enable_words": enable_words,
    }
    if auto_split:
        task["auto_split"] = True
    request.add_body_params("Task", json.dumps(task, ensure_ascii=False))
    payload = json.loads(client.do_action_with_exception(request))
    status_text = payload.get("StatusText")
    if status_text != STATUS_SUCCESS:
        raise SystemExit(f"SubmitTask failed: {json.dumps(payload, ensure_ascii=False)}")
    return payload["TaskId"]


def poll_result(client: AcsClient, region: str, task_id: str, interval: int) -> dict:
    request = CommonRequest()
    request.set_domain(FILETRANS_DOMAINS[region])
    request.set_version("2018-08-17")
    request.set_product("nls-filetrans")
    request.set_action_name("GetTaskResult")
    request.set_method("GET")
    request.add_query_param("TaskId", task_id)

    while True:
        payload = json.loads(client.do_action_with_exception(request))
        status_text = payload.get("StatusText")
        if status_text in {STATUS_RUNNING, STATUS_QUEUEING}:
            time.sleep(interval)
            continue
        return payload


def extract_text(payload: dict) -> str:
    result = payload.get("Result")
    if isinstance(result, dict):
        sentences = result.get("Sentences") or result.get("sentences") or []
        texts = [item.get("Text", "").strip() or item.get("text", "").strip() for item in sentences]
        texts = [item for item in texts if item]
        if texts:
            return "\n".join(texts)
        if "Sentences" not in result and "transcripts" in result:
            transcripts = result.get("transcripts") or []
            texts = [item.get("text", "").strip() for item in transcripts if item.get("text")]
            if texts:
                return "\n".join(texts)
        return json.dumps(result, ensure_ascii=False, indent=2)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Transcribe a remote recording URL with Aliyun ISI async file transcription")
    parser.add_argument("file_url", help="Publicly reachable audio file URL, ideally OSS or a stable HTTPS link")
    parser.add_argument("--region", default=default_region())
    parser.add_argument("--poll-interval", type=int, default=10)
    parser.add_argument("--auto-split", action="store_true", help="Enable intelligent channel splitting when appropriate")
    parser.add_argument("--enable-words", action="store_true", help="Request word-level output in version 4.0")
    parser.add_argument("--json-out", help="Optional output path for raw JSON result")
    parser.add_argument("--txt-out", help="Optional output path for extracted text")
    args = parser.parse_args()

    if args.region not in FILETRANS_DOMAINS:
        raise SystemExit(f"Unsupported region: {args.region}")

    client = build_client(args.region)
    started_at = time.time()
    task_id = submit_task(client, args.region, args.file_url, args.auto_split, args.enable_words)
    payload = poll_result(client, args.region, task_id, args.poll_interval)
    text = extract_text(payload)
    duration_seconds = None
    if isinstance(payload.get("BizDuration"), (int, float)):
        duration_seconds = round(float(payload["BizDuration"]) / 1000.0, 3)
    elapsed_seconds = round(time.time() - started_at, 2)
    payload["_meta"] = {
        "duration_seconds": duration_seconds,
        "elapsed_seconds": elapsed_seconds,
        "estimated_cost_cny": estimate_cost("isi_recording_file", duration_seconds),
        "source_url": args.file_url,
    }

    write_json(args.json_out, payload)
    write_text(args.txt_out, text + "\n")
    append_usage_log(
        {
            "engine": "isi_recording_file",
            "source_type": "remote_url",
            "source_path": args.file_url,
            "duration_seconds": duration_seconds or "",
            "elapsed_seconds": elapsed_seconds,
            "estimated_cost_cny": payload["_meta"]["estimated_cost_cny"] or "",
            "status": payload.get("StatusText", ""),
            "output_text_path": args.txt_out or "",
            "output_json_path": args.json_out or "",
            "oss_object_name": "",
        }
    )

    print(text)


if __name__ == "__main__":
    main()
