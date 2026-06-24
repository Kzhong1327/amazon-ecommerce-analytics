from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
TABLES_DIR = ROOT / "outputs" / "tables"

RATING_COLUMNS = ["user_id", "product_id", "rating", "timestamp"]


def clean_money(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype("string").str.replace(r"[^\d.]", "", regex=True),
        errors="coerce",
    )


def clean_percent(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype("string").str.replace("%", "", regex=False),
        errors="coerce",
    )


def clean_count(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype("string").str.replace(",", "", regex=False),
        errors="coerce",
    )


def text_length(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.len()


def count_comma_items(value: object) -> int:
    if pd.isna(value):
        return 0
    text = str(value).strip()
    if not text:
        return 0
    return len([part for part in text.split(",") if part.strip()])


def build_amazon_outputs() -> tuple[pd.DataFrame, dict]:
    amazon_path = RAW_DIR / "amazon.csv"
    amazon = pd.read_csv(amazon_path, dtype={"product_id": "string"})

    cleaned = amazon.copy()
    cleaned["discounted_price_num"] = clean_money(cleaned["discounted_price"])
    cleaned["actual_price_num"] = clean_money(cleaned["actual_price"])
    cleaned["discount_percentage_num"] = clean_percent(cleaned["discount_percentage"])
    cleaned["rating_num"] = pd.to_numeric(cleaned["rating"], errors="coerce")
    cleaned["rating_count_num"] = clean_count(cleaned["rating_count"])
    cleaned["main_category"] = cleaned["category"].astype("string").str.split("|").str[0]
    cleaned["sub_category"] = cleaned["category"].astype("string").str.split("|").str[1]
    cleaned["review_length_chars"] = text_length(cleaned["review_content"])
    cleaned["review_title_count_est"] = cleaned["review_title"].map(count_comma_items)
    cleaned["review_content_count_est"] = cleaned["review_content"].map(count_comma_items)
    cleaned["estimated_revenue_proxy"] = (
        cleaned["discounted_price_num"] * cleaned["rating_count_num"]
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(PROCESSED_DIR / "amazon_products_cleaned.csv", index=False)

    category_summary = (
        cleaned.groupby("main_category", dropna=False)
        .agg(
            product_rows=("product_id", "size"),
            unique_products=("product_id", "nunique"),
            avg_rating=("rating_num", "mean"),
            total_rating_count=("rating_count_num", "sum"),
            median_discount_pct=("discount_percentage_num", "median"),
            estimated_revenue_proxy=("estimated_revenue_proxy", "sum"),
        )
        .reset_index()
        .sort_values("estimated_revenue_proxy", ascending=False)
    )
    category_summary.to_csv(TABLES_DIR / "amazon_category_summary.csv", index=False)

    top_products = (
        cleaned[
            [
                "product_id",
                "product_name",
                "main_category",
                "discounted_price_num",
                "rating_num",
                "rating_count_num",
                "estimated_revenue_proxy",
            ]
        ]
        .sort_values("estimated_revenue_proxy", ascending=False)
        .head(50)
    )
    top_products.to_csv(TABLES_DIR / "amazon_top_products_by_proxy_revenue.csv", index=False)

    low_rating_products = (
        cleaned[
            [
                "product_id",
                "product_name",
                "main_category",
                "rating_num",
                "rating_count_num",
                "discount_percentage_num",
            ]
        ]
        .dropna(subset=["rating_num", "rating_count_num"])
        .query("rating_num < 4 and rating_count_num >= 1000")
        .sort_values(["rating_num", "rating_count_num"], ascending=[True, False])
        .head(50)
    )
    low_rating_products.to_csv(TABLES_DIR / "amazon_low_rating_high_feedback_products.csv", index=False)

    summary = {
        "rows": int(len(cleaned)),
        "columns": int(cleaned.shape[1]),
        "unique_products": int(cleaned["product_id"].nunique()),
        "duplicate_product_id_rows": int(cleaned["product_id"].duplicated().sum()),
        "missing_values": cleaned.isna().sum().astype(int).to_dict(),
        "main_category_counts": cleaned["main_category"].value_counts(dropna=False).astype(int).to_dict(),
        "rating_min": float(cleaned["rating_num"].min()),
        "rating_max": float(cleaned["rating_num"].max()),
        "avg_rating": float(cleaned["rating_num"].mean()),
        "rating_count_missing": int(cleaned["rating_count_num"].isna().sum()),
    }
    return cleaned, summary


def build_ratings_outputs(amazon_product_ids: set[str]) -> dict:
    ratings_path = RAW_DIR / "ratings_Electronics.csv"
    ratings = pd.read_csv(
        ratings_path,
        header=None,
        names=RATING_COLUMNS,
        dtype={"user_id": "string", "product_id": "string", "rating": "float64", "timestamp": "int64"},
    )
    ratings["date"] = pd.to_datetime(ratings["timestamp"], unit="s")
    ratings["year"] = ratings["date"].dt.year
    ratings["low_rating_flag"] = ratings["rating"].le(2)

    ratings.head(100_000).to_csv(
        PROCESSED_DIR / "ratings_electronics_cleaned_sample_100k.csv",
        index=False,
    )

    product_summary = (
        ratings.groupby("product_id")
        .agg(
            rating_count=("rating", "size"),
            avg_rating=("rating", "mean"),
            low_rating_rate=("low_rating_flag", "mean"),
            first_rating_date=("date", "min"),
            last_rating_date=("date", "max"),
        )
        .reset_index()
        .sort_values("rating_count", ascending=False)
    )
    product_summary.to_csv(TABLES_DIR / "ratings_product_summary.csv", index=False)

    user_summary_top = (
        ratings.groupby("user_id")
        .agg(
            rating_count=("rating", "size"),
            avg_rating_given=("rating", "mean"),
            first_rating_date=("date", "min"),
            last_rating_date=("date", "max"),
        )
        .reset_index()
        .sort_values("rating_count", ascending=False)
        .head(1000)
    )
    user_summary_top.to_csv(TABLES_DIR / "ratings_top_users_by_activity.csv", index=False)

    yearly_summary = (
        ratings.groupby("year")
        .agg(
            rating_count=("rating", "size"),
            unique_users=("user_id", "nunique"),
            unique_products=("product_id", "nunique"),
            avg_rating=("rating", "mean"),
            low_rating_rate=("low_rating_flag", "mean"),
        )
        .reset_index()
    )
    yearly_summary.to_csv(TABLES_DIR / "ratings_yearly_summary.csv", index=False)

    overlap = set(ratings["product_id"].unique()) & amazon_product_ids
    summary = {
        "rows": int(len(ratings)),
        "columns": int(ratings.shape[1]),
        "unique_users": int(ratings["user_id"].nunique()),
        "unique_products": int(ratings["product_id"].nunique()),
        "duplicate_user_product_pairs": int(ratings.duplicated(["user_id", "product_id"]).sum()),
        "missing_values": ratings[RATING_COLUMNS].isna().sum().astype(int).to_dict(),
        "rating_distribution": ratings["rating"].value_counts().sort_index().astype(int).to_dict(),
        "date_min": str(ratings["date"].min().date()),
        "date_max": str(ratings["date"].max().date()),
        "amazon_product_overlap_count": int(len(overlap)),
        "amazon_product_overlap_sample": sorted(overlap)[:20],
        "matrix_density": float(len(ratings) / (ratings["user_id"].nunique() * ratings["product_id"].nunique())),
    }
    return summary


def write_quality_summary(amazon_summary: dict, ratings_summary: dict) -> None:
    combined = {
        "amazon_csv": amazon_summary,
        "ratings_Electronics_csv": ratings_summary,
    }
    (TABLES_DIR / "week1_data_quality_summary.json").write_text(
        json.dumps(combined, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = [
        "# Week 1 Data Quality Summary",
        "",
        "## Amazon Product/Review Data",
        "",
        f"- Rows: {amazon_summary['rows']:,}",
        f"- Columns after cleaning: {amazon_summary['columns']:,}",
        f"- Unique products: {amazon_summary['unique_products']:,}",
        f"- Duplicate product ID rows: {amazon_summary['duplicate_product_id_rows']:,}",
        f"- Average rating: {amazon_summary['avg_rating']:.2f}",
        f"- Rating range: {amazon_summary['rating_min']:.1f} to {amazon_summary['rating_max']:.1f}",
        f"- Missing cleaned rating count values: {amazon_summary['rating_count_missing']:,}",
        "",
        "## Electronics Ratings Data",
        "",
        f"- Rows: {ratings_summary['rows']:,}",
        f"- Unique users: {ratings_summary['unique_users']:,}",
        f"- Unique products: {ratings_summary['unique_products']:,}",
        f"- Duplicate user-product pairs: {ratings_summary['duplicate_user_product_pairs']:,}",
        f"- Date range: {ratings_summary['date_min']} to {ratings_summary['date_max']}",
        f"- User-item matrix density: {ratings_summary['matrix_density']:.8f}",
        f"- Direct product overlap with `amazon.csv`: {ratings_summary['amazon_product_overlap_count']:,}",
        "",
        "## Key Interpretation",
        "",
        "The two datasets are useful for complementary analysis but should not be treated as a fully joinable transaction table. "
        "`amazon.csv` is strongest for product, price, category, and review-text analysis. "
        "`ratings_Electronics.csv` is strongest for user activity, product rating aggregation, and recommendation modeling.",
    ]
    (TABLES_DIR / "week1_data_quality_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    amazon_cleaned, amazon_summary = build_amazon_outputs()
    ratings_summary = build_ratings_outputs(set(amazon_cleaned["product_id"].astype(str)))
    write_quality_summary(amazon_summary, ratings_summary)

    print("Week 1 outputs generated.")
    print(f"Amazon rows: {amazon_summary['rows']:,}")
    print(f"Ratings rows: {ratings_summary['rows']:,}")
    print(f"Direct product overlap: {ratings_summary['amazon_product_overlap_count']:,}")


if __name__ == "__main__":
    main()
