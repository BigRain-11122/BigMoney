#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The ticket menu is the one paper a reader acts on -- does it say which day it is for?

r1684 found the 2026-11-06 issue opening with "今天的票" over a book struck on 2026-10-14:
seventeen sessions of price drift, and nothing on the page said so. The generator now titles
the decision bar and prints the ticket's age, but the defect had already shipped in 17 files,
and a repair with no reader is a repair nobody can check (r1611: the fifth hand-fix must leave
a guard, not a sixth fix).

So this face reads the published papers and answers one question per file: does every
today-word sit on a line that carries its own date? It reads what is on disk; it does not
regenerate, and it does not know whether a printed date is the right one -- that is the
`live_book_day_words` question, asked there about the CEO page.

    python scripts/ticket_day_words.py run
    python scripts/ticket_day_words.py --selftest

Exit codes: 0 every ticket is dated, 1 at least one says 今天 without a date, 2 nothing readable.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from scripts.live_book_day_words import DATE_IN_TEXT  # noqa: E402  (one pattern, r1375)

DOC_GLOB = os.path.join(BASE, "docs", "live_book", "TICKET-MENU-*.md")
OUT = os.path.join(BASE, "results", "ticket_day_words.json")
TODAY_WORDS = ("今天", "今日", "今晚")
# the generator writes "决策日 2026-10-14 的票" in the title and "同一个决策日 **YYYY-MM-DD**"
# in the body; the old page carried the bar only in the body. Both spellings are the same claim.
DECIDED = re.compile(r"决策日 \*{0,2}(20\d{2}-\d{2}-\d{2})\*{0,2}")
AGE = re.compile(r"中间过了 (\d+) 个交易日")
LEFT = re.compile(r"还能用 \*\*(\d+) 个交易日\*\*")
SUPERSEDED = re.compile(r"\*\*(20\d{2}-\d{2}-\d{2})\*\* 那根 bar 就是下一个调仓日")


def audit_text(text, name=None):
    """One paper, read by the reader's question. Word-carrying lines keep their line number."""
    date_in_name = re.search(r"(20\d{2}-\d{2}-\d{2})", name or "")
    decided = DECIDED.search(text)
    hits, undated = [], []
    dec = decided.group(1) if decided else None
    for i, line in enumerate(text.splitlines(), 1):
        words = [w for w in TODAY_WORDS if w in line]
        if not words:
            continue
        d = DATE_IN_TEXT.search(line)
        # carrying *a* date is not the same as carrying the decision bar (r1664/r1684): the
        # 11-06 page said 今天 beside 2026-11-06 while the book was struck on 2026-10-14, so a
        # line dated with the page day still reads as "today's book" when it is three weeks old.
        anchored = bool(d) and (dec is None or d.group(1) == dec)
        rec = {"line": i, "words": words, "dated": bool(d),
               "date_on_line": d.group(1) if d else None,
               "anchored_to_decision_bar": anchored,
               "text": line.strip()[:160]}
        hits.append(rec)
        if not anchored:
            undated.append(rec)
    age = AGE.search(text)
    left = LEFT.search(text)
    sup = SUPERSEDED.search(text)
    row = {"file": name,
           "page_day": date_in_name.group(1) if date_in_name else None,
           "decided_at": dec,
           "ticket_age_td": int(age.group(1)) if age else None,
           "td_to_next_rebalance": int(left.group(1)) if left else None,
           "superseded_at": sup.group(1) if sup else None,
           "n_today_words": len(hits),
           "n_undated": len(undated),
           "undated": undated}
    row["verdict"] = ("TICKET_SAYS_TODAY" if undated
                      else ("TICKET_DATED" if hits or row["decided_at"] else "NO_DAY_WORDS"))
    return row


def run(pattern=DOC_GLOB):
    files = sorted(glob.glob(pattern))
    if not files:
        out = {"verdict": "UNREADABLE", "n_files": 0,
               "sentence": "盘上一张票都读不到——这不是「票面都干净」。", "rows": []}
    else:
        rows = []
        for p in files:
            try:
                with open(p, encoding="utf-8") as fh:
                    text = fh.read()
            except (OSError, ValueError) as exc:
                rows.append({"file": os.path.basename(p), "verdict": "UNREADABLE",
                             "error": "%s: %s" % (type(exc).__name__, exc)})
                continue
            rows.append(audit_text(text, os.path.basename(p)))
        bad = [r for r in rows if r.get("verdict") == "TICKET_SAYS_TODAY"]
        dated = [r for r in rows if r.get("verdict") == "TICKET_DATED"]
        unread = [r for r in rows if r.get("verdict") == "UNREADABLE"]
        out = {"n_files": len(files), "n_dated": len(dated), "n_says_today": len(bad),
               "n_unreadable": len(unread), "rows": rows,
               "generator_note": ("生成器自 r1684 起在标题写决策日、正文披露票龄与剩余交易日；"
                                  "这里读的是已发布的纸，历史票面按原样披露，不回改。"),
               "verdict": ("TICKETS_DATED" if not bad and not unread
                           else ("TICKET_SAYS_TODAY" if bad else "UNREADABLE"))}
        if bad:
            out["sentence"] = (
                "**%d 张票里有 %d 张用「今天」却没带日期**（其余 %d 张已把日子写进标题）：%s。"
                "票面是唯一拿来下单的纸，读者从句子读不出它算的是哪一天。"
                % (len(files), len(bad), len(dated),
                   "、".join("%s 共 %d 处" % (r["file"].replace("TICKET-MENU-", ""),
                                              r["n_undated"]) for r in bad[:6])
                   + ("…" if len(bad) > 6 else "")))
        elif unread:
            out["sentence"] = ("**有 %d 张票读不出来**——「没核到」不是「都干净」。"
                               % len(unread))
        else:
            out["sentence"] = ("**%d 张票全部把决策日写进了标题**，页面里没有不带日期的「今天/今日」。"
                               % len(files))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, OUT)
    print(out.get("sentence") or out["verdict"])
    print("wrote %s" % os.path.relpath(OUT, BASE))
    if out["verdict"] == "UNREADABLE":
        return 2
    return 1 if out["verdict"] == "TICKET_SAYS_TODAY" else 0


def selftest():
    fails = []

    def chk(name, cond):
        if not cond:
            fails.append(name)

    old = ("# 今天的票：四个风险档各买什么（2026-11-06）\n"
           "\n同一套引擎、同一个决策日 **2026-10-14**。\n"
           "> 把该档今天的权重摆回整段面板。\n")
    r = audit_text(old, "TICKET-MENU-2026-11-06.md")
    chk("L1 old page: title today-word has no date on its line", r["n_undated"] >= 1)
    chk("L2 old page: decided bar still read", r["decided_at"] == "2026-10-14")
    chk("L3 old page: verdict is the red one", r["verdict"] == "TICKET_SAYS_TODAY")

    new = ("# 决策日 2026-10-14 的票：四个风险档各买什么（页面 2026-11-06）\n"
           "\n> 价与权重都按 **2026-10-14** 的收盘算；这一页写于 **2026-11-06**，"
           "中间过了 17 个交易日。\n"
           "> 这份票还能用 **3 个交易日**。\n")
    r2 = audit_text(new, "TICKET-MENU-2026-11-06.md")
    chk("L4 new page: no today-word at all", r2["n_today_words"] == 0)
    chk("L5 new page: age and remaining read back", r2["ticket_age_td"] == 17
        and r2["td_to_next_rebalance"] == 3)
    chk("L6 new page: verdict is dated", r2["verdict"] == "TICKET_DATED")

    dated_word = "# 今天（2026-11-06）的票\n\n> 今天买这些。\n"
    r3 = audit_text(dated_word, "x.md")
    chk("L7 no decision bar: a dated line passes, the undated one still fails",
        r3["n_today_words"] == 2 and r3["n_undated"] == 1)

    wrong_day = ("# 今天的票（2026-11-06）\n\n同一个决策日 **2026-10-14**。\n")
    r5 = audit_text(wrong_day, "TICKET-MENU-2026-11-06.md")
    chk("L9 a line dated with the page day is not anchored to the decision bar",
        r5["n_undated"] == 1
        and r5["undated"][0]["date_on_line"] == "2026-11-06"
        and r5["undated"][0]["anchored_to_decision_bar"] is False)

    same_day = "# 今天（2026-10-14）的票\n\n同一个决策日 **2026-10-14**。\n"
    chk("L10 page day == decision day -> anchored",
        audit_text(same_day, "z.md")["n_undated"] == 0)

    sup = ("# 决策日 2026-10-14 的票\n\n"
           "> **这张票已经被换掉了**：**2026-11-11** 那根 bar 就是下一个调仓日。\n")
    r4 = audit_text(sup, "y.md")
    chk("L8 superseded bar is read", r4["superseded_at"] == "2026-11-11")

    empty = os.path.join(BASE, "results", "_selftest_ticket_gate")
    os.makedirs(empty, exist_ok=True)
    for stale in glob.glob(os.path.join(empty, "*.md")):
        os.remove(stale)
    if fails:
        print("ticket_day_words selftest FAIL %d/10: %s" % (len(fails), ", ".join(fails)))
        return 1
    print("ticket_day_words selftest 10/10 PASS")
    return 0


def main(argv):
    args = argv[1:]
    if "--selftest" in args:
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
