# Asset Pricing

资产定价、因子模型与市场异象研究

> 共收录 **59** 篇论文 | [返回索引](../README.md)

---

### [基于切比雪夫张量基和哈密顿雾后拟合的无套利期权价格曲面构建](https://arxiv.org/abs/2512.01967v1)

**日期**: 2025-12-02 | **作者**: Robert Jenkinson Alvarez

**标签**: `Options` `Asset Pricing` `Risk Management` `Volatility`

论文提出从带噪声的买卖报价构建无套利期权价格曲面的方法：全局层面用切比雪夫张量基表示曲面，将静态无套利要求转化为线性不等式，通过凸二次规划高效求解；局部层面引入基于离散风险中性密度雾和哈密顿能量的后拟合层，在保留全局无套利的同时修正噪声报价，实现高买卖价差内覆盖度与低无套利违反率。

---

### [极端风险预测的不平衡鲁棒评估框架](https://arxiv.org/abs/2512.00916v1)

**日期**: 2025-12-02 | **作者**: Sotirios D. Nikolopoulos

**标签**: `Risk Management` `Anomaly`

传统稀有事件预测指标因类别不平衡导致阈值退化，论文提出稀有事件稳定（RES）指标家族，其最优阈值在事件概率趋近零时仍保持内部；模拟及信用违约应用验证RES指标具有稳定阈值、一致模型排名及 prevalence不变性，为极端风险预测提供鲁棒评估框架。

---

### [基于Wasserstein距离的粗糙Bergomi模型高效校准](https://arxiv.org/abs/2512.00448v1)

**日期**: 2025-12-02 | **作者**: Changqing Teng, Guanglian Li

**标签**: `Volatility` `Options` `Asset Pricing`

针对粗糙Bergomi模型因非马尔可夫结构导致的定价与校准难题，论文提出改进的指数和（mSOE）蒙特卡洛方案，混合原点附近奇异核精确模拟与剩余部分多因子近似，实现O(n)成本下的高精度定价（尤其虚值期权）；并基于该定价引擎，以Wasserstein距离为优化目标设计分布匹配校准方案，利用Lipschitz收益的minimax公式提升鲁棒性，数值实验验证了方法有效性及对路径依赖期权的泛化能力。

---

### [随机因子模型中投资组合选择的大道定理收敛速率](https://arxiv.org/abs/2512.00346v1)

**日期**: 2025-12-02 | **作者**: Hiroki Yamamichi

**标签**: `Factor Model` `Portfolio Optimization`

本文研究随机因子模型中投资组合选择大道定理的收敛速率，将最优反馈函数分解为近视投资组合与超额对冲需求，分别在非线性随机因子模型和二次期限结构模型（利率为多元OU过程二次函数）中推导收敛速率，并应用于最优集体投资问题分析终端财富分享规则对收敛速率的影响。

---

### [零售投资者投资期限与盈余公告](https://arxiv.org/abs/2512.00280v1)

**日期**: 2025-12-02 | **作者**: Domonkos F. Vamossy

**标签**: `Behavioral Finance` `Investor Sentiment` `Asset Pricing` `Anomaly`

本文利用2010-2021年StockTwits帖子将股票分为长/短期限，发现期限结构显著预测盈余公告相关回报模式（长期限股票即时反应更大、公告后漂移更明显）；相关多空策略月alpha达0.43%，且事前情绪对短期限股票后续表现影响更显著，证明零售期限结构是盈余回报变异的有用维度。

---

### [油气行业勘探阶段信息资产投资策略优化：一种强化学习方法](https://arxiv.org/abs/2512.00243v1)

**日期**: 2025-12-02 | **作者**: Paulo Roberto de Melo Barros Junior, Monica Alexandra Vilar Ribeiro De Meireles, Jose Luis Lima de Jesus Silva

**标签**: `Reinforcement Learning` `Portfolio Optimization` `Market Microstructure` `Asset Pricing`

本文采用多智能体深度强化学习（DRL）框架，对比油气勘探中传统阶梯式策略与优先早期高质量信息资产的策略，发现前端加载信息投资可降低冗余数据成本、提升储量估值精度；研究还揭示最优投资时机依赖市场竞争而非仅价格波动，竞争环境中能缓解赢家诅咒，开发阶段收益更显著。

---

### [面向稀疏历史数据的概率神经符号推理：融合贝叶斯推断、因果模型与博弈论分配的框架](https://arxiv.org/abs/2512.01723v1)

**日期**: 2025-12-02 | **作者**: Saba Kublashvili

**标签**: `Deep Learning` `Factor Model` `Anomaly`

论文针对历史事件建模中数据稀疏（N<<100）、异质噪声、缺失反事实及需可解释性等挑战，提出HistoricalML框架，融合贝叶斯不确定性量化、结构因果模型、合作博弈论（沙普利值）与注意力神经架构；理论证明稀疏数据下结合领域强先验可一致估计，沙普利分配满足公理公平性，优于纯回归方法；并通过非洲瓜分、布匿战争案例验证。

---

### [智能制造环境下基于机器学习与SHAP分析的铣刀预测性维护研究](https://arxiv.org/abs/2512.01205v1)

**日期**: 2025-12-02 | **作者**: Wen Zhao, Jiawen Ding, Xueting Huang et al.

**标签**: `Anomaly` `Deep Learning` `Time Series`

论文基于AI4I2020数据集，提出涵盖数据预处理、模型训练等六环节的铣刀预测性维护实验流程，对比8种机器学习模型发现XGBoost与随机森林性能突出，结合SHAP分析揭示加工温度、扭矩、转速为故障关键影响因素，为智能制造预测性维护提供方法参考。

---

### [ICAD-LLM：基于大语言模型上下文学习的一劳永逸异常检测](https://arxiv.org/abs/2512.01672v1)

**日期**: 2025-12-02 | **作者**: Zhongyuan Wu, Jingyuan Wang, Zexuan Cheng et al.

**标签**: `LLM` `Anomaly` `Time Series` `Deep Learning`

论文针对现有异常检测方法多聚焦单模态、泛化能力不足的问题，提出ICAD范式（将异常定义为与正常参考集的差异性），并基于大语言模型的上下文学习能力构建ICAD-LLM统一框架，可处理异质数据且泛化到未见过的任务，性能与任务特定方法相当且降低部署成本。

---

### [脑成像中的深度无监督异常检测：大规模基准测试与偏差分析](https://arxiv.org/abs/2512.01534v1)

**日期**: 2025-12-02 | **作者**: Alexander Frotscher, Christian F. Baumgartner, Thomas Wolfers

**标签**: `Anomaly` `Deep Learning` `Benchmark`

本文构建了脑磁共振成像深度无监督异常检测的大规模多中心基准，包含多扫描仪健康数据及多样临床测试集，系统评估算法性能与稳健性，发现重建类（扩散启发式）分割性能较强但存在扫描器、病灶大小等偏差，特征类抗分布偏移更优。

---

### [Rayan AI竞赛获奖方案：组合式检索、零样本异常检测与后门检测](https://arxiv.org/abs/2512.01498v1)

**日期**: 2025-12-02 | **作者**: Ali Nafisi, Sina Asghari, Mohammad Saeed Arvenaghi et al.

**标签**: `Anomaly` `Deep Learning`

该论文提出Rayan AI竞赛的三个获奖方案，分别针对组合式图像检索（视觉+文本输入，95.38%准确率获第一）、零样本异常检测（无异常样本下识别定位图像异常，73.14%准确率获第一）和后门模型检测（检测神经网络隐藏后门触发，78%准确率获第二）；方法在检索、异常检测及模型安全领域有效，可应用于医疗、制造等行业，代码开源。

---

### [小波变换量子支持向量机建模用于网络入侵检测](https://arxiv.org/abs/2512.01365v1)

**日期**: 2025-12-02 | **作者**: Swati Kumari, Shiva Raj Pokhrel, Swathi Chandrasekhar et al.

**标签**: `Anomaly`

论文提出混合量子-经典框架，整合增强型量子支持向量机（QSVM）与量子哈尔小波包变换（QWPT），采用振幅编码量子态制备、多级QWPT特征提取及基于保真度量子核的QSVM结合SPSA优化器训练；在含噪中等规模量子条件下，BoT-IoT和IoT-23数据集异常检测准确率分别达96.67%和89.67%，优于量子自动编码器超7个百分点。

---

### [FC-ADL：基于功能连接的高效微服务异常检测与定位](https://arxiv.org/abs/2512.00844v1)

**日期**: 2025-12-02 | **作者**: Giles Winchester, George Parisis, Luc Berthouze

**标签**: `Anomaly` `Time Series` `Graph Neural Network`

针对微服务架构中异常检测与定位的挑战（传统方法未考虑时变依赖或因果推理计算开销大），论文提出FC-ADL方法，基于神经科学的功能连接高效刻画微服务指标间的时变依赖变化，实现端到端可扩展的异常检测与定位，无需高开销的因果或多变量方法，在多种故障场景下性能优于现有方法且可应用于大规模部署。

---

### [引入AI驱动的物联网能源管理框架](https://arxiv.org/abs/2512.00321v1)

**日期**: 2025-12-02 | **作者**: Shivani Mruthyunjaya, Anandi Dutta, Kazi Sifatul Islam

**标签**: `Time Series` `Anomaly` `Deep Learning`

论文提出一种AI驱动的物联网能源管理框架，集成长期/短期能耗预测、异常检测及定性数据考量，旨在降低能耗并提升电网稳定性；通过电力消费时间序列数据验证了该框架的可行性。

---

### [SD-CGAN：用于物联网网络DDoS异常检测的条件Sinkhorn散度生成对抗网络](https://arxiv.org/abs/2512.00251v1)

**日期**: 2025-12-02 | **作者**: Henry Onyeka, Emmanuel Samson, Liang Hong et al.

**标签**: `Anomaly` `Deep Learning`

针对物联网边缘网络中动态不平衡流量下的DDoS及零日攻击检测难题，提出SD-CGAN框架（条件GAN增强Sinkhorn散度），结合CTGAN数据增强解决类别不平衡，用Sinkhorn散度提升训练稳定性与减少模式崩溃；在CICDDoS2019数据集上评估，性能优于基线方法且计算高效适配边缘部署。

---

### [TIE：用于视觉可解释和不确定性引导的分布外检测的训练-反转-排除框架](https://arxiv.org/abs/2512.00229v1)

**日期**: 2025-12-02 | **作者**: Pirzada Suhail, Rehna Afroz, Amit Sethi

**标签**: `Anomaly` `Deep Learning`

本文针对深度神经网络难以识别分布外（OOD）样本的问题，提出TIE框架，将标准n类分类器扩展为含垃圾类的n+1类模型，通过训练-反转-排除的闭环过程迭代优化；推理时无需外部OOD数据集即可检测OOD，并提供视觉可解释性与不确定性估计。

---

### [因果AI与相关AI在预测性维护中的基准比较](https://arxiv.org/abs/2512.01149v1)

**日期**: 2025-12-02 | **作者**: Krishna Taduri, Shaunak Dhande, Giacinto Paolo et al.

**标签**: `Benchmark` `Anomaly`

论文针对制造业预测性维护中漏检成本为误报50倍的成本不对称问题，评估了8种模型（含基线统计与形式因果推理方法）在1万台CNC机床数据上的表现；其中形式因果推理模型年成本节省116万美元（降70.2%），优于最佳相关模型约8万美元，且误报减少97%、可解释性更好。

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

### [保险行业的极端值统计](https://arxiv.org/abs/2511.22272v1)

**日期**: 2025-12-01 | **作者**: Hansjoerg Albrecher, Jan Beirlant

**标签**: `Risk Management` `Anomaly`

这篇论文调查了极端值建模技术在保险行业的应用及适配需求，涵盖截断、tempered分布、删失和回归等关键技术，并用具体数据集进行实例验证。

---

### [A3T-GCN用于FTSE100成分股价格预测](https://arxiv.org/abs/2511.21873v1)

**日期**: 2025-12-01 | **作者**: A. L. Paredes

**标签**: `Graph Neural Network` `Time Series` `Deep Learning` `Asset Pricing`

本文提出混合A3T-GCN架构预测FTSE100成分股收盘价，基于行业分类及收益/财务比率相关性构建图结构，节点特征含技术指标、归一化与对数收益等；研究发现使用年化对数收益和更短序列的模型可提升预测精度并降低计算量，较长历史序列对长期预测有适度增益。

---

### [Black-Litterman与ESG投资组合优化](https://arxiv.org/abs/2511.21850v1)

**日期**: 2025-12-01 | **作者**: Aviv Alpern, Svetlozar Rachev

**标签**: `Portfolio Optimization` `Risk Management` `Asset Pricing`

论文提出结合ESG数据与Black-Litterman框架的简单投资组合优化策略，以ESG分数作为Stein收缩估计均衡风险溢价的偏差，用多元仿射正态逆高斯变量建模资产并以CVaR为风险度量；该策略结合软 turnover约束后表现优异，4.7年内每日再平衡的最优策略年收益达40-45%。

---

### [资产量子网络：市场相关性与结构风险的非经典框架](https://arxiv.org/abs/2511.21515v2)

**日期**: 2025-12-01 | **作者**: Hui Gong, Akash Sedai, Francesca Medda

**标签**: `Risk Management` `Anomaly` `Volatility`

论文提出资产量子网络（QNA）框架，基于量子信息密度矩阵突破经典相关矩阵的线性pairwise局限，捕捉资产间非线性、高阶及状态依赖的依赖关系；定义纠缠风险指数（ERI）和量子预警信号（QEWS），通过NASDAQ-100数据验证其能识别经典工具无法捕捉的结构风险与依赖几何。

---

### [基于张量分解的群与酉表示发现理论框架](https://arxiv.org/abs/2511.23152v1)

**日期**: 2025-12-01 | **作者**: Dongsung Huh, Halyun Jeong

**标签**: `Factor Model` `Deep Learning`

该论文分析算子值张量分解架构HyperCube模型，将其目标分解为因子尺度调节项与方向对齐非负项，隔离共线流形并证明仅群同位素存在可行解且推动酉性；提出共线性主导猜想，条件下证明全局极小由群的酉正则表示达到，非群操作目标值严格更高，量化模型对群结合结构的归纳偏置。

---

### [基于每步概率分布直接建模的时间序列预测](https://arxiv.org/abs/2511.23260v1)

**日期**: 2025-12-01 | **作者**: Linghao Kong, Xiaopeng Hong

**标签**: `Deep Learning` `Time Series` `Risk Management` `Anomaly`

现有深度时间序列模型直接输出标量难以处理预测不确定性，本文提出interPDN模型，每步直接构建离散概率分布并以其期望作为回归输出；采用双分支交织支持集架构（含粗时间尺度分支），结合自监督一致性约束缓解预测异常，实验验证其性能更优。

---

### [ARES：边缘流的异常识别模型](https://arxiv.org/abs/2511.22078v1)

**日期**: 2025-12-01 | **作者**: Simone Mungari, Albert Bifet, Giuseppe Manco et al.

**标签**: `Anomaly` `Graph Neural Network` `Deep Learning` `Risk Management`

针对边缘流异常检测面临的概念漂移、大数据量及实时响应挑战，论文提出无监督框架ARES，结合图神经网络（GNN）提取节点与边的潜在特征以捕捉异常行为，半空间树（HST）高效隔离异常；并加入基于少量标记数据的监督阈值机制提升跨领域适应性，在真实网络攻击场景验证其优于现有方法。

---

### [用于物联网异常检测的量子自动编码器可训练核建模](https://arxiv.org/abs/2511.21932v1)

**日期**: 2025-12-01 | **作者**: Swathi Chandrasekhar, Shiva Raj Pokhrel, Swati Kumari et al.

**标签**: `Anomaly` `Deep Learning`

本文针对物联网流量高维复杂与网络威胁加剧的问题，提出量子自动编码器（QAE）框架压缩流量为判别性潜在表示，结合量子支持向量分类（QSVC）实现入侵检测；在理想模拟器及IBM量子硬件上验证了方法的准确率提升，且中等退极化噪声可作为隐正则化稳定训练并增强泛化，证明量子机器学习是应对实际网络安全挑战的可行硬件就绪方案。

---

### [智能物联网设备的无监督异常检测：性能与资源对比](https://arxiv.org/abs/2511.21842v1)

**日期**: 2025-12-01 | **作者**: Md. Sad Abdullah Sami, Mushfiquzzaman Abid

**标签**: `Anomaly`

论文针对传统签名-based异常检测无法识别新兴及零日威胁的问题，采用TON_IoT恒温器数据集，对比孤立森林（IF）与一类支持向量机（OC-SVM）两种无监督方法的检测性能及资源占用；结果显示IF在检测指标和计算资源上更优，适合资源受限的IoT边缘设备部署。

---

### [AgentShield：提升多智能体系统（MAS）的安全性与效率](https://arxiv.org/abs/2511.22924v1)

**日期**: 2025-12-01 | **作者**: Kaixiang Wang, Zhaojiacheng Zhou, Bunyod Suvonov et al.

**标签**: `LLM` `Transformer` `Anomaly` `Deep Learning`

该论文针对基于大语言模型（LLM）的多智能体系统（MAS）易受对抗攻击且现有防御存在单点故障或效率损失的问题，提出分布式防御框架AgentShield，通过关键节点审计、轻量令牌审计、两轮共识审计三层设计优化鲁棒性-效率权衡；实验表明其恢复率达92.5%，审计开销降低超70%，在多样拓扑和攻击场景下维持高协作准确率。

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

### [设计制造数据交易市场的声誉系统：结合Q学习和IRL估计效用的多智能体评估](https://arxiv.org/abs/2511.19930v1)

**日期**: 2025-11-28 | **作者**: Kenta Yamamoto, Teruaki Hayashi

**标签**: `Financial Agent` `Reinforcement Learning` `Market Microstructure` `Asset Pricing`

论文针对制造数据交易市场的信息不对称问题，开发了集成强化学习（Q学习）与逆强化学习（IRL）的多智能体模拟器，评估五种声誉系统的市场效果并提出融合优势的混合机制，以提升数据价格与质量的对齐度。

---

### [基于人工智能的智能电网自适应控制混合信息物理框架](https://arxiv.org/abs/2511.21590v1)

**日期**: 2025-11-28 | **作者**: Muhammad Siddique, Sohaib Zafar

**标签**: `Anomaly` `Deep Learning` `Time Series`

本文提出基于机器学习的智能电网全流程数字取证框架，整合传感器数据采集、认证通信、云存储与自动化取证分析，采用随机森林、SVM、深度神经网络等算法实现实时异常检测、事件重建及入侵分析；经仿真实验验证，该框架准确可扩展，能抵御数据篡改等网络攻击，云服务适配大数据驱动的取证工作流。

---

### [混合SIFT-SNN用于交通流控制基础设施的高效异常检测](https://arxiv.org/abs/2511.21337v1)

**日期**: 2025-11-28 | **作者**: Munish Rathee, Boris Bačić, Maryam Doborjeh

**标签**: `Anomaly` `Deep Learning`

论文提出SIFT-SNN框架，整合SIFT空间特征编码、延迟驱动脉冲转换层与LIF脉冲神经网络（SNN），实现交通基础设施结构异常的实时检测；在含6000帧标注（含真实/合成不安全案例）的奥克兰海港大桥数据集上，该框架实现92.3%±0.8%准确率、单帧9.5ms推理时间，低延迟低功耗适配边缘部署，且相比CNN更具可解释性与硬件效率。

---

### [I-GLIDE：用于退化估计中潜在健康指标的输入分组](https://arxiv.org/abs/2511.21208v1)

**日期**: 2025-11-28 | **作者**: Lucas Thil, Jesse Read, Rim Kaddah et al.

**标签**: `Anomaly` `Deep Learning` `Time Series`

该论文针对剩余使用寿命（RUL）预测中健康指标（HI）的不足，首次将RaPP作为HI并证明其优于传统重建误差；提出输入分组范式（I-GLIDE）隔离传感器子集建模特定退化，结合MC dropout和概率潜在空间量化不确定性以提升鲁棒性，在航空航天和制造系统数据上表现更优且具可解释性。

---

### [从一个攻击域到另一个攻击域：基于孪生网络的对比迁移学习用于高级持续威胁检测](https://arxiv.org/abs/2511.20500v1)

**日期**: 2025-11-28 | **作者**: Sidahmed Benabderrahmane, Talal Rahwan

**标签**: `Anomaly` `Deep Learning`

针对高级持续威胁（APT）检测中传统方法类不平衡、高维特征、跨域迁移性差等问题，论文提出整合迁移学习、可解释AI（SHAP）、对比学习与孪生网络的混合框架——用注意力自动编码器实现跨域知识转移，SHAP筛选稳定特征降维，孪生编码器对齐源-目标表示提升异常可分性；在DARPA TC真实数据及合成攻击场景下，该方法检测性能优于经典与深度基线，具备可扩展、可解释、跨域迁移能力。

---

### [基于主动学习辅助注意力对抗双自动编码器的排序增强异常检测](https://arxiv.org/abs/2511.20480v1)

**日期**: 2025-11-28 | **作者**: Sidahmed Benabderrahmane, James Cheney, Talal Rahwan

**标签**: `Anomaly` `Deep Learning`

论文针对APT攻击的异常检测问题，提出主动学习辅助的注意力对抗双自动编码器框架，通过选择性查询标注减少成本并提升检测率；在DARPA多操作系统真实不平衡溯源数据上验证，性能优于现有方法。

---

### [基于概念瓶颈模型的可解释视觉异常检测](https://arxiv.org/abs/2511.20088v1)

**日期**: 2025-11-28 | **作者**: Arianna Stropeni, Valentina Zaccaria, Francesco Borsatti et al.

**标签**: `Anomaly` `Deep Learning`

本文针对视觉异常检测（VAD）模型解释缺乏语义意义的问题，提出基于概念瓶颈模型（CBM）的CONVAD方法；其核心贡献包括开发VAD用概念数据集、改进CBM架构实现概念与视觉双重解释、引入人工异常合成 pipeline 减少对稀有异常样本的依赖，且性能与经典VAD方法相当并提升可解释性。

---

### [基于渐进单应性引导对齐的无监督多视图视觉异常检测](https://arxiv.org/abs/2511.18766v1)

**日期**: 2025-11-28 | **作者**: Xintao Chen, Xiaohao Xu, Bozhong Zheng et al.

**标签**: `Anomaly` `Deep Learning`

本文提出无监督多视图视觉异常检测框架ViewSense-AD（VSAD），核心通过单应性引导的多视图对齐模块（MVAM）对齐相邻视图特征区域，集成到视图对齐潜在扩散模型（VALDM）实现渐进多阶段对齐，结合融合细化模块（FRM）增强特征一致性，通过对比多级别特征与正常原型记忆库完成异常检测，在RealIAD和MANTA数据集上取得SOTA。

---

### [面向问题的时间序列异常检测评估指标分类](https://arxiv.org/abs/2511.18739v1)

**日期**: 2025-11-28 | **作者**: Kaixiang Yang, Jiarong Liu, Yupeng Song et al.

**标签**: `Anomaly` `Time Series` `Benchmark`

本文针对时间序列异常检测评估的挑战，提出面向问题的指标分类框架，将20余种常用指标按6个维度（如基本准确率、时效性、标签不精确容忍度等）分类；通过实验量化各指标区分有效检测与随机噪声的能力，揭示指标适用性需与任务目标对齐，为评估提供统一分析视角。

---

### [多模态实时异常检测及其工业应用](https://arxiv.org/abs/2511.18698v1)

**日期**: 2025-11-28 | **作者**: Aman Verma, Keshav Samdani, Mohd. Samiuddin Shafi

**标签**: `Anomaly` `Deep Learning` `Transformer`

论文提出集成视频与音频处理的多模态实时异常检测系统，包含轻量版（YOLOv8、ByteTrack、AST）和进阶版（多音频模型集成、混合目标检测、跨模态注意力等）；进阶版结合三类音频模型、双目标检测器及复杂融合机制，在通用监控与工业安全场景中实现实时高性能。

---

### [基于眼底图像的功能定位强化深度异常检测](https://arxiv.org/abs/2511.18627v1)

**日期**: 2025-11-28 | **作者**: Jan Benedikt Ruhland, Thorsten Papenbrock, Jan-Peter Sowa et al.

**标签**: `Anomaly` `Deep Learning` `Transformer`

论文针对眼底图像视网膜疾病检测的质量变异、早期表现细微等挑战，系统评估Vision Transformer（ViT）在多数据集和增强策略下的性能，发现几何与颜色增强稳定提升效果，ViT在Papila数据集AUC优于卷积集成基线；同时开发基于GANomaly的异常检测器，提供重建可解释性并泛化到 unseen 数据，结合GUESS实现概率校准。

---

### [MEDIC：用于对撞机实验数据质量监控的网络](https://arxiv.org/abs/2511.18172v1)

**日期**: 2025-11-28 | **作者**: Juvenal Bassa, Arghya Chattopadhyay, Sudhir Malik et al.

**标签**: `Anomaly` `Deep Learning`

论文针对粒子物理实验数据质量监控（DQM）的挑战，提出模拟驱动方法，利用修改后的Delphes探测器模拟工具，开发MEDIC神经网络框架，实现探测器行为学习、异常识别及故障组件定位，为综合DQM系统奠定初步基础。

---

### [经典与量子核的融合实现准确且鲁棒的两样本检验](https://arxiv.org/abs/2511.20941v1)

**日期**: 2025-11-28 | **作者**: Yu Terada, Yugo Ogio, Ken Arai et al.

**标签**: `Deep Learning` `Anomaly`

该论文针对小数据集下核选择难题，基于最大均值差异（MMD）核检验框架提出MMD-FUSE方法，通过融合经典核与量子核的混合测试策略，结合经典核的领域归纳偏置和量子核的表达能力；实验验证表明，经超参数调优后，含量子核的MMD-FUSE测试能力显著优于经典核方法，适用于合成及真实临床数据集。

---

### [数据流中分类器投票线性独立性视角下的集成性能研究](https://arxiv.org/abs/2511.21465v1)

**日期**: 2025-11-28 | **作者**: Enes Bektas, Fazli Can

**标签**: `Algorithmic Trading` `Time Series` `Anomaly`

本文从数据流中分类器投票的线性独立性视角，研究集成规模与性能的关系，推导了达到指定线性独立概率所需集成规模的理论估计；通过OzaBagging和GOOWE等集成方法在真实及合成数据集上验证，发现该估计可有效识别鲁棒集成的性能饱和点，且复杂加权方案的高理论多样性可能引发算法不稳定。

---

### [智能制造中的混合智能体AI与多智能体系统](https://arxiv.org/abs/2511.18258v1)

**日期**: 2025-11-28 | **作者**: Mojtaba A. Farahani, Md Irfan Khan, Thorsten Wuest

**标签**: `LLM` `Anomaly` `Transformer`

本文提出面向智能制造预测性维护的混合智能体AI与多智能体框架，以LLM智能体实现战略编排与自适应推理，结合规则及SLM智能体完成边缘端高效领域任务，分层架构由LLM Planner协调工作流；该框架支持动态模型适应、成本高效维护调度及可解释决策，经工业数据集验证且模块化可扩展。

---

### [语义优势与取证效率：深度学习与心理语言学在商务邮件欺诈检测中的比较分析](https://arxiv.org/abs/2511.20944v1)

**日期**: 2025-11-28 | **作者**: Yaw Osei Adjei

**标签**: `NLP` `Deep Learning` `Transformer` `Anomaly`

论文针对每年造成超29亿美元损失的商务邮件欺诈（BEC），比较两种检测范式——基于DistilBERT的语义流（高精度需GPU）和基于CatBoost的取证心理语言流（低延迟低成本），在对抗性数据集上验证性能，为不同部署场景提供选型参考。

---

