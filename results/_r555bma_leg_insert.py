"""r555 helper: insert the W47 materializer selftest leg after the W46 leg."""
PATH = 'scripts/perpetual_faces_n1.py'
data = open(PATH, 'rb').read().decode('utf-8')
nl = '\r\n' if data.count('\r\n') > 0 else '\n'
print('EOL:', repr(nl))

anchor = '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'
i = data.find(anchor)
assert i > 0, 'T-141 leg anchor not found'

LEG = '''    # --- W47 materializer face (r555 bm-a freeze, own-series law
    #     O-20261001-2355 sec.2 -- bm-a's ELEVENTH owned wave after
    #     W12/W18/W21/W24/W27/W30/W33/W35/W44/W45). Zero-gap relay
    #     after the W46 FULL CLOSEOUT (bm-c r348 same-window: freeze
    #     -> 12/12 no-restart burn -> finalize one-pass K=99,120,
    #     ledger 465,748 -- the chain FULLY caught up W1..W46 at
    #     this freeze, zero pending upstream face). bm-a engine =
    #     TICK architecture (r535 law -- no resident instance; the
    #     next tick's fresh process re-reads the live tree and sees
    #     the W47 row; ignition proof = product growth within 2
    #     ticks per r325 law). Wave 47 = first free number after
    #     W46's landed claim; origin slot vacancy machine-checked
    #     (r511 tail-lock). A = no-skip arithmetic continuation
    #     (137_004 == W46 A end 137_003 + 1) per the W46 row W47+
    #     WARNING projection CLEAN, machine-derived at this freeze;
    #     B = FORCED SKIP-OVER family (W39-B/W43-B): the arithmetic
    #     +200 tail 44_801..45_000 is machine-REFUSED
    #     (SEED_REGISTRY['pc_l2_ic'] = 45_000 falls inside) -- r307
    #     tail-law scan-forward packs at the first free 200-window
    #     45_001..45_200 (results/_r555bma_w47_band_gate.py ADMIT
    #     receipt; NOT a re-pick -- R250: W47 bands never
    #     assigned).
    _set_wave(47)
    try:
        assert WAVE_CONFIGS[47]["a_seed_base"] == pf.N1_BANDS[47]["a"][0], \\
            "W47 A band drift vs law mirror"
        assert WAVE_CONFIGS[47]["b_exit_seed_base"] == \\
            pf.N1_BANDS[47]["b_exit"][0], "W47 B band drift vs law mirror"
        assert WAVE_CONFIGS[47].get("engine_owner") == \\
            pf.N1_BANDS[47].get("engine_owner") == "bm-a", \\
            "W47 engine_owner drift (law mirror parity)"
        w47_a = {A_SEED_BASE + j for j in range(A_N)}
        w47_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w47_a & w47_b), "W47 A/B band overlap"
        assert not (w47_a & reg_ints) and not (w47_b & reg_ints), \\
            "W47 hits SEED_REGISTRY"
        for nm, band in (("A", w47_a), ("B", w47_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W47 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W47 {nm} hits W1"
            assert not (band & probes), f"W47 {nm} hits probe seeds"
        # prior-wave disjointness incl. W44/W45/W46 (all finalizes
        # landed at this freeze -- band registration is the disjointness
        # face; W45 bm-a r554 K=96,920 ledger 463,548; W46 bm-c r348
        # K=99,120 ledger 465,748).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46):
            assert not (w47_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W47 A hits W{wprev}"
            assert not (w47_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W47 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W47 bands must clear it.
        n3r1_used47 = set(range(70_000, 70_006))
        assert not (w47_a & n3r1_used47) and not (w47_b & n3r1_used47), \\
            "W47 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w47_a & lfc_actual12) and not (w47_b & lfc_actual12), \\
            "W47 bands must clear the lfc actual draw range"
        assert not (w47_a & options_actual12) and \\
            not (w47_b & options_actual12), \\
            "W47 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W47 row, r555): A no-skip arithmetic
        # continuation exactly as the W46 row W47+ WARNING projected,
        # machine-derived at this freeze (r535 law --
        # results/_r555bma_w47_band_gate.py leg1-A CLEAN); B FORCED
        # SKIP-OVER past SEED_REGISTRY['pc_l2_ic']=45_000 (leg1-B
        # refusal facts [45000]; leg2-B first clean window
        # 45_001..45_200; NOT a free pick -- R250: W47 bands never
        # assigned).
        assert WAVE_CONFIGS[47]["a_seed_base"] == 137_004 == 137_003 + 1, \\
            "W47 A must start at the W46 A end + 1 (arithmetic continuation)"
        assert 45_000 in reg_ints, \\
            "W47-B refusal fact drift (SEED_REGISTRY['pc_l2_ic']=45_000 " \\
            "must be live)"
        assert WAVE_CONFIGS[47]["b_exit_seed_base"] == 45_001 == 45_000 + 1, \\
            "W47 B must start past the refusal point 45_000 (r307 " \\
            "scan-forward first clean window -- the arithmetic tail " \\
            "44_801..45_000 is machine-REFUSED, W39-B/W43-B family)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W47-SHARD-0", \\
                                          "n1w47-0of12"), "W47 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W47-SHARD-11", \\
                                           "n1w47-11of12")
        assert SHARD_DIR.endswith("n1_w47") and OUT.endswith(
            "n1_w47_results.json"), "W47 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W47 SHARD_DIR collides with W{wprev}"
        # finalize cumulative deps: W17..W46 outputs ALL PRESENT
        # (every prior wave finalized at this freeze -- the chain
        # fully caught up W1..W46, net ledger head 465,748; zero
        # in-flight upstream face, static asserts legal for the
        # full set -- r307 two-state law: no in-flight face here).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W47 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 47 (no 15; W46 registered
        # by the bm-c r348 freeze, finalize landed 04:15 same-day).
        assert sorted(w for w in WAVE_CONFIGS if w < 47) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46], \\
            "W47 prior-wave set must derive from registry keys (no 15, incl. 46)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''

# normalize the leg to the file's EOL
leg_nl = LEG.replace('\n', nl)
new = data[:i] + leg_nl + data[i:]
open(PATH, 'wb').write(new.encode('utf-8'))
print('W47 leg inserted before T-141 block at char', i)
