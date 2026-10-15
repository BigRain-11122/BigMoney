# -*- coding: utf-8 -*-
# r1020 bm-a: W247 five-face freeze EDITOR GENERATOR (Phase-A inline extraction
# + Phase-B count-asserted ordered transform). Source = committed W246 editor
# (results/_w246bma_freeze_edits.py, proven live-fire: freeze 650953086 +
# engine self-burn 12/12 + finalize one-pass r1018 fivekeys ALL PASS).
# OLD blocks extracted AT RUN TIME from the SRC physical bytes by anchor
# (r1012 window() law: zero transcription, count==1 verified). NEW blocks =
# final W247 language. W247 face (frozen probe receipt leg1 governs):
# A 559_501..561_500 hops=0 NINTH consecutive seed-gap A-continuation
# (W246 seat leg4 anticipation confirmed live) / B 544_501..544_700
# hops=1 REGISTERED-REFUSAL staircase band-hop face FIRST-MATERIALIZED
# (naive continuation 542_401..542_600 from the W246-REGISTERED B tail
# 542_400+1 REFUSED by the registered W239 A band 542_501..544_500 -> honest
# forward first-clean 544_501..544_700, B base == refuser-band-end+1 EXACT,
# B_no_ownA_jump=true, B_hop_lands_inside_A=false).
# W248+ projection (probe leg4): A naive 561_501..563_500 CLEAN hops=0 /
# B naive 544_701..544_900 CLEAN hops=0 (W248 seat ALREADY PUBLISHED by bm-c
# r1030 waits-upstream ARMED -- downstream note reflects it).
# Own bundle: seat MSG-20261015-1608-bma-w247-seat @ origin e06f4ee2a;
# prereg research/PERPETUAL_N1_W247_PREREG.md frozen @ 4c403cb16 (bm-a r1019
# window machine derive, SUB from frozen W246 tpl fbfb7b43f);
# probe receipt results/_w247bma_20261015_probe_receipt.json ADMIT;
# upstream W246 finalize ledger 965,535 / K=539,120 (n1_w246_results.json).
import io, os, re, py_compile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w246bma_freeze_edits.py")
OUT = os.path.join(REPO, "results", "_w247bma_freeze_edits.py")

T0 = io.open(SRC, encoding="utf-8", newline="").read()

# ---------- Phase-A legs: wave-form chained rolls (checked vs T0) ----------
P1, P2, P3, P4, P5 = "\x01A\x01", "\x01B\x01", "\x01C\x01", "\x01D\x01", "\x01E\x01"
CHAIN = [
    ("W246", P1), ("W245", "W246"), ("W244", "W245"), (P1, "W247"),
    ("w246bma", "w247bma"),
    ("w245bma", "w246bma"),
    ('246: {"batch"', P2), ('245: {"batch"', '246: {"batch"'), (P2, '247: {"batch"'),
    ('246: {"a"', P3), ('245: {"a"', '246: {"a"'), (P3, '247: {"a"'),
    ('246: {{"batch"', '247: {{"batch"'),
    ('246: {{"a"', '247: {{"a"'),
    ("_set_wave(246)", "_set_wave(247)"),
    ("WAVE_CONFIGS[246]", "WAVE_CONFIGS[247]"),
    ("WAVE_CONFIGS[245]", "WAVE_CONFIGS[246]"),
    ("N1_BANDS.get(245)", "N1_BANDS.get(246)"),
    ("N1_BANDS[245]", "N1_BANDS[246]"),
    ("N1_BANDS[244]", "N1_BANDS[245]"),
    ("N1_BANDS[243]", "N1_BANDS[244]"),
    ("n1_w246", P5), ("n1_w245", "n1_w246"), (P5, "n1_w247"),
    ("n1w246", "n1w247"),
    ("PERPETUAL_N1_W245_PREREG", "PERPETUAL_N1_W246_PREREG"),
]
CHAIN_FLOORS = {
    "W246": 86, "W245": 125, "W244": 7,
    "w246bma": 11, "w245bma": 1,
    '246: {"batch"': 2, '245: {"batch"': 2, '246: {"a"': 1, '245: {"a"': 3,
    '246: {{"batch"': 1, '246: {{"a"': 2,
    "_set_wave(246)": 1, "WAVE_CONFIGS[246]": 2, "WAVE_CONFIGS[245]": 3,
    "N1_BANDS.get(245)": 1, "N1_BANDS[245]": 11, "N1_BANDS[244]": 3, "N1_BANDS[243]": 3,
    "n1_w246": 4, "n1_w245": 3, "n1w246": 2,
    "PERPETUAL_N1_W245_PREREG": 2,
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
    ("15:1x bm-a r1017 freeze window", "18:3x bm-a r1021 freeze window"),
    ("r1013 window; engine self-burn 12/12 + finalize one-pass verified r1015)",
     "r1017 window; engine self-burn 12/12 + finalize one-pass verified r1018)"),
    ("bm-a splice generation r1013 window", "bm-a splice generation r1017 window"),
    ("bm-a r1013 splice generation", "bm-a r1017 splice generation"),
    ("bm-a own seat executed at the bm-a r1013 window; engine self-burn 12/12; finalize one-pass bm-a r1015 own-wave closeout, ledger 963,335 / K=536,920 machine-read",
     "bm-a own seat executed at the bm-a r1017 window; engine self-burn 12/12; finalize one-pass bm-a r1018 own-wave closeout, ledger 965,535 / K=539,120 machine-read"),
    ("the bm-a r1013 window; engine", "the bm-a r1017 window; engine"),
    ("finalize one-pass bm-a r1015 own-wave closeout ledger 963,335 / K=536,920",
     "finalize one-pass bm-a r1018 own-wave closeout ledger 965,535 / K=539,120"),
    ("r1015, pre-seat probe", "r1018, pre-seat probe"),
    ("bm-a r1015 own-wave closeout 13:2x", "bm-a r1018 own-wave closeout 16:0x"),
    ("finalize landing 13:2x", "finalize landing 16:0x"),
    ("own-wave closeout r1015", "own-wave closeout r1018"),
    # --- seat / origin / own-seat continuity ---
    ("own-seat continuity (bm-a landed the W246 chain same-window r1015: freeze 29d3ab761 + engine self-burn 12/12 + finalize one-pass ledger 963,335 / K=536,920; no takeover lane this wave, no declared external turn, origin vacancy four-check green at publish)",
     "own-seat continuity (bm-a landed the W246 chain same-window r1018 finalize: freeze 650953086 + engine self-burn 12/12 + finalize one-pass ledger 965,535 / K=539,120; no takeover lane this wave, no declared external turn, origin vacancy four-check green at publish)"),
    ("r1015, queue-depth supply depth-1 at publish", "r1018, queue-depth supply depth-1 at publish"),
    ("(r1015 MSG-", "(r1018 MSG-"),
    (" r1015 BEFORE this freeze", " r1018 BEFORE this freeze"),
    ("(r1016 derive landed pre-freeze expected)", "(r1019 derive landed pre-freeze expected)"),
    ("r1016 window machine-SUB derive landed pre-freeze", "r1019 window machine-SUB derive landed pre-freeze"),
    ("r1016 window derive landed pre-freeze commit", "r1019 window derive landed pre-freeze commit"),
    ("and committed at origin 4a001a96d, machine-SUB from the frozen W246 prereg 6473fb7f8.",
     "and committed at origin 4c403cb16, machine-SUB from the frozen W246 prereg fbfb7b43f."),
    ("prereg derived by the bm-a r1016 window and committed same-window (machine-SUB from the frozen W246 prereg 6473fb7f8; commit",
     "prereg derived by the bm-a r1019 window and committed same-window (machine-SUB from the frozen W246 prereg fbfb7b43f; commit"),
    ("derived by the bm-a r1016 window", "derived by the bm-a r1019 window"),
    ("785936d84", "e06f4ee2a"),
    ("MSG-20261015-1328-bma-w246-seat", "MSG-20261015-1608-bma-w247-seat"),
    # --- ledger anchors (W246 finalize) ---
    ("963,335", "965,535"), ("536,920", "539,120"),
    ("963_335", "965_535"), ("536_920", "539_120"),
    # --- ordinals ---
    ("owner_rows=235", "owner_rows=236"), ("bma_rows=127", "bma_rows=128"),
    ("len(owner_rows_live) == 235", "len(owner_rows_live) == 236"),
    ("len(bma_rows_live) == 127", "len(bma_rows_live) == 128"),
    ("expect 235/127/67", "expect 236/128/67"),
    ("rows 127", "rows 128"), ("rows 235", "rows 236"),
    ("236th", "237th"), ("128th", "129th"),
    ("bma_ordinal=128", "bma_ordinal=129"),
    ('probe_receipt_bma_ordinal_face": 127', 'probe_receipt_bma_ordinal_face": 128'),
    ("one hundred and twenty-eighth", "one hundred and twenty-ninth"),
    ("ONE HUNDRED AND TWENTY-SEVENTH", "ONE HUNDRED AND TWENTY-EIGHTH"),
    ("TWO HUNDRED AND FORTY-SIXTH", "TWO HUNDRED AND FORTY-SEVENTH"),
    ("thirty-fifth consecutive window", "thirty-sixth consecutive window"),
    ("thirty-fourth consecutive", "thirty-fifth consecutive"),
    # --- face ordinals (frozen W247 receipt governs: A=ninth; gap=ninth) ---
    ("eighth consecutive seed-gap", "ninth consecutive seed-gap"),
    ("gap face eighth consecutive", "gap face ninth consecutive"),
    # --- own band literals (W247 A 559_501..561_500 / B 544_501..544_700) ---
    ("557_501", "559_501"), ("559_500", "561_500"),
    ("542_201", "544_501"), ("542_400", "544_700"),
    # --- upstream tail variable roll ---
    ("w245_a_tail", "w246_a_tail"), ("w245_b_tail", "w246_b_tail"),
    # --- E63 lineage comment (mechanical +1, one-behind face preserved) ---
    ("arith_a245/arith_b245", "arith_a246/arith_b246"),
    # --- projection key roll ---
    ("W247p_", "W248p_"),
    # --- extraction structure (estate fixed 90; legs W232..W245 14; +1 fresh W246 leg) ---
    ("the W247 block appends ONE fresh W246 leg -> 103 rows.",
     "the W247 block appends ONE fresh W246 leg -> 104 rows."),
    ('assert par_full.count("assert pf.N1_BANDS[") == 103', 'assert par_full.count("assert pf.N1_BANDS[") == 104'),
    ("!= 103 (90 estate", "!= 104 (90 estate"),
    ("W232..W245 legs 13", "W232..W245 legs 14"),
    ("extracted verbatim (13)", "extracted verbatim (14)"),
    ('assert legs_sec.count("assert pf.N1_BANDS[") == 13', 'assert legs_sec.count("assert pf.N1_BANDS[") == 14'),
    ("thirteen legs", "fourteen legs"),
    ("list(range(232, 245))", "list(range(232, 246))"),
    ("= 104 rows ending", "= 105 rows ending"),
    ("-> 104 parity rows", "-> 105 parity rows"),
    # --- family-6 boundary quadruple (spaced forms + contiguous stale forms; descending order) ---
    ("range(209, 247)", "range(209, 248)"),
    ("range(16, 246)", "range(16, 247)"),
    ("range(17, 246)", "range(17, 247)"),
    ("if w < 246)", "if w < 247)"),
    ("if w < 245)", "if w < 246)"),
    ("w<246", "w<247"),
    ("w<245", "w<246"),
    ("below 246", "below 247"),
    ("range(16,245)", "range(16,246)"),
    ("range(17,245)", "range(17,246)"),
    ("below-245", "below-246"),
    # --- receipt wave field (one-behind lineage face: = upstream wave) ---
    ('"wave": 245', '"wave": 246'),
]
VMAP_FLOORS = {
    "15:1x bm-a r1017 freeze window": 1,
    "r1013 window; engine self-burn 12/12 + finalize one-pass verified r1015)": 1,
    "bm-a splice generation r1013 window": 1,
    "bm-a r1013 splice generation": 2,
    "the bm-a r1013 window; engine": 1,
    "bm-a own seat executed at the bm-a r1013 window; engine self-burn 12/12; finalize one-pass bm-a r1015 own-wave closeout, ledger 963,335 / K=536,920 machine-read": 1,
    "finalize one-pass bm-a r1015 own-wave closeout ledger 963,335 / K=536,920": 1,
    "r1015, pre-seat probe": 1,
    "bm-a r1015 own-wave closeout 13:2x": 1,
    "finalize landing 13:2x": 2,
    "own-wave closeout r1015": 1,
    "own-seat continuity (bm-a landed the W246 chain same-window r1015: freeze 29d3ab761 + engine self-burn 12/12 + finalize one-pass ledger 963,335 / K=536,920; no takeover lane this wave, no declared external turn, origin vacancy four-check green at publish)": 8,
    "r1015, queue-depth supply depth-1 at publish": 1,
    "(r1015 MSG-": 1,
    " r1015 BEFORE this freeze": 1,
    "(r1016 derive landed pre-freeze expected)": 1,
    "r1016 window machine-SUB derive landed pre-freeze": 2,
    "r1016 window derive landed pre-freeze commit": 1,
    "and committed at origin 4a001a96d, machine-SUB from the frozen W246 prereg 6473fb7f8.": 1,
    "derived by the bm-a r1016 window": 2,
    "prereg derived by the bm-a r1016 window and committed same-window (machine-SUB from the frozen W246 prereg 6473fb7f8; commit": 1,
    "785936d84": 2,
    "MSG-20261015-1328-bma-w246-seat": 7,
    "963,335": 14, "536,920": 14, "963_335": 1, "536_920": 1,
    "owner_rows=235": 1, "bma_rows=127": 1,
    "len(owner_rows_live) == 235": 1, "len(bma_rows_live) == 127": 1,
    "expect 235/127/67": 1,
    "rows 127": 3, "rows 235": 2, "236th": 2, "128th": 6, "bma_ordinal=128": 7,
    'probe_receipt_bma_ordinal_face": 127': 1,
    "one hundred and twenty-eighth": 2,
    "ONE HUNDRED AND TWENTY-SEVENTH": 1,
    "TWO HUNDRED AND FORTY-SIXTH": 3,
    "thirty-fifth consecutive window": 1, "thirty-fourth consecutive": 1,
    "eighth consecutive seed-gap": 8,
    "gap face eighth consecutive": 5,
    "557_501": 2, "559_500": 2, "542_201": 2, "542_400": 2,
    "w245_a_tail": 18, "w245_b_tail": 19,
    "arith_a245/arith_b245": 3,
    "W247p_": 6,
    "the W247 block appends ONE fresh W246 leg -> 103 rows.": 1,
    'assert par_full.count("assert pf.N1_BANDS[") == 103': 1,
    "!= 103 (90 estate": 1,
    "W232..W245 legs 13": 2,
    "extracted verbatim (13)": 1,
    'assert legs_sec.count("assert pf.N1_BANDS[") == 13': 1,
    "thirteen legs": 1,
    "list(range(232, 245))": 1,
    "= 104 rows ending": 1,
    "-> 104 parity rows": 1,
    "range(209, 247)": 2, "range(16, 246)": 2, "range(17, 246)": 3,
    "if w < 246)": 5, "if w < 245)": 1,
    "w<246": 4, "w<245": 3, "below 246": 2,
    "range(16,245)": 3, "range(17,245)": 3, "below-245": 3,
    '"wave": 245': 1,
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
OLD["a1"] = span("# NEW FACE vs the W246 editor (honest disclosure): the W247 B band returns",
                 "# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.", "a1")
OLD["a2"] = span("# W247 FACE (probe receipt leg1 relation_asserts):",
                 "B naive continuation drift vs probe receipt leg1 ARITH_B", "a2")
OLD["a5"] = window('"    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail",', 6, "a5")
OLD["a6"] = window('"    # W247+ projection (gate-derived pre-seat probe leg4, pre-W247",', 8, "a6")
OLD["a7"] = window(' "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN arithmetic ', 9, "a7")
OLD["a8"] = window('"ADMIT convention); W247+ projection per this window gate: ",', 5, "a8")
OLD["a9"] = span('"        # band facts (law sec.4 W247 row): A = FIRST-CLEAN arithmetic",',
                 'assert _entry_shard_of(0, 12) == (\\"PERPETUAL-N1-W247-SHARD-0\\",', "a9")
OLD["a12"] = window('          "+ B=FIRST-CLEAN arithmetic continuation of the prior-wave B tail (double-clean face, "', 2, "a12")
OLD["a13"] = window('                     "B": "FIRST-CLEAN arithmetic continuation of the prior-wave B tail (CLEAN at naive start', 1, "a13")
OLD["a14"] = window('  "downstream_seat": "W247 seat NOT YET PUBLISHED', 1, "a14")
OLD["a17"] = window(" f'{MEM_I}\"b_exit_seed_base\": {b_lo},   # law sec.4 W247 B:", 1, "a17")

# ---------- NEW blocks (final W247 language) ----------
NEW = {}
NEW["a1"] = """# NEW FACE vs the W246 editor (honest disclosure): the W247 B band takes the
# REGISTERED-REFUSAL staircase band-hop face FIRST-MATERIALIZED (the naive
# continuation 542_401..542_600 from the W246-REGISTERED B tail 542_400+1 is
# REFUSED by the registered W239 A band 542_501..544_500 on the post-W246
# universe -- honest forward first-clean walk hops=1 lands at 544_501..544_700,
# B base == refuser band end 544_500+1 EXACT, B_hop_chain=[naive
# 542_401..542_600 -> 544_501; refuser registered W239 A band 542_501..544_500],
# B_naive_hops=1 -- fc_b == fc_b_naive: the hop refuser is the registered W239
# A band, not the own-A reservation; B_no_ownA_jump=true;
# B_hop_lands_inside_A=false; the first-clean B window is NOT inside the W247
# own-wave A window 559_501..561_500) -- relation asserts mirror the probe
# receipt leg1 relation_asserts exactly (B_band_hop_expected_face +
# B_base_above_priorB_tail + B_no_ownA_jump + B_hop_lands_inside_A=false),
# and the staircase band-hop adjacency is machine-asserted (B base ==
# refuser-band-end+1 EXACT). A-face ordinal disclosed honestly: the W246
# receipt said "eighth consecutive seed-gap"; the FROZEN W247 artifacts (probe
# receipt leg1 A_semantics + prereg sec.3 + seat MSG) all say NINTH consecutive
# seed-gap A-continuation face -- the frozen receipt governs, ordinal +1
# disclosed, never transcribed r587.
# Zero hardcoded upstream band values: ALL W246 facts machine-derived from the
# LIVE pf import at freeze time (the registered W246 row -- bm-a own seat
# honored), cross-checked against the committed ADMIT receipt
# (results/_w247bma_20261015_probe_receipt.json) which was derived on the
# post-W246-REGISTERED universe. If the LIVE W246 bands differ from the
# declared face, the continuation asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W246 editor): the parity estate + the W232..W245
# fresh legs are BOTH extracted from the OWN W246 block physical bytes
# (bm-a r1017 splice generation, committed -- structure known exactly); the
# W247 block appends ONE fresh W246 leg (machine-derived from the live
# registered row) -> 105 parity rows (estate 90 ending W231 + W232..W245
# legs 14 + W246 leg 1). Extraction self-asserts the 90-row estate cut and
# the 14-leg segment regardless.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x."""

NEW["a2"] = """# W247 FACE (probe receipt leg1 relation_asserts):
# A keeps the A-continuation base (prior-wave A tail+1 EXACT -- the naive
# arithmetic continuation is CLEAN at its own start, hops=0, A_hop_chain
# empty, A_clean_at_naive_start=true -- ninth consecutive seed-gap face per
# the W246 seat leg4 anticipation confirmed live, frozen receipt A_semantics
# verbatim); B takes the REGISTERED-REFUSAL staircase band-hop face (the
# naive continuation from the W246-REGISTERED B tail is REFUSED by the
# registered W239 A band, honest forward walk hops=1 first-clean, B base ==
# refuser-band-end+1 EXACT, B_hop_chain non-empty, B_naive_hops=1;
# fc_b == fc_b_naive: the hop refuser is the registered W239 A band, not the
# own-A reservation; B_no_ownA_jump=true; B_hop_lands_inside_A=false;
# gap face ninth consecutive); A sits far above
# the B staircase (seed-decoupled A/B gap); machine-derived from the LIVE
# registered row, never transcribed.
assert w246_a_tail + 1 == a_lo, "A continuation base relation broken (A == prior-wave A tail+1 EXACT)"
assert a_lo > w246_b_tail + 1, "seed-decoupled A-continuation face violated: A base must sit ABOVE prior-B tail+1 (seed-gap)"
assert b_hi < a_lo, "seed-decoupled A/B gap face violated: B window must sit entirely below own-A"
assert W246["b_exit"][1] < W246["a"][0], \\
    "upstream W246 row in-wave decoupled relation broken (registered W246 B window must sit below own W246 A window)"
assert leg1.get("hops_A") == 0, "A hop-count drift vs probe receipt leg1 (A band naive hops=0, A-continuation face)"
assert leg1.get("hops_B") == 1, "B hop-count drift vs probe receipt leg1 (B band hops=1, REGISTERED-REFUSAL staircase band-hop face)"
assert leg1.get("A_hop_chain") == [] and (
    leg1.get("A_clean_at_naive_start") is True
    or (leg1.get("relation_asserts") or {}).get("A_clean_at_naive_start") is True
), \\
    "A hop-chain face drift (fc_a == fc_a_naive, hops=0, A_clean_at_naive_start=true -- naive continuation CLEAN at own start)"
assert leg1.get("B_hop_chain") and leg1.get("B_naive_hops") == 1, "B hop-chain face drift (hops=1, REGISTERED-REFUSAL staircase band-hop face FIRST-MATERIALIZED)"
_hc = (leg1.get("B_hop_chain") or [{}])[0]
_refb = (_hc.get("refuser_bands") or [[]])[0]
assert _hc.get("window") == [w246_b_tail + 1, w246_b_tail + 200] and _hc.get("jump_to") == b_lo \\
    and _refb == [pf_mod.N1_BANDS[239]["a"][0], pf_mod.N1_BANDS[239]["a"][1]] \\
    and b_lo == _refb[1] + 1, \\
    f"B hop-chain drift vs probe receipt leg1 (refuser=registered W239 A band, base==refuser-end+1 EXACT): {_hc}"
assert leg1.get("B_hop_lands_inside_A") is False, "B lands-inside-own-A drift vs probe receipt leg1 (B_hop_lands_inside_A must be False)"
assert leg1.get("B_naive_first_clean") == [b_lo, b_hi], "B naive first-clean drift vs probe receipt leg1"
ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_band_hop_expected_face") and ra.get("B_base_above_priorB_tail") \\
    and ra.get("AB_mutual_exclusion") and ra.get("B_no_ownA_jump") \\
    and ra.get("B_hop_lands_inside_A") is False, \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"
assert [w246_a_tail + 1, w246_a_tail + 2_000] == leg1["ARITH_A"], \\
    f"A-continuation start drift vs probe receipt leg1 ARITH_A: {[w246_a_tail + 1, w246_a_tail + 2_000]} != {leg1['ARITH_A']}"
assert [w246_b_tail + 1, w246_b_tail + 200] == leg1["ARITH_B"], \\
    f"B naive continuation drift vs probe receipt leg1 ARITH_B: {[w246_b_tail + 1, w246_b_tail + 200]} != {leg1['ARITH_B']}" """

NEW["a5"] = '''"    # B = FIRST-CLEAN honest forward walk past a REGISTERED refusal",
"    # (naive continuation " + fmt(w246_b_tail + 1) + ".." + fmt(w246_b_tail + 200) + " REFUSED by the",
"    # registered W239 A band " + fmt(pf_mod.N1_BANDS[239]["a"][0]) + ".." + fmt(pf_mod.N1_BANDS[239]["a"][1]) + " -> hop 1 lands at",
"    # " + fmt(b_lo) + ".." + fmt(b_hi) + " (hops=1, B_naive_hops=1, B base == refuser-band-end+1 EXACT;",
"    # fc_b == fc_b_naive: the hop refuser is the registered band, not the own-A",
"    # reservation) -- B lands OUTSIDE the own-A window " + fmt(a_lo) + ".." + fmt(a_hi) + ": seed-decoupled A/B gap face ninth;",'''

NEW["a6"] = '''"    # W248+ projection (gate-derived pre-seat probe leg4, pre-W247",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W248p_A_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " (this window's gate: CLEAN, zero live",
"    # seed refusers) / B naive " + rec["legs"]["leg4"]["W248p_B_naive"] + " CLEAN (staircase continuation, hops=" + str(rec["legs"]["leg4"]["hops_B"]) + ",",
"    # B base == prior-B-tail+1 EXACT, lands OUTSIDE the projection A window;",
"    # B_hop lands-inside-A=false leg present); W248 freezer MUST",
"    # re-derive on the post-W247 universe AND reserve the own-wave A window",
"    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1",
"    # equality); never transcribe r587.",'''

NEW["a7"] = ''' "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN honest forward ",
 "walk past a REGISTERED refusal (the naive continuation ",
 f"{fmt(w246_b_tail + 1)}..{fmt(w246_b_tail + 200)} is REFUSED by the registered W239 A band ",
 f"{fmt(pf_mod.N1_BANDS[239]['a'][0])}..{fmt(pf_mod.N1_BANDS[239]['a'][1])} -- hops=1, B_naive_hops=1, ",
 "B_hop_chain=[naive -> first-clean] staircase band-hop face FIRST-MATERIALIZED ",
 "(fc_b == fc_b_naive: the hop refuser is the registered W239 A band, not the own-A reservation); B lands OUTSIDE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap ",
 "face ninth consecutive; B base == refuser-band-end+1 EXACT ",
 "machine-checkable; cross-window convergence with the W246 seat leg4 succession projection ",'''

NEW["a8"] = '''"ADMIT convention); W248+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W248p_A_naive']} CLEAN (hops=0, zero live seed refusers) / B naive ",
 f"{rec['legs']['leg4']['W248p_B_naive']} CLEAN (hops=0, staircase continuation, B base == prior-B-tail+1 EXACT, lands OUTSIDE the projection A window -- B_hop lands-inside-A=false leg present; seed-gap face ",
 "inherited); W248 freezer MUST re-derive on the post-W247 universe AND ",
 "reserve the own-wave A window when deriving B (do NOT assume the ",'''

NEW["a9"] = '''"        # band facts (law sec.4 W247 row): A = FIRST-CLEAN arithmetic",
"        # continuation of the prior-wave A tail",
f"        # ({fmt(w246_a_tail + 1)}..{fmt(w246_a_tail + 2_000)} CLEAN at naive start on the",
"        # registered universe, hops=0, A_hop_chain empty +",
"        # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,",
"        # ninth consecutive seed-gap face, exactly as the W246 seat leg4",
"        # succession projection notes anticipated; A base == prior-wave A",
f"        # tail+1 ({fmt(w246_a_tail)}+1) machine-checkable;",
"        # B = FIRST-CLEAN honest forward walk past a REGISTERED refusal",
f"        # (naive continuation {fmt(w246_b_tail + 1)}..{fmt(w246_b_tail + 200)} REFUSED by the",
f"        # registered W239 A band {fmt(pf_mod.N1_BANDS[239]['a'][0])}..{fmt(pf_mod.N1_BANDS[239]['a'][1])} -- hop 1 lands at",
f"        # {fmt(b_lo)}..{fmt(b_hi)}; hops=1, B_naive_hops=1, B_hop_chain=[naive -> first-clean],",
"        # staircase band-hop face FIRST-MATERIALIZED (fc_b == fc_b_naive: the",
"        # hop refuser is the registered W239 A band, not the own-A",
"        # reservation), anticipated by the W246 probe leg4 + the W246",
"        # prereg sec.8 downstream_seat projection;",
"        # B lands OUTSIDE the own-A window",
f"        # {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap face ninth consecutive;",
"        # B base == refuser-band-end+1 EXACT",
"        # machine-checkable; B_hop_lands_inside_A=false;",
"        # cross-window convergence with",
"        # the W246 seat leg4 succession projection notes -- all",
"        # MANDATORY notes honored (post-W246 universe",
"        # re-derive + live-trace re-read, no staircase-equality assumption);",
f\'        assert WAVE_CONFIGS[247]["a_seed_base"] == {a_lo} == {w246_a_tail} + 1, (\',
\'            "W247 A must be the first-clean arithmetic continuation of the "\',
\'            "prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true -- "\',
\'            "seed-decoupled A-continuation face, ninth consecutive seed-gap face, "\',
\'            "exactly as the W246 seat leg4 succession projection notes "\',
\'            "anticipated; A base == prior-wave A tail+1 machine-checkable)")\',
f"        arith_a247 = set(range({a_lo}, {a_hi + 1}))",
"        assert not (arith_a247 & reg_ints), \\\\",
\'            "W247 A window must be CLEAN (first-clean ADMIT face, A-continuation)"\',
f\'        assert WAVE_CONFIGS[247]["b_exit_seed_base"] == {b_lo} == pf.N1_BANDS[239]["a"][1] + 1, (\',
\'            "W247 B REGISTERED-REFUSAL staircase band-hop face: the naive continuation "\',
f\'            "{fmt(w246_b_tail + 1)}..{fmt(w246_b_tail + 200)} is REFUSED by the registered W239 A band "\',
f\'            "{fmt(pf_mod.N1_BANDS[239]["a"][0])}..{fmt(pf_mod.N1_BANDS[239]["a"][1])} -- honest forward hop 1 lands at the first-clean window "\',
\'            "(hops=1, B_naive_hops=1, B_hop_chain=[naive -> first-clean]) -- B base == refuser-band-end+1 "\',
\'            "EXACT (B_band_hop_expected_face + B_base_above_priorB_tail + B_no_ownA_jump face relation "\',
\'            "asserts, probe receipt leg1 mirrored exactly; B_hop_lands_inside_A=false)")\',
f"        assert {b_lo} > {w246_b_tail}, \\\\",
\'            "W247 B first-clean base must sit above the prior-wave B tail (staircase band-hop face)"\',
f"        arith_b247 = set(range({b_lo}, {b_hi + 1}))",
"        assert not (arith_b247 & reg_ints), \\\\",
\'            "W247 B window must be CLEAN (first-clean ADMIT face, REGISTERED-REFUSAL staircase band-hop)"\',
"        assert not (arith_b247 & arith_a247), \\\\",
\'            "W247 A/B same-freeze mutual exclusion (seed-decoupled gap face inherited: B below own A)"\',
"        assert _entry_shard_of(0, 12) == (\\"PERPETUAL-N1-W247-SHARD-0\\",",'''

NEW["a12"] = '''\'          "+ B=FIRST-CLEAN honest forward walk past a REGISTERED refusal (staircase band-hop face, "\',
\'          "hops=1, B_naive_hops=1, B base == refuser-band-end+1 EXACT, B_no_ownA_jump=true, "\','''

NEW["a13"] = '''                     "B": "FIRST-CLEAN honest forward walk past a REGISTERED refusal (staircase band-hop face FIRST-MATERIALIZED: naive continuation 542_401..542_600 REFUSED by the registered W239 A band 542_501..544_500 -> first-clean 544_501..544_700, hops=1, B_naive_hops=1, B base == refuser-band-end+1 EXACT; fc_b == fc_b_naive: the hop refuser is the registered W239 A band, not the own-A reservation; B_no_ownA_jump=true; B_hop_lands_inside_A=false; seed-decoupled A/B gap face ninth consecutive)"},'''

NEW["a14"] = '''  "downstream_seat": "W248 seat ALREADY PUBLISHED by bm-c (own-committed b2774fbf3/86819ad77 bm-c r1030, waits-upstream ARMED: W247 in-flight at this freeze window -- this W247 freeze+finalize DISARMS it; W249 = next free number, next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W249 freezer MUST re-derive live on the post-W248 universe + reserve the own-wave A window when deriving B per the W247 seat leg4 mandate, never transcribe r587 -- W248p face per this window's probe leg4: A naive 561_501..563_500 CLEAN (hops=0, zero live refusers) / B naive 544_701..544_900 CLEAN (hops=0, staircase continuation, B base == prior-B-tail+1 EXACT, lands OUTSIDE the projection A window); seed-gap face inherited: W247 A/B decoupled, do NOT assume the staircase A-base==prior-B-tail+1 equality)",'''

NEW["a17"] = ''' f\'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W247 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN REGISTERED-REFUSAL staircase band-hop: naive continuation {fmt(w246_b_tail + 1)}..{fmt(w246_b_tail + 200)} REFUSED by the registered W239 A band {fmt(pf_mod.N1_BANDS[239]["a"][0])}..{fmt(pf_mod.N1_BANDS[239]["a"][1])} -> honest forward hop 1 lands here; B base == refuser-band-end+1 EXACT; fc_b == fc_b_naive: hop refuser = registered band, not own-A reservation; B lands outside own-A; seed-decoupled A/B gap face ninth consecutive)\','''

BLOCKS = ["a1", "a2", "a5", "a6", "a7", "a8", "a9", "a12", "a13", "a14", "a17"]
for name in BLOCKS:
    ob = OLD[name]
    assert T2.count(ob) == 1, "BLOCK %s count=%d (expect 1)" % (name, T2.count(ob))
    T2 = T2.replace(ob, NEW[name].rstrip("\n"), 1)
    assert NEW[name].rstrip("\n") in T2, "BLOCK %s NEW not inserted" % name

# ---------- count-gate leg-count bumps + new [243]==4 insert ----------
for n, c_old, c_new in [(242, 4, 5), (241, 5, 6), (240, 6, 7), (239, 7, 8),
                        (238, 8, 9), (237, 9, 10), (236, 10, 11)]:
    o = 'N1_BANDS[%d]["a"][1])}),\') == %d' % (n, c_old)
    v = 'N1_BANDS[%d]["a"][1])}),\') == %d' % (n, c_new)
    assert T2.count(o) == 1, "count-gate [%d]==%d count=%d" % (n, c_old, T2.count(o))
    T2 = T2.replace(o, v, 1)
_line = ("assert n1_t4.count(f'assert pf.N1_BANDS[244] == {{\"a\": ({fmt(pf_mod.N1_BANDS[244][\"a\"][0])}"
         ", {fmt(pf_mod.N1_BANDS[244][\"a\"][1])}),') == 3")
assert T2.count(_line) == 1, "count-gate [244]==3 line not found (post-vmap)"
_ins = _line + ("\nassert n1_t4.count(f'assert pf.N1_BANDS[243] == {{\"a\": ({fmt(pf_mod.N1_BANDS[243][\"a\"][0])}"
                ", {fmt(pf_mod.N1_BANDS[243][\"a\"][1])}),') == 4")
T2 = T2.replace(_line, _ins, 1)

# ---------- post gates: must-have / must-not-have / precise counts ----------
MUST = ["WAVE_CONFIGS[247]", "PERPETUAL-N1-W247-SHARD-0", "n1w247-0of12",
        '247: {"batch"', "range(16, 247)", "range(17, 247)", "range(209, 248)",
        "range(232, 246)", "W247 materializer face", "arith_b247", "arith_a247",
        "MSG-20261015-1608-bma-w247-seat", "e06f4ee2a", "965,535", "539,120",
        "TWO HUNDRED AND FORTY-SEVENTH", "one hundred and twenty-ninth",
        "W248p_A_naive", "n1_w247_results.json", "B_band_hop_expected_face",
        "REGISTERED-REFUSAL staircase band-hop", "559_501", "544_501",
        "561_501", "staircase band-hop", "129th", "237th", "bma_ordinal=129",
        "ninth consecutive seed-gap", "4c403cb16", "fbfb7b43f",
        "own-seat continuity", "650953086", 'hops_B") == 1',
        'B_naive_hops") == 1', "n1_w246_results.json", "PERPETUAL_N1_W247_PREREG",
        "expect 236/128/67", "B_hop_chain=[naive -> first-clean]"]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s
MUST_NOT = ["WAVE_CONFIGS[245]", "N1_BANDS.get(245)",
            "PERPETUAL-N1-W246", "r1013", "r1015", "r1016",
            "963,335", "536,920", "963_335", "536_920",
            "557_501", "542_201", "542_200",
            "perpetual_n2_w15_scrnull", "bma_ordinal=128", "128th", "236th",
            "TWO HUNDRED AND FORTY-SIXTH", "one hundred and twenty-eighth",
            "ONE HUNDRED AND TWENTY-SEVENTH", "W247p_", "range(16, 246)",
            "range(17, 246)", "range(209, 247)",
            "MSG-20261015-1328", "785936d84", "29d3ab761", "4a001a96d",
            "6473fb7f8", "rows 127", "rows 235",
            "owner_rows=235", 'probe_receipt_bma_ordinal_face": 127',
            "gap face eighth consecutive", "double-clean",
            "B_double_clean_expected_face", "B_hop_chain empty",
            "B_naive_hops=0", "arith_a245", "arith_b245", "W232..W244",
            "thirteen legs", "live-seed-hop", "B_honest_forward_hop_expected_face",
            "takeover lane disclosed", "13:2x", "15:1x",
            "thirty-fifth consecutive window", "thirty-fourth consecutive",
            "n1_w245", "n1w246"]
for s in MUST_NOT:
    if s == "r1015" or s == "6473fb7f8":
        for _m in re.finditer(s, T2):
            print("DBG-%s-CTX:" % s, repr(T2[max(0, _m.start() - 100):_m.end() + 100]))
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))
# the a1 NEW block QUOTES the W246 receipt's "eighth consecutive seed-gap" claim
# exactly once (honest ordinal-jump disclosure: eighth -> NINTH per the frozen
# W247 receipt) -- the single legitimate instance; a second = real drift
assert T2.count("eighth consecutive seed-gap") == 1, \
    "seed-gap eighth-quote must be exactly 1 (a1 honest disclosure), got %d" \
    % T2.count("eighth consecutive seed-gap")
# E63 lineage: the rolled slash form arith_a246/arith_b246 (the W246 editor's
# variable face, referenced by the W247 editor's lineage comments) is the ONLY
# legitimate a246/b246 presence; standalone = un-replaced own-code drift
assert T2.count("arith_a246/arith_b246") == 3, \
    "arith lineage slash-form must be exactly 3, got %d" % T2.count("arith_a246/arith_b246")
assert T2.count("arith_a246") == 3 and T2.count("arith_b246") == 3, \
    "standalone arith_a246/arith_b246 leak (outside slash lineage form)"
# upstream W246 finalize product refs (chain dep check) are the only
# legitimate n1_w246 face; a fourth = un-rolled own-results reference
assert T2.count("n1_w246_results.json") == 3, \
    "upstream n1_w246_results.json refs must be exactly 3, got %d" \
    % T2.count("n1_w246_results.json")
# upstream W246 prereg references are LEGITIMATE in the W247 editor (frozen
# cross-generation naming): exactly 2 = upstream tpl pickaxe + law PRE_KEY_I
# anchor; a third instance = un-rolled OWN-prereg reference (fail-closed)
assert T2.count("PERPETUAL_N1_W246_PREREG") == 2, \
    "upstream W246 prereg refs must be exactly 2 (pickaxe + PRE_KEY_I), got %d" \
    % T2.count("PERPETUAL_N1_W246_PREREG")
assert T2.count('"--", "research/PERPETUAL_N1_W246_PREREG.md"') == 1, \
    "upstream pickaxe line form drift"
assert T2.count('("research/PERPETUAL_N1_W246_PREREG.md') == 1, \
    "PRE_KEY_I anchor form drift"
# the lineage template file ref _w246bma_freeze_edits.py is the single
# legitimate w246bma instance (own-file refs all rolled to w247bma)
assert T2.count("w246bma") == 1 and "_w246bma_freeze_edits.py template" in T2, \
    "w246bma must be exactly 1 (lineage template ref), got %d" % T2.count("w246bma")
# precise legitimate prior-boundary faces (family-6 zero-assert + receipt note)
assert T2.count("if w < 246)") == 1, \
    "if w < 246) count=%d (expect 1: the family-6 zero-assert target only)" % T2.count("if w < 246)")
assert T2.count("w<246") == 3, \
    "w<246 count=%d (expect 3: family-6 stale-gate message + receipt" \
    " prior-boundary note + E63 lineage prior-wave-boundary comment)" % T2.count("w<246")
assert T2.count("if w < 247)") == 5, \
    "if w < 247) count=%d (expect 5: 3 block LHS + family-6 assert x2)" % T2.count("if w < 247)")
# no malformed windows in NEW prose (r773 law)
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
py_compile.compile(OUT, doraise=True)
print("W247 EDITOR GEN OK -> %s (%d lines, %d bytes)" % (OUT, T2.count("\n") + 1, len(T2)))
print("blocks replaced: %s" % ",".join(BLOCKS))
