# 三代记忆架构 — 边界划分审计

> 日期: 2026-06-12 | 审计人: Cask
> 对照: README 架构图 + 方案文档 §五

---

## 一、三层记忆架构总览

| 层 | 理论对应 | 代码位置 | 存储 | 使用方 | 状态 |
|---|----------|----------|------|--------|------|
| **工作记忆** | Baddeley 中央执行+情景缓冲区 | `memory/working.py` | Python deque (内存) | `api/ask.py` | ✅ 活跃 |
| **情景记忆** | Tulving + Zwaan 五维索引 | `memory/episodic.py` | SQLite + ChromaDB | `api/ingest.py`, `api/sleep.py` | ✅ 活跃 |
| **语义记忆** | Kintsch + Asch 完形 | `memory/semantic.py` | Python dict (内存) | **无人使用** | 🔴 死代码 |

---

## 二、Zwaan 五维索引审计

### 设计文档要求
> 按(时间, 空间, 主角, 因果, 意图)索引的事件列表
> 每个事件带重要性权重

### 实际实现

| 维度 | LLM提取 | SQLite存储 | SQLite索引 | 被读取方 |
|------|----------|------------|-----------|----------|
| 时间 (time) | ✅ | ✅ `zwaan_dims.time` | ❌ 无独立索引 | — |
| 空间 (space) | ✅ | ✅ `zwaan_dims.space` | ❌ 无独立索引 | — |
| 主角 (protagonist) | ✅ | ✅ `zwaan_dims.protagonist` | ✅ `idx_events_protag` + 独立列 | sleep.py, validation.py |
| 因果 causality | ✅ (存为`causality`) | ✅ | ❌ 无独立索引 | **⚠️ sleep.py 读的是`cause`** |
| 意图 (intent) | ✅ | ✅ `zwaan_dims.intent` | ❌ 无独立索引 | sleep.py 冲突检测 |

### 🚨 发现 BUG: 因果维度字段名不一致

**`ingestion.py` 存储:**
```python
zwaan["causality"] = "Theron is yelling, Nell panics"
```

**`sleep.py` 读取:**
```python
cause = zwaan.get("cause", "").lower()  # ← 永远为空！
```

`_adjust_importance` 通过 `cause` 匹配 `_PIVOTAL_KEYWORDS`（betray/death/discover/等）来提升关键事件权重。但实际存入的是 `causality`，读取的却是 `cause` → **关键词提升机制从未生效**。

> 影响范围：重要事件（涉及背叛/死亡/发现等）无法获得 +0.15 的权重提升 → 后续 sleep cycle 的冲突检测和弧光推进基于不准确的重要性权重。

---

## 三、数据流闭环审计（API 链路）

### ingest → events → episodic memory
```
/text (chunk) → LLM提取 → NarrativeEvent → SQLite + ChromaDB ✅
              → 角色更新 → database.py (SQLite) ✅
```

### ask → generation → OOC validation → return
```
user问 → WorkingMemory追加 → GenerationService (LLM) → ValidationService (LLM+ChromaDB查询D)
       → 选项返回给用户 ✅
       → 当前对话记入 WorkingMemory ✅
       ⚠️ 生成的选项未写入 EpisodicMemory
```
**缺口：** 用户每次问角色、得到回答的过程，本身也是"事件"——但没被存进情景记忆。这意味着 sleep cycle 无法知道"用户问了什么、角色回答了什么"。

### feedback → preferred_profile EMA → 存储
```
用户选选项+标记 → bias.py EMA计算 → database.py 更新 preferred_profile ✅
⚠️ 用户选择未作为事件写入 EpisodicMemory
```
**缺口：** GenBias 虽然学到了用户的偏好方向，但 sleep cycle 看不到"用户选了A没选B"这个行为本身作为事件。长期来看，sleep 和 genbias 两条学习曲线无法交叉验证。

### profile → 角色档案读取
```
database.py.get_character() → 直接返回 SQLite 数据 ✅
⚠️ SemanticMemory 从未被查询
```
**缺口：** `semantic.py` 定义了一个完整的 `SemanticMemory` 类（带 `get_profile` `upsert_profile` 等方法），但没有任何代码使用它。所有读/写都走 SQLite。这个类是无用代码。

### sleep → 巩固循环
```
EpisodicMemory.get_events() → database.py.get_character() 
→ 冲突检测 → 重要性调整 → 弧光推进 → trait置信度 
→ database.py.upsert_character() ✅
⚠️ 不从 SemanticMemory 读（死代码）
⚠️ 不写回 SemanticMemory
```

---

## 四、综合问题优先级

| 严重度 | 问题 | 影响 | 修复难度 |
|--------|------|------|---------|
| 🔴 **BUG** | sleep.py `zwaan["cause"]` vs ingestion `zwaan["causality"]` 字段名不匹配 | 关键事件权重提升从未生效 | 🟢 改一行 |
| 🟡 **架构** | SemanticMemory 完全死代码 | 200行无用代码，维护负担 | 🟢 标记为废弃或删除 |
| 🟡 **缺口** | User ask/feedback 不写回 EpisodicMemory | 两条学习循环（sleep + genbias）无法交叉验证 | 🟡 需设计事件类型 |
| 🟢 **优化** | Zwaan 只有 protagonist 有独立索引 | 按时间/空间/因果查询需全表扫描 | 🟢 加索引 |

---

## 五、修复建议（按优先级）

### 1. 修 BUG（5分钟）
`sleep.py` L162 将 `zwaan.get("cause", "")` 改为 `zwaan.get("causality", "")`

### 2. SemanticMemory 处理（10分钟）
三种选择：
- **(推荐)** 删掉 `semantic.py`，在 `database.py` 中加 `get_semantic_profile()` 函数作为替代
- 保留但加 `@deprecated` 警告
- 改造为 SQLite 的薄封装

### 3. Ask/Feedback 写回 EpisodicMemory（需设计，非阻塞）
可新增事件类型：
- `type: "user_ask"` — 用户提问，summary=问题内容
- `type: "user_choice"` — 用户选择了哪个选项，关联 marks
- `type: "generated_option"` — 角色生成了哪些选项（带 OOC 评分）
这样 sleep cycle 可以分析"用户偏好 vs 角色性格"的交互模式。但这是一项新功能，不阻塞提交。
