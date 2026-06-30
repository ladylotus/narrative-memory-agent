# NMA Demo 视频脚本 v2

> **角色阵容：** Elizabeth Bennet（傲慢与偏见）+ Lena（Seen/Caelvorn Series）
> **时长：** ~3分钟 · **风格：** 口播 + 屏幕录制
> **核心卖点：** 双小说展示 · 多轮记忆 · 原创角色支持

---

## 🎬 Opening（15s）

| 音频 | 画面 |
|------|------|
| "Fictional characters should remember. They should grow. They should feel real — not reset every time you reload the page." | 黑底白字渐入 → fade 到页面加载 |

---

## Step 1 · 选角色（15s）

| 操作 | 画面 |
|------|------|
| 打开 `http://localhost:3000` | 暗色主题加载，**4个角色**出现在侧栏 |
| 鼠标悬停在 **Elizabeth Bennet** 头像上 | 右区显示场景卡片：`Arc stage: prejudice` |
| 再悬停到 **Lena** 头像上 | 右区更新为 Lena 的场景：`Arc stage: awakening` |

**口播：** "NMA doesn't just support one novel. We preloaded two — Jane Austen's *Pride and Prejudice*, and an original work, *Seen*, from our own Caelvorn Series. Four characters, each with their own backstory, traits, and arc stage."

---

## Step 2 · 第一轮对话：Elizabeth（40s）

| 操作 | 画面 |
|------|------|
| 选中 **Elizabeth**，在输入框打字：*"Mr. Darcy just proposed. What will you tell him?"* | 打字特写 |
| 回车 | 加载动画（4个轮播思考提示）→ 弹出 **4 张选项卡片** |
| 鼠标依次划过每张卡 | 展示风险标签：🟢 Low Risk · 10% / 🟢 Low Risk · 30% / 🟢 Low Risk · 20% / 🔴 High Risk · 90% |
| 点击第 **2 张卡**（A Quiet Reckoning） | 卡牌选中高亮，角色气泡弹出 |

**口播：** "You ask a question, and NMA generates four distinct responses — each scored for how in-character it is. Low Risk means it fits the character perfectly; High Risk means it would break canon. The core innovation: **Dual Circuit Architecture**. Circuit A generates creative options, Circuit B validates them against six OOC factors."

**画面停留：** 选中后弹出的角色气泡内容特写：
> *"You ask for my hand, yet your manner suggests you are conferring a favour rather than seeking a partnership… I will not bind myself to a man who must conquer his pride to tolerate me."*

---

## Step 3 · 反馈 + 追问（30s）

| 操作 | 画面 |
|------|------|
| 点击 **🎯 It's what they'd do** 标记 | 标记选中 |
| 点击 **💾 Save to Memory** | Toast：✅ Saved to memory |

**口播：** "That mark isn't just a like button. It feeds into **GenBias** — an EMA learning loop that adapts future generations to your storytelling preferences."

| 操作 | 画面 |
|------|------|
| **追问** 输入框打字：*"But now that you've had time — is there any part of you that wonders if you were wrong about him?"* | 打字特写 |
| 回车 | 加载 → 再弹出 **4 张选项卡片** |

**口播：** "And the character **remembers**. WorkingMemory stores every exchange within the session. The follow-up options reference what happened before — no context reset."

**画面停留：** 展示 Round 2 的选项，鼠标划过选项 C *Speed as Clarity*：
> *"You ask if I judged him quickly, as though time is the only measure of truth. I have watched him long enough… My certainty is not a flaw. It is my preservation."*

---

## Step 4 · 切换原创角色：Lena（30s）

| 操作 | 画面 |
|------|------|
| 侧栏点击 **Lena** | 角色切换，场景卡片更新 |
| 输入：*"Lena, the Alpha looked at you during the banquet. What went through your mind?"* | 打字 |
| 回车 | 加载 → **4 张选项卡片**，风格明显不同 |

**口播：** "Now watch what happens when we switch to an original character — Lena, an Omega from the Caelvorn Series. Qwen has never read this book. Everything it knows comes from the backstory and traits we defined in the database."

**画面停留：** 展示 Lena 选项的特写（展示选项 A 的部分内容）：
> *"I spent twenty-two years learning how to disappear. But three nights ago, the heavy oak doors swung open and he walked into the kitchen… Being invisible was safe. Being seen by him… I think that's going to get me killed."*

**口播：** "Lena has never been in any training data. Yet the system understands her voice — the kitchen imagery, the terror of being noticed, the grief for Maren. That's because NMA's prompt architecture is **fully generic**: backstory, traits, motivation, arc stage — all read from the database for any character."

---

## Step 5 · 角色 Profile（15s）

| 操作 | 画面 |
|------|------|
| 侧栏切换到 **Profile** tab | 显示 Elizabeth 的五维特质条 + 行为模式 |
| 点击下拉查看 **Lena** 的 Profile | Lena 的 traits: Calm Under Pressure, Invisible by Design, Grief-Bound to Maren… |

**口播：** "Every character has a living cognitive profile — traits, behavior patterns, relationships. All evolving with every conversation and every feedback mark."

---

## Step 6 · Sleep 巩固（15s）

| 操作 | 画面 |
|------|------|
| 侧栏切换到 **Sleep** tab | 显示 Sleep 说明页 |
| 点击 **Run Consolidation** | 三段报告展开：NREM / REM / Self-Audit |

**口播：** "Inspired by human memory consolidation. NREM extracts facts from your conversations. REM abstracts behavioral patterns. Self-Audit evaluates confidence. This is how NMA turns scattered interactions into stable character growth."

---

## Step 7 · 跨会话记忆（10s）

| 操作 | 画面 |
|------|------|
| 刷新页面 | 页面重新加载 |
| 选中 **Elizabeth** | 顶部出现横幅：🔄 Resumed session — X turns remembered |

**口播：** "Cross-session memory. Come back tomorrow — the character remembers who you are and where you left off."

---

## 🎬 Closing（10s）

| 音频 | 画面 |
|------|------|
| "NMA is open source. Try it with your own characters. Pull requests welcome." | GitHub repo URL |
| "Where characters remember who they are — and who you want them to become." | Tagline + Logo |

---

## 附录：录视频 checklist

- [ ] 后端已启动（uvicorn on :8000）
- [ ] 前端已启动（next dev on :3000）
- [ ] Lena 和 Caelan 的 profile 已从人物卡填充
- [ ] 提前跑一次 Sleep 生成一份报告（避免录视频时第一次触发）
- [ ] 屏幕分辨率 1920×1080
- [ ] 浏览器全屏 · 暗色主题
- [ ] 麦克风提前测音
- [ ] 总时长控制在 2:30 - 3:00（超了缩减 Step 4 或 Step 6）
