# -*- coding: utf-8 -*-
"""r642 bm-a: G2-SLOT-STOCK-P1 roster + vendor smoke probe (facts artifact for
prereg freeze). Mirrors results/_r640bma_slot_old_roster_probe.py (old family)
for the stock_ family -- G2_OVERLAP_CENSUS_P2 sec.8 next-slice second mainline
family (r639 family probe priority_table rank-2; rank-1 old family census
closed 0/41 nominated r641, honest negative, family answered per O-1901).

Zero network, zero judgment, deterministic. Legs:
 1. vendor engine import (ml-quant-trading pinned install a770825) + LEGACY_REGISTRY stock_ enumeration
 2. roster cross-check: r639 probe family 14 vs census P2 NEW-FACE rows vs vendor registry 22
 3. per-face daily-panel derivability re-derive (r639 probe says 14/14 derivable, 0 downgrades)
 4. vendor anchors: repo HEAD, file sha256s (incl. _factors_stock.py)
 5. core48 panel facts: 48 in-service members, rows, dates, columns, cutoff truncation, vwap derivability
 6. synthetic Panel smoke: all vendor stock_* faces run on torch CPU panel, shape/mask/finiteness
Output: results/_r642bma_slot_stock_roster_probe.json
"""
import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR_SRC = r"C:\Users\sjs20\Desktop\FluxGroup\quant\toolstack\repos\ml-quant-trading\src"
VENDOR_REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\toolstack\repos\ml-quant-trading"
ANCHOR_HEAD = "a770825f841504e41581f057b4d94160e6a50c2e"
CUTOFF = "2026-09-22"

PANEL_INPUTS = {
    "open", "close", "high", "low", "volume", "vol", "vwap", "amount",
    "returns", "ret", "adv20", "cap",
}
OPS = {
    "rank", "corr", "ts_min", "ts_max", "ts_mean", "ts_sum", "ts_std",
    "ts_rank", "ts_corr", "delta", "delay", "ewma", "sign", "abs",
    "min", "max", "sum", "std", "mean", "log", "sqrt", "signedpower",
}


def _unknown_identifiers(formula: str):
    toks = re.findall(r"[A-Za-z_][A-Za-z_0-9]*", formula or "")
    unknown = []
    for t in toks:
        if t.lower() in PANEL_INPUTS or t in OPS or t.lower() in OPS:
            continue
        if re.fullmatch(r"\d+", t):
            continue
        if t not in unknown:
            unknown.append(t)
    return unknown


def main():
    out = {
        "artifact": "_r642bma_slot_stock_roster_probe",
        "audit": {"network": "zero", "deterministic": True, "judgment": "none (facts probe)"},
        "legs": {},
    }
    fails = []

    # ---- leg 1: vendor import + registry ----
    sys.path.insert(0, VENDOR_SRC)
    import torch  # noqa: E402
    import mlquant.features._factors_stock  # noqa: F401,E402  (decorator registration side-effect)
    from mlquant.features.legacy_factors import LEGACY_REGISTRY  # noqa: E402
    vendor_stock = sorted(k for k in LEGACY_REGISTRY if k.startswith("stock_"))
    out["legs"]["vendor_registry"] = {
        "n_stock_faces": len(vendor_stock),
        "faces": vendor_stock,
    }
    if len(vendor_stock) != 22:
        fails.append(f"vendor stock faces {len(vendor_stock)} != 22 (install drift)")

    # ---- leg 2: roster cross-check ----
    census = json.load(open(os.path.join(ROOT, "results", "g2_overlap_census_p2.json"), encoding="utf-8"))
    stock_rows = {r["face"]: r for r in census["rows"] if r.get("face", "").startswith("stock_")}
    probe = json.load(open(os.path.join(ROOT, "results", "_r639bma_g2_slot_family_probe.json"), encoding="utf-8"))
    fam = [f for f in probe["families"] if f["family"] == "stock"][0]
    probe14 = fam["faces"]
    in_vendor = [f for f in probe14 if f in vendor_stock]
    in_census_newface = [f for f in probe14 if stock_rows.get(f, {}).get("verdict") == "NEW-FACE"]
    excluded8 = sorted(set(stock_rows) - set(probe14))
    excluded_status = {f: stock_rows[f].get("verdict") for f in excluded8}
    out["legs"]["roster_crosscheck"] = {
        "probe_family_n": len(probe14),
        "probe_in_vendor": len(in_vendor),
        "probe_in_census_newface": len(in_census_newface),
        "excluded_from_family": excluded_status,
    }
    if len(in_vendor) != 14:
        fails.append(f"probe family vendor membership {len(in_vendor)} != 14")
    if len(in_census_newface) != 14:
        fails.append(f"probe family NEW-FACE status {len(in_census_newface)} != 14")
    if set(probe14) - set(vendor_stock):
        fails.append("probe family faces missing from vendor registry")

    # ---- leg 3: per-face derivability ----
    deriv = {}
    for f in probe14:
        unk = _unknown_identifiers(stock_rows[f].get("doc_formula") or "")
        deriv[f] = {"formula": stock_rows[f].get("doc_formula"), "unknown_tokens": unk}
    non_derivable = sorted(f for f in deriv if deriv[f]["unknown_tokens"])
    out["legs"]["derivability"] = {
        "panel_derivable": sorted(set(probe14) - set(non_derivable)),
        "non_derivable": {f: deriv[f]["unknown_tokens"] for f in non_derivable},
        "n_derivable": len(probe14) - len(non_derivable),
    }
    if len(non_derivable) != 0:
        fails.append(f"non-derivable count {len(non_derivable)} != 0 (r639 probe said 14/14 derivable)")

    # ---- leg 4: vendor anchors ----
    head = subprocess.run(["git", "-C", VENDOR_REPO, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    def _sha(p):
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    anchors = {"vendor_head": head, "head_matches_install_anchor": head == ANCHOR_HEAD}
    for name in ("_factors_stock.py", "legacy_factors.py", "tensor_factors.py"):
        p = os.path.join(VENDOR_SRC, "mlquant", "features", name)
        anchors[f"sha256_{name}"] = _sha(p)
    out["legs"]["vendor_anchors"] = anchors
    if not anchors["head_matches_install_anchor"]:
        fails.append("vendor HEAD drifted from pinned install anchor a770825")

    # ---- leg 5: core48 panel facts ----
    sys.path.insert(0, ROOT)
    from knowledge.panel_gate import INSERVICE_WHITELIST, INSERVICE_SHA16  # noqa: E402
    daily_dir = os.path.join(ROOT, "data", "daily")
    panel = {}
    for code in sorted(INSERVICE_WHITELIST):
        p = os.path.join(daily_dir, f"{code}.csv")
        if not os.path.exists(p):
            fails.append(f"core48 member {code} csv missing")
            continue
        df = pd.read_csv(p, parse_dates=["date"])
        df = df[df["date"] <= pd.Timestamp(CUTOFF)]
        if df["date"].duplicated().any():
            fails.append(f"{code} duplicate dates")
        panel[code] = df
    union_dates = sorted(set().union(*[set(d["date"]) for d in panel.values()])) if panel else []
    common_start = max(d["date"].min() for d in panel.values())
    min_rows = min(len(d) for d in panel.values())
    bad_cols = [c for c, d in panel.items()
                if not {"open", "high", "low", "close", "volume", "amount"} <= set(d.columns)]
    vwap_ok_frac = {}
    for c, d in panel.items():
        sub = d[d["date"] >= common_start]
        ok = ((sub["amount"] > 0) & (sub["volume"] > 0)).mean()
        vwap_ok_frac[c] = round(float(ok), 6)
    worst_vwap = min(vwap_ok_frac.values())
    out["legs"]["core48_panel"] = {
        "n_members": len(panel),
        "inservice_sha16": INSERVICE_SHA16,
        "union_trading_days": len(union_dates),
        "common_window_start": str(common_start.date()),
        "union_last": str(max(union_dates).date()) if union_dates else None,
        "min_rows_per_member": int(min_rows),
        "bad_columns_members": bad_cols,
        "vwap_ok_fraction_worst": worst_vwap,
        "cutoff": CUTOFF,
    }
    if len(panel) != 48:
        fails.append(f"core48 members loaded {len(panel)} != 48")
    if bad_cols:
        fails.append(f"core48 column gaps: {bad_cols[:5]}")
    if worst_vwap < 0.99:
        fails.append(f"vwap derivation worst fraction {worst_vwap} < 0.99")

    # ---- leg 6: synthetic panel smoke (torch CPU) ----
    torch.manual_seed(0)
    T, N = 300, 20
    rng = np.random.default_rng(7)
    o = rng.lognormal(size=(T, N)).astype(np.float32)
    fields = {
        "open": o, "high": o * 1.02, "low": o * 0.98,
        "close": o * (1 + rng.normal(0, 0.01, (T, N)).astype(np.float32)),
        "volume": (rng.random((T, N)) * 1e6 + 1).astype(np.float32),
    }
    fields["vwap"] = (fields["close"] * (1 + rng.normal(0, 0.002, (T, N)).astype(np.float32)))
    fields["amount"] = fields["vwap"] * fields["volume"]
    mask = (rng.random((T, N)) > 0.1)
    mask[:60] = False
    from mlquant.data.panel import Panel  # noqa: E402
    tt = {k: torch.from_numpy(v) for k, v in fields.items()}
    p = Panel(dates=np.arange(T), stocks=[f"S{i}" for i in range(N)],
              open=tt["open"], high=tt["high"], low=tt["low"], close=tt["close"],
              volume=tt["volume"], vwap=tt["vwap"], mask=torch.from_numpy(mask),
              amount=tt["amount"])
    smoke = {}
    for f in vendor_stock:
        try:
            val, m = LEGACY_REGISTRY[f](p)
            ok_shape = tuple(val.shape) == (T, N) and tuple(m.shape) == (T, N)
            ok_mask = m.dtype == torch.bool
            finite = torch.isfinite(val[mask]).float().mean().item() if m.any() else 0.0
            smoke[f] = {"rc": 0 if (ok_shape and ok_mask) else 1, "finite_frac": round(finite, 4)}
        except Exception as e:  # noqa: BLE001
            smoke[f] = {"rc": 2, "err": type(e).__name__}
    smoke_fail = [f for f, v in smoke.items() if v["rc"] != 0]
    probe14_fail = [f for f in probe14 if smoke.get(f, {}).get("rc") != 0]
    out["legs"]["synthetic_smoke"] = {
        "n_faces": len(vendor_stock),
        "n_fail": len(smoke_fail),
        "fail_faces": smoke_fail,
        "probe_family_fail": probe14_fail,
        "device": "cpu",
    }
    if probe14_fail:
        fails.append(f"probe-family smoke failures: {probe14_fail[:8]}")

    # ---- verdict ----
    out["verdict"] = "PASS" if not fails else "FAIL"
    out["fails"] = fails
    roster = {
        "burn_faces": sorted(set(probe14) - set(non_derivable)),
        "downgraded_fundamental_lane": non_derivable,
        "n_burn": len(probe14) - len(non_derivable),
    }
    out["roster_freeze"] = roster
    dst = os.path.join(ROOT, "results", "_r642bma_slot_stock_roster_probe.json")
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    roster_sha = hashlib.sha256(json.dumps(roster, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    print(f"selftest: {'PASS' if not fails else 'FAIL'} fails={fails}")
    print(f"roster: burn={roster['n_burn']} downgraded={non_derivable} roster_freeze_sha256={roster_sha[:16]}")
    print(f"artifact: {dst}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
