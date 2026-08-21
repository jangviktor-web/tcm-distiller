# 通用工具（源自黄元御skill V2.9实战，沉淀入中医思维蒸馏器）
# 使用：修改 SRC 路径与元数据为你的目标医师/原文；详情见 references/20-original-text-digitalization.md
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用对比：维基版 vs 电子版（素灵微蕴/长沙药解）
用法: python3 compare_wiki.py <素靈微蘊|長沙藥解> <起点行> <终点行>
"""
import re
import sys
from zhconv import convert

def norm(s):
    return convert(s, 'zh-cn').replace(' ', '').replace('\n', '')

book = sys.argv[1]          # 素靈微蘊 / 長沙藥解
start = int(sys.argv[2])    # 电子版起始行(1-based)
end = int(sys.argv[3])      # 电子版结束行

# ── 解析维基版 ──
with open(f'/tmp/wiki_{book}.txt', encoding='utf-8') as f:
    wlines = f.read().split('\n')
wiki_items = []  # [(名称, 正文)]
cur = None; buf = []
for i, l in enumerate(wlines):
    s = l.strip()
    if s == '编辑' and i > 0:
        if cur:
            wiki_items.append((cur, '\n'.join(buf)))
        for j in range(i-1, max(0, i-5), -1):
            if wlines[j].strip():
                cur = wlines[j].strip(); buf = []; break
    elif cur and s and not s.startswith(('From:','Snapshot','Subject','Date','MIME','Content-','boundary','------','姊妹','图册','数据项','目录','编辑')):
        if not re.match(r'^\d+(\.\d+)?$', s) and '維基文庫' not in s and '玉楸藥解' not in s[:12] and '長沙藥解' not in s[:12] and '素靈微蘊' not in s[:12] and '素灵微蕴' not in s[:12]:
            buf.append(s)
if cur: wiki_items.append((cur, '\n'.join(buf)))

# ── 解析电子版 ──
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
        if re.match(r'^\d+$|^\d+·$', t) or t in ('玉楸药解','长沙药解','素灵微蕴','卷一','卷二','卷三','卷四'):
            cur_name = None; continue
        cur_name = t; cur_ln = i + 1; cur_body = []
    elif cur_name and s:
        if re.match(r'^【.*第\d+页】$', s) or re.match(r'^[一二三四五六七八九十]+$', s) or '医书十一种' in s or re.match(r'^#{1,4} ', s):
            continue
        cur_body.append(s)
if cur_name: edrugs.append((cur_name, cur_ln, '\n'.join(cur_body)))

print(f'维基版条目: {len(wiki_items)}')
print(f'电子版条目: {len(edrugs)}')

# 精确匹配
def find_edrug(wn):
    wn_n = norm(wn)
    for en, eln, eb in edrugs:
        if norm(en) == wn_n:
            return en, eln, eb
    for en, eln, eb in edrugs:
        if wn_n in norm(en) or norm(en) in wn_n:
            return en, eln, eb
    return None

# 1. 维基有而电子版缺
print('\n=== 电子版缺失（维基有而电子版无） ===')
missing = 0
for wn, wt in wiki_items:
    if not find_edrug(wn):
        print(f'  ✗ {wn} (维基正文{len(norm(wt))}字)')
        missing += 1
if missing == 0:
    print('  无 ✓')

# 2. 正文差异（首句+长度）
print('\n=== 正文差异明细 ===')
def first_sentence(body):
    m = re.search(r'(味|问曰|曰)[^。\n]{0,40}。', body)
    return m.group(0) if m else body[:40]

diff_cnt = 0
for wn, wt in wiki_items:
    hit = find_edrug(wn)
    if not hit: continue
    en, eln, eb = hit
    w_txt = norm(wt); e_txt = norm(eb)
    if w_txt == e_txt: continue
    diff_cnt += 1
    i = 0
    while i < min(len(w_txt), len(e_txt)) and w_txt[i] == e_txt[i]:
        i += 1
    ctx_w = w_txt[max(0,i-15):i+20]
    ctx_e = e_txt[max(0,i-15):i+20]
    print(f'L{eln} {en}（维基{len(w_txt)}字/电子{len(e_txt)}字）:')
    print(f'  维基…{ctx_w}…')
    print(f'  电子…{ctx_e}…')
print(f'\n共 {diff_cnt} 条有差异')
