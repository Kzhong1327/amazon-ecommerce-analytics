# Week 1 Plan: Data Engineering and Business Understanding

## Week 1 Objective

The first week should build the foundation for the rest of the project. The key outcome is to understand the data, clean it enough for analysis, define an initial metric pool, and document what the data can and cannot support.

## Tasks

1. Data inventory

Identify all available datasets, their source, file size, row count, column count, field names, and table granularity.

2. Field understanding

Create a data dictionary for important fields, including product ID, user ID, rating, review content, price, discount, category, rating count, and timestamp.

3. Data quality checks

Check missing values, duplicates, abnormal values, inconsistent data types, currency symbols, percentage strings, rating formats, and timestamp formats.

4. Join feasibility

Test whether the review/product dataset and rating dataset can be joined by `product_id`. If the overlap is limited, document the limitation and use separate analysis paths.

5. Initial metric definition

Define a candidate metric pool across product, user, review, and recommendation directions. Keep metrics that are both business-relevant and supported by the data.

6. First cleaned dataset

Prepare an analysis-ready version of the available data, including cleaned numeric price fields, rating fields, rating count fields, parsed categories, and converted timestamps where applicable.

7. Week 1 experiment report

Summarize what was done, key observations, data limitations, metric candidates, and the next-step plan.

## Deliverables

- Data inventory document.
- Initial data dictionary.
- Metric definition draft.
- Data quality summary.
- Cleaned or analysis-ready dataset draft.
- Week 1 experiment report.

## Suggested Timeline

- Day 1: Project setup, data inventory, mentor alignment message.
- Day 2: Field understanding, missing value and duplicate checks.
- Day 3: Cleaning rules, type conversion, category parsing, timestamp conversion.
- Day 4: Join feasibility test and first metric pool.
- Day 5: Week 1 report, cleaned dataset draft, and next-week analysis plan.

## Open Questions

- Should the first formal weekly report be sent on Wednesday, 2026-06-10, if the mentor said reports start from next week?
- Should `ratings_Electronics.csv` be treated as the main recommendation dataset while `amazon.csv` is treated as the product/review insight dataset?
- Should GMV be used only as an estimated proxy from product price and rating count, since the current files do not appear to contain true order quantity or transaction records?
