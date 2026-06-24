from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
WEEK3_DIR = ROOT / "outputs" / "week3"
WEEK4_DIR = ROOT / "outputs" / "week4"
FIGURE_DIR = ROOT / "reports" / "week4" / "figures"

FONT_PATH = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")
MONO_FONT_PATH = Path("/System/Library/Fonts/Menlo.ttc")

BG = "#F7F4EC"
INK = "#17324D"
MUTED = "#657786"
GRID = "#D9D5CA"
BLUE = "#1F5A7A"
TEAL = "#2A9D8F"
GOLD = "#E9C46A"
ORANGE = "#F4A261"
RED = "#D95D39"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    index = 1 if bold else 0
    return ImageFont.truetype(str(FONT_PATH), size=size, index=index)


def ensure_dirs() -> None:
    WEEK4_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def business_note(topic: str) -> str:
    notes = {
        "Product Quality & Durability": "覆盖产品最多，适合作为质量、耐用性和做工改进的主线。",
        "Charging & Power": "产品量和反馈量较高，重点关注充电、电池、线缆和接口体验。",
        "Compatibility & Usability": "重点优化设备适配说明、连接步骤和易用性。",
        "Price & Value": "关注价格表达、产品价值感和折扣策略。",
        "Delivery & Packaging": "负面占比最高，应优先检查配送、包装破损和退换货体验。",
        "General Experience": "样本较少，作为整体体验的辅助观察项。",
    }
    return notes.get(topic, "结合评分、情感和样本规模持续监控。")


def build_tableau_metrics() -> pd.DataFrame:
    products = pd.read_csv(WEEK3_DIR / "week3_product_sentiment_topics.csv")
    topics = pd.read_csv(WEEK3_DIR / "week3_topic_summary.csv")
    opportunities = pd.read_csv(WEEK3_DIR / "week3_negative_review_opportunities.csv")
    evaluation = pd.read_csv(WEEK3_DIR / "week3_recommendation_evaluation.csv").iloc[0]

    rows: list[dict] = []

    sentiment_order = ["positive", "neutral", "negative"]
    sentiment_counts = products["sentiment_label"].value_counts()
    for order, label in enumerate(sentiment_order, start=1):
        count = int(sentiment_counts.get(label, 0))
        rows.append(
            {
                "view_name": "Sentiment Distribution",
                "dimension": label,
                "metric_name": "product_count",
                "metric_value": count,
                "share_value": count / len(products),
                "avg_rating": products.loc[products["sentiment_label"].eq(label), "rating_num"].mean(),
                "avg_sentiment_score": products.loc[
                    products["sentiment_label"].eq(label), "sentiment_score"
                ].mean(),
                "negative_share": None,
                "display_order": order,
                "business_note": "整体情感结构用于判断口碑基线，并结合低评分产品做重点排查。",
            }
        )

    total_products = int(topics["product_count"].sum())
    for order, row in enumerate(topics.itertuples(index=False), start=1):
        rows.append(
            {
                "view_name": "Topic Performance",
                "dimension": row.dominant_topic,
                "metric_name": "product_count",
                "metric_value": int(row.product_count),
                "share_value": row.product_count / total_products,
                "avg_rating": row.avg_rating,
                "avg_sentiment_score": row.avg_sentiment_score,
                "negative_share": row.negative_share,
                "display_order": order,
                "business_note": business_note(row.dominant_topic),
            }
        )

    recommendation_rows = [
        ("Hit Rate@5", float(evaluation["hit_rate_at_5"]), 1),
        ("Hit Rate@10", float(evaluation["hit_rate_at_10"]), 2),
    ]
    for label, value, order in recommendation_rows:
        rows.append(
            {
                "view_name": "Recommendation Evaluation",
                "dimension": label,
                "metric_name": "hit_rate",
                "metric_value": value,
                "share_value": value,
                "avg_rating": None,
                "avg_sentiment_score": None,
                "negative_share": None,
                "display_order": order,
                "business_note": "用于衡量真实留出商品是否出现在 Top-N 推荐列表中。",
            }
        )

    for view_name, field in [
        ("Opportunity by Topic", "dominant_topic"),
        ("Opportunity by Category", "main_category"),
    ]:
        counts = opportunities[field].fillna("Unknown").value_counts()
        for order, (label, count) in enumerate(counts.items(), start=1):
            rows.append(
                {
                    "view_name": view_name,
                    "dimension": label,
                    "metric_name": "opportunity_count",
                    "metric_value": int(count),
                    "share_value": count / len(opportunities),
                    "avg_rating": opportunities.loc[opportunities[field].fillna("Unknown").eq(label), "rating_num"].mean(),
                    "avg_sentiment_score": opportunities.loc[
                        opportunities[field].fillna("Unknown").eq(label), "sentiment_score"
                    ].mean(),
                    "negative_share": None,
                    "display_order": order,
                    "business_note": "用于确定产品优化和运营排查的优先范围。",
                }
            )

    kpis = [
        ("Products Analyzed", len(products), 1, "第三周完成情感与主题分析的产品总数。"),
        ("Improvement Opportunities", len(opportunities), 2, "低评分或负面情感产品机会数量。"),
        (
            "Products with Recommendations",
            int(evaluation["products_with_recommendations"]),
            3,
            "已生成相似商品推荐的源商品数量。",
        ),
        (
            "Recommendation Rows",
            int(evaluation["recommendation_rows"]),
            4,
            "推荐结果表中的商品配对数量。",
        ),
    ]
    for label, value, order, note in kpis:
        rows.append(
            {
                "view_name": "KPI",
                "dimension": label,
                "metric_name": "kpi_value",
                "metric_value": value,
                "share_value": None,
                "avg_rating": None,
                "avg_sentiment_score": None,
                "negative_share": None,
                "display_order": order,
                "business_note": note,
            }
        )

    metrics = pd.DataFrame(rows)
    metrics.to_csv(WEEK4_DIR / "week4_tableau_visual_metrics.csv", index=False)
    return metrics


def canvas(title: str, subtitle: str, height: int = 900) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (1600, height), BG)
    draw = ImageDraw.Draw(image)
    draw.text((90, 58), title, fill=INK, font=font(46, bold=True))
    draw.text((90, 120), subtitle, fill=MUTED, font=font(24))
    draw.line((90, 168, 1510, 168), fill=GRID, width=2)
    return image, draw


def save_sentiment_chart(metrics: pd.DataFrame) -> None:
    data = metrics[metrics["view_name"].eq("Sentiment Distribution")].sort_values("display_order")
    image, draw = canvas("评论情感分布", "产品级评论情感结果，n = 1,465", height=760)
    left, top, width, bar_height = 110, 260, 1380, 105
    colors = {"positive": TEAL, "neutral": GOLD, "negative": RED}
    x = left
    for row in data.itertuples(index=False):
        segment = width * float(row.share_value)
        draw.rounded_rectangle((x, top, x + segment, top + bar_height), radius=12, fill=colors[row.dimension])
        x += segment
    legend_y = 445
    for idx, row in enumerate(data.itertuples(index=False)):
        x0 = 130 + idx * 470
        draw.rounded_rectangle((x0, legend_y, x0 + 28, legend_y + 28), radius=5, fill=colors[row.dimension])
        draw.text((x0 + 42, legend_y - 4), row.dimension.title(), fill=INK, font=font(25, bold=True))
        draw.text(
            (x0 + 42, legend_y + 36),
            f"{int(row.metric_value):,} products  |  {row.share_value:.1%}",
            fill=MUTED,
            font=font(23),
        )
    draw.text((110, 620), "主要发现：整体评论明显偏正向，但仍需结合低评分高反馈产品定位具体问题。", fill=INK, font=font(25))
    image.save(FIGURE_DIR / "week4_sentiment_distribution.png")


def save_topic_chart(metrics: pd.DataFrame) -> None:
    data = metrics[metrics["view_name"].eq("Topic Performance")].sort_values("metric_value")
    image, draw = canvas("评论主题规模与风险", "柱长表示产品数量；右侧标注负面占比", height=980)
    left, right, top, bottom = 520, 1120, 230, 870
    max_value = float(data["metric_value"].max())
    row_height = (bottom - top) / len(data)
    for idx, row in enumerate(data.itertuples(index=False)):
        y = top + idx * row_height + 13
        bar_width = (right - left) * float(row.metric_value) / max_value
        risk_color = RED if float(row.negative_share) >= 0.05 else BLUE
        draw.text((90, y + 9), row.dimension, fill=INK, font=font(22))
        draw.rounded_rectangle((left, y, left + bar_width, y + 54), radius=8, fill=risk_color)
        draw.text((1145, y + 8), f"{int(row.metric_value):,}", fill=INK, font=font(22, bold=True))
        draw.text((1290, y + 8), f"负面 {float(row.negative_share):.1%}", fill=RED if risk_color == RED else MUTED, font=font(21))
    image.save(FIGURE_DIR / "week4_topic_performance.png")


def save_topic_risk_matrix(metrics: pd.DataFrame) -> None:
    data = metrics[metrics["view_name"].eq("Topic Performance")].copy()
    image, draw = canvas("主题评分与负面占比", "气泡大小表示产品数量；越靠左上越需要优先关注", height=980)
    left, right, top, bottom = 180, 1460, 230, 820
    x_min, x_max = 4.04, 4.14
    y_min, y_max = 0.0, max(0.13, float(data["negative_share"].max()) * 1.1)
    for i in range(6):
        y = top + (bottom - top) * i / 5
        draw.line((left, y, right, y), fill=GRID, width=2)
        value = y_max - (y_max - y_min) * i / 5
        draw.text((75, y - 14), f"{value:.0%}", fill=MUTED, font=font(19))
    for i in range(6):
        x = left + (right - left) * i / 5
        draw.line((x, top, x, bottom), fill=GRID, width=2)
        value = x_min + (x_max - x_min) * i / 5
        draw.text((x - 24, bottom + 18), f"{value:.2f}", fill=MUTED, font=font(19))
    draw.text((650, 900), "Average Rating", fill=INK, font=font(23, bold=True))
    draw.text((40, 190), "Negative Share", fill=INK, font=font(23, bold=True))
    label_offsets = {
        "Delivery & Packaging": (30, -15),
        "Product Quality & Durability": (82, -6),
        "Price & Value": (30, -6),
        "General Experience": (26, -30),
        "Charging & Power": (-190, -55),
        "Compatibility & Usability": (30, 26),
    }
    for row in data.itertuples(index=False):
        x = left + (float(row.avg_rating) - x_min) / (x_max - x_min) * (right - left)
        y = bottom - (float(row.negative_share) - y_min) / (y_max - y_min) * (bottom - top)
        y = min(y, bottom - 20)
        radius = 16 + math.sqrt(float(row.metric_value)) * 1.5
        color = RED if float(row.negative_share) >= 0.05 else TEAL
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline=INK, width=2)
        short = row.dimension.replace("Product Quality & Durability", "Quality & Durability").replace(
            "Compatibility & Usability", "Compatibility"
        )
        dx, dy = label_offsets.get(row.dimension, (30, -13))
        draw.text((x + dx, y + dy), short, fill=INK, font=font(18, bold=True))
    image.save(FIGURE_DIR / "week4_topic_risk_matrix.png")


def save_recommendation_chart(metrics: pd.DataFrame) -> None:
    data = metrics[metrics["view_name"].eq("Recommendation Evaluation")].sort_values("display_order")
    image, draw = canvas("推荐模型评估", "Hit Rate 表示留出商品进入 Top-N 推荐列表的用户比例", height=820)
    base_y, max_height = 650, 360
    positions = [520, 930]
    for x, row, color in zip(positions, data.itertuples(index=False), [BLUE, TEAL]):
        height = max_height * float(row.metric_value) / 0.10
        draw.rounded_rectangle((x, base_y - height, x + 230, base_y), radius=12, fill=color)
        draw.text((x + 32, base_y - height - 58), f"{float(row.metric_value):.2%}", fill=INK, font=font(38, bold=True))
        draw.text((x + 43, base_y + 24), row.dimension, fill=INK, font=font(28, bold=True))
    draw.text((100, 235), "5,000", fill=INK, font=font(40, bold=True))
    draw.text((100, 290), "evaluated users", fill=MUTED, font=font(22))
    draw.text((100, 390), "4,862", fill=INK, font=font(40, bold=True))
    draw.text((100, 445), "recommendation rows", fill=MUTED, font=font(22))
    image.save(FIGURE_DIR / "week4_recommendation_evaluation.png")


def save_opportunity_chart(metrics: pd.DataFrame) -> None:
    data = metrics[metrics["view_name"].eq("Opportunity by Category")].sort_values("metric_value")
    image, draw = canvas("重点优化产品的类目分布", "100 个低评分或负面反馈产品机会", height=900)
    left, right, top, bottom = 520, 1450, 240, 790
    max_value = float(data["metric_value"].max())
    row_height = (bottom - top) / max(1, len(data))
    for idx, row in enumerate(data.itertuples(index=False)):
        y = top + idx * row_height + 10
        bar_width = (right - left) * float(row.metric_value) / max_value
        draw.text((110, y + 10), row.dimension, fill=INK, font=font(23))
        draw.rounded_rectangle((left, y, left + bar_width, y + 58), radius=8, fill=ORANGE)
        draw.text((left + bar_width + 16, y + 10), f"{int(row.metric_value):,}", fill=INK, font=font(23, bold=True))
    image.save(FIGURE_DIR / "week4_opportunity_by_category.png")


def save_category_overview_chart() -> None:
    data = pd.read_csv(ROOT / "outputs" / "tableau" / "category_performance.csv").copy()
    data = data.sort_values("estimated_revenue_proxy_share").tail(5)
    image, draw = canvas("类目商业关注权重", "代理指标 = 折扣价 × 评分数量，不代表真实销售额", height=900)
    left, right, top, bottom = 520, 1420, 250, 790
    max_value = float(data["estimated_revenue_proxy_share"].max())
    row_height = (bottom - top) / len(data)
    for idx, row in enumerate(data.itertuples(index=False)):
        y = top + idx * row_height + 12
        width = (right - left) * float(row.estimated_revenue_proxy_share) / max_value
        color = TEAL if row.main_category == "Electronics" else BLUE
        draw.text((100, y + 10), row.main_category, fill=INK, font=font(22))
        draw.rounded_rectangle((left, y, left + width, y + 58), radius=8, fill=color)
        draw.text((left + width + 16, y + 10), f"{row.estimated_revenue_proxy_share:.1%}", fill=INK, font=font(22, bold=True))
    image.save(FIGURE_DIR / "final_category_commercial_weight.png")


def save_user_activity_chart() -> None:
    data = pd.read_csv(ROOT / "outputs" / "tableau" / "user_activity_distribution.csv")
    image, draw = canvas("用户活跃度分布", "约 68.6% 的用户只留下 1 次评分", height=900)
    left, right, top, bottom = 300, 1470, 250, 780
    max_value = float(data["user_share"].max())
    step = (right - left) / len(data)
    for idx, row in enumerate(data.itertuples(index=False)):
        x = left + idx * step + 20
        height = (bottom - top) * float(row.user_share) / max_value
        color = ORANGE if row.rating_count_bucket == "1" else BLUE
        draw.rounded_rectangle((x, bottom - height, x + 80, bottom), radius=7, fill=color)
        draw.text((x + 8, bottom + 18), str(row.rating_count_bucket), fill=INK, font=font(18))
        draw.text((x - 4, bottom - height - 38), f"{row.user_share:.1%}", fill=INK, font=font(18, bold=True))
    draw.text((670, 850), "Number of Ratings per User", fill=INK, font=font(23, bold=True))
    image.save(FIGURE_DIR / "final_user_activity_distribution.png")


def save_yearly_trend_chart() -> None:
    data = pd.read_csv(ROOT / "outputs" / "tableau" / "yearly_rating_trend.csv")
    data = data[data["year"] >= 2004].copy()
    image, draw = canvas("年度评分活动趋势", "评分活动在 2013 年达到峰值，2014 年数据可能不完整", height=900)
    left, right, top, bottom = 180, 1450, 250, 760
    max_value = float(data["rating_count"].max())
    points = []
    for idx, row in enumerate(data.itertuples(index=False)):
        x = left + idx * (right - left) / (len(data) - 1)
        y = bottom - float(row.rating_count) / max_value * (bottom - top)
        points.append((x, y, row))
    for i in range(6):
        y = top + i * (bottom - top) / 5
        draw.line((left, y, right, y), fill=GRID, width=2)
        value = max_value * (1 - i / 5)
        draw.text((55, y - 12), f"{value / 1_000_000:.1f}M", fill=MUTED, font=font(18))
    draw.line([(x, y) for x, y, _ in points], fill=TEAL, width=7)
    for x, y, row in points:
        draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=TEAL, outline=INK, width=2)
        if int(row.year) in {2004, 2007, 2010, 2013, 2014}:
            draw.text((x - 24, bottom + 22), str(int(row.year)), fill=INK, font=font(18))
    peak = max(points, key=lambda item: item[2].rating_count)
    draw.text((peak[0] - 75, peak[1] - 50), f"2013 peak\n{int(peak[2].rating_count):,}", fill=INK, font=font(20, bold=True))
    image.save(FIGURE_DIR / "final_yearly_rating_trend.png")


def main() -> None:
    ensure_dirs()
    metrics = build_tableau_metrics()
    save_sentiment_chart(metrics)
    save_topic_chart(metrics)
    save_topic_risk_matrix(metrics)
    save_recommendation_chart(metrics)
    save_opportunity_chart(metrics)
    save_category_overview_chart()
    save_user_activity_chart()
    save_yearly_trend_chart()
    print(f"Week 4 Tableau rows: {len(metrics):,}")
    print(f"Output CSV: {WEEK4_DIR / 'week4_tableau_visual_metrics.csv'}")
    print(f"Figures: {FIGURE_DIR}")


if __name__ == "__main__":
    main()
