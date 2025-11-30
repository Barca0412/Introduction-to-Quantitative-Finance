#!/usr/bin/env python3
"""
arXiv AI+金融论文爬虫
每日抓取 q-fin (Quantitative Finance) 和 cs.LG/cs.AI + finance 相关论文
支持增量检测、LLM相关性判断
"""

import json
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
import time

# 配置
BASE_URL = "http://export.arxiv.org/api/query?"
DATA_DIR = Path(__file__).parent.parent / "data" / "papers"
INDEX_FILE = DATA_DIR / "paper_index.json"
MAX_RESULTS_QFIN = 100
MAX_RESULTS_PER_KEYWORD = 15

# 豆包API配置 (用于相关性判断)
ARK_API_KEY = os.environ.get("ARK_API_KEY", "")
ARK_API_BASE = "https://ark.cn-beijing.volces.com/api/v3"
ARK_JUDGE_MODEL = "deepseek-v3-1-terminus"

# 搜索类别
CATEGORIES = [
    "q-fin.CP",   # Computational Finance
    "q-fin.PM",   # Portfolio Management
    "q-fin.RM",   # Risk Management
    "q-fin.ST",   # Statistical Finance
    "q-fin.TR",   # Trading and Market Microstructure
    "q-fin.GN",   # General Finance
    "q-fin.MF",   # Mathematical Finance
    "q-fin.PR",   # Pricing of Securities
    "q-fin.EC",   # Economics
]

# 扩展关键词体系
FINANCE_KEYWORDS = {
    # 资产定价与行为金融
    "asset_pricing": [
        "asset pricing",
        "factor model",
        "cross-sectional return",
        "anomaly",
        "behavioral finance",
        "investor sentiment",
        "market efficiency",
        "CAPM",
        "Fama French",
    ],
    # 交易与市场微观结构
    "trading": [
        "algorithmic trading",
        "market making",
        "order book",
        "execution",
        "transaction cost",
        "optimal execution",
        "TWAP",
        "VWAP",
    ],
    # 高中低频交易
    "frequency_trading": [
        "high frequency trading",
        "HFT",
        "low latency trading",
        "market microstructure",
        "tick data",
        "intraday trading",
        "statistical arbitrage",
    ],
    # Agent/Deep Research/Benchmark
    "agent_research": [
        "financial agent",
        "LLM agent trading",
        "autonomous trading",
        "multi-agent finance",
        "financial benchmark",
        "FinBench",
        "FinGPT",
        "BloombergGPT",
        "finance evaluation",
    ],
    # RL + 金融
    "rl_finance": [
        "reinforcement learning trading",
        "RL portfolio",
        "deep reinforcement learning finance",
        "policy gradient trading",
        "Q-learning finance",
        "actor-critic trading",
    ],
    # LLM + 金融
    "llm_finance": [
        "LLM finance",
        "large language model trading",
        "GPT finance",
        "ChatGPT stock",
        "financial NLP",
        "sentiment analysis stock",
    ],
    # 通用
    "general": [
        "stock prediction",
        "financial forecasting",
        "portfolio optimization",
        "quantitative finance",
        "factor investing",
        "stock market prediction",
        "equity prediction",
    ],
}


def load_paper_index() -> set:
    """加载已处理论文索引"""
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get("processed_ids", []))
        except:
            pass
    return set()


def save_paper_index(processed_ids: set):
    """保存论文索引"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "processed_ids": list(processed_ids),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_count": len(processed_ids),
    }
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def call_llm_judge(prompt: str) -> str:
    """调用LLM进行相关性判断"""
    if not ARK_API_KEY:
        return "YES"
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url=ARK_API_BASE,
            api_key=ARK_API_KEY,
        )
        
        completion = client.chat.completions.create(
            model=ARK_JUDGE_MODEL,
            messages=[
                {"role": "system", "content": "你是一个学术论文分类助手，只回答YES或NO。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=10,
        )
        
        return completion.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"LLM judge error: {e}")
        return "YES"


def judge_relevance(paper: dict) -> bool:
    """判断论文是否与AI+金融相关"""
    categories = paper.get("categories", [])
    if any("q-fin" in c for c in categories):
        return True
    
    prompt = f"""判断这篇论文是否与"AI+金融/量化投资"相关。
标题: {paper['title']}
摘要: {paper['abstract'][:600]}
只回答 YES 或 NO"""
    
    response = call_llm_judge(prompt)
    return "YES" in response.upper()


def fetch_arxiv(query: str, max_results: int = 50) -> list:
    """调用 arXiv API 获取论文"""
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    
    url = BASE_URL + urllib.parse.urlencode(params)
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read().decode('utf-8')
        return parse_arxiv_response(data)
    except Exception as e:
        print(f"Error fetching arXiv: {e}")
        return []


def parse_arxiv_response(xml_data: str) -> list:
    """解析 arXiv API XML 响应"""
    papers = []
    
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom'
    }
    
    root = ET.fromstring(xml_data)
    
    for entry in root.findall('atom:entry', ns):
        try:
            id_elem = entry.find('atom:id', ns)
            arxiv_id = id_elem.text.split('/abs/')[-1] if id_elem is not None else ""
            
            title_elem = entry.find('atom:title', ns)
            title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else ""
            
            summary_elem = entry.find('atom:summary', ns)
            abstract = summary_elem.text.strip().replace('\n', ' ') if summary_elem is not None else ""
            
            authors = []
            for author in entry.findall('atom:author', ns):
                name_elem = author.find('atom:name', ns)
                if name_elem is not None:
                    authors.append(name_elem.text)
            
            published_elem = entry.find('atom:published', ns)
            published = published_elem.text[:10] if published_elem is not None else ""
            
            categories = []
            for cat in entry.findall('atom:category', ns):
                term = cat.get('term', '')
                if term:
                    categories.append(term)
            
            pdf_link = ""
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    pdf_link = link.get('href', '')
                    break
            
            paper = {
                "id": arxiv_id,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "published": published,
                "categories": categories,
                "pdf_url": pdf_link,
                "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
                "fetched_at": datetime.now().isoformat(),
            }
            papers.append(paper)
            
        except Exception as e:
            print(f"Error parsing entry: {e}")
            continue
    
    return papers


def fetch_qfin_papers() -> list:
    """获取 q-fin 类别论文"""
    query = " OR ".join([f"cat:{cat}" for cat in CATEGORIES])
    return fetch_arxiv(query, MAX_RESULTS_QFIN)


def fetch_ml_finance_papers() -> list:
    """获取 ML/AI + 金融相关论文"""
    papers = []
    all_keywords = []
    for category_keywords in FINANCE_KEYWORDS.values():
        all_keywords.extend(category_keywords)
    
    print(f"  Searching {len(all_keywords)} keywords...")
    
    for i, keyword in enumerate(all_keywords):
        query = f'all:"{keyword}" AND (cat:cs.LG OR cat:cs.AI OR cat:cs.CL OR cat:stat.ML)'
        new_papers = fetch_arxiv(query, MAX_RESULTS_PER_KEYWORD)
        papers.extend(new_papers)
        
        if (i + 1) % 10 == 0:
            print(f"    Processed {i + 1}/{len(all_keywords)} keywords, found {len(papers)} papers so far")
        
        time.sleep(3)
    
    return papers


def deduplicate_papers(papers: list) -> list:
    """去重"""
    seen = set()
    unique = []
    for paper in papers:
        if paper["id"] not in seen:
            seen.add(paper["id"])
            unique.append(paper)
    return unique


def filter_by_index(papers: list, existing_ids: set) -> tuple:
    """根据索引过滤已存在的论文"""
    new_papers = []
    skipped = 0
    for paper in papers:
        if paper["id"] not in existing_ids:
            new_papers.append(paper)
        else:
            skipped += 1
    return new_papers, skipped


def filter_recent_papers(papers: list, days: int = 7) -> list:
    """筛选最近 N 天的论文"""
    cutoff = datetime.now() - timedelta(days=days)
    return [
        p for p in papers 
        if datetime.fromisoformat(p["published"]) >= cutoff
    ]


def filter_by_relevance(papers: list) -> tuple:
    """使用LLM过滤不相关的论文"""
    relevant = []
    filtered = 0
    
    for i, paper in enumerate(papers):
        categories = paper.get("categories", [])
        if any("q-fin" in c for c in categories):
            relevant.append(paper)
            continue
        
        if judge_relevance(paper):
            relevant.append(paper)
        else:
            filtered += 1
            print(f"    Filtered out: {paper['title'][:50]}...")
        
        if (i + 1) % 20 == 0:
            print(f"    Judged {i + 1}/{len(papers)} papers, {len(relevant)} relevant")
    
    return relevant, filtered


def save_papers(papers: list, date: str = None):
    """保存论文到 JSON 文件"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    filepath = DATA_DIR / f"{date}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(papers)} papers to {filepath}")
    return filepath


def main():
    print("=" * 60)
    print(f"arXiv Crawler (Enhanced) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print("\n[1/6] Loading paper index...")
    existing_ids = load_paper_index()
    print(f"Found {len(existing_ids)} papers in index")
    
    print("\n[2/6] Fetching q-fin papers...")
    qfin_papers = fetch_qfin_papers()
    print(f"Found {len(qfin_papers)} q-fin papers")
    
    time.sleep(3)
    
    print("\n[3/6] Fetching ML+Finance papers...")
    ml_papers = fetch_ml_finance_papers()
    print(f"Found {len(ml_papers)} ML+Finance papers")
    
    all_papers = deduplicate_papers(qfin_papers + ml_papers)
    print(f"\nTotal unique papers: {len(all_papers)}")
    
    print("\n[4/6] Filtering by date (last 7 days)...")
    recent_papers = filter_recent_papers(all_papers, days=7)
    print(f"Papers from last 7 days: {len(recent_papers)}")
    
    print("\n[5/6] Filtering by index (incremental)...")
    new_papers, skipped = filter_by_index(recent_papers, existing_ids)
    print(f"New papers: {len(new_papers)}, Skipped (already in index): {skipped}")
    
    if new_papers and ARK_API_KEY:
        print("\n[6/6] Filtering by relevance (LLM judge)...")
        relevant_papers, filtered = filter_by_relevance(new_papers)
        print(f"Relevant papers: {len(relevant_papers)}, Filtered out: {filtered}")
    else:
        relevant_papers = new_papers
        if not ARK_API_KEY:
            print("\n[6/6] Skipping LLM relevance check (no API key)")
    
    if relevant_papers:
        save_papers(relevant_papers)
        
        new_ids = existing_ids | {p["id"] for p in relevant_papers}
        save_paper_index(new_ids)
        print(f"Updated paper index: {len(new_ids)} total papers")
    else:
        print("\nNo new papers to save")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
