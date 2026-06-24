from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
WEEK3_DIR = ROOT / "outputs" / "week3"

RATING_COLUMNS = ["user_id", "product_id", "rating", "timestamp"]

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "can", "for",
    "from", "had", "has", "have", "he", "her", "his", "i", "if", "in", "is",
    "it", "its", "me", "my", "of", "on", "or", "our", "so", "that", "the",
    "their", "them", "there", "this", "to", "too", "very", "was", "we", "were",
    "with", "you", "your", "product", "one", "will", "would", "also", "using",
    "use", "used", "get", "got", "really", "much", "amazon", "buy", "bought",
    "all", "after", "only", "which", "it's", "they", "than", "then", "these",
    "those", "what", "when", "where", "who", "why", "how", "https", "media",
    "images", "webp",
}

POSITIVE_WORDS = {
    "amazing", "awesome", "best", "better", "comfortable", "durable", "easy",
    "excellent", "fast", "fine", "fit", "good", "great", "happy", "impressive",
    "love", "loved", "nice", "perfect", "premium", "quality", "recommend",
    "satisfied", "smooth", "strong", "super", "useful", "value", "well",
    "working", "worth", "sturdy", "reliable", "quick", "clear", "powerful",
}

NEGATIVE_WORDS = {
    "bad", "broken", "cheap", "complaint", "complaints", "damage", "damaged",
    "defective", "disappointed", "issue", "issues", "low", "negative", "noise",
    "poor", "problem", "problems", "refund", "replace", "replacement", "returned",
    "slow", "stopped", "terrible", "waste", "weak", "worst", "fail", "failed",
    "failure", "heat", "heating", "loose", "delay", "delayed",
}

NEGATIONS = {"not", "no", "never", "n't", "without"}

TOPIC_KEYWORDS = {
    "Charging & Power": {
        "charging", "charge", "charger", "cable", "power", "battery", "fast",
        "adapter", "usb", "type", "lightning", "port", "watt",
    },
    "Product Quality & Durability": {
        "quality", "durable", "sturdy", "strong", "broken", "damage", "damaged",
        "defective", "material", "build", "long", "lasting", "working", "stopped",
    },
    "Price & Value": {
        "price", "value", "money", "worth", "cost", "cheap", "affordable",
        "expensive", "budget", "deal",
    },
    "Compatibility & Usability": {
        "phone", "device", "compatible", "easy", "use", "fit", "works", "working",
        "laptop", "mobile", "iphone", "android", "connect", "connection",
    },
    "Delivery & Packaging": {
        "delivery", "delivered", "package", "packaging", "box", "received",
        "return", "returned", "replacement", "refund",
    },
}


def ensure_dirs() -> None:
    WEEK3_DIR.mkdir(parents=True, exist_ok=True)


def load_amazon() -> pd.DataFrame:
    path = PROCESSED_DIR / "amazon_products_cleaned.csv"
    if path.exists():
        return pd.read_csv(path, dtype={"product_id": "string"})
    return pd.read_csv(RAW_DIR / "amazon.csv", dtype={"product_id": "string"})


def raw_words(text: str) -> list[str]:
    return [w.strip("'") for w in re.findall(r"[a-zA-Z][a-zA-Z']{2,}", str(text).lower())]


def tokenize(text: str) -> list[str]:
    return [word for word in raw_words(text) if word not in STOPWORDS]


def enhanced_sentiment(text: str) -> dict[str, float | int | str]:
    words = raw_words(text)
    if not words:
        return {
            "sentiment_score": 0.0,
            "positive_word_count": 0,
            "negative_word_count": 0,
            "sentiment_label": "neutral",
            "sentiment_confidence": 0.0,
        }

    positive = 0
    negative = 0
    for i, word in enumerate(words):
        previous = set(words[max(0, i - 3) : i])
        negated = bool(previous & NEGATIONS)
        if word in POSITIVE_WORDS:
            if negated:
                negative += 1
            else:
                positive += 1
        elif word in NEGATIVE_WORDS:
            if negated:
                positive += 1
            else:
                negative += 1

    raw_score = positive - negative
    norm_score = raw_score / math.sqrt(len(words))
    confidence = (positive + negative) / max(1, len(words))
    if norm_score >= 0.12:
        label = "positive"
    elif norm_score <= -0.12:
        label = "negative"
    else:
        label = "neutral"
    return {
        "sentiment_score": norm_score,
        "positive_word_count": positive,
        "negative_word_count": negative,
        "sentiment_label": label,
        "sentiment_confidence": confidence,
    }


def assign_topic(tokens: list[str]) -> tuple[str, int, str]:
    token_counts = Counter(tokens)
    scores: dict[str, int] = {}
    matched_words: dict[str, list[str]] = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        matches = [word for word in token_counts if word in keywords]
        score = sum(token_counts[word] for word in matches)
        scores[topic] = score
        matched_words[topic] = sorted(matches, key=lambda w: token_counts[w], reverse=True)[:8]

    best_topic, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score == 0:
        return "General Experience", 0, ""
    return best_topic, int(best_score), ", ".join(matched_words[best_topic])


def tfidf_keywords(
    docs: list[list[str]],
    top_n: int = 12,
    allowed_words: set[str] | None = None,
) -> pd.DataFrame:
    doc_freq: Counter[str] = Counter()
    for tokens in docs:
        doc_freq.update(set(tokens))
    total_docs = len(docs)
    rows = []
    global_counts = Counter()
    for tokens in docs:
        if allowed_words is not None:
            tokens = [token for token in tokens if token in allowed_words]
        global_counts.update(tokens)
    for word, count in global_counts.items():
        idf = math.log((1 + total_docs) / (1 + doc_freq[word])) + 1
        rows.append({"word": word, "count": count, "doc_freq": doc_freq[word], "tfidf_score": count * idf})
    return pd.DataFrame(rows).sort_values("tfidf_score", ascending=False).head(top_n)


def build_review_models(amazon: pd.DataFrame) -> dict:
    amazon = amazon.copy()
    amazon["review_text"] = amazon["review_content"].fillna("").astype(str)
    amazon["tokens"] = amazon["review_text"].map(tokenize)
    sentiment_df = pd.DataFrame(amazon["review_text"].map(enhanced_sentiment).tolist())
    amazon = pd.concat([amazon, sentiment_df], axis=1)

    topic_rows = []
    for _, row in amazon.iterrows():
        topic, topic_score, matched_words = assign_topic(row["tokens"])
        topic_rows.append(
            {
                "product_id": row["product_id"],
                "product_name": row.get("product_name", ""),
                "main_category": row.get("main_category", ""),
                "rating_num": row.get("rating_num", np.nan),
                "rating_count_num": row.get("rating_count_num", np.nan),
                "sentiment_score": row["sentiment_score"],
                "sentiment_label": row["sentiment_label"],
                "sentiment_confidence": row["sentiment_confidence"],
                "dominant_topic": topic,
                "topic_score": topic_score,
                "matched_topic_words": matched_words,
                "review_length_chars": row.get("review_length_chars", len(row["review_text"])),
            }
        )
    topic_product = pd.DataFrame(topic_rows)
    topic_product.to_csv(WEEK3_DIR / "week3_product_sentiment_topics.csv", index=False)

    topic_summary = (
        topic_product.groupby("dominant_topic")
        .agg(
            product_count=("product_id", "size"),
            avg_rating=("rating_num", "mean"),
            avg_rating_count=("rating_count_num", "mean"),
            avg_sentiment_score=("sentiment_score", "mean"),
            negative_share=("sentiment_label", lambda s: float((s == "negative").mean())),
        )
        .reset_index()
        .sort_values(["product_count", "negative_share"], ascending=[False, False])
    )
    topic_summary.to_csv(WEEK3_DIR / "week3_topic_summary.csv", index=False)

    keyword_rows = []
    for topic in topic_summary["dominant_topic"]:
        topic_docs = amazon.loc[topic_product["dominant_topic"].eq(topic), "tokens"].tolist()
        if not topic_docs:
            continue
        allowed_words = TOPIC_KEYWORDS.get(topic)
        keywords = tfidf_keywords(topic_docs, top_n=10, allowed_words=allowed_words)
        keywords["dominant_topic"] = topic
        keyword_rows.append(keywords)
    topic_keywords = pd.concat(keyword_rows, ignore_index=True) if keyword_rows else pd.DataFrame()
    topic_keywords.to_csv(WEEK3_DIR / "week3_topic_keywords.csv", index=False)

    negative_opportunities = (
        topic_product.dropna(subset=["rating_num", "rating_count_num"])
        .query("sentiment_label == 'negative' or rating_num < 4")
        .sort_values(["rating_count_num", "sentiment_score"], ascending=[False, True])
        .head(100)
    )
    negative_opportunities.to_csv(WEEK3_DIR / "week3_negative_review_opportunities.csv", index=False)

    return {
        "product_rows": int(len(topic_product)),
        "topic_count": int(topic_summary["dominant_topic"].nunique()),
        "positive_products": int((topic_product["sentiment_label"] == "positive").sum()),
        "neutral_products": int((topic_product["sentiment_label"] == "neutral").sum()),
        "negative_products": int((topic_product["sentiment_label"] == "negative").sum()),
        "top_topic": str(topic_summary.iloc[0]["dominant_topic"]) if len(topic_summary) else "",
        "negative_opportunity_count": int(len(negative_opportunities)),
    }


def load_ratings() -> pd.DataFrame:
    ratings = pd.read_csv(
        RAW_DIR / "ratings_Electronics.csv",
        header=None,
        names=RATING_COLUMNS,
        dtype={"user_id": "string", "product_id": "string", "rating": "float64", "timestamp": "int64"},
    )
    return ratings


def build_item_recommendations(ratings: pd.DataFrame) -> dict:
    user_counts = ratings.groupby("user_id").size()
    eligible_users = user_counts[(user_counts >= 2) & (user_counts <= 20)].index
    if len(eligible_users) > 50_000:
        eligible_users = pd.Series(eligible_users).sample(50_000, random_state=42).astype("string")

    filtered = ratings[ratings["user_id"].isin(set(eligible_users))].copy()
    top_products = set(filtered["product_id"].value_counts().head(10_000).index)
    filtered = filtered[filtered["product_id"].isin(top_products)]

    item_user_count: Counter[str] = Counter()
    pair_counts: Counter[tuple[str, str]] = Counter()
    user_histories: dict[str, list[str]] = {}
    for user_id, group in filtered.groupby("user_id", sort=False):
        products = list(dict.fromkeys(group.sort_values("timestamp")["product_id"].tolist()))
        if len(products) < 2:
            continue
        user_histories[str(user_id)] = products
        item_user_count.update(products)
        for a, b in combinations(sorted(products), 2):
            pair_counts[(a, b)] += 1

    sim_map: defaultdict[str, list[tuple[str, float, int]]] = defaultdict(list)
    for (a, b), co_count in pair_counts.items():
        if co_count < 2:
            continue
        denom = item_user_count[a] + item_user_count[b] - co_count
        similarity = co_count / denom if denom else 0.0
        if similarity <= 0:
            continue
        sim_map[a].append((b, similarity, co_count))
        sim_map[b].append((a, similarity, co_count))

    recommendation_rows = []
    for product_id, recs in sim_map.items():
        for rank, (recommended_product_id, similarity, co_count) in enumerate(
            sorted(recs, key=lambda item: (item[1], item[2]), reverse=True)[:10],
            start=1,
        ):
            recommendation_rows.append(
                {
                    "product_id": product_id,
                    "recommended_product_id": recommended_product_id,
                    "rank": rank,
                    "item_similarity": similarity,
                    "co_rating_user_count": co_count,
                    "source_product_user_count": item_user_count[product_id],
                    "recommended_product_user_count": item_user_count[recommended_product_id],
                }
            )
    recommendations = pd.DataFrame(recommendation_rows)
    recommendations.to_csv(WEEK3_DIR / "week3_item_recommendations.csv", index=False)

    popular_products = [item for item, _ in item_user_count.most_common(50)]
    eval_users = list(user_histories.keys())[:5000]
    hits_at_5 = 0
    hits_at_10 = 0
    evaluated = 0
    for user_id in eval_users:
        products = user_histories[user_id]
        if len(products) < 2:
            continue
        history = products[:-1]
        heldout = products[-1]
        scores: defaultdict[str, float] = defaultdict(float)
        for item in history:
            for rec_item, similarity, _ in sim_map.get(item, [])[:20]:
                if rec_item not in history:
                    scores[rec_item] += similarity
        if not scores:
            for product in popular_products:
                if product not in history:
                    scores[product] += 0.0001
        ranked = [item for item, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]]
        if not ranked:
            continue
        evaluated += 1
        hits_at_5 += int(heldout in ranked[:5])
        hits_at_10 += int(heldout in ranked[:10])

    eval_summary = pd.DataFrame(
        [
            {
                "evaluated_users": evaluated,
                "hit_rate_at_5": hits_at_5 / evaluated if evaluated else 0.0,
                "hit_rate_at_10": hits_at_10 / evaluated if evaluated else 0.0,
                "eligible_users_sampled": int(len(eligible_users)),
                "filtered_interactions": int(len(filtered)),
                "products_with_recommendations": int(recommendations["product_id"].nunique()) if len(recommendations) else 0,
                "recommendation_rows": int(len(recommendations)),
            }
        ]
    )
    eval_summary.to_csv(WEEK3_DIR / "week3_recommendation_evaluation.csv", index=False)

    return eval_summary.iloc[0].to_dict()


def main() -> None:
    ensure_dirs()
    amazon = load_amazon()
    review_summary = build_review_models(amazon)
    ratings = load_ratings()
    rec_summary = build_item_recommendations(ratings)
    print("Week 3 outputs generated.")
    print(f"Review products analyzed: {review_summary['product_rows']:,}")
    print(f"Recommendation rows: {int(rec_summary['recommendation_rows']):,}")
    print(f"Hit rate @10: {rec_summary['hit_rate_at_10']:.4f}")


if __name__ == "__main__":
    main()
