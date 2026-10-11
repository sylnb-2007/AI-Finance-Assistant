# -*- coding: utf-8 -*-
"""
ngram_model.py —— 一个最简单的"语言模型"

核心思想（也是所有大语言模型的思想）：
    语言模型只会做一件事——"根据前面已经出现的字，预测下一个字最可能是什么"。

比如看到 "复" 这个字，它猜测下一个字最可能是 "利"；
看到 "复利"，它猜测下一个字可能是 "就" 或 "是"……

本文件用一个 n-gram（n 元语法）统计模型来实现这件事：
    我们把语料里"某个前文后面跟了哪些字、各出现了几次"统计出来，
    次数越多，就认为概率越大。预测时按这个概率去挑下一个字。

这比神经网络大模型简单得多，但思路完全一致：
    "根据历史，预测下一个 token。"
"""

import random
from collections import defaultdict, Counter

from tokenizer import tokenize_sentence


class NgramModel:
    """n-gram 语言模型。

    参数 n：用"前 n-1 个字"来预测"下一个字"。
        n=2 叫二元模型（bigram），n=3 叫三元模型（trigram），以此类推。
        本项目默认 n=3，也就是看"前面两个字"猜"下一个字"。
    """

    def __init__(self, n=3):
        self.n = n
        # counts 的结构：
        #   counts[(前文1, 前文2, ...)] -> Counter({下一个字: 出现次数})
        # 例如 counts[("复", "利")] -> Counter({"就": 3, "是": 1, "能": 2})
        self.counts = defaultdict(Counter)
        self.vocab = set()  # 词表：语料里出现过的所有字/词

    # ---------- 训练 ----------
    def train(self, corpus):
        """读入语料（一个字符串列表，每项是一句话），统计"前文 -> 下一个字"的次数。"""
        for sentence in corpus:
            tokens = tokenize_sentence(sentence)  # 切字，并加 <BOS>、<EOS>
            for i in range(len(tokens) - 1):
                # 取"前文"，最长 n-1 个字（不足就取全部）
                start = max(0, i - (self.n - 1) + 1)
                context = tuple(tokens[start:i + 1])   # 到当前位置为止的最近几个字
                nxt = tokens[i + 1]                    # 下一个字
                self.counts[context][nxt] += 1
                self.vocab.add(nxt)

    # ---------- 预测 ----------
    def next_token_distribution(self, context, temperature=1.0):
        """给定"前文"，返回一个概率分布（字典：token -> 概率）。

        temperature（温度）用来调节"随机程度"：
            温度越低，模型越爱选概率最高的字（更保守、更死板）；
            温度越高，模型越可能选一些不太常见的字（更大胆、更发散）。
        """
        probs = {}
        # 回退（backoff）：如果没统计到"前文"，就砍掉最老的一个字再试。
        # 这相当于：没见过这个上下文，就退一步看更短的历史。
        for length in range(len(context), -1, -1):
            ctx = context[len(context) - length:]  # 取最近 length 个字
            counter = self.counts.get(ctx)
            if counter:
                total = sum(counter.values())
                for tok, cnt in counter.items():
                    probs[tok] = cnt / total
                break
        if not probs:
            # 完全没有统计（理论上不会发生），就均匀随机选一个词表里的字
            return {tok: 1.0 / len(self.vocab) for tok in self.vocab}

        # 用温度调整分布：每个概率取 (1/温度) 次方后再归一化。
        if temperature != 1.0:
            probs = {tok: p ** (1.0 / temperature) for tok, p in probs.items()}
            s = sum(probs.values())
            probs = {tok: p / s for tok, p in probs.items()}
        return probs

    def sample_next(self, context, temperature=1.0):
        """按概率分布随机抽取下一个字。"""
        probs = self.next_token_distribution(context, temperature)
        tokens = list(probs.keys())
        weights = [probs[t] for t in tokens]
        return random.choices(tokens, weights=weights)[0]

    # ---------- 生成 ----------
    def generate(self, seed="", max_len=40, temperature=0.8):
        """从 seed（开头几个字）开始，一个字一个字往下接，生成一句话。"""
        from tokenizer import BOS, EOS  # 局部导入，避免命名混淆

        if seed:
            result = list(seed)                    # 用用户给的开头
            context = result[-(self.n - 1):]       # 只保留最近 n-1 个字作为"前文"
        else:
            result = []                            # 没有开头，就从 <BOS> 开始
            context = [BOS]

        for _ in range(max_len):
            nxt = self.sample_next(tuple(context), temperature)
            if nxt == EOS:                         # 遇到句尾记号就停
                break
            result.append(nxt)
            context.append(nxt)
            # 让 context 只保留最近 n-1 个字
            context = context[-(self.n - 1):]
        return "".join(result)
