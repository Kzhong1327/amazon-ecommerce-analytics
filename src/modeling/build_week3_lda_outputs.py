from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = ROOT / "data" / "processed"
WEEK3_DIR = ROOT / "outputs" / "week3"

RANDOM_STATE = 42
TOPIC_CANDIDATES = range(3, 9)
TOP_WORDS = 12

DOMAIN_STOPWORDS = {
    "amazon",
    "buy",
    "bought",
    "good",
    "great",
    "best",
    "don",
    "https",
    "images",
    "item",
    "just",
    "like",
    "nice",
    "one",
    "media",
    "overall",
    "price",
    "product",
    "products",
    "quality",
    "really",
    "review",
    "reviews",
    "use",
    "used",
    "using",
    "well",
    "work",
    "worked",
    "working",
    "works",
}

TOPIC_LABELS = {
    1: "Value, Usability & Everyday Products",
    2: "Smart Devices, Wearables & Audio",
    3: "Charging, Cables & Connectivity",
}


def load_data() -> pd.DataFrame:
    amazon = pd.read_csv(
        PROCESSED_DIR / "amazon_products_cleaned.csv",
        dtype={"product_id": "string"},
    )
    sentiment_path = WEEK3_DIR / "week3_nltk_vader_sentiment_comparison.csv"
    if sentiment_path.exists():
        sentiment = pd.read_csv(sentiment_path, dtype={"product_id": "string"})
        if len(amazon) != len(sentiment) or not amazon["product_id"].reset_index(
            drop=True
        ).equals(sentiment["product_id"].reset_index(drop=True)):
            raise ValueError("NLTK sentiment rows are not aligned with the Amazon data.")
        amazon["vader_compound_score"] = sentiment["vader_compound_score"]
        amazon["vader_sentiment_label"] = sentiment["vader_sentiment_label"]
    return amazon


def build_vectorizer() -> CountVectorizer:
    stopwords = sorted(set(ENGLISH_STOP_WORDS) | DOMAIN_STOPWORDS)
    return CountVectorizer(
        lowercase=True,
        stop_words=stopwords,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z]{2,}\b",
        ngram_range=(1, 2),
        min_df=5,
        max_df=0.90,
        max_features=3000,
    )


def compare_topic_counts(
    train_matrix,
    test_matrix,
) -> pd.DataFrame:
    rows = []
    for topic_count in TOPIC_CANDIDATES:
        model = LatentDirichletAllocation(
            n_components=topic_count,
            learning_method="batch",
            max_iter=30,
            random_state=RANDOM_STATE,
            evaluate_every=-1,
        )
        model.fit(train_matrix)
        rows.append(
            {
                "topic_count": topic_count,
                "heldout_perplexity": model.perplexity(test_matrix),
                "train_log_likelihood": model.score(train_matrix),
            }
        )

    comparison = pd.DataFrame(rows)
    selected_topics = int(
        comparison.loc[comparison["heldout_perplexity"].idxmin(), "topic_count"]
    )
    comparison["selected_model"] = comparison["topic_count"].eq(selected_topics)
    return comparison


def get_topic_keywords(
    model: LatentDirichletAllocation,
    feature_names: np.ndarray,
) -> tuple[pd.DataFrame, dict[int, str]]:
    rows = []
    labels = {}
    for topic_index, weights in enumerate(model.components_, start=1):
        top_indices = weights.argsort()[::-1][:TOP_WORDS]
        words = feature_names[top_indices]
        topic_name = TOPIC_LABELS.get(topic_index, " | ".join(words[:3]))
        label = f"Topic {topic_index}: {topic_name}"
        labels[topic_index] = label
        for rank, feature_index in enumerate(top_indices, start=1):
            rows.append(
                {
                    "topic_id": topic_index,
                    "topic_label": label,
                    "word_rank": rank,
                    "keyword": feature_names[feature_index],
                    "keyword_weight": weights[feature_index],
                }
            )
    return pd.DataFrame(rows), labels


def build_product_topics(
    amazon: pd.DataFrame,
    topic_probabilities: np.ndarray,
    topic_labels: dict[int, str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    dominant_indices = topic_probabilities.argmax(axis=1)
    dominant_topic_ids = dominant_indices + 1
    dominant_probabilities = topic_probabilities.max(axis=1)

    columns = [
        "product_id",
        "product_name",
        "main_category",
        "sub_category",
        "rating_num",
        "rating_count_num",
        "discount_percentage_num",
        "estimated_revenue_proxy",
        "review_length_chars",
    ]
    product_topics = amazon[columns].copy()
    product_topics.insert(0, "amazon_record_id", np.arange(1, len(amazon) + 1))
    for optional_column in ["vader_compound_score", "vader_sentiment_label"]:
        if optional_column in amazon.columns:
            product_topics[optional_column] = amazon[optional_column]

    product_topics["lda_topic_id"] = dominant_topic_ids
    product_topics["lda_topic_label"] = [
        topic_labels[topic_id] for topic_id in dominant_topic_ids
    ]
    product_topics["lda_topic_probability"] = dominant_probabilities

    long_rows = []
    for row_index, product_id in enumerate(amazon["product_id"]):
        for topic_index, probability in enumerate(topic_probabilities[row_index], start=1):
            long_rows.append(
                {
                    "amazon_record_id": row_index + 1,
                    "product_id": product_id,
                    "main_category": amazon.iloc[row_index]["main_category"],
                    "topic_id": topic_index,
                    "topic_label": topic_labels[topic_index],
                    "topic_probability": probability,
                    "is_dominant_topic": topic_index == dominant_topic_ids[row_index],
                }
            )
    return product_topics, pd.DataFrame(long_rows)


def build_topic_summary(product_topics: pd.DataFrame) -> pd.DataFrame:
    aggregations = {
        "product_count": ("product_id", "size"),
        "avg_topic_probability": ("lda_topic_probability", "mean"),
        "avg_rating": ("rating_num", "mean"),
        "avg_rating_count": ("rating_count_num", "mean"),
        "estimated_commercial_weight": ("estimated_revenue_proxy", "sum"),
    }
    if "vader_compound_score" in product_topics.columns:
        aggregations["avg_vader_compound"] = ("vader_compound_score", "mean")
        aggregations["vader_negative_share"] = (
            "vader_sentiment_label",
            lambda values: float(values.eq("negative").mean()),
        )

    summary = (
        product_topics.groupby(["lda_topic_id", "lda_topic_label"], dropna=False)
        .agg(**aggregations)
        .reset_index()
    )
    summary["product_share"] = summary["product_count"] / len(product_topics)
    return summary.sort_values("product_count", ascending=False)


def main() -> None:
    WEEK3_DIR.mkdir(parents=True, exist_ok=True)
    amazon = load_data()
    review_text = amazon["review_content"].fillna("").astype(str)

    train_text, test_text = train_test_split(
        review_text,
        test_size=0.20,
        random_state=RANDOM_STATE,
    )
    vectorizer = build_vectorizer()
    train_matrix = vectorizer.fit_transform(train_text)
    test_matrix = vectorizer.transform(test_text)

    comparison = compare_topic_counts(train_matrix, test_matrix)
    selected_topics = int(
        comparison.loc[comparison["selected_model"], "topic_count"].iloc[0]
    )
    comparison.to_csv(WEEK3_DIR / "week3_lda_model_comparison.csv", index=False)

    full_matrix = vectorizer.transform(review_text)
    model = LatentDirichletAllocation(
        n_components=selected_topics,
        learning_method="batch",
        max_iter=50,
        random_state=RANDOM_STATE,
        evaluate_every=-1,
    )
    topic_probabilities = model.fit_transform(full_matrix)

    feature_names = vectorizer.get_feature_names_out()
    topic_keywords, topic_labels = get_topic_keywords(model, feature_names)
    topic_keywords.to_csv(WEEK3_DIR / "week3_lda_topic_keywords.csv", index=False)

    product_topics, topic_distribution = build_product_topics(
        amazon,
        topic_probabilities,
        topic_labels,
    )
    product_topics.to_csv(WEEK3_DIR / "week3_lda_product_topics.csv", index=False)
    topic_distribution.to_csv(
        WEEK3_DIR / "week3_lda_product_topic_distribution.csv",
        index=False,
    )

    topic_summary = build_topic_summary(product_topics)
    topic_summary.to_csv(WEEK3_DIR / "week3_lda_topic_summary.csv", index=False)

    print("LDA outputs generated.")
    print(f"Products analyzed: {len(product_topics):,}")
    print(f"Vocabulary size: {len(feature_names):,}")
    print(f"Selected topic count: {selected_topics}")
    print(topic_summary[["lda_topic_label", "product_count", "avg_rating"]].to_string(index=False))


if __name__ == "__main__":
    main()
    "quality",
