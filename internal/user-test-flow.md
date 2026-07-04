# NMA 用户测试流程 / Demo 视频脚本

**时长：** ~2分钟 · **角色：** Elizabeth Bennet + Fitzwilliam Darcy（Pride and Prejudice）

---

## 🎬 Opening (15s)

| 音频 | 画面 |
|------|------|
| "Characters in fiction should remember. They should grow. They should feel real — not reset every time you close the window." | 黑底白字 fade in，渐暗 → 页面载入动画 |

---

## Step 1 · 选角色 (15s)

| 操作 | 界面预期 | 画面 |
|------|---------|------|
| 打开 `http://localhost:3000` | 暗色主题加载，左侧栏出现两个角色 | 镜头从 logo 拉到全页 |
| 左侧栏已选中 Elizabeth Bennet（默认） | 右区显示场景卡片 + 聊天框 | 鼠标悬停在两个角色头像上示意可切换 |

### ✅ 测试点
- [ ] 两个角色都可见（Elizabeth Bennet + Fitzwilliam Darcy）
- [ ] 页面不报错、无空白区
- [ ] 默认选中 Elizabeth，场景卡片有描述文字

---

## Step 2 · 问问题 + OOC 评分 (30s)

| 操作 | 界面预期 | 画面 |
|------|---------|------|
| 在输入框输入（或直接用预置场景）：*"Elizabeth, Mr. Darcy just proposed. What do you say?"* | 场景卡片更新为选定的 prompt | 打字过程特写 |
| 点击发送或回车 | 加载动画 → 出现 4 张 OptionCard | 加载 → 卡牌弹出动画 |
| 观察每张卡的右上角 | 每张卡有 **risk 标签**（如 🟢 · 22% / 🟠 · 54% / 🔴 · 78%） | 鼠标划过每张卡的 risk badge |

### ✅ 测试点
- [ ] 出现 4 个选项，每张卡都有 risk 等级（green/orange/red）
- [ ] risk 标签同时显示类型（fitting / violation / surprise）
- [ ] 选项有 title + voice 文案，风格像 Elizabeth 会说的话
- [ ] 选项明显参考了剧情事件（如 Darcy 的求婚、舞会上的侮辱）—— 说明情景记忆已注入

**核心亮点口播：** *"Every response is validated through our Dual Circuit — generation plus OOC scoring on five factors: trait consistency, behavior patterns, semantic distance, self-consistency, and surprise value."*

---

## Step 3 · 选路径 + GenBias 反馈 (20s)

| 操作 | 界面预期 | 画面 |
|------|---------|------|
| 点击第 2 或第 3 张卡（推荐选风险中等、听起来像 Elizabeth 的） | 卡牌高亮选中态，其他卡牌变暗 | 点击动画 |
| 在弹出的 mark 选择框中选 **🎯 It's what they'd do** | 四选项外观缩小弹窗 | 选择动作特写 |
| 提交 | Toast 提示 "Feedback saved" | Toast 闪现 |

### ✅ 测试点
- [ ] 点击可选中，选中态清晰
- [ ] mark 弹窗出现，四个选项都可选
- [ ] 选择后 Toast 浮现 "Feedback saved"（无报错）
- [ ] 可以连续问下一个问题

**口播：** *"That mark isn't just a like button. It's training data — our GenBias loop uses EMA to learn what kind of responses you prefer for each character."*

---

## Step 4 · 看角色档案 (15s)

| 操作 | 界面预期 | 画面 |
|------|---------|------|
| 侧栏点击 **Profile** tab | 显示 Elizabeth 的五维特质条 + 行为模式 + 关系网络 | 切换到 Profile 视图 |

### ✅ 测试点
- [ ] Profile 有数据展示（不是空白"no profile yet"）
- [ ] 特质条有百分比数值
- [ ] 行为模式有文本描述
- [ ] 关系网络至少出现 Darcy（如果已摄入）

**口播：** *"Every character has a living cognitive profile — traits, behavior patterns, relationships, all evolving with every conversation."*

---

## Step 5 · 跑一轮 Sleep 巩固 (20s)

| 操作 | 界面预期 | 画面 |
|------|---------|------|
| 侧栏点击 **Sleep** tab | 显示 Sleep 说明页 + "Run Consolidation" 按钮 | 切换到 Sleep 视图 |
| 点击 "Run Consolidation" | 加载动画 → 弹出三段式报告：NREM / REM / Self-Audit | 报告展开动画 |
| 扫一眼报告内容 | 应有：发现的事实、抽象出的 traits、矛盾检测（如果有） | 鼠标从上往下扫 |

### ✅ 测试点
- [ ] 按钮可点击，加载不卡死
- [ ] NREM 阶段列出提取的事实
- [ ] REM 阶段列出抽象的 trait 变化
- [ ] Self-Audit 有置信度评述
- [ ] 如果已有大量事件，报告中会出现 📦 归档行（demo 数据量小则不会触发）
- [ ] 无后端错误（检查浏览器 Console 无红色报错）

**口播：** *"Inspired by human memory consolidation — NREM extracts facts, REM abstracts patterns, and the system audits its own confidence."*

---

## Step 6 · 跨会话记忆 (10s)

| 操作 | 界面预期 | 画面 |
|------|---------|------|
| 侧栏切到 **Darcy** 角色 | Profile / Conversation 内容切换为 Darcy 的数据 | 切角色过渡 |
| 切回 **Elizabeth** | 顶部出现横幅："Resumed session — X turns remaining" | 横幅显现 |

### ✅ 测试点
- [ ] 切到 Darcy 后内容切换正常
- [ ] 切回 Elizabeth 后有黄色/蓝色 session resumption 横幅
- [ ] 横幅显示 turn count 和 last question 摘要

**口播：** *"Characters remember you across sessions. Switch characters, come back — the conversation picks up where you left off."*

---

## 🎬 Closing (10s)

| 音频 | 画面 |
|------|------|
| "NMA is open source. Try it with your own characters. Pull requests welcome." | 最终画面：GitHub repo URL |
| "Where characters remember who they are — and who you want them to become." | 行尾 tagline |

---

## 测试通过标准（快速检查清单）

| # | 步骤 | 核心预期 | 通过 |
|---|------|---------|:----:|
| 1 | 页面加载 | 暗色主题、角色列表可见、无报错 | ☐ |
| 2 | 提问 | 4 个选项 + risk badge | ☐ |
| 3 | 选 + 标记 | 不报错、Toast "Feedback saved" | ☐ |
| 4 | 看 Profile | 特质条 + 行为 + 关系有数据 | ☐ |
| 5 | 跑 Sleep | 三段报告可展开、无后端错误 | ☐ |
| 6 | 切角色回看 | session resumption 横幅出现 | ☐ |

**6 项全绿 → 核心链路完整打通。** 后端、前端、LLM 通信、Memory 读写（含衰减归档）、GenBias 回路的边界测试已在开发环境中 93/93 通过，可以安心准备提交材料。

---

*原始文件：`docs/user-test-flow.md`*
*初稿日期：2026-06-21*
