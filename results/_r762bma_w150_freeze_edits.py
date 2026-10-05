# -*- coding: utf-8 -*-
"""r762 bm-a W150 freeze edits: four insertions (pf N1_BANDS[150] row +
n1 WAVE_CONFIGS[150] + n1 W150 materializer leg + n1 PASS snippet).
EOL-adaptive (r370 law: files are CRLF-dominant -- blocks written CRLF);
needle count==1 (r745); insert-after-last-registered-row + post-anchor
content checks (r560); anchor = predecessor full lines, no whole-anchor
backfill (r580/r581); AST gate after every edit batch (r580/r581).
prereg block built by programmatic double-quote wrapping with the tail
paren KEPT on the last item (r761 Rev.B lesson: s[:-1] strip drops the
content's closing paren -- wrap keeps s intact)."""
import ast
import io

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
CRLF = "\r\n"


def edit(path, pairs):
    src = io.open(path, encoding="utf-8", newline="").read()
    for i, (old, new) in enumerate(pairs):
        n = src.count(old)
        assert n == 1, f"{path}: needle {i} count={n} expect=1: {old[:80]!r}"
        src = src.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="").write(src)
    ast.parse(io.open(path, encoding="utf-8", newline="").read())
    print(f"{path}: {len(pairs)} edits landed, AST gate PASS")


# --- edit 1: pf.py N1_BANDS[150] row (insert after registered W149 row) --------
a1 = ('    149: {"a": (342_604, 344_603), "b_exit": (344_604, 344_803),\r\n'
      '         "engine_owner": "bm-a"},\r\n'
      '}')
w150_row = CRLF.join([
    '    # W150 (bm-a r762 freeze, seat MSG-2026-10-06-070x-bma-w150-seat',
    '    # pushed to origin bb33022de pre-freeze r565 law (r762 pre-seat',
    '    # push; same-window self-ack inbox->processed move 860d529f3 r762;',
    '    # payload = seat MSG + pre-seat probe + probe receipt + W149',
    '    # finalize products; deletion-set EMPTY);',
    '    # band gate ADMIT results/_r762bma_w150_band_gate.py: A = FIRST-CLEAN',
    '    # past the registered W149 B band (arithmetic continuation',
    '    # 344_604..346_603 REFUSED at its own start by the W149 B band',
    '    # 344_604..344_803, exactly as the W149 seat leg4 + r761 gate leg3',
    '    # projections both anticipated; honest forward walk hops=1 ->',
    '    # 344_804..346_803, non-rotational r587 forward-monotone walk;',
    '    # A base == prior-wave B tail+1 (344_803+1) machine-checkable --',
    '    # A-hops-prior-B staircase ninth instance, E36 card);',
    '    # B = FIRST-CLEAN past the own-wave A window (arithmetic',
    '    # continuation 344_804..345_003 CLEAN on the registered universe',
    '    # but lands INSIDE the W150 A band window -- same-freeze mutual',
    '    # exclusion (W141 precedent, leg2 law) -- the walk with the',
    '    # own-wave A window reserved jumps to 346_804 -> 346_804..347_003,',
    '    # hops=1, non-rotational r587 forward-monotone walk; B base ==',
    '    # own-wave A tail+1 (346_803+1) machine-checkable);',
    '    # dual-window derive parity with pre-seat probe',
    '    # results/_r762bma_w150_probe_receipt.json; scan face =',
    '    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1',
    '    # used-seed band + probe cluster 95_000..95_003 + cross-face',
    '    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/',
    '    # N2-W15 probe points.',
    '    # W151+ projection (gate-derived r762): A first-clean',
    '    # 346_804..348_803 CLEAN hops=0 / B first-clean 347_004..347_203',
    '    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the',
    '    # registered W150 B band 346_804..347_003 will refuse the naive',
    '    # W151 A window; W151 freezer MUST re-derive on the post-W150',
    '    # universe AND reserve the own-wave A window when deriving B',
    '    # (W141 precedent, same-freeze mutual exclusion, leg2 law,',
    '    # E36 staircase card; never transcribe r587).',
    '    # NOT a re-pick (R250: W150 bands were never assigned).',
    '    150: {"a": (344_804, 346_803), "b_exit": (346_804, 347_003),',
    '         "engine_owner": "bm-a"},',
])
r1 = ('    149: {"a": (342_604, 344_603), "b_exit": (344_604, 344_803),\r\n'
      '         "engine_owner": "bm-a"},\r\n' + w150_row + '\r\n}')
edit(PF, [(a1, r1)])

# --- edit 2: n1.py WAVE_CONFIGS[150] (prereg block built programmatically) ----
PRE = [
    "research/PERPETUAL_N1_W150_PREREG.md (wave-level frozen ",
    "pre-run; design = frozen v1 null calibration verbatim, ",
    "new seed bands only; ONE HUNDRED-AND-FORTIETH ENGINE-OWNED WAVE ",
    "BY MACHINE-DERIVE (engine_owner rows 139 + candidate), ",
    "own-series continuation per O-20261001-2355 sec.2 (first-free-",
    "number law after the REGISTERED W149 row bm-a r761 freeze ",
    "0cef02a00, SINGLE STATE zero seat gap W2..W149 all ",
    "registered; W149 finalize landed same-window r762, ledger ",
    "head 723,811, merged pool K=325,720; seat published=reserved ",
    "MSG-2026-10-06-070x-bma-w150-seat PUSHED to origin bb33022de ",
    "BEFORE this freeze per r565 early-visibility law (payload = ",
    "seat MSG + pre-seat probe + probe receipt; deletion-set ",
    "EMPTY; same-window self-ack inbox->processed move 860d529f3 ",
    "r762; pre-seat probe and freeze-window band-gate runs ",
    "derive identical, no fork face), ",
    "engine_owner=bm-a, wave 150: ",
    "A = FIRST-CLEAN past the registered W149 B band (the ",
    "arithmetic continuation 344_604..346_603 is REFUSED at its ",
    "own start by the W149 B band 344_604..344_803, exactly as ",
    "the W149 seat leg4 + r761 gate leg3 projection notes ",
    "anticipated; honest forward walk hops=1 -> 344_804..346_803; ",
    "A base == prior-wave B tail+1 machine-checkable = ",
    "A-hops-prior-B staircase ninth instance, E36 card; ",
    "non-rotational r587 forward-monotone walk) + B = ",
    "FIRST-CLEAN past the own-wave A window (the arithmetic ",
    "continuation 344_804..345_003 is CLEAN on the registered ",
    "universe but lands INSIDE the W150 A band window -- ",
    "same-freeze mutual exclusion, W141 precedent, leg2 law ",
    "-- the walk with the own-wave A window reserved jumps ",
    "to 346_804, first-clean 346_804..347_003 hops=1, ",
    "non-rotational r587 forward-monotone walk; B base == ",
    "own-wave A tail+1 machine-checkable; cross-window ",
    "convergence with the W149 seat leg4 + r761 gate leg3 ",
    "projection notes re-derived -- both MANDATORY notes ",
    "honored (post-W149 universe re-derive + own-wave A ",
    "reservation); ADMIT receipt ",
    "results/_r762bma_w150_band_gate.py; W151+ projection ",
    "per this window gate: A first-clean 346_804..348_803 ",
    "CLEAN / B first-clean 347_004..347_203 CLEAN -- naive ",
    "B lands INSIDE the naive A window and the registered ",
    "W150 B band 346_804..347_003 will refuse the naive ",
    "W151 A window; W151 freezer MUST re-derive on the ",
    "post-W150 universe AND reserve the own-wave A window ",
    "when deriving B (W141 precedent, leg2 law, E36 ",
    "staircase card); W1..W149 finalize ALL LANDED (W149 ",
    "finalize one-pass bm-a r762, net chain head 723,811, ",
    "merged pool K=325,720) -- ZERO in-flight upstream ",
    "seats, clean finalize chain precondition -- finalize ",
    "merge loop still derives the wave set from registry ",
    "keys at run time, FAIL-CLOSED r307 always on)",
]
prereg_lines = ['                       150: {"batch": "PERPETUAL-N1-W150",']
for i, s in enumerate(PRE):
    q = '"' + s + '"'
    if i == 0:
        prefix = '                            "prereg": ('
    else:
        prefix = '                                       '
    if i == len(PRE) - 1:
        # r761 Rev.B lesson: keep the content's closing paren intact
        q = '"' + s + '"),'
    prereg_lines.append(prefix + q)
prereg_lines += [
    '                            "a_seed_base": 344_804,        # law sec.4 W150 A: 344_804..346_803 (FIRST-CLEAN past the registered W149 B band; arithmetic 344_604..346_603 REFUSED at own start by the W149 B band; hops=1; A-hops-prior-B staircase ninth instance, E36 card)',
    '                            "b_exit_seed_base": 346_804,   # law sec.4 W150 B: 346_804..347_003 (FIRST-CLEAN past the own-wave A window; arithmetic 344_804..345_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
    '                            "shard_subdir": "n1_w150", "out_name": "n1_w150_results.json",',
    '                            "engine_owner": "bm-a"},',
    '                       }',
]
a2 = ('"shard_subdir": "n1_w149", "out_name": "n1_w149_results.json",\r\n'
      '                            "engine_owner": "bm-a"},\r\n'
      '                       }')
r2 = ('"shard_subdir": "n1_w149", "out_name": "n1_w149_results.json",\r\n'
      '                            "engine_owner": "bm-a"},\r\n' +
      CRLF.join(prereg_lines))

# --- edit 3: n1.py W150 materializer leg ----------------------------------------
a3 = '    finally:\r\n        _set_wave(2)\r\n    # --- T-141 s2 lane face'
LEG = CRLF.join([
    '    # --- W150 materializer face (r762 bm-a freeze, own-series law',
    '    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a\'s',
    '    #     sixty-sixth owned per machine-derive (engine_owner==bm-a',
    '    #     rows 65 + candidate); wave 150 = first free number after',
    '    #     the REGISTERED W149 row (bm-a r761 freeze 0cef02a00) --',
    '    #     SINGLE STATE zero seat gap (W2..W149 all registered). Seat',
    '    #     published=reserved MSG-2026-10-06-070x-bma-w150-seat pushed',
    '    #     to origin bb33022de BEFORE this freeze, r565 law (payload',
    '    #     = seat MSG + pre-seat probe + probe receipt; deletion-set',
    '    #     EMPTY; same-window self-ack inbox->processed move',
    '    #     860d529f3 r762; zero behind-signal, zero --no-verify). ONE',
    '    #     HUNDRED-AND-FORTIETH engine wave BY MACHINE-DERIVE',
    '    #     (engine_owner rows 139 + candidate; gate leg0 machine',
    '    #     output governs per r359 law). W1..W149 finalize ALL',
    '    #     LANDED (net chain head 723,811, K=325,720 merged pool;',
    '    #     W149 finalize one-pass bm-a r762) -- ZERO in-flight',
    '    #     upstream seats, clean finalize chain precondition; the',
    '    #     finalize merge loop still derives the wave set from',
    '    #     registry keys at run time, FAIL-CLOSED r307 always on.',
    '    #     ADMIT receipt results/_r762bma_w150_band_gate.py; banned',
    '    #     gate ADMIT 0; not a re-pick (R250: W150 bands were never',
    '    #     assigned).',
    '    _set_wave(150)',
    '    try:',
    '        assert WAVE_CONFIGS[150]["a_seed_base"] == pf.N1_BANDS[150]["a"][0], \\',
    '            "W150 A band drift vs law mirror"',
    '        assert WAVE_CONFIGS[150]["b_exit_seed_base"] == \\',
    '            pf.N1_BANDS[150]["b_exit"][0], "W150 B band drift vs law mirror"',
    '        assert WAVE_CONFIGS[150].get("engine_owner") == \\',
    '            pf.N1_BANDS[150].get("engine_owner") == "bm-a", \\',
    '            "W150 engine_owner drift (law mirror parity)"',
    '        w150_a = {A_SEED_BASE + j for j in range(A_N)}',
    '        w150_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}',
    '        assert not (w150_a & w150_b), "W150 A/B band overlap"',
    '        assert not (w150_a & reg_ints) and not (w150_b & reg_ints), \\',
    '            "W150 hits SEED_REGISTRY"',
    '        for nm, band in (("A", w150_a), ("B", w150_b)):',
    '            assert not (band & v1_a) and not (band & v1_b), f"W150 {nm} hits v1"',
    '            assert not (band & w1_a) and not (band & w1_b), f"W150 {nm} hits W1"',
    '            assert not (band & probes), f"W150 {nm} hits probe seeds"',
    '        # registered row parity (r307 pinned constants, recent estate)',
    '        assert pf.N1_BANDS[134] == {"a": (311_004, 313_003),',
    '                                    "b_exit": (69_302, 69_501),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W134 row parity drift (r307; bm-a r739)"',
    '        assert pf.N1_BANDS[135] == {"a": (313_004, 315_003),',
    '                                    "b_exit": (69_502, 69_701),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W135 row parity drift (r307; bm-a r740)"',
    '        assert pf.N1_BANDS[136] == {"a": (315_004, 317_003),',
    '                                    "b_exit": (69_702, 69_901),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W136 row parity drift (r307; bm-a r741)"',
    '        assert pf.N1_BANDS[137] == {"a": (317_004, 319_003),',
    '                                    "b_exit": (94_001, 94_200),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W137 row parity drift (r307; bm-a r742)"',
    '        assert pf.N1_BANDS[138] == {"a": (319_004, 321_003),',
    '                                    "b_exit": (94_201, 94_400),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W138 row parity drift (r307; bm-a r743)"',
    '        assert pf.N1_BANDS[139] == {"a": (321_004, 323_003),',
    '                                    "b_exit": (94_401, 94_600),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W139 row parity drift (r307; bm-a r744)"',
    '        assert pf.N1_BANDS[140] == {"a": (323_004, 325_003),',
    '                                    "b_exit": (94_601, 94_800),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W140 row parity drift (r307; bm-a r745)"',
    '        assert pf.N1_BANDS[141] == {"a": (325_004, 327_003),',
    '                                    "b_exit": (327_004, 327_203),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W141 row parity drift (r307; bm-a r747)"',
    '        assert pf.N1_BANDS[142] == {"a": (327_204, 329_203),',
    '                                    "b_exit": (329_204, 329_403),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W142 row parity drift (r307; bm-a r748)"',
    '        assert pf.N1_BANDS[143] == {"a": (329_404, 331_403),',
    '                                    "b_exit": (331_404, 331_603),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W143 row parity drift (r307; bm-a r750)"',
    '        assert pf.N1_BANDS[144] == {"a": (331_604, 333_603),',
    '                                    "b_exit": (333_604, 333_803),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W144 row parity drift (r307; bm-a r752)"',
    '        assert pf.N1_BANDS[145] == {"a": (333_804, 335_803),',
    '                                    "b_exit": (335_804, 336_003),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W145 row parity drift (r307; bm-a r754)"',
    '        assert pf.N1_BANDS[146] == {"a": (336_004, 338_003),',
    '                                    "b_exit": (338_004, 338_203),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W146 row parity drift (r307; bm-a r755)"',
    '        assert pf.N1_BANDS[147] == {"a": (338_204, 340_203),',
    '                                    "b_exit": (340_204, 340_403),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W147 row parity drift (r307; bm-a r757)"',
    '        assert pf.N1_BANDS[148] == {"a": (340_404, 342_403),',
    '                                    "b_exit": (342_404, 342_603),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W148 row parity drift (r307; bm-a r759)"',
    '        assert pf.N1_BANDS[149] == {"a": (342_604, 344_603),',
    '                                    "b_exit": (344_604, 344_803),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W149 row parity drift (r307; bm-a r761)"',
    '        # prior-wave disjointness W2..W149 (single state: all',
    '        # registered, dynamic registry derive, r511 law)',
    '        for wprev in sorted(w for w in WAVE_CONFIGS if w < 150):',
    '            assert not (w150_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
    '                                 for j in range(A_N)}), f"W150 A hits W{wprev}"',
    '            assert not (w150_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
    '                                  for j in range(B_N)}), f"W150 B hits W{wprev}"',
    '        n3r1_used150 = set(range(70_000, 70_006))',
    '        assert not (w150_a & n3r1_used150) and not (w150_b & n3r1_used150), \\',
    '            "W150 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
    '        assert not (w150_a & lfc_actual12) and not (w150_b & lfc_actual12), \\',
    '            "W150 bands must clear the lfc actual draw range"',
    '        assert not (w150_a & options_actual12) and \\',
    '            not (w150_b & options_actual12), \\',
    '            "W150 bands must clear the options_wave2 actual draw range"',
    '        # band facts (law sec.4 W150 row, r762): A = FIRST-CLEAN past',
    '        # the registered W149 B band (the arithmetic continuation',
    '        # 344_604..346_603 is REFUSED at its own start by the W149',
    '        # B band 344_604..344_803, exactly as the W149 seat leg4 +',
    '        # r761 gate leg3 projection notes anticipated; the honest',
    '        # forward walk hops=1 lands 344_804..346_803; A base ==',
    '        # prior-wave B tail+1 (344_803+1) machine-checkable --',
    '        # A-hops-prior-B staircase ninth instance, E36 card;',
    '        # non-rotational r587 forward-monotone walk);',
    '        # B = FIRST-CLEAN past the own-wave A window (the arithmetic',
    '        # continuation 344_804..345_003 is CLEAN on the registered',
    '        # universe but lands INSIDE the W150 A band window --',
    '        # same-freeze mutual exclusion (W141 precedent, leg2 law) --',
    '        # the walk with the own-wave A window reserved jumps to',
    '        # 346_804 and lands 346_804..347_003, hops=1, non-rotational',
    '        # r587 forward-monotone walk; B base == own-wave A tail+1',
    '        # (346_803+1) machine-checkable; cross-window convergence',
    '        # with the W149 seat leg4 + r761 gate leg3 projection notes',
    '        # -- both MANDATORY notes honored (post-W149 universe',
    '        # re-derive + own-wave A reservation when deriving B); seat',
    '        # MSG-070x tail, re-derived).',
    '        assert WAVE_CONFIGS[150]["a_seed_base"] == 344_804 == 344_803 + 1, (',
    '            "W150 A must be the first-clean window past the registered "',
    '            "W149 B band tail 344_803+1 (arithmetic continuation "',
    '            "344_604..346_603 REFUSED at its own start by the W149 B "',
    '            "band 344_604..344_803, exactly as the W149 seat leg4 + "',
    '            "r761 gate leg3 projection notes anticipated; honest "',
    '            "forward walk hops=1; A base == prior-wave B tail+1 "',
    '            "machine-checkable = A-hops-prior-B staircase ninth "',
    '            "instance, E36 card)")',
    '        arith_a150 = set(range(344_804, 346_804))',
    '        assert not (arith_a150 & reg_ints), \\',
    '            "W150 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
    '        assert WAVE_CONFIGS[150]["b_exit_seed_base"] == 346_804 == 346_803 + 1, (',
    '            "W150 B must be the first-clean window past the own-wave A "',
    '            "band tail 346_803+1 (arithmetic continuation "',
    '            "344_804..345_003 CLEAN on the registered universe but "',
    '            "lands INSIDE the W150 A band window; same-freeze mutual "',
    '            "exclusion (W141 precedent, leg2 law) -- the walk with the "',
    '            "own-wave A window reserved jumps to 346_804, first-clean "',
    '            "hops=1, non-rotational r587 forward-monotone walk; B "',
    '            "base == own-wave A tail+1 machine-checkable)")',
    '        arith_b150 = set(range(346_804, 347_004))',
    '        assert not (arith_b150 & reg_ints), \\',
    '            "W150 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
    '        assert not (arith_b150 & arith_a150), \\',
    '            "W150 A/B same-freeze mutual exclusion (B hops past own A)"',
    '        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W150-SHARD-0",',
    '                                          "n1w150-0of12"), "W150 entry identity"',
    '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W150-SHARD-11",',
    '                                           "n1w150-11of12")',
    '        assert SHARD_DIR.endswith("n1_w150") and OUT.endswith(',
    '            "n1_w150_results.json"), "W150 path drift"',
    '        for wprev in sorted(w for w in WAVE_CONFIGS if w < 150):',
    '            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(',
    '                PATHS.results_dir, "p2cal_ext",',
    '                WAVE_CONFIGS[wprev]["shard_subdir"])), \\',
    '                f"W150 shard dir collides with W{wprev}"',
    '        # W150 finalize cumulative deps: W17..W149 outputs ALL PRESENT',
    '        # (landed net chain head 723,811 = W149 bm-a r762 one-pass --',
    '        # ZERO in-flight upstream seats, clean precondition freeze',
    '        # window; the finalize merge loop derives the wave set from',
    '        # registry keys at run time and stays FAIL-CLOSED, r307',
    '        # two-state law).',
    '        for _depw in range(17, 150):',
    '            assert os.path.exists(os.path.join(',
    '                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\',
    '                f"W150 finalize cumulative dep (W{_depw} output) missing"',
    '        # finalize wave-set derivation face (r511 derive law): every',
    '        # registered wave below 150 composes; wave 15 excluded by',
    '        # design; SINGLE STATE (W2..W149 all registered -- no',
    '        # two-state seat disclosure needed at this freeze).',
    '        assert sorted(w for w in WAVE_CONFIGS if w < 150) == \\',
    '            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\',
    '            [w for w in range(16, 150)], \\',
    '            "W150 prior-wave set must derive from registry keys (no 15; " \\',
    '            "W2..W149 registered single state)"',
    '        assert os.path.exists(os.path.join(',
    '            PATHS.root, "research", "PERPETUAL_N1_W150_PREREG.md")), \\',
    '            "W150 per-wave prereg missing (materializer requirement)"',
    '        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"',
    '    finally:',
    '        _set_wave(2)',
])
r3 = ('    finally:\r\n        _set_wave(2)\r\n' + LEG + CRLF +
      '    # --- T-141 s2 lane face')

# --- edit 4: n1.py PASS snippet --------------------------------------------------
a4 = ('"results/_r761bma_w149_band_gate.py, law sec.4 W149 row, "\r\n'
      '          "r761 bm-a] "\r\n'
      '          "+ T-141 s2 "')
snip = CRLF.join([
    '          "+ W150 materializer face [same guard set, dep=W17..W149 "',
    '          "outputs ALL PRESENT (landed net chain head 723,811 = "',
    '          "W149 bm-a r762 one-pass, K=325,720 merged pool; ZERO "',
    '          "in-flight upstream seats), ONE HUNDRED-AND-FORTIETH "',
    '          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 139 "',
    '          "+ candidate) bm-a\'s sixty-sixth owned claim per "',
    '          "machine-derive (engine_owner==bm-a rows 65 + candidate), "',
    '          "A=FIRST-CLEAN past the registered W149 B band (staircase "',
    '          "ninth instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
    '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
    '          "mutual exclusion, hops=1), ADMIT receipt "',
    '          "results/_r762bma_w150_band_gate.py, law sec.4 W150 row, "',
    '          "r762 bm-a] "',
])
r4 = ('"results/_r761bma_w149_band_gate.py, law sec.4 W149 row, "\r\n'
      '          "r761 bm-a] "\r\n' + snip + CRLF + '          "+ T-141 s2 "')

edit(N1, [(a2, r2), (a3, r3), (a4, r4)])

# --- post-edit structural assertions --------------------------------------------
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 150 and len(pf.N1_BANDS) == 148, \
    "pf N1_BANDS row-count drift after W150 insert"
assert pf.N1_BANDS[150] == {"a": (344_804, 346_803),
                            "b_exit": (346_804, 347_003),
                            "engine_owner": "bm-a"}, "W150 row face drift"
assert pf.N1_BANDS[149] == {"a": (342_604, 344_603),
                            "b_exit": (344_604, 344_803),
                            "engine_owner": "bm-a"}, "W149 row survived (r560 no-replace law)"
print("post-edit structural assertions PASS: N1_BANDS 148 rows tail W150, "
      "W149 row intact")
