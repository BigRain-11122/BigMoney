# -*- coding: utf-8 -*-
"""_r251bmc_sumn_w13_probe.py -- W13 pre-selection probe: A158-TSGATE-P1
48-PASS pool next-top family SUMN10_q10 / SUMN20_q10 (loss-share composition
gate, LOW own-quantile side; GATE-RECHECK-confirmed clusters #20/#21) raw-face
facts on the 510300 anchor. NOT results, NOT a strategy claim.

W13 supply-prep slice per TRIAL_LABOR_LAW sec.1 standing-supply step
(r251 bm-c berth, r447 bm-a probe+draft berth precedent mirrored).
Pre-commitment window note (research/DECISION_CHAIN.md sec.4.7 v1.2: next-wave
hypotheses must be frozen BEFORE the previous wave verdict lands; W12
runner/generate landed, screen/judge in-flight on the bm-b lane right now
(T-124) = the W13 berth window is open; W10/W11/W12 themselves were berthed
pre-verdict per the same cadence, r228/r237/r447 precedent).

Pool-turn lineage (r234 digest sec.3 named-pool pointer): census four
positive families all consumed (MAD60/RSV60->W8, ROC20->W10, VSTD20->DEMOTE)
-> 48-PASS pool top: STD20/10_q90 (consumed by W11) -> RSQR20/10_q90
(consumed by W12) -> NEXT = SUMN10/20_q10 (loss-share composition family).

The deferral question this probe answers:
  does the SUMN low-quantile gate (loss-share of |delta-close| over 10/20d
  in its own 252d bottom decile = "gain-dominated window / absent-recent-
  losses state") open a DISTINCT day-level conditional space from the burned
  trial-grammar axes -- esp. W10 MOM (roc20 oversold: MOM reads NET change,
  SUMN reads sign COMPOSITION; a chop-with-net-zero can have high loss-share,
  a flat-quiet window has LOW loss-share with ~zero net) and W12 RSQR (fit
  quality, sign-blind; SUMN is sign-EMBEDDED: low loss-share = up-tilted) --
  or is it a collapsed neighbor like VSTD20_q20 was (98.5% inside W4 calm,
  r234 DEMOTE)?

Cluster honesty (GATE-RECHECK clusters #20/#21, internal corr 1.000):
  SUMN{d}_q10 low side == SUMP{d}_q90 high side == SUMD{d}_q90 high side
  (loss-share low <=> gain-share high <=> diff high, algebraically linked:
  SUMP+SUMN=1, SUMD=2*SUMP-1). The probe quantifies the open-day identity
  overlap on the anchor panel; axis value picks SUMN low side as the
  representative (one face, not three).

Construction honesty (verbatim-import discipline, zero re-implementation):
  SUMN comes from the FROZEN in-repo runner scripts/a158_tsgate_probe.py
  (bm-a r438/439 burn face) -- import a158_tsgate_probe; F =
  alpha158_factors(df); F["SUMN%d"] = loss.rolling(d,min1).sum() /
  (ab.rolling(d,min1).sum() + 1e-12).  Inherited W3-W11 faces come from the
  frozen r237 W11 probe module (results/_r237bmc_stdq90_w11_probe.py) --
  import-reuse of amp/streak/tstate/mom/std face functions verbatim.
  Gate (A158_TSGATE_P1 prereg sec.2 frozen): low side
      f < f.rolling(252, min_periods=120).quantile(0.10)
  decidable = f.notna() & qref.notna() (pit-95/r431 NaN-bucket artifact law).
  Warmup: dfc=NaN at idx 0 -> f valid from bar-idx 1 -> qref first valid at
  bar-idx 120 (same construction family as STD/RSQR, asserted fail-closed).

Direction-EMBEDDED disclosure (SUMN-specific honesty, opposite of W12's
sign-blind face): low loss-share is UP-tilted by construction; the gate
embeds a directional tilt rather than being sign-neutral.  Explicit
direction faces live in the burned axes (GATE/YANG/STREAK/MOM).  This probe
quantifies the roc20-sign split among SUMN-open days (W12 slope-sign split
mirror).

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
import a158_tsgate_probe as a158            # frozen runner (SUMN verbatim)
import _r237bmc_stdq90_w11_probe as r237p   # frozen W11 probe (W3-W11 faces)
import trial_labor_w1 as tl1                 # via r237p lineage (core48 loader)
import _r447bma_rsqr_w12_probe as r447p    # frozen W12 probe (RSQR faces, lineage cross-ref)

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4-W12 probes
OUT = "results/_r251bmc_sumn_w13_probe_facts.json"
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


def sumn_gate(f, qlow_side=None):
    """A158_TSGATE_P1 frozen gate semantics via runner constants (import-reuse),
    LOW side. Returns (open, decidable, qref)."""
    q = a158.QLOW if qlow_side is None else qlow_side
    qref = f.rolling(a158.GATE_WIN, min_periods=a158.GATE_MINP).quantile(q)
    dec = f.notna() & qref.notna()
    return (f < qref) & dec, dec, qref


def hi_gate(f):
    """HIGH-side mirror (SUMP/SUMD cluster identity check)."""
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

    # ---- SUMN faces (frozen-runner verbatim import; zero re-implementation) ----
    di = pd.DataFrame({"open": o, "high": h, "low": l, "close": c, "volume": v},
                      index=pd.RangeIndex(n))
    F = a158.alpha158_factors(di)
    s10, s20 = F["SUMN10"], F["SUMN20"]
    p10, d10f = F["SUMP10"], F["SUMD10"]
    n10_open, dec_n10, q10_10 = sumn_gate(s10)
    n20_open, dec_n20, q10_20 = sumn_gate(s20)
    # cluster identity faces (high-side mirrors, disclosure only)
    p10_open, dec_p10, _ = hi_gate(p10)
    d10_open, dec_d10, _ = hi_gate(d10f)

    # warmup fail-closed: dfc NaN at idx 0 -> f valid from idx 1;
    # qref(252,min120) first valid at bar-idx 120 (STD/RSQR family same seat)
    for tag, dec in (("sumn10", dec_n10), ("sumn20", dec_n20)):
        first_dec = int(np.argmax(dec.to_numpy()))
        assert first_dec == 120, f"{tag} first decidable {first_dec} != 120"

    # internal spot-check vs direct per-window recompute (loss-share identity):
    # SUMN10[i] = sum(max(-(c-c[-1]),0) over window) / (sum|c-c[-1]| + 1e-12)
    cv = c.to_numpy(dtype=float)
    for d_win, series in ((10, s10), (20, s20)):
        for i in (59, 500, 2000):
            dc = cv[i - d_win + 1: i + 1] - cv[i - d_win: i]
            loss = np.clip(-dc, 0, None).sum()
            ab = np.abs(dc).sum()
            ref = loss / (ab + 1e-12)
            got = float(series.iloc[i])
            assert abs(got - ref) < 1e-12, f"SUMN{d_win}@{i} {got} != direct {ref}"

    # ---- cluster identity overlap on anchor (GATE-RECHECK corr 1.000 face) ----
    m = dec_n10 & dec_p10
    ident_p = int((n10_open & p10_open & m).sum())
    m2 = dec_n10 & dec_d10
    ident_d = int((n10_open & d10_open & m2).sum())
    facts_cluster = {
        "sumn10_open_days": int((n10_open & dec_n10).sum()),
        "sump10_hi_open_days": int((p10_open & dec_p10).sum()),
        "joint_decidable_days_p": int(m.sum()),
        "both_open_days_vs_sump": ident_p,
        "joint_decidable_days_d": int(m2.sum()),
        "both_open_days_vs_sumd": ident_d,
        "note": "GATE-RECHECK clusters #20/#21 internal corr 1.000 (census face); "
                "anchor-panel open-day identity quantified here; SUMP+SUMN=1, "
                "SUMD=2*SUMP-1 (algebraic link); axis picks SUMN low side as the "
                "single representative face"}

    # ---- inherited faces (W3-W12 frozen, r237 module verbatim + r447 RSQR) ----
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
    # RSQR faces (W12 axis, r447 frozen probe verbatim-import)
    r20, r10 = F["RSQR20"], F["RSQR10"]
    r20_open, dec_r20, _ = r447p.rsqr_gate(r20)
    r10_open, dec_r10, _ = r447p.rsqr_gate(r10)

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
             "probe_lineage": "r237 W11 probe module + a158 frozen runner verbatim-import (SUMN face, W13 pre-selection) + r447 W12 probe (RSQR adjacency faces); r431 seven-gate + r228 MOM + r234 VSTD + r237 STD + r447 RSQR lineage cross-checked",
             "construction_disclosure": "SUMN=rolling(d).sum of losses / rolling(d).sum of |delta-close| (loss-SHARE of the sign composition, in [0,1]); gate = LOW own-quantile (bottom decile of 252d own history) = gain-dominated / absent-recent-losses state; direction-EMBEDDED (up-tilted by construction, opposite honesty face of W12 sign-blind RSQR); nearest burned neighbors = W10 MOM (net-change velocity, opposite-side composition) + W12 RSQR (sign-blind fit quality)",
             "warmup_disclosure": "SUMN first-decidable bar-idx 120 (dfc NaN at idx 0 -> f valid from idx 1; qref 252/min120) == STD/RSQR family warmup; MOM anchor 139 differs by construction (roc20 shift-20)",
             "cluster_identity": facts_cluster}

    for tag, dec, op in (("sumn10", dec_n10, n10_open), ("sumn20", dec_n20, n20_open)):
        facts[f"{tag}_decidable_days"] = int(dec.sum())
        facts[f"{tag}_open_days"] = int((op & dec).sum())
        facts[f"{tag}_open_rate_on_decidable"] = round(float((op & dec).mean()), 4)

    # direction-embedded disclosure: roc20 sign split among SUMN10-open days
    m_open = n10_open & dec_n10 & roc20.notna()
    facts["sumn10_open_direction_split"] = {
        "roc20_positive_days": int((m_open & (roc20 > 0)).sum()),
        "roc20_negative_days": int((m_open & (roc20 <= 0)).sum()),
        "roc20_zero_days": int((m_open & (roc20 == 0)).sum()),
        "note": "roc20 sign from the same frozen r237 mom face; SUMN-low is "
                "up-tilted by construction; explicit direction conditioning "
                "lives in burned axes (GATE/YANG/STREAK/MOM)"}

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
                           "rsqr20_open_match": f47["rsqr20_open_days"] == int((r20_open & dec_r20).sum()),
                           "rsqr10_open_match": f47["rsqr10_open_days"] == int((r10_open & dec_r10).sum())}
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

    # ---- SUMN10 open-rate inside each inherited gate --------------------------
    def rate(mask_in, gate, dec):
        both = int((mask_in & gate).sum())
        base = int((mask_in & dec).sum())
        return round(100.0 * both / base, 2) if base else float("nan")

    facts["sumn10_open_rate_inside_pct"] = {
        "bull": rate(bull, n10_open, dec_n10), "bear": rate(bear, n10_open, dec_n10),
        "calm": rate(calm, n10_open, dec_n10), "wild": rate(wild, n10_open, dec_n10),
        "yang": rate(yang, n10_open, dec_n10), "red": rate(~yang, n10_open, dec_n10),
        "surge": rate(surge, n10_open, dec_n10), "dry": rate(~surge, n10_open, dec_n10),
        "up_streak2": rate(up_st, n10_open, dec_n10), "down_streak2": rate(dn_st, n10_open, dec_n10),
        "neither_streak": rate(neither, n10_open, dec_n10),
        "mad60_q10_open": rate(mad_q10, n10_open, dec_n10), "mad60_q10_closed": rate(~mad_q10 & dec_mad, n10_open, dec_n10),
        "rsv60_low_open": rate(rsv_low, n10_open, dec_n10), "rsv60_low_closed": rate(~rsv_low & dec_rsv, n10_open, dec_n10),
        "amp_wide": rate(wide == 1, n10_open, dec_n10), "amp_narrow": rate(wide == 0, n10_open, dec_n10),
        "mom_open": rate(mom_open & dec_mom, n10_open, dec_n10 & dec_mom), "mom_closed": rate((~mom_open & dec_mom), n10_open, dec_n10 & dec_mom),
        "std20_open": rate(std20_open & dec_s20, n10_open, dec_n10 & dec_s20), "std20_closed": rate((~std20_open & dec_s20), n10_open, dec_n10 & dec_s20),
        "std10_open": rate(std10_open & dec_s10, n10_open, dec_n10 & dec_s10), "std10_closed": rate((~std10_open & dec_s10), n10_open, dec_n10 & dec_s10),
        "rsqr20_open": rate(r20_open & dec_r20, n10_open, dec_n10 & dec_r20), "rsqr20_closed": rate((~r20_open & dec_r20), n10_open, dec_n10 & dec_r20)}

    # ---- reverse: neighbor-gate rates inside SUMN10-open vs SUMN10-closed ------
    facts["reverse_rates_inside_sumn10_pct"] = {
        "wild_rate_when_sumn10_open": rate(n10_open, wild, dec_n10 & med500.notna()),
        "wild_rate_when_sumn10_closed": rate((~n10_open & dec_n10), wild, dec_n10 & med500.notna()),
        "wide_rate_when_sumn10_open": rate(n10_open, wide == 1, dec_n10 & amp_known),
        "wide_rate_when_sumn10_closed": rate((~n10_open & dec_n10), wide == 1, dec_n10 & amp_known),
        "std20_rate_when_sumn10_open": rate(n10_open & dec_s20, std20_open, dec_n10 & dec_s20),
        "std20_rate_when_sumn10_closed": rate((~n10_open & dec_n10 & dec_s20), std20_open, dec_n10 & dec_s20),
        "yang_rate_when_sumn10_open": rate(n10_open, yang, dec_n10),
        "yang_rate_when_sumn10_closed": rate((~n10_open & dec_n10), yang, dec_n10),
        "mom_rate_when_sumn10_open": rate(n10_open & dec_mom, mom_open, dec_n10 & dec_mom),
        "mom_rate_when_sumn10_closed": rate((~n10_open & dec_n10 & dec_mom), mom_open, dec_n10 & dec_mom),
        "rsqr20_rate_when_sumn10_open": rate(n10_open & dec_r20, r20_open, dec_n10 & dec_r20),
        "rsqr20_rate_when_sumn10_closed": rate((~n10_open & dec_n10 & dec_r20), r20_open, dec_n10 & dec_r20)}

    # ---- neighbor adjacency cross cells (THE deferral question) ----------------
    def cell(a, da, b, db):
        mm = da & db
        both_open = int((a & b & mm).sum())
        a_open = int((a & mm).sum())
        b_open = int((b & mm).sum())
        union = int(((a | b) & mm).sum())
        return {"both_open": both_open, "a_open": a_open, "b_open": b_open,
                "a_open_pct_of_b_open": round(100.0 * both_open / b_open, 2) if b_open else float("nan"),
                "b_open_pct_of_a_open": round(100.0 * both_open / a_open, 2) if a_open else float("nan"),
                "a_only_days": a_open - both_open, "union_days": union, "joint_decidable_days": int(mm.sum())}

    facts["adjacency"] = {
        "sumn10_vs_wild": cell(n10_open, dec_n10, wild, med500.notna()),
        "sumn10_vs_calm": cell(n10_open, dec_n10, calm, med500.notna()),
        "sumn10_vs_wide": cell(n10_open, dec_n10, wide == 1, amp_known),
        "sumn10_vs_narrow": cell(n10_open, dec_n10, wide == 0, amp_known),
        "sumn10_vs_mad60": cell(n10_open, dec_n10, mad_q10, dec_mad),
        "sumn10_vs_rsv60": cell(n10_open, dec_n10, rsv_low, dec_rsv),
        "sumn10_vs_upstreak": cell(n10_open, dec_n10, up_st, st.notna()),
        "sumn10_vs_downstreak": cell(n10_open, dec_n10, dn_st, st.notna()),
        "sumn10_vs_mom": cell(n10_open, dec_n10, mom_open, dec_mom),
        "sumn10_vs_std20": cell(n10_open, dec_n10, std20_open, dec_s20),
        "sumn10_vs_std10": cell(n10_open, dec_n10, std10_open, dec_s10),
        "sumn10_vs_rsqr20": cell(n10_open, dec_n10, r20_open, dec_r20),
        "sumn10_vs_rsqr10": cell(n10_open, dec_n10, r10_open, dec_r10),
        "sumn20_vs_sumn10": cell(n20_open, dec_n20, n10_open, dec_n10)}

    # distinct-space increment faces (r228 "121 mom-only days" pattern)
    dec_calm = dec_n10 & med500.notna()
    dec_nar = dec_n10 & amp_known
    facts["distinct_space_increment"] = {
        "sumn10_open_and_calm_days": int((n10_open & calm & dec_calm).sum()),
        "sumn10_open_and_wild_days": int((n10_open & wild & dec_calm).sum()),
        "sumn10_open_and_narrow_days": int((n10_open & (wide == 0) & dec_nar).sum()),
        "sumn10_open_and_yang_days": int((n10_open & yang & dec_n10).sum()),
        "sumn10_open_and_red_days": int((n10_open & (~yang) & dec_n10).sum()),
        "sumn10_open_and_mom_open_days": int((n10_open & mom_open & (dec_n10 & dec_mom)).sum()),
        "sumn10_open_and_std20_open_days": int((n10_open & std20_open & (dec_n10 & dec_s20)).sum()),
        "sumn10_open_and_std20_closed_days": int((n10_open & (~std20_open & dec_s20) & (dec_n10 & dec_s20)).sum()),
        "sumn10_open_and_rsqr20_open_days": int((n10_open & r20_open & (dec_n10 & dec_r20)).sum()),
        "sumn10_open_and_rsqr20_closed_days": int((n10_open & (~r20_open & dec_r20) & (dec_n10 & dec_r20)).sum()),
        "note": "sumn10_open while burned neighbor faces read the opposite state = conditional-space increment; sumn10_open∧rsqr20_closed = sign-composition-without-fit-quality face (up-tilted chop-rejected) = the construction divergence vs W12; sumn10_open∧rsqr20_open = quiet clean grind co-open face; near-zero counts = collapsed neighbor"}

    # ---- NINE-gate 512-cell crossing (SUMN10_q10 as the 9th face) -------------
    cells = {}
    n_empty = 0
    m9 = dec_n10 & bull.notna() & calm.notna() & amp_known & st.notna() & dec_mad & dec_rsv & dec_s20
    for bname, b in (("bull", bull), ("bear", bear)):
        for vname, vv in (("calm", calm), ("wild", wild)):
            for yname, y in (("yang", yang), ("red", ~yang)):
                for sname, s in (("surge", surge), ("dry", ~surge)):
                    for kname, k in (("up_streak", up_st), ("down_streak", dn_st)):
                        for tname, t in (("mad60", mad_q10), ("rsv60", rsv_low)):
                            for aname, a in (("wide", wide == 1), ("narrow", wide == 0)):
                                for sdname, sd in (("std20_open", std20_open), ("std20_closed", ~std20_open & dec_s20)):
                                    for rname, rr in (("sumn10_open", n10_open), ("sumn10_closed", ~n10_open & dec_n10)):
                                        cnt = int((m9 & b & vv & y & s & k & t & a & sd & rr).sum())
                                        cells["%s|%s|%s|%s|%s|%s|%s|%s|%s" % (bname, vname, yname, sname, kname, tname, aname, sdname, rname)] = cnt
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
            "sumn10_open": bool(n10_open.iloc[i]) if dec_n10.iloc[i] else None,
            "sumn20_open": bool(n20_open.iloc[i]) if dec_n20.iloc[i] else None,
            "sumn10_value": (None if pd.isna(s10.iloc[i]) else round(float(s10.iloc[i]), 6)),
            "sumn10_over_q10ref": (None if pd.isna(s10.iloc[i]) or pd.isna(q10_10.iloc[i]) else round(float(s10.iloc[i] / q10_10.iloc[i]), 3)),
            "std20_open": bool(std20_open.iloc[i]) if dec_s20.iloc[i] else None,
            "roc20_sign": ("pos" if roc20.iloc[i] > 0 else ("neg" if roc20.iloc[i] < 0 else "zero")) if (not pd.isna(roc20.iloc[i]) and dec_n10.iloc[i]) else None}
    facts["extreme_day_states"] = est

    # ---- census-style forward differential (descriptive face, NOT a claim) ----
    for fw in (5, 20):
        fwd = c.shift(-fw) / c - 1.0
        base = dec_n10 & fwd.notna()
        a = fwd[n10_open & base]
        b = fwd[(~n10_open & dec_n10) & base]
        facts[f"forward_{fw}d"] = {
            "n_open": int(len(a)), "n_closed": int(len(b)),
            "mean_fwd_open": round(float(a.mean()), 6) if len(a) else float("nan"),
            "mean_fwd_closed": round(float(b.mean()), 6) if len(b) else float("nan"),
            "diff_open_minus_closed": round(float(a.mean() - b.mean()), 6) if (len(a) and len(b)) else float("nan"),
            "welch_t": tstats(a, b),
            "note": "descriptive probe face on 510300 anchor only; census/recheck universe face = A158-TSGATE-P1 OOS med_t +1.063/+1.000 (1,724 codes) + GATE-RECHECK 5-member CONFIRM (clusters #20/#21); NOT a strategy claim; overlapping windows inflate |t|"}
    # grind decomposition face (composition divergence core: quiet gain-dominated)
    for fw in (20,):
        fwd = c.shift(-fw) / c - 1.0
        base = dec_n10 & fwd.notna() & med500.notna()
        a = fwd[n10_open & calm & base]
        b = fwd[n10_open & wild & base]
        facts["grind_face_forward_20d"] = {
            "n_open_calm": int(len(a)), "n_open_wild": int(len(b)),
            "mean_fwd_open_calm": round(float(a.mean()), 6) if len(a) else float("nan"),
            "mean_fwd_open_wild": round(float(b.mean()), 6) if len(b) else float("nan"),
            "welch_t_calm_vs_wild": tstats(a, b),
            "note": "sumn10_open days split by burned W4 VOL face: calm side = quiet-grind increment face; descriptive only"}
    # direction-split forward face (direction-EMBEDDED honesty mirror of W12)
    for fw in (20,):
        fwd = c.shift(-fw) / c - 1.0
        base = dec_n10 & fwd.notna() & roc20.notna()
        a = fwd[n10_open & (roc20 > 0) & base]
        b = fwd[n10_open & (roc20 <= 0) & base]
        facts["direction_split_forward_20d"] = {
            "n_roc20_pos": int(len(a)), "n_roc20_neg": int(len(b)),
            "mean_fwd_roc20_pos": round(float(a.mean()), 6) if len(a) else float("nan"),
            "mean_fwd_roc20_neg": round(float(b.mean()), 6) if len(b) else float("nan"),
            "welch_t_pos_vs_neg": tstats(a, b),
            "note": "SUMN-low is direction-EMBEDDED (up-tilted); the few open-days with negative roc20 = flat-with-few-losses face; honest readout, direction premium asymmetry (if any) disclosed"}

    # ---- core48 member-level SUMN10_q10 open-rate spread (real roster) ---------
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    rates = {}
    for sym, d2 in sorted(prices.items()):
        d2 = d2[d2.index <= cut]
        if len(d2) >= 260:
            # .to_numpy() first: dict-of-Series construction ALIGNs to the
            # given RangeIndex -> all-NaN reindex artifact (r447 live pit)
            di2 = pd.DataFrame({"open": d2["open"].to_numpy(), "high": d2["high"].to_numpy(),
                                "low": d2["low"].to_numpy(), "close": d2["close"].to_numpy(),
                                "volume": d2["volume"].to_numpy()},
                               index=pd.RangeIndex(len(d2)))
            F2 = a158.alpha158_factors(di2)
            op2, dv2, _ = sumn_gate(F2["SUMN10"])
            if dv2.any():
                rates[str(sym)] = round(float((op2 & dv2).mean()), 4)
    vals = sorted(rates.values())
    facts["core48_sumn10_open_rate"] = {
        "n": len(vals),
        "min": round(vals[0], 4), "median": round(vals[len(vals) // 2], 4),
        "max": round(vals[-1], 4),
        "method": "tl1.load_core() roster (import-reuse via r237 lineage, real core48 face) + frozen-runner SUMN verbatim",
        "members_with_lt260_rows_excluded": len(prices) - len(vals)}

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in facts.items() if not isinstance(v, dict)}, ensure_ascii=False))
    print("sumn10 face: decidable", facts["sumn10_decidable_days"],
          "| open", facts["sumn10_open_days"], "| open_rate", facts["sumn10_open_rate_on_decidable"])
    print("sumn20 face: decidable", facts["sumn20_decidable_days"],
          "| open", facts["sumn20_open_days"], "| open_rate", facts["sumn20_open_rate_on_decidable"])
    print("cluster identity vs SUMP10_hi:", facts_cluster["both_open_days_vs_sump"],
          "/", facts_cluster["sumn10_open_days"], "vs SUMD10_hi:", facts_cluster["both_open_days_vs_sumd"])
    print("512-cell: nonempty", facts["nine_gate_512_cells_nonzero_count"], "empty", facts["nine_gate_512_cells_empty_count"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
