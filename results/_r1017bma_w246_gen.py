# -*- coding: utf-8 -*-
# r1017 bm-a: W246 five-face freeze EDITOR GENERATOR (Phase-A inline extraction
# + Phase-B count-asserted ordered transform). Source = committed W245 editor
# (results/_w245bma_freeze_edits.py, proven live-fire: freeze 29d3ab761 +
# engine self-burn 12/12 + finalize one-pass r1015 fivekeys ALL PASS).
# OLD blocks extracted AT RUN TIME from the SRC physical bytes by anchor
# (r1012 window() law: zero transcription, count==1 verified). NEW blocks =
# final W246 language. W246 face: A 557_501..559_500 FIRST-CLEAN hops=0
# (eighth consecutive seed-gap A-continuation face per the FROZEN W246 probe
# receipt leg1 A_semantics -- ordinal +2 jump vs the W245 receipt's "sixth"
# disclosed honestly, frozen receipt governs) / B 542_201..542_400
# DOUBLE-CLEAN hops=0 (B base == prior-B-tail+1 EXACT, fc_b == fc_b_naive,
# no refusers, no own-A reservation jump, B_hop_lands_inside_A=false).
# W247+ projection (probe leg4): A naive 559_501..561_500 CLEAN hops=0 /
# B naive 542_401..542_600 hits registered W239 A band -> first-clean
# 544_501..544_700 hops=1 staircase band-hop face (first-disclosed).
# Own bundle: seat MSG-20261015-1328-bma-w246-seat @ origin 785936d84;
# prereg research/PERPETUAL_N1_W246_PREREG.md frozen @ 4a001a96d (bm-a r1016
# window machine derive); probe receipt results/_w246bma_20261015_probe_receipt.json
# ADMIT; upstream W245 finalize ledger 963,335 / K=536,920 (n1_w245_results.json).
import io, os, re, py_compile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w245bma_freeze_edits.py")
OUT = os.path.join(REPO, "results", "_w246bma_freeze_edits.py")

T0 = io.open(SRC, encoding="utf-8", newline="").read()

# ---------- Phase-A legs: wave-form chained rolls (checked vs T0) ----------
P1, P2, P3, P4, P5 = "\x01A\x01", "\x01B\x01", "\x01C\x01", "\x01D\x01", "\x01E\x01"
CHAIN = [
    ("W245", P1), ("W244", "W245"), ("W243", "W244"), (P1, "W246"),
    ("w245bma", "w246bma"),
    ("w244bma", "w245bma"),
    ('245: {"batch"', P2), ('244: {"batch"', '245: {"batch"'), (P2, '246: {"batch"'),
    ('245: {"a"', P3), ('244: {"a"', '245: {"a"'), (P3, '246: {"a"'),
    ('245: {{"batch"', '246: {{"batch"'),
    ('245: {{"a"', '246: {{"a"'),
    ("_set_wave(245)", "_set_wave(246)"),
    ("WAVE_CONFIGS[245]", "WAVE_CONFIGS[246]"),
    ("WAVE_CONFIGS[244]", "WAVE_CONFIGS[245]"),
    ("N1_BANDS.get(244)", "N1_BANDS.get(245)"),
    ("N1_BANDS[244]", "N1_BANDS[245]"),
    ("N1_BANDS[243]", "N1_BANDS[244]"),
    ("n1_w245", P5), ("n1_w244", "n1_w245"), (P5, "n1_w246"),
    ("n1w245", "n1w246"),
    ("PERPETUAL_N1_W244_PREREG", "PERPETUAL_N1_W245_PREREG"),
]
CHAIN_FLOORS = {
    "W245": 90, "W244": 110, "W243": 6,
    "w245bma": 11, "w244bma": 1,
    '245: {"batch"': 2, '244: {"batch"': 2, '245: {"a"': 1, '244: {"a"': 3,
    '245: {{"batch"': 1, '245: {{"a"': 2,
    "_set_wave(245)": 1, "WAVE_CONFIGS[245]": 2, "WAVE_CONFIGS[244]": 3,
    "N1_BANDS.get(244)": 1, "N1_BANDS[244]": 11, "N1_BANDS[243]": 3,
    "n1_w245": 3, "n1_w244": 3, "n1w245": 2,
    "PERPETUAL_N1_W244_PREREG": 1,
}
for o, f in CHAIN_FLOORS.items():
    if T0.count(o) < f:
        raise SystemExit("CHAIN FLOOR FAIL: %r count=%d floor=%d" % (o, T0.count(o), f))
T1 = T0
for o, n in CHAIN:
    T1 = T1.replace(o, n)

# ---------- Phase-B legs: everything else (OLD sides are POST-CHAIN text) ----------
VMAP = [
    # --- header/provenance stamps ---
    ("12:4x bm-a r1013 freeze window", "15:1x bm-a r1017 freeze window"),
    ("r1007 window; engine self-burn 12/12 + finalize one-pass verified r1008)",
     "r1013 window; engine self-burn 12/12 + finalize one-pass verified r1015)"),
    ("bm-a splice generation r1007 window", "bm-a splice generation r1013 window"),
    ("r1010, pre-seat probe", "r1015, pre-seat probe"),
    ("bm-a r1008 own-wave closeout 07:4x", "bm-a r1015 own-wave closeout 13:2x"),
    ("finalize landing 07:4x", "finalize landing 13:2x"),
    ("bm-a r1007 splice generation", "bm-a r1013 splice generation"),
    ("the bm-a r1007 window", "the bm-a r1013 window"),
    ("bm-a r1008 own-wave closeout", "bm-a r1015 own-wave closeout"),
    ("own-wave closeout r1008", "own-wave closeout r1015"),
    # --- seat / origin / takeover -> own-seat continuity ---
    ("2b0947947", "785936d84"),
    ("MSG-20261015-0844-bma-w245-seat", "MSG-20261015-1328-bma-w246-seat"),
    ("r1010, queue-depth supply depth-1 at publish", "r1015, queue-depth supply depth-1 at publish"),
    ("(r1010 MSG-", "(r1015 MSG-"),
    (" r1010 BEFORE this freeze", " r1015 BEFORE this freeze"),
    ("(r1010 derive landed pre-freeze expected)", "(r1016 derive landed pre-freeze expected)"),
    ("r1010 absorbed-window machine-SUB derive landed pre-freeze", "r1016 window machine-SUB derive landed pre-freeze"),
    ("r1010 absorbed-window derive landed pre-freeze commit", "r1016 window derive landed pre-freeze commit"),
    ("and landed by the r1011 commit 6473fb7f8, machine-SUB from frozen W246 tpl 260ffd3f8)",
     "and committed at origin 4a001a96d, machine-SUB from the frozen W245 prereg 6473fb7f8"),
    ("derived by the absorbed r1010 window", "derived by the bm-a r1016 window"),
    ("and committed by r1011", "and committed same-window"),
    ("machine-SUB from the frozen W246 tpl 260ffd3f8", "machine-SUB from the frozen W245 prereg 6473fb7f8"),
    ("takeover lane disclosed (GM re-assignment: bm-c declared the W246 turn at r1020 closeout then heartbeat froze 64.5min with zero origin commits post the W245-finalize unblock -- stall >1 round, takeover per the r1009 next-pointer rule)",
     "own-seat continuity (bm-a landed the W245 chain same-window r1015: freeze 29d3ab761 + engine self-burn 12/12 + finalize one-pass ledger 963,335 / K=536,920; no takeover lane this wave, no declared external turn, origin vacancy four-check green at publish)"),
    # --- ledger anchors (W245 finalize) ---
    ("961,135", "963,335"), ("534,720", "536,920"),
    ("961_135", "963_335"), ("534_720", "536_920"),
    # --- ordinals ---
    ("owner_rows=234", "owner_rows=235"), ("bma_rows=126", "bma_rows=127"),
    ("len(owner_rows_live) == 234", "len(owner_rows_live) == 235"),
    ("len(bma_rows_live) == 126", "len(bma_rows_live) == 127"),
    ("expect 234/126/67", "expect 235/127/67"),
    ("rows 126", "rows 127"), ("rows 234", "rows 235"),
    ("235th", "236th"), ("127th", "128th"),
    ("bma_ordinal=127", "bma_ordinal=128"),
    ('probe_receipt_bma_ordinal_face": 126', 'probe_receipt_bma_ordinal_face": 127'),
    ("one hundred and twenty-seventh", "one hundred and twenty-eighth"),
    ("ONE HUNDRED AND TWENTY-SIXTH", "ONE HUNDRED AND TWENTY-SEVENTH"),
    ("TWO HUNDRED AND FORTY-FIFTH", "TWO HUNDRED AND FORTY-SIXTH"),
    ("thirty-third consecutive", "thirty-fourth consecutive"),
    ("thirty-fourth consecutive window", "thirty-fifth consecutive window"),
    # --- face ordinals (frozen W246 receipt governs: A=eighth; gap=eighth) ---
    ("sixth consecutive seed-gap", "eighth consecutive seed-gap"),
    ("gap face seventh consecutive", "gap face eighth consecutive"),
    # --- own band literals (W246 A 557_501..559_500 / B 542_201..542_400) ---
    ("555_501", "557_501"), ("557_500", "559_500"),
    ("542_001", "542_201"), ("542_200", "542_400"),
    # --- upstream tail variable roll ---
    ("w244_a_tail", "w245_a_tail"), ("w244_b_tail", "w245_b_tail"),
    # --- E63 lineage comment (mechanical +1, one-behind face preserved) ---
    ("arith_a244/arith_b244", "arith_a245/arith_b245"),
    # --- projection key roll ---
    ("W246p_", "W247p_"),
    # --- extraction structure (estate fixed 90; legs W232..W244 13; +1 fresh W245 leg) ---
    ("the W246 block appends ONE fresh W245 leg -> 102 rows.",
     "the W246 block appends ONE fresh W245 leg -> 103 rows."),
    ('assert par_full.count("assert pf.N1_BANDS[") == 102', 'assert par_full.count("assert pf.N1_BANDS[") == 103'),
    ("!= 102 (90 estate", "!= 103 (90 estate"),
    ("W232..W244 legs 12", "W232..W244 legs 13"),
    ("extracted verbatim (12)", "extracted verbatim (13)"),
    ('assert legs_sec.count("assert pf.N1_BANDS[") == 12', 'assert legs_sec.count("assert pf.N1_BANDS[") == 13'),
    ("twelve legs", "thirteen legs"),
    ("list(range(232, 244))", "list(range(232, 245))"),
    ("= 103 rows ending", "= 104 rows ending"),
    ("-> 103 parity rows", "-> 104 parity rows"),
    # --- family-6 boundary quadruple (spaced forms + contiguous stale forms) ---
    ("range(209, 246)", "range(209, 247)"),
    ("range(16, 245)", "range(16, 246)"),
    ("range(17, 245)", "range(17, 246)"),
    ("if w < 245)", "if w < 246)"),
    ("if w < 244)", "if w < 245)"),
    ("w<245", "w<246"),
    ("w<244", "w<245"),
    ("below 245", "below 246"),
    ("range(16,244)", "range(16,245)"),
    ("range(17,244)", "range(17,245)"),
    ("below-244", "below-245"),
    # --- receipt wave field (one-behind lineage face: = upstream wave) ---
    ('"wave": 244', '"wave": 245'),
    # --- prereg face note (prereg derive round) ---
    ("(r1010 derive landed pre-freeze expected)", "(r1016 derive landed pre-freeze expected)"),
]
VMAP_FLOORS = {
    "12:4x bm-a r1013 freeze window": 1,
    "bm-a splice generation r1007 window": 1,
    "r1010, pre-seat probe": 1,
    "bm-a r1008 own-wave closeout 07:4x": 1,
    "finalize landing 07:4x": 2,
    "bm-a r1007 splice generation": 2,
    "the bm-a r1007 window": 1,
    "own-wave closeout r1008": 1,
    "2b0947947": 2,
    "MSG-20261015-0844-bma-w245-seat": 7,
    "r1010, queue-depth supply depth-1 at publish": 1,
    "(r1010 MSG-": 1,
    " r1010 BEFORE this freeze": 1,
    "(r1010 derive landed pre-freeze expected)": 1,
    "r1010 absorbed-window machine-SUB derive landed pre-freeze": 2,
    "r1010 absorbed-window derive landed pre-freeze commit": 1,
    "and landed by the r1011 commit 6473fb7f8, machine-SUB from frozen W246 tpl 260ffd3f8)": 1,
    "derived by the absorbed r1010 window": 2,
    "and committed by r1011": 1,
    "machine-SUB from the frozen W246 tpl 260ffd3f8": 1,
    "takeover lane disclosed (GM re-assignment: bm-c declared the W246 turn at r1020 closeout then heartbeat froze 64.5min with zero origin commits post the W245-finalize unblock -- stall >1 round, takeover per the r1009 next-pointer rule)": 8,
    "961,135": 6, "534,720": 6, "961_135": 1, "534_720": 1,
    "owner_rows=234": 1, "bma_rows=126": 1,
    "len(owner_rows_live) == 234": 1, "len(bma_rows_live) == 126": 1,
    "expect 234/126/67": 1,
    "rows 126": 3, "rows 234": 2, "235th": 2, "127th": 6, "bma_ordinal=127": 7,
    'probe_receipt_bma_ordinal_face": 126': 1,
    "one hundred and twenty-seventh": 2,
    "ONE HUNDRED AND TWENTY-SIXTH": 1,
    "TWO HUNDRED AND FORTY-FIFTH": 3,
    "thirty-third consecutive": 1, "thirty-fourth consecutive window": 1,
    "sixth consecutive seed-gap": 8,
    "gap face seventh consecutive": 5,
    "555_501": 1, "557_500": 1, "542_001": 3, "542_200": 3,
    "w244_a_tail": 18, "w244_b_tail": 18,
    "arith_a244/arith_b244": 3,
    "W246p_": 6,
    "the W246 block appends ONE fresh W245 leg -> 102 rows.": 1,
    'assert par_full.count("assert pf.N1_BANDS[") == 102': 1,
    "!= 102 (90 estate": 1,
    "W232..W244 legs 12": 2,
    "extracted verbatim (12)": 1,
    'assert legs_sec.count("assert pf.N1_BANDS[") == 12': 1,
    "twelve legs": 1,
    "list(range(232, 244))": 1,
    "= 103 rows ending": 1,
    "range(209, 246)": 2, "range(16, 245)": 2, "range(17, 245)": 3,
    "if w < 245)": 5, "if w < 244)": 1,
    "w<245": 4, "w<244": 3, "below 245": 2,
    "range(16,244)": 2, "range(17,244)": 2, "below-244": 2,
    '"wave": 244': 1,
    "(r1010 derive landed pre-freeze expected)": 1,
}
def xf(t):
    for o, n in VMAP:
        t = t.replace(o, n)
    return t
for o, f in VMAP_FLOORS.items():
    if T1.count(o) < f:
        raise SystemExit("VMAP FLOOR FAIL (post-chain): %r count=%d floor=%d" % (o, T1.count(o), f))
T2 = xf(T1)

# ---------- Phase-A inline: OLD block extraction from SRC (physical bytes) ----------
def span(start_needle, end_needle, name):
    i = T2.find(start_needle)
    assert i >= 0, name + " START NOT FOUND: " + start_needle[:60]
    ls = T2.rfind("\n", 0, i) + 1
    j = T2.find(end_needle, i)
    assert j >= i, name + " END NOT FOUND: " + end_needle[:60]
    le = T2.find("\n", j)
    if le < 0: le = len(T2)
    block = T2[ls:le]
    assert T2.count(block) == 1, "%s count=%d (expect 1)" % (name, T2.count(block))
    return block

def window(anchor, n, name):
    i = T2.find(anchor)
    assert i >= 0, name + " ANCHOR NOT FOUND: " + anchor[:60]
    ls = T2.rfind("\n", 0, i) + 1
    seg = T2[ls:].split("\n")[:n]
    block = "\n".join(seg)
    assert T2.count(block) == 1, "%s count=%d (expect 1)" % (name, T2.count(block))
    return block

OLD = {}
OLD["a1"] = span("# NEW FACE vs the W245 editor (honest disclosure): the W246 B band takes the",
                 "# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.", "a1")
OLD["a2"] = span("# W246 FACE (probe receipt leg1 relation_asserts):",
                 "B naive continuation drift vs probe receipt leg1 ARITH_B", "a2")
OLD["a5"] = window('"    # B = FIRST-CLEAN post-hop forward walk (the naive continuation",', 6, "a5")
OLD["a6"] = window('"    # W246+ projection (gate-derived pre-seat probe leg4, pre-W246",', 8, "a6")
OLD["a7"] = window(' "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN post-hop ",', 9, "a7")
OLD["a8"] = window('"ADMIT convention); W246+ projection per this window gate: ",', 5, "a8")
OLD["a9"] = span('"        # band facts (law sec.4 W246 row): A = FIRST-CLEAN arithmetic",',
                 'assert _entry_shard_of(0, 12) == (\\"PERPETUAL-N1-W246-SHARD-0\\",', "a9")
OLD["a12"] = window('          "+ B=FIRST-CLEAN post-hop forward walk (live-seed-hop face, "', 2, "a12")
OLD["a13"] = window('                     "B": "FIRST-CLEAN post-hop forward walk (the naive continuation is REFUSED', 1, "a13")
OLD["a14"] = window('  "downstream_seat": "W246 seat NOT YET PUBLISHED', 1, "a14")
OLD["a17"] = window(" f'{MEM_I}\"b_exit_seed_base\": {b_lo},   # law sec.4 W246 B:", 1, "a17")

# ---------- NEW blocks (final W246 language) ----------
NEW = {}
NEW["a1"] = """# NEW FACE vs the W245 editor (honest disclosure): the W246 B band returns
# to the CLEAN staircase base (the naive continuation 542_201..542_400 from
# the W245-REGISTERED B tail 542_200+1 is CLEAN at naive start, hops=0,
# B_hop_chain empty, B_naive_hops=0 -- double-clean arithmetic continuation
# face, anticipated by the W245 probe leg4 + the W245 prereg sec.8
# downstream_seat projection and confirmed live; fc_b == fc_b_naive: no
# refusers, no own-A reservation jump; B_hop_lands_inside_A=false; the
# first-clean B window is NOT inside the W246 own-wave A window
# 557_501..559_500) -- relation asserts mirror the probe receipt leg1
# relation_asserts exactly (B_double_clean_expected_face +
# B_base_above_priorB_tail + B_no_ownA_jump + B_hop_lands_inside_A=false),
# and the staircase adjacency is machine-asserted (B base == prior-wave B
# tail+1 EXACT). A-face ordinal disclosed honestly: the W245 receipt said
# "sixth consecutive seed-gap"; the FROZEN W246 artifacts (probe receipt
# leg1 A_semantics + prereg sec.3 + seat MSG) all say EIGHTH consecutive
# seed-gap A-continuation face -- the frozen receipt governs, ordinal jump
# disclosed, never transcribed r587.
# Zero hardcoded upstream band values: ALL W245 facts machine-derived from the
# LIVE pf import at freeze time (the registered W245 row -- bm-a own seat
# honored), cross-checked against the committed ADMIT receipt
# (results/_w246bma_20261015_probe_receipt.json) which was derived on the
# post-W245-REGISTERED universe. If the LIVE W245 bands differ from the
# declared face, the continuation asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W245 editor): the parity estate + the W232..W244
# fresh legs are BOTH extracted from the OWN W245 block physical bytes
# (bm-a r1013 splice generation, committed -- structure known exactly); the
# W246 block appends ONE fresh W245 leg (machine-derived from the live
# registered row) -> 104 parity rows (estate 90 ending W231 + W232..W244
# legs 13 + W245 leg 1). Extraction self-asserts the 90-row estate cut and
# the 13-leg segment regardless.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x."""

NEW["a2"] = """# W246 FACE (probe receipt leg1 relation_asserts):
# A keeps the A-continuation base (prior-wave A tail+1 EXACT -- the naive
# arithmetic continuation is CLEAN at its own start, hops=0, A_hop_chain
# empty, A_clean_at_naive_start=true -- eighth consecutive seed-gap face per
# the W245 seat leg4 anticipation confirmed live, frozen receipt A_semantics
# verbatim); B returns to the CLEAN staircase base (prior-wave B tail+1
# EXACT, hops=0, B_hop_chain empty, B_naive_hops=0 -- double-clean
# arithmetic continuation face, anticipated by the W245 probe leg4 + the
# W245 prereg sec.8 downstream_seat projection and confirmed live;
# fc_b == fc_b_naive: no refusers, no own-A reservation jump;
# B_hop_lands_inside_A=false; gap face eighth consecutive); A sits far above
# the B staircase (seed-decoupled A/B gap); machine-derived from the LIVE
# registered row, never transcribed.
assert w245_a_tail + 1 == a_lo, "A continuation base relation broken (A == prior-wave A tail+1 EXACT)"
assert w245_b_tail + 1 == b_lo, "B staircase base relation broken (B == prior-wave B tail+1 EXACT -- double-clean face)"
assert a_lo > w245_b_tail + 1, "seed-decoupled A-continuation face violated: A base must sit ABOVE prior-B tail+1 (seed-gap)"
assert b_hi < a_lo, "seed-decoupled A/B gap face violated: B window must sit entirely below own-A"
assert W245["b_exit"][1] < W245["a"][0], \\
    "upstream W245 row in-wave decoupled relation broken (registered W245 B window must sit below own W245 A window)"
assert leg1.get("hops_A") == 0 and leg1.get("hops_B") == 0, "hop-count drift vs probe receipt leg1 (both bands naive hops=0, double-clean face)"
assert leg1.get("A_hop_chain") == [] and (
    leg1.get("A_clean_at_naive_start") is True
    or (leg1.get("relation_asserts") or {}).get("A_clean_at_naive_start") is True
), \\
    "A hop-chain face drift (fc_a == fc_a_naive, hops=0, A_clean_at_naive_start=true -- naive continuation CLEAN at own start)"
assert leg1.get("B_hop_chain") == [] and leg1.get("B_naive_hops") == 0, "B hop-chain face drift (fc_b == fc_b_naive, hops=0, double-clean arithmetic continuation face)"
assert leg1.get("B_hop_lands_inside_A") is False, "B lands-inside-own-A drift vs probe receipt leg1 (B_hop_lands_inside_A must be False)"
assert leg1.get("B_naive_first_clean") == [b_lo, b_hi], "B naive first-clean drift vs probe receipt leg1"
ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_double_clean_expected_face") and ra.get("B_base_above_priorB_tail") \\
    and ra.get("AB_mutual_exclusion") and ra.get("B_no_ownA_jump") \\
    and ra.get("B_hop_lands_inside_A") is False, \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"
assert [w245_a_tail + 1, w245_a_tail + 2_000] == leg1["ARITH_A"], \\
    f"A-continuation start drift vs probe receipt leg1 ARITH_A: {[w245_a_tail + 1, w245_a_tail + 2_000]} != {leg1['ARITH_A']}"
assert [w245_b_tail + 1, w245_b_tail + 200] == leg1["ARITH_B"], \\
    f"B naive continuation drift vs probe receipt leg1 ARITH_B: {[w245_b_tail + 1, w245_b_tail + 200]} != {leg1['ARITH_B']}" """

NEW["a5"] = '''"    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail",
"    # (" + fmt(w245_b_tail + 1) + ".." + fmt(w245_b_tail + 200) + " CLEAN at naive start on the",
"    # registered universe, hops=0, B_hop_chain empty, B_naive_hops=0 --",
"    # double-clean arithmetic continuation face (fc_b == fc_b_naive: no refusers,",
"    # no own-A reservation jump) -- B lands OUTSIDE the own-A window",
"    # " + fmt(a_lo) + ".." + fmt(a_hi) + ": seed-decoupled A/B gap face eighth; B base == prior-B-tail+1 EXACT;",'''

NEW["a6"] = '''"    # W247+ projection (gate-derived pre-seat probe leg4, pre-W246",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W247p_A_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " (this window's gate: CLEAN, zero live",
"    # seed refusers) / B naive " + rec["legs"]["leg4"]["W247p_B_naive"] + " hits the registered W239 A band ->",
"    # honest forward first-clean " + rec["legs"]["leg4"]["W247p_B_first_clean"] + " hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " (staircase band-hop face,",
"    # first-disclosed; B_hop lands-inside-A=false leg present); W247 freezer MUST",
"    # re-derive on the post-W246 universe AND reserve the own-wave A window",
"    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1",
"    # equality); never transcribe r587.",'''

NEW["a7"] = ''' "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN arithmetic ",
 "continuation of the prior-wave B tail (the continuation ",
 f"{fmt(w245_b_tail + 1)}..{fmt(w245_b_tail + 200)} CLEAN at naive start on the registered ",
 "universe, hops=0, B_hop_chain empty, B_naive_hops=0 -- double-clean ",
 "arithmetic continuation face (fc_b == fc_b_naive: no refusers, no own-A ",
 "reservation jump); B lands OUTSIDE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap ",
 "face eighth consecutive; B base == prior-wave B tail+1 EXACT ",
 "machine-checkable; cross-window convergence with the W245 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W245 universe ",'''

NEW["a8"] = '''"ADMIT convention); W247+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W247p_A_naive']} CLEAN (hops=0, zero live seed refusers) / B naive ",
 f"{rec['legs']['leg4']['W247p_B_naive']} hits the registered W239 A band -- honest forward first-clean {rec['legs']['leg4']['W247p_B_first_clean']} hops=1 (staircase band-hop face first-disclosed on the pre-W246 universe; B_hop lands-inside-A=false leg present -- seed-gap face ",
 "inherited); W247 freezer MUST re-derive on the post-W246 universe AND ",
 "reserve the own-wave A window when deriving B (do NOT assume the ",'''

NEW["a9"] = '''"        # band facts (law sec.4 W246 row): A = FIRST-CLEAN arithmetic",
"        # continuation of the prior-wave A tail",
f"        # ({fmt(w245_a_tail + 1)}..{fmt(w245_a_tail + 2_000)} CLEAN at naive start on the",
"        # registered universe, hops=0, A_hop_chain empty +",
"        # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,",
"        # eighth consecutive seed-gap face, exactly as the W245 seat leg4",
"        # succession projection notes anticipated; A base == prior-wave A",
f"        # tail+1 ({fmt(w245_a_tail)}+1) machine-checkable;",
"        # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail",
f"        # ({fmt(w245_b_tail + 1)}..{fmt(w245_b_tail + 200)} CLEAN at naive start on the",
"        # registered universe, hops=0, B_hop_chain empty, B_naive_hops=0 --",
"        # double-clean arithmetic continuation face (fc_b == fc_b_naive: no",
"        # refusers, no own-A reservation jump), anticipated by the W245",
"        # probe leg4 + the W245 prereg sec.8 downstream_seat projection;",
"        # B lands OUTSIDE the own-A window",
f"        # {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap face eighth consecutive;",
"        # B base == prior-wave B tail+1 EXACT",
"        # machine-checkable; B_hop_lands_inside_A=false;",
"        # cross-window convergence with",
"        # the W245 seat leg4 succession projection notes -- all",
"        # MANDATORY notes honored (post-W245 universe",
"        # re-derive + live-trace re-read, no staircase-equality assumption);",
f\'        assert WAVE_CONFIGS[246]["a_seed_base"] == {a_lo} == {w245_a_tail} + 1, (\',
\'            "W246 A must be the first-clean arithmetic continuation of the "\',
\'            "prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true -- "\',
\'            "seed-decoupled A-continuation face, eighth consecutive seed-gap face, "\',
\'            "exactly as the W245 seat leg4 succession projection notes "\',
\'            "anticipated; A base == prior-wave A tail+1 machine-checkable)"\',
f"        arith_a246 = set(range({a_lo}, {a_hi + 1}))",
"        assert not (arith_a246 & reg_ints), \\\\",
\'            "W246 A window must be CLEAN (first-clean ADMIT face, A-continuation)"\',
f\'        assert WAVE_CONFIGS[246]["b_exit_seed_base"] == {b_lo} == {w245_b_tail} + 1, (\',
\'            "W246 B double-clean arithmetic continuation face: the naive staircase continuation "\',
f\'            "{fmt(w245_b_tail + 1)}..{fmt(w245_b_tail + 200)} is CLEAN at naive start on the "\',
\'            "registered universe (hops=0, B_hop_chain empty, B_naive_hops=0) -- B base == prior-B-tail+1 "\',
\'            "EXACT (B_double_clean_expected_face + B_base_above_priorB_tail face relation "\',
\'            "asserts, probe receipt leg1 mirrored exactly; B_no_ownA_jump=true; B_hop_lands_inside_A=false)"\',
f"        assert {b_lo} > {w245_b_tail}, \\\\",
\'            "W246 B staircase base must sit above the prior-wave B tail (double-clean arithmetic continuation face)"\',
f"        arith_b246 = set(range({b_lo}, {b_hi + 1}))",
"        assert not (arith_b246 & reg_ints), \\\\",
\'            "W246 B window must be CLEAN (first-clean ADMIT face, double-clean arithmetic continuation)"\',
"        assert not (arith_b246 & arith_a246), \\\\",
\'            "W246 A/B same-freeze mutual exclusion (seed-decoupled gap face inherited: B below own A)"\',
"        assert _entry_shard_of(0, 12) == (\\"PERPETUAL-N1-W246-SHARD-0\\",",'''

NEW["a12"] = '''\'          "+ B=FIRST-CLEAN arithmetic continuation of the prior-wave B tail (double-clean face, "\',
\'          "hops=0, B_hop_chain empty, B_naive_hops=0, B base == prior-wave B tail+1 EXACT, B_no_ownA_jump=true, "\','''

NEW["a13"] = '''                     "B": "FIRST-CLEAN arithmetic continuation of the prior-wave B tail (CLEAN at naive start on the registered universe; hops=0, B_hop_chain empty, B_naive_hops=0 -- double-clean arithmetic continuation face: B base == prior-B-tail+1 EXACT, fc_b == fc_b_naive, no refusers, no own-A reservation jump; B_no_ownA_jump=true; B_hop_lands_inside_A=false; seed-decoupled A/B gap face eighth consecutive)"},'''

NEW["a14"] = '''  "downstream_seat": "W247 seat NOT YET PUBLISHED at this freeze window (next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W247 freezer MUST re-derive live on the post-W246 universe + reserve the own-wave A window when deriving B per the W246 seat leg4 mandate, never transcribe r587 -- W247p face: A naive 559_501..561_500 CLEAN (hops=0, zero live refusers on the pre-W246 universe) / B naive 542_401..542_600 hits the registered W239 A band -> honest forward first-clean 544_501..544_700 hops=1 staircase band-hop face first-disclosed, B_hop lands-inside-A=false leg present; seed-gap face inherited: W246 A/B decoupled, do NOT assume the staircase A-base==prior-B-tail+1 equality)",'''

NEW["a17"] = ''' f\'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W246 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN double-clean arithmetic continuation: naive staircase {fmt(w245_b_tail + 1)}..{fmt(w245_b_tail + 200)} CLEAN at naive start hops=0, B_hop_chain empty, B_naive_hops=0; B base == prior-B-tail+1 EXACT; fc_b == fc_b_naive, no refusers, no own-A reservation jump; B lands outside own-A; seed-decoupled A/B gap face eighth consecutive)\','''

BLOCKS = ["a1", "a2", "a5", "a6", "a7", "a8", "a9", "a12", "a13", "a14", "a17"]
for name in BLOCKS:
    ob = OLD[name]
    assert T2.count(ob) == 1, "BLOCK %s count=%d (expect 1)" % (name, T2.count(ob))
    T2 = T2.replace(ob, NEW[name].rstrip("\n"), 1)
    assert NEW[name].rstrip("\n") in T2, "BLOCK %s NEW not inserted" % name

# ---------- count-gate leg-count bumps + new [243]==3 insert ----------
for n, c_old, c_new in [(242, 3, 4), (241, 4, 5), (240, 5, 6), (239, 6, 7),
                        (238, 7, 8), (237, 8, 9), (236, 9, 10)]:
    o = 'N1_BANDS[%d]["a"][1])}),\') == %d' % (n, c_old)
    v = 'N1_BANDS[%d]["a"][1])}),\') == %d' % (n, c_new)
    assert T2.count(o) == 1, "count-gate [%d]==%d count=%d" % (n, c_old, T2.count(o))
    T2 = T2.replace(o, v, 1)
_line244 = ("assert n1_t4.count(f'assert pf.N1_BANDS[244] == {{\"a\": ({fmt(pf_mod.N1_BANDS[244][\"a\"][0])}"
            ", {fmt(pf_mod.N1_BANDS[244][\"a\"][1])}),') == 2")
assert T2.count(_line244) == 1, "count-gate [244]==2 line not found (post-vmap)"
_ins = _line244 + ("\nassert n1_t4.count(f'assert pf.N1_BANDS[243] == {{\"a\": ({fmt(pf_mod.N1_BANDS[243][\"a\"][0])}"
                   ", {fmt(pf_mod.N1_BANDS[243][\"a\"][1])}),') == 3")
T2 = T2.replace(_line244, _ins, 1)

# ---------- post gates: must-have / must-not-have / precise counts ----------
MUST = ["WAVE_CONFIGS[246]", "PERPETUAL-N1-W246-SHARD-0", "n1w246-0of12",
        '246: {"batch"', "range(16, 246)", "range(17, 246)", "range(209, 247)",
        "range(232, 245)", "W246 materializer face", "arith_b246", "arith_a246",
        "MSG-20261015-1328-bma-w246-seat", "785936d84", "963,335", "536,920",
        "TWO HUNDRED AND FORTY-SIXTH", "one hundred and twenty-eighth",
        "W247p_A_naive", "n1_w246_results.json", "B_double_clean_expected_face",
        "double-clean arithmetic continuation", "542_201", "557_501",
        "544_501", "staircase band-hop", "128th", "236th", "bma_ordinal=128",
        "eighth consecutive seed-gap", "4a001a96d", "6473fb7f8",
        "own-seat continuity"]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s
MUST_NOT = ["WAVE_CONFIGS[244]", "N1_BANDS.get(244)",
            "PERPETUAL-N1-W245", "r1007", "r1008",
            "r1010", "r1011", "r1020", "961,135", "532,520", "961_135", "534_720",
            "555_501", "542_001", "542_000", "541_901", "542_100",
            "perpetual_n2_w15_scrnull", "bma_ordinal=127", "127th", "235th",
            "TWO HUNDRED AND FORTY-FIFTH", "one hundred and twenty-seventh",
            "W246p_", "range(16, 245)", "range(17, 245)", "range(209, 246)",
            "MSG-20261015-0844", "2b0947947", "260ffd3f8", "rows 126", "rows 234",
            "owner_rows=234", "234/126", 'probe_receipt_bma_ordinal_face": 126',
            "sixth-blanket-removed-see-precise-gate", "gap face seventh consecutive",
            "live-seed-hop", "B_honest_forward_hop_expected_face",
            "arith_a244", "arith_b244", "W232..W243", "twelve legs",
            "ONE HUNDRED AND TWENTY-SIXTH", "takeover lane disclosed",
            "12:4x", "07:4x", "thirty-third consecutive", "thirty-fourth consecutive window",
            "n1_w244", "n1w245", "hops_B\") == 1", "B_naive_hops\") == 1",
            "== 102", "!= 102", "532_520", "958,935"]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))
# the a1 NEW block QUOTES the W245 receipt's "sixth consecutive seed-gap" claim
# exactly once (honest ordinal-jump disclosure: sixth -> EIGHTH per the frozen
# W246 receipt) -- the single legitimate instance; a second = real drift
assert T2.count("sixth consecutive seed-gap") == 1, \
    "seed-gap sixth-quote must be exactly 1 (a1 honest disclosure), got %d" \
    % T2.count("sixth consecutive seed-gap")
# E63 lineage: the rolled slash form arith_a245/arith_b245 (the W245 editor's
# variable face, referenced by the W246 editor's lineage comments) is the ONLY
# legitimate a245/b245 presence; standalone = un-replaced own-code drift
assert T2.count("arith_a245/arith_b245") == 3, \
    "arith lineage slash-form must be exactly 3, got %d" % T2.count("arith_a245/arith_b245")
assert T2.count("arith_a245") == 3 and T2.count("arith_b245") == 3, \
    "standalone arith_a245/arith_b245 leak (outside slash lineage form)"
# upstream W245 finalize product refs (chain dep check) are the only
# legitimate n1_w245 face; a fourth = un-rolled own-results reference
assert T2.count("n1_w245_results.json") == 3, \
    "upstream n1_w245_results.json refs must be exactly 3, got %d" \
    % T2.count("n1_w245_results.json")
# upstream W245 prereg references are LEGITIMATE in the W246 editor (frozen
# cross-generation naming): exactly 2 = upstream tpl pickaxe + law PRE_KEY_I
# anchor; a third instance = un-rolled OWN-prereg reference (fail-closed)
assert T2.count("PERPETUAL_N1_W245_PREREG") == 2, \
    "upstream W245 prereg refs must be exactly 2 (pickaxe + PRE_KEY_I), got %d" \
    % T2.count("PERPETUAL_N1_W245_PREREG")
assert T2.count('"--", "research/PERPETUAL_N1_W245_PREREG.md"') == 1, \
    "upstream pickaxe line form drift"
assert T2.count('("research/PERPETUAL_N1_W245_PREREG.md') == 1, \
    "PRE_KEY_I anchor form drift"
# the lineage template file ref _w245bma_freeze_edits.py is the single
# legitimate w245bma instance (own-file refs all rolled to w246bma)
assert T2.count("w245bma") == 1 and "_w245bma_freeze_edits.py template" in T2, \
    "w245bma must be exactly 1 (lineage template ref), got %d" % T2.count("w245bma")
# precise legitimate prior-boundary faces (family-6 zero-assert + receipt note)
assert T2.count("if w < 245)") == 1, \
    "if w < 245) count=%d (expect 1: the family-6 zero-assert target only)" % T2.count("if w < 245)")
assert T2.count("w<245") == 3, \
    "w<245 count=%d (expect 3: family-6 stale-gate message + receipt" \
    " prior-boundary note + E63 lineage prior-wave-boundary comment)" % T2.count("w<245")
assert T2.count("if w < 246)") == 5, \
    "if w < 246) count=%d (expect 5: 3 block LHS + family-6 assert x2)" % T2.count("if w < 246)")
# no malformed windows in NEW prose (r773 law)
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
py_compile.compile(OUT, doraise=True)
print("W246 EDITOR GEN OK -> %s (%d lines, %d bytes)" % (OUT, T2.count("\n") + 1, len(T2)))
print("blocks replaced: %s" % ",".join(BLOCKS))
