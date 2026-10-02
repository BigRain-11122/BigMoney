    # --- W109 materializer face (r587 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-b's
    #     thirty-seventh owned per machine-derive (engine_owner==bm-b
    #     rows 36 + candidate); wave 109 = first free number after
    #     the REGISTERED W108 row (bm-c r378 freeze 3a3c51b73) --
    #     SINGLE STATE zero seat gap (W2..W108 all registered).
    #     Seat published=reserved MSG-20261002-1817-bmb rev.B pushed
    #     to origin 99e29877c BEFORE this freeze, r565 law; rev.B =
    #     first-draft B projection corrected pre-push (bm-c W108
    #     mid-window advance, refusal point 61_000 own-probe
    #     confirmed, zero prior visibility). NINETY-NINTH engine
    #     wave BY MACHINE-DERIVE (engine_owner rows 98 + candidate;
    #     gate leg0 machine output governs per r359 law). W103
    #     finalize LANDED (chain head 591,148, K=224,520, bm-b r586
    #     one-pass) + FIVE in-flight upstream seats W104 bm-a + W105
    #     bm-c + W106 bm-b + W107 bm-a + W108 bm-c
    #     registered-unfinalized -- FAIL-CLOSED r307 at run time.
    #     ADMIT receipt results/_r587bmb_w109_band_gate.py; not a
    #     re-pick (R250: W109 bands were never assigned).
    _set_wave(109)
    try:
        assert WAVE_CONFIGS[109]["a_seed_base"] == pf.N1_BANDS[109]["a"][0], \
            "W109 A band drift vs law mirror"
        assert WAVE_CONFIGS[109]["b_exit_seed_base"] == \
            pf.N1_BANDS[109]["b_exit"][0], "W109 B band drift vs law mirror"
        assert WAVE_CONFIGS[109].get("engine_owner") == \
            pf.N1_BANDS[109].get("engine_owner") == "bm-b", \
            "W109 engine_owner drift (law mirror parity)"
        w109_a = {A_SEED_BASE + j for j in range(A_N)}
        w109_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w109_a & w109_b), "W109 A/B band overlap"
        assert not (w109_a & reg_ints) and not (w109_b & reg_ints), \
            "W109 hits SEED_REGISTRY"
        for nm, band in (("A", w109_a), ("B", w109_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W109 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W109 {nm} hits W1"
            assert not (band & probes), f"W109 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[103] == {"a": (249_004, 251_003),
                                    "b_exit": (59_401, 59_600),
                                    "engine_owner": "bm-b"}, \
            "registered W103 row parity drift (r307; bm-b r584)"
        assert pf.N1_BANDS[104] == {"a": (251_004, 253_003),
                                    "b_exit": (59_601, 59_800),
                                    "engine_owner": "bm-a"}, \
            "registered W104 row parity drift (r307; bm-a r586 union)"
        assert pf.N1_BANDS[105] == {"a": (253_004, 255_003),
                                    "b_exit": (60_001, 60_200),
                                    "engine_owner": "bm-c"}, \
            "registered W105 row parity drift (r307; bm-c r376)"
        assert pf.N1_BANDS[106] == {"a": (255_004, 257_003),
                                    "b_exit": (60_201, 60_400),
                                    "engine_owner": "bm-b"}, \
            "registered W106 row parity drift (r307; bm-b r585)"
        assert pf.N1_BANDS[107] == {"a": (257_004, 259_003),
                                    "b_exit": (60_401, 60_600),
                                    "engine_owner": "bm-a"}, \
            "registered W107 row parity drift (r307; bm-a r587)"
        assert pf.N1_BANDS[108] == {"a": (259_004, 261_003),
                                    "b_exit": (60_601, 60_800),
                                    "engine_owner": "bm-c"}, \
            "registered W108 row parity drift (r307; bm-c r378)"
        # prior-wave disjointness W2..W108 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 109):
            assert not (w109_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W109 A hits W{wprev}"
            assert not (w109_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W109 B hits W{wprev}"
        n3r1_used109 = set(range(70_000, 70_006))
        assert not (w109_a & n3r1_used109) and not (w109_b & n3r1_used109), \
            "W109 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w109_a & lfc_actual12) and not (w109_b & lfc_actual12), \
            "W109 bands must clear the lfc actual draw range"
        assert not (w109_a & options_actual12) and \
            not (w109_b & options_actual12), \
            "W109 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W109 row, r587): A arithmetic
        # continuation from the registered W108 tails, zero skips;
        # B value-collision jump (W5 precedent family).
        assert WAVE_CONFIGS[109]["a_seed_base"] == 261_004 == 261_003 + 1, (
            "W109 A must be the arithmetic continuation past the W108 "
            "registered A band tail")
        arith_a109 = set(range(261_004, 263_004))
        assert not (arith_a109 & reg_ints), \
            "W109 A window must be CLEAN (arithmetic ADMIT face)"
        assert WAVE_CONFIGS[109]["b_exit_seed_base"] == 61_001, (
            "W109 B must be the first clean window past the refusal point")
        arith_b109_refused = set(range(60_801, 61_001))
        assert arith_b109_refused & reg_ints, \
            ("W109 B refusal fact missing: arithmetic window 60_801..61_000 "
            "must hit SEED_REGISTRY (wild_route_s1=61_000)")
        assert 61_000 in reg_ints, \
            "W109 B refusal point 61_000 (wild_route_s1) missing from registry"
        arith_b109 = set(range(61_001, 61_201))
        assert not (arith_b109 & reg_ints), \
            "W109 B window must be CLEAN (value-collision jump ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W109-SHARD-0",
                                          "n1w109-0of12"), "W109 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W109-SHARD-11",
                                           "n1w109-11of12")
        assert SHARD_DIR.endswith("n1_w109") and OUT.endswith(
            "n1_w109_results.json"), "W109 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 109):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \
                f"W109 shard dir collides with W{wprev}"
        # W109 finalize cumulative deps: W17..W103 outputs ALL PRESENT
        # (landed chain head 591,148 = W103 bm-b r586; W104/W105/W106/
        # W107/W108 registered with finalizes NOT landed -- in-flight
        # upstream seats, honest note; the finalize merge loop derives
        # the wave set from registry keys at run time and stays
        # FAIL-CLOSED, r307 law).
        for _depw in range(17, 104):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \
                f"W109 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 109 composes; wave 15 excluded by
        # design; SINGLE STATE (W2..W108 all registered -- no
        # two-state seat disclosure needed at this freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 109) == \
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \
            [w for w in range(16, 109)], \
            "W109 prior-wave set must derive from registry keys (no 15; " \
            "W2..W108 registered single state)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W109_PREREG.md")), \
            "W109 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)