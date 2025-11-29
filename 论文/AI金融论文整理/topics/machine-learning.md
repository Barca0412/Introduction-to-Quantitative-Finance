# Machine Learning

机器学习在量化金融中的应用，包括深度学习、强化学习、图神经网络、Transformer等

> 共收录 **95** 篇论文 | [返回索引](../README.md)

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

### [工业级推荐系统中时间分布泛化的概率框架](https://arxiv.org/abs/2511.21032v1)

**日期**: 2025-11-28 | **作者**: Yuxuan Zhu, Cong Fu, Yabo Ni et al.

**标签**: `Deep Learning` `Time Series`

针对时间分布偏移（TDS）削弱推荐系统长期准确率的问题，现有方法存在泛化不稳定、表征崩塌等局限，本文提出ELBO_TDS概率框架——先通过统计分析识别关键时间偏移因素并设计数据增强策略扩展训练分布，再基于因果图推导自监督变分目标以避免表征崩塌，实验证明其提升用户GMV且已部署于Shopee产品搜索。

---

### [驱动因子盲视现象：深度序列模型为何在血糖预测中默认依赖自相关性](https://arxiv.org/abs/2511.20601v1)

**日期**: 2025-11-28 | **作者**: Heman Shakeri

**标签**: `Deep Learning` `Time Series`

论文指出深度序列模型在血糖预测中存在“驱动因子盲视”（无法利用胰岛素、饮食、活动等临床信息），通过Δ_drivers（多变量模型相对单变量基线的性能增益）量化该现象；分析其源于架构偏向自相关、驱动因子数据保真度不足、生理异质性三个交互因素；提出生理特征编码器、因果正则化、个性化等缓解策略，并建议未来工作常规报告Δ_drivers避免此类模型被视为最优。

---

### [量化高保真合成网络流量的隐私影响](https://arxiv.org/abs/2511.20497v1)

**日期**: 2025-11-28 | **作者**: Van Tran, Shinan Liu, Tian Li et al.

**标签**: `Deep Learning`

针对网络流量数据稀缺与隐私问题，现有合成流量并非天生隐私保护，论文提出结合成员推理攻击、数据提取攻击及网络特定标识符的综合隐私度量，系统评估不同生成模型的隐私漏洞，发现模型/数据集间风险差异显著，识别训练数据多样性等关键影响因素，为安全合成网络流量生成提供指导。

---

### [使用可解释人工智能识别与双壳类软体动物河豚毒素污染相关的环境因素](https://arxiv.org/abs/2511.20395v1)

**日期**: 2025-11-28 | **作者**: M. C. Schoppema, B. H. M. van der Velden, A. Hürriyetoğlu et al.

**标签**: `Deep Learning` `Time Series`

该研究开发了基于可解释深度学习的模型，以气象和水文特征为输入预测双壳类软体动物河豚毒素（TTX）污染的有无；模型识别出有效日照时长（日长+总辐射）、水温、氯化物浓度等关键关联环境因素，为食品行业和监管部门缓解海洋毒素风险提供工具。

---

### [DUO-TOK：用于人声伴奏生成的双轨语义音乐Tokenizer](https://arxiv.org/abs/2511.20224v1)

**日期**: 2025-11-28 | **作者**: Rui Lin, Zhiyue Wu, Jiahe Le et al.

**标签**: `Deep Learning`

针对现有歌词到歌曲系统中重建质量与语言模型可学习性的矛盾，提出Duo-Tok源感知双码本Tokenizer，采用四阶段SSL中心 pipeline，先预训练编码器再分解表示、学习双码本并训练扩散解码器，在0.75kbps下提升Pareto前沿，实现最优音乐标记AP和最低LM困惑度，同时保持高重建质量。

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

### [理解Transformer学习潜在结构的阶段性动态](https://arxiv.org/abs/2511.19328v1)

**日期**: 2025-11-28 | **作者**: Rohan Saha, Farzane Aminmansour, Alona Fyshe

**标签**: `Transformer` `Benchmark` `Deep Learning` `LLM`

本文使用Alchemy基准，训练仅解码器Transformer并在三类任务（推断缺失规则、组合简单规则解决多步序列、分解复杂例子推断中间步骤）上研究其潜在结构学习的动态；发现模型分阶段掌握能力（先学粗粒度规则再学完整结构），且存在“能稳健组合基本规则但难分解复杂例子发现规则”的关键不对称性，为理解Transformer的潜在结构学习提供了细粒度视角。

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

### [量子自编码器的神经架构搜索](https://arxiv.org/abs/2511.19246v1)

**日期**: 2025-11-28 | **作者**: Hibah Agha, Samuel Yen-Chi Chen, Huan-Hsin Tseng et al.

**标签**: `Deep Learning`

本文提出基于遗传算法的神经架构搜索框架，自动化设计量子自编码器的变分量子电路配置，解决量子电路架构设计复杂的问题；在图像数据集上验证方法有效性，为遗传算法应用于量子架构搜索奠定基础，适配噪声近中期量子时代需求。

---

### [机器N400：精确定位因果语言模型检测语义违规的位置](https://arxiv.org/abs/2511.19232v1)

**日期**: 2025-11-28 | **作者**: Christos-Nikolaos Zacharopoulos, Revekka Kyriakoglou

**标签**: `LLM` `NLP` `Transformer` `Deep Learning`

该研究以因果语言模型phi-2为对象，通过精心构建的含合理/不合理结尾句子的语料，分析各层隐藏状态；利用线性探针和有效维度分析发现，语义违规检测在模型低层难区分、中层后准确率提升，且表征子空间先扩后缩，还联系了人类心理语言学的相关发现。

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

### [基于音乐混合条件的扩散模型分离人声](https://arxiv.org/abs/2511.21342v1)

**日期**: 2025-11-28 | **作者**: Genís Plaja-Roglans, Yun-Ning Hung, Xavier Serra et al.

**标签**: `Deep Learning`

本文提出以音乐混合音频为条件的扩散模型，用于从真实录音中分离独唱人声；该模型改进现有生成系统，补充数据训练后客观指标与非生成基线相当，且扩散采样迭代性支持用户控制质量-效率权衡及输出优化。

---

### [打破安全-能力权衡：带可验证奖励的强化学习在大语言模型中维持安全护栏](https://arxiv.org/abs/2511.21050v1)

**日期**: 2025-11-28 | **作者**: Dongkyu Derek Cho, Huan Song, Arijit Ghosh Chowdhury et al.

**标签**: `LLM` `Reinforcement Learning` `Transformer` `Benchmark`

论文指出大语言模型微调存在安全-能力权衡，现有SFT、RLHF等方法无法避免；首次对带可验证奖励的强化学习（RLVR）进行理论与实证分析，推导KL约束下安全漂移上界并证明消除安全退化的条件，实验显示RLVR可同时提升推理能力与安全护栏，挑战了必然权衡的假设。

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

### [公平性与隐私的融合：多分类中差分隐私与人口统计均等的整合](https://arxiv.org/abs/2511.18876v1)

**日期**: 2025-11-28 | **作者**: Lilian Say, Christophe Denis, Rafael Pinot

**标签**: `Deep Learning`

本文挑战隐私与公平性常被视为冲突的观点，设计后处理算法DP2DP，同时满足差分隐私与人口统计均等；理论分析显示其收敛速率仅比非私有公平方法多对数因子，实验验证了最优的准确率、公平性与隐私三目标权衡。

---

### [探寻优度函数：前向-前向算法优度函数的大规模基准测试](https://arxiv.org/abs/2511.18567v1)

**日期**: 2025-11-28 | **作者**: Arya Shah, Vaibhav Tripathi

**标签**: `Deep Learning` `Benchmark`

该论文针对前向-前向（FF）算法的优度函数，在4个标准图像数据集上对21种不同优度函数进行大规模基准测试，评估分类准确率、能耗及碳足迹；发现部分替代优度函数显著优于默认平方和指标，且存在预测性能与环境成本的权衡，证明优度函数是FF设计的关键超参数，并开源代码供复现。

---

### [MOMA-AC：连续多目标多智能体强化学习的偏好驱动演员-评论员框架](https://arxiv.org/abs/2511.18181v1)

**日期**: 2025-11-28 | **作者**: Adam Callaghan, Karl Mason, Patrick Mannion

**标签**: `Reinforcement Learning` `Deep Learning` `Financial Agent`

本文针对连续状态与动作空间的多目标多智能体强化学习（MOMARL）空白，提出首个内循环演员-评论员框架MOMA-AC，基于TD3/DDPG实例化为MOMA-TD3/DDPG，结合多头演员、集中式评论员与偏好条件架构，可编码冲突目标下最优策略的帕累托前沿；还构建连续MOMARL测试套件，在合作任务中显著提升预期效用与超体积，且随智能体数量增加可稳定扩展。

---

### [使用迭代PPO对齐大语言模型以实现多轮对话结果](https://arxiv.org/abs/2511.21638v1)

**日期**: 2025-11-28 | **作者**: Daniel R. Jiang, Jalaj Bhandari, Yukai Yang et al.

**标签**: `LLM` `NLP` `Reinforcement Learning`

针对多轮对话强化学习（RL）中稀疏长 horizon 奖励及响应与token级生成差异的挑战，论文将多轮RL问题简化为一系列单轮RLHF式问题，用学习到的多轮Q函数作为单轮奖励模型，并证明标准token级PPO解决单轮问题等价于多轮问题的策略改进步骤；基于此提出迭代PPO算法，交替拟合Q函数与改进策略，直接利用现成单轮RLHF工具，兼具在线更新适应性与离线训练稳定性。

---

### [DSD：一种用于边云敏捷大模型服务的分布式推测解码方案](https://arxiv.org/abs/2511.21669v1)

**日期**: 2025-11-28 | **作者**: Fengze Yu, Leshu Li, Brad McDanel et al.

**标签**: `LLM` `Transformer` `Deep Learning`

针对大语言模型（LLM）推理延迟高、边云异构环境扩展性有限的问题，现有推测解码（SD）仅支持单节点，论文提出DSD分布式框架通过协调草稿-目标执行扩展到多设备；同时设计DSD-Sim模拟器捕捉网络等动态，并提出自适应窗口控制（AWC）策略优化吞吐量；实验表明DSD比现有SD基线最多提升1.1倍速度和9.7%吞吐量，实现边云敏捷可扩展LLM服务。

---

### [视觉Transformer中非单调缩放的机制](https://arxiv.org/abs/2511.21635v1)

**日期**: 2025-11-28 | **作者**: Anantha Padmanaban Krishna Kumar

**标签**: `Transformer` `Deep Learning`

本文针对视觉Transformer（ViT）深层性能劣于浅层的问题，通过对ViT-S/B/L在ImageNet上的实证分析，发现其表示演化存在“悬崖-平台-攀升”三阶段模式；提出信息混合指数量化信息扩散，揭示深层ViT额外层多为信息扩散而非任务提升，指出架构应注重深度校准而非单纯增参，该指数可用于模型诊断与未来设计。

---

### [BAMAS：构建预算感知型多智能体系统](https://arxiv.org/abs/2511.21572v1)

**日期**: 2025-11-28 | **作者**: Liming Yang, Junyu Luo, Xuanzhe Liu et al.

**标签**: `LLM` `Reinforcement Learning` `NLP`

该论文针对现有LLM多智能体系统缺乏显式预算约束下结构设计的问题，提出BAMAS方法——先通过整数线性规划选择平衡性能与成本的最优LLM集合，再用强化学习确定智能体交互拓扑并实例化执行；实验表明BAMAS在保持相当性能的同时，成本最多降低86%。

---

### [基于ChatDRex的对话式无代码多智能体疾病模块识别与药物重定位预测](https://arxiv.org/abs/2511.21438v1)

**日期**: 2025-11-28 | **作者**: Simon Süwer, Kester Bagemihl, Sylvie Baier et al.

**标签**: `LLM` `NLP` `Graph Neural Network`

论文提出对话式无代码多智能体系统ChatDRex，基于集成系统医学知识图谱NeDRex，整合生物信息学代理（网络分析、药物重定位、功能验证等）与推理模块（防幻觉）；解决传统药物重定位预测中工具碎片化、数据异构、需专业用户等问题，支持非计算背景研究者通过自然语言完成复杂分析。

---

### [主观深度与时标Transformer：学习在何处及何时计算](https://arxiv.org/abs/2511.21408v1)

**日期**: 2025-11-28 | **作者**: Frederico Wieser, Martin Benfeghoul, Haitham Bou Ammar et al.

**标签**: `Transformer` `Deep Learning` `LLM` `Time Series`

针对标准Transformer计算分配僵化统一限制效率可扩展性的问题，论文提出主观深度Transformer（SDT）和时标Transformer（STT）两种架构，利用贝叶斯惊喜信号动态路由计算：SDT通过交替决策层与动态层基于惊喜做Top-K路由，STT扩展到时间域用过渡网络动态执行/绕过块；两者训练中呈现从 novelty到prediction驱动门控的变化，且自注意力计算减少75%、KV缓存需求减少50%。

---

### [双状态推理的文本转SQL：融合自适应上下文与渐进式生成](https://arxiv.org/abs/2511.21402v1)

**日期**: 2025-11-28 | **作者**: Zhifeng Hao, Qibin Song, Ruichu Cai et al.

**标签**: `LLM` `NLP` `Transformer`

针对现有分治推理方法在复杂企业数据库文本转SQL中存在的上下文容量有限、schema链接不可靠及语义 grounding弱的问题，论文提出DSR-SQL双状态推理框架，通过自适应上下文状态精炼schema构建紧凑语义环境，渐进生成状态以反馈引导状态转移实现自纠正；无需后训练或上下文示例，在Spider2.0-Snow和BIRD开发集上取得竞争力性能。

---

### [Prune4Web：面向Web Agent的DOM树剪枝编程](https://arxiv.org/abs/2511.21398v1)

**日期**: 2025-11-28 | **作者**: Jiayuan Zhang, Kaiquan Chen, Zhihao Lu et al.

**标签**: `LLM` `Transformer` `Deep Learning`

针对基于大语言模型（LLM）的Web Agent处理复杂DOM结构时存在的信息丢失或效率不足问题，提出Prune4Web范式，通过让LLM生成可执行Python评分脚本动态过滤DOM元素，实现25-50倍候选元素减少；同时设计专用数据标注 pipeline和两回合对话训练策略，联合优化模型性能。

---

### [基于RISC-V的边缘AI深度可分离卷积TinyML加速器](https://arxiv.org/abs/2511.21232v1)

**日期**: 2025-11-28 | **作者**: Muhammed Yildirim, Ozcan Ozturk

**标签**: `Deep Learning`

本文针对轻量CNN中深度可分离卷积（DSC）的层间数据传输内存瓶颈，提出一种基于RISC-V的融合逐像素数据流硬件加速器架构（作为自定义功能单元CFU），消除中间缓冲区，数据移动减少达87%；经FPGA和ASIC评估，该架构比RISC-V软件执行提速最多59.3x，且面积功耗表现优异，验证了TinyML资源范围内零缓冲区数据流的可行性。

---

### [当机器人服从补丁：视觉-语言-动作模型的通用可迁移对抗补丁攻击](https://arxiv.org/abs/2511.21192v1)

**日期**: 2025-11-28 | **作者**: Hui Lu, Yi Yu, Yiming Yang et al.

**标签**: `Deep Learning` `Transformer`

现有视觉-语言-动作（VLA）模型的对抗攻击中，通用可迁移补丁研究不足（多过拟合单模型）；论文提出UPA-RFAS框架，结合特征空间目标、鲁棒增强两阶段优化及VLA特有的补丁注意力支配与语义错位损失，学习单个物理补丁，可跨模型、任务、视角迁移，暴露攻击面并建立防御基线。

---

### [BRIDGE：领域引导的程序验证中的表示构建](https://arxiv.org/abs/2511.21104v1)

**日期**: 2025-11-28 | **作者**: Robert Joseph George, Carson Eisenach, Udaya Ghai et al.

**标签**: `LLM` `Deep Learning` `Transformer`

论文提出BRIDGE方法，首次系统研究结构化提示用于可扩展的验证程序生成；该方法将验证分解为代码、规格说明和证明三个互联领域，通过引出功能、规格驱动和证明导向三种推理行为作为中间表示连接各领域，实验表明其在准确性和效率上显著优于标准错误反馈方法。

---

### [用于LLM引导的开放世界强化学习的子目标图增强规划](https://arxiv.org/abs/2511.20993v1)

**日期**: 2025-11-28 | **作者**: Shanwei Fan

**标签**: `LLM` `Reinforcement Learning` `Graph Neural Network`

针对LLM引导强化学习中规划-执行不对齐（子目标不可行/无关、单LLM生成与自验证混淆）的问题，论文提出SGA-ACR框架，整合环境特定子目标图、结构化实体知识与多LLM规划流水线（分离生成、批判、细化），并通过子目标跟踪器监控进度、提供辅助奖励及更新子目标图；在开放世界游戏Crafter的22个任务中验证了该方法的有效性。

---

### [NOIR 2.0：面向日常活动的神经信号操控智能机器人](https://arxiv.org/abs/2511.20848v1)

**日期**: 2025-11-28 | **作者**: Tasha Kim, Yingke Wang, Hanvit Cho et al.

**标签**: `Deep Learning` `LLM`

该论文提出增强版脑机接口系统NOIR 2.0，通过更快更准确的脑信号解码算法将人类意图转化为机器人指令，任务完成时间减少46%；同时采用结合基础模型的少样本机器人学习算法，提升对个体用户的适应性与意图预测效率，显著降低人类操作时间65%。

---

### [E2E-GRec：图神经网络与推荐系统的端到端联合训练框架](https://arxiv.org/abs/2511.20564v1)

**日期**: 2025-11-28 | **作者**: Rui Xue, Shichao Zhu, Liang Qin et al.

**标签**: `Graph Neural Network` `Deep Learning`

针对现有推荐系统中GNN与推荐模型两阶段部署的计算开销高、缺乏联合优化的问题，本文提出端到端联合训练框架E2E-GRec，通过高效子图采样、Graph Feature Auto-Encoder辅助自监督及两级特征融合+Gradnorm动态损失平衡，实现可扩展且稳定的训练，离线评估与在线A/B测试验证了其有效性。

---

### [NNGPT：基于大语言模型的自动机器学习重新思考](https://arxiv.org/abs/2511.20333v1)

**日期**: 2025-11-28 | **作者**: Roman Kochnev, Waleed Khalid, Tolgay Atinc Uzun et al.

**标签**: `LLM` `Deep Learning` `Reinforcement Learning`

论文提出开源框架NNGPT，将大语言模型转化为自改进的神经网络开发AutoML引擎（侧重计算机视觉），通过生成-评估-自改进的闭环系统整合5个LLM驱动的协同管道，实现端到端模型验证与学习，且在执行率、预测精度等指标上优于部分传统方法。

---

### [通过BREW提升语言智能体性能](https://arxiv.org/abs/2511.20297v1)

**日期**: 2025-11-28 | **作者**: Shashank Kirtania, Param Biyani, Priyanshu Gupta et al.

**标签**: `LLM` `Financial Agent` `Reinforcement Learning` `Transformer`

针对当前LLM智能体训练（如PPO等）计算开销大、策略难解释的问题，论文提出BREW框架，通过构建与优化经验环境知识的结构化记忆，结合任务评分器、行为 rubric及状态空间搜索提升智能体性能；实证在OSWorld等基准上实现10-20%精度提升、10-15%工具调用减少且计算高效。

---

### [由大语言模型驱动的交互式AI NPC：CPDC 2025挑战技术报告](https://arxiv.org/abs/2511.20200v1)

**日期**: 2025-11-28 | **作者**: Yitian Huang, Yuxuan Lei, Jianxun Lian et al.

**标签**: `LLM` `NLP` `Reinforcement Learning`

本文介绍团队MSRA_SC在CPDC 2025挑战中的解决方案，提出包含上下文工程（动态工具剪枝、角色裁剪等）和GPU赛道GRPO强化学习训练的框架；该框架提升工具调用稳定性与任务导向对话性能，最终在多个任务中取得优异排名（如Task2 API赛道第一）。

---

### [面向查询依赖的提示优化的统一评估指导框架](https://arxiv.org/abs/2511.19829v1)

**日期**: 2025-11-28 | **作者**: Ke Chen, Yifeng Wang, Hassan Almosapeeh et al.

**标签**: `LLM` `NLP` `Deep Learning`

现有提示优化方法多针对静态模板或依赖不稳定反馈，提示质量缺乏统一系统定义；本文建立面向性能的提示评估框架，开发无需执行的评估器预测多维度质量分数，进而指导度量感知优化器以可解释的查询依赖方式优化提示；实验表明评估器预测准确，优化方法在8个数据集3个骨干模型上超越基线，实现稳定可解释的改进。

---

### [利用大语言模型进行强化学习控制任务中的奖励函数设计](https://arxiv.org/abs/2511.19355v1)

**日期**: 2025-11-28 | **作者**: Franklin Cardenoso, Wouter Caarls

**标签**: `LLM` `Reinforcement Learning`

论文提出无需初步指标和环境源代码的LEARN-Opt框架，能从系统与任务目标的文本描述中自主生成、执行并评估奖励函数候选，还可自主推导性能指标实现无监督评估，实验表现媲美或优于EUREKA且需先验知识更少。

---

### [MAESTRO：通过任务与奖励优化的多智能体环境塑造](https://arxiv.org/abs/2511.19253v1)

**日期**: 2025-11-28 | **作者**: Boyuan Wu

**标签**: `LLM` `Reinforcement Learning` `Deep Learning`

针对合作多智能体强化学习（MARL）中密集奖励函数设计和课程构建的瓶颈，论文提出MAESTRO框架，将大语言模型（LLM）移出执行环作为离线训练架构师，包含语义课程生成器（创建性能驱动的交通场景）和自动奖励合成器（生成适配课程难度的Python奖励函数），引导标准MARL算法（MADDPG）提升交通信号控制任务的性能与稳定性，且不增加部署推理成本。

---

### [大语言模型辅助的电动汽车充电基础设施规划（含真实案例研究）](https://arxiv.org/abs/2511.19055v1)

**日期**: 2025-11-28 | **作者**: Xinda Zheng, Canchen Jiang, Hao Wang

**标签**: `LLM` `NLP` `Deep Learning`

本文提出一种集成方法，联合优化电动汽车充电基础设施的投资决策与充电分配，同时考虑时空需求动态及相互依赖；利用大语言模型（LLM）辅助从结构化自然语言描述生成并优化数学公式，显著降低建模负担；提出基于交替方向乘子法（ADMM）的分布式优化算法应对高维计算复杂度，通过成都150万真实出行记录的案例验证，总成本较无充电分配基线降低30%。

---

### [面向6G可持续连接的无人机辅助物联网中无线电能传输与意图驱动网络优化](https://arxiv.org/abs/2511.18368v1)

**日期**: 2025-11-28 | **作者**: Yue Hu, Xiaoming He, Rui Yuan et al.

**标签**: `Reinforcement Learning` `Transformer`

针对6G下无人机辅助物联网的资源分配问题，论文提出意图驱动的自主网络优化框架，预测模块用超维Transformer（HDT）嵌入数据到超维空间并替换传统操作，决策模块设计双动作多智能体近端策略优化（DA-MAPPO）响应意图与规划轨迹，解决高维动作序列扩展及机载计算密集的障碍。

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

### [NSTR：用于空间变化频率场的神经谱传输表示](https://arxiv.org/abs/2511.18384v1)

**日期**: 2025-11-28 | **作者**: Plein Versace

**标签**: `Deep Learning`

现有隐式神经表示（INR）假设全局平稳谱基，无法适配现实信号的空间频率变化；本文提出NSTR，显式建模空间变化局部频率场，引入可学习频率传输方程约束局部谱演化，通过空间调制全局正弦基重建信号，实验表明其精度-参数权衡优于SIREN等现有方法，收敛更快且具谱流解释性。

---

### [AVERY：基于具身自我意识的自适应VLM分割计算以实现高效灾害响应系统](https://arxiv.org/abs/2511.18151v1)

**日期**: 2025-11-28 | **作者**: Rajat Bhattacharjya, Sing-Yao Wu, Hyunwoo Oh et al.

**标签**: `Transformer` `Deep Learning`

针对灾害响应中无人机机载CNN语义推理能力不足、VLM部署资源需求高及云卸载低带宽失效问题，提出AVERY框架，采用认知启发的双流分割（高频低分辨率上下文流+低频高保真洞察流），并通过轻量化具身自我意识控制器动态适配网络条件与操作员意图以平衡精度-吞吐量 trade-off；实验表明其在LISA-7B VLM上表现优于静态配置，精度较原始图像压缩提升11.2%且能耗较全边缘执行降低93.98%，支持资源受限平台的实时可查询智能。

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

### [超越补丁聚合：用于视觉增强文档检索的三通道金字塔索引](https://arxiv.org/abs/2511.21121v1)

**日期**: 2025-11-28 | **作者**: Anup Roy, Rishabh Gyanendra Upadhyay, Animesh Rameshbhai Panara et al.

**标签**: `LLM` `NLP` `Deep Learning`

针对现有文档检索RAG管道依赖OCR、丢失空间线索及视觉优先模型内存开销大等问题，提出无OCR且模型无关的多模态检索系统VisionRAG；采用三通道金字塔索引框架构建含全局摘要、视觉热点等的轻量检索代理向量，检索时融合多信号排名，再将原始页面图像传给多模态LLM完成QA，降低存储与部署复杂度。

---

### [语义优势与取证效率：深度学习与心理语言学在商务邮件欺诈检测中的比较分析](https://arxiv.org/abs/2511.20944v1)

**日期**: 2025-11-28 | **作者**: Yaw Osei Adjei

**标签**: `NLP` `Deep Learning` `Transformer` `Anomaly`

论文针对每年造成超29亿美元损失的商务邮件欺诈（BEC），比较两种检测范式——基于DistilBERT的语义流（高精度需GPU）和基于CatBoost的取证心理语言流（低延迟低成本），在对抗性数据集上验证性能，为不同部署场景提供选型参考。

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

### [差分平滑缓解锐化并提升大语言模型推理能力](https://arxiv.org/abs/2511.19942v1)

**日期**: 2025-11-28 | **作者**: Jingchu Gai, Guanning Zeng, Huaqing Zhang et al.

**标签**: `LLM` `Reinforcement Learning` `Deep Learning` `NLP`

该论文形式化证明了大语言模型RL微调因选择与强化偏差导致多样性坍塌的机制，提出差分平滑方法——仅对正确轨迹应用奖励修改，可同时提升正确性与多样性，理论优于现有启发式方法，实验在AIME24等数据集验证了效果。

---

### [立场：完美AI对齐的复杂性——RLHF三难困境的形式化](https://arxiv.org/abs/2511.19504v1)

**日期**: 2025-11-28 | **作者**: Subramanyam Sahoo, Aman Chadha, Vinija Jain et al.

**标签**: `LLM` `Reinforcement Learning` `Deep Learning`

本文形式化RLHF的对齐三难困境（无法同时实现多样化人类价值代表性、多项式计算复杂度、对抗扰动鲁棒性）；通过结合统计学习与鲁棒优化的复杂度分析，证明全球规模代表性与鲁棒性需超多项式操作；指出当前RLHF以牺牲代表性解决该困境，框架解释了偏好坍塌等病理问题并给出缓解方向。

---

### [EfficientXpert：基于传播感知剪枝的大语言模型高效领域自适应](https://arxiv.org/abs/2511.19935v1)

**日期**: 2025-11-28 | **作者**: Songlin Zhao, Michael Pitts, Zhuwei Qin

**标签**: `LLM` `NLP` `Transformer`

针对大语言模型（LLM）领域适配中现有压缩方法跨域泛化差或开销高的问题，本文提出EfficientXpert框架，结合传播感知剪枝准则与高效适配器更新算法，集成LoRA微调实现通用模型到稀疏领域专家的一步转换；在健康、法律任务中40%稀疏度下保留98%密集模型性能，优于现有方法，且揭示领域结构变化需自适应剪枝策略。

---

### [SSA：通过特征空间对齐全注意力与稀疏注意力输出的稀疏稀疏注意力](https://arxiv.org/abs/2511.20102v1)

**日期**: 2025-11-28 | **作者**: Zhenyi Shen, Junru Lu, Lin Gui et al.

**标签**: `LLM` `Transformer` `Deep Learning`

全注意力的二次复杂度限制大语言模型（LLM）长上下文高效处理，现有稀疏注意力存在梯度更新不足（低秩键值对无梯度）导致稀疏度 paradox（低于全注意力）。论文提出SSA统一训练框架，层间双向对齐全/稀疏注意力输出，保留所有token梯度流并促进更强稀疏性；在多常识基准上实现稀疏/全推理SOTA，且支持模型平滑适配不同稀疏预算。

---

### [符号信道原理：衡量大语言模型通信中的意义容量](https://arxiv.org/abs/2511.19550v1)

**日期**: 2025-11-28 | **作者**: Davide Picca

**标签**: `LLM` `NLP` `Deep Learning` `Risk Management`

论文提出符号框架分析大语言模型（LLM），用信息论工具量化表达丰富度（源熵）与解释稳定性（消息和人类解释的互信息）的权衡，引入生成复杂度参数λ建模该权衡，定义符号信道并提出意义传输的容量约束，同时展示其在模型 profiling、提示设计等四方面的应用价值。

---

### [SWAN：基于无解压KV缓存压缩的稀疏筛选注意力机制以降低推理内存占用](https://arxiv.org/abs/2511.18936v1)

**日期**: 2025-11-28 | **作者**: Santhosh G S, Saurav Prakash, Balaraman Ravindran

**标签**: `LLM` `Transformer` `Deep Learning`

本文提出免微调框架SWAN，通过离线正交矩阵旋转剪枝KV缓存，无需解压即可直接用于注意力计算；实验表明，SWAN结合小稠密缓冲区可实现50-60%的单token内存节省且性能接近无压缩基线，还支持动态调整压缩级别，是LLM长上下文服务的高效实用方案。

---

### [Nemotron-Flash：面向延迟最优的混合小语言模型](https://arxiv.org/abs/2511.18890v1)

**日期**: 2025-11-28 | **作者**: Yonggan Fu, Xin Dong, Shizhe Diao et al.

**标签**: `LLM` `Deep Learning` `Transformer`

本文针对小语言模型（SLM）实际部署的延迟约束，指出参数效率未必对应实际设备速度提升，识别深度-宽度比（影响小批量延迟）和算子选择（影响延迟与吞吐量）为关键架构因素；通过进化搜索框架自动发现混合SLM中算子的延迟最优组合，结合权重归一化优化训练，推动准确率-延迟前沿。

---

### [面向高效视觉语言模型（VLMs）：基于信息论驱动的自适应结构剪枝压缩方法](https://arxiv.org/abs/2511.19518v1)

**日期**: 2025-11-28 | **作者**: Zhaoqi Xu, Yingying Zhang, Jian Li et al.

**标签**: `Transformer` `Deep Learning`

针对视觉语言模型（VLMs）规模过大导致部署困难且现有压缩方法缺乏理论保证的问题，提出基于信息论的自适应结构压缩框架InfoPrune，以信息瓶颈原理为基础，通过熵基有效秩（eRank）和KS距离量化注意力头贡献，设计训练型头剪枝与无训练FFN低秩近似互补方案；实验表明该方法可实现3.2x FLOP减少、1.8x加速且性能损失可忽略。

---

### [基于大语言模型的带噪声临床笔记下鲁棒公平下次就诊诊断预测研究](https://arxiv.org/abs/2511.18393v1)

**日期**: 2025-11-28 | **作者**: Heejoon Koo

**标签**: `LLM` `NLP` `Transformer`

针对临床笔记含噪声导致LLM诊断预测可靠性与公平性受影响的问题，该研究提出临床锚定的标签缩减方案及模拟医生推理的分层思维链策略，提升了噪声输入下预测的鲁棒性与亚组稳定性，推动LLM在临床决策支持系统中的可靠应用。

---

