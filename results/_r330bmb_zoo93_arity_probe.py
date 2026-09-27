"""r330 bm-b: zoo93 family-ctor arity probe (real call-shape verification).

The hermetic selftest (r263 law) covers gate/sidecar/ledger legs but NOT the
real build_faces ctor call path -- r330 crash slipped through it, and so did
the first mirror-unpack attempt (family ctor returns a DICT of 4 faces +
n_bad, not a single DataFrame). This probe exercises the EXACT fixed call
shape with synthetic panels: unpack (fam_dict, n_bad), assert the family dict,
select the rostered zoo93_arc member, reindex. Mirrors
census_fusion_s2_w2.py build_faces zoo93 block.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

import numpy as np
import pandas as pd

import p1e_factors as ZF

idx = pd.date_range("2026-01-01", periods=90, freq="D")
cols = ["A", "B", "C"]
rng = np.random.default_rng(7)
close = pd.DataFrame(100.0 + rng.normal(0, 1, (90, 3)), index=idx, columns=cols)
vwap = close * 1.001
tr = pd.DataFrame(rng.uniform(0.0, 0.3, (90, 3)), index=idx, columns=cols)

# fixed call shape (mirror of census_fusion_s2_w2.py build_faces zoo93 block)
fam, n_bad = ZF.build_zoo93_arc_family(tr, vwap, close)

# family contract: dict of DataFrames + int counter
assert isinstance(fam, dict), f"ctor fam={type(fam)} not dict"
assert set(fam) == {"zoo93_arc", "zoo93_vrc", "zoo93_src", "zoo93_krc"}, sorted(fam)
for k, v in fam.items():
    assert isinstance(v, pd.DataFrame), f"{k}={type(v)} not DataFrame"
assert isinstance(n_bad, (int, np.integer)), f"n_bad={type(n_bad)}"

# rostered-member selection + reindex (the W2A consumption)
sel = fam["zoo93_arc"]
out = sel.reindex(index=idx, columns=cols)
assert isinstance(out, pd.DataFrame) and out.shape == (90, 3)

# crash-class reproductions: both pre-fix shapes must fail at reindex
for bad in ({"zoo93_arc": ZF.build_zoo93_arc_family(tr, vwap, close)},          # v0: tuple face
            {"zoo93_arc": ZF.build_zoo93_arc_family(tr, vwap, close)[0]}):      # v1: dict face
    try:
        bad["zoo93_arc"].reindex(index=idx, columns=cols)
        raise SystemExit("PRE-FIX SHAPE UNEXPECTEDLY PASSED -- probe invalid")
    except AttributeError:
        pass  # expected: tuple/dict have no reindex (r330 crash class)

print("ARITY-PROBE-PASS family=4 members sel", sel.shape, "n_bad", int(n_bad))
