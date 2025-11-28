# LLM & Agent

大语言模型与金融智能体在量化金融中的应用

> 共收录 **4** 篇论文 | [返回索引](../README.md)

---

### [基于量子分布组合电路（QDisCoCirc）的金融文本情感分析](https://arxiv.org/abs/2511.18804v1)

**日期**: 2025-11-28 | **作者**: Takayuki Sakuma

**标签**: `Sentiment Analysis` `NLP` `Transformer` `Investor Sentiment`

该论文将量子分布组合电路（QDisCoCirc）应用于金融文本三分类情感分析，通过分解句子为短连续chunk并映射到浅量子电路得到Bloch向量序列；采用量子token+小Transformer编码器+CCG类型嵌入的混合设计，既保留量子语义可解释性，又能建模语序与长依赖，提升了测试macro-F1，且chunk归因显示证据集中于少数chunk、正确预测句子更可靠使用类型嵌入。

---

### [基于LLM驱动的代码进化的认知阿尔法挖掘](https://arxiv.org/abs/2511.18850v1)

**日期**: 2025-11-28 | **作者**: Fengyuan Liu, Huang Yi, Sichun Luo et al.

**标签**: `LLM` `Factor Mining` `Asset Pricing` `Algorithmic Trading`

针对现有阿尔法挖掘方法搜索空间狭窄、模型不透明或经济依据不足等问题，本文提出CogAlpha框架，融合代码级阿尔法表示、LLM驱动推理与进化搜索，通过多阶段提示和金融反馈迭代优化候选阿尔法；在A股市场的实验表明，该框架挖掘的阿尔法在预测精度、鲁棒性和泛化性上均优于现有方法。

---

### [重新思考检索：金融领域大语言模型从传统检索增强生成到智能体与非向量推理系统的演进](https://arxiv.org/abs/2511.18177v1)

**日期**: 2025-11-28 | **作者**: Elias Lumer, Matt Melich, Olivia Zino et al.

**标签**: `LLM` `NLP` `Financial Agent` `Benchmark`

本文首次系统对比金融文档的向量基智能体RAG（混合搜索+元数据过滤）与非向量层次节点基RAG架构，评估交叉编码器重排序、小到大分块检索两种增强技术的效果；基于1200份SEC文件和150题基准，测检索指标、回答质量、 latency及成本，发现向量基智能体RAG更优，两种增强技术显著提升性能。

---

### [MortgageLLM：带残差指令迁移、对齐调优和任务特定路由的领域自适应预训练](https://arxiv.org/abs/2511.21101v1)

**日期**: 2025-11-28 | **作者**: Manish Jain, Satheesh Kumar Ponnambalam, Salman Faroz et al.

**标签**: `LLM` `NLP` `Financial Agent` `Transformer`

论文提出抵押贷款领域专用大模型MortgageLLM，采用双轨特化框架从LLaMA-3.1-8B构建对话问答与结构化任务两个专家模型，通过指令残差技术恢复指令遵循能力并设计智能任务路由机制，在领域基准上显著优于基础模型。

---

