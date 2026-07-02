# NMA 进度跟踪 & 提交清单

> Deadline: 2026-07-10 05:00 GMT+8 | 倒计时: 18天（截至6/21）

---

## ✅ 已完成（76项里程碑）

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
| 单元测试（94用例 · bias/decay/validation/bias_prompt/API/Sleep） | ✅ |
| Docker 部署（Dockerfile × 2 + docker-compose + start.sh + .env.example） | ✅ |
| 架构图（英文/中文双版 · 含 GenBias 回路） | ✅ |
| **方向A：记忆衰减系统** | ✅ |
| ├ decay.py — 时间衰减公式（recall_score = importance × exp(-λ×Δt)） | ✅ |
| ├ episodic.py — events 表加 last_accessed_at/access_count + archive 表 + migration | ✅ |
| ├ generation.py — 可选 episodic_context 参数注入情景记忆 | ✅ |
| ├ ask.py — 提问前检索事件 → 算 recall → 塞 prompt → 记访问 | ✅ |
| ├ sleep.py — Phase 1.5 衰减归档 + REM 引用 archive + 报告 | ✅ |
| ├ seed.py — 预置12条P&P事件（Elizabeth 6 + Darcy 6） | ✅ |
| ├ record_access 同步提升 importance（检索效应 +0.01/cap 1.0） | ✅ |
| └ test_decay.py — 25个测试全绿 | ✅ |
| **文档更新** | ✅ |
| ├ README.md — Features 加 Memory Decay + Episodic Memory Injection | ✅ |
| ├ docs/tech-stack.md — 加 Decay Service | ✅ |
| └ internal/user-test-flow.md — 加情景记忆验证点 + 测试数更新 | ✅ |

---

## P0 — 提交必备

| 任务 | 说明 | 依赖 |
|------|------|------|
| □ Project Description（英文 ≤500词） | 初稿已写 → 你 review 改 | 无 |
| □ README 完善（截图/GIF + 快速开始 + 架构） | 初稿已写 → 你 review 改 + 截图 | 需跑起来截图 |
| □ 阿里云部署证明 | 后端部署到阿里云 + 录 <30s 证明视频 | 需一台阿里云 ECS |
| □ Demo 视频 ~3分钟 | 按 internal/user-test-flow.md 录制 + 剪辑 | 需脚本已就绪 |

## P1 — 提交冲刺

| 任务 | 说明 |
|------|------|
| □ Devpost 填表 | 上传视频 + 描述 + 架构图 + repo URL |
| □ LICENSE 可检测性确认 | MIT 已存在，确认 repo 页显示 |

## P2 — 低优先级

| 任务 | 工作量 | 说明 |
|------|--------|------|
| □ 移动端适配 | 🌕🌕🌕🌑 | demo 投屏/手机浏览 |
| □ 首次使用引导 | 🌕🌑🌑🌑 | 略加分，量小 |
| □ 向量检索集成测试 | 🌕🌕🌑🌑 | 需 Qwen API |
| □ SemanticMemory 持久化到 DB | 🌕🌕🌑🌑 | 非阻塞，当前在内存运行 |

---

## 技术债务 / 已知问题

- SemanticMemory 未持久化到 DB（当前在内存运行，服务重启后丢失。非阻塞，上线前可加）
- 无 CI/CD（黑客松不打分）
