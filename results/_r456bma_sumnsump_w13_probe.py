# -*- coding: utf-8 -*-
"""_r456bma_sumnsump_w13_probe.py -- W13 pre-selection probe: A158-TSGATE-P1
48-PASS pool next-top family SUMN20_q10 / SUMN10_q10 (up-share purity side,
GATE-RECHECK-CONFIRM #20/#21 reps; mirror-twin cluster SUMP_q90/SUMD_q90 same
days) raw-face facts on the 510300 anchor. NOT results, NOT a strategy claim.

W13 supply-prep slice per TRIAL_LABOR_LAW sec.1 standing-supply step
(r456 bm-a). Pre-commitment window note (research/DECISION_CHAIN.md sec.4.7
v1.2: next-wave hypotheses must be frozen BEFORE the previous wave verdict
lands; W12 GENERATE just pool-enqueued on the bm-b lane (runner built r445,
frozen prereg r444) with verdict far away = the W13 berth window is open;
W10/W11/W12 themselves were berthed pre-verdict per the same cadence,
r228/r237/r447 three-precedent run).

Pool-turn lineage (r234 digest sec.3 named-pool pointer): census four
positive families all consumed (MAD60/RSV60->W8, ROC20->W10, VSTD20->DEMOTE)
-> 48-PASS pool order STD->RSQR->SUMN/SUMP (STD consumed by W11, RSQR by
W12, both frozen) -> NEXT = SUMN/SUMP (up-share family).

The deferral question this probe answers:
  does the SUMN low-side gate (up-share of absolute movement high = few
  down-parts over the window = DIRECTIONAL purity face) open a DISTINCT
  day-level conditional space from the burned trial-grammar axes -- esp.
  W12 RSQR (fit QUALITY, sign-blind) and W11 STD (price-level dispersion),
  all three being "trend-state" neighbors -- or is it a collapsed neighbor
  like VSTD20_q20 was (98.5% inside W4 calm, r234 DEMOTE)?

Construction honesty (verbatim-import discipline, zero re-implementation):
  SUMN/SUMP/SUMD come from the FROZEN in-repo runner scripts/a158_tsgate_probe.py
  (bm-a r438/439 burn face) -- import a158_tsgate_probe; F = alpha158_factors(df);
  SUMN%d = sum(clip(-diff,0), d) / sum(|diff|, d)  (down-share, in [0,1])
  SUMP%d = sum(clip(+diff,0), d) / sum(|diff|, d)  (up-share, in [0,1])
  => SUMN + SUMP == 1 identically (mirror twins; SUMP%d_q90 fires on the SAME
  days as SUMN%d_q10 -- cluster #20/#21 corr 1.000, empirically verified here).
  Inherited W3-W12 faces come from the frozen probe modules
  (results/_r237bmc_stdq90_w11_probe.py verbatim + r447 RSQR faces rebuilt from
  the same frozen runner import -- zero re-implementation anywhere).
  Gate (A158_TSGATE_P1 prereg sec.2 frozen): low side
      f < f.rolling(252, min_periods=120).quantile(0.10)
  decidable = f.notna() & qref.notna() (pit-95/r431 NaN-bucket artifact law).
  Warmup: f[idx0]=NaN (diff undefined) -> f valid from bar-idx 1 -> qref first
  valid at bar-idx 120 (same construction family as RSQR/STD, asserted
  fail-closed).

Direction disclosure (SUMN-specific honesty, OPPOSITE of RSQR's sign-blind
note): the up-share axis is direction-LOADED -- q10-of-SUMN selects
UP-dominant windows by construction (down-share in own low decile). The
bearish mirror (SUMN_q90 / SUMP_q10, down-dominant windows) NEVER passed the
48-PASS census (absent from the confirm registry -- honest supply face).
Direction conditioning interplay with burned GATE/YANG/STREAK/MOM axes is
therefore a REAL redundancy question, measured by the adjacency cells below.

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
sys.path.insert(0, os.path.join("results"))
import a158_tsgate_probe as a158            # frozen runner (SUMN/SUMP verbatim)
import _r237bmc_stdq90_w11_probe as r237p   # frozen W11 probe (W3-W11 faces)
import trial_labor_w1 as tl1                # via r237p lineage (core48 loader)

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4-W12 probes
OUT = "results/_r456bma_sumnsump_w13_probe_facts.json"
R417_FACTS = "results/_r417bmb_ampgate_probe_facts.json"
R423_FACTS = "results/_r423bmb_w8tstate_probe_facts.json"
R431_FACTS = "results/_r431bmb_ampgate_w9_probe_facts.json"
R228_FACTS = "results/_r228bmc_momgate_w10_probe_facts.json"
R234_FACTS = "results/_r234bmc_vstd20_w11_probe_facts.json"
R237_FACTS = "results/_r237bmc_stdq90_w11_probe_facts.json"
R447_FACTS = "results/_r447bma_rsqr_w12_probe_facts.json"
GATE_RECHECK = "results/gate_recheck_a158.json"

EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]


def sumn_gate(f, qlo_side=None):
    """A158_TSGATE_P1 frozen gate semantics via runner constants (import-reuse).
    Low side: f < rolling q10. Returns (open, decidable, qref)."""
    qref = f.rolling(a158.GATE_WIN, min_periods=a158.GATE_MINP).quantile(a158.QLOW)
    dec = f.notna() & qref.notna()
    return (f < qref) & dec, dec, qref


def rsqr_gate_hi(f):
    """W12 frozen high-side gate (r447 verbatim face, same runner constants)."""
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
    assert n == 3483, f"row count {n} != 3483 (W4-W12 probe anchor)"
    assert df["date"].iloc[-1] == CUTOFF, "last row != cutoff"
    zero_amp = int((df["high"] == df["low"]).sum())  # flat-line day (halt face)
    assert zero_amp == 0, "zero-range rows != 0 (r417 anchor)"

    c, h, l, v, o = (df[k] for k in ("close", "high", "low", "volume", "open"))

    # ---- SUMN/SUMP faces (frozen-runner verbatim import; zero re-implementation) ----
    di = pd.DataFrame({"open": o, "high": h, "low": l, "close": c, "volume": v},
                      index=pd.RangeIndex(n))
    F = a158.alpha158_factors(di)
    sn20, sn10, sp20, beta20 = F["SUMN20"], F["SUMN10"], F["SUMP20"], F["BETA20"]
    sn20_open, dec_sn20, q10_20 = sumn_gate(sn20)
    sn10_open, dec_sn10, q10_10 = sumn_gate(sn10)

    # warmup fail-closed: f valid from idx 1 (diff[0] undefined) -> qref
    # (252, min120) first valid at bar-idx 120 == RSQR/STD family warmup
    for tag, dec in (("sumn20", dec_sn20), ("sumn10", dec_sn10)):
        first_dec = int(np.argmax(dec.to_numpy()))
        assert first_dec == 120, f"{tag} first decidable {first_dec} != 120"

    # internal spot-check vs direct window computation (mirrors r447
    # RSQR-vs-corr^2 face): SUMNd[i] == sum(loss[i-d+1..i]) / (sum(|d|[..]) + eps)
    # -- the frozen runner uses an eps=1e-12 denominator guard, included here;
    # residual diff is pure float summation-order noise (~1e-16)
    cv = c.to_numpy(dtype=float)
    for d_win, series in ((10, sn10), (20, sn20)):
        for i in (59, 500, 2000):
            w = cv[i - d_win + 1: i + 1] - cv[i - d_win: i]
            got = float(series.iloc[i])
            ref = float(np.clip(-w, 0, None).sum() / (np.abs(w).sum() + 1e-12))
            assert abs(got - ref) < 1e-12, f"SUMN{d_win}@{i} {got} != direct {ref}"

    # mirror-twin identity: SUMN + SUMP == 1 (construction), and the q90-side
    # SUMP gate fires on the SAME days as the q10-side SUMN gate (cluster
    # #20/#21 corr 1.000 empirical proof, this panel)
    for d_win, sn_series, sp_series in ((20, sn20, sp20),):
        both = (sn_series + sp_series).dropna()
        assert float((both - 1.0).abs().max()) < 1e-9, "SUMN+SUMP != 1 (eps face)"
        sp_hi_open, _, _ = rsqr_gate_hi(sp_series)  # QHIGH-side reuse for SUMP>q90
        joint = int((sn20_open & sp_hi_open & dec_sn20).sum())
        xor_days = int((sn20_open ^ sp_hi_open).sum())
    facts_mirror = {"sumn_plus_sump_max_dev": float((both - 1.0).abs().max()),
                    "sumn20_q10_vs_sump20_q90_both_open_days": joint,
                    "sumn20_q10_vs_sump20_q90_xor_days": xor_days,
                    "note": "mirror-twin identity SUMN+SUMP==1 (eps 1e-12 denominator); "
                            "SUMN20_q10 and SUMP20_q90 fire identical days = cluster #21 "
                            "corr-1.000 empirical proof; SUMD20_q90 same family monotone "
                            "transform (2*SUMP-1) = same days; supply face = ONE up-share axis"}

    # ---- inherited faces (W3-W12 frozen modules verbatim) ----------------
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
    r20 = F["RSQR20"]
    r20_open, dec_r20, _ = rsqr_gate_hi(r20)  # W12 frozen face (r447 verbatim)

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
             "probe_lineage": "r447 W12 probe paradigm + a158 frozen runner verbatim-import (SUMN/SUMP face, W13 pre-selection); r431 seven-gate + r228 MOM + r234 VSTD + r237 STD + r447 RSQR lineage cross-checked (seven files)",
             "construction_disclosure": "SUMN=down-share of absolute movement sum(clip(-diff,0),d)/sum(|diff|,d) in [0,1]; low-side gate = UP-dominant window (directional PURITY face, direction-LOADED unlike W12 RSQR sign-blind fit-quality); nearest burned neighbors = W12 RSQR (fit quality) + W11 STD (dispersion level): all three read 'trend-state' from different angles; bearish mirror (SUMN_q90/SUMP_q10) never passed the 48-PASS census (honest supply face)",
             "warmup_disclosure": "SUMN first-decidable bar-idx 120 (f valid from idx 1: diff undefined at 0; qref 252/min120) == RSQR/STD family warmup; MOM anchor 139 differs by construction (roc20 shift-20)"}

    for tag, dec, op in (("sumn20", dec_sn20, sn20_open), ("sumn10", dec_sn10, sn10_open)):
        facts[f"{tag}_decidable_days"] = int(dec.sum())
        facts[f"{tag}_open_days"] = int((op & dec).sum())
        facts[f"{tag}_open_rate_on_decidable"] = round(float((op & dec).mean()), 4)

    # direction-loaded disclosure: slope-sign split among SUMN20-open days
    m_open = sn20_open & dec_sn20 & beta20.notna()
    facts["sumn20_open_slope_sign_split"] = {
        "up_slope_days": int((m_open & (beta20 > 0)).sum()),
        "down_slope_days": int((m_open & (beta20 <= 0)).sum()),
        "note": "BETA20 sign from the same frozen runner; up-dominant windows should be "
                "slope-up-heavy BY CONSTRUCTION (direction-loaded axis) -- the split "
                "quantifies how much; direction conditioning still lives in burned axes "
                "(GATE/YANG/STREAK/MOM), redundancy measured in adjacency cells"}

    # ---- determinism cross-check vs frozen probe facts (seven lineage files) ----
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
    if os.path.exists(GATE_RECHECK):
        gr = json.load(open(GATE_RECHECK, encoding="utf-8"))
        refs = {}
        for gname in ("SUMN10_q10", "SUMN20_q10"):
            try:
                ref = gr["gates"][gname]["face_a"]["members"]["510300"]
                refs[gname] = {"n_in_ref": ref["n_in"], "n_out_ref": ref["n_out"]}
            except Exception as e:
                refs[gname] = {"error": str(e)}
        xchecks["gate_recheck_ref"] = {**refs,
            "note": "five-member secondary face different member-panel loading; disclosure reference NOT fail-closed"}
    facts["determinism_cross_checks"] = xchecks

    # ---- SUMN20_q10 open-rate inside each inherited gate ----------------------
    def rate(mask_in, gate, dec):
        both = int((mask_in & gate).sum())
        base = int((mask_in & dec).sum())
        return round(100.0 * both / base, 2) if base else float("nan")

    facts["sumn20_open_rate_inside_pct"] = {
        "bull": rate(bull, sn20_open, dec_sn20), "bear": rate(bear, sn20_open, dec_sn20),
        "calm": rate(calm, sn20_open, dec_sn20), "wild": rate(wild, sn20_open, dec_sn20),
        "yang": rate(yang, sn20_open, dec_sn20), "red": rate(~yang, sn20_open, dec_sn20),
        "surge": rate(surge, sn20_open, dec_sn20), "dry": rate(~surge, sn20_open, dec_sn20),
        "up_streak2": rate(up_st, sn20_open, dec_sn20), "down_streak2": rate(dn_st, sn20_open, dec_sn20),
        "neither_streak": rate(neither, sn20_open, dec_sn20),
        "mad60_q10_open": rate(mad_q10, sn20_open, dec_sn20), "mad60_q10_closed": rate(~mad_q10 & dec_mad, sn20_open, dec_sn20),
        "rsv60_low_open": rate(rsv_low, sn20_open, dec_sn20), "rsv60_low_closed": rate(~rsv_low & dec_rsv, sn20_open, dec_sn20),
        "amp_wide": rate(wide == 1, sn20_open, dec_sn20), "amp_narrow": rate(wide == 0, sn20_open, dec_sn20),
        "mom_open": rate(mom_open & dec_mom, sn20_open, dec_sn20 & dec_mom), "mom_closed": rate((~mom_open & dec_mom), sn20_open, dec_sn20 & dec_mom),
        "std20_open": rate(std20_open & dec_s20, sn20_open, dec_sn20 & dec_s20), "std20_closed": rate((~std20_open & dec_s20), sn20_open, dec_sn20 & dec_s20),
        "std10_open": rate(std10_open & dec_s10, sn20_open, dec_sn20 & dec_s10), "std10_closed": rate((~std10_open & dec_s10), sn20_open, dec_sn20 & dec_s10),
        "rsqr20_open": rate(r20_open & dec_r20, sn20_open, dec_sn20 & dec_r20), "rsqr20_closed": rate((~r20_open & dec_r20), sn20_open, dec_sn20 & dec_r20)}

    # ---- reverse: neighbor-gate rates inside SUMN20-open vs SUMN20-closed ---------
    facts["reverse_rates_inside_sumn20_pct"] = {
        "wild_rate_when_sumn20_open": rate(sn20_open, wild, dec_sn20 & med500.notna()),
        "wild_rate_when_sumn20_closed": rate((~sn20_open & dec_sn20), wild, dec_sn20 & med500.notna()),
        "wide_rate_when_sumn20_open": rate(sn20_open, wide == 1, dec_sn20 & amp_known),
        "wide_rate_when_sumn20_closed": rate((~sn20_open & dec_sn20), wide == 1, dec_sn20 & amp_known),
        "std20_rate_when_sumn20_open": rate(sn20_open & dec_s20, std20_open, dec_sn20 & dec_s20),
        "std20_rate_when_sumn20_closed": rate((~sn20_open & dec_sn20 & dec_s20), std20_open, dec_sn20 & dec_s20),
        "rsqr20_rate_when_sumn20_open": rate(sn20_open & dec_r20, r20_open, dec_sn20 & dec_r20),
        "rsqr20_rate_when_sumn20_closed": rate((~sn20_open & dec_sn20 & dec_r20), r20_open, dec_sn20 & dec_r20),
        "yang_rate_when_sumn20_open": rate(sn20_open, yang, dec_sn20),
        "yang_rate_when_sumn20_closed": rate((~sn20_open & dec_sn20), yang, dec_sn20),
        "mom_rate_when_sumn20_open": rate(sn20_open & dec_mom, mom_open, dec_sn20 & dec_mom),
        "mom_rate_when_sumn20_closed": rate((~sn20_open & dec_sn20 & dec_mom), mom_open, dec_sn20 & dec_mom)}

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
        "sumn20_vs_wild": cell(sn20_open, dec_sn20, wild, med500.notna()),
        "sumn20_vs_calm": cell(sn20_open, dec_sn20, calm, med500.notna()),
        "sumn20_vs_wide": cell(sn20_open, dec_sn20, wide == 1, amp_known),
        "sumn20_vs_narrow": cell(sn20_open, dec_sn20, wide == 0, amp_known),
        "sumn20_vs_mad60": cell(sn20_open, dec_sn20, mad_q10, dec_mad),
        "sumn20_vs_rsv60": cell(sn20_open, dec_sn20, rsv_low, dec_rsv),
        "sumn20_vs_downstreak": cell(sn20_open, dec_sn20, dn_st, st.notna()),
        "sumn20_vs_upstreak": cell(sn20_open, dec_sn20, up_st, st.notna()),
        "sumn20_vs_mom": cell(sn20_open, dec_sn20, mom_open, dec_mom),
        "sumn20_vs_std20": cell(sn20_open, dec_sn20, std20_open, dec_s20),
        "sumn20_vs_std10": cell(sn20_open, dec_sn20, std10_open, dec_s10),
        "sumn20_vs_rsqr20": cell(sn20_open, dec_sn20, r20_open, dec_r20),
        "sumn10_vs_sumn20": cell(sn10_open, dec_sn10, sn20_open, dec_sn20)}

    # distinct-space increment faces (r228 "121 mom-only days" pattern)
    dec_calm = dec_sn20 & med500.notna()
    dec_nar = dec_sn20 & amp_known
    facts["distinct_space_increment"] = {
        "sumn20_open_and_calm_days": int((sn20_open & calm & dec_calm).sum()),
        "sumn20_open_and_wild_days": int((sn20_open & wild & dec_calm).sum()),
        "sumn20_open_and_narrow_days": int((sn20_open & (wide == 0) & dec_nar).sum()),
        "sumn20_open_and_yang_days": int((sn20_open & yang & dec_sn20).sum()),
        "sumn20_open_and_red_days": int((sn20_open & (~yang) & dec_sn20).sum()),
        "sumn20_open_and_mom_open_days": int((sn20_open & mom_open & (dec_sn20 & dec_mom)).sum()),
        "sumn20_open_and_std20_open_days": int((sn20_open & std20_open & (dec_sn20 & dec_s20)).sum()),
        "sumn20_open_and_std20_closed_days": int((sn20_open & (~std20_open & dec_s20) & (dec_sn20 & dec_s20)).sum()),
        "sumn20_open_and_rsqr20_open_days": int((sn20_open & r20_open & (dec_sn20 & dec_r20)).sum()),
        "sumn20_open_and_rsqr20_closed_days": int((sn20_open & (~r20_open & dec_r20) & (dec_sn20 & dec_r20)).sum()),
        "note": "sumn_open while burned neighbor faces read the opposite state = conditional-space increment; sumn_open∧rsqr_closed = up-dominance-without-fit-quality face (direction-led non-linear advance) and rsqr_open∧sumn_closed = fit-quality-without-up-dominance (clean DOWN-trend: sign-blind fit high, up-share low) = the construction divergence vs W12; near-zero counts = collapsed neighbor"}

    # ---- NINE-gate 512-cell crossing (SUMN20_q10 as the 9th face) -------------
    cells = {}
    n_empty = 0
    m9 = dec_sn20 & bull.notna() & calm.notna() & amp_known & st.notna() & dec_mad & dec_rsv & dec_s20
    for bname, b in (("bull", bull), ("bear", bear)):
        for vname, vv in (("calm", calm), ("wild", wild)):
            for yname, y in (("yang", yang), ("red", ~yang)):
                for sname, s in (("surge", surge), ("dry", ~surge)):
                    for kname, k in (("up_streak", up_st), ("down_streak", dn_st)):
                        for tname, t in (("mad60", mad_q10), ("rsv60", rsv_low)):
                            for aname, a in (("wide", wide == 1), ("narrow", wide == 0)):
                                for sdname, sd in (("std20_open", std20_open), ("std20_closed", ~std20_open & dec_s20)):
                                    for sname2, s2 in (("sumn20_open", sn20_open), ("sumn20_closed", ~sn20_open & dec_sn20)):
                                        cnt = int((m9 & b & vv & y & s & k & t & a & sd & s2).sum())
                                        cells["%s|%s|%s|%s|%s|%s|%s|%s|%s" % (bname, vname, yname, sname, kname, tname, aname, sdname, sname2)] = cnt
                                        if cnt == 0:
                                            n_empty += 1
    facts["nine_gate_512_cells_empty_count"] = n_empty
    facts["nine_gate_512_cells_nonzero_count"] = 512 - n_empty
    facts["nine_gate_512_cells_min_nonzero"] = min([x for x in cells.values() if x > 0] or [0])
    facts["nine_gate_512_cells_max"] = max(cells.values())
    facts["nine_gate_all_decidable_days"] = int(m9.sum())
    facts["nine_gate_cells"] = cells

    # ---- extreme days: state readout -------------------------------------------
    est = {}
    for dstr in EXTREME_DAYS:
        idx = df.index[df["date"] == dstr]
        if len(idx) == 0:
            est[dstr] = "not-in-panel"
            continue
        i = int(idx[0])
        est[dstr] = {
            "sumn20_open": bool(sn20_open.iloc[i]) if dec_sn20.iloc[i] else None,
            "sumn10_open": bool(sn10_open.iloc[i]) if dec_sn10.iloc[i] else None,
            "sumn20_value": (None if pd.isna(sn20.iloc[i]) else round(float(sn20.iloc[i]), 6)),
            "sumn20_over_q10ref": (None if pd.isna(sn20.iloc[i]) or pd.isna(q10_20.iloc[i]) else round(float(sn20.iloc[i] / q10_20.iloc[i]), 3)),
            "std20_open": bool(std20_open.iloc[i]) if dec_s20.iloc[i] else None,
            "rsqr20_open": bool(r20_open.iloc[i]) if dec_r20.iloc[i] else None,
            "slope_sign": ("up" if (beta20.iloc[i] > 0) else "down") if (not pd.isna(beta20.iloc[i]) and dec_sn20.iloc[i]) else None}
    facts["extreme_day_states"] = est

    # ---- census-style forward differential (descriptive face, NOT a claim) -----
    for fw in (5, 20):
        fwd = c.shift(-fw) / c - 1.0
        base = dec_sn20 & fwd.notna()
        a = fwd[sn20_open & base]
        b = fwd[(~sn20_open & dec_sn20) & base]
        facts[f"forward_{fw}d"] = {
            "n_open": int(len(a)), "n_closed": int(len(b)),
            "mean_fwd_open": round(float(a.mean()), 6) if len(a) else float("nan"),
            "mean_fwd_closed": round(float(b.mean()), 6) if len(b) else float("nan"),
            "diff_open_minus_closed": round(float(a.mean() - b.mean()), 6) if (len(a) and len(b)) else float("nan"),
            "welch_t": tstats(a, b),
            "note": "descriptive probe face on 510300 anchor only; census/recheck universe face = A158-TSGATE-P1 SUMN20_q10 OOS med_t 1.000 (1,724 codes) + GATE-RECHECK 5-member CONFIRM (net med 0.00921, 4/5); NOT a strategy claim; overlapping windows inflate |t|"}
    # grind decomposition face (construction divergence core: clean-trend low-noise)
    for fw in (20,):
        fwd = c.shift(-fw) / c - 1.0
        base = dec_sn20 & fwd.notna() & med500.notna()
        a = fwd[sn20_open & calm & base]
        b = fwd[sn20_open & wild & base]
        facts["grind_face_forward_20d"] = {
            "n_open_calm": int(len(a)), "n_open_wild": int(len(b)),
            "mean_fwd_open_calm": round(float(a.mean()), 6) if len(a) else float("nan"),
            "mean_fwd_open_wild": round(float(b.mean()), 6) if len(b) else float("nan"),
            "welch_t_calm_vs_wild": tstats(a, b),
            "note": "sumn20_open days split by burned W4 VOL face: calm side = clean-grind increment face; descriptive only"}
    # direction-split forward face (direction-LOADED honesty, opposite of W12 sign-blind)
    for fw in (20,):
        fwd = c.shift(-fw) / c - 1.0
        base = dec_sn20 & fwd.notna() & beta20.notna()
        a = fwd[sn20_open & (beta20 > 0) & base]
        b = fwd[sn20_open & (beta20 <= 0) & base]
        facts["direction_split_forward_20d"] = {
            "n_up_slope": int(len(a)), "n_down_slope": int(len(b)),
            "mean_fwd_up": round(float(a.mean()), 6) if len(a) else float("nan"),
            "mean_fwd_down": round(float(b.mean()), 6) if len(b) else float("nan"),
            "welch_t_up_vs_down": tstats(a, b),
            "note": "SUMN is direction-LOADED (up-dominant selection); slope-split forward readout quantifies residual asymmetry (up-share-high windows with down-slope = distributional tail, not a gate line)"}

    # ---- core48 member-level SUMN20_q10 open-rate spread (real roster) -----------
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    rates = {}
    for sym, d2 in sorted(prices.items()):
        d2 = d2[d2.index <= cut]
        if len(d2) >= 260:
            # .to_numpy() first: dict-of-Series construction ALIGNs to the
            # given RangeIndex -> all-NaN reindex artifact (r447 pit law)
            di2 = pd.DataFrame({"open": d2["open"].to_numpy(), "high": d2["high"].to_numpy(),
                                "low": d2["low"].to_numpy(), "close": d2["close"].to_numpy(),
                                "volume": d2["volume"].to_numpy()},
                               index=pd.RangeIndex(len(d2)))
            F2 = a158.alpha158_factors(di2)
            op2, dv2, _ = sumn_gate(F2["SUMN20"])
            if dv2.any():
                rates[str(sym)] = round(float((op2 & dv2).mean()), 4)
    vals = sorted(rates.values())
    facts["core48_sumn20_open_rate"] = {
        "n": len(vals),
        "min": round(vals[0], 4), "median": round(vals[len(vals) // 2], 4),
        "max": round(vals[-1], 4),
        "method": "tl1.load_core() roster (import-reuse via r237 lineage, real core48 face) + frozen-runner SUMN verbatim",
        "members_with_lt260_rows_excluded": len(prices) - len(vals)}

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in facts.items() if not isinstance(v, dict)}, ensure_ascii=False))
    print("mirror_identity:", json.dumps(facts["mirror_identity"], ensure_ascii=False))
    print("sumn20 face: decidable", facts["sumn20_decidable_days"],
          "| open", facts["sumn20_open_days"], "| open_rate", facts["sumn20_open_rate_on_decidable"])
    print("sumn10 face: decidable", facts["sumn10_decidable_days"],
          "| open", facts["sumn10_open_days"], "| open_rate", facts["sumn10_open_rate_on_decidable"])
    print("slope sign split:", json.dumps(facts["sumn20_open_slope_sign_split"], ensure_ascii=False))
    print("sumn20_open_rate_inside:", json.dumps(facts["sumn20_open_rate_inside_pct"], ensure_ascii=False))
    print("reverse_rates:", json.dumps(facts["reverse_rates_inside_sumn20_pct"], ensure_ascii=False))
    print("adjacency:", json.dumps(facts["adjacency"], ensure_ascii=False))
    print("distinct_space_increment:", json.dumps(facts["distinct_space_increment"], ensure_ascii=False))
    print("fwd20d:", json.dumps(facts["forward_20d"], ensure_ascii=False))
    print("fwd5d:", json.dumps(facts["forward_5d"], ensure_ascii=False))
    print("grind_face:", json.dumps(facts["grind_face_forward_20d"], ensure_ascii=False))
    print("direction_split:", json.dumps(facts["direction_split_forward_20d"], ensure_ascii=False))
    print("nine_gate_512_cells: empty", facts["nine_gate_512_cells_empty_count"],
          "| nonzero", facts["nine_gate_512_cells_nonzero_count"],
          "| min-nonzero", facts["nine_gate_512_cells_min_nonzero"],
          "| max", facts["nine_gate_512_cells_max"],
          "| all-decidable days", facts["nine_gate_all_decidable_days"])
    print("extreme days:", json.dumps(facts["extreme_day_states"], ensure_ascii=False))
    print("determinism_cross_checks:", json.dumps(facts["determinism_cross_checks"]))
    print("core48 sumn20 open rate:", json.dumps(facts["core48_sumn20_open_rate"], ensure_ascii=False))
    print("W13 SUMN20_q10/SUMN10_q10 pre-selection probe facts ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
