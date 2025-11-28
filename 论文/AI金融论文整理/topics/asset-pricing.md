# Asset Pricing

资产定价、因子模型与市场异象研究

> 共收录 **14** 篇论文 | [返回索引](../README.md)

---

### [资产量子网络：市场相关性与结构风险的非经典框架](https://arxiv.org/abs/2511.21515v1)

**日期**: 2025-11-28 | **作者**: Hui Gong, Akash Sharma, Francesca Medda

**标签**: `Risk Management` `Anomaly` `Volatility`

该论文针对经典相关矩阵无法捕捉高阶非线性及状态依赖交互的问题，引入基于密度矩阵的资产量子网络（QNA）框架，利用量子信息数学结构描述市场组织；定义纠缠风险指数（ERI）和量子预警信号（QEWS）两类结构指标，通过NASDAQ-100数据验证其在市场结构分析与风险预警中的优势，如ERI在结构收紧时上升、QEWS可提前显示事件前的结构张力变化。

---

### [重心最优传输问题的动态刻画及其鞅松弛](https://arxiv.org/abs/2511.21287v1)

**日期**: 2025-11-28 | **作者**: Ivan Guo, Severin Nilsson, Johannes Wiesel

**标签**: `Asset Pricing` `Risk Management`

本文将经典最优传输的Benamou-Brenier公式扩展至弱最优传输，得到重心最优传输问题的动态刻画；同时研究该问题的鞅松弛，建立其与鞅Benamou-Brenier公式的关联。

---

### [不完全市场中欧式期权定价与对冲的约束深度学习方法](https://arxiv.org/abs/2511.20837v1)

**日期**: 2025-11-28 | **作者**: Nicolas Baradel

**标签**: `Deep Learning` `Options` `Asset Pricing` `Volatility`

针对不完全市场中欧式期权定价与对冲无唯一无套利解的问题，论文提出约束深度学习方法，用单个神经网络表示期权价格函数（梯度为对冲策略），通过损失函数约束自融资条件；为解决期权收益非光滑与神经网络光滑性冲突，设计嵌入终端收益约束的架构，实验验证其在不同非光滑期权及跳跃场景下P&L分布更优，整合边界约束提升了机器学习在量化金融中的应用。

---

### [Heston模型下的高效重要性采样：短到期与深度虚值期权](https://arxiv.org/abs/2511.19826v1)

**日期**: 2025-11-28 | **作者**: Yun-Feng Tu, Chuan-Hsiang Han

**标签**: `Volatility` `Options` `Asset Pricing` `Benchmark`

论文针对Heston模型下短到期和深度虚值这两个稀有事件场景，基于大偏差原理设计状态依赖的测度变换；短到期 regime证明所提重要性采样漂移达对数效率（渐近最优），深度虚值 regime引入慢均值回复 scaling并通过Riccati分析验证最优性，数值实验显示方差降低超几个数量级。

---

### [含部分信息的随机因子模型下碳惩罚型投资组合保险策略](https://arxiv.org/abs/2511.19186v1)

**日期**: 2025-11-28 | **作者**: Katia Colaneri, Federico D'Amario, Daniele Mancinelli

**标签**: `Factor Model` `Portfolio Optimization` `Risk Management` `Volatility`

论文将碳惩罚融入比例投资组合保险（PPI）策略，以降低碳足迹并平衡风险收益；用含不可观测随机因子的几何布朗运动建模风险资产，结合随机滤波理论求解CRRA效用下的最优策略，量化信息不完全的效用损失，数值分析显示策略可降碳排放强度且不损害财务表现。

---

### [考虑利息成本与税盾的债务回收校准模型：不同财政制度及辖区下的可行性](https://arxiv.org/abs/2511.18614v1)

**日期**: 2025-11-28 | **作者**: Carlo von der Osten, Sabrina Aufiero, Pierpaolo Vivo et al.

**标签**: `Asset Pricing` `Risk Management` `Portfolio Optimization`

论文提出一个新框架，建模股权与抵押贷款动态并纳入抵押贷款利率、股权信贷成本及利息抵扣税盾，通过澳大利亚、德国、瑞士三个辖区校准发现：正利率无税盾会缩小成功区域、延长还款时间，税盾可部分逆转该影响；且租赁房产因税盾规定持续优于自住房产。

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

### [面向污染训练数据的自适应激进拒绝异常检测方法](https://arxiv.org/abs/2511.21378v1)

**日期**: 2025-11-28 | **作者**: Jungi Lee, Jungkwon Kim, Chi Zhang et al.

**标签**: `Anomaly` `Risk Management` `Benchmark`

传统异常检测模型假设训练数据为纯正常数据，但污染数据会严重影响性能，现有方法依赖固定污染率易因实际比例偏差失效；论文提出自适应激进拒绝（AAR）方法，通过改进z-score和高斯混合模型阈值动态排除异常，结合软硬拒绝策略平衡正常数据保留与异常排除；实验表明AAR在多数据集上优于现有SOTA方法，增强污染数据鲁棒性，支持安全、医疗等领域应用。

---

### [RED-F：基于重构-消除的双流对比预测框架用于多元时间序列异常预测](https://arxiv.org/abs/2511.20044v1)

**日期**: 2025-11-28 | **作者**: PengYu Chen, Xiaohou Shi, Yuan Chang et al.

**标签**: `Anomaly` `Time Series` `Deep Learning`

针对多元时间序列异常预测中弱异常前兆易被正常模式淹没的问题，提出RED-F框架：含重构-消除模型（REM）通过混合时频机制生成纯净正常基线，双流对比预测模型（DFM）以基线和原始序列为并行输入，通过对比预测放大前兆信号，且DFM采用多序列预测目标利用远期上下文增强预测能力。

---

### [含未观测上下文的特定上下文因果图发现：非平稳性、机制与时空模式](https://arxiv.org/abs/2511.21537v1)

**日期**: 2025-11-28 | **作者**: Martin Rabel, Jakob Runge

**标签**: `Time Series` `Anomaly`

针对含未观测上下文的非平稳时空数据（如气候网格时间序列），论文提出模块化因果图发现框架，通过修改约束类因果算法的独立性测试层适配数据变化，可复用PC、PCMCI等现有算法并支持结合变化点检测等方法扩展。

---

### [基于LLM驱动的代码进化的认知阿尔法挖掘](https://arxiv.org/abs/2511.18850v1)

**日期**: 2025-11-28 | **作者**: Fengyuan Liu, Huang Yi, Sichun Luo et al.

**标签**: `LLM` `Factor Mining` `Asset Pricing` `Algorithmic Trading`

针对现有阿尔法挖掘方法搜索空间狭窄、模型不透明或经济依据不足等问题，本文提出CogAlpha框架，融合代码级阿尔法表示、LLM驱动推理与进化搜索，通过多阶段提示和金融反馈迭代优化候选阿尔法；在A股市场的实验表明，该框架挖掘的阿尔法在预测精度、鲁棒性和泛化性上均优于现有方法。

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

