#!/usr/bin/env python3
"""
论文处理脚本
使用豆包大模型API为论文生成中文概述和标签
支持增量处理（只处理新论文）
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# 配置
DATA_DIR = Path(__file__).parent.parent / "data" / "papers"
PROCESSED_DIR = DATA_DIR / "processed"
INDEX_FILE = DATA_DIR / "paper_index.json"

# 豆包API配置
ARK_API_KEY = os.environ.get("ARK_API_KEY", "")
ARK_API_BASE = "https://ark.cn-beijing.volces.com/api/v3"
ARK_MODEL = "doubao-seed-1-6-lite-251015"

# 扩展标签列表 (25个)
AVAILABLE_TAGS = [
    # LLM & NLP & Agent
    "LLM",
    "NLP",
    "Sentiment Analysis",
    "Financial Agent",
    # 资产定价
    "Asset Pricing",
    "Factor Model",
    "Anomaly",
    # 行为金融
    "Behavioral Finance",
    "Investor Sentiment",
    # 机器学习
    "Deep Learning",
    "Reinforcement Learning",
    "Time Series",
    "Graph Neural Network",
    "Transformer",
    # 投资组合与风控
    "Portfolio Optimization",
    "Risk Management",
    "Factor Mining",
    # 交易与市场微观结构
    "Algorithmic Trading",
    "High Frequency",
    "Market Microstructure",
    "Execution",
    "Market Making",
    # 衍生品
    "Volatility",
    "Options",
    # 其他
    "Benchmark",
]


def load_processed_ids() -> set:
    """加载所有已处理论文的ID"""
    processed_ids = set()
    
    if PROCESSED_DIR.exists():
        for json_file in PROCESSED_DIR.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    papers = json.load(f)
                    for p in papers:
                        processed_ids.add(p.get("id", ""))
            except:
                continue
    
    return processed_ids


def call_llm(prompt: str) -> Optional[str]:
    """调用豆包API"""
    if not ARK_API_KEY:
        print("Warning: ARK_API_KEY not set, skipping LLM processing")
        return None
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url=ARK_API_BASE,
            api_key=ARK_API_KEY,
        )
        
        completion = client.chat.completions.create(
            model=ARK_MODEL,
            messages=[
                {"role": "system", "content": "你是一个量化金融研究助手，擅长分析学术论文并生成简洁的中文概述。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800,
        )
        
        return completion.choices[0].message.content
        
    except ImportError:
        print("Error: openai package not installed. Run: pip install openai")
        return None
    except Exception as e:
        print(f"LLM API error: {e}")
        return None


def generate_paper_summary(paper: dict) -> dict:
    """为单篇论文生成中文概述和标签"""
    
    tags_str = ", ".join(AVAILABLE_TAGS)
    
    prompt = f"""请分析以下量化金融/AI+金融论文，生成中文概述和标签。

标题: {paper['title']}

摘要: {paper['abstract'][:1500]}

请严格按以下JSON格式输出（只输出JSON，不要其他内容）:
{{
    "chinese_title": "论文中文标题",
    "chinese_summary": "2-3句话的中文概述，说明论文的主要贡献和方法",
    "tags": ["从以下选择2-4个最相关的标签: {tags_str}"],
    "key_contributions": ["核心贡献1", "核心贡献2"]
}}
"""
    
    response = call_llm(prompt)
    
    if response:
        try:
            clean_response = response.strip()
            if clean_response.startswith("```"):
                lines = clean_response.split("\n")
                clean_response = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            
            result = json.loads(clean_response)
            
            valid_tags = [t for t in result.get("tags", []) if t in AVAILABLE_TAGS]
            
            return {
                "chinese_title": result.get("chinese_title", ""),
                "chinese_summary": result.get("chinese_summary", ""),
                "tags": valid_tags if valid_tags else infer_tags_from_categories(paper),
                "key_contributions": result.get("key_contributions", []),
                "processed_at": datetime.now().isoformat(),
            }
        except json.JSONDecodeError:
            print(f"Failed to parse LLM response for paper: {paper['id']}")
    
    return {
        "chinese_title": "",
        "chinese_summary": "",
        "tags": infer_tags_from_categories(paper),
        "key_contributions": [],
        "processed_at": datetime.now().isoformat(),
    }


def infer_tags_from_categories(paper: dict) -> list:
    """根据arXiv分类推断标签"""
    categories = paper.get("categories", [])
    title_lower = paper.get("title", "").lower()
    abstract_lower = paper.get("abstract", "").lower()
    
    tags = []
    
    if any("q-fin.PM" in c for c in categories):
        tags.append("Portfolio Optimization")
    if any("q-fin.RM" in c for c in categories):
        tags.append("Risk Management")
    if any("q-fin.TR" in c for c in categories):
        tags.append("Market Microstructure")
    if any("q-fin.PR" in c for c in categories):
        tags.append("Options")
    
    if any("cs.LG" in c or "stat.ML" in c for c in categories):
        tags.append("Deep Learning")
    if any("cs.CL" in c for c in categories):
        tags.append("NLP")
    
    if "reinforcement learning" in title_lower or "rl" in title_lower:
        tags.append("Reinforcement Learning")
    if "llm" in title_lower or "large language" in title_lower or "gpt" in title_lower:
        tags.append("LLM")
    if "agent" in title_lower:
        tags.append("Financial Agent")
    if "sentiment" in title_lower or "sentiment" in abstract_lower:
        tags.append("Sentiment Analysis")
    if "high frequency" in title_lower or "hft" in title_lower:
        tags.append("High Frequency")
    if "factor" in title_lower:
        tags.append("Factor Mining")
    if "asset pricing" in title_lower or "cross-sectional" in title_lower:
        tags.append("Asset Pricing")
    if "transformer" in title_lower:
        tags.append("Transformer")
    if "graph" in title_lower and "neural" in title_lower:
        tags.append("Graph Neural Network")
    if "benchmark" in title_lower or "evaluation" in title_lower:
        tags.append("Benchmark")
    
    seen = set()
    unique_tags = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            unique_tags.append(t)
    
    return unique_tags[:4] if unique_tags else ["Deep Learning"]


def process_papers(date: str = None):
    """处理指定日期的论文（增量处理）"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    input_file = DATA_DIR / f"{date}.json"
    
    if not input_file.exists():
        print(f"No papers found for {date}")
        return []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    processed_ids = load_processed_ids()
    print(f"Found {len(processed_ids)} already processed papers")
    
    new_papers = [p for p in papers if p["id"] not in processed_ids]
    already_processed = len(papers) - len(new_papers)
    
    print(f"Total papers: {len(papers)}, New: {len(new_papers)}, Already processed: {already_processed}")
    
    if not new_papers:
        print("No new papers to process")
        output_file = PROCESSED_DIR / f"{date}.json"
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    print(f"Processing {len(new_papers)} new papers...")
    
    processed_papers = []
    for i, paper in enumerate(new_papers):
        print(f"[{i+1}/{len(new_papers)}] Processing: {paper['title'][:50]}...")
        
        summary_data = generate_paper_summary(paper)
        processed_paper = {**paper, **summary_data}
        processed_papers.append(processed_paper)
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_file = PROCESSED_DIR / f"{date}.json"
    
    existing_processed = []
    if output_file.exists():
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_processed = json.load(f)
        except:
            pass
    
    existing_ids = {p["id"] for p in existing_processed}
    for p in processed_papers:
        if p["id"] not in existing_ids:
            existing_processed.append(p)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(existing_processed, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(existing_processed)} processed papers to {output_file}")
    return existing_processed


def main():
    print("=" * 60)
    print(f"Paper Processor (Enhanced) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if not ARK_API_KEY:
        print("\nWarning: ARK_API_KEY not set")
        print("Set environment variable: export ARK_API_KEY=your-key")
    
    process_papers()
    print("\nDone!")


if __name__ == "__main__":
    main()
