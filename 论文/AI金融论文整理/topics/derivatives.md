# Derivatives

衍生品定价与波动率建模

> 共收录 **18** 篇论文 | [返回索引](../README.md)

---

### [Option-Implied Zero-Coupon Yields: Unifying Bond and Equity Markets](https://arxiv.org/abs/2512.10823v1)

**日期**: 2025-12-15 | **作者**: Ting-Jung Lee, W. Brent Lindquist, Svetlozar T. Rachev et al.

**标签**: `Options`

---

### [Modelling and valuation of catastrophe bonds across multiple regions](https://arxiv.org/abs/2512.08890v1)

**日期**: 2025-12-15 | **作者**: Krzysztof Burnecki, Marek Teuerle, Martyna Zdeb

**标签**: `Options`

---

### [基于切比雪夫张量基和哈密顿雾后拟合的无套利期权价格曲面构建](https://arxiv.org/abs/2512.01967v1)

**日期**: 2025-12-02 | **作者**: Robert Jenkinson Alvarez

**标签**: `Options` `Asset Pricing` `Risk Management` `Volatility`

论文提出从带噪声的买卖报价构建无套利期权价格曲面的方法：全局层面用切比雪夫张量基表示曲面，将静态无套利要求转化为线性不等式，通过凸二次规划高效求解；局部层面引入基于离散风险中性密度雾和哈密顿能量的后拟合层，在保留全局无套利的同时修正噪声报价，实现高买卖价差内覆盖度与低无套利违反率。

---

### [带非线性Wasserstein投影的贝叶斯分布鲁棒Merton问题](https://arxiv.org/abs/2512.01408v1)

**日期**: 2025-12-02 | **作者**: Jose Blanchet, Jiayi Cheng, Hao Liu et al.

**标签**: `Portfolio Optimization` `Risk Management` `Volatility` `High Frequency`

论文从数据驱动的分布鲁棒视角重新研究Merton连续时间投资组合选择，针对漂移难估计但波动率可测的特点，在贝叶斯Merton模型漂移先验设置单一模糊集（避免时间矩形DRC的过度悲观），通过minimax交换转化为优化先验非线性泛函，结合Karatzas-Zhao闭式解求解；进一步用Wasserstein不确定性下渐近最优最坏情况先验和非线性投影校准模糊半径，实验显示其比DRC悲观性更低、频繁再平衡下优于近视DRO-Markowitz。

---

### [期权轮动策略决策的混合架构：用于透明交易的LLM生成贝叶斯网络](https://arxiv.org/abs/2512.01123v1)

**日期**: 2025-12-02 | **作者**: Xiaoting Kuang, Boken Lin

**标签**: `LLM` `Options` `Algorithmic Trading` `Risk Management`

论文提出LLM与贝叶斯网络结合的混合架构，用LLM构建上下文特定的贝叶斯网络（而非黑盒决策），并选择相关历史数据填充条件概率表实现透明推理；该架构通过反馈循环迭代优化，实证在期权轮动策略上获15.3%年化收益及更优风险调整表现。

---

### [基于Wasserstein距离的粗糙Bergomi模型高效校准](https://arxiv.org/abs/2512.00448v1)

**日期**: 2025-12-02 | **作者**: Changqing Teng, Guanglian Li

**标签**: `Volatility` `Options` `Asset Pricing`

针对粗糙Bergomi模型因非马尔可夫结构导致的定价与校准难题，论文提出改进的指数和（mSOE）蒙特卡洛方案，混合原点附近奇异核精确模拟与剩余部分多因子近似，实现O(n)成本下的高精度定价（尤其虚值期权）；并基于该定价引擎，以Wasserstein距离为优化目标设计分布匹配校准方案，利用Lipschitz收益的minimax公式提升鲁棒性，数值实验验证了方法有效性及对路径依赖期权的泛化能力。

---

### [基于LIME可解释性的电力价格预测机器学习算法比较研究](https://arxiv.org/abs/2512.01212v1)

**日期**: 2025-12-02 | **作者**: Xuanyi Zhao, Jiawen Ding, Xueting Huang et al.

**标签**: `Time Series` `Volatility` `Factor Mining`

本研究针对电力市场价格波动加剧的问题，采用西班牙电力市场的消费、发电及气象多变量数据，对比8种机器学习模型（含线性回归、随机森林、XGBoost等）的电价预测性能，发现KNN表现最优；同时通过LIME可解释性分析，揭示气象因素和供需指标对电价波动的非线性影响机制，提升了预测决策的透明度。

---

### [带摩擦的路径依赖期权定价与对冲的Signature方法](https://arxiv.org/abs/2511.23295v1)

**日期**: 2025-12-01 | **作者**: Eduardo Abi Jaber, Donatien Hainaut, Edouard Motte

**标签**: `Options` `Asset Pricing` `Risk Management` `Market Microstructure`

本文引入带摩擦的路径依赖期权定价与对冲的Signature方法，基于均值二次变差准则将非线性非马尔可夫随机控制问题转化为可处理形式，得到线性反馈形式的对冲策略，系数由扩展张量代数上的非标准无限维Riccati方程刻画；数值实验表明该策略有效，市场冲击使最优交易策略平滑，低截断Signature近似在摩擦市场中准确鲁棒。

---

### [影响加密货币价格的因素：来自比特币、以太坊、达世币、莱特币和门罗币的证据](https://arxiv.org/abs/2511.22782v1)

**日期**: 2025-12-01 | **作者**: Yhlas Sovbetov

**标签**: `Asset Pricing` `Factor Model` `Time Series` `Volatility`

本文采用ARDL技术，基于2010-2018年周度数据，分析五种主流加密货币价格的影响因素；发现加密市场相关因素对其长短周期均显著，吸引力仅长期显著，SP500存在长短周期异质性影响，且各货币存在长期均衡及特定收敛速度。

---

### [期权市场中依赖β的伽马反馈与内生波动率放大](https://arxiv.org/abs/2511.22766v1)

**日期**: 2025-12-01 | **作者**: Haoying Dai

**标签**: `Volatility` `Options` `Market Making` `Market Microstructure`

论文构建理论框架，连接微观期权对冲、股票特定因子暴露与宏观市场动荡，解释伽马挤压事件中的内生波动率放大；通过显式建模做市商delta中性对冲并纳入β依赖的波动率归一化，推导伽马挤压发生的稳定性条件，捕捉做市商对冲与价格变动的非线性递归反馈及自我强化动态。

---

### [资产量子网络：市场相关性与结构风险的非经典框架](https://arxiv.org/abs/2511.21515v2)

**日期**: 2025-12-01 | **作者**: Hui Gong, Akash Sedai, Francesca Medda

**标签**: `Risk Management` `Anomaly` `Volatility`

论文提出资产量子网络（QNA）框架，基于量子信息密度矩阵突破经典相关矩阵的线性pairwise局限，捕捉资产间非线性、高阶及状态依赖的依赖关系；定义纠缠风险指数（ERI）和量子预警信号（QEWS），通过NASDAQ-100数据验证其能识别经典工具无法捕捉的结构风险与依赖几何。

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

