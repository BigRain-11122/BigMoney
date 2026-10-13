
# ---------------- phase 2: pairs (shift-derived anchors, final new text) ----------------
def pair(orig_old, new, n=1):
    global t
    old = shift_text(orig_old)
    c = t.count(old)
    assert c == n, f"PAIR FAIL count {c} != {n}: {old[:110]!r}"
    t = t.replace(old, new)

# --- header blocks ---
pair("""# 2026-10-13 19:2x bm-c r973 freeze window (upstream W1..W232 ALL LANDED, clean precondition): W233 five-face freeze splice editor.""",
"""# 2026-10-13 21:2x bm-c r976 freeze window (upstream W1..W233 ALL LANDED, clean precondition): W234 five-face freeze splice editor.""")
# regression guards for the window-label pair (new side must carry the SHIFTED wave faces)
assert t.count("(upstream W1..W233 ALL LANDED, clean precondition): W234 five-face") == 1
assert t.count("W233 five-face freeze splice editor") == 0

pair("""# present (W232 finalize one-pass r968 15:2x landed in-window 59856ff28; splice
# estate e58dbcda3 committed+pushed by r968 itself in the r968 window (session
# died post-S6 pre-closeout; residual estate absorbed by the r968-continuation cf3501cd9), net chain head 934,189, merged pool K=508,320,
# n1_w232_results.json machine-read) -- ZERO in-flight upstream seats,""",
"""# present (W233 finalize one-pass r974 19:4x landed in-window 260217d39 (r974 absorb closeout); splice
# estate 0ca920362 committed+pushed by the dead r973 window itself (session
# died pre-closeout; residual estate absorbed by r974), net chain head 936,389, merged pool K=510,520,
# n1_w233_results.json machine-read) -- ZERO in-flight upstream seats,""")

pair("""# Lineage: _w232bmc_freeze_edits.py pattern (proven live-fire freeze,
# e58dbcda3 committed+pushed by r968 itself, machine-verified by
# the r968-continuation closeout receipt) + r787 preflight law + r609""",
"""# Lineage: _w233bmc_freeze_edits.py pattern (proven live-fire freeze,
# 0ca920362 committed+pushed by the dead r973 window itself, machine-verified by
# the r974-absorb closeout receipt) + r787 preflight law + r609""")

pair("""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<233>/
# range(16,233)/below-233 triple is count-asserted atomically; the W232
# block's own w<232 face is legitimate prior-wave boundary, not stale).""",
"""# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<234>/
# range(16,234)/below-234 triple is count-asserted atomically; the W233
# block's own w<233 face is legitimate prior-wave boundary, not stale).""")

# --- transitive window slide (multi-wave faces the global shifts corrupt) ---
pair('f"W232+W231+W230+W229+W228 finalize products present "',
     'f"W233+W232+W231+W230+W229 finalize products present "')

pair("""# (chain-order precondition; W231/W230/W229/W228 finalize are transitive deps of the
# W233 freeze and are belt-and-braces checked here + enforced by the block's
# cumulative-deps assert range(17, 233) at selftest time)""",
"""# (chain-order precondition; W232/W231/W230/W229 finalize are transitive deps of the
# W234 freeze and are belt-and-braces checked here + enforced by the block's
# cumulative-deps assert range(17, 234) at selftest time)""")

# --- structural-choice provenance fixup (post-shift anchors) ---
pair("""# (r968 window editor, estate committed+pushed by r968 itself as e58dbcda3), structure known. The W232 block span ends where the""",
"""# (dead-r973 window editor, estate committed+pushed by the dead r973 window itself as 0ca920362), structure known. The W233 block span ends where the""")

# --- seat/prose fixups (post-shift anchors) ---
pair(" " + "MSG-20261013-1345-bmc, executed bm-c r968 (seat 8d3a1b78a); splice e58dbcda3 r968 window committed+pushed by r968 itself (estate machine-verified); engine self-burn 12/12 (5c90051e0+776b15270); finalize one-pass r968 15:2x; six-gate PRE-FINALIZE correct phase standing law held, seventh consecutive), ",
     " " + "MSG-20261013-1530-bmc, executed bm-c r973 (seat dd38a9da8); splice 0ca920362 dead-r973 window committed+pushed by the dead r973 window itself (estate machine-verified); engine self-burn 12/12 (6c1587483+d4cce3ffe); finalize one-pass r974 19:4x; six-gate PRE-FINALIZE correct phase standing law held, eighth consecutive), ")

pair(''' "    #     MSG-20261013-1345-bmc, executed bm-c r968 (seat 8d3a1b78a); splice",
 "    #     e58dbcda3 r968 window committed+pushed by r968 itself (estate",
 "    #     machine-verified); engine self-burn 12/12 (5c90051e0+776b15270) + finalize one-pass r968 15:2x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, seventh",
 "    #     consecutive -- THIS W233 cycle runs PRE-FINALIZE likewise), honest note)",''',
''' "    #     MSG-20261013-1530-bmc, executed bm-c r973 (seat dd38a9da8); splice",
 "    #     0ca920362 dead-r973 window committed+pushed by the dead r973 window itself (estate",
 "    #     machine-verified); engine self-burn 12/12 (6c1587483+d4cce3ffe) + finalize one-pass r974 19:4x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held, eighth",
 "    #     consecutive -- THIS W234 cycle runs PRE-FINALIZE likewise), honest note)",''')

# --- correctness delta (a): probe-receipt ordinal aging face fixed (disclosed header) ---
pair("ordinal machine-read NINETY-THIRD per probe receipt",
     "ordinal machine-read NINETY-FOURTH per probe receipt")

pair('"machine-checkable = A-hops-prior-B staircase NINETY-THIRD ",',
     '"machine-checkable = A-hops-prior-B staircase NINETY-FOURTH ",')

# --- estate/parity count pairs ---
pair('assert par_sec.count("assert pf.N1_BANDS[") == 88 \\',
     'assert par_sec.count("assert pf.N1_BANDS[") == 89 \\')
pair("    and int(_estate_ws[84]) == 226 \\\n    and int(_estate_ws[85]) == 227 \\\n    and int(_estate_ws[86]) == 228 \\\n    and int(_estate_ws[87]) == 229, \\",
     "    and int(_estate_ws[84]) == 226 \\\n    and int(_estate_ws[85]) == 227 \\\n    and int(_estate_ws[86]) == 228 \\\n    and int(_estate_ws[87]) == 229 \\\n    and int(_estate_ws[88]) == 230, \\")
pair('assert par_full.count("assert pf.N1_BANDS[") == 90, \\',
     'assert par_full.count("assert pf.N1_BANDS[") == 91, \\')
pair('    f"full parity span {par_full.count(\'assert pf.N1_BANDS[\')} != 90 (69 estate + W211..W227 legs + W228 leg + W229 leg + W230 leg + W231 leg)"',
     '    f"full parity span {par_full.count(\'assert pf.N1_BANDS[\')} != 91 (69 estate + W211..W228 legs + W229 leg + W230 leg + W231 leg + W232 leg)"')
pair("88-row cut", "89-row cut", 1)
pair("(91 rows: estate 69", "(92 rows: estate 69", 1)   # STRUCTURAL CHOICE face (receipt note fixed by its own block pair)

# --- cfg/row key literals (self-keyed gate strings, colon-continuation form) ---
pair("assert new_cfg.count('233: {\"batch\": \"PERPETUAL-N1-W233\"') == 1",
     "assert new_cfg.count('234: {\"batch\": \"PERPETUAL-N1-W234\"') == 1")
pair("assert n1_t4.count('233: {\"batch\": \"PERPETUAL-N1-W233\"') == 1",
     "assert n1_t4.count('234: {\"batch\": \"PERPETUAL-N1-W234\"') == 1")

# --- post-edit gate value-source fix (pf_mod faces stay [232] under the bare shift; [233] value source) ---
pair("""assert n1_t4.count(f'assert pf.N1_BANDS[232] == {{"a": ({fmt(pf_mod.N1_BANDS[232]["a"][0])}, {fmt(pf_mod.N1_BANDS[232]["a"][1])}),') == 1""",
     """assert n1_t4.count(f'assert pf.N1_BANDS[233] == {{"a": ({fmt(pf_mod.N1_BANDS[233]["a"][0])}, {fmt(pf_mod.N1_BANDS[233]["a"][1])}),') == 1""")

# --- w230_leg def -> w233_leg def (drop oldest leg, add newest; content [233]) ---
pair("""w230_leg = [
 f'        assert pf.N1_BANDS[230] == {{"a": ({fmt(pf_mod.N1_BANDS[230]["a"][0])}, {fmt(pf_mod.N1_BANDS[230]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[230]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[230]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W230 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""",
"""w233_leg = [
 f'        assert pf.N1_BANDS[233] == {{"a": ({fmt(pf_mod.N1_BANDS[233]["a"][0])}, {fmt(pf_mod.N1_BANDS[233]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[233]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[233]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W233 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]""")

# --- receipt upstream + transitive block ---
pair('''  "w232_upstream": {"freeze_sha": w232_freeze_sha, "prereg_sha": w232_prereg_sha,
                    "ledger_total": w232_total, "merged_n": w232_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r968 splice (W232 freeze landed e58dbcda3 r968 window, estate committed+pushed by r968 itself; session died post-S6 pre-closeout, residual absorbed by the r968-continuation) + engine self-burn 12/12 (5c90051e0+776b15270) + r968 finalize one-pass 15:2x 59856ff28 (six-gate PRE-FINALIZE correct phase -- standing law held, seventh consecutive)"},''',
'''  "w233_upstream": {"freeze_sha": w233_freeze_sha, "prereg_sha": w233_prereg_sha,
                    "ledger_total": w233_total, "merged_n": w233_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r973 splice (W233 freeze landed 0ca920362 dead-r973 window, estate committed+pushed by the dead r973 window itself; session died pre-closeout, residual absorbed by r974) + engine self-burn 12/12 (6c1587483+d4cce3ffe) + r974 finalize one-pass 19:4x 260217d39 (six-gate PRE-FINALIZE correct phase -- standing law held, eighth consecutive)"},''')

pair('''  "w231_transitive": {"finalize_product": "results/perpetual_faces/n1_w231_results.json present (belt-and-braces gate; ledger 931,989 / K=506,120)"},''',
     '''  "w232_transitive": {"finalize_product": "results/perpetual_faces/n1_w232_results.json present (belt-and-braces gate; ledger 934,189 / K=508,320)"},''')

# --- receipt parity + family6 notes ---
pair("full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W229 legs + W230 leg + W231 leg + W232 leg -> W233 block = 91 rows ending at W232;",
     "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W230 legs + W231 leg + W232 leg + W233 leg -> W234 block = 92 rows ending at W233;")

pair('"note": "W232 editor family-6 gate carried forward: new block LHS w<233 x3 / RHS range(16,233)+range(17,233) / comment below-233 count-asserted ATOMICALLY before splice; W232 block\'s own w<232 face = legitimate prior-wave boundary (not stale)"',
     '"note": "W233 editor family-6 gate carried forward: new block LHS w<234 x3 / RHS range(16,234)+range(17,234) / comment below-234 count-asserted ATOMICALLY before splice; W233 block\'s own w<233 face = legitimate prior-wave boundary (not stale)"')

# --- receipt ordinal faces ---
pair('''                    "probe_receipt_bmc_ordinal_face": 63,''',
     '''                    "probe_receipt_bmc_ordinal_face": 64,''')

# ---------------- phase 3: sentinel restores (with W234 additions) ----------------
rep("@@KEPT@@", KEPT_ORIG + "\nassert n1_t4.count('    # --- W233 materializer face') == 1  # prior block kept (W233 splice landed 0ca920362 dead-r973 window, estate machine-verified; committed+pushed by the dead r973 window itself, session died pre-closeout, residual estate absorbed by r974 260217d39)", 1)
rep("@@LIVE@@", LIVE_ORIG.replace('"w232_block_kept": 1},', '"w232_block_kept": 1, "w233_block_kept": 1},'), 1)
rep("@@LEG231@@", LEG231_ORIG, 1)
rep("@@LEG232@@", LEG232_ORIG, 1)
# ASM restore = machine-derived aging of the extracted face (descending-order leg
# aging: w232->w233 first, then w231->w232, then w230->w231; no cascades since each
# target is lower than every remaining source)
ASM_NEW = (ASM_ORIG.replace("w232_leg", "w233_leg")
                  .replace("w231_leg", "w232_leg")
                  .replace("w230_leg", "w231_leg"))
assert ASM_NEW == "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w231_leg) + EOL + EOL.join(w232_leg) + EOL + EOL.join(w233_leg) + EOL + EOL.join(tail) + EOL", f"ASM_NEW drift: {ASM_NEW!r}"
rep("@@ASM@@", ASM_NEW, 1)

# ---------------- phase 4: validation (fail-closed) ----------------
# kept-line legit faces (KEPT-internal splice history carries W229..W232 verbatim)
assert t.count("e58dbcda3") == 1, f"kept-line e58dbcda3 count {t.count('e58dbcda3')} != 1"
assert t.count("r968 window") == 1, f"kept-line r968 window != 1"
assert t.count("r968 itself") == 1, f"kept-line r968 itself != 1"
assert t.count("r968-continuation") == 1, f"kept-line r968-continuation != 1"
assert t.count("W232") == 11, f"upstream W232 count {t.count('W232')} != 11 (2 KEPT + 8 shift-landed + 1 transitive-prose)"
# upstream-seat provenance faces (P9/P10 prose carries the W233 seat origin sha)
assert t.count("dd38a9da8") == 2, f"upstream seat-origin dd38a9da8 count {t.count('dd38a9da8')} != 2"

stale = ["(527_404, 529_403)", "(529_404, 529_603)",
 "2a21ef7cc4eaaa70375c7e4baec99f423488d5e2", "SEVENTEEN-level", "MSG-20261013-1345-bmc",
 "r973 freeze window", "r973 freeze-window bundle",
 "expect 222/62", "precedent 221/61 pre-splice", "splice 222/62", "== 222 and len", "rows 222 + candidate",
 "rows 62 + candidate", "bmc_ordinal=63", "63rd", "sixty-third",
 "NINETY-THIRD instance", "NINETY-THIRD",
 "TWO HUNDRED AND THIRTY-THIRD", "934_189", "508_320", "(expect 934,189",
 "r968 15:2x", "r968 seat-time", "probe receipt @ r968 window",
 "twenty-second consecutive", "seventh consecutive",
 "_w233bmc_20261013_probe_receipt.json", "_w233bmc_freeze_receipt.json",
 "w230_leg", "n1w233-", "N1_BANDS.get(232)", "if w < 233)", "if w < 232", "w<232 leaked",
 "range(16, 233)", "range(16,233)", "range(17, 233)", "below 233 composes", "below-233",
 "m230", "_c232", "n3r1_used233", "arith_a233", "arith_b233",
 "N1_BANDS\\[230\\]",
 "W234+ projection", "naive W234 A window", "W234 freezer", "W234+ freezer",
 "downstream W234 seat",
 "59856ff28", "5c90051e0", "776b15270", "cf3501cd9",
 "executed bm-c r968",
 "8d3a1b78a", "e58dbcda3x-guard", "r968-continuationx-guard",
 "@@KEPT@@", "@@LIVE@@", "@@LEG231@@", "@@LEG232@@", "@@ASM@@", "1193b255531f7aadcdff050069371c5e5169b11f" + "x-guard",
 '234: {"batch": "PERPETUAL-N1-W234"x-guard']
for s in stale:
    c = t.count(s)
    assert c == 0, f"STALE TOKEN {s!r} count {c} != 0"

must_one = ["_set_wave(234)",
 "f'{CFG_I}234: ", "f'{ROW_I}234: ", "ROW_I + '234: {\"a\"'", '"wave": 234',
 "MSG-20261013-1955-bmc.md", "936_389", "510_520",
 "(expect 936,389 / 510,520)", "(529_604, 531_603)", "(531_604, 531_803)",
 "int(_estate_ws[88]) == 230", "1193b255531f7aadcdff050069371c5e5169b11f", "EIGHTEEN-level",
 '"probe_receipt_bmc_ordinal_face": 64,', '"w233_block_kept": 1}',
 "N1_BANDS.get(233)", "r974 probe leg0", "r974 seat-time live face",
 "r976 prereg derived", "89-row cut", '== 89 \\', '== 91, \\',
 "n1w234-0of12", "n1w234-11of12", "seat MSG-1234 tail",
 "ordinal machine-read NINETY-FOURTH per probe receipt"]
for s in must_one:
    c = t.count(s)
    assert c == 1, f"MUST-ONE {s!r} count {c} != 1"

# --- calibration dump (dbg6): actual counts for the uncertain final faces ---
_cal = {s: t.count(s) for s in ["W233", "w233_", "n1_w234", "n1_w234_results", "n1_w233_results",
 "0ca920362", "260217d39", "r974 19:4x", "eighth consecutive", "92 rows", "w233_a_tail",
 "w233_b_tail", "w233_freeze_sha", "w233_prereg_sha", "w234_prereg_sha", "w234_receipt_sha",
 "W234", "w234_", "w231_leg", "w232_leg", "w233_leg", "r976", "twenty-third consecutive",
 "NINETY-FOURTH instance", "NINETY-FIFTH instance anticipated", "dd38a9da8",
 "n1_w234", "MSG-20261013-1955-bmc", "MSG-20261013-1530-bmc", "64th", "sixty-fourth",
 "TWO HUNDRED AND THIRTY-FOURTH", "W235+ projection", "naive W235 A window",
 "6c1587483", "d4cce3ffe", "e58dbcda3", "r976 freeze window",
 "WAVE_CONFIGS[234]", "WAVE_CONFIGS[233]", "w232_out_path", "w233_total",
 "w232_transitive", "w233_upstream",
 "assert pf.N1_BANDS[233] ==", "assert pf.N1_BANDS[232] ==", "assert pf.N1_BANDS[231] ==",
 "n1_w233_results.json", "n1_w234_results.json", "engine_owner rows 223 + candidate",
 "rows 223 + candidate", "234: {\"batch\""]}
open(os.path.join(HERE, "_w234bmc_dbg6_counts.json"), "w", encoding="utf-8").write(json.dumps(_cal, indent=1))
print("DBG6 COUNTS:", json.dumps(_cal))

assert t.count("MSG-20261013-1955-bmc") == 4
assert t.count('234: {"batch": "PERPETUAL-N1-W234"') == 2   # new_cfg gate + n1_t4 post-edit gate
assert t.count("MSG-20261013-1530-bmc") == 2          # upstream seat references
assert t.count("W235+ projection") == 2
assert t.count("naive W235 A window") == 2
assert t.count("NINETY-FIFTH instance anticipated") == 2
assert t.count("NINETY-FOURTH instance") == 5
assert t.count("TWO HUNDRED AND THIRTY-FOURTH") == 3
assert t.count("sixty-fourth") == 2
assert t.count("64th") == 6
assert t.count("bmc_ordinal=64") == 3
assert t.count("_w234bmc_20261013_probe_receipt.json") == 9
assert t.count("_w234bmc_freeze_receipt.json") == 1
assert t.count("w230_leg") == 0
assert t.count("w231_leg") == 2
assert t.count("w232_leg") == 2
assert t.count("w233_leg") == 2
assert t.count('"w232_transitive"') == 1
assert t.count('"w233_upstream"') == 2
assert t.count("assert pf.N1_BANDS[233] ==") == 2     # w233_leg def + post-edit gate
assert t.count("assert pf.N1_BANDS[232] ==") == 1     # w232_leg def (sentinel-kept)
assert t.count("assert pf.N1_BANDS[231] ==") == 1     # w231_leg def (sentinel-kept)
assert t.count("WAVE_CONFIGS[234]") == 2             # band-facts self asserts
assert t.count("WAVE_CONFIGS[233]") == 3             # upstream mirror asserts
assert t.count("n1_w234") == 5
assert t.count("n1_w233_results") == 4               # upstream refs (shift-landed)
assert t.count("n1_w234_results") == 2               # self path refs (shift-landed)
assert t.count("0ca920362") >= 6
assert t.count("260217d39") == 4   # SEAT_ORIGIN 1 + header finalize 1 + receipt finalize 1 + KEPT-restore 1
assert t.count("r974 19:4x") == 3
assert t.count("r976 freeze window") == 4
assert t.count("r976 freeze-window bundle") == 2
assert t.count("twenty-third consecutive") == 2
assert t.count("92 rows") == 2
assert t.count("if w < 234)") == 5
assert t.count("range(16, 234)") == 2
assert t.count("range(17, 234)") == 3
assert t.count("registered wave below 234 composes") == 2
assert t.count("eighth consecutive") == 2
assert t.count("w233_a_tail") == 14
assert t.count("w233_b_tail") == 9
assert t.count("w233_freeze_sha") == 6
assert t.count("w234_prereg_sha") == 5
assert t.count("w234_receipt_sha") == 4
assert t.count("6c1587483+d4cce3ffe") == 3
assert t.count("1955") >= 1 and t.count("1530-bmc.md") == 0

open(OUT, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(OUT, doraise=True)
print(f"DERIVE OK: {OUT} ({len(t)} chars, template 50218); py_compile green")
print("NEXT: run the editor (gates fail-closed) -> pf/n1 selftest -> pathspec commit+push -> PRE-FINALIZE six-gate -> engine self-burn verify (2-cycle n1_w234 growth)")
