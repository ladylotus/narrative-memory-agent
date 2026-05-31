# Narrative Memory Agent 叙事记忆智能体

## 赛道：Qwen Cloud Hackathon - Track 1: MemoryAgent

- **官网**: https://qwencloud-hackathon.devpost.com/
- **API控制台**: https://home.qwencloud.com/api-keys（Google/GitHub登录）
- **模型**: `qwen3.6-plus`（OpenAI兼容SDK）
- **Base URL**: 待验证（登录后可从API文档确认）
- **Deadline**: 2026-07-10 05:00 GMT+8

---

## 核心概念

不是"分析角色"，不是"跟角色聊天"——而是 **让角色自己说话，且不OOC**。

### 一句话
> 把一本小说扔给Agent，它蒸馏出一个角色，然后你可以问TA："如果是你，接下来怎么走？"

### 目标用户
1. **作者**（核心痛点）：创作遇到瓶颈时，问角色"你会怎么发展"→角色给出多个选项→作者选择→反馈闭环
2. **读者**（更大市场）：追小说烂尾/崩人设后，跟蒸馏出的角色探讨"if线"

---

## 心理学理论支撑（详见 ~/Caelvorn Series/参考/叙事记忆Agent-心理学理论支持.md）

| 理论 | 用途 |
|------|------|
| Baddeley 工作记忆模型（中央执行+情景缓冲区） | 当前阅读/交互状态的临时处理 |
| Tulving 情景记忆 vs 语义记忆 | 具体事件时间线 vs 抽象角色认知 |
| Zwaan 事件索引五维度（时间/空间/主角/因果/意图） | 结构化叙事追踪 |
| Kintsch 建构-整合模型 | 多样性生成→全局一致性筛选 |
| Asch 完形模型（中心特质） | Leo的"核心不可违背特质"标记 |
| Bartlett 图式理论 | 行为模式自动提取与预期生成 |
| Walker & Stickgold 睡眠记忆巩固 | 离线"巩固→整合→遗忘"循环 |
| Tononi & Cirelli 突触稳态假说 | 冗余信息剪枝，信号噪声比优化 |

---

## 技术架构（规划）

### 三层记忆系统
```
Layer 1: 工作记忆（当前会话）
Layer 2: 情景记忆（事件时间线 + Zwaan五维索引）
Layer 3: 语义记忆（角色认知图式 + 中心特质）
```

### 双回路响应
```
回路A（创意生成）：以角色身份生成多个发展方向
回路B（一致性校验）：比对中心特质 + 历史行为模式 → OOC风险评分
```

### 睡眠巩固（Sleep Cycle）
```
Phase 1 - SWS（事实巩固）：情景→语义迁移，冲突检测
Phase 2 - REM（抽象整合）：模式提取，冗余剪枝，情感解耦
Phase 3 - 自检报告：角色认知更新日志
```

---

## 与渡心阁关系

**完全独立**，代码全开源。Caelvorn Series角色数据作为Demo素材。

---

## 参赛要求（需经常比对）

### Track 1: MemoryAgent
> Build an Agent with persistent memory that autonomously accumulates experience, remembers user preferences, and makes increasingly accurate decisions across multi-turn, cross-session interactions.

**重点：**
- 高效存储检索（efficient memory storage and retrieval）
- 及时遗忘（timely forgetting of outdated information）
- 有限上下文内召回关键记忆（recalling critical memories within limited context windows）

### 提交材料
1. 公开Git仓库（含开源许可，在About区域可见）
2. 阿里云部署证明（录屏或代码文件）
3. 架构图（Qwen Cloud → 后端 → 数据库 → 前端）
4. 3分钟Demo视频（YouTube/Vimeo/Facebook公开）
5. 文字说明
6. 标注赛道
7. 可选：Blog文章（冲$500+$500云额度奖，10个名额）

### 评审标准
| 维度 | 权重 | 要点 |
|------|------|------|
| Technical Depth & Engineering | 30% | QwenCloud API的深入使用（如custom skills、MCP集成）；算法/工程创新 |
| Innovation & AI Creativity | 30% | 架构质量、模块化、可扩展性、错误处理；非平凡逻辑 |
| Problem Value & Impact | 25% | 真实世界相关性；产品化/开源社区潜力 |
| Presentation & Documentation | 15% | Demo清晰度；架构文档质量 |
