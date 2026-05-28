# OOC评分公式 · 论文引用

公式：**OOC_Risk = 1 - (αT + βB + γ(1-D) + δC - εP)**

---

## T — 特质一致性（Trait Consistency）

### 经典：Asch, S. E. (1946)
> "Forming Impressions of Personality"
> *Journal of Abnormal and Social Psychology, 41*(3), 258–290
> 🔗 https://en.wikipedia.org/wiki/Impression_formation

**核心发现**：中心特质（如"热情/冷漠"）不成比例地塑造整体印象，而边缘特质影响较小。人们形成的是**完形印象**而非独立特质的加总。

**为什么支持T因子**：角色的一些特质（Leo的忠诚、隐忍）就是他的"中心特质"——违背它们比违背边缘特质更严重。T因子在公式中权重最高，与此一致。

### 近期：Mannekote, A. et al. (2025)
> "Do Role-Playing Agents Practice What They Preach? Belief-Behavior Consistency in LLM-Based Simulations of Human Trust"
> *arXiv:2507.02197*
> 🔗 https://arxiv.org/abs/2507.02197

**核心发现**：提出了LLM角色扮演Agent的**信念-行为一致性度量**，发现系统性不一致。直接验证了"测量AI角色的特质一致性"这个思路的可行性。

**为什么支持T因子**：不仅理论上成立，而且有人已经在做类似的度量了。说明我们的方法有前例可循。

---

## B — 行为一致性（Behavioral Consistency）

### 经典：Bartlett, F. C. (1932)
> *Remembering: A Study in Experimental and Social Psychology*
> Cambridge University Press.
> 🔗 https://en.wikipedia.org/wiki/Frederic_Bartlett

**核心发现**：引入了**图式理论（Schema Theory）**——记忆不是复制的，而是基于已有知识结构主动重构的。"幽灵之战"实验证明回忆受已有图式塑造。

**为什么支持B因子**：角色在相似情境下的行为应该与其已建立的"行为图式"一致。B因子本质上是测量新选项与历史图式的吻合度。

### 计算实现：Rumelhart, D. E. (1980)
> "Schemata: The Building Blocks of Cognition"
> In Spiro et al. (Eds.), *Theoretical Issues in Reading Comprehension*
> 🔗 https://en.wikipedia.org/wiki/Schema_(psychology)

**核心发现**：将图式理论形式化为计算数据结构——图式具有可填充的"槽位"（slots）。

**为什么支持B因子**：提供了B因子的工程实现思路——角色的历史行为模式就是一组"图式+填充值"，新选项匹配度可量化计算。

---

## D — 语义距离（Semantic Distance）

### 基础：Mikolov, T. et al. (2013)
> "Efficient Estimation of Word Representations in Vector Space"
> *arXiv:1301.3781*
> 🔗 https://arxiv.org/abs/1301.3781

**核心发现**：Word2Vec——词语表示为稠密向量，语义关系通过向量运算保持（king - man + woman ≈ queen）。**余弦距离**衡量语义相似度。

**为什么支持D因子**：整个embedding范式的起点——用向量距离衡量语义距离是统计学上严谨的做法。

### 工程实现：Reimers, N. & Gurevych, I. (2019)
> "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks"
> *EMNLP 2019. arXiv:1908.10084*
> 🔗 https://arxiv.org/abs/1908.10084

**核心发现**：SBERT生成语义上有意义的句子级embedding，通过余弦相似度高效计算语义相似度。

**为什么支持D因子**：D因子的直接实现方法——用SBERT编码角色语义记忆质心，对比生成文本的embedding。

---

## C — 自洽性（Self-Consistency）

### 经典：Festinger, L. (1957)
> *A Theory of Cognitive Dissonance*
> Stanford University Press.
> 🔗 https://en.wikipedia.org/wiki/Cognitive_dissonance

**核心发现**：**认知失调理论**——人类对持有矛盾认知有本能的厌恶，失调感会驱使人们通过改变信念或行为来化解矛盾。

**为什么支持C因子**：角色内部自相矛盾的回应会导致"认知失调"感——读者会觉得"这个角色不对劲"。C因子就是对这种内在矛盾的检测。

### 结构基础：Heider, F. (1946)
> "Attitudes and Cognitive Organization"
> *Journal of Psychology, 21*(1), 107–112
> 🔗 https://en.wikipedia.org/wiki/Balance_theory

**核心发现**：**平衡理论**——个体寻求态度间的平衡关系；不平衡的三元组（P-O-X）会创造张力。

**为什么支持C因子**：提供了一个可形式化的结构模型——检查一个角色回应中是否存在"不平衡"配置。这可以计算化。

---

## P — 惊奇度（Surprise Factor）

### 关键：Itti, L. & Baldi, P. (2009)
> "Bayesian Surprise Attracts Human Attention"
> *Advances in Neural Information Processing Systems (NeurIPS), 19*
> 🔗 https://papers.nips.cc/paper_files/paper/2005/hash/0172d289da48c48de8c5ebf3de9f7ee1-Abstract.html

**核心发现**：将"惊奇"形式化为**贝叶斯惊奇（Bayesian Surprise）**——后验与先验之间的KL散度。高贝叶斯惊奇强烈吸引注意力。

**为什么支持P因子**：提供了P因子的数学定义——惊奇度 = 预期分布（基于角色历史）与生成文本之间的KL散度。这区分了"不好的OOC"（纯粹不一致）和"好的弧光"（意外但合理的角色发展）。

### 理论扩展：Schmidhuber, J. (2010)
> "Formal Theory of Creativity, Fun, and Intrinsic Motivation"
> *IEEE Transactions on Autonomous Mental Development, 2*(3), 230–247
> 🔗 https://en.wikipedia.org/wiki/J%C3%BCrgen_Schmidhuber#Formal_theory_of_creativity

**核心发现**：创造力最大化"有趣性=学习进步"。最优点：**太可预测=无聊，太惊奇=不可理解**。

**为什么支持P因子**：直接验证了 `-εP` 的设计——适当的惊奇度**降低**OOC风险，因为合理的角色发展应该有一定的新颖性。P因子不是惩罚"不像"，而是奖励"合理地不像"。
