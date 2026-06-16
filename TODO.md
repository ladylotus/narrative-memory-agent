# NMA 进度跟踪 & 提交清单

> Deadline: 2026-07-10 05:00 GMT+8 | 倒计时: 27天（截至6/12）

---

## 当前阶段：W3 — 集成与打磨（6/10 - 6/16）

### □ 1. 测试覆盖完善
- [x] feedback 端点测试（`test_api.py` 补充 `/feedback/` 路由，6用例全部通过 ✅）
- [ ] ValidationService 独立单元测试（OOC公式各因子边界）
- [ ] GenerationService 测试（bias注入、trait injection）
- [ ] 向量检索集成测试（ChromaDB + text-embedding-v3）

### □ 2. 前端清理 & 数据规范化
- [ ] `data.ts` 清理：替换 Frankenstein mock 为 Caelvorn 系列真实角色
- [ ] 前后端类型对齐（types.ts ↔ models.py）
- [ ] 错误处理统一（前端 404/500 的 user-friendly fallback）

### □ 3. Deployment 准备
- [ ] Dockerfile（backend + frontend 分容器）
- [ ] QwenCloud 环境变量配置文档
- [ ] 一键启动脚本
- [ ] 架构图更新（加入 GenBias 回路）

---

## W4 — 精细化与演示准备（6/17 - 6/23）

### □ 4. 跨会话记忆（Cross-Session Memory）
- [ ] session context 序列化/反序列化
- [ ] user_preferences 模块
- [ ] 多轮对话恢复验证

### □ 5. 角色演示素材
- [ ] 3~5 个 Caelvorn 角色注入（Caelan, Leo, Kaelen, 等）
- [ ] 每个角色 2~3 段典型问答（展示不同"性格"输出）
- [ ] OOC 触发案例（展示校验回路价值）

### □ 6. 用户体验打磨
- [ ] 首次使用引导（选中角色→输入→提问 三步）
- [ ] Loading/空状态/错误状态 视觉处理
- [ ] 移动端适配（关键）

---

## W5 — 提交包组装（6/24 - 6/30）

### □ 7. 演示视频
- [ ] 场景脚本：3 分钟产品叙事
  - ① 痛点引入：作者写小说卡住
  - ② 解决方案：注入章节→角色蒸馏→问"你会怎么走"
  - ③ 技术亮点：OOC校验 + GenBias喜好学习
- [ ] 屏幕录制 + 画外音
- [ ] 后期剪辑

### □ 8. 提交材料
- [ ] Project Description（英文 500词以内）
- [ ] Tech Stack 清单
- [ ] 仓库 README 完善（截图/GIF）

### □ 9. Devpost 提交
- [ ] 视频链接上传
- [ ] 代码仓库链接
- [ ] 技术实现说明
- [ ] 团队信息

---

## W6 — 缓冲区（7/1 - 7/10）

### □ 10. 应急储备
- [ ] Bug 修复窗口
- [ ] 最后一轮端到端测试
- [ ] 提交按钮前检查清单

---

## 已完成的里程碑

| 模块 | 完成状态 | 备注 |
|------|----------|------|
| 项目骨架（FastAPI + Next.js） | ✅ | |
| 数据库设计（SQLite + ChromaDB） | ✅ | |
| 三层记忆（工作/情景/语义） | ✅ | 语义层未持久化到DB |
| IngestionService 完整管道 | ✅ | |
| Circuit A（GenerationService） | ✅ | |
| Circuit B（ValidationService） | ✅ | OOC 6因子评分 |
| GenBias（EMA 喜好学习） | ✅ | 前后端已打通 |
| Sleep Cycle（3阶段巩固） | ✅ | |
| 前端视图（5个Tab） | ✅ | |
| API 端点（5条路由） | ✅ | |
| 基础测试（API + Sleep） | ✅ | 覆盖率不够 |
| 跨会话记忆分析 | ✅ | 方案已出，待实现 |
| OOC标签区分（violation vs surprise） | ✅ | |
| Feedback偏好设置（always/on-ooc/never） | ✅ | |

---

## 技术债务 / 已知问题

- [ ] SemanticMemory 未持久化到 DB（非阻塞，上线前可加）
- [ ] data.ts 含 Frankenstein 残余数据（低优先级，纯前端无关）
- [ ] 无 CI/CD（没做也没坏处，黑客松不打分）
