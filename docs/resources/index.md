# 量化金融GitHub资源推荐清单

*基于 Introduction-to-Quantitative-Finance repo 补充的开源项目和资料 (63个项目)*

---

## 目录

[[toc]]

---

## 多因子量化框架

| 项目 | 说明 |
|------|------|
| [etccapital/MultiFactor](https://github.com/etccapital/MultiFactor) | 基于华泰证券金工研报的实用多因子回测框架，包含因子数据收集、单因子测试、收益模型、风险模型 |
| [HUANG-NI-YUAN/Multi-Factor_Model](https://github.com/HUANG-NI-YUAN/Multi-Factor_Model) | 量化投资中的多因子框架，包含15个因子，生成回测报告 |
| [microsoft/qlib](https://github.com/microsoft/qlib) | AI导向的量化投资平台，支持多种机器学习范式、市场动态建模、强化学习、自动因子挖掘，含RD-Agent自动R&D |

---

## 回测框架与系统

| 项目 | 说明 |
|------|------|
| [kernc/backtesting.py](https://github.com/kernc/backtesting.py) | 简洁高效的Python回测库，快速执行、内置优化器、详细结果分析 |
| [letianzj/quanttrader](https://github.com/letianzj/quanttrader) | 纯Python事件驱动回测和实盘交易系统，支持股票/期货/期权/外汇，集成IB API |
| [polakowo/vectorbt](https://github.com/polakowo/vectorbt) | 极速向量化回测库，基于NumPy和Numba，支持超大规模参数优化，集成Plotly可视化 |
| [stefan-jansen/zipline-reloaded](https://github.com/stefan-jansen/zipline-reloaded) | Quantopian事件驱动回测框架的维护版本，支持多个市场，Pandas集成 |

---

## 因子挖掘与机器学习

| 项目 | 说明 |
|------|------|
| [nshen7/alpha-gfn](https://github.com/nshen7/alpha-gfn) | 用生成流网络(GFlowNet)挖掘alpha因子，深度强化学习框架 |
| [RndmVariableQ/AlphaAgent](https://github.com/RndmVariableQ/AlphaAgent) | KDD 2025论文代码，LLM驱动的自动因子挖掘，三个专门Agent(想法、因子、评估) |
| [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent) | 多Agent框架用于因子挖掘和模型优化，自动化R&D流程 |
| [ezphuang/rf_stock](https://github.com/ezphuang/rf_stock) | 基于随机森林和多因子模型的选股模型 |

---

## 投资组合优化与风险管理

| 项目 | 说明 |
|------|------|
| [dcajasn/Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib) | 专业投资组合优化库，24种风险度量、均值风险优化、风险平价、CVaR、Maximum Drawdown |
| [PyPortfolioOpt](https://pyportfolioopt.readthedocs.io) | 投资组合优化方法实现，高效前沿、Black-Litterman配置 |
| [Gouldh/ML-Portfolio-Optimization](https://github.com/Gouldh/ML-Portfolio-Optimization) | 机器学习和金融理论结合的投资组合优化，因子分析、Black-Litterman模型 |
| [domokane/FinancePy](https://github.com/domokane/FinancePy) | 衍生品定价和风险管理库，期权/期货定价，使用Numba实现C++级性能 |

---

## 数据获取与处理

| 项目 | 说明 |
|------|------|
| [ranaroussi/yfinance](https://github.com/ranaroussi/yfinance) | Yahoo Finance数据获取库，支持实时流媒体、期权数据、分红等 |
| [Ravdar/yfinance-downloader](https://github.com/Ravdar/yfinance-downloader) | 可视化界面的Yahoo Finance数据下载工具，GUI界面、支持Excel输出 |
| [maxisoft/yahoo-finance-data-downloader](https://github.com/maxisoft/yahoo-finance-data-downloader) | 自动化高效OHLCV数据下载脚本，多线程支持 |

---

## 技术指标与信号

| 项目 | 说明 |
|------|------|
| [mzyates/techindicators](https://github.com/mzyates/techindicators) | 纯NumPy实现的技术指标计算，移动平均、RSI、MACD、CCI等 |
| [elkingarcia11/indicator-calculator](https://github.com/elkingarcia11/indicator-calculator) | 技术指标计算模块，RSI、Stochastic RSI、MACD、ROC、ATR、Bollinger Bands |
| [ubc-mds/stocksignalsr](https://github.com/ubc-mds/stocksignalsr) | 股票买卖信号计算工具(R包)，200日均线、10vs20日交叉、Bollinger Bands |

---

## 衍生品定价

| 项目 | 说明 |
|------|------|
| [ilchen/options-pricing](https://github.com/ilchen/options-pricing) | 欧式和美式期权定价，EWMA和GARCH模型波动率估计，yield curve构造 |
| [just-krivi/option-pricing-models](https://github.com/just-krivi/option-pricing-models) | 欧式期权定价(Black-Scholes、蒙特卡洛、二叉树)，Streamlit Web应用 |
| [AmirDehkordi/OptionGreeks](https://github.com/AmirDehkordi/OptionGreeks) | 期权希腊字母计算和可视化，Delta、Gamma、Theta、Vega等2D和3D可视化 |
| [JRCon1/greeks-package](https://pypi.org/project/greeks/) | 完整希腊字母计算包(一、二、三阶)，无外部依赖，集成Yahoo Finance期权链 |

---

## 深度学习与时间序列

| 项目 | 说明 |
|------|------|
| [sinanw/lstm-stock-price-prediction](https://github.com/sinanw/lstm-stock-price-prediction) | LSTM多变量时间序列股价预测，完整三阶段工作流(EDA、预处理、建模) |
| [034adarsh/Stock-Price-Prediction-Using-LSTM](https://github.com/034adarsh/Stock-Price-Prediction-Using-LSTM) | LSTM股价预测项目，使用yfinance实时数据，Streamlit Web应用 |
| [A-safarji/Time-series-deep-learning](https://github.com/A-safarji/Time-series-deep-learning) | 多模型时间序列预测(LSTM、BiLSTM、NeuralProphet)，PyTorch实现 |
| [gonzalopezgil/xlstm-ts](https://github.com/gonzalopezgil/xlstm-ts) | 扩展LSTM用于时间序列预测，集成小波去噪，股票趋势预测 |

---

## 强化学习交易

| 项目 | 说明 |
|------|------|
| [AI4Finance-Foundation/FinRL](https://github.com/AI4Finance-Foundation/FinRL) | 第一个开源金融强化学习框架，完整生态，支持多个市场、多种DRL算法 |
| [manojravindran90/FinRL-Library](https://github.com/manojravindran90/FinRL-Library) | FinRL库实现，DQN、DDPG、PPO、SAC、A2C、TD3算法 |
| [AI4Finance-Foundation/FinRL-Trading](https://github.com/AI4Finance-Foundation/FinRL-Trading) | FinRL交易平台v2.0，模块化设计、策略框架、风险管理、Alpaca实盘 |
| [theanh97/Deep-RL-Stock-Trading](https://github.com/theanh97/Deep-Reinforcement-Learning-with-Stock-Trading) | 股票交易DRL应用，PPO、A2C、DDPG、SAC、TD3，包含交易成本 |
| [Albert-Z-Guo/Deep-Reinforcement-Stock-Trading](https://github.com/Albert-Z-Guo/Deep-Reinforcement-Stock-Trading) | DRL投资组合管理，模块化可扩展框架 |
| [ICAIF-2020集成策略](https://github.com/Jung132914/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020) | 集成DRL策略(PPO、A2C、DDPG)，ICAIF 2020论文 |

---

## 高频交易与市场微观结构

| 项目 | 说明 |
|------|------|
| [nkaz001/hftbacktest](https://github.com/nkaz001/hftbacktest) | 高频交易和做市回测框架，考虑限价订单、队列位置、延迟，使用L2/L3 Tick数据 |
| [sohaibelkarmi/High-Frequency-Trading-Simulator](https://github.com/sohaibelkarmi/High-Frequency-Trading-Simulator) | 市场微观结构研究沙盒，C++17限价簿、Hawkes过程、Streamlit前端 |
| [visualHFT/VisualHFT](https://github.com/visualHFT/VisualHFT) | 实时市场微观结构分析的WPF/C#桌面应用，限价簿可视化、VPIN等微观结构指标 |

---

## 情感分析与新闻处理

| 项目 | 说明 |
|------|------|
| [FelixCharotte/NLP_Fnews](https://github.com/FelixCharotte/NLP_Fnews) | 财经新闻情感分析NLP项目，使用LLaMA 3微调，结合Binance数据回测 |
| [EthanFalcao/Sentiment-Analysis-in-Financial-Markets](https://github.com/EthanFalcao/Sentiment-Analysis-in-Financial-Markets) | 财经新闻、财报、社交媒体情感分析，BERT处理 |
| [MayCooper/Stock-Market-Sentiment-Analysis](https://github.com/MayCooper/Stock-Market-Sentiment-Analysis-NLP-GloVe-TensorFlow) | 股市新闻情感分析，GloVe嵌入、TensorFlow/Keras、NLTK |
| [sandesha21/Stock-Market-News-Sentiment](https://github.com/sandesha21/Stock-Market-News-Sentiment-Analysis-and-Summarization) | 股市新闻情感分析和摘要生成，NLP、AI技术识别市场移动事件 |
| [Kanishk1420/FinReport](https://github.com/Kanishk1420/FinReport-Explainable-Stock-Earnings-Forecasting-via-News-Factor) | 通过新闻因子预测股票收益，FinBERT情感分析、LSTM预测、EGARCH风险评估 |

---

## 加密货币交易

| 项目 | 说明 |
|------|------|
| [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) | 免费开源加密货币交易机器人，支持多交易所、回测、策略优化、Telegram/WebUI控制 |
| [Open-Trader/opentrader](https://github.com/Open-Trader/opentrader) | 自托管加密货币交易机器人，内置策略(GRID、DCA、RSI)、纸盘交易、回测 |
| [Allora_HyperLiquid_AutoTradeBot](https://github.com/HarbhagwanDhaliwal/Allora_HyperLiquid_AutoTradeBot) | AI驱动的交易机器人(AlloraNetwork + HyperLiquid DEX) |

---

## 综合平台与生态

| 项目 | 说明 |
|------|------|
| [vnpy/vnpy](https://github.com/vnpy/vnpy) | 基于Python的开源量化交易系统框架(VeighNa)，活跃社区，多功能，已用于金融机构 |
| [leoncuhk/awesome-quant-ai](https://github.com/leoncuhk/awesome-quant-ai) | 量化投资AI/ML资源精选列表，策略、工具平台、学习资源、研究论文、社区 |
| [barter-rs/barter-rs](https://github.com/barter-rs/barter-rs) | Rust算法交易生态，高性能、多线程、模块化(策略、风险管理)，支持实盘/纸盘/回测 |

---

## 波动率预测

| 项目 | 说明 |
|------|------|
| [iskakovs/GARCH-models](https://github.com/iskakovs/GARCH-models) | GARCH模型股票波动率预测，GARCH(1,1)、GARCH-M、EGARCH等 |
| [tommasograndi/market-vol-forecasting](https://github.com/tommasograndi/market-vol-forecasting-with-GARCH-models) | FTSE MIB 100指数波动率预测，GARCH、EGARCH、TGARCH、GJR-GARCH对比 |

---

## 股票选择与基本面分析

| 项目 | 说明 |
|------|------|
| [SarmadTanveer/F-Score-Calculator](https://github.com/SarmadTanveer/F-Score-Calculator) | Piotroski F-Score计算工具，财务报表分析、价值投资 |
| [brodyu/predicting-earnings-surprises](https://github.com/brodyu/predicting-earnings-surprises) | 收益惊喜预测，多数据源集成、机器学习预测 |
| [pchernic/Stocks_Quant_Analysis](https://github.com/pchernic/Stocks_Quant_Analysis) | 股票定量分析(yfinance、pandas、matplotlib)，时间序列、相关性、收益等 |
| [pranjal-joshi/Screeni-py](https://github.com/pranjal-joshi/Screeni-py) | 印度NSE股票筛选器，基于突破概率的技术筛选 |

---

## 财务指标与估值

| 项目 | 说明 |
|------|------|
| [JerBouma/FinanceToolkit](https://github.com/JerBouma/FinanceToolkit) | 财务工具包，计算130+财务指标，效率、流动性、盈利能力、偿债能力、估值指标 |

---

## K线图案识别

| 项目 | 说明 |
|------|------|
| [l33tquant/candlestick](https://github.com/l33tquant/candlestick) | Rust实现的K线图案识别库，无依赖、no_std兼容、30+传统日本K线图案 |
| [ruejo2013/ML-Candlestick-Recognition](https://github.com/ruejo2013/Machine-Learning-Candlestick-Recognition-Trading-Strategy) | 机器学习K线图案识别，Naive Bayes、神经网络预测市场走势 |
| [Narfinsel/Candlestick-Pattern-Scanner](https://github.com/Narfinsel/Candlestick-Pattern-Scanner) | K线图案扫描工具(MQL5)，智能交易系统的反转信号检测 |

---

## 风险分析

| 项目 | 说明 |
|------|------|
| [JZ-LIANG/Monte-Carlo-VaR](https://github.com/JZ-LIANG/Stocks-Risk-Analysis-using-Monte-Carlo-Simulation) | 蒙特卡洛模拟和多元回归的投资组合风险分析，VaR(风险价值)估计 |
| [jameshopham/Monte-Carlo-VaR](https://github.com/jameshopham/Application-of-Monte-Carlo-Simulations-in-VaR) | 蒙特卡洛模拟在VaR中的应用，时间序列特征工程、风险度量可视化 |
| [akashdeepo/ML-Finance-Monte-Carlo-RRR](https://github.com/akashdeepo/ML-Finance-Monte-Carlo-RRR) | 集成蒙特卡洛和集成机器学习的市场预测，风险-收益比分析 |

---

## 推荐使用组合方案

### 初学者量化框架
1. **数据获取**: yfinance
2. **技术指标**: techindicators 或 indicator-calculator
3. **回测**: backtesting.py 或 vectorbt
4. **投资组合**: Riskfolio-Lib 或 PyPortfolioOpt

### 专业研究者
1. **多因子框架**: microsoft/qlib 或 etccapital/MultiFactor
2. **因子挖掘**: RndmVariableQ/AlphaAgent (LLM) 或 nshen7/alpha-gfn (RL)
3. **回测系统**: vectorbt (向量化) 或 zipline-reloaded (事件驱动)
4. **深度学习**: FinRL 或 xlstm-ts

### 高频交易研发
1. **回测**: hftbacktest 或 High-Frequency-Trading-Simulator
2. **市场微观结构**: VisualHFT
3. **分析**: 定制化C++/Rust引擎

### 加密货币交易
1. **机器人框架**: freqtrade 或 opentrader
2. **数据源**: ccxt库集成
3. **策略**: 网格、DCA、技术分析

---

## 学习路径建议

### 第一阶段：基础工具 (1-2周)
- 学习yfinance获取数据
- 理解基本技术指标
- 完成第一个简单回测

### 第二阶段：多因子框架 (2-3周)
- 理解多因子模型概念
- 学习MultiFactor或Qlib
- 自行构建单因子并测试

### 第三阶段：高级技术 (3-4周)
- 学习投资组合优化理论
- 尝试机器学习预测(LSTM/RandomForest)
- 理解风险管理框架

### 第四阶段：生产部署 (4-6周)
- 选择合适的回测框架(向量化 vs 事件驱动)
- 构建完整的交易系统
- 实盘前的充分回测和纸盘交易

---

*更新日期: 2025年11月27日 | 来源: GitHub系统搜索(80+项目)*
