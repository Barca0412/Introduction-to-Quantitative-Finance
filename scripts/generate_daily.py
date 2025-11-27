#!/usr/bin/env python3
"""
生成每日论文 Markdown 页面
将处理后的论文数据转换为 VitePress 可用的 Markdown 格式
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 配置
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "papers" / "processed"
DOCS_DIR = PROJECT_ROOT / "docs" / "arxiv"

# 标签到分类的映射
TAG_CATEGORIES = {
    "LLM": "LLM in Quant",
    "NLP": "LLM in Quant",
    "Sentiment Analysis": "LLM in Quant",
    "Asset Pricing": "Asset Pricing",
    "Factor Mining": "Factor Mining",
    "Behavioral Finance": "Behavioral Finance",
    "Portfolio Optimization": "Portfolio & Risk",
    "Risk Management": "Portfolio & Risk",
    "Deep Learning": "Machine Learning",
    "Reinforcement Learning": "Machine Learning",
    "Time Series": "Machine Learning",
    "High Frequency": "Market Microstructure",
    "Market Microstructure": "Market Microstructure",
    "Volatility": "Derivatives & Volatility",
    "Options": "Derivatives & Volatility",
}


def generate_paper_markdown(paper: dict) -> str:
    """生成单篇论文的 Markdown"""
    
    # 标题和链接
    title = paper.get("chinese_title") or paper["title"]
    md = f"### [{title}]({paper['arxiv_url']})\n\n"
    
    # 原文标题（如果有中文标题）
    if paper.get("chinese_title"):
        md += f"**原文**: {paper['title']}\n\n"
    
    # 作者
    authors = ", ".join(paper["authors"][:5])
    if len(paper["authors"]) > 5:
        authors += " et al."
    md += f"**作者**: {authors}\n\n"
    
    # 标签
    tags = paper.get("tags", paper.get("categories", []))[:5]
    if tags:
        tag_str = " ".join([f"`{tag}`" for tag in tags])
        md += f"**标签**: {tag_str}\n\n"
    
    # 中文概述
    if paper.get("chinese_summary"):
        md += f"**中文概述**: {paper['chinese_summary']}\n\n"
    
    # 核心贡献
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
        
        # 找到第一个匹配的分类
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
    
    # 读取处理后的论文数据
    input_file = DATA_DIR / f"{date}.json"
    
    if not input_file.exists():
        # 尝试读取未处理的数据
        input_file = DATA_DIR.parent / f"{date}.json"
        if not input_file.exists():
            print(f"No papers found for {date}")
            return None
    
    with open(input_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    if not papers:
        print(f"No papers to generate for {date}")
        return None
    
    # 解析日期
    year, month, day = date.split("-")
    
    # 创建目录
    output_dir = DOCS_DIR / year / month
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成 Markdown
    md = f"""---
title: {date} AI+金融论文日报
date: {date}
---

# {date} 论文更新

> 共收录 **{len(papers)}** 篇论文

"""
    
    # 按分类组织论文
    categorized = categorize_papers(papers)
    
    # 定义分类顺序
    category_order = [
        "LLM in Quant",
        "Asset Pricing",
        "Factor Mining",
        "Machine Learning",
        "Portfolio & Risk",
        "Behavioral Finance",
        "Market Microstructure",
        "Derivatives & Volatility",
        "Other",
    ]
    
    for category in category_order:
        if category in categorized:
            md += f"## {category}\n\n"
            for paper in categorized[category]:
                md += generate_paper_markdown(paper)
    
    # 写入文件
    output_file = output_dir / f"{date}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"Generated: {output_file}")
    
    # 更新索引
    update_month_index(year, month)
    
    return output_file


def update_month_index(year: str, month: str):
    """更新月份索引页面"""
    month_dir = DOCS_DIR / year / month
    
    # 收集该月所有日期页面
    daily_files = sorted(month_dir.glob("*.md"), reverse=True)
    daily_files = [f for f in daily_files if f.name != "index.md"]
    
    # 生成索引
    md = f"""---
title: {year}年{month}月论文
---

# {year}年{month}月 论文归档

"""
    
    for f in daily_files:
        date = f.stem
        md += f"- [{date}](./{date})\n"
    
    # 写入索引
    index_file = month_dir / "index.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"Updated index: {index_file}")


def update_main_index():
    """更新主索引页面"""
    # 收集所有年份/月份
    years = sorted([d for d in DOCS_DIR.iterdir() if d.is_dir() and d.name.isdigit()], reverse=True)
    
    md = """---
title: arXiv AI+金融论文日报
---

# arXiv AI+金融论文日报

每日更新 arXiv 上 AI+金融相关论文，含中文概述与标签。

## 论文归档

"""
    
    for year_dir in years:
        year = year_dir.name
        months = sorted([d for d in year_dir.iterdir() if d.is_dir()], reverse=True)
        
        md += f"### {year}年\n\n"
        for month_dir in months:
            month = month_dir.name
            daily_count = len(list(month_dir.glob("*.md"))) - 1  # 排除 index.md
            if daily_count > 0:
                md += f"- [{year}年{month}月](./{year}/{month}/) ({daily_count}天)\n"
        md += "\n"
    
    # 写入主索引
    index_file = DOCS_DIR / "index.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"Updated main index: {index_file}")


def main():
    print("=" * 50)
    print(f"Daily Page Generator - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 生成今日页面
    generate_daily_page()
    
    # 更新主索引
    update_main_index()
    
    print("\nDone!")


if __name__ == "__main__":
    main()
