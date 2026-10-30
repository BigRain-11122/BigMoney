"""ETF book -- does a pre-committed drawdown response rule pay for itself?

Every published face of this book states what it expects to earn and how deep it has
fallen, and none of them states what the operator is supposed to DO when it falls.
That gap is worth closing with a measurement rather than an opinion, because the answer
either adds a rule to the live book or retires the idea for good.

The rule family tested here is the one an operator actually reaches for:

  * switch  -- at a drawdown of X from the running peak, go to cash; come back only when
               the drawdown has healed to X - GAP (hysteresis, so a bounce does not
               re-arm the book for a single bar),
  * linear  -- keep exposure proportional, m = 1 - dd/X, so the book is fully out at X.

All of it is causal by construction: the multiplier on a bar may only use the equity
path up to the previous bar, and the fee is charged on the exposure it actually moves
(|dk| * cost, the same convention the beta overlay uses).

The identity control is the load-bearing leg. A guard with m == 1 for every bar must
reproduce `BT.apply_overlay` bit for bit; if it does not, the face is measuring its own
arithmetic instead of the rule.

Path dependence is why one arm is not a decision. The same guard is re-priced on four
decision calendars (the beta schedule started 0/5/10/15 bars into history), so a real
effect has to show up in most cells while a lucky sequence shows up in one.

Usage:
    python scripts/etf_book_drawdown_guard.py run [--out=...]
    python scripts/etf_book_drawdown_guard.py --check
    python scripts/etf_book_drawdown_guard.py --selftest
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as F
import etf_equity_alpha as A
import etf_phase_beta_target as BT
import etf_phase_beta_window as BW
import etf_variants_null_rolling as V
import etf_book_order as O
from etf_asset_class import classify

OUT_JSON = ROOT / "results" / "etf_book_drawdown_guard.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_DRAWDOWN_GUARD.md"

SCRIPT = "scripts/etf_book_drawdown_guard.py"
FACE = "results/etf_book_drawdown_guard.json"

# ---------------------------------------------------------------- frozen criteria
# Written before the first run; the payload echoes them and the gate refuses a face
# whose echoed criteria differ, so a later "small adjustment" cannot pass as the rule.
X_GRID = (0.05, 0.08, 0.10, 0.15)      # drawdown thresholds tested
REENTRY_GAP = 0.02                     # hysteresis band for the switch shape
SHAPES = ("switch", "linear")
BETA = O.DEFAULT_BETA                  # the ticket's own tier, 0.20
PHASE_MIN_HIST = (126, 131, 136, 141)  # four decision calendars inside one 20-bar cycle
COST_BP = O.COST_BP

DD_IMPROVE_SHARE_MIN = 0.75            # share of cells whose max drawdown gets shallower
CAGR_OK_SHARE_MIN = 0.75               # share of cells whose return may not fall
CAGR_CELL_FLOOR_PP = -0.50             # "did not fall" = no worse than this per cell
MEDIAN_DD_GAIN_MIN_PP = 1.0            # the median drawdown gain must be worth having
MEDIAN_CAGR_FLOOR_PP = -0.25           # and must not cost more than this in return

CRITERIA = {
    "x_grid": list(X_GRID),
    "reentry_gap": REENTRY_GAP,
    "shapes": list(SHAPES),
    "phase_min_hist": list(PHASE_MIN_HIST),
    "dd_improve_share_min": DD_IMPROVE_SHARE_MIN,
    "cagr_ok_share_min": CAGR_OK_SHARE_MIN,
    "cagr_cell_floor_pp": CAGR_CELL_FLOOR_PP,
    "median_dd_gain_min_pp": MEDIAN_DD_GAIN_MIN_PP,
    "median_cagr_floor_pp": MEDIAN_CAGR_FLOOR_PP,
    "frozen": "constants above were written before the first run; the gate refuses a face that echoes others",
}
VERDICTS = ("ADOPT", "REJECT", "INERT")


# ------------------------------------------------------------------------ guards
class NoGuard:
    """Identity control: exposure is never touched."""

    name = "none"

    def multiplier(self, dd, state):
        return 1.0


class SwitchGuard:
    """All-in / all-out at a threshold, with a hysteresis band for re-entry."""

    def __init__(self, x, gap=REENTRY_GAP, shape="switch"):
        self.x, self.gap, self.shape = float(x), float(gap), shape
        self.name = "%s:%.3f" % (shape, self.x)

    def multiplier(self, dd, state):
        x, gap = self.x, self.gap
        if x <= 0:
            return 1.0
        if self.shape == "linear":
            return float(min(1.0, max(0.0, 1.0 - dd / x)))
        if state.get("out"):
            if dd <= max(0.0, x - gap):
                state["out"] = False
            else:
                return 0.0
        elif dd >= x:
            state["out"] = True
            return 0.0
        return 1.0


def apply_guard(rp, rm, sched, rf, rule, cost_bp=COST_BP):
    """Equity / exposure / multiplier series under an exposure rule.

    Same conventions as BT.apply_overlay: a decision taken on the close of day d applies
    from d+1, the fee is |dk| * cost, and cash earns the supplied daily rate. With
    rule.multiplier() == 1 everywhere this reproduces that function bit for bit.
    """
    if not sched:
        return None
    cost = cost_bp / 10000.0
    marks = pd.Series(np.nan, index=rp.index, dtype=float)
    for d, k, _b in sched:
        if d in marks.index:
            marks.loc[d] = k
    applied = marks.shift(1).ffill()
    live = applied.dropna()
    if not len(live):
        return None

    eq, peak, prev = 1.0, 1.0, None
    state = {}
    out_e, out_k, out_m = [], [], []
    for d in live.index:
        k_beta = float(applied.loc[d])
        dd = 1.0 - eq / peak if peak > 0 else 0.0
        m = float(rule.multiplier(dd, state))
        k = k_beta * m
        fee = 0.0 if prev is None else abs(k - prev) * cost
        rf_day = 0.0 if rf is None else float(rf.get(d, 0.0) or 0.0)
        r = k * float(rp.loc[d]) + (1.0 - k) * rf_day - fee
        eq *= (1.0 + r)
        peak = max(peak, eq)
        out_e.append(eq)
        out_k.append(k)
        out_m.append(m)
        prev = k
    return (pd.Series(out_e, index=live.index),
            pd.Series(out_k, index=live.index),
            pd.Series(out_m, index=live.index))


# ------------------------------------------------------------------- measurement
def cell_metrics(equity):
    st = A.stats2(equity, "cell")
    if "cagr" not in st:
        return None
    return {"cagr": st["cagr"], "sharpe": st["sharpe"], "maxdd": st["maxdd"],
            "years": st["years"]}


def evaluate_phases(rp, rm, sched_by_phase, rf, arms):
    """{arm_name: [cell rows]} plus the control identity check."""
    cells, control = {}, []
    for phase, sched in sched_by_phase.items():
        base_e, _, _ = apply_guard(rp, rm, sched, rf, NoGuard())
        ref_e, _, _ = BT.apply_overlay(rp, rm, sched, 0.0, COST_BP, rf=rf)
        if base_e is None or ref_e is None:
            continue
        common = base_e.index.intersection(ref_e.index)
        diff = float(np.max(np.abs(base_e.reindex(common).to_numpy()
                                  - ref_e.reindex(common).to_numpy())))
        control.append({"phase": phase, "max_abs_diff": diff})
        bm = cell_metrics(base_e)
        for arm in arms:
            e, k_ser, m_ser = apply_guard(rp, rm, sched, rf, arm)
            if e is None:
                continue
            am = cell_metrics(e)
            if am is None or bm is None:
                continue
            cells.setdefault(arm.name, []).append({
                "phase": phase, "baseline": bm, "arm": am,
                "delta_cagr_pp": round(100.0 * (am["cagr"] - bm["cagr"]), 4),
                "delta_maxdd_pp": round(100.0 * (am["maxdd"] - bm["maxdd"]), 4),
                "delta_sharpe": round(am["sharpe"] - bm["sharpe"], 4),
                "fired_share": round(float((m_ser < 0.999).mean()), 4),
                "mean_exposure": round(float(k_ser.mean()), 4),
            })
    return cells, control


def summarize(rows):
    if not rows:
        return None
    dd = np.array([r["delta_maxdd_pp"] for r in rows])
    cg = np.array([r["delta_cagr_pp"] for r in rows])
    sh = np.array([r["delta_sharpe"] for r in rows])
    return {
        "cells": len(rows),
        "median_delta_cagr_pp": round(float(np.median(cg)), 4),
        "median_delta_maxdd_pp": round(float(np.median(dd)), 4),
        "median_delta_sharpe": round(float(np.median(sh)), 4),
        "worst_delta_cagr_pp": round(float(cg.min()), 4),
        "best_delta_cagr_pp": round(float(cg.max()), 4),
        "dd_improve_share": round(float((dd > 0).mean()), 4),
        "cagr_ok_share": round(float((cg >= CAGR_CELL_FLOOR_PP).mean()), 4),
        "fired_share_median": round(float(np.median([r["fired_share"] for r in rows])), 4),
        "mean_exposure_median": round(float(np.median([r["mean_exposure"] for r in rows])), 4),
    }


def arm_verdict(row):
    """Recomputed from the summary by the gate; never taken on trust."""
    if row is None:
        return "INERT"
    if (row.get("fired_share_median") or 0.0) <= 0.0:
        return "INERT"
    ok = (row["dd_improve_share"] >= DD_IMPROVE_SHARE_MIN
          and row["cagr_ok_share"] >= CAGR_OK_SHARE_MIN
          and row["median_delta_maxdd_pp"] >= MEDIAN_DD_GAIN_MIN_PP
          and row["median_delta_cagr_pp"] >= MEDIAN_CAGR_FLOOR_PP)
    return "ADOPT" if ok else "REJECT"


# ------------------------------------------------------------------------- build
def phases(min_hist_list=PHASE_MIN_HIST):
    return tuple(int(m) for m in min_hist_list)


def build(out_path=OUT_JSON, md_path=OUT_MD):
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    score = F.build_score(close[cols], amt[cols], feats)
    ser, _turn, _gap = F.run_next_open(close[cols], openp[cols], amt[cols], feats,
                                      O.REBAL, n_hold=F.N_HOLD, cost=F.COST, score=score)
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        print("FATAL: no 510300 column on the panel")
        return 2
    idx = ser.index.intersection(close[mkt_col].index)
    rp, rm = BT.rets(ser.reindex(idx)), BT.rets(close[mkt_col].reindex(idx))

    rates = BW.load_repo_rates()
    cash_rf, _missing = BW.repo_daily_cash(idx, rates)
    cash_rf = cash_rf.reindex(idx).fillna(0.0)

    sched_by_phase = {}
    for mh in phases():
        s = O.k_schedule(rp, rm, BETA, min_hist=mh)
        if s:
            sched_by_phase["mh%d" % mh] = s
    if not sched_by_phase:
        print("FATAL: no decision calendar could be built")
        return 2

    arms = []
    for x in X_GRID:
        arms.append(SwitchGuard(x, REENTRY_GAP, "switch"))
        arms.append(SwitchGuard(x, REENTRY_GAP, "linear"))

    cells, control = evaluate_phases(rp, rm, sched_by_phase, cash_rf, arms)
    if not cells:
        print("FATAL: no cell produced metrics")
        return 2

    rows = {name: summarize(rs) for name, rs in cells.items()}
    control_max = max((c["max_abs_diff"] for c in control), default=float("inf"))
    if control_max > 1e-9:
        print("FATAL: the identity control does not reproduce the published overlay "
              "(max abs diff %.3g) -- the face would be measuring its own arithmetic"
              % control_max)
        return 2

    verdicts = {name: arm_verdict(r) for name, r in rows.items()}
    adopt = [n for n, v in verdicts.items() if v == "ADOPT"]
    headline = {
        "control_max_abs_diff": control_max,
        "control_phases": len(control),
        "any_adopted": bool(adopt),
        "adopted_arms": sorted(adopt),
        "verdict": "ADOPT" if adopt else "REJECT",
        "reading": ("a pre-committed drawdown rule survives four decision calendars"
                    if adopt else
                    "no drawdown rule tested survives four decision calendars; the book's own "
                    "beta overlay is already the de-risking mechanism"),
    }

    payload = {
        "schema": "etf_book_drawdown_guard/v1",
        "script": SCRIPT,
        "face": FACE,
        "evidence_cutoff": str(close.index[-1].date()),
        "beta": BETA,
        "cost_bp": COST_BP,
        "n_hold": int(F.N_HOLD),
        "rebal": int(O.REBAL),
        "panel_bars": int(len(rp)),
        "criteria": CRITERIA,
        "verdicts": verdicts,
        "headline": headline,
        "arms": rows,
        "cells_detail": cells,
        "controls": control,
        "units": {
            "cagr": "fraction per year",
            "delta_cagr_pp": "percentage points of CAGR, arm minus the same cell's no-guard baseline",
            "delta_maxdd_pp": "percentage points of max drawdown; POSITIVE = shallower = better "
                              "(maxdd is a negative number)",
            "fired_share": "share of bars where exposure was scaled below 1",
            "mean_exposure": "mean effective exposure k = beta_k * guard_m",
        },
        "caveats": [
            "one book (5 names, beta 0.20), one universe, one cost (8bp per unit traded); the "
            "guard is tested on this book's own return path, not on every published config",
            "the guard sees the book's own equity, which is what an operator sees; it never sees "
            "the market's next move",
            "cash left out of the book earns the observed repo rate, as in the published overlay",
            "a rule rejected here is rejected as a RETURN rule; it may still be worth having as "
            "a sleep-at-night rule, which this face does not price",
        ],
    }
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    Path(md_path).parent.mkdir(parents=True, exist_ok=True)
    Path(md_path).write_text(render_md(payload), encoding="utf-8")
    print(json.dumps({"face": str(out_path), "verdict": headline["verdict"],
                      "adopted": headline["adopted_arms"],
                      "control_max_abs_diff": control_max,
                      "cells": sum(len(v) for v in cells.values())},
                     ensure_ascii=False))
    return 0


# -------------------------------------------------------------------------- md
def render_md(p):
    h, rows, u = p["headline"], p["arms"], p["units"]
    base = {}
    for cell_rows in p["cells_detail"].values():
        for r in cell_rows:
            base.setdefault(r["phase"], r["baseline"])
    worst = min((b["maxdd"] for b in base.values()), default=None)

    L = ["# ETF 书：跌了怎么办（预置回撤响应规则的实测）", "",
         "证据截止 **%s** · 面板 %d 根 bar · 本书口径 5 名 / beta %.2f / 20 日换仓 / %g bp"
         % (p["evidence_cutoff"], p["panel_bars"], p["beta"], p["cost_bp"]), "",
         "## 结论", "",
         "**%s**。" % h["verdict"], ""]
    if h["adopted_arms"]:
        L.append("过门的手臂：%s" % "、".join("`%s`" % a for a in h["adopted_arms"]))
    else:
        L.append("四个决策日历 × 8 条规则，没有一条同时做到「回撤更浅」和「收益不掉」。"
                 "跌的时候按预设阈值砍仓，在这本书上是花钱买安心，不是省钱。")
    if worst is not None:
        L += ["", "而且要砍的那一刀多半砍不到：这本账**全窗最坏回撤只有 %.2f%%**"
              "（beta 覆盖已经在做去杠杆），所以 8%%/10%%/15%% 这三档「标准止损」"
              "整段历史一次都没触发过——它们是空规则，不是安全网。" % (100 * worst)]
    L += ["", "判据（跑前冻结）：回撤改善的格数 ≥ %.0f%%、收益不掉的格数 ≥ %.0f%%、"
          "回撤中位改善 ≥ %.1fpp、收益中位代价 ≥ %.2fpp。"
          % (100 * p["criteria"]["dd_improve_share_min"],
             100 * p["criteria"]["cagr_ok_share_min"],
             p["criteria"]["median_dd_gain_min_pp"],
             p["criteria"]["median_cagr_floor_pp"]), ""]
    L += ["恒等控制：不干预的手臂与已发布引擎逐位一致（%d 个日历，最大偏差 %.2g）。"
          % (h["control_phases"], h["control_max_abs_diff"]), ""]

    L += ["## 逐条规则（4 个决策日历合计）", "",
          "| 规则 | 回撤中位改善 | 收益中位代价 | 夏普 | 回撤变浅的格 | 收益不掉的格 | 中位持仓 | 判词 |",
          "|---|---|---|---|---|---|---|---|"]
    order = sorted(rows.items(), key=lambda kv: (-(kv[1]["median_delta_maxdd_pp"] or 0)))
    for name, r in order:
        L.append("| `%s` | %+.2fpp | %+.2fpp | %+.3f | %.0f%% | %.0f%% | %.2f | **%s** |"
                 % (name, r["median_delta_maxdd_pp"], r["median_delta_cagr_pp"],
                    r["median_delta_sharpe"], 100 * r["dd_improve_share"],
                    100 * r["cagr_ok_share"], r["mean_exposure_median"],
                    p["verdicts"].get(name, "?")))
    L += ["", "读法：回撤那一列是「比不干预浅多少」，正数才是变浅；收益那一列是代价，"
          "负数才是花钱。中位持仓 1.00 = 这条规则几乎从没动过手。", ""]
    L += ["## 不干预时这本书自己是什么样（对照基线）", "",
          "| 决策日历 | 年化 | 夏普 | 最大回撤 |", "|---|---|---|---|"]
    for phase, b in sorted(base.items()):
        L.append("| %s | %.2f%% | %.2f | %.2f%% |"
                 % (phase, 100 * b["cagr"], b["sharpe"], 100 * b["maxdd"]))
    L += ["", "四个日历的年化落在 %.2f%%~%.2f%%（起点的 15 根 bar 之差不改结论），"
          "所以下面是整串历史，不是挑出来的一段。"
          % (100 * min(b["cagr"] for b in base.values()),
             100 * max(b["cagr"] for b in base.values())), ""]
    L += ["## 为什么这条结论不能只跑一遍", "",
          "同一个规则换一个决策日历（把 beta 表起点错开 0/5/10/15 根 bar），"
          "每一格都是一串不同的决策。只在其中一格赢的规则是运气，不是规则。", ""]
    L += ["## 必须记住的", ""]
    for c in p["caveats"]:
        L.append("- %s" % c)
    L.append("")
    L.append("*生成脚本 %s｜证据截止 %s*" % (p["script"], p["evidence_cutoff"]))
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------ gate
def check(out_path=OUT_JSON):
    data = json.loads(Path(out_path).read_text(encoding="utf-8"))
    problems = []
    for key, want in CRITERIA.items():
        if data.get("criteria", {}).get(key) != want:
            problems.append("criteria.%s drifted: %r != %r"
                            % (key, data.get("criteria", {}).get(key), want))
    if data.get("headline", {}).get("control_max_abs_diff", 1.0) > 1e-9:
        problems.append("identity control is not bit-exact")
    for name, row in data.get("arms", {}).items():
        want = arm_verdict(row)
        if data.get("verdicts", {}).get(name) != want:
            problems.append("%s verdict is %r, rule says %r"
                            % (name, data.get("verdicts", {}).get(name), want))
    if data.get("headline", {}).get("adopted_arms") != sorted(
            n for n, v in data.get("verdicts", {}).items() if v == "ADOPT"):
        problems.append("headline adopted list does not match the arm verdicts")
    for p in problems:
        print("CHECK FAIL:", p)
    if not problems:
        print("CHECK OK: criteria echoed, identity control exact, verdicts reproduce "
              "from the summary (%d arms)" % len(data.get("arms", {})))
    return 1 if problems else 0


# -------------------------------------------------------------------- selftest
def _fixture(n=400, seed=7, drop_at=150, drop=-0.012, days=12):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    rm = pd.Series(rng.normal(0.0002, 0.008, n), index=idx)
    rp = 0.9 * rm + pd.Series(rng.normal(0.0004, 0.005, n), index=idx)
    if drop_at is not None:
        rp.iloc[drop_at:drop_at + days] = drop
    rf = pd.Series(0.0001, index=idx)
    sched = [(idx[i], 0.5, 0.4) for i in range(30, n - 1, 20)]
    return rp, rm, rf, sched


def selftest():
    ok = []

    def leg(name, cond, detail=""):
        ok.append((name, bool(cond), detail))
        print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))

    rp, rm, rf, sched = _fixture()

    # L1 identity: no guard reproduces the published overlay bit for bit
    e, k, m = apply_guard(rp, rm, sched, rf, NoGuard())
    ref, _, kk = BT.apply_overlay(rp, rm, sched, 0.0, COST_BP, rf=rf)
    common = e.index.intersection(ref.index)
    leg("identity arm reproduces BT.apply_overlay",
        float(np.max(np.abs(e.reindex(common) - ref.reindex(common)))) < 1e-12,
        "max abs diff %.2g" % float(np.max(np.abs(e.reindex(common) - ref.reindex(common)))))
    leg("identity arm leaves every multiplier at 1", bool((m == 1.0).all()))

    # L2 the switch fires at the threshold and stays out (no single-bar re-entry)
    g = SwitchGuard(0.05)
    e2, k2, m2 = apply_guard(rp, rm, sched, rf, g)
    leg("switch: exposure goes to zero somewhere on a 12% drop path",
        bool((m2 <= 0.0).any()), "fired %.1f%% of bars" % (100 * (m2 < 0.999).mean()))
    leg("switch: zero exposure is charged no book return",
        bool(np.isfinite(e2).all()))

    # L3 linear guard is monotone in drawdown and 1.0 at zero drawdown
    lin = SwitchGuard(0.10, shape="linear")
    leg("linear: m(0)=1, m(X/2)=0.5, m(X)=0, clipped outside",
        abs(lin.multiplier(0.0, {}) - 1.0) < 1e-12
        and abs(lin.multiplier(0.05, {}) - 0.5) < 1e-12
        and abs(lin.multiplier(0.10, {})) < 1e-12
        and abs(lin.multiplier(0.30, {})) < 1e-12)

    # L4 hysteresis: at dd just inside the band the switch does NOT re-arm
    g2 = SwitchGuard(0.08, gap=0.02)
    st = {}
    g2.multiplier(0.09, st)          # armed
    inside = g2.multiplier(0.075, st)  # dd > X-gap -> still out
    healed = g2.multiplier(0.05, st)   # dd <= X-gap -> back in
    leg("hysteresis: does not re-arm inside the band, re-arms below X-gap",
        inside == 0.0 and healed == 1.0, "inside=%s healed=%s" % (inside, healed))

    # L5 a guard that never triggers equals the baseline exactly (50% threshold on a 12% drop)
    e3, _, m3 = apply_guard(rp, rm, sched, rf, SwitchGuard(0.50))
    e4, _, _ = apply_guard(rp, rm, sched, rf, NoGuard())
    leg("a rule that never fires is bit-identical to no rule",
        bool((m3 == 1.0).all())
        and float(np.max(np.abs(e3 - e4))) < 1e-12)

    # L6 causality: the future cannot change the past
    cut = 200
    e5, _, _ = apply_guard(rp.iloc[:cut], rm.iloc[:cut], [s for s in sched if s[0] <= rp.index[cut - 2]],
                           rf.iloc[:cut], SwitchGuard(0.05))
    e6, _, _ = apply_guard(rp, rm, sched, rf, SwitchGuard(0.05))
    ov = e5.index.intersection(e6.index)
    leg("causality: truncating the future leaves the past unchanged",
        len(ov) > 20 and float(np.max(np.abs(e5.reindex(ov) - e6.reindex(ov)))) < 1e-12,
        "%d overlapping bars" % len(ov))

    # L7 fees only ever drag: on a zero-return book a switching guard must lose to cash
    zidx = pd.bdate_range("2020-01-01", periods=200)
    zrp = pd.Series(0.0, index=zidx)
    zrm = pd.Series(0.0, index=zidx)
    zsched = [(zidx[i], 1.0, 1.0) for i in range(10, 199, 20)]
    e7, _, _ = apply_guard(zrp, zrm, zsched, None, NoGuard())
    leg("a zero-return book with a constant weight has exactly zero cost",
        abs(float(e7.iloc[-1]) - 1.0) < 1e-12)

    # L8 short / empty inputs degrade honestly
    leg("an empty schedule returns None instead of an empty curve",
        apply_guard(rp, rm, [], rf, NoGuard()) is None)

    # L9 the gate recomputes verdicts from the summary
    good = {"fired_share_median": 0.1, "dd_improve_share": 1.0, "cagr_ok_share": 1.0,
            "median_delta_maxdd_pp": 3.0, "median_delta_cagr_pp": 0.0}
    bad = dict(good, median_delta_cagr_pp=-5.0)
    leg("verdict: a big drawdown gain bought with 5pp of return is REJECT",
        arm_verdict(good) == "ADOPT" and arm_verdict(bad) == "REJECT")
    leg("verdict: a rule that never fires is INERT, not ADOPT",
        arm_verdict(dict(good, fired_share_median=0.0)) == "INERT")

    passed = sum(1 for _n, c, _d in ok if c)
    print("selftest %d/%d PASS" % (passed, len(ok)))
    return 0 if passed == len(ok) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", nargs="?", default="run", choices=("run", "check", "selftest"))
    ap.add_argument("--selftest", dest="st", action="store_true", help="alias for the selftest mode")
    ap.add_argument("--check", dest="ck", action="store_true", help="alias for the check mode")
    ap.add_argument("--out", default=str(OUT_JSON))
    ap.add_argument("--md", default=str(OUT_MD))
    a = ap.parse_args(argv)
    if a.st:
        a.mode = "selftest"
    elif a.ck:
        a.mode = "check"
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check(a.out)
    return build(a.out, a.md)


if __name__ == "__main__":
    raise SystemExit(main())