# 蒸馏过程留档规范

> V2.3 新增。对标倪海厦 skill（nihaixia）保留的 `references/research/_distill_log.txt` + 8 个过程文档。
> 用途：记录"这个 skill 是怎么来的"，支持后续迭代、溯源、交接。

## 留档内容

### 1. 蒸馏日志 `_distill_log.txt`（放在 references/ 根）

```text
{人物名}蒸馏日志
==============
源文件: {素材清单：讲稿/录音稿/医案集，含路径}
处理: {素材行数/字符数统计}

子Agent产出:
- Agent 1 核心心智: {产出文件名} ({大小})
- Agent 2 决策启发式: {产出文件名} ({大小})
- ...

跳过维度: {哪些维度没提取，为什么}
已知差距: {待补清单}
```

### 2. 调研来源记录

在 05-biography-legacy.md 中已含来源分级表，蒸馏时把**实际用到的来源**记录进去：
- 一手素材：{具体文件/录音，含获取途径}
- 二手素材：{具体报道/转述，标注可信度}
- 黑名单命中：{哪些来源被排除}

### 3. 版本历史 `CHANGELOG.md`（必建，V4.0 由"可选"升为"必建"）

```markdown
# CHANGELOG

## V1.0 (2026-XX-XX)
- 初始蒸馏：{来源}，{覆盖范围}

## V1.1 (2026-XX-XX)
- 新增：{内容}
- 修复：{问题}
```

## 为什么重要

| 场景 | 留档的价值 |
|------|-----------|
| 用户问"这个回答的依据" | 可回查来源分级表 |
| 后续优化（Phase 6） | 知道缺什么素材、上次跳过什么 |
| 交接他人 | 新接手者通过日志快速理解结构 |
| 质量审计 | 素材来源可追溯，防止二手信息污染 |

## 对标参考（nihaixia 的实际留档）

```
nihaixia/references/research/
├── _distill_log.txt      # 蒸馏日志（源文件行数/字符数/处理记录）
├── 01-writings.md        # 著作分析
├── 02-conversations.md   # 对话风格
├── 03-expression-dna.md  # 表达DNA
├── 04-external-views.md  # 外界评价
├── 05-decisions.md       # 决策记录
├── 06-timeline.md        # 时间线
├── 07-teaching-methodology.md  # 教学方法
├── 08-clinical-cases.md  # 临床案例
└── combined_reference.md # 合并精简版
```

> nihaixia 的 research/ 就是它的"蒸馏档案"——我们把这套机制规范化。
