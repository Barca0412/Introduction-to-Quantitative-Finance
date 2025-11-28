#!/usr/bin/env python3
"""
生成每日论文 Markdown 页面
输出到 论文/AI金融论文整理/ 目录 (用于 GitHub README 展示)
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 配置
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "papers" / "processed"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "papers"
OUTPUT_DIR = PROJECT_ROOT / "论文" / "AI金融论文整理"

# 扩展的标签到分类映射
TAG_CATEGORIES = {
    # LLM & Agent
    "LLM": "LLM & Agent",
    "NLP": "LLM & Agent",
    "Sentiment Analysis": "LLM & Agent",
    "Financial Agent": "LLM & Agent",
    # 资产定价
    "Asset Pricing": "Asset Pricing",
    "Factor Model": "Asset Pricing",
    "Anomaly": "Asset Pricing",
    # 因子挖掘
    "Factor Mining": "Factor Mining",
    # 行为金融
    "Behavioral Finance": "Behavioral Finance",
    "Investor Sentiment": "Behavioral Finance",
    # 机器学习
    "Deep Learning": "Machine Learning",
    "Reinforcement Learning": "Machine Learning",
    "Time Series": "Machine Learning",
    "Graph Neural Network": "Machine Learning",
    "Transformer": "Machine Learning",
    # 投资组合与风控
    "Portfolio Optimization": "Portfolio & Risk",
    "Risk Management": "Portfolio & Risk",
    # 交易与市场微观结构
    "Algorithmic Trading": "Trading & Microstructure",
    "High Frequency": "Trading & Microstructure",
    "Market Microstructure": "Trading & Microstructure",
    "Execution": "Trading & Microstructure",
    "Market Making": "Trading & Microstructure",
    # 衍生品
    "Volatility": "Derivatives",
    "Options": "Derivatives",
    # 其他
    "Benchmark": "Benchmark & Evaluation",
    "Quantitative Finance": "Other",
}


def generate_paper_markdown(paper: dict) -> str:
    """生成单篇论文的 Markdown"""
    
    title = paper.get("chinese_title") or paper["title"]
    md = f"### [{title}]({paper['arxiv_url']})\n\n"
    
    if paper.get("chinese_title"):
        md += f"**原文**: {paper['title']}\n\n"
    
    authors = ", ".join(paper["authors"][:5])
    if len(paper["authors"]) > 5:
        authors += " et al."
    md += f"**作者**: {authors}\n\n"
    
    tags = paper.get("tags", paper.get("categories", []))[:5]
    if tags:
        tag_str = " ".join([f"`{tag}`" for tag in tags])
        md += f"**标签**: {tag_str}\n\n"
    
    if paper.get("chinese_summary"):
        md += f"**中文概述**: {paper['chinese_summary']}\n\n"
    
    contributions = paper.get("key_contributions", [])
    if contributions:
        md += "**核心贡献**:\n"
        for i, contrib in enumerate(contributions, 1):
            md += f"  {i}. {contrib}\n"
        md += "\n"
    
    md += "---\n\n"
    return md


def categorize_papers(papers: list) -> dict:
    """将论文按类别分组"""
    categories = defaultdict(list)
    
    for paper in papers:
        tags = paper.get("tags", [])
        
        category = "Other"
        for tag in tags:
            if tag in TAG_CATEGORIES:
                category = TAG_CATEGORIES[tag]
                break
        
        categories[category].append(paper)
    
    return dict(categories)


def generate_daily_page(date: str = None):
    """生成每日论文页面"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    input_file = DATA_DIR / f"{date}.json"
    if not input_file.exists():
        input_file = RAW_DATA_DIR / f"{date}.json"
        if not input_file.exists():
            print(f"No papers found for {date}")
            return None
    
    with open(input_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    if not papers:
        print(f"No papers to generate for {date}")
        return None
    
    daily_dir = OUTPUT_DIR / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    
    md = f"""# {date} AI+金融论文日报

> 共收录 **{len(papers)}** 篇论文 | [返回索引](../README.md)

"""
    
    categorized = categorize_papers(papers)
    
    category_order = [
        "LLM & Agent",
        "Asset Pricing",
        "Factor Mining",
        "Machine Learning",
        "Portfolio & Risk",
        "Behavioral Finance",
        "Trading & Microstructure",
        "Derivatives",
        "Benchmark & Evaluation",
        "Other",
    ]
    
    for category in category_order:
        if category in categorized:
            md += f"## {category}\n\n"
            for paper in categorized[category]:
                md += generate_paper_markdown(paper)
    
    output_file = daily_dir / f"{date}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"Generated: {output_file}")
    
    update_main_index()
    
    return output_file


def update_main_index():
    """更新主索引页面"""
    daily_dir = OUTPUT_DIR / "daily"
    
    daily_files = sorted(daily_dir.glob("*.md"), reverse=True)
    
    stats = []
    for f in daily_files[:30]:
        date = f.stem
        try:
            data_file = DATA_DIR / f"{date}.json"
            if not data_file.exists():
                data_file = RAW_DATA_DIR / f"{date}.json"
            
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as df:
                    papers = json.load(df)
                    stats.append((date, len(papers)))
            else:
                stats.append((date, "?"))
        except:
            stats.append((date, "?"))
    
    md = """# AI+金融论文整理

每日自动更新 arXiv 上 AI+金融相关论文，使用 LLM 生成中文概述与标签。

- 📰 **每日更新**: 自动抓取 q-fin、cs.LG+finance 相关论文
- 🤖 **智能分析**: 使用大模型生成中文摘要和关键贡献
- 🏷️ **主题分类**: LLM & Agent、Asset Pricing、Factor Mining、RL、Trading 等标签
- 🔄 **增量更新**: 自动去重，只处理新论文

---

## 📅 每日更新

| 日期 | 论文数 | 链接 |
|------|--------|------|
"""
    
    for date, count in stats:
        md += f"| {date} | {count} | [查看](./daily/{date}.md) |\n"
    
    md += """
---

## 🏷️ 主题分类

- [LLM & Agent](./topics/llm-agent.md) - 大语言模型与金融智能体
- [Asset Pricing](./topics/asset-pricing.md) - 资产定价与因子模型
- [Factor Mining](./topics/factor-mining.md) - 因子挖掘
- [Machine Learning](./topics/machine-learning.md) - 机器学习方法 (DL/RL/GNN/Transformer)
- [Portfolio & Risk](./topics/portfolio-risk.md) - 投资组合与风险管理
- [Trading & Microstructure](./topics/trading.md) - 交易与市场微观结构
- [Behavioral Finance](./topics/behavioral-finance.md) - 行为金融学
- [Derivatives](./topics/derivatives.md) - 衍生品与波动率
- [Benchmark](./topics/benchmark.md) - 基准测试与评估

---

*自动更新于 """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """*
"""
    
    index_file = OUTPUT_DIR / "README.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"Updated index: {index_file}")


def main():
    print("=" * 60)
    print(f"Daily Page Generator - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    generate_daily_page()
    
    print("\nDone!")


if __name__ == "__main__":
    main()
