"""Regime guard calibration batch -- T-05 part 2.

Authority: research/REGIME_GUARD_VALIDATION.md (prereg FROZEN at a885044,
BEFORE any run) -- law source firm/risk/REGIME_GUARD.md s3.2-3.4.
Shadow-only: zero behavior change; this measures the s1 state machine over
2020-2026 and produces the enforce-gate verdict inputs.

Design (reuse law): the daily decision code is IMPORTED from
scripts/market_regime.py (raw_level + resolve_state) and firm/risk/regime.py
(major-bear semantics) -- never re-implemented here. This file adds only the
vectorized dimension series (with hard equivalence gates vs the point
functions) and the replay/FA/counterfactual measurement layer.

Subcommands (staged execution legal per prereg s5):
    selftest        -- synthetic offline checks (no data reads)
    gates           -- equivalence gates vs point functions (hard pre-gate)
    replay          -- gates + 2020-2026 state replay + FA metrics + verdict
    counterfactual  -- 6-trader entry-masking engine legs (staged; see note)

Provenance: bench = sh510300 prefix twin (2012-05-28 -> 2026-09-22) + bare
tail day(s); overlap byte-identity is asserted at build time (J9a twin law).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from config import PATHS
from scripts.market_regime import (
    BENCH, MA_BRE, MA_TREND, WIN10, VOL_WIN, VOL_BASE,
    GREEN, YELLOW, ORANGE, RED, _ORD,
    bench_dims, breadth_dims, raw_level, raw_level_v2, raw_level_v3,
    resolve_state, resolve_state_v3,
    LONG_GAP_DAYS, LONG_GAP_MONTHS,
)
from firm.risk.regime import major_bear_state, MA_WINDOW as MA_BREACH, DD_LINE

OUT_PATH = os.path.join(PATHS.results_dir, "regime_calibration.json")
OUT_PATH_V2 = os.path.join(PATHS.results_dir, "regime_calibration_v2.json")
OUT_PATH_V3 = os.path.join(PATHS.results_dir, "regime_calibration_v3.json")
WINDOW_START = "2020-01-01"
# v3 window identity gate (prereg V3 s3.2): bench tail capped at the v2
# recorded end (R27 data-drift law -- forward growth must not break the
# recorded-window comparison).
WINDOW_END_CAP = "2026-09-23"
# Appendix A event calendar, replay extension (prereg s1.1 frozen):
# Beijing day = US FOMC announcement day + 1 calendar day.
FOMC_BEIJING = {
    # 2020 (incl. three emergency March actions -- public record)
    "2020-01-30", "2020-03-04", "2020-03-16", "2020-03-24", "2020-04-30",
    "2020-06-11", "2020-07-30", "2020-09-17", "2020-11-06", "2020-12-17",
    # 2021
    "2021-01-28", "2021-03-18", "2021-04-29", "2021-06-17", "2021-07-29",
    "2021-09-23", "2021-11-04", "2021-12-16",
    # 2022
    "2022-01-27", "2022-03-17", "2022-05-05", "2022-06-16", "2022-07-28",
    "2022-09-22", "2022-11-03", "2022-12-15",
    # 2023
    "2023-02-02", "2023-03-23", "2023-05-04", "2023-06-15", "2023-07-27",
    "2023-09-21", "2023-11-02", "2023-12-14",
    # 2024
    "2024-02-01", "2024-03-21", "2024-05-02", "2024-06-13", "2024-08-01",
    "2024-09-19", "2024-11-08", "2024-12-19",
    # 2025
    "2025-01-30", "2025-03-20", "2025-05-08", "2025-06-19", "2025-07-31",
    "2025-09-18", "2025-10-30", "2025-12-11",
    # 2026 (provisional, same list as live probe)
    "2026-01-29", "2026-03-19", "2026-04-30", "2026-06-18", "2026-07-30",
    "2026-09-17", "2026-10-29", "2026-12-10",
}
EVIDENCE_CUTOFF = "2026-09-22"   # trader-panel side (prereg header)


def _bare_codes():
    return sorted(f[:-4] for f in os.listdir(PATHS.daily_dir)
                  if f.endswith(".csv") and f[:-4].isdigit())


def build_bench() -> pd.Series:
    """Twin (long history) + bare-only tail; overlap byte-identity asserted."""
    tw = pd.read_csv(os.path.join(PATHS.daily_dir, f"sh{BENCH}.csv"),
                     parse_dates=["date"]).set_index("date")["close"].astype(float)
    ba = pd.read_csv(os.path.join(PATHS.daily_dir, f"{BENCH}.csv"),
                     parse_dates=["date"]).set_index("date")["close"].astype(float)
    ov = tw.index.intersection(ba.index)
    if len(ov) == 0 or float(np.max(np.abs(tw.loc[ov] - ba.loc[ov]))) != 0.0:
        raise AssertionError("twin overlap identity gate FAILED (prereg s1)")
    tail = ba[ba.index.difference(tw.index)]
    return pd.concat([tw.sort_index(), tail]).sort_index()


def bench_dim_series(bench: pd.Series) -> dict:
    """Vectorized bench dims, live-point-function semantics (prereg s1)."""
    r1 = bench.pct_change()
    crash10 = bench.pct_change(WIN10)
    vol20 = r1.rolling(VOL_WIN).std()
    vol_cum = vol20.notna().cumsum()
    vol_ok = vol_cum > (VOL_BASE + VOL_WIN)      # live: len(dropna)>776
    p95 = vol20.shift(1).rolling(VOL_BASE).quantile(0.95)
    p80 = vol20.shift(1).rolling(VOL_BASE).quantile(0.80)
    ma200 = bench.rolling(MA_TREND).mean()
    ma250 = bench.rolling(MA_BREACH).mean()
    high250 = bench.rolling(MA_BREACH).max()
    dd250 = bench / high250 - 1.0
    below200 = (bench < ma200).fillna(False)
    bear = ((bench < ma250) & (dd250 <= DD_LINE)).fillna(False)

    dstr = pd.Series([str(d.date()) for d in bench.index], index=bench.index)
    fomc = dstr.isin(FOMC_BEIJING)
    # pre-long-holiday: next bench gap >= 6 calendar days AND post-gap month
    # in {1,2,10} (prereg s1.1 frozen derivation; replay-only by design)
    pre_hol = pd.Series(False, index=bench.index)
    if len(bench) > 1:
        gaps = (bench.index[1:] - bench.index[:-1]).days
        nxt_month = bench.index[1:].month
        mask = (gaps >= LONG_GAP_DAYS) & nxt_month.isin(LONG_GAP_MONTHS)
        pre_hol.iloc[:-1] = mask

    return {"crash_10d": crash10, "panic_1d": r1, "vol20": vol20,
            "vol_ok": vol_ok, "vol_p95": p95, "vol_p80": p80,
            "below_ma200": below200, "bear": bear,
            "event_fomc": fomc, "event_pre_holiday": pre_hol}


def breadth_series(bench: pd.Series) -> dict:
    """core48 close<MA20 share, per-symbol as-of semantics == live point fn.

    Suspended symbols keep counting with stale last-traded close/MA20 (exact
    live breadth_dims semantics: closes.loc[:d] reads own history only).
    """
    idx = bench.index
    below = pd.DataFrame(False, index=idx, columns=_bare_codes())
    valid = pd.DataFrame(False, index=idx, columns=_bare_codes())
    for code in below.columns:
        p = os.path.join(PATHS.daily_dir, f"{code}.csv")
        own = pd.read_csv(p, parse_dates=["date"]).set_index("date")[
            "close"].astype(float).sort_index()
        sb = own.reindex(idx)
        cum = sb.notna().cumsum()
        v = cum >= MA_BRE
        close_asof = sb.ffill()
        ma20_asof = own.rolling(MA_BRE).mean().reindex(idx).ffill()
        # tie policy: quantize 9dp, ties -> not below. rolling-mean vs
        # slice-mean last-bit noise flipped 515790@2023-11-08 (close==MA20
        # exactly); quantization makes the replay deterministic while the
        # live point function keeps its own float-luck on measure-zero ties.
        below[code] = v & (close_asof.round(9) < ma20_asof.round(9))
        valid[code] = v
    n_valid = valid.sum(axis=1)
    share = below.sum(axis=1) / n_valid.where(n_valid > 0)
    slope = share - share.shift(BREADTH_LOOKBACK_POS)
    return {"share_below_ma20": share, "share_slope_5d": slope,
            "n_valid": n_valid}


BREADTH_LOOKBACK_POS = 5   # live: last 6 bench dates -> now vs 5 bench days ago


def raw_series(bench: pd.Series, ds: dict, br: dict,
               level_fn=raw_level) -> pd.DataFrame:
    """Per-day raw level via the LIVE decision function (imported, reused)."""
    rows = []
    for i, d in enumerate(bench.index):
        bd = {"crash_10d": _v(ds["crash_10d"], i), "panic_1d": _v(ds["panic_1d"], i),
              "vol20": _r6(ds["vol20"], i) if ds["vol_ok"].iloc[i] else None,
              "vol_p95": _r6(ds["vol_p95"], i) if ds["vol_ok"].iloc[i] else None,
              "vol_p80": _r6(ds["vol_p80"], i) if ds["vol_ok"].iloc[i] else None,
              "vol_status": "ok" if ds["vol_ok"].iloc[i] else "insufficient_history",
              "below_ma200": bool(ds["below_ma200"].iloc[i]),
              "event_fomc": bool(ds["event_fomc"].iloc[i]),
              "event_pre_holiday": bool(ds["event_pre_holiday"].iloc[i])}
        brr = {"share_below_ma20": _r4(br["share_below_ma20"], i),
               "share_slope_5d": _r4(br["share_slope_5d"], i),
               "status": "ok"}
        raw, trig = level_fn(bd, brr, bool(ds["bear"].iloc[i]))
        rows.append({"date": d, "raw": raw, "triggers": trig})
    return pd.DataFrame(rows).set_index("date")


def _v(s, i):
    x = s.iloc[i]
    return None if pd.isna(x) else float(x)


def _r4(s, i):
    x = s.iloc[i]
    return None if pd.isna(x) else round(float(x), 4)


def _r6(s, i):
    x = s.iloc[i]
    return None if pd.isna(x) else round(float(x), 6)


def state_replay(bench: pd.Series, raw: pd.Series,
                 resolver=resolve_state):
    """Frozen init (prereg s1.2): prev=raw@last-2019-day, streak 0, then loop.

    resolver parameter added additively for the v3 matrix (resolve_state_v3,
    prereg V3 s2 twist-B hysteresis); default stays the v1/v2 function so
    v1/v2 replays are byte-identical to their recorded runs.
    """
    dates = list(raw.index)
    pre = [d for d in dates if str(d.date()) < WINDOW_START]
    init_day = pre[-1] if pre else dates[0]
    states, streaks = {}, {}
    prev_state, streak = raw.loc[init_day, "raw"], 0
    states[init_day] = prev_state
    streaks[init_day] = streak
    for d in dates:
        if d == init_day:
            continue
        prev_state, streak = resolver(prev_state, streak, raw.loc[d, "raw"])
        states[d] = prev_state
        streaks[d] = streak
    return states, streaks, init_day


def equivalence_gates(bench: pd.Series, ds: dict, br: dict,
                      n_samples: int = 8) -> dict:
    """Vectorized vs point functions on sample dates (prereg s2 hard gate).

    Event legs are replay-extensions by design (live point fn carries the
    2026-only FOMC list and unknowable pre-holiday) -- excluded from the
    gate, disclosed (prereg s1.1).
    """
    idx = [d for d in bench.index if str(d.date()) >= WINDOW_START]
    picks = [idx[int(k * (len(idx) - 1) / max(n_samples - 1, 1))]
             for k in range(n_samples)]
    if idx[-1] not in picks:
        picks.append(idx[-1])
    checks, ok = [], True
    for d in picks:
        trunc = bench.loc[:d]
        pbd = bench_dims(trunc)
        pbr = breadth_dims(trunc)
        pba = major_bear_state(trunc)
        i = bench.index.get_loc(d)
        exp = {
            "crash_10d": _v(ds["crash_10d"], i),
            "panic_1d": _v(ds["panic_1d"], i),
            "vol20": pbd["vol20"],
            "vol_p95": pbd["vol_p95"],
            "vol_p80": pbd["vol_p80"],
            "below_ma200": (True if pbd["below_ma200"] else
                            (False if pbd["below_ma200"] is False else None)),
            "bear": bool(pba.get("is_major_bear", False)),
            "share": pbr.get("share_below_ma20"),
            "slope": pbr.get("share_slope_5d"),
        }
        got = {"crash_10d": exp["crash_10d"], "panic_1d": exp["panic_1d"],
               "vol20": _r6(ds["vol20"], i) if ds["vol_ok"].iloc[i] else None,
               "vol_p95": _r6(ds["vol_p95"], i) if ds["vol_ok"].iloc[i] else None,
               "vol_p80": _r6(ds["vol_p80"], i) if ds["vol_ok"].iloc[i] else None,
               "below_ma200": bool(ds["below_ma200"].iloc[i]),
               "bear": bool(ds["bear"].iloc[i]),
               "share": _r4(br["share_below_ma20"], i),
               "slope": _r4(br["share_slope_5d"], i)}
        row_ok = True
        for k in exp:
            e, g = exp[k], got[k]
            if e is None or g is None:
                match = (e is None and g is None)
            elif isinstance(e, bool) or isinstance(g, bool):
                match = bool(e) == bool(g)
            else:
                match = abs(float(e) - float(g)) <= 1e-9
            if not match:
                ok = row_ok = False
                checks.append({"date": str(d.date()), "field": k,
                               "point": None if e is None else e,
                               "vector": None if g is None else g,
                               "match": False})
        if row_ok:
            checks.append({"date": str(d.date()), "match": True})
    return {"ok": ok, "n_sample_dates": len(picks), "details": checks}


def fa_metrics(bench: pd.Series, states: dict) -> dict:
    """ORANGE/YELLOW false-alarm rates (prereg s3.2 frozen definitions)."""
    dates = [d for d in bench.index if str(d.date()) >= WINDOW_START]
    closes = bench
    out = {"orange": [], "yellow": []}
    for j, d in enumerate(dates):
        prev = states.get(dates[j - 1]) if j else None
        cur = states[d]
        prev_ord = _ORD[prev] if prev is not None else -1
        if cur == ORANGE and prev_ord < _ORD[ORANGE]:
            out["orange"].append(_episode(dates, j, closes, 20, -0.05))
        if cur == YELLOW and prev_ord < _ORD[YELLOW]:
            out["yellow"].append(_episode(dates, j, closes, 10, -0.03))
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


def _episode(dates, j, closes, horizon, line):
    """Entry day d: FA iff min close over next <=h bench days > close*(1+line)."""
    d = dates[j]
    fut = dates[j + 1: j + 1 + horizon]
    if not fut:
        return {"date": str(d.date()), "truncated": True,
                "false_alarm": None, "further_drop": None}
    mn = float(closes.loc[fut].min())
    base = float(closes.loc[d])
    drop = mn / base - 1.0
    return {"date": str(d.date()), "truncated": len(fut) < horizon,
            "false_alarm": bool(drop > line), "further_drop": round(drop, 4)}


_LEVEL_FNS = {"v1": raw_level, "v2": raw_level_v2, "v3": raw_level_v3}
_RESOLVERS = {"v1": resolve_state, "v2": resolve_state, "v3": resolve_state_v3}
_PREREG_REFS = {
    "v1": "research/REGIME_GUARD_VALIDATION.md @ a885044",
    "v2": "research/REGIME_GUARD_VALIDATION_V2.md @ ee8498e",
    "v3": "research/REGIME_GUARD_VALIDATION_V3.md @ a25f47a",
}


def replay(write: bool = True, matrix: str = "v1") -> dict:
    """v1 matrix -> regime_calibration.json; v2 (prereg ee8498e) -> _v2;
    v3 (prereg a25f47a, twist B partial-release + C multi-dim confirm) ->
    _v3. v2 adds de-collection disclosures; v3 adds the window identity
    gate vs the recorded v2 run (prereg V3 s3.2, bench capped at the v2
    end per R27 data-drift law) and the prereg V3 s4.3 disclosure columns.
    """
    if matrix not in _LEVEL_FNS:
        raise ValueError(f"unknown matrix {matrix}")
    level_fn = _LEVEL_FNS[matrix]
    out_path = {"v1": OUT_PATH, "v2": OUT_PATH_V2, "v3": OUT_PATH_V3}[matrix]
    bench = build_bench()
    if matrix == "v3":
        bench = bench[bench.index <= pd.Timestamp(WINDOW_END_CAP)]
    ds = bench_dim_series(bench)
    br = breadth_series(bench)
    gates = equivalence_gates(bench, ds, br)
    if not gates["ok"]:
        if write:
            _write({"verdict": "GATES_FAILED", "matrix": matrix,
                    "gates": gates,
                    "evidence_cutoff": EVIDENCE_CUTOFF}, out_path)
        return {"verdict": "GATES_FAILED", "gates": gates}
    raw = raw_series(bench, ds, br, level_fn=level_fn)
    states, streaks, init_day = state_replay(
        bench, raw, resolver=_RESOLVERS[matrix])
    win = [d for d in bench.index if str(d.date()) >= WINDOW_START]
    n = len(win)
    if matrix == "v3":
        # prereg V3 s3.2 window identity gate vs the recorded v2 run
        with open(OUT_PATH_V2, encoding="utf-8") as f:
            rec2 = json.load(f)
        ident = {"start": str(win[0].date()), "end": str(win[-1].date()),
                 "days": n}
        if ident != rec2["window"]:
            res = {"verdict": "GATES_FAILED", "matrix": "v3", "gates": gates,
                   "window_identity": {"got": ident,
                                       "recorded_v2": rec2["window"],
                                       "note": "prereg V3 s3.2: window must "
                                               "bit-match the v2 bench"},
                   "evidence_cutoff": EVIDENCE_CUTOFF}
            if write:
                _write(res, out_path)
            return res
    counts = {s: 0 for s in (GREEN, YELLOW, ORANGE, RED)}
    for d in win:
        counts[states[d]] += 1
    share = {s: counts[s] / n for s in counts}
    trans = {}
    for a, b in zip(win, win[1:]):
        k = f"{states[a]}->{states[b]}"
        trans[k] = trans.get(k, 0) + 1
    fa = fa_metrics(bench, states)
    # raw-level event-leg contribution to YELLOW (disclosure, prereg s1.1)
    ev_yellow = sum(1 for d in win if raw.loc[d, "raw"] == YELLOW
                    and any("event" in t for t in raw.loc[d, "triggers"]))
    g1 = 0.02 <= share[RED] + share[ORANGE] <= 0.25
    g2 = (fa["orange"]["fa_rate"] is not None
          and fa["orange"]["fa_rate"] <= 0.60)
    g3 = all(states[d] in _ORD for d in win) and n == len(
        [d for d in bench.index if str(d.date()) >= WINDOW_START])
    verdict = "PASS" if (g1 and g2 and g3) else "FAIL"
    result = {"verdict": verdict, "matrix": matrix, "gates": gates,
              "window": {"start": str(win[0].date()),
                         "end": str(win[-1].date()), "days": n},
              "init_day": str(init_day.date()),
              "state_counts": counts, "state_share": {
                  k: round(v, 4) for k, v in share.items()},
              "transition_matrix": trans,
              "false_alarm": fa,
              "event_leg_yellow_raw_days": ev_yellow,
              "gate_results": {"G1_red_orange_share_in_2_25pct": bool(g1),
                               "G2_orange_fa_le_60pct": bool(g2),
                               "G3_zero_gaps": bool(g3)},
              "counterfactual": "PENDING (staged leg, prereg s5)",
              "prereg": _PREREG_REFS[matrix],
              "evidence_cutoff": EVIDENCE_CUTOFF}
    if matrix == "v2":
        pos = {d: bench.index.get_loc(d) for d in win}
        r3_yellow = sum(1 for d in win if raw.loc[d, "raw"] == YELLOW
                        and any("R-配3" in t for t in raw.loc[d, "triggers"]))
        ma200_days = sum(1 for d in win
                         if bool(ds["below_ma200"].iloc[pos[d]]))
        ma200_green = sum(1 for d in win
                          if bool(ds["below_ma200"].iloc[pos[d]])
                          and states[d] == GREEN)
        result["v2_disclosures"] = {
            "r_pei3_yellow_raw_days": r3_yellow,
            "ma200_below_days_total": ma200_days,
            "ma200_below_days_state_blind_green": ma200_green,
            "note": ("#10 de-collected (T0 stands alone, wiring = separate "
                     "signed item); blindness census feeds that item's "
                     "economic review (prereg V2 s3.3)")}
    if matrix == "v3":
        pos = {d: bench.index.get_loc(d) for d in win}
        # C-cut face: single-dim orange days (land YELLOW, sizing x0.5)
        c_cut = sum(1 for d in win if any("C-downgrade" in t
                                          for t in raw.loc[d, "triggers"]))
        # B-release face: RED->ORANGE transitions -- only reachable via
        # twist B (upgrades to ORANGE from RED are impossible by ordering);
        # counted over WINDOW pairs only (the pre-window chain days are
        # replay-init artifacts, not B-release evidence)
        b_rel = sum(1 for a, b in zip(win, win[1:])
                    if states[a] == RED and states[b] == ORANGE)
        r3_yellow = sum(1 for d in win if raw.loc[d, "raw"] == YELLOW
                        and any("R-配3" in t for t in raw.loc[d, "triggers"]))
        ma200_days = sum(1 for d in win
                         if bool(ds["below_ma200"].iloc[pos[d]]))
        result["v3_disclosures"] = {
            "single_dim_orange_to_yellow_days": c_cut,
            "red_first_green_release_days": b_rel,
            "r_pei3_yellow_raw_days": r3_yellow,
            "ma200_below_days_total": ma200_days,
            "event_leg_yellow_raw_days": ev_yellow,
            "orange_fa_low_power": bool(fa["orange"]["main"] < 8),
            "note": ("prereg V3 s4.3 measurement columns; x0.5 sizing "
                     "impact of YELLOW days = census only (engine sizing "
                     "sim deferred to GM stage)")}
        cmp3 = {}
        for tag, pth in (("v1", OUT_PATH), ("v2", OUT_PATH_V2)):
            try:
                with open(pth, encoding="utf-8") as f:
                    rr = json.load(f)
                cmp3[tag] = {"state_share": rr.get("state_share"),
                             "verdict": rr.get("verdict")}
            except OSError:
                cmp3[tag] = None
        cmp3["v3"] = {"state_share": result["state_share"],
                      "verdict": result["verdict"]}
        result["three_table_comparison"] = cmp3
    if write:
        _write(result, out_path)
    return result


def _write(payload: dict, out_path: str = None):
    out_path = out_path or OUT_PATH
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    os.replace(tmp, out_path)


def counterfactual(write: bool = True, matrix: str = "v1") -> dict:
    """Prereg s3.3 staged leg: 6 traders x {baseline, ORANGE/RED-masked}.

    Masking zeroes ENTRY rows on ORANGE/RED state days (states derive from
    <=t data only -- no lookahead); exit semantics stay the strategy's own
    (derived from the UNMASKED entry). 12 engine runs = real trials ->
    science_gates ledger +12. Measurement only: the batch verdict is already
    frozen by G1/G2 (FAIL); this leg never reverses it (prereg s8).

    matrix="v1" -> regime_calibration.json (batch regime_guard_calibration,
    r56 part3 done); matrix="v2" -> regime_calibration_v2.json (batch
    regime_guard_calibration_v2, prereg V2 ee8498e s3.5) -- v2 state series
    via raw_level_v2, mask = v2 ORANGE/RED days, plus YELLOW entry census
    (per-trader entries on v2-YELLOW days; the x0.5 sizing impact stays a
    census per prereg V2 s3.5 -- engine sizing sim deferred to GM stage,
    not implemented, honest note).
    """
    from firm.hr import TRADERS_DIR, load_trader
    try:
        from science_gates import append_ledger
    except ImportError:                       # imported-as-module fallback
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from science_gates import append_ledger
    from engine import run_backtest
    from live.paper import (OOS_START, SIGNAL_BUILDERS, ExitPatch,
                            _evidence_matches, build_panels, evidence_cutoff,
                            load_core, seg_metrics)

    # 1. deterministic re-derivation of the frozen state series (matrix-
    #    selected); hard abort if the bench has drifted since (counts must
    #    match the recorded run for THAT matrix).
    if matrix not in _LEVEL_FNS:
        raise ValueError(f"unknown matrix {matrix}")
    level_fn = _LEVEL_FNS[matrix]
    out_path = {"v1": OUT_PATH, "v2": OUT_PATH_V2,
                "v3": OUT_PATH_V3}[matrix]
    batch = (f"regime_guard_calibration"
             if matrix == "v1" else f"regime_guard_calibration_{matrix}")
    bench = build_bench()
    if matrix == "v3":
        bench = bench[bench.index <= pd.Timestamp(WINDOW_END_CAP)]
    raw = raw_series(bench, bench_dim_series(bench), breadth_series(bench),
                     level_fn=level_fn)
    states, _, _ = state_replay(bench, raw, resolver=_RESOLVERS[matrix])
    win = [d for d in bench.index if str(d.date()) >= WINDOW_START]
    counts = {}
    for d in win:
        counts[states[d]] = counts.get(states[d], 0) + 1
    with open(out_path, encoding="utf-8") as f:
        recorded = json.load(f)
    want = {k: counts.get(k, 0) for k in ("GREEN", "YELLOW", "ORANGE", "RED")}
    if want != {k: int(v) for k, v in recorded["state_counts"].items()}:
        raise AssertionError(f"state_counts drift vs recorded {matrix} run: "
                             f"{want} != {recorded['state_counts']}")
    mask_set = {d for d in win if states[d] in (ORANGE, RED)}
    yellow_set = {d for d in win if states[d] == YELLOW}

    tids = [t[:-5] for t in sorted(os.listdir(TRADERS_DIR))
            if t.endswith(".json") and not t.startswith("_")]
    if len(tids) != 6:
        raise AssertionError(f"roster size {len(tids)} != 6 (prereg s3.3)")
    prices_full = load_core()
    rows, mask_rows_n = [], None
    for tid in tids:
        t = load_trader(tid)
        cutoff = evidence_cutoff(t, prices_full)
        ps = pd.Timestamp(cutoff)
        prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
        P = build_panels(prices)
        entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
        exit_sig = (entry <= 0)              # strategy's own exit semantics
        params = {k: v for k, v in t["params"].items() if k != "entry"}
        mask_rows = entry.index[entry.index.isin(mask_set)]
        if mask_rows_n is None:
            mask_rows_n = len(mask_rows)
        entry_masked = entry.copy()
        for c in entry_masked.columns:       # dtype-faithful zeroing
            entry_masked.loc[mask_rows, c] = (False
                                               if entry_masked[c].dtype == bool
                                               else 0)
        with ExitPatch(t.get("exit_overrides")):
            base = run_backtest(prices, params, entry_signal=entry,
                                exit_signal=exit_sig)
            msk = run_backtest(prices, params, entry_signal=entry_masked,
                               exit_signal=exit_sig)
        # baseline MUST reproduce registration evidence (anchor law)
        eq = pd.Series(base["equity_curve"],
                       index=P["close"].index[:len(base["equity_curve"])])
        oos_tr = sum(1 for tr in base["trades"]
                     if str(tr["date"]) >= OOS_START)
        got_is = {**seg_metrics(eq[eq.index < pd.Timestamp(OOS_START)]),
                  "trades": base["metrics"]["num_trades"] - oos_tr}
        got_is2 = {**seg_metrics(eq, OOS_START), "trades": oos_tr}
        a_ok = (_evidence_matches(got_is, t["backtest"]["in_sample"])
                and _evidence_matches(got_is2, t["backtest"]["out_sample"]))
        blocked = int((entry.loc[mask_rows] > 0).sum().sum()) \
            if len(mask_rows) else 0
        total_e = int((entry > 0).sum().sum())
        # v2 prereg s3.5 disclosure: YELLOW entry census (x0.5 sizing
        # impact stays a census; engine sizing sim deferred to GM stage)
        y_rows = entry.index[entry.index.isin(yellow_set)]
        yellow_e = int((entry.loc[y_rows] > 0).sum().sum()) \
            if len(y_rows) else 0
        bm, mm = base["metrics"], msk["metrics"]
        rows.append({"tid": tid, "anchor_ok": bool(a_ok),
                     "blocked_entries": blocked, "total_entries": total_e,
                     "blocked_share": (round(blocked / total_e, 4)
                                       if total_e else None),
                     "yellow_entries": yellow_e,
                     "yellow_days_in_window": len(yellow_set),
                     "base_trades": bm["num_trades"],
                     "masked_trades": mm["num_trades"],
                     "d_trades": mm["num_trades"] - bm["num_trades"],
                     "base_sharpe": round(bm["sharpe"], 4),
                     "masked_sharpe": round(mm["sharpe"], 4),
                     "d_sharpe": round(mm["sharpe"] - bm["sharpe"], 4),
                     "base_annual": round(bm["annual_return"], 4),
                     "masked_annual": round(mm["annual_return"], 4),
                     "d_annual": round(mm["annual_return"]
                                       - bm["annual_return"], 4)})
    if not all(r["anchor_ok"] for r in rows):
        raise AssertionError("baseline anchor gate FAILED -- batch invalid")

    def rng(vals):
        return {"min": min(vals), "max": max(vals)}

    led = append_ledger(batch, 12,
                        note=f"prereg s3.3: 6 traders x {{baseline, "
                             f"ORANGE/RED entry-mask}} full-history legs "
                             f"(matrix={matrix})",
                        evidence_cutoff=EVIDENCE_CUTOFF)
    cf = {"n_runs": 12, "matrix": matrix,
          "mask_days_in_window": len(mask_set),
          "mask_days_on_panel": mask_rows_n,
          "rows": rows,
          "yellow_entry_census": (
              "per-row yellow_entries: entries falling on YELLOW state "
              f"days (matrix={matrix} prereg; x0.5 sizing impact = census "
              "only, engine sizing sim deferred to GM stage -- not "
              "implemented)")
          if matrix in ("v2", "v3") else None,
          "range": {"d_sharpe": rng([r["d_sharpe"] for r in rows]),
                    "d_annual": rng([r["d_annual"] for r in rows]),
                    "d_trades": rng([r["d_trades"] for r in rows]),
                    "blocked_share": rng([r["blocked_share"] for r in rows
                                          if r["blocked_share"] is not None])},
          "anchors_ok": True, "ledger": led,
          "note": "measurement only; verdict unchanged (G1/G2 FAIL frozen "
                  "by the replay leg, prereg s8 -- re-prereg is the only "
                  "enforce path)"}
    if write:
        recorded["counterfactual"] = cf
        # top-level trials_ledger = the ONLY key ledger_head() scans (chain
        # visibility); counterfactual.ledger is the provenance copy.
        recorded["trials_ledger"] = led
        _write(recorded, out_path)
    return cf


def _selftest() -> bool:
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [calib] {name}... {'PASS' if cond else 'FAIL'}")

    # A: synthetic bench -- engineered -14% 10d crash -> RED episode, FA path
    idx = pd.bdate_range("2020-01-01", periods=900)
    bench = pd.Series(4.0, index=idx)
    bench.iloc[500:510] = 4.0 * (1 - 0.14 * pd.Series(
        range(1, 11), index=idx[500:510]) / 10)
    fa = fa_metrics(bench, {d: (RED if 500 <= i < 510 else GREEN)
                            for i, d in enumerate(idx)})
    check("A RED crash episode recorded as orange-episodes=0",
          fa["orange"]["episodes"] == 0)

    # B: ORANGE episode + FA classification (further drop < 5% -> FA)
    states = {d: (ORANGE if i == 400 else GREEN) for i, d in enumerate(idx)}
    fa = fa_metrics(bench, states)
    check("B single-day ORANGE episode counted",
          fa["orange"]["episodes"] == 1 and
          fa["orange"]["main"] == 1 and fa["orange"]["fa_rate"] is not None)

    # C: truncated episode at history end excluded from main rate
    states = {d: (ORANGE if i == 899 else GREEN) for i, d in enumerate(idx)}
    fa = fa_metrics(bench, states)
    check("C end-of-history ORANGE episode truncated",
          fa["orange"]["truncated"] == 1 and fa["orange"]["main"] == 0)

    # D: pre-holiday derivation -- >=6d gap into October -> day before flagged
    d1 = pd.date_range("2025-09-22", "2025-09-30", freq="B")
    d2 = pd.date_range("2025-10-09", "2025-10-15", freq="B")
    idx2 = d1.append(d2)
    b2 = pd.Series(4.0, index=idx2)
    ds2 = bench_dim_series(b2)
    pre = ds2["event_pre_holiday"]
    gap_pos = list(idx2).index(pd.Timestamp("2025-09-30"))
    check("D Oct pre-holiday flagged on last day before gap",
          bool(pre.iloc[gap_pos]) and not bool(pre.iloc[0])
          and not bool(pre.iloc[-1]))

    # E: May labor-day gap (6d, month 5) -> NOT flagged (appendix A filter)
    e1 = pd.date_range("2025-04-28", "2025-04-30", freq="B")
    e2 = pd.date_range("2025-05-06", "2025-05-12", freq="B")
    idx3 = e1.append(e2)
    b3 = pd.Series(4.0, index=idx3)
    ds3 = bench_dim_series(b3)
    check("E non-CNY/National gaps never flagged",
          not bool(ds3["event_pre_holiday"].any()))

    # F: FOMC Beijing membership + replay-only disclosure
    check("F FOMC 2026 Beijing dates match live list length 2020-2026",
          len(FOMC_BEIJING) == 58)

    # G: resolve_state reuse -- replay init contract
    states, streaks, init_day = state_replay(
        b2, pd.DataFrame({"raw": [GREEN] * len(b2)}, index=b2.index))
    check("G state replay all-GREEN bench stays GREEN",
          all(s == GREEN for s in states.values()))

    # V2 mapping unit gates (prereg V2 s2, frozen @ ee8498e)
    bd_calm = {"crash_10d": -0.01, "panic_1d": -0.005, "vol20": 0.010,
               "vol_p95": 0.020, "vol_p80": 0.015, "vol_status": "ok",
               "below_ma200": True, "event_fomc": False,
               "event_pre_holiday": False}
    br_ok = {"share_below_ma20": 0.10, "share_slope_5d": -0.01,
             "status": "ok"}
    lvl_a, _ = raw_level_v2(bd_calm, br_ok, True)
    check("V2a bear calm -> YELLOW (v1-RED fixpoint)", lvl_a == YELLOW)
    lvl_f, _ = raw_level_v2(bd_calm, br_ok, False)
    check("V2f #10-only day -> GREEN (de-collected)", lvl_f == GREEN)
    lvl_b, _ = raw_level_v2(dict(bd_calm, crash_10d=-0.13), br_ok, False)
    check("V2b crash -13% -> RED", lvl_b == RED)
    lvl_c, _ = raw_level_v2(dict(bd_calm, panic_1d=-0.06), br_ok, False)
    check("V2c panic -6% -> RED", lvl_c == RED)
    lvl_d, _ = raw_level_v2(dict(bd_calm, vol20=0.025), br_ok, False)
    check("V2d vol>p95 -> ORANGE", lvl_d == ORANGE)
    lvl_e, _ = raw_level_v2(bd_calm,
                            {"share_below_ma20": 0.85,
                             "share_slope_5d": -0.02, "status": "ok"}, False)
    check("V2e breadth 85%+neg slope -> ORANGE", lvl_e == ORANGE)
    lvl_g, _ = raw_level_v2(dict(bd_calm, crash_10d=-0.09), br_ok, True)
    check("V2g bear+crash -9% -> ORANGE", lvl_g == ORANGE)
    lvl_h, _ = raw_level_v2(dict(bd_calm, event_fomc=True), br_ok, False)
    check("V2h event window -> YELLOW", lvl_h == YELLOW)

    # V3 unit gates (prereg V3 s3.3 (a)-(p), frozen @ a25f47a)
    s, k = resolve_state_v3(RED, 0, GREEN)
    check("V3a RED first green -> ORANGE partial release, streak=1",
          s == ORANGE and k == 1)
    s, k = resolve_state_v3(ORANGE, 1, GREEN)
    check("V3b second green after B-release -> GREEN", s == GREEN and k == 2)
    s, k = resolve_state_v3(ORANGE, 1, RED)
    check("V3c crisis resurgence after release -> RED, streak=0",
          s == RED and k == 0)
    s, k = resolve_state_v3(ORANGE, 0, GREEN)
    check("V3d true-orange holds on first green", s == ORANGE and k == 1)
    s2, k2 = resolve_state_v3(s, k, GREEN)
    check("V3d2 second green downgrades true-orange", s2 == GREEN and k2 == 2)
    s, k = resolve_state_v3(RED, 0, ORANGE)
    check("V3e RED holds on non-green raw, streak=0", s == RED and k == 0)
    lvl_f, _ = raw_level_v3(dict(bd_calm, crash_10d=-0.09), br_ok, False)
    check("V3f single-dim orange (crash -9%) -> YELLOW", lvl_f == YELLOW)
    lvl_g, _ = raw_level_v3(dict(bd_calm, crash_10d=-0.09, vol20=0.025),
                            br_ok, False)
    check("V3g crash -9% + vol>p95 -> ORANGE", lvl_g == ORANGE)
    lvl_h3, _ = raw_level_v3(dict(bd_calm, crash_10d=-0.09),
                            {"share_below_ma20": 0.85,
                             "share_slope_5d": -0.02, "status": "ok"}, False)
    check("V3h crash -9% + breadth collapse -> ORANGE", lvl_h3 == ORANGE)
    lvl_i, _ = raw_level_v3(dict(bd_calm, vol20=0.025), br_ok, False)
    check("V3i single-dim vol>p95 -> YELLOW", lvl_i == YELLOW)
    lvl_j, _ = raw_level_v3(bd_calm,
                            {"share_below_ma20": 0.85,
                             "share_slope_5d": -0.02, "status": "ok"}, False)
    check("V3j single-dim breadth collapse -> YELLOW", lvl_j == YELLOW)
    lvl_k, _ = raw_level_v3(dict(bd_calm, crash_10d=-0.13), br_ok, False)
    check("V3k crash -13% single-dim -> RED (no confirm)", lvl_k == RED)
    lvl_l, _ = raw_level_v3(dict(bd_calm, panic_1d=-0.06), br_ok, False)
    check("V3l panic -6% single-dim -> RED", lvl_l == RED)
    lvl_m, _ = raw_level_v3(bd_calm, br_ok, True)
    check("V3m bear calm -> YELLOW", lvl_m == YELLOW)
    lvl_n, _ = raw_level_v3(bd_calm, br_ok, False)   # below_ma200=True ignored
    check("V3n #10-only day -> GREEN (de-collected)", lvl_n == GREEN)
    lvl_o, _ = raw_level_v3(dict(bd_calm, event_fomc=True), br_ok, False)
    check("V3o event window -> YELLOW", lvl_o == YELLOW)
    s, k = resolve_state_v3(RED, 0, YELLOW)
    check("V3p RED holds on YELLOW-floor raw (known interaction)",
          s == RED and k == 0)
    return ok


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "selftest" in argv:
        ok = _selftest()
        print(f"  [calib] selftest {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    if "gates" in argv:
        bench = build_bench()
        g = equivalence_gates(bench, bench_dim_series(bench),
                              breadth_series(bench))
        print(json.dumps({"ok": g["ok"], "n_dates": g["n_sample_dates"],
                          "fails": [c for c in g["details"]
                                    if not c.get("match", True)]},
                         ensure_ascii=False, indent=1))
        return 0 if g["ok"] else 1
    if any(a.startswith("counterfactual") for a in argv):
        # NOTE: startswith prefix dispatch (prereg V3 s6 law, r58 overwrite
        # accident): the matrix is parsed from the matched token; an unknown
        # variant must NEVER fall through to the v1 default (its replay
        # rewrites regime_calibration.json and wipes recorded blocks).
        tok = next(a for a in argv if a.startswith("counterfactual"))
        matrix = ("v3" if tok == "counterfactual-v3"
                  else "v2" if tok == "counterfactual-v2"
                  else "v1" if tok == "counterfactual" else None)
        if matrix is None:
            print(f"unknown counterfactual variant: {tok}")
            return 2
        cf = counterfactual(matrix=matrix)
        print(json.dumps({"matrix": cf["matrix"],
                          "n_runs": cf["n_runs"],
                          "mask_days_window": cf["mask_days_in_window"],
                          "mask_days_panel": cf["mask_days_on_panel"],
                          "yellow_entries": {r["tid"]: r["yellow_entries"]
                                             for r in cf["rows"]},
                          "range": cf["range"],
                          "anchors_ok": cf["anchors_ok"],
                          "ledger_total": (cf.get("ledger") or {}).get("total"),
                          "rows": [{k: r[k] for k in
                                    ("tid", "blocked_entries",
                                     "blocked_share", "d_trades",
                                     "d_sharpe", "d_annual")}
                                   for r in cf["rows"]],
                          "out": {"v1": OUT_PATH, "v2": OUT_PATH_V2,
                                  "v3": OUT_PATH_V3}[matrix]},
                         ensure_ascii=False, indent=1))
        return 0
    tok = next((a for a in argv if a.startswith("replay-")), None)
    if tok == "replay-v2" or tok == "replay-v3":
        matrix = "v2" if tok == "replay-v2" else "v3"
        res = replay(write=True, matrix=matrix)
        print(json.dumps({"verdict": res["verdict"], "matrix": matrix,
                          "gates_ok": res["gates"]["ok"],
                          "window": res.get("window"),
                          "state_share": res.get("state_share"),
                          "gate_results": res.get("gate_results"),
                          "fa_orange": (res.get("false_alarm") or {})
                          .get("orange", {}).get("fa_rate"),
                          "fa_yellow": (res.get("false_alarm") or {})
                          .get("yellow", {}).get("fa_rate"),
                          "v2_disclosures": res.get("v2_disclosures"),
                          "v3_disclosures": res.get("v3_disclosures"),
                          "three_table_comparison":
                              res.get("three_table_comparison"),
                          "out": {"v2": OUT_PATH_V2,
                                  "v3": OUT_PATH_V3}[matrix]},
                         ensure_ascii=False, indent=1))
        return 0 if res["verdict"] == "PASS" else 1
    res = replay(write=True)
    print(json.dumps({"verdict": res["verdict"],
                      "gates_ok": res["gates"]["ok"],
                      "window": res.get("window"),
                      "state_share": res.get("state_share"),
                      "gate_results": res.get("gate_results"),
                      "fa_orange": (res.get("false_alarm") or {})
                      .get("orange", {}).get("fa_rate"),
                      "fa_yellow": (res.get("false_alarm") or {})
                      .get("yellow", {}).get("fa_rate"),
                      "out": OUT_PATH}, ensure_ascii=False, indent=1))
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
