# 第四周 Tableau 操作指南

## 数据源

只需要导入一个文件：

`outputs/week4/week4_tableau_visual_metrics.csv`

建议字段类型：

- `view_name`：字符串 / Dimension
- `dimension`：字符串 / Dimension
- `metric_name`：字符串 / Dimension
- `metric_value`：数值 / Measure
- `share_value`：数值，格式设置为 Percentage
- `avg_rating`：数值，保留 2 位小数
- `avg_sentiment_score`：数值，保留 2 位小数
- `negative_share`：数值，格式设置为 Percentage
- `display_order`：整数
- `business_note`：字符串 / Dimension

不要把这个 CSV 和其他表建立 Relationship 或 Join。每张图使用 `view_name` 作为筛选条件。

## Worksheet 1：KPI Cards

1. 将 `view_name` 拖到 Filters，只选择 `KPI`。
2. 将 `dimension` 拖到 Columns。
3. 将 `metric_value` 拖到 Text。
4. 将 `business_note` 拖到 Tooltip。
5. Marks 选择 Text，打开 Show Mark Labels。
6. 按 `display_order` 排序。

## Worksheet 2：Sentiment Distribution

1. 将 `view_name` 拖到 Filters，只选择 `Sentiment Distribution`。
2. 将 `dimension` 拖到 Columns。
3. 将 `metric_value` 拖到 Rows。
4. 将 `dimension` 拖到 Color。
5. 将 `metric_value` 和 `share_value` 拖到 Label。
6. 将 `avg_rating`、`avg_sentiment_score` 和 `business_note` 拖到 Tooltip。
7. Marks 选择 Bar。

建议颜色：positive 使用绿色，neutral 使用黄色，negative 使用红色。

## Worksheet 3：Topic Performance

1. 将 `view_name` 拖到 Filters，只选择 `Topic Performance`。
2. 将 `dimension` 拖到 Rows。
3. 将 `metric_value` 拖到 Columns。
4. 将 `negative_share` 拖到 Color 和 Label。
5. 将 `avg_rating`、`avg_sentiment_score`、`share_value` 和 `business_note` 拖到 Tooltip。
6. 按 `metric_value` 降序排列。
7. Marks 选择 Bar。

## Worksheet 4：Topic Risk Matrix

1. 将 `view_name` 拖到 Filters，只选择 `Topic Performance`。
2. 将 `avg_rating` 拖到 Columns。
3. 将 `negative_share` 拖到 Rows。
4. 将 `metric_value` 拖到 Size。
5. 将 `dimension` 拖到 Label。
6. 将 `negative_share` 拖到 Color。
7. 将 `business_note`、`avg_sentiment_score` 和 `share_value` 拖到 Tooltip。
8. Marks 选择 Circle。

这张图中越靠左表示平均评分越低，越靠上表示负面占比越高，圆越大表示涉及产品越多。

## Worksheet 5：Recommendation Evaluation

1. 将 `view_name` 拖到 Filters，只选择 `Recommendation Evaluation`。
2. 将 `dimension` 拖到 Columns。
3. 将 `metric_value` 拖到 Rows。
4. 将 `metric_value` 拖到 Label。
5. 将数字格式设置为 Percentage，保留 2 位小数。
6. Marks 选择 Bar。

## Worksheet 6：Opportunity by Category

1. 将 `view_name` 拖到 Filters，只选择 `Opportunity by Category`。
2. 将 `dimension` 拖到 Rows。
3. 将 `metric_value` 拖到 Columns。
4. 将 `metric_value` 和 `share_value` 拖到 Label。
5. 将 `avg_rating`、`avg_sentiment_score` 和 `business_note` 拖到 Tooltip。
6. 按 `metric_value` 降序排列。

## Dashboard 4：Model Insights & Business Actions

建议布局：

1. 顶部：KPI Cards。
2. 中间左侧：Sentiment Distribution。
3. 中间右侧：Topic Performance。
4. 下方左侧：Topic Risk Matrix。
5. 下方右侧：Recommendation Evaluation。
6. 底部：Opportunity by Category。

Dashboard 标题建议使用：

`Model Insights & Business Actions`

副标题可以写：

`Week 4 Visualization Supplement: Review Topics, Product Opportunities and Recommendation Evaluation`

