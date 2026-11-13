# 量化研究入门 · Introduction to Quantitative Finance

> 中文开源量化知识库：用免费数据一步步做完的**项目式量化教程**，配合概念知识库、研报与论文目录，以及每天更新的 **FinPaperRadar（AI × 金融论文雷达）**。

<p align="center">
  <a href="https://barca0412.github.io/Introduction-to-Quantitative-Finance/"><strong>文档站</strong></a> ·
  <a href="https://barca0412.github.io/Introduction-to-Quantitative-Finance/tutorials/"><strong>教程</strong></a> ·
  <a href="https://barca0412.github.io/Introduction-to-Quantitative-Finance/arxiv/"><strong>论文雷达</strong></a> ·
  <a href="https://barca0412.github.io/Introduction-to-Quantitative-Finance/library/"><strong>研报与论文</strong></a> ·
  <a href="https://github.com/Barca0412/Introduction-to-Quantitative-Finance/discussions"><strong>参与讨论</strong></a>
</p>

<p align="center">
  <a href="https://github.com/Barca0412/Introduction-to-Quantitative-Finance/stargazers"><img src="https://img.shields.io/github/stars/Barca0412/Introduction-to-Quantitative-Finance?style=flat&color=ffd700" alt="GitHub stars"></a>
  <a href="https://github.com/Barca0412/Introduction-to-Quantitative-Finance/forks"><img src="https://img.shields.io/github/forks/Barca0412/Introduction-to-Quantitative-Finance?style=flat" alt="GitHub forks"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/Barca0412/Introduction-to-Quantitative-Finance" alt="MIT License"></a>
  <a href="https://huggingface.co/datasets/Barca21412/FinPaperRadar"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20dataset-FinPaperRadar-yellow" alt="FinPaperRadar dataset on Hugging Face"></a>
  <a href="https://atomgit.com/Barca12345/Introduction-to-Quantitative-Finance"><img src="https://atomgit.com/Barca12345/Introduction-to-Quantitative-Finance/star/new_badge.svg" alt="AtomGit G-Star"></a>
</p>

## 这里有什么

网上的量化资料很多，但大多只给概念或只给清单，初学者很难把"数据、因子、回测、组合"真正串起来做一遍。这个项目的核心是教程：每一讲用免费数据完成一个具体的研究任务，并说明结果怎么读、哪里容易出错。

| 栏目 | 内容 |
| --- | --- |
| [教程](https://barca0412.github.io/Introduction-to-Quantitative-Finance/tutorials/) | 每一讲是一个完整小项目，附代码、样例数据和练习 |
| [知识库](https://barca0412.github.io/Introduction-to-Quantitative-Finance/wiki/) | 多因子框架、数据源、因子、回测、组合优化的概念页 |
| [研报与论文](https://barca0412.github.io/Introduction-to-Quantitative-Finance/library/) | 194 份卖方金工研报、一百多篇学术论文的目录，以及讲义复现过的研报 |
| [论文雷达](https://barca0412.github.io/Introduction-to-Quantitative-Finance/arxiv/) | 每天抓取 arXiv 新论文，打标签、写中文摘要，支持语义检索 |
| [资源](https://barca0412.github.io/Introduction-to-Quantitative-Finance/resources/) | 精选开源项目、数据接口、论坛和课程 |

如果这个项目对你有帮助，欢迎点一个 Star ⭐，让更多量化学习者看到它。

## 讲义

首批因子投资讲义正在整理，上线后会列在这里和[教程页](https://barca0412.github.io/Introduction-to-Quantitative-Finance/tutorials/)。每一讲都按同样的结构写：要解决的问题、你会做出什么、数据与环境、分步实现、结果与解读、常见的坑（前视偏差、幸存者偏差、交易成本）、延伸阅读、练习。

<a id="section-arxiv"></a>

## FinPaperRadar · AI × 金融论文雷达

每天从 arXiv 的 10 个分类抓取新论文，用大模型打研究标签、提取关键词、写中文摘要，并提供趋势图、机构筛选和语义检索。入口：[barca0412.github.io/Introduction-to-Quantitative-Finance/arxiv/](https://barca0412.github.io/Introduction-to-Quantitative-Finance/arxiv/)。

完整历史数据以 Parquet 格式发布在 [Hugging Face 数据集](https://huggingface.co/datasets/Barca21412/FinPaperRadar)，GitHub Release [`radar-data`](https://github.com/Barca0412/Introduction-to-Quantitative-Finance/releases/tag/radar-data) 留有镜像，都不进 git。我们生成的标签、中文摘要、评分和向量按 CC BY 4.0 授权，arXiv 元数据本身是 CC0。流水线代码在 `scripts/arxiv_radar/`。

<!-- ARXIV_RADAR_STATUS:START -->
> [!NOTE]
> FinPaperRadar（AI × 金融论文雷达）machine-updated status
> - Latest update: 2026-11-13
> - Indexed papers: 28275
> - Focus papers: 16631
> - Latest publication date: 2026-11-12
> - Monitored categories: 10
> - Full dataset (CC BY 4.0 for FinPaperRadar additions): [Hugging Face](https://huggingface.co/datasets/Barca21412/FinPaperRadar) · [GitHub Release mirror](https://github.com/Barca0412/Introduction-to-Quantitative-Finance/releases/tag/radar-data)
<!-- ARXIV_RADAR_STATUS:END -->

<a id="section1"></a>

## 仓库里的资料

- [卖方金工研报](https://barca0412.github.io/Introduction-to-Quantitative-Finance/library/reports)：华泰人工智能、华泰多因子、海通、另类交易策略、基金研究等系列，原文件在 [`资料/卖方金工研报`](./资料/卖方金工研报)
- [论文](https://barca0412.github.io/Introduction-to-Quantitative-Finance/library/papers)：投资者情绪、行为金融学等方向，原文件在 [`论文`](./论文)
- [技术指标回测代码](./资料/技术指标回测代码)
- [量化研究实习中的代码笔记](https://github.com/Barca0412/Note-for-Programming)

<a id="section2"></a>

## 公开资料整理

- [数据源与另类数据](./资料/数据源与另类数据.md)
- [回测框架](./资料/回测.md)
- [因子挖掘与评估](./资料/因子挖掘.md)
- [因子组合（飞书文档）](https://xwfixqlhmsm.feishu.cn/wiki/PkCdw7MpKixStVkyIHwcTVhKngh?from=from_copylink)
- [投资组合优化与风控](./资料/投资组合优化与风控.md)

### 开源项目

#### 多因子量化框架
- [microsoft/qlib](https://github.com/microsoft/qlib) - AI导向量化投资平台，支持自动因子挖掘
- [etccapital/MultiFactor](https://github.com/etccapital/MultiFactor) - 基于华泰研报的多因子回测框架
- [HUANG-NI-YUAN/Multi-Factor_Model](https://github.com/HUANG-NI-YUAN/Multi-Factor_Model) - 15因子量化投资框架

#### 回测框架
- [kernc/backtesting.py](https://github.com/kernc/backtesting.py) - 简洁高效Python回测库
- [polakowo/vectorbt](https://github.com/polakowo/vectorbt) - 极速向量化回测，支持大规模参数优化
- [manifoldbt/manifoldbt](https://github.com/manifoldbt/manifoldbt) - 基于 Rust 核心的高性能 Python 回测引擎：向量化信号、真实成交（费用/滑点/前视偏差）、参数扫描、walk-forward、蒙特卡洛
- [stefan-jansen/zipline-reloaded](https://github.com/stefan-jansen/zipline-reloaded) - Quantopian事件驱动框架维护版

#### 因子挖掘与机器学习
- [RndmVariableQ/AlphaAgent](https://github.com/RndmVariableQ/AlphaAgent) - KDD 2025 LLM驱动因子挖掘
- [nshen7/alpha-gfn](https://github.com/nshen7/alpha-gfn) - GFlowNet挖掘alpha因子
- [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent) - 多Agent自动化R&D
- [AutoResearch-Factory/AgonAlpha](https://github.com/AutoResearch-Factory/AgonAlpha) - LLM多Agent自主alpha挖掘，WorldQuant BRAIN上60次提交获17个SPECTACULAR

#### 投资组合优化
- [dcajasn/Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib) - 专业组合优化，24种风险度量
- [PyPortfolioOpt](https://pyportfolioopt.readthedocs.io) - 高效前沿、Black-Litterman

#### 强化学习交易
- [AI4Finance-Foundation/FinRL](https://github.com/AI4Finance-Foundation/FinRL) - 开源金融强化学习框架
- [AI4Finance-Foundation/FinRL-Trading](https://github.com/AI4Finance-Foundation/FinRL-Trading) - 实盘交易v2.0

#### 深度学习时序预测
- [gonzalopezgil/xlstm-ts](https://github.com/gonzalopezgil/xlstm-ts) - 扩展LSTM时间序列预测
- [sinanw/lstm-stock-price-prediction](https://github.com/sinanw/lstm-stock-price-prediction) - LSTM多变量股价预测

#### 情感分析
- [FelixCharotte/NLP_Fnews](https://github.com/FelixCharotte/NLP_Fnews) - LLaMA 3财经新闻情感分析
- [Kanishk1420/FinReport](https://github.com/Kanishk1420/FinReport-Explainable-Stock-Earnings-Forecasting-via-News-Factor) - FinBERT+LSTM收益预测

#### 加密货币
- [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) - 开源加密货币交易机器人
- [Open-Trader/opentrader](https://github.com/Open-Trader/opentrader) - 自托管交易机器人

#### 综合平台
- [vnpy/vnpy](https://github.com/vnpy/vnpy) - VeighNa国产量化交易框架
- [leoncuhk/awesome-quant-ai](https://github.com/leoncuhk/awesome-quant-ai) - AI/ML量化资源精选
- [chaosquant2022/ML-Quant](https://github.com/chaosquant2022/ML-Quant) - 机器学习量化策略合集
- ...

### 高频交易

- [nkaz001/hftbacktest](https://github.com/nkaz001/hftbacktest) - 高频交易和做市回测框架，支持L2/L3 Tick数据
- [sohaibelkarmi/High-Frequency-Trading-Simulator](https://github.com/sohaibelkarmi/High-Frequency-Trading-Simulator) - 市场微观结构研究沙盒，C++17限价簿
- [visualHFT/VisualHFT](https://github.com/visualHFT/VisualHFT) - 实时市场微观结构分析，VPIN等指标
- [High-Frequency-Trading-Model-with-IB](https://github.com/jamesmawm/High-Frequency-Trading-Model-with-IB)
- [hummingbot:high-frequency crypto trading bots](https://github.com/hummingbot/hummingbot)
- [tribeca:A high frequency, market making cryptocurrency trading platform](https://github.com/michaelgrosner/tribeca)
- ...

### 基金研究

- [FundCombination](https://github.com/MrDujing/FundCombination)
- 基金研究相关的卖方研报见 [研报目录 · 基金研究](https://barca0412.github.io/Introduction-to-Quantitative-Finance/library/reports#基金研究)
- ...

### 量化论坛

- 国内

  - [聚宽量化交易平台](https://www.joinquant.com/)
  - [VeighNa量化社区](https://www.vnpy.com/forum/)
  - [掘金量化社区](https://bbs.myquant.cn/)
  - [Datayes!优矿](https://uqer.datayes.com/v3/community/list)
  - [开拓者社区](https://www.tbquant.net/forum)
  - [BigQuant](https://bigquant.com/)
  - [发明者量化](https://www.fmz.com/)
  - [真格量化](https://quant.pobo.net.cn/login#/)
  - ...
- 国外

  - [Allocate Smartly](https://allocatesmartly.com/)
  - [Financial Hacker](https://financial-hacker.com/)
  - [Quantstart](https://www.quantstart.com/)
  - [Macrosynergy](https://research.macrosynergy.com/)
  - [Raposa](https://raposa.trade/blog/)
  - [Finominal](https://finominal.com/?country=US)
  - ...

### 课程&学习

- [金融大数据量化分析](https://github.com/plouto-quants/FBDQA-2019A)
- [人大：《金融计量与量化策略分析》《量化投资交易策略分析与系统设计》](https://github.com/xhlgogo/Quantitative-Investment-Trading-system)
- [Datawhale量化开源课程](https://github.com/datawhalechina/whale-quant)
- ...

### 一些工具[暂存]

- [Connected papers](https://www.connectedpapers.com/)
- [from Data to Viz](https://www.data-to-viz.com/)
- [Python Graph Gallery](https://python-graph-gallery.com/)
- [查金融工作论文:SSRN](https://www.ssrn.com/index.cfm/en/)
- [arxiv](https://arxiv.org/)
- ...

## 交流与合作

本项目由湖南大学金融科技协会 Quant Group 维护。欢迎交流讲义内容、数据集使用、课程合作或研究合作。

- Email：qgh124430@hnu.edu.cn / guohaoqi@u.nus.edu
- 微信：qgh985695077
- [湖南大学金融科技协会介绍](https://www.guohaoqi.cn/hft-association)

<div align="center">
  <img width="420" alt="扫码加入湖南大学金融科技协会 HFT 成员群和实习群" src="https://github.com/user-attachments/assets/60a940e6-88b6-4c6d-ae86-6c125085ca14" />
</div>

署名、授权和引用方式见[关于页](https://barca0412.github.io/Introduction-to-Quantitative-Finance/about)。

<a id="contributing"></a>

## 参与贡献

欢迎修正错误、补充资料、改进讲义。怎么写一讲新讲义、资源清单收录什么样的项目，见 [CONTRIBUTING.md](./CONTRIBUTING.md)。有想法可以先在 [Discussions](https://github.com/Barca0412/Introduction-to-Quantitative-Finance/discussions) 交流。

## Star History

<div align="center">
  <img src="https://api.star-history.com/svg?repos=Barca0412/Introduction-to-Quantitative-Finance&type=Date" alt="Star History Chart" width="600">
</div>

---

本项目用于教育与研究，不构成投资建议。
