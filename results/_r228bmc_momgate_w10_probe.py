# -*- coding: utf-8 -*-
"""_r228bmc_momgate_w10_probe.py -- W10 MOM-gate (ROC20_q10) raw-face probe (candidate sec.2 facts, NOT results).

W10 candidate-supply slice per TRIAL_LABOR_LAW sec.1 standing-supply step
(MSG-20260929-1705-bm-c-ALL declaration, D-02 dual-signal leg 2 = this artifact
landing). Parking form: facts feed
research/TRIAL_LABOR_W10_CANDIDATE_MOM_PREREG_DRAFT.md.

Definitions (zero-invention law):
  MOM face  (census family O-1855(4) ROC20_q10, structural transplant of the
  in-repo census-verbatim decile-gate mechanics -- the MAD60_q10 pattern frozen
  verbatim in W8 prereg sec.2 / r431 probe tstate_faces() -- applied to the
  20-day rate-of-change indicator):
      roc20(d) = close(d)/close(d-20) - 1
      q10_ref  = roc20.rolling(252, min_periods=120).quantile(0.10)
      mom_oversold (gate open) = roc20 < q10_ref
  Warmup honesty: roc20 first valid at bar-idx 20; q10_ref first valid at
  bar-idx 139 (20 + 120 - 1). Census-side exact-definition re-verification
  (toolstack gate_census.py, bm-a face) = candidate reuse-checklist item.

Seven inherited gate faces (W3-W9 frozen, r431 probe lineage verbatim):
  GATE (MA200 bull/bear) / VOL (vol20-vs-med500 calm/wild) / YANG (close>open)
  / VCONF (volume-vs-med20 surge/dry) / STREAK (W7 up/down_streak2) /
  TSTATE (W8 deep_pullback MAD60_q10 + oversold_rsv RSV60<0.2) /
  AMP (W9 intraday_range vs med20amp wide/narrow).

New crossing faces (open readings, no priors): MOM x TSTATE (speed-vs-position
adjacency disclosure), MOM x STREAK (speed-vs-direction), MOM x AMP
(speed-vs-amplitude), plus eight-gate 256-cell grid; extreme-day
eight-dimensional states; census-style 20d/5d forward differential on the
510300 anchor (descriptive probe face, NOT a strategy claim). Deterministic,
zero network, read-only. NaN-comparison bucket artifact law (pit-95/r431):
every conditional rate uses notna()-derived decidable masks, never
map({False->x}) on comparison series.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join("scripts"))
import trial_labor_w1 as tl1  # import-face reuse law (loader T-22/T-34 lineage)

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4-W9 probes
OUT = "results/_r228bmc_momgate_w10_probe_facts.json"
R417_FACTS = "results/_r417bmb_ampgate_probe_facts.json"
R423_FACTS = "results/_r423bmb_w8tstate_probe_facts.json"
R431_FACTS = "results/_r431bmb_ampgate_w9_probe_facts.json"

EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]


def mom_faces(df):
    """ROC20_q10 census-family gate (structural transplant of the in-repo
    MAD60_q10 decile mechanics). Returns (roc20, q10_ref, mom_open, decidable)."""
    c = df["close"]
    roc20 = c / c.shift(20) - 1.0
    q10_ref = roc20.rolling(252, min_periods=120).quantile(0.10)
    mom_open = roc20 < q10_ref  # NaN comparison -> False; decidable below
    decidable = q10_ref.notna() & roc20.notna()
    return roc20, q10_ref, mom_open, decidable


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
    assert n == 3483, f"row count {n} != 3483 (W4-W9 probe anchor)"
    assert df["date"].iloc[-1] == CUTOFF, "last row != cutoff"
    zero_amp = int((df["high"] == df["low"]).sum())  # flat-line day (halt face)
    assert zero_amp == 0, "zero-range rows != 0 (r417 anchor)"

    c, h, l, v, o = (df[k] for k in ("close", "high", "low", "volume", "open"))

    # ---- MOM face (this probe's new face) ------------------------------------
    roc20, q10_ref, mom_open, dec_mom = mom_faces(df)
    warmup_mom = int(n - int(dec_mom.sum()))
    first_decidable_idx = int(np.argmax(dec_mom.to_numpy()))
    assert first_decidable_idx == 139, f"MOM first decidable {first_decidable_idx} != 139"
    assert int(dec_mom.sum()) + warmup_mom == n

    # ---- inherited faces (W3-W9 verbatim) ------------------------------------
    amp, med20amp, wide = amp_faces(df)
    amp_known = wide.notna()
    st = streak_faces(df)
    up_st, dn_st, neither = st == 1.0, st == 0.0, st == -1.0
    mad_q10, rsv_low, decidable, rsv60 = tstate_faces(df)
    dec_mad = decidable["deep_pullback_mad60_q10"]
    dec_rsv = decidable["oversold_rsv60_low02"]

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
             "mom_warmup_gate_closed_bars": warmup_mom,
             "mom_first_decidable_bar_idx": first_decidable_idx,
             "mom_decidable_days": int(dec_mom.sum()),
             "mom_open_days": int((mom_open & dec_mom).sum()),
             "mom_open_rate_on_decidable": round(float((mom_open & dec_mom).mean()), 4),
             "roc20_nan_rows_before_bar20": int(roc20.isna().sum()),
             "probe_lineage": "r431 seven-gate lineage + MOM face (W10 candidate supply, eight-gate crossing)"}

    # ---- determinism cross-check vs r417 / r423 / r431 frozen fact files ------
    xchecks = {}
    if os.path.exists(R431_FACTS):
        f31 = json.load(open(R431_FACTS, encoding="utf-8"))
        xchecks["r431"] = {
            "wide_days_match": f31["wide_days"] == int((wide[amp_known] == 1).sum()),
            "amp_warmup_match": f31["amp_warmup_gate_closed_bars"] == int(amp_known.isna().sum() if False else (n - int(amp_known.sum()))),
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
    facts["determinism_cross_checks"] = xchecks

    # ---- MOM inside each inherited gate (decidable-mask honest rates) ---------
    def rate(mask_in, gate, dec):
        both = int((mask_in & gate).sum())
        base = int((mask_in & dec).sum())
        return round(100.0 * both / base, 2) if base else float("nan")

    facts["mom_open_rate_inside_pct"] = {
        "bull": rate(bull, mom_open, dec_mom), "bear": rate(bear, mom_open, dec_mom),
        "calm": rate(calm, mom_open, dec_mom), "wild": rate(wild, mom_open, dec_mom),
        "yang": rate(yang, mom_open, dec_mom), "red": rate(~yang, mom_open, dec_mom),
        "surge": rate(surge, mom_open, dec_mom), "dry": rate(~surge, mom_open, dec_mom),
        "up_streak2": rate(up_st, mom_open, dec_mom), "down_streak2": rate(dn_st, mom_open, dec_mom),
        "neither_streak": rate(neither, mom_open, dec_mom),
        "mad60_q10_open": rate(mad_q10, mom_open, dec_mom), "mad60_q10_closed": rate(~mad_q10 & dec_mad, mom_open, dec_mom),
        "rsv60_low_open": rate(rsv_low, mom_open, dec_mom), "rsv60_low_closed": rate(~rsv_low & dec_rsv, mom_open, dec_mom),
        "amp_wide": rate(wide == 1, mom_open, dec_mom), "amp_narrow": rate(wide == 0, mom_open, dec_mom)}

    # ---- reverse: gate rates inside MOM-open vs MOM-closed --------------------
    dec_all = dec_mom & st.notna()
    facts["reverse_rates_inside_mom_pct"] = {
        "down_streak_rate_when_mom_open": rate(mom_open, dn_st, dec_all),
        "down_streak_rate_when_mom_closed": rate(~mom_open & dec_mom, dn_st, dec_all),
        "mad60_rate_when_mom_open": rate(mom_open & dec_mad, mad_q10, dec_mom & dec_mad),
        "mad60_rate_when_mom_closed": rate((~mom_open & dec_mom) & dec_mad, mad_q10, dec_mom & dec_mad),
        "rsv60_rate_when_mom_open": rate(mom_open & dec_rsv, rsv_low, dec_mom & dec_rsv),
        "rsv60_rate_when_mom_closed": rate((~mom_open & dec_mom) & dec_rsv, rsv_low, dec_mom & dec_rsv)}

    # ---- adjacency cross cells (speed vs position vs direction vs amplitude) -
    def cell(a, da, b, db):
        m = da & db
        both_open = int((a & b & m).sum())
        a_open = int((a & m).sum())
        b_open = int((b & m).sum())
        union = int(((a | b) & m).sum())
        return {"both_open": both_open, "a_open": a_open, "b_open": b_open,
                "a_open_pct_of_b_open": round(100.0 * both_open / b_open, 2) if b_open else float("nan"),
                "union_days": union, "joint_decidable_days": int(m.sum())}

    facts["adjacency"] = {
        "mom_vs_mad60": cell(mom_open, dec_mom, mad_q10, dec_mad),
        "mom_vs_rsv60": cell(mom_open, dec_mom, rsv_low, dec_rsv),
        "mom_vs_downstreak": cell(mom_open, dec_mom, dn_st, st.notna()),
        "mom_vs_wide": cell(mom_open, dec_mom, wide == 1, amp_known)}

    # ---- EIGHT-gate 256-cell crossing ----------------------------------------
    cells = {}
    n_empty = 0
    m8 = dec_mom & bull.notna() & calm.notna() & amp_known & st.notna() & dec_mad & dec_rsv
    for bname, b in (("bull", bull), ("bear", bear)):
        for vname, vv in (("calm", calm), ("wild", wild)):
            for yname, y in (("yang", yang), ("red", ~yang)):
                for sname, s in (("surge", surge), ("dry", ~surge)):
                    for kname, k in (("up_streak", up_st), ("down_streak", dn_st)):
                        for tname, t in (("mad60", mad_q10), ("rsv60", rsv_low)):
                            for aname, a in (("wide", wide == 1), ("narrow", wide == 0)):
                                for mname, mm in (("mom_open", mom_open), ("mom_closed", ~mom_open & dec_mom)):
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

    # ---- extreme days: eight-dimensional state readout ------------------------
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
                     "mom_open": bool(mom_open.iloc[i]) if dec_mom.iloc[i] else None,
                     "roc20_value": (None if pd.isna(roc20.iloc[i]) else round(float(roc20.iloc[i]), 4)),
                     "roc20_over_q10ref": (None if pd.isna(roc20.iloc[i]) or pd.isna(q10_ref.iloc[i]) else round(float(roc20.iloc[i] / q10_ref.iloc[i]), 3))}
    facts["extreme_day_states"] = est

    # ---- census-style forward differential (descriptive face, NOT a claim) ----
    for fw in (5, 20):
        fwd = c.shift(-fw) / c - 1.0
        base = dec_mom & fwd.notna()  # forward window inside panel
        a = fwd[mom_open & base]
        b = fwd[(~mom_open & dec_mom) & base]
        facts[f"forward_{fw}d"] = {
            "n_open": int(len(a)), "n_closed": int(len(b)),
            "mean_fwd_open": round(float(a.mean()), 6) if len(a) else float("nan"),
            "mean_fwd_closed": round(float(b.mean()), 6) if len(b) else float("nan"),
            "diff_open_minus_closed": round(float(a.mean() - b.mean()), 6) if (len(a) and len(b)) else float("nan"),
            "welch_t": tstats(a, b),
            "note": "descriptive probe face on 510300 anchor only; census universe face = 1,724 codes (O-1855(4)); NOT a strategy claim; overlapping windows inflate |t|"}

    # ---- core48 member-level MOM open-rate spread (real roster, import-reuse) --
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    rates = {}
    for sym, d2 in sorted(prices.items()):
        d2 = d2[d2.index <= cut]
        if len(d2) >= 260:
            _, _, mo, dm = mom_faces(d2)
            if dm.any():
                rates[str(sym)] = round(float((mo & dm).mean()), 4)
    vals = sorted(rates.values())
    facts["core48_mom_open_rate"] = {
        "n": len(vals),
        "min": round(vals[0], 4), "median": round(vals[len(vals) // 2], 4),
        "max": round(vals[-1], 4),
        "method": "tl1.load_core() roster (import-reuse, real core48 face)",
        "members_with_lt260_rows_excluded": len(prices) - len(vals)}

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in facts.items() if not isinstance(v, dict)}, ensure_ascii=False))
    print("mom face: warmup", warmup_mom, "| decidable", facts["mom_decidable_days"],
          "| open", facts["mom_open_days"], "| open_rate", facts["mom_open_rate_on_decidable"])
    print("mom_open_rate_inside:", json.dumps(facts["mom_open_rate_inside_pct"], ensure_ascii=False))
    print("adjacency:", json.dumps(facts["adjacency"], ensure_ascii=False))
    print("fwd20d:", json.dumps(facts["forward_20d"], ensure_ascii=False))
    print("fwd5d:", json.dumps(facts["forward_5d"], ensure_ascii=False))
    print("eight_gate_256_cells: empty", facts["eight_gate_256_cells_empty_count"],
          "| nonzero", facts["eight_gate_256_cells_nonzero_count"],
          "| min-nonzero", facts["eight_gate_256_cells_min_nonzero"],
          "| max", facts["eight_gate_256_cells_max"],
          "| all-decidable days", facts["eight_gate_all_decidable_days"])
    print("extreme days:", json.dumps({k: (v if isinstance(v, str) else {"mom": v["mom_open"], "roc20": v["roc20_value"]}) for k, v in est.items()}, ensure_ascii=False))
    print("determinism_cross_checks:", json.dumps(facts["determinism_cross_checks"]))
    print("core48 mom open rate:", json.dumps(facts["core48_mom_open_rate"], ensure_ascii=False))
    print("W10 MOM probe facts ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
