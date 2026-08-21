# 通用工具（源自黄元御skill V2.9实战，沉淀入中医思维蒸馏器）
# 使用：修改 SRC 路径与元数据为你的目标医师/原文；详情见 references/20-original-text-digitalization.md
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 titles_v2.json 生成《黄元御医书十一种》全文索引 markdown v2
v2 修复：四圣心源卷二/玉楸药解卷二纳入卷级；四级标题篇目收录；卷名正名；勘误注扩充
"""
import json

with open("/tmp/titles_v2.json", encoding="utf-8") as f:
    data = json.load(f)

books_raw = data["books"]   # (行号, 书名) 一级标题不含卷
vols_raw = data["vols"]     # (行号, 卷名) 含卷（已含两个###特例）
secs = data["secs"]         # (行号, 标题)

TOTAL_LINES = 38266
BOOK_DISPLAY = {"灵素微蕴": "素灵微蕴", "四圣悬板": "四圣悬枢", "玉椒药解": "玉楸药解"}
VOL_DISPLAY = {"玉椒药解卷六·鳞介鱼虫部": "玉楸药解卷六·鳞介鱼虫部",
               "玉椒药解卷七·人部": "玉楸药解卷七·人部",
               "金贵悬解卷一": "金匮悬解卷一"}

# 书级列表：过滤校余偶识（并入素问悬解）
book_list = [(ln, t) for ln, t in books_raw if t != "校余偶识"]

# 书的结束行
book_bounds = []
for i, (ln, name) in enumerate(book_list):
    end = book_list[i + 1][0] - 1 if i + 1 < len(book_list) else TOTAL_LINES
    book_bounds.append((ln, name, end))

# 卷归属书（按行号范围）+ 卷名正名
book_of_vol = {}
for vln, vname in vols_raw:
    owner = None
    for bln, bname, bend in book_bounds:
        if bln <= vln <= bend:
            owner = bname
            break
    if owner is None:
        continue
    vname = VOL_DISPLAY.get(vname, vname)
    book_of_vol.setdefault(owner, []).append((vln, vname))

# 卷内去重：同名卷只保留行号最小的（防页眉残留）
for bname in book_of_vol:
    seen = {}
    for vln, vname in book_of_vol[bname]:
        if vname not in seen:
            seen[vname] = vln
    book_of_vol[bname] = [(vln, vname) for vname, vln in seen.items()]

# 卷边界
vol_bounds = {}
for bname, vlist in book_of_vol.items():
    bln = next(b for b, n, e in book_bounds if n == bname)
    bend = next(e for b, n, e in book_bounds if n == bname)
    vlist_sorted = sorted(vlist)
    for i, (vln, vname) in enumerate(vlist_sorted):
        vend = vlist_sorted[i + 1][0] - 1 if i + 1 < len(vlist_sorted) else bend
        vol_bounds[vname] = (vln, vend)

def locate_owner(ln):
    for bln, bname, bend in book_bounds:
        if bln <= ln <= bend:
            vname = None
            for vln, vn in book_of_vol.get(bname, []):
                vs, ve = vol_bounds[vn]
                if vs <= ln <= ve:
                    vname = vn
                    break
            return bname, vname
    return None, None

# 篇目归属
secs_by_book = {}
for sln, stitle in secs:
    bname, vname = locate_owner(sln)
    if bname is None:
        continue
    secs_by_book.setdefault(bname, []).append((sln, stitle, vname))

# 篇目去重：同一书内同标题只保留行号最小的（目录复述剔除，正文在前）
for bname in secs_by_book:
    seen = {}
    for sln, stitle, vname in secs_by_book[bname]:
        key = stitle
        if key not in seen:
            seen[key] = (sln, stitle, vname)
    secs_by_book[bname] = sorted(seen.values())

lines = []
A = lines.append

A("# 《黄元御医书十一种》全文检索索引")
A("")
A("> **源文件**：`modules/06_yishu_11zhong.md`（共 38266 行 / 约 145 万字 / 3.5MB，黄元御医书十一种全集合订本）")
A("> **用途**：AI 检索路由表。当用户问及黄元御任何著作、篇目、病症、方剂、药物时，**先在本索引中定位行号**，再打开源文件读取原文。")
A("")
A("## 使用说明（AI 检索三步法）")
A("")
A("1. **定位**：用 match 在本索引搜索关键词（书名 / 篇名 / 病症 / 方名 / 药名），得到目标行号 `Lxxxx`")
A("2. **读取**：`file_read modules/06_yishu_11zhong.md`，`offset = Lxxxx - 5`，`limit = 80`（行号以上下文 5 行为起点，可容忍 ±2 行偏差）")
A("3. **溯源**：引用原文时保留行号出处，方便复核")
A("")
A("⚠️ 本文件只做定位，不收录原文。原文一律读源文件。")
A("")

# ── 书目总览 ──
A("## 书目总览（11 部）")
A("")
A("| # | 书名 | 起始行 | 结束行 | 卷数 | 内容提要 |")
A("|---|------|--------|--------|------|----------|")
books_meta = {
    "素问悬解": "重编《素问》八十一篇，十三卷，黄氏移正错简、以类相从",
    "灵枢悬解": "重编《灵枢》八十一篇，九卷，按刺法/经络/营卫等归类",
    "难经悬解": "注解《难经》八十一难，分卷上/下",
    "伤寒悬解": "重编《伤寒论》，卷首仲景微旨+六经各篇+类证+汗下宜忌，凡16部分",
    "金匮悬解": "重编《金匮要略》，外感/内伤/外科/妇人，二十四卷",
    "伤寒说意": "以浅近文字说伤寒六经辨证大义，卷首六经六气解+十卷",
    "四圣心源": "黄氏医学总纲：天人解/六气解/脉法/劳伤/杂病/七窍/疮疡/妇人，十卷",
    "素灵微蕴": "早期理论著作，卷三/四含医案；26解+序意（27条）",
    "四圣悬枢": "温病/疫病/痘病/疹病四解+伊公四问，五卷",
    "长沙药解": "以仲景方所用药物为主，四卷载药百余种",
    "玉楸药解": "补《长沙药解》未备之药，分草/木/金石/果/禽兽/鳞介/人/杂类八部",
}
for i, (bln, bname, bend) in enumerate(book_bounds, 1):
    nvol = len(book_of_vol.get(bname, []))
    meta = books_meta.get(BOOK_DISPLAY.get(bname, bname), "")
    shown = BOOK_DISPLAY.get(bname, bname)
    A(f"| {i} | **{shown}** | {bln} | {bend} | {nvol} 卷 | {meta} |")
A("")
A("> **勘误与排版说明**：① 原文标题有少量笔误——「灵素微蕴」实为《素灵微蕴》，「四圣悬板」实为《四圣悬枢》，「玉椒药解」「玉枫药解」（含卷六/卷七卷名）实为《玉楸药解》，「金贵悬解」实为《金匮悬解》，索引已统一为正名；② 「校余偶识」为《素问悬解》卷末附录，已并入该书；③ 《金匮悬解》卷二十三/二十四原文标题作「金匮要略卷N·附录」，索引沿用原文；④ 源文件卷标题层级偶有不一（四圣心源卷二 L27052、玉楸药解卷二 L36694 为三级标题），索引照收不误；⑤ 个别篇目名有 OCR 讹字（如「齁喘解」即齁喘、「噎膈根原」即噎膈、「二十年」即二十难、目录页「谷疽/酒疽/色痘」即谷疸/酒疸/色疸），检索时可原文/正名双向尝试。")
A("")

# ── 关键词速查 ──
A("## 关键词速查")
A("")
A("| 关键词 | 定位 |")
A("|--------|------|")
keyword_map = [
    ("一气周流 / 阴阳变化", "四圣心源·天人解·阴阳变化 L26865"),
    ("五行生克（以气不以质）", "四圣心源·天人解·五行生克 L26882"),
    ("中气（劳伤解·中气）", "四圣心源·劳伤解·中气 L27499"),
    ("六气解（四圣心源卷二）", "四圣心源·卷二·六气解 L27052（六气名目 L27056 起）"),
    ("六气从化 / 六气偏见 / 本气衰旺", "四圣心源·卷二·六气解 L27060 / L27078 / L27094"),
    ("六气治法（治六气六法）", "四圣心源·卷二·六气解·六气治法 L27200"),
    ("六气解（伤寒说意卷首）", "伤寒说意·卷首·六气解 L24585"),
    ("寸口脉法", "四圣心源·脉法解·寸口脉法 L27242"),
    ("消渴（独责肝木）", "素灵微蕴·消渴解 L30706"),
    ("目病（黄元御自述误治）", "素灵微蕴·目病解 L30862"),
    ("齁喘（齁喘解，赵彦威案）", "素灵微蕴·齁喘解 L30454"),
    ("中风", "素灵微蕴·中风解 L30792"),
    ("温病名义/根原", "四圣悬枢·温病解·温病名义 L31119"),
    ("疫病原始", "四圣悬枢·疫病解·疫病原始 L31343"),
    ("痘病根原", "四圣悬枢·痘病解·痘病根原 L31783"),
    ("疹病根原", "四圣悬枢·疹病解·疹病根原 L32138"),
    ("桂枝汤证", "伤寒说意·太阳经·桂枝汤证 L24709；伤寒悬解·太阳经 L13625"),
    ("麻黄汤证", "伤寒说意·太阳经·麻黄汤证 L24715；伤寒悬解 L13788"),
    ("肾气丸（消渴冷饮案）", "素灵微蕴·消渴解 L30706（金匮悬解·卷十一·肾气丸 L20959）"),
    ("六经解", "伤寒说意·卷首·六经解 L24537"),
    ("甘草（长沙药解首药）", "长沙药解·卷一·甘草 L33006"),
    ("茯苓", "长沙药解·卷四·茯苓 L34996"),
    ("当归", "长沙药解·卷二·当归 L33711"),
    ("地黄", "长沙药解·卷二·地黄 L33750"),
    ("白术", "长沙药解·卷一·白术 L33051"),
    ("人参", "长沙药解·卷一·人参 L33090"),
    ("苍术", "玉楸药解·卷一·草部·苍术 L35934"),
    ("丁香（木部药）", "玉楸药解·卷二·木部·丁香 L36702"),
    ("缩砂仁", "玉楸药解·卷一·草部·缩砂仁 L35975"),
    ("耳目根原", "四圣心源·七窍解·耳目根原 L28708"),
    ("目病根原", "四圣心源·七窍解·目病根原 L28724"),
    ("妇人·经脉根原", "四圣心源·妇人解·经脉根原 L29168"),
    ("鼓胀根原", "四圣心源·杂病解上·鼓胀根原 L27839"),
    ("黄疸根原", "四圣心源·杂病解下·黄疸根原 L28520"),
    ("中风根原", "四圣心源·杂病解下·中风根原 L28407"),
    ("痈疽根原", "四圣心源·疮疡解·痈疽根原 L29023"),
    ("水寒土湿（病机总纲）", "四圣心源·杂病解诸根原（如消渴根原 L27969、中风根原 L28407）"),
    ("土枢四象 / 左升右降", "四圣心源·天人解·阴阳变化 L26865"),
    ("六节脏象论", "素问悬解·卷十·六节脏象论 L4947"),
    ("三部九候论", "素问悬解·卷二·三部九候论 L1004"),
    ("一难~八十一难", "难经悬解·卷上 L11615 起 / 卷下 L12044 起"),
    ("温病解第一~伊公四问", "四圣悬枢 L31115 ~ L32877"),
    ("仲景微旨（寒温异气）", "伤寒悬解·卷首·寒温异气 L12732"),
    ("伤寒类证三十六章", "伤寒悬解·卷十三 L17381"),
    ("禽兽鱼虫果食菜谷禁忌", "金匮悬解·卷二十四·附录 L23370"),
    ("头痛 / 眩晕 / 项强", "伤寒悬解·太阳经·头项强痛 L13567；四圣心源·七窍解·耳目根原 L28708（清阳不升）"),
]
for kw, loc in keyword_map:
    A(f"| {kw} | {loc} |")
A("")
A("> 更多词条：直接 match 下方「逐书篇目索引」中对应书的篇目名。")
A("")

# ── 逐书篇目索引 ──
A("## 逐书篇目索引")
A("")
for i, (bln, bname, bend) in enumerate(book_bounds, 1):
    shown = BOOK_DISPLAY.get(bname, bname)
    A(f"### {i}. {shown}（L{bln}–L{bend}）")
    A("")
    vols = book_of_vol.get(bname, [])
    secs_this = secs_by_book.get(bname, [])
    if vols:
        A("| 卷 | 行号 | 主要篇目 |")
        A("|-----|------|----------|")
        for vln, vname in vols:
            vsecs = [s for s in secs_this if s[2] == vname]
            if vsecs:
                first = vsecs[0][1]
                rest = "、".join(s[1] for s in vsecs[1:6])
                more = f" 等{len(vsecs)}篇" if len(vsecs) > 6 else ""
                A(f"| {vname} | L{vln} | {first}；{rest}{more} |")
            else:
                A(f"| {vname} | L{vln} | — |")
        A("")
        A(f"**完整篇目（{len(secs_this)}条）**：")
        A("")
        for sln, stitle, svol in secs_this:
            A(f"- `L{sln}` {stitle}")
        A("")
    else:
        A(f"**篇目（{len(secs_this)}条）**：")
        A("")
        for sln, stitle, svol in secs_this:
            A(f"- `L{sln}` {stitle}")
        A("")

A("---")
A("生成说明：本索引由脚本自动提取源文件标题生成（含二~四级标题，去重页眉/目录复述），行号与源文件一一对应。")

out = "/sandbox/workspace/skills/黄元御中医辩证skill/modules/06_yishu_11zhong_INDEX.md"
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"生成完成: {out}")
print(f"总行数: {len(lines)}")
import os
print(f"文件大小: {os.path.getsize(out)/1024:.1f} KB")
