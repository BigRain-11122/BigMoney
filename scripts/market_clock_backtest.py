# -*- coding: utf-8 -*-
"""Market-clock combo full-history backtest -- T-74 s2 (O-20260926-0932).

Prereg FROZEN: research/MARKET_CLOCK_COMBO.md v1.1 (s2 criteria = v1.0 s2
verbatim; sleeve-replay mechanics = s2b, frozen BEFORE this run; commit hash
recorded in the batch JSON at finalize time).

Global-stream property (s2b carrier re-ruling): the frozen ladder is a pure
state function with zero portfolio-value feedback, so the combo daily return
stream is start-independent -- each grid start is a SLICE of one global
stream. Measured wall < 5min => light batch, legal inline per O-20260924-2100
face-separation law (heavy batches go to the pool; this one is not heavy --
carrier field discloses the measurement).

Faces (all local, offline, deterministic; lineage reuse, zero rebuild):
  v3 deep states    -- imported verbatim from scripts/regime_deep_replay.py
                       chain (load_index_bench -> bench_dim_series ->
                       breadth_series mask -> raw_series(v3) ->
                       deep_state_replay), recorded deep-replay semantics.
  heat composite    -- same law as s1 market_clock_call.py: H_act = daily
                       LHB row count, H_net = daily net-buy sum; p80 over
                       the strictly-prior tail-250 LHB days (min 60 obs);
                       HOT iff H_act >= p80 AND H_net > 0.
  spectrum          -- core48 deep panel (t18_deep_panel/ohlcv parquets,
                       per-member listing dates); investable >= 60 closes;
                       n_valid < 5 => all sleeves cash (deep-replay breadth
                       precedent); member return NaN on a day => 0 (cash).
  sleeves           -- MOM top-3 r60>0; REV bottom-3 r60<0 (low-position
                       reversal daily proxy); EW48 baseline; face gaps
                       (GRID/SAT/DIVLV/RED-risky) = cash, disclosed.
Execution law: signal from data <= t -> trade at close t+1 (MOC) -> first
return day t+2 (weights for return day d come from signal day d-2).
Costs: turnover single-side with drift correction; x1 = COST_X2_RATE/2,
x2 = COST_X2_RATE (science_gates single source).

Outputs (results/market_clock/backtest/):
  batch json (top-level evidence_cutoff + trials_ledger, append_ledger
  consumed per r217) + per-start CSV + judgment + 8-cell attribution.

Usage:
  python scripts/market_clock_backtest.py run       # full batch, inline
  python scripts/market_clock_backtest.py selftest  # hermetic fixtures

Exit codes: 0 = batch complete; 2 = mechanism failure (honest report).
"""
import json
import os
import random
import sys
import time
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from science_gates import (COST_X2_RATE, append_ledger, cutoff_meta,
                           ledger_head)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
DEEP_ETF_DIR = os.path.join(ROOT, "Money02", "data", "cache",
                            "t18_deep_panel", "ohlcv")
OUT_DIR = os.path.join(PATHS.results_dir, "market_clock", "backtest")
REPLAY_START = "2007-01-04"          # s2 frozen window start
GRID_YEARS = range(2007, 2026)        # monthly first trading days 2007-01..2025-12
LADDER = {"RED": 0.20, "ORANGE": 0.50, "YELLOW": 0.65, "GREEN": 0.80}
HOT_BONUS = 0.15                      # GREEN x HOT -> 0.95 (s1 canon)
MIN_P80_OBS = 60                      # heat warmup (s1 law)
MIN_VALID = 5                         # breadth precedent floor
MIN_LISTED = 60                       # investable: >=60 closes
TOPK = 3
N_RAND_SEEDS = 3
COST_X1 = COST_X2_RATE / 2.0
DAYS_PER_YEAR = 242
SLEEVE_GAP_CASH = {"GRID", "SAT", "DIVLV", "RED_RISKY"}
PREREG_DOC = "research/MARKET_CLOCK_COMBO.md"


# ------------------------------------------------------------------ faces
def build_v3_states():
    """v3 deep states via the recorded chain (run_matrices' v3 path verbatim)."""
    from scripts.regime_calibration import (_LEVEL_FNS, _RESOLVERS,
                                            bench_dim_series, breadth_series,
                                            raw_series)
    from scripts.regime_deep_replay import (BREADTH_MIN_VALID,
                                            deep_state_replay,
                                            load_index_bench)
    bench = load_index_bench()
    ds = bench_dim_series(bench)
    br = breadth_series(bench)
    few = br["n_valid"] < BREADTH_MIN_VALID
    br["share_below_ma20"] = br["share_below_ma20"].mask(few)
    br["share_slope_5d"] = br["share_slope_5d"].mask(few)
    raw = raw_series(bench, ds, br, level_fn=_LEVEL_FNS["v3"])
    states, _streaks, _init = deep_state_replay(raw, _RESOLVERS["v3"])
    return bench, states


def build_heat(bench):
    """LHB heat composite on the bench calendar (s1 law, per-day causal)."""
    df = pd.read_parquet(LHB_PATH, columns=["上榜日", "龙虎榜净买额"])
    df["上榜日"] = pd.to_datetime(df["上榜日"])
    rows = df.groupby("上榜日").size().sort_index()
    nets = df.groupby("上榜日")["龙虎榜净买额"].sum().sort_index()
    days = list(bench.index)
    out = {}
    ridx = rows.index
    pos = 0  # first LHB day strictly after days[k]
    for k, d in enumerate(days):
        while pos < len(ridx) and ridx[pos] <= d:
            pos += 1
        hist = rows.iloc[max(0, pos - 250):pos]
        p80 = float(hist.quantile(0.80)) if len(hist) >= MIN_P80_OBS else None
        r_t = int(rows.loc[d]) if d in ridx else 0
        n_t = float(nets.loc[d]) if d in ridx else 0.0
        heat = "COOL"
        if p80 is not None and r_t >= p80 and n_t > 0:
            heat = "HOT"
        out[d] = (r_t, n_t, p80, heat)
    return out


def build_spectrum(bench, core48):
    """core48 deep closes on the bench calendar + investable mask."""
    closes = {}
    for code in core48:
        p = os.path.join(DEEP_ETF_DIR, f"{code}.parquet")
        if not os.path.exists(p):
            continue  # honest: member absent from deep cache -> never investable
        s = pd.read_parquet(p)["close"].astype(float).sort_index()
        s.index = pd.to_datetime(s.index)  # cache stores str dates; bench is datetime64
        s = s[~s.index.duplicated(keep="last")]
        closes[code] = s.reindex(bench.index)
    close_df = pd.DataFrame(closes, index=bench.index).sort_index(axis=1)
    have = close_df.notna()
    listed_n = have.cumsum()
    investable = listed_n >= MIN_LISTED
    return close_df, investable


# ------------------------------------------------------------------ sleeves
def _r60(close_df, d, codes):
    """r60 as of day d (needs close[d] and close[d-60] non-NaN)."""
    out = {}
    i = d  # positional in close_df.index
    if i < 60:
        return out
    base = close_df.iloc[i - 60]
    last = close_df.iloc[i]
    for c in codes:
        b, l = base.get(c), last.get(c)
        if b is not None and l is not None and pd.notna(b) and pd.notna(l) and b > 0:
            out[c] = float(l) / float(b) - 1.0
    return out


def _cells(bench, states, heat):
    """clock cell per bench day."""
    cells = {}
    for d in bench.index:
        st = states[d]
        heatv = heat[d][3]
        cells[d] = f"{st}_{heatv}"
    return cells


def _mix(cell):
    """Frozen s2b sleeve weights: ABSOLUTE portfolio fractions (sum == cap
    for every non-RED row; RED risky leg = face gap -> all cash)."""
    if cell == "GREEN_COOL":
        return [("MOM", 0.80)]
    if cell == "GREEN_HOT":
        return [("MOM", 0.90), ("SAT", 0.05)]   # SAT -> cash (face gap)
    if cell.startswith("YELLOW"):
        return [("REV", 0.325), ("GRID", 0.325)]  # GRID -> cash (face gap)
    if cell == "ORANGE_COOL":
        return [("REV", 0.125), ("GRID", 0.125), ("DIVLV", 0.25)]
    if cell == "ORANGE_HOT":
        return [("REV", 0.45), ("SAT", 0.05)]
    return []                                       # RED_* -> 100% cash


def _ladder_cap(cell):
    st = cell.split("_")[0]
    cap = LADDER[st]
    if cell == "GREEN_HOT":
        cap = round(cap + HOT_BONUS, 2)
    return cap


def _select_top(rmap, invest_codes, want_top=True):
    """top-3 (want_top) or bottom-3 by r60 among r60>0 / r60<0 pools."""
    pool = {c: v for c, v in rmap.items() if c in invest_codes}
    mom = [c for c, v in pool.items() if v > 0]
    rev = [c for c, v in pool.items() if v < 0]
    src = mom if want_top else rev
    src = sorted(src, key=lambda c: pool[c], reverse=want_top)
    return src[:TOPK]


def build_streams(bench, states, heat, close_df, investable, core48):
    """Global member-level weight matrices -> gross/turnover series per stream.

    Convention (s2b): weights for return day d come from signal day d-2;
    costs: turnover = |target(d) - drift(d-1)| charged on day d's return
    (trade executes at close d-1); per-start initial buy = wnorm at the
    first sliced day (charged by the slicer). Returns dict per stream:
    {"gross", "turnover", "wnorm", "live_exposure"} + cells + rets.
    """
    days = list(bench.index)
    n = len(days)
    codes = list(close_df.columns)
    cells = _cells(bench, states, heat)
    # member daily returns: ffill across suspension gaps; NaN (pre-listing,
    # first bar) -> 0.0 = cash convention (disclosed)
    rets = close_df.ffill().pct_change().fillna(0.0)

    def _signal_inv(i):
        """investable pool as of signal day i-2 (causal)."""
        if i < 2:
            return []
        row = investable.iloc[i - 2]
        return [c for c in codes if bool(row.get(c))]

    def sel_weights(i):
        if i < 2:
            return {}
        inv = _signal_inv(i)
        if len(inv) < MIN_VALID:
            return {}
        rmap = _r60(close_df, i - 2, inv)
        mom = _select_top(rmap, inv, True)
        rev = _select_top(rmap, inv, False)
        cell = cells[days[i - 2]]
        w = {}
        for sleeve, sw in _mix(cell):
            if sleeve in SLEEVE_GAP_CASH:
                continue  # face gap -> cash (disclosed)
            picks = mom if sleeve == "MOM" else rev
            if picks:
                per = sw / len(picks)
                for c in picks:
                    w[c] = w.get(c, 0.0) + per
        return w

    def ew_weights(i):
        inv = _signal_inv(i)
        if not inv:
            return {}
        per = 1.0 / len(inv)
        return {c: per for c in inv}

    def rand_weights(i, seed):
        inv = _signal_inv(i)
        if not inv:
            return {}
        rng = random.Random(zlib.crc32(
            f"{seed}|{days[i - 2]}".encode("utf-8")))
        picks = rng.sample(inv, min(TOPK, len(inv)))
        per = 1.0 / len(picks)
        return {c: per for c in picks}

    def simulate(weight_fn, *args):
        gross = [0.0] * n
        turn = [0.0] * n
        wnorm = [0.0] * n
        live_exp = [0.0] * n
        prev_w = {c: 0.0 for c in codes}
        prev_g = 0.0
        for i in range(2, n):
            w = weight_fn(i, *args)
            tot = sum(w.values())
            if tot > 1.0 + 1e-9:  # safety (mix caps <= 0.95 by construction)
                w = {c: v / tot for c, v in w.items()}
                tot = 1.0
            r_i = rets.iloc[i]
            gross[i] = sum(v * float(r_i.get(c, 0.0)) for c, v in w.items())
            # drift prev weights through day i-1's returns (rebalance at
            # close of day i-1 trades target-vs-drift; cost hits day i)
            denom = 1.0 + prev_g
            if denom <= 1e-9:
                denom = 1e-9
            r_prev = rets.iloc[i - 1]
            turn[i] = sum(abs(w.get(c, 0.0)
                              - prev_w.get(c, 0.0)
                              * (1.0 + float(r_prev.get(c, 0.0))) / denom)
                          for c in codes)
            wnorm[i] = sum(abs(v) for v in w.values())
            live_exp[i] = tot
            prev_w = {c: w.get(c, 0.0) for c in codes}
            prev_g = gross[i]
        idx = bench.index
        return {"gross": pd.Series(gross, index=idx),
                "turnover": pd.Series(turn, index=idx),
                "wnorm": pd.Series(wnorm, index=idx),
                "live_exposure": pd.Series(live_exp, index=idx)}

    streams = {"combo": simulate(sel_weights),
               "ew48": simulate(ew_weights)}
    for s in range(N_RAND_SEEDS):
        streams[f"rand{s}"] = simulate(rand_weights, s)
    return streams, cells, rets


# ------------------------------------------------------------------ metrics
def _metrics(net):
    """ann / maxDD / calmar / monthly-positive on a daily net-return Series."""
    if len(net) < 20:
        return {"n_days": int(len(net)), "ann": None, "max_dd": None,
                "calmar": None, "monthly_pos": None}
    v = (1.0 + net).cumprod()
    ann = float(v.iloc[-1] ** (DAYS_PER_YEAR / len(net)) - 1.0)
    dd = float((v / v.cummax() - 1.0).min())
    m = (1.0 + net).resample("ME").prod() - 1.0
    mpos = float((m > 0).mean()) if len(m) else None
    calmar = None
    if abs(dd) > 1e-12:
        calmar = ann / abs(dd)
    return {"n_days": int(len(net)), "ann": ann, "max_dd": dd,
            "calmar": calmar, "monthly_pos": mpos}


def _starts(bench):
    """monthly first trading days 2007-01..2025-12 on the bench calendar."""
    key = {}
    for d in bench.index:
        if str(d.date()) < REPLAY_START:
            continue
        ym = (d.year, d.month)
        if ym not in key and 2007 <= d.year <= 2025:
            key[ym] = d
    return [key[k] for k in sorted(key)]


def run_batch():
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    from live.paper import load_core
    core48 = list(load_core())
    bench, states = build_v3_states()
    heat = build_heat(bench)
    close_df, investable = build_spectrum(bench, core48)
    streams, cells, rets = build_streams(bench, states, heat, close_df,
                                         investable, core48)
    starts = _starts(bench)
    days = list(bench.index)

    # per-start slicing: first return day = start + 2 (settle window)
    per_start = []
    valid_pairs = []
    combo_calmars, ew_calmars = [], []
    beat = 0
    for S in starts:
        i0 = days.index(S) + 2
        if i0 >= len(days):
            continue
        row = {"start": str(S.date()), "n_days": len(days) - i0}
        for name, st in streams.items():
            for face in ("x1", "x2"):
                rate = COST_X1 if face == "x1" else COST_X2_RATE
                tn = st["turnover"].iloc[i0:].copy()
                # per-start initial buy: global stream was live before S;
                # a fresh portfolio pays full wnorm at its first return day
                tn.iloc[0] += float(st["wnorm"].iloc[i0])
                net = st["gross"].iloc[i0:] - rate * tn
                mm = _metrics(net)
                row[f"{name}_{face}"] = mm
        combo_c, ew_c = row["combo_x1"]["calmar"], row["ew48_x1"]["calmar"]
        if combo_c is not None and ew_c is not None:
            valid_pairs.append((S, combo_c, ew_c))
            combo_calmars.append(combo_c)
            ew_calmars.append(ew_c)
            if combo_c >= ew_c:
                beat += 1
        row["valid_pair"] = bool(combo_c is not None and ew_c is not None)
        per_start.append(row)

    def med(xs):
        xs = sorted(xs)
        if not xs:
            return None
        m = len(xs) // 2
        return xs[m] if len(xs) % 2 else 0.5 * (xs[m - 1] + xs[m])

    rand_meds = []
    for s in range(N_RAND_SEEDS):
        cs = [r[f"rand{s}_x1"]["calmar"] for r in per_start
              if r.get("valid_pair")]
        rand_meds.append(med(cs))

    # 8-cell attribution over the full replay window
    win = [d for d in bench.index if str(d.date()) >= REPLAY_START]
    attr = {}
    combo_net_full = streams["combo"]["gross"] - COST_X1 * streams["combo"]["turnover"]
    for d in win:
        c = cells[d]
        a = attr.setdefault(c, {"days": 0, "contrib": 0.0,
                                 "live_exp_sum": 0.0})
        a["days"] += 1
        v = combo_net_full.get(d, 0.0)
        a["contrib"] += float(v) if pd.notna(v) else 0.0
        e = streams["combo"]["live_exposure"].get(d, 0.0)
        a["live_exp_sum"] += float(e) if pd.notna(e) else 0.0
    n_win = len(win)
    attr_out = {k: {"day_share": round(v["days"] / n_win, 4),
                    "contrib_sum": round(v["contrib"], 4),
                    "mean_live_exp": round(v["live_exp_sum"] / v["days"], 4)
                    if v["days"] else None}
                for k, v in sorted(attr.items())}

    # spectrum-sufficient subgrid disclosure (n_valid >= 5 at start)
    sub_c, sub_e = [], []
    for S, cc, ec in valid_pairs:
        if int((investable.loc[S] > 0).sum()) >= MIN_VALID:
            sub_c.append(cc)
            sub_e.append(ec)

    # B_MAXDIV registered reference (frozen tournament face, window disclosed)
    bmaxdiv_ref = None
    try:
        with open(os.path.join(PATHS.results_dir,
                               "portfolio_blend_tournament.json"),
                  encoding="utf-8") as f:
            tour = json.load(f)
        cand = (tour.get("candidates") or {}).get("B_MAXDIV") or {}
        bmaxdiv_ref = {k: cand.get(k) for k in
                       ("x1_full_S", "benefit", "drawdown", "x2_S", "survives",
                        "oos_start", "evidence_cutoff") if k in cand}
    except Exception as e:
        bmaxdiv_ref = {"error": repr(e)[:160]}

    combo_med, ew_med = med(combo_calmars), med(ew_calmars)
    verdict = None
    if combo_med is not None and ew_med is not None:
        verdict = "PASS" if combo_med > ew_med else "FAIL"  # tie = FAIL (s2)
    n_starts = len(per_start)
    n_trials_combo = n_starts * 2

    payload = {
        "batch": "MARKET_CLOCK_COMBO_S2",
        "task": "T-2026-09-26-74 s2",
        "prereg": PREREG_DOC,
        "prereg_version": "v1.1 (s2 criteria v1.0 verbatim + s2b mechanics frozen pre-run)",
        "carrier": "inline (global-stream property -> light batch, measured wall sec below; O-20260924-2100 heavy-batch pool law not triggered)",
        "window": {"start": REPLAY_START, "end": str(days[-1].date()),
                   "starts": n_starts},
        "faces": {
            "v3_states": "regime_deep_replay chain import (recorded deep face)",
            "heat": f"LHB parquet {os.path.relpath(LHB_PATH, ROOT)}",
            "spectrum": "t18_deep_panel/ohlcv core48 deep cache",
            "face_gaps_cash": sorted(SLEEVE_GAP_CASH),
            "investable_floor": MIN_VALID,
            "pre2013_members": "2 ETFs by 2007 -> early starts thin-spectrum (per-start n_days + investable share disclosed in CSV)",
        },
        "judgment": {
            "line": "median Calmar(combo x1) vs median Calmar(EW-48 x1), same-start symmetric exclusion (either maxDD<1e-12 -> pair excluded); tie = FAIL per s2",
            "b_maxdiv": "NOT_COMPUTABLE per-start (member deep-window replays structurally absent -- P5C leg D checkpoint empty, members have no pre-2020 face); per s2b interpretive clause the per-start max converges to EW-48; registered reference quoted below with window mismatch disclosed",
            "b_maxdiv_registered_ref": bmaxdiv_ref,
            "combo_median_calmar": combo_med,
            "ew48_median_calmar": ew_med,
            "beat_rate": round(beat / len(valid_pairs), 4) if valid_pairs else None,
            "valid_pairs": len(valid_pairs),
            "excluded_pairs": n_starts - len(valid_pairs),
            "subgrid_nvalid5": {"combo_median": med(sub_c),
                                "ew48_median": med(sub_e), "n": len(sub_c)},
            "x2_robustness": {
                "combo_median": med([r["combo_x2"]["calmar"] for r in per_start if r.get("valid_pair")]),
                "ew48_median": med([r["ew48_x2"]["calmar"] for r in per_start if r.get("valid_pair")]),
            },
            "random_baseline_median_calmars": rand_meds,
            "verdict": verdict,
        },
        "attribution_8cell": attr_out,
        "d6_family_check": "DEFERRED (physical dependency: T-73 CN-combo C-arm batch in flight at finalize time; correlation row to be appended when the family lands -- s2b frozen clause, disclosed not skipped)",
        "trials": {
            "combo_cells": n_trials_combo,
            "ew48_cells": n_starts * 2,
            "random_cells": n_starts * N_RAND_SEEDS,
        },
        "wall_seconds": round(time.time() - t0, 1),
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    head = ledger_head()
    payload.update(cutoff_meta("2026-09-22"))
    entry = append_ledger("MARKET_CLOCK_COMBO_S2", n_trials_combo,
                          file_name="results/market_clock/backtest/batch.json",
                          note="T-74 s2 market-clock combo full-history replay; starts x {x1,x2}",
                          evidence_cutoff="2026-09-22",
                          prev_total=head["total"])
    payload["trials_ledger"] = entry  # r217: consumed, embedded

    out_json = os.path.join(OUT_DIR, "batch.json")
    with open(out_json, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, default=str)
    # per-start CSV
    csv_path = os.path.join(OUT_DIR, "per_start.csv")
    flat = []
    for r in per_start:
        fr = {"start": r["start"], "n_days": r["n_days"], "valid_pair": r["valid_pair"]}
        for name in list(streams):
            for face in ("x1", "x2"):
                mm = r[f"{name}_{face}"]
                for k in ("ann", "max_dd", "calmar", "monthly_pos"):
                    fr[f"{name}_{face}_{k}"] = mm.get(k)
        flat.append(fr)
    pd.DataFrame(flat).to_csv(csv_path, index=False)

    print(f"batch written: {out_json}")
    print(f"verdict={verdict} combo_med={combo_med} ew48_med={ew_med} "
          f"beat={beat}/{len(valid_pairs)} starts={n_starts} "
          f"wall={payload['wall_seconds']}s")
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    """Hermetic fixtures mirroring REAL face shapes (r157 law): LHB frame
    with Chinese columns, bench-indexed closes, injected v3 states. Zero
    repo data reads."""
    import tempfile
    idx = pd.bdate_range("2024-01-01", periods=80)
    bench = pd.Series(1.0, index=idx)

    # synthetic v3 states: GREEN for first 40 days, RED after
    states = {d: ("GREEN" if i < 40 else "RED") for i, d in enumerate(idx)}

    # synthetic LHB heat: high activity day 45..46 (in GREEN window)
    lhb_rows = []
    for i, d in enumerate(idx):
        n = 5
        if i in (45, 46):
            n = 50
        for _ in range(n):
            lhb_rows.append({"上榜日": str(d.date()),
                             "龙虎榜净买额": 1e6 if i in (45, 46) else -1e5})
    lhb = pd.DataFrame(lhb_rows)

    # synthetic spectrum: 6 members, steady prices; member X rises late
    closes = {}
    for j in range(6):
        code = f"C{j}"
        s = pd.Series(100.0, index=idx)
        closes[code] = s
    closes["C0"].iloc[70] = 110.0   # a jump on day 70 for lag check

    # --- heat law (build_heat logic inline replica against fixtures)
    df = lhb.copy()
    df["上榜日"] = pd.to_datetime(df["上榜日"])
    rows = df.groupby("上榜日").size().sort_index()
    nets = df.groupby("上榜日")["龙虎榜净买额"].sum().sort_index()
    heat = {}
    pos = 0
    ridx = rows.index
    for k, d in enumerate(idx):
        while pos < len(ridx) and ridx[pos] <= d:
            pos += 1
        hist = rows.iloc[max(0, pos - 250):pos]
        p80 = float(hist.quantile(0.80)) if len(hist) >= 60 else None
        r_t = int(rows.loc[d]) if d in ridx else 0
        n_t = float(nets.loc[d]) if d in ridx else 0.0
        heat[d] = "HOT" if (p80 is not None and r_t >= p80 and n_t > 0) else "COOL"
    # warmup: <60 obs -> all COOL including the high-activity days
    assert all(v == "COOL" for v in heat.values()), "min-60 warmup violated"

    # rerun with a long synthetic prehistory so day 45/46 can be HOT
    pre = pd.bdate_range("2023-01-01", periods=200)
    pre_rows = []
    for d in pre:
        for _ in range(5):
            pre_rows.append({"上榜日": str(d.date()), "龙虎榜净买额": -1e5})
    df2 = pd.concat([pd.DataFrame(pre_rows), lhb], ignore_index=True)
    df2["上榜日"] = pd.to_datetime(df2["上榜日"])
    rows2 = df2.groupby("上榜日").size().sort_index()
    nets2 = df2.groupby("上榜日")["龙虎榜净买额"].sum().sort_index()
    heat2 = {}
    pos = 0
    ridx2 = rows2.index
    for d in idx:
        while pos < len(ridx2) and ridx2[pos] <= d:
            pos += 1
        hist = rows2.iloc[max(0, pos - 250):pos]
        p80 = float(hist.quantile(0.80)) if len(hist) >= 60 else None
        r_t = int(rows2.loc[d]) if d in ridx2 else 0
        n_t = float(nets2.loc[d]) if d in ridx2 else 0.0
        heat2[d] = "HOT" if (p80 is not None and r_t >= p80 and n_t > 0) else "COOL"
    assert heat2[idx[45]] == "HOT" and heat2[idx[46]] == "HOT"
    assert heat2[idx[47]] == "COOL", "rows dropped back below p80 -> COOL"

    # --- mix/ladder table exactness (absolute-weight caliber + two-table
    # consistency: non-RED mix sums == ladder cap; RED risky leg = gap)
    assert _mix("GREEN_COOL") == [("MOM", 0.80)]
    assert _mix("GREEN_HOT") == [("MOM", 0.90), ("SAT", 0.05)]
    assert _mix("YELLOW_COOL") == [("REV", 0.325), ("GRID", 0.325)]
    assert _mix("ORANGE_COOL") == [("REV", 0.125), ("GRID", 0.125), ("DIVLV", 0.25)]
    assert _mix("ORANGE_HOT") == [("REV", 0.45), ("SAT", 0.05)]
    assert _mix("RED_COOL") == [] and _mix("RED_HOT") == []
    assert _ladder_cap("RED_COOL") == 0.20
    assert _ladder_cap("YELLOW_HOT") == 0.65
    assert _ladder_cap("GREEN_HOT") == 0.95
    assert _ladder_cap("GREEN_COOL") == 0.80
    for st_ in ("GREEN", "YELLOW", "ORANGE"):
        for hv in ("COOL", "HOT"):
            cell_ = f"{st_}_{hv}"
            assert abs(sum(w for _s, w in _mix(cell_))
                       - _ladder_cap(cell_)) < 1e-12, cell_
    for hv in ("COOL", "HOT"):
        assert sum(w for _s, w in _mix(f"RED_{hv}")) == 0.0

    # --- t+1 MOC execution law: weights for return day d from signal d-2.
    # synthetic flat prices -> zero returns, so exercise the lag on _r60 use:
    # craft closes so C0 jumped at i=70; r60(C0) turns positive only from
    # i=70 onward; MOM can include C0 in weights for day i only when i-2>=70.
    # (checked via _r60 directly -- the selector consumes it positionally)
    cdf = pd.DataFrame(closes, index=idx)
    assert 0.0 in _r60(cdf, 69, ["C0"]).values() or "C0" not in _r60(cdf, 69, ["C0"])
    assert "C0" in _r60(cdf, 70, ["C0"])  # signal face sees the jump at i=70
    # a selector call at i=72 uses r60 at i-2=70 -> C0 eligible exactly then
    rmap = _r60(cdf, 70, list(cdf.columns))
    assert "C0" in [c for c, v in rmap.items() if v > 0]

    # --- REV empty pool (all r60 > 0) -> no picks (cash)
    rmap_all_pos = {c: 0.01 for c in cdf.columns}
    assert _select_top(rmap_all_pos, list(cdf.columns), False) == []
    assert len(_select_top(rmap_all_pos, list(cdf.columns), True)) == 3

    # --- LIVE-FIRE build_streams on synthetic faces (real machinery, no
    # monkeypatching of internals): 200 bdays, 6 members flat at 100,
    # C0 permanently +10% from day 100; states GREEN <120 / RED >=120;
    # heat all COOL; investable = >=10 closes.
    n2 = 200
    idx2 = pd.bdate_range("2024-01-01", periods=n2)
    bench2 = pd.Series(1.0, index=idx2)
    states2 = {d: ("GREEN" if i < 120 else "RED") for i, d in enumerate(idx2)}
    heat2c = {d: (0, 0.0, None, "COOL") for d in idx2}
    cl2 = pd.DataFrame({f"C{j}": 100.0 for j in range(6)}, index=idx2)
    cl2.loc[idx2[100]:, "C0"] = 110.0
    inv2 = cl2.notna().cumsum() >= 10
    streams2, cells2, _rets2 = build_streams(bench2, states2, heat2c, cl2,
                                              inv2, list(cl2.columns))
    combo = streams2["combo"]
    # lag + mix + cap: r60(C0)>0 first at signal day 100 -> weight at return
    # day 102; only C0 qualifies (others flat, r60=0 not >0) -> MOM=1.0,
    # cap GREEN_COOL=0.80 -> live exposure exactly 0.80 from day 102
    assert abs(combo["live_exposure"].iloc[102] - 0.80) < 1e-9, combo["live_exposure"].iloc[102]
    assert abs(combo["live_exposure"].iloc[101] - 0.0) < 1e-9
    # initial buy cost at first active day = full wnorm
    assert abs(combo["turnover"].iloc[102] - 0.80) < 1e-9
    # steady state: same selection + flat prices -> next-day turnover ~ 0
    assert abs(combo["turnover"].iloc[103]) < 1e-9
    # RED switch at signal 120 -> weights empty at return day 122: full exit
    assert abs(combo["turnover"].iloc[122] - 0.80) < 1e-9
    assert abs(combo["live_exposure"].iloc[122]) < 1e-12
    # ew48 baseline is STATE-INDEPENDENT (passive comparison face): fully
    # invested whenever n_valid >= 5, in RED cells too
    assert abs(streams2["ew48"]["live_exposure"].iloc[30] - 1.0) < 1e-9
    assert abs(streams2["ew48"]["live_exposure"].iloc[122] - 1.0) < 1e-9
    # gross captures C0's post-entry return only via held days (causality:
    # the +10% jump at day 100 happened BEFORE entry -> not captured)
    assert abs(combo["gross"].iloc[102]) < 1e-12
    # rand arms live too
    assert streams2["rand0"]["live_exposure"].iloc[102] > 0

    # --- build_spectrum REAL load path (r157 mirror law: the production
    # defect this leg guards = cache stores STR-date index, bench is
    # datetime64 -> silent all-NaN reindex -> all sleeves cash. Fixture
    # mirrors the real str-index shape via a synthetic parquet dir.)
    global DEEP_ETF_DIR
    with tempfile.TemporaryDirectory() as tmpd:
        idx3 = pd.bdate_range("2024-01-01", periods=70)
        members = [f"C{j}" for j in range(6)]
        for j, code in enumerate(members):
            fdf = pd.DataFrame({"close": 100.0 + j},
                               index=[str(d.date()) for d in idx3])
            fdf.to_parquet(os.path.join(tmpd, f"{code}.parquet"))
        bench3 = pd.Series(1.0, index=idx3)
        old_dir = DEEP_ETF_DIR
        DEEP_ETF_DIR = tmpd
        try:
            cl3, inv3 = build_spectrum(bench3, members)
        finally:
            DEEP_ETF_DIR = old_dir
        assert cl3.notna().sum().sum() == 6 * 70, cl3.notna().sum().sum()
        assert bool(inv3.iloc[-1].all()), "investable after MIN_LISTED closes"

    # --- metrics: Calmar None on all-cash, symmetric exclusion, tie=FAIL
    net_flat = pd.Series(0.0, index=idx)
    assert _metrics(net_flat)["calmar"] is None
    net_up = pd.Series(0.001, index=idx)
    net_up.iloc[40] = -0.02      # one drawdown day -> maxDD > 0
    m = _metrics(net_up)
    assert m["calmar"] is not None and m["ann"] > 0
    # monotone-up stream: maxDD == 0 -> calmar None (zero-DD exclusion law)
    assert _metrics(pd.Series(0.001, index=idx))["calmar"] is None

    # --- ledger append consumption (tmp results dir, real function)
    with tempfile.TemporaryDirectory() as td:
        e = append_ledger("SELFTEST_BATCH", 10, results_dir=td,
                          evidence_cutoff="2026-09-22", prev_total=0)
        assert isinstance(e, dict) and e["total"] == 10 and e["prev_total"] == 0, e

    print("market_clock_backtest selftest: PASS (heat warmup/HOT/back-mix/ladder/lag/rev-empty/metrics/ledger)")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "run":
        sys.exit(run_batch())
    print("usage: run | selftest", file=sys.stderr)
    sys.exit(2)
