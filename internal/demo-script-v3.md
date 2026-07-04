# NMA 演示文档 v3

> **生产地址：** `http://47.84.196.253:3000`
> **角色阵容：** Elizabeth Bennet（傲慢与偏见）+ Caelan Ashmark（Caelvorn Series）
> **时长：** ~3分钟
>
> **修订说明（v2→v3）：**
> - 元认知 v2 去掉了例句模板，after-sleep 的回答不再有固定句式
> - before/after 调整为演示的高潮而非铺垫
> - 操作指南（先）和视频脚本（后）分离

---

# 一、操作指南

> 录视频前逐项确认，录制时按步骤操作。
> **核心原则：** 不需要念词，按步骤做就好，画面配合后期口播。

## 录制前 Checklist

- [ ] 浏览器打开 `http://47.84.196.253:3000`，确认侧栏有 4 个角色
- [ ] **预跑一次 Sleep**（避免录制时第一次触发等待太久）：
  1. 点击侧栏 **Elizabeth Bennet**
  2. 切到 **💤 Sleep Log** tab
  3. 点击 **🌙 Run Sleep Consolidation**，等待完成
  4. 确认三段报告展开
- [ ] 确认麦克风正常工作
- [ ] 屏幕分辨率 1920×1080
- [ ] 浏览器全屏 · 暗色主题
- [ ] **清空 Elizabeth 的 last_sleep_report**（确保现场 before/after 对比干净）：
  - 后端执行 SQL：`UPDATE characters SET last_sleep_report = NULL WHERE name = 'Elizabeth Bennet'`
  - 或直接在服务器上 `docker exec <backend> python -c "from app.database import get_character, upsert_character; c = get_character('Elizabeth Bennet'); c['last_sleep_report'] = ''; upsert_character(c)"`

---

## Step 1 · Opening（~15s）

**画面操作：** 无操作。页面已打开。

**后期配：** 黑底白字渐入 → fade 到页面

---

## Step 2 · 选角色 + Profile（~20s）

**画面操作：**
1. 侧栏 **Caelan Ashmark**（🐺）已选中
2. 鼠标悬停在 Caelan 头像上（如果有 hover 效果）
3. 点击上方 **🧠 Profile** tab
4. 鼠标慢慢划过 Traits 列表（Order-Driven 100%、Blind Spot 90% 等）
5. 鼠标划过 Relationship Network 区域（Mira, Edran, Lena, Corvan）
6. 切回 **💬 Chat** tab

**注意：** 不要点太快，让观众有时间看到 7 个特质和关系网的内容。

---

## Step 3 · Elizabeth 第一问（~30s）

**画面操作：**
1. 侧栏点击 **Elizabeth Bennet**（📖）
2. 在输入框打字：
   ```
   Mr. Darcy just proposed. What will you tell him?
   ```
   （打字时镜头可以给特写——节奏上留一秒）
3. 点击 **What would you do?**
4. **等待** 4 张选项卡片加载出来（~5-10s，服务器响应较慢）
5. 鼠标**依次划过**每张卡片，停一秒（让观众看到 OOC 标签）：
   - 选项 A: `✅ Fitting · XX%`
   - 选项 B: `✅ Fitting · XX%` 或 `🟠 Surprising · XX%`
   - 选项 C: `⚠️ Off-track · XX%`
   - 选项 D: `❌ OOC · XX%` 或 `🚫 OOC Violation · XX%`
6. 点击**选项 B**（Fitting 方向的选项——实际选 OOC 最低的那个）

**特别注意：** OOC 标签有 `✅ Fitting` / `🟠 Surprising` / `⚠️ Off-track` / `❌ OOC` / `🚫 OOC Violation`。口播要注意不要说成 Low Risk/High Risk，直接念标签名。

---

## Step 4 · 反馈 + GenBias（~15s）

**画面操作：**
1. 在 Feedback 弹窗中，点击 `□ It's what they'd do`
2. 点击 **💾 Save to Memory**
3. 等待 Toast 出现：`✅ Saved to memory · Your preference will guide future generations`
4. 稍等一秒让观众看到

---

## Step 5 · 切 Caelan 跨小说（~20s）

**画面操作：**
1. 侧栏点击 **Caelan Ashmark**（🐺）
2. 在输入框打字：
   ```
   At the banquet, your Bond triggered to an Omega kitchen worker. What went through your mind?
   ```
3. 点击 **What would you do?**
4. 选项加载后，鼠标划过 2-3 张卡片（展示与 Elizabeth 完全不同的风格）
5. **不需要选选项**——展示即可

---

## Step 6 · Sleep 巩固（~20s）

**画面操作：**
1. 侧栏切回 **Elizabeth Bennet**
2. 点击 **💤 Sleep Log** tab
3. 点击 **🌙 Run Again**（预跑后按钮已变为 Run Again）
4. **等待** 三段报告展开（~5-15s，后台正在分析）：
   - `💤 Fact Consolidation` — 数据/冲突检测
   - `🧩 Abstraction & Integration` — 模式提取
   - `🔍 Self-Audit Report` — 总结摘要
5. 鼠标划过三段的摘要内容——让观众看清每段在做什么
6. 切回 **💬 Chat** tab

---

## Step 7 · Elizabeth 再问（~25s）

**画面操作：**
1. Elizabeth 仍在 Chat tab
2. 输入框打字——**同一问题**：
   ```
   Mr. Darcy just proposed. What will you tell him?
   ```
3. 点击 **What would you do?**
4. 选项加载后，鼠标划过卡片
5. **此处后期口播重点解释**——同一个人、同一问题、睡前后的回答差异
6. 自然收尾（不需要再选选项了）

---

## Step 8 · 刷新页面（~10s）

**画面操作：**
1. 按下 **F5** 刷新页面
2. 页面重新加载
3. 点击 **Elizabeth Bennet**
4. 让摄像头停在横幅上 2 秒：
   `🔁 Welcome back — X previous exchanges remembered.`
   `Last question: "Mr. Darcy just proposed..."`

---

## Step 9 · Closing（~10s）

**画面操作：** 无操作。页面不动。

**后期配：** GitHub repo URL fade in → Tagline

---

# 二、视频脚本

> 格式：`[时间] 音频 | 画面`

---

## 🎬 Opening（15s）

```
[0:00-0:15]
音频: "Fictional characters should remember. They should grow.
       They should feel real — not reset every time you reload the page."
画面: 黑底白字渐入 "Fictional characters should remember."
      → 渐入 "They should grow."
      → 渐入 "They should feel real."
      → 淡出 → fade 到页面
```

---

## Step 2 · 选角色 + Profile（20s）

```
[0:15-0:35]
音频: "NMA doesn't just support one novel. We preloaded two — Jane Austen's
       Pride and Prejudice and an original work from our own Caelvorn Series.
       Four characters, each with their own backstory, traits, and arc stage.

       Take Caelan Ashmark — the system has extracted seven core traits from
       his narrative, each with a confidence score. A relationship network.
       This is what the agent knows about him, and it evolves with every
       conversation and every sleep consolidation."

画面: [0:15] 侧栏 Caelan 选中
      [0:20] 切到 Profile tab → 慢慢划过 7 个 traits
      [0:27] 划过 Relationship Network（Mira, Edran, Lena, Corvan）
      [0:32] 切回 Chat tab
```

---

## Step 3 · Elizabeth 第一问（30s）

```
[0:35-1:05]
音频: "Now let's talk to Elizabeth Bennet. You ask a question, and NMA
       generates four distinct responses — each scored for how in-character
       it is. '✅ Fitting' means it matches perfectly. '❌ OOC' means it
       would break canon.

       The core innovation: Dual Circuit Architecture. Circuit A generates
       creative options. Circuit B validates each one against five OOC
       factors — trait consistency, behavioral patterns, semantic distance,
       self-consistency, and surprisal."

画面: [0:35] 侧栏点 Elizabeth
      [0:40] 打字特写: Mr. Darcy just proposed. What will you tell him?
      [0:46] 点 What would you do?
      [0:48] 加载动画
      [0:53] 依次划过 4 张选项卡:
               ✅ Fitting · 10%
               ✅ Fitting · 25% 或 🟠 Surprising
               ⚠️ Off-track · 45%
               ❌ OOC · 88% 或 🚫 OOC Violation
      [1:00] 点击选项 B（Fitting）
```

---

## Step 4 · 反馈 + GenBias（15s）

```
[1:05-1:20]
音频: "That mark isn't just a like button. NMA asks why you chose this
       — was it because this is what the character would do? That choice
       feeds into GenBias, an EMA learning loop that adapts future
       generations toward your storytelling preferences over time."

画面: [1:05] 点击 □ It's what they'd do
      [1:10] 点击 💾 Save to Memory
      [1:13] Toast: ✅ Saved to memory
```

---

## Step 5 · 切 Caelan 跨小说（20s）

```
[1:20-1:40]
音频: "Now watch what happens when we switch to a completely different
       novel — Caelan Ashmark from the Caelvorn Series. Qwen has never
       read this book. Everything it knows about him comes from the
       database: his backstory, his traits, his motivation, his arc stage.

       The prompt architecture is fully generic. Any character, any novel."

画面: [1:20] 侧栏点 Caelan
      [1:25] 打字: At the banquet, your Bond triggered to an Omega kitchen worker...
      [1:30] 点 What would you do?
      [1:33] 加载完成 → 鼠标划过 2-3 张卡
      [1:38] 展示选项 A 的内容片段（风格明显不同）
```

---

## Step 6 · Sleep 巩固（20s）

```
[1:40-2:00]
音频: "Now let's run a Sleep Consolidation cycle. Inspired by human
       memory consolidation — NREM extracts facts and detects conflicts,
       REM abstracts behavioral patterns and prunes redundancy, and
       the Self-Audit evaluates confidence.

       This is how NMA turns scattered interactions into stable
       character growth."

画面: [1:40] 侧栏点 Elizabeth
      [1:42] 切到 💤 Sleep Log tab
      [1:45] 点击 🌙 Run Again
      [1:48] 加载中...
      [1:52] 三段报告展开:
              💤 Fact Consolidation
              🧩 Abstraction & Integration
              🔍 Self-Audit Report
      [1:57] 鼠标划过三段内容
      [2:00] 切回 💬 Chat tab
```

---

## Step 7 · Elizabeth 再问（25s）

```
[2:00-2:25]
音频: "Now here's where it gets interesting. Same character. Same question.
       But after sleep — after the system has consolidated her events,
       extracted patterns, and updated her cognitive profile — listen to
       how she answers.

       She isn't given a template. She isn't told 'show self-awareness.'
       The consolidation data is simply present in her context, and she
       naturally integrates it into her response. That's real metacognition."

画面: [2:00] Elizabeth 在 Chat tab
      [2:05] 打字: Mr. Darcy just proposed. What will you tell him?
      [2:10] 点 What would you do?
      [2:15] 选项加载 → 依次划过
      [2:20] 停在某个选项上（展示内容——与 Step 3 的回答有可感知差异）
```

---

## Step 8 · 刷新页面（10s）

```
[2:25-2:35]
音频: "And close the browser. Come back tomorrow — the character
       remembers who you are and where you left off."

画面: [2:25] F5 刷新
      [2:28] 页面重新加载
      [2:30] 点 Elizabeth
      [2:32] 横幅特写:
              🔁 Welcome back — X exchanges remembered.
              "Mr. Darcy just proposed..."
```

---

## 🎬 Closing（10s）

```
[2:35-2:45]
音频: "NMA is open source. Try it with your own characters.
       Pull requests welcome.
       
       Where characters remember who they are —
       and who you want them to become."

画面: [2:35] GitHub repo URL fade in
      [2:40] Tagline + Logo
      [2:45] Fade to black
```

---

## 附录：分镜速查表

| 步骤 | 时间 | 操作 | 口播内容 |
|------|------|------|---------|
| Opening | 0:00-0:15 | — | 角色不应该每次重置 |
| Profile | 0:15-0:35 | Caelan → Profile tab → 展示 traits | 双小说支持，认知画像 |
| Elizabeth Q1 | 0:35-1:05 | 选 Elizabeth → 打字 → 展示 4 选项 → 选一个 | Dual Circuit, OOC 评分 |
| Feedback | 1:05-1:20 | 反馈标记 → Save to Memory | GenBias 学习闭环 |
| Caelan | 1:20-1:40 | 切 Caelan → 打字 → 展示选项 | 通用架构，任何小说 |
| Sleep | 1:40-2:00 | 切回 Elizabeth → Sleep Log → Run | 三段巩固流程 |
| Elizabeth Q2 | 2:00-2:25 | 同一问题 → 展示 different 回答 | 元认知自然流露 |
| Refresh | 2:25-2:35 | F5 → 点 Elizabeth → 横幅 | 跨会话记忆 |
| Closing | 2:35-2:45 | — | GitHub + 口号 |

> **总时长：~2:45**（控制在 3:00 以内）
> **备选压缩方案：** 如果超时，可缩短 Step 5（Caelan 跨小说）或 Step 4（Feedback）各 5 秒。
