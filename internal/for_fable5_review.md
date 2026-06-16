# Narrative Memory Agent — Architecture Review Request for Fable 5

## Project Overview

**Narrative Memory Agent (NMA)** is a hackathon project for the Qwen Cloud Global AI Hackathon (Track 1: MemoryAgent), deadline July 10, 2026.

**What it does:** You give the agent a novel, it distills a character from it, and then you can ask that character "What would you do in this situation?" The character responds in first-person with 2-3 development options, each scored for OOC (Out-of-Character) risk. It's for authors stuck at plot bottlenecks who want to ask their characters directly.

**Tech stack:** FastAPI (Python) backend, Next.js frontend, Qwen Cloud LLM APIs (`qwen3.6-plus` + `text-embedding-v3`), SQLite + ChromaDB (local file-based) for storage.

**Psychological theory grounding:** Baddeley working memory, Tulving episodic/semantic memory, Zwaan event-indexing model (5 dimensions), Kintsch construction-integration model, Asch gestalt impression, Bartlett schema theory, Walker & Stickgold sleep consolidation, Tononi & Cirelli synaptic homeostasis.

---

## Key Files (paths relative to repo root `~/forge/narrative-memory-agent/`)

### Design Documents
- `README.md` — Project overview, architecture concept, submission requirements
- `TODO.md` — Progress tracking, 6-week schedule, remaining work
- `internal/方案文档.md` — Full design document (Chinese, 378 lines)
- `internal/跨会话记忆分析.md` — Cross-session memory analysis (105 lines)
- `internal/记忆架构审计-Zwaan索引与数据流闭环.md` — Architecture audit (121 lines)

### Backend Source Code
- `backend/app/main.py` — FastAPI entry point, 5 route prefixes
- `backend/app/config.py` — Configuration (QWEN API key, model, paths)
- `backend/app/database.py` — SQLite layer, character CRUD (127 lines)
- `backend/app/seed.py` — Demo character seeding
- `backend/app/memory/__init__.py` — Empty
- `backend/app/memory/working.py` — Working memory (30 lines)
- `backend/app/memory/episodic.py` — Episodic memory, SQLite + Zwaan indexing (127 lines)
- `backend/app/memory/semantic.py` — Semantic memory (29 lines, UNUSED)
- `backend/app/memory/vectors.py` — ChromaDB vector store wrapper (93 lines)
- `backend/app/services/ingestion.py` — Novel text → memory pipeline (361 lines)
- `backend/app/services/generation.py` — Circuit A: character voice generation (175 lines)
- `backend/app/services/validation.py` — Circuit B: OOC risk scoring (270 lines)
- `backend/app/services/bias.py` — Generation Bias EMA computation (93 lines)
- `backend/app/services/bias_prompt.py` — Bias prompt construction
- `backend/app/services/sleep.py` — Sleep consolidation, 3-phase cycle (614 lines)
- `backend/app/api/ask.py` — POST /ask/ (97 lines)
- `backend/app/api/ingest.py` — POST /ingest/ (38 lines)
- `backend/app/api/feedback.py` — POST /feedback/
- `backend/app/api/profile.py` — GET /profile/
- `backend/app/api/sleep.py` — POST /sleep/
- `backend/app/models/event.py` — NarrativeEvent dataclass
- `backend/app/models/character.py` — CharacterProfile/Trait dataclasses
- `backend/pyproject.toml` — Dependencies (28 lines)

---

## Design Document: 方案文档.md (Full Content)

```
# Narrative Memory Agent · 方案文档

## 一、一句话

> 给Agent一本小说，它蒸馏出角色，然后你可以问TA："如果是你，接下来会怎么走？"
>
> **不是陪你跟角色玩的。是帮你理解角色在想什么的。**

## 二、核心差异（vs Character.AI 等角色对话产品）

| 维度 | Character.AI | Narrative Memory Agent |
|------|-------------|----------------------|
| **你在干嘛** | 跟角色互动/对话 | 问角色"你怎么看自己" |
| **角色的功能** | 陪你玩，让你沉浸 | 自我揭示，让你理解 |
| **OOC意味着** | 体验被破坏了（坏事） | 角色认知模型与行为发生冲突 → **这是数据** |
| **你的收获** | 娱乐/陪伴 | 对角色的**理解** |
| **角色自己** | 没有自我意识，一切为了服务对话 | 能意识到自己的变化和困惑（元认知） |

**核心洞察**：在Character.AI里，OOC是坏事，因为它破坏了沉浸感。在Narrative Memory Agent里，OOC是**数据**——角色跟自己的认知模型发生冲突，说明角色在成长，弧光出现了。OOC校验不是为了"让角色永远不崩"，而是让角色**知道自己崩了**。

**例如**："以我的性格，遇到这个情况我会先退一步，但这件事涉及到XX底线，我这次不会忍"
——在Character.AI里不会有这段话。角色不会说"以我的性格，我本来会……"，角色直接就"我不忍了"就完了。只有在角色被训练成**能审视自己**的系统里，他才能说出这种话。这是**元认知（metacognition）**层面的差异。

## 三、用户与场景

### 用户A：作者（你）
- **场景**：写Caelvorn写到瓶颈，不知道Leo下一步该怎么走
- **痛点**：角色一致性难维持，写着写着OOC
- **用法**：上传已有章节 → 问Leo → Leo给3个发展选项（带OOC风险评分）→ 你选 → 反馈闭环

### 用户B：读者
- **场景**：追的小说烂尾/崩人设，想看看"if线"会怎么走
- **痛点**：意难平，但没人能续
- **用法**：上传小说 → 选角色 → 在关键节点问"如果你选了另一个……"
- **前提**：追更读者认识角色——ta比你更清楚主角不该怎么做。"作者写得稀烂"本身就是ta在意角色一致性的证据，因此ta的标记可信度与作者相当。

> **黑客松优先级：** 仅实现用户A（作者场景）。用户B延后，若有余力再做。
> **数据管道共享：** 两场景的标记数据走同一套 Generation Bias 系统，读者场景上线后自动继承已训练的偏好。

## 四、核心功能

### 4.1 小说摄入
- 上传文本（.txt / 粘贴内容 / 分章节）
- Agent阅读并构建三重记忆

### 4.2 角色蒸馏
- 自动识别主要角色
- 提取行为模式、中心特质、关系网
- 输出结构化角色档案

### 4.3 问角色
- 用户输入场景/问题
- 回路A（创意生成）：以角色身份生成2-3个发展选项
- 回路B（一致性校验）：每个选项给出OOC风险分数 + 理由
- 用户选择后，反馈写入记忆系统

### 4.4 睡眠巩固（后台离线）
- 读完N章后触发
- 冲突检测 → 整合 → 冗余剪枝
- 输出巩固日志（可选查看）

## 五、技术架构

```
┌────────────────────────────────────────────────────┐
│                   前端 (Next.js)                     │
│  小说上传  →  角色选择  →  对话  →  档案查看        │
└──────────────────────┬─────────────────────────────┘
                       │ HTTP API
┌──────────────────────▼─────────────────────────────┐
│                  后端 (FastAPI)                      │
│                                                     │
│  /ingest    → 小说分词 + 角色识别 + 记忆构建          │
│  /ask       → 回路A(生成) + 回路B(校验)               │
│  /profile   → 输出角色认知档案                         │
│  /sleep     → 触发睡眠巩固（可选手动）                   │
│                                                     │
│  ┌──────────────────────────────────────┐            │
│  │         三层记忆系统                     │            │
│  │  ┌──────────┐ ┌──────────┐ ┌────────┐ │            │
│  │  │ 工作记忆   │ │ 情景记忆  │ │ 语义记忆│ │            │
│  │  │ (会话缓存) │ │(事件索引) │ │(角色认知)│ │            │
│  │  └──────────┘ └──────────┘ └────────┘ │            │
│  └──────────────────────────────────────┘            │
│                                                     │
│  ┌──────────────────────────────────────┐            │
│  │      Qwen Cloud API (dashscope)       │            │
│  │  模型: qwen3.6-plus + 嵌入模型          │            │
│  └──────────────────────────────────────┘            │
└─────────────────────────────────────────────────────┘
```

### 记忆层详细设计

#### 工作记忆（Working Memory）
- **对应理论**：Baddeley工作记忆模型（中央执行 + 情景缓冲区）
- **实现**：当前对话上下文窗口（最近N轮）
- **容量**：~4K tokens 滚动窗口
- **特性**：注意力路由，决定什么存入情景记忆

#### 情景记忆（Episodic Memory）
- **对应理论**：Tulving情景记忆 + Zwaan事件索引五维度
- **实现**：按(时间, 空间, 主角, 因果, 意图)索引的事件列表
- **存储**：SQLite + 向量嵌入（用于相似度检索）
- **特性**：每个事件带重要性权重，低权重可被遗忘

#### 语义记忆（Semantic Memory）
- **对应理论**：Kintsch情境模型 + Asch完形印象
- **实现**：角色认知图式（中心特质 + 行为模式 + 动机曲线 + 关系网）
- **存储**：结构化的JSON文档 + 向量索引
- **特性**：睡眠巩固时从情景记忆中提取/更新

### 双回路响应流程

```
用户提问："Leo，如果仇人来找你合作，你会怎么做？"
                ↓
     ┌── 回路A：创意生成 ───────────────────┐
     │  用Qwen，以Leo身份思考               │
     │  输出3个选项（A/B/C）                │
     └──────────────┬──────────────────────┘
                    ↓
     ┌── 回路B：一致性校验 ───────────────────┐
     │  对比语义记忆中的Leo中心特质            │
     │  比对历史行为模式                     │
     │  每个选项输出OOC风险评分               │
     │    选项A: 吻合88% ✅                   │
     │    选项B: 吻合62% ⚠️（轻微偏离）        │
     │    选项C: 吻合23% ❌（高危OOC）         │
     └──────────────┬──────────────────────┘
                    ↓
              用户选择 → 反馈写入情景记忆
```

### 睡眠巩固流程

```
触发条件：新增N个事件 / 手动触发 / 定时
                ↓
    Phase 1 - 事实巩固（类比NREM/SWS）
      情景→语义迁移：提取事件中的重复模式
      冲突检测：新事件与已有认知矛盾→标记待解决
                ↓
    Phase 2 - 抽象整合（类比REM）
      模式提取："Leo第3-5章都选择退让→回避应对模式"
      冗余剪枝：删除低权重/已整合的原始事件
      情感解耦：事件的情感标签与内容分离存储
                ↓
    Phase 3 - 输出报告
      更新了哪些认知
      解决了哪些冲突
      角色认知置信度变化
```

## 六、技术选型

| 层 | 技术 | 理由 |
|----|------|------|
| **前端** | Next.js | 你熟，渡心阁同栈 |
| **后端** | FastAPI + Python | 我帮你写，生态好 |
| **LLM** | Qwen3.6-plus (dashscope) | 比赛要求，OpenAI兼容SDK |
| **嵌入** | Qwen embedding API | 同平台，零额外费用 |
| **向量存储** | ChromaDB (本地文件) | 轻量，无需部署外部服务 |
| **结构化存储** | SQLite | 单文件，部署简单 |

## 九、Generation Bias：选择驱动生成偏向

> 2026/5/31 新增 — Jasmine 提出。

### 9.1 核心理念
> **用户的标记才是最好的学习。**

系统不猜用户为什么选某个选项——直接问。通过一次简单的标记（多选），获取选择背后的语义，从而决定"这个选择是否应该影响未来的生成偏向"。

### 9.2 完整流程

```
用户看到 3 个选项：
  A: "我不会忍"  (T=0.9, B=0.8, D=0.2, C=0.9, P=0.1 · OOC=12%)
  B: "…我忍了"  (T=0.6, B=0.5, D=0.4, C=0.7, P=0.3 · OOC=45%)
  C: "我不知道"  (T=0.3, B=0.4, D=0.7, C=0.5, P=0.6 · OOC=78%)

用户选了 B
       ↓
系统弹出一个轻量标记：
  「你选这个是因为……？」
  □ 这就是他会做的事      ← 角色驱动 → EMA 正常更新
  □ 情节需要这个走向      ← 剧情驱动 → 不更新 preferred_profile
  □ 想看看这个可能性      ← 实验心态 → 不更新
  □ 说不上来，就是感觉    ← 默认 → EMA 低权重更新

用户勾选后，系统：
  如果 角色驱动 → preferred_profile = EMA(old, B_profile, alpha=0.3)
  其它方向     → 不更新
```

### 9.6 设计优化（2026/6/9 复盘）

#### 惊奇度的 UI 表达
OOC_Risk = 1 - (αT + βB + γ(1-D) + δC - εP) 中，P（惊奇度）降低风险分——因为"出乎意料但合理的发展"是好角色的标志。

但用户看到"高风险"标签的直觉反应是"这个不对"。需要区分：
- **🔴 高风险（背离角色）**：T/B/C 低 → 角色行为不可信
- **🟠 高风险（有惊喜）**：P 高且其他因子正常 → "出乎意料但合理"

前端可在 `ooc_details` 中加一个 `type` 字段：`"violation"`（背离） vs `"surprise"`（惊喜），标签文案不同呈现。

#### 因子权重（实际代码采用的权重，validation.py）

| 因子 | 符号 | 权重 | 含义 |
|------|------|------|------|
| 特质一致性 | α | **0.35** | 是否违背核心特质 |
| 行为一致性 | β | **0.25** | 是否符合历史行为模式 |
| 语义距离 | γ | **0.15** | ChromaDB 真实向量距离归一化 |
| 自身一致性 | δ | **0.15** | 选项内部逻辑自洽性 |
| 惊奇度 | ε | **0.10** | 出乎意料但合理 → 降低 OOC 分 |

权重总和 α+β+γ+δ = 0.90，ε 从总分中减去（而非加入）。

#### Violation vs Surprise 分类
```
consistency = (T + B + C) / 3.0
if risk >= 0.66 AND consistency < 0.4  → "violation"  （背离角色）
if risk >= 0.66 AND P >= 0.6 AND consistency >= 0.4  → "surprise"  （惊喜）
else  → "normal"
```

#### D（语义距离）计算细节
D 不是 LLM 估计值，而是通过以下管道计算：
1. 对每个选项的 `voice` 文本调用 `text-embedding-v3` 生成嵌入
2. ChromaDB `events` 集合按 `protagonist` 筛选，搜索 top-k
3. 平均 top-k 的 L2 距离
4. 归一化为 `d = clamp(L2_avg / 1.5, 0, 1)`
5. 结果标记 `"D_source": "chromadb"`，消费者可据此判断 D 的可信度
```

---

## Design Document: 跨会话记忆分析.md (Full Content)

```
# 跨会话记忆 · 需求分析与架构覆盖度

> 来源：Qwen Cloud Hackathon Track1 官方要求 + NirDiamant Agent Memory Bible
> 整理日期：2026/6/1

## 一、官方要求

**原文（Qwen Cloud Hackathon 官网）：**
> *"Build an Agent with persistent memory that autonomously accumulates experience, remembers user preferences, and makes increasingly accurate decisions across **multi-turn, cross-session interactions**."*

### 三个独立要求

| 级别 | 含义 |
|------|------|
| **Multi-turn** 🗣️ | 同一次对话里，A说完B回，不要断了就忘 |
| **Cross-session** 🔄 | 关浏览器走人，明天回来开新会话，还记得昨天的事 |
| **User preferences** 🧑 | 系统知道你喜欢什么风格、上次选了哪个选项、习惯什么问法 |

三者缺一不可。

## 二、跨会话的行业定义

来自 NirDiamant Agent Memory Bible（421 stars，业界定标仓库）：

> [cross_session_memory.ipynb](https://github.com/NirDiamant/Agent_Memory_Techniques/blob/main/all_techniques/21_cross_session_memory/cross_session_memory.ipynb)
>
> *"Cross-session memory operates at the boundaries of sessions. It serializes state when a session ends and deserializes it when a new session starts."*

### 核心机制

```
Session 1: 用户来 → 对话 → 结束时保存状态
                 ↓              ↑
           持久化存储（SQLite + ChromaDB）
                 ↓              ↑
Session 2: 用户回来 → 加载记忆 → 续上对话
```

关键洞察：
- **边界操作**（serialize/deserialize）而非运行时持续同步
- session 的起点和终点是记忆操作的两个触发点
- 不需要实时双向同步——这是架构简化的重要依据

## 三、NMA 架构覆盖度

### 存储层覆盖

| 组件 | 持久化？ | 用途 | 对应需求 |
|------|---------|------|---------|
| SQLite（events / characters） | ✅ 文件持久 | 情景记忆 + 语义记忆 | Cross-session |
| ChromaDB（向量嵌入） | ✅ 文件持久 | 语义检索 | Cross-session |
| 工作记忆 | ❌ 临时的 | 当前会话上下文，每次重建 | Multi-turn（运行时） |

### 依赖链分析
SQLite 和 ChromaDB 都是文件持久 → **天然跨会话**。
用户关浏览器再打开，只要后端还在跑（或数据文件在），就记得昨天的事。

### 覆盖缺口

| 缺口 | 影响 | 方案 |
|------|------|------|
| Session resumption 代码未写 | 后端重启后不会自动从 SQLite 重建工作记忆 | 实现 `services/session_resumption.py` |
| 前端不知道"第几次来" | 无法区分冷启动 vs 续接 | 加 `/session/new` 端点 |
| User preferences 未实现 | 系统没有用户偏好表现 | Generation Bias（方案已定版） |

## 四、提交演示要点

### 方案A（现场演示首选）：切角色法
1. **与角色A对话** → 工作记忆积累上下文 → 用户做选择并标记"角色驱动"
2. **切到角色B**（触发角色A的 serialize）
3. **问角色B一个问题**（确认B的记忆独立于A）
4. **切回角色A**（触发角色A的 deserialize）
5. **角色A记得第1步的对话和选择** → 跨会话能力已证明 ✅

### 方案B（备选视频）：关浏览器重开
1. **Session 1：** 摄入一段小说 → 识别角色 → 对话 → 得到用户选择反馈
2. **关闭浏览器 / 重启服务**
3. **Session 2：** 打开页面 → 自动识别"老用户" → 角色和记忆还在 → 续上对话
4. **验证：** 角色记得昨天的关键事件，Generation Bias 反映昨天的选择倾向
```

---

## Design Document: 记忆架构审计-Zwaan索引与数据流闭环.md (Full Content)

```
# 三代记忆架构 — 边界划分审计

> 日期: 2026-06-12 | 审计人: Cask
> 对照: README 架构图 + 方案文档 §五

## 一、三层记忆架构总览

| 层 | 理论对应 | 代码位置 | 存储 | 使用方 | 状态 |
|---|----------|----------|------|--------|------|
| **工作记忆** | Baddeley 中央执行+情景缓冲区 | `memory/working.py` | Python deque (内存) | `api/ask.py` | ✅ 活跃 |
| **情景记忆** | Tulving + Zwaan 五维索引 | `memory/episodic.py` | SQLite + ChromaDB | `api/ingest.py`, `api/sleep.py` | ✅ 活跃 |
| **语义记忆** | Kintsch + Asch 完形 | `memory/semantic.py` | Python dict (内存) | **无人使用** | 🔴 死代码 |

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

## 四、综合问题优先级

| 严重度 | 问题 | 影响 | 修复难度 |
|--------|------|------|---------|
| 🔴 **BUG** | sleep.py `zwaan["cause"]` vs ingestion `zwaan["causality"]` 字段名不匹配 | 关键事件权重提升从未生效 | 🟢 改一行 |
| 🟡 **架构** | SemanticMemory 完全死代码 | 200行无用代码，维护负担 | 🟢 标记为废弃或删除 |
| 🟡 **缺口** | User ask/feedback 不写回 EpisodicMemory | 两条学习循环（sleep + genbias）无法交叉验证 | 🟡 需设计事件类型 |
| 🟢 **优化** | Zwaan 只有 protagonist 有独立索引 | 按时间/空间/因果查询需全表扫描 | 🟢 加索引 |

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
```

---

## Memory Layer — Full Source Code

### `backend/app/memory/working.py`

```python
"""Working memory — current session context buffer."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

MAX_WINDOW = 10  # rolling window of turns


@dataclass
class Turn:
    role: str  # "user" | "character"
    content: str


class WorkingMemory:
    """Short-term session buffer (Baddeley's central executive + episodic buffer)."""

    def __init__(self, max_window: int = MAX_WINDOW) -> None:
        self._buffer: deque[Turn] = deque(maxlen=max_window)

    def add(self, role: str, content: str) -> None:
        self._buffer.append(Turn(role=role, content=content))

    def get_context(self) -> list[Turn]:
        return list(self._buffer)

    def clear(self) -> None:
        self._buffer.clear()
```

### `backend/app/memory/__init__.py`

```python
# Empty file
```

### `backend/app/memory/episodic.py`

```python
"""Episodic memory — SQLite + vector retrieval (Zwaan-indexed events)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.config import SQLITE_PATH
from app.models.event import NarrativeEvent


class EpisodicMemory:
    """Event-indexed episodic store backed by SQLite.

    Each event is indexed by (time, space, protagonist, causality, intent)
    — Zwaan's event-indexing model — plus a vector embedding for
    similarity search.
    """

    def __init__(self, db_path: Path | str = SQLITE_PATH) -> None:
        self._path = Path(db_path)
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id          TEXT PRIMARY KEY,
                chapter     INTEGER NOT NULL,
                position    TEXT NOT NULL DEFAULT '',
                protagonist TEXT NOT NULL,
                summary     TEXT NOT NULL,
                importance  REAL NOT NULL DEFAULT 0.5,
                embedding   TEXT,          -- JSON float array
                related     TEXT,          -- JSON string array
                zwaan_dims  TEXT,          -- JSON dict
                emotion_tags TEXT,         -- JSON string array (Plutchik emotions)
                created_at  TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_events_protag
                ON events(protagonist);
            CREATE INDEX IF NOT EXISTS idx_events_chapter
                ON events(chapter);
        """)
        # Migration: add emotion_tags if missing (existing DB)
        try:
            self._conn.execute("ALTER TABLE events ADD COLUMN emotion_tags TEXT")
            self._conn.commit()
        except sqlite3.OperationalError:
            pass  # column already exists
        self._conn.commit()

    def add_event(self, event: NarrativeEvent) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO events
                (id, chapter, position, protagonist, summary,
                 importance, embedding, related, zwaan_dims)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.id,
                event.chapter,
                event.position,
                event.protagonist,
                event.summary,
                event.importance,
                json.dumps(event.embedding) if event.embedding else None,
                json.dumps(event.related_entities),
                json.dumps(event.zwaan_dims),
            ),
        )
        self._conn.commit()

    def get_events(
        self,
        protagonist: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM events"
        params: list[Any] = []
        if protagonist:
            query += " WHERE protagonist = ?"
            params.append(protagonist)
        query += " ORDER BY chapter, position LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = self._conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def update_importance(self, event_id: str, new_importance: float) -> None:
        self._conn.execute(
            "UPDATE events SET importance = ? WHERE id = ?",
            (new_importance, event_id),
        )
        self._conn.commit()

    def update_emotion_tags(
        self, event_id: str, tags: list[str]
    ) -> None:
        self._conn.execute(
            "UPDATE events SET emotion_tags = ? WHERE id = ?",
            (json.dumps(tags, ensure_ascii=False), event_id),
        )
        self._conn.commit()

    def delete_event(self, event_id: str) -> None:
        self._conn.execute(
            "DELETE FROM events WHERE id = ?",
            (event_id,),
        )
        self._conn.commit()

    def count_events(self, protagonist: str | None = None) -> int:
        query = "SELECT COUNT(*) FROM events"
        params: list[Any] = []
        if protagonist:
            query += " WHERE protagonist = ?"
            params.append(protagonist)
        return self._conn.execute(query, params).fetchone()[0]
```

### `backend/app/memory/semantic.py`

```python
"""Semantic memory — character cognitive schemas (traits, relations, patterns)."""

from __future__ import annotations

from typing import Any

from app.models.character import CharacterProfile


class SemanticMemory:
    """Long-term character knowledge — traits, behavior patterns, relations.

    Built and refined during sleep consolidation.
    """

    def __init__(self) -> None:
        self._profiles: dict[str, CharacterProfile] = {}

    def get_profile(self, name: str) -> CharacterProfile | None:
        return self._profiles.get(name)

    def upsert_profile(self, profile: CharacterProfile) -> None:
        self._profiles[profile.name] = profile

    def list_characters(self) -> list[str]:
        return list(self._profiles.keys())

    def get_all_profiles(self) -> dict[str, CharacterProfile]:
        return dict(self._profiles)
```

### `backend/app/memory/vectors.py`

```python
"""Vector store wrapper — ChromaDB for embedding-based retrieval."""
# ruff: noqa: ERA001

from __future__ import annotations

from typing import Any

import chromadb
from chromadb.config import Settings

from app.config import CHROMA_PATH


class VectorStore:
    """Lightweight ChromaDB wrapper for similarity search."""

    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(
            path=str(CHROMA_PATH),
            settings=Settings(anonymized_telemetry=False),
        )

    def _collection(self, name: str):
        """Get or create a named collection."""
        return self._client.get_or_create_collection(name=name)

    def add(
        self,
        collection: str,
        id: str,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        self._collection(collection).add(
            embeddings=[embedding],
            ids=[id],
            metadatas=[metadata],
        )

    def delete(self, collection: str, id: str) -> None:
        """Delete a single item by ID."""
        self._collection(collection).delete(ids=[id])

    def get_all_by_metadata(
        self,
        collection: str,
        where: dict[str, Any],
    ) -> dict[str, Any]:
        """Retrieve all items matching a metadata filter.

        Returns dict with keys: ids, embeddings, metadatas, documents.
        """
        return self._collection(collection).get(where=where)

    def search(
        self,
        collection: str,
        query_embedding: list[float],
        top_k: int = 10,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search the collection by embedding vector similarity.

        Args:
            collection: Name of the ChromaDB collection.
            query_embedding: The embedding vector to search with.
            top_k: Maximum number of results to return.
            where: Optional metadata filter dict (e.g. {"protagonist": "Caelan"}).

        Returns:
            List of {id, score (distance), metadata} dicts sorted by
            increasing distance (most similar first).
        """
        kwargs: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }
        if where:
            kwargs["where"] = where

        results = self._collection(collection).query(**kwargs)
        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "score": results["distances"][0][i]
                if results.get("distances")
                else None,
                "metadata": results["metadatas"][0][i]
                if results.get("metadatas")
                else {},
            })
        return output
```

---

## Key Service Files

### `backend/app/services/bias.py`

```python
"""Generation Bias — EMA computation for preferred_profile.

EMA (Exponential Moving Average) updates the character's preferred_profile,
a 5-dim vector [T, B, D, C, P], based on which options the user marks as
fitting the character.

Decision logic:
  - marks contains "这就是他会做的事"      → alpha=0.3  (正常更新)
  - marks only "剧情驱动/实验心态"  → 不更新
  - marks only "说不上来"          → alpha=0.1  (低权重)
  - marks empty (auto mode)        → alpha=0.15 (静默)
"""

from __future__ import annotations

from typing import Any

__all__ = ["update_preferred_profile"]

DIMENSION_KEYS = ["T", "B", "D", "C", "P"]

ALPHA_CHARACTER_DRIVEN = 0.30   # "这就是他会做的事"
ALPHA_GUT_FEELING = 0.10        # "说不上来，就是感觉"
ALPHA_AUTO = 0.15               # 默认自动（不弹窗，静默更新）
ALPHA_NONE = 0.0                # 剧情驱动/实验心态（不更新）

MARK_CHARACTER_DRIVEN = "这就是他会做的事"
MARK_PLOT_DRIVEN = "情节需要这个走向"
MARK_EXPERIMENTAL = "想看看这个可能性"
MARK_GUT_FEELING = "说不上来，就是感觉"


def _should_update(marks: list[str]) -> bool:
    if not marks:
        return True  # auto mode
    if MARK_CHARACTER_DRIVEN in marks:
        return True
    if marks == [MARK_GUT_FEELING]:
        return True
    return False


def _get_alpha(marks: list[str]) -> float:
    if not marks:
        return ALPHA_AUTO
    if MARK_CHARACTER_DRIVEN in marks:
        return ALPHA_CHARACTER_DRIVEN
    if marks == [MARK_GUT_FEELING]:
        return ALPHA_GUT_FEELING
    return ALPHA_NONE


def _ema(old: list[float] | None, new: list[float], alpha: float) -> list[float]:
    if old is None or len(old) != len(new):
        return new
    return [alpha * n + (1.0 - alpha) * o for o, n in zip(old, new)]


def _scores_to_vector(scores: dict[str, float]) -> list[float]:
    return [scores.get(k, 0.5) for k in DIMENSION_KEYS]


def update_preferred_profile(
    old_profile: list[float] | None,
    selected_scores: dict[str, float],
    marks: list[str],
) -> dict[str, Any]:
    if not _should_update(marks):
        return {"updated": False, "profile": old_profile}

    alpha = _get_alpha(marks)
    new_vector = _scores_to_vector(selected_scores)
    updated = _ema(old_profile, new_vector, alpha)

    return {"updated": True, "profile": updated}
```

### `backend/app/services/ingestion.py` (first 50 lines for structure, key methods shown)

```python
"""Ingestion service — novel text → memory construction pipeline.

Pipeline:
  1. Chunk text into manageable segments
  2. For each chunk, use Qwen to extract events + characters
  3. Build NarrativeEvent objects with Zwaan indexing
  4. Generate embeddings via text-embedding-v3
  5. Store events → EpisodicMemory (SQLite + ChromaDB)
  6. Upsert characters → Database + SemanticMemory
"""

from __future__ import annotations

import json
import re
import uuid
from typing import Any

from openai import AsyncOpenAI

from app.config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, QWEN_EMBEDDING_MODEL
from app.database import get_character, upsert_character, list_characters
from app.memory.episodic import EpisodicMemory
from app.memory.vectors import VectorStore
from app.models.event import NarrativeEvent
from app.models.character import CharacterProfile, Trait


# ── Clients ──────────────────────────────────────────────

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    return _client


class IngestionService:
    """Orchestrate novel text ingestion into the three memory layers."""

    def __init__(self) -> None:
        self._episodic = EpisodicMemory()
        self._vectors = VectorStore()

    async def process_text(self, text: str, title: str | None = None, chunk_size: int = 3000) -> dict[str, Any]:
        """Ingest novel text: extract → embed → store."""
        chunks = self._chunk_text(text, chunk_size)
        all_events: list[NarrativeEvent] = []
        all_characters: dict[str, dict[str, Any]] = {}
        chapter_number = 1

        for i, chunk in enumerate(chunks):
            result = await self._analyze_chunk(chunk, chapter_number, i + 1)
            events = result.get("events", [])
            characters = result.get("characters", {})

            for evt_data in events:
                event = self._build_event(evt_data, chapter_number, i)
                all_events.append(event)

            for name, info in characters.items():
                if name not in all_characters:
                    all_characters[name] = {"mentions": 0, "traits": [], "relations": {}}
                all_characters[name]["mentions"] += 1
                all_characters[name]["traits"] = self._merge_traits(
                    all_characters[name]["traits"], info.get("traits", []))
                all_characters[name]["relations"].update(info.get("relations", {}))

        # Generate embeddings & store events
        for event in all_events:
            embedding = await self._get_embedding(event.summary)
            if embedding:
                event.embedding = embedding
            self._episodic.add_event(event)
            if embedding:
                self._vectors.add(collection="events", id=event.id, embedding=embedding,
                                  metadata={"event_id": event.id, "protagonist": event.protagonist,
                                            "chapter": event.chapter, "summary": event.summary[:200]})

        # Upsert characters to database
        new_characters: list[str] = []
        for name, info in all_characters.items():
            existing = get_character(name)
            if not existing:
                new_characters.append(name)
            merged = self._merge_character(existing, name, info)
            upsert_character(merged)

        return {"status": "ok", "title": title or "", "chunks_processed": len(chunks),
                "events_extracted": len(all_events), "characters_found": list(all_characters.keys()),
                "new_characters": new_characters}
```

### `backend/app/services/generation.py` (Circuit A)

```python
"""Circuit A — creative generation (character voice) using Qwen API."""

from __future__ import annotations

import json
import re
from typing import Any

from openai import AsyncOpenAI

from app.config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL
from app.database import get_character
from app.memory.working import Turn
from app.services.bias_prompt import profile_to_bias_prompt


_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    return _client


class GenerationService:
    """Generate character response options in role — Circuit A."""

    async def generate_options(
        self,
        character: str,
        question: str,
        num_options: int = 3,
        context_history: list[Turn] | None = None,
    ) -> list[dict[str, Any]]:
        profile = get_character(character)
        if profile is None:
            raise ValueError(f"Character '{character}' not found in database")

        traits = profile.get("traits", [])
        trait_desc = "; ".join(
            f"{t.get('name', '?')} ({t.get('category', 'core')}): {t.get('description', '')}"
            for t in traits
        )

        system_prompt = (
            f"You are {profile['name']}.\n"
            f"Backstory: {profile.get('backstory', '')}\n"
            f"Core traits: {trait_desc}\n"
            f"Motivation: {profile.get('motivation', '')}\n"
            f"Current arc stage: {profile.get('arc_stage', 'unknown')}\n\n"
            f"You are a character in a novel. A reader/author asks you a question "
            f"about what you would do in a given situation.\n"
            f"Answer **in first person**, in your own voice and style.\n"
            f"Speak naturally — you don't have to explain yourself.\n"
            f"You can be uncertain, decisive, conflicted, or mysterious — whatever fits.\n"
        )

        if context_history:
            turns_text = "\n".join(
                f"{'Reader' if t.role == 'user' else 'You'}: {t.content}"
                for t in context_history
            )
            system_prompt += f"\nConversation so far:\n{turns_text}\n"

        preferred = profile.get("preferred_profile")
        if preferred and isinstance(preferred, list) and len(preferred) >= 5:
            bias_text = profile_to_bias_prompt(preferred)
            if bias_text:
                system_prompt += f"\n---\n{bias_text}\n---\n"

        user_prompt = (
            f"The reader now asks you: \"{question}\"\n\n"
            f"Give me {num_options} different possible responses you might give.\n"
            f"They should represent **distinctly different directions** you could take — "
            f"for example:\n"
            f"- One that stays closest to your core nature (safe/expected)\n"
            f"- One that explores a less obvious side of you (interesting/surprising)\n"
            f"- One that is bold or unexpected but still plausibly you\n\n"
            f"Return ONLY valid JSON in this exact format, no other text:\n"
            f'{{"options": [\n'
            f'  {{"label": "A", "title": "short title", "voice": "the full response in first person"}},\n'
            f'  ...\n'
            f"]}}\n"
        )

        client = _get_client()
        resp = await client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": user_prompt}],
            temperature=0.8,
            max_tokens=2048,
        )

        content = resp.choices[0].message.content or "{}"
        return self._parse_options(content)

    @staticmethod
    def _parse_options(raw: str) -> list[dict[str, Any]]:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return _fallback_options(raw)
        try:
            data = json.loads(match.group())
        except json.JSONDecodeError:
            return _fallback_options(raw)
        options = data.get("options", [])
        if not options:
            return _fallback_options(raw)
        out = []
        for i, opt in enumerate(options):
            out.append({"label": opt.get("label", chr(65 + i)),
                        "title": opt.get("title", f"Option {chr(65 + i)}"),
                        "voice": opt.get("voice", opt.get("text", ""))})
        return out


def _fallback_options(raw: str) -> list[dict[str, Any]]:
    return [{"label": "A", "title": "Response", "voice": raw[:500]}]
```

### `backend/app/services/validation.py` (Circuit B — OOC Validation)

```python
"""Circuit B — OOC validation using multi-factor scoring via Qwen + real vector distance.

Implements: OOC_Risk = 1 - (αT + βB + γ(1-D) + δC - εP)

Semantic distance (D) is computed from real ChromaDB embedding distance,
not estimated by the LLM.
"""

from __future__ import annotations

import json
import re
import statistics
from typing import Any

from openai import AsyncOpenAI

from app.config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, QWEN_EMBEDDING_MODEL
from app.database import get_character
from app.memory.vectors import VectorStore


_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    return _client


class ValidationService:
    """Validate character responses against established cognitive profile.

    Multi-factor model:
      α (trait consistency)  — 0.35  — does it violate core traits?
      β (behaviour pattern)  — 0.25  — is it consistent with past behaviour?
      γ (semantic distance)  — 0.15  — is it semantically far from the character's
                              historical events? (computed from real ChromaDB vectors)
      δ (self-consistency)   — 0.15  — is the option internally consistent?
      ε (novelty / surprise) — 0.10  — is it unexpectedly but plausibly interesting?
    """

    def __init__(self) -> None:
        self.alpha = 0.35
        self.beta = 0.25
        self.gamma = 0.15
        self.delta = 0.15
        self.epsilon = 0.10
        self._vectors = VectorStore()

    async def validate_many(
        self,
        character: str,
        options: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        profile = get_character(character)
        if profile is None:
            raise ValueError(f"Character '{character}' not found")

        traits = profile.get("traits", [])
        trait_desc = "; ".join(
            f"{t.get('name', '?')} ({t.get('category', '?')}): {t.get('description', '')}"
            for t in traits
        )

        options_text = "\n\n".join(
            f"Option {opt.get('label', chr(65 + i))}: \"{opt.get('voice', '')}\""
            for i, opt in enumerate(options)
        )

        # ── LLM prompt — evaluates T, B, C, P (NOT D) ──────────
        prompt = (
            f"You are an OOC (Out-of-Character) evaluation assistant for a novel.\n\n"
            f"Character: {profile['name']}\n"
            f"Backstory: {profile.get('backstory', '')}\n"
            f"Core traits: {trait_desc}\n"
            f"Motivation: {profile.get('motivation', '')}\n\n"
            f"Below are response options generated for this character.\n"
            f"For EACH option, rate the following **four** dimensions on a scale "
            f"of 0.0 to 1.0:\n\n"
            f"- T (Trait consistency): Does this option violate any core trait? "
            f"1.0 = perfectly consistent, 0.0 = violates a core trait.\n"
            f"- B (Behaviour consistency): Is this consistent with how the character "
            f"would behave based on their past? 1.0 = very consistent, 0.0 = never.\n"
            f"- C (Self-consistency): Is this option internally logical and "
            f"non-contradictory? 1.0 = perfectly self-consistent, 0.0 = contradictory.\n"
            f"- P (Surprise / novelty): How unexpected is this option? "
            f"1.0 = very surprising but still plausible, 0.0 = totally predictable.\n\n"
            f"Options to evaluate:\n{options_text}\n\n"
            f"Return ONLY valid JSON, no other text:\n"
            f'{{"scores": [\n'
            f'  {{"label": "A", "T": 0.9, "B": 0.8, "C": 0.9, "P": 0.1, "reason": "brief note"}},\n'
            f"  ...\n"
            f"]}}\n"
        )

        client = _get_client()
        resp = await client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048,
        )

        content = resp.choices[0].message.content or "{}"
        raw_scores = self._parse_scores(content, len(options))

        # ── Compute real semantic distance D from ChromaDB ──────
        real_d_values = await self._compute_semantic_distances(options, character)

        # ── Apply formula to each option ────────────────────────
        for i, score in enumerate(raw_scores):
            t = score.get("T", 0.5)
            b = score.get("B", 0.5)
            d = real_d_values[i] if i < len(real_d_values) else 0.5
            c = score.get("C", 0.5)
            p = score.get("P", 0.5)

            risk = 1.0 - (
                self.alpha * t
                + self.beta * b
                + self.gamma * (1.0 - d)
                + self.delta * c
                - self.epsilon * p
            )
            risk = max(0.0, min(1.0, risk))

            score["ooc_risk"] = round(risk, 4)
            score["details"] = {
                "T": round(t, 2), "B": round(b, 2), "D": round(d, 2),
                "C": round(c, 2), "P": round(p, 2), "D_source": "chromadb",
            }

            # Classify: violation vs surprise
            consistency = (t + b + c) / 3.0
            if risk >= 0.66 and consistency < 0.4:
                score["details"]["type"] = "violation"
            elif risk >= 0.66 and p >= 0.6 and consistency >= 0.4:
                score["details"]["type"] = "surprise"
            else:
                score["details"]["type"] = "normal"

        return raw_scores

    async def _compute_semantic_distances(
        self, options: list[dict[str, Any]], character: str
    ) -> list[float]:
        """Compute real semantic distance D for each option from ChromaDB."""
        client = _get_client()
        d_values: list[float] = []

        for opt in options:
            voice = opt.get("voice", "")
            if not voice:
                d_values.append(0.5)
                continue

            try:
                emb_resp = await client.embeddings.create(
                    model=QWEN_EMBEDDING_MODEL, input=voice)
                embedding = emb_resp.data[0].embedding
            except Exception:
                d_values.append(0.5)
                continue

            try:
                results = self._vectors.search(
                    collection="events", query_embedding=embedding,
                    top_k=10, where={"protagonist": character})
            except Exception:
                d_values.append(0.5)
                continue

            if not results:
                d_values.append(0.5)
                continue

            distances = [r["score"] for r in results if r["score"] is not None]
            if not distances:
                d_values.append(0.5)
                continue

            avg_dist = statistics.mean(distances)
            d = max(0.0, min(1.0, avg_dist / 1.5))
            d_values.append(round(d, 4))

        return d_values
```

### `backend/app/services/sleep.py` (structure overview + Phase 1 key logic)

```python
"""Sleep consolidation service — three-phase memory consolidation cycle.

Analogous to the human sleep cycle:
  Phase 1 (NREM/SWS) — Episodic → semantic migration, conflict detection
  Phase 2 (REM)      — LLM pattern extraction + vector redundancy pruning
                       + emotion tagging + arc progression + confidence adjustment
  Phase 3            — Consolidation report
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from app.config import (QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, QWEN_EMBEDDING_MODEL)
from app.database import get_character, upsert_character
from app.memory.episodic import EpisodicMemory
from app.memory.vectors import VectorStore

logger = logging.getLogger(__name__)

_CONFLICT_MAP: dict[str, set[str]] = {
    "avoid": {"brave", "courageous", "bold", "fearless", "reckless", ...},
    "submit": {"dominant", "proud", "defiant", "rebellious", ...},
    "retreat": {"persistent", "stubborn", "determined", "resolute", ...},
    "betray": {"loyal", "faithful", "devoted", "true", ...},
    "deceive": {"honest", "honorable", "forthright", "direct", ...},
    "hesitate": {"decisive", "resolute", "unwavering", "confident", ...},
    "flee": {"protective", "guardian", "defender", "fearless", ...},
}

_PIVOTAL_KEYWORDS = [
    "betray", "death", "discover", "revelation", "confrontation",
    "sacrifice", "bond", "sever", "choose", "cross",
]

_ARC_TRANSITION_THRESHOLD = 3
_PATTERN_SAMPLE_SIZE = 20
_EMOTION_SAMPLE_SIZE = 10
_PRUNE_DISTANCE_THRESHOLD = 0.05
_PRUNE_MIN_IMPORTANCE = 0.3


class ConsolidationReport:
    """Structured output of a sleep cycle."""
    def __init__(self, character: str) -> None:
        self.character = character
        self.phase1 = {"events_analyzed": 0, "conflicts_detected": [], "importance_adjustments": []}
        self.phase2 = {"patterns_extracted": [], "events_pruned": 0, "events_tagged": 0,
                       "trait_updates": [], "arc_stage_change": None}
        self.phase3 = {"summary": "", "confidence_delta": 0.0}


class SleepService:
    """Three-phase memory consolidation for a character."""

    def __init__(self, episodic: EpisodicMemory) -> None:
        self._episodic = episodic
        self._vectors = VectorStore()

    async def consolidate(self, character_name: str) -> dict[str, Any]:
        report = ConsolidationReport(character_name)
        char_data = get_character(character_name)
        if char_data is None:
            return {"status": "error", "message": f"Character '{character_name}' not found"}

        events = self._episodic.get_events(protagonist=character_name, limit=500)
        if not events:
            return {"status": "ok", "character": character_name, "message": "No events to consolidate", "report": {}}

        # Phase 1 — fact consolidation
        event_impacts = self._phase1_fact_consolidation(events, char_data, report)
        for event_id, new_imp in event_impacts:
            self._episodic.update_importance(event_id, new_imp)

        # Phase 2 — REM (hybrid)
        await self._phase2_rem(events, char_data, report)

        # Phase 3 — summary
        self._phase3_generate_report(report)

        upsert_character(char_data)

        return {"status": "ok", "character": character_name, "message": "Sleep cycle complete",
                "report": {"phase1": report.phase1, "phase2": report.phase2, "phase3": report.phase3}}

    def _phase1_fact_consolidation(self, events, char_data, report):
        """Analyze events for conflicts and importance adjustments."""
        report.phase1["events_analyzed"] = len(events)
        traits = char_data.get("traits", [])
        trait_descriptors = []
        for t in traits:
            trait_descriptors.append(t.get("name", ""))
            desc = t.get("description", "")
            if desc:
                trait_descriptors.append(desc)
        descriptor_text = " ".join(trait_descriptors).lower()

        importance_updates = []
        for ev in events:
            raw_imp = ev.get("importance", 0.5)
            zwaan = self._parse_zwaan(ev)
            intent = (zwaan.get("intent", "") or "").lower()
            cause = (zwaan.get("causality", "") or "").lower()  # ⚠️ BUG: should be "causality" not "cause"
            summary = ev.get("summary", "") or ""

            self._detect_conflicts(intent, descriptor_text, summary, raw_imp, report)
            new_imp = self._adjust_importance(raw_imp, cause, summary, report)

            if abs(new_imp - raw_imp) > 0.01:
                importance_updates.append((ev["id"], new_imp))
        return importance_updates
```

---

## API Endpoints Structure

### `backend/app/main.py`

```python
"""FastAPI application entry point."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ask, feedback, ingest, profile, sleep
from app.seed import seed_demo_character

app = FastAPI(
    title="Narrative Memory Agent",
    description="Qwen Cloud Hackathon — Track 1: MemoryAgent",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup() -> None:
    seed_demo_character()

app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(ask.router, prefix="/ask", tags=["ask"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(sleep.router, prefix="/sleep", tags=["sleep"])

@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "project": "narrative-memory-agent"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

### `backend/app/api/ask.py` — POST /ask/

- Route: `POST /ask/`
- Request body: `AskRequest` (character: str, question: str, num_options: int = 3)
- Response: `AskResponse` with merged options (text + OOC scores + details)
- Injects working memory context into generation
- Runs Circuit A (GenerationService) → Circuit B (ValidationService)
- Records user question into working memory
- **⚠️ Does NOT write ask/response to EpisodicMemory**

### `backend/app/api/ingest.py` — POST /ingest/

- Route: `POST /ingest/`
- Request body: `IngestRequest` (text: str, title: str | None)
- Response: counts of chunks/events/characters
- Calls `IngestionService.process_text()`
- Returns immediately after processing (no async background job)

### Key data flow gaps (from the architecture audit):

1. **BUG**: `sleep.py` reads `zwaan["cause"]` but `ingestion.py` stores `zwaan["causality"]` — keyword-based importance boosting never works
2. **DEAD CODE**: `memory/semantic.py` is defined but never imported or used by any consumer
3. **MISSING FEEDBACK LOOP**: User asks and feedback choices are NOT written into EpisodicMemory — sleep cycle cannot learn from user interaction patterns
4. **NO SESSION RESUMPTION**: Working memory is pure Python in-memory dict — restarting the backend loses all session context
5. **NO CROSS-SESSION USER PREFERENCES**: GenBias `preferred_profile` is per-character, not per-user — no user identity management

---

## Project Status and TODO

From `TODO.md` (June 12, 2026 — 27 days to deadline):

**Done:**
- ✅ Project skeleton (FastAPI + Next.js)
- ✅ Database design (SQLite + ChromaDB)
- ✅ Three-layer memory (working/episodic/semantic) — semantic not persisted
- ✅ IngestionService complete pipeline
- ✅ Circuit A (GenerationService)
- ✅ Circuit B (ValidationService) — 6-factor OOC scoring
- ✅ GenBias (EMA preference learning)
- ✅ Sleep Cycle (3-phase consolidation)
- ✅ Frontend views (5 tabs)
- ✅ API endpoints (5 routes)
- ✅ Basic tests (API + Sleep)
- ✅ OOC tag distinction (violation vs surprise)
- ✅ Feedback preference settings

**Remaining (W3-W6):**
- Session resumption code not written
- No user identity/preferences system
- SemanticMemory not persisted to DB
- No Dockerfile or deployment config
- No demo video or submission materials
- data.ts has Frankenstein mock data (not Caelvorn characters)
- No CI/CD

**Tech debt:**
- SemanticMemory not persisted to DB
- data.ts contains Frankenstein residual data
- No CI/CD

---

## pyproject.toml

```toml
[project]
name = "narrative-memory-agent"
version = "0.1.0"
description = "Narrative Memory Agent - Qwen Cloud Hackathon Track 1: MemoryAgent"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic>=2.0.0",
    "openai>=1.0.0",
    "chromadb>=0.5.0",
    "httpx>=0.27.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "pytest-asyncio>=0.24.0"]

[tool.ruff]
line-length = 100
target-version = "py311"
```

---

## Request for Review

**Please review this architecture end-to-end. Identify:**

**(a) The weakest links and highest-risk design decisions** — what will break first or cause the most pain under pressure with 27 days to deadline?

**(b) What's missing that the hackathon judges will look for** — given the Track 1 official requirements ("autonomously accumulates experience, remembers user preferences, and makes increasingly accurate decisions across multi-turn, cross-session interactions"), the submission requirements (public repo, deployment proof, architecture diagram, 3-min demo video), and the judging criteria (30% technical depth, 30% innovation, 25% problem value, 15% presentation).

**(c) Whether the three-layer memory model (episodic/semantic/procedural) is correctly implemented given the Qwen Cloud embedding/LLM APIs available** — specifically the gaps identified in the architecture audit: the dead SemanticMemory class, the causality field name bug in sleep.py, the missing feedback loop where user interactions don't feed into episodic memory, and whether the Zwaan five-dimension indexing is actually used effectively or just stored as opaque JSON.

**(d) What specific changes you'd make if you had to ship this by July 10 with just one more full development week** — prioritize ruthlessly. What do you cut, what do you fix, what do you add? Give specific code-level recommendations where possible.
