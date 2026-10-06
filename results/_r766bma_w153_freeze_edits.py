# -*- coding: utf-8 -*-
"""r766 bm-a W153 freeze edits: four insertions (pf N1_BANDS[153] row +
n1 WAVE_CONFIGS[153] + n1 W153 materializer leg + n1 PASS snippet).
EOL-adaptive (r370 law: files are CRLF-dominant -- blocks written CRLF);
needle count==1 (r745); insert-after-last-registered-row + post-anchor
content checks (r560); anchor = predecessor full lines, no whole-anchor
backfill (r580/r581); AST gate after every edit batch (r580/r581).
prereg block built by programmatic double-quote wrapping with the tail
paren KEPT on the last item (r761 Rev.B lesson + r762/r763/r764 precedent).
Bloodline: r764 _r764bma_w152_freeze_edits.py verbatim machinery, W153
facts live-registry-driven (band gate _r766bma_w153_band_gate.py rc0)."""
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


# --- edit 1: pf.py N1_BANDS[153] row (insert after registered W152 row) --------
a1 = ('    152: {"a": (349_204, 351_203), "b_exit": (351_204, 351_403),\r\n'
      '         "engine_owner": "bm-a"},\r\n'
      '}')
w153_row = CRLF.join([
    '    # W153 (bm-a r766 freeze, seat MSG-2026-10-06-084x-bma-w153-seat',
    '    # pushed to origin 3ae290395 pre-freeze r565 law (r766 pre-seat',
    '    # push; payload = seat MSG + pre-seat probe + probe receipt;',
    '    # delivery window absorbed a behind-3 bm-c r607 peer wave via',
    '    # rebase + own daemon churn-absorb precede, zero --no-verify;',
    '    # same-window self-ack inbox->processed move r766;',
    '    # deletion-set EMPTY);',
    '    # band gate ADMIT results/_r766bma_w153_band_gate.json: A = FIRST-CLEAN',
    '    # past the registered W152 B band (arithmetic continuation',
    '    # 351_204..353_203 REFUSED at its own start by the W152 B band',
    '    # 351_204..351_403, exactly as the W152 seat leg4 + r764 gate',
    '    # leg3 + r765 sec8 succession projection notes all anticipated;',
    '    # honest forward walk hops=1 -> 351_404..353_403, non-rotational',
    '    # r587 forward-monotone walk; A base == prior-wave B tail+1',
    '    # (351_403+1) machine-checkable -- A-hops-prior-B staircase',
    '    # twelfth instance, E36 card);',
    '    # B = FIRST-CLEAN past the own-wave A window (arithmetic',
    '    # continuation 351_404..351_603 CLEAN on the registered universe',
    '    # but lands INSIDE the W153 A band window -- same-freeze mutual',
    '    # exclusion (W141 precedent, leg2 law) -- the walk with the',
    '    # own-wave A window reserved jumps to 353_404 -> 353_404..353_603,',
    '    # hops=1, non-rotational r587 forward-monotone walk; B base ==',
    '    # own-wave A tail+1 (353_403+1) machine-checkable);',
    '    # dual-window derive parity with pre-seat probe',
    '    # results/_r766bma_w153_probe_receipt.json; scan face =',
    '    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1',
    '    # used-seed band + probe cluster 95_000..95_003 + cross-face',
    '    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/',
    '    # N2-W15 probe points.',
    '    # W154+ projection (gate-derived r766): A first-clean',
    '    # 353_404..355_403 CLEAN hops=0 / B first-clean 353_604..353_803',
    '    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the',
    '    # registered W153 B band 353_404..353_603 will refuse the naive',
    '    # W154 A window; W154 freezer MUST re-derive on the post-W153',
    '    # universe AND reserve the own-wave A window when deriving B',
    '    # (W141 precedent, same-freeze mutual exclusion, leg2 law,',
    '    # E36 staircase card; never transcribe r587).',
    '    # NOT a re-pick (R250: W153 bands were never assigned).',
    '    153: {"a": (351_404, 353_403), "b_exit": (353_404, 353_603),',
    '         "engine_owner": "bm-a"},',
])
r1 = ('    152: {"a": (349_204, 351_203), "b_exit": (351_204, 351_403),\r\n'
      '         "engine_owner": "bm-a"},\r\n' + w153_row + '\r\n}')
edit(PF, [(a1, r1)])

# --- edit 2: n1.py WAVE_CONFIGS[153] (prereg block built programmatically) ----
PRE = [
    "research/PERPETUAL_N1_W153_PREREG.md (wave-level frozen ",
    "pre-run; design = frozen v1 null calibration verbatim, ",
    "new seed bands only; ONE HUNDRED-AND-FORTY-THIRD ENGINE-OWNED WAVE ",
    "BY MACHINE-DERIVE (engine_owner rows 142 + candidate), ",
    "own-series continuation per O-20261001-2355 sec.2 (first-free-",
    "number law after the REGISTERED W152 row bm-a r764 freeze ",
    "520eb01ca, SINGLE STATE zero seat gap W2..W152 all ",
    "registered; W152 finalize landed same-window r765, ledger ",
    "head 730,411, merged pool K=332,320; seat published=reserved ",
    "MSG-2026-10-06-084x-bma-w153-seat PUSHED to origin 3ae290395 ",
    "BEFORE this freeze per r565 early-visibility law (payload = ",
    "seat MSG + pre-seat probe + probe receipt; deletion-set ",
    "EMPTY; delivery window absorbed a behind-3 bm-c r607 peer ",
    "wave via rebase + own daemon churn-absorb precede, zero ",
    "--no-verify; pre-seat probe and freeze-window band-gate ",
    "runs derive identical, no fork face), ",
    "engine_owner=bm-a, wave 153: ",
    "A = FIRST-CLEAN past the registered W152 B band (the ",
    "arithmetic continuation 351_204..353_203 is REFUSED at its ",
    "own start by the W152 B band 351_204..351_403, exactly as ",
    "the W152 seat leg4 + r764 gate leg3 + r765 sec8 succession ",
    "projection notes anticipated; honest forward walk hops=1 -> ",
    "351_404..353_403; A base == prior-wave B tail+1 ",
    "machine-checkable = A-hops-prior-B staircase twelfth ",
    "instance, E36 card; non-rotational r587 forward-monotone ",
    "walk) + B = FIRST-CLEAN past the own-wave A window (the ",
    "arithmetic continuation 351_404..351_603 is CLEAN on the ",
    "registered universe but lands INSIDE the W153 A band ",
    "window -- same-freeze mutual exclusion, W141 precedent, ",
    "leg2 law -- the walk with the own-wave A window reserved ",
    "jumps to 353_404, first-clean 353_404..353_603 hops=1, ",
    "non-rotational r587 forward-monotone walk; B base == ",
    "own-wave A tail+1 machine-checkable; cross-window ",
    "convergence with the W152 seat leg4 + r764 gate leg3 + ",
    "r765 sec8 succession projection notes re-derived -- all ",
    "MANDATORY notes honored (post-W152 universe re-derive + ",
    "own-wave A reservation); ADMIT receipt ",
    "results/_r766bma_w153_band_gate.json; W154+ projection ",
    "per this window gate: A first-clean 353_404..355_403 ",
    "CLEAN / B first-clean 353_604..353_803 CLEAN -- naive ",
    "B lands INSIDE the naive A window and the registered ",
    "W153 B band 353_404..353_603 will refuse the naive ",
    "W154 A window; W154 freezer MUST re-derive on the ",
    "post-W153 universe AND reserve the own-wave A window ",
    "when deriving B (W141 precedent, leg2 law, E36 ",
    "staircase card); W1..W152 finalize ALL LANDED (W152 ",
    "finalize one-pass bm-a r765, net chain head 730,411, ",
    "merged pool K=332,320) -- ZERO in-flight upstream ",
    "seats, clean finalize chain precondition -- finalize ",
    "merge loop still derives the wave set from registry ",
    "keys at run time, FAIL-CLOSED r307 always on)",
]
prereg_lines = ['                       153: {"batch": "PERPETUAL-N1-W153",']
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
    '                            "a_seed_base": 351_404,        # law sec.4 W153 A: 351_404..353_403 (FIRST-CLEAN past the registered W152 B band; arithmetic 351_204..353_203 REFUSED at own start by the W152 B band; hops=1; A-hops-prior-B staircase twelfth instance, E36 card)',
    '                            "b_exit_seed_base": 353_404,   # law sec.4 W153 B: 353_404..353_603 (FIRST-CLEAN past the own-wave A window; arithmetic 351_404..351_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
    '                            "shard_subdir": "n1_w153", "out_name": "n1_w153_results.json",',
    '                            "engine_owner": "bm-a"},',
    '                       }',
]
a2 = ('"shard_subdir": "n1_w152", "out_name": "n1_w152_results.json",\r\n'
      '                            "engine_owner": "bm-a"},\r\n'
      '                       }')
r2 = ('"shard_subdir": "n1_w152", "out_name": "n1_w152_results.json",\r\n'
      '                            "engine_owner": "bm-a"},\r\n' +
      CRLF.join(prereg_lines))

# --- edit 3: n1.py W153 materializer leg ----------------------------------------
a3 = '    finally:\r\n        _set_wave(2)\r\n    # --- T-141 s2 lane face'
LEG = CRLF.join([
    '    # --- W153 materializer face (r766 bm-a freeze, own-series law',
    '    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a\'s',
    '    #     sixty-ninth owned per machine-derive (engine_owner==bm-a',
    '    #     rows 68 + candidate); wave 153 = first free number after',
    '    #     the REGISTERED W152 row (bm-a r764 freeze 520eb01ca) --',
    '    #     SINGLE STATE zero seat gap (W2..W152 all registered). Seat',
    '    #     published=reserved MSG-2026-10-06-084x-bma-w153-seat pushed',
    '    #     to origin 3ae290395 BEFORE this freeze, r565 law (payload',
    '    #     = seat MSG + pre-seat probe + probe receipt; deletion-set',
    '    #     EMPTY; delivery window absorbed a behind-3 bm-c r607 peer',
    '    #     wave via rebase + own daemon churn-absorb precede; zero',
    '    #     --no-verify; same-window self-ack inbox->processed move',
    '    #     r766). ONE HUNDRED-AND-FORTY-THIRD engine wave BY',
    '    #     MACHINE-DERIVE (engine_owner rows 142 + candidate; gate',
    '    #     leg0 machine output governs per r359 law).',
    '    #     W1..W152 finalize ALL LANDED (net chain head 730,411,',
    '    #     K=332,320 merged pool; W152 finalize one-pass bm-a r765)',
    '    #     -- ZERO in-flight upstream seats, clean finalize chain',
    '    #     precondition; the finalize merge loop still derives the',
    '    #     wave set from registry keys at run time, FAIL-CLOSED r307',
    '    #     always on. ADMIT receipt results/_r766bma_w153_band_gate.json;',
    '    #     banned gate ADMIT 0; not a re-pick (R250: W153 bands were',
    '    #     never assigned).',
    '    _set_wave(153)',
    '    try:',
    '        assert WAVE_CONFIGS[153]["a_seed_base"] == pf.N1_BANDS[153]["a"][0], \\',
    '            "W153 A band drift vs law mirror"',
    '        assert WAVE_CONFIGS[153]["b_exit_seed_base"] == \\',
    '            pf.N1_BANDS[153]["b_exit"][0], "W153 B band drift vs law mirror"',
    '        assert WAVE_CONFIGS[153].get("engine_owner") == \\',
    '            pf.N1_BANDS[153].get("engine_owner") == "bm-a", \\',
    '            "W153 engine_owner drift (law mirror parity)"',
    '        w153_a = {A_SEED_BASE + j for j in range(A_N)}',
    '        w153_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}',
    '        assert not (w153_a & w153_b), "W153 A/B band overlap"',
    '        assert not (w153_a & reg_ints) and not (w153_b & reg_ints), \\',
    '            "W153 hits SEED_REGISTRY"',
    '        for nm, band in (("A", w153_a), ("B", w153_b)):',
    '            assert not (band & v1_a) and not (band & v1_b), f"W153 {nm} hits v1"',
    '            assert not (band & w1_a) and not (band & w1_b), f"W153 {nm} hits W1"',
    '            assert not (band & probes), f"W153 {nm} hits probe seeds"',
    '        # registered row parity (r307 pinned constants, recent estate)',
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
    '        assert pf.N1_BANDS[150] == {"a": (344_804, 346_803),',
    '                                    "b_exit": (346_804, 347_003),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W150 row parity drift (r307; bm-a r762)"',
    '        assert pf.N1_BANDS[151] == {"a": (347_004, 349_003),',
    '                                    "b_exit": (349_004, 349_203),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W151 row parity drift (r307; bm-a r763)"',
    '        assert pf.N1_BANDS[152] == {"a": (349_204, 351_203),',
    '                                    "b_exit": (351_204, 351_403),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W152 row parity drift (r307; bm-a r764)"',
    '        # prior-wave disjointness W2..W152 (single state: all',
    '        # registered, dynamic registry derive, r511 law)',
    '        for wprev in sorted(w for w in WAVE_CONFIGS if w < 153):',
    '            assert not (w153_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
    '                                 for j in range(A_N)}), f"W153 A hits W{wprev}"',
    '            assert not (w153_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
    '                                  for j in range(B_N)}), f"W153 B hits W{wprev}"',
    '        n3r1_used153 = set(range(70_000, 70_006))',
    '        assert not (w153_a & n3r1_used153) and not (w153_b & n3r1_used153), \\',
    '            "W153 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
    '        assert not (w153_a & lfc_actual12) and not (w153_b & lfc_actual12), \\',
    '            "W153 bands must clear the lfc actual draw range"',
    '        assert not (w153_a & options_actual12) and \\',
    '            not (w153_b & options_actual12), \\',
    '            "W153 bands must clear the options_wave2 actual draw range"',
    '        # band facts (law sec.4 W153 row, r766): A = FIRST-CLEAN past',
    '        # the registered W152 B band (the arithmetic continuation',
    '        # 351_204..353_203 is REFUSED at its own start by the W152',
    '        # B band 351_204..351_403, exactly as the W152 seat leg4 +',
    '        # r764 gate leg3 + r765 sec8 succession projection notes',
    '        # anticipated; the honest forward walk hops=1 lands',
    '        # 351_404..353_403; A base == prior-wave B tail+1 (351_403+1)',
    '        # machine-checkable -- A-hops-prior-B staircase twelfth',
    '        # instance, E36 card; non-rotational r587 forward-monotone',
    '        # walk);',
    '        # B = FIRST-CLEAN past the own-wave A window (the arithmetic',
    '        # continuation 351_404..351_603 is CLEAN on the registered',
    '        # universe but lands INSIDE the W153 A band window --',
    '        # same-freeze mutual exclusion (W141 precedent, leg2 law) --',
    '        # the walk with the own-wave A window reserved jumps to',
    '        # 353_404 and lands 353_404..353_603, hops=1, non-rotational',
    '        # r587 forward-monotone walk; B base == own-wave A tail+1',
    '        # (353_403+1) machine-checkable; cross-window convergence',
    '        # with the W152 seat leg4 + r764 gate leg3 + r765 sec8',
    '        # succession projection notes -- all MANDATORY notes',
    '        # honored (post-W152 universe re-derive + own-wave A',
    '        # reservation when deriving B); seat MSG-084x tail,',
    '        # re-derived).',
    '        assert WAVE_CONFIGS[153]["a_seed_base"] == 351_404 == 351_403 + 1, (',
    '            "W153 A must be the first-clean window past the registered "',
    '            "W152 B band tail 351_403+1 (arithmetic continuation "',
    '            "351_204..353_203 REFUSED at its own start by the W152 B "',
    '            "band 351_204..351_403, exactly as the W152 seat leg4 + "',
    '            "r764 gate leg3 + r765 sec8 succession projection notes "',
    '            "anticipated; honest forward walk hops=1; A base == "',
    '            "prior-wave B tail+1 machine-checkable = A-hops-prior-B "',
    '            "staircase twelfth instance, E36 card)")',
    '        arith_a153 = set(range(351_404, 353_404))',
    '        assert not (arith_a153 & reg_ints), \\',
    '            "W153 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
    '        assert WAVE_CONFIGS[153]["b_exit_seed_base"] == 353_404 == 353_403 + 1, (',
    '            "W153 B must be the first-clean window past the own-wave A "',
    '            "band tail 353_403+1 (arithmetic continuation "',
    '            "351_404..351_603 CLEAN on the registered universe but "',
    '            "lands INSIDE the W153 A band window; same-freeze mutual "',
    '            "exclusion (W141 precedent, leg2 law) -- the walk with the "',
    '            "own-wave A window reserved jumps to 353_404, first-clean "',
    '            "hops=1, non-rotational r587 forward-monotone walk; B "',
    '            "base == own-wave A tail+1 machine-checkable)")',
    '        arith_b153 = set(range(353_404, 353_604))',
    '        assert not (arith_b153 & reg_ints), \\',
    '            "W153 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
    '        assert not (arith_b153 & arith_a153), \\',
    '            "W153 A/B same-freeze mutual exclusion (B hops past own A)"',
    '        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W153-SHARD-0",',
    '                                          "n1w153-0of12"), "W153 entry identity"',
    '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W153-SHARD-11",',
    '                                           "n1w153-11of12")',
    '        assert SHARD_DIR.endswith("n1_w153") and OUT.endswith(',
    '            "n1_w153_results.json"), "W153 path drift"',
    '        for wprev in sorted(w for w in WAVE_CONFIGS if w < 153):',
    '            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(',
    '                PATHS.results_dir, "p2cal_ext",',
    '                WAVE_CONFIGS[wprev]["shard_subdir"])), \\',
    '                f"W153 shard dir collides with W{wprev}"',
    '        # W153 finalize cumulative deps: W17..W152 outputs ALL PRESENT',
    '        # (landed net chain head 730,411 = W152 bm-a r765 one-pass --',
    '        # ZERO in-flight upstream seats, clean precondition freeze',
    '        # window; the finalize merge loop derives the wave set from',
    '        # registry keys at run time and stays FAIL-CLOSED, r307',
    '        # two-state law).',
    '        for _depw in range(17, 153):',
    '            assert os.path.exists(os.path.join(',
    '                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\',
    '                f"W153 finalize cumulative dep (W{_depw} output) missing"',
    '        # finalize wave-set derivation face (r511 derive law): every',
    '        # registered wave below 153 composes; wave 15 excluded by',
    '        # design; SINGLE STATE (W2..W152 all registered -- no',
    '        # two-state seat disclosure needed at this freeze).',
    '        assert sorted(w for w in WAVE_CONFIGS if w < 153) == \\',
    '            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\',
    '            [w for w in range(16, 153)], \\',
    '            "W153 prior-wave set must derive from registry keys (no 15; " \\',
    '            "W2..W152 registered single state)"',
    '        assert os.path.exists(os.path.join(',
    '            PATHS.root, "research", "PERPETUAL_N1_W153_PREREG.md")), \\',
    '            "W153 per-wave prereg missing (materializer requirement)"',
    '        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"',
    '    finally:',
    '        _set_wave(2)',
])
r3 = ('    finally:\r\n        _set_wave(2)\r\n' + LEG + CRLF +
      '    # --- T-141 s2 lane face')

# --- edit 4: n1.py PASS snippet --------------------------------------------------
a4 = ('"results/_r764bma_w152_band_gate.json, law sec.4 W152 row, "\r\n'
      '          "r764 bm-a] "\r\n'
      '          "+ T-141 s2 "')
snip = CRLF.join([
    '          "+ W153 materializer face [same guard set, dep=W17..W152 "',
    '          "outputs ALL PRESENT (landed net chain head 730,411 = "',
    '          "W152 bm-a r765 one-pass, K=332,320 merged pool; ZERO "',
    '          "in-flight upstream seats), ONE HUNDRED-AND-FORTY-THIRD "',
    '          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 142 "',
    '          "+ candidate) bm-a\'s sixty-ninth owned claim per "',
    '          "machine-derive (engine_owner==bm-a rows 68 + candidate), "',
    '          "A=FIRST-CLEAN past the registered W152 B band (staircase "',
    '          "twelfth instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
    '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
    '          "mutual exclusion, hops=1), ADMIT receipt "',
    '          "results/_r766bma_w153_band_gate.json, law sec.4 W153 row, "',
    '          "r766 bm-a] "',
])
r4 = ('"results/_r764bma_w152_band_gate.json, law sec.4 W152 row, "\r\n'
      '          "r764 bm-a] "\r\n' + snip + CRLF + '          "+ T-141 s2 "')

edit(N1, [(a2, r2), (a3, r3), (a4, r4)])

# --- post-edit structural assertions --------------------------------------------
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 153 and len(pf.N1_BANDS) == 151, \
    "pf N1_BANDS row-count drift after W153 insert"
assert pf.N1_BANDS[153] == {"a": (351_404, 353_403),
                            "b_exit": (353_404, 353_603),
                            "engine_owner": "bm-a"}, "W153 row face drift"
assert pf.N1_BANDS[152] == {"a": (349_204, 351_203),
                            "b_exit": (351_204, 351_403),
                            "engine_owner": "bm-a"}, "W152 row survived (r560 no-replace law)"
print("post-edit structural assertions PASS: N1_BANDS 151 rows tail W153, "
      "W152 row intact")
