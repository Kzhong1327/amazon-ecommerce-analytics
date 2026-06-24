# Amazon 电商商业数据分析

这是一个基于 Amazon 商品与评分数据的四周端到端商业分析项目。项目覆盖数据清洗、业务指标、探索性分析、Tableau 仪表盘、NLTK 情感分析、LDA 主题模型、推荐系统原型和最终商业建议。

## 项目目标

项目围绕以下问题展开：

1. 哪些类目和产品更值得优先投入运营与质量资源？
2. 用户评分行为有什么分布和时间趋势？
3. 用户评论主要讨论什么，哪些主题的负面风险更高？
4. 是否可以基于用户共同评分行为生成相似商品推荐？
5. 当前数据能否支持类目增长、高价值用户和库存预测分析？

## 数据来源

项目使用两份互补但不能完整关联的数据：

- `amazon.csv`：1,465 条产品记录、1,351 个唯一商品，包含类目、价格、折扣、评分和评论文本。
- `ratings_Electronics.csv`：7,824,482 条评分记录、4,201,696 个用户和 476,002 个商品。

两个数据集只有 6 个商品 ID 精确重合，因此项目分别分析产品评论与用户评分行为，没有强行合并。

原始数据不应提交到 GitHub。下载后请放置在：

```text
data/raw/amazon.csv
data/raw/ratings_Electronics.csv
```

## 关键结论

- Electronics 占估算商业关注权重的 82.3%，但该指标是“折扣价 × 评分数量”，不是实际销售额。
- 100 个重点优化产品中，Electronics 有 51 个、Home&Kitchen 有 25 个、Computers&Accessories 有 23 个。
- 68.6% 的用户只评分一次，评分矩阵高度稀疏。
- 评分活动在 2013 年达到 2,626,582 条；2014 年数据可能不完整，不能直接解释为业务下降。
- NLTK VADER 识别出 74 条负向产品记录，高于词典 baseline 的 26 条，两种方法标签一致率为 91.26%。
- LDA 最终选择 3 个主题；易用性、性价比和日常体验主题覆盖 56.72% 的记录，负向占比为 5.78%。
- 推荐原型的 Hit Rate@5 为 7.12%，Hit Rate@10 为 8.64%，适合作为候选召回 baseline。

项目无法直接计算类目真实增长率、高价值用户消费额、转化率、复购率和库存预测。这些指标需要订单、金额、曝光、点击、加购和库存数据。

## 四周工作流

### Week 1：数据基础

- 字段、粒度和数据质量检查。
- 价格、评分数、折扣率和时间字段清洗。
- 类目拆分和两个数据集关联可行性检查。
- 输出分析就绪数据、数据字典和指标定义。

### Week 2：探索性分析与 Tableau

- 类目和产品表现分析。
- 用户活跃度、评分偏好和年度趋势分析。
- 评论长度、关键词和初步情感分析。
- 构建三页 Tableau 仪表盘。

Week 2 共生成 12 个 Tableau 数据文件，位于 `outputs/tableau/`：

- 产品与类目：`category_performance.csv`、`product_performance.csv`、`amazon_rating_distribution.csv`。
- 用户行为：`user_activity_distribution.csv`、`user_activity_top.csv`、`user_rating_preference.csv`、`yearly_rating_trend.csv`。
- 评论分析：`review_keyword_frequency.csv`、`review_length_vs_rating.csv`、`product_review_sentiment.csv`、`category_sentiment_summary.csv`、`sentiment_rating_distribution.csv`。

Week 2 的完整可视化交付还包括：

- `reports/dashboard/business_overview.twb`：可继续编辑的 Tableau workbook。
- `reports/dashboard/week2_tableau_export.pdf`：Tableau 导出的 13 页仪表盘和工作表。
- `reports/week2/screenshots/`：Week 1–2 脚本运行和 Tableau CSV 形状截图。
- `docs/week1_week2_experiment_report.md`：Week 1–2 合并实验报告文字版。
- `report/第一周与第二周实验报告.pdf`：Week 1–2 合并实验报告 PDF。

### Week 3：文本与推荐模型

- 自定义词典情感 baseline。
- NLTK VADER 情感对比。
- sklearn LDA 主题模型和主题数选择。
- item-item 共现推荐及留出评估。

### Week 4：综合商业分析

- 整合产品、用户、评论和推荐结果。
- 明确直接指标、代理指标和不可回答问题。
- 提出产品、供应链、营销、推荐与库存数据建设建议。
- 整理最终报告、GitHub 结构和演示材料。

## 项目结构

```text
data/
  raw/                 # 原始数据，本地保存，不提交 GitHub
  processed/           # 清洗后或抽样数据
docs/                  # 数据字典、周报、模型补充说明和最终报告
outputs/
  tables/              # Week 1 汇总结果
  tableau/             # Tableau 可直接导入的 CSV
  week3/               # 情感、LDA 和推荐输出
  week4/               # 最终可视化长表
reports/
  dashboard/           # Tableau workbook 和 Week 2 导出 PDF
  week2/               # Week 1–2 运行截图
  week3/               # NLTK 与 LDA 图片
  week4/               # 综合商业分析图片
src/
  data/                 # Week 1 数据处理
  analysis/             # Week 2 分析
  modeling/             # Week 3 文本与推荐模型
  visualization/        # Week 3/4 可视化脚本
```

## 环境安装

建议使用 Python 3.10 或以上版本：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m nltk.downloader vader_lexicon
```

## 运行顺序

在项目根目录依次运行：

```bash
python src/data/build_week1_outputs.py
python src/analysis/build_week2_outputs.py
python src/modeling/build_week3_outputs.py
python src/modeling/build_week3_nltk_outputs.py
python src/modeling/build_week3_lda_outputs.py
python src/visualization/build_week3_nltk_lda_figures.py
python src/visualization/build_week4_outputs.py
```

## Tableau

Tableau workbook 位于：

```text
reports/dashboard/business_overview.twb
```

Tableau 导出的完整 13 页结果位于：

```text
reports/dashboard/week2_tableau_export.pdf
```

可直接导入 Tableau 的数据位于 `outputs/tableau/`、`outputs/week3/` 和 `outputs/week4/`。主要仪表盘包括：

- Business Overview：类目评分数、平均评分和商业关注权重。
- Product & Review Insights：评分分布、关键词和情感结果。
- User Behavior Analysis：用户活跃度、评分偏好和年度趋势。
- Review Topic Modeling：NLTK 情感、LDA 主题覆盖、关键词和风险产品。

## 最终交付

- [最终商业报告 Word 完整版](reports/final_report/Amazon电商商业数据分析项目最终报告_完整版.docx)
- [最终商业报告文字版](docs/final_business_report_text.md)
- [Week 1–2 合并实验报告](docs/week1_week2_experiment_report.md)
- [Week 2 Tableau 导出结果](reports/dashboard/week2_tableau_export.pdf)
- [第三周 NLTK 补充说明](docs/week3_nltk_supplement.md)
- [第三周 LDA 补充说明](docs/week3_lda_supplement.md)
- [第四周 Tableau 指南](docs/week4_tableau_guide.md)
- [项目演示视频讲稿](docs/demo_video_script.md)

## 方法限制

- 商业关注权重不是真实 GMV。
- 高频用户不等于高消费用户。
- 两个数据集不能完整关联，用户行为无法直接连接评论主题。
- `review_content` 可能合并多条评论，情感和主题是产品记录级综合信号。
- LDA 受样本规模和词袋假设限制。
- 推荐模型是原型，尚未完成生产级排序和线上 A/B 测试。
