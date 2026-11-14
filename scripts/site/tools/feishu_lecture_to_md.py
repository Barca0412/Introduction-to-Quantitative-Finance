"""Convert the two Feishu lecture exports (lark-cli markdown) into VitePress lecture pages."""
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

SRC = Path("/tmp/claude/lectures")
REPO = Path("/Users/barca/HFT/open_source/Introduction-to-Quantitative-Finance")
GH = "https://github.com/Barca0412/Introduction-to-Quantitative-Finance/blob/main/"
TRAE_URL = "https://mp.weixin.qq.com/s/Gg68A1Ue5y-UYR-FXyYeHw"
SHEETS = json.load(open(SRC / "sheets_md.json"))


def report_link(path: str) -> str:
    return GH + "/".join(quote(p) for p in path.split("/"))


REPORTS = {
    "20160929-华泰证券-多因子系列之二：华泰单因子测试之估值类因子.pdf": "资料/卖方金工研报/华泰多因子系列/20160929-华泰证券-多因子系列之二：华泰单因子测试之估值类因子.pdf",
    "2021-03-18_海通证券_选股因子系列研究（七十三）：使用基本面逻辑改进ROE因子.pdf": "资料/卖方金工研报/海通报告/2021-03-18_海通证券_选股因子系列研究（七十三）：使用基本面逻辑改进ROE因子.pdf",
    "20190104-华泰证券-多因子系列之十：因子合成方法实证分析.pdf": "资料/卖方金工研报/华泰多因子系列/20190104-华泰证券-多因子系列之十：因子合成方法实证分析.pdf",
    "华泰证券-华泰人工智能系列之14：对抗过拟合：从时序交叉验证谈起.pdf": "资料/卖方金工研报/华泰人工智能/华泰证券-华泰人工智能系列之14：对抗过拟合：从时序交叉验证谈起.pdf",
    "2023-12-13_海通证券_选股因子系列研究（九十一）：组合规模、交易成本和大单冲击对因子表现的影响分析.pdf": "资料/卖方金工研报/海通报告/2023-12-13_海通证券_选股因子系列研究（九十一）：组合规模、交易成本和大单冲击对因子表现的影响分析.pdf",
}

LECTURES = {
    "01": {
        "slug": "01-capm-beta",
        "feishu": "https://hnufintech.feishu.cn/wiki/JRF9wx8Q5iHUlNk7uaycR8linmg",
        "front": """---
title: 实战一：计算 A 股个股与行业的 CAPM Beta
description: 用 CSMAR 月度数据和 Python，按证监会行业分类估计 A 股各行业和个股的 CAPM Beta，画出时变 Beta，比较个股与所属行业的差异，并附上用 AI 编程工具辅助写代码的参考提示词。
tutorial:
  order: 1
  level: 入门
  prerequisites: [Python 基础, 线性回归]
  data: [CSMAR 国泰安（需高校或机构账号）]
  author: 陈俊希、蒙思宇、王星尧、刘泽楚（整理） · 唐国豪教授《量化投资》课程
  license: 文字 CC BY-NC-SA 4.0 · 代码 MIT
  code: false
  wiki: [/wiki/framework, /wiki/data]
---
""",
    },
    "02": {
        "slug": "02-size-value-effects",
        "feishu": "https://hnufintech.feishu.cn/wiki/EU7ZwzeiAiXOU6kYlQcccilZnEc",
        "front": """---
title: 实战二：中国股票市场的价值效应与规模效应
description: 用 CSMAR 财务报表和月度交易数据，按账面市值比和市值把 A 股分成十组，用投资组合排序法检验价值效应与规模效应，讨论壳价值对 A 股因子的影响，并附上 AI 编程辅助的参考提示词。
tutorial:
  order: 2
  level: 进阶
  prerequisites: [实战一, pandas 数据处理, 投资组合排序法]
  data: [CSMAR 国泰安（需高校或机构账号）]
  author: 陈俊希、陈卓然、王星尧、刘泽楚、王子元、陈云、陈怡帆（整理） · 唐国豪教授《量化投资》课程
  license: 文字 CC BY-NC-SA 4.0 · 代码 MIT
  code: false
  wiki: [/wiki/factors/, /wiki/factors/fundamental, /wiki/backtest]
  reports:
""" + "".join(
            f"    - title: {Path(name).stem}\n      link: {report_link(path)}\n" for name, path in REPORTS.items()
        ) + """  papers:
    - title: Liu, Stambaugh & Yuan (2019). Size and Value in China. Journal of Financial Economics
      link: https://doi.org/10.1016/j.jfineco.2019.03.008
---
""",
    },
}

ALT_PREFIX = re.compile(r"^(这张图片|该图片|此图片|图片|这是一张|这是一份|这是|该图|这张图|图中)(展示了|展示的是|呈现了|呈现的是|为|是|显示了)?[：:，,]?")


def short_alt(alt: str) -> str:
    alt = ALT_PREFIX.sub("", alt.strip())
    alt = re.split(r"[。；;]", alt)[0]
    alt = alt.replace("[", "").replace("]", "")
    return (alt[:60] + "…") if len(alt) > 60 else alt


def convert(n: str) -> str:
    cfg = LECTURES[n]
    text = (SRC / f"lecture{n}.md").read_text()
    out_dir = REPO / "docs" / "tutorials" / cfg["slug"]
    img_dir = out_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    # 1. images -> local webp, in order of appearance (same order as tokens.tsv)
    counter = {"i": 0}

    def img(m):
        counter["i"] += 1
        i = counter["i"]
        shutil.copy(SRC / "webp" / f"{n}-{i:02d}.webp", img_dir / f"{i:02d}.webp")
        return f"![{short_alt(m.group(1))}](./images/{i:02d}.webp)"

    text = re.sub(r"!\[([^\]]*)\]\(https://feishu\.cn/file/[A-Za-z0-9]+\)", img, text)

    # 2. header: drop <title>, the TRAE logo (first image), promo line and bookmark
    text = re.sub(r"<title>.*?</title>\s*", "", text, count=1, flags=re.S)
    text = re.sub(r"^!\[[^\]]*\]\(\./images/01\.webp\)\s*", "", text, count=1)
    (img_dir / "01.webp").unlink(missing_ok=True)  # the sponsor logo is not published
    text = re.sub(r"TRAE 高校扶持计划：[^\n]*\n", "", text, count=1)
    text = re.sub(r"<bookmark[^>]*></bookmark>\s*", "", text)
    m = re.search(r"以下内容根据唐国豪教授量化投资课程整理，作者：([^\n]+)\n", text)
    authors = m.group(1).strip() if m else ""
    title = re.search(r"^title: (.+)$", cfg["front"], re.M).group(1)
    header = (
        f"# {title}\n\n"
        f"> 本讲根据**湖南大学金融与统计学院唐国豪教授《量化投资》课程**整理，整理：{authors}。  \n"
        f"> 飞书原文：[飞书文档]({cfg['feishu']}) · 本讲得到 [TRAE 高校扶持计划]({TRAE_URL}) 支持。\n\n"
        "::: warning 数据说明\n"
        "本讲使用 CSMAR 国泰安数据库的数据，需要高校或机构账号才能下载；数据和课程配套代码不随本页公开。\n"
        ":::\n"
    )
    text = re.sub(r"以下内容根据唐国豪教授量化投资课程整理，作者：[^\n]+\n", "", text, count=1)
    text = re.sub(r"^\s*---\s*\n", "", text.lstrip(), count=1)  # the divider under the byline

    # 3. attachments (not published)
    text = re.sub(
        r"证监会行业指引文件，Sas版代码，python版代码\s*<figure[^>]*>.*?</figure>",
        "参考程序（证监会行业指引文件、SAS 版和 Python 版代码）是课程配套资料，未随本页公开。",
        text,
        flags=re.S,
    )
    text = re.sub(r"<figure[^>]*>.*?</figure>\s*", "", text, flags=re.S)

    # 4. embedded sheets -> markdown tables (report names link to the PDFs in the repo)
    def sheet(m):
        table = SHEETS[m.group(1)].replace("****", "")
        for name, path in REPORTS.items():
            table = table.replace(name, f"[{Path(name).stem}]({report_link(path)})")
        return "\n" + table + "\n"

    text = re.sub(r'<sheet sheet-id="([A-Za-z0-9]+)"[^>]*>(?:</sheet>)?', sheet, text)

    # 5. callouts -> VitePress containers; keep the prompt's line breaks
    def callout(m):
        emoji, body = m.group(1), m.group(2).strip("\n")
        lines = body.split("\n")
        heading = ""
        if lines and re.fullmatch(r"\*\*[^*]+[：:]?\*\*", lines[0].strip()):
            heading = lines[0].strip().strip("*").rstrip("：:")
            lines = lines[1:]
        kind = "tip" if emoji.startswith("🧑") else "info"
        title = f"{emoji} {heading or ('提示词' if kind == 'tip' else '提示')}"
        body = "  \n".join(l.rstrip() for l in lines if l.strip() != "")
        return f"\n::: {kind} {title}\n{body}\n:::\n"

    text = re.sub(r'<callout emoji="([^"]+)">\s*(.*?)\s*</callout>', callout, text, flags=re.S)

    # 6. side-by-side images
    def grid(m):
        cols = re.findall(r'<column width-ratio="([0-9.]+)">\s*(.*?)\s*</column>', m.group(1), flags=re.S)
        tmpl = " ".join(f"{float(r):.3f}fr" for r, _ in cols)
        inner = "\n".join(f'<div>\n\n{c.strip()}\n\n</div>' for _, c in cols)
        return f'\n<div class="lecture-grid" style="grid-template-columns: {tmpl}">\n{inner}\n</div>\n'

    text = re.sub(r"<grid>(.*?)</grid>", grid, text, flags=re.S)

    # 7. the page title is the only h1: shift every body heading down one level
    text = re.sub(r"^(#{1,5}) ", r"#\1 ", text, flags=re.M)

    # 8. tidy: bold-wrapped headings, bare URLs in the reading list, blank-line runs
    text = re.sub(r"^(#{1,6}) \*\*(.+?)\*\*\s*$", r"\1 \2", text, flags=re.M)
    text = re.sub(r"(?<![(\[<])(https?://[^\s)<>]+)", r"<\1>", text)
    text = re.sub(r"\]\(<(https?://[^>]+)>\)", r"](\1)", text)  # undo inside markdown links
    text = re.sub(r"\[<(https?://[^>]+)>\]", r"[\1]", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"

    page = cfg["front"] + "\n" + header + "\n" + text + "\n---\n\n本讲用于教育与研究，不构成投资建议。\n"
    (out_dir / "index.md").write_text(page)
    leftovers = sorted(set(re.findall(r"<(callout|grid|column|sheet|figure|bookmark|source|title)\b", page)))
    print(f"{cfg['slug']}: {counter['i']} images, {len(page)} chars, leftover tags: {leftovers or 'none'}")


for n in sys.argv[1:] or ["01", "02"]:
    convert(n)
