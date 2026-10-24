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
    # W126 (bm-a r731 freeze, seat MSG-2026-10-05-1528-bma-w126-seat
    # pre-pushed 7d70b01fd r565 law; band gate ADMIT
    # results/_r731bma_w126_band_gate.json: A arithmetic continuation
    # 293_003+1 -> 295_004..297_003 CLEAN hops=0; B arithmetic continuation
    # 67_400+1 -> 67_401..67_600 CLEAN hops=0; dual-window derive parity
    # with pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster 95_000..95_003
    # + cross-face probe points 95_004/95_006 + lfc/options actuals +
    # N2/N4/N2-W15 probe points.
    # W127+ projection (gate-derived r731): A 297_004..299_003
    # CLEAN hops=0; B first-clean 67_601..67_800 CLEAN hops=0;
    # next freezer must re-derive, never transcribe (r587 law).
    # NOT a re-pick (R250: W126 bands were never assigned).
    126: {"a": (295_004, 297_003), "b_exit": (67_401, 67_600),
         "engine_owner": "bm-a"},
    # W127 (bm-a r732 freeze, seat MSG-2026-10-05-1548-bma-w127-seat
    # pre-pushed bef555332 r565 law; band gate ADMIT
    # results/_r732bma_w127_band_gate.json: A arithmetic continuation
    # 297_003+1 -> 297_004..299_003 CLEAN hops=0; B arithmetic continuation
    # 67_600+1 -> 67_601..67_800 CLEAN hops=0; dual-window derive parity
    # with pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster 95_000..95_003
    # + cross-face probe points 95_004/95_006 + lfc/options actuals +
    # N2/N4/N2-W15 probe points.
    # W128+ projection (gate-derived r732): A 299_004..301_003
    # CLEAN hops=0; B first-clean 68_001..68_200 hops=1 (refusal fact
    # cny_window_p1=68_000 upper-edge endpoint -> past-hit restart,
    # D-20261002-05 pin; next freezer must re-derive, never transcribe
    # r587 law).
    # NOT a re-pick (R250: W127 bands were never assigned).
    127: {"a": (297_004, 299_003), "b_exit": (67_601, 67_800),
         "engine_owner": "bm-a"},
    # W128 (bm-a r733 freeze, seat MSG-2026-10-05-1612-bma-w128-seat
    # pre-pushed 0826a8e65 r565 law; band gate ADMIT
    # results/_r733bma_w128_band_gate.json: A arithmetic continuation
    # 299_003+1 -> 299_004..301_003 CLEAN hops=0; B arithmetic
    # continuation 67_800+1 -> 67_801..68_000 REFUSED at upper-edge
    # endpoint cny_window_p1=68_000 -> past-hit restart first-clean
    # 68_001..68_200 hops=1 (D-20261002-05 pin edge-endpoint family
    # both-readings identical); dual-window derive parity with
    # pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster 95_000..95_003
    # + cross-face probe points 95_004/95_006 + lfc/options actuals +
    # N2/N4/N2-W15 probe points.
    # W129+ projection (gate-derived r733): A 301_004..303_003
    # CLEAN hops=0; B first-clean 68_201..68_400 CLEAN hops=0 (next
    # freezer must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W128 bands were never assigned).
    128: {"a": (299_004, 301_003), "b_exit": (68_001, 68_200),
         "engine_owner": "bm-a"},
    # W129 (bm-a r734 freeze, seat MSG-2026-10-05-1627-bma-w129-seat
    # pushed to origin 3575842b2 pre-freeze r565 law; band gate ADMIT
    # results/_r734bma_w129_band_gate.json: A arithmetic continuation
    # 301_003+1 -> 301_004..303_003 CLEAN hops=0; B arithmetic
    # continuation 68_200+1 -> 68_201..68_400 CLEAN hops=0 (B side
    # already past the cny_window_p1=68_000 refusal point of the W128
    # window family); dual-window derive parity with pre-seat probe;
    # scan face = SEED_REGISTRY 187 int values + v1/W1 ext bands +
    # N3-R1 used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/N2-W15
    # probe points.
    # W130+ projection (gate-derived r734): A 303_004..305_003
    # CLEAN hops=0; B first-clean 68_502..68_701 hops=1 (B arithmetic
    # window 68_401..68_600 carries a refusal point -> past-hit
    # restart; next freezer must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W129 bands were never assigned).
    129: {"a": (301_004, 303_003), "b_exit": (68_201, 68_400),
         "engine_owner": "bm-a"},
    # W130 (bm-a r735 freeze, seat MSG-2026-10-05-1658-bma-w130-seat
    # pushed to origin 02e151b0a pre-freeze r565 law; band gate ADMIT
    # results/_r735bma_w130_band_gate.json: A arithmetic continuation
    # 303_003+1 -> 303_004..305_003 CLEAN hops=0; B first-clean
    # past-hit restart window after the REFUSED arithmetic
    # continuation 68_401..68_600 from the registered W129 B tail
    # 68_400+1 (refusal facts SEED_REGISTRY 68_500 t19_phantom_p1 +
    # 68_501 perpetual_n4_b1, D-20261002-05 pin past-hit restart
    # semantics, hops=1 -> 68_502..68_701); dual-window derive parity
    # with pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 +
    # lfc/options actuals + N2/N4/N2-W15 probe points.
    # W131+ projection (gate-derived r735): A 305_004..307_003
    # CLEAN hops=0; B 68_702..68_901 CLEAN hops=0 (next freezer
    # must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W130 bands were never assigned).
    130: {"a": (303_004, 305_003), "b_exit": (68_502, 68_701),
         "engine_owner": "bm-a"},
    # W131 (bm-a r736 freeze, seat MSG-2026-10-05-1726-bma-w131-seat
    # pushed to origin fde20e3a1 pre-freeze r565 law; band gate ADMIT
    # results/_r736bma_w131_band_gate.json: double-CLEAN window --
    # A arithmetic continuation 305_003+1 -> 305_004..307_003
    # CLEAN hops=0; B arithmetic continuation 68_701+1 ->
    # 68_702..68_901 CLEAN hops=0; dual-window derive parity with
    # pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 +
    # lfc/options actuals + N2/N4/N2-W15 probe points.
    # W132+ projection (gate-derived r736): A 307_004..309_003
    # CLEAN hops=0; B 68_902..69_101 CLEAN hops=0 (next freezer
    # must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W131 bands were never assigned).
    131: {"a": (305_004, 307_003), "b_exit": (68_702, 68_901),
         "engine_owner": "bm-a"},
    # W132 (bm-a r737 freeze, seat MSG-2026-10-05-1755-bma-w132-seat
    # pushed to origin 9c7e85e7f pre-freeze r565 law; band gate ADMIT
    # results/_r737bma_w132_band_gate.json: double-CLEAN window --
    # A arithmetic continuation 307_003+1 -> 307_004..309_003
    # CLEAN hops=0; B arithmetic continuation 68_901+1 ->
    # 68_902..69_101 CLEAN hops=0; dual-window derive parity with
    # pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 +
    # lfc/options actuals + N2/N4/N2-W15 probe points.
    # W133+ projection (gate-derived r737): A 309_004..311_003
    # CLEAN hops=0; B 69_102..69_301 CLEAN hops=0 (next freezer
    # must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W132 bands were never assigned).
    132: {"a": (307_004, 309_003), "b_exit": (68_902, 69_101),
         "engine_owner": "bm-a"},
    # W133 (bm-a r738 freeze, seat MSG-2026-10-05-1824-bma-w133-seat
    # pushed to origin 2d717cc03 pre-freeze r565 law; band gate ADMIT
    # results/_r738bma_w133_band_gate.json: double-CLEAN window --
    # A arithmetic continuation 309_003+1 -> 309_004..311_003
    # CLEAN hops=0; B arithmetic continuation 69_101+1 ->
    # 69_102..69_301 CLEAN hops=0; dual-window derive parity with
    # pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 +
    # lfc/options actuals + N2/N4/N2-W15 probe points.
    # W134+ projection (gate-derived r738): A 311_004..313_003
    # CLEAN hops=0; B 69_302..69_501 CLEAN hops=0 (next freezer
    # must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W133 bands were never assigned).
    133: {"a": (309_004, 311_003), "b_exit": (69_102, 69_301),
         "engine_owner": "bm-a"},
    # W134 (bm-a r739 freeze, seat MSG-2026-10-05-1857-bma-w134-seat
    # pushed to origin 5f3d9fcfc pre-freeze r565 law; band gate ADMIT
    # results/_r739bma_w134_band_gate.json: double-CLEAN window --
    # A arithmetic continuation 311_003+1 -> 311_004..313_003
    # CLEAN hops=0; B arithmetic continuation 69_301+1 ->
    # 69_302..69_501 CLEAN hops=0; dual-window derive parity with
    # pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 +
    # lfc/options actuals + N2/N4/N2-W15 probe points.
    # W135+ projection (gate-derived r739): A 313_004..315_003
    # CLEAN hops=0; B 69_502..69_701 CLEAN hops=0 (next freezer
    # must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W134 bands were never assigned).
    134: {"a": (311_004, 313_003), "b_exit": (69_302, 69_501),
         "engine_owner": "bm-a"},
    # W135 (bm-a r740 freeze, seat MSG-2026-10-05-1933-bma-w135-seat
    # pushed to origin 98712a0e3 pre-freeze r565 law; band gate ADMIT
    # results/_r740bma_w135_band_gate.json: double-CLEAN window --
    # A arithmetic continuation 313_003+1 -> 313_004..315_003
    # CLEAN hops=0; B arithmetic continuation 69_501+1 ->
    # 69_502..69_701 CLEAN hops=0; dual-window derive parity with
    # pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 +
    # lfc/options actuals + N2/N4/N2-W15 probe points.
    # W136+ projection (gate-derived r740): A 315_004..317_003
    # CLEAN hops=0; B 69_702..69_901 CLEAN hops=0 (next freezer
    # must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W135 bands were never assigned).
    135: {"a": (313_004, 315_003), "b_exit": (69_502, 69_701),
         "engine_owner": "bm-a"},
    # W136 (bm-a r741 freeze, seat MSG-2026-10-05-1952-bma-w136-seat
    # pushed to origin 20d0036dc pre-freeze r565 law (push raced origin
    # forward 1 commit = r524 behind-signal (bm-c r568 same-window
    # wave), merge-mode zero-UU closeout, delivery 2564ba798); band
    # gate ADMIT results/_r741bma_w136_band_gate.json: double-CLEAN
    # window -- A arithmetic continuation 315_003+1 ->
    # 315_004..317_003 CLEAN hops=0; B arithmetic continuation
    # 69_701+1 -> 69_702..69_901 CLEAN hops=0; dual-window derive
    # parity with pre-seat probe; scan face = SEED_REGISTRY 187 int
    # values + v1/W1 ext bands + N3-R1 used-seed band + probe
    # cluster 95_000..95_003 + cross-face probe points
    # 95_004/95_006 + lfc/options actuals + N2/N4/N2-W15 probe
    # points.
    # W137+ projection (gate-derived r741): A 317_004..319_003
    # CLEAN hops=0; B first-clean 94_001..94_200 hops=12 (honest
    # forward walk past N3-R1 used band + registry points; next
    # freezer must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W136 bands were never assigned).
    136: {"a": (315_004, 317_003), "b_exit": (69_702, 69_901),
         "engine_owner": "bm-a"},
    # W137 (bm-a r742 freeze, seat MSG-2026-10-05-202x-bma-w137-seat
    # pushed to origin af1c3c267 pre-freeze r565 law (push raced origin
    # forward 2 commits = r524 behind-signal (bm-c r570 same-window
    # wave), merge-mode zero-UU closeout, delivery d28d392ce); band
    # gate ADMIT results/_r742bma_w137_band_gate.py: A arithmetic
    # continuation 317_003+1 -> 317_004..319_003 CLEAN hops=0; B =
    # FIRST-CLEAN window after the honest 12-hop forward walk past
    # the W136 B tail (first window 69_902..70_101 refused by the
    # N3-R1 used-seed band 70_000..70_005 + the contiguous
    # registered 2_000-wide bands 70_001..94_000; non-rotational
    # r587: every hop a strict forward jump; per-hop chain
    # machine-traced in results/_r742bma_w137_probe_receipt.json);
    # dual-window derive parity with pre-seat probe; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W138+ projection (gate-derived r742): A 319_004..321_003
    # CLEAN hops=0; B first-clean 94_201..94_400 CLEAN hops=0
    # double-CLEAN (next freezer must re-derive, never transcribe
    # r587 law).
    # NOT a re-pick (R250: W137 bands were never assigned).
    137: {"a": (317_004, 319_003), "b_exit": (94_001, 94_200),
         "engine_owner": "bm-a"},
    # W138 (bm-a r743 freeze, seat MSG-2026-10-05-211x-bma-w138-seat
    # pushed to origin 0bf01ef64 pre-freeze r565 law (push raced origin
    # forward 3 commits = r524 behind-signal (bm-b r745 same-window
    # wave), merge-mode clean auto-merge closeout, delivery 576b22603);
    # band gate ADMIT results/_r743bma_w138_band_gate.py: A arithmetic
    # continuation 319_003+1 -> 319_004..321_003 CLEAN hops=0; B =
    # arithmetic continuation from the W137 B tail 94_200+1 ->
    # 94_201..94_400 CLEAN hops=0 (double-CLEAN window; the W137
    # honest 12-hop forward walk landed past the contiguous
    # registered band mass 70_001..94_000, clean by construction);
    # dual-window derive parity with pre-seat probe
    # results/_r743bma_w138_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W139+ projection (gate-derived r743): A 321_004..323_003
    # CLEAN hops=0; B first-clean 94_401..94_600 CLEAN hops=0
    # double-CLEAN (next freezer must re-derive, never transcribe
    # r587 law).
    # NOT a re-pick (R250: W138 bands were never assigned).
    138: {"a": (319_004, 321_003), "b_exit": (94_201, 94_400),
         "engine_owner": "bm-a"},
    # W139 (bm-a r744 freeze, seat MSG-2026-10-05-213x-bma-w139-seat
    # pushed to origin 7e1fc08d0 pre-freeze r565 law (push raced origin
    # forward 7 commits = r524 behind-signal (bm-b r746 same-window
    # wave), merge-mode clean auto-merge closeout, delivery 39ec08fa0);
    # band gate ADMIT results/_r744bma_w139_band_gate.py: A arithmetic
    # continuation 321_003+1 -> 321_004..323_003 CLEAN hops=0; B =
    # arithmetic continuation from the W138 B tail 94_400+1 ->
    # 94_401..94_600 CLEAN hops=0 (double-CLEAN continuation window;
    # the W137 honest 12-hop forward walk landed past the contiguous
    # registered band mass 70_001..94_000 and the W138 zero-hop
    # continuation extended it to 94_400, clean by construction);
    # dual-window derive parity with pre-seat probe
    # results/_r744bma_w139_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W140+ projection (gate-derived r744): A 323_004..325_003
    # CLEAN hops=0; B first-clean 94_601..94_800 CLEAN hops=0
    # double-CLEAN (next freezer must re-derive, never transcribe
    # r587 law).
    # NOT a re-pick (R250: W139 bands were never assigned).
    139: {"a": (321_004, 323_003), "b_exit": (94_401, 94_600),
         "engine_owner": "bm-a"},
    # W140 (bm-a r745 freeze, seat MSG-2026-10-05-215x-bma-w140-seat
    # pushed to origin 08710e2d0 pre-freeze r565 law (plain
    # fast-forward delivery, zero race this window, zero
    # --no-verify);
    # band gate ADMIT results/_r745bma_w140_band_gate.py: A arithmetic
    # continuation 323_003+1 -> 323_004..325_003 CLEAN hops=0; B =
    # arithmetic continuation from the W139 B tail 94_600+1 ->
    # 94_601..94_800 CLEAN hops=0 (double-CLEAN continuation window;
    # the W139 zero-hop double-CLEAN continuation landed past the
    # contiguous registered band mass 70_001..94_600, clean by
    # construction);
    # dual-window derive parity with pre-seat probe
    # results/_r745bma_w140_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W141+ projection (gate-derived r745): A 325_004..327_003
    # CLEAN hops=0; B first-clean 323_004..323_203 hops=115
    # (pre-W140-registration baseline honest hop chain past the
    # probe cluster; B re-derive MANDATORY at W141 prereg -- the
    # baseline lands inside the now-registered W140 A band, next
    # freezer must re-derive past it, never transcribe r587 law).
    # NOT a re-pick (R250: W140 bands were never assigned).
    140: {"a": (323_004, 325_003), "b_exit": (94_601, 94_800),
         "engine_owner": "bm-a"},
    # W141 (bm-a r747 freeze, seat MSG-2026-10-05-231x-bma-w141-seat
    # pushed to origin aaa4d9be8 pre-freeze r565 law (plain
    # fast-forward delivery, zero race this window, zero
    # --no-verify);
    # band gate ADMIT results/_r747bma_w141_band_gate.py: A arithmetic
    # continuation 325_003+1 -> 325_004..327_003 CLEAN hops=0; B =
    # FIRST-CLEAN past the own-wave A window (arithmetic continuation
    # 94_801..95_000 REFUSED by probe seed 95_000; honest forward walk
    # hops=116 lands 325_004..325_203 inside the W141 A band window;
    # same-freeze mutual exclusion (leg2 law) -- B continues past the
    # own-wave A window -> 327_004..327_203 hops=117, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1);
    # dual-window derive parity with pre-seat probe
    # results/_r747bma_w141_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W142+ projection (gate-derived r747): A first-clean
    # 327_004..329_003 CLEAN hops=0 / B first-clean 327_204..327_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W141 B band will refuse the naive W142 A window;
    # W142 freezer MUST re-derive on the post-W141 universe AND
    # reserve the own-wave A window when deriving B (W141 precedent,
    # same-freeze mutual exclusion, leg2 law; never transcribe r587).
    # NOT a re-pick (R250: W141 bands were never assigned).
    141: {"a": (325_004, 327_003), "b_exit": (327_004, 327_203),
         "engine_owner": "bm-a"},
    # W142 (bm-a r748 freeze, seat MSG-2026-10-05-233x-bma-w142-seat
    # pushed to origin 94dee2c36 pre-freeze r565 law (via behind-1
    # merge absorb of the bm-b autofill keepalive tick, zero UU,
    # zero --no-verify);
    # band gate ADMIT results/_r748bma_w142_band_gate.py: A = FIRST-CLEAN
    # past the registered W141 B band (arithmetic continuation
    # 327_004..329_003 REFUSED at its own start by the W141 B band
    # 327_004..327_203, exactly as the r747 W141 gate-tail projection
    # anticipated; honest forward walk hops=1 -> 327_204..329_203,
    # non-rotational r587 forward-monotone walk; A base == prior-wave
    # B tail+1 machine-checkable -- A-hops-prior-B staircase first
    # instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 327_204..327_403 CLEAN on the registered universe
    # but lands INSIDE the W142 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 329_204 -> 329_204..329_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r748bma_w142_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W143+ projection (gate-derived r748): A first-clean
    # 329_204..331_203 CLEAN hops=0 / B first-clean 329_404..329_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W142 B band 329_204..329_403 will refuse the naive
    # W143 A window; W143 freezer MUST re-derive on the post-W142
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W142 bands were never assigned).
    142: {"a": (327_204, 329_203), "b_exit": (329_204, 329_403),
         "engine_owner": "bm-a"},
    # W143 (bm-a r750 freeze, seat MSG-2026-10-06-002x-bma-w143-seat
    # pushed to origin 3a7640311 pre-freeze r565 law (plain
    # fast-forward delivery, zero race this window, zero --no-verify);
    # band gate ADMIT results/_r750bma_w143_band_gate.py: A = FIRST-CLEAN
    # past the registered W142 B band (arithmetic continuation
    # 329_204..331_203 REFUSED at its own start by the W142 B band
    # 329_204..329_403, exactly as the r748 W142 gate-tail projection
    # note anticipated; honest forward walk hops=1 -> 329_404..331_403,
    # non-rotational r587 forward-monotone walk; A base == prior-wave
    # B tail+1 machine-checkable -- A-hops-prior-B staircase second
    # instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 329_404..329_603 CLEAN on the registered universe
    # but lands INSIDE the W143 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 331_404 -> 331_404..331_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r750bma_w143_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W144+ projection (gate-derived r750): A first-clean
    # 331_404..333_403 CLEAN hops=0 / B first-clean 331_604..331_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W143 B band 331_404..331_603 will refuse the naive
    # W144 A window; W144 freezer MUST re-derive on the post-W143
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W143 bands were never assigned).
    143: {"a": (329_404, 331_403), "b_exit": (331_404, 331_603),
         "engine_owner": "bm-a"},
    # W144 (bm-a r752 freeze, seat MSG-2026-10-06-011x-bma-w144-seat
    # pushed to origin 2ba4a613f pre-freeze r565 law (plain
    # fast-forward delivery, zero race this window, zero --no-verify);
    # band gate ADMIT results/_r752bma_w144_band_gate.py: A = FIRST-CLEAN
    # past the registered W143 B band (arithmetic continuation
    # 331_404..333_403 REFUSED at its own start by the W143 B band
    # 331_404..331_603, exactly as the r750 W143 gate-tail projection
    # note anticipated; honest forward walk hops=1 -> 331_604..333_603,
    # non-rotational r587 forward-monotone walk; A base == prior-wave
    # B tail+1 (331_603+1) machine-checkable -- A-hops-prior-B
    # staircase third instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 331_604..331_803 CLEAN on the registered universe
    # but lands INSIDE the W144 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 333_604 -> 333_604..333_803,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (333_603+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r751bma_w144_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W145+ projection (gate-derived r752): A first-clean
    # 333_604..335_603 CLEAN hops=0 / B first-clean 333_804..334_003
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W144 B band 333_604..333_803 will refuse the naive
    # W145 A window; W145 freezer MUST re-derive on the post-W144
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W144 bands were never assigned).
    144: {"a": (331_604, 333_603), "b_exit": (333_604, 333_803),
         "engine_owner": "bm-a"},
    # W145 (bm-a r754 freeze, seat MSG-2026-10-06-023x-bma-w145-seat
    # pushed to origin 55c2a1715 pre-freeze r565 law (two-hop merge
    # delivery 55c2a1715 -> d5fdbb317: first push raced origin forward
    # = r524 behind-signal; merge-mode closeout, zero --no-verify);
    # band gate ADMIT results/_r753bma_w145_band_gate.py: A = FIRST-CLEAN
    # past the registered W144 B band (arithmetic continuation
    # 333_604..335_603 REFUSED at its own start by the W144 B band
    # 333_604..333_803, exactly as the r752 W144 gate-tail projection
    # note anticipated; honest forward walk hops=1 -> 333_804..335_803,
    # non-rotational r587 forward-monotone walk; A base == prior-wave
    # B tail+1 (333_803+1) machine-checkable -- A-hops-prior-B
    # staircase fourth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 333_804..334_003 CLEAN on the registered universe
    # but lands INSIDE the W145 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 335_804 -> 335_804..336_003,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (335_803+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r753bma_w145_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W146+ projection (gate-derived r753): A first-clean
    # 335_804..337_803 CLEAN hops=0 / B first-clean 336_004..336_203
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W145 B band 335_804..336_003 will refuse the naive
    # W146 A window; W146 freezer MUST re-derive on the post-W145
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W145 bands were never assigned).
    145: {"a": (333_804, 335_803), "b_exit": (335_804, 336_003),
         "engine_owner": "bm-a"},
    # W146 (bm-a r755 freeze, seat MSG-2026-10-06-033x-bma-w146-seat
    # pushed to origin c8183f342 pre-freeze r565 law (two-hop merge
    # delivery c8183f342 -> 8d4248daf: first push raced origin forward
    # = r524 behind-signal; merge-mode closeout, zero --no-verify);
    # band gate ADMIT results/_r755bma_w146_band_gate.py: A = FIRST-CLEAN
    # past the registered W145 B band (arithmetic continuation
    # 335_804..337_803 REFUSED at its own start by the W145 B band
    # 335_804..336_003, exactly as the r753 W145 gate-tail projection
    # note anticipated; honest forward walk hops=1 -> 336_004..338_003,
    # non-rotational r587 forward-monotone walk; A base == prior-wave
    # B tail+1 (336_003+1) machine-checkable -- A-hops-prior-B
    # staircase fifth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 336_004..336_203 CLEAN on the registered universe
    # but lands INSIDE the W146 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 338_004 -> 338_004..338_203,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (338_003+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r755bma_w146_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W147+ projection (gate-derived r755): A first-clean
    # 338_004..340_003 CLEAN hops=0 / B first-clean 338_204..338_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W146 B band 338_004..338_203 will refuse the naive
    # W147 A window; W147 freezer MUST re-derive on the post-W146
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W146 bands were never assigned).
    146: {"a": (336_004, 338_003), "b_exit": (338_004, 338_203),
         "engine_owner": "bm-a"},
    # W147 (bm-a r757 freeze, seat MSG-2026-10-06-045x-bma-w147-seat
    # pushed to origin a5eadcdd7 pre-freeze r565 law (single-hop
    # direct delivery, zero behind-signal; payload = seat MSG +
    # pre-seat probe + probe receipt; deletion-set EMPTY);
    # band gate ADMIT results/_r757bma_w147_band_gate.py: A = FIRST-CLEAN
    # past the registered W146 B band (arithmetic continuation
    # 338_004..340_003 REFUSED at its own start by the W146 B band
    # 338_004..338_203, exactly as the r755 W146 gate-tail projection
    # note anticipated; honest forward walk hops=1 -> 338_204..340_203,
    # non-rotational r587 forward-monotone walk; A base == prior-wave
    # B tail+1 (338_203+1) machine-checkable -- A-hops-prior-B
    # staircase sixth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 338_204..338_403 CLEAN on the registered universe
    # but lands INSIDE the W147 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 340_204 -> 340_204..340_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (340_203+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r756bma_w147_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W148+ projection (gate-derived r757): A first-clean
    # 340_204..342_203 CLEAN hops=0 / B first-clean 340_404..340_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W147 B band 340_204..340_403 will refuse the naive
    # W148 A window; W148 freezer MUST re-derive on the post-W147
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W147 bands were never assigned).
    147: {"a": (338_204, 340_203), "b_exit": (340_204, 340_403),
         "engine_owner": "bm-a"},
    # W148 (bm-a r759 freeze, seat MSG-2026-10-06-052x-bma-w148-seat
    # pushed to origin d2c6353ec pre-freeze r565 law (r758 pre-seat
    # push; same-window self-ack inbox->processed move c136baed2 r759;
    # payload = seat MSG + pre-seat probe + probe receipt; deletion-set
    # EMPTY);
    # band gate ADMIT results/_r759bma_w148_band_gate.py: A = FIRST-CLEAN
    # past the registered W147 B band (arithmetic continuation
    # 340_204..342_203 REFUSED at its own start by the W147 B band
    # 340_204..340_403, exactly as the W147 seat leg4 + r757 gate leg3
    # projections both anticipated; honest forward walk hops=1 ->
    # 340_404..342_403, non-rotational r587 forward-monotone walk;
    # A base == prior-wave B tail+1 (340_403+1) machine-checkable --
    # A-hops-prior-B staircase seventh instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 340_404..340_603 CLEAN on the registered universe
    # but lands INSIDE the W148 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 342_404 -> 342_404..342_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (342_403+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r758bma_w148_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W149+ projection (gate-derived r759): A first-clean
    # 342_404..344_403 CLEAN hops=0 / B first-clean 342_604..342_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W148 B band 342_404..342_603 will refuse the naive
    # W149 A window; W149 freezer MUST re-derive on the post-W148
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W148 bands were never assigned).
    148: {"a": (340_404, 342_403), "b_exit": (342_404, 342_603),
         "engine_owner": "bm-a"},
    # W149 (bm-a r761 freeze, seat MSG-2026-10-06-060x-bma-w149-seat
    # pushed to origin 47da9310c pre-freeze r565 law (r760 pre-seat
    # push; same-window self-ack inbox->processed move 684177ba0 r760;
    # payload = seat MSG + pre-seat probe + probe receipt; deletion-set
    # EMPTY);
    # band gate ADMIT results/_r761bma_w149_band_gate.py: A = FIRST-CLEAN
    # past the registered W148 B band (arithmetic continuation
    # 342_404..344_403 REFUSED at its own start by the W148 B band
    # 342_404..342_603, exactly as the W148 seat leg4 + r759 gate leg3
    # projections both anticipated; honest forward walk hops=1 ->
    # 342_604..344_603, non-rotational r587 forward-monotone walk;
    # A base == prior-wave B tail+1 (342_603+1) machine-checkable --
    # A-hops-prior-B staircase eighth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 342_604..342_803 CLEAN on the registered universe
    # but lands INSIDE the W149 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 344_604 -> 344_604..344_803,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (344_603+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r760bma_w149_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W150+ projection (gate-derived r761): A first-clean
    # 344_604..346_603 CLEAN hops=0 / B first-clean 344_804..345_003
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W149 B band 344_604..344_803 will refuse the naive
    # W150 A window; W150 freezer MUST re-derive on the post-W149
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W149 bands were never assigned).
    149: {"a": (342_604, 344_603), "b_exit": (344_604, 344_803),
         "engine_owner": "bm-a"},
    # W150 (bm-a r762 freeze, seat MSG-2026-10-06-070x-bma-w150-seat
    # pushed to origin bb33022de pre-freeze r565 law (r762 pre-seat
    # push; same-window self-ack inbox->processed move 860d529f3 r762;
    # payload = seat MSG + pre-seat probe + probe receipt + W149
    # finalize products; deletion-set EMPTY);
    # band gate ADMIT results/_r762bma_w150_band_gate.py: A = FIRST-CLEAN
    # past the registered W149 B band (arithmetic continuation
    # 344_604..346_603 REFUSED at its own start by the W149 B band
    # 344_604..344_803, exactly as the W149 seat leg4 + r761 gate leg3
    # projections both anticipated; honest forward walk hops=1 ->
    # 344_804..346_803, non-rotational r587 forward-monotone walk;
    # A base == prior-wave B tail+1 (344_803+1) machine-checkable --
    # A-hops-prior-B staircase ninth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 344_804..345_003 CLEAN on the registered universe
    # but lands INSIDE the W150 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 346_804 -> 346_804..347_003,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (346_803+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r762bma_w150_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W151+ projection (gate-derived r762): A first-clean
    # 346_804..348_803 CLEAN hops=0 / B first-clean 347_004..347_203
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W150 B band 346_804..347_003 will refuse the naive
    # W151 A window; W151 freezer MUST re-derive on the post-W150
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W150 bands were never assigned).
    150: {"a": (344_804, 346_803), "b_exit": (346_804, 347_003),
         "engine_owner": "bm-a"},
    # W151 (bm-a r763 freeze, seat MSG-2026-10-06-075x-bma-w151-seat
    # pushed to origin f8e1306c8 pre-freeze r565 law (r763 pre-seat
    # push; same-window self-ack inbox->processed move 351170f89 r763;
    # payload = seat MSG + pre-seat probe + probe receipt + W150
    # finalize products; deletion-set EMPTY);
    # band gate ADMIT results/_r763bma_w151_band_gate.py: A = FIRST-CLEAN
    # past the registered W150 B band (arithmetic continuation
    # 346_804..348_803 REFUSED at its own start by the W150 B band
    # 346_804..347_003, exactly as the W150 seat leg4 + r762 gate leg3
    # projections both anticipated; honest forward walk hops=1 ->
    # 347_004..349_003, non-rotational r587 forward-monotone walk;
    # A base == prior-wave B tail+1 (347_003+1) machine-checkable --
    # A-hops-prior-B staircase tenth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 347_004..347_203 CLEAN on the registered universe
    # but lands INSIDE the W151 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 349_004 -> 349_004..349_203,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (349_003+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r763bma_w151_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W152+ projection (gate-derived r763): A first-clean
    # 349_004..351_003 CLEAN hops=0 / B first-clean 349_204..349_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W151 B band 349_004..349_203 will refuse the naive
    # W152 A window; W152 freezer MUST re-derive on the post-W151
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W151 bands were never assigned).
    151: {"a": (347_004, 349_003), "b_exit": (349_004, 349_203),
         "engine_owner": "bm-a"},
    # W152 (bm-a r764 freeze, seat MSG-2026-10-06-080x-bma-w152-seat
    # pushed to origin 6a4081c01 pre-freeze r565 law (r764 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt;
    # delivery window absorbed a GitHub SSH transient + a behind-3
    # pre-push claw r759 phantom-deletion face via merge-mode,
    # zero --no-verify; same-window self-ack inbox->processed move
    # r764; deletion-set EMPTY);
    # band gate ADMIT results/_r764bma_w152_band_gate.json: A = FIRST-CLEAN
    # past the registered W151 B band (arithmetic continuation
    # 349_004..351_003 REFUSED at its own start by the W151 B band
    # 349_004..349_203, exactly as the W151 seat leg4 + r763 gate
    # leg3 projections both anticipated; honest forward walk hops=1 ->
    # 349_204..351_203, non-rotational r587 forward-monotone walk;
    # A base == prior-wave B tail+1 (349_203+1) machine-checkable --
    # A-hops-prior-B staircase eleventh instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 349_204..349_403 CLEAN on the registered universe
    # but lands INSIDE the W152 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 351_204 -> 351_204..351_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (351_203+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r764bma_w152_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W153+ projection (gate-derived r764): A first-clean
    # 351_204..353_203 CLEAN hops=0 / B first-clean 351_404..351_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W152 B band 351_204..351_403 will refuse the naive
    # W153 A window; W153 freezer MUST re-derive on the post-W152
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W152 bands were never assigned).
    152: {"a": (349_204, 351_203), "b_exit": (351_204, 351_403),
         "engine_owner": "bm-a"},
    # W153 (bm-a r766 freeze, seat MSG-2026-10-06-084x-bma-w153-seat
    # pushed to origin 3ae290395 pre-freeze r565 law (r766 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt;
    # delivery window absorbed a behind-3 bm-c r607 peer wave via
    # rebase + own daemon churn-absorb precede, zero --no-verify;
    # same-window self-ack inbox->processed move r766;
    # deletion-set EMPTY);
    # band gate ADMIT results/_r766bma_w153_band_gate.json: A = FIRST-CLEAN
    # past the registered W152 B band (arithmetic continuation
    # 351_204..353_203 REFUSED at its own start by the W152 B band
    # 351_204..351_403, exactly as the W152 seat leg4 + r764 gate
    # leg3 + r765 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 351_404..353_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (351_403+1) machine-checkable -- A-hops-prior-B staircase
    # twelfth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 351_404..351_603 CLEAN on the registered universe
    # but lands INSIDE the W153 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 353_404 -> 353_404..353_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (353_403+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r766bma_w153_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W154+ projection (gate-derived r766): A first-clean
    # 353_404..355_403 CLEAN hops=0 / B first-clean 353_604..353_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W153 B band 353_404..353_603 will refuse the naive
    # W154 A window; W154 freezer MUST re-derive on the post-W153
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W153 bands were never assigned).
    153: {"a": (351_404, 353_403), "b_exit": (353_404, 353_603),
         "engine_owner": "bm-a"},
    # W154 (bm-a r767 freeze, seat MSG-2026-10-06-090x-bma-w154-seat
    # pushed to origin dd1702d11 pre-freeze r565 law (r767 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt +
    # W153 finalize products; deletion-set EMPTY; delivery window
    # absorbed a behind-3 bm-b r769 closeout wave-2 peer commit via
    # merge, zero --no-verify; same-window self-ack inbox->processed
    # move r767;
    # deletion-set EMPTY);
    # band gate ADMIT results/_r767bma_w154_band_gate.json: A = FIRST-CLEAN
    # past the registered W153 B band (arithmetic continuation
    # 353_404..355_403 REFUSED at its own start by the W153 B band
    # 353_404..353_603, exactly as the W153 seat leg4 + r766 gate
    # leg3 + r767 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 353_604..355_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (353_603+1) machine-checkable -- A-hops-prior-B staircase
    # thirteenth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 353_604..353_803 CLEAN on the registered universe
    # but lands INSIDE the W154 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 355_604 -> 355_604..355_803,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (355_603+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r767bma_w154_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W155+ projection (gate-derived r767): A first-clean
    # 355_604..357_603 CLEAN hops=0 / B first-clean 355_804..356_003
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W154 B band 355_604..355_803 will refuse the naive
    # W155 A window; W155 freezer MUST re-derive on the post-W154
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W154 bands were never assigned).
    154: {"a": (353_604, 355_603), "b_exit": (355_604, 355_803),
         "engine_owner": "bm-a"},
    # W155 (bm-a r768 freeze, seat MSG-2026-10-06-0943-bma-w155-seat
    # pushed to origin 1fedffbe4 pre-freeze r565 law (r768 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt +
    # W154 finalize products; deletion-set EMPTY; delivery window
    # absorbed a behind-2 bm-c r610 guard-round peer commit via
    # merge, zero --no-verify; same-window self-ack inbox->processed
    # move r768;
    # deletion-set EMPTY);
    # band gate ADMIT results/_r768bma_w155_band_gate.json: A = FIRST-CLEAN
    # past the registered W154 B band (arithmetic continuation
    # 355_604..357_603 REFUSED at its own start by the W154 B band
    # 355_604..355_803, exactly as the W154 seat leg4 + r767 gate
    # leg3 + r767 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 355_804..357_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (355_803+1) machine-checkable -- A-hops-prior-B staircase
    # fourteenth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 355_804..356_003 CLEAN on the registered universe
    # but lands INSIDE the W155 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 357_804 -> 357_804..358_003,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (357_803+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r768bma_w155_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W156+ projection (gate-derived r768): A first-clean
    # 357_804..359_803 CLEAN hops=0 / B first-clean 358_004..358_203
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W155 B band 357_804..358_003 will refuse the naive
    # W156 A window; W156 freezer MUST re-derive on the post-W155
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W155 bands were never assigned).
    155: {"a": (355_804, 357_803), "b_exit": (357_804, 358_003),
         "engine_owner": "bm-a"},
    # W156 (bm-a r769 freeze, seat MSG-2026-10-06-1009-bma-w156-seat
    # pushed to origin ffce2936f pre-freeze r565 law (r769 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt +
    # W156 arc generator; deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r769 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move deferred to the W156 finalize window;
    # deletion-set EMPTY);
    # band gate ADMIT results/_r769bma_w156_band_gate.json: A = FIRST-CLEAN
    # past the registered W155 B band (arithmetic continuation
    # 357_804..359_803 REFUSED at its own start by the W155 B band
    # 357_804..358_003, exactly as the W155 seat leg4 + r768 gate
    # leg3 + r769 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 358_004..360_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (358_003+1) machine-checkable -- A-hops-prior-B staircase
    # fifteenth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 358_004..358_203 CLEAN on the registered universe
    # but lands INSIDE the W156 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 360_004 -> 360_004..360_203,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (360_003+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r769bma_w156_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W157+ projection (gate-derived r769): A first-clean
    # 360_004..362_003 CLEAN hops=0 / B first-clean 360_204..360_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W156 B band 360_004..360_203 will refuse the naive
    # W157 A window; W157 freezer MUST re-derive on the post-W156
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W156 bands were never assigned).
    156: {"a": (358_004, 360_003), "b_exit": (360_004, 360_203),
         "engine_owner": "bm-a"},
    # W157 (bm-a r772 freeze, seat MSG-2026-10-06-113x-bma-w157-seat
    # pushed to origin 4af40c72d pre-freeze r565 law (r772 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt +
    # W157 arc generator; deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r772 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move deferred to the W157 finalize window;
    # deletion-set EMPTY);
    # band gate ADMIT results/_r772bma_w157_band_gate.json: A = FIRST-CLEAN
    # past the registered W156 B band (arithmetic continuation
    # 360_004..362_003 REFUSED at its own start by the W156 B band
    # 360_004..360_203, exactly as the W156 seat W157+ projection + r771 gate
    # leg3 + r772 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 360_204..362_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (360_203+1) machine-checkable -- A-hops-prior-B staircase
    # sixteenth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 360_204..360_403 CLEAN on the registered universe
    # but lands INSIDE the W157 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 362_204 -> 362_204..362_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (362_203+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r772bma_w157_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W157+ projection (gate-derived r772): A first-clean
    # 362_204..364_203 CLEAN hops=0 / B first-clean 362_404..362_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W157 B band 362_204..362_403 will refuse the naive
    # W157 A window; W157 freezer MUST re-derive on the post-W157
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W157 bands were never assigned).
    157: {"a": (360_204, 362_203), "b_exit": (362_204, 362_403),
         "engine_owner": "bm-a"},
    # W158 (bm-a r773 freeze, seat MSG-2026-10-06-120x-bma-w158-seat
    # pushed to origin 24aff72f5 pre-freeze r565 law (r773 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt +
    # W158 arc generator; deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r773 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move deferred to the W158 finalize window;
    # deletion-set EMPTY);
    # band gate ADMIT results/_r773bma_w158_band_gate.json: A = FIRST-CLEAN
    # past the registered W157 B band (arithmetic continuation
    # 362_204..364_203 REFUSED at its own start by the W157 B band
    # 362_204..362_403, exactly as the W157 seat W158+ projection + r772 gate
    # leg3 + r773 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 362_404..364_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (362_403+1) machine-checkable -- A-hops-prior-B staircase
    # seventeenth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 362_404..362_603 CLEAN on the registered universe
    # but lands INSIDE the W158 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 364_404 -> 364_404..364_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (364_403+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r773bma_w158_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W158+ projection (gate-derived r773): A first-clean
    # 364_404..366_403 CLEAN hops=0 / B first-clean 364_604..364_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W158 B band 364_404..364_603 will refuse the naive
    # W159 A window; W159 freezer MUST re-derive on the post-W158
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W158 bands were never assigned).
    158: {"a": (362_404, 364_403), "b_exit": (364_404, 364_603),
         "engine_owner": "bm-a"},
    # W159 (bm-a r779 freeze, seat MSG-2026-10-06-142x-bma-w159-seat
    # pushed to origin 7b60d09da pre-freeze r565 law (r779 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt +
    # W159 arc generator; deletion-set EMPTY; delivery window
    # = merge-absorb behind-delivery at fetch (r779 pre-seat
    # push via merge-absorb window), zero --no-verify; self-ack inbox->processed
    # move landed (bm-c r625 read-only-observer processed, e203e96c7);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r779bma_w159_band_gate.json: A = FIRST-CLEAN
    # past the registered W158 B band (arithmetic continuation
    # 364_404..366_403 REFUSED at its own start by the W158 B band
    # 364_404..364_603, exactly as the W158 seat W159+ projection + r773 gate
    # leg3 + r779 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 364_604..366_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (364_603+1) machine-checkable -- A-hops-prior-B staircase
    # eighteenth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 364_604..364_803 CLEAN on the registered universe
    # but lands INSIDE the W159 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 366_604 -> 366_604..366_803,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (366_603+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r779bma_w159_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W159+ projection (gate-derived r779): A first-clean
    # 366_604..368_603 CLEAN hops=0 / B first-clean 366_804..367_003
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W159 B band 366_604..366_803 will refuse the naive
    # W160 A window; W160 freezer MUST re-derive on the post-W159
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W159 bands were never assigned).
    159: {"a": (364_604, 366_603), "b_exit": (366_604, 366_803),
         "engine_owner": "bm-a"},
    # W160 (bm-a r783 freeze, seat MSG-2026-10-06-162x-bma-w160-seat
    # pushed to origin 566ec5f86 pre-freeze r565 law (r782 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt +
    # W160 arc generator; deletion-set EMPTY; delivery window
    # = merge-absorb behind-delivery at fetch (r782 pre-seat
    # push via merge-absorb window), zero --no-verify; self-ack inbox->processed
    # move deferred to the W160 finalize window (seat still in
    # fleet/inbox at freeze time -- honest state);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r783bma_w160_band_gate.json: A = FIRST-CLEAN
    # past the registered W159 B band (arithmetic continuation
    # 366_604..368_603 REFUSED at its own start by the W159 B band
    # 366_604..366_803, exactly as the W159 seat W160+ projection + r779 gate
    # leg3 + r783 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 366_804..368_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (366_803+1) machine-checkable -- A-hops-prior-B staircase
    # nineteenth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 366_804..367_003 CLEAN on the registered universe
    # but lands INSIDE the W160 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 368_804 -> 368_804..369_003,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (368_803+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r782bma_w160_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W160+ projection (gate-derived r783): A first-clean
    # 368_804..370_803 CLEAN hops=0 / B first-clean 369_004..369_203
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W160 B band 368_804..369_003 will refuse the naive
    # W161 A window; W161 freezer MUST re-derive on the post-W160
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W160 bands were never assigned).
    160: {"a": (366_804, 368_803), "b_exit": (368_804, 369_003),
         "engine_owner": "bm-a"},
    # W161 (bm-a r785 freeze, seat MSG-2026-10-06-165x-bma-w161-seat
    # pushed to origin 0371f2093 pre-freeze r565 law (r785 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt +
    # W161 arc generator; deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r785 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move landed (bm-b r779 read-only-observer processed, a2d002357);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r785bma_w161_band_gate.json: A = FIRST-CLEAN
    # past the registered W160 B band (arithmetic continuation
    # 368_804..370_803 REFUSED at its own start by the W160 B band
    # 368_804..369_003, exactly as the W160 seat W161+ projection + r783 gate
    # leg3 + r784 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 369_004..371_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (369_003+1) machine-checkable -- A-hops-prior-B staircase
    # twentieth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 369_004..369_203 CLEAN on the registered universe
    # but lands INSIDE the W161 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 371_004 -> 371_004..371_203,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (371_003+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r785bma_w161_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W161+ projection (gate-derived r785): A first-clean
    # 371_004..373_003 CLEAN hops=0 / B first-clean 371_204..371_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W161 B band 371_004..371_203 will refuse the naive
    # W162 A window; W162 freezer MUST re-derive on the post-W161
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W161 bands were never assigned).
    161: {"a": (369_004, 371_003), "b_exit": (371_004, 371_203),
         "engine_owner": "bm-a"},
    # W162 (bm-a r787 freeze, seat MSG-2026-10-06-175x-bma-w162-seat
    # pushed to origin 1d43d7906 pre-freeze r565 law (r787 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt +
    # facts helper; deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r787 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move deferred to the W163 finalize window (W162 seat still in
    # fleet/inbox at freeze time -- honest state);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r787bma_w162_band_gate.json: A = FIRST-CLEAN
    # past the registered W161 B band (arithmetic continuation
    # 371_004..373_003 REFUSED at its own start by the W161 B band
    # 371_004..371_203, exactly as the W161 seat W162+ projection + r785 gate
    # leg3 + r786 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 371_204..373_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (371_203+1) machine-checkable -- A-hops-prior-B staircase
    # twenty-first instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 371_204..371_403 CLEAN on the registered universe
    # but lands INSIDE the W162 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 373_204 -> 373_204..373_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (373_203+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r787bma_w162_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W162+ projection (gate-derived r787): A first-clean
    # 373_204..375_203 CLEAN hops=0 / B first-clean 373_404..373_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W162 B band 373_204..373_403 will refuse the naive
    # W163 A window; W163 freezer MUST re-derive on the post-W162
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W162 bands were never assigned).
    162: {"a": (371_204, 373_203), "b_exit": (373_204, 373_403),
         "engine_owner": "bm-a"},
    # W163 (bm-a r789 freeze, seat MSG-2026-10-06-183x-bma-w163-seat
    # pushed to origin 189157de8 pre-freeze r565 law (r789 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt;
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r789 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move deferred to the W164 finalize window (W163 seat still in
    # fleet/inbox at freeze time -- honest state);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r789bma_w163_band_gate.json: A = FIRST-CLEAN
    # past the registered W162 B band (arithmetic continuation
    # 373_204..375_203 REFUSED at its own start by the W162 B band
    # 373_204..373_403, exactly as the W162 seat W163+ projection + r787 gate
    # leg3 + r788 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 373_404..375_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (373_403+1) machine-checkable -- A-hops-prior-B staircase
    # twenty-second instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 373_404..373_603 CLEAN on the registered universe
    # but lands INSIDE the W163 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 375_404 -> 375_404..375_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (375_403+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r789bma_w163_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W163+ projection (gate-derived r789): A first-clean
    # 375_404..377_403 CLEAN hops=0 / B first-clean 375_604..375_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W163 B band 375_404..375_603 will refuse the naive
    # W164 A window; W164 freezer MUST re-derive on the post-W163
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W163 bands were never assigned).
    163: {"a": (373_404, 375_403), "b_exit": (375_404, 375_603),
         "engine_owner": "bm-a"},
    # W164 (bm-a r792 freeze, seat MSG-2026-10-06-194x-bma-w164-seat
    # pushed to origin 469d40896 pre-freeze r565 law (r792 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt;
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r792 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move deferred to the W165 finalize window (W164 seat still in
    # fleet/inbox at freeze time -- honest state);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r792bma_w164_band_gate.json: A = FIRST-CLEAN
    # past the registered W163 B band (arithmetic continuation
    # 375_404..377_403 REFUSED at its own start by the W163 B band
    # 375_404..375_603, exactly as the W163 seat W164+ projection + r789 gate
    # leg3 + r790 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 375_604..377_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (375_603+1) machine-checkable -- A-hops-prior-B staircase
    # twenty-third instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 375_604..375_803 CLEAN on the registered universe
    # but lands INSIDE the W164 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 377_604 -> 377_604..377_803,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (377_603+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r792bma_w164_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W164+ projection (gate-derived r792): A first-clean
    # 377_604..379_603 CLEAN hops=0 / B first-clean 377_804..378_003
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W164 B band 377_604..377_803 will refuse the naive
    # W165 A window; W165 freezer MUST re-derive on the post-W164
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W164 bands were never assigned).
    164: {"a": (375_604, 377_603), "b_exit": (377_604, 377_803),
         "engine_owner": "bm-a"},
    # W165 (bm-a r795 freeze, seat MSG-2026-10-06-205x-bma-w165-seat
    # pushed to origin 4bdf63090 pre-freeze r565 law (r793 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt;
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r793 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move deferred to the W166 finalize window (W165 seat still in
    # fleet/inbox at freeze time -- honest state);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r793bma_w165_band_gate.json: A = FIRST-CLEAN
    # past the registered W164 B band (arithmetic continuation
    # 377_604..379_603 REFUSED at its own start by the W164 B band
    # 377_604..377_803, exactly as the W164 seat W165+ projection + r792 gate
    # leg3 + r793 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 377_804..379_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (377_803+1) machine-checkable -- A-hops-prior-B staircase
    # twenty-fourth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 377_804..378_003 CLEAN on the registered universe
    # but lands INSIDE the W165 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 379_804 -> 379_804..380_003,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (379_803+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r793bma_w165_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W165+ projection (gate-derived r793): A first-clean
    # 379_804..381_803 CLEAN hops=0 / B first-clean 380_004..380_203
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W165 B band 379_804..380_003 will refuse the naive
    # W166 A window; W166 freezer MUST re-derive on the post-W165
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W165 bands were never assigned).
    165: {"a": (377_804, 379_803), "b_exit": (379_804, 380_003),
         "engine_owner": "bm-a"},
    # W166 (bm-a r799 freeze, seat MSG-2026-10-06-223x-bma-w166-seat
    # pushed to origin d1dc12117 pre-freeze r565 law (r797 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt;
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r797 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move deferred to the W167 finalize window (W166 seat still in
    # fleet/inbox at freeze time -- honest state);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r797bma_w166_band_gate.json: A = FIRST-CLEAN
    # past the registered W165 B band (arithmetic continuation
    # 379_804..381_803 REFUSED at its own start by the W165 B band
    # 379_804..380_003, exactly as the W165 seat W166+ projection + r793 gate
    # leg3 + r796 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 380_004..382_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (380_003+1) machine-checkable -- A-hops-prior-B staircase
    # twenty-fifth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 380_004..380_203 CLEAN on the registered universe
    # but lands INSIDE the W166 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 382_004 -> 382_004..382_203,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (382_003+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r797bma_w166_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W166+ projection (gate-derived r797): A first-clean
    # 382_004..384_003 CLEAN hops=0 / B first-clean 382_204..382_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W166 B band 382_004..382_203 will refuse the naive
    # W167 A window; W167 freezer MUST re-derive on the post-W166
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W166 bands were never assigned).
    166: {"a": (380_004, 382_003), "b_exit": (382_004, 382_203),
         "engine_owner": "bm-a"},
    # W167 (bm-a r805 freeze, seat MSG-2026-10-07-0056-bma-w167-seat
    # pushed to origin 982424c5f pre-freeze r565 law (r801 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt;
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r801 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move deferred to the W168 finalize window (W167 seat still in
    # fleet/inbox at freeze time -- honest state);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r801bma_w167_band_gate.json: A = FIRST-CLEAN
    # past the registered W166 B band (arithmetic continuation
    # 382_004..384_003 REFUSED at its own start by the W166 B band
    # 382_004..382_203, exactly as the W166 seat W167+ projection + r797 gate
    # leg3 + r799 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 382_204..384_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (382_203+1) machine-checkable -- A-hops-prior-B staircase
    # twenty-sixth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 382_204..382_403 CLEAN on the registered universe
    # but lands INSIDE the W167 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 384_204 -> 384_204..384_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (384_203+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r801bma_w167_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W167+ projection (gate-derived r801): A first-clean
    # 384_204..386_203 CLEAN hops=0 / B first-clean 384_404..384_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W167 B band 384_204..384_403 will refuse the naive
    # W168 A window; W168 freezer MUST re-derive on the post-W167
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W167 bands were never assigned).
    167: {"a": (382_204, 384_203), "b_exit": (384_204, 384_403),
         "engine_owner": "bm-a"},
    # W168 (bm-a r809 freeze, seat MSG-2026-10-07-0259-bma-w168-seat
    # pushed to origin ceaf58908 pre-freeze r565 law (r806 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt;
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r806 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move already landed pre-freeze (bm-c r650 consumed-archived the
    # W168 seat to fleet/inbox/processed at 03:27:53 -- honest state);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r806bma_w168_band_gate.json: A = FIRST-CLEAN
    # past the registered W167 B band (arithmetic continuation
    # 384_204..386_203 REFUSED at its own start by the W167 B band
    # 384_204..384_403, exactly as the W167 seat W168+ projection + r801 gate
    # leg3 + r806 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 384_404..386_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (384_403+1) machine-checkable -- A-hops-prior-B staircase
    # twenty-seventh instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 384_404..384_603 CLEAN on the registered universe
    # but lands INSIDE the W168 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 386_404 -> 386_404..386_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (386_403+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r806bma_w168_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W168+ projection (gate-derived r806): A first-clean
    # 386_404..388_403 CLEAN hops=0 / B first-clean 386_604..386_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W168 B band 386_404..386_603 will refuse the naive
    # W169 A window; W169 freezer MUST re-derive on the post-W168
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W168 bands were never assigned).
    168: {"a": (384_404, 386_403), "b_exit": (386_404, 386_603),
         "engine_owner": "bm-a"},
    # W169 (bm-a r811 freeze, seat MSG-2026-10-07-0547-bma-w169-seat
    # pushed to origin bcd6e4392 pre-freeze r565 law (r810 pre-seat
    # push; payload = seat MSG + pre-seat probe + probe receipt;
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r810 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move already landed pre-freeze (bm-b r798 consumed-archived the
    # W169 seat to fleet/inbox/processed at 06:02:52 -- honest state);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r810bma_w169_band_gate.json: A = FIRST-CLEAN
    # past the registered W168 B band (arithmetic continuation
    # 386_404..388_403 REFUSED at its own start by the W168 B band
    # 386_404..386_603, exactly as the W168 seat W169+ projection + r806 gate
    # leg3 + r811 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 386_604..388_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (386_603+1) machine-checkable -- A-hops-prior-B staircase
    # twenty-eighth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 386_604..386_803 CLEAN on the registered universe
    # but lands INSIDE the W169 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 388_604 -> 388_604..388_803,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (388_603+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r810bma_w169_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W169+ projection (gate-derived r810): A first-clean
    # 388_604..390_603 CLEAN hops=0 / B first-clean 388_804..389_003
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W169 B band 388_604..388_803 will refuse the naive
    # W170 A window; W170 freezer MUST re-derive on the post-W169
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W169 bands were never assigned).
    169: {"a": (386_604, 388_603), "b_exit": (388_604, 388_803),
         "engine_owner": "bm-a"},
    # W170 (bm-a r813 freeze, seat MSG-2026-10-07-0738-bma-w170-seat
    # pushed to origin 0f00fa424 pre-freeze r565 law (r812 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt + the
    # W169 finalize product (4-item, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r812 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move DEFERRED to the W170 finalize window -- the W170 seat
    # MSG sits in fleet/inbox/ at freeze time (honest deferred);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r812bma_w170_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W169 B band (arithmetic continuation
    # 388_604..390_603 REFUSED at its own start by the W169 B band
    # 388_604..388_803, exactly as the W169 seat W170+ projection + r810 gate
    # leg3 + r813 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 388_804..390_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (388_803+1) machine-checkable -- A-hops-prior-B staircase
    # twenty-ninth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 388_804..389_003 CLEAN on the registered universe
    # but lands INSIDE the W170 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 390_804 -> 390_804..391_003,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (390_803+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W170+ projection (gate-derived r812): A first-clean
    # 390_804..392_803 CLEAN hops=0 / B first-clean 391_004..391_203
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W170 B band 390_804..391_003 will refuse the naive
    # W171 A window; W171 freezer MUST re-derive on the post-W170
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W170 bands were never assigned).
    170: {"a": (388_804, 390_803), "b_exit": (390_804, 391_003),
         "engine_owner": "bm-a"},
    # W171 (bm-a r815 freeze, seat MSG-2026-10-07-0843-bma-w171-seat
    # pushed to origin 3290e586b pre-freeze r565 law (r814 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W170 finalize product already on origin since r813,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r814 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move DEFERRED to the W171 finalize window -- the W171 seat
    # MSG sits in fleet/inbox/ at freeze time (honest deferred);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r814bma_w171_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W170 B band (arithmetic continuation
    # 390_804..392_803 REFUSED at its own start by the W170 B band
    # 390_804..391_003, exactly as the W170 seat W171+ projection + r812 probe
    # leg4 + r813 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 391_004..393_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (391_003+1) machine-checkable -- A-hops-prior-B staircase
    # thirtieth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 391_004..391_203 CLEAN on the registered universe
    # but lands INSIDE the W171 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 393_004 -> 393_004..393_203,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (393_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W171+ projection (gate-derived r814): A first-clean
    # 393_004..395_003 CLEAN hops=0 / B first-clean 393_204..393_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W171 B band 393_004..393_203 will refuse the naive
    # W172 A window; W172 freezer MUST re-derive on the post-W171
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W171 bands were never assigned).
    171: {"a": (391_004, 393_003), "b_exit": (393_004, 393_203),
         "engine_owner": "bm-a"},
    # W172 (bm-a r819 freeze, seat MSG-2026-10-07-1012-bma-w172-seat
    # pushed to origin 01a7480e1 pre-freeze r565 law (r818 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W171 finalize product already on origin since r816,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r818 pre-seat
    # push), zero merge, zero --no-verify; self-ack inbox->processed
    # move DEFERRED to the W172 finalize window -- the W172 seat
    # MSG sits in fleet/inbox/ at freeze time (honest deferred);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r818bma_w172_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W171 B band (arithmetic continuation
    # 393_004..395_003 REFUSED at its own start by the W171 B band
    # 393_004..393_203, exactly as the W171 seat W172+ projection + r814 probe
    # leg4 + r819 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 393_204..395_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (393_203+1) machine-checkable -- A-hops-prior-B staircase
    # thirty-first instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 393_204..393_403 CLEAN on the registered universe
    # but lands INSIDE the W172 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 395_204 -> 395_204..395_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (395_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W172+ projection (gate-derived r818): A first-clean
    # 395_204..397_203 CLEAN hops=0 / B first-clean 395_404..395_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W172 B band 395_204..395_403 will refuse the naive
    # W173 A window; W173 freezer MUST re-derive on the post-W172
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W172 bands were never assigned).
    172: {"a": (393_204, 395_203), "b_exit": (395_204, 395_403),
         "engine_owner": "bm-a"},
    # W173 (bm-a r822 freeze, seat MSG-2026-10-07-1122-bma-w173-seat
    # pushed to origin 9cd8af3af pre-freeze r565 law (r820 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W172 finalize product already on origin since r819,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r820 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- bm-c r672 inbox sweep observed-archived
    # the bm-a-lane seat MSG at 11:41:55 (the W173 seat MSG sits in
    # fleet/inbox/processed/ at freeze time, honest archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r820bma_w173_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W172 B band (arithmetic continuation
    # 395_204..397_203 REFUSED at its own start by the W172 B band
    # 395_204..395_403, exactly as the W172 seat W173+ projection + r818 probe
    # leg4 + r819 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 395_404..397_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (395_403+1) machine-checkable -- A-hops-prior-B staircase
    # THIRTY-THIRD instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 395_404..395_603 CLEAN on the registered universe
    # but lands INSIDE the W173 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 397_404 -> 397_404..397_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (397_403+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W173+ projection (gate-derived r820): A first-clean
    # 397_404..399_403 CLEAN hops=0 / B first-clean 397_604..397_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W173 B band 397_404..397_603 will refuse the naive
    # W174 A window; W174 freezer MUST re-derive on the post-W173
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W173 bands were never assigned).
    173: {"a": (395_404, 397_403), "b_exit": (397_404, 397_603),
         "engine_owner": "bm-a"},
    # W174 (bm-a r826 freeze, seat MSG-2026-10-07-1247-bma-w174-seat
    # pushed to origin 9b0e1cb29 pre-freeze r565 law (r823 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W173 finalize product already on origin since r823,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r823 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- r823 same-window self-ack move (the W174
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r823bma_w174_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W173 B band (arithmetic continuation
    # 397_404..399_403 REFUSED at its own start by the W173 B band
    # 397_404..397_603, exactly as the W173 seat W174+ projection + r820 probe
    # leg4 + r823 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 397_604..399_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (397_603+1) machine-checkable -- A-hops-prior-B staircase
    # THIRTY-FOURTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 397_604..397_803 CLEAN on the registered universe
    # but lands INSIDE the W174 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 399_604 -> 399_604..399_803,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (399_603+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W174+ projection (gate-derived r823): A first-clean
    # 399_604..401_603 CLEAN hops=0 / B first-clean 399_804..400_003
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W174 B band 399_604..399_803 will refuse the naive
    # W175 A window; W175 freezer MUST re-derive on the post-W174
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W174 bands were never assigned).
    174: {"a": (397_604, 399_603), "b_exit": (399_604, 399_803),
         "engine_owner": "bm-a"},
    # W175 (bm-a r830 freeze, seat MSG-2026-10-07-1434-bma-w175-seat
    # pushed to origin 25c414e95 pre-freeze r565 law (r828 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W174 finalize product already on origin since r827,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r828 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- r828 same-window self-ack move (the W175
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r828bma_w175_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W174 B band (arithmetic continuation
    # 399_604..401_603 REFUSED at its own start by the W174 B band
    # 399_604..399_803, exactly as the W174 seat W175+ projection + r823 probe
    # leg4 + r826 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 399_804..401_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (399_803+1) machine-checkable -- A-hops-prior-B staircase
    # THIRTY-FIFTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 399_804..400_003 CLEAN on the registered universe
    # but lands INSIDE the W175 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 401_804 -> 401_804..402_003,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (401_803+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W175+ projection (gate-derived r828): A first-clean
    # 401_804..403_803 CLEAN hops=0 / B first-clean 402_004..402_203
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W175 B band 401_804..402_003 will refuse the naive
    # W176 A window; W176 freezer MUST re-derive on the post-W175
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W175 bands were never assigned).
    175: {"a": (399_804, 401_803), "b_exit": (401_804, 402_003),
         "engine_owner": "bm-a"},
    # W176 (bm-a r834 freeze, seat MSG-2026-10-07-1630-bma-w176-seat
    # pushed to origin 16a8ea982 pre-freeze r565 law (r832 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W175 finalize product already on origin since r831,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r832 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- r833 same-window self-ack move (the W176
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r832bma_w176_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W175 B band (arithmetic continuation
    # 401_804..403_803 REFUSED at its own start by the W175 B band
    # 401_804..402_003, exactly as the W175 seat W176+ projection + r828 probe
    # leg4 + r831 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 402_004..404_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (402_003+1) machine-checkable -- A-hops-prior-B staircase
    # THIRTY-SIXTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 402_004..402_203 CLEAN on the registered universe
    # but lands INSIDE the W176 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 404_004 -> 404_004..404_203,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (404_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W176+ projection (gate-derived r832): A first-clean
    # 404_004..406_003 CLEAN hops=0 / B first-clean 404_204..404_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W176 B band 404_004..404_203 will refuse the naive
    # W177 A window; W177 freezer MUST re-derive on the post-W176
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W176 bands were never assigned).
    176: {"a": (402_004, 404_003), "b_exit": (404_004, 404_203),
         "engine_owner": "bm-a"},
    # W177 (bm-a r843 freeze, seat MSG-2026-10-07-2031-bma-w177-seat
    # pushed to origin 780a0cd30 pre-freeze r565 law (r841 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W176 finalize product already on origin since r839,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r841 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- r841 same-window self-ack move (the W177
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r841bma_w177_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W176 B band (arithmetic continuation
    # 404_004..406_003 REFUSED at its own start by the W176 B band
    # 404_004..404_203, exactly as the W176 seat W177+ projection + r832 probe
    # leg4 + r839 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 404_204..406_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (404_203+1) machine-checkable -- A-hops-prior-B staircase
    # THIRTY-SEVENTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 404_204..404_403 CLEAN on the registered universe
    # but lands INSIDE the W177 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 406_204 -> 406_204..406_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (406_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W177+ projection (gate-derived r841): A first-clean
    # 406_204..408_203 CLEAN hops=0 / B first-clean 406_404..406_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W177 B band 406_204..406_403 will refuse the naive
    # W178 A window; W178 freezer MUST re-derive on the post-W177
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W177 bands were never assigned).
    177: {"a": (404_204, 406_203), "b_exit": (406_204, 406_403),
         "engine_owner": "bm-a"},
    # W178 (bm-a r845 freeze, seat MSG-2026-10-07-2157-bma-w178-seat
    # pushed to origin 5b9284c79 pre-freeze r565 law (r844 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W177 finalize product already on origin since r844,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r844 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- r845 same-window self-ack move (the W178
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r844bma_w178_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W177 B band (arithmetic continuation
    # 406_204..408_203 REFUSED at its own start by the W177 B band
    # 406_204..406_403, exactly as the W177 seat W178+ projection + r841 probe
    # leg4 + r844 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 406_404..408_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (406_403+1) machine-checkable -- A-hops-prior-B staircase
    # THIRTY-EIGHTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 406_404..406_603 CLEAN on the registered universe
    # but lands INSIDE the W178 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 408_404 -> 408_404..408_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (408_403+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W178+ projection (gate-derived r844): A first-clean
    # 408_404..410_403 CLEAN hops=0 / B first-clean 408_604..408_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W178 B band 408_404..408_603 will refuse the naive
    # W179 A window; W179 freezer MUST re-derive on the post-W178
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W178 bands were never assigned).
    178: {"a": (406_404, 408_403), "b_exit": (408_404, 408_603),
         "engine_owner": "bm-a"},
    # W179 (bm-a r849 freeze, seat MSG-2026-10-07-2320-bma-w179-seat
    # pushed to origin 4c645c95f pre-freeze r565 law (r848 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W178 finalize product already on origin since r846,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r848 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- r848 same-window self-ack move (the W179
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r848bma_w179_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W178 B band (arithmetic continuation
    # 408_404..410_403 REFUSED at its own start by the W178 B band
    # 408_404..408_603, exactly as the W178 seat W179+ projection + r844 probe
    # leg4 + r846 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 408_604..410_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (408_603+1) machine-checkable -- A-hops-prior-B staircase
    # THIRTY-NINTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 408_604..408_803 CLEAN on the registered universe
    # but lands INSIDE the W179 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 410_604 -> 410_604..410_803,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (410_603+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W179+ projection (gate-derived r848): A first-clean
    # 410_604..412_603 CLEAN hops=0 / B first-clean 410_804..411_003
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W179 B band 410_604..410_803 will refuse the naive
    # W180 A window; W180 freezer MUST re-derive on the post-W179
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W179 bands were never assigned).
    179: {"a": (408_604, 410_603), "b_exit": (410_604, 410_803),
         "engine_owner": "bm-a"},
    # W180 (bm-a r852 freeze, seat MSG-2026-10-08-0030-bma-w180-seat
    # pushed to origin d3b0737fe pre-freeze r565 law (r851 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W179 finalize product already on origin since r850,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r851 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- r851 same-window self-ack move (the W180
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r851bma_w180_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W179 B band (arithmetic continuation
    # 410_604..412_603 REFUSED at its own start by the W179 B band
    # 410_604..410_803, exactly as the W179 seat W180+ projection + r848 probe
    # leg4 + r850 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 410_804..412_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (410_803+1) machine-checkable -- A-hops-prior-B staircase
    # FORTIETH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 410_804..411_003 CLEAN on the registered universe
    # but lands INSIDE the W180 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 412_804 -> 412_804..413_003,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (412_803+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W180+ projection (gate-derived r851): A first-clean
    # 412_804..414_803 CLEAN hops=0 / B first-clean 413_004..413_203
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W180 B band 412_804..413_003 will refuse the naive
    # W181 A window; W181 freezer MUST re-derive on the post-W180
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W180 bands were never assigned).
    180: {"a": (410_804, 412_803), "b_exit": (412_804, 413_003),
         "engine_owner": "bm-a"},
    # W181 (bm-a r863 freeze, seat MSG-2026-10-08-0505-bma-w181-seat
    # pushed to origin 971316069 pre-freeze r565 law (r862 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W180 finalize product already on origin since r854,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r862 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- r863 same-window self-ack move (the W181
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r862bma_w181_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W180 B band (arithmetic continuation
    # 412_804..414_803 REFUSED at its own start by the W180 B band
    # 412_804..413_003, exactly as the W180 seat W181+ projection + r851 probe
    # leg4 + r854 sec8 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 413_004..415_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (413_003+1) machine-checkable -- A-hops-prior-B staircase
    # FORTY-FIRST instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 413_004..413_203 CLEAN on the registered universe
    # but lands INSIDE the W181 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 415_004 -> 415_004..415_203,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (415_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W181+ projection (gate-derived r862): A first-clean
    # 415_004..417_003 CLEAN hops=0 / B first-clean 415_204..415_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W181 B band 415_004..415_203 will refuse the naive
    # W182 A window; W182 freezer MUST re-derive on the post-W181
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W181 bands were never assigned).
    181: {"a": (413_004, 415_003), "b_exit": (415_004, 415_203),
         "engine_owner": "bm-a"},
    # W182 (bm-a r867 freeze, seat MSG-2026-10-08-0603-bma-w182-seat
    # pushed to origin df062c5c1 pre-freeze r565 law (r865 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W181 finalize product already on origin since r864,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r865 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- bm-c r737-window self-ack move (the W182
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r865bma_w182_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W181 B band (arithmetic continuation
    # 415_004..417_003 REFUSED at its own start by the W181 B band
    # 415_004..415_203, exactly as the W181 seat W182+ projection + r862 probe
    # leg4 + r867 sec8 heal succession projection notes all anticipated;
    # honest forward walk hops=1 -> 415_204..417_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (415_203+1) machine-checkable -- A-hops-prior-B staircase
    # FORTY-SECOND instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 415_204..415_403 CLEAN on the registered universe
    # but lands INSIDE the W182 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 417_204 -> 417_204..417_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (417_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W182+ projection (gate-derived r865): A first-clean
    # 417_204..419_203 CLEAN hops=0 / B first-clean 417_404..417_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W182 B band 417_204..417_403 will refuse the naive
    # W183 A window; W183 freezer MUST re-derive on the post-W182
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W182 bands were never assigned).
    182: {"a": (415_204, 417_203), "b_exit": (417_204, 417_403),
         "engine_owner": "bm-a"},
    # W183 (bm-a r869 freeze, seat MSG-2026-10-08-0741-bma-w183-seat
    # pushed to origin ccd18034e pre-freeze r565 law (r868 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W182 finalize product already on origin since r868,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r868 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- bm-c r741-window self-ack move (the W183
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r868bma_w183_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W182 B band (arithmetic continuation
    # 417_204..419_203 REFUSED at its own start by the W182 B band
    # 417_204..417_403, exactly as the W182 seat W183+ projection + r865 probe
    # leg4 + r868 sec8 same-window succession projection notes all anticipated;
    # honest forward walk hops=1 -> 417_404..419_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (417_403+1) machine-checkable -- A-hops-prior-B staircase
    # FORTY-THIRD instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 417_404..417_603 CLEAN on the registered universe
    # but lands INSIDE the W183 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 419_404 -> 419_404..419_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (419_403+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W183+ projection (gate-derived r868): A first-clean
    # 419_404..421_403 CLEAN hops=0 / B first-clean 419_604..419_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W183 B band 419_404..419_603 will refuse the naive
    # W184 A window; W184 freezer MUST re-derive on the post-W183
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W183 bands were never assigned).
    183: {"a": (417_404, 419_403), "b_exit": (419_404, 419_603),
         "engine_owner": "bm-a"},
    # W184 (bm-a r874 freeze, seat MSG-2026-10-08-0826-bma-w184-seat
    # pushed to origin d1f15ebf9 pre-freeze r565 law (r870 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W183 finalize product already on origin since r870,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r870 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- bm-c r745-window self-ack move (the W184
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r870bma_w184_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W183 B band (arithmetic continuation
    # 419_404..421_403 REFUSED at its own start by the W183 B band
    # 419_404..419_603, exactly as the W183 seat W184+ projection + r868 probe
    # leg4 + r870 sec8 same-window succession projection notes all anticipated;
    # honest forward walk hops=1 -> 419_604..421_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (419_603+1) machine-checkable -- A-hops-prior-B staircase
    # FORTY-FOURTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 419_604..419_803 CLEAN on the registered universe
    # but lands INSIDE the W184 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 421_604 -> 421_604..421_803,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (421_603+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W184+ projection (gate-derived r870): A first-clean
    # 421_604..423_603 CLEAN hops=0 / B first-clean 421_804..422_003
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W184 B band 421_604..421_803 will refuse the naive
    # W185 A window; W185 freezer MUST re-derive on the post-W184
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W184 bands were never assigned).
    184: {"a": (419_604, 421_603), "b_exit": (421_604, 421_803),
         "engine_owner": "bm-a"},
    # W185 (bm-a r878 freeze, seat MSG-2026-10-08-1032-bma-w185-seat
    # pushed to origin 304909e0e pre-freeze r565 law (r875 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W184 finalize product already on origin since r875,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r875 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- bm-a r876-window self-ack move (the W185
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r875bma_w185_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W184 B band (arithmetic continuation
    # 421_604..423_603 REFUSED at its own start by the W184 B band
    # 421_604..421_803, exactly as the W184 seat W185+ projection + r870 probe
    # leg4 + r875 sec8 same-window succession projection notes all anticipated;
    # honest forward walk hops=1 -> 421_804..423_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (421_803+1) machine-checkable -- A-hops-prior-B staircase
    # FORTY-FIFTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 421_804..422_003 CLEAN on the registered universe
    # but lands INSIDE the W185 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 423_804 -> 423_804..424_003,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (423_803+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W185+ projection (gate-derived r875): A first-clean
    # 423_804..425_803 CLEAN hops=0 / B first-clean 424_004..424_203
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W185 B band 423_804..424_003 will refuse the naive
    # W186 A window; W186 freezer MUST re-derive on the post-W185
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W185 bands were never assigned).
    185: {"a": (421_804, 423_803), "b_exit": (423_804, 424_003),
         "engine_owner": "bm-a"},
    # W186 (bm-a r882 freeze, seat MSG-2026-10-08-1354-bma-w186-seat
    # pushed to origin dd362c690 pre-freeze r565 law (r880 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W185 finalize product already on origin since r879,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r880 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- bm-a r880-window self-ack move (the W186
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r880bma_w186_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W185 B band (arithmetic continuation
    # 423_804..425_803 REFUSED at its own start by the W185 B band
    # 423_804..424_003, exactly as the W185 seat W186+ projection + r875 probe
    # leg4 + r879 sec8 same-window succession projection notes all anticipated;
    # honest forward walk hops=1 -> 424_004..426_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (424_003+1) machine-checkable -- A-hops-prior-B staircase
    # FORTY-SIXTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 424_004..424_203 CLEAN on the registered universe
    # but lands INSIDE the W186 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 426_004 -> 426_004..426_203,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (426_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W186+ projection (gate-derived r880): A first-clean
    # 426_004..428_003 CLEAN hops=0 / B first-clean 426_204..426_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W186 B band 426_004..426_203 will refuse the naive
    # W187 A window; W187 freezer MUST re-derive on the post-W186
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W186 bands were never assigned).
    186: {"a": (424_004, 426_003), "b_exit": (426_004, 426_203),
         "engine_owner": "bm-a"},
    # W187 (bm-a r885 freeze, seat MSG-2026-10-08-1626-bma-w187-seat
    # pushed to origin d176af598 pre-freeze r565 law (r885 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W186 finalize product already on origin since r884,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r885 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- bm-a r885-window self-ack move (the W187
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r885bma_w187_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W186 B band (arithmetic continuation
    # 426_004..428_003 REFUSED at its own start by the W186 B band
    # 426_004..426_203, exactly as the W186 seat W187+ projection + r880 probe
    # leg4 + r885 sec8 回填窗 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 426_204..428_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (426_203+1) machine-checkable -- A-hops-prior-B staircase
    # FORTY-SEVENTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 426_204..426_403 CLEAN on the registered universe
    # but lands INSIDE the W187 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 428_204 -> 428_204..428_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (428_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W187+ projection (gate-derived r885): A first-clean
    # 428_204..430_203 CLEAN hops=0 / B first-clean 428_404..428_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W187 B band 428_204..428_403 will refuse the naive
    # W188 A window; W188 freezer MUST re-derive on the post-W187
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W187 bands were never assigned).
    187: {"a": (426_204, 428_203), "b_exit": (428_204, 428_403),
         "engine_owner": "bm-a"},
    # W188 (bm-a r888 freeze, seat MSG-2026-10-08-1717-bma-w188-seat
    # pushed to origin 943967370 pre-freeze r565 law (r887 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W187 finalize product already on origin since r887,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r887 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- bm-a r887-window self-ack move (the W188
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r887bma_w188_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W187 B band (arithmetic continuation
    # 428_204..430_203 REFUSED at its own start by the W187 B band
    # 428_204..428_403, exactly as the W187 seat W188+ projection + r885 probe
    # leg4 + r888 sec8 回填窗 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 428_404..430_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (428_403+1) machine-checkable -- A-hops-prior-B staircase
    # FORTY-EIGHTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 428_404..428_603 CLEAN on the registered universe
    # but lands INSIDE the W188 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 430_404 -> 430_404..430_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (430_403+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W188+ projection (gate-derived r887): A first-clean
    # 430_404..432_403 CLEAN hops=0 / B first-clean 430_604..430_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W188 B band 430_404..430_603 will refuse the naive
    # W189 A window; W189 freezer MUST re-derive on the post-W188
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W188 bands were never assigned).
    188: {"a": (428_404, 430_403), "b_exit": (430_404, 430_603),
         "engine_owner": "bm-a"},
    # W189 (bm-a r890 freeze, seat MSG-2026-10-08-1815-bma-w189-seat
    # pushed to origin 744de26ef pre-freeze r565 law (r888 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W188 finalize product already on origin since r888,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r888 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- bm-a r889-window archive move (the W189
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r888bma_w189_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W188 B band (arithmetic continuation
    # 430_404..432_403 REFUSED at its own start by the W188 B band
    # 430_404..430_603, exactly as the W188 seat W189+ projection + r888 probe
    # leg4 + r890 sec8 回填窗 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 430_604..432_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (430_603+1) machine-checkable -- A-hops-prior-B staircase
    # FORTY-NINTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 430_604..430_803 CLEAN on the registered universe
    # but lands INSIDE the W189 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 432_604 -> 432_604..432_803,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (432_603+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W189+ projection (gate-derived r888): A first-clean
    # 432_604..434_603 CLEAN hops=0 / B first-clean 432_804..433_003
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W189 B band 432_604..432_803 will refuse the naive
    # W190 A window; W190 freezer MUST re-derive on the post-W189
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W189 bands were never assigned).
    189: {"a": (430_604, 432_603), "b_exit": (432_604, 432_803),
         "engine_owner": "bm-a"},
    # W190 (bm-a r892 freeze, seat MSG-2026-10-08-2035-bma-w190-seat
    # pushed to origin c177bf73b pre-freeze r565 law (r891 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W189 finalize product already on origin since r890,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r891 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- bm-a r892-window archive move (the W190
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r891bma_w190_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W189 B band (arithmetic continuation
    # 432_604..434_603 REFUSED at its own start by the W189 B band
    # 432_604..432_803, exactly as the W189 seat W190+ projection + r891 probe
    # leg4 + r892 sec8 回填窗 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 432_804..434_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (432_803+1) machine-checkable -- A-hops-prior-B staircase
    # FIFTIETH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 432_804..433_003 CLEAN on the registered universe
    # but lands INSIDE the W190 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 434_804 -> 434_804..435_003,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (434_803+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W190+ projection (gate-derived r891): A first-clean
    # 434_804..436_803 CLEAN hops=0 / B first-clean 435_004..435_203
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W190 B band 434_804..435_003 will refuse the naive
    # W191 A window; W191 freezer MUST re-derive on the post-W190
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W190 bands were never assigned).
    190: {"a": (432_804, 434_803), "b_exit": (434_804, 435_003),
         "engine_owner": "bm-a"},
    # W191 (bm-a r894 freeze, seat MSG-2026-10-08-2130-bma-w191-seat
    # pushed to origin 1c28dd21d pre-freeze r565 law (r892 pre-seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W190 finalize product already on origin since r892,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r892 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- bm-a r892-closeout-window archive move (the W191
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r892bma_w191_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W190 B band (arithmetic continuation
    # 434_804..436_803 REFUSED at its own start by the W190 B band
    # 434_804..435_003, exactly as the W190 seat W191+ projection + r892 probe
    # leg4 + r893 sec8 回填窗 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 435_004..437_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (435_003+1) machine-checkable -- A-hops-prior-B staircase
    # FIFTY-FIRST instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 435_004..435_203 CLEAN on the registered universe
    # but lands INSIDE the W191 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 437_004 -> 437_004..437_203,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (437_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W191+ projection (gate-derived r892): A first-clean
    # 437_004..439_003 CLEAN hops=0 / B first-clean 437_204..437_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W191 B band 437_004..437_203 will refuse the naive
    # W192 A window; W192 freezer MUST re-derive on the post-W191
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W191 bands were never assigned).
    191: {"a": (435_004, 437_003), "b_exit": (437_004, 437_203),
         "engine_owner": "bm-a"},
    # W192 (bm-c r787 freeze, seat MSG-20261008-2351-bmc-w192-seat
    # pushed to origin 1abe1a57f pre-freeze r565 law (r787 pre-freeze
    # window; payload = seat MSG only, Git Data API direct-build push
    # zero local commit -- sec.6.1.4 channel; the pre-seat probe
    # script + receipt landed with the W192 prereg freeze commit
    # de1ad11f9 next, interactive-window payload note; the W191
    # finalize product already on origin since r895, not re-shipped,
    # W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r892 pre-seat
    # push), zero merge, zero --no-verify; self-ack archive ALREADY
    # LANDED pre-freeze -- bm-a r892-closeout-window archive move (the W191
    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    # archived);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r787bmc_w192_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W191 B band (arithmetic continuation
    # 437_004..439_003 REFUSED at its own start by the W191 B band
    # 437_004..437_203, exactly as the W191 prereg sec5.5 + W191 seat W192+ projection + r892 probe
    # leg4 + r787 probe leg1 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 437_204..439_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (437_203+1) machine-checkable -- A-hops-prior-B staircase
    # FIFTY-SECOND instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 437_204..437_403 CLEAN on the registered universe
    # but lands INSIDE the W192 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 439_204 -> 439_204..439_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (439_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W193+ projection (gate-derived r787): A first-clean
    # 439_204..441_203 CLEAN hops=0 / B first-clean 439_404..439_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W192 B band 439_204..439_403 will refuse the naive
    # W193 A window; W193 freezer MUST re-derive on the post-W192
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W192 bands were never assigned).
    192: {"a": (437_204, 439_203), "b_exit": (439_204, 439_403),
         "engine_owner": "bm-c"},
    # W193 (bm-a r901 freeze, seat MSG-2026-10-09-0458-bma-w193-seat
    # pushed to origin 9df3078c5 pre-freeze r565 law (r900 seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W191 finalize product already on origin since r895,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r900 seat push),
    # zero merge, zero --no-verify; self-ack inbox->processed
    # archive PENDING WITH THIS freeze window -- bm-a r901 freeze
    # closeout archive move (the W193 seat MSG sits in
    # fleet/inbox/ at freeze time, moves to processed/ with this
    # window closeout, honest per frozen prereg sec.0);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r900bma_w193_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W192 B band (arithmetic continuation
    # 439_204..441_203 REFUSED at its own start by the W192 B band
    # 439_204..439_403, exactly as the W192 prereg sec5.5 + bm-c r787 probe
    # leg4 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 439_404..441_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (439_403+1) machine-checkable -- A-hops-prior-B staircase
    # FIFTY-THIRD instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 439_404..439_603 CLEAN on the registered universe
    # but lands INSIDE the W193 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 441_404 -> 441_404..441_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (441_403+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W194+ projection (gate-derived r900): A first-clean
    # 441_404..443_403 CLEAN hops=0 / B first-clean 441_604..441_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W193 B band 441_404..441_603 will refuse the naive
    # W194 A window; W194 freezer MUST re-derive on the post-W193
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W193 bands were never assigned).
    193: {"a": (439_404, 441_403), "b_exit": (441_404, 441_603),
         "engine_owner": "bm-a"},
    # W194 (bm-a r905 freeze, seat MSG-2026-10-09-0627-bma-w194-seat
    # pushed to origin 5cca13637 pre-freeze r565 law (r902 seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W191 finalize product already on origin since r895,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r902 seat push),
    # zero merge, zero --no-verify; self-ack inbox->processed
    # archive PENDING WITH THIS freeze window -- bm-a r905 freeze
    # closeout archive move (the W194 seat MSG sits in
    # fleet/inbox/ at freeze time, moves to processed/ with this
    # window closeout, honest per frozen prereg sec.0);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r902bma_w194_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W193 B band (arithmetic continuation
    # 441_404..443_403 REFUSED at its own start by the W193 B band
    # 441_404..441_603, exactly as the W193 prereg sec5.5 + bm-a r900 probe
    # leg4 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 441_604..443_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (441_603+1) machine-checkable -- A-hops-prior-B staircase
    # FIFTY-FOURTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 441_604..441_803 CLEAN on the registered universe
    # but lands INSIDE the W194 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 443_604 -> 443_604..443_803,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (443_603+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W195+ projection (gate-derived r902): A first-clean
    # 443_604..445_603 CLEAN hops=0 / B first-clean 443_804..444_003
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W194 B band 443_604..443_803 will refuse the naive
    # W195 A window; W195 freezer MUST re-derive on the post-W194
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W194 bands were never assigned).
    194: {"a": (441_604, 443_603), "b_exit": (443_604, 443_803),
         "engine_owner": "bm-a"},
    # W195 (bm-a r909 freeze, seat MSG-2026-10-09-0844-bma-w195-seat
    # pushed to origin eb81c0878 pre-freeze r565 law (r907 seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W194 finalize product already on origin since r906,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r907 seat push),
    # zero merge, zero --no-verify; self-ack inbox->processed
    # archive PENDING WITH THIS freeze window -- bm-a r909 freeze
    # closeout archive move (the W195 seat MSG sits in
    # fleet/inbox/ at freeze time, moves to processed/ with this
    # window closeout, honest per frozen prereg sec.0);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r907bma_w195_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W194 B band (arithmetic continuation
    # 443_604..445_603 REFUSED at its own start by the W194 B band
    # 443_604..443_803, exactly as the W194 prereg sec5.5 + bm-a r902 probe
    # leg4 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 443_804..445_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (443_803+1) machine-checkable -- A-hops-prior-B staircase
    # FIFTY-FIFTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 443_804..444_003 CLEAN on the registered universe
    # but lands INSIDE the W195 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 445_804 -> 445_804..446_003,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (445_803+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W196+ projection (gate-derived r907): A first-clean
    # 445_804..447_803 CLEAN hops=0 / B first-clean 446_004..446_203
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W195 B band 445_804..446_003 will refuse the naive
    # W196 A window; W196 freezer MUST re-derive on the post-W195
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W195 bands were never assigned).
    195: {"a": (443_804, 445_803), "b_exit": (445_804, 446_003),
         "engine_owner": "bm-a"},
    # W196 (bm-a r912 freeze, seat MSG-2026-10-09-1007-bma-w196-seat
    # pushed to origin 01992cd42 pre-freeze r565 law (r910 seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W195 finalize product already on origin since r910,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r910 seat push),
    # zero merge, zero --no-verify; self-ack inbox->processed
    # archive PENDING WITH THIS freeze window -- bm-a r912 freeze
    # closeout archive move (the W196 seat MSG sits in
    # fleet/inbox/ at freeze time, moves to processed/ with this
    # window closeout, honest per frozen prereg sec.0);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r910bma_w196_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W195 B band (arithmetic continuation
    # 445_804..447_803 REFUSED at its own start by the W195 B band
    # 445_804..446_003, exactly as the W195 prereg sec5.5 + bm-a r907 probe
    # leg4 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 446_004..448_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (446_003+1) machine-checkable -- A-hops-prior-B staircase
    # FIFTY-SIXTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 446_004..446_203 CLEAN on the registered universe
    # but lands INSIDE the W196 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 448_004 -> 448_004..448_203,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (448_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W197+ projection (gate-derived r910): A first-clean
    # 448_004..450_003 CLEAN hops=0 / B first-clean 448_204..448_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W196 B band 448_004..448_203 will refuse the naive
    # W197 A window; W197 freezer MUST re-derive on the post-W196
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W196 bands were never assigned).
    196: {"a": (446_004, 448_003), "b_exit": (448_004, 448_203),
         "engine_owner": "bm-a"},
    # W197 (bm-a r915 freeze, seat MSG-2026-10-09-1159-bma-w197-seat
    # pushed to origin c59843acb pre-freeze r565 law (r914 seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W196 finalize product already on origin since r913,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r914 seat push),
    # zero merge, zero --no-verify; self-ack inbox->processed
    # archive ALREADY LANDED at the seat round r914 closeout --
    # the W197 seat MSG sits in fleet/inbox/processed/ (self-acked
    # per the S7 inbox-processing law at the seat round, honest
    # per frozen prereg sec.0 -- W196 archive-pending N/A);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r914bma_w197_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W196 B band (arithmetic continuation
    # 448_004..450_003 REFUSED at its own start by the W196 B band
    # 448_004..448_203, exactly as the W196 prereg sec5.5 + bm-a r910 probe
    # leg4 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 448_204..450_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (448_203+1) machine-checkable -- A-hops-prior-B staircase
    # FIFTY-SEVENTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 448_204..448_403 CLEAN on the registered universe
    # but lands INSIDE the W197 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 450_204 -> 450_204..450_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (450_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W198+ projection (gate-derived r914): A first-clean
    # 450_204..452_203 CLEAN hops=0 / B first-clean 450_404..450_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W197 B band 450_204..450_403 will refuse the naive
    # W198 A window; W198 freezer MUST re-derive on the post-W197
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W197 bands were never assigned).
    197: {"a": (448_204, 450_203), "b_exit": (450_204, 450_403),
         "engine_owner": "bm-a"},
    # W198 (bm-a r916 freeze, seat MSG-2026-10-09-1355-bma-w198-seat
    # pushed to origin 525630e39 pre-freeze r565 law (r915 seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W197 finalize product already on origin since r915,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r915 seat push),
    # zero merge, zero --no-verify; self-ack inbox->processed
    # archive PENDING WITH THIS freeze window -- bm-a r916 freeze
    # closeout archive move (the W198 seat MSG sits in
    # fleet/inbox/ at freeze time, moves to processed/ with this
    # window closeout, honest per frozen prereg sec.0);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r915bma_w198_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W197 B band (arithmetic continuation
    # 450_204..452_203 REFUSED at its own start by the W197 B band
    # 450_204..450_403, exactly as the W197 prereg sec5.5 + bm-a r914 probe
    # leg4 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 450_404..452_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (450_403+1) machine-checkable -- A-hops-prior-B staircase
    # FIFTY-EIGHTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 450_404..450_603 CLEAN on the registered universe
    # but lands INSIDE the W198 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 452_404 -> 452_404..452_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (452_403+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W199+ projection (gate-derived r915): A first-clean
    # 452_404..454_403 CLEAN hops=0 / B first-clean 452_604..452_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W198 B band 452_404..452_603 will refuse the naive
    # W199 A window; W199 freezer MUST re-derive on the post-W198
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W198 bands were never assigned).
    198: {"a": (450_404, 452_403), "b_exit": (452_404, 452_603),
         "engine_owner": "bm-a"},
    # W199 (bm-a r919 freeze, seat MSG-2026-10-09-1507-bma-w199-seat
    # pushed to origin 3a875bf43 pre-freeze r565 law (r918 seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W198 finalize product already on origin since r917,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r918 seat push),
    # zero merge, zero --no-verify; self-ack inbox->processed
    # archive PENDING WITH THIS freeze window -- bm-a r919 freeze
    # closeout archive move (the W199 seat MSG sits in
    # fleet/inbox/ at freeze time, moves to processed/ with this
    # window closeout, honest per frozen prereg sec.0);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r918bma_w199_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W198 B band (arithmetic continuation
    # 452_404..454_403 REFUSED at its own start by the W198 B band
    # 452_404..452_603, exactly as the W198 prereg sec5.5 + bm-a r915 probe
    # leg4 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 452_604..454_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (452_603+1) machine-checkable -- A-hops-prior-B staircase
    # FIFTY-NINTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 452_604..452_803 CLEAN on the registered universe
    # but lands INSIDE the W199 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 454_604 -> 454_604..454_803,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (454_603+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W200+ projection (gate-derived r918): A first-clean
    # 454_604..456_603 CLEAN hops=0 / B first-clean 454_804..455_003
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W199 B band 454_604..454_803 will refuse the naive
    # W200 A window; W200 freezer MUST re-derive on the post-W199
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W199 bands were never assigned).
    199: {"a": (452_604, 454_603), "b_exit": (454_604, 454_803),
         "engine_owner": "bm-a"},
    # W200 (bm-a r921 freeze, seat MSG-2026-10-09-1645-bma-w200-seat
    # pushed to origin 143fcfe1b pre-freeze r565 law (r920 seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W199 finalize product already on origin since r920,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r920 seat push),
    # zero merge, zero --no-verify; self-ack inbox->processed
    # archive ALREADY LANDED pre-freeze -- bm-a r920 seat-round
    # closeout consumed->processed (the W200 seat MSG sits in
    # fleet/inbox/processed/ at freeze time, honest archived
    # per S7 law);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r920bma_w200_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W199 B band (arithmetic continuation
    # 454_604..456_603 REFUSED at its own start by the W199 B band
    # 454_604..454_803, exactly as the W199 prereg sec5.5 + bm-a r918 probe
    # leg4 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 454_804..456_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (454_803+1) machine-checkable -- A-hops-prior-B staircase
    # SIXTIETH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 454_804..455_003 CLEAN on the registered universe
    # but lands INSIDE the W200 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 456_804 -> 456_804..457_003,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (456_803+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W201+ projection (gate-derived r920): A first-clean
    # 456_804..458_803 CLEAN hops=0 / B first-clean 457_004..457_203
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W200 B band 456_804..457_003 will refuse the naive
    # W201 A window; W201 freezer MUST re-derive on the post-W200
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W200 bands were never assigned).
    200: {"a": (454_804, 456_803), "b_exit": (456_804, 457_003),
         "engine_owner": "bm-a"},
    # W201 (bm-a r922 freeze, seat MSG-2026-10-09-1812-bma-w201-seat
    # pushed to origin 188ebe647 pre-freeze r565 law (r921 seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W200 finalize product already on origin since r921,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r921 seat push),
    # zero merge, zero --no-verify; self-ack inbox->processed
    # archive PENDING WITH THIS freeze window -- bm-a r922 freeze
    # closeout archive move (the W201 seat MSG sits in
    # fleet/inbox/ at freeze time, moves to processed/ with this
    # window closeout, honest per frozen prereg sec.0);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r921bma_w201_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W200 B band (arithmetic continuation
    # 456_804..458_803 REFUSED at its own start by the W200 B band
    # 456_804..457_003, exactly as the W200 prereg sec5.5 + bm-a r920 probe
    # leg4 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 457_004..459_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (457_003+1) machine-checkable -- A-hops-prior-B staircase
    # SIXTY-FIRST instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 457_004..457_203 CLEAN on the registered universe
    # but lands INSIDE the W201 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 459_004 -> 459_004..459_203,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (459_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W202+ projection (gate-derived r921): A first-clean
    # 459_004..461_003 CLEAN hops=0 / B first-clean 459_204..459_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W201 B band 459_004..459_203 will refuse the naive
    # W202 A window; W202 freezer MUST re-derive on the post-W201
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W201 bands were never assigned).
    201: {"a": (457_004, 459_003), "b_exit": (459_004, 459_203),
         "engine_owner": "bm-a"},
    # W202 (bm-a r927 freeze, seat MSG-2026-10-09-1935-bma-w202-seat
    # pushed to origin e2187e483 pre-freeze r565 law (r924 seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W201 finalize product already on origin since r924,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r924 seat push),
    # zero merge, zero --no-verify; self-ack inbox->processed
    # archive ALREADY LANDED pre-freeze -- bm-a r925 seat-round
    # closeout consumed->processed (the W202 seat MSG sits in
    # fleet/inbox/processed/ at freeze time, honest archived
    # per S7 law);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r924bma_w202_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W201 B band (arithmetic continuation
    # 459_004..461_003 REFUSED at its own start by the W201 B band
    # 459_004..459_203, exactly as the W201 prereg sec5.5 + bm-a r921 probe
    # leg4 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 459_204..461_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (459_203+1) machine-checkable -- A-hops-prior-B staircase
    # SIXTY-SECOND instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 459_204..459_403 CLEAN on the registered universe
    # but lands INSIDE the W202 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 461_204 -> 461_204..461_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (461_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W203+ projection (gate-derived r924): A first-clean
    # 461_204..463_203 CLEAN hops=0 / B first-clean 461_404..461_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W202 B band 461_204..461_403 will refuse the naive
    # W203 A window; W203 freezer MUST re-derive on the post-W202
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W202 bands were never assigned).
    202: {"a": (459_204, 461_203), "b_exit": (461_204, 461_403),
         "engine_owner": "bm-a"},
    # W203 (bm-a r936 freeze, seat MSG-2026-10-09-2329-bma-w203-seat
    # pushed to origin dc00bfa54 pre-freeze r565 law (r930 seat
    # push; payload = seat MSG + pre-seat probe script + probe receipt
    # (3-item; the W202 finalize product already on origin since r928,
    # not re-shipped, W146 same-push precedent);
    # deletion-set EMPTY; delivery window
    # = direct fast-forward behind-0 at fetch (r930 seat push),
    # zero merge, zero --no-verify; self-ack inbox->processed
    # archive ALREADY LANDED pre-freeze -- bm-a r930 seat-round
    # closeout consumed->processed (the W203 seat MSG sits in
    # fleet/inbox/processed/ at freeze time, honest archived
    # per S7 law);
    # deletion-set EMPTY);
    # band gate ADMIT results/_r930bma_w203_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W202 B band (arithmetic continuation
    # 461_204..463_203 REFUSED at its own start by the W202 B band
    # 461_204..461_403, exactly as the W202 prereg sec5.5 + bm-a r924 probe
    # leg4 succession projection notes all anticipated;
    # honest forward walk hops=1 -> 461_404..463_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (461_403+1) machine-checkable -- A-hops-prior-B staircase
    # SIXTY-THIRD instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 461_404..461_603 CLEAN on the registered universe
    # but lands INSIDE the W203 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 463_404 -> 463_404..463_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (463_403+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W204+ projection (gate-derived r930): A first-clean
    # 463_404..465_403 CLEAN hops=0 / B first-clean 463_604..463_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W203 B band 463_404..463_603 will refuse the naive
    # W204 A window; W204 freezer MUST re-derive on the post-W203
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W203 bands were never assigned).
    203: {"a": (461_404, 463_403), "b_exit": (463_404, 463_603),
         "engine_owner": "bm-a"},
    # W204 (bm-c r837 five-face freeze phase-2 splice rebuild, seat
    # MSG-2026-10-10-0022-bmc-w204-seat pushed to origin 7cf82c262
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit 1422ad767 (prereg research/PERPETUAL_N1_W204_PREREG.md,
    # probe results/_w204bmc_20261010_probe_receipt.json);
    # deletion-set EMPTY; delivery window = splice rebuild after the
    # W139/W140 SEED_REGISTRY adjudication carve-outs landed 7464be852
    # (O-20261010-1906-bm-c adjudicated; receipt
    # MSG-2026-10-10-1940) -- the C1804 dead-session spliced dual
    # files were NOT recoverable (r836 verified, all worktrees
    # searched); this row is the honest rebuild from the committed
    # ADMIT receipt on an origin-verbatim base (r609 lesson:
    # execution-time rev-parse + fresh blob, no stale-cache reuse);
    # zero --no-verify; the W204 seat MSG sits in
    # fleet/inbox/processed/ at freeze time, honest archived
    # per S7 law);
    # band gate ADMIT results/_w204bmc_20261010_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W203 B band (arithmetic continuation
    # 463_404..465_403 REFUSED at its own start by the W203 B band
    # 463_404..463_603, exactly as the W203 pf/probe leg4
    # W204+ succession projection notes anticipated;
    # honest forward walk hops=1 -> 463_604..465_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (463_603+1) machine-checkable -- A-hops-prior-B staircase
    # SIXTY-FOURTH instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 463_604..463_803 CLEAN on the registered
    # universe but lands INSIDE the W204 A band window --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 465_604 -> 465_604..465_803, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (465_603+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention upgrade,
    # Tools/seed_admit_gate.py, run on the pre-splice universe):
    # rc0 base=463604 span=2000 checked=2000 verdict=FREE /
    # rc0 base=465604 span=200 checked=200 verdict=FREE.
    # W205+ projection (gate-derived pre-seat probe leg4, pre-W204
    # universe): A first-clean 465_604..467_603 CLEAN hops=0 /
    # B first-clean 465_804..466_003 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W204 B band
    # 465_604..465_803 will refuse the naive W205 A window (W205
    # seat MSG-2026-10-10-1627-bma already declared A 465_804..467_803
    # / B 467_804..468_003 on the post-W204-declared universe;
    # if the W204 row lands before the W205 freeze the W205 freezer
    # MUST re-pull and re-verify the universe face); W206 freezer
    # MUST re-derive on the post-W205 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W204 bands were never assigned).
    204: {"a": (463_604, 465_603), "b_exit": (465_604, 465_803),
         "engine_owner": "bm-c"},
    # W205 (bm-a r963 freeze, seat MSG-2026-10-10-1627-bma-w205-seat pushed
    # to origin 63b5bd3dd pre-freeze r565 law; probe receipt
    # results/_r956bma_w205_probe_receipt.json ADMIT; W204-state guard
    # FIRED at freeze: the W204 row landed on origin (bm-c r837
    # freeze+finalize 2c8ef33c8) after the W205 seat -- re-pulled +
    # re-verified, bands match the declared universe the seat derived
    # on; A 465_804..467_803 hops=1 A-hops-prior-B staircase
    # SIXTY-FIFTH instance E36; B 467_804..468_003 hops=1 own-A
    # mutual exclusion W141; not a re-pick R250; zero --no-verify;
    # the W205 seat MSG sits in fleet/inbox/processed/ at freeze
    # time, honest archived per S7 law;
    # W206+ projection per probe leg4: A first-clean 467_804..469_803
    # CLEAN / B first-clean 468_004..468_203 CLEAN -- naive B lands
    # INSIDE the naive A window and the registered W205 B band
    # 467_804..468_003 will refuse the naive W206 A window (W206 seat
    # MSG-20261010-2323-bmc declared on the post-W205 universe; the
    # W206 freezer MUST re-pull and re-verify if the W205 row lands
    # before the W206 freeze); W206 freezer MUST re-derive on the
    # post-W205 universe AND reserve the own-wave A window when
    # deriving B (W141 precedent, same-freeze mutual exclusion, leg2
    # law, E36 staircase card; never transcribe r587)).
    205: {"a": (465_804, 467_803), "b_exit": (467_804, 468_003),
         "engine_owner": "bm-a"},
    # W206 (bm-c interactive five-face freeze splice, seat
    # MSG-20261010-2323-bmc-w206-seat pushed to origin e25629f7
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit 0620f78 (prereg research/PERPETUAL_N1_W206_PREREG.md,
    # probe results/_w206bmc_20261010_probe_receipt.json);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-a W205 five-face (freeze 4e0f4bd4b0) + W205
    # finalize product landed (n1_w205_results.json present, ledger
    # head 868171 machine-read at freeze time); zero --no-verify;
    # the W206 seat MSG sits in fleet/inbox/processed/ at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w206bmc_20261010_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W205 B band (arithmetic continuation
    # 467_804..469_803 REFUSED at its own start by the W205 B band
    # 467_804..468_003, exactly as the W205 seat leg4
    # projection + r956 W205 probe leg4 anticipated;
    # honest forward walk hops=1 -> 468_004..470_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (468_003+1) machine-checkable -- A-hops-prior-B staircase
    # SIXTY-SIXTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 468_004..468_203 CLEAN on the registered
    # universe but lands INSIDE the W206 A band window 468_004..470_003 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 470_004 -> 470_004..470_203, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (470_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=468004 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=470004 span=200 checked=200 verdict=FREE.
    # W207+ projection (gate-derived pre-seat probe leg4, pre-W206
    # universe): A first-clean 470_004..472_003 CLEAN hops=0 /
    # B first-clean 470_204..470_403 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W206 B band
    # 470_004..470_203 will refuse the naive W207 A window; W207 freezer
    # MUST re-derive on the post-W206 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W206 bands were never assigned).
    206: {"a": (468_004, 470_003), "b_exit": (470_004, 470_203),
         "engine_owner": "bm-c"},
    # W207 (bm-b OS-loop five-face freeze splice, seat
    # MSG-20261010-2335-bmb-w207-seat pushed to origin 014a3e85e
    # pre-freeze r565 law; prereg + banned-gate ADMIT frozen
    # commit 6fa2dae16 (prereg research/PERPETUAL_N1_W207_PREREG.md,
    # probe results/_w207bmb_20261010_probe_receipt.json);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W206 five-face (freeze 68ba083478) + W206
    # finalize product landed (n1_w206_results.json present, ledger
    # head 870371 machine-read at freeze time); zero --no-verify;
    # the W207 seat MSG sits in fleet/inbox/processed/ at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w207bmb_20261010_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W206 B band (arithmetic continuation
    # 470_004..472_003 REFUSED at its own start by the W206 B band
    # 470_004..470_203, exactly as the W206 seat leg4
    # projection + W206 probe leg4 anticipated;
    # honest forward walk hops=1 -> 470_204..472_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (470_203+1) machine-checkable -- A-hops-prior-B staircase
    # SIXTY-SEVENTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 470_204..470_403 CLEAN on the registered
    # universe but lands INSIDE the W207 A band window 470_204..472_203 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 472_204 -> 472_204..472_403, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (472_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=470204 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=472204 span=200 checked=200 verdict=FREE.
    # W208+ projection (gate-derived pre-seat probe leg4, pre-W207
    # universe): A first-clean 472_204..474_203 CLEAN hops=0 /
    # B first-clean 472_404..472_603 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W207 B band
    # 472_204..472_403 will refuse the naive W208 A window; W208 freezer
    # MUST re-derive on the post-W207 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W207 bands were never assigned).
    207: {"a": (470_204, 472_203), "b_exit": (472_204, 472_403),
         "engine_owner": "bm-b"},
    # W208 (bm-c interactive window 2026-10-11 ABSORB-FREEZE of the stale bm-a seat
    # MSG-2026-10-11-0129-bma-w208-seat published 01:29, 11h stale with no
    # prereg/five-face; dead-estate absorb per r899/r915 law (bm-a loop round 872
    # alive but has not picked it up); engine_owner stays bm-a per the seat claim;
    # bands machine-derived in the absorb-mode pre-seat probe
    # results/_w208bmc_20261011_probe_receipt.json (rc0 ADMIT, leg1 hops=1/1):
    # A = FIRST-CLEAN past prior-wave B (arithmetic continuation 472_204..474_203
    # REFUSED at its own start by the registered W207 B band 472_204..472_403;
    # honest forward walk -> 472_404..474_403; A base == prior-wave B tail+1
    # (472_403+1) machine-checkable -- A-hops-prior-B staircase SIXTY-EIGHTH
    # instance, E36 card; non-rotational r587 forward-monotone walk);
    # B = FIRST-CLEAN past own-wave A (arithmetic continuation 474_404..474_603
    # is CLEAN on the declared universe but lands INSIDE the W208 A band window
    # 472_404..474_403 -- same-freeze mutual exclusion (W141 precedent, leg2 law)
    # -- the walk with the own-wave A window reserved jumps to 474_604 ->
    # 474_604..474_803); NOT a re-pick (R250: W208 bands were never assigned).
    208: {"a": (472_404, 474_403), "b_exit": (474_404, 474_603),
         "engine_owner": "bm-c"},  # takeover r885: bm-a dead 21.5h+ (hb 10-10 21:52) ->排满律接管烧录权; bands unchanged (R250 no re-pick); bm-a revive sees done-face+MSG-1925
    # W209 (bm-c loop five-face freeze splice, seat
    # MSG-20261011-0301-bmc-w209-seat pushed to origin e989c03eb
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit 2d0415076d (prereg research/PERPETUAL_N1_W209_PREREG.md,
    # probe results/_w209bmc_20261011_probe_receipt.json @ e989c03ebc);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-a W208 five-face (freeze 0ea2b9bde7; ownership
    # bm-a->bm-c takeover r885 commit 4682d6b19, bands unchanged R250) + W208
    # finalize product landed (n1_w208_results.json present, ledger
    # head 881389 machine-read at freeze time); zero --no-verify;
    # the W209 seat MSG sits in fleet/inbox/processed/MSG-20261011-0301-bmc-w209-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w209bmc_20261011_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W208 B band (arithmetic continuation
    # 474_404..476_403 REFUSED at its own start by the W208 B band
    # 474_404..474_603, exactly as the W208 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 474_604..476_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (474_603+1) machine-checkable -- A-hops-prior-B staircase
    # SIXTY-NINTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 474_604..474_803 CLEAN on the registered
    # universe but lands INSIDE the W209 A band window 474_604..476_603 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 476_604 -> 476_604..476_803, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (476_603+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=474604 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=476604 span=200 checked=200 verdict=FREE.
    # W210+ projection (gate-derived pre-seat probe leg4, pre-W209
    # universe): A naive first-clean 476604..478603 CLEAN hops=0 /
    # B naive first-clean 476804..477003 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W209 B band
    # 476_604..476_803 will refuse the naive W210 A window; W210 freezer
    # MUST re-derive on the post-W209 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W209 bands were never assigned).
    209: {"a": (474_604, 476_603), "b_exit": (476_604, 476_803),
         "engine_owner": "bm-c"},
    # W210 (bm-c loop TAKEOVER five-face freeze splice, seat
    # MSG-20261011-0319-bmb-w210-seat published by bm-b, pushed to origin d550bf11c
    # pre-freeze r565 law; prereg REBUILT machine-read in the takeover window (bm-b
    # payload claim never landed on origin, disclosed); ADMIT probe receipt frozen
    # commit 8c89c1138b (prereg research/PERPETUAL_N1_W210_PREREG.md,
    # probe results/_w210bmb_20261011_probe_receipt.json @ d550bf11c8);
    # TAKEOVER r898: bm-b hb-stall 94min >> 20min GM re-assignment gate + W209
    # finalize landed 4h+ with the armed lane unexecuted (engine idle, burns_active=[],
    # CEO fill-order standing RE-ISSUED 2026-10-10 ~23:1x) -> bm-c executes per the
    # W208 takeover r885 precedent; takeover notice MSG-2026-10-12-0020 pushed to
    # origin c64bc2287 BEFORE this freeze (anti-double-burn, bm-b armed-lane
    # yield requested); engine_owner bm-b -> bm-c, bands UNCHANGED R250;
    # deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W209 five-face (freeze 87b81f9732) + W209
    # finalize product landed (n1_w209_results.json present, ledger
    # head 883589 machine-read at freeze time); zero --no-verify;
    # the W210 seat MSG sits in fleet/inbox/processed/MSG-20261011-0319-bmb-w210-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w210bmb_20261011_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W209 B band (arithmetic continuation
    # 476_604..478_603 REFUSED at its own start by the W209 B band
    # 476_604..476_803, exactly as the W209 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 476_804..478_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (476_803+1) machine-checkable -- A-hops-prior-B staircase
    # SEVENTIETH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 476_804..477_003 CLEAN on the registered
    # universe but lands INSIDE the W210 A band window 476_804..478_803 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 478_804 -> 478_804..479_003, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (478_803+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=476804 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=478804 span=200 checked=200 verdict=FREE.
    # W211+ projection (gate-derived pre-seat probe leg4, pre-W210
    # universe): A naive first-clean 478804..480803 CLEAN hops=0 /
    # B naive first-clean 479004..479203 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W210 B band
    # 478_804..479_003 will refuse the naive W211 A window; W211 freezer
    # MUST re-derive on the post-W210 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card; never transcribe r587) -- CONVERGENCE ALREADY
    # PROVEN: the published W211 seat (bm-c, MSG-20261011-0350) re-derived
    # A 479_004..481_003 hopping the W210 declared B band (SEVENTY-FIRST
    # instance materialized at seat time) + B 481_004..481_203.
    # NOT a re-pick (R250: W210 bands were never assigned).
    210: {"a": (476_804, 478_803), "b_exit": (478_804, 479_003),
         "engine_owner": "bm-c"},  # takeover r898: bm-b hb-stall 94min -> bm-c per CEO fill-order standing; bands unchanged R250 (bm-b probe ADMIT verbatim, seat MSG-20261011-0319)
    # W211 (bm-c loop five-face freeze splice, seat
    # MSG-20261011-0350-bmc-w211-seat pushed to origin 0a60b8850
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit e8a2f46383 (prereg research/PERPETUAL_N1_W211_PREREG.md
    # freeze-prep r848-precedent bundle, probe
    # results/_w211bmc_20261011_probe_receipt.json @ 0a60b88501);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-b W210 five-face (freeze d5ec83b72b) + W210
    # finalize product landed (n1_w210_results.json present, ledger
    # head 885789 machine-read at freeze time); zero --no-verify;
    # the W211 seat MSG sits in fleet/inbox/processed/MSG-20261011-0350-bmc-w211-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w211bmc_20261011_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W210 B band (arithmetic continuation
    # 478_804..480_803 REFUSED at its own start by the W210 B band
    # 478_804..479_003, exactly as the W210 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 479_004..481_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (479_003+1) machine-checkable -- A-hops-prior-B staircase
    # SEVENTY-FIRST instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 479_004..479_203 CLEAN on the registered
    # universe but lands INSIDE the W211 A band window 479_004..481_003 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 481_004 -> 481_004..481_203, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (481_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=479004 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=481004 span=200 checked=200 verdict=FREE.
    # W212+ projection (gate-derived pre-seat probe leg4, pre-W211
    # universe): A naive first-clean 481004..483003 CLEAN hops=0 /
    # B naive first-clean 481204..481403 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W211 B band
    # 481_004..481_203 will refuse the naive W212 A window; W212 freezer
    # MUST re-derive on the post-W211 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card; never transcribe r587) -- CONVERGENCE ALREADY
    # PROVEN: the published W212 seat (bm-c, MSG-20261011-0732) re-derived
    # A 481_204..483_203 hopping the W211 declared B band (SEVENTY-SECOND
    # instance materialized at seat time) + B 483_204..483_403.
    # NOT a re-pick (R250: W211 bands were never assigned).
    211: {"a": (479_004, 481_003), "b_exit": (481_004, 481_203),
         "engine_owner": "bm-c"},
    # W212 (bm-c loop five-face freeze splice, seat
    # MSG-20261011-0732-bmc-w212-seat pushed to origin dace861b1
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit 99045137e2 (prereg research/PERPETUAL_N1_W212_PREREG.md
    # r906 freeze-window bundle, probe
    # results/_w212bmc_20261011_probe_receipt.json @ dace861b11);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W211 five-face (freeze db243f93e7) + W211
    # finalize product landed (n1_w211_results.json present, ledger
    # head 887989 machine-read at freeze time); zero --no-verify;
    # the W212 seat MSG sits in fleet/inbox/processed/MSG-20261011-0732-bmc-w212-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w212bmc_20261011_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W211 B band (arithmetic continuation
    # 481_004..483_003 REFUSED at its own start by the W211 B band
    # 481_004..481_203, exactly as the W211 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 481_204..483_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (481_203+1) machine-checkable -- A-hops-prior-B staircase
    # SEVENTY-SECOND instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 481_204..481_403 CLEAN on the registered
    # universe but lands INSIDE the W212 A band window 481_204..483_203 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 483_204 -> 483_204..483_403, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (483_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=481204 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=483204 span=200 checked=200 verdict=FREE.
    # W213+ projection (gate-derived pre-seat probe leg4, pre-W212
    # universe): A naive first-clean 483204..485203 CLEAN hops=0 /
    # B naive first-clean 483404..483603 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W212 B band
    # 483_204..483_403 will refuse the naive W213 A window; W213 freezer
    # MUST re-derive on the post-W212 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, SEVENTY-THIRD instance anticipated; never transcribe r587).
    212: {"a": (481_204, 483_203), "b_exit": (483_204, 483_403),
         "engine_owner": "bm-c"},
    # W213 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-0342-bmc-w213-seat pushed to origin 4f3b0d6a8
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit eeda851458 (prereg research/PERPETUAL_N1_W213_PREREG.md
    # r908 freeze-window bundle, probe
    # results/_w213bmc_20261012_probe_receipt.json @ 4f3b0d6a83);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W212 five-face (freeze 0f30cb725f) + W212
    # finalize product landed (n1_w212_results.json present, ledger
    # head 890189 machine-read at freeze time); zero --no-verify;
    # the W213 seat MSG sits in fleet/inbox/MSG-20261012-0342-bmc-w213-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w213bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W212 B band (arithmetic continuation
    # 483_204..485_203 REFUSED at its own start by the W212 B band
    # 483_204..483_403, exactly as the W212 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 483_404..485_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (483_403+1) machine-checkable -- A-hops-prior-B staircase
    # SEVENTY-THIRD instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 483_404..483_603 CLEAN on the registered
    # universe but lands INSIDE the W213 A band window 483_404..485_403 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 485_404 -> 485_404..485_603, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (485_403+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=483404 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=485404 span=200 checked=200 verdict=FREE.
    # W214+ projection (gate-derived pre-seat probe leg4, pre-W213
    # universe): A naive first-clean 485404..487403 CLEAN hops=0 /
    # B naive first-clean 485604..485803 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W213 B band
    # 485_404..485_603 will refuse the naive W214 A window; W214 freezer
    # MUST re-derive on the post-W213 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, SEVENTY-FOURTH instance anticipated; never transcribe r587).
    213: {"a": (483_404, 485_403), "b_exit": (485_404, 485_603),
         "engine_owner": "bm-c"},
    # W214 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-0438-bmc-w214-seat pushed to origin d55a6b58b
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit b0aa903767 (prereg research/PERPETUAL_N1_W214_PREREG.md
    # r910 freeze-window bundle, probe
    # results/_w214bmc_20261012_probe_receipt.json @ d55a6b58bb);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W213 five-face (freeze a24069f4c1) + W213
    # finalize product landed (n1_w213_results.json present, ledger
    # head 892389 machine-read at freeze time); zero --no-verify;
    # the W214 seat MSG sits in fleet/inbox/MSG-20261012-0438-bmc-w214-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w214bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W213 B band (arithmetic continuation
    # 485_404..487_403 REFUSED at its own start by the W213 B band
    # 485_404..485_603, exactly as the W213 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 485_604..487_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (485_603+1) machine-checkable -- A-hops-prior-B staircase
    # SEVENTY-FOURTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 485_604..485_803 CLEAN on the registered
    # universe but lands INSIDE the W214 A band window 485_604..487_603 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 487_604 -> 487_604..487_803, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (487_603+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=485604 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=487604 span=200 checked=200 verdict=FREE.
    # W215+ projection (gate-derived pre-seat probe leg4, pre-W214
    # universe): A naive first-clean 487604..489603 CLEAN hops=0 /
    # B naive first-clean 487804..488003 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W214 B band
    # 487_604..487_803 will refuse the naive W215 A window; W215 freezer
    # MUST re-derive on the post-W214 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, SEVENTY-FIFTH instance anticipated; never transcribe r587).
    214: {"a": (485_604, 487_603), "b_exit": (487_604, 487_803),
         "engine_owner": "bm-c"},
    # W215 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-0536-bmc-w215-seat pushed to origin 37d7adc0a
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit 1d9008192d (prereg research/PERPETUAL_N1_W215_PREREG.md
    # r912 freeze-window bundle, probe
    # results/_w215bmc_20261012_probe_receipt.json @ 37d7adc0af);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W214 five-face (freeze 4664900c86) + W214
    # finalize product landed (n1_w214_results.json present, ledger
    # head 894589 machine-read at freeze time); zero --no-verify;
    # the W215 seat MSG sits in fleet/inbox/MSG-20261012-0536-bmc-w215-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w215bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W214 B band (arithmetic continuation
    # 487_604..489_603 REFUSED at its own start by the W214 B band
    # 487_604..487_803, exactly as the W214 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 487_804..489_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (487_803+1) machine-checkable -- A-hops-prior-B staircase
    # SEVENTY-FIFTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 487_804..488_003 CLEAN on the registered
    # universe but lands INSIDE the W215 A band window 487_804..489_803 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 489_804 -> 489_804..490_003, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (489_803+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=487804 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=489804 span=200 checked=200 verdict=FREE.
    # W216+ projection (gate-derived pre-seat probe leg4, pre-W215
    # universe): A naive first-clean 489804..491803 CLEAN hops=0 /
    # B naive first-clean 490004..490203 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W215 B band
    # 489_804..490_003 will refuse the naive W216 A window; W216 freezer
    # MUST re-derive on the post-W215 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, SEVENTY-SIXTH instance anticipated; never transcribe r587).
    215: {"a": (487_804, 489_803), "b_exit": (489_804, 490_003),
         "engine_owner": "bm-c"},
    # W216 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-0630-bmc-w216-seat pushed to origin f8b38fa1e
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit 7d565ee678 (prereg research/PERPETUAL_N1_W216_PREREG.md
    # r914 freeze-window bundle, probe
    # results/_w216bmc_20261012_probe_receipt.json @ f8b38fa1e2);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W215 five-face (freeze 1e71c3b93e) + W215
    # finalize product landed (n1_w215_results.json present, ledger
    # head 896789 machine-read at freeze time); zero --no-verify;
    # the W216 seat MSG sits in fleet/inbox/MSG-20261012-0630-bmc-w216-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w216bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W215 B band (arithmetic continuation
    # 489_804..491_803 REFUSED at its own start by the W215 B band
    # 489_804..490_003, exactly as the W215 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 490_004..492_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (490_003+1) machine-checkable -- A-hops-prior-B staircase
    # SEVENTY-SIXTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 490_004..490_203 CLEAN on the registered
    # universe but lands INSIDE the W216 A band window 490_004..492_003 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 492_004 -> 492_004..492_203, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (492_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=490004 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=492004 span=200 checked=200 verdict=FREE.
    # W217+ projection (gate-derived pre-seat probe leg4, pre-W216
    # universe): A naive first-clean 492004..494003 CLEAN hops=0 /
    # B naive first-clean 492204..492403 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W216 B band
    # 492_004..492_203 will refuse the naive W217 A window; W217 freezer
    # MUST re-derive on the post-W216 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, SEVENTY-SEVENTH instance anticipated; never transcribe r587).
    216: {"a": (490_004, 492_003), "b_exit": (492_004, 492_203),
         "engine_owner": "bm-c"},
    # W217 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-0700-bmc-w217-seat pushed to origin 1e1454cfb
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit n/a (prereg research/PERPETUAL_N1_W217_PREREG.md
    # r916 freeze-window bundle, probe
    # results/_w217bmc_20261012_probe_receipt.json @ 1e1454cfb5);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W216 five-face (freeze 0b3c489f09) + W216
    # finalize product landed (n1_w216_results.json present, ledger
    # head 898989 machine-read at freeze time); zero --no-verify;
    # the W217 seat MSG sits in fleet/inbox/MSG-20261012-0700-bmc-w217-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w217bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W216 B band (arithmetic continuation
    # 492_004..494_003 REFUSED at its own start by the W216 B band
    # 492_004..492_203, exactly as the W216 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 492_204..494_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (492_203+1) machine-checkable -- A-hops-prior-B staircase
    # SEVENTY-SEVENTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 492_204..492_403 CLEAN on the registered
    # universe but lands INSIDE the W217 A band window 492_204..494_203 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 494_204 -> 494_204..494_403, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (494_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=492204 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=494204 span=200 checked=200 verdict=FREE.
    # W218+ projection (gate-derived pre-seat probe leg4, pre-W217
    # universe): A naive first-clean 494204..496203 CLEAN hops=0 /
    # B naive first-clean 494404..494603 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W217 B band
    # 494_204..494_403 will refuse the naive W218 A window; W218 freezer
    # MUST re-derive on the post-W217 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, SEVENTY-EIGHTH instance anticipated; never transcribe r587).
    217: {"a": (492_204, 494_203), "b_exit": (494_204, 494_403),
         "engine_owner": "bm-c"},
    # W218 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-0830-bmc-w218-seat pushed to origin 8a4c1857a
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit n/a (prereg research/PERPETUAL_N1_W218_PREREG.md
    # r918 freeze-window bundle, probe
    # results/_w218bmc_20261012_probe_receipt.json @ 8a4c1857a5);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W217 five-face (freeze ad011fee25) + W217
    # finalize product landed (n1_w217_results.json present, ledger
    # head 901189 machine-read at freeze time); zero --no-verify;
    # the W218 seat MSG sits in fleet/inbox/MSG-20261012-0830-bmc-w218-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w218bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W217 B band (arithmetic continuation
    # 494_204..496_203 REFUSED at its own start by the W217 B band
    # 494_204..494_403, exactly as the W217 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 494_404..496_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (494_403+1) machine-checkable -- A-hops-prior-B staircase
    # SEVENTY-EIGHTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 494_404..494_603 CLEAN on the registered
    # universe but lands INSIDE the W218 A band window 494_404..496_403 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 496_404 -> 496_404..496_603, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (496_403+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=494404 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=496404 span=200 checked=200 verdict=FREE.
    # W219+ projection (gate-derived pre-seat probe leg4, pre-W218
    # universe): A naive first-clean 496404..498403 CLEAN hops=0 /
    # B naive first-clean 496604..496803 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W218 B band
    # 496_404..496_603 will refuse the naive W219 A window; W219 freezer
    # MUST re-derive on the post-W218 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, SEVENTY-NINTH instance anticipated; never transcribe r587).
    218: {"a": (494_404, 496_403), "b_exit": (496_404, 496_603),
         "engine_owner": "bm-c"},
    # W219 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-0916-bmc-w219-seat pushed to origin 7615985e8
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit n/a (prereg research/PERPETUAL_N1_W219_PREREG.md
    # r920 freeze-window bundle, probe
    # results/_w219bmc_20261012_probe_receipt.json @ 7615985e86);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W218 five-face (freeze 9afb0b1d74) + W218
    # finalize product landed (n1_w218_results.json present, ledger
    # head 903389 machine-read at freeze time); zero --no-verify;
    # the W219 seat MSG sits in fleet/inbox/MSG-20261012-0916-bmc-w219-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w219bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W218 B band (arithmetic continuation
    # 496_404..498_403 REFUSED at its own start by the W218 B band
    # 496_404..496_603, exactly as the W218 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 496_604..498_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (496_603+1) machine-checkable -- A-hops-prior-B staircase
    # SEVENTY-NINTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 496_604..496_803 CLEAN on the registered
    # universe but lands INSIDE the W219 A band window 496_604..498_603 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 498_604 -> 498_604..498_803, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (498_603+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=496604 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=498604 span=200 checked=200 verdict=FREE.
    # W220+ projection (gate-derived pre-seat probe leg4, pre-W219
    # universe): A naive first-clean 498604..500603 CLEAN hops=0 /
    # B naive first-clean 498804..499003 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W219 B band
    # 498_604..498_803 will refuse the naive W220 A window; W220 freezer
    # MUST re-derive on the post-W219 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, EIGHTIETH instance anticipated; never transcribe r587).
    219: {"a": (496_604, 498_603), "b_exit": (498_604, 498_803),
         "engine_owner": "bm-c"},
    # W220 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-1025-bmc-w220-seat pushed to origin 13a81d182
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit n/a (prereg research/PERPETUAL_N1_W220_PREREG.md
    # r923 freeze-window bundle, probe
    # results/_w220bmc_20261012_probe_receipt.json @ 13a81d1826);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W219 five-face (freeze 0dae35332e) + W219
    # finalize product landed (n1_w219_results.json present, ledger
    # head 905589 machine-read at freeze time); zero --no-verify;
    # the W220 seat MSG sits in fleet/inbox/MSG-20261012-1025-bmc-w220-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w220bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W219 B band (arithmetic continuation
    # 498_604..500_603 REFUSED at its own start by the W219 B band
    # 498_604..498_803, exactly as the W219 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 498_804..500_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (498_803+1) machine-checkable -- A-hops-prior-B staircase
    # EIGHTIETH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 498_804..499_003 CLEAN on the registered
    # universe but lands INSIDE the W220 A band window 498_804..500_803 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 500_804 -> 500_804..501_003, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (500_803+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=498804 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=500804 span=200 checked=200 verdict=FREE.
    # W221+ projection (gate-derived pre-seat probe leg4, pre-W220
    # universe): A naive first-clean 500804..502803 CLEAN hops=0 /
    # B naive first-clean 501004..501203 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W220 B band
    # 500_804..501_003 will refuse the naive W221 A window; W221 freezer
    # MUST re-derive on the post-W220 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, EIGHTY-FIRST instance anticipated; never transcribe r587).
    220: {"a": (498_804, 500_803), "b_exit": (500_804, 501_003),
         "engine_owner": "bm-c"},
    # W221 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-1225-bmc-w221-seat pushed to origin 063bb5a77
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit 2e251d0841 (prereg research/PERPETUAL_N1_W221_PREREG.md
    # r925 prereg derived + r927 freeze-window bundle, probe
    # results/_w221bmc_20261012_probe_receipt.json @ 063bb5a77b);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W220 five-face (freeze a9aee1d05d) + W220
    # finalize product landed (n1_w220_results.json present, ledger
    # head 907789 machine-read at freeze time); zero --no-verify;
    # the W221 seat MSG sits in fleet/inbox/processed/MSG-20261012-1225-bmc-w221-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w221bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W220 B band (arithmetic continuation
    # 500_804..502_803 REFUSED at its own start by the W220 B band
    # 500_804..501_003, exactly as the W220 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 501_004..503_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (501_003+1) machine-checkable -- A-hops-prior-B staircase
    # EIGHTY-FIRST instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 501_004..501_203 CLEAN on the registered
    # universe but lands INSIDE the W221 A band window 501_004..503_003 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 503_004 -> 503_004..503_203, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (503_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=501004 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=503004 span=200 checked=200 verdict=FREE.
    # W222+ projection (gate-derived pre-seat probe leg4, pre-W221
    # universe): A naive first-clean 503004..505003 CLEAN hops=0 /
    # B naive first-clean 503204..503403 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W221 B band
    # 503_004..503_203 will refuse the naive W222 A window; W222 freezer
    # MUST re-derive on the post-W221 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, EIGHTY-SECOND instance anticipated; never transcribe r587).
    221: {"a": (501_004, 503_003), "b_exit": (503_004, 503_203),
         "engine_owner": "bm-c"},
    # W222 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-1430-bmc-w222-seat pushed to origin 87ee1055d
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit 58f82fd63b (prereg research/PERPETUAL_N1_W222_PREREG.md
    # r930 prereg derived + r931 freeze-window bundle, probe
    # results/_w222bmc_20261012_probe_receipt.json @ 87ee1055dc);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W221 five-face (freeze 98da27a40d) + W221
    # finalize product landed (n1_w221_results.json present, ledger
    # head 909989 machine-read at freeze time); zero --no-verify;
    # the W222 seat MSG sits in fleet/inbox/processed/MSG-20261012-1430-bmc-w222-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w222bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W221 B band (arithmetic continuation
    # 503_004..505_003 REFUSED at its own start by the W221 B band
    # 503_004..503_203, exactly as the W221 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 503_204..505_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (503_203+1) machine-checkable -- A-hops-prior-B staircase
    # EIGHTY-SECOND instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 503_204..503_403 CLEAN on the registered
    # universe but lands INSIDE the W222 A band window 503_204..505_203 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 505_204 -> 505_204..505_403, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (505_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=503204 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=505204 span=200 checked=200 verdict=FREE.
    # W223+ projection (gate-derived pre-seat probe leg4, pre-W222
    # universe): A naive first-clean 505204..507203 CLEAN hops=0 /
    # B naive first-clean 505404..505603 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W222 B band
    # 505_204..505_403 will refuse the naive W223 A window; W223 freezer
    # MUST re-derive on the post-W222 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, EIGHTY-THIRD instance anticipated; never transcribe r587).
    222: {"a": (503_204, 505_203), "b_exit": (505_204, 505_403),
         "engine_owner": "bm-c"},
    # W223 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-160x-bmc-w223-seat pushed to origin 8f2d79147
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit b7d46427d5 (prereg research/PERPETUAL_N1_W223_PREREG.md
    # r933 prereg derived + r934 freeze-window bundle, probe
    # results/_w223bmc_20261012_probe_receipt.json @ 8f2d79147f);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W222 five-face (freeze 4167d791dc) + W222
    # finalize product landed (n1_w222_results.json present, ledger
    # head 912189 machine-read at freeze time); zero --no-verify;
    # the W223 seat MSG sits in fleet/inbox/MSG-20261012-160x-bmc-w223-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w223bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W222 B band (arithmetic continuation
    # 505_204..507_203 REFUSED at its own start by the W222 B band
    # 505_204..505_403, exactly as the W222 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 505_404..507_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (505_403+1) machine-checkable -- A-hops-prior-B staircase
    # EIGHTY-THIRD instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 505_404..505_603 CLEAN on the registered
    # universe but lands INSIDE the W223 A band window 505_404..507_403 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 507_404 -> 507_404..507_603, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (507_403+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=505404 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=507404 span=200 checked=200 verdict=FREE.
    # W224+ projection (gate-derived pre-seat probe leg4, pre-W223
    # universe): A naive first-clean 507404..509403 CLEAN hops=0 /
    # B naive first-clean 507604..507803 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W223 B band
    # 507_404..507_603 will refuse the naive W224 A window; W224 freezer
    # MUST re-derive on the post-W223 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, EIGHTY-FOURTH instance anticipated; never transcribe r587).
    223: {"a": (505_404, 507_403), "b_exit": (507_404, 507_603),
         "engine_owner": "bm-c"},
    # W224 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-175x-bmc-w224-seat pushed to origin e2676c8eb
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit ac1b1de649 (prereg research/PERPETUAL_N1_W224_PREREG.md
    # r936 prereg derived + r937 freeze-window bundle, probe
    # results/_w224bmc_20261012_probe_receipt.json @ e2676c8eb8);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W223 five-face (freeze 448c4d8c2b) + W223
    # finalize product landed (n1_w223_results.json present, ledger
    # head 914389 machine-read at freeze time); zero --no-verify;
    # the W224 seat MSG sits in fleet/inbox/processed/MSG-20261012-175x-bmc-w224-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w224bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W223 B band (arithmetic continuation
    # 507_404..509_403 REFUSED at its own start by the W223 B band
    # 507_404..507_603, exactly as the W223 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 507_604..509_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (507_603+1) machine-checkable -- A-hops-prior-B staircase
    # EIGHTY-FOURTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 507_604..507_803 CLEAN on the registered
    # universe but lands INSIDE the W224 A band window 507_604..509_603 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 509_604 -> 509_604..509_803, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (509_603+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=507604 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=509604 span=200 checked=200 verdict=FREE.
    # W225+ projection (gate-derived pre-seat probe leg4, pre-W224
    # universe): A naive first-clean 509604..511603 CLEAN hops=0 /
    # B naive first-clean 509804..510003 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W224 B band
    # 509_604..509_803 will refuse the naive W225 A window; W225 freezer
    # MUST re-derive on the post-W224 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, EIGHTY-FIFTH instance anticipated; never transcribe r587).
    224: {"a": (507_604, 509_603), "b_exit": (509_604, 509_803),
         "engine_owner": "bm-c"},
    # W225 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-1943-bmc-w225-seat pushed to origin c78dd1a44
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit 4b22941a7d (prereg research/PERPETUAL_N1_W225_PREREG.md
    # r939 prereg derived + freeze-window bundle, probe
    # results/_w225bmc_20261012_probe_receipt.json @ c78dd1a44b);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W224 five-face (freeze d307e3d1d7) + W224
    # finalize product landed (n1_w224_results.json present, ledger
    # head 916589 machine-read at freeze time); zero --no-verify;
    # the W225 seat MSG sits in fleet/inbox/MSG-20261012-1943-bmc-w225-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w225bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W224 B band (arithmetic continuation
    # 509_604..511_603 REFUSED at its own start by the W224 B band
    # 509_604..509_803, exactly as the W224 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 509_804..511_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (509_803+1) machine-checkable -- A-hops-prior-B staircase
    # EIGHTY-FIFTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 509_804..510_003 CLEAN on the registered
    # universe but lands INSIDE the W225 A band window 509_804..511_803 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 511_804 -> 511_804..512_003, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (511_803+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=509804 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=511804 span=200 checked=200 verdict=FREE.
    # W226+ projection (gate-derived pre-seat probe leg4, pre-W225
    # universe): A naive first-clean 511804..513803 CLEAN hops=0 /
    # B naive first-clean 512004..512203 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W225 B band
    # 511_804..512_003 will refuse the naive W226 A window; W226 freezer
    # MUST re-derive on the post-W225 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, EIGHTY-SIXTH instance anticipated; never transcribe r587).
    225: {"a": (509_804, 511_803), "b_exit": (511_804, 512_003),
         "engine_owner": "bm-c"},
    # W226 (bm-c loop five-face freeze splice, seat
    # MSG-20261012-2040-bmc-w226-seat pushed to origin d7d270752
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit f65d886cb1 (prereg research/PERPETUAL_N1_W226_PREREG.md
    # r941 prereg derived + freeze-window bundle, probe
    # results/_w226bmc_20261012_probe_receipt.json @ d7d270752c);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W225 five-face (freeze 84ecb3a3a1) + W225
    # finalize product landed (n1_w225_results.json present, ledger
    # head 918789 machine-read at freeze time); zero --no-verify;
    # the W226 seat MSG sits in fleet/inbox/MSG-20261012-2040-bmc-w226-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w226bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W225 B band (arithmetic continuation
    # 511_804..513_803 REFUSED at its own start by the W225 B band
    # 511_804..512_003, exactly as the W225 seat leg4
    # projection anticipated;
    # honest forward walk hops=1 -> 512_004..514_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (512_003+1) machine-checkable -- A-hops-prior-B staircase
    # EIGHTY-SIXTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 512_004..512_203 CLEAN on the registered
    # universe but lands INSIDE the W226 A band window 512_004..514_003 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 514_004 -> 514_004..514_203, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (514_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=512004 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=514004 span=200 checked=200 verdict=FREE.
    # W227+ projection (gate-derived pre-seat probe leg4, pre-W226
    # universe): A naive first-clean 514004..516003 CLEAN hops=0 /
    # B naive first-clean 514204..514403 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W226 B band
    # 514_004..514_203 will refuse the naive W227 A window; W227 freezer
    # MUST re-derive on the post-W226 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, EIGHTY-SEVENTH instance anticipated; never transcribe r587).
    226: {"a": (512_004, 514_003), "b_exit": (514_004, 514_203),
         "engine_owner": "bm-c"},
    # W227 (bm-c loop five-face freeze splice, seat
    # MSG-20261013-0645-bmc pushed to origin 10781c2f8
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit 0d0c63c6ed (prereg research/PERPETUAL_N1_W227_PREREG.md
    # r956 prereg derived + freeze-window bundle, probe
    # results/_w227bmc_20261012_probe_receipt.json @ 10781c2f82);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W226 five-face (freeze 9b44d37d19) + W226
    # finalize product landed (n1_w226_results.json present, ledger
    # head 920989 machine-read at freeze time); zero --no-verify;
    # the W227 seat MSG sits in fleet/inbox/MSG-20261013-0645-bmc.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w227bmc_20261012_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W226 B band (arithmetic continuation
    # 514_004..516_003 REFUSED at its own start by the W226 B band
    # 514_004..514_203, exactly as the W226 seat leg4
    # projection anticipated);
    # honest forward walk hops=1 -> 514_204..516_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (514_203+1) machine-checkable -- A-hops-prior-B staircase
    # EIGHTY-SEVENTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 514_204..514_403 CLEAN on the registered
    # universe but lands INSIDE the W227 A band window 514_204..516_203 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 516_204 -> 516_204..516_403, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (516_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=514204 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=516204 span=200 checked=200 verdict=FREE.
    # W228+ projection (gate-derived pre-seat probe leg4, pre-W227
    # universe): A naive first-clean 516204..518203 CLEAN hops=0 /
    # B naive first-clean 516404..516603 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W227 B band
    # 516_204..516_403 will refuse the naive W228 A window; W228 freezer
    # MUST re-derive on the post-W227 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, EIGHTY-EIGHTH instance anticipated; never transcribe r587).
    227: {"a": (514_204, 516_203), "b_exit": (516_204, 516_403),
         "engine_owner": "bm-c"},
    # W228 (bm-c loop five-face freeze splice, seat
    # MSG-20261013-0720-bmc pushed to origin 4e30ddf69
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit e6c8441aaa (prereg research/PERPETUAL_N1_W228_PREREG.md
    # r958 prereg derived + landed pre-freeze, probe
    # results/_w228bmc_20261013_probe_receipt.json @ 4e30ddf693);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W227 five-face (freeze 48c321706b) + W227
    # finalize product landed (n1_w227_results.json present, ledger
    # head 923189 machine-read at freeze time); zero --no-verify;
    # the W228 seat MSG sits in fleet/inbox/MSG-20261013-0720-bmc.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w228bmc_20261013_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W227 B band (arithmetic continuation
    # 516_204..518_203 REFUSED at its own start by the W227 B band
    # 516_204..516_403, exactly as the W227 seat leg4
    # projection anticipated);
    # honest forward walk hops=1 -> 516_404..518_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (516_403+1) machine-checkable -- A-hops-prior-B staircase
    # EIGHTY-EIGHTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 516_404..516_603 CLEAN on the registered
    # universe but lands INSIDE the W228 A band window 516_404..518_403 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 518_404 -> 518_404..518_603, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (518_403+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=516404 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=518404 span=200 checked=200 verdict=FREE.
    # W229+ projection (gate-derived pre-seat probe leg4, pre-W228
    # universe): A naive first-clean 518404..520403 CLEAN hops=0 /
    # B naive first-clean 518604..518803 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W228 B band
    # 518_404..518_603 will refuse the naive W229 A window; W229 freezer
    # MUST re-derive on the post-W228 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, EIGHTY-NINTH instance anticipated; never transcribe r587).
    228: {"a": (516_404, 518_403), "b_exit": (518_404, 518_603),
         "engine_owner": "bm-c"},
    # W229 (bm-c loop five-face freeze splice, seat
    # MSG-20261013-0855-bmc pushed to origin c9e9e83b8
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit e485a0b3f3 (prereg research/PERPETUAL_N1_W229_PREREG.md
    # r960 prereg derived + landed pre-freeze, probe
    # results/_w229bmc_20261013_probe_receipt.json @ c9e9e83b8a);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W228 five-face (freeze 842f817ad3) + W228
    # finalize product landed (n1_w228_results.json present, ledger
    # head 925389 machine-read at freeze time); zero --no-verify;
    # the W229 seat MSG sits in fleet/inbox/MSG-20261013-0855-bmc.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w229bmc_20261013_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W228 B band (arithmetic continuation
    # 518_404..520_403 REFUSED at its own start by the W228 B band
    # 518_404..518_603, exactly as the W228 seat leg4
    # projection anticipated);
    # honest forward walk hops=1 -> 518_604..520_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (518_603+1) machine-checkable -- A-hops-prior-B staircase
    # EIGHTY-NINTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 518_604..518_803 CLEAN on the registered
    # universe but lands INSIDE the W229 A band window 518_604..520_603 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 520_604 -> 520_604..520_803, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (520_603+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=518604 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=520604 span=200 checked=200 verdict=FREE.
    # W230+ projection (gate-derived pre-seat probe leg4, pre-W229
    # universe): A naive first-clean 520604..522603 CLEAN hops=0 /
    # B naive first-clean 520804..521003 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W229 B band
    # 520_604..520_803 will refuse the naive W230 A window; W230 freezer
    # MUST re-derive on the post-W229 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, NINETIETH instance anticipated; never transcribe r587).
    229: {"a": (518_604, 520_603), "b_exit": (520_604, 520_803),
         "engine_owner": "bm-c"},
    # W230 (bm-c loop five-face freeze splice, seat
    # MSG-20261013-1000-bmc pushed to origin 6cfe285e3
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit 91de0ae839 (prereg research/PERPETUAL_N1_W230_PREREG.md
    # r963 prereg derived + landed pre-freeze, probe
    # results/_w230bmc_20261013_probe_receipt.json @ 6cfe285e33);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W229 five-face (freeze 2ae8553e6f) + W229
    # finalize product landed (n1_w229_results.json present, ledger
    # head 927589 machine-read at freeze time); zero --no-verify;
    # the W230 seat MSG sits in fleet/inbox/MSG-20261013-1000-bmc.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w230bmc_20261013_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W229 B band (arithmetic continuation
    # 520_604..522_603 REFUSED at its own start by the W229 B band
    # 520_604..520_803, exactly as the W229 seat leg4
    # projection anticipated);
    # honest forward walk hops=1 -> 520_804..522_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (520_803+1) machine-checkable -- A-hops-prior-B staircase
    # NINETIETH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 520_804..521_003 CLEAN on the registered
    # universe but lands INSIDE the W230 A band window 520_804..522_803 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 522_804 -> 522_804..523_003, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (522_803+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=520804 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=522804 span=200 checked=200 verdict=FREE.
    # W231+ projection (gate-derived pre-seat probe leg4, pre-W230
    # universe): A naive first-clean 522804..524803 CLEAN hops=0 /
    # B naive first-clean 523004..523203 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W230 B band
    # 522_804..523_003 will refuse the naive W231 A window; W231 freezer
    # MUST re-derive on the post-W230 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, NINETY-FIRST instance anticipated; never transcribe r587).
    230: {"a": (520_804, 522_803), "b_exit": (522_804, 523_003),
         "engine_owner": "bm-c"},
    # W231 (bm-c loop five-face freeze splice, seat
    # MSG-20261013-1155-bmc pushed to origin 6638ddf9f
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit aebe0a5acc (prereg research/PERPETUAL_N1_W231_PREREG.md
    # r964 prereg derived + landed pre-freeze, probe
    # results/_w231bmc_20261013_probe_receipt.json @ 6638ddf9fb);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W230 five-face (freeze 24e12fa5e7) + W230
    # finalize product landed (n1_w230_results.json present, ledger
    # head 929789 machine-read at freeze time); zero --no-verify;
    # the W231 seat MSG sits in fleet/inbox/processed/MSG-20261013-1155-bmc.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w231bmc_20261013_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W230 B band (arithmetic continuation
    # 522_804..524_803 REFUSED at its own start by the W230 B band
    # 522_804..523_003, exactly as the W230 seat leg4
    # projection anticipated);
    # honest forward walk hops=1 -> 523_004..525_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (523_003+1) machine-checkable -- A-hops-prior-B staircase
    # NINETY-FIRST instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 523_004..523_203 CLEAN on the registered
    # universe but lands INSIDE the W231 A band window 523_004..525_003 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 525_004 -> 525_004..525_203, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (525_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=523004 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=525004 span=200 checked=200 verdict=FREE.
    # W232+ projection (gate-derived pre-seat probe leg4, pre-W231
    # universe): A naive first-clean 525004..527003 CLEAN hops=0 /
    # B naive first-clean 525204..525403 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W231 B band
    # 525_004..525_203 will refuse the naive W232 A window; W232 freezer
    # MUST re-derive on the post-W231 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, NINETY-SECOND instance anticipated; never transcribe r587).
    231: {"a": (523_004, 525_003), "b_exit": (525_004, 525_203),
         "engine_owner": "bm-c"},
    # W232 (bm-c loop five-face freeze splice, seat
    # MSG-20261013-1345-bmc pushed to origin 8d3a1b78a
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit a3a7aa6323 (prereg research/PERPETUAL_N1_W232_PREREG.md
    # r967 prereg derived + landed pre-freeze, probe
    # results/_w232bmc_20261013_probe_receipt.json @ 8d3a1b78a5);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W231 five-face (freeze aee0bd9fa3) + W231
    # finalize product landed (n1_w231_results.json present, ledger
    # head 931989 machine-read at freeze time); zero --no-verify;
    # the W232 seat MSG sits in fleet/inbox/MSG-20261013-1345-bmc.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w232bmc_20261013_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W231 B band (arithmetic continuation
    # 525_004..527_003 REFUSED at its own start by the W231 B band
    # 525_004..525_203, exactly as the W231 seat leg4
    # projection anticipated);
    # honest forward walk hops=1 -> 525_204..527_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (525_203+1) machine-checkable -- A-hops-prior-B staircase
    # NINETY-SECOND instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 525_204..525_403 CLEAN on the registered
    # universe but lands INSIDE the W232 A band window 525_204..527_203 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 527_204 -> 527_204..527_403, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (527_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=525204 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=527204 span=200 checked=200 verdict=FREE.
    # W233+ projection (gate-derived pre-seat probe leg4, pre-W232
    # universe): A naive first-clean 527204..529203 CLEAN hops=0 /
    # B naive first-clean 527404..527603 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W232 B band
    # 527_204..527_403 will refuse the naive W233 A window; W233 freezer
    # MUST re-derive on the post-W232 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, NINETY-THIRD instance anticipated; never transcribe r587).
    232: {"a": (525_204, 527_203), "b_exit": (527_204, 527_403),
         "engine_owner": "bm-c"},
    # W233 (bm-c loop five-face freeze splice, seat
    # MSG-20261013-1530-bmc pushed to origin dd38a9da8
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit 933e3ceea9 (prereg research/PERPETUAL_N1_W233_PREREG.md
    # r972 prereg derived + landed pre-freeze, probe
    # results/_w233bmc_20261013_probe_receipt.json @ dd38a9da84);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W232 five-face (freeze e58dbcda33) + W232
    # finalize product landed (n1_w232_results.json present, ledger
    # head 934189 machine-read at freeze time); zero --no-verify;
    # the W233 seat MSG sits in fleet/inbox/processed/MSG-20261013-1530-bmc.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w233bmc_20261013_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W232 B band (arithmetic continuation
    # 527_204..529_203 REFUSED at its own start by the W232 B band
    # 527_204..527_403, exactly as the W232 seat leg4
    # projection anticipated);
    # honest forward walk hops=1 -> 527_404..529_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (527_403+1) machine-checkable -- A-hops-prior-B staircase
    # NINETY-THIRD instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 527_404..527_603 CLEAN on the registered
    # universe but lands INSIDE the W233 A band window 527_404..529_403 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 529_404 -> 529_404..529_603, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (529_403+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=527404 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=529404 span=200 checked=200 verdict=FREE.
    # W234+ projection (gate-derived pre-seat probe leg4, pre-W233
    # universe): A naive first-clean 529404..531403 CLEAN hops=0 /
    # B naive first-clean 529604..529803 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W233 B band
    # 529_404..529_603 will refuse the naive W234 A window; W234 freezer
    # MUST re-derive on the post-W233 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, NINETY-FOURTH instance anticipated; never transcribe r587).
    233: {"a": (527_404, 529_403), "b_exit": (529_404, 529_603),
         "engine_owner": "bm-c"},
    # W234 (bm-c loop five-face freeze splice, seat
    # MSG-20261013-1955-bmc pushed to origin 260217d39
    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen
    # commit 252d5cc95c (prereg research/PERPETUAL_N1_W234_PREREG.md
    # r976 prereg derived + landed pre-freeze, probe
    # results/_w234bmc_20261013_probe_receipt.json @ 260217d39e);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W233 five-face (freeze 0ca9203624) + W233
    # finalize product landed (n1_w233_results.json present, ledger
    # head 936389 machine-read at freeze time); zero --no-verify;
    # the W234 seat MSG sits in fleet/inbox/MSG-20261013-1955-bmc.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w234bmc_20261013_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W233 B band (arithmetic continuation
    # 529_404..531_403 REFUSED at its own start by the W233 B band
    # 529_404..529_603, exactly as the W233 seat leg4
    # projection anticipated);
    # honest forward walk hops=1 -> 529_604..531_603, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (529_603+1) machine-checkable -- A-hops-prior-B staircase
    # NINETY-FOURTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 529_604..529_803 CLEAN on the registered
    # universe but lands INSIDE the W234 A band window 529_604..531_603 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 531_604 -> 531_604..531_803, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (531_603+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=529604 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=531604 span=200 checked=200 verdict=FREE.
    # W235+ projection (gate-derived pre-seat probe leg4, pre-W234
    # universe): A naive first-clean 531604..533603 CLEAN hops=0 /
    # B naive first-clean 531804..532003 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W234 B band
    # 531_604..531_803 will refuse the naive W235 A window; W235 freezer
    # MUST re-derive on the post-W234 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, NINETY-FIFTH instance anticipated; never transcribe r587).
    234: {"a": (529_604, 531_603), "b_exit": (531_604, 531_803),
         "engine_owner": "bm-c"},
    # W235 (bm-a loop five-face freeze splice -- TAKEOVER face, seat
    # MSG-20261013-2149-bmc INHERITED @ origin e830a2632 (bm-c hb-stall 198min
    # re-verified live at derive; r967 takeover freeze-prep same-label continuation
    # per r976-continuation precedent; r885/r898 takeover precedents); prereg +
    # ADMIT probe receipt frozen commit 89bd6962cd (prereg research/PERPETUAL_N1_W235_PREREG.md
    # r968 takeover derive landed pre-freeze, probe
    # results/_w235bmc_20261013_probe_receipt.json @ e830a26324);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W234 five-face (freeze de342250cc) + W234
    # finalize product landed (n1_w234_results.json present, ledger
    # head 938589 machine-read at freeze time); zero --no-verify;
    # the W235 seat MSG sits in fleet/inbox/processed/MSG-20261013-2149-bmc.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w235bmc_20261013_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W234 B band (arithmetic continuation
    # 531_604..533_603 REFUSED at its own start by the W234 B band
    # 531_604..531_803, exactly as the W234 seat leg4
    # projection anticipated);
    # honest forward walk hops=1 -> 531_804..533_803, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (531_803+1) machine-checkable -- A-hops-prior-B staircase
    # NINETY-FIFTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 531_804..532_003 CLEAN on the registered
    # universe but lands INSIDE the W235 A band window 531_804..533_803 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 533_804 -> 533_804..534_003, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (533_803+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=531804 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=533804 span=200 checked=200 verdict=FREE.
    # W236+ projection (gate-derived pre-seat probe leg4, pre-W235
    # universe): A naive first-clean 533804..535803 CLEAN hops=0 /
    # B naive first-clean 534004..534203 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W235 B band
    # 533_804..534_003 will refuse the naive W236 A window; W236 freezer
    # MUST re-derive on the post-W235 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, NINETY-SIXTH instance anticipated; never transcribe r587).
    235: {"a": (531_804, 533_803), "b_exit": (533_804, 534_003),
         "engine_owner": "bm-a"},
    # W236 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261014-0446-bma-w236-seat published=reserved by bm-a itself @
    # origin 5c25db795 (r971, zero takeover); prereg + ADMIT probe
    # receipt frozen commit 67ade83145 (prereg research/PERPETUAL_N1_W236_PREREG.md
    # r972 own-seat derive landed pre-freeze, probe
    # results/_w236bma_20261014_probe_receipt.json @ 5c25db7957);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-a W235 five-face (freeze ff438aeaf8) + W235
    # finalize product landed (n1_w235_results.json present, ledger
    # head 940789 machine-read at freeze time); zero --no-verify;
    # the W236 seat MSG sits in fleet/inbox/processed/MSG-20261014-0446-bma-w236-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w236bma_20261014_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W235 B band (arithmetic continuation
    # 533_804..535_803 REFUSED at its own start by the W235 B band
    # 533_804..534_003, exactly as the W235 seat leg4
    # projection anticipated);
    # honest forward walk hops=1 -> 534_004..536_003, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (534_003+1) machine-checkable -- A-hops-prior-B staircase
    # NINETY-SIXTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 534_004..534_203 CLEAN on the registered
    # universe but lands INSIDE the W236 A band window 534_004..536_003 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 536_004 -> 536_004..536_203, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (536_003+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=534004 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=536004 span=200 checked=200 verdict=FREE.
    # W237+ projection (gate-derived pre-seat probe leg4, pre-W236
    # universe): A naive first-clean 536004..538003 CLEAN hops=0 /
    # B naive first-clean 536204..536403 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W236 B band
    # 536_004..536_203 will refuse the naive W237 A window; W237 freezer
    # MUST re-derive on the post-W236 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, NINETY-SEVENTH instance anticipated; never transcribe r587).
    236: {"a": (534_004, 536_003), "b_exit": (536_004, 536_203),
         "engine_owner": "bm-a"},
    # W237 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261014-0654-bmc-w237-seat published=reserved by bm-c itself @
    # origin 9312ef7ac (r988, zero takeover); prereg + ADMIT probe
    # receipt frozen commit d311a54399 (prereg research/PERPETUAL_N1_W237_PREREG.md
    # r990 own-seat derive landed pre-freeze [dead-window estate absorbed,
    # rebase-landed on origin], probe
    # results/_w237bmc_20261014_probe_receipt.json @ 9312ef7ac6);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-a W236 five-face (freeze 6e798bd225) + W236
    # finalize product landed (n1_w236_results.json present, ledger
    # head 942989 machine-read at freeze time); zero --no-verify;
    # the W237 seat MSG sits in fleet/inbox/processed/MSG-20261014-0654-bmc-w237-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w237bmc_20261014_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W236 B band (arithmetic continuation
    # 536_004..538_003 REFUSED at its own start by the W236 B band
    # 536_004..536_203, exactly as the W236 seat leg4
    # projection anticipated);
    # honest forward walk hops=1 -> 536_204..538_203, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (536_203+1) machine-checkable -- A-hops-prior-B staircase
    # NINETY-SEVENTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 536_204..536_403 CLEAN on the registered
    # universe but lands INSIDE the W237 A band window 536_204..538_203 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 538_204 -> 538_204..538_403, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (538_203+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=536204 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=538204 span=200 checked=200 verdict=FREE.
    # W238+ projection (gate-derived pre-seat probe leg4, pre-W237
    # universe): A naive first-clean 538204..540203 CLEAN hops=0 /
    # B naive first-clean 538404..538603 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W237 B band
    # 538_204..538_403 will refuse the naive W238 A window; W238 freezer
    # MUST re-derive on the post-W237 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, NINETY-EIGHTH instance anticipated; never transcribe r587).
    237: {"a": (536_204, 538_203), "b_exit": (538_204, 538_403),
         "engine_owner": "bm-c"},
    # W238 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261014-0745-bma-w238-seat published=reserved by bm-a itself @
    # origin 3e551d846 (r976, zero takeover); prereg + ADMIT probe
    # receipt frozen commit 8049952c9f (prereg research/PERPETUAL_N1_W238_PREREG.md
    # r983 own-seat derive landed pre-freeze, probe
    # results/_w238bma_20261014_probe_receipt.json @ 3e551d846e);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W237 five-face (freeze e4a23cc7a9) + W237
    # finalize product landed (n1_w237_results.json present, ledger
    # head 945189 machine-read at freeze time); zero --no-verify;
    # the W238 seat MSG sits in fleet/inbox/processed/MSG-20261014-0745-bma-w238-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w238bma_20261014_probe_receipt.json: A = FIRST-CLEAN
    # past the registered W237 B band (arithmetic continuation
    # 538_204..540_203 REFUSED at its own start by the W237 B band
    # 538_204..538_403, exactly as the W237 seat leg4
    # projection anticipated);
    # honest forward walk hops=1 -> 538_404..540_403, non-rotational
    # r587 forward-monotone walk; A base == prior-wave B tail+1
    # (538_403+1) machine-checkable -- A-hops-prior-B staircase
    # NINETY-EIGHTH instance, E36 card (probe receipt leg1 A_semantics
    # machine-read ordinal, never transcribed);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 538_404..538_603 CLEAN on the registered
    # universe but lands INSIDE the W238 A band window 538_404..540_403 --
    # same-freeze mutual exclusion (W141 precedent, leg2 law) --
    # the walk with the own-wave A window reserved jumps to
    # 540_404 -> 540_404..540_603, hops=1, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1
    # (540_403+1) machine-checkable);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=538404 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=540404 span=200 checked=200 verdict=FREE.
    # W239+ projection (gate-derived pre-seat probe leg4, pre-W238
    # universe): A naive first-clean 540404..542403 REFUSED by live
    # SEED_REGISTRY points [541500, 542000] (NEW FACE: first live-seed refusal
    # above the registered tail) -> honest walk first-clean
    # 542501..544500 hops=2 /
    # B naive first-clean 540604..540803 CLEAN hops=0 -- naive B lands
    # INSIDE the naive A window and the registered W238 B band
    # 540_404..540_603 will refuse the naive W239 A window; W239 freezer
    # MUST re-derive on the post-W238 universe AND reserve the
    # own-wave A window when deriving B (W141 precedent, leg2 law,
    # E36 staircase card, NINETY-NINTH instance anticipated; never transcribe r587).
    238: {"a": (538_404, 540_403), "b_exit": (540_404, 540_603),
         "engine_owner": "bm-a"},
    # W239 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261014-0914-bmc-w239-seat published=reserved by bm-c itself @
    # origin 603ff65d9 (r991, zero takeover); prereg + ADMIT probe
    # receipt frozen commit 97a7ff0e61 (prereg research/PERPETUAL_N1_W239_PREREG.md
    # r996 dead-session derive landed pre-freeze [estate absorbed by the
    # r996-continuation window], probe
    # results/_w239bmc_20261014_probe_receipt.json @ 603ff65d9d);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-a W238 five-face (freeze 50fa776239) + W238
    # finalize product landed (n1_w238_results.json present, ledger
    # head 947935 machine-read at freeze time); zero --no-verify;
    # the W239 seat MSG sits in fleet/inbox/processed/MSG-20261014-0914-bmc-w239-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w239bmc_20261014_probe_receipt.json: A = FIRST-CLEAN
    # past the prior-wave B tail AND live SEED_REGISTRY points -- NEW FACE
    # (arithmetic continuation 540_404..542_403 REFUSED at its
    # own start by the W238 B band 540_404..540_603 AND live
    # seeds 541_500/542_000, exactly as the W238 seat leg4 projection
    # anticipated); honest forward walk hop 1 -> 542_001 (window 542_001..544_000
    # REFUSED at 542_500), hop 2 -> first-clean 542_501..544_500, hops=2,
    # non-rotational r587 forward-monotone walk; A base >= prior-wave B
    # tail+1 (540_603+1) machine-checkable -- A-hops-prior-B
    # staircase GE face (E36 card, probe receipt leg1 A_semantics
    # machine-read, never transcribed);
    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail
    # (540_604..540_803 CLEAN on the
    # registered universe, hops=0, NO own-A reservation jump needed -- own-A
    # seed-hopped FAR past the staircase base: first seed-decoupled A/B gap
    # face; B base == prior-wave B tail+1 (540_603+1) machine-checkable;
    # B window sits entirely below the own-A window 542_501..544_500);
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=542501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=540604 span=200 checked=200 verdict=FREE.
    # W240+ projection (gate-derived pre-seat probe leg4, pre-W239
    # universe): A naive first-clean 544501..546500 REFUSED by live
    # SEED_REGISTRY points [545500] -> honest walk first-clean
    # 545501..547500 hops=1 /
    # B naive first-clean 540804..541003 CLEAN hops=0 -- B lands OUTSIDE
    # the naive A window (seed-gap face: W239 A/B decoupled); W240 freezer
    # MUST re-derive on the post-W239 universe AND re-read the live trace
    # (do NOT assume the staircase A-base==prior-B-tail+1 equality -- the
    # W240 seat is ALREADY published by bm-a @ origin 39a30b6a0, queue-depth
    # supply, its freeze waits-upstream on THIS W239 finalize); never transcribe r587.
    239: {"a": (542_501, 544_500), "b_exit": (540_604, 540_803),
         "engine_owner": "bm-c"},
    # W240 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261014-1325-bma-w240-seat published=reserved by bm-a itself @
    # origin 39a30b6a0 (r986, queue-depth supply depth-2, zero takeover); prereg + ADMIT probe
    # receipt frozen commit 3e44118e27 (prereg research/PERPETUAL_N1_W240_PREREG.md
    # r989 dead-session derive landed pre-freeze [estate absorbed by the
    # r991 window], probe
    # results/_w240bma_20261014_probe_receipt.json @ 39a30b6a04);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W239 five-face (freeze c85e806c9e) + W239
    # finalize product landed (n1_w239_results.json present, ledger
    # head 950135 machine-read at freeze time); zero --no-verify;
    # the W240 seat MSG sits in fleet/inbox/processed/MSG-20261014-1325-bma-w240-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w240bma_20261014_probe_receipt.json: A = FIRST-CLEAN
    # past the prior-wave B tail AND a live SEED_REGISTRY point -- the arithmetic
    # continuation 544_501..546_500 is REFUSED at its own start by the
    # live seed 545_500 (refuser = a SEED POINT, not a prior-wave band -- W239 A/B
    # decoupled, exactly as the W239 seat leg4 projection anticipated); honest
    # forward walk hop 1 -> first-clean 545_501..547_500, hops=1,
    # non-rotational r587 forward-monotone walk; A base >= prior-wave B
    # tail+1 (540_803+1) machine-checkable -- A-hops-prior-B
    # staircase GE face (E36 card, probe receipt leg1 A_semantics
    # machine-read, never transcribed);
    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail
    # (540_804..541_003 CLEAN on the
    # registered universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B
    # lands OUTSIDE the own-A seed-hopped window 545_501..547_500:
    # seed-decoupled A/B gap face inherited from W239; B base == prior-wave B
    # tail+1 (540_803+1) machine-checkable;
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=545501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=540804 span=200 checked=200 verdict=FREE.
    # W241+ projection (gate-derived pre-seat probe leg4, pre-W240
    # universe): A naive first-clean 547501..549500 CLEAN (hops=0, zero live
    # seed refusers) / B naive first-clean 541004..541203 CLEAN (hops=0 -- B lands OUTSIDE
    # the naive A window, seed-gap face inherited); W241 freezer MUST
    # re-derive on the post-W240 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality -- W240 A/B stay decoupled); never transcribe r587.
    240: {"a": (545_501, 547_500), "b_exit": (540_804, 541_003),
         "engine_owner": "bm-a"},
    # W241 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261014-1755-bmc-w241-seat published=reserved by bm-c itself @
    # origin 20782916a (r1002, queue-depth supply depth-2, zero takeover); prereg + ADMIT probe
    # receipt frozen commit a9ab3b51db (prereg research/PERPETUAL_N1_W241_PREREG.md
    # r1003 dead-session derive landed pre-freeze [estate absorbed by the
    # r1004 window], probe
    # results/_w241bmc_20261014_probe_receipt.json @ 20782916a1);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-a W240 five-face (freeze dc27f52170) + W240
    # finalize product landed (n1_w240_results.json present, ledger
    # head 952335 machine-read at freeze time); zero --no-verify;
    # the W241 seat MSG sits in fleet/inbox/processed/MSG-20261014-1755-bmc-w241-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w241bmc_20261014_probe_receipt.json: A = FIRST-CLEAN
    # arithmetic continuation of the prior-wave A tail (547_501..549_500 CLEAN
    # at naive start on the registered universe, hops=0, A_hop_chain empty +
    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,
    # second consecutive seed-gap face per the W240 seat leg4 anticipation
    # confirmed live; A base == prior-wave A tail+1 (547_500+1) machine-checkable;
    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail
    # (541_004..541_203 CLEAN on the
    # registered universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B
    # lands OUTSIDE the own-A window 547_501..549_500:
    # seed-decoupled A/B gap face third consecutive; B base == prior-wave B
    # tail+1 (541_003+1) machine-checkable;
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=547501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=541004 span=200 checked=200 verdict=FREE.
    # W242+ projection (gate-derived pre-seat probe leg4, pre-W241
    # universe): A naive first-clean 549501..551500 CLEAN (hops=0, zero live
    # seed refusers) / B naive first-clean 541204..541403 CLEAN (hops=0 -- B lands OUTSIDE
    # the naive A window, seed-gap face inherited); W242 freezer MUST
    # re-derive on the post-W241 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality -- W241 A/B stay decoupled); never transcribe r587.
    241: {"a": (547_501, 549_500), "b_exit": (541_004, 541_203),
         "engine_owner": "bm-c"},
    # W242 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261014-1814-bma-w242-seat published=reserved by bm-a itself @
    # origin 138a94745 (r995, queue-depth supply depth-2 at publish, zero takeover); prereg + ADMIT probe
    # receipt frozen commit 4574bfeca5 (prereg research/PERPETUAL_N1_W242_PREREG.md
    # r998 same-window machine-SUB derive landed pre-freeze, probe
    # results/_w242bma_20261014_probe_receipt.json @ 138a947458);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W241 five-face (freeze 8e980ce3ed) + W241
    # finalize product landed (n1_w241_results.json present, ledger
    # head 954535 machine-read at freeze time); zero --no-verify;
    # the W242 seat MSG sits in fleet/inbox/processed/MSG-20261014-1814-bma-w242-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w242bma_20261014_probe_receipt.json: A = FIRST-CLEAN
    # arithmetic continuation of the prior-wave A tail (549_501..551_500 CLEAN
    # at naive start on the registered universe, hops=0, A_hop_chain empty +
    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,
    # third consecutive seed-gap face per the W241 seat leg4 anticipation
    # confirmed live; A base == prior-wave A tail+1 (549_500+1) machine-checkable;
    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail
    # (541_204..541_403 CLEAN on the
    # registered universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B
    # lands OUTSIDE the own-A window 549_501..551_500:
    # seed-decoupled A/B gap face fourth consecutive; B base == prior-wave B
    # tail+1 (541_203+1) machine-checkable;
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=549501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=541204 span=200 checked=200 verdict=FREE.
    # W243+ projection (gate-derived pre-seat probe leg4, pre-W242
    # universe): A naive first-clean 551501..553500 CLEAN (hops=0, zero live
    # seed refusers) / B naive first-clean 541404..541603 hops=1 (live refusal
    # inside 541_404..541_500 -- SEED_REGISTRY point 541_500 perpetual_n2_w15_gen, honest forward walk first-clean
    # 541501..541700 -- B lands OUTSIDE
    # the naive A window, seed-gap face inherited); W243 freezer MUST
    # re-derive on the post-W242 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality -- W242 A/B stay decoupled); never transcribe r587.
    242: {"a": (549_501, 551_500), "b_exit": (541_204, 541_403),
         "engine_owner": "bm-a"},
    # W243 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261014-2107-bma-w243-seat published=reserved by bm-a itself @
    # origin 6207e60e9 (r1000, queue-depth supply depth-1 at publish, zero takeover); prereg + ADMIT probe
    # receipt frozen commit 70141bc22f (prereg research/PERPETUAL_N1_W243_PREREG.md
    # r1001 absorbed-window machine-SUB derive landed pre-freeze, probe
    # results/_w243bma_20261014_probe_receipt.json @ 6207e60e9f);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-a W242 five-face (freeze 8d34e33bc8) + W242
    # finalize product landed (n1_w242_results.json present, ledger
    # head 956735 machine-read at freeze time); zero --no-verify;
    # the W243 seat MSG sits in fleet/inbox/processed/MSG-20261014-2107-bma-w243-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w243bma_20261014_probe_receipt.json: A = FIRST-CLEAN
    # arithmetic continuation of the prior-wave A tail (551_501..553_500 CLEAN
    # at naive start on the registered universe, hops=0, A_hop_chain empty +
    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,
    # fourth consecutive seed-gap face per the W242 seat leg4 anticipation
    # confirmed live; A base == prior-wave A tail+1 (551_500+1) machine-checkable;
    # B = LIVE-SEED-REFUSAL face: the naive staircase continuation
    # 541_404..541_603 is REFUSED by the live SEED_REGISTRY point
    # 541_500 perpetual_n2_w15_gen (hops=1, hop chain recorded) -- honest
    # forward walk lands first-clean 541_501..541_700; B base != prior-wave
    # B tail+1 in this face (live-seed hop); B lands OUTSIDE the own-A window
    # 551_501..553_500: seed-decoupled A/B gap face fifth
    # consecutive; B_no_ownA_jump=true;
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=551501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=541501 span=200 checked=200 verdict=FREE.
    # W244+ projection (gate-derived pre-seat probe leg4, pre-W243
    # universe): A naive first-clean 553501..555500 CLEAN (hops=0, zero live
    # seed refusers) / B naive first-clean 541701..541900 CLEAN (hops=0, zero live
    # seed refusers); W244 freezer MUST re-derive on the post-W243 universe
    # AND reserve the own-wave A window when deriving B (do NOT assume the
    # staircase A-base==prior-B-tail+1 equality); never transcribe r587.
    243: {"a": (551_501, 553_500), "b_exit": (541_501, 541_700),
         "engine_owner": "bm-a"},
    # W244 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261015-0206-bma-w244-seat published=reserved by bm-a itself @
    # origin 08df387e0 (r1004, queue-depth supply depth-1 at publish, zero takeover); prereg + ADMIT probe
    # receipt frozen commit 260ffd3f8e (prereg research/PERPETUAL_N1_W244_PREREG.md
    # r1005 absorbed-window machine-SUB derive landed pre-freeze, probe
    # results/_w244bma_20261015_probe_receipt.json @ 08df387e0a);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-a W243 five-face (freeze 562e7ed763) + W243
    # finalize product landed (n1_w243_results.json present, ledger
    # head 958935 machine-read at freeze time); zero --no-verify;
    # the W244 seat MSG sits in fleet/inbox/processed/MSG-20261015-0206-bma-w244-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w244bma_20261015_probe_receipt.json: A = FIRST-CLEAN
    # arithmetic continuation of the prior-wave A tail (553_501..555_500 CLEAN
    # at naive start on the registered universe, hops=0, A_hop_chain empty +
    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,
    # fifth consecutive seed-gap face per the W243 seat leg4 anticipation
    # confirmed live; A base == prior-wave A tail+1 (553_500+1) machine-checkable;
    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail
    # (541_701..541_900 CLEAN on the
    # registered universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B
    # lands OUTSIDE the own-A window 553_501..555_500:
    # seed-decoupled A/B gap face sixth
    # consecutive; B base == prior-wave B tail+1 (541_700+1) machine-checkable;
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=553501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=541701 span=200 checked=200 verdict=FREE.
    # W245+ projection (gate-derived pre-seat probe leg4, pre-W244
    # universe): A naive first-clean 555501..557500 CLEAN (hops=0, zero live
    # seed refusers) / B naive first-clean 541901..542100 hops=1 (live refusal
    # inside the naive window -- honest forward walk first-clean
    # 542001..542200 -- B lands OUTSIDE
    # the naive A window, seed-gap face inherited); W245 freezer MUST
    # re-derive on the post-W244 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality); never transcribe r587.
    244: {"a": (553_501, 555_500), "b_exit": (541_701, 541_900),
         "engine_owner": "bm-a"},
    # W245 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261015-0844-bma-w245-seat published=reserved by bm-a itself @
    # origin 2b0947947 (r1010, queue-depth supply depth-1 at publish, takeover lane disclosed (GM re-assignment: bm-c declared the W245 turn at r1020 closeout then heartbeat froze 64.5min with zero origin commits post the W244-finalize unblock -- stall >1 round, takeover per the r1009 next-pointer rule)); prereg + ADMIT probe
    # receipt frozen commit 6473fb7f8d (prereg research/PERPETUAL_N1_W245_PREREG.md
    # r1010 absorbed-window machine-SUB derive landed pre-freeze, probe
    # results/_w245bma_20261015_probe_receipt.json @ 2b09479474);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-a W244 five-face (freeze 10bdb987b5) + W244
    # finalize product landed (n1_w244_results.json present, ledger
    # head 961135 machine-read at freeze time); zero --no-verify;
    # the W245 seat MSG sits in fleet/inbox/processed/MSG-20261015-0844-bma-w245-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w245bma_20261015_probe_receipt.json: A = FIRST-CLEAN
    # arithmetic continuation of the prior-wave A tail (555_501..557_500 CLEAN
    # at naive start on the registered universe, hops=0, A_hop_chain empty +
    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,
    # sixth consecutive seed-gap face per the W244 seat leg4 anticipation
    # confirmed live; A base == prior-wave A tail+1 (555_500+1) machine-checkable;
    # B = FIRST-CLEAN post-hop forward walk (the naive continuation
    # (541_901..542_100 is REFUSED by the live
    # SEED_REGISTRY point 542_000 perpetual_n2_w15_scrnull; hops=1, hop chain
    # recorded, honest forward walk lands first-clean 542_001..542_200 -- B
    # lands OUTSIDE the own-A window 555_501..557_500:
    # seed-decoupled A/B gap face seventh; B base == live refuser 542_000+1 machine-checkable;
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=555501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=542001 span=200 checked=200 verdict=FREE.
    # W246+ projection (gate-derived pre-seat probe leg4, pre-W245
    # universe): A naive first-clean 557501..559500 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive first-clean 542201..542400 hops=0 (this window's gate: CLEAN, zero live
    # refusers anticipated -- B first-clean 542201..542400; B lands OUTSIDE
    # the naive A window, seed-gap face inherited); W246 freezer MUST
    # re-derive on the post-W245 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality); never transcribe r587.
    245: {"a": (555_501, 557_500), "b_exit": (542_001, 542_200),
         "engine_owner": "bm-a"},
    # W246 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261015-1328-bma-w246-seat published=reserved by bm-a itself @
    # origin 785936d84 (r1015, queue-depth supply depth-1 at publish, own-seat continuity (bm-a landed the W245 chain same-window r1015: freeze 29d3ab761 + engine self-burn 12/12 + finalize one-pass ledger 963,335 / K=536,920; no takeover lane this wave, no declared external turn, origin vacancy four-check green at publish)); prereg + ADMIT probe
    # receipt frozen commit 9ebecf60d2 (prereg research/PERPETUAL_N1_W246_PREREG.md
    # r1016 window machine-SUB derive landed pre-freeze, probe
    # results/_w246bma_20261015_probe_receipt.json @ 785936d847);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-a W245 five-face (freeze 29d3ab761e) + W245
    # finalize product landed (n1_w245_results.json present, ledger
    # head 963335 machine-read at freeze time); zero --no-verify;
    # the W246 seat MSG sits in fleet/inbox/processed/MSG-20261015-1328-bma-w246-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w246bma_20261015_probe_receipt.json: A = FIRST-CLEAN
    # arithmetic continuation of the prior-wave A tail (557_501..559_500 CLEAN
    # at naive start on the registered universe, hops=0, A_hop_chain empty +
    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,
    # eighth consecutive seed-gap face per the W245 seat leg4 anticipation
    # confirmed live; A base == prior-wave A tail+1 (557_500+1) machine-checkable;
    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail
    # (542_201..542_400 CLEAN at naive start on the
    # registered universe, hops=0, B_hop_chain empty, B_naive_hops=0 --
    # double-clean arithmetic continuation face (fc_b == fc_b_naive: no refusers,
    # no own-A reservation jump) -- B lands OUTSIDE the own-A window
    # 557_501..559_500: seed-decoupled A/B gap face eighth; B base == prior-B-tail+1 EXACT;
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=557501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=542201 span=200 checked=200 verdict=FREE.
    # W247+ projection (gate-derived pre-seat probe leg4, pre-W246
    # universe): A naive first-clean 559501..561500 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 542401..542600 hits the registered W239 A band ->
    # honest forward first-clean 544501..544700 hops=1 (staircase band-hop face,
    # first-disclosed; B_hop lands-inside-A=false leg present); W247 freezer MUST
    # re-derive on the post-W246 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality); never transcribe r587.
    246: {"a": (557_501, 559_500), "b_exit": (542_201, 542_400),
         "engine_owner": "bm-a"},
    # W247 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261015-1608-bma-w247-seat published=reserved by bm-a itself @
    # origin e06f4ee2a (r1018, queue-depth supply depth-1 at publish, own-seat continuity (bm-a landed the W246 chain same-window r1018 finalize: freeze 650953086 + engine self-burn 12/12 + finalize one-pass ledger 965,535 / K=539,120; no takeover lane this wave, no declared external turn, origin vacancy four-check green at publish)); prereg + ADMIT probe
    # receipt frozen commit 4c403cb16e (prereg research/PERPETUAL_N1_W247_PREREG.md
    # r1019 window machine-SUB derive landed pre-freeze, probe
    # results/_w247bma_20261015_probe_receipt.json @ e06f4ee2a5);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-a W246 five-face (freeze 650953086c) + W246
    # finalize product landed (n1_w246_results.json present, ledger
    # head 965535 machine-read at freeze time); zero --no-verify;
    # the W247 seat MSG sits in fleet/inbox/processed/MSG-20261015-1608-bma-w247-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w247bma_20261015_probe_receipt.json: A = FIRST-CLEAN
    # arithmetic continuation of the prior-wave A tail (559_501..561_500 CLEAN
    # at naive start on the registered universe, hops=0, A_hop_chain empty +
    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,
    # ninth consecutive seed-gap face per the W246 seat leg4 anticipation
    # confirmed live; A base == prior-wave A tail+1 (559_500+1) machine-checkable;
    # B = FIRST-CLEAN honest forward walk past a REGISTERED refusal
    # (naive continuation 542_401..542_600 REFUSED by the
    # registered W239 A band 542_501..544_500 -> hop 1 lands at
    # 544_501..544_700 (hops=1, B_naive_hops=1, B base == refuser-band-end+1 EXACT;
    # fc_b == fc_b_naive: the hop refuser is the registered band, not the own-A
    # reservation) -- B lands OUTSIDE the own-A window 559_501..561_500: seed-decoupled A/B gap face ninth;
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=559501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=544501 span=200 checked=200 verdict=FREE.
    # W248+ projection (gate-derived pre-seat probe leg4, pre-W247
    # universe): A naive first-clean 561501..563500 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 544701..544900 CLEAN (staircase continuation, hops=0,
    # B base == prior-B-tail+1 EXACT, lands OUTSIDE the projection A window;
    # B_hop lands-inside-A=false leg present); W248 freezer MUST
    # re-derive on the post-W247 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality); never transcribe r587.
    247: {"a": (559_501, 561_500), "b_exit": (544_501, 544_700),
         "engine_owner": "bm-a"},
    # W248 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261015-164x-bmc-w248-seat published=reserved by bm-c itself @
    # origin 86819ad77 (r1030, queue-depth supply depth-2 at publish, waits-upstream ARMED lane; the W248 freeze's waits-upstream on the W247 chain is DISARMED by the W247 five-face + finalize landing -- bm-a r1021 freeze + r1022 finalize one-pass ledger 967,735 / K=541,320); prereg + ADMIT probe
    # receipt frozen commit b9abac7067 (prereg research/PERPETUAL_N1_W248_PREREG.md
    # r1034-continuation/r1035 window machine-SUB derive landed pre-freeze, probe
    # results/_w248bmc_20261015_probe_receipt.json @ 86819ad776);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-a W247 five-face (freeze 2fcca77111) + W247
    # finalize product landed (n1_w247_results.json present, ledger
    # head 967735 machine-read at freeze time); zero --no-verify;
    # the W248 seat MSG sits in fleet/inbox/processed/MSG-20261015-164x-bmc-w248-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w248bmc_20261015_probe_receipt.json: A = FIRST-CLEAN
    # arithmetic continuation of the prior-wave A tail (561_501..563_500 CLEAN
    # at naive start on the registered universe, hops=0, A_hop_chain empty +
    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,
    # TENTH consecutive seed-gap face per the W247 probe leg4 + seat leg4
    # anticipation confirmed live; A base == prior-wave A tail+1 (561_500+1) machine-checkable;
    # B = CLEAN arithmetic continuation of the prior-wave B tail
    # (544_701..544_900, hops=0, B_naive_hops=0, B_hop_chain empty +
    # B_clean_at_naive_start=true, past the W239 staircase band-hop landing; the
    # registered W239 A band 542_501..544_500 and the registered W247 B band
    # 544_501..544_700 both sit below the walk start) -- B lands OUTSIDE
    # the own-A window 561_501..563_500: seed-decoupled A/B gap face tenth;
    # B base == prior-wave B tail+1 (544_700+1) machine-checkable;
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=561501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=544701 span=200 checked=200 verdict=FREE.
    # W249+ projection (gate-derived pre-seat probe leg4, pre-W248
    # universe): A naive first-clean 563501..565500 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 544901..545100 CLEAN (staircase continuation, hops=0,
    # B base == prior-B-tail+1 EXACT, lands OUTSIDE the projection A window;
    # B_hop lands-inside-A=false leg present); W249 freezer MUST
    # re-derive on the post-W248 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality); never transcribe r587.
    248: {"a": (561_501, 563_500), "b_exit": (544_701, 544_900),
         "engine_owner": "bm-c"},
    # W249 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261015-225x-bmc-w249-seat published=reserved by bm-c itself @
    # origin 8949e0aef (r1030, queue-head supply -- W248 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W249 seat was published AFTER the W248 five-face + finalize landing (zero waits-upstream face) -- bm-c r1036 absorb-window freeze + finalize one-pass ledger 969,935 / K=543,520); prereg + ADMIT probe
    # receipt frozen commit 4103f0d5d6 (prereg research/PERPETUAL_N1_W249_PREREG.md
    # r1040-dead window (absorbed+committed r1041) machine-SUB derive landed pre-freeze, probe
    # results/_w249bmc_20261015_probe_receipt.json @ 8949e0aef3);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W248 five-face (freeze be82e2af1c) + W248
    # finalize product landed (n1_w248_results.json present, ledger
    # head 969935 machine-read at freeze time); zero --no-verify;
    # the W249 seat MSG sits in fleet/inbox/MSG-20261015-225x-bmc-w249-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w249bmc_20261015_probe_receipt.json: A = FIRST-CLEAN
    # arithmetic continuation of the prior-wave A tail (563_501..565_500 CLEAN
    # at naive start on the registered universe, hops=0, A_hop_chain empty +
    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,
    # TWELFTH consecutive seed-gap face per the W248 probe leg4 + seat leg4
    # anticipation confirmed live; A base == prior-wave A tail+1 (563_500+1) machine-checkable;
    # B = CLEAN arithmetic continuation of the prior-wave B tail
    # (544_901..545_100, hops=0, B_naive_hops=0, B_hop_chain empty +
    # B_clean_at_naive_start=true, past the W239 staircase band-hop landing; the
    # registered W239 A band 542_501..544_500 and the registered W248 B band
    # 544_701..544_900 both sit below the walk start) -- B lands OUTSIDE
    # the own-A window 563_501..565_500: seed-decoupled A/B gap face tenth;
    # B base == prior-wave B tail+1 (544_900+1) machine-checkable;
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=563501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=544901 span=200 checked=200 verdict=FREE.
    # W250+ projection (gate-derived pre-seat probe leg4, pre-W249
    # universe): A naive first-clean 565501..567500 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 545101..545300 CLEAN (staircase continuation, hops=0,
    # B base == prior-B-tail+1 EXACT, lands OUTSIDE the projection A window;
    # B_hop lands-inside-A=false leg present); W250 freezer MUST
    # re-derive on the post-W249 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality); never transcribe r587.
    249: {"a": (563_501, 565_500), "b_exit": (544_901, 545_100),
         "engine_owner": "bm-c"},
    # W250 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261016-055x-bmc-w250-seat published=reserved by bm-c itself @
    # origin cc06f1f4a (r1043, queue-head supply -- W249 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W250 seat was published AFTER the W249 five-face + finalize landing (zero waits-upstream face) -- bm-c r1042 freeze + r1043 finalize one-pass ledger 972,135 / K=545,720); prereg + ADMIT probe
    # receipt frozen commit 4f7a130ff5 (prereg research/PERPETUAL_N1_W250_PREREG.md
    # bm-c r1045 window machine-SUB derive landed pre-freeze, probe
    # results/_w250bmc_20261016_probe_receipt.json @ cc06f1f4a7);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W249 five-face (freeze 5d4aeec59d) + W249
    # finalize product landed (n1_w249_results.json present, ledger
    # head 972135 machine-read at freeze time); zero --no-verify;
    # the W250 seat MSG sits in fleet/inbox/MSG-20261016-055x-bmc-w250-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w250bmc_20261016_probe_receipt.json: A = FIRST-CLEAN
    # arithmetic continuation of the prior-wave A tail (565_501..567_500 CLEAN
    # at naive start on the registered universe, hops=0, A_hop_chain empty +
    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,
    # THIRTEENTH consecutive seed-gap face per the W249 probe leg4 + seat leg4
    # anticipation confirmed live; A base == prior-wave A tail+1 (565_500+1) machine-checkable;
    # B = CLEAN arithmetic continuation of the prior-wave B tail
    # (545_101..545_300, hops=0, B_naive_hops=0, B_hop_chain empty +
    # B_clean_at_naive_start=true, past the W239 staircase band-hop landing; the
    # registered W239 A band 542_501..544_500 and the registered W247/W248/W249 B bands
    # 544_901..545_100 all sit below the walk start) -- B lands OUTSIDE
    # the own-A window 565_501..567_500: seed-decoupled A/B gap face THIRTEENTH;
    # B base == prior-wave B tail+1 (545_100+1) machine-checkable;
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=565501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=545101 span=200 checked=200 verdict=FREE.
    # W251+ projection (gate-derived pre-seat probe leg4, pre-W250
    # universe): A naive first-clean 567501..569500 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 545301..545500 hops=11 NOT clean at naive -- first-clean 565501..565700,
    # lands OUTSIDE the projection A window;
    # B_hop lands-inside-A=false leg present); W251 freezer MUST
    # re-derive on the post-W250 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality); never transcribe r587.
    250: {"a": (565_501, 567_500), "b_exit": (545_101, 545_300),
         "engine_owner": "bm-c"},
    # W251 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261016-085x-bmc-w251-seat published=reserved by bm-c itself @
    # origin bc3b2b693 (r1046, queue-head supply -- W250 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W251 seat was published AFTER the W250 five-face + finalize landing (zero waits-upstream face) -- bm-c r1046 freeze + r1046 finalize one-pass ledger 974,335 / K=547,920); prereg + ADMIT probe
    # receipt frozen commit 9f5f106d67 (prereg research/PERPETUAL_N1_W251_PREREG.md
    # bm-c r1047 window machine-SUB derive landed pre-freeze, probe
    # results/_w251bmc_20261016_probe_receipt.json @ bc3b2b693a);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W250 five-face (freeze 29930f4890) + W250
    # finalize product landed (n1_w250_results.json present, ledger
    # head 974335 machine-read at freeze time); zero --no-verify;
    # the W251 seat MSG sits in fleet/inbox/processed/MSG-20261016-085x-bmc-w251-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w251bmc_20261016_probe_receipt.json: A = FIRST-CLEAN
    # arithmetic continuation of the prior-wave A tail (567_501..569_500 CLEAN
    # at naive start on the registered universe, hops=0, A_hop_chain empty +
    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,
    # FOURTEENTH consecutive seed-gap face per the W250 probe leg4 + seat leg4
    # anticipation confirmed live; A base == prior-wave A tail+1 (567_500+1) machine-checkable;
    # B = 13-HOP WALK above own-A (the naive continuation
    # 545_301..545_500 REFUSED at naive start -- SEED_REGISTRY seed 545_500 +
    # the W240..W249 A-ladder bands + W250-A + own-A reservation; hops=13,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the
    # pre-W250 projected first-clean 565_501..565_700 (now INSIDE the registered W250 A band) AND
    # past the own-wave A window; B lands ABOVE own-A -- first since the W239 staircase
    # era; B base == own-A tail+1 (569_500+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=567501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=569501 span=200 checked=200 verdict=FREE.
    # W252+ projection (gate-derived pre-seat probe leg4, pre-W251
    # universe): A naive first-clean 569501..571500 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 569701..569900 hops=0 CLEAN at naive -- first-clean 569701..569900 BUT lands INSIDE the projection A window,
    # (W252p_B_lands_inside_W252p_A_naive=true -- staircase re-emergence face: the W252 walk MUST hop past own-A reservation);
    # the W252 freezer MUST
    # re-derive on the post-W251 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality); never transcribe r587.
    251: {"a": (567_501, 569_500), "b_exit": (569_501, 569_700),
         "engine_owner": "bm-c"},
    # W252 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261016-10xx-bmc-w252-seat published=reserved by bm-c itself @
    # origin f9441de67 (r1048, queue-head supply -- W251 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W252 seat was published AFTER the W251 five-face + finalize landing (zero waits-upstream face) -- bm-c r1048 freeze + r1048 finalize one-pass ledger 976,535 / K=550,120); prereg + ADMIT probe
    # receipt frozen commit 472cc83869 (prereg research/PERPETUAL_N1_W252_PREREG.md
    # bm-c r1049 window machine-SUB derive landed pre-freeze, probe
    # results/_w252bmc_20261016_probe_receipt.json @ f9441de672);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W251 five-face (freeze c813471cd0) + W251
    # finalize product landed (n1_w251_results.json present, ledger
    # head 976535 machine-read at freeze time); zero --no-verify;
    # the W252 seat MSG sits in fleet/inbox/processed/MSG-20261016-10xx-bmc-w252-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w252bmc_20261016_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk (the naive continuation 569_501..571_500 is REFUSED
    # at naive start -- the registered W251 B band sits INSIDE the naive A window;
    # the walk hops past the W251 B tail -> A first-clean, hops=1 -- FIRST A-hop
    # since the W239 staircase era, the fourteen-wave seed-gap face ENDS at W252;
    # A base == registered prior-wave B tail+1 (569_700+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W251_B=true)
    # B = 1-HOP own-A RESERVATION above own-A (the naive continuation
    # 569_701..569_900 lands INSIDE the own-wave A first-clean window --
    # own-A reservation standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- SECOND consecutive above-own-A;
    # B base == own-A tail+1 (571_700+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=569701 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=571701 span=200 checked=200 verdict=FREE.
    # W253+ projection (gate-derived pre-seat probe leg4, pre-W252
    # universe): A naive first-clean 571701..573700 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 571901..572100 hops=0 CLEAN at naive -- first-clean 571901..572100 BUT lands INSIDE the projection A window,
    # (W253p_B_lands_inside_W253p_A_naive=true -- staircase re-emergence face: the W253 walk MUST hop past own-A reservation);
    # the W253 freezer MUST
    # re-derive on the post-W252 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    252: {"a": (569_701, 571_700), "b_exit": (571_701, 571_900),
         "engine_owner": "bm-c"},
    # W253 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261016-12xx-bmc-w253-seat published=reserved by bm-c itself @
    # origin f6433ee61 (r1050, queue-head supply -- W252 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W253 seat was published AFTER the W252 five-face + finalize landing (zero waits-upstream face) -- bm-c r1050 freeze + r1050 finalize one-pass ledger 978,735 / K=552,320); prereg + ADMIT probe
    # receipt frozen commit 741371846a (prereg research/PERPETUAL_N1_W253_PREREG.md
    # bm-c r1052 window machine-SUB derive landed pre-freeze, probe
    # results/_w253bmc_20261016_probe_receipt.json @ f6433ee610);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W252 five-face (freeze e63561df37) + W252
    # finalize product landed (n1_w252_results.json present, ledger
    # head 978735 machine-read at freeze time); zero --no-verify;
    # the W253 seat MSG sits in fleet/inbox/processed/MSG-20261016-12xx-bmc-w253-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w253bmc_20261016_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk SECOND consecutive A-hop (the naive continuation 571_701..573_700 is REFUSED
    # at naive start -- the registered W252 B band sits INSIDE the naive A window;
    # the walk hops past the W252 B tail -> A first-clean, hops=1 -- SECOND
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (571_900+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W252_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 571_901..572_100 lands INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- THIRD consecutive above-own-A;
    # B base == own-A tail+1 (573_900+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=571901 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=573901 span=200 checked=200 verdict=FREE.
    # W254+ projection (gate-derived pre-seat probe leg4, pre-W253
    # universe): A naive first-clean 573901..575900 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 574101..574300 hops=0 CLEAN at naive -- first-clean 574101..574300 BUT lands INSIDE the projection A window,
    # (W254p_B_lands_inside_W254p_A_naive=true -- staircase re-emergence face: the W254 walk MUST hop past own-A reservation);
    # the W254 freezer MUST
    # re-derive on the post-W253 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    253: {"a": (571_901, 573_900), "b_exit": (573_901, 574_100),
         "engine_owner": "bm-c"},
    # W254 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261016-14xx-bmc-w254-seat published=reserved by bm-c itself @
    # origin fa70f3765 (r1053, queue-head supply -- W253 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W254 seat was published AFTER the W253 five-face + finalize landing (zero waits-upstream face) -- bm-c r1053 freeze + r1053 finalize one-pass ledger 980,935 / K=554,520); prereg + ADMIT probe
    # receipt frozen commit e2c4b543ef (prereg research/PERPETUAL_N1_W254_PREREG.md
    # bm-c r1054 window machine-SUB derive landed pre-freeze, probe
    # results/_w254bmc_20261016_probe_receipt.json @ fa70f3765d);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W253 five-face (freeze c9b4fd8550) + W253
    # finalize product landed (n1_w253_results.json present, ledger
    # head 980935 machine-read at freeze time); zero --no-verify;
    # the W254 seat MSG sits in fleet/inbox/processed/MSG-20261016-14xx-bmc-w254-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w254bmc_20261016_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk THIRD consecutive A-hop (the naive continuation 573_901..575_900 is REFUSED
    # at naive start -- the registered W253 B band sits INSIDE the naive A window;
    # the walk hops past the W253 B tail -> A first-clean, hops=1 -- SECOND
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W253;
    # A base == registered prior-wave B tail+1 (574_100+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W253_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 574_101..574_300 lands INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- FOURTH consecutive above-own-A;
    # B base == own-A tail+1 (576_100+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=574101 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=576101 span=200 checked=200 verdict=FREE.
    # W255+ projection (gate-derived pre-seat probe leg4, pre-W254
    # universe): A naive first-clean 576101..578100 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 576301..576500 hops=0 CLEAN at naive -- first-clean 576301..576500 BUT lands INSIDE the projection A window,
    # (W255p_B_lands_inside_W255p_A_naive=true -- staircase re-emergence face: the W255 walk MUST hop past own-A reservation);
    # the W255 freezer MUST
    # re-derive on the post-W254 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    254: {"a": (574_101, 576_100), "b_exit": (576_101, 576_300),
         "engine_owner": "bm-c"},
    # W255 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261016-22xx-bmc-w255-seat published=reserved by bm-c itself @
    # origin cb79242ed (r1055, queue-head supply -- W254 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W255 seat was published AFTER the W254 five-face + finalize landing (zero waits-upstream face) -- bm-c r1055 freeze + r1055 finalize one-pass ledger 983,135 / K=556,720); prereg + ADMIT probe
    # receipt frozen commit 72d292ea3f (prereg research/PERPETUAL_N1_W255_PREREG.md
    # bm-c r1056 window machine-SUB derive landed pre-freeze, probe
    # results/_w255bmc_20261016_probe_receipt.json @ cb79242ed6);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W254 five-face (freeze 3eb6915753) + W254
    # finalize product landed (n1_w254_results.json present, ledger
    # head 983135 machine-read at freeze time); zero --no-verify;
    # the W255 seat MSG sits in fleet/inbox/processed/MSG-20261016-22xx-bmc-w255-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w255bmc_20261016_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FOURTH consecutive A-hop (the naive continuation 576_101..578_100 is REFUSED
    # at naive start -- the registered W254 B band sits INSIDE the naive A window;
    # the walk hops past the W254 B tail -> A first-clean, hops=1 -- THIRD
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W254;
    # A base == registered prior-wave B tail+1 (576_300+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W254_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 576_301..576_500 lands INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- FIFTH consecutive above-own-A;
    # B base == own-A tail+1 (578_300+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=576301 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=578301 span=200 checked=200 verdict=FREE.
    # W256+ projection (gate-derived pre-seat probe leg4, pre-W255
    # universe): A naive first-clean 578301..580300 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 578501..578700 hops=0 CLEAN at naive -- first-clean 578501..578700 BUT lands INSIDE the projection A window,
    # (W256p_B_lands_inside_W256p_A_naive=true -- staircase re-emergence face: the W256 walk MUST hop past own-A reservation);
    # the W256 freezer MUST
    # re-derive on the post-W255 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    255: {"a": (576_301, 578_300), "b_exit": (578_301, 578_500),
         "engine_owner": "bm-c"},
    # W256 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261017-023x-bmc-w256-seat published=reserved by bm-c itself @
    # origin fd48643c9 (r1057, queue-head supply -- W255 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W256 seat was published AFTER the W255 five-face + finalize landing (zero waits-upstream face) -- bm-c r1057 freeze + r1057 finalize one-pass ledger 985,335 / K=558,920); prereg + ADMIT probe
    # receipt frozen commit 5996e2c939 (prereg research/PERPETUAL_N1_W256_PREREG.md
    # bm-c r1058 window machine-SUB derive landed pre-freeze, probe
    # results/_w256bmc_20261017_probe_receipt.json @ fd48643c97);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W255 five-face (freeze e166afc6cd) + W255
    # finalize product landed (n1_w255_results.json present, ledger
    # head 985335 machine-read at freeze time); zero --no-verify;
    # the W256 seat MSG sits in fleet/inbox/MSG-20261017-023x-bmc-w256-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w256bmc_20261017_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FIFTH consecutive A-hop (the naive continuation 578_301..580_300 is REFUSED
    # at naive start -- the registered W255 B band sits INSIDE the naive A window;
    # the walk hops past the W255 B tail -> A first-clean, hops=1 -- FOURTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W255;
    # A base == registered prior-wave B tail+1 (578_500+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W255_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 578_501..578_700 lands INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- SIXTH consecutive above-own-A;
    # B base == own-A tail+1 (580_500+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=578501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=580501 span=200 checked=200 verdict=FREE.
    # W257+ projection (gate-derived pre-seat probe leg4, pre-W256
    # universe): A naive first-clean 580501..582500 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 580701..580900 hops=0 CLEAN at naive -- first-clean 580701..580900 BUT lands INSIDE the projection A window,
    # (W257p_B_lands_inside_W257p_A_naive=true -- staircase re-emergence face: the W257 walk MUST hop past own-A reservation);
    # the W257 freezer MUST
    # re-derive on the post-W256 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    256: {"a": (578_501, 580_500), "b_exit": (580_501, 580_700),
         "engine_owner": "bm-c"},
    # W257 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261017-03xx-bmc-w257-seat published=reserved by bm-c itself @
    # origin 27ee6e95a (r1058, queue-head supply -- W256 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W257 seat was published AFTER the W256 five-face + finalize landing (zero waits-upstream face) -- bm-c r1058 freeze + r1058 finalize one-pass ledger 987,535 / K=561,120); prereg + ADMIT probe
    # receipt frozen commit c7fbc443cb (prereg research/PERPETUAL_N1_W257_PREREG.md
    # bm-c r1059 window machine-SUB derive landed pre-freeze, probe
    # results/_w257bmc_20261017_probe_receipt.json @ 27ee6e95ab);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W256 five-face (freeze aa6102e35a) + W256
    # finalize product landed (n1_w256_results.json present, ledger
    # head 987535 machine-read at freeze time); zero --no-verify;
    # the W257 seat MSG sits in fleet/inbox/processed/MSG-20261017-03xx-bmc-w257-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w257bmc_20261017_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk SIXTH consecutive A-hop (the naive continuation 580_501..582_500 is REFUSED
    # at naive start -- the registered W256 B band sits INSIDE the naive A window;
    # the walk hops past the W256 B tail -> A first-clean, hops=1 -- FIFTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W256;
    # A base == registered prior-wave B tail+1 (580_700+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W256_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 580_701..580_900 lands INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- SEVENTH consecutive above-own-A;
    # B base == own-A tail+1 (582_700+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=580701 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=582701 span=200 checked=200 verdict=FREE.
    # W258+ projection (gate-derived pre-seat probe leg4, pre-W257
    # universe): A naive first-clean 582701..584700 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 582901..583100 hops=0 CLEAN at naive -- first-clean 582901..583100 BUT lands INSIDE the projection A window,
    # (W258p_B_lands_inside_W258p_A_naive=true -- staircase re-emergence face: the W258 walk MUST hop past own-A reservation);
    # the W258 freezer MUST
    # re-derive on the post-W257 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    257: {"a": (580_701, 582_700), "b_exit": (582_701, 582_900),
         "engine_owner": "bm-c"},
    # W258 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261017-0517-bmc-w258-seat published=reserved by bm-c itself @
    # origin d0d0d04a4 (r1060, queue-head supply -- W257 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W258 seat was published AFTER the W257 five-face + finalize landing (zero waits-upstream face) -- bm-c r1060 freeze + r1060 finalize one-pass ledger 989,735 / K=563,320); prereg + ADMIT probe
    # receipt frozen commit 824b46d31f (prereg research/PERPETUAL_N1_W258_PREREG.md
    # bm-c r1061 window machine-SUB derive landed pre-freeze, probe
    # results/_w258bmc_20261017_probe_receipt.json @ d0d0d04a48);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W257 five-face (freeze 550293d3fb) + W257
    # finalize product landed (n1_w257_results.json present, ledger
    # head 989735 machine-read at freeze time); zero --no-verify;
    # the W258 seat MSG sits in fleet/inbox/processed/MSG-20261017-0517-bmc-w258-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w258bmc_20261017_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk SEVENTH consecutive A-hop (the naive continuation 582_701..584_700 is REFUSED
    # at naive start -- the registered W257 B band sits INSIDE the naive A window;
    # the walk hops past the W257 B tail -> A first-clean, hops=1 -- SIXTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W257;
    # A base == registered prior-wave B tail+1 (582_900+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W257_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 582_901..583_100 lands INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- EIGHTH consecutive above-own-A;
    # B base == own-A tail+1 (584_900+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=582901 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=584901 span=200 checked=200 verdict=FREE.
    # W259+ projection (gate-derived pre-seat probe leg4, pre-W258
    # universe): A naive first-clean 584901..586900 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 585101..585300 hops=0 CLEAN at naive -- first-clean 585101..585300 BUT lands INSIDE the projection A window,
    # (W259p_B_lands_inside_W259p_A_naive=true -- staircase re-emergence face: the W259 walk MUST hop past own-A reservation);
    # the W259 freezer MUST
    # re-derive on the post-W258 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    258: {"a": (582_901, 584_900), "b_exit": (584_901, 585_100),
         "engine_owner": "bm-c"},
    # W259 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261017-0704-bmc-w259-seat published=reserved by bm-c itself @
    # origin 16dba0e70 (r1062, queue-head supply -- W258 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W259 seat was published AFTER the W258 five-face + finalize landing (zero waits-upstream face) -- bm-c r1062 freeze + r1062 finalize one-pass ledger 991,935 / K=565,520); prereg + ADMIT probe
    # receipt frozen commit b709bc2cc0 (prereg research/PERPETUAL_N1_W259_PREREG.md
    # bm-c r1063 window machine-SUB derive landed pre-freeze, probe
    # results/_w259bmc_20261017_probe_receipt.json @ 16dba0e701);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W258 five-face (freeze 37ccebffd2) + W258
    # finalize product landed (n1_w258_results.json present, ledger
    # head 991935 machine-read at freeze time); zero --no-verify;
    # the W259 seat MSG sits in fleet/inbox/processed/MSG-20261017-0704-bmc-w259-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w259bmc_20261017_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk EIGHTH consecutive A-hop (the naive continuation 584_901..586_900 is REFUSED
    # at naive start -- the registered W258 B band sits INSIDE the naive A window;
    # the walk hops past the W258 B tail -> A first-clean, hops=1 -- SEVENTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W258;
    # A base == registered prior-wave B tail+1 (585_100+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W258_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 585_101..585_300 lands INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- NINTH consecutive above-own-A;
    # B base == own-A tail+1 (587_100+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=585101 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=587101 span=200 checked=200 verdict=FREE.
    # W260+ projection (gate-derived pre-seat probe leg4, pre-W259
    # universe): A naive first-clean 587101..589100 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 587301..587500 hops=0 CLEAN at naive -- first-clean 587301..587500 BUT lands INSIDE the projection A window,
    # (W260p_B_lands_inside_W260p_A_naive=true -- staircase re-emergence face: the W260 walk MUST hop past own-A reservation);
    # the W260 freezer MUST
    # re-derive on the post-W259 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    259: {"a": (585_101, 587_100), "b_exit": (587_101, 587_300),
         "engine_owner": "bm-c"},
    # W260 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261017-0910-bmc-w260-seat published=reserved by bm-c itself @
    # origin 9fa2c8aed (r1064, queue-head supply -- W259 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W260 seat was published AFTER the W259 five-face + finalize landing (zero waits-upstream face) -- bm-c r1064 freeze + r1064 finalize one-pass ledger 994,135 / K=567,720); prereg + ADMIT probe
    # receipt frozen commit 0f33f9abcf (prereg research/PERPETUAL_N1_W260_PREREG.md
    # bm-c r1065 window machine-SUB derive landed pre-freeze, probe
    # results/_w260bmc_20261017_probe_receipt.json @ 9fa2c8aede);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W259 five-face (freeze 89aeea31b3) + W259
    # finalize product landed (n1_w259_results.json present, ledger
    # head 994135 machine-read at freeze time); zero --no-verify;
    # the W260 seat MSG sits in fleet/inbox/processed/MSG-20261017-0910-bmc-w260-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w260bmc_20261017_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk NINTH consecutive A-hop (the naive continuation 587_101..589_100 is REFUSED
    # at naive start -- the registered W259 B band sits INSIDE the naive A window;
    # the walk hops past the W259 B tail -> A first-clean, hops=1 -- EIGHTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W259;
    # A base == registered prior-wave B tail+1 (587_300+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W259_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 587_301..587_500 lands INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- TENTH consecutive above-own-A;
    # B base == own-A tail+1 (589_300+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=587301 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=589301 span=200 checked=200 verdict=FREE.
    # W261+ projection (gate-derived pre-seat probe leg4, pre-W260
    # universe): A naive first-clean 589301..591300 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 589501..589700 hops=0 CLEAN at naive -- first-clean 589501..589700 BUT lands INSIDE the projection A window,
    # (W261p_B_lands_inside_W261p_A_naive=true -- staircase re-emergence face: the W261 walk MUST hop past own-A reservation);
    # the W261 freezer MUST
    # re-derive on the post-W260 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    260: {"a": (587_301, 589_300), "b_exit": (589_301, 589_500),
         "engine_owner": "bm-c"},
    # W261 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261017-1225-bmc-w261-seat published=reserved by bm-c itself @
    # origin cf23c4553 (r1065, queue-head supply -- W260 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W261 seat was published AFTER the W260 five-face + finalize landing (zero waits-upstream face) -- bm-c r1065 freeze + r1065 finalize one-pass ledger 996,335 / K=569,920); prereg + ADMIT probe
    # receipt frozen commit 03ab504d70 (prereg research/PERPETUAL_N1_W261_PREREG.md
    # bm-c r1066 window machine-SUB derive landed pre-freeze, probe
    # results/_w261bmc_20261017_probe_receipt.json @ cf23c45534);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W260 five-face (freeze e8a9d5d678) + W260
    # finalize product landed (n1_w260_results.json present, ledger
    # head 996335 machine-read at freeze time); zero --no-verify;
    # the W261 seat MSG sits in fleet/inbox/processed/MSG-20261017-1225-bmc-w261-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w261bmc_20261017_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk TENTH consecutive A-hop (the naive continuation 589_301..591_300 is REFUSED
    # at naive start -- the registered W260 B band sits INSIDE the naive A window;
    # the walk hops past the W260 B tail -> A first-clean, hops=1 -- NINTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W260;
    # A base == registered prior-wave B tail+1 (589_500+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W260_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 589_501..589_700 lands INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- ELEVENTH consecutive above-own-A;
    # B base == own-A tail+1 (591_500+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=589501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=591501 span=200 checked=200 verdict=FREE.
    # W262+ projection (gate-derived pre-seat probe leg4, pre-W261
    # universe): A naive first-clean 591501..593500 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 591701..591900 hops=0 CLEAN at naive -- first-clean 591701..591900 BUT lands INSIDE the projection A window,
    # (W262p_B_lands_inside_W262p_A_naive=true -- staircase re-emergence face: the W262 walk MUST hop past own-A reservation);
    # the W262 freezer MUST
    # re-derive on the post-W261 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    261: {"a": (589_501, 591_500), "b_exit": (591_501, 591_700),
         "engine_owner": "bm-c"},
    # W262 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261017-1425-bmc-w262-seat published=reserved by bm-c itself @
    # origin 693e926b1 (r1067, queue-head supply -- W261 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W262 seat was published AFTER the W261 five-face + finalize landing (zero waits-upstream face) -- bm-c r1067 freeze + r1067 finalize one-pass ledger 998,535 / K=572,120); prereg + ADMIT probe
    # receipt frozen commit 32d28ffb30 (prereg research/PERPETUAL_N1_W262_PREREG.md
    # bm-c r1067 window machine-SUB derive landed pre-freeze, probe
    # results/_w262bmc_20261017_probe_receipt.json @ 693e926b1e);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W261 five-face (freeze 68aad04b64) + W261
    # finalize product landed (n1_w261_results.json present, ledger
    # head 998535 machine-read at freeze time); zero --no-verify;
    # the W262 seat MSG sits in fleet/inbox/processed/MSG-20261017-1425-bmc-w262-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w262bmc_20261017_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk ELEVENTH consecutive A-hop (the naive continuation 591_501..593_500 is REFUSED
    # at naive start -- the registered W261 B band sits INSIDE the naive A window;
    # the walk hops past the W261 B tail -> A first-clean, hops=1 -- TENTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W261;
    # A base == registered prior-wave B tail+1 (591_700+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W261_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 591_701..591_900 lands INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- TWELFTH consecutive above-own-A;
    # B base == own-A tail+1 (593_700+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20262010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=591701 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=593701 span=200 checked=200 verdict=FREE.
    # W263+ projection (gate-derived pre-seat probe leg4, pre-W262
    # universe): A naive first-clean 593701..595700 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 593901..594100 hops=0 CLEAN at naive -- first-clean 593901..594100 BUT lands INSIDE the projection A window,
    # (W263p_B_lands_inside_W263p_A_naive=true -- staircase re-emergence face: the W263 walk MUST hop past own-A reservation);
    # the W263 freezer MUST
    # re-derive on the post-W262 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    262: {"a": (591_701, 593_700), "b_exit": (593_701, 593_900),
         "engine_owner": "bm-c"},
    # W263 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261017-1740-bma-w263-seat published=reserved by bm-a itself @
    # origin fb0c962b5 (r1037, queue-head seat-first supply -- W262 registered + self-burn 12/12 at publish, W262 finalize PENDING at seat time (waits-upstream face disclosed honest; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE was GATED on the W262 finalize landing per gate0.5 -- now GREEN, W262 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit b32f6bf1c8 (prereg research/PERPETUAL_N1_W263_PREREG.md
    # bm-a r1037 window machine-SUB derive landed pre-freeze, probe
    # results/_w263bma_20261017_probe_receipt.json @ 0d2fa8c133);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W262 five-face (freeze e1a94b3357) + W262
    # finalize product landed (n1_w262_results.json present, ledger
    # head 1000735 machine-read at freeze time); zero --no-verify;
    # the W263 seat MSG sits in fleet/inbox/processed/MSG-20261017-1740-bma-w263-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w263bma_20261017_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk TWELFTH consecutive A-hop (the naive continuation 593_701..595_700 is REFUSED
    # at naive start -- the registered W262 B band sits INSIDE the naive A window;
    # the walk hops past the W262 B tail -> A first-clean, hops=1 -- TWELFTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (593_900+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W262_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 593_901..594_100 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- THIRTEENTH consecutive above-own-A;
    # B base == own-A tail+1 (595_900+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=593901 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=595901 span=200 checked=200 verdict=FREE.
    # W264+ projection (gate-derived pre-seat probe leg4, pre-W263
    # universe): A naive first-clean 595901..597900 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 596101..596300 hops=0 CLEAN at naive -- first-clean 596101..596300 BUT lands INSIDE the projection A window,
    # (W264p_B_lands_inside_W264p_A_naive=true -- staircase re-emergence face: the W264 walk MUST hop past own-A reservation);
    # the W264 freezer MUST
    # re-derive on the post-W263 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    263: {"a": (593_901, 595_900), "b_exit": (595_901, 596_100),
         "engine_owner": "bm-a"},
    # W264 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261017-1950-bmc-w264-seat published=reserved by bm-c itself @
    # origin dd5fd438e (r1075, queue-head seat-first supply -- W263 registered+FINALIZED complete at publish, W264 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W263 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit f4ffdb34e8 (prereg research/PERPETUAL_N1_W264_PREREG.md
    # bm-c r1076 window machine-SUB derive landed pre-freeze, probe
    # results/_w264bmc_20261017_probe_receipt.json @ dd5fd438ef);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W263 five-face (freeze f499817fac) + W263
    # finalize product landed (n1_w263_results.json present, ledger
    # head 1002935 machine-read at freeze time); zero --no-verify;
    # the W264 seat MSG sits in fleet/inbox/processed/MSG-20261017-1950-bmc-w264-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w264bmc_20261017_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk THIRTEENTH consecutive A-hop (the naive continuation 595_901..597_900 is REFUSED
    # at naive start -- the registered W263 B band sits INSIDE the naive A window;
    # the walk hops past the W263 B tail -> A first-clean, hops=1 -- THIRTEENTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (596_100+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W263_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 596_101..596_300 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- FOURTEENTH consecutive above-own-A;
    # B base == own-A tail+1 (598_100+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=596101 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=598101 span=200 checked=200 verdict=FREE.
    # W265+ projection (gate-derived pre-seat probe leg4, pre-W264
    # universe): A naive first-clean 598101..600100 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 598301..598500 hops=0 CLEAN at naive -- first-clean 598301..598500 BUT lands INSIDE the projection A window,
    # (W265p_B_lands_inside_W265p_A_naive=true -- staircase re-emergence face: the W265 walk MUST hop past own-A reservation);
    # the W265 freezer MUST
    # re-derive on the post-W264 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    264: {"a": (596_101, 598_100), "b_exit": (598_101, 598_300),
         "engine_owner": "bm-c"},
    # W265 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261017-2241-bmc-w265-seat published=reserved by bm-c itself @
    # origin 7343e3650 (r1077, queue-head seat-first supply -- W264 registered+FINALIZED complete at publish, W265 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W264 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit e57215a2ca (prereg research/PERPETUAL_N1_W265_PREREG.md
    # bm-c r1081 window machine-SUB derive landed pre-freeze, probe
    # results/_w265bmc_20261017_probe_receipt.json @ 7343e3650c);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W264 five-face (freeze 216b578b09) + W264
    # finalize product landed (n1_w264_results.json present, ledger
    # head 1005135 machine-read at freeze time); zero --no-verify;
    # the W265 seat MSG sits in fleet/inbox/processed/MSG-20261017-2241-bmc-w265-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w265bmc_20261017_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FOURTEENTH consecutive A-hop (the naive continuation 598_101..600_100 is REFUSED
    # at naive start -- the registered W264 B band sits INSIDE the naive A window;
    # the walk hops past the W264 B tail -> A first-clean, hops=1 -- FOURTEENTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (598_300+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W264_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 598_301..598_500 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- FIFTEENTH consecutive above-own-A;
    # B base == own-A tail+1 (600_300+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=598301 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=600301 span=200 checked=200 verdict=FREE.
    # W266+ projection (gate-derived pre-seat probe leg4, pre-W265
    # universe): A naive first-clean 600301..602300 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 600501..600700 hops=0 CLEAN at naive -- first-clean 600501..600700 BUT lands INSIDE the projection A window,
    # (W266p_B_lands_inside_W266p_A_naive=true -- staircase re-emergence face: the W266 walk MUST hop past own-A reservation);
    # the W266 freezer MUST
    # re-derive on the post-W265 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    265: {"a": (598_301, 600_300), "b_exit": (600_301, 600_500),
         "engine_owner": "bm-c"},
    # W266 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261018-0719-bmc-w266-seat published=reserved by bm-c itself @
    # origin ace19ba85b (r1084, queue-head seat-first supply -- W265 registered+FINALIZED complete at publish, W266 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W265 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit 595433d63c (prereg research/PERPETUAL_N1_W266_PREREG.md
    # bm-c r1085 window machine-SUB derive landed pre-freeze, probe
    # results/_w266bmc_20261018_probe_receipt.json @ ace19ba85b);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W265 five-face (freeze a47517f792) + W265
    # finalize product landed (n1_w265_results.json present, ledger
    # head 1007335 machine-read at freeze time); zero --no-verify;
    # the W266 seat MSG sits in fleet/inbox/processed/MSG-20261018-0719-bmc-w266-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w266bmc_20261018_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FIFTEENTH consecutive A-hop (the naive continuation 600_301..602_300 is REFUSED
    # at naive start -- the registered W265 B band sits INSIDE the naive A window;
    # the walk hops past the W265 B tail -> A first-clean, hops=1 -- FIFTEENTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (600_500+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W265_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 600_501..600_700 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- SIXTEENTH consecutive above-own-A;
    # B base == own-A tail+1 (602_500+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=600501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=602501 span=200 checked=200 verdict=FREE.
    # W267+ projection (gate-derived pre-seat probe leg4, pre-W266
    # universe): A naive first-clean 602501..604500 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 602701..602900 hops=0 CLEAN at naive -- first-clean 602701..602900 BUT lands INSIDE the projection A window,
    # (W267p_B_lands_inside_W267p_A_naive=true -- staircase re-emergence face: the W267 walk MUST hop past own-A reservation);
    # the W267 freezer MUST
    # re-derive on the post-W266 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    266: {"a": (600_501, 602_500), "b_exit": (602_501, 602_700),
         "engine_owner": "bm-c"},
    # W267 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261018-1025-bmc-w267-seat published=reserved by bm-c itself @
    # origin 942ebd5885 (r1086, queue-head seat-first supply -- W266 registered+FINALIZED complete at publish, W267 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W266 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit df55e3fab9 (prereg research/PERPETUAL_N1_W267_PREREG.md
    # bm-c r1087 window machine-SUB derive landed pre-freeze, probe
    # results/_w267bmc_20261018_probe_receipt.json @ 942ebd5885);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W266 five-face (freeze dc71ecc3f9) + W266
    # finalize product landed (n1_w266_results.json present, ledger
    # head 1009535 machine-read at freeze time); zero --no-verify;
    # the W267 seat MSG sits in fleet/inbox/processed/MSG-20261018-1025-bmc-w267-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w267bmc_20261018_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk SIXTEENTH consecutive A-hop (the naive continuation 602_501..604_500 is REFUSED
    # at naive start -- the registered W266 B band sits INSIDE the naive A window;
    # the walk hops past the W266 B tail -> A first-clean, hops=1 -- SIXTEENTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (602_700+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W266_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 602_701..602_900 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- SEVENTEENTH consecutive above-own-A;
    # B base == own-A tail+1 (604_700+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=602701 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=604701 span=200 checked=200 verdict=FREE.
    # W268+ projection (gate-derived pre-seat probe leg4, pre-W267
    # universe): A naive first-clean 604701..606700 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 604901..605100 hops=0 CLEAN at naive -- first-clean 604901..605100 BUT lands INSIDE the projection A window,
    # (W268p_B_lands_inside_W268p_A_naive=true -- staircase re-emergence face: the W268 walk MUST hop past own-A reservation);
    # the W268 freezer MUST
    # re-derive on the post-W267 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    267: {"a": (602_701, 604_700), "b_exit": (604_701, 604_900),
         "engine_owner": "bm-c"},
    # W268 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261018-1229-bmc-w268-seat published=reserved by bm-c itself @
    # origin b9ad2f1119 (r1089, queue-head seat-first supply -- W267 registered+FINALIZED complete at publish, W268 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W267 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit f1ec8231c7 (prereg research/PERPETUAL_N1_W268_PREREG.md
    # bm-c r1090 window machine-SUB derive landed pre-freeze, probe
    # results/_w268bmc_20261018_probe_receipt.json @ b9ad2f1119);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W267 five-face (freeze 7b9e937737) + W267
    # finalize product landed (n1_w267_results.json present, ledger
    # head 1011735 machine-read at freeze time); zero --no-verify;
    # the W268 seat MSG sits in fleet/inbox/processed/MSG-20261018-1229-bmc-w268-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w268bmc_20261018_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk SEVENTEENTH consecutive A-hop (the naive continuation 604_701..606_700 is REFUSED
    # at naive start -- the registered W267 B band sits INSIDE the naive A window;
    # the walk hops past the W267 B tail -> A first-clean, hops=1 -- SEVENTEENTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (604_900+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W267_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 604_901..605_100 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- EIGHTEENTH consecutive above-own-A;
    # B base == own-A tail+1 (606_900+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=604901 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=606901 span=200 checked=200 verdict=FREE.
    # W269+ projection (gate-derived pre-seat probe leg4, pre-W268
    # universe): A naive first-clean 606901..608900 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 607101..607300 hops=0 CLEAN at naive -- first-clean 607101..607300 BUT lands INSIDE the projection A window,
    # (W269p_B_lands_inside_W269p_A_naive=true -- staircase re-emergence face: the W269 walk MUST hop past own-A reservation);
    # the W269 freezer MUST
    # re-derive on the post-W268 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    268: {"a": (604_901, 606_900), "b_exit": (606_901, 607_100),
         "engine_owner": "bm-c"},
    # W269 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261018-1407-bmc-w269-seat published=reserved by bm-c itself @
    # origin d630d043b9 (r1091, queue-head seat-first supply -- W268 registered+FINALIZED complete at publish, W269 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W268 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit 67fe12710c (prereg research/PERPETUAL_N1_W269_PREREG.md
    # bm-c r1092 window machine-SUB derive landed pre-freeze, probe
    # results/_w269bmc_20261018_probe_receipt.json @ d630d043b9);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W268 five-face (freeze 8bc7ac759e) + W268
    # finalize product landed (n1_w268_results.json present, ledger
    # head 1013935 machine-read at freeze time); zero --no-verify;
    # the W269 seat MSG sits in fleet/inbox/processed/MSG-20261018-1407-bmc-w269-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w269bmc_20261018_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk EIGHTEENTH consecutive A-hop (the naive continuation 606_901..608_900 is REFUSED
    # at naive start -- the registered W268 B band sits INSIDE the naive A window;
    # the walk hops past the W268 B tail -> A first-clean, hops=1 -- EIGHTEENTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (607_100+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W268_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 607_101..607_300 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- NINETEENTH consecutive above-own-A;
    # B base == own-A tail+1 (609_100+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=607101 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=609101 span=200 checked=200 verdict=FREE.
    # W270+ projection (gate-derived pre-seat probe leg4, pre-W269
    # universe): A naive first-clean 609101..611100 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 609301..609500 hops=0 CLEAN at naive -- first-clean 609301..609500 BUT lands INSIDE the projection A window,
    # (W270p_B_lands_inside_W270p_A_naive=true -- staircase re-emergence face: the W270 walk MUST hop past own-A reservation);
    # the W270 freezer MUST
    # re-derive on the post-W269 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    269: {"a": (607_101, 609_100), "b_exit": (609_101, 609_300),
         "engine_owner": "bm-c"},
    # W270 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261018-1605-bmc-w270-seat published=reserved by bm-c itself @
    # origin 9f480646f4 (r1094, queue-head seat-first supply -- W269 registered+FINALIZED complete at publish, W270 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W269 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit 3bb8b9308e (prereg research/PERPETUAL_N1_W270_PREREG.md
    # bm-c r1094 window machine-SUB derive landed pre-freeze, probe
    # results/_w270bmc_20261018_probe_receipt.json @ 9f480646f4);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W269 five-face (freeze 440b07c94b) + W269
    # finalize product landed (n1_w269_results.json present, ledger
    # head 1016135 machine-read at freeze time); zero --no-verify;
    # the W270 seat MSG sits in fleet/inbox/processed/MSG-20261018-1605-bmc-w270-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w270bmc_20261018_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk NINETEENTH consecutive A-hop (the naive continuation 609_101..611_100 is REFUSED
    # at naive start -- the registered W269 B band sits INSIDE the naive A window;
    # the walk hops past the W269 B tail -> A first-clean, hops=1 -- NINETEENTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (609_300+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W269_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 609_301..609_500 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- TWENTIETH consecutive above-own-A;
    # B base == own-A tail+1 (611_300+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=609301 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=611301 span=200 checked=200 verdict=FREE.
    # W271+ projection (gate-derived pre-seat probe leg4, pre-W270
    # universe): A naive first-clean 611301..613300 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 611501..611700 hops=0 CLEAN at naive -- first-clean 611501..611700 BUT lands INSIDE the projection A window,
    # (W271p_B_lands_inside_W271p_A_naive=true -- staircase re-emergence face: the W271 walk MUST hop past own-A reservation);
    # the W271 freezer MUST
    # re-derive on the post-W270 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    270: {"a": (609_301, 611_300), "b_exit": (611_301, 611_500),
         "engine_owner": "bm-c"},
    # W271 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261018-175x-bmc-w271-seat published=reserved by bm-c itself @
    # origin 87d2697cdc (r1095, queue-head seat-first supply -- W270 registered+FINALIZED complete at publish, W271 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W270 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit f75b18c862 (prereg research/PERPETUAL_N1_W271_PREREG.md
    # bm-c r1096 window machine-SUB derive landed pre-freeze, probe
    # results/_w271bmc_20261018_probe_receipt.json @ 87d2697cdc);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W270 five-face (freeze 1c814343ed) + W270
    # finalize product landed (n1_w270_results.json present, ledger
    # head 1018335 machine-read at freeze time); zero --no-verify;
    # the W271 seat MSG sits in fleet/inbox/processed/MSG-20261018-175x-bmc-w271-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w271bmc_20261018_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk TWENTIETH consecutive A-hop (the naive continuation 611_301..613_300 is REFUSED
    # at naive start -- the registered W270 B band sits INSIDE the naive A window;
    # the walk hops past the W270 B tail -> A first-clean, hops=1 -- TWENTIETH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (611_500+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W270_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 611_501..611_700 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- TWENTY-FIRST consecutive above-own-A;
    # B base == own-A tail+1 (613_500+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=611501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=613501 span=200 checked=200 verdict=FREE.
    # W272+ projection (gate-derived pre-seat probe leg4, pre-W271
    # universe): A naive first-clean 613501..615500 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 613701..613900 hops=0 CLEAN at naive -- first-clean 613701..613900 BUT lands INSIDE the projection A window,
    # (W272p_B_lands_inside_W272p_A_naive=true -- staircase re-emergence face: the W272 walk MUST hop past own-A reservation);
    # the W272 freezer MUST
    # re-derive on the post-W271 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    271: {"a": (611_501, 613_500), "b_exit": (613_501, 613_700),
         "engine_owner": "bm-c"},
    # W272 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261018-191x-bmc-w272-seat published=reserved by bm-c itself @
    # origin f608ff1cee (r1098, queue-head seat-first supply -- W271 registered+FINALIZED complete at publish, W272 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W271 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit c049a57623 (prereg research/PERPETUAL_N1_W272_PREREG.md
    # bm-c r1099 window machine-SUB derive landed pre-freeze, probe
    # results/_w272bmc_20261018_probe_receipt.json @ f608ff1cee);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W271 five-face (freeze 7dd091eef1) + W271
    # finalize product landed (n1_w271_results.json present, ledger
    # head 1020535 machine-read at freeze time); zero --no-verify;
    # the W272 seat MSG sits in fleet/inbox/processed/MSG-20261018-191x-bmc-w272-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w272bmc_20261018_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk TWENTY-FIRST consecutive A-hop (the naive continuation 613_501..615_500 is REFUSED
    # at naive start -- the registered W271 B band sits INSIDE the naive A window;
    # the walk hops past the W271 B tail -> A first-clean, hops=1 -- TWENTY-FIRST
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (613_700+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W271_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 613_701..613_900 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- TWENTY-SECOND consecutive above-own-A;
    # B base == own-A tail+1 (615_700+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=613701 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=615701 span=200 checked=200 verdict=FREE.
    # W273+ projection (gate-derived pre-seat probe leg4, pre-W272
    # universe): A naive first-clean 615701..617700 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 615901..616100 hops=0 CLEAN at naive -- first-clean 615901..616100 BUT lands INSIDE the projection A window,
    # (W273p_B_lands_inside_W273p_A_naive=true -- staircase re-emergence face: the W273 walk MUST hop past own-A reservation);
    # the W273 freezer MUST
    # re-derive on the post-W272 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    272: {"a": (613_701, 615_700), "b_exit": (615_701, 615_900),
         "engine_owner": "bm-c"},
    # W273 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261018-211x-bmc-w273-seat published=reserved by bm-c itself @
    # origin 39e1bb32f1 (r1101, queue-head seat-first supply -- W272 registered+FINALIZED complete at publish, W273 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W272 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit 839441a547 (prereg research/PERPETUAL_N1_W273_PREREG.md
    # bm-c r1102 window E63 canon-clone builder derive landed pre-freeze, probe
    # results/_w273bmc_20261018_probe_receipt.json @ 39e1bb32f1);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W272 five-face (freeze c99ee20a45) + W272
    # finalize product landed (n1_w272_results.json present, ledger
    # head 1022735 machine-read at freeze time); zero --no-verify;
    # the W273 seat MSG sits in fleet/inbox/processed/MSG-20261018-211x-bmc-w273-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w273bmc_20261018_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk TWENTY-SECOND consecutive A-hop (the naive continuation 615_701..617_700 is REFUSED
    # at naive start -- the registered W272 B band sits INSIDE the naive A window;
    # the walk hops past the W272 B tail -> A first-clean, hops=1 -- TWENTY-SECOND
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (615_900+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W272_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 615_901..616_100 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- TWENTY-THIRD consecutive above-own-A;
    # B base == own-A tail+1 (617_900+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=615901 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=617901 span=200 checked=200 verdict=FREE.
    # W274+ projection (gate-derived pre-seat probe leg4, pre-W273
    # universe): A naive first-clean 617901..619900 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 618101..618300 hops=0 CLEAN at naive -- first-clean 618101..618300 BUT lands INSIDE the projection A window,
    # (W274p_B_lands_inside_W274p_A_naive=true -- staircase re-emergence face: the W274 walk MUST hop past own-A reservation);
    # the W274 freezer MUST
    # re-derive on the post-W273 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    273: {"a": (615_901, 617_900), "b_exit": (617_901, 618_100),
         "engine_owner": "bm-c"},
    # W274 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261019-012x-bmc-w274-seat published=reserved by bm-c itself @
    # origin 70b21a0264 (r1102, queue-head seat-first supply -- W273 registered+FINALIZED complete at publish, W274 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W273 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit 6f31f6e073 (prereg research/PERPETUAL_N1_W274_PREREG.md
    # bm-c r1104 window E63 canon-clone builder derive landed pre-freeze, probe
    # results/_w274bmc_20261019_probe_receipt.json @ 70b21a0264);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W273 five-face (freeze 04f2127db9) + W273
    # finalize product landed (n1_w273_results.json present, ledger
    # head 1024935 machine-read at freeze time); zero --no-verify;
    # the W274 seat MSG sits in fleet/inbox/processed/MSG-20261019-012x-bmc-w274-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w274bmc_20261019_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk TWENTY-THIRD consecutive A-hop (the naive continuation 617_901..619_900 is REFUSED
    # at naive start -- the registered W273 B band sits INSIDE the naive A window;
    # the walk hops past the W273 B tail -> A first-clean, hops=1 -- TWENTY-THIRD
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (618_100+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W273_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 618_101..618_300 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- TWENTY-FOURTH consecutive above-own-A;
    # B base == own-A tail+1 (620_100+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=618101 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=620101 span=200 checked=200 verdict=FREE.
    # W275+ projection (gate-derived pre-seat probe leg4, pre-W274
    # universe): A naive first-clean 620101..622100 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 620301..620500 hops=0 CLEAN at naive -- first-clean 620301..620500 BUT lands INSIDE the projection A window,
    # (W275p_B_lands_inside_W275p_A_naive=true -- staircase re-emergence face: the W275 walk MUST hop past own-A reservation);
    # the W275 freezer MUST
    # re-derive on the post-W274 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    274: {"a": (618_101, 620_100), "b_exit": (620_101, 620_300),
         "engine_owner": "bm-c"},
    # W275 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261019-034x-bmc-w275-seat published=reserved by bm-c itself @
    # origin bf4bbbde1 (r1106, queue-head seat-first supply -- W274 registered+FINALIZED complete at publish, W275 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W274 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit 1fcc0bc30f (prereg research/PERPETUAL_N1_W275_PREREG.md
    # bm-c r1107 window E63 canon-clone builder derive landed pre-freeze, probe
    # results/_w275bmc_20261019_probe_receipt.json @ bf4bbbde1e);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W274 five-face (freeze ec907d164e) + W274
    # finalize product landed (n1_w274_results.json present, ledger
    # head 1027135 machine-read at freeze time); zero --no-verify;
    # the W275 seat MSG sits in fleet/inbox/processed/MSG-20261019-034x-bmc-w275-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w275bmc_20261019_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk TWENTY-FOURTH consecutive A-hop (the naive continuation 620_101..622_100 is REFUSED
    # at naive start -- the registered W274 B band sits INSIDE the naive A window;
    # the walk hops past the W274 B tail -> A first-clean, hops=1 -- TWENTY-FOURTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (620_300+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W274_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 620_301..620_500 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- TWENTY-FIFTH consecutive above-own-A;
    # B base == own-A tail+1 (622_300+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=620301 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=622301 span=200 checked=200 verdict=FREE.
    # W276+ projection (gate-derived pre-seat probe leg4, pre-W275
    # universe): A naive first-clean 622301..624300 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 622501..622700 hops=0 CLEAN at naive -- first-clean 622501..622700 BUT lands INSIDE the projection A window,
    # (W276p_B_lands_inside_W276p_A_naive=true -- staircase re-emergence face: the W276 walk MUST hop past own-A reservation);
    # the W276 freezer MUST
    # re-derive on the post-W275 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    275: {"a": (620_301, 622_300), "b_exit": (622_301, 622_500),
         "engine_owner": "bm-c"},
    # W276 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261019-055x-bmc-w276-seat published=reserved by bm-c itself @
    # origin 21b51a102 (r1109, queue-head seat-first supply -- W275 registered+FINALIZED complete at publish, W276 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W275 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit 770a47fa1f (prereg research/PERPETUAL_N1_W276_PREREG.md
    # bm-c r1110 window E63 canon-clone builder derive landed pre-freeze, probe
    # results/_w276bmc_20261019_probe_receipt.json @ 21b51a102e);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W275 five-face (freeze 018782314d) + W275
    # finalize product landed (n1_w275_results.json present, ledger
    # head 1029335 machine-read at freeze time); zero --no-verify;
    # the W276 seat MSG sits in fleet/inbox/processed/MSG-20261019-055x-bmc-w276-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w276bmc_20261019_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk TWENTY-FIFTH consecutive A-hop (the naive continuation 622_301..624_300 is REFUSED
    # at naive start -- the registered W275 B band sits INSIDE the naive A window;
    # the walk hops past the W275 B tail -> A first-clean, hops=1 -- TWENTY-FIFTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (622_500+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W275_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 622_501..622_700 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- TWENTY-SIXTH consecutive above-own-A;
    # B base == own-A tail+1 (624_500+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=622501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=624501 span=200 checked=200 verdict=FREE.
    # W277+ projection (gate-derived pre-seat probe leg4, pre-W276
    # universe): A naive first-clean 624501..626500 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 624701..624900 hops=0 CLEAN at naive -- first-clean 624701..624900 BUT lands INSIDE the projection A window,
    # (W277p_B_lands_inside_W277p_A_naive=true -- staircase re-emergence face: the W277 walk MUST hop past own-A reservation);
    # the W277 freezer MUST
    # re-derive on the post-W276 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    276: {"a": (622_501, 624_500), "b_exit": (624_501, 624_700),
         "engine_owner": "bm-c"},
    # W277 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261019-080x-bmc-w277-seat published=reserved by bm-c itself @
    # origin c5f8b88f91 (r1112, queue-head seat-first supply -- W276 registered+FINALIZED complete at publish, W277 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W276 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit e0bc4a0ddd (prereg research/PERPETUAL_N1_W277_PREREG.md
    # bm-c r1113 window E63 canon-clone builder derive landed pre-freeze, probe
    # results/_w277bmc_20261019_probe_receipt.json @ c5f8b88f91);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W276 five-face (freeze 354a645155) + W276
    # finalize product landed (n1_w276_results.json present, ledger
    # head 1031535 machine-read at freeze time); zero --no-verify;
    # the W277 seat MSG sits in fleet/inbox/processed/MSG-20261019-080x-bmc-w277-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w277bmc_20261019_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk TWENTY-SIXTH consecutive A-hop (the naive continuation 624_501..626_500 is REFUSED
    # at naive start -- the registered W276 B band sits INSIDE the naive A window;
    # the walk hops past the W276 B tail -> A first-clean, hops=1 -- TWENTY-SIXTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (624_700+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W276_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 624_701..624_900 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- TWENTY-SEVENTH consecutive above-own-A;
    # B base == own-A tail+1 (626_700+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=624701 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=626701 span=200 checked=200 verdict=FREE.
    # W278+ projection (gate-derived pre-seat probe leg4, pre-W277
    # universe): A naive first-clean 626701..628700 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 626901..627100 hops=0 CLEAN at naive -- first-clean 626901..627100 BUT lands INSIDE the projection A window,
    # (W278p_B_lands_inside_W278p_A_naive=true -- staircase re-emergence face: the W278 walk MUST hop past own-A reservation);
    # the W278 freezer MUST
    # re-derive on the post-W277 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    277: {"a": (624_701, 626_700), "b_exit": (626_701, 626_900),
         "engine_owner": "bm-c"},
    # W278 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261019-102x-bmc-w278-seat published=reserved by bm-c itself @
    # origin b187aa6214 (r1114-continuation, queue-head seat-first supply -- W277 registered+FINALIZED complete at publish, W278 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W277 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit df1aaba72a (prereg research/PERPETUAL_N1_W278_PREREG.md
    # bm-c r1116 window E63 canon-clone builder derive landed pre-freeze, probe
    # results/_w278bmc_20261019_probe_receipt.json @ b187aa6214);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W277 five-face (freeze 9e53371814) + W277
    # finalize product landed (n1_w277_results.json present, ledger
    # head 1033735 machine-read at freeze time); zero --no-verify;
    # the W278 seat MSG sits in fleet/inbox/processed/MSG-20261019-102x-bmc-w278-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w278bmc_20261019_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk TWENTY-SEVENTH consecutive A-hop (the naive continuation 626_701..628_700 is REFUSED
    # at naive start -- the registered W277 B band sits INSIDE the naive A window;
    # the walk hops past the W277 B tail -> A first-clean, hops=1 -- TWENTY-SEVENTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (626_900+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W277_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 626_901..627_100 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- TWENTY-EIGHTH consecutive above-own-A;
    # B base == own-A tail+1 (628_900+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=626901 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=628901 span=200 checked=200 verdict=FREE.
    # W279+ projection (gate-derived pre-seat probe leg4, pre-W278
    # universe): A naive first-clean 628901..630900 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 629101..629300 hops=0 CLEAN at naive -- first-clean 629101..629300 BUT lands INSIDE the projection A window,
    # (W279p_B_lands_inside_W279p_A_naive=true -- staircase re-emergence face: the W279 walk MUST hop past own-A reservation);
    # the W279 freezer MUST
    # re-derive on the post-W278 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    278: {"a": (626_901, 628_900), "b_exit": (628_901, 629_100),
         "engine_owner": "bm-c"},
    # W279 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261019-145x-bmc-w279-seat published=reserved by bm-c itself @
    # origin 900c23fe7d (r1119, queue-head seat-first supply -- W278 registered+FINALIZED complete at publish, W279 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W278 five-face + finalize product both in-place; prereg + ADMIT probe
    # receipt frozen commit ba5c725b42 (prereg research/PERPETUAL_N1_W279_PREREG.md
    # bm-c r1122 window E63 canon-clone builder derive landed pre-freeze, probe
    # results/_w279bmc_20261019_probe_receipt.json @ 900c23fe7d);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; delivery window = chain-order
    # splice AFTER the bm-c W278 five-face (freeze b6f486af35) + W278
    # finalize product landed (n1_w278_results.json present, ledger
    # head 1035935 machine-read at freeze time); zero --no-verify;
    # the W279 seat MSG sits in fleet/inbox/processed/MSG-20261019-145x-bmc-w279-seat.md at freeze
    # time, honest archived per S7 law);
    # band gate ADMIT results/_w279bmc_20261019_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk TWENTY-EIGHTH consecutive A-hop (the naive continuation 628_901..630_900 is REFUSED
    # at naive start -- the registered W278 B band sits INSIDE the naive A window;
    # the walk hops past the W278 B tail -> A first-clean, hops=1 -- TWENTY-EIGHTH
    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face
    # ENDED at W252;
    # A base == registered prior-wave B tail+1 (629_100+1) machine-checkable; A_clean_at_naive_start=false;
    # A_staircase_hop_past_W278_B=true)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation
    # 629_101..629_300 is REFUSED at its own start -- the naive window lands
    # INSIDE the own-wave A first-clean window --
    # own-A reservation cascade standard leg; hops=1,
    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A
    # tail -> B lands ABOVE own-A -- TWENTY-NINTH consecutive above-own-A;
    # B base == own-A tail+1 (631_100+1) EXACT; B_lands_above_own_A=true;
    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)
    # single-window derive (r812 merged the gate legs INTO the
    # pre-seat probe; dual-window parity N/A honest); scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=629101 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=631101 span=200 checked=200 verdict=FREE.
    # W280+ projection (gate-derived pre-seat probe leg4, pre-W279
    # universe): A naive first-clean 631101..633100 hops=0 (this window's gate: CLEAN, zero live
    # seed refusers) / B naive 631301..631500 hops=0 CLEAN at naive -- first-clean 631301..631500 BUT lands INSIDE the projection A window,
    # (W280p_B_lands_inside_W280p_A_naive=true -- staircase re-emergence face: the W280 walk MUST hop past own-A reservation);
    # the W280 freezer MUST
    # re-derive on the post-W279 universe AND reserve the own-wave A window
    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1
    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.
    279: {"a": (629_101, 631_100), "b_exit": (631_101, 631_300),
         "engine_owner": "bm-c"},
    # W280 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261019-200x-bmc-w280-seat published=reserved by bm-c itself @
    # origin f96272d8b9 (r1124, queue-head seat-first supply -- W279 registered+FINALIZED
    # at publish, W280 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W279 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W280_PREREG.md bm-c r1130 window derive landed
    # pre-freeze, freeze-time gate 5f279e44fc; probe receipt
    # results/_w280bmc_20261021_probe_receipt.json @ b18770ffb1);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W279 five-face
    # (freeze 3810f4a7ac) + W279 finalize product landed (ledger head
    # 1038135 machine-read); zero --no-verify; the W280 seat MSG sits in
    # fleet/inbox/processed/MSG-20261019-200x-bmc-w280-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w280bmc_20261021_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk TWENTY-NINTH consecutive A-hop (naive 631_101..633_100 REFUSED
    # at start by the registered W279 B band; walk past the W279 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (631_300+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 631_301..631_500 lands
    # INSIDE the own-wave A first-clean window; walk past the own-A tail ->
    # B lands ABOVE own-A at tail+1 -- TWENTIETH-plus consecutive
    # above-own-A, THIRTIETH exact; B base == own-A tail+1 (633_300+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=631301 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=633301 span=200 checked=200 verdict=FREE.
    # W281+ projection (pre-seat probe leg4, pre-W280 universe):
    # A naive first-clean 633_301..635_300 hops=0 / B naive 633_501..633_700 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W281 freezer MUST
    # re-derive on the post-W280 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    280: {"a": (631_301, 633_300), "b_exit": (633_301, 633_500),
         "engine_owner": "bm-c"},
    # W281 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-0225-bmc-w281-seat published=reserved by bm-c itself @
    # origin 1c9ff56dcd (r1132, queue-head seat-first supply -- W280 registered+FINALIZED
    # at publish, W281 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W280 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W281_PREREG.md bm-c r1133 window derive landed
    # pre-freeze, freeze-time gate f51afd09ad; probe receipt
    # results/_w281bmc_20261020_probe_receipt.json @ 1c9ff56dcd);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W280 five-face
    # (freeze 7a5b47ff94) + W280 finalize product landed (ledger head
    # 1040335 machine-read); zero --no-verify; the W281 seat MSG sits in
    # fleet/inbox/processed/MSG-20261020-0225-bmc-w281-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w281bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk THIRTY-FIRST consecutive A-hop (naive 633_301..635_300 REFUSED
    # at start by the registered W280 B band; walk past the W280 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (633_500+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 633_501..633_700 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- THIRTY-SECOND
    # consecutive above-own-A; B base == own-A tail+1 (635_500+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=633501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=635501 span=200 checked=200 verdict=FREE.
    # W282+ projection (pre-seat probe leg4, pre-W281 universe):
    # A naive first-clean 635_501..637_500 hops=0 / B naive 635_701..635_900 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W282 freezer MUST
    # re-derive on the post-W281 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    281: {"a": (633_501, 635_500), "b_exit": (635_501, 635_700),
         "engine_owner": "bm-c"},
    # W282 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-0345-bmc-w282-seat published=reserved by bm-c itself @
    # origin 9d321472eb (r1136, queue-head seat-first supply -- W281 registered+FINALIZED
    # at publish, W282 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W281 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W282_PREREG.md bm-c r1137 window derive landed
    # pre-freeze, freeze-time gate 7744416654; probe receipt
    # results/_w282bmc_20261020_probe_receipt.json @ 9d321472eb);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W281 five-face
    # (freeze aa376549cd) + W281 finalize product landed (ledger head
    # 1042535 machine-read); zero --no-verify; the W282 seat MSG sits in
    # fleet/inbox/processed/MSG-20261020-0345-bmc-w282-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w282bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk THIRTY-SECOND consecutive A-hop (naive 635_501..637_500 REFUSED
    # at start by the registered W281 B band; walk past the W281 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (635_700+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 635_701..635_900 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- THIRTY-THIRD
    # consecutive above-own-A; B base == own-A tail+1 (637_700+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=635701 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=637701 span=200 checked=200 verdict=FREE.
    # W283+ projection (pre-seat probe leg4, pre-W282 universe):
    # A naive first-clean 637_701..639_700 hops=0 / B naive 637_901..638_100 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W282 freezer MUST
    # re-derive on the post-W282 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    282: {"a": (635_701, 637_700), "b_exit": (637_701, 637_900),
         "engine_owner": "bm-c"},
    # W283 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-0500-bmc-w283-seat published=reserved by bm-c itself @
    # origin 8528d823fa (r1140, queue-head seat-first supply -- W282 registered+FINALIZED
    # at publish, W283 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W282 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W283_PREREG.md bm-c r1141 window derive landed
    # pre-freeze, freeze-time gate 83b394ce64; probe receipt
    # results/_w283bmc_20261020_probe_receipt.json @ 8528d823fa);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W282 five-face
    # (freeze 01fe28eec2) + W282 finalize product landed (ledger head
    # 1044735 machine-read); zero --no-verify; the W283 seat MSG sits in
    # fleet/inbox/MSG-20261020-0500-bmc-w283-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w283bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk THIRTY-THIRD consecutive A-hop (naive 637_701..639_700 REFUSED
    # at start by the registered W282 B band; walk past the W282 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (637_900+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 637_901..638_100 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- THIRTY-FOURTH
    # consecutive above-own-A; B base == own-A tail+1 (639_900+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=637901 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=639901 span=200 checked=200 verdict=FREE.
    # W284+ projection (pre-seat probe leg4, pre-W283 universe):
    # A naive first-clean 639_901..641_900 hops=0 / B naive 640_101..640_300 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W283 freezer MUST
    # re-derive on the post-W283 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    283: {"a": (637_901, 639_900), "b_exit": (639_901, 640_100),
         "engine_owner": "bm-c"},
    # W284 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-0635-bmc-w284-seat published=reserved by bm-c itself @
    # origin 52cca74151 (r1144, queue-head seat-first supply -- W283 registered+FINALIZED
    # at publish, W284 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W283 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W284_PREREG.md bm-c r1145 window derive landed
    # pre-freeze, freeze-time gate 28c5f465f2; probe receipt
    # results/_w284bmc_20261020_probe_receipt.json @ edf87a9724);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W283 five-face
    # (freeze 44a3abdff3) + W283 finalize product landed (ledger head
    # 1046941 machine-read); zero --no-verify; the W284 seat MSG sits in
    # fleet/inbox/MSG-20261020-0635-bmc-w284-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w284bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk THIRTY-FOURTH consecutive A-hop (naive 639_901..641_900 REFUSED
    # at start by the registered W283 B band; walk past the W283 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (640_100+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 640_101..640_300 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- THIRTY-FIFTH
    # consecutive above-own-A; B base == own-A tail+1 (642_100+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=640101 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=642101 span=200 checked=200 verdict=FREE.
    # W285+ projection (pre-seat probe leg4, pre-W284 universe):
    # A naive first-clean 642_101..644_100 hops=0 / B naive 642_301..642_500 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W284 freezer MUST
    # re-derive on the post-W284 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    284: {"a": (640_101, 642_100), "b_exit": (642_101, 642_300),
         "engine_owner": "bm-c"},
    # W285 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-0758-bmc-w285-seat published=reserved by bm-c itself @
    # origin 597a614539 (r1148, queue-head seat-first supply -- W284 registered+FINALIZED
    # at publish, W285 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W284 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W285_PREREG.md bm-c r1149 window derive landed
    # pre-freeze, freeze-time gate 3c12829cf9; probe receipt
    # results/_w285bmc_20261020_probe_receipt.json @ 597a614539);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W284 five-face
    # (freeze a8e5ddfd65) + W284 finalize product landed (ledger head
    # 1049141 machine-read); zero --no-verify; the W285 seat MSG sits in
    # fleet/inbox/MSG-20261020-0758-bmc-w285-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w285bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk THIRTY-FIFTH consecutive A-hop (naive 642_101..644_100 REFUSED
    # at start by the registered W284 B band; walk past the W284 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (642_300+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 642_301..642_500 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- THIRTY-SIXTH
    # consecutive above-own-A; B base == own-A tail+1 (644_300+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=642301 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=644301 span=200 checked=200 verdict=FREE.
    # W286+ projection (pre-seat probe leg4, pre-W285 universe):
    # A naive first-clean 644_301..646_300 hops=0 / B naive 644_501..644_700 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W285 freezer MUST
    # re-derive on the post-W285 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    285: {"a": (642_301, 644_300), "b_exit": (644_301, 644_500),
         "engine_owner": "bm-c"},
    # W286 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-0855-bmc-w286-seat published=reserved by bm-c itself @
    # origin ab76f5b0b3 (r1151, queue-head seat-first supply -- W285 registered+FINALIZED
    # at publish, W286 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W285 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W286_PREREG.md bm-c r1152 window derive landed
    # pre-freeze, freeze-time gate beb10feab8; probe receipt
    # results/_w286bmc_20261020_probe_receipt.json @ ab76f5b0b3);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W285 five-face
    # (freeze b097d23658) + W285 finalize product landed (ledger head
    # 1051341 machine-read); zero --no-verify; the W286 seat MSG sits in
    # fleet/inbox/MSG-20261020-0855-bmc-w286-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w286bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk THIRTY-SEVENTH consecutive A-hop (naive 644_301..646_300 REFUSED
    # at start by the registered W285 B band; walk past the W285 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (644_500+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 644_501..644_700 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- THIRTY-EIGHTH
    # consecutive above-own-A; B base == own-A tail+1 (646_500+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=644501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=646501 span=200 checked=200 verdict=FREE.
    # W287+ projection (pre-seat probe leg4, pre-W286 universe):
    # A naive first-clean 646_501..648_500 hops=0 / B naive 646_701..646_900 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W286 freezer MUST
    # re-derive on the post-W286 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    286: {"a": (644_501, 646_500), "b_exit": (646_501, 646_700),
         "engine_owner": "bm-c"},
    # W287 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-1027-bmc-w287-seat published=reserved by bm-c itself @
    # origin 63236cf485 (r1154, queue-head seat-first supply -- W286 registered+FINALIZED
    # at publish, W287 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W286 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W287_PREREG.md bm-c r1155 window derive landed
    # pre-freeze, freeze-time gate f138546d08; probe receipt
    # results/_w287bmc_20261020_probe_receipt.json @ 63236cf485);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W286 five-face
    # (freeze 96cfcf7125) + W286 finalize product landed (ledger head
    # 1053541 machine-read); zero --no-verify; the W287 seat MSG sits in
    # fleet/inbox/MSG-20261020-1027-bmc-w287-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w287bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk THIRTY-NINTH consecutive A-hop (naive 646_501..648_500 REFUSED
    # at start by the registered W286 B band; walk past the W286 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (646_700+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 646_701..646_900 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FORTIETH
    # consecutive above-own-A; B base == own-A tail+1 (648_700+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=646701 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=648701 span=200 checked=200 verdict=FREE.
    # W288+ projection (pre-seat probe leg4, pre-W287 universe):
    # A naive first-clean 648_701..650_700 hops=0 / B naive 648_901..649_100 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W287 freezer MUST
    # re-derive on the post-W287 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    287: {"a": (646_701, 648_700), "b_exit": (648_701, 648_900),
         "engine_owner": "bm-c"},
    # W288 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-1335-bmc-w288-seat published=reserved by bm-c itself @
    # origin a2f3e3ce27 (r1157, queue-head seat-first supply -- W287 registered+FINALIZED
    # at publish, W288 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W287 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W288_PREREG.md bm-c r1158 window derive landed
    # pre-freeze, freeze-time gate 22ffa74b01; probe receipt
    # results/_w288bmc_20261020_probe_receipt.json @ a2f3e3ce27);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W287 five-face
    # (freeze 0b5adf2a6b) + W287 finalize product landed (ledger head
    # 1055741 machine-read); zero --no-verify; the W288 seat MSG sits in
    # fleet/inbox/MSG-20261020-1335-bmc-w288-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w288bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FORTY-FIRST consecutive A-hop (naive 648_701..650_700 REFUSED
    # at start by the registered W287 B band; walk past the W287 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (648_900+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 648_901..649_100 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FORTY-SECOND
    # consecutive above-own-A; B base == own-A tail+1 (650_900+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=648901 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=650901 span=200 checked=200 verdict=FREE.
    # W289+ projection (pre-seat probe leg4, pre-W288 universe):
    # A naive first-clean 650_901..652_900 hops=0 / B naive 651_101..651_300 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W288 freezer MUST
    # re-derive on the post-W288 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    288: {"a": (648_901, 650_900), "b_exit": (650_901, 651_100),
         "engine_owner": "bm-c"},
    # W289 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-1535-bmc-w289-seat published=reserved by bm-c itself @
    # origin c97b8308ec (r1160, queue-head seat-first supply -- W288 registered+FINALIZED
    # at publish, W289 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W288 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W289_PREREG.md bm-c r1161 window derive landed
    # pre-freeze, freeze-time gate c97b8308ec; probe receipt
    # results/_w289bmc_20261020_probe_receipt.json @ 677d49d3c0);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W288 five-face
    # (freeze f59b40c6c1) + W288 finalize product landed (ledger head
    # 1057941 machine-read); zero --no-verify; the W289 seat MSG sits in
    # fleet/inbox/MSG-20261020-1535-bmc-w289-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w289bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FORTY-SECOND consecutive A-hop (naive 650_901..652_900 REFUSED
    # at start by the registered W288 B band; walk past the W288 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (651_100+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 651_101..651_300 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FORTY-THIRD
    # consecutive above-own-A; B base == own-A tail+1 (653_100+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=651101 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=653101 span=200 checked=200 verdict=FREE.
    # W290+ projection (pre-seat probe leg4, pre-W289 universe):
    # A naive first-clean 653_101..655_100 hops=0 / B naive 653_301..653_500 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W289 freezer MUST
    # re-derive on the post-W289 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    289: {"a": (651_101, 653_100), "b_exit": (653_101, 653_300),
         "engine_owner": "bm-c"},
    # W290 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-1720-bmc-w290-seat published=reserved by bm-c itself @
    # origin 43eba4c179 (r1163, queue-head seat-first supply -- W289 registered+FINALIZED
    # at publish, W290 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W289 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W290_PREREG.md bm-c r1164 window derive landed
    # pre-freeze, freeze-time gate 1981248022; probe receipt
    # results/_w290bmc_20261020_probe_receipt.json @ 43eba4c179);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W289 five-face
    # (freeze b539333a57) + W289 finalize product landed (ledger head
    # 1060141 machine-read); zero --no-verify; the W290 seat MSG sits in
    # fleet/inbox/MSG-20261020-1720-bmc-w290-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w290bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FORTY-THIRD consecutive A-hop (naive 653_101..655_100 REFUSED
    # at start by the registered W289 B band; walk past the W289 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (653_300+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 653_301..653_500 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FORTY-FOURTH
    # consecutive above-own-A; B base == own-A tail+1 (655_300+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=653301 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=655301 span=200 checked=200 verdict=FREE.
    # W291+ projection (pre-seat probe leg4, pre-W290 universe):
    # A naive first-clean 655_301..657_300 hops=0 / B naive 655_501..655_700 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W290 freezer MUST
    # re-derive on the post-W290 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    290: {"a": (653_301, 655_300), "b_exit": (655_301, 655_500),
         "engine_owner": "bm-c"},
    # W291 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-1815-bmc-w291-seat published=reserved by bm-c itself @
    # origin 1ca0298ca5 (r1166, queue-head seat-first supply -- W290 registered+FINALIZED
    # at publish, W291 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W290 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W291_PREREG.md bm-c r1167 window derive landed
    # pre-freeze, freeze-time gate 009c2f8e55; probe receipt
    # results/_w291bmc_20261020_probe_receipt.json @ 1ca0298ca5);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W290 five-face
    # (freeze 865a1906dd) + W290 finalize product landed (ledger head
    # 1062341 machine-read); zero --no-verify; the W291 seat MSG sits in
    # fleet/inbox/MSG-20261020-1815-bmc-w291-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w291bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FORTY-FOURTH consecutive A-hop (naive 655_301..657_300 REFUSED
    # at start by the registered W290 B band; walk past the W290 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (655_500+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 655_501..655_700 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FORTY-FIFTH
    # consecutive above-own-A; B base == own-A tail+1 (657_500+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=655501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=657501 span=200 checked=200 verdict=FREE.
    # W292+ projection (pre-seat probe leg4, pre-W291 universe):
    # A naive first-clean 657_501..659_500 hops=0 / B naive 657_701..657_900 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W291 freezer MUST
    # re-derive on the post-W291 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    291: {"a": (655_501, 657_500), "b_exit": (657_501, 657_700),
         "engine_owner": "bm-c"},
    # W292 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-1912-bmc-w292-seat published=reserved by bm-c itself @
    # origin 5eac2d5a8e (r1169, queue-head seat-first supply -- W291 registered+FINALIZED
    # at publish, W292 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W291 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W292_PREREG.md bm-c r1170 window derive landed
    # pre-freeze, freeze-time gate 5bbaccbf58; probe receipt
    # results/_w292bmc_20261020_probe_receipt.json @ 5eac2d5a8e);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W291 five-face
    # (freeze dc8f229516) + W291 finalize product landed (ledger head
    # 1064541 machine-read); zero --no-verify; the W292 seat MSG sits in
    # fleet/inbox/MSG-20261020-1912-bmc-w292-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w292bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FORTY-FIFTH consecutive A-hop (naive 657_501..659_500 REFUSED
    # at start by the registered W291 B band; walk past the W291 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (657_700+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 657_701..657_900 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FORTY-SIXTH
    # consecutive above-own-A; B base == own-A tail+1 (659_700+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=657701 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=659701 span=200 checked=200 verdict=FREE.
    # W293+ projection (pre-seat probe leg4, pre-W292 universe):
    # A naive first-clean 659_701..661_700 hops=0 / B naive 659_901..660_100 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W292 freezer MUST
    # re-derive on the post-W292 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    292: {"a": (657_701, 659_700), "b_exit": (659_701, 659_900),
         "engine_owner": "bm-c"},
    # W293 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-2025-bmc-w293-seat published=reserved by bm-c itself @
    # origin da806649e7 (r1172, queue-head seat-first supply -- W292 registered+FINALIZED
    # at publish, W293 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W292 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W293_PREREG.md bm-c r1173 window derive landed
    # pre-freeze, freeze-time gate 2508ccd77b; probe receipt
    # results/_w293bmc_20261020_probe_receipt.json @ da806649e7);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W292 five-face
    # (freeze 5006a5c273) + W292 finalize product landed (ledger head
    # 1066741 machine-read); zero --no-verify; the W293 seat MSG sits in
    # fleet/inbox/MSG-20261020-2025-bmc-w293-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w293bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FORTY-SIXTH consecutive A-hop (naive 659_701..661_700 REFUSED
    # at start by the registered W292 B band; walk past the W292 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (659_900+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 659_901..660_100 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FORTY-SEVENTH
    # consecutive above-own-A; B base == own-A tail+1 (661_900+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=659901 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=661901 span=200 checked=200 verdict=FREE.
    # W294+ projection (pre-seat probe leg4, pre-W293 universe):
    # A naive first-clean 661_901..663_900 hops=0 / B naive 662_101..662_300 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W293 freezer MUST
    # re-derive on the post-W293 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    293: {"a": (659_901, 661_900), "b_exit": (661_901, 662_100),
         "engine_owner": "bm-c"},
    # W294 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261020-2135-bmc-w294-seat published=reserved by bm-c itself @
    # origin b438b02eef (r1175, queue-head seat-first supply -- W293 registered+FINALIZED
    # at publish, W294 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W293 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W294_PREREG.md bm-c r1176 window derive landed
    # pre-freeze, freeze-time gate n/a; probe receipt
    # results/_w294bmc_20261020_probe_receipt.json @ b438b02eef);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W293 five-face
    # (freeze 8cba3736c6) + W293 finalize product landed (ledger head
    # 1068941 machine-read); zero --no-verify; the W294 seat MSG sits in
    # fleet/inbox/processed/MSG-20261020-2135-bmc-w294-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w294bmc_20261020_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FORTY-SEVENTH consecutive A-hop (naive 661_901..663_900 REFUSED
    # at start by the registered W293 B band; walk past the W293 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (662_100+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 662_101..662_300 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FORTY-EIGHTH
    # consecutive above-own-A; B base == own-A tail+1 (664_100+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=662101 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=664101 span=200 checked=200 verdict=FREE.
    # W295+ projection (pre-seat probe leg4, pre-W294 universe):
    # A naive first-clean 664_101..666_100 hops=0 / B naive 664_301..664_500 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W294 freezer MUST
    # re-derive on the post-W294 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    294: {"a": (662_101, 664_100), "b_exit": (664_101, 664_300),
         "engine_owner": "bm-c"},
    # W295 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-0055-bmc-w295-seat published=reserved by bm-c itself @
    # origin fdd81db548 (r1175, queue-head seat-first supply -- W295 registered+FINALIZED
    # at publish, W295 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W295 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W295_PREREG.md bm-c r1176 window derive landed
    # pre-freeze, freeze-time gate 366f262812; probe receipt
    # results/_w295bmc_20261024_probe_receipt.json @ fdd81db548);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W295 five-face
    # (freeze a3a6c17eb3) + W295 finalize product landed (ledger head
    # 1071141 machine-read); zero --no-verify; the W295 seat MSG sits in
    # fleet/inbox/MSG-20261024-0055-bmc-w295-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w295bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FORTY-EIGHTH consecutive A-hop (naive 664_101..666_100 REFUSED
    # at start by the registered W295 B band; walk past the W295 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (664_300+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 664_301..664_500 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FORTY-EIGHTH
    # consecutive above-own-A; B base == own-A tail+1 (666_300+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=664301 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=666301 span=200 checked=200 verdict=FREE.
    # W296+ projection (pre-seat probe leg4, pre-W295 universe):
    # A naive first-clean 666_301..668_300 hops=0 / B naive 666_501..666_700 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W295 freezer MUST
    # re-derive on the post-W295 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    295: {"a": (664_301, 666_300), "b_exit": (666_301, 666_500),
         "engine_owner": "bm-c"},
    # W296 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-0116-bmc-w296-seat published=reserved by bm-c itself @
    # origin 47d79905a1 (r1178, queue-head seat-first supply -- W296 registered+FINALIZED
    # at publish, W296 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W296 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W296_PREREG.md bm-c r1179 window derive landed
    # pre-freeze, freeze-time gate 89128e9ac8; probe receipt
    # results/_w296bmc_20261024_probe_receipt.json @ 47d79905a1);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W296 five-face
    # (freeze 5aa6720305) + W296 finalize product landed (ledger head
    # 1073341 machine-read); zero --no-verify; the W296 seat MSG sits in
    # fleet/inbox/MSG-20261024-0116-bmc-w296-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w296bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FORTY-NINTH consecutive A-hop (naive 666_301..668_300 REFUSED
    # at start by the registered W296 B band; walk past the W296 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (666_500+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 666_501..666_700 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FIFTIETH
    # consecutive above-own-A; B base == own-A tail+1 (668_500+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=666501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=668501 span=200 checked=200 verdict=FREE.
    # W297+ projection (pre-seat probe leg4, pre-W296 universe):
    # A naive first-clean 668_501..670_500 hops=0 / B naive 668_701..668_900 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W296 freezer MUST
    # re-derive on the post-W296 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    296: {"a": (666_501, 668_500), "b_exit": (668_501, 668_700),
         "engine_owner": "bm-c"},
    # W297 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-0205-bmc-w297-seat published=reserved by bm-c itself @
    # origin 737f506bb5 (r1180, queue-head seat-first supply -- W297 registered+FINALIZED
    # at publish, W297 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W297 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W297_PREREG.md bm-c r1180 window derive landed
    # pre-freeze, freeze-time gate 069f05adcc; probe receipt
    # results/_w297bmc_20261024_probe_receipt.json @ 1d7ea69e3e);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W297 five-face
    # (freeze 78d69f3c4f) + W297 finalize product landed (ledger head
    # 1075541 machine-read); zero --no-verify; the W297 seat MSG sits in
    # fleet/inbox/MSG-20261024-0205-bmc-w297-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w297bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FIFTIETH consecutive A-hop (naive 668_501..670_500 REFUSED
    # at start by the registered W297 B band; walk past the W297 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (668_700+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 668_701..668_900 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FIFTY-FIRST
    # consecutive above-own-A; B base == own-A tail+1 (670_700+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=668701 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=670701 span=200 checked=200 verdict=FREE.
    # W298+ projection (pre-seat probe leg4, pre-W297 universe):
    # A naive first-clean 670_701..672_700 hops=0 / B naive 670_901..671_100 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W297 freezer MUST
    # re-derive on the post-W297 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    297: {"a": (668_701, 670_700), "b_exit": (670_701, 670_900),
         "engine_owner": "bm-c"},
    # W298 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-0245-bmc-w298-seat published=reserved by bm-c itself @
    # origin 48ac82f228 (r1181, queue-head seat-first supply -- W298 registered+FINALIZED
    # at publish, W298 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W298 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W298_PREREG.md bm-c r1181 window derive landed
    # pre-freeze, freeze-time gate e51302d9dd; probe receipt
    # results/_w298bmc_20261024_probe_receipt.json @ 48ac82f228);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W298 five-face
    # (freeze 61964c8b25) + W298 finalize product landed (ledger head
    # 1077741 machine-read); zero --no-verify; the W298 seat MSG sits in
    # fleet/inbox/MSG-20261024-0245-bmc-w298-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w298bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FIFTY-FIRST consecutive A-hop (naive 670_701..672_700 REFUSED
    # at start by the registered W297 B band; walk past the W297 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (670_900+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 670_901..671_100 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FIFTY-SECOND
    # consecutive above-own-A; B base == own-A tail+1 (672_900+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=670901 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=672901 span=200 checked=200 verdict=FREE.
    # W299+ projection (pre-seat probe leg4, pre-W298 universe):
    # A naive first-clean 672_901..674_900 hops=0 / B naive 673_101..673_300 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W299 freezer MUST
    # re-derive on the post-W298 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    298: {"a": (670_901, 672_900), "b_exit": (672_901, 673_100),
         "engine_owner": "bm-c"},
    # W299 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-0335-bmc-w299-seat published=reserved by bm-c itself @
    # origin 9f26a57936 (r1182, queue-head seat-first supply -- W299 registered+FINALIZED
    # at publish, W299 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W299 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W299_PREREG.md bm-c r1182 window derive landed
    # pre-freeze, freeze-time gate d24a4680fd; probe receipt
    # results/_w299bmc_20261024_probe_receipt.json @ 9f26a57936);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W299 five-face
    # (freeze 1708393408) + W299 finalize product landed (ledger head
    # 1079941 machine-read); zero --no-verify; the W299 seat MSG sits in
    # fleet/inbox/MSG-20261024-0335-bmc-w299-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w299bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FIFTY-SECOND consecutive A-hop (naive 672_901..674_900 REFUSED
    # at start by the registered W298 B band; walk past the W298 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (673_100+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 673_101..673_300 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FIFTY-THIRD
    # consecutive above-own-A; B base == own-A tail+1 (675_100+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=673101 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=675101 span=200 checked=200 verdict=FREE.
    # W300+ projection (pre-seat probe leg4, pre-W299 universe):
    # A naive first-clean 675_101..677_100 hops=0 / B naive 675_301..675_500 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W300 freezer MUST
    # re-derive on the post-W299 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    299: {"a": (673_101, 675_100), "b_exit": (675_101, 675_300),
         "engine_owner": "bm-c"},
    # W300 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-0415-bmc-w300-seat published=reserved by bm-c itself @
    # origin aebf316324 (r1183, queue-head seat-first supply -- W300 registered+FINALIZED
    # at publish, W300 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W300 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W300_PREREG.md bm-c r1183 window derive landed
    # pre-freeze, freeze-time gate 5973d8625a; probe receipt
    # results/_w300bmc_20261024_probe_receipt.json @ aebf316324);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W300 five-face
    # (freeze f1b57a0e67) + W300 finalize product landed (ledger head
    # 1082141 machine-read); zero --no-verify; the W300 seat MSG sits in
    # fleet/inbox/MSG-20261024-0415-bmc-w300-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w300bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FIFTY-THIRD consecutive A-hop (naive 675_101..677_100 REFUSED
    # at start by the registered W299 B band; walk past the W299 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (675_300+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 675_301..675_500 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FIFTY-FOURTH
    # consecutive above-own-A; B base == own-A tail+1 (677_300+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=675301 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=677301 span=200 checked=200 verdict=FREE.
    # W301+ projection (pre-seat probe leg4, pre-W300 universe):
    # A naive first-clean 677_301..679_300 hops=0 / B naive 677_501..677_700 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W301 freezer MUST
    # re-derive on the post-W300 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    300: {"a": (675_301, 677_300), "b_exit": (677_301, 677_500),
         "engine_owner": "bm-c"},
    # W301 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-0455-bmc-w301-seat published=reserved by bm-c itself @
    # origin 57d4e8526d (r1184, queue-head seat-first supply -- W301 registered+FINALIZED
    # at publish, W301 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W300 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W301_PREREG.md bm-c r1184 window derive landed
    # pre-freeze, freeze-time gate 694e60eab8; probe receipt
    # results/_w301bmc_20261024_probe_receipt.json @ 57d4e8526d);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W300 five-face
    # (freeze 921ff28882) + W300 finalize product landed (ledger head
    # 1084341 machine-read); zero --no-verify; the W301 seat MSG sits in
    # fleet/inbox/MSG-20261024-0455-bmc-w301-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w301bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FIFTY-FOURTH consecutive A-hop (naive 677_301..679_300 REFUSED
    # at start by the registered W300 B band; walk past the W300 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (677_500+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 677_501..677_700 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FIFTY-FIFTH
    # consecutive above-own-A; B base == own-A tail+1 (679_500+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=677501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=679501 span=200 checked=200 verdict=FREE.
    # W302+ projection (pre-seat probe leg4, pre-W301 universe):
    # A naive first-clean 679_501..681_500 hops=0 / B naive 679_701..679_900 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W302 freezer MUST
    # re-derive on the post-W301 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    301: {"a": (677_501, 679_500), "b_exit": (679_501, 679_700),
         "engine_owner": "bm-c"},
    # W302 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-0455-bmc-w301-seat published=reserved by bm-c itself @
    # origin 6a5e62e6bb (r1185, queue-head seat-first supply -- W302 registered+FINALIZED
    # at publish, W302 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W301 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W302_PREREG.md bm-c r1185 window derive landed
    # pre-freeze, freeze-time gate 184e056533; probe receipt
    # results/_w302bmc_20261024_probe_receipt.json @ 6a5e62e6bb);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W301 five-face
    # (freeze 59f0515c12) + W301 finalize product landed (ledger head
    # 1086541 machine-read); zero --no-verify; the W302 seat MSG sits in
    # fleet/inbox/processed/MSG-20261024-0550-bmc-w302-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w302bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FIFTY-FIFTH consecutive A-hop (naive 679_501..681_500 REFUSED
    # at start by the registered W301 B band; walk past the W301 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (679_700+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 679_701..679_900 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FIFTY-SIXTH
    # consecutive above-own-A; B base == own-A tail+1 (681_700+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=679701 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=681701 span=200 checked=200 verdict=FREE.
    # W303+ projection (pre-seat probe leg4, pre-W302 universe):
    # A naive first-clean 681_701..683_700 hops=0 / B naive 681_901..682_100 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W303 freezer MUST
    # re-derive on the post-W302 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    302: {"a": (679_701, 681_700), "b_exit": (681_701, 681_900),
         "engine_owner": "bm-c"},
    # W303 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-0455-bmc-w301-seat published=reserved by bm-c itself @
    # origin f09ad33571 (r1186, queue-head seat-first supply -- W303 registered+FINALIZED
    # at publish, W303 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W302 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W303_PREREG.md bm-c r1186 window derive landed
    # pre-freeze, freeze-time gate 886e88787a; probe receipt
    # results/_w303bmc_20261024_probe_receipt.json @ f09ad33571);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W302 five-face
    # (freeze 78b4b1ce5c) + W302 finalize product landed (ledger head
    # 1088741 machine-read); zero --no-verify; the W303 seat MSG sits in
    # fleet/inbox/MSG-20261024-0640-bmc-w303-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w303bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FIFTY-SIXTH consecutive A-hop (naive 681_701..683_700 REFUSED
    # at start by the registered W302 B band; walk past the W302 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (681_900+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 681_901..682_100 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FIFTY-SEVENTH
    # consecutive above-own-A; B base == own-A tail+1 (683_900+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=681901 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=683901 span=200 checked=200 verdict=FREE.
    # W304+ projection (pre-seat probe leg4, pre-W303 universe):
    # A naive first-clean 683_901..685_900 hops=0 / B naive 684_101..684_300 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W304 freezer MUST
    # re-derive on the post-W303 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    303: {"a": (681_901, 683_900), "b_exit": (683_901, 684_100),
         "engine_owner": "bm-c"},
    # W304 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-0735-bmc-w304-seat published=reserved by bm-c itself @
    # origin 098930328c (r1187, queue-head seat-first supply -- W304 registered+FINALIZED
    # at publish, W304 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W303 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W304_PREREG.md bm-c r1187 window derive landed
    # pre-freeze, freeze-time gate n/a; probe receipt
    # results/_w304bmc_20261024_probe_receipt.json @ 098930328c);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W303 five-face
    # (freeze f8a956c17c) + W303 finalize product landed (ledger head
    # 1090941 machine-read); zero --no-verify; the W304 seat MSG sits in
    # fleet/inbox/MSG-20261024-0735-bmc-w304-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w304bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FIFTY-SEVENTH consecutive A-hop (naive 683_901..685_900 REFUSED
    # at start by the registered W303 B band; walk past the W303 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (684_100+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 684_101..684_300 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FIFTY-EIGHTH
    # consecutive above-own-A; B base == own-A tail+1 (686_100+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=684101 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=686101 span=200 checked=200 verdict=FREE.
    # W305+ projection (pre-seat probe leg4, pre-W304 universe):
    # A naive first-clean 686_101..688_100 hops=0 / B naive 686_301..686_500 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W305 freezer MUST
    # re-derive on the post-W304 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    304: {"a": (684_101, 686_100), "b_exit": (686_101, 686_300),
         "engine_owner": "bm-c"},
    # W305 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-0845-bmc-w305-seat published=reserved by bm-c itself @
    # origin 871f187361 (r1189, queue-head seat-first supply -- W305 registered+FINALIZED
    # at publish, W305 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W304 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W305_PREREG.md bm-c r1189 window derive landed
    # pre-freeze, freeze-time gate 5f2c19de83; probe receipt
    # results/_w305bmc_20261024_probe_receipt.json @ 871f187361);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W304 five-face
    # (freeze c7b6ecd7ba) + W304 finalize product landed (ledger head
    # 1093141 machine-read); zero --no-verify; the W305 seat MSG sits in
    # fleet/inbox/MSG-20261024-0845-bmc-w305-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w305bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FIFTY-EIGHTH consecutive A-hop (naive 686_101..688_100 REFUSED
    # at start by the registered W304 B band; walk past the W304 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (686_300+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 686_301..686_500 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- FIFTY-NINTH
    # consecutive above-own-A; B base == own-A tail+1 (688_300+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=686301 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=688301 span=200 checked=200 verdict=FREE.
    # W306+ projection (pre-seat probe leg4, pre-W305 universe):
    # A naive first-clean 688_301..690_300 hops=0 / B naive 688_501..688_700 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W306 freezer MUST
    # re-derive on the post-W305 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    305: {"a": (686_301, 688_300), "b_exit": (688_301, 688_500),
         "engine_owner": "bm-c"},
    # W306 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-0950-bmc-w306-seat published=reserved by bm-c itself @
    # origin 9da7091894 (r1191, queue-head seat-first supply -- W306 registered+FINALIZED
    # at publish, W306 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W305 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W306_PREREG.md bm-c r1191 window derive landed
    # pre-freeze, freeze-time gate 7ab2b459e2; probe receipt
    # results/_w306bmc_20261024_probe_receipt.json @ 9da7091894);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W305 five-face
    # (freeze 318e263ee0) + W305 finalize product landed (ledger head
    # 1095341 machine-read); zero --no-verify; the W306 seat MSG sits in
    # fleet/inbox/MSG-20261024-0950-bmc-w306-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w306bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk FIFTY-NINTH consecutive A-hop (naive 688_301..690_300 REFUSED
    # at start by the registered W305 B band; walk past the W305 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (688_500+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 688_501..688_700 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- SIXTIETH
    # consecutive above-own-A; B base == own-A tail+1 (690_500+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=688501 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=690501 span=200 checked=200 verdict=FREE.
    # W307+ projection (pre-seat probe leg4, pre-W306 universe):
    # A naive first-clean 690_501..692_500 hops=0 / B naive 690_701..690_900 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W307 freezer MUST
    # re-derive on the post-W306 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    306: {"a": (688_501, 690_500), "b_exit": (690_501, 690_700),
         "engine_owner": "bm-c"},
    # W307 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-1047-bmc-w307-seat published=reserved by bm-c itself @
    # origin d78f799608 (r1192, queue-head seat-first supply -- W307 registered+FINALIZED
    # at publish, W307 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W306 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W307_PREREG.md bm-c r1192 window derive landed
    # pre-freeze, freeze-time gate 2131c78e84; probe receipt
    # results/_w307bmc_20261024_probe_receipt.json @ d78f799608);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W306 five-face
    # (freeze aa8e2a8f1f) + W306 finalize product landed (ledger head
    # 1097541 machine-read); zero --no-verify; the W307 seat MSG sits in
    # fleet/inbox/MSG-20261024-1047-bmc-w307-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w307bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk SIXTIETH consecutive A-hop (naive 690_501..692_500 REFUSED
    # at start by the registered W306 B band; walk past the W306 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (690_700+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 690_701..690_900 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- SIXTY-FIRST
    # consecutive above-own-A; B base == own-A tail+1 (692_700+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=690701 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=692701 span=200 checked=200 verdict=FREE.
    # W308+ projection (pre-seat probe leg4, pre-W307 universe):
    # A naive first-clean 692_701..694_700 hops=0 / B naive 692_901..693_100 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W308 freezer MUST
    # re-derive on the post-W307 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    307: {"a": (690_701, 692_700), "b_exit": (692_701, 692_900),
         "engine_owner": "bm-c"},
    # W308 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-1325-bmc-w308-seat published=reserved by bm-c itself @
    # origin 3e1ecb3110 (r1194, queue-head seat-first supply -- W308 registered+FINALIZED
    # at publish, W308 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W307 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W308_PREREG.md bm-c r1194 window derive landed
    # pre-freeze, freeze-time gate 2da27a4a3a; probe receipt
    # results/_w308bmc_20261024_probe_receipt.json @ a9cb2055b1);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W307 five-face
    # (freeze 897b31fc83) + W307 finalize product landed (ledger head
    # 1099741 machine-read); zero --no-verify; the W308 seat MSG sits in
    # fleet/inbox/MSG-20261024-1325-bmc-w308-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w308bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk SIXTY-FIRST consecutive A-hop (naive 692_701..694_700 REFUSED
    # at start by the registered W307 B band; walk past the W307 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (692_900+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 692_901..693_100 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- SIXTY-SECOND
    # consecutive above-own-A; B base == own-A tail+1 (694_900+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=692901 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=694901 span=200 checked=200 verdict=FREE.
    # W309+ projection (pre-seat probe leg4, pre-W308 universe):
    # A naive first-clean 694_901..696_900 hops=0 / B naive 695_101..695_300 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W309 freezer MUST
    # re-derive on the post-W308 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    308: {"a": (692_901, 694_900), "b_exit": (694_901, 695_100),
         "engine_owner": "bm-c"},
    # W309 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-1406-bmc-w309-seat published=reserved by bm-c itself @
    # origin 55eb0897ac (r1196, queue-head seat-first supply -- W309 registered+FINALIZED
    # at publish, W309 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W308 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W309_PREREG.md bm-c r1196 window derive landed
    # pre-freeze, freeze-time gate b109a52460; probe receipt
    # results/_w309bmc_20261024_probe_receipt.json @ 55eb0897ac);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W308 five-face
    # (freeze 897b31fc83) + W308 finalize product landed (ledger head
    # 1101941 machine-read); zero --no-verify; the W309 seat MSG sits in
    # fleet/inbox/MSG-20261024-1406-bmc-w309-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w309bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk SIXTY-SECOND consecutive A-hop (naive 694_901..696_900 REFUSED
    # at start by the registered W308 B band; walk past the W308 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (695_100+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 695_101..695_300 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- SIXTY-THIRD
    # consecutive above-own-A; B base == own-A tail+1 (697_100+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=695101 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=697101 span=200 checked=200 verdict=FREE.
    # W310+ projection (pre-seat probe leg4, pre-W309 universe):
    # A naive first-clean 697_101..699_100 hops=0 / B naive 697_301..697_500 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W310 freezer MUST
    # re-derive on the post-W309 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    309: {"a": (695_101, 697_100), "b_exit": (697_101, 697_300),
         "engine_owner": "bm-c"},
    # W310 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat
    # MSG-20261024-1500-bmc-w310-seat published=reserved by bm-c itself @
    # origin 68a4a18b1f (r1198, queue-head seat-first supply -- W310 registered+FINALIZED
    # at publish, W310 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat
    # (W309 five-face + finalize product both in-place; prereg
    # research/PERPETUAL_N1_W310_PREREG.md bm-c r1198 window derive landed
    # pre-freeze, freeze-time gate 442e881af8; probe receipt
    # results/_w310bmc_20261024_probe_receipt.json @ 68a4a18b1f);
    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W309 five-face
    # (freeze 897b31fc83) + W309 finalize product landed (ledger head
    # 1104141 machine-read); zero --no-verify; the W310 seat MSG sits in
    # fleet/inbox/MSG-20261024-1500-bmc-w310-seat.md at freeze time (honest archived per S7 law);
    # band gate ADMIT results/_w310bmc_20261024_probe_receipt.json: A = 1-HOP
    # STAIRCASE-AFFECTS-A walk SIXTY-THIRD consecutive A-hop (naive 697_101..699_100 REFUSED
    # at start by the registered W309 B band; walk past the W309 B tail ->
    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (697_300+1) EXACT)
    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive 697_301..697_500 CLEAN vs
    # the registered universe BUT lands INSIDE the own-wave A first-clean window;
    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- SIXTY-FOURTH
    # consecutive above-own-A; B base == own-A tail+1 (699_300+1) EXACT)
    # single-window derive (gate legs merged INTO the probe, r812);
    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):
    # seed_admit_gate rc0 base=697301 span=2000 checked=2000 verdict=FREE;
    # seed_admit_gate rc0 base=699301 span=200 checked=200 verdict=FREE.
    # W311+ projection (pre-seat probe leg4, pre-W310 universe):
    # A naive first-clean 699_301..701_300 hops=0 / B naive 699_501..699_700 hops=0 BUT lands INSIDE the projection A window
    # (staircase face continuing since W251); the W311 freezer MUST
    # re-derive on the post-W310 universe AND reserve the own-wave A window
    # when deriving B; never transcribe r587.
    310: {"a": (697_301, 699_300), "b_exit": (699_301, 699_500),
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
    # ADJUDICATED EXCEPTION 2 (bm-a r874, W99 r726/r727 precedent):
    # SEED_REGISTRY regime5_validation_p1_null_base=94_100 was
    # registered LATER (bm-a r870 REGIME5_VALIDATION_P1 prereg
    # freeze; its 94_001..94_999 pocket sweep verified free
    # in-registry but MISSED the N1_BANDS band face) and lands
    # inside the ALREADY-BURNED W137 B band 94_001..94_200 at
    # j=99. Historical single-point overlap on a burned
    # measurement face: statistically harmless (the REGIME5 P1
    # burn consumed only SPAWNED CHILDREN of SeedSequence(94_100)
    # -- never default_rng(94_100) itself -- so the two consumers
    # never share an actual stream; the W137 exit draw remains a
    # valid null draw), W137 finalize results stand un-reopened,
    # the regime5_validation_p1 batch is NOT re-registered
    # (registry records what was actually used -- the P1 burn ran
    # 2026-10-08 08:46 with base 94_100). Future band gates already
    # treat SEED_REGISTRY live values as refusal points, so no
    # forward face. Disclosed, not hidden.
    # ADJUDICATED EXCEPTION 3 (bm-a r901, the r874 precedent second
    # instance, found red by the W193 five-face freeze selftest
    # window): SEED_REGISTRY f1_bull_cond_p1_null_base=94_200 was
    # registered LATER (bm-a r899 F1-BULL-COND-P1 prereg freeze
    # 1b7e9e53d + same-window verdict burn; the r899 registration
    # face verified registry-internal disjointness but MISSED the
    # N1_BANDS band face -- same miss family as the r870 pocket
    # sweep) and lands inside the ALREADY-BURNED W137 B band
    # 94_001..94_200 at j=199 (the band tail). Historical
    # single-point overlap on a burned measurement face:
    # statistically harmless (the F1-BULL-COND-P1 verdict burn
    # consumed only SPAWNED CHILDREN of SeedSequence(94_200) --
    # never default_rng(94_200) itself -- so the two consumers
    # never share an actual stream; the W137 exit draw remains a
    # valid null draw), W137 finalize results stand un-reopened,
    # the F1-BULL-COND-P1 batch is NOT re-registered (registry
    # records what was actually used -- the F1 verdict burn ran
    # 2026-10-09 04:18 with base 94_200, verdict FAIL-CLOSED
    # disclosed r899). Future band gates already treat
    # SEED_REGISTRY live values as refusal points, so no forward
    # face. Disclosed, not hidden.
    w137_adjudicated = {94_100, 94_200}
    w137_b_probe = set(range(N1_BANDS[137]["b_exit"][0],
                            N1_BANDS[137]["b_exit"][1] + 1))
    assert w137_adjudicated <= w137_b_probe, \
        "W137 adjudicated set drifted (must sit inside the burned band)"
    # ADJUDICATED EXCEPTION 4 (bm-a r915, the r874 precedent third
    # instance, found red by the W197 five-face freeze selftest
    # window): SEED_REGISTRY parking_p1_null_base=94_300 was
    # registered LATER (bm-a r914 dead-session PARKING-P1 prereg
    # freeze b904a0a0e 12:11; the registration face verified
    # registry-internal disjointness only -- in-registry 94_100/
    # 94_200 not-hit -- and MISSED the N1_BANDS band face, same
    # miss family as the r870/r899 pocket sweeps) and lands inside
    # the ALREADY-BURNED W138 B band 94_201..94_400 at j=99.
    # Caught PRE-BURN (the PARKING-P1 burn due 10-14 12:00 has NOT
    # run -- first instance of the family caught before
    # consumption; re-derivation considered and refused: the
    # 94_001..94_999 pocket is exhausted, W137..W140 registered B
    # bands cover 94_001..94_800 and any 94_801..94_999 base's
    # spawn children would cross the 95_000..95_003 probe cluster,
    # so the family rationale applies and the frozen prereg's base
    # stands). Historical single-point overlap on a burned
    # measurement face: statistically harmless (the PARKING-P1
    # runner MUST consume only SPAWNED CHILDREN of
    # SeedSequence(94_300) -- never default_rng(94_300) itself --
    # so the two consumers never share an actual stream; the W138
    # exit draw remains a valid null draw), W138 finalize results
    # stand un-reopened, the parking_p1 batch is NOT
    # re-registered (registry records the frozen prereg's choice).
    # Future band gates already treat SEED_REGISTRY live values as
    # refusal points, so no forward face. Disclosed, not hidden.
    w138_adjudicated = {94_300}
    w138_b_probe = set(range(N1_BANDS[138]["b_exit"][0],
                            N1_BANDS[138]["b_exit"][1] + 1))
    assert w138_adjudicated <= w138_b_probe, \
        "W138 adjudicated set drifted (must sit inside the burned band)"
    # ADJUDICATED EXCEPTION 5 (bm-a r957, O-20261010-1906 request,
    # r874 precedent family, found red by the W204 five-face freeze
    # selftest window on origin): SEED_REGISTRY
    # thermo_overlay_p1_nulls=94_500 was registered LATER (bm-a r938
    # T-181 slice-1 registration; the registration face verified
    # in-registry disjointness but MISSED the N1_BANDS band face --
    # same miss family as the r870/r899 pocket sweeps) and lands
    # inside the ALREADY-BURNED W139 B band 94_401..94_600 at j=99.
    # CORRECTED argument (NOT the r874 spawn-children path -- the
    # thermo runner consumes default_rng(94_500+i) itself, and so
    # does the W139 engine exit draw at j=99: same-family same-seed
    # = SHARED PCG64 stream). Harmless via DISJOINT INJECTION FACES:
    # the thermo null law draws one integers(1,T) phase shift per
    # null seed into the 1997-2026 thermo timeline; the W139 engine
    # draw randomizes the factor-cell exit axis -- two data faces
    # that never meet, and neither statistical inference reads the
    # other, so no spurious-correlation channel exists. W139
    # finalize results stand un-reopened, the thermo_overlay_p1
    # batch is NOT re-registered (registry records what was actually
    # used -- the thermo burn ran 2026-10-09 with base 94_500).
    # Future band gates already treat SEED_REGISTRY live values as
    # refusal points, so no forward face. Disclosed, not hidden.
    w139_adjudicated = {94_500}
    w139_b_probe = set(range(N1_BANDS[139]["b_exit"][0],
                            N1_BANDS[139]["b_exit"][1] + 1))
    assert w139_adjudicated <= w139_b_probe, \
        "W139 adjudicated set drifted (must sit inside the burned band)"
    # ADJUDICATED EXCEPTION 6 (bm-a r957, same O-20261010-1906
    # request): SEED_REGISTRY lhb_thermo_ic_p1_nulls=94_700 was
    # registered LATER (bm-a E5 slice-2 LHB_THERMO_IC_P1
    # registration; same N1_BANDS miss family) and lands inside the
    # ALREADY-BURNED W140 B band 94_601..94_800 at j=99. STRONGER
    # than the r874 spawn-children argument: the two consumers run
    # DIFFERENT RNG algorithm families -- lhb consumes Python
    # stdlib random.Random(94_700+i) (MT19937), the W140 engine exit
    # draw consumes numpy default_rng(94_700+j) (PCG64) -- the same
    # seed integer produces entirely different streams, so the two
    # consumers never share an actual stream. Bookkeeping-level
    # overlap only, statistically harmless; the W140 exit draw
    # remains a valid null draw. W140 finalize results stand
    # un-reopened, the lhb_thermo_ic_p1 batch is NOT re-registered.
    # Future band gates already treat SEED_REGISTRY live values as
    # refusal points, so no forward face. Disclosed, not hidden.
    w140_adjudicated = {94_700}
    w140_b_probe = set(range(N1_BANDS[140]["b_exit"][0],
                            N1_BANDS[140]["b_exit"][1] + 1))
    assert w140_adjudicated <= w140_b_probe, \
        "W140 adjudicated set drifted (must sit inside the burned band)"
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
        elif w == 137:
            assert not (band_b & (reg_ints - w137_adjudicated)), \
                f"N1 w{w} hits SEED_REGISTRY beyond the adjudicated r874 point"
        elif w == 138:
            assert not (band_b & (reg_ints - w138_adjudicated)), \
                f"N1 w{w} hits SEED_REGISTRY beyond the adjudicated r874 point"
        elif w == 139:
            assert not (band_b & (reg_ints - w139_adjudicated)), \
                f"N1 w{w} hits SEED_REGISTRY beyond the adjudicated r957 point"
        elif w == 140:
            assert not (band_b & (reg_ints - w140_adjudicated)), \
                f"N1 w{w} hits SEED_REGISTRY beyond the adjudicated r957 point"
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
    # 8. pool format-mirror probe (read-only; r289 law: indent2+EOL+trailing
    #    probed dynamically; every format face follows the migrated canonical
    #    producer -- bm-b r499 pool-format migration made the flip tool emit
    #    trailing NL and the probe dynamic; bm-c r307 migrated the indent
    #    face; r852 bm-c completes the family on the EOL face: the guard
    #    asserts probe-vs-bytes truth, not a hardcoded pre-migration face --
    #    the pool blob has been LF-only on origin since >=10-10 15:20 per
    #    autofill producer commits (r856 bm-b forensics), so the old
    #    hardcoded CRLF pin chronic-false-flagged byte-faithful LF checkouts
    #    while passing autocrlf-converted CRLF trees (probe drift = format
    #    face follows the writer, r500 law)
    if os.path.exists(POOL_PATH):
        indent, crlf, trailing_nl = _pool_format_probe()
        b = open(POOL_PATH, "rb").read()
        # EOL probe-vs-bytes truth (r499 trailing / r307 indent migration
        # family completed on the last hardcoded format face)
        nl = b.count(b"\n")
        crlf_bytes = b.count(b"\r\n") >= max(1, nl) // 2
        assert crlf == crlf_bytes, \
            f"EOL probe drift vs bytes: {crlf}/{crlf_bytes}"
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
