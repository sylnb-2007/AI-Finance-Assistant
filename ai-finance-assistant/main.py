# -*- coding: utf-8 -*-
"""
main.py —— 程序入口：在命令行里和"AI 金融小助手"聊天。

运行方法（在项目文件夹里）：
    py main.py

聊天时可用的指令：
    输入问题         -> 机器人回答（优先查知识库，查不到就用模型生成）
    :gen 股票        -> 强制用语言模型，以"股票"开头生成一句话
    :temp 0.5        -> 调整生成温度（0.1~2.0，越低越保守，越高越大胆）
    :help            -> 显示帮助
    :quit 或 exit    -> 退出
"""

import os
import sys

# 编码处理（Windows 中文环境的常见坑）：
#  - 直接在命令行窗口运行时，Python 会自动用 Unicode 输出中文，无需处理；
#  - 如果把输出重定向到文件/管道，默认会按系统编码(GBK)写，可能乱码。
# 所以这里只在"输出被重定向"时才统一成 UTF-8，两种场景都能正确显示中文。
if not sys.stdout.isatty():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if not sys.stdin.isatty():
    try:
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

from chatbot import FinanceChatbot

BASE = os.path.dirname(os.path.abspath(__file__))
FAQ_PATH = os.path.join(BASE, "data", "finance_faq.json")
CORPUS_PATH = os.path.join(BASE, "data", "finance_corpus.txt")

WELCOME = """\
==================================================
  AI 金融小助手（简易大语言模型演示）
==================================================
  这是一个教学项目：用最简单的代码，演示大语言模型
  最核心的思想——"根据前文，预测下一个字"。

  · 问一个金融问题，我会先查知识库给出准确答案；
  · 查不到时，我会用语言模型"现场编"一段话给你看。

  输入 :help 查看全部指令，:quit 退出。
==================================================
"""

HELP = """\
可用指令：
  [直接输入问题]   例如：什么是复利 / 新手如何开始理财
  :gen 开头文字    让语言模型以指定文字开头生成一句话，例如 :gen 股票
  :temp 数值       设置生成温度（0.1~2.0），例如 :temp 1.2
  :help            显示本帮助
  :quit / exit     退出程序
"""


def main():
    print(WELCOME)
    bot = FinanceChatbot(FAQ_PATH, CORPUS_PATH)
    temperature = 0.8

    while True:
        try:
            raw = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if raw == "":
            continue
        if raw in (":quit", "exit", "quit"):
            print("再见！投资路上，慢慢来比较快。")
            break
        if raw == ":help":
            print(HELP)
            continue
        if raw.startswith(":temp"):
            parts = raw.split()
            if len(parts) == 2:
                try:
                    temperature = float(parts[1])
                    temperature = max(0.1, min(2.0, temperature))
                except ValueError:
                    pass
            print(f"当前生成温度：{temperature:.2f}（越低越保守，越高越大胆）")
            continue
        if raw.startswith(":gen"):
            seed = raw[4:].strip()
            text = bot.model.generate(seed=seed, max_len=40, temperature=temperature)
            print(f"助手（模型生成）：{text}")
            continue

        # 正常问答
        answer, mode = bot.answer(raw, temperature=temperature)
        tag = "知识库" if mode == "知识库" else "模型生成"
        print(f"助手（{tag}）：{answer}")


if __name__ == "__main__":
    main()
