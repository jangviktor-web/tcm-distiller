# 通用工具（源自黄元御skill V2.9实战，沉淀入中医思维蒸馏器）
# 使用：修改 SRC 路径与元数据为你的目标医师/原文；详情见 references/20-original-text-digitalization.md
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""综合清理：HTML div页码容器 + 页眉串混入 + 黄元淑讹字（保留表格）"""
import re

SRC = "/sandbox/workspace/skills/黄元御中医辩证skill/modules/06_yishu_11zhong.md"

with open(SRC, encoding="utf-8") as f:
    lines = f.readlines()

orig = len(lines)
stats = {}

# 1. 黄元淑 → 黄元御
cnt = 0
for i, l in enumerate(lines):
    if "黄元淑" in l:
        lines[i] = l.replace("黄元淑", "黄元御")
        cnt += l.count("黄元淑")
stats["黄元淑→黄元御"] = cnt

# 2. 删除页眉串（内经是解卷X，带/不带符号）
pat_header = re.compile(r'[☑■☐]?内经是解卷[一二三四五六七八九十]+')
cnt = 0
for i, l in enumerate(lines):
    if pat_header.search(l):
        new = pat_header.sub('', l)
        cnt += len(pat_header.findall(l))
        lines[i] = new
stats["页眉串删除"] = cnt

# 3. 去掉 div 标签（保留 table/tr/td）
div_pat = re.compile(r'<div[^>]*>|</div>')
cnt = 0
for i, l in enumerate(lines):
    if '<div' in l or '</div>' in l:
        new = div_pat.sub('', l)
        cnt += 1
        lines[i] = new
stats["div标签行"] = cnt

# 4. 删除纯页码/空内容行（div清理后残留）
del_cnt = 0
kept = []
for l in lines:
    s = l.strip()
    if re.match(r'^\d+\s*·?\s*$', s):      # 纯页码 "16 ·"
        del_cnt += 1
        continue
    if s in ('·', '· ', '·\u3000') or re.match(r'^[\s·]+$', s):
        del_cnt += 1
        continue
    if s == '':                              # 空行保留（占位）
        kept.append(l)
        continue
    kept.append(l)
stats["页码行删除"] = del_cnt
lines = kept

print(f"行数: {orig} → {len(lines)} (减少{orig-len(lines)})")
for k, v in stats.items():
    print(f"  {k}: {v}")

with open(SRC, "w", encoding="utf-8") as f:
    f.writelines(lines)

# 验证
with open(SRC, encoding="utf-8") as f:
    t = f.read()
print("\n验证:")
print(f"  残留黄元淑: {t.count('黄元淑')}")
print(f"  残留内经是解: {t.count('内经是解')}")
print(f"  残留div: {t.count('<div')}")
print(f"  保留table: {t.count('<table')}")
print(f"  保留tr: {t.count('<tr')}")
