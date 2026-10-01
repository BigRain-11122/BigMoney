"""PERPETUAL_FACES N1 wave runner -- T-133 s2 (CEO O-2026-09-30-2340).

Law: research/PERPETUAL_FACES.md v1.0 sec.2/sec.4 (FROZEN bm-b r484).
Wave prereg: per-wave frozen pre-run (R99; bands = law sec.4 ledger rows
verbatim, R250 one-step -- bands frozen in the law BEFORE any wave runner
exists, no re-pick after freeze).

v0.3 (bm-b r490): wave-parameterized (--wave, law sec.4 pre-assigned rows
W2/W3; W2 default = landed frozen wave, byte-identical behavior). Wave
config travels to spawn-side workers via the executor initializer (Windows
spawn re-imports the module with W2 defaults -- the initializer re-pins the
wave before any rng use). finalize() composes the cumulative pool per law
sec.5 (canon + W1 ext + every completed prior wave + this wave).

Design = frozen v1 null calibration VERBATIM via import-face reuse:
  engine      = p2_null_calibration.run_one (same-source, no re-impl)
  assembly    = p2_null_calibration_ext._assemble / _entry_matrix / p_for
  slice law   = contiguous shard slicing, zero gap/overlap (ext pattern)
  determinism = same seed -> byte-equal rerun (shard file = checkpoint)

W2 bands (law sec.4):
  family A: j = 0..1999, entry seed = 12_100 + j  (random entry, engine exit)
  family B: j = 0..199,  entry seed = 12_100 + j (paired with A[j]),
                            exit seed = 21_100 + j (random exit, p=0.05)
W3 bands (law sec.4):
  family A: j = 0..1999, entry seed = 14_100 + j
  family B: j = 0..199,  entry seed = 14_100 + j (paired with A[j]),
                            exit seed = 21_300 + j

Subcommands:
  run --shard i --of N [--wave W] [--workers P]
                         burn shard i of N for wave W (default 2; also
                         accepts --nshards), writes
                         results/p2cal_ext/n1_w<W>/shard-<i>-of-<N>.json
                         --workers P: process-pool size (default: full cores,
                         O-2026-09-30-2355 multicore law + O-20260930-1858
                         holiday full-core mobilization; BLAS capped 1/worker)
  finalize [--wave W]    FAIL-CLOSED merge of all shards -> cumulative null
                         pool (law sec.5: canon 120 + W1 ext 2200 +
                         completed prior waves + this wave 2200),
                         skill_line_v2 K-lift at same n_eff (v2 attribution
                         law), ledger +2200, writes
                         results/perpetual_faces/n1_w<W>_results.json
  probe                 2-run end-to-end design probe at out-of-band seeds
                         95_002/95_003 (ledger +0; W2 design face only --
                         wave 3 design = W2 verbatim, honest no-op)
  parity                serial-vs-pool byte-equality check on real wave
                         j-slice (O-2355 conversion verification face;
                         ledger +0; writes _n1_w2_parity.json; W2 face only)
  status [--wave W]     shard inventory + finalize state (read-only)
  selftest              offline hermetic checks (no network, no engine)
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
CUTOFF = ext.CUTOFF                      # 2026-09-22 same-window law
A_N = 2000
B_N = 200
PROBE_ENTRY_SEED = 95_002               # out-of-band (design probe only)
PROBE_EXIT_SEED = 95_003
OUT_DIR = os.path.join(PATHS.results_dir, "perpetual_faces")
W1_EXT_OUT = os.path.join(PATHS.results_dir, "p2_calibration_v2_ext.json")

# --- law sec.4 wave ledger (bands verbatim; runner is wave-parameterized,
#     single source = law file mirrored in perpetual_faces.N1_BANDS which
#     selftest asserts parity against -- never a new pick after freeze) ---
WAVE_CONFIGS = {
    2: {"batch": "PERPETUAL-N1-W2",
        "prereg": ("research/PERPETUAL_N1_W2_PREREG.md (wave-level frozen "
                   "pre-run; design = frozen v1 null calibration verbatim, "
                   "new seed bands only)"),
        "a_seed_base": 12_100,           # law sec.4 W2 A: 12_100..14_099
        "b_exit_seed_base": 21_100,      # law sec.4 W2 B: 21_100..21_299
        "shard_subdir": "n1_w2", "out_name": "n1_w2_results.json"},
    3: {"batch": "PERPETUAL-N1-W3",
        "prereg": ("research/PERPETUAL_N1_W3_PREREG.md (wave-level frozen "
                   "pre-run; design = frozen v1 null calibration verbatim, "
                   "new seed bands only)"),
        "a_seed_base": 14_100,           # law sec.4 W3 A: 14_100..16_099
        "b_exit_seed_base": 21_300,      # law sec.4 W3 B: 21_300..21_499
        "shard_subdir": "n1_w3", "out_name": "n1_w3_results.json"},
    4: {"batch": "PERPETUAL-N1-W4",
        "prereg": ("research/PERPETUAL_N1_W4_PREREG.md (wave-level frozen "
                   "pre-run; design = frozen v1 null calibration verbatim, "
                   "new seed bands only)"),
        "a_seed_base": 16_100,           # law sec.4 W4 A: 16_100..18_099
        "b_exit_seed_base": 21_500,      # law sec.4 W4 B: 21_500..21_699
        "shard_subdir": "n1_w4", "out_name": "n1_w4_results.json"},
    # W5 (r307 bm-c, prereg-time tail extension): A skip-over -- the
    # arithmetic +2_000 tail 18_100..20_099 hits the v1 B in-use band
    # 20_000..20_019 (and ext W1 B 20_100..20_299); disjointness hard law
    # wins, A packs at the first free window (W5 B end + 1); B keeps the
    # +200 stride verbatim. W6+ must re-base B (its arithmetic tail lands
    # inside this A band) -- same disclosed skip-over discipline.
    5: {"batch": "PERPETUAL-N1-W5",
        "prereg": ("research/PERPETUAL_N1_W5_PREREG.md (wave-level frozen "
                   "pre-run; design = frozen v1 null calibration verbatim, "
                   "new seed bands only)"),
        "a_seed_base": 21_900,           # law sec.4 W5 A: 21_900..23_899 (skip-over)
        "b_exit_seed_base": 21_700,      # law sec.4 W5 B: 21_700..21_899
        "shard_subdir": "n1_w5", "out_name": "n1_w5_results.json"},
    # W6 (r309 bm-c, law sec.4 W6+ WARNING executed): A keeps the
    # arithmetic +2_000 tail (23_900..25_899, clean); B's arithmetic +200
    # tail 21_900..22_099 is documented-refused (falls inside the W5 A
    # band) -- B re-bases past every reserved band incl. this wave's own
    # A band, packing at W6 A end + 1 (25_900..26_099). Same disclosed
    # skip-over discipline as W5; NOT a re-pick (R250).
    6: {"batch": "PERPETUAL-N1-W6",
        "prereg": ("research/PERPETUAL_N1_W6_PREREG.md (wave-level frozen "
                   "pre-run; design = frozen v1 null calibration verbatim, "
                   "new seed bands only)"),
        "a_seed_base": 23_900,           # law sec.4 W6 A: 23_900..25_899 (arithmetic)
        "b_exit_seed_base": 25_900,      # law sec.4 W6 B: 25_900..26_099 (skip-over)
        "shard_subdir": "n1_w6", "out_name": "n1_w6_results.json"},
    # W7 (r501 bm-b, same disclosed skip-over discipline -- BOTH tails
    # refused): A's arithmetic +2_000 tail 25_900..27_899 is
    # documented-refused (falls on the W6 B band 25_900..26_099), so A
    # re-bases past every reserved band, packing at W6 B end + 1
    # (26_100..28_099); B's arithmetic +200 tail 26_100..26_299 is in
    # turn refused (falls inside THIS wave's own A band), so B re-bases
    # incl. this wave's A, packing at W7 A end + 1 (28_100..28_299).
    # NOT a re-pick (R250).
    7: {"batch": "PERPETUAL-N1-W7",
        "prereg": ("research/PERPETUAL_N1_W7_PREREG.md (wave-level frozen "
                   "pre-run; design = frozen v1 null calibration verbatim, "
                   "new seed bands only)"),
        "a_seed_base": 26_100,           # law sec.4 W7 A: 26_100..28_099 (skip-over)
        "b_exit_seed_base": 28_100,      # law sec.4 W7 B: 28_100..28_299 (skip-over)
        "shard_subdir": "n1_w7", "out_name": "n1_w7_results.json"},
}

PREREG = WAVE_CONFIGS[2]["prereg"]
A_SEED_BASE = WAVE_CONFIGS[2]["a_seed_base"]
B_EXIT_SEED_BASE = WAVE_CONFIGS[2]["b_exit_seed_base"]
SHARD_DIR = os.path.join(PATHS.results_dir, "p2cal_ext",
                         WAVE_CONFIGS[2]["shard_subdir"])
OUT = os.path.join(OUT_DIR, WAVE_CONFIGS[2]["out_name"])
PROBE_OUT = os.path.join(OUT_DIR, "_n1_w2_probe.json")


def _set_wave(w: int) -> None:
    """Switch the active wave face (law sec.4 pre-assigned rows only; the
    W2 default path stays byte-identical). Also used as the spawn-side
    wave carrier: child processes re-import the module with W2 defaults,
    so the executor initializer re-pins the wave before any rng use."""
    global WAVE, BATCH, PREREG, A_SEED_BASE, B_EXIT_SEED_BASE, SHARD_DIR, OUT
    cfg = WAVE_CONFIGS[w]
    WAVE = w
    BATCH = cfg["batch"]
    PREREG = cfg["prereg"]
    A_SEED_BASE = cfg["a_seed_base"]
    B_EXIT_SEED_BASE = cfg["b_exit_seed_base"]
    SHARD_DIR = os.path.join(PATHS.results_dir, "p2cal_ext", cfg["shard_subdir"])
    OUT = os.path.join(OUT_DIR, cfg["out_name"])


# --- pool harvest handshake (r496 canon, T-134 s3) -------------------------
# Worker-side half: on a verified-done shard write results/pool_claims/
# <entry>/<shard>.<machine>.json state=closed outcome=ok so the launcher's
# harvest flip lands the shard done. The worker NEVER writes
# runnable_pool.json (pool single-writer law). Without this handshake a
# completed wave reads as a crash to the fuse and autofill relaunches the
# same shard forever (r498 live family: 12/12 checkpoints on disk, pool
# shards stuck 'ready', claim-relaunch churn every tick).

def _machine_id() -> str:
    try:
        return json.load(open(os.path.join(
            PATHS.root, "fleet", "machine.json"), encoding="utf-8")
        ).get("machine_id", "unknown")
    except Exception:
        return "unknown"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S") + time.strftime("%z")[:3] \
        + ":" + time.strftime("%z")[3:]


def _pool_claim(entry_id: str, shard_key: str, detail: str) -> None:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = os.path.join(root, "results", "pool_claims",
                     entry_id.replace("/", "_"))
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, f"{shard_key}.{_machine_id()}.json")
    now = _now_iso()
    with open(fp, "w", encoding="utf-8") as f:
        json.dump({"machine_id": _machine_id(), "state": "closed",
                   "pid": os.getpid(), "heartbeat": now, "outcome": "ok",
                   "exit_code": 0, "closed_at": now, "result_ref": detail},
                  f, ensure_ascii=False, indent=1)
    print(f"pool claim closed: {os.path.basename(fp)}", flush=True)


def _entry_shard_of(shard: int, nshards: int) -> tuple:
    """Pool entry/shard identity (mirrors the T-133 s2 registration face:
    PERPETUAL-N1-W<wave>-SHARD-<i> / n1w<wave>-<i>of<N>)."""
    return (f"PERPETUAL-N1-W{WAVE}-SHARD-{shard}", f"n1w{WAVE}-{shard}of{nshards}")


def _shard_valid(path: str, shard: int, nshards: int) -> bool:
    """Checkpoint presence law (pool contract: presence=done, deterministic
    rerun byte-equal): a shard file counts as done only if it parses, its
    shard/nshards fields match, the slice ranges obey the contiguous slice
    law, and both families carry exactly the expected run counts."""
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return False
    if d.get("batch") != BATCH or d.get("shard") != shard \
            or d.get("nshards") != nshards:
        return False
    a_lo, a_hi = d.get("a_range") or [-1, -1]
    b_lo, b_hi = d.get("b_range") or [-1, -1]
    if (a_lo, a_hi) != (shard * A_N // nshards, (shard + 1) * A_N // nshards):
        return False
    if (b_lo, b_hi) != (shard * B_N // nshards, (shard + 1) * B_N // nshards):
        return False
    fams = d.get("families") or {}
    n_a = len((fams.get("A_random_engine_exit") or {}).get("runs") or [])
    n_b = len((fams.get("B_random_entry_random_exit") or {}).get("runs") or [])
    return n_a == a_hi - a_lo and n_b == b_hi - b_lo


def p_for(j: int) -> float:
    """50-seed block alternation, v1 pattern continuation (import-face)."""
    return ext.p_for(j)


# --- O-2026-09-30-2355 multicore law: single body, two drivers (serial/pool) ---
_CTX = None        # per-process assembled engine context (spawn-safe global)


def _worker_init(wave: int = 2):
    global _CTX
    _set_wave(wave)          # spawn carrier: re-pin wave before any rng use
    v1m, prices, idx, closes, cost_rate = ext._assemble()
    _CTX = (prices, idx, closes, closes.shape[0], closes.shape[1],
            list(closes.columns))


def _run_a(j: int) -> dict:
    prices, idx, closes, n_days, n_syms, cols = _CTX
    p = p_for(j)
    rng = np.random.default_rng(A_SEED_BASE + j)
    entry = ext._entry_matrix(rng, n_days, n_syms, idx, cols, p)
    exit_ = pd.DataFrame(False, index=idx, columns=cols)
    r = v1.run_one(prices, idx, entry, exit_, {}, f"w{WAVE}A_p{p}_j{j}")
    return {**r, "p": p, "seed_rng": A_SEED_BASE + j,
            "note": f"w{WAVE} random entry p={p} rng={A_SEED_BASE + j}; "
                    f"exits=engine rules (v1 design verbatim)"}


def _run_b(j: int) -> dict:
    prices, idx, closes, n_days, n_syms, cols = _CTX
    p = p_for(j)
    rng = np.random.default_rng(A_SEED_BASE + j)      # SAME matrix as A[j]
    entry = ext._entry_matrix(rng, n_days, n_syms, idx, cols, p)
    rng_x = np.random.default_rng(B_EXIT_SEED_BASE + j)
    exit_ = pd.DataFrame((rng_x.random((n_days, n_syms)) < v1.P_EXIT),
                         index=idx, columns=cols)
    r = v1.run_one(prices, idx, entry, exit_, {}, f"w{WAVE}B_p{p}_j{j}")
    return {**r, "p": p, "seed_rng_entry": A_SEED_BASE + j,
            "seed_rng_exit": B_EXIT_SEED_BASE + j,
            "note": f"w{WAVE} random entry rng={A_SEED_BASE + j} "
                    f"(paired with w{WAVE}A_j{j}) + random exit "
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

    # checkpoint presence law: verified-done shard -> claim handshake +
    # skip the burn (pool contract "presence=done; deterministic rerun
    # byte-equal"; stops the relaunch churn on already-burned shards).
    ckpt = os.path.join(SHARD_DIR, f"shard-{shard}-of-{nshards}.json")
    if os.path.exists(ckpt) and _shard_valid(ckpt, shard, nshards):
        entry_id, shard_key = _entry_shard_of(shard, nshards)
        _pool_claim(entry_id, shard_key,
                    f"verified checkpoint skip: {os.path.basename(ckpt)} "
                    f"(presence=done, slice+family counts verified)")
        print(f"skip: {os.path.basename(ckpt)} verified done "
              f"(slice A[{a_lo}..{a_hi}) B[{b_lo}..{b_hi}))", flush=True)
        return 0

    if workers > 1:
        _cap_blas_threads()
        with ProcessPoolExecutor(max_workers=workers,
                                  initializer=_worker_init,
                                  initargs=(WAVE,)) as ex:
            fam_a = list(ex.map(_run_a, range(a_lo, a_hi)))
            fam_b = list(ex.map(_run_b, range(b_lo, b_hi)))
    else:
        _worker_init(WAVE)                   # in-process ctx, serial driver
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
    entry_id, shard_key = _entry_shard_of(shard, nshards)
    _pool_claim(entry_id, shard_key,
                f"shard burned: {os.path.basename(path)} "
                f"({out['audit']['n_backtests']} runs, "
                f"{out['audit']['elapsed_sec']}s)")
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


def _wave_values(w: int) -> list:
    """Prior wave's run sharpes from its committed finalize output
    (law sec.5 cumulative composition; FAIL-CLOSED on incompleteness)."""
    fp = os.path.join(OUT_DIR, WAVE_CONFIGS[w]["out_name"])
    d = json.load(open(fp, encoding="utf-8"))
    fams = d.get("families") or {}
    a = (fams.get("A_random_engine_exit") or {}).get("runs") or []
    b = (fams.get("B_random_entry_random_exit") or {}).get("runs") or []
    vals = [float(r["full"]["sharpe"]) for r in a + b]
    assert len(vals) == A_N + B_N, \
        f"prior wave W{w} file incomplete: {len(vals)} != {A_N + B_N} (FAIL-CLOSED)"
    return vals


def finalize() -> int:
    shard_files = sorted(glob.glob(os.path.join(
        SHARD_DIR, "shard-*-of-*.json")))
    if not shard_files:
        print(f"finalize: FAIL-CLOSED -- no shard files under "
              f"results/p2cal_ext/{WAVE_CONFIGS[WAVE]['shard_subdir']}/")
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
    wv_vals = [float(r["full"]["sharpe"]) for r in a_runs + b_runs]
    # law sec.5 cumulative composition: canon + W1 ext + every completed
    # prior wave's finalize output + this wave (N_eff never resets)
    pre_values = list(canon_pool["values"]) + w1_vals       # 2,320 base
    pre_parts = ["canon 120", "W1 ext 2200"]
    for w in range(2, WAVE):
        pre_values += _wave_values(w)
        pre_parts.append(f"W{w} 2200")
    merged_values = pre_values + wv_vals

    def cov(vals, schema):
        return {"n_values": len(vals), "schemas_parsed": [schema],
                "known_unparsed": [], "mu": sum(vals) / len(vals),
                "sigma": sg._pstdev(vals)}

    cov_pre = cov(pre_values, " + ".join(pre_parts)
                  + f" (pre-W{WAVE} cumulative)")
    cov_wv = cov(wv_vals, f"n1_w{WAVE} shard merge: "
                          "families[*].runs[].full.sharpe")
    cov_mrg = cov(merged_values, " + ".join(pre_parts + [f"W{WAVE} 2200"]))

    # K-lift at the SAME n_eff on both sides (v2 attribution law verbatim)
    line_old = sg.skill_line_v2(batch_cells=0,
                                null_pool={"values": pre_values,
                                           "coverage": cov_pre})
    line_new = sg.skill_line_v2(batch_cells=0,
                                null_pool={"values": merged_values,
                                           "coverage": cov_mrg})

    led = sg.append_ledger(BATCH, A_N + B_N,
                           f"perpetual_faces/n1_w{WAVE}_results.json",
                           note=f"perpetual N1 nulls-deepening wave {WAVE} (law "
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
            f"pre_w{WAVE}_cumulative": {"n_values": cov_pre["n_values"],
                                        "mu": cov_pre["mu"],
                                        "sigma": cov_pre["sigma"]},
            f"w{WAVE}_only": {"n_values": cov_wv["n_values"],
                              "mu": cov_wv["mu"], "sigma": cov_wv["sigma"]},
            "merged": {"n_values": cov_mrg["n_values"], "mu": cov_mrg["mu"],
                       "sigma": cov_mrg["sigma"]},
            f"mu_delta_w{WAVE}_vs_w{WAVE-1}ext": None,  # filled below
            f"se_mu_at_k{cov_mrg['n_values']}": round(
                cov_mrg["sigma"] / (cov_mrg["n_values"] ** 0.5), 6),
        },
        "skill_line_v2_k_lift": {
            "n_eff_held_equal": line_old["n_eff"],
            f"line_pre_w{WAVE}": line_old["line"],
            f"line_merged_{cov_mrg['n_values']}": line_new["line"],
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
    if WAVE == 2:
        w1d = json.load(open(W1_EXT_OUT, encoding="utf-8"))
        prior_mu = ((w1d.get("null_pool_old_vs_new") or {})
                    .get("ext_only") or {}).get("mu")
    else:
        wprev = json.load(open(os.path.join(
            OUT_DIR, WAVE_CONFIGS[WAVE - 1]["out_name"]), encoding="utf-8"))
        prior_mu = ((wprev.get("null_pool_cumulative") or {})
                    .get(f"w{WAVE - 1}_only") or {}).get("mu")
    if prior_mu is not None:
        out["null_pool_cumulative"][f"mu_delta_w{WAVE}_vs_w{WAVE-1}ext"] = round(
            cov_wv["mu"] - prior_mu, 6)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, default=str)
    print(f"pre-W{WAVE}  mu={cov_pre['mu']:.4f} sigma={cov_pre['sigma']:.4f} "
          f"(K={cov_pre['n_values']})")
    print(f"w{WAVE}      mu={cov_wv['mu']:.4f} sigma={cov_wv['sigma']:.4f} "
          f"(K={cov_wv['n_values']})")
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
    if WAVE != 2:
        print(f"probe: W2 design-verification face only (wave {WAVE} design "
              f"= W2 verbatim, already verified r485) -- honest no-op")
        return 0
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
    if WAVE != 2:
        print(f"parity: O-2355 conversion-verification face ran on W2 "
              f"(byte-equal PASS, r485/r488); wave {WAVE} reuses the same "
              f"serial/pool driver verbatim -- honest no-op")
        return 0
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
    # 10. pool harvest handshake (r498): entry/shard identity mirrors the
    # T-133 s2 registration face; _shard_valid accepts only slice-law-
    # conforming, family-count-exact checkpoints (presence=done contract).
    import tempfile
    assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W2-SHARD-0", "n1w2-0of12")
    assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W2-SHARD-11", "n1w2-11of12")
    a0, a1 = 3 * A_N // 12, 4 * A_N // 12
    b0, b1 = 3 * B_N // 12, 4 * B_N // 12
    good = {"batch": BATCH, "shard": 3, "nshards": 12, "a_range": [a0, a1],
            "b_range": [b0, b1],
            "families": {"A_random_engine_exit": {"runs": [{}] * (a1 - a0)},
                         "B_random_entry_random_exit": {"runs": [{}] * (b1 - b0)}}}
    with tempfile.NamedTemporaryFile("w", suffix=".json",
                                      delete=False) as tf:
        json.dump(good, tf)
        tp = tf.name
    try:
        assert _shard_valid(tp, 3, 12), "valid checkpoint rejected"
        for bad in ({"batch": "OTHER", "shard": 3, "nshards": 12},
                    {**good, "shard": 4},
                    {**good, "a_range": [a0 + 1, a1]},
                    {**good, "families": {
                        "A_random_engine_exit": {"runs": [{}] * (a1 - a0 - 1)},
                        "B_random_entry_random_exit": {"runs": [{}] * (b1 - b0)}}},
                    "{truncated json"):
            with open(tp, "w", encoding="utf-8") as f:
                if isinstance(bad, str):
                    f.write(bad)
                else:
                    json.dump(bad, f)
            assert not _shard_valid(tp, 3, 12), f"invalid checkpoint accepted: {bad.get('batch', bad) if isinstance(bad, dict) else bad}"  # noqa: E501
    finally:
        os.unlink(tp)
    assert _machine_id(), "machine_id unreadable"
    # 11. wave-3 face (per-shard materializer lane): law sec.4 W3 rows
    # verbatim, disjointness vs every in-use band, spawn-carrier parity,
    # entry identity, path separation, prereg presence (never fake-supply),
    # finalize cumulative dependency present.
    _set_wave(3)
    try:
        import perpetual_faces as pf
        assert WAVE_CONFIGS[3]["a_seed_base"] == pf.N1_BANDS[3]["a"][0], \
            "W3 A band drift vs law mirror"
        assert WAVE_CONFIGS[3]["b_exit_seed_base"] == \
            pf.N1_BANDS[3]["b_exit"][0], "W3 B band drift vs law mirror"
        w3_a = {A_SEED_BASE + j for j in range(A_N)}
        w3_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w3_a & w3_b), "W3 A/B band overlap"
        assert not (w3_a & reg_ints) and not (w3_b & reg_ints), \
            "W3 hits SEED_REGISTRY"
        for nm, band in (("A", w3_a), ("B", w3_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W3 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W3 {nm} hits W1"
            assert not (band & probes), f"W3 {nm} hits probe seeds"
        assert not (w3_a & {WAVE_CONFIGS[2]["a_seed_base"] + j
                            for j in range(A_N)}), "W3 A hits W2 band"
        assert not (w3_b & {WAVE_CONFIGS[2]["b_exit_seed_base"] + j
                             for j in range(B_N)}), "W3 B hits W2 band"
        la = set(range(pf.N1_BANDS[4]["a"][0], pf.N1_BANDS[4]["a"][1] + 1))
        lb = set(range(pf.N1_BANDS[4]["b_exit"][0],
                       pf.N1_BANDS[4]["b_exit"][1] + 1))
        assert not (w3_a & la) and not (w3_b & lb), "W3 hits law W4 band"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W3-SHARD-0",
                                          "n1w3-0of12"), "W3 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W3-SHARD-11",
                                           "n1w3-11of12")
        assert SHARD_DIR.endswith("n1_w3") and OUT.endswith(
            "n1_w3_results.json"), "W3 path drift"
        assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
            PATHS.results_dir, "p2cal_ext", WAVE_CONFIGS[2]["shard_subdir"])), \
            "W3 shard dir collides with W2"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W3_PREREG.md")), \
            "W3 per-wave prereg missing (materializer requirement)"
        assert os.path.exists(os.path.join(
            OUT_DIR, WAVE_CONFIGS[2]["out_name"])), \
            "W3 finalize cumulative dep (W2 output) missing"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- wave-4 face (r507 bm-a: same guard set as W3, cumulative dep = W3) ---
    _set_wave(4)
    try:
        assert WAVE_CONFIGS[4]["a_seed_base"] == pf.N1_BANDS[4]["a"][0], \
            "W4 A band drift vs law mirror"
        assert WAVE_CONFIGS[4]["b_exit_seed_base"] == \
            pf.N1_BANDS[4]["b_exit"][0], "W4 B band drift vs law mirror"
        w4_a = {A_SEED_BASE + j for j in range(A_N)}
        w4_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w4_a & w4_b), "W4 A/B band overlap"
        assert not (w4_a & reg_ints) and not (w4_b & reg_ints), \
            "W4 hits SEED_REGISTRY"
        for nm, band in (("A", w4_a), ("B", w4_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W4 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W4 {nm} hits W1"
            assert not (band & probes), f"W4 {nm} hits probe seeds"
        assert not (w4_a & {WAVE_CONFIGS[2]["a_seed_base"] + j
                            for j in range(A_N)}), "W4 A hits W2 band"
        assert not (w4_b & {WAVE_CONFIGS[2]["b_exit_seed_base"] + j
                             for j in range(B_N)}), "W4 B hits W2 band"
        assert not (w4_a & {WAVE_CONFIGS[3]["a_seed_base"] + j
                            for j in range(A_N)}), "W4 A hits W3 band"
        assert not (w4_b & {WAVE_CONFIGS[3]["b_exit_seed_base"] + j
                             for j in range(B_N)}), "W4 B hits W3 band"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W4-SHARD-0",
                                          "n1w4-0of12"), "W4 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W4-SHARD-11",
                                           "n1w4-11of12")
        assert SHARD_DIR.endswith("n1_w4") and OUT.endswith(
            "n1_w4_results.json"), "W4 path drift"
        assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
            PATHS.results_dir, "p2cal_ext", WAVE_CONFIGS[2]["shard_subdir"])), \
            "W4 shard dir collides with W2"
        assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
            PATHS.results_dir, "p2cal_ext", WAVE_CONFIGS[3]["shard_subdir"])), \
            "W4 shard dir collides with W3"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W4_PREREG.md")), \
            "W4 per-wave prereg missing (materializer requirement)"
        assert os.path.exists(os.path.join(
            OUT_DIR, WAVE_CONFIGS[3]["out_name"])), \
            "W4 finalize cumulative dep (W3 output) missing"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- wave-5 face (r307 bm-c: same guard set as W3/W4, dep = W4;
    #     A band = documented skip-over per law sec.4 W5 row) ---
    _set_wave(5)
    try:
        assert WAVE_CONFIGS[5]["a_seed_base"] == pf.N1_BANDS[5]["a"][0], \
            "W5 A band drift vs law mirror"
        assert WAVE_CONFIGS[5]["b_exit_seed_base"] == \
            pf.N1_BANDS[5]["b_exit"][0], "W5 B band drift vs law mirror"
        w5_a = {A_SEED_BASE + j for j in range(A_N)}
        w5_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w5_a & w5_b), "W5 A/B band overlap"
        assert not (w5_a & reg_ints) and not (w5_b & reg_ints), \
            "W5 hits SEED_REGISTRY"
        for nm, band in (("A", w5_a), ("B", w5_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W5 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W5 {nm} hits W1"
            assert not (band & probes), f"W5 {nm} hits probe seeds"
        for wprev in (2, 3, 4):
            assert not (w5_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                for j in range(A_N)}), f"W5 A hits W{wprev}"
            assert not (w5_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                               for j in range(B_N)}), f"W5 B hits W{wprev}"
        # skip-over refusal facts (law sec.4 W5 row): the arithmetic
        # +2_000 tail WOULD hit the v1 B in-use band -> disjointness law
        # forces the skip; packing invariant = A sits at W5 B end + 1.
        arith_a = {WAVE_CONFIGS[4]["a_seed_base"] + 2000 + j
                  for j in range(A_N)}
        assert arith_a & v1_b, "refused arithmetic tail must hit v1 B (doc)"
        assert arith_a & reg_ints, "refused arithmetic tail must hit registry"
        assert WAVE_CONFIGS[5]["a_seed_base"] == \
            WAVE_CONFIGS[5]["b_exit_seed_base"] + B_N, \
            "W5 packing drift (A must sit at W5 B end + 1)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W5-SHARD-0",
                                          "n1w5-0of12"), "W5 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W5-SHARD-11",
                                           "n1w5-11of12")
        assert SHARD_DIR.endswith("n1_w5") and OUT.endswith(
            "n1_w5_results.json"), "W5 path drift"
        for wprev in (2, 3, 4):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W5 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W5_PREREG.md")), \
            "W5 per-wave prereg missing (materializer requirement)"
        assert os.path.exists(os.path.join(
            OUT_DIR, WAVE_CONFIGS[4]["out_name"])), \
            "W5 finalize cumulative dep (W4 output) missing"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
        # --- wave-6 face (r309 bm-c: same guard set, dep = W5; B band =
        #     documented skip-over per law sec.4 W6+ WARNING row) ---
        _set_wave(6)
        try:
            assert WAVE_CONFIGS[6]["a_seed_base"] == pf.N1_BANDS[6]["a"][0], \
                "W6 A band drift vs law mirror"
            assert WAVE_CONFIGS[6]["b_exit_seed_base"] == \
                pf.N1_BANDS[6]["b_exit"][0], "W6 B band drift vs law mirror"
            w6_a = {A_SEED_BASE + j for j in range(A_N)}
            w6_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
            assert not (w6_a & w6_b), "W6 A/B band overlap"
            assert not (w6_a & reg_ints) and not (w6_b & reg_ints), \
                "W6 hits SEED_REGISTRY"
            for nm, band in (("A", w6_a), ("B", w6_b)):
                assert not (band & v1_a) and not (band & v1_b), f"W6 {nm} hits v1"
                assert not (band & w1_a) and not (band & w1_b), f"W6 {nm} hits W1"
                assert not (band & probes), f"W6 {nm} hits probe seeds"
            for wprev in (2, 3, 4, 5):
                assert not (w6_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                    for j in range(A_N)}), f"W6 A hits W{wprev}"
                assert not (w6_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                    for j in range(B_N)}), f"W6 B hits W{wprev}"
            # skip-over refusal facts (law sec.4 W6+ WARNING): the B
            # arithmetic +200 tail lands inside the W5 A band -> the skip
            # is forced; packing invariant = B sits at W6 A end + 1 (A
            # keeps its arithmetic +2_000 tail = W5 A end + 1).
            arith_b = {WAVE_CONFIGS[5]["b_exit_seed_base"] + 200 + j
                       for j in range(B_N)}
            assert arith_b & {WAVE_CONFIGS[5]["a_seed_base"] + j
                              for j in range(A_N)}, \
                "refused B arithmetic tail must hit W5 A (doc)"
            assert WAVE_CONFIGS[6]["a_seed_base"] == \
                WAVE_CONFIGS[5]["a_seed_base"] + 2000, \
                "W6 A must keep the arithmetic +2_000 tail (W5 A end + 1)"
            assert WAVE_CONFIGS[6]["b_exit_seed_base"] == \
                WAVE_CONFIGS[6]["a_seed_base"] + A_N, \
                "W6 packing drift (B must sit at W6 A end + 1)"
            assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W6-SHARD-0",
                                              "n1w6-0of12"), "W6 entry identity"
            assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W6-SHARD-11",
                                               "n1w6-11of12")
            assert SHARD_DIR.endswith("n1_w6") and OUT.endswith(
                "n1_w6_results.json"), "W6 path drift"
            for wprev in (2, 3, 4, 5):
                assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                    PATHS.results_dir, "p2cal_ext",
                    WAVE_CONFIGS[wprev]["shard_subdir"])), \
                    f"W6 shard dir collides with W{wprev}"
            assert os.path.exists(os.path.join(
                PATHS.root, "research", "PERPETUAL_N1_W6_PREREG.md")), \
                "W6 per-wave prereg missing (materializer requirement)"
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[5]["out_name"])), \
                "W6 finalize cumulative dep (W5 output) missing"
            assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
            # --- wave-7 face (r501 bm-b: same guard set; BOTH bands =
            #     documented skip-over per law sec.4 W7 row) ---
            _set_wave(7)
            try:
                assert WAVE_CONFIGS[7]["a_seed_base"] == pf.N1_BANDS[7]["a"][0], \
                    "W7 A band drift vs law mirror"
                assert WAVE_CONFIGS[7]["b_exit_seed_base"] == \
                    pf.N1_BANDS[7]["b_exit"][0], "W7 B band drift vs law mirror"
                w7_a = {A_SEED_BASE + j for j in range(A_N)}
                w7_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
                assert not (w7_a & w7_b), "W7 A/B band overlap"
                assert not (w7_a & reg_ints) and not (w7_b & reg_ints), \
                    "W7 hits SEED_REGISTRY"
                for nm, band in (("A", w7_a), ("B", w7_b)):
                    assert not (band & v1_a) and not (band & v1_b), f"W7 {nm} hits v1"
                    assert not (band & w1_a) and not (band & w1_b), f"W7 {nm} hits W1"
                    assert not (band & probes), f"W7 {nm} hits probe seeds"
                for wprev in (2, 3, 4, 5, 6):
                    assert not (w7_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                        for j in range(A_N)}), f"W7 A hits W{wprev}"
                    assert not (w7_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                        for j in range(B_N)}), f"W7 B hits W{wprev}"
                # skip-over refusal facts (law sec.4 W7 row): A's
                # arithmetic +2_000 tail hits the W6 B band and B's
                # arithmetic +200 tail falls inside the W7 A band -- BOTH
                # skips forced; packing: A == W6 B end + 1, B == W7 A end + 1.
                arith_a7 = {WAVE_CONFIGS[6]["a_seed_base"] + 2000 + j
                            for j in range(A_N)}
                assert arith_a7 & {WAVE_CONFIGS[6]["b_exit_seed_base"] + j
                                   for j in range(B_N)}, \
                    "refused A arithmetic tail must hit W6 B (doc)"
                arith_b7 = {WAVE_CONFIGS[6]["b_exit_seed_base"] + 200 + j
                            for j in range(B_N)}
                assert arith_b7 & {WAVE_CONFIGS[7]["a_seed_base"] + j
                                   for j in range(A_N)}, \
                    "refused B arithmetic tail must hit W7 A (doc)"
                assert WAVE_CONFIGS[7]["a_seed_base"] == \
                    WAVE_CONFIGS[6]["b_exit_seed_base"] + B_N, \
                    "W7 packing drift (A must sit at W6 B end + 1)"
                assert WAVE_CONFIGS[7]["b_exit_seed_base"] == \
                    WAVE_CONFIGS[7]["a_seed_base"] + A_N, \
                    "W7 packing drift (B must sit at W7 A end + 1)"
                assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W7-SHARD-0",
                                                  "n1w7-0of12"), "W7 entry identity"
                assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W7-SHARD-11",
                                                   "n1w7-11of12")
                assert SHARD_DIR.endswith("n1_w7") and OUT.endswith(
                    "n1_w7_results.json"), "W7 path drift"
                for wprev in (2, 3, 4, 5, 6):
                    assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                        PATHS.results_dir, "p2cal_ext",
                        WAVE_CONFIGS[wprev]["shard_subdir"])), \
                        f"W7 shard dir collides with W{wprev}"
                assert os.path.exists(os.path.join(
                    PATHS.root, "research", "PERPETUAL_N1_W7_PREREG.md")), \
                    "W7 per-wave prereg missing (materializer requirement)"
                # W7 finalize cumulative dep (W6 output) = IN FLIGHT at
                # drafting (12/12 burned pool-side, finalize queued on the
                # bm-a product push per MSG-20261001-103x) -- no static
                # exists-assert here: it would false-red now and expire
                # later (r307 two-state lesson family); the finalize merge
                # loop is FAIL-CLOSED on any missing prior-wave output at
                # run time, which is the real guard.
                assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
            finally:
                _set_wave(2)
        finally:
            _set_wave(2)
    finally:
        _set_wave(2)
    print("selftest: PASS (v1 constants + seed bands disjoint [v1/W1/registry/"
          "law W2/W3] + law band parity + p pattern + determinism + slice "
          "math + canon intact + W1 dep complete + path safety + O-2355 "
          "multiprocess code-backed workers plan + r498 pool claim "
          "handshake identity/verify + W3 materializer face "
          "[bands/identity/paths/prereg/cumulative-dep/spawn-carrier] "
          "+ W4 materializer face [same guard set, dep=W3] "
          "+ W5 materializer face [same guard set, dep=W4, A=skip-over "
          "per law sec.4 W5 row] + W6 materializer face [same guard set, "
          "dep=W5, B=skip-over per law sec.4 W6+ WARNING row] "
          "+ W7 materializer face [same guard set, dep=W6 in-flight="
          "runtime FAIL-CLOSED guard, BOTH bands skip-over per law "
          "sec.4 W7 row, r501 bm-b])")
    return 0


def main():
    argv = sys.argv[1:]
    if "--wave" in argv:
        w = int(argv[argv.index("--wave") + 1])
        if w not in WAVE_CONFIGS:
            print(f"unknown wave {w} (law sec.4 pre-assigned rows: "
                  f"{sorted(WAVE_CONFIGS)}; W5+ bands extend per-wave at "
                  f"prereg time, law sec.4 tail rows)")
            return 2
        _set_wave(w)
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
        print("usage: run --shard i --of N [--wave W] [--workers P] | "
              "finalize [--wave W] | probe | parity | status [--wave W] | "
              "selftest")
        return 2
    if "run" not in argv:
        print("usage: run --shard i --of N [--wave W] [--workers P]")
        return 2
    assert 0 <= shard < nshards, "shard out of range"
    return run_shard(shard, nshards, workers=_resolve_workers(argv))


if __name__ == "__main__":
    sys.exit(main())
