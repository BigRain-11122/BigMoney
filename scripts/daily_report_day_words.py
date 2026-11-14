"""The third paper the CEO opens: the daily report prints 67 dates and 7 day words.

r1669..r1673 taught this question to the ETF book page and then to the one-pager. This is
`docs/daily_report/REPORT-*.md`, the longest of the three, and the one where "which day is this
number from" is asked hardest: on Saturday 2026-11-14 the paper printed 「今日 否」 for the
kill-day reading and 「今天：不动」 for the book, while every number behind those sentences came
from the 2026-11-13 bar.

Three questions, and they are not the same question:

  * **the date claim** -- "the sentence names a day; is it the day the field it quotes carries?"
    Reuses `live_book_day_words._date_claims` (one matcher, three readers);
  * **the foreign date** -- "is this day on the twin JSON at all?" The paper prints decision-log
    rows, a ten-day series table, silence timestamps and machine sample times. Writing 67 rules
    would be one rule per sentence and still miss tomorrow's; instead every printed date no
    rule claims must at least appear among the twin's own date values (`member_of_twin`), or be
    a task id / a stated policy date. A date that is none of those is foreign and blocking.
  * **the day word** -- "does this sentence assert today's number with a bar that is not today?"
    Per-sentence bars, because this paper mixes them: §六's floor-compliance count is about the
    report day itself, §九/§十二 are about the last bar.

Verdicts, none interchangeable:

  * PRINTED_DATES_AGREE      -- every claimed date matches its field, no foreign date, no day
                                word on another bar, no undated day word;
  * PRINTED_DATE_MISMATCH    -- a claimed date disagrees with the field its sentence quotes;
  * DAY_WORD_ON_STALE_PAGE   -- a day word asserts a number priced on another bar (both named);
  * PRINTED_BUT_UNANCHORED   -- the paper carries day words with no date at all;
  * PRINTED_DATE_FOREIGN     -- a printed date the twin JSON does not contain (named);
  * PRINTED_SELF_DATED       -- dates are present but some are unmapped/unverifiable: not green;
  * UNVERIFIED_PRINTED_FACE  -- the paper could not be read ("could not check" is never clean).

Exit codes: 0 green, 1 a named debt, 2 the artifact cannot be read.

Usage:
    python scripts/daily_report_day_words.py run
    python scripts/daily_report_day_words.py check
    python scripts/daily_report_day_words.py --selftest
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

from scripts import live_book_day_words as LBW      # noqa: E402  (date matcher, one copy)
from scripts import live_usage_day_words as LUW     # noqa: E402  (printed-row reader, one copy)

OUT_DIR = os.path.join(ROOT, "docs", "daily_report")
FACE = os.path.join(ROOT, "results", "daily_report_day_words.json")
CLEAN = ("PRINTED_DATES_AGREE",)

_D = r"(20\d{2}-\d{2}-\d{2})"
# One rule per sentence that quotes a field of the twin JSON. Anything not claimed here must
# still pass the membership test below; the two together are why this leg can cover a 67-date
# paper without 67 hand-written rules.
CLAIM_RULES = [
    (re.compile(r"^# 每日战报 — " + _D), ["report_date"]),
    (re.compile(r"^> 生成 " + _D), ["generated_at"]),
    (re.compile(r"\*\*市场时钟\*\*：`[A-Z_]+`（asof " + _D + r"）"), ["combat.market_clock.asof"]),
    (re.compile(r"在册交易员\*\*（\d+ 员 · marks " + _D + r"）"), ["combat.marks_asof"]),
    (re.compile(r"LIVE-" + _D), ["live_usage.day"]),
    (re.compile(r"\*\*纸盘六员\*\*（asof " + _D + r" · 前值 " + _D + r"）"),
     ["pnl_attribution.paper6.asof", "pnl_attribution.paper6.prior"]),
    (re.compile(r"面板 marks asof=" + _D), ["pnl_attribution.asof"]),
    (re.compile(r"\*\*AGGR 进攻族\*\*（\d+ 账户 · asof " + _D),
     ["pnl_attribution.families[0].asof"]),
    (re.compile(r"\*\*ALLOC 配置族\*\*（\d+ 账户 · asof " + _D),
     ["pnl_attribution.families[1].asof"]),
    (re.compile(r"\*\*GRID 网格族\*\*（\d+ 账户 · asof " + _D),
     ["pnl_attribution.families[2].asof"]),
    (re.compile(r"\*\*SYSV1 路由族\*\*（\d+ 账户 · asof " + _D),
     ["pnl_attribution.families[3].asof"]),
    (re.compile(r"\*\*证据截止\*\* " + _D + r" · 窗 " + _D + r"\.\." + _D),
     ["stage_style.cutoff", "stage_style.window.lo", "stage_style.window.hi"]),
    (re.compile(r"截止日：四面同为 \*\*" + _D + r"\*\*"), ["market_risk.cutoff"]),
    (re.compile(r"\*\*定价日 " + _D + r"\*\*（决策 " + _D + r"）· 下一次调仓 " + _D),
     ["etf_book.priced_bar", "etf_book.book_decided_at", "etf_book.next_rebalance_date"]),
    (re.compile(r"前向账本 \d+ 根 bar（" + _D + "→" + _D + r"）"),
     ["etf_book.forward.inception", "etf_book.forward.as_of"]),
    (re.compile(r"对「四只等权」[\d.]+ pp（bar " + _D + r"）"), ["etf_book.priced_bar"]),
    (re.compile(r"块重抽 \d+ 次，截止 " + _D), ["etf_book.envelope.evidence_cutoff"]),
    (re.compile(r"账本 \d+ 名 · k [\d.]+ · vol_target [\d.]+% · 决策 bar " + _D),
     ["book_identity.ledger.bar"]),
    (re.compile(r"执行单 \d+ 名 · k [\d.]+ · beta_target [\d.]+ · 决策 bar " + _D),
     ["book_identity.ticket.bar"]),
    (re.compile(r"· 板面 " + _D + "T"), ["lane_authority.as_of"]),
    (re.compile(r"· 面 " + _D + r"T\d\d:\d\d"), ["lane_silence.generated"]),
    (re.compile(r"longest silence " + _D + r"T[\d:]+ -> " + _D),
     ["lane_silence.longest_silence.from", "lane_silence.longest_silence.to"]),
    (re.compile(r"自 " + _D + r"T\d\d:\d\d 起"), ["lane_silence.open_gap.since"]),
    (re.compile(r"\*\*bm-a\*\*：py [\d.]+%（总机 [\d.]+% · " + _D),
     ["utilization.machines.bm-a.latest_ts"]),
    (re.compile(r"\*\*bm-b\*\*：py [\d.]+%（总机 [\d.]+% · " + _D),
     ["utilization.machines.bm-b.latest_ts"]),
    (re.compile(r"\*\*bm-c\*\*：py [\d.]+%（总机 [\d.]+% · " + _D),
     ["utilization.machines.bm-c.latest_ts"]),
    (re.compile(r"\*\*核分布/并行效率三机对照（T-134 s4 · " + _D + r"）\*\*"),
     ["core_spread.day"]),
    (re.compile(r"\*\*CPU 有效工时（" + _D + r"）\*\*"), ["core_spread.day"]),
    (re.compile(r'"prev_generated": "' + _D), ["token_line.delta_vs_prev.prev_generated"]),
]

# Dates that are neither data claims nor free-floating: a task id, or a stated policy date
# (`前向积累制（2026-10-08 起）`, `CEO 终面 2026-10-26 交付面`, `署名自 2026-11-13 r1293 起`).
# They are counted and printed, and none of them counts as checked (r1672 L7c precedent).
RECORD_RULES = [
    (re.compile(r"T-" + _D), "identifier", "ticket id carries a date"),
    (re.compile(r"前向积累制（" + _D + " 起）"), "policy", "collector start date"),
    (re.compile(r"CEO 终面 " + _D + " 交付面"), "record", "delivery date of the stage-style face"),
    (re.compile(r"署名自 " + _D + r" r\d+ 起"), "record", "when the lane started signing samples"),
]

# Only forms that assert a number about a day. The bar each sentence is priced on differs:
# `__page__` means the report day itself (today's sample counts), a field path means that
# section's own bar. This is the r1672 defect on this paper, twice.
DAY_CLAIM_RULES = [
    (re.compile(r"今日底线合规 \d+/\d+"), "__page__", "counts samples taken on the report day"),
    (re.compile(r"当日零发射"), "core_spread.day", "asserts the day's launches"),
    (re.compile(r"当日零判定批"), "core_spread.day", "asserts the day's judged batches"),
    (re.compile(r"；今日 [是否]"), "market_risk.cutoff", "asserts the kill-day reading"),
    (re.compile(r"^- (今天|在 \d{4}-\d{2}-\d{2} 那根 bar 上)：\*\*(不动|换书)\*\*"),
     "etf_book.priced_bar", "hands out an instruction"),
]
DAY_HONEST_RULES = [
    re.compile(r"当日 bar 未出"),
    re.compile(r"（非当日）"),
    re.compile(r"当日=周六无交易照出"),
    re.compile(r"两池不在同一交易日"),
    re.compile(r"今日尚未有 ?bar"),
]


def _pages():
    """(json path, md path) of the newest report pair, by the date in the file name."""
    pairs = []
    for name in os.listdir(OUT_DIR) if os.path.isdir(OUT_DIR) else []:
        m = re.match(r"^REPORT-(\d{4}-\d{2}-\d{2})\.json$", name)
        if m:
            pairs.append((m.group(1), name))
    if not pairs:
        return None, None
    day, name = sorted(pairs)[-1]
    return (os.path.join(OUT_DIR, name),
            os.path.join(OUT_DIR, "REPORT-%s.md" % day))


def _twin_dates(v, out):
    if isinstance(v, str):
        out.update(LBW.DATE_IN_TEXT.findall(v))
    elif isinstance(v, dict):
        for kv in v.values():
            _twin_dates(kv, out)
    elif isinstance(v, (list, tuple)):
        for kv in v:
            _twin_dates(kv, out)
    return out


def _extra_faces(doc):
    """The paper's 十二 prints a book-identity line that lives in no JSON field.

    Same source the writer used (`etf_book_identity`), so the audit resolves the bar from the
    identity face rather than from the sentence it is checking.
    """
    try:
        from scripts import etf_book_identity as BI
        face = BI.face()
    except Exception:
        return {}
    return {"book_identity": face if isinstance(face, dict) else {}}


def census(doc, printed, twin=None):
    ret = {"page_day": None, "bar_day": None, "verdict": "UNREADABLE", "sentence": "",
           "printed": {"state": "not_measured"}, "date_claims": {"state": "not_measured"},
           "day_claims": {"state": "not_measured"}}
    if not isinstance(doc, dict) or not doc:
        ret["sentence"] = "战报的 JSON 读不出来——这不是「没有日词」，是没法核验。"
        return ret
    doc = dict(doc)
    doc.update(_extra_faces(doc))
    ret["page_day"] = str(doc.get("report_date") or "")[:10] or None
    ret["bar_day"] = str((doc.get("combat") or {}).get("marks_asof") or "")[:10] or None
    if printed is None:
        ret["printed"] = {"state": "unreadable"}
        ret["verdict"] = "UNVERIFIED_PRINTED_FACE"
        ret["sentence"] = ("战报的印刷面读不出来（只读到 JSON）——「没核到」不等于「没问题」，"
                           "所以这一面不给绿。")
        return ret

    rows = LUW._printed_rows(printed)
    day_rows = LUW._day_word_rows(rows)
    honest_rows = [r for r in day_rows
                   if any(p.search(r.get("line") or "") for p in DAY_HONEST_RULES)]
    debt_rows = [r for r in day_rows if r not in honest_rows]
    undated = [r for r in debt_rows if not r["self_dated"]]
    ret["printed"] = {"state": "ok", "n_lines": len(day_rows), "n_all_lines": len(rows),
                      "n_honest": len(honest_rows),
                      "n_self_dated": len(debt_rows) - len(undated),
                      "n_undated": len(undated), "undated": undated[:40], "rows": rows}

    universe = twin if twin is not None else _twin_dates(doc, set())

    def classify(rec):
        line = rec.get("line") or ""
        for pat, bucket, _why in RECORD_RULES:
            if pat.search(line):
                return bucket
        return "member_of_twin" if rec.get("date") in universe else None

    ret["date_claims"] = LBW._date_claims(rows, doc, rules=CLAIM_RULES,
                                          unmapped_classifier=classify)
    dc = ret["date_claims"]
    foreign = [r for r in (dc.get("unmapped") or [])]
    dc["foreign"] = foreign
    dc["n_foreign"] = dc.get("n_unmapped", 0)
    dc["n_member"] = (dc.get("buckets") or {}).get("member_of_twin", 0)

    def bar_for(field):
        if field == "__page__":
            return ret["page_day"]
        return LBW._doc_value(doc, field)

    ret["day_claims"] = LUW._day_claims(day_rows, ret["page_day"], ret["bar_day"],
                                        rules=DAY_CLAIM_RULES, bar_for=bar_for,
                                        honest_forms=DAY_HONEST_RULES)
    dy = ret["day_claims"]
    if dc.get("n_mismatch"):
        ret["verdict"] = "PRINTED_DATE_MISMATCH"
    elif dy.get("n_stale"):
        ret["verdict"] = "DAY_WORD_ON_STALE_PAGE"
    elif ret["printed"].get("n_undated"):
        ret["verdict"] = "PRINTED_BUT_UNANCHORED"
    elif dc.get("n_foreign"):
        ret["verdict"] = "PRINTED_DATE_FOREIGN"
    elif (dc.get("n_claims") and not dc.get("n_unverifiable")
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
        return ("**战报上 %d 处日期里，有 %d 处与它引用的那张面对不上**：%s。"
                % (dc.get("n_claims", 0), dc.get("n_mismatch", 0), named))
    if c["verdict"] == "DAY_WORD_ON_STALE_PAGE":
        named = "；".join("「%s」" % r["line"][:50] for r in (dy.get("offenders") or [])[:4])
        return ("**本页是 %s 的战报，可它拿「今天/今日」说的是 %s 那根 bar 的数**（%d 处）：%s。"
                "周五收盘价的数印在周六的纸上，读者读成自己今天的数。"
                % (c.get("page_day") or "?", c.get("bar_day") or "?", dy.get("n_stale", 0), named))
    if c["verdict"] == "PRINTED_BUT_UNANCHORED":
        return ("**战报上 %d 行日词、%d 行读不出是哪一天**——规则还没覆盖这些句子，"
                "所以这一面说不出它们对不对。" % (pr.get("n_lines", 0), pr.get("n_undated", 0)))
    if c["verdict"] == "PRINTED_DATE_FOREIGN":
        named = "、".join(r["date"] for r in (dc.get("foreign") or [])[:6])
        return ("**战报上印着 %d 个日子，这 %d 个在它自己的 JSON 里找不到**：%s——"
                "读者照这些日子去对账，对不上任何一张面。"
                % (pr.get("n_all_lines", 0), dc.get("n_foreign", 0), named))
    if c["verdict"] == "PRINTED_DATES_AGREE":
        return ("**战报上 %d 处日期逐句对上了它引用的那张面**（%d 条规则，0 处判不了）；"
                "另有 %d 处日期落在成文约定/票号上（计数不核）、%d 处只是「JSON 里也有这一天」；"
                "日词 %d 行没有一行坐在别的 bar 上（本页 %s，最近一根 bar %s）。"
                "这一面核的是「句子写的日子 == 那个字段写的日子」，不核那个字段本身对不对。"
                % (dc.get("n_claims", 0), dc.get("n_rules", 0),
                   sum(n for k, n in (dc.get("buckets") or {}).items() if k != "member_of_twin"),
                   dc.get("n_member", 0), pr.get("n_lines", 0),
                   c.get("page_day") or "?", c.get("bar_day") or "?"))
    return ("**战报上 %d 处日期都带了日子，但 %d 处判不了（字段缺）**——判不了的不算对上，"
            "这一面不给绿。" % (dc.get("n_claims", 0), dc.get("n_unverifiable", 0)))


def _read(json_face=None, page_face=None):
    jf, pf = (_pages() if json_face is None else (json_face, page_face))
    if not jf:
        return None, None, "no REPORT-*.json under docs/daily_report"
    try:
        with open(jf, "r", encoding="utf-8") as fh:
            doc = json.load(fh) or {}
    except (OSError, ValueError) as exc:
        return None, None, "%s: %s" % (type(exc).__name__, exc)
    printed = None
    try:
        with open(pf, "r", encoding="utf-8") as fh:
            printed = fh.read()
    except (OSError, ValueError):
        printed = None
    return doc, printed, None


def run(out=FACE):
    doc, printed, err = _read()
    if err:
        print("DAILY_REPORT_DAY_WORDS_UNREADABLE %s" % err)
        return 2
    c = census(doc, printed)
    jf, pf = _pages()
    c["script"] = "daily_report_day_words"
    c["artifact"] = os.path.relpath(jf, ROOT).replace(os.sep, "/")
    c["page"] = os.path.relpath(pf, ROOT).replace(os.sep, "/")
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
    print("verdict %s | page %s | bar %s | day-word lines %s (self-dated %s / undated %s)"
          % (c["verdict"], c.get("page_day") or "?", c.get("bar_day") or "?",
             pr.get("n_lines", "-"), pr.get("n_self_dated", "-"), pr.get("n_undated", "-")))
    print("  DATES claims %s | ok %s | mismatch %s | unverifiable %s | unmapped %s | rules %s"
          % (dc.get("n_claims", "-"), dc.get("n_ok", "-"), dc.get("n_mismatch", "-"),
             dc.get("n_unverifiable", "-"), dc.get("n_unmapped", "-"), dc.get("n_rules", "-")))
    print("  BUCKETS %s"
          % ", ".join("%s=%s" % (k, v) for k, v in sorted((dc.get("buckets") or {}).items())))
    print("  DAYS  claims %s | stale %s | honest-forms %s"
          % (dy.get("n_claims", "-"), dy.get("n_stale", "-"), dy.get("n_honest_forms", "-")))
    for r in dc.get("mismatches") or []:
        print("  DATE-MISMATCH %s | printed %s | %s = %s"
              % (r["heading"], r["date"], r["field"], r["expected"]))
    for r in dc.get("unmapped") or []:
        print("  DATE-FOREIGN %s | %s | %s" % (r["heading"], r["date"], r["line"][:80]))
    for r in dy.get("offenders") or []:
        print("  STALE-DAY %s | page %s vs bar %s | %s"
              % (r["heading"], r["page_day"], r["bar_day"], r["line"][:100]))
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

    def doc(day="2026-11-14", bar="2026-11-13"):
        return {"report_date": day, "generated_at": day + " 10:56:44",
                "combat": {"market_clock": {"asof": bar}, "marks_asof": bar},
                "live_usage": {"day": day},
                "pnl_attribution": {"asof": bar,
                                    "paper6": {"asof": bar, "prior": "2026-11-12"},
                                    "families": [{"asof": bar}, {"asof": "2026-10-28"},
                                                 {"asof": bar}, {"asof": "2026-10-29"}]},
                "stage_style": {"cutoff": "2026-10-19",
                                "window": {"lo": "2013-04-01", "hi": "2026-10-19"}},
                "market_risk": {"cutoff": bar, "series": [{"date": bar}]},
                "core_spread": {"day": day},
                "lane_authority": {"as_of": "2026-11-14T10:56:40"},
                "lane_silence": {"generated": "2026-11-14T10:05:36",
                                 "longest_silence": {"from": "2026-11-11T16:00",
                                                     "to": "2026-11-11T18:47"},
                                 "open_gap": {"since": "2026-11-14T09:10"}},
                "utilization": {"machines": {"bm-a": {"latest_ts": "2026-11-13 19:59:02"},
                                             "bm-b": {"latest_ts": "2026-10-30 07:20:32"},
                                             "bm-c": {"latest_ts": "2026-11-14 10:04:26"}}},
                "token_line": {"delta_vs_prev": {"prev_generated": "2026-11-14 03:31:16"}},
                "decisions_tail": ["- 2026-09-26 09:32 · T-74 市场时钟组合"],
                "etf_book": {"priced_bar": bar, "book_decided_at": "2026-11-11",
                             "next_rebalance_date": "2026-12-09",
                             "forward": {"inception": "2026-10-23", "as_of": bar},
                             "envelope": {"evidence_cutoff": bar}}}

    def page(day="2026-11-14", bar="2026-11-13", kill="（bar 2026-11-13）否",
             action="在 2026-11-13 那根 bar 上：**不动**"):
        return "\n".join([
            "# 每日战报 — " + day,
            "> 生成 " + day + " 10:56:44 · 聚合面零新判据 · 缺面如实标注",
            "## 一、实战面",
            "- **市场时钟**：`RED_COOL`（asof " + bar + "）· 仓位阶梯帽 0.2",
            "- **在册交易员**（6 员 · marks " + bar + "）：总权益 5944976.54 CNY",
            "## 二、CEO 实盘使用面（T-105 直达）",
            "- **[实盘一页纸直达](../live_usage/LIVE-" + day + ".md)**（LIVE-" + day + "）",
            "## 三、研发面（24h）",
            "- **核分布/并行效率三机对照（T-134 s4 · " + day + "）**：当日零发射",
            "- **CPU 有效工时（" + day + "）**：当日零判定批",
            "## 四、决策面（GM 自主决策日志尾 · 最后一条 2026-09-26）",
            "- 2026-09-26 09:32 · T-74 市场时钟组合",
            "## 五、明日队列（公司自排优先级）",
            "- T-2026-09-24-16(claimed) fund-premium-data-probe",
            "## 九、市场风险面",
            "- 截止日：四面同为 **" + bar + "**",
            "- 读法（机械口径，不含判据）：跌停数 ≥ 涨停数 → 记为**杀跌日**（bar " + bar + "）；" + kill,
            "## 十二、ETF 那本账（纸盘：现在该不该动、能期待什么）",
            "- **定价日 " + bar + "**（决策 2026-11-11）· 下一次调仓 2026-12-09",
            "- " + action + "（继续持有到 2026-12-09）；现在换一次书=年化让出 17.29%",
            "- 前向账本 16 根 bar（2026-10-23→" + bar + "）：NAV 1.0108942788",
        ])

    # L1 a Saturday paper whose kill-day word belongs to Friday is the r1672 defect, here
    c = census(doc(), page(kill="今日 否"))
    leg("L1 stale kill-day word is an offender",
        c["verdict"] == "DAY_WORD_ON_STALE_PAGE", c["verdict"])
    leg("L1b sentence names both days",
        "2026-11-14" in c["sentence"] and "2026-11-13" in c["sentence"], c["sentence"][:80])

    # L2 the same sentence with the bar named is green
    c2 = census(doc(), page())
    leg("L2 bar-named day word is green", c2["verdict"] == "PRINTED_DATES_AGREE",
        "%s claims=%s ok=%s unmapped=%s unverif=%s undated=%s"
        % (c2["verdict"], c2["date_claims"].get("n_claims"), c2["date_claims"].get("n_ok"),
           c2["date_claims"].get("n_unmapped"), c2["date_claims"].get("n_unverifiable"),
           c2["printed"].get("n_undated")))

    # L3 a task id is counted apart, never as checked and never as foreign
    leg("L3 identifier bucket counted", (c2["date_claims"].get("buckets") or {}).get("identifier") == 1,
        str(c2["date_claims"].get("buckets")))

    # L4 a date the twin JSON does not contain is foreign and blocking
    c4 = census(doc(), page().replace("- 2026-09-26 09:32 · T-74", "- 2026-09-19 09:32 · T-74"))
    leg("L4 foreign date blocks", c4["verdict"] == "PRINTED_DATE_FOREIGN", c4["verdict"])
    leg("L4b the foreign date is named", "2026-09-19" in c4["sentence"], c4["sentence"][:90])

    # L5 a claimed date that disagrees with its field is a mismatch
    c5 = census(doc(), page().replace("**定价日 2026-11-13**", "**定价日 2026-11-12**"))
    leg("L5 date mismatch", c5["verdict"] == "PRINTED_DATE_MISMATCH", c5["verdict"])

    # L6 a day word with no date at all still blocks
    c6 = census(doc(), page().replace("## 十二、ETF 那本账（纸盘：现在该不该动、能期待什么）",
                                      "## 十二、ETF 那本账（纸盘：今天该不该动）"))
    leg("L6 undated day word blocks", c6["verdict"] == "PRINTED_BUT_UNANCHORED", c6["verdict"])

    # L7 the page day's own count is never stale (per-sentence bars, not one page-wide bar)
    c7 = census(doc(), page().replace("（总机 33.0%", "（总机 33.0%"))
    leg("L7 same-day sentences stay green", c7["verdict"] == "PRINTED_DATES_AGREE", c7["verdict"])

    # L8 an unreadable paper is never clean
    c8 = census(doc(), None)
    leg("L8 unreadable paper", c8["verdict"] == "UNVERIFIED_PRINTED_FACE", c8["verdict"])

    # L9 a missing twin is unreadable, not zero dates
    c9 = census({}, page())
    leg("L9 missing doc", c9["verdict"] == "UNREADABLE", c9["verdict"])

    # L10 the real published pair yields a verdict (whatever it says today)
    try:
        rdoc, rprinted, rerr = _read()
    except Exception as exc:  # pragma: no cover
        rdoc, rprinted, rerr = None, None, str(exc)
    leg("L10 live pair readable", rerr is None and isinstance(rdoc, dict), str(rerr))
    if rerr is None and rprinted is not None:
        live = census(rdoc, rprinted)
        leg("L10b live pair yields a verdict", live["verdict"] in (
            "PRINTED_DATES_AGREE", "PRINTED_DATE_MISMATCH", "DAY_WORD_ON_STALE_PAGE",
            "PRINTED_BUT_UNANCHORED", "PRINTED_DATE_FOREIGN", "PRINTED_SELF_DATED"),
            live["verdict"])

    print("daily_report_day_words selftest %d/%d" % (ok, total))
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
