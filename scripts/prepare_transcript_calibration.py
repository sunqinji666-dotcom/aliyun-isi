#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", "", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = text.replace(",,", "，").replace("。。", "。")
    text = text.replace("？。", "？").replace("！。", "！")
    chunks = re.split(r"(?<=[。！？])", text)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    paragraphs: list[str] = []
    buffer: list[str] = []
    for chunk in chunks:
        buffer.append(chunk)
        if len(buffer) >= 3:
            paragraphs.append("".join(buffer))
            buffer = []
    if buffer:
        paragraphs.append("".join(buffer))
    return "\n\n".join(paragraphs).strip()


def build_prompt(identity: str, raw_text: str, rough_text: str, final_path: Path) -> str:
    return f"""# Transcript Calibration Prompt

请把这份语音转写稿，按“{identity}”的工作身份进行校准，输出成可直接阅读、可继续整理脚本或字幕的最终文稿。

要求：
1. 修正常见语音识别错误，但不要过度改写原意。
2. 保留口语风格和创作者表达习惯。
3. 重点校准 AI 视频创作、摄影、剪辑、导演、分镜、提示词、工作流相关术语。
4. 若专有名词不确定，不要瞎编，用 `【待确认】` 标出来。
5. 输出三部分：
   - 粗转写稿
   - 校准终稿
   - 术语待确认

建议最终文件写入：
`{final_path}`

## 原始转写

{raw_text}

## 预清洗版本

{rough_text}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a transcript calibration package for the current AI model")
    parser.add_argument("transcript_file", help="Raw transcript txt file")
    parser.add_argument(
        "--identity",
        default="摄影、剪辑、导演、AI 视频创作者",
        help="Working identity used to calibrate tone and terminology",
    )
    parser.add_argument("--rough-out", help="Optional path for cleaned rough draft")
    parser.add_argument("--final-out", help="Optional target path for final calibrated manuscript")
    parser.add_argument("--prompt-out", help="Optional path for calibration prompt bundle")
    args = parser.parse_args()

    transcript_path = Path(args.transcript_file).expanduser().resolve()
    if not transcript_path.exists():
        raise SystemExit(f"Transcript file not found: {transcript_path}")

    raw_text = transcript_path.read_text(encoding="utf-8").strip()
    rough_text = normalize_text(raw_text)

    rough_path = Path(args.rough_out).expanduser().resolve() if args.rough_out else transcript_path.with_suffix(".rough.md")
    final_path = Path(args.final_out).expanduser().resolve() if args.final_out else transcript_path.with_suffix(".final.md")
    prompt_path = Path(args.prompt_out).expanduser().resolve() if args.prompt_out else transcript_path.with_suffix(".calibration-prompt.md")

    rough_path.write_text(f"# 粗转写稿\n\n{rough_text}\n", encoding="utf-8")
    prompt_text = build_prompt(args.identity, raw_text, rough_text, final_path)
    prompt_path.write_text(prompt_text, encoding="utf-8")

    print(f"rough_out={rough_path}")
    print(f"prompt_out={prompt_path}")
    print(f"final_out={final_path}")


if __name__ == "__main__":
    main()
