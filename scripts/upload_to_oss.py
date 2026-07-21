#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from aliyun_isi_common import load_env, upload_local_file_to_oss


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Upload a local file to Aliyun OSS and print a signed URL")
    parser.add_argument("local_file", help="Local file path")
    parser.add_argument("--object-prefix", default="codex-upload")
    args = parser.parse_args()

    object_name, signed_url = upload_local_file_to_oss(args.local_file, args.object_prefix)
    print(json.dumps({"object_name": object_name, "signed_url": signed_url}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
