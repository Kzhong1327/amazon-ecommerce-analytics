# Week 1-2 实验报告

本报告汇总 Amazon 电商商业数据分析项目第 1-2 周的实验过程、个人思路、关键代码、实验结果、运行截图说明、本周完成情况和下周计划。

## 第一周：数据理解与数据工程基础

### 本周已完成

第一周主要完成项目基础建设，包括数据理解、数据质量检查、字段清洗、数据关联性判断和第一版指标口径设计。

已完成内容包括：

- 阅读项目说明，确认项目是一个 4 周 Amazon 电商端到端商业数据分析项目。
- 确认两个核心数据集：`amazon.csv` 和 `ratings_Electronics.csv`。
- 检查两个数据集的行数、字段数、缺失值、异常值、字段类型和数据粒度。
- 修正 `ratings_Electronics.csv` 的读取方式：该文件没有表头，需要手动指定字段名。
- 将 `user_id` 和 `product_id` 按字符串读取，避免带前导 0 的商品 ID 被错误转换。
- 测试两个数据集通过 `product_id` 直接关联的可行性。
- 编写第一周处理脚本 `src/data/build_week1_outputs.py`。
- 生成第一周数据质量摘要和清洗后的分析基础表。

### 个人思路

第一周的核心思路是先判断数据是否可靠、字段是否能支撑业务问题，而不是急着画图或建模。因为项目最终需要从清洗、分析、建模落到商业建议，如果前期没有弄清楚数据粒度和字段限制，后续容易出现指标解释过度或错误合并数据的问题。

我重点关注三个问题：两个数据集分别适合回答什么业务问题；两个数据集能否通过 `product_id` 合并；哪些指标可以直接计算，哪些只能作为 proxy。

检查后发现，`amazon.csv` 更适合做产品、类目、价格、评分和评论文本分析；`ratings_Electronics.csv` 更适合做用户行为、评分趋势和推荐模型。两个数据集直接重合的产品 ID 很少，因此后续应该把它们作为互补数据源使用。

### 实验关键代码

读取没有表头的评分数据：

```python
ratings = pd.read_csv(
    ratings_path,
    header=None,
    names=["user_id", "product_id", "rating", "timestamp"],
    dtype={
        "user_id": "string",
        "product_id": "string",
        "rating": "float64",
        "timestamp": "int64",
    },
)
ratings["date"] = pd.to_datetime(ratings["timestamp"], unit="s")
```

清洗价格、折扣和评分数量：

```python
cleaned["discounted_price_num"] = clean_money(cleaned["discounted_price"])
cleaned["actual_price_num"] = clean_money(cleaned["actual_price"])
cleaned["discount_percentage_num"] = clean_percent(cleaned["discount_percentage"])
cleaned["rating_num"] = pd.to_numeric(cleaned["rating"], errors="coerce")
cleaned["rating_count_num"] = clean_count(cleaned["rating_count"])
```

判断两个数据集的产品 ID 重合情况：

```python
overlap = set(ratings["product_id"].unique()) & amazon_product_ids
```

### 实验结果

- `amazon.csv` 有 1,465 行、16 个原始字段、1,351 个唯一产品。
- `ratings_Electronics.csv` 有 7,824,482 行、4 个原始字段、4,201,696 个唯一用户和 476,002 个唯一产品。
- `amazon.csv` 中 `rating_count` 有 2 个缺失值。
- `amazon.csv` 中有 1 条 `rating` 原始值为 `|`，转换成数值型 `rating_num` 时变成缺失。
- 两个数据集通过 `product_id` 直接匹配时，只有 6 个产品 ID 重合。
- 用户-商品评分矩阵密度约为 0.00000391，说明推荐系统数据非常稀疏。

最重要的结论是：两个数据集不适合强行合并成一个完整宽表。后续应该分开使用：`amazon.csv` 用于产品和评论分析，`ratings_Electronics.csv` 用于用户行为和推荐模型。

### 运行截图

第一周运行截图保存在 `reports/screenshots/week1_run_summary.png`。

## 第二周：探索性分析与 Tableau 数据准备

### 本周已完成

第二周主要完成探索性分析和 Tableau / Power BI 数据准备。分析分为三条主线：类目与产品表现、用户行为、产品评论内容。

已完成内容包括：

- 基于 `amazon.csv` 做类目表现分析，包括产品数、平均评分、总评分数、折扣水平和估算商业权重。
- 基于 `ratings_Electronics.csv` 做用户活跃分析，包括用户评分次数分布、高活跃用户识别和评分偏好对比。
- 分析评分数据的年度趋势，识别评分行为峰值年份。
- 基于 `review_content` 做评论关键词分析。
- 使用轻量词典方法做初步评论情感分析。
- 生成 Tableau / Power BI 可直接导入的 CSV。
- 在 Tableau 中开始搭建 3 个 Dashboard：业务概览、产品与评论洞察、用户行为分析。

### 个人思路

第二周的思路是先用探索性分析找出最值得深入的业务方向，而不是一开始就直接建模。由于当前数据不包含真实订单金额、购买数量、曝光或点击数据，所以我没有直接使用真实 GMV、转化率或 ROI，而是使用更谨慎的 proxy 指标。

对于类目和产品表现，我使用 `estimated_revenue_proxy = discounted_price_num * rating_count_num` 作为估算商业权重。这个指标不是实际销售额，而是用于近似衡量产品或类目的商业关注度。

对于用户分析，因为数据没有真实购买金额，所以我没有直接定义“高价值用户”，而是用评分次数定义“高活跃用户”。这样更符合当前数据实际。

对于评论分析，第二周先使用关键词和轻量情感分析做初步探索，第三周可以继续升级为更正式的 NLP 情感模型或主题模型。

### 实验关键代码

构建估算商业权重：

```python
amazon["estimated_revenue_proxy"] = (
    amazon["discounted_price_num"] * amazon["rating_count_num"]
)
```

构建用户活跃度分布：

```python
user_activity = (
    ratings.groupby("user_id")
    .agg(
        rating_count=("rating", "size"),
        avg_rating_given=("rating", "mean"),
        first_rating_date=("date", "min"),
        last_rating_date=("date", "max"),
        unique_products_rated=("product_id", "nunique"),
    )
    .reset_index()
)
```

定义高活跃用户：

```python
q99 = user_activity["rating_count"].quantile(0.99)
user_activity["user_segment"] = user_activity["rating_count"].apply(
    lambda x: "high_activity_user" if x >= q99 else "regular_user"
)
```

评论关键词和情感分析：

```python
word_counter = Counter()
for text in amazon["review_content"].fillna(""):
    word_counter.update(tokenize(text))

sentiment = amazon["review_content"].fillna("").apply(sentiment_score)
amazon["sentiment_score"] = [item[0] for item in sentiment]
amazon["sentiment_label"] = amazon["sentiment_score"].map(sentiment_label)
```

### 实验结果

- 本次分析共准备了 9 个主类目和 1,465 条产品记录。
- 按估算商业权重看，`Electronics` 是最重要的类目。
- `Electronics` 在 `estimated_revenue_proxy` 中占比约 82.3%。
- 识别出 49 个“估算商业权重较高但评分偏低”的产品。
- `ratings_Electronics.csv` 的评分时间范围为 1998 年到 2014 年。
- 评分行为峰值年份为 2013 年。
- 约 68.6% 的用户只留下过 1 次评分，说明用户行为非常稀疏。
- 高活跃用户阈值为至少 12 次评分，共识别出 42,507 个高活跃用户。
- 高频用户中 5 星评分占比约 59.0%，普通用户中 5 星评分占比约 55.1%。
- 初步评论情感标签分布为：positive 1,347 条，neutral 84 条，negative 34 条。
- 评论高频词包括 `quality`、`cable`、`phone`、`charging`、`battery`、`easy`、`working` 等。

这些结果说明，`Electronics` 是最值得关注的类目；用户评分行为非常稀疏；评论内容主要集中在产品质量、电子配件、手机充电、电池表现和使用体验等方面。

### 运行截图

第二周运行截图保存在：

- `reports/screenshots/week2_run_summary.png`
- `reports/screenshots/tableau_csv_shapes.png`

### Tableau 仪表盘结果

第二周已准备好 Tableau / Power BI 可导入 CSV，位置是 `outputs/tableau/`。

建议 Dashboard 分为 3 页：

- `Business Overview: Category Performance`
- `Product & Review Insights`
- `User Behavior Analysis`

其中业务概览页展示类目商业权重、总评分数和平均评分；产品与评论洞察页展示评分分布、评论关键词和情感分析；用户行为页展示用户活跃度、评分偏好和高活跃用户。

### 下周 TODO

第三周计划进入建模和深度洞察阶段，重点包括：

- 对评论文本做更深入的情感分析。
- 尝试做评论主题建模，提取用户关注的核心主题。
- 基于 `ratings_Electronics.csv` 构建简单推荐模型。
- 评估推荐模型效果。
- 将建模结果转化为可以支持商业建议的洞察。
