# 发布物料规范

> V2.3 新增。对标倪海厦 skill（nihaixia）的 README.md（含徽章/安装说明/触发词）+ logo + 版本号。
> 用途：蒸馏完成后的对外交付件，让技能可传播、可安装、可识别。

## 必交付件

### 1. README.md（技能目录根）

对标 nihaixia README 结构：

```markdown
<div align="center">
<img width="120" src="logo.jpg" alt="{人物名}skill Logo">
# {人物名}skill · {一句话定位}
**{核心卖点}**：{如 129条伤寒论 · 23篇金匮 · 849个医案}
[![版本](https://img.shields.io/badge/版本-V{版本号}-blue)](CHANGELOG.md)
</div>

> 「{人物最有代表性的一句原话}」—— {人物名}

### 一句话介绍
{将{人物名}的思维体系蒸馏为可激活的 Agent Skill}

**直接激活词**：{触发词1} / {触发词2} / {触发词3}

## 快速安装
{安装方式：clawhub / 手动复制 + ima_skill_create}

## 目录结构
{技能目录树}

## 使用示例
{2~3 个示例问答}

## 免责声明
{安全声明：教育用途、不提供医疗建议等}
```

### 2. 触发词清单

在 README 和 SKILL.md description 中保持一致：

| 触发词 | 场景 |
|--------|------|
| {姓名} | 通用提问 |
| {姓名}会怎么看 | 角色视角提问 |
| {学派}思维 | 用其思维框架分析 |
| {代表理论} | 特定理论问题 |

> 触发词 = 人物姓名 + 视角短语 + 学派词 + 代表理论词，4 类至少各 1 个。

### 3. 版本号规范

| 版本 | 含义 | 示例 |
|------|------|------|
| V1.0 | 首次蒸馏完成 | V1.0 |
| V1.x | 内容补充/修复 | V1.1、V1.2 |
| V2.0 | 结构级优化（如新增维度） | V2.0 |
| +Bencao 等后缀 | 特殊增强包 | V2.1+Bencao |

版本号写入：README 徽章（可选）+ SKILL.md description（可选）+ **CHANGELOG.md（必建）**

**CHANGELOG 最小模板**（V3.6 新增·要求产出 skill 必带）：
```markdown
# {人物名} Skill 更新日志

## V{版本号}（{日期}）

### 🔧 修复
- {如：清除 SKILL.md 行号残留引用 2 处（L4868 → 搜"判断瘀血的方法"）}
### ✨ 新增
- {如：关键词索引 +12 条（甲状腺/尿毒症/渐冻症…）}
### 📈 优化
- {如：索引引用 97 → 132 条，全部实测验证有效，0 失效}
### ⏸ 保留未采纳
- {如：西医批评不补索引（命中 534 行噪音无定位价值）}
```

### 4. logo（可选）

- 尺寸：120px 展示用，源文件建议 512×512
- 命名：logo.jpg / logo.png，放技能目录根
- 主题：与人物/学派相关（如 nihaixia 用中医风格图）

## 交付检查清单

- [ ] README.md 存在，含一句话介绍 + 安装方式 + 免责声明
- [ ] 触发词在 README 与 SKILL.md description 一致
- [ ] 版本号规范（**CHANGELOG.md 必建**，README 徽章可选叠加）
- [ ] 安全声明明确（教育用途、不提供医疗/诊断建议）
- [ ] 示例问答 ≥ 2 个（展示角色风味）

## 发布渠道（V4.1 新增·源自 wujutong 发布实战）

### 1. GitHub 推送（git 直连不可用时走 Git Data API）
- 网络事实：github.com 直连常被墙、codeload.github.com 可下载 zip、api.github.com 可访问（带 Bearer PAT）
- 四步推送：POST /git/blobs（base64 逐文件）→ POST /git/trees → POST /git/commits → PATCH /git/refs/heads/main
- 坑：GitHub Secret Scanning 拦截含 token 的 blob（422）——排除 .git/（config 含 token）与 .bak；未认证限流 60 次/小时，全带 Bearer（5000 次/小时）
- 发布前必须：GBK 乱码全清（见 references/20 编码统一）、文件编码统一 UTF-8

### 2. ClawHub 发布
- `clawhub login`（@用户名）→ `clawhub publish` 或 install 流程
- 注意：发布前备份 cases/ 等大目录（wujutong 实测：乱码文件被平台误删导致同步中断）

### 3. 打包交付
- skill 本体 tar.gz（排除 mp4/wav 大文件）
- 附配套文档包（勘误表/审计报告/CHANGELOG）
