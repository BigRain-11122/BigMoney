# -*- coding: utf-8 -*-
"""W20 freeze-window kin-orthogonality probe (bm-c r1027).
r720 paradigm (W16 prereg sec.1 precedent): mask co-occurrence containment
of the 38 new W20 entry cells vs already-burned kin faces, measured on the
510300 panel truncated to evidence_cutoff 2026-09-22 (3,483 rows, first
2012-05-28 -- G-ANCHOR face identical to W19 sec.2 panel anchor).
Read-only probe; facts frozen to results/_r1027bmc_w20_kin_orthogonality.json.
Kin definitions verbatim from their canonical implementation sites:
  turnover_surge   strategies/sentiment.py (n=20, threshold=2.0)
  volume_mound     strategies/folk.py entry face (mound=1.3, entry leg only)
  vol_regime_switch strategies/volatility.py (n=20, ma_n=200)
  time_series_momentum strategies/momentum.py (n=200)
  pullback_bounce  strategies/mean_reversion.py (trend_n=60, pullback_n=10)
  max30_q10       scripts/trial_labor_w16.py frozen spec (MAX30 ratio < own-trailing q10)
  deep_pullback   scripts/trial_labor_w8.py census face (MAD60_q10)
"""
import itertools, json, os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

CUTOFF = "2026-09-22"
df = pd.read_csv("data/daily/sh510300.csv")
df["date"] = pd.to_datetime(df["date"])
df = df[df["date"] <= CUTOFF].set_index("date").astype(float)
close, high, volume = df["close"], df["high"], df["volume"]
n_bars = len(close)

# ---------------- new W20 masks (frozen definitions, sec.3 of prereg) ----
def m_dd_rung_entry(high_n, depth):
    rh = close.rolling(high_n).max()
    dd = close / rh - 1.0
    return (dd <= -depth).fillna(False)

def m_near_52w_high(lookback, pct):
    rm = close.rolling(lookback).max()
    return (close >= (1.0 - pct) * rm).fillna(False)

def m_turnover_regime(n, q_lo, q_hi):
    # self-relative quantile rank of today's volume in its trailing n-day window
    def _q(w):
        return (w <= w[-1]).mean()
    q = volume.rolling(n).apply(_q, raw=True)
    state = np.zeros(n_bars, dtype=int)  # 0=LOW 1=HIGH
    prev = 0
    qv = q.values
    for i in range(n_bars):
        x = qv[i]
        if np.isnan(x):
            prev = 0
            state[i] = 0
            continue
        if x >= q_hi:
            prev = 1
        elif x < q_lo:
            prev = 0
        # else: hysteresis band -> carry previous state
        state[i] = prev
    onset = np.zeros(n_bars, dtype=bool)
    onset[1:] = (state[1:] == 1) & (state[:-1] == 0)
    return pd.Series(onset, index=close.index)

W20_CELLS = []
for hn, dp in itertools.product([20, 60, 120, 240], [0.10, 0.15, 0.20, 0.25, 0.30]):
    W20_CELLS.append(("dd_rung_entry", {"high_n": hn, "depth": dp},
                       m_dd_rung_entry(hn, dp)))
for lb, pc in itertools.product([126, 252], [0.02, 0.05, 0.08]):
    W20_CELLS.append(("near_52w_high", {"lookback": lb, "pct": pc},
                      m_near_52w_high(lb, pc)))
for nn, ql, qh in itertools.product([60, 120], [0.50, 0.60, 0.70], [0.90, 0.95]):
    W20_CELLS.append(("turnover_regime", {"n": nn, "q_lo": ql, "q_hi": qh},
                      m_turnover_regime(nn, ql, qh)))

# ---------------- kin masks (burned faces, verbatim definitions) ---------
KIN = {}
v20 = volume.rolling(20).mean()
KIN["turnover_surge_20_2"] = (volume > 2.0 * v20).fillna(False)
v5 = volume.rolling(5).mean()
v60 = volume.rolling(60, min_periods=60).mean()
ret10 = close.pct_change(10)
KIN["volume_mound_entry"] = ((v5 > 1.3 * v60) & ret10.between(0.01, 0.06)).fillna(False)
rv = close.pct_change().rolling(20).std()
KIN["vol_regime_switch_20_200"] = ((rv < rv.rolling(252).median())
                                   & (close > close.rolling(200).mean())).fillna(False)
KIN["time_series_momentum_200"] = (close > close.shift(200)).fillna(False)
KIN["pullback_bounce_60_10"] = ((close > close.rolling(60).mean())
                                & (close.pct_change(10) < -0.05)).fillna(False)
MAX30 = high.rolling(30).max() / close
KIN["max30_q10"] = (MAX30 < MAX30.rolling(252, min_periods=120).quantile(0.10)).fillna(False)
ma60 = close.rolling(60).mean()
dist = close / ma60 - 1.0
q10_ref = dist.rolling(252, min_periods=120).quantile(0.10)
KIN["deep_pullback_mad60_q10"] = (dist < q10_ref).fillna(False)

# ---------------- containment matrix ------------------------------------
FAM_KIN = {
    "dd_rung_entry": ["deep_pullback_mad60_q10", "pullback_bounce_60_10"],
    "near_52w_high": ["max30_q10", "time_series_momentum_200"],
    "turnover_regime": ["turnover_surge_20_2", "volume_mound_entry",
                        "vol_regime_switch_20_200"],
}
R = {"cutoff": CUTOFF, "n_bars": n_bars, "first": str(close.index[0].date()),
     "kin_mask_days": {k: int(v.sum()) for k, v in KIN.items()},
     "cells": [], "family_max_containment": {}}
for fn, params, mask in W20_CELLS:
    nm = int(mask.sum())
    row = {"fn": fn, "params": params, "mask_days": nm, "containment": {}}
    for kn, kv in KIN.items():
        inter = int((mask & kv).sum())
        cont_new_in_kin = inter / nm if nm else None
        kdays = int(kv.sum())
        cont_kin_in_new = inter / kdays if kdays else None
        row["containment"][kn] = {"inter": inter,
                                  "new_in_kin": round(cont_new_in_kin, 4) if cont_new_in_kin is not None else None,
                                  "kin_in_new": round(cont_kin_in_new, 4) if cont_kin_in_new is not None else None}
    R["cells"].append(row)
for fam, kns in FAM_KIN.items():
    mx = {}
    for kn in kns:
        vals = [c["containment"][kn]["new_in_kin"] for c in R["cells"]
                if c["fn"] == fam and c["containment"][kn]["new_in_kin"] is not None]
        mx[kn] = round(max(vals), 4) if vals else None
    R["family_max_containment"][fam] = mx

# mirror line = W16 sec.1 (d) 65% containment precedent
flags = []
for fam, kns in FAM_KIN.items():
    for kn, v in R["family_max_containment"][fam].items():
        if v is not None and v >= 0.65:
            flags.append("%s in %s containment %.2f >= 0.65 mirror-line" % (fam, kn, v))
R["mirror_line_flags"] = flags
R["machine_id"] = "bm-c"; R["round"] = "r1027"
out = "results/_r1027bmc_w20_kin_orthogonality.json"
with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump(R, f, ensure_ascii=False, indent=1, sort_keys=True)
print("KIN-PROBE WRITTEN", out, "| cells:", len(R["cells"]), "| kin days:", R["kin_mask_days"])
print("family max containment (new_in_kin):")
for fam, mx in R["family_max_containment"].items():
    print(" ", fam, mx)
print("mirror flags:", R["mirror_line_flags"] or "NONE")
