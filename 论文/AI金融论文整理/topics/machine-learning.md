# Machine Learning

机器学习在量化金融中的应用，包括深度学习、强化学习、图神经网络、Transformer等

> 共收录 **18** 篇论文 | [返回索引](../README.md)

---

### [基于迁移学习的投资组合优化](https://arxiv.org/abs/2511.21221v1)

**日期**: 2025-11-28 | **作者**: Kexin Wang, Xiaomeng Zhang, Xinyu Zhang

**标签**: `Portfolio Optimization` `Deep Learning`

论文针对资产市场存在共享信息特征的特点，提出基于迁移学习的投资组合策略，通过前向验证利用跨市场信息提升目标市场投资表现；该策略可渐近识别有效数据集，选择性纳入有效信息并丢弃误导信息，渐近实现最大夏普比率；数值与案例研究（A股H股双重上市股票、美国各行业股票）验证了其良好性能。

---

### [不完全市场中欧式期权定价与对冲的约束深度学习方法](https://arxiv.org/abs/2511.20837v1)

**日期**: 2025-11-28 | **作者**: Nicolas Baradel

**标签**: `Deep Learning` `Options` `Asset Pricing` `Volatility`

针对不完全市场中欧式期权定价与对冲无唯一无套利解的问题，论文提出约束深度学习方法，用单个神经网络表示期权价格函数（梯度为对冲策略），通过损失函数约束自融资条件；为解决期权收益非光滑与神经网络光滑性冲突，设计嵌入终端收益约束的架构，实验验证其在不同非光滑期权及跳跃场景下P&L分布更优，整合边界约束提升了机器学习在量化金融中的应用。

---

### [自激发索赔下的最优分红与资本注入](https://arxiv.org/abs/2511.19701v1)

**日期**: 2025-11-28 | **作者**: Paulin Aubert, Etienne Chevalier, Vathana Ly Vath

**标签**: `Reinforcement Learning` `Risk Management` `Portfolio Optimization` `Benchmark`

本文研究自激发索赔（Hawkes过程）下Cramér-Lundberg模型的最优分红与资本注入问题，建立价值函数分析性质并以显式阈值刻画最优资本注入策略，证明其为HJB变分不等式的唯一粘性解；数值上结合单调有限差分+Howard策略迭代得到基准解，提出基于策略梯度和演员-评论家的强化学习方法，学习策略匹配基准且稳定，为高维扩展提供可扩展思路。

---

### [基于量子分布组合电路（QDisCoCirc）的金融文本情感分析](https://arxiv.org/abs/2511.18804v1)

**日期**: 2025-11-28 | **作者**: Takayuki Sakuma

**标签**: `Sentiment Analysis` `NLP` `Transformer` `Investor Sentiment`

该论文将量子分布组合电路（QDisCoCirc）应用于金融文本三分类情感分析，通过分解句子为短连续chunk并映射到浅量子电路得到Bloch向量序列；采用量子token+小Transformer编码器+CCG类型嵌入的混合设计，既保留量子语义可解释性，又能建模语序与长依赖，提升了测试macro-F1，且chunk归因显示证据集中于少数chunk、正确预测句子更可靠使用类型嵌入。

---

### [重新审视金融领域的时间序列基础模型](https://arxiv.org/abs/2511.18578v1)

**日期**: 2025-11-28 | **作者**: Eghbal Rahimikia, Hao Ni, Weiguan Wang

**标签**: `Time Series` `Deep Learning` `Transformer` `Benchmark`

本文是首个全面实证研究时间序列基础模型（TSFMs）在全球金融市场表现的工作，利用大规模日度超额收益数据集对比零样本推理、微调及从头预训练与基准模型的效果；发现现成预训练TSFMs在零样本和微调场景下表现不佳，但基于金融数据从头预训练的模型在预测能力和经济收益上显著提升，且增大数据集、合成数据增强及超参调优可进一步优化性能。

---

### [长期市场模拟的随机过程](https://arxiv.org/abs/2511.18125v1)

**日期**: 2025-11-28 | **作者**: Gilles Zumbach

**标签**: `Time Series` `Portfolio Optimization` `Risk Management` `Volatility`

论文针对长期投资的战略资产配置（SAA），指出传统Bachelier模型的局限性，提出融入金融时间序列最新进展（收益负相关、异方差、厚尾及非对称分布）的多元随机过程；同时强调漂移项估计的关键影响，通过概率预测替代点预测将漂移不确定性纳入蒙特卡洛模拟，提升长期财富规划的模拟质量。

---

### [带财务目标和确定时间范围的投资组合优化强化学习方法](https://arxiv.org/abs/2511.18076v1)

**日期**: 2025-11-28 | **作者**: Fermat Leukam, Rock Stephane Koffi, Prudence Djagba

**标签**: `Reinforcement Learning` `Portfolio Optimization` `Risk Management` `Volatility`

论文提出结合G-Learning算法与GIRL算法（逆强化学习的G学习方法）的投资组合优化增强方法，目标是在目标日期前最大化投资组合价值并最小化投资者定期贡献，在高波动市场中使夏普比率从0.42提升至0.483，验证了强化学习方法的稳健优化能力。

---

### [混合LSTM与PPO网络用于动态投资组合优化](https://arxiv.org/abs/2511.17963v1)

**日期**: 2025-11-28 | **作者**: Jun Kevin, Pujianto Yugopuspito

**标签**: `Portfolio Optimization` `Reinforcement Learning` `Deep Learning` `Time Series`

论文提出融合长短期记忆网络（LSTM）预测与近端策略优化（PPO）强化学习的混合框架，利用LSTM捕捉时间依赖，PPO在连续动作空间自适应优化投资组合配置；通过2018-2024年多资产（美股、印尼股市、美债、主流加密货币）数据集评估，该框架相比等权、指数及单模型基准，在非平稳市场下收益更高、韧性更强。

---

### [一种用于风险建模中空间嵌入的多视图对比学习框架](https://arxiv.org/abs/2511.17954v1)

**日期**: 2025-11-28 | **作者**: Freek Holvoet, Christopher Blier-Wong, Katrien Antonio

**标签**: `Risk Management` `Deep Learning` `Asset Pricing`

论文提出多视图对比学习框架，整合卫星图像与OpenStreetMap等多源空间数据生成空间嵌入，训练后可直接从经纬度生成嵌入；在法国房价预测案例中，该嵌入显著提升各类模型精度，且具有可解释性与跨区域迁移性。

---

### [HJM约束下带神经滤波器的无套利债券及收益率曲线预测](https://arxiv.org/abs/2511.17892v1)

**日期**: 2025-11-28 | **作者**: Xiang Gao, Cody Hyndman

**标签**: `Deep Learning` `Time Series` `Asset Pricing` `Market Microstructure`

本文基于Heath-Jarrow-Morton（HJM）期限结构模型和动态Nelson-Siegel前向利率参数化，开发无套利深度学习框架；通过结合卡尔曼/扩展卡尔曼/粒子滤波器与LSTM/CLSTM嵌入无套利漂移约束，训练中引入显式套利误差正则化（AER）项；实证应用于美债和企业债数据，显示该正则化在短期限（尤5天预测）提升预测性能，增强市场一致性并降低误差。

---

### [RED-F：基于重构-消除的双流对比预测框架用于多元时间序列异常预测](https://arxiv.org/abs/2511.20044v1)

**日期**: 2025-11-28 | **作者**: PengYu Chen, Xiaohou Shi, Yuan Chang et al.

**标签**: `Anomaly` `Time Series` `Deep Learning`

针对多元时间序列异常预测中弱异常前兆易被正常模式淹没的问题，提出RED-F框架：含重构-消除模型（REM）通过混合时频机制生成纯净正常基线，双流对比预测模型（DFM）以基线和原始序列为并行输入，通过对比预测放大前兆信号，且DFM采用多序列预测目标利用远期上下文增强预测能力。

---

### [动态市场行为预测的深度学习模型优化](https://arxiv.org/abs/2511.19090v1)

**日期**: 2025-11-28 | **作者**: Shenghan Zhao, Yuzhen Lin, Ximeng Yang et al.

**标签**: `Deep Learning` `Time Series` `Transformer` `Benchmark`

论文聚焦电商零售SKU级多horizon（H=1、7、14）日度需求/收入预测，提出融合多尺度时序卷积、门控循环模块及时序感知自注意力的混合序列模型；经严格时间分割训练评估，模型在准确率及峰值/假期稳健性上优于传统及前沿基准模型，且通过消融实验与统计显著性检验验证可靠性并开源实现。

---

### [含未观测上下文的特定上下文因果图发现：非平稳性、机制与时空模式](https://arxiv.org/abs/2511.21537v1)

**日期**: 2025-11-28 | **作者**: Martin Rabel, Jakob Runge

**标签**: `Time Series` `Anomaly`

针对含未观测上下文的非平稳时空数据（如气候网格时间序列），论文提出模块化因果图发现框架，通过修改约束类因果算法的独立性测试层适配数据变化，可复用PC、PCMCI等现有算法并支持结合变化点检测等方法扩展。

---

### [基于贝叶斯的带动态狄利克雷先验的在线标签偏移估计](https://arxiv.org/abs/2511.18615v1)

**日期**: 2025-11-28 | **作者**: Jiawei Hu, Javier A. Barria

**标签**: `Deep Learning`

针对监督学习中标签偏移（训练与测试类先验分布差异）导致分类器性能下降的问题，论文提出FMAPLS（全最大后验标签偏移）及其在线版本online-FMAPLS，通过批量/在线EM算法联合动态优化狄利克雷超参数和类先验，克服现有MAPLS的刚性约束；引入线性替代函数（LSF）得到闭式解降低计算复杂度，在线版本用随机近似实现流数据实时适应，理论分析了收敛率与精度的权衡，实验验证方法性能更优。

---

### [带单调非线性批评者分解的多智能体交叉熵方法](https://arxiv.org/abs/2511.18671v2)

**日期**: 2025-11-28 | **作者**: Yan Wang, Ke Deng, Yongli Ren

**标签**: `Reinforcement Learning` `Deep Learning`

合作多智能体强化学习（MARL）的集中训练分散执行（CTDE）框架存在集中分散不匹配（CDM）问题，现有价值分解方法面临线性表达有限或非线性需集中梯度的权衡；论文提出带单调非线性批评者分解（NCD）的多智能体交叉熵方法（MCEM），通过提升高价值联合动作概率排除次优行为，还扩展了带修正k步回报和Retrace的离策略学习，实验表明其在连续与离散动作基准上优于当前最优方法。

---

### [MortgageLLM：带残差指令迁移、对齐调优和任务特定路由的领域自适应预训练](https://arxiv.org/abs/2511.21101v1)

**日期**: 2025-11-28 | **作者**: Manish Jain, Satheesh Kumar Ponnambalam, Salman Faroz et al.

**标签**: `LLM` `NLP` `Financial Agent` `Transformer`

论文提出抵押贷款领域专用大模型MortgageLLM，采用双轨特化框架从LLaMA-3.1-8B构建对话问答与结构化任务两个专家模型，通过指令残差技术恢复指令遵循能力并设计智能任务路由机制，在领域基准上显著优于基础模型。

---

### [定向操纵：基于斜率的金融时间序列数据攻击](https://arxiv.org/abs/2511.19330v1)

**日期**: 2025-11-28 | **作者**: Dominik Luszczynski

**标签**: `Deep Learning` `Time Series` `Anomaly` `Algorithmic Trading`

本文针对金融时间序列预测的对抗攻击研究不足问题，提出通用斜率攻击与最小二乘斜率攻击两种方法，可使N-HiTS模型的股票预测斜率翻倍；该攻击能绕过CNN判别器等标准安全机制，还可结合GAN生成逼真合成数据，同时设计样本恶意软件证明需保护模型推理全流程。

---

### [KAN与LSTM在时间序列预测中的性能比较](https://arxiv.org/abs/2511.18613v1)

**日期**: 2025-11-28 | **作者**: Tabish Ali Rather, S M Mahmudul Hasan Joy, Nadezda Sukhorukova et al.

**标签**: `Deep Learning` `Time Series` `Asset Pricing`

本文以均方根误差（RMSE）评估预测准确性与可解释性的权衡，比较Kolmogorov-Arnold网络（KAN）与长短期记忆网络（LSTM）在非确定性股票价格时间序列预测中的性能；研究发现LSTM在所有测试预测 horizon 上表现显著更优，标准KAN误差高且实用性有限，但KAN在资源受限、精度要求较低的场景下计算效率有优势，结果支持LSTM用于实际金融预测并建议持续研究专门化KAN架构。

---

