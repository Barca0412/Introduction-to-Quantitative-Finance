# Derivatives

衍生品定价与波动率建模

> 共收录 **7** 篇论文 | [返回索引](../README.md)

---

### [资产量子网络：市场相关性与结构风险的非经典框架](https://arxiv.org/abs/2511.21515v1)

**日期**: 2025-11-28 | **作者**: Hui Gong, Akash Sharma, Francesca Medda

**标签**: `Risk Management` `Anomaly` `Volatility`

该论文针对经典相关矩阵无法捕捉高阶非线性及状态依赖交互的问题，引入基于密度矩阵的资产量子网络（QNA）框架，利用量子信息数学结构描述市场组织；定义纠缠风险指数（ERI）和量子预警信号（QEWS）两类结构指标，通过NASDAQ-100数据验证其在市场结构分析与风险预警中的优势，如ERI在结构收紧时上升、QEWS可提前显示事件前的结构张力变化。

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

### [连续时间下含比例交易成本的超对冲问题](https://arxiv.org/abs/2511.18169v1)

**日期**: 2025-11-28 | **作者**: Atiqah Almuzaini, Çağın Ararat, Jin Ma

**标签**: `Risk Management` `Options` `Portfolio Optimization`

本文利用集值随机分析工具重新研究连续时间下含比例交易成本的超对冲问题，基于Black-Scholes型中间价市场模型定义动态超对冲集族并以集值积分表示，证明其为多组合时间一致的动态集值风险测度；进一步在路径空间引入带预定误差的近似超对冲集，通过集值Bellman原理关联不同时间的近似集，为刻画超对冲集的集值微分结构奠定基础。

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

