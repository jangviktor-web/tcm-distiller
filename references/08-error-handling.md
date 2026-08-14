# 系统性错误处理与回退机制

> **版本**: v2.0  
> **适用范围**: TCM-Distiller v2 全流水线  
> **更新日期**: 2025-07-14

---

## 1. 子Agent超时/失败处理

### 1.1 重试机制

| 重试次数 | 等待间隔 | 触发条件 |
|---------|---------|---------|
| 第1次重试 | 10s | 子Agent调用超时 或 返回 `status: error` |
| 第2次重试 | 30s | 第1次重试仍失败 |
| 第3次重试 | 60s | 第2次重试仍失败 |

**实现伪代码**：

```python
RETRY_INTERVALS = [10, 30, 60]
MAX_RETRIES = len(RETRY_INTERVALS)

for attempt in range(MAX_RETRIES):
    result = invoke_sub_agent(dimension, model=current_model)
    if result.status == "success":
        break
    if attempt < MAX_RETRIES - 1:
        sleep(RETRY_INTERVALS[attempt])
        log.warning(f"重试第{attempt+1}次: 维度={dimension}")
    else:
        # 进入降级策略
        handle_degration(dimension, error=result.error)
```

### 1.2 降级策略

当同一维度在当前模型档位下连续失败后，按序执行降级：

| 降级步骤 | 操作 | 说明 |
|---------|------|------|
| Step 1 | `heavy` → `light` 模型降级 | 使用更轻量的模型继续执行该维度 |
| Step 2 | `light` 模型仍失败 → 跳过 | 进入跳过策略（见 1.3） |

> **注意**：降级仅针对**当前失败维度**，不影响其他维度正常执行。如果主模型本就是 `light`，则直接进入跳过策略。

### 1.3 跳过策略

- **跳过的触发条件**：同一维度**连续 3 次失败**（含重试 + 降级后的重试）
- **跳过时的操作**：
  1. 中止该维度的所有后续尝试
  2. 在 `已知差距清单` 中记录一条条目（格式见下方）
  3. 继续处理下一个维度

**已知差距清单条目规范**：

```yaml
- dimension: "决策启发式"
  stage: "素材分析"
  error: "OpenAI API 返回 429 RateLimitError"
  retry_count: 3
  degration_used: true
  skipped_at: "2025-07-14T10:32:00Z"
  impact: "该维度使用默认占位内容填充"
```

**已知差距清单存储位置**：  
每次流水线执行结束后，自动追加到 `references/known-gaps.yaml`。如果该文件不存在则自动创建。

---

## 2. 网络搜索失败处理

### 2.1 分层备用机制

```
主方案: 原始关键词搜索
  │
  ├─ ❌ 失败 → 第一备用: 切换搜索关键词
  │               │
  │               ├─ 精简: 去掉停用词/限定词，保留核心术语
  │               └─ 扩展: 添加同义词/上位词/英文对应词
  │
  ├─ ❌ 失败 → 第二备用: 仅使用本地素材分析
  │               │
  │               └─ 依赖本地素材库 + 模型已有知识
  │
  └─ ❌ 失败 → 第三备用: 标注缺失 + 占位符
                  │
                  └─ SKILL.md 中留占位注释
```

### 2.2 关键词切换策略

| 策略 | 示例（原始: "中医辨证论治思维特征"） |
|------|--------------------------------------|
| **精简** | `辨证论治 思维` |
| **扩展** | `中医 辨证论治 思维特征 临床决策 模式` |
| **英文** | `TCM syndrome differentiation thinking pattern` |
| **混合** | `traditional Chinese medicine辩证思维 cognitive model` |

### 2.3 仅本地素材方案

当第一备用仍失败时，搜索范围回退至知识库：

1. 搜索 `kb`（个人知识库）中与该维度相关的所有素材
2. 搜索 `note` 中所有相关笔记
3. 仅基于以上本地内容 + 模型训练知识进行分析
4. 输出中标注：`[来源说明：仅基于本地素材，未进行网络验证]`

### 2.4 素材缺失标注

当所有备用方案均失败时：

1. 在 SKILL.md 对应维度下插入占位注释：
   ```markdown
   <!-- TODO: 素材缺失 - 维度: [维度名称] - 需人工补充 -->
   ```
2. 在 `known-gaps.yaml` 中记录：
   ```yaml
   - dimension: "..."
     stage: "搜索"
     error: "所有搜索方案均失败"
     fallback_used: ["精简关键词", "扩展关键词", "英文搜索", "仅本地素材"]
     placeholder_added: true
     timestamp: "2025-07-14T10:32:00Z"
   ```

---

## 3. 输入素材格式校验

所有输入素材在进入分析流水线前，需通过以下四层校验：

### 3.1 文件大小校验

| 阈值 | 处理方式 |
|------|---------|
| < 10 MB | ✅ 正常处理 |
| ≥ 10 MB | ⚠️ 记录警告日志 + 提示用户拆分文件 |
| ≥ 50 MB | ❌ 拒绝处理，返回错误信息 |

**校验代码示例**：

```python
MAX_FILE_SIZE_MB = 10
file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
if file_size_mb >= MAX_FILE_SIZE_MB:
    log.warning(f"文件过大: {file_path} ({file_size_mb:.1f}MB)")
    if file_size_mb >= 50:
        raise FileTooLargeError(f"文件超过50MB，无法处理: {file_path}")
    return Warning(f"建议将文件拆分为小于{MAX_FILE_SIZE_MB}MB的片段")
```

### 3.2 编码校验

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 检测编码 | 使用 `chardet` 或 `cchardet` 检测文件编码 |
| 2 | UTF-8 检查 | 若检测为 UTF-8，直接读取 |
| 3 | 自动转码 | 若非 UTF-8，尝试转换为 UTF-8（支持 GBK/GB2312/Big5/Shift-JIS 等常见编码） |
| 4 | 转码失败 | 记录错误，跳过该素材 |

```python
import chardet

with open(file_path, "rb") as f:
    raw = f.read()
    detected = chardet.detect(raw)
    encoding = detected.get("encoding", "utf-8")
    
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw.decode(encoding)
            # 成功转码
        except (UnicodeDecodeError, LookupError):
            log.error(f"无法解码文件: {file_path}, 检测编码: {encoding}")
            raise
```

### 3.3 内容完整性校验

| 检查项 | 方法 | 未通过处理 |
|--------|------|-----------|
| 文件非空 | `os.path.getsize() > 0` | 跳过该文件，记录空文件警告 |
| 可读内容 | 去除空白后 `len(text.strip()) > 100` | 跳过该文件，记录无实质内容警告 |
| 最小段落数 | 至少包含 1 个完整段落（>50字） | 标记为"内容过少"，降级为辅助素材 |

### 3.4 OCR 质量校验

适用于图片/扫描件经 OCR 处理后的文本：

| 检测项 | 判定标准 | 处理方式 |
|--------|---------|---------|
| 乱码字符率 | `□`、`▯`、`�` 等占全文比例 > 5% | ⚠️ 提示人工校验 |
| 异常连续符号 | 连续 10+ 个非常见字符 | ⚠️ 提示可能存在 OCR 错误 |
| 低质量标记 | 包含 "OCR识别结果"、"置信度<80%" 等元信息 | ✅ 自动标记后继续处理 |

```python
GARBAGE_CHARS = set("□▯�■●◆※＠＆＊＃")
ocr_text = read_file(file_path)
garbage_count = sum(1 for c in ocr_text if c in GARBAGE_CHARS)
garbage_ratio = garbage_count / max(len(ocr_text), 1)

if garbage_ratio > 0.05:
    log.warning(f"OCR质量低: 乱码率 {garbage_ratio:.1%}, 建议人工校验")
    # 继续处理但添加标记
    add_quality_flag(file_path, "ocr_low_quality")
```

---

## 4. Token预算超限降级

当单次调用 Token 消耗超过预设预算时，按档位逐级降级。

### 4.1 档位定义

| 档位 | Token预算 | 分析维度数 | 每维深度 |
|------|----------|-----------|---------|
| 🟢 **深度档** | 32K tokens | 5 维 | 深度分析（含多轮追问） |
| 🟡 **标准档** | 16K tokens | 5 维 | 标准分析（单轮深入） |
| 🟠 **快速档** | 8K tokens | 3 维 | 表层分析 |
| 🔴 **最小档** | 4K tokens | 1 维 | 仅核心心智模型 |

### 4.2 降级路径

```
深度档 (32K, 9维, 深度)
  │  ⚠️ 超限
  ▼
标准档 (16K, 9维, 标准)
  │  ⚠️ 超限
  ▼
快速档 (8K, 3维)
  │  ⚠️ 超限
  ▼
最小档 (4K, 1维)
  │  ⚠️ 超限
  ▼
记录到已知差距清单，跳过该步骤
```

### 4.3 维度裁剪规则（快速档 → 最小档）

| 档位 | 保留维度 | 说明 |
|------|---------|------|
| **深度/标准档** | 全部 5 维 | 1. 核心心智模型<br>2. 概念构建框架<br>3. 决策启发式<br>4. 认知路径<br>5. 表达DNA |
| **快速档 (3维)** | 3 维 | 1. 核心心智模型 ✅<br>2. 决策启发式 ✅<br>3. 表达DNA ✅<br>4. 概念构建框架 ❌<br>5. 认知路径 ❌ |
| **最小档 (1维)** | 1 维 | 1. 核心心智模型 ✅<br>2-5. 其余维度 ❌ |

### 4.4 Token消耗监控

每次子Agent调用前后记录 Token 消耗：

```python
def monitor_token_usage(func):
    def wrapper(*args, **kwargs):
        before = get_token_usage()  # 采集调用前
        result = func(*args, **kwargs)
        after = get_token_usage()   # 采集调用后
        consumed = after - before
        log.info(f"[Token] {func.__name__}: consumed={consumed}, "
                 f"budget={kwargs.get('budget', 'N/A')}")
        if consumed > kwargs.get('budget', float('inf')):
            log.warning(f"[Token] 超限: {consumed} > {kwargs.get('budget')}")
            # 触发降级
            raise TokenBudgetExceeded(consumed, kwargs.get('budget'))
        return result
    return wrapper
```

---

## 5. 中间产物版本管理

### 5.1 备份机制

每次对 `SKILL.md` 进行修改前，必须执行备份：

```bash
# 备份当前版本
cp SKILL.md SKILL.md.bak

# 确认备份成功
diff SKILL.md SKILL.md.bak > /dev/null && echo "备份成功" || echo "备份失败"
```

**备份文件命名规范**：

| 场景 | 命令 |
|------|------|
| 单次备份 | `cp SKILL.md SKILL.md.bak` |
| 分版本备份 | `cp SKILL.md SKILL.md.bak.$(date +%Y%m%d_%H%M%S)` |

### 5.2 注册前校验

在执行 `ima_skill_create -d` 或 `ima_skill_update -d` 前，必须确认：

```bash
# 检查 YAML frontmatter 是否存在
head -1 SKILL.md | grep -q "^---" && echo "Frontmatter 存在" || echo "缺少 Frontmatter！"

# 检查必填字段
python3 -c "
import yaml
with open('SKILL.md') as f:
    content = f.read()
parts = content.split('---')
if len(parts) >= 3:
    meta = yaml.safe_load(parts[1])
    required = ['name', 'description', 'version']
    for field in required:
        assert field in meta, f'缺少必填字段: {field}'
    print('校验通过')
else:
    print('格式错误：缺少 YAML frontmatter')
"
```

### 5.3 回滚方法

```bash
# 标准回滚（从单次备份恢复）
cp SKILL.md.bak SKILL.md && echo "已回滚至上一个版本"

# 注册回滚后的版本
ima_skill_create -d   # 首次注册 或
ima_skill_update -d   # 更新已有 skill

# 如果指定版本备份存在
cp SKILL.md.bak.20250714_100000 SKILL.md && echo "已回滚至 20250714_100000 版本"
```

### 5.4 版本管理清单

| 阶段 | 操作 | 说明 |
|------|------|------|
| 修改前 | `cp SKILL.md SKILL.md.bak` | 备份当前稳定版本 |
| 修改后 | 人工审查 diff 输出 | 确认修改正确 |
| 注册前 | 校验 YAML frontmatter | 确保必填字段完整 |
| 注册后 | 验证注册结果 | `ima_skill_list` 检查 |
| 出错时 | 执行回滚脚本 | 恢复上一个版本 |

---

## 6. 质量校验 Gate 模型

### 6.1 Gate 流程

```
 ┌─────────────────────────────────────────────────────────┐
 │                 Phase X 产出                             │
 │    (子Agent分析结果 / SKILL.md草稿 / 素材标注)              │
 └──────────────────────┬──────────────────────────────────┘
                        │
                        ▼
 ┌─────────────────────────────────────────────────────────┐
 │              格式校验 (Checklist)                         │
 │                                                         │
 │  □ 1. YAML frontmatter 完整且合法                         │
 │  □ 2. 所有必填字段已填写                                  │
 │  □ 3. 无占位符残留 (TODO / FIXME)                        │
 │  □ 4. 引用格式正确                                      │
 │  □ 5. 所有链接可访问（若含 URL）                           │
 │  □ 6. 无编码/乱码问题                                    │
 │  □ 7. 文件大小在限制范围内                                │
 └──────────────────────┬──────────────────────────────────┘
                        │
                        ▼
                    ┌──────┐
                    │ 通过? │
                    └──┬───┘
               ┌───────┴────────┐
               ✅ 是             ❌ 否
               │                 │
               ▼                 ▼
    ┌──────────────────┐  ┌──────────────────┐
    │  进入下一阶段      │  │  重试或降级        │
    │  (继续正常流程)    │  │  (retry_count++)  │
    └──────────────────┘  └────────┬─────────┘
                                   │
                          ┌────────┴────────┐
                          │ retry_count     │
                          │ >= 3?           │
                          └───┬──────┬──────┘
                         ✅ 是    ❌ 否
                          │        │
                          ▼        ▼
              ┌─────────────────┐  └─→ 修正后重试
              │ 记录到已知差距    │     (回到"格式校验")
              │ 清单，继续执行    │
              └─────────────────┘
```

### 6.2 各阶段 CheckList 明细

#### Phase 1: 素材分析阶段 Gate

```yaml
checklist:
  - check: "文件大小 < 10MB"
    command: "stat -c%s {file} | awk '{if($1>10485760) print \"FAIL\"; else print \"PASS\"}'"
  - check: "编码为 UTF-8"
    command: "file -i {file} | grep -q 'charset=utf-8' && echo 'PASS' || echo 'FAIL'"
  - check: "内容非空"
    command: "[ -s {file} ] && echo 'PASS' || echo 'FAIL'"
  - check: "无高频乱码字符"
    command: "python3 -c \"open('{file}').read().count('□') < len(open('{file}').read())*0.05 and print('PASS') or print('FAIL')\""
```

#### Phase 2: 维度分析阶段 Gate

```yaml
checklist:
  - check: "9维度全部完成（或已记录跳过）"
    command: "grep -q '维度.*分析完成\|known_gap' {output_dir}/summary.md && echo 'PASS' || echo 'FAIL'"
  - check: "无原始报错信息残留"
    command: "! grep -qi 'traceback\\|error\\|exception' {output_dir}/*.md && echo 'PASS' || echo 'FAIL'"
  - check: "每维输出不低于最低字数要求 (300字)"
    command: "python3 -c \"min_len=min(len(open(f'{output_dir}/{d}.md').read()) for d in dimensions); print('PASS' if min_len>=300 else 'FAIL')\""
```

#### Phase 3: SKILL.md 生成阶段 Gate

```yaml
checklist:
  - check: "YAML frontmatter 存在"
    command: "head -1 SKILL.md | grep -q '^---' && echo 'PASS' || echo 'FAIL'"
  - check: "必填字段完整"
    command: "python3 -c \"import yaml; m=yaml.safe_load(open('SKILL.md').read().split('---')[1]); assert all(k in m for k in ['name','description','version']); print('PASS')\""
  - check: "无 TODO 占位符残留"
    command: "! grep -qi 'TODO\\|FIXME\\|占位' SKILL.md && echo 'PASS' || echo 'FAIL'"
  - check: "版本号已递增"
    command: "grep '^version:' SKILL.md | grep -q 'v2\\|v3' && echo 'PASS' || echo '注意检查版本号'"
```

### 6.3 Gate 执行引擎

```python
def run_gate(phase: str, artifacts: dict) -> dict:
    """
    执行指定阶段的质量门禁检查。
    
    Args:
        phase: 阶段名称 ("phase1_material" / "phase2_dimension" / "phase3_skill")
        artifacts: 待检查的产物字典 {name: file_path}
    
    Returns:
        {"passed": bool, "results": {check_name: "PASS"/"FAIL"}, "retry_count": int}
    """
    checklist = load_checklist(phase)
    results = {}
    all_passed = True
    
    for check in checklist:
        result = execute_check(check, artifacts)
        results[check["check"]] = result
        if result != "PASS":
            all_passed = False
    
    if not all_passed:
        retry_count = get_retry_count(phase)
        if retry_count >= 3:
            record_known_gap(phase, results)
            return {"passed": False, "results": results, "action": "skip_and_continue"}
        else:
            increment_retry_count(phase)
            return {"passed": False, "results": results, "action": "retry"}
    
    reset_retry_count(phase)
    return {"passed": True, "results": results, "action": "proceed"}
```

### 6.4 重试与跳过规则

| 阶段 | 重试内容 | 跳过后果 |
|------|---------|---------|
| Phase 1 | 重新采集/校验素材 | 跳过该素材，使用其余素材继续 |
| Phase 2 | 重新调用子Agent分析该维度 | 该维度标记为"已知差距"，使用默认模板填充 |
| Phase 3 | 重新生成 SKILL.md | 使用上一版本的 SKILL.md（若有备份） |

---

## 附录

### A. 错误码速查表

| 错误码 | 含义 | 处理方式 |
|--------|------|---------|
| `E001` | 子Agent超时 | 重试 → 降级 → 跳过 |
| `E002` | API鉴权失败 | 检查 API Key，中止流程 |
| `E003` | Token预算超限 | 降级档位 |
| `E004` | 文件过大 | 提示拆分或跳过 |
| `E005` | 编码错误 | 自动转码或跳过 |
| `E006` | OCR质量过低 | 标记并继续，提示人工校验 |
| `E007` | 搜索无结果 | 依次切换备用方案 |
| `E008` | YAML格式错误 | 修正后重试，最多3次 |

### B. 文件结构

```
references/
├── 08-error-handling.md     # 本文档
├── known-gaps.yaml           # 已知差距清单（自动生成）
└── templates/
    └── gap-record.yaml       # 差距记录模板
```
