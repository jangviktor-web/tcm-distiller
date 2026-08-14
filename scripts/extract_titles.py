# 通用工具（源自黄元御skill V2.9实战，沉淀入中医思维蒸馏器）
# 使用：修改 SRC 路径与元数据为你的目标医师/原文；详情见 references/20-original-text-digitalization.md
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取黄元御医书十一种的标题结构 v2
修复：①支持四级标题（#### 难经各难/伤寒脉法章/素问缪刺论等正文篇目）
     ②###/#### 级"卷"标题（四圣心源卷二/玉楸药解卷二）纳入卷级
     ③过滤页眉（标题=书/卷名）与笔画索引（X划）等噪音
"""
import json
import re

SRC = "/sandbox/workspace/skills/黄元御中医辩证skill/modules/06_yishu_11zhong.md"

# 一级标题（书/卷级）
H1_RE = re.compile(r"^# (?!#)(.+)$")
# 二~四级标题
SEC_RE = re.compile(r"^#{2,4} (.+)$")

NOISE_PUNCT = re.compile(r"[。，；？！、]")
def is_noise(title: str, h1_titles: set) -> bool:
    t = title.strip()
    if len(t) > 30:
        return True
    if NOISE_PUNCT.search(t):
        return True
    if len(t) > 12 and re.search(r"[者也矣焉耳]$", t):
        return True
    if t in h1_titles:            # 页眉：标题==书/卷名
        return True
    if re.match(r"^[一二三四五六七八九十百]+划$", t):  # 书末笔画索引
        return True
    if re.match(r"^第?\d+页?$", t):  # 纯页码
        return True
    if t.startswith("·"):           # 页眉残片（原"书名卷X·内容"被OCR截断）
        return True
    if re.search(r"[A-Za-z]", t):   # OCR乱码（含拉丁字母）
        return True
    return False

# 第一遍：收集一级标题（书/卷名），用于页眉过滤
h1_titles = set()
with open(SRC, encoding="utf-8") as f:
    for line in f:
        m = H1_RE.match(line.rstrip("\n"))
        if m:
            h1_titles.add(m.group(1).strip())

books = []   # (行号, 标题) 书级（不含"卷"字）
vols = []    # (行号, 标题) 卷级（含"卷"字，含 ###/#### 层级的）
secs = []    # (行号, 标题) 篇目级

# 真实卷标白名单：源文件中以 ### 层级出现的真实卷标题（其余卷均为 # 一级）
VOL_SPECIAL = {"四圣心源卷二·六气解", "玉楸药解卷二·木部"}

with open(SRC, encoding="utf-8") as f:
    for lineno, line in enumerate(f, 1):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        m = H1_RE.match(line)
        if m:
            title = m.group(1).strip()
            if title == "校余偶识":      # 素问悬解卷末附录，作为篇目收录
                secs.append((lineno, title))
                continue
            if "卷" in title:
                vols.append((lineno, title))
            else:
                books.append((lineno, title))
            continue
        m = SEC_RE.match(line)
        if m:
            title = m.group(1).strip()
            # 卷级标题：含"卷"字且在白名单（如 "四圣心源卷二·六气解"）
            if "卷" in title and title in VOL_SPECIAL:
                vols.append((lineno, title))
                continue
            if is_noise(title, h1_titles):
                continue
            secs.append((lineno, title))

print(f"书级标题: {len(books)}")
print(f"卷级标题(含###/####层级): {len(vols)}")
print(f"篇目级标题(过滤后): {len(secs)}")

with open("/tmp/titles_v2.json", "w", encoding="utf-8") as f:
    json.dump({"books": books, "vols": vols, "secs": secs}, f, ensure_ascii=False, indent=1)

# 抽样验证
print("\n=== 卷级标题含层级异常的 ===")
h1_vols = set(t for ln, t in books if "卷" in t)  # 空，books已无卷
for ln, t in vols:
    if not t.startswith("·"):
        pass
# 打印所有卷级
for ln, t in vols:
    print(f"  L{ln}: {t}")
