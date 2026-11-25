#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2097 (bm-c): append the methodology card to knowledge/METHODOLOGY_ASSETS.md.

The card is about ruler admission: a spread that comes from a reading already refuted in
this repo is not uncertainty, and averaging it into a band is what makes a rate look
ruler-bound. Kept as a script so the append is reproducible and CJK-safe.
"""
from __future__ import annotations

import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "knowledge", "METHODOLOGY_ASSETS.md")

CARD = """
## E-20261125-r2097 判例：区间里的那把尺子可能已经被证伪——「宽」不等于「不确定」

r2094 把 carry 书按三把尺子折成钱，诚实报出 IC 2.76 / 9.65 / 9.68%（分歧 6.92pp），并拒绝挑一把，
判词写成 PAYS_ON_ITS_WORST_RULER_BUT_THE_RATE_IS_RULER_BOUND。r2096 随后证明移仓日的台阶是后付
（次日回吐 0.170/0.159，移仓后 8 日比前 8 日低 3.96/5.29pp，p=0.026/0.030）：把台阶记成当日收益的那把尺子
**不是最差的一把，而是错的一把**。于是 6.92pp 的「不确定性」里，6.89pp 来自一个已被本仓证伪的读数。

三条可复用：
①**区间先过准入，再谈宽窄**——凡「A/B/C 三个读数各报一个」的结论，必须问一句：这三个读数是并列的
可能世界，还是一个已经被别的面否掉了？把被否掉的读数平均进区间，会把「我算错了」伪装成「世界不确定」。
②**准入规则要落在常量上并被负控驱动**——本面把 `verdict == COST_BOOKED_BY_LATER_CARRY` 写成脚本常量，
负控里把 IC 的两把尺子改成 PARTIAL_REVERSAL，区间必须**整个消失**（不是变宽），这样规则才不是文风。
③**口径未定的品种不许报数**——IM 两把有样本的尺子给出不同**种类**的解释（部分回吐 p=0.607 / 真成本 p=0.421），
样本量早已过 min_pairs=30，所以「无可报数」是正确的输出，且必须同时印出「会改判的条件」并注明
`can_be_bought_with_capital: false`——加钱不动这道门。

第四问，本轮顺带立法：**先决次序要声明，不要发现**。会计 > 资本 > 流动性 > 下单：会计有争议的书不能写成
「资金到位即可下单」，否则读者会以为补钱就能解决，而实际要等的是那个读数自己变。

How：任何「按多个读数报区间」的面，下一轮必须回答两件事——哪些读数被采信、被拒的读数由谁的话拒的
（引用判词词面，不引用印象）；无采信读数时，输出「无可报数」并把改判条件连同数字一起印。
本判例正身 `scripts/idx_fut_carry_decision_face.py`（selftest 26/26）+ 负控
`results/_r2097bmc_decision_face_negative.py`（11/11 PASS）+ 面 `results/idx_fut_carry_decision_face.json`
+ 文档 `research/IDX_FUT_CARRY_DECISION_FACE.md` + QA `qa/decision-face-r2097.md`。
"""


def main():
    text = io.open(PATH, encoding="utf-8", newline="").read()
    if "E-20261125-r2097" in text:
        print("already present")
        return 0
    if not text.endswith("\n"):
        text += "\n"
    io.open(PATH, "w", encoding="utf-8", newline="").write(text + CARD)
    print("appended %d chars" % len(CARD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
