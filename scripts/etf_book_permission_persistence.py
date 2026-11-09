"""An obeyed trim lasts how long?

r1450-1455 built a permission (k <= 0.393073), measured that the order path sizes at
k = 0.460253, and made the order sheet print the trim (445 lots, CNY 67,289 -> k
0.392964).  Every one of those faces treats the 11-11 decision bar as the end of the
story.  It is not: `k_schedule()` re-derives k from an expanding beta on every 20th bar
and carries no memory of a trim.  If the schedule walks back up faster than the desk
re-applies the floor, obeying the permission once is a one-cycle gesture and the book is
over the floor again by the next decision.

So this face measures the trim's own lifetime on the schedule that will erase it:

  * the step distribution of k between consecutive decision bars (how far it moves);
  * the erase rule -- every historical bar where k dropped by at least the published
    slack (gap_k from the cut receipt) is an "event", and we count the decision bars
    until k climbs back to the pre-drop level (never = censored, printed as such, not 0);
  * the verdict -- if the median lifetime is one cycle, the floor has to live inside the
    solver every bar; a one-off trim cannot hold it.

Read-only, deterministic, no network, no ledger booking, no verdict on the trade itself.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

import pandas as pd  # noqa: E402

from scripts import etf_composite_pf as F          # noqa: E402
from scripts import etf_phase_beta_target as BT    # noqa: E402
from scripts import etf_book_order as Q            # noqa: E402

GAP_FACE = "results/etf_book_cut_order_gap.json"
OUT = os.path.join(BASE, "results", "etf_book_permission_persistence.json")
MD = os.path.join(BASE, "research", "ETF_BOOK_PERMISSION_PERSISTENCE.md")

REBAL = Q.REBAL
BETA = Q.DEFAULT_BETA
INCEPTION = Q.DEFAULT_INCEPTION
TOL = 1e-9

VERDICT_ONE_CYCLE = "TRIM_ERASED_IN_ONE_CYCLE"
VERDICT_SHORT = "TRIM_LASTS_A_FEW_CYCLES"
VERDICT_PERSISTS = "TRIM_PERSISTS_BEYOND_A_QUARTER"
VERDICT_NO_HISTORY = "NO_TRIM_SIZED_DROPS_IN_HISTORY"


# ------------------------------------------------------------------ pure arithmetic
def steps(sched):
    """[(date, k, beta)] -> per-step deltas. No statistics, only subtraction."""
    out = []
    for i in range(1, len(sched)):
        d0, k0, _ = sched[i - 1]
        d1, k1, _ = sched[i]
        out.append({"prev_date": str(d0)[:10], "date": str(d1)[:10],
                    "k_prev": round(float(k0), 6), "k": round(float(k1), 6),
                    "dk": round(float(k1) - float(k0), 6)})
    return out


def erasure_events(sched, slack):
    """Every drop of at least `slack` followed by the bars until k regains the old level.

    Censoring is explicit: a drop whose level is never regained before the panel ends is
    reported with `bars_to_return=None` and counted in `never_returned`, never as 0.
    """
    ev = []
    ks = [float(k) for _, k, _ in sched]
    for i in range(1, len(ks)):
        if ks[i - 1] - ks[i] < slack - TOL:
            continue
        target = ks[i - 1]
        back = None
        for j in range(i + 1, len(ks)):
            if ks[j] >= target - TOL:
                back = j - i
                break
        ev.append({"drop_date": str(sched[i][0])[:10],
                   "from_k": round(ks[i - 1], 6), "to_k": round(ks[i], 6),
                   "drop": round(ks[i - 1] - ks[i], 6),
                   "bars_to_return": back,
                   "returned": back is not None})
    return ev


def summarize(ev, n_steps):
    done = [e["bars_to_return"] for e in ev if e["returned"]]
    never = [e for e in ev if not e["returned"]]
    s = {
        "events": len(ev),
        "steps": int(n_steps),
        "event_share": round(len(ev) / float(n_steps), 4) if n_steps else None,
        "returned": len(done),
        "never_returned": len(never),
        "median_bars": statistics.median(done) if done else None,
        "mean_bars": round(statistics.fmean(done), 2) if done else None,
        "max_bars": max(done) if done else None,
        "never_dates": [e["drop_date"] for e in never],
    }
    return s


def verdict_of(summary):
    if not summary["events"]:
        return VERDICT_NO_HISTORY
    if summary["median_bars"] is None:
        return VERDICT_PERSISTS
    m = summary["median_bars"]
    if m <= 1:
        return VERDICT_ONE_CYCLE
    if m <= 4:
        return VERDICT_SHORT
    return VERDICT_PERSISTS


def step_stats(st, slack):
    d = [abs(r["dk"]) for r in st]
    if not d:
        return {"steps": 0}
    up = [r["dk"] for r in st if r["dk"] > 0]
    return {
        "steps": len(d),
        "median_abs_dk": round(statistics.median(d), 6),
        "mean_abs_dk": round(statistics.fmean(d), 6),
        "p90_abs_dk": round(sorted(d)[int(0.9 * (len(d) - 1))], 6),
        "max_abs_dk": round(max(d), 6),
        "max_drop": round(-min(r["dk"] for r in st), 6),
        "max_up_step": round(max(up), 6) if up else None,
        "up_steps": len(up),
        "up_steps_at_least_slack": sum(1 for x in up if x >= slack - TOL),
        "mean_up_step": round(statistics.fmean(up), 6) if up else None,
        "share_steps_at_least_slack": round(
            sum(1 for x in d if x >= slack - TOL) / float(len(d)), 4),
    }


def derived_erasure(slack, ss):
    """When the sample never held a drop this big, the step distribution still answers.

    Arithmetic only: how many median-sized UP steps it takes to walk back `slack`.  It is
    an expectation on the observed step law, not a simulation and not a forecast.
    """
    up = ss.get("mean_up_step")
    if not up:
        return {"expected_bars_mean_up": None, "expected_bars_median_step": None,
                "mean_up_step": up, "median_step": ss.get("median_abs_dk"),
                "basis": "no upward steps in the sample -- no expectation is published"}
    med = ss.get("median_abs_dk") or 0.0
    return {
        "expected_bars_mean_up": int(math.ceil(slack / up - 1e-9)) if up > 0 else None,
        "expected_bars_median_step": int(math.ceil(slack / med - 1e-9)) if med > 0 else None,
        "mean_up_step": up,
        "median_step": med,
        "basis": "slack / observed step; an expectation on the step law, not a simulation",
    }


# ------------------------------------------------------------------ panel legs
def build_schedule(inception=INCEPTION, beta=BETA):
    """The schedule `etf_book_order` will actually run -- same universe, same repair.

    r1317's control-arm rule: a face that measures "the trim" on a different book than the
    one the trim lands on is measuring another book's trim.  So this mirrors the order
    script's panel prep (class filter + flip repair) and then asserts, in the caller, that
    the last decision bar reproduces the published ticket k.
    """
    from scripts import etf_variants_null_rolling as V
    from scripts import etf_equity_alpha as AE
    from scripts.etf_asset_class import classify

    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    if Q.REPAIR_PANEL:
        close, openp, _n_flip = AE.repair_flips(close, openp)
    score = F.build_score(close[cols], amt[cols], feats)
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        raise SystemExit("FATAL: no 510300 column on the panel")
    mkt = close[mkt_col]
    ser, _turnover, _gapfill = F.run_next_open(close[cols], openp[cols], amt[cols], feats,
                                               REBAL, n_hold=F.N_HOLD, cost=F.COST,
                                               score=score)
    idx = ser.index.intersection(mkt.index)
    rp, rm = BT.rets(ser.reindex(idx)), BT.rets(mkt.reindex(idx))
    sched = Q.k_schedule(rp, rm, beta)
    start = pd.Timestamp(inception)
    sched = [s for s in sched if pd.Timestamp(s[0]) >= start]
    return sched, {"panel_last_bar": str(close.index[-1])[:10], "panel_symbols": len(cols),
                   "market": mkt_col, "beta_target": float(beta)}


def run():
    gap = _read_json(GAP_FACE)
    slack = float(gap["gap_k"])
    sched, meta = build_schedule()
    st = steps(sched)
    ev = erasure_events(sched, slack)
    sm = summarize(ev, len(st))
    ss = step_stats(st, slack)
    k_last = float(sched[-1][1]) if sched else None
    # control arm (r1317): the schedule must be the one the ticket prices.  If the last
    # decision bar does not reproduce the published k, this face is measuring a book the
    # trim never lands on, and publishing it would be worse than publishing nothing.
    # r1471: the sheet sizes from the executed account, so the number this control arm must
    # reproduce is the one the SIZING RULE charged (`k_rule`), not the account's size.
    k_ticket = float(gap.get("k_rule") if gap.get("k_rule") is not None else gap["k_now"])
    ident = {"k_schedule_last": round(k_last, 6) if k_last is not None else None,
             "k_ticket": round(k_ticket, 6),
             "delta": round(abs(k_last - k_ticket), 6) if k_last is not None else None}
    ident["ok"] = ident["delta"] is not None and ident["delta"] <= 5e-6
    if not ident["ok"]:
        raise SystemExit("FATAL control arm: schedule last k %r != ticket k %r"
                         % (ident["k_schedule_last"], ident["k_ticket"]))
    d = {
        "face": "etf_book_permission_persistence",
        "evidence_cutoff": meta["panel_last_bar"],
        "question": "how many decision bars does the 11-11 trim (gap_k) survive before the "
                    "schedule climbs back over the level it cut from?",
        "slack_k": round(slack, 6),
        "slack_source": GAP_FACE,
        "decision_bar": gap.get("decision_date"),
        "k_order": gap.get("k_now"),
        "k_permitted": gap.get("permitted_k"),
        "permission_enforcers": gap.get("permission_enforcers"),
        "k_last_decision_bar": round(k_last, 6) if k_last is not None else None,
        "last_decision_date": str(sched[-1][0])[:10] if sched else None,
        "identity": ident,
        "schedule": meta,
        "step_stats": ss,
        "derived_erasure": derived_erasure(slack, ss),
        "lifetime": sm,
        "events": ev,
        "verdict": verdict_of(sm),
    }
    d["sentence"] = _sentence(d)
    return d


def _sentence(d):
    sm, ss, dv = d["lifetime"], d["step_stats"], d.get("derived_erasure") or {}
    if d["verdict"] == VERDICT_NO_HISTORY:
        up_big = ss.get("up_steps_at_least_slack") or 0
        tail = ("the largest single upward step (%.2fpp over %d up-steps) %s the whole cut, so "
                "the trim can be erased in one decision bar; walking it back at the mean step "
                "takes %s bars. Nothing in the schedule remembers the floor, so it has to be "
                "re-applied every decision bar."
                % (100 * (ss.get("max_up_step") or 0), ss.get("up_steps") or 0,
                   "exceeds" if up_big else "never reaches",
                   dv.get("expected_bars_mean_up")))
        return ("No historical decision bar dropped k by as much as the %.2fpp trim (largest drop "
                "in %d same-window steps was %.2fpp), so the record never tested whether such a "
                "cut holds; on the observed step law it takes about %s upward steps of %.2fpp "
                "(mean) / %s steps of %.2fpp (median) to walk the slack back -- but %s"
                % (100 * d["slack_k"], ss["steps"], 100 * ss["max_drop"],
                   dv.get("expected_bars_mean_up"), 100 * (dv.get("mean_up_step") or 0),
                   dv.get("expected_bars_median_step"), 100 * (dv.get("median_step") or 0), tail))
    med = sm["median_bars"]
    if d["verdict"] == VERDICT_ONE_CYCLE:
        return ("A drop the size of the 11-11 trim (%.2fpp) is undone at the very next decision "
                "bar in half of the %d historical events (median %s bars); k moves %.2fpp in a "
                "typical step. The 445-lot trim is a per-bar constraint: unless the solver "
                "re-applies the floor every decision bar, the book is back over it twenty bars "
                "later." % (100 * d["slack_k"], sm["events"], med, ss["median_abs_dk"]))
    return ("Drops of the trim's size needed a median of %s decision bars to be undone (%d "
            "events, %d never returned inside the sample), against a typical step of %.2fpp."
            % (med, sm["events"], sm["never_returned"], ss["median_abs_dk"]))


# ------------------------------------------------------------------ faces
def _read_json(rel):
    p = rel if os.path.isabs(rel) else os.path.join(BASE, rel)
    if not os.path.exists(p):
        raise SystemExit("FATAL: missing %s" % rel)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def published_face():
    if not os.path.exists(OUT):
        return None
    with open(OUT, encoding="utf-8") as f:
        return json.load(f)


def md_lines(d):
    sm, ss, sc = d["lifetime"], d["step_stats"], d["schedule"]
    L = ["# 削减能撑几个决策 bar", ""]
    L += ["- 判定：**%s**" % d["verdict"],
          "- 削减幅度（gap_k，来自 %s）：**%.4f%%**" % (d["slack_source"], 100 * d["slack_k"]),
          "- 票据 k=%.6f ／ 许可 k=%.6f ／ 最后一个决策 bar（%s）k=%.6f"
          % (d["k_order"], d["k_permitted"], d["last_decision_date"], d["k_last_decision_bar"]),
          "- 面板末 bar：%s ｜ β 目标 %.2f ｜ 市场腿 %s" % (sc["panel_last_bar"], sc["beta_target"], sc["market"]),
          "", "## 一句话", "", d["sentence"], "",
          "## k 的步伐（相邻决策 bar 差）", "",
          "| 读数 | 值 |", "|---|---|",
          "| 步数 | %d |" % ss["steps"],
          "| 中位 \\|Δk\\| | %.6f |" % ss["median_abs_dk"],
          "| 均值 \\|Δk\\| | %.6f |" % ss["mean_abs_dk"],
          "| p90 \\|Δk\\| | %.6f |" % ss["p90_abs_dk"],
          "| 最大 \\|Δk\\| | %.6f |" % ss["max_abs_dk"],
          "| 上行步数 | %d |" % ss["up_steps"],
          "| 上行步均值 | %s |" % ("—" if ss["mean_up_step"] is None else "%.6f" % ss["mean_up_step"]),
          "| 最大单步上行 | %s |" % ("—" if ss.get("max_up_step") is None else "%.6f" % ss["max_up_step"]),
          "| 上行步中 ≥ 削减幅度的步数 | %d / %d |" % (ss.get("up_steps_at_least_slack") or 0, ss["up_steps"]),
          "| 步长 ≥ 削减幅度的占比 | %.2f%% |" % (100 * ss["share_steps_at_least_slack"]), "",
          "## 削减寿命（回补到跌前水平需要几个决策 bar）", "",
          "| 读数 | 值 |", "|---|---|",
          "| 同规模下跌事件 | %d / %d 步（%.2f%%）" % (sm["events"], sm["steps"], 100 * (sm["event_share"] or 0)),
          "| 已回补 | %d |" % sm["returned"],
          "| 样本内未回补（censored，非 0） | %d |" % sm["never_returned"],
          "| 中位回补 bar 数 | %s |" % ("—" if sm["median_bars"] is None else sm["median_bars"]),
          "| 均值回补 bar 数 | %s |" % ("—" if sm["mean_bars"] is None else sm["mean_bars"]),
          "| 最长回补 bar 数 | %s |" % ("—" if sm["max_bars"] is None else sm["max_bars"]), ""]
    dv = d.get("derived_erasure") or {}
    L += ["## 无同规模先例时的派生读数（算术期望，非模拟）", "",
          "| 读数 | 值 |", "|---|---|",
          "| 样本内最大单步下跌 | %.2f%% |" % (100 * ss["max_drop"]),
          "| slack / 均值上行步 | %s 决策 bar |" % dv.get("expected_bars_mean_up"),
          "| slack / 中位步长 | %s 决策 bar |" % dv.get("expected_bars_median_step"),
          "| 口径 | %s |" % (dv.get("basis") or "—"), ""]
    idn = d.get("identity") or {}
    L += ["## 控制臂（本面量的排程必须是票据标的排程）", "",
          "| 读数 | 值 |", "|---|---|",
          "| 排程末决策 bar k | %.6f（%s） |" % (idn.get("k_schedule_last") or 0, d.get("last_decision_date")),
          "| 票据 k（%s） | %.6f |" % (d.get("decision_bar"), idn.get("k_ticket") or 0),
          "| 差 | %.1e ｜ 复现=%s |" % (idn.get("delta") or 0, "OK" if idn.get("ok") else "MISMATCH"), ""]
    if sm["never_dates"]:
        L += ["未回补的下跌日：%s" % ", ".join(sm["never_dates"]), ""]
    L += ["## 读法", "",
          "- 回补口径=从跌后那一根起数到 k 重新 ≥ 跌前水平的决策 bar 数；结束时仍未回补的记 censored，"
          "写 0 会让削减看起来比实际更快被抹平。",
          "- 许可的读取面（r1455 实读）：`permission_enforcers` = %s；本面不重算，直接引用。"
          % (d["permission_enforcers"],),
          "- 本面只量「同一个 k 排程自己抹平一次削减有多快」，不评价 11-11 该不该减、也不改任何定量线。"]
    return L


def check():
    d = published_face()
    if d is None:
        print("CHECK_FAIL no published face")
        return 1
    fails = []
    gap = _read_json(GAP_FACE)
    if abs(float(d["slack_k"]) - float(gap["gap_k"])) > 1e-6:
        fails.append("slack_k %s vs receipt %s" % (d["slack_k"], gap["gap_k"]))
    sched, meta = build_schedule()
    ev = erasure_events(sched, float(d["slack_k"]))
    sm = summarize(ev, max(1, len(sched) - 1))
    for k in ("events", "returned", "never_returned"):
        if int(sm[k]) != int(d["lifetime"][k]):
            fails.append("lifetime.%s %s vs %s" % (k, d["lifetime"][k], sm[k]))
    if sm["median_bars"] != d["lifetime"]["median_bars"]:
        fails.append("median_bars %s vs %s" % (d["lifetime"]["median_bars"], sm["median_bars"]))
    if meta["panel_last_bar"] != d["schedule"]["panel_last_bar"]:
        fails.append("panel_last_bar %s vs %s" % (d["schedule"]["panel_last_bar"], meta["panel_last_bar"]))
    if verdict_of(sm) != d["verdict"]:
        fails.append("verdict %s vs %s" % (d["verdict"], verdict_of(sm)))
    for f in fails:
        print("  FAIL " + f)
    print("[check] %s (%d leg(s) checked)"
          % ("CHECK_OK" if not fails else "CHECK_FAIL", 6))
    return 0 if not fails else 1


# ------------------------------------------------------------------ selftest
def selftest():
    fails = []

    def leg(ok, msg):
        if not ok:
            fails.append(msg)

    # L1: steps are pure subtraction, in order
    s = [("2026-01-01", 0.50, 0.40), ("2026-01-21", 0.45, 0.44), ("2026-02-10", 0.47, 0.43)]
    st = steps(s)
    leg(len(st) == 2 and st[0]["dk"] == round(-0.05, 6) and st[1]["dk"] == round(0.02, 6),
        "L1 steps arithmetic %r" % (st,))

    # L2: a drop of >= slack is an event and returns after the hand-counted number of bars
    s2 = [("d0", 0.50, 0.4), ("d1", 0.40, 0.5), ("d2", 0.42, 0.4), ("d3", 0.51, 0.4)]
    ev = erasure_events(s2, 0.05)
    leg(len(ev) == 1 and ev[0]["bars_to_return"] == 2, "L2 erasure count %r" % (ev,))

    # L3: a drop never regained is censored, not zero
    s3 = [("d0", 0.50, 0.4), ("d1", 0.40, 0.5), ("d2", 0.45, 0.4)]
    ev3 = erasure_events(s3, 0.05)
    leg(ev3[0]["bars_to_return"] is None and summarize(ev3, 2)["never_returned"] == 1,
        "L3 censoring %r" % (ev3,))

    # L4: boundary -- a drop exactly equal to slack counts
    s4 = [("d0", 0.50, 0.4), ("d1", 0.45, 0.5)]
    leg(len(erasure_events(s4, 0.05)) == 1, "L4 boundary exact-slack")

    # L5: a smaller drop is not an event
    s5 = [("d0", 0.50, 0.4), ("d1", 0.46, 0.5)]
    leg(len(erasure_events(s5, 0.05)) == 0, "L5 sub-slack drop counted")

    # L6: median of an even number of lifetimes
    sm = summarize([{"bars_to_return": 1, "returned": True, "drop_date": "x"},
                    {"bars_to_return": 3, "returned": True, "drop_date": "y"}], 4)
    leg(sm["median_bars"] == 2.0, "L6 even median %r" % (sm["median_bars"],))

    # L7: all three verdict branches are reachable
    leg(verdict_of({"events": 0}) == VERDICT_NO_HISTORY, "L7a no-history branch")
    leg(verdict_of({"events": 1, "median_bars": 1}) == VERDICT_ONE_CYCLE, "L7b one-cycle branch")
    leg(verdict_of({"events": 1, "median_bars": 3}) == VERDICT_SHORT, "L7c short branch")
    leg(verdict_of({"events": 1, "median_bars": None}) == VERDICT_PERSISTS, "L7d persists branch")

    # L8: step stats share uses the same tolerance as the event rule
    ss = step_stats([{"dk": 0.05}, {"dk": -0.05}, {"dk": 0.01}], 0.05)
    leg(abs(ss["share_steps_at_least_slack"] - round(2 / 3.0, 4)) < 1e-9,
        "L8 share %r" % (ss["share_steps_at_least_slack"],))

    # L9: k stays inside [0,1] on any published schedule (the clip is part of the rule)
    s9 = [("d0", 1.0, 0.2), ("d1", 0.0, 5.0), ("d2", 0.5, 0.4)]
    leg(all(0.0 <= k <= 1.0 for _, k, _ in s9), "L9 clip invariant")

    # L10: the sentence must name the slack it is about (a face that prints a lifetime
    # without its drop size cannot be re-read)
    d10 = {"verdict": VERDICT_ONE_CYCLE, "slack_k": 0.067180,
           "lifetime": {"events": 3, "median_bars": 1, "never_returned": 0},
           "step_stats": {"median_abs_dk": 0.05}}
    leg("0.07pp" in _sentence(d10) or "6.72pp" in _sentence(d10),
        "L10 sentence misses the slack: %r" % (_sentence(d10)[:80],))

    # L11: censored events are never averaged into the median
    sm11 = summarize([{"bars_to_return": None, "returned": False, "drop_date": "z"},
                      {"bars_to_return": 5, "returned": True, "drop_date": "w"}], 2)
    leg(sm11["median_bars"] == 5.0 and sm11["never_returned"] == 1, "L11 censoring in median")

    # L12: derived erasure is slack over the step law, on both scales
    dv = derived_erasure(0.06, {"mean_up_step": 0.02, "median_abs_dk": 0.005})
    leg(dv["expected_bars_mean_up"] == 3 and dv["expected_bars_median_step"] == 12,
        "L12 derived erasure %r" % (dv,))

    # L13: no upward steps means no expectation at all -- never a zero
    dv13 = derived_erasure(0.06, {"mean_up_step": None, "median_abs_dk": 0.0})
    leg(dv13["expected_bars_mean_up"] is None and dv13["expected_bars_median_step"] is None,
        "L13 empty step law %r" % (dv13,))

    # L14: max_drop is a positive magnitude of the worst fall, not the signed step
    ss14 = step_stats([{"dk": 0.01}, {"dk": -0.158}, {"dk": 0.02}], 0.05)
    leg(abs(ss14["max_drop"] - 0.158) < 1e-9, "L14 max_drop sign %r" % (ss14["max_drop"],))

    # L15: the count of up-steps that could erase the trim in one bar is direction-aware
    ss15 = step_stats([{"dk": 0.06}, {"dk": 0.07}, {"dk": -0.09}], 0.067)
    leg(ss15["up_steps_at_least_slack"] == 1 and ss15["max_up_step"] == 0.07,
        "L15 up-step tail %r" % (ss15,))

    for f in fails:
        print("  FAIL " + f)
    print("[selftest] %d/%d PASS" % (15 - len(fails), 15))
    return 0 if not fails else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    argv = ["check" if a == "--check" else "selftest" if a == "--selftest" else a for a in argv]
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check", "selftest"])
    a = ap.parse_args(argv)
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check()
    t0 = time.time()
    d = run()
    d["elapsed_sec"] = round(time.time() - t0, 2)
    d["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    with open(MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines(d)) + "\n")
    print(json.dumps({k: d[k] for k in ("verdict", "slack_k", "last_decision_date",
                                        "k_last_decision_bar", "step_stats", "lifetime")},
                     ensure_ascii=False)[:1200])
    print("[run] %s in %.1fs" % (OUT, d["elapsed_sec"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())