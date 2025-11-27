#!/usr/bin/env python3
"""
arXiv AI+金融论文爬虫
每日抓取 q-fin (Quantitative Finance) 和 cs.LG/cs.AI + finance 相关论文
"""

import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
import time
import re

# 配置
BASE_URL = "http://export.arxiv.org/api/query?"
DATA_DIR = Path(__file__).parent.parent / "data" / "papers"
MAX_RESULTS = 50

# 搜索类别
CATEGORIES = [
    "q-fin.CP",   # Computational Finance
    "q-fin.PM",   # Portfolio Management
    "q-fin.RM",   # Risk Management
    "q-fin.ST",   # Statistical Finance
    "q-fin.TR",   # Trading and Market Microstructure
    "q-fin.GN",   # General Finance
]

# 额外关键词搜索 (用于 cs.LG/cs.AI 中的金融相关论文)
FINANCE_KEYWORDS = [
    "stock prediction",
    "financial forecasting",
    "portfolio optimization",
    "algorithmic trading",
    "market prediction",
    "asset pricing",
    "quantitative finance",
    "factor investing",
    "LLM finance",
    "large language model trading",
]


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
    
    # 定义命名空间
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom'
    }
    
    root = ET.fromstring(xml_data)
    
    for entry in root.findall('atom:entry', ns):
        try:
            # 提取论文 ID
            id_elem = entry.find('atom:id', ns)
            arxiv_id = id_elem.text.split('/abs/')[-1] if id_elem is not None else ""
            
            # 提取标题
            title_elem = entry.find('atom:title', ns)
            title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else ""
            
            # 提取摘要
            summary_elem = entry.find('atom:summary', ns)
            abstract = summary_elem.text.strip().replace('\n', ' ') if summary_elem is not None else ""
            
            # 提取作者
            authors = []
            for author in entry.findall('atom:author', ns):
                name_elem = author.find('atom:name', ns)
                if name_elem is not None:
                    authors.append(name_elem.text)
            
            # 提取发布日期
            published_elem = entry.find('atom:published', ns)
            published = published_elem.text[:10] if published_elem is not None else ""
            
            # 提取分类
            categories = []
            for cat in entry.findall('atom:category', ns):
                term = cat.get('term', '')
                if term:
                    categories.append(term)
            
            # 提取链接
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
    return fetch_arxiv(query, MAX_RESULTS)


def fetch_ml_finance_papers() -> list:
    """获取 ML/AI + 金融相关论文"""
    papers = []
    for keyword in FINANCE_KEYWORDS[:5]:  # 限制请求数量
        query = f'all:"{keyword}" AND (cat:cs.LG OR cat:cs.AI OR cat:cs.CL)'
        papers.extend(fetch_arxiv(query, 10))
        time.sleep(3)  # 遵守 arXiv API 限制
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


def filter_recent_papers(papers: list, days: int = 7) -> list:
    """筛选最近 N 天的论文"""
    cutoff = datetime.now() - timedelta(days=days)
    return [
        p for p in papers 
        if datetime.fromisoformat(p["published"]) >= cutoff
    ]


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
    print("=" * 50)
    print(f"arXiv Crawler - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 获取 q-fin 论文
    print("\n[1/2] Fetching q-fin papers...")
    qfin_papers = fetch_qfin_papers()
    print(f"Found {len(qfin_papers)} q-fin papers")
    
    time.sleep(3)  # 遵守 API 限制
    
    # 获取 ML + 金融论文
    print("\n[2/2] Fetching ML+Finance papers...")
    ml_papers = fetch_ml_finance_papers()
    print(f"Found {len(ml_papers)} ML+Finance papers")
    
    # 合并去重
    all_papers = deduplicate_papers(qfin_papers + ml_papers)
    print(f"\nTotal unique papers: {len(all_papers)}")
    
    # 筛选最近 7 天
    recent_papers = filter_recent_papers(all_papers, days=7)
    print(f"Papers from last 7 days: {len(recent_papers)}")
    
    # 保存
    save_papers(recent_papers)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
