# NMA 进度跟踪 & 提交清单

> Deadline: 2026-07-10 05:00 GMT+8 | 倒计时: 18天（截至6/21）

---

## ✅ 已完成（72项里程碑）

| 模块 | 状态 |
|------|------|
| 项目骨架（FastAPI + Next.js） | ✅ |
| 数据库设计（SQLite + ChromaDB） | ✅ |
| 三层记忆（工作/情景/语义） | ✅ 语义层未持久化到DB（非阻塞） |
| IngestionService 完整管道 | ✅ |
| Circuit A（GenerationService） | ✅ |
| Circuit B（ValidationService · OOC 6因子） | ✅ |
| GenBias（EMA 喜好学习 · 前后端打通） | ✅ |
| Sleep Cycle（3阶段巩固） | ✅ |
| 前端视图（5个Tab） | ✅ |
| API 端点（/ingest /ask /profile /sleep /feedback /session + /health） | ✅ 共6个路由 |
| OOC标签区分（violation vs surprise） | ✅ |
| Feedback偏好设置（always/on-ooc/never） | ✅ |
| 错误处理统一（ErrorToast 共享组件） | ✅ |
| 类型对齐（CharacterProfile + 移除 `as any`） | ✅ |
| 跨会话记忆（序列化/反序列化/恢复/前端横幅） | ✅ |
| 角色演示素材（《傲慢与偏见》Elizabeth + Darcy · 完整场景 + 4选项 · 4个演示问题） | ✅ |
| 单元测试（80用例 · Validation + Generation + bias + bias_prompt + API反馈 + Sleep） | ✅ |
| Docker 部署（Dockerfile × 2 + docker-compose + start.sh + .env.example） | ✅ |
| 架构图（英文/中文双版 · 含 GenBias 回路） | ✅ |

---

## P0 — 提交必备（6/21 - 6/25）

| 任务 | 说明 | 依赖 |
|------|------|------|
| □ Project Description（英文 ≤500词） | 初稿已写 → 你 review 改 | 无 |
| □ README 完善（截图/GIF + 快速开始 + 架构） | 初稿已写 → 你 review 改 + 截图 | 需跑起来截图 |
| □ Tech Stack 清单 | 已写 docs/tech-stack.md → 你确认格式 | 无，已知全部信息 |

## P1 — 演示准备（6/25 - 6/30）

| 任务 | 说明 | 依赖 |
|------|------|------|
| □ 演示视频脚本（~3分钟） | 痛点→方案→技术亮点的叙事线 | 需你确认方向 |
| □ 屏幕录制 + 画外音 | 实际操作录制 | 脚本定稿后 |
| □ 后期剪辑 | 加字幕/过渡/标注 | 录制完成后 |

## P2 — 加分项（有时间再做）

| 任务 | 工作量 | 说明 |
|------|--------|------|
| □ 移动端适配 | 🌕🌕🌕🌑 | demo 投屏/手机浏览 |
| □ 首次使用引导（选角→输入→提问） | 🌕🌑🌑🌑 | 略加分，量小 |

## P3 — 低优先级（截止前可加）

| 任务 | 说明 |
|------|------|
| □ 向量检索集成测试（ChromaDB + text-embedding-v3） | 需 Qwen API，集成测试 |
| □ SemanticMemory 持久化到 DB | 非阻塞，当前在内存运行 |

## P4 — 可做可不做

| 任务 | 说明 |
|------|------|
| □ CI/CD | 黑客松不打分，无实际收益 |

---

## 技术债务 / 已知问题

- SemanticMemory 未持久化到 DB（当前在内存运行，服务重启后丢失。非阻塞，上线前可加）
- 无 CI/CD（黑客松不打分）
