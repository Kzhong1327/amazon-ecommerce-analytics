# 第三周实验报告

## 本周已完成

第三周我主要开始做建模和深度洞察，重点放在两个方向：评论文本分析和推荐系统原型。

在评论分析部分，我基于 `amazon.csv` 的 `review_content` 做了更细的情感分析，并尝试提取用户评论中的主要关注主题。相比第二周只看高频词，这一周我希望进一步回答：用户到底是在关注质量、充电、电池、价格，还是配送和包装。

在推荐系统部分，我基于 `ratings_Electronics.csv` 做了一个 item-item 共现相似度推荐原型。这个原型的目标不是直接做生产级推荐系统，而是先验证能否根据用户评分行为生成“相似商品推荐”。

本周生成了产品级情感和主题结果、主题汇总表、主题关键词、负面反馈产品机会、商品推荐结果和推荐评估结果。

## 个人思路

第三周的思路是从第二周的 EDA 往“模型和洞察”推进。第二周已经发现用户评论中经常出现 `quality`、`charging`、`battery`、`cable`、`phone` 等词，所以第三周我继续围绕评论文本做更深入的分析。

我的实现顺序是先建立容易解释的 baseline，再补充正式模型做比较。情感分析先使用扩展版正负向词典和否定词处理，之后加入 NLTK VADER；主题分析先使用关键词主题组和 TF-IDF 风格排序，之后使用 scikit-learn LDA 从数据中自动学习主题。推荐系统目前仍使用 item-item 共现相似度，还没有使用 surprise。

这种顺序让我可以先确认数据和业务含义，再观察正式模型带来了哪些变化。LDA 不需要提前规定“质量”或“充电”等主题，而是根据词语共现自动形成主题；同时它仍然是词袋模型，所以我会把结果当作评论关注方向，而不是对每条评论做绝对分类。

## 实验关键代码

第三周核心脚本是：

- `src/modeling/build_week3_outputs.py`

### 1. 评论情感分析

情感分析使用正负向词典，并加入简单否定词判断。例如 `not good` 这类情况，不能直接把 `good` 当成正向词。

```python
def enhanced_sentiment(text: str) -> dict[str, float | int | str]:
    words = raw_words(text)
    positive = 0
    negative = 0
    for i, word in enumerate(words):
        previous = set(words[max(0, i - 3) : i])
        negated = bool(previous & NEGATIONS)
        if word in POSITIVE_WORDS:
            if negated:
                negative += 1
            else:
                positive += 1
        elif word in NEGATIVE_WORDS:
            if negated:
                positive += 1
            else:
                negative += 1

    raw_score = positive - negative
    norm_score = raw_score / math.sqrt(len(words))
```

这个方法比第二周的基础情感分析稍微细一点，因为它考虑了简单否定结构。

### 2. 评论主题 baseline

主题提取先定义几个用户可能关注的方向，比如充电、电池、质量、价格、兼容性、配送等，然后根据评论中出现的关键词判断主要主题。

```python
TOPIC_KEYWORDS = {
    "Charging & Power": {"charging", "charge", "charger", "cable", "power", "battery"},
    "Product Quality & Durability": {"quality", "durable", "sturdy", "broken", "material"},
    "Price & Value": {"price", "value", "money", "worth", "cheap"},
    "Compatibility & Usability": {"phone", "device", "compatible", "easy", "works"},
    "Delivery & Packaging": {"delivery", "package", "replacement", "refund"},
}
```

```python
def assign_topic(tokens: list[str]) -> tuple[str, int, str]:
    token_counts = Counter(tokens)
    scores = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        matches = [word for word in token_counts if word in keywords]
        score = sum(token_counts[word] for word in matches)
        scores[topic] = score
    best_topic, best_score = max(scores.items(), key=lambda item: item[1])
```

这个方法作为 baseline 可以快速得到可解释的主题结果，也能帮助检查后续 LDA 主题是否合理。

### 3. LDA 评论主题模型

正式主题模型位于 `src/modeling/build_week3_lda_outputs.py`。评论先通过 `CountVectorizer` 转换为词频矩阵，并保留单词和双词组合。随后比较 3 到 8 个主题模型的验证集困惑度：

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

验证集困惑度最低的模型被选为最终模型，再为 1,465 条产品记录计算主题概率和主主题。

### 4. 推荐系统原型

推荐系统使用 item-item 共现相似度。简单理解就是：如果两个商品经常被同一个用户评分过，那么这两个商品可能有一定相似性。

```python
for user_id, group in filtered.groupby("user_id", sort=False):
    products = list(dict.fromkeys(group.sort_values("timestamp")["product_id"].tolist()))
    if len(products) < 2:
        continue
    item_user_count.update(products)
    for a, b in combinations(sorted(products), 2):
        pair_counts[(a, b)] += 1
```

商品相似度使用 Jaccard 风格计算：

```python
similarity = co_count / (item_user_count[a] + item_user_count[b] - co_count)
```

最后根据相似度为每个商品输出 Top-N 推荐商品。

## 实验结果

### 评论情感与主题结果

本周共分析 1,465 条产品记录，识别出 6 个主题组：

- `Product Quality & Durability`
- `Charging & Power`
- `Compatibility & Usability`
- `Price & Value`
- `Delivery & Packaging`
- `General Experience`

关键词主题 baseline 中产品数量最多的是 `Product Quality & Durability`。正式 LDA 比较了 3 到 8 个主题，最终选择验证集困惑度最低的 3 主题模型，困惑度为 1817.96。

LDA 的三个主题分别为：

- `Value, Usability & Everyday Products`：831 条记录，占 56.72%，平均评分 4.083。
- `Smart Devices, Wearables & Audio`：301 条记录，占 20.55%，平均评分 4.053。
- `Charging, Cables & Connectivity`：333 条记录，占 22.73%，平均评分 4.171。

第一个主题覆盖范围最大，VADER 负向占比也最高，为 5.78%；智能设备、穿戴与音频主题平均评分最低，主要关键词包括 phone、battery、watch、sound、camera、screen 和 bluetooth。这个结果说明后续业务建议可以重点关注日常易用性、安装与性价比，以及智能设备的续航、显示和连接体验。

情感分析结果如下：

- positive 产品：1,380
- neutral 产品：59
- negative 产品：26

此外，我导出了 100 条负面反馈或评分偏低的产品优化机会。这些产品可以在第四周商业建议里继续使用，比如用于提出产品质量优化、页面描述优化或售后策略建议。

### 推荐系统结果

推荐系统部分使用评分次数在 2 到 20 次之间的用户作为候选用户，并抽样 50,000 个用户构建 item-item 共现相似度。

推荐原型结果如下：

- 使用的过滤后交互记录：96,018 条
- 有推荐结果的商品数：2,102 个
- 推荐结果行数：4,862 行
- 评估用户数：5,000 个
- Hit Rate@5：0.0712
- Hit Rate@10：0.0864

这个结果说明，简单 item-item 共现推荐已经可以生成推荐候选，但整体命中率仍然有限。我认为主要原因是评分矩阵非常稀疏，很多用户只评分过很少商品，商品之间能学习到的共现关系不够丰富。

## 已生成产物

第三周产物位于：

- `outputs/week3/`

主要文件包括：

- `week3_product_sentiment_topics.csv`：产品级情感和主题结果。
- `week3_topic_summary.csv`：主题汇总表。
- `week3_topic_keywords.csv`：每个主题的代表关键词。
- `week3_negative_review_opportunities.csv`：负面反馈或低评分产品机会。
- `week3_item_recommendations.csv`：item-item 推荐结果。
- `week3_recommendation_evaluation.csv`：推荐系统评估结果。
- `week3_nltk_vader_sentiment_comparison.csv`：词典情感与 NLTK VADER 对比。
- `week3_lda_model_comparison.csv`：LDA 主题数选择结果。
- `week3_lda_topic_keywords.csv`：LDA 主题关键词及权重。
- `week3_lda_product_topics.csv`：每条产品记录的主主题和主题概率。
- `week3_lda_product_topic_distribution.csv`：所有产品记录的主题概率长表。
- `week3_lda_topic_summary.csv`：LDA 主题业务指标汇总。

## 方法限制

当前第三周模型还是 prototype，有几个限制需要说明：

- 情感分析已经补充 NLTK VADER，但评论字段可能合并多条评论，因此标签仍是产品级综合信号。
- 已完成正式 sklearn LDA，但样本量较小，而且 LDA 的词袋假设不能理解完整语序和上下文。
- 推荐模型使用 item-item 共现相似度，不是完整矩阵分解或 surprise 协同过滤模型。
- 推荐评估使用轻量留出法，适合原型验证，但不代表生产环境效果。

这些限制不影响第三周作为建模原型交付，但第四周写最终商业报告时，需要清楚说明模型方法和解释边界。

## 第四周 TODO

第四周进入商业应用和综合报告阶段，计划包括：

- 整合前 3 周的数据清洗、EDA、评论分析和推荐模型结果。
- 总结最重要的业务发现。
- 将评论主题和负面反馈产品转化为产品优化建议。
- 将用户行为和推荐结果转化为运营或推荐策略建议。
- 整理最终报告 PDF/PPT。
- 整理代码和输出文件，形成结构清晰的项目交付包。
