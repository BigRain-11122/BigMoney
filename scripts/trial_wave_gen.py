"""TRIAL-WAVE1-1000 s1: candidate generation engine + structural dedup gate.

Order chain: O-2026-09-27-2245-bm-a (T-2026-09-27-94, CEO immediate) +
TRIAL_LABOR_LAW v1.0 sec.1/3/4. Prereg FROZEN at
research/TRIAL_WAVE1_PREREG.md (commit precedes any burn, R99 law).

Zero new signal functions: candidates draw ONLY from the registered
SIGNAL_BUILDERS vocabulary (exact-string keys; live.paper contract:
unknown string -> hard abort, no silent fallback) x the frozen exit /
timing parameter space (bridge kwargs + ExitPatch fields). Entry-arg
randomization is wave-2 territory (registry-keyed vocabulary boundary,
prereg sec.3 honest deferral).

Draw bases: SEED_REGISTRY["trial_wave1"] = 20_920_000 (FAM-REV) /
20_920_001 (FAM-ROT); numpy default_rng(PCG64) uniform draws, no
hand-picked points (RANDOM_LARGE_SAMPLE_LAW sec.2.2).

Dedup gate (prereg sec.3):
  * generation face: sha256 over canonical JSON (entry+params+
    exit_overrides); collision -> re-draw, MAX_TRY_MULT x cap, honest
    shortfall if the discrete space saturates (ceiling, not quota).
  * report face: |corr|>=0.999 collapse happens downstream in the
    s2/s3 report faces (T-84 s3 law) -- this engine only guarantees
    structural distinctness.

Outputs:
  results/trial_wave1/candidates.jsonl  one candidate per line
  results/trial_wave1/manifest.json     counts/seed/grammar sha/dedup

selftest: offline determinism probe -- regenerate in memory, compare
fingerprint sequence against candidates.jsonl (zero dup, exact count,
schema fields). Exit 0 PASS / 1 FAIL.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SEED_BASE_REV = 20_920_000          # SEED_REGISTRY["trial_wave1"]
SEED_BASE_ROT = 20_920_001
N_PER_FAMILY = 500                  # RANDOM_LARGE_SAMPLE_LAW sec.2.2 (>=500/family)
MAX_TRY_MULT = 10                   # dedup re-draw cap -> honest shortfall
EVIDENCE_CUTOFF = "2026-09-22"      # P-5C frozen grid (prereg sec.2)

FAMILIES = [
    ("FAM-REV", "oversold_bounce(lookback=20, drop=-15%, shrink=0.8)",
     SEED_BASE_REV),
    ("FAM-ROT", "top_n_rotation(composite, n=5, rebal_days=20)",
     SEED_BASE_ROT),
]

# frozen draw space (prereg sec.3 -- do not touch after freeze commit)
TD_PERIOD_LO, TD_PERIOD_HI = 8, 35          # inclusive integers
TD_THRESH = (0.03, 0.09)
TSA_RANGE = (0.015, 0.07)
TLOCK_RANGE = (0.03, 0.10)
TP_LEVEL_RANGE = (0.04, 0.14)
TP_K_CHOICES = (1, 2, 3)
LOSS_TIME_CHOICES = (5, 7, 10, 16, 20)      # holding-period family + g2-folk 16

OUT_DIR = os.path.join("results", "trial_wave1")
OUT_CAND = os.path.join(OUT_DIR, "candidates.jsonl")
OUT_MANIFEST = os.path.join(OUT_DIR, "manifest.json")
PREREG_REF = "research/TRIAL_WAVE1_PREREG.md"


def _grammar_spec() -> dict:
    """Canonical grammar description -- hashed into the manifest."""
    return {
        "families": [
            {"family": f, "entry": e, "seed_base": s}
            for f, e, s in FAMILIES
        ],
        "draw_space": {
            "time_decay_period": [TD_PERIOD_LO, TD_PERIOD_HI, "int"],
            "time_decay_threshold": list(TD_THRESH),
            "trailing_stop_activate": list(TSA_RANGE),
            "trailing_lock": list(TLOCK_RANGE),
            "take_profit_levels": {"k": list(TP_K_CHOICES),
                                   "range": list(TP_LEVEL_RANGE)},
            "take_profit_fractions": "dirichlet-simplex-matching-k",
            "loss_time_days": list(LOSS_TIME_CHOICES),
        },
        "n_per_family": N_PER_FAMILY,
        "dedup": "structural sha256 canonical-json, redraw cap 10x",
        "seed_registry_key": "trial_wave1",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "prereg_ref": PREREG_REF,
    }


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _fingerprint(entry: str, params: dict, ovr: dict) -> str:
    return hashlib.sha256(
        _canon({"entry": entry, "params": params, "exit_overrides": ovr})
    ).hexdigest()


def _draw_fractions(rng, k: int) -> list:
    """k-length simplex draw, 3dp, residual landed on the largest leg."""
    raw = rng.dirichlet(np.ones(k))
    fr = [round(float(x), 3) for x in raw]
    resid = round(1.0 - sum(fr), 3)
    fr[int(np.argmax(fr))] = round(fr[int(np.argmax(fr))] + resid, 3)
    return fr


def _draw_one(rng) -> tuple:
    """One parameter draw -> (params, exit_overrides)."""
    td_period = int(rng.integers(TD_PERIOD_LO, TD_PERIOD_HI + 1))
    td_thresh = round(float(rng.uniform(*TD_THRESH)), 4)
    tsa = round(float(rng.uniform(*TSA_RANGE)), 4)
    tlock = round(float(rng.uniform(*TLOCK_RANGE)), 4)
    k = int(rng.choice(TP_K_CHOICES))
    levels = sorted(round(float(rng.uniform(*TP_LEVEL_RANGE)), 3)
                    for _ in range(k))
    while len(set(levels)) < k:            # 3dp tie -> redraw levels
        levels = sorted(round(float(rng.uniform(*TP_LEVEL_RANGE)), 3)
                        for _ in range(k))
    fracs = _draw_fractions(rng, k)
    ltd = int(rng.choice(LOSS_TIME_CHOICES))
    params = {
        "time_decay_period": td_period,
        "time_decay_threshold": td_thresh,
        "trailing_stop_activate": tsa,
        "take_profit_levels": levels,
        "trailing_lock": tlock,
    }
    ovr = {"loss_time_days": ltd, "take_profit_fractions": fracs}
    return params, ovr


def _validate_vocabulary() -> list:
    """Hard gate: family entry strings must be registered SIGNAL_BUILDERS."""
    import live.paper as lp
    vocab = set(lp.SIGNAL_BUILDERS.keys())
    missing = [e for _, e, _ in FAMILIES if e not in vocab]
    if missing:
        sys.stderr.write("FATAL: entry strings not in SIGNAL_BUILDERS: "
                         f"{missing}\n")
        sys.exit(2)
    return sorted(vocab)


def generate() -> int:
    vocab = _validate_vocabulary()
    os.makedirs(OUT_DIR, exist_ok=True)
    candidates, seen = [], {}
    stats = []
    for fam, entry, seed in FAMILIES:
        rng = np.random.default_rng(seed)
        fam_cands, tries, collisions = [], 0, 0
        max_tries = N_PER_FAMILY * MAX_TRY_MULT
        while len(fam_cands) < N_PER_FAMILY and tries < max_tries:
            tries += 1
            params, ovr = _draw_one(rng)
            fp = _fingerprint(entry, params, ovr)
            if fp in seen:
                collisions += 1
                continue
            seen[fp] = True
            fam_cands.append({
                "cand_id": f"TRIAL-W1-{fam.split('-')[1]}-"
                           f"{len(fam_cands) + 1:03d}",
                "family": fam,
                "entry": entry,
                "params": params,
                "exit_overrides": ovr,
                "fp": fp,
            })
        candidates.extend(fam_cands)
        stats.append({
            "family": fam, "entry": entry, "seed_base": seed,
            "drawn": len(fam_cands), "tries": tries,
            "collisions": collisions,
            "shortfall": max(0, N_PER_FAMILY - len(fam_cands)),
        })
    with open(OUT_CAND, "w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c, ensure_ascii=False, sort_keys=True)
                    + "\n")
    manifest = {
        "batch": "TRIAL-WAVE1-1000",
        "ticket_ref": "T-2026-09-27-94 s1",
        "prereg_ref": PREREG_REF,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "grammar_sha256": hashlib.sha256(_canon(_grammar_spec())).hexdigest(),
        "vocabulary_size": len(vocab),
        "n_candidates": len(candidates),
        "n_target": N_PER_FAMILY * len(FAMILIES),
        "families": stats,
        "dedup_law": "structural sha256 (gen face) + |corr|>=0.999 "
                     "collapse (report face, T-84 s3)",
        "note": "ceiling not quota: shortfalls honest; same-grammar "
                "no-rerun (TRIAL_GRAMMAR_REGISTRY)",
    }
    with open(OUT_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for s in stats:
        print(f"gen {s['family']}: {s['drawn']}/{N_PER_FAMILY} "
              f"(tries={s['tries']} collisions={s['collisions']} "
              f"shortfall={s['shortfall']})")
    print(f"TOTAL {len(candidates)} candidates -> {OUT_CAND}")
    return 0


def selftest() -> int:
    """Offline determinism probe: regenerate fp sequence, compare file."""
    n_fail = 0
    if not os.path.exists(OUT_CAND):
        print("selftest: SKIP (no candidates.jsonl yet -- run gen first)")
        return 0
    with open(OUT_CAND, encoding="utf-8") as f:
        rows = [json.loads(x) for x in f if x.strip()]
    regen = []
    for fam, entry, seed in FAMILIES:
        rng = np.random.default_rng(seed)
        fam_seen, fam_cands = set(), []
        tries = 0
        while len(fam_cands) < N_PER_FAMILY and tries < N_PER_FAMILY * MAX_TRY_MULT:
            tries += 1
            params, ovr = _draw_one(rng)
            fp = _fingerprint(entry, params, ovr)
            if fp in fam_seen:
                continue
            fam_seen.add(fp)
            fam_cands.append(fp)
        regen.extend(fam_cands)
    got = [r["fp"] for r in rows]
    if got != regen:
        print("selftest: FAIL fp sequence diverges from file")
        n_fail += 1
    if len(set(got)) != len(got):
        print("selftest: FAIL duplicate fingerprints present")
        n_fail += 1
    fam_counts = {}
    for r in rows:
        fam_counts[r["family"]] = fam_counts.get(r["family"], 0) + 1
        for k in ("cand_id", "family", "entry", "params",
                  "exit_overrides", "fp"):
            if k not in r:
                print(f"selftest: FAIL schema field {k} missing")
                n_fail += 1
                break
        if r["entry"] not in [e for _, e, _ in FAMILIES]:
            print(f"selftest: FAIL entry outside frozen families {r['entry']}")
            n_fail += 1
    print(f"selftest: family counts {fam_counts}")
    print(f"trial_wave_gen selftest: "
          f"{3 - n_fail if n_fail < 3 else 0}/3 PASS, {n_fail} FAIL")
    return 1 if n_fail else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["gen", "selftest"])
    args = ap.parse_args()
    if args.cmd == "gen":
        return generate()
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
