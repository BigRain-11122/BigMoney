# -*- coding: utf-8 -*-
"""r768 bm-a W155 freeze edits: four insertions (pf N1_BANDS[155] row +
n1 WAVE_CONFIGS[155] + n1 W155 materializer leg + n1 PASS snippet).
EOL-adaptive (r370 law: files are CRLF-dominant -- blocks written CRLF);
needle count==1 (r745); insert-after-last-registered-row + post-anchor
content checks (r560); anchor = predecessor full lines, no whole-anchor
backfill (r580/r581); AST gate after every edit batch (r580/r581).
prereg block built by programmatic double-quote wrapping with the tail
paren KEPT on the last item (r761 Rev.B lesson + r762/r763/r764/r766/r767
precedent).
Bloodline: r767 _r767bma_w154_freeze_edits.py verbatim machinery, W155
facts live-registry-driven (band gate _r768bma_w155_band_gate.py rc0)."""
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


# --- edit 1: pf.py N1_BANDS[155] row (insert after registered W154 row) --------
a1 = ('    154: {"a": (353_604, 355_603), "b_exit": (355_604, 355_803),\r\n'
      '         "engine_owner": "bm-a"},\r\n'
      '}')
w155_row = CRLF.join([
    '    # W155 (bm-a r768 freeze, seat MSG-2026-10-06-0943-bma-w155-seat',
    '    # pushed to origin 1fedffbe4 pre-freeze r565 law (r768 pre-seat',
    '    # push; payload = seat MSG + pre-seat probe + probe receipt +',
    '    # W154 finalize products; deletion-set EMPTY; delivery window',
    '    # absorbed a behind-2 bm-c r610 guard-round peer commit via',
    '    # merge, zero --no-verify; same-window self-ack inbox->processed',
    '    # move r768;',
    '    # deletion-set EMPTY);',
    '    # band gate ADMIT results/_r768bma_w155_band_gate.json: A = FIRST-CLEAN',
    '    # past the registered W154 B band (arithmetic continuation',
    '    # 355_604..357_603 REFUSED at its own start by the W154 B band',
    '    # 355_604..355_803, exactly as the W154 seat leg4 + r767 gate',
    '    # leg3 + r767 sec8 succession projection notes all anticipated;',
    '    # honest forward walk hops=1 -> 355_804..357_803, non-rotational',
    '    # r587 forward-monotone walk; A base == prior-wave B tail+1',
    '    # (355_803+1) machine-checkable -- A-hops-prior-B staircase',
    '    # fourteenth instance, E36 card);',
    '    # B = FIRST-CLEAN past the own-wave A window (arithmetic',
    '    # continuation 355_804..356_003 CLEAN on the registered universe',
    '    # but lands INSIDE the W155 A band window -- same-freeze mutual',
    '    # exclusion (W141 precedent, leg2 law) -- the walk with the',
    '    # own-wave A window reserved jumps to 357_804 -> 357_804..358_003,',
    '    # hops=1, non-rotational r587 forward-monotone walk; B base ==',
    '    # own-wave A tail+1 (357_803+1) machine-checkable);',
    '    # dual-window derive parity with pre-seat probe',
    '    # results/_r768bma_w155_probe_receipt.json; scan face =',
    '    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1',
    '    # used-seed band + probe cluster 95_000..95_003 + cross-face',
    '    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/',
    '    # N2-W15 probe points.',
    '    # W156+ projection (gate-derived r768): A first-clean',
    '    # 357_804..359_803 CLEAN hops=0 / B first-clean 358_004..358_203',
    '    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the',
    '    # registered W155 B band 357_804..358_003 will refuse the naive',
    '    # W156 A window; W156 freezer MUST re-derive on the post-W155',
    '    # universe AND reserve the own-wave A window when deriving B',
    '    # (W141 precedent, same-freeze mutual exclusion, leg2 law,',
    '    # E36 staircase card; never transcribe r587).',
    '    # NOT a re-pick (R250: W155 bands were never assigned).',
    '    155: {"a": (355_804, 357_803), "b_exit": (357_804, 358_003),',
    '         "engine_owner": "bm-a"},',
])
r1 = ('    154: {"a": (353_604, 355_603), "b_exit": (355_604, 355_803),\r\n'
      '         "engine_owner": "bm-a"},\r\n' + w155_row + '\r\n}')
edit(PF, [(a1, r1)])

# --- edit 2: n1.py WAVE_CONFIGS[155] (prereg block built programmatically) ----
PRE = [
    "research/PERPETUAL_N1_W155_PREREG.md (wave-level frozen ",
    "pre-run; design = frozen v1 null calibration verbatim, ",
    "new seed bands only; ONE HUNDRED-AND-FORTY-FIFTH ENGINE-OWNED WAVE ",
    "BY MACHINE-DERIVE (engine_owner rows 144 + candidate), ",
    "own-series continuation per O-20261001-2355 sec.2 (first-free-",
    "number law after the REGISTERED W154 row bm-a r767 freeze ",
    "3095cb47e, SINGLE STATE zero seat gap W2..W154 all ",
    "registered; W154 finalize landed same-window r768, ledger ",
    "head 734,811, merged pool K=336,720; seat published=reserved ",
    "MSG-2026-10-06-0943-bma-w155-seat PUSHED to origin 1fedffbe4 ",
    "BEFORE this freeze per r565 early-visibility law (payload = ",
    "seat MSG + pre-seat probe + probe receipt + W154 finalize ",
    "products; deletion-set EMPTY; delivery window absorbed a ",
    "behind-2 bm-c r610 guard-round peer commit via merge, ",
    "zero --no-verify; pre-seat probe and freeze-window band-gate ",
    "runs derive identical, no fork face), ",
    "engine_owner=bm-a, wave 155: ",
    "A = FIRST-CLEAN past the registered W154 B band (the ",
    "arithmetic continuation 355_604..357_603 is REFUSED at its ",
    "own start by the W154 B band 355_604..355_803, exactly as ",
    "the W154 seat leg4 + r767 gate leg3 + r767 sec8 succession ",
    "projection notes anticipated; honest forward walk hops=1 -> ",
    "355_804..357_803; A base == prior-wave B tail+1 ",
    "machine-checkable = A-hops-prior-B staircase fourteenth ",
    "instance, E36 card; non-rotational r587 forward-monotone ",
    "walk) + B = FIRST-CLEAN past the own-wave A window (the ",
    "arithmetic continuation 355_804..356_003 is CLEAN on the ",
    "registered universe but lands INSIDE the W155 A band ",
    "window -- same-freeze mutual exclusion, W141 precedent, ",
    "leg2 law -- the walk with the own-wave A window reserved ",
    "jumps to 357_804, first-clean 357_804..358_003 hops=1, ",
    "non-rotational r587 forward-monotone walk; B base == ",
    "own-wave A tail+1 machine-checkable; cross-window ",
    "convergence with the W154 seat leg4 + r767 gate leg3 + ",
    "r767 sec8 succession projection notes re-derived -- all ",
    "MANDATORY notes honored (post-W154 universe re-derive + ",
    "own-wave A reservation); ADMIT receipt ",
    "results/_r768bma_w155_band_gate.json; W156+ projection ",
    "per this window gate: A first-clean 357_804..359_803 ",
    "CLEAN / B first-clean 358_004..358_203 CLEAN -- naive ",
    "B lands INSIDE the naive A window and the registered ",
    "W155 B band 357_804..358_003 will refuse the naive ",
    "W156 A window; W156 freezer MUST re-derive on the ",
    "post-W155 universe AND reserve the own-wave A window ",
    "when deriving B (W141 precedent, leg2 law, E36 ",
    "staircase card); W1..W154 finalize ALL LANDED (W154 ",
    "finalize one-pass bm-a r768, net chain head 734,811, ",
    "merged pool K=336,720) -- ZERO in-flight upstream ",
    "seats, clean finalize chain precondition -- finalize ",
    "merge loop still derives the wave set from registry ",
    "keys at run time, FAIL-CLOSED r307 always on)",
]
prereg_lines = ['                       155: {"batch": "PERPETUAL-N1-W155",']
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
    '                            "a_seed_base": 355_804,        # law sec.4 W155 A: 355_804..357_803 (FIRST-CLEAN past the registered W154 B band; arithmetic 355_604..357_603 REFUSED at own start by the W154 B band; hops=1; A-hops-prior-B staircase fourteenth instance, E36 card)',
    '                            "b_exit_seed_base": 357_804,   # law sec.4 W155 B: 357_804..358_003 (FIRST-CLEAN past the own-wave A window; arithmetic 355_804..356_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
    '                            "shard_subdir": "n1_w155", "out_name": "n1_w155_results.json",',
    '                            "engine_owner": "bm-a"},',
    '                       }',
]
a2 = ('"shard_subdir": "n1_w154", "out_name": "n1_w154_results.json",\r\n'
      '                            "engine_owner": "bm-a"},\r\n'
      '                       }')
r2 = ('"shard_subdir": "n1_w154", "out_name": "n1_w154_results.json",\r\n'
      '                            "engine_owner": "bm-a"},\r\n' +
      CRLF.join(prereg_lines))

# --- edit 3: n1.py W155 materializer leg ----------------------------------------
a3 = '    finally:\r\n        _set_wave(2)\r\n    # --- T-141 s2 lane face'
LEG = CRLF.join([
    '    # --- W155 materializer face (r768 bm-a freeze, own-series law',
    '    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a\'s',
    '    #     seventy-first owned per machine-derive (engine_owner==bm-a',
    '    #     rows 70 + candidate); wave 155 = first free number after',
    '    #     the REGISTERED W154 row (bm-a r767 freeze 3095cb47e) --',
    '    #     SINGLE STATE zero seat gap (W2..W154 all registered). Seat',
    '    #     published=reserved MSG-2026-10-06-0943-bma-w155-seat pushed',
    '    #     to origin 1fedffbe4 BEFORE this freeze, r565 law (payload',
    '    #     = seat MSG + pre-seat probe + probe receipt + W154 finalize',
    '    #     products; deletion-set EMPTY; delivery window absorbed a',
    '    #     behind-2 bm-c r610 guard-round peer commit via merge;',
    '    #     zero --no-verify; same-window self-ack inbox->processed move',
    '    #     r768). ONE HUNDRED-AND-FORTY-FIFTH engine wave BY',
    '    #     MACHINE-DERIVE (engine_owner rows 144 + candidate; gate',
    '    #     leg0 machine output governs per r359 law).',
    '    #     W1..W154 finalize ALL LANDED (net chain head 734,811,',
    '    #     K=336,720 merged pool; W154 finalize one-pass bm-a r768)',
    '    #     -- ZERO in-flight upstream seats, clean finalize chain',
    '    #     precondition; the finalize merge loop still derives the',
    '    #     wave set from registry keys at run time, FAIL-CLOSED r307',
    '    #     always on. ADMIT receipt results/_r768bma_w155_band_gate.json;',
    '    #     banned gate ADMIT 0; not a re-pick (R250: W155 bands were',
    '    #     never assigned).',
    '    _set_wave(155)',
    '    try:',
    '        assert WAVE_CONFIGS[155]["a_seed_base"] == pf.N1_BANDS[155]["a"][0], \\',
    '            "W155 A band drift vs law mirror"',
    '        assert WAVE_CONFIGS[155]["b_exit_seed_base"] == \\',
    '            pf.N1_BANDS[155]["b_exit"][0], "W155 B band drift vs law mirror"',
    '        assert WAVE_CONFIGS[155].get("engine_owner") == \\',
    '            pf.N1_BANDS[155].get("engine_owner") == "bm-a", \\',
    '            "W155 engine_owner drift (law mirror parity)"',
    '        w155_a = {A_SEED_BASE + j for j in range(A_N)}',
    '        w155_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}',
    '        assert not (w155_a & w155_b), "W155 A/B band overlap"',
    '        assert not (w155_a & reg_ints) and not (w155_b & reg_ints), \\',
    '            "W155 hits SEED_REGISTRY"',
    '        for nm, band in (("A", w155_a), ("B", w155_b)):',
    '            assert not (band & v1_a) and not (band & v1_b), f"W155 {nm} hits v1"',
    '            assert not (band & w1_a) and not (band & w1_b), f"W155 {nm} hits W1"',
    '            assert not (band & probes), f"W155 {nm} hits probe seeds"',
    '        # registered row parity (r307 pinned constants, recent estate)',
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
    '        assert pf.N1_BANDS[153] == {"a": (351_404, 353_403),',
    '                                    "b_exit": (353_404, 353_603),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W153 row parity drift (r307; bm-a r766)"',
    '        assert pf.N1_BANDS[154] == {"a": (353_604, 355_603),',
    '                                    "b_exit": (355_604, 355_803),',
    '                                    "engine_owner": "bm-a"}, \\',
    '            "registered W154 row parity drift (r307; bm-a r767)"',
    '        # prior-wave disjointness W2..W154 (single state: all',
    '        # registered, dynamic registry derive, r511 law)',
    '        for wprev in sorted(w for w in WAVE_CONFIGS if w < 155):',
    '            assert not (w155_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
    '                                 for j in range(A_N)}), f"W155 A hits W{wprev}"',
    '            assert not (w155_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
    '                                  for j in range(B_N)}), f"W155 B hits W{wprev}"',
    '        n3r1_used155 = set(range(70_000, 70_006))',
    '        assert not (w155_a & n3r1_used155) and not (w155_b & n3r1_used155), \\',
    '            "W155 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
    '        assert not (w155_a & lfc_actual12) and not (w155_b & lfc_actual12), \\',
    '            "W155 bands must clear the lfc actual draw range"',
    '        assert not (w155_a & options_actual12) and \\',
    '            not (w155_b & options_actual12), \\',
    '            "W155 bands must clear the options_wave2 actual draw range"',
    '        # band facts (law sec.4 W155 row, r768): A = FIRST-CLEAN past',
    '        # the registered W154 B band (the arithmetic continuation',
    '        # 355_604..357_603 is REFUSED at its own start by the W154',
    '        # B band 355_604..355_803, exactly as the W154 seat leg4 +',
    '        # r767 gate leg3 + r767 sec8 succession projection notes',
    '        # anticipated; the honest forward walk hops=1 lands',
    '        # 355_804..357_803; A base == prior-wave B tail+1 (355_803+1)',
    '        # machine-checkable -- A-hops-prior-B staircase fourteenth',
    '        # instance, E36 card; non-rotational r587 forward-monotone',
    '        # walk);',
    '        # B = FIRST-CLEAN past the own-wave A window (the arithmetic',
    '        # continuation 355_804..356_003 is CLEAN on the registered',
    '        # universe but lands INSIDE the W155 A band window --',
    '        # same-freeze mutual exclusion (W141 precedent, leg2 law) --',
    '        # the walk with the own-wave A window reserved jumps to',
    '        # 357_804 and lands 357_804..358_003, hops=1, non-rotational',
    '        # r587 forward-monotone walk; B base == own-wave A tail+1',
    '        # (357_803+1) machine-checkable; cross-window convergence',
    '        # with the W154 seat leg4 + r767 gate leg3 + r767 sec8',
    '        # succession projection notes -- all MANDATORY notes',
    '        # honored (post-W154 universe re-derive + own-wave A',
    '        # reservation when deriving B); seat MSG-0943 tail,',
    '        # re-derived).',
    '        assert WAVE_CONFIGS[155]["a_seed_base"] == 355_804 == 355_803 + 1, (',
    '            "W155 A must be the first-clean window past the registered "',
    '            "W154 B band tail 355_803+1 (arithmetic continuation "',
    '            "355_604..357_603 REFUSED at its own start by the W154 B "',
    '            "band 355_604..355_803, exactly as the W154 seat leg4 + "',
    '            "r767 gate leg3 + r767 sec8 succession projection notes "',
    '            "anticipated; honest forward walk hops=1; A base == "',
    '            "prior-wave B tail+1 machine-checkable = A-hops-prior-B "',
    '            "staircase fourteenth instance, E36 card)")',
    '        arith_a155 = set(range(355_804, 357_804))',
    '        assert not (arith_a155 & reg_ints), \\',
    '            "W155 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
    '        assert WAVE_CONFIGS[155]["b_exit_seed_base"] == 357_804 == 357_803 + 1, (',
    '            "W155 B must be the first-clean window past the own-wave A "',
    '            "band tail 357_803+1 (arithmetic continuation "',
    '            "355_804..356_003 CLEAN on the registered universe but "',
    '            "lands INSIDE the W155 A band window; same-freeze mutual "',
    '            "exclusion (W141 precedent, leg2 law) -- the walk with the "',
    '            "own-wave A window reserved jumps to 357_804, first-clean "',
    '            "hops=1, non-rotational r587 forward-monotone walk; B "',
    '            "base == own-wave A tail+1 machine-checkable)")',
    '        arith_b155 = set(range(357_804, 358_004))',
    '        assert not (arith_b155 & reg_ints), \\',
    '            "W155 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
    '        assert not (arith_b155 & arith_a155), \\',
    '            "W155 A/B same-freeze mutual exclusion (B hops past own A)"',
    '        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W155-SHARD-0",',
    '                                          "n1w155-0of12"), "W155 entry identity"',
    '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W155-SHARD-11",',
    '                                           "n1w155-11of12")',
    '        assert SHARD_DIR.endswith("n1_w155") and OUT.endswith(',
    '            "n1_w155_results.json"), "W155 path drift"',
    '        for wprev in sorted(w for w in WAVE_CONFIGS if w < 155):',
    '            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(',
    '                PATHS.results_dir, "p2cal_ext",',
    '                WAVE_CONFIGS[wprev]["shard_subdir"])), \\',
    '                f"W155 shard dir collides with W{wprev}"',
    '        # W155 finalize cumulative deps: W17..W154 outputs ALL PRESENT',
    '        # (landed net chain head 734,811 = W154 bm-a r768 one-pass --',
    '        # ZERO in-flight upstream seats, clean precondition freeze',
    '        # window; the finalize merge loop derives the wave set from',
    '        # registry keys at run time and stays FAIL-CLOSED, r307',
    '        # two-state law).',
    '        for _depw in range(17, 155):',
    '            assert os.path.exists(os.path.join(',
    '                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\',
    '                f"W155 finalize cumulative dep (W{_depw} output) missing"',
    '        # finalize wave-set derivation face (r511 derive law): every',
    '        # registered wave below 155 composes; wave 15 excluded by',
    '        # design; SINGLE STATE (W2..W154 all registered -- no',
    '        # two-state seat disclosure needed at this freeze).',
    '        assert sorted(w for w in WAVE_CONFIGS if w < 155) == \\',
    '            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\',
    '            [w for w in range(16, 155)], \\',
    '            "W155 prior-wave set must derive from registry keys (no 15; " \\',
    '            "W2..W154 registered single state)"',
    '        assert os.path.exists(os.path.join(',
    '            PATHS.root, "research", "PERPETUAL_N1_W155_PREREG.md")), \\',
    '            "W155 per-wave prereg missing (materializer requirement)"',
    '        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"',
    '    finally:',
    '        _set_wave(2)',
])
r3 = ('    finally:\r\n        _set_wave(2)\r\n' + LEG + CRLF +
      '    # --- T-141 s2 lane face')

# --- edit 4: n1.py PASS snippet --------------------------------------------------
a4 = ('"results/_r767bma_w154_band_gate.json, law sec.4 W154 row, "\r\n'
      '          "r767 bm-a] "\r\n'
      '          "+ T-141 s2 "')
snip = CRLF.join([
    '          "+ W155 materializer face [same guard set, dep=W17..W154 "',
    '          "outputs ALL PRESENT (landed net chain head 734,811 = "',
    '          "W154 bm-a r768 one-pass, K=336,720 merged pool; ZERO "',
    '          "in-flight upstream seats), ONE HUNDRED-AND-FORTY-FIFTH "',
    '          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 144 "',
    '          "+ candidate) bm-a\'s seventy-first owned claim per "',
    '          "machine-derive (engine_owner==bm-a rows 70 + candidate), "',
    '          "A=FIRST-CLEAN past the registered W154 B band (staircase "',
    '          "fourteenth instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
    '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
    '          "mutual exclusion, hops=1), ADMIT receipt "',
    '          "results/_r768bma_w155_band_gate.json, law sec.4 W155 row, "',
    '          "r768 bm-a] "',
])
r4 = ('"results/_r767bma_w154_band_gate.json, law sec.4 W154 row, "\r\n'
      '          "r767 bm-a] "\r\n' + snip + CRLF + '          "+ T-141 s2 "')

edit(N1, [(a2, r2), (a3, r3), (a4, r4)])

# --- post-edit structural assertions --------------------------------------------
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 155 and len(pf.N1_BANDS) == 153, \
    "pf N1_BANDS row-count drift after W155 insert"
assert pf.N1_BANDS[155] == {"a": (355_804, 357_803),
                            "b_exit": (357_804, 358_003),
                            "engine_owner": "bm-a"}, "W155 row face drift"
assert pf.N1_BANDS[154] == {"a": (353_604, 355_603),
                            "b_exit": (355_604, 355_803),
                            "engine_owner": "bm-a"}, "W154 row survived (r560 no-replace law)"
print("post-edit structural assertions PASS: N1_BANDS 153 rows tail W155, "
      "W154 row intact")
