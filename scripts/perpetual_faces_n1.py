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
    # W8 (r312 bm-c, forced-skip family -- the law sec.4 pinned W8+
    # WARNING window itself is gate-refused): A's arithmetic +2_000
    # tail (28_100..30_099) is documented-refused -- it hits the W7 B
    # band (28_100..28_299) AND the SEED_REGISTRY lfc_p1_screen point
    # 30_000 (actual draw range 30_000..30_099, N_RAND=50 x 2 exit
    # regimes); the law-pinned first-free prediction (28_300..30_299)
    # is refused by the same registry point + actual range -- so A
    # packs at the first 2,000-window clear of every reserved band AND
    # the lfc actual draw range (30_100..32_099); B's arithmetic +200
    # tail (28_300..28_499) is clean this wave (the A jump cleared the
    # predicted collision) and keeps the stride verbatim. NOT a re-pick
    # (R250). N2/N4 yield note: this A band covers the 30_000+ domain;
    # N2-W15 draft probe bands (31_000/31_500/32_000) must re-pick at
    # their freeze per law sec.4 (MSG heads-up sent r312).
    8: {"batch": "PERPETUAL-N1-W8",
        "prereg": ("research/PERPETUAL_N1_W8_PREREG.md (wave-level frozen "
                   "pre-run; design = frozen v1 null calibration verbatim, "
                   "new seed bands only)"),
        "a_seed_base": 30_100,           # law sec.4 W8 A: 30_100..32_099 (skip-over)
        "b_exit_seed_base": 28_300,      # law sec.4 W8 B: 28_300..28_499 (arithmetic)
        "shard_subdir": "n1_w8", "out_name": "n1_w8_results.json"},
    # W9 (r506 bm-b, O-20261001-1332 sec.1.2 supply step): BOTH arithmetic
    # tails land clean exactly as the W8 row projected (A 32_100 == W8 A
    # end + 1, B 28_500 == W8 B end + 1) -- no forced skip this wave;
    # machine-verified at prereg time (results/_r506bmb_w9_band_gate.py
    # ADMIT receipt). NOT a re-pick (R250). N2/N4 preregs must steer
    # clear of 32_100..34_099 per law sec.4.
    9: {"batch": "PERPETUAL-N1-W9",
        "prereg": ("research/PERPETUAL_N1_W9_PREREG.md (wave-level frozen "
                   "pre-run; design = frozen v1 null calibration verbatim, "
                   "new seed bands only)"),
        "a_seed_base": 32_100,           # law sec.4 W9 A: 32_100..34_099 (arithmetic)
        "b_exit_seed_base": 28_500,      # law sec.4 W9 B: 28_500..28_699 (arithmetic)
        "shard_subdir": "n1_w9", "out_name": "n1_w9_results.json"},
    # W10 (r508 bm-b, T-2026-10-01-141 s1 FIRST ENGINE-OWNED WAVE:
    # engine_owner=bm-b -> burned by scripts/saturation_engine.py local
    # perpetual queue, NEVER materialized into the pool by cmd_supply
    # (engine-owner skip gate, SATURATION_ENGINE_LAW sec.1/sec.2 -- zero
    # cross-machine duplication). BOTH arithmetic tails land clean
    # exactly as the W9 row projected (A 34_100 == W9 A end + 1,
    # B 28_700 == W9 B end + 1) -- no forced skip this wave; machine-
    # verified at prereg time (results/_r508bmb_w10_band_gate.py ADMIT
    # receipt). NOT a re-pick (R250).
    10: {"batch": "PERPETUAL-N1-W10",
         "prereg": ("research/PERPETUAL_N1_W10_PREREG.md (wave-level frozen "
                    "pre-run; design = frozen v1 null calibration verbatim, "
                    "new seed bands only; FIRST ENGINE-OWNED WAVE "
                    "T-2026-10-01-141 s1, engine_owner=bm-b)"),
         "a_seed_base": 34_100,          # law sec.4 W10 A: 34_100..36_099 (arithmetic)
         "b_exit_seed_base": 28_700,     # law sec.4 W10 B: 28_700..28_899 (arithmetic)
         "shard_subdir": "n1_w10", "out_name": "n1_w10_results.json",
         "engine_owner": "bm-b"},
    # W11 (r510 bm-b, never-dry supply law: SECOND ENGINE-OWNED WAVE,
    # engine_owner=bm-b -> burned by scripts/saturation_engine.py local
    # perpetual queue, NEVER materialized into the pool by cmd_supply
    # (engine-owner skip gate, SATURATION_ENGINE_LAW sec.1/sec.2 -- zero
    # cross-machine duplication). BOTH arithmetic tails land clean
    # exactly as the W10 row projected (A 36_100 == W10 A end + 1,
    # B 28_900 == W10 B end + 1) -- no forced skip this wave; machine-
    # verified at prereg time (results/_r510bmb_w11_band_gate.py ADMIT
    # receipt, pre-W11 9-row state + 158 registry values + lfc range).
    # NOT a re-pick (R250).
    11: {"batch": "PERPETUAL-N1-W11",
         "prereg": ("research/PERPETUAL_N1_W11_PREREG.md (wave-level frozen "
                    "pre-run; design = frozen v1 null calibration verbatim, "
                    "new seed bands only; SECOND ENGINE-OWNED WAVE, "
                    "never-dry supply law, engine_owner=bm-b)"),
         "a_seed_base": 36_100,          # law sec.4 W11 A: 36_100..38_099 (arithmetic)
         "b_exit_seed_base": 28_900,     # law sec.4 W11 B: 28_900..29_099 (arithmetic)
         "shard_subdir": "n1_w11", "out_name": "n1_w11_results.json",
         "engine_owner": "bm-b"},
    # W12 (r523 bm-a, never-dry supply law: THIRD ENGINE-OWNED WAVE, first
    # bm-a-owned engine wave -> burned by scripts/saturation_engine.py local
    # perpetual queue, NEVER materialized into the pool by cmd_supply
    # (engine-owner skip gate, SATURATION_ENGINE_LAW sec.1/sec.2 -- zero
    # cross-machine duplication). A's arithmetic +2_000 tail (38_100..40_099)
    # is REFUSED per the W11 row's WARNING projection -- it hits the N2/N4
    # design-probe reserved points 40_000/40_001 AND SEED_REGISTRY
    # new_signal_p1 40_000 / new_signal_p1_ce 40_050; A packs at the first
    # 2,000-window clear of every reserved band + actual draw range
    # (63_050..65_049, options_wave2 actual 63_000..63_049 avoided); B's
    # arithmetic +200 tail (29_100..29_299, W11 B end + 1) lands clean and
    # keeps the stride verbatim. Machine-verified at prereg time
    # (results/_r523bma_w12_band_gate.py ADMIT receipt). Skip is FORCED
    # (leg1 arithmetic-tail REFUSED evidence), NOT a re-pick (R250).
    12: {"batch": "PERPETUAL-N1-W12",
         "prereg": ("research/PERPETUAL_N1_W12_PREREG.md (wave-level frozen "
                    "pre-run; design = frozen v1 null calibration verbatim, "
                    "new seed bands only; THIRD ENGINE-OWNED WAVE, "
                    "never-dry supply law, engine_owner=bm-a)"),
         "a_seed_base": 63_050,          # law sec.4 W12 A: 63_050..65_049 (skip-over)
         "b_exit_seed_base": 29_100,     # law sec.4 W12 B: 29_100..29_299 (arithmetic)
         "shard_subdir": "n1_w12", "out_name": "n1_w12_results.json",
         "engine_owner": "bm-a"},
    # W13 (r512 bm-b, never-dry supply law standing step = the r512
    # watermark-red anti-idle root fix: FOURTH ENGINE-OWNED WAVE,
    # engine_owner=bm-b -- bm-b's third owned wave after W10/W11, W12=bm-a
    # in flight at freeze time -> burned by scripts/saturation_engine.py
    # local perpetual queue, NEVER materialized into the pool by cmd_supply
    # (engine-owner skip gate, SATURATION_ENGINE_LAW sec.1/sec.2 -- zero
    # cross-machine duplication). A's arithmetic +2_000 tail
    # (65_050..67_049) is REFUSED per the W12 row's WARNING projection --
    # it hits the SEED_REGISTRY cluster bond_carry_w3a 66_000 /
    # p1e_zoo_behavior 67_000; A packs at the first 2,000-window clear of
    # every reserved band AND the actual draw ranges (70_001..72_000);
    # B's arithmetic +200 tail (29_300..29_499, W12 B end + 1) lands clean
    # and keeps the stride verbatim. Machine-verified at prereg time
    # (results/_r512bmb_w13_band_gate.py ADMIT receipt). Skip is FORCED
    # (leg1 arithmetic-tail REFUSED evidence), NOT a re-pick (R250).
    13: {"batch": "PERPETUAL-N1-W13",
         "prereg": ("research/PERPETUAL_N1_W13_PREREG.md (wave-level frozen "
                    "pre-run; design = frozen v1 null calibration verbatim, "
                    "new seed bands only; FOURTH ENGINE-OWNED WAVE, "
                    "never-dry supply law, engine_owner=bm-b)"),
         "a_seed_base": 70_001,          # law sec.4 W13 A: 70_001..72_000 (skip-over)
         "b_exit_seed_base": 29_300,     # law sec.4 W13 B: 29_300..29_499 (arithmetic)
         "shard_subdir": "n1_w13", "out_name": "n1_w13_results.json",
         "engine_owner": "bm-b"},
    # W14 (r325 bm-c, never-dry supply law standing step = the r325
    # watermark-red runnable-work-idle-low-cpu root fix; sovereignty
    # rotation law F-20261001-01 slot W14=bm-c -- bm-c's FIRST owned
    # engine wave): BOTH arithmetic tails land clean exactly as the W13
    # row's W14+ WARNING projected (A 72_001 == W13 A end + 1, B 29_500 ==
    # W13 B end + 1) -- no forced skip this wave; machine-verified at
    # prereg time (results/_r325bmc_w14_band_gate.py ADMIT receipt,
    # 12-row N1_BANDS + 158 registry values + lfc/options actual ranges).
    # Burned by the engine local perpetual queue, NEVER materialized
    # into the pool by cmd_supply (engine-owner skip gate,
    # SATURATION_ENGINE_LAW sec.1/sec.2 -- zero cross-machine
    # duplication). NOT a re-pick (R250). W15+ WARNING: A +2_000
    # arithmetic tail 74_001..76_000 and B +200 tail 29_700..29_899
    # project clean -- verify at W15 prereg time as always (W15=bm-a).
    14: {"batch": "PERPETUAL-N1-W14",
         "prereg": ("research/PERPETUAL_N1_W14_PREREG.md (wave-level frozen "
                    "pre-run; design = frozen v1 null calibration verbatim, "
                    "new seed bands only; FIFTH ENGINE-OWNED WAVE, "
                    "sovereignty rotation law W14=bm-c, engine_owner=bm-c)"),
         "a_seed_base": 72_001,          # law sec.4 W14 A: 72_001..74_000 (arithmetic)
         "b_exit_seed_base": 29_500,     # law sec.4 W14 B: 29_500..29_699 (arithmetic)
         "shard_subdir": "n1_w14", "out_name": "n1_w14_results.json",
         "engine_owner": "bm-c"},
    # W16 (r515 bm-b, prereg-time extension per the W14 row's W15+
    # WARNING -- never-dry supply law standing step / r515 watermark-red
    # anti-idle root fix; sovereignty rotation law F-20261001-01 slot
    # W13=bm-b anchored +3 -> W16=bm-b; unified wave number 15 held by
    # bm-a's N2-W15 draft (seed domain 30_000+/40_000+ per law sec.4
    # N2/N4 row, disjoint from this band) -- N1 face numbering continues
    # at W16 with no W15 row): BOTH arithmetic tails land clean exactly
    # as the W14 row projected (A 74_001 == W14 A end + 1, B 29_700 ==
    # W14 B end + 1); machine-verified at prereg time
    # (results/_r515bmb_w16_band_gate.py ADMIT receipt). SIXTH
    # ENGINE-OWNED WAVE, bm-b's fourth.
    16: {"batch": "PERPETUAL-N1-W16",
         "prereg": ("research/PERPETUAL_N1_W16_PREREG.md (wave-level frozen "
                    "pre-run; design = frozen v1 null calibration verbatim, "
                    "new seed bands only; SIXTH ENGINE-OWNED WAVE, "
                    "sovereignty rotation law W16=bm-b, engine_owner=bm-b)"),
         "a_seed_base": 74_001,          # law sec.4 W16 A: 74_001..76_000 (arithmetic)
         "b_exit_seed_base": 29_700,     # law sec.4 W16 B: 29_700..29_899 (arithmetic)
         "shard_subdir": "n1_w16", "out_name": "n1_w16_results.json",
         "engine_owner": "bm-b"},
    # W17 (r328 bm-c, prereg-time extension per the W16 row's W17+
    # WARNING -- never-dry supply law standing step / r328 watermark-red
    # anti-idle root fix; sovereignty rotation law F-20261001-01 slot
    # W14=bm-c anchored +3 -> W17=bm-c, bm-c's SECOND owned wave): SPLIT
    # tails -- A's arithmetic +2_000 tail (76_001 == W16 A end + 1)
    # lands clean (stride kept verbatim, no skip); B's arithmetic +200
    # tail (29_900..30_099) is REFUSED as the W16 row projected (lfc
    # actual draw 30_000..30_099, SEED_REGISTRY lfc_p1_screen=30_000) --
    # B re-bases past every reserved band incl. this wave's own A band,
    # packing at the first clean 200-window (38_100..38_299, W11 A end
    # + 1) per the W5/W6/W8/W12 forced-skip-over family; skip FORCED per
    # leg1-B refusal facts, NOT a re-pick (R250). Machine-verified at
    # prereg time (results/_r328bmc_w17_band_gate.py ADMIT receipt).
    # SEVENTH ENGINE-OWNED WAVE.
    17: {"batch": "PERPETUAL-N1-W17",
         "prereg": ("research/PERPETUAL_N1_W17_PREREG.md (wave-level frozen "
                    "pre-run; design = frozen v1 null calibration verbatim, "
                    "new seed bands only; SEVENTH ENGINE-OWNED WAVE, "
                    "sovereignty rotation law W17=bm-c, engine_owner=bm-c)"),
         "a_seed_base": 76_001,          # law sec.4 W17 A: 76_001..78_000 (arithmetic)
         "b_exit_seed_base": 38_100,     # law sec.4 W17 B: 38_100..38_299 (forced skip-over)
         "shard_subdir": "n1_w17", "out_name": "n1_w17_results.json",
         "engine_owner": "bm-c"},
    # W18 (r530 bm-a, prereg-time extension per the W17 row's W18+
    # WARNING -- never-dry supply law standing step; sovereignty
    # rotation law F-20260928 law sec.4 W17 row verbatim slot W18=bm-a,
    # bm-a's SECOND owned N1 wave after W12; freeze window opened only
    # AFTER the W17xW19 same-band double-freeze adjudication landed
    # (MSG-184x/185x commit-time ruling: W17 stands, bm-b W19 yields;
    # mirrors healed by bm-c 6efed57b6 -- selftests green on healed
    # set)): BOTH tails arithmetic-clean for the first time since the
    # W5/W6/W8/W12/W17 B-skip family -- A's +2_000 tail (78_001 ==
    # W17 A end + 1) and B's +200 tail (38_300 == W17 B end + 1)
    # both land clean as the W17 row projected (stride kept verbatim,
    # no skip on either side). Machine-verified at prereg time
    # (results/_r530bma_w18_band_gate.py ADMIT receipt incl. the
    # r529-mandated N3-R1 actual-seed-set leg 70_000..70_005).
    # EIGHTH ENGINE-OWNED WAVE.
    18: {"batch": "PERPETUAL-N1-W18",
         "prereg": ("research/PERPETUAL_N1_W18_PREREG.md (wave-level frozen "
                    "pre-run; design = frozen v1 null calibration verbatim, "
                    "new seed bands only; EIGHTH ENGINE-OWNED WAVE, "
                    "sovereignty rotation law W18=bm-a, engine_owner=bm-a)"),
         "a_seed_base": 78_001,          # law sec.4 W18 A: 78_001..80_000 (arithmetic)
         "b_exit_seed_base": 38_300,     # law sec.4 W18 B: 38_300..38_499 (arithmetic)
         "shard_subdir": "n1_w18", "out_name": "n1_w18_results.json",
         "engine_owner": "bm-a"},
    # W19 (r517 bm-b freeze + r518 SAME-WINDOW DOUBLE-FREEZE COLLISION
    # YIELD + re-band -- r511 commit-order law: bm-c's W17 rows reached
    # origin first (r328) while the r517 W19 freeze was drafted blind to
    # it; both machines deterministic-same-verdict the W16 table-tail
    # continuation -- bm-b is the latercomer and YIELDS per
    # MSG-20261001-184x. Old-band products (12/12 burned, finalize NEVER
    # ran -> zero ledger pollution) all discarded at yield. Re-band skips
    # past BOTH W17's registered bands AND W18's PUBLISHED PROJECTION
    # (A 78_001..80_000 / B 38_300..38_499, rotation slot W18=bm-a --
    # r511 exhaustive-reservation-scan lesson: published projections are
    # reserved faces; taking them would manufacture a THIRD collision
    # against bm-a's slot). EIGHTH ENGINE-OWNED WAVE, bm-b's fifth,
    # engine_owner=bm-b per sovereignty rotation law F-20261001-01 slot
    # W19=bm-b (wave number 18 unfrozen, gap notes, r516 derive law).
    # Machine-verified at re-freeze time (results/_r517bmb_w19_band_gate.py
    # v3 ADMIT receipt vs the 15-row union table incl. W17 + W18
    # published projection + N3-R1 used-seed band 70_000..70_005
    # (MSG-183x mandatory leg) + SEED_REGISTRY + probes + actuals).
    # NOT a re-pick (R250).
    19: {"batch": "PERPETUAL-N1-W19",
         "prereg": ("research/PERPETUAL_N1_W19_PREREG.md (wave-level frozen "
                    "pre-run; design = frozen v1 null calibration verbatim, "
                    "new seed bands only; EIGHTH ENGINE-OWNED WAVE, "
                    "sovereignty rotation law W19=bm-b, engine_owner=bm-b, "
                    "r511 same-window collision yield vs W17 + re-band "
                    "past W18 published projection)"),
         "a_seed_base": 80_001,          # law sec.4 W19 A: 80_001..82_000 (arithmetic, re-based past W18 projection)
         "b_exit_seed_base": 38_500,     # law sec.4 W19 B: 38_500..38_699 (arithmetic, re-based past W18 projection)
         "shard_subdir": "n1_w19", "out_name": "n1_w19_results.json",
         "engine_owner": "bm-b"},
    # W20 (r330 bm-c, never-dry supply law standing step: NINTH
    # ENGINE-OWNED WAVE, bm-c's third, engine_owner=bm-c per
    # sovereignty rotation law F-20261001-01 slot W20=bm-c per law
    # sec.4 W19 row verbatim; freeze window opened only AFTER bm-b's
    # W19 yield disposition landed on origin -- r329 pointer gate
    # discharged). BOTH arithmetic tails land clean exactly as the
    # W19 row projected (A 82_001 == W19 A end + 1, B 38_700 == W19
    # B end + 1) -- no skip on either side (38k-segment continuation
    # of the W17 B re-base lineage). Machine-verified at prereg time
    # (results/_r330bmc_w20_band_gate.py ADMIT receipt vs the 17-row
    # pre-W20 table incl. W18/W19 + SEED_REGISTRY + probes/actuals +
    # N3-R1 used-seed band 70_000..70_005 MSG-183x mandatory leg).
    # NOT a re-pick (R250).
    20: {"batch": "PERPETUAL-N1-W20",
         "prereg": ("research/PERPETUAL_N1_W20_PREREG.md (wave-level frozen "
                    "pre-run; design = frozen v1 null calibration verbatim, "
                    "new seed bands only; NINTH ENGINE-OWNED WAVE, "
                    "sovereignty rotation law W20=bm-c, engine_owner=bm-c, "
                    "r329 pointer gate discharged: bm-b W19 v3 re-band "
                    "landed on origin)"),
                 "a_seed_base": 82_001,          # law sec.4 W20 A: 82_001..84_000 (arithmetic)
                 "b_exit_seed_base": 38_700,    # law sec.4 W20 B: 38_700..38_899 (arithmetic)
                 "shard_subdir": "n1_w20", "out_name": "n1_w20_results.json",
                 "engine_owner": "bm-c"},
            # W21 (r533 bm-a, never-dry supply law standing step: TENTH
            # ENGINE-OWNED WAVE, bm-a's THIRD, engine_owner=bm-a per
            # sovereignty rotation law F-20261001-01 slot W21=bm-a per law
            # sec.4 W20 row verbatim (W18=bm-a anchored, +3 -> W21=bm-a).
            # BOTH arithmetic tails land clean exactly as the W20 row projected
            # (A 84_001 == W20 A end + 1, B 38_900 == W20 B end + 1) -- no skip
            # on either side (38k-segment continuation). Machine-verified at
            # prereg time (results/_r533bma_w21_band_gate.py ADMIT receipt vs
            # the 19-row pre-W21 table incl. W18/W19/W20 + SEED_REGISTRY +
            # probes/actuals + N3-R1 used-seed band 70_000..70_005 MSG-183x
            # mandatory leg). NOT a re-pick (R250: W21 bands were never
            # assigned; the measurement face has no result to fish).
            21: {"batch": "PERPETUAL-N1-W21",
                 "prereg": ("research/PERPETUAL_N1_W21_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; TENTH ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W21=bm-a, engine_owner=bm-a, "
                            "W20 row slot assignment verbatim)"),
                 "a_seed_base": 84_001,          # law sec.4 W21 A: 84_001..86_000 (arithmetic)
                 "b_exit_seed_base": 38_900,    # law sec.4 W21 B: 38_900..39_099 (arithmetic)
                 "shard_subdir": "n1_w21", "out_name": "n1_w21_results.json",
                 "engine_owner": "bm-a"},
            # W22 (r519 bm-b, prereg-time extension per the W21 row's
            # W22+ WARNING; never-dry supply law standing step;
            # sovereignty rotation law F-20261001-01 slot W22=bm-b per
            # the W21 row verbatim, bm-b's SIXTH owned wave after
            # W10/W11/W13/W16/W19): BOTH tails arithmetic-clean exactly
            # as the W21 row projected (A 86_001..88_000 == W21 A end+1,
            # B 39_100..39_299 == W21 B end+1, no skip either side).
            # Machine-verified at prereg time
            # (results/_r519bmb_w22_band_gate.py ADMIT receipt vs the
            # 20-row pre-W22 table incl. W18/W19/W20/W21 + SEED_REGISTRY
            # + probes/actuals + N3-R1 used-seed band 70_000..70_005
            # MSG-183x mandatory leg). NOT a re-pick (R250: W22 bands
            # were never assigned; the measurement face has no result
            # to fish).
            22: {"batch": "PERPETUAL-N1-W22",
                 "prereg": ("research/PERPETUAL_N1_W22_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; ELEVENTH ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W22=bm-b, engine_owner=bm-b, "
                            "W21 row slot assignment verbatim)"),
                 "a_seed_base": 86_001,          # law sec.4 W22 A: 86_001..88_000 (arithmetic)
                 "b_exit_seed_base": 39_100,    # law sec.4 W22 B: 39_100..39_299 (arithmetic)
                 "shard_subdir": "n1_w22", "out_name": "n1_w22_results.json",
                 "engine_owner": "bm-b"},
            # W23 (r332 bm-c, prereg-time extension per the W22 row's
            # W23+ WARNING; never-dry supply law standing step;
            # sovereignty rotation law F-20261001-01 slot W23=bm-c per
            # the W22 row verbatim, bm-c's FOURTH owned wave after
            # W14/W17/W20): BOTH tails arithmetic-clean exactly as the
            # W22 row projected (A 88_001..90_000 == W22 A end + 1,
            # B 39_300..39_499 == W22 B end + 1, no skip either side,
            # 39k-segment continuation). Machine-verified at prereg
            # time (results/_r332bmc_w23_band_gate.py ADMIT receipt vs
            # the 21-row pre-W23 table incl. W18/W19/W20/W21/W22 +
            # SEED_REGISTRY + probes/actuals + N3-R1 used-seed band
            # 70_000..70_005 MSG-183x mandatory leg). NOT a re-pick
            # (R250: W23 bands were never assigned; the measurement
            # face has no result to fish).
            23: {"batch": "PERPETUAL-N1-W23",
                 "prereg": ("research/PERPETUAL_N1_W23_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; TWELFTH ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W23=bm-c, engine_owner=bm-c, "
                            "W22 row slot assignment verbatim)"),
                 "a_seed_base": 88_001,          # law sec.4 W23 A: 88_001..90_000 (arithmetic)
                 "b_exit_seed_base": 39_300,    # law sec.4 W23 B: 39_300..39_499 (arithmetic)
                 "shard_subdir": "n1_w23", "out_name": "n1_w23_results.json",
                 "engine_owner": "bm-c"},
            # W24 (r535 bm-a, prereg-time extension per the W23 row's
            # W24+ WARNING; never-dry supply law standing step;
            # sovereignty rotation law F-20261001-01 slot W24=bm-a per
            # the W23 row verbatim, bm-a's FOURTH owned wave after
            # W12/W18/W21): BOTH tails arithmetic-clean exactly as the
            # W23 row projected (A 90_001..92_000 == W23 A end + 1,
            # B 39_500..39_699 == W23 B end + 1, no skip either side,
            # 39k-segment continuation). Machine-verified at prereg
            # time (results/_r535bma_w24_band_gate.py ADMIT receipt vs
            # the 22-row pre-W24 table incl. W18/W19/W20/W21/W22/W23 +
            # SEED_REGISTRY + probes/actuals + N3-R1 used-seed band
            # 70_000..70_005 MSG-183x r529 mandatory leg). NOT a re-pick
            # (R250: W24 bands were never assigned; the measurement
            # face has no result to fish).
            24: {"batch": "PERPETUAL-N1-W24",
                 "prereg": ("research/PERPETUAL_N1_W24_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; THIRTEENTH ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W24=bm-a, engine_owner=bm-a, "
                            "W23 row slot assignment verbatim)"),
                 "a_seed_base": 90_001,          # law sec.4 W24 A: 90_001..92_000 (arithmetic)
                 "b_exit_seed_base": 39_500,    # law sec.4 W24 B: 39_500..39_699 (arithmetic)
                 "shard_subdir": "n1_w24", "out_name": "n1_w24_results.json",
                 "engine_owner": "bm-a"},
            # W25 (r520 bm-b, prereg-time extension per the W24 row's
            # W25+ WARNING; never-dry supply law standing step;
            # sovereignty rotation law F-20261001-01 slot W25=bm-b per
            # the W24 row verbatim, bm-b's SEVENTH owned wave after
            # W10/W11/W13/W16/W19/W22): BOTH tails arithmetic-clean
            # exactly as the W24 row projected (A 92_001..94_000 ==
            # W24 A end + 1, B 39_700..39_899 == W24 B end + 1, no skip
            # either side, 39k-segment continuation). Machine-verified
            # at prereg time (results/_r520bmb_w25_band_gate.py ADMIT
            # receipt vs the 23-row pre-W25 table incl.
            # W18/W19/W20/W21/W22/W23/W24 + SEED_REGISTRY + probes/
            # actuals + N3-R1 used-seed band 70_000..70_005 MSG-183x
            # r529 mandatory leg). NOT a re-pick (R250: W25 bands were
            # never assigned; the measurement face has no result to
            # fish).
            25: {"batch": "PERPETUAL-N1-W25",
                 "prereg": ("research/PERPETUAL_N1_W25_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; FOURTEENTH ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W25=bm-b, engine_owner=bm-b, "
                            "W24 row slot assignment verbatim)"),
                 "a_seed_base": 92_001,          # law sec.4 W25 A: 92_001..94_000 (arithmetic)
                 "b_exit_seed_base": 39_700,    # law sec.4 W25 B: 39_700..39_899 (arithmetic)
                 "shard_subdir": "n1_w25", "out_name": "n1_w25_results.json",
                 "engine_owner": "bm-b"},
            # W26 (r335 bm-c, prereg-time extension per the W25 row's
            # W26+ WARNING; never-dry supply law standing step;
            # sovereignty rotation law F-20261001-01 slot W26=bm-c per
            # the W25 row verbatim, bm-c's FIFTH owned wave after
            # W14/W17/W20/W23): BOTH tails FORCED SKIP -- A's +2_000
            # tail (94_001..96_000 == W25 A end + 1) REFUSED by the
            # r335 DISCOVERY: it hits ALL FOUR runner design-probe
            # seeds (ext 95_000/95_001 + n1 95_002/95_003, batch-band-
            # reserved by the selftest disjoint law) -- the r520/r535
            # gate receipts' reserved universe omitted the probe
            # cluster (the W25 row's "A projects clean" WARNING was a
            # blind-spot miss, caught by this runner's materializer
            # selftest leg; past waves W24/W25 clear the cluster --
            # zero retroactive harm) -> jump to the first clean
            # 2,000-window: 95_004..97_003 (W12 A-skip precedent);
            # B's +200 tail (39_900..40_099) FORCED SKIP exactly as
            # the W25 row WARNING projected (hits N2/N4 design-probe
            # retention points 40_000/40_001 AND SEED_REGISTRY value
            # 40_050) -> jump to the first continuous 200-window
            # clear of all reserved faces: 40_051..40_250
            # (W5/W6/W8/W12/W17 jump-family precedent, machine-derived
            # never a free pick R250/r518). Machine-verified at prereg
            # time (results/_r335bmc_w26_band_gate.py ADMIT receipt vs
            # the 24-row pre-W26 table incl. W21/W22/W23/W24/W25 +
            # SEED_REGISTRY + probes/actuals + probe-seed cluster
            # r335 discovery leg + N3-R1 used-seed band 70_000..70_005
            # MSG-183x r529 mandatory leg). NOT a re-pick (R250: W26
            # bands were never assigned; the measurement face has no
            # result to fish).
            26: {"batch": "PERPETUAL-N1-W26",
                 "prereg": ("research/PERPETUAL_N1_W26_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; FIFTEENTH ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W26=bm-c, engine_owner=bm-c, "
                            "W25 row slot assignment verbatim)"),
                 "a_seed_base": 95_004,          # law sec.4 W26 A: 95_004..97_003 (forced-skip jump, probe seeds)
                 "b_exit_seed_base": 40_051,    # law sec.4 W26 B: 40_051..40_250 (forced-skip jump)
                 "shard_subdir": "n1_w26", "out_name": "n1_w26_results.json",
                 "engine_owner": "bm-c"},
            # W27 (r539 bm-a, prereg-time extension per the W26 row's
            # W27+ WARNING; never-dry supply law standing step;
            # sovereignty rotation law F-20260901-01 slot W27=bm-a per
            # the W26 row verbatim, bm-a's FIFTH owned wave after
            # W12/W18/W21/W24): BOTH tails arithmetic-clean exactly as
            # the W26 row projected (A 97_004..99_003 == W26 A end + 1,
            # B 40_251..40_450 == W26 B end + 1, no skip either side,
            # 40k-segment continuation). Machine-verified at prereg
            # time (results/_r539bma_w27_band_gate.py ADMIT receipt vs
            # the 25-row pre-W27 table incl. W23/W24/W25/W26 +
            # SEED_REGISTRY + probes/actuals + probe-seed cluster
            # r335 discovery leg + N3-R1 used-seed band 70_000..70_005
            # MSG-183x r529 mandatory leg). NOT a re-pick (R250: W27
            # bands were never assigned; the measurement face has no
            # result to fish).
            27: {"batch": "PERPETUAL-N1-W27",
                 "prereg": ("research/PERPETUAL_N1_W27_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; SIXTEENTH ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W27=bm-a, engine_owner=bm-a, "
                            "W26 row slot assignment verbatim)"),
                 "a_seed_base": 97_004,          # law sec.4 W27 A: 97_004..99_003 (arithmetic)
                 "b_exit_seed_base": 40_251,    # law sec.4 W27 B: 40_251..40_450 (arithmetic)
                 "shard_subdir": "n1_w27", "out_name": "n1_w27_results.json",
                 "engine_owner": "bm-a"},
            # W28 (r523 bm-b, prereg-time extension per the W27 row's
            # W28+ WARNING; never-dry supply law standing step;
            # sovereignty rotation law F-20260901-01 slot W28=bm-b
            # per the W27 row verbatim, bm-b's EIGHTH owned wave
            # after W10/W11/W13/W16/W19/W22/W25): BOTH tails
            # arithmetic-clean exactly as the W27 row projected
            # (A 99_004..101_003 == W27 A end + 1, B 40_451..40_650
            # == W27 B end + 1, no skip either side, 40k-segment
            # continuation). Machine-verified at prereg time
            # (results/_r523bmb_w28_band_gate.py ADMIT receipt vs
            # the 26-row pre-W28 table incl. W24/W25/W26/W27 +
            # SEED_REGISTRY + probes/actuals + probe-seed cluster
            # 95_000..95_003 r335 discovery leg + N3-R1 used-seed
            # band 70_000..70_005 MSG-183x r529 mandatory leg).
            # NOT a re-pick (R250: W28 bands were never assigned;
            # the measurement face has no result to fish).
            28: {"batch": "PERPETUAL-N1-W28",
                 "prereg": ("research/PERPETUAL_N1_W28_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; SEVENTEENTH ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W28=bm-b, engine_owner=bm-b, "
                            "W27 row slot assignment verbatim)"),
                 "a_seed_base": 99_004,          # law sec.4 W28 A: 99_004..101_003 (arithmetic)
                 "b_exit_seed_base": 40_451,    # law sec.4 W28 B: 40_451..40_650 (arithmetic)
                 "shard_subdir": "n1_w28", "out_name": "n1_w28_results.json",
                 "engine_owner": "bm-b"},
            # W29 (r336 bm-c, prereg-time extension per the W28 row's
            # W29+ WARNING; never-dry supply law standing step;
            # sovereignty rotation law F-20261001-01 slot W29=bm-c
            # per the W28 row verbatim, bm-c's SIXTH owned wave
            # after W14/W17/W20/W23/W26): BOTH tails
            # arithmetic-clean exactly as the W28 row projected
            # (A 101_004..103_003 == W28 A end + 1, B 40_651..40_850
            # == W28 B end + 1, no skip either side, 40k-segment
            # continuation). Machine-verified at prereg time
            # (results/_r336bmc_w29_band_gate.py ADMIT receipt vs
            # the 27-row pre-W29 table incl. W25/W26/W27/W28 +
            # SEED_REGISTRY + probes/actuals + probe-seed cluster
            # 95_000..95_003 r335 discovery leg + N3-R1 used-seed
            # band 70_000..70_005 MSG-183x r529 mandatory leg).
            # NOT a re-pick (R250: W29 bands were never assigned;
            # the measurement face has no result to fish).
            29: {"batch": "PERPETUAL-N1-W29",
                 "prereg": ("research/PERPETUAL_N1_W29_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; EIGHTEENTH ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W29=bm-c, engine_owner=bm-c, "
                            "W28 row slot assignment verbatim)"),
                 "a_seed_base": 101_004,        # law sec.4 W29 A: 101_004..103_003 (arithmetic)
                 "b_exit_seed_base": 40_651,    # law sec.4 W29 B: 40_651..40_850 (arithmetic)
                 "shard_subdir": "n1_w29", "out_name": "n1_w29_results.json",
                 "engine_owner": "bm-c"},
            # W30 (r541 bm-a, prereg-time extension per the W28 row's W29+
            # WARNING -- never-dry supply law standing step; sovereignty
            # rotation law F-20260901-01 slot W30=bm-a per the W27=bm-a
            # real anchor (finalize landed bm-a r540, K=57,320, ledger
            # 423,948 chain head; W28=bm-b / W29=bm-c seats continue the
            # +3 rotation -> W30=bm-a). W29 (bm-c seat) NOT registered at
            # this freeze: its published projection (A 101_004..103_003 /
            # B 40_651..40_850, the W28 row's W29+ WARNING naming the
            # W29=bm-c rotation slot) is a RESERVED FACE (r518: published
            # projection = reserved face) -- W30 skips past it. A side:
            # first clean window 103_004..105_003 == W29 projected A
            # tail + 1, no further skip. B side: 40_851..41_050 (W29
            # projected B tail + 1) hits SEED_REGISTRY p4_batch1=41_000
            # -> advance to 41_001..41_200 (W26 B re-base skip lineage,
            # in-band point skip family). Machine-verified at prereg
            # time (results/_r541bma_w30_band_gate.py ADMIT receipt vs
            # the 26-row pre-W30 table incl. W25/W26/W27/W28 +
            # SEED_REGISTRY + probes/actuals + probe-seed cluster
            # 95_000..95_003 r335 discovery leg + N3-R1 used-seed band
            # 70_000..70_005 MSG-183x r529 mandatory leg + W29
            # published-projection reservation leg). NINETEENTH engine-
            # owned wave. NOT a re-pick (R250: W30 bands were never
            # assigned; the measurement face has no result to fish).
            30: {"batch": "PERPETUAL-N1-W30",
                 "prereg": ("research/PERPETUAL_N1_W30_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; NINETEENTH ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W30=bm-a, engine_owner=bm-a, "
                            "W28 row slot assignment verbatim + W29 published-"
                            "projection skip (r518) + B-side p4_batch1=41_000 "
                            "in-band skip)"),
                 "a_seed_base": 103_004,        # law sec.4 W30 A: 103_004..105_003 (skip past W29 projection)
                 "b_exit_seed_base": 41_001,    # law sec.4 W30 B: 41_001..41_200 (skip past p4_batch1=41_000)
                 "shard_subdir": "n1_w30", "out_name": "n1_w30_results.json",
                 "engine_owner": "bm-a"},
            # W31 (r525 bm-b, prereg-time extension per the W30 row's
            # W31+ WARNING -- never-dry supply law standing step;
            # sovereignty rotation law F-20260901-01 slot W31=bm-b
            # per the +3 rotation from the W28=bm-b real anchor
            # (finalize landed bm-b r524; W29=bm-c SEATED AND
            # FINALIZED mid-draft bm-c r337 -- K=61,720, ledger
            # 428,348 chain head; W30=bm-a frozen r541 burn in
            # flight -- registered in-use face). W29's published
            # projection window was honored by the bm-c freeze
            # taking exactly that window (r337, r518 discharged).
            # BOTH tails arithmetic-clean exactly as the W30 row's
            # W31+ WARNING projected (A 105_004..107_003 == W30 A
            # end + 1, B 41_201..41_400 == W30 B end + 1, no skip
            # either side). Machine-verified at prereg time
            # (results/_r525bmb_w31_band_gate.py ADMIT receipt vs
            # the 28-row pre-W31 table incl. W25/W26/W27/W28/W29/W30
            # + SEED_REGISTRY + probes/actuals + probe-seed cluster
            # 95_000..95_003 r335 discovery leg + N3-R1 used-seed
            # band 70_000..70_005 MSG-183x r529 mandatory leg).
            # TWENTIETH engine-owned wave, bm-b's NINTH owned wave.
            # NOT a re-pick (R250: W31 bands were never assigned;
            # the measurement face has no result to fish).
            31: {"batch": "PERPETUAL-N1-W31",
                 "prereg": ("research/PERPETUAL_N1_W31_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; TWENTIETH ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W31=bm-b, engine_owner=bm-b, "
                            "W30 row slot assignment verbatim, both tails "
                            "arithmetic continuation)"),
                 "a_seed_base": 105_004,        # law sec.4 W31 A: 105_004..107_003 (arithmetic)
                 "b_exit_seed_base": 41_201,    # law sec.4 W31 B: 41_201..41_400 (arithmetic)
                 "shard_subdir": "n1_w31", "out_name": "n1_w31_results.json",
                 "engine_owner": "bm-b"},
            # W32 (r339 bm-c, prereg-time extension per the W31 row's
            # W32+ WARNING -- never-dry supply law standing step;
            # sovereignty rotation law F-20260901-01 slot W32=bm-c
            # per the +3 rotation from the W29=bm-c real anchor
            # (finalize landed bm-c r337, K=61,720; W30 finalize
            # landed bm-a r542, K=63,920, ledger 430,548; W31
            # finalize landed bm-b, K=66,120, ledger 432,748 chain
            # head -- every pre-W32 seat closed at this freeze).
            # BOTH tails arithmetic-clean exactly as the W31 row's
            # W32+ WARNING projected (A 107_004..109_003 == W31 A
            # end + 1, B 41_401..41_600 == W31 B end + 1, no skip
            # either side). Machine-verified at prereg time
            # (results/_r339bmc_w32_band_gate.py ADMIT receipt vs
            # the 29-row pre-W32 table incl. W29/W30/W31 +
            # SEED_REGISTRY + probes/actuals + probe-seed cluster
            # 95_000..95_003 r335 discovery leg + N3-R1 used-seed
            # band 70_000..70_005 MSG-183x r529 mandatory leg).
            # TWENTY-FIRST ENGINE-OWNED WAVE, bm-c's SEVENTH owned
            # wave after W14/W17/W20/W23/W26/W29. NOT a re-pick
            # (R250: W32 bands were never assigned; the measurement
            # face has no result to fish).
            32: {"batch": "PERPETUAL-N1-W32",
                 "prereg": ("research/PERPETUAL_N1_W32_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; TWENTY-FIRST ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W32=bm-c, engine_owner=bm-c, "
                            "W31 row slot assignment verbatim, both tails "
                            "arithmetic continuation)"),
                 "a_seed_base": 107_004,        # law sec.4 W32 A: 107_004..109_003 (arithmetic)
                 "b_exit_seed_base": 41_401,    # law sec.4 W32 B: 41_401..41_600 (arithmetic)
                 "shard_subdir": "n1_w32", "out_name": "n1_w32_results.json",
                 "engine_owner": "bm-c"},
            # W33 (r544 bm-a, prereg-time extension per the W32 row's
            # W33+ WARNING -- never-dry supply law standing step;
            # sovereignty rotation law F-20260901-01 slot W33=bm-a
            # per the +3 rotation from the W30=bm-a real anchor
            # (finalize landed bm-a r542, K=63,920; W31 finalize
            # landed bm-b r525, K=66,120, ledger 432,748 chain head;
            # W32 bm-c r339 registered + burned 12/12 + ledger-
            # appended -- its finalize sits pending at the bm-c seat
            # and consumes nothing this freeze touches; r543 seat
            # discipline discharged: the W32 row IS landed). BOTH
            # tails arithmetic-clean exactly as the W32 row's W33+
            # WARNING projected (A 109_004..111_003 == W32 A end +
            # 1, B 41_601..41_800 == W32 B end + 1, no skip either
            # side). Machine-verified at prereg time
            # (results/_r544bma_w33_band_gate.py ADMIT receipt vs
            # the 30-row pre-W33 table incl. W30/W31/W32 +
            # SEED_REGISTRY + probes/actuals + probe-seed cluster
            # 95_000..95_003 r335 discovery leg + N3-R1 used-seed
            # band 70_000..70_005 MSG-183x r529 mandatory leg).
            # TWENTY-SECOND ENGINE-OWNED WAVE, bm-a's SEVENTH owned
            # wave after W12/W18/W21/W24/W27/W30. NOT a re-pick
            # (R250: W33 bands were never assigned; the measurement
            # face has no result to fish).
            33: {"batch": "PERPETUAL-N1-W33",
                 "prereg": ("research/PERPETUAL_N1_W33_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; TWENTY-SECOND ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W33=bm-a, engine_owner=bm-a, "
                            "W32 row slot assignment verbatim, both tails "
                            "arithmetic continuation)"),
                 "a_seed_base": 109_004,        # law sec.4 W33 A: 109_004..111_003 (arithmetic)
                 "b_exit_seed_base": 41_601,    # law sec.4 W33 B: 41_601..41_800 (arithmetic)
                 "shard_subdir": "n1_w33", "out_name": "n1_w33_results.json",
                 "engine_owner": "bm-a"},
            # W34 (r527 bm-b, prereg-time extension per the W33 row's
            # W34+ WARNING -- never-dry supply law standing step +
            # O-20261001-2355 CEO de-throttle order (every machine
            # keeps its own continuous series, waiting forbidden;
            # sequence constraints preserve finalize ORDER only).
            # Sovereignty rotation law F-20260901-01 slot W34=bm-b
            # per the +3 rotation from the W31=bm-b real anchor
            # (finalize landed bm-b r525, K=66,120; W33 finalize
            # landed bm-a r544 same-window, K=70,520, ledger 437,148
            # chain head -- W1..W33 ALL finalized at this freeze, the
            # chain fully caught up, zero pending upstream face for
            # the first time). BOTH tails arithmetic-clean exactly as
            # the W33 row's W34+ WARNING projected (A 111_004..113_003
            # == W33 A end + 1, B 41_801..42_000 == W33 B end + 1, no
            # skip either side). Machine-verified at prereg time
            # (results/_r527bmb_w34_band_gate.py ADMIT receipt vs the
            # 31-row pre-W34 table incl. W30/W31/W32/W33 +
            # SEED_REGISTRY + probes/actuals + probe-seed cluster
            # 95_000..95_003 r335 discovery leg + N3-R1 used-seed
            # band 70_000..70_005 MSG-183x r529 mandatory leg; the
            # same-window pre-scan receipt _r527bmb_w34_pre_band_gate.py
            # is the leg-0 evidence base). TWENTY-THIRD ENGINE-OWNED
            # WAVE, bm-b's TENTH owned wave after W10/W11/W13/W16/
            # W19/W22/W25/W28/W31. NOT a re-pick (R250: W34 bands
            # were never assigned; the measurement face has no
            # result to fish).
            34: {"batch": "PERPETUAL-N1-W34",
                 "prereg": ("research/PERPETUAL_N1_W34_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; TWENTY-THIRD ENGINE-OWNED WAVE, "
                            "sovereignty rotation law W34=bm-b + O-20261001-2355 "
                            "de-throttle order, engine_owner=bm-b, W33 row slot "
                            "assignment verbatim, both tails arithmetic continuation)"),
                 "a_seed_base": 111_004,        # law sec.4 W34 A: 111_004..113_003 (arithmetic)
                 "b_exit_seed_base": 41_801,    # law sec.4 W34 B: 41_801..42_000 (arithmetic)
                 "shard_subdir": "n1_w34", "out_name": "n1_w34_results.json",
                 "engine_owner": "bm-b"},
            # W35 (r545 bm-a, engine de-throttle law O-20261001-2355
            # sec.2 -- per-machine self-owned continuous series,
            # zero-gap relay after W33 full closeout (finalize landed
            # bm-a r544, K=70,520, ledger 437,148 chain-linear); seat
            # system retired by the same order). Wave 35 = next free
            # number after W34's published claim (bm-b pre-scan
            # ADMIT-READY r527, freeze pending at the bm-b seat --
            # published projection = reserved face per r518). Forced
            # skip over the published W34 projection windows
            # machine-proven by results/_r545bma_w35_band_gate.py
            # refusal facts. TWENTY-FOURTH engine-owned wave, bm-a's
            # EIGHTH owned wave after W12/W18/W21/W24/W27/W30/W33.
            # NOT a re-pick (R250: W35 bands were never assigned; the
            # measurement face has no result to fish).
            35: {"batch": "PERPETUAL-N1-W35",
                 "prereg": ("research/PERPETUAL_N1_W35_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; TWENTY-FOURTH ENGINE-OWNED WAVE, "
                            "engine de-throttle law O-20261001-2355 sec.2 "
                            "own-continuous-series, engine_owner=bm-a, forced skip "
                            "over W34 published projection, wave 35 = first free "
                            "number after W34's claim)"),
                 "a_seed_base": 113_004,        # law sec.4 W35 A: 113_004..115_003 (post-projection)
                 "b_exit_seed_base": 42_001,    # law sec.4 W35 B: 42_001..42_200 (post-projection)
                 "shard_subdir": "n1_w35", "out_name": "n1_w35_results.json",
                 "engine_owner": "bm-a"},
            # W36 (r528 bm-b, engine de-throttle law O-20261001-2355
            # sec.2 -- per-machine self-owned continuous series,
            # zero-gap relay after W34 full closeout (freeze+12/12 burn
            # +finalize landed bm-b r528 same-window, K=72,720, ledger
            # net head 437,340); wave 36 = first free number after
            # W35's landed claim, seat system retired by the same
            # order). BOTH tails arithmetic-clean exactly as the W35
            # row's W36+ WARNING projected (no skip either side).
            # Machine-verified at prereg time (results/_r528bmb_
            # w36_band_gate.py ADMIT receipt vs the 33-row pre-W36
            # table incl. W34/W35 + SEED_REGISTRY + probe-seed cluster
            # + N3-R1 used-seed band). TWENTY-FIFTH ENGINE-OWNED WAVE,
            # bm-b's ELEVENTH owned wave. NOT a re-pick (R250).
            36: {"batch": "PERPETUAL-N1-W36",
                 "prereg": ("research/PERPETUAL_N1_W36_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; TWENTY-FIFTH ENGINE-OWNED WAVE, "
                            "engine de-throttle law O-20261001-2355 sec.2 "
                            "own-continuous-series, engine_owner=bm-b, wave 36 = "
                            "first free number after W35's claim, both tails "
                            "arithmetic continuation)"),
                 "a_seed_base": 115_004,        # law sec.4 W36 A: 115_004..117_003 (arithmetic)
                 "b_exit_seed_base": 42_201,    # law sec.4 W36 B: 42_201..42_400 (arithmetic)
                 "shard_subdir": "n1_w36", "out_name": "n1_w36_results.json",
                 "engine_owner": "bm-b"},
            # W37 (r341 bm-c, own-series continuation per CEO
            # de-throttle order O-20261001-2355 sec.2 -- bm-c's EIGHTH
            # owned wave after W14/W17/W20/W23/W26/W29/W32; follows the
            # r341 W36 yield to bm-b per r511 commit-order law, zero
            # burn zero ledger zero loss -- the crashed-session draft
            # never landed). Wave 37 = first free number: W35 (bm-a)
            # and W36 (bm-b) both registered; BOTH tails arithmetic
            # continuation from the registered W36 row, no skip.
            # Machine-verified at prereg time
            # (results/_r341bmc_w37_band_gate.py ADMIT receipt vs the
            # 34-row pre-W37 table + SEED_REGISTRY + probes/actuals +
            # probe-seed cluster 95_000..95_003 r335 discovery leg +
            # N3-R1 used-seed band 70_000..70_005 MSG-183x r529
            # mandatory leg). TWENTY-SIXTH ENGINE-OWNED WAVE,
            # engine_owner=bm-c (local queue, no pool entry).
            # NOT a re-pick (R250: W37 bands were never assigned).
            37: {"batch": "PERPETUAL-N1-W37",
                 "prereg": ("research/PERPETUAL_N1_W37_PREREG.md (wave-level frozen "
                            "pre-run; design = frozen v1 null calibration verbatim, "
                            "new seed bands only; TWENTY-SIXTH ENGINE-OWNED WAVE, "
                            "own-series continuation per O-20261001-2355 sec.2 "
                            "(seat system terminated, first-free-number law), "
                            "engine_owner=bm-c, both tails arithmetic continuation "
                            "from the registered W36 row, no skip)"),
                        "a_seed_base": 117_004,        # law sec.4 W37 A: 117_004..119_003 (arithmetic)
                        "b_exit_seed_base": 42_401,    # law sec.4 W37 B: 42_401..42_600 (arithmetic)
                        "shard_subdir": "n1_w37", "out_name": "n1_w37_results.json",
                        "engine_owner": "bm-c"},
                  # W38 (r529 bm-b, own-series continuation per CEO
                  # de-throttle order O-20261001-2355 sec.2 -- bm-b's TWELFTH
                  # owned wave after W10/W11/W13/W16/W19/W22/W25/W28/W31/
                  # W34/W36; follows the W36 FULL CLOSEOUT this same window
                  # (r529: finalize one-pass 441,740, K=77,120 == sec.0
                  # projection) -> zero-gap relay. Wave 38 = first free
                  # number: W35 (bm-a), W36 (bm-b) and W37 (bm-c) all
                  # registered; BOTH tails arithmetic continuation from the
                  # registered W37 row, no skip. Machine-verified at prereg
                  # time (results/_r529bmb_w38_band_gate.py ADMIT receipt
                  # vs the 35-row pre-W38 table + SEED_REGISTRY + probes/
                  # actuals + probe-seed cluster 95_000..95_003 r335
                  # discovery leg + N3-R1 used-seed band 70_000..70_005
                  # MSG-183x r529 mandatory leg). TWENTY-SEVENTH
                  # ENGINE-OWNED WAVE, engine_owner=bm-b (local queue, no
                  # pool entry). NOT a re-pick (R250: W38 bands were never
                  # assigned).
                  38: {"batch": "PERPETUAL-N1-W38",
                       "prereg": ("research/PERPETUAL_N1_W38_PREREG.md (wave-level frozen "
                                  "pre-run; design = frozen v1 null calibration verbatim, "
                                  "new seed bands only; TWENTY-SEVENTH ENGINE-OWNED WAVE, "
                                  "own-series continuation per O-20261001-2355 sec.2 "
                                  "(seat system terminated, first-free-number law), "
                                  "engine_owner=bm-b, both tails arithmetic continuation "
                                  "from the registered W37 row, no skip)"),
                       "a_seed_base": 119_004,        # law sec.4 W38 A: 119_004..121_003 (arithmetic)
                       "b_exit_seed_base": 42_601,    # law sec.4 W38 B: 42_601..42_800 (arithmetic)
                       "shard_subdir": "n1_w38", "out_name": "n1_w38_results.json",
                       "engine_owner": "bm-b"},
                  # W39 (r342 bm-c freeze): TWENTY-EIGHTH ENGINE-OWNED WAVE.
                  # A = arithmetic continuation from W38 (no skip, W38 row
                  # W39+ WARNING projected CLEAN, machine-verified); B =
                  # FORCED SKIP past SEED_REGISTRY p4_folk=43_000 (the
                  # arithmetic window 42_801..43_000 refused at its tail
                  # point; first clean window 43_001..43_200 derived,
                  # r307 wave-band tail law). NOT a re-pick (R250: W39
                  # bands were never assigned).
                  39: {"batch": "PERPETUAL-N1-W39",
                       "prereg": ("research/PERPETUAL_N1_W39_PREREG.md (wave-level frozen "
                                  "pre-run; design = frozen v1 null calibration verbatim, "
                                  "new seed bands only; TWENTY-EIGHTH ENGINE-OWNED WAVE, "
                                  "own-series continuation per O-20261001-2355 sec.2 "
                                  "(seat system terminated, first-free-number law), "
                                  "engine_owner=bm-c, A tail arithmetic continuation "
                                  "from the registered W38 row no skip, B tail FORCED "
                                  "SKIP past SEED_REGISTRY p4_folk=43_000 per the W38 "
                                  "row W39+ WARNING refusal, r307 wave-band tail law)"),
                       "a_seed_base": 121_004,        # law sec.4 W39 A: 121_004..123_003 (arithmetic)
                       "b_exit_seed_base": 43_001,    # law sec.4 W39 B: 43_001..43_200 (gate-skip past 43_000)
                       "shard_subdir": "n1_w39", "out_name": "n1_w39_results.json",
                       "engine_owner": "bm-c"},
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


# --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2: 池=账本非闸门) ----------
# "pool" (default) = r496/r497 claim handshake ON: pool-lane daemon harvest
# flips POOL entries from these claim files -- byte-identical legacy face.
# "engine" = pre-claim exempt: perpetual-face burns under the resident
# saturation engine derive authorization from the frozen prereg + law band
# row and have NO pool entry to flip, so claim files there would be pure
# orphan git traffic (the engine's batched ledger appender is the record).
_LANE = "pool"


def _set_lane(lane: str) -> None:
    global _LANE
    _LANE = lane


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
    if _LANE == "engine":
        # T-141 s2 / law sec.2: engine-lane burns are pre-claim exempt --
        # no pool entry exists to harvest-flip, so the handshake file would
        # be orphan git traffic; the engine's batched append is the ledger.
        print(f"claim exempt (engine lane, law sec.2): {shard_key}", flush=True)
        return
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
    # wave set DERIVES from the WAVE_CONFIGS registry keys below the
    # current wave -- never a contiguous range() (r511 derive law; the
    # W16 freeze exposed the gap: unified wave number 15 is held by the
    # N2 face draft, so N1 keys run 2..14 then 16 -- range(2, WAVE)
    # KeyErrors on the missing 15).
    for w in sorted(w for w in WAVE_CONFIGS if w < WAVE):
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
    # prior wave for the mu_delta readout DERIVES from the registry
    # (largest existing key below WAVE; 1 for W2), never WAVE - 1
    # (r511 derive law; W16 gap: unified number 15 held by N2 face).
    prior_wave = 1 if WAVE == 2 else max(w for w in WAVE_CONFIGS if w < WAVE)
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
        prior_wave = 1
    else:
        # prior wave DERIVES from the registry (largest existing key
        # below WAVE), never WAVE - 1 (r511 derive law; W16 gap: the
        # unified number 15 is held by the N2 face, so the prior N1
        # wave is 14).
        prior_wave = max(w for w in WAVE_CONFIGS if w < WAVE)
        wprev = json.load(open(os.path.join(
            OUT_DIR, WAVE_CONFIGS[prior_wave]["out_name"]), encoding="utf-8"))
        prior_mu = ((wprev.get("null_pool_cumulative") or {})
                    .get(f"w{prior_wave}_only") or {}).get("mu")
    if prior_mu is not None:
        out["null_pool_cumulative"][f"mu_delta_w{WAVE}_vs_w{prior_wave}ext"] = \
            round(cov_wv["mu"] - prior_mu, 6)
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
            # --- wave-8 face (r312 bm-c: same guard set; A = documented
            #     skip-over with a registry-point refusal -- the law
            #     sec.4 pinned W8+ WARNING window itself is gate-refused;
            #     B keeps the arithmetic stride verbatim, no skip) ---
            _set_wave(8)
            try:
                assert WAVE_CONFIGS[8]["a_seed_base"] == pf.N1_BANDS[8]["a"][0], \
                    "W8 A band drift vs law mirror"
                assert WAVE_CONFIGS[8]["b_exit_seed_base"] == \
                    pf.N1_BANDS[8]["b_exit"][0], "W8 B band drift vs law mirror"
                w8_a = {A_SEED_BASE + j for j in range(A_N)}
                w8_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
                assert not (w8_a & w8_b), "W8 A/B band overlap"
                assert not (w8_a & reg_ints) and not (w8_b & reg_ints), \
                    "W8 hits SEED_REGISTRY"
                for nm, band in (("A", w8_a), ("B", w8_b)):
                    assert not (band & v1_a) and not (band & v1_b), f"W8 {nm} hits v1"
                    assert not (band & w1_a) and not (band & w1_b), f"W8 {nm} hits W1"
                    assert not (band & probes), f"W8 {nm} hits probe seeds"
                for wprev in (2, 3, 4, 5, 6, 7):
                    assert not (w8_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                        for j in range(A_N)}), f"W8 A hits W{wprev}"
                    assert not (w8_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                        for j in range(B_N)}), f"W8 B hits W{wprev}"
                # skip-over refusal facts (law sec.4 W8 row): A's
                # arithmetic +2_000 tail hits the W7 B band AND the
                # lfc_p1_screen registry point 30_000; the law-pinned
                # W8+ warning window (28_300..30_299) is refused by the
                # same point -- double refusal, skip forced. B's
                # arithmetic +200 tail is CLEAN this wave (the A jump
                # cleared the predicted collision): stride kept verbatim.
                arith_a8 = {WAVE_CONFIGS[7]["a_seed_base"] + 2000 + j
                            for j in range(A_N)}
                assert arith_a8 & {WAVE_CONFIGS[7]["b_exit_seed_base"] + j
                                   for j in range(B_N)}, \
                    "refused A arithmetic tail must hit W7 B (doc)"
                assert 30_000 in arith_a8 and 30_000 in reg_ints, \
                    "refused A arithmetic tail must hit lfc_p1_screen point (doc)"
                warned_a8 = set(range(28_300, 30_300))
                assert 30_000 in warned_a8, \
                    "law-pinned W8 warning window must be refused (doc)"
                assert WAVE_CONFIGS[8]["a_seed_base"] == 30_100 and \
                    WAVE_CONFIGS[8]["a_seed_base"] > 30_099, \
                    "W8 packing drift (A must clear the lfc actual range 30_000..30_099)"
                arith_b8 = {WAVE_CONFIGS[7]["b_exit_seed_base"] + 200 + j
                            for j in range(B_N)}
                assert not (arith_b8 & w8_a), \
                    "W8 B arithmetic tail must be clean (no skip this wave)"
                assert WAVE_CONFIGS[8]["b_exit_seed_base"] == \
                    WAVE_CONFIGS[7]["b_exit_seed_base"] + B_N, \
                    "W8 B stride drift (must sit at W7 B end + 1)"
                assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W8-SHARD-0",
                                                  "n1w8-0of12"), "W8 entry identity"
                assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W8-SHARD-11",
                                                   "n1w8-11of12")
                assert SHARD_DIR.endswith("n1_w8") and OUT.endswith(
                    "n1_w8_results.json"), "W8 path drift"
                for wprev in (2, 3, 4, 5, 6, 7):
                    assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                        PATHS.results_dir, "p2cal_ext",
                        WAVE_CONFIGS[wprev]["shard_subdir"])), \
                        f"W8 shard dir collides with W{wprev}"
                assert os.path.exists(os.path.join(
                    PATHS.root, "research", "PERPETUAL_N1_W8_PREREG.md")), \
                    "W8 per-wave prereg missing (materializer requirement)"
                # W8 finalize cumulative dep (W7 output) present on tree
                # at drafting (r312 bm-c landed n1_w7_results.json in the
                # same window) -- static exists-assert valid here.
                assert os.path.exists(os.path.join(
                    OUT_DIR, WAVE_CONFIGS[7]["out_name"])), \
                    "W8 finalize cumulative dep (W7 output) missing"
                assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
            finally:
                _set_wave(2)
            # --- wave-9 face (r506 bm-b, O-20261001-1332 sec.1.2: same
            #     guard set; arithmetic continuation -- BOTH tails land
            #     clean exactly as the W8 row projected, no skip this
            #     wave; ADMIT receipt results/_r506bmb_w9_band_gate.py) ---
            _set_wave(9)
            try:
                assert WAVE_CONFIGS[9]["a_seed_base"] == pf.N1_BANDS[9]["a"][0], \
                    "W9 A band drift vs law mirror"
                assert WAVE_CONFIGS[9]["b_exit_seed_base"] == \
                    pf.N1_BANDS[9]["b_exit"][0], "W9 B band drift vs law mirror"
                w9_a = {A_SEED_BASE + j for j in range(A_N)}
                w9_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
                assert not (w9_a & w9_b), "W9 A/B band overlap"
                assert not (w9_a & reg_ints) and not (w9_b & reg_ints), \
                    "W9 hits SEED_REGISTRY"
                for nm, band in (("A", w9_a), ("B", w9_b)):
                    assert not (band & v1_a) and not (band & v1_b), f"W9 {nm} hits v1"
                    assert not (band & w1_a) and not (band & w1_b), f"W9 {nm} hits W1"
                    assert not (band & probes), f"W9 {nm} hits probe seeds"
                for wprev in (2, 3, 4, 5, 6, 7, 8):
                    assert not (w9_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                        for j in range(A_N)}), f"W9 A hits W{wprev}"
                    assert not (w9_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                       for j in range(B_N)}), f"W9 B hits W{wprev}"
                # arithmetic continuation facts (law sec.4 W9 row): both
                # tails land clean (W8 row projection + prereg-time ADMIT
                # receipt) -- A sits at W8 A end + 1, B at W8 B end + 1,
                # strides verbatim, no skip-over refusal facts this wave.
                lfc_actual9 = set(range(30_000, 30_100))
                assert not (w9_a & lfc_actual9) and not (w9_b & lfc_actual9), \
                    "W9 bands must clear the lfc actual draw range"
                assert WAVE_CONFIGS[9]["a_seed_base"] == \
                    WAVE_CONFIGS[8]["a_seed_base"] + A_N, \
                    "W9 A stride drift (arithmetic continuation, no skip)"
                assert WAVE_CONFIGS[9]["b_exit_seed_base"] == \
                    WAVE_CONFIGS[8]["b_exit_seed_base"] + B_N, \
                    "W9 B stride drift (arithmetic continuation, no skip)"
                assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W9-SHARD-0",
                                                  "n1w9-0of12"), "W9 entry identity"
                assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W9-SHARD-11",
                                                   "n1w9-11of12")
                assert SHARD_DIR.endswith("n1_w9") and OUT.endswith(
                    "n1_w9_results.json"), "W9 path drift"
                for wprev in (2, 3, 4, 5, 6, 7, 8):
                    assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                        PATHS.results_dir, "p2cal_ext",
                        WAVE_CONFIGS[wprev]["shard_subdir"])), \
                        f"W9 shard dir collides with W{wprev}"
                assert os.path.exists(os.path.join(
                    PATHS.root, "research", "PERPETUAL_N1_W9_PREREG.md")), \
                    "W9 per-wave prereg missing (materializer requirement)"
                # W9 finalize cumulative dep (W8 output) present on tree
                # at drafting (bm-c r315 landed n1_w8_results.json with
                # same-window backfill) -- static exists-assert valid.
                assert os.path.exists(os.path.join(
                    OUT_DIR, WAVE_CONFIGS[8]["out_name"])), \
                    "W9 finalize cumulative dep (W8 output) missing"
                assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
            finally:
                _set_wave(2)
            # --- wave-10 face (r508 bm-b, T-2026-10-01-141 s1 FIRST
            #     ENGINE-OWNED WAVE: engine_owner=bm-b, burned by the
            #     saturation engine local queue, never pool-materialized;
            #     arithmetic continuation BOTH tails clean per ADMIT
            #     receipt) ---
            _set_wave(10)
            try:
                assert WAVE_CONFIGS[10]["a_seed_base"] == pf.N1_BANDS[10]["a"][0], \
                    "W10 A band drift vs law mirror"
                assert WAVE_CONFIGS[10]["b_exit_seed_base"] == \
                    pf.N1_BANDS[10]["b_exit"][0], "W10 B band drift vs law mirror"
                assert WAVE_CONFIGS[10].get("engine_owner") == \
                    pf.N1_BANDS[10].get("engine_owner") == "bm-b", \
                    "W10 engine_owner drift (law mirror parity)"
                w10_a = {A_SEED_BASE + j for j in range(A_N)}
                w10_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
                assert not (w10_a & w10_b), "W10 A/B band overlap"
                assert not (w10_a & reg_ints) and not (w10_b & reg_ints), \
                    "W10 hits SEED_REGISTRY"
                for nm, band in (("A", w10_a), ("B", w10_b)):
                    assert not (band & v1_a) and not (band & v1_b), f"W10 {nm} hits v1"
                    assert not (band & w1_a) and not (band & w1_b), f"W10 {nm} hits W1"
                    assert not (band & probes), f"W10 {nm} hits probe seeds"
                for wprev in (2, 3, 4, 5, 6, 7, 8, 9):
                    assert not (w10_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                         for j in range(A_N)}), f"W10 A hits W{wprev}"
                    assert not (w10_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                        for j in range(B_N)}), f"W10 B hits W{wprev}"
                # arithmetic continuation facts (law sec.4 W10 row): both
                # tails land clean (W9 row projection + prereg-time ADMIT
                # receipt) -- A sits at W9 A end + 1, B at W9 B end + 1,
                # strides verbatim, no skip-over refusal facts this wave.
                lfc_actual10 = set(range(30_000, 30_100))
                assert not (w10_a & lfc_actual10) and not (w10_b & lfc_actual10), \
                    "W10 bands must clear the lfc actual draw range"
                assert WAVE_CONFIGS[10]["a_seed_base"] == \
                    WAVE_CONFIGS[9]["a_seed_base"] + A_N, \
                    "W10 A stride drift (arithmetic continuation, no skip)"
                assert WAVE_CONFIGS[10]["b_exit_seed_base"] == \
                    WAVE_CONFIGS[9]["b_exit_seed_base"] + B_N, \
                    "W10 B stride drift (arithmetic continuation, no skip)"
                assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W10-SHARD-0",
                                                  "n1w10-0of12"), "W10 entry identity"
                assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W10-SHARD-11",
                                                   "n1w10-11of12")
                assert SHARD_DIR.endswith("n1_w10") and OUT.endswith(
                    "n1_w10_results.json"), "W10 path drift"
                for wprev in (2, 3, 4, 5, 6, 7, 8, 9):
                    assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                        PATHS.results_dir, "p2cal_ext",
                        WAVE_CONFIGS[wprev]["shard_subdir"])), \
                        f"W10 shard dir collides with W{wprev}"
                assert os.path.exists(os.path.join(
                    PATHS.root, "research", "PERPETUAL_N1_W10_PREREG.md")), \
                    "W10 per-wave prereg missing (materializer requirement)"
                # W10 finalize cumulative dep (W9 output) = IN FLIGHT at
                # drafting (12/12 burned pool-side, finalize queued) -- no
                # static exists-assert here: it would false-red now and
                # expire later (r307 two-state lesson family, W7 leg same
                # pattern); the finalize merge loop is FAIL-CLOSED on any
                # missing prior-wave output at run time, which is the real
                # guard.
                assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
            finally:
                _set_wave(2)
        finally:
            _set_wave(2)
    finally:
        _set_wave(2)
    # --- wave-11 face (r510 bm-b, never-dry supply law: SECOND
    #     ENGINE-OWNED WAVE, engine_owner=bm-b; arithmetic continuation
    #     BOTH tails clean per the W10 row's projection + prereg-time ADMIT
    #     receipt results/_r510bmb_w11_band_gate.py; standalone leg --
    #     try/finally restores the W2 default face either way) ---
    _set_wave(11)
    try:
        assert WAVE_CONFIGS[11]["a_seed_base"] == pf.N1_BANDS[11]["a"][0], \
            "W11 A band drift vs law mirror"
        assert WAVE_CONFIGS[11]["b_exit_seed_base"] == \
            pf.N1_BANDS[11]["b_exit"][0], "W11 B band drift vs law mirror"
        assert WAVE_CONFIGS[11].get("engine_owner") == \
            pf.N1_BANDS[11].get("engine_owner") == "bm-b", \
            "W11 engine_owner drift (law mirror parity)"
        w11_a = {A_SEED_BASE + j for j in range(A_N)}
        w11_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w11_a & w11_b), "W11 A/B band overlap"
        assert not (w11_a & reg_ints) and not (w11_b & reg_ints), \
            "W11 hits SEED_REGISTRY"
        for nm, band in (("A", w11_a), ("B", w11_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W11 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W11 {nm} hits W1"
            assert not (band & probes), f"W11 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10):
            assert not (w11_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W11 A hits W{wprev}"
            assert not (w11_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W11 B hits W{wprev}"
        # arithmetic continuation facts (law sec.4 W11 row): both tails
        # land clean (W10 row projection + prereg-time ADMIT receipt) --
        # A sits at W10 A end + 1, B at W10 B end + 1, strides verbatim,
        # no skip-over refusal facts this wave.
        lfc_actual11 = set(range(30_000, 30_100))
        assert not (w11_a & lfc_actual11) and not (w11_b & lfc_actual11), \
            "W11 bands must clear the lfc actual draw range"
        assert WAVE_CONFIGS[11]["a_seed_base"] == \
            WAVE_CONFIGS[10]["a_seed_base"] + A_N, \
            "W11 A stride drift (arithmetic continuation, no skip)"
        assert WAVE_CONFIGS[11]["b_exit_seed_base"] == \
            WAVE_CONFIGS[10]["b_exit_seed_base"] + B_N, \
            "W11 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W11-SHARD-0",
                                          "n1w11-0of12"), "W11 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W11-SHARD-11",
                                           "n1w11-11of12")
        assert SHARD_DIR.endswith("n1_w11") and OUT.endswith(
            "n1_w11_results.json"), "W11 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W11 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W11_PREREG.md")), \
            "W11 per-wave prereg missing (materializer requirement)"
        # W11 finalize cumulative dep (W10 output) = PRESENT at drafting
        # time (W10 finalize landed r509 before this freeze) -- static
        # exists-assert holds and never expires (r307 two-state law
        # family; contrast the W10 leg's in-flight runtime guard).
        assert os.path.exists(os.path.join(
            OUT_DIR, WAVE_CONFIGS[10]["out_name"])), \
            "W11 finalize cumulative dep (W10 output) missing"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- wave-12 face (r523 bm-a, never-dry supply law: THIRD
    #     ENGINE-OWNED WAVE, FIRST bm-a-owned, engine_owner=bm-a;
    #     A = FORCED SKIP-OVER per the W11 row's W12+ WARNING projection
    #     (arithmetic tail 38_100..40_099 REFUSED on N2/N4 probe points
    #     40_000/40_001 + SEED_REGISTRY 40_000/40_050; first clean
    #     2,000-window 63_050..65_049 per ADMIT receipt
    #     results/_r523bma_w12_band_gate.py); B = arithmetic +200 clean;
    #     standalone leg -- try/finally restores the W2 default face) ---
    _set_wave(12)
    try:
        assert WAVE_CONFIGS[12]["a_seed_base"] == pf.N1_BANDS[12]["a"][0], \
            "W12 A band drift vs law mirror"
        assert WAVE_CONFIGS[12]["b_exit_seed_base"] == \
            pf.N1_BANDS[12]["b_exit"][0], "W12 B band drift vs law mirror"
        assert WAVE_CONFIGS[12].get("engine_owner") == \
            pf.N1_BANDS[12].get("engine_owner") == "bm-a", \
            "W12 engine_owner drift (law mirror parity)"
        w12_a = {A_SEED_BASE + j for j in range(A_N)}
        w12_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w12_a & w12_b), "W12 A/B band overlap"
        assert not (w12_a & reg_ints) and not (w12_b & reg_ints), \
            "W12 hits SEED_REGISTRY"
        for nm, band in (("A", w12_a), ("B", w12_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W12 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W12 {nm} hits W1"
            assert not (band & probes), f"W12 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11):
            assert not (w12_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W12 A hits W{wprev}"
            assert not (w12_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                for j in range(B_N)}), f"W12 B hits W{wprev}"
        # forced skip-over facts (law sec.4 W12 row): the arithmetic +2_000
        # tail (W11 A end + 1 .. +2_000) is REFUSED (N2/N4 probe points
        # 40_000/40_001 + SEED_REGISTRY new_signal_p1 40_000 /
        # new_signal_p1_ce 40_050 -- machine evidence leg1 of the ADMIT
        # receipt); A packs at the FIRST 2,000-window clear of every
        # reserved band AND the actual draw ranges -- lfc 30_000..30_099
        # (leg-3e family) AND options_wave2 63_000..63_049 (K=50, new
        # avoidance face this wave); B keeps the +200 stride verbatim.
        lfc_actual12 = set(range(30_000, 30_100))
        options_actual12 = set(range(63_000, 63_050))
        assert not (w12_a & lfc_actual12) and not (w12_b & lfc_actual12), \
            "W12 bands must clear the lfc actual draw range"
        assert not (w12_a & options_actual12) and \
            not (w12_b & options_actual12), \
            "W12 bands must clear the options_wave2 actual draw range"
        arith_lo = WAVE_CONFIGS[11]["a_seed_base"] + A_N
        arith_hits12 = sorted(v for v in reg_ints | {40_000, 40_001}
                              if arith_lo <= v <= arith_lo + A_N - 1)
        assert arith_hits12, "W12 skip-over must be forced (arithmetic tail clean?)"
        assert WAVE_CONFIGS[12]["a_seed_base"] > arith_lo, \
            "W12 A must skip past the refused arithmetic tail"
        assert WAVE_CONFIGS[12]["b_exit_seed_base"] == \
            WAVE_CONFIGS[11]["b_exit_seed_base"] + B_N, \
            "W12 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W12-SHARD-0",
                                          "n1w12-0of12"), "W12 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W12-SHARD-11",
                                           "n1w12-11of12")
        assert SHARD_DIR.endswith("n1_w12") and OUT.endswith(
            "n1_w12_results.json"), "W12 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W12 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W12_PREREG.md")), \
            "W12 per-wave prereg missing (materializer requirement)"
        # W12 finalize cumulative dep (W11 output) = IN FLIGHT at drafting
        # (bm-b engine burning W11 shards, finalize queued on bm-b) -- no
        # static exists-assert here: it would false-red now and expire
        # later (r307 two-state lesson family, W10 leg same pattern); the
        # finalize merge loop is FAIL-CLOSED on any missing prior-wave
        # output at run time, which is the real guard.
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- wave-13 face (r512 bm-b, never-dry supply law standing step =
    #     the r512 watermark-red anti-idle root fix: FOURTH ENGINE-OWNED
    #     WAVE, engine_owner=bm-b per sovereignty rotation law; A = FORCED
    #     SKIP-OVER per the W12 row's W13+ WARNING projection (arithmetic
    #     tail 65_050..67_049 REFUSED on SEED_REGISTRY cluster
    #     bond_carry_w3a 66_000 / p1e_zoo_behavior 67_000; first clean
    #     2,000-window 70_001..72_000 per ADMIT receipt
    #     results/_r512bmb_w13_band_gate.py); B = arithmetic +200 clean;
    #     standalone leg -- try/finally restores the W2 default face) ---
    _set_wave(13)
    try:
        assert WAVE_CONFIGS[13]["a_seed_base"] == pf.N1_BANDS[13]["a"][0], \
            "W13 A band drift vs law mirror"
        assert WAVE_CONFIGS[13]["b_exit_seed_base"] == \
            pf.N1_BANDS[13]["b_exit"][0], "W13 B band drift vs law mirror"
        assert WAVE_CONFIGS[13].get("engine_owner") == \
            pf.N1_BANDS[13].get("engine_owner") == "bm-b", \
            "W13 engine_owner drift (law mirror parity)"
        w13_a = {A_SEED_BASE + j for j in range(A_N)}
        w13_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w13_a & w13_b), "W13 A/B band overlap"
        assert not (w13_a & reg_ints) and not (w13_b & reg_ints), \
            "W13 hits SEED_REGISTRY"
        for nm, band in (("A", w13_a), ("B", w13_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W13 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W13 {nm} hits W1"
            assert not (band & probes), f"W13 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
            assert not (w13_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W13 A hits W{wprev}"
            assert not (w13_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                for j in range(B_N)}), f"W13 B hits W{wprev}"
        # forced skip-over facts (law sec.4 W13 row): the arithmetic +2_000
        # tail (W12 A end + 1 .. +2_000) is REFUSED (SEED_REGISTRY cluster
        # bond_carry_w3a 66_000 / p1e_zoo_behavior 67_000 -- machine
        # evidence leg1 of the ADMIT receipt); A packs at the first
        # 2,000-window clear of every reserved band AND the actual draw
        # ranges carried forward from W12's avoidance faces (lfc
        # 30_000..30_099, options_wave2 63_000..63_049); B keeps the
        # +200 stride verbatim.
        assert not (w13_a & lfc_actual12) and not (w13_b & lfc_actual12), \
            "W13 bands must clear the lfc actual draw range"
        assert not (w13_a & options_actual12) and \
            not (w13_b & options_actual12), \
            "W13 bands must clear the options_wave2 actual draw range"
        arith_lo13 = WAVE_CONFIGS[12]["a_seed_base"] + A_N
        arith_hits13 = sorted(v for v in reg_ints
                              if arith_lo13 <= v <= arith_lo13 + A_N - 1)
        assert arith_hits13 == [66_000, 67_000], \
            "W13 skip-over must be forced (arithmetic tail clean?)"
        assert WAVE_CONFIGS[13]["a_seed_base"] > arith_lo13, \
            "W13 A must skip past the refused arithmetic tail"
        assert WAVE_CONFIGS[13]["b_exit_seed_base"] == \
            WAVE_CONFIGS[12]["b_exit_seed_base"] + B_N, \
            "W13 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W13-SHARD-0",
                                          "n1w13-0of12"), "W13 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W13-SHARD-11",
                                           "n1w13-11of12")
        assert SHARD_DIR.endswith("n1_w13") and OUT.endswith(
            "n1_w13_results.json"), "W13 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W13 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W13_PREREG.md")), \
            "W13 per-wave prereg missing (materializer requirement)"
        # W13 finalize cumulative dep (W12 output) = PRESENT at leg-writing
        # time (bm-a r524 closeout landed W12 finalize before this leg)
        # -- static exists-assert holds and never expires (r307 two-state
        # law family; the finalize merge loop stays FAIL-CLOSED at runtime).
        assert os.path.exists(os.path.join(
            OUT_DIR, WAVE_CONFIGS[12]["out_name"])), \
            "W13 finalize cumulative dep (W12 output) missing"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- wave-14 face (r325 bm-c, never-dry supply law standing step =
    #     the r325 watermark-red anti-idle root fix: FIFTH ENGINE-OWNED
    #     WAVE, engine_owner=bm-c per sovereignty rotation law
    #     F-20261001-01 slot (W13=bm-b anchored, W14=bm-c); BOTH
    #     arithmetic tails land clean exactly as the W13 row's W14+
    #     WARNING projected (A 72_001 == W13 A end + 1, B 29_500 ==
    #     W13 B end + 1) -- no forced skip, stride kept verbatim per
    #     ADMIT receipt results/_r325bmc_w14_band_gate.py; standalone
    #     leg -- try/finally restores the W2 default face) ---
    _set_wave(14)
    try:
        assert WAVE_CONFIGS[14]["a_seed_base"] == pf.N1_BANDS[14]["a"][0], \
            "W14 A band drift vs law mirror"
        assert WAVE_CONFIGS[14]["b_exit_seed_base"] == \
            pf.N1_BANDS[14]["b_exit"][0], "W14 B band drift vs law mirror"
        assert WAVE_CONFIGS[14].get("engine_owner") == \
            pf.N1_BANDS[14].get("engine_owner") == "bm-c", \
            "W14 engine_owner drift (law mirror parity)"
        w14_a = {A_SEED_BASE + j for j in range(A_N)}
        w14_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w14_a & w14_b), "W14 A/B band overlap"
        assert not (w14_a & reg_ints) and not (w14_b & reg_ints), \
            "W14 hits SEED_REGISTRY"
        for nm, band in (("A", w14_a), ("B", w14_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W14 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W14 {nm} hits W1"
            assert not (band & probes), f"W14 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13):
            assert not (w14_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W14 A hits W{wprev}"
            assert not (w14_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                for j in range(B_N)}), f"W14 B hits W{wprev}"
        # arithmetic-continuation facts (law sec.4 W14 row): the +2_000
        # tail (W13 A end + 1 .. +2_000) and the +200 tail (W13 B end + 1
        # .. +200) both land CLEAN -- machine evidence leg1 of the ADMIT
        # receipt (results/_r325bmc_w14_band_gate.py); stride kept
        # verbatim, NO skip (skip-over would need REFUSED evidence).
        assert not (w14_a & lfc_actual12) and not (w14_b & lfc_actual12), \
            "W14 bands must clear the lfc actual draw range"
        assert not (w14_a & options_actual12) and \
            not (w14_b & options_actual12), \
            "W14 bands must clear the options_wave2 actual draw range"
        arith_lo14 = WAVE_CONFIGS[13]["a_seed_base"] + A_N
        arith_hits14 = sorted(v for v in reg_ints
                              if arith_lo14 <= v <= arith_lo14 + A_N - 1)
        assert arith_hits14 == [], \
            "W14 arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[14]["a_seed_base"] == arith_lo14, \
            "W14 A stride drift (arithmetic continuation, NO skip)"
        assert WAVE_CONFIGS[14]["b_exit_seed_base"] == \
            WAVE_CONFIGS[13]["b_exit_seed_base"] + B_N, \
            "W14 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W14-SHARD-0",
                                          "n1w14-0of12"), "W14 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W14-SHARD-11",
                                           "n1w14-11of12")
        assert SHARD_DIR.endswith("n1_w14") and OUT.endswith(
            "n1_w14_results.json"), "W14 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W14 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W14_PREREG.md")), \
            "W14 per-wave prereg missing (materializer requirement)"
        # W14 finalize cumulative dep (W13 output) = PRESENT at leg-writing
        # time (bm-b r513 finalize landed before this leg) -- static
        # exists-assert holds and never expires (r307 two-state law
        # family; the finalize merge loop stays FAIL-CLOSED at runtime).
        assert os.path.exists(os.path.join(
            OUT_DIR, WAVE_CONFIGS[13]["out_name"])), \
            "W14 finalize cumulative dep (W13 output) missing"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- wave-16 face (r515 bm-b, never-dry supply law standing step =
    #     the r515 watermark-red anti-idle root fix: SIXTH ENGINE-OWNED
    #     WAVE, engine_owner=bm-b per sovereignty rotation law
    #     F-20261001-01 slot (W13=bm-b anchored, +3 -> W16=bm-b;
    #     unified wave number 15 concurrently held by bm-a's N2-W15
    #     draft -- N1 face numbering continues at W16 with no W15 row);
    #     BOTH arithmetic tails land clean exactly as the W14 row's
    #     W15+ WARNING projected (A 74_001 == W14 A end + 1, B 29_700 ==
    #     W14 B end + 1) -- no forced skip, stride kept verbatim per
    #     ADMIT receipt results/_r515bmb_w16_band_gate.py; standalone
    #     leg -- try/finally restores the W2 default face) ---
    _set_wave(16)
    try:
        assert WAVE_CONFIGS[16]["a_seed_base"] == pf.N1_BANDS[16]["a"][0], \
            "W16 A band drift vs law mirror"
        assert WAVE_CONFIGS[16]["b_exit_seed_base"] == \
            pf.N1_BANDS[16]["b_exit"][0], "W16 B band drift vs law mirror"
        assert WAVE_CONFIGS[16].get("engine_owner") == \
            pf.N1_BANDS[16].get("engine_owner") == "bm-b", \
            "W16 engine_owner drift (law mirror parity)"
        w16_a = {A_SEED_BASE + j for j in range(A_N)}
        w16_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w16_a & w16_b), "W16 A/B band overlap"
        assert not (w16_a & reg_ints) and not (w16_b & reg_ints), \
            "W16 hits SEED_REGISTRY"
        for nm, band in (("A", w16_a), ("B", w16_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W16 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W16 {nm} hits W1"
            assert not (band & probes), f"W16 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14):
            assert not (w16_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W16 A hits W{wprev}"
            assert not (w16_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                for j in range(B_N)}), f"W16 B hits W{wprev}"
        # arithmetic-continuation facts (law sec.4 W16 row): the +2_000
        # tail (W14 A end + 1 .. +2_000) and the +200 tail (W14 B end + 1
        # .. +200) both land CLEAN -- machine evidence leg1 of the ADMIT
        # receipt (results/_r515bmb_w16_band_gate.py); stride kept
        # verbatim, NO skip (skip-over would need REFUSED evidence).
        assert not (w16_a & lfc_actual12) and not (w16_b & lfc_actual12), \
            "W16 bands must clear the lfc actual draw range"
        assert not (w16_a & options_actual12) and \
            not (w16_b & options_actual12), \
            "W16 bands must clear the options_wave2 actual draw range"
        arith_lo16 = WAVE_CONFIGS[14]["a_seed_base"] + A_N
        arith_hits16 = sorted(v for v in reg_ints
                              if arith_lo16 <= v <= arith_lo16 + A_N - 1)
        assert arith_hits16 == [], \
            "W16 arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[16]["a_seed_base"] == arith_lo16, \
            "W16 A stride drift (arithmetic continuation, NO skip)"
        assert WAVE_CONFIGS[16]["b_exit_seed_base"] == \
            WAVE_CONFIGS[14]["b_exit_seed_base"] + B_N, \
            "W16 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W16-SHARD-0",
                                          "n1w16-0of12"), "W16 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W16-SHARD-11",
                                          "n1w16-11of12")
        assert SHARD_DIR.endswith("n1_w16") and OUT.endswith(
            "n1_w16_results.json"), "W16 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W16 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W16_PREREG.md")), \
            "W16 per-wave prereg missing (materializer requirement)"
        # W16 finalize cumulative dep (W14 output) = PRESENT at leg-writing
        # time (bm-c r325 finalize landed before this leg) -- static
        # exists-assert holds and never expires (r307 two-state law
        # family; the finalize merge loop stays FAIL-CLOSED at runtime).
        assert os.path.exists(os.path.join(
            OUT_DIR, WAVE_CONFIGS[14]["out_name"])), \
            "W16 finalize cumulative dep (W14 output) missing"
        # finalize wave-set derivation face (r511 derive law, W16 gap
        # law): unified wave number 15 is held by the N2 face, so the
        # N1 registry keys below W16 run 2..14 -- the finalize
        # cumulative loop derives from registry keys (sorted < wave),
        # never a contiguous range(2, wave) (live KeyError caught at
        # the first gap-tolerant finalize, fixed same window).
        assert sorted(w for w in WAVE_CONFIGS if w < 16) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], \
            "W16 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- wave-17 face (r328 bm-c, never-dry supply law standing step =
    #     the r328 watermark-red anti-idle root fix: SEVENTH ENGINE-OWNED
    #     WAVE, engine_owner=bm-c per sovereignty rotation law
    #     F-20261001-01 slot (W14=bm-c anchored, +3 -> W17=bm-c; wave
    #     number 15 remains held by bm-a's N2-W15 draft); SPLIT tails
    #     per the W16 row's W17+ WARNING: A +2_000 arithmetic tail
    #     (76_001 == W16 A end + 1) lands CLEAN -- stride kept verbatim,
    #     NO skip; B +200 arithmetic tail (29_900..30_099) is REFUSED
    #     (lfc actual draw 30_000..30_099, SEED_REGISTRY point 30_000
    #     inside) -- B re-bases past every reserved band incl. this
    #     wave's own A band, packing at the first clean 200-window
    #     (38_100..38_299, W11 A end + 1) per the W5/W6/W8/W12
    #     forced-skip-over family, ADMIT receipt
    #     results/_r328bmc_w17_band_gate.py; standalone leg --
    #     try/finally restores the W2 default face) ---
    _set_wave(17)
    try:
        assert WAVE_CONFIGS[17]["a_seed_base"] == pf.N1_BANDS[17]["a"][0], \
            "W17 A band drift vs law mirror"
        assert WAVE_CONFIGS[17]["b_exit_seed_base"] == \
            pf.N1_BANDS[17]["b_exit"][0], "W17 B band drift vs law mirror"
        assert WAVE_CONFIGS[17].get("engine_owner") == \
            pf.N1_BANDS[17].get("engine_owner") == "bm-c", \
            "W17 engine_owner drift (law mirror parity)"
        w17_a = {A_SEED_BASE + j for j in range(A_N)}
        w17_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w17_a & w17_b), "W17 A/B band overlap"
        assert not (w17_a & reg_ints) and not (w17_b & reg_ints), \
            "W17 hits SEED_REGISTRY"
        for nm, band in (("A", w17_a), ("B", w17_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W17 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W17 {nm} hits W1"
            assert not (band & probes), f"W17 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16):
            assert not (w17_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W17 A hits W{wprev}"
            assert not (w17_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W17 B hits W{wprev}"
        # split-tail facts (law sec.4 W17 row): A arithmetic tail CLEAN
        # (machine evidence leg1-A of the ADMIT receipt) -- stride kept
        # verbatim, NO skip; B arithmetic tail REFUSED (leg1-B refusal
        # facts: lfc actual 30_000..30_099 + SEED_REGISTRY 30_000) --
        # skip-over FORCED, B packs past every reserved band.
        assert not (w17_a & lfc_actual12) and not (w17_b & lfc_actual12), \
            "W17 bands must clear the lfc actual draw range"
        assert not (w17_a & options_actual12) and \
            not (w17_b & options_actual12), \
            "W17 bands must clear the options_wave2 actual draw range"
        arith_lo17 = WAVE_CONFIGS[16]["a_seed_base"] + A_N
        arith_hits17 = sorted(v for v in reg_ints
                              if arith_lo17 <= v <= arith_lo17 + A_N - 1)
        assert arith_hits17 == [], \
            "W17 A arithmetic tail must be clean (ADMIT receipt leg1-A)"
        assert WAVE_CONFIGS[17]["a_seed_base"] == arith_lo17, \
            "W17 A stride drift (arithmetic continuation, NO skip)"
        arith_b_lo17 = WAVE_CONFIGS[16]["b_exit_seed_base"] + B_N
        assert set(range(arith_b_lo17, arith_b_lo17 + B_N)) & lfc_actual12, \
            "W17 B skip-over must be forced (arithmetic tail clean?)"
        assert WAVE_CONFIGS[17]["b_exit_seed_base"] > arith_b_lo17, \
            "W17 B must skip past the refused arithmetic tail"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W17-SHARD-0",
                                          "n1w17-0of12"), "W17 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W17-SHARD-11",
                                          "n1w17-11of12")
        assert SHARD_DIR.endswith("n1_w17") and OUT.endswith(
            "n1_w17_results.json"), "W17 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W17 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W17_PREREG.md")), \
            "W17 per-wave prereg missing (materializer requirement)"
        # W17 finalize cumulative dep (W16 output) = PRESENT at
        # leg-writing time (bm-b r516 finalize landed before this leg)
        # -- static exists-assert holds and never expires (r307
        # two-state law family; the finalize merge loop stays
        # FAIL-CLOSED at runtime).
        assert os.path.exists(os.path.join(
            OUT_DIR, WAVE_CONFIGS[16]["out_name"])), \
            "W17 finalize cumulative dep (W16 output) missing"
        # finalize wave-set derivation face (r511 derive law, gap law):
        # registry keys below W17 run 2..14 + 16 (no 15) -- derive from
        # registry keys, never a contiguous range.
        assert sorted(w for w in WAVE_CONFIGS if w < 17) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16], \
            "W17 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- wave-18 face (r531 bm-a, never-dry supply law standing step =
    #     the anti-idle root fix after the W17 close: EIGHTH
    #     ENGINE-OWNED WAVE, engine_owner=bm-a per sovereignty
    #     rotation law F-20261001-01 slot (law sec.4 W17 row verbatim
    #     "W18=bm-a slot"; rotation arithmetic 17+3=20 goes to bm-c);
    #     bm-a's SECOND owned N1 wave after W12; wave number 15
    #     remains held by bm-a's N2-W15 draft; freeze window opened
    #     only AFTER the W17xW19 same-band double-freeze adjudication
    #     landed (MSG-184x/185x commit-time ruling: W17 stands, bm-b
    #     W19 yields; mirrors healed by bm-c 6efed57b6); BOTH tails
    #     arithmetic-clean for the first time since the W5/W6/W8/W12/
    #     W17 B-skip family -- A's +2_000 tail (78_001 == W17 A end
    #     + 1) and B's +200 tail (38_300 == W17 B end + 1) both pack
    #     arithmetic per the W17 row's W18+ WARNING projection; ADMIT
    #     receipt results/_r530bma_w18_band_gate.py (r530 bm-a draft
    #     window, crashed session), ADMIT re-verified against the
    #     HEAD 15-row pre-W18 table by results/_r531bma_w18_admit_
    #     reverify.py (r531 bm-a adoption window, r314 adopt-after-
    #     verify law); carries the r529-mandated N3 actual-seed-set
    #     leg (70_000..70_005); standalone leg -- try/finally
    #     restores the W2 default face) ---
    _set_wave(18)
    try:
        assert WAVE_CONFIGS[18]["a_seed_base"] == pf.N1_BANDS[18]["a"][0], \
            "W18 A band drift vs law mirror"
        assert WAVE_CONFIGS[18]["b_exit_seed_base"] == \
            pf.N1_BANDS[18]["b_exit"][0], "W18 B band drift vs law mirror"
        assert WAVE_CONFIGS[18].get("engine_owner") == \
            pf.N1_BANDS[18].get("engine_owner") == "bm-a", \
            "W18 engine_owner drift (law mirror parity)"
        w18_a = {A_SEED_BASE + j for j in range(A_N)}
        w18_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w18_a & w18_b), "W18 A/B band overlap"
        assert not (w18_a & reg_ints) and not (w18_b & reg_ints), \
            "W18 hits SEED_REGISTRY"
        for nm, band in (("A", w18_a), ("B", w18_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W18 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W18 {nm} hits W1"
            assert not (band & probes), f"W18 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17):
            assert not (w18_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W18 A hits W{wprev}"
            assert not (w18_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W18 B hits W{wprev}"
        assert not (w18_a & lfc_actual12) and not (w18_b & lfc_actual12), \
            "W18 bands must clear the lfc actual draw range"
        assert not (w18_a & options_actual12) and \
            not (w18_b & options_actual12), \
            "W18 bands must clear the options_wave2 actual draw range"
        # r529 law-mandated leg: the N3 used-seed SET (actual values,
        # not the registry point) must be disjoint -- single-source
        # derive from perpetual_faces_n3 (SEED_BASE + family index).
        import perpetual_faces_n3 as pf_n3
        n3_r1_seeds = set(range(pf_n3.SEED_BASE,
                                pf_n3.SEED_BASE + len(pf_n3.FAMILIES)))
        assert not (w18_a & n3_r1_seeds) and not (w18_b & n3_r1_seeds), \
            "W18 bands must clear the N3-R1 actual seed set (r529 leg)"
        # both-tails arithmetic facts (law sec.4 W18 row): A +2_000
        # tail (78_001 == W17 A end + 1) and B +200 tail (38_300 ==
        # W17 B end + 1) BOTH land clean -- stride kept verbatim, NO
        # skip on either side (ADMIT receipt leg1/leg2; first
        # both-arithmetic wave since the W5/W6/W8/W12/W17 family).
        arith_lo18 = WAVE_CONFIGS[17]["a_seed_base"] + A_N
        arith_hits18 = sorted(v for v in reg_ints
                              if arith_lo18 <= v <= arith_lo18 + A_N - 1)
        assert arith_hits18 == [], \
            "W18 A arithmetic tail must be clean (ADMIT receipt leg1-A)"
        assert WAVE_CONFIGS[18]["a_seed_base"] == arith_lo18, \
            "W18 A stride drift (arithmetic continuation, NO skip)"
        arith_b_lo18 = WAVE_CONFIGS[17]["b_exit_seed_base"] + B_N
        arith_b_hits18 = sorted(v for v in reg_ints
                                if arith_b_lo18 <= v <= arith_b_lo18 + B_N - 1)
        assert arith_b_hits18 == [], \
            "W18 B arithmetic tail must be clean (ADMIT receipt leg1-B)"
        assert WAVE_CONFIGS[18]["b_exit_seed_base"] == arith_b_lo18, \
            "W18 B stride drift (arithmetic continuation, NO skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W18-SHARD-0",
                                          "n1w18-0of12"), "W18 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W18-SHARD-11",
                                          "n1w18-11of12")
        assert SHARD_DIR.endswith("n1_w18") and OUT.endswith(
            "n1_w18_results.json"), "W18 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W18 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W18_PREREG.md")), \
            "W18 per-wave prereg missing (materializer requirement)"
        # W18 finalize cumulative dep (W17 output) = PRESENT at
        # leg-writing time (bm-c r328 finalize landed 18:3x before this
        # leg) -- static exists-assert holds and never expires (r307
        # two-state law family; the finalize merge loop stays
        # FAIL-CLOSED at runtime).
        assert os.path.exists(os.path.join(
            OUT_DIR, WAVE_CONFIGS[17]["out_name"])), \
            "W18 finalize cumulative dep (W17 output) missing"
        # finalize wave-set derivation face (r511 derive law, gap law):
        # registry keys below W18 run 2..14 + 16 + 17 (no 15) --
        # derive from registry keys, never a contiguous range.
        assert sorted(w for w in WAVE_CONFIGS if w < 18) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17], \
            "W18 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)

    # --- wave-19 face (r517 bm-b freeze + r518 SAME-WINDOW DOUBLE-FREEZE
    #     COLLISION YIELD + re-band per r511 commit-order law and
    #     MSG-20261001-184x: bm-c's W17 rows reached origin first (r328)
    #     while the r517 W19 freeze was drafted blind to it; both
    #     machines deterministic-same-verdict the W16 table-tail
    #     continuation -- bm-b is the latercomer and YIELDS. Old-band
    #     W19 products (12/12 burned, finalize NEVER ran -> zero
    #     science-ledger pollution) all discarded at yield. EIGHTH
    #     ENGINE-OWNED WAVE, engine_owner=bm-b per sovereignty rotation
    #     law F-20261001-01 slot W19=bm-b (wave number 18 unfrozen, gap
    #     notes, r516 derive law). Re-band skips past BOTH W17's
    #     registered bands AND W18's PUBLISHED PROJECTION (rotation
    #     slot W18=bm-a; r511 exhaustive-reservation-scan lesson:
    #     published projections are reserved faces) -- both tails
    #     arithmetic continuation from the W18 projection tail, ADMIT
    #     receipt v3 results/_r517bmb_w19_band_gate.py (incl. the
    #     MSG-183x mandatory N3-R1 used-seed band leg); NOT a re-pick
    #     (R250); standalone leg -- try/finally restores the W2 default
    #     face) ---
    _set_wave(19)
    try:
        assert WAVE_CONFIGS[19]["a_seed_base"] == pf.N1_BANDS[19]["a"][0], \
            "W19 A band drift vs law mirror"
        assert WAVE_CONFIGS[19]["b_exit_seed_base"] == \
            pf.N1_BANDS[19]["b_exit"][0], "W19 B band drift vs law mirror"
        assert WAVE_CONFIGS[19].get("engine_owner") == \
            pf.N1_BANDS[19].get("engine_owner") == "bm-b", \
            "W19 engine_owner drift (law mirror parity)"
        w19_a = {A_SEED_BASE + j for j in range(A_N)}
        w19_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w19_a & w19_b), "W19 A/B band overlap"
        assert not (w19_a & reg_ints) and not (w19_b & reg_ints), \
            "W19 hits SEED_REGISTRY"
        for nm, band in (("A", w19_a), ("B", w19_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W19 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W19 {nm} hits W1"
            assert not (band & probes), f"W19 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17):
            assert not (w19_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W19 A hits W{wprev}"
            assert not (w19_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W19 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W19 bands must clear it.
        n3r1_used = set(range(70_000, 70_006))
        assert not (w19_a & n3r1_used) and not (w19_b & n3r1_used), \
            "W19 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # W18 published-projection reserved-face leg (r511 lesson):
        # W18 (slot bm-a) is projected at A 78_001..80_000 / B
        # 38_300..38_499 (W17 row W18+ WARNING + bm-a r529 gate
        # projection CLEAN) -- W19 must clear it entirely.
        w18_proj_a = set(range(78_001, 80_001))
        w18_proj_b = set(range(38_300, 38_500))
        assert not (w19_a & w18_proj_a) and not (w19_b & w18_proj_b), \
            "W19 bands hit W18's published projection (slot bm-a reserved)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w19_a & lfc_actual12) and not (w19_b & lfc_actual12), \
            "W19 bands must clear the lfc actual draw range"
        assert not (w19_a & options_actual12) and \
            not (w19_b & options_actual12), \
            "W19 bands must clear the options_wave2 actual draw range"
        # re-based arithmetic facts (law sec.4 W19 row, r511 yield):
        # BOTH tails continue from the W18 published projection (the
        # new reservation tail) and land CLEAN -- strides kept verbatim,
        # NO skip; the W17-tail arithmetic position (78_001..80_000 /
        # 38_300..38_499) is REFUSED for W19 by slot precedence (it IS
        # W18's projection -- machine gate v3 leg2 refusal facts), NOT a
        # re-pick (R250).
        arith_lo19 = 78_001 + A_N          # W18 projected A end + 1
        arith_hits19 = sorted(v for v in reg_ints
                              if arith_lo19 <= v <= arith_lo19 + A_N - 1)
        assert arith_hits19 == [], \
            "W19 A arithmetic tail must be clean (ADMIT receipt v3 leg1)"
        assert WAVE_CONFIGS[19]["a_seed_base"] == arith_lo19, \
            "W19 A stride drift (arithmetic continuation past W18 proj, NO skip)"
        b_arith_lo19 = 38_300 + B_N        # W18 projected B end + 1
        b_arith_hits19 = sorted(v for v in reg_ints
                                if b_arith_lo19 <= v <= b_arith_lo19 + B_N - 1)
        assert b_arith_hits19 == [], \
            "W19 B arithmetic tail must be clean (ADMIT receipt v3 leg1)"
        assert WAVE_CONFIGS[19]["b_exit_seed_base"] == b_arith_lo19, \
            "W19 B stride drift (arithmetic continuation past W18 proj, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W19-SHARD-0",
                                          "n1w19-0of12"), "W19 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W19-SHARD-11",
                                           "n1w19-11of12")
        assert SHARD_DIR.endswith("n1_w19") and OUT.endswith(
            "n1_w19_results.json"), "W19 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W19 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W19_PREREG.md")), \
            "W19 per-wave prereg missing (materializer requirement)"
        # W19 finalize cumulative deps: W16 output = PRESENT (bm-b r516
        # finalize landed); W17 output = PRESENT (bm-c r328 finalize
        # landed, K=35,320, ledger 401,948) -- static exists-asserts hold
        # and never expire (r307 two-state law family); the finalize
        # merge loop stays FAIL-CLOSED on any missing prior-wave output
        # at run time.
        assert os.path.exists(os.path.join(
            OUT_DIR, WAVE_CONFIGS[16]["out_name"])), \
            "W19 finalize cumulative dep (W16 output) missing"
        assert os.path.exists(os.path.join(
            OUT_DIR, WAVE_CONFIGS[17]["out_name"])), \
            "W19 finalize cumulative dep (W17 output) missing"
        # finalize wave-set derivation face (r511 derive law, W19 gap
        # law): unified wave number 18 remains unfrozen at this window
        # -- the N1 registry keys below W19 run 2..14 + 16 + 17; the
        # finalize cumulative loop derives from registry keys (sorted <
        # wave), never a contiguous range (r516 W16-gap precedent).
        assert sorted(w for w in WAVE_CONFIGS if w < 19) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18], \
            "W19 prior-wave set must derive from registry keys (no 15; " \
            "18 registered by W18 freeze r531 bm-a -- pin updated per " \
            "post-freeze coherence, derive law unchanged)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W20 materializer face (r330 bm-c freeze) ------------------------
    _set_wave(20)
    try:
        assert WAVE_CONFIGS[20]["a_seed_base"] == pf.N1_BANDS[20]["a"][0], \
            "W20 A band drift vs law mirror"
        assert WAVE_CONFIGS[20]["b_exit_seed_base"] == \
            pf.N1_BANDS[20]["b_exit"][0], "W20 B band drift vs law mirror"
        assert WAVE_CONFIGS[20].get("engine_owner") == \
            pf.N1_BANDS[20].get("engine_owner") == "bm-c", \
            "W20 engine_owner drift (law mirror parity)"
        w20_a = {A_SEED_BASE + j for j in range(A_N)}
        w20_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w20_a & w20_b), "W20 A/B band overlap"
        assert not (w20_a & reg_ints) and not (w20_b & reg_ints), \
            "W20 hits SEED_REGISTRY"
        for nm, band in (("A", w20_a), ("B", w20_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W20 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W20 {nm} hits W1"
            assert not (band & probes), f"W20 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19):
            assert not (w20_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W20 A hits W{wprev}"
            assert not (w20_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W20 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W20 bands must clear it.
        n3r1_used = set(range(70_000, 70_006))
        assert not (w20_a & n3r1_used) and not (w20_b & n3r1_used), \
            "W20 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w20_a & lfc_actual12) and not (w20_b & lfc_actual12), \
            "W20 bands must clear the lfc actual draw range"
        assert not (w20_a & options_actual12) and \
            not (w20_b & options_actual12), \
            "W20 bands must clear the options_wave2 actual draw range"
        # arithmetic facts (law sec.4 W20 row, r330): BOTH tails continue
        # from the W19 REGISTERED tail (registry-derived, not prose) and
        # land CLEAN -- strides kept verbatim, NO skip (ADMIT receipt
        # results/_r330bmc_w20_band_gate.py leg1/leg2).
        arith_lo20 = pf.N1_BANDS[19]["a"][1] + 1     # W19 registered A end + 1
        arith_hits20 = sorted(v for v in reg_ints
                              if arith_lo20 <= v <= arith_lo20 + A_N - 1)
        assert arith_hits20 == [], \
            "W20 A arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[20]["a_seed_base"] == arith_lo20, \
            "W20 A stride drift (arithmetic continuation, NO skip)"
        b_arith_lo20 = pf.N1_BANDS[19]["b_exit"][1] + 1  # W19 reg B end + 1
        b_arith_hits20 = sorted(v for v in reg_ints
                                if b_arith_lo20 <= v <= b_arith_lo20 + B_N - 1)
        assert b_arith_hits20 == [], \
            "W20 B arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[20]["b_exit_seed_base"] == b_arith_lo20, \
            "W20 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W20-SHARD-0",
                                          "n1w20-0of12"), "W20 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W20-SHARD-11",
                                           "n1w20-11of12")
        assert SHARD_DIR.endswith("n1_w20") and OUT.endswith(
            "n1_w20_results.json"), "W20 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W20 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W20_PREREG.md")), \
            "W20 per-wave prereg missing (materializer requirement)"
        # W20 finalize cumulative deps: W17 output = PRESENT (bm-c r328
        # finalize landed, K=35,320, ledger 401,948). W18/W19 finalize
        # outputs are NOT landed at this freeze window (bm-a/bm-b engines
        # burning) -- no static exists-assert pinned for them; the
        # finalize merge loop stays FAIL-CLOSED on any missing prior-wave
        # output at run time (r307 two-state law family).
        assert os.path.exists(os.path.join(
            OUT_DIR, WAVE_CONFIGS[17]["out_name"])), \
            "W20 finalize cumulative dep (W17 output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 20 (no 15; 18/19
        # registered by the r531/r517 freezes).
        assert sorted(w for w in WAVE_CONFIGS if w < 20) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19], \
            "W20 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W21 materializer face (r533 bm-a freeze) ------------------------
    _set_wave(21)
    try:
        assert WAVE_CONFIGS[21]["a_seed_base"] == pf.N1_BANDS[21]["a"][0], \
            "W21 A band drift vs law mirror"
        assert WAVE_CONFIGS[21]["b_exit_seed_base"] == \
            pf.N1_BANDS[21]["b_exit"][0], "W21 B band drift vs law mirror"
        assert WAVE_CONFIGS[21].get("engine_owner") == \
            pf.N1_BANDS[21].get("engine_owner") == "bm-a", \
            "W21 engine_owner drift (law mirror parity)"
        w21_a = {A_SEED_BASE + j for j in range(A_N)}
        w21_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w21_a & w21_b), "W21 A/B band overlap"
        assert not (w21_a & reg_ints) and not (w21_b & reg_ints), \
            "W21 hits SEED_REGISTRY"
        for nm, band in (("A", w21_a), ("B", w21_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W21 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W21 {nm} hits W1"
            assert not (band & probes), f"W21 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20):
            assert not (w21_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W21 A hits W{wprev}"
            assert not (w21_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W21 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W21 bands must clear it.
        n3r1_used21 = set(range(70_000, 70_006))
        assert not (w21_a & n3r1_used21) and not (w21_b & n3r1_used21), \
            "W21 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w21_a & lfc_actual12) and not (w21_b & lfc_actual12), \
            "W21 bands must clear the lfc actual draw range"
        assert not (w21_a & options_actual12) and \
            not (w21_b & options_actual12), \
            "W21 bands must clear the options_wave2 actual draw range"
        # arithmetic facts (law sec.4 W21 row, r533): BOTH tails continue
        # from the W20 REGISTERED tail (registry-derived, not prose) and
        # land CLEAN -- strides kept verbatim, NO skip (ADMIT receipt
        # results/_r533bma_w21_band_gate.py leg1/leg2).
        arith_lo21 = pf.N1_BANDS[20]["a"][1] + 1     # W20 registered A end + 1
        arith_hits21 = sorted(v for v in reg_ints
                              if arith_lo21 <= v <= arith_lo21 + A_N - 1)
        assert arith_hits21 == [], \
            "W21 A arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[21]["a_seed_base"] == arith_lo21, \
            "W21 A stride drift (arithmetic continuation, NO skip)"
        b_arith_lo21 = pf.N1_BANDS[20]["b_exit"][1] + 1  # W20 reg B end + 1
        b_arith_hits21 = sorted(v for v in reg_ints
                                if b_arith_lo21 <= v <= b_arith_lo21 + B_N - 1)
        assert b_arith_hits21 == [], \
            "W21 B arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[21]["b_exit_seed_base"] == b_arith_lo21, \
            "W21 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W21-SHARD-0",
                                          "n1w21-0of12"), "W21 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W21-SHARD-11",
                                           "n1w21-11of12")
        assert SHARD_DIR.endswith("n1_w21") and OUT.endswith(
            "n1_w21_results.json"), "W21 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W21 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W21_PREREG.md")), \
            "W21 per-wave prereg missing (materializer requirement)"
        # W21 finalize cumulative deps: W17 output PRESENT (bm-c r328),
        # W18 output PRESENT (r532 finalize + r518/r533 restore lineage),
        # W19 output PRESENT (r518 bm-b second finalize = final,
        # ledger 406,348). W20 finalize output NOT landed at this freeze
        # window (bm-c pending) -- no static exists-assert pinned; the
        # finalize merge loop stays FAIL-CLOSED on any missing prior
        # output at run time (r307 two-state law family).
        for _depw in (17, 18, 19):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W21 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 21 (no 15; 20 registered
        # by the r330 bm-c freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 21) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20], \
            "W21 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W22 materializer face (r519 bm-b freeze) ------------------------
    _set_wave(22)
    try:
        assert WAVE_CONFIGS[22]["a_seed_base"] == pf.N1_BANDS[22]["a"][0], \
            "W22 A band drift vs law mirror"
        assert WAVE_CONFIGS[22]["b_exit_seed_base"] == \
            pf.N1_BANDS[22]["b_exit"][0], "W22 B band drift vs law mirror"
        assert WAVE_CONFIGS[22].get("engine_owner") == \
            pf.N1_BANDS[22].get("engine_owner") == "bm-b", \
            "W22 engine_owner drift (law mirror parity)"
        w22_a = {A_SEED_BASE + j for j in range(A_N)}
        w22_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w22_a & w22_b), "W22 A/B band overlap"
        assert not (w22_a & reg_ints) and not (w22_b & reg_ints), \
            "W22 hits SEED_REGISTRY"
        for nm, band in (("A", w22_a), ("B", w22_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W22 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W22 {nm} hits W1"
            assert not (band & probes), f"W22 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21):
            assert not (w22_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W22 A hits W{wprev}"
            assert not (w22_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W22 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W22 bands must clear it.
        n3r1_used22 = set(range(70_000, 70_006))
        assert not (w22_a & n3r1_used22) and not (w22_b & n3r1_used22), \
            "W22 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w22_a & lfc_actual12) and not (w22_b & lfc_actual12), \
            "W22 bands must clear the lfc actual draw range"
        assert not (w22_a & options_actual12) and \
            not (w22_b & options_actual12), \
            "W22 bands must clear the options_wave2 actual draw range"
        # arithmetic facts (law sec.4 W22 row, r519): BOTH tails continue
        # from the W21 REGISTERED tail (registry-derived, not prose) and
        # land CLEAN -- strides kept verbatim, NO skip (ADMIT receipt
        # results/_r519bmb_w22_band_gate.py leg1/leg2).
        arith_lo22 = pf.N1_BANDS[21]["a"][1] + 1     # W21 registered A end + 1
        arith_hits22 = sorted(v for v in reg_ints
                              if arith_lo22 <= v <= arith_lo22 + A_N - 1)
        assert arith_hits22 == [], \
            "W22 A arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[22]["a_seed_base"] == arith_lo22, \
            "W22 A stride drift (arithmetic continuation, NO skip)"
        b_arith_lo22 = pf.N1_BANDS[21]["b_exit"][1] + 1  # W21 reg B end + 1
        b_arith_hits22 = sorted(v for v in reg_ints
                                if b_arith_lo22 <= v <= b_arith_lo22 + B_N - 1)
        assert b_arith_hits22 == [], \
            "W22 B arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[22]["b_exit_seed_base"] == b_arith_lo22, \
            "W22 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W22-SHARD-0",
                                          "n1w22-0of12"), "W22 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W22-SHARD-11",
                                           "n1w22-11of12")
        assert SHARD_DIR.endswith("n1_w22") and OUT.endswith(
            "n1_w22_results.json"), "W22 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W22 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W22_PREREG.md")), \
            "W22 per-wave prereg missing (materializer requirement)"
        # W22 finalize cumulative deps: W17/W18/W19/W20 outputs PRESENT
        # (W20 finalize = bm-c r331, product byte-restored r519 bm-b
        # after the c209aa962 closeout stomp). W21 finalize output NOT
        # landed at this freeze window (bm-a pending) -- no static
        # exists-assert pinned; the finalize merge loop stays
        # FAIL-CLOSED on any missing prior output at run time (r307
        # two-state law family).
        for _depw in (17, 18, 19, 20):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W22 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 22 (no 15; 21 registered
        # by the r533 bm-a freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 22) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21], \
            "W22 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W23 materializer face (r332 bm-c freeze) ------------------------
    _set_wave(23)
    try:
        assert WAVE_CONFIGS[23]["a_seed_base"] == pf.N1_BANDS[23]["a"][0], \
            "W23 A band drift vs law mirror"
        assert WAVE_CONFIGS[23]["b_exit_seed_base"] == \
            pf.N1_BANDS[23]["b_exit"][0], "W23 B band drift vs law mirror"
        assert WAVE_CONFIGS[23].get("engine_owner") == \
            pf.N1_BANDS[23].get("engine_owner") == "bm-c", \
            "W23 engine_owner drift (law mirror parity)"
        w23_a = {A_SEED_BASE + j for j in range(A_N)}
        w23_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w23_a & w23_b), "W23 A/B band overlap"
        assert not (w23_a & reg_ints) and not (w23_b & reg_ints), \
            "W23 hits SEED_REGISTRY"
        for nm, band in (("A", w23_a), ("B", w23_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W23 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W23 {nm} hits W1"
            assert not (band & probes), f"W23 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22):
            assert not (w23_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W23 A hits W{wprev}"
            assert not (w23_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W23 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W23 bands must clear it.
        n3r1_used23 = set(range(70_000, 70_006))
        assert not (w23_a & n3r1_used23) and not (w23_b & n3r1_used23), \
            "W23 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w23_a & lfc_actual12) and not (w23_b & lfc_actual12), \
            "W23 bands must clear the lfc actual draw range"
        assert not (w23_a & options_actual12) and \
            not (w23_b & options_actual12), \
            "W23 bands must clear the options_wave2 actual draw range"
        # arithmetic facts (law sec.4 W23 row, r332): BOTH tails continue
        # from the W22 REGISTERED tail (registry-derived, not prose) and
        # land CLEAN -- strides kept verbatim, NO skip (ADMIT receipt
        # results/_r332bmc_w23_band_gate.py leg1/leg2).
        arith_lo23 = pf.N1_BANDS[22]["a"][1] + 1     # W22 registered A end + 1
        arith_hits23 = sorted(v for v in reg_ints
                              if arith_lo23 <= v <= arith_lo23 + A_N - 1)
        assert arith_hits23 == [], \
            "W23 A arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[23]["a_seed_base"] == arith_lo23, \
            "W23 A stride drift (arithmetic continuation, NO skip)"
        b_arith_lo23 = pf.N1_BANDS[22]["b_exit"][1] + 1  # W22 reg B end + 1
        b_arith_hits23 = sorted(v for v in reg_ints
                                if b_arith_lo23 <= v <= b_arith_lo23 + B_N - 1)
        assert b_arith_hits23 == [], \
            "W23 B arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[23]["b_exit_seed_base"] == b_arith_lo23, \
            "W23 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W23-SHARD-0",
                                          "n1w23-0of12"), "W23 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W23-SHARD-11",
                                           "n1w23-11of12")
        assert SHARD_DIR.endswith("n1_w23") and OUT.endswith(
            "n1_w23_results.json"), "W23 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W23 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W23_PREREG.md")), \
            "W23 per-wave prereg missing (materializer requirement)"
        # W23 finalize cumulative deps: W17/W18/W19/W20 outputs PRESENT
        # (W20 finalize = bm-c r331, product byte-restored r519 bm-b
        # after the c209aa962 closeout stomp, MSG-201x three-face
        # verified). W21 finalize output NOT landed at this freeze
        # window (bm-a burning, r534 pushed shards 6-10) and W22 output
        # not landed (bm-b r519 frozen, engine burn pending) -- no
        # static exists-assert pinned for either; the finalize merge
        # loop stays FAIL-CLOSED on any missing prior output at run
        # time (r307 two-state law family).
        for _depw in (17, 18, 19, 20):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W23 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 23 (no 15; 22 registered
        # by the r519 bm-b freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 23) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22], \
            "W23 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W24 materializer face (r535 bm-a freeze) ------------------------
    _set_wave(24)
    try:
        assert WAVE_CONFIGS[24]["a_seed_base"] == pf.N1_BANDS[24]["a"][0], \
            "W24 A band drift vs law mirror"
        assert WAVE_CONFIGS[24]["b_exit_seed_base"] == \
            pf.N1_BANDS[24]["b_exit"][0], "W24 B band drift vs law mirror"
        assert WAVE_CONFIGS[24].get("engine_owner") == \
            pf.N1_BANDS[24].get("engine_owner") == "bm-a", \
            "W24 engine_owner drift (law mirror parity)"
        w24_a = {A_SEED_BASE + j for j in range(A_N)}
        w24_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w24_a & w24_b), "W24 A/B band overlap"
        assert not (w24_a & reg_ints) and not (w24_b & reg_ints), \
            "W24 hits SEED_REGISTRY"
        for nm, band in (("A", w24_a), ("B", w24_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W24 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W24 {nm} hits W1"
            assert not (band & probes), f"W24 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23):
            assert not (w24_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W24 A hits W{wprev}"
            assert not (w24_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W24 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W24 bands must clear it.
        n3r1_used24 = set(range(70_000, 70_006))
        assert not (w24_a & n3r1_used24) and not (w24_b & n3r1_used24), \
            "W24 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w24_a & lfc_actual12) and not (w24_b & lfc_actual12), \
            "W24 bands must clear the lfc actual draw range"
        assert not (w24_a & options_actual12) and \
            not (w24_b & options_actual12), \
            "W24 bands must clear the options_wave2 actual draw range"
        # arithmetic facts (law sec.4 W24 row, r535): BOTH tails continue
        # from the W23 REGISTERED tail (registry-derived, not prose) and
        # land CLEAN -- strides kept verbatim, NO skip (ADMIT receipt
        # results/_r535bma_w24_band_gate.py leg1/leg2).
        arith_lo24 = pf.N1_BANDS[23]["a"][1] + 1     # W23 registered A end + 1
        arith_hits24 = sorted(v for v in reg_ints
                              if arith_lo24 <= v <= arith_lo24 + A_N - 1)
        assert arith_hits24 == [], \
            "W24 A arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[24]["a_seed_base"] == arith_lo24, \
            "W24 A stride drift (arithmetic continuation, NO skip)"
        b_arith_lo24 = pf.N1_BANDS[23]["b_exit"][1] + 1  # W23 reg B end + 1
        b_arith_hits24 = sorted(v for v in reg_ints
                                if b_arith_lo24 <= v <= b_arith_lo24 + B_N - 1)
        assert b_arith_hits24 == [], \
            "W24 B arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[24]["b_exit_seed_base"] == b_arith_lo24, \
            "W24 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W24-SHARD-0",
                                          "n1w24-0of12"), "W24 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W24-SHARD-11",
                                           "n1w24-11of12")
        assert SHARD_DIR.endswith("n1_w24") and OUT.endswith(
            "n1_w24_results.json"), "W24 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W24 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W24_PREREG.md")), \
            "W24 per-wave prereg missing (materializer requirement)"
        # W24 finalize cumulative deps: W17/W18/W19/W20/W21/W22 outputs
        # PRESENT (W20 finalize = bm-c r331, product byte-restored r519
        # bm-b; W21 finalize = bm-a r534; W22 finalize = bm-b r519
        # addendum, K=46,320, ledger 412,948 chain head). W23 output
        # NOT landed at this freeze window (bm-c r332 frozen, engine
        # burn pending) -- no static exists-assert pinned; the finalize
        # merge loop stays FAIL-CLOSED on any missing prior output at
        # run time (r307 two-state law family).
        for _depw in (17, 18, 19, 20, 21, 22):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W24 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 24 (no 15; 23 registered
        # by the r332 bm-c freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 24) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23], \
            "W24 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W25 materializer face (r520 bm-b freeze) ------------------------
    _set_wave(25)
    try:
        assert WAVE_CONFIGS[25]["a_seed_base"] == pf.N1_BANDS[25]["a"][0], \
            "W25 A band drift vs law mirror"
        assert WAVE_CONFIGS[25]["b_exit_seed_base"] == \
            pf.N1_BANDS[25]["b_exit"][0], "W25 B band drift vs law mirror"
        assert WAVE_CONFIGS[25].get("engine_owner") == \
            pf.N1_BANDS[25].get("engine_owner") == "bm-b", \
            "W25 engine_owner drift (law mirror parity)"
        w25_a = {A_SEED_BASE + j for j in range(A_N)}
        w25_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w25_a & w25_b), "W25 A/B band overlap"
        assert not (w25_a & reg_ints) and not (w25_b & reg_ints), \
            "W25 hits SEED_REGISTRY"
        for nm, band in (("A", w25_a), ("B", w25_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W25 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W25 {nm} hits W1"
            assert not (band & probes), f"W25 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24):
            assert not (w25_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W25 A hits W{wprev}"
            assert not (w25_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W25 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W25 bands must clear it.
        n3r1_used25 = set(range(70_000, 70_006))
        assert not (w25_a & n3r1_used25) and not (w25_b & n3r1_used25), \
            "W25 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w25_a & lfc_actual12) and not (w25_b & lfc_actual12), \
            "W25 bands must clear the lfc actual draw range"
        assert not (w25_a & options_actual12) and \
            not (w25_b & options_actual12), \
            "W25 bands must clear the options_wave2 actual draw range"
        # arithmetic facts (law sec.4 W25 row, r520): BOTH tails continue
        # from the W24 REGISTERED tail (registry-derived, not prose) and
        # land CLEAN -- strides kept verbatim, NO skip (ADMIT receipt
        # results/_r520bmb_w25_band_gate.py leg1/leg2).
        arith_lo25 = pf.N1_BANDS[24]["a"][1] + 1     # W24 registered A end + 1
        arith_hits25 = sorted(v for v in reg_ints
                              if arith_lo25 <= v <= arith_lo25 + A_N - 1)
        assert arith_hits25 == [], \
            "W25 A arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[25]["a_seed_base"] == arith_lo25, \
            "W25 A stride drift (arithmetic continuation, NO skip)"
        b_arith_lo25 = pf.N1_BANDS[24]["b_exit"][1] + 1  # W24 reg B end + 1
        b_arith_hits25 = sorted(v for v in reg_ints
                                if b_arith_lo25 <= v <= b_arith_lo25 + B_N - 1)
        assert b_arith_hits25 == [], \
            "W25 B arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[25]["b_exit_seed_base"] == b_arith_lo25, \
            "W25 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W25-SHARD-0",
                                          "n1w25-0of12"), "W25 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W25-SHARD-11",
                                           "n1w25-11of12")
        assert SHARD_DIR.endswith("n1_w25") and OUT.endswith(
            "n1_w25_results.json"), "W25 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W25 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W25_PREREG.md")), \
            "W25 per-wave prereg missing (materializer requirement)"
        # W25 finalize cumulative deps: W17/W18/W19/W20/W21/W22 outputs
        # PRESENT (W22 finalize = bm-b r519 addendum, K=46,320, ledger
        # 412,948 chain head). W23 output NOT landed at this freeze
        # window (bm-c r332 frozen, engine burn in flight) and W24 output
        # NOT landed (bm-a r535 frozen, burn pending) -- no static
        # exists-assert pinned for 23/24; the finalize merge loop stays
        # FAIL-CLOSED on any missing prior output at run time (r307
        # two-state law family).
        for _depw in (17, 18, 19, 20, 21, 22):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W25 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 25 (no 15; 23/24 registered
        # by the r332 bm-c / r535 bm-a freezes).
        assert sorted(w for w in WAVE_CONFIGS if w < 25) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24], \
            "W25 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W26 materializer face (r335 bm-c freeze) ------------------------
    _set_wave(26)
    try:
        assert WAVE_CONFIGS[26]["a_seed_base"] == pf.N1_BANDS[26]["a"][0], \
            "W26 A band drift vs law mirror"
        assert WAVE_CONFIGS[26]["b_exit_seed_base"] == \
            pf.N1_BANDS[26]["b_exit"][0], "W26 B band drift vs law mirror"
        assert WAVE_CONFIGS[26].get("engine_owner") == \
            pf.N1_BANDS[26].get("engine_owner") == "bm-c", \
            "W26 engine_owner drift (law mirror parity)"
        w26_a = {A_SEED_BASE + j for j in range(A_N)}
        w26_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w26_a & w26_b), "W26 A/B band overlap"
        assert not (w26_a & reg_ints) and not (w26_b & reg_ints), \
            "W26 hits SEED_REGISTRY"
        for nm, band in (("A", w26_a), ("B", w26_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W26 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W26 {nm} hits W1"
            assert not (band & probes), f"W26 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25):
            assert not (w26_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W26 A hits W{wprev}"
            assert not (w26_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W26 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W26 bands must clear it.
        n3r1_used26 = set(range(70_000, 70_006))
        assert not (w26_a & n3r1_used26) and not (w26_b & n3r1_used26), \
            "W26 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w26_a & lfc_actual12) and not (w26_b & lfc_actual12), \
            "W26 bands must clear the lfc actual draw range"
        assert not (w26_a & options_actual12) and \
            not (w26_b & options_actual12), \
            "W26 bands must clear the options_wave2 actual draw range"
        # arithmetic facts (law sec.4 W26 row, r335): BOTH tails are FORCED
        # SKIP. A: the +2_000 arithmetic window 94_001..96_000 hits ALL
        # FOUR runner design-probe seeds (95_000..95_003 -- this leg is
        # the DISCOVERY FACE: the r520/r535 gate receipts' reserved
        # universe omitted the probe cluster; past waves W24/W25 clear
        # it) -> jump to the first clean 2,000-window 95_004..97_003
        # (W12 A-skip precedent). B: the +200 arithmetic window
        # 39_900..40_099 hits the N2/N4 design-probe reserved points
        # 40_000/40_001 AND SEED_REGISTRY values (new_signal_p1 40_000 /
        # new_signal_p1_ce 40_050) -> jump to the first continuous clean
        # 200-window: 40_051..40_250 (ADMIT receipt
        # results/_r335bmc_w26_band_gate.py leg1/leg2).
        arith_lo26 = pf.N1_BANDS[25]["a"][1] + 1     # W25 registered A end + 1
        a_arith_hits26 = sorted(v for v in probes
                                if arith_lo26 <= v <= arith_lo26 + A_N - 1)
        assert a_arith_hits26 == [95_000, 95_001, 95_002, 95_003], \
            "W26 A arithmetic tail must hit the probe-seed cluster " \
            "(forced-skip refusal facts, r335 discovery)"
        assert WAVE_CONFIGS[26]["a_seed_base"] > a_arith_hits26[-1], \
            "W26 A jump target must clear the refusal points (95_003)"
        assert WAVE_CONFIGS[26]["a_seed_base"] == 95_004, \
            "W26 A jump target drift (first clean window, ADMIT leg2-A)"
        b_arith_lo26 = pf.N1_BANDS[25]["b_exit"][1] + 1  # W25 reg B end + 1
        b_arith_hits26 = sorted(v for v in reg_ints | {40_001}
                                if b_arith_lo26 <= v <= b_arith_lo26 + B_N - 1)
        assert b_arith_hits26, \
            "W26 B arithmetic tail must be DIRTY (forced-skip refusal facts)"
        assert b_arith_hits26 == [40_000, 40_001, 40_050], \
            "W26 B refusal-facts drift vs the W25 row WARNING projection"
        assert WAVE_CONFIGS[26]["b_exit_seed_base"] > b_arith_hits26[-1], \
            "W26 B jump target must clear the refusal points (40_050)"
        assert WAVE_CONFIGS[26]["b_exit_seed_base"] == 40_051, \
            "W26 B jump target drift (first clean window, ADMIT leg2-B)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W26-SHARD-0",
                                          "n1w26-0of12"), "W26 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W26-SHARD-11",
                                           "n1w26-11of12")
        assert SHARD_DIR.endswith("n1_w26") and OUT.endswith(
            "n1_w26_results.json"), "W26 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W26 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W26_PREREG.md")), \
            "W26 per-wave prereg missing (materializer requirement)"
        # W26 finalize cumulative deps: W17/W18/W19/W20/W21/W22/W23 outputs
        # PRESENT (W23 finalize = bm-c r335, K=48,520, ledger 415,148 chain
        # head). W24 output NOT landed at this freeze window (bm-a 12/12
        # burned, finalize chain-unblocked by W23 but pending on bm-a)
        # and W25 output NOT landed (bm-b 12/12 burned, finalize queued
        # behind W24) -- no static exists-assert pinned for 24/25; the
        # finalize merge loop stays FAIL-CLOSED on any missing prior
        # output at run time (r307 two-state law family).
        for _depw in (17, 18, 19, 20, 21, 22, 23):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W26 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 26 (no 15; 24/25 registered
        # by the r535 bm-a / r520 bm-b freezes).
        assert sorted(w for w in WAVE_CONFIGS if w < 26) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25], \
            "W26 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W27 materializer face (r539 bm-a freeze) ------------------------
    _set_wave(27)
    try:
        assert WAVE_CONFIGS[27]["a_seed_base"] == pf.N1_BANDS[27]["a"][0], \
            "W27 A band drift vs law mirror"
        assert WAVE_CONFIGS[27]["b_exit_seed_base"] == \
            pf.N1_BANDS[27]["b_exit"][0], "W27 B band drift vs law mirror"
        assert WAVE_CONFIGS[27].get("engine_owner") == \
            pf.N1_BANDS[27].get("engine_owner") == "bm-a", \
            "W27 engine_owner drift (law mirror parity)"
        w27_a = {A_SEED_BASE + j for j in range(A_N)}
        w27_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w27_a & w27_b), "W27 A/B band overlap"
        assert not (w27_a & reg_ints) and not (w27_b & reg_ints), \
            "W27 hits SEED_REGISTRY"
        for nm, band in (("A", w27_a), ("B", w27_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W27 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W27 {nm} hits W1"
            assert not (band & probes), f"W27 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26):
            assert not (w27_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W27 A hits W{wprev}"
            assert not (w27_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W27 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W27 bands must clear it.
        n3r1_used27 = set(range(70_000, 70_006))
        assert not (w27_a & n3r1_used27) and not (w27_b & n3r1_used27), \
            "W27 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w27_a & lfc_actual12) and not (w27_b & lfc_actual12), \
            "W27 bands must clear the lfc actual draw range"
        assert not (w27_a & options_actual12) and \
            not (w27_b & options_actual12), \
            "W27 bands must clear the options_wave2 actual draw range"
        # arithmetic facts (law sec.4 W27 row, r539): BOTH tails continue
        # from the W26 REGISTERED tail (registry-derived, not prose) and
        # land CLEAN -- strides kept verbatim, NO skip (ADMIT receipt
        # results/_r539bma_w27_band_gate.py leg1/leg2; W26 row W27+
        # WARNING projection verified).
        arith_lo27 = pf.N1_BANDS[26]["a"][1] + 1     # W26 registered A end + 1
        a_arith_hits27 = sorted(v for v in reg_ints | probes
                                if arith_lo27 <= v <= arith_lo27 + A_N - 1)
        assert a_arith_hits27 == [], \
            "W27 A arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[27]["a_seed_base"] == arith_lo27, \
            "W27 A stride drift (arithmetic continuation, NO skip)"
        b_arith_lo27 = pf.N1_BANDS[26]["b_exit"][1] + 1  # W26 reg B end + 1
        b_arith_hits27 = sorted(v for v in reg_ints | {40_001}
                                if b_arith_lo27 <= v <= b_arith_lo27 + B_N - 1)
        assert b_arith_hits27 == [], \
            "W27 B arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[27]["b_exit_seed_base"] == b_arith_lo27, \
            "W27 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W27-SHARD-0",
                                          "n1w27-0of12"), "W27 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W27-SHARD-11",
                                           "n1w27-11of12")
        assert SHARD_DIR.endswith("n1_w27") and OUT.endswith(
            "n1_w27_results.json"), "W27 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W27 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W27_PREREG.md")), \
            "W27 per-wave prereg missing (materializer requirement)"
        # W27 finalize cumulative deps: W17/W18/W19/W20/W21/W22/W23/W24/
        # W25 outputs PRESENT (W25 finalize = bm-b r522, K=52,920,
        # ledger 419,548 chain head; W24 = bm-a r538 before it). W26
        # output NOT landed at this freeze window (bm-c burn in
        # progress, finalize pending on the bm-c seat) -- no static
        # exists-assert pinned for 26; the finalize merge loop stays
        # FAIL-CLOSED on any missing prior output at run time (r307
        # two-state law family).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W27 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 27 (no 15; 25/26 registered
        # by the r520 bm-b / r335 bm-c freezes).
        assert sorted(w for w in WAVE_CONFIGS if w < 27) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26], \
            "W27 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W28 materializer face (r523 bm-b freeze) ------------------------
    _set_wave(28)
    try:
        assert WAVE_CONFIGS[28]["a_seed_base"] == pf.N1_BANDS[28]["a"][0], \
            "W28 A band drift vs law mirror"
        assert WAVE_CONFIGS[28]["b_exit_seed_base"] == \
            pf.N1_BANDS[28]["b_exit"][0], "W28 B band drift vs law mirror"
        assert WAVE_CONFIGS[28].get("engine_owner") == \
            pf.N1_BANDS[28].get("engine_owner") == "bm-b", \
            "W28 engine_owner drift (law mirror parity)"
        w28_a = {A_SEED_BASE + j for j in range(A_N)}
        w28_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w28_a & w28_b), "W28 A/B band overlap"
        assert not (w28_a & reg_ints) and not (w28_b & reg_ints), \
            "W28 hits SEED_REGISTRY"
        for nm, band in (("A", w28_a), ("B", w28_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W28 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W28 {nm} hits W1"
            assert not (band & probes), f"W28 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27):
            assert not (w28_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W28 A hits W{wprev}"
            assert not (w28_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W28 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W28 bands must clear it.
        n3r1_used28 = set(range(70_000, 70_006))
        assert not (w28_a & n3r1_used28) and not (w28_b & n3r1_used28), \
            "W28 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w28_a & lfc_actual12) and not (w28_b & lfc_actual12), \
            "W28 bands must clear the lfc actual draw range"
        assert not (w28_a & options_actual12) and \
            not (w28_b & options_actual12), \
            "W28 bands must clear the options_wave2 actual draw range"
        # arithmetic facts (law sec.4 W28 row, r523): BOTH tails continue
        # from the W27 REGISTERED tail (registry-derived, not prose) and
        # land CLEAN -- strides kept verbatim, NO skip (ADMIT receipt
        # results/_r523bmb_w28_band_gate.py leg1/leg2; W27 row W28+
        # WARNING projection verified).
        arith_lo28 = pf.N1_BANDS[27]["a"][1] + 1     # W27 registered A end + 1
        a_arith_hits28 = sorted(v for v in reg_ints | probes
                                if arith_lo28 <= v <= arith_lo28 + A_N - 1)
        assert a_arith_hits28 == [], \
            "W28 A arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[28]["a_seed_base"] == arith_lo28, \
            "W28 A stride drift (arithmetic continuation, NO skip)"
        b_arith_lo28 = pf.N1_BANDS[27]["b_exit"][1] + 1  # W27 reg B end + 1
        b_arith_hits28 = sorted(v for v in reg_ints | {40_001}
                                if b_arith_lo28 <= v <= b_arith_lo28 + B_N - 1)
        assert b_arith_hits28 == [], \
            "W28 B arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[28]["b_exit_seed_base"] == b_arith_lo28, \
            "W28 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W28-SHARD-0",
                                          "n1w28-0of12"), "W28 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W28-SHARD-11",
                                           "n1w28-11of12")
        assert SHARD_DIR.endswith("n1_w28") and OUT.endswith(
            "n1_w28_results.json"), "W28 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W28 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W28_PREREG.md")), \
            "W28 per-wave prereg missing (materializer requirement)"
        # W28 finalize cumulative deps: W17/W18/W19/W20/W21/W22/W23/W24/
        # W25 outputs PRESENT (W25 finalize = bm-b r522, K=52,920,
        # ledger 419,548 chain head). W26 output NOT landed at this
        # freeze window (12/12 burned on bm-c r335, finalize pending on
        # the bm-c seat); W27 output NOT landed (bm-a r539 burn in
        # progress) -- no static exists-assert pinned for 26/27; the
        # finalize merge loop stays FAIL-CLOSED on any missing prior
        # output at run time (r307 two-state law family).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W28 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 28 (no 15; 26/27 registered
        # by the r335 bm-c / r539 bm-a freezes).
        assert sorted(w for w in WAVE_CONFIGS if w < 28) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27], \
            "W28 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W29 materializer face (r336 bm-c freeze) ------------------------
    _set_wave(29)
    try:
        assert WAVE_CONFIGS[29]["a_seed_base"] == pf.N1_BANDS[29]["a"][0], \
            "W29 A band drift vs law mirror"
        assert WAVE_CONFIGS[29]["b_exit_seed_base"] == \
            pf.N1_BANDS[29]["b_exit"][0], "W29 B band drift vs law mirror"
        assert WAVE_CONFIGS[29].get("engine_owner") == \
            pf.N1_BANDS[29].get("engine_owner") == "bm-c", \
            "W29 engine_owner drift (law mirror parity)"
        w29_a = {A_SEED_BASE + j for j in range(A_N)}
        w29_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w29_a & w29_b), "W29 A/B band overlap"
        assert not (w29_a & reg_ints) and not (w29_b & reg_ints), \
            "W29 hits SEED_REGISTRY"
        for nm, band in (("A", w29_a), ("B", w29_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W29 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W29 {nm} hits W1"
            assert not (band & probes), f"W29 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28):
            assert not (w29_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W29 A hits W{wprev}"
            assert not (w29_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W29 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W29 bands must clear it.
        n3r1_used29 = set(range(70_000, 70_006))
        assert not (w29_a & n3r1_used29) and not (w29_b & n3r1_used29), \
            "W29 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w29_a & lfc_actual12) and not (w29_b & lfc_actual12), \
            "W29 bands must clear the lfc actual draw range"
        assert not (w29_a & options_actual12) and \
            not (w29_b & options_actual12), \
            "W29 bands must clear the options_wave2 actual draw range"
        # arithmetic facts (law sec.4 W29 row, r336): BOTH tails continue
        # from the W28 REGISTERED tail (registry-derived, not prose) and
        # land CLEAN -- strides kept verbatim, NO skip (ADMIT receipt
        # results/_r336bmc_w29_band_gate.py leg1/leg2; W28 row W29+
        # WARNING projection verified).
        arith_lo29 = pf.N1_BANDS[28]["a"][1] + 1     # W28 registered A end + 1
        a_arith_hits29 = sorted(v for v in reg_ints | probes
                               if arith_lo29 <= v <= arith_lo29 + A_N - 1)
        assert a_arith_hits29 == [], \
            "W29 A arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[29]["a_seed_base"] == arith_lo29, \
            "W29 A stride drift (arithmetic continuation, NO skip)"
        b_arith_lo29 = pf.N1_BANDS[28]["b_exit"][1] + 1  # W28 reg B end + 1
        b_arith_hits29 = sorted(v for v in reg_ints | {40_001}
                                if b_arith_lo29 <= v <= b_arith_lo29 + B_N - 1)
        assert b_arith_hits29 == [], \
            "W29 B arithmetic tail must be clean (ADMIT receipt leg1)"
        assert WAVE_CONFIGS[29]["b_exit_seed_base"] == b_arith_lo29, \
            "W29 B stride drift (arithmetic continuation, no skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W29-SHARD-0",
                                          "n1w29-0of12"), "W29 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W29-SHARD-11",
                                          "n1w29-11of12")
        assert SHARD_DIR.endswith("n1_w29") and OUT.endswith(
            "n1_w29_results.json"), "W29 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W29 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W29_PREREG.md")), \
            "W29 per-wave prereg missing (materializer requirement)"
        # W29 finalize cumulative deps: W17/W18/W19/W20/W21/W22/W23/W24/
        # W25/W26 outputs PRESENT (W26 finalize = bm-c r336, K=55,120,
        # ledger 421,748 chain head; W25 = bm-b r522 before it). W27
        # output NOT landed at this freeze window (12/12 burned on
        # bm-a r539, finalize pending on the bm-a seat -- chain-unblocked
        # by W26); W28 output NOT landed (bm-b r523 burn in progress)
        # -- no static exists-assert pinned for 27/28; the finalize
        # merge loop stays FAIL-CLOSED on any missing prior output at
        # run time (r307 two-state law family).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W29 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 29 (no 15; 27/28 registered
        # by the r539 bm-a / r523 bm-b freezes).
        assert sorted(w for w in WAVE_CONFIGS if w < 29) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28], \
            "W29 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W30 materializer face (r541 bm-a freeze) --------------------------
    _set_wave(30)
    try:
        assert WAVE_CONFIGS[30]["a_seed_base"] == pf.N1_BANDS[30]["a"][0], \
            "W30 A band drift vs law mirror"
        assert WAVE_CONFIGS[30]["b_exit_seed_base"] == \
            pf.N1_BANDS[30]["b_exit"][0], "W30 B band drift vs law mirror"
        assert WAVE_CONFIGS[30].get("engine_owner") == \
            pf.N1_BANDS[30].get("engine_owner") == "bm-a", \
            "W30 engine_owner drift (law mirror parity)"
        w30_a = {A_SEED_BASE + j for j in range(A_N)}
        w30_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w30_a & w30_b), "W30 A/B band overlap"
        assert not (w30_a & reg_ints) and not (w30_b & reg_ints), \
            "W30 hits SEED_REGISTRY"
        for nm, band in (("A", w30_a), ("B", w30_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W30 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W30 {nm} hits W1"
            assert not (band & probes), f"W30 {nm} hits probe seeds"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28):
            assert not (w30_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W30 A hits W{wprev}"
            assert not (w30_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W30 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W30 bands must clear it.
        n3r1_used30 = set(range(70_000, 70_006))
        assert not (w30_a & n3r1_used30) and not (w30_b & n3r1_used30), \
            "W30 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w30_a & lfc_actual12) and not (w30_b & lfc_actual12), \
            "W30 bands must clear the lfc actual draw range"
        assert not (w30_a & options_actual12) and \
            not (w30_b & options_actual12), \
            "W30 bands must clear the options_wave2 actual draw range"
        # W29 PUBLISHED-PROJECTION RESERVATION leg (r518: published
        # projection = reserved face; W28 row W29+ WARNING names the
        # bm-c rotation slot). W29 is NOT registered at this freeze --
        # its projected window is written into the reserved universe as
        # refusal facts; W30 must clear it on both sides.
        w29_proj_a = set(range(101_004, 103_004))
        w29_proj_b = set(range(40_651, 40_851))
        assert not (w30_a & w29_proj_a), \
            "W30 A overlaps the W29 published projection 101_004..103_003 " \
            "(reserved face, r518)"
        assert not (w30_b & w29_proj_b), \
            "W30 B overlaps the W29 published projection 40_651..40_850 " \
            "(reserved face, r518)"
        # skip facts (law sec.4 W30 row, r541): A = first clean window
        # past the W29 projection (candidate start == W29 projected A
        # end + 1, no further skip); B = the arithmetic window from the
        # W29 projected B tail (40_851..41_050) hits SEED_REGISTRY
        # p4_batch1=41_000 -> candidate start == 41_000 + 1 (in-band
        # point skip, W26-B re-base lineage).
        assert WAVE_CONFIGS[30]["a_seed_base"] == 103_004 == 103_003 + 1, \
            "W30 A must start at the W29 projected A end + 1 (skip r518)"
        assert 41_000 in {v for v in reg_ints if 40_851 <= v <= 41_050}, \
            "W30 B skip forcedness: p4_batch1=41_000 must sit inside the " \
            "refused arithmetic window 40_851..41_050"
        assert WAVE_CONFIGS[30]["b_exit_seed_base"] == 41_001 == 41_000 + 1, \
            "W30 B must start at p4_batch1=41_000 + 1 (in-band skip)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W30-SHARD-0",
                                          "n1w30-0of12"), "W30 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W30-SHARD-11",
                                           "n1w30-11of12")
        assert SHARD_DIR.endswith("n1_w30") and OUT.endswith(
            "n1_w30_results.json"), "W30 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W30 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W30_PREREG.md")), \
            "W30 per-wave prereg missing (materializer requirement)"
        # W30 finalize cumulative deps: W17..W28 outputs PRESENT (W28
        # finalize = bm-b r524, K=59,520, ledger 426,148 chain head --
        # landed mid-draft on this freeze window, anchor-roll law
        # disclosed; local copy byte-identical to origin). W29 NOT
        # registered (bm-c seat pending) -- the finalize merge loop
        # stays FAIL-CLOSED on any missing prior output at run time
        # (r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W30 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 30 (no 15; no 29 -- the
        # bm-c seat stays unregistered at this freeze; W29 landing later
        # auto-joins the set by registry derivation).
        # (r337 bm-c same-window amendment: W29 registered -> auto-joined the
        #  set by registry derivation exactly as this freeze-window comment
        #  projected; expected list +29 per r531 minimal-disclosure law.)
        assert sorted(w for w in WAVE_CONFIGS if w < 30) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29], \
            "W30 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W31 materializer face (r525 bm-b freeze) ----------------------------
    _set_wave(31)
    try:
        assert WAVE_CONFIGS[31]["a_seed_base"] == pf.N1_BANDS[31]["a"][0], \
            "W31 A band drift vs law mirror"
        assert WAVE_CONFIGS[31]["b_exit_seed_base"] == \
            pf.N1_BANDS[31]["b_exit"][0], "W31 B band drift vs law mirror"
        assert WAVE_CONFIGS[31].get("engine_owner") == \
            pf.N1_BANDS[31].get("engine_owner") == "bm-b", \
            "W31 engine_owner drift (law mirror parity)"
        w31_a = {A_SEED_BASE + j for j in range(A_N)}
        w31_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w31_a & w31_b), "W31 A/B band overlap"
        assert not (w31_a & reg_ints) and not (w31_b & reg_ints), \
            "W31 hits SEED_REGISTRY"
        for nm, band in (("A", w31_a), ("B", w31_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W31 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W31 {nm} hits W1"
            assert not (band & probes), f"W31 {nm} hits probe seeds"
        # prior-wave disjointness incl. W29 (SEATED r337 -- its published
        # projection window was taken verbatim, r518 published=reserved
        # discharged; the registered band IS the reserved face now) and
        # W30 (bm-a r541, burn in flight -- registered in-use face).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30):
            assert not (w31_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W31 A hits W{wprev}"
            assert not (w31_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W31 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W31 bands must clear it.
        n3r1_used31 = set(range(70_000, 70_006))
        assert not (w31_a & n3r1_used31) and not (w31_b & n3r1_used31), \
            "W31 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w31_a & lfc_actual12) and not (w31_b & lfc_actual12), \
            "W31 bands must clear the lfc actual draw range"
        assert not (w31_a & options_actual12) and \
            not (w31_b & options_actual12), \
            "W31 bands must clear the options_wave2 actual draw range"
        # arithmetic-continuation facts (law sec.4 W31 row, r525): BOTH
        # tails land clean exactly as the W30 row's W31+ WARNING
        # projected -- no forced skip either side (candidate start ==
        # W30 band end + 1 on both sides; the W30-published projection
        # window IS the candidate, machine-verified by the r525 gate).
        assert WAVE_CONFIGS[31]["a_seed_base"] == 105_004 == 105_003 + 1, \
            "W31 A must start at the W30 A end + 1 (arithmetic continuation)"
        assert WAVE_CONFIGS[31]["b_exit_seed_base"] == 41_201 == 41_200 + 1, \
            "W31 B must start at the W30 B end + 1 (arithmetic continuation)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W31-SHARD-0",
                                          "n1w31-0of12"), "W31 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W31-SHARD-11",
                                           "n1w31-11of12")
        assert SHARD_DIR.endswith("n1_w31") and OUT.endswith(
            "n1_w31_results.json"), "W31 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W31 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W31_PREREG.md")), \
            "W31 per-wave prereg missing (materializer requirement)"
        # W31 finalize cumulative deps: W17..W29 outputs PRESENT (W29
        # finalize = bm-c r337, K=61,720, ledger 428,348 chain head --
        # landed mid-draft on this freeze window, anchor-roll law
        # disclosed; local copy byte-identical to origin). W30 (bm-a,
        # r541) IS REGISTERED with burn in flight -- its output is NOT
        # asserted present at freeze time (two-state law, r307): the
        # finalize merge loop derives the prior-wave set from registry
        # keys and stays FAIL-CLOSED on any missing prior output at
        # run time, so a W31 finalize ahead of the W30 finalize simply
        # waits (chain-linearity discipline, r519 same-head law; r337
        # CHAIN GATE handover: next finalize seats W30=bm-a then
        # W31=bm-b).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W31 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 31 (no 15; W29 seated r337;
        # W30 registered r541 in-flight -- auto-joins the set by registry
        # derivation).
        assert sorted(w for w in WAVE_CONFIGS if w < 31) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30], \
            "W31 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W32 materializer face (r339 bm-c freeze) --------------------------
    _set_wave(32)
    try:
        assert WAVE_CONFIGS[32]["a_seed_base"] == pf.N1_BANDS[32]["a"][0], \
            "W32 A band drift vs law mirror"
        assert WAVE_CONFIGS[32]["b_exit_seed_base"] == \
            pf.N1_BANDS[32]["b_exit"][0], "W32 B band drift vs law mirror"
        assert WAVE_CONFIGS[32].get("engine_owner") == \
            pf.N1_BANDS[32].get("engine_owner") == "bm-c", \
            "W32 engine_owner drift (law mirror parity)"
        w32_a = {A_SEED_BASE + j for j in range(A_N)}
        w32_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w32_a & w32_b), "W32 A/B band overlap"
        assert not (w32_a & reg_ints) and not (w32_b & reg_ints), \
            "W32 hits SEED_REGISTRY"
        for nm, band in (("A", w32_a), ("B", w32_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W32 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W32 {nm} hits W1"
            assert not (band & probes), f"W32 {nm} hits probe seeds"
        # prior-wave disjointness incl. W29 (seated, discharged r518),
        # W30 (r541 bm-a, finalized r542) and W31 (r525 bm-b,
        # finalized -- every pre-W32 seat closed at this freeze).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31):
            assert not (w32_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W32 A hits W{wprev}"
            assert not (w32_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W32 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W32 bands must clear it.
        n3r1_used32 = set(range(70_000, 70_006))
        assert not (w32_a & n3r1_used32) and not (w32_b & n3r1_used32), \
            "W32 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w32_a & lfc_actual12) and not (w32_b & lfc_actual12), \
            "W32 bands must clear the lfc actual draw range"
        assert not (w32_a & options_actual12) and \
            not (w32_b & options_actual12), \
            "W32 bands must clear the options_wave2 actual draw range"
        # arithmetic-continuation facts (law sec.4 W32 row, r339): BOTH
        # tails land clean exactly as the W31 row's W32+ WARNING
        # projected -- no forced skip either side (candidate start ==
        # W31 band end + 1 on both sides; the W31-published projection
        # window IS the candidate, machine-verified by the r339 gate).
        assert WAVE_CONFIGS[32]["a_seed_base"] == 107_004 == 107_003 + 1, \
            "W32 A must start at the W31 A end + 1 (arithmetic continuation)"
        assert WAVE_CONFIGS[32]["b_exit_seed_base"] == 41_401 == 41_400 + 1, \
            "W32 B must start at the W31 B end + 1 (arithmetic continuation)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W32-SHARD-0",
                                          "n1w32-0of12"), "W32 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W32-SHARD-11",
                                           "n1w32-11of12")
        assert SHARD_DIR.endswith("n1_w32") and OUT.endswith(
            "n1_w32_results.json"), "W32 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W32 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W32_PREREG.md")), \
            "W32 per-wave prereg missing (materializer requirement)"
        # W32 finalize cumulative deps: W17..W31 outputs ALL PRESENT
        # (every pre-W32 seat closed at this freeze -- W31 finalize
        # landed on origin, ledger 432,748 chain head; local copy
        # byte-identical to origin after the S0 pull).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W32 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 32 (no 15; W30/W31 both
        # seated and finalized).
        assert sorted(w for w in WAVE_CONFIGS if w < 32) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], \
            "W32 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W33 materializer face (r544 bm-a freeze) --------------------------
    _set_wave(33)
    try:
        assert WAVE_CONFIGS[33]["a_seed_base"] == pf.N1_BANDS[33]["a"][0], \
            "W33 A band drift vs law mirror"
        assert WAVE_CONFIGS[33]["b_exit_seed_base"] == \
            pf.N1_BANDS[33]["b_exit"][0], "W33 B band drift vs law mirror"
        assert WAVE_CONFIGS[33].get("engine_owner") == \
            pf.N1_BANDS[33].get("engine_owner") == "bm-a", \
            "W33 engine_owner drift (law mirror parity)"
        w33_a = {A_SEED_BASE + j for j in range(A_N)}
        w33_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w33_a & w33_b), "W33 A/B band overlap"
        assert not (w33_a & reg_ints) and not (w33_b & reg_ints), \
            "W33 hits SEED_REGISTRY"
        for nm, band in (("A", w33_a), ("B", w33_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W33 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W33 {nm} hits W1"
            assert not (band & probes), f"W33 {nm} hits probe seeds"
        # prior-wave disjointness incl. W30 (bm-a own lineage, finalized
        # r542), W31 (bm-b, finalized) and W32 (bm-c, registered + burned
        # 12/12 on origin, finalize pending at the bm-c seat at this
        # freeze -- band registration IS the reservation face).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32):
            assert not (w33_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W33 A hits W{wprev}"
            assert not (w33_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W33 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W33 bands must clear it.
        n3r1_used33 = set(range(70_000, 70_006))
        assert not (w33_a & n3r1_used33) and not (w33_b & n3r1_used33), \
            "W33 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w33_a & lfc_actual12) and not (w33_b & lfc_actual12), \
            "W33 bands must clear the lfc actual draw range"
        assert not (w33_a & options_actual12) and \
            not (w33_b & options_actual12), \
            "W33 bands must clear the options_wave2 actual draw range"
        # arithmetic-continuation facts (law sec.4 W33 row, r544): BOTH
        # tails land clean exactly as the W32 row's W33+ WARNING
        # projected -- no forced skip either side (candidate start ==
        # W32 band end + 1 on both sides; the W32-published projection
        # window IS the candidate, machine-verified by the r544 gate).
        assert WAVE_CONFIGS[33]["a_seed_base"] == 109_004 == 109_003 + 1, \
            "W33 A must start at the W32 A end + 1 (arithmetic continuation)"
        assert WAVE_CONFIGS[33]["b_exit_seed_base"] == 41_601 == 41_600 + 1, \
            "W33 B must start at the W32 B end + 1 (arithmetic continuation)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W33-SHARD-0",
                                          "n1w33-0of12"), "W33 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W33-SHARD-11",
                                           "n1w33-11of12")
        assert SHARD_DIR.endswith("n1_w33") and OUT.endswith(
            "n1_w33_results.json"), "W33 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W33 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W33_PREREG.md")), \
            "W33 per-wave prereg missing (materializer requirement)"
        # W33 finalize cumulative deps: W17..W32 outputs ALL PRESENT
        # (W32 finalize landed bm-c same-window AFTER this freeze's
        # commit -- K=68,320 chain-linear, ledger head 434,948; the
        # dep pin auto-join +32 executed this window per the r531-1
        # minimal-amendment precedent, exactly as bm-c r337 amended
        # the W30 leg +29 when W29 landed).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W33 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 33 (no 15; W30/W31/W32 all
        # seated -- W32 registration is the reservation face).
        assert sorted(w for w in WAVE_CONFIGS if w < 33) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32], \
            "W33 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W34 materializer face (r527 bm-b freeze) --------------------------
    _set_wave(34)
    try:
        assert WAVE_CONFIGS[34]["a_seed_base"] == pf.N1_BANDS[34]["a"][0], \
            "W34 A band drift vs law mirror"
        assert WAVE_CONFIGS[34]["b_exit_seed_base"] == \
            pf.N1_BANDS[34]["b_exit"][0], "W34 B band drift vs law mirror"
        assert WAVE_CONFIGS[34].get("engine_owner") == \
            pf.N1_BANDS[34].get("engine_owner") == "bm-b", \
            "W34 engine_owner drift (law mirror parity)"
        w34_a = {A_SEED_BASE + j for j in range(A_N)}
        w34_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w34_a & w34_b), "W34 A/B band overlap"
        assert not (w34_a & reg_ints) and not (w34_b & reg_ints), \
            "W34 hits SEED_REGISTRY"
        for nm, band in (("A", w34_a), ("B", w34_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W34 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W34 {nm} hits W1"
            assert not (band & probes), f"W34 {nm} hits probe seeds"
        # prior-wave disjointness incl. W30 (bm-a own lineage, finalized
        # r542), W31 (bm-b, finalized r525), W32 (bm-c, finalized r340
        # window) and W33 (bm-a, registered + burned 12/12 + FINALIZED
        # bm-a r544 same-window as this freeze -- the chain fully caught
        # up: W1..W33 all finalized at this freeze, zero pending upstream
        # face for the first time).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33):
            assert not (w34_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W34 A hits W{wprev}"
            assert not (w34_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W34 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W34 bands must clear it.
        n3r1_used34 = set(range(70_000, 70_006))
        assert not (w34_a & n3r1_used34) and not (w34_b & n3r1_used34), \
            "W34 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w34_a & lfc_actual12) and not (w34_b & lfc_actual12), \
            "W34 bands must clear the lfc actual draw range"
        assert not (w34_a & options_actual12) and \
            not (w34_b & options_actual12), \
            "W34 bands must clear the options_wave2 actual draw range"
        # arithmetic-continuation facts (law sec.4 W34 row, r527): BOTH
        # tails land clean exactly as the W33 row's W34+ WARNING
        # projected -- no forced skip either side (candidate start ==
        # W33 band end + 1 on both sides; the W33-published projection
        # window IS the candidate, machine-verified by the r527 gate).
        assert WAVE_CONFIGS[34]["a_seed_base"] == 111_004 == 111_003 + 1, \
            "W34 A must start at the W33 A end + 1 (arithmetic continuation)"
        assert WAVE_CONFIGS[34]["b_exit_seed_base"] == 41_801 == 41_800 + 1, \
            "W34 B must start at the W33 B end + 1 (arithmetic continuation)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W34-SHARD-0",
                                          "n1w34-0of12"), "W34 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W34-SHARD-11",
                                           "n1w34-11of12")
        assert SHARD_DIR.endswith("n1_w34") and OUT.endswith(
            "n1_w34_results.json"), "W34 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W34 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W34_PREREG.md")), \
            "W34 per-wave prereg missing (materializer requirement)"
        # W34 finalize cumulative deps: W17..W33 outputs ALL PRESENT
        # (W33 finalize landed bm-a r544 same-window as this freeze --
        # K=70,520 chain-linear, ledger head 437,148; W1..W33 ALL
        # finalized at this freeze: the dep pin needs NO auto-join
        # amendment for the first time, the chain is fully caught up).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W34 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 34 (no 15; W30/W31/W32/W33
        # all seated and finalized).
        assert sorted(w for w in WAVE_CONFIGS if w < 34) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33], \
            "W34 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W35 materializer face (r545 bm-a freeze, de-throttle law
    #     O-20261001-2355 sec.2 own-continuous-series) -----------------
    _set_wave(35)
    try:
        assert WAVE_CONFIGS[35]["a_seed_base"] == pf.N1_BANDS[35]["a"][0], \
            "W35 A band drift vs law mirror"
        assert WAVE_CONFIGS[35]["b_exit_seed_base"] == \
            pf.N1_BANDS[35]["b_exit"][0], "W35 B band drift vs law mirror"
        assert WAVE_CONFIGS[35].get("engine_owner") == \
            pf.N1_BANDS[35].get("engine_owner") == "bm-a", \
            "W35 engine_owner drift (law mirror parity)"
        w35_a = {A_SEED_BASE + j for j in range(A_N)}
        w35_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w35_a & w35_b), "W35 A/B band overlap"
        assert not (w35_a & reg_ints) and not (w35_b & reg_ints), \
            "W35 hits SEED_REGISTRY"
        for nm, band in (("A", w35_a), ("B", w35_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W35 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W35 {nm} hits W1"
            assert not (band & probes), f"W35 {nm} hits probe seeds"
        # prior-wave disjointness incl. W30/W31/W32/W33/W34 (all
        # registered; W34 registered by the bm-b r528 freeze adopted
        # in this same merge -- the +34 auto-join of the r531-1/r541
        # minimal-amendment precedent; the band-gate PUBLISHED leg
        # and the arithmetic-continuation facts below cover it).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34):
            assert not (w35_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W35 A hits W{wprev}"
            assert not (w35_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W35 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W35 bands must clear it.
        n3r1_used35 = set(range(70_000, 70_006))
        assert not (w35_a & n3r1_used35) and not (w35_b & n3r1_used35), \
            "W35 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w35_a & lfc_actual12) and not (w35_b & lfc_actual12), \
            "W35 bands must clear the lfc actual draw range"
        assert not (w35_a & options_actual12) and \
            not (w35_b & options_actual12), \
            "W35 bands must clear the options_wave2 actual draw range"
        # forced-skip facts (law sec.4 W35 row, r545): the arithmetic
        # continuation from W33 IS the published W34 projection
        # (A 111_004..113_003 / B 41_801..42_000, bm-b pre-scan
        # ADMIT-READY r527) -> reserved face per r518; W35 starts at
        # the published projection end + 1 on both sides (machine-
        # proven forced skip, gate refusal facts).
        assert WAVE_CONFIGS[35]["a_seed_base"] == 113_004 == 113_003 + 1, \
            "W35 A must start at the W34 published projection end + 1"
        assert WAVE_CONFIGS[35]["b_exit_seed_base"] == 42_001 == 42_000 + 1, \
            "W35 B must start at the W34 published projection end + 1"
        w34_proj_a = set(range(111_004, 113_004))
        w34_proj_b = set(range(41_801, 42_001))
        assert not (w35_a & w34_proj_a) and not (w35_b & w34_proj_b), \
            "W35 bands hit the published W34 projection (r518 reserved face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W35-SHARD-0",
                                          "n1w35-0of12"), "W35 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W35-SHARD-11",
                                           "n1w35-11of12")
        assert SHARD_DIR.endswith("n1_w35") and OUT.endswith(
            "n1_w35_results.json"), "W35 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W35 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W35_PREREG.md")), \
            "W35 per-wave prereg missing (materializer requirement)"
        # W35 finalize cumulative deps: W17..W33 outputs ALL PRESENT;
        # W34 registered at the bm-b r528 freeze adopted in this merge
        # -- the dep pin auto-joined +34 per the r531-1/r541 minimal-
        # amendment precedent (finalize runtime composes every registry
        # key below 35 = FAIL-CLOSED honest wait for the W34 output).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W35 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 35 (no 15, no 34 until
        # bm-b registers W34 -- then the runtime FAIL-CLOSED compose
        # consumes it automatically).
        assert sorted(w for w in WAVE_CONFIGS if w < 35) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34], \
            "W35 prior-wave set must derive from registry keys (no 15, incl. 34)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W36 materializer face (r528 bm-b freeze, de-throttle law
    #     O-20261001-2355 sec.2 own-continuous-series) -----------------
    _set_wave(36)
    try:
        assert WAVE_CONFIGS[36]["a_seed_base"] == pf.N1_BANDS[36]["a"][0], \
            "W36 A band drift vs law mirror"
        assert WAVE_CONFIGS[36]["b_exit_seed_base"] == \
            pf.N1_BANDS[36]["b_exit"][0], "W36 B band drift vs law mirror"
        assert WAVE_CONFIGS[36].get("engine_owner") == \
            pf.N1_BANDS[36].get("engine_owner") == "bm-b", \
            "W36 engine_owner drift (law mirror parity)"
        w36_a = {A_SEED_BASE + j for j in range(A_N)}
        w36_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w36_a & w36_b), "W36 A/B band overlap"
        assert not (w36_a & reg_ints) and not (w36_b & reg_ints), \
            "W36 hits SEED_REGISTRY"
        for nm, band in (("A", w36_a), ("B", w36_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W36 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W36 {nm} hits W1"
            assert not (band & probes), f"W36 {nm} hits probe seeds"
        # prior-wave disjointness incl. W30..W34 (all registered) and
        # W35 (bm-a, registered + burning at this freeze -- in-flight
        # coexists by band disjointness per r531 law).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35):
            assert not (w36_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W36 A hits W{wprev}"
            assert not (w36_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W36 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W36 bands must clear it.
        n3r1_used36 = set(range(70_000, 70_006))
        assert not (w36_a & n3r1_used36) and not (w36_b & n3r1_used36), \
            "W36 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w36_a & lfc_actual12) and not (w36_b & lfc_actual12), \
            "W36 bands must clear the lfc actual draw range"
        assert not (w36_a & options_actual12) and \
            not (w36_b & options_actual12), \
            "W36 bands must clear the options_wave2 actual draw range"
        # arithmetic-continuation facts (law sec.4 W36 row, r528): BOTH
        # tails land clean exactly as the W35 row's W36+ WARNING
        # projected -- no skip either side (candidate start == W35 band
        # end + 1 on both sides; the W35-published projection window IS
        # the candidate, machine-verified by the r528 gate).
        assert WAVE_CONFIGS[36]["a_seed_base"] == 115_004 == 115_003 + 1, \
            "W36 A must start at the W35 A end + 1 (arithmetic continuation)"
        assert WAVE_CONFIGS[36]["b_exit_seed_base"] == 42_201 == 42_200 + 1, \
            "W36 B must start at the W35 B end + 1 (arithmetic continuation)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W36-SHARD-0",
                                          "n1w36-0of12"), "W36 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W36-SHARD-11",
                                           "n1w36-11of12")
        assert SHARD_DIR.endswith("n1_w36") and OUT.endswith(
            "n1_w36_results.json"), "W36 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W36 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W36_PREREG.md")), \
            "W36 per-wave prereg missing (materializer requirement)"
        # W36 finalize cumulative deps: W17..W34 outputs ALL PRESENT
        # (W34 finalize landed bm-b r528 same-window as this freeze --
        # net ledger head 437,340); W35 registered + BURNING at this
        # freeze (bm-a) -- the dep pin carries the W35-pending
        # two-state honest note per the r541 W30 precedent (finalize
        # runtime composes every registry key below 36 = FAIL-CLOSED
        # honest wait for the W35 output once it lands).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W36 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 36 (no 15; W30..W35 all
        # seated, W35 in-flight = runtime FAIL-CLOSED guard).
        assert sorted(w for w in WAVE_CONFIGS if w < 36) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35], \
            "W36 prior-wave set must derive from registry keys (no 15)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W37 materializer face (r341 bm-c freeze, own-series law
    #     O-20261001-2355 sec.2; follows the r341 W36 yield to bm-b per
    #     r511 commit-order law -- the crashed-session W36 draft never
    #     landed, zero burn zero ledger zero loss) --------------------
    _set_wave(37)
    try:
        assert WAVE_CONFIGS[37]["a_seed_base"] == pf.N1_BANDS[37]["a"][0], \
            "W37 A band drift vs law mirror"
        assert WAVE_CONFIGS[37]["b_exit_seed_base"] == \
            pf.N1_BANDS[37]["b_exit"][0], "W37 B band drift vs law mirror"
        assert WAVE_CONFIGS[37].get("engine_owner") == \
            pf.N1_BANDS[37].get("engine_owner") == "bm-c", \
            "W37 engine_owner drift (law mirror parity)"
        w37_a = {A_SEED_BASE + j for j in range(A_N)}
        w37_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w37_a & w37_b), "W37 A/B band overlap"
        assert not (w37_a & reg_ints) and not (w37_b & reg_ints), \
            "W37 hits SEED_REGISTRY"
        for nm, band in (("A", w37_a), ("B", w37_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W37 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W37 {nm} hits W1"
            assert not (band & probes), f"W37 {nm} hits probe seeds"
        # prior-wave disjointness incl. W35 (bm-a, burned 12/12 on
        # origin, finalize pending) and W36 (bm-b, registered + burning
        # at this freeze -- in-flight coexists by band disjointness
        # per r531 law).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36):
            assert not (w37_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W37 A hits W{wprev}"
            assert not (w37_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W37 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W37 bands must clear it.
        n3r1_used37 = set(range(70_000, 70_006))
        assert not (w37_a & n3r1_used37) and not (w37_b & n3r1_used37), \
            "W37 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w37_a & lfc_actual12) and not (w37_b & lfc_actual12), \
            "W37 bands must clear the lfc actual draw range"
        assert not (w37_a & options_actual12) and \
            not (w37_b & options_actual12), \
            "W37 bands must clear the options_wave2 actual draw range"
        # arithmetic-continuation facts (law sec.4 W37 row, r341): BOTH
        # tails land clean exactly as the W36 row's W37+ WARNING
        # projected -- no skip either side (candidate start == W36 band
        # end + 1 on both sides; the r528-published projection window IS
        # the candidate, machine-verified by the r341 gate).
        assert WAVE_CONFIGS[37]["a_seed_base"] == 117_004 == 117_003 + 1, \
            "W37 A must start at the W36 A end + 1 (arithmetic continuation)"
        assert WAVE_CONFIGS[37]["b_exit_seed_base"] == 42_401 == 42_400 + 1, \
            "W37 B must start at the W36 B end + 1 (arithmetic continuation)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W37-SHARD-0",
                                          "n1w37-0of12"), "W37 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W37-SHARD-11",
                                           "n1w37-11of12")
        assert SHARD_DIR.endswith("n1_w37") and OUT.endswith(
            "n1_w37_results.json"), "W37 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W37 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W37_PREREG.md")), \
            "W37 per-wave prereg missing (materializer requirement)"
        # W37 finalize cumulative deps: W17..W34 outputs ALL PRESENT
        # (W34 finalize landed bm-b r528 -- net ledger head 437,340);
        # W35 (bm-a, burned 12/12, finalize pending at this freeze) and
        # W36 (bm-b, registered + burning) -- the dep pin carries the
        # two-state honest note per the r541 W30 precedent (finalize
        # runtime composes every registry key below 37 = FAIL-CLOSED
        # honest wait for the W35/W36 outputs once they land).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W37 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 37 (no 15; W35/W36
        # in-flight = runtime FAIL-CLOSED guard).
        assert sorted(w for w in WAVE_CONFIGS if w < 37) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36], \
            "W37 prior-wave set must derive from registry keys (no 15, incl. 35+36)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W38 materializer face (r529 bm-b freeze, own-series law
    #     O-20261001-2355 sec.2 -- bm-b's TWELFTH owned wave after
    #     W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/W36; zero-gap relay
    #     after the W36 FULL CLOSEOUT this same window) ---------------
    _set_wave(38)
    try:
        assert WAVE_CONFIGS[38]["a_seed_base"] == pf.N1_BANDS[38]["a"][0], \
            "W38 A band drift vs law mirror"
        assert WAVE_CONFIGS[38]["b_exit_seed_base"] == \
            pf.N1_BANDS[38]["b_exit"][0], "W38 B band drift vs law mirror"
        assert WAVE_CONFIGS[38].get("engine_owner") == \
            pf.N1_BANDS[38].get("engine_owner") == "bm-b", \
            "W38 engine_owner drift (law mirror parity)"
        w38_a = {A_SEED_BASE + j for j in range(A_N)}
        w38_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w38_a & w38_b), "W38 A/B band overlap"
        assert not (w38_a & reg_ints) and not (w38_b & reg_ints), \
            "W38 hits SEED_REGISTRY"
        for nm, band in (("A", w38_a), ("B", w38_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W38 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W38 {nm} hits W1"
            assert not (band & probes), f"W38 {nm} hits probe seeds"
        # prior-wave disjointness incl. W36 (bm-b, closed FULL-LIFECYCLE
        # this same window -- r529 finalize one-pass K=77,120, ledger
        # 441,740 chain-linear) and W37 (bm-c, registered + burning at
        # this freeze -- in-flight coexists by band disjointness per
        # r531 law).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37):
            assert not (w38_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W38 A hits W{wprev}"
            assert not (w38_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W38 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W38 bands must clear it.
        n3r1_used38 = set(range(70_000, 70_006))
        assert not (w38_a & n3r1_used38) and not (w38_b & n3r1_used38), \
            "W38 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w38_a & lfc_actual12) and not (w38_b & lfc_actual12), \
            "W38 bands must clear the lfc actual draw range"
        assert not (w38_a & options_actual12) and \
            not (w38_b & options_actual12), \
            "W38 bands must clear the options_wave2 actual draw range"
        # arithmetic-continuation facts (law sec.4 W38 row, r529): BOTH
        # tails land clean exactly as the W37 row's W38+ WARNING
        # projected -- no skip either side (candidate start == W37 band
        # end + 1 on both sides; the r341-published projection window IS
        # the candidate, machine-verified by the r529 gate).
        assert WAVE_CONFIGS[38]["a_seed_base"] == 119_004 == 119_003 + 1, \
            "W38 A must start at the W37 A end + 1 (arithmetic continuation)"
        assert WAVE_CONFIGS[38]["b_exit_seed_base"] == 42_601 == 42_600 + 1, \
            "W38 B must start at the W37 B end + 1 (arithmetic continuation)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W38-SHARD-0",
                                          "n1w38-0of12"), "W38 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W38-SHARD-11",
                                           "n1w38-11of12")
        assert SHARD_DIR.endswith("n1_w38") and OUT.endswith(
            "n1_w38_results.json"), "W38 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W38 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W38_PREREG.md")), \
            "W38 per-wave prereg missing (materializer requirement)"
        # W38 finalize cumulative deps: W17..W36 outputs ALL PRESENT
        # (W34 finalize r528 bm-b K=72,720; W35 finalize bm-a r546
        # K=74,920; W36 finalize bm-b r529 this same window K=77,120 --
        # net ledger head 441,740); W37 (bm-c, registered + burning at
        # this freeze) -- the dep pin carries the two-state honest note
        # per the r541 W30 precedent (finalize runtime composes every
        # registry key below 38 = FAIL-CLOSED honest wait for the W37
        # output once it lands).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W38 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 38 (no 15; W37
        # in-flight = runtime FAIL-CLOSED guard).
        assert sorted(w for w in WAVE_CONFIGS if w < 38) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37], \
            "W38 prior-wave set must derive from registry keys (no 15, incl. 37)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W39 materializer face (r342 bm-c freeze, own-series law
    #     O-20261001-2355 sec.2 -- bm-c's NINTH owned wave after
    #     W14/W17/W20/W23/W26/W29/W32/W37; zero-gap relay after the
    #     W37 FULL CLOSEOUT this same window r342: finalize one-pass
    #     K=79,320, ledger 443,940 chain-linear) ---------------
    _set_wave(39)
    try:
        assert WAVE_CONFIGS[39]["a_seed_base"] == pf.N1_BANDS[39]["a"][0], \
            "W39 A band drift vs law mirror"
        assert WAVE_CONFIGS[39]["b_exit_seed_base"] == \
            pf.N1_BANDS[39]["b_exit"][0], "W39 B band drift vs law mirror"
        assert WAVE_CONFIGS[39].get("engine_owner") == \
            pf.N1_BANDS[39].get("engine_owner") == "bm-c", \
            "W39 engine_owner drift (law mirror parity)"
        w39_a = {A_SEED_BASE + j for j in range(A_N)}
        w39_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w39_a & w39_b), "W39 A/B band overlap"
        assert not (w39_a & reg_ints) and not (w39_b & reg_ints), \
            "W39 hits SEED_REGISTRY"
        for nm, band in (("A", w39_a), ("B", w39_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W39 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W39 {nm} hits W1"
            assert not (band & probes), f"W39 {nm} hits probe seeds"
        # prior-wave disjointness incl. W37 (bm-c, closed FULL-LIFECYCLE
        # this same window -- r342 finalize one-pass K=79,320, ledger
        # 443,940 chain-linear) and W38 (bm-b, registered + burned 12/12
        # + finalize pending at this freeze -- in-flight coexists by
        # band disjointness per r531 law).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38):
            assert not (w39_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W39 A hits W{wprev}"
            assert not (w39_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                 for j in range(B_N)}), f"W39 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W39 bands must clear it.
        n3r1_used39 = set(range(70_000, 70_006))
        assert not (w39_a & n3r1_used39) and not (w39_b & n3r1_used39), \
            "W39 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w39_a & lfc_actual12) and not (w39_b & lfc_actual12), \
            "W39 bands must clear the lfc actual draw range"
        assert not (w39_a & options_actual12) and \
            not (w39_b & options_actual12), \
            "W39 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W39 row, r342): A = arithmetic continuation
        # clean exactly as the W38 row's W39+ WARNING projected; B =
        # FORCED SKIP -- the arithmetic window 42_801..43_000 is REFUSED
        # by the registry point p4_folk=43_000 (tail point), first clean
        # window 43_001..43_200 machine-derived (r307 wave-band tail law
        # precedent W26/W30; candidate == machine-derived, not prose).
        assert WAVE_CONFIGS[39]["a_seed_base"] == 121_004 == 121_003 + 1, \
            "W39 A must start at the W38 A end + 1 (arithmetic continuation)"
        assert 43_000 in reg_ints, \
            "W39 B forced-skip refusal fact missing (p4_folk=43_000)"
        assert WAVE_CONFIGS[39]["b_exit_seed_base"] == 43_001 == 43_000 + 1, \
            "W39 B must start at the refusal point + 1 (forced skip, r307)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W39-SHARD-0",
                                          "n1w39-0of12"), "W39 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W39-SHARD-11",
                                           "n1w39-11of12")
        assert SHARD_DIR.endswith("n1_w39") and OUT.endswith(
            "n1_w39_results.json"), "W39 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W39 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W39_PREREG.md")), \
            "W39 per-wave prereg missing (materializer requirement)"
        # W39 finalize cumulative deps: W17..W37 outputs ALL PRESENT
        # (W34 finalize r528 bm-b K=72,720; W35 finalize bm-a r546
        # K=74,920; W36 finalize bm-b r529 K=77,120; W37 finalize bm-c
        # r342 this same window K=79,320 -- net ledger head 443,940);
        # W38 (bm-b, burned 12/12 + finalize pending at this freeze) --
        # the dep pin carries the two-state honest note per the r541 W30
        # precedent (finalize runtime composes every registry key below
        # 39 = FAIL-CLOSED honest wait for the W38 output once it lands).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W39 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 39 (no 15; W38
        # in-flight = runtime FAIL-CLOSED guard).
        assert sorted(w for w in WAVE_CONFIGS if w < 39) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38], \
            "W39 prior-wave set must derive from registry keys (no 15, incl. 38)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim
    #     exemption): engine lane writes NO claim file (orphan-traffic
    #     ban -- engine waves have no pool entry to harvest-flip);
    #     pool default restored after the probe. ---
    _set_lane("engine")
    try:
        _claim_dir = os.path.join(PATHS.root, "results", "pool_claims",
                                  "SELFTEST-LANE-EXEMPT")
        _pool_claim("SELFTEST-LANE-EXEMPT", "selftest-key",
                    "selftest: engine-lane exemption face (law sec.2)")
        assert not os.path.exists(_claim_dir), \
            "engine lane must not write pool claim files (law sec.2)"
    finally:
        _set_lane("pool")
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
          "sec.4 W7 row, r501 bm-b] + W8 materializer face [same "
          "guard set, dep=W7 present same-window, A=skip-over with "
          "registry-point refusal (law-pinned warning window refused "
          "too), B=stride verbatim, law sec.4 W8 row, r312 bm-c] "
          "+ W9 materializer face [same guard set, dep=W8 present, "
          "arithmetic continuation both tails clean per ADMIT receipt, "
          "law sec.4 W9 row, r506 bm-b] + W10 materializer face [same "
          "guard set, dep=W9 in-flight=runtime FAIL-CLOSED guard "
          "(r307 two-state law), FIRST ENGINE-OWNED WAVE "
          "engine_owner=bm-b per T-2026-10-01-141 s1, arithmetic "
          "continuation both tails clean per ADMIT receipt, law sec.4 "
          "W10 row, r508 bm-b] + W11 materializer face [same guard "
          "set, dep=W10 present (finalize landed r509), SECOND "
          "ENGINE-OWNED WAVE engine_owner=bm-b per never-dry supply "
          "law, arithmetic continuation both tails clean per ADMIT "
          "receipt results/_r510bmb_w11_band_gate.py, law sec.4 W11 "
          "row, r510 bm-b] + W12 materializer face [same guard set, "
          "dep=W11 in-flight=runtime FAIL-CLOSED guard (r307 two-state "
          "law), THIRD ENGINE-OWNED WAVE first bm-a-owned "
          "engine_owner=bm-a per never-dry supply law, A=forced "
          "skip-over per law sec.4 W12 row + ADMIT receipt "
          "results/_r523bma_w12_band_gate.py, B=arithmetic stride "
          "verbatim, options_wave2 actual-range avoidance new face, "
          "r523 bm-a] + W13 materializer face [same guard set, "
          "dep=W12 present (finalize landed r524 bm-a), FOURTH "
          "ENGINE-OWNED WAVE engine_owner=bm-b per sovereignty rotation "
          "law, A=forced skip-over per law sec.4 W13 row + ADMIT receipt "
          "results/_r512bmb_w13_band_gate.py, B=arithmetic stride "
          "verbatim, r513 bm-b] + W14 materializer face [same guard "
          "set, dep=W13 present (finalize landed r513 bm-b), FIFTH "
          "ENGINE-OWNED WAVE first bm-c-owned engine_owner=bm-c per "
          "sovereignty rotation law F-20261001-01 slot W14=bm-c, "
          "arithmetic continuation both tails clean per ADMIT receipt "
          "results/_r325bmc_w14_band_gate.py, law sec.4 W14 row, "
          "r325 bm-c] + W16 materializer face [same guard set, "
          "dep=W14 present (finalize landed r325 bm-c), SIXTH "
          "ENGINE-OWNED WAVE bm-b's fourth engine_owner=bm-b per "
          "sovereignty rotation law F-20261001-01 slot W16=bm-b "
          "(wave number 15 concurrently held by bm-a's N2-W15 draft), "
          "arithmetic continuation both tails clean per ADMIT receipt "
          "results/_r515bmb_w16_band_gate.py, law sec.4 W16 row, "
          "r515 bm-b] + W17 materializer face [same guard set, "
          "dep=W16 present (finalize landed r516 bm-b), SEVENTH "
          "ENGINE-OWNED WAVE bm-c's second engine_owner=bm-c per "
          "sovereignty rotation law F-20261001-01 slot W17=bm-c, "
          "SPLIT tails: A=arithmetic stride verbatim per ADMIT "
          "receipt results/_r328bmc_w17_band_gate.py leg1-A, "
          "B=forced skip-over (lfc actual draw refusal, leg1-B), "
          "law sec.4 W17 row, r328 bm-c] + W18 materializer face "
          "[same guard set, dep=W17 present (finalize landed r328 "
          "bm-c), EIGHTH ENGINE-OWNED WAVE bm-a's second "
          "engine_owner=bm-a per sovereignty rotation law F-20261001-01 "
          "slot W18=bm-a, BOTH tails arithmetic-clean per ADMIT receipt "
          "results/_r530bma_w18_band_gate.py (r-verified "
          "results/_r531bma_w18_admit_reverify.py), r529 N3 "
          "actual-seed-set leg, law sec.4 W18 row, r531 bm-a] "
          "+ W19 materializer face "
          "[same guard set, dep=W16 present (finalize landed r516 "
          "bm-b) + dep=W17 present (finalize landed r328 bm-c), "
          "EIGHTH ENGINE-OWNED WAVE bm-b's fifth engine_owner=bm-b "
          "per sovereignty rotation law F-20261001-01 slot W19=bm-b "
          "(wave number 18 unfrozen, gap notes, r516 derive law), "
          "SAME-WINDOW DOUBLE-FREEZE COLLISION YIELD vs W17 per r511 "
          "commit-order law + MSG-20261001-184x: bands re-based past "
          "W17's registered bands AND W18's published projection "
          "(A=80_001..82_000, B=38_500..38_699, both arithmetic "
          "continuation clean per ADMIT receipt v3 "
          "results/_r517bmb_w19_band_gate.py incl. the MSG-183x "
          "N3-R1 used-seed band leg), old-band products discarded "
          "at yield (12/12 burned, finalize never ran, zero ledger "
          "pollution), law sec.4 W19 row, r518 bm-b] "
          "+ W20 materializer face "
          "[same guard set, dep=W17 present (finalize landed r328 bm-c; "
          "W18/W19 finalize outputs NOT pinned at freeze window -- "
          "in-flight on bm-a/bm-b engines, finalize merge loop stays "
          "FAIL-CLOSED at run time), NINTH ENGINE-OWNED WAVE bm-c's "
          "third engine_owner=bm-c per sovereignty rotation law "
          "F-20261001-01 slot W20=bm-c (r329 pointer gate discharged: "
          "bm-b W19 v3 re-band landed on origin), BOTH tails "
          "arithmetic-clean per ADMIT receipt "
          "results/_r330bmc_w20_band_gate.py (registry-derived "
          "continuation, no skip), N3-R1 used-seed leg, law sec.4 "
          "W20 row, r330 bm-c] + W21 materializer face [same guard "
          "set, dep=W17/W18/W19 outputs present (finalizes landed "
          "r328-c/r532-a/r518-b, ledger head 406,348; W20 finalize "
          "output NOT pinned at freeze window -- bm-c pending, "
          "finalize merge loop stays FAIL-CLOSED at run time), "
          "TENTH ENGINE-OWNED WAVE bm-a's third engine_owner=bm-a "
          "per sovereignty rotation law F-20261001-01 slot W21=bm-a "
          "(W20 row slot assignment verbatim), BOTH tails "
          "arithmetic-clean per ADMIT receipt "
          "results/_r533bma_w21_band_gate.py (registry-derived "
          "continuation, no skip), N3-R1 used-seed leg, law sec.4 "
          "W21 row, r533 bm-a] + W22 materializer face [same guard "
          "set, dep=W17/W18/W19/W20 outputs present (finalizes "
          "landed r328-c/r532-a/r518-b/r331-c, ledger head 408,548; "
          "W20 r331 product byte-restored r519 bm-b after the "
          "c209aa962 closeout stomp; W21 finalize output NOT pinned "
          "at freeze window -- bm-a pending, finalize merge loop "
          "stays FAIL-CLOSED at run time), ELEVENTH ENGINE-OWNED "
          "WAVE bm-b's sixth engine_owner=bm-b per sovereignty "
          "rotation law F-20261001-01 slot W22=bm-b (W21 row slot "
          "assignment verbatim), BOTH tails arithmetic-clean per "
          "ADMIT receipt results/_r519bmb_w22_band_gate.py "
          "(registry-derived continuation, no skip; W21 in-flight "
          "coexists by band disjointness per r531 law), N3-R1 "
          "used-seed leg, law sec.4 W22 row, r519 bm-b] "
          "+ W23 materializer face [same guard "
          "set, dep=W17/W18/W19/W20 outputs present (finalizes "
          "landed r328-c/r532-a/r518-b/r331-c, ledger head 408,548; "
          "W20 r331 product byte-restored r519 bm-b after the "
          "c209aa962 closeout stomp, MSG-201x three-face verified; "
          "W21/W22 finalize outputs NOT pinned at freeze window -- "
          "bm-a burning / bm-b pending, finalize merge loop stays "
          "FAIL-CLOSED at run time), TWELFTH ENGINE-OWNED WAVE "
          "bm-c's fourth engine_owner=bm-c per sovereignty rotation "
          "law F-20261001-01 slot W23=bm-c (W22 row slot assignment "
          "verbatim), BOTH tails arithmetic-clean per ADMIT receipt "
          "results/_r332bmc_w23_band_gate.py (registry-derived "
          "continuation, no skip; W21/W22 in-flight coexist by band "
          "disjointness per r531 law), N3-R1 used-seed leg, law sec.4 "
          "W23 row, r332 bm-c] "
          "+ W24 materializer face [same guard set, dep=W17/W18/W19/W20/"
          "W21/W22 outputs present (finalizes landed r328-c/r532-a/r518-b/"
          "r331-c/r534-a/r519-b, ledger head 412,948; W23 finalize output "
          "NOT pinned at freeze window -- bm-c burning, finalize merge "
          "loop stays FAIL-CLOSED at run time), THIRTEENTH ENGINE-OWNED "
          "WAVE bm-a's fourth engine_owner=bm-a per sovereignty rotation "
          "law F-20261001-01 slot W24=bm-a (W23 row slot assignment "
          "verbatim), BOTH tails arithmetic-clean per ADMIT receipt "
          "results/_r535bma_w24_band_gate.py (registry-derived "
          "continuation, no skip; W23 in-flight coexists by band "
          "disjointness per r531 law), N3-R1 used-seed leg, law sec.4 "
          "W24 row, r535 bm-a] "
          "+ W25 materializer face [same guard set, dep=W17/W18/W19/W20/"
          "W21/W22 outputs present (finalizes landed r328-c/r532-a/r518-b/"
          "r331-c/r534-a/r519-b, ledger head 412,948; W23/W24 finalize "
          "outputs NOT pinned at freeze window -- bm-c burning / bm-a "
          "burn pending, finalize merge loop stays FAIL-CLOSED at run "
          "time), FOURTEENTH ENGINE-OWNED WAVE bm-b's seventh "
          "engine_owner=bm-b per sovereignty rotation law F-20261001-01 "
          "slot W25=bm-b (W24 row slot assignment verbatim), BOTH tails "
          "arithmetic-clean per ADMIT receipt "
          "results/_r520bmb_w25_band_gate.py (registry-derived "
          "continuation, no skip; W23/W24 in-flight coexist by band "
          "disjointness per r531 law), N3-R1 used-seed leg, law sec.4 "
          "W25 row, r520 bm-b] "
          "+ W26 materializer face [same guard set, dep=W17/W18/W19/W20/"
          "W21/W22/W23 outputs present (finalizes landed r328-c/r532-a/"
          "r518-b/r331-c/r534-a/r519-b/r335-c, ledger head 415,148; "
          "W24/W25 finalize outputs NOT pinned at freeze window -- "
          "bm-a/bm-b finalize pending in chain order, finalize merge "
          "loop stays FAIL-CLOSED at run time), FIFTEENTH ENGINE-OWNED "
          "WAVE bm-c's fifth engine_owner=bm-c per sovereignty rotation "
          "law F-20261001-01 slot W26=bm-c (W25 row slot assignment "
          "verbatim), BOTH tails FORCED SKIP per ADMIT receipt "
          "results/_r335bmc_w26_band_gate.py -- A arithmetic 94_001.."
          "96_000 hits the probe-seed cluster 95_000..95_003 (r335 "
          "discovery: gate receipts' reserved universe omitted probe "
          "seeds; caught by this materializer leg) -> first clean "
          "window 95_004..97_003 machine-derived (W12 A-skip family); "
          "B arithmetic 39_900..40_099 hits 40_000/40_001/40_050 "
          "refusal facts (W25 row WARNING) -> first clean window "
          "40_051..40_250 machine-derived (W5/W6/W8/W12/W17 jump "
          "family, R250/r518), N3-R1 used-seed leg, law sec.4 W26 "
          "row, r335 bm-c] "
          "+ W27 materializer face [same guard set, dep=W17..W25 "
          "outputs present (finalizes landed r328-c/r532-a/r518-b/"
          "r331-c/r534-a/r519-b/r335-c/r538-a/r522-b, ledger head "
          "419,548; W26 finalize output NOT pinned at freeze window -- "
          "bm-c burn in progress, finalize merge loop stays "
          "FAIL-CLOSED at run time), SIXTEENTH "
          "ENGINE-OWNED WAVE bm-a's fifth engine_owner=bm-a per "
          "sovereignty rotation law F-20260901-01 slot W27=bm-a (W26 "
          "row slot assignment verbatim), BOTH tails arithmetic-clean "
          "per ADMIT receipt results/_r539bma_w27_band_gate.py "
          "(registry-derived continuation, no skip; W26 W27+ WARNING "
          "projection verified; probe-seed cluster + N3-R1 used-seed "
          "leg), law sec.4 W27 row, r539 bm-a] "
          "+ W28 materializer face [same guard set, dep=W17..W25 "
          "outputs present (finalizes landed r328-c/r532-a/r518-b/"
          "r331-c/r534-a/r519-b/r335-c/r538-a/r522-b, ledger head "
          "419,548; W26/W27 finalize outputs NOT pinned at freeze "
          "window -- bm-c finalize pending / bm-a burning, finalize "
          "merge loop stays FAIL-CLOSED at run time), SEVENTEENTH "
          "ENGINE-OWNED WAVE bm-b's eighth engine_owner=bm-b per "
          "sovereignty rotation law F-20260901-01 slot W28=bm-b (W27 "
          "row slot assignment verbatim), BOTH tails arithmetic-clean "
          "per ADMIT receipt results/_r523bmb_w28_band_gate.py "
          "(registry-derived continuation, no skip; W27 W28+ WARNING "
          "projection verified; probe-seed cluster + N3-R1 used-seed "
          "leg), law sec.4 W28 row, r523 bm-b] "
          "+ W29 materializer face [same guard set, dep=W17..W26 "
          "outputs present (finalizes landed r328-c/r532-a/r518-b/"
          "r331-c/r534-a/r519-b/r335-c/r538-a/r522-b/r336-c, ledger "
          "head 421,748; W27/W28 finalize outputs NOT pinned at freeze "
          "window -- bm-a finalize pending (chain-unblocked by W26) / "
          "bm-b burning, finalize merge loop stays FAIL-CLOSED at run "
          "time), EIGHTEENTH ENGINE-OWNED WAVE bm-c's sixth "
          "engine_owner=bm-c per sovereignty rotation law "
          "F-20260901-01 slot W29=bm-c (W28 row slot assignment "
          "verbatim), BOTH tails arithmetic-clean per ADMIT receipt "
          "results/_r336bmc_w29_band_gate.py (registry-derived "
          "continuation, no skip; W28 W29+ WARNING projection "
          "verified; probe-seed cluster + N3-R1 used-seed leg), "
          "law sec.4 W29 row, r336 bm-c] "
           "+ W30 materializer face [same guard set, dep=W17..W28 "
          "outputs present (W28 finalize landed bm-b r524 mid-draft, "
          "K=59,520, ledger head 426,148, anchor-roll law disclosed; "
          "W29 unregistered, finalize merge loop stays FAIL-CLOSED at "
          "run time, r307 two-state law), NINETEENTH ENGINE-OWNED WAVE bm-a's sixth "
          "engine_owner=bm-a per sovereignty rotation law "
          "F-20260901-01 slot W30=bm-a (W28 row slot assignment "
          "verbatim), DUAL SKIP faces per ADMIT receipt "
          "results/_r541bma_w30_band_gate.py (A = skip past the W29 "
          "PUBLISHED PROJECTION 101_004..103_003 reserved for the "
          "bm-c seat, r518 published=reserved leg; B = in-band point "
          "skip past SEED_REGISTRY p4_batch1=41_000, W26-B re-base "
          "lineage; candidate == machine-derived first clean windows "
          "103_004..105_003 / 41_001..41_200), probe-seed cluster + "
          "N3-R1 used-seed leg, law sec.4 W30 row, r541 bm-a] "
          "+ W31 materializer face [same guard set, dep=W17..W29 "
          "present (W29 finalize landed bm-c r337 mid-draft, K=61,720, "
          "ledger head 428,348, anchor-roll law disclosed; W30 "
          "registered-in-flight two-state dep), BOTH tails arithmetic "
          "continuation per law sec.4 W31 row 105_004..107_003 / "
          "41_201..41_400, first zero-skip wave since W28, r525 bm-b] "
          "+ W32 materializer face [same guard set, dep=W17..W31 "
          "ALL present (every pre-W32 seat closed at freeze: W29 "
          "bm-c r337 K=61,720 / W30 bm-a r542 K=63,920 ledger "
          "430,548 / W31 bm-b K=66,120 ledger 432,748 chain head), "
          "BOTH tails arithmetic continuation per law sec.4 W32 row "
          "107_004..109_003 / 41_401..41_600, zero skip, r339 bm-c] "
          "+ W33 materializer face [same guard set, dep=W17..W32 "
          "ALL present (W32 finalize landed bm-c same-window after "
          "this freeze -- K=68,320 chain-linear, dep-pin auto-join "
          "+32 executed per r531-1 minimal-amendment precedent; at "
          "freeze the pin was W17..W31 with the W32-pending honest "
          "note per r541 W30 precedent), BOTH tails "
          "arithmetic continuation per law sec.4 W33 row "
          "109_004..111_003 / 41_601..41_800, zero skip, "
          "TWENTY-SECOND ENGINE-OWNED WAVE engine_owner=bm-a per "
          "sovereignty rotation law F-20260901-01 slot W33=bm-a "
          "(W32 row slot assignment verbatim), r544 bm-a] "
          "+ W34 materializer face [same guard set, dep=W17..W33 "
          "ALL present (W1..W33 all finalized at this freeze -- the "
          "chain fully caught up, zero pending upstream face for the "
          "first time, no dep-pin auto-join amendment needed), BOTH "
          "tails arithmetic continuation per law sec.4 W34 row "
          "111_004..113_003 / 41_801..42_000, zero skip, "
          "TWENTY-THIRD ENGINE-OWNED WAVE engine_owner=bm-b per "
          "sovereignty rotation law F-20260901-01 slot W34=bm-b + "
          "O-20261001-2355 de-throttle order (W33 row slot assignment "
          "verbatim), r527 bm-b] "
          "+ W35 materializer face [same guard set, dep=W17..W34 "
          "ALL present (W34 registered by the bm-b r528 freeze adopted "
          "in the same merge -- dep-pin auto-join +34 executed per "
          "r531-1/r541 minimal-amendment precedent; finalize runtime "
          "FAIL-CLOSED composes every registry key below 35), FORCED "
          "SKIP over the published "
          "W34 projection windows A 111_004..113_003 / B 41_801..42_000 "
          "(reserved face r518; candidate == published-projection end + 1 "
          "both sides, machine-proven by results/_r545bma_w35_band_gate.py "
          "refusal facts), law sec.4 W35 row 113_004..115_003 / "
          "42_001..42_200, TWENTY-FOURTH ENGINE-OWNED WAVE "
          "engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (first bm-a "
          "wave under the de-throttle law, zero-gap relay after W33 "
          "close), r545 bm-a] "
          "+ W36 materializer face [same guard set, dep=W17..W34 ALL "
          "present + W35 registered-in-flight two-state dep (bm-a "
          "burning at this freeze -- finalize runtime FAIL-CLOSED "
          "composes every registry key below 36), BOTH tails "
          "arithmetic continuation per law sec.4 W36 row "
          "115_004..117_003 / 42_201..42_400, zero skip, "
          "TWENTY-FIFTH ENGINE-OWNED WAVE engine_owner=bm-b per engine "
          "de-throttle law O-20261001-2355 sec.2 own-continuous-series "
          "(zero-gap relay after the W34 full closeout, wave 36 = "
          "first free number after W35's claim), r528 bm-b] "
          "+ W37 materializer face [same guard set, dep=W17..W34 ALL "
          "present + W35/W36 registered-in-flight two-state deps "
          "(W35 burned 12/12 finalize pending; W36 bm-b burning at "
          "this freeze -- finalize runtime FAIL-CLOSED composes every "
          "registry key below 37), BOTH tails arithmetic continuation "
          "per law sec.4 W37 row 117_004..119_003 / 42_401..42_600, "
          "zero skip, TWENTY-SIXTH ENGINE-OWNED WAVE engine_owner=bm-c "
          "per engine de-throttle law O-20261001-2355 sec.2 "
          "own-continuous-series (follows the r341 W36 yield to bm-b "
          "per r511 commit-order law, wave 37 = first free number "
          "after W36's claim), r341 bm-c] "
          "+ W38 materializer face [same guard set, dep=W17..W36 ALL "
          "present (W35 finalize bm-a r546 K=74,920 + W36 finalize "
          "bm-b r529 K=77,120 chain-linear -- dep-pin auto-join +35+36 "
          "executed same window; W37 bm-c registered-in-flight "
          "two-state dep -- finalize runtime FAIL-CLOSED composes "
          "every registry key below 38), BOTH tails arithmetic "
          "continuation per law sec.4 W38 row 119_004..121_003 / "
          "42_601..42_800, zero skip, TWENTY-SEVENTH ENGINE-OWNED "
          "WAVE engine_owner=bm-b per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (zero-gap "
          "relay after the W36 full closeout this same window, wave "
          "38 = first free number after W37's claim), r529 bm-b] "
          "+ W39 materializer face [same guard set, dep=W17..W37 ALL "
          "present (W37 finalize bm-c r342 K=79,320, ledger 443,940 "
          "chain-linear -- dep-pin auto-join +37 executed same "
          "window; W38 bm-b burned-12/12 finalize-pending "
          "two-state dep -- finalize runtime FAIL-CLOSED composes "
          "every registry key below 39), A=arithmetic continuation "
          "clean per law sec.4 W39 row 121_004..123_003 (W38 row "
          "W39+ WARNING projection verified machine-side), "
          "B=FORCED SKIP past SEED_REGISTRY p4_folk=43_000 (the "
          "arithmetic window 42_801..43_000 refused at its tail "
          "point per the W38 row W39+ WARNING; first clean window "
          "43_001..43_200 machine-derived, r307 wave-band tail law), "
          "TWENTY-EIGHTH ENGINE-OWNED WAVE engine_owner=bm-c per "
          "engine de-throttle law O-20261001-2355 sec.2 "
          "own-continuous-series (zero-gap relay after the W37 full "
          "closeout this same window, wave 39 = first free number "
          "after W38's claim), r342 bm-c] "
          "+ T-141 s2 "
          "engine-lane claim exemption [law sec.2 pre-claim exempt "
          "face])")
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
    if "--lane" in argv:
        lane = argv[argv.index("--lane") + 1]
        if lane not in ("pool", "engine"):
            print(f"unknown lane {lane!r} (pool|engine, law sec.2)")
            return 2
        _set_lane(lane)
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
        print("usage: run --shard i --of N [--wave W] [--workers P] "
              "[--lane pool|engine] | finalize [--wave W] | probe | parity | "
              "status [--wave W] | selftest")
        return 2
    if "run" not in argv:
        print("usage: run --shard i --of N [--wave W] [--workers P]")
        return 2
    assert 0 <= shard < nshards, "shard out of range"
    return run_shard(shard, nshards, workers=_resolve_workers(argv))


if __name__ == "__main__":
    sys.exit(main())
