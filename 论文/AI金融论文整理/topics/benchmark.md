# Benchmark & Evaluation

金融AI基准测试与模型评估

> 共收录 **22** 篇论文 | [返回索引](../README.md)

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

### [PEFT-Bench：一种参数高效微调方法基准](https://arxiv.org/abs/2511.21285v1)

**日期**: 2025-11-28 | **作者**: Robert Belanec, Branislav Pecher, Ivan Srba et al.

**标签**: `LLM` `NLP` `Benchmark`

针对大语言模型（LLM）微调成本高且现有参数高效微调（PEFT）方法评估存在局限的问题，论文提出PEFT-Bench统一端到端基准，覆盖27个NLP数据集和6种PEFT方法；同时引入PSCP指标，综合可训练参数、推理速度与训练内存等因素评估PEFT方法。

---

### [Transformer中的方向优化不对称性：一种合成压力测试](https://arxiv.org/abs/2511.19997v1)

**日期**: 2025-11-28 | **作者**: Mihir Sahasrabudhe

**标签**: `Transformer` `Benchmark` `Deep Learning` `LLM`

论文设计了完全合成、熵控制的基准（基于可调分支因子K的随机字符串映射），构建零条件熵的前向任务与解析熵下限的反向任务；发现即使无语言先验等语义信息，GPT-2等Transformer存在强方向优化差距（远大于MLP），预训练初始化不消除该差距，LoRA在高熵反向映射遇容量墙，隔离了因果Transformer训练固有的方向摩擦特征。

---

### [机器精度下的算子学习](https://arxiv.org/abs/2511.19980v1)

**日期**: 2025-11-28 | **作者**: Aras Bacho, Aleksei G. Sorokin, Xianjin Yang et al.

**标签**: `Deep Learning` `Benchmark`

针对神经算子学习复杂度提升但精度难显著提升的问题，本文提出CHONKNORIS方法，基于牛顿类方法回归Tikhonov正则化牛顿-Kantorovich更新关联椭圆算子的Cholesky因子，通过收缩映射实现机器精度，且所需精度低于端到端解算子近似，在多类非线性正反问题中验证有效。

---

### [混合类型数据的聚类方法：一项比较研究](https://arxiv.org/abs/2511.19755v1)

**日期**: 2025-11-28 | **作者**: Badih Ghattas, Alvaro Sanchez San-Benito

**标签**: `Benchmark` `Factor Mining`

该研究系统比较混合类型数据的聚类方法，涵盖k-prototypes等距离类方法及KAMILA等概率类方法；通过模拟实验分析簇数量、重叠度等因素对性能的影响，发现KAMILA、LCM、k-prototypes表现最优，且所有方法均有R包实现。

---

### [理解Transformer学习潜在结构的阶段性动态](https://arxiv.org/abs/2511.19328v1)

**日期**: 2025-11-28 | **作者**: Rohan Saha, Farzane Aminmansour, Alona Fyshe

**标签**: `Transformer` `Benchmark` `Deep Learning` `LLM`

本文使用Alchemy基准，训练仅解码器Transformer并在三类任务（推断缺失规则、组合简单规则解决多步序列、分解复杂例子推断中间步骤）上研究其潜在结构学习的动态；发现模型分阶段掌握能力（先学粗粒度规则再学完整结构），且存在“能稳健组合基本规则但难分解复杂例子发现规则”的关键不对称性，为理解Transformer的潜在结构学习提供了细粒度视角。

---

### [面向问题的时间序列异常检测评估指标分类](https://arxiv.org/abs/2511.18739v1)

**日期**: 2025-11-28 | **作者**: Kaixiang Yang, Jiarong Liu, Yupeng Song et al.

**标签**: `Anomaly` `Time Series` `Benchmark`

本文针对时间序列异常检测评估的挑战，提出面向问题的指标分类框架，将20余种常用指标按6个维度（如基本准确率、时效性、标签不精确容忍度等）分类；通过实验量化各指标区分有效检测与随机噪声的能力，揭示指标适用性需与任务目标对齐，为评估提供统一分析视角。

---

### [打破安全-能力权衡：带可验证奖励的强化学习在大语言模型中维持安全护栏](https://arxiv.org/abs/2511.21050v1)

**日期**: 2025-11-28 | **作者**: Dongkyu Derek Cho, Huan Song, Arijit Ghosh Chowdhury et al.

**标签**: `LLM` `Reinforcement Learning` `Transformer` `Benchmark`

论文指出大语言模型微调存在安全-能力权衡，现有SFT、RLHF等方法无法避免；首次对带可验证奖励的强化学习（RLVR）进行理论与实证分析，推导KL约束下安全漂移上界并证明消除安全退化的条件，实验显示RLVR可同时提升推理能力与安全护栏，挑战了必然权衡的假设。

---

### [探寻优度函数：前向-前向算法优度函数的大规模基准测试](https://arxiv.org/abs/2511.18567v1)

**日期**: 2025-11-28 | **作者**: Arya Shah, Vaibhav Tripathi

**标签**: `Deep Learning` `Benchmark`

该论文针对前向-前向（FF）算法的优度函数，在4个标准图像数据集上对21种不同优度函数进行大规模基准测试，评估分类准确率、能耗及碳足迹；发现部分替代优度函数显著优于默认平方和指标，且存在预测性能与环境成本的权衡，证明优度函数是FF设计的关键超参数，并开源代码供复现。

---

### [论大语言模型天生规划能力的局限性](https://arxiv.org/abs/2511.21591v1)

**日期**: 2025-11-28 | **作者**: Charles Schepanowski, Charles Ling

**标签**: `LLM` `NLP` `Benchmark`

该研究以经典8-puzzle任务（无需外部工具）测试大语言模型（LLM）的规划与状态推理能力，在不同提示条件及反馈下评估多模型表现；发现无外部工具时LLM规划能力存在显著局限（状态表示脆弱、启发式规划弱），指出需显式状态维护与结构化搜索机制提升规划能力。

---

### [MADRA：面向风险感知具身规划的多智能体辩论框架](https://arxiv.org/abs/2511.21460v1)

**日期**: 2025-11-28 | **作者**: Junjian Wang, Lidan Zhao, Xi Sheryl Zhang

**标签**: `LLM` `Risk Management` `Benchmark`

针对具身AI任务规划中现有方法计算成本高或过度拒绝的问题，提出无训练的MADRA多智能体辩论风险评估框架，通过多个LLM代理辩论指令安全性、关键评估者打分及迭代共识投票，减少误拒并保持危险任务敏感性；还引入分层认知协作规划框架提升任务成功率，贡献SafeAware-VH基准数据集，实验验证其性能优于现有方法。

---

### [考虑负责任AI的大语言模型越狱攻击防御](https://arxiv.org/abs/2511.18933v1)

**日期**: 2025-11-28 | **作者**: Ryan Wong, Hosea David Yu Fei Ng, Dhananjai Sharma et al.

**标签**: `LLM` `Deep Learning` `Transformer` `Benchmark`

该文系统分类现有大语言模型（LLM）越狱防御的三类干预（提示层、模型层、训练时），提出三个防御策略——提示层防御框架、基于logit的推理时引导防御、基于MetaGPT的领域特定Agent防御；实验表明攻击成功率显著下降，Agent防御可完全缓解攻击，同时指出防御需权衡安全、性能与可扩展性。

---

### [从代码基础模型到智能体与应用：代码智能实用指南](https://arxiv.org/abs/2511.18538v1)

**日期**: 2025-11-28 | **作者**: Jian Yang, Wei Zhang, Shark Liu et al.

**标签**: `LLM` `Transformer` `Reinforcement Learning` `Benchmark`

论文系统梳理代码大语言模型（LLM）的全生命周期（含数据整理、预训练、微调、强化学习等），分析通用及代码专用LLM的能力与技术权衡，指出学术研究与实际部署的差距并映射实用研究方向，还开展系列实验验证。

---

### [CostNav：具身智能体成本感知评估的导航基准](https://arxiv.org/abs/2511.20216v1)

**日期**: 2025-11-28 | **作者**: Haebin Seong, Sungmin Kim, Minchan Kim et al.

**标签**: `Benchmark` `Financial Agent` `Deep Learning`

现有导航基准忽略商业部署的经济可行性，论文提出首个成本感知导航基准CostNav，基于行业参数建模全生命周期成本（硬件、训练、能源、维护等）与收入（含服务等级协议SLA）；定量揭示任务成功优化与商业可行的差距，基线虽有43% SLA合规但亏损（碰撞维护占99.7%成本），并建立多类导航方法的评估基础。

---

### [构建与基准测试：面向基于文本的钓鱼和垃圾邮件检测框架的带标签邮件数据集](https://arxiv.org/abs/2511.21448v1)

**日期**: 2025-11-28 | **作者**: Rebeka Toth, Tamas Bisztray, Richard Dubniczky

**标签**: `LLM` `NLP` `Sentiment Analysis` `Benchmark`

本研究构建了包含钓鱼、垃圾邮件及合法邮件（明确区分人类与LLM生成内容）的综合带标签数据集，标注类别、情感诉求及动机；通过基准测试筛选可靠LLM标注全数据集，评估其在原始与重写邮件上的检测性能，发现钓鱼检测能力较强但垃圾邮件与合法邮件区分存挑战，开源相关代码与资源。

---

### [Semantic-KG：利用知识图谱构建语义相似度测量基准](https://arxiv.org/abs/2511.19925v1)

**日期**: 2025-11-28 | **作者**: Qiyao Wei, Edward Morrell, Lea Goetz et al.

**标签**: `LLM` `NLP` `Benchmark` `Graph Neural Network`

该论文针对现有语义相似度方法侧重语法词汇而非语义、基准存在成本高/领域有限等问题，提出基于知识图谱生成多领域（含金融）语义相似/不相似自然语言对的基准构建方法；通过对比传统NLP方法与LLM-as-judge，发现语义变异子类型和领域会影响方法性能，无方法一致最优，为LLM语义检测应用提供启示。

---

### [ToolOrchestra：通过高效模型与工具编排提升智能](https://arxiv.org/abs/2511.21689v1)

**日期**: 2025-11-28 | **作者**: Hongjin Su, Shizhe Diao, Ximing Lu et al.

**标签**: `LLM` `Reinforcement Learning` `Benchmark`

论文提出ToolOrchestra方法，通过结合结果、效率及用户偏好的强化学习训练小型编排器（8B模型），协调智能工具解决复杂任务；该编排器在HLE等基准上比GPT-5准确率更高、成本更低（如HLE得分37.1%超GPT-5的35.1%且效率2.5x），实现性能与成本的最优权衡，还能泛化到未见过的工具。

---

