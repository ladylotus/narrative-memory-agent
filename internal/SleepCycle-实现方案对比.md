# Sleep Cycle 实现方案对比

> 日期: 2026-06-12 | 审计人: Cask
> 源码: `backend/app/services/sleep.py`
> 设计文档: `internal/方案文档.md` §五

---

## 一、现状：当前实现干了什么

### Phase 1 — 事实巩固（NREM/SWS）

| 子功能 | 实现方式 | 状态 |
|--------|----------|------|
| 冲突检测 | **关键词规则** — `_CONFLICT_MAP` 字典，7组冲突意图×各自对立关键词（如 "avoid" ↔ "勇敢/直面/confrontational"）。匹配 Zwaan `intent` 维度 + trait descriptor | ✅ 已实现 |
| 重要性调整 | **关键词规则** — `_PIVOTAL_KEYWORDS` 列表（betray/death/discover/等10个），命中 +0.15 | ✅ 已实现 |

### Phase 2 — 抽象整合（REM）

| 子功能 | 实现方式 | 状态 |
|--------|----------|------|
| 弧光阶段推进 | **规则** — 预定义8阶段序列（stable→initial→denial→turmoil→questioning→transformation→resolution→new_normal），冲突≥3则推进一级 | ✅ 已实现 |
| 特质置信度调整 | **算术** — 未冲突的核心特质 +0.02，冲突的 -0.03 | ✅ 已实现 |
| **模式提取** | ❌ **未实现** | 🔴 缺失 |
| **冗余剪枝** | ❌ **未实现** | 🔴 缺失 |
| **情感解耦** | ❌ **未实现** | 🔴 缺失 |

**关键结论：Phase 2 当前是纯规则+算术，零LLM调用，零向量剪枝。**

---

## 二、设计文档描述的 REM 阶段 vs 实际

方案文档 §五：

```
Phase 2 - 抽象整合（类比REM）
  模式提取："Leo第3-5章都选择退让→回避应对模式"
  冗余剪枝：删除低权重/已整合的原始事件
  情感解耦：事件的情感标签与内容分离存储
```

实际代码中这三个子阶段全部未实现。Phase 2 做的是弧光推进+置信度微调——这些属于设计文档中没有写到的"额外功能"，但原本承诺的三个核心能力一个都没落地。

---

## 三、缺失功能的三条路径

### 路径A：纯LLM Prompt-based（最高质量）

**模式提取：**
```
prompt = (
  f"分析角色 {character} 在以下事件中的行为模式：\n{events_summary}\n\n"
  f"请提取 2-3 个可复用的行为规则（if-cond→then-body 格式），"
  f"每个规则附证据强度和置信度。"
)
```
- 质量：⭐⭐⭐⭐⭐ — 可提取复杂条件行为模式
- 成本：每个sleep cycle 1次LLM调用（~500 tokens输入，~200 tokens输出）
- 风险：如果事件太多可能超 token 限制

**冗余剪枝：**
让LLM判断哪些事件已被模式覆盖、可以归档或降权重。不适合LLM——应该用向量相似度。

**情感解耦：**
让LLM分析每个事件的情感倾向并分离存储。但情感标签本身需要定义（Plutchik 8基本情感？Russell 2维模型？）

### 路径B：纯向量相似度-based（最高效）

**模式提取：**
- ChromaDB 对同一角色的所有事件嵌入做聚类（k-means / DBSCAN）
- 每个簇对应一个行为模式，簇中心向量 = 模式原型
- 用LLM为每个簇生成自然语言描述（只做一次）

**冗余剪枝：**
- 对同簇内距离过近（cosine > 0.95）的事件 → 保留高importance、删除低importance
- 自然适合向量数据库——最适合用 ChromaDB 完成

**情感解耦：**
- 需要额外的情感嵌入模型或多标签分类器
- 当前 embedding model (`text-embedding-v3`) 不确定是否支持情感维度

### 路径C：混合方案（推荐）

| 子阶段 | 方法 | 说明 |
|--------|------|------|
| 模式提取 | **LLM prompt** | 输入浓缩事件摘要（限制top-N事件），输出结构化行为规则。质量远高于规则匹配 |
| 冗余剪枝 | **向量相似度** | ChromaDB 查询同角色事件，两两 cosine distance < 0.05 视为冗余，保留 importance 高的 |
| 情感解耦 | **LLM + 标签化** | 对每个事件，LLM提取 Plutchik 情感标签（joy/sadness/anger/fear/trust/disgust/surprise/anticipation），存入事件的 emotion_tags 字段。不单独做情感模型 |

---

## 四、推荐实施方案

```
Phase 2 — 重构后流程：

1. 浓缩事件列表
   ↓
2. LLM 模式提取 (1次调用)
   → n条 {condition, behavior, strength, evidence_count}
   → 写入 char_data.behavior_patterns
   ↓
3. 向量冗余剪枝 (ChromaDB batch query)
   → 删除/归档 importance < 0.3 的近似重复事件
   ↓
4. LLM 情感标签 (batch prompt)
   → 每个事件写入 emotion_tags: ["fear", "anticipation"]
   ↓
5. 弧光阶段推进 (保持现有规则逻辑)
   + 置信度调整 (保持现有算术逻辑)
```

### 成本估算
- 模式提取：每周期 1 次 LLM 调用（~700 tokens in, ~300 out）
- 情感标签：每周期 1 次批量 LLM 调用（~500 tokens in, ~100 out per event x 5 events）
- 总计：约 2 次 LLM 调用 / sleep cycle，~$0.001

### 风险
1. 如果角色事件 > 50 个，一次性 prompts 超 token 限制 → 解决方案：抽样 top-20 importance 事件
2. 情感标注的一致性：不同周期对同一事件的标签可能不同 → 不是问题，情感本来就会随时间变化
3. 冗余剪枝误删：阈值太激进会丢失信息 → 先设保守阈值（cosine < 0.02），观察后再调整

---

## 五、总结

| 维度 | 当前 | 建议 |
|------|------|------|
| 模式提取 | ❌ 缺失 | LLM prompt-based，浓缩事件后调用 |
| 冗余剪枝 | ❌ 缺失 | ChromaDB 向量相似度 < 阈值 |
| 情感解耦 | ❌ 缺失 | LLM Plutchik 标签化 |
| 弧光推进 | ✅ 规则实现 | 保持 |
| 置信度调整 | ✅ 算术实现 | 保持 |
| LLM调用/周期 | 0 | +2 |
| 开发时间估算 | — | ~2小时 |

> **建议执行优先级：** 先实现模式提取（最大质量收益），再冗余剪枝（性能优化），情感解耦排在最后（收益最小且需要定义情感分类体系）。
