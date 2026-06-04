# Claude Mythos 多Agent协同 — NMA设计参考

> 2026-06-01 整理 · 来源见文末链接

---

## 事件概述

2026年5月26日，Anthropic工程师Sholto Douglas在X平台宣布，其最新模型**Claude Mythos**成功解决了组合几何学中一个世纪难题——**埃尔德什单位距离猜想**（Erdős unit distance conjecture，1946年提出），给出了"巧妙而简洁的证明"。

此前OpenAI的GPT-5.5也已攻克同一难题，标志着头部AI在纯数学发现领域的竞争进入白热化。

---

## 多Agent协同范式（与NMA直接相关）

此次突破的核心不是单一模型的智商，而是**多Agent协同架构**：

1. **并行生成**：多个独立Claude Code实例分别接收问题，各自生成不同的解决方案路径
2. **交叉验证**：汇总所有路径后，分发给其他独立运行的实例进行交叉验证
3. **择优收敛**：数学家Daniel Litt评论称，Mythos初始结果"略逊于"OpenAI的方案，但通过多实例间的互相校验，最终独立推导出**更具原创性和简洁的证明**

这与NMA的**双回路设计**（Circuit A生成多样化选项 + Circuit B多维度验证评分）在理念上高度一致——都是"生成多条路径→交叉验证→择优"的范式。

## 关键细节

- **技术栈**：基于Claude Code实例，非单一模型推理
- **协作方式**：Agent实例负责生成路径 → 汇总 → 分发 → 交叉验证
- **最终输出**：由Claude Opus 4.7编译发布正式证明版本
- **菲尔兹奖得主评价**：确认ChatGPT 5.5 Pro已能在两小时内完成博士级数学研究

## 行业影响

- **欧洲央行**因Mythos解禁召开紧急会议评估网络安全威胁
- **五角大楼**成立工作组加速AI在敏感网络中的应用
- 标志着AI从"提示工程"全面转向**自主Agent时代**

## 对NMA的启发

| NMA组件 | Mythos对照 | 可借鉴点 |
|---------|-----------|---------|
| Circuit A (Generation) | 多个Claude Code实例并行生成 | 多样性路径生成策略 |
| Circuit B (Validation) | 实例间交叉验证 | 验证的独立性与对抗性 |
| SleepCycle | 汇总→评估→收敛 | 多轮迭代的质量提升机制 |
| Session Resumption | 跨实例上下文保持 | 长时间多Agent协作的持久化 |

---

## 参考链接

- [Anthropic发布Claude Mythos模型，以简洁证明解决埃尔德什单位距离猜想](https://www.sohu.com/a/1028285150_122396381)
- [断网解题，Claude Mythos推翻Erdős 80年猜想！比OpenAI更短更漂亮 - 36氪](https://m.36kr.com/p/3827354186847105)
- [Reddit讨论：Mythos vs GPT-5.5方案对比](https://www.reddit.com/r/singularity/comments/1toeii7/mythos_using_claude_code_also_solves_the_unit/)
- [Anthropic官方发布页（需确认）](https://anthropic.com/news)
