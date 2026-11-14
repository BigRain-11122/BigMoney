"""The CEO one-pager says 今日 while its own numbers were priced on another bar.

r1669..r1671 taught this question to the etf book page (`scripts/live_book_day_words.py`):
count the today-words a reader can actually see, then read every printed date against the
field its sentence quotes. That page is not the only paper the CEO opens. `docs/live_usage/
LIVE-*.md` prints **今日 +¥0（对比 2026-11-13）** on a Saturday: the reader's day has had no
session, and the number belongs to 2026-11-13. The same audit, on the second paper, is this
module.

Two questions, and they are not the same question:

  * **the date claim** -- "the sentence names a day; is that day the one the field carries?"
    Reuses `live_book_day_words._date_claims` verbatim (r1375 family: one implementation,
    two readers -- a second copy of the matcher is the defect that never gets fixed twice);
  * **the day word** -- "this sentence uses 今天/今日 to assert today's number; is the page's
    own day the day that number was priced on?" Only *value-claiming* today-words are
    judged. "今日尚未有 bar" and "今日 09:15 起随源点亮" are the honest forms -- they say the
    reader's day has nothing yet -- and are counted as honest, never as offenders.

Verdicts, none of which is interchangeable:

  * PRINTED_DATES_AGREE      -- every printed date matches its field and no today-word borrows
                                a day it does not have;
  * PRINTED_DATE_MISMATCH    -- a printed date disagrees with the field its sentence quotes;
  * DAY_WORD_ON_STALE_PAGE   -- a today-word asserts a number that was priced on another bar
                                (named with both days);
  * PRINTED_SELF_DATED       -- dates are present but some are unmapped/unverifiable: not
                                green, the audit simply cannot say;
  * PRINTED_BUT_UNANCHORED   -- the paper carries day words the rules cannot read at all;
  * UNVERIFIED_PRINTED_FACE  -- the paper could not be read ("could not check" is never clean).

Exit codes: 0 green, 1 a named debt, 2 the artifact cannot be read.

Usage:
    python scripts/live_usage_day_words.py run
    python scripts/live_usage_day_words.py check
    python scripts/live_usage_day_words.py --selftest
"""
from __future__ import annotations

import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from scripts import live_book_day_words as LBW  # noqa: E402  (shared matcher, one copy)

JSON_FACE = os.path.join(ROOT, "docs", "live_usage", "LIVE-latest.json")
PAGE_FACE = os.path.join(ROOT, "docs", "live_usage", "LIVE-latest.md")
FACE = os.path.join(ROOT, "results", "live_usage_day_words.json")

_D = r"(20\d{2}-\d{2}-\d{2})"
# Each rule anchors one sentence of this page to the field that issued it. A printed date no
# rule claims stays `unmapped` and blocks the green (r1671: unmapped is a debt, not a pass).
CLAIM_RULES = [
    (re.compile(r"^# CEO 实盘使用一页纸 · " + _D), ["day"]),
    (re.compile(r"自动生成 " + _D), ["generated"]),
    (re.compile(r"最后必须已有 bar 的会话是 \*\*" + _D + r"\*\*"), ["freshness.expected_bar"]),
    (re.compile(r"⑥ ETF 复合书：截至 \*\*" + _D + r"\*\*"), ["etf_book.last_bar"]),
    (re.compile(r"③ 风险带（zt 四面板）：截至 \*\*" + _D + r"\*\*"), ["risk_tape.cutoff"]),
    (re.compile(r"① 市场政体态：截至 \*\*" + _D + r"\*\*"), ["market.asof"]),
    (re.compile(r"定价面板尾 bar：\*\*" + _D + r"\*\*"), ["freshness.book_panel_last_bar"]),
    (re.compile(r"当前政体态：RED\*\*.*· asof " + _D), ["market.asof"]),
    (re.compile(r"`RED_COOL`（asof " + _D + r"）"), ["market.clock_asof"]),
    (re.compile(r"截止 " + _D + " · 涨停池"), ["risk_tape.cutoff"]),
    (re.compile(r"杀跌日（bar " + _D + r"）"), ["risk_tape.cutoff"]),
    (re.compile(r"较 " + _D + " 收盘"), ["freshness.expected_bar"]),
    (re.compile(r"今日 [+\-−]?¥[\d,]+（对比 " + _D + r"）"), ["rollup.day_prior"]),
    (re.compile(r"\*\*账本\*\*：" + _D + " 播种"), ["etf_book.first_bar"]),
    (re.compile(r"\*\*账本\*\*：2026-10-23 播种 → " + _D), ["etf_book.last_bar"]),
    (re.compile(r"top-10 名义持仓.*?证据截至 " + _D), ["national_team.s2_evidence_cutoff"]),
    (re.compile(r"EXODUS 段：.*?证据截至 " + _D), ["national_team.s3_evidence_cutoff"]),
    (re.compile(r"日历在册最后一日 " + _D), ["freshness.calendar_last"]),
    (re.compile(r"结论：全部面都追到 " + _D), ["freshness.expected_bar"]),
    (re.compile(r"（as_of " + _D + "·RESEARCH_READOUT"), ["recommendation.as_of"]),
    (re.compile(r"入场 " + _D + "·单边换手"), ["recommendation.entry_date"]),
    (re.compile(r"账本 \d+ 名 · k [\d.]+ · vol_target [\d.]+% · 决策 bar " + _D),
     ["book_identity.ledger.bar"]),
    (re.compile(r"执行单 \d+ 名 · k [\d.]+ · beta_target [\d.]+ · 决策 bar " + _D),
     ["book_identity.ticket.bar"]),
    (re.compile(r"未定稿 bar：" + _D), ["etf_book.provisional_bars[0]"]),
]

# Dates that are rule constants, not data claims: 月界（2026-10-01）is when a gate opens, and
# no field can disagree with it. They are counted and printed separately -- a policy date that
# quietly joined the pass bucket would be the "unmapped becomes green" defect (r1671).
POLICY_RULES = [
    re.compile(r"月界（" + _D + "）"),
]

# Only sentences that assert a number about the reader's own day. `honest` marks the forms
# that say the day has nothing yet -- those are the cure, not the disease.
DAY_CLAIM_RULES = [
    (re.compile(r"今日 [+\-−]?¥[\d,]+"), "rollup.day_pnl_cny", "asserts today's P&L"),
    (re.compile(r"今日 \*\*未判\*\*"), "risk_tape.kill_day_unavailable", "asserts today's read"),
    (re.compile(r"杀跌日，今日 (是|否)"), "risk_tape.kill_day", "asserts today's session"),
]
DAY_HONEST_RULES = [
    re.compile(r"今日尚未有 ?bar"),
    re.compile(r"今日 09:15 起随源点亮"),
]

CLEAN = ("PRINTED_DATES_AGREE",)


def _printed_rows(text):
    """Every printed line under its heading -- the date audit reads all of them.

    `live_book_day_words._printed_census` keeps only today-word lines because there the two
    questions sit on the same sentences. Here they do not: the one-pager prints 23 dates and
    only 5 of them are near a today-word, so reusing that row filter would audit 5 of 23 and
    call the rest unmapped -- a face that measures the wrong paper (E240 family).
    """
    rows, heading = [], "(页首)"
    for line in (text or "").split("\n"):
        if line.startswith("## "):
            heading = line[3:].strip()[:46]
        if not line.strip():
            continue
        rows.append({"heading": heading, "line": line.strip()[:400],
                     "self_dated": bool(LBW.DATE_IN_TEXT.search(line))})
    return rows


def _day_word_rows(rows):
    return [r for r in rows if any(w in (r.get("line") or "") for w in LBW.DAY_WORDS)]


def _day_claims(rows, page_day, bar_day):
    """Value-claiming today-words, each read against the day the page's own bar falls on."""
    claims, offenders, honest = [], [], []
    for row in rows or []:
        line = row.get("line") or ""
        if any(p.search(line) for p in DAY_HONEST_RULES):
            honest.append({"heading": row.get("heading"), "line": line[:140]})
            continue
        for pat, field, why in DAY_CLAIM_RULES:
            if not pat.search(line):
                continue
            stale = bool(page_day and bar_day and page_day != bar_day)
            rec = {"heading": row.get("heading"), "field": field, "why": why,
                   "page_day": page_day, "bar_day": bar_day,
                   "reading": "stale_day" if stale else "same_day",
                   "line": line[:160]}
            claims.append(rec)
            if stale:
                offenders.append(rec)
            break
    return {"n_claims": len(claims), "n_stale": len(offenders),
            "n_honest_forms": len(honest), "claims": claims[:20],
            "offenders": offenders[:20], "honest": honest[:10]}


def census(doc, printed):
    """Two papers, two questions: the printed dates, and the day words that assert a number."""
    ret = {"artifact": None, "page_day": None, "bar_day": None, "verdict": "UNREADABLE",
           "sentence": "", "printed": {"state": "not_measured"},
           "date_claims": {"state": "not_measured"}, "day_claims": {"state": "not_measured"}}
    if not isinstance(doc, dict) or not doc:
        ret["sentence"] = "一页纸的 JSON 读不出来——这不是「没有日词」，是没法核验。"
        return ret
    ret["page_day"] = str(doc.get("day") or "")[:10] or None
    ret["bar_day"] = str((doc.get("freshness") or {}).get("expected_bar") or "")[:10] or None
    if printed is None:
        ret["printed"] = {"state": "unreadable"}
        ret["verdict"] = "UNVERIFIED_PRINTED_FACE"
        ret["sentence"] = ("一页纸的印刷面读不出来（只读到 JSON）——「没核到」不等于「没问题」，"
                           "所以这一面不给绿。")
        return ret
    rows = _printed_rows(printed)
    day_rows = _day_word_rows(rows)
    honest_rows = [r for r in day_rows
                   if any(p.search(r.get("line") or "") for p in DAY_HONEST_RULES)]
    debt_rows = [r for r in day_rows if r not in honest_rows]
    heads = []
    for r in rows:
        if r["heading"] not in heads:
            heads.append(r["heading"])
    undated = [r for r in debt_rows if not r["self_dated"]]
    pr = {"state": "ok", "n_lines": len(day_rows), "n_all_lines": len(rows),
          "n_headings": len(heads), "n_honest": len(honest_rows),
          "n_self_dated": len(debt_rows) - len(undated),
          "n_undated": len(undated), "undated": undated[:40],
          "headings": heads[:12], "rows": rows}
    ret["printed"] = pr
    ret["date_claims"] = LBW._date_claims(rows, doc, rules=CLAIM_RULES)
    policy = []
    if ret["date_claims"].get("unmapped"):
        keep = []
        for r in ret["date_claims"]["unmapped"]:
            if any(p.search(r.get("line") or "") for p in POLICY_RULES):
                policy.append(r)
            else:
                keep.append(r)
        ret["date_claims"]["unmapped"] = keep
        ret["date_claims"]["n_unmapped"] = len(keep)
    ret["date_claims"]["n_policy"] = len(policy)
    ret["date_claims"]["policy"] = policy
    ret["day_claims"] = _day_claims(day_rows, ret["page_day"], ret["bar_day"])
    dc, dy = ret["date_claims"], ret["day_claims"]
    if dc.get("n_mismatch"):
        ret["verdict"] = "PRINTED_DATE_MISMATCH"
    elif dy.get("n_stale"):
        ret["verdict"] = "DAY_WORD_ON_STALE_PAGE"
    elif pr.get("n_undated"):
        # a today-word that names no day at all is the reader-facing debt, and it comes
        # before any date-rule gap: "有人读不出这一天" outranks "这一处我还没规则可核".
        ret["verdict"] = "PRINTED_BUT_UNANCHORED"
    elif (dc.get("n_claims") and not dc.get("n_unmapped") and not dc.get("n_unverifiable")
          and dc.get("n_ok") == dc.get("n_claims")):
        ret["verdict"] = "PRINTED_DATES_AGREE"
    else:
        ret["verdict"] = "PRINTED_SELF_DATED"
    ret["sentence"] = sentence(ret)
    return ret


def sentence(c):
    pr, dc, dy = c.get("printed") or {}, c.get("date_claims") or {}, c.get("day_claims") or {}
    if c["verdict"] == "PRINTED_DATE_MISMATCH":
        named = "；".join("「%s」里写 `%s`，而 %s 是 `%s`"
                         % (r["heading"], r["date"], r["field"], r["expected"])
                         for r in (dc.get("mismatches") or [])[:4])
        return ("**一页纸上 %d 处日期里，有 %d 处与它引用的那张面对不上**：%s。"
                % (dc.get("n_claims", 0), dc.get("n_mismatch", 0), named))
    if c["verdict"] == "DAY_WORD_ON_STALE_PAGE":
        named = "；".join("「%s」" % r["line"][:60] for r in (dy.get("offenders") or [])[:4])
        return ("**本页是 %s 的页面，可它拿「今天/今日」说的是 %s 那根 bar 的数**（%d 处）：%s。"
                "读者在 %s 打开这页，读到的是自己今天的数，而那张面停在 %s。"
                % (c.get("page_day") or "?", c.get("bar_day") or "?", dy.get("n_stale", 0),
                   named, c.get("page_day") or "?", c.get("bar_day") or "?"))
    if c["verdict"] == "PRINTED_DATES_AGREE":
        return ("**一页纸上 %d 处日期逐句对上了它引用的那张面**（%d 条规则，0 处判不了，"
                "0 处无规则可核）；日词 %d 行全部自带日期，其中 %d 处拿「今天」说数的地方"
                "落在本页自己的 bar（%s）上。这一面核的是「句子写的日子 == 那个字段写的日子」，"
                "不核那个字段本身对不对。"
                % (dc.get("n_claims", 0), dc.get("n_rules", 0), pr.get("n_lines", 0),
                   dy.get("n_claims", 0), c.get("bar_day") or "?"))
    if c["verdict"] == "PRINTED_SELF_DATED":
        return ("**一页纸上 %d 行日词都自带日期，但 %d 处日期没有规则可核 / %d 处字段缺失**——"
                "核不了的不算对上，这一面不给绿。"
                % (pr.get("n_lines", 0), dc.get("n_unmapped", 0), dc.get("n_unverifiable", 0)))
    if c["verdict"] == "PRINTED_BUT_UNANCHORED":
        return ("**一页纸上 %d 行日词、%d 行读不出是哪一天**——规则还没覆盖这些句子，"
                "所以这一面说不出它们对不对。"
                % (pr.get("n_lines", 0), pr.get("n_undated", 0)))
    return c["sentence"] or "**这一面没有结论**。"


def _read(json_face=JSON_FACE, page_face=PAGE_FACE):
    """(doc, printed, error). The page is read through the published pair, never a guess."""
    try:
        with open(json_face, "r", encoding="utf-8") as fh:
            doc = json.load(fh) or {}
    except (OSError, ValueError) as exc:
        return None, None, "%s: %s" % (type(exc).__name__, exc)
    printed = None
    try:
        with open(page_face, "r", encoding="utf-8") as fh:
            printed = fh.read()
    except (OSError, ValueError):
        printed = None
    return doc, printed, None


def run(out=FACE):
    doc, printed, err = _read()
    if err:
        print("LIVE_USAGE_DAY_WORDS_UNREADABLE %s" % err)
        return 2
    c = census(doc, printed)
    c["script"] = "live_usage_day_words"
    c["artifact"] = "docs/live_usage/LIVE-latest.json"
    c["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(c, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("%s | %s" % (c["verdict"], c["sentence"]))
    return 0 if c["verdict"] in CLEAN else 1


def check():
    doc, printed, err = _read()
    if err:
        print("CHECK_UNREADABLE %s" % err)
        return 2
    c = census(doc, printed)
    pr, dc, dy = c["printed"], c["date_claims"], c["day_claims"]
    print("verdict %s | page %s | bar %s | printed %s lines (self-dated %s / undated %s)"
          % (c["verdict"], c.get("page_day") or "?", c.get("bar_day") or "?",
             pr.get("n_lines", "-"), pr.get("n_self_dated", "-"), pr.get("n_undated", "-")))
    print("  DATES claims %s | ok %s | mismatch %s | unverifiable %s | unmapped %s | rules %s"
          % (dc.get("n_claims", "-"), dc.get("n_ok", "-"), dc.get("n_mismatch", "-"),
             dc.get("n_unverifiable", "-"), dc.get("n_unmapped", "-"), dc.get("n_rules", "-")))
    print("  DAYS  claims %s | stale %s | honest-forms %s"
          % (dy.get("n_claims", "-"), dy.get("n_stale", "-"), dy.get("n_honest_forms", "-")))
    for r in dc.get("mismatches") or []:
        print("  DATE-MISMATCH %s | printed %s | %s = %s"
              % (r["heading"], r["date"], r["field"], r["expected"]))
    for r in dc.get("unmapped") or []:
        print("  DATE-UNMAPPED %s | %s | %s" % (r["heading"], r["date"], r["line"][:80]))
    for r in dy.get("offenders") or []:
        print("  STALE-DAY %s | page %s vs bar %s | %s"
              % (r["heading"], r["page_day"], r["bar_day"], r["line"][:100]))
    for r in dy.get("honest") or []:
        print("  HONEST-DAY %s | %s" % (r["heading"], r["line"][:90]))
    print(c["sentence"])
    return 0 if c["verdict"] in CLEAN else 1


def selftest():
    total = ok = 0

    def leg(name, cond, detail=""):
        nonlocal total, ok
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s %s" % (name, detail))

    def doc(day="2026-11-14", bar="2026-11-13", prior="2026-11-13"):
        return {"day": day, "generated": day + "T10:56:48",
                "freshness": {"expected_bar": bar, "book_panel_last_bar": bar},
                "market": {"asof": bar, "clock_asof": bar},
                "risk_tape": {"cutoff": bar},
                "etf_book": {"last_bar": bar, "first_bar": "2026-10-23"},
                "rollup": {"day_prior": prior},
                "national_team": {"s2_evidence_cutoff": "2026-08-31",
                                  "s3_evidence_cutoff": "2026-09-24"}}

    def page(day="2026-11-14", bar="2026-11-13", prior="2026-11-13", amount="0"):
        return "\n".join([
            "# CEO 实盘使用一页纸 · " + day,
            "> 自动生成 " + day + "T10:56:48",
            "## ⓪ 本页新鲜度",
            "- 最后必须已有 bar 的会话是 **" + bar + "**",
            "  - ⑥ ETF 复合书：截至 **" + bar + "**",
            "  - ③ 风险带（zt 四面板）：截至 **" + bar + "**",
            "  - ① 市场政体态：截至 **" + bar + "**",
            "- 书的定价面板尾 bar：**" + bar + "**",
            "## ① 市场判定",
            "- **当前政体态：RED**（shadow 探测）· asof " + bar,
            "- **市场时钟**：`RED_COOL`（asof " + bar + "）",
            "- **市场风险面**：截止 " + bar + " · 涨停池 37 · 读法：跌停≥涨停 → 杀跌日，今日 否",
            "## ③ 六员分配",
            "- **六员合计**：今日 +¥" + amount + "（对比 " + prior + "）",
            "### 盘中档",
            "- 今日尚未有 bar（上一场收盘档·09:15 起随源点亮）",
            "  - 510050：上一场收盘 2.889（上一场收盘档（今日 09:15 起随源点亮））",
            "## ⑥ ETF 复合书",
            "- **账本**：2026-10-23 播种 → " + bar,
        ])

    # L1 a Saturday page whose P&L is priced on Friday is named with both days
    c = census(doc(), page())
    leg("L1 stale day word is an offender", c["verdict"] == "DAY_WORD_ON_STALE_PAGE", c["verdict"])
    leg("L1b sentence names both days",
        "2026-11-14" in c["sentence"] and "2026-11-13" in c["sentence"], c["sentence"][:80])
    leg("L1c the kill-day sentence is named too", c["day_claims"]["n_stale"] >= 1)

    # L2 the same page on a session day is green
    c2 = census(doc(day="2026-11-13", bar="2026-11-13", prior="2026-11-12"),
                page(day="2026-11-13", bar="2026-11-13", prior="2026-11-12", amount="1,234"))
    leg("L2 same day is green", c2["verdict"] == "PRINTED_DATES_AGREE",
        "%s claims=%s ok=%s unmapped=%s unverif=%s undated=%s fields=%s"
        % (c2["verdict"], c2["date_claims"].get("n_claims"), c2["date_claims"].get("n_ok"),
           c2["date_claims"].get("n_unmapped"), c2["date_claims"].get("n_unverifiable"),
           c2["printed"].get("n_undated"),
           [r["field"] for r in c2["date_claims"].get("claims") or []
            if r.get("reading") == "unverifiable"]))

    # L3 the honest forms are never offenders
    c3 = census(doc(), page())
    leg("L3 honest no-bar form counted apart", c3["day_claims"]["n_honest_forms"] >= 2,
        str(c3["day_claims"]["n_honest_forms"]))

    # L4 a printed date that disagrees with its field is a mismatch (both dates printed)
    bad = page().replace("定价面板尾 bar：**2026-11-13**", "定价面板尾 bar：**2026-11-12**")
    c4 = census(doc(), bad)
    leg("L4 date mismatch", c4["verdict"] == "PRINTED_DATE_MISMATCH", c4["verdict"])
    leg("L4b both dates printed", "2026-11-12" in c4["sentence"] and "2026-11-13" in c4["sentence"])

    # L5 an unreadable paper is never clean
    c5 = census(doc(), None)
    leg("L5 unreadable paper", c5["verdict"] == "UNVERIFIED_PRINTED_FACE", c5["verdict"])
    leg("L5b not in CLEAN", c5["verdict"] not in CLEAN)

    # L6 a date no rule claims blocks the green rather than counting as checked
    same = page(day="2026-11-13", bar="2026-11-13", prior="2026-11-12", amount="1,234")
    c6 = census(doc(day="2026-11-13", bar="2026-11-13", prior="2026-11-12"),
                same.replace("## ③ 六员分配", "## ③ 六员分配\n- 上个季度 2026-06-30 的读数"))
    leg("L6 unmapped date blocks green", c6["verdict"] == "PRINTED_SELF_DATED", c6["verdict"])
    leg("L6b unmapped counted", c6["date_claims"]["n_unmapped"] >= 1)

    # L7 the JSON missing is unreadable, not zero day words
    c7 = census({}, page())
    leg("L7 missing doc", c7["verdict"] == "UNREADABLE", c7["verdict"])

    # L7c a rule constant (月界) is counted apart and never counts as checked
    c7c = census(doc(day="2026-11-13", bar="2026-11-13", prior="2026-11-12"),
                 same + "\n- 公司自动实盘开闸=月界（2026-10-01）+CEO 唯一门")
    leg("L7c policy date keeps the page green", c7c["verdict"] == "PRINTED_DATES_AGREE",
        c7c["verdict"])
    leg("L7d policy date is counted, not checked",
        c7c["date_claims"].get("n_policy") == 1
        and c7c["date_claims"].get("n_claims") == c2["date_claims"].get("n_claims"),
        "policy=%s claims=%s vs base=%s" % (c7c["date_claims"].get("n_policy"),
                                            c7c["date_claims"].get("n_claims"),
                                            c2["date_claims"].get("n_claims")))

    # L8 the real published pair (whatever it says today) must be self-consistent to parse
    try:
        rdoc, rprinted, rerr = _read()
    except Exception as exc:  # pragma: no cover
        rdoc, rprinted, rerr = None, None, str(exc)
    leg("L8 live pair readable", rerr is None and isinstance(rdoc, dict), str(rerr))
    if rerr is None and rprinted is not None:
        live = census(rdoc, rprinted)
        leg("L8b live pair yields a verdict", live["verdict"] in (
            "PRINTED_DATES_AGREE", "PRINTED_DATE_MISMATCH", "DAY_WORD_ON_STALE_PAGE",
            "PRINTED_SELF_DATED", "PRINTED_BUT_UNANCHORED"), live["verdict"])

    print("live_usage_day_words selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    arg = (argv[1] if len(argv) > 1 else "run").strip()
    if arg in ("--selftest", "selftest"):
        return selftest()
    if arg == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
