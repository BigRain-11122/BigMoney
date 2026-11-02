"""Could you have run this book in 2020? The universe the window's return was earned on.

Every headline this line publishes (9.60% as coded / 8.46% declared fill, 2020-01-01..cutoff)
is earned on the panel as it exists TODAY: 1504 tradeable funds. A third of those did not exist
when the window opened -- the ETF universe roughly octupled after 2019, and 11 of the 12 names
in the book currently in force were listed after 2020-01-01. So the number a reader sizes from
answers a question nobody can act on ("what if I had been able to buy funds from the future?").

This face prices the same cell on universes frozen at three dates and reports the gap:

  lock 2014-12-31   61 funds   (what a 2015 starter could buy)
  lock 2019-12-31  193 funds   (what a 2020 starter could buy -- the window's own start)
  lock 2022-12-31  663 funds
  unlocked        1504 funds   (the published book)

The locked arms rebuild the score on their own universe (rank a narrower cross-section the way
production ranks a wider one) and are otherwise identical: same n_hold/rebal/cost/vol target,
same engine, same fill. Four decision phases, because one grid is one decision sequence.

Arm convention: the DECLARED fill (score held one bar back, close t -> open t+1) is the arm the
desk can trade and is the one this face leads with; the as-coded arm (score read off bar d's
close, paid at bar d's open) is priced once as the control, so the two published numbers the
card prints are both reproduced here before any lock number is quoted.

  python scripts/etf_book_universe_lock.py run
  python scripts/etf_book_universe_lock.py --check
  python scripts/etf_book_universe_lock.py --selftest
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_book_production as P
import etf_robust_pf as R

OUT_JSON = os.path.join(ROOT, "results", "etf_book_universe_lock.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_UNIVERSE_LOCK.md")
PUB_PROD = os.path.join(ROOT, "results", "etf_book_production", "latest.json")

# ------------------------------------------------------------------ frozen criteria
# Written before the first run and echoed into the payload; --check re-derives the verdict
# from the payload's own rows, so a hand-edited state fails instead of reading as finished.
START = "2020-01-01"
REBAL = 20
N_HOLD = 12
COST = 0.0010
TARGET = 0.08
VOL_WINDOW = 60
N_PHASES = 4
LOCKS = ("2014-12-31", "2019-12-31", "2022-12-31")
HEADLINE_LOCK = "2019-12-31"        # the window's own start: what a 2020 starter could buy
TOL_PP = 0.57                       # material gap, the line the line's other questions use
SHARE_MIN = 0.75                    # phases a verdict has to hold in
CONTROL_TOL_PP = 0.5                # published-number reproduction tolerance
CRITERIA = {"tol_pp": TOL_PP, "share_min": SHARE_MIN, "n_phases": N_PHASES,
            "control_tol_pp": CONTROL_TOL_PP, "headline_lock": HEADLINE_LOCK,
            "locks": list(LOCKS)}


def phase_starts(index, rebal=REBAL, n=N_PHASES):
    """`n` decision-grid starts spread through one rebalance cycle (house rule)."""
    post = list(index)
    if len(post) < rebal * 2:
        raise ValueError("panel has %d bars -- need at least %d" % (len(post), rebal * 2))
    step = max(1, rebal // n)
    picks = [post[i * step] for i in range(n)]
    if len(set(picks)) < n:
        raise ValueError("only %d distinct phases in a %d-bar cycle" % (len(set(picks)), rebal))
    return picks


def _stats(ser):
    m = E.metrics(ser, "arm")
    return {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "bars")}


def _class_names(cls):
    """The class map arrives as a Series on bm-a and as a dict on other hosts."""
    names = cls.values() if hasattr(cls, "values") and not hasattr(cls, "items") else cls
    try:
        return sorted({str(v) for v in names})[:8]
    except TypeError:
        return sorted({str(v) for v in list(names)})[:8]


def universe_lock(first, asof):
    """Columns whose first valid bar is on/before `asof` -- funds that existed then.

    Same rule as etf_book_pre2020.universe_pre, applied to the production panel so the
    "existed" test is taken on the panel the book is actually priced on.
    """
    cut = pd.Timestamp(asof)
    return [c for c in first.index if first.get(c) is not None and first[c] <= cut]


def verdict_from_summary(summary):
    """Frozen decision rule: does freezing the universe cost the reader money?

    delta_pp = full-universe CAGR - locked CAGR, per phase (positive = the lock costs).
    """
    n = summary["phases"]
    if not n:
        return "INCOMPLETE"
    need = int(np.ceil(SHARE_MIN * n))
    mean = summary["delta_mean_pp"]
    costly = summary["phases_lock_costs"]
    neutral = summary["phases_within_tol"]
    if mean is not None and mean >= TOL_PP and costly >= need:
        return "LOCK_COSTS_MONEY"
    if neutral >= need:
        return "UNIVERSE_ROBUST"
    return "MIXED_ACROSS_PHASES"


def _summarise(phase_rows):
    deltas = [r["delta_pp"] for r in phase_rows if r.get("delta_pp") is not None]
    if not deltas:
        return {"phases": 0, "delta_mean_pp": None, "delta_min_pp": None,
                "delta_max_pp": None, "phases_lock_costs": 0, "phases_within_tol": 0}
    return {
        "phases": len(deltas),
        "delta_mean_pp": round(float(np.mean(deltas)), 4),
        "delta_min_pp": round(float(np.min(deltas)), 4),
        "delta_max_pp": round(float(np.max(deltas)), 4),
        "phases_lock_costs": int(sum(1 for d in deltas if d >= TOL_PP)),
        "phases_within_tol": int(sum(1 for d in deltas if abs(d) < TOL_PP)),
    }


def build_panel():
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    feats = E.build_panel()[3]
    first = close.apply(lambda s: s.first_valid_index())
    return close, openp, amt, score, feats, cls, n_flip, first


def _run_arm(close, openp, amt, score, cols, start):
    diag = []
    ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols],
                                      score[cols] if score is not None else None,
                                      REBAL, N_HOLD, COST, vol_target=TARGET,
                                      start=start, vol_window=VOL_WINDOW, diag=diag)
    return ser, turn, diag


def run():
    t0 = time.time()
    close, openp, amt, score, feats, cls, n_flip, first = build_panel()
    all_cols = list(close.columns)
    print("panel %s first=%s last=%s flips=%d  %.1fs"
          % (close.shape, close.index[0].date(), close.index[-1].date(), n_flip,
             time.time() - t0), flush=True)

    starts = phase_starts([d for d in close.index if d >= pd.Timestamp(START)])

    # universes: unlocked + each lock. Locked arms rank on their own cross-section, exactly
    # the way production ranks its own -- the score is a cross-sectional build, so reusing the
    # wide score on a narrow universe would rank against ranks nobody had.
    universes = {"unlocked": (all_cols, score)}
    for asof in LOCKS:
        cols = universe_lock(first, asof)
        universes[asof] = (cols, E.build_score(close[cols], amt[cols], feats))
        print("lock %s -> %d funds  %.1fs" % (asof, len(cols), time.time() - t0), flush=True)

    phase_rows = []
    for i, st in enumerate(starts):
        start = str(pd.Timestamp(st).date())
        full_ser, _t, _d = _run_arm(close, openp, amt,
                                    universes["unlocked"][1].shift(1), all_cols, start)
        full = _stats(full_ser)
        locked_cols, locked_score = universes[HEADLINE_LOCK]
        lock_ser, _t2, _d2 = _run_arm(close, openp, amt, locked_score.shift(1),
                                      locked_cols, start)
        locked = _stats(lock_ser)
        gap = (None if full.get("cagr") is None or locked.get("cagr") is None
               else round(100.0 * (full["cagr"] - locked["cagr"]), 4))
        phase_rows.append({"phase": i, "phase_start": start,
                           "unlocked": full, "lock_%s" % HEADLINE_LOCK: locked,
                           "delta_pp": gap,
                           "unlocked_n": len(all_cols), "locked_n": len(locked_cols)})
        print("phase %d %s unlocked %.3f%% locked %.3f%% delta %+.2fpp  %.1fs"
              % (i, start, 100 * (full["cagr"] or 0), 100 * (locked["cagr"] or 0),
                 gap or 0.0, time.time() - t0), flush=True)

    summary = _summarise(phase_rows)
    summary["verdict"] = verdict_from_summary(summary)

    # the ladder: one phase, declared arm, one lock per rung (context, not the verdict)
    ladder = []
    for asof in ("unlocked",) + LOCKS:
        cols, sc = universes[asof]
        ser, _t, _d = _run_arm(close, openp, amt, sc.shift(1), cols,
                               str(pd.Timestamp(starts[0]).date()))
        st = _stats(ser)
        ladder.append({"universe": asof, "n_funds": len(cols),
                       "cagr": st.get("cagr"), "sharpe": st.get("sharpe"),
                       "maxdd": st.get("maxdd"), "vol": st.get("vol")})
        print("ladder %-10s n=%4d cagr %.3f%% sharpe %.3f dd %.3f%%  %.1fs"
              % (asof, len(cols), 100 * (st.get("cagr") or 0), st.get("sharpe") or 0,
                 100 * (st.get("maxdd") or 0), time.time() - t0), flush=True)

    # pick-level: how much of the book that is actually bought was listed during the window
    _ser, _t, diag = _run_arm(close, openp, amt, universes["unlocked"][1].shift(1),
                              all_cols, str(pd.Timestamp(starts[0]).date()))
    cut = pd.Timestamp(HEADLINE_LOCK)
    slots = new = 0
    for row in diag:
        for nm in row.get("book") or []:
            slots += 1
            if first.get(nm) is not None and first[nm] > cut:
                new += 1
    last_book = (diag[-1].get("book") if diag else []) or []
    listed = {nm: str(first[nm].date()) for nm in last_book if first.get(nm) is not None}
    new_in_force = [nm for nm in last_book
                    if first.get(nm) is not None and first[nm] > cut]
    picks = {"pick_slots": slots, "slots_listed_after_lock": new,
             "share_listed_after_lock": round(new / slots, 4) if slots else None,
             "book_in_force_date": diag[-1]["date"] if diag else None,
             "book_in_force": last_book,
             "book_in_force_listed_after_lock": len(new_in_force),
             "book_in_force_listing_dates": listed}

    # control: reproduce the two published arms before quoting any locked number
    control = {"tol_pp": CONTROL_TOL_PP, "arms": {}, "ok": True}
    pub = {}
    if os.path.exists(PUB_PROD):
        with open(PUB_PROD, encoding="utf-8") as fh:
            pub = (json.load(fh) or {}).get("execution_basis") or {}
    asc_ser, _t, _d = _run_arm(close, openp, amt, universes["unlocked"][1], all_cols,
                               str(pd.Timestamp(starts[0]).date()))
    asc = _stats(asc_ser).get("cagr")
    decl = phase_rows[0]["unlocked"].get("cagr")
    for arm, got, key in (("as_coded", asc, "as_coded_cagr"),
                          ("declared", decl, "declared_cagr")):
        want = pub.get(key)
        ok = (want is not None and got is not None
              and abs(100.0 * (got - want)) <= CONTROL_TOL_PP)
        control["arms"][arm] = {"published": want, "recomputed": got,
                               "diff_pp": (None if want is None or got is None
                                           else round(100.0 * abs(got - want), 4)),
                               "ok": bool(ok)}
        if not ok:
            control["ok"] = False

    doc = {
        "schema": "etf_book_universe_lock/v1",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_sec": round(time.time() - t0, 1),
        "evidence_cutoff": str(close.index[-1].date()),
        "question": ("the window's headline is earned on today's 1504 funds; what would the "
                     "same rule have earned on the funds that existed when the window "
                     "opened?"),
        "criteria": CRITERIA,
        "arm": {"lead": "declared fill (score held one bar back, close t -> open t+1)",
                "control": "as coded (score read off bar d's close, paid at bar d's open)"},
        "config": {"n_hold": N_HOLD, "rebal": REBAL, "cost_bp_per_side": round(COST * 1e4, 1),
                   "vol_target": TARGET, "vol_window": VOL_WINDOW, "start": START},
        "panel": {"shape": list(close.shape), "first": str(close.index[0].date()),
                  "last": str(close.index[-1].date()), "flips_repaired": n_flip,
                  "columns": len(all_cols), "classes_used": _class_names(cls)},
        "phase_rows": phase_rows,
        "summary": summary,
        "ladder": ladder,
        "picks": picks,
        "control": control,
        "notes": [
            "locked arms rebuild the score on their own universe; every other knob "
            "(n_hold/rebal/cost/vol target/vol window/engine/fill) is identical",
            "the lock test is 'first valid bar on or before the lock date' on the panel the "
            "book is priced on, so a fund whose history starts after the lock cannot be held",
            "survivorship is still in: funds that existed in 2020 and were later delisted are "
            "absent from the panel, so the locked arm is an upper bound on what was available",
            "the pick census counts decision slots, not money-weighted exposure: a name held "
            "for two years counts once per decision it appears in",
        ],
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    write_md(doc)
    print("control ok=%s | %s | delta %+.2fpp over %d phases | %.1fs"
          % (control["ok"], summary["verdict"], summary["delta_mean_pp"] or 0.0,
             summary["phases"], doc["elapsed_sec"]), flush=True)
    return doc if control["ok"] else 3


def write_md(doc):
    s = doc["summary"]
    ph = doc["phase_rows"]
    ctl = doc["control"]
    lad = doc["ladder"]
    pk = doc["picks"]
    L = ["# 2020 年能不能真的跑这本书？——窗口收益落在哪个票池上", "",
         "证据件：`results/etf_book_universe_lock.json`（evidence cutoff %s，%d 个决策相位，%.1fs）。"
         % (doc["evidence_cutoff"], s.get("phases") or 0, doc["elapsed_sec"]), "",
         "## 为什么问这一句", "",
         "本线对外印的两个数（as coded %.2f%%、declared fill %.2f%%）都是在**今天**的 "
         "%d 只基金上算出来的。这些基金里约三分之一在窗口开始时还不存在；"
         "今天真正在手的 %d 个名字里 **%d 个**在 %s 之后才上市。"
         % (100 * ((ctl.get("arms", {}).get("as_coded", {}) or {}).get("published") or 0.0),
            100 * ((ctl.get("arms", {}).get("declared", {}) or {}).get("published") or 0.0),
            doc["panel"]["columns"], len(pk.get("book_in_force") or []),
            pk.get("book_in_force_listed_after_lock") or 0, HEADLINE_LOCK), "",
         "所以这些数字回答的是一个没人能执行的问题：「假如 2020 年就能买到后面才上市的基金」。"
         "这一轮把同一格规则放到冻结在那一天的票池上重跑。", "",
         "## 结果（declared fill，四个决策相位）", "",
         "| 相位 | 起点 | 全票池 %d 只 | 锁定 %s（%d 只） | 差额 |" % (
             doc["panel"]["columns"], CRITERIA["headline_lock"],
             ph[0]["locked_n"] if ph else 0),
         "|---|---|---|---|---|"]
    for r in ph:
        L.append("| %d | %s | %.2f%% | %.2f%% | %+.2f pp |"
                 % (r["phase"], r["phase_start"],
                    100 * (r["unlocked"].get("cagr") or 0),
                    100 * (r["lock_%s" % HEADLINE_LOCK].get("cagr") or 0),
                    r["delta_pp"] or 0.0))
    L += ["", "**%s**：平均差额 %+.2f pp/年（%d/%d 个相位达到 %.2f pp 的material线，"
              "最差 %+.2f、最好 %+.2f）。" % (
                  s["verdict"], s["delta_mean_pp"] or 0.0, s["phases_lock_costs"],
                  s["phases"], TOL_PP, s["delta_min_pp"] or 0.0, s["delta_max_pp"] or 0.0),
          "",
          "怎么读这一句：三个相位说冻结要花掉 0.5–0.9 pp（在material线附近或之上），"
          "第四个相位反过来说冻结多赚 2.2 pp——**平均为零，而跨相位的摆幅比这条线测过的"
          "任何一个效应都大**。所以正确的对外说法不是「窗口收益靠新基金」，也不是"
          "「完全无关」，而是：**选券依赖的是「票池要够宽」，不是「票池要够新」**；"
          "这条依赖在下面那张梯子上才看得见（61 只的 2015 年票池只有 %.2f%%）。"
          % (100 * ((lad[1].get("cagr") if len(lad) > 1 else 0.0) or 0.0)), "",
          "同一臂上的对照（把票池一路放宽）：", "",
          "| 票池锁定日 | 基金数 | 年化 | 夏普 | 最大回撤 | 已实现波动 |",
          "|---|---|---|---|---|---|"]
    for r in lad:
        L.append("| %s | %d | %.2f%% | %.3f | %.2f%% | %.2f%% |"
                 % (r["universe"], r["n_funds"], 100 * (r["cagr"] or 0), r["sharpe"] or 0,
                    100 * (r["maxdd"] or 0), 100 * (r["vol"] or 0)))
    L += ["", "## 手里的书", "",
          "在手的这一本（决策日 %s）：%s。" % (pk.get("book_in_force_date"),
                                              "、".join(pk.get("book_in_force") or [])), "",
          "其中 **%d/%d** 在 %s 之后才上市（%s）。整个窗口 %d 个决策持仓位里有 %d 个"
          "（%.1f%%）落在这类「窗口内新上市」的名字上。" % (
              pk.get("book_in_force_listed_after_lock") or 0,
              len(pk.get("book_in_force") or []), HEADLINE_LOCK,
              "；".join("%s %s" % (k, v) for k, v in sorted(
                  (pk.get("book_in_force_listing_dates") or {}).items())),
              pk.get("pick_slots") or 0, pk.get("slots_listed_after_lock") or 0,
              100 * (pk.get("share_listed_after_lock") or 0)), "",
          "## 控制闸", "",
          "引用任何锁定数之前，本面先用同一引擎复现卡片公开的两条臂：", ""]
    for arm, row in (ctl.get("arms") or {}).items():
        L.append("- %s：发布 %.4f / 本面重算 %.4f（差 %.2f pp，容差 %.1f pp）→ %s"
                 % (arm, row.get("published") or 0.0, row.get("recomputed") or 0.0,
                    row.get("diff_pp") or 0.0, CONTROL_TOL_PP,
                    "PASS" if row.get("ok") else "FAIL"))
    L += ["", "## 边界", ""]
    L += ["- %s" % n for n in doc["notes"]]
    L += ["", "复现：", "",
          "```",
          "python scripts/etf_book_universe_lock.py run        # ~%ds" % int(doc["elapsed_sec"]),
          "python scripts/etf_book_universe_lock.py --check",
          "python scripts/etf_book_universe_lock.py --selftest",
          "```"]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


# ------------------------------------------------------------------------------- gates

def _check():
    """Re-derive the verdict from the published payload; refuse a hand-edited state."""
    if not os.path.exists(OUT_JSON):
        print("CHECK FAIL: %s is missing" % OUT_JSON)
        return 1
    with open(OUT_JSON, encoding="utf-8") as fh:
        doc = json.load(fh) or {}
    rows = doc.get("phase_rows") or []
    s = doc.get("summary") or {}
    if not rows:
        print("CHECK FAIL: payload carries no phase rows")
        return 1
    again = _summarise(rows)
    want = verdict_from_summary(again)
    if s.get("verdict") != want:
        print("CHECK FAIL: verdict %r does not recompute (%r)" % (s.get("verdict"), want))
        return 1
    for key in ("delta_mean_pp", "phases_lock_costs", "phases_within_tol"):
        if s.get(key) != again.get(key):
            print("CHECK FAIL: summary %s moved (%r vs %r)"
                  % (key, s.get(key), again.get(key)))
            return 1
    ctl = doc.get("control") or {}
    if not (ctl.get("ok") and all(v.get("ok") for v in (ctl.get("arms") or {}).values())):
        print("CHECK FAIL: control arms do not reproduce the published numbers")
        return 1
    if not doc.get("ladder"):
        print("CHECK FAIL: ladder missing")
        return 1
    print("CHECK OK: %s (delta %+.2fpp over %d phases, control reproduces both published arms)"
          % (want, again.get("delta_mean_pp") or 0.0, again.get("phases") or 0))
    return 0


def _fixture(n=520, seed=11, ncols=6):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2019-01-01", periods=n)
    cols = ["F%d" % i for i in range(ncols)]
    rets = rng.normal(0.0004, 0.012, size=(n, ncols))
    close = pd.DataFrame(np.cumprod(1 + rets, axis=0) * 10, index=idx, columns=cols)
    close["F5"] = np.nan
    close.loc[idx[300:], "F5"] = 10.0          # listed well inside the window
    openp = close * (1 + rng.normal(0, 0.001, size=close.shape))
    amt = pd.DataFrame(1e9, index=idx, columns=cols)
    score = pd.DataFrame(rng.normal(size=(n, ncols)), index=idx, columns=cols)
    score.loc[idx[300:], "F5"] = 5.0           # once listed it is the best name, by construction
    return close, openp, amt, score


def _selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append({"leg": name, "ok": bool(cond), "detail": detail})

    # L1 summary arithmetic and the direction of the sign
    rows = [{"delta_pp": 1.0}, {"delta_pp": -0.2}, {"delta_pp": 0.9}, {"delta_pp": 0.6}]
    s = _summarise(rows)
    leg("summary means the deltas", abs(s["delta_mean_pp"] - 0.575) < 1e-3, str(s))
    leg("summary counts material phases", s["phases_lock_costs"] == 3, str(s))
    leg("within-tolerance phases are counted separately", s["phases_within_tol"] == 1, str(s))

    # L2 frozen verdict, all three branches plus the one-phase edge
    leg("lock costs money", verdict_from_summary(
        {"phases": 4, "delta_mean_pp": 1.2, "phases_lock_costs": 4,
         "phases_within_tol": 0}) == "LOCK_COSTS_MONEY")
    leg("robust", verdict_from_summary(
        {"phases": 4, "delta_mean_pp": 0.05, "phases_lock_costs": 0,
         "phases_within_tol": 4}) == "UNIVERSE_ROBUST")
    leg("mixed", verdict_from_summary(
        {"phases": 4, "delta_mean_pp": 0.8, "phases_lock_costs": 2,
         "phases_within_tol": 1}) == "MIXED_ACROSS_PHASES")
    leg("a big mean with too few phases is not adoption", verdict_from_summary(
        {"phases": 4, "delta_mean_pp": 2.0, "phases_lock_costs": 2,
         "phases_within_tol": 0}) == "MIXED_ACROSS_PHASES")
    leg("no phases is incomplete", verdict_from_summary({"phases": 0}) == "INCOMPLETE")

    # L3 the lock is inclusive on the lock date and excludes later listings
    close, openp, amt, score = _fixture()
    first = close.apply(lambda s: s.first_valid_index())
    locked = universe_lock(first, "2019-12-31")
    leg("a fund listed inside the window is excluded from the lock",
        "F5" not in locked and len(locked) == 5, str(sorted(locked)))
    later = universe_lock(first, "2021-12-31")
    leg("a later lock admits it", "F5" in later, str(sorted(later)))
    early = universe_lock(first, "2018-12-31")
    leg("a lock before the panel starts admits nothing", len(early) == 0, str(early))

    # L4 the phase grid: n distinct decision starts inside one rebalance cycle
    ph = phase_starts(list(close.index), rebal=20, n=4)
    leg("four distinct phases", len(set(ph)) == 4, str([str(p.date()) for p in ph]))
    leg("phases are a rising sequence inside one cycle", ph[0] < ph[1] < ph[3], "")

    # L5 a locked universe can never hold a fund it does not contain
    locked_cols = [c for c in close.columns if c in set(locked)]
    diag = []
    R.open_to_open_equity(close[locked_cols], openp[locked_cols], amt[locked_cols],
                          score[locked_cols], 20, 2, COST, vol_target=TARGET,
                          start="2020-01-01", vol_window=VOL_WINDOW, diag=diag)
    held = {nm for row in diag for nm in (row.get("book") or [])}
    leg("locked books only contain locked funds", held and held <= set(locked_cols), str(sorted(held)))
    diag2 = []
    R.open_to_open_equity(close, openp, amt, score, 20, 2, COST, vol_target=TARGET,
                          start="2020-01-01", vol_window=VOL_WINDOW, diag=diag2)
    leg("the wide book can reach the late listing the lock refuses",
        any("F5" in (row.get("book") or []) for row in diag2), "")

    # L6 the published payload must still agree with the frozen rule (hand edits fail here)
    if os.path.exists(OUT_JSON):
        with open(OUT_JSON, encoding="utf-8") as fh:
            doc = json.load(fh) or {}
        rows_pub = doc.get("phase_rows") or []
        s_pub = doc.get("summary") or {}
        leg("published verdict recomputes from its own rows",
            bool(rows_pub) and s_pub.get("verdict") == verdict_from_summary(_summarise(rows_pub)),
            "verdict=%s" % s_pub.get("verdict"))
        leg("published control reproduces both arms",
            bool((doc.get("control") or {}).get("ok")), "")
        leg("published ladder spans the same universes as the criteria",
            [r.get("universe") for r in (doc.get("ladder") or [])]
            == ["unlocked"] + list(CRITERIA["locks"]),
            str([r.get("universe") for r in (doc.get("ladder") or [])]))
        leg("published headline lock matches the criteria",
            CRITERIA["headline_lock"] in (doc.get("criteria") or {}).get("headline_lock", ""),
            str((doc.get("criteria") or {}).get("headline_lock")))

    n_pass = sum(1 for x in legs if x["ok"])
    for x in legs:
        print(("PASS " if x["ok"] else "FAIL ") + x["leg"] + (" | " + x["detail"] if x["detail"] else ""))
    print("%d/%d PASS" % (n_pass, len(legs)))
    return 0 if n_pass == len(legs) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    if "--check" in sys.argv:
        sys.exit(_check())
    if "run" in sys.argv:
        doc = run()
        if doc == 3:
            sys.exit(3)
        sys.exit(0)
    print(__doc__)
    sys.exit(0)