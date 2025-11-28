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

# 主题配置
TOPICS = {
    "llm": {
        "title": "LLM in Quant",
        "description": "大语言模型在量化金融中的应用",
        "tags": ["LLM", "NLP", "Sentiment Analysis"],
    },
    "asset-pricing": {
        "title": "Asset Pricing",
        "description": "资产定价相关研究",
        "tags": ["Asset Pricing"],
    },
    "factor-mining": {
        "title": "Factor Mining",
        "description": "因子挖掘与评估",
        "tags": ["Factor Mining"],
    },
    "machine-learning": {
        "title": "Machine Learning",
        "description": "机器学习在量化中的应用",
        "tags": ["Deep Learning", "Reinforcement Learning", "Time Series"],
    },
    "portfolio-risk": {
        "title": "Portfolio & Risk",
        "description": "投资组合优化与风险管理",
        "tags": ["Portfolio Optimization", "Risk Management"],
    },
    "behavioral-finance": {
        "title": "Behavioral Finance",
        "description": "行为金融学",
        "tags": ["Behavioral Finance"],
    },
    "market-microstructure": {
        "title": "Market Microstructure",
        "description": "市场微观结构与高频交易",
        "tags": ["High Frequency", "Market Microstructure"],
    },
}


def load_all_papers() -> list:
    """加载所有论文数据"""
    all_papers = []
    
    # 从处理后的数据加载
    for json_file in sorted(DATA_DIR.glob("*.json"), reverse=True):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                papers = json.load(f)
                for p in papers:
                    p["source_date"] = json_file.stem
                all_papers.extend(papers)
        except:
            continue
    
    # 如果没有处理后的数据，从原始数据加载
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
    
    # 去重
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
    
    if paper.get("chinese_summary"):
        md += f"{paper['chinese_summary']}\n\n"
    
    md += "---\n\n"
    return md


def generate_topic_page(topic_id: str, topic_config: dict, papers: list):
    """生成单个主题页面"""
    
    # 筛选相关论文
    relevant_papers = []
    for paper in papers:
        paper_tags = paper.get("tags", [])
        paper_cats = paper.get("categories", [])
        
        # 检查标签匹配
        for tag in topic_config["tags"]:
            if tag in paper_tags:
                relevant_papers.append(paper)
                break
    
    if not relevant_papers:
        return
    
    # 按日期排序
    relevant_papers.sort(key=lambda x: x.get("source_date", ""), reverse=True)
    
    # 生成 Markdown
    md = f"""# {topic_config['title']}

{topic_config['description']}

> 共收录 **{len(relevant_papers)}** 篇论文 | [返回索引](../README.md)

---

"""
    
    for paper in relevant_papers[:50]:  # 限制数量
        md += generate_paper_entry(paper)
    
    # 写入文件
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"{topic_id}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"Generated topic: {output_file} ({len(relevant_papers)} papers)")


def main():
    print("=" * 50)
    print(f"Topic Index Generator - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 加载所有论文
    print("\nLoading papers...")
    all_papers = load_all_papers()
    print(f"Total papers: {len(all_papers)}")
    
    # 生成各主题页面
    print("\nGenerating topic pages...")
    for topic_id, topic_config in TOPICS.items():
        generate_topic_page(topic_id, topic_config, all_papers)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
