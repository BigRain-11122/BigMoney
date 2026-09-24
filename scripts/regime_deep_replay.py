"""Deep-history regime replay -- T-2026-09-24-13 deliverable-2.

Prereg FROZEN at 59403dc (research/REGIME_GUARD_DEEP_REPLAY.md, written
BEFORE any run). Measurement/calibration batch: zero engine runs, zero
signal functions, zero registration consequences, trials=0 (prereg s0),
zero threshold edits. Products are v3+ citation and GM briefing material
only -- zero behavior change (enforce wiring is law O-1325, untouched).

Bench = hs300 INDEX face (Money02/data/index/hs300.parquet, 2005-04-08 ->
2026-09-22, 5216 rows), single series, NEVER spliced with the ETF price
face (index points vs yuan -- prereg s1). The basis difference vs the ETF
face is quantified by gate D-C and judged by D-D (prereg s2).

Lineage reuse (prereg s5): the decision layer is IMPORTED, never
re-implemented -- bench_dim_series/breadth_series/raw_series/_LEVEL_FNS/
_RESOLVERS/_episode come from scripts/regime_calibration.py (frozen
v1/v2/v3 semantics verbatim). Thin wrappers exist ONLY where the
recorded-batch code hardcodes the 2020 window start:
  * deep_state_replay  -- init anchor = FIRST bench day (prereg s1),
    vs calibration.state_replay which inits at the last pre-2020 day.
  * fa_metrics_deep     -- FA round scan over the FULL window, vs
    calibration.fa_metrics which scans from 2020-01-01. FA definitions
    (v1 s3.2: ORANGE entry <=20 bench days further-drop <5%; YELLOW entry
    <=10 days maxDD <3%; truncated rounds excluded from the main rate)
    are line-level reused via calibration._episode.
Breadth deep rule (prereg s1): days with n_valid < 5 core48 members do
NOT trigger the breadth dims (t18_deep_axis >=5-member precedent); live
point-function semantics untouched (mask feeds raw_series as None).

Subcommands (prereg s5): gates -> replay -> selftest.
  gates    -- D-A..D-D hard pre-gates (fail = batch invalid, exit 1)
  replay   -- gates + full one-shot replay -> results/regime_deep_replay.json
             + results/regime_deep_replay_episodes.csv (exit 1 on gate fail)
  selftest -- synthetic offline checks, zero data reads
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS
from scripts.regime_calibration import (
    EVIDENCE_CUTOFF, _LEVEL_FNS, _PREREG_REFS, _RESOLVERS, _episode,
    bench_dim_series, breadth_series, build_bench, raw_series,
)
from scripts.market_regime import GREEN, ORANGE, RED, YELLOW, _ORD

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PARQUET = os.path.join(ROOT, "Money02", "data", "index", "hs300.parquet")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
OUT_JSON = os.path.join(PATHS.results_dir, "regime_deep_replay.json")
OUT_JSON_V2 = os.path.join(PATHS.results_dir, "regime_deep_replay_v2.json")
OUT_CSV = os.path.join(PATHS.results_dir, "regime_deep_replay_episodes.csv")
RECORDED = {
    "v1": os.path.join(PATHS.results_dir, "regime_calibration.json"),
    "v2": os.path.join(PATHS.results_dir, "regime_calibration_v2.json"),
    "v3": os.path.join(PATHS.results_dir, "regime_calibration_v3.json"),
}
OVERLAP_START = "2012-05-28"     # twin first date (D-C overlap window)
OVERLAP_END = "2026-09-22"       # index-face last bar == evidence_cutoff
SUB_START, SUB_END = "2020-01-02", "2026-09-22"
DD_RO_BOUND = 0.06              # |R+O share delta| <= 6pp (prereg s2 D-D)
DD_FA_BOUND = 0.20              # ORANGE FA rate delta <= 20pp
DC_R1_BOUND_BP = 200.0          # |daily return delta| hard bound (prereg s2 D-C, v1 -- superseded)
DC_V2_MEDIAN_BP = 15.0          # V2 candidate (b): median distribution bound (GM ruling MSG-20260924-1722)
DC_V2_P999_BP = 400.0           # V2 candidate (b): p99.9 tail bound
DC_CRISIS_R1 = 0.05             # mechanical crisis day: |r1| >= 5% on either face
EP_ENTER, EP_EXIT = -0.15, -0.05   # dd250 crisis bands (prereg s1, hysteresis)
BREADTH_MIN_VALID = 5           # deep-scope breadth rule (prereg s1)
# prereg s2 recorded ETF-face baselines (cross-check against the recorded
# files at gate time; the FILES are the source of truth for D-D)
PREREG_RECORDED = {"v1": {"ro": 0.6158, "fa": 0.818},
                   "v2": {"ro": 0.2653, "fa": 0.571}}
MATRICES = ("v1", "v2", "v3")


def load_index_bench() -> pd.Series:
    """hs300 index face -> close Series (Money02 strictly read-only)."""
    df = pd.read_parquet(INDEX_PARQUET)
    s = pd.Series(df["close"].astype(float).values,
                  index=pd.to_datetime(df["date"]))
    return s.sort_index()


# ---------------------------------------------------------------- gates

def gate_da(bench: pd.Series) -> dict:
    """D-A index-face integrity (prereg s2)."""
    mono = bool(bench.index.is_monotonic_increasing)
    unique = bool(bench.index.is_unique)
    no_nan = bool(bench.notna().all())
    first_ok = str(bench.index[0].date()) <= "2005-04-08"
    rows_ok = len(bench) >= 5200
    return {"ok": mono and unique and no_nan and first_ok and rows_ok,
            "strictly_monotonic": mono, "no_duplicates": unique,
            "close_no_nan": no_nan,
            "first_date": str(bench.index[0].date()),
            "first_le_2005_04_08": bool(first_ok),
            "rows": len(bench), "rows_ge_5200": bool(rows_ok),
            "last_date": str(bench.index[-1].date())}


def gate_db() -> dict:
    """D-B bars anchor: 10444 files / 5222 parquet (T-18 GC same anchor)."""
    files = os.listdir(BARS_DIR)
    n_all = len(files)
    n_pq = sum(1 for f in files if f.endswith(".parquet"))
    return {"ok": n_all == 10444 and n_pq == 5222,
            "files_total": n_all, "files_expected": 10444,
            "parquet_total": n_pq, "parquet_expected": 5222}


def dc_v2_verdict(dr1: pd.Series, crisis_mask: pd.Series) -> dict:
    """Pure v2_b judgment core (offline-testable). GM ruling
    MSG-20260924-1722 candidate (b): median <= 15bp AND p99.9 <= 400bp
    distribution bounds (full overlap window, crisis days included -- a
    corrupt face inflates both regardless); the max face is crisis-aware
    (only days with |r1| < 5% on BOTH faces count) and carries NO hard
    bound; days above the p99.9 bound are exempted microstructure-event
    disclosure, never corruption."""
    med_bp = float(dr1.median()) * 1e4
    p999_bp = float(dr1.quantile(0.999)) * 1e4
    nc = dr1[~crisis_mask.reindex(dr1.index).fillna(False)]
    return {"ok": bool(med_bp <= DC_V2_MEDIAN_BP and p999_bp <= DC_V2_P999_BP),
            "median_bp": round(med_bp, 3),
            "p99_9_bp": round(p999_bp, 2),
            "non_crisis_max_bp": (round(float(nc.max()) * 1e4, 2)
                                  if len(nc) else None),
            "crisis_days_n": int(crisis_mask.sum())}


def gate_dc(bench: pd.Series, mode: str = "v1") -> dict:
    """D-C basis difference: index vs ETF face over the twin overlap.

    mode="v1" (superseded, kept for regression fixtures): max |daily
    return delta| <= 200bp hard bound -- misclassified real microstructure
    days as corruption (v1 GATES_FAILED, HQ-F-20260924-11).
    mode="v2_b" (prereg V2 s2, GM ruling MSG-20260924-1722 candidate (b)):
    median <= 15bp AND p99.9 <= 400bp distribution bounds; crisis-aware max
    face (|r1| < 5% on BOTH faces to count, no hard bound); days above the
    p99.9 bound = exempted microstructure-event disclosure. Full disclosure
    of median / p99.9 and the 10-day cumulative return max|delta|
    (dividend/fee drag enters the ledger honestly, prereg s2).
    """
    etf = build_bench()
    etf = etf[etf.index <= pd.Timestamp(OVERLAP_END)]
    ov = bench.index.intersection(etf.index)
    b2, e2 = bench.loc[ov], etf.loc[ov]
    rb, re = b2.pct_change(), e2.pct_change()
    dr1 = (rb - re).abs().dropna()
    dr10 = (b2.pct_change(10) - e2.pct_change(10)).abs().dropna()
    max_bp = float(dr1.max()) * 1e4
    worst = [{"date": str(d.date()), "abs_dr1_bp": round(float(v) * 1e4, 1)}
             for d, v in dr1.sort_values(ascending=False).head(12).items()]
    common = {
        "overlap_start": str(ov[0].date()), "overlap_end": str(ov[-1].date()),
        "overlap_start_expected": OVERLAP_START,
        "n_days": int(len(ov)),
        "abs_dr1_bp": {"max": round(max_bp, 2),
                       "median": round(float(dr1.median()) * 1e4, 3),
                       "p99_9": round(float(dr1.quantile(0.999)) * 1e4, 2)},
        "abs_dr10_max_bp": round(float(dr10.max()) * 1e4, 2),
        "worst_days": worst,
        "worst_days_note": ("top |dr1| days -- 2015-07/2016-01 千股"
                            "跌停/涨停锁定+熔断日与极端溢价日=ETF↔指数"
                            "微观结构分歧（涨停锁价低于公允值/熔断早收），"
                            "非数据腐坏（原始行/D-A/子窗连检三方佐证）")}
    if mode == "v1":
        return {"ok": max_bp <= DC_R1_BOUND_BP,
                "bound_bp": DC_R1_BOUND_BP,
                **common}
    # mode == "v2_b" (production V2 leg)
    crisis_mask = ((rb.abs() >= DC_CRISIS_R1) | (re.abs() >= DC_CRISIS_R1)
                   ).reindex(dr1.index).fillna(False)
    core = dc_v2_verdict(dr1, crisis_mask)
    above = [{"date": str(d.date()), "abs_dr1_bp": round(float(v) * 1e4, 1),
              "crisis_day": bool(crisis_mask.loc[d]),
              "exempt": "microstructure event (not corruption)"}
             for d, v in dr1[dr1 > DC_V2_P999_BP / 1e4]
             .sort_values(ascending=False).items()]
    return {"ok": core["ok"], "mode": "v2_b",
            "bounds_bp": {"median": DC_V2_MEDIAN_BP,
                          "p99_9": DC_V2_P999_BP},
            "judgment": core,
            "max_face_crisis_aware": {
                "definition": "|r1| < %.0f%% on BOTH faces to count"
                              % (DC_CRISIS_R1 * 100),
                "hard_bound": None,
                "crisis_days_n": core["crisis_days_n"],
                "non_crisis_max_bp": core["non_crisis_max_bp"]},
            "above_p99_9_exempt": above,
            **common}


# ------------------------------------------------- deep replay primitives

def deep_state_replay(raw: pd.Series, resolver) -> tuple:
    """State machine over the FULL window, init = FIRST bench day
    (prereg s1 frozen: 2005-04-08, prev=raw@that day, streak=0; warmup
    missing dims -> GREEN).

    Thin variant of calibration.state_replay: the loop body and resolver
    semantics are identical (imported resolver); the ONLY delta is the
    init anchor -- calibration.state_replay picks the last pre-2020 day,
    which would leave the 2005-2019 chain empty and violate prereg s1.
    """
    dates = list(raw.index)
    init_day = dates[0]
    prev_state, streak = raw.loc[init_day, "raw"], 0
    states, streaks = {init_day: prev_state}, {init_day: streak}
    for d in dates[1:]:
        prev_state, streak = resolver(prev_state, streak, raw.loc[d, "raw"])
        states[d] = prev_state
        streaks[d] = streak
    return states, streaks, init_day


def fa_metrics_deep(bench: pd.Series, states: dict) -> dict:
    """FA metrics over the FULL window -- v1 s3.2 definitions line-level
    reused via calibration._episode (ORANGE: <=20 bench days, further drop
    <5% = FA; YELLOW: <=10 days, <3%; truncated rounds excluded from the
    main rate). Thin variant of calibration.fa_metrics: only the window
    filter is removed (it scans from 2020-01-01; deep prereg s1 scans the
    whole 2005+ window)."""
    dates = list(bench.index)
    out = {"orange": [], "yellow": []}
    for j, d in enumerate(dates):
        prev = states.get(dates[j - 1]) if j else None
        cur = states[d]
        prev_ord = _ORD[prev] if prev is not None else -1
        if cur == ORANGE and prev_ord < _ORD[ORANGE]:
            out["orange"].append(_episode(dates, j, bench, 20, -0.05))
        if cur == YELLOW and prev_ord < _ORD[YELLOW]:
            out["yellow"].append(_episode(dates, j, bench, 10, -0.03))
    res = {}
    for lvl in ("orange", "yellow"):
        eps = out[lvl]
        main = [e for e in eps if not e["truncated"]]
        trunc = [e for e in eps if e["truncated"]]
        fa = [e for e in main if e["false_alarm"]]
        res[lvl] = {"episodes": len(eps), "main": len(main),
                    "truncated": len(trunc), "false_alarms": len(fa),
                    "fa_rate": (len(fa) / len(main)) if main else None,
                    "episode_dates": [e["date"] for e in eps],
                    "fa_dates": [e["date"] for e in fa],
                    "truncated_dates": [e["date"] for e in trunc]}
    return res


def crisis_episodes(bench: pd.Series) -> list:
    """dd250 mechanical crisis segmentation (prereg s1 frozen: segment C
    starts at the first dd250 <= -15% day outside any episode; ends at the
    first in-segment day with dd250 > -5% (-15%..-5% hysteresis band);
    window-end without recovery = truncated). Naming is a LABEL only and
    never moves a boundary."""
    dd250 = bench / bench.rolling(250).max() - 1.0
    eps, in_ep, cur = [], False, None
    for d, v in dd250.items():
        if pd.isna(v):
            continue
        if not in_ep:
            if v <= EP_ENTER:
                in_ep, cur = True, {"start": d, "end": None,
                                    "truncated": False,
                                    "trough": float(v), "trough_date": d}
            continue
        if v < cur["trough"]:
            cur["trough"], cur["trough_date"] = float(v), d
        if v > EP_EXIT:                      # strictly above -5% ends the run
            cur["end"] = d
            eps.append(cur)
            in_ep, cur = False, None
    if in_ep:
        cur["truncated"] = True
        eps.append(cur)
    for k, ep in enumerate(eps, 1):
        ep["episode"] = k
    return eps


_EP_NAMES = {2007: "2008 GFC", 2008: "2008 GFC", 2010: "2011 熊",
             2011: "2011 熊", 2013: "2013 钱荒", 2015: "2015 杠杆熊",
             2016: "2016 熔断", 2018: "2018 贸易熊", 2020: "2020 COVID",
             2021: "2021-22 熊", 2022: "2021-22 熊", 2024: "2024-01 微盘崩"}


def episode_name(ep: dict) -> str:
    """Label by trough-year anchor (prereg s1 naming map; label only)."""
    base = _EP_NAMES.get(ep["trough_date"].year)
    return base if base else f"{ep['start']:%Y-%m} 机械段（规则发现）"


def run_matrices(bench: pd.Series):
    """Three-matrix deep replay on shared dimension series.

    Breadth deep rule (prereg s1): share/slope masked to NaN on days with
    n_valid < 5 -> raw_series passes None -> breadth dims never trigger
    there (honest floor; live point-function semantics untouched).
    """
    ds = bench_dim_series(bench)
    br = breadth_series(bench)
    few = br["n_valid"] < BREADTH_MIN_VALID
    br["share_below_ma20"] = br["share_below_ma20"].mask(few)
    br["share_slope_5d"] = br["share_slope_5d"].mask(few)
    out = {}
    for mx in MATRICES:
        raw = raw_series(bench, ds, br, level_fn=_LEVEL_FNS[mx])
        states, _, init_day = deep_state_replay(raw, _RESOLVERS[mx])
        dates = list(bench.index)
        counts = {s: 0 for s in (GREEN, YELLOW, ORANGE, RED)}
        for d in dates:
            counts[states[d]] += 1
        share = {s: counts[s] / len(dates) for s in counts}
        trans = {}
        for a, b in zip(dates, dates[1:]):
            k = f"{states[a]}->{states[b]}"
            trans[k] = trans.get(k, 0) + 1
        fa = fa_metrics_deep(bench, states)
        out[mx] = {"states": states, "raw": raw, "fa": fa,
                   "counts": counts, "share": share, "transitions": trans,
                   "init_day": init_day}
    return out, ds, br


def subwindow_stats(bench: pd.Series, states: dict, fa: dict) -> dict:
    """2020-01-02..2026-09-22 subwindow stats for gate D-D (the recorded
    ETF-face batches ran this window with a fresh last-2019-day init; the
    deep chain arrives with 2005-2019 history -- the frozen 6pp/20pp
    bounds absorb exactly that chain difference)."""
    sub = [d for d in bench.index
           if SUB_START <= str(d.date()) <= SUB_END]
    counts = {s: 0 for s in (GREEN, YELLOW, ORANGE, RED)}
    for d in sub:
        counts[states[d]] += 1
    n = len(sub)
    ro = (counts[ORANGE] + counts[RED]) / n if n else None
    o_fa = fa["orange"]
    in_sub = [x for x in o_fa["episode_dates"]
              if SUB_START <= x <= SUB_END]
    fa_n = sum(1 for x in o_fa["fa_dates"] if SUB_START <= x <= SUB_END)
    tr_n = sum(1 for x in o_fa["truncated_dates"]
               if SUB_START <= x <= SUB_END)
    main = len(in_sub) - tr_n     # fa ⊆ main; truncated disjoint from main
    return {"days": n, "state_counts": counts,
            "ro_share": round(ro, 4) if ro is not None else None,
            "orange_rounds": len(in_sub), "orange_main": main,
            "orange_false_alarms": fa_n,
            "orange_fa_rate": round(fa_n / main, 4) if main else None}


def gate_dd(bench: pd.Series, matrices: dict) -> dict:
    """D-D continuity: index-based subwindow vs recorded ETF-face runs
    (prereg s2: per matrix |R+O share delta| <= 6pp AND ORANGE FA rate
    delta <= 20pp; a breach = verdict CONTINUITY_FAIL, scarce-conclusion
    embargo until the basis semantics are clarified)."""
    rec = {}
    for mx, p in RECORDED.items():
        with open(p, encoding="utf-8") as f:
            r = json.load(f)
        rec[mx] = {"ro": r["state_share"]["ORANGE"] + r["state_share"]["RED"],
                   "fa": r["false_alarm"]["orange"]["fa_rate"],
                   "window": r["window"]}
    xcheck = {}
    for mx in ("v1", "v2"):
        xcheck[mx] = {
            "prereg_ro": PREREG_RECORDED[mx]["ro"], "file_ro": rec[mx]["ro"],
            "prereg_fa": PREREG_RECORDED[mx]["fa"], "file_fa": rec[mx]["fa"],
            "match": (abs(rec[mx]["ro"] - PREREG_RECORDED[mx]["ro"]) <= 0.005
                      and abs(rec[mx]["fa"] - PREREG_RECORDED[mx]["fa"]) <= 0.005)}
    per, ok = {}, True
    for mx in MATRICES:
        s = subwindow_stats(bench, matrices[mx]["states"], matrices[mx]["fa"])
        d_ro = abs(s["ro_share"] - rec[mx]["ro"])
        d_fa = (abs(s["orange_fa_rate"] - rec[mx]["fa"])
                if s["orange_fa_rate"] is not None and rec[mx]["fa"] is not None
                else None)
        m_ok = (d_ro <= DD_RO_BOUND and d_fa is not None
                and d_fa <= DD_FA_BOUND)
        ok &= m_ok
        per[mx] = {"sub": s, "recorded_etf": rec[mx],
                   "d_ro_share_pp": round(d_ro * 100, 2),
                   "d_orange_fa_pp": (round(d_fa * 100, 2)
                                      if d_fa is not None else None),
                   "bounds": {"ro_pp": 6.0, "fa_pp": 20.0},
                   "pass": bool(m_ok)}
    return {"ok": bool(ok), "per_matrix": per,
            "prereg_vs_file_crosscheck": xcheck,
            "note": ("index-face subwindow vs recorded ETF-face runs; v3 "
                     "recorded window ends 2026-09-23 (1-day tail vs index "
                     "face disclosed, prereg s1)")}


def dim_availability(bench: pd.Series, ds: dict, br: dict) -> dict:
    """First-fire/first-computable date per dimension (prereg s1 honest
    floors; FOMC frozen calendar covers 2020-2026 only -> pre-2020 never
    fires, disclosed)."""
    def first(cond):
        for d, v in cond.items():
            if bool(v):
                return str(d.date())
        return None
    ma200 = bench.rolling(200).mean()
    dd250_ok = bench.rolling(250).max().notna()
    return {
        "crash_10d_first_computable": first(ds["crash_10d"].notna()),
        "panic_1d_first_computable": first(ds["panic_1d"].notna()),
        "below_ma200_first_computable": first(ma200.notna()),
        "r_pei3_dd250_first_computable": first(dd250_ok),
        "r_pei3_bear_first_fire": first(ds["bear"]),
        "vol20_3y_quantile_first_ok": first(ds["vol_ok"]),
        "breadth_first_n_valid_ge_5": first(br["n_valid"] >= BREADTH_MIN_VALID),
        "breadth_masked_days_n_valid_lt_5": int((br["n_valid"] < BREADTH_MIN_VALID).sum()),
        "event_fomc_first_fire": first(ds["event_fomc"]),
        "event_fomc_pre_2020": "never fires (frozen calendar covers 2020-2026 only, prereg s1 disclosure)",
        "event_pre_holiday_first_fire": first(ds["event_pre_holiday"]),
    }


def j_bands(ro_share: float) -> str:
    """J1/J2 three-band rule (prereg s3 frozen)."""
    if ro_share > 0.40:
        return "结构性非稀缺"
    if ro_share > 0.25:
        return "混合"
    return "稀缺驱动"


def j_fa_band(fa_rate) -> str:
    if fa_rate is None:
        return "n/a（无主回合）"
    return "结构性" if fa_rate > 0.60 else "稀缺驱动"


# ------------------------------------------------------------- product

def _episode_rows(bench: pd.Series, eps: list, matrices: dict) -> list:
    """J4 per-episode table: state-day distribution x {v1,v2,v3}, R+O
    share, in-segment ORANGE round/FA counts (entry day inside the
    segment; truncated segments run to the window end)."""
    rows = []
    for ep in eps:
        d1 = ep["end"] if ep["end"] is not None else bench.index[-1]
        seg = [d for d in bench.index if ep["start"] <= d <= d1]
        row = {"episode": ep["episode"], "name": episode_name(ep),
               "start": str(ep["start"].date()),
               "end": None if ep["truncated"] else str(d1.date()),
               "truncated": bool(ep["truncated"]), "n_days": len(seg),
               "dd250_trough": round(ep["trough"], 4),
               "dd250_trough_date": str(ep["trough_date"].date())}
        for mx in MATRICES:
            st = matrices[mx]["states"]
            c = {s: 0 for s in (GREEN, YELLOW, ORANGE, RED)}
            for d in seg:
                c[st[d]] += 1
            seg_set = set(str(d.date()) for d in seg)
            o_fa = matrices[mx]["fa"]["orange"]
            rounds_in = sum(1 for x in o_fa["episode_dates"] if x in seg_set)
            fa_in = sum(1 for x in o_fa["fa_dates"] if x in seg_set)
            row[f"{mx}_G"], row[f"{mx}_Y"] = c[GREEN], c[YELLOW]
            row[f"{mx}_O"], row[f"{mx}_R"] = c[ORANGE], c[RED]
            row[f"{mx}_RO_share"] = round((c[ORANGE] + c[RED]) / len(seg), 4)
            row[f"{mx}_orange_rounds_in"] = rounds_in
            row[f"{mx}_orange_fa_in"] = fa_in
        rows.append(row)
    return rows


def _write_json(payload: dict, path: str):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    os.replace(tmp, path)


def replay(write: bool = True) -> dict:
    """One-shot deep replay (prereg s5: rerun-forbidden after the fact;
    a corrupted product = deterministic re-execution legal)."""
    bench = load_index_bench()
    da, db, dc = gate_da(bench), gate_db(), gate_dc(bench, mode="v2_b")
    matrices, ds, br = run_matrices(bench)
    dd = gate_dd(bench, matrices)
    gates = {"D-A": da, "D-B": db, "D-C": dc, "D-D": dd}
    base = {"batch": "REGIME_GUARD_DEEP_REPLAY_V2",
            "prereg": ("research/REGIME_GUARD_DEEP_REPLAY_V2.md (FROZEN r106"
                       " post GM ruling MSG-20260924-1722 candidate (b);"
                       " v1 lineage @ 8c8c9f0)"),
            "matrix_prereg_refs": dict(_PREREG_REFS),
            "trials": 0,
            "ledger": "none (measurement batch, prereg s0)",
            "evidence_cutoff": EVIDENCE_CUTOFF,
            "bench": {"source": "Money02/data/index/hs300.parquet (read-only)",
                      "face": "hs300 index points -- never spliced with the ETF yuan face (prereg s1)",
                      "rows": len(bench),
                      "start": str(bench.index[0].date()),
                      "end": str(bench.index[-1].date())},
            "gates": gates}
    if not all(g["ok"] for g in gates.values()):
        res = {**base, "verdict": "GATES_FAILED"}
        if write:
            _write_json(res, OUT_JSON_V2)
        return res

    eps = crisis_episodes(bench)
    ep_rows = _episode_rows(bench, eps, matrices)
    all_ep_dates = set()
    for row in ep_rows:
        d1 = row["end"] if row["end"] else str(bench.index[-1].date())
        all_ep_dates.update({str(d.date()) for d in bench.index
                             if row["start"] <= str(d.date()) <= d1})

    mats_out, j4_summary = {}, {}
    for mx in MATRICES:
        m = matrices[mx]
        fa = m["fa"]
        o_out = sum(1 for x in fa["orange"]["fa_dates"] if x not in all_ep_dates)
        o_in = sum(1 for x in fa["orange"]["fa_dates"] if x in all_ep_dates)
        # R+O day split inside/outside episodes (deliverable-3 evidence)
        ro_in = ro_out = 0
        for d in bench.index:
            if m["states"][d] in (ORANGE, RED):
                if str(d.date()) in all_ep_dates:
                    ro_in += 1
                else:
                    ro_out += 1
        g1 = 0.02 <= m["share"][RED] + m["share"][ORANGE] <= 0.25
        g2 = (fa["orange"]["fa_rate"] is not None
              and fa["orange"]["fa_rate"] <= 0.60)
        mats_out[mx] = {
            "full_window": {"days": len(bench),
                            "state_counts": m["counts"],
                            "state_share": {k: round(v, 4)
                                            for k, v in m["share"].items()},
                            "transition_matrix": m["transitions"]},
            "init_day": str(m["init_day"].date()),
            "false_alarm": fa,
            "subwindow_2020_2026": subwindow_stats(bench, m["states"], fa),
            "law_gate_diagnostics": {
                "G1_ro_share_in_2_25pct": bool(g1),
                "G2_orange_fa_le_60pct": bool(g2),
                "G3_zero_gaps": bool(len(m["states"]) == len(bench)),
                "note": "law s3.3 values audited on the deep window for "
                        "diagnosis only -- this batch carries no PASS/FAIL "
                        "enforcement semantics (prereg s3)"},
            "prereg": _PREREG_REFS[mx]}
        j4_summary[mx] = {
            "orange_fa_in_episodes": o_in, "orange_fa_outside_episodes": o_out,
            "orange_rounds_outside_episodes": (
                len(fa["orange"]["episode_dates"])
                - sum(1 for x in fa["orange"]["episode_dates"]
                      if x in all_ep_dates)),
            "ro_days_in_episodes": ro_in, "ro_days_outside_episodes": ro_out}

    v1, v2, v3 = (mats_out[m]["full_window"]["state_share"] for m in MATRICES)
    fa1 = mats_out["v1"]["false_alarm"]["orange"]["fa_rate"]
    fa2 = mats_out["v2"]["false_alarm"]["orange"]["fa_rate"]
    fa3 = mats_out["v3"]["false_alarm"]["orange"]["fa_rate"]
    ro1, ro2, ro3 = (v1["ORANGE"] + v1["RED"], v2["ORANGE"] + v2["RED"],
                     v3["ORANGE"] + v3["RED"])
    j3_ok = (0.02 <= ro3 <= 0.25) and (fa3 is not None and fa3 <= 0.60)
    verdicts = {
        "J1": {"matrix": "v1", "deep_ro_share": round(ro1, 4),
               "ro_band": j_bands(ro1),
               "deep_orange_fa": None if fa1 is None else round(fa1, 4),
               "fa_band": j_fa_band(fa1),
               "verdict": (f"深窗 v1 R+O={ro1:.2%} -> {j_bands(ro1)}；"
                           f"ORANGE FA={fa1 if fa1 is None else round(fa1, 4)} "
                           f"-> {j_fa_band(fa1)}（G1 败因裁定）")},
        "J2": {"matrix": "v2", "deep_ro_share": round(ro2, 4),
               "ro_band": j_bands(ro2),
               "recorded_6_7y_ro": 0.2653,
               "window_driven_breach": bool(ro2 <= 0.25),
               "deep_orange_fa": None if fa2 is None else round(fa2, 4),
               "fa_band": j_fa_band(fa2),
               "verdict": (f"深窗 v2 R+O={ro2:.2%} -> {j_bands(ro2)}；"
                           f"1.53pp 越界="
                           f"{'窗驱动（深窗≤25%）' if ro2 <= 0.25 else '深窗复现越界=结构性'}")},
        "J3": {"matrix": "v3", "deep_ro_share": round(ro3, 4),
               "deep_orange_fa": None if fa3 is None else round(fa3, 4),
               "robust_out_of_window": bool(j3_ok),
               "verdict": ("v3 6.7 年 PASS 在 21 年窗外复现=稳健引证（写入 "
                           "HANDOVER 与 v3 引证面）" if j3_ok else
                           "脆弱性发现：深窗 v3 越法定界，如实呈报 GM，"
                           "零触碰 enforce 接线（引证面仅此）")},
    }
    res = {**base, "verdict": "GATES_OK",
           "n_crisis_episodes": len(eps),
           "dim_availability": dim_availability(bench, ds, br),
           "matrices": mats_out,
           "episodes": ep_rows,
           "j4_summary": j4_summary,
           "J1": verdicts["J1"], "J2": verdicts["J2"], "J3": verdicts["J3"],
           "notes": [
               "episode 命名=标签不影响边界（机械规则冻结，prereg s1）",
               "FA 回合归属：回合首日∈段 C -> 段内；否则段外（prereg s1）",
               "广度 n_valid<5 日双维不触发（深窗专用语义）；live 点函数零触碰",
               "FOMC 冻结日历只覆盖 2020-2026 -> 2020 前恒不触发=覆盖面披露",
               "本批 trials=0（测量批无引擎腿）；零阈值改动"]}
    if write:
        _write_json(res, OUT_JSON_V2)
        import csv as _csv
        with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
            w = _csv.DictWriter(f, fieldnames=list(ep_rows[0].keys()))
            w.writeheader()
            w.writerows(ep_rows)
    return res


def _summary(res: dict) -> dict:
    """Compact stdout summary (round-report friendly)."""
    out = {"verdict": res["verdict"], "trials": res["trials"],
           "evidence_cutoff": res["evidence_cutoff"],
           "gates": {k: v["ok"] for k, v in res["gates"].items()},
           "bench": res["bench"]}
    if res["verdict"] != "GATES_OK":
        return out
    out["n_crisis_episodes"] = res["n_crisis_episodes"]
    for mx in MATRICES:
        fw = res["matrices"][mx]["full_window"]
        fa = res["matrices"][mx]["false_alarm"]["orange"]
        out[mx] = {"ro_share": round(fw["state_share"]["ORANGE"]
                                     + fw["state_share"]["RED"], 4),
                   "orange_fa_rate": fa["fa_rate"],
                   "sub_ro_share": res["matrices"][mx]
                   ["subwindow_2020_2026"]["ro_share"]}
    out["J1"] = res["J1"]["ro_band"] + " / FA " + res["J1"]["fa_band"]
    out["J2"] = res["J2"]["ro_band"] + (" / breach window-driven"
                                        if res["J2"]["window_driven_breach"]
                                        else " / breach reproduced deep")
    out["J3"] = ("robust" if res["J3"]["robust_out_of_window"]
                 else "FRAGILE -- report to GM")
    return out


# ------------------------------------------------------------- selftest

def _selftest() -> bool:
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [deep-replay] {name}... {'PASS' if cond else 'FAIL'}")

    # A: dd250 episode segmentation -- bands, hysteresis, truncation
    idx = pd.bdate_range("2005-04-08", periods=700)
    b = pd.Series(1000.0, index=idx)
    b.iloc[300:340] = 1000.0 * (1 - 0.20 * pd.Series(
        range(1, 41), index=idx[300:340]) / 40)       # dip to -20%
    b.iloc[340:400] = b.iloc[339]                    # flat in band
    b.iloc[400:449] = 990.0                          # recovers > -5% (vs win max 1000)
    b.iloc[449:550] = 990.0
    b.iloc[550:590] = 990.0 * (1 - 0.18 * pd.Series(
        range(1, 41), index=idx[550:590]) / 40)       # second dip, no recovery
    b.iloc[590:] = b.iloc[589]                        # hold trough to window end
    eps = crisis_episodes(b)
    check("A two episodes found, second truncated",
          len(eps) == 2 and eps[0]["truncated"] is False
          and eps[1]["truncated"] is True)
    dd = b / b.rolling(250).max() - 1.0
    check("A episode1 start = first dd250<=-15% day",
          eps[0]["start"] == (dd <= -0.15).idxmax()
          if (dd <= -0.15).any() else False)

    # B: band edges -- dd250 exactly -15% fires; exactly -5% does NOT end.
    # Series length 549 keeps the 100-peak inside the rolling window to the
    # very end (a longer series would let the window max decay and end the
    # episode mechanically via dd250->0 -- formula-correct, not a fixture).
    idx2 = pd.bdate_range("2010-01-01", periods=549)
    b2 = pd.Series(100.0, index=idx2)
    for i in range(300, 500):
        b2.iloc[i] = 85.0                            # dd250 = -15% exactly
    b2.iloc[500:] = 96.0                             # -4% > -5% -> ends
    eps2 = crisis_episodes(b2)
    check("B -15% exact fires / -4% recovery ends",
          len(eps2) == 1 and eps2[0]["end"] == idx2[500])
    b3 = b2.copy()
    b3.iloc[500:] = 95.0                             # -5% exact -> no end
    eps3 = crisis_episodes(b3)
    check("B -5% exact does NOT end (strict > rule), truncated",
          len(eps3) == 1 and eps3[0]["truncated"] is True
          and eps3[0]["end"] is None)

    # C: deep init semantics -- init at FIRST bench day, prev=raw@day0
    rawf = pd.DataFrame({"raw": [GREEN, GREEN, ORANGE, GREEN, GREEN, GREEN]},
                        index=pd.bdate_range("2005-04-08", periods=6))
    from scripts.market_regime import resolve_state
    st, sk, init = deep_state_replay(rawf, resolve_state)
    check("C init_day = first bench date (2005-04-08)",
          str(init.date()) == "2005-04-08" and st[init] == GREEN)
    check("C ORANGE holds 1 green day, releases on 2nd",
          st[rawf.index[3]] == ORANGE and st[rawf.index[4]] == GREEN)

    # D: FA deep scan counts pre-2020 rounds (full-window scan)
    idx4 = pd.bdate_range("2008-01-01", periods=300)
    b4 = pd.Series(4.0, index=idx4)
    states4 = {}
    for i, d in enumerate(idx4):
        states4[d] = ORANGE if i == 50 else GREEN
    fa4 = fa_metrics_deep(b4, states4)
    check("D pre-2020 ORANGE round scanned (2008 entry)",
          fa4["orange"]["episodes"] == 1
          and fa4["orange"]["episode_dates"][0].startswith("2008"))

    # E: breadth masking -- n_valid<5 -> share NaN -> no trigger
    br5 = {"n_valid": pd.Series([0, 3, 5, 48], index=idx4[:4]),
           "share_below_ma20": pd.Series([0.9, 0.9, 0.9, 0.9], index=idx4[:4]),
           "share_slope_5d": pd.Series([-0.05] * 4, index=idx4[:4])}
    few = br5["n_valid"] < BREADTH_MIN_VALID
    masked = br5["share_below_ma20"].mask(few)
    check("E n_valid<5 days masked to NaN, >=5 kept",
          bool(masked.iloc[0:2].isna().all()) and bool(masked.iloc[2:].notna().all()))

    # F: D-C math -- identical faces -> zero delta; 1% perturbation -> 100bp
    x = pd.Series(100.0 * (1 + 0.001 * pd.Series(
        range(60), index=pd.bdate_range("2012-05-28", periods=60))))
    dr = (x.pct_change() - x.pct_change()).abs().dropna()
    check("F identical faces max|dr1|=0", float(dr.max()) == 0.0)
    y = x.copy()
    y.iloc[-1] *= 0.99
    dr2 = (y.pct_change() - x.pct_change()).abs().dropna()
    check("F 1% single-day perturbation ~= 100bp",
          99.0 <= float(dr2.max()) * 1e4 <= 101.0)

    # G: naming map + fallback
    ep08 = {"start": pd.Timestamp("2007-10-01"),
            "trough_date": pd.Timestamp("2008-10-28")}
    ep09 = {"start": pd.Timestamp("2009-03-01"),
            "trough_date": pd.Timestamp("2009-08-31")}
    check("G 2008 trough -> GFC label; unknown year -> mechanical fallback",
          episode_name(ep08) == "2008 GFC"
          and "机械段" in episode_name(ep09))

    # H: J-bands (prereg s3 frozen thresholds)
    check("H J-bands 41%->结构性 / 26%->混合 / 24%->稀缺",
          j_bands(0.41) == "结构性非稀缺" and j_bands(0.26) == "混合"
          and j_bands(0.24) == "稀缺驱动")
    check("H J-fa-band 61%->结构性 / 60%->稀缺驱动 / None->n/a",
          j_fa_band(0.61) == "结构性" and j_fa_band(0.60) == "稀缺驱动"
          and j_fa_band(None) == "n/a（无主回合）")
    check("H J3 robust predicate", (0.02 <= 0.10 <= 0.25 and 0.50 <= 0.60)
          and not (0.02 <= 0.26 <= 0.25))

    # I: subwindow FA denominator -- fa ⊆ main, truncated disjoint; a
    #    rate > 1 is mathematically impossible (found live in r103 first
    #    gates run: main had the fa count subtracted twice).
    idx6 = pd.to_datetime(["2019-06-01", "2020-05-01", "2020-05-02",
                           "2021-06-01", "2025-01-10", "2026-09-20",
                           "2026-09-21"])
    b6 = pd.Series(4.0, index=idx6)
    states6 = {d: GREEN for d in idx6}
    fa6 = {"orange": {
        "episode_dates": ["2019-06-01", "2020-05-01", "2021-06-01",
                          "2025-01-10", "2026-09-20"],
        "fa_dates": ["2021-06-01", "2025-01-10"],
        "truncated_dates": ["2026-09-20"]}}
    s6 = subwindow_stats(b6, states6, fa6)
    check("I sub FA denominator: main=rounds-truncated, rate<=1",
          s6["orange_rounds"] == 4 and s6["orange_main"] == 3
          and s6["orange_false_alarms"] == 2
          and s6["orange_fa_rate"] == 0.6667)

    # J: V2 candidate (b) judgment core (GM ruling MSG-20260924-1722)
    idxj = pd.bdate_range("2012-05-28", periods=2000)
    base_delta = pd.Series(0.001, index=idxj)          # 10bp healthy days
    cm = pd.Series(False, index=idxj)
    v = dc_v2_verdict(base_delta, cm)
    check("J v2_b healthy distribution PASS (10bp median/p99.9)",
          v["ok"] is True and v["median_bp"] == 10.0
          and v["non_crisis_max_bp"] == 10.0)
    big = base_delta.copy()
    big.iloc[-1] = 0.050                                # one 500bp day
    cm2 = pd.Series(False, index=idxj)
    cm2.iloc[-1] = True                                 # flagged crisis
    v2 = dc_v2_verdict(big, cm2)
    check("J v2_b crisis day exempted from max face, gate still PASS",
          v2["ok"] is True and v2["non_crisis_max_bp"] == 10.0
          and v2["crisis_days_n"] == 1)
    corr = base_delta.copy()
    corr.iloc[:1100] = 0.003                            # majority at 30bp
    v3 = dc_v2_verdict(corr, cm)
    check("J v2_b median corruption FAIL (30bp median > 15bp bound)",
          v3["ok"] is False and v3["median_bp"] == 30.0)
    tail = base_delta.copy()
    tail.iloc[::10] = 0.05                              # 10% days at 500bp
    v4 = dc_v2_verdict(tail, pd.Series(False, index=idxj))
    check("J v2_b tail corruption FAIL (p99.9 500bp > 400bp bound)",
          v4["ok"] is False and v4["p99_9_bp"] == 500.0)
    return ok


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "selftest" in argv:
        ok = _selftest()
        print(f"  [deep-replay] selftest {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    if "gates" in argv:
        bench = load_index_bench()
        da, db, dc = gate_da(bench), gate_db(), gate_dc(bench, mode="v2_b")
        matrices, _, _ = run_matrices(bench)
        dd = gate_dd(bench, matrices)
        gates = {"D-A": da, "D-B": db, "D-C": dc, "D-D": dd}
        ok = all(g["ok"] for g in gates.values())
        print(json.dumps({"gates_ok": ok,
                          "per_gate": {k: v["ok"] for k, v in gates.items()},
                          "D-A": da, "D-B": db,
                          "D-C": dc["abs_dr1_bp"],
                          "D-D": {m: {"d_ro_pp": v["d_ro_share_pp"],
                                      "d_fa_pp": v["d_orange_fa_pp"],
                                      "pass": v["pass"]}
                                  for m, v in dd["per_matrix"].items()}},
                         ensure_ascii=False, indent=1))
        return 0 if ok else 1
    if "replay" in argv:
        res = replay(write=True)
        print(json.dumps(_summary(res), ensure_ascii=False, indent=1))
        print(f"  out: {OUT_JSON_V2}")
        print(f"  out: {OUT_CSV}" if res["verdict"] == "GATES_OK" else "")
        return 0 if res["verdict"] == "GATES_OK" else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
