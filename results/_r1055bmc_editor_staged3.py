# -*- coding: utf-8 -*-
# r1055 bm-c: derive results/_w254bmc_freeze_edits.py from the committed W253
# freeze-edits script (results/_w253bmc_freeze_edits.py, proven live-fire W253
# splice bm-c r1053 window: splice c9b4fd855 + engine self-burn 12/12 +
# finalize one-pass ledger 980,935 / K=554,520 five-key ALL PASS by the r1053
# continuation closeout fa70f3765) via COUNT-ASSERTED ORDERED TRANSFORM (E63
# lineage, 6th-gen pass ordering: P1 structural outputs BLANKET-IMMUNE; the
# W254 extraction faces stay structurally identical to the W253 estate
# mandate -- estate 69 rows W138..W206 full-span ONLY + kept W211..W238 (28)
# + dropped W239..W252 (14) + fresh W239..W253 (15) = 112 parity rows per the
# frozen W254 prereg sec.3 mandate -- only the count faces move 14->15 /
# 111->112 / 41->42 / 13->14).
# W254 facts (machine-read from the probe receipt, never transcribed):
# bands A 574_101..576_100 (1-HOP STAIRCASE-AFFECTS-A walk, THIRD
# consecutive A-hop -- the naive continuation 573_901..575_900 is REFUSED at
# its own start: the registered W253 B band 573_901..574_100 sits INSIDE the
# naive A window = staircase CONTINUES to affect A; the W253 prereg sec.5
# item5 A-CLEAN-at-naive projection was a pre-W253-universe face, superseded
# live per r587, divergence disclosed; the walk hops past the W253 B tail
# 574_100 -> A first-clean 574_101..576_100, hops=1; A base == registered
# prior-wave B tail+1 (574_100+1) EXACT) / B 576_101..576_300 (1-HOP own-A
# RESERVATION CASCADE above own-A, FOURTH consecutive -- the naive
# continuation 574_101..574_300 is REFUSED at its own start: the naive
# window lands INSIDE the own-wave W254 A first-clean window
# 574_101..576_100, own-A reservation cascade standard leg; the walk hops
# past the own-A tail 576_100 -> B landing 576_101..576_300, hops=1; B base
# == own-A tail+1 (576_100+1) EXACT), upstream W253 = bm-c own chain, seat
# MSG-20261016-14xx-bmc-w254-seat @ origin fa70f3765 r1053 closeout,
# prereg e2c4b543e derived bm-c r1054 (authored 18:0x).
import io, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w253bmc_freeze_edits.py")
DST = os.path.join(REPO, "results", "_w254bmc_freeze_edits.py")

t = io.open(SRC, encoding="utf-8").read()
log = []

def rep(old, new, expect=None, tag=""):
    global t
    n = t.count(old)
    if expect is not None:
        assert n == expect, f"[{tag}] count {n} != {expect} for: {old[:70]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x {old[:48]!r}")

# xf(): exact composition of the blanket passes (P2/P3/P4) + the P5a
# sensitive mappings, used to derive post-pass needles for whole-chunk
# replacements WITHOUT hand-transcription (zero mental-derivation risk).
def xf(s):
    # blankets, in pass order: P2 downstream, P3 self, P4 upstream
    s = s.replace("W254", "W255")
    s = s.replace("253", "254")
    s = s.replace("252", "253")
    # P5a mappings (post-blanket forms)
    s = s.replace("MSG-20261016-12xx-bmc-w254-seat", "MSG-20261016-14xx-bmc-w254-seat")
    s = s.replace("r1050", "r1053")
    s = s.replace("r1052", "r1054")
    s = s.replace("978,735", "980,935")
    s = s.replace("552,320", "554,520")
    s = s.replace("SEVENTY-THIRD", "SEVENTY-FOURTH")
    s = s.replace("TWO HUNDRED AND FIFTY-THIRD", "TWO HUNDRED AND FIFTY-FOURTH")
    s = s.replace("forty-first consecutive", "forty-second consecutive")
    s = s.replace("bmc_ordinal=73", "bmc_ordinal=74")
    s = s.replace("authored 13:2x", "authored 18:0x")
    s = s.replace("f6433ee61", "fa70f3765")
    s = s.replace("741371846", "e2c4b543e")
    return s

def chunk(src_text, dst_text, tag):
    global t
    needle = xf(src_text)
    n = t.count(needle)
    assert n == 1, f"[{tag}] chunk needle count {n} != 1 (needle head: {needle[:80]!r})"
    t = t.replace(needle, dst_text)
    log.append(f"{tag}: chunk 1x ({len(src_text)} -> {len(dst_text)} chars)")

# ============ P1: structural faces, BLANKET-IMMUNE outputs ============
rep("(249, 248, 247, 246, 245, 244, 243, 242, 241, 240)",
    "(250, 249, 248, 247, 246, 245, 244, 243, 242, 241)", 2, "P1-transitive-deps")
rep("range(209, 254)", "range(209, 255)", 2, "P1-liveness-range")
rep('def fmt(n):  # 571901 -> "571_901"', 'def fmt(n):  # 574101 -> "574_101"', 1, "P1-fmt-comment")

# ============ P2: downstream shift W254 -> W255 (incl. W254p_* receipt keys) ============
rep("W254", "W255", None, "P2-downstream")
assert "W254" not in t, "P2 leftover W254"

# ============ P3: self shift 253 -> 254 ============
n253 = t.count("253")
rep("253", "254", None, "P3-self")
log.append(f"P3 consumed {n253} '253' substrings")

# ============ P4: upstream shift 252 -> 253 ============
n252 = t.count("252")
rep("252", "253", None, "P4-upstream")
log.append(f"P4 consumed {n252} '252' substrings")

# ============ P5a: numeric/anchor/ordinal/window faces (post-blanket forms) ============
rep("978_735", "980_935", 1, "P5a-ledger-int")
rep("552_320", "554_520", 1, "P5a-k-int")
rep("978,735", "980,935", 8, "P5a-ledger-prose")
rep("552,320", "554,520", 8, "P5a-k-prose")
rep("bmc_ordinal=73", "bmc_ordinal=74", 7, "P5a-ordinal72")
rep("SEVENTY-THIRD", "SEVENTY-FOURTH", 3, "P5a-seventysecond")
rep("TWO HUNDRED AND FIFTY-THIRD", "TWO HUNDRED AND FIFTY-FOURTH", 3, "P5a-250th")
rep("forty-first consecutive", "forty-second consecutive", 2, "P5a-finface")
rep("73rd own wave", "74th own wave", 3, "P5a-72nd-ownwave")
rep("MSG-20261016-12xx-bmc-w254-seat", "MSG-20261016-14xx-bmc-w254-seat", 7, "P5a-seat-msg")
rep("f6433ee61", "fa70f3765", 2, "P5a-seat-origin")
rep("741371846", "e2c4b543e", 1, "P5a-prereg-commit")
# r-window faces: upstream W253 chain = splice r1053 window (dead 14:0x-15:0x
# estate, landed c9b4fd855) + finalize r1053 (closeout 15:2x fa70f3765);
# W254 prereg derive window = r1054 (authored 18:0x); this freeze = r1055.
rep("2026-10-16 14:2x bm-c r1053 freeze window", "2026-10-16 20:2x bm-c r1055 freeze window", 1, "P5a-header-window")
rep("W253 finalize one-pass bm-c r1050 window closeout 12:2x",
    "W253 finalize one-pass bm-c r1053 window closeout 15:2x", 1, "P5a-closeout-window")
rep("r1050 splice window", "r1053 splice window", 3, "P5a-splice-window")
rep("r1050", "r1053", 19, "P5a-splice-window-rest")
rep("r1052", "r1054", 7, "P5a-prereg-window")
rep("authored 13:2x", "authored 18:0x", 2, "P5a-authored-time")
# aging-face needle heals (same-window disclosed, r1045/r1047/r1050 precedent family):
rep("transitive window W240..W249 checked", "transitive window W241..W250 checked", 1, "P5a-aging-deps-cmt")
rep("engine_owner==bm-c rows 72 + candidate", "engine_owner==bm-c rows 73 + candidate", 1, "P5a-aging-rows71-heal")

# ============ P5b: extraction count faces (frozen W254 prereg sec.3 mandate) ============
# estate 69 (W138..W206) + kept W211..W238 (28) UNCHANGED; dropped W239..W252 (13);
# fresh W239..W253 (14); total parity 111 rows; legs segment W211..W252 (41).
rep("# block's own W239..W251 legs (13 rows) do NOT enter the estate path;",
    "# block's own W239..W252 legs (14 rows) do NOT enter the estate path;", 1, "P5b-hdr-ownlegs")
rep("# after extraction, fresh W239..W253 legs (14 rows) are added,",
    "# after extraction, fresh W239..W253 legs (15 rows) are added,", 1, "P5b-hdr-freshlegs")
rep("# parity = 111 rows (W138..W206 + W211..W253). Zero assumption zero risk.",
    "# parity = 112 rows (W138..W206 + W211..W253). Zero assumption zero risk.", 1, "P5b-hdr-parity-count")
rep("# block's own W239..W251 legs (13) are EXCLUDED from the estate path per the",
    "# block's own W239..W252 legs (14) are EXCLUDED from the estate path per the", 1, "P5b-ext-excl")
rep("# prereg mandate; the W254 block appends fresh W239..W253 legs (14,",
    "# prereg mandate; the W254 block appends fresh W239..W253 legs (15,", 1, "P5b-ext-fresh")
rep("# machine-derived from the LIVE pf registry at freeze time) -> 111 parity",
    "# machine-derived from the LIVE pf registry at freeze time) -> 112 parity", 1, "P5b-ext-parcount")
rep("assert par_full.count(\"assert pf.N1_BANDS[\") == 110, \\\n    f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 110 (69 estate + W211..W251 legs 41)\"",
    "assert par_full.count(\"assert pf.N1_BANDS[\") == 111, \\\n    f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 111 (69 estate + W211..W252 legs 42)\"", 1, "P5b-parfull")
rep("assert legs_sec.count(\"assert pf.N1_BANDS[\") == 41 \\\n    and [int(w) for w in _legs_ws] == list(range(211, 253)), \\\n    f\"legs segment not W211..W251 forty-one legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}\"",
    "assert legs_sec.count(\"assert pf.N1_BANDS[\") == 42 \\\n    and [int(w) for w in _legs_ws] == list(range(211, 253)), \\\n    f\"legs segment not W211..W252 forty-two legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}\"", 1, "P5b-legs-assert")
rep("# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W253\n# block's own W239..W251 legs (13) are excluded from the estate path",
    "# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W253\n# block's own W239..W252 legs (14) are excluded from the estate path", 1, "P5b-split-cmt")
rep("assert legs_dropped.count(\"assert pf.N1_BANDS[\") == 13 \\\n    and [int(w) for w in _dropped_ws] == list(range(239, 253)), \\\n    f\"dropped segment not W239..W251 thirteen legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}\"",
    "assert legs_dropped.count(\"assert pf.N1_BANDS[\") == 14 \\\n    and [int(w) for w in _dropped_ws] == list(range(239, 253)), \\\n    f\"dropped segment not W239..W252 fourteen legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}\"", 1, "P5b-dropped-assert")
rep('"fresh_legs_row_asserts": 14,', '"fresh_legs_row_asserts": 15,', 1, "P5b-rcpt-fresh13")
rep("+ legs_kept.count(\"assert pf.N1_BANDS[\") + 14,",
    "+ legs_kept.count(\"assert pf.N1_BANDS[\") + 15,", 1, "P5b-rcpt-total13")
rep('"    #     physical bytes; the W253 block\'s own W239..W251 legs (13) are",',
    '"    #     physical bytes; the W253 block\'s own W239..W252 legs (14) are",', 1, "P5b-hdr-ownlegs-mat")
rep('"    #     W239..W253 legs (14) added, machine-derived from the live pf",',
    '"    #     W239..W253 legs (15) added, machine-derived from the live pf",', 1, "P5b-hdr-freshlegs-mat")
rep('"    #     registry at freeze time -> 111 parity rows (W138..W206+W211..W253).",',
    '"    #     registry at freeze time -> 112 parity rows (W138..W206+W211..W253).",', 1, "P5b-hdr-parcount-mat")

# receipt note (single big face: counts + generation stamp)
chunk('''
                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W238 legs (28) extracted verbatim per the frozen W253 prereg sec.3 mandate; the W252 block's own W239..W251 legs (13) EXCLUDED from the estate path per the same mandate; fresh W239..W252 legs (14) machine-derived from the live pf registry -> W253 block = 111 rows (W138..W206 + W211..W252); disclosed: (a) inherited W213 leg error-string face preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-253 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 5th-gen prevention this window: the W253 derive editor kept the P1-blanket-immune pass ordering and the extraction-restructure legs/kept/dropped wave-identity asserts fixed post-blanket (list(range(211,252))/list(range(211,239))/list(range(239,252)) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},
''',
'''
                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W238 legs (28) extracted verbatim per the frozen W254 prereg sec.3 mandate; the W253 block's own W239..W252 legs (14) EXCLUDED from the estate path per the same mandate; fresh W239..W253 legs (15) machine-derived from the live pf registry -> W254 block = 112 rows (W138..W206 + W211..W253); disclosed: (a) inherited W213 leg error-string face preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-254 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 6th-gen prevention this window: the W254 derive editor kept the P1-blanket-immune pass ordering and the extraction-restructure legs/kept/dropped wave-identity asserts fixed post-blanket (list(range(211,253))/list(range(211,239))/list(range(239,253)) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},
''', "P5b-rcpt-note")

# ============ P5c: band literals (probe ADMIT receipt bands) ============
rep('assert (a_lo, a_hi) == (571_901, 573_900) and (b_lo, b_hi) == (573_901, 574_100), \\',
    'assert (a_lo, a_hi) == (574_101, 576_100) and (b_lo, b_hi) == (576_101, 576_300), \\', 1, "P5c-band-drift")

# ============ P5d: ordinal/leg0/deps faces ============
rep('assert len(owner_rows_live) == 242 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 72, \\',
    'assert len(owner_rows_live) == 243 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 73, \\', 1, "P5d-ord-gate")
rep("(expect 242/129/72 PRE-splice post-W253 registration; this candidate = bm-c's 74th own wave per the same live-derive law, r587/r359)",
    "(expect 243/129/73 PRE-splice post-W253 registration; this candidate = bm-c's 74th own wave per the same live-derive law, r587/r359)", 1, "P5d-ord-err")
rep('# receipt leg0 face owner_rows=242 / bmc_rows=72 / bmc_ordinal=74',
    '# receipt leg0 face owner_rows=243 / bmc_rows=73 / bmc_ordinal=74', 1, "P5d-leg0-prose")
rep("-> owner rows 242 + candidate = 243rd EXACT; bm-c rows 72 +",
    "-> owner rows 243 + candidate = 244th EXACT; bm-c rows 73 +", 1, "P5d-ord-owner-prose")
rep("# candidate = 73rd EXACT -- bm-c own-seat continuity face (bm-c published the",
    "# candidate = 74th EXACT -- bm-c own-seat continuity face (bm-c published the", 1, "P5d-ord-bmc-prose")
rep("freeze-time live face owner rows 242 + candidate = 243rd EXACT",
    "freeze-time live face owner rows 243 + candidate = 244th EXACT", 1, "P5d-rcpt-242nd")
rep("freeze-time live derive bmc rows 72 + candidate 73rd EXACT per r587/r359",
    "freeze-time live derive bmc rows 73 + candidate 74th EXACT per r587/r359", 1, "P5d-bundle-72nd")
rep("post-W253 registration: bm-c rows 72 + candidate = 73rd owned",
    "post-W253 registration: bm-c rows 73 + candidate = 74th owned", 1, "P5d-rcpt-72nd-owned")
rep('"probe_receipt_bmc_ordinal_face": 73,', '"probe_receipt_bmc_ordinal_face": 74,', 1, "P5d-rcpt-ordface")
rep('f"W253+W248..W239 finalize products present "', 'f"W254+W249..W240 finalize products present "', 1, "P5d-print-deps")

# ============ P5e: A/B face structural rewrites (staircase + cascade CONTINUE) ============
# header NEW FACE block
chunk('''
# NEW FACE vs the W252 editor (honest disclosure, frozen W253 prereg sec.3
# mandate): BOTH bands take 1-HOP WALK faces -- staircase + cascade
# CONTINUE -- A = STAIRCASE-AFFECTS-A 1-hop walk, SECOND consecutive A-hop
# (the naive continuation 571_701..573_700 is REFUSED at its own start --
# the registered W252 B band 571_701..571_900 sits INSIDE the naive A
# window = staircase re-emergence continues to affect A; the W252 prereg
# sec.5 item5 A-CLEAN-at-naive projection was a pre-W252-universe face,
# superseded live per r587, divergence disclosed; the walk hops past the
# W252 B tail 571_900 -> A first-clean 571_901..573_900, hops=1; A base ==
# registered prior-wave B tail+1 (571_900+1) floor relation EXACT this
# window; A_clean_at_naive_start=false; A_staircase_hop_past_W252_B=true);
# B = 1-HOP own-A RESERVATION CASCADE above own-A, THIRD consecutive
# above-own-A (the naive continuation 571_901..572_100 is REFUSED at its
# own start -- the naive window lands INSIDE the own-wave A first-clean
# window 571_901..573_900, own-A reservation cascade standard leg; the
# walk hops past the own-A tail 573_900 -> B landing 573_901..574_100,
# hops=1; B lands ABOVE own-A; B base == own-A tail+1 (573_900+1) EXACT;
# B_naive_refused_at_start=true; B_lands_above_own_A=true;
# B_hop_lands_inside_A=false; hops=1).
''',
'''
# NEW FACE vs the W253 editor (honest disclosure, frozen W254 prereg sec.3
# mandate): BOTH bands take 1-HOP WALK faces -- staircase + cascade
# CONTINUE -- A = STAIRCASE-AFFECTS-A 1-hop walk, THIRD consecutive A-hop
# (the naive continuation 573_901..575_900 is REFUSED at its own start --
# the registered W253 B band 573_901..574_100 sits INSIDE the naive A
# window = staircase re-emergence continues to affect A; the W253 prereg
# sec.5 item5 A-CLEAN-at-naive projection was a pre-W253-universe face,
# superseded live per r587, divergence disclosed; the walk hops past the
# W253 B tail 574_100 -> A first-clean 574_101..576_100, hops=1; A base ==
# registered prior-wave B tail+1 (574_100+1) floor relation EXACT this
# window; A_clean_at_naive_start=false; A_staircase_hop_past_W253_B=true);
# B = 1-HOP own-A RESERVATION CASCADE above own-A, FOURTH consecutive
# above-own-A (the naive continuation 574_101..574_300 is REFUSED at its
# own start -- the naive window lands INSIDE the own-wave A first-clean
# window 574_101..576_100, own-A reservation cascade standard leg; the
# walk hops past the own-A tail 576_100 -> B landing 576_101..576_300,
# hops=1; B lands ABOVE own-A; B base == own-A tail+1 (576_100+1) EXACT;
# B_naive_refused_at_start=true; B_lands_above_own_A=true;
# B_hop_lands_inside_A=false; hops=1).
''', "P5e-hdr")

# band facts comment block
chunk('''
# W253 FACE (probe receipt leg1 relation_asserts):
# A takes the 1-HOP STAIRCASE-AFFECTS-A walk face, SECOND consecutive A-hop
# (naive continuation REFUSED at its own start -- A_clean_at_naive_start=false,
# A_staircase_hop_past_W252_B=true, hops=1, A_hop_chain verbatim in the
# receipt; the registered W252 B band sits INSIDE the naive A window =
# staircase re-emergence continues to affect A; the W252 prereg sec.5 item5
# A-CLEAN-at-naive projection superseded live r587, divergence disclosed;
# the walk hops past the W252 B tail -> A first-clean; A base == registered
# prior-wave B tail+1 EXACT -- SECOND consecutive A-hop of the staircase
# era, the fourteen-wave seed-gap face ENDED at W252); B takes the 1-HOP
# own-A RESERVATION CASCADE face (naive continuation REFUSED at its own
# start -- B_naive_refused_at_start=true, hops=1, B_hop_chain verbatim in
# the receipt; the naive window lands INSIDE the own-wave A first-clean
# window, own-A reservation cascade standard leg; the walk hops past the
# own-A tail -> B lands ABOVE own-A, B_lands_above_own_A=true -- B base ==
# own-A tail+1 EXACT, THIRD consecutive above-own-A landing);
# machine-derived from the LIVE registered row, never transcribed.
''',
'''
# W254 FACE (probe receipt leg1 relation_asserts):
# A takes the 1-HOP STAIRCASE-AFFECTS-A walk face, THIRD consecutive A-hop
# (naive continuation REFUSED at its own start -- A_clean_at_naive_start=false,
# A_staircase_hop_past_W253_B=true, hops=1, A_hop_chain verbatim in the
# receipt; the registered W253 B band sits INSIDE the naive A window =
# staircase re-emergence continues to affect A; the W253 prereg sec.5 item5
# A-CLEAN-at-naive projection superseded live r587, divergence disclosed;
# the walk hops past the W253 B tail -> A first-clean; A base == registered
# prior-wave B tail+1 EXACT -- THIRD consecutive A-hop of the staircase
# era, the fourteen-wave seed-gap face ENDED at W252); B takes the 1-HOP
# own-A RESERVATION CASCADE face (naive continuation REFUSED at its own
# start -- B_naive_refused_at_start=true, hops=1, B_hop_chain verbatim in
# the receipt; the naive window lands INSIDE the own-wave A first-clean
# window, own-A reservation cascade standard leg; the walk hops past the
# own-A tail -> B lands ABOVE own-A, B_lands_above_own_A=true -- B base ==
# own-A tail+1 EXACT, FOURTH consecutive above-own-A landing);
# machine-derived from the LIVE registered row, never transcribed.
''', "P5e-bandfacts")

# band-facts assert lines (A face)
rep('assert w253_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1 EXACT -- the 1-hop walk past the registered W253 B band; second consecutive A-hop of the staircase era; A_staircase_hop_past_W253_B=true)"',
    'assert w253_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1 EXACT -- the 1-hop walk past the registered W253 B band; third consecutive A-hop of the staircase era; A_staircase_hop_past_W253_B=true)"', 1, "P5e-a-base")
rep('assert a_lo >= w253_b_tail + 1, "A staircase landing floor relation (A base >= registered prior-wave B tail+1; the fourteen-wave seed-gap face ENDED at W253 -- second consecutive A-hop of the staircase era, A base == prior-B tail+1 EXACT this window per the prereg floor-relation mandate)"',
    'assert a_lo >= w253_b_tail + 1, "A staircase landing floor relation (A base >= registered prior-wave B tail+1; the fourteen-wave seed-gap face ENDED at W252 -- third consecutive A-hop of the staircase era, A base == prior-B tail+1 EXACT this window per the prereg floor-relation mandate)"', 1, "P5e-a-floor")
rep('assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation cascade lands ABOVE own-A -- third consecutive above-own-A; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"',
    'assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation cascade lands ABOVE own-A -- fourth consecutive above-own-A; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"', 1, "P5e-b-base")

# relation_asserts gate (W252_W253 rsv-key fix -- the P4 blanket produces the
# W251_W253 hybrid face; the probe receipt leg1 keys are W252_W253)
rep('''ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") is False and ra.get("A_staircase_hop_past_W253_B") \\
    and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_clean_at_naive_start") is False and ra.get("B_base_above_W253_tail") \\
    and ra.get("AB_mutual_exclusion") and ra.get("B_hop_lands_inside_A") is False \\
    and ra.get("B_lands_above_own_A") and ra.get("W251_W253_bands_respected_A") and ra.get("W251_W253_bands_respected_B"), \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"''',
'''ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") is False and ra.get("A_staircase_hop_past_W253_B") \\
    and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_clean_at_naive_start") is False and ra.get("B_base_above_W253_tail") \\
    and ra.get("AB_mutual_exclusion") and ra.get("B_hop_lands_inside_A") is False \\
    and ra.get("B_lands_above_own_A") and ra.get("W252_W253_bands_respected_A") and ra.get("W252_W253_bands_respected_B"), \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"''', 1, "P5e-ra-gate")

# pf_comment A/B lines
chunk('''
"    # band gate ADMIT results/_w253bmc_20261016_probe_receipt.json: A = 1-HOP",
"    # STAIRCASE-AFFECTS-A walk SECOND consecutive A-hop (the naive continuation " + fmt(w252_a_tail + 1) + ".." + fmt(w252_a_tail + 2_000) + " is REFUSED",
"    # at naive start -- the registered W252 B band sits INSIDE the naive A window;",
"    # the walk hops past the W252 B tail -> A first-clean, hops=1 -- SECOND",
"    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face",
"    # ENDED at W252;",
"    # A base == registered prior-wave B tail+1 (" + fmt(w252_b_tail) + "+1) machine-checkable; A_clean_at_naive_start=false;",
"    # A_staircase_hop_past_W252_B=true)",
"    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation",
"    # " + fmt(w252_b_tail + 1) + ".." + fmt(w252_b_tail + 200) + " lands INSIDE the own-wave A first-clean window --",
"    # own-A reservation cascade standard leg; hops=1,",
"    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A",
"    # tail -> B lands ABOVE own-A -- THIRD consecutive above-own-A;",
"    # B base == own-A tail+1 (" + fmt(a_hi) + "+1) EXACT; B_lands_above_own_A=true;",
"    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)",
''',
'''
"    # band gate ADMIT results/_w254bmc_20261016_probe_receipt.json: A = 1-HOP",
"    # STAIRCASE-AFFECTS-A walk THIRD consecutive A-hop (the naive continuation " + fmt(w253_a_tail + 1) + ".." + fmt(w253_a_tail + 2_000) + " is REFUSED",
"    # at naive start -- the registered W253 B band sits INSIDE the naive A window;",
"    # the walk hops past the W253 B tail -> A first-clean, hops=1 -- SECOND",
"    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face",
"    # ENDED at W253;",
"    # A base == registered prior-wave B tail+1 (" + fmt(w253_b_tail) + "+1) machine-checkable; A_clean_at_naive_start=false;",
"    # A_staircase_hop_past_W253_B=true)",
"    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation",
"    # " + fmt(w253_b_tail + 1) + ".." + fmt(w253_b_tail + 200) + " lands INSIDE the own-wave A first-clean window --",
"    # own-A reservation cascade standard leg; hops=1,",
"    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A",
"    # tail -> B lands ABOVE own-A -- FOURTH consecutive above-own-A;",
"    # B base == own-A tail+1 (" + fmt(a_hi) + "+1) EXACT; B_lands_above_own_A=true;",
"    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)",
''', "P5e-pfcmt")

# PRE block A/B lines
chunk('''
 "wave 253: ",
 "A = 1-HOP STAIRCASE-AFFECTS-A walk SECOND consecutive A-hop (the naive continuation ",
 f"{fmt(w252_a_tail + 1)}..{fmt(w252_a_tail + 2_000)} is REFUSED at its own start ",
 "-- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; ",
 "the registered W252 B band sits INSIDE the naive A window = staircase re-emergence continues to affect A; ",
 "the W252 prereg sec.5 item5 A-CLEAN-at-naive projection superseded live r587, divergence disclosed; the walk hops past the W252 B tail -> ",
 "A first-clean; A base == registered prior-wave B tail+1 (",
 f"{fmt(w252_b_tail)}+1) machine-checkable; SECOND consecutive A-hop of the staircase era, ",
 "the fourteen-wave seed-gap face ENDED at W252; non-rotational r587 forward-monotone walk) ",
 "+ B = 1-HOP own-A RESERVATION CASCADE above own-A ",
 "(the naive continuation ",
 f"{fmt(w252_b_tail + 1)}..{fmt(w252_b_tail + 200)} is REFUSED at its own start ",
 "-- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the ",
 f"naive window lands INSIDE the own-wave A first-clean window (own-A reservation cascade standard leg); the walk hops past the own-wave A tail -> B lands ABOVE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT; THIRD consecutive above-own-A ",
 "landing; B base == own-A tail+1 (",
 f"{fmt(a_hi)}+1) machine-checkable; cross-window convergence with the W252 prereg sec.5 item5 + W252 probe leg4 + seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W252 universe ",
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",
''',
'''
"wave 254: ",
 "A = 1-HOP STAIRCASE-AFFECTS-A walk THIRD consecutive A-hop (the naive continuation ",
 f"{fmt(w253_a_tail + 1)}..{fmt(w253_a_tail + 2_000)} is REFUSED at its own start ",
 "-- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; ",
 "the registered W253 B band sits INSIDE the naive A window = staircase re-emergence continues to affect A; ",
 "the W253 prereg sec.5 item5 A-CLEAN-at-naive projection superseded live r587, divergence disclosed; the walk hops past the W253 B tail -> ",
 "A first-clean; A base == registered prior-wave B tail+1 (",
 f"{fmt(w253_b_tail)}+1) machine-checkable; THIRD consecutive A-hop of the staircase era, ",
 "the fourteen-wave seed-gap face ENDED at W252; non-rotational r587 forward-monotone walk) ",
 "+ B = 1-HOP own-A RESERVATION CASCADE above own-A ",
 "(the naive continuation ",
 f"{fmt(w253_b_tail + 1)}..{fmt(w253_b_tail + 200)} is REFUSED at its own start ",
 "-- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the ",
 f"naive window lands INSIDE the own-wave A first-clean window (own-A reservation cascade standard leg); the walk hops past the own-wave A tail -> B lands ABOVE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT; FOURTH consecutive above-own-A ",
 "landing; B base == own-A tail+1 (",
 f"{fmt(a_hi)}+1) machine-checkable; cross-window convergence with the W253 prereg sec.5 item5 + W253 probe leg4 + seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W253 universe ",
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",
''', "P5e-pre")

# MEM_I comment lines (A + B faces)
rep(""" f'{MEM_I}\"a_seed_base\": {a_lo},        # law sec.4 W254 A: {fmt(a_lo)}..{fmt(a_hi)} (1-HOP STAIRCASE-AFFECTS-A walk SECOND consecutive A-hop; naive {fmt(w253_a_tail + 1)}..{fmt(w253_a_tail + 2_000)} REFUSED at start -- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; registered W253 B band inside the naive A window; second consecutive A-hop of the staircase era -- seed-gap face ENDED at W253; A base == registered prior-wave B tail+1)',""",
    """ f'{MEM_I}\"a_seed_base\": {a_lo},        # law sec.4 W254 A: {fmt(a_lo)}..{fmt(a_hi)} (1-HOP STAIRCASE-AFFECTS-A walk THIRD consecutive A-hop; naive {fmt(w253_a_tail + 1)}..{fmt(w253_a_tail + 2_000)} REFUSED at start -- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; registered W253 B band inside the naive A window; third consecutive A-hop of the staircase era -- seed-gap face ENDED at W252; A base == registered prior-wave B tail+1)',""",
    1, "P5e-mem-a")
rep(""" f'{MEM_I}\"b_exit_seed_base\": {b_lo},   # law sec.4 W254 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION CASCADE above own-A; naive {fmt(w253_b_tail + 1)}..{fmt(w253_b_tail + 200)} REFUSED at start -- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; naive window lands inside the own-wave A first-clean window -> own-A reservation cascade; B lands ABOVE own-A at tail+1 EXACT -- third consecutive above-own-A; B base == own-A tail+1)',""",
    """ f'{MEM_I}\"b_exit_seed_base\": {b_lo},   # law sec.4 W254 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION CASCADE above own-A; naive {fmt(w253_b_tail + 1)}..{fmt(w253_b_tail + 200)} REFUSED at start -- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; naive window lands inside the own-wave A first-clean window -> own-A reservation cascade; B lands ABOVE own-A at tail+1 EXACT -- fourth consecutive above-own-A; B base == own-A tail+1)',""",
    1, "P5e-mem-b")

# tail band-facts comments (A + B lines)
chunk('''
"        # band facts (law sec.4 W253 row): A = 1-HOP STAIRCASE-AFFECTS-A",
"        # walk SECOND consecutive A-hop (the naive continuation",
f"        # {fmt(w252_a_tail + 1)}..{fmt(w252_a_tail + 2_000)} REFUSED at naive start -- the registered W252 B band",
f"        # {fmt(pf_mod.N1_BANDS[252]['b_exit'][0])}..{fmt(pf_mod.N1_BANDS[252]['b_exit'][1])} sits INSIDE the naive A window (staircase re-emergence",
"        # continues to affect A; the W252 prereg sec.5 item5 A-CLEAN-at-naive projection superseded live r587,",
"        # divergence disclosed); hops=1, A_hop_chain verbatim in the probe receipt,",
"        # A_clean_at_naive_start=false, A_staircase_hop_past_W252_B=true; the walk hops",
"        # past the W252 B tail -> A first-clean; A base ==",
f"        # registered prior-wave B tail+1 ({fmt(w252_b_tail)}+1) machine-checkable; SECOND consecutive A-hop of the W239",
"        # staircase era -- the fourteen-wave seed-gap face ENDED at W252;",
"        # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation",
f"        # {fmt(w252_b_tail + 1)}..{fmt(w252_b_tail + 200)} REFUSED at naive start -- the naive window lands",
"        # INSIDE the own-wave A first-clean window (own-A reservation cascade standard leg); hops=1,",
"        # B_hop_chain verbatim in the probe receipt; the walk hops past the own-wave A tail",
f"        # -> B lands ABOVE the own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT -- THIRD consecutive",
"        # above-own-A landing;",
"        # B base == own-A tail+1 EXACT",
"        # machine-checkable; B_hop_lands_inside_A=false;",
"        # B_lands_above_own_A=true; cross-window convergence with",
"        # the W252 prereg sec.5 item5 + W252 probe leg4 + seat leg4 succession projection notes -- all",
"        # MANDATORY notes honored (post-W252 universe",
"        # re-derive + live-trace re-read, no staircase-equality assumption);",
''',
'''
"        # band facts (law sec.4 W254 row): A = 1-HOP STAIRCASE-AFFECTS-A",
"        # walk THIRD consecutive A-hop (the naive continuation",
f"        # {fmt(w253_a_tail + 1)}..{fmt(w253_a_tail + 2_000)} REFUSED at naive start -- the registered W253 B band",
f"        # {fmt(pf_mod.N1_BANDS[253]['b_exit'][0])}..{fmt(pf_mod.N1_BANDS[253]['b_exit'][1])} sits INSIDE the naive A window (staircase re-emergence",
"        # continues to affect A; the W253 prereg sec.5 item5 A-CLEAN-at-naive projection superseded live r587,",
"        # divergence disclosed); hops=1, A_hop_chain verbatim in the probe receipt,",
"        # A_clean_at_naive_start=false, A_staircase_hop_past_W253_B=true; the walk hops",
"        # past the W253 B tail -> A first-clean; A base ==",
f"        # registered prior-wave B tail+1 ({fmt(w253_b_tail)}+1) machine-checkable; THIRD consecutive A-hop of the W239",
"        # staircase era -- the fourteen-wave seed-gap face ENDED at W252;",
"        # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation",
f"        # {fmt(w253_b_tail + 1)}..{fmt(w253_b_tail + 200)} REFUSED at naive start -- the naive window lands",
"        # INSIDE the own-wave A first-clean window (own-A reservation cascade standard leg); hops=1,",
"        # B_hop_chain verbatim in the probe receipt; the walk hops past the own-wave A tail",
f"        # -> B lands ABOVE the own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT -- FOURTH consecutive",
"        # above-own-A landing;",
"        # B base == own-A tail+1 EXACT",
"        # machine-checkable; B_hop_lands_inside_A=false;",
"        # B_lands_above_own_A=true; cross-window convergence with",
"        # the W253 prereg sec.5 item5 + W253 probe leg4 + seat leg4 succession projection notes -- all",
"        # MANDATORY notes honored (post-W253 universe",
"        # re-derive + live-trace re-read, no staircase-equality assumption);",
''', "P5e-tailcmt")

# tail assert block (A face message)
rep('            "W254 A staircase-affects-A walk SECOND consecutive A-hop: the naive "\',\n\'            "continuation is REFUSED at its own start (the registered W253 B band sits INSIDE "\',\n\'            "the naive A window -- staircase re-emergence continues; hops=1, A_hop_chain verbatim in the probe receipt, "\',\n\'            "A_clean_at_naive_start=false, A_staircase_hop_past_W253_B=true; the walk hops past "\',\n\'            "the W253 B tail -> A first-clean -- SECOND consecutive A-hop of the staircase era, "\',\n\'            "the fourteen-wave seed-gap face ENDED at W253; A base == registered prior-wave B "\',\n\'            "tail+1 machine-checkable, floor relation honored)"',
    '            "W254 A staircase-affects-A walk THIRD consecutive A-hop: the naive "\',\n\'            "continuation is REFUSED at its own start (the registered W253 B band sits INSIDE "\',\n\'            "the naive A window -- staircase re-emergence continues; hops=1, A_hop_chain verbatim in the probe receipt, "\',\n\'            "A_clean_at_naive_start=false, A_staircase_hop_past_W253_B=true; the walk hops past "\',\n\'            "the W253 B tail -> A first-clean -- THIRD consecutive A-hop of the staircase era, "\',\n\'            "the fourteen-wave seed-gap face ENDED at W252; A base == registered prior-wave B "\',\n\'            "tail+1 machine-checkable, floor relation honored)"', 1, "P5e-tail-amsg")

# tail assert block (B face messages)
rep("'            \"W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation \"'",
    "'            \"W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation \"'", 1, "P5e-tail-bassert2")
rep("'            \"W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)\"'",
    "'            \"W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)\"'", 1, "P5e-tail-bclean")
rep("'            \"W254 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- third consecutive above-own-A; zero overlap)\"'",
    "'            \"W254 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- fourth consecutive above-own-A; zero overlap)\"'", 1, "P5e-tail-excl")

# pr print A/B lines
chunk(''' '          "A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, "',
 '          "registered W252 B band inside the naive A window, SECOND consecutive A-hop of the staircase era, "',
 '          "the fourteen-wave seed-gap face ENDED at W252) "',
 '          "+ B=1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, "',
 '          "B_hop_chain verbatim, naive window lands inside the own-wave A window -> own-A reservation cascade, "',
 '          "B base == own-A tail+1 EXACT, B_lands_above_own_A=true, "',
 '          "THIRD consecutive above-own-A landing), chain-order splice from the "''',
''' '          "A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, "',
 '          "registered W253 B band inside the naive A window, THIRD consecutive A-hop of the staircase era, "',
 '          "the fourteen-wave seed-gap face ENDED at W252) "',
 '          "+ B=1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, "',
 '          "B_hop_chain verbatim, naive window lands inside the own-wave A window -> own-A reservation cascade, "',
 '          "B base == own-A tail+1 EXACT, B_lands_above_own_A=true, "',
 '          "FOURTH consecutive above-own-A landing), chain-order splice from the "''', "P5e-pr")

# receipt band_semantics A + B values
rep('"A": "1-HOP STAIRCASE-AFFECTS-A walk SECOND consecutive A-hop (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 571_701..573_700 refused at start -- the registered W253 B band 571_701..571_900 sits INSIDE the naive A window (staircase re-emergence continues; the W253 prereg sec.5 item5 A-CLEAN-at-naive projection superseded live r587, divergence disclosed); the walk hops past the W253 B tail 571_900 -> A first-clean 571_901..573_900 -- SECOND consecutive A-hop of the staircase era, the fourteen-wave seed-gap face ENDED at W253; A_clean_at_naive_start=false; A_staircase_hop_past_W253_B=true; A base == registered prior-wave B tail+1 (571_900+1) EXACT)"',
    '"A": "1-HOP STAIRCASE-AFFECTS-A walk THIRD consecutive A-hop (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 573_901..575_900 refused at start -- the registered W253 B band 573_901..574_100 sits INSIDE the naive A window (staircase re-emergence continues; the W253 prereg sec.5 item5 A-CLEAN-at-naive projection superseded live r587, divergence disclosed); the walk hops past the W253 B tail 574_100 -> A first-clean 574_101..576_100 -- THIRD consecutive A-hop of the staircase era, the fourteen-wave seed-gap face ENDED at W252; A_clean_at_naive_start=false; A_staircase_hop_past_W253_B=true; A base == registered prior-wave B tail+1 (574_100+1) EXACT)"', 1, "P5e-rcpt-semantics-A")
rep('"B": "1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the naive continuation 571_901..572_100 is refused at start -- the naive window lands INSIDE the own-wave W254 A first-clean window 571_901..573_900 (own-A reservation cascade standard leg; the W253 prereg sec.5 item5 + probe leg4 projected landing superseded live -- the A face itself moved, divergence disclosed per r587); the walk hops past the own-A tail 573_900 -> B landing 573_901..574_100; B lands ABOVE own-A -- THIRD consecutive above-own-A landing; B_lands_above_own_A=true; B_hop_lands_inside_A=false; B base == own-A tail+1 (573_900+1) EXACT)"',
    '"B": "1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the naive continuation 574_101..574_300 is refused at start -- the naive window lands INSIDE the own-wave W254 A first-clean window 574_101..576_100 (own-A reservation cascade standard leg; the W253 prereg sec.5 item5 + probe leg4 projected landing superseded live -- the A face itself moved, divergence disclosed per r587); the walk hops past the own-A tail 576_100 -> B landing 576_101..576_300; B lands ABOVE own-A -- FOURTH consecutive above-own-A landing; B_lands_above_own_A=true; B_hop_lands_inside_A=false; B base == own-A tail+1 (576_100+1) EXACT)"', 1, "P5e-rcpt-semantics-B")

# downstream W255+ projection face (probe leg4 verbatim numbers)


with io.open(r"results/_r1055bmc_staged3_t.txt", "w", encoding="utf-8", newline="") as f:
    f.write(t)
k = t.find("p face per this window's probe leg4")
print("anchor at", k)
print(t[k - 20:k + 1100])
print("STAGE3 OK")
