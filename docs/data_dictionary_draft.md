# Data Dictionary Draft

## `amazon.csv`

| Field | Meaning | Current Type | Cleaning / Usage Notes |
| --- | --- | --- | --- |
| `product_id` | Product identifier | string | Can be used as product key inside `amazon.csv`; direct overlap with ratings data is limited |
| `product_name` | Product name | string | Useful for product-level interpretation and reporting |
| `category` | Product category path | string | Split by `|` into category levels |
| `discounted_price` | Discounted selling price | string | Remove currency symbol and commas, convert to numeric |
| `actual_price` | Original price | string | Remove currency symbol and commas, convert to numeric |
| `discount_percentage` | Discount percentage | string | Remove `%`, convert to numeric |
| `rating` | Average product rating | string / numeric | Convert to numeric; check abnormal values |
| `rating_count` | Number of ratings or reviews | string / numeric | Remove commas, convert to numeric; has missing values |
| `about_product` | Product description | string | Can support keyword or product feature analysis |
| `user_id` | User IDs associated with reviews | string | Often comma-separated; may need splitting if doing review-level analysis |
| `user_name` | User names associated with reviews | string | Often comma-separated; not recommended as an analysis key |
| `review_id` | Review IDs | string | Often comma-separated; may need splitting if exploding reviews |
| `review_title` | Review titles | string | Text analysis input |
| `review_content` | Review body text | string | Text analysis input for sentiment and topic modeling |
| `img_link` | Product image link | string | Usually not needed for core analytics |
| `product_link` | Product URL | string | Useful for reference, not a core analysis field |

## `ratings_Electronics.csv`

This file should be loaded with no header row.

| Field | Meaning | Current Type | Cleaning / Usage Notes |
| --- | --- | --- | --- |
| `user_id` | User identifier | string | Main key for user activity and recommendation analysis |
| `product_id` | Product identifier | string | Main key for product rating aggregation and recommendation analysis |
| `rating` | User rating for product | float | Values range from 1.0 to 5.0 |
| `timestamp` | Unix timestamp | integer | Convert to datetime for trend analysis |
| `date` | Converted date field | datetime | Derived from `timestamp` |

## Derived Fields to Create

| Field | Source | Purpose |
| --- | --- | --- |
| `discounted_price_num` | `discounted_price` | Numeric price analysis |
| `actual_price_num` | `actual_price` | Numeric price analysis |
| `discount_percentage_num` | `discount_percentage` | Promotion analysis |
| `rating_num` | `rating` | Rating analysis |
| `rating_count_num` | `rating_count` | Product popularity and proxy demand analysis |
| `main_category` | `category` | Category-level aggregation |
| `sub_category` | `category` | More detailed category analysis |
| `review_length` | `review_content` | Review depth and content analysis |
| `rating_date` | `timestamp` | Time-based user rating trend analysis |

## Fields Not Currently Available

The current local data does not appear to directly include:

- True order ID.
- True purchase quantity.
- True transaction amount.
- Page view, impression, click, cart, or conversion events.
- Marketing campaign cost.

Because of this, metrics such as true GMV, conversion rate, true repurchase rate, and ROI should either be avoided or clearly labeled as proxy metrics.
