from __future__ import annotations

from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
WEEK3_DIR = ROOT / "outputs" / "week3"
FIGURE_DIR = ROOT / "reports" / "week3" / "nltk_lda_figures"

COLORS = {
    "positive": "#2A9D8F",
    "neutral": "#E9C46A",
    "negative": "#E76F51",
    "baseline_dictionary": "#457B9D",
    "nltk_vader": "#D1495B",
}
TOPIC_COLOR_MAP = {1: "#1F5D78", 2: "#D98E04", 3: "#4C956C"}
SENTIMENT_ORDER = ["positive", "neutral", "negative"]


def set_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.facecolor": "#F7F3EA",
            "axes.facecolor": "#FFFDF8",
            "axes.edgecolor": "#D8D2C4",
            "axes.titleweight": "bold",
            "axes.titlesize": 15,
            "axes.labelsize": 11,
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "grid.color": "#E7E1D5",
            "grid.linewidth": 0.8,
        }
    )


def save_figure(fig: plt.Figure, filename: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        FIGURE_DIR / filename,
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)


def short_topic(label: str) -> str:
    name = str(label).split(":", maxsplit=1)[-1].strip()
    return textwrap.fill(name, width=30)


def plot_sentiment_method_comparison() -> None:
    data = pd.read_csv(WEEK3_DIR / "week3_nltk_sentiment_distribution.csv")
    pivot = (
        data.pivot(index="sentiment_label", columns="method", values="product_share")
        .reindex(SENTIMENT_ORDER)
        .fillna(0)
    )
    methods = ["baseline_dictionary", "nltk_vader"]
    method_labels = ["Baseline dictionary", "NLTK VADER"]
    positions = np.arange(len(SENTIMENT_ORDER))
    width = 0.36

    fig, (ax_full, ax_detail) = plt.subplots(1, 2, figsize=(12.5, 5.3))
    for index, (method, label) in enumerate(zip(methods, method_labels)):
        values = pivot[method].to_numpy()
        bars = ax_full.bar(
            positions + (index - 0.5) * width,
            values,
            width,
            color=COLORS[method],
            label=label,
        )
        ax_full.bar_label(bars, labels=[f"{value:.1%}" for value in values], padding=3)

    ax_full.set_title("Overall sentiment distribution")
    ax_full.set_xticks(positions, [label.title() for label in SENTIMENT_ORDER])
    ax_full.set_ylabel("Share of product records")
    ax_full.yaxis.set_major_formatter(PercentFormatter(1))
    ax_full.set_ylim(0, 1.04)
    ax_full.legend(frameon=False, loc="upper right")

    detail_labels = ["neutral", "negative"]
    detail_positions = np.arange(len(detail_labels))
    for index, (method, label) in enumerate(zip(methods, method_labels)):
        values = pivot.loc[detail_labels, method].to_numpy()
        bars = ax_detail.bar(
            detail_positions + (index - 0.5) * width,
            values,
            width,
            color=COLORS[method],
            label=label,
        )
        ax_detail.bar_label(bars, labels=[f"{value:.1%}" for value in values], padding=3)

    ax_detail.set_title("Neutral and negative detail")
    ax_detail.set_xticks(detail_positions, [label.title() for label in detail_labels])
    ax_detail.set_ylabel("Share of product records")
    ax_detail.yaxis.set_major_formatter(PercentFormatter(1))
    ax_detail.set_ylim(0, 0.065)
    fig.suptitle(
        "Baseline Dictionary vs NLTK VADER",
        fontsize=20,
        fontweight="bold",
        x=0.04,
        y=0.98,
        ha="left",
    )
    fig.text(
        0.04,
        0.89,
        "VADER identifies more negative records while the overall positive share remains unchanged.",
        color="#5D625F",
    )
    fig.subplots_adjust(top=0.72, wspace=0.28)
    save_figure(fig, "01_nltk_sentiment_method_comparison.png")


def plot_sentiment_confusion_matrix() -> None:
    data = pd.read_csv(WEEK3_DIR / "week3_nltk_sentiment_confusion.csv")
    matrix = (
        data.pivot(
            index="baseline_sentiment_label",
            columns="vader_sentiment_label",
            values="product_count",
        )
        .reindex(index=SENTIMENT_ORDER, columns=SENTIMENT_ORDER)
        .fillna(0)
        .astype(int)
    )
    values = matrix.to_numpy()
    total = values.sum()

    fig, ax = plt.subplots(figsize=(8.2, 6.5))
    image = ax.imshow(
        values,
        cmap="YlOrRd",
        norm=LogNorm(vmin=1, vmax=max(1, values.max())),
    )
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            count = values[row, column]
            share = count / total
            color = "white" if count > values.max() * 0.1 else "#2D3230"
            ax.text(
                column,
                row,
                f"{count:,}\n{share:.1%}",
                ha="center",
                va="center",
                fontweight="bold",
                color=color,
            )

    ax.set_xticks(range(3), [label.title() for label in SENTIMENT_ORDER])
    ax.set_yticks(range(3), [label.title() for label in SENTIMENT_ORDER])
    ax.set_xlabel("NLTK VADER label")
    ax.set_ylabel("Baseline dictionary label")
    ax.set_title("Where the Two Sentiment Methods Agree and Disagree", pad=20)
    fig.colorbar(image, ax=ax, label="Product record count (log scale)", shrink=0.78)
    fig.text(
        0.5,
        0.02,
        "Diagonal cells are agreements; off-diagonal cells show changed classifications.",
        ha="center",
        color="#5D625F",
    )
    save_figure(fig, "02_nltk_sentiment_confusion_matrix.png")


def plot_topic_sentiment_composition() -> None:
    data = pd.read_csv(WEEK3_DIR / "week3_lda_product_topics.csv")
    counts = pd.crosstab(data["lda_topic_label"], data["vader_sentiment_label"])
    counts = counts.reindex(columns=SENTIMENT_ORDER, fill_value=0)
    shares = counts.div(counts.sum(axis=1), axis=0)
    shares = shares.loc[counts.sum(axis=1).sort_values(ascending=True).index]
    labels = [short_topic(label) for label in shares.index]

    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    left = np.zeros(len(shares))
    for sentiment in SENTIMENT_ORDER:
        values = shares[sentiment].to_numpy()
        bars = ax.barh(
            labels,
            values,
            left=left,
            color=COLORS[sentiment],
            label=sentiment.title(),
            height=0.58,
        )
        for bar, value, start in zip(bars, values, left):
            if value >= 0.025:
                ax.text(
                    start + value / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{value:.1%}",
                    ha="center",
                    va="center",
                    color="white" if sentiment != "neutral" else "#3B3F3D",
                    fontweight="bold",
                )
        left += values

    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xlabel("Share within each LDA topic")
    ax.set_ylabel("")
    ax.set_title("NLTK VADER Sentiment Composition within LDA Topics", pad=18)
    ax.legend(ncol=3, frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.23))
    fig.text(
        0.5,
        0.01,
        "This view connects what customers discuss (LDA) with how they feel (VADER).",
        ha="center",
        color="#5D625F",
    )
    fig.subplots_adjust(left=0.31, bottom=0.24)
    save_figure(fig, "03_lda_topic_sentiment_composition.png")


def plot_topic_business_summary() -> None:
    data = pd.read_csv(WEEK3_DIR / "week3_lda_topic_summary.csv").sort_values(
        "product_count", ascending=True
    )
    labels = [short_topic(label) for label in data["lda_topic_label"]]
    colors = [TOPIC_COLOR_MAP[int(topic_id)] for topic_id in data["lda_topic_id"]]

    fig, (ax_coverage, ax_risk) = plt.subplots(1, 2, figsize=(13.5, 6.2))
    coverage_bars = ax_coverage.barh(labels, data["product_share"], color=colors, height=0.58)
    for bar, count, share in zip(
        coverage_bars, data["product_count"], data["product_share"]
    ):
        ax_coverage.text(
            bar.get_width() - 0.012,
            bar.get_y() + bar.get_height() / 2,
            f"{count:,} ({share:.1%})",
            ha="right",
            va="center",
            fontweight="bold",
            color="white",
        )
    ax_coverage.set_xlim(0, max(data["product_share"]) * 1.35)
    ax_coverage.xaxis.set_major_formatter(PercentFormatter(1))
    ax_coverage.set_xlabel("Share of product records")
    ax_coverage.set_title("Topic coverage")

    risk_bars = ax_risk.barh(
        labels,
        data["vader_negative_share"],
        color=colors,
        height=0.58,
    )
    for bar, negative_share, rating in zip(
        risk_bars, data["vader_negative_share"], data["avg_rating"]
    ):
        ax_risk.text(
            bar.get_width() + 0.0015,
            bar.get_y() + bar.get_height() / 2,
            f"{negative_share:.1%} negative | {rating:.2f} avg rating",
            va="center",
            fontweight="bold",
        )
    ax_risk.set_xlim(0, max(data["vader_negative_share"]) * 1.75)
    ax_risk.xaxis.set_major_formatter(PercentFormatter(1))
    ax_risk.set_xlabel("VADER negative share")
    ax_risk.set_title("Sentiment risk and average rating")
    ax_risk.tick_params(axis="y", labelleft=False)

    fig.suptitle(
        "LDA Topic Coverage and Business Risk",
        fontsize=20,
        fontweight="bold",
        x=0.04,
        ha="left",
    )
    fig.text(
        0.04,
        0.92,
        "Prioritize topics by both business reach and negative sentiment, not by one metric alone.",
        color="#5D625F",
    )
    fig.subplots_adjust(top=0.78, left=0.23, wspace=0.25)
    save_figure(fig, "04_lda_topic_business_summary.png")


def plot_topic_keywords() -> None:
    data = pd.read_csv(WEEK3_DIR / "week3_lda_topic_keywords.csv")
    topics = data["topic_id"].drop_duplicates().sort_values().tolist()
    fig, axes = plt.subplots(1, len(topics), figsize=(15.5, 6.5), sharex=False)
    if len(topics) == 1:
        axes = [axes]

    for ax, topic_id in zip(axes, topics):
        color = TOPIC_COLOR_MAP[int(topic_id)]
        topic_data = (
            data.loc[data["topic_id"].eq(topic_id)]
            .nsmallest(8, "word_rank")
            .sort_values("keyword_weight", ascending=True)
        )
        bars = ax.barh(
            topic_data["keyword"],
            topic_data["keyword_weight"],
            color=color,
            height=0.62,
        )
        ax.bar_label(bars, fmt="%.0f", padding=3, fontsize=8)
        ax.set_title(short_topic(topic_data["topic_label"].iloc[0]), fontsize=12, pad=12)
        ax.set_xlabel("LDA keyword weight")
        ax.grid(axis="y", visible=False)

    fig.suptitle(
        "Top Keywords Learned by the LDA Model",
        fontsize=20,
        fontweight="bold",
        x=0.04,
        ha="left",
    )
    fig.text(
        0.04,
        0.92,
        "Higher weights indicate words that contribute more strongly to each topic.",
        color="#5D625F",
    )
    fig.subplots_adjust(top=0.76, wspace=0.45)
    save_figure(fig, "05_lda_topic_keywords.png")


def main() -> None:
    set_style()
    plot_sentiment_method_comparison()
    plot_sentiment_confusion_matrix()
    plot_topic_sentiment_composition()
    plot_topic_business_summary()
    plot_topic_keywords()
    print(f"Generated 5 figures in: {FIGURE_DIR}")


if __name__ == "__main__":
    main()
