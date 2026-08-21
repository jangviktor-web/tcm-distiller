# 通用工具（源自黄元御skill V2.9实战，沉淀入中医思维蒸馏器）
# 使用：修改 SRC 路径与元数据为你的目标医师/原文；详情见 references/20-original-text-digitalization.md
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全量校验：索引中每个 Lxxxx 行号 + 标题 是否与源文件一致"""
import re

INDEX = "/sandbox/workspace/skills/黄元御中医辩证skill/modules/06_yishu_11zhong_INDEX.md"
SRC = "/sandbox/workspace/skills/黄元御中医辩证skill/modules/06_yishu_11zhong.md"

with open(SRC, encoding="utf-8") as f:
    src_lines = f.readlines()

with open(INDEX, encoding="utf-8") as f:
    idx = f.read()

# 1) 校验 `Lxxxx` 开头的篇目条目
pat = re.compile(r"- `L(\d+)` (.+)")
mismatch = []
checked = 0
for m in pat.finditer(idx):
    ln, title = int(m.group(1)), m.group(2).strip()
    checked += 1
    if ln < 1 or ln > len(src_lines):
        mismatch.append((ln, title, "<行号越界>"))
        continue
    actual = src_lines[ln - 1].strip()
    # 标题行应匹配：源文件行是 # 标题，且标题文本与索引一致（容忍☑■等符号差异）
    if not actual.startswith("#"):
        mismatch.append((ln, title, f"非标题行: {actual[:30]}"))
        continue
    # 从 # 后取标题文本
    actual_title = actual.lstrip("#").strip()
    if actual_title != title:
        mismatch.append((ln, title, f"标题不一致: {actual_title[:30]}"))

print(f"篇目条目总数: {checked}")
print(f"不匹配: {len(mismatch)}")
for ln, t, reason in mismatch[:40]:
    print(f"  L{ln} [{t}] -> {reason}")

# 2) 校验卷表行号
vol_pat = re.compile(r"\| ([^|]+) \| L(\d+) \|")
print("\n卷表行号校验（抽查前30）:")
vol_mismatch = []
for m in vol_pat.finditer(idx):
    vname, ln = m.group(1).strip(), int(m.group(2))
    if "主要篇目" in vname or "行号" in vname or "卷" not in vname:
        continue
    if ln < 1 or ln > len(src_lines):
        vol_mismatch.append((ln, vname, "<越界>"))
        continue
    actual = src_lines[ln - 1].strip()
    if not actual.startswith("#"):
        vol_mismatch.append((ln, vname, f"非标题行: {actual[:30]}"))
        continue
    actual_title = actual.lstrip("#").strip()
    if actual_title != vname:
        vol_mismatch.append((ln, vname, f"不一致: {actual_title[:40]}"))
print(f"卷条目不匹配: {len(vol_mismatch)}")
for ln, t, reason in vol_mismatch[:40]:
    print(f"  L{ln} [{t}] -> {reason}")
