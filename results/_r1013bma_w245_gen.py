# -*- coding: utf-8 -*-
# r1013 bm-a: W245 five-face freeze EDITOR GENERATOR (Phase-B count-asserted
# ordered transform). Source = committed W244 editor
# (results/_w244bma_freeze_edits.py, proven live-fire: freeze 10bdb987b +
# engine self-burn 12/12 + finalize one-pass r1008 fivekeys ALL PASS).
# OLD blocks loaded from the committed dead-window Phase-A inventory
# (results/_r1012bma_w245_oldblocks/*.txt, estate-absorb 85be61aa0) --
# physical bytes, never re-typed. NEW blocks final W245 language.
# W245 facts: probe ADMIT receipt results/_w245bma_20261015_probe_receipt.json
# (A 555_501..557_500 clean hops=0 sixth seed-gap / B naive 541_901..542_100
# REFUSED by live SEED_REGISTRY 542_000 perpetual_n2_w15_scrnull -> honest
# forward first-clean 542_001..542_200 hops=1); prereg 6473fb7f8; seat
# MSG-20261015-0844-bma-w245-seat @ 2b0947947; upstream W244 finalize
# ledger 961,135 / K=534,720. Zero transcription of upstream band values:
# the generated editor machine-derives all upstream facts live at run time.
import io, os, re, sys, py_compile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w244bma_freeze_edits.py")
OUT = os.path.join(REPO, "results", "_w245bma_freeze_edits.py")
OLD_DIR = os.path.join(REPO, "results", "_r1012bma_w245_oldblocks")

T0 = io.open(SRC, encoding="utf-8", newline="").read()

# ---------- ordered vmap (placeholder-safe; applied to full text AND old blocks) ----------
P1, P2, P3, P4 = "\x01A\x01", "\x01B\x01", "\x01C\x01", "\x01D\x01"
VMAP = [
    ("W244", P1), ("W243", "W244"), (P1, "W245"),
    ("w244bma", "w245bma"),
    ('244: {"batch"', P2), ('243: {"batch"', '244: {"batch"'), (P2, '245: {"batch"'),
    ('244: {"a"', P3), ('243: {"a"', '244: {"a"'), (P3, '245: {"a"'),
    ("WAVE_CONFIGS[244]", "WAVE_CONFIGS[245]"),
    ("N1_BANDS.get(243)", "N1_BANDS.get(244)"),
    ("N1_BANDS[243]", "N1_BANDS[244]"),
    ("555_500", "557_500"), ("553_501", "555_501"),
    ("541_701", "542_001"), ("541_900", "542_200"),
    ("958,935", "961,135"), ("532,520", "534,720"),
    ("958_935", "961_135"), ("532_520", "534_720"),
    ("70141bc22", P4), ("260ffd3f8", "6473fb7f8"), (P4, "260ffd3f8"),
    ("08df387e0", "2b0947947"),
    ("MSG-20261015-0206-bma-w244-seat", "MSG-20261015-0844-bma-w245-seat"),
    ("06:1x bm-a r1007 freeze window", "12:4x bm-a r1013 freeze window"),
    ("01:4x", "07:4x"),
    ("r1002", "r1007"), ("r1003", "r1008"),
    ("r1005", "r1010"), ("r1006", "r1011"), ("r1004", "r1010"),
    ("TWO HUNDRED AND FORTY-FOURTH", "TWO HUNDRED AND FORTY-FIFTH"),
    ("one hundred and twenty-sixth", "one hundred and twenty-seventh"),
    ("bma_ordinal=126", "bma_ordinal=127"),
    ("126th", "127th"),
    ('probe_receipt_bma_ordinal_face": 125', 'probe_receipt_bma_ordinal_face": 126'),
    ("rows 125", "rows 126"),
    ("234th", "235th"),
    ("rows 233", "rows 234"),
    ("!= 101 (90 estate", "!= 102 (90 estate"),
    ("== 101", "== 102"),
    ("W232..W242 legs 11", "W232..W243 legs 12"),
    ("W232..W242 legs extracted verbatim (11)", "W232..W243 legs extracted verbatim (12)"),
    ("W232..W242 fresh legs", "W232..W243 fresh legs"),
    ("W232..W242 eleven legs", "W232..W243 twelve legs"),
    ("eleven legs", "twelve legs"),
    ("-> 101 rows", "-> 102 rows"),
    ("102 rows ending", "103 rows ending"),
    ('== 11 \\', '== 12 \\'),
    ("list(range(232, 243))", "list(range(232, 244))"),
    ("(242, 241, 240, 239, 238, 237, 236, 235, 234, 233)",
     "(243, 242, 241, 240, 239, 238, 237, 236, 235, 234)"),
    ("range(209, 245)", "range(209, 246)"),
    ("w<244", "w<245"), ("range(16, 244)", "range(16, 245)"),
    ("range(17, 244)", "range(17, 245)"),
    ("below 244", "below 245"),
    ("fifth consecutive seed-gap", "sixth consecutive seed-gap"),
    ("gap face sixth consecutive", "gap face seventh consecutive"),
    ("thirty-third consecutive window", "thirty-fourth consecutive window"),
    ("zero takeover", "takeover lane disclosed (GM re-assignment: bm-c declared the W245 turn at r1020 closeout then heartbeat froze 64.5min with zero origin commits post the W244-finalize unblock -- stall >1 round, takeover per the r1009 next-pointer rule)"),
]
# expected hit floors on the FULL text (count-asserted; 0 = optional)
VMAP_FLOORS = {
    "w244bma": 3, '244: {"batch"': 1, '243: {"batch"': 1, '244: {"a"': 1, '243: {"a"': 2,
    "WAVE_CONFIGS[244]": 2, "N1_BANDS.get(243)": 1, "N1_BANDS[243]": 2,
    "958,935": 2, "532,520": 2, "958_935": 1, "532_520": 1,
    "08df387e0": 1, "MSG-20261015-0206-bma-w244-seat": 1, "01:4x": 2,
    "r1002": 3, "r1003": 3, "r1005": 2, "r1006": 2, "r1004": 3,
    "TWO HUNDRED AND FORTY-FOURTH": 1, "one hundred and twenty-sixth": 1,
    "bma_ordinal=126": 2, "126th": 2, "rows 125": 3, "234th": 1, "rows 233": 1,
    "!= 101 (90 estate": 1, "== 101": 1, "W232..W242 legs 11": 2,
    "W232..W242 fresh legs": 2, "-> 101 rows": 1, "102 rows ending": 1,
    "list(range(232, 243))": 1, "range(209, 245)": 2,
    "w<244": 2, "range(16, 244)": 2, "range(17, 244)": 2, "below 244": 2,
    "fifth consecutive seed-gap": 2, "zero takeover": 5,
    "(242, 241, 240, 239, 238, 237, 236, 235, 234, 233)": 2,
}

def xf(t):
    for o, n in VMAP:
        t = t.replace(o, n)
    return t

for o, _ in VMAP:
    f = VMAP_FLOORS.get(o)
    if f is not None and T0.count(o) < f:
        raise SystemExit("VMAP FLOOR FAIL: %r count=%d floor=%d" % (o, T0.count(o), f))

T1 = xf(T0)

# ---------- block replacements (OLD' = xf(OLD inventory bytes); NEW final) ----------
def old(name):
    return io.open(os.path.join(OLD_DIR, name + ".txt"), encoding="utf-8", newline="").read()

NEW = {}

NEW["a1"] = """# NEW FACE vs the W244 editor (honest disclosure): the W245 B band takes the
# live-seed-hop face (hops=1 -- the naive continuation
# 541_901..542_100 is REFUSED by the live SEED_REGISTRY point 542_000
# perpetual_n2_w15_scrnull inside the naive window; honest forward walk lands
# first-clean 542_001..542_200) -- B base != prior-B-tail+1 EXACT in this
# face; relation asserts mirror the probe receipt leg1 relation_asserts
# exactly (B_honest_forward_hop_expected_face +
# B_base_above_priorB_tail), and the hop adjacency is machine-asserted
# (B base == live refuser 542_000+1 EXACT; B_naive_hops=1 recorded).
# Zero hardcoded upstream band values: ALL W244 facts machine-derived from the
# LIVE pf import at freeze time (the registered W244 row -- bm-a own seat
# honored), cross-checked against the committed ADMIT receipt
# (results/_w245bma_20261015_probe_receipt.json) which was derived on the
# post-W244-REGISTERED universe. If the LIVE W244 bands differ from the
# declared face, the continuation asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W244 editor): the parity estate + the W232..W243
# fresh legs are BOTH extracted from the OWN W244 block physical bytes
# (bm-a r1007 splice generation, committed -- structure known exactly); the
# W245 block appends ONE fresh W244 leg (machine-derived from the live
# registered row) -> 103 parity rows (estate 90 ending W231 + W232..W243
# legs 12 + W244 leg 1). Extraction self-asserts the 90-row estate cut and
# the 12-leg segment regardless.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
"""

NEW["a2"] = """# W245 FACE (probe receipt leg1 relation_asserts):
# A keeps the A-continuation base (prior-wave A tail+1 EXACT -- the naive
# arithmetic continuation is CLEAN at its own start, hops=0, A_hop_chain
# empty, A_clean_at_naive_start=true -- sixth consecutive seed-gap face per
# the W244 seat leg4 anticipation confirmed live); B takes the live-seed-hop
# face (the naive continuation 541_901..542_100 is REFUSED by the live
# SEED_REGISTRY point 542_000 perpetual_n2_w15_scrnull inside the naive
# window; hops=1, hop chain recorded, honest forward walk lands first-clean
# 542_001..542_200 -- B base == live refuser+1 EXACT, B_no_ownA_jump=true;
# B_hop_lands_inside_A=false; gap face seventh consecutive); A sits far above
# the B staircase (seed-decoupled A/B gap); machine-derived from the LIVE
# registered row, never transcribed.
assert w244_a_tail + 1 == a_lo, "A continuation base relation broken (A == prior-wave A tail+1 EXACT)"
assert w244_b_tail + 1 < b_lo, "B live-seed-hop face violated: B base must sit ABOVE the refused naive base (prior-B tail+1)"
assert a_lo > w244_b_tail + 1, "seed-decoupled A-continuation face violated: A base must sit ABOVE prior-B tail+1 (seed-gap)"
assert b_hi < a_lo, "seed-decoupled A/B gap face violated: B window must sit entirely below own-A"
assert W244["b_exit"][1] < W244["a"][0], \\
    "upstream W244 row in-wave decoupled relation broken (registered W244 B window must sit below own W244 A window)"
assert leg1.get("hops_A") == 0 and leg1.get("hops_B") == 1, "hop-count drift vs probe receipt leg1 (A naive hops=0 / B hops=1 live-seed refusal)"
assert leg1.get("A_hop_chain") == [] and (
    leg1.get("A_clean_at_naive_start") is True
    or (leg1.get("relation_asserts") or {}).get("A_clean_at_naive_start") is True
), \\
    "A hop-chain face drift (fc_a == fc_a_naive, hops=0, A_clean_at_naive_start=true -- naive continuation CLEAN at own start)"
assert leg1.get("B_naive_hops") == 1 and (leg1.get("B_hop_chain") or [{}])[0].get("refuser_pts") == [542_000], \\
    "B hop-chain face drift (B_naive_hops=1, first refuser point 542_000 -- live-seed hop face)"
assert leg1.get("B_naive_first_clean") == [b_lo, b_hi], "B naive first-clean drift vs probe receipt leg1"
ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_honest_forward_hop_expected_face") and ra.get("B_base_above_priorB_tail") \\
    and ra.get("AB_mutual_exclusion") and ra.get("B_no_ownA_jump"), \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"
assert [w244_a_tail + 1, w244_a_tail + 2_000] == leg1["ARITH_A"], \\
    f"A-continuation start drift vs probe receipt leg1 ARITH_A: {[w244_a_tail + 1, w244_a_tail + 2_000]} != {leg1['ARITH_A']}"
assert [w244_b_tail + 1, w244_b_tail + 200] == leg1["ARITH_B"], \\
    f"B naive continuation drift vs probe receipt leg1 ARITH_B: {[w244_b_tail + 1, w244_b_tail + 200]} != {leg1['ARITH_B']}"
"""

NEW["a5"] = """\"    # B = FIRST-CLEAN post-hop forward walk (the naive continuation\",
\"    # (\" + fmt(w244_b_tail + 1) + \"..\" + fmt(w244_b_tail + 200) + \" is REFUSED by the live\",
\"    # SEED_REGISTRY point 542_000 perpetual_n2_w15_scrnull; hops=1, hop chain\",
\"    # recorded, honest forward walk lands first-clean \" + fmt(b_lo) + \"..\" + fmt(b_hi) + \" -- B\",
\"    # lands OUTSIDE the own-A window \" + fmt(a_lo) + \"..\" + fmt(a_hi) + \":\",
\"    # seed-decoupled A/B gap face seventh; B base == live refuser 542_000+1 machine-checkable;\",
"""

NEW["a6"] = """\"    # W246+ projection (gate-derived pre-seat probe leg4, pre-W245\",
\"    # universe): A naive first-clean \" + rec[\"legs\"][\"leg4\"][\"W246p_A_naive\"] + \" hops=\" + str(rec[\"legs\"][\"leg4\"][\"hops_A\"]) + \" (this window's gate: CLEAN, zero live\",
\"    # seed refusers) / B naive first-clean \" + rec[\"legs\"][\"leg4\"][\"W246p_B_naive\"] + \" hops=\" + str(rec[\"legs\"][\"leg4\"][\"hops_B\"]) + \" (this window's gate: CLEAN, zero live\",
\"    # refusers anticipated -- B first-clean \" + rec[\"legs\"][\"leg4\"][\"W246p_B_first_clean\"] + \"; B lands OUTSIDE\",
\"    # the naive A window, seed-gap face inherited); W246 freezer MUST\",
\"    # re-derive on the post-W245 universe AND reserve the own-wave A window\",
\"    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1\",
"""

NEW["a7"] = """ \"non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN post-hop \",
 \"forward walk (the naive continuation \",
 f\"{fmt(w244_b_tail + 1)}..{fmt(w244_b_tail + 200)} is REFUSED by the live SEED_REGISTRY point \",
 \"542_000 perpetual_n2_w15_scrnull -- hops=1, hop chain recorded; honest forward walk first-clean \",
 f\"{fmt(b_lo)}..{fmt(b_hi)} -- B lands OUTSIDE the \",
 f\"own-A window {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap \",
 \"face seventh consecutive; B base == live refuser 542_000+1 \",
 \"machine-checkable; cross-window convergence with the W244 seat leg4 succession projection \",
 \"notes -- all MANDATORY notes honored (post-W244 universe \",
 \"re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt \",
"""

NEW["a8"] = """ \"ADMIT convention); W246+ projection per this window gate: \",
 f\"A naive first-clean {rec['legs']['leg4']['W246p_A_naive']} CLEAN (hops=0, zero live seed refusers) / B naive first-clean \",
 f\"{rec['legs']['leg4']['W246p_B_naive']} hops=0 (both windows CLEAN on the pre-W245 universe, zero live refusers anticipated -- B first-clean {rec['legs']['leg4']['W246p_B_first_clean']} -- lands OUTSIDE the naive A window -- seed-gap face \",
 \"inherited); W246 freezer MUST re-derive on the post-W245 universe AND \",
 \"reserve the own-wave A window when deriving B (do NOT assume the \",
"""

NEW["a9"] = "\"        # band facts (law sec.4 W245 row): A = FIRST-CLEAN arithmetic\",\n" \
"  \"        # continuation of the prior-wave A tail\",\n" \
" f\"        # ({fmt(w244_a_tail + 1)}..{fmt(w244_a_tail + 2_000)} CLEAN at naive start on the\",\n" \
"  \"        # registered universe, hops=0, A_hop_chain empty +\",\n" \
"  \"        # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,\",\n" \
"  \"        # sixth consecutive seed-gap face, exactly as the W244 seat leg4\",\n" \
"  \"        # succession projection notes anticipated; A base == prior-wave A\",\n" \
" f\"        # tail+1 ({fmt(w244_a_tail)}+1) machine-checkable;\",\n" \
"  \"        # B = FIRST-CLEAN post-hop forward walk (the naive continuation\",\n" \
" f\"        # ({fmt(w244_b_tail + 1)}..{fmt(w244_b_tail + 200)} is REFUSED by the live SEED_REGISTRY\",\n" \
"  \"        # point 542_000 perpetual_n2_w15_scrnull; hops=1, hop chain\",\n" \
"  \"        # recorded, honest forward walk lands first-clean\",\n" \
" f\"        # {fmt(b_lo)}..{fmt(b_hi)} -- B\",\n" \
"  \"        # lands OUTSIDE the own-A window\",\n" \
" f\"        # {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap face seventh consecutive;\",\n" \
"  \"        # B base == live refuser 542_000+1\",\n" \
"  \"        # machine-checkable;\",\n" \
"  \"        # B_no_ownA_jump=true (fc_b == fc_b_naive -- the hop is seed-driven,\",\n" \
"  \"        # not an own-A reservation jump); cross-window convergence with\",\n" \
"  \"        # the W244 seat leg4 succession projection notes -- all\",\n" \
"  \"        # MANDATORY notes honored (post-W244 universe\",\n" \
"  \"        # re-derive + live-trace re-read, no staircase-equality assumption);\",\n" \
" f'        assert WAVE_CONFIGS[245][\"a_seed_base\"] == {a_lo} == {w244_a_tail} + 1, ('\n" \
" '            \"W245 A must be the first-clean arithmetic continuation of the \"'\n" \
" '            \"prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true -- \"'\n" \
" '            \"seed-decoupled A-continuation face, sixth consecutive seed-gap face, \"'\n" \
" '            \"exactly as the W244 seat leg4 succession projection notes \"'\n" \
" '            \"anticipated; A base == prior-wave A tail+1 machine-checkable)\")'\n" \
" f\"        arith_a245 = set(range({a_lo}, {a_hi + 1}))\"\n" \
" \"        assert not (arith_a245 & reg_ints), \\\\\"\n" \
" '            \"W245 A window must be CLEAN (first-clean ADMIT face, A-continuation)\"'\n" \
" f'        assert WAVE_CONFIGS[245][\"b_exit_seed_base\"] == {b_lo} == {542_000} + 1, ('\n" \
" '            \"W245 B live-seed-hop face: the naive staircase continuation \"'\n" \
" f'            \"{fmt(w244_b_tail + 1)}..{fmt(w244_b_tail + 200)} is REFUSED by the live \"'\n" \
" '            \"SEED_REGISTRY point 542_000 perpetual_n2_w15_scrnull (hops=1, hop chain \"'\n" \
" '            \"recorded) -- honest forward walk lands first-clean \"'\n" \
" f'            \"{fmt(b_lo)}..{fmt(b_hi)}; B base == refuser+1 EXACT, B base != prior-B-tail+1 \"'\n" \
" '            \"in this face (B_base_above_priorB_tail + B_live_seed_hop face relation \"'\n" \
" '            \"asserts, probe receipt leg1 mirrored exactly; B_no_ownA_jump=true)\")'\n" \
" f\"        assert {b_lo} > {w244_b_tail} + 1, \\\\\"\n" \
" '            \"W245 B first-clean base must sit above the refused naive base (live-seed hop face)\"'\n" \
" f\"        assert 542_000 in reg_ints and 542_000 not in set(range(\"\n" \
" f\"{b_lo}, {b_hi + 1})), \\\\\"\n" \
" '            \"W245 B refuser-adjacency face: the live refuser 542_000 must sit inside SEED_REGISTRY and immediately below the B window\"'\n" \
" f\"        arith_b245 = set(range({b_lo}, {b_hi + 1}))\"\n" \
" \"        assert not (arith_b245 & reg_ints), \\\\\"\n" \
" '            \"W245 B window must be CLEAN (first-clean ADMIT face, post-hop forward walk)\"'\n" \
" \"        assert not (arith_b245 & arith_a245), \\\\\"\n" \
" '            \"W245 A/B same-freeze mutual exclusion (seed-decoupled gap face inherited: B below own A)\"'\n" \
" \"        assert _entry_shard_of(0, 12) == (\\\"PERPETUAL-N1-W245-SHARD-0\\\",\n" \
" '                                          \"n1w245-0of12\"), \"W245 entry identity\"'\n"

NEW["a12"] = """ '          \"+ B=FIRST-CLEAN post-hop forward walk (live-seed-hop face, \"',
 '          \"hops=1, hop chain recorded, B base == live refuser 542_000+1 EXACT, B base != prior-B-tail+1, \"',
"""

NEW["a13"] = """                     \"B\": \"FIRST-CLEAN post-hop forward walk (the naive continuation is REFUSED by the live SEED_REGISTRY point 542_000 perpetual_n2_w15_scrnull; hops=1, hop chain recorded, honest forward walk lands first-clean -- B base == refuser+1 EXACT, B base != prior-B-tail+1 in this face; B_no_ownA_jump=true; B_hop_lands_inside_A=false; seed-decoupled A/B gap face seventh consecutive)\"},
"""

NEW["a14"] = """  \"downstream_seat\": \"W246 seat NOT YET PUBLISHED at this freeze window (next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W246 freezer MUST re-derive live on the post-W245 universe + reserve the own-wave A window when deriving B per the W245 seat leg4 mandate, never transcribe r587 -- W246p face: A naive 557_501..559_500 CLEAN (hops=0) / B naive 542_201..542_400 CLEAN (hops=0, zero live refusers anticipated on the pre-W245 universe))\",
"""

NEW["a17"] = """ f'{MEM_I}\"b_exit_seed_base\": {b_lo},   # law sec.4 W245 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN post-hop forward walk: naive staircase {fmt(w244_b_tail + 1)}..{fmt(w244_b_tail + 200)} REFUSED by live SEED_REGISTRY point 542_000 perpetual_n2_w15_scrnull, hops=1, hop chain recorded; honest forward walk first-clean; B base == refuser+1 EXACT; B lands outside own-A; seed-decoupled A/B gap face seventh consecutive)',
"""

# a15 = pure band-literal line -> already rolled by vmap (no block needed).
BLOCKS = ["a1", "a2", "a5", "a6", "a7", "a8", "a9", "a12", "a13", "a14", "a17"]
T2 = T1
for name in BLOCKS:
    ob = xf(old(name))
    assert T2.count(ob) == 1, "BLOCK %s count=%d (expect 1)" % (name, T2.count(ob))
    T2 = T2.replace(ob, NEW[name].rstrip("\n"), 1)
    assert NEW[name].rstrip("\n") in T2, "BLOCK %s NEW not inserted" % name

# a15 = pure band-literal line -> already rolled by vmap (no block needed).

# ---------- count-gate leg-count bumps ([242]..[236]: +1 each) + new [243]==2 line ----------
for n, c_old, c_new in [(242, 2, 3), (241, 3, 4), (240, 4, 5), (239, 5, 6),
                        (238, 6, 7), (237, 7, 8), (236, 8, 9)]:
    o = "N1_BANDS[%d][\"a\"][1])}),') == %d" % (n, c_old)
    v = "N1_BANDS[%d][\"a\"][1])}),') == %d" % (n, c_new)
    assert T2.count(o) == 1, "count-gate [%d]==%d count=%d" % (n, c_old, T2.count(o))
    T2 = T2.replace(o, v, 1)
# insert [243]==2 line after the [244]==1 line (rolled from the original [243]==1)
_line244 = "assert n1_t4.count(f'assert pf.N1_BANDS[244] == {{\"a\": ({fmt(pf_mod.N1_BANDS[244][\"a\"][0])}, {fmt(pf_mod.N1_BANDS[244][\"a\"][1])}),') == 1"
assert T2.count(_line244) == 1, "count-gate [244]==1 line not found"
_ins = _line244 + "\nassert n1_t4.count(f'assert pf.N1_BANDS[243] == {{\"a\": ({fmt(pf_mod.N1_BANDS[243][\"a\"][0])}, {fmt(pf_mod.N1_BANDS[243][\"a\"][1])}),') == 2"
T2 = T2.replace(_line244, _ins, 1)

# ---------- post gates: must-have / must-not-have ----------
MUST = ["WAVE_CONFIGS[245]", "PERPETUAL-N1-W245-SHARD-0", "n1w245-0of12",
        '245: {"batch"', "range(16, 245)", "range(17, 245)", "range(209, 246)",
        "range(232, 244)", "W245 materializer face", "arith_b245", "arith_a245",
        "perpetual_n2_w15_scrnull", "542_000", "MSG-20261015-0844-bma-w245-seat",
        "2b0947947", "6473fb7f8", "961,135", "534,720", "TWO HUNDRED AND FORTY-FIFTH",
        "one hundred and twenty-seventh", "W246p_A_naive", "n1_w245_results.json" ]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s
MUST_NOT = ["W243", "WAVE_CONFIGS[244]", "N1_BANDS.get(243)", "N1_BANDS[243]",
            "PERPETUAL_N1_W243", "w243bma", "w244bma", "r1002", "r1003", "r1005",
            "r1006", "r1004", "958,935", "532,520", "553_501", "541_701",
            "08df387e0", "70141bc22", "126th", "234th", "TWO HUNDRED AND FORTY-FOURTH",
            "one hundred and twenty-sixth", "W245p_", "range(16, 244)",
            "range(17, 244)", "range(209, 245)", "bma_ordinal=126",
            "MSG-20261015-0206", "list(range(232, 243))"]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))
# known legitimate exception: prior-block boundary note keeps ONE w<244 face
assert T2.count("w<244") == 1, "w<244 prior-boundary note count=%d (expect 1)" % T2.count("w<244")

# no malformed windows in NEW prose (r773 law)
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
py_compile.compile(OUT, doraise=True)
print("W245 EDITOR GEN OK -> %s (%d lines, %d bytes)" % (OUT, T2.count("\n") + 1, len(T2)))
print("blocks replaced: %s" % ",".join(BLOCKS))
