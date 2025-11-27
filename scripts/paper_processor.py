#!/usr/bin/env python3
"""
论文处理脚本
使用 LLM API 为论文生成中文概述和标签
支持 OpenAI API 和兼容接口
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import urllib.request
import urllib.error

# 配置
DATA_DIR = Path(__file__).parent.parent / "data" / "papers"
PROCESSED_DIR = DATA_DIR / "processed"

# LLM 配置 (从环境变量读取)
LLM_API_KEY = os.environ.get("OPENAI_API_KEY", "")
LLM_API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

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
    """调用 LLM API"""
    if not LLM_API_KEY:
        print("Warning: No API key configured, skipping LLM processing")
        return None
    
    url = f"{LLM_API_BASE}/chat/completions"
    
    data = json.dumps({
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个量化金融研究助手，擅长分析学术论文。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500,
    }).encode('utf-8')
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}",
    }
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"LLM API error: {e}")
        return None


def generate_paper_summary(paper: dict) -> dict:
    """为单篇论文生成中文概述和标签"""
    
    prompt = f"""请分析以下量化金融论文，生成中文概述和标签。

标题: {paper['title']}

摘要: {paper['abstract'][:1500]}

请严格按以下 JSON 格式输出（只输出 JSON，不要其他内容）:
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
            # 尝试解析 JSON
            # 处理可能的 markdown 代码块
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
    
    # 返回默认值
    return {
        "chinese_title": "",
        "chinese_summary": "",
        "tags": [],
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
        
        # 生成 LLM 概述
        summary_data = generate_paper_summary(paper)
        
        # 合并数据
        processed_paper = {**paper, **summary_data}
        processed_papers.append(processed_paper)
    
    # 保存处理后的数据
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
    
    if not LLM_API_KEY:
        print("\nWarning: OPENAI_API_KEY not set")
        print("Set environment variable to enable LLM processing")
        print("Example: export OPENAI_API_KEY=sk-...")
    
    process_papers()
    print("\nDone!")


if __name__ == "__main__":
    main()
