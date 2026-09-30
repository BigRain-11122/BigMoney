# -*- coding: utf-8 -*-
"""_r471bmb_cntn20_w14_supplement.py -- W14 freeze-window supplement probe:
completes the cntn20_lo member's missing D6 disclosure faces that the r470
berth probe did not carry (it probed cntn20 at core-facts level only).

Adjudication context (bm-b r471 freeze step, adoption MSG-154x): GATE-RECHECK
roster readings demote bm-c draft's second windows RESI30_q90/CNTD10_q90
(both RECHECK-FAIL + C1-demotion) and confirm RESI60_q90/CNTD5_q90/CNTN20_q10
-> adjudicated axis members RESI{none,resi60_hi} + CNTD{none,cntd5_hi,cntn20_lo}.
This supplement brings cntn20_lo to the same fail-closed disclosure standard
as resi60/cntd5 (nine-gate 512-cell matrix + full burned-axes adjacency +
grind/direction splits + mirror XOR + distinct-space increments + core48
spread), and re-asserts the r470 anchor facts for the other members
(verbatim-import discipline, zero re-implementation of constructions).

Deterministic, zero network, read-only, marks +0, SEED +0. Dual-run byte
identity required (freeze-window anchor verification face).
"""
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join("scripts"))
sys.path.insert(0, os.path.join("results"))
import a158_tsgate_probe as a158            # frozen runner (CNTN/CNTD/RESI verbatim)
import _r237bmc_stdq90_w11_probe as r237p   # frozen W11 probe (W3-W11 faces)
import _r456bma_sumnsump_w13_probe as w13p   # frozen W13 probe (sumn gate verbatim)
import trial_labor_w1 as tl1                # via r237 lineage (core48 loader)

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4-W13 probes
OUT = "results/_r471bmb_cntn20_w14_supplement_facts.json"
R470_FACTS = "results/_r470bmb_vsumd_resi_w14_probe_facts.json"
GATE_RECHECK = "results/gate_recheck_a158.json"
EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]


def hi_gate(f):
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
    zero_amp = int((df["high"] == df["low"]).sum())
    assert zero_amp == 0, "zero-range rows != 0 (r417 anchor)"

    c, h, l, v, o = (df[k] for k in ("close", "high", "low", "volume", "open"))

    di = pd.DataFrame({"open": o, "high": h, "low": l, "close": c, "volume": v},
                      index=pd.RangeIndex(n))
    F = a158.alpha158_factors(di)
    cn20, cd20, cp20 = F["CNTN20"], F["CNTD20"], F["CNTP20"]
    cd5, resi60, beta20, rsqr20 = F["CNTD5"], F["RESI60"], F["BETA20"], F["RSQR20"]
    cn20_open, dec_cn20, _ = w13p.sumn_gate(cn20)   # CNTN20_q10 low side (CONFIRM rep)
    cd20_open, dec_cd20, _ = hi_gate(cd20)          # same-window mirror, high side
    cd5_open, dec_cd5, _ = hi_gate(cd5)             # r470 anchor member
    re60_open, dec_re60, _ = hi_gate(resi60)        # r470 anchor member

    # warmup fail-closed (r470 CNT-family law: first-decidable 119)
    for tag, dec, first_expect in (("cntn20", dec_cn20, 119),
                                   ("cntd20", dec_cd20, 119),
                                   ("cntd5", dec_cd5, 119),
                                   ("resi60", dec_re60, 120)):
        first_dec = int(np.argmax(dec.to_numpy()))
        assert first_dec == first_expect, f"{tag} first decidable {first_dec} != {first_expect}"

    # r470 anchor alignment (freeze-window 逐位对账 face)
    f70 = json.load(open(R470_FACTS, encoding="utf-8"))
    assert f70["cntn20_decidable_days"] == int(dec_cn20.sum()) == 3364
    assert f70["cntn20_open_days"] == int((cn20_open & dec_cn20).sum()) == 265
    assert f70["resi60_decidable_days"] == int(dec_re60.sum()) == 3363
    assert f70["resi60_open_days"] == int((re60_open & dec_re60).sum()) == 390
    assert f70["cntd5_decidable_days"] == int(dec_cd5.sum()) == 3364
    assert f70["cntd5_open_days"] == int((cd5_open & dec_cd5).sum()) == 137

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
    r20_open, dec_r20, _ = hi_gate(rsqr20)
    sn20 = F["SUMN20"]
    sn20_open, dec_sn20, _ = w13p.sumn_gate(sn20)

    ma200 = c.rolling(200, min_periods=200).mean()
    bull, bear = c > ma200, c <= ma200
    ret = c.pct_change()
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    calm, wild = vol20 <= med500, vol20 > med500
    med20v = v.rolling(20, min_periods=20).median()
    surge = v > med20v
    yang = c > o

    facts = {"cutoff": CUTOFF, "rows": int(n), "zero_range_rows": zero_amp,
             "probe_lineage": "r470 W14 berth probe supplement (bm-b r471 freeze window); "
                              "a158 frozen runner verbatim-import; r237/w13 frozen faces "
                              "verbatim; GATE-RECHECK adjudication face "
                              "(RESI30/CNTD10 FAIL-demote, CNTN20 CONFIRM promote)",
             "adjudication_disclosure": {
                 "draft_member_set": "RESI{resi60_hi,resi30_hi} + CNTD{cntd10_hi,cntd5_hi} (pool OOS top-two per family)",
                 "recheck_verdicts": {"RESI60_q90": "RECHECK-CONFIRM (face_a med_net +0.005699)",
                                      "RESI30_q90": "RECHECK-FAIL (face_a med_net -0.006028 sign-flip vs P1 OOS 0.433) + c1_demotion list",
                                      "CNTD10_q90": "RECHECK-FAIL + c1_demotion list",
                                      "CNTD5_q90": "RECHECK-CONFIRM (face_a med_net +0.009845)",
                                      "CNTN20_q10": "RECHECK-CONFIRM (face_a med_net +0.007839)",
                                      "CNTD20_q90": "ABSENT from recheck (below threshold / cluster-eliminated; same-window construction twin of cntn20_lo, disclosed not-taken)"},
                 "adjudicated_member_set": "RESI{none,resi60_hi} + CNTD{none,cntd5_hi,cntn20_lo} (evidence-forced single RESI window disclosed; CNTD family spans 5d net-dominance high + 20d down-share low)",
                 "axis_multiplier": "2 x 3 = 6 (draft announced 9 with both-3-value axes; adjudication carries recheck evidence)"}}

    for tag, dec, op in (("cntn20", dec_cn20, cn20_open),
                         ("cntd20", dec_cd20, cd20_open)):
        facts[f"{tag}_decidable_days"] = int(dec.sum())
        facts[f"{tag}_open_days"] = int((op & dec).sum())
        facts[f"{tag}_open_rate_on_decidable"] = round(float((op & dec).mean()), 4)

    # ---- mirror faces: CNTN20_q10 vs CNTD20_q90 (construction mirror, XOR not necessarily 0) ----
    both_nd = (cp20 + cn20).dropna()
    xor_nd = int((cn20_open ^ cd20_open).sum())
    both_nd_open = int((cn20_open & cd20_open & (dec_cn20 & dec_cd20)).sum())
    facts["mirror_identity"] = {
        "cntp20_plus_cntn20_max_dev": float((both_nd - 1.0).abs().max()),
        "cntp20_plus_cntn20_lt1_days": int(((cp20 + cn20) < 1.0 - 1e-12).sum()),
        "cntn20_q10_vs_cntd20_q90_xor_days": xor_nd,
        "cntn20_q10_vs_cntd20_q90_both_open_days": both_nd_open,
        "note": "CNTD=CNTP-CNTN strictly-decreasing affine of CNTN pointwise -> q10-side "
                "CNTN gate should fire same days as CNTD20_q90, BUT zero/flat-change days "
                "(CNTP+CNTN<1) move both toward 0 and quantile rank-flips make XOR>0 legal "
                "(draft sec.2 mirror-twin note: XOR not necessarily 0, empirical item)"}

    # ---- full burned-axes adjacency (cntn20 as member a) --------------------
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

    facts["adjacency_cntn20"] = {
        "cntn20_vs_wild": cell(cn20_open, dec_cn20, wild, med500.notna()),
        "cntn20_vs_calm": cell(cn20_open, dec_cn20, calm, med500.notna()),
        "cntn20_vs_wide": cell(cn20_open, dec_cn20, wide == 1, amp_known),
        "cntn20_vs_narrow": cell(cn20_open, dec_cn20, wide == 0, amp_known),
        "cntn20_vs_mad60": cell(cn20_open, dec_cn20, mad_q10, dec_mad),
        "cntn20_vs_rsv60": cell(cn20_open, dec_cn20, rsv_low, dec_rsv),
        "cntn20_vs_downstreak": cell(cn20_open, dec_cn20, dn_st, st.notna()),
        "cntn20_vs_upstreak": cell(cn20_open, dec_cn20, up_st, st.notna()),
        "cntn20_vs_mom": cell(cn20_open, dec_cn20, mom_open, dec_mom),
        "cntn20_vs_std20": cell(cn20_open, dec_cn20, std20_open, dec_s20),
        "cntn20_vs_rsqr20": cell(cn20_open, dec_cn20, r20_open, dec_r20),
        "cntn20_vs_sumn20": cell(cn20_open, dec_cn20, sn20_open, dec_sn20),
        "cntn20_vs_resi60": cell(cn20_open, dec_cn20, re60_open, dec_re60),
        "cntn20_vs_cntd5": cell(cn20_open, dec_cn20, cd5_open, dec_cd5),
        "cntn20_vs_cntd20": cell(cn20_open, dec_cn20, cd20_open, dec_cd20),
        "cntn20_vs_surge": cell(cn20_open, dec_cn20, surge, med20v.notna()),
        "cntn20_vs_bull": cell(cn20_open, dec_cn20, bull, ma200.notna()),
        "cntn20_vs_bear": cell(cn20_open, dec_cn20, bear, ma200.notna())}

    facts["distinct_space_increment_cntn20"] = {
        "cntn20_open_and_sumn20_closed_days": int((cn20_open & (~sn20_open & dec_sn20) & (dec_cn20 & dec_sn20)).sum()),
        "cntn20_open_and_sumn20_open_days": int((cn20_open & sn20_open & (dec_cn20 & dec_sn20)).sum()),
        "cntn20_open_and_upstreak_closed_days": int((cn20_open & (~up_st & st.notna()) & (dec_cn20 & st.notna())).sum()),
        "cntn20_open_and_cntd5_closed_days": int((cn20_open & (~cd5_open & dec_cd5) & (dec_cn20 & dec_cd5)).sum()),
        "cntn20_open_and_cntd5_open_days": int((cn20_open & cd5_open & (dec_cn20 & dec_cd5)).sum()),
        "cntn20_open_and_resi60_open_days": int((cn20_open & re60_open & (dec_cn20 & dec_re60)).sum()),
        "cntn20_open_and_resi60_closed_days": int((cn20_open & (~re60_open & dec_re60) & (dec_cn20 & dec_re60)).sum()),
        "note": "cntn20_open while SUMN closed = down-day FREQUENCY low without price-magnitude "
                "dominance (few-down-day grind face) = frequency-vs-purity divergence vs W13; "
                "cntn20∧upstreak_closed = persistence WITHOUT 2-day streak momentum"}

    # ---- nine-gate 512-cell crossing (cntn20 as the 9th, W13 pattern) ------
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

    cells_cn, empty_cn, m9_cn = grid9(cn20_open, dec_cn20, "cntn20")
    facts["cntn20_nine_gate_512_cells_empty_count"] = empty_cn
    facts["cntn20_nine_gate_512_cells_nonzero_count"] = 512 - empty_cn
    facts["cntn20_nine_gate_512_cells_min_nonzero"] = min([x for x in cells_cn.values() if x > 0] or [0])
    facts["cntn20_nine_gate_512_cells_max"] = max(cells_cn.values())
    facts["cntn20_nine_gate_all_decidable_days"] = m9_cn
    facts["cntn20_nine_gate_cells"] = cells_cn

    # ---- forward faces (descriptive only) ------------------------------------
    for fw in (5, 20):
        fwd = c.shift(-fw) / c - 1.0
        base = dec_cn20 & fwd.notna()
        a = fwd[cn20_open & base]
        b = fwd[(~cn20_open & dec_cn20) & base]
        facts[f"cntn20_forward_{fw}d"] = {
            "n_open": int(len(a)), "n_closed": int(len(b)),
            "mean_fwd_open": round(float(a.mean()), 6) if len(a) else float("nan"),
            "mean_fwd_closed": round(float(b.mean()), 6) if len(b) else float("nan"),
            "diff_open_minus_closed": round(float(a.mean() - b.mean()), 6) if (len(a) and len(b)) else float("nan"),
            "welch_t": tstats(a, b),
            "note": "descriptive probe face on 510300 anchor only; recheck-universe face = "
                    "GATE-RECHECK CNTN20_q10 CONFIRM (OOS med_t 0.617, face_a med_net +0.007839); "
                    "NOT a strategy claim; overlapping windows inflate |t|"}
    # grind decomposition (calm-vs-wild)
    fwd = c.shift(-20) / c - 1.0
    base = dec_cn20 & fwd.notna() & med500.notna()
    a = fwd[cn20_open & calm & base]
    b = fwd[cn20_open & wild & base]
    facts["cntn20_grind_face_forward_20d"] = {
        "n_open_calm": int(len(a)), "n_open_wild": int(len(b)),
        "mean_fwd_open_calm": round(float(a.mean()), 6) if len(a) else float("nan"),
        "mean_fwd_open_wild": round(float(b.mean()), 6) if len(b) else float("nan"),
        "welch_t_calm_vs_wild": tstats(a, b),
        "note": "open days split by burned W4 VOL face: calm side = clean-grind increment face; descriptive only"}
    # direction split (BETA20 sign)
    base = dec_cn20 & fwd.notna() & beta20.notna()
    a = fwd[cn20_open & (beta20 > 0) & base]
    b = fwd[cn20_open & (beta20 <= 0) & base]
    facts["cntn20_direction_split_forward_20d"] = {
        "n_up_slope": int(len(a)), "n_down_slope": int(len(b)),
        "mean_fwd_up": round(float(a.mean()), 6) if len(a) else float("nan"),
        "mean_fwd_down": round(float(b.mean()), 6) if len(b) else float("nan"),
        "welch_t_up_vs_down": tstats(a, b),
        "note": "slope-split forward readout (BETA20 from same frozen runner); descriptive only"}

    # ---- extreme days: state readout -----------------------------------------
    est = {}
    for dstr in EXTREME_DAYS:
        idx = df.index[df["date"] == dstr]
        if len(idx) == 0:
            est[dstr] = "not-in-panel"
            continue
        i = int(idx[0])
        est[dstr] = {
            "cntn20_open": bool(cn20_open.iloc[i]) if dec_cn20.iloc[i] else None,
            "cntd5_open": bool(cd5_open.iloc[i]) if dec_cd5.iloc[i] else None,
            "resi60_open": bool(re60_open.iloc[i]) if dec_re60.iloc[i] else None,
            "cntn20_value": (None if pd.isna(cn20.iloc[i]) else round(float(cn20.iloc[i]), 6)),
            "cntd20_value": (None if pd.isna(cd20.iloc[i]) else round(float(cd20.iloc[i]), 6)),
            "sumn20_open": bool(sn20_open.iloc[i]) if dec_sn20.iloc[i] else None,
            "upstreak": bool(up_st.iloc[i]) if (not pd.isna(st.iloc[i])) else None}
    facts["extreme_day_states"] = est

    # ---- GATE-RECHECK roster ref (adjudication material, disclosure face) ----
    gr = json.load(open(GATE_RECHECK, encoding="utf-8"))
    refs = {}
    for gname in ("RESI60_q90", "CNTD5_q90", "CNTN20_q10"):
        g = gr["gates"][gname]
        refs[gname] = {"verdict": g["verdict"],
                       "p1_oos_med_t": g["p1_oos_med_t"],
                       "face_a_med_net_510300": g["face_a"]["members"]["510300"]["net"]}
    facts["gate_recheck_refs"] = refs

    # ---- core48 member-level cntn20 open-rate spread (real roster) -----------
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    rates_n = {}
    for sym, d2 in sorted(prices.items()):
        d2 = d2[d2.index <= cut]
        if len(d2) >= 260:
            di2 = pd.DataFrame({"open": d2["open"].to_numpy(), "high": d2["high"].to_numpy(),
                                "low": d2["low"].to_numpy(), "close": d2["close"].to_numpy(),
                                "volume": d2["volume"].to_numpy()},
                               index=pd.RangeIndex(len(d2)))
            F2 = a158.alpha158_factors(di2)
            op2n, dv2n, _ = w13p.sumn_gate(F2["CNTN20"])
            if dv2n.any():
                rates_n[str(sym)] = round(float((op2n & dv2n).mean()), 4)
    vals_n = sorted(rates_n.values())
    facts["core48_cntn20_open_rate"] = {
        "n": len(vals_n),
        "min": round(vals_n[0], 4), "median": round(vals_n[len(vals_n) // 2], 4),
        "max": round(vals_n[-1], 4),
        "method": "tl1.load_core() roster + frozen-runner CNTN20 low-side gate verbatim",
        "members_with_lt260_rows_excluded": len(prices) - len(vals_n)}

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in facts.items() if not isinstance(v, dict)}, ensure_ascii=False))
    print("mirror:", json.dumps(facts["mirror_identity"], ensure_ascii=False))
    print("cntn20 adjacency:", json.dumps(facts["adjacency_cntn20"], ensure_ascii=False))
    print("cntn20 distinct:", json.dumps(facts["distinct_space_increment_cntn20"], ensure_ascii=False))
    print("cntn20 512-cells: empty", facts["cntn20_nine_gate_512_cells_empty_count"],
          "| nonzero", facts["cntn20_nine_gate_512_cells_nonzero_count"],
          "| all-decidable", facts["cntn20_nine_gate_all_decidable_days"])
    print("cntn20 grind:", json.dumps(facts["cntn20_grind_face_forward_20d"], ensure_ascii=False))
    print("cntn20 dirsplit:", json.dumps(facts["cntn20_direction_split_forward_20d"], ensure_ascii=False))
    print("cntn20 fwd20d:", json.dumps(facts["cntn20_forward_20d"], ensure_ascii=False))
    print("recheck refs:", json.dumps(facts["gate_recheck_refs"], ensure_ascii=False))
    print("core48 cntn20 open rate:", json.dumps(facts["core48_cntn20_open_rate"], ensure_ascii=False))
    print("W14 cntn20 supplement facts ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
