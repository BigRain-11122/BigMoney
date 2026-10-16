# -*- coding: utf-8 -*-
# r1046 bm-c: derive results/_w250bmc_freeze_edits.py from the committed W249
# editor (results/_w249bmc_freeze_edits.py, proven live-fire W249 splice bm-c
# r1042 window) via COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage).
# E63 3rd-GEN PREVENTION (vs the r1042 2nd-instance heal): pass ordering
# redesigned -- P1 structural outputs are BLANKET-IMMUNE (no '249'/'248'/'W250'
# substrings inside any P1 replacement), and the legs/dropped wave-identity
# asserts are fixed POST-BLANKET (P5b) so no blanket can corrupt them.
# Receipt keys are read from the actual results/_w250bmc_20261016_probe_receipt.json
# faces (never transcribed). W250 facts: bands A 565_501..567_500 / B 545_101..545_300,
# upstream W249 = bm-c own chain (r1042 splice 5d4aeec59 + r1043 finalize ledger
# 972,135 / K=545,720), seat MSG-20261016-055x-bmc-w250-seat @ origin cc06f1f4a r1043,
# prereg 4f7a130ff derived bm-c r1045, parity estate 91 + kept W233..W237 (5) +
# dropped W238..W248 (11) + fresh W238..W249 (12) = 108 rows, THIRTEENTH seed-gap.
import io, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w249bmc_freeze_edits.py")
DST = os.path.join(REPO, "results", "_w250bmc_freeze_edits.py")

t = io.open(SRC, encoding="utf-8").read()
log = []

def rep(old, new, expect=None, tag=""):
    global t
    n = t.count(old)
    if expect is not None:
        assert n == expect, f"[{tag}] count {n} != {expect} for: {old[:70]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x {old[:48]!r}")

# ============ P1: structural faces, BLANKET-IMMUNE outputs ============
rep("(245, 244, 243, 242, 241, 240, 239, 238, 237, 236)",
    "(246, 245, 244, 243, 242, 241, 240, 239, 238, 237)", 2, "P1-transitive-deps")
rep("range(209, 250)", "range(209, 251)", 2, "P1-liveness-range")
rep("[232, 233, 234, 235, 236]", "[233, 234, 235, 236, 237]", 1, "P1-kept-list")
rep("range(237, 249)", "range(238, 250)", 2, "P1-fresh/legcount-loop")
rep("kept segment not W232..W236 five legs", "kept segment not W233..W237 five legs", 1, "P1-kept-err")
rep("assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[237] == {\"a\": (')",
    "assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[238] == {\"a\": (')", 1, "P1-fresh-firstline")
rep('assert par_sec.count("assert pf.N1_BANDS[") == 90 \\',
    'assert par_sec.count("assert pf.N1_BANDS[") == 91 \\', 1, "P1-estate-count")
rep('    and int(_estate_ws[89]) == 231, \\',
    '    and int(_estate_ws[89]) == 231 \\\n    and int(_estate_ws[90]) == 232, \\', 1, "P1-estate-decomp")
rep("estate segment not W138..W206 full-span 69 rows + W211..W230 legs + W231 leg:",
    "estate segment not W138..W206 full-span 69 rows + W211..W231 legs + W232 leg:", 1, "P1-estate-err")
rep('assert par_full.count("assert pf.N1_BANDS[") == 106, \\',
    'assert par_full.count("assert pf.N1_BANDS[") == 107, \\', 1, "P1-parfull-count")
rep('def fmt(n):  # 563501 -> "563_501"', 'def fmt(n):  # 565501 -> "565_501"', 1, "P1-fmt-comment")

# ============ P2: downstream shift W250 -> W251 (incl. W250p_* receipt keys) ============
rep("W250", "W251", None, "P2-downstream")
assert "W250" not in t, "P2 leftover W250"

# ============ P3: self shift 249 -> 250 (catches W249 + bare) ============
n249 = t.count("249")
rep("249", "250", None, "P3-self")
log.append(f"P3 consumed {n249} '249' substrings")

# ============ P4: upstream shift 248 -> 249 ============
n248 = t.count("248")
rep("248", "249", None, "P4-upstream")
log.append(f"P4 consumed {n248} '248' substrings")

# ============ P5a: numeric/anchor blanket reps (post-blanket forms) ============
rep("969_935", "972_135", 1, "P5a-ledger-int")
rep("543_520", "545_720", 1, "P5a-k-int")
rep("969,935", "972,135", 8, "P5a-ledger-prose")
rep("543,520", "545,720", 8, "P5a-k-prose")
rep("TWELFTH consecutive", "THIRTEENTH consecutive", 13, "P5a-seedgap")
rep("tenth consecutive seed-gap face per", "thirteenth consecutive seed-gap face per", 1, "P5a-seedgap-lc1")
rep("(seed-decoupled A/B gap,\n# tenth consecutive); machine-derived", "(seed-decoupled A/B gap,\n# thirteenth consecutive); machine-derived", 1, "P5a-seedgap-lc2")
rep("seed-decoupled A/B gap face tenth;", "seed-decoupled A/B gap face THIRTEENTH;", 1, "P5a-gapface-tenth")
rep("MSG-20261015-225x-bmc-w250-seat", "MSG-20261016-055x-bmc-w250-seat", 7, "P5a-seat-msg")
rep("8949e0aef", "cc06f1f4a", 2, "P5a-seat-origin")
rep("bmc_ordinal=69", "bmc_ordinal=70", 7, "P5a-ordinal69")
rep("_w250bmc_20261015", "_w250bmc_20261016", 10, "P5a-receipt-date")
rep("thirty-seventh consecutive fully-clean freeze window", "thirty-eighth consecutive fully-clean freeze window", 1, "P5a-finface")
rep("clean-precondition thirty-seventh consecutive window", "clean-precondition thirty-eighth consecutive window", 1, "P5a-prereg-note")
rep("SIXTY-NINTH", "SEVENTIETH", 3, "P5a-sixtyninth")
rep("TWO HUNDRED AND FORTY-NINTH", "TWO HUNDRED AND FIFTIETH", 3, "P5a-249th")

# ============ P5b: structural wave-identity fixes (post-blanket, E63-immune) ============
rep("== list(range(232, 249))", "== list(range(233, 249))", 1, "P5b-legs-range")
rep("legs segment not W232..W247 sixteen legs", "legs segment not W233..W248 sixteen legs", 1, "P5b-legs-err")
rep("!= 106 (90 estate + W232..W247 legs 16)", "!= 107 (91 estate + W233..W248 legs 16)", 1, "P5b-parfull-fstr")
rep("== list(range(237, 249))", "== list(range(238, 249))", 1, "P5b-dropped-range")
rep("dropped segment not W237..W247 eleven legs", "dropped segment not W238..W248 eleven legs", 1, "P5b-dropped-err")
rep('m232 = re.search(r" *assert pf\\.N1_BANDS\\[232\\] ==", par_full)',
    'm233 = re.search(r" *assert pf\\.N1_BANDS\\[233\\] ==", par_full)', 1, "P5b-m233-def")
rep('assert m232, "upstream W232 row leg not found inside W249 parity span"',
    'assert m233, "upstream W233 row leg not found inside W249 parity span"', 1, "P5b-m233-assert")
rep("par_sec = par_full[:m232.start()]", "par_sec = par_full[:m233.start()]", 1, "P5b-m233-parsec")
rep("legs_sec = par_full[m232.start():]", "legs_sec = par_full[m233.start():]", 1, "P5b-m233-legssec")
rep('m237 = re.search(r" *assert pf\\.N1_BANDS\\[237\\] ==", legs_sec)',
    'm238 = re.search(r" *assert pf\\.N1_BANDS\\[238\\] ==", legs_sec)', 1, "P5b-m238-def")
rep('assert m237, "W237 leg boundary not found inside W250 legs segment (prereg sec.3 split face)"',
    'assert m238, "W238 leg boundary not found inside W250 legs segment (prereg sec.3 split face)"', 1, "P5b-m238-assert")
rep("legs_kept = legs_sec[:m237.start()]", "legs_kept = legs_sec[:m238.start()]", 1, "P5b-m238-kept")
rep("legs_dropped = legs_sec[m237.start():]", "legs_dropped = legs_sec[m238.start():]", 1, "P5b-m238-dropped")
rep("# prereg sec.3 mandate split: keep W232..W236 verbatim (5 legs); the W249",
    "# prereg sec.3 mandate split: keep W233..W237 verbatim (5 legs); the W249", 1, "P5b-split-cmt1")
rep("# block's own W237..W247 legs (11) are excluded from the estate path",
    "# block's own W238..W248 legs (11) are excluded from the estate path", 1, "P5b-split-cmt2")

# extraction comment block
rep("# STRUCTURAL CHOICE (frozen W250 prereg sec.3 mandate): extract the 90-row",
    "# STRUCTURAL CHOICE (frozen W250 prereg sec.3 mandate): extract the 91-row", 1, "P5b-ext-90")
rep("# estate (W138..W206 full-span 69 rows + W211..W231 legs) AND the W232..W236",
    "# estate (W138..W206 full-span 69 rows + W211..W232 legs) AND the W233..W237", 1, "P5b-ext-estate")
rep("# legs (4) from the OWN W249 block physical bytes (bm-c r1036 splice",
    "# legs (5) from the OWN W249 block physical bytes (bm-c r1042 splice", 1, "P5b-ext-kept")
rep("# W237..W247 legs (11) are EXCLUDED from the estate path per the prereg",
    "# W238..W248 legs (11) are EXCLUDED from the estate path per the prereg", 1, "P5b-ext-dropped")
rep("# mandate; the W250 block appends fresh W237..W249 legs (12, machine-derived",
    "# mandate; the W250 block appends fresh W238..W249 legs (12, machine-derived", 1, "P5b-ext-fresh")
rep("# from the LIVE pf registry at freeze time) -> 107 parity rows.",
    "# from the LIVE pf registry at freeze time) -> 108 parity rows.", 1, "P5b-ext-parity")

# header parity block
rep("the W249\n# block's own W237..W247 legs (11 rows) do NOT enter the estate path;",
    "the W249\n# block's own W238..W248 legs (11 rows) do NOT enter the estate path;", 1, "P5b-hdr-dropped")
rep("# after extraction, fresh W237..W249 legs (12 rows) are added,",
    "# after extraction, fresh W238..W249 legs (12 rows) are added,", 1, "P5b-hdr-fresh")
rep("# parity = 107 rows (W138..W206 + W211..W249). Zero assumption zero risk.",
    "# parity = 108 rows (W138..W206 + W211..W249). Zero assumption zero risk.", 1, "P5b-hdr-parity")

# emitted materializer hdr parity lines
rep('"    #     estate 90 rows (W138..W206 full-span 69 + W211..W231 legs) +",',
    '"    #     estate 91 rows (W138..W206 full-span 69 + W211..W232 legs) +",', 1, "P5b-emit-estate")
rep('"    #     W232..W236 legs (5) extracted verbatim from the OWN W250 block",',
    '"    #     W233..W237 legs (5) extracted verbatim from the OWN W249 block",', 1, "P5b-emit-kept")
rep('"    #     physical bytes; the W249 block\'s own W237..W247 legs (11) are",',
    '"    #     physical bytes; the W249 block\'s own W238..W248 legs (11) are",', 1, "P5b-emit-dropped")
rep('"    #     W237..W249 legs (12) added, machine-derived from the live pf",',
    '"    #     W238..W249 legs (12) added, machine-derived from the live pf",', 1, "P5b-emit-fresh")
rep('"    #     registry at freeze time -> 107 parity rows (W138..W206+W211..W249).",',
    '"    #     registry at freeze time -> 108 parity rows (W138..W206+W211..W249).",', 1, "P5b-emit-parity")

# receipt parity note
rep("+ W211..W231 legs (estate 90) + W232..W236 legs extracted verbatim (5) per the frozen",
    "+ W211..W232 legs (estate 91) + W233..W237 legs extracted verbatim (5) per the frozen", 1, "P5b-rcpt-estate")
rep("the W249 block's own W237..W247 legs (11) EXCLUDED",
    "the W249 block's own W238..W248 legs (11) EXCLUDED", 1, "P5b-rcpt-dropped")
rep("fresh W237..W249 legs (12) machine-derived", "fresh W238..W249 legs (12) machine-derived", 1, "P5b-rcpt-fresh")
rep("-> W250 block = 107 rows (W138..W206 + W211..W249); disclosed:",
    "-> W250 block = 108 rows (W138..W206 + W211..W249); disclosed:", 1, "P5b-rcpt-total")
rep("(d) E63 heal 2nd instance this window: derived legs/dropped wave-identity asserts carried endpoint +2 (range(232,250)/range(237,250)) instead of the live-structure +1 (range(232,249)/range(237,249)) -- healed against machine-verified live block (106 rows, legs W232..W247) before splice, zero splice executed pre-heal",
    "(d) E63 3rd-gen prevention this window: the W250 derive editor reordered passes so P1 structural outputs are blanket-immune and the legs/dropped wave-identity asserts are fixed post-blanket (range(233,249)/range(238,249) live-structure exact) -- zero heal needed, zero splice executed pre-verify", 1, "P5b-e63-note")
rep('"OWN W249 block physical bytes (bm-c splice generation r1036 absorb window, structure known exactly)"',
    '"OWN W249 block physical bytes (bm-c splice generation r1042 window, structure known exactly)"', 1, "P5b-rcpt-source")

# ============ P5c: band literals + staircase faces ============
rep("assert (a_lo, a_hi) == (563_501, 565_500) and (b_lo, b_hi) == (544_901, 545_100), \\",
    "assert (a_lo, a_hi) == (565_501, 567_500) and (b_lo, b_hi) == (545_101, 545_300), \\", 1, "P5c-band-drift")
rep("# arithmetic continuation of the prior-wave A tail (563_501..565_500, naive",
    "# arithmetic continuation of the prior-wave A tail (565_501..567_500, naive", 1, "P5c-band-ahdr")
rep("prior-wave B tail (544_901..545_100, hops=0, B_naive_hops=0, B_hop_chain",
    "prior-wave B tail (545_101..545_300, hops=0, B_naive_hops=0, B_hop_chain", 1, "P5c-band-bhdr")
rep("# OUTSIDE the own-A window 563_501..565_500; B base == prior-wave B tail+1",
    "# OUTSIDE the own-A window 565_501..567_500; B base == prior-wave B tail+1", 1, "P5c-band-owna")
rep("# (544_700+1) EXACT; B_no_ownA_jump=true; B_hop_lands_inside_A=false).",
    "# (545_100+1) EXACT; B_no_ownA_jump=true; B_hop_lands_inside_A=false).", 1, "P5c-band-bbase")
rep("# W249 B band 544_501..544_700 both sit below the walk start; B lands",
    "# W247/W248/W249 B bands all sit below the walk start; B lands", 1, "P5c-hdr-staircase")
rep("# registered W239 A band and the registered W249 B band both sit below the",
    "# registered W239 A band and the registered W247/W248/W249 B bands all sit below the", 1, "P5c-leg1-staircase")
rep('and the registered W249 B band",', 'and the registered W247/W248/W249 B bands",', 1, "P5c-pfcmt-staircase")
rep(' + " both sit below the walk start) -- B lands OUTSIDE",', ' + " all sit below the walk start) -- B lands OUTSIDE",', 1, "P5c-pfcmt-bothall")
rep("the registered W247/W249 B bands 544_501..544_700 + 544_701..544_900 all sit below the walk start",
    "the registered W247/W248/W249 B bands 544_501..544_700 + 544_701..544_900 + 544_901..545_100 all sit below the walk start", 1, "P5c-rcpt-staircase")
rep("and the registered W249 B band {fmt(W249['b_exit'][0])}..{fmt(W249['b_exit'][1])} both sit below the walk start);",
    "and the registered W247/W248/W249 B bands all sit below the walk start);", 2, "P5c-fstr-staircase")

# ============ P5d: receipt relation keys + ordinals + seat/window faces ============
rep("W247_W249_bands_respected", "W248_W249_bands_respected", 2, "P5d-rsv-keys")
rep("== 238 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 68",
    "== 239 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 69", 1, "P5d-ord-gate")
rep("(expect 238/129/68 PRE-splice post-W249 registration; this candidate = bm-c's 69th own wave per the same live-derive law, r587/r359)",
    "(expect 239/129/69 PRE-splice post-W249 registration; this candidate = bm-c's 70th own wave per the same live-derive law, r587/r359)", 1, "P5d-ord-err")
rep("# receipt leg0 face owner_rows=236 / bmc_rows=67 / bmc_ordinal=70",
    "# receipt leg0 face owner_rows=239 / bmc_rows=69 / bmc_ordinal=70", 1, "P5d-leg0-prose")
rep("# = seat-time PRE-W250-splice live faces (post-W246-REGISTERED universe with",
    "# = seat-time PRE-W250-splice live faces (post-W249-REGISTERED universe,", 1, "P5d-leg0-universe")
rep("# the W249 seat in-flight); live derive at freeze time:",
    "# upstream complete -- queue-head supply); live derive at freeze time:", 1, "P5d-leg0-inflight")
rep("# W249 splice LANDED (finalize adds no registry rows) -> owner rows 238 + candidate = 238th EXACT; bm-c rows 67 +",
    "# W249 splice LANDED (finalize adds no registry rows) -> owner rows 239 + candidate = 240th EXACT; bm-c rows 69 +", 1, "P5d-ord-owner-prose")
rep("# candidate = 68th EXACT -- bm-c own-seat continuity face (bm-c published the",
    "# candidate = 70th EXACT -- bm-c own-seat continuity face (bm-c published the", 1, "P5d-ord-bmc-prose")
rep("# W250 seat itself r1030; waits-upstream ARMED lane disarmed by the W249 chain",
    "# W250 seat itself r1043; queue-head supply -- W249 chain complete at publish, ZERO", 1, "P5d-seat-lane")
rep("# landing bm-c r1036)", "# waits-upstream face (bm-c r1042 splice + r1043 finalize))", 1, "P5d-seat-lane2")
rep('waits-upstream DISARMED face), "', 'queue-head supply, ZERO waits-upstream face), "', 1, "P5d-print-lane")
rep('f"W249+W244..W235 finalize products present "', 'f"W249+W245..W236 finalize products present "', 1, "P5d-print-deps")
rep('(69th own wave per live derive; "', '(70th own wave per live derive; "', 1, "P5d-print-69th")
rep("bm-c's 69th own wave per live derive", "bm-c's 70th own wave per live derive", 1, "P5d-rcpt-69th")
rep('"probe_receipt_bmc_ordinal_face": 69,', '"probe_receipt_bmc_ordinal_face": 70,', 1, "P5d-rcpt-ordface")
rep("post-W249 registration: bm-c rows 68 + candidate = 68th owned",
    "post-W249 registration: bm-c rows 69 + candidate = 70th owned", 1, "P5d-rcpt-68th")
rep("waits-upstream disarmed by W249 landing)",
    "queue-head supply -- W249 complete at publish, ZERO waits-upstream face)", 1, "P5d-rcpt-lane")
rep("freeze-time live face owner rows 238 + candidate = 238th EXACT",
    "freeze-time live face owner rows 239 + candidate = 240th EXACT", 1, "P5d-rcpt-238th")
rep("freeze-time live derive bmc rows 68 + candidate 68th EXACT per r587/r359",
    "freeze-time live derive bmc rows 69 + candidate 70th EXACT per r587/r359", 1, "P5d-bundle-68th")

# header window/lineage/seat faces
rep("# 2026-10-15 21:2x bm-c r1041 freeze window (upstream W1..W249 ALL LANDED, clean",
    "# 2026-10-16 07:5x bm-c r1046 freeze window (upstream W1..W249 ALL LANDED, clean", 1, "P5d-hdr-window")
rep("# precondition -- W249 finalize one-pass bm-c r1036 absorb-window closeout 22:1x,",
    "# precondition -- W249 finalize one-pass bm-c r1043 window closeout 05:5x,", 1, "P5d-hdr-precond")
rep("@ origin cc06f1f4a r1030, pre-seat probe", "@ origin cc06f1f4a r1043, pre-seat probe", 1, "P5d-hdr-seat")
rep("# the W250 seat's waits-upstream ARMED on the W249 chain is DISARMED by the\n# W249 five-face + finalize landing (bm-c r1036 absorb-window freeze + finalize\n# one-pass ledger 972,135 / K=545,720)); zero DRAFT marker; per-wave prereg",
    "# the W250 seat was published AFTER the W249 five-face + finalize landing\n# (queue-head supply -- W249 complete at publish, ZERO waits-upstream face;\n# bm-c r1042 splice + r1043 finalize one-pass ledger 972,135 / K=545,720)); zero DRAFT marker; per-wave prereg", 1, "P5d-hdr-seat-lane")
rep("# PERPETUAL_N1_W250_PREREG.md derived by the r1040-dead window (absorbed+committed r1041)",
    "# PERPETUAL_N1_W250_PREREG.md derived by the bm-c r1045 window (machine-SUB from the frozen W249 template)", 1, "P5d-hdr-prereg")
rep("# (authored 04:04:22, banned_direction_gate rc0, committed+pushed same window).",
    "# (authored 07:2x, banned_direction_gate ADMIT rc0, committed+pushed same window 4f7a130ff).", 1, "P5d-hdr-authored")
rep("# Lineage: _w249bmc_freeze_edits.py template (proven live-fire freeze, bm-c\n# r1036 absorb window; engine self-burn 12/12 + finalize one-pass verified same window)",
    "# Lineage: _w249bmc_freeze_edits.py template (proven live-fire freeze, bm-c\n# r1042 splice window; engine self-burn 12/12 + finalize one-pass verified r1043)", 1, "P5d-hdr-lineage")
rep("# post-W246-REGISTERED universe with the W249 candidate bands treated as",
    "# post-W249-REGISTERED universe with the W250 candidate bands treated as", 1, "P5d-hdr-universe")
rep('"    # origin " + SEAT_ORIGIN + " (r1030, queue-head supply -- W249 complete',
    '"    # origin " + SEAT_ORIGIN + " (r1043, queue-head supply -- W249 complete', 1, "P5d-pfcmt-seat")
rep("bm-c r1036 absorb-window freeze + finalize one-pass ledger 972,135 / K=545,720); prereg + ADMIT probe",
    "bm-c r1042 freeze + r1043 finalize one-pass ledger 972,135 / K=545,720); prereg + ADMIT probe", 1, "P5d-pfcmt-upstream")
rep('"    # r1040-dead window (absorbed+committed r1041) machine-SUB derive landed pre-freeze, probe",',
    '"    # bm-c r1045 window machine-SUB derive landed pre-freeze, probe",', 1, "P5d-pfcmt-prereg")
rep('"r1040-dead window (absorbed+committed r1041) machine-SUB derive landed pre-freeze -- bm-c own-seat ",',
    '"bm-c r1045 window machine-SUB derive landed pre-freeze -- bm-c own-seat ",', 1, "P5d-cfg-prereg")
rep('r1040-dead window (absorbed+committed r1041) derive landed pre-freeze commit {w250_prereg_sha[:10]}; this freeze splice editor",',
    'bm-c r1045 window derive landed pre-freeze commit {w250_prereg_sha[:10]}; this freeze splice editor",', 1, "P5d-hdr-emit-prereg")
rep('"    #     the bm-c r1036 absorb window; engine",',
    '"    #     the bm-c r1042 splice window; engine",', 1, "P5d-hdr-emit-upstream1")
rep('"    #     self-burn 12/12 + finalize one-pass bm-c r1036 absorb-window closeout ledger 972,135 / K=545,720",',
    '"    #     self-burn 12/12 + finalize one-pass bm-c r1043 closeout ledger 972,135 / K=545,720",', 1, "P5d-hdr-emit-upstream2")
rep('"    #     (r1030 MSG-20261016-055x-bmc-w250-seat @ origin "', '"    #     (r1043 MSG-20261016-055x-bmc-w250-seat @ origin "', 1, "P5d-hdr-emit-seat")
rep("bm-c own seat executed at the bm-c r1036 absorb window; engine self-burn 12/12; finalize one-pass bm-c r1036 absorb-window closeout, ledger 972,135 / K=545,720 machine-read), ",
    "bm-c own seat executed at the bm-c r1042 splice window; engine self-burn 12/12; finalize one-pass bm-c r1043 closeout, ledger 972,135 / K=545,720 machine-read), ", 1, "P5d-cfg-upstream")
rep('"repair_chain_note": "W249 bm-c own-wave closeout r1036 absorb window (five-face splice "',
    '"repair_chain_note": "W249 bm-c own-wave closeout r1043 (five-face splice "', 1, "P5d-rcpt-repair")
rep(" r1037 BEFORE this freeze per r565 law", " r1043 BEFORE this freeze per r565 law", 1, "P5d-rcpt-seat-r")
rep("the W250 freeze's waits-upstream on the W249 chain DISARMED by the W249 five-face + finalize landing bm-c r1036)",
    "the W250 seat published post-W249-chain (queue-head supply, freeze-UNBLOCKED; the W249 five-face + finalize landed bm-c r1042 splice + r1043 finalize before publish)", 1, "P5d-rcpt-seat-lane")
rep('"note": "prereg derived by the r1040-dead window (absorbed+committed r1041) (authored 04:04:22, banned gate ADMIT rc0 re-verified r1041, committed r1041; commit "',
    '"note": "prereg derived by the bm-c r1045 window (authored 07:2x, banned gate ADMIT rc0 re-verified r1045, committed r1045; commit "', 1, "P5d-rcpt-bundle")

# leg4 projection prose (honest W251p face: B naive NOT clean, hops=11, first-clean elsewhere)
rep('"    # seed refusers) / B naive " + rec["legs"]["leg4"]["W251p_B_naive"] + " CLEAN (staircase continuation, hops=" + str(rec["legs"]["leg4"]["hops_B"]) + ",",',
    '"    # seed refusers) / B naive " + rec["legs"]["leg4"]["W251p_B_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " NOT clean at naive -- first-clean " + rec["legs"]["leg4"]["W251p_B_first_clean"] + ",",', 1, "P5d-pfcmt-leg4B")
rep('"    # B base == prior-B-tail+1 EXACT, lands OUTSIDE the projection A window;",',
    '"    # lands OUTSIDE the projection A window;",', 1, "P5d-pfcmt-leg4C")
rep("W251p face per this window's probe leg4: A naive 563501..565500 CLEAN (hops=0, zero live refusers) / B naive 544901..545100 CLEAN (hops=0, staircase continuation, B base == prior-B-tail+1 EXACT, lands OUTSIDE the projection A window); seed-gap face inherited: W250 A/B decoupled, do NOT assume the staircase A-base==prior-B-tail+1 equality",
    "W251p face per this window's probe leg4: A naive 567501..569500 CLEAN (hops=0, zero live refusers) / B naive 545301..545500 hops=11 NOT clean at naive, first-clean 565501..565700 (B_hop lands-inside-A=false leg present); seed-gap face inherited: W250 A/B decoupled, re-read the live trace at W251 derive time, do NOT assume the staircase A-base==prior-B-tail+1 equality", 1, "P5d-rcpt-downstream")
rep("f\"{rec['legs']['leg4']['W251p_B_naive']} CLEAN (hops=0, staircase continuation, B base == prior-B-tail+1 EXACT, lands OUTSIDE the projection A window -- B_hop lands-inside-A=false leg present; seed-gap face \"",
    "f\"{rec['legs']['leg4']['W251p_B_naive']} hops={rec['legs']['leg4']['hops_B']} NOT clean at naive -- first-clean {rec['legs']['leg4']['W251p_B_first_clean']} (B_hop lands-inside-A=false leg present; seed-gap face \"", 1, "P5d-cfg-leg4B")

# ============ structural output gates ============
for needle, want in [
    ("# --- W250 materializer face", 2),
    ("# --- W249 materializer face", 1),
    ('"+ W250 materializer face', 2),
    ("range(16, 250)", 2),
    ("range(17, 250)", 3),
    ("range(238, 250)", 2),
    ("range(233, 249)", 1),
    ("list(range(238, 249))", 1),
    ("range(209, 251)", 2),
    ("if w < 250)", 5),
    ("if w < 249)", 1),
    ("_w250bmc_20261016_probe_receipt.json", 10),
    ("_w250bmc_freeze_receipt.json", 1),
    ("MSG-20261016-055x-bmc-w250-seat", 7),
    ("cc06f1f4a", 2),
    ("972_135", 1),
    ("545_720", 1),
    ("(565_501, 567_500)", 1),
    ("(545_101, 545_300)", 1),
    ('B_base_above_W249_tail', 1),
    ('W248_W249_bands_respected_A', 1),
    ('W248_W249_bands_respected_B', 1),
    ("W251p_A_naive", 2),
    ("W251p_B_first_clean", 2),
    ("arith_a250", 6),
    ("arith_b250", 6),
    ('"PERPETUAL-N1-W250-SHARD-0"', None),
    ('n1_w250_results.json', None),
    ("THIRTEENTH consecutive", 13),
    ("thirteenth consecutive", 2),
    ("SEVENTIETH", 3),
    ("TWO HUNDRED AND FIFTIETH", 3),
    ("thirty-eighth consecutive", 2),
    ("bmc_ordinal=70", 7),
    ("r1042 splice window", 3),
    ("r1043", 14),
    # anti-gates: stale faces must be zero
    ("r1036", 0),
    ("r1030", 0),
    ("r1040-dead", 0),
    ("r1037", 0),
    ("r1041", 0),
    ("8949e0aef", 0),
    ("969,935", 0),
    ("543,520", 0),
    ("969_935", 0),
    ("543_520", 0),
    ("TWELFTH", 0),
    ("tenth consecutive", 0),
    ("face tenth", 0),
    ("W247_W249_bands_respected", 0),
    ("MSG-20261015-225x", 0),
    ("bmc_ordinal=69", 0),
    ("68th", 0),
    ("69th", 0),
    ("238th", 0),
    ("thirty-seventh", 0),
    ("20261015_probe_receipt", 0),
]:
    n = t.count(needle)
    if want is not None:
        assert n == want, f"OUTPUT-GATE {needle!r}: {n} != {want}"
    log.append(f"OUT {needle!r} = {n}")

io.open(DST, "w", encoding="utf-8", newline="").write(t)
import py_compile
py_compile.compile(DST, doraise=True)
io.open(os.path.join(REPO, "results", "_w250bmc_derive_editor_log.txt"), "w",
        encoding="utf-8").write("\n".join(log))
print(f"DERIVE OK -> {DST} ({len(t)} chars); {len(log)} transform log rows")
print("\n".join(log[-12:]))
