"""ETF board -- the wide gap the reader sees today: does history ever hand it back?

The two census faces answer "are these two tickers the same thing" (r1804 by name, r1806 by
price) and the money they print is the *choice cost*: hold the expensive twin instead of the
cheap one and you paid 33,762.8 CNY on a 100,000 CNY ticket. That number has never been asked
the follow-up question, and a reader cannot get it from the gap level alone either: a pair can
sit wide for years and never hand the travelled points back inside one rebalancing grid.

r1523 measured exactly this harvest -- but only for the pairs this book itself had swapped,
because it priced the result on the notional that actually traded. On 2026-11-16 that left the
face with `pairs: []`: every candidate was "this ticket did not swap this name out". The board
holds 76 accepted same-name groups and 815 same-basket cross-name pairs, and not one of them
was being measured.

So this face asks the same question of the whole board, on a stated ticket size instead of on
this book's traded notional:

  * candidates come from the two census faces (same-basket only: a name that agreed and prices
    that agreed, or prices that agreed under two different names) -- both readers are imported,
    so this face cannot disagree with either about what a candidate is;
  * the gap path is the same reconstruction the sibling-gap face uses (100*ln(P_A/P_B) over the
    common sessions), and the level's unknown NAV-base constant cancels out of every change, so
    a pair with no premium anchor still yields an honest delta series;
  * the cohort is "sessions at least as wide as today", the horizon is 20 sessions (one rebal
    grid, same as r1523), and the four-side toll is charged against the harvest;
  * a pair whose cohort is thinner than MIN_COHORT is reported as thin, never as "does not pay".

One caveat is load-bearing and printed on the face: without a premium anchor this measures the
price ratio's path, not the premium's. A pair whose ratio trends (fees, dividends) is refused
upstream by the census year gate; a pair that passes it is treated as bounded, and that premise
is stated rather than assumed.

Usage:
    python scripts/etf_swap_harvest_census.py run
    python scripts/etf_swap_harvest_census.py --check
    python scripts/etf_swap_harvest_census.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_sibling_gap as gap          # noqa: E402  (panels, calendars, gap path)
import etf_label_census as lc              # noqa: E402  (notional, material line, one copy)

ALIAS_JSON = os.path.join(ROOT, "results", "etf_alias_census.json")
LABEL_JSON = os.path.join(ROOT, "results", "etf_label_census.json")
TRIGGER_JSON = os.path.join(ROOT, "results", "etf_book_swap_trigger.json")
OUT_JSON = os.path.join(ROOT, "results", "etf_swap_harvest_census.json")
OUT_MD = os.path.join(ROOT, "results", "etf_swap_harvest_census.md")

WINDOW_DAYS = 250      # the same year the census quotes its drift over
HORIZON = 20           # one REBAL grid, matching r1523
MIN_COHORT = 8         # fewer sessions than this is not a distribution
TAIL_EPS = 1e-9
FLOOR_PP = 0.10        # the smallest daily move this face will call an event, whatever the sd
NOTIONAL_CNY = lc.NOTIONAL_CNY
MATERIAL_PP = lc.MATERIAL_PP

CAVEATS = [
    "this prices one exchange and one exchange back at the horizon; it is not a book backtest -- "
    "nothing else moves, and no other name is re-ranked inside the horizon",
    "the harvest is a better entry into the same basket, not a realised gain: what the pair hands "
    "back is what decides whether a second exchange pays for its own four sides",
    "with no premium anchor the path measured is the price ratio, not the premium; pairs whose "
    "ratio trends are refused upstream by the census year gate, and that premise is stated here "
    "rather than assumed",
    "the ticket size is a stated 100,000 CNY, not this book's traded notional -- the board's "
    "answer is per comparable ticket, so two pairs are comparable to each other",
    "the pairs are alternatives to one another, not a portfolio: the board total adds up the "
    "harvest of many pairs, and one ticket can only make one of those choices",
    "a cohort member whose forward window is not inside the panel is censored, never scored as a "
    "zero change",
    "width is measured from the pair's own window median, so the unknown NAV-base constant "
    "cancels; that also means the face never claims to know which of the two tickers is the "
    "expensive one on a pair with no premium anchor",
]


def _read_json(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (ValueError, OSError):
        return None


def toll_pp(cost_bp):
    """Four sides: two to get in, two to get out."""
    return round(4.0 * float(cost_bp) / 100.0, 4)


def _cost_bp(trig):
    crit = (trig or {}).get("criteria") or {}
    v = crit.get("cost_bp_per_side")
    return None if v is None else float(v)


def candidates(alias_face, label_face):
    """Every pair either census called the same basket, one row per pair.

    The two sources overlap (a same-name pair appears in both), so the dedup key is the sorted
    code pair and the sources are collected instead of the row being counted twice.
    """
    seen = {}
    for p in (alias_face or {}).get("pairs") or []:
        if (p.get("state") or "").upper() != "SAME_BASKET":
            continue
        a, b = str(p.get("a")), str(p.get("b"))
        if not a or not b or a == b:
            continue
        key = tuple(sorted((a, b)))
        rec = seen.setdefault(key, {"a": key[0], "b": key[1], "sources": [],
                                    "same_name": bool(p.get("same_name")),
                                    "census_share": p.get("share"),
                                    "census_drift_pp": p.get("drift_pp")})
        if "alias" not in rec["sources"]:
            rec["sources"].append("alias")
    for fam in (label_face or {}).get("families") or []:
        for p in fam.get("pairs") or []:
            if (p.get("state") or "").upper() != "BASKET":
                continue
            a, b = str(p.get("a")), str(p.get("b"))
            if not a or not b or a == b:
                continue
            key = tuple(sorted((a, b)))
            rec = seen.setdefault(key, {"a": key[0], "b": key[1], "sources": [],
                                        "same_name": True, "census_share": None,
                                        "census_drift_pp": None})
            if "label" not in rec["sources"]:
                rec["sources"].append("label")
            rec["same_name"] = True
    return sorted(seen.values(), key=lambda r: (r["a"], r["b"]))


def despiked_path(series, k=gap.STEP_SD, floor=FLOOR_PP):
    """Rebuild the path with its one-day steps (splits, share changes) replaced by the normal drift.

    A 5:1 split inside the window is a 160 pp one-day move in 100*ln(P_A/P_B) and would otherwise
    be read as a premium that "narrowed" -- the first version of this face printed +109 pp
    harvests that were nothing but a split (r1808). Anything wider than `k` robust sd (and wider
    than `floor`, so a pair whose gap barely moves cannot have its only move called an event) is a
    step: it is replaced by the window's median day change, which is the pair's ordinary drift.
    """
    if len(series) < 3:
        return list(series)
    d = [series[i] - series[i - 1] for i in range(1, len(series))]
    med = statistics.median(d)
    mad = statistics.median([abs(x - med) for x in d]) * 1.4826
    scale = max(mad, floor)
    level = [0.0]
    for dd in d:
        step = med if abs(dd - med) > k * scale else dd
        level.append(level[-1] + step)
    return level


def gap_path(code_a, code_b, cache=None):
    """The pair's gap path over the quoted window, or (None, why).

    The level carries the two NAV bases; every change used below is a difference inside this
    series, so the unknown constant cancels and no premium anchor is required.
    """
    cache = cache if cache is not None else {}
    closes = []
    for code in (code_a, code_b):
        if code not in cache:
            path = gap.find_daily(code)
            if not path:
                cache[code] = None
            else:
                try:
                    cache[code] = gap.load_close(path)
                except OSError:
                    cache[code] = None
        closes.append(cache[code])
    if closes[0] is None or closes[1] is None:
        return None, "没有本地日线面板"
    dates, ca, cb = gap.common_series(closes[0], closes[1])
    if len(dates) < gap.MIN_DAYS:
        return None, "共同交易日只有 %d 根（门槛 %d）" % (len(dates), gap.MIN_DAYS)
    series = gap.gap_series(ca, cb)
    return despiked_path(series[-WINDOW_DAYS:]), None


def forward_deltas(rec, width_today, horizon):
    """Width change `horizon` sessions after every session at least as wide as today.

    Width is measured from the pair's own window median, not from zero. Without a premium anchor
    the level of 100*ln(P_A/P_B) carries an unknown constant (the two NAV bases), so neither the
    sign of the gap nor "how many pp wide" is knowable; the distance to the window's own median
    is -- it shifts by exactly the same constant and cancels (r1808).
    """
    n = len(rec)
    med = statistics.median(rec)
    w = [abs(x - med) for x in rec]
    deltas, censored, members = [], 0, 0
    for i in range(n):
        if w[i] < width_today - TAIL_EPS:
            continue
        members += 1
        j = i + horizon
        if j >= n:
            censored += 1
            continue
        deltas.append(w[j] - w[i])   # a narrowing gap is negative here
    return deltas, censored, members


def measure_pair(cand, series, toll, notional=NOTIONAL_CNY):
    """One pair: is today's width inside a cohort that has ever handed the points back?"""
    row = {"a": cand["a"], "b": cand["b"], "sources": list(cand["sources"]),
           "same_name": cand.get("same_name"), "sessions": None,
           "gap_today_pp": None, "gap_today_percentile": None,
           "cohort": None, "harvest_pp": None, "net_after_toll_pp": None,
           "net_after_toll_cny": None, "verdict": None, "why": ""}
    if not series:
        row["verdict"] = "CANNOT_MEASURE"
        row["why"] = "价差路径读不出"
        return row
    row["sessions"] = len(series)
    today = series[-1]
    med = statistics.median(series)
    width_today = abs(today - med)
    row["gap_today_pp"] = round(float(today), 3)
    row["gap_today_percentile"] = gap.percentile_rank(series, today)
    row["width_today_pp"] = round(float(width_today), 3)
    deltas, censored, members = forward_deltas(series, width_today, HORIZON)
    row["cohort"] = {"members": members, "n": len(deltas), "censored": censored,
                     "threshold_width_pp": round(float(width_today), 3),
                     "window_median_pp": round(float(med), 3)}
    if len(deltas) < MIN_COHORT:
        row["verdict"] = "COHORT_TOO_SMALL"
        row["why"] = ("今天这么宽只出现过 %d 次（可比 %d 次，门槛 %d）：少样本的「中位」不是分布"
                      % (members, len(deltas), MIN_COHORT))
        return row
    median_delta = float(statistics.median(deltas))
    harvest = -median_delta              # a narrowing gap is the swap holder's gain
    net = harvest - toll
    row["harvest_pp"] = round(harvest, 4)
    row["net_after_toll_pp"] = round(net, 4)
    row["net_after_toll_cny"] = round(float(notional) * net / 100.0, 2)
    row["verdict"] = "PAYS" if net > 0 else "DOES_NOT_PAY"
    return row


def compute(ctx):
    """Measure every candidate; refuse what cannot be measured, never as a flat zero."""
    alias_face = ctx.get("alias_census")
    label_face = ctx.get("label_census")
    trig = ctx.get("swap_trigger")
    session = (alias_face or {}).get("session") or (label_face or {}).get("session")
    face = {"artifact": "etf_swap_harvest_census", "bar": session,
            "evidence_cutoff": session, "verdict": None, "sentence": "",
            "refused": None, "pairs": [], "totals": {}, "candidates": 0,
            "skipped": [], "cost_bp_per_side": None, "toll_pp": None,
            "horizon": HORIZON, "window_days": WINDOW_DAYS, "min_cohort": MIN_COHORT,
            "notional_cny": NOTIONAL_CNY, "material_gap_pp": MATERIAL_PP,
            "sources": {"alias_census": "results/etf_alias_census.json",
                        "label_census": "results/etf_label_census.json",
                        "swap_trigger": "results/etf_book_swap_trigger.json"},
            "caveats": list(CAVEATS)}

    if not alias_face and not label_face:
        face["verdict"] = "CANNOT_MEASURE"
        face["refused"] = "两个普查面都不在盘上"
        face["sentence"] = "这一问答不了：两个普查面都不在盘上。"
        return face
    cost = _cost_bp(trig)
    if cost is None:
        face["verdict"] = "CANNOT_MEASURE"
        face["refused"] = "换票触发面没有 cost_bp_per_side"
        face["sentence"] = ("这一问答不了：四边成本读不出来，净额就是编出来的数"
                           "（scripts/etf_book_swap_trigger.py run）。")
        return face
    toll = toll_pp(cost)
    face["cost_bp_per_side"] = cost
    face["toll_pp"] = toll

    cands = candidates(alias_face, label_face)
    face["candidates"] = len(cands)
    cache, rows, skipped = {}, [], []
    for cand in cands:
        series, why = gap_path(cand["a"], cand["b"], cache)
        if series is None:
            skipped.append({"a": cand["a"], "b": cand["b"], "why": why})
            continue
        rows.append(measure_pair(cand, series, toll))

    face["pairs"] = rows
    face["skipped"] = skipped
    measured = [r for r in rows if r.get("verdict") in ("PAYS", "DOES_NOT_PAY")]
    thin = [r for r in rows if r.get("verdict") == "COHORT_TOO_SMALL"]
    unreadable = [r for r in rows if r.get("verdict") == "CANNOT_MEASURE"]
    face["counts"] = {"candidates": len(cands), "measured": len(measured),
                      "pays": sum(1 for r in measured if r["verdict"] == "PAYS"),
                      "does_not_pay": sum(1 for r in measured if r["verdict"] == "DOES_NOT_PAY"),
                      "cohort_too_small": len(thin), "cannot_measure": len(unreadable),
                      "no_panel": len(skipped)}
    if not measured:
        face["verdict"] = "NOTHING_MEASURED"
        face["sentence"] = ("这一问答不了：%d 对候选里没有一对的宽档样本够厚——"
                            "这不是「收不回来」的结论。" % len(cands))
        return face

    pays = [r for r in measured if r["verdict"] == "PAYS"]
    face["totals"] = {
        "measured_pairs": len(measured),
        "pays_pairs": len(pays),
        "net_after_toll_cny": round(sum(r["net_after_toll_cny"] or 0.0 for r in pays), 2),
        "median_net_pp": round(float(statistics.median(
            [r["net_after_toll_pp"] for r in pays])), 4) if pays else None,
        "median_harvest_pp": round(float(statistics.median(
            [r["harvest_pp"] for r in pays])), 4) if pays else None,
    }
    # Material money: a pair whose harvest clears the line the census uses to call a gap worth
    # acting on. Below it the swap is a trade in rounding noise, however positive.
    material = [r for r in pays if (r["net_after_toll_pp"] or 0.0) >= MATERIAL_PP]
    face["totals"]["material_pairs"] = len(material)
    face["totals"]["material_cny"] = round(
        sum(r["net_after_toll_cny"] or 0.0 for r in material), 2)
    face["verdict"] = "PAYS" if face["totals"]["net_after_toll_cny"] > 0 else "DOES_NOT_PAY"
    face["sentence"] = sentence(face)
    return face


def sentence(face):
    c = face.get("counts") or {}
    t = face.get("totals") or {}
    return ("%d 对「价格上是同一个篮子」里，%d 对今天这么宽的历史样本够厚：其中 %d 对"
            "二十个交易日后价差收窄到付完四边成本还有剩，%d 对收不回来；按一手 %s 元算，"
            "捡得回来的合计 %s 元（过物质线的 %d 对、%s 元）。"
            % (c.get("candidates", 0), c.get("measured", 0), t.get("pays_pairs", 0),
               c.get("does_not_pay", 0), format(int(face.get("notional_cny") or 0), ","),
               format(t.get("net_after_toll_cny") or 0.0, ",.0f"),
               t.get("material_pairs") or 0,
               format(t.get("material_cny") or 0.0, ",.0f")))


def _fmt_money(v):
    return format(float(v or 0.0), ",.0f")


def _fmt_pp(v, nd=2):
    return "读不出" if v is None else ("%+.*f" % (nd, v))


def render_md(face):
    c = face.get("counts") or {}
    t = face.get("totals") or {}
    head = [
        "# 盘口的价差，收得回来吗（%s）" % (face.get("bar") or "?"),
        "",
        face.get("sentence") or "",
        "",
        "口径：候选=%s（同名族 %s 与异名族 %s 里被判为同一篮子的对，去重后 %d 对）；"
        "窗 %d 个交易日；持有 %d 个交易日（一个调仓网格）；四边成本 %s pp；一手 %s 元。"
        % ("两普查面", face["sources"]["label_census"], face["sources"]["alias_census"],
           c.get("candidates", 0), face.get("window_days") or WINDOW_DAYS,
           face.get("horizon") or HORIZON, face.get("toll_pp"), _fmt_money(face.get("notional_cny"))),
        "",
        "| 计数 | 对数 |",
        "| --- | --- |",
        "| 候选对 | %d |" % c.get("candidates", 0),
        "| 样本够厚 | %d |" % c.get("measured", 0),
        "| 收得回来 | %d |" % c.get("pays", 0),
        "| 收不回来 | %d |" % c.get("does_not_pay", 0),
        "| 今天这么宽的历史不足 %d 次 | %d |" % (face.get("min_cohort") or MIN_COHORT,
                                              c.get("cohort_too_small", 0)),
        "| 没有本地日线 | %d |" % c.get("no_panel", 0),
        "",
        "## 收得回来的（按净额排序，前 20）",
        "",
        "| A | B | 同名 | 今日价差 pp | 今日分位 | 今日宽度 pp | 历史样本 | 收窄 pp | 净 pp | 一手净额 元 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    pays = [r for r in (face.get("pairs") or []) if r.get("verdict") == "PAYS"]
    pays.sort(key=lambda r: -(r.get("net_after_toll_cny") or 0.0))
    for r in pays[:20]:
        head.append("| %s | %s | %s | %s | %s | %s | %d | %s | %s | %s |"
                    % (r["a"], r["b"], "是" if r.get("same_name") else "否",
                       _fmt_pp(r.get("gap_today_pp")), r.get("gap_today_percentile"),
                       _fmt_pp(r.get("width_today_pp")),
                       (r.get("cohort") or {}).get("n", 0), _fmt_pp(r.get("harvest_pp")),
                       _fmt_pp(r.get("net_after_toll_pp")), _fmt_money(r.get("net_after_toll_cny"))))
    if t.get("material_pairs"):
        head += ["", "过物质线（净额 ≥ %s pp）的 %d 对合计 %s 元。"
                 % (_fmt_pp(face.get("material_gap_pp")), t["material_pairs"],
                    _fmt_money(t.get("material_cny")))]
    head += ["", "## 收不回来的（前 10，按净额最差）", "",
             "| A | B | 今日价差 pp | 历史样本 | 收窄 pp | 净 pp |", "| --- | --- | --- | --- | --- | --- |"]
    worst = [r for r in (face.get("pairs") or []) if r.get("verdict") == "DOES_NOT_PAY"]
    worst.sort(key=lambda r: (r.get("net_after_toll_pp") or 0.0))
    for r in worst[:10]:
        head.append("| %s | %s | %s | %d | %s | %s |"
                    % (r["a"], r["b"], _fmt_pp(r.get("gap_today_pp")),
                       (r.get("cohort") or {}).get("n", 0), _fmt_pp(r.get("harvest_pp")),
                       _fmt_pp(r.get("net_after_toll_pp"))))
    head += ["", "## 不许偷懒的三条", "",
             "1. **今天这么宽一次都没出现过的对不进判词**：样本不足 %d 次的对单列（%d 对），"
             "不写成「收不回来」。" % (face.get("min_cohort") or MIN_COHORT,
                                      c.get("cohort_too_small", 0)),
             "2. **没有溢价锚时量的是价格比，不是溢价**：长期漂移（费率/分红）的对已被普查的年门拒掉，"
             "这条前提写在这里而不是当成事实。",
             "3. **钱是一手的名义额，不是这本书今天卖了多少**：%d 元一手让两对之间可比，"
             "但它不是这一单的实际规模。" % int(face.get("notional_cny") or 0),
             "", "## 限制条款（面的原文）", ""]
    for cv in face.get("caveats") or []:
        head.append("- %s" % cv)
    return "\n".join(head) + "\n"


def check(face):
    """Re-derive the counts, the toll and the money from the published rows."""
    problems = []
    rows = face.get("pairs") or []
    toll = face.get("toll_pp")
    if toll is None:
        problems.append("toll_pp 缺")
    elif abs(toll - round(4.0 * float(face.get("cost_bp_per_side") or 0.0) / 100.0, 4)) > 1e-9:
        problems.append("toll_pp 与四边成本不一致")
    notional = float(face.get("notional_cny") or 0.0)
    measured = [r for r in rows if r.get("verdict") in ("PAYS", "DOES_NOT_PAY")]
    pays = [r for r in measured if r.get("verdict") == "PAYS"]
    for r in measured:
        want = round((r.get("harvest_pp") or 0.0) - (toll or 0.0), 4)
        if abs((r.get("net_after_toll_pp") or 0.0) - want) > 5e-4:
            problems.append("%s/%s 净额 ≠ 收窄 − 四边成本" % (r["a"], r["b"]))
        want_cny = round(notional * (r.get("net_after_toll_pp") or 0.0) / 100.0, 2)
        # net_after_toll_pp is published rounded to 4 decimals, so the ticket money can only be
        # re-derived to within half a unit of that last digit -- 5e-5 pp on the stated notional.
        tol_cny = notional * 5e-5 / 100.0 + 0.01
        if abs((r.get("net_after_toll_cny") or 0.0) - want_cny) > tol_cny:
            problems.append("%s/%s 一手净额 ≠ 名义额×净 pp" % (r["a"], r["b"]))
        if (r.get("verdict") == "PAYS") != ((r.get("net_after_toll_pp") or 0.0) > 0):
            problems.append("%s/%s 判词与净额符号不符" % (r["a"], r["b"]))
    counts = face.get("counts") or {}
    if counts.get("measured") != len(measured):
        problems.append("measured 计数与行不符")
    if counts.get("pays") != len(pays):
        problems.append("pays 计数与行不符")
    if counts.get("does_not_pay") != len(measured) - len(pays):
        problems.append("does_not_pay 计数与行不符")
    totals = face.get("totals") or {}
    want_total = round(sum(r.get("net_after_toll_cny") or 0.0 for r in pays), 2)
    if abs((totals.get("net_after_toll_cny") or 0.0) - want_total) > 0.05:
        problems.append("总计净额 ≠ 各对净额之和")
    material = [r for r in pays
                if (r.get("net_after_toll_pp") or 0.0) >= (face.get("material_gap_pp") or 0.0)]
    if totals.get("material_pairs") != len(material):
        problems.append("物质线以上对数与行不符")
    return {"artifact": face.get("artifact"), "ok": not problems, "problems": problems,
            "rows": len(rows), "measured": len(measured)}


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def L1_toll():
        assert toll_pp(8.0) == 0.32, "四边 8bp = 0.32pp"
        assert toll_pp(5.0) == 0.20, "四边 5bp = 0.20pp"

    def L2_shift_invariance():
        # The unknown NAV-base constant shifts the whole path; width from the window median
        # shifts with it, so every reading below must be identical.
        series = [0.0] * 60 + [5.0] * 20 + [0.0] * 60 + [5.0] * 20 + [0.0] * 60 + [5.0] * 10
        shifted = [x + 37.5 for x in series]
        a = measure_pair({"a": "1", "b": "2", "sources": ["alias"]}, series, 0.32)
        b = measure_pair({"a": "1", "b": "2", "sources": ["alias"]}, shifted, 0.32)
        assert a["harvest_pp"] == b["harvest_pp"], "平移价差水平不改收窄读数（无溢价锚的前提）"
        assert a["net_after_toll_pp"] == b["net_after_toll_pp"], "净额同样平移不变"
        assert a["width_today_pp"] == b["width_today_pp"], "宽度以自身中位为中心，同样平移不变"

    def L3_narrowing_pays():
        series = [0.0] * 60 + [5.0] * 20 + [0.0] * 60 + [5.0] * 20 + [0.0] * 60 + [5.0] * 10
        row = measure_pair({"a": "1", "b": "2", "sources": ["alias"]}, series, 0.32)
        assert row["verdict"] == "PAYS", "宽档后收窄应判收得回来：%r" % (row["verdict"],)
        assert row["harvest_pp"] > 0, "收窄=正收成"

    def L4_flat_does_not_pay():
        series = [1.0] * 100
        row = measure_pair({"a": "1", "b": "2", "sources": ["alias"]}, series, 0.32)
        assert row["verdict"] == "DOES_NOT_PAY", "价差不动时收成 0，付四边即负"
        assert abs(row["net_after_toll_pp"] + 0.32) < 1e-9, "净额应恰为 −toll"

    def L5_thin_cohort():
        # Today is the widest the pair has ever been: four earlier sessions reach it, and none
        # of them has a forward window left inside the panel.
        series = [0.0] * 100 + [3.0] * 4
        row = measure_pair({"a": "1", "b": "2", "sources": ["alias"]}, series, 0.32)
        assert row["verdict"] == "COHORT_TOO_SMALL", "样本不足要单列，不写收不回来：%r" % (row["verdict"],)
        assert row["net_after_toll_pp"] is None, "样本不足时不许印净额"

    def L6_dedup():
        alias_face = {"pairs": [
            {"a": "159915", "b": "510300", "state": "SAME_BASKET", "same_name": False},
            {"a": "510300", "b": "159915", "state": "SAME_BASKET", "same_name": False},
            {"a": "159915", "b": "512880", "state": "DAYS_APART", "same_name": False},
        ]}
        label_face = {"families": [{"pairs": [
            {"a": "159915", "b": "510300", "state": "BASKET"},
            {"a": "159915", "b": "512880", "state": "NOT_BASKET"},
        ]}]}
        cands = candidates(alias_face, label_face)
        assert len(cands) == 1, "同一对两个来源同一方向只算一行：%d" % len(cands)
        assert cands[0]["sources"] == ["alias", "label"], "两个来源都要留痕：%r" % (cands[0]["sources"],)
        assert cands[0]["a"] == "159915" and cands[0]["b"] == "510300", "去重键要排序"

    def L7_only_same_basket():
        alias_face = {"pairs": [
            {"a": "1", "b": "2", "state": "WALKS_APART"},
            {"a": "1", "b": "3", "state": "UNPRICED"},
        ]}
        assert candidates(alias_face, None) == [], "被拒的对不进候选"

    def L8_missing_panel():
        series, why = gap_path("999999", "999998", {})
        assert series is None and "日线" in why, "没有面板要说没有面板：%r" % (why,)

    def L9_totals_and_counts():
        rows = [
            {"a": "1", "b": "2", "verdict": "PAYS", "harvest_pp": 0.9, "net_after_toll_pp": 0.58,
             "net_after_toll_cny": 580.0},
            {"a": "3", "b": "4", "verdict": "PAYS", "harvest_pp": 0.5, "net_after_toll_pp": 0.18,
             "net_after_toll_cny": 180.0},
            {"a": "5", "b": "6", "verdict": "DOES_NOT_PAY", "harvest_pp": 0.1,
             "net_after_toll_pp": -0.22, "net_after_toll_cny": -220.0},
        ]
        face = {"artifact": "x", "pairs": rows, "toll_pp": 0.32, "cost_bp_per_side": 8.0,
                "notional_cny": 100000.0, "material_gap_pp": 0.5,
                "counts": {"measured": 3, "pays": 2, "does_not_pay": 1},
                "totals": {"net_after_toll_cny": 760.0, "material_pairs": 1}}
        res = check(face)
        assert res["ok"], "干净面应过检：%r" % (res["problems"],)
        bad = dict(face)
        bad["totals"] = dict(face["totals"])
        bad["totals"]["net_after_toll_cny"] = 700.0
        assert not check(bad)["ok"], "总计被改小必须被抓"

    def L10_sentence_cites_counts():
        face = {"counts": {"candidates": 815, "measured": 700, "pays": 40, "does_not_pay": 660},
                "totals": {"pays_pairs": 40, "net_after_toll_cny": 12345.0,
                           "material_pairs": 3, "material_cny": 6000.0},
                "notional_cny": 100000}
        s = sentence(face)
        for token in ("815", "700", "40", "660", "12,345", "3", "6,000"):
            assert token in s, "句子要引用它拿到的计数 %s：%s" % (token, s)

    def L11_split_is_not_a_premium():
        # A 5:1 split: the ratio drops 160 pp in one session and stays there. Read raw, the
        # "harvest" of every earlier wide session would be 160 pp; despiked, it is nothing.
        raw = [0.0] * 120 + [-160.0] * 120
        path = despiked_path(raw)
        span = max(path) - min(path)
        assert span < 5.0, "拆分台阶要被剔掉，不能读成 160pp 的溢价收窄：%.1f" % span
        row = measure_pair({"a": "1", "b": "2", "sources": ["alias"]}, path, 0.32)
        assert (row["harvest_pp"] or 0.0) < 1.0, "剔除台阶后收成应近 0：%r" % (row["harvest_pp"],)

    for name, fn in [
        ("L1 四边成本=4×单边", L1_toll),
        ("L2 平移不变（无溢价锚前提）", L2_shift_invariance),
        ("L3 宽档后收窄=收得回来", L3_narrowing_pays),
        ("L4 价差不动=收不回来", L4_flat_does_not_pay),
        ("L5 样本不足单列不判负", L5_thin_cohort),
        ("L6 两来源同一对只算一行", L6_dedup),
        ("L7 被拒对不进候选", L7_only_same_basket),
        ("L8 缺面板如实说", L8_missing_panel),
        ("L9 总计/计数/物质线与行一致", L9_totals_and_counts),
        ("L10 句子引用自己的计数", L10_sentence_cites_counts),
        ("L11 拆分台阶不读成溢价", L11_split_is_not_a_premium),
    ]:
        leg(name, fn)
    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, why in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, ("  -- " + why) if why else ""))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def write_out(face):
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(face))


def run():
    ctx = {"alias_census": _read_json(ALIAS_JSON),
           "label_census": _read_json(LABEL_JSON),
           "swap_trigger": _read_json(TRIGGER_JSON)}
    face = compute(ctx)
    write_out(face)
    print(face.get("sentence") or face.get("refused") or "")
    print("verdict=%s counts=%s" % (face.get("verdict"),
                                    json.dumps(face.get("counts") or {}, ensure_ascii=False)))
    res = check(face)
    print("check %s problems=%s" % ("OK" if res["ok"] else "FAIL", res["problems"]))
    return 0 if res["ok"] else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--check", action="store_true", help="re-derive the published face")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check or args.cmd == "check":
        face = _read_json(OUT_JSON)
        if not face:
            print("no face on disk")
            return 2
        res = check(face)
        print("CHECK %s problems=%s rows=%d measured=%d"
              % ("OK" if res["ok"] else "FAIL", res["problems"], res["rows"], res["measured"]))
        return 0 if res["ok"] else 1
    return run()


if __name__ == "__main__":
    sys.exit(main())
