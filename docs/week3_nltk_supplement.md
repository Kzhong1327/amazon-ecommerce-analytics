# 第三周补充：NLTK VADER 情感分析对比

## 补充目的

原项目说明要求第三周使用 NLTK 或 TextBlob 进行更深入的评论情感分析。原第三周版本使用的是自定义正负词典和简单否定词处理，可以作为 baseline，但不能等同于 NLTK 情感模型。

本次补充使用 NLTK 的 VADER 情感分析器重新分析 `amazon_products_cleaned.csv` 中 1,465 条产品评论文本，并与原 baseline 标签进行比较。VADER 的标准阈值为：compound 大于等于 0.05 判定为 positive，小于等于 -0.05 判定为 negative，其余为 neutral。

## 关键代码

```python
from nltk.sentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
vader = pd.DataFrame(review_text.map(analyzer.polarity_scores).tolist())
```

```python
def vader_label(compound: float) -> str:
    if compound >= 0.05:
        return "positive"
    if compound <= -0.05:
        return "negative"
    return "neutral"
```

完整脚本位于：

`src/modeling/build_week3_nltk_outputs.py`

## 对比结果

| 方法 | Positive | Neutral | Negative |
| --- | ---: | ---: | ---: |
| 自定义词典 baseline | 1,380（94.2%） | 59（4.0%） | 26（1.8%） |
| NLTK VADER | 1,380（94.2%） | 11（0.8%） | 74（5.1%） |

两种方法的标签一致率为 91.26%。VADER 识别出的负向产品数量明显更多，其中 47 条 baseline positive 被 VADER 判定为 negative，14 条 baseline neutral 被 VADER 判定为 negative。

这一差异说明自定义词典更容易把包含大量正向词的长评论判为 positive，而 VADER 会综合考虑词语强度、否定和上下文标点，因此对部分负面表达更加敏感。但 Amazon 数据中的 `review_content` 可能把多条评论合并在一个字段中，所以 VADER 的产品级标签仍不能直接解释为单条评论情绪。

## Tableau 建议图表

数据源：

`outputs/week3/week3_nltk_sentiment_distribution.csv`

建议制作分组柱状图：

- Columns：`sentiment_label`
- Rows：`product_count`
- Color：`method`
- Label：`product_count` 和 `product_share`

图表标题：

`Baseline Dictionary vs NLTK VADER Sentiment Distribution`

还可以制作一张情感标签混淆热力图。

数据源：

`outputs/week3/week3_nltk_sentiment_confusion.csv`

Tableau 字段放置：

- Columns：`baseline_sentiment_label`
- Rows：`vader_sentiment_label`
- Color：`product_count`
- Label：`product_count`
- Tooltip：`product_share`
- Marks：Square

图表标题：

`Baseline vs NLTK VADER Label Agreement`

## 新增产物

- `outputs/week3/week3_nltk_vader_sentiment_comparison.csv`
- `outputs/week3/week3_nltk_sentiment_distribution.csv`
- `outputs/week3/week3_nltk_sentiment_confusion.csv`
- `outputs/week3/week3_nltk_category_sentiment.csv`
- `outputs/week3/week3_nltk_disagreement_samples.csv`

## 与其他第三周模型的关系

正式 LDA 主题模型已经通过 scikit-learn 补充完成，具体过程和结果见 `docs/week3_lda_supplement.md`。当前仍未完成的是 surprise 协同过滤推荐对比；已有推荐结果仍属于 item-item 共现相似度 baseline。
- 当前推荐模型仍是 item-item 共现相似度 baseline。
