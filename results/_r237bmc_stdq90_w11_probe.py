# -*- coding: utf-8 -*-
"""_r237bmc_stdq90_w11_probe.py -- W11 pre-selection probe: A158-TSGATE-P1
48-PASS pool top family STD20_q90 / STD10_q90 (high price-dispersion side,
GATE-RECHECK-confirmed #17/#18 singleton clusters) raw-face facts on the
510300 anchor. NOT results, NOT a strategy claim.

W11 supply-prep slice per TRIAL_LABOR_LAW sec.1 standing-supply step
(r237 bm-c). Pre-commitment window note (research/DECISION_CHAIN.md sec.4.7
v1.2: next-wave hypotheses must be frozen BEFORE the previous wave verdict
lands; W10-JUDGE is in-flight on the bm-b lane right now = the berth window
is open; W10 itself was berthed pre-W9-verdict per the same cadence).

The deferral question this probe answers (r234 digest sec.3 pool turn):
  does the STD20_q90 gate open a DISTINCT day-level conditional space from
  the already-burned trial-grammar axes -- W4 VOL (calm/wild return-vol
  median split), W9 AMP (wide/narrow intraday range), W8 TSTATE
  (mad60/rsv60), W10 MOM (roc20_oversold) -- or is it a collapsed neighbor
  like VSTD20_q20 was (98.5% inside W4 calm, r234 DEMOTE)?

Key structural disclosure (construction honesty, zero invention):
  A158 STD20 (frozen runner scripts/a158_tsgate_probe.py L240):
      F["STD%d"] = c.rolling(d, min_periods=1).std() / c   [pandas ddof=1]
  = price-LEVEL std over d closes normalized by close -> includes DRIFT
  (a steady grind trend has high STD even with tiny daily returns).
  W4 vol20 = std of daily returns (ddof=1) -> noise face, drift-free.
  These two diverge exactly in trending-low-noise regimes; that divergence
  IS the candidate increment face (std_high while calm).
  Gate (A158_TSGATE_P1 prereg sec.2 frozen): high side
      f > f.rolling(252, min_periods=120).quantile(0.90)
  decidable = f.notna() & qref.notna() (pit-95/r431 NaN-bucket artifact law).
  Warmup: f[idx 0] = NaN (single-obs std ddof=1) -> f valid from bar-idx 1 ->
  qref first valid at bar-idx 120 (0-based; 120 valid f values needed).
  Honest disclosure: differs from the MOM/ROC20_q10 anchor (first decidable
  139) because STD needs no 20-bar shift.

Seven inherited gate faces (W3-W10 frozen, r228/r431/r234 probe lineage
verbatim): GATE (MA200 bull/bear) / VOL (vol20-vs-med500 calm/wild) /
YANG (close>open) / VCONF (volume-vs-med20 surge/dry) / STREAK (W7
up/down_streak2) / TSTATE (W8 MAD60_q10 + RSV60<0.2) / AMP (W9
intraday_range wide/narrow). MOM (W10 roc20_q10) carried for adjacency only.

GATE-RECHECK face_a cross-reference (results/gate_recheck_a158.json, bm-a
17:49): STD20_q90 510300 n_in=247 / n_out=2094 (five-member secondary face,
different member-panel loading); disclosed as reference, NOT fail-closed.

Deterministic, zero network, read-only.
"""
import json
import os
import sys

# GBK-console print guard (r236 pit law; idempotent, harmless)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join("scripts"))
import trial_labor_w1 as tl1  # import-face reuse law (loader T-22/T-34 lineage)

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4-W10 probes
OUT = "results/_r237bmc_stdq90_w11_probe_facts.json"
R417_FACTS = "results/_r417bmb_ampgate_probe_facts.json"
R423_FACTS = "results/_r423bmb_w8tstate_probe_facts.json"
R431_FACTS = "results/_r431bmb_ampgate_w9_probe_facts.json"
R228_FACTS = "results/_r228bmc_momgate_w10_probe_facts.json"
R234_FACTS = "results/_r234bmc_vstd20_w11_probe_facts.json"
GATE_RECHECK = "results/gate_recheck_a158.json"

EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]


def std_faces(df, win):
    """A158 frozen STD gate (construction verbatim from
    scripts/a158_tsgate_probe.py L240 + prereg sec.2 high-quantile gate).
    Returns (f, qref, open, decidable)."""
    c = df["close"]
    f = c.rolling(win, min_periods=1).std(ddof=1) / c
    qref = f.rolling(252, min_periods=120).quantile(0.90)
    gate_open = f > qref  # NaN comparison -> False; decidable below
    decidable = qref.notna() & f.notna()
    return f, qref, gate_open, decidable


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


def mom_faces(df):
    """W10-frozen MOM face (r228 probe verbatim): roc20_q10 oversold gate."""
    c = df["close"]
    roc20 = c / c.shift(20) - 1.0
    q10_ref = roc20.rolling(252, min_periods=120).quantile(0.10)
    gate_open = roc20 < q10_ref
    decidable = q10_ref.notna() & roc20.notna()
    return roc20, q10_ref, gate_open, decidable


def tstats(a, b):
    """Welch t-stat for two independent samples (descriptive face only)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float("nan")
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = (va / na + vb / nb) ** 0.5
    if se == 0:
        return float("nan")
    return round(float((a.mean() - b.mean()) / se), 3)


def main() -> int:
    df = pd.read_csv(os.path.join("data", "daily", "sh510300.csv"))
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)
    n = len(df)
    assert n == 3483, f"row count {n} != 3483 (W4-W10 probe anchor)"
    assert df["date"].iloc[-1] == CUTOFF, "last row != cutoff"
    zero_amp = int((df["high"] == df["low"]).sum())  # flat-line day (halt face)
    assert zero_amp == 0, "zero-range rows != 0 (r417 anchor)"

    c, h, l, v, o = (df[k] for k in ("close", "high", "low", "volume", "open"))

    # ---- STD faces (this probe's new faces, A158 frozen construction) --------
    std20, q90_20, std20_open, dec_s20 = std_faces(df, 20)
    std10, q90_10, std10_open, dec_s10 = std_faces(df, 10)
    for tag, dec in (("std20", dec_s20), ("std10", dec_s10)):
        first_decidable_idx = int(np.argmax(dec.to_numpy()))
        # f[idx 0] = NaN (single-obs std ddof=1) -> f first valid idx 1 ->
        # qref window needs 120 valid f values -> first decidable idx 120.
        assert first_decidable_idx == 120, f"{tag} first decidable {first_decidable_idx} != 120"
    assert int(dec_s20.sum()) + (n - int(dec_s20.sum())) == n

    # ---- inherited faces (W3-W10 verbatim) ------------------------------------
    amp, med20amp, wide = amp_faces(df)
    amp_known = wide.notna()
    st = streak_faces(df)
    up_st, dn_st, neither = st == 1.0, st == 0.0, st == -1.0
    mad_q10, rsv_low, decidable, rsv60 = tstate_faces(df)
    dec_mad = decidable["deep_pullback_mad60_q10"]
    dec_rsv = decidable["oversold_rsv60_low02"]
    roc20, q10mom, mom_open, dec_mom = mom_faces(df)

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
             "probe_lineage": "r431 seven-gate lineage + r228 MOM + r234 VSTD probe pattern + A158-TSGATE-P1 frozen STD construction (STD20_q90/STD10_q90 face, W11 pre-selection)",
             "construction_disclosure": "A158 STD20=c.rolling(20,min_periods=1).std(ddof=1)/c (price-LEVEL std incl. drift) vs W4 vol20=return std (noise, drift-free); divergence face = trending-low-noise regimes = the candidate increment",
             "warmup_disclosure": "STD first-decidable bar-idx 120 (f[idx0]=NaN single-obs ddof=1 std -> f valid from idx 1; qref 252/min120 needs 120 valid f values) vs MOM anchor 139 (roc20 shift-20) -- different by construction, asserted deterministic"}

    for tag, f_, dec, op in (("std20", std20, dec_s20, std20_open),
                             ("std10", std10, dec_s10, std10_open)):
        facts[f"{tag}_decidable_days"] = int(dec.sum())
        facts[f"{tag}_open_days"] = int((op & dec).sum())
        facts[f"{tag}_open_rate_on_decidable"] = round(float((op & dec).mean()), 4)

    # ---- determinism cross-check vs frozen probe facts ------------------------
    xchecks = {}
    if os.path.exists(R431_FACTS):
        f31 = json.load(open(R431_FACTS, encoding="utf-8"))
        xchecks["r431"] = {
            "wide_days_match": f31["wide_days"] == int((wide[amp_known] == 1).sum()),
            "mad60_open_match": f31["amp_tstate_cross"]["cross_cells"]["mad60_and_wide"] + f31["amp_tstate_cross"]["cross_cells"]["mad60_and_narrow"] == int(mad_q10.sum()),
            "rsv60_open_match": f31["amp_tstate_cross"]["cross_cells"]["rsv60_and_wide"] + f31["amp_tstate_cross"]["cross_cells"]["rsv60_and_narrow"] == int(rsv_low.sum())}
    if os.path.exists(R417_FACTS):
        f17 = json.load(open(R417_FACTS, encoding="utf-8"))
        xchecks["r417"] = {"wide_total_match": f17["wide_total"] == int((wide[amp_known] == 1).sum())}
    if os.path.exists(R423_FACTS):
        f23 = json.load(open(R423_FACTS, encoding="utf-8"))
        xchecks["r423"] = {
            "streak_up_match": f23["streak_face"]["up_streak2_days"] == int(up_st.sum()),
            "streak_down_match": f23["streak_face"]["down_streak2_days"] == int(dn_st.sum()),
            "streak_neither_match": f23["streak_face"]["neither_days"] == int(neither.sum())}
    if os.path.exists(R228_FACTS):
        f28 = json.load(open(R228_FACTS, encoding="utf-8"))
        xchecks["r228"] = {"rows_match": f28["rows"] == int(n),
                           "mom_decidable_match": f28["mom_decidable_days"] == int(dec_mom.sum()),
                           "mom_open_match": f28.get("mom_open_days") == int((mom_open & dec_mom).sum())}
    if os.path.exists(R234_FACTS):
        f34 = json.load(open(R234_FACTS, encoding="utf-8"))
        xchecks["r234"] = {"rows_match": f34["rows"] == int(n),
                            "calm_wild_lineage": f34["rows"] == int(n)}
    if os.path.exists(GATE_RECHECK):
        gr = json.load(open(GATE_RECHECK, encoding="utf-8"))
        try:
            ref = gr["gates"]["STD20_q90"]["face_a"]["members"]["510300"]
            xchecks["gate_recheck_ref"] = {"std20_q90_510300_n_in_ref": ref["n_in"],
                                            "n_out_ref": ref["n_out"],
                                            "note": "five-member secondary face different member-panel loading; disclosure reference NOT fail-closed"}
        except Exception as e:
            xchecks["gate_recheck_ref"] = {"error": str(e)}
    facts["determinism_cross_checks"] = xchecks

    # ---- STD20_q90 open-rate inside each inherited gate (honest decidable rates)
    def rate(mask_in, gate, dec):
        both = int((mask_in & gate).sum())
        base = int((mask_in & dec).sum())
        return round(100.0 * both / base, 2) if base else float("nan")

    facts["std20_open_rate_inside_pct"] = {
        "bull": rate(bull, std20_open, dec_s20), "bear": rate(bear, std20_open, dec_s20),
        "calm": rate(calm, std20_open, dec_s20), "wild": rate(wild, std20_open, dec_s20),
        "yang": rate(yang, std20_open, dec_s20), "red": rate(~yang, std20_open, dec_s20),
        "surge": rate(surge, std20_open, dec_s20), "dry": rate(~surge, std20_open, dec_s20),
        "up_streak2": rate(up_st, std20_open, dec_s20), "down_streak2": rate(dn_st, std20_open, dec_s20),
        "neither_streak": rate(neither, std20_open, dec_s20),
        "mad60_q10_open": rate(mad_q10, std20_open, dec_s20), "mad60_q10_closed": rate(~mad_q10 & dec_mad, std20_open, dec_s20),
        "rsv60_low_open": rate(rsv_low, std20_open, dec_s20), "rsv60_low_closed": rate(~rsv_low & dec_rsv, std20_open, dec_s20),
        "amp_wide": rate(wide == 1, std20_open, dec_s20), "amp_narrow": rate(wide == 0, std20_open, dec_s20),
        "mom_open": rate(mom_open & dec_mom, std20_open, dec_s20 & dec_mom), "mom_closed": rate((~mom_open & dec_mom), std20_open, dec_s20 & dec_mom)}

    # ---- reverse: neighbor-gate rates inside STD-open vs STD-closed ------------
    facts["reverse_rates_inside_std20_pct"] = {
        "wild_rate_when_std20_open": rate(std20_open, wild, dec_s20 & med500.notna()),
        "wild_rate_when_std20_closed": rate((~std20_open & dec_s20), wild, dec_s20 & med500.notna()),
        "wide_rate_when_std20_open": rate(std20_open, wide == 1, dec_s20 & amp_known),
        "wide_rate_when_std20_closed": rate((~std20_open & dec_s20), wide == 1, dec_s20 & amp_known),
        "yang_rate_when_std20_open": rate(std20_open, yang, dec_s20),
        "yang_rate_when_std20_closed": rate((~std20_open & dec_s20), yang, dec_s20),
        "mad60_rate_when_std20_open": rate(std20_open & dec_mad, mad_q10, dec_s20 & dec_mad),
        "rsv60_rate_when_std20_open": rate(std20_open & dec_rsv, rsv_low, dec_s20 & dec_rsv)}

    # ---- neighbor adjacency cross cells (THE deferral question) ----------------
    def cell(a, da, b, db):
        m = da & db
        both_open = int((a & b & m).sum())
        a_open = int((a & m).sum())
        b_open = int((b & m).sum())
        union = int(((a | b) & m).sum())
        return {"both_open": both_open, "a_open": a_open, "b_open": b_open,
                "a_open_pct_of_b_open": round(100.0 * both_open / b_open, 2) if b_open else float("nan"),
                "b_open_pct_of_a_open": round(100.0 * both_open / a_open, 2) if a_open else float("nan"),
                "a_only_days": a_open - both_open, "union_days": union, "joint_decidable_days": int(m.sum())}

    facts["adjacency"] = {
        "std20_vs_wild": cell(std20_open, dec_s20, wild, med500.notna()),
        "std20_vs_calm": cell(std20_open, dec_s20, calm, med500.notna()),
        "std20_vs_wide": cell(std20_open, dec_s20, wide == 1, amp_known),
        "std20_vs_narrow": cell(std20_open, dec_s20, wide == 0, amp_known),
        "std20_vs_mad60": cell(std20_open, dec_s20, mad_q10, dec_mad),
        "std20_vs_rsv60": cell(std20_open, dec_s20, rsv_low, dec_rsv),
        "std20_vs_downstreak": cell(std20_open, dec_s20, dn_st, st.notna()),
        "std20_vs_upstreak": cell(std20_open, dec_s20, up_st, st.notna()),
        "std20_vs_mom": cell(std20_open, dec_s20, mom_open, dec_mom),
        "std10_vs_std20": cell(std10_open, dec_s10, std20_open, dec_s20)}

    # distinct-space increment faces (r228 MOM "121 mom-only days" pattern)
    dec_calm = dec_s20 & med500.notna()
    dec_nar = dec_s20 & amp_known
    facts["distinct_space_increment"] = {
        "std20_open_and_calm_days": int((std20_open & calm & dec_calm).sum()),
        "std20_open_and_wild_days": int((std20_open & wild & dec_calm).sum()),
        "std20_open_and_narrow_days": int((std20_open & (wide == 0) & dec_nar).sum()),
        "std20_open_and_yang_days": int((std20_open & yang & dec_s20).sum()),
        "std20_open_and_red_days": int((std20_open & (~yang) & dec_s20).sum()),
        "std20_open_and_mom_open_days": int((std20_open & mom_open & (dec_s20 & dec_mom)).sum()),
        "note": "std_open while burned neighbor faces read the opposite state = conditional-space increment; std_open∧calm = drift-dominated high-dispersion face (the construction divergence); near-zero counts = collapsed neighbor"}

    # ---- EIGHT-gate 256-cell crossing (STD20_q90 as the 8th face) ------------
    cells = {}
    n_empty = 0
    m8 = dec_s20 & bull.notna() & calm.notna() & amp_known & st.notna() & dec_mad & dec_rsv
    for bname, b in (("bull", bull), ("bear", bear)):
        for vname, vv in (("calm", calm), ("wild", wild)):
            for yname, y in (("yang", yang), ("red", ~yang)):
                for sname, s in (("surge", surge), ("dry", ~surge)):
                    for kname, k in (("up_streak", up_st), ("down_streak", dn_st)):
                        for tname, t in (("mad60", mad_q10), ("rsv60", rsv_low)):
                            for aname, a in (("wide", wide == 1), ("narrow", wide == 0)):
                                for mname, mm in (("std20_open", std20_open), ("std20_closed", ~std20_open & dec_s20)):
                                    cnt = int((m8 & b & vv & y & s & k & t & a & mm).sum())
                                    cells["%s|%s|%s|%s|%s|%s|%s|%s" % (bname, vname, yname, sname, kname, tname, aname, mname)] = cnt
                                    if cnt == 0:
                                        n_empty += 1
    facts["eight_gate_256_cells_empty_count"] = n_empty
    facts["eight_gate_256_cells_nonzero_count"] = 256 - n_empty
    facts["eight_gate_256_cells_min_nonzero"] = min([x for x in cells.values() if x > 0] or [0])
    facts["eight_gate_256_cells_max"] = max(cells.values())
    facts["eight_gate_all_decidable_days"] = int(m8.sum())
    facts["eight_gate_cells"] = cells

    # ---- extreme days: state readout -------------------------------------------
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
                     "std20_open": bool(std20_open.iloc[i]) if dec_s20.iloc[i] else None,
                     "std10_open": bool(std10_open.iloc[i]) if dec_s10.iloc[i] else None,
                     "std20_value": (None if pd.isna(std20.iloc[i]) else round(float(std20.iloc[i]), 6)),
                     "std20_over_q90ref": (None if pd.isna(std20.iloc[i]) or pd.isna(q90_20.iloc[i]) else round(float(std20.iloc[i] / q90_20.iloc[i]), 3))}
    facts["extreme_day_states"] = est

    # ---- census-style forward differential (descriptive face, NOT a claim) -----
    for fw in (5, 20):
        fwd = c.shift(-fw) / c - 1.0
        base = dec_s20 & fwd.notna()  # forward window inside panel
        a = fwd[std20_open & base]
        b = fwd[(~std20_open & dec_s20) & base]
        facts[f"forward_{fw}d"] = {
            "n_open": int(len(a)), "n_closed": int(len(b)),
            "mean_fwd_open": round(float(a.mean()), 6) if len(a) else float("nan"),
            "mean_fwd_closed": round(float(b.mean()), 6) if len(b) else float("nan"),
            "diff_open_minus_closed": round(float(a.mean() - b.mean()), 6) if (len(a) and len(b)) else float("nan"),
            "welch_t": tstats(a, b),
            "note": "descriptive probe face on 510300 anchor only; census/recheck universe face = A158-TSGATE-P1 OOS med_t +2.06 (1,724 codes) + GATE-RECHECK 5/5 five-member; NOT a strategy claim; overlapping windows inflate |t|"}
    # drift-direction decomposition face (construction divergence core)
    for fw in (20,):
        fwd = c.shift(-fw) / c - 1.0
        base = dec_s20 & fwd.notna() & yang & med500.notna()
        a = fwd[std20_open & calm & base]
        b = fwd[std20_open & wild & base]
        facts["drift_face_forward_20d"] = {
            "n_open_calm": int(len(a)), "n_open_wild": int(len(b)),
            "mean_fwd_open_calm": round(float(a.mean()), 6) if len(a) else float("nan"),
            "mean_fwd_open_wild": round(float(b.mean()), 6) if len(b) else float("nan"),
            "welch_t_calm_vs_wild": tstats(a, b),
            "note": "std20_open days split by burned W4 VOL face: calm side = drift-dominated increment face; descriptive only"}

    # ---- core48 member-level STD20_q90 open-rate spread (real roster) -----------
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    rates = {}
    for sym, d2 in sorted(prices.items()):
        d2 = d2[d2.index <= cut]
        if len(d2) >= 260:
            f_, q_, op, dv = std_faces(d2, 20)
            if dv.any():
                rates[str(sym)] = round(float((op & dv).mean()), 4)
    vals = sorted(rates.values())
    facts["core48_std20_open_rate"] = {
        "n": len(vals),
        "min": round(vals[0], 4), "median": round(vals[len(vals) // 2], 4),
        "max": round(vals[-1], 4),
        "method": "tl1.load_core() roster (import-reuse, real core48 face)",
        "members_with_lt260_rows_excluded": len(prices) - len(vals)}

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in facts.items() if not isinstance(v, dict)}, ensure_ascii=False))
    print("std20 face: decidable", facts["std20_decidable_days"],
          "| open", facts["std20_open_days"], "| open_rate", facts["std20_open_rate_on_decidable"])
    print("std10 face: decidable", facts["std10_decidable_days"],
          "| open", facts["std10_open_days"], "| open_rate", facts["std10_open_rate_on_decidable"])
    print("std20_open_rate_inside:", json.dumps(facts["std20_open_rate_inside_pct"], ensure_ascii=False))
    print("reverse_rates:", json.dumps(facts["reverse_rates_inside_std20_pct"], ensure_ascii=False))
    print("adjacency:", json.dumps(facts["adjacency"], ensure_ascii=False))
    print("distinct_space_increment:", json.dumps(facts["distinct_space_increment"], ensure_ascii=False))
    print("fwd20d:", json.dumps(facts["forward_20d"], ensure_ascii=False))
    print("fwd5d:", json.dumps(facts["forward_5d"], ensure_ascii=False))
    print("drift_face:", json.dumps(facts["drift_face_forward_20d"], ensure_ascii=False))
    print("eight_gate_256_cells: empty", facts["eight_gate_256_cells_empty_count"],
          "| nonzero", facts["eight_gate_256_cells_nonzero_count"],
          "| min-nonzero", facts["eight_gate_256_cells_min_nonzero"],
          "| max", facts["eight_gate_256_cells_max"],
          "| all-decidable days", facts["eight_gate_all_decidable_days"])
    print("extreme days:", json.dumps({k: (v if isinstance(v, str) else {"s20": v["std20_open"], "s10": v["std10_open"], "ratio": v["std20_over_q90ref"]}) for k, v in est.items()}, ensure_ascii=False))
    print("determinism_cross_checks:", json.dumps(facts["determinism_cross_checks"]))
    print("core48 std20 open rate:", json.dumps(facts["core48_std20_open_rate"], ensure_ascii=False))
    print("W11 STD20_q90/STD10_q90 pre-selection probe facts ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
