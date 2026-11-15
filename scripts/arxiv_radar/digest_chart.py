"""The "谁在做" chart of the weekly digest: an inline SVG drawn from the facts (no LLM).

Three parts, read top to bottom:
  left   institutions with >= 2 papers this week, bar colour = type (高校 / 企业 / 其他)
  right  countries and regions (one neutral colour: the count is the message)
  bottom how the papers' author teams are made up (one stacked bar, 100 %)

Colours (dataviz reference palette, validated light and dark, no blue): 高校 aqua,
校企合作 violet, 企业 orange; "other" and "unknown" are greys, not series colours. Every bar
carries its number, so colour is never the only cue; each mark has a <title> tooltip.
Text uses the site's text variables, so it follows light / dark mode.
"""

from __future__ import annotations

from html import escape
from typing import Any, Dict, List

TYPE_COLOUR = {"高校": "#1baf7a", "企业": "#eb6834"}
OTHER = "#a3a29c"
UNKNOWN = "#d6d5cf"
NEUTRAL = "#8a8984"
MIX = [("只有高校", "#1baf7a"), ("校企合作", "#6250d6"), ("只有企业", "#eb6834"),
       ("其他类型机构", OTHER), ("未查到机构", UNKNOWN)]

WIDTH = 720
ROW = 24
TEXT = "fill:var(--vp-c-text-1,#1f1f1f)"
MUTED = "fill:var(--vp-c-text-2,#5c5b57)"
FONT = "font-family:-apple-system,'PingFang SC','Noto Sans SC','Microsoft YaHei',sans-serif"


def _text(x: float, y: float, s: str, size: int = 13, style: str = TEXT, anchor: str = "start") -> str:
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" text-anchor="{anchor}" '
            f'style="{style};{FONT}">{escape(s)}</text>')


def _bar(x: float, y: float, w: float, h: float, colour: str, tip: str) -> str:
    w = max(w, 2)
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="3" fill="{colour}">'
            f'<title>{escape(tip)}</title></rect>')


def _bars(items: List[Dict[str, Any]], x0: float, width: float, y0: float, label_w: float,
          colour_of) -> List[str]:
    out = []
    top = max((i["n"] for i in items), default=1)
    span = width - label_w - 34
    for k, item in enumerate(items):
        y = y0 + k * ROW
        name = item["name"] if len(item["name"]) <= 12 else item["name"][:11] + "…"
        out.append(_text(x0 + label_w - 8, y + 13, name, anchor="end"))
        w = span * item["n"] / top
        out.append(_bar(x0 + label_w, y + 2, w, 14, colour_of(item), f"{item['name']}：{item['n']} 篇"))
        out.append(_text(x0 + label_w + w + 6, y + 13, str(item["n"]), size=12, style=MUTED))
    return out


def who_svg(who: Dict[str, Any], papers: int) -> str:
    """One line of inline SVG (Markdown keeps an HTML block only without blank lines)."""
    insts = (who.get("institutions") or [])[:8]
    countries = (who.get("countries") or [])[:8]
    rows = max(len(insts), len(countries), 1)
    half = WIDTH / 2
    parts = [_text(0, 16, "发文 2 篇以上的机构", 14), _text(half + 16, 16, "作者所在国家和地区", 14)]
    if insts:
        parts += _bars(insts, 0, half, 28, 150, lambda i: TYPE_COLOUR.get(i.get("type", ""), OTHER))
    else:
        parts.append(_text(0, 46, "本周没有机构发文超过 1 篇", style=MUTED))
    parts += _bars(countries, half + 16, half - 16, 28, 96, lambda i: NEUTRAL)

    # Legend for the institution colours (only the types that appear).
    y = 28 + rows * ROW + 8
    x = 0.0
    for name, colour in (("高校", TYPE_COLOUR["高校"]), ("企业", TYPE_COLOUR["企业"]), ("其他", OTHER)):
        if any((i.get("type") or "其他") == name or (name == "其他" and i.get("type") not in TYPE_COLOUR) for i in insts):
            parts.append(f'<rect x="{x:.0f}" y="{y}" width="10" height="10" rx="2" fill="{colour}"/>')
            parts.append(_text(x + 15, y + 9, name, 12, MUTED))
            x += 60

    # Team make-up: one stacked bar over all the week's papers.
    mix = who.get("collaboration") or {}
    y += 34
    parts.append(_text(0, y, f"作者团队构成（共 {papers} 篇）", 14))
    y += 10
    total = sum(mix.values()) or 1
    x = 0.0
    labels = []
    for name, colour in MIX:
        n = mix.get(name, 0)
        if not n:
            continue
        w = WIDTH * n / total
        parts.append(_bar(x, y, w - 2, 18, colour, f"{name}：{n} 篇"))
        labels.append((x, name, n, colour))
        x += w
    # Legend under the bar: left to right, wrapping to a new line when full.
    lx, ly = 0.0, y + 28
    for _, name, n, colour in labels:
        label = f"{name} {n}"
        w = 14 + sum(12 if ord(ch) > 0x2E80 else 7 for ch in label) + 18
        if lx and lx + w > WIDTH:
            lx, ly = 0.0, ly + 20
        parts.append(f'<rect x="{lx:.0f}" y="{ly}" width="10" height="10" rx="2" fill="{colour}"/>')
        parts.append(_text(lx + 14, ly + 9, label, 12, MUTED))
        lx += w
    height = ly + 20
    cross = who.get("cross_country_papers")
    if cross is not None:
        parts.append(_text(0, height + 10, f"其中跨国合作 {cross} 篇（作者来自两个及以上国家和地区）", 12, MUTED))
        height += 22
    return (f'<svg viewBox="0 0 {WIDTH} {height:.0f}" width="100%" role="img" '
            f'aria-label="本周论文的机构、国家和地区、作者团队构成" style="max-width:{WIDTH}px">'
            + "".join(parts) + "</svg>")
