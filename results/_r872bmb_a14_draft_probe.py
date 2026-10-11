# -*- coding: utf-8 -*-
"""r872 bm-b T26 slice-1 fact probe (read-only, zero shared-face writes).

A14-PREDFACE draft-window facts (PREREG_TEMPLATE sec.2 pre-probe truth):
 1) five-member anchor rows + tail date at evidence_cutoff 2026-10-09
    (raw pd.read_csv truncation face, G-ANCHOR-FACE four-tuple);
 2) machinery import face: sg / tpl / fv / probe(A158) / mp1 / t23 all
    import clean;
 3) per-member 22-gate computability: A158 17 CONFIRM (fv.GATES17) +
    MP1 5 CONFIRM (gate_recheck_mp1.json library_entries) -- mask-mean
    features f_c2 / f_mp1 / f_c2v4 constructible, AND-decidable starts;
 4) MP1 anchor reproduction at this cutoff (510300 DELTA(VOLUME,30)_q10
    dec==3341 open==390 first==149, G-ANCHOR-MP1 in-probe re-derivation);
 5) RAW-face window pair counts (stride-20, IS<=2016-12-31 / OOS>=2017)
    per (member, feature) + RESID-face master intersection counts;
 6) feature cross-correlation disclosure face (f_c2 ~ f_mp1 ~ f_c2v4).

Output: results/_r872bmb_a14_draft_probe.json (advisory facts only,
zero verdicts, zero ledger, zero registry writes)."""
import json
import os
import sys

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (os.path.join(_ROOT, "scripts"), _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # r236 GBK law

import science_gates as sg                     # noqa: E402
import t101_v4_a2_prescreen as tpl             # noqa: E402
import t101_v4_a158_fv as fv                   # noqa: E402
import a158_tsgate_probe as probe              # noqa: E402
import mp1_tsgate_probe as mp1                  # noqa: E402

CUTOFF = "2026-10-09"
SPLIT = tpl.SPLIT                              # 2017-01-01 family constant
STRIDE = 20
FWD = 20
MEMBERS = ["510300", "510050", "510500", "512100", "588000"]
IS_ELIGIBLE = ["510300", "510050", "510500"]
FEATURES = ["f_c2v4", "f_mp1", "f_c2"]
ANCHOR_FACE = {c: "data/daily/sh%s.csv" % c for c in MEMBERS}

RECHECK = json.load(open(os.path.join(os.path.dirname(os.path.abspath(
    __file__)), "gate_recheck_mp1.json"), encoding="utf-8"))
MP1_CONFIRM = sorted(e["gate"] if isinstance(e, dict) else e
                     for e in RECHECK["library_entries"])
assert len(MP1_CONFIRM) == 5, MP1_CONFIRM
assert len(fv.GATES17) == 17
UNION22 = sorted(set(fv.GATES17) | set(MP1_CONFIRM))
assert len(UNION22) == 22


def load_panel(code):
    path = ANCHOR_FACE[code]
    df = pd.read_csv(path)                     # raw direct read (four-tuple)
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)
    assert not df.empty and df["date"].iloc[-1] == CUTOFF, (code, df["date"].iloc[-1])
    return df


def member_gate_masks(df):
    """A158 17 + MP1 5 gate masks (probe / mp1 single-source machinery)."""
    Fa = probe.alpha158_factors(df)
    assert len(Fa) == probe.N_FACTORS, len(Fa)
    ga = {g[0]: (g[1], g[2]) for g in probe.gate_universe(Fa)}
    miss = [g for g in fv.GATES17 if g not in ga]
    assert not miss, miss
    Fm = mp1.mp1_factors(df)                   # t23.evaluate single source
    gm = {g[0]: (g[1], g[2]) for g in mp1.gate_universe(Fm)}
    miss2 = [g for g in MP1_CONFIRM if g not in gm]
    assert not miss2, miss2
    return ga, gm


def mask_mean(gates, names, index):
    mean = pd.concat([gates[g][0].astype(float) for g in names],
                     axis=1).mean(axis=1)
    dec = pd.Series(True, index=index)
    for g in names:
        dec = dec & gates[g][1]
    return mean, dec


out = {"probe": "a14-predface-draft-facts", "cutoff": CUTOFF,
       "split": SPLIT, "stride": STRIDE, "fwd": FWD,
       "features": FEATURES, "members": MEMBERS,
       "a158_confirm_17": sorted(fv.GATES17), "mp1_confirm_5": MP1_CONFIRM,
       "union22_size": len(UNION22), "overlap_size": len(
           set(fv.GATES17) & set(MP1_CONFIRM)),
       "import_face": "sg/tpl/fv/probe/mp1/t23 all imported clean",
       "anchor_rows": {}, "tail_dates": {},
       "decidable_start": {}, "raw_windows": {}, "resid_windows": {},
       "mp1_anchor_reproduction": None, "feature_xcorr": {}}

panels, feats, closes, dates = {}, {}, {}, {}
for m in MEMBERS:
    df = load_panel(m)
    out["anchor_rows"][m] = int(len(df))
    out["tail_dates"][m] = df["date"].iloc[-1]
    panels[m] = df
    ga, gm = member_gate_masks(df)
    dates[m] = pd.DatetimeIndex(df["date"])
    f_c2, d_c2 = mask_mean(ga, sorted(fv.GATES17), df.index)
    f_mp1, d_mp1 = mask_mean(gm, MP1_CONFIRM, df.index)
    f_v4 = pd.concat([f_c2, f_mp1], axis=1).mean(axis=1)
    d_v4 = d_c2 & d_mp1
    feats[m] = {"f_c2v4": (f_v4, d_v4.values), "f_mp1": (f_mp1, d_mp1.values),
                 "f_c2": (f_c2, d_c2.values)}
    closes[m] = pd.Series(df["close"].values, index=dates[m])
    st = {}
    for f in FEATURES:
        pos = np.flatnonzero(feats[m][f][1])
        st[f] = {"first_decidable": str(dates[m][pos[0]].date())
                 if len(pos) else None,
                 "n_decidable": int(len(pos))}
    out["decidable_start"][m] = st
    if m == "510300":
        k = "DELTA(VOLUME,30)_q10"
        g0 = gm[k]
        out["mp1_anchor_reproduction"] = {
            "gate": k, "decidable": int(g0[1].sum()),
            "open": int(g0[0].sum()),
            "first_decidable_idx": int(np.flatnonzero(g0[1].values)[0]),
            "expect": [3341, 390, 149]}

# RAW-face window pair counts (A13 cell_pairs_raw semantics)
for m in MEMBERS:
    n_panel = len(panels[m])
    wr = {}
    for f in FEATURES:
        vals, dec = feats[m][f]
        pos = np.flatnonzero(dec)
        n = len(pos)
        rebal = np.arange(0, n, STRIDE)
        keep = rebal[rebal + FWD <= n_panel - 1 - pos[0]]
        dts = dates[m][pos[keep]]
        is_n = int(np.count_nonzero(np.asarray(dts < pd.Timestamp(SPLIT))))
        oos_n = int(len(dts)) - is_n
        wr[f] = {"n_pairs": int(len(dts)), "is": is_n, "oos": oos_n,
                 "first_rebal": str(dts[0].date()), "last_rebal": str(dts[-1].date())}
    out["raw_windows"][m] = wr

# RESID-face master intersection (A11 law) pair counts per (member, feature)
master = None
for m in MEMBERS:
    master = dates[m] if master is None else master.intersection(dates[m])
out["resid_master"] = {"first": str(master[0].date()), "last": str(master[-1].date()),
                       "n": int(len(master))}
dec_frames = {f: {m: pd.Series(feats[m][f][1], index=dates[m])
                  for m in MEMBERS} for f in FEATURES}
for f in FEATURES:
    dec = None
    for m in MEMBERS:
        d = dec_frames[f][m].reindex(master).fillna(False).astype(bool)
        dec = d if dec is None else (dec & d)
    pos = np.flatnonzero(dec.values)
    n_panel = len(master)
    v0 = pos[0]
    rebal = np.arange(0, len(pos), STRIDE)
    keep = rebal[v0 + rebal + FWD <= n_panel - 1]
    dts = master[pos[keep]]
    is_n = int(np.count_nonzero(np.asarray(dts < pd.Timestamp(SPLIT))))
    out["resid_windows"][f] = {"n_pairs": int(len(dts)), "is": is_n,
                              "oos": int(len(dts)) - is_n,
                              "first_rebal": str(dts[0].date()),
                              "last_rebal": str(dts[-1].date()),
                              "n_master": int(len(master))}

# feature cross-correlation disclosure (per member, common decidable f_c2v4)
for m in MEMBERS:
    d_v4 = feats[m]["f_c2v4"][1]
    pos = np.flatnonzero(d_v4)
    mat = {}
    for a in FEATURES:
        for b in FEATURES:
            if a < b:
                xa = feats[m][a][0].values[pos]
                xb = feats[m][b][0].values[pos]
                ok = ~(np.isnan(xa) | np.isnan(xb))
                if int(ok.sum()) >= 3:
                    from scipy.stats import spearmanr
                    r = float(spearmanr(xa[ok], xb[ok]).statistic)
                else:
                    r = float("nan")
                mat["%s~%s" % (a, b)] = {"spearman": r, "n": int(ok.sum())}
    out["feature_xcorr"][m] = mat

dest = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "_r872bmb_a14_draft_probe.json")
with open(dest, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print("draft probe facts landed ->", dest)
print("anchor_rows:", out["anchor_rows"])
print("mp1_anchor:", out["mp1_anchor_reproduction"])
for m in MEMBERS:
    print(m, "dec_starts:", {f: out["decidable_start"][m][f]["first_decidable"] for f in FEATURES})
for f in FEATURES:
    print("resid", f, out["resid_windows"][f])
