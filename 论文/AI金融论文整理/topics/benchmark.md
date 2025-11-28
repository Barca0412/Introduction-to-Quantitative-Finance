# Benchmark & Evaluation

金融AI基准测试与模型评估

> 共收录 **6** 篇论文 | [返回索引](../README.md)

---

### [Heston模型下的高效重要性采样：短到期与深度虚值期权](https://arxiv.org/abs/2511.19826v1)

**日期**: 2025-11-28 | **作者**: Yun-Feng Tu, Chuan-Hsiang Han

**标签**: `Volatility` `Options` `Asset Pricing` `Benchmark`

论文针对Heston模型下短到期和深度虚值这两个稀有事件场景，基于大偏差原理设计状态依赖的测度变换；短到期 regime证明所提重要性采样漂移达对数效率（渐近最优），深度虚值 regime引入慢均值回复 scaling并通过Riccati分析验证最优性，数值实验显示方差降低超几个数量级。

---

### [自激发索赔下的最优分红与资本注入](https://arxiv.org/abs/2511.19701v1)

**日期**: 2025-11-28 | **作者**: Paulin Aubert, Etienne Chevalier, Vathana Ly Vath

**标签**: `Reinforcement Learning` `Risk Management` `Portfolio Optimization` `Benchmark`

本文研究自激发索赔（Hawkes过程）下Cramér-Lundberg模型的最优分红与资本注入问题，建立价值函数分析性质并以显式阈值刻画最优资本注入策略，证明其为HJB变分不等式的唯一粘性解；数值上结合单调有限差分+Howard策略迭代得到基准解，提出基于策略梯度和演员-评论家的强化学习方法，学习策略匹配基准且稳定，为高维扩展提供可扩展思路。

---

### [重新审视金融领域的时间序列基础模型](https://arxiv.org/abs/2511.18578v1)

**日期**: 2025-11-28 | **作者**: Eghbal Rahimikia, Hao Ni, Weiguan Wang

**标签**: `Time Series` `Deep Learning` `Transformer` `Benchmark`

本文是首个全面实证研究时间序列基础模型（TSFMs）在全球金融市场表现的工作，利用大规模日度超额收益数据集对比零样本推理、微调及从头预训练与基准模型的效果；发现现成预训练TSFMs在零样本和微调场景下表现不佳，但基于金融数据从头预训练的模型在预测能力和经济收益上显著提升，且增大数据集、合成数据增强及超参调优可进一步优化性能。

---

### [面向污染训练数据的自适应激进拒绝异常检测方法](https://arxiv.org/abs/2511.21378v1)

**日期**: 2025-11-28 | **作者**: Jungi Lee, Jungkwon Kim, Chi Zhang et al.

**标签**: `Anomaly` `Risk Management` `Benchmark`

传统异常检测模型假设训练数据为纯正常数据，但污染数据会严重影响性能，现有方法依赖固定污染率易因实际比例偏差失效；论文提出自适应激进拒绝（AAR）方法，通过改进z-score和高斯混合模型阈值动态排除异常，结合软硬拒绝策略平衡正常数据保留与异常排除；实验表明AAR在多数据集上优于现有SOTA方法，增强污染数据鲁棒性，支持安全、医疗等领域应用。

---

### [动态市场行为预测的深度学习模型优化](https://arxiv.org/abs/2511.19090v1)

**日期**: 2025-11-28 | **作者**: Shenghan Zhao, Yuzhen Lin, Ximeng Yang et al.

**标签**: `Deep Learning` `Time Series` `Transformer` `Benchmark`

论文聚焦电商零售SKU级多horizon（H=1、7、14）日度需求/收入预测，提出融合多尺度时序卷积、门控循环模块及时序感知自注意力的混合序列模型；经严格时间分割训练评估，模型在准确率及峰值/假期稳健性上优于传统及前沿基准模型，且通过消融实验与统计显著性检验验证可靠性并开源实现。

---

### [重新思考检索：金融领域大语言模型从传统检索增强生成到智能体与非向量推理系统的演进](https://arxiv.org/abs/2511.18177v1)

**日期**: 2025-11-28 | **作者**: Elias Lumer, Matt Melich, Olivia Zino et al.

**标签**: `LLM` `NLP` `Financial Agent` `Benchmark`

本文首次系统对比金融文档的向量基智能体RAG（混合搜索+元数据过滤）与非向量层次节点基RAG架构，评估交叉编码器重排序、小到大分块检索两种增强技术的效果；基于1200份SEC文件和150题基准，测检索指标、回答质量、 latency及成本，发现向量基智能体RAG更优，两种增强技术显著提升性能。

---

