# Candidate Business Metrics

## Principle

The goal is not to calculate every possible metric. The goal is to select metrics that can support a coherent business story and can be calculated or reasonably approximated from the available data.

Each metric should answer four questions:

- What business question does it support?
- Which field is needed?
- Can the current dataset support it directly?
- Is it a core metric or only a supporting metric?

## Product and Sales Proxy Metrics

| Metric | Meaning | Possible Formula | Data Support | Notes |
| --- | --- | --- | --- | --- |
| Product count | Number of unique products | `nunique(product_id)` | Direct | Basic scale metric |
| Review count | Product popularity / feedback volume | `rating_count` or count of ratings | Direct | Available in `amazon.csv` and can also be aggregated from ratings data |
| Average rating | Product reputation | average of `rating` | Direct | Useful for product quality comparison |
| Low-rating rate | Product risk | share of ratings <= 2 | Direct in ratings data; approximate in review data | Strong for identifying products needing improvement |
| Discount rate | Promotion intensity | `discount_percentage` | Direct after cleaning | Useful for price and promotion analysis |
| Estimated GMV proxy | Approximate product commercial weight | cleaned price * rating_count | Proxy only | Not true GMV unless real order quantity exists |

## User Metrics

| Metric | Meaning | Possible Formula | Data Support | Notes |
| --- | --- | --- | --- | --- |
| Active user count | User base scale | `nunique(user_id)` | Direct | Strong in ratings dataset |
| User rating count | User activity level | count ratings by user | Direct | Can identify high-frequency users |
| High-frequency user | Active user segment | users in top percentile by rating count | Direct | Threshold can be top 10% or top 20% |
| Repeat interaction proxy | User repeatedly interacts with products | user has multiple product ratings | Direct | Not true repeat purchase unless transaction data exists |

## Review and Content Metrics

| Metric | Meaning | Possible Formula | Data Support | Notes |
| --- | --- | --- | --- | --- |
| Review text length | User expression intensity | word count or character count | Direct in `amazon.csv` | Useful for comparing positive and negative reviews |
| Review title/content keywords | User concerns | keyword frequency / TF-IDF | Direct | Can support later topic modeling |
| Sentiment score | Positive or negative review tone | TextBlob / VADER / other NLP model | Derived | Better for Week 3 |
| Topic themes | Main user concerns | LDA or clustering | Derived | Better for Week 3 |

## Recommendation Metrics

| Metric | Meaning | Possible Formula | Data Support | Notes |
| --- | --- | --- | --- | --- |
| User-item rating matrix density | Sparsity of recommendation data | ratings / users / items | Direct | Important for model feasibility |
| Item similarity | Similar product recommendation | item-based collaborative filtering | Derived | Strong use case for `ratings_Electronics.csv` |
| Model RMSE / MAE | Rating prediction error | Surprise or sklearn evaluation | Derived | Useful if building rating prediction |
| Precision / Recall | Recommendation relevance | top-N evaluation | Derived | More advanced; use if time allows |

## Recommended Week 1 Core Metrics

For Week 1, the first metric set can stay focused:

- Product count.
- Review count or rating count.
- Average rating.
- Low-rating rate.
- Discount rate.
- Active user count.
- User rating count.
- High-frequency user definition.
- Review text length.
- Estimated GMV proxy, only if clearly labeled as a proxy.

## First Generated Metric Tables

The current Week 1 script has already generated the following metric tables:

| Output | Main Metrics | Purpose |
| --- | --- | --- |
| `outputs/tables/amazon_category_summary.csv` | product rows, unique products, average rating, total rating count, median discount, estimated revenue proxy | Category-level product and commercial proxy overview |
| `outputs/tables/amazon_top_products_by_proxy_revenue.csv` | price, rating, rating count, estimated revenue proxy | Identify commercially important products for later product analysis |
| `outputs/tables/amazon_low_rating_high_feedback_products.csv` | rating, rating count, discount | Identify products with enough feedback but weaker reputation |
| `outputs/tables/ratings_product_summary.csv` | rating count, average rating, low-rating rate, first/last rating date | Product-level rating performance from the large ratings dataset |
| `outputs/tables/ratings_top_users_by_activity.csv` | user rating count, average rating given, first/last rating date | Identify high-activity users |
| `outputs/tables/ratings_yearly_summary.csv` | yearly rating count, unique users, unique products, average rating, low-rating rate | Time trend and dataset coverage analysis |

## Metrics to Be Careful With

- True GMV: needs real transaction quantity or order amount. Current data may not support it directly.
- Conversion rate: needs impressions, clicks, carts, or visits. Current data does not appear to support it.
- True repeat purchase rate: needs purchase transactions by user. Ratings can only support repeat interaction proxy.
- ROI: needs cost and campaign data. Current data does not appear to support it.
