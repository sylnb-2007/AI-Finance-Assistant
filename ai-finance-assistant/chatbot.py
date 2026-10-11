# -*- coding: utf-8 -*-
"""
chatbot.py —— 把"知识库问答"和"语言模型生成"组合成一个金融小助手。

本项目的机器人有两种回答方式：

1) 知识库回答（检索式）：
     把用户的问题和金融知识库里每一条问题的"关键词"做匹配，
     命中哪条就给哪条的现成答案。答案准确、可靠。

2) 模型生成（生成式）：
     如果知识库里没有匹配，就用 n-gram 语言模型"编"一段金融味儿的话，
     让你直观看到"预测下一个字"是怎么工作的。

两者结合，既保证能给出有用的金融知识，又能演示语言模型的原理。
"""

import json
import os

from tokenizer import tokenize
from ngram_model import NgramModel


class FinanceChatbot:
    def __init__(self, faq_path, corpus_path, n=3):
        # 1) 加载金融知识库
        with open(faq_path, encoding="utf-8") as f:
            self.faq = json.load(f)

        # 2) 加载语料并训练语言模型
        with open(corpus_path, encoding="utf-8") as f:
            corpus = [line.strip() for line in f if line.strip()]
        self.model = NgramModel(n=n)
        self.model.train(corpus)

    # ---------- 知识库检索 ----------
    def _match_score(self, question, faq_item):
        """计算用户问题与某条知识库问题的"匹配得分"。"""
        # 把用户输入切字，并做成集合，方便看"关键词有没有出现"
        user_tokens = set(tokenize(question))
        keywords = faq_item["k"].split()  # 这条知识的关键词
        score = 0
        for kw in keywords:
            if kw in question:            # 关键词直接出现在问题里，得分最高
                score += 2
            elif kw in user_tokens:       # 或作为独立 token 出现
                score += 1
        return score

    def retrieve(self, question, threshold=2):
        """在知识库里找最匹配的一条，得分足够高就返回它的答案，否则返回 None。"""
        best = None
        best_score = 0
        for item in self.faq:
            s = self._match_score(question, item)
            if s > best_score:
                best_score = s
                best = item
        if best and best_score >= threshold:
            return best, best_score
        return None, best_score

    # ---------- 对外接口 ----------
    def answer(self, question, temperature=0.8):
        """回答问题。返回 (回答文本, 模式)。
        模式是 "知识库" 或 "生成"。"""
        hit, score = self.retrieve(question)
        if hit:
            return hit["a"], "知识库"

        # 没匹配到，就用语言模型生成一段金融文本作为演示
        generated = self.model.generate(seed="", max_len=40, temperature=temperature)
        return generated, "生成"


# 便于单独测试
if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    bot = FinanceChatbot(
        os.path.join(base, "data", "finance_faq.json"),
        os.path.join(base, "data", "finance_corpus.txt"),
    )
    for q in ["什么是复利", "新手如何开始理财", "什么是市盈率", "讲讲爱情"]:
        a, mode = bot.answer(q)
        print(f"[{mode}] 问：{q}\n    答：{a}\n")
