# -*- coding: utf-8 -*-
"""
make_pdfs.py —— 生成两份 PDF 手册：
  1) 使用手册.pdf  —— 怎么用这个项目
  2) 原理手册.pdf  —— 通俗讲解大语言模型原理

运行方法：  py make_pdfs.py
依赖：      pip install fpdf2
中文字体：  使用 Windows 自带的「黑体」(simhei.ttf)
"""

import os
from fpdf import FPDF

FONT_PATH = r"C:\Windows\Fonts\simhei.ttf"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# 主题色（金融感的深蓝色）
PRIMARY = (21, 60, 110)      # 深蓝
ACCENT = (196, 30, 58)       # 红色点缀
GRAY_BG = (245, 245, 245)    # 代码块浅灰底
TEXT = (30, 30, 30)


class Book(FPDF):
    """带中文换行、标题、代码块等样式的 PDF 辅助类。"""

    def __init__(self):
        super().__init__()
        self.add_font("hei", "", FONT_PATH)
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(18, 16, 18)
        self._body = 11      # 正文字号
        self._code = 9       # 代码字号
        self._width = 174    # 正文可用宽度(mm)

    # ---------- 基础排版 ----------
    def _wrap(self, text, width):
        """按字符逐个测量宽度，把长文本切成不超宽的行。"""
        lines = []
        for raw in text.split("\n"):
            line = ""
            for ch in raw:
                if self.get_string_width(line + ch) <= width:
                    line += ch
                else:
                    lines.append(line)
                    line = ch
            lines.append(line)
        return lines

    def _print_lines(self, lines, height, indent=0):
        """逐行输出（用于正文），可带首行缩进（只缩进第一行）。"""
        for i, ln in enumerate(lines):
            if i == 0 and indent:
                # 首行缩进：左边多让出 indent，宽度相应减小，避免右侧溢出
                self.set_x(self.l_margin + indent)
                self.cell(self._width - indent, height, ln, new_x="LMARGIN", new_y="NEXT")
            else:
                self.set_x(self.l_margin)
                self.cell(self._width, height, ln, new_x="LMARGIN", new_y="NEXT")

    # ---------- 元素 ----------
    def cover(self, text, sub=""):
        self.set_font("hei", "", 26)
        self.set_text_color(*PRIMARY)
        self.ln(6)
        self.cell(self._width, 14, text, new_x="LMARGIN", new_y="NEXT", align="C")
        if sub:
            self.set_font("hei", "", 12)
            self.set_text_color(120, 120, 120)
            self.cell(self._width, 8, sub, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_text_color(*TEXT)
        self.ln(4)

    def chapter(self, num, text):
        """一级标题（章）"""
        if self.get_y() > 240:
            self.add_page()
        self.ln(4)
        self.set_font("hei", "", 16)
        self.set_text_color(*PRIMARY)
        self.cell(self._width, 9, f"{num}　{text}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.l_margin + 40, self.get_y())
        self.ln(3)
        self.set_text_color(*TEXT)

    def section(self, text):
        """二级标题（节）"""
        self.ln(2)
        self.set_font("hei", "", 13)
        self.set_text_color(*PRIMARY)
        self.cell(self._width, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
        self.set_text_color(*TEXT)

    def para(self, text):
        """正文段落，首行缩进两个字。"""
        self.set_font("hei", "", self._body)
        self.set_text_color(*TEXT)
        lines = self._wrap(text, self._width)
        self._print_lines(lines, 6.2, indent=8)
        self.ln(2)

    def bullet(self, text, mark="·"):
        """项目符号条目。"""
        self.set_font("hei", "", self._body)
        self.set_text_color(*TEXT)
        lines = self._wrap(text, self._width - 8)
        for i, ln in enumerate(lines):
            prefix = mark + " " if i == 0 else "  "
            self.set_x(self.l_margin)
            self.cell(6, 6, prefix)
            self.cell(self._width - 8, 6, ln, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def code(self, text):
        """代码块：浅灰底、小字号、等宽感排版。"""
        self.set_font("hei", "", self._code)
        lines = self._wrap(text, self._width - 10)
        box_h = len(lines) * 4.6 + 4
        # 若当前页放不下整块，先换页
        if self.get_y() + box_h > self.h - 18:
            self.add_page()
        y0 = self.get_y()
        # 画背景
        self.set_fill_color(*GRAY_BG)
        self.rect(self.l_margin, y0, self._width, box_h, style="F")
        self.set_text_color(40, 40, 40)
        self.set_xy(self.l_margin + 5, y0 + 2)
        for ln in lines:
            self.cell(self._width - 10, 4.6, ln, new_x="LMARGIN", new_y="NEXT")
            self.set_x(self.l_margin + 5)
        self.set_y(y0 + box_h + 3)
        self.set_text_color(*TEXT)

    def note(self, text):
        """提示框：浅色强调。"""
        self.set_font("hei", "", self._body)
        lines = self._wrap(text, self._width - 10)
        box_h = len(lines) * 5.6 + 6
        if self.get_y() + box_h > self.h - 18:
            self.add_page()
        y0 = self.get_y()
        self.set_fill_color(235, 240, 248)
        self.rect(self.l_margin, y0, self._width, box_h, style="F")
        self.set_text_color(*PRIMARY)
        self.set_xy(self.l_margin + 5, y0 + 3)
        for ln in lines:
            self.cell(self._width - 10, 5.6, ln, new_x="LMARGIN", new_y="NEXT")
            self.set_x(self.l_margin + 5)
        self.set_y(y0 + box_h + 3)
        self.set_text_color(*TEXT)


# =====================================================================
# 使用手册
# =====================================================================
def build_user_manual():
    pdf = Book()
    pdf.add_page()

    pdf.cover("AI 金融小助手 · 使用手册", "一个零依赖、可复刻的迷你大语言模型（AI+金融）")

    pdf.note("先声明：这是一个用于学习大语言模型原理的教学项目，所有金融内容仅作知识科普，不构成任何投资建议。")

    # 1 简介
    pdf.chapter("1", "这是什么项目")
    pdf.para("AI 金融小助手是一个用纯 Python 写的迷你对话模型。它只有四个代码文件、两个数据文件，"
             "不需要安装任何第三方库（生成 PDF 手册的那个脚本除外），就能在你的电脑上跑起来。")
    pdf.para("它只做一件核心的事——演示大语言模型（LLM）最根本的思想：「根据前面已经出现的字，预测下一个字最可能是什么」。"
             "在金融这个方向下，我们让它既能回答金融知识问题，又能像真的模型一样「编」出金融味儿的句子。")

    # 2 环境要求
    pdf.chapter("2", "运行环境要求")
    pdf.bullet("Python 3.8 及以上版本（本项目在 3.14 上测试通过）。")
    pdf.bullet("Windows / macOS / Linux 均可，无需安装任何第三方库。")
    pdf.bullet("只需要会打开「命令行」（Windows 上叫 cmd 或 PowerShell 或终端）。")

    # 3 快速开始
    pdf.chapter("3", "三步快速开始")
    pdf.section("第 1 步：确认 Python 已安装")
    pdf.para("在命令行里输入下面这行并回车，如果显示出 Python 的版本号（形如 Python 3.14.0），就说明装好了：")
    pdf.code("py --version")
    pdf.para("如果提示「不是内部或外部命令」，说明还没装 Python。请到 python.org 下载安装，安装时一定勾选「Add Python to PATH」。")

    pdf.section("第 2 步：进入项目文件夹并运行")
    pdf.para("用命令行进入本项目的文件夹，然后运行：")
    pdf.code("py main.py")
    pdf.para("（如果 py 命令不可用，可换成 python main.py。）看到下面这样的欢迎界面，就说明启动成功了：")
    pdf.code("==================================================\n"
             "  AI 金融小助手（简易大语言模型演示）\n"
             "==================================================\n"
             "  输入 :help 查看全部指令，:quit 退出。")

    pdf.section("第 3 步：开始聊天")
    pdf.para("在「你：」后面直接输入一个金融问题，回车即可。比如：")
    pdf.code("你：什么是复利\n"
             "助手（知识库）：复利就是利滚利，利息也能继续产生利息。……\n"
             "你：新手如何开始理财\n"
             "助手（知识库）：新手建议：先留好应急资金，再学习基础知识……")

    # 4 两种回答模式
    pdf.chapter("4", "两种回答模式")
    pdf.para("这个机器人有两条「回答路径」，理解它们，你就理解了这个项目的一半。")
    pdf.section("模式一：知识库回答（检索式）")
    pdf.para("当你的问题能匹配到知识库里的某条问题时，机器人会直接把那条「现成答案」返回给你。"
             "比如问「什么是市盈率」，它就会给出预先写好的解释。这种方式答案准确、可靠，但只能回答知识库里有的内容。")
    pdf.section("模式二：模型生成（生成式）")
    pdf.para("当知识库里没有匹配的问题时，机器人会切换到「语言模型」模式，用 n-gram 模型现场编一段话。"
             "这正是大语言模型的核心玩法——不是背答案，而是根据学到的字词搭配规律，一个字一个字地「接龙」。")
    pdf.note("小技巧：生成的话常常语法通顺但内容有点怪，这是正常的，也是很好的学习素材。它说明统计模型学会了「字与字的搭配」，但还没真正「理解」含义。更多原理请看《原理手册.pdf》。")

    # 5 指令详解
    pdf.chapter("5", "指令详解")
    pdf.section("直接提问")
    pdf.para("输入任何问题即可。机器人会先尝试匹配知识库，匹配不到再走生成。提问时可以随意一点，比如：")
    pdf.code("什么是复利\n什么是市盈率 PE\n基金定投是什么\n新手怎么理财")

    pdf.section(":gen —— 强制生成")
    pdf.para("想跳过知识库、直接看语言模型「编」话，用 :gen 加上开头几个字：")
    pdf.code(":gen 股票\n:gen 复利\n:gen 投资")
    pdf.para("模型会以你给的字开头，一个字一个字往下接，直到遇到句尾或达到长度上限。开头字不同，编出来的内容就不同。")

    pdf.section(":temp —— 调整生成温度")
    pdf.para("「温度」(temperature) 控制生成时的随机程度，范围约 0.1 ~ 2.0：")
    pdf.bullet("温度越低（如 0.2）：模型越爱选概率最高的字，输出更保守、更死板，甚至重复。")
    pdf.bullet("温度越高（如 1.5）：模型越可能选冷门字，输出更大胆、更多样，但也更容易乱。")
    pdf.para("默认是 0.8。你可以试试：")
    pdf.code(":temp 0.3\n:temp 1.5")

    pdf.section(":help 与 :quit")
    pdf.code(":help       查看所有指令\n:quit       退出程序（也可以输入 exit 或 quit）")

    # 6 文件结构
    pdf.chapter("6", "项目文件结构")
    pdf.para("搞懂每个文件是干什么的，你就掌握了整个项目的骨架。")
    pdf.code("ai-finance-assistant/\n"
             "├── main.py             程序入口（交互聊天界面）\n"
             "├── chatbot.py          机器人逻辑（检索 + 生成）\n"
             "├── ngram_model.py      语言模型（统计预测下一个字）\n"
             "├── tokenizer.py        分词器（把句子切成 token）\n"
             "├── data/\n"
             "│   ├── finance_faq.json    金融知识库（问答对）\n"
             "│   └── finance_corpus.txt  金融语料（模型教材）\n"
             "├── make_pdfs.py       生成两份 PDF 手册的脚本\n"
             "├── 使用手册.pdf        本文件\n"
             "├── 原理手册.pdf        原理讲解\n"
             "└── README.md          项目说明")
    pdf.section("各文件职责")
    pdf.bullet("tokenizer.py：分词器。把句子切成一个个 token（记号）。中文按「字」切，连续的英文/数字合并成一个。")
    pdf.bullet("ngram_model.py：语言模型。统计「某几个字后面跟什么字、各出现几次」，预测时按这个概率抽下一个字。")
    pdf.bullet("chatbot.py：把知识库检索和语言模型生成组合起来，对外提供 answer() 方法。")
    pdf.bullet("main.py：命令行交互界面，负责读输入、调 chatbot、打印结果，还处理中文编码。")
    pdf.bullet("data/：两份数据——知识库（给出准确答案）+ 语料（训练语言模型）。")

    # 7 常见问题与排错
    pdf.chapter("7", "常见问题与排错")
    pdf.section("Q1：运行时中文乱码怎么办？")
    pdf.para("在 Windows 的 cmd/PowerShell 里直接运行 py main.py 一般不会乱码（Python 会自动用 Unicode 输出）。"
             "如果你用老旧终端遇到乱码，可尝试把终端字体换成支持中文的字体，或使用 Windows Terminal。")
    pdf.section("Q2：提示找不到 finance_faq.json？")
    pdf.para("请确保是在「项目根目录」下运行，即当前目录里能看到 main.py。程序是靠文件相对路径找数据的，"
             "不要只拷贝 main.py 到别处单独运行。")
    pdf.section("Q3：生成的句子完全看不懂？")
    pdf.para("这是正常的。这个迷你模型只学了 100 来句金融语料，能力极其有限，它的意义是「演示原理」而非「实用」。"
             "想让它编得更像样，就往 finance_corpus.txt 里多抄一些金融句子。")
    pdf.section("Q4：问的问题总匹配不到知识库？")
    pdf.para("可以试试换一个关键词更明确的问法。也可以自己往 finance_faq.json 里加问答，格式照抄已有条目即可。")

    # 8 动手改造
    pdf.chapter("8", "动手改造（强烈建议）")
    pdf.para("学习的最好方式是自己动手改。这里给三个由易到难的小任务：")
    pdf.bullet("任务 1：往 finance_faq.json 里加一条你自己的问答（比如「什么是杠杆」），重启程序试试。")
    pdf.bullet("任务 2：往 finance_corpus.txt 里加 10 句金融句子，再用 :gen 看生成有没有变好。")
    pdf.bullet("任务 3：打开 ngram_model.py，把 n 从 3 改成 2 或 4，观察生成结果的变化，想想为什么。")
    pdf.para("改完运行 py main.py 即可生效，无需重新安装任何东西——这正是这个项目「简单易复刻」的原因。")

    pdf.note("配套文档：《原理手册.pdf》会用大白话和类比，讲清楚这套代码背后的道理，建议一起阅读。")

    out = os.path.join(OUT_DIR, "使用手册.pdf")
    pdf.output(out)
    print("已生成：", out)


# =====================================================================
# 原理手册
# =====================================================================
def build_principles_manual():
    pdf = Book()
    pdf.add_page()

    pdf.cover("大语言模型原理手册", "用大白话和类比，讲懂「AI 为什么能对话」")

    pdf.note("本手册面向零基础读者，不需要任何编程或数学基础。读完它，你就能理解 ChatGPT 这类大语言模型最底层的思路。")

    # 1 一个直觉
    pdf.chapter("1", "先从一个直觉开始")
    pdf.para("你有没有用过手机输入法的「联想词」？你打一个「复」，输入法马上提示「利」「习」「杂」等候选字；"
             "你选了「利」，它又接着提示「息」「滚」……输入法之所以猜得准，是因为它见过海量的中文文本，"
             "统计出「复」后面最常跟哪个字。")
    pdf.para("大语言模型（LLM）的本质，就是一个「超级加强版的输入法联想」。它做的只有一件事："
             "根据前面已经出现的所有文字，预测「下一个字最可能是什么」。预测出来一个，就把这个字接上去，"
             "然后再预测下一个，如此循环，一句话、一段话就源源不断地「长」出来了。")
    pdf.note("一句话概括：语言模型 = 一台会「接龙」的机器。你给它开头，它一个字一个字地往下接。")

    # 2 第一步：切字
    pdf.chapter("2", "第一步：把句子切成小块（分词）")
    pdf.para("计算机不能像人一样直接「读」整句话，它需要先把文字切成一小块一小块，每一小块叫一个 token（记号）。"
             "这就像做菜前先把食材切成丁，或者搭乐高前先有一盒积木。")
    pdf.section("中文怎么切？")
    pdf.para("英文单词之间有空格，切起来容易；中文没有空格，最自然的切法就是「一个字一块」。"
             "所以「复利就是利滚利」会被切成 7 个小块：复、利、就、是、利、滚、利。"
             "数字和英文则连成整体，比如「2024」和「PE」各算一块。")
    pdf.section("再加两个特殊记号")
    pdf.para("我们还会在每句话的开头和结尾，分别加一个特殊记号 <BOS>（开头）和 <EOS>（结尾）。"
             "它们就像一句话的「起跑线」和「终点线」，让模型知道一句话从哪里开始、到哪里结束。")
    pdf.code("tokenize(\"复利就是利滚利\")\n"
             "-> ['复', '利', '就', '是', '利', '滚', '利']")

    # 3 第二步：数一数
    pdf.chapter("3", "第二步：统计「谁后面跟谁」")
    pdf.para("有了切成小块的一堆句子（这叫「语料」），模型要做的第二步是：数一数——"
             "在语料里，「复」这个字后面，出现「利」几次？出现「习」几次？……"
             "出现次数越多，我们就认为它「越可能」跟在后面。")
    pdf.section("一个具体例子")
    pdf.para("假设语料里有一句「复利就是利滚利」。模型会像这样统计（看「前一个字」预测「下一个字」）：")
    pdf.code("复 -> 利    （出现 1 次）\n"
             "利 -> 就    （出现 1 次）\n"
             "就 -> 是    （出现 1 次）\n"
             "是 -> 利    （出现 1 次）\n"
             "利 -> 滚    （出现 1 次）\n"
             "滚 -> 利    （出现 1 次）")
    pdf.para("如果把语料扩大成千上万句，「复」后面的「利」会一次次被数到，次数越来越多，"
             "于是模型就「学会」了：看到「复」，下一个最可能是「利」。")
    pdf.section("不只眼前一个字")
    pdf.para("只看着前一个字，太短视了。比如「利」后面可能跟「息」，也可能跟「滚」，到底跟哪个，取决于更前面的字。"
             "所以模型会多看几个字——看前两个字、前三个字……来决定下一个字。这种「看前 n-1 个字预测下一个字」的方法，"
             "就叫 n-gram（n 元语法）模型。n 越大，看得越远，但要统计的组合也越多。")
    pdf.note("本项目默认 n=3，也就是「看前面两个字，猜下一个字」。")

    # 4 第三步：掷骰子
    pdf.chapter("4", "第三步：按概率掷骰子（采样与温度）")
    pdf.para("统计完次数后，我们把「次数」换算成「概率」。比如「复」后面：利出现 100 次、习出现 20 次、杂出现 5 次，"
             "那么概率就是 利 80%、习 16%、杂 4%。")
    pdf.para("生成下一个字时，模型不是死板地永远选「利」，而是像掷一个「不均匀的骰子」："
             "骰子各个面的面积不一样，「利」那一面最大，被掷到的机会最高，但偶尔也会掷到「习」或「杂」。"
             "这种随机性，让每次生成的句子都略有不同，更像真人在说话。")
    pdf.section("「温度」是个什么旋钮？")
    pdf.para("温度（temperature）是控制这个骰子「有多不均匀」的旋钮：")
    pdf.bullet("温度低：骰子更极端，几乎总出「利」，输出保守、死板。")
    pdf.bullet("温度高：骰子更平均，冷门字也敢出，输出大胆、多样，但也更容易乱。")
    pdf.para("你在程序里输入 :temp 1.5，就是把温度调高，生成更天马行空；:temp 0.3 则让它更循规蹈矩。")

    # 5 对照本项目
    pdf.chapter("5", "对照本项目：代码到底做了什么")
    pdf.para("现在回头看这个项目的代码，会发现它正好就是上面三步，几乎没有多余的东西。")
    pdf.section("训练 = 数数")
    pdf.code("for sentence in corpus:\n"
             "    tokens = 切字(句子)\n"
             "    for 每个位置 i:\n"
             "        前文 = tokens[i-1], tokens[i]   # 前两个字\n"
             "        下一个 = tokens[i+1]\n"
             "        次数[前文][下一个] += 1          # 数一次")
    pdf.para("这一段就是「训练」——没有神经网络，没有 GPU，就是把语料从头到尾数一遍。")
    pdf.section("预测 = 查表 + 掷骰子")
    pdf.code("def 预测下一个字(前文, 温度):\n"
             "    概率表 = 把 次数[前文] 换算成概率\n"
             "    用温度调整概率的「均匀程度」\n"
             "    按概率随机抽一个 -> 下一个字")
    pdf.section("生成 = 循环接龙")
    pdf.code("result = \"复\"\n"
             "循环很多次:\n"
             "    下一个 = 预测下一个字(result 的最后两个字)\n"
             "    result += 下一个\n"
             "    遇到 <EOS> 就停\n"
             "输出 result")
    pdf.para("把这三段拼起来，就得到了一个能「说话」的模型。简单吧？这就是大语言模型的「最小可用版本」。")

    # 6 和真 GPT 差在哪
    pdf.chapter("6", "我们的小模型，和 ChatGPT 差在哪里？")
    pdf.para("思路完全一样——都是「预测下一个字」。差别在三个「量级」上。")
    pdf.section("差别一：数据量")
    pdf.para("我们的模型只读了约 100 句金融语料，像只读过一篇短文的小孩；ChatGPT 读的是互联网上几乎所有的文字，"
             "相当于把整个图书馆都读完了。读得越多，字与字的搭配规律就记得越全。")
    pdf.section("差别二：记忆方式")
    pdf.para("n-gram 是「死记硬背」：它只能记住「最近 2 个字后面跟什么」，一句话再长，它也只看眼前。"
             "而 ChatGPT 用神经网络（一种模仿大脑的数学结构）和「注意力机制」（能回头看整句话甚至整篇文章），"
             "把远距离的关联也抓住了。比如它能理解「小明把书送给小红」里的「把」和「送」隔得远，却是一对。")
    pdf.section("差别三：参数规模")
    pdf.para("我们模型的「知识」就是一张统计表，几万个数；ChatGPT 的神经网络里有上千亿个可调节的「旋钮」（叫参数），"
             "能表达极其复杂的规律。规模大了，才会涌现出理解、推理、甚至「创造力」。")
    pdf.note("打个比方：n-gram 像是「背熟了一本词语搭配词典」，而 GPT 像是「读遍天下书、还懂得举一反三的学霸」。"
             "但两者追根究底，都在做同一件事——预测下一个字。")

    # 7 为什么预测下一个字 = 智能
    pdf.chapter("7", "为什么「预测下一个字」能产生智能？")
    pdf.para("你可能会怀疑：就预测一个字，凭什么叫「智能」？关键在于——要把下一个字预测得准，模型被迫要学会理解。")
    pdf.bullet("要接对「1+1=__」，它得会算术；")
    pdf.bullet("要接对「北京是中国的__」，它得懂常识；")
    pdf.bullet("要接对「这篇文章的中心思想是__」，它得会阅读和理解；")
    pdf.bullet("要接对「推荐一个适合定投的__」，它得懂金融知识。")
    pdf.para("所以，「预测下一个字」这个看似简单的任务，其实是一个「逼着模型变聪明」的终极考试。"
             "模型为了考高分，不得不把语言、知识、逻辑都内化进去。这就是大语言模型如此强大的根本原因。")

    # 8 AI+金融
    pdf.chapter("8", "AI 在金融领域能做什么？")
    pdf.para("把「预测下一个字」的能力放到金融方向，就有了很多真实应用，我们这个项目只是其中最小的一角。")
    pdf.bullet("智能客服/投教助手：像本项目一样，回答股票、基金、理财等常见问题。")
    pdf.bullet("研报与资讯生成：根据数据自动撰写财报解读、市场点评。")
    pdf.bullet("舆情与情绪分析：从新闻、社交文本里判断市场情绪是乐观还是悲观。")
    pdf.bullet("风险提示：结合规则，提示投资者注意杠杆、止损、仓位等风险。")
    pdf.bullet("知识抽取：从海量公告、合同里自动提取关键信息。")
    pdf.note("重要提醒：语言模型会「一本正经地编」，在金融这种高风险场景，AI 只能当辅助，不能代替人做投资决策。")

    # 9 总结
    pdf.chapter("9", "总结：一张图看懂")
    pdf.para("整个大语言模型的逻辑，可以用一条流水线概括：")
    pdf.code("大量文字(语料)\n"
             "   │  切字\n"
             "   ▼\n"
             "一串 token\n"
             "   │  统计「谁后面跟谁」\n"
             "   ▼\n"
             "概率表（或神经网络）\n"
             "   │  掷骰子选下一个字\n"
             "   ▼\n"
             "一个字一个字接下去 -> 一段话")
    pdf.para("记住这五个关键词，你就入门了：")
    pdf.bullet("token：被切碎的文字小块；")
    pdf.bullet("语料：给模型「读」的大量文字；")
    pdf.bullet("训练：统计规律、调整参数的过程；")
    pdf.bullet("采样：按概率随机选下一个字；")
    pdf.bullet("温度：控制随机程度的旋钮。")

    # 10 亲手实验
    pdf.chapter("10", "给你留一个亲手实验")
    pdf.para("读完原理，建议回到程序里做这几个实验，把「纸上原理」变成「亲眼所见」：")
    pdf.bullet("实验 1：把 :temp 从 0.2 调到 1.8，感受输出从「死板」到「乱来」的变化——这就是温度。")
    pdf.bullet("实验 2：往 finance_corpus.txt 里加 10 句金融句子，重启后再 :gen，看输出是否更像样——这就是数据的力量。")
    pdf.bullet("实验 3：把 ngram_model.py 里的 n 改小（2）再改大（4），观察变化——这就是「看多远」的权衡。")
    pdf.para("做完这三个实验，你不仅听懂了原理，还亲手验证了原理。祝你学习顺利！")

    out = os.path.join(OUT_DIR, "原理手册.pdf")
    pdf.output(out)
    print("已生成：", out)


if __name__ == "__main__":
    build_user_manual()
    build_principles_manual()
    print("全部完成。")
