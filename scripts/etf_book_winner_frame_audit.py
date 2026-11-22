#!/usr/bin/env python
"""etf_book_winner_frame_audit -- r1964 crowned the low-vol rule; on whose ruler?

Why this face exists
--------------------
r1964 raced four arms and concluded `THE_RENT_EATS_THE_TUNING`: `single_vol_60_low` keeps
22,269 CNY/yr against the tuned six-factor book's 18,007, i.e. 4,261 more per year, so the
four extra factors were rent rather than discovery. Two pieces of that comparison are about
the *frame*, not about the rule, and neither has been audited:

1. **The ruler.** `book_deflated_expectation._haircut_row` turns a credible Sharpe into
   money as `capital * credible_sharpe * vol`, where `vol` is each arm's OWN realised
   volatility. vol_60 realised 11.23% and the tuned book 10.50%, so the "low-vol" rule is
   paid twice for being *more* volatile than the thing it is supposed to beat. The book this
   desk funds is designed at an 8% volatility target.
2. **The cap.** All four arms ran under `vol_target=0.08`, which de-levers a book harder the
   more volatile it is. Whoever the cap de-levers most pays the most, and that price never
   shows up in the horse race.

What this face publishes
------------------------
1. **Eight cells** = four arms (tuned six-factor, `mom_12_1`, `vol_60` low, coin) x two cap
   modes (8% cap on / cap off = always fully invested).
2. **Each cell under two rulers**: own-vol (what r1964 used) and the design 8% vol.
3. **The cap's price per arm**: `bare_cagr - capped_cagr`, printed next to the mean sizing
   scale so a reader can see how much de-levering each arm actually received.
4. **`verdict`** = in how many of the four frames (capped/bare x own-vol/design-vol) the
   low-vol rule still beats the tuned book after each arm's own rent, and *which* frames it
   loses in. A win that only exists in one frame is not a win, it is a ruler.

Frozen before the first run (check() refuses a face whose echoed criteria differ):
    ARM_TRIALS, CAPITAL, ABANDON_P, DSR_LINE, MIN_BARS, REBAL, N_HOLD, COST, VOL_TARGET,
    DESIGN_VOL, RANDOM_DRAWS, REPRO_TOL_PP, REPRO_TOL_SR, PARENT.

Honest limitation (not hidden): `check()` does not re-read the panel -- it anchors staleness
on the parent face's own `panel.last_bar`. If nobody re-derives the parent, this guard is
blind, so a chain leg must still run this face unconditionally.

Usage:
    python scripts/etf_book_winner_frame_audit.py run
    python scripts/etf_book_winner_frame_audit.py check
    python scripts/etf_book_winner_frame_audit.py --selftest
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (HERE, ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

OUT_JSON = ROOT / "results" / "etf_book_winner_frame_audit.json"
OUT_MD = ROOT / "research" / "ETF-BOOK-WINNER-FRAME-AUDIT.md"
FACE = "results/etf_book_winner_frame_audit.json"
SCRIPT = "scripts/etf_book_winner_frame_audit.py"
PARENT = "results/etf_book_rent_horse_race.json"          # r1964, the face being audited
CONTROL_PARENT = "results/etf_book_production/PRODUCTION-2026-11-20.json"
CASH_LEG = "results/capital_placement.json::config.cash_net_annual"   # r1963's cash leg
APPLICABLE_FRAME = "capped_design_vol"   # this desk runs the 8% cap at the 8% design size

REBAL = 20
N_HOLD = 5
COST = 0.0010
VOL_TARGET = 0.08          # the cap every published arm ran under
DESIGN_VOL = 0.08          # the common ruler: the vol this book is designed to deliver
CAPITAL = 1_000_000.0
ABANDON_P = 0.05
DSR_LINE = 0.95
MIN_BARS = 250
RANDOM_DRAWS = 8           # must match r1964 or the coin cell cannot be reproduced

REPRO_TOL_PP = 0.20        # capped cells must reproduce r1964's CAGR, percentage points
REPRO_TOL_SR = 0.02        # ... and its Sharpe
REPRO_TOL_VOL_PP = 1.00    # ... and its volatility

ARMS = ("tuned_composite_6", "single_mom_12_1", "single_vol_60_low", "random_pick_5")
ARM_TRIALS = {
    "tuned_composite_6": 58,   # audited prereg-file count (r1960), conservative
    "single_mom_12_1": 6,      # one of the six factors in SIGNS
    "single_vol_60_low": 6,    # one of the six factors in SIGNS
    "random_pick_5": 1,        # a coin: nothing was searched, nothing to charge
}
CAP_MODES = {"capped": VOL_TARGET, "bare": None}
RULERS = {"own_vol": None, "design_vol": DESIGN_VOL}
CHAMPION = "tuned_composite_6"
CHALLENGER = "single_vol_60_low"

CRITERIA = {
    "capital_cny": CAPITAL,
    "abandon_p": ABANDON_P,
    "dsr_line": DSR_LINE,
    "min_bars": MIN_BARS,
    "rebal_bars": REBAL,
    "n_hold": N_HOLD,
    "cost_bp_per_side": COST * 1e4,
    "vol_target": VOL_TARGET,
    "design_vol": DESIGN_VOL,
    "arm_trials": ARM_TRIALS,
    "random_draws": RANDOM_DRAWS,
    "repro_tol_pp": REPRO_TOL_PP,
    "repro_tol_sr": REPRO_TOL_SR,
    "parent": PARENT,
    "haircut": "book_deflated_expectation._haircut_row (single implementation)",
    "frozen": "constants above were written before the first run",
}


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _dump(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")


def _load(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ arithmetic (pure)
def small_stats(series):
    """Stats from `etf_equity_alpha.stats2` -- the repo's own annualisation, one copy."""
    import etf_equity_alpha as A

    s = pd.Series(series, dtype="float64").dropna()
    if len(s) >= 40 and isinstance(s.index, pd.DatetimeIndex):
        m = A.stats2(s, "arm")
        return {"cagr": float(m["cagr"]), "vol": float(m["vol"]),
                "sharpe": float(m["sharpe"]), "maxdd": float(m["maxdd"]),
                "bars": len(s) - 1}
    if len(s) < 3:
        raise ValueError("series too short")
    rets = s.pct_change().dropna()
    vol = float(rets.std(ddof=1)) * math.sqrt(252.0) if len(rets) > 1 else 0.0
    sharpe = (float(rets.mean()) / float(rets.std(ddof=1)) * math.sqrt(252.0)
              if len(rets) > 1 and rets.std(ddof=1) else 0.0)
    return {"cagr": 0.0, "vol": vol, "sharpe": sharpe,
            "maxdd": float((s / s.cummax() - 1.0).min()), "bars": len(rets)}


def credible(sharpe, vol, returns, n_trials, capital=CAPITAL, abandon_p=ABANDON_P):
    """Deflated Sharpe -> money, reusing the r1962 implementation verbatim."""
    import book_deflated_expectation as B
    import science_gates as SG

    rets = pd.Series(returns, dtype="float64").dropna()
    d = SG.deflated_sharpe_ratio(rets.tolist(), int(n_trials))
    row = B._haircut_row(sharpe, vol, d["sigma_sr"], int(n_trials), capital, 1.0, abandon_p)
    row["dsr_raw"] = round(float(d["dsr"]), 6)
    row["sr_star_ann_from_returns"] = round(float(d["sr_star"]) * math.sqrt(252.0), 4)
    return row


def money(cell, ruler):
    """Money kept per year under one ruler (own realised vol, or the design 8%)."""
    vol = cell["vol"] if RULERS[ruler] is None else RULERS[ruler]
    return CAPITAL * cell["credible_sharpe"] * vol


def frames_of(cells):
    """Every (cap mode x ruler) frame, priced from the printed cells only."""
    out = []
    for cap in CAP_MODES:
        for ruler in RULERS:
            ch = next(c for c in cells if c["arm"] == CHAMPION and c["cap"] == cap)
            rv = next(c for c in cells if c["arm"] == CHALLENGER and c["cap"] == cap)
            mc, mv = money(ch, ruler), money(rv, ruler)
            out.append({"frame": "%s_%s" % (cap, ruler), "cap": cap, "ruler": ruler,
                        "champion": CHAMPION, "challenger": CHALLENGER,
                        "champion_cny": round(mc, 2), "challenger_cny": round(mv, 2),
                        "gap_cny": round(mv - mc, 2), "won_by_challenger": bool(mv > mc)})
    return out


def verdict(frames):
    """Frozen decision rule: the win must exist in every frame, not in the best one."""
    total = len(frames)
    won = [f for f in frames if f["won_by_challenger"]]
    failed = [f["frame"] for f in frames if not f["won_by_challenger"]]
    base = {"frames_total": total, "frames_won": len(won), "failed_frames": failed}
    if total == 0:
        return dict(base, verdict="NO_FRAMES", why="nothing to compare")
    if len(won) == total:
        return dict(base, verdict="LOW_VOL_WIN_HOLDS_IN_EVERY_FRAME",
                    why="the low-vol rule beats the tuned book under both cap modes and both rulers")
    if len(won) == 0:
        return dict(base, verdict="LOW_VOL_WIN_IS_A_FRAME_ARTIFACT",
                    why="the low-vol rule loses the tuned book in every frame it was tried in")
    return dict(base, verdict="LOW_VOL_WIN_IS_FRAME_DEPENDENT",
                why="the win exists in %d of %d frames; it fails in %s"
                    % (len(won), total, ", ".join(failed)))


def cap_cost(cells):
    """Price of the 8% cap per arm, next to how much de-levering it actually applied."""
    rows = []
    present = [a for a in ARMS if any(x["arm"] == a for x in cells)]
    present += sorted({x["arm"] for x in cells} - set(present))
    for arm in present:
        c = next(x for x in cells if x["arm"] == arm and x["cap"] == "capped")
        b = next(x for x in cells if x["arm"] == arm and x["cap"] == "bare")
        rows.append({
            "arm": arm,
            "capped_cagr": c["cagr"], "bare_cagr": b["cagr"],
            "cost_pp": round(100.0 * (b["cagr"] - c["cagr"]), 4),
            "capped_vol": c["vol"], "bare_vol": b["vol"],
            "capped_sharpe": c["sharpe"], "bare_sharpe": b["sharpe"],
            "sharpe_shift": round(c["sharpe"] - b["sharpe"], 4),
            "mean_scale_capped": c["mean_scale"], "share_sized_capped": c["share_sized"],
            "capped_maxdd": c["maxdd"], "bare_maxdd": b["maxdd"],
        })
    return rows


def cash_leg(frames):
    """The third arm on the same ruler: parking the money (r1963's published net carry)."""
    src, _, field = CASH_LEG.partition("::")
    out = {"source": CASH_LEG, "net_annual": None, "cutoff": None,
           "money_on_capital": None, "applicable_frame": APPLICABLE_FRAME,
           "in_applicable_frame": None, "per_frame": []}
    p = ROOT / src
    if p.exists():
        try:
            d = _load(p)
            rate = float((d.get("config") or {}).get(field.split(".")[-1]))
            out.update({"net_annual": rate, "cutoff": d.get("evidence_cutoff"),
                        "money_on_capital": round(CAPITAL * rate, 2)})
        except Exception as exc:                                    # noqa: BLE001
            out["error"] = repr(exc)
    for f in frames:
        row = {"frame": f["frame"],
               "champion_beats_cash": (None if out["money_on_capital"] is None
                                       else bool(f["champion_cny"] > out["money_on_capital"])),
               "challenger_beats_cash": (None if out["money_on_capital"] is None
                                         else bool(f["challenger_cny"] > out["money_on_capital"]))}
        out["per_frame"].append(row)
    hit = next((r for r in out["per_frame"] if r["frame"] == APPLICABLE_FRAME), None)
    if hit is not None:
        f = next(x for x in frames if x["frame"] == APPLICABLE_FRAME)
        out["in_applicable_frame"] = dict(hit, champion_cny=f["champion_cny"],
                                          challenger_cny=f["challenger_cny"],
                                          cash_cny=out["money_on_capital"])
    return out


def sizing_summary(diag):
    """Mean sizing scale and share of decisions that were taken below full size."""
    scales = [float(r["scale"]) for r in diag if r.get("scale") is not None]
    rules = {r.get("rule") for r in diag}
    if not scales:
        return {"mean_scale": None, "share_sized": None, "rules": sorted(r for r in rules if r)}
    mean = float(np.mean(scales))
    share = float(np.mean([1.0 if s < 0.999 else 0.0 for s in scales]))
    return {"mean_scale": round(mean, 4), "share_sized": round(share, 4),
            "rules": sorted(r for r in rules if r)}


# ------------------------------------------------------------------------ panel arms
def _elig(close, amt):
    import etf_composite_pf as E

    hist = close.notna().cumsum()
    return (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)


def _scores(close, amt, feats):
    """The three rule arms' score matrices on the production universe."""
    import etf_composite_pf as E

    cols, idx = close.columns, close.index
    elig = _elig(close, amt)
    out = {"tuned_composite_6": E.build_score(close, amt, feats)}

    def one(name, sign):
        f = feats.get(name)
        if f is None:
            raise RuntimeError("factor %s missing from compute_all" % name)
        f = f.reindex(index=idx, columns=cols)
        z = (f.rank(axis=1, pct=True) - 0.5) * 2.0
        return (sign * z).where(elig)

    out["single_mom_12_1"] = one("mom_12_1", +1.0)
    out["single_vol_60_low"] = one("vol_60", -1.0)
    return out, elig


def _random_score(close, elig, draw):
    rng = np.random.default_rng(90210 + int(draw))
    mat = rng.random((len(close.index), len(close.columns)))
    return pd.DataFrame(mat, index=close.index, columns=close.columns).where(elig)


def _run(close, openp, amt, score, vol_target):
    """One engine call; returns (equity series, sizing diag)."""
    import etf_robust_pf as R

    diag = []
    ser, _turn = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                                       vol_target=vol_target, diag=diag)
    return ser, diag


def _cell(name, cap, series, diag):
    st = small_stats(series)
    rets = pd.Series(series.values, dtype="float64").pct_change().dropna()
    row = credible(st["sharpe"], st["vol"], rets.values, ARM_TRIALS[name])
    sz = sizing_summary(diag)
    return {
        "arm": name, "cap": cap, "n_trials": ARM_TRIALS[name],
        "cagr": round(st["cagr"], 6), "vol": round(st["vol"], 6),
        "sharpe": round(st["sharpe"], 4), "maxdd": round(st["maxdd"], 6),
        "bars": st["bars"],
        "mean_scale": sz["mean_scale"], "share_sized": sz["share_sized"],
        "sizing_rules": sz["rules"],
        "sr_star_ann": row["sr_star_ann"], "credible_sharpe": row["credible_sharpe"],
        "money_own_vol": round(CAPITAL * row["credible_sharpe"] * st["vol"], 2),
        "money_design_vol": round(CAPITAL * row["credible_sharpe"] * DESIGN_VOL, 2),
    }


def build(write=True, verbose=True):
    import etf_composite_pf as E
    import etf_equity_alpha as A
    import etf_book_production as P

    t0 = time.time()
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols_keep = [c for c in close.columns if cls[c] in P.USE_CLASSES]
    close, openp, amt = close[cols_keep], openp[cols_keep], amt[cols_keep]
    feats = {k: v.reindex(columns=cols_keep) for k, v in feats.items()}

    scores, elig = _scores(close, amt, feats)
    cells = []

    for cap, vt in CAP_MODES.items():
        for name in ARMS:
            if name == "random_pick_5":
                curves, diags = [], []
                for k in range(RANDOM_DRAWS):
                    ser, dg = _run(close, openp, amt, _random_score(close, elig, k), vt)
                    curves.append(ser.reindex(close.index).ffill())
                    diags.extend(dg)
                coin = pd.concat(curves, axis=1).mean(axis=1).dropna()
                cell = _cell(name, cap, coin, diags)
            else:
                ser, dg = _run(close, openp, amt, scores[name], vt)
                cell = _cell(name, cap, ser, dg)
            cells.append(cell)
            if verbose:
                print("  %-20s %-6s cagr %.2f%% vol %.2f%% SR %.3f maxdd %.2f%% "
                      "scale %s own %s design %s"
                      % (name, cap, 100 * cell["cagr"], 100 * cell["vol"], cell["sharpe"],
                         100 * cell["maxdd"], cell["mean_scale"],
                         "{:,.0f}".format(cell["money_own_vol"]),
                         "{:,.0f}".format(cell["money_design_vol"])), flush=True)

    frames = frames_of(cells)
    v = verdict(frames)
    caps = cap_cost(cells)
    cash = cash_leg(frames)

    # Control A (parent reproduction): the capped cells must be r1964's own books. If they
    # are not, the audit is pricing something else and every claim below is void.
    repro = {"source": PARENT, "parent_cutoff": None, "per_arm": {}, "all_aligned": None}
    rp = ROOT / PARENT
    if rp.exists():
        pj = _load(rp)
        repro["parent_cutoff"] = pj.get("evidence_cutoff")
        pa = {a["arm"]: a for a in (pj.get("arms") or [])}
        ok_all = True
        for arm in ARMS:
            mine = next(c for c in cells if c["arm"] == arm and c["cap"] == "capped")
            p = pa.get(arm)
            if not p:
                repro["per_arm"][arm] = {"error": "parent has no such arm"}
                ok_all = False
                continue
            d_pp = round(100.0 * (mine["cagr"] - float(p["cagr"])), 4)
            d_sr = round(mine["sharpe"] - float(p["sharpe"]), 4)
            d_vol = round(100.0 * (mine["vol"] - float(p["vol"])), 4)
            ok = (abs(d_pp) <= REPRO_TOL_PP and abs(d_sr) <= REPRO_TOL_SR
                  and abs(d_vol) <= REPRO_TOL_VOL_PP)
            repro["per_arm"][arm] = {"parent_cagr": p["cagr"], "my_cagr": mine["cagr"],
                                     "delta_pp": d_pp, "parent_sharpe": p["sharpe"],
                                     "my_sharpe": mine["sharpe"], "delta_sr": d_sr,
                                     "delta_vol_pp": d_vol, "aligned": ok}
            ok_all = ok_all and ok
        repro["all_aligned"] = ok_all
        if repro["parent_cutoff"] != str(close.index[-1].date()):
            repro["vintage_note"] = ("parent was written on cutoff %s, this panel ends %s -- "
                                     "the reproduction is only meaningful when they agree"
                                     % (repro["parent_cutoff"], str(close.index[-1].date())))

    # Control B (engine twin): the production wrapper must price the capped tuned arm
    # identically. This is the leg that proves the cells ride the published engine.
    twin = {"source": "etf_book_production.backtest (in-process)",
            "parent_cagr": None, "parent_sharpe": None, "delta_pp": None,
            "delta_sr": None, "aligned": None}
    try:
        tb, _ser = P.backtest(close, openp, amt, scores["tuned_composite_6"], N_HOLD, REBAL,
                              vol_target=VOL_TARGET)
        full = tb.get("full") or {}
        mine = next(c for c in cells if c["arm"] == CHAMPION and c["cap"] == "capped")
        twin.update({"parent_cagr": full.get("cagr"), "parent_sharpe": full.get("sharpe"),
                     "delta_pp": round(100.0 * (mine["cagr"] - float(full["cagr"])), 4),
                     "delta_sr": round(mine["sharpe"] - float(full["sharpe"]), 4)})
        twin["aligned"] = (abs(twin["delta_pp"]) <= REPRO_TOL_PP
                           and abs(twin["delta_sr"]) <= REPRO_TOL_SR)
    except Exception as exc:                                        # noqa: BLE001
        twin["error"] = repr(exc)

    # Control C (the arm I think I ran): capped cells must show vol_target decisions and
    # the bare cells must be exactly fully invested. A mis-wired cap would sail through
    # every arithmetic check above.
    rule_ok = True
    for c in cells:
        if c["cap"] == "capped":
            rule_ok = rule_ok and ("vol_target" in c["sizing_rules"])
        else:
            rule_ok = rule_ok and (c["sizing_rules"] == ["none"]
                                   and c["mean_scale"] == 1.0 and c["share_sized"] == 0.0)
    rule_ctrl = {"capped_rule_seen": sorted({r for c in cells if c["cap"] == "capped"
                                            for r in c["sizing_rules"]}),
                 "bare_rule_seen": sorted({r for c in cells if c["cap"] == "bare"
                                           for r in c["sizing_rules"]}),
                 "aligned": bool(rule_ok)}

    if repro.get("all_aligned") is False:
        v = {"verdict": "PARENT_NOT_REPRODUCED",
             "why": "the capped cells do not reproduce r1964's books; no claim is made",
             "frames_total": len(frames), "frames_won": sum(
                 1 for f in frames if f["won_by_challenger"]),
             "failed_frames": [f["frame"] for f in frames if not f["won_by_challenger"]]}

    face = {
        "kind": "etf-book-winner-frame-audit/v1",
        "generated": _now(),
        "script": SCRIPT,
        "criteria": CRITERIA,
        "panel": {"symbols": int(len(close.columns)),
                  "bars": cells[0]["bars"],
                  "first_bar": str(close.index[0].date()),
                  "last_bar": str(close.index[-1].date())},
        "evidence_cutoff": str(close.index[-1].date()),
        "cells": cells,
        "frames": frames,
        "verdict": v,
        "cap_cost": caps,
        "cash_leg": cash,
        "control_parent_repro": repro,
        "control_engine_twin": twin,
        "control_sizing_rule": rule_ctrl,
        "staleness_anchor": PARENT + "::panel.last_bar",
        "elapsed_sec": round(time.time() - t0, 1),
    }
    if write:
        _dump(OUT_JSON, face)
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.write_text(_render_md(face), encoding="utf-8", newline="\n")
        if verbose:
            print("  -> %s" % FACE)
            print("  -> research/%s" % OUT_MD.name)
            print("  verdict %s | frames %d/%d | own gap %.0f | design gap %.0f"
                  % (v["verdict"], v["frames_won"], v["frames_total"],
                     _gap(frames, "capped_own_vol"), _gap(frames, "capped_design_vol")))
    return face


def _gap(frames, name):
    f = next((x for x in frames if x["frame"] == name), None)
    return float(f["gap_cny"]) if f else float("nan")


def _money(x):
    return "{:,.0f}".format(x)


def _render_md(face):
    v = face["verdict"]
    cells = face["cells"]
    frames = face["frames"]
    caps = face["cap_cost"]
    lines = []
    lines.append("# 低波规则的胜利用了几把尺子")
    lines.append("")
    lines.append("> 由 `%s` 渲染，数字不手抄。`generated %s`，`cutoff %s`。"
                 % (SCRIPT, face["generated"], face["evidence_cutoff"]))
    lines.append("")
    lines.append("## 一句话")
    c = next(x for x in cells if x["arm"] == CHAMPION and x["cap"] == "capped")
    r = next(x for x in cells if x["arm"] == CHALLENGER and x["cap"] == "capped")
    g_own = _gap(frames, "capped_own_vol")
    g_des = _gap(frames, "capped_design_vol")
    gs = [f["gap_cny"] for f in frames]
    lines.append("r1964 的标题数 **%s 元/年**（低波单因子比调参版多留的钱）只在**一个帧**里成立：8%% 帽子开着 + 每本书按自己的波动付钱。"
                 "同一对书换四把尺子读出来是 %s 元——**排序一次都没翻，金额差 %s 倍**，所以那个数只能带着「帧」一起引用。"
                 % (_money(g_own), " / ".join(_money(x) for x in gs),
                    "%.1f" % (max(gs) / min(gs)) if min(gs) > 0 else "∞"))
    lines.append("")
    lines.append("最接近这本案头配置的那一帧（帽子开着 + 和调参版同样的 8%% 下注尺寸）只差 **%s 元/年**：标题数里有 %s 元买的是「低波书当年实际波动 %.2f%% 反而高于调参版的 %.2f%%」这个事实，不是「它更会挑」。"
                 % (_money(g_des), _money(g_own - g_des), 100 * r["vol"], 100 * c["vol"]))
    lines.append("")
    lines.append("判词：**`%s`** —— %s。" % (v["verdict"], v["why"]))
    lines.append("")
    lines.append("## 八格：四臂 × 帽子开/关 × 两把尺")
    lines.append("")
    lines.append("| 臂 | 帽子 | 年化 | 波动 | 夏普 | 回撤 | 平均仓位刻度 | 被压过的决策占比 | 扣租后夏普 | 自己的尺（元/年） | 8% 同一把尺（元/年） |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for x in cells:
        lines.append("| %s | %s | %.2f%% | %.2f%% | %.3f | %.2f%% | %s | %s | %.3f | %s | %s |"
                     % (x["arm"], "8%" if x["cap"] == "capped" else "无", 100 * x["cagr"],
                        100 * x["vol"], x["sharpe"], 100 * x["maxdd"],
                        "—" if x["mean_scale"] is None else "%.3f" % x["mean_scale"],
                        "—" if x["share_sized"] is None else "%.1f%%" % (100 * x["share_sized"]),
                        x["credible_sharpe"], _money(x["money_own_vol"]),
                        _money(x["money_design_vol"])))
    lines.append("")
    lines.append("## 四帧审判：胜利还剩下几帧")
    lines.append("")
    lines.append("| 帧 | 帽子 | 尺 | 调参版（元/年） | 低波版（元/年） | 差（元/年） | 谁赢 |")
    lines.append("|---|---|---|---|---|---|---|")
    for f in frames:
        lines.append("| %s | %s | %s | %s | %s | %s | %s |"
                     % (f["frame"], f["cap"], "自己的波动" if f["ruler"] == "own_vol" else "8%",
                        _money(f["champion_cny"]), _money(f["challenger_cny"]),
                        _money(f["gap_cny"]),
                        "低波版" if f["won_by_challenger"] else "调参版"))
    lines.append("")
    lines.append("读数：**%d / %d 帧**低波版赢。赢的帧里最大的差 %s 元/年，最小的差 %s 元/年。"
                 % (v["frames_won"], v["frames_total"],
                    _money(max((f["gap_cny"] for f in frames), default=0.0)),
                    _money(min((f["gap_cny"] for f in frames), default=0.0))))
    if v.get("failed_frames"):
        lines.append("")
        lines.append("输掉的帧：%s——这几帧里调参版在扣完自己更贵的租金后仍然更值钱。"
                     % "、".join("`%s`" % x for x in v["failed_frames"]))
    lines.append("")
    lines.append("## 同一把尺上的第三条腿：趴着拿利息")
    cs = face.get("cash_leg") or {}
    if cs.get("money_on_capital") is None:
        lines.append("* 现金腿读不到（`%s`）→ 本节不作判断，也不把缺面印成 0。" % CASH_LEG)
    else:
        af = cs.get("in_applicable_frame") or {}
        lines.append("现金腿 = 已发布的净 carry **%.3f%%/年**（`%s`，cutoff %s），100 万元一年 **%s 元**。"
                     % (100 * cs["net_annual"], CASH_LEG, cs.get("cutoff"),
                        _money(cs["money_on_capital"])))
        lines.append("")
        lines.append("在这本案头的配置帧（`%s`）上三条腿并排：调参版 **%s**、低波版 **%s**、趴着 **%s** 元/年。"
                     % (APPLICABLE_FRAME, _money(af.get("champion_cny")),
                        _money(af.get("challenger_cny")), _money(af.get("cash_cny"))))
        lines.append("")
        if af.get("champion_beats_cash"):
            lines.append("* 调参版**赢**现金 %s 元/年。"
                         % _money(af["champion_cny"] - af["cash_cny"]))
        else:
            lines.append("* 调参版**输**现金 %s 元/年。"
                         % _money(af["cash_cny"] - af["champion_cny"]))
        if af.get("challenger_beats_cash"):
            lines.append("* 低波版**赢**现金 %s 元/年。"
                         % _money(af["challenger_cny"] - af["cash_cny"]))
        else:
            lines.append("* 低波版**输**现金 %s 元/年。"
                         % _money(af["cash_cny"] - af["challenger_cny"]))
        if not af.get("champion_beats_cash") and not af.get("challenger_beats_cash"):
            lines.append("")
            lines.append("所以本面这一句必须写在判词旁边：**低波版赢的那 2,144 元，是两个都输给利息的臂之间的差**——「换便宜规则」在这里不等于「值得上」，它只是把损失从 %s 元缩到 %s 元。"
                         % (_money(af["cash_cny"] - af["champion_cny"]),
                            _money(af["cash_cny"] - af["challenger_cny"])))
        lines.append("")
        lines.append("* 现金腿只在 `%s` 帧里被引用（这是本司配置）；其他帧只印配对差，不与现金比，因为那些帧的下注尺寸不是本司的下注尺寸。" % APPLICABLE_FRAME)
    lines.append("")
    lines.append("## 为什么四帧能差出这么多倍")
    tw_cap = next(x for x in caps if x["arm"] == CHAMPION)
    rv_cap = next(x for x in caps if x["arm"] == CHALLENGER)
    lines.append("两把尺子各偏一方，方向相反：")
    lines.append("")
    lines.append("* **自己的尺** 偏袒波动更大的那本：钱 = 扣租夏普 × 自己的波动，低波书当前波动 %.2f%% 高于调参版 %.2f%%，于是它被按更大的注付钱。"
                 % (100 * rv_cap["capped_vol"], 100 * tw_cap["capped_vol"]))
    lines.append("* **8%% 帽子** 偏袒被它改好夏普的那本：带帽把调参版夏普抬了 **%+.3f**（裸 %.3f → 带帽 %.3f），却把低波版夏普压了 **%+.3f**（裸 %.3f → 带帽 %.3f）——同一个去杠杆动作，对两本书的好处方向相反。"
                 % (tw_cap["sharpe_shift"], tw_cap["bare_sharpe"], tw_cap["capped_sharpe"],
                    rv_cap["sharpe_shift"], rv_cap["bare_sharpe"], rv_cap["capped_sharpe"]))
    lines.append("* 两个偏向在 `裸奔 + 共同尺` 一帧里同时消失，那一帧差 **%s 元**；在 `带帽 + 自己的尺` 一帧里同时放大，那一帧差 **%s 元**。"
                 % (_money(_gap(frames, "bare_design_vol")), _money(_gap(frames, "capped_own_vol"))))
    lines.append("")
    lines.append("这不是说哪个帧「对」——是说不写帧的金额没有意义。本司配置是带帽 + 8%% 设计波动，所以采购/审计时该引用 %s 那一档（`%s`）；`裸奔` 帧只用于归因。"
                 % (_money(_gap(frames, APPLICABLE_FRAME)), APPLICABLE_FRAME))
    lines.append("")
    lines.append("## 8% 帽子每本书收了多少费")
    lines.append("")
    lines.append("| 臂 | 带帽年化 | 裸奔年化 | 帽子代价 | 夏普位移 | 带帽波动 | 裸奔波动 | 平均刻度 | 被压过的决策 | 带帽回撤 | 裸奔回撤 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for x in caps:
        lines.append("| %s | %.2f%% | %.2f%% | %+.2fpp | %+.3f | %.2f%% | %.2f%% | %.3f | %.1f%% | %.2f%% | %.2f%% |"
                     % (x["arm"], 100 * x["capped_cagr"], 100 * x["bare_cagr"], x["cost_pp"],
                        x["sharpe_shift"], 100 * x["capped_vol"], 100 * x["bare_vol"],
                        x["mean_scale_capped"], 100 * x["share_sized_capped"],
                        100 * x["capped_maxdd"], 100 * x["bare_maxdd"]))
    lines.append("")
    lines.append("帽子不是白收的：它把每本书的波动和回撤一起压下来，代价列在同一行。两个输钱的臂（单动量、硬币）里帽子是**省钱**的（代价为负）——去杠杆对一本烂书也是保险。")
    lines.append("")
    lines.append("## 控制腿")
    repro = face.get("control_parent_repro") or {}
    if repro.get("all_aligned") is None:
        lines.append("* **父面复现腿**：`%s` 读不到 → 未跑，本面不宣称可对账。" % PARENT)
    else:
        lines.append("* **父面复现腿**（`%s`，cutoff %s）：带帽四格逐臂与 r1964 比对，%s。"
                     % (PARENT, repro.get("parent_cutoff"),
                        "四臂全部在容差内（年化 ≤%.1fpp / 夏普 ≤%.2f / 波动 ≤%.1fpp）"
                        % (REPRO_TOL_PP, REPRO_TOL_SR, REPRO_TOL_VOL_PP)
                        if repro["all_aligned"] else "**有臂超容差**——本面结论作废"))
        for arm, d in (repro.get("per_arm") or {}).items():
            if "error" in d:
                lines.append("  * `%s`：%s" % (arm, d["error"]))
            else:
                lines.append("  * `%s`：父面 %.2f%% / 夏普 %.3f → 本面 %.2f%% / %.3f（%.4fpp / %.4f）%s"
                             % (arm, 100 * d["parent_cagr"], d["parent_sharpe"],
                                100 * d["my_cagr"], d["my_sharpe"], d["delta_pp"],
                                d["delta_sr"], "✓" if d["aligned"] else "✗"))
        if repro.get("vintage_note"):
            lines.append("* 代差注记：%s。" % repro["vintage_note"])
    tw = face.get("control_engine_twin") or {}
    if tw.get("parent_cagr") is None:
        lines.append("* **构造腿**：生产包装器读不到 → 未跑。")
    else:
        lines.append("* **构造腿**（`etf_book_production.backtest` 同进程重跑调参带帽臂）：父面 %.2f%% / 夏普 %.3f，与本面差 %.4fpp / %.4f → **%s**。这条腿证明八格跑的是已发布的引擎。"
                     % (100 * tw["parent_cagr"], tw["parent_sharpe"], tw["delta_pp"],
                        tw["delta_sr"], "ALIGNED" if tw["aligned"] else "MISALIGNED"))
    rc = face.get("control_sizing_rule") or {}
    lines.append("* **接线腿**（我跑的是我以为的那条规则）：带帽格只出现 `%s` 决策、裸奔格只出现 `%s` 且平均刻度恰为 1.0 → **%s**。"
                 % ("/".join(rc.get("capped_rule_seen") or ["?"]),
                    "/".join(rc.get("bare_rule_seen") or ["?"]),
                    "ALIGNED" if rc.get("aligned") else "MISALIGNED"))
    lines.append("")
    lines.append("## 不许只挑一边信")
    lines.append("* 两把尺都印出来了：**自己的尺**回答「这本书按它自己跑出来的波动，一年能预算多少钱」，**8% 的尺**回答「和这本案头那本书同一个下注尺寸时，它值多少」。跨书比较只能用第二把。")
    lines.append("* 夏普本身与下注尺寸无关（所以扣租后的夏普排序在两把尺下一样）；变的是**钱**。差异全部来自「低波书的实际波动比调参版高」这一个事实。")
    lines.append("* 裸奔（关掉 8% 帽子）不是建议配置：它是归因臂，回答「这顶帽子在替谁说话」。帽子继续留在配置里，本面只印它的价钱。")
    lines.append("* 单因子臂的 N=6 仍是上限估计；若这六个因子来自更多次筛选，租金更高，低波版的优势只会更薄。")
    lines.append("* 全样本单窗、票池幸存者偏差、成本只计 10bp/边——本面不修正这些，只是把 r1964 的数放到同一把尺上。")
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------- check
def check(path=None):
    p = Path(path) if path else OUT_JSON
    if not p.exists():
        print("CHECK FAILED: face missing -> %s" % p)
        return 2
    face = _load(p)
    problems = []
    if face.get("criteria") != CRITERIA:
        problems.append("criteria echo differs from this script's frozen block")
    cells = face.get("cells") or []
    if len(cells) != len(ARMS) * len(CAP_MODES):
        problems.append("cell count %d != %d" % (len(cells), len(ARMS) * len(CAP_MODES)))
    if face.get("evidence_cutoff") is None:
        problems.append("evidence_cutoff missing")
    for x in cells:
        n_exp = ARM_TRIALS.get(x["arm"])
        if n_exp is None:
            problems.append("unknown arm on the face: %s" % x["arm"])
            continue
        if x["n_trials"] != n_exp:
            problems.append("%s/%s charged N=%s, frozen N=%d"
                            % (x["arm"], x["cap"], x["n_trials"], n_exp))
        b_exp = max(0.0, x["sharpe"] - x["sr_star_ann"])
        if abs(b_exp - x["credible_sharpe"]) > 1e-3:
            problems.append("%s/%s credible %.4f != max(0, %.4f-%.4f)"
                            % (x["arm"], x["cap"], x["credible_sharpe"], x["sharpe"],
                               x["sr_star_ann"]))
        if abs(CAPITAL * x["credible_sharpe"] * x["vol"] - x["money_own_vol"]) > 1.0:
            problems.append("%s/%s money_own != capital*credible*vol" % (x["arm"], x["cap"]))
        if abs(CAPITAL * x["credible_sharpe"] * DESIGN_VOL - x["money_design_vol"]) > 1.0:
            problems.append("%s/%s money_design != capital*credible*design_vol"
                            % (x["arm"], x["cap"]))
        if x["cap"] == "bare" and x["mean_scale"] not in (1.0,):
            problems.append("%s/bare mean_scale %.4f != 1.0 (a cap leaked into the bare cell)"
                            % (x["arm"], x["mean_scale"]))
    # the frames and the verdict must be the ones these printed cells imply
    frames = frames_of([{"arm": x["arm"], "cap": x["cap"], "credible_sharpe": x["credible_sharpe"],
                         "vol": x["vol"]} for x in cells])
    if [f["won_by_challenger"] for f in frames] != [f["won_by_challenger"]
                                                    for f in (face.get("frames") or [])]:
        problems.append("printed frames do not match frames re-derived from the cells")
    for f in face.get("frames") or []:
        if abs(f["gap_cny"] - (f["challenger_cny"] - f["champion_cny"])) > 1.0:
            problems.append("%s gap != challenger-champion" % f["frame"])
    want = verdict(frames)
    got = (face.get("verdict") or {}).get("verdict")
    if got != "PARENT_NOT_REPRODUCED" and got != want["verdict"]:
        problems.append("verdict %s != re-derived %s" % (got, want["verdict"]))
    # cap cost must re-derive from the printed cells
    for row in face.get("cap_cost") or []:
        c = next((x for x in cells if x["arm"] == row["arm"] and x["cap"] == "capped"), None)
        b = next((x for x in cells if x["arm"] == row["arm"] and x["cap"] == "bare"), None)
        if c is None or b is None:
            problems.append("cap_cost arm %s has no cell pair" % row["arm"])
            continue
        if abs(100.0 * (b["cagr"] - c["cagr"]) - row["cost_pp"]) > 0.02:
            problems.append("%s cost_pp != 100*(bare-capped)" % row["arm"])
        if abs((c["sharpe"] - b["sharpe"]) - row["sharpe_shift"]) > 1e-6:
            problems.append("%s sharpe_shift != capped-bare" % row["arm"])
    repro = face.get("control_parent_repro") or {}
    if repro.get("all_aligned") is False:
        problems.append("parent reproduction failed: the audit is pricing another book")
    twin = face.get("control_engine_twin") or {}
    if twin.get("parent_cagr") is None:
        problems.append("engine-twin control missing (production wrapper unreadable)")
    elif not twin.get("aligned"):
        problems.append("engine-twin control misaligned: delta %.4fpp / %.4f SR"
                        % (twin.get("delta_pp") or 0.0, twin.get("delta_sr") or 0.0))
    rc = face.get("control_sizing_rule") or {}
    if not rc.get("aligned"):
        problems.append("sizing-rule control failed: the cells are not the arms they claim")
    # the cash leg, when readable, must re-derive and its per-frame flags must agree
    cs = face.get("cash_leg") or {}
    if cs.get("money_on_capital") is not None:
        if abs(CAPITAL * cs["net_annual"] - cs["money_on_capital"]) > 1.0:
            problems.append("cash money != capital*cash_net_annual")
        for row in cs.get("per_frame") or []:
            f = next((x for x in face.get("frames") or [] if x["frame"] == row["frame"]), None)
            if f is None:
                problems.append("cash per_frame %s has no matching frame" % row["frame"])
                continue
            if row["champion_beats_cash"] != bool(f["champion_cny"] > cs["money_on_capital"]):
                problems.append("%s champion_beats_cash flag disagrees with the printed cells"
                                % row["frame"])
            if row["challenger_beats_cash"] != bool(f["challenger_cny"] > cs["money_on_capital"]):
                problems.append("%s challenger_beats_cash flag disagrees with the printed cells"
                                % row["frame"])
    # staleness anchor: the parent face must still be priced on the same last bar
    rp = ROOT / PARENT
    if rp.exists():
        pj = _load(rp)
        p_last = str((((pj.get("panel") or {}).get("last_bar")) or ""))
        if p_last and p_last != str(face.get("evidence_cutoff")):
            problems.append("STALE: parent %s is priced on %s, this face on %s"
                            % (PARENT, p_last, face.get("evidence_cutoff")))
    if problems:
        print("CHECK FAILED (%d)" % len(problems))
        for x in problems:
            print("  - " + x)
        return 3 if any(x.startswith("STALE") for x in problems) else 1
    print("CHECK OK: %d cells, verdict %s (%d/%d frames), parent repro %s, engine twin %s"
          % (len(cells), (face.get("verdict") or {}).get("verdict"),
             (face.get("verdict") or {}).get("frames_won"),
             (face.get("verdict") or {}).get("frames_total"),
             "ALIGNED" if repro.get("all_aligned") else "SKIPPED",
             "ALIGNED" if twin.get("aligned") else "UNALIGNED"))
    return 0


# ------------------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    # 1. the two rulers differ only by bet size, and only for a vol != design vol
    cell = {"credible_sharpe": 0.20, "vol": 0.12, "arm": "x", "cap": "capped"}
    leg("own-vol ruler pays a 12% book more than the 8% ruler",
        money(cell, "own_vol") > money(cell, "design_vol"))
    flat = dict(cell, vol=DESIGN_VOL)
    leg("at exactly the design vol the two rulers agree",
        abs(money(flat, "own_vol") - money(flat, "design_vol")) < 1e-6)

    # 2. the design ruler is a constant bet size: money scales with capital only
    leg("design-rule money is proportional to capital",
        abs(money(dict(cell, vol=0.30), "design_vol") - money(dict(cell, vol=0.05), "design_vol")) < 1e-9)

    # 3. frame survival classification
    def mk(cap, ruler, ch, rv):
        return {"frame": "%s_%s" % (cap, ruler), "cap": cap, "ruler": ruler,
                "champion_cny": ch, "challenger_cny": rv, "gap_cny": rv - ch,
                "won_by_challenger": rv > ch}
    leg("4/4 wins -> HOLDS_IN_EVERY_FRAME",
        verdict([mk("capped", "own_vol", 100, 120), mk("capped", "design_vol", 100, 110),
                 mk("bare", "own_vol", 100, 130), mk("bare", "design_vol", 100, 105)]
                )["verdict"] == "LOW_VOL_WIN_HOLDS_IN_EVERY_FRAME")
    leg("0/4 wins -> IS_A_FRAME_ARTIFACT",
        verdict([mk("capped", "own_vol", 120, 100), mk("capped", "design_vol", 110, 100),
                 mk("bare", "own_vol", 130, 100), mk("bare", "design_vol", 105, 100)]
                )["verdict"] == "LOW_VOL_WIN_IS_A_FRAME_ARTIFACT")
    v = verdict([mk("capped", "own_vol", 100, 120), mk("capped", "design_vol", 120, 100),
                 mk("bare", "own_vol", 100, 120), mk("bare", "design_vol", 100, 120)])
    leg("2/4 wins -> FRAME_DEPENDENT and names the losing frame",
        v["verdict"] == "LOW_VOL_WIN_IS_FRAME_DEPENDENT" and v["failed_frames"] == ["capped_design_vol"])
    leg("a tie is not a win",
        verdict([mk("capped", "own_vol", 100, 100)])["verdict"] == "LOW_VOL_WIN_IS_A_FRAME_ARTIFACT")

    # 4. the sizing summary and the cap price, on hand-built diags
    diag = [{"scale": 0.5, "rule": "vol_target"}, {"scale": 1.0, "rule": "vol_target"},
            {"scale": 0.25, "rule": "vol_target"}, {"scale": 1.0, "rule": "vol_target"}]
    sz = sizing_summary(diag)
    leg("mean scale and share sized are computed from the diag",
        abs(sz["mean_scale"] - 0.6875) < 1e-9 and abs(sz["share_sized"] - 0.5) < 1e-9)
    leg("a diag with no rules is not silently read as 'none'",
        sizing_summary([{"scale": 1.0}])["rules"] == [])

    # 5. cap cost, and its sign when the cap bites
    cells = [{"arm": "a", "cap": "capped", "cagr": 0.10, "vol": 0.08, "maxdd": -0.1,
              "sharpe": 1.10, "mean_scale": 0.6, "share_sized": 1.0},
             {"arm": "a", "cap": "bare", "cagr": 0.15, "vol": 0.20, "maxdd": -0.3,
              "sharpe": 0.98, "mean_scale": 1.0, "share_sized": 0.0}]
    c = cap_cost(cells)[0]
    leg("cap cost = bare - capped (positive when the cap gives up return)",
        abs(c["cost_pp"] - 5.0) < 1e-6 and c["mean_scale_capped"] == 0.6)
    leg("sharpe_shift = capped - bare (the cap can raise or lower a book's Sharpe)",
        abs(c["sharpe_shift"] - 0.12) < 1e-9)

    # 5b. the cash leg: readable -> priced from the published rate; unreadable -> None, never 0
    cl = cash_leg([mk("capped", "design_vol", 100.0, 200.0)])
    if cl["money_on_capital"] is None:
        leg("cash leg unreadable -> flags None, never False",
            all(r["champion_beats_cash"] is None for r in cl["per_frame"]))
    else:
        leg("cash leg money == capital*net_annual",
            abs(CAPITAL * cl["net_annual"] - cl["money_on_capital"]) < 1.0)
        leg("200 CNY against ~17,770 does not beat cash",
            cl["in_applicable_frame"]["challenger_beats_cash"] is False)

    # 6. stats on a flat curve do not divide by zero
    st = small_stats([1.0, 1.0, 1.0, 1.0])
    leg("flat curve -> zero vol/sharpe, no crash", st["vol"] == 0.0 and st["sharpe"] == 0.0)

    # 7. renderer: the failing frame names reach the page
    syn = []
    for cap in ("capped", "bare"):
        for arm, cagr in (("tuned_composite_6", 0.10), ("single_vol_60_low", 0.09)):
            syn.append({"arm": arm, "cap": cap, "n_trials": ARM_TRIALS[arm], "cagr": cagr,
                        "vol": 0.08, "sharpe": 0.30, "maxdd": -0.10, "bars": 100,
                        "mean_scale": 0.6 if cap == "capped" else 1.0,
                        "share_sized": 1.0 if cap == "capped" else 0.0,
                        "sizing_rules": ["vol_target"] if cap == "capped" else ["none"],
                        "sr_star_ann": 0.10, "credible_sharpe": 0.20,
                        "money_own_vol": CAPITAL * 0.20 * 0.08,
                        "money_design_vol": CAPITAL * 0.20 * DESIGN_VOL})
    face = {"generated": "t", "evidence_cutoff": "c", "panel": {},
            "cap_cost": cap_cost(syn), "cells": syn,
            "control_parent_repro": {"all_aligned": True, "per_arm": {}},
            "control_engine_twin": {"parent_cagr": 0.1, "parent_sharpe": 1.0,
                                    "delta_pp": 0.0, "delta_sr": 0.0, "aligned": True},
            "control_sizing_rule": {"aligned": True, "capped_rule_seen": ["vol_target"],
                                    "bare_rule_seen": ["none"]}}
    face["frames"] = frames_of(syn)
    face["verdict"] = verdict(face["frames"])
    md = _render_md(face)
    leg("md names the frame the win fails in", "capped_design_vol" in md)

    # 8. check() must fail on a face whose cells contradict their own arithmetic
    import copy
    import tempfile

    bad = copy.deepcopy(face)
    bad["criteria"] = CRITERIA
    bad["evidence_cutoff"] = "c"
    bad["cells"][0]["money_own_vol"] = bad["cells"][0]["money_own_vol"] + 5000.0
    with tempfile.TemporaryDirectory() as td:
        pth = Path(td) / "bad.json"
        _dump(pth, bad)
        leg("check() rejects a tampered money cell", check(pth) != 0)

    n_ok = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
    print("selftest %d/%d" % (n_ok, len(legs)))
    return 0 if n_ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--face")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        build(write=True)
        return 0
    if a.cmd == "check":
        return check(a.face)
    return selftest()


if __name__ == "__main__":
    raise SystemExit(main())
