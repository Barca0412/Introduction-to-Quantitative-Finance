"""
Generate interactive charts from stats.json using Plotly.
Creates HTML files that can be embedded in VitePress.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any

import plotly.graph_objects as go

# Paths
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
PUBLIC_DIR = BASE_DIR / "docs" / "public"
CHARTS_DIR = PUBLIC_DIR / "arxiv-charts"
DATA_PUBLIC_DIR = PUBLIC_DIR / "arxiv-data"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_PUBLIC_DIR.mkdir(parents=True, exist_ok=True)


def copy_data_to_public():
    """Copy data files to public directory for frontend access."""
    try:
        shutil.copy2(DATA_DIR / "papers.json", DATA_PUBLIC_DIR / "papers.json")
        shutil.copy2(DATA_DIR / "stats.json", DATA_PUBLIC_DIR / "stats.json")
        embeddings_file = DATA_DIR / "embeddings_index.json"
        if embeddings_file.exists():
            shutil.copy2(embeddings_file, DATA_PUBLIC_DIR / "embeddings_index.json")
        print("Copied data files to public directory")
    except Exception as e:
        print(f"Warning: Could not copy data files: {e}")


def load_stats() -> Dict[str, Any]:
    """Load statistics from JSON file."""
    stats_file = DATA_DIR / "stats.json"
    with open(stats_file, "r", encoding="utf-8") as f:
        return json.load(f)


def create_trend_chart(
    stats: Dict[str, Any],
    chart_type: str = "tags",
    mode: str = "daily"
) -> go.Figure:
    """
    Create a trend chart using Plotly.

    Args:
        stats: Statistics data
        chart_type: 'tags' or 'keywords'
        mode: 'daily' or 'cumulative'

    Returns:
        Plotly Figure object
    """
    # Map chart_type to the actual key in stats JSON
    stats_key = f"{chart_type.rstrip('s')}_stats"  # tags -> tag_stats, keywords -> keyword_stats
    data = stats.get(stats_key, {}).get("_all", {}).get(mode, [])
    if not data:
        # Create empty figure
        fig = go.Figure()
        fig.update_layout(
            title=f"No data for {chart_type} ({mode})",
            height=500
        )
        return fig

    # Extract all unique keys (tags or keywords)
    all_keys = set()
    for item in data:
        all_keys.update(item.get("counts", {}).keys())

    sorted_keys = sorted(all_keys)
    dates = [item["date"] for item in data]

    # Create figure
    fig = go.Figure()

    # Define color palette
    colors = [
        "#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444",
        "#06b6d4", "#ec4899", "#84cc16", "#6366f1", "#14b8a6"
    ]

    # Add traces for each key
    for i, key in enumerate(sorted_keys):
        counts = [item.get("counts", {}).get(key, 0) for item in data]
        color = colors[i % len(colors)]

        fig.add_trace(go.Scatter(
            x=dates,
            y=counts,
            mode='lines+markers',
            name=key,
            line=dict(color=color, width=2),
            marker=dict(size=4),
            hovertemplate=f"<b>{key}</b><br>Date: %{{x}}<br>Count: %{{y}}<extra></extra>"
        ))

    # Update layout
    chart_title = {
        "tags": "Research Tags",
        "keywords": "Keywords"
    }[chart_type]

    mode_title = {
        "daily": "Daily Count",
        "cumulative": "Cumulative Count"
    }[mode]

    fig.update_layout(
        title=dict(
            text=f"{chart_title} - {mode_title}",
            font=dict(size=18, color="#1f2937")
        ),
        height=500,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        margin=dict(l=50, r=20, t=60, b=60),
        xaxis=dict(
            title=dict(text="Date", font=dict(size=14)),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=dict(text="Count", font=dict(size=14)),
            tickfont=dict(size=12)
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif")
    )

    return fig


def generate_all_charts(stats: Dict[str, Any]):
    """Generate all chart combinations and save as HTML."""
    chart_types = ["tags", "keywords"]
    modes = ["daily", "cumulative"]

    for chart_type in chart_types:
        for mode in modes:
            fig = create_trend_chart(stats, chart_type, mode)

            # Generate HTML filename
            filename = f"{chart_type}_{mode}.html"
            filepath = CHARTS_DIR / filename

            # Save as standalone HTML
            fig.write_html(
                str(filepath),
                include_plotlyjs="cdn",
                full_html=True,
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                }
            )

            print(f"Generated: {filename}")


def create_combined_trend_chart(stats: Dict[str, Any]) -> go.Figure:
    """
    Create a chart with tabs for different views.
    Uses Plotly's dropdown button feature.

    Args:
        stats: Statistics data

    Returns:
        Plotly Figure object
    """
    # Get data for all combinations
    datasets = []
    buttons = []

    chart_types = [("tags", "Tags"), ("keywords", "Keywords")]
    modes = [("daily", "Daily"), ("cumulative", "Cumulative")]

    for chart_type, type_label in chart_types:
        for mode, mode_label in modes:
            stats_key = f"{chart_type.rstrip('s')}_stats"
            data = stats.get(stats_key, {}).get("_all", {}).get(mode, [])
            if not data:
                continue

            # Extract all unique keys
            all_keys = set()
            for item in data:
                all_keys.update(item.get("counts", {}).keys())

            sorted_keys = sorted(all_keys)
            dates = [item["date"] for item in data]

            # Create traces
            traces = []
            colors = [
                "#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444",
                "#06b6d4", "#ec4899", "#84cc16", "#6366f1", "#14b8a6"
            ]

            for i, key in enumerate(sorted_keys):
                counts = [item.get("counts", {}).get(key, 0) for item in data]
                color = colors[i % len(colors)]

                traces.append(go.Scatter(
                    x=dates,
                    y=counts,
                    mode='lines+markers',
                    name=key,
                    line=dict(color=color, width=2),
                    marker=dict(size=4),
                    visible=True if len(datasets) == 0 else "legendonly"
                ))

            datasets.append({
                "type": chart_type,
                "mode": mode,
                "label": f"{type_label} - {mode_label}",
                "traces": traces
            })

    if not datasets:
        fig = go.Figure()
        fig.update_layout(title="No chart data available")
        return fig

    # Create figure with first dataset
    fig = go.Figure(data=datasets[0]["traces"])

    # Add updatemenu buttons
    updatemenus: list[dict[str, Any]] = [
        dict(
            active=0,
            buttons=list(),
            x=0.1,
            xanchor="left",
            y=1.02,
            yanchor="bottom",
            direction="right",
            bgcolor="white",
            bordercolor="#e5e7eb",
            font=dict(size=12)
        )
    ]

    # Create buttons for each dataset
    for i, dataset in enumerate(datasets):
        button = dict(
            label=dataset["label"],
            method="update",
            args=[
                {"visible": [True] * len(dataset["traces"])},
                {"title": {"text": f"Research Trends - {dataset['label']}"}}
            ]
        )
        updatemenus[0]["buttons"].append(button)

    fig.update_layout(
        updatemenus=updatemenus,
        title=dict(
            text=f"Research Trends - {datasets[0]['label']}",
            font=dict(size=18, color="#1f2937")
        ),
        height=500,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        margin=dict(l=50, r=20, t=60, b=60),
        xaxis=dict(
            title=dict(text="Date", font=dict(size=14)),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=dict(text="Count", font=dict(size=14)),
            tickfont=dict(size=12)
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif")
    )

    return fig


def generate_combined_chart(stats: Dict[str, Any]):
    """Generate combined chart with dropdown tabs."""
    try:
        fig = create_combined_trend_chart(stats)

        filepath = CHARTS_DIR / "combined.html"
        fig.write_html(
            str(filepath),
            include_plotlyjs="cdn",
            full_html=True,
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
            }
        )

        print(f"Generated: combined.html")
    except Exception as e:
        print(f"Warning: Could not generate combined chart: {e}")


if __name__ == "__main__":
    print("Loading stats...")
    stats = load_stats()

    print("Generating charts...")
    generate_all_charts(stats)

    print("\nGenerating combined chart...")
    generate_combined_chart(stats)

    print(f"\nAll charts saved to: {CHARTS_DIR}")
