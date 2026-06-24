# Tableau Dashboard Plan

## 当前状态

第二周 Tableau / Power BI 所需的 CSV 已准备好，路径为：

```text
outputs/tableau/
```

目前还没有导入 Tableau。下一步需要先确认数据口径和仪表盘结构。

## Dashboard 1: Business Overview

目标：展示整体类目表现、估算商业权重、评分趋势和重点产品机会。

建议数据源：

- `category_performance.csv`
- `product_performance.csv`
- `yearly_rating_trend.csv`

建议图表：

- 类目估算商业权重柱状图。
- 类目平均评分对比。
- 年度评分行为趋势折线图。
- 产品机会散点图：`rating_count_num` vs `rating_num`，颜色使用 `opportunity_segment`，大小使用 `estimated_revenue_proxy`。

核心解释：

- `estimated_revenue_proxy` 不是实际销售额，而是 `discounted_price_num * rating_count_num`。
- 它适合用来判断类目或产品的商业关注优先级。

## Dashboard 2: Product & Review Insights

目标：展示产品评分、评论长度、情感倾向和用户关注关键词。

建议数据源：

- `amazon_rating_distribution.csv`
- `review_length_vs_rating.csv`
- `product_review_sentiment.csv`
- `category_sentiment_summary.csv`
- `review_keyword_frequency.csv`
- `sentiment_rating_distribution.csv`

建议图表：

- 产品评分分布柱状图。
- 评论长度与评分区间热力图。
- 类目情感得分对比。
- 情感标签与评分区间分布。
- 评论关键词词云或 Top keyword bar chart。
- 低评分/负面情感产品明细表。

核心解释：

- Week 2 情感分析是基于词典规则的初步探索。
- Week 3 已补充 NLTK VADER 和 sklearn LDA，相关 CSV 可以继续加入评论洞察仪表盘。

## Dashboard 3: User Behavior Analysis

目标：展示用户活跃度、评分偏好和购买/互动模式代理分析。

建议数据源：

- `user_activity_distribution.csv`
- `user_activity_top.csv`
- `user_rating_preference.csv`
- `yearly_rating_trend.csv`

建议图表：

- 用户评分次数分布柱状图。
- 高频用户 Top 表。
- 高频用户 vs 普通用户评分偏好堆叠柱状图。
- 年度评分行为趋势折线图。

核心解释：

- 当前数据没有真实购买金额，因此不能定义真实高价值用户。
- 本阶段使用 high-activity user，即评分次数位于 top 1% 的用户，作为用户行为分析的重点群体。

## 建议 Tableau 导入顺序

1. 先导入 `category_performance.csv`，做业务概览第一张柱状图。
2. 导入 `yearly_rating_trend.csv`，做年度趋势线。
3. 导入 `product_performance.csv`，做产品机会散点图。
4. 导入评论相关 CSV，做产品与评论洞察页面。
5. 导入用户相关 CSV，做用户行为页面。

## 导入前确认

在正式打开 Tableau 导入之前，建议先确认以下三点：

- Dashboard 页面结构是否采用这 3 页。
- 是否保留英文变量名，方便 Tableau 字段识别。
- 最终汇报时是否用中文标题和中文注释。
