# Trading & Microstructure

交易策略、市场微观结构与高频交易

> 共收录 **19** 篇论文 | [返回索引](../README.md)

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

### [自动去杠杆（ADL）：不可能定理与优化](https://arxiv.org/abs/2512.01112v1)

**日期**: 2025-12-02 | **作者**: Tarun Chitra

**标签**: `Risk Management` `Market Microstructure` `Algorithmic Trading`

该论文首次构建永续期货自动去杠杆（ADL）的严格模型，证明ADL机制存在交易所偿付能力、收入与交易者公平性的三难困境；构造三类最优ADL机制以平衡该困境，并通过Hyperliquid数据集实证发现现有生产机制过度使用ADL，给盈利交易者造成大量不必要损失。

---

### [稳定币市场政治风险的预警信号：2024年美国大选前后的人类与算法行为](https://arxiv.org/abs/2512.00893v1)

**日期**: 2025-12-02 | **作者**: Kundan Mukhia, Buddha Nath Sharma, Salam Rabindrajit Luwang et al.

**标签**: `Risk Management` `Behavioral Finance` `Algorithmic Trading` `Time Series`

本文以2024年美国大选为政治风险事件，区分人类驱动的P2P稳定币交易与算法活动，通过结构突变分析、替代基检验等方法发现，人类驱动的ERC-20交易在大选前2天出现变化，早于交易所交易量（大选日）和算法智能合约活动（2025年1月）；结合能量谱分析与结构向量自回归验证，人类驱动的稳定币流动可作为政治压力的预警指标。

---

### [油气行业勘探阶段信息资产投资策略优化：一种强化学习方法](https://arxiv.org/abs/2512.00243v1)

**日期**: 2025-12-02 | **作者**: Paulo Roberto de Melo Barros Junior, Monica Alexandra Vilar Ribeiro De Meireles, Jose Luis Lima de Jesus Silva

**标签**: `Reinforcement Learning` `Portfolio Optimization` `Market Microstructure` `Asset Pricing`

本文采用多智能体深度强化学习（DRL）框架，对比油气勘探中传统阶梯式策略与优先早期高质量信息资产的策略，发现前端加载信息投资可降低冗余数据成本、提升储量估值精度；研究还揭示最优投资时机依赖市场竞争而非仅价格波动，竞争环境中能缓解赢家诅咒，开发阶段收益更显著。

---

### [带摩擦的路径依赖期权定价与对冲的Signature方法](https://arxiv.org/abs/2511.23295v1)

**日期**: 2025-12-01 | **作者**: Eduardo Abi Jaber, Donatien Hainaut, Edouard Motte

**标签**: `Options` `Asset Pricing` `Risk Management` `Market Microstructure`

本文引入带摩擦的路径依赖期权定价与对冲的Signature方法，基于均值二次变差准则将非线性非马尔可夫随机控制问题转化为可处理形式，得到线性反馈形式的对冲策略，系数由扩展张量代数上的非标准无限维Riccati方程刻画；数值实验表明该策略有效，市场冲击使最优交易策略平滑，低截断Signature近似在摩擦市场中准确鲁棒。

---

### [期权市场中依赖β的伽马反馈与内生波动率放大](https://arxiv.org/abs/2511.22766v1)

**日期**: 2025-12-01 | **作者**: Haoying Dai

**标签**: `Volatility` `Options` `Market Making` `Market Microstructure`

论文构建理论框架，连接微观期权对冲、股票特定因子暴露与宏观市场动荡，解释伽马挤压事件中的内生波动率放大；通过显式建模做市商delta中性对冲并纳入β依赖的波动率归一化，推导伽马挤压发生的稳定性条件，捕捉做市商对冲与价格变动的非线性递归反馈及自我强化动态。

---

### [基于自适应决斗双深度Q网络与Mamba的Uniswap V3复制与扩展](https://arxiv.org/abs/2511.22101v1)

**日期**: 2025-12-01 | **作者**: Zhaofeng Zhang

**标签**: `Reinforcement Learning` `Market Making` `Deep Learning` `Algorithmic Trading`

论文首先完成了Uniswap V3自适应流动性提供深度强化学习论文的复制，涵盖Uniswap子图数据获取、实现细节及结果分析；随后提出结合Mamba与双深度Q网络（DDQN）并设计新奖励函数的改进模型，引入两个新基准对比，该模型理论支撑更强且部分测试表现更优。

---

### [GSpaRC：用于实时射频信道重建的高斯喷溅方法](https://arxiv.org/abs/2511.22793v1)

**日期**: 2025-12-01 | **作者**: Bhavya Sai Nukapotula, Rishabh Tripathi, Seth Pregler et al.

**标签**: `Deep Learning` `High Frequency`

针对无线通信中信道状态信息（CSI）获取开销大且现有重建方法延迟较高的问题，提出GSpaRC算法，首次突破1ms延迟屏障并保持高精度；该算法采用带距离衰减等物理特征的轻量神经模型参数化3D高斯基元表示射频环境，通过等距投影模拟全向天线，自定义CUDA pipeline实现多维度并行处理以提升实时性。

---

### [基于单次概率前向传播和代码生成的贝叶斯神经网络加速执行](https://arxiv.org/abs/2511.23440v1)

**日期**: 2025-12-01 | **作者**: Bernhard Klein, Falk Selker, Hendrik Borras et al.

**标签**: `Deep Learning` `Execution`

该论文针对贝叶斯神经网络（BNN）因多次采样导致计算成本高的问题，提出基于单次概率前向传播（PFP）的方法——假设权重和激活为高斯分布，用单次确定性前向传播替代随机变分推断（SVI）的多次采样；结合TVM深度学习编译器实现端到端训练、编译优化及嵌入式ARM CPU部署 pipeline，实验表明PFP-BNN在小批量下最高可实现4200x加速，且在Dirty-MNIST任务的准确率、不确定性估计和OOD检测上与SVI-BNN相当。

---

### [桥接规划与执行：真实世界截止时间下的多智能体路径规划](https://arxiv.org/abs/2511.21886v1)

**日期**: 2025-12-01 | **作者**: Jingtian Yan, Shuai Zhou, Stephen F. Smith et al.

**标签**: `Execution` `Deep Learning` `Benchmark`

现有多智能体路径规划（MAPF）多忽略执行时因素（如运动学约束、通信延迟），针对真实截止时间场景的差距，论文提出REMAP框架，通过ExecTimeNet准确估计路径执行时间，集成到MAPF-LNS、CBS等主流方法解决MAPF-RD问题，实验显示解质量提升最多20%。

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

### [设计制造数据交易市场的声誉系统：结合Q学习和IRL估计效用的多智能体评估](https://arxiv.org/abs/2511.19930v1)

**日期**: 2025-11-28 | **作者**: Kenta Yamamoto, Teruaki Hayashi

**标签**: `Financial Agent` `Reinforcement Learning` `Market Microstructure` `Asset Pricing`

论文针对制造数据交易市场的信息不对称问题，开发了集成强化学习（Q学习）与逆强化学习（IRL）的多智能体模拟器，评估五种声誉系统的市场效果并提出融合优势的混合机制，以提升数据价格与质量的对齐度。

---

### [论AI算法进步的起源](https://arxiv.org/abs/2511.21622v1)

**日期**: 2025-11-28 | **作者**: Hans Gundlach, Alex Fogelson, Jayson Lynch et al.

**标签**: `Transformer` `Deep Learning` `LLM` `Algorithmic Trading`

论文通过小尺度消融实验、文献调查及缩放实验发现，2012-2023年AI训练FLOP效率提升的大部分（6930倍）来自算法的尺度依赖改进（如LSTM到Transformer的compute-optimal scaling law指数差异），而非小模型算法创新；指出此前对算法进步的估计高估了小模型贡献，算法效率度量强依赖参考尺度。

---

### [数据流中分类器投票线性独立性视角下的集成性能研究](https://arxiv.org/abs/2511.21465v1)

**日期**: 2025-11-28 | **作者**: Enes Bektas, Fazli Can

**标签**: `Algorithmic Trading` `Time Series` `Anomaly`

本文从数据流中分类器投票的线性独立性视角，研究集成规模与性能的关系，推导了达到指定线性独立概率所需集成规模的理论估计；通过OzaBagging和GOOWE等集成方法在真实及合成数据集上验证，发现该估计可有效识别鲁棒集成的性能饱和点，且复杂加权方案的高理论多样性可能引发算法不稳定。

---

