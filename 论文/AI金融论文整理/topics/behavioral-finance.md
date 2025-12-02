# Behavioral Finance

行为金融学与投资者情绪

> 共收录 **10** 篇论文 | [返回索引](../README.md)

---

### [不完美的必要性：通过模拟认知有限性逆转模型崩塌](https://arxiv.org/abs/2512.01354v1)

**日期**: 2025-12-02 | **作者**: Zhongjie Jiang

**标签**: `LLM` `NLP` `Behavioral Finance` `Risk Management`

本文指出合成数据因追求统计平滑去除人类文本的认知相关不规则性，加速模型崩塌；提出Prompt驱动认知计算框架（PMCSF），含认知状态解码器（CSD）和带认知扰动算子的认知文本编码器（CTE），模拟人类认知过程生成带典型不完美的文本；验证显示CTE文本与人类文本差异小，且A股压力测试中策略最大回撤降低47.4%。

---

### [稳定币市场政治风险的预警信号：2024年美国大选前后的人类与算法行为](https://arxiv.org/abs/2512.00893v1)

**日期**: 2025-12-02 | **作者**: Kundan Mukhia, Buddha Nath Sharma, Salam Rabindrajit Luwang et al.

**标签**: `Risk Management` `Behavioral Finance` `Algorithmic Trading` `Time Series`

本文以2024年美国大选为政治风险事件，区分人类驱动的P2P稳定币交易与算法活动，通过结构突变分析、替代基检验等方法发现，人类驱动的ERC-20交易在大选前2天出现变化，早于交易所交易量（大选日）和算法智能合约活动（2025年1月）；结合能量谱分析与结构向量自回归验证，人类驱动的稳定币流动可作为政治压力的预警指标。

---

### [随机风险厌恶下的均衡投资：（非）唯一性、最优性与比较静态分析](https://arxiv.org/abs/2512.00830v1)

**日期**: 2025-12-02 | **作者**: Cheng Weilun, Liang Zongxia, Wang Sheng et al.

**标签**: `Portfolio Optimization` `Risk Management` `Behavioral Finance`

这篇论文研究随机风险厌恶参数一般分布下的无限维投资组合选择问题，刻画了确定性均衡投资策略的结构（有限期望风险厌恶时均衡唯一，无限期望时可能多均衡或平凡解）；引入三类最优性准则并明确其均衡的存在唯一性，还通过比较静态分析发现反向 hazard rate 占优的风险厌恶分布对应更不激进的均衡策略。

---

### [带S形效用的随机占优约束优化：差表现区域算法与神经网络](https://arxiv.org/abs/2512.00299v1)

**日期**: 2025-12-02 | **作者**: Zeyun Hu, Yang Liu

**标签**: `Portfolio Optimization` `Risk Management` `Deep Learning` `Behavioral Finance`

论文研究带一阶和二阶随机占优（SD）约束的S形非凹效用静态投资组合选择问题，明确求解一阶SD约束下一般S形效用的最优解；针对二阶SD约束问题（因Sion定理无效难以解析求解），提出差表现区域算法找次优解，并开发算法引导的分段神经网络框架学习该问题解。

---

### [零售投资者投资期限与盈余公告](https://arxiv.org/abs/2512.00280v1)

**日期**: 2025-12-02 | **作者**: Domonkos F. Vamossy

**标签**: `Behavioral Finance` `Investor Sentiment` `Asset Pricing` `Anomaly`

本文利用2010-2021年StockTwits帖子将股票分为长/短期限，发现期限结构显著预测盈余公告相关回报模式（长期限股票即时反应更大、公告后漂移更明显）；相关多空策略月alpha达0.43%，且事前情绪对短期限股票后续表现影响更显著，证明零售期限结构是盈余回报变异的有用维度。

---

### [读心还是误读？大五人格测试中的大语言模型](https://arxiv.org/abs/2511.23101v1)

**日期**: 2025-12-01 | **作者**: Francesco Di Cursi, Chiara Boldrini, Marco Conti et al.

**标签**: `LLM` `NLP` `Behavioral Finance`

该论文测试5个大语言模型（含GPT-4及开源轻量模型）在3个异构数据集和2种提示策略下的大五人格二分类预测，发现丰富提示减少无效输出但引入系统偏差，不同特质预测难度差异显著；现有开箱即用LLM暂不适合自动人格预测，需协调提示设计、特质框架与评估指标。

---

### [匹配市场中的限价订单簿动态：微观结构、价差与执行滑点](https://arxiv.org/abs/2511.20606v2)

**日期**: 2025-11-28 | **作者**: Yao Wu

**标签**: `Market Microstructure` `Execution` `Behavioral Finance`

本文针对传统匹配市场模型假设货币转移可弥补效用差异但实证存在结构性偏好缺口的问题，引入基于刚性买卖价差的限价订单簿系统微观结构框架，用潜在偏好状态矩阵刻画个体偏好；建立阈值不可能定理并提出动态离散选择执行模型，数值实验验证持续滑点等现象，统一解释匹配失败、补偿低效等问题。

---

### [基于量子分布组合电路（QDisCoCirc）的金融文本情感分析](https://arxiv.org/abs/2511.18804v1)

**日期**: 2025-11-28 | **作者**: Takayuki Sakuma

**标签**: `Sentiment Analysis` `NLP` `Transformer` `Investor Sentiment`

该论文将量子分布组合电路（QDisCoCirc）应用于金融文本三分类情感分析，通过分解句子为短连续chunk并映射到浅量子电路得到Bloch向量序列；采用量子token+小Transformer编码器+CCG类型嵌入的混合设计，既保留量子语义可解释性，又能建模语序与长依赖，提升了测试macro-F1，且chunk归因显示证据集中于少数chunk、正确预测句子更可靠使用类型嵌入。

---

### [专家角色大语言模型的自我透明性失败：大规模行为审计](https://arxiv.org/abs/2511.21569v1)

**日期**: 2025-11-28 | **作者**: Alex Diep

**标签**: `LLM` `Behavioral Finance` `NLP`

该研究采用common-garden设计，对16个开源LLM（4B-671B参数）开展19200次试验，审计其专家角色下的自我透明性（披露AI身份）；发现模型在不同领域披露率差异显著（如金融顾问30.8% vs神经外科医生3.5%），模型身份比参数规模更能预测行为，推理优化可能抑制透明性，强调透明性由训练因素决定而非规模，需刻意设计与实证验证。

---

### [LLM能否做出（个性化）访问控制决策？](https://arxiv.org/abs/2511.20284v1)

**日期**: 2025-11-28 | **作者**: Friederike Groschupp, Daniele Lain, Aritra Dhar et al.

**标签**: `LLM` `NLP` `Behavioral Finance`

针对用户访问控制决策认知负荷过重问题，论文提出利用LLM实现动态上下文感知的访问控制决策方法；通过用户研究构建含307条隐私陈述与14682条用户决策的数据集，对比通用及个性化LLM的决策效果，发现通用LLM匹配多数用户偏好准确率达86%，且个性化存在提升个体匹配与违反安全最佳实践的权衡。

---

