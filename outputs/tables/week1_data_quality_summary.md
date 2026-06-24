# Week 1 Data Quality Summary

## Amazon Product/Review Data

- Rows: 1,465
- Columns after cleaning: 27
- Unique products: 1,351
- Duplicate product ID rows: 114
- Average rating: 4.10
- Rating range: 2.0 to 5.0
- Missing cleaned rating count values: 2

## Electronics Ratings Data

- Rows: 7,824,482
- Unique users: 4,201,696
- Unique products: 476,002
- Duplicate user-product pairs: 0
- Date range: 1998-12-04 to 2014-07-23
- User-item matrix density: 0.00000391
- Direct product overlap with `amazon.csv`: 6

## Key Interpretation

The two datasets are useful for complementary analysis but should not be treated as a fully joinable transaction table. `amazon.csv` is strongest for product, price, category, and review-text analysis. `ratings_Electronics.csv` is strongest for user activity, product rating aggregation, and recommendation modeling.
