#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import posixpath
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
LOGS_DIR = ROOT / "logs"
USAGE_CSV = LOGS_DIR / "usage_history.csv"
USAGE_JSONL = LOGS_DIR / "usage_history.jsonl"

FLASH_ENDPOINTS = {
    "cn-shanghai": "https://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/FlashRecognizer",
    "cn-beijing": "https://nls-gateway-cn-beijing.aliyuncs.com/stream/v1/FlashRecognizer",
    "cn-shenzhen": "https://nls-gateway-cn-shenzhen.aliyuncs.com/stream/v1/FlashRecognizer",
}

ASYNC_TTS_ENDPOINTS = {
    "cn-shanghai": "https://nls-gateway-cn-shanghai.aliyuncs.com/rest/v1/tts/async",
}

FILETRANS_DOMAINS = {
    "cn-shanghai": "filetrans.cn-shanghai.aliyuncs.com",
    "cn-beijing": "filetrans.cn-beijing.aliyuncs.com",
    "cn-shenzhen": "filetrans.cn-shenzhen.aliyuncs.com",
}

WS_TTS_ENDPOINTS = {
    "cn-shanghai": "wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1",
    "cn-beijing": "wss://nls-gateway-cn-beijing.aliyuncs.com/ws/v1",
    "cn-shenzhen": "wss://nls-gateway-cn-shenzhen.aliyuncs.com/ws/v1",
}

RATE_PER_HOUR = {
    "isi_flashrecognizer": 3.30,
    "isi_recording_file": 2.50,
    "isi_idle_file": 1.00,
    "bailian_paraformer": 0.288,
}


def load_env(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def env(name: str, fallback: str | None = None) -> str:
    value = os.getenv(name, fallback)
    if not value:
        raise SystemExit(f"Missing required config: {name}")
    return value


def default_region() -> str:
    return os.getenv("ALIYUN_REGION", "cn-shanghai")


def create_token(region: str | None = None) -> tuple[str, int]:
    region = region or default_region()
    ak_id = os.getenv("ALIYUN_AK_ID") or env("ALIYUN_ACCESS_KEY_ID")
    ak_secret = os.getenv("ALIYUN_AK_SECRET") or env("ALIYUN_ACCESS_KEY_SECRET")
    client = AcsClient(ak_id, ak_secret, region)
    request = CommonRequest()
    request.set_method("POST")
    request.set_domain("nls-meta.cn-shanghai.aliyuncs.com")
    request.set_version("2019-02-28")
    request.set_action_name("CreateToken")
    response = client.do_action_with_exception(request)
    payload = json.loads(response)
    token = payload["Token"]["Id"]
    expire_time = payload["Token"]["ExpireTime"]
    return token, expire_time


def app_key() -> str:
    return os.getenv("NLS_APP_KEY") or env("ALIYUN_NLS_APP_KEY")


def write_text(path: str | None, text: str) -> None:
    if not path:
        return
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def write_json(path: str | None, payload: Any) -> None:
    if not path:
        return
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def download_binary(url: str, path: str) -> None:
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=1800) as response:
        response.raise_for_status()
        with target.open("wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)


def oss_bucket():
    try:
        import oss2  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "Missing oss2. Run `python3 -m pip install -r requirements.txt` in this folder first."
        ) from exc

    endpoint = env("ALIYUN_OSS_ENDPOINT")
    bucket_name = env("ALIYUN_OSS_BUCKET")
    auth = oss2.Auth(env("ALIYUN_ACCESS_KEY_ID"), env("ALIYUN_ACCESS_KEY_SECRET"))
    return oss2.Bucket(auth, endpoint, bucket_name)


def upload_local_file_to_oss(local_path: str, object_prefix: str = "codex-upload") -> tuple[str, str]:
    source = Path(local_path).expanduser().resolve()
    if not source.exists():
        raise SystemExit(f"Local file not found: {source}")
    bucket = oss_bucket()
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    safe_name = source.name.replace(" ", "_")
    object_name = posixpath.join(object_prefix, f"{timestamp}-{safe_name}")
    result = bucket.put_object_from_file(object_name, str(source))
    if result.status != 200:
        raise SystemExit(f"OSS upload failed with status {result.status}")
    signed_url = bucket.sign_url("GET", object_name, 3600)
    return object_name, signed_url


def delete_oss_object(object_name: str) -> bool:
    bucket = oss_bucket()
    result = bucket.delete_object(object_name)
    return getattr(result, "status", None) == 204


def estimate_cost(engine: str, duration_seconds: float | None) -> float | None:
    if duration_seconds is None:
        return None
    rate = RATE_PER_HOUR.get(engine)
    if rate is None:
        return None
    return round((duration_seconds / 3600.0) * rate, 4)


def append_usage_log(record: dict[str, Any]) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    normalized = {"logged_at": datetime.now().isoformat(timespec="seconds"), **record}
    header = [
        "logged_at",
        "engine",
        "source_type",
        "source_path",
        "duration_seconds",
        "elapsed_seconds",
        "estimated_cost_cny",
        "status",
        "output_text_path",
        "output_json_path",
        "oss_object_name",
    ]
    if not USAGE_CSV.exists():
        USAGE_CSV.write_text(",".join(header) + "\n", encoding="utf-8")
    row = []
    for key in header:
        text = str(normalized.get(key, ""))
        text = text.replace('"', '""')
        if "," in text or '"' in text or "\n" in text:
            text = f'"{text}"'
        row.append(text)
    with USAGE_CSV.open("a", encoding="utf-8") as f:
        f.write(",".join(row) + "\n")
    with USAGE_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(normalized, ensure_ascii=False) + "\n")


def probe_media_duration_seconds(path: str | Path) -> float | None:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    target = str(Path(path).expanduser())
    import subprocess

    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            target,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    try:
        return round(float(result.stdout.strip()), 3)
    except ValueError:
        return None
