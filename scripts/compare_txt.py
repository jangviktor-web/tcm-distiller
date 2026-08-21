# 通用工具（源自黄元御skill V2.9实战，沉淀入中医思维蒸馏器）
# 使用：修改 SRC 路径与元数据为你的目标医师/原文；详情见 references/20-original-text-digitalization.md
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用校对 v2：维基文库txt导出版 vs 电子版（逐篇正文对比）
用法: python3 compare_txt.py <上传txt> <起行> <止行> [书名]
"""
import re
import sys
from zhconv import convert

def norm(s):
    t = convert(s, 'zh-cn')
    t = re.sub(r'[\s\u3000]+', '', t)
    t = re.sub(r'[，。；：！？、〈〉《》「」『』（）\[\]【】"\'·•—-]', '', t)
    return t

src_txt = sys.argv[1]
start = int(sys.argv[2])
end = int(sys.argv[3])
bookname = sys.argv[4] if len(sys.argv) > 4 else ''

with open(src_txt, encoding='utf-8', errors='ignore') as f:
    raw = f.read()
wlines = [l.strip() for l in raw.split('\n')]
# 找正文起点
body_start = 0
for i, l in enumerate(wlines):
    if '作者：' in l or '作者:' in l:
        body_start = i + 1
wlines = wlines[body_start:]

def is_title_line(l):
    if not l or len(l) > 14:
        return False
    if re.search(r'[。，；？！、：]', l):
        return False
    if re.match(r'^(味|治|主|此|其|凡|諸|诸|若|蓋|盖|故|乃|方|一名|亦名|生|焙|炒|蒸|研|製|制|取|用)', l):
        return False
    if re.match(r'^(第\d+頁|第\d+页|姊妹|图册|数据项|版本|序|目錄|目录)', l):
        return False
    return True

candidates = [(i, l) for i, l in enumerate(wlines) if is_title_line(l)]

# 电子版条目
with open('/sandbox/workspace/skills/黄元御中医辩证skill/modules/06_yishu_11zhong.md', encoding='utf-8') as f:
    elines = f.readlines()
edrugs = []
cur_name = None; cur_ln = None; cur_body = []
for i in range(start-1, min(end, len(elines))):
    l = elines[i].rstrip('\n'); s = l.strip()
    m = re.match(r'^#{2,4} (.+)$', s)
    if m:
        if cur_name: edrugs.append((cur_name, cur_ln, '\n'.join(cur_body)))
        title = m.group(1).strip()
        t = re.sub(r'^[■☑☐]+\s*', '', title)
        if re.match(r'^\d+$|^\d+·$', t):
            cur_name = None; continue
        cur_name = t; cur_ln = i + 1; cur_body = []
    elif cur_name and s:
        if re.match(r'^【.*第\d+页】$', s) or re.match(r'^[一二三四五六七八九十]+$', s) or '医书十一种' in s or re.match(r'^#{1,4} ', s):
            continue
        cur_body.append(s)
if cur_name: edrugs.append((cur_name, cur_ln, '\n'.join(cur_body)))

# 过滤电子版噪音条目（标题含句读 = 正文误标）
edrugs = [(n, ln, b) for n, ln, b in edrugs if not re.search(r'[。，；？！、]', n) and len(n) <= 20]
print(f'电子版有效条目: {len(edrugs)}')

# 逐条定位 + 提取 txt 正文 + 对比
results = []
used_idx = set()
for en, eln, eb in edrugs:
    en_n = norm(en)
    if len(en_n) < 2: continue
    hit = None
    for ci, cl in candidates:
        if norm(cl) == en_n and ci not in used_idx:
            hit = ci; break
    if hit is None:
        for ci, cl in candidates:
            if ci not in used_idx and (en_n in norm(cl) or norm(cl) in en_n):
                hit = ci; break
    if hit is None:
        results.append(('MISS', en, eln, '', eb))
        continue
    used_idx.add(hit)
    # txt 正文：本标题到下一个未用标题之间
    nxt = None
    for ci, cl in candidates:
        if ci > hit and ci not in used_idx:
            nxt = ci; break
    wbody = '\n'.join(wlines[hit+1:nxt]) if nxt else '\n'.join(wlines[hit+1:])
    results.append(('OK', en, eln, wbody, eb))

# 输出
print(f'\n=== 未定位（txt中找不到标题） ===')
miss = [r for r in results if r[0] == 'MISS']
for _, en, eln, _, _ in miss:
    print(f'  ✗ {en} (L{eln})')
print(f'共 {len(miss)} 个')

print(f'\n=== 正文差异（首处差异点） ===')
diffs = 0
for kind, en, eln, wb, eb in results:
    if kind == 'MISS': continue
    w_txt = norm(wb); e_txt = norm(eb)
    if w_txt == e_txt: continue
    # 长度比
    ratio = abs(len(w_txt) - len(e_txt)) / max(len(w_txt), len(e_txt), 1)
    i = 0
    while i < min(len(w_txt), len(e_txt)) and w_txt[i] == e_txt[i]:
        i += 1
    ctx_w = w_txt[max(0,i-12):i+18]
    ctx_e = e_txt[max(0,i-12):i+18]
    flag = '🔴' if ratio > 0.25 else '🟡'
    print(f'{flag} L{eln} {en}（维基{len(w_txt)}/电子{len(e_txt)}字,差{int(abs(len(w_txt)-len(e_txt)))}）:')
    print(f'    维基…{ctx_w}…')
    print(f'    电子…{ctx_e}…')
    diffs += 1
print(f'\n共 {diffs} 条差异')
