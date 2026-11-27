"""纯 Python 中文 BM25 检索器（零第三方依赖）。

中文分词策略：单字 + 相邻二元组（bigram）。
例如"客流时空特征" -> 客,流,时,空,特,征,客流,流时,时空,空特,特征。
该方法对中文检索足够有效，且不需要安装 jieba。
"""
import math
import re
from collections import Counter


def tokenize(text: str):
    """中文字符切分：单字 + bigram；英文/数字按词切分。"""
    text = text.lower()
    tokens = []
    for seg in re.findall(r"[\u4e00-\u9fff]+|[a-z0-9]+", text):
        if re.match(r"^[\u4e00-\u9fff]", seg):
            tokens.extend(seg)                       # 单字
            tokens.extend(seg[i:i+2] for i in range(len(seg) - 1))  # 二字词
        else:
            tokens.append(seg)
    return tokens


class BM25Retriever:
    def __init__(self, chunks, k1=1.5, b=0.75):
        self.chunks = chunks
        self.k1, self.b = k1, b
        self.docs = [tokenize(c["text"]) for c in chunks]
        self.tf = [Counter(d) for d in self.docs]
        self.df = Counter()
        for d in self.docs:
            for t in set(d):
                self.df[t] += 1
        self.N = len(self.docs)
        self.avgdl = sum(len(d) for d in self.docs) / max(self.N, 1)

    def _score(self, query_tokens, idx):
        score, doc, dl = 0.0, self.tf[idx], len(self.docs[idx])
        for term in set(query_tokens):
            f = doc.get(term, 0)
            if not f:
                continue
            df = self.df[term]
            idf = math.log(1 + (self.N - df + 0.5) / (df + 0.5))
            denom = f + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            score += idf * f * (self.k1 + 1) / denom
        return score

    def retrieve(self, query, top_k=3):
        """返回得分最高的 top_k 个文本块（附 score）。"""
        qt = tokenize(query)
        scored = [(self._score(qt, i), i) for i in range(self.N)]
        scored = [(s, i) for s, i in scored if s > 0]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {**self.chunks[i], "score": round(s, 4)}
            for s, i in scored[:top_k]
        ]
