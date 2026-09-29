"""T-101-V4-A7-PRESCREEN — liquidity-regime defensive-gate arm, cheap pre-screen face.

Prereg: research/T-101-V4-A7-PRESCREEN_PREREG.md (frozen pre-run, r435 bm-a).
Gate signal = GC001 (exchange overnight reverse-repo) close, annualized %:
    L1 level gate : close > 5.00                 -> liquidity stress -> risk-off
    L2 z-score    : (close - roll120.mean)/std(ddof=1) > 3.0 -> risk-off
Position = risk-on when no stress; T+1 open execution (O-1132 conservative proxy);
cost 0.05% per leg (0.1% round-trip, A2 parity); cash leg 0%. Five-member frozen
universe O-1555; IS/OOS split 2017-01-01; bear/bull/chop on 510300 MA200;
same-mask circular-shift nulls K=200/cell seed base 20309000 (SEED_REGISTRY
t101_v4_a7_scrnull). D6 binding face = REPO-CALENDAR carry-family proxies
(prereg sec.1 pre-declared); vs-B&H unconditional corr disclosed as structural
beta face (sparse-gate pre-declaration, r433 lesson law), not a reject line.
Lesson-112: append_ledger return value embedded in out["trials_ledger"] before
json.dump (t101_v4_a2_corrsource.py C-fix template).
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import science_gates as sg  # noqa: E402

EVIDENCE_CUTOFF = "2026-09-28"
UNIVERSE = ["510300", "510050", "510500", "512100", "588000"]
GATES = ["LIQ-L1:GC001>5.00", "LIQ-L2:GC001z120>3.0"]
LEVEL_TH = 5.00
Z_WINDOW = 120
Z_TH = 3.0
SPLIT = "2017-01-01"
COST_LEG = 0.0005  # 0.05% per leg -> 0.1% round-trip (A2 parity)
NULL_K = 200
NULL_SEED_BASE = sg.SEED_REGISTRY["t101_v4_a7_scrnull"]
MIN_OOS_ENTRIES = 15  # A2 parity: each stress-episode end = one independent evidence unit
MAXDD_FLOOR = -0.35  # descriptive clause (BACKTEST_SCIENCE)
ANCHOR_FACE = {c: f"data/daily/sh{c}.csv" for c in UNIVERSE}  # G-ANCHOR-FACE equity legs
SIGNAL_FACE = "data/repo_daily/GC001.csv"  # G-ANCHOR-FACE signal leg (T-88 collector face)


def load_panel(code: str) -> pd.DataFrame:
    path = ANCHOR_FACE[code]
    if not os.path.exists(path):
        raise SystemExit(f"FACE-MISMATCH VOID: declared anchor {path} missing")
    df = pd.read_csv(path)  # raw direct read, per prereg four-tuple
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= EVIDENCE_CUTOFF].reset_index(drop=True)  # D2 forward lockbox
    if df.empty or df["date"].iloc[-1] != EVIDENCE_CUTOFF:
        raise SystemExit(f"FACE-MISMATCH VOID: {code} tail {df['date'].iloc[-1] if len(df) else 'empty'} != {EVIDENCE_CUTOFF}")
    return df


def load_signal() -> pd.DataFrame:
    if not os.path.exists(SIGNAL_FACE):
        raise SystemExit(f"FACE-MISMATCH VOID: declared signal anchor {SIGNAL_FACE} missing")
    df = pd.read_csv(SIGNAL_FACE)
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= EVIDENCE_CUTOFF].reset_index(drop=True)
    if df.empty or df["date"].iloc[-1] != EVIDENCE_CUTOFF:
        raise SystemExit(f"FACE-MISMATCH VOID: GC001 tail {df['date'].iloc[-1] if len(df) else 'empty'} != {EVIDENCE_CUTOFF}")
    rate = df["close"].astype(float)
    bad = ((rate <= 0) | (rate >= 200)).sum()  # T-88 rate-band law, prereg sec.2
    if bad:
        raise SystemExit(f"FACE-MISMATCH VOID: GC001 rate band 0<close<200 violated on {bad} rows")
    return df


def stress_mask(sig: pd.DataFrame) -> dict:
    """Two frozen gates on GC001 close; returns stress masks on repo calendar."""
    c = sig["close"].astype(float)
    l1 = (c > LEVEL_TH).fillna(False)
    mu = c.rolling(Z_WINDOW).mean()
    sd = c.rolling(Z_WINDOW).std(ddof=1)
    z = (c - mu) / sd.replace(0, np.nan)
    l2 = (z > Z_TH).fillna(False)
    return {GATES[0]: l1, GATES[1]: l2}


def position_series(sig: pd.DataFrame, mask: pd.Series, member_dates: np.ndarray) -> pd.Series:
    """risk-on position on repo calendar (T+1 lag), forward-filled to member dates (causal)."""
    pos_repo = (~mask).shift(1).fillna(False).astype(bool)  # signal day t -> executed day t+1
    s = pd.Series(pos_repo.values, index=sig["date"].values)
    return s.reindex(member_dates).ffill().fillna(True).astype(bool)  # pre-signal warmup = risk-on


def regime_segment(benchmark: pd.DataFrame) -> pd.Series:
    c = benchmark["close"]
    ma200 = c.rolling(200).mean()
    slope = ma200.diff(60)
    bear = (c < ma200) & (slope < 0)
    bull = (c > ma200) & (slope > 0)
    seg = pd.Series("chop", index=benchmark.index)
    seg[bear] = "bear"
    seg[bull] = "bull"
    return seg


def daily_returns(df: pd.DataFrame, pos: pd.Series) -> pd.Series:
    o, c = df["open"].values, df["close"].values
    close_prev = np.roll(c, 1)
    close_prev[0] = np.nan
    ret = np.full(len(c), np.nan)
    p = pos.values
    for i in range(1, len(c)):
        if p[i] and p[i - 1]:
            ret[i] = c[i] / c[i - 1] - 1  # holding day
        elif p[i] and not p[i - 1]:
            ret[i] = c[i] / o[i] - 1 - COST_LEG  # entry day (open fill - cost)
        elif not p[i] and p[i - 1]:
            ret[i] = o[i] / c[i - 1] - 1 - COST_LEG  # exit day (open fill - cost)
        else:
            ret[i] = 0.0  # cash leg 0%
    return pd.Series(ret, index=df.index).fillna(0.0)


def sharpe(r: pd.Series) -> float:
    if len(r) < 20 or r.std() == 0:
        return float("nan")
    return float(r.mean() / r.std() * np.sqrt(252))


def max_drawdown(r: pd.Series) -> float:
    eq = (1 + r).cumprod()
    return float((eq / eq.cummax() - 1).min())


def ann_ret(r: pd.Series) -> float:
    total = float((1 + r).prod())
    yrs = len(r) / 252
    return total ** (1 / yrs) - 1 if yrs > 0 and total > 0 else float("nan")


def count_entries(pos: pd.Series, sel: pd.Series) -> int:
    p = pos[sel].values
    prev = np.roll(p, 1)
    prev[0] = False
    return int(((p) & (~prev)).sum())


def main() -> int:
    t0 = time.time()
    sig = load_signal()  # probe-anchor same-face assertion: declared signal path used
    masks = stress_mask(sig)
    gate_on_repo = {g: int(m.sum()) for g, m in masks.items()}  # stress days, full history
    panels = {c: load_panel(c) for c in UNIVERSE}  # equity legs, same-face assertion
    bm = panels["510300"]
    seg_all = regime_segment(bm)
    seg_by_date = pd.Series(seg_all.values, index=bm["date"].values)

    # D6 carry-family proxies on repo calendar (REPO-CALENDAR cash-leg family, prereg sec.1)
    carry_daily = pd.Series((sig["close"].astype(float) / 100.0 / 252.0).values, index=sig["date"].values)
    rate_diff = pd.Series(sig["close"].astype(float).diff().values, index=sig["date"].values)

    rows, json_cells, strat_daily = [], {}, {}
    for code in UNIVERSE:
        df = panels[code]
        dates = df["date"].values
        bh_ret = df["close"].pct_change().fillna(0.0)
        for gate in GATES:
            pos = position_series(sig, masks[gate], dates)
            r = daily_returns(df, pos)
            strat_daily[(code, gate)] = pd.Series(r.values, index=dates)
            is_sel = df["date"] < SPLIT
            oos_sel = ~is_sel
            full_stats = {"sharpe": sharpe(r), "ann_ret": ann_ret(r), "maxdd": max_drawdown(r)}
            is_stats = {"sharpe": sharpe(r[is_sel]), "ann_ret": ann_ret(r[is_sel])}
            oos_stats = {"sharpe": sharpe(r[oos_sel]), "ann_ret": ann_ret(r[oos_sel]), "maxdd": max_drawdown(r[oos_sel]),
                         "entries": count_entries(pos, oos_sel.values)}
            oos_excess = oos_stats["ann_ret"] - ann_ret(bh_ret[oos_sel])
            cell = {"inst": code, "gate": gate,
                    "riskoff_days_full": int((~pos).sum()), "riskoff_days_oos": int((~pos[oos_sel.values]).sum()),
                    "IS": is_stats, "OOS": oos_stats, "full": full_stats,
                    "oos_excess_vs_bh": oos_excess, "oos_n": int(oos_sel.sum()), "is_n": int(is_sel.sum())}
            # segmentation (regime faces on 510300 dates)
            seg_stats = {}
            seg_lookup = seg_by_date.reindex(dates).fillna("pre_benchmark")
            for segname in ("bear", "bull", "chop"):
                sel = (seg_lookup == segname) & (df["date"].values >= SPLIT)
                if sel.sum() >= 30:
                    seg_stats[segname] = {"oos_ann_ret": ann_ret(r[sel.values]), "oos_days": int(sel.sum())}
            cell["segments_oos"] = seg_stats
            # nulls: same-mask circular shift K=200
            rng = np.random.default_rng(NULL_SEED_BASE)
            pos_arr = pos.values.astype(int)
            null_sharpes = []
            for _ in range(NULL_K):
                k = int(rng.integers(1, len(pos_arr) - 1))
                shifted = np.roll(pos_arr, k)
                r_null = daily_returns(df, pd.Series(shifted.astype(bool), index=df.index))
                null_sharpes.append(sharpe(r_null))
            cell["null"] = {"k": NULL_K, "med_sharpe": float(np.nanmedian(null_sharpes)),
                            "p95_sharpe": float(np.nanpercentile(null_sharpes, 95))}
            # pre-screen verdict (frozen 4 criteria, prereg sec.3/4)
            verdict = "SURVIVE" if (
                oos_excess > 0
                and oos_stats["entries"] >= MIN_OOS_ENTRIES
                and full_stats["maxdd"] >= MAXDD_FLOOR
                and oos_stats["sharpe"] > cell["null"]["med_sharpe"]
            ) else "KILL"
            fail = []
            if oos_excess <= 0: fail.append("oos_excess<=0")
            if oos_stats["entries"] < MIN_OOS_ENTRIES: fail.append("entries<15(thin_evidence_face)")
            if full_stats["maxdd"] < MAXDD_FLOOR: fail.append("maxdd<-35%")
            if not (oos_stats["sharpe"] > cell["null"]["med_sharpe"]): fail.append("sharpe<=null_med")
            cell["verdict"] = verdict
            cell["fail_reasons"] = fail
            json_cells[f"{code}|{gate}"] = cell
            rows.append({"inst": code, "gate": gate, "verdict": verdict,
                         "oos_excess_vs_bh": round(oos_excess, 6),
                         "oos_sharpe": round(oos_stats["sharpe"], 4),
                         "oos_entries": oos_stats["entries"],
                         "riskoff_days_oos": cell["riskoff_days_oos"],
                         "full_maxdd": round(full_stats["maxdd"], 4),
                         "null_med_sharpe": round(cell["null"]["med_sharpe"], 4),
                         "fail_reasons": ";".join(fail)})

    # D6 faces per prereg sec.1: binding = carry-family; vs-B&H = pre-declared structural disclosure
    d6 = {"vs_bh": {}, "vs_carry_family": {}, "gate_pair": {}}
    bh_daily = {c: pd.Series(panels[c]["close"].pct_change().fillna(0).values, index=panels[c]["date"].values) for c in UNIVERSE}
    carry_m = carry_daily.reindex(panels[UNIVERSE[0]]["date"].values).ffill()
    rdiff_m = rate_diff.reindex(panels[UNIVERSE[0]]["date"].values).ffill()
    for (code, gate), sr in strat_daily.items():
        for bc, br in bh_daily.items():
            common = sr.index.intersection(br.index)
            if len(common) > 250:
                v = float(np.corrcoef(sr.loc[common], br.loc[common])[0, 1])
                d6["vs_bh"][f"{code}|{gate}_vs_{bc}"] = round(v, 4)
        cm = carry_m.reindex(sr.index)
        rm = rdiff_m.reindex(sr.index)
        ok = ~(cm.isna() | rm.isna() | (sr == 0).all())
        d6["vs_carry_family"][f"{code}|{gate}_vs_carry"] = round(float(np.corrcoef(sr[ok], cm[ok])[0, 1]), 4)
        d6["vs_carry_family"][f"{code}|{gate}_vs_ratediff"] = round(float(np.corrcoef(sr[ok], rm[ok])[0, 1]), 4)
    for code in UNIVERSE:
        a, b = strat_daily[(code, GATES[0])], strat_daily[(code, GATES[1])]
        v = float(np.corrcoef(a.values, b.values)[0, 1])
        d6["gate_pair"][code] = round(v, 4)
    d6["max_abs_vs_bh_disclosed"] = max(abs(v) for v in d6["vs_bh"].values())
    d6["vs_bh_pre_declared"] = "structural beta face of sparse defensive gate (prereg sec.1): disclosed, not a reject line"
    d6["max_abs_vs_carry_family"] = max(abs(v) for v in d6["vs_carry_family"].values())
    d6["d6_verdict"] = "ACCEPT" if d6["max_abs_vs_carry_family"] < 0.7 else "REJECT_corr>=0.7"
    d6["in_family_note"] = "REPO-CALENDAR-P1/P2 cells carry metrics only (no daily series in results JSON); carry proxies = GC001 daily carry + daily rate diff on same anchor face; full numeric family D6 deferred to full-judge face if any survivor reaches it (A2 precedent line)"

    out = {
        "batch": "T-101-V4-A7-PRESCREEN",
        "prereg": "research/T-101-V4-A7-PRESCREEN_PREREG.md",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": {"cutoff_meta": {"cutoff": EVIDENCE_CUTOFF}},
        "universe": UNIVERSE, "gates": GATES,
        "gate_frozen_params": {"level_th": LEVEL_TH, "z_window": Z_WINDOW, "z_th": Z_TH,
                               "signal_face": SIGNAL_FACE, "signal_first": str(sig['date'].iloc[0]),
                               "stress_days_full_history": gate_on_repo},
        "split": SPLIT, "cost_leg": COST_LEG, "null_k": NULL_K, "null_seed_base": NULL_SEED_BASE,
        "cells": json_cells, "d6": d6,
        "summary": {
            "n_cells": len(json_cells),
            "survivors": sum(1 for c in json_cells.values() if c["verdict"] == "SURVIVE"),
            "killed": sum(1 for c in json_cells.values() if c["verdict"] == "KILL"),
        },
        "audit": {"elapsed_sec": round(time.time() - t0, 1), "host": "bm-a",
                  "lane": "bm-a (repo panel data/repo_daily + ETF panel data/daily)"},
    }
    out["trials_ledger"] = sg.append_ledger(  # lesson-112: embed before dump, never drop the return
        "T-101-V4-A7-PRESCREEN", 10, "t101_v4_a7_prescreen.json",
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="A7 liquidity-regime defensive-gate arm cheap pre-screen; 2 gates x 5 members")
    with open("results/t101_v4_a7_prescreen.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    pd.DataFrame(rows).to_csv("results/t101_v4_a7_prescreen.csv", index=False)
    print(f"elapsed={out['audit']['elapsed_sec']}s cells={len(json_cells)} "
          f"survivors={out['summary']['survivors']} killed={out['summary']['killed']} "
          f"stress_days_full={gate_on_repo}")
    print(f"d6_carry_max|corr|={d6['max_abs_vs_carry_family']} d6={d6['d6_verdict']} "
          f"vs_bh_disclosed_max|corr|={d6['max_abs_vs_bh_disclosed']}")
    print(f"ledger: prev={out['trials_ledger']['prev_total']} +{out['trials_ledger']['batch_trials']} "
          f"-> total={out['trials_ledger']['total']}")
    for r in rows:
        print(f"{r['inst']} {r['gate']:22s} {r['verdict']:7s} oos_excess={r['oos_excess_vs_bh']:+.4f} "
              f"sharpe={r['oos_sharpe']:+.3f} entries={r['oos_entries']} riskoff_days_oos={r['riskoff_days_oos']} "
              f"maxdd={r['full_maxdd']:+.2%} null_med={r['null_med_sharpe']:+.3f} {r['fail_reasons']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
