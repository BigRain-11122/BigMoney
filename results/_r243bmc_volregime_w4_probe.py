# -*- coding: utf-8 -*-
"""_r243bmc_volregime_w4_probe.py -- INNOVATION-QUOTA-SLOT-4 pre-freeze probe:
zoo #96 volume_regime_bimodal (param-frozen bm-b r263 digest
DIGEST-20260926-wave10-paramfreeze-95-96.md sec.3, clean-room, zero code
copy) volume-index three-threshold state-machine raw-face facts on the
510300 anchor. NOT results, NOT a strategy claim. Read-only, deterministic,
zero network.

SLOT-4 supply slice per O-20260928-1614 sec.1/4(d) fill-ladder innovation
quota (>=1 new hypothesis family per idle window; pool supply_family_streak
139min+ at r243 open, ready=0<3 floor breach) -- bm-c r243.

Family selection anti-dup face (r243 live-read):
  * #95 index_higher_mom_timing was consumed by SLOT-3 (HIGHERMOM-TIMING-P1
    judged-negative 0/3, r240); #96 volume_regime_bimodal is the OTHER
    param-frozen zoo row from the same digest = untried in-repo.
  * Volume-native TIMING face is a new measurement object for the quota
    line: burned axes are price/return-derived (VOL=ret std, AMP=range,
    MOM=ret speed, STD=price dispersion, TSTATE=position, STREAK=runs);
    #96 = traded-QUANTITY HMA ratio with a NON-MONOTONE V-shape (both
    extremes long, middle flat) -- no burned grammar axis carries a
    non-monotone threshold face.
  * volume-RSI x3 families judged-negative R59 = cross-section factor
    usage (bm-b r121), NOT timing usage -- usage-different, disclosed.
  * VCONF surge/dry (v > med20v) is a descriptive 512-cell gate face,
    never a burned grammar axis -- closest in-repo volume face, overlap
    quantified below.

Construction (r263 digest sec.3 frozen, our-side clean-room):
  volume_index = HMA(volume, 5) / HMA(volume, slow), slow=100 (研报主口径
  AMA5/AMA100) and slow=45 (复现调参面 disclosure leg, calc_func vs
  bt_func divergence disclosed in the digest); HMA(W) = WMA(2*WMA(p,W/2)
  - WMA(p,W), round(sqrt(W))); WMA weights 1..n.  Three-threshold state
  machine: upper thr 1.15 (overheat -> long), mid 1.0..1.15 flat (观望),
  0.807..1.0 flat (short leg structurally unavailable on ETF spot ->
    cash, zoo #94 judgment precedent), lower thr 1.15**-1.5 (a=1.5,
    drought/地量反弹 -> long).  Int-window disclosure: half=W//2,
    sq=int(round(sqrt(W))) -> 100:{50,10}, 45:{22,7}.
  Causal convention (probe face only): state(t) readable at close t;
  descriptive forward windows are descriptive, the runner shifts for
  T+1 (frozen in prereg sec.3).

Anchor cutoff = 2026-09-22 (P-5C frozen binding, W4-W12 probe anchor,
cross-family D6 faces align by date). Quota-slot W3 used freeze-day
2026-09-28 face -- SLOT-4 takes the conservative P-5C anchor instead,
difference disclosed in prereg sec.0.
"""
import json
import math
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join("results"))
import _r237bmc_stdq90_w11_probe as r237p  # frozen W11 probe faces

CUTOFF = "2026-09-22"
OUT = "results/_r243bmc_volregime_w4_probe_facts.json"
PANEL = "data/daily/sh510300.csv"
EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]
UPPER = 1.15
LOWER = UPPER ** -1.5  # a=1.5 -> 0.8073...


def wma(s, n):
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return s.rolling(n).apply(lambda x: float(np.dot(x, w) / w.sum()),
                              raw=True)


def hma(s, n):
    half = int(n) // 2
    sq = int(round(math.sqrt(int(n))))
    return wma(2 * wma(s, half) - wma(s, int(n)), sq)


def tstats(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3:
        return {"n_a": len(a), "n_b": len(b), "t": None}
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = math.sqrt(va / len(a) + vb / len(b))
    if se == 0:
        return {"n_a": len(a), "n_b": len(b), "t": None}
    t = (a.mean() - b.mean()) / se
    return {"n_a": len(a), "n_b": len(b), "t": round(float(t), 3),
            "mean_a": round(float(a.mean()), 6),
            "mean_b": round(float(b.mean()), 6)}


def rate(mask_in, gate, dec):
    """r447 probe verbatim: P(gate | mask_in & dec) * 100."""
    both = int((mask_in & gate).sum())
    base = int((mask_in & dec).sum())
    return round(100.0 * both / base, 2) if base else float("nan")


def main() -> int:
    df = pd.read_csv(PANEL)
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)
    assert len(df) == 3483, "G-PANEL rows %d != 3483" % len(df)
    assert df["date"].iloc[0] == "2012-05-28"
    assert df["date"].iloc[-1] == CUTOFF

    close, vol = df["close"], df["volume"]
    o, h, l = df["open"], df["high"], df["low"]
    ret = close.pct_change()

    # inherited D6 faces (r237 frozen module, verbatim import; API per
    # r447 probe usage: std_faces(df,win)->(std,q90,open,dec);
    # amp_faces(df)->(amp,med,wide 1/0/NaN); streak_faces(df)->state
    # (1=up,0=down,-1=neither,NaN warmup); tstate_faces(df)->(mad_q10,
    # rsv_low,dec,rsv60); mom_faces(df)->(roc20,q10,open,dec))
    di = pd.DataFrame({"open": o, "high": h, "low": l, "close": close,
                       "volume": vol}, index=df.index)
    std20, _q90s20, std20_open, dec_s20 = r237p.std_faces(di, 20)
    _amp, _medamp, amp_wide = r237p.amp_faces(di)
    st_state = r237p.streak_faces(di)
    mad_q10, rsv_low, _dec_ts, _rsv60 = r237p.tstate_faces(di)
    _roc20, _q10m, mom_open, dec_mom = r237p.mom_faces(di)
    tstate_open = (mad_q10.fillna(False) | rsv_low.fillna(False))
    streak_up = st_state == 1.0

    # W4 VOL face (r447 probe inline construction, verbatim)
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    calm, wild = vol20 <= med500, vol20 > med500

    # VCONF surge face (r237 construction)
    med20v = vol.rolling(20, min_periods=20).median()
    surge = vol > med20v

    # forward descriptive windows (zoo validation window = 5d; 20d = lineage)
    fwd5 = close.pct_change(5).shift(-5)
    fwd20 = close.pct_change(20).shift(-20)

    facts = {"probe": "INNOVATION-QUOTA-SLOT-4 volume_regime_bimodal "
                      "pre-freeze facts (zoo #96, r263 frozen params)",
             "anchor": PANEL, "cutoff": CUTOFF,
             "panel": {"rows": int(len(df)), "first": df["date"].iloc[0],
                       "last": df["date"].iloc[-1]},
             "construction": {"upper_thr": UPPER, "lower_thr": round(LOWER, 6),
                              "a": 1.5, "slow_windows": [100, 45],
                              "int_windows": {"100": [50, 10], "45": [22, 7]},
                              "position_rule": "long = vi>1.15 (overheat) OR "
                              "vi<lower (drought); mid band flat (ETF no "
                              "short leg, zoo #94 precedent)"},
             "cells": {}}

    for slow in (100, 45):
        vi = hma(vol, 5) / hma(vol, slow)
        dec = vi.notna()
        first_dec = int(np.argmax(dec.values))  # first True idx
        over = vi > UPPER
        drought = vi < LOWER
        mid_upper = (vi >= 1.0) & (vi <= UPPER)
        mid_lower = (vi > LOWER) & (vi < 1.0)
        long_open = over | drought

        d = {"decidable": int(dec.sum()), "first_decidable_bar_idx": first_dec,
             "overheat_open": int(over.sum()),
             "drought_open": int(drought.sum()),
             "long_open": int(long_open.sum()),
             "open_rate": round(float(long_open.sum() / dec.sum()), 6),
             "mid_upper_flat": int(mid_upper.sum()),
             "mid_lower_flat": int(mid_lower.sum()),
             "dec_vs_dec100": None}

        # descriptive forward faces (overlap-window optimism note applies)
        d["fwd5_long_open_vs_decidable"] = tstats(
            (fwd20 * 0 + fwd5)[long_open & dec],
            fwd5[dec])
        d["fwd20_long_open_vs_decidable"] = tstats(
            fwd20[long_open & dec], fwd20[dec])
        # V-shape decomposition (honest negatives face)
        d["fwd5_overheat_vs_drought"] = tstats(fwd5[over & dec],
                                               fwd5[drought & dec])
        d["fwd5_long_vs_calm"] = tstats(fwd5[long_open & calm.fillna(False)],
                                        fwd5[calm.fillna(False)])
        d["fwd5_long_vs_wild"] = tstats(fwd5[long_open & wild.fillna(False)],
                                        fwd5[wild.fillna(False)])

        # extreme-day face
        ext = {}
        for day in EXTREME_DAYS:
            idx = df.index[df["date"] == day]
            if len(idx) == 0:
                ext[day] = "absent"
                continue
            i = int(idx[0])
            v_i = float(vi.iloc[i]) if dec.iloc[i] else None
            st = ("overheat" if over.iloc[i] else
                  "drought" if drought.iloc[i] else
                  "mid_upper_flat" if mid_upper.iloc[i] else
                  "mid_lower_flat" if mid_lower.iloc[i] else "warmup")
            ext[day] = {"state": st, "vi": None if v_i is None
                        else round(v_i, 6)}
        d["extreme_days"] = ext
        d["extreme_open_count"] = int(sum(
            1 for v in ext.values()
            if isinstance(v, dict) and v["state"] in ("overheat", "drought")))

        # D6 adjacency faces (date-aligned via boolean arrays on same panel)
        def cell(a_mask, a_dec, b_mask, b_dec):
            both = a_dec & b_dec
            return {"both": int((a_mask & b_mask & both).sum()),
                    "a_only": int((a_mask & ~b_mask & both).sum()),
                    "b_only": int((~a_mask & b_mask & both).sum()),
                    "neither": int((~a_mask & ~b_mask & both).sum()),
                    "a_in_b": round(float((a_mask & b_mask).sum()) /
                                    float(a_mask.sum()), 4) if a_mask.sum() else None}

        lo_dec = long_open & dec
        d["d6"] = {
            "vs_w4_calm": cell(lo_dec, dec, calm.fillna(False), dec & med500.notna()),
            "vs_w4_wild": cell(lo_dec, dec, wild.fillna(False), dec & med500.notna()),
            "vs_vconf_surge": cell(lo_dec, dec, surge.fillna(False), dec & med20v.notna()),
            "vs_w11_std20_open": cell(lo_dec, dec,
                                      std20_open.fillna(False), dec & dec_s20),
            "vs_w10_mom_open": cell(lo_dec, dec,
                                     mom_open.fillna(False), dec & dec_mom),
            "vs_w9_amp_wide": cell(lo_dec, dec,
                                   (amp_wide == 1).fillna(False), dec),
            "vs_w7_streak_up": cell(lo_dec, dec,
                                    streak_up.fillna(False), dec),
            "vs_w8_tstate_open": cell(lo_dec, dec,
                                      tstate_open, dec),
        }
        # state-conditioned regime reads (context faces)
        d["regime_rates"] = {
            "pct_long_when_calm": rate(calm.fillna(False), lo_dec, dec & med500.notna()),
            "pct_long_when_wild": rate(wild.fillna(False), lo_dec, dec & med500.notna()),
            "pct_long_when_surge": rate(surge.fillna(False), lo_dec, dec & med20v.notna()),
            "pct_long_when_dry": rate((~surge).fillna(False), lo_dec, dec & med20v.notna()),
        }
        facts["cells"]["slow%d" % slow] = d

    # slow100 vs slow45 intra-family overlap (axis-variant disclosure)
    vi100 = hma(vol, 5) / hma(vol, 100)
    vi45 = hma(vol, 5) / hma(vol, 45)
    lo100 = ((vi100 > UPPER) | (vi100 < LOWER)) & vi100.notna()
    lo45 = ((vi45 > UPPER) | (vi45 < LOWER)) & vi45.notna()
    both_dec = vi100.notna() & vi45.notna()
    facts["intra_family"] = {
        "slow100_vs_slow45": {"both": int((lo100 & lo45 & both_dec).sum()),
                              "s100_only": int((lo100 & ~lo45 & both_dec).sum()),
                              "s45_only": int((~lo100 & lo45 & both_dec).sum()),
                              "s100_in_s45": round(float((lo100 & lo45).sum())
                                                   / float(lo100.sum()), 4)}
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)
    print("facts ->", OUT)
    for slow, d in facts["cells"].items():
        print("%s: decidable=%d first_decidable=%d long_open=%d "
              "(over=%d/drought=%d) open_rate=%s extreme_open=%d" % (
                  slow, d["decidable"], d["first_decidable_bar_idx"],
                  d["long_open"], d["overheat_open"], d["drought_open"],
                  d["open_rate"], d["extreme_open_count"]))
    print("intra:", facts["intra_family"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
