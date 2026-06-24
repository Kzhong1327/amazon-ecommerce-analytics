from __future__ import annotations

from pathlib import Path

import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer


ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = ROOT / "data" / "processed"
WEEK3_DIR = ROOT / "outputs" / "week3"


def vader_label(compound: float) -> str:
    if compound >= 0.05:
        return "positive"
    if compound <= -0.05:
        return "negative"
    return "neutral"


def main() -> None:
    amazon = pd.read_csv(
        PROCESSED_DIR / "amazon_products_cleaned.csv",
        dtype={"product_id": "string"},
    )
    baseline = pd.read_csv(
        WEEK3_DIR / "week3_product_sentiment_topics.csv",
        dtype={"product_id": "string"},
    )[
        [
            "product_id",
            "sentiment_score",
            "sentiment_label",
            "dominant_topic",
        ]
    ].rename(
        columns={
            "sentiment_score": "baseline_sentiment_score",
            "sentiment_label": "baseline_sentiment_label",
        }
    )

    analyzer = SentimentIntensityAnalyzer()
    review_text = amazon["review_content"].fillna("").astype(str)
    vader = pd.DataFrame(review_text.map(analyzer.polarity_scores).tolist())
    vader = vader.rename(
        columns={
            "neg": "vader_negative_score",
            "neu": "vader_neutral_score",
            "pos": "vader_positive_score",
            "compound": "vader_compound_score",
        }
    )
    vader["vader_sentiment_label"] = vader["vader_compound_score"].map(vader_label)

    if len(amazon) != len(baseline) or not amazon["product_id"].reset_index(drop=True).equals(
        baseline["product_id"].reset_index(drop=True)
    ):
        raise ValueError("Baseline rows are not aligned with the cleaned Amazon data.")

    comparison = pd.concat(
        [
            amazon[
                [
                    "product_id",
                    "product_name",
                    "main_category",
                    "rating_num",
                    "rating_count_num",
                    "review_length_chars",
                ]
            ].reset_index(drop=True),
            vader,
            baseline.drop(columns="product_id").reset_index(drop=True),
        ],
        axis=1,
    )
    comparison["label_agreement"] = comparison["vader_sentiment_label"].eq(
        comparison["baseline_sentiment_label"]
    )
    comparison.to_csv(
        WEEK3_DIR / "week3_nltk_vader_sentiment_comparison.csv",
        index=False,
    )

    method_rows = []
    for method, column in [
        ("baseline_dictionary", "baseline_sentiment_label"),
        ("nltk_vader", "vader_sentiment_label"),
    ]:
        counts = comparison[column].value_counts()
        for label in ["positive", "neutral", "negative"]:
            count = int(counts.get(label, 0))
            method_rows.append(
                {
                    "method": method,
                    "sentiment_label": label,
                    "product_count": count,
                    "product_share": count / len(comparison),
                }
            )
    pd.DataFrame(method_rows).to_csv(
        WEEK3_DIR / "week3_nltk_sentiment_distribution.csv",
        index=False,
    )

    confusion = (
        comparison.groupby(
            ["baseline_sentiment_label", "vader_sentiment_label"],
            dropna=False,
        )
        .agg(product_count=("product_id", "size"))
        .reset_index()
    )
    confusion["product_share"] = confusion["product_count"] / len(comparison)
    confusion.to_csv(
        WEEK3_DIR / "week3_nltk_sentiment_confusion.csv",
        index=False,
    )

    category = (
        comparison.groupby("main_category", dropna=False)
        .agg(
            product_count=("product_id", "size"),
            avg_rating=("rating_num", "mean"),
            avg_vader_compound=("vader_compound_score", "mean"),
            vader_positive_share=(
                "vader_sentiment_label",
                lambda s: float(s.eq("positive").mean()),
            ),
            vader_neutral_share=(
                "vader_sentiment_label",
                lambda s: float(s.eq("neutral").mean()),
            ),
            vader_negative_share=(
                "vader_sentiment_label",
                lambda s: float(s.eq("negative").mean()),
            ),
            baseline_vader_agreement=("label_agreement", "mean"),
        )
        .reset_index()
        .sort_values("product_count", ascending=False)
    )
    category.to_csv(
        WEEK3_DIR / "week3_nltk_category_sentiment.csv",
        index=False,
    )

    disagreements = comparison.loc[~comparison["label_agreement"]].copy()
    disagreements["vader_strength"] = disagreements["vader_compound_score"].abs()
    disagreements = disagreements.sort_values(
        ["rating_count_num", "vader_strength"],
        ascending=[False, False],
    ).head(100)
    disagreements.to_csv(
        WEEK3_DIR / "week3_nltk_disagreement_samples.csv",
        index=False,
    )

    print("NLTK VADER outputs generated.")
    print(f"Products analyzed: {len(comparison):,}")
    print(f"Baseline/VADER agreement: {comparison['label_agreement'].mean():.2%}")
    print(
        "VADER labels:",
        comparison["vader_sentiment_label"].value_counts().to_dict(),
    )


if __name__ == "__main__":
    main()
