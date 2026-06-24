# Week 2 Experiment Report Draft

## 1. 本周目标

第二周的目标是完成探索性分析与可视化准备，重点围绕三个方向展开：

- 用户与销售代理指标分析。
- 产品评分与评论内容分析。
- 为 Tableau / Power BI 仪表盘准备可直接导入的数据表。

由于当前数据集中没有真实订单金额、订单数量、点击、曝光或转化数据，本周将“销售额”相关分析明确处理为代理指标分析，而不是直接声称为真实 GMV。

## 2. 本周完成内容

### 2.1 用户与销售代理指标分析

基于 `amazon.csv` 的产品、价格、评分和评论数信息，构建了类目和产品表现分析表：

- 不同类目的产品数量。
- 不同类目的平均评分。
- 不同类目的总评分数。
- 不同类目的平均折扣水平。
- 不同类目的估算商业权重。

其中估算商业权重定义为：

```text
estimated_revenue_proxy = discounted_price_num * rating_count_num
```

这个指标不是严格意义上的销售额，而是用于估计产品或类目的商业重要性。它可以帮助识别“用户反馈多、价格权重高、值得优先关注”的类目和产品。

基于 `ratings_Electronics.csv`，完成了用户活跃分析：

- 用户评分次数分布。
- 高频用户识别。
- 高频用户与普通用户的评分偏好对比。
- 年度评分行为趋势。

本周将高活跃用户定义为评分次数位于 top 1% 的用户。当前数据中，高活跃用户阈值为至少 12 次评分。

### 2.2 产品与评论分析

基于 `amazon.csv`，完成了以下产品和评论分析：

- 产品评分分布。
- 不同类目的评分差异。
- 评论长度与评分区间的关系。
- 基于评论文本的高频词分析。
- 基于简单词典规则的初步情感分析。

情感分析目前是初步探索版本，使用正负向关键词词典计算评论文本倾向。它适合用于 Week 2 的初步 EDA，但不能替代 Week 3 更正式的 NLP 情感模型或主题模型。

### 2.3 仪表盘数据准备

已生成 Tableau / Power BI 可直接导入的 CSV 文件，统一放在：

```text
outputs/tableau/
```

本周重点产物是 Tableau / Power BI 可直接导入的结构化 CSV。静态图不作为核心交付物，后续图表会在 Tableau 中完成。

## 3. 关键发现

### 3.1 类目与产品表现

- 本次分析共准备了 9 个主类目和 1,465 条产品记录。
- 按估算商业权重看，`Electronics` 是最重要的类目。
- `Electronics` 在估算商业权重中的占比约为 82.3%。
- 识别出 49 个“估算商业权重较高但评分偏低”的产品，这类产品适合后续重点分析和优化建议。

### 3.2 用户行为

- `ratings_Electronics.csv` 的评分时间范围为 1998 年到 2014 年。
- 评分行为峰值年份为 2013 年。
- 用户行为非常稀疏，约 68.6% 的用户只留下过 1 次评分。
- 高活跃用户阈值为至少 12 次评分。
- 当前识别出 42,507 个高活跃用户，占全部 4,201,696 个用户的一小部分。
- 高频用户中 5 星评分占比约 59.0%，普通用户中 5 星评分占比约 55.1%，说明高活跃用户整体评分倾向略更正向。

### 3.3 产品与评论

- 初步情感分析结果显示，大多数产品评论文本偏正向。
- 当前产品情感标签分布为：positive 1,347 条，neutral 84 条，negative 34 条。
- 评论高频词包括：`quality`、`cable`、`phone`、`charging`、`battery`、`easy`、`working` 等。
- 这些关键词说明用户评论重点集中在产品质量、线缆/电子配件、手机充电、电池表现和使用体验。

## 4. 已生成的 Tableau / Power BI 数据表

| 文件 | 用途 |
| --- | --- |
| `outputs/tableau/category_performance.csv` | 类目表现：产品数、平均评分、总评分数、折扣、估算商业权重 |
| `outputs/tableau/product_performance.csv` | 产品表现明细：价格、评分、评论数、估算商业权重、机会分层 |
| `outputs/tableau/yearly_rating_trend.csv` | 年度评分趋势 |
| `outputs/tableau/user_activity_top.csv` | 高频用户明细 |
| `outputs/tableau/user_activity_distribution.csv` | 用户评分次数分布 |
| `outputs/tableau/user_rating_preference.csv` | 高频用户与普通用户评分偏好 |
| `outputs/tableau/product_review_sentiment.csv` | 产品级评论情感结果 |
| `outputs/tableau/category_sentiment_summary.csv` | 类目级情感汇总 |
| `outputs/tableau/review_keyword_frequency.csv` | 评论关键词频率 |
| `outputs/tableau/review_length_vs_rating.csv` | 评论长度与评分区间关系 |
| `outputs/tableau/amazon_rating_distribution.csv` | 产品评分分布 |
| `outputs/tableau/sentiment_rating_distribution.csv` | 情感标签与评分分布 |

## 5. 数据限制

- 当前数据不包含真实订单金额和订单数量，因此不能直接计算真实 GMV。
- 当前数据不包含曝光、点击、加购或访问数据，因此不能计算真实转化率。
- 当前数据不包含真实购买交易记录，因此用户价值更适合暂时定义为高活跃用户，而不是真实高消费用户。
- 两个数据集的 `product_id` 直接重合很少，因此不适合强行合并成完整交易宽表。
- Week 2 的情感分析是轻量词典方法，主要用于探索；Week 3 可以进一步使用更正式的 NLP 方法。

## 6. 下一步

下一步可以进入 Tableau / Power BI 仪表盘制作，但在导入前需要先确认：

- 是否接受使用 `estimated_revenue_proxy` 作为销售代理指标。
- 是否接受将 high-value user 暂时表述为 high-activity user。
- 仪表盘是否按三个页面搭建：业务概览、产品与评论洞察、用户行为分析。
