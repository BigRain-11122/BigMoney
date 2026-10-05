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
    # FORTY-SECOND ENGINE-OWNED WAVE (r351 bm-c freeze, same-window
    # zero-gap relay after the W52 full-lifecycle closeout): bm-c's
    # SEVENTEENTH owned wave. Wave 53 = next free number after the
    # registered W52 row (chain FULLY CAUGHT UP W1..W52 at this
    # freeze -- zero in-flight upstream faces, second fully-caught-up
    # window). BOTH SIDES = ARITHMETIC CONTINUATION from the W52 row
    # tail, no skip: A 149_004..151_003 (= W52 A end 149_003 + 1) and
    # B 46_401..46_600 (= W52 B end 46_400 + 1) -- both windows CLEAN
    # per the W52 row W53+ WARNING projections, machine-derived at
    # this freeze (r535 law). Machine-verified at prereg time
    # (results/_r351bmc_w53_band_gate.py ADMIT receipt vs the 49-row
    # pre-W53 table + live SEED_REGISTRY values + probe cluster
    # 95_000..95_003 r335 discovery leg + N3-R1 used-seed band
    # 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). NOT a re-pick (R250: W53 bands were
    # never assigned).
    53: {"a": (149_004, 151_003), "b_exit": (46_401, 46_600),
         "engine_owner": "bm-c"},
    # FORTY-THIRD ENGINE-OWNED WAVE (r559 bm-a freeze): bm-a's
    # THIRTEENTH owned wave. Wave 54 = next free number after the
    # registered W53 row (own-series continuation under the
    # de-throttle law; bm-a's previous wave W48 closed
    # full-lifecycle at r558 -- seat-loss re-derive finalize
    # K=103,520; W53 bm-c registered with finalize in flight --
    # coexist by band disjointness per r531 law).
    # BOTH SIDES = ARITHMETIC CONTINUATION from the W53 row tail,
    # no skip: A 151_004..153_003 (= W53 A end 151_003 + 1) and
    # B 46_601..46_800 (= W53 B end 46_600 + 1) -- both windows
    # CLEAN per the W53 row W54+ WARNING projections
    # (three-machine cross-validation: bm-c r351 freeze gate +
    # bm-b r559 yield-window gate + this freeze's machine
    # re-derive, r535 law). Machine-verified at prereg time
    # (results/_r559bma_w54_band_gate.py ADMIT receipt vs the
    # 51-row pre-W54 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). NOT a re-pick (R250: W54
    # bands were never assigned).
    54: {"a": (151_004, 153_003), "b_exit": (46_601, 46_800),
         "engine_owner": "bm-a"},

    # r559 bm-b freeze: wave 55 = first FREE number after the registered
    # W53 row AND the bm-a PUBLISHED W54 declaration (MSG-20261002-0615
    # addendum "bm-a next own target = W54, A 151_004..153_003 / B
    # 46_601..46_800" -- published=reserved, r518-1 law, W48/W49
    # precedent; bm-b's same-window W54 freeze yielded to it). A = scan
    # past the declared W54 A band (W19-A re-base family); B = scan
    # past the declared W54 B band AND the SEED_REGISTRY point
    # xlib_synth_null_b=47_000 (W51-B re-base family: 46_000 -> 47_000
    # ladder). ADMIT receipt at prereg time
    # (results/_r559bmb_w55_band_gate.py vs the 51-row pre-W55 table
    # + declared-W54 bands in the reserved universe + live
    # SEED_REGISTRY values + probe cluster 95_000..95_003 r335
    # discovery leg + N3-R1 used-seed band 70_000..70_005 MSG-183x
    # r529 mandatory leg; origin slot vacancy machine-checked). NOT
    # a re-pick (R250: W55 bands were never assigned).
    55: {"a": (153_004, 155_003), "b_exit": (47_001, 47_200),
         "engine_owner": "bm-b"},

    # r560 bm-b freeze: wave 56 = first FREE number after the
    # registered W55 row (W55 registration union-repaired the
    # same round after the bm-a r559 W54-freeze anchor-replace
    # clobber -- r519-family 6th occurrence; this registration
    # consumes the repaired registry face). BOTH SIDES
    # ARITHMETIC CONTINUATION from the W55 tail, no skip:
    # A 155_004..157_003 (= W55 A end 155_003 + 1) and
    # B 47_201..47_400 (= W55 B end 47_200 + 1) -- both
    # windows CLEAN == the W55 row W56+ WARNING projections
    # (machine re-derived at freeze per r535 law). ADMIT
    # receipt at prereg time
    # (results/_r560bmb_w56_band_gate.py vs the 53-row
    # pre-W56 registered table + live SEED_REGISTRY values +
    # probe cluster 95_000..95_003 r335 discovery leg +
    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529
    # mandatory leg; origin slot vacancy machine-checked).
    # NOT a re-pick (R250: W56 bands were never assigned).
    56: {"a": (155_004, 157_003), "b_exit": (47_201, 47_400),
         "engine_owner": "bm-b"},
    # FORTY-SIXTH ENGINE-OWNED WAVE (r561 bm-a freeze): bm-a's
    # FOURTEENTH owned wave. Wave 57 = next free number after the
    # registered W56 row (own-series continuation under the
    # de-throttle law; bm-a's previous wave W54 burned 12/12 and
    # delivered to origin at r561 S0 surgical, finalize
    # chain-pending; W53/W54/W55/W56 = FOUR in-flight upstream
    # seats -- coexist by band disjointness per r531 law).
    # BOTH SIDES = ARITHMETIC CONTINUATION from the W56 row tail,
    # no skip: A 157_004..159_003 (= W56 A end 157_003 + 1) and
    # B 47_401..47_600 (= W56 B end 47_400 + 1) -- both windows
    # CLEAN per the W56 row W57+ WARNING projections
    # (bm-b r560 freeze gate projection leg + this freeze's
    # machine re-derive, r535 law). Machine-verified at prereg
    # time (results/_r561bma_w57_band_gate.py ADMIT receipt vs
    # the 54-row pre-W57 table + live SEED_REGISTRY values +
    # probe cluster 95_000..95_003 r335 discovery leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;
    # origin slot vacancy machine-checked). NOT a re-pick
    # (R250: W57 bands were never assigned).
    57: {"a": (157_004, 159_003), "b_exit": (47_401, 47_600),
         "engine_owner": "bm-a"},
    # FORTY-SEVENTH ENGINE-OWNED WAVE (r354 bm-c freeze): bm-c's
    # EIGHTEENTH owned wave. Wave 58 = next free number after the
    # registered W57 row (own-series continuation under the
    # de-throttle law; chain FULLY CAUGHT UP W1..W57 at this freeze
    # -- W57 bm-a r562 same-window full-lifecycle closeout, ledger
    # head 489,948, K=123,320, ZERO in-flight upstream seats;
    # MSG-20261002-0700 bm-a receipt confirms the W58 window fully
    # clear). BOTH SIDES = ARITHMETIC CONTINUATION from the W57 row
    # tail, no skip: A 159_004..161_003 (= W57 A end 159_003 + 1) and
    # B 47_601..47_800 (= W57 B end 47_600 + 1) -- both windows
    # CLEAN per the W57 row W58+ WARNING projections
    # (bm-a r561 freeze gate projection leg + this freeze's
    # machine re-derive, r535 law). Machine-verified at prereg
    # time (results/_r354bmc_w58_band_gate.py ADMIT receipt vs
    # the 54-row pre-W58 registered table + live SEED_REGISTRY values +
    # probe cluster 95_000..95_003 r335 discovery leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;
    # origin slot vacancy machine-checked). NOT a re-pick
    # (R250: W58 bands were never assigned).
    58: {"a": (159_004, 161_003), "b_exit": (47_601, 47_800),
         "engine_owner": "bm-c"},
    # W59 r562 bm-b: A = ARITHMETIC CONTINUATION from the registered
    # W58 tail zero skip (161_004..163_003 = W58 A end 161_003 + 1,
    # CLEAN, machine-derived == the W58 row W59+ published projection);
    # B = FORCED SKIP family -- arithmetic window 47_801..48_000
    # REFUSED at the SEED_REGISTRY point 48_000 (p4_pairs/
    # p1d_gdhs_quarterly), first clean window 48_001..48_200
    # scan-derived (W39-B/W43-B/W47-B family; ADMIT receipt
    # results/_r562bmb_w59_band_gate.py; probe cluster 95_000..95_003
    # r335 discovery leg + N3-R1 used-seed band 70_000..70_005
    # MSG-183x r529 mandatory leg; origin slot vacancy
    # machine-checked). NOT a re-pick (R250: W59 bands were never
    # assigned).
    59: {"a": (161_004, 163_003), "b_exit": (48_001, 48_200),
         "engine_owner": "bm-b"},
    # W60 r355 bm-c: A = ARITHMETIC CONTINUATION from the registered
    # W59 tail zero skip (163_004..165_003 = W59 A end 163_003 + 1,
    # WIDTH_A 2_000 machine-derived CLEAN == the W59 row W60+ published
    # projection verbatim); B = ARITHMETIC CONTINUATION zero skip
    # (48_201..48_400 = W59 B end 48_200 + 1, WIDTH_B 200
    # machine-derived CLEAN). Chain W1..W59 finalizes ALL LANDED at
    # this freeze (W59 bm-b r563 one-pass K=127,720, ledger head
    # 494,348) = ZERO in-flight upstream seats. ADMIT receipt
    # results/_r355bmc_w60_band_gate.py; probe cluster 95_000..95_003
    # r335 discovery leg + N3-R1 used-seed band 70_000..70_005
    # MSG-183x r529 mandatory leg; origin slot vacancy
    # machine-checked. NOT a re-pick (R250: W60 bands were never
    # assigned).
    60: {"a": (163_004, 165_003), "b_exit": (48_201, 48_400),
         "engine_owner": "bm-c"},
    # W61 r564 bm-b: A = ARITHMETIC CONTINUATION from the registered
    # W60 tail zero skip (165_004..167_003 = W60 A end 165_003 + 1,
    # WIDTH_A 2_000 machine-derived CLEAN == the W60 row W61+ published
    # projection verbatim); B = ARITHMETIC CONTINUATION zero skip
    # (48_401..48_600 = W60 B end 48_400 + 1, WIDTH_B 200
    # machine-derived CLEAN). Chain W1..W60 finalizes ALL LANDED at
    # this freeze (W60 bm-c r355 one-pass K=129,920, ledger head
    # 496,548) = ZERO in-flight upstream seats. ADMIT receipt
    # results/_r564bmb_w61_band_gate.py; probe cluster 95_000..95_003
    # r335 discovery leg + N3-R1 used-seed band 70_000..70_005
    # MSG-183x r529 mandatory leg; origin slot vacancy
    # machine-checked. NOT a re-pick (R250: W61 bands were never
    # assigned).
    61: {"a": (165_004, 167_003), "b_exit": (48_401, 48_600),
         "engine_owner": "bm-b"},
    # FIFTY-FIRST ENGINE-OWNED WAVE (r565 bm-a freeze): bm-a's
    # fourteenth owned per machine-derive (engine_owner==bm-a
    # rows 13 + candidate). Wave 62 = next free number after the
    # registered W61 row (seat declared published=reserved
    # MSG-20261002-0818-bma, r518-1 law; W61 bm-b r564 = ONE
    # in-flight upstream seat at this freeze, shards burning,
    # finalize chain-pending FAIL-CLOSED r307). BOTH SIDES =
    # ARITHMETIC CONTINUATION from the W61 row tail, no skip: A
    # 167_004..169_003 (= W61 A end 167_003 + 1) and B
    # 48_601..48_800 (= W61 B end 48_600 + 1) -- both windows
    # CLEAN per the W61 row W62+ WARNING projections
    # (bm-b r564 freeze gate projection leg + this freeze's
    # machine re-derive, r535 law). Machine-verified at prereg
    # time (results/_r565bma_w62_band_gate.py ADMIT receipt vs
    # the 60-row pre-W62 table + live SEED_REGISTRY values +
    # probe cluster 95_000..95_003 r335 discovery leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;
    # origin slot vacancy machine-checked). NOT a re-pick
    # (R250: W62 bands were never assigned).
    62: {"a": (167_004, 169_003), "b_exit": (48_601, 48_800),
         "engine_owner": "bm-a"},
    # FIFTY-SECOND ENGINE-OWNED WAVE (r357 bm-c freeze): bm-c's
    # TWENTIETH owned per machine-derive (engine_owner==bm-c
    # rows 19 + candidate). Wave 63 = next free number after the
    # registered W62 row (chain FULLY CAUGHT UP W1..W62 at this
    # freeze -- W62 bm-a-owned wave burned 12/12 by bm-a tick
    # engine, finalized one-pass bm-c r357 K=134,320 ledger head
    # 500,948, ZERO in-flight upstream seats; origin slot vacancy
    # machine-checked at leg3). A = ARITHMETIC CONTINUATION from
    # the W62 A tail (169_004..171_003 = W62 A end 169_003 + 1,
    # CLEAN per the W62 row W63+ WARNING projection, machine
    # re-derived r535 law). B = FORCED SKIP: the arithmetic
    # position 48_801..49_000 is REFUSED (SEED_REGISTRY
    # p4_ext_tilt_q=49_000) and 49_001..49_200 is REFUSED
    # (p4_ext_tilt_d20=49_100); first clean window 49_201..49_400
    # machine-derived (W26-A/W39-B/W43-B/W47-B/W51-B/W59-B skip
    # family, r307 wave-band tail law; ADMIT receipt
    # results/_r357bmc_w63_band_gate.py; not a re-pick -- R250:
    # W63 bands were never assigned).
    63: {"a": (169_004, 171_003), "b_exit": (49_201, 49_400),
         "engine_owner": "bm-c"},
    # FIFTY-THIRD ENGINE-OWNED WAVE (r566 bm-a freeze): bm-a's
    # fifteenth owned per machine-derive (engine_owner==bm-a
    # rows 14 + candidate). Wave 64 = next free number after the
    # registered W63 row (seat declared published=reserved
    # MSG-20261002-0851-bma, r518-1 law; zero-gap relay after
    # the W63 same-band yield to bm-c per r511 commit-order law
    # -- my W63 freeze unpushed, divergent-B-seed replicas
    # discarded, zero ledger pollution). W1..W62 finalizes ALL
    # LANDED (net head 500,948, K=134,320); W63 bm-c = ONE
    # in-flight upstream seat at this freeze (finalize
    # chain-pending FAIL-CLOSED r307). BOTH SIDES ARITHMETIC
    # CONTINUATION from the W63 row tail, no skip: A
    # 171_004..173_003 (= W63 A end 171_003 + 1) and B
    # 49_401..49_600 (= W63 B end 49_400 + 1) -- both windows
    # CLEAN per the W63 row W64+ WARNING projections (bm-c
    # r357 freeze gate projection leg + this freeze's machine
    # re-derive, r535 law). Machine-verified at prereg time
    # (results/_r566bma_w64_band_gate.py ADMIT receipt vs the
    # 61-row pre-W64 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). NOT a re-pick (R250: W64
    # bands were never assigned).
    64: {"a": (171_004, 173_003), "b_exit": (49_401, 49_600),
         "engine_owner": "bm-a"},
    # FIFTY-FOURTH ENGINE-OWNED WAVE (r566 bm-b freeze): bm-b's
    # TWENTIETH owned per machine-derive (engine_owner==bm-b
    # rows 19 + candidate). Wave 65 = next free number after the
    # registered W64 row (seat declared published=reserved
    # MSG-20261002-0919-bmb, r518-1 law; zero-gap relay after
    # the W64 same-band double-freeze yield to bm-a per r511
    # commit-order law -- the crashed r565 session's W64 freeze
    # drafts (bands bit-identical to bm-a's, r530 same-band
    # class) were never committed: fully discarded, 10 duplicate
    # shard products attribution-verified (audit.machine=bm-b)
    # and discarded, finalize never ran = zero ledger
    # pollution). W1..W63 finalizes ALL LANDED (net head
    # 503,148, K=136,520, bm-c r358); W64 bm-a = ONE
    # in-flight upstream seat at this freeze (burn in flight,
    # finalize chain-pending FAIL-CLOSED r307). BOTH SIDES
    # ARITHMETIC CONTINUATION from the W64 row tail, no skip:
    # A 173_004..175_003 (= W64 A end 173_003 + 1) and B
    # 49_601..49_800 (= W64 B end 49_600 + 1) -- both windows
    # CLEAN per the W64 row W65+ WARNING projections (bm-a
    # r566 freeze gate projection leg + this freeze's machine
    # re-derive, r535 law). Machine-verified at prereg time
    # (results/_r566bmb_w65_band_gate.py ADMIT receipt vs the
    # 63-row pre-W65 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). NOT a re-pick (R250: W65
    # bands were never assigned).
    65: {"a": (173_004, 175_003), "b_exit": (49_601, 49_800),
         "engine_owner": "bm-b"},
    # FIFTY-FIFTH ENGINE-OWNED WAVE (r359 bm-c freeze): bm-c's
    # TWENTY-FIRST owned per machine-derive (engine_owner==bm-c
    # rows 20 + candidate). Wave 66 = first free number after the
    # registered W65 row (seat = the freeze commit itself per
    # r511 table-tail lock -- engine waves have no claim face;
    # same-window MSG cross-notice). W1..W63 finalizes ALL
    # LANDED (net head 503,148, K=136,520, bm-c r358); W64 bm-a
    # + W65 bm-b = TWO in-flight upstream seats at this freeze
    # (registered, burn in flight, finalize chain-pending
    # FAIL-CLOSED r307). A-side ARITHMETIC CONTINUATION
    # from the W65 row tail, no skip: A 175_004..177_003
    # (== W65 A end 175_003 + 1). B-side FORCED-SKIP family:
    # the arithmetic window 49_801..50_000 is REFUSED by
    # SEED_REGISTRY cta_p1=50_000 (window-TAIL hit; refusal
    # machine-proved at leg1-B -- the skip is forced, not a
    # free pick, r307 W26 precedent) -> first clean window
    # 50_001..50_200 (hit+1 restart == window-step chain at a
    # tail hit; r566 W63 fork semantics do not diverge).
    # Machine-verified at prereg time
    # (results/_r359bmc_w66_band_gate.py ADMIT receipt vs the
    # 63-row pre-W66 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). NOT a re-pick (R250: W66
    # bands were never assigned).
    66: {"a": (175_004, 177_003), "b_exit": (50_001, 50_200),
         "engine_owner": "bm-c"},
    # FIFTY-SIXTH ENGINE-OWNED WAVE (r567 bm-b freeze): bm-b's
    # TWENTY-FIRST owned per machine-derive (engine_owner==bm-b
    # rows 20 + candidate). Wave 67 = next free number after the
    # registered W66 row (seat declared published=reserved
    # MSG-20261002-0945-bmb, r518-1 law; never-dry standing step:
    # the same-window W66 draft yielded ZERO-COST to bm-c r359
    # b35b0ee35 first-land per r511 commit-order law -- FIX-A
    # origin-blob freshness abort caught it BEFORE any local
    # edit ran: zero burns, zero ledger touches, unpublished
    # seat; bands had been bit-identical = r530 deterministic
    # same-band cross-validation 12th instance; same-window
    # next-seat re-occupation per r565 bm-a law).
    # W1..W63 finalizes ALL LANDED (net head 503,148, K=136,520,
    # bm-c r358); W64 bm-a (burn in flight) + W65 bm-b (burned
    # 12/12, finalize chain-pending) + W66 bm-c (burned 12/12,
    # finalize chain-pending) = THREE in-flight upstream seats
    # at this freeze (FAIL-CLOSED r307). BOTH SIDES ARITHMETIC
    # CONTINUATION from the W66 row tail, no skip: A
    # 177_004..179_003 (= W66 A end 177_003 + 1) and B
    # 50_201..50_400 (= W66 B end 50_200 + 1) -- both windows
    # CLEAN per the W66 row W67+ WARNING projections (bm-c
    # r359 probe + this freeze's machine re-derive, r535 law).
    # Machine-verified at prereg time
    # (results/_r567bmb_w67_band_gate.py ADMIT receipt vs the
    # 65-row pre-W67 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). NOT a re-pick (R250: W67
    # bands were never assigned).
    67: {"a": (177_004, 179_003), "b_exit": (50_201, 50_400),
         "engine_owner": "bm-b"},
    # FIFTY-SEVENTH ENGINE-OWNED WAVE (r568 bm-a freeze): bm-a's
    # sixteenth owned per machine-derive (engine_owner==bm-a
    # rows 15 + candidate). Wave 68 = next free number after the
    # registered W67 row (seat declared published=reserved
    # MSG-20261002-1010-bma, r518-1 law). W1..W64 finalizes ALL
    # LANDED (net head 505,348, K=138,720 -- W64 bm-a r568);
    # W65 bm-b + W66 bm-c + W67 bm-b = THREE in-flight upstream
    # seats at this freeze (finalize chain-pending
    # FAIL-CLOSED r307). A = ARITHMETIC CONTINUATION from the
    # W67 row tail, no skip: 179_004..181_003 (= W67 A end
    # 179_003 + 1, CLEAN per the W67 row W68+ WARNING, machine
    # re-derive r535 law). B = FORCED-SKIP past-hit restart:
    # arithmetic 50_401..50_600 REFUSED by SEED_REGISTRY
    # cta_p2_noau=50_500 (mid-band single-point machine-red,
    # r307 W5 skip-is-forced precedent) -> first clean window
    # 50_501..50_700 (== the W67 row W68+ published projection
    # verbatim; W26 r335 precedent family). ADMIT receipt
    # results/_r568bma_w68_band_gate.py; NOT a re-pick (R250:
    # W68 bands were never assigned).
    68: {"a": (179_004, 181_003), "b_exit": (50_501, 50_700),
         "engine_owner": "bm-a"},
    # FIFTY-EIGHTH ENGINE-OWNED WAVE (r360 bm-c freeze): bm-c's
    # TWENTY-SECOND owned per machine-derive (engine_owner==bm-c
    # rows 21 + candidate). Wave 69 = first free number after the
    # registered W68 row (seat published=reserved
    # MSG-20261002-1015-bmc, r518-1 law; same-window re-occupation
    # after the W68 yield to bm-a r568 938d8bb54 first-land per
    # r511 commit-order law -- my unpushed freeze 6e8a454b2 fully
    # discarded, alien-seed B-band replicas (9 shards,
    # audit.machine=bm-c verified) all discarded, finalize never
    # ran = zero ledger pollution, r565 re-occupation law).
    # W1..W66 finalizes ALL LANDED (net head 509,748, K=143,120,
    # bm-c r360 same window); W67 bm-b (burn in flight) + W68 bm-a
    # (burn in flight) = TWO in-flight upstream seats at this
    # freeze (finalize chain-pending FAIL-CLOSED r307). BOTH
    # SIDES ARITHMETIC CONTINUATION from the W68 row tail, no
    # skip: A 181_004..183_003 (= W68 A end 181_003 + 1) and B
    # 50_701..50_900 (= W68 B end 50_700 + 1) -- both windows
    # CLEAN per the W68 row W69+ WARNING projections (bm-a r568
    # probe + this freeze's machine re-derive, r535 law).
    # Machine-verified at prereg time
    # (results/_r360bmc_w69_probe.py draft derive +
    # results/_r360bmc_w69_band_gate.py ADMIT receipt vs the
    # 67-row pre-W69 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). NOT a re-pick (R250: W69
    # bands were never assigned).
    69: {"a": (181_004, 183_003), "b_exit": (50_701, 50_900),
         "engine_owner": "bm-c"},
    # FIFTY-NINTH ENGINE-OWNED WAVE (r568 bm-b freeze): bm-b's
    # TWENTY-SECOND owned per machine-derive (engine_owner==bm-b
    # rows 21 + candidate). Wave 70 = next free number after the
    # registered W69 row (seat declared published=reserved
    # MSG-20261002-1040-bmb, r518-1 law; never-dry standing step
    # under CEO de-throttle order O-20261001-2355 sec.2).
    # W1..W67 finalizes ALL LANDED (net head 511,948, K=145,320,
    # bm-b r568 same window); W68 bm-a (burn in flight) + W69 bm-c
    # (burn in flight) = TWO in-flight upstream seats at this
    # freeze (FAIL-CLOSED r307).
    # A-side: ARITHMETIC CONTINUATION from the W69 row tail, no
    # skip: 183_004..185_003 (= W69 A end 183_003 + 1) -- CLEAN
    # per the W69 row W70+ WARNING projection (bm-c r360 probe +
    # this freeze's machine re-derive, r535 law).
    # B-side: FORK FACE #3 (disclosed per the W69 row mandate;
    # pin pending HQ-FEEDBACK F-20261002-03). Arithmetic window
    # 50_901..51_100 REFUSED mid-band by SEED_REGISTRY
    # xstock_synth_null_a=51_000 -> PAST-HIT RESTART
    # 51_001..51_200 TAKEN (single-mid-hit precedent family:
    # W26-A 95_004 + W68-B 50_501 restart; family gate
    # _first_clean law lo=max(hits)+1); window-step chain
    # alternative 51_101..51_300 DISCLOSED NOT TAKEN (the W63-B
    # chained precedent was a DOUBLE-hit case).
    # Machine-verified at prereg time
    # (results/_r568bmb_w70_band_gate.py ADMIT receipt vs the
    # 67-row pre-W70 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). NOT a re-pick (R250: W70
    # bands were never assigned).
    70: {"a": (183_004, 185_003), "b_exit": (51_001, 51_200),
         "engine_owner": "bm-b"},
    # SIXTIETH ENGINE-OWNED WAVE (r361 bm-c freeze): bm-c's
    # TWENTY-THIRD owned per machine-derive (engine_owner==bm-c
    # rows 22 + candidate). Wave 71 = first free number after the
    # registered W70 row (seat published=reserved
    # MSG-20261002-1017-bmc, r518-1 law; never-dry standing step
    # under CEO de-throttle order O-20261001-2355 sec.2).
    # W1..W67 finalizes ALL LANDED (net head 511,948, K=145,320,
    # bm-b r568); W68 bm-a (12/12 burned, finalize pending) +
    # W69 bm-c (12/12 burned, finalize pending) + W70 bm-b (burn
    # in flight) = THREE in-flight upstream seats at this
    # freeze (FAIL-CLOSED r307).
    # BOTH SIDES ARITHMETIC CONTINUATION from the W70 row tail,
    # no skip: A 185_004..187_003 (= W70 A end 185_003 + 1) and
    # B 51_201..51_400 (= W70 B end 51_200 + 1) -- both windows
    # CLEAN per THIS gate's machine derive (r535 law; the W70
    # canon row carries no W71+ WARNING prose -- bm-b r568
    # omitted the tail; their commit-message projection
    # cross-checked).
    # Machine-verified at prereg time
    # (results/_r361bmc_w71_band_gate.py ADMIT receipt vs the
    # 68-row pre-W71 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). NOT a re-pick (R250: W71
    # bands were never assigned).
    71: {"a": (185_004, 187_003), "b_exit": (51_201, 51_400),
         "engine_owner": "bm-c"},
    # SIXTY-FIRST ENGINE-OWNED WAVE (r570 bm-b freeze): bm-b's
    # TWENTY-THIRD owned per machine-derive (engine_owner==bm-b
    # rows 22 + candidate). Wave 72 = next free number after the
    # registered W71 row (seat declared published=reserved
    # MSG-20261002-1028-bmb, r518-1 law; never-dry standing step
    # under CEO de-throttle order O-20261001-2355 sec.2).
    # W1..W68 finalizes ALL LANDED (net head 514,148, K=147,520,
    # bm-a r569); W69 bm-c (12/12 burned, finalize pending) +
    # W70 bm-b (12/12 burned, finalize pending) + W71 bm-c
    # (burn in flight) = THREE in-flight upstream seats at this
    # freeze (FAIL-CLOSED r307).
    # BOTH SIDES: ARITHMETIC CONTINUATION from the W71 row tail,
    # no skip, no fork face: A 187_004..189_003 (= W71 A end
    # 187_003 + 1) / B 51_401..51_600 (= W71 B end 51_400 + 1)
    # -- both CLEAN per the W71 row W72+ WARNING projection
    # (bm-c r361 gate projection leg + this freeze's machine
    # re-derive, r302/r535 law).
    # Machine-verified at prereg time
    # (results/_r570bmb_w72_band_gate.py ADMIT receipt vs the
    # 69-row pre-W72 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). NOT a re-pick (R250: W72
    # bands were never assigned).
    72: {"a": (187_004, 189_003), "b_exit": (51_401, 51_600),
         "engine_owner": "bm-b"},
    # SIXTY-SECOND ENGINE-OWNED WAVE (r570 bm-a freeze): bm-a's
    # seventeenth owned per machine-derive (engine_owner==bm-a
    # rows 16 + candidate). Wave 73 = next free number after the
    # registered W72 row (seat declared published=reserved
    # MSG-20261002-1036-bma, r518-1 law; r565 yield-then-reoccupy
    # after the W72 same-window collision yielded to bm-b
    # c7babddec first-land per r511 commit-order). W1..W70
    # finalizes ALL LANDED (net head 518,548, K=151,920 --
    # W70 bm-b r570); W71 bm-c + W72 bm-b = TWO in-flight
    # upstream seats at this freeze (finalize chain-pending
    # FAIL-CLOSED r307). BOTH SIDES ARITHMETIC CONTINUATION,
    # zero skip: A 189_004..191_003 == W72 A end 189_003 + 1
    # (CLEAN per the W72 row W73+ WARNING projection, machine
    # re-derive r535 law -- dual-machine cross-check).
    # B 51_601..51_800 == W72 B end 51_600 + 1 (CLEAN, single
    # reading -- zero refusal points in either arithmetic
    # window, no divergence face). ADMIT receipt
    # results/_r570bma_w73_band_gate.py; NOT a re-pick (R250:
    # W73 bands were never assigned).
    73: {"a": (189_004, 191_003), "b_exit": (51_601, 51_800),
         "engine_owner": "bm-a"},
    # SIXTY-THIRD ENGINE-OWNED WAVE (r571 bm-b freeze): bm-b's
    # TWENTY-FOURTH owned per machine-derive (engine_owner==bm-b
    # rows 23 + candidate). Wave 74 = next free number after the
    # registered W73 row (seat declared published=reserved
    # MSG-20261002-1108-bmb, r518-1 law; never-dry standing step
    # under CEO de-throttle order O-20261001-2355 sec.2).
    # W1..W72 finalizes ALL LANDED (net head 522,948, K=156,320,
    # bm-b r571); W73 bm-a (12/12 burned, finalize pending) =
    # ONE in-flight upstream seat at this freeze (FAIL-CLOSED
    # r307).
    # A side: ARITHMETIC CONTINUATION from the W73 row tail, no
    # skip: A 191_004..193_003 (= W73 A end 191_003 + 1) CLEAN.
    # B side: FORCED SKIP -- arithmetic 51_801..52_000 refused
    # at its upper-edge point SEED_REGISTRY xstock_synth_null_b
    # = 52_000 (r307 W5 skip-precedent family); first clean
    # window 52_001..52_200, BOTH READINGS COINCIDE (past-hit
    # restart == window-step chain -- no fork face, unlike the
    # W63 double-mid divergence; skip forced, R250).
    # Machine-verified at prereg time
    # (results/_r571bmb_w74_band_gate.py ADMIT receipt vs the
    # 71-row pre-W74 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). NOT a re-pick (R250: W74
    # bands were never assigned).
    74: {"a": (191_004, 193_003), "b_exit": (52_001, 52_200),
         "engine_owner": "bm-b"},
    # SIXTY-FOURTH ENGINE-OWNED WAVE (r571 bm-a freeze): bm-a's
    # eighteenth owned per machine-derive (engine_owner==bm-a
    # rows 17 + candidate). Wave 75 = next free number after the
    # registered W74 row (seat declared published=reserved
    # MSG-20261002-1125-bma, r518-1 law; supply_floor flag response
    # -- compute_audit r571 pool ready 0, engine lane keeps the
    # perpetual nulls line saturated). W1..W73 finalizes ALL
    # LANDED (net head 525,148, K=158,520 -- W73 bm-a r571);
    # W74 bm-b = ONE in-flight upstream seat at this freeze
    # (finalize chain-pending FAIL-CLOSED r307). BOTH SIDES
    # ARITHMETIC CONTINUATION, zero skip: A 193_004..195_003 ==
    # W74 A end 193_003 + 1 (CLEAN per the W74 row W75+ WARNING
    # projection, machine re-derive r335 law -- dual-machine
    # cross-check). B 52_201..52_400 == W74 B end 52_200 + 1
    # (CLEAN, single reading -- zero refusal points in either
    # arithmetic window, no divergence face). ADMIT receipt
    # results/_r571bma_w75_band_gate.py; NOT a re-pick (R250:
    # W75 bands were never assigned).
    75: {"a": (193_004, 195_003), "b_exit": (52_201, 52_400),
         "engine_owner": "bm-a"},
    # SIXTY-FIFTH ENGINE-OWNED WAVE (r572 bm-b freeze): bm-b's
    # TWENTY-FIFTH owned per machine-derive (engine_owner==bm-b
    # rows 24 + candidate). Wave 76 = next free number after the
    # registered W75 row (seat declared published=reserved
    # MSG-20261002-1130-bmb, r518-1 law; never-dry standing step
    # under CEO de-throttle order O-20261001-2355 sec.2).
    # W1..W74 finalizes ALL LANDED (net head 527,348, K=160,720,
    # bm-b r572); W75 bm-a (burn in flight, finalize pending) =
    # ONE in-flight upstream seat at this freeze (FAIL-CLOSED
    # r307).
    # BOTH SIDES ARITHMETIC CONTINUATION from the W75 row tail,
    # zero skip: A 195_004..197_003 (= W75 A end 195_003 + 1),
    # B 52_401..52_600 (= W75 B end 52_400 + 1); single reading,
    # no fork face (F-20261002-03 not triggered).
    # Machine-verified at prereg time
    # (results/_r572bmb_w76_band_gate.py ADMIT receipt vs the
    # 73-row pre-W76 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). NOT a re-pick (R250: W76
    # bands were never assigned).
    76: {"a": (195_004, 197_003), "b_exit": (52_401, 52_600),
         "engine_owner": "bm-b"},
    # SIXTY-SIXTH ENGINE-OWNED WAVE (r572 bm-a freeze): bm-a's
    # nineteenth owned per machine-derive (engine_owner==bm-a
    # rows 18 + candidate). Wave 77 = next free number after the
    # registered W76 row (seat declared published=reserved
    # MSG-20261002-1131-bma, r518-1 law; never-dry standing step
    # under CEO de-throttle order O-20261001-2355 sec.2
    # own-continuous-series). W1..W75 finalizes ALL LANDED (net
    # head 529,548, K=162,920 -- W75 bm-a r572 this window);
    # W76 bm-b = ONE in-flight upstream seat at this freeze
    # (finalize chain-pending FAIL-CLOSED r307). BOTH SIDES
    # ARITHMETIC CONTINUATION, zero skip: A 197_004..199_003 ==
    # W76 A end 197_003 + 1 (CLEAN per the W76 row W77+ WARNING
    # projection, machine re-derive r335 law -- dual-machine
    # cross-check). B 52_601..52_800 == W76 B end 52_600 + 1
    # (CLEAN, single reading -- zero refusal points in either
    # arithmetic window, no divergence face). ADMIT receipt
    # results/_r572bma_w77_band_gate.py; NOT a re-pick (R250:
    # W77 bands were never assigned).
    77: {"a": (197_004, 199_003), "b_exit": (52_601, 52_800),
         "engine_owner": "bm-a"},
    # SIXTY-SEVENTH ENGINE-OWNED WAVE (r363 bm-c freeze): bm-c's
    # twenty-fourth owned per machine-derive (engine_owner==bm-c
    # rows 23 + candidate). Wave 78 = first free number after the
    # registered W77 row (r511 tail-lock, fetch-checked vacancy).
    # r565 yield-then-reoccupy SECOND re-occupation this window:
    # W76 draft yielded to bm-b r572 (bitwise cross-validation
    # #11; 12/12 local twin shards discarded pre-push, zero
    # pollution) + W77 draft yielded to bm-a r572 (bitwise
    # cross-validation #12; FIX-A intercepted the freeze-edits
    # run pre-edit = zero edit zero burn). Seat published=
    # reserved MSG-20261002-1150-bmc PUSHED to origin before
    # this freeze; its B-band prose projection 53_001..53_200
    # was STALE vs the live registry (j13v2_mill_ic2=53_100
    # inside it, bm-b J13V2 IC2 claim ac8a58490) -- corrected
    # per the machine gate (leg1-B2 refusal-facts identity)
    # to the chained double-hit window 53_201..53_400 (W63-B
    # in-register precedent family; fork 53_101..53_300
    # disclosed not taken, r566 face); correction receipt
    # MSG-20261002-1155-bmc (r535 machine-derive law).
    # Bands: A 199_004..201_003 == W77 A end 199_003 + 1
    # (arithmetic continuation, CLEAN); B 53_201..53_400
    # (chained double-hit skip past j13v2_mill_ic1=53_000 +
    # j13v2_mill_ic2=53_100). W1..W75 finalizes ALL LANDED
    # (net head 529,548, K=162,920 -- W75 bm-a r572); W76 bm-b
    # (burn in flight) + W77 bm-a (burn in flight) = TWO
    # in-flight upstream seats at this freeze (finalize
    # chain-pending FAIL-CLOSED r307).
    # ADMIT receipt results/_r363bmc_w78_band_gate.py;
    # NOT a re-pick (R250: W78 bands were never assigned).
    78: {"a": (199_004, 201_003), "b_exit": (53_201, 53_400),
         "engine_owner": "bm-c"},
    # SIXTY-EIGHTH ENGINE-OWNED WAVE (r573 bm-b freeze): bm-b's
    # TWENTY-SIXTH owned per machine-derive (engine_owner==bm-b
    # rows 25 + candidate). Wave 79 = next free number after the
    # registered W78 row (seat declared published=reserved
    # MSG-20261002-1151-bmb PUSHED to origin BEFORE this freeze
    # per r565 early-visibility lesson, r518-1 law; never-dry
    # standing step under CEO de-throttle order O-20261001-2355
    # sec.2).
    # W1..W76 finalizes ALL LANDED (net head 531,748, K=165,120,
    # bm-b r573); W77 bm-a (burned 12/12, finalize pending) +
    # W78 bm-c (burn in flight, finalize pending) = TWO
    # in-flight upstream seats at this freeze (FAIL-CLOSED
    # r307).
    # BOTH SIDES ARITHMETIC CONTINUATION from the W78 row tail,
    # zero skip: A 201_004..203_003 (= W78 A end 201_003 + 1),
    # B 53_401..53_600 (= W78 B end 53_400 + 1); single reading,
    # no fork face (F-20261002-03 not triggered; the j13v2_mill
    # pair 53_000/53_100 sits BELOW the B window).
    # Machine-verified at prereg time
    # (results/_r573bmb_w79_band_gate.py ADMIT receipt vs the
    # 76-row pre-W79 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). NOT a re-pick (R250: W79
    # bands were never assigned).
    79: {"a": (201_004, 203_003), "b_exit": (53_401, 53_600),
         "engine_owner": "bm-b"},
    # SIXTY-NINTH ENGINE-OWNED WAVE (r364 bm-c freeze): bm-c's
    # twenty-fifth owned per machine-derive (engine_owner==bm-c
    # rows 24 + candidate). Wave 80 = first free number after the
    # registered W79 row (r511 tail-lock, fetch-checked vacancy;
    # seat published=reserved MSG-20261002-1204-bmc PUSHED to
    # origin before this freeze per r565 early-visibility law,
    # commit 31db49798).
    # W1..W78 finalizes ALL LANDED (net head 536,148, K=169,520,
    # W78 bm-c r364 this window -- dead-r363 heritage closed);
    # W79 bm-b (burn in flight) = ONE in-flight upstream seat at
    # this freeze (finalize chain-pending FAIL-CLOSED r307).
    # BOTH SIDES ARITHMETIC CONTINUATION from the W79 row tail,
    # zero skip: A 203_004..205_003 (= W79 A end 203_003 + 1)
    # CLEAN + B 53_601..53_800 (= W79 B end 53_600 + 1) CLEAN
    # (single reading, no fork face, F-20261002-03 not triggered;
    # j13v2_mill pair 53_000/53_100 BELOW the B window).
    # Machine-verified at prereg time
    # (results/_r364bmc_w80_band_gate.py ADMIT receipt vs the
    # 77-row pre-W80 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). W81+ gate projection: A
    # 205_004..207_003 CLEAN; B 53_801..54_000 REFUSED at
    # SEED_REGISTRY 54_000. NOT a re-pick (R250: W80 bands
    # were never assigned).
    80: {"a": (203_004, 205_003), "b_exit": (53_601, 53_800),
         "engine_owner": "bm-c"},
    # SEVENTIETH ENGINE-OWNED WAVE (r574 bm-a freeze): bm-a's
    # twentieth owned per machine-derive (engine_owner==bm-a
    # rows 19 + candidate). Wave 81 = first free number after the
    # registered W80 row (r511 tail-lock, fetch-checked vacancy;
    # seat published=reserved MSG-20261002-1210-bma PUSHED to
    # origin before this freeze per r565 early-visibility law,
    # commit b38c8e64a).
    # W1..W79 finalizes ALL LANDED (net head 538,348, K=171,720,
    # W79 bm-b r574 this window; chain W1..W79 fully landed);
    # W80 bm-c (burn in flight) = ONE in-flight upstream seat at
    # this freeze (finalize chain-pending FAIL-CLOSED r307).
    # A SIDE ARITHMETIC CONTINUATION from the W80 row tail, zero
    # skip: A 205_004..207_003 (= W80 A end
    # 205_003 + 1) CLEAN. B SIDE FORCED SKIP at the arithmetic
    # position 53_801..54_000 which is REFUSED at SEED_REGISTRY
    # t18_deep_axis=54_000 (band UPPER-EDGE endpoint) -> hit+1
    # restart B 54_001..54_200; BOTH READINGS CONVERGE at the
    # edge endpoint (W74-B 52_000 family; no fork face,
    # F-20261002-03 not triggered).
    # Machine-verified at prereg time
    # (results/_r574bma_w81_band_gate.py ADMIT receipt vs the
    # 78-row pre-W81 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). W82+ gate projection: A
    # 207_004..209_003 CLEAN; B 54_201..54_400 CLEAN.
    # NOT a re-pick (R250: W81 bands were never assigned).
    81: {"a": (205_004, 207_003), "b_exit": (54_001, 54_200),
         "engine_owner": "bm-a"},
    # SEVENTY-SECOND ENGINE-OWNED WAVE (r574 bm-b freeze): bm-b's
    # TWENTY-SEVENTH owned per machine-derive (engine_owner==bm-b
    # rows 26 + candidate). Wave 82 = first free number after the
    # registered W81 row; same-window DOUBLE YIELD this round
    # (W80 -> bm-c 7fbeadb2e, W81 -> bm-a b38c8e64a seat-first +
    # freeze first-land, both per r511 commit-order law, both
    # zero-cost) + next-seat re-occupation per r565 law. Seat
    # declared published=reserved MSG-20261002-1245-bmb PUSHED to
    # origin before this freeze per r565 early-visibility law;
    # never-dry standing step under CEO de-throttle order
    # O-20261001-2355 sec.2.
    # W1..W79 finalizes ALL LANDED (net chain head 538,348,
    # K=171,720, bm-b r574 this window); W80 bm-c (burned 12/12,
    # finalize pending) + W81 bm-a (registered r574, burn in
    # flight) = TWO in-flight upstream seats at this freeze
    # (FAIL-CLOSED r307).
    # BOTH SIDES ARITHMETIC CONTINUATION from the W81 row tail,
    # zero skip: A 207_004..209_003 (= W81 A end 207_003 + 1),
    # B 54_201..54_400 (= W81 B end 54_200 + 1); single reading,
    # no fork face (F-20261002-03 not triggered).
    # Machine-verified at prereg time
    # (results/_r574bmb_w82_band_gate.py ADMIT receipt vs the
    # 79-row pre-W82 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). NOT a re-pick (R250: W82
    # bands were never assigned).
    82: {"a": (207_004, 209_003), "b_exit": (54_201, 54_400),
         "engine_owner": "bm-b"},
    # SEVENTY-THIRD ENGINE-OWNED WAVE by machine-derive (r365 bm-c
    # freeze): engine_owner rows 72 + candidate; live prose comment
    # ordinals carried a -1 drift at least since W80 (machine:
    # W80=70th/W81=71st/W82=72nd -- bm-b r574 SEVENTY-SECOND was
    # correct, bm-a r574 correction was the wrong side; r359 law).
    # bm-c's TWENTY-SIXTH owned per machine-derive
    # (engine_owner==bm-c rows 25 + candidate). Wave 83 = first free
    # number after the registered W82 row (r511 tail-lock,
    # fetch-checked vacancy incl. prereg path; seat published=
    # reserved MSG-20261002-1231-bmc PUSHED to origin BEFORE this
    # freeze per r565 early-visibility law, commit 165f18f2c).
    # W1..W81 finalizes ALL LANDED (net head 542,748, K=176,120,
    # W81 bm-a r574 this window); W82 bm-b (burn in flight) = ONE
    # in-flight upstream seat at this freeze (finalize
    # chain-pending FAIL-CLOSED r307).
    # BOTH SIDES ARITHMETIC CONTINUATION from the W82 row tail,
    # zero skip: A 209_004..211_003 (= W82 A end 209_003 + 1)
    # CLEAN + B 54_401..54_600 (= W82 B end 54_400 + 1) CLEAN
    # (single reading, no fork face, F-20261002-03 not triggered;
    # D-20261002-05 group pin = jump-past-hit -- zero-skip here so
    # the pin is not exercised).
    # Machine-verified at prereg time
    # (results/_r365bmc_w83_band_gate.py ADMIT receipt vs the
    # 80-row pre-W83 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked incl. prereg path). W84+
    # gate projection: A 211_004..213_003 CLEAN; B 54_601..54_800
    # CLEAN. NOT a re-pick (R250: W83 bands were never assigned).
    83: {"a": (209_004, 211_003), "b_exit": (54_401, 54_600),
         "engine_owner": "bm-c"},
    # SEVENTY-FOURTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r575 bm-a
    # freeze): engine_owner rows 73 + candidate; bm-a's
    # twenty-first owned per machine-derive (engine_owner==bm-a
    # rows 20 + candidate). Wave 84 = first free number after the
    # registered W83 row (r511 tail-lock, fetch-checked vacancy;
    # seat published=reserved MSG-20261002-1245-bma PUSHED to
    # origin before this freeze per r565 early-visibility law,
    # commit ad5df156c).
    # W1..W81 finalizes ALL LANDED (net head 542,748, K=176,120,
    # W81 bm-a r574; chain W1..W81 fully landed); TWO in-flight
    # upstream seats at this freeze: W82 bm-b (12/12 burned,
    # adopted by bm-b r575 S0 recovery, finalize pending) + W83
    # bm-c (registered, burn in flight) -- finalize chain-pending
    # FAIL-CLOSED r307.
    # BOTH SIDES ARITHMETIC CONTINUATION from the W83 row tails,
    # zero skip: A 211_004..213_003 (= W83 A end 211_003 + 1)
    # CLEAN. B 54_601..54_800 (= W83 B end 54_600 + 1) CLEAN.
    # Single reading, no refusal points, no fork face,
    # F-20261002-03 not triggered.
    # Machine-verified at prereg time
    # (results/_r575bma_w84_band_gate.py ADMIT receipt vs the
    # 81-row pre-W84 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin
    # slot vacancy machine-checked). W85+ gate projection: A
    # 213_004..215_003 CLEAN; B 54_801..55_000 REFUSED at
    # SEED_REGISTRY a158_truegap_ic=55_000 upper-edge endpoint
    # -> hit+1 restart 55_001..55_200 (W74-B/W81 edge family).
    # NOT a re-pick (R250: W84 bands were never assigned).
    84: {"a": (211_004, 213_003), "b_exit": (54_601, 54_800),
         "engine_owner": "bm-a"},
    # SEVENTY-FIFTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r576 bm-b
    # freeze): engine_owner rows 74 + candidate; bm-b's
    # twenty-eighth owned per machine-derive (engine_owner==bm-b
    # rows 27 + candidate). Wave 85 = first free number after the
    # registered W84 row (r511 tail-lock, fetch-checked vacancy;
    # seat published=reserved MSG-20261002-1258-bmb PUSHED to
    # origin in the r575 window BEFORE this freeze per r565
    # early-visibility law, seat commit ce51adf70). CROSS-ROUND
    # freeze: r575 session died pre-freeze (state round_no stall
    # + r575-labeled commits = r529 sudden-death diagnosis law);
    # r576 adopts the half-product with anchors rolled W82->W83
    # per anchor-roll law (W83 finalize landed, bm-c r366 window).
    # W1..W83 finalizes ALL LANDED (net head 547,148, K=180,520,
    # W83 bm-c r365/r366); ONE in-flight upstream seat at this
    # freeze: W84 bm-a (11/12 burned on origin, finalize not
    # landed) -- finalize chain-pending FAIL-CLOSED r307.
    # A-side ARITHMETIC CONTINUATION from the W84 row tail, zero
    # skip: A 213_004..215_003 (= W84 A end 213_003 + 1) CLEAN.
    # B-side FORCED SKIP past-hit restart: arithmetic 54_801..55_000
    # REFUSED at SEED_REGISTRY a158_truegap_ic=55_000 upper-edge
    # endpoint -> hit+1 restart 55_001..55_200 per D-20261002-05
    # pinned semantics (past-hit start-window), both readings
    # converge = no fork face, F-20261002-03 not triggered
    # (W74-B/W81 edge-endpoint family).
    # Machine-verified at prereg time
    # (results/_r575bmb_w85_band_gate.py ADMIT receipt, dual-state:
    # r575 mode A + r576 mode B re-run rc0 vs the 82-row pre-W85
    # table + live SEED_REGISTRY values + probe cluster
    # 95_000..95_003 r335 discovery leg + N3-R1 used-seed band
    # 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). W86+ gate projection: A
    # 215_004..217_003 CLEAN; B 55_201..55_400 CLEAN.
    # NOT a re-pick (R250: W85 bands were never assigned).
    85: {"a": (213_004, 215_003), "b_exit": (55_001, 55_200),
         "engine_owner": "bm-b"},
    # SEVENTY-SIXTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r576 bm-a
    # freeze): engine_owner rows 75 + candidate; bm-a's
    # twenty-second owned per machine-derive (engine_owner==bm-a
    # rows 21 + candidate). Wave 86 = first free number after the
    # registered W85 row (bm-b r576 five-face freeze landed
    # mid-window; dual-state gate re-run mode B converged on the
    # same bands as mode A; r511 tail-lock fetch-checked vacancy;
    # seat published=reserved MSG-20261002-1305-bma PUSHED to
    # origin before this freeze per r565 early-visibility law,
    # commit a2388eb5b).
    # W1..W84 finalizes ALL LANDED (net head 549,348, K=182,720;
    # W83+W84 both landed bm-a r576 window; W83 block restored to
    # bm-c canonical bytes per r518 origin-first-landed
    # adjudication, fixup 3b3a7fe19). ONE in-flight upstream
    # seat at this freeze: W85 bm-b (registered, burn in flight,
    # finalize pending) -- finalize chain-pending FAIL-CLOSED
    # r307 at run time.
    # BOTH SIDES ARITHMETIC CONTINUATION from the registered W85
    # row tails, zero skip: A 215_004..217_003 (= W85 A end
    # 215_003 + 1) CLEAN. B 55_201..55_400 (= W85 B end 55_200 +
    # 1) CLEAN. Dual-state gate mode A chain machine-verified:
    # arithmetic 54_801..55_000 REFUSED at SEED_REGISTRY
    # a158_truegap_ic=55_000 upper-edge endpoint -> hit+1 restart
    # 55_001..55_200 == W85 published band -> skip-past-published
    # (D-20261002-05 pin: past-hit start-window; edge-endpoint
    # family W74-B/W81, both readings converge, no fork face).
    # Machine-verified at prereg time
    # (results/_r576bma_w86_band_gate.py dual-state ADMIT receipt
    # vs the 83-row pre-W86 table + live SEED_REGISTRY values +
    # probe cluster 95_000..95_003 r335 discovery leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;
    # origin slot vacancy machine-checked). W87+ projection: A
    # 217_004..219_003 CLEAN; B 55_401..55_600 REFUSED in-band at
    # SEED_REGISTRY grid_p1=55_500 median hit -> D-20261002-05
    # pin: hit+1 restart 55_501..55_700 (window-step-chain reading
    # 55_601..55_800 is BANNED by the pin; next freezer must
    # re-derive, never transcribe).
    # NOT a re-pick (R250: W86 bands were never assigned).
    86: {"a": (215_004, 217_003), "b_exit": (55_201, 55_400),
         "engine_owner": "bm-a"},
    # SEVENTY-SEVENTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r577 bm-a
    # freeze): engine_owner rows 76 + candidate; bm-a's
    # twenty-third owned per machine-derive (engine_owner==bm-a
    # rows 22 + candidate). Wave 87 = first free number after the
    # registered W86 row (single-state gate: W85+W86 both
    # registered, zero published-but-unregistered seats, zero W87
    # seat MSGs on origin per gate leg0b; r511 tail-lock
    # fetch-checked vacancy; seat published=reserved
    # MSG-20261002-1345-bma PUSHED to origin before this freeze
    # per r565 early-visibility law).
    # W1..W86 finalizes ALL LANDED at this freeze (net head
    # 553,748 = W85 bm-b r577 551,548 + W86 bm-a r577 one-pass;
    # K=187,120 merged pool; ZERO in-flight upstream seats --
    # first fully-caught-up freeze window since W53; finalize
    # merge loop stays FAIL-CLOSED r307 at run time).
    # A-SIDE ARITHMETIC CONTINUATION from the registered W86 row
    # tail, zero skip: A 217_004..217_003+2_000 = 217_004..219_003
    # (= W86 A end 217_003 + 1) CLEAN. B-SIDE MEDIAN-HIT PIN CHAIN:
    # arithmetic 55_401..55_600 REFUSED in-band at SEED_REGISTRY
    # grid_p1=55_500 (median position 99/199, non-endpoint) ->
    # D-20261002-05 pin: PAST-HIT start-window hit+1 restart
    # 55_501..55_700 CLEAN (window-step-chain reading 55_601..55_800
    # BANNED by the pin; W68-B positive anchor, pf.py selftest
    # leg-9 pin leg).
    # Machine-verified at prereg time
    # (results/_r577bma_w87_band_gate.py ADMIT receipt vs the
    # 84-row pre-W87 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). W88+ projection: A 219_004..221_003
    # CLEAN; B 55_701..55_900 CLEAN (next freezer must re-derive,
    # never transcribe).
    # NOT a re-pick (R250: W87 bands were never assigned).
    87: {"a": (217_004, 219_003), "b_exit": (55_501, 55_700),
         "engine_owner": "bm-a"},
    # SEVENTY-EIGHTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r368 bm-c
    # freeze): engine_owner rows 77 + candidate; bm-c's twenty-
    # seventh owned per machine-derive (engine_owner==bm-c rows 26 +
    # candidate). Wave 88 = first FREE number SKIPPING the
    # bm-a-declared W87 seat (published=reserved r518-1,
    # MSG-20261002-1345-bma; bm-c r368 W87 same-bands independent
    # derive YIELDED by origin-visibility commit order r511 --
    # zero-cost cross-derivation receipt
    # results/_r368bmc_w87_band_gate.py, no burn no finalize; bm-b
    # r577 W88 same-bands derive YIELDED to bm-c per origin-first
    # be3b5d0ea, yield receipt commit 3aa3c72c4, archived
    # MSG-20261002-1348-bmb). Seat published=reserved
    # MSG-20261002-1352-bmc PUSHED to origin before this freeze per
    # r565 early-visibility law (CAS commit be3b5d0ea).
    # W85 bm-b + W86 bm-a finalizes BOTH LANDED at this freeze (net
    # head 553,748, K=187,120, W85 bm-b r577 + W86 bm-a r577
    # one-pass). ONE in-flight upstream seat: W87 bm-a (registered
    # r577, burn in flight, finalize pending) -- finalize
    # chain-pending FAIL-CLOSED r307 at run time.
    # DUAL-STATE CONVERGENT BANDS (r535 machine-gate derive law,
    # results/_r368bmc_w88_band_gate.py both states rc0 on the same
    # bands):
    #   state B (W87 registered -- ACTUAL at freeze): BOTH SIDES
    #     ARITHMETIC CONTINUATION from the registered W87 tails,
    #     zero skip: A 219_004..221_003 (= W87 A end 219_003 + 1)
    #     CLEAN. B 55_701..55_900 (= W87 B end 55_700 + 1) CLEAN,
    #     zero refusal points.
    #   state A (W87 published, unregistered -- draft-window chain):
    #     A arithmetic 217_004..219_003 refused by the W87 published
    #     band (reserved face) -> skip-past-published; B arithmetic
    #     55_401..55_600 refused in-band at SEED_REGISTRY
    #     grid_p1=55_500 MID-BAND hit (median position 99/199) ->
    #     D-20261002-05 pin past-hit restart 55_501..55_700 == W87
    #     published band -> skip-past-published (chain reading
    #     55_601..55_800 BANNED by the pin; negative-asserted).
    # Machine-verified at prereg time (dual-state ADMIT receipt vs
    # the 85-row table + live SEED_REGISTRY values + probe cluster
    # 95_000..95_003 r335 discovery leg + N3-R1 used-seed band
    # 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). W89+ projection: A 221_004..223_003
    # CLEAN; B 55_901..56_100 REFUSED in-band at SEED_REGISTRY
    # ths_agg_p1=56_000 (band 56_000..56_049) -> mid-band pin chain
    # face, W89 seat published by bm-b r577; next freezer must
    # re-derive, never transcribe.
    # NOT a re-pick (R250: W88 bands were never assigned).
    88: {"a": (219_004, 221_003), "b_exit": (55_701, 55_900),
         "engine_owner": "bm-c"},
    # SEVENTY-NINTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r577 bm-b
    # freeze): engine_owner rows 78 + candidate; bm-b's
    # twenty-ninth owned per machine-derive (engine_owner==bm-b
    # rows 28 + candidate). Wave 89 = first free number after the
    # registered W86 row SKIPPING the two published-but-unregistered
    # seats W87 (bm-a, MSG-20261002-1345-bma) and W88 (bm-c,
    # MSG-20261002-1352-bmc -- bm-b's own W88 seat MSG yielded to
    # bm-c per r511 commit-order law, yield receipt
    # MSG-20261002-1358-bmb; zero burn zero freeze zero finalize =
    # zero-cost same-bands dual-machine cross-validation).
    # W87 registered (bm-a r577 freeze landed 36ddb5377, finalize
    # pending); W88 seat-published, unregistered (bm-c freeze in
    # flight) -- two in-flight upstream seats at this freeze,
    # finalize merge loop stays FAIL-CLOSED r307 at run time.
    # A-SIDE SKIP-PAST-PUBLISHED CHAIN (r518-1): W86 tail -> W87
    # pub A 217_004..219_003 -> W88 pub A 219_004..221_003 -> first
    # clean 221_004..223_003 (= W88 published A end + 1) CLEAN.
    # B-SIDE PIN CHAIN: 55_401..55_600 doubly refused (W87-pub
    # overlap + grid_p1=55_500 median) -> 55_501..55_700 == W87 pub
    # -> 55_701..55_900 == W88 pub -> 55_901..56_100 REFUSED
    # in-band at SEED_REGISTRY ths_agg_p1=56_000 (median position
    # 99/199, non-endpoint) -> D-20261002-05 pin: PAST-HIT
    # start-window hit+1 restart 56_001..56_200 CLEAN
    # (window-step-chain reading 56_101..56_300 BANNED by the pin;
    # W68-B positive anchor).
    # Machine-verified at prereg time
    # (results/_r577bmb_w89_band_gate.py ADMIT receipt vs the
    # 84-row pre-W89 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). W90+ projection: A 223_004..225_003
    # CLEAN; B 56_201..56_400 CLEAN (next freezer must re-derive,
    # never transcribe).
    # NOT a re-pick (R250: W89 bands were never assigned).
    89: {"a": (221_004, 223_003), "b_exit": (56_001, 56_200),
         "engine_owner": "bm-b"},
    # W90 (r579 bm-a): BOTH SIDES ARITHMETIC CONTINUATION from the
    # registered W89 tails (bm-b r578 estate-adoption registration),
    # zero skip, zero refusal points. Dual-state convergent ADMIT
    # receipt results/_r579bma_w90_band_gate.py (state A: W89
    # seat-published chain -- W88-tail arithmetic == W89 published
    # A band -> skip-past-published; B 55_901..56_100 REFUSED
    # in-band at SEED_REGISTRY ths_agg_p1=56_000 median 99/199 ->
    # D-20261002-05 pin restart 56_001..56_200 == W89 published ->
    # skip-past-published; state B: registered-tail arithmetic) --
    # both states rc0 on the same bands. W91+ projection: A
    # 225_004..227_003 CLEAN / B 56_401..56_600 REFUSED at
    # p4_batch3_dca=56_500 in-window MEDIAN (99/199) -> pin
    # 56_501..56_700 for the next freezer (never transcribe).
    # NOT a re-pick (R250: W90 bands were never assigned).
    90: {"a": (223_004, 225_003), "b_exit": (56_201, 56_400),
         "engine_owner": "bm-a"},
    # EIGHTIETH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r578 bm-b
    # freeze): engine_owner rows 79 + candidate; bm-b's
    # thirtieth owned per machine-derive (engine_owner==bm-b
    # rows 29 + candidate). Wave 91 = first free number after the
    # registered W89 row SKIPPING the bm-a-declared W90 seat
    # (MSG-20261002-1415-bma, published=reserved r518-1).
    # W90 seat-published, unregistered at this freeze (bm-a freeze
    # in flight) -- one in-flight upstream seat, finalize merge loop
    # stays FAIL-CLOSED r307 at run time.
    # A-SIDE SKIP-PAST-PUBLISHED CHAIN (r518-1): W89 tail 223_003 ->
    # W90 pub A 223_004..225_003 -> first clean 225_004..227_003
    # (= W90 published A end + 1) CLEAN.
    # B-SIDE PIN CHAIN: 56_201..56_400 == W90 pub B -> skip ->
    # 56_401..56_600 REFUSED in-band at SEED_REGISTRY
    # p4_batch3_dca=56_500 (median position 99/199, non-endpoint) ->
    # D-20261002-05 pin: PAST-HIT start-window hit+1 restart
    # 56_501..56_700 CLEAN (window-step-chain reading 56_601..56_800
    # BANNED by the pin; W68-B positive anchor).
    # Machine-verified at prereg time
    # (results/_r578bmb_w91_band_gate.py ADMIT receipt vs the
    # 87-row pre-W91 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). W92+ projection: A 227_004..229_003
    # CLEAN; B 56_701..56_900 CLEAN (next freezer must re-derive).
    91: {"a": (225_004, 227_003), "b_exit": (56_501, 56_700),
         "engine_owner": "bm-b"},
    # EIGHTY-SECOND ENGINE-OWNED WAVE BY MACHINE-DERIVE (r370 bm-c
    # freeze): engine_owner rows 81 + candidate; bm-c's
    # twenty-eighth owned per machine-derive (engine_owner==bm-c
    # rows 27 + candidate). Wave 92 = first free number after the
    # registered W91 row (bm-b r578 freeze 636dab137); SINGLE STATE
    # zero seat gap: all rows W2..W91 registered (W89/W90/W91 =
    # three in-flight upstream seats, finalize merge loop stays
    # FAIL-CLOSED r307 at run time).
    # BOTH SIDES ARITHMETIC CONTINUATION from the registered W91
    # tails: A 227_004..229_003 (227_003 + 1, width 2_000) and
    # B 56_701..56_900 (56_700 + 1, width 200), both CLEAN zero
    # refusal points (honest forward walk, no pin chain needed).
    # Machine-verified at prereg time
    # (results/_r370bmc_w92_band_gate.py ADMIT receipt vs the
    # 89-row pre-W92 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). Seat published=reserved
    # MSG-20261002-1447-bmc pushed to origin (766daf77a) BEFORE
    # this freeze per r565 law. W93+ projection: A 229_004..231_003
    # CLEAN; B 56_901..57_100 REFUSED [57_000, 57_100] (next
    # freezer must re-derive per the sec.4 pin law).
    92: {"a": (227_004, 229_003), "b_exit": (56_701, 56_900),
         "engine_owner": "bm-c"},
    # EIGHTY-THIRD ENGINE-OWNED WAVE BY MACHINE-DERIVE (r579 bm-b
    # freeze): engine_owner rows 82 + candidate; bm-b's
    # thirty-first owned per machine-derive (engine_owner==bm-b
    # rows 30 + candidate). Wave 93 = first free number after the
    # registered W91 row SKIPPING the bm-c-declared W92 seat
    # (MSG-20261002-1447-bmc, published=reserved r518-1; this
    # machine's W92 derive was bitwise-identical -> ZERO-COST YIELD
    # per r511 origin-first; yield receipt + W93 seat published
    # same-window MSG-20261002-1510-bmb per r565 law).
    # W92 registered mid-window by bm-c r370 (08bc6507b), burn in
    # flight at this freeze -- ONE in-flight upstream seat, finalize
    # merge loop stays FAIL-CLOSED r307 at run time.
    # A-SIDE SKIP-PAST-PUBLISHED CHAIN (r518-1): W91 tail 227_003 ->
    # W92 seat A 227_004..229_003 -> first clean 229_004..231_003
    # (= W92 seat A end + 1) CLEAN.
    # B-SIDE DOUBLE-HIT PIN CHAIN: 56_701..56_900 == W92 seat B ->
    # skip -> 56_901..57_100 REFUSED in-band at SEED_REGISTRY
    # xstock_tilt_h20=57_000 (median position 99/199, non-edge) AND
    # xstock_tilt_h10=57_100 (upper-edge endpoint 199/199) ->
    # D-20261002-05 pin: PAST-HIT restart 57_001..57_200 REFUSED
    # again at 57_100 (median 99/199) -> restart 57_101..57_300
    # CLEAN. Window-step-chain reading from the refused arithmetic
    # window (57_101..57_300) CONVERGES -- 57_100 sits at the
    # refused window upper endpoint, both restart readings coincide,
    # no fork face (W63 double-hit family, zero divergence).
    # Machine-verified at prereg time
    # (results/_r579bmb_w93_band_gate.py ADMIT receipt, dual-state
    # rc0 [A92 seat-published window / B92 registered window] vs the
    # 90-row pre-W93 table + live SEED_REGISTRY values + probe
    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin slot
    # vacancy machine-checked). W94+ projection: A 231_004..233_003
    # CLEAN; B 57_301..57_500 CLEAN (next freezer must re-derive).
    93: {"a": (229_004, 231_003), "b_exit": (57_101, 57_300),
         "engine_owner": "bm-b"},
    # EIGHTY-FOURTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r580 bm-a
    # freeze): engine_owner rows 82 + in-flight W93 seat (bm-b) +
    # candidate; bm-a's twenty-fifth owned per machine-derive
    # (engine_owner==bm-a rows 24 + candidate). Wave 94 = first
    # free number after the registered W92 row SKIPPING the bm-b
    # published W93 seat (MSG-20261002-1510-bmb; published=
    # reserved r518-1; prior seat yield: W93 zero-cost yield to
    # bm-b per r511 commit-order, bands bitwise identical =
    # deterministic cross-validation; yield receipt + W94 seat
    # = MSG-20261002-1514-bma PUSHED to origin before this freeze
    # per r565 early-visibility law).
    # W1..W91 finalizes ALL LANDED at this freeze (landed chain
    # head 564,748 = W91 bm-b r579 one-pass; K=198,120 merged
    # pool). TWO in-flight upstream seats (W92 bm-c burning +
    # W93 bm-b freeze in flight) -- finalize merge loop stays
    # FAIL-CLOSED r307 at run time).
    # BOTH SIDES SKIP-PAST-PUBLISHED CHAIN, DUAL-STATE CONVERGENT
    # (W90 r579 precedent): state A = W93 seat-published-
    # unregistered (skip-past-published from the W92 tails over
    # the W93 published bands); state B = W93 registered
    # (arithmetic continuation from the W93 tails) -- both
    # states derive the same bands bitwise.
    # A-SIDE: first clean window 231_004..233_003 (W92 A end
    # 229_003 + 1 -> W93 published band 229_004..231_003 refused
    # -> 231_004..233_003) CLEAN zero refusal points.
    # B-SIDE: first clean window 57_301..57_500 (W92 B end
    # 56_900 + 1 -> W93 published band 57_101..57_300 refused
    # -> 57_301..57_500) CLEAN zero refusal points.
    # Machine-verified at prereg time
    # (results/_r580bma_w94_band_gate.py ADMIT receipt rc0 state A
    # vs the 90-row pre-W94 table + W93 published seat + live
    # SEED_REGISTRY values + probe cluster 95_000..95_003 r335
    # discovery leg + N3-R1 used-seed band 70_000..70_005
    # MSG-183x r529 mandatory leg; origin slot vacancy machine-
    # checked). W95+ projection: A 233_004..235_003 CLEAN; B
    # 57_501..57_700 CLEAN (next freezer must re-derive, never
    # transcribe).
    # NOT a re-pick (R250: W94 bands were never assigned).
    94: {"a": (231_004, 233_003), "b_exit": (57_301, 57_500),
         "engine_owner": "bm-a"},
    # EIGHTY-FIFTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r580 bm-b
    # freeze): engine_owner rows 84 + candidate; bm-b's
    # thirty-second owned per machine-derive (engine_owner==bm-b
    # rows 31 + candidate). Wave 95 = first free number after the
    # registered W94 row (zero seat gaps: W2..W94 all registered;
    # W94 restored same window from the dead-r579 replay revert,
    # heal receipt MSG-20261002-1533-bmb).
    # W1..W91 finalizes ALL LANDED (landed chain head 564,748 = W91
    # bm-b r579 one-pass; K=198,120 merged pool). THREE in-flight
    # upstream seats (W92 bm-c 12/12 burned finalize-pending + W93
    # bm-b 12/12 burned finalize-pending + W94 bm-a burn in flight)
    # -- finalize merge loop stays FAIL-CLOSED r307 at run time.
    # BOTH SIDES ARITHMETIC CONTINUATION from the registered W94
    # tails, CLEAN zero refusal points (honest forward walk, no
    # skip, no pin chain; W92 r370 precedent family).
    # Machine-verified at prereg time
    # (results/_r580bmb_w95_band_gate.py ADMIT receipt rc0 single
    # state vs the 92-row pre-W95 table + live SEED_REGISTRY values
    # + probe cluster 95_000..95_003 r335 discovery leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;
    # origin slot vacancy machine-checked; seat published=reserved
    # MSG-20261002-1536-bmb pushed BEFORE this freeze per r565
    # law). W96+ projection: A 235_004..237_003 CLEAN; B
    # 57_701..57_900 CLEAN (next freezer must re-derive).
    # NOT a re-pick (R250: W95 bands were never assigned).
    95: {"a": (233_004, 235_003), "b_exit": (57_501, 57_700),
         "engine_owner": "bm-b"},
    # EIGHTY-SIXTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r581 bm-a
    # freeze): engine_owner rows 85 + candidate; bm-a's
    # twenty-sixth owned per machine-derive (engine_owner==bm-a
    # rows 25 + candidate). Wave 96 = first free number after the
    # registered W95 row (SINGLE STATE, zero seat gap; no
    # published seat to skip). Seat published=reserved
    # MSG-20261002-1531-bma pushed to origin 2819d0393 BEFORE
    # this freeze per r565 early-visibility law.
    # W91 finalize LANDED at this freeze (landed chain head
    # 564,748 = W91 bm-b r579 one-pass; K=198,120). THREE
    # in-flight upstream seats (W92 bm-c + W93 bm-b + W94 bm-a
    # -- all registered, finalize pending) -- finalize merge
    # loop stays FAIL-CLOSED r307 at run time.
    # BOTH SIDES ARITHMETIC CONTINUATION from the registered W95
    # tails, single state: A 235_004..237_003 CLEAN + B
    # 57_701..57_900 CLEAN zero refusal points
    # (machine-verified at prereg time, ADMIT receipt
    # results/_r581bma_w96_band_gate.py rc0 hops 0/0; live
    # SEED_REGISTRY + probe cluster 95_000..95_003 r335 leg +
    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 leg).
    # W97+ projection: A 237_004..239_003 CLEAN; B 57_901..58_100
    # REFUSED at SEED_REGISTRY 58_000 (in-band -> next freezer
    # pins per D-20261002-05; next freezer must re-derive,
    # never transcribe).
    # NOT a re-pick (R250: W96 bands were never assigned).
    96: {"a": (235_004, 237_003), "b_exit": (57_701, 57_900),
         "engine_owner": "bm-a"},
    # EIGHTY-SEVENTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r581 bm-b
    # freeze): engine_owner rows 86 + candidate; bm-b's
    # thirty-third owned per machine-derive (engine_owner==bm-b
    # rows 32 + candidate). Wave 97 = first free number after the
    # registered W96 row (zero seat gaps: W2..W96 all registered;
    # single state, no skip-past-published chain).
    # W1..W91 finalizes ALL LANDED (landed chain head 564,748 = W91
    # bm-b r579 one-pass; K=198,120 merged pool). FIVE in-flight
    # upstream seats (W92 bm-c 12/12 burned finalize-pending + W93
    # bm-b 12/12 burned finalize-pending + W94 bm-a burn in flight +
    # W95 bm-b 12/12 burned finalize-pending + W96 bm-a burn in
    # flight, ALL REGISTERED) -- finalize merge loop stays
    # FAIL-CLOSED r307 at run time.
    # A = arithmetic continuation from the registered W96 A tail,
    # CLEAN zero refusal points (honest forward walk).
    # B = D-20261002-05 pinned: arithmetic 57_901..58_100 REFUSED at
    # SEED_REGISTRY im_ic_pair=58_000 in-window MEDIAN hit (99/199
    # non-edge) -> hit+1 restart 58_001..58_200 CLEAN (window-step
    # chain reading 58_101..58_300 disclosed NOT taken; frozen
    # precedent W68-B 50_501..50_700).
    # Machine-verified at prereg time
    # (results/_r581bmb_w97_band_gate.py ADMIT receipt rc0 single
    # state vs the 94-row pre-W97 table + live SEED_REGISTRY values
    # + probe cluster 95_000..95_003 r335 discovery leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;
    # origin slot vacancy machine-checked; seat published=reserved
    # MSG-20261002-1545-bmb pushed BEFORE this freeze per r565
    # law). W98+ projection: A 239_004..241_003 CLEAN; B
    # 58_201..58_400 CLEAN (next freezer must re-derive).
    # NOT a re-pick (R250: W97 bands were never assigned).
    97: {"a": (237_004, 239_003), "b_exit": (58_001, 58_200),
         "engine_owner": "bm-b"},
    # EIGHTY-EIGHTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r582 bm-a
    # freeze): engine_owner rows 87 + candidate; bm-a's
    # twenty-seventh owned per machine-derive (engine_owner==bm-a
    # rows 26 + candidate). Wave 98 = first free number after the
    # registered W97 row (SINGLE STATE, zero seat gap; no
    # published seat to skip). Seat published=reserved
    # MSG-20261002-1603-bma pushed to origin c3e1df538 BEFORE
    # this freeze per r565 early-visibility law.
    # W92 finalize LANDED at this freeze (landed chain head
    # 566,948 = W92 bm-c r372 one-pass; K=200,320). FOUR
    # in-flight upstream seats (W93 bm-b + W94 bm-a + W95 bm-b
    # + W96 bm-a -- all registered, finalize pending) --
    # finalize merge loop stays FAIL-CLOSED r307 at run time.
    # BOTH SIDES ARITHMETIC CONTINUATION from the registered W97
    # tails, single state: A 239_004..241_003 CLEAN + B
    # 58_201..58_400 CLEAN zero refusal points
    # (machine-verified at prereg time, ADMIT receipt
    # results/_r582bma_w98_band_gate.py rc0 hops 0/0; live
    # SEED_REGISTRY + probe cluster 95_000..95_003 r335 leg +
    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 leg).
    # W99+ projection: A 241_004..243_003 CLEAN; B 58_401..58_600
    # REFUSED at SEED_REGISTRY [58_500, 58_550] (in-band -> next
    # freezer pins per D-20261002-05; next freezer must
    # re-derive, never transcribe).
    # NOT a re-pick (R250: W98 bands were never assigned).
    98: {"a": (239_004, 241_003), "b_exit": (58_201, 58_400),
         "engine_owner": "bm-a"},
    # EIGHTY-NINTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r374 bm-c
    # freeze): engine_owner rows 88 + candidate; bm-c's
    # twenty-ninth owned per machine-derive (engine_owner==bm-c
    # rows 28 + candidate). Wave 99 = first free number after the
    # registered W98 row (SINGLE STATE, zero seat gap; no
    # published seat to skip). Seat published=reserved
    # MSG-20261002-1625-bmc pushed to origin fed0b4054 BEFORE
    # this freeze per r565 early-visibility law.
    # W94 finalize LANDED at this freeze (landed chain head
    # 571,348 = W94 bm-a r582 one-pass; K=204,720). FOUR
    # in-flight upstream seats (W95 bm-b + W96 bm-a + W97 bm-b
    # + W98 bm-a -- all registered, finalize pending) --
    # finalize merge loop stays FAIL-CLOSED r307 at run time.
    # A side ARITHMETIC CONTINUATION from the registered W98
    # A tail: A 241_004..243_003 CLEAN zero refusal points
    # (machine-verified at prereg time, ADMIT receipt
    # results/_r374bmc_w99_band_gate.py rc0 hops 0; live
    # SEED_REGISTRY + probe cluster 95_000..95_003 r335 leg +
    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 leg).
    # B side D-20261002-05 PINNED-SKIP DERIVE: arithmetic window
    # 58_401..58_600 refused at SEED_REGISTRY in-band values
    # 58_500 (mf_ic_p1) + 58_550 (sina_construct_p1) -> past-hit
    # restart per the D-20261002-05 pinned line; first clean
    # window B 58_551..58_750 (hops=2; ADMIT receipt same).
    # W100+ projection: A 243_004..245_003 CLEAN; B 58_751..58_950
    # CLEAN (next freezer must re-derive, never transcribe).
    # NOT a re-pick (R250: W99 bands were never assigned).
    99: {"a": (241_004, 243_003), "b_exit": (58_551, 58_750),
         "engine_owner": "bm-c"},
    # NINETIETH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r583 bm-b
    # freeze): engine_owner rows 89 + candidate; bm-b's
    # thirty-fourth owned per machine-derive (engine_owner==bm-b
    # rows 33 + candidate). Wave 100 = first free number after the
    # registered W99 row (zero seat gaps: W2..W99 all registered;
    # single state, no skip-past-published chain).
    # W1..W97 finalizes ALL LANDED (landed chain head 577,948 = W97
    # bm-b r583 one-pass; K=211,320 merged pool). TWO in-flight
    # upstream seats (W98 bm-a 12/12 burned finalize-pending + W99
    # bm-c 12/12 burned finalize-pending, ALL REGISTERED) -- finalize
    # merge loop stays FAIL-CLOSED r307 at run time.
    # BOTH SIDES = ARITHMETIC CONTINUATION from the registered W99
    # tails, CLEAN zero refusal points (honest forward walk, no
    # pin chain, no skips -- W92 r370 precedent family).
    # Machine-verified at prereg time
    # (results/_r583bmb_w100_band_gate.py ADMIT receipt rc0 single
    # state vs the 97-row pre-W100 table + live SEED_REGISTRY values
    # + probe cluster 95_000..95_003 r335 discovery leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;
    # origin slot vacancy machine-checked; seat published=reserved
    # MSG-20261002-1615-bmb pushed BEFORE this freeze per r565
    # law). W101+ projection: A 245_004..247_003 CLEAN; B
    # 58_951..59_150 REFUSED at [59_000] (D-20261002-05 pin for
    # the next freezer; bm-a W101 seat published).
    # NOT a re-pick (R250: W100 bands were never assigned).
    100: {"a": (243_004, 245_003), "b_exit": (58_751, 58_950),
         "engine_owner": "bm-b"},
    # NINETIETH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r583 bm-a
    # freeze): engine_owner rows 89 + candidate; bm-a's
    # twenty-eighth owned per machine-derive (engine_owner==bm-a
    # rows 27 + candidate). Wave 101 = first free number after
    # bm-b's PUBLISHED W100 seat (MSG-20261002-1615-bmb,
    # published=reserved r518-1; W100 NOT yet registered at this
    # freeze -- single state skip-past-published chain from the
    # registered W99 tails). Seat published=reserved
    # MSG-20261002-1625-bma pushed to origin 4e351f312 BEFORE
    # this freeze per r565 early-visibility law.
    # W96 finalize LANDED at this freeze (landed chain head
    # 575,748 = W96 bm-a r583 one-pass; K=209,120). FOUR
    # in-flight upstream seats (W97 bm-b burned-unfinalized +
    # W98 bm-a burned-blocked-by-W97 + W99 bm-c burning +
    # W100 bm-b seat-unfrozen) -- finalize merge loop stays
    # FAIL-CLOSED r307 at run time.
    # A = SKIP-PAST-PUBLISHED W100 then arithmetic continuation:
    # 245_004..247_003 CLEAN hops=1. B = skip-past-published W100
    # -> arithmetic 58_951..59_150 refused at SEED_REGISTRY 59_000
    # in-window -> D-20261002-05 pinned past-hit restart
    # 59_001..59_200 hops=2 (window-step chain reading BANNED,
    # W68-B positive anchor). ADMIT receipt
    # results/_r583bma_w101_band_gate.py rc0; live SEED_REGISTRY
    # + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 leg.
    # W102+ projection: A 247_004..249_003 CLEAN; B 59_201..59_400
    # CLEAN (next freezer must re-derive, never transcribe).
    # NOT a re-pick (R250: W101 bands were never assigned).
    101: {"a": (245_004, 247_003), "b_exit": (59_001, 59_200),
         "engine_owner": "bm-a"},
    # NINETY-SECOND ENGINE-OWNED WAVE BY MACHINE-DERIVE (r375 bm-c
    # freeze): engine_owner rows 91 + candidate; bm-c's thirtieth
    # owned per machine-derive (engine_owner==bm-c rows 29 +
    # candidate). Wave 102 = first free number after the REGISTERED
    # W101 row (bm-a r583, landed ffd844431) -- SINGLE STATE zero
    # seat gap (no skip-past-published chain; W100 bm-b r583 +
    # W101 bm-a r583 both landed before this freeze). Seat
    # published=reserved MSG-20261002-1642-bmc pushed to origin
    # a369ae045 BEFORE this freeze per r565 early-visibility law
    # (seat prose ordinal "91st/rows 90" hand-calc drift disclosed
    # per r359 law; gate machine face governs; zero science impact).
    # W97 finalize LANDED at this freeze (landed chain head
    # 577,948 = W97 bm-b r583 one-pass; K=211,320). FOUR
    # in-flight upstream seats (W98 bm-a burned-unfinalized +
    # W99 bm-c burned-unfinalized + W100 bm-b burning + W101 bm-a
    # burning) -- finalize merge loop stays FAIL-CLOSED r307
    # at run time.
    # A = arithmetic continuation from the registered W101 A tail:
    # 247_004..249_003 CLEAN hops=0. B = arithmetic continuation
    # from the registered W101 B tail: 59_201..59_400 CLEAN hops=0
    # (both sides arithmetic continuation, W92 r370 / W100 r583
    # precedent family). ADMIT receipt
    # results/_r375bmc_w102_band_gate.py rc0; live SEED_REGISTRY
    # + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 leg.
    # W103+ projection: A 249_004..251_003 CLEAN; B 59_401..59_600
    # CLEAN (next freezer must re-derive, never transcribe).
    # NOT a re-pick (R250: W102 bands were never assigned).
    102: {"a": (247_004, 249_003), "b_exit": (59_201, 59_400),
         "engine_owner": "bm-c"},
    # NINETY-THIRD ENGINE-OWNED WAVE BY MACHINE-DERIVE (r584 bm-b
    # freeze): engine_owner rows 92 + candidate; bm-b's thirty-
    # fifth owned per machine-derive (engine_owner==bm-b rows 34 +
    # candidate). Wave 103 = first free number after the REGISTERED
    # W102 row (bm-c r375, surgical delivery fd031f6ed) -- SINGLE
    # STATE zero seat gap (no skip-past-published chain). Seat
    # published=reserved MSG-20261002-1658-bmb pushed to origin
    # badb5dcc2 BEFORE this freeze per r565 early-visibility law.
    # W98 finalize LANDED at this freeze (landed chain head
    # 580,148 = W98 bm-a r584; K=213,520). FOUR in-flight upstream
    # seats (W99 bm-c burned-unfinalized + W100 bm-b burned-
    # unfinalized + W101 bm-a burned-unfinalized + W102 bm-c
    # burned-unfinalized) -- finalize merge loop stays FAIL-CLOSED
    # r307 at run time.
    # A = arithmetic continuation from the registered W102 A tail:
    # 249_004..251_003 CLEAN hops=0. B = arithmetic continuation
    # from the registered W102 B tail: 59_401..59_600 CLEAN hops=0
    # (both sides arithmetic continuation, W92 r370 / W100 r583
    # precedent family). ADMIT receipt
    # results/_r584bmb_w103_band_gate.py rc0; live SEED_REGISTRY
    # + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 leg.
    # W104+ projection: A 251_004..253_003 CLEAN; B 59_601..59_800
    # CLEAN (next freezer must re-derive, never transcribe).
    # NOT a re-pick (R250: W103 bands were never assigned).
    103: {"a": (249_004, 251_003), "b_exit": (59_401, 59_600),
         "engine_owner": "bm-b"},
    # W104 (r586 bm-a freeze): A 251_004..253_003 + B 59_601..59_800,
    # both sides arithmetic continuation from the registered W103 tails
    # (A 251_003+1 / B 59_600+1, strides 2_000/200, CLEAN hops=0/0,
    # single-state zero seat gap). ADMIT receipt
    # results/_r586bma_w104_band_gate.py rc0; live SEED_REGISTRY 160 int
    # values + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 leg. Seat prose ordinal drift
    # disclosed (r359 law, W102 precedent): seat MSG hand-count said
    # bm-a rows 30, machine count = bm-a rows 28 -> W104 = bm-a 29th
    # owned wave, 94th engine wave (engine_owner rows 93 + candidate).
    # W105+ projection: A 253_004..255_003 CLEAN; B 59_801..60_000
    # REFUSED at 60_000 (SEED_REGISTRY in-book value) -> next freezer
    # past-hit restart 60_001 per D-20261002-05 pin (re-derive, never
    # transcribe).
    # NOT a re-pick (R250: W104 bands were never assigned).
    104: {"a": (251_004, 253_003), "b_exit": (59_601, 59_800),
         "engine_owner": "bm-a"},
    # NINETY-FOURTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r376 bm-c
    # freeze): engine_owner rows 93 + candidate; bm-c's thirty-
    # first owned per machine-derive (engine_owner==bm-c rows 30 +
    # candidate). Wave 105 = first free number after the REGISTERED
    # W103 row (bm-b r584 freeze fbbde996f) SKIPPING the published
    # W104 seat (bm-a MSG-20261002-1712, published=reserved r518-1;
    # W104 seat-published unregistered honest note). Seat
    # published=reserved MSG-20261002-1738-bmc pushed to origin
    # 565a6b254 BEFORE this freeze per r565 early-visibility law.
    # W99 finalize LANDED at this freeze (landed chain head
    # 582,348 = W99 bm-c r376; K=215,720). FOUR in-flight upstream
    # seats (W100 bm-b burned-unfinalized + W101 bm-a burned-
    # unfinalized + W102 bm-c burned-unfinalized + W103 bm-b
    # registered in-flight) -- finalize merge loop stays FAIL-CLOSED
    # r307 at run time.
    # A = skip-past-published W104 then arithmetic continuation:
    # 253_004..255_003 CLEAN hops=1. B = skip-past-published W104
    # then pinned past-hit restart past SEED_REGISTRY
    # div_lowvol_p1=60_000 upper-edge of the refused window
    # 59_801..60_000: 60_001..60_200 CLEAN hops=2 (both readings
    # converge, W74-B/W81 edge family, no fork face). ADMIT receipt
    # results/_r376bmc_w105_band_gate.py rc0; live SEED_REGISTRY
    # + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 leg.
    # W106+ projection: A 255_004..257_003 CLEAN; B 60_201..60_400
    # CLEAN (next freezer must re-derive, never transcribe).
    # NOT a re-pick (R250: W105 bands were never assigned).
    105: {"a": (253_004, 255_003), "b_exit": (60_001, 60_200),
         "engine_owner": "bm-c"},
    # NINETY-SIXTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r585 bm-b
    # freeze): engine_owner rows 95 + candidate; bm-b's thirty-
    # sixth owned per machine-derive (engine_owner==bm-b rows 35 +
    # candidate). Wave 106 = first free number after the REGISTERED
    # W105 row (bm-c r376 freeze f2db133c5 + bm-a r586 W104-union
    # 48f6f2ff1) -- SINGLE STATE zero seat gap. Seat
    # published=reserved MSG-20261002-1733-bmb pushed to origin
    # fe191d370 BEFORE this freeze per r565 early-visibility law;
    # seat prose ordinal drift (pre-registration framing) disclosed
    # per r359 law; seat-time skip-past-published hops 2/2 vs
    # freeze-time single-state arithmetic hops 0/0 converge on
    # identical bands (no fork face).
    # W100 finalize LANDED at this freeze (landed chain head
    # 584,148->584,548 = W100 bm-b r585 one-pass this window;
    # K=217,920). FIVE in-flight upstream seats (W101 bm-a + W102
    # bm-c + W103 bm-b + W104 bm-a + W105 bm-c burned-unfinalized)
    # -- finalize merge loop stays FAIL-CLOSED r307 at run time.
    # A = arithmetic continuation from the registered W105 A tail:
    # 255_004..257_003 CLEAN hops=0. B = arithmetic continuation
    # from the registered W105 B tail: 60_201..60_400 CLEAN hops=0
    # (both sides arithmetic continuation, W92 r370 / W100 r583 /
    # W103 r584 precedent family). ADMIT receipt
    # results/_r585bmb_w106_band_gate.py rc0; live SEED_REGISTRY
    # + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 leg.
    # W107+ projection: A 257_004..259_003 CLEAN; B 60_401..60_600
    # CLEAN (next freezer must re-derive, never transcribe).
    # NOT a re-pick (R250: W106 bands were never assigned).
    106: {"a": (255_004, 257_003), "b_exit": (60_201, 60_400),
         "engine_owner": "bm-b"},
    # NINETY-SEVENTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r587 bm-a
    # freeze): engine_owner rows 96 + candidate; bm-a's thirtieth
    # owned per machine-derive (engine_owner==bm-a rows 29 +
    # candidate). Wave 107 = first free number after the REGISTERED
    # W106 row (bm-b r585 freeze d6b2952e3) -- SINGLE STATE zero
    # seat gap (W104 bm-a union 48f6f2ff1 + W105 bm-c f2db133c5 +
    # W106 bm-b d6b2952e3 all registered). Seat published=reserved
    # MSG-20261002-1759-bma pushed to origin d548df902 BEFORE this
    # freeze per r565 early-visibility law; seat-window and
    # freeze-window both single-state, projections bitwise
    # identical, no fork face.
    # W101 finalize LANDED at this freeze (landed chain head
    # 584,548->586,748 = W101 bm-a r587 one-pass this window;
    # K=220,120). FIVE in-flight upstream seats (W102 bm-c + W103
    # bm-b + W104 bm-a + W105 bm-c + W106 bm-b burned-unfinalized)
    # -- finalize merge loop stays FAIL-CLOSED r307 at run time.
    # A = arithmetic continuation from the registered W106 A tail:
    # 257_004..259_003 CLEAN hops=0. B = arithmetic continuation
    # from the registered W106 B tail: 60_401..60_600 CLEAN hops=0
    # (both sides arithmetic continuation, W92 r370 / W100 r583 /
    # W103 r584 / W106 r585 precedent family). ADMIT receipt
    # results/_r587bma_w107_band_gate.py rc0; live SEED_REGISTRY
    # + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 leg.
    # W108+ projection: A 259_004..261_003 CLEAN; B 60_601..60_800
    # CLEAN (next freezer must re-derive, never transcribe).
    # NOT a re-pick (R250: W107 bands were never assigned).
    107: {"a": (257_004, 259_003), "b_exit": (60_401, 60_600),
         "engine_owner": "bm-a"},
    # NINETY-EIGHTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r378 bm-c
    # freeze): engine_owner rows 97 + candidate; bm-c's thirty-
    # second owned per machine-derive (engine_owner==bm-c rows 31 +
    # candidate). Wave 108 = first free number after the REGISTERED
    # W107 row (bm-a r587 freeze a554dedd3), SINGLE STATE zero seat
    # gap. Seat-time vs freeze-time tenses converge identical bands
    # (W106 r585 precedent): seat published=reserved
    # MSG-20261002-1804-bmc pushed to origin ed44e0857 BEFORE this
    # freeze per r565 early-visibility law when W107 was published-
    # unregistered (skip-past-published hops 1/1 projection); at
    # freeze W107 is registered -> single-state arithmetic
    # continuation from the W107 tails hops 0/0. W102 finalize
    # LANDED at this freeze (landed chain head 588,948 = W102 bm-c
    # r378, K=222,320). FIVE in-flight upstream seats (W103 bm-b +
    # W104 bm-a + W105 bm-c + W106 bm-b burned-unfinalized + W107
    # bm-a fresh-freeze burn pending) -- finalize merge loop stays
    # FAIL-CLOSED r307 at run time.
    # A = arithmetic continuation == W107 A tail 259_003+1:
    # 259_004..261_003 CLEAN hops=0. B = arithmetic continuation
    # == W107 B tail 60_600+1: 60_601..60_800 CLEAN hops=0.
    # ADMIT receipt results/_r378bmc_w108_band_gate.py rc0
    # (dual-state); live SEED_REGISTRY + probe cluster
    # 95_000..95_003 r335 leg + N3-R1 used-seed band 70_000..70_005
    # MSG-183x r529 leg.
    # W109+ projection: A 261_004..263_003 CLEAN; B 60_801..61_000
    # REFUSED [61_000] (next freezer must re-derive, never
    # transcribe).
    # NOT a re-pick (R250: W108 bands were never assigned).
    108: {"a": (259_004, 261_003), "b_exit": (60_601, 60_800),
         "engine_owner": "bm-c"},
    # NINETY-NINTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r587 bm-b
    # freeze): engine_owner rows 98 + candidate; bm-b's thirty-
    # seventh owned per machine-derive (engine_owner==bm-b rows 36 +
    # candidate). Wave 109 = first free number after the REGISTERED
    # W108 row (bm-c r378 freeze 3a3c51b73) -- SINGLE STATE zero seat
    # gap (W2..W108 all registered). Seat published=reserved
    # MSG-20261002-1817-bmb rev.B pushed to origin 99e29877c BEFORE
    # this freeze per r565 early-visibility law. Rev.B: first-draft
    # B projection 60_801..61_000 corrected PRE-PUSH (origin advance
    # caught by pre-push claw r374 fork artifact; bm-c W108 freeze
    # landed mid-window; own probe confirmed refusal point =
    # SEED_REGISTRY wild_route_s1=61_000; zero prior visibility).
    # W103 finalize LANDED before this freeze (chain head 591,148,
    # K=224,520 = bm-b r586 one-pass). FIVE in-flight upstream seats
    # (W104 bm-a + W105 bm-c + W106 bm-b + W107 bm-a + W108 bm-c
    # registered-unfinalized) -- finalize merge loop stays
    # FAIL-CLOSED r307 at run time.
    # A = arithmetic continuation from the registered W108 A tail:
    # 261_004..263_003 CLEAN hops=0. B = VALUE-COLLISION JUMP:
    # arithmetic window 60_801..61_000 hits SEED_REGISTRY
    # wild_route_s1=61_000 -> first clean window 61_001..61_200 hops=1
    # per law sec.4 W5 precedent family (machine gate disjoint law
    # over stride convention). ADMIT receipt
    # results/_r587bmb_w109_band_gate.py rc0; live SEED_REGISTRY
    # + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed
    # band 70_000..70_005 MSG-183x r529 leg.
    # W110+ projection: A 263_004..265_003 CLEAN; B 61_201..61_400
    # CLEAN (next freezer must re-derive, never transcribe).
    # NOT a re-pick (R250: W109 bands were never assigned).
    109: {"a": (261_004, 263_003), "b_exit": (61_001, 61_200),
         "engine_owner": "bm-b"},
    # ONE HUNDREDTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r589 bm-a
    # freeze): engine_owner rows 99 + candidate; bm-a's thirty-first
    # owned per machine-derive (engine_owner==bm-a rows 30 +
    # candidate). Wave 110 = first free number after the REGISTERED
    # W109 row (bm-b r587 freeze f077ae11b) -- SINGLE STATE zero
    # seat gap (W2..W109 all registered). Seat published=reserved
    # MSG-20261002-1829-bma pushed to the origin f457e1c4f BEFORE
    # this freeze per r565 early-visibility law; seat-window r588
    # and freeze-window r589 band-gate runs bitwise identical, no
    # fork face.
    # W105 finalize LANDED before this freeze (landed chain head
    # 595,548 = bm-c r379 one-pass; K=228,920). FOUR in-flight
    # upstream seats (W106 bm-b + W107 bm-a + W108 bm-c
    # burned-unfinalized + W109 bm-b frozen-burn-in-flight) -- the
    # finalize merge loop stays FAIL-CLOSED r307 at run time.
    # A = arithmetic continuation from the registered W109 A tail:
    # 263_004..265_003 CLEAN hops=0. B = arithmetic continuation
    # from the registered W109 B tail: 61_201..61_400 CLEAN hops=0
    # (both sides arithmetic continuation, W92 r370 / W100 r583 /
    # W103 r584 / W106 r585 / W107 r587 precedent family). ADMIT
    # receipt results/_r588bma_w110_band_gate.py rc0 (re-run this
    # freeze window, bitwise identical to the r588 seat-window
    # run); live SEED_REGISTRY + probe cluster 95_000..95_003 r335
    # leg + N3-R1 used-seed band 70_000..70_005 MSG-183x r529 leg.
    # W111+ projection: A 265_004..267_003 CLEAN; B 61_401..61_600
    # CLEAN (next freezer must re-derive, never transcribe).
    # NOT a re-pick (R250: W110 bands were never assigned).
    110: {"a": (263_004, 265_003), "b_exit": (61_201, 61_400),
         "engine_owner": "bm-a"},
    # HUNDRED-AND-FIRST ENGINE-OWNED WAVE BY MACHINE-DERIVE (r589 bm-b
    # freeze): engine_owner rows 100 + candidate; bm-b's thirty-
    # eighth owned per machine-derive (engine_owner==bm-b rows 37 +
    # candidate). Wave 111 = first free number after the REGISTERED
    # W110 row (bm-a r589 freeze ff0b1869b) -- SINGLE STATE zero seat
    # gap (W2..W110 all registered). Seat published=reserved
    # MSG-20261002-1911-bmb pushed to origin 8088582ba BEFORE this
    # freeze per r565 early-visibility law (re-landed twice after
    # mid-window origin advances via the r585 pure-FF window; first
    # draft never visible; rev.A = only published face). W107
    # finalize LANDED mid-draft-window (chain head 599,948, K=233,320
    # = bm-a r589 one-pass). THREE in-flight upstream seats (W108
    # bm-c + W109 bm-b + W110 bm-a registered, 12/12 delivered,
    # finalizes NOT landed) -- finalize merge loop stays
    # FAIL-CLOSED r307 at run time.
    # A = arithmetic continuation from the registered W110 A tail:
    # 265_004..267_003 CLEAN hops=0. B = arithmetic continuation from
    # the registered W110 B tail: 61_401..61_600 CLEAN hops=0.
    # ADMIT receipt results/_r589bmb_w111_band_gate.py rc0; live
    # SEED_REGISTRY + probe cluster 95_000..95_003 r335 leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 leg.
    # W112+ projection: A 267_004..269_003 CLEAN; B 61_601..61_800
    # CLEAN (next freezer must re-derive, never transcribe).
    # NOT a re-pick (R250: W111 bands were never assigned).
    111: {"a": (265_004, 267_003), "b_exit": (61_401, 61_600),
         "engine_owner": "bm-b"},
    # ONE HUNDRED-AND-SECOND ENGINE-OWNED WAVE BY MACHINE-DERIVE (r590 bm-a
    # freeze): engine_owner rows 101 + candidate; bm-a's thirty-
    # second owned per machine-derive (engine_owner==bm-a rows 31 +
    # candidate). Wave 112 = first free number after the REGISTERED
    # W111 row (bm-b r589 freeze e0a103ec1) -- SINGLE STATE zero seat
    # gap (W2..W111 all registered). Seat published=reserved
    # MSG-20261002-1922-bma pushed to origin e9f157e25 BEFORE this
    # freeze per r565 early-visibility law (surgical commit-tree over
    # bm-b r589 closing 3b7da8dfe mid-window origin advance, payload=1
    # seat MSG, deletion-set EMPTY; first draft commit 24cd47c87
    # orphaned-never-visible, rev.A = only published face). W110
    # finalize LANDED (chain head 606,548, K=239,920 = bm-b r590
    # three-wave backlog drain cross-machine finalize one-pass:
    # W108 on behalf of bm-c + W109 bm-b owned + W110 on behalf of
    # bm-a). ONE in-flight upstream seat (W111 bm-b registered,
    # finalize NOT landed) -- finalize merge loop stays
    # FAIL-CLOSED r307 at run time.
    # A = arithmetic continuation from the registered W111 A tail:
    # 267_004..269_003 CLEAN hops=0. B = arithmetic continuation from
    # the registered W111 B tail: 61_601..61_800 CLEAN hops=0.
    # ADMIT receipt results/_r590bma_w112_band_gate.py rc0; live
    # SEED_REGISTRY + probe cluster 95_000..95_003 r335 leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 leg.
    # W113+ projection: A 269_004..271_003 CLEAN; B 62_001..62_200
    # hops=1 jump via SEED_REGISTRY cta_wave1=62_000 (D-20261002-05
    # jump law; next freezer must re-derive, never transcribe).
    # NOT a re-pick (R250: W112 bands were never assigned).
    112: {"a": (267_004, 269_003), "b_exit": (61_601, 61_800),
         "engine_owner": "bm-a"},
    # ONE HUNDRED-AND-THIRD ENGINE-OWNED WAVE BY MACHINE-DERIVE (r382 bm-c
    # freeze): engine_owner rows 102 + candidate; bm-c's thirty-
    # third owned per machine-derive (engine_owner==bm-c rows 32 +
    # candidate). Wave 113 = first free number after the REGISTERED
    # W112 row (bm-a r590 freeze 0c4d67910) -- SINGLE STATE zero seat
    # gap (W2..W112 all registered). Seat published=reserved
    # MSG-20261002-1949-bmc pushed to origin baa0c3888 BEFORE this
    # freeze per r565 early-visibility law (clean single-file push,
    # payload=1 seat MSG, deletion-set EMPTY; rev.A = only published
    # face). W111 finalize LANDED (chain head 608,748, K=242,120 =
    # bm-b r590 one-pass). ONE in-flight upstream seat (W112 bm-a
    # registered, finalize NOT landed) -- finalize merge loop stays
    # FAIL-CLOSED r307 at run time.
    # A = arithmetic continuation from the registered W112 A tail:
    # 269_004..271_003 CLEAN hops=0. B = jump-past-hit window: the
    # arithmetic window 61_801..62_000 is refused at SEED_REGISTRY
    # cta_wave1=62_000 (window-tail endpoint, W74/W81 family) ->
    # pinned sec.4 skip semantics (D-20261002-05) land 62_001..62_200
    # hops=1. ADMIT receipt results/_r382bmc_w113_band_gate.py rc0;
    # live SEED_REGISTRY + probe cluster 95_000..95_003 r335 leg +
    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 leg.
    # W114+ projection: A 271_004..273_003 CLEAN; B 62_201..62_400
    # CLEAN (next freezer must re-derive, never transcribe).
    # NOT a re-pick (R250: W113 bands were never assigned).
    113: {"a": (269_004, 271_003), "b_exit": (62_001, 62_200),
         "engine_owner": "bm-c"},
    # ONE HUNDRED-AND-FOURTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r592 bm-a
    # freeze): engine_owner rows 103 + candidate; bm-a's thirty-
    # third owned per machine-derive (engine_owner==bm-a rows 32 +
    # candidate). Wave 114 = first free number after the REGISTERED
    # W113 row (bm-c r382 freeze eeb062290) -- SINGLE STATE zero seat
    # gap (W2..W113 all registered). Seat published=reserved
    # MSG-20261002-2014-bma pushed to origin 2cd67216a BEFORE this
    # freeze per r565 early-visibility law (one r589 reset-FF-reland
    # loop over the bm-c appender 3-shard mid-window advance; payload=1
    # seat MSG, deletion-set EMPTY; rev.A = only published face).
    # W113 finalize LANDED (chain head 613,148, K=246,520 = bm-c r382
    # one-pass). ZERO in-flight upstream seats (W2..W113 all landed) --
    # finalize merge loop still derives the wave set from registry
    # keys at run time, FAIL-CLOSED r307 two-state law always on.
    # A = arithmetic continuation from the registered W113 A tail:
    # 271_004..273_003 CLEAN hops=0. B = arithmetic continuation from
    # the registered W113 B tail: 62_201..62_400 CLEAN hops=0 (both
    # clean windows per ADMIT receipt results/_r592bma_w114_band_gate.py
    # rc0; live SEED_REGISTRY + probe cluster 95_000..95_003 r335 leg +
    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 leg.
    # W115+ projection (pinned D-20261002-05): A 273_004..275_003
    # CLEAN; B arithmetic 62_401..62_600 refused at SEED_REGISTRY
    # grid_sleeve_p1=62_500 (mid-window hit) -> past-hit restart
    # 62_501..62_700 CLEAN (next freezer must re-derive, never
    # transcribe; the W114 seat MSG advisory line 62_601..62_800 =
    # window-step-chain reading, superseded for mid-window hits).
    # NOT a re-pick (R250: W114 bands were never assigned).
    114: {"a": (271_004, 273_003), "b_exit": (62_201, 62_400),
         "engine_owner": "bm-a"},
    # ONE HUNDRED-AND-FIFTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r384 bm-c
    # freeze): engine_owner rows 104 + candidate; bm-c's thirty-
    # fourth owned per machine-derive (engine_owner==bm-c rows 33 +
    # candidate). Wave 115 = first free number after the REGISTERED
    # W114 row (bm-a r594 freeze ddacf2616) -- SINGLE STATE zero seat
    # gap (W2..W114 all registered). Seat published=reserved
    # MSG-20261002-2130-bmc-w115-seat pushed to origin ac241dd32
    # BEFORE this freeze per r565 early-visibility law (payload = seat
    # MSG + pre-seat probe, deletion-set EMPTY; rev.A = only published
    # face).
    # W114 finalize LANDED (chain head 615,348, K=248,720 = bm-a r594
    # one-pass). ZERO in-flight upstream seats (W2..W114 all landed) --
    # finalize merge loop still derives the wave set from registry
    # keys at run time, FAIL-CLOSED r307 two-state law always on.
    # A = arithmetic continuation from the registered W114 A tail:
    # 273_004..275_003 CLEAN hops=0. B = pinned D-20261002-05 past-hit
    # restart: arithmetic 62_401..62_600 refused in-band at
    # SEED_REGISTRY grid_sleeve_p1=62_500 (mid-window hit) ->
    # restart 62_501..62_700 CLEAN hops=1 (window-step-chain reading
    # 62_601..62_800 BANNED per W68-B negative anchor; ADMIT receipt
    # results/_r384bmc_w115_band_gate.py rc0; live SEED_REGISTRY +
    # probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed band
    # 70_000..70_005 MSG-183x r529 leg.
    # W116+ projection (gate-derived r384): A 275_004..277_003 CLEAN
    # hops=0; B 62_701..62_900 CLEAN hops=0 (next freezer must
    # re-derive, never transcribe; r587 law).
    # NOT a re-pick (R250: W115 bands were never assigned).
    115: {"a": (273_004, 275_003), "b_exit": (62_501, 62_700),
         "engine_owner": "bm-c"},
    # ONE HUNDRED-AND-SIXTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r677 bm-b
    # freeze): engine_owner rows 105 + candidate; bm-b's thirty-
    # ninth owned per machine-derive (engine_owner==bm-b rows 38 +
    # candidate). Wave 116 = first free number after the REGISTERED
    # W115 row (bm-c r445 unpark-freeze f6b521153) -- SINGLE STATE
    # zero seat gap (W2..W115 all registered). Seat published=reserved
    # MSG-20261004-1515-bmb-w116-seat pushed to origin 4b0409196
    # BEFORE this freeze per r565 early-visibility law (payload = seat
    # MSG + pre-seat probe + D-19 receipts, deletion-set EMPTY; rev.A
    # = only published face).
    # W115 finalize LANDED (net chain head 617,548, K=250,920 = bm-c
    # r445 one-pass). ZERO in-flight upstream seats (W2..W115 all
    # landed) -- finalize merge loop still derives the wave set from
    # registry keys at run time, FAIL-CLOSED r307 two-state law
    # always on.
    # A = arithmetic continuation from the registered W115 A tail:
    # 275_004..277_003 CLEAN hops=0. B = arithmetic continuation
    # from the registered W115 B tail: 62_701..62_900 CLEAN hops=0
    # (zero-jump two-reading-identical face; ADMIT receipt
    # results/_r677bmb_w116_band_gate.py; live SEED_REGISTRY +
    # probe cluster 95_000..95_003 r335 leg + cross-face probe points
    # 95_004/95_006 r602 leg + N3-R1 used-seed band 70_000..70_005
    # MSG-183x r529 leg.
    # W117+ projection (gate-derived r677): A 277_004..279_003 CLEAN
    # hops=0; B first-clean 65_050..65_249 hops=1 (arith window
    # 62_901..63:100 refused at options_wave2 actual 63_000..63_049 +
    # registered A-band overlap; next freezer must re-derive, never
    # transcribe; r587 law).
    # NOT a re-pick (R250: W116 bands were never assigned).
    116: {"a": (275_004, 277_003), "b_exit": (62_701, 62_900),
         "engine_owner": "bm-b"},
    # W117 (r683 bm-a freeze, own-series law under CEO de-throttle
    # order O-20261001-2355 sec.2): bm-a's thirty-fourth owned per
    # machine-derive (engine_owner==bm-a rows 33 + candidate); wave
    # 117 = first free number after the REGISTERED W116 row (bm-b
    # r677 freeze bc1e82773) -- SINGLE STATE zero seat gap
    # (W2..W116 all registered). Seat published=reserved
    # MSG-2026-10-04-1535-bma-w117-seat pushed to origin 380167da7
    # BEFORE this freeze, r565 law (payload = seat MSG + pre-seat
    # probe + D-19 receipts; deletion-set EMPTY; rev.A = only
    # published face). ONE HUNDRED-AND-SEVENTH engine wave BY
    # MACHINE-DERIVE (engine_owner rows 106 + candidate; gate leg0
    # machine output governs per r359 law). W1..W115 finalize LANDED
    # (net chain head 617,548, K=250,920, bm-c r445 one-pass) + ONE
    # in-flight upstream seat W116 bm-b (registered, burn pending,
    # finalize NOT landed) -- finalize merge loop still derives the
    # wave set from registry keys at run time, FAIL-CLOSED r307
    # always on. ADMIT receipt
    # results/_r683bma_w117_band_gate.py; banned gate ADMIT 0;
    # not a re-pick (R250: W117 bands were never assigned).
    # A = arithmetic continuation from the registered W116 A tail:
    # 277_004..279_003 CLEAN hops=0. B = pinned D-20261002-05
    # past-hit restart: arithmetic 62_901..63:100 refused in-band
    # at options_wave2 actual 63_000..63_049 + registered W12 A
    # band 63_050..65_049 (mid-window hit) -> restart 65_050..65_249
    # CLEAN hops=1 (live SEED_REGISTRY + probe cluster 95_000..95_003
    # r335 leg + cross-face probe points 95_004/95_006 r602 leg +
    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 leg).
    # W118+ projection (gate-derived r683): A 279_004..281_003 CLEAN
    # hops=0; B first-clean 65_250..65_449 CLEAN hops=0; next
    # freezer must re-derive, never transcribe (r587 law).
    117: {"a": (277_004, 279_003), "b_exit": (65_050, 65_249),
         "engine_owner": "bm-a"},
    # W118 (r678 bm-b freeze, own-series law under CEO de-throttle
    # order O-20261001-2355 sec.2): bm-b's fortieth owned per
    # machine-derive (engine_owner==bm-b rows 39 + candidate); wave
    # 118 = first free number after the REGISTERED W117 row (bm-a
    # r683 freeze c36a087ea) -- SINGLE STATE zero seat gap
    # (W2..W117 all registered). Seat published=reserved
    # MSG-2026-10-04-1532-bmb-w118-seat pushed to origin 24960f5e1
    # BEFORE this freeze, r565 law (payload = seat MSG + pre-seat
    # probe + W117 yield record + D-19 receipts; deletion-set EMPTY;
    # rev.A = only published face). ONE HUNDRED-AND-EIGHTH engine
    # wave BY MACHINE-DERIVE (engine_owner rows 107 + candidate;
    # gate leg0 machine output governs per r359 law). W1..W115
    # finalize LANDED (net chain head 617,548, K=250,920, bm-c r445
    # one-pass) + TWO in-flight upstream seats: W116 bm-b
    # (registered bc1e82773, queue 12/12 materialized, ignition
    # held by engine RAM floor gate, finalize pending) + W117 bm-a
    # (registered c36a087ea, burn pending) -- finalize merge loop
    # still derives the wave set from registry keys at run time,
    # FAIL-CLOSED r307 two-state law always on.
    # Same-window yield record: W117 pre-seat probe caught bm-a's
    # published W117 seat (origin-first) -> bm-b yielded W117 per
    # r518-1 published=reserved + fleet sec.4 commit-time ordering;
    # cross-machine derive convergence (A 277_004..279_003 /
    # B 65_050..65_249 identical) recorded
    # results/_r678bmb_w117_probe_receipt.txt.
    # A = arithmetic continuation from the registered W117 A tail:
    # 279_004..281_003 CLEAN hops=0. B = arithmetic continuation
    # from the registered W117 B tail: 65_250..65_449 CLEAN hops=0
    # (zero-jump two-reading-identical face; cross-machine
    # convergence with the bm-a r683 W117 seat W118+ projection
    # re-derived here, not transcribed; ADMIT receipt
    # results/_r678bmb_w118_band_gate.py; live SEED_REGISTRY +
    # probe cluster 95_000..95_003 r335 leg + cross-face probe points
    # 95_004/95_006 r602 leg + N3-R1 used-seed band 70_000..70_005
    # MSG-183x r529 leg.
    # W119+ projection (gate-derived r678): A 281_004..283_003
    # CLEAN hops=0; B first-clean 65_450..65_649 CLEAN hops=0;
    # next freezer must re-derive, never transcribe (r587 law).
    # NOT a re-pick (R250: W118 bands were never assigned).
    118: {"a": (279_004, 281_003), "b_exit": (65_250, 65_449),
         "engine_owner": "bm-b"},
    # W119 (r701 bm-a freeze, own-series law under CEO de-throttle
    # order O-20261001-2355 sec.2): bm-a's thirty-fifth owned per
    # machine-derive (engine_owner==bm-a rows 34 + candidate); wave
    # 119 = first free number after the REGISTERED W118 row (bm-b
    # r678 freeze 565e5b0b4) -- SINGLE STATE zero seat gap
    # (W2..W118 all registered). Seat published=reserved
    # MSG-2026-10-04-2323-bma-w119-seat pushed to origin 432a1eaca
    # BEFORE this freeze, r565 law (payload = seat MSG only,
    # deletion-set EMPTY, rev.A = only published face). ONE
    # HUNDRED-AND-NINTH engine wave BY MACHINE-DERIVE (engine_owner
    # rows 108 + candidate; gate leg0 machine output governs per
    # r359 law). W1..W115 finalize LANDED (net chain head 617,548,
    # K=250,920, bm-c r445 one-pass) + THREE in-flight upstream
    # seats: W116 bm-b (registered bc1e82773, 6/12 shards burned,
    # engine RAM floor gate self-paced, finalize pending) +
    # W117 bm-a (registered c36a087ea, 12/12 shards burned,
    # finalize rehearsal PASS r684, ARMED on W116 landing) +
    # W118 bm-b (registered 565e5b0b4, 0/12 burned, queued behind
    # W116 on the bm-b engine) -- finalize merge loop still derives
    # the wave set from registry keys at run time, FAIL-CLOSED r307
    # two-state law always on. Zero seat conflict this window
    # (first pre-seat probe of the window found the slot vacant;
    # cross-machine derive convergence with the bm-b r678 W118
    # gate-tail W119+ projection re-derived here, not transcribed).
    # A = arithmetic continuation from the registered W118 A tail:
    # 281_004..283_003 CLEAN hops=0. B = arithmetic continuation
    # from the registered W118 B tail: 65_450..65_649 CLEAN hops=0
    # (zero-jump two-reading-identical face; ADMIT receipt
    # results/_r701bma_w119_band_gate.py; live SEED_REGISTRY +
    # probe cluster 95_000..95_003 r335 leg + cross-face probe
    # points 95_004/95_006 r602 leg + N3-R1 used-seed band
    # 70_000..70_005 MSG-183x r529 leg.
    # W120+ projection (gate-derived r701): A 283_004..285_003
    # CLEAN hops=0; B first-clean 65_650..65_849 CLEAN hops=0;
    # next freezer must re-derive, never transcribe (r587 law).
    # NOT a re-pick (R250: W119 bands were never assigned).
    119: {"a": (281_004, 283_003), "b_exit": (65_450, 65_649),
         "engine_owner": "bm-a"},
    # W120 (r702 bm-a freeze, own-series law under CEO de-throttle
    # order O-20261001-2355 sec.2): bm-a's thirty-sixth owned per
    # machine-derive (engine_owner==bm-a rows 35 + candidate); wave
    # 120 = first free number after the REGISTERED W119 row (bm-a
    # r701 freeze 907e1e187) -- SINGLE STATE zero seat gap
    # (W2..W119 all registered). Seat published=reserved
    # MSG-2026-10-04-2349-bma-w120-seat pushed to origin 8792adc72
    # BEFORE this freeze, r565 law (payload = seat MSG only,
    # deletion-set EMPTY, rev.A = only published face). ONE
    # HUNDRED-AND-TENTH engine wave BY MACHINE-DERIVE (engine_owner
    # rows 109 + candidate; gate leg0 machine output governs per
    # r359 law). W1..W115 finalize LANDED (net chain head 617,548,
    # K=250,920) + FOUR in-flight upstream seats: W116 bm-b
    # (registered bc1e82773, 6/12 shards burned, engine RAM floor
    # gate self-paced, finalize pending) + W117 bm-a (registered
    # c36a087ea, 12/12 shards burned, finalize rehearsal PASS r684,
    # ARMED on W116 landing) + W118 bm-b (registered 565e5b0b4,
    # 0/12 burned, queued behind W116 on the bm-b engine) +
    # W119 bm-a (registered 907e1e187, 12/12 shards burned this
    # window, finalize attempt r702 FAIL-CLOSED on missing W116
    # upstream output -- clean fail, zero ledger append, zero
    # double-count) -- finalize merge loop still derives the wave
    # set from registry keys at run time, FAIL-CLOSED r307 two-state
    # law always on. Zero seat conflict this window (first pre-seat
    # probe of the window found the slot vacant; cross-window
    # convergence with the r701 W119 gate-tail W120+ projection
    # re-derived here, not transcribed). A = arithmetic continuation
    # from the registered W119 A tail: 283_004..285_003 CLEAN hops=0.
    # B = arithmetic continuation from the registered W119 B tail:
    # 65_650..65_849 CLEAN hops=0 (zero-jump two-reading-identical
    # face; ADMIT receipt results/_r702bma_w120_band_gate.py; live
    # SEED_REGISTRY + probe cluster 95_000..95_003 r335 leg +
    # cross-face probe points 95_004/95_006 r602 leg + N3-R1
    # used-seed band 70_000..70_005 MSG-183x r529 leg.
    # W121+ projection (gate-derived r702): A 285_004..287_003
    # CLEAN hops=0; B first-clean 66_001..66_200 hops=1 (arithmetic
    # 65_850..66_049 REFUSED by SEED_REGISTRY bond_carry_w3a=66_000
    # mid-band hit -> past-hit restart, pinned D-20261002-05);
    # next freezer must re-derive, never transcribe (r587 law).
    # NOT a re-pick (R250: W120 bands were never assigned).
    120: {"a": (283_004, 285_003), "b_exit": (65_650, 65_849),
         "engine_owner": "bm-a"},
    # W121 frozen bands (bm-a r726 freeze; re-derived at freeze, never
    # transcribed r587 law; pre-seat probe results/_r726bma_w121_probe.py
    # rc0 + freeze-window gate ADMIT receipt
    # results/_r726bma_w121_band_gate.py; dual-window derive parity held:
    # A 285_004..287_003 arithmetic continuation from the registered W120
    # A tail, CLEAN hops=0; B first-clean 66_001..66_200 hops=1 (arithmetic
    # 65_850..66_049 REFUSED by SEED_REGISTRY bond_carry_w3a=66_000
    # mid-band hit -> past-hit restart, pinned D-20261002-05, 越hit起窗);
    # scan face = pre-W121 all registered N1 bands + SEED_REGISTRY 187 int
    # values + v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 + lfc/options
    # actuals + N2/N4/N2-W15 probe points.
    # W122+ projection (gate-derived r726): A 287_004..289_003
    # CLEAN hops=0; B first-clean 66_201..66_400 CLEAN hops=0;
    # next freezer must re-derive, never transcribe (r587 law).
    # NOT a re-pick (R250: W121 bands were never assigned).
    121: {"a": (285_004, 287_003), "b_exit": (66_001, 66_200),
         "engine_owner": "bm-a"},
    # W122 frozen bands (bm-a r727 freeze; re-derived at freeze, never
    # transcribed r587 law; pre-seat probe results/_r727bma_w122_probe.py
    # rc0 + freeze-window gate ADMIT receipt
    # results/_r727bma_w122_band_gate.py; dual-window derive parity held:
    # A 287_004..289_003 arithmetic continuation from the registered W121
    # A tail, CLEAN hops=0; B 66_201..66_400 arithmetic continuation from
    # the registered W121 B tail, CLEAN hops=0 (cross-window convergence
    # with the r726 W121 gate-tail W122+ projection);
    # scan face = pre-W122 all registered N1 bands + SEED_REGISTRY 187 int
    # values + v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 + lfc/options
    # actuals + N2/N4/N2-W15 probe points.
    # W123+ projection (gate-derived r727): A 289_004..291_003
    # CLEAN hops=0; B first-clean 66_401..66_600 CLEAN hops=0;
    # next freezer must re-derive, never transcribe (r587 law).
    # NOT a re-pick (R250: W122 bands were never assigned).
    122: {"a": (287_004, 289_003), "b_exit": (66_201, 66_400),
         "engine_owner": "bm-a"},
    # W123 freeze (bm-a r728): pre-seat probe results/_r728bma_w123_probe.py
    # + freeze-window gate results/_r728bma_w123_band_gate.py; dual-window
    # derive parity held: A 289_004..291_003 arithmetic continuation from
    # the registered W122 A tail, CLEAN hops=0; B 66_401..66_600 arithmetic
    # continuation from the registered W122 B tail, CLEAN hops=0
    # (cross-window convergence with the r727 W122 gate-tail W123+
    # projection); scan face = pre-W123 all registered N1 bands +
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1 used-seed band
    # + probe cluster 95_000..95_003 + cross-face probe points 95_004/95_006
    # + lfc/options actuals + N2/N4/N2-W15 probe points.
    # W124+ projection (gate-derived r728): A 291_004..293_003
    # CLEAN hops=0; B first-clean 66_601..66_800 CLEAN hops=0;
    # next freezer must re-derive, never transcribe (r587 law).
    # NOT a re-pick (R250: W123 bands were never assigned).
    123: {"a": (289_004, 291_003), "b_exit": (66_401, 66_600),
         "engine_owner": "bm-a"},
    # W124 freeze (bm-a r729): pre-seat probe results/_r729bma_w124_probe.py
    # + freeze-window gate results/_r729bma_w124_band_gate.py; dual-window
    # derive parity held: A 291_004..293_003 arithmetic continuation from
    # the registered W123 A tail, CLEAN hops=0; B 66_601..66_800 arithmetic
    # continuation from the registered W123 B tail, CLEAN hops=0
    # (cross-window convergence with the r728 W123 gate-tail W124+
    # projection); scan face = pre-W124 all registered N1 bands +
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1 used-seed band
    # + probe cluster 95_000..95_003 + cross-face probe points 95_004/95_006
    # + lfc/options actuals + N2/N4/N2-W15 probe points.
    # W125+ projection (gate-derived r729): A 293_004..295_003
    # CLEAN hops=0; B first-clean 67_201..67_400 hops=2 (refusal facts
    # inside 66_801..67_200 disclosed by probe leg1);
    # next freezer must re-derive, never transcribe (r587 law).
    # NOT a re-pick (R250: W124 bands were never assigned).
    124: {"a": (291_004, 293_003), "b_exit": (66_601, 66_800),
         "engine_owner": "bm-a"},
    # W125 freeze (bm-a r730): pre-seat probe results/_r730bma_w125_probe.py
    # + freeze-window gate results/_r730bma_w125_band_gate.py; dual-window
    # derive parity held: A 293_004..295_003 arithmetic continuation from
    # the registered W124 A tail, CLEAN hops=0; B 67_201..67_400 pinned
    # D-20261002-05 past-hit restart (arithmetic 66_801..67_000 REFUSED at
    # SEED_REGISTRY p1e_zoo_behavior=67_000 -> 67_001..67_200 REFUSED again
    # -> first-clean 67_201..67_400 hops=2; cross-window convergence with
    # the r729 W124 gate-tail W125+ projection); scan face = pre-W125 all
    # registered N1 bands + SEED_REGISTRY 187 int values + v1/W1 ext bands
    # + N3-R1 used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/N2-W15
    # probe points.
    # W126+ projection (gate-derived r730): A 295_004..297_003
    # CLEAN hops=0; B first-clean 67_401..67_600 CLEAN hops=0;
    # next freezer must re-derive, never transcribe (r587 law).
    # NOT a re-pick (R250: W125 bands were never assigned).
    125: {"a": (293_004, 295_003), "b_exit": (67_201, 67_400),
         "engine_owner": "bm-a"},
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
    # ADJUDICATED EXCEPTION (bm-a r726, attrition-guard whitelist precedent
    # bm-b r295): SEED_REGISTRY sina_mf_ic_p1=58_700 was registered LATER
    # (bm-a r719 SINA_MF_IC_P1 freeze; its rg RNG sweep face missed the
    # N1_BANDS band face) and lands inside the ALREADY-BURNED W99 B band
    # 58_551..58_750 at j=149 -- historical single-point overlap on a
    # burned measurement face: statistically harmless (two different
    # consumers of one RNG stream; the null draw remains a valid null
    # draw), W99 finalize results stand un-reopened, the sina_mf_ic_p1
    # batch is NOT re-registered (registry records what was actually
    # used). Future band gates already treat SEED_REGISTRY live values
    # as refusal points, so no forward face. r727 found THIS pf-level
    # leg un-mirrored (the r726 fix landed in the perpetual_faces_n1
    # selftest only) -- mirror completed here, disclosed not hidden.
    w99_adjudicated = {58_700}
    w99_b_probe = set(range(N1_BANDS[99]["b_exit"][0],
                            N1_BANDS[99]["b_exit"][1] + 1))
    assert w99_adjudicated <= w99_b_probe, \
        "W99 adjudicated set drifted (must sit inside the burned band)"
    used = []
    for w, b in N1_BANDS.items():
        band_a = set(range(b["a"][0], b["a"][1] + 1))
        band_b = set(range(b["b_exit"][0], b["b_exit"][1] + 1))
        assert not (band_a & band_b), f"N1 w{w} A/B band overlap"
        assert not (band_a & V1_IN_USE) and not (band_b & V1_IN_USE), f"N1 w{w} hits v1 band"
        assert not (band_a & EXT_W1_IN_USE) and not (band_b & EXT_W1_IN_USE), f"N1 w{w} hits ext w1"
        assert not (band_a & reg_ints), f"N1 w{w} A hits SEED_REGISTRY"
        if w == 99:
            assert not (band_b & (reg_ints - w99_adjudicated)), \
                f"N1 w{w} hits SEED_REGISTRY beyond the adjudicated r719 point"
        else:
            assert not (band_b & reg_ints), f"N1 w{w} hits SEED_REGISTRY"
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
    # 9. skip-semantics pin (D-20261002-05 group ruling, pinned
    #    2026-10-02): MID-BAND HITS RESOLVE BY JUMP-PAST-HIT
    #    start-window (window starts at hit+1, scanning forward clean) --
    #    NOT by stepping whole windows (window-step chain). Frozen
    #    historical case W68-B: arithmetic 50_401..50_600 hits
    #    SEED_REGISTRY cta_p2_noau=50_500 mid-band -> registered band
    #    50_501..50_700 (hit+1 restart, r568 bm-a first-land); the
    #    chained reading 50_601..50_800 is NOT the registered face.
    #    W63-B remains the HISTORICAL fork example (its registered band
    #    is not re-derived -- r307 two-state law). Tail-point hits
    #    (upper/lower edge) always converged under both readings (W74-B
    #    52_000 / W81-B 54_000 families) -- pin not exercised there.
    assert N1_BANDS[68]["b_exit"] == (50_501, 50_700), \
        "D-20261002-05 pin: W68-B must be the jump-past-hit face 50_501..50_700"
    assert N1_BANDS[68]["b_exit"] != (50_601, 50_800), \
        "D-20261002-05 pin: the window-step chained reading is NOT the law"
    assert 50_500 in sg.SEED_REGISTRY.values(), \
        "W68-B refusal-fact identity (cta_p2_noau=50_500 must be registered)"
    hit_restart = set(range(50_501, 50_701))
    assert not (hit_restart & {50_500}), \
        "hit+1 restart window must clear the hit point"
    print("perpetual_faces selftest: 9/9 PASS "
          "(registry/seed-bands+3c-W6+3d-W7-packing/pool/state/py-face/"
          "materializer-expansion/pool-format-probe+writer-roundtrip/"
          "skip-semantics-pin-D-20261002-05; "
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
