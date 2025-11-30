#!/usr/bin/env python3
"""
生成主题索引页面
按标签聚合论文，生成主题分类页面
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 配置
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "papers" / "processed"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "papers"
OUTPUT_DIR = PROJECT_ROOT / "论文" / "AI金融论文整理" / "topics"

# 金融相关标签（论文必须至少包含一个才能被收录）
FINANCE_RELATED_TAGS = {
    "Asset Pricing", "Factor Model", "Anomaly",
    "Portfolio Optimization", "Risk Management",
    "Algorithmic Trading", "High Frequency", "Market Microstructure", "Execution", "Market Making",
    "Factor Mining",
    "Behavioral Finance", "Investor Sentiment",
    "Volatility", "Options",
    "Sentiment Analysis",  # 金融情感分析
    "Financial Agent",  # 金融智能体
}

# 扩展的主题配置
TOPICS = {
    "llm-agent": {
        "title": "LLM & Agent",
        "description": "大语言模型与金融智能体在量化金融中的应用",
        "tags": ["LLM", "NLP", "Sentiment Analysis", "Financial Agent"],
    },
    "asset-pricing": {
        "title": "Asset Pricing",
        "description": "资产定价、因子模型与市场异象研究",
        "tags": ["Asset Pricing", "Factor Model", "Anomaly"],
    },
    "factor-mining": {
        "title": "Factor Mining",
        "description": "因子挖掘与评估",
        "tags": ["Factor Mining"],
    },
    "machine-learning": {
        "title": "Machine Learning",
        "description": "机器学习在量化金融中的应用，包括深度学习、强化学习、图神经网络、Transformer等",
        "tags": ["Deep Learning", "Reinforcement Learning", "Time Series", "Graph Neural Network", "Transformer"],
    },
    "portfolio-risk": {
        "title": "Portfolio & Risk",
        "description": "投资组合优化与风险管理",
        "tags": ["Portfolio Optimization", "Risk Management"],
    },
    "trading": {
        "title": "Trading & Microstructure",
        "description": "交易策略、市场微观结构与高频交易",
        "tags": ["Algorithmic Trading", "High Frequency", "Market Microstructure", "Execution", "Market Making"],
    },
    "behavioral-finance": {
        "title": "Behavioral Finance",
        "description": "行为金融学与投资者情绪",
        "tags": ["Behavioral Finance", "Investor Sentiment"],
    },
    "derivatives": {
        "title": "Derivatives",
        "description": "衍生品定价与波动率建模",
        "tags": ["Volatility", "Options"],
    },
    "benchmark": {
        "title": "Benchmark & Evaluation",
        "description": "金融AI基准测试与模型评估",
        "tags": ["Benchmark"],
    },
}


def load_all_papers() -> list:
    """加载所有论文数据"""
    all_papers = []
    
    for json_file in sorted(DATA_DIR.glob("*.json"), reverse=True):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                papers = json.load(f)
                for p in papers:
                    p["source_date"] = json_file.stem
                all_papers.extend(papers)
        except:
            continue
    
    if not all_papers:
        for json_file in sorted(RAW_DATA_DIR.glob("*.json"), reverse=True):
            if json_file.parent.name == "processed":
                continue
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    papers = json.load(f)
                    for p in papers:
                        p["source_date"] = json_file.stem
                    all_papers.extend(papers)
            except:
                continue
    
    seen = set()
    unique = []
    for p in all_papers:
        if p["id"] not in seen:
            seen.add(p["id"])
            unique.append(p)
    
    return unique


def generate_paper_entry(paper: dict) -> str:
    """生成单篇论文条目"""
    title = paper.get("chinese_title") or paper["title"]
    date = paper.get("source_date", paper.get("published", ""))
    
    md = f"### [{title}]({paper['arxiv_url']})\n\n"
    md += f"**日期**: {date} | "
    
    authors = ", ".join(paper["authors"][:3])
    if len(paper["authors"]) > 3:
        authors += " et al."
    md += f"**作者**: {authors}\n\n"
    
    tags = paper.get("tags", [])[:4]
    if tags:
        tag_str = " ".join([f"`{tag}`" for tag in tags])
        md += f"**标签**: {tag_str}\n\n"
    
    if paper.get("chinese_summary"):
        md += f"{paper['chinese_summary']}\n\n"
    
    md += "---\n\n"
    return md


def is_finance_related(paper: dict) -> bool:
    """检查论文是否与金融相关（至少包含一个金融标签）"""
    paper_tags = set(paper.get("tags", []))
    # q-fin 类别的论文直接算金融相关
    categories = paper.get("categories", [])
    if any("q-fin" in c for c in categories):
        return True
    # 检查是否有金融相关标签
    return bool(paper_tags & FINANCE_RELATED_TAGS)


def generate_topic_page(topic_id: str, topic_config: dict, papers: list):
    """生成单个主题页面"""
    
    relevant_papers = []
    for paper in papers:
        paper_tags = paper.get("tags", [])
        
        # 必须是金融相关的论文
        if not is_finance_related(paper):
            continue
        
        for tag in topic_config["tags"]:
            if tag in paper_tags:
                relevant_papers.append(paper)
                break
    
    if not relevant_papers:
        md = f"""# {topic_config['title']}

{topic_config['description']}

> 暂无相关论文 | [返回索引](../README.md)

"""
    else:
        relevant_papers.sort(key=lambda x: x.get("source_date", ""), reverse=True)
        
        md = f"""# {topic_config['title']}

{topic_config['description']}

> 共收录 **{len(relevant_papers)}** 篇论文 | [返回索引](../README.md)

---

"""
        
        for paper in relevant_papers[:100]:
            md += generate_paper_entry(paper)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"{topic_id}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)
    
    count = len(relevant_papers) if relevant_papers else 0
    print(f"Generated topic: {output_file} ({count} papers)")


def main():
    print("=" * 60)
    print(f"Topic Index Generator - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print("\nLoading papers...")
    all_papers = load_all_papers()
    print(f"Total papers: {len(all_papers)}")
    
    print("\nGenerating topic pages...")
    for topic_id, topic_config in TOPICS.items():
        generate_topic_page(topic_id, topic_config, all_papers)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
