# -*- coding: utf-8 -*-
"""_r277bmc_resicnt_w14_probe.py -- W14 berth-holder supplementary probe:
RESI30_q90 / CNTD10_q90 anchor facts (the two member-set faces NOT covered by
bm-b r470's probe facts) + cross-machine twin cross-validation of the SHARED
faces (resi60/cntd5/cntn20) against results/_r470bmb_vsumd_resi_w14_probe_facts.json
(r98 twin-same-side law: same panel, same frozen runner, two machines ->
byte-equal readings) + CNTD_q90==CNTN_q10 mirror-twin XOR measurement
(W14 draft sec.2 note item: construction mirror expected near-same-day co-open,
zero-change-day boundary [CNTP+CNTN<=1 not identically 1] makes XOR non-
necessarily-zero = probe-measured item, NOT pre-written).

NOT results, NOT a strategy claim. Deterministic, zero network, read-only,
marks +0, SEED +0.

Berth context (MSG-20260930-154x-bmb-ALL adjudication): bm-c r276 = W14 drafting
berth holder (research/TRIAL_LABOR_W14_CANDIDATE_RESICNT_PREREG_DRAFT.md =
canonical candidate draft; bm-c member set = RESI{resi60_hi,resi30_hi} +
CNTD{cntd10_hi,cntd5_hi}); bm-b r470 adopted the freeze step and holds probe
facts for resi60/cntd5/cntn20 (+vsumd20 own-face). Gap faces for the freeze-step
adjudication = resi30_hi / cntd10_hi -> THIS probe. Freeze step itself stays
bm-b lane (yielded per MSG-154x sec.3).

Construction honesty (verbatim-import discipline, zero re-implementation):
  RESI/CNTD/CNTN/CNTP come from the FROZEN in-repo runner
  scripts/a158_tsgate_probe.py (import a158_tsgate_probe; F = alpha158_factors(df)):
    RESI%d  = last-point residual of rolling OLS(close, d) / close
    CNTP%d  = mean(up-day, d); CNTN%d = mean(down-day, d)
    CNTD%d  = CNTP%d - CNTN%d  (net up-day density dominance in [-1,1])
  Gate (A158_TSGATE_P1 prereg sec.2 frozen): high side
      f > f.rolling(252, min_periods=120).quantile(0.90)
  low side (CNTN mirror, W13 sumn_gate verbatim):
      f < f.rolling(252, min_periods=120).quantile(0.10)
  decidable = f.notna() & qref.notna() (pit-95/r431 NaN-bucket artifact law).
  Warmup fail-closed (measured + asserted): RESI family first-decidable idx 120
  (RESI[0] NaN: expanding k=1 -> Stt=0 guard; qref(252,min120) needs 120 non-NaN
  -> idx 120), CNT family first-decidable idx 119 (up/down-day indicator at idx
  0 = comparison-vs-NaN -> False -> 0.0 NOT NaN -> qref one bar earlier);
  honest one-bar construction-family divergence (r470 disclosure lineage).

Pool-turn lineage: TRIAL_LABOR_LAW sec.5 standing-supply channel, 48-PASS pool
(results/a158_tsgate_p1.json) unconsumed order after STD(W11)/RSQR(W12)/SUMN(W13):
RESI family (RESI60_q90 OOS med_t 1.178 highest unconsumed / RESI30_q90 0.433)
+ CNTD family (CNTD10_q90 1.016 / CNTD5_q90 0.815; mirror CNTN10_q10 1.013 /
CNTN5_q10 0.776). W14 draft = berth-holder canonical candidate (r276).
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
import a158_tsgate_probe as a158            # frozen runner (RESI/CNTD/CNTN verbatim)
import _r237bmc_stdq90_w11_probe as r237p   # frozen W11 probe (W3-W11 faces + tstats)
import _r456bma_sumnsump_w13_probe as w13p   # frozen W13 probe (sumn_gate verbatim)
import trial_labor_w1 as tl1                 # via r237 lineage (core48 loader)

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4-W13 probes
OUT = "results/_r277bmc_resicnt_w14_probe_facts.json"
R470_FACTS = "results/_r470bmb_vsumd_resi_w14_probe_facts.json"  # twin cross-val target
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
    (import-reuse, W12/W13/r470 probe lineage). Returns (open, decidable, qref)."""
    qref = f.rolling(a158.GATE_WIN, min_periods=a158.GATE_MINP).quantile(a158.QHIGH)
    dec = f.notna() & qref.notna()
    return (f > qref) & dec, dec, qref


def tstats(a, b):
    return r237p.tstats(a, b)  # frozen Welch-t helper (r237 verbatim, rounds 3)


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

    # ---- member-set faces (frozen-runner verbatim import; zero re-impl) ------
    di = pd.DataFrame({"open": o, "high": h, "low": l, "close": c, "volume": v},
                      index=pd.RangeIndex(n))
    F = a158.alpha158_factors(di)
    resi60, resi30 = F["RESI60"], F["RESI30"]
    cd10, cd5 = F["CNTD10"], F["CNTD5"]
    cn10, cn5, cn20 = F["CNTN10"], F["CNTN5"], F["CNTN20"]
    cp10, cp5 = F["CNTP10"], F["CNTP5"]
    beta20, rsqr20 = F["BETA20"], F["RSQR20"]

    re60_open, dec_re60, _ = hi_gate(resi60)   # r470 twin face 1
    re30_open, dec_re30, _ = hi_gate(resi30)   # GAP face 1 (this probe's core)
    cd10_open, dec_cd10, _ = hi_gate(cd10)      # GAP face 2 (this probe's core)
    cd5_open, dec_cd5, _ = hi_gate(cd5)        # r470 twin face 2
    cn10_open, dec_cn10, _ = w13p.sumn_gate(cn10)  # mirror twin of cd10 (q10 low)
    cn5_open, dec_cn5, _ = w13p.sumn_gate(cn5)     # mirror twin of cd5 (q10 low)
    cn20_open, dec_cn20, _ = w13p.sumn_gate(cn20)  # r470 twin face 3 (recompute)

    # warmup fail-closed (measured; family consistency + r470 disclosure parity)
    for tag, dec, first_expect in (("resi60", dec_re60, 120), ("resi30", dec_re30, 120),
                                   ("cntd10", dec_cd10, 119), ("cntd5", dec_cd5, 119),
                                   ("cntn10", dec_cn10, 119), ("cntn5", dec_cn5, 119),
                                   ("cntn20", dec_cn20, 119)):
        first_dec = int(np.argmax(dec.to_numpy()))
        assert first_dec == first_expect, f"{tag} first decidable {first_dec} != {first_expect}"
    assert int(dec_re60.sum()) == 3363, "resi60 decidable != 3363 (twin parity)"
    assert int(dec_re30.sum()) == 3363, "resi30 decidable != 3363 (family parity)"
    assert int(dec_cd10.sum()) == 3364, "cntd10 decidable != 3364 (family parity)"
    assert int(dec_cd5.sum()) == 3364, "cntd5 decidable != 3364 (twin parity)"
    assert int(dec_cn20.sum()) == 3364, "cntn20 decidable != 3364 (twin parity)"

    # internal spot-check vs direct window computation (W13/r470 probe discipline)
    cv = c.to_numpy(dtype=float)
    # RESI30[i] == (close[i] - ols_fit(t=1..30, y=close[i-29..i])[30]) / close[i]
    for i in (500, 2000):
        y = cv[i - 29: i + 1]
        t = np.arange(1, 31, dtype=float)
        b_ref, a_ref = np.polyfit(t, y, 1)  # polyfit returns [slope, intercept]
        resid = y[-1] - (a_ref + b_ref * 30.0)
        got = float(resi30.iloc[i]) * cv[i]
        assert abs(got - resid) < 1e-6, f"RESI30@{i} {got} != direct {resid}"
    # CNTD10[i] == mean(up-day,10d) - mean(down-day,10d); CNTN10[i] == mean(down-day,10d)
    up_d = (cv[1:] > cv[:-1]).astype(float)
    dn_d = (cv[1:] < cv[:-1]).astype(float)
    for i in (59, 500, 2000):
        w10u = up_d[i - 10:i].mean()
        w10d = dn_d[i - 10:i].mean()
        got = float(cd10.iloc[i])
        assert abs(got - (w10u - w10d)) < 1e-12, f"CNTD10@{i} {got} != direct {w10u - w10d}"
        got_n = float(cn10.iloc[i])
        assert abs(got_n - w10d) < 1e-12, f"CNTN10@{i} {got_n} != direct {w10d}"

    # ---- CNTD_q90 vs CNTN_q10 mirror-twin XOR (draft sec.2 note, measured) ----
    zero_chg_days = int((c == c.shift(1)).sum())

    facts = {"cutoff": CUTOFF, "rows": int(n), "first_date": str(df["date"].iloc[0]),
             "last_date": str(df["date"].iloc[-1]), "zero_range_rows": zero_amp,
             "zero_change_close_days_total": zero_chg_days,
             "probe_lineage": "W13 r456 + r470 probe paradigm; a158 frozen runner "
                              "verbatim-import (RESI/CNTD/CNTN face); berth-holder "
                              "supplementary probe for W14 freeze-step adjudication "
                              "(MSG-20260930-154x gap faces resi30/cntd10)",
             "construction_disclosure": {
                 "resi": "RESI%d=last-point residual of rolling OLS(close,%d)/close; "
                         "high-side gate = price stretched ABOVE own trend line "
                         "(trend-extension position face); RESI30 vs RESI60 = same "
                         "construction, 30d vs 60d window = intra-family window "
                         "redundancy face measured here; nearest burned neighbor = "
                         "W12 RSQR (same OLS, fit QUALITY) + W8 RSV60 (range position)",
                 "cntd": "CNTD%d=CNTP%d-CNTN%d net up-day density dominance in [-1,1]; "
                         "high-side gate = up-day FREQUENCY dominance window; vs W7 "
                         "STREAK (2d run continuity) / W13 SUMN (price-magnitude purity) "
                         "/ W10 MOM (speed); CNTD10 vs CNTD5 = intra-family window "
                         "redundancy face measured here",
                 "mirror": "CNTD_q90 vs CNTN_q10: if CNTP+CNTN==1 identically "
                           "(no unchanged-close days in window), CNTD=1-2*CNTN strictly "
                           "monotone -> gates fire SAME days (XOR=0); zero-change days "
                           "break the identity -> XOR>0 possible = measured, not pre-written"},

             "warmup_disclosure": "RESI family (resi60/resi30) first-decidable 120: RESI[0] "
                                  "NaN (expanding k=1 Stt=0 guard), qref(252,min120) needs "
                                  "120 non-NaN -> idx 120; CNT family (cntd/cntn) "
                                  "first-decidable 119 (idx-0 comparison-vs-NaN -> 0.0 not "
                                  "NaN -> one bar earlier); honest one-bar divergence (r470 "
                                  "disclosure lineage)"}

    for tag, dec, op in (("resi60", dec_re60, re60_open), ("resi30", dec_re30, re30_open),
                         ("cntd10", dec_cd10, cd10_open), ("cntd5", dec_cd5, cd5_open),
                         ("cntn10", dec_cn10, cn10_open), ("cntn5", dec_cn5, cn5_open),
                         ("cntn20", dec_cn20, cn20_open)):
        facts[f"{tag}_decidable_days"] = int(dec.sum())
        facts[f"{tag}_open_days"] = int((op & dec).sum())
        facts[f"{tag}_open_rate_on_decidable"] = round(float((op & dec).mean()), 4)

    # ---- mirror-twin XOR measurement (measured, honest; driver disclosed) ----
    mirror = {}
    for tag, cd_open, cd_dec, cn_open, cn_dec, cp, cn in (
            ("cntd10", cd10_open, dec_cd10, cn10_open, dec_cn10, cp10, cn10),
            ("cntd5", cd5_open, dec_cd5, cn5_open, dec_cn5, cp5, cn5)):
        m = cd_dec & cn_dec
        both = int((cd_open & cn_open & m).sum())
        xor = int((cd_open ^ cn_open).sum())
        cd_only = int((cd_open & ~cn_open & m).sum())
        cn_only = int((~cd_open & cn_open & m).sum())
        # driver split: among XOR days, those whose CURRENT d-window contains >=1
        # unchanged close (CNTP+CNTN < 1 - 1e-12) = the draft sec.2 boundary driver;
        # zerochange-free XOR days = quantile-REFERENCE divergence (trailing-252
        # history windows contain zerochange days -> q90(CNTD) != 1-2*q10(CNTN)).
        win_has_zero = ((cp + cn) < 1.0 - 1e-12) & m
        xor_mask = (cd_open ^ cn_open) & m
        mirror[tag + "_q90_vs_cntn" + tag[4:] + "_q10"] = {
            "joint_decidable_days": int(m.sum()),
            "both_open_days": both, "xor_days": xor,
            "cntd_only_days": cd_only, "cntn_only_days": cn_only,
            "joint_decidable_days_with_zerochange_in_window": int(win_has_zero.sum()),
            "xor_days_with_zerochange_in_window": int((xor_mask & win_has_zero).sum()),
            "xor_days_without_zerochange_in_window": int((xor_mask & ~win_has_zero).sum()),
            "note": "measured XOR is dominated by QUANTILE-REFERENCE divergence, not "
                    "current-window boundary: xor_days_without_zerochange counts XOR "
                    "days whose CURRENT d-window is zerochange-free (pointwise "
                    "CNTD=1-2*CNTN holds there), but the trailing-252 reference "
                    "windows contain zerochange-bearing history -> q90(CNTD) != "
                    "1-2*q10(CNTN) at reference level; zerochange-bearing CURRENT "
                    "windows (the draft sec.2 boundary) are the MINOR driver "
                    "(measured: 1/19 cntd10, 2/20 cntd5); near-mirror but not "
                    "identity -> CNTN_q10 pool readings are near-duplicates of the "
                    "CNTD face at ~9% open-day divergence, dedup handled downstream"}
    facts["mirror_twin_xor"] = mirror

    # ---- inherited burned faces (W3-W13 frozen modules verbatim) ------------
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

    # direction-loaded disclosure: slope-sign split among open days (member faces)
    for tag, op, dec in (("resi60", re60_open, dec_re60), ("resi30", re30_open, dec_re30),
                         ("cntd10", cd10_open, dec_cd10), ("cntd5", cd5_open, dec_cd5)):
        m_open = op & dec & beta20.notna()
        facts[f"{tag}_open_slope_sign_split"] = {
            "up_slope_days": int((m_open & (beta20 > 0)).sum()),
            "down_slope_days": int((m_open & (beta20 <= 0)).sum()),
            "note": "BETA20 sign from the same frozen runner; both RESI faces "
                    "sign-aware by construction (high residual = above-trend "
                    "stretch); CNTD faces direction-LOADED (up-day density)"}

    # ---- cross-machine twin cross-validation vs r470 facts (r98 law) ---------
    twin = {}
    if not os.path.exists(R470_FACTS):
        twin["r470"] = {"error": "facts file absent", "verdict": "FAIL"}
        raise SystemExit("twin target absent: " + R470_FACTS)
    r470 = json.load(open(R470_FACTS, encoding="utf-8"))
    ok, bad = 0, []
    def twin_eq(name, mine, theirs):
        nonlocal ok
        if mine == theirs:
            ok += 1
        else:
            bad.append({"face": name, "mine": mine, "r470": theirs})
    for tag in ("resi60", "cntd5", "cntn20"):
        twin_eq(tag + "_decidable", facts[tag + "_decidable_days"], r470[tag + "_decidable_days"])
        twin_eq(tag + "_open", facts[tag + "_open_days"], r470[tag + "_open_days"])
        twin_eq(tag + "_open_rate", facts[tag + "_open_rate_on_decidable"], r470[tag + "_open_rate_on_decidable"])
    # forward stats twin (recompute here, compare rounded scalars)
    fwd20 = c.shift(-20) / c - 1.0
    fwd5 = c.shift(-5) / c - 1.0
    for tag, op, dec in (("resi60", re60_open, dec_re60), ("cntd5", cd5_open, dec_cd5),
                         ("cntn20", cn20_open, dec_cn20)):
        base = dec & fwd20.notna()
        a_ = fwd20[op & base]
        b_ = fwd20[(~op & dec) & base]
        twin_eq(tag + "_fwd20_diff", round(float(a_.mean() - b_.mean()), 6),
                r470[tag + "_forward_20d"]["diff_open_minus_closed"])
        twin_eq(tag + "_fwd20_t", tstats(a_, b_), r470[tag + "_forward_20d"]["welch_t"])
        base5 = dec & fwd5.notna()
        a5 = fwd5[op & base5]
        b5 = fwd5[(~op & dec) & base5]
        twin_eq(tag + "_fwd5_diff", round(float(a5.mean() - b5.mean()), 6),
                r470[tag + "_forward_5d"]["diff_open_minus_closed"])
        twin_eq(tag + "_fwd5_t", tstats(a5, b5), r470[tag + "_forward_5d"]["welch_t"])
    # grind + direction + fit splits twin
    for tag, op, dec in (("resi60", re60_open, dec_re60), ("cntd5", cd5_open, dec_cd5)):
        base = dec & fwd20.notna() & med500.notna()
        a_ = fwd20[op & calm & base]
        b_ = fwd20[op & wild & base]
        twin_eq(tag + "_grind_calm_mean", round(float(a_.mean()), 6),
                r470[tag + "_grind_face_forward_20d"]["mean_fwd_open_calm"])
        twin_eq(tag + "_grind_wild_mean", round(float(b_.mean()), 6),
                r470[tag + "_grind_face_forward_20d"]["mean_fwd_open_wild"])
        twin_eq(tag + "_grind_t", tstats(a_, b_),
                r470[tag + "_grind_face_forward_20d"]["welch_t_calm_vs_wild"])
        base = dec & fwd20.notna() & beta20.notna()
        a_ = fwd20[op & (beta20 > 0) & base]
        b_ = fwd20[op & (beta20 <= 0) & base]
        twin_eq(tag + "_dirsplit_up_mean", round(float(a_.mean()), 6),
                r470[tag + "_direction_split_forward_20d"]["mean_fwd_up"])
        twin_eq(tag + "_dirsplit_down_mean", round(float(b_.mean()), 6),
                r470[tag + "_direction_split_forward_20d"]["mean_fwd_down"])
        twin_eq(tag + "_dirsplit_t", tstats(a_, b_),
                r470[tag + "_direction_split_forward_20d"]["welch_t_up_vs_down"])
    base = dec_re60 & fwd20.notna() & dec_r20
    a_ = fwd20[re60_open & r20_open & base]
    b_ = fwd20[re60_open & (~r20_open & dec_r20) & base]
    twin_eq("resi60_fit_open_mean", round(float(a_.mean()), 6),
            r470["resi60_fit_quality_split_forward_20d"]["mean_fwd_rsqr_open"])
    twin_eq("resi60_fit_closed_mean", round(float(b_.mean()), 6),
            r470["resi60_fit_quality_split_forward_20d"]["mean_fwd_rsqr_closed"])
    twin_eq("resi60_fit_t", tstats(a_, b_),
            r470["resi60_fit_quality_split_forward_20d"]["welch_t"])
    facts["twin_cross_validation_r470"] = {
        "checks_passed": ok, "checks_failed": len(bad),
        "failed_detail": bad,
        "verdict": "PASS" if not bad else "FAIL",
        "note": "r98 twin-same-side law: bm-c recompute vs bm-b r470 facts on "
                "shared faces (resi60/cntd5/cntn20 gate counts + forward/grind/"
                "dirsplit/fit rounded scalars); same panel + same frozen runner "
                "-> byte-equal expected; any drift = escalation face"}
    assert not bad, "twin cross-validation FAIL: " + json.dumps(bad, ensure_ascii=False)

    # ---- open-rate inside each inherited gate (member faces) ------------------
    def rate(mask_in, gate, dec):
        both = int((mask_in & gate).sum())
        base = int((mask_in & dec).sum())
        return round(100.0 * both / base, 2) if base else float("nan")

    for tag, op, dec in (("resi60", re60_open, dec_re60), ("resi30", re30_open, dec_re30),
                         ("cntd10", cd10_open, dec_cd10), ("cntd5", cd5_open, dec_cd5)):
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
            "sumn20_open": rate(sn20_open & dec_sn20, op, dec & dec_sn20), "sumn20_closed": rate((~sn20_open & dec_sn20), op, dec & dec_sn20),
            "resi60_open": rate(re60_open & dec_re60, op, dec & dec_re60), "resi30_open": rate(re30_open & dec_re30, op, dec & dec_re30),
            "cntd10_open": rate(cd10_open & dec_cd10, op, dec & dec_cd10), "cntd5_open": rate(cd5_open & dec_cd5, op, dec & dec_cd5)}
    # cross-face rates (intra-family + resi x cntd)
    facts["cross_new_face_rates"] = {
        "resi30_open_rate_when_resi60_open": rate(re60_open & dec_re60, re30_open, dec_re30 & dec_re60),
        "resi60_open_rate_when_resi30_open": rate(re30_open & dec_re30, re60_open, dec_re60 & dec_re30),
        "cntd10_open_rate_when_cntd5_open": rate(cd5_open & dec_cd5, cd10_open, dec_cd10 & dec_cd5),
        "cntd5_open_rate_when_cntd10_open": rate(cd10_open & dec_cd10, cd5_open, dec_cd5 & dec_cd10),
        "cntd10_open_rate_when_resi30_open": rate(re30_open & dec_re30, cd10_open, dec_cd10 & dec_re30),
        "resi30_open_rate_when_cntd10_open": rate(cd10_open & dec_cd10, re30_open, dec_re30 & dec_cd10),
        "cntd10_open_rate_when_resi60_open": rate(re60_open & dec_re60, cd10_open, dec_cd10 & dec_re60)}

    # ---- neighbor adjacency cross cells (THE freeze-step adjudication faces) --
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

    adj_r30 = {
        "resi30_vs_resi60": cell(re30_open, dec_re30, re60_open, dec_re60),
        "resi30_vs_wild": cell(re30_open, dec_re30, wild, med500.notna()),
        "resi30_vs_calm": cell(re30_open, dec_re30, calm, med500.notna()),
        "resi30_vs_wide": cell(re30_open, dec_re30, wide == 1, amp_known),
        "resi30_vs_narrow": cell(re30_open, dec_re30, wide == 0, amp_known),
        "resi30_vs_mad60": cell(re30_open, dec_re30, mad_q10, dec_mad),
        "resi30_vs_rsv60": cell(re30_open, dec_re30, rsv_low, dec_rsv),
        "resi30_vs_downstreak": cell(re30_open, dec_re30, dn_st, st.notna()),
        "resi30_vs_upstreak": cell(re30_open, dec_re30, up_st, st.notna()),
        "resi30_vs_mom": cell(re30_open, dec_re30, mom_open, dec_mom),
        "resi30_vs_std20": cell(re30_open, dec_re30, std20_open, dec_s20),
        "resi30_vs_rsqr20": cell(re30_open, dec_re30, r20_open, dec_r20),
        "resi30_vs_sumn20": cell(re30_open, dec_re30, sn20_open, dec_sn20),
        "resi30_vs_cntd10": cell(re30_open, dec_re30, cd10_open, dec_cd10),
        "resi30_vs_bull": cell(re30_open, dec_re30, bull, ma200.notna()),
        "resi30_vs_bear": cell(re30_open, dec_re30, bear, ma200.notna())}
    facts["adjacency_resi30"] = adj_r30
    adj_c10 = {
        "cntd10_vs_cntd5": cell(cd10_open, dec_cd10, cd5_open, dec_cd5),
        "cntd10_vs_wild": cell(cd10_open, dec_cd10, wild, med500.notna()),
        "cntd10_vs_calm": cell(cd10_open, dec_cd10, calm, med500.notna()),
        "cntd10_vs_wide": cell(cd10_open, dec_cd10, wide == 1, amp_known),
        "cntd10_vs_narrow": cell(cd10_open, dec_cd10, wide == 0, amp_known),
        "cntd10_vs_mad60": cell(cd10_open, dec_cd10, mad_q10, dec_mad),
        "cntd10_vs_rsv60": cell(cd10_open, dec_cd10, rsv_low, dec_rsv),
        "cntd10_vs_downstreak": cell(cd10_open, dec_cd10, dn_st, st.notna()),
        "cntd10_vs_upstreak": cell(cd10_open, dec_cd10, up_st, st.notna()),
        "cntd10_vs_mom": cell(cd10_open, dec_cd10, mom_open, dec_mom),
        "cntd10_vs_std20": cell(cd10_open, dec_cd10, std20_open, dec_s20),
        "cntd10_vs_rsqr20": cell(cd10_open, dec_cd10, r20_open, dec_r20),
        "cntd10_vs_sumn20": cell(cd10_open, dec_cd10, sn20_open, dec_sn20),
        "cntd10_vs_resi30": cell(cd10_open, dec_cd10, re30_open, dec_re30),
        "cntd10_vs_resi60": cell(cd10_open, dec_cd10, re60_open, dec_re60),
        "cntd10_vs_surge": cell(cd10_open, dec_cd10, surge, med20v.notna()),
        "cntd10_vs_yang": cell(cd10_open, dec_cd10, yang, pd.Series(np.ones(n, dtype=bool), index=c.index))}
    facts["adjacency_cntd10"] = adj_c10

    # distinct-space increment faces (r228 "mom-only days" pattern)
    facts["distinct_space_increment_resi30"] = {
        "resi30_open_and_resi60_closed_days": int((re30_open & (~re60_open & dec_re60) & (dec_re30 & dec_re60)).sum()),
        "resi30_open_and_resi60_open_days": int((re30_open & re60_open & (dec_re30 & dec_re60)).sum()),
        "resi30_open_and_rsqr20_closed_days": int((re30_open & (~r20_open & dec_r20) & (dec_re30 & dec_r20)).sum()),
        "resi30_open_and_rsqr20_open_days": int((re30_open & r20_open & (dec_re30 & dec_r20)).sum()),
        "resi30_open_and_mom_closed_days": int((re30_open & (~mom_open & dec_mom) & (dec_re30 & dec_mom)).sum()),
        "resi30_open_and_rsv60_notlow_days": int((re30_open & (~rsv_low & dec_rsv) & (dec_re30 & dec_rsv)).sum()),
        "note": "resi30_open while resi60 closed = short-window stretch WITHOUT "
                "long-window stretch (recent acceleration inside a flat/below 60d "
                "trend) = the intra-family increment face; near-zero = collapsed "
                "neighbor of resi60 (drop-candidate for freeze step)"}
    facts["distinct_space_increment_cntd10"] = {
        "cntd10_open_and_cntd5_closed_days": int((cd10_open & (~cd5_open & dec_cd5) & (dec_cd10 & dec_cd5)).sum()),
        "cntd10_open_and_cntd5_open_days": int((cd10_open & cd5_open & (dec_cd10 & dec_cd5)).sum()),
        "cntd10_open_and_sumn20_closed_days": int((cd10_open & (~sn20_open & dec_sn20) & (dec_cd10 & dec_sn20)).sum()),
        "cntd10_open_and_sumn20_open_days": int((cd10_open & sn20_open & (dec_cd10 & dec_sn20)).sum()),
        "cntd10_open_and_upstreak_closed_days": int((cd10_open & (~up_st & st.notna()) & (dec_cd10 & st.notna())).sum()),
        "cntd10_open_and_resi30_open_days": int((cd10_open & re30_open & (dec_cd10 & dec_re30)).sum()),
        "note": "cntd10_open while cntd5 closed = sustained density WITHOUT "
                "5d-burst = persistence-vs-burst divergence; cntd10_open while "
                "SUMN closed = up-day FREQUENCY without price-magnitude dominance "
                "(grind-of-small-gains face) vs W13"}

    # ---- NINE-gate 512-cell crossing (gap faces as the 9th, W13/r470 pattern) -
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

    for tag, op, dec in (("resi30", re30_open, dec_re30), ("cntd10", cd10_open, dec_cd10)):
        cells_x, empty_x, m9_x = grid9(op, dec, tag)
        facts[f"{tag}_nine_gate_512_cells_empty_count"] = empty_x
        facts[f"{tag}_nine_gate_512_cells_nonzero_count"] = 512 - empty_x
        facts[f"{tag}_nine_gate_512_cells_min_nonzero"] = min([x for x in cells_x.values() if x > 0] or [0])
        facts[f"{tag}_nine_gate_512_cells_max"] = max(cells_x.values())
        facts[f"{tag}_nine_gate_all_decidable_days"] = m9_x
        facts[f"{tag}_nine_gate_cells"] = cells_x
    # 512-grid twin check for resi60 (shared face, r470 has grid)
    cells_r60, empty_r60, m9_r60 = grid9(re60_open, dec_re60, "resi60")
    twin_eq("resi60_512_empty", empty_r60, r470["resi60_nine_gate_512_cells_empty_count"])
    twin_eq("resi60_512_max", max(cells_r60.values()), r470["resi60_nine_gate_512_cells_max"])
    twin_eq("resi60_512_all_dec", m9_r60, r470["resi60_nine_gate_all_decidable_days"])
    facts["twin_cross_validation_r470"]["checks_passed"] = ok
    facts["twin_cross_validation_r470"]["checks_failed"] = len(bad)
    facts["twin_cross_validation_r470"]["failed_detail"] = bad
    assert not bad, "512-grid twin FAIL: " + json.dumps(bad, ensure_ascii=False)

    # ---- extreme days: state readout ------------------------------------------
    est = {}
    for dstr in EXTREME_DAYS:
        idx = df.index[df["date"] == dstr]
        if len(idx) == 0:
            est[dstr] = "not-in-panel"
            continue
        i = int(idx[0])
        est[dstr] = {
            "resi60_open": bool(re60_open.iloc[i]) if dec_re60.iloc[i] else None,
            "resi30_open": bool(re30_open.iloc[i]) if dec_re30.iloc[i] else None,
            "cntd10_open": bool(cd10_open.iloc[i]) if dec_cd10.iloc[i] else None,
            "cntd5_open": bool(cd5_open.iloc[i]) if dec_cd5.iloc[i] else None,
            "cntn10_open": bool(cn10_open.iloc[i]) if dec_cn10.iloc[i] else None,
            "resi60_value": (None if pd.isna(resi60.iloc[i]) else round(float(resi60.iloc[i]), 6)),
            "resi30_value": (None if pd.isna(resi30.iloc[i]) else round(float(resi30.iloc[i]), 6)),
            "cntd10_value": (None if pd.isna(cd10.iloc[i]) else round(float(cd10.iloc[i]), 6)),
            "cntd5_value": (None if pd.isna(cd5.iloc[i]) else round(float(cd5.iloc[i]), 6)),
            "sumn20_open": bool(sn20_open.iloc[i]) if dec_sn20.iloc[i] else None,
            "std20_open": bool(std20_open.iloc[i]) if dec_s20.iloc[i] else None,
            "rsqr20_open": bool(r20_open.iloc[i]) if dec_r20.iloc[i] else None,
            "slope_sign": ("up" if (beta20.iloc[i] > 0) else "down") if (not pd.isna(beta20.iloc[i]) and dec_re30.iloc[i]) else None}
    facts["extreme_day_states"] = est

    # ---- census-style forward differential (descriptive, NOT a claim) ----------
    for fw in (5, 20):
        fwd = c.shift(-fw) / c - 1.0
        for tag, op, dec in (("resi30", re30_open, dec_re30), ("cntd10", cd10_open, dec_cd10)):
            base = dec & fwd.notna()
            a_ = fwd[op & base]
            b_ = fwd[(~op & dec) & base]
            facts[f"{tag}_forward_{fw}d"] = {
                "n_open": int(len(a_)), "n_closed": int(len(b_)),
                "mean_fwd_open": round(float(a_.mean()), 6) if len(a_) else float("nan"),
                "mean_fwd_closed": round(float(b_.mean()), 6) if len(b_) else float("nan"),
                "diff_open_minus_closed": round(float(a_.mean() - b_.mean()), 6) if (len(a_) and len(b_)) else float("nan"),
                "welch_t": tstats(a_, b_),
                "note": "descriptive probe face on 510300 anchor only; pool/recheck "
                        "universe face = GATE-RECHECK CONFIRM readings (RESI30_q90 "
                        "OOS 0.433 / CNTD10_q90 1.016); NOT a strategy claim; "
                        "overlapping windows inflate |t|"}
    # grind decomposition (calm-vs-wild split, W13/r470 honesty-face pattern)
    fwd = c.shift(-20) / c - 1.0
    for tag, op, dec in (("resi30", re30_open, dec_re30), ("cntd10", cd10_open, dec_cd10)):
        base = dec & fwd.notna() & med500.notna()
        a_ = fwd[op & calm & base]
        b_ = fwd[op & wild & base]
        facts[f"{tag}_grind_face_forward_20d"] = {
            "n_open_calm": int(len(a_)), "n_open_wild": int(len(b_)),
            "mean_fwd_open_calm": round(float(a_.mean()), 6) if len(a_) else float("nan"),
            "mean_fwd_open_wild": round(float(b_.mean()), 6) if len(b_) else float("nan"),
            "welch_t_calm_vs_wild": tstats(a_, b_),
            "note": "open days split by burned W4 VOL face: calm side = clean-grind "
                    "increment face; descriptive only"}
    # direction split (BETA20 sign)
    for tag, op, dec in (("resi30", re30_open, dec_re30), ("cntd10", cd10_open, dec_cd10)):
        base = dec & fwd.notna() & beta20.notna()
        a_ = fwd[op & (beta20 > 0) & base]
        b_ = fwd[op & (beta20 <= 0) & base]
        facts[f"{tag}_direction_split_forward_20d"] = {
            "n_up_slope": int(len(a_)), "n_down_slope": int(len(b_)),
            "mean_fwd_up": round(float(a_.mean()), 6) if len(a_) else float("nan"),
            "mean_fwd_down": round(float(b_.mean()), 6) if len(b_) else float("nan"),
            "welch_t_up_vs_down": tstats(a_, b_),
            "note": "slope-split forward readout quantifies residual asymmetry"}
    # resi30 fit-quality split (extension-with-fit vs blowoff)
    base = dec_re30 & fwd.notna() & dec_r20
    a_ = fwd[re30_open & r20_open & base]
    b_ = fwd[re30_open & (~r20_open & dec_r20) & base]
    facts["resi30_fit_quality_split_forward_20d"] = {
        "n_rsqr_open": int(len(a_)), "n_rsqr_closed": int(len(b_)),
        "mean_fwd_rsqr_open": round(float(a_.mean()), 6) if len(a_) else float("nan"),
        "mean_fwd_rsqr_closed": round(float(b_.mean()), 6) if len(b_) else float("nan"),
        "welch_t": tstats(a_, b_),
        "note": "resi30_open days split by W12 RSQR20: ∧open = clean trend "
                "extension, ∧closed = blowoff/noise; descriptive only"}

    # ---- core48 member-level open-rate spread (real roster) ---------------------
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    rates_r30 = {}
    rates_c10 = {}
    for sym, d2 in sorted(prices.items()):
        d2 = d2[d2.index <= cut]
        if len(d2) >= 260:
            di2 = pd.DataFrame({"open": d2["open"].to_numpy(), "high": d2["high"].to_numpy(),
                                "low": d2["low"].to_numpy(), "close": d2["close"].to_numpy(),
                                "volume": d2["volume"].to_numpy()},
                               index=pd.RangeIndex(len(d2)))
            F2 = a158.alpha158_factors(di2)
            op_r, dv_r, _ = hi_gate(F2["RESI30"])
            op_c, dv_c, _ = hi_gate(F2["CNTD10"])
            if dv_r.any():
                rates_r30[str(sym)] = round(float((op_r & dv_r).mean()), 4)
            if dv_c.any():
                rates_c10[str(sym)] = round(float((op_c & dv_c).mean()), 4)
    for key, vals, label in (("core48_resi30_open_rate", rates_r30, "RESI30"),
                             ("core48_cntd10_open_rate", rates_c10, "CNTD10")):
        vs = sorted(vals.values())
        facts[key] = {
            "n": len(vs),
            "min": round(vs[0], 4) if vs else None,
            "median": round(vs[len(vs) // 2], 4) if vs else None,
            "max": round(vs[-1], 4) if vs else None,
            "method": "tl1.load_core() roster (import-reuse via r237 lineage) + "
                      "frozen-runner " + label + " verbatim",
            "members_with_lt260_rows_excluded": len(prices) - len(vs)}

    # ---- determinism cross-check vs frozen probe facts (nine lineage files) ----
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
        for gname in ("RESI30_q90", "RESI60_q90", "CNTD10_q90", "CNTD5_q90",
                      "CNTN10_q10", "CNTN5_q10"):
            try:
                ref = gr["gates"][gname]["face_a"]["members"]["510300"]
                refs[gname] = {"n_in_ref": ref["n_in"], "n_out_ref": ref["n_out"]}
            except Exception as e:
                refs[gname] = {"error": str(e)}
        xchecks["gate_recheck_ref"] = {**refs,
            "note": "five-member secondary face different member-panel loading; "
                    "disclosure reference NOT fail-closed (r470 same disclosure)"}
    facts["determinism_cross_checks"] = xchecks

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in facts.items() if not isinstance(v, dict)}, ensure_ascii=False))
    print("mirror_twin_xor:", json.dumps(facts["mirror_twin_xor"], ensure_ascii=False))
    print("twin_cross_validation_r470:", json.dumps({k: v for k, v in facts["twin_cross_validation_r470"].items() if k != "failed_detail"}, ensure_ascii=False))
    for tag in ("resi30", "cntd10", "resi60", "cntd5"):
        print(f"{tag} face: decidable", facts[f"{tag}_decidable_days"],
              "| open", facts[f"{tag}_open_days"], "| open_rate", facts[f"{tag}_open_rate_on_decidable"])
    print("resi30 slope split:", json.dumps(facts["resi30_open_slope_sign_split"], ensure_ascii=False))
    print("cntd10 slope split:", json.dumps(facts["cntd10_open_slope_sign_split"], ensure_ascii=False))
    print("adjacency resi30_vs_resi60:", json.dumps(facts["adjacency_resi30"]["resi30_vs_resi60"], ensure_ascii=False))
    print("adjacency cntd10_vs_cntd5:", json.dumps(facts["adjacency_cntd10"]["cntd10_vs_cntd5"], ensure_ascii=False))
    print("distinct resi30:", json.dumps(facts["distinct_space_increment_resi30"], ensure_ascii=False))
    print("distinct cntd10:", json.dumps(facts["distinct_space_increment_cntd10"], ensure_ascii=False))
    for tag in ("resi30", "cntd10"):
        print(f"{tag} fwd20d:", json.dumps(facts[f"{tag}_forward_20d"], ensure_ascii=False))
        print(f"{tag} fwd5d:", json.dumps(facts[f"{tag}_forward_5d"], ensure_ascii=False))
        print(f"{tag} grind:", json.dumps(facts[f"{tag}_grind_face_forward_20d"], ensure_ascii=False))
        print(f"{tag} dirsplit:", json.dumps(facts[f"{tag}_direction_split_forward_20d"], ensure_ascii=False))
        print(f"{tag} 512-cells: empty", facts[f"{tag}_nine_gate_512_cells_empty_count"],
              "| nonzero", facts[f"{tag}_nine_gate_512_cells_nonzero_count"],
              "| all-decidable", facts[f"{tag}_nine_gate_all_decidable_days"])
    print("resi30 fit-split:", json.dumps(facts["resi30_fit_quality_split_forward_20d"], ensure_ascii=False))
    print("extreme days:", json.dumps(facts["extreme_day_states"], ensure_ascii=False))
    print("determinism_cross_checks:", json.dumps(facts["determinism_cross_checks"]))
    print("core48 resi30 open rate:", json.dumps(facts["core48_resi30_open_rate"], ensure_ascii=False))
    print("core48 cntd10 open rate:", json.dumps(facts["core48_cntd10_open_rate"], ensure_ascii=False))
    print("W14 berth-holder supplementary probe facts (resi30/cntd10 gap faces + r470 twin cross-val) ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
