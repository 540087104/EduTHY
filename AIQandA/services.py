"""AI 智能答疑匹配引擎。

核心思路：
    不依赖外部大模型 API，使用「中文二元组 + 关键词重合度」实现轻量级
    语义匹配。相比传统的精确关键词匹配，它能容忍学生提问时的措辞差异，
    例如 "怎么查看当前目录" 与 "如何知道我在哪个文件夹" 都能命中
    同一条问答对。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from .models import QuestionAnswerPair


def _clean(text: str) -> str:
    """去掉空白与标点，只保留中文、字母、数字。"""
    return re.sub(r"[^\w\u4e00-\u9fff]", "", text or "", flags=re.UNICODE)


def _tokenize(text: str) -> set[str]:
    """把一段中文文本切分成二元字符组集合。

    二元组（bigram）能较好地捕捉中文词语的局部语义，且不需要额外词典。
    例如 "查看目录" -> {"查看", "看目", "目录"}。
    """
    text = _clean(text)
    if len(text) < 2:
        return {text} if text else set()
    return {text[i : i + 2] for i in range(len(text) - 1)}


def _unigrams(text: str) -> set[str]:
    """单字集合，作为二元组的补充，捕捉跨词语义重合。"""
    return set(_clean(text))


def _split_keywords(raw: str) -> set[str]:
    """把关键词字段按中英文逗号 / 空格切分。"""
    if not raw:
        return set()
    return {k.strip() for k in re.split(r"[,\s，]+", raw) if k.strip()}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


@dataclass
class MatchResult:
    """一次匹配的结果。"""

    qa: QuestionAnswerPair | None
    score: float
    answer: str


class AIChatService:
    """对外提供统一的答疑接口。"""

    # 命中阈值：综合得分低于该值视为未命中，走兜底回答
    THRESHOLD = 0.15

    def __init__(self, qa_pairs: Iterable[QuestionAnswerPair] | None = None):
        # 允许注入数据集，方便测试
        self._qa_pairs = list(qa_pairs) if qa_pairs is not None else None

    def _load_pairs(self) -> list[QuestionAnswerPair]:
        if self._qa_pairs is not None:
            return self._qa_pairs
        return list(QuestionAnswerPair.objects.filter(is_active=True).select_related("chapter"))

    def _score(self, question: str, qa: QuestionAnswerPair) -> float:
        """综合得分 = 0.5*二元组相似度 + 0.3*关键词重合度 + 0.2*单字重合度。"""
        q_tokens = _tokenize(question)
        doc_tokens = _tokenize(f"{qa.question} {qa.keywords}")
        bigram_score = _jaccard(q_tokens, doc_tokens)

        q_words = _split_keywords(question)
        kw_words = _split_keywords(qa.keywords)
        keyword_score = _jaccard(q_words, kw_words) if kw_words else 0.0

        unigram_score = _jaccard(_unigrams(question), _unigrams(f"{qa.question} {qa.keywords}"))

        return 0.5 * bigram_score + 0.3 * keyword_score + 0.2 * unigram_score

    def answer(self, question: str) -> MatchResult:
        """返回最佳匹配结果。"""
        pairs = self._load_pairs()
        if not pairs:
            return MatchResult(
                qa=None,
                score=0.0,
                answer="知识库暂无内容，请联系老师添加问答对。",
            )

        best_qa, best_score = max(
            ((qa, self._score(question, qa)) for qa in pairs),
            key=lambda x: x[1],
        )

        if best_score < self.THRESHOLD:
            return MatchResult(
                qa=None,
                score=best_score,
                answer=(
                    "抱歉，我暂时没有找到完全匹配的答案。"
                    "你可以尝试换一种问法，或把问题提交给老师，"
                    "老师会尽快补充到知识库中。"
                ),
            )

        return MatchResult(qa=best_qa, score=best_score, answer=best_qa.answer)
