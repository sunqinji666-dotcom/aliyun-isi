#!/usr/bin/env python3
"""
知识库文稿主题检索工具
用于快速找到与指定主题相关的文稿文件
"""

import os
import sys
import glob

# 知识库路径
BASE_DIR = "/path/to/transcripts"

TRANSCRIPT_DIRS = [
    os.path.join(BASE_DIR, "爱戏剧的柏拉图-视频转录/转录结果"),
    os.path.join(BASE_DIR, "恋爱脱单实战课：从心动到确定关系/转录结果"),
    os.path.join(BASE_DIR, "一门给年轻人的恋爱成长课/转录结果"),
]


def search_by_keywords(keywords: list[str]) -> list[tuple[str, str, float]]:
    """
    根据关键词搜索文稿
    返回: [(文件路径, 匹配内容摘要, 匹配度), ...]
    """
    results = []
    
    for dir_path in TRANSCRIPT_DIRS:
        if not os.path.exists(dir_path):
            continue
        
        txt_files = glob.glob(os.path.join(dir_path, "*.txt"))
        
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                match_count = 0
                matched_snippets = []
                
                for keyword in keywords:
                    if keyword in content:
                        match_count += 1
                        # 提取关键词前后 100 字作为上下文
                        idx = content.find(keyword)
                        while idx != -1:
                            start = max(0, idx - 100)
                            end = min(len(content), idx + 100)
                            snippet = content[start:end].replace('\n', '')
                            matched_snippets.append(f"...{snippet}...")
                            idx = content.find(keyword, idx + 1)
                
                if match_count > 0:
                    relevance = match_count / len(keywords)
                    results.append((txt_file, matched_snippets[:3], relevance))
                    
            except Exception as e:
                print(f"⚠️ 读取失败: {txt_file} - {e}", file=sys.stderr)
    
    # 按匹配度排序
    results.sort(key=lambda x: x[2], reverse=True)
    return results


def list_all_files() -> list[tuple[str, str]]:
    """列出所有文稿文件及其所属项目"""
    files = []
    for dir_path in TRANSCRIPT_DIRS:
        if not os.path.exists(dir_path):
            continue
        project_name = os.path.basename(os.path.dirname(dir_path))
        txt_files = glob.glob(os.path.join(dir_path, "*.txt"))
        for txt_file in sorted(txt_files):
            filename = os.path.basename(txt_file)
            files.append((filename, project_name))
    return files


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print(f"  {sys.argv[0]} search <关键词1> <关键词2> ...")
        print(f"  {sys.argv[0]} list")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "search":
        keywords = sys.argv[2:]
        print(f"🔍 搜索关键词: {', '.join(keywords)}")
        print("=" * 60)
        
        results = search_by_keywords(keywords)
        
        if not results:
            print("❌ 未找到相关内容")
            return
        
        print(f"✅ 找到 {len(results)} 篇相关文稿\n")
        
        for i, (file_path, snippets, relevance) in enumerate(results[:10], 1):
            filename = os.path.basename(file_path)
            project = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
            print(f"{i}. {filename}")
            print(f"   来源: {project}")
            print(f"   匹配度: {relevance:.0%}")
            if snippets:
                print(f"   摘要: {snippets[0][:80]}...")
            print()
    
    elif command == "list":
        files = list_all_files()
        print(f"📚 知识库文稿总计: {len(files)} 篇")
        print("=" * 60)
        
        current_project = None
        for filename, project in files:
            if project != current_project:
                print(f"\n📁 {project}")
                current_project = project
            print(f"  - {filename}")
    
    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
