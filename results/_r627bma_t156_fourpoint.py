# r627 bm-a: T-156 four-point verify (MSG-0827 sec.5) on the swapped p1c_stock panel
# Run AFTER the quarantine swap. Verdict file: results/_r627bma_t156_fourpoint.json
# (a) meta vwap_688_check gate=true  (b) 13-file SHA-256 == sender manifest
# (c) 688001 amount/close magnitude ~1.84e6 (not 1.84e8)  (d) n_base @ pos 7381 (2020-12-01) == 3292 (bm-b PE_x1)
import json, hashlib, os, sys

CACHE = r"Money02\data\cache\p1c_stock"
SENDER = "fleet/transfers/T-2026-10-03-156-sender.json"
OUT = "results/_r627bma_t156_fourpoint.json"
POS = 7381
EXPECT_N_BASE = 3292        # bm-b cells_VALUE-PE_x1.jsonl start 2020-12-01
EXPECT_N_ACTIVE = 3875      # same row, n_active_universe

verdict = {"ts": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
           "machine": "bm-a", "points": {}, "pass": False}

# ---- (a) meta gate ----
meta = json.load(open(os.path.join(CACHE, "meta.json"), encoding="utf-8"))
vg = (meta.get("validation") or {}).get("vwap_688_check") or {}
gate = vg.get("gate")
verdict["points"]["a_meta_vwap_688_check"] = {
    "value": gate, "n_detail": len(vg.get("details", [])),
    "generated": meta.get("generated"), "pass": bool(gate)}

# ---- (b) hashes vs sender manifest ----
man = json.load(open(SENDER, encoding="utf-8-sig"))
hash_ok, hash_rows = True, []
for f in man["files"]:
    p = os.path.join(CACHE, f["file"])
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    ok = (h.hexdigest() == f["sha256"]) and (os.path.getsize(p) == f["bytes"])
    hash_rows.append({"file": f["file"], "pass": bool(ok)})
    hash_ok = hash_ok and ok
verdict["points"]["b_hashes_vs_sender"] = {"n": len(hash_rows), "pass": hash_ok,
                                           "rows": hash_rows}

# ---- (c) 688 magnitude spot ----
import numpy as np
import pandas as pd
dates = np.load(os.path.join(CACHE, "dates.npy"))
idx = pd.to_datetime(dates, unit="us")
# locate 688001 column: cache syms order == sorted parquet names == meta shape;
# load via the canonical loader for symbol order (single source)
sys.path.insert(0, "scripts")
import p1c_stock_ic_batch as P1C
_, syms, _ = P1C.load_universe()
j = syms.index("688001")
lo = int(np.searchsorted(idx.values, np.datetime64("2024-01-01")))
hi = int(np.searchsorted(idx.values, np.datetime64("2024-12-31")))
am = np.load(os.path.join(CACHE, "amount.npy"), mmap_mode="r")
cl = np.load(os.path.join(CACHE, "close.npy"), mmap_mode="r")
# r615 probe metric: median(amount/close) = implied share count (off-caliber was
# ~1.84e8 = exactly 100x real ~1.84e6 for 688001)
with np.errstate(invalid="ignore"):
    implied = (np.asarray(am[lo:hi, j], dtype=np.float64)
               / np.asarray(cl[lo:hi, j], dtype=np.float64))
imp_med = float(np.nanmedian(implied))
c_ok = (1.0e6 <= imp_med <= 1.0e7)
verdict["points"]["c_688001_magnitude"] = {"implied_shares_median_2024": imp_med,
                                           "window": "2024-01-01..2024-12-31",
                                           "expect_offcaliber": 1.837731501e8,
                                           "pass": bool(c_ok)}

# ---- (d) n_base recompute via the runner's own mask (pos 7381) ----
import fund_value_p1 as FV
FV._init_worker()
assert str(FV._G["idx"][POS].date()) == "2020-12-01", FV._G["idx"][POS]
u = FV._month_universe(POS)
n_base = int(len(u["base_j"]))
n_active = int(u["n_active"])
d_ok = (n_base == EXPECT_N_BASE) and (n_active == EXPECT_N_ACTIVE)
verdict["points"]["d_n_base_2020_12"] = {"pos": POS, "date": str(FV._G["idx"][POS].date()),
                                         "n_base": n_base, "expect": EXPECT_N_BASE,
                                         "n_active": n_active, "expect_active": EXPECT_N_ACTIVE,
                                         "pass": bool(d_ok)}

verdict["pass"] = all(v["pass"] for v in verdict["points"].values())
json.dump(verdict, open(OUT, "w", encoding="utf-8"), indent=1)
print(json.dumps(verdict, indent=1)[:1200])
sys.exit(0 if verdict["pass"] else 1)
