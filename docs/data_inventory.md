# Data Inventory and Initial Observations

## Files Checked

| File | Description | Current Location | Notes |
| --- | --- | --- | --- |
| Project brief PDF | Original project requirement | `intern项目/基于Amazon电商真实数据集：Amazon Product Reviews & Amazon Sales  Dataset 的商业化数据分析.pdf` | Defines 4-week project stages |
| Amazon product/review table | Product metadata, price, rating, review content | `data/raw/amazon.csv` | 1,465 rows, 16 columns |
| Electronics ratings table | User-product-rating-time records | `data/raw/ratings_Electronics.csv` | 7,824,482 rows, 4 columns |
| Initial notebook | Early data loading and checks | `files/file/dataprocess.ipynb` | Currently contains basic loading, display, missing value, shape, and info checks |
| Week 1 processing script | Reusable cleaning and summary generation | `src/data/build_week1_outputs.py` | Generates processed datasets and summary tables |

## `amazon.csv`

Shape:

- Rows: 1,465
- Columns: 16
- Unique products: 1,351
- Duplicate `product_id` count: 114

Columns:

- `product_id`
- `product_name`
- `category`
- `discounted_price`
- `actual_price`
- `discount_percentage`
- `rating`
- `rating_count`
- `about_product`
- `user_id`
- `user_name`
- `review_id`
- `review_title`
- `review_content`
- `img_link`
- `product_link`

Initial observations:

- `rating_count` has 2 missing values.
- Price fields contain currency symbols and need numeric cleaning.
- Discount percentage contains `%` and needs numeric conversion.
- Category is a hierarchical string separated by `|`.
- Some fields such as `user_id`, `user_name`, `review_id`, `review_title`, and `review_content` contain comma-separated values, meaning one row may summarize multiple reviews.

## `ratings_Electronics.csv`

Shape:

- Rows: 7,824,482
- Columns: 4
- Unique users: 4,201,696
- Unique products: 476,002
- Duplicate user-product pairs: 0
- Date range: 1998-12-04 to 2014-07-23

Correct column interpretation:

- `user_id`
- `product_id`
- `rating`
- `timestamp`

Important note:

The file appears to have no header row. If loaded with default `pd.read_csv()`, the first data row is incorrectly treated as the header. It should be loaded with:

```python
ratings = pd.read_csv(
    "data/raw/ratings_Electronics.csv",
    header=None,
    names=["user_id", "product_id", "rating", "timestamp"],
    dtype={"user_id": "string", "product_id": "string"}
)
```

The ID fields should be read as strings. Some product IDs have leading zeroes, and loading them as numbers would corrupt the identifier.

Rating distribution:

| Rating | Count |
| --- | ---: |
| 1.0 | 901,765 |
| 2.0 | 456,322 |
| 3.0 | 633,073 |
| 4.0 | 1,485,781 |
| 5.0 | 4,347,541 |

## Join Feasibility

Direct overlap between `amazon.csv.product_id` and `ratings_Electronics.csv.product_id` is currently very limited:

- Unique products in `amazon.csv`: 1,351
- Unique products in `ratings_Electronics.csv`: 476,002
- Direct product ID overlap: 6

This suggests that the two local datasets should not be treated as a fully joinable sales-review pair without further validation.

Recommended approach:

- Use `amazon.csv` for product metadata, pricing, category, rating, and review text analysis.
- Use `ratings_Electronics.csv` for user-product interaction, rating distribution, user activity, and recommendation modeling.
- Only use the small direct overlap as a validation sample, not as the main analysis table.

## Immediate Cleaning Needs

- Convert `discounted_price` and `actual_price` to numeric values. Completed in `data/processed/amazon_products_cleaned.csv`.
- Convert `discount_percentage` to numeric percentage. Completed in `data/processed/amazon_products_cleaned.csv`.
- Convert `rating` to numeric and handle abnormal values. Completed in `data/processed/amazon_products_cleaned.csv`.
- Convert `rating_count` to numeric by removing commas. Completed in `data/processed/amazon_products_cleaned.csv`.
- Split `category` into category levels. Completed for `main_category` and `sub_category`.
- Convert Unix `timestamp` in ratings data to date. Completed in the 100k cleaned sample and all generated ratings summary tables.
- Decide whether comma-separated review fields in `amazon.csv` should be exploded into review-level rows.

## Generated Week 1 Outputs

- `data/processed/amazon_products_cleaned.csv`
- `data/processed/ratings_electronics_cleaned_sample_100k.csv`
- `outputs/tables/amazon_category_summary.csv`
- `outputs/tables/amazon_top_products_by_proxy_revenue.csv`
- `outputs/tables/amazon_low_rating_high_feedback_products.csv`
- `outputs/tables/ratings_product_summary.csv`
- `outputs/tables/ratings_top_users_by_activity.csv`
- `outputs/tables/ratings_yearly_summary.csv`
- `outputs/tables/week1_data_quality_summary.md`
- `outputs/tables/week1_data_quality_summary.json`
