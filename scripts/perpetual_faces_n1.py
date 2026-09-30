"""PERPETUAL_FACES N1 wave-2 runner -- T-133 s2 (CEO O-2026-09-30-2340).

Law: research/PERPETUAL_FACES.md v1.0 sec.2/sec.4 (FROZEN bm-b r484).
Wave prereg: research/PERPETUAL_N1_W2_PREREG.md (wave-level frozen
pre-run, R99; bands = law sec.4 ledger W2 rows verbatim, R250 one-step).

Design = frozen v1 null calibration VERBATIM via import-face reuse:
  engine      = p2_null_calibration.run_one (same-source, no re-impl)
  assembly    = p2_null_calibration_ext._assemble / _entry_matrix / p_for
  slice law   = contiguous shard slicing, zero gap/overlap (ext pattern)
  determinism = same seed -> byte-equal rerun (shard file = checkpoint)

W2 bands (law sec.4):
  family A: j = 0..1999, entry seed = 12_100 + j  (random entry, engine exit)
  family B: j = 0..199,  entry seed = 12_100 + j (paired with A[j]),
                            exit seed = 21_100 + j (random exit, p=0.05)

Subcommands:
  run --shard i --of N [--workers W]  burn shard i of N (also accepts --nshards),
                         writes results/p2cal_ext/n1_w2/shard-<i>-of-<N>.json
                         --workers W: process-pool size (default: full cores,
                         O-2026-09-30-2355 multicore law + O-20260930-1858
                         holiday full-core mobilization; BLAS capped 1/worker)
  finalize               FAIL-CLOSED merge of all shards -> cumulative null
                         pool (canon 120 + W1 ext 2200 + W2 2200 = 4520),
                         skill_line_v2 K-lift at same n_eff (v2 attribution
                         law), ledger +2200, writes
                         results/perpetual_faces/n1_w2_results.json
  probe                  2-run end-to-end design probe at out-of-band seeds
                         95_002/95_003 (ledger +0)
  parity                 serial-vs-pool byte-equality check on real wave
                         j-slice (O-2355 conversion verification face;
                         ledger +0; writes _n1_w2_parity.json)
  status                 shard inventory + finalize state (read-only)
  selftest               offline hermetic checks (no network, no engine)
"""
import glob
import json
import multiprocessing
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402  (engine deps, kept for import-face parity)

from config import PATHS  # noqa: E402
import science_gates as sg  # noqa: E402
import p2_null_calibration as v1  # noqa: E402
import p2_null_calibration_ext as ext  # noqa: E402

BATCH = "PERPETUAL-N1-W2"
WAVE = 2
LAW_REF = "research/PERPETUAL_FACES.md v1.0 sec.4 (T-133 s2, O-2026-09-30-2340)"
PREREG = ("research/PERPETUAL_N1_W2_PREREG.md (wave-level frozen pre-run; "
          "design = frozen v1 null calibration verbatim, new seed bands only)")
CUTOFF = ext.CUTOFF                      # 2026-09-22 same-window law
A_N = 2000
B_N = 200
A_SEED_BASE = 12_100                    # law sec.4: 12_100..14_099
B_EXIT_SEED_BASE = 21_100               # law sec.4: 21_100..21_299
PROBE_ENTRY_SEED = 95_002               # out-of-band (design probe only)
PROBE_EXIT_SEED = 95_003
SHARD_DIR = os.path.join(PATHS.results_dir, "p2cal_ext", "n1_w2")
OUT_DIR = os.path.join(PATHS.results_dir, "perpetual_faces")
OUT = os.path.join(OUT_DIR, "n1_w2_results.json")
PROBE_OUT = os.path.join(OUT_DIR, "_n1_w2_probe.json")
W1_EXT_OUT = os.path.join(PATHS.results_dir, "p2_calibration_v2_ext.json")


def p_for(j: int) -> float:
    """50-seed block alternation, v1 pattern continuation (import-face)."""
    return ext.p_for(j)


# --- O-2026-09-30-2355 multicore law: single body, two drivers (serial/pool) ---
_CTX = None        # per-process assembled engine context (spawn-safe global)


def _worker_init():
    global _CTX
    v1m, prices, idx, closes, cost_rate = ext._assemble()
    _CTX = (prices, idx, closes, closes.shape[0], closes.shape[1],
            list(closes.columns))


def _run_a(j: int) -> dict:
    prices, idx, closes, n_days, n_syms, cols = _CTX
    p = p_for(j)
    rng = np.random.default_rng(A_SEED_BASE + j)
    entry = ext._entry_matrix(rng, n_days, n_syms, idx, cols, p)
    exit_ = pd.DataFrame(False, index=idx, columns=cols)
    r = v1.run_one(prices, idx, entry, exit_, {}, f"w2A_p{p}_j{j}")
    return {**r, "p": p, "seed_rng": A_SEED_BASE + j,
            "note": f"w2 random entry p={p} rng={A_SEED_BASE + j}; "
                    f"exits=engine rules (v1 design verbatim)"}


def _run_b(j: int) -> dict:
    prices, idx, closes, n_days, n_syms, cols = _CTX
    p = p_for(j)
    rng = np.random.default_rng(A_SEED_BASE + j)      # SAME matrix as A[j]
    entry = ext._entry_matrix(rng, n_days, n_syms, idx, cols, p)
    rng_x = np.random.default_rng(B_EXIT_SEED_BASE + j)
    exit_ = pd.DataFrame((rng_x.random((n_days, n_syms)) < v1.P_EXIT),
                         index=idx, columns=cols)
    r = v1.run_one(prices, idx, entry, exit_, {}, f"w2B_p{p}_j{j}")
    return {**r, "p": p, "seed_rng_entry": A_SEED_BASE + j,
            "seed_rng_exit": B_EXIT_SEED_BASE + j,
            "note": f"w2 random entry rng={A_SEED_BASE + j} "
                    f"(paired with w2A_j{j}) + random exit "
                    f"rng={B_EXIT_SEED_BASE + j} p={v1.P_EXIT}"}


def _resolve_workers(argv) -> int:
    """O-2355: workers_plan from declaration to code. Default = full cores
    (O-20260930-1858 holiday full-core mobilization), BLAS capped 1/worker
    so the pool does not oversubscribe."""
    if "--workers" in argv:
        w = int(argv[argv.index("--workers") + 1])
        assert w >= 1, "workers must be >= 1"
        return w
    return max(1, multiprocessing.cpu_count())


def _cap_blas_threads():
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS"):
        os.environ.setdefault(var, "1")


def run_shard(shard: int, nshards: int, workers: int = 1) -> int:
    a_lo, a_hi = shard * A_N // nshards, (shard + 1) * A_N // nshards
    b_lo, b_hi = shard * B_N // nshards, (shard + 1) * B_N // nshards
    t0 = time.time()

    if workers > 1:
        _cap_blas_threads()
        with ProcessPoolExecutor(max_workers=workers,
                                  initializer=_worker_init) as ex:
            fam_a = list(ex.map(_run_a, range(a_lo, a_hi)))
            fam_b = list(ex.map(_run_b, range(b_lo, b_hi)))
    else:
        _worker_init()                       # in-process ctx, serial driver
        fam_a = [_run_a(j) for j in range(a_lo, a_hi)]
        fam_b = [_run_b(j) for j in range(b_lo, b_hi)]
    print(f"  A[{a_lo}..{a_hi}) + B[{b_lo}..{b_hi}) done "
          f"({len(fam_a)}+{len(fam_b)} runs, {time.time()-t0:.0f}s, "
          f"workers={workers})", flush=True)

    os.makedirs(SHARD_DIR, exist_ok=True)
    out = {
        "batch": BATCH,
        "preregistered_doc": PREREG,
        "law_ref": LAW_REF,
        "evidence_cutoff": CUTOFF,
        "shard": shard, "nshards": nshards,
        "a_range": [a_lo, a_hi], "b_range": [b_lo, b_hi],
        "families": {"A_random_engine_exit": {"n": len(fam_a), "runs": fam_a},
                     "B_random_entry_random_exit": {"n": len(fam_b), "runs": fam_b}},
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": len(fam_a) + len(fam_b),
                  "workers": workers,
                  "cpu_parallel": ("multiprocess (ProcessPoolExecutor, "
                                    f"{workers} workers, O-2355)"
                                    if workers > 1 else
                                    "serial (single-process)"),
                  "machine": json.loads(open(
                      os.path.join(PATHS.root, "fleet", "machine.json"),
                      encoding="utf-8").read()).get("machine_id", "unknown")},
    }
    path = os.path.join(SHARD_DIR, f"shard-{shard}-of-{nshards}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, default=str)
    print(f"saved: {path} ({out['audit']['elapsed_sec']}s, "
          f"{out['audit']['n_backtests']} runs)")
    return 0


def _w1_values():
    """W1 ext run sharpes (cumulative-pool dependency, in-repo committed)."""
    d = json.load(open(W1_EXT_OUT, encoding="utf-8"))
    fams = d.get("families") or {}
    a = (fams.get("A_random_engine_exit") or {}).get("runs") or []
    b = (fams.get("B_random_entry_random_exit") or {}).get("runs") or []
    vals = [float(r["full"]["sharpe"]) for r in a + b]
    assert len(vals) == ext.A_EXT_N + ext.B_EXT_N, \
        f"W1 ext file incomplete: {len(vals)} != 2200 (FAIL-CLOSED)"
    return vals


def finalize() -> int:
    shard_files = sorted(glob.glob(os.path.join(
        SHARD_DIR, "shard-*-of-*.json")))
    if not shard_files:
        print("finalize: FAIL-CLOSED -- no shard files under "
              "results/p2cal_ext/n1_w2/")
        return 2
    a_runs, b_runs, nshards_seen = [], [], set()
    for sf in shard_files:
        d = json.load(open(sf, encoding="utf-8"))
        fams = d.get("families") or {}
        a_runs += (fams.get("A_random_engine_exit") or {}).get("runs") or []
        b_runs += (fams.get("B_random_entry_random_exit") or {}).get("runs") or []
        nshards_seen.add(d.get("nshards"))
    if len(nshards_seen) != 1 or None in nshards_seen:
        print(f"finalize: FAIL-CLOSED -- mixed nshards {sorted(nshards_seen)}")
        return 2
    nshards = nshards_seen.pop()
    done = {json.load(open(sf, encoding="utf-8"))["shard"] for sf in shard_files}
    if done != set(range(nshards)):
        print(f"finalize: FAIL-CLOSED -- shards {sorted(done)} != "
              f"0..{nshards-1} (burn not complete)")
        return 2
    if len(a_runs) != A_N or len(b_runs) != B_N:
        print(f"finalize: FAIL-CLOSED -- A {len(a_runs)} != {A_N} or "
              f"B {len(b_runs)} != {B_N} (slice overlap/gap)")
        return 2
    if len({r["name"] for r in a_runs}) != A_N or \
       len({r["name"] for r in b_runs}) != B_N:
        print("finalize: FAIL-CLOSED -- duplicate run names")
        return 2

    canon_pool = sg.null_sharpes()               # canon 120, untouched
    canon_cov = canon_pool["coverage"]
    w1_vals = _w1_values()
    w2_vals = [float(r["full"]["sharpe"]) for r in a_runs + b_runs]
    pre_values = list(canon_pool["values"]) + w1_vals       # 2,320
    merged_values = pre_values + w2_vals                   # 4,520

    def cov(vals, schema):
        return {"n_values": len(vals), "schemas_parsed": [schema],
                "known_unparsed": [], "mu": sum(vals) / len(vals),
                "sigma": sg._pstdev(vals)}

    cov_pre = cov(pre_values, "canon 120 + W1 ext 2200 (pre-W2 cumulative)")
    cov_w2 = cov(w2_vals, "n1_w2 shard merge: families[*].runs[].full.sharpe")
    cov_mrg = cov(merged_values, "canon 120 + W1 ext 2200 + W2 2200")

    # K-lift at the SAME n_eff on both sides (v2 attribution law verbatim)
    line_old = sg.skill_line_v2(batch_cells=0,
                                null_pool={"values": pre_values,
                                           "coverage": cov_pre})
    line_new = sg.skill_line_v2(batch_cells=0,
                                null_pool={"values": merged_values,
                                           "coverage": cov_mrg})

    led = sg.append_ledger(BATCH, A_N + B_N, "perpetual_faces/n1_w2_results.json",
                           note="perpetual N1 nulls-deepening wave 2 (law "
                                "PERPETUAL_FACES v1.0 sec.4): 2,200 new-seed "
                                "null trials, frozen v1 design, window "
                                "2026-09-22",
                           evidence_cutoff=CUTOFF)

    a_full = [float(r["full"]["sharpe"]) for r in a_runs]
    out = {
        "batch": BATCH,
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": PREREG,
        "law_ref": LAW_REF,
        "evidence_cutoff": CUTOFF,
        "science_gates": {"cutoff_meta": {"evidence_cutoff": CUTOFF,
                                          "source": "frozen v1/v2 canon "
                                                    "window (same-window law)"},
                          "ledger": led},
        "universe": {"pool": "core48-bare-codes", "n_syms": 48,
                     "history": f"2020-01-02 .. {CUTOFF} (hard truncation)"},
        "families": {
            "A_random_engine_exit": {
                "n": A_N,
                "full_sharpe_p95": round(float(np.percentile(a_full, 95)), 4),
                "full_sharpe_p99": round(float(np.percentile(a_full, 99)), 4),
                "full_sharpe_mu": round(sum(a_full) / len(a_full), 6),
                "runs": a_runs},
            "B_random_entry_random_exit": {"n": B_N, "runs": b_runs},
        },
        "null_pool_cumulative": {
            "canon": {"n_values": canon_cov["n_values"], "mu": canon_cov["mu"],
                      "sigma": canon_cov["sigma"]},
            "pre_w2_cumulative": {"n_values": cov_pre["n_values"],
                                  "mu": cov_pre["mu"],
                                  "sigma": cov_pre["sigma"]},
            "w2_only": {"n_values": cov_w2["n_values"], "mu": cov_w2["mu"],
                        "sigma": cov_w2["sigma"]},
            "merged": {"n_values": cov_mrg["n_values"], "mu": cov_mrg["mu"],
                       "sigma": cov_mrg["sigma"]},
            "mu_delta_w2_vs_w1ext": None,  # filled below from W1 file
            "se_mu_at_k4520": round(cov_mrg["sigma"] / (cov_mrg["n_values"] ** 0.5), 6),
        },
        "skill_line_v2_k_lift": {
            "n_eff_held_equal": line_old["n_eff"],
            "line_pre_w2": line_old["line"],
            "line_merged_4520": line_new["line"],
            "line_delta_k_lift": round(line_new["line"] - line_old["line"], 4),
            "passive_term": line_new.get("passive"),
            "formula": "max(passive+0.10, mu + sigma*sqrt(2*ln N_eff))",
            "canon_flip": "NOT performed by this wave -- governance proposal "
                          "face only (K2200 same law)",
        },
        "shards_consumed": [os.path.basename(s) for s in shard_files],
        "audit": {"machine": json.loads(open(
            os.path.join(PATHS.root, "fleet", "machine.json"),
            encoding="utf-8").read()).get("machine_id", "unknown"),
            "finalize_only": True},
    }
    w1d = json.load(open(W1_EXT_OUT, encoding="utf-8"))
    w1_ext_cov = (w1d.get("null_pool_old_vs_new") or {}).get("ext_only") or {}
    if w1_ext_cov.get("mu") is not None:
        out["null_pool_cumulative"]["mu_delta_w2_vs_w1ext"] = round(
            cov_w2["mu"] - w1_ext_cov["mu"], 6)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, default=str)
    print(f"pre-W2  mu={cov_pre['mu']:.4f} sigma={cov_pre['sigma']:.4f} "
          f"(K={cov_pre['n_values']})")
    print(f"w2      mu={cov_w2['mu']:.4f} sigma={cov_w2['sigma']:.4f} "
          f"(K={cov_w2['n_values']})")
    print(f"merged  mu={cov_mrg['mu']:.4f} sigma={cov_mrg['sigma']:.4f} "
          f"(K={cov_mrg['n_values']})")
    print(f"skill_line_v2 @n_eff={line_old['n_eff']}: {line_old['line']} -> "
          f"{line_new['line']} (K-lift delta "
          f"{line_new['line']-line_old['line']:+.4f})")
    print(f"ledger: {led}")
    print(f"saved: {OUT}")
    return 0


def probe() -> int:
    """2-run end-to-end design probe at out-of-band seeds. Ledger +0."""
    v1m, prices, idx, closes, cost_rate = ext._assemble()
    n_days, n_syms = closes.shape
    cols = list(closes.columns)
    t0 = time.time()
    runs = []
    for name, seed, p, with_exit in (
            ("probeA", PROBE_ENTRY_SEED, v1.BASELINE_P[0], False),
            ("probeB", PROBE_EXIT_SEED, v1.BASELINE_P[1], True)):
        rng = np.random.default_rng(seed)
        entry = ext._entry_matrix(rng, n_days, n_syms, idx, cols, p)
        if with_exit:
            rng_x = np.random.default_rng(PROBE_EXIT_SEED)
            exit_ = pd.DataFrame((rng_x.random((n_days, n_syms)) < v1.P_EXIT),
                                 index=idx, columns=cols)
        else:
            exit_ = pd.DataFrame(False, index=idx, columns=cols)
        r = v1.run_one(prices, idx, entry, exit_, {}, name)
        runs.append({**r, "p": p, "seed_rng": seed, "random_exit": with_exit})
        print(f"  {name} full_s={r['full']['sharpe']:>7.3f} "
              f"n_trades={r['n_trades']}")
    rng = np.random.default_rng(PROBE_ENTRY_SEED)
    m1 = (rng.random((3, 3)) < 0.5).astype(int)
    rng = np.random.default_rng(PROBE_ENTRY_SEED)
    m2 = (rng.random((3, 3)) < 0.5).astype(int)
    assert (m1 == m2).all(), "probe seed drift"
    out = {"batch": BATCH + "-probe", "evidence_cutoff": CUTOFF,
           "note": "design verification only, out-of-band seeds 95_002/95_003; "
                  "NOT batch trials; ledger +0",
           "universe_syms": n_syms, "panel_end": str(idx[-1].date()),
           "runs": runs, "elapsed_sec": round(time.time() - t0, 1)}
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(PROBE_OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, default=str)
    print(f"saved: {PROBE_OUT} ({out['elapsed_sec']}s)")
    return 0


def parity() -> int:
    """O-2355 conversion verification: serial vs process-pool byte-equality
    on a real wave j-slice. Ledger +0 (same wave j's, re-burned identically
    inside their shards; evidence file out-of-band, finalize ignores it)."""
    _cap_blas_threads()
    a_js = [0, 1, 2, 3]
    b_js = [0, 1]
    t0 = time.time()
    _worker_init()
    ser_a = [_run_a(j) for j in a_js]
    ser_b = [_run_b(j) for j in b_js]
    with ProcessPoolExecutor(max_workers=4, initializer=_worker_init) as ex:
        par_a = list(ex.map(_run_a, a_js))
        par_b = list(ex.map(_run_b, b_js))

    def canon(rs):
        return [json.dumps(x, sort_keys=True, default=str) for x in rs]

    ok_a = canon(ser_a) == canon(par_a)
    ok_b = canon(ser_b) == canon(par_b)
    ok = ok_a and ok_b
    out = {"batch": BATCH + "-parity", "evidence_cutoff": CUTOFF,
           "law_ref": "O-2026-09-30-2355 (conversion verified: pool output "
                      "byte-equal to serial on wave j-slice)",
           "note": "design/engine verification only; NOT batch trials; "
                   "ledger +0; j's belong to the wave itself",
           "a_slice": a_js, "b_slice": b_js,
           "byte_equal": {"A": ok_a, "B": ok_b},
           "elapsed_sec": round(time.time() - t0, 1)}
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "_n1_w2_parity.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, default=str, indent=2)
    print(f"parity: A={ok_a} B={ok_b} -> "
          f"{'PASS' if ok else 'FAIL'} ({out['elapsed_sec']}s)")
    return 0 if ok else 2


def status() -> int:
    nshards = 12
    present = sorted(int(os.path.basename(p).split("-")[1])
                     for p in glob.glob(os.path.join(
                         SHARD_DIR, f"shard-*-of-{nshards}.json")))
    print(f"batch: {BATCH} (law wave {WAVE}, nshards={nshards})")
    print(f"shards present: {len(present)}/{nshards} {present}")
    print(f"finalize output exists: {os.path.exists(OUT)}")
    return 0


def selftest() -> int:
    # 1. frozen v1 design constants inherited verbatim (import-face)
    assert v1.N_BASELINES == 100 and v1.N_PAIRED == 20
    assert v1.BASELINE_P == [0.02, 0.05] and v1.P_EXIT == 0.05
    assert CUTOFF == "2026-09-22" and CUTOFF == ext.CUTOFF
    # 2. seed bands: W2 vs v1 in-use / W1 ext / SEED_REGISTRY / law W3-W4
    w2_a = {A_SEED_BASE + j for j in range(A_N)}
    w2_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
    v1_a = {10_000 + k for k in range(v1.N_BASELINES)}
    v1_b = {20_000 + k for k in range(v1.N_PAIRED)}
    w1_a = {ext.A_SEED_BASE + j for j in range(ext.A_EXT_N)}
    w1_b = {ext.B_EXIT_SEED_BASE + j for j in range(ext.B_EXT_N)}
    reg = sg.SEED_REGISTRY
    reg_ints = {v for v in reg.values() if isinstance(v, (int, float))}
    assert not (w2_a & w2_b), "W2 A/B band overlap"
    for nm, band in (("A", w2_a), ("B", w2_b)):
        assert not (band & v1_a) and not (band & v1_b), f"W2 {nm} hits v1 band"
        assert not (band & w1_a) and not (band & w1_b), f"W2 {nm} hits W1 ext"
        assert not (band & reg_ints), f"W2 {nm} hits SEED_REGISTRY"
    import perpetual_faces as pf
    law_w2 = pf.N1_BANDS[2]
    assert law_w2["a"] == (A_SEED_BASE, A_SEED_BASE + A_N - 1), "law band A drift"
    assert law_w2["b_exit"] == (B_EXIT_SEED_BASE, B_EXIT_SEED_BASE + B_N - 1), \
        "law band B drift"
    for w, b in pf.N1_BANDS.items():
        if w == WAVE:
            continue
        la = set(range(b["a"][0], b["a"][1] + 1))
        lb = set(range(b["b_exit"][0], b["b_exit"][1] + 1))
        assert not (w2_a & la) and not (w2_b & lb), f"W2 hits law W{w} band"
    # probe seeds: out-of-band, disjoint from everything + W1 probes
    probes = {PROBE_ENTRY_SEED, PROBE_EXIT_SEED,
              ext.PROBE_ENTRY_SEED, ext.PROBE_EXIT_SEED}
    assert len(probes) == 4, "probe seed collision with W1 probes"
    assert not (probes & reg_ints), "probe seed in SEED_REGISTRY"
    assert not (probes & (w2_a | w2_b | v1_a | v1_b | w1_a | w1_b)), \
        "probe seed inside a batch band"
    # 3. p block pattern continuation (v1 verbatim)
    assert [p_for(j) for j in (0, 49, 50, 99, 100, 149, 150)] == \
        [0.02, 0.02, 0.05, 0.05, 0.02, 0.02, 0.05]
    # 4. determinism
    rng = np.random.default_rng(A_SEED_BASE + 0)
    m1 = (rng.random((3, 2)) < 0.5).astype(int)
    rng = np.random.default_rng(A_SEED_BASE + 0)
    m2 = (rng.random((3, 2)) < 0.5).astype(int)
    assert (m1 == m2).all(), "seed drift"
    # 5. shard slice math: contiguous, no gap/overlap, totals exact
    for nshards in (1, 2, 4, 12):
        a_ranges = [(i * A_N // nshards, (i + 1) * A_N // nshards)
                    for i in range(nshards)]
        assert a_ranges[0][0] == 0 and a_ranges[-1][1] == A_N
        for (lo1, hi1), (lo2, hi2) in zip(a_ranges, a_ranges[1:]):
            assert hi1 == lo2, "A slice gap/overlap"
        b_ranges = [(i * B_N // nshards, (i + 1) * B_N // nshards)
                    for i in range(nshards)]
        assert b_ranges[0][0] == 0 and b_ranges[-1][1] == B_N
        for (lo1, hi1), (lo2, hi2) in zip(b_ranges, b_ranges[1:]):
            assert hi1 == lo2, "B slice gap/overlap"
    # 6. canon intact (shape only, no mutation)
    canon = json.load(open(os.path.join(PATHS.results_dir,
                                        "p2_calibration.json"), encoding="utf-8"))
    assert canon["universe"]["n_syms"] == 48
    assert canon["universe"]["history"].endswith(CUTOFF)
    cov = sg.null_sharpes()["coverage"]
    assert cov["n_values"] == 120 and cov["mu"] is not None
    # 7. W1 ext dependency present + complete (finalize cumulative base)
    assert os.path.exists(W1_EXT_OUT), "W1 ext output missing (finalize dep)"
    vals = _w1_values()
    assert len(vals) == 2200
    # 8. output path safety: never writes canon or W1 files
    for forbidden in (os.path.join(PATHS.results_dir, "p2_calibration.json"),
                     os.path.join(PATHS.results_dir, "p2_calibration_v2.json"),
                     W1_EXT_OUT, ext.EXT_OUT):
        assert os.path.abspath(OUT) != os.path.abspath(forbidden), \
            "output path collides with canon/W1 file"
    assert os.path.abspath(SHARD_DIR) != os.path.abspath(ext.SHARD_DIR), \
        "shard dir collides with W1 shard dir"
    # 9. O-2026-09-30-2355 multicore law: workers_plan is code, not declaration
    import pickle
    for fn in (_worker_init, _run_a, _run_b):
        pickle.dumps(fn)                      # spawn-picklable top-level fns
    default_w = _resolve_workers([])
    assert default_w >= 1
    if multiprocessing.cpu_count() >= 2:
        assert default_w >= 2, \
            "O-2355: pool runner default must be multiprocess on multi-core"
    assert _resolve_workers(["--workers", "3"]) == 3
    assert _resolve_workers(["run", "--shard", "0", "--of", "12"]) == default_w
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ.pop(var, None)
    _cap_blas_threads()
    assert os.environ["OMP_NUM_THREADS"] == "1", "BLAS cap missing"
    print("selftest: PASS (v1 constants + seed bands disjoint [v1/W1/registry/"
          "law W3-W4] + law band parity + p pattern + determinism + slice "
          "math + canon intact + W1 dep complete + path safety + O-2355 "
          "multiprocess code-backed workers plan)")
    return 0


def main():
    argv = sys.argv[1:]
    if "selftest" in argv:
        return selftest()
    if "finalize" in argv:
        return finalize()
    if "probe" in argv:
        return probe()
    if "parity" in argv:
        return parity()
    if "status" in argv:
        return status()
    shard = nshards = None
    if "--shard" in argv:
        shard = int(argv[argv.index("--shard") + 1])
    if "--of" in argv:
        nshards = int(argv[argv.index("--of") + 1])
    if "--nshards" in argv:
        nshards = int(argv[argv.index("--nshards") + 1])
    if shard is None or nshards is None:
        print(__doc__)
        print("usage: run --shard i --of N [--workers W] | finalize | probe | "
              "parity | status | selftest")
        return 2
    if "run" not in argv:
        print("usage: run --shard i --of N [--workers W]")
        return 2
    assert 0 <= shard < nshards, "shard out of range"
    return run_shard(shard, nshards, workers=_resolve_workers(argv))


if __name__ == "__main__":
    sys.exit(main())
