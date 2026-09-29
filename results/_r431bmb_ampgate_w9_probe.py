# -*- coding: utf-8 -*-
"""_r431bmb_ampgate_w9_probe.py -- W9 AMP-gate raw-face probe (prereg sec.2 facts, NOT results).

W9 drafting berth upgrade per TRIAL_LABOR_W8_CANDIDATE_AMP_PREREG_DRAFT.md reuse
checklist face (4), adapted to post-W8 lineage: AMP axis is now stacked on the
W8-frozen twelve-tuple world (STREAK from W7 + TSTATE from W8), so the probe
crossing is SEVEN-gate 128-cell (gate x vol x yang x vconf x streak x tstate x
amp) instead of the checklist's pre-W8 six-gate 64-cell wording.

Definitions verbatim (zero-invention law):
  AMP face  (r417 probe, engine/factors.py::intraday_range registered formula):
      amp(d) = (high-low)/close; med20amp = rolling-20 median (min_periods=20,
      incl d); amp_wide = amp > med20amp; amp_narrow = <= ; 19-bar warmup.
  STREAK face (W7-frozen, r206 probe lineage):
      up_streak2 / down_streak2 / neither; 2-bar warmup.
  TSTATE face (census-verbatim, toolstack gate_census O-1855(4)):
      deep_pullback (MAD60_q10): dist = close/MA60-1 < rolling252 q10
      oversold_rsv (RSV60_low<0.2): rsv < 0.2 (hh==ll -> NaN)
  GATE/VOL/YANG/VCONF faces (W3/W4/W5/W6 frozen): MA200 / vol20-vs-med500 /
      close>open / volume-vs-med20.

New crossing faces (open readings, no priors): AMP x STREAK and AMP x TSTATE
rates both directions + 4-cell counts; extreme-day seven-dimensional states;
core48 member-level AMP wide-rate spread. Deterministic, zero network,
read-only. Determinism cross-checks against frozen r417 (AMP) and r423
(STREAK/TSTATE) probe fact files -- reproduced anchors must match exactly.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join("scripts"))
import trial_labor_w1 as tl1  # import-face reuse law (loader T-22/T-34 lineage)

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4-W8 probes
OUT = "results/_r431bmb_ampgate_w9_probe_facts.json"
R417_FACTS = "results/_r417bmb_ampgate_probe_facts.json"
R423_FACTS = "results/_r423bmb_w8tstate_probe_facts.json"

EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]


def amp_faces(df):
    """(high-low)/close + rolling-20 median (min_periods=20, incl d);
    wide=1/narrow=0.  Registered formula engine/factors.py::intraday_range."""
    amp = (df["high"] - df["low"]) / df["close"]
    med = amp.rolling(20, min_periods=20).median()
    wide = (amp > med).astype("float")  # NaN window stays NaN
    wide[med.isna()] = float("nan")
    return amp, med, wide


def streak_faces(df):
    """up/down 2-day close-over-close run; -1=neither; NaN only first 2 bars.
    W7-frozen definition verbatim (r206 probe lineage, warmup bar-idx==2)."""
    up1 = df["close"] > df["close"].shift(1)
    up2 = df["close"].shift(1) > df["close"].shift(2)
    dn1 = df["close"] < df["close"].shift(1)
    dn2 = df["close"].shift(1) < df["close"].shift(2)
    state = pd.Series(float("nan"), index=df.index)
    judge = (df["close"].shift(2)).notna()  # bars 0-1 = warmup gate-closed
    state[judge & (up1 & up2).fillna(False)] = 1.0
    state[judge & (dn1 & dn2).fillna(False)] = 0.0
    state[judge & ~((up1 & up2).fillna(False) | (dn1 & dn2).fillna(False))] = -1.0
    return state


def tstate_faces(df):
    """census-verbatim TSTATE gates; returns (mad60_q10, rsv60_low, decidable, rsv60)."""
    c, h, l = df["close"], df["high"], df["low"]
    ma60 = c.rolling(60).mean()
    dist = c / ma60 - 1.0
    q10_ref = dist.rolling(252, min_periods=120).quantile(0.10)
    mad_q10 = dist < q10_ref

    hh60, ll60 = h.rolling(60).max(), l.rolling(60).min()
    rng60 = (hh60 - ll60).replace(0, np.nan)
    rsv60 = (c - ll60) / rng60
    rsv_low = rsv60 < 0.2

    decidable = {"deep_pullback_mad60_q10": q10_ref.notna(),
                 "oversold_rsv60_low02": rsv60.notna()}
    return mad_q10, rsv_low, decidable, rsv60


def main() -> int:
    df = pd.read_csv(os.path.join("data", "daily", "sh510300.csv"))
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)
    n = len(df)
    assert n == 3483, f"row count {n} != 3483 (W4-W8 probe anchor)"
    assert df["date"].iloc[-1] == CUTOFF, "last row != cutoff"
    zero_amp = int((df["high"] == df["low"]).sum())  # flat-line day (halt face)
    assert zero_amp == 0, "zero-range rows != 0 (r417 anchor)"

    c, h, l, v, o = (df[k] for k in ("close", "high", "low", "volume", "open"))

    # ---- AMP face (r417 verbatim) ------------------------------------------
    amp, med20amp, wide = amp_faces(df)
    amp_known = wide.notna()
    warmup_amp = int(wide.isna().sum())  # == 19 anchor
    assert int(amp_known.sum()) + warmup_amp == n

    # ---- STREAK face (W7-frozen verbatim) ------------------------------------
    st = streak_faces(df)
    up_st, dn_st, neither = st == 1.0, st == 0.0, st == -1.0
    assert int(st.isna().sum()) == 2

    # ---- TSTATE faces (census-verbatim) --------------------------------------
    mad_q10, rsv_low, decidable, rsv60 = tstate_faces(df)

    # ---- W3-W6 gate faces -----------------------------------------------------
    ma200 = c.rolling(200, min_periods=200).mean()
    bull, bear = c > ma200, c <= ma200
    ret = c.pct_change()
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    calm, wild = vol20 <= med500, vol20 > med500
    med20v = v.rolling(20, min_periods=20).median()
    surge = v > med20v
    yang = c > o

    facts = {"cutoff": CUTOFF, "rows": int(n), "first_date": str(df["date"].iloc[0]),
             "last_date": str(df["date"].iloc[-1]), "zero_range_rows": zero_amp,
             "amp_warmup_gate_closed_bars": warmup_amp,
             "amp_decidable_days": int(amp_known.sum()),
             "wide_days": int((wide[amp_known] == 1).sum()),
             "narrow_days": int((wide[amp_known] == 0).sum()),
             "wide_rate_on_decidable": round(float(wide[amp_known].mean()), 4),
             "probe_lineage": "r417 AMP face + r423 STREAK/TSTATE faces merged (W9 berth upgrade, seven-gate crossing)"}

    # ---- determinism cross-check vs r417 / r423 frozen fact files -------------
    xchecks = {}
    if os.path.exists(R417_FACTS):
        f17 = json.load(open(R417_FACTS, encoding="utf-8"))
        xchecks["r417"] = {
            "wide_total_match": f17["wide_total"] == facts["wide_days"],
            "warmup_match": f17["warmup_gate_closed_bars"] == warmup_amp,
            "zero_range_match": f17["zero_range_rows"] == zero_amp}
    if os.path.exists(R423_FACTS):
        f23 = json.load(open(R423_FACTS, encoding="utf-8"))
        xchecks["r423"] = {
            "streak_up_match": f23["streak_face"]["up_streak2_days"] == int(up_st.sum()),
            "streak_down_match": f23["streak_face"]["down_streak2_days"] == int(dn_st.sum()),
            "streak_neither_match": f23["streak_face"]["neither_days"] == int(neither.sum()),
            "mad60_open_match": f23["deep_pullback_mad60_q10"]["gate_true_days"] == int(mad_q10.sum()),
            "rsv60_open_match": f23["oversold_rsv60_low02"]["gate_true_days"] == int(rsv_low.sum())}
    facts["determinism_cross_checks"] = xchecks

    # ---- AMP inside GATE/VOL/YANG/VCONF (r417 faces re-verified) --------------
    def rate(mask_in, gate, dec):
        both = int((mask_in & gate).sum())
        base = int((mask_in & dec).sum())
        return round(100.0 * both / base, 2) if base else float("nan")

    facts["wide_rate_inside_pct"] = {
        "bull": rate(bull, wide == 1, amp_known), "bear": rate(bear, wide == 1, amp_known),
        "calm": rate(calm, wide == 1, amp_known), "wild": rate(wild, wide == 1, amp_known),
        "yang": rate(yang, wide == 1, amp_known), "red": rate(~yang, wide == 1, amp_known),
        "surge": rate(surge, wide == 1, amp_known), "dry": rate(~surge, wide == 1, amp_known),
    }

    # ---- NEW: AMP x STREAK crossing (open reading, no prior) -------------------
    facts["amp_streak_cross"] = {
        "wide_rate_inside_streak_pct": {
            "up_streak2": rate(up_st, wide == 1, amp_known),
            "down_streak2": rate(dn_st, wide == 1, amp_known),
            "neither": rate(neither, wide == 1, amp_known)},
        "streak_rate_inside_wide_pct": {
            "up_pct": rate(wide == 1, up_st, st.notna()),
            "down_pct": rate(wide == 1, dn_st, st.notna()),
            "neither_pct": rate(wide == 1, neither, st.notna())},
        "streak_rate_inside_narrow_pct": {
            "up_pct": rate(wide == 0, up_st, st.notna()),
            "down_pct": rate(wide == 0, dn_st, st.notna()),
            "neither_pct": rate(wide == 0, neither, st.notna())},
        "cross_cells": {
            "up_and_wide": int((up_st & (wide == 1)).sum()),
            "up_and_narrow": int((up_st & (wide == 0)).sum()),
            "down_and_wide": int((dn_st & (wide == 1)).sum()),
            "down_and_narrow": int((dn_st & (wide == 0)).sum())}}

    # ---- NEW: AMP x TSTATE crossing (open reading, no prior) ------------------
    dec_mad = decidable["deep_pullback_mad60_q10"]
    dec_rsv = decidable["oversold_rsv60_low02"]
    facts["amp_tstate_cross"] = {
        "wide_rate_inside_tstate_pct": {
            "mad60_q10_open": rate(mad_q10, wide == 1, amp_known),
            "rsv60_low_open": rate(rsv_low, wide == 1, amp_known),
            "mad60_q10_closed": rate(~mad_q10, wide == 1, amp_known),
            "rsv60_low_closed": rate(~rsv_low, wide == 1, amp_known)},
        "tstate_rate_inside_wide_pct": {
            "mad60_pct": rate(wide == 1, mad_q10, dec_mad),
            "rsv60_pct": rate(wide == 1, rsv_low, dec_rsv)},
        "tstate_rate_inside_narrow_pct": {
            "mad60_pct": rate(wide == 0, mad_q10, dec_mad),
            "rsv60_pct": rate(wide == 0, rsv_low, dec_rsv)},
        "cross_cells": {
            "mad60_and_wide": int((mad_q10 & (wide == 1)).sum()),
            "mad60_and_narrow": int((mad_q10 & (wide == 0)).sum()),
            "rsv60_and_wide": int((rsv_low & (wide == 1)).sum()),
            "rsv60_and_narrow": int((rsv_low & (wide == 0)).sum())}}

    # ---- r417 heritage: 4-face crossings re-verified ---------------------------
    for gname, g in (("bull", bull), ("bear", bear)):
        for w in (1, 0):
            facts.setdefault("cross_gate", {})[f"{'wide' if w else 'narrow'}_and_{gname}"] = int((g & (wide == w) & amp_known).sum())
    for vname, vv in (("calm", calm), ("wild", wild)):
        for w in (1, 0):
            facts.setdefault("cross_vol", {})[f"{'wide' if w else 'narrow'}_and_{vname}"] = int((vv & (wide == w) & amp_known).sum())
    for yname, y in (("yang", yang), ("red", ~yang)):
        for w in (1, 0):
            facts.setdefault("cross_yang", {})[f"{yname}_and_{'wide' if w else 'narrow'}"] = int((y & (wide == w) & amp_known).sum())
    for sname, s in (("surge", surge), ("dry", ~surge)):
        for w in (1, 0):
            facts.setdefault("cross_vconf", {})[f"{sname}_and_{'wide' if w else 'narrow'}"] = int((s & (wide == w) & amp_known).sum())

    # ---- SEVEN-gate 128-cell crossing (gate x vol x yang x vconf x streak x tstate x amp)
    cells = {}
    n_empty = 0
    m7 = bull.notna() & calm.notna() & amp_known & st.notna() & dec_mad  # all-decidable window
    for bname, b in (("bull", bull), ("bear", bear)):
        for vname, vv in (("calm", calm), ("wild", wild)):
            for yname, y in (("yang", yang), ("red", ~yang)):
                for sname, s in (("surge", surge), ("dry", ~surge)):
                    for kname, k in (("up_streak", up_st), ("down_streak", dn_st)):
                        for tname, t in (("mad60", mad_q10), ("rsv60", rsv_low)):
                            for aname, a in (("wide", wide == 1), ("narrow", wide == 0)):
                                cnt = int((m7 & b & vv & y & s & k & t & a).sum())
                                cells["%s|%s|%s|%s|%s|%s|%s" % (bname, vname, yname, sname, kname, tname, aname)] = cnt
                                if cnt == 0:
                                    n_empty += 1
    facts["seven_gate_128_cells"] = cells
    facts["seven_gate_128_cells_empty_count"] = n_empty
    facts["seven_gate_128_cells_nonzero_count"] = 128 - n_empty
    facts["seven_gate_128_cells_min_nonzero"] = min([x for x in cells.values() if x > 0] or [0])
    facts["seven_gate_128_cells_max"] = max(cells.values())
    facts["seven_gate_all_decidable_days"] = int(m7.sum())

    # ---- extreme days: seven-dimensional state readout --------------------------
    est = {}
    for dstr in EXTREME_DAYS:
        idx = df.index[df["date"] == dstr]
        if len(idx) == 0:
            est[dstr] = "not-in-panel"
            continue
        i = int(idx[0])
        stv = None if pd.isna(st.iloc[i]) else ("up_streak2" if st.iloc[i] == 1.0 else ("down_streak2" if st.iloc[i] == 0.0 else "neither"))
        m = med20amp.iloc[i]
        est[dstr] = {"streak": stv,
                     "tstate_mad60_q10": bool(mad_q10.iloc[i]),
                     "tstate_rsv60_low": bool(rsv_low.iloc[i]),
                     "rsv60_value": (None if pd.isna(rsv60.iloc[i]) else round(float(rsv60.iloc[i]), 4)),
                     "amp_state": ("wide" if (amp.iloc[i] > m) else "narrow"),
                     "amp_over_med20": round(float(amp.iloc[i] / m), 3)}
    facts["extreme_day_states"] = est

    # ---- core48 member-level AMP wide-rate spread (real roster, import-reuse) --
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    rates = {}
    for sym, d2 in sorted(prices.items()):
        d2 = d2[d2.index <= cut]
        if len(d2) >= 60:
            _, _, w2 = amp_faces(d2)
            k2 = w2.notna()
            if k2.any():
                rates[str(sym)] = round(float(w2[k2].mean()), 4)
    vals = sorted(rates.values())
    facts["core48_wide_rate"] = {
        "n": len(vals),
        "min": round(vals[0], 4), "median": round(vals[len(vals) // 2], 4),
        "max": round(vals[-1], 4),
        "method": "tl1.load_core() roster (import-reuse, real core48 face)",
        "members_with_lt60_rows_excluded": len(prices) - len(vals)}

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in facts.items() if not isinstance(v, dict)}, ensure_ascii=False))
    print("seven_gate_128_cells: empty", facts["seven_gate_128_cells_empty_count"],
          "| nonzero", facts["seven_gate_128_cells_nonzero_count"],
          "| min-nonzero", facts["seven_gate_128_cells_min_nonzero"],
          "| max", facts["seven_gate_128_cells_max"],
          "| all-decidable days", facts["seven_gate_all_decidable_days"])
    print("amp_streak_cross:", json.dumps(facts["amp_streak_cross"]["cross_cells"]))
    print("amp_tstate_cross:", json.dumps(facts["amp_tstate_cross"]["cross_cells"]))
    print("determinism_cross_checks:", json.dumps(facts["determinism_cross_checks"]))
    print("W9 AMP probe facts ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
