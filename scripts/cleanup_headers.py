# 通用工具（源自黄元御skill V2.9实战，沉淀入中医思维蒸馏器）
# 使用：修改 SRC 路径与元数据为你的目标医师/原文；详情见 references/20-original-text-digitalization.md
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理页眉混入正文（书名卷号 264处 + #####垃圾 140处）"""
import re

SRC = "/sandbox/workspace/skills/黄元御中医辩证skill/modules/06_yishu_11zhong.md"

with open(SRC, encoding="utf-8") as f:
    lines = f.readlines()
orig = len(lines)

# 书名页眉模式（带/不带符号）
book_pat = re.compile(
    r'[☑■☐]?(内经是解|灵枢是解|伤寒说意|四圣心源|金匮悬解|素问悬解|难经悬解|'
    r'长沙药解|玉楸药解|四圣悬板|難經懸解|傷寒懸解|金匱懸解|四聖懸樞|'
    r'傷寒說意|四聖心源|素問懸解|靈樞懸解|長沙藥解|玉楸藥解)卷[一二三四五六七八九十]+'
)

# ##### 页眉行（如 "##### 难经悬解" / "##### 难经态解"）
hash_pat = re.compile(r'^#{2,5}\s*(内经是解|灵枢是解|难经悬解|难经态解|素问悬解|伤寒悬解|金匮悬解|伤寒说意|四圣心源|四圣悬板|长沙药解|玉楸药解|難經懸解|傷寒懸解|金匱懸解|傷寒說意|四聖心源|素問懸解|靈樞懸解|長沙藥解|玉楸藥解)\s*$')

# 纯 ### 页眉（书名）
pure_pat = re.compile(r'^#{2,5}\s*(内经是解|灵枢是解|难经悬解|素问悬解|伤寒悬解|金匮悬解|伤寒说意|四圣心源|四圣悬板|长沙药解|玉楸药解)\s*$')

stats = {"书名页眉串": 0, "#####页眉行": 0, "删行": 0}
kept = []
for l in lines:
    s = l.strip()
    # 1. ##### 页眉行 → 删行
    if hash_pat.match(s) or pure_pat.match(s):
        stats["#####页眉行"] += 1
        stats["删行"] += 1
        continue
    # 2. 书名卷号页眉串（句中/行中删除）
    if book_pat.search(l):
        new = book_pat.sub('', l)
        stats["书名页眉串"] += book_pat.findall(l).__len__()
        l = new
        if l.strip() == '':
            stats["删行"] += 1
            continue
    kept.append(l)

print(f"行数: {orig} → {len(kept)}")
for k, v in stats.items():
    print(f"  {k}: {v}")

with open(SRC, "w", encoding="utf-8") as f:
    f.writelines(kept)

# 验证
with open(SRC, encoding="utf-8") as f:
    t = f.read()
left = 0
for pat in ['灵枢是解卷','伤寒说意卷','四圣心源卷','金匮悬解卷','素问悬解卷','难经悬解卷','长沙药解卷','玉楸药解卷','四圣悬板卷','内经是解卷']:
    c = t.count(pat)
    left += c
    if c: print(f'  残留 {pat}: {c}')
print(f'书名页眉总残留: {left}')
print(f'#####残留: {t.count("#####")}')
