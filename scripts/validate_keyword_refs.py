#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用关键词引用验证器（源自 nihaixia 索引事故实战，沉淀入中医思维蒸馏器 V3.6）
验证 SKILL.md 中所有「文件 搜"关键词"」引用：关键词必须真实存在于目标文件。

使用：
    python3 scripts/validate_keyword_refs.py                     # 默认验证当前目录 SKILL.md
    python3 scripts/validate_keyword_refs.py --skill path/SKILL.md
    python3 scripts/validate_keyword_refs.py --skill path/SKILL.md --quiet   # 仅输出失效项
    python3 scripts/validate_keyword_refs.py --count-lines       # 按行计数模式（grep -c 语义，审计口径）
    python3 scripts/validate_keyword_refs.py --min-hits 5 --max-hits 400  # 命中量阈值检查（25-index-audit 关键词选择原则）

退出码：0 = 全部有效；1 = 存在失效引用（CI 可用）
"""
import argparse
import os
import re
import sys

def validate(skill_path: str, quiet: bool = False, count_lines: bool = False,
             min_hits: int = 0, max_hits: int = 0) -> int:
    base = os.path.dirname(os.path.abspath(skill_path))
    with open(skill_path, encoding="utf-8") as f:
        skill = f.read()
    lines = skill.split("\n")

    # 匹配「<文件> 搜"关键词"」格式（文件可为 SKILL.md / modules/*.md / references/*.md / cases/*.md）
    # 字符类含连字符与大写：references/20-original-text-digitalization.md 等文件名含 "-"
    pattern = re.compile(
        r'((?:SKILL|modules/[A-Za-z0-9_-]+|references/[A-Za-z0-9_/-]+|cases/[A-Za-z0-9_-]+)\.md)\s*搜["“]([^"”]+)["”]'
    )

    checked, skipped, problems, threshold_warns = 0, 0, [], []
    # 统计含「搜」但格式不匹配的行（防静默跳过）
    search_marker = re.compile(r'搜["“][^"”]+["”]')
    for i, line in enumerate(lines, 1):
        if search_marker.search(line) and not pattern.search(line):
            skipped += 1
            if not quiet:
                print(f"  [跳过·格式不匹配] 行{i}: {line.strip()[:80]}")
        for m in pattern.finditer(line):
            checked += 1
            fname, kw = m.group(1), m.group(2)
            if fname == "SKILL.md":
                content = skill
            else:
                fpath = os.path.join(base, fname)
                if not os.path.exists(fpath):
                    problems.append((i, fname, kw, "文件不存在"))
                    continue
                with open(fpath, encoding="utf-8") as f:
                    content = f.read()
            if kw not in content:
                problems.append((i, fname, kw, "关键词不存在"))
                continue
            # 命中量阈值检查（按行口径，与 25-index-audit.md 关键词选择原则一致）
            if min_hits or max_hits:
                hits = sum(1 for l in content.split("\n") if kw in l)
                if min_hits and hits < min_hits:
                    threshold_warns.append((i, fname, kw, hits, f"<{min_hits}行·不单独索引"))
                if max_hits and hits > max_hits:
                    threshold_warns.append((i, fname, kw, hits, f">{max_hits}行·噪音"))

    if not quiet:
        print(f"引用总数: {checked}, 失效: {len(problems)}, 跳过(格式不匹配): {skipped}"
              + (f", 阈值警告: {len(threshold_warns)}" if threshold_warns else ""))
    for ln, fname, kw, reason in problems:
        print(f"  [失效] 行{ln}: {fname} 搜\"{kw}\" -> {reason}")
    for ln, fname, kw, hits, reason in threshold_warns:
        print(f"  [阈值] 行{ln}: {fname} 搜\"{kw}\" 命中{hits}行 -> {reason}")
    return 1 if problems else 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="验证 SKILL.md 关键词引用有效性")
    ap.add_argument("--skill", default="SKILL.md", help="SKILL.md 路径（默认当前目录）")
    ap.add_argument("--quiet", action="store_true", help="仅输出失效项")
    ap.add_argument("--count-lines", action="store_true", help="按行计数模式（grep -c 语义，对齐审计口径）")
    ap.add_argument("--min-hits", type=int, default=0, help="最小命中行数阈值（低于报警，如 5）")
    ap.add_argument("--max-hits", type=int, default=0, help="最大命中行数阈值（高于报警，如 400）")
    args = ap.parse_args()
    sys.exit(validate(args.skill, args.quiet, args.count_lines, args.min_hits, args.max_hits))
