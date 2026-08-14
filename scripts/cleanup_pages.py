# 通用工具（源自黄元御skill V2.9实战，沉淀入中医思维蒸馏器）
# 使用：修改 SRC 路径与元数据为你的目标医师/原文；详情见 references/20-original-text-digitalization.md
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理 OCR 页码页眉残留：独立行页眉 / 句中【N】 / 慧解变体"""
import re

SRC = "/sandbox/workspace/skills/黄元御中医辩证skill/modules/06_yishu_11zhong.md"
with open(SRC, encoding="utf-8") as f:
    lines = f.readlines()
orig = len(lines)

# 独立行页眉：含"医书"+第N页（可带【】前缀或残缺）
line_pat = re.compile(
    r'^[【\s]*[^。\n]{0,25}医书[^。\n]{0,20}第\d+页[】\s]*$'
)
# 句中【N】页码
num_pat = re.compile(r'【\d+】')
# 句中【...第N页...】
page_pat = re.compile(r'【[^】]*第\d+页[^】]*】')
# 慧解变体页眉（金匱慧解卷X = 金匮悬解卷X页眉OCR错）
hui_pat = re.compile(r'[☑■☐]?(金匱|金匮)慧解卷[一二三四五六七八九十]+')

stats = {"独立行页眉": 0, "句中【N】": 0, "句中【第N页】": 0, "慧解变体": 0}
kept = []
for l in lines:
    s = l.strip()
    # 1. 独立行页眉 → 删行
    if line_pat.match(s):
        stats["独立行页眉"] += 1
        continue
    # 2. 句中【N】
    if num_pat.search(l):
        n = len(num_pat.findall(l))
        stats["句中【N】"] += n
        l = num_pat.sub('', l)
    # 3. 句中【...第N页...】
    if page_pat.search(l):
        n = len(page_pat.findall(l))
        stats["句中【第N页】"] += n
        l = page_pat.sub('', l)
    # 4. 慧解变体
    if hui_pat.search(l):
        n = len(hui_pat.findall(l))
        stats["慧解变体"] += n
        l = hui_pat.sub('', l)
    kept.append(l)

print(f"行数: {orig} → {len(kept)}")
for k, v in stats.items():
    print(f"  {k}: {v}")

with open(SRC, "w", encoding="utf-8") as f:
    f.writelines(kept)

with open(SRC, encoding="utf-8") as f:
    t = f.read()
print(f"验证: 残留【N】{len(num_pat.findall(t))} | 残留独立页眉 {len(line_pat.findall(t))} | 慧解 {t.count('慧解')}")
