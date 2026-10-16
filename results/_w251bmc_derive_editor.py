# -*- coding: utf-8 -*-
# r1048 bm-c: derive results/_w251bmc_freeze_edits.py from the committed W250
# editor (results/_w250bmc_freeze_edits.py, proven live-fire W250 splice bm-c
# r1046 window: splice 29930f489 by dead r1046-predecessor + finalize one-pass
# by the r1046 continuation, ledger 974,335 / K=547,920 five-key ALL PASS)
# via COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage, 3rd-gen pass ordering:
# P1 structural outputs BLANKET-IMMUNE, wave-identity asserts fixed
# post-blanket in P5b).
# W251 facts (machine-read, never transcribed): bands A 567_501..569_500
# (FIRST-CLEAN hops=0, FOURTEENTH consecutive seed-gap, A base==W250 A tail
# 567_500+1) / B 569_501..569_700 = 13-HOP WALK above own-A (naive
# 545_301..545_500 REFUSED at seed 545_500 + W240..W249 A-ladder + W250-A +
# own-A reservation; B base==own-A tail 569_500+1 EXACT; first above-own-A
# landing since the W239 staircase era), upstream W250 = bm-c own chain,
# seat MSG-20261016-085x-bmc-w251-seat @ origin bc3b2b693 r1046, prereg
# 9f5f106d6 derived bm-c r1047, parity estate 92 (W138..W206 69 +
# W211..W233 23) + kept W234..W238 (5) + dropped W239..W249 (11) + fresh
# W239..W250 (12) = 109 rows.
import io, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w250bmc_freeze_edits.py")
DST = os.path.join(REPO, "results", "_w251bmc_freeze_edits.py")

t = io.open(SRC, encoding="utf-8").read()
log = []

def rep(old, new, expect=None, tag=""):
    global t
    n = t.count(old)
    if expect is not None:
        assert n == expect, f"[{tag}] count {n} != {expect} for: {old[:70]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x {old[:48]!r}")

# xf(): exact composition of the blanket passes (P2/P3/P4) + the THIRTEENTH
# sensitives of P5a, used to derive post-pass needles for whole-chunk
# replacements WITHOUT hand-transcription (zero mental-derivation risk).
def xf(s):
    s = s.replace("W251", "W252")
    s = s.replace("250", "251")
    s = s.replace("249", "250")
    s = s.replace("THIRTEENTH consecutive", "FOURTEENTH consecutive")
    s = s.replace("thirteenth consecutive", "fourteenth consecutive")
    s = s.replace("face THIRTEENTH;", "face FOURTEENTH;")
    return s

def chunk(src_text, dst_text, tag):
    global t
    needle = xf(src_text)
    n = t.count(needle)
    assert n == 1, f"[{tag}] chunk needle count {n} != 1 (needle head: {needle[:80]!r})"
    t = t.replace(needle, dst_text)
    log.append(f"{tag}: chunk 1x ({len(src_text)} -> {len(dst_text)} chars)")

# ============ P1: structural faces, BLANKET-IMMUNE outputs ============
rep("(246, 245, 244, 243, 242, 241, 240, 239, 238, 237)",
    "(247, 246, 245, 244, 243, 242, 241, 240, 239, 238)", 2, "P1-transitive-deps")
rep("range(209, 251)", "range(209, 252)", 2, "P1-liveness-range")
rep("[233, 234, 235, 236, 237]", "[234, 235, 236, 237, 238]", 1, "P1-kept-list")
rep("range(238, 250)", "range(239, 251)", 2, "P1-fresh/legcount-loop")
rep("kept segment not W233..W237 five legs", "kept segment not W234..W238 five legs", 1, "P1-kept-err")
rep("assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[238] == {\"a\": (')",
    "assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[239] == {\"a\": (')", 1, "P1-fresh-firstline")
rep('assert par_sec.count("assert pf.N1_BANDS[") == 91 \\',
    'assert par_sec.count("assert pf.N1_BANDS[") == 92 \\', 1, "P1-estate-count")
rep('    and int(_estate_ws[89]) == 231 \\\n    and int(_estate_ws[90]) == 232, \\',
    '    and int(_estate_ws[89]) == 231 \\\n    and int(_estate_ws[90]) == 232 \\\n    and int(_estate_ws[91]) == 233, \\', 1, "P1-estate-decomp")
rep("estate segment not W138..W206 full-span 69 rows + W211..W231 legs + W232 leg:",
    "estate segment not W138..W206 full-span 69 rows + W211..W232 legs + W233 leg:", 1, "P1-estate-err")
rep('assert par_full.count("assert pf.N1_BANDS[") == 107, \\',
    'assert par_full.count("assert pf.N1_BANDS[") == 108, \\', 1, "P1-parfull-count")
rep('def fmt(n):  # 565501 -> "565_501"', 'def fmt(n):  # 567501 -> "567_501"', 1, "P1-fmt-comment")

# ============ P2: downstream shift W251 -> W252 (incl. W251p_* receipt keys) ============
rep("W251", "W252", None, "P2-downstream")
assert "W251" not in t, "P2 leftover W251"

# ============ P3: self shift 250 -> 251 ============
n250 = t.count("250")
rep("250", "251", None, "P3-self")
log.append(f"P3 consumed {n250} '250' substrings")

# ============ P4: upstream shift 249 -> 250 ============
n249 = t.count("249")
rep("249", "250", None, "P4-upstream")
log.append(f"P4 consumed {n249} '249' substrings")

# ============ P5a: numeric/anchor/ordinal/window faces (post-blanket forms) ============
rep("972_135", "974_335", 1, "P5a-ledger-int")
rep("545_720", "547_920", 1, "P5a-k-int")
rep("972,135", "974,335", 8, "P5a-ledger-prose")
rep("545,720", "547,920", 8, "P5a-k-prose")
rep("THIRTEENTH consecutive", "FOURTEENTH consecutive", 13, "P5a-seedgap")
rep("thirteenth consecutive", "fourteenth consecutive", 2, "P5a-seedgap-lc")
rep("face THIRTEENTH;", "face FOURTEENTH;", 1, "P5a-gapface-semi")
rep("MSG-20261016-055x-bmc-w251-seat", "MSG-20261016-085x-bmc-w251-seat", 7, "P5a-seat-msg")
rep("cc06f1f4a", "bc3b2b693", 2, "P5a-seat-origin")
rep("4f7a130ff", "9f5f106d6", 1, "P5a-prereg-commit")
rep("bmc_ordinal=70", "bmc_ordinal=71", 7, "P5a-ordinal70")
rep("thirty-eighth consecutive", "thirty-ninth consecutive", 2, "P5a-finface")
rep("SEVENTIETH", "SEVENTY-FIRST", 3, "P5a-seventieth")
rep("TWO HUNDRED AND FIFTIETH", "TWO HUNDRED AND FIFTY-FIRST", 3, "P5a-250th")
# r-window faces: upstream W250 chain = splice r1046 window + finalize r1046;
# W251 prereg derive window = r1047; this freeze window = r1048.
rep("W250 finalize one-pass bm-c r1043 window closeout 05:5x",
    "W250 finalize one-pass bm-c r1046 window closeout 08:3x", 1, "P5a-closeout-window")
rep("2026-10-16 07:5x bm-c r1046 freeze window", "2026-10-16 09:2x bm-c r1048 freeze window", 1, "P5a-header-window")
rep("r1042 splice window", "r1046 splice window", 3, "P5a-splice-window")
rep("r1042", "r1046", 6, "P5a-splice-window-rest")
rep("r1043", "r1046", 13, "P5a-finalize-window")
rep("r1045", "r1047", 7, "P5a-prereg-window")
rep("authored 07:2x", "authored 09:0x", 2, "P5a-authored-time")
# aging-face needle heals (same-window disclosed, r1045/r1047 precedent family):
rep("wave 245 = first free number after the", "wave 251 = first free number after the", 1, "P5a-aging-wave245")
rep("transitive window W235..W244 checked", "transitive window W238..W247 checked", 1, "P5a-aging-deps-cmt")

# ============ P5b: structural wave-identity fixes (post-blanket, E63-immune) ============
rep("== list(range(233, 250))", "== list(range(234, 250))", 1, "P5b-legs-range")
rep("legs segment not W233..W248 sixteen legs", "legs segment not W234..W249 sixteen legs", 1, "P5b-legs-err")
rep('!= 107 (91 estate + W233..W248 legs 16)', '!= 108 (92 estate + W234..W249 legs 16)', 1, "P5b-parfull-fstr")
rep("== list(range(238, 250))", "== list(range(239, 250))", 1, "P5b-dropped-range")
rep("dropped segment not W238..W248 eleven legs", "dropped segment not W239..W249 eleven legs", 1, "P5b-dropped-err")
rep('m233 = re.search(r" *assert pf\\.N1_BANDS\\[233\\] ==", par_full)',
    'm234 = re.search(r" *assert pf\\.N1_BANDS\\[234\\] ==", par_full)', 1, "P5b-m234-def")
rep('assert m233, "upstream W233 row leg not found inside W250 parity span"',
    'assert m234, "upstream W234 row leg not found inside W250 parity span"', 1, "P5b-m234-assert")
rep("par_sec = par_full[:m233.start()]", "par_sec = par_full[:m234.start()]", 1, "P5b-m234-parsec")
rep("legs_sec = par_full[m233.start():]", "legs_sec = par_full[m234.start():]", 1, "P5b-m234-legssec")
rep('m238 = re.search(r" *assert pf\\.N1_BANDS\\[238\\] ==", legs_sec)',
    'm239 = re.search(r" *assert pf\\.N1_BANDS\\[239\\] ==", legs_sec)', 1, "P5b-m239-def")
rep('assert m238, "W238 leg boundary not found inside W251 legs segment (prereg sec.3 split face)"',
    'assert m239, "W239 leg boundary not found inside W251 legs segment (prereg sec.3 split face)"', 1, "P5b-m239-assert")
rep("legs_kept = legs_sec[:m238.start()]", "legs_kept = legs_sec[:m239.start()]", 1, "P5b-m239-kept")
rep("legs_dropped = legs_sec[m238.start():]", "legs_dropped = legs_sec[m239.start():]", 1, "P5b-m239-dropped")
rep("# prereg sec.3 mandate split: keep W233..W237 verbatim (5 legs); the W250",
    "# prereg sec.3 mandate split: keep W234..W238 verbatim (5 legs); the W250", 1, "P5b-split-cmt1")
rep("# block's own W238..W248 legs (11) are excluded from the estate path",
    "# block's own W239..W249 legs (11) are excluded from the estate path", 1, "P5b-split-cmt2")
# inline extraction comment
rep("# STRUCTURAL CHOICE (frozen W251 prereg sec.3 mandate): extract the 91-row",
    "# STRUCTURAL CHOICE (frozen W251 prereg sec.3 mandate): extract the 92-row", 1, "P5b-ext-91")
rep("# estate (W138..W206 full-span 69 rows + W211..W232 legs) AND the W233..W237",
    "# estate (W138..W206 full-span 69 rows + W211..W233 legs) AND the W234..W238", 1, "P5b-ext-estate")
rep("# W238..W248 legs (11) are EXCLUDED from the estate path per the prereg",
    "# W239..W249 legs (11) are EXCLUDED from the estate path per the prereg", 1, "P5b-ext-dropped")
rep("# mandate; the W251 block appends fresh W238..W250 legs (12, machine-derived",
    "# mandate; the W251 block appends fresh W239..W250 legs (12, machine-derived", 1, "P5b-ext-fresh")
rep("# from the LIVE pf registry at freeze time) -> 108 parity rows.",
    "# from the LIVE pf registry at freeze time) -> 109 parity rows.", 1, "P5b-ext-parity")
# header parity block
rep("# block's own W238..W248 legs (11 rows) do NOT enter the estate path;",
    "# block's own W239..W249 legs (11 rows) do NOT enter the estate path;", 1, "P5b-hdr-dropped")
rep("# after extraction, fresh W238..W250 legs (12 rows) are added,",
    "# after extraction, fresh W239..W250 legs (12 rows) are added,", 1, "P5b-hdr-fresh")
rep("# parity = 108 rows (W138..W206 + W211..W250). Zero assumption zero risk.",
    "# parity = 109 rows (W138..W206 + W211..W250). Zero assumption zero risk.", 1, "P5b-hdr-parity")
# emitted materializer hdr parity lines
rep('"    #     estate 91 rows (W138..W206 full-span 69 + W211..W232 legs) +",',
    '"    #     estate 92 rows (W138..W206 full-span 69 + W211..W233 legs) +",', 1, "P5b-emit-estate")
rep('"    #     W233..W237 legs (5) extracted verbatim from the OWN W250 block",',
    '"    #     W234..W238 legs (5) extracted verbatim from the OWN W250 block",', 1, "P5b-emit-kept")
rep('"    #     physical bytes; the W250 block\'s own W238..W248 legs (11) are",',
    '"    #     physical bytes; the W250 block\'s own W239..W249 legs (11) are",', 1, "P5b-emit-dropped")
rep('"    #     W238..W250 legs (12) added, machine-derived from the live pf",',
    '"    #     W239..W250 legs (12) added, machine-derived from the live pf",', 1, "P5b-emit-fresh")
rep('"    #     registry at freeze time -> 108 parity rows (W138..W206+W211..W250).",',
    '"    #     registry at freeze time -> 109 parity rows (W138..W206+W211..W250).",', 1, "P5b-emit-parity")
# receipt parity note
rep("+ W211..W232 legs (estate 91) + W233..W237 legs extracted verbatim (5) per the frozen",
    "+ W211..W233 legs (estate 92) + W234..W238 legs extracted verbatim (5) per the frozen", 1, "P5b-rcpt-estate")
rep("the W250 block's own W238..W248 legs (11) EXCLUDED",
    "the W250 block's own W239..W249 legs (11) EXCLUDED", 1, "P5b-rcpt-dropped")
rep("fresh W238..W250 legs (12) machine-derived", "fresh W239..W250 legs (12) machine-derived", 1, "P5b-rcpt-fresh")
rep("-> W251 block = 108 rows (W138..W206 + W211..W250); disclosed:",
    "-> W251 block = 109 rows (W138..W206 + W211..W250); disclosed:", 1, "P5b-rcpt-total")

# ============ P5c: band literals (probe ADMIT receipt bands) ============
rep('assert (a_lo, a_hi) == (565_501, 567_500) and (b_lo, b_hi) == (545_101, 545_300), \\',
    'assert (a_lo, a_hi) == (567_501, 569_500) and (b_lo, b_hi) == (569_501, 569_700), \\', 1, "P5c-band-drift")

# ============ P5d: ordinal/leg0/deps faces ============
rep('assert len(owner_rows_live) == 239 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 69, \\',
    'assert len(owner_rows_live) == 240 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 70, \\', 1, "P5d-ord-gate")
rep("(expect 239/129/69 PRE-splice post-W250 registration; this candidate = bm-c's 70th own wave per the same live-derive law, r587/r359)",
    "(expect 240/129/70 PRE-splice post-W250 registration; this candidate = bm-c's 71st own wave per the same live-derive law, r587/r359)", 1, "P5d-ord-err")
rep('# receipt leg0 face owner_rows=239 / bmc_rows=69 / bmc_ordinal=71',
    '# receipt leg0 face owner_rows=240 / bmc_rows=70 / bmc_ordinal=71', 1, "P5d-leg0-prose")
rep("-> owner rows 239 + candidate = 240th EXACT; bm-c rows 69 +",
    "-> owner rows 240 + candidate = 241st EXACT; bm-c rows 70 +", 1, "P5d-ord-owner-prose")
rep("# candidate = 70th EXACT -- bm-c own-seat continuity face (bm-c published the",
    "# candidate = 71st EXACT -- bm-c own-seat continuity face (bm-c published the", 1, "P5d-ord-bmc-prose")
rep("freeze-time live face owner rows 239 + candidate = 240th EXACT",
    "freeze-time live face owner rows 240 + candidate = 241st EXACT", 1, "P5d-rcpt-239th")
rep("freeze-time live derive bmc rows 69 + candidate 70th EXACT per r587/r359",
    "freeze-time live derive bmc rows 70 + candidate 71st EXACT per r587/r359", 1, "P5d-bundle-70th")
rep("post-W250 registration: bm-c rows 69 + candidate = 70th owned",
    "post-W250 registration: bm-c rows 70 + candidate = 71st owned", 1, "P5d-rcpt-70th")
rep("70th own wave", "71st own wave", 2, "P5d-70th-ownwave")
rep('"probe_receipt_bmc_ordinal_face": 70,', '"probe_receipt_bmc_ordinal_face": 71,', 1, "P5d-rcpt-ordface")
rep('f"W250+W245..W236 finalize products present "', 'f"W250+W246..W237 finalize products present "', 1, "P5d-print-deps")
rep("W248_W250_bands_respected", "W249_W250_bands_respected", 2, "P5d-rsv-keys")

# ============ P5e: B-face structural rewrite (13-HOP WALK above own-A) ============
# header NEW FACE block
chunk(
"""# NEW FACE vs the W249 editor (honest disclosure, frozen W250 prereg sec.3
# mandate): BOTH bands take the CLEAN-hops=0 face -- A = FIRST-CLEAN
# arithmetic continuation of the prior-wave A tail (565_501..567_500, naive
# start CLEAN on the post-W249-REGISTERED universe, hops=0, A_hop_chain
# empty + A_clean_at_naive_start=true, seed-decoupled A-continuation face,
# THIRTEENTH consecutive seed-gap face, anticipated by the W249 probe leg4 +
# seat leg4 and confirmed live); B = CLEAN arithmetic continuation of the
# prior-wave B tail (545_101..545_300, hops=0, B_naive_hops=0, B_hop_chain
# empty + B_clean_at_naive_start=true, past the W239 staircase band-hop
# landing -- the registered W239 A band 542_501..544_500 and the registered
# W247/W248/W249 B bands all sit below the walk start; B lands
# OUTSIDE the own-A window 565_501..567_500; B base == prior-wave B tail+1
# (545_100+1) EXACT; B_no_ownA_jump=true; B_hop_lands_inside_A=false).""",
"""# NEW FACE vs the W250 editor (honest disclosure, frozen W251 prereg sec.3
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
# B_lands_above_own_A=true; B_hop_lands_inside_A=false; hops=13).""", "P5e-hdr")

# band facts comment block
chunk(
"""# W250 FACE (probe receipt leg1 relation_asserts):
# A keeps the A-continuation base (prior-wave A tail+1 EXACT -- the naive
# arithmetic continuation is CLEAN at its own start, hops=0, A_hop_chain
# empty, A_clean_at_naive_start=true -- thirteenth consecutive seed-gap face per
# the W249 probe leg4 + seat leg4 anticipation confirmed live, frozen receipt
# A_semantics verbatim); B takes the CLEAN arithmetic continuation face
# (prior-wave B tail+1 EXACT, hops=0, B_naive_hops=0, B_hop_chain empty,
# B_clean_at_naive_start=true, past the W239 staircase band-hop landing; the
# registered W239 A band and the registered W247/W248/W249 B bands all sit below the
# walk start); A sits far above the B staircase (seed-decoupled A/B gap,
# thirteenth consecutive); machine-derived from the LIVE registered row, never
# transcribed.""",
"""# W251 FACE (probe receipt leg1 relation_asserts):
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
# transcribed.""", "P5e-bandfacts")

# band-facts assert lines (B face)
rep('assert leg1.get("hops_B") == 0, "B hop-count drift vs probe receipt leg1 (B band hops=0, CLEAN arithmetic continuation face)"',
    'assert leg1.get("hops_B") == 13, "B hop-count drift vs probe receipt leg1 (B band hops=13, 13-hop walk face above own-A)"', 1, "P5e-hopsB")
rep('assert leg1.get("B_hop_chain") == [] and leg1.get("B_naive_hops") == 0, \\\n    "B hop-chain face drift (hops=0, CLEAN arithmetic continuation face -- no band-hop this wave)"',
    'assert len(leg1.get("B_hop_chain") or []) == 13 and leg1.get("B_naive_refused_at_start") is True, \\\n    "B hop-chain face drift (hops=13 walk face -- naive continuation REFUSED at start, B_naive_refused_at_start=true; B_hop_chain verbatim in the probe receipt)"', 1, "P5e-hopchain")
rep('assert leg1.get("B_naive_first_clean") == [b_lo, b_hi], "B naive first-clean drift vs probe receipt leg1"',
    'assert leg1.get("B_lands_above_own_A") is True and leg1.get("B_naive") == [w250_b_tail + 1, w250_b_tail + 200], "B lands-above-own-A + naive-window drift vs probe receipt leg1 (B_lands_above_own_A=true; B base == own-A tail+1 EXACT; naive window == prior-B tail+1..+200)"', 1, "P5e-aboveowna")
rep('and ra.get("B_clean_at_naive_start") and ra.get("B_base_above_W250_tail") \\',
    'and ra.get("B_clean_at_naive_start") is False and ra.get("B_base_above_W250_tail") \\', 1, "P5e-ra-bclean")
rep('assert b_hi < a_lo, "seed-decoupled A/B gap face violated: B window must sit entirely below own-A"',
    'assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 13-hop walk lands ABOVE own-A -- first since the W239 staircase era; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"', 1, "P5e-belowowna")

# pf_comment B lines
chunk(
'''"    # B = CLEAN arithmetic continuation of the prior-wave B tail",
"    # (" + fmt(w249_b_tail + 1) + ".." + fmt(w249_b_tail + 200) + ", hops=0, B_naive_hops=0, B_hop_chain empty +",
"    # B_clean_at_naive_start=true, past the W239 staircase band-hop landing; the",
"    # registered W239 A band " + fmt(pf_mod.N1_BANDS[239]["a"][0]) + ".." + fmt(pf_mod.N1_BANDS[239]["a"][1]) + " and the registered W247/W248/W249 B bands",
"    # " + fmt(W249["b_exit"][0]) + ".." + fmt(W249["b_exit"][1]) + " all sit below the walk start) -- B lands OUTSIDE",
"    # the own-A window " + fmt(a_lo) + ".." + fmt(a_hi) + ": seed-decoupled A/B gap face THIRTEENTH;",
"    # B base == prior-wave B tail+1 (" + fmt(w249_b_tail) + "+1) machine-checkable;",''',
'''"    # B = 13-HOP WALK above own-A (the naive continuation",
"    # " + fmt(w250_b_tail + 1) + ".." + fmt(w250_b_tail + 200) + " REFUSED at naive start -- SEED_REGISTRY seed 545_500 +",
"    # the W240..W249 A-ladder bands + W250-A + own-A reservation; hops=13,",
"    # B_hop_chain verbatim in the probe receipt; the walk hops past the",
"    # pre-W250 projected first-clean 565_501..565_700 (now INSIDE the registered W250 A band) AND",
"    # past the own-wave A window; B lands ABOVE own-A -- first since the W239 staircase",
"    # era; B base == own-A tail+1 (" + fmt(a_hi) + "+1) EXACT; B_lands_above_own_A=true;",
"    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)",''', "P5e-pfcmt")

# PRE block B lines
chunk(
''' "non-rotational r587 forward-monotone walk) + B = CLEAN arithmetic ",
 "continuation of the prior-wave B tail (the continuation ",
 f"{fmt(w249_b_tail + 1)}..{fmt(w249_b_tail + 200)} is CLEAN at its own start ",
 "-- hops=0, B_naive_hops=0, B_hop_chain empty + B_clean_at_naive_start=true, past the W239 ",
 f"staircase band-hop landing (the registered W239 A band {fmt(pf_mod.N1_BANDS[239]['a'][0])}..{fmt(pf_mod.N1_BANDS[239]['a'][1])} and the registered W247/W248/W249 B bands all sit below the walk start); B lands OUTSIDE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap ",
 "face THIRTEENTH consecutive; B base == prior-wave B tail+1 (",
 f"{fmt(w249_b_tail)}+1) machine-checkable; cross-window convergence with the W249 probe leg4 + seat leg4 succession projection ",''',
''' "non-rotational r587 forward-monotone walk) + B = 13-HOP WALK above own-A ",
 "(the naive continuation ",
 f"{fmt(w250_b_tail + 1)}..{fmt(w250_b_tail + 200)} is REFUSED at its own start ",
 "-- hops=13, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the ",
 f"walk hops past the W240..W249 A-ladder bands + W250-A + the own-wave A window (own-A reservation standard leg); B lands ABOVE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT; first above-own-A landing since the W239 ",
 "staircase era; B base == own-A tail+1 (",
 f"{fmt(a_hi)}+1) machine-checkable; cross-window convergence with the W250 prereg sec.5 item5 + W250 probe leg4 + seat leg4 succession projection ",''', "P5e-pre")

# tail band-facts comments (B lines)
chunk(
'''"        # B = CLEAN arithmetic continuation of the prior-wave B tail",
f"        # ({fmt(w249_b_tail + 1)}..{fmt(w249_b_tail + 200)} CLEAN at naive start, hops=0,",
"        # B_naive_hops=0, B_hop_chain empty + B_clean_at_naive_start=true,",
f"        # past the W239 staircase band-hop landing (the registered W239 A band {fmt(pf_mod.N1_BANDS[239]['a'][0])}..{fmt(pf_mod.N1_BANDS[239]['a'][1])}",
f"        # and the registered W247/W248/W249 B bands all sit below the walk start);",
"        # B lands OUTSIDE the own-A window",
f"        # {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap face THIRTEENTH consecutive;",
"        # B base == prior-wave B tail+1 EXACT",
"        # machine-checkable; B_hop_lands_inside_A=false;",
"        # B_no_ownA_jump=true; cross-window convergence with",
"        # the W249 probe leg4 + seat leg4 succession projection notes -- all",
"        # MANDATORY notes honored (post-W249 universe",
"        # re-derive + live-trace re-read, no staircase-equality assumption);"''',
'''"        # B = 13-HOP WALK above own-A (the naive continuation",
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
"        # re-derive + live-trace re-read, no staircase-equality assumption);"''', "P5e-tailcmt")

# tail assert block (B face) -- split into six exact-line reps (the closing
# "probe receipt leg1 mirrored exactly; B_hop_lands_inside_A=false" line is
# structurally unchanged and NOT re-emitted)
rep("f'        assert WAVE_CONFIGS[251][\"b_exit_seed_base\"] == {b_lo} == {w250_b_tail} + 1, ('",
    "f'        assert WAVE_CONFIGS[251][\"b_exit_seed_base\"] == {b_lo} == {a_hi} + 1, ('", 1, "P5e-tail-bassert1")
rep("'            \"W251 B CLEAN arithmetic continuation face: the naive continuation \"'",
    "'            \"W251 B 13-HOP WALK face: the naive continuation \"'", 1, "P5e-tail-bassert2")
rep("f'            \"{fmt(w250_b_tail + 1)}..{fmt(w250_b_tail + 200)} is CLEAN at its own start \"'",
    "f'            \"{fmt(w250_b_tail + 1)}..{fmt(w250_b_tail + 200)} is REFUSED at its own start \"'", 1, "P5e-tail-bassert3")
rep("'            \"(hops=0, B_naive_hops=0, B_hop_chain empty + B_clean_at_naive_start=true, \"'",
    "'            \"(hops=13, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; \"'", 1, "P5e-tail-bassert4")
rep("'            \"past the W239 staircase band-hop landing) -- B base == prior-wave B tail+1 \"'",
    "'            \"the walk hops past the W240..W249 A-ladder bands + W250-A + the own-wave A window) -- B base == own-A tail+1 \"'", 1, "P5e-tail-bassert5")
rep("'            \"EXACT (B_base_above_priorB_tail + B_no_ownA_jump face relation asserts, \"'",
    "'            \"EXACT (B_lands_above_own_A + B_base_above_W250_tail face relation asserts, \"'", 1, "P5e-tail-bassert6")
rep("'            \"W251 B clean-continuation base must sit above the prior-wave B tail\"'",
    "'            \"W251 B walk base must sit above the prior-wave B tail\"'", 1, "P5e-tail-bbase")
rep("'            \"W251 B window must be CLEAN (first-clean ADMIT face, clean arithmetic continuation)\"'",
    "'            \"W251 B window must be CLEAN (first-clean ADMIT face, 13-hop walk landing)\"'", 1, "P5e-tail-bclean")
rep("'            \"W251 A/B same-freeze mutual exclusion (seed-decoupled gap face inherited: B below own A)\"'",
    "'            \"W251 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- first since the W239 staircase era; zero overlap)\"'", 1, "P5e-tail-excl")

# pr (print) B lines
chunk(
''' '          "+ B=CLEAN arithmetic continuation of prior-wave B tail (hops=0, B_naive_hops=0, "',
 '          "B_hop_chain empty + B_clean_at_naive_start=true, past the W239 staircase landing, "',
 '          "B base == prior-B tail+1 EXACT, B_no_ownA_jump=true, "',
 '          "seed-decoupled A/B gap face THIRTEENTH consecutive), chain-order splice from the "''',
''' '          "+ B=13-HOP WALK above own-A (hops=13, B_naive_refused_at_start=true, "',
 '          "B_hop_chain verbatim, hops past the W240..W249 A-ladder + W250-A + own-A reservation, "',
 '          "B base == own-A tail+1 EXACT, B_lands_above_own_A=true, "',
 '          "first above-own-A landing since the W239 staircase era), chain-order splice from the "''', "P5e-pr")

# cfg MEM_I b_exit_seed_base comment line (B face)
chunk(
""" f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W250 B: {fmt(b_lo)}..{fmt(b_hi)} (CLEAN arithmetic continuation of the prior-wave B tail; {fmt(w249_b_tail + 1)}..{fmt(w249_b_tail + 200)} CLEAN at naive start hops=0, B_naive_hops=0, B_hop_chain empty + B_clean_at_naive_start=true; past the W239 staircase band-hop landing; B lands outside own-A; seed-decoupled A/B gap face THIRTEENTH consecutive; B base == prior-B tail+1)',""",
""" f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W251 B: {fmt(b_lo)}..{fmt(b_hi)} (13-HOP WALK above own-A; naive {fmt(w250_b_tail + 1)}..{fmt(w250_b_tail + 200)} REFUSED at start -- hops=13, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; hops past the W240..W249 A-ladder + W250-A + own-A reservation; B lands ABOVE own-A at tail+1 EXACT -- first since the W239 staircase era; B base == own-A tail+1)',""", "P5e-mem-b")

# receipt band_semantics B value (raw dict-literal text, post-blanket forms)
rep('"B": "CLEAN arithmetic continuation of prior-wave B tail (hops=0, B_naive_hops=0, B_hop_chain empty + B_clean_at_naive_start=true; past the W239 staircase band-hop landing -- the registered W239 A band 542_501..544_500 and the registered W247/W248/W250 B bands 544_501..544_700 + 544_701..544_900 + 544_901..545_100 all sit below the walk start; B_no_ownA_jump=true; B_hop_lands_inside_A=false; seed-decoupled A/B gap face FOURTEENTH consecutive; B base == prior-B tail+1 EXACT)"',
    '"B": "13-HOP WALK above own-A (hops=13, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the naive continuation 545_301..545_500 refused at start -- SEED_REGISTRY seed 545_500 + the W240..W249 A-ladder bands + W250-A + own-A reservation; the walk hops past the pre-W250 projected first-clean 565_501..565_700 (now INSIDE the registered W250 A band 565_501..567_500) and past the own-wave A window; B lands ABOVE own-A -- first above-own-A landing since the W239 staircase era; B_lands_above_own_A=true; B_hop_lands_inside_A=false; B base == own-A tail+1 (569_500+1) EXACT)"', 1, "P5e-rcpt-semantics")

# leg4 W252p projection faces (pf_comment + PRE + downstream_seat)
rep('"    # seed refusers) / B naive " + rec["legs"]["leg4"]["W252p_B_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " NOT clean at naive -- first-clean " + rec["legs"]["leg4"]["W252p_B_first_clean"] + ",",',
    '"    # seed refusers) / B naive " + rec["legs"]["leg4"]["W252p_B_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " CLEAN at naive -- first-clean " + rec["legs"]["leg4"]["W252p_B_first_clean"] + " BUT lands INSIDE the projection A window,",', 1, "P5e-pfcmt-leg4B")
rep('"    # lands OUTSIDE the projection A window;",',
    '"    # (W252p_B_lands_inside_W252p_A_naive=true -- staircase re-emergence face: the W252 walk MUST hop past own-A reservation);",', 1, "P5e-pfcmt-leg4C")
rep('"    # B_hop lands-inside-A=false leg present); W252 freezer MUST",',
    '"    # the W252 freezer MUST",', 1, "P5e-pfcmt-leg4D")
rep("f\"{rec['legs']['leg4']['W252p_B_naive']} hops={rec['legs']['leg4']['hops_B']} NOT clean at naive -- first-clean {rec['legs']['leg4']['W252p_B_first_clean']} (B_hop lands-inside-A=false leg present; seed-gap face \",",
    "f\"{rec['legs']['leg4']['W252p_B_naive']} hops={rec['legs']['leg4']['hops_B']} CLEAN at naive -- first-clean {rec['legs']['leg4']['W252p_B_first_clean']} BUT lands INSIDE the W252 projection A window (W252p_B_lands_inside_W252p_A_naive=true staircase re-emergence face; seed-gap face \",", 1, "P5e-pre-leg4B")
rep("W252p face per this window's probe leg4: A naive 567501..569500 CLEAN (hops=0, zero live refusers) / B naive 545301..545500 hops=11 NOT clean at naive, first-clean 565501..565700 (B_hop lands-inside-A=false leg present); seed-gap face inherited: W251 A/B decoupled, re-read the live trace at W252 derive time, do NOT assume the staircase A-base==prior-B-tail+1 equality",
    "W252p face per this window's probe leg4: A naive 569501..571500 CLEAN (hops=0, zero live refusers) / B naive 569701..569900 hops=0 CLEAN at naive, first-clean 569701..569900 BUT lands INSIDE the W252 projection A window (W252p_B_lands_inside_W252p_A_naive=true staircase re-emergence face: the W252 walk MUST hop past the own-A reservation); seed-gap face inherited: W251 A/B decoupled, re-read the live trace at W252 derive time, do NOT assume the staircase A-base==prior-B-tail+1 equality", 1, "P5e-rcpt-downstream")

# ============ structural output gates ============
for needle, want in [
    ("# --- W251 materializer face", 2),
    ("# --- W250 materializer face", 1),
    ('"+ W251 materializer face', 2),
    ("range(16, 251)", 2),
    ("range(17, 251)", 3),
    ("range(239, 251)", 2),
    ("range(234, 250)", 1),
    ("list(range(239, 250))", 1),
    ("range(209, 252)", 2),
    ("if w < 251)", 5),
    ("if w < 250)", 1),
    ("_w251bmc_20261016_probe_receipt.json", 10),
    ("_w251bmc_freeze_receipt.json", 1),
    ("MSG-20261016-085x-bmc-w251-seat", 7),
    ("bc3b2b693", 2),
    ("974_335", 1),
    ("547_920", 1),
    ("(567_501, 569_500)", 1),
    ("(569_501, 569_700)", 1),
    ('B_base_above_W250_tail', 2),
    ('W249_W250_bands_respected_A', 1),
    ('W249_W250_bands_respected_B', 1),
    ("W252p_A_naive", 5),
    ("W252p_B_first_clean", 2),
    ("arith_a251", 6),
    ("arith_b251", 6),
    ('"PERPETUAL-N1-W251-SHARD-0"', None),
    ('n1_w251_results.json', None),
    ("FOURTEENTH consecutive", 8),
    ("fourteenth consecutive", 2),
    ("SEVENTY-FIRST", 3),
    ("TWO HUNDRED AND FIFTY-FIRST", 3),
    ("thirty-ninth consecutive", 2),
    ("bmc_ordinal=71", 7),
    ("r1046 splice window", 3),
    ("r1047", 7),
    ("r1048 freeze window", 1),
    ("hops=13", None),
    ("13-HOP WALK", None),
    # anti-gates: stale faces must be zero
    ("r1042", 0),
    ("r1043", 0),
    ("r1045", 0),
    ("4f7a130ff", 0),
    ("cc06f1f4a", 0),
    ("972,135", 0),
    ("545,720", 0),
    ("972_135", 0),
    ("545_720", 0),
    ("THIRTEENTH", 0),
    ("thirteenth", 0),
    ("W248_W250_bands_respected", 0),
    ("W248_W249_bands_respected", 0),
    ("MSG-20261016-055x", 0),
    ("bmc_ordinal=70", 0),
    ("70th", 0),
    ("69th", 0),
    ("240th", 0),
    ("239/129/69", 0),
    ("thirty-eighth", 0),
    ("B_naive_hops", 0),
    ("B_naive_first_clean", 0),
    ("B_no_ownA_jump", 0),
    ("B_clean_at_naive_start=true", 0),
    ("hops=0, B_naive_hops", 0),
    ("B = CLEAN arithmetic", 0),
    ("CLEAN arithmetic continuation of prior-wave B tail", 0),
    ("CLEAN arithmetic continuation face", 0),
    ("CLEAN arithmetic continuation of the prior-wave B tail", 0),
    ("B lands OUTSIDE", 0),
    ("(565_501, 567_500)", 0),
    ("(545_101, 545_300)", 0),
    ("wave 245", 0),
    ("W235..W244", 0),
    ("r1036", 0),
    ("r1030", 0),
    ("r1040-dead", 0),
    ("20261015_probe_receipt", 0),
    ("07:5x", 0),
    ("05:5x", 0),
    ("estate 91", 0),
    ("108 parity", 0),
    ("108 rows", 0),
    ("== 107", 0),
]:
    n = t.count(needle)
    if want is not None:
        assert n == want, f"OUTPUT-GATE {needle!r}: {n} != {want}"
    log.append(f"OUT {needle!r} = {n}")

io.open(DST, "w", encoding="utf-8", newline="").write(t)
import py_compile
py_compile.compile(DST, doraise=True)
io.open(os.path.join(REPO, "results", "_w251bmc_derive_editor_log.txt"), "w",
        encoding="utf-8").write("\n".join(log))
print(f"DERIVE OK -> {DST} ({len(t)} chars); {len(log)} transform log rows")
print("\n".join(log[-14:]))
