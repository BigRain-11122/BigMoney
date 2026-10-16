# -*- coding: utf-8 -*-
# r1050 bm-c: derive results/_w252bmc_freeze_edits.py from the committed W251
# editor (results/_w251bmc_freeze_edits.py, proven live-fire W251 splice bm-c
# r1048 window: splice c813471cd by the dead r1048-predecessor + finalize
# one-pass by the r1048 continuation, ledger 976,535 / K=550,120 five-key
# ALL PASS) via COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage, 4th-gen pass
# ordering: P1 structural outputs BLANKET-IMMUNE, wave-identity asserts fixed
# post-blanket in P5b; the W252 extraction RESTRUCTURE -- estate 69 rows
# W138..W206 full-span ONLY + kept W211..W238 (28) + fresh W239..W251 (13)
# = 110 parity rows per the frozen W252 prereg sec.3 mandate -- is executed
# as post-blanket chunk rewrites, zero hand-transcription of blanket faces).
# W252 facts (machine-read, never transcribed): bands A 569_701..571_700
# (1-HOP STAIRCASE-AFFECTS-A walk -- naive 569_501..571_500 REFUSED at the
# registered W251 B band 569_501..569_700, A first-hop since the W239
# staircase era, the fourteen-wave seed-gap face ENDS at W252, A base ==
# registered prior-wave B tail+1 (569_700+1) EXACT) / B 571_701..571_900
# (1-HOP own-A RESERVATION above own-A -- naive 569_701..569_900 lands
# INSIDE the own-wave A first-clean window, second consecutive
# above-own-A, B base == own-A tail+1 (571_700+1) EXACT), upstream W251 =
# bm-c own chain, seat MSG-20261016-10xx-bmc-w252-seat @ origin f9441de67
# r1048, prereg 472cc8386 derived bm-c r1049, parity estate 69 (W138..W206
# full-span, r858 absorb generation) + kept W211..W238 (28) + dropped
# W239..W250 (12) + fresh W239..W251 (13) = 110 rows.
import io, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w251bmc_freeze_edits.py")
DST = os.path.join(REPO, "results", "_w252bmc_freeze_edits.py")

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
    s = s.replace("W252", "W253")
    s = s.replace("251", "252")
    s = s.replace("250", "251")
    # P5a mappings (post-blanket forms)
    s = s.replace("MSG-20261016-085x-bmc-w252-seat", "MSG-20261016-10xx-bmc-w252-seat")
    s = s.replace("r1046", "r1048")
    s = s.replace("r1047", "r1049")
    s = s.replace("974,335", "976,535")
    s = s.replace("547,920", "550,120")
    s = s.replace("SEVENTY-FIRST", "SEVENTY-SECOND")
    s = s.replace("TWO HUNDRED AND FIFTY-FIRST", "TWO HUNDRED AND FIFTY-SECOND")
    s = s.replace("thirty-ninth consecutive", "fortieth consecutive")
    s = s.replace("bmc_ordinal=71", "bmc_ordinal=72")
    s = s.replace("authored 09:0x", "authored 10:2x")
    s = s.replace("bc3b2b693", "f9441de67")
    s = s.replace("9f5f106d6", "472cc8386")
    return s

def chunk(src_text, dst_text, tag):
    global t
    needle = xf(src_text)
    n = t.count(needle)
    assert n == 1, f"[{tag}] chunk needle count {n} != 1 (needle head: {needle[:80]!r})"
    t = t.replace(needle, dst_text)
    log.append(f"{tag}: chunk 1x ({len(src_text)} -> {len(dst_text)} chars)")

# ============ P1: structural faces, BLANKET-IMMUNE outputs ============
rep("(247, 246, 245, 244, 243, 242, 241, 240, 239, 238)",
    "(248, 247, 246, 245, 244, 243, 242, 241, 240, 239)", 2, "P1-transitive-deps")
rep("range(209, 252)", "range(209, 253)", 2, "P1-liveness-range")
rep('def fmt(n):  # 567501 -> "567_501"', 'def fmt(n):  # 569701 -> "569_701"', 1, "P1-fmt-comment")

# ============ P2: downstream shift W252 -> W253 (incl. W252p_* receipt keys) ============
rep("W252", "W253", None, "P2-downstream")
assert "W252" not in t, "P2 leftover W252"

# ============ P3: self shift 251 -> 252 ============
n251 = t.count("251")
rep("251", "252", None, "P3-self")
log.append(f"P3 consumed {n251} '251' substrings")

# ============ P4: upstream shift 250 -> 251 ============
n250 = t.count("250")
rep("250", "251", None, "P4-upstream")
log.append(f"P4 consumed {n250} '250' substrings")

# ============ P5a: numeric/anchor/ordinal/window faces (post-blanket forms) ============
rep("974_335", "976_535", 1, "P5a-ledger-int")  # r1050 fix: dead-window typo 976_335; W251 finalize ledger = 976,535 (r1048 fivekey receipt)
rep("547_920", "550_120", 1, "P5a-k-int")
rep("974,335", "976,535", 8, "P5a-ledger-prose")
rep("547,920", "550,120", 8, "P5a-k-prose")
rep("bmc_ordinal=71", "bmc_ordinal=72", 7, "P5a-ordinal71")
rep("SEVENTY-FIRST", "SEVENTY-SECOND", 3, "P5a-seventyfirst")
rep("TWO HUNDRED AND FIFTY-FIRST", "TWO HUNDRED AND FIFTY-SECOND", 3, "P5a-250th")
rep("thirty-ninth consecutive", "fortieth consecutive", 2, "P5a-finface")
rep("71st own wave", "72nd own wave", 3, "P5a-71st-ownwave")
rep("MSG-20261016-085x-bmc-w252-seat", "MSG-20261016-10xx-bmc-w252-seat", 7, "P5a-seat-msg")
rep("bc3b2b693", "f9441de67", 2, "P5a-seat-origin")
rep("9f5f106d6", "472cc8386", 1, "P5a-prereg-commit")
# r-window faces: upstream W251 chain = splice r1048 window + finalize r1048
# (closeout 10:0x); W252 prereg derive window = r1049; this freeze = r1050.
rep("2026-10-16 09:2x bm-c r1048 freeze window", "2026-10-16 11:0x bm-c r1050 freeze window", 1, "P5a-header-window")
rep("W251 finalize one-pass bm-c r1046 window closeout 08:3x",
    "W251 finalize one-pass bm-c r1048 window closeout 10:0x", 1, "P5a-closeout-window")
rep("r1046 splice window", "r1048 splice window", 3, "P5a-splice-window")
rep("r1046", "r1048", 19, "P5a-splice-window-rest")
rep("r1047", "r1049", 7, "P5a-prereg-window")
rep("authored 09:0x", "authored 10:2x", 2, "P5a-authored-time")
# aging-face needle heals (same-window disclosed, r1045/r1047 precedent family):
rep("transitive window W238..W247 checked", "transitive window W239..W248 checked", 1, "P5a-aging-deps-cmt")
rep("engine_owner==bm-c rows 68 + candidate", "engine_owner==bm-c rows 71 + candidate", 1, "P5a-aging-rows68-heal")

# ============ P5b: extraction restructure (frozen W252 prereg sec.3 mandate) ============
# estate boundary moves to W211: estate = W138..W206 69-row full-span ONLY;
# kept legs = W211..W238 (28); dropped = W239..W250 (12); fresh = W239..W251 (13).
rep('''m234 = re.search(r" *assert pf\\.N1_BANDS\\[234\\] ==", par_full)
assert m234, "upstream W234 row leg not found inside W251 parity span"
par_sec = par_full[:m234.start()]
legs_sec = par_full[m234.start():]''',
'''m211 = re.search(r" *assert pf\\.N1_BANDS\\[211\\] ==", par_full)
assert m211, "upstream W211 row leg not found inside W251 parity span (estate boundary: W138..W206 full-span 69 rows only, frozen W252 prereg sec.3 mandate)"
par_sec = par_full[:m211.start()]
legs_sec = par_full[m211.start():]''', 1, "P5b-m211-boundary")

chunk('''# STRUCTURAL CHOICE (frozen W251 prereg sec.3 mandate): extract the 92-row
# estate (W138..W206 full-span 69 rows + W211..W233 legs) AND the W234..W238
# legs (5) from the OWN W250 block physical bytes (bm-c r1046 splice
# generation, committed -- structure known exactly); the W250 block's own
# W239..W249 legs (11) are EXCLUDED from the estate path per the prereg
# mandate; the W251 block appends fresh W239..W250 legs (12, machine-derived
# from the LIVE pf registry at freeze time) -> 109 parity rows.''',
'''# STRUCTURAL CHOICE (frozen W252 prereg sec.3 mandate): extract the 69-row
# estate (W138..W206 full-span 69 rows, r858 absorb generation) AND the
# W211..W238 legs (28) from the OWN W251 block physical bytes (bm-c r1048
# splice generation, committed -- structure known exactly); the W251
# block's own W239..W250 legs (12) are EXCLUDED from the estate path per the
# prereg mandate; the W252 block appends fresh W239..W251 legs (13,
# machine-derived from the LIVE pf registry at freeze time) -> 110 parity
# rows.''', "P5b-ext-choice")

chunk('''_estate_ws = re.findall(r"assert pf\\.N1_BANDS\\[(\\d+)\\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 92 \\
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \\
    and [int(_estate_ws[69 + i]) for i in range(11)] == [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221] \\
    and [int(_estate_ws[80 + i]) for i in range(9)] == [222, 223, 224, 225, 226, 227, 228, 229, 230] \\
    and int(_estate_ws[89]) == 231 \\
    and int(_estate_ws[90]) == 232 \\
    and int(_estate_ws[91]) == 233, \\
    f"estate segment not W138..W206 full-span 69 rows + W211..W232 legs + W233 leg: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-4:])}"''',
'''_estate_ws = re.findall(r"assert pf\\.N1_BANDS\\[(\\d+)\\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 69 \\
    and [int(w) for w in _estate_ws] == list(range(138, 207)), \\
    f"estate segment not W138..W206 full-span 69 rows (frozen W252 prereg sec.3 estate-extraction mandate): n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-4:])}"''', "P5b-estate-assert")

rep('''assert par_full.count("assert pf.N1_BANDS[") == 108, \\
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 108 (92 estate + W234..W249 legs 16)"''',
'''assert par_full.count("assert pf.N1_BANDS[") == 109, \\
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 109 (69 estate + W211..W250 legs 40)"''', 1, "P5b-parfull")

rep('''_legs_ws = re.findall(r"assert pf\\.N1_BANDS\\[(\\d+)\\] ==", legs_sec)
assert legs_sec.count("assert pf.N1_BANDS[") == 16 \\
    and [int(w) for w in _legs_ws] == list(range(234, 251)), \\
    f"legs segment not W234..W249 sixteen legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}"''',
'''_legs_ws = re.findall(r"assert pf\\.N1_BANDS\\[(\\d+)\\] ==", legs_sec)
assert legs_sec.count("assert pf.N1_BANDS[") == 40 \\
    and [int(w) for w in _legs_ws] == list(range(211, 251)), \\
    f"legs segment not W211..W250 forty legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}"''', 1, "P5b-legs-assert")

rep('''# prereg sec.3 mandate split: keep W234..W238 verbatim (5 legs); the W251
# block's own W239..W249 legs (11) are excluded from the estate path''',
'''# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W251
# block's own W239..W250 legs (12) are excluded from the estate path''', 1, "P5b-split-cmt")

rep('''_kept_ws = re.findall(r"assert pf\\.N1_BANDS\\[(\\d+)\\] ==", legs_kept)
assert legs_kept.count("assert pf.N1_BANDS[") == 5 \\
    and [int(w) for w in _kept_ws] == [234, 235, 236, 237, 238], \\
    f"kept segment not W234..W238 five legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"''',
'''_kept_ws = re.findall(r"assert pf\\.N1_BANDS\\[(\\d+)\\] ==", legs_kept)
assert legs_kept.count("assert pf.N1_BANDS[") == 28 \\
    and [int(w) for w in _kept_ws] == list(range(211, 239)), \\
    f"kept segment not W211..W238 twenty-eight legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"''', 1, "P5b-kept-assert")

rep('''_dropped_ws = re.findall(r"assert pf\\.N1_BANDS\\[(\\d+)\\] ==", legs_dropped)
assert legs_dropped.count("assert pf.N1_BANDS[") == 11 \\
    and [int(w) for w in _dropped_ws] == list(range(239, 251)), \\
    f"dropped segment not W239..W249 eleven legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}"''',
'''_dropped_ws = re.findall(r"assert pf\\.N1_BANDS\\[(\\d+)\\] ==", legs_dropped)
assert legs_dropped.count("assert pf.N1_BANDS[") == 12 \\
    and [int(w) for w in _dropped_ws] == list(range(239, 251)), \\
    f"dropped segment not W239..W250 twelve legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}"''', 1, "P5b-dropped-assert")

rep("# ---------- fresh legs W236..W251 (machine-derived from the LIVE pf registry) ----------",
    "# ---------- fresh legs W239..W251 (machine-derived from the LIVE pf registry) ----------",
    1, "P5b-fresh-cmt-heal")

# materializer hdr PARITY lines (emitted comment block)
chunk(''' "    #     PARITY STRUCTURAL CHOICE (frozen W251 prereg sec.3 mandate):",
 "    #     estate 92 rows (W138..W206 full-span 69 + W211..W233 legs) +",
 "    #     W234..W238 legs (5) extracted verbatim from the OWN W250 block",
 "    #     physical bytes; the W250 block's own W239..W249 legs (11) are",
 "    #     EXCLUDED from the estate path per the prereg mandate; fresh",
 "    #     W239..W250 legs (12) added, machine-derived from the live pf",
 "    #     registry at freeze time -> 109 parity rows (W138..W206+W211..W250).",''',
'''"    #     PARITY STRUCTURAL CHOICE (frozen W252 prereg sec.3 mandate):",
 "    #     estate 69 rows (W138..W206 full-span, r858 absorb generation) +",
 "    #     W211..W238 legs (28) extracted verbatim from the OWN W251 block",
 "    #     physical bytes; the W251 block's own W239..W250 legs (12) are",
 "    #     EXCLUDED from the estate path per the prereg mandate; fresh",
 "    #     W239..W251 legs (13) added, machine-derived from the live pf",
 "    #     registry at freeze time -> 110 parity rows (W138..W206+W211..W251).",''', "P5b-hdr-parity")

# receipt parity_section fields + note
rep('                     "fresh_legs_row_asserts": 12,',
    '                     "fresh_legs_row_asserts": 13,', 1, "P5b-rcpt-fresh12")
rep('''                     "total_parity_rows": par_sec.count("assert pf.N1_BANDS[")
                                          + legs_kept.count("assert pf.N1_BANDS[") + 12,''',
'''                     "total_parity_rows": par_sec.count("assert pf.N1_BANDS[")
                                          + legs_kept.count("assert pf.N1_BANDS[") + 13,''', 1, "P5b-rcpt-total12")

chunk('''                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W233 legs (estate 92) + W234..W238 legs extracted verbatim (5) per the frozen W251 prereg sec.3 mandate; the W250 block's own W239..W249 legs (11) EXCLUDED from the estate path per the same mandate; fresh W239..W250 legs (12) machine-derived from the live pf registry -> W251 block = 109 rows (W138..W206 + W211..W250); disclosed: (a) inherited W213 leg error-string face preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-251 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 3rd-gen prevention this window: the W251 derive editor reordered passes so P1 structural outputs are blanket-immune and the legs/dropped wave-identity asserts are fixed post-blanket (range(233,250)/range(238,250) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},''',
'''                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W238 legs (28) extracted verbatim per the frozen W252 prereg sec.3 mandate; the W251 block's own W239..W250 legs (12) EXCLUDED from the estate path per the same mandate; fresh W239..W251 legs (13) machine-derived from the live pf registry -> W252 block = 110 rows (W138..W206 + W211..W251); disclosed: (a) inherited W213 leg error-string face preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-252 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 4th-gen prevention this window: the W252 derive editor reordered passes so P1 structural outputs are blanket-immune and the extraction-restructure legs/kept/dropped wave-identity asserts are fixed post-blanket (list(range(211,251))/list(range(211,239))/list(range(239,251)) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},''', "P5b-rcpt-note")

# header PARITY comment (3 line-level heals)
rep("# block's own W239..W249 legs (11 rows) do NOT enter the estate path;",
    "# block's own W239..W250 legs (12 rows) do NOT enter the estate path;", 1, "P5b-hdr-ownlegs")
rep("# after extraction, fresh W239..W251 legs (12 rows) are added,",
    "# after extraction, fresh W239..W251 legs (13 rows) are added,", 1, "P5b-hdr-freshlegs")
rep("# parity = 109 rows (W138..W206 + W211..W251). Zero assumption zero risk.",
    "# parity = 110 rows (W138..W206 + W211..W251). Zero assumption zero risk.", 1, "P5b-hdr-parity-count")

# ============ P5c: band literals (probe ADMIT receipt bands) ============
rep('assert (a_lo, a_hi) == (567_501, 569_500) and (b_lo, b_hi) == (569_501, 569_700), \\',
    'assert (a_lo, a_hi) == (569_701, 571_700) and (b_lo, b_hi) == (571_701, 571_900), \\', 1, "P5c-band-drift")

# ============ P5d: ordinal/leg0/deps faces ============
rep('assert len(owner_rows_live) == 240 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 70, \\',
    'assert len(owner_rows_live) == 241 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 71, \\', 1, "P5d-ord-gate")
rep("(expect 240/129/70 PRE-splice post-W251 registration; this candidate = bm-c's 72nd own wave per the same live-derive law, r587/r359)",
    "(expect 241/129/71 PRE-splice post-W251 registration; this candidate = bm-c's 72nd own wave per the same live-derive law, r587/r359)", 1, "P5d-ord-err")
rep('# receipt leg0 face owner_rows=240 / bmc_rows=70 / bmc_ordinal=72',
    '# receipt leg0 face owner_rows=241 / bmc_rows=71 / bmc_ordinal=72', 1, "P5d-leg0-prose")
rep("-> owner rows 240 + candidate = 241st EXACT; bm-c rows 70 +",
    "-> owner rows 241 + candidate = 242nd EXACT; bm-c rows 71 +", 1, "P5d-ord-owner-prose")
rep("# candidate = 71st EXACT -- bm-c own-seat continuity face (bm-c published the",
    "# candidate = 72nd EXACT -- bm-c own-seat continuity face (bm-c published the", 1, "P5d-ord-bmc-prose")
rep("freeze-time live face owner rows 240 + candidate = 241st EXACT",
    "freeze-time live face owner rows 241 + candidate = 242nd EXACT", 1, "P5d-rcpt-241st")
rep("freeze-time live derive bmc rows 70 + candidate 71st EXACT per r587/r359",
    "freeze-time live derive bmc rows 71 + candidate 72nd EXACT per r587/r359", 1, "P5d-bundle-71st")
rep("post-W251 registration: bm-c rows 70 + candidate = 71st owned",
    "post-W251 registration: bm-c rows 71 + candidate = 72nd owned", 1, "P5d-rcpt-71st-owned")
rep('"probe_receipt_bmc_ordinal_face": 71,', '"probe_receipt_bmc_ordinal_face": 72,', 1, "P5d-rcpt-ordface")
rep('f"W251+W246..W237 finalize products present "', 'f"W251+W247..W238 finalize products present "', 1, "P5d-print-deps")

# ============ P5e: A/B face structural rewrites (BOTH bands change face) ============
# header NEW FACE block
chunk('''# NEW FACE vs the W250 editor (honest disclosure, frozen W251 prereg sec.3
# mandate): A = FIRST-CLEAN arithmetic continuation of the prior-wave A tail
# (567_501..569_500, naive start CLEAN on the post-W250-REGISTERED universe,
# hops=0, A_hop_chain empty + A_clean_at_naive_start=true, seed-decoupled
# A-continuation face, FOURTEENTH consecutive seed-gap face, anticipated by
# the W250 prereg sec.5 item5 + W250 probe leg4 + seat leg4 and confirmed
# live); B = 13-HOP WALK above own-A (the naive continuation 545_301..545_500
# is REFUSED at its own start -- SEED_REGISTRY seed 545_500 + the W240..W249
# A-ladder bands per the W250 prereg sec.5 item5 projection; the pre-W250
# projected first-clean 565_501..565_700 is now INSIDE the registered W250
# A band, so the post-W250 walk hops past it AND past the own-wave A window;
# B lands ABOVE own-A -- first above-own-A landing since the W239 staircase
# era; B base == own-A tail+1 (569_500+1) EXACT; B_naive_refused_at_start=true;
# B_lands_above_own_A=true; B_hop_lands_inside_A=false; hops=13).''',
'''# NEW FACE vs the W251 editor (honest disclosure, frozen W252 prereg sec.3
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
# B_hop_lands_inside_A=false; hops=1).''', "P5e-hdr")

# band facts comment block
chunk('''# W251 FACE (probe receipt leg1 relation_asserts):
# A keeps the A-continuation base (prior-wave A tail+1 EXACT -- the naive
# arithmetic continuation is CLEAN at its own start, hops=0, A_hop_chain
# empty, A_clean_at_naive_start=true -- fourteenth consecutive seed-gap face per
# the W250 prereg sec.5 item5 + W250 probe leg4 + seat leg4 anticipation confirmed live, frozen receipt
# A_semantics verbatim); B takes the 13-HOP WALK face (naive continuation
# REFUSED at its own start -- B_naive_refused_at_start=true, hops=13,
# B_hop_chain verbatim in the receipt; the walk hops past the W240..W249
# A-ladder bands + W250-A + the own-wave A window reservation); B lands
# ABOVE own-A (B_lands_above_own_A=true -- B base == own-A tail+1 EXACT,
# first above-own-A landing since the W239 staircase era); A sits far above
# the B staircase base (seed-decoupled A/B gap,
# fourteenth consecutive); machine-derived from the LIVE registered row, never
# transcribed.''',
'''# W252 FACE (probe receipt leg1 relation_asserts):
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
# LIVE registered row, never transcribed.''', "P5e-bandfacts")

# band-facts assert lines (A face)
rep('assert w251_a_tail + 1 == a_lo, "A continuation base relation broken (A == prior-wave A tail+1 EXACT)"',
    'assert w251_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1 EXACT -- the 1-hop walk past the registered W251 B band; first A-hop since the W239 staircase era; A_staircase_hop_past_W251_B=true)"', 1, "P5e-a-base")
rep('assert a_lo > w251_b_tail + 1, "seed-decoupled A-continuation face violated: A base must sit ABOVE prior-B tail+1 (seed-gap)"',
    'assert a_lo >= w251_b_tail + 1, "A staircase landing floor relation (A base >= registered prior-wave B tail+1; the fourteen-wave seed-gap face ENDS at W252 -- first A-hop since the W239 staircase era, A base == prior-B tail+1 EXACT this window per the prereg floor-relation mandate)"', 1, "P5e-a-floor")
rep('assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 13-hop walk lands ABOVE own-A -- first since the W239 staircase era; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"',
    'assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation lands ABOVE own-A -- second consecutive above-own-A; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"', 1, "P5e-b-base")
rep('assert W251["b_exit"][1] < W251["a"][0], \\\n    "upstream W251 row in-wave decoupled relation broken (registered W251 B window must sit below own W251 A window)"',
    'assert W251["b_exit"][0] == W251["a"][1] + 1, \\\n    "upstream W251 row above-own-A staircase relation broken (registered W251 B base == own W251 A tail+1 EXACT -- the above-own-A face inherited from the W251 freeze)"', 1, "P5e-upstream-rel")
rep('assert leg1.get("hops_A") == 0, "A hop-count drift vs probe receipt leg1 (A band naive hops=0, A-continuation face)"',
    'assert leg1.get("hops_A") == 1, "A hop-count drift vs probe receipt leg1 (A band naive hops=1, staircase-affects-A walk face)"', 1, "P5e-hopsA")
rep('assert leg1.get("hops_B") == 13, "B hop-count drift vs probe receipt leg1 (B band hops=13, 13-hop walk face above own-A)"',
    'assert leg1.get("hops_B") == 1, "B hop-count drift vs probe receipt leg1 (B band hops=1, own-A reservation walk face above own-A)"', 1, "P5e-hopsB")
rep('''assert leg1.get("A_hop_chain") == [] and (
    leg1.get("A_clean_at_naive_start") is True
    or (leg1.get("relation_asserts") or {}).get("A_clean_at_naive_start") is True
), \\
    "A hop-chain face drift (fc_a == fc_a_naive, hops=0, A_clean_at_naive_start=true -- naive continuation CLEAN at own start)"''',
'''assert len(leg1.get("A_hop_chain") or []) == 1 and (
    leg1.get("A_clean_at_naive_start") is False
    or (leg1.get("relation_asserts") or {}).get("A_clean_at_naive_start") is False
), \\
    "A hop-chain face drift (hops=1 staircase-affects-A walk -- naive continuation REFUSED at own start, the registered W251 B band sits inside the naive A window; A_hop_chain verbatim in the probe receipt)"''', 1, "P5e-hopchainA")
rep('assert len(leg1.get("B_hop_chain") or []) == 13 and leg1.get("B_naive_refused_at_start") is True, \\\n    "B hop-chain face drift (hops=13 walk face -- naive continuation REFUSED at start, B_naive_refused_at_start=true; B_hop_chain verbatim in the probe receipt)"',
    'assert len(leg1.get("B_hop_chain") or []) == 1 and leg1.get("B_naive_refused_at_start") is True, \\\n    "B hop-chain face drift (hops=1 own-A reservation walk -- naive continuation lands INSIDE the own-wave A window, B_naive_refused_at_start=true; B_hop_chain verbatim in the probe receipt)"', 1, "P5e-hopchainB")

# relation_asserts gate (incl. W250_W251 rsv-key fix -- both instances live here)
rep('''ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_clean_at_naive_start") is False and ra.get("B_base_above_W251_tail") \\
    and ra.get("AB_mutual_exclusion") and ra.get("B_hop_lands_inside_A") is False \\
    and ra.get("W249_W251_bands_respected_A") and ra.get("W249_W251_bands_respected_B"), \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"''',
'''ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") is False and ra.get("A_staircase_hop_past_W251_B") \\
    and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_clean_at_naive_start") is False and ra.get("B_base_above_W251_tail") \\
    and ra.get("AB_mutual_exclusion") and ra.get("B_hop_lands_inside_A") is False \\
    and ra.get("B_lands_above_own_A") and ra.get("W250_W251_bands_respected_A") and ra.get("W250_W251_bands_respected_B"), \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"''', 1, "P5e-ra-gate")

# pf_comment A/B lines
chunk('''"    # band gate ADMIT results/_w251bmc_20261016_probe_receipt.json: A = FIRST-CLEAN",
"    # arithmetic continuation of the prior-wave A tail (" + fmt(w250_a_tail + 1) + ".." + fmt(w250_a_tail + 2_000) + " CLEAN",
"    # at naive start on the registered universe, hops=0, A_hop_chain empty +",
"    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,",
"    # FOURTEENTH consecutive seed-gap face per the W250 probe leg4 + seat leg4",
"    # anticipation confirmed live; A base == prior-wave A tail+1 (" + fmt(w250_a_tail) + "+1) machine-checkable;",
"    # B = 13-HOP WALK above own-A (the naive continuation",
"    # " + fmt(w250_b_tail + 1) + ".." + fmt(w250_b_tail + 200) + " REFUSED at naive start -- SEED_REGISTRY seed 545_500 +",
"    # the W240..W249 A-ladder bands + W250-A + own-A reservation; hops=13,",
"    # B_hop_chain verbatim in the probe receipt; the walk hops past the",
"    # pre-W250 projected first-clean 565_501..565_700 (now INSIDE the registered W250 A band) AND",
"    # past the own-wave A window; B lands ABOVE own-A -- first since the W239 staircase",
"    # era; B base == own-A tail+1 (" + fmt(a_hi) + "+1) EXACT; B_lands_above_own_A=true;",
"    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)",''',
'''"    # band gate ADMIT results/_w252bmc_20261016_probe_receipt.json: A = 1-HOP",
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
"    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)",''', "P5e-pfcmt")

# PRE block A/B lines
chunk(''' "wave 251: ",
 "A = FIRST-CLEAN arithmetic continuation of the prior-wave A tail (the continuation ",
 f"{fmt(w250_a_tail + 1)}..{fmt(w250_a_tail + 2_000)} is CLEAN at its own start ",
 "-- hops=0, A_hop_chain empty + A_clean_at_naive_start=true, seed-decoupled ",
 "A-continuation face, FOURTEENTH consecutive seed-gap face exactly as the W250 probe leg4 + seat leg4 ",
 "succession projection notes anticipated; A base == prior-wave A tail+1 (",
 f"{fmt(w250_a_tail)}+1) machine-checkable; ",
 "non-rotational r587 forward-monotone walk) + B = 13-HOP WALK above own-A ",
 "(the naive continuation ",
 f"{fmt(w250_b_tail + 1)}..{fmt(w250_b_tail + 200)} is REFUSED at its own start ",
 "-- hops=13, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the ",
 f"walk hops past the W240..W249 A-ladder bands + W250-A + the own-wave A window (own-A reservation standard leg); B lands ABOVE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT; first above-own-A landing since the W239 ",
 "staircase era; B base == own-A tail+1 (",
 f"{fmt(a_hi)}+1) machine-checkable; cross-window convergence with the W250 prereg sec.5 item5 + W250 probe leg4 + seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W250 universe ",
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",''',
''' "wave 252: ",
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
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",''', "P5e-pre")

# MEM_I comment lines (A + B faces)
rep(""" f'{MEM_I}\"a_seed_base\": {a_lo},        # law sec.4 W252 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN arithmetic continuation of the prior-wave A tail; {fmt(w251_a_tail + 1)}..{fmt(w251_a_tail + 2_000)} CLEAN at naive start hops=0, A_hop_chain empty + A_clean_at_naive_start=true; seed-decoupled A-continuation face FOURTEENTH consecutive seed-gap face; A base == prior-A tail+1)',""",
    """ f'{MEM_I}\"a_seed_base\": {a_lo},        # law sec.4 W252 A: {fmt(a_lo)}..{fmt(a_hi)} (1-HOP STAIRCASE-AFFECTS-A walk; naive {fmt(w251_a_tail + 1)}..{fmt(w251_a_tail + 2_000)} REFUSED at start -- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; registered W251 B band inside the naive A window; A first-hop since the W239 staircase era -- seed-gap face ENDS at W252; A base == registered prior-wave B tail+1)',""",
    1, "P5e-mem-a")
rep(""" f'{MEM_I}\"b_exit_seed_base\": {b_lo},   # law sec.4 W252 B: {fmt(b_lo)}..{fmt(b_hi)} (13-HOP WALK above own-A; naive {fmt(w251_b_tail + 1)}..{fmt(w251_b_tail + 200)} REFUSED at start -- hops=13, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; hops past the W240..W249 A-ladder + W251-A + own-A reservation; B lands ABOVE own-A at tail+1 EXACT -- first since the W239 staircase era; B base == own-A tail+1)',""",
    """ f'{MEM_I}\"b_exit_seed_base\": {b_lo},   # law sec.4 W252 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION above own-A; naive {fmt(w251_b_tail + 1)}..{fmt(w251_b_tail + 200)} REFUSED at start -- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; naive window lands inside the own-wave A first-clean window -> own-A reservation; B lands ABOVE own-A at tail+1 EXACT -- second consecutive above-own-A; B base == own-A tail+1)',""",
    1, "P5e-mem-b")

# tail band-facts comments (A + B lines)
chunk('''"        # band facts (law sec.4 W251 row): A = FIRST-CLEAN arithmetic",
"        # continuation of the prior-wave A tail",
f"        # ({fmt(w250_a_tail + 1)}..{fmt(w250_a_tail + 2_000)} CLEAN at naive start on the",
"        # registered universe, hops=0, A_hop_chain empty +",
"        # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,",
"        # FOURTEENTH consecutive seed-gap face, exactly as the W250 probe leg4 +",
"        # seat leg4 succession projection notes anticipated; A base ==",
f"        # prior-wave A tail+1 ({fmt(w250_a_tail)}+1) machine-checkable;",
"        # B = 13-HOP WALK above own-A (the naive continuation",
f"        # {fmt(w250_b_tail + 1)}..{fmt(w250_b_tail + 200)} REFUSED at naive start -- SEED_REGISTRY seed 545_500 +",
"        # the W240..W249 A-ladder bands + W250-A + own-A reservation; hops=13,",
"        # B_hop_chain verbatim in the probe receipt; the walk hops past the",
f"        # pre-W250 projected first-clean 565_501..565_700 (now INSIDE the registered W250 A band {fmt(pf_mod.N1_BANDS[250]['a'][0])}..{fmt(pf_mod.N1_BANDS[250]['a'][1])})",
"        # and past the own-wave A window; B lands ABOVE the own-A window",
f"        # {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT -- first above-own-A landing since the W239 staircase era;",
"        # B base == own-A tail+1 EXACT",
"        # machine-checkable; B_hop_lands_inside_A=false;",
"        # B_lands_above_own_A=true; cross-window convergence with",
"        # the W250 prereg sec.5 item5 + W250 probe leg4 + seat leg4 succession projection notes -- all",
"        # MANDATORY notes honored (post-W250 universe",
"        # re-derive + live-trace re-read, no staircase-equality assumption);",''',
'''"        # band facts (law sec.4 W252 row): A = 1-HOP STAIRCASE-AFFECTS-A",
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
"        # re-derive + live-trace re-read, no staircase-equality assumption);",''', "P5e-tailcmt")

# tail assert block (A face head + messages)
rep("f'        assert WAVE_CONFIGS[252][\"a_seed_base\"] == {a_lo} == {w251_a_tail} + 1, ('",
    "f'        assert WAVE_CONFIGS[252][\"a_seed_base\"] == {a_lo} == {w251_b_tail} + 1, ('", 1, "P5e-tail-aassert1")
rep('            "W252 A must be the first-clean arithmetic continuation of the "\',\n\'            "prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true -- "\',\n\'            "seed-decoupled A-continuation face, FOURTEENTH consecutive seed-gap face, "\',\n\'            "exactly as the W251 probe leg4 + seat leg4 succession projection notes "\',\n\'            "anticipated; A base == prior-wave A tail+1 machine-checkable)"',
    '            "W252 A staircase-affects-A walk: the naive continuation is REFUSED at "\',\n\'            "its own start (the registered W251 B band sits INSIDE the naive A window -- "\',\n\'            "staircase re-emergence affects A; hops=1, A_hop_chain verbatim in the probe receipt, "\',\n\'            "A_clean_at_naive_start=false, A_staircase_hop_past_W251_B=true; the walk hops past "\',\n\'            "the W251 B tail -> A first-clean -- FIRST A-hop since the W239 staircase era, "\',\n\'            "the fourteen-wave seed-gap face ENDS at W252; A base == registered prior-wave B "\',\n\'            "tail+1 machine-checkable, floor relation honored)"', 1, "P5e-tail-amsg")
rep('            "W252 A window must be CLEAN (first-clean ADMIT face, A-continuation)"\'', '            "W252 A window must be CLEAN (first-clean ADMIT face, staircase walk landing)"\'', 1, "P5e-tail-aclean")

# tail assert block (B face messages)
rep("'            \"W252 B 13-HOP WALK face: the naive continuation \"'",
    "'            \"W252 B 1-HOP own-A RESERVATION face: the naive continuation \"'", 1, "P5e-tail-bassert2")
rep("'            \"(hops=13, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; \"'",
    "'            \"(hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; \"'", 1, "P5e-tail-bassert4")
rep("'            \"the walk hops past the W240..W249 A-ladder bands + W251-A + the own-wave A window) -- B base == own-A tail+1 \"'",
    "'            \"the naive window lands INSIDE the own-wave A first-clean window -- own-A reservation hops B past the own-wave A tail) -- B base == own-A tail+1 \"'", 1, "P5e-tail-bassert5")
rep("'            \"W252 B window must be CLEAN (first-clean ADMIT face, 13-hop walk landing)\"'",
    "'            \"W252 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation landing)\"'", 1, "P5e-tail-bclean")
rep("'            \"W252 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- first since the W239 staircase era; zero overlap)\"'",
    "'            \"W252 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- second consecutive above-own-A; zero overlap)\"'", 1, "P5e-tail-excl")

# pr print A/B lines
chunk(''' '          "A=FIRST-CLEAN arithmetic continuation of prior-wave A tail (A-continuation face, "',
 '          "hops=0, A_hop_chain empty + A_clean_at_naive_start=true, seed-decoupled FOURTEENTH consecutive seed-gap face) "',
 '          "+ B=13-HOP WALK above own-A (hops=13, B_naive_refused_at_start=true, "',
 '          "B_hop_chain verbatim, hops past the W240..W249 A-ladder + W250-A + own-A reservation, "',
 '          "B base == own-A tail+1 EXACT, B_lands_above_own_A=true, "',
 '          "first above-own-A landing since the W239 staircase era), chain-order splice from the "''',
''' '          "A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, "',
 '          "registered W251 B band inside the naive A window, FIRST A-hop since the W239 staircase era, "',
 '          "the fourteen-wave seed-gap face ENDS at W252) "',
 '          "+ B=1-HOP own-A RESERVATION above own-A (hops=1, B_naive_refused_at_start=true, "',
 '          "B_hop_chain verbatim, naive window lands inside the own-wave A window -> own-A reservation, "',
 '          "B base == own-A tail+1 EXACT, B_lands_above_own_A=true, "',
 '          "SECOND consecutive above-own-A landing), chain-order splice from the "''', "P5e-pr")

# receipt band_semantics A + B values
rep('"A": "FIRST-CLEAN arithmetic continuation of prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true; seed-decoupled A-continuation face, FOURTEENTH consecutive seed-gap face; A base == prior-A tail+1 EXACT)"',
    '"A": "1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 569_501..571_500 refused at start -- the registered W251 B band 569_501..569_700 sits INSIDE the naive A window (staircase re-emergence affects A; the W251 prereg sec.5 item5 A-CLEAN projection superseded live r587, divergence disclosed); the walk hops past the W251 B tail 569_700 -> A first-clean 569_701..571_700 -- FIRST A-hop since the W239 staircase era, the fourteen-wave seed-gap face ENDS at W252; A_clean_at_naive_start=false; A_staircase_hop_past_W251_B=true; A base == registered prior-wave B tail+1 (569_700+1) EXACT)"', 1, "P5e-rcpt-semantics-A")
rep('"B": "13-HOP WALK above own-A (hops=13, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the naive continuation 545_301..545_500 refused at start -- SEED_REGISTRY seed 545_500 + the W240..W249 A-ladder bands + W251-A + own-A reservation; the walk hops past the pre-W251 projected first-clean 565_501..565_700 (now INSIDE the registered W251 A band 565_501..567_500) and past the own-wave A window; B lands ABOVE own-A -- first above-own-A landing since the W239 staircase era; B_lands_above_own_A=true; B_hop_lands_inside_A=false; B base == own-A tail+1 (569_500+1) EXACT)"',
    '"B": "1-HOP own-A RESERVATION above own-A (hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the naive continuation 569_701..569_900 is refused at start -- the naive window lands INSIDE the own-wave W252 A first-clean window 569_701..571_700 (own-A reservation standard leg; the W251 prereg sec.5 item5 projected landing ~571_501..571_700 superseded live -- the A face itself moved, divergence disclosed per r587); the walk hops past the own-A tail 571_700 -> B landing 571_701..571_900; B lands ABOVE own-A -- SECOND consecutive above-own-A landing; B_lands_above_own_A=true; B_hop_lands_inside_A=false; B base == own-A tail+1 (571_700+1) EXACT)"', 1, "P5e-rcpt-semantics-B")

# downstream W253+ projection faces (stale numbers + staircase-continuation caveat)
rep("W253p face per this window's probe leg4: A naive 569501..571500 CLEAN (hops=0, zero live refusers) / B naive 569701..569900 hops=0 CLEAN at naive, first-clean 569701..569900 BUT lands INSIDE the W253 projection A window (W253p_B_lands_inside_W253p_A_naive=true staircase re-emergence face: the W253 walk MUST hop past the own-A reservation); seed-gap face inherited: W252 A/B decoupled, re-read the live trace at W253 derive time, do NOT assume the staircase A-base==prior-B-tail+1 equality",
    "W253p face per this window's probe leg4 (pre-W252 universe): A naive 571701..573700 CLEAN (hops=0, zero live refusers) / B naive 571901..572100 hops=0 CLEAN at naive, first-clean 571901..572100 BUT lands INSIDE the W253 projection A window (W253p_B_lands_inside_W253p_A_naive=true staircase face continuation: on the post-W252 universe the W253 naive A window start is REFUSED by the registered W252 B band -- staircase affects A inherited, the A first-clean and the B own-A reservation landing both move up, live re-derive governs); re-read the live trace at W253 derive time, do NOT assume the staircase A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities", 1, "P5e-rcpt-downstream")
rep('"    # equality); never transcribe r587.",',
    '"    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.",', 1, "P5e-pfcmt-leg4-eq")
rep('"staircase A-base==prior-B-tail+1 equality) -- the finalize ",',
    '"staircase A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities) -- the finalize ",', 1, "P5e-pre-leg4-eq")

# r1050 fix: ARITH_A naive-window start-drift assert message still carries the
# W251-era "A-continuation" face language (check itself stays valid for W252:
# naive arith window [569_501, 571_500] == probe leg1 ARITH_A) -- purge the
# stale face word to satisfy the anti-gate.
rep('f"A-continuation start drift vs probe receipt leg1 ARITH_A: {[w251_a_tail + 1, w251_a_tail + 2_000]} != {leg1[\'ARITH_A\']}"',
    'f"A naive-arithmetic window start drift vs probe receipt leg1 ARITH_A: {[w251_a_tail + 1, w251_a_tail + 2_000]} != {leg1[\'ARITH_A\']}"', 1, "P5e-aritha-msg")

# ============ structural output gates ============
for needle, want in [
    ("# --- W252 materializer face", 2),
    ("# --- W251 materializer face", 1),
    ('"+ W252 materializer face', 2),
    ("range(16, 252)", 2),
    ("range(17, 252)", 3),
    ("range(239, 252)", 2),
    ("list(range(211, 251))", 1),
    ("list(range(211, 239))", 1),
    ("list(range(239, 251))", 1),  # r1050 fix: dropped-assert dst is the sole spaced occurrence (fresh legs = range(239,252) loops; receipt-note form is space-less)
    ("range(209, 253)", 2),
    ("if w < 252)", 5),
    ("if w < 251)", 1),
    ("_w252bmc_20261016_probe_receipt.json", 10),
    ("_w252bmc_freeze_receipt.json", 1),
    ("MSG-20261016-10xx-bmc-w252-seat", 7),
    ("f9441de67", 2),
    ("976_535", 1),
    ("550_120", 1),
    ("(569_701, 571_700)", 1),
    ("(571_701, 571_900)", 1),
    ("W250_W251_bands_respected_A", 1),
    ("W250_W251_bands_respected_B", 1),
    ("B_base_above_W251_tail", 2),
    ("A_staircase_hop_past_W251_B", None),
    ("W253p_A_naive", 5),
    ("W253p_B_first_clean", 2),
    ("arith_a252", 6),
    ("arith_b252", 6),
    ('"PERPETUAL-N1-W252-SHARD-0"', 1),
    ("n1_w252_results.json", 2),
    ("n1_w252", 4),
    ("n1w252", 2),
    ("PERPETUAL-N1-W252", 7),
    ("_w252bmc", 11),
    ("w244_a", 12),
    ("SEVENTY-SECOND", 3),
    ("TWO HUNDRED AND FIFTY-SECOND", 3),
    ("fortieth consecutive", 2),
    ("bmc_ordinal=72", 7),
    ("72nd own wave", 3),
    ("r1048 splice window", 3),
    ("r1048", 23),
    ("r1049", 7),
    ("r1050 freeze window", 1),
    ("estate 69", 1),
    ("= 110 rows", 2),
    ("110 parity", 2),
    ("hops=1", None),
    ("1-HOP", None),
    ("FIRST A-hop", None),
    ("seed-gap face ENDS", None),
    # anti-gates: stale faces must be zero
    ("r1046", 0),
    ("r1047", 0),
    ("9f5f106d6", 0),
    ("bc3b2b693", 0),
    ("974,335", 0),
    ("547,920", 0),
    ("974_335", 0),
    ("547_920", 0),
    ("FOURTEENTH", 0),
    ("fourteenth", 0),
    ("thirty-ninth", 0),
    ("MSG-20261016-085x", 0),
    ("08:3x", 0),
    ("09:2x", 0),
    ("authored 09:0x", 0),
    ("bmc_ordinal=71", 0),
    ("71st", 0),
    ("241st", 0),
    ("240/129/70", 0),
    ("SEVENTY-FIRST", 0),
    ("TWO HUNDRED AND FIFTY-FIRST", 0),
    ("13-HOP", 0),
    ("hops=13", 0),
    ("FIRST-CLEAN", 0),
    ("A-continuation", 0),
    ("seed-decoupled", 0),
    ("A_clean_at_naive_start=true", 0),
    ("W249_W251_bands_respected", 0),
    ("estate 92", 0),
    ("92 estate", 0),
    ("== 92", 0),
    ("== 108", 0),
    ("== 16", 0),
    ("eleven legs", 0),
    ("sixteen legs", 0),
    ("five legs", 0),
    ("109 parity", 0),
    ("109 rows", 0),
    ("m234", 0),
    ("(567_501, 569_500)", 0),
    ("(569_501, 569_700)", 0),
    ("545_500", 0),
    ("565_501..565_700", 0),
    ("rows 68 + candidate", 0),
    ("W236..W251", 0),
    ("list(range(234, 251))", 0),
]:
    n = t.count(needle)
    if want is not None:
        assert n == want, f"OUTPUT-GATE {needle!r}: {n} != {want}"
    log.append(f"OUT {needle!r} = {n}")

io.open(DST, "w", encoding="utf-8", newline="").write(t)
import py_compile
py_compile.compile(DST, doraise=True)
io.open(os.path.join(REPO, "results", "_w252bmc_derive_editor_log.txt"), "w",
        encoding="utf-8").write("\n".join(log))
print(f"DERIVE OK -> {DST} ({len(t)} chars); {len(log)} transform log rows")
print("\n".join(log[-12:]))
