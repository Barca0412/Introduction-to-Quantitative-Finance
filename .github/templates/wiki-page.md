---
# 知识库概念页模板。复制到 docs/wiki/（因子相关放 docs/wiki/factors/），文件名用英文短名，例如 ic.md。
# 以 # 开头的注释行可以删掉。
title: IC、RankIC 与 ICIR
# 80–120 字，写给搜索引擎和 AI 看：这个概念是什么、怎么算、A 股上怎么用。
description: 信息系数（IC）衡量因子值和下期收益的相关程度，是检验因子是否有效的核心指标。本页给出 IC、RankIC、ICIR 的定义和公式，并用 AKShare 的免费 A 股数据算一遍。
wiki:
  level: 入门                    # 入门 / 进阶 / 高级
  prerequisites: [因子预处理]     # 读这页之前最好先懂的概念
  code: true                     # 页面里有可运行代码时写 true
---

# IC、RankIC 与 ICIR

<!--
写作要求：
- 每个事实都给出处（论文、教材章节、官方文档或仓库里的研报），放在"出处"一节。
- 代码必须在全新环境里能跑通，只用读者免费拿得到的数据（AKShare 等），30 行以内为宜。
- 实证图由这段代码真实生成，图片放 docs/public/wiki/<页面名>/。
- 不写"内容建设中"之类的占位文字；还没写的小节就先不放。
- 讲单个因子的页面，在"直觉和例子"之后加三节：起源、成因、A 股实证。
-->

**一句话：** 用一两句话直接给出结论，读者和搜索引擎只读这一段也能拿到答案。

## 直觉和例子

用一个具体的 A 股例子说明这个概念在研究里解决什么问题。

## 公式

$$
\mathrm{IC}_t = \operatorname{corr}\left(f_{i,t},\; r_{i,t+1}\right)
$$

逐个解释公式里的符号。

## 最小可运行代码

```python
# pip install akshare pandas
import akshare as ak
import pandas as pd

# ……从取数据到算出结果，保持 30 行以内
```

运行结果：

![本页实证图](/wiki/ic/example.png)

## 结果怎么读

经验阈值写清楚出自谁（例如"研报常用 |IC| > 0.02 作为有效门槛"要给出处），并说明它的适用范围。

## 常见的坑

- **前视偏差**：
- **幸存者偏差**：
- **交易成本**：

## 工具

- [alphalens-reloaded](https://github.com/stefan-jansen/alphalens-reloaded)：……

## 出处

- 论文：作者（年份）. 标题. 期刊. DOI 链接
- 教材：书名，章节
- 研报：链接到[研报目录](/library/reports)里的原文件

## 相关概念

- [因子预处理](/wiki/factors/)
