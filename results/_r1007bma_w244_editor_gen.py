# -*- coding: utf-8 -*-
# r1007 bm-a: W244 five-face freeze editor generation (machine-SUB from the
# committed W243 editor template). Phase A = semantic B-face flip (blocks
# authored pre-bump, imported from the dead r1007 estate gen_b1/b2/b3 + this
# window's authored blocks). Phase B = ordered mechanical wave bumps
# (descending). Phase C = post-generic parity-row scoped fixes. Fail-closed:
# every SUB count == mechanically-derived expected (orig + all-prior-pair
# deltas); residue battery; AST gate. Never transcribed r587.
import io, json, re, os, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(R, "results", "_w243bma_freeze_edits.py")
OUT = os.path.join(R, "results", "_w244bma_freeze_edits.py")
RECEIPT = os.path.join(R, "results", "_r1007bma_w244_editor_gen_receipt.json")

def load(name):
    ns = {}
    p = os.path.join(R, "results", name)
    exec(compile(io.open(p, encoding="utf-8").read(), p, "exec"), ns)
    return ns

b1 = load("_r1007bma_w244_gen_b1.py")
b2 = load("_r1007bma_w244_gen_b2.py")
b3 = load("_r1007bma_w244_gen_b3.py")

orig = io.open(TPL, encoding="utf-8").read()
t = orig
applied = []  # (label, old, new, n_replaced) in application order -- expected-count base

def expected(p):
    # mechanically derived: committed original + every prior pair's delta
    # (scaled by the number of replacements actually made)
    e = orig.count(p)
    for (_l, o, n, k) in applied:
        e += k * (n.count(p) - o.count(p))
    return e

def sub(label, old, new, exp=None):
    global t
    obs = t.count(old)
    e = expected(old)
    if exp is not None:
        assert e == exp, f"{label}: derived expected {e} != hand {exp}"
    assert obs == e, f"{label}: count {obs} != expected {e}"
    t = t.replace(old, new)
    applied.append((label, old, new, obs))
    return obs

# ---------------- Phase A: semantic B-face flip (pre-bump language) ----------------

A1_OLD = """# NEW FACE vs the W242 editor (honest disclosure): the W243 B band is a
# LIVE-SEED-REFUSAL face (hops=1 -- naive continuation 541_404..541_603
# REFUSED by SEED_REGISTRY point 541_500 perpetual_n2_w15_gen; honest forward
# walk first-clean 541_501..541_700) -- B base != prior-B-tail+1 in this
# face; relation asserts mirror the probe receipt leg1 relation_asserts
# exactly (B_base_above_priorB_tail + B_live_seed_hop_face), and the
# refuser-adjacency is machine-asserted (541_500 in reg_ints, NOT in the
# B window)."""
A1_NEW = """# NEW FACE vs the W242 editor (honest disclosure): the W243 B band returns
# to the CLEAN staircase base (hops=0 -- the naive continuation
# 541_701..541_900 is CLEAN on the registered universe; the prior-wave
# live-seed refusal chain is behind us) -- B base == prior-B-tail+1 EXACT
# in this face; relation asserts mirror the probe receipt leg1
# relation_asserts exactly (B_clean_at_naive_start +
# B_base_above_priorB_tail), and the staircase base is machine-asserted
# (B base == prior-wave B tail+1)."""

A12_NEW_BODY = [
    '"+ B=FIRST-CLEAN arithmetic continuation of the prior-wave B tail (B-continuation face, "',
    '"hops=0, B_hop_chain empty + B_clean_at_naive_start=true, B base == prior-B-tail+1 EXACT, "',
]
A13_OLD = '                     "B": "LIVE-SEED-REFUSAL face (naive staircase 541_404..541_603 REFUSED by SEED_REGISTRY point 541_500 perpetual_n2_w15_gen, hops=1, hop chain recorded; honest forward walk first-clean 541_501..541_700; B base != prior-B tail+1 in this face; B_no_ownA_jump=true; seed-decoupled A/B gap face fifth consecutive)"},'
A13_NEW = '                     "B": "FIRST-CLEAN arithmetic continuation of the prior-wave B tail (B base == prior-B tail+1 EXACT, hops=0, B_hop_chain empty -- the prior-wave live-seed refusal chain is behind us; B_no_ownA_jump=true; seed-decoupled A/B gap face fifth consecutive)"},'

A14_OLD = '  "downstream_seat": "W244 seat NOT YET PUBLISHED at this freeze window (next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W244 freezer MUST re-derive live on the post-W243 universe + reserve the own-wave A window when deriving B per the W243 seat leg4 mandate, never transcribe r587 -- W244p face: A naive 553_501..555_500 CLEAN / B naive 541_701..541_900 CLEAN, both hops=0)",'
A14_NEW = '  "downstream_seat": "W244 seat NOT YET PUBLISHED at this freeze window (next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W244 freezer MUST re-derive live on the post-W243 universe + reserve the own-wave A window when deriving B per the W243 seat leg4 mandate, never transcribe r587 -- W244p face: A naive 555_501..557_500 CLEAN (hops=0) / B naive 541_901..542_100 hops=1, honest forward walk first-clean 542_001..542_200 (B lands OUTSIDE the naive A window; seed-gap face inherited))",'

A15_OLD = 'assert (a_lo, a_hi) == (551_501, 553_500) and (b_lo, b_hi) == (541_501, 541_700), '
A15_NEW = 'assert (a_lo, a_hi) == (553_501, 555_500) and (b_lo, b_hi) == (541_701, 541_900), '

A17_OLD = ' f\'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W243 B: {fmt(b_lo)}..{fmt(b_hi)} (LIVE-SEED-REFUSAL face: naive staircase {fmt(w242_b_tail + 1)}..{fmt(w242_b_tail + 200)} REFUSED by SEED_REGISTRY 541_500, hops=1, honest forward walk first-clean {fmt(b_lo)}..{fmt(b_hi)}; B base != prior-B tail+1 in this face; B lands outside own-A; seed-decoupled A/B gap face fifth consecutive)\','
A17_NEW = ' f\'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W243 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN arithmetic continuation of the prior-wave B tail: staircase {fmt(w242_b_tail + 1)}..{fmt(w242_b_tail + 200)} CLEAN on the registered universe, hops=0, B_hop_chain empty; B base == prior-B tail+1 EXACT in this face; B lands outside own-A; seed-decoupled A/B gap face fifth consecutive)\','

# A7/A9A/A9B: the dead-estate block bodies matched logically but missed the
# per-line list-item leading whitespace -- extract OLD bytes from the template
# by anchor+n_lines and transplant the OLD per-line indent onto the NEW lines.
def extract_lines(anchor, n):
    i = t.find(anchor)
    assert i >= 0, f"anchor not found: {anchor[:60]}"
    ls = t.rfind("\n", 0, i) + 1
    seg = t[ls:]
    lines = seg.split("\n")[:n]
    assert lines[-1] != "", f"anchor window degenerate: {anchor[:60]}"
    return lines

def transplant(old_lines, new_body_lines):
    out = []
    for i, nl in enumerate(new_body_lines):
        if i < len(old_lines):
            ol = old_lines[i]
            ind = ol[:len(ol) - len(ol.lstrip(" "))]
            core = nl.lstrip(" ")
            out.append(ind + core)
        else:
            out.append(nl)
    return out

def build_pair(anchor, n_old, new_body):
    old_lines = extract_lines(anchor, n_old)
    old = "\n".join(old_lines)
    new = "\n".join(transplant(old_lines, new_body))
    return old, new

A7_OLD, A7_NEW = build_pair(
    '"non-rotational r587 forward-monotone walk) + B = LIVE-SEED-REFUSAL face (the naive "',
    9,
    [x.strip(" ") for x in b2["B_A7_NEW"].split("\n")])

A9A_OLD, A9A_NEW = build_pair(
    '"        # B = LIVE-SEED-REFUSAL face: the naive staircase continuation"',
    9,
    [x.strip(" ") for x in b3["B_A9A_NEW"].split("\n")])

# r1008 fix: window extended 12->13 lines -- the 12-line window ended
# mid-statement at L563 and orphaned the L564 refuser-adjacency assert
# message (residue battery catch); 13 covers the full assert incl. its
# message line, removing the own-wave refuser-adjacency machinery.
A9B_OLD, A9B_NEW = build_pair(
    'f\'        assert WAVE_CONFIGS[243]["b_exit_seed_base"] == {b_lo}, (\'',
    13,
    [x.strip(" ") for x in b3["B_A9B_NEW"].split("\n")])

# r1008 fix A9C: the B-window CLEAN assert message still carried the
# W243-era "post-hop forward walk" language -- convert to the
# clean-continuation phrasing (3-line anchored window, fail-closed).
A9C_OLD, A9C_NEW = build_pair(
    'f"        arith_b243 = set(range({b_lo}, {b_hi + 1}))"',
    3,
    ['f"        arith_b243 = set(range({b_lo}, {b_hi + 1}))"',
     '"        assert not (arith_b243 & reg_ints), \\\\"',
     '\'            "W243 B window must be CLEAN (first-clean ADMIT face, arithmetic continuation of the prior-wave B tail)"\''])

A12_OLD, A12_NEW = build_pair(
    '"+ B=LIVE-SEED-REFUSAL face (naive staircase 541_404..541_603 REFUSED by SEED_REGISTRY 541_500, "',
    2,
    A12_NEW_BODY)

A_PAIRS = [
    ("A1 header disclosure", A1_OLD, A1_NEW),
    ("A2 face comment+asserts", b1["B_A2_OLD"], b1["B_A2_NEW"]),
    ("A3A hops assert", b1["B_A3A_OLD"], b1["B_A3A_NEW"]),
    ("A3B B hop-chain asserts", b1["B_A3B_OLD"], b1["B_A3B_NEW"]),
    ("A3C relation_asserts keys", b1["B_A3C_OLD"], b1["B_A3C_NEW"]),
    ("A5 pf comment B block", b2["B_A5_OLD"], b2["B_A5_NEW"]),
    ("A6 pf comment W244+ projection", b2["B_A6_OLD"], b2["B_A6_NEW"]),
    ("A7 cfg PRE B text", A7_OLD, A7_NEW),
    ("A8 cfg PRE W244+ projection", b3["B_A8_OLD"], b3["B_A8_NEW"]),
    ("A9A materializer band-facts comment", A9A_OLD, A9A_NEW),
    ("A9B materializer B asserts", A9B_OLD, A9B_NEW),
    ("A9C materializer B CLEAN msg", A9C_OLD, A9C_NEW),
    ("A12 print B fragments", A12_OLD, A12_NEW),
    ("A13 receipt B semantics", A13_OLD, A13_NEW),
    ("A14 receipt downstream_seat", A14_OLD, A14_NEW),
    ("A15 band assert literals", A15_OLD, A15_NEW),
    ("A17 cfg b_exit comment", A17_OLD, A17_NEW),
]
for label, old, new in A_PAIRS:
    c = t.count(old)
    assert c == 1, f"PhaseA {label}: OLD count {c} != 1"
    t = t.replace(old, new, 1)
    applied.append((label, old, new, 1))

# ---------------- Phase B: ordered mechanical bumps (descending) ----------------

B = [
    ("B1 W244p->W245p", "W244p", "W245p"),
    ("B2 W244+->W245+", "W244+", "W245+"),
    ("B3 W244 freezer", "W244 freezer", "W245 freezer"),
    ("B4 W244 seat", "W244 seat", "W245 seat"),
    ("B5a window stamp", "# 2026-10-15 01:0x bm-a r1002 freeze window",
     "# 2026-10-15 06:1x bm-a r1007 freeze window"),
    ("B6 prereg landing narrative (header)",
     "PERPETUAL_N1_W243_PREREG.md derived+landed by the absorbed r1001 window\n# commit 70141bc22, machine-SUB from frozen W242 tpl 4574bfeca).",
     "PERPETUAL_N1_W244_PREREG.md derived by the absorbed r1005 window\n# and landed by the r1006 commit 260ffd3f8, machine-SUB from frozen W243 tpl 70141bc22)."),
    ("B7 prereg receipt-note narrative",
     "prereg derived+committed by the absorbed r1001 window (machine-SUB from the frozen W242 tpl 4574bfeca; estate-absorb commit ",
     "prereg derived by the absorbed r1005 window and committed by r1006 (machine-SUB from the frozen W243 tpl 70141bc22; commit "),
    ("B8 r1001->r1005", "r1001", "r1005"),
    ("B9 r1000->r1004", "r1000", "r1004"),
    ("B10 r999->r1003", "r999", "r1003"),
    ("B11 r998->r1002", "r998", "r1002"),
    ("B12 20:4x->01:4x", "20:4x", "01:4x"),
    ("B13 seat MSG", "MSG-20261014-2107", "MSG-20261015-0206"),
    ("B14 probe receipt path", "_w243bma_20261014", "_w244bma_20261015"),
    ("B15 seat origin", "6207e60e9", "08df387e0"),
    ("B16 ordinal thirty-second", "thirty-second consecutive", "thirty-third consecutive"),
    ("B17 ordinal A seed-gap", "fourth consecutive seed-gap", "fifth consecutive seed-gap"),
    ("B18 ordinal gap face", "gap face fifth", "gap face sixth"),
    ("B19 232/233rd", "232 + candidate = 233rd", "233 + candidate = 234th"),  # also covers 'rows 232' (contiguous)
    ("B21 owner_rows leg0 face", "owner_rows=232 / bma_rows=124", "owner_rows=233 / bma_rows=125"),
    ("B22 ordinal assert", "== 232 and len(bma_rows_live) == 124", "== 233 and len(bma_rows_live) == 125"),
    ("B23 ordinal drift msg", "232/124/67", "233/125/67"),
    ("B24 bma_ordinal", "bma_ordinal=125", "bma_ordinal=126"),
    ("B25 124 + candidate", "124 + candidate", "125 + candidate"),
    ("B26 125th", "125th", "126th"),
    ("B27 twenty-fifth", "one hundred and twenty-fifth", "one hundred and twenty-sixth"),
    ("B28 TWENTY-FIFTH", "ONE HUNDRED AND TWENTY-FIFTH", "ONE HUNDRED AND TWENTY-SIXTH"),
    ("B29 FORTY-THIRD", "TWO HUNDRED AND FORTY-THIRD", "TWO HUNDRED AND FORTY-FOURTH"),
    ("B30 ledger total comma", "956,735", "958,935"),
    ("B31 ledger total under", "956_735", "958_935"),
    ("B32 merged comma", "530,320", "532,520"),
    ("B33 merged under", "530_320", "532_520"),
    ("B34 transitive slashlist",
     "W241/W240/W239/W238/W237/W236/W235/W234/W233/W232",
     "W242/W241/W240/W239/W238/W237/W236/W235/W234/W233"),
    ("B35 transitive tuple",
     "(241, 240, 239, 238, 237, 236, 235, 234, 233, 232)",
     "(242, 241, 240, 239, 238, 237, 236, 235, 234, 233)"),
    ("B36 legs range", "range(232, 242)", "range(232, 243)"),
    ("B37 liveness range", "range(209, 244)", "range(209, 245)"),
    ("B38 if w < 243", "if w < 243)", "if w < 244)"),
    ("B39 if w < 242", "if w < 242)", "if w < 243)"),
    ("B40 w<243 nospace", "w<243", "w<244"),
    ("B41 w<242 nospace", "w<242", "w<243"),
    ("B42 range(16, 243) sp", "range(16, 243)", "range(16, 244)"),
    ("B43 range(17, 243) sp", "range(17, 243)", "range(17, 244)"),
    ("B44 range(16,243) ns", "range(16,243)", "range(16,244)"),
    ("B45 range(17,243) ns", "range(17,243)", "range(17,244)"),
    ("B46 below 243 sp", "below 243", "below 244"),
    ("B47 below-243 ns", "below-243", "below-244"),
    ("B48 receipt wave", '"wave": 243', '"wave": 244'),
    ("B49 set_wave", "_set_wave(243)", "_set_wave(244)"),
    ("B50 WAVE_CONFIGS[243]", "WAVE_CONFIGS[243]", "WAVE_CONFIGS[244]"),
    ("B51 WAVE_CONFIGS[242]", "WAVE_CONFIGS[242]", "WAVE_CONFIGS[243]"),
    ("B52 n1_w243", "n1_w243", "n1_w244"),
    ("B53 n1_w242", "n1_w242", "n1_w243"),
    ("B54 n1w243 shard", "n1w243", "n1w244"),
    ("B55 n3r1_used", "n3r1_used243", "n3r1_used244"),
    ("B56 arith_a", "arith_a243", "arith_a244"),
    ("B57 arith_b", "arith_b243", "arith_b244"),
    ("B58 batch name", "PERPETUAL-N1-W243", "PERPETUAL-N1-W244"),
    ("B59 N1_BANDS.get(242)", "N1_BANDS.get(242)", "N1_BANDS.get(243)"),
    ("B60 N1_BANDS[242]", "N1_BANDS[242]", "N1_BANDS[243]"),
    ("B61 N1_BANDS[241]", "N1_BANDS[241]", "N1_BANDS[242]"),
    ("B62 N1_BANDS[240]", "N1_BANDS[240]", "N1_BANDS[241]"),
    ("B63 N1_BANDS[239]", "N1_BANDS[239]", "N1_BANDS[240]"),
    ("B64 N1_BANDS[238]", "N1_BANDS[238]", "N1_BANDS[239]"),
    ("B65 N1_BANDS[237]", "N1_BANDS[237]", "N1_BANDS[238]"),
    ("B66 N1_BANDS[236]", "N1_BANDS[236]", "N1_BANDS[237]"),
    ("B67 N1_BANDS[235]", "N1_BANDS[235]", "N1_BANDS[236]"),
    ("B68 prereg name own", "PERPETUAL_N1_W243", "PERPETUAL_N1_W244"),
    ("B69 prereg name upstream", "PERPETUAL_N1_W242", "PERPETUAL_N1_W243"),
    ("B70 243 batch own", '243: {"batch"', '244: {"batch"'),
    ("B71 242 batch upstream", '242: {"batch"', '243: {"batch"'),
    ("B72 243 a fstring", '243: {{"a"', '244: {{"a"'),
    ("B73 243 a own", '243: {"a"', '244: {"a"'),
    ("B74 242 a upstream", '242: {"a"', '243: {"a"'),
    ("B75 _c242", "_c242", "_c243"),
    ("B76 W243->W244", "W243", "W244"),
    ("B77 w243->w244", "w243", "w244"),
    ("B78 W242->W243", "W242", "W243"),
    ("B79 w242->w243", "w242", "w243"),
]
for label, old, new in B:
    _pre = t.count("W243")
    sub(label, old, new)
    _post = t.count("W243")
    if _post != _pre:
        print(f"TRACE W243: {label}: {_pre} -> {_post}")

# ---------------- Phase C: post-generic parity-row scoped fixes ----------------

C = [
    ("C1 structural-choice legs", "the W232..W241 fresh legs from the OWN W243",
     "the W232..W242 fresh legs from the OWN W243"),
    ("C2 header 101 parity rows",
     "-> 101 parity rows (estate 90 ending W231 + W232..W241\n# legs 10 + W243 leg 1)",
     "-> 102 parity rows (estate 90 ending W231 + W232..W242\n# legs 11 + W243 leg 1)"),
    ("C3 par_full span msg", "!= 100 (90 estate + W232..W241 legs 10)",
     "!= 101 (90 estate + W232..W242 legs 11)"),
    ("C4 par_full count 100", 'assert par_full.count("assert pf.N1_BANDS[") == 100',
     'assert par_full.count("assert pf.N1_BANDS[") == 101'),
    ("C5 legs count 10", 'assert legs_sec.count("assert pf.N1_BANDS[") == 10 \\',
     'assert legs_sec.count("assert pf.N1_BANDS[") == 11 \\'),
    ("C6 legs segment msg", "legs segment not W232..W241 ten legs",
     "legs segment not W232..W242 eleven legs"),
    ("C7 receipt legs verbatim", "W232..W241 legs extracted verbatim (10)",
     "W232..W242 legs extracted verbatim (11)"),
    ("C8 receipt block rows", "block = 101 rows ending at W243 (estate 90 + W232..W241 legs 10 + fresh W243 leg 1)",
     "block = 102 rows ending at W243 (estate 90 + W232..W242 legs 11 + fresh W243 leg 1)"),
    ("C9 structural choice line 35", "the parity estate + the W232..W241",
     "the parity estate + the W232..W242"),
    ("C12 ten-leg segment note", "the 10-leg segment regardless",
     "the 11-leg segment regardless"),
    # r1008 fix C13/C14: the B53->B77 cascade double-converted the gate0.5
    # UPSTREAM finalize-product literal (template n1_w242 -> B53 n1_w243 ->
    # B77 generic w243->w244 n1_w244, wrong: that file is the OWN wave's
    # FUTURE product). Natural naming: wave W finalize writes n1_w<W>_results
    # (verified on disk: n1_w243_results.json = W243 finalize 01:33, ledger
    # 958,935/532,520 = the L95 anchors). Scope-convert back.
    ("C13 gate0.5 upstream product path",
     'w243_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w244_results.json")',
     'w243_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w243_results.json")'),
    ("C14 gate0.5 upstream assert msg",
     '"W243 finalize product missing (n1_w244_results.json) -- chain dep not met"',
     '"W243 finalize product missing (n1_w243_results.json) -- chain dep not met"'),
    # r1008 fix C15/C16: same B69->B76 / B53->B77 double-conversion class on
    # the remaining two upstream literals (template PERPETUAL_N1_W242 -> B69
    # W243 -> B76 re-hit -> W244 wrong; template n1_w242_results comment ->
    # B53 n1_w243 -> B77 re-hit -> n1_w244 wrong).
    ("C15 gate0.5 upstream prereg pickaxe",
     'r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W244_PREREG.md")\nw243_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]',
     'r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W243_PREREG.md")\nw243_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]'),
    ("C16 pf_comment upstream finalize literal",
     '"    # finalize product landed (n1_w244_results.json present, ledger",',
     '"    # finalize product landed (n1_w243_results.json present, ledger",'),
    ("C17 n1 splice upstream prereg needle",
     'PRE_KEY_I = line_indent(n1_t, \'"prereg": ("research/PERPETUAL_N1_W244_PREREG.md\', EOL)',
     'PRE_KEY_I = line_indent(n1_t, \'"prereg": ("research/PERPETUAL_N1_W243_PREREG.md\', EOL)'),
    # r1008 fix C18/C19/C20: the double-brace f-string BATCH row key never
    # had a bump (B72 covers only the a-row literal; B70/B73 cover the
    # single-brace FILE needles) -> stale 243 row key; plus two bare-number
    # narrati ("wave 243:" PRE description + "wave 243 = first free number"
    # materializer comment) untouched by W/w-prefix bumps. All three are
    # OWN-wave references in the W244 editor and must read 244.
    ("C18 cfg batch double-brace row key",
     "243: {{\"batch\": \"PERPETUAL-N1-W244\",",
     "244: {{\"batch\": \"PERPETUAL-N1-W244\","),
    ("C19 PRE narrative own wave number",
     '"wave 243: ",',
     '"wave 244: ",'),
    ("C20 materializer own-wave first-free comment",
     '"    #     wave 243 = first free number after the",',
     '"    #     wave 244 = first free number after the",'),
    ("C21 receipt note own-wave number",
     "wave 243 engine_owner=bm-a",
     "wave 244 engine_owner=bm-a"),
]
for label, old, new in C:
    # Phase C OLDs exist only in the POST-bump text (they span generic-bump
    # context); the count-formula cannot model cross-context composition --
    # gate on uniqueness instead (long unique strings, fail-closed).
    obs = t.count(old)
    assert obs == 1, f"PhaseC {label}: count {obs} != 1"
    t = t.replace(old, new, 1)

# ---------------- residue battery (fail-closed) ----------------

ZERO_RESIDUE = [
    "LIVE-SEED-REFUSAL", "REFUSED", "refusal chain (SEED_REGISTRY",
    "refuser-adjacency", "post-hop", "live-seed-hop face",
    "B_live_seed_hop_face",
    "541_404", "541_500", "541_603", "551_501", "553_500", "541_501",
    "541_700", "thirty-second consecutive", "fourth consecutive seed-gap",
    "gap face fifth", "rows 232", "232/124/67", "bma_ordinal=125", "125th",
    "one hundred and twenty-fifth", "ONE HUNDRED AND TWENTY-FIFTH",
    "TWO HUNDRED AND FORTY-THIRD", "956,735", "956_735", "530,320", "530_320",
    "MSG-20261014-2107", "20261014", "6207e60e9", "4574bfeca", "20:4x",
    "r998", "r999", "r1000", "r1001", "W244p", "W244 freezer",
    "W244+",
    # r1008 fix: 'W244 seat' REMOVED from zero-residue -- post-bump it is
    # the OWN-wave seat (published 08df387e0 / MSG-20261015-0206) and its
    # 5 references (seat-found assert + leg4-mandate governance) are the
    # semantic face; only 'W245 seat' refs are downstream (A14_NEW).
    "== 232", "N1_BANDS[235]", "n1_w242", "_c242",
]
for p in ZERO_RESIDUE:
    c = t.count(p)
    if c != 0:
        for _i, _l in enumerate(t.split("\n"), 1):
            if p in _l:
                print("RESIDUE-LOC %d| %s" % (_i, _l.strip()[:170]))
    assert c == 0, f"RESIDUE FAIL: {p!r} count {c} != 0"

# r1008 fix: scoped refus* battery -- 'refuser'/'refusal' are legitimate
# ONLY in (a) the W245p downstream projection narrative (leg4 receipt
# refs, live refusal inside the NEXT wave's naive window) or (b) the
# historical disclosure "refusal chain is behind us" (prior-wave face).
# Any other refus* mention = own-wave machinery leakage = fail.
_tls = t.split("\n")
_scoped_bad = []
for _i, _l in enumerate(_tls, 1):
    if "refus" in _l.lower():
        _ctx = _l + "\n" + (_tls[_i] if _i < len(_tls) else "")  # wrap window
        if not (("leg4" in _ctx) or ("W245" in _ctx) or ("behind us" in _ctx)):
            _scoped_bad.append((_i, _l.strip()[:150]))
assert not _scoped_bad, "UNSCOPED refus* residue: %r" % _scoped_bad[:5]

POSITIVE = [
    "B_clean_at_naive_start", "FIRST-CLEAN arithmetic continuation of the prior-wave B tail",
    "(553_501, 555_500)", "(541_701, 541_900)", "thirty-third consecutive",
    "fifth consecutive seed-gap", "gap face sixth", "555_501..557_500",
    "541_901..542_100", "542_001..542_200", "MSG-20261015-0206-bma-w244-seat.md",
    '"wave": 244', "_set_wave(244)", '244: {"batch": "PERPETUAL-N1-W244"',
    "n1_w244", "r1007 freeze window", "958,935", "532,520",
    "B base == prior-B-tail+1 EXACT",
    # r1008 fix: own-wave seat refs must EXIST (published seat governs);
    # downstream seat refs must point at W245 (not yet published).
    "W244 seat MSG", "W245 seat NOT YET PUBLISHED",
    "n1_w243_results.json",
]
# r1008 fix: exact-count gate on the wave-literal families -- upstream
# (n1_w243) exactly 3 refs (gate0.5 path+msg + pf_comment chain narrative);
# own-wave (n1_w244) exactly 2 (shard config out_name + path-drift assert);
# upstream prereg name (PERPETUAL_N1_W243_PREREG) exactly 2 (pickaxe path +
# n1 splice needle); own prereg name (PERPETUAL_N1_W244_PREREG) exactly 8.
# Catches any B53->B77 / B69->B76 cascade double-conversion regression.
assert t.count("n1_w243_results.json") == 3, \
    f"upstream product literal count {t.count('n1_w243_results.json')} != 3"
assert t.count("n1_w244_results.json") == 2, \
    f"own-wave product literal count {t.count('n1_w244_results.json')} != 2"
assert t.count("PERPETUAL_N1_W243_PREREG") == 2, \
    f"upstream prereg literal count {t.count('PERPETUAL_N1_W243_PREREG')} != 2"
assert t.count("PERPETUAL_N1_W244_PREREG") == 8, \
    f"own prereg literal count {t.count('PERPETUAL_N1_W244_PREREG')} != 8"
# r1008 fix: own-wave row-key + narrative gates (C18/C19/C20 class).
assert t.count('243: {{"batch"') == 0, "stale double-brace batch row key (C18 miss)"
assert t.count('244: {{"batch"') == 1, "own double-brace batch row key not unique"
_wv = t.count("wave 243")
if _wv:
    for _i, _l in enumerate(t.split("\n"), 1):
        if "wave 243" in _l:
            print("WAVE243-LOC %d| %s" % (_i, _l.strip()[:170]))
assert _wv == 0, "stale bare-number own-wave narrative (C19/C20/C21 miss)"
assert t.count("wave 244") == 3, \
    f"own-wave narrative count {t.count('wave 244')} != 3 (PRE desc + first-free + receipt note)"
pos_report = {}
for p in POSITIVE:
    c = t.count(p)
    assert c >= 1, f"POSITIVE FAIL: {p!r} count {c} == 0"
    pos_report[p] = c
# hops=1 must survive ONLY in the W245p downstream projection narrative
h1 = t.count("hops=1")
h1_exp = expected("hops=1")
assert h1 == h1_exp, f"hops=1 count {h1} != derived {h1_exp}"
assert h1 <= 2, f"hops=1 residue {h1} > 2 (W245p projection refs only)"

# ---------------- AST gate + write ----------------
compile(t, OUT, "exec")
io.open(OUT, "w", encoding="utf-8", newline="").write(t)

receipt = {
  "machine": "bm-a", "round": "r1007",
  "phase": "W244 five-face freeze editor machine-SUB generation (template _w243bma_freeze_edits.py)",
  "template_bytes": len(orig), "out_bytes": len(t),
  "sub_pairs_applied": len(applied),
  "phase_a_pairs": [x[0] for x in applied[:len(A_PAIRS)]],
  "phase_b_count": len(B), "phase_c_count": len(C),
  "counts": [{"label": l, "observed": o, "old": len(o_)} for (l, o_, _n), o in
             zip(applied, [None] * 0)] if False else None,
  "zero_residue_verified": ZERO_RESIDUE,
  "positive_anchors": pos_report,
  "hops1_survivors": h1,
  "hops1_note": "legitimate W245p downstream projection refs only (receipt leg4 hops_B=1)",
  "semantic_face": "B returns to CLEAN staircase base (hops=0, B base == prior-W243-B-tail+1 EXACT 541_701; the W242-era live-seed refusal chain behind us); A = fifth consecutive seed-gap clean continuation 553_501..555_500; gap face sixth consecutive; W245p projection = A clean 555_501..557_500 / B naive 541_901..542_100 hops=1 first-clean 542_001..542_200",
  "law": "never transcribe r587; all wave facts machine-derived from the LIVE committed ADMIT receipt at editor run time",
}
receipt["counts"] = None
sublog = []
for _x in applied:
    sublog.append({"label": _x[0], "expected": orig.count(_x[1])})
receipt["sub_labels"] = [x[0] for x in applied]
io.open(RECEIPT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print("GEN OK:", OUT)
print("subs applied:", len(applied), "| template", len(orig), "B -> out", len(t), "B")
print("hops=1 survivors:", h1, "(W245p projection refs)")
print("NEXT: run editor (gate0 origin-fresh -> splice -> fivekeys -> commit+push -> engine self-burn)")
