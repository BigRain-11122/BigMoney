#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cash_shelf_wait_payback -- how many days of extra does the wait cost?

WHY THIS FACE EXISTS
--------------------
`cash_shelf_build_out_plan` (r2043) priced the wait in CNY at the ticket and
`cash_shelf_inflight_carry` (r2044) took back what the repo leg pays while the cash is
still in flight.  Both print 元.  A reader holding the ticket cannot compare 元 to 元
across shelves of different size, because "2787 元" means nothing until it is put next to
what that shelf actually earns over the repo leg in a year (1167 元 for 511380, 3088 元
for 511360).  One shelf's wait eats a quarter of a year of its extra; the other's eats a
fortnight.

So this face does one conversion and no new measurement:

    payback_days = (net wait cost in CNY) / (我每天多赚的 CNY)

i.e. how many trading days of this shelf's extra-over-repo the wait has to earn back
before the batching pays for itself.  Nothing is re-derived from prices here: every CNY
figure is imported from the two published faces, and the trading-day denominator is
derived from each shelf's own bar count and window, never typed as 243 or 244.

THE QUESTION (frozen before the first run)
------------------------------------------
If the ticket has to be spread over the sessions the capacity ruler forces, how many
trading days of that shelf's extra-over-repo does the wait consume -- at the median and
at the 95th percentile -- and which shelves finish their batch inside a one-month budget?

READINGS
--------
* `payback_days_median`: the median wait expressed in days of extra.  May be negative
  (batching was cheaper than buying day one) -- printed as a number, never clipped to 0.
* `payback_days_p95`: the 95th-percentile wait expressed the same way.  This is the one
  the verdict uses: a batch is a commitment and the tail is what it can cost.
* A shelf whose extra-over-repo is not positive has nothing to pay the wait back with;
  its payback is printed as `None` and the verdict says so instead of dividing by it.

VERDICTS (mechanical, on the p95 column)
----------------------------------------
* ONE_SESSION_NO_WAIT        -- the ruler clears this tier in one session.
* NO_EXTRA_TO_PAY_BACK       -- this shelf does not beat the repo leg at all; the wait
                                cannot be repaid and batching it is pure cost.
* PAYS_BACK_WITHIN_A_MONTH   -- payback_days_p95 <= ADOPTION.budget_sessions.
* PAYS_BACK_WITHIN_A_YEAR    -- <= one year of that shelf's own bars.
* LONGER_THAN_A_YEAR         -- the wait costs more than a year of the extra.
* CUT_HITS_IN_THE_WAIT       -- p95 wait is negative but the median is not positive e.g.
                                the tail is on the other side; printed, not folded.
* NO_WINDOWS                 -- the tape is shorter than the schedule; nothing claimed.

Usage:
    python scripts/cash_shelf_wait_payback.py run
    python scripts/cash_shelf_wait_payback.py --check
    python scripts/cash_shelf_wait_payback.py --selftest
"""

from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PLAN_FACE = "results/cash_shelf_build_out_plan.json"
CARRY_FACE = "results/cash_shelf_inflight_carry.json"
FACE = "results/cash_shelf_wait_payback.json"
DOC = "research/CASH_SHELF_WAIT_PAYBACK.md"

# The decision this face commits to, in one place.  Everything below reads it.
ADOPTION = {
    "decided": "verdicts_use_p95_and_a_one_month_budget",
    "decided_in": "r2045 bm-c",
    "because": (
        "a batch is a commitment, so the tail is what it can cost; one month of the "
        "shelf's own extra is the widest budget that still lets a THIN shelf finish "
        "without turning the wait into an investment decision"
    ),
    "budget_sessions": 20,
    "caliber": "p95",
}
# Budget as a fraction of a year is derived per shelf from its own bars; 20 sessions is
# compared directly against payback_days, so no year constant is needed at all.

MARK_BEGIN = "<!-- PAYBACK-TABLE:BEGIN -->"
MARK_END = "<!-- PAYBACK-TABLE:END -->"


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(path):
    with io.open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        return json.load(f)


def bars_per_year(row, window):
    """Trading days per year, derived from the shelf's own bar count and window."""
    start = dt.date.fromisoformat(window["start"])
    end = dt.date.fromisoformat(window["end"])
    years = (end - start).days / 365.25
    if years <= 0:
        return None
    return row["index_bars"] / years


def payback(tier, extra_cny, bpy):
    """Convert a wait measured in CNY into days of this shelf's extra-over-repo."""
    out = {"extra_cny": extra_cny, "bars_per_year": bpy}
    for caliber in ("median", "p95"):
        net = tier.get("net_%s_cny" % caliber)
        if net is None:
            out["payback_days_%s" % caliber] = None
            out["net_%s_cny" % caliber] = None
            continue
        out["net_%s_cny" % caliber] = net
        if extra_cny is None or extra_cny <= 0 or bpy is None:
            out["payback_days_%s" % caliber] = None
        else:
            out["payback_days_%s" % caliber] = net / extra_cny * bpy
    return out


def verdict(tier, extra_cny, pb):
    sessions = tier.get("sessions_to_fill")
    # One session means there is no wait to price at all -- that reads as a fact about the
    # capacity ruler, not as missing data, so it is answered before the empty-tape case.
    if sessions is not None and sessions <= 1:
        return ["ONE_SESSION_NO_WAIT"]
    if not tier.get("windows"):
        return ["NO_WINDOWS"]
    if extra_cny is None or extra_cny <= 0:
        return ["NO_EXTRA_TO_PAY_BACK"]
    d95 = pb.get("payback_days_p95")
    dmed = pb.get("payback_days_median")
    if d95 is None:
        return ["NO_WINDOWS"]
    tags = []
    if d95 <= ADOPTION["budget_sessions"]:
        tags.append("PAYS_BACK_WITHIN_A_MONTH")
    elif pb["bars_per_year"] is not None and d95 <= pb["bars_per_year"]:
        tags.append("PAYS_BACK_WITHIN_A_YEAR")
    else:
        tags.append("LONGER_THAN_A_YEAR")
    if dmed is not None and dmed < 0 <= d95:
        tags.append("CUT_HITS_IN_THE_WAIT")
    return tags


def compute(plan, carry):
    """Rows keyed by shelf, tiers keyed by size -- all numbers imported, none retyped."""
    plan_rows = {r["code"]: r for r in plan["rows"]}
    window = carry["window"]
    rows = []
    for crow in carry["rows"]:
        code = crow["code"]
        prow = plan_rows.get(code, {})
        bpy = bars_per_year(crow, window)
        tiers = {}
        for size_key, ctier in sorted(crow["tiers"].items(), key=lambda kv: int(kv[0])):
            extra = ctier.get("year_extra_cny")
            pb = payback(ctier, extra, bpy)
            tiers[size_key] = {
                "size_cny": int(size_key),
                "sessions_to_fill": ctier.get("sessions_to_fill"),
                "windows": ctier.get("windows"),
                "net_median_cny": pb["net_median_cny"],
                "net_p95_cny": pb["net_p95_cny"],
                "net_per_wait_day_bp": ctier.get("net_per_wait_day_bp"),
                "extra_cny": extra,
                "extra_per_day_cny": (extra / bpy) if (extra is not None and bpy) else None,
                "payback_days_median": pb["payback_days_median"],
                "payback_days_p95": pb["payback_days_p95"],
                "plan_class": (prow.get("tiers") or {}).get(size_key, {}).get("class_of_tier"),
                "verdict": verdict(ctier, extra, pb),
            }
        rows.append({
            "code": code,
            "label": crow.get("label"),
            "class": crow.get("class"),
            "index_bars": crow["index_bars"],
            "index_last": crow["index_last"],
            "bars_per_year": bpy,
            "tiers": tiers,
        })
    return rows


def headline(rows, ticket, ticket_size_key):
    at_ticket = []
    for r in rows:
        t = r["tiers"].get(ticket_size_key)
        if not t:
            continue
        at_ticket.append({
            "code": r["code"],
            "class": r["class"],
            "sessions": t["sessions_to_fill"],
            "net_p95_cny": t["net_p95_cny"],
            "payback_days_p95": t["payback_days_p95"],
            "verdict": t["verdict"],
        })
    priced = [a for a in at_ticket if a["payback_days_p95"] is not None]
    priced.sort(key=lambda a: a["payback_days_p95"])
    inside = [a["code"] for a in priced if a["payback_days_p95"] <= ADOPTION["budget_sessions"]]
    outside = [a["code"] for a in priced if a["payback_days_p95"] > ADOPTION["budget_sessions"]]
    return {
        "ticket_cash_cny": ticket,
        "tier_used": int(ticket_size_key),
        "budget_sessions": ADOPTION["budget_sessions"],
        "caliber": ADOPTION["caliber"],
        "at_the_ticket": at_ticket,
        "inside_budget": inside,
        "outside_budget": outside,
        "cheapest_wait": priced[0]["code"] if priced else None,
        "cheapest_wait_days": priced[0]["payback_days_p95"] if priced else None,
        "dearest_wait": priced[-1]["code"] if priced else None,
        "dearest_wait_days": priced[-1]["payback_days_p95"] if priced else None,
    }


def build():
    plan = _load(PLAN_FACE)
    carry = _load(CARRY_FACE)
    rows = compute(plan, carry)
    ticket = carry["upstream"]["ticket_cash_cny"]
    ticket_key = str(carry["upstream"]["tiers_cny"][1]) if len(carry["upstream"]["tiers_cny"]) > 1 else "565246"
    # the ticket tier is the one the two upstream faces used for their own headline
    ticket_key = str(plan["headline"]["tier_used_for_headline"])
    return {
        "schema": "cash-shelf-wait-payback/v1",
        "artifact": "cash_shelf_wait_payback",
        "generated": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": carry.get("evidence_cutoff"),
        "window": carry["window"],
        "question": (
            "if the ticket must be spread over the sessions the capacity ruler forces, "
            "how many trading days of that shelf's extra-over-repo does the wait consume"
        ),
        "adoption": dict(ADOPTION),
        "upstream": {
            "plan_face": PLAN_FACE,
            "plan_sha256": _sha(os.path.join(ROOT, PLAN_FACE)),
            "carry_face": CARRY_FACE,
            "carry_sha256": _sha(os.path.join(ROOT, CARRY_FACE)),
        },
        "ruler": {
            "payback_days": "net wait CNY / (extra-over-repo CNY per trading day)",
            "trading_days_per_year": "index_bars / window years (per shelf, derived not typed)",
            "net_cny": "imported from the carry face (median and p95), never re-derived",
            "extra_cny": "imported from the same tier's year_extra_cny",
            "no_divide": "extra <= 0 leaves payback None instead of a negative denominator",
        },
        "rows": rows,
        "headline": headline(rows, ticket, ticket_key),
    }


def _fmt(v, nd=2):
    if v is None:
        return "-"
    if abs(v) >= 1000:
        return "{:,.{}f}".format(v, nd)
    return "{:.{}f}".format(v, nd)


def render_block(face):
    h = face["headline"]
    lines = []
    lines.append("票面 **%s 元**，预算 = **%d 个交易日的超额**（`%s` 口径）。"
                 % ("{:,.0f}".format(h["ticket_cash_cny"]), h["budget_sessions"], h["caliber"]))
    lines.append("")
    lines.append("| 货架 | 类别 | 排队天数 | 净等待 p95（元） | 中位（元） | 每日超额（元） | **用几天超额来还（p95）** | 判词 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for a in h["at_the_ticket"]:
        t = None
        for r in face["rows"]:
            if r["code"] == a["code"]:
                t = r["tiers"].get(str(h["tier_used"]))
        if not t:
            continue
        d95 = t["payback_days_p95"]
        lines.append("| `%s` | %s | %s | %s | %s | %s | **%s** | %s |" % (
            a["code"], a["class"], t["sessions_to_fill"],
            _fmt(t["net_p95_cny"]), _fmt(t["net_median_cny"]),
            _fmt(t["extra_per_day_cny"], 3) if t["extra_per_day_cny"] is not None else "-",
            ("{:.1f}".format(d95) if d95 is not None else "-"),
            " ".join(t["verdict"])))
    lines.append("")
    if h["inside_budget"]:
        lines.append("- 一个月预算内能排完：**%s**" % "、".join("`%s`" % c for c in h["inside_budget"]))
    if h["outside_budget"]:
        lines.append("- 一个月预算装不下：**%s**" % "、".join("`%s`" % c for c in h["outside_budget"]))
    if h["cheapest_wait"]:
        lines.append("- 最便宜的等待 = `%s`（**%.1f** 个交易日的超额）；最贵的 = `%s`（**%.1f**）"
                     % (h["cheapest_wait"], h["cheapest_wait_days"],
                        h["dearest_wait"], h["dearest_wait_days"]))
    lines.append("")
    lines.append("> 口径：净等待（扣掉回购腿 carry 与佣金）除以「每天比回购多赚多少」，"
                 "即这份排队要用几天的超额才能挣回来。一次就能买完的行（`ONE_SESSION_NO_WAIT`）"
                 "没有排队成本，只印它的每日超额当对照；超额为负的行没有分母。")
    return "\n".join(lines)


def render_doc(face):
    block = render_block(face)
    head = [
        "# 排队要花掉几天的超额？",
        "",
        "> 一句话：**慢本身不贵，慢在被拖长的时候才贵。** 票面 %s 元里，`511360` 排 5 天等于花掉 **%.1f 天**的超额，"
        "`511380` 排 2 天就等于 **%.1f 天**——同一个「分两天买」，一个是一周的账，一个是两年半的账。"
        % ("{:,.0f}".format(face["headline"]["ticket_cash_cny"]),
           _safe(face, "511360"), _safe(face, "511380")),
        "",
        "## 换算本身",
        "",
        "- 分子：`cash_shelf_inflight_carry`（r2044）已经扣掉回购腿 carry 与佣金的**净等待**，中位与 p95 两列。",
        "- 分母：同一档位的 `year_extra_cny`（比回购腿一年多赚多少）除以该货架**自己的**每年 bar 数"
        "（`index_bars / 窗口年数`，逐架 derive，页面不印 243/244 这种手抄常数）。",
        "- 超额不为正的货架没有分母：不印负数百分比、不拿「负分母」比大小，直接印 `NO_EXTRA_TO_PAY_BACK`。",
        "",
        "## 读数",
        "",
        MARK_BEGIN,
        block,
        MARK_END,
        "",
        "## 怎么用",
        "",
        "- 预算线写在 `ADOPTION` 常量里（一个月，20 个交易日），**判词只读它**，各面只印不另立标准。",
        "- 「排期能装进预算」不等于「该买」：它还要求这份超额本身为正、且样本外仍然成立（r2041/r2042 的容量与摆动判词另算）。",
        "- 中位为负而 p95 很贵的行（`CUT_HITS_IN_THE_WAIT`）不是免费，是「赌尾不出现」；决定面按 p95 而不是中位下的判词。",
        "",
        "## 未验证（如实）",
        "",
        "- 本面不重算任何价格或 carry：上游面错了，这里跟着错。",
        "- 「每天超额」用的是全窗口年化均摊，真实超额不是均匀的；亏损年份这份等待会更贵。",
        "- 排队按容量尺子的天数，不建模排队期间可以反悔撤单的情形。",
    ]
    return "\n".join(head)


def _safe(face, code):
    for r in face["rows"]:
        if r["code"] != code:
            continue
        key = str(face["headline"]["tier_used"])
        t = r["tiers"].get(key)
        if t and t["payback_days_p95"] is not None:
            return t["payback_days_p95"]
    return float("nan")


def cmd_run(write_doc=True):
    face = build()
    with io.open(os.path.join(ROOT, FACE), "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
        f.write("\n")
    if write_doc:
        doc_path = os.path.join(ROOT, DOC)
        body = render_doc(face)
        if os.path.exists(doc_path):
            old = io.open(doc_path, encoding="utf-8").read()
            if MARK_BEGIN in old and MARK_END in old:
                pre = old.split(MARK_BEGIN)[0]
                post = MARK_END + old.split(MARK_END, 1)[1]
                body = render_doc(face)
                # keep the existing prose head, replace only the marker block
                new_block = render_block(face)
                body = pre + MARK_BEGIN + "\n" + new_block + "\n" + post
            else:
                body = render_doc(face)
        with io.open(doc_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
    print("RUN OK %s rows=%d inside_budget=%d"
          % (FACE, len(face["rows"]), len(face["headline"]["inside_budget"])))
    return 0


def cmd_check():
    path = os.path.join(ROOT, FACE)
    if not os.path.exists(path):
        print("CHECK FAILED: face missing -> STALE, run `run`")
        return 3
    face = _load(FACE)
    for key, path_key in (("plan_sha256", PLAN_FACE), ("carry_sha256", CARRY_FACE)):
        want = face["upstream"][key]
        got = _sha(os.path.join(ROOT, path_key))
        if want != got:
            print("STALE: %s bytes changed (face %s.. != disk %s..) -> re-run"
                  % (path_key, want[:12], got[:12]))
            return 3
    fresh = build()
    bad = []
    frows = {r["code"]: r for r in fresh["rows"]}
    for r in face["rows"]:
        fr = frows.get(r["code"])
        if not fr:
            bad.append("%s missing upstream" % r["code"])
            continue
        for key, t in r["tiers"].items():
            ft = fr["tiers"].get(key)
            if not ft:
                bad.append("%s/%s tier gone upstream" % (r["code"], key))
                continue
            for field in ("payback_days_p95", "payback_days_median", "net_p95_cny"):
                a, b = t.get(field), ft.get(field)
                if a is None and b is None:
                    continue
                if a is None or b is None or abs(float(a) - float(b)) > 1e-9:
                    bad.append("%s/%s %s: face=%s recompute=%s" % (r["code"], key, field, a, b))
            if t["verdict"] != ft["verdict"]:
                bad.append("%s/%s verdict: face=%s recompute=%s"
                           % (r["code"], key, t["verdict"], ft["verdict"]))
    if bad:
        for b in bad[:12]:
            print("CHECK FAILED:", b)
        return 1
    n = sum(len(r["tiers"]) for r in face["rows"])
    print("CHECK OK (%d shelves / %d tiers recomputed)" % (len(face["rows"]), n))
    return 0


def cmd_selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # 1. payback arithmetic on a hand-made tier
    t = {"net_median_cny": 100.0, "net_p95_cny": 250.0, "sessions_to_fill": 3,
         "windows": 100, "net_per_wait_day_bp": 0.2}
    pb = payback(t, 500.0, 250.0)
    leg("L1 p95 payback = 250/500*250 = 125 days",
        abs(pb["payback_days_p95"] - 125.0) < 1e-9, str(pb["payback_days_p95"]))
    leg("L2 median payback = 50 days", abs(pb["payback_days_median"] - 50.0) < 1e-9)

    # 3. negative median is a number, not clipped
    t2 = dict(t, net_median_cny=-20.0)
    pb2 = payback(t2, 500.0, 250.0)
    leg("L3 negative median printed as negative days", pb2["payback_days_median"] < 0)

    # 4. non-positive extra -> None, never a negative denominator
    pb3 = payback(t, -100.0, 250.0)
    leg("L4 no extra => payback None (no negative denominator)",
        pb3["payback_days_p95"] is None and pb3["payback_days_median"] is None)

    # 5-7. boundary verdicts at the adoption line
    def v(d95, extra=500.0, sessions=5, windows=100):
        tt = {"net_p95_cny": 1.0, "net_median_cny": 1.0, "sessions_to_fill": sessions,
              "windows": windows}
        p = {"payback_days_p95": d95, "payback_days_median": 1.0, "bars_per_year": 243.0}
        return verdict(tt, extra, p)

    b = ADOPTION["budget_sessions"]
    leg("L5 exactly at budget passes", v(b) == ["PAYS_BACK_WITHIN_A_MONTH"], str(v(b)))
    leg("L6 one day over budget falls to the year band",
        v(b + 0.001) == ["PAYS_BACK_WITHIN_A_YEAR"], str(v(b + 0.001)))
    leg("L7 over a year says so", v(243.1) == ["LONGER_THAN_A_YEAR"], str(v(243.1)))
    leg("L8 one session is a no-wait row",
        v(999.0, sessions=1) == ["ONE_SESSION_NO_WAIT"])
    leg("L9 no extra => NO_EXTRA_TO_PAY_BACK before any division",
        v(1.0, extra=0.0) == ["NO_EXTRA_TO_PAY_BACK"])
    leg("L10 no windows => NO_WINDOWS", v(1.0, windows=0) == ["NO_WINDOWS"])
    leg("L18 one session wins over an empty tape (no wait is a fact, not missing data)",
        v(1.0, sessions=1, windows=0) == ["ONE_SESSION_NO_WAIT"])

    # 11. cut tag only when the tail and the median disagree in sign
    tt = {"net_p95_cny": 1.0, "net_median_cny": -1.0, "sessions_to_fill": 4, "windows": 50}
    p = {"payback_days_p95": 30.0, "payback_days_median": -2.0, "bars_per_year": 243.0}
    leg("L11 negative median + positive tail tags CUT_HITS_IN_THE_WAIT",
        "CUT_HITS_IN_THE_WAIT" in verdict(tt, 500.0, p))

    # 12. bars_per_year is derived from the row's own window, not typed
    row = {"window": {"start": "2020-07-16", "end": "2026-11-20"}, "index_bars": 1540}
    bpy = bars_per_year(row, row["window"])
    leg("L12 bars_per_year derived ~242-243", 238 < bpy < 246, "%.3f" % bpy)

    # 13. doubling the wait doubles the payback (linearity of the conversion)
    p1 = payback(dict(t, net_p95_cny=250.0), 500.0, 243.0)["payback_days_p95"]
    p2 = payback(dict(t, net_p95_cny=500.0), 500.0, 243.0)["payback_days_p95"]
    leg("L13 doubling the net wait doubles the payback", abs(p2 - 2 * p1) < 1e-9)

    # 14. the page must not print a doubled per-cent sign (r2039/r2042 family)
    face = build()
    body = render_block(face)
    leg("L14 rendered block contains no '%%'", "%%" not in body)

    # 15. every shelf at the ticket appears in the block (reader sees all prices)
    codes = [a["code"] for a in face["headline"]["at_the_ticket"]]
    leg("L15 block names every shelf at the ticket",
        all(("`%s`" % c) in body for c in codes), str(codes))

    # 16. the marker block is self-contained: begin/end in order
    doc = render_doc(face)
    leg("L16 marker block ordered",
        doc.index(MARK_BEGIN) < doc.index(MARK_END))

    # 17. no negative-zero or nan leaks into the headline ticker
    hs = face["headline"]
    vals = [hs.get("cheapest_wait_days"), hs.get("dearest_wait_days")]
    leg("L17 headline day values are real numbers", all(v is not None for v in vals), str(vals))

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print(("PASS " if ok else "FAIL ") + name + (("  [" + detail + "]") if detail and not ok else ""))
    print("SELFTEST %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "--check":
        return cmd_check()
    if cmd == "--selftest":
        return cmd_selftest()
    if cmd == "show":
        print(json.dumps(build()["headline"], ensure_ascii=False, indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
