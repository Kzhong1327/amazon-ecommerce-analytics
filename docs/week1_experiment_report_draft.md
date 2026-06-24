# 第一周实验报告草稿

## 1. 本周目标

第一周的目标是为 Amazon 电商商业数据分析项目搭建基础。主要工作包括理解当前可用数据集、检查数据质量、判断数据表之间的关联可行性、定义候选业务指标，并准备第一版可用于后续分析的数据结构。

## 2. 已完成工作

- 阅读项目说明，明确 4 周项目周期和每周核心任务。
- 将 `data/raw/` 作为原始数据的统一存放位置和后续处理的数据源。
- 检查了 `data/raw/amazon.csv` 和 `data/raw/ratings_Electronics.csv` 两个数据集。
- 初步理解了关键字段、表粒度、数据行数、字段数量和潜在业务用途。
- 发现 `ratings_Electronics.csv` 没有表头，读取时需要手动指定列名。
- 发现 `user_id` 和 `product_id` 应保留为字符串类型，避免部分商品 ID 的前导 0 被误删。
- 测试了两个数据集通过 `product_id` 直接关联的可行性。
- 搭建了第一版项目文件结构和文档结构。
- 编写了第一周可复用处理脚本：`src/data/build_week1_outputs.py`。
- 在 `data/processed/` 和 `outputs/tables/` 下生成了清洗后数据和数据质量汇总结果。

## 3. 初步数据理解

`amazon.csv` 主要包含产品层面的信息，包括商品 ID、商品名称、类目、折扣价、原价、折扣比例、平均评分、评分数量、产品描述、评论标题和评论内容等字段。这个数据集更适合用于产品表现、价格、折扣、类目和评论文本分析。

`ratings_Electronics.csv` 主要包含用户-商品-评分-时间记录。它的数据量更大，更适合用于用户活跃度分析、评分趋势分析、产品评分聚合和后续推荐模型。

## 4. 关键发现

- `amazon.csv` 有 1,465 行、16 个原始字段、1,351 个唯一产品。
- `ratings_Electronics.csv` 有 7,824,482 行、4 个原始字段、4,201,696 个唯一用户和 476,002 个唯一产品。
- `amazon.csv` 中 `rating_count` 有 2 个缺失值。
- `ratings_Electronics.csv` 在解释后的 4 个字段中没有缺失值。
- 两个数据集通过 `product_id` 直接匹配时，只有 6 个产品 ID 重合。
- 用户-商品评分矩阵密度约为 0.00000391，说明推荐系统数据非常稀疏。
- `amazon.csv` 更适合做产品、类目、价格、评分和评论内容分析。
- `ratings_Electronics.csv` 更适合做用户活跃度、评分聚合、年度趋势和推荐模型。

## 5. 数据限制

当前数据集并不完全支持真实交易层面的销售分析，主要限制包括：

- 真实 GMV 需要订单数量或真实交易金额，当前数据不直接支持。
- 转化率需要曝光、点击、加购或访问数据，当前数据不支持。
- 真实复购率需要用户购买交易记录，当前评分数据只能支持“重复互动”或“高活跃用户”的近似分析。
- 两个数据集通过 `product_id` 的直接重合很少，因此不适合强行合并成完整销售-评论宽表。

因此，后续如果使用销售额、用户价值或复购相关指标，需要明确标注为 proxy 指标或近似分析。

## 6. 候选指标方向

第一版候选指标池包括：

- 产品表现：产品数量、评论/评分数量、平均评分、低评分率。
- 价格与促销：原价、折扣价、折扣率。
- 用户行为：活跃用户数、用户评分次数、高频用户。
- 评论洞察：评论长度、高频关键词、情感分数、主题方向。
- 推荐系统：用户-商品评分矩阵密度、商品相似度、RMSE/MAE、Top-N 推荐准确率或召回率。

## 7. 已生成产物

清洗后数据：

- `data/processed/amazon_products_cleaned.csv`
- `data/processed/ratings_electronics_cleaned_sample_100k.csv`

汇总表：

- `outputs/tables/amazon_category_summary.csv`
- `outputs/tables/amazon_top_products_by_proxy_revenue.csv`
- `outputs/tables/amazon_low_rating_high_feedback_products.csv`
- `outputs/tables/ratings_product_summary.csv`
- `outputs/tables/ratings_top_users_by_activity.csv`
- `outputs/tables/ratings_yearly_summary.csv`
- `outputs/tables/week1_data_quality_summary.md`
- `outputs/tables/week1_data_quality_summary.json`

## 8. 下一步计划

- 检查清洗后的 `amazon_products_cleaned.csv`，确认后续是否需要对重复 `product_id` 进行产品层面去重或聚合。
- 判断是否需要将 `amazon.csv` 中逗号分隔的评论字段拆成更细的评论级数据。
- 使用 `ratings_product_summary.csv` 和 `ratings_top_users_by_activity.csv` 继续寻找第二周可深入分析的方向。
- 第二周开始围绕产品表现、用户活跃度、产品口碑和评论内容进行探索性分析与可视化准备。
