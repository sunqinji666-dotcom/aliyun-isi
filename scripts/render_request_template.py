#!/usr/bin/env python3
"""
Render a reusable implementation brief for Aliyun ISI tasks.

This script is intentionally simple so other AI tools or humans can run it to
produce a concrete handoff before generating code.
"""

from __future__ import annotations

import argparse
from textwrap import dedent


def main() -> None:
    parser = argparse.ArgumentParser(description="Render an Aliyun ISI task brief")
    parser.add_argument(
        "--capability",
        default="tts",
        help="One of: tts, long-tts, sentence-asr, realtime-asr, file-asr",
    )
    parser.add_argument(
        "--runtime",
        default="node",
        help="Target runtime, for example: node, python, java",
    )
    parser.add_argument(
        "--delivery",
        default="backend-api",
        help="Target delivery shape, for example: backend-api, web-client, batch-job",
    )
    args = parser.parse_args()

    print(
        dedent(
            f"""
            # Aliyun ISI Implementation Brief

            Capability: {args.capability}
            Runtime: {args.runtime}
            Delivery: {args.delivery}

            Required configuration:
            - ALIYUN_ACCESS_KEY_ID
            - ALIYUN_ACCESS_KEY_SECRET
            - ALIYUN_NLS_APP_KEY

            Default architecture:
            - Backend owns credentials
            - Client receives only short-lived auth or calls the backend

            Deliverables:
            - .env.example
            - minimal runnable sample
            - verification steps
            - common error handling

            Checklist:
            1. Activate the ISI service in Alibaba Cloud
            2. Create/select the target project and confirm AppKey
            3. Match the service type to the product requirement
            4. Verify token lifecycle and audio/text limits
            5. Keep secrets out of frontend code
            """
        ).strip()
    )


if __name__ == "__main__":
    main()
