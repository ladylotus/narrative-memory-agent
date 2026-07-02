# NMA 冲刺方案：记忆衰减 + 双角色对话

**目标：** 补齐"遗忘"短板（Track 1 核心要求）+ 拉满演示效果与技术创新评分  
**时机：** W5（6/29 - 7/5），截稿前最后一轮大迭代  
**总估时：** 5-6 天（两人分工则 3-4 天）

---

## 方向 A：记忆衰减系统

### 现状问题

events 表的 `importance` **只升不降**：SleepCycle 只会把关键事件的重要性提上去（+0.15），但从不衰减。这导致：
- 大量旧事件和当前决策无关，但仍占据 ChromaDB 检索空间
- /ask 生成的 prompt 里塞了太多不相关信息，干扰 OOC 评分质量
- "及时遗忘"这个 Track 1 要求形同虚设

### 方案设计

#### A-1. 衰减模型（`backend/app/services/decay.py`，新文件）

**双因子衰减公式：**
```
decay_factor = exp(-λ_time × Δt - λ_access × access_count)
recall_score = importance × decay_factor
```

- `Δt`：该事件距离当前的时间（按 chapter 差值或时间戳）
- `access_count`：该事件被检索/用于生成的次数
- `λ_time = 0.05`，`λ_access = 0.02`（可配置）
- 每次 /ask 调用时会 increment 被检索到的事件的 `access_count`

**三个层级：**

| recall_score 区间 | 分类 | 行为 |
|------------------|------|------|
| ≥ 0.3 | Active | 正常进入上下文 |
| 0.1 - 0.3 | Fading | 摘要压缩后进入上下文 |
| < 0.1 | Archived | 从活跃查询中排除，保留在归档表以供 SleepCycle 参考 |

#### A-2. 数据库变更（`backend/app/database.py`）

**events 表新增列：**
- `last_accessed_at TEXT` — 最后一次被检索的时间戳
- `access_count INTEGER DEFAULT 0` — 累计检索次数

**新增 archive 表：**
```sql
CREATE TABLE IF NOT EXISTS event_archive (
    id          TEXT PRIMARY KEY,
    original_id TEXT NOT NULL,          -- 关联原事件 ID
    character   TEXT NOT NULL,
    summary     TEXT NOT NULL,          -- 压缩后的摘要（更短）
    full_text   TEXT,                   -- 原完整摘要（备查）
    importance  REAL NOT NULL,
    decayed_at  TEXT DEFAULT (datetime('now')),
    zwaan_dims  TEXT                    -- JSON，保留维度索引
);
```

当事件进入 archive 状态时：
1. 压缩摘要（取原文前 80 字 + 关键 zwaan 维度）
2. 从 ChromaDB 删除该事件的向量
3. 写入 archive 表
4. 将 `importance` 设为 0.05（标记为 archive，不再参与常规检索）

#### A-3. /ask 端点改造（`backend/app/api/ask.py`）

在 `_get_wm()` 或生成 prompt 之前，插入一步：

1. 遍历该角色的 active 事件（importance > 0.05）
2. 计算每个事件的 `recall_score`
3. 按 recall_score 排序取 top-K
4. Fading 区间的事件用压缩摘要（`summary[:100]`）替代完整摘要
5. 每次检索到的事件递增 `access_count` + 更新 `last_accessed_at`

#### A-4. SleepCycle 集成（`backend/app/services/sleep.py`）

**Phase 1 增加衰减步骤：**
- 遍历该角色所有 active 事件，计算 decay
- recall_score < 0.1 的事件 → archive
- 更新报告中新增 `events_archived: N`

**Phase 2 REM 模式提取时包含 archive 事件：**
- archive 表中的事件也参与 LLM 模式提取（作为长期行为参照）
- 但它们的权重（importance × decay_factor）较低，不会主导提取结果

#### A-5. 受影响文件清单

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `backend/app/services/decay.py` | 🆕 新建 | 衰减模型 + recall_score 计算 |
| `backend/app/database.py` | 🔴 修改 | events 表加列 + archive 表建表 + archive CRUD |
| `backend/app/memory/episodic.py` | 🔴 修改 | add_event/get_events 支持新字段 |
| `backend/app/api/ask.py` | 🔴 修改 | 插入 recall 过滤逻辑 |
| `backend/app/services/sleep.py` | 🔴 修改 | Phase 1 加入衰减检查，REM 包括 archive 数据 |
| `backend/tests/test_decay.py` | 🆕 新建 | 衰减曲线测试 + 归档边界测试 |

### 测试要点

- 初始 importance=0.3 的事件经过 N 轮 /ask 调用后 recall_score 降到 0.1 以下
- 归档事件不再出现在 /ask 的上下文中
- SleepCycle 归档后可正确压缩摘要并写入 archive 表
- 高频访问的事件 decay_factor 衰减更快（access_count 因子起作用）

---

## 方向 C：双角色对话

### 现状

现在只能用户 ↔ 单个角色对话。为了实现"两个角色自己说话"的能力，需要一个新端点，它同时加载两个角色的 GenBias profile，各自生成响应，再编排成交替形式。

### 方案设计

#### C-1. 后端 /dialog 端点（`backend/app/api/dialog.py`，新文件）

```
POST /dialog
Body: {
  "character_a": "Elizabeth Bennet",
  "character_b": "Fitzwilliam Darcy",
  "scene": "The morning after the Netherfield ball, Elizabeth encounters Darcy alone in the garden.",
  "turns": 3
}
Response: {
  "a_id": "elizabeth",
  "b_id": "darcy",
  "lines": [
    { "speaker": "b", "text": "...", "risk": {...}, "ooc_scores": {...} },
    { "speaker": "a", "text": "...", "risk": {...}, "ooc_scores": {...} },
    ...
  ]
}
```

**核心逻辑（`backend/app/services/dialog.py`，新文件）：**

```python
class DialogService:
    def __init__(self):
        self.gen = GenerationService()
        self.val = ValidationService()

    async def generate_dialog(
        self, char_a: str, char_b: str,
        scene: str, turns: int
    ) -> DialogResponse:
```

1. 加载两个角色的 profile（含各自的 GenBias preferred_profile）
2. 构建各自的 working memory（含 scene 描述 + 对话历史）
3. 交替调用 GenerationService（用各自的 bias）+ ValidationService
4. 每个角色的 ooc 校验用对方的最新发言作为上下文
5. 返回对话线数组

#### C-2. 对话约束

每个角色生成的 prompt 必须包含：
- 当前场景描述
- 对方上一句发言
- 自己的性格 + GenBias 偏向
- 禁止观念类提示词（不要写"你觉得…"）

**prompt 模板（以 Elizabeth 为例）：**
```
You are Elizabeth Bennet. 
Traits: {traits}
Your learned preference: {preferred_profile bias prompt}

Scene: {scene}
Darcy just said: "{darcy_last_line}"

What do you say next? Respond in Elizabeth's authentic voice.
Generate 2-3 options with different takes.
```

#### C-3. 前端展示

**新增视图"Dialog"tab**（`frontend/src/components/DialogView.tsx`）

布局：

```
┌─────────────────────────────────────┐
│  🎭 角色对话                           │
│  ───────────────────────────────────  │
│  [Elizabeth Bennet]  ↔  [Darcy]       │
│  [场景输入框]                          │
│  [回合数: 3 ▼] [开始对话]               │
│  ───────────────────────────────────  │
│                                      │
│  🟣 Darcy: 线 1 [risk badge]          │
│  🟢 Elizabeth: 线 2 [risk badge]      │
│  🟣 Darcy: 线 3 [risk badge]          │
│  🟢 Elizabeth: 线 4 [risk badge]      │
│  ...                                 │
│                                      │
│  每行可点击 → 弹出 mark 反馈            │
│  (共享 GenBias，标记后跟单角色生效)       │
└─────────────────────────────────────┘
```

**受影响的文件：**

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `backend/app/api/dialog.py` | 🆕 新建 | POST /dialog 端点 |
| `backend/app/services/dialog.py` | 🆕 新建 | DialogService，交替生成 |
| `backend/app/main.py` | 🔴 修改 | 注册 router |
| `backend/app/models/__init__.py` | 🔴 修改 | DialogRequest / DialogResponse / DialogLine |
| `backend/tests/test_dialog.py` | 🆕 新建 | 对话生成 + OOC + 边界测试 |
| `frontend/src/components/DialogView.tsx` | 🆕 新建 | 对话视图组件 |
| `frontend/src/app/page.tsx` | 🔴 修改 | 新增 tab 和路由 |
| `frontend/src/lib/types.ts` | 🔴 修改 | 新增 Dialog 类型 |
| `frontend/src/lib/api.ts` | 🔴 修改 | 新增 dialog API 调用 |
| `frontend/src/app/globals.css` | 🔴 修改 | 对话视图样式 |

---

## 并行工作流

你和我就算只有 5 天（6/29 → 7/3），分两条线：

| 天 | 你在做什么 | 我在这里做什么 |
|---|-----------|--------------|
| **Day 1** | 录 Alibaba Cloud 部署证明视频 + 注册 YouTube | 写 decay.py + events 表迁移 |
| **Day 2** | 录主 Demo 视频（按 user-test-flow.md） | 写 dialog.py + /dialog 端点 |
| **Day 3** | 视频剪辑 + 补充素材 | 写 DialogView.tsx + 前端对接 |
| **Day 4** | Devpost 填表 + 上传材料 | SleepCycle 集成 + 测试覆盖 |
| **Day 5** | 最终检查 + 提交 | 剩余测试 + 最终联调 |

## 评分对照（提交后）

| 标准 | 权重 | 打中什么 |
|------|:----:|---------|
| **Technical Depth & Engineering** | 30% | 衰减公式 + 双角色交替生成 + 各自的 GenBias 独立生效 |
| **Innovation & AI Creativity** | 30% | 双角色对话是 Judge 看得懂的 "wow moment"，衰减机制对标人类遗忘曲线 |
| **Problem Value & Impact** | 25% | 衰减解决"记忆越多越不准"的实际痛点；双角色对话展示协作推理能力 |
| **Presentation & Documentation** | 15% | 3 分钟视频 + 架构图 + 代码文件证明 |

## 风险和权衡

| 风险 | 概率 | 缓解 |
|------|:----:|------|
| 双角色配置 LLM 输出不稳定 | 🟡 中 | temperature=0.3 控制 + 每步 OOC 校验兜底，超标就重试 |
| 衰减参数（λ）需要调优 | 🟢 低 | 默认值从 λ_time=0.05 起步，测试跑 decay_curve 验证 |
| 前端 DialogView 开发量偏大 | 🟡 中 | 复用现有 ConversationView 样式和组件模式，去掉 feedback bar + 替换为选线标记 |
| 时间不够两道都上 | 🟡 中 | 优先方向 A（衰减→硬需求），C 是可选的冲击项 |
