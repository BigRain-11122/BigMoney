#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""render research/PAGE_FMT_GUARD_V2.md from results/page_fmt_guard_v2.scan.json

The page is a derived face: every number in it comes from the scan JSON, so a re-scan that
moves a number cannot leave the page printing yesterday's figure (r1860).  `--check`
re-renders and compares byte for byte; editing a figure by hand turns it red.

Usage:
    python scripts/page_fmt_guard_v2_page.py --write
    python scripts/page_fmt_guard_v2_page.py --check
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FACE = os.path.join(ROOT, "results", "page_fmt_guard_v2.scan.json")
PAGE = os.path.join(ROOT, "research", "PAGE_FMT_GUARD_V2.md")

PCT2 = "%" + "%"   # the two-character sequence the defect leaves on a page


def load():
    if not os.path.exists(FACE):
        sys.stderr.write("STALE: face missing: %s -- run the scan first\n" % FACE)
        raise SystemExit(2)
    return json.load(io.open(FACE, encoding="utf-8"))


def bucket(face):
    reader, silent, syntax = [], [], []
    for h in face["hazards"]:
        if h["kind"] == "SYNTAX_ERROR":
            syntax.append(h)
        elif h.get("published_hits"):
            reader.append(h)
        else:
            silent.append(h)
    return reader, silent, syntax


def render(face):
    c = face["counts"]
    sup = c["suppressed"]
    v1 = face.get("v1_reference") or {}
    reader, silent, syntax = bucket(face)
    out = []
    a = out.append

    a("# 页面百分号闸第二轮：把「一半是误报」修成可查的账")
    a("")
    a("> 覆盖 `Tools/page_fmt_guard_v2.py`。它读第一轮闸（`Tools/page_fmt_guard.py`，r2111），")
    a("> 同一套规则只加三种压制，每种压制都有名字、有自己的自检夹具，并且被计数打印出来。")
    a("")
    a("面：`results/page_fmt_guard_v2.scan.json`（生成 %s）｜本页由 `scripts/page_fmt_guard_v2_page.py`"
      % face["generated"])
    a("渲染，正文数字全部取自那张面，手改一位即 `--check` 变红。")
    a("")

    a("## 这一轮压掉了什么")
    a("")
    a("第一轮把三类**正确代码**报成缺陷（r2112 抽读 20 条定谳）。三种压制各自是一条规则，不是一份名单：")
    a("")
    a("| 压制 | 计数 | 规则（凭什么放过） |")
    a("|---|---:|---|")
    a("| 侦测器字面量 | %d | 整个值就是两个百分号；或它是比较运算的操作数（`assert \"1.21%s\" not in md`）；或最近的一次调用写进 `bad/err/issues/problems/fail/warn/note/diag/alerts/violations` 之一 |"
      % (sup.get("DETECTOR_LITERAL", 0), PCT2))
    a("| 映射转换 | %d | 引发告警的 `%%` 开的是合法的 `%%(name)s` 映射转换 |" % sup.get("MAPPING_FORMAT", 0))
    a("| 省略位数精度 | %d | 引发告警的是 `%%.f` / `%%0.f`（精度不写数字），Python 接受 |"
      % sup.get("RELAXED_PRECISION", 0))
    a("| 后来被格式化 | %d | 字面量绑给一个名字（或绑进名字里装着的容器），这个名字后来被 `名字 %% ...` 用掉，或在 for 循环里解包后其中一员被格式化 |"
      % sup.get("TEMPLATE_APPLIED_LATER", 0))
    a("")
    if v1.get("total") is not None:
        a("**净效果：第一轮 %d 条 → 本轮残差 %d 条，压掉 %d 条（= 上表之和 %d）。**"
          % (v1["total"], c["residue_total"], v1["total"] - c["residue_total"], c["suppressed_total"]))
        a("第一轮自己那份计数里还含本文件（夹具就是故意写坏的），已从对照里剔除：`%s`。"
          % ", ".join(v1.get("excluded") or []))
    a("")

    a("## 读者今天真的在读到的（%d 条，每条的页面名是搜出来的，不是猜的）" % len(reader))
    a("")
    a("判据：把该字面量开头的 24 个可读字符拿去 `research/` + `docs/` 的**已发布 markdown 全文**里搜，")
    a("搜到就把它引到那一页。也就是说下面每一条，读者打开那一页就能看见两个百分号。")
    a("")
    a("| 源文件:行 | 页面 |")
    a("|---|---|")
    for h in reader:
        a("| `%s:%s` | %s |" % (h["file"], h["line"], ", ".join("`%s`" % p for p in h["published_hits"])))
    a("")

    a("## 没有出现在任何已发布页面上的（%d 条，如实分组，不假装它们不存在）" % len(silent))
    a("")
    a("| 源文件:行 | 类型 | 为什么读者可能还没看见 |")
    a("|---|---|---|")
    for h in silent:
        why = ("机器面字符串：写进 JSON（心跳/结果面）而不是页面，读 JSON 的人会看见两个百分号"
               if h["file"].endswith("_r1684bmc_closeout.py") or "hedgeable_beta" in h["file"]
               else "页面写入器里的一行，但本次已发布页面里搜不到这句话——分支没跑到，或页面还没重生")
        if h["kind"] == "BARE_PCT_IN_FORMAT":
            why = ("真缺陷：这串要过 `%%` 运算，而 `%s` 后面跟的是全角分号，Python 会在渲染时抛 "
                   "ValueError（不是理论风险，是下一次跑 `--write` 就炸）" % h.get("offender", ""))
        a("| `%s:%s` | %s | %s |" % (h["file"], h["line"], h["kind"], why))
    a("")

    if syntax:
        a("## 与百分号无关、但共用同一条出生站的（%d 条）" % len(syntax))
        a("")
        for h in syntax:
            a("- `%s:%s` — 这个文件根本编译不了：%s" % (h["file"], h["line"], h["snippet"]))
        a("")

    a("## 还不接进链，因为残差还得先修")
    a("")
    a("本轮只证明「闸可以只报真缺陷」，没有把残差修掉：%d 条 = %d 条页面写入器里的字面量/非法转换"
      % (c["residue_total"], len(reader) + len(silent)))
    a("（其中 %d 条已印在读者的页面上）+ %d 条编译不了的文件。" % (len(reader), len(syntax)))
    a("修法只有一种——未格式化的串把两个百分号写回一个。这些脚本面都已提交、多为别窗所写，")
    a("竞争窗里禁改共享面（r1907），所以这一条留给独占窗。顺序应当是：先修残差，再把本闸接成")
    a("`Tools/s6_chain_bmc.py` 的 check-only 腿与 `smoke_test.py` 的一条腿；接早了就是一条常红腿（r1789）。")
    a("")

    a("## 这一面不回答什么")
    a("")
    a("- 参数个数/形状不匹配（`\"%(a)s\" % 1`、`\"%s %s\" % (a,)`）：要操作数才能判，本闸只看字面量；")
    a("- f-string 与 `.format()`：那边百分号是普通文本，两边判都会错，直接跳过并计数（本次跳过 f-string %d 个）；"
      % face["scope"]["fstrings_skipped"])
    a("- 不复核已发布页面本身是否还该印这个数：本闸只回答「这一串会不会原样漏到读者眼里」。")
    a("")
    return "\n".join(out) + "\n"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    face = load()
    text = render(face)
    if "--write" in argv:
        io.open(PAGE, "w", encoding="utf-8", newline="\n").write(text)
        print("wrote %s (%d bytes)" % (os.path.relpath(PAGE, ROOT), len(text.encode("utf-8"))))
        return 0
    if "--check" in argv:
        if not os.path.exists(PAGE):
            print("STALE: page missing: %s" % os.path.relpath(PAGE, ROOT))
            return 3
        have = io.open(PAGE, encoding="utf-8").read()
        if have != text:
            a, b = have.splitlines(), text.splitlines()
            for i in range(max(len(a), len(b))):
                x = a[i] if i < len(a) else "<missing>"
                y = b[i] if i < len(b) else "<missing>"
                if x != y:
                    print("CHECK FAILED: page differs from the face at line %d" % (i + 1))
                    print("  page: %s" % x[:120])
                    print("  face: %s" % y[:120])
                    return 3
            print("CHECK FAILED: page length differs")
            return 3
        print("CHECK_OK page matches the face byte for byte")
        return 0
    sys.stderr.write(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
