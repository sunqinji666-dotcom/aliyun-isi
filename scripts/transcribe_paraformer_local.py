#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time

from aliyun_isi_common import append_usage_log, delete_oss_object, estimate_cost, load_env, probe_media_duration_seconds, upload_local_file_to_oss, write_json, write_text
from transcribe_paraformer_url import fetch_result_text, poll_task, submit_task


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Upload a local file to OSS and transcribe it with Bailian Paraformer")
    parser.add_argument("local_file", help="Local audio path")
    parser.add_argument("--object-prefix", default="codex-upload")
    parser.add_argument("--poll-interval", type=int, default=2)
    parser.add_argument("--speaker-count", type=int, default=0, help="Number of speakers for diarization (0=off, 2-10=on)")
    parser.add_argument("--txt-out", help="Optional output path for plain text")
    parser.add_argument("--json-out", help="Optional output path for task JSON")
    parser.add_argument("--keep-oss", action="store_true", help="Keep the temporary OSS object after transcription")
    args = parser.parse_args()

    from aliyun_isi_common import env

    started_at = time.time()
    print("status=uploading_to_oss")
    object_name, signed_url = upload_local_file_to_oss(args.local_file, args.object_prefix)
    print(f"status=uploaded object_name={object_name}")
    print("status=submitting_paraformer_task")
    task_id = submit_task(signed_url, env("BAILIAN_API_KEY"), speaker_count=args.speaker_count)
    print(f"status=submitted task_id={task_id}")
    print("status=polling_paraformer_result")
    payload = poll_task(task_id, env("BAILIAN_API_KEY"), args.poll_interval)
    finished_at = time.time()
    payload["_meta"] = {"oss_object_name": object_name, "signed_url": signed_url}
    text = fetch_result_text(payload)
    payload["_meta"]["elapsed_seconds"] = round(finished_at - started_at, 2)
    duration_seconds = probe_media_duration_seconds(args.local_file)
    if duration_seconds is None and isinstance(payload.get("usage", {}).get("duration"), (int, float)):
        duration_seconds = round(float(payload["usage"]["duration"]), 3)
    payload["_meta"]["duration_seconds"] = duration_seconds
    payload["_meta"]["estimated_cost_cny"] = estimate_cost("bailian_paraformer", duration_seconds)

    deleted = False
    if not args.keep_oss:
        print("status=deleting_temporary_oss_object")
        deleted = delete_oss_object(object_name)
        print(f"status=oss_cleanup deleted={str(deleted).lower()}")
    else:
        print("status=oss_cleanup skipped=true")
    payload["_meta"]["oss_deleted_after_transcription"] = deleted
    payload["_meta"]["oss_kept"] = bool(args.keep_oss)

    write_json(args.json_out, payload)
    write_text(args.txt_out, text + "\n")
    append_usage_log(
        {
            "engine": "bailian_paraformer",
            "source_type": "local_file_via_oss",
            "source_path": args.local_file,
            "duration_seconds": duration_seconds or "",
            "elapsed_seconds": payload["_meta"]["elapsed_seconds"],
            "estimated_cost_cny": payload["_meta"]["estimated_cost_cny"] or "",
            "status": payload.get("output", {}).get("task_status", ""),
            "output_text_path": args.txt_out or "",
            "output_json_path": args.json_out or "",
            "oss_object_name": object_name,
        }
    )
    print(json.dumps({"oss_object_name": object_name, "elapsed_seconds": payload["_meta"]["elapsed_seconds"]}, ensure_ascii=False))
    print(text)


if __name__ == "__main__":
    main()
