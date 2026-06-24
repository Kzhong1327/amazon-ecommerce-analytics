from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
TABLEAU_DIR = ROOT / "outputs" / "tableau"

RATING_COLUMNS = ["user_id", "product_id", "rating", "timestamp"]

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "can", "for",
    "from", "good", "great", "had", "has", "have", "he", "her", "his", "i", "if",
    "in", "is", "it", "its", "me", "my", "not", "of", "on", "or", "our", "so",
    "that", "the", "their", "them", "there", "this", "to", "too", "very", "was",
    "we", "were", "with", "you", "your", "product", "one", "will", "would", "also",
    "using", "use", "used", "get", "got", "really", "much", "amazon", "buy",
    "bought", "price", "all", "after", "only", "which", "it's", "they", "than",
    "then", "these", "those", "what", "when", "where", "who", "why", "how",
}

POSITIVE_WORDS = {
    "amazing", "awesome", "best", "better", "comfortable", "durable", "easy",
    "excellent", "fast", "fine", "fit", "good", "great", "happy", "impressive",
    "love", "loved", "nice", "perfect", "quality", "recommend", "satisfied",
    "smooth", "strong", "super", "useful", "value", "well", "working", "worth",
}

NEGATIVE_WORDS = {
    "bad", "broken", "cheap", "complaint", "complaints", "damage", "damaged",
    "defective", "disappointed", "issue", "issues", "low", "negative", "noise",
    "not", "poor", "problem", "problems", "refund", "replace", "replacement",
    "returned", "slow", "stopped", "terrible", "waste", "weak", "worst",
}


def ensure_dirs() -> None:
    TABLEAU_DIR.mkdir(parents=True, exist_ok=True)


def load_amazon() -> pd.DataFrame:
    processed = PROCESSED_DIR / "amazon_products_cleaned.csv"
    if processed.exists():
        return pd.read_csv(processed, dtype={"product_id": "string"})
    raw = pd.read_csv(RAW_DIR / "amazon.csv", dtype={"product_id": "string"})
    raw["discounted_price_num"] = pd.to_numeric(
        raw["discounted_price"].astype("string").str.replace(r"[^\d.]", "", regex=True),
        errors="coerce",
    )
    raw["actual_price_num"] = pd.to_numeric(
        raw["actual_price"].astype("string").str.replace(r"[^\d.]", "", regex=True),
        errors="coerce",
    )
    raw["discount_percentage_num"] = pd.to_numeric(
        raw["discount_percentage"].astype("string").str.replace("%", "", regex=False),
        errors="coerce",
    )
    raw["rating_num"] = pd.to_numeric(raw["rating"], errors="coerce")
    raw["rating_count_num"] = pd.to_numeric(
        raw["rating_count"].astype("string").str.replace(",", "", regex=False),
        errors="coerce",
    )
    raw["main_category"] = raw["category"].astype("string").str.split("|").str[0]
    raw["sub_category"] = raw["category"].astype("string").str.split("|").str[1]
    raw["review_length_chars"] = raw["review_content"].fillna("").astype(str).str.len()
    raw["estimated_revenue_proxy"] = raw["discounted_price_num"] * raw["rating_count_num"]
    return raw


def load_ratings() -> pd.DataFrame:
    ratings = pd.read_csv(
        RAW_DIR / "ratings_Electronics.csv",
        header=None,
        names=RATING_COLUMNS,
        dtype={
            "user_id": "string",
            "product_id": "string",
            "rating": "float64",
            "timestamp": "int64",
        },
    )
    ratings["date"] = pd.to_datetime(ratings["timestamp"], unit="s")
    ratings["year"] = ratings["date"].dt.year
    ratings["low_rating_flag"] = ratings["rating"].le(2)
    return ratings


def raw_words(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z']{2,}", str(text).lower())
    return [word.strip("'") for word in words]


def tokenize(text: str) -> list[str]:
    words = raw_words(text)
    return [word.strip("'") for word in words if word.strip("'") not in STOPWORDS]


def sentiment_score(text: str) -> tuple[float, int, int]:
    words = raw_words(text)
    if not words:
        return 0.0, 0, 0
    positive = sum(1 for word in words if word in POSITIVE_WORDS)
    negative = sum(1 for word in words if word in NEGATIVE_WORDS)
    score = (positive - negative) / math.sqrt(len(words))
    return score, positive, negative


def sentiment_label(score: float) -> str:
    if score >= 0.15:
        return "positive"
    if score <= -0.15:
        return "negative"
    return "neutral"


def build_product_and_category_analysis(amazon: pd.DataFrame) -> dict:
    amazon = amazon.copy()
    revenue_q75 = amazon["estimated_revenue_proxy"].quantile(0.75)
    discount_q75 = amazon["discount_percentage_num"].quantile(0.75)

    def segment(row: pd.Series) -> str:
        if row["estimated_revenue_proxy"] >= revenue_q75 and row["rating_num"] < 4.0:
            return "high_proxy_revenue_low_rating"
        if row["estimated_revenue_proxy"] >= revenue_q75 and row["rating_num"] >= 4.2:
            return "high_proxy_revenue_high_rating"
        if row["discount_percentage_num"] >= discount_q75 and row["rating_num"] < 4.0:
            return "high_discount_low_rating"
        if row["rating_num"] >= 4.5:
            return "high_satisfaction"
        return "standard_monitoring"

    amazon["opportunity_segment"] = amazon.apply(segment, axis=1)
    amazon["rating_band"] = pd.cut(
        amazon["rating_num"],
        bins=[0, 3, 3.5, 4, 4.5, 5],
        labels=["<=3.0", "3.1-3.5", "3.6-4.0", "4.1-4.5", "4.6-5.0"],
        include_lowest=True,
    )
    amazon["review_length_bucket"] = pd.cut(
        amazon["review_length_chars"],
        bins=[0, 250, 500, 1000, 2000, float("inf")],
        labels=["0-250", "251-500", "501-1000", "1001-2000", "2000+"],
        include_lowest=True,
    )
    amazon.to_csv(TABLEAU_DIR / "product_performance.csv", index=False)

    category = (
        amazon.groupby("main_category", dropna=False)
        .agg(
            product_rows=("product_id", "size"),
            unique_products=("product_id", "nunique"),
            avg_rating=("rating_num", "mean"),
            median_rating=("rating_num", "median"),
            total_rating_count=("rating_count_num", "sum"),
            avg_discount_pct=("discount_percentage_num", "mean"),
            median_discount_pct=("discount_percentage_num", "median"),
            avg_review_length_chars=("review_length_chars", "mean"),
            estimated_revenue_proxy=("estimated_revenue_proxy", "sum"),
            high_proxy_revenue_low_rating_products=(
                "opportunity_segment",
                lambda s: int((s == "high_proxy_revenue_low_rating").sum()),
            ),
        )
        .reset_index()
        .sort_values("estimated_revenue_proxy", ascending=False)
    )
    total_proxy = category["estimated_revenue_proxy"].sum()
    category["estimated_revenue_proxy_share"] = category["estimated_revenue_proxy"] / total_proxy
    category.to_csv(TABLEAU_DIR / "category_performance.csv", index=False)

    rating_distribution = (
        amazon.groupby("rating_band", observed=False)
        .agg(product_rows=("product_id", "size"), total_rating_count=("rating_count_num", "sum"))
        .reset_index()
    )
    rating_distribution.to_csv(TABLEAU_DIR / "amazon_rating_distribution.csv", index=False)

    rating_length = (
        amazon.groupby(["rating_band", "review_length_bucket"], observed=False)
        .agg(
            product_rows=("product_id", "size"),
            avg_review_length_chars=("review_length_chars", "mean"),
            avg_rating_count=("rating_count_num", "mean"),
        )
        .reset_index()
    )
    rating_length.to_csv(TABLEAU_DIR / "review_length_vs_rating.csv", index=False)

    return {
        "category_rows": int(len(category)),
        "product_rows": int(len(amazon)),
        "top_category": str(category.iloc[0]["main_category"]) if len(category) else "",
        "top_category_proxy": float(category.iloc[0]["estimated_revenue_proxy"]) if len(category) else 0.0,
        "high_proxy_low_rating_count": int((amazon["opportunity_segment"] == "high_proxy_revenue_low_rating").sum()),
    }


def build_user_and_time_analysis(ratings: pd.DataFrame) -> dict:
    yearly = (
        ratings.groupby("year")
        .agg(
            rating_count=("rating", "size"),
            unique_users=("user_id", "nunique"),
            unique_products=("product_id", "nunique"),
            avg_rating=("rating", "mean"),
            low_rating_rate=("low_rating_flag", "mean"),
        )
        .reset_index()
        .sort_values("year")
    )
    yearly["rating_count_yoy"] = yearly["rating_count"].pct_change()
    yearly.to_csv(TABLEAU_DIR / "yearly_rating_trend.csv", index=False)

    user_activity = (
        ratings.groupby("user_id")
        .agg(
            rating_count=("rating", "size"),
            avg_rating_given=("rating", "mean"),
            first_rating_date=("date", "min"),
            last_rating_date=("date", "max"),
            unique_products_rated=("product_id", "nunique"),
        )
        .reset_index()
    )
    q99 = user_activity["rating_count"].quantile(0.99)
    user_activity["user_segment"] = user_activity["rating_count"].apply(
        lambda x: "high_activity_user" if x >= q99 else "regular_user"
    )

    top_users = user_activity.sort_values("rating_count", ascending=False).head(5000)
    top_users.to_csv(TABLEAU_DIR / "user_activity_top.csv", index=False)

    bins = [0, 1, 2, 5, 10, 20, 50, 100, float("inf")]
    labels = ["1", "2", "3-5", "6-10", "11-20", "21-50", "51-100", "100+"]
    user_activity["rating_count_bucket"] = pd.cut(
        user_activity["rating_count"],
        bins=bins,
        labels=labels,
        include_lowest=True,
    )
    user_distribution = (
        user_activity.groupby("rating_count_bucket", observed=False)
        .agg(user_count=("user_id", "size"), avg_rating_given=("avg_rating_given", "mean"))
        .reset_index()
    )
    user_distribution["user_share"] = user_distribution["user_count"] / user_distribution["user_count"].sum()
    user_distribution.to_csv(TABLEAU_DIR / "user_activity_distribution.csv", index=False)

    rating_preference = (
        ratings.merge(user_activity[["user_id", "user_segment"]], on="user_id", how="left")
        .groupby(["user_segment", "rating"])
        .agg(rating_count=("rating", "size"))
        .reset_index()
    )
    rating_preference["segment_total"] = rating_preference.groupby("user_segment")["rating_count"].transform("sum")
    rating_preference["rating_share"] = rating_preference["rating_count"] / rating_preference["segment_total"]
    rating_preference.to_csv(TABLEAU_DIR / "user_rating_preference.csv", index=False)

    return {
        "year_min": int(yearly["year"].min()),
        "year_max": int(yearly["year"].max()),
        "peak_year": int(yearly.sort_values("rating_count", ascending=False).iloc[0]["year"]),
        "high_activity_threshold": int(q99),
        "high_activity_users": int((user_activity["user_segment"] == "high_activity_user").sum()),
        "total_users": int(len(user_activity)),
    }


def build_review_analysis(amazon: pd.DataFrame) -> dict:
    amazon = amazon.copy()
    amazon["rating_band"] = pd.cut(
        amazon["rating_num"],
        bins=[0, 3, 3.5, 4, 4.5, 5],
        labels=["<=3.0", "3.1-3.5", "3.6-4.0", "4.1-4.5", "4.6-5.0"],
        include_lowest=True,
    )
    sentiment = amazon["review_content"].fillna("").apply(sentiment_score)
    amazon["sentiment_score"] = [item[0] for item in sentiment]
    amazon["positive_word_count"] = [item[1] for item in sentiment]
    amazon["negative_word_count"] = [item[2] for item in sentiment]
    amazon["sentiment_label"] = amazon["sentiment_score"].map(sentiment_label)

    product_review_sentiment = amazon[
        [
            "product_id",
            "product_name",
            "main_category",
            "rating_num",
            "rating_count_num",
            "review_length_chars",
            "sentiment_score",
            "sentiment_label",
            "positive_word_count",
            "negative_word_count",
        ]
    ].copy()
    product_review_sentiment.to_csv(TABLEAU_DIR / "product_review_sentiment.csv", index=False)

    category_sentiment = (
        amazon.groupby("main_category", dropna=False)
        .agg(
            product_rows=("product_id", "size"),
            avg_rating=("rating_num", "mean"),
            avg_review_length_chars=("review_length_chars", "mean"),
            avg_sentiment_score=("sentiment_score", "mean"),
            positive_share=("sentiment_label", lambda s: float((s == "positive").mean())),
            neutral_share=("sentiment_label", lambda s: float((s == "neutral").mean())),
            negative_share=("sentiment_label", lambda s: float((s == "negative").mean())),
        )
        .reset_index()
        .sort_values("avg_sentiment_score", ascending=False)
    )
    category_sentiment.to_csv(TABLEAU_DIR / "category_sentiment_summary.csv", index=False)

    word_counter: Counter[str] = Counter()
    for text in amazon["review_content"].fillna(""):
        word_counter.update(tokenize(text))
    word_freq = pd.DataFrame(word_counter.most_common(250), columns=["word", "count"])
    word_freq.to_csv(TABLEAU_DIR / "review_keyword_frequency.csv", index=False)

    sentiment_distribution = (
        amazon.groupby(["sentiment_label", "rating_band"], observed=False)
        .agg(product_rows=("product_id", "size"), avg_rating=("rating_num", "mean"))
        .reset_index()
    )
    sentiment_distribution.to_csv(TABLEAU_DIR / "sentiment_rating_distribution.csv", index=False)

    return {
        "positive_products": int((amazon["sentiment_label"] == "positive").sum()),
        "neutral_products": int((amazon["sentiment_label"] == "neutral").sum()),
        "negative_products": int((amazon["sentiment_label"] == "negative").sum()),
        "top_keywords": word_freq.head(15).to_dict(orient="records"),
        "avg_sentiment_score": float(amazon["sentiment_score"].mean()),
    }


def main() -> None:
    ensure_dirs()
    amazon = load_amazon()
    build_product_and_category_analysis(amazon)
    ratings = load_ratings()
    build_user_and_time_analysis(ratings)
    build_review_analysis(amazon)

    print("Week 2 outputs generated.")
    print(f"Tableau-ready files: {TABLEAU_DIR}")


if __name__ == "__main__":
    main()
