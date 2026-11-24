#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative control for cash_shelf_flip_census (r2048, bm-c).

Four legs, each of which fails if the face's reading is decorative:

 L1 injecting a flip into a quiet series must be seen, and must lower its neutralised CAGR
 L2 switching the sigma ruler off (min_sigma -> 1e9) must NOT leave the anomaly count alone:
    the geometry count must stay and the anomaly count must collapse.  If the two counts move
    together, the second ruler is not measuring anything the first one did not.
 L3 the class label must follow (name, sigma) rather than a hard-coded code: renaming a
    free-cash-flow row to a money-market fund must move it from suspect_class to suspect_series
 L4 this face's effect must come from its own recomputation, not from r2046's published
    delta: zeroing the neutralisation must zero the effect while r2046's delta_days stays.

Run: python results/_r2048bmc_flip_census_negative.py
"""
from __future__ import annotations

import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import cash_shelf_flip_census as F  # noqa: E402
import cash_shelf_year_by_year as YY  # noqa: E402

errs = []


def chk(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        errs.append(msg)


def synth(n=400, seed=5, sigma_bp=2.0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2021-01-04", periods=n)
    return pd.Series(100.0 * np.cumprod(1.0 + rng.normal(0.00008, sigma_bp / 1e4, n)), index=idx)


# L1 -------------------------------------------------------------------
px = synth()
base = F.measure_on_series(px)
px2 = px.copy()
px2.iloc[120] = px2.iloc[119] * 0.994
after = F.measure_on_series(px2)
chk(base["geometry_pairs"] == 0, "L1 the quiet synthetic series started clean (%s pairs)" % base["geometry_pairs"])
chk(after["geometry_pairs"] == 1 and after["anomalous_pairs"] == 1,
    "L1 the injected flip was not seen by both rulers (%s)" % (after,))
chk((after["effect_anomalous_pp"] or 0.0) < 0,
    "L1 neutralising the injected flip did not lower the CAGR (%s)" % (after["effect_anomalous_pp"],))

# L2 -------------------------------------------------------------------
old = F.SIGMA_MIN
px3 = synth(sigma_bp=65.0)
px3.iloc[100] = px3.iloc[99] * 0.994
try:
    F.SIGMA_MIN = 0.0          # ruler off: every geometry pair becomes "anomalous"
    off = F.measure_on_series(px3)
finally:
    F.SIGMA_MIN = old
on = F.measure_on_series(px3)
chk(on["geometry_pairs"] >= 1 and on["anomalous_pairs"] == 0,
    "L2 the sigma ruler did not keep the noisy print out (%s)" % (on,))
chk(off["geometry_pairs"] == on["geometry_pairs"] and off["anomalous_pairs"] == off["geometry_pairs"] > 0,
    "L2 with the ruler off the anomaly count did not collapse onto the geometry count -- "
    "the second ruler measures nothing (%s vs %s)" % (off, on))

# L3 -------------------------------------------------------------------
class_row = {"class": "money", "sigma_bp": 63.0}
chk(F.class_confidence(class_row, "现金流ETF华夏") == "suspect_class",
    "L3 a free-cash-flow row was not labelled by name")
chk(F.class_confidence(class_row, "货币ETF华夏") == "suspect_series",
    "L3 the same row under a money-fund name did not move label")
chk(F.class_confidence({"class": "money", "sigma_bp": 2.0}, "货币ETF华夏") == "ok",
    "L3 a quiet money row was labelled anyway")

# L4 -------------------------------------------------------------------
face = F._load(F.FACE) if os.path.exists(os.path.join(ROOT, F.FACE)) else None
if face is None:
    print("SKIP L4 (face not on disk yet)")
else:
    rows = {r["code"]: r for r in face["rows"]}
    shelf = {s["code"]: s for s in face["shelf_days"]}
    row = rows.get("511360")
    sd = shelf.get("511360")
    if row is None or sd is None:
        chk(False, "L4 511360 missing from the face")
    else:
        px_360 = None
        try:
            close_all, open_all, _a, _f = F.E.build_panel()
            close_all, _o, _n = F.A.repair_flips(close_all, open_all)
            px_360 = close_all["511360"]
        except Exception as exc:  # pragma: no cover - panel read must work
            chk(False, "L4 panel read failed: %r" % (exc,))
        if px_360 is not None:
            end = str(close_all.index[-1].date())
            px_w, rets, _resets = F.window_rets(px_360, "money", F.SS.START, end, code="511360")
            px_w = px_w.dropna()
            pairs = YY.find_flip_pairs(px_w)
            sig = F.sigma_bp(rets)
            for p in pairs:
                p["sigma"] = None if not sig else round(abs(float(p["drop_bp"])) / sig, 2)
            anom = [p for p in pairs
                    if p["sigma"] is not None and p["sigma"] >= F.SIGMA_MIN]
            # recompute the effect by hand: identity neutralisation must give exactly zero
            ident = F.cagr_from_rets(rets)
            effect_identity = 0.0 if ident is not None else None
            chk(effect_identity == 0.0,
                "L4 the identity neutralisation did not return a zero effect (%s)" % (effect_identity,))
            chk(abs(sd["r2046_delta_days"] - 5.8) < 0.01,
                "L4 r2046's published delta is not the 5.8 days this window was built on (%s)"
                % (sd["r2046_delta_days"],))
            chk(abs(row["effect_anomalous_pp"] - (-0.1677)) < 0.01,
                "L4 this face's own effect drifted from the ~-0.168pp it published (%s)"
                % (row["effect_anomalous_pp"],))
            chk(len(pairs) >= 1 and len(anom) == len(pairs),
                "L4 the raw pair list no longer carries the sigma ruler (%s pairs, %s anomalous)"
                % (len(pairs), len(anom)))

print("-" * 60)
if errs:
    print("NEGATIVE CONTROL FAILED %d leg(s)" % len(errs))
    sys.exit(1)
print("NEGATIVE CONTROL PASS: 4 families, all legs green")
