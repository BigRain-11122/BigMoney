"""DIV_LOWVOL_P1 prefreeze data probe -- Tier-2 dividend-lowvol carry sleeve.

Pre-prereg probe facts ONLY (PREREG_TEMPLATE s2: 跑前探针事实, 非结果). Feeds the
hard-bound triad design (D-20260925-01(1)) with distribution facts and cites
the RECORDED regime replay (results/regime_calibration.json, ETF-face v1
matrix) for the ORANGE gate segments -- zero state-machine re-implementation;
the per-day state series is recomputed via the IMPORTED frozen layer
(regime_calibration.build_bench/bench_dim_series/breadth_series/raw_series/
state_replay) and cross-checked against the recorded aggregates as a
probe-level drift gate (recorded window 2020-01-02..2026-09-23).

DATA-FACE DISCOVERY (this probe, in-panel mechanical evidence): the raw sina
face is UNADJUSTED and 512890 carries a 1:2 share split (last cum bar
2021-10-21 close 1.639 -> suspended 2021-10-22 -> first post bar 2021-10-25
close 0.801; ratio 2.0449 ~= 2). The unadjusted face shows a phantom -51.13%
overnight "return" that poisons every distribution stat. The probe therefore
reports BOTH faces: raw (discovery evidence) and split-adjusted (the face the
prereg freezes for the batch; batch-local in-memory adjustment, corpus files
untouched). 510880 has zero >12% breaks (annual cash distributions = the
known sub-12% ex-div phantom drops; price face understates carry by the
distribution yield -- conservative, disclosed).

Authority chain: GM CAND tiered-approve Tier-2 (DIGEST-20260925-spm-stability-
paradigms.md GM 判定节, R177) -> this probe -> research/DIV_LOWVOL_P1.md
prereg freeze (separate commit) -> runner slice (not this file).

Usage:
    python scripts/div_lowvol_probe.py            # probe -> results/div_lowvol_probe.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS
from scripts.regime_calibration import (
    build_bench, bench_dim_series, breadth_series, raw_series, state_replay,
)
from scripts.market_regime import GREEN, ORANGE, RED, YELLOW

RECORDED = os.path.join(PATHS.results_dir, "regime_calibration.json")
OUT = os.path.join(PATHS.results_dir, "div_lowvol_probe.json")
WINDOW_START = "2020-01-02"   # recorded replay window start (regime_calibration.json)
WINDOW_END = "2026-09-22"     # trader-panel cutoff == dividend-leg last bar (probe asserts)
LEGS = {"512890": "sh512890.csv", "510880": "sh510880.csv"}
BENCH = "510300"
CRISIS_ABS_R = 0.05           # crisis-log face (frozen candidate for prereg)
MAX_DD_CAP = -0.12             # max hard-cap candidate for prereg (frozen constant)

# Corporate-action enumeration (probe fact; see module docstring). The prereg
# freezes this EVENT LIST (not a generic detector): batch-local in-memory
# adjustment only, corpus files never touched.
SPLIT_EVENTS = {
    "512890": {"first_post_split_bar": "2021-10-25", "factor": 0.5,
               "suspended_bars": ["2021-10-22"],
               "mechanical_evidence": {"last_cum_close": 1.639,
                                       "first_post_close": 0.801,
                                       "ratio": 2.0449,
                                       "overnight_raw_return": -0.5113}},
    "510880": None,
}


def _leg_frame(fname: str) -> pd.DataFrame:
    df = pd.read_csv(os.path.join(PATHS.daily_dir, fname), parse_dates=["date"])
    return df.set_index("date").sort_index()


def _adjust_split(df: pd.DataFrame, ev: dict | None) -> pd.DataFrame:
    """Batch-local in-memory split adjustment (prereg-frozen event list)."""
    if ev is None:
        return df
    cut = pd.Timestamp(ev["first_post_split_bar"])
    out = df.copy()
    pre = out.index < cut
    for col in ("open", "high", "low", "close"):
        if col in out.columns:
            out.loc[pre, col] = out.loc[pre, col] * ev["factor"]
    # volume left unadjusted: smaller pre-split ADV -> stricter V2 cost
    # estimate (conservative bias, disclosed in prereg s2/s3)
    return out


def _dist_face(r: pd.Series) -> dict:
    return {
        "n": int(r.size),
        "median": round(float(r.median()), 6),
        "std": round(float(r.std()), 6),
        "p001_loss_tail": round(float(r.quantile(0.001)), 6),
        "min": round(float(r.min()), 6),
        "max": round(float(r.max()), 6),
        "abs_r_ge_5pct_days": [str(d.date()) for d in r[r.abs() >= CRISIS_ABS_R].index],
    }


def main() -> int:
    rec = json.load(open(RECORDED, encoding="utf-8"))
    rec_win = rec["window"]          # 2020-01-02 .. 2026-09-23 (recorded)
    if rec_win["start"] != WINDOW_START:
        print(f"[probe] recorded window start {rec_win['start']} != {WINDOW_START}")
        return 2

    raw_legs = {code: _leg_frame(f) for code, f in LEGS.items()}
    adj_legs = {code: _adjust_split(raw_legs[code], SPLIT_EVENTS[code]) for code in LEGS}
    bench = _leg_frame(f"{BENCH}.csv")

    facts_instruments = {}
    for code in LEGS:
        s = raw_legs[code]["close"]
        facts_instruments[code] = {
            "rows": int(len(s)), "start": str(s.index[0].date()),
            "end": str(s.index[-1].date()),
            "covers_window_end": bool(s.index[-1] >= pd.Timestamp(WINDOW_END)),
            "split_event": SPLIT_EVENTS[code],
            "breaks_gt_12pct_overnight": [
                {"date": str(d.date()), "raw_overnight_ret": round(float(v), 6)}
                for d, v in s.pct_change().items() if abs(float(v)) > 0.12],
        }

    # completeness: calendar = bench ACTUAL trading days in window (generic
    # business-day calendars include A-share holidays -> false holes); zero
    # NaN closes excluding enumerated suspension bars (fund suspended for
    # the split); corpus staleness beyond 09-22 is out of window by
    # construction.
    susp = {d for ev in SPLIT_EVENTS.values() if ev
            for d in ev["suspended_bars"]}
    bdays = bench.loc[(bench.index >= pd.Timestamp(WINDOW_START))
                      & (bench.index <= pd.Timestamp(WINDOW_END))].index
    align = pd.DataFrame(
        {code: adj_legs[code]["close"] for code in LEGS} | {BENCH: bench["close"]})
    win_slice = align.reindex(bdays)
    nan_days = {c: int(win_slice[c].isna().sum()) for c in win_slice.columns}
    nan_days_excl_susp = {
        c: int(win_slice.loc[[d for d in bdays if str(d.date()) not in susp], c].isna().sum())
        for c in win_slice.columns}
    completeness = {
        "window_bench_trading_days": int(len(bdays)),
        "suspension_bars_whitelisted": sorted(susp),
        "nan_close_days_raw": nan_days,
        "nan_close_days_excl_suspension": nan_days_excl_susp,
        "gate_all_legs_cover_end": facts_instruments["512890"]["covers_window_end"]
            and facts_instruments["510880"]["covers_window_end"]
            and bool(bench["close"].index[-1] >= pd.Timestamp(WINDOW_END)),
        "gate_zero_nan_excl_suspension": bool(all(v == 0 for v in nan_days_excl_susp.values())),
    }

    # --- recorded-regime cross-checked per-day state series (imported layer) ---
    bb = build_bench()
    ds = bench_dim_series(bb)
    br = breadth_series(bb)
    raw = raw_series(bb, ds, br)
    states, _streaks, _init = state_replay(bb, raw)
    ser = pd.Series({d: states[d] for d in states}).sort_index()
    rec_slice = ser[(ser.index >= pd.Timestamp(rec_win["start"]))
                    & (ser.index <= pd.Timestamp(rec_win["end"]))]
    sleeve_slice = ser[(ser.index >= pd.Timestamp(WINDOW_START))
                       & (ser.index <= pd.Timestamp(WINDOW_END))]
    rec_counts = {s: int((rec_slice == s).sum()) for s in (GREEN, YELLOW, ORANGE, RED)}
    sleeve_counts = {s: int((sleeve_slice == s).sum()) for s in (GREEN, YELLOW, ORANGE, RED)}

    def _episodes(series: pd.Series) -> list:
        segs, in_seg, start, prev = [], False, None, None
        for d, st in series.items():
            if st == ORANGE and not in_seg:
                start, in_seg = d, True
            elif st != ORANGE and in_seg:
                segs.append((start, prev))
                in_seg = False
            prev = d
        if in_seg:
            segs.append((start, prev))
        return segs

    rec_eps = _episodes(rec_slice)
    sleeve_eps = _episodes(sleeve_slice)
    drift_gate = {
        "recorded_window": {"start": rec_win["start"], "end": rec_win["end"]},
        "recomputed_state_counts_recorded_window": rec_counts,
        "recorded_state_counts": {k: int(v) for k, v in rec["state_counts"].items()},
        "recomputed_orange_episodes_recorded_window": len(rec_eps),
        "recorded_orange_episodes": int(rec["false_alarm"]["orange"]["episodes"]),
        "counts_match": bool(
            rec_counts == {k: int(v) for k, v in rec["state_counts"].items()}
            and len(rec_eps) == int(rec["false_alarm"]["orange"]["episodes"])),
        "sleeve_window_orange": {"days": sleeve_counts[ORANGE], "episodes": len(sleeve_eps)},
    }

    # --- pair equal-weight daily returns (split-adjusted face = prereg face) ---
    px = win_slice.dropna()
    ret = px.pct_change().dropna()
    pair_r = 0.5 * ret["512890"] + 0.5 * ret["510880"]
    bench_r = ret[BENCH]

    # raw-face discovery evidence (unadjusted): the phantom -51% day et al.
    raw_align = pd.DataFrame(
        {code: raw_legs[code]["close"] for code in LEGS} | {BENCH: bench["close"]})
    raw_ret = raw_align.reindex(bdays).dropna().pct_change().dropna()
    raw_pair_r = 0.5 * raw_ret["512890"] + 0.5 * raw_ret["510880"]
    raw_face = {
        "note": "unadjusted face kept as discovery evidence only; NOT the prereg face",
        "pair_daily_returns": _dist_face(raw_pair_r),
        "raw_2021_10_25_pair_ret": round(float(raw_pair_r.loc["2021-10-25"]), 6)
            if "2021-10-25" in raw_pair_r.index else None,
    }

    pair_daily = _dist_face(pair_r)

    # --- 20d rolling cumulative return distribution (detection-primary bound) ---
    cum20 = (1.0 + pair_r).rolling(20).apply(lambda x: x.prod(), raw=True) - 1.0
    cum20 = cum20.dropna()
    pair_cum20 = {
        "n": int(cum20.size),
        "median": round(float(cum20.median()), 6),
        "q001_cut_line_candidate": round(float(cum20.quantile(0.001)), 6),
        "q01_context": round(float(cum20.quantile(0.01)), 6),
        "min": round(float(cum20.min()), 6),
        "min_date": str(cum20.idxmin().date()),
    }

    # --- pair HWM drawdown (max hard cap face) ---
    eq = (1.0 + pair_r).cumprod()
    dd = eq / eq.cummax() - 1.0
    pair_dd = {
        "max_dd": round(float(dd.min()), 6),
        "max_dd_date": str(dd.idxmin().date()),
        "days_dd_le_minus_12pct": int((dd <= MAX_DD_CAP).sum()),
    }

    # --- ORANGE-segment stats: pair vs bench (segment-gate priors) ---
    seg_rows = []
    for start, end in sleeve_eps:
        seg_pair_r = pair_r[(pair_r.index >= start) & (pair_r.index <= end)]
        seg_bench_r = bench_r[(bench_r.index >= start) & (bench_r.index <= end)]
        if len(seg_pair_r) < 2:
            continue
        seg_eq = (1.0 + seg_pair_r).cumprod()
        seg_dd = float((seg_eq / seg_eq.cummax() - 1.0).min())
        pair_cum = float(seg_eq.iloc[-1] - 1.0)
        bench_cum = float((1.0 + seg_bench_r).prod() - 1.0)
        seg_rows.append({
            "start": str(start.date()), "end": str(end.date()),
            "n_days": int(len(seg_pair_r)),
            "pair_cumret": round(pair_cum, 6),
            "bench_cumret": round(bench_cum, 6),
            "beat_bench": bool(pair_cum > bench_cum),
            "worst_in_seg_dd": round(seg_dd, 6),
        })
    or_mask = pair_r.index.isin([d for d in sleeve_slice.index if sleeve_slice[d] == ORANGE])
    orange_face = {
        "n_segments": len(seg_rows),
        "beat_count": int(sum(1 for r in seg_rows if r["beat_bench"])),
        "pair_orange_days_mean_daily": round(float(pair_r[or_mask].mean()), 6),
        "bench_orange_days_mean_daily": round(float(bench_r[or_mask].mean()), 6),
        "worst_seg_pair_dd": min((r["worst_in_seg_dd"] for r in seg_rows), default=None),
    }

    # --- recent-window (H1 law: 2021+) face ---
    rec_mask = pair_r.index >= pd.Timestamp("2021-01-01")

    def _ann(r):
        if len(r) < 20:
            return None
        total = float((1.0 + r).prod())
        return round(total ** (244.0 / len(r)) - 1.0, 6)

    recent = {
        "window": "2021-01-01..cutoff",
        "pair_ann": _ann(pair_r[rec_mask]),
        "bench_ann": _ann(bench_r[rec_mask]),
    }

    out = {
        "probe": "DIV_LOWVOL_P1 prefreeze data probe (facts only, no batch run)",
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "machine": "bm-a",
        "window": {"start": WINDOW_START, "end": WINDOW_END},
        "evidence_cutoff": WINDOW_END,
        "instruments": facts_instruments,
        "completeness": completeness,
        "regime_reuse": {
            "recorded_file": "results/regime_calibration.json",
            "recorded_verdict": rec.get("verdict"),
            "drift_gate": drift_gate,
        },
        "prereg_face": "split-adjusted (batch-local, event list frozen here); "
                       "price face (distributions NOT credited -> understates carry)",
        "raw_face_discovery": raw_face,
        "pair_daily_returns": pair_daily,
        "pair_cumret_20d": pair_cum20,
        "pair_hwm_dd": pair_dd,
        "orange_segment_stats": {**orange_face, "per_segment": seg_rows},
        "recent_window_2021plus": recent,
        "frozen_candidates_for_prereg": {
            "crisis_log_abs_r": CRISIS_ABS_R,
            "max_dd_cap": MAX_DD_CAP,
            "cut_line_p999_cum20": pair_cum20["q001_cut_line_candidate"],
            "split_event_list": SPLIT_EVENTS,
        },
        "notes": [
            "hard-bound triad (D-20260925-01(1)): (a) detection primary = q0.001 of pair 20d cumret (distribution bound, in-sample-calibrated PROTECTIVE line, disclosed); (b) max hard cap = HWM DD <= -12% with crisis-day awareness (|r1|>=5% crisis log, cut is the protective action, no exemption protects the position); (c) extreme-day priors frozen in prereg s5.",
            "S11 external tail anchors (index face, NOT this panel): CSI dividend TRI -71.6% (2007-10..2008-11) / -45.7% (2015-06..2016-01) -- systemic-crash non-defense of low-vol/dividend factors; the sleeve's hard bounds are the structural response (ORANGE->RED flip + in-ORANGE crisis cut).",
            "episode count basis: recorded ETF-face v1 matrix; sleeve entries = episodes x 2 legs (pair form) predicted in prereg s5.",
            "ex-div phantom drops: both legs distribute cash annually; price face shows sub-5% phantom negatives on ex-div days and never credits the distribution -> measured carry is a LOWER bound of the true carry (conservative, disclosed).",
        ],
    }
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    os.replace(tmp, OUT)

    ok = (completeness["gate_all_legs_cover_end"]
          and completeness["gate_zero_nan_excl_suspension"]
          and drift_gate["counts_match"])
    print(f"[probe] recorded_win orange={rec_counts[ORANGE]}/{len(rec_eps)} "
          f"match={drift_gate['counts_match']} | sleeve_win orange="
          f"{sleeve_counts[ORANGE]}/{len(sleeve_eps)} | "
          f"cut20_q001={pair_cum20['q001_cut_line_candidate']} "
          f"maxDD={pair_dd['max_dd']} beat={orange_face['beat_count']}/{len(seg_rows)}")
    print(f"[probe] written {OUT}; probe_gates_ok={ok}")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
