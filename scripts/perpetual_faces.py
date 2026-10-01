"""PERPETUAL_FACES generator v0.3 -- T-133 s2 (CEO O-2026-09-30-2340).

v0.2 (bm-b r485): N1 runner landed (scripts/perpetual_faces_n1.py, wave-2
prereg research/PERPETUAL_N1_W2_PREREG.md frozen pre-run); first-wave W2
materialized via autofill submit per law freeze-signature sequencing line
("runner lands one batch, materialize one batch").

v0.3 (bm-b r490): per-shard materializer pattern landed (the "next slice"
the v0.2 registry promised). Runner is wave-parameterized (v0.3 --wave,
law sec.4 pre-assigned rows W2/W3; spawn-side wave carrier via executor
initargs). supply() now expands the next law wave into 12 per-shard pool
entries (W2 registration face verbatim) when the 3-leg trigger fires;
per-wave prereg presence is the materialization gate (never fake-supply);
pool rewrites mirror the file's probed indent/EOL (r289 format law).

Law: research/PERPETUAL_FACES.md v1.0 (FROZEN bm-b r484 2026-09-30).
Face-level prereg frozen ONCE (ticket law); per-wave preregs (R99
discipline) reference the law's pre-assigned seed bands (sec.4 ledger,
R250 one-step law -- bands frozen here BEFORE any wave runner exists,
no re-pick after freeze).

Faces (law sec.2):
  N1 nulls-deepening        base: p2_null_calibration(.ext) pattern
  N2 random-subspace        base: trial_labor chain grammar (exploration)
  N3 neighborhood robustness base: t24_g2_pack.py generalization
  N4 bootstrap alternate-history  base: engine replay + resample layer

v0.1 scope: trigger evaluation + flags + face registry + seed-band
disjointness selftest + honest no-op when no face runner has landed.
Materialization (pool entry write) activates per-face as runners land
(law freeze-signature sequencing: N1-W2 -> N3-R1 -> N2-W15 -> N4-B1);
a face with runner=None is NEVER materialized (fake-supply ban, law
sec.1 honest clause).

Contract (law sec.1/sec.3):
  supply   evaluate 3-leg trigger (pool starving AND py<70 AND no
           same-face in-flight wave) -> materialize next wave for the
           first runner-landed face in priority order N1>N3>N2>N4 as
           12 per-shard entries (per-wave prereg required, never
           fake-supply; next wave derived from pool entry truth).
           Writes flags to results/perpetual_faces_state.json
           (pool_starved / supply_floor / faces_pending) consumed by
           the s3 daily-report/CEO-face wiring.  exit 0 normal (incl.
           honest no-op), 2 mechanism failure.
  status   read-only trigger face + registry + flags report. exit 0/2.
  selftest offline hermetic checks (no network, no pool writes):
           face registry integrity, seed-band disjointness vs
           science_gates.SEED_REGISTRY + v1/ext in-use bands, pool
           parse, state round-trip, materializer expansion face,
           pool format-mirror probe. exit 0/1.

Single-writer law: pool file written ONLY by this lane-machine
generator on materialization; autofill stays read-only (pool schema
single_writer note, unchanged). All materialized entries carry
worker_class=self-contained, lane_owner=ANY (R31/R65 lawful).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS  # noqa: E402
import science_gates as sg  # noqa: E402

LAW_REF = "research/PERPETUAL_FACES.md v1.0 (T-133 s2, O-2026-09-30-2340)"
STATE_PATH = os.path.join(PATHS.results_dir, "perpetual_faces_state.json")
POOL_PATH = os.path.join(PATHS.results_dir, "runnable_pool.json")

# --- law sec.4 pre-assigned seed bands (frozen, append-only ledger) ---
N1_BANDS = {
    2: {"a": (12_100, 14_099), "b_exit": (21_100, 21_299)},
    3: {"a": (14_100, 16_099), "b_exit": (21_300, 21_499)},
    4: {"a": (16_100, 18_099), "b_exit": (21_500, 21_699)},
    # W5 (r307 bm-c, prereg-time tail extension per the law's "波5+ 顺延"
    # clause): the arithmetic +2_000 tail (18_100..20_099) collides with
    # the v1 B in-use band 20_000..20_019, SEED_REGISTRY value 20000 and
    # the ext W1 B band 20_100..20_299 -- the disjointness hard law
    # (selftest leg 2, R250) wins over the stride convention, so A skips
    # to the first contiguous 2,000-window beyond every reserved band
    # (21_900 == W5 B end + 1, packing invariant in selftest leg 3b).
    # NOT a re-pick: the W5 band was never assigned and the measurement
    # face has no result to fish. W6+ WARNING: the B +200 arithmetic tail
    # (21_900..22_099) now lands inside the W5 A band -- the W6 prereg
    # must re-base B with the same disclosed skip-over discipline.
    5: {"a": (21_900, 23_899), "b_exit": (21_700, 21_899)},
    # W6 (r309 bm-c, prereg-time extension per the law's pinned W6+
    # WARNING): B keeps its arithmetic stride concept but the +200 tail
    # (21_900..22_099) is documented-refused (falls inside the W5 A band
    # 21_900..23_899) -- disjointness hard law wins, so B skips past
    # every reserved band INCLUDING this wave's own A band and packs at
    # the first free 200-window (== W6 A end + 1). A itself keeps the
    # arithmetic +2_000 tail verbatim (23_900 == W5 A end + 1, no
    # collision). NOT a re-pick: W6 bands were never assigned and the
    # measurement face has no result to fish (R250).
    6: {"a": (23_900, 25_899), "b_exit": (25_900, 26_099)},
    # W7 (r501 bm-b, prereg-time extension, same pinned skip-over
    # discipline -- BOTH tails refused this wave): A's arithmetic
    # +2_000 tail (25_900..27_899) is documented-refused (falls on the
    # W6 B band 25_900..26_099), so A skips past every reserved band and
    # packs at the first free 2,000-window (W6 B end + 1 == 26_100);
    # B's arithmetic +200 tail (26_100..26_299) is in turn refused (it
    # falls inside THIS wave's own A band), so B skips past every
    # reserved band including this wave's A and packs at W7 A end + 1.
    # Refusal facts machine-proven in selftest leg 3d. NOT a re-pick:
    # W7 bands were never assigned, measurement face has nothing to
    # fish (R250). W8+ WARNING: A's arithmetic tail (28_100..30_099)
    # will land on the W7 B band -- W8 must re-base A the same way.
    7: {"a": (26_100, 28_099), "b_exit": (28_100, 28_299)},
    # W8 (r312 bm-c, prereg-time extension -- the law sec.4 pinned W8+
    # WARNING window itself is gate-refused): A's arithmetic +2_000
    # tail (28_100..30_099) is documented-refused -- hits the W7 B band
    # (28_100..28_299) AND the SEED_REGISTRY lfc_p1_screen point
    # 30_000 (actual draw range 30_000..30_099, N_RAND=50 x 2 exit
    # regimes); the law-pinned first-free prediction (28_300..30_299)
    # is refused by the same point + actual range -- so A packs at the
    # first 2,000-window clear of every reserved band AND the lfc
    # actual draw range (30_100..32_099); B's arithmetic +200 tail
    # (28_300..28_499) is clean this wave and keeps the stride
    # verbatim. NOT a re-pick (R250). N2/N4 yield note: this A band
    # covers the 30_000+ domain -- N2-W15 draft probe bands
    # (31_000/31_500/32_000) must re-pick at their freeze per law
    # sec.4 (MSG heads-up r312). W9+ WARNING: both arithmetic tails
    # project clean next wave (A 32_100..34_099, B 28_500..28_699) --
    # no forced skip expected; verify at prereg time as always.
    8: {"a": (30_100, 32_099), "b_exit": (28_300, 28_499)},
    # W9 (r506 bm-b, prereg-time extension per O-20261001-1332 sec.1.2 --
    # arithmetic tails land clean exactly as the W8 row projected): A
    # 32_100 == W8 A end + 1, B 28_500 == W8 B end + 1; no skip-over
    # this wave, both strides kept verbatim. Machine-verified at prereg
    # time against every reserved band + SEED_REGISTRY + the lfc actual
    # draw range (results/_r506bmb_w9_band_gate.py ADMIT receipt); the
    # all-bands disjoint leg 2 covers W9 automatically once listed.
    # NOT a re-pick (R250). N2/N4 yield note: this A band covers
    # 32_100..34_099 -- N2/N4 preregs must steer clear per law sec.4.
    9: {"a": (32_100, 34_099), "b_exit": (28_500, 28_699)},
    # W10 (r508 bm-b, prereg-time extension per T-2026-10-01-141 s1 --
    # FIRST ENGINE-OWNED WAVE: engine_owner=bm-b -> burned by the
    # saturation engine local perpetual queue (SATURATION_ENGINE_LAW
    # sec.1/sec.2), NEVER pool-materialized -- cmd_supply refuses
    # engine-owned waves (zero cross-machine duplication face);
    # arithmetic tails land clean exactly as the W9 row projected):
    # A 34_100 == W9 A end + 1, B 28_700 == W9 B end + 1; no skip-over
    # this wave, both strides kept verbatim. Machine-verified at prereg
    # time (results/_r508bmb_w10_band_gate.py ADMIT receipt); the
    # all-bands disjoint leg 2 covers W10 automatically once listed.
    # NOT a re-pick (R250). N2/N4 yield note: this A band covers
    # 34_100..36_099 -- N2/N4 preregs must steer clear per law sec.4.
    10: {"a": (34_100, 36_099), "b_exit": (28_700, 28_899),
         "engine_owner": "bm-b"},
    # W11 (r510 bm-b, prereg-time extension per the never-dry supply law --
    # SECOND ENGINE-OWNED WAVE: engine_owner=bm-b, burned by the
    # saturation engine local perpetual queue (SATURATION_ENGINE_LAW
    # sec.1/sec.2), NEVER pool-materialized -- cmd_supply refuses
    # engine-owned waves; arithmetic tails land clean exactly as the W10
    # row projected): A 36_100 == W10 A end + 1, B 28_900 == W10 B end + 1;
    # no skip this wave, both strides kept verbatim. Machine-verified at
    # prereg time against the pre-W11 9-row state + 158 SEED_REGISTRY
    # values + the lfc actual draw range (results/_r510bmb_w11_band_gate.py
    # ADMIT receipt); the all-bands disjoint leg 2 covers W11 automatically
    # once listed. NOT a re-pick (R250). N2/N4 yield note: this A band
    # covers 36_100..38_099 -- N2/N4 preregs must steer clear per law
    # sec.4. W12+ WARNING: A +2_000 arithmetic tail 38_100..40_099 contains
    # the N2/N4 design-probe reserved points 40_000/40_001 -> W12 prereg
    # must skip-position A (machine gate decides; B +200 = 29_100..29_299
    # projects clean, still verified at that time).
    11: {"a": (36_100, 38_099), "b_exit": (28_900, 29_099),
         "engine_owner": "bm-b"},
    # W12 (r523 bm-a, prereg-time extension per the W11 row's W12+
    # WARNING): A's +2_000 arithmetic tail (38_100..40_099) is REFUSED --
    # N2/N4 design-probe reserved points 40_000/40_001 + SEED_REGISTRY
    # new_signal_p1 40_000 / new_signal_p1_ce 40_050 -- so A skips to the
    # first 2,000-window clear of every reserved band AND the actual draw
    # ranges (63_050..65_049; options_wave2 actual 63_000..63_049 avoided,
    # lfc leg-3e family); B keeps the +200 stride verbatim (29_100 ==
    # W11 B end + 1, clean). Third engine-owned wave, FIRST bm-a-owned.
    # ADMIT receipt: results/_r523bma_w12_band_gate.py. Skip is FORCED,
    # NOT a re-pick (R250). W13+ WARNING: A +2_000 arithmetic tail
    # 65_050..67_049 hits SEED_REGISTRY bond_carry_w3a 66_000 /
    # p1e_zoo_behavior 67_000 / p1e_synth_null_b 67_200 -> W13 prereg
    # must skip-position A again; B +200 = 29_300..29_499 projects clean,
    # still verified at that time.
    12: {"a": (63_050, 65_049), "b_exit": (29_100, 29_299),
         "engine_owner": "bm-a"},
    # W13 (r512 bm-b, prereg-time extension per the W12 row's W13+
    # WARNING -- never-dry supply law standing step / r512 watermark-red
    # anti-idle root fix): A's +2_000 arithmetic tail (65_050..67_049) is
    # REFUSED -- SEED_REGISTRY cluster bond_carry_w3a 66_000 /
    # p1e_zoo_behavior 67_000 -- so A skips to the first 2,000-window
    # clear of every reserved band AND the actual draw ranges
    # (70_001..72_000); B keeps the +200 stride verbatim (29_300 ==
    # W12 B end + 1, clean). FOURTH engine-owned wave, bm-b's third.
    # ADMIT receipt: results/_r512bmb_w13_band_gate.py. Skip is FORCED,
    # NOT a re-pick (R250). W14+ WARNING: A +2_000 arithmetic tail
    # 72_001..74_000 and B +200 tail 29_500..29_699 project clean on the
    # current registry face -- verify at prereg time as always.
    13: {"a": (70_001, 72_000), "b_exit": (29_300, 29_499),
         "engine_owner": "bm-b"},
    # W14 (r325 bm-c, prereg-time extension per the W13 row's W14+
    # WARNING -- never-dry supply law standing step / r325 watermark-red
    # runnable-work-idle-low-cpu root fix; sovereignty rotation law
    # F-20261001-01 slot: W13=bm-b anchored / W14=bm-c / W15=bm-a):
    # BOTH arithmetic tails land clean exactly as the W13 row projected
    # (A 72_001 == W13 A end + 1, B 29_500 == W13 B end + 1) -- no forced
    # skip this wave; machine-verified at prereg time
    # (results/_r325bmc_w14_band_gate.py ADMIT receipt, 12-row N1_BANDS +
    # 158 registry values + lfc/options actual ranges). FIFTH engine-owned
    # wave, bm-c's first. NOT a re-pick (R250). W15+ WARNING: A +2_000
    # arithmetic tail 74_001..76_000 and B +200 tail 29_700..29_899
    # project clean on the current registry face -- verify at prereg time
    # as always.
    14: {"a": (72_001, 74_000), "b_exit": (29_500, 29_699),
         "engine_owner": "bm-c"},
    # W16 (r515 bm-b, prereg-time extension per the W14 row's W15+
    # WARNING -- never-dry supply law standing step / r515 watermark-red
    # anti-idle root fix; sovereignty rotation law F-20261001-01 slot:
    # W13=bm-b anchored, +3 -> W16=bm-b; unified wave number 15 is
    # concurrently held by bm-a's N2-W15 draft (seed domain 30_000+/
    # 40_000+ per law sec.4 N2/N4 row -- disjoint from this 74_001+
    # domain), so the N1 face numbering continues at W16 with NO W15
    # row): BOTH arithmetic tails land clean exactly as the W14 row
    # projected (A 74_001 == W14 A end + 1, B 29_700 == W14 B end + 1) --
    # no forced skip this wave; machine-verified at prereg time
    # (results/_r515bmb_w16_band_gate.py ADMIT receipt, 13-row N1_BANDS +
    # 158 registry values + N2/N4 probe points + N2-W15 draft probe
    # points + lfc/options actual ranges). SIXTH engine-owned wave,
    # bm-b's fourth. NOT a re-pick (R250). W17+ WARNING: A +2_000
    # arithmetic tail 76_001..78_000 projects clean on the current
    # registry face; B +200 tail 29_900..30_099 is REFUSED by projection
    # (hits the lfc actual draw 30_000..30_099 -- SEED_REGISTRY point
    # 30_000 inside) -> W17 prereg must skip-position B (machine gate
    # decides; W5/W6/W8 skip family); A tail still verified at that time.
    16: {"a": (74_001, 76_000), "b_exit": (29_700, 29_899),
         "engine_owner": "bm-b"},
    # W17 (r328 bm-c, prereg-time extension per the W16 row's W17+
    # WARNING -- never-dry supply law standing step / r328 watermark-red
    # anti-idle root fix; sovereignty rotation law F-20261001-01 slot:
    # W14=bm-c anchored, +3 -> W17=bm-c, bm-c's SECOND owned wave):
    # SPLIT tails -- A's arithmetic +2_000 tail (76_001..78_000 == W16
    # A end + 1) lands clean exactly as the W16 row projected (stride
    # kept verbatim, no skip); B's arithmetic +200 tail (29_900..30_099)
    # is REFUSED as projected (hits the lfc actual draw 30_000..30_099,
    # SEED_REGISTRY point lfc_p1_screen=30_000 inside) -- B re-bases
    # past every reserved band incl. this wave's own A band, packing at
    # the first clean 200-window (38_100..38_299, W11 A end + 1) per
    # the W5/W6/W8/W12 forced-skip-over family. Skip is FORCED (leg1-B
    # refusal facts), NOT a re-pick (R250). Machine-verified at prereg
    # time (results/_r328bmc_w17_band_gate.py ADMIT receipt, 14-row
    # N1_BANDS + 158 registry values + N2/N4 probe points + N2-W15
    # draft probe points + lfc/options actual ranges). SEVENTH
    # engine-owned wave. W18+ WARNING: A +2_000 tail 78_001..80_000 and
    # B +200 tail 38_300..38_499 project clean -- verify at W18 prereg
    # (rotation slot W18=bm-a).
    17: {"a": (76_001, 78_000), "b_exit": (38_100, 38_299),
         "engine_owner": "bm-c"},
    # W18 (r530 bm-a, prereg-time extension per the W17 row's W18+
    # WARNING -- never-dry supply law standing step; sovereignty
    # rotation law F-20261001-01 slot W18=bm-a per law sec.4 W17 row
    # verbatim, bm-a's SECOND owned N1 wave after W12; freeze window
    # opened only AFTER the W17xW19 same-band double-freeze adjudication
    # landed (MSG-184x/185x: W17 stands, bm-b W19 yields; mirrors healed
    # 6efed57b6)): BOTH tails arithmetic-clean for the first time since
    # the W5/W6/W8/W12/W17 B-skip family -- A's +2_000 tail
    # (78_001..80_000 == W17 A end + 1) and B's +200 tail
    # (38_300..38_499 == W17 B end + 1) both land clean exactly as the
    # W17 row projected (stride kept verbatim, no skip on either side).
    # Machine-verified at prereg time (results/_r530bma_w18_band_gate.py
    # ADMIT receipt, 15-row N1_BANDS + 158 registry values + N2/N4
    # probe points + N2-W15 draft probe points + lfc/options actual
    # ranges + r529-mandated N3-R1 actual-seed-set leg 70_000..70_005).
    # EIGHTH engine-owned wave. W19+ WARNING: A +2_000 tail 80_001..82_000
    # and B +200 tail 38_500..38_699 project clean -- verify at W19
    # prereg (bm-b W19 yield re-band must machine-scan past this W18
    # freeze per post-to-yield rotation law).
    18: {"a": (78_001, 80_000), "b_exit": (38_300, 38_499),
         "engine_owner": "bm-a"},
    # W19 (r517 bm-b freeze + r518 SAME-WINDOW DOUBLE-FREEZE COLLISION
    # YIELD + re-band -- r511 commit-order law: bm-c's W17 rows reached
    # origin first (r328, ~18:23) while the r517 W19 freeze was drafted
    # blind to it; both machines deterministic-same-verdict the W16
    # table-tail continuation (A 76_001..78_000 + B skip-over
    # 38_100..38_299) -- bm-b is the latercomer and YIELDS per
    # MSG-20261001-184x. Old-band W19 shard products (12/12 burned,
    # engine finished shards 9-11 at 18:30-18:32 before truncation
    # could land; finalize NEVER ran -> zero science-ledger pollution)
    # all discarded at yield. Re-band skips past BOTH W17's registered
    # bands AND W18's PUBLISHED PROJECTION (A 78_001..80_000 / B
    # 38_300..38_499, rotation slot W18=bm-a, published in the W17 row
    # W18+ WARNING + bm-a r529 gate projection CLEAN -- taking them for
    # W19 would manufacture a THIRD collision against bm-a's slot; r511
    # exhaustive-reservation-scan lesson: published projections are
    # reserved faces). W19 v3 bands = first clean arithmetic continuation
    # past W18's projection: A 80_001..82_000 (== W18 projected A end
    # + 1), B 38_500..38_699 (== W18 projected B end + 1), both tails
    # arithmetic clean. Machine-verified at re-freeze time
    # (results/_r517bmb_w19_band_gate.py v3 ADMIT receipt vs the 15-row
    # union table incl. W17 + W18 published projection + N3-R1 used-seed
    # band 70_000..70_005 (MSG-183x mandatory leg) + SEED_REGISTRY 158
    # values + N2/N4 + N2-W15 draft probes + lfc/options actual ranges).
    # NOT a re-pick (R250: the pre-yield W19 assignment is voided by
    # the collision; the measurement face has zero results to fish --
    # finalize never ran, ledger +0). W20+ WARNING: A +2_000 tail
    # 82_001..84_000 and B +200 tail 38_700..38_899 project clean --
    # verify at W20 prereg (rotation slot W20=bm-c).
    19: {"a": (80_001, 82_000), "b_exit": (38_500, 38_699),
         "engine_owner": "bm-b"},
    # W20 (r330 bm-c, prereg-time extension per the W19 row's W20+ WARNING
    # -- never-dry supply law standing step; sovereignty rotation law
    # F-20261001-01 slot W20=bm-c per law sec.4 W19 row verbatim, bm-c's
    # THIRD owned wave after W14/W17; freeze window opened only AFTER
    # bm-b's W19 yield disposition landed on origin (r329 pointer gate:
    # W19 v3 re-band row in-canon, A 80_001..82_000 / B 38_500..38_699,
    # prereg frozen, engine burning on bm-b)): BOTH tails
    # arithmetic-clean exactly as the W19 row projected -- A's +2_000
    # tail (82_001..84_000 == W19 A end + 1) and B's +200 tail
    # (38_700..38_899 == W19 B end + 1), no skip on either side (38k-
    # segment continuation of the W17 B re-base lineage). Machine-
    # verified at prereg time (results/_r330bmc_w20_band_gate.py ADMIT
    # receipt vs the 17-row pre-W20 table incl. W18/W19 + SEED_REGISTRY
    # values + N2/N4 probe points + N2-W15 draft probe points +
    # lfc/options actual ranges + N3-R1 used-seed band 70_000..70_005,
    # MSG-183x r529 mandatory leg). NINTH engine-owned wave. NOT a
    # re-pick (R250: W20 bands were never assigned; the measurement
    # face has no result to fish). W21+ WARNING: A +2_000 tail
    # 84_001..86_000 and B +200 tail 38_900..39_099 projection
    # per the r330 gate receipt -- verify at W21 prereg (rotation
    # slot W21=bm-a).
    # W21 (r533 bm-a, prereg-time extension per the W20 row's W21+ WARNING
    # -- never-dry supply law standing step; sovereignty rotation law
    # F-20261001-01 slot W21=bm-a per law sec.4 W20 row verbatim, bm-a's
    # THIRD owned wave after W12/W18; no pointer gate pending: W20
    # registered + burned 12/12 by bm-c r330, its finalize sequenced
    # independently by the registry chain order): BOTH tails
    # arithmetic-clean exactly as the W20 row projected -- A's +2_000
    # tail (84_001..86_000 == W20 A end + 1) and B's +200 tail
    # (38_900..39_099 == W20 B end + 1), no skip on either side (38k-
    # segment continuation of the W17 B re-base lineage). Machine-
    # verified at prereg time (results/_r533bma_w21_band_gate.py ADMIT
    # receipt vs the 19-row pre-W21 table incl. W18/W19/W20 +
    # SEED_REGISTRY values + N2/N4 probe points + N2-W15 draft probe
    # points + lfc/options actual ranges + N3-R1 used-seed band
    # 70_000..70_005, MSG-183x r529 mandatory leg). TENTH engine-owned
    # wave. NOT a re-pick (R250: W21 bands were never assigned; the
    # measurement face has no result to fish). W22+ WARNING: A +2_000
    # tail 86_001..88_000 and B +200 tail 39_100..39_299 projection
    # per the r533 gate receipt -- verify at W22 prereg (rotation
    # slot W22=bm-b).
    20: {"a": (82_001, 84_000), "b_exit": (38_700, 38_899),
         "engine_owner": "bm-c"},
    21: {"a": (84_001, 86_000), "b_exit": (38_900, 39_099),
         "engine_owner": "bm-a"},
    # W22 (r519 bm-b, prereg-time extension per the W21 row's W22+ WARNING
    # -- never-dry supply law standing step; sovereignty rotation law
    # F-20261001-01 slot W22=bm-b per law sec.4 W21 row verbatim, bm-b's
    # SIXTH owned wave after W10/W11/W13/W16/W19; no pointer gate pending:
    # W20 registered + burned 12/12 + FINALIZED by bm-c r331 (K=41,920,
    # ledger 408,548; r331 product byte-restored r519 bm-b after the
    # c209aa962 closeout stomp, zero science pollution), W21 registered
    # + burning by bm-a r533 -- coexistence judged by band disjointness
    # not commit order, r531 law): BOTH tails arithmetic-clean exactly as
    # the W21 row projected -- A's +2_000 tail (86_001..88_000 == W21 A
    # end + 1) and B's +200 tail (39_100..39_299 == W21 B end + 1), no
    # skip on either side (38k-segment continuation of the W17 B re-base
    # lineage). Machine-verified at prereg time
    # (results/_r519bmb_w22_band_gate.py ADMIT receipt vs the 20-row
    # pre-W22 table incl. W18/W19/W20/W21 + SEED_REGISTRY values + N2/N4
    # probe points + N2-W15 draft probe points + lfc/options actual
    # ranges + N3-R1 used-seed band 70_000..70_005, MSG-183x r529
    # mandatory leg). ELEVENTH engine-owned wave. NOT a re-pick (R250:
    # W22 bands were never assigned; the measurement face has no result
    # to fish). W23+ WARNING: A +2_000 tail 88_001..90_000 and B +200
    # tail 39_300..39_499 projection per the r519 gate receipt -- verify
    # at W23 prereg (rotation slot W23=bm-c).
    22: {"a": (86_001, 88_000), "b_exit": (39_100, 39_299),
         "engine_owner": "bm-b"},
    # W23 (r332 bm-c, prereg-time extension per the W22 row's W23+ WARNING
    # -- never-dry supply law standing step; sovereignty rotation law
    # F-20261001-01 slot W23=bm-c per law sec.4 W22 row verbatim, bm-c's
    # FOURTH owned wave after W14/W17/W20; no pointer gate pending: W20
    # registered + burned 12/12 + FINALIZED by bm-c r331 (K=41,920,
    # ledger 408,548 chain head; product byte-restored r519 bm-b after
    # the c209aa962 closeout stomp, zero science pollution, MSG-201x
    # three-face verified), W21 registered + burning by bm-a r533 (r534
    # pushed shards 6-10, finalize pending on bm-a), W22 registered by
    # bm-b r519 (engine burn pending on bm-b) -- coexistence judged by
    # band disjointness not commit order, r531 law): BOTH tails
    # arithmetic-clean exactly as the W22 row projected -- A's +2_000
    # tail (88_001..90_000 == W22 A end + 1) and B's +200 tail
    # (39_300..39_499 == W22 B end + 1), no skip on either side (39k-
    # segment continuation of the W17 B re-base lineage). Machine-
    # verified at prereg time (results/_r332bmc_w23_band_gate.py ADMIT
    # receipt vs the 21-row pre-W23 table incl. W18/W19/W20/W21/W22 +
    # SEED_REGISTRY values + N2/N4 probe points + N2-W15 draft probe
    # points + lfc/options actual ranges + N3-R1 used-seed band
    # 70_000..70_005, MSG-183x r529 mandatory leg). TWELFTH engine-owned
    # wave. NOT a re-pick (R250: W23 bands were never assigned; the
    # measurement face has no result to fish). W24+ WARNING: A +2_000
    # tail 90_001..92_000 and B +200 tail 39_500..39_699 projection per
    # the r332 gate receipt -- verify at W24 prereg (rotation slot
    # W24=bm-a).
    23: {"a": (88_001, 90_000), "b_exit": (39_300, 39_499),
         "engine_owner": "bm-c"},
    # W24 (r535 bm-a, prereg-time extension per the W23 row's W24+ WARNING
    # -- never-dry supply law standing step; sovereignty rotation law
    # F-20261001-01 slot W24=bm-a per law sec.4 W23 row verbatim, bm-a's
    # FOURTH owned wave after W12/W18/W21; no pointer gate pending:
    # W21 registered + burned 12/12 + FINALIZED by bm-a r534 (K=44,120,
    # ledger 410,748), W22 registered + burned + FINALIZED by bm-b r519
    # addendum (K=46,320, ledger 412,948 chain head), W23 registered by
    # bm-c r332 (engine burn pending on bm-c) -- coexistence judged by
    # band disjointness not commit order, r531 law): BOTH tails
    # arithmetic-clean exactly as the W23 row projected -- A's +2_000
    # tail (90_001..92_000 == W23 A end + 1) and B's +200 tail
    # (39_500..39_699 == W23 B end + 1), no skip on either side (39k-
    # segment continuation of the W17 B re-base lineage). Machine-
    # verified at prereg time (results/_r535bma_w24_band_gate.py ADMIT
    # receipt vs the 22-row pre-W24 table incl. W18/W19/W20/W21/W22/W23
    # + SEED_REGISTRY values + N2/N4 probe points + N2-W15 draft probe
    # points + lfc/options actual ranges + N3-R1 used-seed band
    # 70_000..70_005, MSG-183x r529 mandatory leg). THIRTEENTH
    # engine-owned wave. NOT a re-pick (R250: W24 bands were never
    # assigned; the measurement face has no result to fish). W25+
    # WARNING: A +2_000 tail 92_001..94_000 and B +200 tail
    # 39_700..39_899 projection per the r535 gate receipt -- verify at
    # W25 prereg (rotation slot W25=bm-b).
    24: {"a": (90_001, 92_000), "b_exit": (39_500, 39_699),
         "engine_owner": "bm-a"},
    # W25 (r520 bm-b, prereg-time extension per the W24 row's W25+ WARNING
    # -- never-dry supply law standing step; sovereignty rotation law
    # F-20261001-01 slot W25=bm-b per law sec.4 W24 row verbatim, bm-b's
    # SEVENTH owned wave after W10/W11/W13/W16/W19/W22; no pointer gate
    # pending: W22 registered + burned + FINALIZED by bm-b r519 addendum
    # (K=46,320, ledger 412,948 chain head), W23 registered by bm-c r332
    # (engine burn in flight, finalize pending on bm-c), W24 registered
    # by bm-a r535 (engine burn pending on bm-a) -- coexistence judged by
    # band disjointness not commit order, r531 law): BOTH tails
    # arithmetic-clean exactly as the W24 row projected -- A's +2_000
    # tail (92_001..94_000 == W24 A end + 1) and B's +200 tail
    # (39_700..39_899 == W24 B end + 1), no skip on either side (39k-
    # segment continuation of the W17 B re-base lineage). Machine-
    # verified at prereg time (results/_r520bmb_w25_band_gate.py ADMIT
    # receipt vs the 23-row pre-W25 table incl. W18..W24 + SEED_REGISTRY
    # values + N2/N4 probe points + N2-W15 draft probe points +
    # lfc/options actual ranges + N3-R1 used-seed band 70_000..70_005,
    # MSG-183x r529 mandatory leg). FOURTEENTH engine-owned wave. NOT a
    # re-pick (R250: W25 bands were never assigned; the measurement
    # face has no result to fish). W26+ WARNING: A +2_000 tail
    # 94_001..96_000 projects clean; B +200 tail 39_900..40_099 WILL
    # HIT the N2/N4 design-probe reserved points 40_000/40_001 --
    # W26 (bm-c slot) must run the disjoint machine gate and jump B to
    # the first clean window past all reserved faces (W5/W6/W8/W12/W17
    # jump family precedent; projection REFUSED per the r520 gate
    # receipt -- verify at W26 prereg).
    25: {"a": (92_001, 94_000), "b_exit": (39_700, 39_899),
         "engine_owner": "bm-b"},
    # W26 (r335 bm-c, prereg-time extension per the W25 row's W26+
    # WARNING -- never-dry supply law standing step; sovereignty rotation
    # law F-20261001-01 slot W26=bm-c per law sec.4 W25 row verbatim,
    # bm-c's FIFTH owned wave after W14/W17/W20/W23; no pointer gate
    # pending: W23 registered + burned + FINALIZED by bm-c r335 (K=48,520,
    # ledger 415,148 chain head -- unblocks W24 finalize in chain order),
    # W24 registered + burned 12/12 by bm-a r536, W25 registered + burned
    # 12/12 by bm-b r521 -- coexistence judged by band disjointness not
    # commit order, r531 law): BOTH tails FORCED SKIP -- A's +2_000 tail
    # (94_001..96_000 == W25 A end + 1) REFUSED by the r335 DISCOVERY:
    # it hits ALL FOUR runner design-probe seeds (ext 95_000/95_001 +
    # n1 95_002/95_003, batch-band-reserved by the selftest disjoint
    # law) -- the r520/r535 gate receipts' reserved universe omitted the
    # probe cluster (the W25 row's "A projects clean" WARNING was a
    # blind-spot miss, caught by the n1 materializer selftest leg; past
    # waves W24/W25 clear the cluster -- zero retroactive harm) -> jump
    # to the first clean 2,000-window: 95_004..97_003 (W12 A-skip
    # precedent); B's +200 tail (39_900..40_099) FORCED SKIP
    # exactly as the W25 row WARNING projected (hits N2/N4 design-probe
    # retention points 40_000/40_001 AND SEED_REGISTRY value 40_050 --
    # machine refusal facts in the gate receipt) -> jump to the first
    # continuous 200-window clear of all reserved faces: 40_051..40_250
    # (W5/W6/W8/W12/W17 jump-family precedent, machine-derived never a
    # free pick R250/r518). Machine-verified at prereg time
    # (results/_r335bmc_w26_band_gate.py ADMIT receipt vs the 24-row
    # pre-W26 table incl. W21/W22/W23/W24/W25 + SEED_REGISTRY + probes/
    # actuals + probe-seed cluster r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg). NOT a re-pick
    # (R250: W26 bands were never assigned; the measurement face has no
    # result to fish).
    26: {"a": (95_004, 97_003), "b_exit": (40_051, 40_250),
         "engine_owner": "bm-c"},
    # W27 (r539 bm-a, prereg-time extension per the W26 row's W27+
    # WARNING -- never-dry supply law standing step; sovereignty rotation
    # law F-20260901-01 slot W27=bm-a per the W26 row verbatim, bm-a's
    # FIFTH owned wave after W12/W18/W21/W24; no pointer gate pending:
    # W24 registered + burned 12/12 + FINALIZED by bm-a r538 (K=50,720,
    # ledger 417,348), W25 registered + burned 12/12 + FINALIZED by
    # bm-b r522 (K=52,920, ledger 419,548 chain head), W26
    # registered + burn in progress by bm-c r335 (finalize pending on
    # the bm-c seat) -- coexistence judged by band disjointness not
    # commit order, r531 law): BOTH tails arithmetic-clean exactly as
    # the W26 row projected (A's +2_000 tail 97_004..99_003 == W26 A
    # end + 1, B's +200 tail 40_251..40_450 == W26 B end + 1, no skip
    # on either side, 40k-segment continuation of the W26 B re-base
    # lineage). Machine-verified at prereg time
    # (results/_r539bma_w27_band_gate.py ADMIT receipt vs the 25-row
    # pre-W27 table incl. W23/W24/W25/W26 + SEED_REGISTRY values +
    # probe-seed cluster 95_000..95_003 r335 discovery leg + N2/N4
    # probe points + N2-W15 draft probe points + lfc/options actual
    # ranges + N3-R1 used-seed band 70_000..70_005, MSG-183x r529
    # mandatory leg). SIXTEENTH engine-owned wave. NOT a re-pick
    # (R250: W27 bands were never assigned; the measurement face has
    # no result to fish). W28+ WARNING: A +2_000 tail 99_004..101_003
    # and B +200 tail 40_451..40_650 projection per the r539 gate
    # receipt -- verify at W28 prereg (rotation slot W28=bm-b).
    27: {"a": (97_004, 99_003), "b_exit": (40_251, 40_450),
         "engine_owner": "bm-a"},
    # W28 (r523 bm-b, prereg-time extension per the W27 row's W28+
    # WARNING -- never-dry supply law standing step; sovereignty
    # rotation law F-20260901-01 slot W28=bm-b per the W27 row
    # verbatim, bm-b's EIGHTH owned wave after W10/W11/W13/W16/W19/
    # W22/W25; no pointer gate pending: W25 registered + burned 12/12
    # + FINALIZED by bm-b r522 (K=52,920, ledger 419,548 chain head),
    # W26 registered + burned 12/12 by bm-c r335 (finalize pending on
    # the bm-c seat), W27 registered by bm-a r539 (burn in progress on
    # bm-a) -- coexistence judged by band disjointness not commit
    # order, r531 law): BOTH tails arithmetic-clean exactly as the
    # W27 row projected (A's +2_000 tail 99_004..101_003 == W27 A
    # end + 1, B's +200 tail 40_451..40_650 == W27 B end + 1, no
    # skip on either side, 40k-segment continuation of the W26 B
    # re-base lineage). Machine-verified at prereg time
    # (results/_r523bmb_w28_band_gate.py ADMIT receipt vs the 26-row
    # pre-W28 table incl. W24/W25/W26/W27 + SEED_REGISTRY values +
    # probe-seed cluster 95_000..95_003 r335 discovery leg + N2/N4
    # probe points + N2-W15 draft probe points + lfc/options actual
    # ranges + N3-R1 used-seed band 70_000..70_005, MSG-183x r529
    # mandatory leg). SEVENTEENTH engine-owned wave. NOT a re-pick
    # (R250: W28 bands were never assigned; the measurement face has
    # no result to fish). W29+ WARNING: A +2_000 tail 101_004..103_003
    # and B +200 tail 40_651..40_850 projection per the r523 gate
    # receipt -- verify at W29 prereg (rotation slot W29=bm-c).
    # W29 (r336 bm-c, prereg-time extension per the W28 row's W29+
    # WARNING -- never-dry supply law standing step; sovereignty
    # rotation law F-20261001-01 slot W29=bm-c per the W28 row
    # verbatim, bm-c's SIXTH owned wave after W14/W17/W20/W23/W26;
    # no pointer gate pending: W26 registered + burned 12/12 +
    # FINALIZED by bm-c r336 (K=55,120, ledger 421,748 chain head),
    # W27 registered + burned 12/12 by bm-a r539 (finalize pending
    # on the bm-a seat, chain-unblocked by the W26 finalize), W28
    # registered by bm-b r523 (burn in progress on bm-b) --
    # coexistence judged by band disjointness not commit order,
    # r531 law): BOTH tails arithmetic-clean exactly as the W28
    # row projected (A's +2_000 tail 101_004..103_003 == W28 A
    # end + 1, B's +200 tail 40_651..40_850 == W28 B end + 1, no
    # skip on either side, 40k-segment continuation of the W26 B
    # re-base lineage). Machine-verified at prereg time
    # (results/_r336bmc_w29_band_gate.py ADMIT receipt vs the 27-row
    # pre-W29 table incl. W25/W26/W27/W28 + SEED_REGISTRY values +
    # probe-seed cluster 95_000..95_003 r335 discovery leg + N2/N4
    # probe points + N2-W15 draft probe points + lfc/options actual
    # ranges + N3-R1 used-seed band 70_000..70_005, MSG-183x r529
    # mandatory leg). EIGHTEENTH engine-owned wave. NOT a re-pick
    # (R250: W29 bands were never assigned; the measurement face has
    # no result to fish). W30+ WARNING: A +2_000 tail 103_004..105_003
    # and B +200 tail 40_851..41_050 projection per the r336 gate
    # receipt -- B tail EXPECTED REFUSAL (registry point 41_000
    # inside the arithmetic window, first-since-W26 forced-skip
    # candidate on the B side); verify at W30 prereg (rotation slot
    # W30=bm-a).
    29: {"a": (101_004, 103_003), "b_exit": (40_651, 40_850),
         "engine_owner": "bm-c"},    # W30 (r541 bm-a, prereg-time extension per the W28 row's W29+
    # WARNING -- never-dry supply law standing step; sovereignty
    # rotation law F-20260901-01 slot W30=bm-a per the W27=bm-a real
    # anchor: finalize landed bm-a r540, K=57,320, ledger 423,948
    # chain head; W28=bm-b / W29=bm-c seats continue the +3 rotation
    # -> W30=bm-a). W29 (bm-c seat) NOT registered at this freeze:
    # its published projection (A 101_004..103_003 / B 40_651..40_850,
    # the W28 row's W29+ WARNING naming the W29=bm-c rotation slot)
    # is a RESERVED FACE (r518: published projection = reserved face)
    # -- W30 skips past it. A side: first clean window 103_004..105_003
    # == W29 projected A tail + 1, no further skip. B side: the
    # arithmetic-from-W29-projection window 40_851..41_050 hits
    # SEED_REGISTRY p4_batch1=41_000 -> advance to 41_001..41_200
    # (W26 B re-base skip lineage, in-band point skip family).
    # Machine-verified at prereg time (results/_r541bma_w30_band_gate.py
    # ADMIT receipt vs the 26-row pre-W30 table incl. W25/W26/W27/W28
    # + SEED_REGISTRY values + probe-seed cluster 95_000..95_003 r335
    # discovery leg + N2/N4 probe points + N2-W15 draft probe points
    # + lfc/options actual ranges + N3-R1 used-seed band 70_000..70_005,
    # MSG-183x r529 mandatory leg + W29 published-projection reservation
    # leg). NINETEENTH engine-owned wave. NOT a re-pick (R250: W30 bands
    # were never assigned; the measurement face has no result to fish).
    # W31+ WARNING: A +2_000 tail 105_004..107_003 and B +200 tail
    # 41_201..41_400 projection per the r541 gate receipt -- verify at
    # W31 prereg (rotation slot W31=bm-b).
    28: {"a": (99_004, 101_003), "b_exit": (40_451, 40_650),
         "engine_owner": "bm-b"},
    30: {"a": (103_004, 105_003), "b_exit": (41_001, 41_200),
         "engine_owner": "bm-a"},
    # W31 (r525 bm-b, prereg-time extension per the W30 row's W31+
    # WARNING -- never-dry supply law standing step; sovereignty
    # rotation law F-20260901-01 slot W31=bm-b per the +3 rotation
    # from the W28=bm-b real anchor (finalize landed bm-b r524;
    # W29=bm-c SEATED AND FINALIZED mid-draft bm-c r337 -- K=61,720,
    # ledger 428,348 chain head; W30=bm-a frozen r541 burn in
    # flight -- registered in-use face). W29's published projection
    # (A 101_004..103_003 / B 40_651..40_850) was honored by the bm-c
    # freeze taking exactly that window (r337, r518 published=
    # reserved discharged). BOTH tails arithmetic-clean exactly as
    # the W30 row's W31+ WARNING projected (A 105_004..107_003 ==
    # W30 A end + 1, B 41_201..41_400 == W30 B end + 1, no skip
    # either side). Machine-verified at prereg time
    # (results/_r525bmb_w31_band_gate.py ADMIT receipt vs the 28-row
    # pre-W31 table incl. W25/W26/W27/W28/W29/W30 + SEED_REGISTRY
    # values + probe-seed cluster 95_000..95_003 r335 discovery leg
    # + N3-R1 used-seed band 70_000..70_005 MSG-183x r529 mandatory
    # leg). TWENTIETH engine-owned wave, bm-b's NINTH owned wave
    # after W10/W11/W13/W16/W19/W22/W25/W28. NOT a re-pick (R250:
    # W31 bands were never assigned; the measurement face has no
    # result to fish). W32+ WARNING: A +2_000 tail 107_004..109_003
    # and B +200 tail 41_401..41_600 projection per the r525 gate
    # receipt -- verify at W32 prereg (rotation slot W32=bm-c).
    # W32 (r339 bm-c, prereg-time extension per the W31 row's W32+
    # WARNING -- never-dry supply law standing step; sovereignty
    # rotation law F-20260901-01 slot W32=bm-c per the +3 rotation
    # from the W29=bm-c real anchor (finalize landed bm-c r337,
    # K=61,720; W30 finalize landed bm-a r542, K=63,920, ledger
    # 430,548; W31 finalize landed bm-b r525/r526 lineage, K=66,120,
    # ledger 432,748 chain head -- every pre-W32 seat closed at
    # this freeze). BOTH tails arithmetic-clean exactly as the W31
    # row's W32+ WARNING projected (A 107_004..109_003 == W31 A
    # end + 1, B 41_401..41_600 == W31 B end + 1, no skip either
    # side). Machine-verified at prereg time
    # (results/_r339bmc_w32_band_gate.py ADMIT receipt vs the 29-row
    # pre-W32 table incl. W29/W30/W31 + SEED_REGISTRY values +
    # probe-seed cluster 95_000..95_003 r335 discovery leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg).
    # TWENTY-FIRST engine-owned wave, bm-c's SEVENTH owned wave
    # after W14/W17/W20/W23/W26/W29. NOT a re-pick (R250: W32
    # bands were never assigned; the measurement face has no
    # result to fish). W33+ WARNING: A +2_000 tail 109_004..111_003
    # and B +200 tail 41_601..41_800 projection per the r339 gate
    # receipt -- verify at W33 prereg (rotation slot W33=bm-a).
    31: {"a": (105_004, 107_003), "b_exit": (41_201, 41_400),
         "engine_owner": "bm-b"},
    32: {"a": (107_004, 109_003), "b_exit": (41_401, 41_600),
         "engine_owner": "bm-c"},
    # W33 (r544 bm-a, prereg-time extension per the W32 row's W33+
    # WARNING -- never-dry supply law standing step; sovereignty
    # rotation law F-20260901-01 slot W33=bm-a per the +3 rotation
    # from the W30=bm-a real anchor (finalize landed bm-a r542,
    # K=63,920; W31 finalize landed bm-b r525, K=66,120, ledger
    # 432,748 chain head; W32 bm-c r339 registered + burned 12/12
    # on origin + ledger-appended -- its finalize sits pending at
    # the bm-c seat, consuming nothing this freeze touches; r543
    # seat discipline "W32 row landed then take over" discharged:
    # the W32 row IS landed; band-disjoint coexistence per r531
    # proven machine-side by this freeze's gate receipt). BOTH
    # tails arithmetic-clean exactly as the W32 row's W33+ WARNING
    # projected (A 109_004..111_003 == W32 A end + 1, B 41_601..
    # 41_800 == W32 B end + 1, no skip either side). Machine-
    # verified at prereg time (results/_r544bma_w33_band_gate.py
    # ADMIT receipt vs the 30-row pre-W33 table incl. W30/W31/W32
    # + SEED_REGISTRY values + probe-seed cluster 95_000..95_003
    # r335 discovery leg + N3-R1 used-seed band 70_000..70_005
    # MSG-183x r529 mandatory leg). TWENTY-SECOND engine-owned
    # wave, bm-a's SEVENTH owned wave after W12/W18/W21/W24/W27/
    # W30. NOT a re-pick (R250: W33 bands
    # were never assigned; the measurement face has no result to
    # fish). W34+ WARNING: A +2_000 tail 111_004..113_003 and B
    # +200 tail 41_801..42_000 projection per the r544 gate
    # receipt -- verify at W34 prereg (rotation slot W34=bm-b).
    33: {"a": (109_004, 111_003), "b_exit": (41_601, 41_800),
         "engine_owner": "bm-a"},
    # W34 (r527 bm-b, prereg-time extension per the W33 row's W34+
    # WARNING -- never-dry supply law standing step + O-20261001-2355
    # CEO de-throttle order (seat serialization ruled a law-sec.1
    # "never-dry" violation: every machine keeps its own continuous
    # series, waiting forbidden; sequential scientific constraints
    # may preserve finalize ORDER only -- order is not idleness).
    # Sovereignty rotation law F-20260901-01 slot W34=bm-b per the
    # +3 rotation from the W31=bm-b real anchor (finalize landed
    # bm-b r525, K=66,120; W33 finalize landed bm-a r544 same-window,
    # K=70,520, ledger 437,148 chain head -- W1..W33 ALL finalized
    # at this freeze, the chain fully caught up, zero pending
    # upstream face for the first time). BOTH tails arithmetic-clean
    # exactly as the W33 row's W34+ WARNING projected (A 111_004..
    # 113_003 == W33 A end + 1, B 41_801..42_000 == W33 B end + 1,
    # no skip either side). Machine-verified at prereg time
    # (results/_r527bmb_w34_band_gate.py ADMIT receipt vs the 31-row
    # pre-W34 table incl. W30/W31/W32/W33 + SEED_REGISTRY values +
    # probe-seed cluster 95_000..95_003 r335 discovery leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg; the
    # same-window pre-scan receipt results/_r527bmb_w34_pre_band_
    # gate.py is the leg-0 evidence base). TWENTY-THIRD engine-owned
    # wave, bm-b's TENTH owned wave after W10/W11/W13/W16/W19/W22/
    # W25/W28/W31. NOT a re-pick (R250: W34 bands were never
    # assigned; the measurement face has no result to fish).
    # W35+ WARNING: A +2_000 tail 113_004..115_003 and B +200 tail
    # 42_001..42_200 projection per the r527 gate receipt -- verify
    # at W35 prereg (rotation slot W35=bm-c).
    34: {"a": (111_004, 113_003), "b_exit": (41_801, 42_000),
         "engine_owner": "bm-b"},
    # W35 (r545 bm-a, engine de-throttle law O-20261001-2355 sec.2:
    # per-machine self-owned continuous series, zero-gap relay after the
    # machine's previous wave closes -- W33 finalize landed bm-a r544,
    # K=70,520, ledger 437,148 chain-linear). NOT a re-pick (R250: W35
    # bands were never assigned; the measurement face has no result to
    # fish). Wave number 35 = next free number after W34's published
    # claim (bm-b pre-scan ADMIT-READY receipt r527: A 111_004..113_003
    # / B 41_801..42_000, freeze pending at the bm-b seat under the new
    # de-throttle law -- published projection = reserved face per r518;
    # wave numbers are first-free-number allocation, no seat waiting).
    # Forced skip over the published W34 projection windows, machine-
    # proven by results/_r545bma_w35_band_gate.py refusal facts (the
    # skip is forced, not a free choice -- r518 execution face).
    # W36+ WARNING: A +2_000 tail 115_004..117_003 and B +200 tail
    # 42_201..42_400 projection per the r545 gate receipt -- verify at
    # W36 prereg (first-free-number law under O-2355 de-throttle).
    35: {"a": (113_004, 115_003), "b_exit": (42_001, 42_200),
         "engine_owner": "bm-a"},
    # W36 (r528 bm-b, engine de-throttle law O-20261001-2355 sec.2:
    # per-machine self-owned continuous series, zero-gap relay after
    # the machine's previous wave closes -- W34 closed FULL-LIFECYCLE
    # bm-b r528 same-window (freeze -> 12/12 burn -> finalize, K=72,720,
    # ledger net head 437,340). Wave number 36 = FIRST FREE NUMBER after
    # W35's landed claim (bm-a r545; seat system retired by the same
    # order). NOT a re-pick (R250: W36 bands were never assigned; the
    # measurement face has no result to fish). BOTH tails arithmetic-
    # clean exactly as the W35 row's W36+ WARNING projected
    # (A 115_004..117_003 == W35 A end + 1, B 42_201..42_400 == W35 B
    # end + 1, no skip either side). Machine-verified at prereg time
    # (results/_r528bmb_w36_band_gate.py ADMIT receipt vs the 33-row
    # pre-W36 table incl. W34/W35 + SEED_REGISTRY values + probe-seed
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed band
    # 70_000..70_005 MSG-183x r529 mandatory leg). TWENTY-FIFTH
    # engine-owned wave, bm-b's ELEVENTH owned wave after W10/W11/W13/
    # W16/W19/W22/W25/W28/W31/W34.
    # W37+ WARNING: A +2_000 tail 117_004..119_003 and B +200 tail
    # 42_401..42_600 projection per the r528 gate receipt -- verify at
    # W37 prereg (first-free-number law under O-2355 de-throttle).
    36: {"a": (115_004, 117_003), "b_exit": (42_201, 42_400),
         "engine_owner": "bm-b"},
    # W37 (r341 bm-c, own-series continuation per CEO de-throttle order
    # O-20261001-2355 sec.2 -- seat system TERMINATED: each machine
    # materializes its next wave the moment its previous closes, no
    # seat waiting. bm-c's EIGHTH owned wave after W14/W17/W20/W23/
    # W26/W29/W32; this freeze follows the r341 W36 yield (bm-b's W36
    # landed on origin 00:33:17 while this machine's identical W36
    # draft sat uncommitted from a crashed session -- r511 commit-order
    # yield, zero burn zero ledger zero loss). Wave 37 = first free
    # number: W35 (bm-a) and W36 (bm-b) both registered; BOTH tails
    # arithmetic continuation from the registered W36 row, no skip
    # either side (A 117_004..119_003 == W36 A end + 1; B 42_401..42_600
    # == W36 B end + 1). Machine-verified at prereg time
    # (results/_r341bmc_w37_band_gate.py ADMIT receipt vs the 34-row
    # pre-W37 table incl. W33/W34/W35/W36 + SEED_REGISTRY values +
    # probe-seed cluster 95_000..95_003 r335 discovery leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg).
    # TWENTY-SIXTH ENGINE-OWNED WAVE, engine_owner=bm-c
    # (SATURATION_ENGINE_LAW sec.1/2 same contract as W10..W36, local
    # queue, no pool entry). NOT a re-pick (R250: W37 bands were never
    # assigned; the measurement face has no result to fish).
    # W38+ WARNING: A +2_000 tail 119_004..121_003 and B +200 tail
    # 42_601..42_800 projection per the r341 gate receipt -- verify at
    # the next freeze's prereg (own-series: verify against the live
    # table tail + all published projections at that time).
    37: {"a": (117_004, 119_003), "b_exit": (42_401, 42_600),
         "engine_owner": "bm-c"},
    # W38 (r529 bm-b, own-series continuation per CEO de-throttle
    # order O-20261001-2355 sec.2 -- bm-b's TWELFTH owned wave after
    # W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/W36; follows the W36
    # FULL CLOSEOUT this same window (r529: finalize one-pass
    # 441,740, K=77,120 == sec.0 projection) -> zero-gap relay, wave
    # number 38 = first free number after W37's landed claim (bm-c
    # r341). BOTH tails arithmetic continuation from the registered
    # W37 row, no skip either side (A 119_004..121_003 == W37 A end
    # + 1; B 42_601..42_800 == W37 B end + 1). Machine-verified at
    # prereg time (results/_r529bmb_w38_band_gate.py ADMIT receipt vs
    # the 35-row pre-W38 table incl. W33/W34/W35/W36/W37 +
    # SEED_REGISTRY values + probe-seed cluster 95_000..95_003 r335
    # discovery leg + N3-R1 used-seed band 70_000..70_005 MSG-183x
    # r529 mandatory leg). TWENTY-SEVENTH ENGINE-OWNED WAVE,
    # engine_owner=bm-b (SATURATION_ENGINE_LAW sec.1/2 same contract
    # as W10..W37, local queue, no pool entry). NOT a re-pick (R250:
    # W38 bands were never assigned; the measurement face has no
    # result to fish).
    # W39+ WARNING: A +2_000 tail 121_004..123_003 and B +200 tail
    # 42_801..43_000 projection per the r529 gate receipt -- verify at
    # the next freeze's prereg (own-series: verify against the live
    # table tail + all published projections at that time).
    38: {"a": (119_004, 121_003), "b_exit": (42_601, 42_800),
         "engine_owner": "bm-b"},
    # W39 (r342 bm-c freeze): TWENTY-EIGHTH ENGINE-OWNED WAVE, engine_owner=
    # bm-c per O-20261001-2355 sec.2 own-continuous-series (zero-gap relay
    # after the W37 FULL CLOSEOUT same window r342: finalize one-pass K=
    # 79,320, ledger 443,940 chain-linear). A = arithmetic continuation
    # (the W38 row's W39+ WARNING projected CLEAN, machine-verified); B =
    # FORCED SKIP -- the arithmetic window 42_801..43_000 is REFUSED by
    # the SEED_REGISTRY point p4_folk=43_000 (tail point), first clean
    # window 43_001..43_200 machine-derived (r307 wave-band tail law).
    # NOT a re-pick (R250: W39 bands were never assigned).
    39: {"a": (121_004, 123_003), "b_exit": (43_001, 43_200),
         "engine_owner": "bm-c"},
    # W40 (r531 bm-b, own-series continuation per CEO de-throttle
    # order O-20261001-2355 sec.2 -- bm-b's THIRTEENTH owned wave after
    # W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/W36/W38; zero-gap relay
    # after the W38 FULL CLOSEOUT (r530: finalize one-pass K=81,520,
    # ledger head 446,140; W39 registered+burned by bm-c r342, finalize
    # pending on the bm-c lane) -> wave number 40 = FIRST FREE NUMBER
    # after bm-c's W39 landed claim. SIDES INDEPENDENTLY ADJUDICATED
    # per the W39 row's W40+ WARNING: A tail ARITHMETIC continuation
    # NO SKIP (123_004..125_003 == W39 A end + 1); B tail ARITHMETIC
    # continuation NO SKIP (43_201..43_400 == W39 B end + 1) -- both
    # sides projected CLEAN by the W39 row warning AND machine-derived
    # at this freeze (results/_r531bmb_w40_band_gate.py ADMIT receipt
    # vs the 37-row pre-W40 table incl. W35/W36/W37/W38/W39 + live
    # SEED_REGISTRY values + probe-seed cluster 95_000..95_003 r335
    # discovery leg + N3-R1 used-seed band 70_000..70_005 MSG-183x
    # r529 mandatory leg; origin slot vacancy machine-checked).
    # TWENTY-NINTH->THIRTIETH ENGINE-OWNED WAVE, engine_owner=bm-b
    # (SATURATION_ENGINE_LAW sec.1/2 same contract as W10..W39, local
    # queue, no pool entry). NOT a re-pick (R250: W40 bands were never
    # assigned; the measurement face has no result to fish).
    40: {"a": (123_004, 125_003), "b_exit": (43_201, 43_400),
         "engine_owner": "bm-b"},
    # W41 (r344 bm-c, own-series continuation per O-20261001-2355
    # sec.2 -- bm-c's TENTH owned wave; zero-gap relay after the W39
    # FULL CLOSEOUT (freeze r342 -> 12/12 no-restart burn -> finalize
    # r343 K=83,520... K=83,720 ledger 448,340; products delivered r344).
    # Wave 41 = first free number after bm-b's W40 landed claim (r531,
    # burn in flight at this freeze). SIDES INDEPENDENTLY ADJUDICATED
    # per the W40 row's W41+ WARNING: A tail arithmetic continuation
    # no skip (125_004..127_003 == W40 A end + 1); B tail arithmetic
    # continuation no skip (43_401..43_600 == W40 B end + 1).
    # Machine-verified at prereg time
    # (results/_r344bmc_w41_band_gate.py ADMIT receipt vs the 38-row
    # pre-W41 table + live SEED_REGISTRY values + probe-seed cluster
    # 95_000..95_003 r335 discovery leg + N3-R1 used-seed band
    # 70_000..70_005 MSG-183x r529 mandatory leg; origin slot vacancy
    # machine-checked). THIRTY-FIRST ENGINE-OWNED WAVE,
    # engine_owner=bm-c (local queue, no pool entry). NOT a re-pick
    # (R250: W41 bands never assigned).
    41: {"a": (125_004, 127_003), "b_exit": (43_401, 43_600),
         "engine_owner": "bm-c"},
    # W42 (r345 bm-c, own-series continuation per O-20261001-2355
    # sec.2 -- bm-c's ELEVENTH owned wave; zero-gap relay after the W41
    # FULL CLOSEOUT (freeze r344 -> 12/12 same-window burn -> finalize
    # r345 K=88,120, ledger 452,740 chain head; W40 restore incident
    # same-window healed 2fa252cc1). Wave 42 = first free number after
    # W41's landed claim. SIDES INDEPENDENTLY ADJUDICATED per the W41
    # row's W42+ WARNING: A tail arithmetic continuation no skip
    # (127_004..129_003 == W41 A end + 1); B tail arithmetic
    # continuation no skip (43_601..43_800 == W41 B end + 1).
    # Machine-verified at prereg time (results/_r345bmc_w42_band_gate.py
    # ADMIT receipt vs the 39-row pre-W42 table + live SEED_REGISTRY
    # values + probe-seed cluster 95_000..95_003 r335 discovery leg +
    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;
    # origin slot vacancy machine-checked). THIRTY-SECOND ENGINE-OWNED
    # WAVE, engine_owner=bm-c (local queue, no pool entry). NOT a
    # re-pick (R250: W42 bands never assigned).
    42: {"a": (127_004, 129_003), "b_exit": (43_601, 43_800),
         "engine_owner": "bm-c"},
    # W43 (r346 bm-c): A tail arithmetic continuation no skip; B =
    # machine-derived first clean window past the REFUSED arithmetic
    # 43_801..44_000 (SEED_REGISTRY p4_queue=44_000 tail point, W42
    # row W43+ WARNING, W39-B skip family). THIRTY-THIRD ENGINE-OWNED
    # WAVE, engine_owner=bm-c (local queue, no pool entry). NOT a
    # re-pick (R250: W43 bands never assigned; B skip forced).
    43: {"a": (129_004, 131_003), "b_exit": (44_001, 44_200),
         "engine_owner": "bm-c"},
    # W44 (r553 bm-a, own-series continuation per O-20261001-2355
    # sec.2 -- bm-a's NINTH owned wave after W12/W18/W21/W24/W27/
    # W30/W33/W35; the W40 cross-burn attempt yielded canon to bm-b
    # r531, not owned). Zero-gap relay after the W43 FULL CLOSEOUT
    # (bm-c r346 same-window three-stage: freeze b3411b7c9 ->
    # 12/12 burn -> finalize one-pass K=92,520, ledger 457,140 chain
    # head). Wave 44 = first free number after W43's landed claim.
    # BOTH SIDES no-skip arithmetic continuations per the W43 row's
    # W44+ WARNING projections, machine-derived at this freeze (r535
    # law: clean-projection claims must be machine-derived, never
    # prose-copied): A = 131_004..133_003 == W43 A end + 1; B =
    # 44_201..44_400 == W43 B end + 1. Machine-verified at prereg
    # time (results/_r553bma_w44_band_gate.py ADMIT receipt vs the
    # 41-row pre-W44 table + live SEED_REGISTRY values + probe-seed
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). THIRTY-FOURTH ENGINE-OWNED WAVE,
    # engine_owner=bm-a (local queue, no pool entry). NOT a re-pick
    # (R250: W44 bands never assigned).
    44: {"a": (131_004, 133_003), "b_exit": (44_201, 44_400),
         "engine_owner": "bm-a"},
    # W45 (r554 bm-a, own-series continuation per O-20261001-2355
    # sec.2 -- bm-a's TENTH owned wave after W12/W18/W21/W24/W27/
    # W30/W33/W35/W44; zero-gap relay after the W44 FULL CLOSEOUT:
    # r553 freeze -> 12/12 burn -> r554 finalize one-pass K=94,720,
    # ledger 459,340 chain head, chain FULLY caught up W1..W44).
    # Wave 45 = first free number after W44's landed claim. BOTH
    # SIDES no-skip arithmetic continuations per the W44 row's W45+
    # WARNING projections, machine-derived at this freeze (r535 law:
    # clean-projection claims must be machine-derived, never
    # prose-copied): A = 133_004..135_003 == W44 A end + 1; B =
    # 44_401..44_600 == W44 B end + 1. Machine-verified at prereg
    # time (results/_r554bma_w45_band_gate.py ADMIT receipt vs the
    # 42-row pre-W45 table + live SEED_REGISTRY values + probe-seed
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). THIRTY-FIFTH ENGINE-OWNED WAVE,
    # engine_owner=bm-a (local queue, no pool entry). NOT a re-pick
    # (R250: W45 bands never assigned).
    45: {"a": (133_004, 135_003), "b_exit": (44_401, 44_600),
         "engine_owner": "bm-a"},
    # W46 (r348 bm-c, own-series continuation per O-20261001-2355
    # sec.2 -- bm-c's FOURTEENTH owned wave after W14/W17/W20/W23/W26/
    # W29/W32/W37/W39/W41/W42/W43; the W44 same-number draft YIELDED
    # to bm-a's r553 canonical freeze -- identical bands, r530
    # deterministic law, r511 commit-order yield). Zero-gap relay
    # after the W43 FULL CLOSEOUT (bm-c r346 same-window: freeze
    # b3411b7c9 -> 12/12 no-restart burn -> finalize one-pass
    # K=92,520, ledger 457,140). UPSTREAM W45 (bm-a r554 freeze
    # 03:59:59) IN FLIGHT at this freeze: burn on the bm-a tick
    # engine, finalize pending; W46 finalize chain-order is
    # FAIL-CLOSED on the W45 output at run time (W7/W10/W12 in-flight
    # dep precedent, r307 two-state law). Wave 46 = first free number
    # after W45's landed claim (slot 46 vacant on origin,
    # machine-checked at the gate leg3 + the vacancy tool). BOTH
    # SIDES no-skip arithmetic continuations per the W45 row's W46+
    # WARNING projections, machine-derived at this freeze (r535
    # law: clean-projection claims must be machine-derived, never
    # prose-copied): A = 135_004..137_003 == W45 A end + 1; B =
    # 44_601..44_800 == W45 B end + 1. Machine-verified at prereg
    # time (results/_r348bmc_w46_band_gate.py ADMIT receipt vs the
    # 43-row pre-W46 table + live SEED_REGISTRY values + probe-seed
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed band
    # 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). THIRTY-SIXTH ENGINE-OWNED WAVE,
    # engine_owner=bm-c (local queue, no pool entry). NOT a re-pick
    # (R250: W46 bands were never assigned).
    46: {"a": (135_004, 137_003), "b_exit": (44_601, 44_800),
         "engine_owner": "bm-c"},
    # W47 (r534 bm-b, own-series continuation per O-20261001-2355
    # sec.2 -- bm-b's FOURTEENTH owned wave after W10/W11/W13/W16/
    # W19/W22/W25/W28/W31/W34/W36/W38/W40; the dead r533 session's
    # W42/W44 same-number drafts YIELDED to bm-c r345 / bm-a r553
    # canonical freezes -- identical bands, r530 deterministic law,
    # r511 commit-order yield). Zero-gap relay after the W40 FULL
    # CLOSEOUT (bm-b r532) + fleet chain catch-up: W45 (bm-a r554)
    # and W46 (bm-c r348 same-window full-lifecycle K=99,120, ledger
    # 465,748) BOTH FINALIZED before this freeze -- ZERO in-flight
    # upstream faces at this freeze (first fully caught-up window).
    # Wave 47 = first free number after W46's landed claim (slot 47
    # vacant on origin, machine-checked at the gate leg3). A side =
    # no-skip arithmetic continuation per the W46 row's W47+ WARNING
    # projection (137_004..139_003, machine-derived at this freeze,
    # r535 law); B side = FORCED SKIP past SEED_REGISTRY
    # pc_l2_ic=45_000 (arithmetic window 44_801..45_000 REFUSED,
    # refusal facts machine-verified -- W26-A/W39-B/W43-B skip
    # family), scan-forward first clean window 45_001..45_200.
    # Machine-verified at prereg time
    # (results/_r534bmb_w47_band_gate.py ADMIT receipt vs the 44-row
    # pre-W47 table + live SEED_REGISTRY values + probe-seed cluster
    # 95_000..95_003 r335 discovery leg + N3-R1 used-seed band
    # 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). THIRTY-SEVENTH ENGINE-OWNED WAVE,
    # engine_owner=bm-b (local queue, no pool entry). NOT a re-pick
    # (R250: W47 bands were never assigned).
    47: {"a": (137_004, 139_003), "b_exit": (45_001, 45_200),
         "engine_owner": "bm-b"},
    # W48 (r557 bm-a, own-series continuation per O-20261001-2355
    # sec.2 -- bm-a's ELEVENTH owned wave after W12/W18/W21/W24/W27/
    # W30/W33/W35/W44/W45; the dead r555 session's W46/W47 same-number
    # drafts YIELDED to bm-c r348 / bm-b r534 canonical freezes,
    # r530/r511 laws). Zero-gap relay: W45 (bm-a r554 K=96,920 ledger
    # 463,548), W46 (bm-c r348 same-window full-lifecycle K=99,120
    # ledger 465,748) and W47 (bm-b r556 same-window finalize K=101,320
    # ledger 467,948) ALL FINALIZED before this freeze lands -- the
    # chain FULLY caught up, zero in-flight upstream faces (W47
    # landed same-window at this freeze window; the pre-rebase draft
    # noted it in-flight, updated here post-rebase per r518
    # origin-timing law). Wave 48 = first free number per the r555
    # yield receipt's published bm-a W48 claim (bm-b r556 honored it
    # and skipped to W49 -- published=reserved r518-1 law); origin
    # slot vacancy machine-checked. BOTH SIDES = no-skip arithmetic
    # continuations per the W47 row's W48+ WARNING projections
    # (A 139_004..141_003 / B 45_201..45_400), machine-derived at
    # this freeze (r535 law: clean-projection claims must be
    # machine-derived, never prose-copied). Machine-verified at
    # prereg time (results/_r557bma_w48_band_gate.py ADMIT receipt
    # vs the 46-row table incl. W49 + live SEED_REGISTRY values +
    # probe-seed cluster 95_000..95_003 r335 discovery leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;
    # origin slot vacancy machine-checked). THIRTY-EIGHTH
    # ENGINE-OWNED WAVE, engine_owner=bm-a (local queue, no pool
    # entry). NOT a re-pick (R250: W48 bands were never assigned).
    48: {"a": (139_004, 141_003), "b_exit": (45_201, 45_400),
         "engine_owner": "bm-a"},
    # THIRTY-EIGHTH ENGINE-OWNED WAVE (r556 bm-b freeze): bm-b's
    # FIFTEENTH owned wave after W10/W11/W13/W16/W19/W22/W25/W28/W31/
    # W34/W36/W38/W40/W47. Wave 49 = next free number SKIPPING the
    # W48 slot (bm-a declared W48 as their next own wave in the r555
    # W47-yield receipt; published number intent honored per the
    # W19/W18 precedent -- wave numbers need not be contiguous, r516
    # derive law). BOTH SIDES = FORCED SKIP past the W48 PUBLISHED
    # PROJECTION (r518 ① published=reserved law, W19-A/B re-base
    # family): the W47 row's W48+ WARNING projects A 139_004..141_003
    # / B 45_201..45_400 (machine-derived by the r534 gate's W48+
    # projection legs, CLEAN vs points -- the reservation is the
    # published face itself, not a point hit). bm-b's W49 A-side
    # arithmetic position (139_004..141_003 = W47 A end + 1) and
    # B-side arithmetic position (45_201..45_400 = W47 B end + 1)
    # BOTH REFUSED by the published-projection reserved face ->
    # scan-forward first clean windows 141_004..143_003 /
    # 45_401..45_600. Skip is FORCED, not a free pick (R250: W49
    # bands were never assigned). Machine-verified at prereg time
    # (results/_r556bmb_w49_band_gate.py ADMIT receipt vs the 46-row
    # pre-W49 table + live SEED_REGISTRY values + probe-seed cluster
    # 95_000..95_003 r335 discovery leg + N3-R1 used-seed band
    # 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). W47 finalized BEFORE this freeze
    # (bm-b r556 same-window: K=101,320, ledger 467,948); W48 not
    # registered at this freeze (unregistered-gap honest note per
    # the W19/W18 precedent -- the finalize merge loop derives the
    # wave set from registry keys at run time and stays FAIL-CLOSED
    # on any not-yet-finalized upstream seat, r307 two-state law).
    # [r557 bm-a rebase disclosure: W48 registered by this same
    # merged commit -- W49 is thereby the THIRTY-NINTH engine wave
    # in landed order; the r556 freeze-time prose above is the
    # historical fact at its freeze window, kept verbatim per the
    # r531 minimal-disclosure law; registry derives from keys, zero
    # code impact.]
    49: {"a": (141_004, 143_003), "b_exit": (45_401, 45_600),
         "engine_owner": "bm-b"},
    # THIRTY-NINTH ENGINE-OWNED WAVE (r350 bm-c freeze): bm-c's
    # FOURTEENTH owned wave after W14/W17/W20/W23/W26/W29/W32/W37/
    # W39/W41/W42/W43/W46. Wave 50 = next free number after the
    # registered W49 row (W48 = bm-a-declared slot in the r555
    # W47-yield receipt, still UNREGISTERED at this freeze --
    # W19/W18 non-contiguity precedent, r516 derive law). BOTH
    # SIDES = ARITHMETIC CONTINUATION from the W49 row tail, no
    # skip: A 143_004..145_003 (= W49 A end 143_003 + 1) and
    # B 45_601..45_800 (= W49 B end 45_600 + 1) -- both windows
    # CLEAN vs the full reserved universe (46 registered rows +
    # the W48 PUBLISHED PROJECTION bands A 139_004..141_003 /
    # B 45_201..45_400 reserved per r518-①, N3-R1 used-seed band
    # 70_000..70_005, probe-seed cluster 95_000..95_003, live
    # SEED_REGISTRY values, probe/actual draw ranges; ADMIT
    # receipt results/_r350bmc_w50_band_gate.py, origin slot
    # vacancy machine-checked). NOT a re-pick (R250: W50 bands
    # were never assigned). W47 finalized BEFORE this freeze
    # (bm-b r556 same-window K=101,320, ledger 467,948); W49
    # registered by bm-b r556 with its finalize NOT landed at
    # this freeze (in-flight upstream honest note -- the finalize
    # merge loop derives the wave set from registry keys at run
    # time and stays FAIL-CLOSED on any not-yet-finalized
    # upstream seat, r307 two-state law).
    50: {"a": (143_004, 145_003), "b_exit": (45_601, 45_800),
         "engine_owner": "bm-c"},
    # FOURTIETH ENGINE-OWNED WAVE (r350 bm-c freeze): bm-c's FIFTEENTH
    # owned wave. Wave 51 = next free number after the registered W50
    # row (zero-gap relay in the bm-c own-series under the de-throttle
    # law; W48/W49/W50 all registered, their finalizes chain-ordered).
    # A = ARITHMETIC CONTINUATION from the W50 row tail, no skip
    # (145_004..147_003 = W50 A end + 1, CLEAN machine-derived).
    # B = FORCED SKIP past SEED_REGISTRY xlib_synth_null_a=46_000
    # (arithmetic window 45_801..46_000 REFUSED at its tail point per
    # the W50 row W51+ WARNING; first clean window 46_001..46_200
    # machine-derived, W26-A/W39-B/W43-B skip family). NOT a re-pick
    # (R250: W51 bands were never assigned). Machine-verified at
    # prereg time (results/_r350bmc_w51_band_gate.py ADMIT receipt vs
    # the 47-row pre-W51 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed band
    # 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked).
    51: {"a": (145_004, 147_003), "b_exit": (46_001, 46_200),
         "engine_owner": "bm-c"},
    # FORTY-FIRST ENGINE-OWNED WAVE (r351 bm-c freeze): bm-c's
    # SIXTEENTH owned wave. Wave 52 = next free number after the
    # registered W51 row (zero-gap relay in the bm-c own-series under
    # the de-throttle law; W48 re-derive + W50/W51 finalizes
    # chain-ordered and pending, coexist by band disjointness per
    # r531). BOTH SIDES = ARITHMETIC CONTINUATION from the W51 row
    # tail, no skip: A 147_004..149_003 (= W51 A end 147_003 + 1) and
    # B 46_201..46_400 (= W51 B end 46_200 + 1) -- both windows CLEAN
    # per the W51 row W52+ WARNING projections, machine-derived at
    # this freeze (r535 law: clean-projection claims must be
    # machine-derived, never prose-copied). Machine-verified at
    # prereg time (results/_r351bmc_w52_band_gate.py ADMIT receipt vs
    # the 48-row pre-W52 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed band
    # 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). NOT a re-pick (R250: W52 bands were
    # never assigned).
    52: {"a": (147_004, 149_003), "b_exit": (46_201, 46_400),
         "engine_owner": "bm-c"},
}
# v1 + ext(wave-1) in-use bands (source of truth: those runners' constants)
V1_IN_USE = set(range(10_000, 10_100)) | set(range(20_000, 20_020))
EXT_W1_IN_USE = set(range(10_100, 12_100)) | set(range(20_100, 20_300))

# --- face registry (law sec.2; runner=None = not landed, never materialized) ---
FACES = [
    {"id": "N1", "name": "nulls-deepening", "priority": 1,
     "runner": "scripts/perpetual_faces_n1.py",
     "runner_args": ["run"],  # per-shard args appended at materialization
     "wave": 2, "prereg_ref": "research/PERPETUAL_N1_W2_PREREG.md",
     # per-shard materializer pattern landed r490 (runner v0.3 --wave):
     # supply() expands the next law sec.4 wave into 12 per-shard entries
     # when the 3-leg trigger fires; per-wave prereg presence is the gate
     "supply_ready": True},
    {"id": "N3", "name": "neighborhood-robustness", "priority": 2,
     "runner": "scripts/perpetual_faces_n3.py",
     "runner_args": ["run", "--member"],   # member id appended per shard
     "wave": 1, "prereg_ref": "research/PERPETUAL_N3_R1_PREREG.md",
     # runner landed r509 bm-a (selftest 7/7 + real-data anchor probe 6/6
     # + one write-path shard smoke per r506 real-run law) -- per-shard
     # materializer pattern lands same window per freeze-signature
     # sequencing; member list + entry ids single-sourced from the runner
     "supply_ready": True},
    {"id": "N2", "name": "random-subspace-furnace", "priority": 3, "runner": None,
     "runner_args": None, "wave": 15, "prereg_ref": None},
    {"id": "N4", "name": "bootstrap-alt-history", "priority": 4, "runner": None,
     "runner_args": None, "wave": 1, "prereg_ref": None},
]


def _load_pool():
    """Parse runnable_pool.json; tolerate missing file as empty pool."""
    if not os.path.exists(POOL_PATH):
        return {"entries": {}}
    with open(POOL_PATH, encoding="utf-8") as f:
        return json.load(f)


def _pool_live_count(pool):
    """Live = claimable/pending supply. park_note'd entries are deliberate
    governance holds (r304 park_note marker law / r504 authority law),
    not supply: their unfreeze is gated on canon self-proof or a GM
    ruling and the picker never claims a 'waiting' entry -- counting
    them as live deadlocks the never-dry law behind a parked entry
    forever (live case r497: W14 re-park N=0 held live=1 while every
    burnable face was done and the pool was truly starved)."""
    entries = pool.get("entries", [])
    vals = entries.values() if isinstance(entries, dict) else entries
    n = 0
    for e in vals:
        if str(e.get("status", "")) not in ("ready", "waiting", "running"):
            continue
        if e.get("park_note"):
            continue
        if not _claimable(e):
            continue
        n += 1
    return n


def _claimable(e):
    """True when the entry still has burnable work. An entry whose every
    shard is done is burn-complete regardless of its entry.status -- the
    daemon harvest only lands the shard layer (r488 presence=done
    semantics) and the entry-layer done flip belongs to the observing
    round (r180 dual-flip), so a closed wave awaiting its entry flip is
    a ghost face, not supply. Counting ghosts as live deadlocks the
    never-dry law behind a finished wave forever (live case r309: 12
    finalized W5 entries entry=ready blocked the W6 supply trigger while
    every burnable face was done)."""
    shards = e.get("shards") or []
    if shards and all(str(s.get("status", "")) == "done" for s in shards):
        return False
    return True


def _py_face():
    """Lane machine py CPU pct from its autofill state last_tick; None if unknown."""
    try:
        p = os.path.join(PATHS.root, "fleet", "machine.json")
        with open(p, encoding="utf-8") as f:
            mid = json.load(f).get("machine_id")
        p = os.path.join(PATHS.results_dir, f"autofill_state.{mid}.json")
        if not os.path.exists(p):
            return None
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        return float(d.get("last_tick", {}).get("py_cpu_pct"))
    except Exception:
        return None


def _trigger():
    pool = _load_pool()
    live = _pool_live_count(pool)
    starving = live == 0
    py = _py_face()
    py_ok = True if py is None else py < 70.0
    return pool, live, starving, py, py_ok


def _load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"version": 1, "law_ref": LAW_REF, "waves": [], "last_supply": None}


def _write_state(st):
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE_PATH)


def _expand_wave_entries(face, wave, ts):
    """Per-shard materializer (law sec.1): expand one wave into 12 pool
    entries -- the W2 registration face verbatim (one entry per shard,
    runner carries the wave, checkpoint=presence=done contract, unclaimed
    shard faces). Pure function: no pool/state writes (selftest exercises
    it hermetically)."""
    bands = N1_BANDS[wave]
    entries = []
    for i in range(12):
        entries.append({
            "id": f"PERPETUAL-N1-W{wave}-SHARD-{i}",
            "ticket_ref": "T-2026-09-30-133 s2 (O-2026-09-30-2340)",
            "prereg_ref": (f"research/PERPETUAL_N1_W{wave}_PREREG.md "
                           f"(frozen pre-run; law sec.4 W{wave} bands "
                           f"A {bands['a'][0]}+ / B-exit {bands['b_exit'][0]}+)"),
            "consumer_plan": ("science_gates null-pool deepening: merged "
                              "pool (law sec.5 cumulative) -> skill_line_v2 "
                              "K-lift + p95/p99 face (G1 prime skill line "
                              "consumer)"),
            "runner": "scripts/perpetual_faces_n1.py",
            "runner_args": ["run", "--shard", str(i), "--of", "12",
                            "--wave", str(wave)],
            "lane_owner": "ANY",
            "priority": 1,
            "status": "ready",
            "entered_at": ts,
            "worker_class": "self-contained",
            "data_gates": ("in-runner FAIL-CLOSED: universe==48 bare codes "
                           "+ panel end==2026-09-22 same-window + law sec.4 "
                           "seed bands (selftest-enforced) + determinism "
                           "byte-equal rerun"),
            "shards": [{
                "key": f"n1w{wave}-{i}of12",
                "status": "ready",
                "checkpoint": (f"results/p2cal_ext/n1_w{wave}/"
                              f"shard-{i}-of-12.json (presence=done; "
                              f"deterministic rerun byte-equal)"),
                "note": (f"N1-W{wave} wave shard {i} of 12 "
                         f"(A2000+B200 contiguous slice); ~2min serial burn"),
            }],
            "workers_plan": {
                "workers": 8, "priority": "BelowNormal",
                "workers_law": ("ProcessPoolExecutor code-backed, "
                                "O-20260930-2355 multicore law (serial-vs-"
                                "pool byte-equal parity proven on W2); "
                                "BLAS 1/worker cap; --workers override"),
            },
        })
    return entries


def _expand_n3_r1_entries(ts):
    """N3-R1 materializer (law sec.1): expand the wave into 6 per-member
    pool entries. Member list + entry ids are single-sourced from the
    runner module (import face -- pool ids and the runner's pool_claims
    handshake can never drift apart). Pure function: no writes."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import perpetual_faces_n3 as n3   # single-source member/entry face
    entries = []
    for m in n3.load_members():
        mid = m["id"]
        spec = n3.FAMILIES[mid]
        n_cells = 2 + 2 * len(spec["oat"])
        entries.append({
            "id": n3.pool_entry_id(mid),
            "ticket_ref": "T-2026-09-30-133 s2 (O-2026-09-30-2340; "
                          "N3 face wave-1 per canon drafting order "
                          "N1-W2 -> N3-R1)",
            "prereg_ref": "research/PERPETUAL_N3_R1_PREREG.md "
                          "(frozen pre-run; seed band perpetual_n3_r1 "
                          "= 70_000+member_idx registered in "
                          "SEED_REGISTRY pre-freeze)",
            "consumer_plan": ("G2 evidence-supply deepening: per-member "
                              "packs (neighborhood/cost_x3/per_year/"
                              "bootstrap_ci/current-line recheck/"
                              "g2_registration_v2) -> finalize merge "
                              "results/perpetual_faces/n3_r1_results.json "
                              "+ ledger +28; measurement face, no "
                              "registration claim"),
            "runner": "scripts/perpetual_faces_n3.py",
            "runner_args": ["run", "--member", mid],
            "lane_owner": "ANY",
            "priority": 1,
            "status": "ready",
            "entered_at": ts,
            "worker_class": "self-contained",
            "data_gates": ("in-runner FAIL-CLOSED: universe==48 bare codes "
                           "+ panel end==2026-09-22 same-window + anchor "
                           "gate vs member-file recorded evidence "
                           "(tol 0.002, trades exact) + determinism "
                           "byte-equal rerun (JSONL checkpoint "
                           "presence=done)"),
            "shards": [{
                "key": mid,
                "status": "ready",
                "checkpoint": (f"results/perpetual_faces/n3_r1/cells-{mid}"
                               f".jsonl (presence=done; deterministic rerun "
                               f"byte-equal)"),
                "note": (f"N3-R1 member shard {mid}: {n_cells} engine "
                         f"cells (center anchor + x3 + "
                         f"{2 * len(spec['oat'])} OAT nbhd); "
                         f"~40-80s single-core light burn"),
            }],
            "workers_plan": {
                "workers": 1, "priority": "BelowNormal",
                "workers_law": ("light batch honest single-core (per-cell "
                                "engine run ~5-10s; no multicore shell "
                                "for a <5min shard)"),
            },
        })
    return entries


def _pool_format_probe():
    """r289 format law: probe the pool file's indent + EOL + trailing-NL
    face before any rewrite (bare json.dump defaults = whole-file diff).
    Missing file -> the canonical producer face (indent 2, CRLF)."""
    indent, crlf, trailing_nl = 2, True, False
    if os.path.exists(POOL_PATH):
        b = open(POOL_PATH, "rb").read()
        nl = b.count(b"\n")
        crlf = b.count(b"\r\n") >= max(1, nl) // 2
        trailing_nl = b.endswith(b"\n")
        for line in b.decode("utf-8", errors="replace").split("\n"):
            s = line.strip()
            if s.startswith('"'):
                indent = len(line) - len(line.lstrip(" "))
                break
    return indent, crlf, trailing_nl


def _pool_write_mirror(pool):
    """Atomic pool write mirroring the probed producer format (single-writer
    lane law; the tmp+replace face is the established producer pattern)."""
    indent, crlf, trailing_nl = _pool_format_probe()
    s = json.dumps(pool, ensure_ascii=False, indent=indent)
    if crlf:
        s = s.replace("\n", "\r\n")
    if trailing_nl and not s.endswith("\n"):
        s += "\r\n" if crlf else "\n"
    tmp = POOL_PATH + ".tmp"
    with open(tmp, "wb") as f:
        f.write(s.encode("utf-8"))
    os.replace(tmp, POOL_PATH)


def cmd_status():
    pool, live, starving, py, py_ok = _trigger()
    pending = [f["id"] for f in sorted(FACES, key=lambda x: x["priority"]) if not f["runner"]]
    landed = [f["id"] for f in FACES if f["runner"]]
    blocked = [f["id"] for f in FACES
               if f["runner"] and not f.get("supply_ready", True)]
    print(f"pool live entries: {live} (starving={starving})")
    print(f"lane py_cpu face: {py} (py_ok={py_ok})")
    print(f"faces runner-landed: {landed or 'NONE'}")
    if blocked:
        print(f"supply-blocked (per-shard materializer pending, honest): {blocked}")
    print(f"faces pending (honest, never materialized): {pending}")
    st = _load_state()
    w = len(st.get("waves", []))
    print(f"materialized waves to date: {w}")
    if starving and pending and not landed:
        print("VERDICT: supply_floor=true pool_starved=true "
              "faces_pending=%s -- runner landing is the remediation lane "
              "(law freeze-signature sequencing)" % ",".join(pending))
    elif starving:
        print("VERDICT: pool_starved=true supply runnable via landed faces")
    else:
        print("VERDICT: pool has live supply; no action")
    return 0


def cmd_supply():
    pool, live, starving, py, py_ok = _trigger()
    st = _load_state()
    st["flags"] = {
        "pool_starved": bool(starving),
        "supply_floor": bool(starving and not any(f["runner"] for f in FACES)),
        "generated_at": sg._now() if hasattr(sg, "_now") else None,
    }
    st["last_supply"] = {
        "live": live, "starving": bool(starving), "py": py, "py_ok": py_ok,
        "faces_pending": [f["id"] for f in FACES if not f["runner"]],
    }
    if not (starving and py_ok):
        st["flags"]["supply_floor"] = False
        _write_state(st)
        print(f"supply: no trigger (live={live} py={py}) -- flags updated")
        return 0
    landed = [f for f in sorted(FACES, key=lambda x: x["priority"])
              if f["runner"] and f.get("supply_ready", True)]
    blocked = [f["id"] for f in FACES
               if f["runner"] and not f.get("supply_ready", True)]
    if blocked:
        st["last_supply"]["supply_blocked"] = blocked
    if not landed:
        _write_state(st)
        if blocked:
            print(f"supply: trigger MET but runner-landed faces awaiting the "
                  f"per-shard materializer pattern ({','.join(blocked)}) -- "
                  f"honest no-op, flags written; first wave materialized via "
                  f"autofill submit per law sequencing line")
        else:
            print("supply: trigger MET but no face runner landed -- honest no-op, "
                  "flags written (pool_starved/supply_floor) for s3 wiring; "
                  "N1-W2 runner is the next law-sequenced deliverable")
        return 0
    ts = sg._now() if hasattr(sg, "_now") else None
    vals = list(pool.get("entries", []))
    if isinstance(pool.get("entries"), dict):
        vals = list(pool["entries"].values())
    # face dispatch in priority order (law sec.1 N1>N3>N2>N4) with
    # per-face wave gates; a face gated by its own wave state (bands /
    # per-wave prereg / same-face in-flight) falls through to the next
    # landed face -- canon sequencing (N1-W2 -> N3-R1 -> N2-W15 -> N4-B1)
    # is honored by the gates, not by hardcoding one face.
    chosen = None            # (face_id, payload)
    for face in landed:
        fid = face["id"]
        # law sec.1 leg-3: no same-face in-flight wave (live =
        # ready/waiting/running; park_note'd entries are deliberate
        # holds, not in-flight supply -- same r304/r504 marker law)
        live = [e for e in vals
                if str(e.get("id", "")).startswith(f"PERPETUAL-{fid}-")
                and str(e.get("status", "")) in ("ready", "waiting",
                                                "running")
                and not e.get("park_note")
                and _claimable(e)]
        if live:
            st["last_supply"]["awaiting"] = (f"{fid} wave in flight "
                                             f"({len(live)} live entries)")
            continue
        if fid == "N1":
            # next wave from pool entry truth (materialization ledger of
            # record; generator-local state waves[] is not the
            # cross-machine truth face)
            waves_seen = []
            for e in vals:
                eid = str(e.get("id", ""))
                if eid.startswith("PERPETUAL-N1-W") and "-SHARD-" in eid:
                    try:
                        waves_seen.append(int(
                            eid.split("PERPETUAL-N1-W")[1]
                               .split("-SHARD-")[0]))
                    except (IndexError, ValueError):
                        pass
            wave = (max(waves_seen) + 1) if waves_seen else face["wave"]
            if wave not in N1_BANDS:
                st["last_supply"]["awaiting"] = \
                    f"law sec.4 bands for W{wave}"
                continue
            # SATURATION_ENGINE_LAW sec.1 (T-2026-10-01-141 s1):
            # engine-owned waves burn in the owning machine's local
            # perpetual queue and NEVER enter the pool -- materializing
            # them here would double-burn against the engine (r297
            # family). Honest refusal, face falls through.
            owner = N1_BANDS[wave].get("engine_owner")
            if owner:
                st["last_supply"]["awaiting"] = \
                    f"W{wave} engine-owned by {owner} (local queue burn)"
                continue
            prereg_rel = f"research/PERPETUAL_N1_W{wave}_PREREG.md"
            if not os.path.exists(os.path.join(PATHS.root, prereg_rel)):
                st["last_supply"]["awaiting"] = f"frozen prereg for W{wave}"
                continue
            chosen = (fid, wave)
            break
        if fid == "N3":
            if not os.path.exists(os.path.join(PATHS.root,
                                               face["prereg_ref"])):
                st["last_supply"]["awaiting"] = "frozen prereg for N3-R1"
                continue
            chosen = (fid, None)
            break
        # N2/N4: runner not landed yet -> honest fall-through
        st["last_supply"]["awaiting"] = f"{fid} runner not landed"
    if chosen is None:
        _write_state(st)
        print(f"supply: trigger MET but every landed face is gated "
              f"({st['last_supply'].get('awaiting')}) -- honest no-op")
        return 0
    face_id, wave = chosen
    if face_id == "N1":
        new_entries = _expand_wave_entries(face, wave, ts)
        bands_rec = N1_BANDS.get(wave)
        id_msg = f"PERPETUAL-N1-W{wave}-SHARD-0..11"
        wave_no = wave
    else:
        new_entries = _expand_n3_r1_entries(ts)
        bands_rec = {"seed_base": 70_000, "band": "70_000+member_idx"}
        id_msg = "PERPETUAL-N3-R1-<6 members>"
        wave_no = 1
    existing_ids = {str(e.get("id", "")) for e in vals}
    new_entries = [e for e in new_entries if e["id"] not in existing_ids]
    if not new_entries:
        _write_state(st)
        print(f"supply: {face_id} per-shard entries already in pool -- "
              f"idempotent no-op")
        return 0
    pool.setdefault("entries", [])
    if isinstance(pool["entries"], dict):
        for e in new_entries:
            pool["entries"][e["id"]] = e
    else:
        pool["entries"].extend(new_entries)
    pool["updated_at"] = ts
    _pool_write_mirror(pool)
    st["waves"].append({"face": face_id, "wave": wave_no, "entered_at": ts,
                        "n_entries": len(new_entries), "bands": bands_rec})
    _write_state(st)
    print(f"supply: materialized {len(new_entries)} per-shard entries "
          f"{id_msg} into runnable_pool "
          f"(single-writer lane write, format-mirrored)")
    return 0


def cmd_selftest():
    global POOL_PATH               # 8b swaps it to a temp file (restored)
    ok = True
    # 1. face registry integrity (law sec.2: four faces, priorities 1-4)
    ids = [f["id"] for f in sorted(FACES, key=lambda x: x["priority"])]
    assert ids == ["N1", "N3", "N2", "N4"], "face priority order drift"
    assert all("runner" in f and "wave" in f for f in FACES)
    # 2. seed bands disjoint: intra-N1, vs v1, vs ext wave-1, vs SEED_REGISTRY
    reg_ints = {v for v in sg.SEED_REGISTRY.values() if isinstance(v, (int, float))}
    used = []
    for w, b in N1_BANDS.items():
        band_a = set(range(b["a"][0], b["a"][1] + 1))
        band_b = set(range(b["b_exit"][0], b["b_exit"][1] + 1))
        assert not (band_a & band_b), f"N1 w{w} A/B band overlap"
        assert not (band_a & V1_IN_USE) and not (band_b & V1_IN_USE), f"N1 w{w} hits v1 band"
        assert not (band_a & EXT_W1_IN_USE) and not (band_b & EXT_W1_IN_USE), f"N1 w{w} hits ext w1"
        assert not (band_a & reg_ints) and not (band_b & reg_ints), f"N1 w{w} hits SEED_REGISTRY"
        used.append((band_a, band_b))
    for i in range(len(used)):
        for j in range(i + 1, len(used)):
            assert not (used[i][0] & used[j][0]) and not (used[i][1] & used[j][1]), \
                f"N1 waves {i + 2}/{j + 2} band overlap"
    # 3. band continuity (no unassigned gap inside the pre-assigned ladder)
    for w in (3, 4):
        assert N1_BANDS[w]["a"][0] == N1_BANDS[w - 1]["a"][1] + 1, f"N1 w{w} A gap"
        assert N1_BANDS[w]["b_exit"][0] == N1_BANDS[w - 1]["b_exit"][1] + 1, f"N1 w{w} B gap"
    # 3b. W5 skip-over packing invariant (law sec.4 W5 row): the arithmetic
    # +2_000 tail (18_100..20_099) is documented-refused (hits v1 B band
    # 20_000..20_019 / registry 20000 / ext W1 B 20_100..20_299); A sits at
    # the first free window after every reserved band == W5 B end + 1, and
    # the B tail keeps the +200 stride (W4 B end + 1).
    assert N1_BANDS[5]["a"][0] == N1_BANDS[5]["b_exit"][1] + 1, \
        "W5 packing drift (A must sit at W5 B end + 1)"
    assert N1_BANDS[5]["a"][1] - N1_BANDS[5]["a"][0] + 1 == 2000, "W5 A width"
    assert N1_BANDS[5]["b_exit"][1] - N1_BANDS[5]["b_exit"][0] + 1 == 200, "W5 B width"
    assert N1_BANDS[4]["b_exit"][1] + 1 == N1_BANDS[5]["b_exit"][0], "W5 B tail gap"
    # 3c. W6 skip-over packing invariant (law sec.4 W6+ WARNING): A keeps
    # the arithmetic +2_000 tail (W5 A end + 1); B's arithmetic +200 tail
    # (21_900..22_099) is documented-refused -- it falls inside the W5 A
    # band -- so B skips past every reserved band including this wave's
    # own A band and packs at the first free 200-window (W6 A end + 1).
    # Refusal facts machine-proven: the arithmetic B position MUST
    # collide (the skip is forced, not a free pick).
    assert N1_BANDS[6]["a"][0] == N1_BANDS[5]["a"][1] + 1, "W6 A tail gap"
    assert N1_BANDS[6]["a"][1] - N1_BANDS[6]["a"][0] + 1 == 2000, "W6 A width"
    assert N1_BANDS[6]["b_exit"][1] - N1_BANDS[6]["b_exit"][0] + 1 == 200, "W6 B width"
    assert N1_BANDS[6]["b_exit"][0] == N1_BANDS[6]["a"][1] + 1, \
        "W6 packing drift (B must sit at W6 A end + 1)"
    arith_b = set(range(N1_BANDS[5]["b_exit"][1] + 1,
                        N1_BANDS[5]["b_exit"][1] + 201))
    w5_a = set(range(N1_BANDS[5]["a"][0], N1_BANDS[5]["a"][1] + 1))
    assert arith_b & w5_a, \
        "W6 B skip must be forced (arithmetic tail must hit the W5 A band)"
    # 3d. W7 skip-over packing invariant (r501 bm-b, same forced-skip
    # family -- BOTH tails refused this wave): A's arithmetic +2_000
    # tail (25_900..27_899) is documented-refused (hits the W6 B band
    # 25_900..26_099), so A packs at the first free 2,000-window ==
    # W6 B end + 1; B's arithmetic +200 tail (26_100..26_299) is refused
    # too (falls inside this wave's own A band), so B packs at
    # W7 A end + 1. Refusal facts machine-proven below.
    assert N1_BANDS[7]["a"][1] - N1_BANDS[7]["a"][0] + 1 == 2000, "W7 A width"
    assert N1_BANDS[7]["b_exit"][1] - N1_BANDS[7]["b_exit"][0] + 1 == 200, \
        "W7 B width"
    assert N1_BANDS[7]["a"][0] == N1_BANDS[6]["b_exit"][1] + 1, \
        "W7 packing drift (A must sit at W6 B end + 1)"
    assert N1_BANDS[7]["b_exit"][0] == N1_BANDS[7]["a"][1] + 1, \
        "W7 packing drift (B must sit at W7 A end + 1)"
    arith_a7 = set(range(N1_BANDS[6]["a"][1] + 1, N1_BANDS[6]["a"][1] + 2001))
    w6_b = set(range(N1_BANDS[6]["b_exit"][0], N1_BANDS[6]["b_exit"][1] + 1))
    assert arith_a7 & w6_b, \
        "W7 A skip must be forced (arithmetic tail must hit the W6 B band)"
    arith_b7 = set(range(N1_BANDS[6]["b_exit"][1] + 1,
                         N1_BANDS[6]["b_exit"][1] + 201))
    w7_a = set(range(N1_BANDS[7]["a"][0], N1_BANDS[7]["a"][1] + 1))
    assert arith_b7 & w7_a, \
        "W7 B skip must be forced (arithmetic tail must hit the W7 A band)"
    # 3e. W8 skip-over packing invariant (r312 bm-c, forced-skip family
    # with a registry-point refusal): A's arithmetic +2_000 tail
    # (28_100..30_099) is documented-refused -- it hits the W7 B band
    # AND the SEED_REGISTRY lfc_p1_screen point 30_000 (actual draw
    # range 30_000..30_099, N_RAND=50 x 2 exit regimes); the law
    # sec.4 pinned W8+ WARNING window (28_300..30_299) is refused by
    # the same point + actual range, so A packs at the first
    # 2,000-window clear of every reserved band AND the lfc actual
    # draw range (30_100..32_099); B's arithmetic +200 tail
    # (28_300..28_499) is clean this wave (the A jump cleared the
    # collision the warning predicted) and keeps the stride verbatim.
    # Refusal facts machine-proven below.
    assert N1_BANDS[8]["a"][1] - N1_BANDS[8]["a"][0] + 1 == 2000, "W8 A width"
    assert N1_BANDS[8]["b_exit"][1] - N1_BANDS[8]["b_exit"][0] + 1 == 200, \
        "W8 B width"
    arith_a8 = set(range(N1_BANDS[7]["a"][1] + 1, N1_BANDS[7]["a"][1] + 2001))
    w7_b = set(range(N1_BANDS[7]["b_exit"][0], N1_BANDS[7]["b_exit"][1] + 1))
    assert arith_a8 & w7_b, \
        "W8 A skip must be forced (arithmetic tail must hit the W7 B band)"
    assert 30_000 in arith_a8 and 30_000 in sg.SEED_REGISTRY.values(), \
        "W8 A skip must be forced (arithmetic tail must hit lfc_p1_screen registry point)"
    warned_a8 = set(range(28_300, 30_300))
    lfc_actual = set(range(30_000, 30_100))
    assert 30_000 in warned_a8 and (warned_a8 & lfc_actual), \
        "law-pinned W8 warning window must be refused (registry point + lfc actual range)"
    w8_a = set(range(N1_BANDS[8]["a"][0], N1_BANDS[8]["a"][1] + 1))
    assert not (w8_a & lfc_actual), "W8 A must clear the lfc actual draw range"
    assert N1_BANDS[8]["a"][0] == 30_100, \
        "W8 A packs at the first 2,000-window clear of the lfc actual range"
    assert N1_BANDS[8]["a"][0] > max(N1_BANDS[7]["b_exit"][1], *lfc_actual), \
        "W8 A must sit beyond every reserved band and the lfc range"
    arith_b8 = set(range(N1_BANDS[7]["b_exit"][1] + 1,
                         N1_BANDS[7]["b_exit"][1] + 201))
    assert not (arith_b8 & w8_a), \
        "W8 B arithmetic tail must be clean (no skip this wave)"
    assert N1_BANDS[8]["b_exit"][0] == N1_BANDS[7]["b_exit"][1] + 1, \
        "W8 B tail gap (stride kept verbatim)"
    # 3f. W9 arithmetic-continuation invariant (r506 bm-b, O-20261001-1332
    # sec.1.2): the W8 row projected BOTH arithmetic tails clean, and the
    # machine gate at prereg time confirmed ADMIT (no forced skip this
    # wave) -- A == W8 A end + 1, B == W8 B end + 1, strides verbatim,
    # both clear of every reserved band + SEED_REGISTRY + the lfc actual
    # draw range (leg 2 all-bands disjoint covers W9 once listed here).
    assert N1_BANDS[9]["a"][1] - N1_BANDS[9]["a"][0] + 1 == 2000, "W9 A width"
    assert N1_BANDS[9]["b_exit"][1] - N1_BANDS[9]["b_exit"][0] + 1 == 200, \
        "W9 B width"
    assert N1_BANDS[9]["a"][0] == N1_BANDS[8]["a"][1] + 1, \
        "W9 A must keep the arithmetic stride (no skip -- ADMIT receipt)"
    assert N1_BANDS[9]["b_exit"][0] == N1_BANDS[8]["b_exit"][1] + 1, \
        "W9 B must keep the arithmetic stride (no skip -- ADMIT receipt)"
    w9_a = set(range(N1_BANDS[9]["a"][0], N1_BANDS[9]["a"][1] + 1))
    w9_b = set(range(N1_BANDS[9]["b_exit"][0], N1_BANDS[9]["b_exit"][1] + 1))
    assert not (w9_a & lfc_actual) and not (w9_b & lfc_actual), \
        "W9 bands must clear the lfc actual draw range"
    # 3g. W10 arithmetic-continuation invariant (r508 bm-b, T-2026-10-01-
    # 141 s1 FIRST ENGINE-OWNED WAVE): the W9 row projected BOTH
    # arithmetic tails clean, and the machine gate at prereg time
    # confirmed ADMIT (no forced skip) -- A == W9 A end + 1, B == W9 B
    # end + 1, strides verbatim, both clear of every reserved band +
    # SEED_REGISTRY + the lfc actual draw range (leg 2 all-bands
    # disjoint covers W10 once listed here). engine_owner parity is
    # asserted against the runner's WAVE_CONFIGS by the n1 selftest W10
    # materializer leg; here the structural face: only engine-owned
    # waves carry engine_owner, and cmd_supply must refuse them.
    assert N1_BANDS[10]["a"][1] - N1_BANDS[10]["a"][0] + 1 == 2000, "W10 A width"
    assert N1_BANDS[10]["b_exit"][1] - N1_BANDS[10]["b_exit"][0] + 1 == 200, \
        "W10 B width"
    assert N1_BANDS[10]["a"][0] == N1_BANDS[9]["a"][1] + 1, \
        "W10 A must keep the arithmetic stride (no skip -- ADMIT receipt)"
    assert N1_BANDS[10]["b_exit"][0] == N1_BANDS[9]["b_exit"][1] + 1, \
        "W10 B must keep the arithmetic stride (no skip -- ADMIT receipt)"
    w10_a = set(range(N1_BANDS[10]["a"][0], N1_BANDS[10]["a"][1] + 1))
    w10_b = set(range(N1_BANDS[10]["b_exit"][0], N1_BANDS[10]["b_exit"][1] + 1))
    assert not (w10_a & lfc_actual) and not (w10_b & lfc_actual), \
        "W10 bands must clear the lfc actual draw range"
    assert N1_BANDS[10].get("engine_owner") == "bm-b", \
        "W10 engine_owner must be bm-b (T-141 s1 first engine wave)"
    # engine-wave set derives from the band table itself (r511 law: enum-
    # snapshot legs must derive, never hardcode wave ids -- W12 patched
    # this tuple by hand once, W13 flagged it red again at freeze time;
    # structural truth: engine ownership is an era property, not a
    # per-wave whitelist -- every engine-owned wave must be >= 10, every
    # wave below the engine era stays pool-owned).
    assert all(w >= 10 for w in N1_BANDS
               if N1_BANDS[w].get("engine_owner")), \
        "pool-era waves must stay pool-owned (engine_owner only on W10+ engine waves)"
    # 3h. W11 arithmetic-continuation invariant (r510 bm-b, SECOND
    # ENGINE-OWNED WAVE): the W10 row projected BOTH arithmetic tails
    # clean and the machine gate at prereg time confirmed ADMIT (no
    # forced skip) -- A == W10 A end + 1, B == W10 B end + 1, strides
    # verbatim, both clear of every reserved band + SEED_REGISTRY + the
    # lfc actual draw range (leg 2 all-bands disjoint covers W11 once
    # listed here). engine_owner parity is asserted against the runner's
    # WAVE_CONFIGS by the n1 selftest W11 materializer leg; here the
    # structural face: only engine-owned waves carry engine_owner, and
    # cmd_supply must refuse them.
    assert N1_BANDS[11]["a"][1] - N1_BANDS[11]["a"][0] + 1 == 2000, "W11 A width"
    assert N1_BANDS[11]["b_exit"][1] - N1_BANDS[11]["b_exit"][0] + 1 == 200, \
        "W11 B width"
    assert N1_BANDS[11]["a"][0] == N1_BANDS[10]["a"][1] + 1, \
        "W11 A must keep the arithmetic stride (no skip -- ADMIT receipt)"
    assert N1_BANDS[11]["b_exit"][0] == N1_BANDS[10]["b_exit"][1] + 1, \
        "W11 B must keep the arithmetic stride (no skip -- ADMIT receipt)"
    w11_a = set(range(N1_BANDS[11]["a"][0], N1_BANDS[11]["a"][1] + 1))
    w11_b = set(range(N1_BANDS[11]["b_exit"][0], N1_BANDS[11]["b_exit"][1] + 1))
    assert not (w11_a & lfc_actual) and not (w11_b & lfc_actual), \
        "W11 bands must clear the lfc actual draw range"
    assert N1_BANDS[11].get("engine_owner") == "bm-b", \
        "W11 engine_owner must be bm-b (never-dry engine wave)"
    # 4. pool parse (read-only; missing file tolerated)
    pool = _load_pool()
    _pool_live_count(pool)
    # 4b. park_note'd entries are deliberate holds, never live supply
    # (r304/r504 marker law; live case r497 W14 re-park deadlocked the
    # starvation leg -- the face this generator exists to feed)
    probe_pool = {"entries": [
        {"id": "A", "status": "done"},
        {"id": "B", "status": "waiting"},
        {"id": "C", "status": "waiting", "park_note": "governance hold"},
        {"id": "D", "status": "ready", "park_note": "governance hold"},
        {"id": "E", "status": "ready"},
    ]}
    assert _pool_live_count(probe_pool) == 2, \
        "park_note'd entries must not count as live supply"
    # 4c. ghost faces are not supply (r309 W5 live case: a finalized wave
    # awaiting its entry-layer done flip must not block the never-dry
    # trigger): ready + all shards done = burn-complete = not claimable;
    # ready + any shard not done = claimable; shardless entries keep the
    # legacy claimable face.
    probe_pool2 = {"entries": [
        {"id": "G1", "status": "ready",
         "shards": [{"key": "k", "status": "done"}]},
        {"id": "G2", "status": "ready",
         "shards": [{"key": "k", "status": "ready"}]},
        {"id": "G3", "status": "ready",
         "shards": [{"key": "k1", "status": "done"},
                    {"key": "k2", "status": "ready"}]},
    ]}
    assert _pool_live_count(probe_pool2) == 2, \
        "ghost (all-shards-done) entries must not count as live supply"
    # 5. state round-trip (no pool writes; state file may be created in tmp)
    st = _load_state()
    st["_selftest_probe"] = True
    st2 = json.loads(json.dumps(st))
    assert st2.get("_selftest_probe") is True
    del st["_selftest_probe"]
    # 6. py face reader robustness (missing machine file -> None, no crash)
    assert _py_face() is None or isinstance(_py_face(), float)
    # 7. per-shard materializer expansion face (pure function; no writes)
    ts = "2026-10-01T00:00:00"
    exp = _expand_wave_entries(FACES[0], 3, ts)
    assert len(exp) == 12, "expansion must be 12 per-shard entries"
    assert [e["id"] for e in exp] == \
        [f"PERPETUAL-N1-W3-SHARD-{i}" for i in range(12)]
    for i, e in enumerate(exp):
        assert e["runner_args"] == ["run", "--shard", str(i), "--of", "12",
                                    "--wave", "3"], f"shard {i} args drift"
        assert e["status"] == "ready" and e["lane_owner"] == "ANY"
        assert e["worker_class"] == "self-contained"
        assert e["entered_at"] == ts and e["priority"] == 1
        assert "PERPETUAL_N1_W3_PREREG" in e["prereg_ref"]
        assert str(N1_BANDS[3]["a"][0]) in e["prereg_ref"], "law A band uncited"
        assert str(N1_BANDS[3]["b_exit"][0]) in e["prereg_ref"], "law B band uncited"
        assert len(e["shards"]) == 1 and e["shards"][0]["key"] == f"n1w3-{i}of12"
        assert e["shards"][0]["status"] == "ready"
        assert e["shards"][0]["checkpoint"].startswith(
            f"results/p2cal_ext/n1_w3/shard-{i}-of-12.json")
        assert "owner" not in e["shards"][0], "unclaimed at materialization"
        assert e["workers_plan"]["workers"] >= 1, "O-2355 workers face"
        for forbidden_owner in ("owner", "owner_since", "done_at", "done_by"):
            assert forbidden_owner not in e["shards"][0]
    # expansion band cites stay law-frozen (R250): tamper probe refuses
    bands_copy = dict(N1_BANDS[3])
    try:
        N1_BANDS[3] = {"a": (99_999, 99_999), "b_exit": (99_998, 99_998)}
        bad = _expand_wave_entries(FACES[0], 3, ts)
        assert "99999" in bad[0]["prereg_ref"], "expansion ignores band table"
    finally:
        N1_BANDS[3] = bands_copy
    # 7b. N3-R1 materializer expansion face (pure function; no writes;
    # member list + entry ids single-sourced from the runner module)
    exp3 = _expand_n3_r1_entries(ts)
    assert len(exp3) == 6, "N3-R1 expansion must be 6 per-member entries"
    import perpetual_faces_n3 as n3mod
    assert [e["id"] for e in exp3] == \
        [n3mod.pool_entry_id(m["id"]) for m in n3mod.load_members()], \
        "N3 entry ids drifted from the runner handshake face"
    for e in exp3:
        mid = e["id"].split("PERPETUAL-N3-R1-")[1]
        assert e["runner_args"] == ["run", "--member", mid], "N3 args drift"
        assert e["status"] == "ready" and e["lane_owner"] == "ANY"
        assert e["worker_class"] == "self-contained"
        assert "PERPETUAL_N3_R1_PREREG" in e["prereg_ref"], "N3 prereg uncited"
        assert "70_000" in e["prereg_ref"], "N3 seed band uncited"
        assert e["shards"][0]["key"] == mid
        assert e["shards"][0]["checkpoint"] == (
            f"results/perpetual_faces/n3_r1/cells-{mid}.jsonl "
            f"(presence=done; deterministic rerun byte-equal)")
        assert e["workers_plan"]["workers"] == 1, "N3 light-batch workers face"
        for forbidden_owner in ("owner", "owner_since", "done_at", "done_by"):
            assert forbidden_owner not in e["shards"][0]
    # 8. pool format-mirror probe (read-only; r289 law: indent2+CRLF probed;
    #    trailing face follows the migrated canonical producer -- bm-b r499
    #    pool-format migration made the flip tool emit trailing NL and the
    #    probe dynamic; the guard asserts probe-vs-bytes truth, not a
    #    hardcoded pre-migration face)
    if os.path.exists(POOL_PATH):
        indent, crlf, trailing_nl = _pool_format_probe()
        assert crlf, f"pool EOL face drifted: crlf={crlf}"
        b = open(POOL_PATH, "rb").read()
        assert trailing_nl == b.endswith(b"\n"), "trailing probe drift vs bytes"
        # indent probe-vs-bytes truth (bm-c r307 trailing-pin fix applied
        # to the indent face too: the file's real indent is whatever the
        # majority producer writes -- a hardcoded pre-migration pin only
        # chronic-false-flags every resolve/producer cycle)
        probe_indent = None
        for line in b.decode("utf-8", errors="replace").split("\n"):
            if line.strip().startswith('"'):
                probe_indent = len(line) - len(line.lstrip(" "))
                break
        assert indent == probe_indent, \
            f"indent probe drift vs bytes: {indent}/{probe_indent}"
    # 8b. writer round-trip on a temp file (hermetic; real pool untouched):
    # probe defaults + CRLF mirror + no trailing NL + byte-identical face
    real_pool = POOL_PATH
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        try:
            POOL_PATH = os.path.join(td, "pool_probe.json")
            sample = {"version": 1, "entries": [{"id": "X-1", "n": [1, 2]}]}
            _pool_write_mirror(sample)
            b = open(POOL_PATH, "rb").read()
            assert b.count(b"\r\n") == b.count(b"\n") and b.count(b"\n") > 0, \
                "CRLF mirror broken"
            assert not b.endswith(b"\n"), "trailing NL leaked"
            assert b'{\r\n  "version": 1' in b, "indent2 mirror broken"
            rt = json.loads(b.decode("utf-8"))
            assert rt == sample, "round-trip content drift"
            # probe on the temp face agrees (indent2/CRLF/no-trailing)
            assert _pool_format_probe() == (2, True, False)
        finally:
            POOL_PATH = real_pool
    print("perpetual_faces selftest: 8/8 PASS "
          "(registry/seed-bands+3c-W6+3d-W7-packing/pool/state/py-face/"
          "materializer-expansion/pool-format-probe+writer-roundtrip; "
          "4b park_note + 4c ghost claimable legs)")
    return 0 if ok else 1


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    try:
        if cmd == "status":
            return cmd_status()
        if cmd == "supply":
            return cmd_supply()
        if cmd == "selftest":
            return cmd_selftest()
        print(f"unknown subcommand: {cmd} (use status|supply|selftest)")
        return 2
    except AssertionError as e:
        print(f"selftest FAIL: {e}")
        return 1
    except Exception as e:  # mechanism failure: report honestly, never mask
        print(f"mechanism failure: {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
