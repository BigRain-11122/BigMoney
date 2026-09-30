"""P2 null-calibration K-lift extension (CEO O-20260930-2054 sec.1 e-item /
O-20260930-1858 sec.2.e -- science-face investment: nulls/baseline sample
expansion, K value increase).

Extends the FROZEN null design (research/NULL_CALIBRATION.md v1.0, frozen
2026-09-23 pre-run; v2 = same design re-executed on the fixed engine, RW-6,
results/p2_calibration_v2.json) with NEW seeds -- same 48-symbol bare-code
core48 universe, same window (evidence_cutoff 2026-09-22 hard truncation),
same engine (run_backtest via p2_null_calibration.run_one), same single-source
FeeSchedule cost:

  family A ext: 2,000 random-entry x engine-exit runs, j = 0..1999
                entry rng seed = 10_100 + j   (range 10_100..12_099)
                p_entry = BASELINE_P[(j // 50) % 2]  (50-seed block alternation
                continues the v1 pattern {0.02, 0.05})
  family B ext:   200 paired random-entry + random-exit runs, j = 0..199
                entry rng = 10_100 + j (SAME entry matrix as A-ext[j],
                pairing semantics preserved), exit rng = 20_100 + j
                (range 20_100..20_299), p_exit = P_EXIT = 0.05

Seed discipline: v1 in-use ranges are 10_000..10_099 / 20_000..20_019; the
extension bands are disjoint from those AND from every SEED_REGISTRY value
(selftest leg). No passive re-run (family C identical by construction,
v2 note verbatim). Canon files results/p2_calibration{,_v2}.json are NOT
touched by any subcommand.

Subcommands:
  --shard i --nshards N   burn this shard's contiguous slice of A-ext + B-ext,
                          single deterministic pass, writes
                          results/p2cal_ext/shard-<i>-of-<N>.json (overwrite-
                          idempotent; re-run reproduces byte-equal runs)
  finalize                merge all shard files (FAIL-CLOSED on missing
                          shards), derive extended pool (canon 120 + ext
                          2,200), old-vs-new mu/sigma and skill_line_v2 at
                          the SAME n_eff (v2 attribution law), append ledger
                          +2,200 (new-seed null trials; FUSION_GRID null-
                          counting precedent), write
                          results/p2_calibration_v2_ext.json. Canon flip is
                          NOT performed here -- follow-on governance proposal
                          with the old-vs-new numbers.
  probe                   2-run end-to-end design probe at out-of-band seeds
                          (40_000 / 40_001) -- design verification only, not a
                          batch trial, ledger +0, writes
                          results/_p2cal_ext_probe.json
  selftest                offline hermetic checks (constants, seed bands,
                          slice math, canon intact, no network, no panel)
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from config import PATHS
import science_gates as sg

CUTOFF = "2026-09-22"          # v1/v2 canon window end -- frozen, same-window law
A_EXT_N = 2000                 # pre-registered (prereg sec.3)
B_EXT_N = 200                  # pre-registered (prereg sec.3)
A_SEED_BASE = 10_100           # 10_100 + j, j = 0..1999
B_EXIT_SEED_BASE = 20_100      # 20_100 + j, j = 0..199
PROBE_ENTRY_SEED = 95_000      # out-of-band (design probe only)
PROBE_EXIT_SEED = 95_001
SHARD_DIR = os.path.join(PATHS.results_dir, "p2cal_ext")
EXT_OUT = os.path.join(PATHS.results_dir, "p2_calibration_v2_ext.json")
PROBE_OUT = os.path.join(PATHS.results_dir, "_p2cal_ext_probe.json")


def p_for(j: int) -> float:
    """Entry-frequency block pattern: continues the v1 50-seed alternation."""
    import p2_null_calibration as v1
    return v1.BASELINE_P[(j // 50) % 2]


def load_core_at_cutoff(min_listing_days: int = 60) -> dict:
    """v2 semantics verbatim: v1 load + hard truncation at the frozen cutoff."""
    import p2_null_calibration as v1
    out = {}
    ps = pd.Timestamp(CUTOFF)
    for code, df in v1.load_core(min_listing_days).items():
        out[code] = df[df.index <= ps]
    return out


def _assemble():
    """Shared assembly: panel, union index, ffill closes, fee cost rate."""
    import p2_null_calibration as v1
    from knowledge.rules import FeeSchedule

    prices = load_core_at_cutoff()
    n_syms = len(prices)
    assert n_syms == 48, f"universe drift: {n_syms} != 48 bare codes (FAIL-CLOSED)"
    idx_all = sorted({d for df in prices.values() for d in df.index})
    idx = pd.DatetimeIndex(idx_all)
    closes = pd.DataFrame(
        {s: df["close"] for s, df in prices.items()}).reindex(idx).sort_index().ffill()
    fee = FeeSchedule()
    cost_rate = (fee.commission_rate + fee.handling_fee +
                 fee.supervision_fee + fee.slippage_a)
    return v1, prices, idx, closes, cost_rate


def _entry_matrix(rng, n_days, n_syms, idx, cols, p):
    return pd.DataFrame((rng.random((n_days, n_syms)) < p).astype(int),
                         index=idx, columns=cols)


def run_shard(shard: int, nshards: int) -> int:
    v1, prices, idx, closes, cost_rate = _assemble()
    n_days, n_syms = closes.shape
    cols = list(closes.columns)
    t0 = time.time()

    a_lo, a_hi = shard * A_EXT_N // nshards, (shard + 1) * A_EXT_N // nshards
    b_lo, b_hi = shard * B_EXT_N // nshards, (shard + 1) * B_EXT_N // nshards

    fam_a = []
    for j in range(a_lo, a_hi):
        p = p_for(j)
        rng = np.random.default_rng(A_SEED_BASE + j)
        entry = _entry_matrix(rng, n_days, n_syms, idx, cols, p)
        exit_ = pd.DataFrame(False, index=idx, columns=cols)
        r = v1.run_one(prices, idx, entry, exit_, {}, f"extA_p{p}_j{j}")
        fam_a.append({**r, "p": p, "seed_rng": A_SEED_BASE + j,
                      "note": f"ext random entry p={p} rng={A_SEED_BASE + j}; "
                              f"exits=engine rules (v1 design verbatim)"})
        print(f"  A[j{j}] full_s={r['full']['sharpe']:>7.3f} "
              f"({time.time()-t0:.0f}s)", flush=True)

    fam_b = []
    for j in range(b_lo, b_hi):
        p = p_for(j)
        rng = np.random.default_rng(A_SEED_BASE + j)      # SAME matrix as A-ext[j]
        entry = _entry_matrix(rng, n_days, n_syms, idx, cols, p)
        rng_x = np.random.default_rng(B_EXIT_SEED_BASE + j)
        exit_ = pd.DataFrame((rng_x.random((n_days, n_syms)) < v1.P_EXIT),
                             index=idx, columns=cols)
        r = v1.run_one(prices, idx, entry, exit_, {}, f"extB_p{p}_j{j}")
        fam_b.append({**r, "p": p, "seed_rng_entry": A_SEED_BASE + j,
                      "seed_rng_exit": B_EXIT_SEED_BASE + j,
                      "note": f"ext random entry rng={A_SEED_BASE + j} "
                              f"(paired with extA_j{j}) + random exit "
                              f"rng={B_EXIT_SEED_BASE + j} p={v1.P_EXIT}"})
        print(f"  B[j{j}] full_s={r['full']['sharpe']:>7.3f} "
              f"({time.time()-t0:.0f}s)", flush=True)

    os.makedirs(SHARD_DIR, exist_ok=True)
    out = {
        "batch": "P2-NULL-CALIB-EXT-K2200",
        "preregistered_doc": "research/P2_NULL_KLIFT_PREREG.md (frozen pre-run; "
                             "design = NULL_CALIBRATION.md v1.0 verbatim + v2 "
                             "fixed-engine law, new seed bands only)",
        "evidence_cutoff": CUTOFF,
        "shard": shard, "nshards": nshards,
        "a_range": [a_lo, a_hi], "b_range": [b_lo, b_hi],
        "families": {"A_random_engine_exit": {"n": len(fam_a), "runs": fam_a},
                     "B_random_entry_random_exit": {"n": len(fam_b), "runs": fam_b}},
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": len(fam_a) + len(fam_b),
                  "workers": 1, "cpu_parallel": "serial (single-process)",
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


def finalize() -> int:
    import glob
    shard_files = sorted(glob.glob(os.path.join(
        SHARD_DIR, "shard-*-of-*.json")))
    if not shard_files:
        print("finalize: FAIL-CLOSED -- no shard files under results/p2cal_ext/")
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
    done = {(d_["shard"]) for d_ in (json.load(open(sf, encoding="utf-8"))
                                     for sf in shard_files)}
    if done != set(range(nshards)):
        print(f"finalize: FAIL-CLOSED -- shards {sorted(done)} != "
              f"0..{nshards-1} (missing shards, burn not complete)")
        return 2
    if len(a_runs) != A_EXT_N or len(b_runs) != B_EXT_N:
        print(f"finalize: FAIL-CLOSED -- A {len(a_runs)} != {A_EXT_N} or "
              f"B {len(b_runs)} != {B_EXT_N} (slice overlap/gap)")
        return 2
    if len({r["name"] for r in a_runs}) != A_EXT_N or \
       len({r["name"] for r in b_runs}) != B_EXT_N:
        print("finalize: FAIL-CLOSED -- duplicate run names")
        return 2

    v2_pool = sg.null_sharpes()          # canon read (120 values, untouched)
    v2_cov = v2_pool["coverage"]
    ext_values = [float(r["full"]["sharpe"]) for r in a_runs + b_runs]
    merged_values = list(v2_pool["values"]) + ext_values
    cov_ext = {"n_values": len(ext_values),
               "schemas_parsed": ["p2cal_ext shard merge: families[*].runs[]."
                                  "full.sharpe (new seed bands 10_100+j / "
                                  "20_100+j)"],
               "known_unparsed": [],
               "mu": sum(ext_values) / len(ext_values),
               "sigma": sg._pstdev(ext_values)}
    cov_merged = {"n_values": len(merged_values),
                  "schemas_parsed": ["p2_calibration_v2 canon (120) + "
                                     "p2cal_ext merge (2200)"],
                  "known_unparsed": [],
                  "mu": sum(merged_values) / len(merged_values),
                  "sigma": sg._pstdev(merged_values)}

    # line recompute at the SAME n_eff on both sides (v2 attribution law)
    line_old = sg.skill_line_v2(batch_cells=0, null_pool=v2_pool)
    line_new = sg.skill_line_v2(
        batch_cells=0, null_pool={"values": merged_values, "coverage": cov_merged})

    led = sg.append_ledger("P2-NULL-CALIB-EXT-K2200", A_EXT_N + B_EXT_N,
                           "p2_calibration_v2_ext.json",
                           note="null baseline K-lift (CEO O-2054 e-item): "
                                "2,200 new-seed null trials, frozen v1/v2 "
                                "design, window 2026-09-22",
                           evidence_cutoff=CUTOFF)

    a_full = [float(r["full"]["sharpe"]) for r in a_runs]
    b_full = [float(r["full"]["sharpe"]) for r in b_runs]
    se_mu_v2 = (v2_cov["sigma"] or 0.0) / (v2_cov["n_values"] ** 0.5)
    out = {
        "batch": "P2-NULL-CALIB-EXT-K2200",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/P2_NULL_KLIFT_PREREG.md",
        "evidence_cutoff": CUTOFF,
        "science_gates": {"cutoff_meta": {"evidence_cutoff": CUTOFF,
                                          "source": "frozen v1/v2 canon window "
                                                    "(same-window law)"},
                          "ledger": led},
        "universe": {"pool": "core48-bare-codes", "n_syms": 48,
                     "history": f"2020-01-02 .. {CUTOFF} (hard truncation)"},
        "families": {
            "A_random_engine_exit": {
                "n": A_EXT_N,
                "full_sharpe_p95": round(float(np.percentile(a_full, 95)), 4),
                "full_sharpe_mu": round(sum(a_full) / len(a_full), 6),
                "runs": a_runs},
            "B_random_entry_random_exit": {"n": B_EXT_N, "runs": b_runs},
            "C_passive": {"note": "not re-run -- identical to v2 family C by "
                                  "construction (v2 note verbatim)"},
        },
        "null_pool_old_vs_new": {
            "v2_canon": {"n_values": v2_cov["n_values"], "mu": v2_cov["mu"],
                         "sigma": v2_cov["sigma"],
                         "se_mu_at_k120": round(se_mu_v2, 6)},
            "ext_only": {"n_values": cov_ext["n_values"], "mu": cov_ext["mu"],
                         "sigma": cov_ext["sigma"]},
            "merged": {"n_values": cov_merged["n_values"],
                       "mu": cov_merged["mu"], "sigma": cov_merged["sigma"]},
            "mu_delta_merged_vs_canon": round(
                cov_merged["mu"] - v2_cov["mu"], 6),
            "sigma_delta_merged_vs_canon": round(
                cov_merged["sigma"] - v2_cov["sigma"], 6),
        },
        "skill_line_v2_old_vs_new": {
            "n_eff_held_equal": line_old["n_eff"],
            "canon_line_at_same_neff": line_old["line"],
            "merged_line_at_same_neff": line_new["line"],
            "line_delta_k_lift": round(line_new["line"] - line_old["line"], 4),
            "passive_term": line_new.get("passive"),
            "formula": "max(passive+0.10, mu + sigma*sqrt(2*ln N_eff))",
            "canon_flip": "NOT performed by this batch -- follow-on governance "
                          "proposal consumes these numbers (prereg sec.4)",
        },
        "shards_consumed": [os.path.basename(s) for s in shard_files],
        "audit": {"machine": json.loads(open(
            os.path.join(PATHS.root, "fleet", "machine.json"),
            encoding="utf-8").read()).get("machine_id", "unknown"),
            "finalize_only": True},
    }
    with open(EXT_OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, default=str)
    print(f"canon  mu={v2_cov['mu']:.4f} sigma={v2_cov['sigma']:.4f} "
          f"(K={v2_cov['n_values']})")
    print(f"ext    mu={cov_ext['mu']:.4f} sigma={cov_ext['sigma']:.4f} "
          f"(K={cov_ext['n_values']})")
    print(f"merged mu={cov_merged['mu']:.4f} sigma={cov_merged['sigma']:.4f} "
          f"(K={cov_merged['n_values']})")
    print(f"skill_line_v2 @n_eff={line_old['n_eff']}: {line_old['line']} -> "
          f"{line_new['line']} (K-lift delta "
          f"{line_new['line']-line_old['line']:+.4f})")
    print(f"ledger: {led}")
    print(f"saved: {EXT_OUT}")
    return 0


def probe() -> int:
    """2-run end-to-end design probe at out-of-band seeds. Ledger +0."""
    v1, prices, idx, closes, cost_rate = _assemble()
    n_days, n_syms = closes.shape
    cols = list(closes.columns)
    t0 = time.time()
    runs = []
    for name, seed, p, with_exit in (
            ("probeA", PROBE_ENTRY_SEED, v1.BASELINE_P[0], False),
            ("probeB", PROBE_EXIT_SEED, v1.BASELINE_P[1], True)):
        rng = np.random.default_rng(seed)
        entry = _entry_matrix(rng, n_days, n_syms, idx, cols, p)
        if with_exit:
            rng_x = np.random.default_rng(PROBE_EXIT_SEED)
            exit_ = pd.DataFrame((rng_x.random((n_days, n_syms)) < v1.P_EXIT),
                                 index=idx, columns=cols)
        else:
            exit_ = pd.DataFrame(False, index=idx, columns=cols)
        r = v1.run_one(prices, idx, entry, exit_, {}, name)
        runs.append({**r, "p": p, "seed_rng": seed,
                     "random_exit": with_exit})
        print(f"  {name} full_s={r['full']['sharpe']:>7.3f} "
              f"n_trades={r['n_trades']}")
    # seed determinism re-check (probe leg)
    rng = np.random.default_rng(PROBE_ENTRY_SEED)
    m1 = (rng.random((3, 3)) < 0.5).astype(int)
    rng = np.random.default_rng(PROBE_ENTRY_SEED)
    m2 = (rng.random((3, 3)) < 0.5).astype(int)
    assert (m1 == m2).all(), "probe seed drift"
    out = {"batch": "P2-NULL-CALIB-EXT-K2200-probe", "evidence_cutoff": CUTOFF,
           "note": "design verification only, out-of-band seeds 95_000/95_001; "
                   "NOT batch trials; ledger +0",
           "universe_syms": n_syms, "panel_end": str(idx[-1].date()),
           "runs": runs, "elapsed_sec": round(time.time() - t0, 1)}
    with open(PROBE_OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, default=str)
    print(f"saved: {PROBE_OUT} ({out['elapsed_sec']}s)")
    return 0


def selftest() -> int:
    import p2_null_calibration as v1
    # 1. design constants inherited verbatim
    assert v1.N_BASELINES == 100 and v1.N_PAIRED == 20
    assert v1.BASELINE_P == [0.02, 0.05] and v1.P_EXIT == 0.05
    # 2. seed bands disjoint from v1 in-use ranges and SEED_REGISTRY values
    v1_a = {10_000 + k for k in range(v1.N_BASELINES)}
    v1_b = {20_000 + k for k in range(v1.N_PAIRED)}
    ext_a = {A_SEED_BASE + j for j in range(A_EXT_N)}
    ext_bx = {B_EXIT_SEED_BASE + j for j in range(B_EXT_N)}
    assert not (ext_a & v1_a) and not (ext_bx & v1_b), "seed band overlap v1"
    assert not (ext_a & ext_bx), "A entry band overlaps B exit band"
    reg = sg.SEED_REGISTRY
    reg_ints = {v for v in reg.values() if isinstance(v, (int, float))}
    assert not (ext_a & reg_ints) and not (ext_bx & reg_ints), \
        "seed band collides with SEED_REGISTRY"
    probe_seeds = {PROBE_ENTRY_SEED, PROBE_EXIT_SEED}
    assert not (probe_seeds & reg_ints), "probe seed in SEED_REGISTRY"
    # 3. p block pattern continuation
    assert [p_for(j) for j in (0, 49, 50, 99, 100, 149, 150)] == \
        [0.02, 0.02, 0.05, 0.05, 0.02, 0.02, 0.05]
    # 4. seed determinism
    rng = np.random.default_rng(A_SEED_BASE + 0)
    m1 = (rng.random((3, 2)) < 0.5).astype(int)
    rng = np.random.default_rng(A_SEED_BASE + 0)
    m2 = (rng.random((3, 2)) < 0.5).astype(int)
    assert (m1 == m2).all(), "seed drift"
    # 5. shard slice math: contiguous, no gap/overlap, totals exact
    for nshards in (1, 2, 4, 5):
        a_ranges = [(i * A_EXT_N // nshards, (i + 1) * A_EXT_N // nshards)
                    for i in range(nshards)]
        assert a_ranges[0][0] == 0 and a_ranges[-1][1] == A_EXT_N
        for (lo1, hi1), (lo2, hi2) in zip(a_ranges, a_ranges[1:]):
            assert hi1 == lo2, "A slice gap/overlap"
        b_ranges = [(i * B_EXT_N // nshards, (i + 1) * B_EXT_N // nshards)
                    for i in range(nshards)]
        assert b_ranges[0][0] == 0 and b_ranges[-1][1] == B_EXT_N
        for (lo1, hi1), (lo2, hi2) in zip(b_ranges, b_ranges[1:]):
            assert hi1 == lo2, "B slice gap/overlap"
    # 6. canon files present and intact (shape only, no mutation)
    canon = json.load(open(os.path.join(PATHS.results_dir,
                                        "p2_calibration.json"), encoding="utf-8"))
    assert canon["universe"]["n_syms"] == 48
    assert canon["universe"]["history"].endswith(CUTOFF)
    cov = sg.null_sharpes()["coverage"]
    assert cov["n_values"] == 120 and cov["mu"] is not None
    # 7. output paths: ext never writes canon files
    assert os.path.abspath(EXT_OUT) != os.path.abspath(
        os.path.join(PATHS.results_dir, "p2_calibration_v2.json"))
    assert os.path.abspath(EXT_OUT) != os.path.abspath(
        os.path.join(PATHS.results_dir, "p2_calibration.json"))
    print("selftest: PASS (design constants + seed bands disjoint + p pattern "
          "+ determinism + slice math + canon intact + path safety)")
    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "selftest" in argv:
        sys.exit(selftest())
    if "finalize" in argv:
        sys.exit(finalize())
    if "probe" in argv:
        sys.exit(probe())
    shard = nshards = None
    if "--shard" in argv:
        shard = int(argv[argv.index("--shard") + 1])
    if "--nshards" in argv:
        nshards = int(argv[argv.index("--nshards") + 1])
    if shard is None or nshards is None:
        print(__doc__)
        print("usage: --shard i --nshards N | finalize | probe | selftest")
        sys.exit(2)
    assert 0 <= shard < nshards, "shard out of range"
    sys.exit(run_shard(shard, nshards))
