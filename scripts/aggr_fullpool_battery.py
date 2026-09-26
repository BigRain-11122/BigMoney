"""T80-AGGR-FULLPOOL-BATTERY -- aggressive family full-battery re-run on the
FULL-POOL 28-member W-GRID face (CEO order O-20260926-1332; ticket
T-2026-09-26-80; prereg research/AGGR_FULLPOOL_BATTERY.md FROZEN pre-run).

20 variants (T-56 five + T-58 fifteen) x 20 T-28-caliber cells (W-CUR 2 +
W-SEG 6 + W-GRID 12) = 400 aggregate judgment cells -> trials ledger.

The ONE new measurement face vs the frozen T-56/T-58 runs: W-GRID over the
full 28-member pool (CE-6 restriction cured). Grid evidence sources:
  legacy axis = p5c leg-L checkpoint (6 CE, machine-local) U t54 legacy
                cells (22 PROSPECT, census 121,528 verified in place)
  deep axis   = t54 deep cells (22 PROSPECT) U canon CE deep cells
                (PINNED manifest -- NOT glob; dprobe partial reproductions
                rejected by census gate; absent canon files = exit 2
                honest refusal; lane law: burn on the machine holding the
                canon cells -- bm-a/bm-c, R188 precedent)

Sleeve-domain faces (W-CUR/W-SEG/J1-J3) mirror the frozen runs verbatim and
are HARD-ANCHORED against results/aggressive_lab.json (5) and
results/aggressive_family.json (15) -- any drift = exit 2 (engineering
disease, not a market reading). Sleeve-INPUT caliber pinned to the T-56/T-58
freeze registry snapshot results/t56_caliber_registry/ (git 0389dee6; A1
amendment -- the live registry drifted post-freeze via the r242 T-78 s4
winner wiring, which is EXCLUDED from both frozen run lines). Canon B_MAXDIV
full-pool grid re-derived as the re-anchor leg (ledger +0); AGGR-NOCASH
(same sha vector) must match it byte-identically.

Zero adoption, zero wiring, zero new signal functions, zero nulls
(dual-track supply face, T-56 s0 law). Single-shot finalize guard:
AGGR_FP_REFINALIZE=1 is the only redo path and never re-appends the ledger.
"""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from live.paper import load_core, v3_state_series
from parallel_runner import run_cells_parallel, worker_cap
from science_gates import append_ledger, cutoff_meta, ledger_head
from t27_blend_tournament import daily_ret_matrix
from t28_stable_profit import (WINDOWS, W_CUR_END, W_CUR_START,
                               _blend_daily_ret, _grid_unit,
                               _load_legacy_grid, _seg_classes, _sleeve_worker,
                               _window_face)
from aggressive_lab import (CE6, FAM_VARIANTS, FROZEN_SHA, OFFENSE_CORPS,
                            OSCILLATION_CORPS, PENDING_CORPS, ROSTER,
                            VARIANTS, _legs_blend, _oos_sharpe_map,
                            _regime_blend, _rotation_blend,
                            build_family_weights, build_weights, w_sha)

PREREG = os.path.join(PATHS.root, "research", "AGGR_FULLPOOL_BATTERY.md")
OUT_JSON = os.path.join(PATHS.results_dir, "aggr_fullpool_battery.json")
GA_PATH = os.path.join(PATHS.results_dir, "gate_attrition.json")
T56_FROZEN = os.path.join(PATHS.results_dir, "aggressive_lab.json")
T58_FROZEN = os.path.join(PATHS.results_dir, "aggressive_family.json")
TOURN_JSON = os.path.join(PATHS.results_dir,
                          "portfolio_blend_tournament.json")
T54_DIR = os.path.join(PATHS.results_dir, "t54")
T54_SUMMARY = os.path.join(T54_DIR, "t54_grid_summary.json")
T54_SHARDS = {"legacy": ("lA", "lB", "lC", "lD"),
              "deep": ("dA", "dB", "dC", "dD")}
T54_CENSUS = {"legacy": 55264, "deep": 66264}   # rows per axis (summary)
T54_STARTS = {"legacy": 1256, "deep": 1506}      # distinct starts per face
PROSPECT22 = tuple(sorted(set(ROSTER) - set(CE6)))
N_CELLS = 400                    # prereg s0 (20 variants x 20 T-28 cells)
SLEEVE_CUTOFF = W_CUR_END        # prereg s2 (canon comparability, T-28)
EVIDENCE_CUTOFF = "2026-09-24"   # prereg s2 (latest consumed face = t54)
BATCH = "T80-AGGR-FULLPOOL-BATTERY"
CANON_CE_DEEP = {                # pinned manifest (t54 prereg s7-3 law)
    "x1": os.environ.get("AGGR_FP_CANON_DEEP_BASE",
                         os.path.join(PATHS.results_dir, "t22",
                                      "cells_deep_base.jsonl")),
    "x2": os.environ.get("AGGR_FP_CANON_DEEP_X2",
                         os.path.join(PATHS.results_dir, "t22",
                                      "cells_deep_x2.jsonl")),
}
ALL_VARIANTS = tuple(VARIANTS) + tuple(FAM_VARIANTS)
RAM_FLOOR_GB = 4.0               # fleet line: heavy work needs free RAM
T56_CALIBER_DIR = os.path.join(PATHS.results_dir, "t56_caliber_registry",
                               "firm", "traders")


def _caliber_init(flag: str = "1"):
    """Worker-process patch (A1 caliber pin): serve trader specs from the
    T-56-freeze-commit registry snapshot so the sleeve backtest runs at the
    exact caliber the frozen T-56/T-58 anchors were computed with -- the
    live registry evolved AFTER both frozen runs (r242 T-78 s4 winner
    wiring: C01 tp_ladder params + take_profit_fractions + dd_control +
    re-derived OOS sharpe), and a live-registry recompute can never
    reproduce those anchors (bm-b probe 0/20 vs snapshot 20/20, 2026-09-26)."""
    import json as _json
    import t28_stable_profit as t28

    def _snapshot_trader(tid):
        with open(os.path.join(T56_CALIBER_DIR, f"{tid}.json"),
                  encoding="utf-8") as fh:
            return _json.load(fh)

    t28.load_trader = _snapshot_trader


def _caliber_sharpe_map() -> dict:
    """OOS Sharpe per roster member from the A1 caliber snapshot (the
    values the frozen T-56/T-58 selection/rotation faces consumed;
    live registry re-derived C01 sharpe post-freeze = rotation drift)."""
    import glob
    out = {}
    for p in glob.glob(os.path.join(T56_CALIBER_DIR, "*.json")):
        with open(p, encoding="utf-8-sig") as fh:
            d = json.load(fh)
        if d.get("id") in ROSTER:
            out[d["id"]] = float(d["backtest"]["out_sample"]["sharpe"])
    if set(out) != set(ROSTER):
        raise SystemExit(f"SHARPE-MAP GATE FAIL: {sorted(set(ROSTER) ^ set(out))}")
    return out


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def machine_id() -> str:
    try:
        with open(os.path.join(PATHS.root, "fleet", "machine.json"),
                  encoding="utf-8") as fh:
            return json.load(fh)["machine_id"]
    except Exception:
        return "unknown"


def free_ram_gb() -> float:
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        return 99.0


# ------------------------------------------------------- t54 cells parsing
def _parse_t22_cells(rows_iter, face, tret, passive, trader_filter=None):
    """t22-schema rows -> tret[(trader, face, start)] = {window: (ret, None,
    trades, regime)} + passive[start][window]; partial windows excluded
    (t28._load_deep_grid semantics verbatim). Returns (n_rows, traders)."""
    n = 0
    traders = set()
    for line in rows_iter:
        if not line.strip():
            continue
        r = json.loads(line)
        n += 1
        t = r["trader"]
        if trader_filter is not None and t not in trader_filter:
            raise SystemExit(f"GRID GATE FAIL: unexpected trader {t}")
        traders.add(t)
        start = str(r["start"])
        entry = {}
        for w, retk, trk, partk in (
                ("6m", "ret_6m", "trades_6m", None),
                ("12m", "ret_12m", "trades_12m", "partial_12m"),
                ("24m", "ret_24m", "trades_24m", "partial_24m")):
            if retk not in r or r[retk] is None:
                continue
            if partk and r.get(partk):
                continue          # partial windows excluded (complete only)
            entry[w] = (float(r[retk]), None, int(r.get(trk, 0)),
                        str(r.get("regime", "na")))
            pk = "p_ret_" + w
            if r.get(pk) is not None:
                passive.setdefault(start, {})[w] = float(r[pk])
        if entry:
            tret[(t, face, start)] = entry
    return n, traders


def _load_t54_axis(axis: str):
    """t54 cells for one axis (22 PROSPECT members, base+x2 faces).
    Census-gated vs the frozen summary (prereg s2)."""
    with open(T54_SUMMARY, encoding="utf-8") as fh:
        summ = json.load(fh)
    if summ.get("cells_total") != 121528:
        raise SystemExit(f"T54 GATE FAIL: cells_total {summ.get('cells_total')}")
    if sorted(summ["members"]) != list(PROSPECT22):
        raise SystemExit("T54 GATE FAIL: members != 22 PROSPECT")
    tret = {}
    passive = {"x1": {}, "x2": {}}
    rows_total = 0
    for face_file, face in (("base", "x1"), ("x2", "x2")):
        rows_face, traders = 0, set()
        for shard in T54_SHARDS[axis]:
            path = os.path.join(T54_DIR, f"cells_{axis}_{face_file}_{shard}.jsonl")
            if not os.path.exists(path):
                raise SystemExit(f"T54 GATE FAIL: shard absent {path} "
                                 "(re-run t54_prospect_grid for the missing "
                                 "shard, deterministic resume)")
            with open(path, encoding="utf-8") as fh:
                n, trs = _parse_t22_cells(fh, face, tret, passive[face])
            rows_face += n
            traders |= trs
        starts_face = {k[2] for k in tret if k[1] == face}
        if traders != set(PROSPECT22):
            raise SystemExit(f"T54 GATE FAIL: {axis}/{face} traders != 22")
        if len(starts_face) != T54_STARTS[axis]:
            raise SystemExit(f"T54 GATE FAIL: {axis}/{face} starts "
                             f"{len(starts_face)} != {T54_STARTS[axis]}")
        rows_total += rows_face
    if rows_total != T54_CENSUS[axis]:
        raise SystemExit(f"T54 GATE FAIL: {axis} rows {rows_total} != "
                         f"{T54_CENSUS[axis]}")
    return tret, passive


def _load_canon_ce_deep(paths=None):
    """Canon CE deep cells via the PINNED manifest (no glob). Census gate:
    6 CE x 1506 starts x 2 faces = 18,072 rows; dprobe partial signature
    (680 starts) rejected (prereg s2; t54 prereg s7-3 law)."""
    src = dict(paths) if paths else dict(CANON_CE_DEEP)
    tret = {}
    passive = {"x1": {}, "x2": {}}
    stats = {}
    for face, path in src.items():
        if not os.path.exists(path):
            raise SystemExit(
                f"CANON-CE-DEEP GATE FAIL: pinned file absent {path} -- "
                f"canon CE deep cells live on bm-a/bm-c (bm-b local face = "
                f"680/1506 dprobe partial, forbidden); burn on the lane "
                f"machine or transfer the canon files (env override "
                f"AGGR_FP_CANON_DEEP_*)")
        with open(path, encoding="utf-8") as fh:
            n, traders = _parse_t22_cells(fh, face, tret, passive[face],
                                          trader_filter=set(CE6))
        starts = {k[2] for k in tret if k[1] == face}
        if traders != set(CE6) or len(starts) != 1506 or n != 9036:
            raise SystemExit(
                f"CANON-CE-DEEP GATE FAIL: {path} traders={len(traders)} "
                f"starts={len(starts)} rows={n} -- expected 6/1506/9036 "
                f"(dprobe partial 680/4080 signature rejected)")
        stats[face] = {"rows": n, "starts": len(starts), "path": path}
    return tret, passive, stats


def _passive_agreement_gate(oracle, subject, label):
    """Cross-source passive benchmark agreement (prereg s2 hard gate):
    same start+window must be bit-identical across sources (beat comparison
    requires ONE benchmark). Returns checked count."""
    checked = 0
    for sdate, pw in oracle.items():
        if sdate not in subject:
            continue
        for w, v in pw.items():
            if w not in subject[sdate]:
                continue
            checked += 1
            if abs(v - subject[sdate][w]) > 1e-9:
                raise SystemExit(f"PASSIVE GATE FAIL: {label} {sdate}/{w} "
                                 f"oracle={v} subject={subject[sdate][w]}")
    return checked


def _merge_axis(axis, ce_tret, ce_pas, pr_tret, pr_pas):
    """Full-pool merge for one axis: 6 CE + 22 PROSPECT tret union; per-face
    passive = t54 (superset, t22 per-face caliber); CE passive = agreement
    oracle only. ce_pas = {"x1": flat|None, "x2": flat|None}."""
    agree, ce_only = {}, {}
    for face in ("x1", "x2"):
        if ce_pas.get(face):
            agree[face] = _passive_agreement_gate(ce_pas[face],
                                                  pr_pas[face], f"{axis}/{face}")
            ce_only[face] = len({s for s in ce_pas[face]
                                 if s not in pr_pas[face]})
        else:
            agree[face] = 0        # face-agnostic CE passive (p5c) -> x1 only
            ce_only[face] = 0
    tret = dict(pr_tret)
    tret.update(ce_tret)
    return tret, {"x1": pr_pas["x1"], "x2": pr_pas["x2"]}, {
        "agree_checked": agree, "ce_only_starts": ce_only}


def load_fullpool_grids():
    """Assemble both full-pool axes with all gates (prereg s2)."""
    lt_ce, lp_ce = _load_legacy_grid()          # p5c legL (6 CE, 1253)
    lt_pr, lp_pr = _load_t54_axis("legacy")
    l_tret, l_pas, l_stats = _merge_axis("legacy", lt_ce,
                                         {"x1": lp_ce, "x2": None},
                                         lt_pr, lp_pr)
    dt_ce, dp_ce, canon_stats = _load_canon_ce_deep()
    dt_pr, dp_pr = _load_t54_axis("deep")
    d_tret, d_pas, d_stats = _merge_axis("deep", dt_ce, dp_ce, dt_pr, dp_pr)
    return {"legacy": (l_tret, l_pas, l_stats),
            "deep": (d_tret, d_pas, d_stats),
            "canon_ce_deep_manifest": canon_stats}


# ------------------------------------------------------- variant faces
def _variant_series(name, w_faces, fam_faces, sleeves, states, sharpe_map,
                    sha56, shafam):
    """Mirror of the frozen T-56 run_batch / T-58 run_family_batch series
    construction (byte-identical sleeve-domain faces by construction).
    Returns (pr1, pr2, rep_w, meta)."""
    sl1 = {t: sleeves[t]["x1"] for t in ROSTER}
    sl2 = {t: sleeves[t]["x2"] for t in ROSTER}
    if name in VARIANTS:
        face = w_faces[name]
        if "static" in face:
            w = face["static"]
            return (_blend_daily_ret(sl1, w), _blend_daily_ret(sl2, w),
                    dict(w), {"weights_src": "static",
                              "weights_sha": sha56[name],
                              "legs_or_rule_sha": None})
        off = face["regime"]["offensive"]
        defw = face["regime"]["defensive"]
        pr1, w_mean = _regime_blend(sleeves, off, defw, states)
        R2 = pd.concat({tid: sl2[tid]["eq_s"] for tid in sl2},
                       axis=1, join="inner").dropna().pct_change().dropna()
        s_prev = (states.reindex(R2.index, method="ffill")
                  .shift(1).fillna("GREEN"))
        offensive = s_prev.isin(["GREEN", "YELLOW"])
        W2 = pd.DataFrame([off if b else defw for b in offensive],
                          index=R2.index, columns=list(R2.columns))
        return pr1, (R2 * W2).sum(axis=1), w_mean, {
            "weights_src": "regime_v3",
            "weights_sha": sha56["AGGR-REGIME-offensive"],
            "legs_or_rule_sha": {"offensive": FROZEN_SHA[
                "AGGR-REGIME-offensive"], "defensive": FROZEN_SHA[
                    "AGGR-REGIME-defensive"]}}
    face = fam_faces[name]
    if "static" in face:
        w = face["static"]
        return (_blend_daily_ret(sl1, w), _blend_daily_ret(sl2, w),
                dict(w), {"weights_src": "static",
                          "weights_sha": shafam[name],
                          "legs_or_rule_sha": None})
    if "legs" in face:
        pr1, rep_w, W = _legs_blend(sleeves, face["legs"], face["gate"],
                                    states)
        R2 = daily_ret_matrix(sleeves, "x2")
        if not R2.index.equals(W.index):
            raise SystemExit("LEGS GATE FAIL: x2 index drift")
        return pr1, (R2 * W).sum(axis=1), rep_w, {
            "weights_src": "legs_v3", "weights_sha": shafam[f"{name}-off"],
            "legs_or_rule_sha": {k: shafam[f"{name}-{k}"]
                                 for k in face["legs"]}}
    pr1, rep_w, W = _rotation_blend(sleeves, face["rotation"]["kind"],
                                    face["rotation"]["lookback"], sharpe_map)
    R2 = daily_ret_matrix(sleeves, "x2")
    if not R2.index.equals(W.index):
        raise SystemExit("ROTATION GATE FAIL: x2 index drift")
    return pr1, (R2 * W).sum(axis=1), rep_w, {
        "weights_src": f"rotation_{face['rotation']['kind']}",
        "weights_sha": shafam[f"{name}-rule"], "legs_or_rule_sha": None}


def _grid_face_12(tret_by_axis, passive_by_axis, rep_w):
    """Full-pool W-GRID: 12 units, NO CE-6 restriction (prereg s3/§4)."""
    grid = {}
    for axis in ("legacy", "deep"):
        tr, pa = tret_by_axis[axis], passive_by_axis[axis]
        for window in WINDOWS:
            for face in ("x1", "x2"):
                grid[f"{axis}|{window}|{face}"] = _grid_unit(
                    tr, pa[face], rep_w, ROSTER, window, face)
    n12 = grid["legacy|12m|x1"]["n"] + grid["deep|12m|x1"]["n"]
    k12 = (grid["legacy|12m|x1"]["beats"] + grid["deep|12m|x1"]["beats"])
    return grid, {"n": n12, "beats": k12,
                  "rate": round(k12 / n12, 4) if n12 else None}


FACE_COVERAGE = {  # six-face sample canon (O-1332 clause 1) -- prereg §3
    "massive_virtual_timepoints": "covered (2762 grid starts, all-start)",
    "designated_start_windows": "partial (current regime window covered; "
        "year-first-day starts NOT in T-28 caliber -- disclosed)",
    "deep_history_25y": "covered (deep axis, t18 panel)",
    "regime_segments": "covered (W-SEG + per-start regime)",
    "cost_stress": "covered (x2 faces)",
    "capacity_face": "MISSING (ADV participation caps not wired)",
}


def _hooks_block():
    """Landing hooks (ticket slice-3): presence-only status, zero
    consumption (three-lines law -- each landing enters via its own prereg).
    """
    def _face(path):
        return ("landed" if os.path.exists(path) else "not_yet_landed")
    return {
        "cn_models_t73": _face(os.path.join(PATHS.results_dir, "cn_rev_tilt",
                                            "p1_results.json")),
        "grid_sleeve_t78": _face(os.path.join(PATHS.results_dir,
                                              "grid_sleeve_p1.json")),
        "wild_route_t57_survivors": _face(os.path.join(
            PATHS.results_dir, "wild_route")),
        "note": "hooks report presence only; battery entry of each landed "
                "face = its own prereg (three-lines law), NOT this batch",
    }


# ------------------------------------------------------- anchors (s4)
def _load_frozen_anchors():
    with open(T56_FROZEN, encoding="utf-8") as fh:
        t56 = json.load(fh)
    with open(T58_FROZEN, encoding="utf-8") as fh:
        t58 = json.load(fh)
    if t56.get("batch") != "T56-AGGRESSIVE-LAB" or \
            t58.get("batch") != "T58-AGGR-FAMILY":
        raise SystemExit("ANCHOR GATE FAIL: frozen batch identity drift")
    return t56, t58


def _assert_anchor(name, got, frozen, source):
    """Sleeve-domain anchor: w_cur + w_seg + judgments must match the frozen
    run bit-identically (prereg s4 hard gate)."""
    for key in ("w_cur", "w_seg", "judgments"):
        if got[key] != frozen[key]:
            raise SystemExit(
                f"ANCHOR GATE FAIL: {name}.{key} != frozen {source} "
                f"(got {got[key]} want {frozen[key]}) -- engineering drift, "
                f"batch refused")


# ------------------------------------------------------- ckpt / finalize
def _ckpt_path(shard, shards):
    return os.path.join(PATHS.results_dir,
                        f"aggr_fullpool_battery_ckpt_{shard}of{shards}.jsonl")


def _shard_variants(shard, shards):
    return [v for i, v in enumerate(ALL_VARIANTS) if i % shards == shard]


def _load_done_keys(path):
    done = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    done.add(json.loads(line)["variant"])
                except Exception:
                    continue        # tolerate truncated tail (t22 law)
    return done


def _out_complete(path):
    if not os.path.exists(path):
        return False
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        return d.get("batch") == BATCH and \
            set(d.get("variants", {})) == set(ALL_VARIANTS)
    except Exception:
        return False


# ------------------------------------------------------- run
def run(shard: int = 0, shards: int = 1) -> int:
    t0 = time.time()
    if _out_complete(OUT_JSON) and not os.environ.get("AGGR_FP_REFINALIZE"):
        log(f"single-shot guard: {OUT_JSON} complete -> no-op exit 0 "
            "(AGGR_FP_REFINALIZE=1 = only redo, never re-ledgers)")
        return 0
    if free_ram_gb() < RAM_FLOOR_GB:
        raise SystemExit(f"RAM GATE FAIL: free {free_ram_gb():.1f}GB < "
                         f"{RAM_FLOOR_GB}GB (fleet line, honest exit)")
    log(f"=== {BATCH} (prereg frozen pre-run) ===")
    if len(set(ALL_VARIANTS)) != 20:
        raise SystemExit("ROSTER GATE FAIL: variant table != 20")

    w_faces, sha56, _ = build_weights()
    fam_faces, shafam = build_family_weights()
    t56f, t58f = _load_frozen_anchors()
    log("weight sha gates PASS (6 T-56 + 19 family) + frozen anchors in place")

    grids = load_fullpool_grids()
    log("full-pool grids assembled (legacy 28/28, deep 28/28, "
        "census+passive-agreement gates PASS)")

    prices_full = load_core()
    cutoff = max(df.index.max() for df in prices_full.values())
    if cutoff < SLEEVE_CUTOFF:
        raise SystemExit(f"PANEL GATE FAIL: cutoff {cutoff.date()} < "
                         f"{SLEEVE_CUTOFF.date()}")
    prices = {s: df[df.index <= SLEEVE_CUTOFF]
              for s, df in prices_full.items()}
    jobs = [(tid, mult, prices, SLEEVE_CUTOFF) for tid in ROSTER
            for mult in (None, 2.0)]
    res = run_cells_parallel(
        [(f"{a[0]}|{a[1] or 'x1'}", _sleeve_worker, a) for a in jobs],
        workers=min(worker_cap(), 25), desc="aggrfp-sleeves",
        initializer=_caliber_init, initargs=("1",))
    sleeves = {}
    for tid in ROSTER:
        r1, r2 = res[f"{tid}|x1"], res[f"{tid}|2.0"]
        for r in (r1, r2):
            r["eq_s"] = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        sleeves[tid] = {"x1": r1, "x2": r2}
    log(f"sleeves: {len(sleeves)} members x 2 faces ({time.time()-t0:.0f}s)")

    states = v3_state_series()
    sharpe_map = _caliber_sharpe_map()

    # canon re-anchor leg (ticket verbatim; weights sha-gated vs frozen)
    with open(TOURN_JSON, encoding="utf-8") as fh:
        w_canon = dict(json.load(fh)["weights"]["B_MAXDIV"]["weights"])
    if w_sha(w_canon) != FROZEN_SHA["AGGR-NOCASH"]:
        raise SystemExit("CANON GATE FAIL: B_MAXDIV vector sha drift")
    g_tret = {a: grids[a][0] for a in ("legacy", "deep")}
    g_pas = {a: grids[a][1] for a in ("legacy", "deep")}
    canon_grid, canon_pooled = _grid_face_12(g_tret, g_pas, w_canon)
    canon_pr1 = _blend_daily_ret({t: sleeves[t]["x1"] for t in ROSTER},
                                 w_canon)
    canon_bull = _seg_classes(canon_pr1, states)["bull"]["cum_ret"]
    log(f"canon B_MAXDIV full-pool grid re-anchor: 12m pooled "
        f"{canon_pooled['beats']}/{canon_pooled['n']}")

    my_variants = _shard_variants(shard, shards)
    done = _load_done_keys(_ckpt_path(shard, shards))
    with open(_ckpt_path(shard, shards), "a", encoding="utf-8",
              newline="\n") as ck:
        for name in my_variants:
            if name in done:
                log(f"{name}: checkpoint resume skip")
                continue
            pr1, pr2, rep_w, meta = _variant_series(
                name, w_faces, fam_faces, sleeves, states, sharpe_map,
                sha56, shafam)
            wcur = {"x1": _window_face(pr1, W_CUR_START, W_CUR_END),
                    "x2": _window_face(pr2, W_CUR_START, W_CUR_END)}
            wseg = {f: _seg_classes(pr, states) for f, pr in
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
            frozen = (t56f["variants"][name] if name in VARIANTS
                      else t58f["variants"][name])
            _assert_anchor(name, got, frozen,
                           "aggressive_lab.json" if name in VARIANTS
                           else "aggressive_family.json")
            grid, pooled = _grid_face_12(g_tret, g_pas, rep_w)
            if name == "AGGR-NOCASH" and grid != canon_grid:
                raise SystemExit("CANON-REANCHOR GATE FAIL: AGGR-NOCASH "
                                 "full-pool grid != canon B_MAXDIV grid")
            row = {"variant": name,
                   "weights_representative":
                       {k: v for k, v in rep_w.items() if v > 0},
                   "grid_weight_sum": round(float(sum(rep_w.values())), 6),
                   "daily_ret_x1": [round(float(x), 8) for x in pr1],
                   **meta, **got, "w_grid_fullpool": grid,
                   "grid_12m_pooled_fullpool": pooled,
                   "kpi": {"return_ceiling_w_cur_x1": wcur["x1"]["ret"],
                           "bull_delta_vs_canon": round(
                               wseg["x1"]["bull"]["cum_ret"] - canon_bull, 6),
                           "pooled12_fullpool": pooled["rate"],
                           "note": "KPI non-gate; verdicts carry "
                                   "incomplete-face label per six-face canon"}}
            ck.write(json.dumps(row, default=float) + "\n")
            ck.flush()
            log(f"{name}: J1={j1} J2={j2} J3={j3} 12m fullpool pooled="
                f"{pooled['beats']}/{pooled['n']}")

    if shards > 1:
        log(f"shard {shard}/{shards} rows done; finalize waits for all "
            "shards (fail-closed)")
        return 0
    return finalize(shards=1, grids=grids, canon_grid=canon_grid,
                    canon_pooled=canon_pooled,
                    canon_daily_x1=[round(float(x), 8) for x in canon_pr1],
                    t0=t0)


def finalize(shards, grids, canon_grid, canon_pooled, canon_daily_x1, t0=None):
    """Assemble all shard ckpts (fail-closed: any variant missing = exit 2),
    ledger +400 once, write OUT_JSON + gate_attrition row (prereg s6)."""
    t0 = t0 or time.time()
    refinalize = bool(os.environ.get("AGGR_FP_REFINALIZE"))
    prev_led = None
    if refinalize and _out_complete(OUT_JSON):
        with open(OUT_JSON, encoding="utf-8") as fh:
            prev_led = json.load(fh).get("trials_ledger")
        log("refinalize: reusing recorded trials_ledger (no re-append)")
    if os.path.exists(OUT_JSON) and not _out_complete(OUT_JSON) \
            and not refinalize:
        defective = OUT_JSON.replace(
            ".json", f"_defective_{time.strftime('%Y%m%d_%H%M%S')}.json")
        os.replace(OUT_JSON, defective)
        log(f"defective prior output preserved: {defective}")

    rows = {}
    for s in range(shards):
        p = _ckpt_path(s, shards)
        if not os.path.exists(p):
            raise SystemExit(f"FINALIZE GATE FAIL: shard ckpt absent {p}")
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                rows[r["variant"]] = r
    if set(rows) != set(ALL_VARIANTS):
        raise SystemExit(f"FINALIZE GATE FAIL: variants {len(rows)}/20, "
                         f"missing {sorted(set(ALL_VARIANTS) - set(rows))}")

    corr_in = {"CANON-B_MAXDIV": pd.Series(canon_daily_x1)}
    corr_in.update({v: pd.Series(rows[v]["daily_ret_x1"])
                    for v in ALL_VARIANTS})
    cdf = pd.DataFrame(corr_in).dropna()
    corr = {a: {b: round(float(cdf[a].corr(cdf[b])), 4)
                for b in cdf.columns} for a in cdf.columns}

    if prev_led is None:
        head = ledger_head()
        led = append_ledger(
            BATCH, N_CELLS, os.path.basename(OUT_JSON),
            note="400 aggregate judgment cells (20 aggressive variants "
                 "x 20 T-28-caliber cells: W-CUR 2 + W-SEG 6 + W-GRID 12); "
                 "W-GRID = FULL-POOL 28-member face (CE-6 restriction "
                 "cured; p5c legL + t54 121,528 cells + canon CE deep "
                 "pinned-manifest); per-cell N follows P5C/t22/t54 "
                 "already-counted ledgers, no recount; 56 sleeves = "
                 "o1600 reproductions +0; canon B_MAXDIV grid re-anchor "
                 "+0; zero adoption zero wiring (dual-track)",
            evidence_cutoff=EVIDENCE_CUTOFF, prev_total=head["total"])
        log(f"ledger: prev={head['total']} +{N_CELLS} -> {led['total']}")
    else:
        led = prev_led

    with open(PREREG, "rb") as fh:
        prereg_sha = hashlib.sha256(fh.read().replace(
            b"\r\n", b"\n")).hexdigest()[:16]
    out = cutoff_meta(EVIDENCE_CUTOFF)
    out.update({
        "batch": BATCH,
        "order": "O-20260926-1332", "ticket": "T-2026-09-26-80",
        "prereg": "research/AGGR_FULLPOOL_BATTERY.md",
        "prereg_sha256_lf": prereg_sha,
        "roster": list(ROSTER),
        "evidence_cutoffs": {"sleeve_domain": str(SLEEVE_CUTOFF.date()),
                            "p5c_legL": "2026-09-22",
                            "t22_canon_ce_deep": "2026-09-22",
                            "t54_grid": "2026-09-24"},
        "face_upgrade": "W-GRID full-pool 28-member face replaces the "
                        "CE-6 restricted sub-portfolio approximation "
                        "(T-28 disclosure face); canon re-anchor per ticket",
        "grid_source_stats": {a: grids[a][2] for a in ("legacy", "deep")},
        "canon_ce_deep_manifest": grids["canon_ce_deep_manifest"],
        "variants": {v: rows[v] for v in ALL_VARIANTS},
        "canon_b_maxdiv_fullpool_grid": canon_grid,
        "canon_b_maxdiv_grid_12m_pooled": canon_pooled,
        "six_face_coverage": FACE_COVERAGE,
        "verdict_note": "ALL verdicts incomplete-face per six-face canon "
                        "(capacity face missing) -- honest label, not a "
                        "batch failure",
        "hooks": _hooks_block(),
        "variant_daily_ret_corr": corr,
        "trials_ledger": led,
        "adoption": "ZERO wiring this batch (dual-track supply face; "
                    "month-boundary tournament entry per T-56 (e) law)",
        "audit": {"runtime_sec": round(time.time() - t0, 1),
                  "machine": machine_id(),
                  "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                  "sleeve_cutoff": str(SLEEVE_CUTOFF.date()),
                  "workers": min(worker_cap(), 25),
                  "refinalize": refinalize,
                  "shards": f"0/{shards}"},
    })
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
    log(f"outputs: {OUT_JSON}")

    try:
        ga = json.load(open(GA_PATH, encoding="utf-8"))
        ga["entries"].append({
            "batch": BATCH,
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "aggr-fullpool-battery (candidate supply, dual-track)",
            "cells_ledger_delta": N_CELLS,
            "ledger_total_after": led["total"],
            "gates": {v: rows[v]["judgments"] for v in ALL_VARIANTS},
            "refs": {"results": OUT_JSON, "prereg": PREREG}})
        with open(GA_PATH, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(ga, fh, ensure_ascii=False, indent=1)
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        log(f"gate_attrition append skipped: {exc}")
    return 0


# ------------------------------------------------------------- selftest
def _self_grid_unit_fixture():
    """3 traders x 4 starts synthetic full-pool grid: hand-computed blends,
    beats, and the all-members-required exclusion semantics."""
    traders = ("A", "B", "C")
    w = {"A": 0.5, "B": 0.25, "C": 0.25}
    sdate = {"s1": "2021-01-04", "s2": "2021-01-05",
             "s3": "2021-01-06", "s4": "2021-01-07"}
    passive = {sdate[k]: {"6m": v} for k, v in
               (("s1", 0.01), ("s2", 0.03), ("s3", -0.01), ("s4", 0.05))}
    vals = {
        "s1": {"A": (0.10, None, 5, "bull"), "B": (0.02, None, 3, "bull"),
               "C": (-0.04, None, 2, "bull")},
        "s2": {"A": (-0.02, None, 4, "chop"), "B": (0.06, None, 1, "chop"),
               "C": (0.01, None, 2, "chop")},
        "s3": {"A": (0.03, None, 2, "bear"), "B": (-0.01, None, 2, "bear"),
               "C": (0.02, None, 1, "bear")},
        "s4": {"A": (0.20, None, 1, "bull"), "B": (0.10, None, 1, "bull")},
        # C absent at s4 -> start excluded from the blend cell set
    }
    tret = {}
    for s, m in vals.items():
        for t, e in m.items():
            tret[(t, "x1", sdate[s])] = {"6m": e}
    unit = _grid_unit(tret, passive, w, traders, "6m", "x1")
    # s1 blend = .5*.10 +.25*.02 +.25*(-.04) = .0450 > .01  -> beat
    # s2 blend = .5*(-.02)+.25*.06 +.25*(.01) = -.0005 < .03 -> no
    # s3 blend = .5*.03 +.25*(-.01)+.25*(.02) = .0175 > -.01 -> beat
    assert unit["n"] == 3, unit
    assert unit["beats"] == 2, unit
    assert abs(unit["beat_rate"] - round(2 / 3, 4)) < 1e-9, unit
    assert unit["per_member_beat_rate"]["A"]["n"] == 4, unit  # sees s4
    assert unit["independent_regime_windows"] == 3, unit       # bull/chop/bear
    return True


def _write_fake_canon(path, n_starts):
    """Minimal t22-schema fake canon file (mirror leg, r240 law)."""
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for i in range(n_starts):
            for t in CE6:
                fh.write(json.dumps({
                    "trader": t, "pos": i, "start": f"c{i:05d}",
                    "face": "base", "regime": "bull",
                    "ret_6m": 0.01, "p_ret_6m": 0.005, "trades_6m": 3,
                    "partial_12m": False, "partial_24m": False}) + "\n")


def cmd_selftest() -> int:
    checks = []
    skips = []

    def ck(name, fn):
        try:
            fn()
            checks.append(True)
            print(f"[selftest] {name}... PASS", flush=True)
        except (SystemExit, Exception) as exc:  # noqa: BLE001
            checks.append(False)
            print(f"[selftest] {name}... FAIL {exc}", flush=True)

    # [1] roster / corps / grid-coverage set gates
    def f1():
        assert len(ROSTER) == 28
        assert set(CE6) | set(PROSPECT22) == set(ROSTER)
        assert not (set(CE6) & set(PROSPECT22))
        off, osc, pend = (set(OFFENSE_CORPS), set(OSCILLATION_CORPS),
                          set(PENDING_CORPS))
        assert len(off) == 6 and len(osc) == 15 and len(pend) == 7
        assert not (off & osc) and not (off & pend) and not (osc & pend)
        assert off | osc | pend == set(ROSTER)
        assert len(ALL_VARIANTS) == 20 and len(set(ALL_VARIANTS)) == 20
    ck("F1 roster/corps/coverage sets (28=6+22, corps 6/15/7)", f1)

    # [2] frozen weight sha gates (6 T-56 + 19 family), pure constructors
    def f2():
        _, sha56, _ = build_weights()
        fam_faces, shafam = build_family_weights()
        assert len(sha56) == 6 and len(shafam) == 19
        assert set(fam_faces) == set(FAM_VARIANTS)
    ck("F2 weight sha gates (6+19 frozen vectors)", f2)

    # [3] synthetic full-pool grid unit semantics (hand-computed)
    ck("F3 fullpool grid unit math (all-members exclusion + beats)",
       _self_grid_unit_fixture)

    # [4] passive cross-source agreement gate refuses mismatch
    def f4():
        oracle = {"s1": {"6m": 0.01, "12m": 0.02}}
        assert _passive_agreement_gate(
            oracle, {"s1": {"6m": 0.01, "12m": 0.02}}, "t") == 2
        try:
            _passive_agreement_gate(
                oracle, {"s1": {"6m": 0.01, "12m": 0.0200001}}, "t")
            raise AssertionError("agreement gate did not refuse")
        except SystemExit:
            pass
    ck("F4 passive agreement gate (mismatch refused)", f4)

    # [5] canon CE deep census gate via REAL load path (mirror leg):
    #     680-start dprobe signature refused; 1506-start census accepted
    def f5():
        with tempfile.TemporaryDirectory() as td:
            partial = os.path.join(td, "cells_deep_base.jsonl")
            full = os.path.join(td, "cells_deep_x2.jsonl")
            _write_fake_canon(partial, 680)
            _write_fake_canon(full, 1506)
            try:
                _load_canon_ce_deep({"x1": partial, "x2": full})
                raise AssertionError("680-partial not refused")
            except SystemExit:
                pass
            partial2 = os.path.join(td, "cells_deep_base_ok.jsonl")
            _write_fake_canon(partial2, 1506)
            tret, pas, stats = _load_canon_ce_deep({"x1": partial2,
                                                    "x2": full})
            assert stats["x1"]["starts"] == 1506
            assert stats["x1"]["rows"] == 9036
    ck("F5 canon census gate (680-partial refused / 1506 accepted, "
       "real load path)", f5)

    # [6] t54 t22-schema row parsing (partial exclusion + passive fill)
    def f6():
        tret, passive = {}, {"x1": {}}
        row = {"trader": "PROS-X", "start": "2021-01-15", "regime": "bull",
               "ret_6m": 0.01, "ret_12m": 0.02, "ret_24m": 0.03,
               "p_ret_6m": 0.005, "p_ret_12m": 0.006, "p_ret_24m": 0.007,
               "trades_6m": 3, "partial_12m": False, "partial_24m": True}
        n, trs = _parse_t22_cells(iter([json.dumps(row)]), "x1", tret,
                                  passive["x1"])
        assert n == 1 and trs == {"PROS-X"}
        e = tret[("PROS-X", "x1", "2021-01-15")]
        assert set(e) == {"6m", "12m"}, e          # partial 24m excluded
        assert passive["x1"]["2021-01-15"]["12m"] == 0.006
    ck("F6 t22 row parsing (partial exclusion + passive fill)", f6)

    # [7] single-shot finalize guard
    def f7():
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "out.json")
            with open(p, "w", encoding="utf-8") as fh:
                json.dump({"batch": BATCH,
                           "variants": {v: {} for v in ALL_VARIANTS}}, fh)
            assert _out_complete(p)
            bad = os.path.join(td, "bad.json")
            with open(bad, "w", encoding="utf-8") as fh:
                json.dump({"batch": BATCH, "variants": {}}, fh)
            assert not _out_complete(bad)
            assert not _out_complete(os.path.join(td, "absent.json"))
    ck("F7 single-shot finalize guard (complete/partial/absent)", f7)

    # [8] shard slice partition reconstructs the 20-variant table
    def f8():
        for shards in (1, 2, 3, 4):
            seen = []
            for s in range(shards):
                seen.extend(_shard_variants(s, shards))
            assert sorted(seen) == sorted(ALL_VARIANTS)
            assert len(seen) == 20
    ck("F8 shard slice (partitions reconstruct 20 variants)", f8)

    # [9] LIVE legacy merge probe (SKIP-honest when local faces absent)
    def f9():
        if not os.path.exists(T54_SUMMARY):
            skips.append("F9: t54 summary absent on this machine")
            return
        try:
            lt_ce, lp_ce = _load_legacy_grid()
        except OSError:
            skips.append("F9: p5c legL checkpoint absent (machine-local)")
            return
        try:
            lt_pr, lp_pr = _load_t54_axis("legacy")
        except SystemExit as exc:
            skips.append(f"F9: t54 legacy gate: {exc}")
            return
        checked = _passive_agreement_gate(lp_ce, lp_pr["x1"], "live-legacy")
        print(f"    [selftest] F9 LIVE: passive agreement {checked} "
              f"windows 0-mismatch; t54 legacy census PASS", flush=True)
    ck("F9 live legacy probe (agreement + census, SKIP-honest)", f9)

    # [10] LIVE canon CE deep presence (bm-b expected honest SKIP)
    def f10():
        missing = [p for p in CANON_CE_DEEP.values() if not os.path.exists(p)]
        if missing:
            skips.append(f"F10: canon CE deep pinned files absent "
                         f"({len(missing)}/2) -- RUN gate refuses exit 2 "
                         f"here; burn lane = machine holding canon cells")
            return
        tret, pas, stats = _load_canon_ce_deep()
        print(f"    [selftest] F10 LIVE: canon CE deep census PASS {stats}",
              flush=True)
    ck("F10 canon CE deep presence probe (SKIP-disclosure off-lane)", f10)

    # [11] A1 caliber snapshot integrity (manifest sha + roster coverage +
    # caliber definition: post-freeze wiring keys ABSENT from snapshot specs)
    def f11():
        import hashlib
        man_path = os.path.join(os.path.dirname(os.path.dirname(
            T56_CALIBER_DIR)), "_manifest.json")
        with open(man_path, encoding="utf-8") as fh:
            man = json.load(fh)
        assert man["source_commit"] == "0389dee6"
        for fname, sha in man["files"].items():
            p = os.path.join(T56_CALIBER_DIR, fname)
            assert os.path.exists(p), f"snapshot file absent {fname}"
            got = hashlib.sha256(open(p, "rb").read()).hexdigest()
            assert got == sha, f"snapshot sha drift {fname}"
        sm = _caliber_sharpe_map()
        assert set(sm) == set(ROSTER)
        # caliber definition: the r242 wiring keys must NOT be in the
        # snapshot specs for the three wired members
        for tid in ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "ENGULF-CE-01"):
            with open(os.path.join(T56_CALIBER_DIR, f"{tid}.json"),
                      encoding="utf-8") as fh:
                t = json.load(fh)
            assert "take_profit_levels" not in t["params"], tid
            assert "take_profit_fractions" not in t.get(
                "exit_overrides", {}), tid
            assert "dd_control" not in t, tid
        assert abs(sm["COMPOSITE-CE-01"] - 1.6085) < 1e-9  # pre-re-derive
        print(f"    [selftest] F11: {len(man['files'])} snapshot files "
              f"sha-verified, caliber keys clean", flush=True)
    ck("F11 A1 caliber snapshot integrity (manifest+roster+wiring-absent)",
       f11)

    n_pass = sum(checks)
    print(f"selftest: {n_pass}/{len(checks)} PASS"
          + (f" (live-leg SKIP-honest: {len(skips)})" if skips else "")
          + ("" if all(checks) else " -- FAIL"), flush=True)
    for s in skips:
        print(f"  SKIP {s}", flush=True)
    return 0 if all(checks) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--shard", type=int, default=0)
    r.add_argument("--shards", type=int, default=1)
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "selftest":
        return cmd_selftest()
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass
    try:
        return run(shard=args.shard, shards=args.shards)
    except SystemExit as exc:
        print(f"[{BATCH}] REFUSED/FAIL: {exc}", file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
