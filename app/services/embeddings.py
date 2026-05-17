import hashlib
import math
import os
import re
from collections import Counter
from collections.abc import Iterable

from app.services.html_parser import normalize_text


MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
VECTOR_SIZE = 384

QUERY_EXPANSIONS: dict[str, list[str]] = {
    "服务器": ["后端", "服务", "基础设施", "Kubernetes", "节点", "不可用"],
    "挂了": ["不可用", "故障", "崩溃", "超时", "异常", "宕机"],
    "宕机": ["不可用", "故障", "崩溃", "节点", "服务"],
    "黑客": ["安全", "入侵", "攻击", "漏洞", "恶意软件", "威胁"],
    "攻击": ["安全", "DDoS", "SQL注入", "入侵", "WAF", "威胁"],
    "机器学习": ["AI", "算法", "模型", "推荐", "推理", "GPU"],
    "模型": ["AI", "算法", "推荐", "推理", "效果", "特征"],
    "出问题": ["故障", "异常", "下降", "不可用", "延迟"],
    "质量下降": ["效果下降", "推荐", "点击率", "相关性", "模型"],
    "推荐": ["推荐系统", "模型", "点击率", "效果下降", "召回"],
    "主从": ["数据库", "复制", "延迟", "DBA", "MySQL"],
    "延迟": ["超时", "慢", "P99", "复制", "响应"],
}


class EmbeddingModel:
    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.model_name = model_name
        self._model = self._load_sentence_transformer(model_name)

    @property
    def backend(self) -> str:
        if self._model is None:
            return "hashing-fallback"
        return f"sentence-transformers:{self.model_name}"

    def embed_documents(self, texts: Iterable[str]) -> list[list[float]]:
        materialized = list(texts)
        if self._model is not None:
            return self._encode_sentence_transformers(materialized)
        return [hashing_embedding(text) for text in materialized]

    def embed_query(self, query: str) -> list[float]:
        expanded = expand_query(query)
        if self._model is not None:
            return self._encode_sentence_transformers([expanded])[0]
        return hashing_embedding(expanded)

    def _load_sentence_transformer(self, model_name: str):
        try:
            from sentence_transformers import SentenceTransformer

            return SentenceTransformer(model_name)
        except Exception:
            return None

    def _encode_sentence_transformers(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(
            texts,
            batch_size=32,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [vector.astype(float).tolist() for vector in vectors]


def expand_query(query: str) -> str:
    expanded_terms: list[str] = [query]
    query_lower = query.lower()
    for key, values in QUERY_EXPANSIONS.items():
        if key.lower() in query_lower:
            expanded_terms.extend(values)
    return normalize_text(" ".join(expanded_terms))


def hashing_embedding(text: str, dimensions: int = VECTOR_SIZE) -> list[float]:
    tokens = _tokens(text)
    vector = [0.0] * dimensions
    counts = Counter(tokens)
    for token, count in counts.items():
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign * (1.0 + math.log(count))
    return _normalize(vector)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def _tokens(text: str) -> list[str]:
    normalized = normalize_text(text)
    ascii_tokens = re.findall(r"[A-Za-z0-9+#.-]+", normalized.lower())
    chinese_terms = re.findall(r"[\u4e00-\u9fff]{2,}", normalized)
    char_bigrams = [
        term[index : index + 2]
        for term in chinese_terms
        for index in range(max(len(term) - 1, 0))
    ]
    return ascii_tokens + chinese_terms + char_bigrams


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]
