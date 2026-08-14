# Phase 2：框架合成检查清单

> 在注册前逐项检查。每项不通过 → 修补后再注册。

## 注册前自查

### frontmatter
- [ ] `name` 为 kebab-case，≤64 字符
- [ ] `name` 不含 `ima-` 前缀
- [ ] `description` 含触发词和不适用边界
- [ ] YAML 语法正确（冒号后空格、缩进一致）

### SKILL.md 核心内容
- [ ] 含关键词索引（分组：六经/方剂/症状/饮食/剂量/理论）
- [ ] 含诊断公式（≥6个，适配该中医师的辨证体系）
- [ ] 含方证/方剂速查表（≥5组类似方对比）
- [ ] 含六经/分科速查节
- [ ] 含预后/死证速查
- [ ] 含角色扮演规则（V2.3：4段式模板——激活条件/路由规则/频率约束/失败预防，见 10-roleplay-template.md）
- [ ] 含调研来源表（一手/二手/本地三级分级）
- [ ] 含内在张力章节（≥3组，取自 06-tensions.md）
- [ ] 含智识谱系章节（取自 07-intellectual-lineage.md）
- [ ] 含常见问题速查FAQ（≥5个，取自 08-faq.md）
- [ ] 含临床安全层（取自 09-clinical-safety.md，含安全提示）
- [ ] 含 modules/ 内容摘要表（V2.3新增，见 14-modules-summary.md）
- [ ] 有医案素材时：含 cases/ 医案库（证-机-方-效链，见 13-cases-guide.md）
- [ ] 无 `[TODO]` 残留
- [ ] ≤ 400 行（推荐 200-400 行；允许"索引+内嵌精选原文"混合模式放宽到 500+）

### modules/ 完整性
- [ ] 如果讲稿覆盖伤寒论：有 modules/01_shanghan.md
- [ ] 如果讲稿覆盖金匮要略：有 modules/02_jingui.md
- [ ] 如果有医案集：有 modules/ 对应文件
- [ ] modules/ 文件包含可检索的完整讲稿原文

### references/ 完整性
- [ ] 01-core-philosophy.md ≥ 5KB
- [ ] 02-decision-heuristics.md ≥ 3KB
- [ ] 03-expression-dna.md ≥ 3KB（含负面清单）
- [ ] 04-antipatterns-boundaries.md ≥ 3KB（诚实边界6层）
- [ ] 05-biography-legacy.md ≥ 3KB（含来源分级）
- [ ] 06-tensions.md ≥ 2KB（内在张力，V2.2新增）
- [ ] 07-intellectual-lineage.md ≥ 2KB（智识谱系，V2.2新增）
- [ ] 08-faq.md ≥ 2KB（常见问题速查，V2.2新增）
- [ ] 09-clinical-safety.md ≥ 2KB（临床安全层，V2.2新增）

### 行数标杆
| 组件 | 最低 | 推荐 |
|------|:---:|:---:|
| SKILL.md | 200 行 | 300-400 行 |
| 每个 reference | 100 行 | 150+ 行 |
| modules/ | 有即可 | 完整原文 |

> 行数统一规范（V2.4）：新蒸馏目标 200-400 行；优化已有 ≥ 原始行数×2；内嵌精选原文模式可放宽到 500+，以注册成功为准。

## 注册命令

```bash
ima_skill_create -d /sandbox/workspace/skills/{skill_name}/
```

## 常见注册错误

| 错误码 | 原因 | 解决 |
|--------|------|------|
| 411003 | YAML frontmatter 缺失或格式错误 | 补全 name/description |
| command not found | Shell 会话切换 | 重新执行 |
| Parse skill file failed | SKILL.md 内容格式问题 | 检查 YAML 语法 |
