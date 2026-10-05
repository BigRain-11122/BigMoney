# -*- coding: utf-8 -*-
"""W16-candidate gate probe: MAX30_q10 + RANK30_q90 (A158-TSGATE-P1 48-PASS pool
unconsumed order #5/#8, bench-archived by bm-b r470 draft; probe = the W16 supply
line's next transaction per r277/r470 lineage). Candidates are W-grammar supply
faces on the FROZEN 510300 anchor panel (P-5C cutoff 2026-09-22, 3,483 rows).

Laws honored:
- frozen runner verbatim-import (scripts/a158_tsgate_probe.py: alpha158_factors
  + gate_universe + GATE_WIN/GATE_MINP/QLOW/QHIGH constants; zero re-impl)
- burned-axis gate block verbatim from results/_r470bmb_vsumd_resi_w14_probe.py
  lineage (r237p W3-W11 faces + w13p sumn gate + inline W3-W6 states), plus
  W14 axes now burned (RESI60_hi, CNTD10_hi via hi_gate on runner features)
- double-run byte identity (r277/r470 血统), GBK console reconfigure entry (r236)
- probe facts only, no ledger writes, no prereg numbers pre-written (占位纪律)
"""
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")  # r236 GBK console entry law
sys.path.insert(0, os.path.join("scripts"))
sys.path.insert(0, os.path.join("results"))
sys.path.insert(0, os.path.join(".codely-cli", "scripts-archive"))  # r624 archive law
import pandas as pd

import a158_tsgate_probe as a158           # frozen runner (MAX/RANK verbatim)
import _r237bmc_stdq90_w11_probe as r237p  # frozen W11 probe (W3-W11 faces)
import _r456bma_sumnsump_w13_probe as w13p  # frozen W13 probe (sumn gate verbatim)

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4-W15 probes
OUT = "results/_r720bma_maxrank_w16_probe_facts.json"
GATE_RECHECK = "results/gate_recheck_a158.json"
EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]
CANDS = ["MAX30_q10", "RANK30_q90"]
FAMILY_MIRRORS = ["MAX30_q90", "RANK30_q10"]


def hi_gate(f):
    """A158 frozen high-side gate semantics via runner constants (r470 verbatim)."""
    qref = f.rolling(a158.GATE_WIN, min_periods=a158.GATE_MINP).quantile(a158.QHIGH)
    dec = f.notna() & qref.notna()
    return (f > qref) & dec, dec, qref


def tstats(a, b):
    return r237p.tstats(a, b)  # frozen Welch-t helper (r237 verbatim)


def build_facts():
    df = pd.read_csv(os.path.join("data", "daily", "sh510300.csv"))
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)
    n = len(df)
    assert n == 3483, "row count %d != 3483 (W4-W15 probe anchor)" % n
    assert df["date"].iloc[-1] == CUTOFF

    o, h, l, c, v = (df[k] for k in ("open", "high", "low", "close", "volume"))
    ret = c.pct_change()
    zero_amp = int(((h - l).abs() < 1e-12).sum())

    # --- candidate faces: frozen runner verbatim (gate_universe consumption) ---
    F = a158.alpha158_factors(df)
    gu = {name: (op, dec) for name, op, dec in a158.gate_universe(F)}
    cand_ops, cand = {}, {}
    for name in CANDS + FAMILY_MIRRORS:
        op, dec = gu[name]
        cand_ops[name] = op
        cand[name] = {"n_open": int(op.sum()), "n_dec": int(dec.sum())}

    warmup = {}
    for name in CANDS + FAMILY_MIRRORS:
        warmup[name] = int(gu[name][1].idxmax()) if int(gu[name][1].sum()) else -1

    # --- burned-axes gate days (r470 inherited block verbatim + W14 additions) ---
    amp, med20amp, wide = r237p.amp_faces(df)
    amp_known = wide.notna()
    st = r237p.streak_faces(df)
    up_st, dn_st = st == 1.0, st == -1.0
    mad_q10, rsv_low, decidable, rsv60 = r237p.tstate_faces(df)
    # lineage cross-check vs r431 W9 probe facts (r470 verbatim pattern): guards
    # the decidable-vs-open mask bug caught in-window (dec_mad/dec_rsv are
    # decidables ~always-True, NOT the W8 open masks)
    f31 = json.load(io.open("results/_r431bmb_ampgate_w9_probe_facts.json",
                            encoding="utf-8"))
    cc = f31["amp_tstate_cross"]["cross_cells"]
    assert int(mad_q10.sum()) == cc["mad60_and_wide"] + cc["mad60_and_narrow"], \
        "W8 mad60 open count mismatch vs r431 facts"
    assert int(rsv_low.sum()) == cc["rsv60_and_wide"] + cc["rsv60_and_narrow"], \
        "W8 rsv60 open count mismatch vs r431 facts"
    roc20, q10mom, mom_open, dec_mom = r237p.mom_faces(df)
    std20, q90s_20, std20_open, dec_s20 = r237p.std_faces(df, 20)
    std10, q90s_10, std10_open, dec_s10 = r237p.std_faces(df, 10)
    r20_open, dec_r20, _ = hi_gate(F["RSQR20"])
    sn20_open, dec_sn20, _ = w13p.sumn_gate(F["SUMN20"])
    resi60_open, dec_resi, _ = hi_gate(F["RESI60"])   # W14 burned axis
    cntd10_open, dec_cntd, _ = hi_gate(F["CNTD10"])   # W14 burned axis

    ma200 = c.rolling(200, min_periods=200).mean()
    bull, bear = c > ma200, c <= ma200
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    calm, wild = vol20 <= med500, vol20 > med500
    med20v = v.rolling(20, min_periods=20).median()
    surge, dry = v > med20v, v <= med20v
    yang = c > o
    first_yang = yang & ~yang.shift(1).fillna(False)

    burned = {
        "gate_bull": bull, "gate_bear": bear,
        "vol_calm": calm & med500.notna(), "vol_wild": wild & med500.notna(),
        "yang_first": first_yang, "vconf_surge": surge & med20v.notna(),
        "vconf_dry": dry & med20v.notna(),
        "streak_up2": up_st, "streak_dn2": dn_st,
        "tstate_deep_pullback": mad_q10, "tstate_oversold_rsv": rsv_low,
        "mom_q10": mom_open, "std20_hi": std20_open, "std10_hi": std10_open,
        "rsqr20_hi": r20_open & dec_r20, "sumn20_hi": sn20_open & dec_sn20,
        "resi60_hi(W14)": resi60_open & dec_resi, "cntd10_hi(W14)": cntd10_open & dec_cntd,
        "amp_wide": (wide == 1) & amp_known, "amp_narrow": (wide == 0) & amp_known,
    }
    burned = {k: v.fillna(False).astype(bool) for k, v in burned.items()}

    # --- co-open matrices + DEMOTE-line containment (98.5% VSTD law) ---
    coopen = {}
    for cn in CANDS + FAMILY_MIRRORS:
        op = cand_ops[cn]
        n_new = int(op.sum())
        row = {}
        for bn, bop in burned.items():
            nb = int((op & bop).sum())
            row[bn] = {"both": nb, "new_only": n_new - nb,
                       "burned_only": int(bop.sum()) - nb,
                       "containment_of_new": round(nb / n_new, 4) if n_new else None}
        coopen[cn] = row
    # mutual adjacency of the two candidates (near-mirror family disclosure)
    a0, b0 = cand_ops["MAX30_q10"], cand_ops["RANK30_q90"]
    na, nbb = int(a0.sum()), int((a0 & b0).sum())
    mutual = {"both": nbb, "max30q10_only": na - nbb,
              "rank30q90_only": int(b0.sum()) - nbb,
              "max30q10_in_rank30q90": round(nbb / na, 4) if na else None,
              "rank30q90_in_max30q10": round(nbb / int(b0.sum()), 4) if int(b0.sum()) else None,
              "xor_days": int((a0 ^ b0).sum())}

    # --- forward 20d split: calm vs wild (four-wave wild-concentration check) ---
    fwd20 = c.shift(-20) / c - 1
    fwd = {}
    for cn in CANDS:
        op = cand_ops[cn]
        fc, fw = fwd20[op & calm], fwd20[op & wild]
        entry = {}
        for k, s in (("calm", fc), ("wild", fw)):
            s = s.dropna()
            entry[k] = {"n": int(len(s)), "mean_fwd20": round(float(s.mean()), 5) if len(s) else None}
        if len(fc.dropna()) > 2 and len(fw.dropna()) > 2:
            entry["t_calm_vs_wild"] = round(float(tstats(fc.dropna(), fw.dropna())), 3)
        entry["up_day_share_on_open"] = round(float((ret[op] > 0).mean()), 4) if int(op.sum()) else None
        entry["fwd20_on_up"] = (round(float(fwd20[op & (ret > 0)].dropna().mean()), 5)
                                if int((op & (ret > 0)).sum()) else None)
        entry["fwd20_on_dn"] = (round(float(fwd20[op & (ret <= 0)].dropna().mean()), 5)
                                if int((op & (ret <= 0)).sum()) else None)
        fwd[cn] = entry

    # --- extreme-day states (7 frozen days) ---
    dser = df["date"]
    extreme = {}
    for cn in CANDS + FAMILY_MIRRORS:
        op = cand_ops[cn]
        extreme[cn] = {d: bool(op.iloc[list(dser).index(d)])
                       if d in set(dser) else None for d in EXTREME_DAYS}

    # --- GATE-RECHECK disclosure (reference only, not fail-closed) ---
    recheck = {}
    try:
        gr = json.load(io.open(GATE_RECHECK, encoding="utf-8"))
        blob = json.dumps(gr)
        for cn in CANDS:
            recheck[cn] = ("present-in-recheck" if cn.split("_")[0] in blob
                           else "not-in-recheck-roster (disclosure: A158-TSGATE-P1 "
                                "main census face is the reference)")
    except Exception as e:
        recheck = {"error": str(e)[:80]}

    facts = {
        "probe": "W16 candidate gate probe MAX30_q10 + RANK30_q90",
        "lineage": "r277/r470 probe paradigm; a158 frozen runner verbatim-import; "
                   "burned-axis block r470 verbatim + W14 axes (RESI60_hi/CNTD10_hi) "
                   "added as burned since W14/N2-W15 consumption",
        "supply_source": "A158-TSGATE-P1 48-PASS pool unconsumed order #5/#8 "
                         "(bench-archived by bm-b r470 draft sec. supply pool)",
        "cutoff": CUTOFF, "rows": int(n), "first_date": str(dser.iloc[0]),
        "last_date": str(dser.iloc[-1]), "zero_range_rows": zero_amp,
        "construction_disclosure": {
            "MAX30": "MAX30=high.rolling(30).max()/close (frozen runner); MAX30_q10 "
                     "= close NEAR its 30d high (breakout-position face, LOW side of "
                     "the ratio); nearest burned = W8 RSV60 family (range position, "
                     "but W8 burned the LOW side oversold_rsv60_low02; high side "
                     "unburned) + W14 RESI60_hi (trend deviation above trend)",
            "RANK30": "RANK30=close.rolling(30).rank(pct=True) (frozen runner); "
                      "RANK30_q90 = close at top percentile of own 30d range "
                      "(range-top face); mutual near-mirror with MAX30_q10 measured "
                      "in mutual_adjacency",
        },
        "candidates": {k: {kk: vv for kk, vv in v.items()} for k, v in cand.items()},
        "warmup_first_decidable_idx": warmup,
        "coopen_vs_burned": coopen,
        "mutual_adjacency_max30q10_vs_rank30q90": mutual,
        "forward20_split": fwd,
        "extreme_day_states": extreme,
        "gate_recheck_disclosure": recheck,
        "demote_line_note": "VSTD20 DEMOTE precedent: containment >= 98.5% with "
                            "<11-day increment = axis demoted (r234 law)",
    }
    return facts


def main() -> int:
    f1 = build_facts()
    f2 = build_facts()
    b1 = json.dumps(f1, ensure_ascii=False, sort_keys=True).encode("utf-8")
    b2 = json.dumps(f2, ensure_ascii=False, sort_keys=True).encode("utf-8")
    sha = hashlib.sha256(b1).hexdigest()
    assert b1 == b2, "double-run byte identity FAILED"
    f1["self_double_run_sha256"] = sha
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(f1, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print("facts written:", OUT)
    print("sha256(sorted-facts):", sha[:16].upper(), "double-run identity PASS")
    for cn in CANDS:
        v = f1["candidates"][cn]
        print("%s: open=%d dec=%d warmup_idx=%d" %
              (cn, v["n_open"], v["n_dec"], f1["warmup_first_decidable_idx"][cn]))
    m = f1["mutual_adjacency_max30q10_vs_rank30q90"]
    print("mutual: both=%d max30_only=%d rank30_only=%d xor=%d" %
          (m["both"], m["max30q10_only"], m["rank30q90_only"], m["xor_days"]))
    top = sorted(((bn, r["containment_of_new"])
                  for bn, r in f1["coopen_vs_burned"]["MAX30_q10"].items()
                  if r["containment_of_new"] is not None),
                 key=lambda x: -x[1])[:3]
    print("MAX30_q10 top containment:", top)
    top2 = sorted(((bn, r["containment_of_new"])
                   for bn, r in f1["coopen_vs_burned"]["RANK30_q90"].items()
                   if r["containment_of_new"] is not None),
                  key=lambda x: -x[1])[:3]
    print("RANK30_q90 top containment:", top2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
