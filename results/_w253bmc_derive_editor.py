# -*- coding: utf-8 -*-
# r1053 bm-c: derive results/_w253bmc_freeze_edits.py from the committed W252
# freeze-edits script (results/_w252bmc_freeze_edits.py, proven live-fire W252
# splice bm-c r1050 window: splice e63561df3 + engine self-burn 12/12 +
# finalize one-pass ledger 978,735 / K=552,320 five-key ALL PASS by the r1050
# continuation closeout f6433ee61) via COUNT-ASSERTED ORDERED TRANSFORM (E63
# lineage, 5th-gen pass ordering: P1 structural outputs BLANKET-IMMUNE; the
# W253 extraction faces stay structurally identical to the W252 estate
# mandate -- estate 69 rows W138..W206 full-span ONLY + kept W211..W238 (28)
# + dropped W239..W251 (13) + fresh W239..W252 (14) = 111 parity rows per the
# frozen W253 prereg sec.3 mandate -- only the count faces move 13->14 /
# 110->111 / 40->41 / 12->13).
# W253 facts (machine-read from the probe receipt, never transcribed):
# bands A 571_901..573_900 (1-HOP STAIRCASE-AFFECTS-A walk, SECOND
# consecutive A-hop -- the naive continuation 571_701..573_700 is REFUSED at
# its own start: the registered W252 B band 571_701..571_900 sits INSIDE the
# naive A window = staircase CONTINUES to affect A; the W252 prereg sec.5
# item5 A-CLEAN-at-naive projection was a pre-W252-universe face, superseded
# live per r587, divergence disclosed; the walk hops past the W252 B tail
# 571_900 -> A first-clean 571_901..573_900, hops=1; A base == registered
# prior-wave B tail+1 (571_900+1) EXACT) / B 573_901..574_100 (1-HOP own-A
# RESERVATION CASCADE above own-A, THIRD consecutive -- the naive
# continuation 571_901..572_100 is REFUSED at its own start: the naive
# window lands INSIDE the own-wave W253 A first-clean window
# 571_901..573_900, own-A reservation cascade standard leg; the walk hops
# past the own-A tail 573_900 -> B landing 573_901..574_100, hops=1; B base
# == own-A tail+1 (573_900+1) EXACT), upstream W252 = bm-c own chain, seat
# MSG-20261016-12xx-bmc-w253-seat @ origin f6433ee61 r1050 closeout,
# prereg 741371846 derived bm-c r1052 (authored 13:2x).
import io, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w252bmc_freeze_edits.py")
DST = os.path.join(REPO, "results", "_w253bmc_freeze_edits.py")

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
    s = s.replace("W253", "W254")
    s = s.replace("252", "253")
    s = s.replace("251", "252")
    # P5a mappings (post-blanket forms)
    s = s.replace("MSG-20261016-10xx-bmc-w253-seat", "MSG-20261016-12xx-bmc-w253-seat")
    s = s.replace("r1048", "r1050")
    s = s.replace("r1049", "r1052")
    s = s.replace("976,535", "978,735")
    s = s.replace("550,120", "552,320")
    s = s.replace("SEVENTY-SECOND", "SEVENTY-THIRD")
    s = s.replace("TWO HUNDRED AND FIFTY-SECOND", "TWO HUNDRED AND FIFTY-THIRD")
    s = s.replace("fortieth consecutive", "forty-first consecutive")
    s = s.replace("bmc_ordinal=72", "bmc_ordinal=73")
    s = s.replace("authored 10:2x", "authored 13:2x")
    s = s.replace("f9441de67", "f6433ee61")
    s = s.replace("472cc8386", "741371846")
    return s

def chunk(src_text, dst_text, tag):
    global t
    needle = xf(src_text)
    n = t.count(needle)
    assert n == 1, f"[{tag}] chunk needle count {n} != 1 (needle head: {needle[:80]!r})"
    t = t.replace(needle, dst_text)
    log.append(f"{tag}: chunk 1x ({len(src_text)} -> {len(dst_text)} chars)")

# ============ P1: structural faces, BLANKET-IMMUNE outputs ============
rep("(248, 247, 246, 245, 244, 243, 242, 241, 240, 239)",
    "(249, 248, 247, 246, 245, 244, 243, 242, 241, 240)", 2, "P1-transitive-deps")
rep("range(209, 253)", "range(209, 254)", 2, "P1-liveness-range")
rep('def fmt(n):  # 569701 -> "569_701"', 'def fmt(n):  # 571901 -> "571_901"', 1, "P1-fmt-comment")

# ============ P2: downstream shift W253 -> W254 (incl. W253p_* receipt keys) ============
rep("W253", "W254", None, "P2-downstream")
assert "W253" not in t, "P2 leftover W253"

# ============ P3: self shift 252 -> 253 ============
n252 = t.count("252")
rep("252", "253", None, "P3-self")
log.append(f"P3 consumed {n252} '252' substrings")

# ============ P4: upstream shift 251 -> 252 ============
n251 = t.count("251")
rep("251", "252", None, "P4-upstream")
log.append(f"P4 consumed {n251} '251' substrings")

# ============ P5a: numeric/anchor/ordinal/window faces (post-blanket forms) ============
rep("976_535", "978_735", 1, "P5a-ledger-int")
rep("550_120", "552_320", 1, "P5a-k-int")
rep("976,535", "978,735", 8, "P5a-ledger-prose")
rep("550,120", "552,320", 8, "P5a-k-prose")
rep("bmc_ordinal=72", "bmc_ordinal=73", 7, "P5a-ordinal72")
rep("SEVENTY-SECOND", "SEVENTY-THIRD", 3, "P5a-seventysecond")
rep("TWO HUNDRED AND FIFTY-SECOND", "TWO HUNDRED AND FIFTY-THIRD", 3, "P5a-250th")
rep("fortieth consecutive", "forty-first consecutive", 2, "P5a-finface")
rep("72nd own wave", "73rd own wave", 3, "P5a-72nd-ownwave")
rep("MSG-20261016-10xx-bmc-w253-seat", "MSG-20261016-12xx-bmc-w253-seat", 7, "P5a-seat-msg")
rep("f9441de67", "f6433ee61", 2, "P5a-seat-origin")
rep("472cc8386", "741371846", 1, "P5a-prereg-commit")
# r-window faces: upstream W252 chain = splice r1050 window (dead 11:33-12:15
# estate, landed e63561df3) + finalize r1050 (closeout 12:2x f6433ee61);
# W253 prereg derive window = r1052 (authored 13:2x); this freeze = r1053.
rep("2026-10-16 11:0x bm-c r1050 freeze window", "2026-10-16 14:2x bm-c r1053 freeze window", 1, "P5a-header-window")
rep("W252 finalize one-pass bm-c r1048 window closeout 10:0x",
    "W252 finalize one-pass bm-c r1050 window closeout 12:2x", 1, "P5a-closeout-window")
rep("r1048 splice window", "r1050 splice window", 3, "P5a-splice-window")
rep("r1048", "r1050", 19, "P5a-splice-window-rest")
rep("r1049", "r1052", 7, "P5a-prereg-window")
rep("authored 10:2x", "authored 13:2x", 2, "P5a-authored-time")
# aging-face needle heals (same-window disclosed, r1045/r1047/r1050 precedent family):
rep("transitive window W239..W248 checked", "transitive window W240..W249 checked", 1, "P5a-aging-deps-cmt")
rep("engine_owner==bm-c rows 71 + candidate", "engine_owner==bm-c rows 72 + candidate", 1, "P5a-aging-rows71-heal")

# ============ P5b: extraction count faces (frozen W253 prereg sec.3 mandate) ============
# estate 69 (W138..W206) + kept W211..W238 (28) UNCHANGED; dropped W239..W251 (13);
# fresh W239..W252 (14); total parity 111 rows; legs segment W211..W251 (41).
rep("# block's own W239..W250 legs (12 rows) do NOT enter the estate path;",
    "# block's own W239..W251 legs (13 rows) do NOT enter the estate path;", 1, "P5b-hdr-ownlegs")
rep("# after extraction, fresh W239..W252 legs (13 rows) are added,",
    "# after extraction, fresh W239..W252 legs (14 rows) are added,", 1, "P5b-hdr-freshlegs")
rep("# parity = 110 rows (W138..W206 + W211..W252). Zero assumption zero risk.",
    "# parity = 111 rows (W138..W206 + W211..W252). Zero assumption zero risk.", 1, "P5b-hdr-parity-count")
rep("# block's own W239..W250 legs (12) are EXCLUDED from the estate path per the",
    "# block's own W239..W251 legs (13) are EXCLUDED from the estate path per the", 1, "P5b-ext-excl")
rep("# prereg mandate; the W253 block appends fresh W239..W252 legs (13,",
    "# prereg mandate; the W253 block appends fresh W239..W252 legs (14,", 1, "P5b-ext-fresh")
rep("# machine-derived from the LIVE pf registry at freeze time) -> 110 parity",
    "# machine-derived from the LIVE pf registry at freeze time) -> 111 parity", 1, "P5b-ext-parcount")
rep("assert par_full.count(\"assert pf.N1_BANDS[\") == 109, \\\n    f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 109 (69 estate + W211..W250 legs 40)\"",
    "assert par_full.count(\"assert pf.N1_BANDS[\") == 110, \\\n    f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 110 (69 estate + W211..W251 legs 41)\"", 1, "P5b-parfull")
rep("assert legs_sec.count(\"assert pf.N1_BANDS[\") == 40 \\\n    and [int(w) for w in _legs_ws] == list(range(211, 252)), \\\n    f\"legs segment not W211..W250 forty legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}\"",
    "assert legs_sec.count(\"assert pf.N1_BANDS[\") == 41 \\\n    and [int(w) for w in _legs_ws] == list(range(211, 252)), \\\n    f\"legs segment not W211..W251 forty-one legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}\"", 1, "P5b-legs-assert")
rep("# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W252\n# block's own W239..W250 legs (12) are excluded from the estate path",
    "# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W252\n# block's own W239..W251 legs (13) are excluded from the estate path", 1, "P5b-split-cmt")
rep("assert legs_dropped.count(\"assert pf.N1_BANDS[\") == 12 \\\n    and [int(w) for w in _dropped_ws] == list(range(239, 252)), \\\n    f\"dropped segment not W239..W250 twelve legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}\"",
    "assert legs_dropped.count(\"assert pf.N1_BANDS[\") == 13 \\\n    and [int(w) for w in _dropped_ws] == list(range(239, 252)), \\\n    f\"dropped segment not W239..W251 thirteen legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}\"", 1, "P5b-dropped-assert")
rep('"fresh_legs_row_asserts": 13,', '"fresh_legs_row_asserts": 14,', 1, "P5b-rcpt-fresh13")
rep("+ legs_kept.count(\"assert pf.N1_BANDS[\") + 13,",
    "+ legs_kept.count(\"assert pf.N1_BANDS[\") + 14,", 1, "P5b-rcpt-total13")
rep('"    #     physical bytes; the W252 block\'s own W239..W250 legs (12) are",',
    '"    #     physical bytes; the W252 block\'s own W239..W251 legs (13) are",', 1, "P5b-hdr-ownlegs-mat")
rep('"    #     W239..W252 legs (13) added, machine-derived from the live pf",',
    '"    #     W239..W252 legs (14) added, machine-derived from the live pf",', 1, "P5b-hdr-freshlegs-mat")
rep('"    #     registry at freeze time -> 110 parity rows (W138..W206+W211..W252).",',
    '"    #     registry at freeze time -> 111 parity rows (W138..W206+W211..W252).",', 1, "P5b-hdr-parcount-mat")

# receipt note (single big face: counts + generation stamp)
chunk('''                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W238 legs (28) extracted verbatim per the frozen W252 prereg sec.3 mandate; the W251 block's own W239..W250 legs (12) EXCLUDED from the estate path per the same mandate; fresh W239..W251 legs (13) machine-derived from the live pf registry -> W252 block = 110 rows (W138..W206 + W211..W251); disclosed: (a) inherited W213 leg error-string face preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-252 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 4th-gen prevention this window: the W252 derive editor reordered passes so P1 structural outputs are blanket-immune and the extraction-restructure legs/kept/dropped wave-identity asserts are fixed post-blanket (list(range(211,251))/list(range(211,239))/list(range(239,251)) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},''',
'''                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W238 legs (28) extracted verbatim per the frozen W253 prereg sec.3 mandate; the W252 block's own W239..W251 legs (13) EXCLUDED from the estate path per the same mandate; fresh W239..W252 legs (14) machine-derived from the live pf registry -> W253 block = 111 rows (W138..W206 + W211..W252); disclosed: (a) inherited W213 leg error-string face preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-253 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 5th-gen prevention this window: the W253 derive editor kept the P1-blanket-immune pass ordering and the extraction-restructure legs/kept/dropped wave-identity asserts fixed post-blanket (list(range(211,252))/list(range(211,239))/list(range(239,252)) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},''', "P5b-rcpt-note")

# ============ P5c: band literals (probe ADMIT receipt bands) ============
rep('assert (a_lo, a_hi) == (569_701, 571_700) and (b_lo, b_hi) == (571_701, 571_900), \\',
    'assert (a_lo, a_hi) == (571_901, 573_900) and (b_lo, b_hi) == (573_901, 574_100), \\', 1, "P5c-band-drift")

# ============ P5d: ordinal/leg0/deps faces ============
rep('assert len(owner_rows_live) == 241 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 71, \\',
    'assert len(owner_rows_live) == 242 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 72, \\', 1, "P5d-ord-gate")
rep("(expect 241/129/71 PRE-splice post-W252 registration; this candidate = bm-c's 73rd own wave per the same live-derive law, r587/r359)",
    "(expect 242/129/72 PRE-splice post-W252 registration; this candidate = bm-c's 73rd own wave per the same live-derive law, r587/r359)", 1, "P5d-ord-err")
rep('# receipt leg0 face owner_rows=241 / bmc_rows=71 / bmc_ordinal=73',
    '# receipt leg0 face owner_rows=242 / bmc_rows=72 / bmc_ordinal=73', 1, "P5d-leg0-prose")
rep("-> owner rows 241 + candidate = 242nd EXACT; bm-c rows 71 +",
    "-> owner rows 242 + candidate = 243rd EXACT; bm-c rows 72 +", 1, "P5d-ord-owner-prose")
rep("# candidate = 72nd EXACT -- bm-c own-seat continuity face (bm-c published the",
    "# candidate = 73rd EXACT -- bm-c own-seat continuity face (bm-c published the", 1, "P5d-ord-bmc-prose")
rep("freeze-time live face owner rows 241 + candidate = 242nd EXACT",
    "freeze-time live face owner rows 242 + candidate = 243rd EXACT", 1, "P5d-rcpt-242nd")
rep("freeze-time live derive bmc rows 71 + candidate 72nd EXACT per r587/r359",
    "freeze-time live derive bmc rows 72 + candidate 73rd EXACT per r587/r359", 1, "P5d-bundle-72nd")
rep("post-W252 registration: bm-c rows 71 + candidate = 72nd owned",
    "post-W252 registration: bm-c rows 72 + candidate = 73rd owned", 1, "P5d-rcpt-72nd-owned")
rep('"probe_receipt_bmc_ordinal_face": 72,', '"probe_receipt_bmc_ordinal_face": 73,', 1, "P5d-rcpt-ordface")
rep('f"W252+W247..W238 finalize products present "', 'f"W252+W248..W239 finalize products present "', 1, "P5d-print-deps")

# ============ P5e: A/B face structural rewrites (staircase + cascade CONTINUE) ============
# header NEW FACE block
chunk('''# NEW FACE vs the W251 editor (honest disclosure, frozen W252 prereg sec.3
# mandate): BOTH bands take 1-HOP WALK faces -- A = STAIRCASE-AFFECTS-A
# 1-hop walk (the naive continuation 569_501..571_500 is REFUSED at its own
# start -- the registered W251 B band 569_501..569_700 sits INSIDE the naive
# A window = staircase re-emergence affects A too; the W251 prereg sec.5
# item5 A-CLEAN projection was a pre-W251-universe face, superseded live per
# r587, divergence disclosed; the walk hops past the W251 B tail 569_700 ->
# A first-clean 569_701..571_700, hops=1 -- FIRST A-HOP SINCE THE W239
# STAIRCASE ERA, the fourteen-wave seed-gap face ENDS at W252; A base ==
# registered prior-wave B tail+1 (569_700+1) floor relation EXACT this
# window; A_clean_at_naive_start=false; A_staircase_hop_past_W251_B=true);
# B = 1-HOP own-A RESERVATION above own-A (the naive continuation
# 569_701..569_900 is REFUSED at its own start -- the naive window lands
# INSIDE the own-wave A first-clean window 569_701..571_700, own-A
# reservation standard leg; the walk hops past the own-A tail 571_700 ->
# B landing 571_701..571_900, hops=1; B lands ABOVE own-A -- SECOND
# consecutive above-own-A landing; B base == own-A tail+1 (571_700+1) EXACT;
# B_naive_refused_at_start=true; B_lands_above_own_A=true;
# B_hop_lands_inside_A=false; hops=1).''',
'''# NEW FACE vs the W252 editor (honest disclosure, frozen W253 prereg sec.3
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
# B_hop_lands_inside_A=false; hops=1).''', "P5e-hdr")

# band facts comment block
chunk('''# W252 FACE (probe receipt leg1 relation_asserts):
# A takes the 1-HOP STAIRCASE-AFFECTS-A walk face (naive continuation
# REFUSED at its own start -- A_clean_at_naive_start=false,
# A_staircase_hop_past_W251_B=true, hops=1, A_hop_chain verbatim in the
# receipt; the registered W251 B band sits INSIDE the naive A window =
# staircase re-emergence affects A; the W251 prereg sec.5 item5 A-CLEAN
# projection superseded live r587, divergence disclosed; the walk hops past
# the W251 B tail -> A first-clean; A base == registered prior-wave B
# tail+1 EXACT -- FIRST A-hop since the W239 staircase era, the
# fourteen-wave seed-gap face ENDS at W252); B takes the 1-HOP own-A
# RESERVATION face (naive continuation REFUSED at its own start --
# B_naive_refused_at_start=true, hops=1, B_hop_chain verbatim in the
# receipt; the naive window lands INSIDE the own-wave A first-clean window,
# own-A reservation standard leg; the walk hops past the own-A tail -> B
# lands ABOVE own-A, B_lands_above_own_A=true -- B base == own-A tail+1
# EXACT, SECOND consecutive above-own-A landing); machine-derived from the
# LIVE registered row, never transcribed.''',
'''# W253 FACE (probe receipt leg1 relation_asserts):
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
# machine-derived from the LIVE registered row, never transcribed.''', "P5e-bandfacts")

# band-facts assert lines (A face)
rep('assert w252_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1 EXACT -- the 1-hop walk past the registered W252 B band; first A-hop since the W239 staircase era; A_staircase_hop_past_W252_B=true)"',
    'assert w252_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1 EXACT -- the 1-hop walk past the registered W252 B band; second consecutive A-hop of the staircase era; A_staircase_hop_past_W252_B=true)"', 1, "P5e-a-base")
rep('assert a_lo >= w252_b_tail + 1, "A staircase landing floor relation (A base >= registered prior-wave B tail+1; the fourteen-wave seed-gap face ENDS at W253 -- first A-hop since the W239 staircase era, A base == prior-B tail+1 EXACT this window per the prereg floor-relation mandate)"',
    'assert a_lo >= w252_b_tail + 1, "A staircase landing floor relation (A base >= registered prior-wave B tail+1; the fourteen-wave seed-gap face ENDED at W252 -- second consecutive A-hop of the staircase era, A base == prior-B tail+1 EXACT this window per the prereg floor-relation mandate)"', 1, "P5e-a-floor")
rep('assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation lands ABOVE own-A -- second consecutive above-own-A; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"',
    'assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation cascade lands ABOVE own-A -- third consecutive above-own-A; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"', 1, "P5e-b-base")

# relation_asserts gate (W251_W252 rsv-key fix -- the P4 blanket produces the
# W250_W252 hybrid face; the probe receipt leg1 keys are W251_W252)
rep('''ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") is False and ra.get("A_staircase_hop_past_W252_B") \\
    and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_clean_at_naive_start") is False and ra.get("B_base_above_W252_tail") \\
    and ra.get("AB_mutual_exclusion") and ra.get("B_hop_lands_inside_A") is False \\
    and ra.get("B_lands_above_own_A") and ra.get("W250_W252_bands_respected_A") and ra.get("W250_W252_bands_respected_B"), \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"''',
'''ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") is False and ra.get("A_staircase_hop_past_W252_B") \\
    and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_clean_at_naive_start") is False and ra.get("B_base_above_W252_tail") \\
    and ra.get("AB_mutual_exclusion") and ra.get("B_hop_lands_inside_A") is False \\
    and ra.get("B_lands_above_own_A") and ra.get("W251_W252_bands_respected_A") and ra.get("W251_W252_bands_respected_B"), \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"''', 1, "P5e-ra-gate")

# pf_comment A/B lines
chunk('''"    # band gate ADMIT results/_w252bmc_20261016_probe_receipt.json: A = 1-HOP",
"    # STAIRCASE-AFFECTS-A walk (the naive continuation " + fmt(w251_a_tail + 1) + ".." + fmt(w251_a_tail + 2_000) + " is REFUSED",
"    # at naive start -- the registered W251 B band sits INSIDE the naive A window;",
"    # the walk hops past the W251 B tail -> A first-clean, hops=1 -- FIRST A-hop",
"    # since the W239 staircase era, the fourteen-wave seed-gap face ENDS at W252;",
"    # A base == registered prior-wave B tail+1 (" + fmt(w251_b_tail) + "+1) machine-checkable; A_clean_at_naive_start=false;",
"    # A_staircase_hop_past_W251_B=true)",
"    # B = 1-HOP own-A RESERVATION above own-A (the naive continuation",
"    # " + fmt(w251_b_tail + 1) + ".." + fmt(w251_b_tail + 200) + " lands INSIDE the own-wave A first-clean window --",
"    # own-A reservation standard leg; hops=1,",
"    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A",
"    # tail -> B lands ABOVE own-A -- SECOND consecutive above-own-A;",
"    # B base == own-A tail+1 (" + fmt(a_hi) + "+1) EXACT; B_lands_above_own_A=true;",
"    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)",''',
'''"    # band gate ADMIT results/_w253bmc_20261016_probe_receipt.json: A = 1-HOP",
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
"    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)",''', "P5e-pfcmt")

# PRE block A/B lines
chunk(''' "wave 252: ",
 "A = 1-HOP STAIRCASE-AFFECTS-A walk (the naive continuation ",
 f"{fmt(w251_a_tail + 1)}..{fmt(w251_a_tail + 2_000)} is REFUSED at its own start ",
 "-- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; ",
 "the registered W251 B band sits INSIDE the naive A window = staircase re-emergence affects A; ",
 "the W251 prereg sec.5 item5 A-CLEAN projection superseded live r587, divergence disclosed; the walk hops past the W251 B tail -> ",
 "A first-clean; A base == registered prior-wave B tail+1 (",
 f"{fmt(w251_b_tail)}+1) machine-checkable; FIRST A-hop since the W239 staircase era, ",
 "the fourteen-wave seed-gap face ENDS at W252; non-rotational r587 forward-monotone walk) ",
 "+ B = 1-HOP own-A RESERVATION above own-A ",
 "(the naive continuation ",
 f"{fmt(w251_b_tail + 1)}..{fmt(w251_b_tail + 200)} is REFUSED at its own start ",
 "-- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the ",
 f"naive window lands INSIDE the own-wave A first-clean window (own-A reservation standard leg); the walk hops past the own-wave A tail -> B lands ABOVE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT; SECOND consecutive above-own-A ",
 "landing; B base == own-A tail+1 (",
 f"{fmt(a_hi)}+1) machine-checkable; cross-window convergence with the W251 prereg sec.5 item5 + W251 probe leg4 + seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W251 universe ",
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",''',
''' "wave 253: ",
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
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",''', "P5e-pre")

# MEM_I comment lines (A + B faces)
rep(""" f'{MEM_I}\"a_seed_base\": {a_lo},        # law sec.4 W253 A: {fmt(a_lo)}..{fmt(a_hi)} (1-HOP STAIRCASE-AFFECTS-A walk; naive {fmt(w252_a_tail + 1)}..{fmt(w252_a_tail + 2_000)} REFUSED at start -- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; registered W252 B band inside the naive A window; A first-hop since the W239 staircase era -- seed-gap face ENDS at W253; A base == registered prior-wave B tail+1)',""",
    """ f'{MEM_I}\"a_seed_base\": {a_lo},        # law sec.4 W253 A: {fmt(a_lo)}..{fmt(a_hi)} (1-HOP STAIRCASE-AFFECTS-A walk SECOND consecutive A-hop; naive {fmt(w252_a_tail + 1)}..{fmt(w252_a_tail + 2_000)} REFUSED at start -- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; registered W252 B band inside the naive A window; second consecutive A-hop of the staircase era -- seed-gap face ENDED at W252; A base == registered prior-wave B tail+1)',""",
    1, "P5e-mem-a")
rep(""" f'{MEM_I}\"b_exit_seed_base\": {b_lo},   # law sec.4 W253 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION above own-A; naive {fmt(w252_b_tail + 1)}..{fmt(w252_b_tail + 200)} REFUSED at start -- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; naive window lands inside the own-wave A first-clean window -> own-A reservation; B lands ABOVE own-A at tail+1 EXACT -- second consecutive above-own-A; B base == own-A tail+1)',""",
    """ f'{MEM_I}\"b_exit_seed_base\": {b_lo},   # law sec.4 W253 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION CASCADE above own-A; naive {fmt(w252_b_tail + 1)}..{fmt(w252_b_tail + 200)} REFUSED at start -- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; naive window lands inside the own-wave A first-clean window -> own-A reservation cascade; B lands ABOVE own-A at tail+1 EXACT -- third consecutive above-own-A; B base == own-A tail+1)',""",
    1, "P5e-mem-b")

# tail band-facts comments (A + B lines)
chunk('''"        # band facts (law sec.4 W252 row): A = 1-HOP STAIRCASE-AFFECTS-A",
"        # walk (the naive continuation",
f"        # {fmt(w251_a_tail + 1)}..{fmt(w251_a_tail + 2_000)} REFUSED at naive start -- the registered W251 B band",
f"        # {fmt(pf_mod.N1_BANDS[251]['b_exit'][0])}..{fmt(pf_mod.N1_BANDS[251]['b_exit'][1])} sits INSIDE the naive A window (staircase re-emergence",
"        # affects A; the W251 prereg sec.5 item5 A-CLEAN projection superseded live r587,",
"        # divergence disclosed); hops=1, A_hop_chain verbatim in the probe receipt,",
"        # A_clean_at_naive_start=false, A_staircase_hop_past_W251_B=true; the walk hops",
"        # past the W251 B tail -> A first-clean; A base ==",
f"        # registered prior-wave B tail+1 ({fmt(w251_b_tail)}+1) machine-checkable; FIRST A-hop since the W239",
"        # staircase era -- the fourteen-wave seed-gap face ENDS at W252;",
"        # B = 1-HOP own-A RESERVATION above own-A (the naive continuation",
f"        # {fmt(w251_b_tail + 1)}..{fmt(w251_b_tail + 200)} REFUSED at naive start -- the naive window lands",
"        # INSIDE the own-wave A first-clean window (own-A reservation standard leg); hops=1,",
"        # B_hop_chain verbatim in the probe receipt; the walk hops past the own-wave A tail",
f"        # -> B lands ABOVE the own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT -- SECOND consecutive",
"        # above-own-A landing;",
"        # B base == own-A tail+1 EXACT",
"        # machine-checkable; B_hop_lands_inside_A=false;",
"        # B_lands_above_own_A=true; cross-window convergence with",
"        # the W251 prereg sec.5 item5 + W251 probe leg4 + seat leg4 succession projection notes -- all",
"        # MANDATORY notes honored (post-W251 universe",
"        # re-derive + live-trace re-read, no staircase-equality assumption);",''',
'''"        # band facts (law sec.4 W253 row): A = 1-HOP STAIRCASE-AFFECTS-A",
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
"        # re-derive + live-trace re-read, no staircase-equality assumption);",''', "P5e-tailcmt")

# tail assert block (A face message)
rep('            "W253 A staircase-affects-A walk: the naive continuation is REFUSED at "\',\n\'            "its own start (the registered W252 B band sits INSIDE the naive A window -- "\',\n\'            "staircase re-emergence affects A; hops=1, A_hop_chain verbatim in the probe receipt, "\',\n\'            "A_clean_at_naive_start=false, A_staircase_hop_past_W252_B=true; the walk hops past "\',\n\'            "the W252 B tail -> A first-clean -- FIRST A-hop since the W239 staircase era, "\',\n\'            "the fourteen-wave seed-gap face ENDS at W253; A base == registered prior-wave B "\',\n\'            "tail+1 machine-checkable, floor relation honored)"',
    '            "W253 A staircase-affects-A walk SECOND consecutive A-hop: the naive "\',\n\'            "continuation is REFUSED at its own start (the registered W252 B band sits INSIDE "\',\n\'            "the naive A window -- staircase re-emergence continues; hops=1, A_hop_chain verbatim in the probe receipt, "\',\n\'            "A_clean_at_naive_start=false, A_staircase_hop_past_W252_B=true; the walk hops past "\',\n\'            "the W252 B tail -> A first-clean -- SECOND consecutive A-hop of the staircase era, "\',\n\'            "the fourteen-wave seed-gap face ENDED at W252; A base == registered prior-wave B "\',\n\'            "tail+1 machine-checkable, floor relation honored)"', 1, "P5e-tail-amsg")

# tail assert block (B face messages)
rep("'            \"W253 B 1-HOP own-A RESERVATION face: the naive continuation \"'",
    "'            \"W253 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation \"'", 1, "P5e-tail-bassert2")
rep("'            \"W253 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation landing)\"'",
    "'            \"W253 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)\"'", 1, "P5e-tail-bclean")
rep("'            \"W253 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- second consecutive above-own-A; zero overlap)\"'",
    "'            \"W253 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- third consecutive above-own-A; zero overlap)\"'", 1, "P5e-tail-excl")

# pr print A/B lines
chunk(''' '          "A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, "',
 '          "registered W251 B band inside the naive A window, FIRST A-hop since the W239 staircase era, "',
 '          "the fourteen-wave seed-gap face ENDS at W252) "',
 '          "+ B=1-HOP own-A RESERVATION above own-A (hops=1, B_naive_refused_at_start=true, "',
 '          "B_hop_chain verbatim, naive window lands inside the own-wave A window -> own-A reservation, "',
 '          "B base == own-A tail+1 EXACT, B_lands_above_own_A=true, "',
 '          "SECOND consecutive above-own-A landing), chain-order splice from the "''',
''' '          "A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, "',
 '          "registered W252 B band inside the naive A window, SECOND consecutive A-hop of the staircase era, "',
 '          "the fourteen-wave seed-gap face ENDED at W252) "',
 '          "+ B=1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, "',
 '          "B_hop_chain verbatim, naive window lands inside the own-wave A window -> own-A reservation cascade, "',
 '          "B base == own-A tail+1 EXACT, B_lands_above_own_A=true, "',
 '          "THIRD consecutive above-own-A landing), chain-order splice from the "''', "P5e-pr")

# receipt band_semantics A + B values
rep('"A": "1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 569_501..571_500 refused at start -- the registered W252 B band 569_501..569_700 sits INSIDE the naive A window (staircase re-emergence affects A; the W252 prereg sec.5 item5 A-CLEAN projection superseded live r587, divergence disclosed); the walk hops past the W252 B tail 569_700 -> A first-clean 569_701..571_700 -- FIRST A-hop since the W239 staircase era, the fourteen-wave seed-gap face ENDS at W253; A_clean_at_naive_start=false; A_staircase_hop_past_W252_B=true; A base == registered prior-wave B tail+1 (569_700+1) EXACT)"',
    '"A": "1-HOP STAIRCASE-AFFECTS-A walk SECOND consecutive A-hop (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 571_701..573_700 refused at start -- the registered W252 B band 571_701..571_900 sits INSIDE the naive A window (staircase re-emergence continues; the W252 prereg sec.5 item5 A-CLEAN-at-naive projection superseded live r587, divergence disclosed); the walk hops past the W252 B tail 571_900 -> A first-clean 571_901..573_900 -- SECOND consecutive A-hop of the staircase era, the fourteen-wave seed-gap face ENDED at W252; A_clean_at_naive_start=false; A_staircase_hop_past_W252_B=true; A base == registered prior-wave B tail+1 (571_900+1) EXACT)"', 1, "P5e-rcpt-semantics-A")
rep('"B": "1-HOP own-A RESERVATION above own-A (hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the naive continuation 569_701..569_900 is refused at start -- the naive window lands INSIDE the own-wave W253 A first-clean window 569_701..571_700 (own-A reservation standard leg; the W252 prereg sec.5 item5 projected landing ~571_501..571_700 superseded live -- the A face itself moved, divergence disclosed per r587); the walk hops past the own-A tail 571_700 -> B landing 571_701..571_900; B lands ABOVE own-A -- SECOND consecutive above-own-A landing; B_lands_above_own_A=true; B_hop_lands_inside_A=false; B base == own-A tail+1 (571_700+1) EXACT)"',
    '"B": "1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the naive continuation 571_901..572_100 is refused at start -- the naive window lands INSIDE the own-wave W253 A first-clean window 571_901..573_900 (own-A reservation cascade standard leg; the W252 prereg sec.5 item5 + probe leg4 projected landing superseded live -- the A face itself moved, divergence disclosed per r587); the walk hops past the own-A tail 573_900 -> B landing 573_901..574_100; B lands ABOVE own-A -- THIRD consecutive above-own-A landing; B_lands_above_own_A=true; B_hop_lands_inside_A=false; B base == own-A tail+1 (573_900+1) EXACT)"', 1, "P5e-rcpt-semantics-B")

# downstream W254+ projection face (probe leg4 verbatim numbers)
rep("W254p face per this window's probe leg4 (pre-W253 universe): A naive 571701..573700 CLEAN (hops=0, zero live refusers) / B naive 571901..572100 hops=0 CLEAN at naive, first-clean 571901..572100 BUT lands INSIDE the W254 projection A window (W254p_B_lands_inside_W254p_A_naive=true staircase face continuation: on the post-W253 universe the W254 naive A window start is REFUSED by the registered W253 B band -- staircase affects A inherited, the A first-clean and the B own-A reservation landing both move up, live re-derive governs); re-read the live trace at W254 derive time, do NOT assume the staircase A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities",
    "W254p face per this window's probe leg4 (pre-W253 universe): A naive 573901..575900 CLEAN (hops=0, zero live refusers -- pre-W253-universe face) / B naive 574101..574300 hops=0 CLEAN at naive, first-clean 574101..574300 BUT lands INSIDE the W254 projection A window (W254p_B_lands_inside_W254p_A_naive=true staircase face continuation since W251: A hops over prior B, B lands above own-A; on the post-W253 universe the W254 naive A window start 573_901 lands INSIDE the registered W253 B band 573_901..574_100 -- staircase affects A inherited, the A first-clean and the B own-A reservation cascade landing both move up, live re-derive governs); re-read the live trace at W254 derive time, do NOT assume the staircase A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities", 1, "P5e-rcpt-downstream")

# ============ structural output gates ============
for needle, want in [
    ("# --- W253 materializer face", 2),
    ("# --- W252 materializer face", 1),
    ('"+ W253 materializer face', 2),
    ("range(16, 253)", 2),
    ("range(17, 253)", 3),
    ("range(239, 253)", 2),
    ("list(range(211, 252))", 1),
    ("list(range(211, 239))", 1),
    ("list(range(239, 252))", 1),
    ("range(209, 254)", 2),
    ("if w < 253)", 5),
    ("if w < 252)", 1),
    ("_w253bmc_20261016_probe_receipt.json", 10),
    ("_w253bmc_freeze_receipt.json", 1),
    ("MSG-20261016-12xx-bmc-w253-seat", 7),
    ("f6433ee61", 2),
    ("978_735", 1),
    ("552_320", 1),
    ("(571_901, 573_900)", 1),
    ("(573_901, 574_100)", 1),
    ("W251_W252_bands_respected_A", 1),
    ("W251_W252_bands_respected_B", 1),
    ("B_base_above_W252_tail", 2),
    ("A_staircase_hop_past_W252_B", None),
    ("W254p_A_naive", 5),
    ("W254p_B_first_clean", 2),
    ("arith_a253", 6),
    ("arith_b253", 6),
    ('"PERPETUAL-N1-W253-SHARD-0"', 1),
    ("n1_w253_results.json", 2),
    ("n1_w253", 4),
    ("n1w253", 2),
    ("PERPETUAL-N1-W253", 7),
    ("_w253bmc", 11),
    ("w244_a", 12),
    ("SEVENTY-THIRD", 3),
    ("TWO HUNDRED AND FIFTY-THIRD", 3),
    ("forty-first consecutive", 2),
    ("bmc_ordinal=73", 7),
    ("73rd own wave", 3),
    ("r1050 splice window", 3),
    ("r1050", 23),
    ("r1052", 7),
    ("r1053 freeze window", 1),
    ("estate 69", 1),
    ("= 111 rows", 2),
    ("111 parity", 2),
    ("hops=1", None),
    ("1-HOP", None),
    ("SECOND consecutive A-hop", None),
    ("THIRD consecutive above-own-A", None),
    # anti-gates: stale faces must be zero
    ("r1048", 0),
    ("r1049", 0),
    ("472cc8386", 0),
    ("f9441de67", 0),
    ("976,535", 0),
    ("550,120", 0),
    ("976_535", 0),
    ("550_120", 0),
    ("SEVENTY-SECOND", 0),
    ("TWO HUNDRED AND FIFTY-SECOND", 0),
    ("fortieth consecutive", 0),
    ("MSG-20261016-10xx", 0),
    ("authored 10:2x", 0),
    ("bmc_ordinal=72", 0),
    ("72nd own wave", 0),
    ("242nd", 0),
    ("241/129/71", 0),
    ("SECOND consecutive above-own-A", 0),
    ("FIRST A-hop", 0),
    ("seed-gap face ENDS", 0),
    ("569_501..571_500", 0),
    ("569_501..569_700", 0),
    ("569_701..569_900", 0),
    ("569_701..571_700", 0),
    ("~571_501..571_700", 0),
    ("(569_701, 571_700)", 0),
    ("(571_701, 571_900)", 0),
    ("== 109", 0),
    ("forty legs", 0),
    ("twelve legs", 0),
    ("109 parity", 0),
    ("m234", 0),
    ("list(range(234, 251))", 0),
]:
    n = t.count(needle)
    if want is not None:
        assert n == want, f"OUTPUT-GATE {needle!r}: {n} != {want}"
    log.append(f"OUT {needle!r} = {n}")

io.open(DST, "w", encoding="utf-8", newline="").write(t)
import py_compile
py_compile.compile(DST, doraise=True)
io.open(os.path.join(REPO, "results", "_w253bmc_derive_editor_log.txt"), "w",
        encoding="utf-8").write("\n".join(log))
print(f"DERIVE OK -> {DST} ({len(t)} chars); {len(log)} transform log rows")
print("\n".join(log[-12:]))
