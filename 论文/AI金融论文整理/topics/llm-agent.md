# LLM & Agent

大语言模型与金融智能体在量化金融中的应用

> 共收录 **55** 篇论文 | [返回索引](../README.md)

---

### [基于量子分布组合电路（QDisCoCirc）的金融文本情感分析](https://arxiv.org/abs/2511.18804v1)

**日期**: 2025-11-28 | **作者**: Takayuki Sakuma

**标签**: `Sentiment Analysis` `NLP` `Transformer` `Investor Sentiment`

该论文将量子分布组合电路（QDisCoCirc）应用于金融文本三分类情感分析，通过分解句子为短连续chunk并映射到浅量子电路得到Bloch向量序列；采用量子token+小Transformer编码器+CCG类型嵌入的混合设计，既保留量子语义可解释性，又能建模语序与长依赖，提升了测试macro-F1，且chunk归因显示证据集中于少数chunk、正确预测句子更可靠使用类型嵌入。

---

### [基于LLM驱动的代码进化的认知阿尔法挖掘](https://arxiv.org/abs/2511.18850v1)

**日期**: 2025-11-28 | **作者**: Fengyuan Liu, Huang Yi, Sichun Luo et al.

**标签**: `LLM` `Factor Mining` `Asset Pricing` `Algorithmic Trading`

针对现有阿尔法挖掘方法搜索空间狭窄、模型不透明或经济依据不足等问题，本文提出CogAlpha框架，融合代码级阿尔法表示、LLM驱动推理与进化搜索，通过多阶段提示和金融反馈迭代优化候选阿尔法；在A股市场的实验表明，该框架挖掘的阿尔法在预测精度、鲁棒性和泛化性上均优于现有方法。

---

### [重新思考检索：金融领域大语言模型从传统检索增强生成到智能体与非向量推理系统的演进](https://arxiv.org/abs/2511.18177v1)

**日期**: 2025-11-28 | **作者**: Elias Lumer, Matt Melich, Olivia Zino et al.

**标签**: `LLM` `NLP` `Financial Agent` `Benchmark`

本文首次系统对比金融文档的向量基智能体RAG（混合搜索+元数据过滤）与非向量层次节点基RAG架构，评估交叉编码器重排序、小到大分块检索两种增强技术的效果；基于1200份SEC文件和150题基准，测检索指标、回答质量、 latency及成本，发现向量基智能体RAG更优，两种增强技术显著提升性能。

---

### [MortgageLLM：带残差指令迁移、对齐调优和任务特定路由的领域自适应预训练](https://arxiv.org/abs/2511.21101v1)

**日期**: 2025-11-28 | **作者**: Manish Jain, Satheesh Kumar Ponnambalam, Salman Faroz et al.

**标签**: `LLM` `NLP` `Financial Agent` `Transformer`

论文提出抵押贷款领域专用大模型MortgageLLM，采用双轨特化框架从LLaMA-3.1-8B构建对话问答与结构化任务两个专家模型，通过指令残差技术恢复指令遵循能力并设计智能任务路由机制，在领域基准上显著优于基础模型。

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

### [专家角色大语言模型的自我透明性失败：大规模行为审计](https://arxiv.org/abs/2511.21569v1)

**日期**: 2025-11-28 | **作者**: Alex Diep

**标签**: `LLM` `Behavioral Finance` `NLP`

该研究采用common-garden设计，对16个开源LLM（4B-671B参数）开展19200次试验，审计其专家角色下的自我透明性（披露AI身份）；发现模型在不同领域披露率差异显著（如金融顾问30.8% vs神经外科医生3.5%），模型身份比参数规模更能预测行为，推理优化可能抑制透明性，强调透明性由训练因素决定而非规模，需刻意设计与实证验证。

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

### [KOM：用于膝骨关节炎（KOA）精准管理的多智能体人工智能系统](https://arxiv.org/abs/2511.19798v1)

**日期**: 2025-11-28 | **作者**: Weizhi Liu, Xi Chen, Zekun Jiang et al.

**标签**: `LLM` `Deep Learning` `Risk Management`

针对全球超6亿膝骨关节炎（KOA）患者个性化多学科干预资源不足的问题，开发多智能体系统KOM，可自动化KOA评估、风险预测与治疗处方；实验显示其在影像分析和处方生成上优于通用大模型，且与临床医生协作能提升诊疗效率（减少38.5%时间）和治疗质量。

---

### [理解Transformer学习潜在结构的阶段性动态](https://arxiv.org/abs/2511.19328v1)

**日期**: 2025-11-28 | **作者**: Rohan Saha, Farzane Aminmansour, Alona Fyshe

**标签**: `Transformer` `Benchmark` `Deep Learning` `LLM`

本文使用Alchemy基准，训练仅解码器Transformer并在三类任务（推断缺失规则、组合简单规则解决多步序列、分解复杂例子推断中间步骤）上研究其潜在结构学习的动态；发现模型分阶段掌握能力（先学粗粒度规则再学完整结构），且存在“能稳健组合基本规则但难分解复杂例子发现规则”的关键不对称性，为理解Transformer的潜在结构学习提供了细粒度视角。

---

### [多语言大语言模型的生成式查询扩展用于跨语言信息检索](https://arxiv.org/abs/2511.19325v1)

**日期**: 2025-11-28 | **作者**: Olivia Macmillan-Scott, Roksana Goworek, Eda B. Özyiğit

**标签**: `LLM` `NLP`

该研究采用多语言大语言模型（mLLMs）开展生成式查询扩展（以伪文档生成替代传统同义词增强），评估不同策略及微调变体以识别跨语言检索性能驱动因素；发现查询长度决定有效提示技术、语言脚本差异显著制约跨语言检索、微调仅在训练测试格式匹配时增益明显，强调需更平衡的多语言训练与评估资源。

---

### [机器N400：精确定位因果语言模型检测语义违规的位置](https://arxiv.org/abs/2511.19232v1)

**日期**: 2025-11-28 | **作者**: Christos-Nikolaos Zacharopoulos, Revekka Kyriakoglou

**标签**: `LLM` `NLP` `Transformer` `Deep Learning`

该研究以因果语言模型phi-2为对象，通过精心构建的含合理/不合理结尾句子的语料，分析各层隐藏状态；利用线性探针和有效维度分析发现，语义违规检测在模型低层难区分、中层后准确率提升，且表征子空间先扩后缩，还联系了人类心理语言学的相关发现。

---

### [基于远程监督的语言无关情感标注：以英语、Sepedi语和Setswana语为例](https://arxiv.org/abs/2511.19818v1)

**日期**: 2025-11-28 | **作者**: Koena Ronny Mabokela, Tim Schlippe, Mpho Raborife et al.

**标签**: `NLP` `Sentiment Analysis`

本文针对非洲低资源语言缺乏情感标注数据的问题，提出一种基于情感表情和词汇的自动语言无关情感标注方法；利用SAfriSenti南非多语言情感语料实验，英语、Sepedi语和Setswana语标注准确率分别达66%、69%和63%，平均仅需修正34%自动标注结果，有效降低手动标注成本。

---

### [打破安全-能力权衡：带可验证奖励的强化学习在大语言模型中维持安全护栏](https://arxiv.org/abs/2511.21050v1)

**日期**: 2025-11-28 | **作者**: Dongkyu Derek Cho, Huan Song, Arijit Ghosh Chowdhury et al.

**标签**: `LLM` `Reinforcement Learning` `Transformer` `Benchmark`

论文指出大语言模型微调存在安全-能力权衡，现有SFT、RLHF等方法无法避免；首次对带可验证奖励的强化学习（RLVR）进行理论与实证分析，推导KL约束下安全漂移上界并证明消除安全退化的条件，实验显示RLVR可同时提升推理能力与安全护栏，挑战了必然权衡的假设。

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

### [论大语言模型天生规划能力的局限性](https://arxiv.org/abs/2511.21591v1)

**日期**: 2025-11-28 | **作者**: Charles Schepanowski, Charles Ling

**标签**: `LLM` `NLP` `Benchmark`

该研究以经典8-puzzle任务（无需外部工具）测试大语言模型（LLM）的规划与状态推理能力，在不同提示条件及反馈下评估多模型表现；发现无外部工具时LLM规划能力存在显著局限（状态表示脆弱、启发式规划弱），指出需显式状态维护与结构化搜索机制提升规划能力。

---

### [BAMAS：构建预算感知型多智能体系统](https://arxiv.org/abs/2511.21572v1)

**日期**: 2025-11-28 | **作者**: Liming Yang, Junyu Luo, Xuanzhe Liu et al.

**标签**: `LLM` `Reinforcement Learning` `NLP`

该论文针对现有LLM多智能体系统缺乏显式预算约束下结构设计的问题，提出BAMAS方法——先通过整数线性规划选择平衡性能与成本的最优LLM集合，再用强化学习确定智能体交互拓扑并实例化执行；实验表明BAMAS在保持相当性能的同时，成本最多降低86%。

---

### [MADRA：面向风险感知具身规划的多智能体辩论框架](https://arxiv.org/abs/2511.21460v1)

**日期**: 2025-11-28 | **作者**: Junjian Wang, Lidan Zhao, Xi Sheryl Zhang

**标签**: `LLM` `Risk Management` `Benchmark`

针对具身AI任务规划中现有方法计算成本高或过度拒绝的问题，提出无训练的MADRA多智能体辩论风险评估框架，通过多个LLM代理辩论指令安全性、关键评估者打分及迭代共识投票，减少误拒并保持危险任务敏感性；还引入分层认知协作规划框架提升任务成功率，贡献SafeAware-VH基准数据集，实验验证其性能优于现有方法。

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

### [Chatty-KG：面向知识图谱的按需对话式问答多智能体AI系统](https://arxiv.org/abs/2511.20940v1)

**日期**: 2025-11-28 | **作者**: Reham Omar, Abdelghny Orogat, Ibrahim Abdelaziz et al.

**标签**: `LLM` `NLP` `Financial Agent`

论文提出模块化多智能体系统Chatty-KG，针对现有RAG序列化结构、多轮上下文处理不足及传统KGQA单轮问答等局限，通过任务专用LLM智能体协作（上下文解释、对话跟踪等）结合RAG检索与结构化执行，实现自然问题到可执行SPARQL查询的准确低延迟转换；实验在多规模多样化KG上显著优于SOTA基线，模块化设计支持动态KG无需微调预训练。

---

### [NOIR 2.0：面向日常活动的神经信号操控智能机器人](https://arxiv.org/abs/2511.20848v1)

**日期**: 2025-11-28 | **作者**: Tasha Kim, Yingke Wang, Hanvit Cho et al.

**标签**: `Deep Learning` `LLM`

该论文提出增强版脑机接口系统NOIR 2.0，通过更快更准确的脑信号解码算法将人类意图转化为机器人指令，任务完成时间减少46%；同时采用结合基础模型的少样本机器人学习算法，提升对个体用户的适应性与意图预测效率，显著降低人类操作时间65%。

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

### [智能制造中的混合智能体AI与多智能体系统](https://arxiv.org/abs/2511.18258v1)

**日期**: 2025-11-28 | **作者**: Mojtaba A. Farahani, Md Irfan Khan, Thorsten Wuest

**标签**: `LLM` `Anomaly` `Transformer`

本文提出面向智能制造预测性维护的混合智能体AI与多智能体框架，以LLM智能体实现战略编排与自适应推理，结合规则及SLM智能体完成边缘端高效领域任务，分层架构由LLM Planner协调工作流；该框架支持动态模型适应、成本高效维护调度及可解释决策，经工业数据集验证且模块化可扩展。

---

### [LLM能否做出（个性化）访问控制决策？](https://arxiv.org/abs/2511.20284v1)

**日期**: 2025-11-28 | **作者**: Friederike Groschupp, Daniele Lain, Aritra Dhar et al.

**标签**: `LLM` `NLP` `Behavioral Finance`

针对用户访问控制决策认知负荷过重问题，论文提出利用LLM实现动态上下文感知的访问控制决策方法；通过用户研究构建含307条隐私陈述与14682条用户决策的数据集，对比通用及个性化LLM的决策效果，发现通用LLM匹配多数用户偏好准确率达86%，且个性化存在提升个体匹配与违反安全最佳实践的权衡。

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

### [用于表格数据分析的多模态对话代理](https://arxiv.org/abs/2511.18405v1)

**日期**: 2025-11-28 | **作者**: Mohammad Nour Al Awad, Sergey Ivanov, Olga Tikhonova et al.

**标签**: `LLM` `NLP` `Financial Agent`

本文提出多模态对话代理Talk2Data，整合LLM、自动语音识别（Whisper）、文本转语音（Coqui）、代码生成（Qwen-coder）及沙盒执行工具，支持语音/文本交互与多轮上下文感知对话；实验在3个数据集48个任务上实现95.8%准确率，7B参数LLM在准确率、延迟与成本间取得最优平衡，计算过程可验证。

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

### [基于大语言模型的带噪声临床笔记下鲁棒公平下次就诊诊断预测研究](https://arxiv.org/abs/2511.18393v1)

**日期**: 2025-11-28 | **作者**: Heejoon Koo

**标签**: `LLM` `NLP` `Transformer`

针对临床笔记含噪声导致LLM诊断预测可靠性与公平性受影响的问题，该研究提出临床锚定的标签缩减方案及模拟医生推理的分层思维链策略，提升了噪声输入下预测的鲁棒性与亚组稳定性，推动LLM在临床决策支持系统中的可靠应用。

---

