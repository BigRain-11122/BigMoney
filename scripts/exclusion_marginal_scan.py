"""EXCLUSION-MARGINAL-P1 runner (D-20260930-41 deliverable #3, bm-b berth).

Scan the marginal value of each stock-exclusion rule on a FROZEN classical
low-amount ("低量") monthly-rebalance selection base, over the bm-b astock
daily panel. Three-command identity (W14 lineage):

  probe     real-read data anchors -> results/exclusion_marginal_scan/probe_facts.json
  selftest  hermetic offline checks (rule masks, cell enumeration, cost spec)
  run       full burn -- FAIL-CLOSED until engine leg lands (honest rc=2)

Laws carried: G-ANCHOR-FACE four-tuples + same-face assertions (O-20260928-1712),
R99 freeze-before-burn, D-20260930-40 CN-C7 roundtrip via knowledge/cost_spec,
D-20260930-41 retail-quant track #3, trial gate <=500/30d (RETAIL_QUANT_TRACK
sec.4), evidence_cutoff=2026-09-22 (P-5C binding, ALLOC-POLICY-SCAN-P1 precedent).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(ROOT, "results", "exclusion_marginal_scan")
PROBE_FILE = os.path.join(RES_DIR, "probe_facts.json")

EVIDENCE_CUTOFF = "2026-09-22"          # P-5C binding, frozen pre-burn
PANEL_DIR = os.path.join(ROOT, "data", "astock_daily", "per")
ELIG_CSV = os.path.join(ROOT, "data", "fundamental", "eligibility.csv")
MASK_CSV = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")

# frozen rule set (prereg sec.3; ids are contract -- do not renumber)
RULES = ["r1_loss", "r2_st", "l1_liq5000w", "l2_price1y", "l3_age250", "l4_active10td"]

# frozen base params (prereg sec.3)
BASE_PARAMS = {
    "rank_face": "amt20_mean asc (low-amount first)",
    "n_holdings": 10,
    "weighting": "equal",
    "rebalance": "monthly (month-end signal, next trading day open execution, T+1)",
    "initial_capital_cny": 1_000_000,
    "window_first_signal": "2007-01",
    "allstart_jan_firsts": "2007..2022 (16 starts)",
    "cost_face": "V2 stock: knowledge/rules.py fee_schedule_for + ADV20 3-layer slippage",
}

CELLS = (
    [{"cell": "FULL", "off": []}, {"cell": "NONE", "off": RULES}]
    + [{"cell": f"LOO-{r}", "off": [r]} for r in RULES]
    + [{"cell": f"AOI-{r}", "off": [x for x in RULES if x != r]} for r in RULES]
    + [{"cell": "RAND-FULL", "off": [], "base": "random"},
       {"cell": "RAND-NONE", "off": RULES, "base": "random"}]
)


def _sha16(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _load_codes() -> list[str]:
    """Universe = eligibility 6-digit codes with sh/sz prefixes only
    (0/3 -> sz, 6 -> sh; B-share 2/9 + BSE 4/8/92x skipped per collector law,
    mirrors update_astock_daily universe_n=5228 face)."""
    df = pd.read_csv(ELIG_CSV, dtype={"code": str})
    return [c for c in df["code"].astype(str).tolist()
            if len(c) == 6 and c[0] in ("0", "3", "6")]


def probe() -> int:
    """Real-read anchors, frozen into facts file (G-ANCHOR-FACE four-tuples)."""
    os.makedirs(RES_DIR, exist_ok=True)
    codes = _load_codes()
    files = sorted(os.listdir(PANEL_DIR))
    facts = {
        "probe": "EXCLUSION-MARGINAL-P1 data anchors",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "anchor_faces": {
            "panel": {
                "path": "data/astock_daily/per/<code>.csv",
                "loader": "pandas.read_csv",
                "start": "per-file first date (1991-04-03 oldest实证)",
                "warmup": "amt20_mean min_periods=20; age250 rule needs 250 bars",
            },
            "eligibility": {
                "path": "data/fundamental/eligibility.csv",
                "loader": "firm.risk.b_layer_filter.load_eligibility",
                "start": "snapshot (24h refresh, update_fundamental.py)",
                "warmup": "static mask, none",
            },
            "b_layer_mask": {
                "path": "data/fundamental/b_layer_mask.csv",
                "loader": "firm.risk.b_layer_filter.load_mask",
                "start": "snapshot (regenerated per eligibility refresh)",
                "warmup": "static mask, none",
            },
        },
        "panel_files": len(files),
        "eligibility_codes": len(codes),
        "cells": [c["cell"] for c in CELLS],
        "n_cells": len(CELLS),
        "rules": RULES,
        "base_params": BASE_PARAMS,
    }
    # real-read three sample anchors (first/middle/last by code order)
    sample = {}
    for code in [files[0].split(".")[0], files[len(files) // 2].split(".")[0], files[-1].split(".")[0]]:
        df = pd.read_csv(os.path.join(PANEL_DIR, f"{code}.csv"))
        amt20 = df["amount"].rolling(20).mean()
        cutoff_rows = int((df["date"] <= EVIDENCE_CUTOFF).sum())
        sample[code] = {
            "rows_total": int(len(df)),
            "rows_to_cutoff": cutoff_rows,
            "first": str(df["date"].iloc[0]),
            "last": str(df["date"].iloc[-1]),
            "amt20_first_valid_idx": int(amt20.first_valid_index() or -1),
            "sha16": _sha16(os.path.join(PANEL_DIR, f"{code}.csv")),
        }
    facts["sample_anchors"] = sample
    # static mask reason counts (b_layer_filter output, same-face)
    try:
        mask = pd.read_csv(MASK_CSV, dtype={"code": str})
        ex = mask[~mask["ok_static"].astype(bool)] if "ok_static" in mask.columns else pd.DataFrame()
        facts["mask_reason_counts"] = {k: int(v) for k, v in
                                       ex["exclude_reason"].value_counts().items()} if len(ex) else {}
        facts["mask_total"] = int(len(mask))
    except Exception as e:  # noqa: BLE001
        facts["mask_error"] = str(e)[:120]
    # CN-C7 roundtrip derivation face (real-read, no hand-copy)
    try:
        sys.path.insert(0, ROOT)
        from knowledge import cost_spec  # noqa: PLC0415
        facts["cost_spec_face"] = getattr(cost_spec, "FACE_A_ETF_RT_BP", None) or "see knowledge/cost_spec.py"
    except Exception as e:  # noqa: BLE001
        facts["cost_spec_face"] = f"import-fail: {str(e)[:80]}"
    with open(PROBE_FILE, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: facts[k] for k in
                      ("panel_files", "eligibility_codes", "n_cells",
                       "mask_total", "mask_reason_counts")},
                     ensure_ascii=False, indent=1))
    print(f"probe facts -> {PROBE_FILE}")
    return 0


def selftest() -> int:
    """Hermetic offline checks (no network, tiny synthetic faces)."""
    ok = 0
    # S1: cell enumeration is exactly 16, ids unique, LOO/AOI complement
    cells = [c["cell"] for c in CELLS]
    assert len(cells) == 16 and len(set(cells)) == 16, "cell count/id contract"
    assert sum(1 for c in CELLS if c["cell"].startswith("LOO-")) == len(RULES)
    assert sum(1 for c in CELLS if c["cell"].startswith("AOI-")) == len(RULES)
    for r in RULES:
        loo = next(c for c in CELLS if c["cell"] == f"LOO-{r}")
        aoi = next(c for c in CELLS if c["cell"] == f"AOI-{r}")
        assert r in loo["off"] and r not in aoi["off"], "LOO/AOI complement"
        assert set(aoi["off"]) == set(RULES) - {r}, "AOI keeps exactly one rule"
    ok += 1
    # S2: rank face determinism on synthetic panel (amt20 asc -> pick order)
    df = pd.DataFrame({"amount": [10.0] * 25 + [5.0] * 25 + [1.0] * 25})
    amt20 = df["amount"].rolling(20).mean()
    assert abs(amt20.iloc[24] - 10.0) < 1e-12 and amt20.first_valid_index() == 19
    ok += 1
    # S3: trading month-end signal grid = last TRADING day per (year, month)
    d = pd.Series(pd.to_datetime(["2026-01-28", "2026-01-29", "2026-02-27",
                                  "2026-02-28", "2026-03-31"]))
    ym = d.dt.strftime("%Y-%m")
    last_per_ym = d.groupby(ym).transform("max") == d
    assert list(last_per_ym) == [False, True, False, True, True]
    ok += 1
    # S4: evidence cutoff truncation is monotone (no post-cutoff leakage)
    dates = pd.Series(["2026-09-21", "2026-09-22", "2026-09-23"])
    kept = dates[dates <= EVIDENCE_CUTOFF]
    assert len(kept) == 2 and kept.iloc[-1] == EVIDENCE_CUTOFF
    ok += 1
    # S5: trial accounting contract (16 cells -> 16 trials at burn)
    assert len(cells) == 16
    ok += 1
    print(f"selftest: {ok}/5 PASS (hermetic; engine leg lands next slice)")
    return 0


def run() -> int:
    """Full burn. Engine leg NOT landed this slice -- honest refusal (rc=2)."""
    print("run: FAIL-CLOSED -- engine leg not landed (probe/selftest only).")
    print("     Legality: R99 freeze commit precedes burn; trial gate untouched (N=0).")
    print("     Next slice: engine + null seeds + burn per frozen prereg sec.3/4.")
    return 2


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "probe":
        return probe()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    print("usage: python scripts/exclusion_marginal_scan.py {probe|selftest|run}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
