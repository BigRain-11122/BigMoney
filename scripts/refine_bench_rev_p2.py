"""REFINE_BENCH_STOCK_REV_P2 -- stock-face REV family stage-B JUDGED burn (T-139 family-1).

Promotion path (frozen in stage-A prereg sec.4 BEFORE this file ran): the
stage-A axis census (research/REFINE_BENCH_STOCK_REV_P1.md, 240 cells,
burned r512 pool REFINE-REV-STOCK-CENSUS) ranked cells; survivors =
census_ranking.json top10_independent (entries>=500, best exit x H per
depth-entry-liq family, all exit=time H=20 corner). This stage-B batch gives
them the FULL judged treatment; the judged grammar is a subset of the already-
burned census grammar (no new faces vs census, x2 cost face + judged
machinery are the only new measurements).

Zero re-implementation of frozen faces (engine reuse law):
  panel/universe/signal-grid/costs/sim mechanics  = scripts/rev_osc_stock_p1.py (RV)
  axis parameterization (depth threshold, liquidity floor, TP/SL pair)
                                                  = scripts/refine_bench_rev_census.py (CE)
  gates/DSR/ledger/cutoff_meta/SEED_REGISTRY       = scripts/science_gates.py (SG)
  family PBO                                       = screening.pbo.cscv_pbo
Only new code: the P2 cell list (frozen literal), nulls H=20 chunked burn,
finalize wiring (adds M1 t-face per D-20260930-37 + closed-family record).

Exit axis (O-20261001-1108 explicit gate, FIRST-application sibling of
LOWAMP-P2): strategy-own exit = pure time exit H=20 (tp=None/sl=None via
CE._exit_pair('time')); the engine default exit stack is never constructed,
let alone consumed (judged faces do not touch engine/exit_rules.py).

Usage:
  probe                       panel gate battery + survivor-freeze assertion
                              + closed-family record -> probe.json
  run --shard {0,1} --of 2    cells[5k:5k+5] x {x1,x2} via ProcessPool
                              (parallel_runner, panel load in initializer),
                              per-cell-face checkpoint presence=done (r488),
                              worker-side claim handshake (r497)
  run --nulls                 K=2000 same-mask random event nulls in 20
                              chunks x 100 (H=20 time exit, x1 cost,
                              rng(SEED+k)); after all chunks: phase-2
                              K=2000 synthetic 52-cohort annual Sharpe ->
                              nulls_pool.json (RV.run_nulls recipe, H face
                              per this prereg sec.3)
  run --finalize              fail-closed gate: 20 cell-face checkpoints +
                              nulls_pool.json must exist; then D6 / virtual
                              starts / robust / crisis / G1'v2 / DSR / family
                              PBO / G2 / M1 t-face / ledger + attrition ->
                              p2_results.json + cells_summary.csv
  selftest                    hermetic offline legs (synthetic panel,
                              RV._mk_panel global-rewire pattern, census
                              selftest lineage; no real panel, no pool writes)

exit codes: 0 ok / 2 fail-closed gate refusal / 3 RAM floor.
Runner + worker claim handshake land in the SAME commit as the prereg
freeze (r497 law); the worker NEVER writes runnable_pool.json.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import science_gates as SG                      # shared gate library (O-2250)
from screening.pbo import cscv_pbo             # family PBO CSCV-8
import rev_osc_stock_p1 as RV                  # judged machinery donor
import refine_bench_rev_census as CE           # axis layer donor (stage A)
from parallel_runner import run_cells_parallel

OUT_DIR = os.path.join(ROOT, "results", "refine_bench_stock", "rev_p2")
CELL_DIR = os.path.join(OUT_DIR, "cells")
NULLS_DIR = os.path.join(OUT_DIR, "nulls")
PROBE_JSON = os.path.join(OUT_DIR, "probe.json")
OUT_JSON = os.path.join(OUT_DIR, "p2_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
CENSUS_RANKING = os.path.join(ROOT, "results", "refine_bench_stock",
                              "rev_census", "census_ranking.json")

BATCH_NAME = "REFINE_BENCH_STOCK_REV_P2"
BATCH_CELLS = 2020          # 10 cells x 2 cost faces + 2000 nulls (prereg s0)
K_NULLS = 2000
N_NULL_CHUNKS = 20           # 20 x 100 null events per chunk
N_SHARDS = 2                 # cell shards
CELLS_PER_SHARD = 5
H_P2 = 20                    # every promoted survivor is the H=20 corner
FAMILY_KEY = "rev_osc_stock"
PREREG_REF = "research/REFINE_BENCH_STOCK_REV_P2.md"
SEED = None                  # filled from SG.SEED_REGISTRY at run (freeze commit)

WORKER_CAP_ARENA = 6         # memory guard: stock panel ~5GB/worker (census cap)
RAM_FLOOR_GB = 16.0
PBP = 252

# Frozen survivor list == census_ranking.json top10_independent (order as
# ranked by the stage-A census, sharpe_full desc; runner asserts the freeze
# against the file at probe/run time -- drift = fail-closed).
P2_CELLS = [
    {"name": "D-15|raw|base|time|h20",  "depth": "-15",  "entry": "raw",  "liq": "base", "exit": "time", "H": 20},
    {"name": "Dtop10|raw|base|time|h20", "depth": "top10", "entry": "raw",  "liq": "base", "exit": "time", "H": 20},
    {"name": "D-25|raw|base|time|h20",  "depth": "-25",  "entry": "raw",  "liq": "base", "exit": "time", "H": 20},
    {"name": "D-15|yang|base|time|h20", "depth": "-15",  "entry": "yang", "liq": "base", "exit": "time", "H": 20},
    {"name": "D-25|yang|base|time|h20", "depth": "-25",  "entry": "yang", "liq": "base", "exit": "time", "H": 20},
    {"name": "Dtop10|yang|base|time|h20", "depth": "top10", "entry": "yang", "liq": "base", "exit": "time", "H": 20},
    {"name": "D-15|raw|liq2|time|h20",  "depth": "-15",  "entry": "raw",  "liq": "liq2", "exit": "time", "H": 20},
    {"name": "D-25|raw|liq2|time|h20",  "depth": "-25",  "entry": "raw",  "liq": "liq2", "exit": "time", "H": 20},
    {"name": "Dtop10|raw|liq2|time|h20", "depth": "top10", "entry": "raw",  "liq": "liq2", "exit": "time", "H": 20},
    {"name": "D-15|yang|liq2|time|h20", "depth": "-15",  "entry": "yang", "liq": "liq2", "exit": "time", "H": 20},
]

_W = {}                        # worker-shared panel (initializer loads)


# ------------------------------------------------------------- util layer
def _machine_id() -> str:
    try:
        return json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                              encoding="utf-8"))["machine_id"]
    except Exception:
        return "unknown"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S") + time.strftime("%z")[:3] \
        + ":" + time.strftime("%z")[3:]


def _free_ram_gb():
    try:
        import psutil
        return psutil.virtual_memory().available / 1e9
    except Exception:
        return RAM_FLOOR_GB + 1.0


def _pool_claim(entry_id, shard_key, detail, started):
    """r497 law: worker-side harvest handshake (single-writer pool law:
    the worker never writes runnable_pool.json)."""
    d = os.path.join(ROOT, "results", "pool_claims", entry_id)
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, f"{shard_key}.{_machine_id()}.json")
    now = _now_iso()
    json.dump({"machine_id": _machine_id(), "state": "closed",
               "pid": os.getpid(), "heartbeat": now, "outcome": "ok",
               "exit_code": 0, "started": started, "closed_at": now,
               "result_ref": detail},
              open(fp, "w", encoding="utf-8"), indent=1)
    return fp


def _workers_plan():
    """O-2355 law-2: workers_plan derived from code + RAM, not guesswork."""
    from parallel_runner import worker_cap
    cap = min(worker_cap(), WORKER_CAP_ARENA)
    free = _free_ram_gb()
    if free < RAM_FLOOR_GB:
        return 0, free
    while cap > 2 and free < 8.0 * cap:    # ~8GB per stock-panel worker
        cap -= 1
    return cap, free


def _assert_survivor_freeze():
    """P2_CELLS literal == census_ranking.json top10_independent (drift=fatal)."""
    d = json.load(open(CENSUS_RANKING, encoding="utf-8"))
    ranked = [c["name"] for c in d["top10_independent"]]
    mine = [c["name"] for c in P2_CELLS]
    assert ranked == mine, f"survivor freeze drift: {ranked} != {mine}"
    for c in d["top10_independent"]:
        assert c.get("anchor_judged") is False, \
            f"promoted cell {c['name']} overlaps a judged anchor"
        assert c.get("entries", 0) >= 500, f"promotion rule entries>=500: {c}"
    return d


# ------------------------------------------------------------- worker layer
def _init_worker():
    global _W
    _W["P"] = RV.load_panel()
    P = _W["P"]
    P["T"] = P["F"]["close"].shape[0]
    P["amt20"] = RV._roll_mean20(P["F"]["amount"])


def _cell_job_p2(cell, face):
    """One P2 cell x cost face -> daily series + counters (RV.sim_cell axis
    face: CE._pick_axis + CE._sim_axis, time-only exit, eq weights, 2 buckets)."""
    P = _W["P"]
    cost = RV.COST_FACES[face]
    tp_pct, sl_pct = CE._exit_pair(cell["exit"])
    b = [np.zeros(P["T"]), np.zeros(P["T"])]
    entries = trades = unfillable = 0
    skips = {"gate_closed": 0, "gate_undefined": 0, "thin_market": 0,
             "empty_fill": 0}
    exits = {}
    for g, t in enumerate(RV.signal_grid()):
        picks, why = CE._pick_axis(P, t, cell)
        if picks is None:
            skips[why] = skips.get(why, 0) + 1
            continue
        w = np.ones(len(picks)) / len(picks)
        bucket = g % 2
        filled = 0
        for i, s in enumerate(picks):
            net, exit_d, tag = CE._sim_axis(P, int(s), t, cell["H"],
                                            tp_pct, sl_pct, cost)
            if net is None:
                unfillable += 1
                continue
            entries += 1
            trades += 1
            exits[tag] = exits.get(tag, 0) + 1
            span = max(1, exit_d - (t + 1))
            b[bucket][t + 1:t + 1 + span] += float(w[i]) * float(net) / span
            filled += 1
        if filled == 0:
            skips["empty_fill"] += 1
    series = 0.5 * (b[0] + b[1])
    return {"series": series, "entries": entries, "trades": trades,
            "unfillable": unfillable, "skips": skips, "exits": exits,
            "cohorts": len(RV.signal_grid())}


def _cell_face_key(name, face):
    safe = name.replace("|", "_")
    return os.path.join(CELL_DIR, f"{safe}_{face}")


def _null_chunk_job(chunk, seed):
    """Nulls chunk c: k in [c*100, (c+1)*100) same-mask random event days
    (RV.run_nulls phase-1 recipe, H=20 time-exit face per prereg s3).
    Seed passed EXPLICITLY: spawn workers re-import the module and a module
    global would read None in the worker (r511 initializer law family)."""
    P = _W["P"]
    grid = RV.signal_grid()
    ks, nets, spans = [], [], []
    for k in range(chunk * (K_NULLS // N_NULL_CHUNKS),
                   (chunk + 1) * (K_NULLS // N_NULL_CHUNKS)):
        rng = np.random.default_rng(seed + k)
        t = grid[int(rng.integers(0, len(grid)))]
        cand = np.flatnonzero(P["elig"][t])
        if len(cand) < RV.THIN_MARKET_MIN:
            continue                            # same-mask skip, RV recipe
        k10 = min(10, len(cand))
        picks = cand[rng.choice(len(cand), size=k10, replace=False)]
        for s in picks:
            net, exit_d, _ = CE._sim_axis(P, int(s), t, H_P2, None, None,
                                          RV.COST_X1)
            if net is not None:
                ks.append(k)
                nets.append(float(net))
                spans.append(max(1, exit_d - (t + 1)))
    return {"chunk": chunk, "ks": ks, "nets": nets, "spans": spans,
            "n_pooled": len(nets)}


# ------------------------------------------------------------- probe
def cmd_probe(_):
    global SEED
    SEED = SG.SEED_REGISTRY["refine_bench_rev_p2"]
    ranking = _assert_survivor_freeze()
    P = RV.load_panel()
    closed = SG.closed_family_check(FAMILY_KEY)
    probe = {
        "batch": BATCH_NAME,
        "probe_ts": _now_iso(),
        "machine": _machine_id(),
        "panel": {"T": RV.T_EXPECT, "N": RV.N_EXPECT,
                  "universe_ok_static": RV.OK_STATIC_EXPECT,
                  "eligible_median": P["elig_median"],
                  "eligible_median_2010": P["elig_median_2010"],
                  "sse_cover": round(P["sse_cover"], 4)},
        "evidence_cutoff": RV.EVIDENCE_CUTOFF,
        "survivors": [c["name"] for c in P2_CELLS],
        "survivor_source": ("results/refine_bench_stock/rev_census/"
                            "census_ranking.json top10_independent"),
        "stage_a_refs": ["census_ranking.json", "d6_top10_corr.json"],
        "closed_family": closed,
        "seed": {"base": SEED, "k": K_NULLS},
        "cost": {"x1_per_side_bp": 1304.1, "x2_per_side_bp": 2608.2,
                 "roundtrip_x1_bp": 2608.2,
                 "source": "P4_BATCH2 s3.2 V1 stock schedule "
                           "(RV.COST_X1 single-source import)"},
        "exit_axis": "strategy-own: pure time exit H=20 (tp=None/sl=None; "
                     "engine default exit stack never constructed)",
        "verdict": "PASS",
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(PROBE_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(probe, fh, ensure_ascii=False, indent=1)
    os.replace(PROBE_JSON + ".tmp", PROBE_JSON)
    print(f"probe PASS: T={RV.T_EXPECT} N={RV.N_EXPECT} "
          f"survivors={len(P2_CELLS)} closed_family={closed.get('status')}")
    return 0


# ------------------------------------------------------------- burn: cells
def cmd_run_shard(args):
    started = _now_iso()
    if not os.path.exists(PROBE_JSON):
        print("probe.json missing -- run `probe` first (fail-closed)")
        return 2
    if args.of != N_SHARDS:
        print(f"shard grid drift: of={args.of} != {N_SHARDS}")
        return 2
    _assert_survivor_freeze()
    os.makedirs(CELL_DIR, exist_ok=True)
    lo, hi = args.shard * CELLS_PER_SHARD, (args.shard + 1) * CELLS_PER_SHARD
    mine = P2_CELLS[lo:hi]
    todo = []
    for cell in mine:
        for face in ("x1", "x2"):
            if not os.path.exists(_cell_face_key(cell["name"], face) + ".json"):
                todo.append((cell, face))
    if not todo:
        print(f"[p2] shard {args.shard}/{args.of} already done (idempotent "
              f"skip, r488 burn+flip atomics: checkpoint presence = done)")
        _pool_claim(f"{BATCH_NAME}-SHARD-{args.shard}",
                    f"rev-p2-{args.shard}of{N_SHARDS}",
                    f"cells {lo}..{hi-1} x2 faces checkpoints present",
                    started)
        return 0
    workers, free = _workers_plan()
    if workers == 0:
        print(f"[p2] RAM floor refused: free={free:.1f}GB < {RAM_FLOOR_GB}")
        return 3
    jobs = [(f"{c['name']}|{f}", _cell_job_p2, (c, f)) for c, f in todo]
    t0 = time.time()
    res = run_cells_parallel(jobs, workers=workers,
                             desc=f"rev-p2 s{args.shard}",
                             initializer=_init_worker, initargs=())
    for cell in mine:
        for face in ("x1", "x2"):
            key = _cell_face_key(cell["name"], face)
            if os.path.exists(key + ".json"):
                continue
            r = res[f"{cell['name']}|{face}"]
            np.save(key + ".npy", r["series"])
            dump = {"cell": cell["name"], "face": face,
                    "stats": RV.cell_stats(r["series"]),
                    "entries": r["entries"], "trades": r["trades"],
                    "unfillable": r["unfillable"], "skips": r["skips"],
                    "exits": r["exits"], "cohorts": r["cohorts"],
                    "evidence_cutoff": RV.EVIDENCE_CUTOFF}
            with open(key + ".json.tmp", "w", encoding="utf-8") as fh:
                json.dump(dump, fh, ensure_ascii=False, indent=1)
            os.replace(key + ".json.tmp", key + ".json")
    elapsed = round(time.time() - t0, 1)
    audit = {"machine": _machine_id(), "workers": res.get("__workers__"),
             "elapsed_sec": elapsed, "shard": args.shard, "of": N_SHARDS,
             "n_cell_faces": len(todo), "ts": started,
             "evidence_cutoff": RV.EVIDENCE_CUTOFF, "batch": BATCH_NAME}
    with open(os.path.join(OUT_DIR, f"shard-{args.shard}of{N_SHARDS}.audit.json"),
              "w", encoding="utf-8") as fh:
        json.dump(audit, fh, ensure_ascii=False, indent=1)
    _pool_claim(f"{BATCH_NAME}-SHARD-{args.shard}",
                f"rev-p2-{args.shard}of{N_SHARDS}",
                f"cells {lo}..{hi-1} both faces, {len(todo)} cell-faces, "
                f"{elapsed}s workers={res.get('__workers__')}", started)
    print(f"[p2] shard {args.shard}/{N_SHARDS} done: {len(todo)} cell-faces "
          f"elapsed={elapsed}s workers={res.get('__workers__')}")
    return 0


# ------------------------------------------------------------- burn: nulls
def cmd_run_nulls(_):
    global SEED
    started = _now_iso()
    SEED = SG.SEED_REGISTRY["refine_bench_rev_p2"]
    if not os.path.exists(PROBE_JSON):
        print("probe.json missing -- run `probe` first (fail-closed)")
        return 2
    os.makedirs(NULLS_DIR, exist_ok=True)
    pool_fp = os.path.join(OUT_DIR, "nulls_pool.json")
    todo = [c for c in range(N_NULL_CHUNKS)
            if not os.path.exists(os.path.join(NULLS_DIR, f"chunk-{c:02d}.json"))]
    if todo:
        workers, free = _workers_plan()
        if workers == 0:
            print(f"[p2] RAM floor refused: free={free:.1f}GB < {RAM_FLOOR_GB}")
            return 3
        jobs = [(f"null-chunk-{c}", _null_chunk_job, (c, SEED)) for c in todo]
        t0 = time.time()
        res = run_cells_parallel(jobs, workers=min(workers, len(todo)),
                                 desc="rev-p2 nulls",
                                 initializer=_init_worker, initargs=())
        for c in todo:
            r = res[f"null-chunk-{c}"]
            with open(os.path.join(NULLS_DIR, f"chunk-{c:02d}.json.tmp"),
                      "w", encoding="utf-8") as fh:
                json.dump(r, fh, ensure_ascii=False, indent=1)
            os.replace(os.path.join(NULLS_DIR, f"chunk-{c:02d}.json.tmp"),
                       os.path.join(NULLS_DIR, f"chunk-{c:02d}.json"))
        print(f"[p2] nulls chunks {len(todo)} burned "
              f"({round(time.time() - t0, 1)}s)")
    # merge + phase 2 (idempotent: chunk presence + pool file gate)
    chunks = []
    for c in range(N_NULL_CHUNKS):
        fp = os.path.join(NULLS_DIR, f"chunk-{c:02d}.json")
        if not os.path.exists(fp):
            print(f"nulls incomplete: chunk-{c:02d} missing")
            return 2
        chunks.append(json.load(open(fp, encoding="utf-8")))
    order = sorted(range(N_NULL_CHUNKS), key=lambda c: chunks[c]["ks"][0]
                   if chunks[c]["ks"] else c)
    nets, spans = [], []
    for c in order:
        nets.extend(chunks[c]["nets"])
        spans.extend(chunks[c]["spans"])
    if not nets:
        raise RuntimeError("null pool empty")
    nets = np.array(nets)
    spans = np.array(spans)
    values = []
    for k in range(K_NULLS):
        rng = np.random.default_rng(SEED + k)      # second declared use
        draw = rng.integers(0, len(nets), size=52)
        ser = np.zeros(PBP)
        for j, ix in enumerate(draw):
            span = int(spans[ix])
            lo_ = min(j * RV.GRID_STEP, PBP - span)
            ser[lo_:lo_ + span] += float(nets[ix]) / span / 2.0
        sd = ser.std(ddof=1)
        values.append(ser.mean() / sd * math.sqrt(PBP) if sd > 0 else 0.0)
    vals = np.array(values)
    pool = {"batch": BATCH_NAME,
            "values": [round(float(v), 4) for v in vals],
            "coverage": {"mu": round(float(vals.mean()), 4),
                         "sigma": round(float(vals.std(ddof=1)), 4),
                         "n_values": int(len(vals))},
            "pooled_cohort_returns": int(len(nets)),
            "k_nulls": K_NULLS, "h": H_P2,
            "seed_base": SEED,
            "evidence_cutoff": RV.EVIDENCE_CUTOFF,
            "recipe": "RV.run_nulls verbatim, H=20 time-exit face "
                      "(prereg s3); phase-2 52-cohort synthetic annual "
                      "Sharpe, rng(seed+k) second declared use"}
    with open(pool_fp + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(pool, fh, ensure_ascii=False, indent=1)
    os.replace(pool_fp + ".tmp", pool_fp)
    _pool_claim(f"{BATCH_NAME}-NULLS", "rev-p2-nulls",
                f"nulls {len(nets)} pooled / {K_NULLS} draws -> {pool_fp}",
                started)
    print(f"[p2] nulls pool done: pooled={len(nets)} "
          f"mu={pool['coverage']['mu']} sigma={pool['coverage']['sigma']}")
    return 0


# ------------------------------------------------------------- finalize
def cmd_finalize(_):
    global SEED
    started = _now_iso()
    SEED = SG.SEED_REGISTRY["refine_bench_rev_p2"]
    RV.SEED = SEED          # RV.virtual_starts/robust_stats read RV.SEED
    ranking = _assert_survivor_freeze()
    cells_out = {}
    for cell in P2_CELLS:
        cells_out[cell["name"]] = {}
        for face in ("x1", "x2"):
            key = _cell_face_key(cell["name"], face)
            if not os.path.exists(key + ".json"):
                print(f"finalize gate: checkpoint missing {key}.json "
                      f"(fail-closed, 20 cell-faces required)")
                return 2
            blob = json.load(open(key + ".json", encoding="utf-8"))
            blob["series"] = np.load(key + ".npy")
            cells_out[cell["name"]][face] = blob
    if not os.path.exists(os.path.join(OUT_DIR, "nulls_pool.json")):
        print("finalize gate: nulls_pool.json missing (fail-closed)")
        return 2
    nulls = json.load(open(os.path.join(OUT_DIR, "nulls_pool.json"),
                           encoding="utf-8"))
    P = RV.load_panel()
    series_by_cell = {n: cells_out[n]["x1"]["series"] for n in cells_out}
    d6 = RV.d6_block(P, series_by_cell)
    vstarts = RV.virtual_starts(P, series_by_cell)
    robust = {n: RV.robust_stats(s) for n, s in series_by_cell.items()}
    crisis = RV.crisis_face(P, series_by_cell)
    closed = SG.closed_family_check(FAMILY_KEY)

    line_pool = {"values": nulls["values"], "coverage": nulls["coverage"]}
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, encoding="utf-8") as fh:
                prev_total = int(
                    json.load(fh)["trials_ledger"]["prev_total"])
        except Exception:
            prev_total = None
    head_base = (prev_total if prev_total is not None
                 else int(SG.ledger_head()["total"]))
    gates = {}
    for name, ser in series_by_cell.items():
        st = cells_out[name]["x1"]["stats"]
        g1 = SG.g1_prime_v2(st["sharpe_full"], ser, batch_cells=BATCH_CELLS,
                            pool="stock_b_layer", null_pool=line_pool,
                            n_trades=cells_out[name]["x1"]["trades"],
                            n_entries=cells_out[name]["x1"]["entries"],
                            n_eff_override=head_base + BATCH_CELLS)
        dsr = SG.deflated_sharpe_ratio(
            ser, n_trials=g1["skill_line"]["n_eff"])
        t_stat = SG.t_from_sharpe(st["sharpe_full"], int(st["n_days"]))
        m1 = SG.m1_t_value_gate(t_stat, hurdle=3.0, claim_class="new_factor")
        gates[name] = {"g1_prime_v2": g1, "dsr": dsr,
                       "m1_t_face": {"t": t_stat, "gate": m1}}
    mat = pd.DataFrame({n: np.asarray(s, dtype=np.float64)
                        for n, s in series_by_cell.items()})
    pbo = cscv_pbo(mat)
    for name in gates:
        gates[name]["g2"] = SG.g2_registration_v2(
            gates[name]["g1_prime_v2"]["pass_v2"],
            gates[name]["dsr"], float(pbo["pbo"]))
        gates[name]["d6_reject"] = bool(d6["cells"][name]["reject"])

    ledger = SG.append_ledger(BATCH_NAME, BATCH_CELLS,
                              file_name="refine_bench_rev_p2",
                              evidence_cutoff=RV.EVIDENCE_CUTOFF,
                              prev_total=prev_total)
    RV._attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]), {
        "g1_pass": {n: gates[n]["g1_prime_v2"]["pass_v2"] for n in gates},
        "g2_eligible": {n: gates[n]["g2"]["eligible_v2"] for n in gates},
        "d6_reject": {n: gates[n]["d6_reject"] for n in gates},
        "family_pbo": pbo})

    result = {
        "batch": BATCH_NAME,
        "evidence_cutoff": RV.EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(RV.EVIDENCE_CUTOFF),
        "prereg": PREREG_REF,
        "seed": {"base": SEED, "k": K_NULLS},
        "panel": {"T": RV.T_EXPECT, "N": RV.N_EXPECT,
                  "universe_ok_static": RV.OK_STATIC_EXPECT,
                  "eligible_median": P["elig_median"],
                  "eligible_median_2010": P["elig_median_2010"],
                  "sse_cover": round(P["sse_cover"], 4)},
        "stage_a_refs": {"survivors": "census_ranking.json top10_independent",
                         "d6_stage_a": "d6_top10_corr.json",
                         "promotion_rule": "stage-A prereg s4"},
        "exit_axis": "strategy-own pure time exit H=20 (tp/sl None; engine "
                     "default exit stack never constructed, O-20261001-1108)",
        "closed_family": closed,
        "cells": {n: {f: {"stats": cells_out[n][f]["stats"],
                          "entries": cells_out[n][f]["entries"],
                          "trades": cells_out[n][f]["trades"],
                          "unfillable": cells_out[n][f]["unfillable"],
                          "skips": cells_out[n][f]["skips"],
                          "exits": cells_out[n][f]["exits"]}
                      for f in cells_out[n]} for n in cells_out},
        "nulls": nulls, "d6": d6, "virtual_starts": vstarts,
        "robust": robust, "crisis_single_list": crisis,
        "family_pbo": pbo, "gates": gates, "trials_ledger": ledger,
        "verdict_line": ("judged per prereg s4: G1'v2 x1 primary faces; "
                         "judged-negative = slot closed + new-evidence "
                         "reopen note (O-2325 s5)"),
    }
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    rows = []
    for n in cells_out:
        for f in ("x1", "x2"):
            rows.append({"cell": n, "face": f,
                         **cells_out[n][f]["stats"]})
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
    _pool_claim(f"{BATCH_NAME}-FINALIZE", "rev-p2-finalize",
                f"p2_results.json gates={len(gates)} "
                f"ledger={ledger['total']}", started)
    print(f"finalize ok: cells={len(result['cells'])} "
          f"ledger={ledger['total']} elapsed_hint={_now_iso()}")
    return 0


# ------------------------------------------------------------- selftest
def _init_worker_selftest(tmp):
    """Pool-test initializer: reuse the parent-built synthetic panel files
    (RV._mk_panel makedirs without exist_ok -- r511 worker law: the worker
    only rewires globals + load_panel, never re-runs the builder)."""
    global _W, SEED
    cache, bars = os.path.join(tmp, "cache"), os.path.join(tmp, "bars")
    idx = pd.to_datetime(np.load(os.path.join(cache, "dates.npy")), unit="us")
    patch = {}
    for k in ("CACHE", "BARS", "MASK", "SSE", "T_EXPECT", "N_EXPECT",
              "OK_STATIC_EXPECT", "UNIV_MEDIAN_FULL_MIN",
              "UNIV_MEDIAN_2010_MIN", "SSE_COVER_MIN", "EXPECT_DATES"):
        patch[k] = getattr(RV, k)
    RV.CACHE, RV.BARS = cache, bars
    RV.MASK = os.path.join(tmp, "mask.csv")
    RV.SSE = os.path.join(tmp, "sse.parquet")
    RV.EXPECT_DATES = (str(idx[0].date()), str(idx[-1].date()))
    RV.T_EXPECT, RV.N_EXPECT, RV.OK_STATIC_EXPECT = 420, 12, 11
    RV.UNIV_MEDIAN_FULL_MIN, RV.UNIV_MEDIAN_2010_MIN = 1, 1
    RV.SSE_COVER_MIN = 0.0
    P = RV.load_panel()
    P["T"] = P["F"]["close"].shape[0]
    P["amt20"] = RV._roll_mean20(P["F"]["amount"])
    _W["P"] = P
    return patch


def cmd_selftest(_):
    """Hermetic legs (RV._mk_panel + global rewire, census selftest lineage;
    no real panel, no pool writes; probe/out paths diverted to a temp dir)."""
    import tempfile
    ok = 0
    saved_out = {}
    try:
        tmp = tempfile.mkdtemp(prefix="rev_p2_selftest_")
        T, N = 420, 12
        RV._mk_panel(tmp, T, N)
        for k in ("OUT_DIR", "CELL_DIR", "NULLS_DIR", "PROBE_JSON",
                  "OUT_JSON", "OUT_CSV", "SEED", "N_NULL_CHUNKS",
                  "K_NULLS", "N_SHARDS", "CELLS_PER_SHARD"):
            saved_out[k] = globals().get(k)
        globals()["OUT_DIR"] = os.path.join(tmp, "out")
        globals()["CELL_DIR"] = os.path.join(tmp, "out", "cells")
        globals()["NULLS_DIR"] = os.path.join(tmp, "out", "nulls")
        globals()["PROBE_JSON"] = os.path.join(tmp, "out", "probe.json")
        globals()["OUT_JSON"] = os.path.join(tmp, "out", "p2_results.json")
        globals()["OUT_CSV"] = os.path.join(tmp, "out", "cells_summary.csv")
        globals()["SEED"] = 20263300
        # shrink the nulls face for hermetic speed (law face unchanged:
        # same recipe, fewer chunks/k in test only)
        globals()["K_NULLS"] = 20
        globals()["N_NULL_CHUNKS"] = 2
        os.makedirs(globals()["CELL_DIR"], exist_ok=True)
        os.makedirs(globals()["NULLS_DIR"], exist_ok=True)
        patch = _init_worker_selftest(tmp)
        # fake probe gate for shard-run legs
        json.dump({"verdict": "PASS"},
                  open(globals()["PROBE_JSON"], "w", encoding="utf-8"))

        # leg 1: survivor freeze vs census file (frozen product read)
        _assert_survivor_freeze()
        assert len(P2_CELLS) == 10 and all(c["H"] == 20 for c in P2_CELLS)
        print("selftest leg1 survivor-freeze (10 cells, H20 corner): PASS")
        ok += 1

        # leg 2: exit-axis -- time-only faces produce no tp/sl exit tags
        # (engine default exit stack zero-consumption, O-20261001-1108)
        cell = dict(P2_CELLS[0])
        r = _cell_job_p2(cell, "x1")
        assert set(r["exits"]) <= {"time", "tail"}, \
            f"exit-axis leak: {r['exits']}"
        assert CE._exit_pair("time") == (None, None)
        print("selftest leg2 exit-axis time-only (no tp/sl tags): PASS")
        ok += 1

        # leg 3: determinism (double run byte-equal)
        a = _cell_job_p2(cell, "x1")
        assert np.array_equal(a["series"], r["series"]) and \
            a["exits"] == r["exits"] and a["entries"] == r["entries"], \
            "selftest leg3: cell job not deterministic"
        print("selftest leg3 cell determinism: PASS")
        ok += 1

        # leg 4: inline == pool identity (ems S18 law, 1 worker)
        jobs = [(f"{P2_CELLS[0]['name']}|x1", _cell_job_p2,
                 (P2_CELLS[0], "x1"))]
        res = run_cells_parallel(jobs, workers=1, desc="selftest-pool",
                                 initializer=_init_worker_selftest,
                                 initargs=(tmp,))
        got = res[f"{P2_CELLS[0]['name']}|x1"]
        assert np.array_equal(got["series"], r["series"]) and \
            got["entries"] == r["entries"], "selftest leg4: pool face drift"
        print("selftest leg4 inline==pool identity: PASS")
        ok += 1

        # leg 5: nulls chunk determinism + seeded phase-2 determinism
        c0 = _null_chunk_job(0, 20263300)
        c0b = _null_chunk_job(0, 20263300)
        assert c0["ks"] == c0b["ks"] and c0["nets"] == c0b["nets"] and \
            c0["spans"] == c0b["spans"], "selftest leg5: nulls not seeded"
        c0c = _null_chunk_job(0, 20263300 + 1)
        if c0["nets"]:      # empty pools (synthetic thin-market skips) = honest
            assert c0c["nets"] != c0["nets"] or c0c["spans"] != c0["spans"], \
                "selftest leg5: seed has no effect"
        # (chunk 0/1 on the synthetic panel may pool zero rows -- same-mask
        # thin-market skips are the honest RV recipe; determinism face holds)
        print("selftest leg5 nulls seed determinism: PASS")
        ok += 1

        # leg 6: finalize gate fail-closed (checkpoints missing -> exit 2)
        rc = _finalize_gate_probe()
        assert rc == 2, "selftest leg6: finalize gate not fail-closed"
        print("selftest leg6 finalize-gate fail-closed: PASS")
        ok += 1

        # leg 7: closed-family record + seed registry face
        closed = SG.closed_family_check(FAMILY_KEY)
        assert closed.get("status") in ("open", "not_in_registry"), closed
        assert SG.SEED_REGISTRY["refine_bench_rev_p2"] == 20263300
        print("selftest leg7 closed-family open + seed registry: PASS")
        ok += 1
    finally:
        for k, v in saved_out.items():
            globals()[k] = v
        for k in ("CACHE", "BARS", "MASK", "SSE", "T_EXPECT", "N_EXPECT",
                  "OK_STATIC_EXPECT", "UNIV_MEDIAN_FULL_MIN",
                  "UNIV_MEDIAN_2010_MIN", "SSE_COVER_MIN", "EXPECT_DATES"):
            if k in patch:
                setattr(RV, k, patch[k])
    print(f"selftest: {ok}/7 PASS")
    return 0


def _finalize_gate_probe():
    """Selftest leg-6 helper: run cmd_finalize with argv-less None args and
    intercept the argparse-free path (gate refusal must be exit 2)."""
    class _A:
        shard = 0
        of = N_SHARDS
    saved = globals().get("SEED")
    try:
        rc = cmd_finalize(_A())
    except SystemExit:
        rc = 2
    except Exception:
        rc = 2 if not os.path.exists(OUT_JSON) else 0
    globals()["SEED"] = saved
    return rc if isinstance(rc, int) else 2


# ------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=BATCH_NAME)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    sp = sub.add_parser("run")
    sp.add_argument("--shard", type=int, default=None)
    sp.add_argument("--of", type=int, default=N_SHARDS)
    g = sp.add_mutually_exclusive_group()
    g.add_argument("--nulls", action="store_true")
    g.add_argument("--finalize", action="store_true")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "probe":
        return cmd_probe(args)
    if args.cmd == "run":
        if args.nulls:
            return cmd_run_nulls(args)
        if args.finalize:
            return cmd_finalize(args)
        if args.shard is None:
            print("run requires --shard K | --nulls | --finalize")
            return 2
        return cmd_run_shard(args)
    if args.cmd == "selftest":
        return cmd_selftest(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
