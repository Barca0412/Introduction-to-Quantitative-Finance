#!/usr/bin/env python3
"""
论文处理脚本
使用豆包大模型API为论文生成中文概述和标签
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# 配置
DATA_DIR = Path(__file__).parent.parent / "data" / "papers"
PROCESSED_DIR = DATA_DIR / "processed"

# 豆包API配置
ARK_API_KEY = os.environ.get("ARK_API_KEY", "")
ARK_API_BASE = "https://ark.cn-beijing.volces.com/api/v3"
ARK_MODEL = "doubao-seed-1-6-lite-251015"

# 标签列表
AVAILABLE_TAGS = [
    "LLM",
    "Asset Pricing",
    "Behavioral Finance",
    "Factor Mining",
    "Portfolio Optimization",
    "Risk Management",
    "Deep Learning",
    "Reinforcement Learning",
    "High Frequency",
    "NLP",
    "Time Series",
    "Market Microstructure",
    "Sentiment Analysis",
    "Volatility",
    "Options",
]


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
    
    prompt = f"""请分析以下量化金融论文，生成中文概述和标签。

标题: {paper['title']}

摘要: {paper['abstract'][:1500]}

请严格按以下JSON格式输出（只输出JSON，不要其他内容）:
{{
    "chinese_title": "论文中文标题",
    "chinese_summary": "2-3句话的中文概述，说明论文的主要贡献",
    "tags": ["从以下选择2-4个最相关的标签: {', '.join(AVAILABLE_TAGS)}"],
    "key_contributions": ["核心贡献1", "核心贡献2"]
}}
"""
    
    response = call_llm(prompt)
    
    if response:
        try:
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            
            result = json.loads(clean_response)
            return {
                "chinese_title": result.get("chinese_title", ""),
                "chinese_summary": result.get("chinese_summary", ""),
                "tags": result.get("tags", []),
                "key_contributions": result.get("key_contributions", []),
            }
        except json.JSONDecodeError:
            print(f"Failed to parse LLM response for paper: {paper['id']}")
    
    # 返回默认值（基于原始分类推断标签）
    default_tags = []
    categories = paper.get("categories", [])
    if any("q-fin" in c for c in categories):
        default_tags.append("Quantitative Finance")
    if any("cs.LG" in c or "cs.AI" in c for c in categories):
        default_tags.append("Deep Learning")
    
    return {
        "chinese_title": "",
        "chinese_summary": "",
        "tags": default_tags or ["Quantitative Finance"],
        "key_contributions": [],
    }


def process_papers(date: str = None):
    """处理指定日期的论文"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    input_file = DATA_DIR / f"{date}.json"
    
    if not input_file.exists():
        print(f"No papers found for {date}")
        return []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    print(f"Processing {len(papers)} papers...")
    
    processed_papers = []
    for i, paper in enumerate(papers):
        print(f"[{i+1}/{len(papers)}] Processing: {paper['title'][:50]}...")
        
        summary_data = generate_paper_summary(paper)
        processed_paper = {**paper, **summary_data}
        processed_papers.append(processed_paper)
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_file = PROCESSED_DIR / f"{date}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_papers, f, ensure_ascii=False, indent=2)
    
    print(f"Saved processed papers to {output_file}")
    return processed_papers


def main():
    print("=" * 50)
    print(f"Paper Processor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    if not ARK_API_KEY:
        print("\nWarning: ARK_API_KEY not set")
        print("Set environment variable: export ARK_API_KEY=your-key")
    
    process_papers()
    print("\nDone!")


if __name__ == "__main__":
    main()
