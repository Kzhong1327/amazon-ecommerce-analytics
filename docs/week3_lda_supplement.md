# 第三周补充：LDA 评论主题模型

## 实验目的

前面的主题分析是根据预先定义的关键词把评论分到质量、充电、价格、兼容性和配送等主题中。这种方法容易解释，但主题范围由人工提前决定，可能遗漏数据中自然形成的讨论方向。因此本次补充使用 scikit-learn 的 `LatentDirichletAllocation` 建立正式 LDA 模型，让主题直接从评论词语的共现关系中产生。

本次分析使用 `amazon_products_cleaned.csv` 中 1,465 条产品记录的 `review_content`。由于同一 `product_id` 在原始数据中可能重复，输出中另外生成了 `amazon_record_id`，确保 Tableau 不会把不同记录错误合并。

## 个人思路

我没有直接指定一个主题数，而是先比较 3 到 8 个主题。评论文本按 80% 训练集和 20% 验证集拆分，在相同词表和随机种子下分别训练模型，再比较验证集困惑度。困惑度越低，表示模型对未参与训练的评论解释得越好。最终 3 主题模型的困惑度最低，因此采用 3 个主题，而不是为了让图表更丰富而强行选择更多主题。

文本向量使用词频而不是 TF-IDF，因为 LDA 的概率假设基于词语出现次数。向量化时保留单词和双词组合，删除英文停用词以及 `product`、`review`、`quality` 等区分度较低的领域泛词；词语至少在 5 条评论中出现，词表上限为 3,000。

## 实验关键代码

核心脚本为 `src/modeling/build_week3_lda_outputs.py`。

```python
vectorizer = CountVectorizer(
    stop_words=stopwords,
    ngram_range=(1, 2),
    min_df=5,
    max_df=0.90,
    max_features=3000,
)
```

候选主题数比较使用验证集困惑度：

```python
for topic_count in range(3, 9):
    model = LatentDirichletAllocation(
        n_components=topic_count,
        learning_method="batch",
        max_iter=30,
        random_state=42,
    )
    model.fit(train_matrix)
    heldout_perplexity = model.perplexity(test_matrix)
```

选择主题数后，模型会为每条产品评论输出各主题概率，并把概率最高的主题作为主主题：

```python
topic_probabilities = model.fit_transform(full_matrix)
dominant_topic_ids = topic_probabilities.argmax(axis=1) + 1
dominant_probabilities = topic_probabilities.max(axis=1)
```

## 实验结果

主题数比较结果如下：

| 主题数 | 验证集困惑度 |
|---:|---:|
| 3 | 1817.96 |
| 4 | 1930.40 |
| 5 | 2054.97 |
| 6 | 2269.58 |
| 7 | 2426.53 |
| 8 | 2564.18 |

3 主题模型的验证集困惑度最低。最终三个主题的业务解释如下：

| LDA 主题 | 代表关键词 | 产品数 | 产品占比 | 平均评分 | VADER 负向占比 |
|---|---|---:|---:|---:|---:|
| Value, Usability & Everyday Products | easy、water、money、value、installation、mouse | 831 | 56.72% | 4.083 | 5.78% |
| Smart Devices, Wearables & Audio | phone、battery、watch、sound、camera、screen、bluetooth | 301 | 20.55% | 4.053 | 4.32% |
| Charging, Cables & Connectivity | cable、charging、fast、usb、charger、power | 333 | 22.73% | 4.171 | 3.90% |

第一类主题覆盖 831 条记录，是范围最大的主题，同时 VADER 负向占比也是三个主题中最高的 5.78%。它反映的不是单一产品类型，而是用户对易用性、安装、性价比和日常使用体验的综合评价，因此可以作为优先监控的广泛体验主题。

智能设备、穿戴与音频主题的平均评分最低，为 4.053，关键词集中在手机、电池、手表、声音、相机、屏幕和蓝牙。对这一主题的商业建议应更关注设备性能、续航、显示效果和连接体验。

充电、线缆与连接主题的平均评分最高，为 4.171，负向占比最低，为 3.90%。这说明该主题整体口碑相对稳定，但由于仍包含大量充电速度、USB、充电器和功率讨论，仍适合用于页面参数和兼容性说明优化。

## 生成文件

- `week3_lda_model_comparison.csv`：3–8 个主题模型的困惑度和模型选择结果。
- `week3_lda_topic_keywords.csv`：每个主题前 12 个关键词及其权重。
- `week3_lda_product_topics.csv`：每条产品记录的主主题、主题概率、评分和情感信息。
- `week3_lda_product_topic_distribution.csv`：每条记录属于所有主题的概率长表。
- `week3_lda_topic_summary.csv`：主题规模、评分、商业权重和 VADER 负向占比汇总。

以上文件都位于 `outputs/week3/`。

## Tableau 插图建议

第一张图建议使用 `week3_lda_model_comparison.csv` 制作折线图：

- Columns：`topic_count`
- Rows：`heldout_perplexity`
- Label：`heldout_perplexity`
- Color：`selected_model`
- 标题：`LDA Topic Number Selection`

第二张图使用 `week3_lda_topic_summary.csv` 制作横向柱状图：

- Rows：`lda_topic_label`
- Columns：`product_count`
- Color：`vader_negative_share`
- Label：`product_count` 和 `product_share`
- 标题：`LDA Topic Coverage and Negative Risk`

第三张图仍使用主题汇总表制作气泡图：

- Columns：`avg_rating`
- Rows：`vader_negative_share`
- Size：`product_count`
- Color：`lda_topic_label`
- Label：`lda_topic_label`
- 标题：`LDA Topic Performance and Risk Matrix`

## 方法限制

本次已经使用正式 LDA，而不是关键词主题规则，但仍有三个限制。第一，数据只有 1,465 条产品级记录，样本规模不大。第二，`review_content` 可能合并多条用户评论，因此主题代表的是产品记录的综合讨论方向。第三，LDA 基于词袋假设，不能理解完整语序和上下文。后续可以使用 Gensim 计算 coherence，并与当前困惑度结果交叉验证，也可以尝试 BERTopic 等语义主题方法作为对照。
