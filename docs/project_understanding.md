# Project Understanding

## Overall Understanding

My understanding is that this project is an end-to-end business analytics project based on real Amazon ecommerce datasets. The goal is not only to clean data or draw charts, but to complete a full workflow from data cleaning and integration, metric definition, analysis, modeling, and visualization to final business recommendations.

The project should use Amazon product review data and sales or rating-related data to explore business questions such as user behavior, user concerns, product evaluation, product recommendation, and how these insights can become practical strategies for product optimization, marketing, operations, or supply chain improvement.

## Main Business Directions

At the beginning, I should avoid narrowing the project too early. The first step is to explore the datasets broadly and identify which directions are best supported by the data.

Potential directions include:

- Sales or product performance: identify high-performing categories or products through price, discount, rating count, and rating-related indicators.
- User behavior: identify active users, high-frequency users, and user-product interaction patterns.
- Product evaluation: compare average rating, review count, low-rating risk, and product popularity.
- Review insights: use review content to understand user concerns, pain points, and positive feedback.
- Recommendation: use user-product-rating data to build a simple collaborative filtering or item-based recommendation prototype.

## Important Data Caveat

Based on the current local files, `amazon.csv` and `ratings_Electronics.csv` may not be a perfect product-level join pair.

- `amazon.csv` has 1,465 rows and 1,351 unique products.
- `ratings_Electronics.csv` has 7,824,482 user-product rating records and 476,002 unique products.
- Direct `product_id` overlap between the two files is currently very small.

This means the project should not assume that the two datasets can be fully merged into one complete sales-review table. In Week 1, I should document this limitation and decide whether to:

- Analyze the two datasets as complementary sources.
- Build a narrow joined table only for overlapping products.
- Use `amazon.csv` for product/review/price analysis and `ratings_Electronics.csv` for recommendation modeling.

## Today Alignment Message

I can explain my understanding to the mentor as:

> I understand this project as an end-to-end Amazon ecommerce business analytics project. The goal is to build a complete workflow from data cleaning and integration, metric definition, exploratory analysis, modeling, and visualization to final business recommendations.  
>   
> For Week 1, I will first focus on building the foundation: understanding the fields and granularity of each dataset, checking missing values, duplicates, abnormal values, and data types, then exploring which business metrics can be supported by the available fields. I will first explore broadly from sales/product performance, user behavior, product evaluation, review insights, and recommendation angles, then narrow down to the strongest directions based on data quality and business value.  
>   
> One preliminary finding is that the two current local datasets may not be fully joinable by product ID, so I will document the join feasibility and data limitations clearly, and propose a practical analysis structure based on what the data can support.
