# Phase 3：质量验证标准

> 以倪海厦 nihaixia skill 为参照标杆。
> 以下数据来自实际对比（2026-07-24）：

## 倪海厦 Skill 架构（标杆值）

```
nihaixia/
├── SKILL.md        11,202 行（含所有核心内容+诊断公式+医案精选）
├── modules/         3.1 MB（10个模块：伤寒/金匮/内经/针灸/本草/医案/梁冬对话/…)
└── references/      56 KB
```

## 对比检查表

| 维度 | 胡希恕 V1.0 | 胡希恕 V2.0 | 倪海厦标杆 | 检查项 |
|------|:----------:|:----------:|:----------:|--------|
| SKILL.md 行数 | 60 ❌ | 304 ⚠️ | 11,202 | ≥ 200 行即可（推荐 200-400） |
| modules/ 大小 | 无 ❌ | 1.9MB ✅ | 3.1MB | 必须 ≥ 原始讲稿大小 |
| 诊断公式 | 0 ❌ | 20 公式 ✅ | 8 公式 | ≥ 6 个 |
| 方证鉴别表 | 无 ❌ | 9 组 ✅ | 9 组 | ≥ 5 组 |
| 饮食调理公式 | 无 ❌ | 8 公式 ✅ | 有 | 有则加分 |
| 剂量公式 | 无 ❌ | 4 公式 ✅ | 有 | 有则加分 |
| S7 剂量勘误（V4.0新增） | — | — | 258方全勘误 ✅ | **方剂/经方型必做**：勘误表+二次检测+P0-P3 修复+汇总报告（含三体系换算与诚实标注，见 references/26） |
| 条辨框架 | 无 ❌ | 七步法 ✅ | 有 | 有则加分 |
| 六经/分科速查 | 无 ❌ | 12 节 ✅ | 12 节 | 覆盖该中医辨证体系 |
| 常见问题FAQ | 无 ❌ | 7 个 ✅ | 有 | ≥ 5 个 |
| 角色扮演规则 | 无 ❌ | 5 条 ✅ | 有 | 必须有 |
| 内在张力（V2.2新增） | 无 ❌ | — | 4 组（nihaixia「内在张力」章节） | ≥ 3 组，含两面原文支撑 |
| 智识谱系（V2.2新增） | 无 ❌ | — | 有（受谁影响→影响谁→思想地图） | 必须有 |
| 临床安全层（V2.2新增） | 无 ❌ | — | 有（误治急救/传变预警/用药铁律） | 必须有 |
| 调研来源分级（V2.2新增） | 无 ❌ | — | 有（一手/二手/本地） | 必须有 |
| 角色扮演4段式（V2.3新增） | 无 ❌ | — | 有（激活/路由/频率/失败预防） | 必须有 |
| 医案库 cases/（V2.3新增） | 无 ❌ | — | 6类140KB | 有素材则≥5案，证-机-方-效链 |
| 模块内容摘要表（V2.3新增） | 无 ❌ | — | 有（modules摘要节） | 必须有 |
| 角色一致性自测（V2.3新增） | 无 ❌ | — | — | 4类12题，❌<2 |
| 调研来源表 | 弱 ❌ | 详 ✅ | 有 | 必须有 |
| 关键词索引 | 粗略 ❌ | 分组 ✅ | 极详 | 分组即可 |
| references 文件数 | 5 个 ✅ | 7 个 ✅ | 有 | ≥ 5 个 |

> ⚠️ 注：倪海厦的 SKILL.md 11K 行是特例（他把所有 content 塞进了 SKILL.md），其他技能不必追求这个数字。300+ 行 + modules/ 完整原文是合理的架构。

## 迭代检查流程

```
Phase 2 注册后 → 用户试用 → 发现问题
    ↓
如果用户说"缺失了什么"：
  1. 用 shell 检查当前所有文件行数和大小
  2. 对比上表找出差距项
  3. 用 find/grep 从 modules/ 搜索对应内容
  4. 补充到 references/ 和 SKILL.md
  5. 重新注册
    ↓
如果用户说"参考XX架构完善"：
  1. 读取 XX skill 的文件结构
  2. 逐项对比差异
  3. 补齐缺失的组件
  4. 重新注册
```

## 自动化质量脚本（可选）

```bash
# 检查 skill 健康状态
python3 << 'PY'
import os
dir = "/sandbox/workspace/skills/{skill_name}"
issues = []

# 检查文件大小
for f in ['references/01-core-philosophy.md',
          'references/02-decision-heuristics.md']:
    p = os.path.join(dir, f)
    if os.path.exists(p) and os.path.getsize(p) < 3000:
        issues.append(f"{f} 太小 ({os.path.getsize(p)}B)")

# 检查 modules/
if not os.path.exists(f"{dir}/modules/"):
    issues.append("缺少 modules/ 目录")

# 检查 SKILL.md 行数
skill = open(f"{dir}/SKILL.md").read()
if skill.count('\n') < 200:
    issues.append(f"SKILL.md 只有 {skill.count(chr(10))} 行")

# 检查内在张力（V2.2新增）
if not os.path.exists(f"{dir}/references/06-tensions.md"):
    issues.append("缺少 references/06-tensions.md（内在张力）")
elif open(f"{dir}/references/06-tensions.md").read().count("张力") < 3:
    issues.append("内在张力不足 3 组")

# 检查 V2.2 新增维度文件
for name, path in [("智识谱系", "07-intellectual-lineage.md"),
                   ("常见问题速查", "08-faq.md"),
                   ("临床安全层", "09-clinical-safety.md")]:
    p = os.path.join(dir, "references", path)
    if not os.path.exists(p):
        issues.append(f"缺少 references/{path}（{name}）")

if issues:
    print("⚠️ 发现以下问题:")
    for i in issues: print(f"  - {i}")
else:
    print("✅ 质量检查通过")
PY
```
