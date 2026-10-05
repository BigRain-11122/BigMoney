# -*- coding: utf-8 -*-
"""r761 bm-a W149 freeze edits: four insertions (pf N1_BANDS[149] row +
n1 WAVE_CONFIGS[149] + n1 W149 materializer leg + n1 PASS snippet).
EOL-adaptive (r370 law: files are CRLF-dominant -- blocks written CRLF);
needle count==1 (r745); insert-after-last-registered-row + post-anchor
content checks (r560); anchor = predecessor full lines, no whole-anchor
backfill (r580/r581); AST gate after every edit batch (r580/r581).
Rev.B: first run aborted at the n1 AST gate (prereg continuation lines
missing their closing double-quotes); both scripts rolled back pristine
per r370 before this rerun; prereg block now built by programmatic
double-quote wrapping (immune to the missing-quote bug class)."""
import ast
import io

PF = r"scripts\perpetual_faces.py"
N1 = r"scripts\perpetual_faces_n1.py"
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


# --- edit 1: pf.py N1_BANDS[149] row (insert after registered W148 row) --------
a1 = ('    148: {"a": (340_404, 342_403), "b_exit": (342_404, 342_603),\r\n'
      '         "engine_owner": "bm-a"},\r\n'
      '}')
w149_row = CRLF.join([
    '    # W149 (bm-a r761 freeze, seat MSG-2026-10-06-060x-bma-w149-seat',
    '    # pushed to origin 47da9310c pre-freeze r565 law (r760 pre-seat',
    '    # push; same-window self-ack inbox->processed move 684177ba0 r760;',
    '    # payload = seat MSG + pre-seat probe + probe receipt; deletion-set',
    '    # EMPTY);',
    '    # band gate ADMIT results/_r761bma_w149_band_gate.py: A = FIRST-CLEAN',
    '    # past the registered W148 B band (arithmetic continuation',
    '    # 342_404..344_403 REFUSED at its own start by the W148 B band',
    '    # 342_404..342_603, exactly as the W148 seat leg4 + r759 gate leg3',
    '    # projections both anticipated; honest forward walk hops=1 ->',
    '    # 342_604..344_603, non-rotational r587 forward-monotone walk;',
    '    # A base == prior-wave B tail+1 (342_603+1) machine-checkable --',
    '    # A-hops-prior-B staircase eighth instance, E36 card);',
    '    # B = FIRST-CLEAN past the own-wave A window (arithmetic',
    '    # continuation 342_604..342_803 CLEAN on the registered universe',
    '    # but lands INSIDE the W149 A band window -- same-freeze mutual',
    '    # exclusion (W141 precedent, leg2 law) -- the walk with the',
    '    # own-wave A window reserved jumps to 344_604 -> 344_604..344_803,',
    '    # hops=1, non-rotational r587 forward-monotone walk; B base ==',
    '    # own-wave A tail+1 (344_603+1) machine-checkable);',
    '    # dual-window derive parity with pre-seat probe',
    '    # results/_r760bma_w149_probe_receipt.json; scan face =',
    '    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1',
    '    # used-seed band + probe cluster 95_000..95_003 + cross-face',
    '    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/',
    '    # N2-W15 probe points.',
    '    # W150+ projection (gate-derived r761): A first-clean',
    '    # 344_604..346_603 CLEAN hops=0 / B first-clean 344_804..345_003',
    '    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the',
    '    # registered W149 B band 344_604..344_803 will refuse the naive',
    '    # W150 A window; W150 freezer MUST re-derive on the post-W149',
    '    # universe AND reserve the own-wave A window when deriving B',
    '    # (W141 precedent, same-freeze mutual exclusion, leg2 law,',
    '    # E36 staircase card; never transcribe r587).',
    '    # NOT a re-pick (R250: W149 bands were never assigned).',
    '    149: {"a": (342_604, 344_603), "b_exit": (344_604, 344_803),',
    '         "engine_owner": "bm-a"},',
])
r1 = ('    148: {"a": (340_404, 342_403), "b_exit": (342_404, 342_603),\r\n'
      '         "engine_owner": "bm-a"},\r\n' + w149_row + '\r\n}')
edit(PF, [(a1, r1)])

# --- edit 2: n1.py WAVE_CONFIGS[149] (prereg block built programmatically) ------
PRE = [
    "research/PERPETUAL_N1_W149_PREREG.md (wave-level frozen ",
    "pre-run; design = frozen v1 null calibration verbatim, ",
    "new seed bands only; ONE HUNDRED-AND-THIRTY-NINTH ENGINE-OWNED WAVE ",
    "BY MACHINE-DERIVE (engine_owner rows 138 + candidate), ",
    "own-series continuation per O-20261001-2355 sec.2 (first-free-",
    "number law after the REGISTERED W148 row bm-a r759 freeze ",
    "92c5ab03c, SINGLE STATE zero seat gap W2..W148 all ",
    "registered; W148 finalize landed same-window r760, ledger ",
    "head 721,611, merged pool K=323,520; seat published=reserved ",
    "MSG-2026-10-06-060x-bma-w149-seat PUSHED to origin 47da9310c ",
    "BEFORE this freeze per r565 early-visibility law (payload = ",
    "seat MSG + pre-seat probe + probe receipt; deletion-set ",
    "EMPTY; same-window self-ack inbox->processed move 684177ba0 ",
    "r760; pre-seat probe and freeze-window band-gate runs ",
    "derive identical, no fork face), ",
    "engine_owner=bm-a, wave 149: ",
    "A = FIRST-CLEAN past the registered W148 B band (the ",
    "arithmetic continuation 342_404..344_403 is REFUSED at its ",
    "own start by the W148 B band 342_404..342_603, exactly as ",
    "the W148 seat leg4 + r759 gate leg3 projection notes ",
    "anticipated; honest forward walk hops=1 -> 342_604..344_603; ",
    "A base == prior-wave B tail+1 machine-checkable = ",
    "A-hops-prior-B staircase eighth instance, E36 card; ",
    "non-rotational r587 forward-monotone walk) + B = ",
    "FIRST-CLEAN past the own-wave A window (the arithmetic ",
    "continuation 342_604..342_803 is CLEAN on the registered ",
    "universe but lands INSIDE the W149 A band window -- ",
    "same-freeze mutual exclusion, W141 precedent, leg2 law ",
    "-- the walk with the own-wave A window reserved jumps ",
    "to 344_604, first-clean 344_604..344_803 hops=1, ",
    "non-rotational r587 forward-monotone walk; B base == ",
    "own-wave A tail+1 machine-checkable; cross-window ",
    "convergence with the W148 seat leg4 + r759 gate leg3 ",
    "projection notes re-derived -- both MANDATORY notes ",
    "honored (post-W148 universe re-derive + own-wave A ",
    "reservation); ADMIT receipt ",
    "results/_r761bma_w149_band_gate.py; W150+ projection ",
    "per this window gate: A first-clean 344_604..346_603 ",
    "CLEAN / B first-clean 344_804..345_003 CLEAN -- naive ",
    "B lands INSIDE the naive A window and the registered ",
    "W149 B band 344_604..344_803 will refuse the naive ",
    "W150 A window; W150 freezer MUST re-derive on the ",
    "post-W149 universe AND reserve the own-wave A window ",
    "when deriving B (W141 precedent, leg2 law, E36 ",
    "staircase card); W1..W148 finalize ALL LANDED (W148 ",
    "finalize one-pass bm-a r760, net chain head 721,611, ",
    "merged pool K=323,520) -- ZERO in-flight upstream ",
    "seats, clean finalize chain precondition -- finalize ",
    "merge loop still derives the wave set from registry ",
    "keys at run time, FAIL-CLOSED r307 always on)",
]
prereg_lines = ['                       149: {"batch": "PERPETUAL-N1-W149",']
for i, s in enumerate(PRE):
    q = '"' + s + '"'
    if i == 0:
        prefix = '                            "prereg": ('
    else:
        prefix = '                                       '
    if i == len(PRE) - 1:
        q = '"' + s[:-1] + '"),'
    prereg_lines.append(prefix + q)
prereg_lines += [
    '                            "a_seed_base": 342_604,        # law sec.4 W149 A: 342_604..344_603 (FIRST-CLEAN past the registered W148 B band; arithmetic 342_404..344_403 REFUSED at own start by the W148 B band; hops=1; A-hops-prior-B staircase eighth instance, E36 card)',
    '                            "b_exit_seed_base": 344_604,   # law sec.4 W149 B: 344_604..344_803 (FIRST-CLEAN past the own-wave A window; arithmetic 342_604..342_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
    '                            "shard_subdir": "n1_w149", "out_name": "n1_w149_results.json",',
    '                            "engine_owner": "bm-a"},',
    '                       }',
]
a2 = ('"shard_subdir": "n1_w148", "out_name": "n1_w148_results.json",\r\n'
      '                            "engine_owner": "bm-a"},\r\n'
      '                       }')
r2 = ('"shard_subdir": "n1_w148", "out_name": "n1_w148_results.json",\r\n'
      '                            "engine_owner": "bm-a"},\r\n' +
      CRLF.join(prereg_lines))

# --- edit 3: n1.py W149 materializer leg ----------------------------------------
a3 = '    finally:\r\n        _set_wave(2)\r\n    # --- T-141 s2 lane face'
LEG = CRLF.join([
    '    # --- W149 materializer face (r761 bm-a freeze, own-series law',
    '    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a\'s',
    '    #     sixty-fifth owned per machine-derive (engine_owner==bm-a',
    '    #     rows 64 + candidate); wave 149 = first free number after',
    '    #     the REGISTERED W148 row (bm-a r759 freeze 92c5ab03c) --',
    '    #     SINGLE STATE zero seat gap (W2..W148 all registered). Seat',
    '    #     published=reserved MSG-2026-10-06-060x-bma-w149-seat pushed',
    '    #     to origin 47da9310c BEFORE this freeze, r565 law (payload',
    '    #     = seat MSG + pre-seat probe + probe receipt; deletion-set',
    '    #     EMPTY; same-window self-ack inbox->processed move',
    '    #     684177ba0 r760; zero behind-signal, zero --no-verify). ONE',
    '    #     HUNDRED-AND-THIRTY-NINTH engine wave BY MACHINE-DERIVE',
    '    #     (engine_owner rows 138 + candidate; gate leg0 machine',
    '    #     output governs per r359 law). W1..W148 finalize ALL',
    '    #     LANDED (net chain head 721,611, K=323,520 merged pool;',
    '    #     W148 finalize one-pass bm-a r760) -- ZERO in-flight',
    '    #     upstream seats, clean finalize chain precondition; the',
    '    #     finalize merge loop still derives the wave set from',
    '    #     registry keys at run time, FAIL-CLOSED r307 always on.',
    '    #     ADMIT receipt results/_r761bma_w149_band_gate.py; banned',
    '    #     gate ADMIT 0; not a re-pick (R250: W149 bands were never',
    '    #     assigned).',
    '    _set_wave(149)',
    '    try:',
    '        assert WAVE_CONFIGS[149]["a_seed_base"] == pf.N1_BANDS[149]["a"][0], \\',
    '            "W149 A band drift vs law mirror"',
    '        assert WAVE_CONFIGS[149]["b_exit_seed_base"] == \\',
    '            pf.N1_BANDS[149]["b_exit"][0], "W149 B band drift vs law mirror"',
    '        assert WAVE_CONFIGS[149].get("engine_owner") == \\',
    '            pf.N1_BANDS[149].get("engine_owner") == "bm-a", \\',
    '            "W149 engine_owner drift (law mirror parity)"',
    '        w149_a = {A_SEED_BASE + j for j in range(A_N)}',
    '        w149_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}',
    '        assert not (w149_a & w149_b), "W149 A/B band overlap"',
    '        assert not (w149_a & reg_ints) and not (w149_b & reg_ints), \\',
    '            "W149 hits SEED_REGISTRY"',
    '        for nm, band in (("A", w149_a), ("B", w149_b)):',
    '            assert not (band & v1_a) and not (band & v1_b), f"W149 {nm} hits v1"',
    '            assert not (band & w1_a) and not (band & w1_b), f"W149 {nm} hits W1"',
    '            assert not (band & probes), f"W149 {nm} hits probe seeds"',
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
    '        # prior-wave disjointness W2..W148 (single state: all',
    '        # registered, dynamic registry derive, r511 law)',
    '        for wprev in sorted(w for w in WAVE_CONFIGS if w < 149):',
    '            assert not (w149_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
    '                                 for j in range(A_N)}), f"W149 A hits W{wprev}"',
    '            assert not (w149_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
    '                                  for j in range(B_N)}), f"W149 B hits W{wprev}"',
    '        n3r1_used149 = set(range(70_000, 70_006))',
    '        assert not (w149_a & n3r1_used149) and not (w149_b & n3r1_used149), \\',
    '            "W149 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
    '        assert not (w149_a & lfc_actual12) and not (w149_b & lfc_actual12), \\',
    '            "W149 bands must clear the lfc actual draw range"',
    '        assert not (w149_a & options_actual12) and \\',
    '            not (w149_b & options_actual12), \\',
    '            "W149 bands must clear the options_wave2 actual draw range"',
    '        # band facts (law sec.4 W149 row, r761): A = FIRST-CLEAN past',
    '        # the registered W148 B band (the arithmetic continuation',
    '        # 342_404..344_403 is REFUSED at its own start by the W148',
    '        # B band 342_404..342_603, exactly as the W148 seat leg4 +',
    '        # r759 gate leg3 projection notes anticipated; the honest',
    '        # forward walk hops=1 lands 342_604..344_603; A base ==',
    '        # prior-wave B tail+1 (342_603+1) machine-checkable --',
    '        # A-hops-prior-B staircase eighth instance, E36 card;',
    '        # non-rotational r587 forward-monotone walk);',
    '        # B = FIRST-CLEAN past the own-wave A window (the arithmetic',
    '        # continuation 342_604..342_803 is CLEAN on the registered',
    '        # universe but lands INSIDE the W149 A band window --',
    '        # same-freeze mutual exclusion (W141 precedent, leg2 law) --',
    '        # the walk with the own-wave A window reserved jumps to',
    '        # 344_604 and lands 344_604..344_803, hops=1, non-rotational',
    '        # r587 forward-monotone walk; B base == own-wave A tail+1',
    '        # (344_603+1) machine-checkable; cross-window convergence',
    '        # with the W148 seat leg4 + r759 gate leg3 projection notes',
    '        # -- both MANDATORY notes honored (post-W148 universe',
    '        # re-derive + own-wave A reservation when deriving B); seat',
    '        # MSG-060x tail, re-derived).',
    '        assert WAVE_CONFIGS[149]["a_seed_base"] == 342_604 == 342_603 + 1, (',
    '            "W149 A must be the first-clean window past the registered "',
    '            "W148 B band tail 342_603+1 (arithmetic continuation "',
    '            "342_404..344_403 REFUSED at its own start by the W148 B "',
    '            "band 342_404..342_603, exactly as the W148 seat leg4 + "',
    '            "r759 gate leg3 projection notes anticipated; honest "',
    '            "forward walk hops=1; A base == prior-wave B tail+1 "',
    '            "machine-checkable = A-hops-prior-B staircase eighth "',
    '            "instance, E36 card)")',
    '        arith_a149 = set(range(342_604, 344_604))',
    '        assert not (arith_a149 & reg_ints), \\',
    '            "W149 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
    '        assert WAVE_CONFIGS[149]["b_exit_seed_base"] == 344_604 == 344_603 + 1, (',
    '            "W149 B must be the first-clean window past the own-wave A "',
    '            "band tail 344_603+1 (arithmetic continuation "',
    '            "342_604..342_803 CLEAN on the registered universe but "',
    '            "lands INSIDE the W149 A band window; same-freeze mutual "',
    '            "exclusion (W141 precedent, leg2 law) -- the walk with the "',
    '            "own-wave A window reserved jumps to 344_604, first-clean "',
    '            "hops=1, non-rotational r587 forward-monotone walk; B "',
    '            "base == own-wave A tail+1 machine-checkable)")',
    '        arith_b149 = set(range(344_604, 344_804))',
    '        assert not (arith_b149 & reg_ints), \\',
    '            "W149 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
    '        assert not (arith_b149 & arith_a149), \\',
    '            "W149 A/B same-freeze mutual exclusion (B hops past own A)"',
    '        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W149-SHARD-0",',
    '                                          "n1w149-0of12"), "W149 entry identity"',
    '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W149-SHARD-11",',
    '                                           "n1w149-11of12")',
    '        assert SHARD_DIR.endswith("n1_w149") and OUT.endswith(',
    '            "n1_w149_results.json"), "W149 path drift"',
    '        for wprev in sorted(w for w in WAVE_CONFIGS if w < 149):',
    '            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(',
    '                PATHS.results_dir, "p2cal_ext",',
    '                WAVE_CONFIGS[wprev]["shard_subdir"])), \\',
    '                f"W149 shard dir collides with W{wprev}"',
    '        # W149 finalize cumulative deps: W17..W148 outputs ALL PRESENT',
    '        # (landed net chain head 721,611 = W148 bm-a r760 one-pass --',
    '        # ZERO in-flight upstream seats, clean precondition freeze',
    '        # window; the finalize merge loop derives the wave set from',
    '        # registry keys at run time and stays FAIL-CLOSED, r307',
    '        # two-state law).',
    '        for _depw in range(17, 149):',
    '            assert os.path.exists(os.path.join(',
    '                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\',
    '                f"W149 finalize cumulative dep (W{_depw} output) missing"',
    '        # finalize wave-set derivation face (r511 derive law): every',
    '        # registered wave below 149 composes; wave 15 excluded by',
    '        # design; SINGLE STATE (W2..W148 all registered -- no',
    '        # two-state seat disclosure needed at this freeze).',
    '        assert sorted(w for w in WAVE_CONFIGS if w < 149) == \\',
    '            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\',
    '            [w for w in range(16, 149)], \\',
    '            "W149 prior-wave set must derive from registry keys (no 15; " \\',
    '            "W2..W148 registered single state)"',
    '        assert os.path.exists(os.path.join(',
    '            PATHS.root, "research", "PERPETUAL_N1_W149_PREREG.md")), \\',
    '            "W149 per-wave prereg missing (materializer requirement)"',
    '        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"',
    '    finally:',
    '        _set_wave(2)',
])
r3 = ('    finally:\r\n        _set_wave(2)\r\n' + LEG + CRLF +
      '    # --- T-141 s2 lane face')

# --- edit 4: n1.py PASS snippet --------------------------------------------------
a4 = ('"results/_r759bma_w148_band_gate.py, law sec.4 W148 row, "\r\n'
      '          "r759 bm-a] "\r\n'
      '          "+ T-141 s2 "')
snip = CRLF.join([
    '          "+ W149 materializer face [same guard set, dep=W17..W148 "',
    '          "outputs ALL PRESENT (landed net chain head 721,611 = "',
    '          "W148 bm-a r760 one-pass, K=323,520 merged pool; ZERO "',
    '          "in-flight upstream seats), ONE HUNDRED-AND-THIRTY-NINTH "',
    '          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 138 "',
    '          "+ candidate) bm-a\'s sixty-fifth owned claim per "',
    '          "machine-derive (engine_owner==bm-a rows 64 + candidate), "',
    '          "A=FIRST-CLEAN past the registered W148 B band (staircase "',
    '          "eighth instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
    '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
    '          "mutual exclusion, hops=1), ADMIT receipt "',
    '          "results/_r761bma_w149_band_gate.py, law sec.4 W149 row, "',
    '          "r761 bm-a] "',
])
r4 = ('"results/_r759bma_w148_band_gate.py, law sec.4 W148 row, "\r\n'
      '          "r759 bm-a] "\r\n' + snip + CRLF + '          "+ T-141 s2 "')

edit(N1, [(a2, r2), (a3, r3), (a4, r4)])

# --- post-edit structural assertions --------------------------------------------
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 149 and len(pf.N1_BANDS) == 147, \
    "pf N1_BANDS row-count drift after W149 insert"
assert pf.N1_BANDS[149] == {"a": (342_604, 344_603),
                            "b_exit": (344_604, 344_803),
                            "engine_owner": "bm-a"}, "W149 row face drift"
assert pf.N1_BANDS[148] == {"a": (340_404, 342_403),
                            "b_exit": (342_404, 342_603),
                            "engine_owner": "bm-a"}, "W148 row survived (r560 no-replace law)"
print("post-edit structural assertions PASS: N1_BANDS 147 rows tail W149, "
      "W148 row intact")
