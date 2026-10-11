# -*- coding: utf-8 -*-
"""
tokenizer.py —— 极简分词器

大语言模型（LLM）并不直接"看懂"文字，而是先把文字切成一小块一小块，
每一小块叫做一个 token（记号）。模型实际上是在处理一串 token。

中文没有空格，最自然的切法就是"按字切分"：
    每个汉字 = 一个 token；
    连续的数字或英文 = 合并成一个 token（比如 "GDP"、"2024" 保持完整）。

这样代码极简、零依赖，同时真实体现了"分词"这一步在做什么。
"""

# 两个特殊记号：
#   <BOS> 表示"句子的开头"（begin of sentence）
#   <EOS> 表示"句子的结尾"（end of sentence）
BOS = "<BOS>"
EOS = "<EOS>"


def tokenize(text):
    """把一段文字切成 token 列表。

    例子：
        tokenize("复利就是利滚利")
        -> ['复', '利', '就', '是', '利', '滚', '利']

        tokenize("ROE 是净资产收益率")
        -> ['ROE', '是', '净', '资', '产', '收', '益', '率']
    """
    tokens = []
    buf = ""  # 临时存放"连续的英文/数字"
    for ch in text:
        # 如果是英文字母或数字，先攒进 buf，直到遇到其它字符
        if ch.isascii() and ch.isalnum():
            buf += ch
        else:
            # 遇到非英文/数字字符，先把攒好的 buf 作为一个 token 放进去
            if buf:
                tokens.append(buf)
                buf = ""
            # 空格直接跳过，其它字符（汉字、标点等）各算一个 token
            if not ch.isspace():
                tokens.append(ch)
    if buf:
        tokens.append(buf)
    return tokens


def tokenize_sentence(text):
    """把一句话切成 token，并加上 <BOS> 开头、<EOS> 结尾。

    加上这两个记号，是为了让模型"知道"一句话从哪里开始、到哪里结束。
    """
    return [BOS] + tokenize(text) + [EOS]
