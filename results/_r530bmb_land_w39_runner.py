from pathlib import Path

# r500 byte-level lesson (LF-only targets): byte-level patch with
# explicit LF normalization. Re-lands: WAVE_CONFIGS[39] + selftest W39
# materializer face + selftest prose, all in scripts/perpetual_faces_n1.py.

p = Path(r"scripts/perpetual_faces_n1.py")
data = p.read_bytes().decode("utf-8")

old1 = '''                       "shard_subdir": "n1_w38", "out_name": "n1_w38_results.json",
                       "engine_owner": "bm-b"},
                 }'''
new1 = '''                       "shard_subdir": "n1_w38", "out_name": "n1_w38_results.json",
                       "engine_owner": "bm-b"},
                  # W39 (r530 bm-b, own-series continuation per O-20261001-2355
                  # sec.2 -- bm-b's THIRTEENTH owned wave; follows the W38
                  # 12/12 burn this same window -> zero-gap relay. Wave 39 =
                  # first free number after W38's landed claim (bm-b r529).
                  # SIDES INDEPENDENTLY ADJUDICATED per the W38 row's W39+
                  # WARNING: A tail arithmetic continuation no skip
                  # (121_004..123_003 == W38 A end + 1); B tail FORCED SKIP
                  # past 43_000 (arithmetic 42_801..43_000 refused -- tail
                  # point 43_000 = SEED_REGISTRY p4_folk hit, r307 tail-law
                  # precedent, jump to first clean window 43_001..43_200,
                  # forced not a free pick). Machine-verified at prereg time
                  # (results/_r530bmb_w39_band_gate.py ADMIT receipt vs the
                  # 36-row pre-W39 table + SEED_REGISTRY values + probe-seed
                  # cluster 95_000..95_003 r335 discovery leg + N3-R1
                  # used-seed band 70_000..70_005 MSG-183x r529 mandatory
                  # leg; B-side refusal facts [43_000 p4_folk] machine-
                  # verified; origin slot vacancy machine-checked).
                  # TWENTY-EIGHTH ENGINE-OWNED WAVE, engine_owner=bm-b
                  # (local queue, no pool entry). NOT a re-pick (R250: W39
                  # bands were never assigned).
                  39: {"batch": "PERPETUAL-N1-W39",
                       "prereg": ("research/PERPETUAL_N1_W39_PREREG.md (wave-level frozen "
                                  "pre-run; design = frozen v1 null calibration verbatim, "
                                  "new seed bands only; TWENTY-EIGHTH ENGINE-OWNED WAVE, "
                                  "own-series continuation per O-20261001-2355 sec.2 "
                                  "(seat system terminated, first-free-number law), "
                                  "engine_owner=bm-b, A tail arithmetic continuation from "
                                  "the registered W38 row no skip, B tail forced skip past "
                                  "43_000 p4_folk to first clean window per r307 precedent)"),
                       "a_seed_base": 121_004,        # law sec.4 W39 A: 121_004..123_003 (arithmetic)
                       "b_exit_seed_base": 43_001,    # law sec.4 W39 B: 43_001..43_200 (forced skip past 43_000)
                       "shard_subdir": "n1_w39", "out_name": "n1_w39_results.json",
                       "engine_owner": "bm-b"},
                 }'''

old2 = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
new2 = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W39 materializer face (r530 bm-b freeze, own-series law
    #     O-20261001-2355 sec.2 -- bm-b's THIRTEENTH owned wave after
    #     W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/W36/W38; zero-gap relay
    #     after the W38 12/12 burn this same window) ---------------
    _set_wave(39)
    try:
        assert WAVE_CONFIGS[39]["a_seed_base"] == pf.N1_BANDS[39]["a"][0], \\
            "W39 A band drift vs law mirror"
        assert WAVE_CONFIGS[39]["b_exit_seed_base"] == \\
            pf.N1_BANDS[39]["b_exit"][0], "W39 B band drift vs law mirror"
        assert WAVE_CONFIGS[39].get("engine_owner") == \\
            pf.N1_BANDS[39].get("engine_owner") == "bm-b", \\
            "W39 engine_owner drift (law mirror parity)"
        w39_a = {A_SEED_BASE + j for j in range(A_N)}
        w39_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w39_a & w39_b), "W39 A/B band overlap"
        assert not (w39_a & reg_ints) and not (w39_b & reg_ints), \\
            "W39 hits SEED_REGISTRY"
        for nm, band in (("A", w39_a), ("B", w39_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W39 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W39 {nm} hits W1"
            assert not (band & probes), f"W39 {nm} hits probe seeds"
        # prior-wave disjointness incl. W37 (bm-c, 12/12 burned, finalize
        # pending at this freeze per r543 chain order) and W38 (bm-b,
        # 12/12 burned this same window -- in-flight coexists by band
        # disjointness per r531 law).
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
        assert not (w39_a & n3r1_used39) and not (w39_b & n3r1_used39), \\
            "W39 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w39_a & lfc_actual12) and not (w39_b & lfc_actual12), \\
            "W39 bands must clear the lfc actual draw range"
        assert not (w39_a & options_actual12) and \\
            not (w39_b & options_actual12), \\
            "W39 bands must clear the options_wave2 actual draw range"
        # band-landing facts (law sec.4 W39 row, r530): sides independently
        # adjudicated per the W38 row's W39+ WARNING -- A tail arithmetic
        # continuation (candidate start == W38 A end + 1, no skip); B tail
        # FORCED SKIP past 43_000 (the refused arithmetic window is
        # 42_801..43_000 with the single registry-point hit 43_000 =
        # SEED_REGISTRY p4_folk; the jump to the first clean window past ALL
        # reserved faces is forced not a free pick, r307 tail-law precedent,
        # machine-verified by the r530 gate refusal facts).
        assert WAVE_CONFIGS[39]["a_seed_base"] == 121_004 == 121_003 + 1, \\
            "W39 A must start at the W38 A end + 1 (arithmetic continuation)"
        assert WAVE_CONFIGS[39]["b_exit_seed_base"] == 43_001 == 43_000 + 1, \\
            "W39 B must start past the forced-skip point 43_000 (r307)"
        assert 43_000 in reg_ints, \\
            "W39 B forced-skip refusal fact 43_000 missing from SEED_REGISTRY"
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
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W39 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W39_PREREG.md")), \\
            "W39 per-wave prereg missing (materializer requirement)"
        # W39 finalize cumulative deps: W17..W36 outputs ALL PRESENT
        # (W34 finalize r528 bm-b K=72,720; W35 finalize bm-a r546 K=74,920;
        # W36 finalize bm-b r529 K=77,120 -- net ledger head 441,740); W37
        # (bm-c, 12/12 burned, finalize pending at this freeze per r543
        # chain order) and W38 (bm-b, 12/12 burned this same window,
        # finalize chain-blocked on the W37 block) -- the dep pin carries
        # the two-state honest note per the r541 W30 precedent (finalize
        # runtime composes every registry key below 39 = FAIL-CLOSED
        # honest wait for the W37/W38 outputs once they land).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W39 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 39 (no 15; W37/W38
        # in-flight = runtime FAIL-CLOSED guard).
        assert sorted(w for w in WAVE_CONFIGS if w < 39) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38], \\
            "W39 prior-wave set must derive from registry keys (no 15, incl. 37+38)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''

old3 = '''          "relay after the W36 full closeout this same window, wave "
          "38 = first free number after W37's claim), r529 bm-b] "
          "+ T-141 s2 "'''
new3 = '''          "relay after the W36 full closeout this same window, wave "
          "38 = first free number after W37's claim), r529 bm-b] "
          "+ W39 materializer face [same guard set, dep=W17..W36 ALL "
          "present + W37/W38 registered-in-flight two-state deps "
          "(W37 bm-c 12/12 burned finalize pending per r543 chain "
          "order; W38 bm-b 12/12 burned this same window -- finalize "
          "runtime FAIL-CLOSED composes every registry key below 39), "
          "SIDES INDEPENDENTLY ADJUDICATED per law sec.4 W39 row: "
          "A=arithmetic continuation 121_004..123_003 zero skip, "
          "B=FORCED SKIP past 43_000 (SEED_REGISTRY p4_folk, r307 "
          "tail-law precedent, first clean window 43_001..43_200 "
          "machine-derived), engine_owner=bm-b per engine de-throttle "
          "law O-20261001-2355 sec.2 own-continuous-series (zero-gap "
          "relay after the W38 12/12 burn, wave 39 = first free "
          "number after W38's claim), r530 bm-b] "
          "+ T-141 s2 "'''

for tag, old, new in ((1, old1, new1), (2, old2, new2), (3, old3, new3)):
    old = old.replace("\r\n", "\n")
    new = new.replace("\r\n", "\n")
    assert data.count(old) == 1, f"anchor{tag} not unique"
    data = data.replace(old, new)

p.write_bytes(data.encode("utf-8"))
print("WAVE_CONFIGS[39] + selftest W39 face + prose landed (byte-level LF)")
