"""P-1e zoo behavior-factor IC batch runner (P1E_ZOO_BEHAVIOR_IC.md, frozen r219).

Prereg SS9 schedule step-2 delivery: runner + selftest BEFORE pooling
(O-20260924-2100 execution-face split: >5min compute = runnable_pool +
autofill; in-round inline runs forbidden by the frozen prereg).

Reuse only, no rewrite (prereg SS6):
  - p1c_stock_ic_batch: load_universe / fwd_rets / gates_v123 (identical
    recorded-v1 constants V1 floor 0.02, V2 IR 0.30, V3 retain 0.5, A3 500)
    / _chain_head_total (r60 one-chain head: max total over results/ AND
    results/shortline/)
  - shortline_p1_ic._ic_series_fast (rank-after-pairing fast IC) with the
    batch-pre equivalence gate vs composite_ic.ic_series (<=1e-6, abort)
  - p1e_factors constructors (selftest-gated r219, ARC brute-force 1.18e-15)
  - science_gates.append_ledger (pure fn returning dict -> caller MUST
    embed the return value, r217 lesson)

Frozen by prereg before any numbers (SS0/SS3/SS4):
  cells        : 7 members (#85 terrified/stv, #92 coin_team, #93
               arc/vrc/src/krc) x 3 horizons (h5/h10/h20), h10 primary
  nulls        : 3 mask classes x K=50 white noise, seeds 67000+i
               (SEED_REGISTRY 'p1e_zoo_behavior'), class blocks in frozen
               order [M_close, M_close_tr, M_arc] -> seeds 67000..67149
  masks        : input-tradability masks, P-1d mask-class paradigm
               (data-face availability of the same-class real factor's
               inputs -- NOT the estimator's warmup/validity sparsity):
                 M_close    = close finite            (terrified)
                 M_close_tr = close & tr_frac finite  (stv, coin_team)
                 M_arc      = close & tr & vwap finite (#93 family)
               support mismatch (real factors are warmer/sparser via
               rolling windows / 60-row ARC validity) is disclosed in the
               audit; V2 IR line is the true gate (family precedent).
  ledger       : append_ledger('P-1e', 157, ...) = 7 computed + 150 nulls;
                 engine ledger untouched (zero engine runs)
  cutoff       : evidence_cutoff = 2026-09-22 (cache stamp; frozen panel,
                 no reflow) -> top-level + science_gates.cutoff_meta

Subcommands (idempotent via checkpoints, safe to kill/restart):
  selftest                 offline gates (synthetic + frozen-constant
                           hand-computed legs + data-face census; no writes)
  run-nulls --class C      one mask-class null leg -> p1e_nulls_<C>.json
  run-cells               7 members x 3h -> p1e_partial/<factor>.json
  finalize                authoritative gates + results JSON/CSV + ledger
                           (fail-closed: any missing/err part = exit 2,
                           zero artifacts, r217 law)
  status                  checkpoint census
"""
import argparse
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import p1c_stock_ic_batch as P1C                    # established harness
from composite_ic import IS_END, ic_series, stats_block   # methodology
from shortline_p1_ic import _ic_series_fast         # gated fast IC path
import p1e_factors as F                             # frozen constructors
from science_gates import (SEED_REGISTRY, append_ledger,  # r217 pure fn
                           ledger_head)  # r231 fix family: canonical head

CACHE_DIR = P1C.CACHE_DIR
OUT_DIR = P1C.OUT_DIR                              # results/shortline
RES_DIR = os.path.join(ROOT, "research", "shortline")
PARTIAL_DIR = os.path.join(OUT_DIR, "p1e_partial")
RESULT_JSON = os.path.join(OUT_DIR, "p1e_zoo_behavior.json")
RESULT_CSV = os.path.join(RES_DIR, "p1e_zoo_behavior_results.csv")
EQUIV_JSON = os.path.join(OUT_DIR, "p1e_equiv.json")

HORIZONS = [5, 10, 20]
H_GATE = 10                    # primary judgement horizon (prereg SS4)
N_NULLS = 50
SEED0 = int(SEED_REGISTRY["p1e_zoo_behavior"])     # 67000, r219 registered
NULL_Q = 0.95
CUTOFF = "2026-09-22"          # evidence_cutoff (frozen cache stamp)
BATCH_TRIALS = 157             # 7 computed + 150 nulls (prereg SS0)
EQUIV_TOL = 1e-6
IS_END_TS = pd.Timestamp(IS_END)

# frozen class order = seed-block order (prereg SS3: seeds 67000+i, band
# 67000..67149, continuous ledger)
CLASSES = ["M_close", "M_close_tr", "M_arc"]
CLASS_MASK_NOTE = {
    "M_close": "close finite (terrified inputs: close-derived returns)",
    "M_close_tr": "close & tr_frac finite (stv/coin_team inputs)",
    "M_arc": "close & tr_frac & vwap finite (#93 family inputs)",
}
# member -> its mask class (prereg SS3 null classes)
MEMBERS = [
    ("zoo85_terrified", "M_close"),
    ("zoo85_stv", "M_close_tr"),
    ("zoo92_coin_team", "M_close_tr"),
    ("zoo93_arc", "M_arc"),
    ("zoo93_vrc", "M_arc"),
    ("zoo93_src", "M_arc"),
    ("zoo93_krc", "M_arc"),
]


# ------------------------------------------------------------------ panels

def _load_field(idx, syms, field, ffill=False):
    mm = np.load(os.path.join(CACHE_DIR, field + ".npy"), mmap_mode="r")
    df = pd.DataFrame(np.asarray(mm, dtype=np.float64),
                      index=idx, columns=syms)
    if ffill:
        df = df.ffill()
    del mm
    return df


def load_sidecar_tr(idx, syms):
    """Derived turnover sidecar (r219 materialization; bars turnover col is
    all-NaN except final bar, TURNOVER_DERIVATION.md -- never consumed)."""
    p = os.path.join(CACHE_DIR, "turnover_derived.npy")
    mp = os.path.join(CACHE_DIR, "turnover_derived.meta.json")
    assert os.path.exists(p) and os.path.exists(mp), \
        "turnover_derived sidecar missing (scripts/p1e_turnover_derive.py)"
    meta = json.load(open(mp, encoding="utf-8"))
    assert meta["shape"]["T"] == len(idx) and meta["shape"]["N"] == len(syms), \
        "sidecar shape mismatch vs universe"
    tr = _load_field(idx, syms, "turnover_derived")
    fin = tr.values[np.isfinite(tr.values)]
    med = float(np.median(fin)) if fin.size else 0.0
    if med > 3.0:                      # percent -> fraction (probe convention)
        tr = tr / 100.0
        conv = "percent -> /100 to fraction"
    else:
        conv = "already fraction"
    return tr, {"source": "turnover_derived.npy sidecar",
                "sidecar_generated": meta.get("generated"),
                "convention": conv}


def load_panels(need):
    """Minimal per-shard panel load. ``need`` subset of {close, open, vwap,
    tr}. close/open are ffilled (P-1c harness convention), vwap raw."""
    idx, syms, meta = P1C.load_universe()
    out = {}
    for f in sorted(need):
        if f == "tr":
            tr, tr_meta = load_sidecar_tr(idx, syms)
            out["tr"] = tr
            out["_tr_meta"] = tr_meta
        elif f == "vwap":
            out["vwap"] = _load_field(idx, syms, "vwap")
        else:
            out[f] = _load_field(idx, syms, f, ffill=True)
    return idx, syms, meta, out


def build_masks(panels):
    """Per-class minimal load form: a mask is built only from panels
    actually loaded (M_close runs close-only and must not touch
    tr/vwap -- r221 first-fire KeyError fix, r198 mirror family)."""
    close = panels["close"]
    m_close = close.notna()
    out = {"M_close": m_close}
    if "tr" in panels:
        m_tr = m_close & panels["tr"].notna()
        out["M_close_tr"] = m_tr
        if "vwap" in panels:
            out["M_arc"] = m_tr & panels["vwap"].notna()
    return out


# ------------------------------------------------------- batch-pre gates

def equivalence_gate(panels, tag):
    """Batch-run precondition (prereg SS3): fast IC vs reference on a real
    cache slice; write-once evidence file; abort exit 1 on fail."""
    if os.path.exists(EQUIV_JSON):
        ev = json.load(open(EQUIV_JSON, encoding="utf-8"))
        if ev.get("pass") and ev.get("max_abs_diff", 9.9) <= EQUIV_TOL:
            print(f"equivalence checkpoint PASS (max|d|="
                  f"{ev['max_abs_diff']:.2e}, cached)", flush=True)
            return ev
    close = panels["close"]
    sl = close.iloc[-600:, :60]
    fwd20 = close.shift(-20) / close - 1.0
    probe = -close.pct_change(60)
    ref = ic_series(probe, fwd20)
    fast = _ic_series_fast(probe, fwd20)
    common = ref.index.intersection(fast.index)
    worst = float((ref[common] - fast[common]).abs().max()) \
        if len(common) else 9.9
    ok = worst <= EQUIV_TOL and len(ref) == len(fast)
    ev = {"tag": tag, "n_ref": len(ref), "n_fast": len(fast),
          "max_abs_diff": worst, "tol": EQUIV_TOL, "pass": bool(ok),
          "probe": "-mom60 real slice 600x60, fwd h20 (P-1c selftest form)"}
    if ok and not os.path.exists(EQUIV_JSON):
        with open(EQUIV_JSON, "w", encoding="utf-8") as f:
            json.dump(ev, f, indent=2)
    print(f"equivalence gate [{tag}]: n_ref={len(ref)} n_fast={len(fast)} "
          f"max|d|={worst:.2e} {'PASS' if ok else 'FAIL'}", flush=True)
    if not ok:
        sys.exit(1)
    return ev


# ------------------------------------------------------------------ nulls

def class_seed_band(cls):
    i = CLASSES.index(cls)
    return SEED0 + i * N_NULLS, SEED0 + (i + 1) * N_NULLS   # [lo, hi)


def run_nulls(cls):
    lo, hi = class_seed_band(cls)
    out_path = os.path.join(OUT_DIR, f"p1e_nulls_{cls}.json")
    if os.path.exists(out_path):
        old = json.load(open(out_path, encoding="utf-8"))
        print(f"nulls checkpoint exists for {cls} (n_nulls="
              f"{old.get('n_nulls')}), skip", flush=True)
        return 0
    t0 = time.time()
    idx, syms, meta, panels = load_panels({"close", "tr", "vwap"}
                                          if cls == "M_arc" else
                                          ({"close", "tr"}
                                           if cls == "M_close_tr"
                                           else {"close"}))
    # all classes need the full mask census for the audit; M_close leg
    # avoids loading tr/vwap by reporting honestly what it saw:
    ev = equivalence_gate(panels, f"run-nulls/{cls}")
    close = panels["close"]
    fwd = P1C.fwd_rets({"close": close})
    masks = build_masks(panels)
    mask = masks[cls]
    n_cells = int(mask.sum().sum())
    print(f"class {cls}: mask cells={n_cells} "
          f"({n_cells / float(mask.size):.4f} share), "
          f"seed band [{lo}, {hi})", flush=True)
    abs_means = {h: [] for h in HORIZONS}
    abs_irs = {h: [] for h in HORIZONS}
    for k in range(N_NULLS):
        rng = np.random.default_rng(lo + k)
        vals = pd.DataFrame(rng.standard_normal(close.shape),
                            index=close.index, columns=close.columns)
        vals = vals.where(mask)
        for h in HORIZONS:
            s = _ic_series_fast(vals, fwd[h])
            blk = stats_block(s[s.index <= IS_END_TS])
            if "ic_mean" in blk:
                abs_means[h].append(abs(blk["ic_mean"]))
                abs_irs[h].append(abs(blk["ic_ir"]))
        del vals
        if (k + 1) % 10 == 0:
            print(f"  nulls[{cls}] {k + 1}/{N_NULLS} "
                  f"({time.time() - t0:.0f}s)", flush=True)
    per_h = {f"h{h}": {
        "p95_abs_ic": round(float(np.quantile(abs_means[h], NULL_Q)), 4),
        "p50_abs_ic": round(float(np.median(abs_means[h])), 4),
        "p95_abs_ir": round(float(np.quantile(abs_irs[h], NULL_Q)), 4),
        "n_nulls": len(abs_means[h]),
    } for h in HORIZONS}
    out = {
        "class": cls,
        "mask": CLASS_MASK_NOTE[cls],
        "mask_cells": n_cells,
        "mask_cell_share": round(n_cells / float(mask.size), 4),
        "n_nulls": N_NULLS,
        "seed_band": [lo, hi],
        "seed_base": SEED0,
        "noise": "white noise standard normal, masked by class mask",
        "is_end": str(IS_END),
        "per_h": per_h,
        "meta": {"elapsed_s": round(time.time() - t0, 1),
                 "equivalence": ev,
                 "turnover": panels.get("_tr_meta"),
                 "evidence_cutoff": CUTOFF},
    }
    json.loads(json.dumps(out))          # verify-parse before write (r185)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"saved: {out_path} ({json.dumps(per_h)})", flush=True)
    return 0


# ------------------------------------------------------------------ cells

def _cell_record(nm, fdf, fwd, t_start):
    rec = {"factor": nm, "status": "ok", "compute_s": round(time.time() - t_start, 2)}
    is_rows = fdf.index <= IS_END_TS
    rec["is_valid_cells"] = int(fdf.loc[is_rows].notna().sum().sum())
    rec["is_valid_cell_share"] = round(
        rec["is_valid_cells"] / float(np.prod(fdf.loc[is_rows].shape)), 4)
    for h in HORIZONS:
        s = _ic_series_fast(fdf, fwd[h])
        blk_full = stats_block(s)
        blk_is = stats_block(s[s.index <= IS_END_TS])
        blk_oos = stats_block(s[s.index > IS_END_TS])
        p = f"h{h}_"
        for seg, blk in (("full", blk_full), ("is", blk_is), ("oos", blk_oos)):
            rec[p + seg + "_ic"] = blk.get("ic_mean", "")
            rec[p + seg + "_ir"] = blk.get("ic_ir", "")
            rec[p + seg + "_n"] = blk.get("n_periods", 0)
    return rec


def run_cells():
    t0 = time.time()
    os.makedirs(PARTIAL_DIR, exist_ok=True)
    idx, syms, meta, panels = load_panels({"close", "open", "tr", "vwap"})
    ev = equivalence_gate(panels, "run-cells")
    close, open_, tr_frac = panels["close"], panels["open"], panels["tr"]
    vwap = panels["vwap"]
    rets = close / close.shift(1) - 1.0
    fwd = P1C.fwd_rets({"close": close})
    todo = [nm for nm, _ in MEMBERS
            if not os.path.exists(os.path.join(PARTIAL_DIR, nm + ".json"))]
    print(f"cells todo: {len(todo)}/{len(MEMBERS)}", flush=True)

    def _save(nm, rec):
        with open(os.path.join(PARTIAL_DIR, nm + ".json"), "w",
                  encoding="utf-8") as f:
            json.dump(rec, f, indent=2, ensure_ascii=False)

    # -- #85 legs (one frame at a time; peak RAM discipline)
    if "zoo85_terrified" in todo:
        tc = time.time()
        fdf = F.build_zoo85_terrified(rets)
        _save("zoo85_terrified", _cell_record("zoo85_terrified", fdf, fwd, tc))
        print("  zoo85_terrified done", flush=True)
        del fdf
    if "zoo85_stv" in todo:
        tc = time.time()
        fdf = F.build_zoo85_stv(rets, tr_frac)
        _save("zoo85_stv", _cell_record("zoo85_stv", fdf, fwd, tc))
        print("  zoo85_stv done", flush=True)
        del fdf
    if "zoo92_coin_team" in todo:
        tc = time.time()
        fdf = F.build_zoo92_coin_team(close, open_, tr_frac)
        _save("zoo92_coin_team",
              _cell_record("zoo92_coin_team", fdf, fwd, tc))
        print("  zoo92_coin_team done", flush=True)
        del fdf
    # -- #93 family (constructor returns all four at once)
    fam_todo = [nm for nm in ("zoo93_arc", "zoo93_vrc", "zoo93_src",
                              "zoo93_krc") if nm in todo]
    if fam_todo:
        tc = time.time()
        fam, n_bad = F.build_zoo93_arc_family(tr_frac, vwap, close)
        for nm in fam_todo:
            rec = _cell_record(nm, fam[nm], fwd, tc)
            rec["zoo93_nonfinite_arc_cells"] = n_bad
            _save(nm, rec)
            print(f"  {nm} done", flush=True)
        del fam
    print(f"run-cells complete ({time.time() - t0:.0f}s, "
          f"equivalence max|d|={ev['max_abs_diff']:.2e})", flush=True)
    return 0


# --------------------------------------------------------------- finalize

def _validate_inputs(nulls, cells):
    """Fail-closed pre-check (r217: any error/missing part = refuse,
    zero artifacts)."""
    problems = []
    for cls in CLASSES:
        if cls not in nulls:
            problems.append(f"nulls missing class {cls}")
        elif nulls[cls].get("n_nulls") != N_NULLS:
            problems.append(f"nulls[{cls}] n_nulls="
                            f"{nulls[cls].get('n_nulls')} != {N_NULLS}")
    for nm, _ in MEMBERS:
        if nm not in cells:
            problems.append(f"cell checkpoint missing: {nm}")
        elif cells[nm].get("status") != "ok":
            problems.append(f"cell[{nm}] status={cells[nm].get('status')}")
    return problems


def _thresholds(nulls):
    out = {}
    for cls in CLASSES:
        per_h = nulls[cls]["per_h"]
        out[cls] = {f"h{h}": {"p95_abs_ic": per_h[f"h{h}"]["p95_abs_ic"]}
                    for h in HORIZONS}
    return out


def finalize():
    t0 = time.time()
    nulls = {}
    for cls in CLASSES:
        p = os.path.join(OUT_DIR, f"p1e_nulls_{cls}.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                nulls[cls] = json.load(f)
    cells = {}
    for nm, _ in MEMBERS:
        p = os.path.join(PARTIAL_DIR, nm + ".json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                cells[nm] = json.load(f)
    problems = _validate_inputs(nulls, cells)
    if problems:
        print("FINALIZE REFUSED (fail-closed, zero artifacts):", flush=True)
        for x in problems:
            print(f"  - {x}", flush=True)
        sys.exit(2)
    thr = _thresholds(nulls)

    rows = []
    for nm, cls in MEMBERS:
        r = dict(cells[nm])
        r["mask_class"] = cls
        for h in HORIZONS:
            blk_is = {"ic_mean": r.get(f"h{h}_is_ic"),
                      "ic_ir": r.get(f"h{h}_is_ir"),
                      "n_periods": r.get(f"h{h}_is_n", 0)}
            blk_oos = {"ic_mean": r.get(f"h{h}_oos_ic")}
            g = P1C.gates_v123(blk_is, blk_oos, thr[cls][f"h{h}"])
            r[f"h{h}_pass"] = g["pass"]
            r[f"h{h}_v1_thr"] = max(P1C.V1_FLOOR,
                                    thr[cls][f"h{h}"]["p95_abs_ic"])
            if h == H_GATE:
                r["gates"] = g
                r["in_pool"] = g["pass"]        # h10 = primary judgement
        rows.append(r)
    pool = [r["factor"] for r in rows if r.get("in_pool")]
    per_h = {f"h{h}": sum(1 for r in rows if r.get(f"h{h}_pass"))
             for h in HORIZONS}

    # idempotent delta ledger (r61/p1c precedent): re-finalize with zero
    # new cells keeps the frozen ledger block verbatim.
    old = None
    if os.path.exists(RESULT_JSON):
        try:
            with open(RESULT_JSON, encoding="utf-8") as f:
                old = json.load(f)
        except Exception:
            old = None
    old_factors = {r.get("factor") for r in (old or {}).get("rows", [])}
    new_cells = [nm for nm, _ in MEMBERS if nm not in old_factors]
    if old is not None and not new_cells:
        _prev = ledger_head()["total"]     # r112 canonical (r231 fix family)
        ledger = old.get("trials_ledger") or {
            "prev_total": _prev, "batch_trials": 0, "total": _prev}
    else:
        prev = ledger_head()["total"]      # r112 canonical recursive head
        # (r231 fix family: the narrow P1C._chain_head_total misses nested
        # batch dirs such as results/wild_route/ and forks the chain)
        ledger = append_ledger(                  # pure fn -> EMBED (r217)
            "P-1e", BATCH_TRIALS,
            file_name="shortline/p1e_zoo_behavior.json",
            note="factor-ledger r32 accounting: 7 computed + 150 nulls "
                 "(3 mask classes x K=50, seeds 67000..67149); "
                 "delta-idempotent; engine ledger N untouched (zero "
                 "engine runs)",
            evidence_cutoff=CUTOFF, prev_total=prev)
    assert isinstance(ledger, dict) and "total" in ledger, "ledger embed"

    out = {
        "meta": {
            "batch": "P-1e zoo behavior-factor IC (#85/#92/#93)",
            "pre_reg": "research/shortline/P1E_ZOO_BEHAVIOR_IC.md "
                        "(frozen r219, commit 48163b47)",
            "order": "O-1819 advisory -> T-64 slice-5 consumption face "
                     "(ASTYLE_ZOO #85/#92/#93)",
            "claim": "MSG-20260926-0255-bm-b (F-04, r219)",
            "lane": "bm-b (prereg SS9; machine-local p1c_stock cache + "
                    "turnover sidecar, r188 lane-pin law)",
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "is_end": str(IS_END),
            "gate_horizon": H_GATE,
            "report_horizons": HORIZONS,
            "multiplicity": "7 members x 3 horizons counted; h10 is the "
                             "primary judgement; h20 crossers are archived "
                             "with a snooping discount, no promotion",
            "universe": "p1c_stock cache panel T=8792 N=5222 (ok 5130), "
                        "selection face NOT b_layer-masked (P-1c SS2 "
                        "same-caliber)",
            "seed_band": [SEED0, SEED0 + 3 * N_NULLS],
            "mask_classes": CLASS_MASK_NOTE,
            "mask_disclosure": "null masks are input-tradability masks "
                               "(P-1d paradigm); real factors carry extra "
                               "warmup/validity sparsity (rolling-20 / ARC "
                               "60-row window) -> nulls are slightly more "
                               "covered than the real members; V2 IR line "
                               "is the true gate (family precedent)",
            "engine_runs": 0,
        },
        "evidence_cutoff": CUTOFF,            # C2 legal key (top level)
        "science_gates": {"cutoff_meta": CUTOFF},
        "thresholds": {cls: nulls[cls]["per_h"] for cls in CLASSES},
        "nulls_meta": {cls: {"mask": nulls[cls]["mask"],
                              "mask_cells": nulls[cls]["mask_cells"],
                              "seed_band": nulls[cls]["seed_band"]}
                       for cls in CLASSES},
        "equivalence": json.load(open(EQUIV_JSON, encoding="utf-8"))
        if os.path.exists(EQUIV_JSON) else None,
        "counts": {"computed": len(rows), "nulls": 3 * N_NULLS,
                   "pool_h10": len(pool), "per_h_pass": per_h},
        "pool_h10": pool,
        "trials_ledger": ledger,
        "rows": rows,
        "audit": {
            "elapsed_s": round(time.time() - t0, 1),
            "workers": 1,
            "cpu_cap_policy": "O-20260923-1738 single-proc vectorized",
            "constructor_source": "scripts/p1e_factors.py (frozen r219, "
                                  "selftest ARC brute-force 1.18e-15)",
            "turnover": "derived sidecar (bars turnover col all-NaN "
                        "except final bar, never consumed)",
            "coverage": {r["factor"]: {
                "is_valid_cells": r.get("is_valid_cells"),
                "is_valid_cell_share": r.get("is_valid_cell_share")}
                for r in rows},
        },
    }
    json.loads(json.dumps(out))               # verify-parse before write
    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    pd.DataFrame(rows).to_csv(RESULT_CSV, index=False, encoding="utf-8")
    print(f"finalize: computed={len(rows)} pool_h10={len(pool)} "
          f"per_h={per_h}", flush=True)
    print(f"ledger: {json.dumps(ledger)}", flush=True)
    print(f"saved: {RESULT_JSON}", flush=True)
    print(f"saved: {RESULT_CSV}", flush=True)
    return 0


# ------------------------------------------------------------------ status

def status():
    n_nulls = sum(os.path.exists(os.path.join(
        OUT_DIR, f"p1e_nulls_{c}.json")) for c in CLASSES)
    ck = len(glob.glob(os.path.join(PARTIAL_DIR, "*.json")))
    print(f"nulls classes={n_nulls}/3 cells={ck}/7 "
          f"equiv={os.path.exists(EQUIV_JSON)} "
          f"final={os.path.exists(RESULT_JSON)}", flush=True)
    return 0


# ---------------------------------------------------------------- selftest

def selftest():
    t0 = time.time()
    ok_all = True

    def check(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}", flush=True)

    print("[1/9] constructor delegation (p1e_factors.selftest, frozen "
          "definitions):", flush=True)
    check("p1e_factors selftest rc==0", F.selftest() == 0)

    print("[2/9] synthetic IC equivalence vs composite_ic.ic_series:",
          flush=True)
    rng = np.random.default_rng(11)
    T, N = 300, 40
    idx = pd.date_range("2020-01-01", periods=T, freq="B")
    cols = [f"S{i}" for i in range(N)]
    close = pd.DataFrame(10 + np.cumsum(rng.normal(0, .2, (T, N)), axis=0),
                         index=idx, columns=cols)
    fac = pd.DataFrame(rng.standard_normal((T, N)), index=idx, columns=cols)
    facmask = rng.random((T, N)) < 0.8         # holes: mask interplay leg
    fac = fac.where(pd.DataFrame(facmask, index=idx, columns=cols))
    fwd = close.shift(-10) / close - 1.0
    ref = ic_series(fac, fwd)
    fast = _ic_series_fast(fac, fwd)
    common = ref.index.intersection(fast.index)
    worst = float((ref[common] - fast[common]).abs().max()) \
        if len(common) else 9.9
    check(f"IC equivalence max|d|={worst:.1e} n_eq={len(ref) == len(fast)}",
          worst <= EQUIV_TOL and len(ref) == len(fast))

    print("[3/9] seed-block mapping (frozen class order):", flush=True)
    check("SEED_REGISTRY base == 67000", SEED0 == 67000)
    bands = [class_seed_band(c) for c in CLASSES]
    flat = [s for lo, hi in bands for s in range(lo, hi)]
    check("3x50 disjoint continuous band 67000..67149",
          len(flat) == 150 and len(set(flat)) == 150
          and min(flat) == 67000 and max(flat) == 67149)
    check("class order frozen [M_close, M_close_tr, M_arc]",
          CLASSES == ["M_close", "M_close_tr", "M_arc"]
          and class_seed_band("M_close")[0] == 67000
          and class_seed_band("M_close_tr")[0] == 67050
          and class_seed_band("M_arc")[0] == 67100)

    print("[4/9] mask-class logic on synthetic panels:", flush=True)
    pn = {"close": close, "tr": fac, "vwap": fac * 0.5}
    pn["tr"].iloc[:5, 0] = np.nan              # tr hole in col 0
    pn["vwap"].iloc[10:15, 1] = np.nan          # vwap hole in col 1
    mk = build_masks(pn)
    mc, mt, ma = mk["M_close"], mk["M_close_tr"], mk["M_arc"]
    check("M_close == close finite",
          bool((mc == close.notna()).all().all()))
    check("M_close_tr == close & tr (hole respected)",
          bool((mt == (close.notna() & pn['tr'].notna())).all().all())
          and not bool(mt.iloc[:5, 0].any()))
    check("M_arc == close & tr & vwap (both holes respected)",
          bool((ma == (close.notna() & pn['tr'].notna()
                      & pn['vwap'].notna())).all().all())
          and not bool(ma.iloc[10:15, 1].any())
          and not bool(ma.iloc[:5, 0].any()))
    mk_prod = build_masks({"close": close})   # M_close production form
    check("M_close production form: close-only panels, no KeyError, "
          "single honest mask (r221)",
          set(mk_prod.keys()) == {"M_close"}
          and bool((mk_prod["M_close"] == close.notna()).all().all()))

    print("[5/9] V1/V2/V3 hand-computed legs (production gates_v123):",
          flush=True)
    # fixture A: is 0.04 (thr 0.025 -> V1 T), ir 0.31 (V2 T), oos 0.018
    # (< 0.5*0.04 -> V3 F), n 600 -> A3 T; hand: pass=False
    gA = P1C.gates_v123({"ic_mean": 0.04, "ic_ir": 0.31, "n_periods": 600},
                        {"ic_mean": 0.018}, {"p95_abs_ic": 0.025})
    check("fixture A: v1 v2 a3 T, v3 F, pass F",
          gA["v1"] and gA["v2"] and gA["a3"] and not gA["v3"]
          and not gA["pass"])
    # fixture B: retention exactly 0.5 boundary -> >= passes; sign flip F
    gB = P1C.gates_v123({"ic_mean": 0.04, "ic_ir": 0.31, "n_periods": 600},
                        {"ic_mean": 0.020}, {"p95_abs_ic": 0.025})
    gC = P1C.gates_v123({"ic_mean": 0.04, "ic_ir": 0.31, "n_periods": 600},
                        {"ic_mean": -0.05}, {"p95_abs_ic": 0.025})
    check("fixture B boundary |oos|==0.5|is| passes V3", gB["v3"]
          and gB["pass"])
    check("fixture C opposite-sign oos fails V3 despite magnitude",
          not gC["v3"] and not gC["pass"])
    # fixture D: below null p95 -> V1 F even above floor
    gD = P1C.gates_v123({"ic_mean": 0.022, "ic_ir": 0.31, "n_periods": 600},
                        {"ic_mean": 0.015}, {"p95_abs_ic": 0.025})
    check("fixture D null p95 binds over 0.02 floor -> V1 F",
          not gD["v1"] and not gD["pass"])

    print("[6/9] nulls checkpoint idempotency + fail-closed finalize:",
          flush=True)
    check("nulls guard: existing file -> skip path",
          os.path.exists(os.path.join(
              OUT_DIR, "p1e_nulls_M_close.json")) is False
          or json.load(open(os.path.join(OUT_DIR, "p1e_nulls_M_close.json"),
                           encoding="utf-8")).get("n_nulls") == N_NULLS)
    probs = _validate_inputs({"M_close": {"n_nulls": 50}},
                             {"zoo85_terrified": {"status": "ok"}})
    check("validate_inputs refuses on missing classes/cells",
          len(probs) == 2 + 6)   # 2 nulls classes + 6 cells missing
    probs2 = _validate_inputs(
        {c: {"n_nulls": 50} for c in CLASSES},
        {nm: {"status": "ok"} for nm, _ in MEMBERS})
    check("validate_inputs green on complete fixture", probs2 == [])
    probs3 = _validate_inputs(
        {c: {"n_nulls": 50} for c in CLASSES},
        dict([("zoo93_krc", {"status": "error"})] +
             [(nm, {"status": "ok"}) for nm, _ in MEMBERS
              if nm != "zoo93_krc"]))
    check("validate_inputs refuses error-status cell (r217)",
          any("zoo93_krc" in x for x in probs3))

    print("[7/9] ledger embed leg (append_ledger pure fn, r217):", flush=True)
    led = append_ledger("P-1e-selftest-fixture", 157, prev_total=100,
                        evidence_cutoff=CUTOFF)
    check("ledger returns dict, total=prev+157, cutoff embedded",
          isinstance(led, dict) and led["total"] == 257
          and led["prev_total"] == 100
          and led.get("evidence_cutoff") == CUTOFF)

    print("[8/9] fwd/turnover conventions:", flush=True)
    c2 = pd.DataFrame({"A": [1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0,
                             256.0, 512.0, 1024.0, 2048.0]})
    fw = P1C.fwd_rets({"close": c2})[10]      # P1C HORIZONS = [5,10,20]
    expect0 = c2.iloc[10, 0] / c2.iloc[0, 0] - 1.0
    check("fwd_ret h10 == close.shift(-10)/close-1",
          bool(np.isclose(fw.iloc[0, 0], expect0))
          and bool(fw.iloc[2:].isna().all().all())
          and bool(fw.iloc[:2].notna().all().all()))
    tr_pct = pd.DataFrame([[5.0], [7.0]])
    med = float(np.median(tr_pct.values[np.isfinite(tr_pct.values)]))
    check("turnover unit probe: median>3 -> /100 (probe convention)",
          med > 3.0 and (tr_pct / 100.0).iloc[0, 0] == 0.05)

    print("[9/9] frozen data-face census (existence/read, no batch):",
          flush=True)
    try:
        idx2, syms2, meta2 = P1C.load_universe()
        check("universe meta loads",
              meta2["shape"]["T"] == 8792 and meta2["shape"]["N"] == 5222)
        side = os.path.join(CACHE_DIR, "turnover_derived.npy")
        check("sidecar + all consumed fields present",
              os.path.exists(side) and all(
                  os.path.exists(os.path.join(CACHE_DIR, f + ".npy"))
                  for f in ("close", "open", "vwap")))
        head = np.load(os.path.join(CACHE_DIR, "close.npy"), mmap_mode="r")
        check("close npy head readable shape match",
              tuple(head.shape) == (8792, 5222))
        del head
    except Exception as ex:
        check(f"data-face census ({type(ex).__name__}: {str(ex)[:80]})",
              False)

    print(f"SELFTEST {'PASS' if ok_all else 'FAIL'} "
          f"({time.time() - t0:.0f}s)", flush=True)
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["selftest", "run-nulls", "run-cells",
                                     "finalize", "status"])
    ap.add_argument("--class", dest="cls",
                    choices=CLASSES + ["ALL"])
    a = ap.parse_args()
    if a.mode == "selftest":
        sys.exit(selftest())
    if a.mode == "status":
        sys.exit(status())
    if a.mode == "run-nulls":
        if not a.cls:
            print("--class required (or ALL)", flush=True)
            sys.exit(2)
        order = CLASSES if a.cls == "ALL" else [a.cls]
        rc = 0
        for cls in order:
            rc |= run_nulls(cls)
        sys.exit(rc)
    if a.mode == "run-cells":
        sys.exit(run_cells())
    if a.mode == "finalize":
        sys.exit(finalize())


if __name__ == "__main__":
    main()
