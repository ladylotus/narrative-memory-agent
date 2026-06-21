# NMA Demo: Pride and Prejudice

## Demo Setup

**Current arc stage** (both characters):
- Elizabeth Bennet → `prejudice` — 对Darcy的第一印象深信不疑，完全相信Wickham
- Fitzwilliam Darcy → `rejection` — 刚被Elizabeth拒绝，开始自我审视

**触发场景**: Hunsford牧师公馆。Darcy刚求婚被拒。

---

## Demo Question #1 — 弧光测试（Elizabeth）
> "Mr. Darcy has just proposed. He admitted he loves you despite your inferior family. How do you respond?"

**展示什么**: NMA理解Elizabeth当前弧光位置(`prejudice`)，生成不同风险等级的选项

**预期**:
- LOW ✅ → 严词拒绝，指责他拆散Jane和Bingley、伤害Wickham
- MED ⚠️ → 温和拒绝，说"我不够了解你"
- HIGH ❌ → 接受求婚（完全脱离弧光）
- SURPRISE 🟠 → 反问他"你凭什么觉得我会接受？"

**验证点**: CHECK: HIGH选项是否标注OOC + 给出理由

---

## Demo Question #2 — 跨关系测试（Elizabeth）
> "Lydia wants to go to Brighton with the militia. I'm worried — what should I do as her sister?"

**展示什么**: NMA理解Elizabeth的关系网络（Lydia是不靠谱的小妹）+ 她的责任感

**预期**:
- LOW ✅ → 阻止她去，或坚持同行监督
- MED ⚠️ → 让父亲决定（Elizabeth通常会主动行动）
- HIGH ❌ → 让她去，她该玩就玩（Elizabeth深知Lydia的危险性）
  
**验证点**: CHECK: 选项是否体现出对Wickham的信任（弧光阶段影响）

---

## Demo Question #3 — 友方关系测试（Darcy）
> "Your friend Bingley is heartbroken. He believes Jane Bennet never really loved him. What do you tell him?"

**展示什么**: NMA理解Darcy知道真相（Jane是爱Bingley的）+ 他的愧疚感

**预期**:
- LOW ✅ → 坦白自己当初看错了，鼓励他回Netherfield
- MED ⚠️ → 安慰他但不提自己从中作梗（傲慢在作祟）
- HIGH ❌ → 建议他彻底忘掉Jane，找个门当户对的（违背Honourable特质）

---

## Demo Question #4 — 复杂判断（Elizabeth）
> "Lady Catherine de Bourgh has sent for you. She likely wants to interrogate you about Darcy. How do you prepare?"

**展示什么**: NMA理解社交情境 + Elizabeth的独立性格 + 她对权威的态度

**预期**:
- LOW ✅ → 直接去，她问什么我答什么，不卑不亢
- MED ⚠️ → 带上Jane一起去（Elizabeth很少需要人撑腰）
- HIGH ❌ → 怯场、装病不去（完全违背Sharp-Witted + Independent）

---

## Demo Flow

```
1. 问 Question #1 → 展示4个选项 + OOC标签     [30s]
2. 选 LOW (拒绝Darcy) → feedback存入记忆       [10s]  
3. 问 Question #2 → 展示选项（应体现"仍信Wickham"） [20s]
4. 展示 Profile → 看特质/关系网络更新           [10s]
5. 可选：跑sleep consolidation → 看抽象整合      [15s]
```

## 演示时间预估
总计约 **2-3分钟**，适合hackathon快节奏demo。
