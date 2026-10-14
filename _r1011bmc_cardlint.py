#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""card-lint.py - handover-card lint (MASTER-AGENT BLUEPRINT v2 sec.4 -> CEO-PROXY CHARTER sec.7)

Phase 1-beta-4 enforcement gate (O-20261014-1745): the nine-element handover card is
enforced by a mechanical lint, not by LLM self-discipline. Missing field = reject (打回).

Usage:
  python Tools/card-lint.py card.txt          # nine-element card (cross-machine / POOL card)
  python Tools/card-lint.py --min card.txt    # orders-row minimum set (5 elements)
  python Tools/card-lint.py --text "..."      # inline text instead of a file

Exit codes: 0 = pass; 2 = missing fields (打回, dispatch invalid); 1 = usage/IO error.
"""
import re
import sys

# (name, compiled regex, remediation hint)
FULL = [
    ("1 @机+lane",
     [re.compile(r"@\w+"), re.compile(r"lane|hq-central-night-gpu|cpu-sound|gpu-production")],
     "缺「@机+lane」：写 @bm-x + 车道名（bm-a=hq-central-night-gpu / bm-b=cpu-sound / bm-c=gpu-production）"),
    ("2 回执窗",
     [re.compile(r"回执窗|回执.{0,6}\d+\s*[hd日小]")],
     "缺「回执窗」：写硬窗时长（如 回执窗 24h）"),
    ("3 验收物+证据指针",
     [re.compile(r"验收物|验收")],
     "缺「验收物」：写产物路径+可核证据指针（commit/台账行/日志）"),
    ("4 spec 指针",
     [re.compile(r"spec\s*[:：=]|SPEC|规格|正典|cph4/[\w./-]+|Tools/[\w./\\-]+")],
     "缺「spec 指针」：写规格/正典路径（禁口述规格）"),
    ("5 溯源令号",
     [re.compile(r"O-20\d{6}(-\d+)?")],
     "缺「溯源令号」：写 O-YYYYMMDD-NNNN（orders 台账行）"),
    ("6 输入/输出",
     [re.compile(r"输入"), re.compile(r"输出")],
     "缺「输入/输出」：写输入件与输出件路径"),
    ("7 依赖",
     [re.compile(r"依赖")],
     "缺「依赖」：写上游卡/件（无依赖也要写「无依赖」）"),
    ("8 卡 ID",
     [re.compile(r"POOL-[A-Za-z0-9-]+")],
     "缺「卡 ID」：写 POOL-<序>（主AGENT 开卡时编制）"),
    ("9 provenance 三态",
     [re.compile(r"provenance|来源", re.I), re.compile(r"直述|转述|推断")],
     "缺「provenance 三态」：标 直述（CEO 原话）/转述（窗口转单）/推断（自驱派生）之一"),
]

MIN = ["1 @机+lane", "2 回执窗", "3 验收物+证据指针", "5 溯源令号"]


def main(argv):
    args = list(argv[1:])
    minimum = "--min" in args
    if minimum:
        args.remove("--min")
    text = None
    if "--text" in args:
        i = args.index("--text")
        if i + 1 >= len(args):
            print("usage: card-lint.py [--min] <file> | --text \"...\"")
            return 1
        text = args[i + 1]
    else:
        if not args:
            print("usage: card-lint.py [--min] <file> | --text \"...\"")
            return 1
        try:
            with open(args[0], "r", encoding="utf-8-sig") as f:
                text = f.read()
        except OSError as e:
            print("IO-ERROR: %s" % e)
            return 1

    checks = [c for c in FULL if (c[0] in MIN if minimum else True)]
    missing = []
    for name, pats, hint in checks:
        if all(p.search(text) is None for p in pats):
            missing.append((name, hint))

    if missing:
        print("CARD-LINT REJECT (%d missing):" % len(missing))
        for name, hint in missing:
            print("  - %s -> %s" % (name, hint))
        print("REJECT: dispatch invalid (CHARTER 7.1: nine-element card, missing field = reject)")
        return 2

    print("CARD-LINT PASS (%d/%d elements present%s)"
          % (len(checks), len(checks), ", --min row-level" if minimum else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
