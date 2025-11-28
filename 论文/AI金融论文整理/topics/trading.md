# Trading & Microstructure

交易策略、市场微观结构与高频交易

> 共收录 **5** 篇论文 | [返回索引](../README.md)

---

### [匹配市场中的限价订单簿动态：微观结构、价差与执行滑点](https://arxiv.org/abs/2511.20606v2)

**日期**: 2025-11-28 | **作者**: Yao Wu

**标签**: `Market Microstructure` `Execution` `Behavioral Finance`

本文针对传统匹配市场模型假设货币转移可弥补效用差异但实证存在结构性偏好缺口的问题，引入基于刚性买卖价差的限价订单簿系统微观结构框架，用潜在偏好状态矩阵刻画个体偏好；建立阈值不可能定理并提出动态离散选择执行模型，数值实验验证持续滑点等现象，统一解释匹配失败、补偿低效等问题。

---

### [带流动性迁移的霍克斯驱动订单簿动力学的扩散极限](https://arxiv.org/abs/2511.18117v1)

**日期**: 2025-11-28 | **作者**: Levon Mahseredjian

**标签**: `Market Microstructure` `High Frequency` `Algorithmic Trading`

论文构建了多元霍克斯过程驱动的限价订单簿介观模型，引入相邻价格水平间流动性迁移事件（强度由霍克斯结构控制），从微观订单流出发推导扩散近似，得到反映队列容量的介观反射随机微分方程系统，建立了高频事件模型与市场微观结构宏观随机描述的数学桥梁。

---

### [HJM约束下带神经滤波器的无套利债券及收益率曲线预测](https://arxiv.org/abs/2511.17892v1)

**日期**: 2025-11-28 | **作者**: Xiang Gao, Cody Hyndman

**标签**: `Deep Learning` `Time Series` `Asset Pricing` `Market Microstructure`

本文基于Heath-Jarrow-Morton（HJM）期限结构模型和动态Nelson-Siegel前向利率参数化，开发无套利深度学习框架；通过结合卡尔曼/扩展卡尔曼/粒子滤波器与LSTM/CLSTM嵌入无套利漂移约束，训练中引入显式套利误差正则化（AER）项；实证应用于美债和企业债数据，显示该正则化在短期限（尤5天预测）提升预测性能，增强市场一致性并降低误差。

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

