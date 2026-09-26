"""_r256bmb_anchor_probe.py -- T-80 anchor-drift localizer (one-shot, fleet-shareable).

Context: bm-a 14:30 T80 battery burn refused at the FIRST sleeve-domain anchor
(AGGR-CONC-TOP2 w_cur got ret 0.040724 vs frozen 0.043774, same n_days 177;
fail-closed, zero partial products). bm-a's message hypothesizes canon/dA
cell byte drift -- THIS PROBE DISPROVES THE HYPOTHESIS BY CONSTRUCTION: the
anchor got{} is computed from SLEEVES ONLY (data/daily panel ->
run_backtest eq curves -> blend), while canon/dA cells feed W-GRID which the
battery computes AFTER the anchor assert. Therefore transferring dA/canon
cannot clear this gate; the drift lives in the panel/engine/env face.

What it does (exact mirror of the battery's pre-anchor legs, grids SKIPPED --
anchor does not consume them):
  1. battery-parity gates: weight sha, frozen anchors, RAM floor, cutoff
  2. sleeve phase verbatim: 28 members x 2 faces over prices[:2026-09-23]
  3. ALL 20 variant anchors recomputed (w_cur/w_seg/judgments) vs frozen
     aggressive_lab.json / aggressive_family.json -- exact dict equality,
     battery _assert_anchor semantics
  4. cross-machine fingerprints: env versions, per-symbol truncated-panel
     digests, per-member eq digests, states/sharpe-map digests -- two
     machines compare these WITHOUT transferring any data

Usage:  python results/_r256bmb_anchor_probe.py [--t56-caliber]
        --t56-caliber: strip post-T56-freeze registry deltas (exit_overrides +
        dd_control keys, the r242 T-78 s4 winner wiring on C01/C02/ENGULF)
        inside each worker process before the sleeve backtest -- tests
        whether T-56-caliber restoration reproduces the frozen anchors.
Output: results/_r256bmb_anchor_probe.json (+ -t56caliber.json suffix in
        caliber mode) + per-variant PASS/FAIL stdout
Exit:   0 = all 20 anchors bit-identical (machine is anchor-faithful)
        2 = gate/env failure (RAM floor, panel cutoff, import face)
        3 = any anchor mismatch (drift localized to sleeve/panel/env face)
"""
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "_r256bmb_anchor_probe.json")


def _caliber_init(flag: str):
    """Worker-process patch: serve trader specs from the T-56-freeze-commit
    registry snapshot (results/t56_caliber_registry/firm/traders/*.json,
    extracted byte-faithfully from git 0389dee6) so the sleeve backtest runs
    at the exact caliber the frozen T-56/T-58 anchors were computed with
    (pre the r242 T-78 s4 winner wiring: no take_profit_levels/fractions,
    no dd_control, pre-re-derive OOS sharpe)."""
    import json as _json
    import os as _os
    import t28_stable_profit as t28
    snap = _os.path.join(_os.path.dirname(
        _os.path.abspath(__file__)), "t56_caliber_registry",
        "firm", "traders")

    def _snapshot_trader(tid):
        with open(_os.path.join(snap, f"{tid}.json"), encoding="utf-8") as fh:
            return _json.load(fh)

    t28.load_trader = _snapshot_trader


def main() -> int:
    t0 = time.time()
    caliber = "--t56-caliber" in sys.argv
    if caliber:
        globals()["OUT_JSON"] = OUT_JSON.replace(
            ".json", "-t56caliber.json")
    import pandas as pd
    import aggr_fullpool_battery as bat

    if bat.free_ram_gb() < bat.RAM_FLOOR_GB:
        print(f"[probe] RAM GATE FAIL: free {bat.free_ram_gb():.1f}GB < "
              f"{bat.RAM_FLOOR_GB}GB")
        return 2

    w_faces, sha56, _ = bat.build_weights()
    fam_faces, shafam = bat.build_family_weights()
    t56f, t58f = bat._load_frozen_anchors()
    for name, sha in sha56.items():
        if sha != bat.FROZEN_SHA[name]:
            print(f"[probe] SHA GATE FAIL: {name} {sha}")
            return 2
    print(f"[probe] weight sha gates PASS (6+19) + frozen anchors in place")

    prices_full = bat.load_core()
    cutoff = max(df.index.max() for df in prices_full.values())
    if cutoff < bat.SLEEVE_CUTOFF:
        print(f"[probe] PANEL GATE FAIL: cutoff {cutoff.date()} < "
              f"{bat.SLEEVE_CUTOFF.date()}")
        return 2
    prices = {s: df[df.index <= bat.SLEEVE_CUTOFF]
              for s, df in prices_full.items()}
    print(f"[probe] panel: {len(prices)} symbols, cutoff {cutoff.date()}, "
          f"truncated to {bat.SLEEVE_CUTOFF.date()}")

    jobs = [(tid, mult, prices, bat.SLEEVE_CUTOFF) for tid in bat.ROSTER
            for mult in (None, 2.0)]
    pool_kw = ({"initializer": _caliber_init, "initargs": ("1",)}
               if caliber else {})
    res = bat.run_cells_parallel(
        [(f"{a[0]}|{a[1] or 'x1'}", bat._sleeve_worker, a) for a in jobs],
        workers=min(bat.worker_cap(), 25), desc="anchor-probe-sleeves",
        **pool_kw)
    sleeves = {}
    for tid in bat.ROSTER:
        r1, r2 = res[f"{tid}|x1"], res[f"{tid}|2.0"]
        for r in (r1, r2):
            r["eq_s"] = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        sleeves[tid] = {"x1": r1, "x2": r2}
    print(f"[probe] sleeves: {len(sleeves)} members x 2 faces "
          f"({time.time()-t0:.0f}s)")

    states = bat.v3_state_series()
    if caliber:
        import glob as _glob
        snap_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "t56_caliber_registry", "firm", "traders")
        sharpe_map = {}
        for p in _glob.glob(os.path.join(snap_dir, "*.json")):
            with open(p, encoding="utf-8") as fh:
                d = json.load(fh)
            if d.get("id") in bat.ROSTER:
                sharpe_map[d["id"]] = float(
                    d["backtest"]["out_sample"]["sharpe"])
        if set(sharpe_map) != set(bat.ROSTER):
            print("[probe] SHARPE GATE FAIL: snapshot roster incomplete")
            return 2
    else:
        sharpe_map = bat._oos_sharpe_map()

    anchors, fails = {}, []
    for name in bat.ALL_VARIANTS:
        pr1, pr2, _rep_w, _meta = bat._variant_series(
            name, w_faces, fam_faces, sleeves, states, sharpe_map,
            sha56, shafam)
        wcur = {"x1": bat._window_face(pr1, bat.W_CUR_START, bat.W_CUR_END),
                "x2": bat._window_face(pr2, bat.W_CUR_START, bat.W_CUR_END)}
        wseg = {f: bat._seg_classes(pr, states) for f, pr in
                (("x1", pr1), ("x2", pr2))}
        j1 = bool(wcur["x1"]["ret"] > 0 and abs(wcur["x1"]["dd"]) <= 0.05)
        j2 = bool(wcur["x2"]["ret"] > 0)
        j3 = all((wseg[f][c]["cum_ret"] is not None
                  and wseg[f][c]["cum_ret"] >= -0.05)
                 for f in ("x1", "x2") for c in ("bull", "chop", "bear"))
        got = {"w_cur": wcur, "w_seg": wseg,
               "judgments": {"J1_current_window_profit": j1,
                             "J2_x2_survival": j2,
                             "J3_regime_segment_stability": j3}}
        frozen = (t56f["variants"][name] if name in bat.VARIANTS
                  else t58f["variants"][name])
        src = ("aggressive_lab.json" if name in bat.VARIANTS
               else "aggressive_family.json")
        delta = {k: {"got": got[k], "want": frozen[k]}
                 for k in ("w_cur", "w_seg", "judgments")
                 if got[k] != frozen[k]}
        anchors[name] = {"pass": not delta, "source": src,
                         "delta": delta or None}
        if delta:
            fails.append(name)
            print(f"[probe] {name}: FAIL vs {src}")
            for k, d in delta.items():
                print(f"    {k}: got {json.dumps(d['got'])[:200]}")
                print(f"    {k}: want {json.dumps(d['want'])[:200]}")
        else:
            print(f"[probe] {name}: PASS")

    # ------------------------------------------------- fingerprints
    def _sha_lines(lines):
        h = hashlib.sha256()
        for ln in lines:
            h.update(ln.encode("utf-8"))
        return h.hexdigest()[:16]

    panel_fp = {}
    for sym in sorted(prices):
        df = prices[sym]
        panel_fp[sym] = {
            "n": int(len(df)),
            "first": str(df.index.min().date()),
            "last": str(df.index.max().date()),
            "sha": _sha_lines(
                f"{d.date()}|{o:.10g}|{h_:.10g}|{l:.10g}|{c:.10g}|"
                f"{v:.10g}|{a:.10g}"
                for d, o, h_, l, c, v, a in zip(
                    df.index, df["open"], df["high"], df["low"],
                    df["close"], df["volume"], df["amount"]))}

    eq_fp = {}
    for tid in bat.ROSTER:
        for face in ("x1", "x2"):
            r = sleeves[tid][face]
            eq_fp[f"{tid}|{face}"] = _sha_lines(
                f"{d}:{e:.8f}"
                for d, e in zip(pd.to_datetime(r["dates"]), r["eq"]))

    import numpy as np
    out = {
        "batch": "T80-ANCHOR-PROBE",
        "machine": bat.machine_id(),
        "mode": "t56_caliber_strip" if caliber else "current_registry",
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "probe_sha256_16": hashlib.sha256(
            open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16],
        "sleeve_cutoff": str(bat.SLEEVE_CUTOFF.date()),
        "panel_cutoff": str(cutoff.date()),
        "anchors": anchors,
        "n_pass": len(bat.ALL_VARIANTS) - len(fails),
        "n_total": len(bat.ALL_VARIANTS),
        "fails": fails,
        "fingerprints": {
            "python": sys.version.split()[0],
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "panel_symbols": len(prices),
            "panel": panel_fp,
            "member_eq": eq_fp,
            "states_sha": _sha_lines(f"{d}:{s}" for d, s in
                                     states.items()),
            "sharpe_map_sha": _sha_lines(
                f"{k}:{v:.8f}" for k, v in sorted(sharpe_map.items())),
        },
        "runtime_s": round(time.time() - t0, 1),
    }
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, default=str)
    print(f"[probe] {out['n_pass']}/{out['n_total']} anchors bit-identical; "
          f"artifact {OUT_JSON} ({out['runtime_s']}s)")
    return 0 if not fails else 3


if __name__ == "__main__":
    sys.exit(main())
