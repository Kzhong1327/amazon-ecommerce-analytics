# 第四周实验报告

## 一、本周工作概述

第四周的重点是把前三周已经完成的数据清洗、探索性分析和模型结果整理成更容易理解的可视化，并进一步转化为业务建议。本周没有重新训练一套复杂模型，而是围绕第三周的评论主题、情感分析、负面产品机会和推荐评估结果，制作 Tableau 可直接使用的长表数据和静态图。

本周新增了 `week4_tableau_visual_metrics.csv`。这张表将情感分布、主题表现、推荐命中率、重点优化产品分布和关键 KPI 统一成同一种长表结构，后续可以在 Tableau 中通过 `view_name` 过滤不同图表，不需要建立多个数据源之间的关系。

## 二、个人思路

前三周已经完成了从原始数据到模型原型的主要分析流程，但模型输出主要是 CSV 和文字结果，读者需要自己查看字段才能理解。因此第四周我希望解决的是“如何让分析结果更容易被业务人员读懂”。

在主题分析中，我把产品数量和负面占比分开看。产品数量可以反映问题影响范围，负面占比可以反映风险强度。例如产品质量与耐用性主题覆盖 421 个产品，是规模最大的主题；配送与包装主题只有 34 个产品，但负面占比达到 11.8%，因此仍然值得优先排查。

推荐系统方面，我没有只展示 Hit Rate 数值，而是同时保留评估用户数、可推荐商品数和推荐结果行数，帮助读者理解模型目前的覆盖范围。当前模型适合作为相似商品候选生成的基础版本，后续可以继续使用 surprise 等库构建协同过滤模型并比较效果。

## 三、实验关键代码

### 1. 生成情感分布数据

```python
sentiment_order = ["positive", "neutral", "negative"]
sentiment_counts = products["sentiment_label"].value_counts()
for order, label in enumerate(sentiment_order, start=1):
    count = int(sentiment_counts.get(label, 0))
```

### 2. 将主题指标整理为 Tableau 长表

```python
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
        }
    )
```

### 3. 整理推荐模型评估指标

```python
recommendation_rows = [
    ("Hit Rate@5", float(evaluation["hit_rate_at_5"]), 1),
    ("Hit Rate@10", float(evaluation["hit_rate_at_10"]), 2),
]
```

## 四、实验结果与主要发现

### 1. 评论情感

- 1,465 个产品中，positive 为 1,380 个，占 94.2%。
- neutral 为 59 个，占 4.0%；negative 为 26 个，占 1.8%。
- 正向产品平均评分约为 4.12，负向产品平均评分约为 3.74。
- 整体口碑明显偏正向，但仍需要结合低评分和高反馈产品定位具体问题。

### 2. 评论主题

- Product Quality & Durability 包含 421 个产品，占 28.7%，是覆盖范围最大的主题。
- Charging & Power 包含 404 个产品，占 27.6%，说明充电、电池、线缆和接口体验也是主要关注点。
- Delivery & Packaging 只有 34 个产品，但负面占比达到 11.8%，是风险比例最高的主题。
- 主题规模和风险比例需要一起判断，不能只按产品数量决定优先级。

### 3. 重点优化产品

- 共筛选出 100 个低评分或负面反馈产品机会。
- Electronics 有 51 个，占 51%；Home&Kitchen 有 25 个，占 25%。
- Computers&Accessories 有 23 个，占 23%；MusicalInstruments 有 1 个。
- 产品优化和运营排查可以优先从 Electronics 开始。

### 4. 推荐模型

- 评估用户数为 5,000。
- Hit Rate@5 为 7.12%，Hit Rate@10 为 8.64%。
- 将推荐列表从 5 个增加到 10 个，命中率提高 1.52 个百分点。
- 当前输出覆盖 2,102 个源商品，共生成 4,862 条商品推荐关系。
- 模型已经能够生成相似商品候选，但准确率和覆盖率仍有提升空间。

## 五、商业建议

1. 产品质量：针对质量与耐用性主题建立重点监控清单，优先检查高反馈、低评分商品的材料、做工和使用寿命问题。
2. 充电体验：对充电、电池、线缆和接口相关商品优化兼容性说明、功率参数和使用指南。
3. 配送包装：虽然相关产品数量较少，但负面占比最高，应检查包装破损、配送延迟和退换货流程。
4. 类目运营：100 个重点优化产品中 Electronics 占 51%，可优先投入页面优化、售后说明和质量排查资源。
5. 推荐策略：将 item-item 模型作为候选召回层，后续再结合协同过滤、商品属性和流行度进行排序。

## 六、已生成产物

- `src/visualization/build_week4_outputs.py`
- `outputs/week4/week4_tableau_visual_metrics.csv`
- `reports/week4/figures/week4_sentiment_distribution.png`
- `reports/week4/figures/week4_topic_performance.png`
- `reports/week4/figures/week4_topic_risk_matrix.png`
- `reports/week4/figures/week4_recommendation_evaluation.png`
- `reports/week4/figures/week4_opportunity_by_category.png`

## 七、后续改进

- 使用 TextBlob 或 NLTK 与当前词典情感方法进行比较。
- 使用 Gensim coherence 或语义主题模型继续验证当前 sklearn LDA 的稳定性。
- 使用 surprise 构建协同过滤模型，并比较 Hit Rate、Precision 和 Recall。
- 如果后续获得真实订单、曝光和点击数据，可以进一步计算真实销售额、转化率和用户价值。
