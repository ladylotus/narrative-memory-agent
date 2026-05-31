# 📋 NMA 黑客松 — 项目跟踪

> **赛道：** Qwen Cloud Track1 · **Deadline:** 2026/7/10
> **仓库：** `ladylotus/narrative-memory-agent`（当前 private，提交前改为 public）
> **模型：** `qwen3.6-plus`（主模型）+ `text-embedding-v3`（嵌入）
> **状态：** 开发中 · 2026/5/31 更新

---

## 🗺️ 总路线图

```
W1 (5/27-6/2)  方案定稿 + 架构图 + Git仓库初始化     ← 📍 现在（W1末）
                → Qwen API验证 + 基础骨架 (done)
                → Next.js前端骨架 (done)

W2 (6/3-6/9)   小说摄入 + 角色识别 + 三层记忆构建
                → IngestionService 真实逻辑
                → 嵌入检索跑通

W3 (6/10-6/16) 回路A(创意生成) + 回路B(OOC校验)
                → 用Caelvorn角色测试

W4 (6/17-6/23) 睡眠巩固实现 + 前端对接后端API

W5 (6/24-6/30) 打磨 + 前端完善 + 端到端验证

W6 (7/1-7/7)   阿里云部署 + Demo视频录制 + 文字说明

W7 (7/8-7/10)  最终检查 + 提交
```

### 📦 提交材料清单（W7前完成）

| 材料 | 状态 |
|------|------|
| 公开 Git 仓库（含 MIT 许可证） | 🟡 已有，提交前改 public |
| 阿里云部署证明（URL + 说明） | ❌ |
| 架构图 | ✅ `docs/architecture.en/zh.html` |
| 3 分钟 Demo 视频 | ❌ |
| 文字说明（项目描述） | ❌ 最终版需英文 |
| 赛道标注 Track 1: MemoryAgent | ❌ Devpost 上标 |
| Blog 文章（可选，冲 $500+$500 云额度奖） | ❌ |

---

## ✅ 已完成

### 📐 方案与设计
- [x] **方案文档** — `方案文档.md`（双回路设计：创意生成 Circuit A + OOC 校验 Circuit B）
- [x] **技术风险分析** — `技术风险分析.md`（OOC 公式推导、多因子模型、权重关系图）
- [x] **市场验证** — `市场验证.md`
- [x] **OOC 论文引用** — `OOC公式-论文引用.md`
- [x] **架构图** — `docs/architecture.html`（英文）+ `docs/架构图.html`（中文），已 commit

### 🏗️ 后端（FastAPI）
- [x] **项目骨架** — `backend/` 目录结构，`pyproject.toml` 依赖配置
- [x] **4 个 API 端点（stub）**：
  - `POST /ingest` — 小说摄入
  - `POST /ask` — 与角色对话（含 OOC 校验）
  - `GET /profile/{name}` — 角色档案查询
  - `POST /sleep` — 睡眠巩固
- [x] **3 层记忆架构** — working / episodic / semantic（含 `vectors.py` 嵌入 stub）
- [x] **数据模型** — `Character`, `Event` schema
- [x] **服务层** — ingestion / generation / validation stubs
- [x] **Qwen API 验证通过** — `qwen3.6-plus`、`qwen-plus`、`qwen3.6-flash`、`text-embedding-v3` 均可调用
- [x] **qwen3.6-plus 角色扮演测试** — Circuit A + B 双回路均通过，模型自带 CoT 推理
- [x] **pytest 测试** — 5/5 测试通过（health + 4 端点）

### 🎨 前端（Next.js）
- [x] **Next.js 项目初始化** — `frontend/`，TypeScript + Tailwind CSS
- [x] **5 个页面组件**：
  - `Sidebar` — 角色列表侧栏（暗色 + emoji）
  - `ConversationView` — 对话交互（OOC 三色标签 ✅⚠️❌、选项卡片）
  - `ProfileView` — 角色档案
  - `SleepLogView` — 睡眠巩固日志
  - `SettingsView` — 设置面板
- [x] **数据层** — `types.ts` + `data.ts`（示例数据）
- [x] **布局** — `layout.tsx` + `globals.css`（暗色主题 #0a0a0c）
- [x] **构建通过** — `npm run build` 无报错

### 📦 基础设施
- [x] **Git 仓库初始化** — GitHub: `ladylotus/narrative-memory-agent`
- [x] **MIT License** — `LICENSE`
- [x] **README** — 已更新正确链接（Devpost、Qwen Cloud Console）
- [x] **.gitignore** — 排除 `.env`、`node_modules`、`.venv`、`__pycache__` 等
- [x] **.env 配置** — API Key、Base URL、模型名

---

## ❌ 未完成 / 待做

### 🔄 后端服务（核心逻辑）
- [ ] **GenerationService** — 真实的 Circuit A 实现：调用 qwen3.6-plus 生成角色回复
- [ ] **ValidationService** — 真实的 Circuit B 实现：调用 qwen3.6-plus 进行 OOC 校验 + 风险评分
- [ ] **IngestionService** — 小说文本解析 + 角色提取 + 事件分段的真实逻辑
- [ ] **SleepCycle 实现** — 工作记忆 → 情景记忆 → 语义记忆的压缩/整合/遗忘

### 🌐 前后端对接
- [ ] **API 客户端封装** — 前端 fetch 封装，指向 FastAPI 后端（含 CORS 配置）
- [ ] **真实数据替换示例数据** — 用后端 `/profile` 和 `/ingest` 的结果驱动 UI
- [ ] **对话流串联** — 前端发消息 → `/ask` → 显示回复 + OOC 标签

### 🧪 测试与验证
- [ ] **完整端到端测试** — 摄入一段小说 → 建立角色 → 对话 → 睡眠巩固 → 再对话验证记忆
- [ ] **边缘情况测试** — 空输入、长文本、多角色同时对话、OOC 边界案例

### 🧹 提交准备（7/10 前）
- [ ] **仓库改为 public** — 提交前操作
- [ ] **README 精修** — 项目简介、使用说明、架构图、截图
- [ ] **Devpost 提交** — 项目描述 + 视频/截图 + 源码链接
- [ ] **清理文件** — 移除开发痕迹(.env 模板保留但不含 key)、检查敏感信息泄露

---

## 🔜 下一步做什么（优先级排序）

| 优先级 | 事项 | 预计时长 |
|--------|------|----------|
| 🔴 P0 | **填 GenerationService + ValidationService 的代码** — 让 `/ask` 真正调用 Qwen API 并返回 OOC 评分 | 2-3h |
| 🔴 P0 | **SleepCycle 逻辑** — 从工作记忆到语义记忆的压缩通道 | 1-2h |
| 🟡 P1 | **IngestionService** — 小说摄入的文字解析逻辑 | 1-2h |
| 🟡 P1 | **前端对接后端 API** — fetch 封装 + 真实数据替代示例 | 1-2h |
| 🟢 P2 | **端到端测试** — 用一段实际小说跑通全流程 | 1h |
| 🟢 P2 | **README 精修 + 截图** | 0.5h |
| ⚪ P3 | **Devpost 提交** | 0.5h |

---

---

## 🧠 跨会话记忆（比赛核心要求）

**官方原文（Qwen Cloud Hackathon 官网）：**
> *"Build an Agent with persistent memory that autonomously accumulates experience, remembers user preferences, and makes increasingly accurate decisions across **multi-turn, cross-session interactions**."*

### 三个独立要求，缺一不可

| 级别 | 含义 | 我们当前状态 |
|------|------|-------------|
| **Multi-turn** 🗣️ | 同一次对话里，A说完B回，不要断了就忘 | ✅ 工作记忆覆盖 |
| **Cross-session** 🔄 | 关浏览器走人，明天回来开新会话，还记得昨天的事 | ⚠️ 架构扛得住，但需要显式设计 session resumption |
| **User preferences** 🧑 | 系统知道你喜欢什么风格、上次选了哪个选项、习惯什么问法 | 🔴 还没写 |

### 跨会话的行业定义

来自 NirDiamant Agent Memory Bible（421 stars，业界定标仓库）[cross_session_memory.ipynb](https://github.com/NirDiamant/Agent_Memory_Techniques/blob/main/all_techniques/21_cross_session_memory/cross_session_memory.ipynb)：

> *"Cross-session memory operates at the boundaries of sessions. It serializes state when a session ends and deserializes it when a new session starts."*

核心机制：
```
Session 1: 用户来 → 对话 → 结束时保存状态
                 ↓              ↑
           持久化存储（SQLite + ChromaDB）
                 ↓              ↑
Session 2: 用户回来 → 加载记忆 → 续上对话
```

### 我们的架构覆盖度

| 组件 | 持久化？ | 用途 |
|------|---------|------|
| SQLite（events / characters） | ✅ 文件持久 | 情景记忆 + 语义记忆 |
| ChromaDB（向量嵌入） | ✅ 文件持久 | 语义检索 |
| 工作记忆 | ❌ 临时的 | 当前会话上下文，每次重建 |

**依赖链：** SQLite 和 ChromaDB 都是文件持久 → 天然跨会话。用户关浏览器再打开，只要后端还在跑（或数据文件在），就记得昨天的事。

### 需要显式补的内容

- [ ] `services/session_resumption.py` — 启动时从 SQLite 加载之前的角色和记忆，重建工作记忆上下文
- [ ] `memory/user_preferences.py` — 记录用户选过的选项、提问偏好
- [ ] `services/preference.py` — 从用户选择序列中提取偏好模式
- [ ] 前端 `/session/new` 端点 — 显式区分"第一次打开"vs"回访用户"（冷启动 vs 续接）
- [ ] 后端启动时——若 SQLite 中有数据 → 跨会话加载；若空 → 冷启动欢迎页
- [ ] 提交演示时——明确在 Demo 中展示：**\"昨天聊了Leo，今天打开还认识\"**

---

## 🔑 重要备忘

- **提交前必须 repo 变 public** — 否则评审查不到
- **.env 不能 commit** — 已加 `.gitignore`，之后做模板 `.env.example`
- **前端构建暂用示例数据** — 后端 API 跑通后再替换
- **提交材料需英文** — Devpost 要求，最终版 README 统一翻译
- **Caelvorn 做 Demo** — 用 Caelvorn 系列小说作为演示案例
- **全开源，独立于渡心阁** — 不涉及渡心阁的任何代码和数据
