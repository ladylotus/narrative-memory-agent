# Yann Dubois 持续学习论点 — NMA设计参考

> 2026-06-01 整理 · 来源见文末链接

## 核心框架

Yann Dubois（OpenAI后训练前沿团队联合负责人）在播客访谈中提出的「时间-实用性」坐标框架：

- **AI at t=0**：起点比大多数新员工高，但后续曲线基本平坦——模型不会学习企业内部知识
- **人类**：起点低但学习曲线陡峭
- **关键指标**：曲线下的面积（累积价值），人类在很多场景依然胜出

## 对NMA的启发

这个框架直接解释了为什么**外挂记忆系统是必须的**：

| 问题 | NMA方案 |
|------|---------|
| 模型自己不会成长 | 记忆层累积用户交互历史 |
| 跨会话无连续性 | Session Resumption 加载SQLite角色+上下文 |
| 无个性化学习 | Generation Bias根据用户反馈调整preferred_profile |
| SleepCycle模拟「巩固」 | 冲突检测→弧光演变→结构化报告 |

## 参考链接

- [搜狐全文](https://www.sohu.com/a/1026572983_122189055)
- [凤凰网转载](https://h5.ifeng.com/c/vivo/v002a2OsjP--QOUiZCNzin6XKsMnWGEuPet0hVkLErWXJ7aE__)
- [51CTO摘要](https://www.51cto.com/article/844094.html)
