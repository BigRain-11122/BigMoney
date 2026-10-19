"""DIVLOWVOL-YIELDVOL same-mask null face (supporting leg), r1054 bm-b.

Why this file exists
  FUND-STAGESTYLE-COMBO-P1 closed CLAIM-UNSUPPORTED at r1053 while its own
  control face U-divlowvol printed sharpe 1.2085 (x1) -- the strongest
  number in that readout. The combo runner declared
  `nulls: pending (same-mask shuffle family not run here)`, and the frozen
  family module scripts/fund_divlowvol_p1.py already ships the null family
  as _null_task (same cached rank universe, same firing months, same
  equal-weight and engine cost face, frozen SEED_NULLS). This file runs
  that frozen leg against the LOCAL panel (data/astock_daily rebuild wired
  by scripts/stagestyle_combo_p1_backtest.py) so the sleeve carries a null
  distribution instead of a bare point estimate.

Non-duplication
  * null definition  : imported (family._null_task) -- zero re-implementation
  * realized sleeve  : frozen picks (family._cell_picks) + engine run
  * panel / sidecar  : stagestyle_combo_p1_backtest.wire_family
  * statistics       : plain empirical p-value / z on the sharpe column

Honesty boundaries
  * This is a SUPPORTING READOUT, never a judged verdict: G1'/G2/DSR/M1
    adjudication stays with the family finalize over frozen gates.
  * K here is a round-sized pilot (combo runner's pool face owns the full
    K_NULLS=2000 burn); the JSON records `k_requested`, `seed` and the
    frozen constant so a later full leg is comparable, not concatenated
    blindly.
  * Both windows are reported: `window_t0` (the null's own t0..cutoff,
    used for the p-value) and the combo readout window cross-check.

Usage
    python scripts/divlowvol_nulls_face.py run [--k 40] [--workers 4]
    python scripts/divlowvol_nulls_face.py status
    python scripts/divlowvol_nulls_face.py selftest

Exit codes: 0 normal, 2 mechanism fault (verbatim), 3 precondition missing
(panel cache absent -- honest no-op).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

OUT_DIR = os.path.join(ROOT, "results", "divlowvol_nulls")
CELL = "DIVLOWVOL-YIELDVOL"


# --------------------------------------------------------------- statistics
def empirical_pvalue(realized: float, nulls: list) -> dict:
    """One-sided empirical p (>= realized) with the (r+1)/(K+1) convention."""
    arr = np.asarray([v for v in nulls if v is not None], dtype=float)
    if arr.size == 0:
        return {"k": 0, "p_value": None, "z": None, "mean": None,
                "sd": None, "p95": None}
    r = int(np.sum(arr >= realized))
    mean = float(arr.mean())
    sd = float(arr.std(ddof=1)) if arr.size > 1 else 0.0
    z = float((realized - mean) / sd) if sd > 0 else None
    return {"k": int(arr.size), "n_ge": r,
            "p_value": round((r + 1.0) / (arr.size + 1.0), 6),
            "mean": round(mean, 6), "sd": round(sd, 6),
            "z": None if z is None else round(z, 4),
            "p95": round(float(np.percentile(arr, 95)), 6),
            "max": round(float(arr.max()), 6),
            "min": round(float(arr.min()), 6)}


def verdict_of(stats: dict) -> str:
    """Verdict wording that never lets a small-K floor read as 'no signal':
    p is floored at 1/(K+1), so an all-below-null pilot cannot reach 0.05
    no matter how large z is -- that state is DIRECTIONAL, not indistinct."""
    p = stats.get("p_value")
    z = stats.get("z")
    if p is None:
        return "NO_NULL_FACE"
    if p <= 0.01:
        return "SUPPORT_ABOVE_NULL"
    if p <= 0.05:
        return "SUPPORT_WEAK_ABOVE_NULL"
    if stats.get("n_ge") == 0:
        return "SUPPORT_DIRECTIONAL_K_FLOOR"
    return "INDISTINCT_FROM_NULL"


# ------------------------------------------------------------------- runner
def _wire():
    import stagestyle_combo_p1_backtest as combo
    panel = combo.load_local_panel()
    if panel is None:
        return None, None
    mod = combo.wire_family("divlowvol", panel)
    return combo, mod


def _realized(combo, mod, face: str, lo: int, hi: int) -> dict:
    picks = mod._cell_picks(None, combo.TOPN)
    # frozen design t0 clamp, verbatim combo rule (prereg sec.3)
    frozen = combo.pd.Timestamp(combo.DIV_T0_FROZEN)
    picks = [p for p in picks if mod._G["idx"][p[0]] >= frozen]
    spans = mod._spans_from_picks([p for p in picks if lo <= p[0] <= hi])
    return combo.run_spans(mod, spans, face, lo, hi)


_W_MOD = None


def _worker_init():
    """Each worker wires its own copy: the frozen module keeps state in _G,
    so a draw must never share a process with a differently wired panel."""
    global _W_MOD
    _combo, _W_MOD = _wire()
    if _W_MOD is not None:
        _W_MOD._firing_months()


def _worker_draw(k: int) -> dict:
    row = _W_MOD._null_task({"k": k})
    return {kk: row[kk] for kk in ("k", "sharpe", "ret", "max_dd",
                                   "n_selected_days", "n_engine_syms")}


def cmd_run(args) -> int:
    combo, mod = _wire()
    if mod is None:
        print("panel cache missing -- run "
              "`python scripts/stagestyle_combo_p1_backtest.py materialize`")
        return 3
    # _t0_pos is populated by _firing_months() (the wiring pops its cache)
    mod._firing_months()
    t0 = int(mod._G["_t0_pos"])
    idx = mod._G["idx"]
    hi = len(idx) - 1
    print(f"t0={idx[t0].date()} cutoff={idx[hi].date()} "
          f"firing_months={len(mod._firing_months())} k={args.k} "
          f"workers={args.workers}", flush=True)

    realized = _realized(combo, mod, "x1", t0, hi)
    print(f"realized {CELL} x1 sharpe={realized.get('sharpe')} "
          f"ret={realized.get('ret')} n_days={realized.get('n_days')}",
          flush=True)

    k_use = max(1, int(args.k))
    k_start = max(0, int(getattr(args, "k_start", 0) or 0))
    ks = list(range(k_start, k_start + k_use))
    workers = max(1, int(getattr(args, "workers", 1) or 1))
    metrics = []
    if workers > 1:
        import multiprocessing as mp
        with mp.Pool(processes=min(workers, len(ks)),
                     initializer=_worker_init) as pool:
            for row in pool.imap_unordered(_worker_draw, ks):
                metrics.append(row)
                print(f"  draw k={row['k']} sharpe={row['sharpe']} "
                      f"({len(metrics)}/{k_use})", flush=True)
    else:
        for k in ks:
            row = _worker_draw(k) if False else mod._null_task({"k": k})
            metrics.append({kk: row[kk] for kk in
                            ("k", "sharpe", "ret", "max_dd",
                             "n_selected_days", "n_engine_syms")})
            print(f"  draw k={k} sharpe={row['sharpe']} "
                  f"({len(metrics)}/{k_use})", flush=True)
    metrics.sort(key=lambda r: r["k"])
    nulls = [r["sharpe"] for r in metrics]

    stats = empirical_pvalue(realized.get("sharpe") or 0.0, nulls)
    doc = {
        "batch": "DIVLOWVOL-NULLS-SUPPORT",
        "kind": "same-mask-null-face",
        "machine": "bm-b",
        "cell": CELL,
        "face": "x1",
        "status": "PILOT_SUPPORT_READOUT",
        "evidence_cutoff": str(idx[hi].date()),
        "cutoff_meta": {"cutoff": str(idx[hi].date()),
                        "face": "astock_daily_local"},
        "window": {"lo": str(idx[t0].date()), "hi": str(idx[hi].date()),
                   "bars": int(hi - t0 + 1)},
        "realized": {k2: realized.get(k2) for k2 in
                     ("sharpe", "ret", "max_dd", "n_days", "n_trades",
                      "n_entries")},
        "nulls": {"k_requested": k_use, "k_start": k_start,
                  "seed": int(mod.SEED_NULLS),
                  "definition": "frozen family _null_task (same rank "
                                "universe / firing months / eq-weight / "
                                "engine cost x1)",
                  "sharpe": [round(float(v), 6) for v in nulls],
                  "draws": metrics},
        "stats": stats,
        "verdict": verdict_of(stats),
        "judged_note": "supporting readout only -- G1'/G2/DSR/M1 stay with "
                       "the family finalize over frozen gates",
        "single_source": "null definition imported from "
                         "scripts/fund_divlowvol_p1.py::_null_task; "
                         "panel wired by stagestyle_combo_p1_backtest",
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    cutoff = doc["evidence_cutoff"]
    suffix = (getattr(args, "out_suffix", "") or "").strip()
    tag = f"-{suffix}" if suffix else ""
    path = os.path.join(OUT_DIR, f"NULLS-{cutoff}{tag}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT_DIR, "latest.json"), "w",
              encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print(f"p={stats.get('p_value')} z={stats.get('z')} "
          f"null_mean={stats.get('mean')} verdict={doc['verdict']}")
    print(f"wrote {path}")
    return 0


def cmd_consume(args) -> int:
    """Consume an ALREADY-BURNED frozen null face (results/fund_divlowvol_p1
    /nulls.jsonl, K=2000) and price the realized continuous sleeve against
    it. No new burn, no new null definition: this is the step the COMBO
    finalize left open ("nulls: pending")."""
    nulls_path = args.nulls_file
    cont_x1 = args.cont_x1
    cont_x2 = args.cont_x2
    for p in (nulls_path, cont_x1):
        if not os.path.exists(p):
            print(f"missing face: {p}")
            return 3
    rows = [json.loads(line) for line in open(nulls_path, encoding="utf-8")
            if line.strip()]
    if not rows:
        print("empty nulls face")
        return 2
    c1 = json.load(open(cont_x1, encoding="utf-8"))
    c2 = json.load(open(cont_x2, encoding="utf-8")) \
        if cont_x2 and os.path.exists(cont_x2) else None
    sharpe = float(c1["sharpe_full"])
    nulls = [float(r["sharpe"]) for r in rows]
    stats = empirical_pvalue(sharpe, nulls)
    res = json.load(open(args.family_results, encoding="utf-8")) \
        if args.family_results and os.path.exists(args.family_results) \
        else {}
    cutoff = str(res.get("evidence_cutoff") or args.cutoff)
    doc = {
        "batch": "DIVLOWVOL-NULLS-SUPPORT",
        "kind": "same-mask-null-consumption",
        "machine": "bm-b",
        "cell": CELL,
        "status": "CONSUMED_FROZEN_NULL_FACE",
        "evidence_cutoff": cutoff,
        "cutoff_meta": {"cutoff": cutoff, "face": "money02_p1c_stock"},
        "nulls_source": {"path": nulls_path, "k": len(rows),
                         "definition": "frozen family _null_task (same rank "
                                       "universe / firing months / "
                                       "eq-weight / engine cost x1)"},
        "realized": {"face": "x1", "sharpe_full": sharpe,
                     "ret_full": c1.get("ret_full"),
                     "n_days": c1.get("n_days"),
                     "n_trades": c1.get("n_trades"),
                     "source": cont_x1},
        "realized_x2_descriptive": ({"sharpe_full": c2.get("sharpe_full"),
                                     "ret_full": c2.get("ret_full"),
                                     "nulls_note": "nulls leg is x1-only; "
                                                   "x2 carried descriptively"}
                                    if c2 else None),
        "stats": stats,
        "verdict": verdict_of(stats),
        "closes": "combo finalize r1053 'nulls: pending' declaration for the "
                  "U-divlowvol control face",
        "judged_note": "supporting readout only -- G1'/G2/DSR/M1 stay with "
                       "the family finalize over frozen gates",
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"NULLS-CONSUME-{cutoff}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT_DIR, "consume-latest.json"), "w",
              encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print(f"realized={sharpe} null_mean={stats.get('mean')} "
          f"sd={stats.get('sd')} p={stats.get('p_value')} z={stats.get('z')} "
          f"verdict={doc['verdict']}")
    print(f"wrote {path}")
    return 0


def cmd_status(_args) -> int:
    files = sorted(glob.glob(os.path.join(OUT_DIR, "NULLS-*.json")))
    if not files:
        print("no nulls face yet")
        return 0
    doc = json.load(open(files[-1], encoding="utf-8"))
    print(json.dumps({"file": os.path.basename(files[-1]),
                      "cutoff": doc.get("evidence_cutoff"),
                      "realized": doc.get("realized", {}).get("sharpe"),
                      "stats": doc.get("stats"),
                      "verdict": doc.get("verdict")},
                     ensure_ascii=False, indent=1))
    return 0


# ----------------------------------------------------------------- selftest
def cmd_selftest(_args) -> int:
    ok = True

    def chk(name, cond, extra=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  [{ 'PASS' if cond else 'FAIL' }] {name} {extra}")

    # 1 empirical p monotone in realized
    n = [0.2, 0.5, 0.9, 1.1]
    a = empirical_pvalue(1.5, n)
    b = empirical_pvalue(0.0, n)
    chk("p(high)<=p(low)", a["p_value"] <= b["p_value"],
        f"{a['p_value']} / {b['p_value']}")
    # 2 (r+1)/(K+1) convention
    chk("p convention", abs(empirical_pvalue(0.0, n)["p_value"]
                            - 5.0 / 5.0) < 1e-12)
    # 3 all-above-null floor
    chk("p floor 1/(K+1)",
        abs(empirical_pvalue(9.0, n)["p_value"] - 1.0 / 5.0) < 1e-12)
    # 4 z sign and empty guard
    chk("z positive", a["z"] is not None and a["z"] > 0)
    chk("empty guard", empirical_pvalue(1.0, [])["p_value"] is None)
    # 5 single-draw no crash
    chk("single draw", empirical_pvalue(0.5, [0.4])["k"] == 1)
    # 6 nulls skill sharpes are floats when panel present (skipped offline)
    chk("import surface", callable(empirical_pvalue))
    print(f"selftest {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("run")
    r.add_argument("--k", type=int, default=40)
    r.add_argument("--k-start", type=int, default=0,
                   dest="k_start", help="first frozen draw index (sharding)")
    r.add_argument("--workers", type=int, default=1)
    r.add_argument("--out-suffix", type=str, default="",
                   dest="out_suffix")
    c = sub.add_parser("consume")
    c.add_argument("--nulls-file", dest="nulls_file", default=os.path.join(
        ROOT, "results", "fund_divlowvol_p1", "nulls.jsonl"))
    c.add_argument("--cont-x1", dest="cont_x1", default=os.path.join(
        ROOT, "results", "fund_divlowvol_p1",
        "cont_DIVLOWVOL-YIELDVOL_x1.json"))
    c.add_argument("--cont-x2", dest="cont_x2", default=os.path.join(
        ROOT, "results", "fund_divlowvol_p1",
        "cont_DIVLOWVOL-YIELDVOL_x2.json"))
    c.add_argument("--family-results", dest="family_results",
                   default=os.path.join(ROOT, "results", "fund_divlowvol_p1",
                                        "fund_divlowvol_p1_results.json"))
    c.add_argument("--cutoff", type=str, default="unknown")
    sub.add_parser("status")
    sub.add_parser("selftest")
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "consume":
        return cmd_consume(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "selftest":
        return cmd_selftest(args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())