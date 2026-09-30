# -*- coding: utf-8 -*-
"""_r470bmb_vsumd_resi_w14_probe.py -- W14 pre-selection probe: A158-TSGATE-P1
48-PASS pool next unconsumed CONFIRM families VSUMD20_q10/VSUMD10_q10-side
mirror = VSUMD20_q90/VSUMD10_q90 (volume-delta direction purity, GATE-RECHECK
CONFIRM #24/#25/#26 reps) + RESI60_q90 (trend-extension deviation, CONFIRM
#12 rep) raw-face facts on the 510300 anchor. NOT results, NOT a strategy
claim.

W14 supply-prep slice per TRIAL_LABOR_LAW sec.1 standing-supply step
(bm-b r470 berth). O-1132 sample-expansion order: generate cap 5,000->10,000
from W14 + >=2 new mechanism faces per wave -> this probe carries BOTH new
faces' anchor facts. O-1147 combination-line order: portfolio-book face =
separate downstream prereg per reform canon sec.6 (NOT merged into this
batch) -- consumer_plan pointer only.

Berth-window honesty: W13 JUDGE verdict landed 2026-09-30 12:33 (before this
berth) = pre-commitment window (DECISION_CHAIN v1.2 sec.4.7) already closed
for W14 -- disclosed. Supply selection consumed ONLY pre-verdict frozen
sources: 48-PASS CONFIRM registry (r439/r441 GATE-RECHECK, frozen in-repo
2026-09-29 17:49) + r441 verdict named VSUMD30 route + O-1132/O-1147 order
text. W13 verdict face (SUMN axis screen-toxic) shares no information
channel with VSUMD/RESI family selection (different factor families) --
honest note, not a claim of immunization.

Pool-turn lineage (r234 digest sec.3 named-pool pointer, extended): census
four positive families all consumed (MAD60/RSV60->W8, ROC20->W10, VSTD20->
DEMOTE) -> 48-PASS pool order STD->RSQR->SUMN/SUMP consumed by W11/W12/W13
(all frozen+judged) -> NEXT unconsumed CONFIRM families by strength:
VSUMD20_q90 (OOS 0.876, 5/5 members, net med +0.01340) and RESI60_q90
(OOS med_t 1.178, the highest unconsumed CONFIRM OOS) -- this probe answers
the deferral question for BOTH.

The deferral question this probe answers:
  (a) VSUMD (volume-delta direction purity): does the up-volume-dominance
      high-side gate open a DISTINCT day-level conditional space from the
      burned trial-grammar axes -- esp. W13 SUMN (price-diff direction
      purity: SAME functional form on a different series = the true
      nearest neighbor), W4 VOL (volume LEVEL), W6 VCONF (volume shape) --
      or is it a collapsed neighbor like VSTD20_q20 was (98.5% inside W4
      calm, r234 DEMOTE)?
  (b) RESI60 (trend-extension deviation): does the OLS-residual high side
      (price stretched above own 60d trend) open a distinct space from
      W8 RSV60 (range position face, same 60d window) and W12 RSQR (same
      OLS construction family, fit quality) -- position-vs-trend is a
      genuinely different reading, but 60d-window position faces are the
      known collapse risk (r234 law).

Construction honesty (verbatim-import discipline, zero re-implementation):
  VSUMD/VSUMP/VSUMN and RESI come from the FROZEN in-repo runner
  scripts/a158_tsgate_probe.py -- import a158_tsgate_probe;
  F = alpha158_factors(df);
  VSUMP%d = sum(clip(+dv,0),d)/sum(|dv|,d); VSUMN%d = sum(clip(-dv,0),d)/
  sum(|dv|,d); VSUMD%d = (sum(clip(+dv,0),d) - sum(clip(-dv,0),d)) /
  sum(|dv|,d)   (volume-delta direction dominance in [-1,1])
  RESI%d  = last-point residual of rolling OLS(close, d) / close
  Gate (A158_TSGATE_P1 prereg sec.2 frozen): high side
      f > f.rolling(252, min_periods=120).quantile(0.90)
  decidable = f.notna() & qref.notna() (pit-95/r431 NaN-bucket artifact law).
  Mirror-twin face: VSUMD is a strictly-decreasing affine transform of
  VSUMN pointwise (eps=1e-12 denominator guard adds a day-varying ~1e-12/
  vsa offset) -> VSUMD_q90 should fire on the SAME days as VSUMN_q10 and
  VSUMP_q90 (cluster #24/#25/#26 corr 1.000); XOR measured here, eps-face
  residue disclosed honestly.

Deterministic, zero network, read-only, marks +0, SEED +0.
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
sys.path.insert(0, os.path.join("results"))
import a158_tsgate_probe as a158            # frozen runner (VSUMD/RESI verbatim)
import _r237bmc_stdq90_w11_probe as r237p   # frozen W11 probe (W3-W11 faces)
import _r456bma_sumnsump_w13_probe as w13p   # frozen W13 probe (sumn gate verbatim)
import trial_labor_w1 as tl1                # via r237p lineage (core48 loader)

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4-W13 probes
OUT = "results/_r470bmb_vsumd_resi_w14_probe_facts.json"
R417_FACTS = "results/_r417bmb_ampgate_probe_facts.json"
R423_FACTS = "results/_r423bmb_w8tstate_probe_facts.json"
R431_FACTS = "results/_r431bmb_ampgate_w9_probe_facts.json"
R228_FACTS = "results/_r228bmc_momgate_w10_probe_facts.json"
R234_FACTS = "results/_r234bmc_vstd20_w11_probe_facts.json"
R237_FACTS = "results/_r237bmc_stdq90_w11_probe_facts.json"
R447_FACTS = "results/_r447bma_rsqr_w12_probe_facts.json"
R456_FACTS = "results/_r456bma_sumnsump_w13_probe_facts.json"
GATE_RECHECK = "results/gate_recheck_a158.json"

EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]


def hi_gate(f):
    """A158_TSGATE_P1 frozen high-side gate semantics via runner constants
    (import-reuse, W12/W13 probe lineage). Returns (open, decidable, qref)."""
    qref = f.rolling(a158.GATE_WIN, min_periods=a158.GATE_MINP).quantile(a158.QHIGH)
    dec = f.notna() & qref.notna()
    return (f > qref) & dec, dec, qref


def tstats(a, b):
    return r237p.tstats(a, b)  # frozen Welch-t helper (r237 verbatim)


def main() -> int:
    df = pd.read_csv(os.path.join("data", "daily", "sh510300.csv"))
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)
    n = len(df)
    assert n == 3483, f"row count {n} != 3483 (W4-W13 probe anchor)"
    assert df["date"].iloc[-1] == CUTOFF, "last row != cutoff"
    zero_amp = int((df["high"] == df["low"]).sum())  # flat-line day (halt face)
    assert zero_amp == 0, "zero-range rows != 0 (r417 anchor)"

    c, h, l, v, o = (df[k] for k in ("close", "high", "low", "volume", "open"))

    # ---- VSUMD / RESI faces (frozen-runner verbatim import; zero re-impl) ----
    di = pd.DataFrame({"open": o, "high": h, "low": l, "close": c, "volume": v},
                      index=pd.RangeIndex(n))
    F = a158.alpha158_factors(di)
    vd20, vd10, vd30 = F["VSUMD20"], F["VSUMD10"], F["VSUMD30"]
    vn20, vp20 = F["VSUMN20"], F["VSUMP20"]
    resi60, beta20, rsqr20 = F["RESI60"], F["BETA20"], F["RSQR20"]
    cd5, cn20 = F["CNTD5"], F["CNTN20"]
    vd20_open, dec_vd20, q90_20 = hi_gate(vd20)
    vd10_open, dec_vd10, q90_10 = hi_gate(vd10)
    re60_open, dec_re60, q90_r60 = hi_gate(resi60)
    cd5_open, dec_cd5, q90_cd5 = hi_gate(cd5)      # CNTD5_q90 (CONFIRM #1 rep)
    cn20_open, dec_cn20, q90_cn20 = w13p.sumn_gate(cn20)  # CNTN20_q10 low side (CONFIRM #2)

    # warmup fail-closed: vd/cd valid from idx 1 (diff undefined at 0); resi
    # valid from idx 0 (expanding min_periods=1); CNT up/down-day indicators are
    # (c>c.shift(1)).astype(float) -> idx-0 comparison-vs-NaN = False = 0.0 NOT
    # NaN -> CNTD/CNTN valid from idx 0 -> qref(252,min120) first valid at 119
    # (ONE bar earlier than the SUMN/RSQR/STD family -- honest disclosure)
    for tag, dec, first_expect in (("vsumd20", dec_vd20, 120), ("vsumd10", dec_vd10, 120),
                                   ("resi60", dec_re60, 120), ("cntd5", dec_cd5, 119),
                                   ("cntn20", dec_cn20, 119)):
        first_dec = int(np.argmax(dec.to_numpy()))
        assert first_dec == first_expect, f"{tag} first decidable {first_dec} != {first_expect}"

    # internal spot-check vs direct window computation (W13 probe discipline):
    # VSUMD%d[i] == (sum(clip(+dv,0)) - sum(clip(-dv,0))) / (sum(|dv|) + 1e-12)
    vv = v.to_numpy(dtype=float)
    for d_win, series in ((10, vd10), (20, vd20)):
        for i in (59, 500, 2000):
            w = vv[i - d_win + 1: i + 1] - vv[i - d_win: i]
            got = float(series.iloc[i])
            ref = float((np.clip(w, 0, None).sum() - np.clip(-w, 0, None).sum())
                        / (np.abs(w).sum() + 1e-12))
            assert abs(got - ref) < 1e-12, f"VSUMD{d_win}@{i} {got} != direct {ref}"
    # RESI60[i] == (close[i] - ols_fit(t=1..60, y=close[i-59..i])[60]) / close[i]
    cv = c.to_numpy(dtype=float)
    for i in (500, 2000):
        y = cv[i - 59: i + 1]
        t = np.arange(1, 61, dtype=float)
        b_ref, a_ref = np.polyfit(t, y, 1)  # polyfit returns [slope, intercept]
        resid = y[-1] - (a_ref + b_ref * 60.0)
        got = float(resi60.iloc[i]) * cv[i]
        assert abs(got - resid) < 1e-6, f"RESI60@{i} {got} != direct {resid}"
    # CNTD5[i] == mean(up-day,5d) - mean(down-day,5d); CNTN20[i] == mean(down-day,20d)
    up_d = (cv[1:] > cv[:-1]).astype(float)
    dn_d = (cv[1:] < cv[:-1]).astype(float)
    for i in (59, 500, 2000):
        w5u = up_d[i - 5:i].mean()   # diffs d-4..d (idx i-5..i-1 in diff array)
        w5d = dn_d[i - 5:i].mean()
        got = float(cd5.iloc[i])
        assert abs(got - (w5u - w5d)) < 1e-12, f"CNTD5@{i} {got} != direct {w5u - w5d}"
        got_n = float(cn20.iloc[i])
        w20d = dn_d[i - 20:i].mean()
        assert abs(got_n - w20d) < 1e-12, f"CNTN20@{i} {got_n} != direct {w20d}"

    # mirror-twin identity: VSUMP+VSUMN==1 (eps face); VSUMD = 1-2*VSUMN-eps'
    both = (vp20 + vn20).dropna()
    facts_mirror = {"vsump_plus_vsumn_max_dev": float((both - 1.0).abs().max()),
                    "note_id": "VSUMP+VSUMN==vsA/(vsA+1e-12) (eps denominator face), "
                               "max dev quantifies eps residue"}
    # same-days empirical proof: VSUMD20_q90 vs VSUMP20_q90 vs VSUMN20_q10
    vp20_hi, _, _ = hi_gate(vp20)
    vn20_lo, _, _ = w13p.sumn_gate(vn20)  # W13 frozen low-side gate (import-reuse)
    xor_p = int((vd20_open ^ vp20_hi).sum())
    xor_n = int((vd20_open ^ vn20_lo).sum())
    both_p = int((vd20_open & vp20_hi & dec_vd20).sum())
    facts_mirror.update({
        "vsumd20_q90_vs_vsump20_q90_both_open_days": both_p,
        "vsumd20_q90_vs_vsump20_q90_xor_days": xor_p,
        "vsumd20_q90_vs_vsumn20_q10_xor_days": xor_n,
        "note": "VSUMD strictly-decreasing affine of VSUMN pointwise (eps~1e-12/vsa "
                "day-varying offset) -> q90-side VSUMD gate should fire same days as "
                "VSUMP_q90/VSUMN_q10 (cluster #24/#25/#26 corr 1.000); XOR>0 = eps "
                "rank-flip residue, disclosed honestly"})

    # ---- inherited burned faces (W3-W13 frozen modules verbatim) -----------
    amp, med20amp, wide = r237p.amp_faces(df)
    amp_known = wide.notna()
    st = r237p.streak_faces(df)
    up_st, dn_st, neither = st == 1.0, st == 0.0, st == -1.0
    mad_q10, rsv_low, decidable, rsv60 = r237p.tstate_faces(df)
    dec_mad = decidable["deep_pullback_mad60_q10"]
    dec_rsv = decidable["oversold_rsv60_low02"]
    roc20, q10mom, mom_open, dec_mom = r237p.mom_faces(df)
    std20, q90s_20, std20_open, dec_s20 = r237p.std_faces(df, 20)
    std10, q90s_10, std10_open, dec_s10 = r237p.std_faces(df, 10)
    r20_open, dec_r20, _ = hi_gate(rsqr20)  # W12 frozen face (r447 verbatim)
    sn20 = F["SUMN20"]
    sn20_open, dec_sn20, _ = w13p.sumn_gate(sn20)  # W13 frozen face (r456 verbatim)

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
             "mirror_identity": facts_mirror,
             "probe_lineage": "W13 r456 probe paradigm + a158 frozen runner verbatim-import "
                              "(VSUMD/VSUMP/VSUMN/RESI face, W14 pre-selection); r417/r423/r431/"
                              "r228/r234/r237/r447/r456 eight-lineage cross-checked",
             "construction_disclosure": {
                 "vsumd": "VSUMD=(sum(clip(+dv,0),d)-sum(clip(-dv,0),d))/(sum(|dv|,d)+1e-12) in "
                          "[-1,1] volume-delta direction dominance; high-side gate = up-VOLUME-"
                          "dominant window (OBV-family state); nearest burned neighbor = W13 SUMN "
                          "(SAME functional form on price diffs vs volume deltas) + W4 VOL level "
                          "+ W6 VCONF shape; direction-LOADED like SUMN",
                 "resi": "RESI60=last-point residual of rolling OLS(close,60)/close; high-side "
                         "gate = price stretched ABOVE own 60d trend (trend-extension state); "
                         "nearest burned neighbors = W8 RSV60 (60d RANGE position, same window) "
                         "+ W12 RSQR (same OLS construction, fit QUALITY not deviation MAGNITUDE); "
                         "sign-aware deviation face, new dimension family vs all burned axes"},
             "warmup_disclosure": "vsumd/resi first-decidable bar-idx 120 (vd valid from idx 1: "
                                  "dv undefined at 0; resi valid from idx 0 expanding min_periods=1; "
                                  "qref 252/min120 binds both) == RSQR/STD/SUMN family warmup; "
                                  "CNTD/CNTN first-decidable 119 (up/down-day indicator at idx 0 = "
                                  "comparison-vs-NaN -> False -> 0.0 not NaN -> qref one bar earlier); "
                                  "honest one-bar construction-family divergence"}

    for tag, dec, op in (("vsumd20", dec_vd20, vd20_open), ("vsumd10", dec_vd10, vd10_open),
                         ("resi60", dec_re60, re60_open), ("cntd5", dec_cd5, cd5_open),
                         ("cntn20", dec_cn20, cn20_open)):
        facts[f"{tag}_decidable_days"] = int(dec.sum())
        facts[f"{tag}_open_days"] = int((op & dec).sum())
        facts[f"{tag}_open_rate_on_decidable"] = round(float((op & dec).mean()), 4)

    # direction-loaded disclosure: slope-sign split among open days (all faces)
    for tag, op, dec in (("vsumd20", vd20_open, dec_vd20), ("resi60", re60_open, dec_re60),
                         ("cntd5", cd5_open, dec_cd5), ("cntn20", cn20_open, dec_cn20)):
        m_open = op & dec & beta20.notna()
        facts[f"{tag}_open_slope_sign_split"] = {
            "up_slope_days": int((m_open & (beta20 > 0)).sum()),
            "down_slope_days": int((m_open & (beta20 <= 0)).sum()),
            "note": "BETA20 sign from the same frozen runner; VSUMD direction-LOADED "
                    "(up-volume dominant) but slope split quantifies price-trend agreement "
                    "vs volume-trend divergence; RESI60 sign-aware by construction "
                    "(high residual = above-trend stretch)"}

    # ---- determinism cross-check vs frozen probe facts (eight lineage files) --
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
        xchecks["r234"] = {"rows_match": f34["rows"] == int(n)}
    if os.path.exists(R237_FACTS):
        f37 = json.load(open(R237_FACTS, encoding="utf-8"))
        xchecks["r237"] = {"rows_match": f37["rows"] == int(n),
                           "std20_decidable_match": f37["std20_decidable_days"] == int(dec_s20.sum()),
                           "std20_open_match": f37["std20_open_days"] == int((std20_open & dec_s20).sum()),
                           "std10_open_match": f37["std10_open_days"] == int((std10_open & dec_s10).sum())}
    if os.path.exists(R447_FACTS):
        f47 = json.load(open(R447_FACTS, encoding="utf-8"))
        xchecks["r447"] = {"rows_match": f47["rows"] == int(n),
                           "rsqr20_decidable_match": f47["rsqr20_decidable_days"] == int(dec_r20.sum()),
                           "rsqr20_open_match": f47["rsqr20_open_days"] == int((r20_open & dec_r20).sum())}
    if os.path.exists(R456_FACTS):
        f56 = json.load(open(R456_FACTS, encoding="utf-8"))
        xchecks["r456"] = {"rows_match": f56["rows"] == int(n),
                           "sumn20_decidable_match": f56["sumn20_decidable_days"] == int(dec_sn20.sum()),
                           "sumn20_open_match": f56["sumn20_open_days"] == int((sn20_open & dec_sn20).sum())}
    if os.path.exists(GATE_RECHECK):
        gr = json.load(open(GATE_RECHECK, encoding="utf-8"))
        refs = {}
        for gname in ("VSUMD10_q90", "VSUMD20_q90", "VSUMD30_q90", "RESI60_q90"):
            try:
                ref = gr["gates"][gname]["face_a"]["members"]["510300"]
                refs[gname] = {"n_in_ref": ref["n_in"], "n_out_ref": ref["n_out"]}
            except Exception as e:
                refs[gname] = {"error": str(e)}
        xchecks["gate_recheck_ref"] = {**refs,
            "note": "five-member secondary face different member-panel loading; disclosure reference NOT fail-closed"}
    facts["determinism_cross_checks"] = xchecks

    # ---- open-rate inside each inherited gate (both new faces) ---------------
    def rate(mask_in, gate, dec):
        both = int((mask_in & gate).sum())
        base = int((mask_in & dec).sum())
        return round(100.0 * both / base, 2) if base else float("nan")

    for tag, op, dec in (("vsumd20", vd20_open, dec_vd20), ("resi60", re60_open, dec_re60),
                         ("cntd5", cd5_open, dec_cd5), ("cntn20", cn20_open, dec_cn20)):
        facts[f"{tag}_open_rate_inside_pct"] = {
            "bull": rate(bull, op, dec), "bear": rate(bear, op, dec),
            "calm": rate(calm, op, dec), "wild": rate(wild, op, dec),
            "yang": rate(yang, op, dec), "red": rate(~yang, op, dec),
            "surge": rate(surge, op, dec), "dry": rate(~surge, op, dec),
            "up_streak2": rate(up_st, op, dec), "down_streak2": rate(dn_st, op, dec),
            "neither_streak": rate(neither, op, dec),
            "mad60_q10_open": rate(mad_q10, op, dec), "mad60_q10_closed": rate(~mad_q10 & dec_mad, op, dec),
            "rsv60_low_open": rate(rsv_low, op, dec), "rsv60_low_closed": rate(~rsv_low & dec_rsv, op, dec),
            "amp_wide": rate(wide == 1, op, dec), "amp_narrow": rate(wide == 0, op, dec),
            "mom_open": rate(mom_open & dec_mom, op, dec & dec_mom), "mom_closed": rate((~mom_open & dec_mom), op, dec & dec_mom),
            "std20_open": rate(std20_open & dec_s20, op, dec & dec_s20), "std20_closed": rate((~std20_open & dec_s20), op, dec & dec_s20),
            "rsqr20_open": rate(r20_open & dec_r20, op, dec & dec_r20), "rsqr20_closed": rate((~r20_open & dec_r20), op, dec & dec_r20),
            "sumn20_open": rate(sn20_open & dec_sn20, op, dec & dec_sn20), "sumn20_closed": rate((~sn20_open & dec_sn20), op, dec & dec_sn20)}
    # cross-new-face rates
    facts["cross_new_face_rates"] = {
        "vsumd20_open_rate_when_resi60_open": rate(re60_open & dec_re60, vd20_open, dec_vd20 & dec_re60),
        "vsumd20_open_rate_when_resi60_closed": rate((~re60_open & dec_re60), vd20_open, dec_vd20 & dec_re60),
        "resi60_open_rate_when_vsumd20_open": rate(vd20_open & dec_vd20, re60_open, dec_re60 & dec_vd20),
        "resi60_open_rate_when_vsumd20_closed": rate((~vd20_open & dec_vd20), re60_open, dec_re60 & dec_vd20),
        "cntd5_open_rate_when_resi60_open": rate(re60_open & dec_re60, cd5_open, dec_cd5 & dec_re60),
        "resi60_open_rate_when_cntd5_open": rate(cd5_open & dec_cd5, re60_open, dec_re60 & dec_cd5),
        "cntn20_open_rate_when_cntd5_open": rate(cd5_open & dec_cd5, cn20_open, dec_cn20 & dec_cd5)}

    # ---- neighbor adjacency cross cells (THE deferral question, both faces) ----
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

    adj_vd = {
        "vsumd20_vs_wild": cell(vd20_open, dec_vd20, wild, med500.notna()),
        "vsumd20_vs_calm": cell(vd20_open, dec_vd20, calm, med500.notna()),
        "vsumd20_vs_wide": cell(vd20_open, dec_vd20, wide == 1, amp_known),
        "vsumd20_vs_narrow": cell(vd20_open, dec_vd20, wide == 0, amp_known),
        "vsumd20_vs_mad60": cell(vd20_open, dec_vd20, mad_q10, dec_mad),
        "vsumd20_vs_rsv60": cell(vd20_open, dec_vd20, rsv_low, dec_rsv),
        "vsumd20_vs_downstreak": cell(vd20_open, dec_vd20, dn_st, st.notna()),
        "vsumd20_vs_upstreak": cell(vd20_open, dec_vd20, up_st, st.notna()),
        "vsumd20_vs_mom": cell(vd20_open, dec_vd20, mom_open, dec_mom),
        "vsumd20_vs_std20": cell(vd20_open, dec_vd20, std20_open, dec_s20),
        "vsumd20_vs_rsqr20": cell(vd20_open, dec_vd20, r20_open, dec_r20),
        "vsumd20_vs_sumn20": cell(vd20_open, dec_vd20, sn20_open, dec_sn20),
        "vsumd20_vs_resi60": cell(vd20_open, dec_vd20, re60_open, dec_re60),
        "vsumd20_vs_surge": cell(vd20_open, dec_vd20, surge, med20v.notna()),
        "vsumd10_vs_vsumd20": cell(vd10_open, dec_vd10, vd20_open, dec_vd20)}
    adj_re = {
        "resi60_vs_wild": cell(re60_open, dec_re60, wild, med500.notna()),
        "resi60_vs_calm": cell(re60_open, dec_re60, calm, med500.notna()),
        "resi60_vs_wide": cell(re60_open, dec_re60, wide == 1, amp_known),
        "resi60_vs_narrow": cell(re60_open, dec_re60, wide == 0, amp_known),
        "resi60_vs_mad60": cell(re60_open, dec_re60, mad_q10, dec_mad),
        "resi60_vs_rsv60": cell(re60_open, dec_re60, rsv_low, dec_rsv),
        "resi60_vs_rsv60_highside_notlow": cell(re60_open, dec_re60, ~rsv_low & dec_rsv, dec_rsv),
        "resi60_vs_downstreak": cell(re60_open, dec_re60, dn_st, st.notna()),
        "resi60_vs_upstreak": cell(re60_open, dec_re60, up_st, st.notna()),
        "resi60_vs_mom": cell(re60_open, dec_re60, mom_open, dec_mom),
        "resi60_vs_std20": cell(re60_open, dec_re60, std20_open, dec_s20),
        "resi60_vs_rsqr20": cell(re60_open, dec_re60, r20_open, dec_r20),
        "resi60_vs_rsqr20_closed": cell(re60_open, dec_re60, ~r20_open & dec_r20, dec_r20),
        "resi60_vs_sumn20": cell(re60_open, dec_re60, sn20_open, dec_sn20),
        "resi60_vs_vsumd20": cell(re60_open, dec_re60, vd20_open, dec_vd20),
        "resi60_vs_bull": cell(re60_open, dec_re60, bull, ma200.notna()),
        "resi60_vs_bear": cell(re60_open, dec_re60, bear, ma200.notna())}
    facts["adjacency_vsumd20"] = adj_vd
    facts["adjacency_resi60"] = adj_re
    adj_cd = {
        "cntd5_vs_wild": cell(cd5_open, dec_cd5, wild, med500.notna()),
        "cntd5_vs_calm": cell(cd5_open, dec_cd5, calm, med500.notna()),
        "cntd5_vs_wide": cell(cd5_open, dec_cd5, wide == 1, amp_known),
        "cntd5_vs_narrow": cell(cd5_open, dec_cd5, wide == 0, amp_known),
        "cntd5_vs_mad60": cell(cd5_open, dec_cd5, mad_q10, dec_mad),
        "cntd5_vs_rsv60": cell(cd5_open, dec_cd5, rsv_low, dec_rsv),
        "cntd5_vs_downstreak": cell(cd5_open, dec_cd5, dn_st, st.notna()),
        "cntd5_vs_upstreak": cell(cd5_open, dec_cd5, up_st, st.notna()),
        "cntd5_vs_mom": cell(cd5_open, dec_cd5, mom_open, dec_mom),
        "cntd5_vs_std20": cell(cd5_open, dec_cd5, std20_open, dec_s20),
        "cntd5_vs_rsqr20": cell(cd5_open, dec_cd5, r20_open, dec_r20),
        "cntd5_vs_sumn20": cell(cd5_open, dec_cd5, sn20_open, dec_sn20),
        "cntd5_vs_resi60": cell(cd5_open, dec_cd5, re60_open, dec_re60),
        "cntd5_vs_vsumd20": cell(cd5_open, dec_cd5, vd20_open, dec_vd20),
        "cntd5_vs_surge": cell(cd5_open, dec_cd5, surge, med20v.notna()),
        "cntd5_vs_yang": cell(cd5_open, dec_cd5, yang, pd.Series(np.ones(n, dtype=bool), index=c.index)),
        "cntn20_vs_cntd5": cell(cn20_open, dec_cn20, cd5_open, dec_cd5),
        "cntn20_vs_sumn20": cell(cn20_open, dec_cn20, sn20_open, dec_sn20),
        "cntn20_vs_upstreak": cell(cn20_open, dec_cn20, up_st, st.notna())}
    facts["adjacency_cntd5"] = adj_cd

    # distinct-space increment faces (r228 "mom-only days" pattern)
    dec_calm = dec_vd20 & med500.notna()
    dec_nar = dec_vd20 & amp_known
    facts["distinct_space_increment_vsumd20"] = {
        "vsumd20_open_and_calm_days": int((vd20_open & calm & dec_calm).sum()),
        "vsumd20_open_and_wild_days": int((vd20_open & wild & dec_calm).sum()),
        "vsumd20_open_and_narrow_days": int((vd20_open & (wide == 0) & dec_nar).sum()),
        "vsumd20_open_and_sumn20_closed_days": int((vd20_open & (~sn20_open & dec_sn20) & (dec_vd20 & dec_sn20)).sum()),
        "vsumd20_open_and_sumn20_open_days": int((vd20_open & sn20_open & (dec_vd20 & dec_sn20)).sum()),
        "vsumd20_open_and_rsqr20_closed_days": int((vd20_open & (~r20_open & dec_r20) & (dec_vd20 & dec_r20)).sum()),
        "note": "vsumd_open while W13 SUMN reads opposite = volume-direction WITHOUT price-direction "
                "agreement (accumulation-into-chop face) = the construction divergence vs W13; "
                "near-zero counts = collapsed neighbor (VSTD20 precedent line)"}
    facts["distinct_space_increment_resi60"] = {
        "resi60_open_and_rsv60_low_days": int((re60_open & rsv_low & (dec_re60 & dec_rsv)).sum()),
        "resi60_open_and_rsv60_notlow_days": int((re60_open & (~rsv_low & dec_rsv) & (dec_re60 & dec_rsv)).sum()),
        "resi60_open_and_rsqr20_open_days": int((re60_open & r20_open & (dec_re60 & dec_r20)).sum()),
        "resi60_open_and_rsqr20_closed_days": int((re60_open & (~r20_open & dec_r20) & (dec_re60 & dec_r20)).sum()),
        "resi60_open_and_mom_closed_days": int((re60_open & (~mom_open & dec_mom) & (dec_re60 & dec_mom)).sum()),
        "note": "resi60_open while RSV60 low (deep 60d-range position) = above-trend stretch DESPITE "
                "range-oversold = trend-vs-range divergence face; resi60∧rsqr20_closed = stretched "
                "above a POORLY-fit trend (blowoff/noise face) vs ∧open = clean trend extension"}
    facts["distinct_space_increment_cntd5"] = {
        "cntd5_open_and_sumn20_closed_days": int((cd5_open & (~sn20_open & dec_sn20) & (dec_cd5 & dec_sn20)).sum()),
        "cntd5_open_and_sumn20_open_days": int((cd5_open & sn20_open & (dec_cd5 & dec_sn20)).sum()),
        "cntd5_open_and_resi60_open_days": int((cd5_open & re60_open & (dec_cd5 & dec_re60)).sum()),
        "cntd5_open_and_upstreak_closed_days": int((cd5_open & (~up_st & st.notna()) & (dec_cd5 & st.notna())).sum()),
        "note": "cntd5_open while SUMN closed = up-day FREQUENCY without price-magnitude dominance "
                "(grind-of-small-gains face) = frequency-vs-purity divergence vs W13; near-zero = collapsed"}

    # ---- NINE-gate 512-cell crossing (each new face as the 9th, W13 pattern) --
    def grid9(face_open, face_dec, tag):
        cells = {}
        n_empty = 0
        m9 = (face_dec & bull.notna() & calm.notna() & amp_known & st.notna()
              & dec_mad & dec_rsv & dec_s20)
        for bname, b in (("bull", bull), ("bear", bear)):
            for vname, vv in (("calm", calm), ("wild", wild)):
                for yname, y in (("yang", yang), ("red", ~yang)):
                    for sname, s in (("surge", surge), ("dry", ~surge)):
                        for kname, k in (("up_streak", up_st), ("down_streak", dn_st)):
                            for tname, t in (("mad60", mad_q10), ("rsv60", rsv_low)):
                                for aname, a in (("wide", wide == 1), ("narrow", wide == 0)):
                                    for sdname, sd in (("std20_open", std20_open), ("std20_closed", ~std20_open & dec_s20)):
                                        for fname2, f2 in ((tag + "_open", face_open), (tag + "_closed", ~face_open & face_dec)):
                                            cnt = int((m9 & b & vv & y & s & k & t & a & sd & f2).sum())
                                            cells["%s|%s|%s|%s|%s|%s|%s|%s|%s" % (bname, vname, yname, sname, kname, tname, aname, sdname, fname2)] = cnt
                                            if cnt == 0:
                                                n_empty += 1
        return cells, n_empty, int(m9.sum())

    cells_vd, empty_vd, m9_vd = grid9(vd20_open, dec_vd20, "vsumd20")
    facts["vsumd20_nine_gate_512_cells_empty_count"] = empty_vd
    facts["vsumd20_nine_gate_512_cells_nonzero_count"] = 512 - empty_vd
    facts["vsumd20_nine_gate_512_cells_min_nonzero"] = min([x for x in cells_vd.values() if x > 0] or [0])
    facts["vsumd20_nine_gate_512_cells_max"] = max(cells_vd.values())
    facts["vsumd20_nine_gate_all_decidable_days"] = m9_vd
    facts["vsumd20_nine_gate_cells"] = cells_vd
    cells_re, empty_re, m9_re = grid9(re60_open, dec_re60, "resi60")
    facts["resi60_nine_gate_512_cells_empty_count"] = empty_re
    facts["resi60_nine_gate_512_cells_nonzero_count"] = 512 - empty_re
    facts["resi60_nine_gate_512_cells_min_nonzero"] = min([x for x in cells_re.values() if x > 0] or [0])
    facts["resi60_nine_gate_512_cells_max"] = max(cells_re.values())
    facts["resi60_nine_gate_all_decidable_days"] = m9_re
    facts["resi60_nine_gate_cells"] = cells_re
    cells_cd, empty_cd, m9_cd = grid9(cd5_open, dec_cd5, "cntd5")
    facts["cntd5_nine_gate_512_cells_empty_count"] = empty_cd
    facts["cntd5_nine_gate_512_cells_nonzero_count"] = 512 - empty_cd
    facts["cntd5_nine_gate_512_cells_min_nonzero"] = min([x for x in cells_cd.values() if x > 0] or [0])
    facts["cntd5_nine_gate_512_cells_max"] = max(cells_cd.values())
    facts["cntd5_nine_gate_all_decidable_days"] = m9_cd
    facts["cntd5_nine_gate_cells"] = cells_cd

    # ---- extreme days: state readout ------------------------------------------
    est = {}
    for dstr in EXTREME_DAYS:
        idx = df.index[df["date"] == dstr]
        if len(idx) == 0:
            est[dstr] = "not-in-panel"
            continue
        i = int(idx[0])
        est[dstr] = {
            "vsumd20_open": bool(vd20_open.iloc[i]) if dec_vd20.iloc[i] else None,
            "vsumd10_open": bool(vd10_open.iloc[i]) if dec_vd10.iloc[i] else None,
            "resi60_open": bool(re60_open.iloc[i]) if dec_re60.iloc[i] else None,
            "cntd5_open": bool(cd5_open.iloc[i]) if dec_cd5.iloc[i] else None,
            "cntn20_open": bool(cn20_open.iloc[i]) if dec_cn20.iloc[i] else None,
            "vsumd20_value": (None if pd.isna(vd20.iloc[i]) else round(float(vd20.iloc[i]), 6)),
            "resi60_value": (None if pd.isna(resi60.iloc[i]) else round(float(resi60.iloc[i]), 6)),
            "cntd5_value": (None if pd.isna(cd5.iloc[i]) else round(float(cd5.iloc[i]), 6)),
            "sumn20_open": bool(sn20_open.iloc[i]) if dec_sn20.iloc[i] else None,
            "std20_open": bool(std20_open.iloc[i]) if dec_s20.iloc[i] else None,
            "rsqr20_open": bool(r20_open.iloc[i]) if dec_r20.iloc[i] else None,
            "slope_sign": ("up" if (beta20.iloc[i] > 0) else "down") if (not pd.isna(beta20.iloc[i]) and dec_re60.iloc[i]) else None}
    facts["extreme_day_states"] = est

    # ---- census-style forward differential (descriptive, NOT a claim) ----------
    for fw in (5, 20):
        fwd = c.shift(-fw) / c - 1.0
        for tag, op, dec in (("vsumd20", vd20_open, dec_vd20), ("resi60", re60_open, dec_re60),
                             ("cntd5", cd5_open, dec_cd5), ("cntn20", cn20_open, dec_cn20)):
            base = dec & fwd.notna()
            a = fwd[op & base]
            b = fwd[(~op & dec) & base]
            facts[f"{tag}_forward_{fw}d"] = {
                "n_open": int(len(a)), "n_closed": int(len(b)),
                "mean_fwd_open": round(float(a.mean()), 6) if len(a) else float("nan"),
                "mean_fwd_closed": round(float(b.mean()), 6) if len(b) else float("nan"),
                "diff_open_minus_closed": round(float(a.mean() - b.mean()), 6) if (len(a) and len(b)) else float("nan"),
                "welch_t": tstats(a, b),
                "note": "descriptive probe face on 510300 anchor only; census/recheck universe "
                        "face = GATE-RECHECK CONFIRM five-member readings (VSUMD20_q90 net med "
                        "+0.01340 5/5, RESI60_q90 OOS med_t 1.178); NOT a strategy claim; "
                        "overlapping windows inflate |t|"}
    # grind decomposition (calm-vs-wild split, W13 honesty-face pattern)
    for tag, op, dec in (("vsumd20", vd20_open, dec_vd20), ("resi60", re60_open, dec_re60),
                         ("cntd5", cd5_open, dec_cd5)):
        fwd = c.shift(-20) / c - 1.0
        base = dec & fwd.notna() & med500.notna()
        a = fwd[op & calm & base]
        b = fwd[op & wild & base]
        facts[f"{tag}_grind_face_forward_20d"] = {
            "n_open_calm": int(len(a)), "n_open_wild": int(len(b)),
            "mean_fwd_open_calm": round(float(a.mean()), 6) if len(a) else float("nan"),
            "mean_fwd_open_wild": round(float(b.mean()), 6) if len(b) else float("nan"),
            "welch_t_calm_vs_wild": tstats(a, b),
            "note": "open days split by burned W4 VOL face: calm side = clean-grind increment "
                    "face; descriptive only"}
    # direction split (BETA20 sign, W13 honesty-face pattern)
    for tag, op, dec in (("vsumd20", vd20_open, dec_vd20), ("resi60", re60_open, dec_re60),
                         ("cntd5", cd5_open, dec_cd5)):
        fwd = c.shift(-20) / c - 1.0
        base = dec & fwd.notna() & beta20.notna()
        a = fwd[op & (beta20 > 0) & base]
        b = fwd[op & (beta20 <= 0) & base]
        facts[f"{tag}_direction_split_forward_20d"] = {
            "n_up_slope": int(len(a)), "n_down_slope": int(len(b)),
            "mean_fwd_up": round(float(a.mean()), 6) if len(a) else float("nan"),
            "mean_fwd_down": round(float(b.mean()), 6) if len(b) else float("nan"),
            "welch_t_up_vs_down": tstats(a, b),
            "note": "slope-split forward readout quantifies residual asymmetry of the "
                    "direction-loaded faces (VSUMD direction-LOADED like SUMN; RESI60 "
                    "sign-aware by construction)"}
    # resi60 fit-quality split (extension-with-fit vs blowoff, construction divergence core)
    fwd = c.shift(-20) / c - 1.0
    base = dec_re60 & fwd.notna() & dec_r20
    a = fwd[re60_open & r20_open & base]
    b = fwd[re60_open & (~r20_open & dec_r20) & base]
    facts["resi60_fit_quality_split_forward_20d"] = {
        "n_rsqr_open": int(len(a)), "n_rsqr_closed": int(len(b)),
        "mean_fwd_rsqr_open": round(float(a.mean()), 6) if len(a) else float("nan"),
        "mean_fwd_rsqr_closed": round(float(b.mean()), 6) if len(b) else float("nan"),
        "welch_t": tstats(a, b),
        "note": "resi60_open days split by W12 RSQR20: ∧open = clean trend extension "
                "(stretched above a WELL-fit trend), ∧closed = blowoff/noise (stretched above "
                "a poorly-fit trend) = the construction divergence vs W12; descriptive only"}

    # ---- core48 member-level open-rate spread (real roster) ---------------------
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    rates = {}
    rates_c = {}
    for sym, d2 in sorted(prices.items()):
        d2 = d2[d2.index <= cut]
        if len(d2) >= 260:
            di2 = pd.DataFrame({"open": d2["open"].to_numpy(), "high": d2["high"].to_numpy(),
                                "low": d2["low"].to_numpy(), "close": d2["close"].to_numpy(),
                                "volume": d2["volume"].to_numpy()},
                               index=pd.RangeIndex(len(d2)))
            F2 = a158.alpha158_factors(di2)
            op2, dv2, _ = hi_gate(F2["VSUMD20"])
            op2c, dv2c, _ = hi_gate(F2["CNTD5"])
            if dv2.any():
                rates[str(sym)] = round(float((op2 & dv2).mean()), 4)
            if dv2c.any():
                rates_c[str(sym)] = round(float((op2c & dv2c).mean()), 4)
    vals = sorted(rates.values())
    facts["core48_vsumd20_open_rate"] = {
        "n": len(vals),
        "min": round(vals[0], 4), "median": round(vals[len(vals) // 2], 4),
        "max": round(vals[-1], 4),
        "method": "tl1.load_core() roster (import-reuse via r237 lineage, real core48 face) "
                  "+ frozen-runner VSUMD verbatim",
        "members_with_lt260_rows_excluded": len(prices) - len(vals)}
    vals_c = sorted(rates_c.values())
    facts["core48_cntd5_open_rate"] = {
        "n": len(vals_c),
        "min": round(vals_c[0], 4), "median": round(vals_c[len(vals_c) // 2], 4),
        "max": round(vals_c[-1], 4),
        "method": "tl1.load_core() roster + frozen-runner CNTD5 verbatim",
        "members_with_lt260_rows_excluded": len(prices) - len(vals_c)}

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in facts.items() if not isinstance(v, dict)}, ensure_ascii=False))
    print("mirror_identity:", json.dumps(facts["mirror_identity"], ensure_ascii=False))
    for tag in ("vsumd20", "vsumd10", "resi60", "cntd5", "cntn20"):
        print(f"{tag} face: decidable", facts[f"{tag}_decidable_days"],
              "| open", facts[f"{tag}_open_days"], "| open_rate", facts[f"{tag}_open_rate_on_decidable"])
    print("vsumd20 slope split:", json.dumps(facts["vsumd20_open_slope_sign_split"], ensure_ascii=False))
    print("resi60 slope split:", json.dumps(facts["resi60_open_slope_sign_split"], ensure_ascii=False))
    print("cntd5 slope split:", json.dumps(facts["cntd5_open_slope_sign_split"], ensure_ascii=False))
    print("vsumd20 adjacency:", json.dumps(facts["adjacency_vsumd20"], ensure_ascii=False))
    print("resi60 adjacency:", json.dumps(facts["adjacency_resi60"], ensure_ascii=False))
    print("cntd5 adjacency:", json.dumps(facts["adjacency_cntd5"], ensure_ascii=False))
    print("vsumd20 distinct:", json.dumps(facts["distinct_space_increment_vsumd20"], ensure_ascii=False))
    print("resi60 distinct:", json.dumps(facts["distinct_space_increment_resi60"], ensure_ascii=False))
    for tag in ("vsumd20", "resi60", "cntd5"):
        print(f"{tag} fwd20d:", json.dumps(facts[f"{tag}_forward_20d"], ensure_ascii=False))
        print(f"{tag} fwd5d:", json.dumps(facts[f"{tag}_forward_5d"], ensure_ascii=False))
        print(f"{tag} grind:", json.dumps(facts[f"{tag}_grind_face_forward_20d"], ensure_ascii=False))
        print(f"{tag} dirsplit:", json.dumps(facts[f"{tag}_direction_split_forward_20d"], ensure_ascii=False))
        print(f"{tag} 512-cells: empty", facts[f"{tag}_nine_gate_512_cells_empty_count"],
              "| nonzero", facts[f"{tag}_nine_gate_512_cells_nonzero_count"],
              "| all-decidable", facts[f"{tag}_nine_gate_all_decidable_days"])
    print("cntn20 fwd20d:", json.dumps(facts["cntn20_forward_20d"], ensure_ascii=False))
    print("cntd5 distinct:", json.dumps(facts["distinct_space_increment_cntd5"], ensure_ascii=False))
    print("resi60 fit-split:", json.dumps(facts["resi60_fit_quality_split_forward_20d"], ensure_ascii=False))
    print("extreme days:", json.dumps(facts["extreme_day_states"], ensure_ascii=False))
    print("determinism_cross_checks:", json.dumps(facts["determinism_cross_checks"]))
    print("core48 vsumd20 open rate:", json.dumps(facts["core48_vsumd20_open_rate"], ensure_ascii=False))
    print("core48 cntd5 open rate:", json.dumps(facts["core48_cntd5_open_rate"], ensure_ascii=False))
    print("W14 VSUMD/RESI/CNTD pre-selection probe facts ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
