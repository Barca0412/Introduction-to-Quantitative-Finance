# Machine Learning

机器学习在量化金融中的应用，包括深度学习、强化学习、图神经网络、Transformer等

> 共收录 **42** 篇论文 | [返回索引](../README.md)

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

### [含未观测上下文的特定上下文因果图发现：非平稳性、机制与时空模式](https://arxiv.org/abs/2511.21537v1)

**日期**: 2025-11-28 | **作者**: Martin Rabel, Jakob Runge

**标签**: `Time Series` `Anomaly`

针对含未观测上下文的非平稳时空数据（如气候网格时间序列），论文提出模块化因果图发现框架，通过修改约束类因果算法的独立性测试层适配数据变化，可复用PC、PCMCI等现有算法并支持结合变化点检测等方法扩展。

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

### [KOM：用于膝骨关节炎（KOA）精准管理的多智能体人工智能系统](https://arxiv.org/abs/2511.19798v1)

**日期**: 2025-11-28 | **作者**: Weizhi Liu, Xi Chen, Zekun Jiang et al.

**标签**: `LLM` `Deep Learning` `Risk Management`

针对全球超6亿膝骨关节炎（KOA）患者个性化多学科干预资源不足的问题，开发多智能体系统KOM，可自动化KOA评估、风险预测与治疗处方；实验显示其在影像分析和处方生成上优于通用大模型，且与临床医生协作能提升诊疗效率（减少38.5%时间）和治疗质量。

---

### [通过类别相似性增强保形预测](https://arxiv.org/abs/2511.19359v1)

**日期**: 2025-11-28 | **作者**: Ariel Fargion, Lahav Dabah, Tom Tirer

**标签**: `Deep Learning` `Risk Management`

该论文聚焦保形预测（CP）的增强，针对类别语义分组场景，提出用分组惩罚项优化CP评分函数，理论证明其对分组指标的优势及降低平均预测集大小的效果；进一步提出无需人工语义分区的模型特定变体，再缩小预测集规模；并通过多CP方法、模型及数据集实证验证有效性。

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

### [独立策略梯度强化学习在多微电网系统经济可靠能源管理中的应用](https://arxiv.org/abs/2511.20977v1)

**日期**: 2025-11-28 | **作者**: Junkai Hu, Li Xia

**标签**: `Reinforcement Learning` `Risk Management` `Deep Learning` `Portfolio Optimization`

针对多微电网系统（MMS）的经济可靠能源管理问题，本文将其建模为均值-方差团队随机博弈（MV-TSG），提出已知参数下的分布式独立策略梯度算法（含收敛分析）及未知参数下的数据驱动深度强化学习方法；数值实验验证方法可平衡经济性能与运行可靠性，充分利用MMS分布式计算能力。

---

### [用于偏差缓解的进化样本权重：有效性取决于优化目标](https://arxiv.org/abs/2511.20909v1)

**日期**: 2025-11-28 | **作者**: Anil K. Saini, Jose Guadalupe Hernandez, Emily F. Wong et al.

**标签**: `Deep Learning` `Risk Management`

本文比较遗传算法进化样本权重、基于数据集特征计算权重及等权重三种方法，以预测（准确率、AUC）和公平性（人口 parity差、 subgroup假阴性公平）指标为优化目标开展实验；发现进化权重可实现更优的公平-预测性能权衡，但有效性依赖优化目标，其中准确率与人口 parity差的组合在最多数据集上优于其他策略。

---

### [带ω-正则目标与约束的强化学习](https://arxiv.org/abs/2511.19849v1)

**日期**: 2025-11-28 | **作者**: Dominik Wagner, Leon Witzman, Luke Ong

**标签**: `Reinforcement Learning` `Risk Management`

针对强化学习（RL）标量奖励难以表达时序/安全目标、易奖励 hacking，且单标量掩盖风险-性能 trade-off的问题，论文结合ω-正则目标与显式约束，分开处理安全要求和优化目标；提出基于线性规划的模型基RL算法，极限下生成最大化ω-正则目标满足概率且满足约束阈值的策略，并建立到带最优性保证的约束极限平均问题的转换。

---

### [MOMA-AC：连续多目标多智能体强化学习的偏好驱动演员-评论员框架](https://arxiv.org/abs/2511.18181v1)

**日期**: 2025-11-28 | **作者**: Adam Callaghan, Karl Mason, Patrick Mannion

**标签**: `Reinforcement Learning` `Deep Learning` `Financial Agent`

本文针对连续状态与动作空间的多目标多智能体强化学习（MOMARL）空白，提出首个内循环演员-评论员框架MOMA-AC，基于TD3/DDPG实例化为MOMA-TD3/DDPG，结合多头演员、集中式评论员与偏好条件架构，可编码冲突目标下最优策略的帕累托前沿；还构建连续MOMARL测试套件，在合作任务中显著提升预期效用与超体积，且随智能体数量增加可稳定扩展。

---

### [通过BREW提升语言智能体性能](https://arxiv.org/abs/2511.20297v1)

**日期**: 2025-11-28 | **作者**: Shashank Kirtania, Param Biyani, Priyanshu Gupta et al.

**标签**: `LLM` `Financial Agent` `Reinforcement Learning` `Transformer`

针对当前LLM智能体训练（如PPO等）计算开销大、策略难解释的问题，论文提出BREW框架，通过构建与优化经验环境知识的结构化记忆，结合任务评分器、行为 rubric及状态空间搜索提升智能体性能；实证在OSWorld等基准上实现10-20%精度提升、10-15%工具调用减少且计算高效。

---

### [大规模网络中资源替代的公平OR-ML框架](https://arxiv.org/abs/2511.18269v1)

**日期**: 2025-11-28 | **作者**: Ved Mohan, El Mehdi Er Raqabi, Pascal Van Hentenryck

**标签**: `Portfolio Optimization` `Deep Learning`

针对大规模物流网络资源供需不平衡及分散场景下协调难、需兼顾公平与调度员偏好的问题，论文提出结合运筹学（OR）与机器学习（ML）的通用框架；OR组件建模求解带公平约束的资源替代问题，ML组件通过历史数据学习偏好、引导决策探索并动态选top-κ资源提升效率，输出高质量解供调度员选择。

---

### [智能制造中的混合智能体AI与多智能体系统](https://arxiv.org/abs/2511.18258v1)

**日期**: 2025-11-28 | **作者**: Mojtaba A. Farahani, Md Irfan Khan, Thorsten Wuest

**标签**: `LLM` `Anomaly` `Transformer`

本文提出面向智能制造预测性维护的混合智能体AI与多智能体框架，以LLM智能体实现战略编排与自适应推理，结合规则及SLM智能体完成边缘端高效领域任务，分层架构由LLM Planner协调工作流；该框架支持动态模型适应、成本高效维护调度及可解释决策，经工业数据集验证且模块化可扩展。

---

### [CostNav：具身智能体成本感知评估的导航基准](https://arxiv.org/abs/2511.20216v1)

**日期**: 2025-11-28 | **作者**: Haebin Seong, Sungmin Kim, Minchan Kim et al.

**标签**: `Benchmark` `Financial Agent` `Deep Learning`

现有导航基准忽略商业部署的经济可行性，论文提出首个成本感知导航基准CostNav，基于行业参数建模全生命周期成本（硬件、训练、能源、维护等）与收入（含服务等级协议SLA）；定量揭示任务成功优化与商业可行的差距，基线虽有43% SLA合规但亏损（碰撞维护占99.7%成本），并建立多类导航方法的评估基础。

---

### [语义优势与取证效率：深度学习与心理语言学在商务邮件欺诈检测中的比较分析](https://arxiv.org/abs/2511.20944v1)

**日期**: 2025-11-28 | **作者**: Yaw Osei Adjei

**标签**: `NLP` `Deep Learning` `Transformer` `Anomaly`

论文针对每年造成超29亿美元损失的商务邮件欺诈（BEC），比较两种检测范式——基于DistilBERT的语义流（高精度需GPU）和基于CatBoost的取证心理语言流（低延迟低成本），在对抗性数据集上验证性能，为不同部署场景提供选型参考。

---

### [符号信道原理：衡量大语言模型通信中的意义容量](https://arxiv.org/abs/2511.19550v1)

**日期**: 2025-11-28 | **作者**: Davide Picca

**标签**: `LLM` `NLP` `Deep Learning` `Risk Management`

论文提出符号框架分析大语言模型（LLM），用信息论工具量化表达丰富度（源熵）与解释稳定性（消息和人类解释的互信息）的权衡，引入生成复杂度参数λ建模该权衡，定义符号信道并提出意义传输的容量约束，同时展示其在模型 profiling、提示设计等四方面的应用价值。

---

