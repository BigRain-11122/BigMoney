# -*- coding: utf-8 -*-
# r1062 bm-c: BUILD results/_w258bmc_derive_editor.py from the committed W257
# derive-editor canon (results/_w257bmc_derive_editor.py @ HEAD) by machine
# splice (E63 10th-gen zero-transcription law: every replay-chain family
# literal + every replay sublist is spliced VERBATIM from the committed canon
# bytes; only the new-generation section texts are hand-authored here and
# every count is floor-asserted). Builder receipt: results/_r1062bmc_build_editor_log.txt.
import io, subprocess, sys

CANON = "results/_w257bmc_derive_editor.py"
DST = "results/_w258bmc_derive_editor.py"
LOG = "results/_r1062bmc_build_editor_log.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w257bmc_derive_editor.py"], capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head and len(blob_wt) == 40, f"canon blob drift: wt={blob_wt} head={blob_head}"

t = io.open(CANON, encoding="utf-8", newline="").read()
log = [f"S0 canon blob verified {blob_wt[:16]} == HEAD twin (worktree clean face)"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] {n} != {expect}: {old[:90]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

def sect(start_marker, end_marker, new_text, tag):
    global t
    i = t.index(start_marker)
    j = t.index(end_marker, i)
    t = t[:i] + new_text + t[j:]
    log.append(f"{tag}: section {j - i} -> {len(new_text)} chars")

def extend_family(var, kind, tag, new_subs):
    """E257 final call  ->  E258: _X_W257 reconstruction line + NEW final call.
    The E257 final sublist text is extracted VERBATIM from the canon bytes."""
    global t
    i = t.index(f"{kind}(age({var}),")
    if kind == "rep":
        end_marker = f'1, "{tag}")'
    else:
        end_marker = f'"{tag}"), "{tag}")'
    j = t.index(end_marker, i) + len(end_marker)
    k = t.index(f"mk(age({var}),", i)
    lo = t.index("[", k) + 1
    hi = t.index(f'], "{tag}")', k)
    sublist = t[lo:hi]
    nv = var[:-1] + "7"                       # _X_W256 -> _X_W257
    recon = (f"{nv} = mk257(age_prev2({var}), [{sublist}], \"{tag}-prev3\")")
    if kind == "rep":
        new_final = (f"rep(age({nv}),\n    mk(age({nv}), [{new_subs}\n    ], \"{tag}\"),\n    1, \"{tag}\")")
    else:
        new_final = (f"chunk(age({nv}),\n      mk(age({nv}), [{new_subs}\n      ], \"{tag}\"), \"{tag}\")")
    t = t[:i] + recon + "\n" + new_final + t[j:]
    log.append(f"extend {var}: final -> recon+final (sublist {len(sublist)}B spliced verbatim)")

# ---------- 1) header ----------
NEW_HEADER = r'''# -*- coding: utf-8 -*-
# r1062 bm-c: derive results/_w258bmc_freeze_edits.py from the committed W257
# freeze-edits script (results/_w257bmc_freeze_edits.py, proven live-fire W257
# splice bm-c r1060 window: splice 550293d3f + engine self-burn 12/12 + finalize
# one-pass ledger 989,735 / K=563,320 five-key 6/6 by the r1060 closeout 5632ebf2b)
# via COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage, 10th-gen pass ordering:
# P1 structural outputs BLANKET-IMMUNE; the W258 extraction faces move ONE
# structural face vs the W257 estate mandate -- the kept/dropped split
# boundary MOVES 239->240 per the frozen W258 prereg sec.3 mandate [kept
# W211..W239 (29) + dropped W240..W256 (17) + fresh W240..W257 (18) = 116
# parity rows W138..W206+W211..W257, the W258 block parity list enumerates
# W211..W257 with NO gap]; the boundary move = NEW-face direct-rep class
# this generation: four m239->m240 code faces + kept assert 28/range(211,239)
# -> 29/range(211,240) + dropped range lower bound + fresh-loop/leg-count
# lower bounds + the mat-hdr kept line, all pre-flight count-asserted).
# W258 facts (machine-read from the probe receipt _w258bmc_20261017, never
# transcribed):
# bands A 582_901..584_900 (1-HOP STAIRCASE-AFFECTS-A walk, SEVENTH
# consecutive A-hop -- the naive continuation 582_701..584_700 is REFUSED at
# its own start: the registered W257 B band 582_701..582_900 sits INSIDE the
# naive A window = staircase re-emergence continues to affect A, the W257
# prereg sec.5.5 item5 A-naive-CLEAN pre-W257-universe projection superseded
# live per r587, divergence disclosed; the walk hops past the W257 B tail
# 582_900 -> A first-clean 582_901..584_900, hops=1; A base == registered
# prior-wave B tail+1 (582_900+1) EXACT this window; A_clean_at_naive_start=
# false; A_staircase_hop_past_W257_B=true) /
# B 584_901..585_100 (1-HOP own-A RESERVATION CASCADE above own-A, EIGHTH
# consecutive above-own-A -- the naive continuation 582_901..583_100 is
# REFUSED at its own start -- the naive window lands INSIDE the own-wave
# W258 A first-clean window 582_901..584_900, own-A reservation cascade
# standard leg; the walk hops past the own-A tail 584_900 -> B landing
# 584_901..585_100, hops=1; B lands ABOVE own-A; B base == own-A tail+1
# (584_900+1) EXACT; B_naive_refused_at_start=true; B_lands_above_own_A=true;
# B_hop_lands_inside_A=false; hops=1), upstream W257 = bm-c own chain, seat
# MSG-20261017-0517-bmc-w258-seat @ origin d0d0d04a4 (r1060 closeout, W258
# SEAT published post-W257-chain -- queue-head FREEZE-UNBLOCKED supply, zero
# waits-upstream), prereg 824b46d31 derived bm-c r1061 (authored 05:5x,
# banned_direction_gate ADMIT rc0, committed+pushed same window; splice
# window = r1062 THIS window -- prereg window != splice window this
# generation, disclosed; W258 prereg freeze landed 05:51:53 by r1061).
# Needle law this generation: ALL chunk/repp needles are machine-derived via
# age() = the exact blanket composition (P2 W258->W259, P3 257->258,
# P4 256->257) applied to the W257-script-era literals; the era chunk faces
# are reconstructed by the FOUR-LEVEL chain mk255(age_prev255(W254 literal))
# -> mk256(age_prev(...)) -> mk257(age_prev2(...)) -> age() needle (E63
# 10th-gen, disclosed; needle pre-flight probe
# results/_w258bmc_editor_needle_preflight.py ALL PASS -- 134 faces measured
# on the committed W257 freeze-edits script; this editor itself was built by
# the machine-splice builder results/_r1062bmc_build_editor.py -- family
# literals + replay sublists spliced verbatim from the committed E257 canon
# bytes, zero hand-transcription).
# Date-stable face this generation: the probe receipt basename date does NOT
# roll AGAIN (20261017 == 20261017, second consecutive date-stable
# generation) -- the P5f rep is an identity count-assert (10x), zero heal
# needed (disclosed).
'''
sect(t.split("\n", 1)[0], "import io, os, subprocess, sys", NEW_HEADER, "hdr")

# ---------- 2) path faces + blob sha (order: DST/LOG first, then SRC) ----------
rep('"_w257bmc_freeze_edits.py"', '"_w258bmc_freeze_edits.py"', 1, "dst-path")
rep('"_w257bmc_derive_editor_log.txt"', '"_w258bmc_derive_editor_log.txt"', 1, "log-path")
rep('"_w256bmc_freeze_edits.py"', '"_w257bmc_freeze_edits.py"', 1, "src-path")
rep('HEAD:results/_w256bmc_freeze_edits.py', 'HEAD:results/_w257bmc_freeze_edits.py', 1, "src-blob-path")
rep('assert blob_wt == "ba18d525d40b20c3a151c17c7933812deaf414f2"',
    'assert blob_wt == "8889dc881a075f0332dd268bb760a960f2974e59"', 1, "src-blob-sha")

# ---------- 3) era functions (four-level era chain this generation) ----------
NEW_ERAS = r'''# age_prev255(): the W255 editor's blanket composition -- used ONLY to
# reconstruct the W255-script chunk faces from the W254-era literals (the
# needles the r1057 editor itself consumed; preserved verbatim from the W256
# editor canon).
def age_prev255(s):
    s = s.replace("W255", "W256")
    s = s.replace("254", "255")
    s = s.replace("253", "254")
    return s

# age_prev(): the W256 editor's blanket composition (P2 W256->W257,
# P3 255->256, P4 254->255) -- reconstructs the W256-script chunk faces from
# the W255-era faces.
def age_prev(s):
    s = s.replace("W256", "W257")
    s = s.replace("255", "256")
    s = s.replace("254", "255")
    return s

# age_prev2(): the W257 editor's blanket composition (P2 W257->W258,
# P3 256->257, P4 255->256) -- reconstructs the W257-script chunk faces from
# the W256-era faces (NEW level this generation, disclosed; body = the W257
# editor's age() verbatim).
def age_prev2(s):
    s = s.replace("W257", "W258")
    s = s.replace("256", "257")
    s = s.replace("255", "256")
    return s

# age(): EXACT composition of MY blanket passes (P2 downstream W258->W259,
# P3 self 257->258, P4 upstream 256->257) -- derives post-pass needles from
# W257-script-era literals WITHOUT hand-derivation.
def age(s):
    s = s.replace("W258", "W259")
    s = s.replace("257", "258")
    s = s.replace("256", "257")
    return s

'''
sect("# age_prev255(): the W255 editor", "def rep(old, new, expect=None, tag=", NEW_ERAS, "eras")

# ---------- 4) mk257 def insert + mk() comment roll ----------
NEW_MK257 = r'''# mk257(): rebuild the W257-script chunk from the W256-era face (asserts
# the W257 editor's fact subs exactly as the r1060 editor ran them; NEW
# level this generation, disclosed).
def mk257(needle, repls, tag):
    s = needle
    for old, new, cnt in repls:
        n = s.count(old)
        assert n == cnt, f"[{tag}.{s.count(old)}] sub {old[:56]!r}: {n} != {cnt}"
        s = s.replace(old, new)
    return s

'''
sect("# mk(): build a chunk NEW text", "def mk(needle, repls, tag):",
     NEW_MK257 + '# mk(): build a chunk NEW text from its (post-blanket) needle via ordered\n# count-asserted fact replacements -- W257 facts from the probe receipt.\n\n', "mk257")
rep("W257 facts from the probe receipt", "W258 facts from the probe receipt", 1, "mk-comment-roll")

# ---------- 5) P1..P4x ----------
NEW_P1_P4X = r'''# ============ P1: structural faces, BLANKET-IMMUNE outputs ============
rep("(253, 252, 251, 250, 249, 248, 247, 246, 245, 244)",
    "(254, 253, 252, 251, 250, 249, 248, 247, 246, 245)", 2, "P1-transitive-deps")
rep("range(209, 258)", "range(209, 259)", 2, "P1-liveness-range")
rep('def fmt(n):  # 580701 -> "580_701"', 'def fmt(n):  # 582901 -> "582_901"', 1, "P1-fmt-comment")

# ============ P2: downstream shift W258 -> W259 ============
rep("W258", "W259", None, "P2-downstream")
assert "W258" not in t, "P2 leftover W258"

# ============ P3: self shift 257 -> 258 ============
n257 = t.count("257")
rep("257", "258", None, "P3-self")
log.append(f"P3 consumed {n257} '257' substrings")

# ============ P4: upstream shift 256 -> 257 ============
n256 = t.count("256")
rep("256", "257", None, "P4-upstream")
log.append(f"P4 consumed {n256} '256' substrings")

# ============ P4x: blanket-exemption heal (API-name face, disclosed) ============
# the P4 self-shift rep("256","257") hits the FOUR "hashlib.sha256" API-name
# occurrences inside the source (sha256 is an ALGORITHM name, not a wave
# face) -- restored verbatim immediately post-blanket, count-asserted 4x
# (third consecutive generation with this face; evidence = pre-flight
# sha256=4 / sha257=0 on the committed W257 script).
rep("hashlib.sha257", "hashlib.sha256", 4, "P4x-sha256-api-heal")

'''
sect("# ============ P1: structural faces", "# ============ P5a: numeric/anchor", NEW_P1_P4X, "P1-P4x")

# ---------- 6) P5a ----------
NEW_P5A = r'''# ============ P5a: numeric/anchor/ordinal/window faces (post-blanket forms) ============
# r-window ORDER DISCLOSURE (needle-heal family, vs the W257 editor order):
# the source's own prereg-window refs are r1059 (7x) AND its freeze stamp is
# "r1060 freeze window" (1x header) -- the E258 chain reps CREATE new "r1060"
# strings (from the 23 "r1058" refs), so the header-window rep runs FIRST
# (consumes the unique full-stamp needle BEFORE any r1058->r1060 creation
# lands), prereg-window second, closeout/splice/rest after. Counts
# pre-flight-verified on the committed W257 script: r1059=7 / r1058=23
# (1 closeout + 3 splice-window + 19 rest) / r1060=1 (header stamp only).
rep(age("2026-10-17 04:4x bm-c r1060 freeze window"), "2026-10-17 06:2x bm-c r1062 freeze window", 1, "P5a-header-window")
rep(age("r1059"), "r1061", 7, "P5a-prereg-window")
rep(age("W256 finalize one-pass bm-c r1058 window closeout 04:0x"),
    "W257 finalize one-pass bm-c r1060 window closeout 05:1x", 1, "P5a-closeout-window")
rep(age("r1058 splice window"), "r1060 splice window", 3, "P5a-splice-window")
rep(age("r1058"), "r1060", 19, "P5a-splice-window-rest")
rep(age("authored 04:1x"), "authored 05:5x", 2, "P5a-authored-time")
rep(age("987_535"), "989_735", 1, "P5a-ledger-int")
rep(age("561_120"), "563_320", 1, "P5a-k-int")
rep(age("987,535"), "989,735", 8, "P5a-ledger-prose")
rep(age("561,120"), "563,320", 8, "P5a-k-prose")
rep(age("bmc_ordinal=77"), "bmc_ordinal=78", 7, "P5a-ordinal77")
rep(age("SEVENTY-SEVENTH"), "SEVENTY-EIGHTH", 3, "P5a-seventyseventh")
rep(age("TWO HUNDRED AND FIFTY-SEVENTH"), "TWO HUNDRED AND FIFTY-EIGHTH", 3, "P5a-250th")
rep(age("forty-fifth consecutive"), "forty-sixth consecutive", 2, "P5a-finface")
rep(age("77th own wave"), "78th own wave", 3, "P5a-77th-ownwave")
rep(age("MSG-20261017-03xx-bmc-w257-seat"), "MSG-20261017-0517-bmc-w258-seat", 7, "P5a-seat-msg")
rep(age("27ee6e95a"), "d0d0d04a4", 2, "P5a-seat-origin")
rep(age("c7fbc443c"), "824b46d31", 1, "P5a-prereg-commit")
# aging-face needle heals (same-window disclosed, r1045/r1047/r1050/r1055/r1057/r1058 precedent family):
rep(age("transitive window W244..W253 checked"), "transitive window W245..W254 checked", 1, "P5a-aging-deps-cmt")
rep(age("engine_owner==bm-c rows 76 + candidate"), "engine_owner==bm-c rows 77 + candidate", 1, "P5a-aging-rows-heal")

'''
sect("# ============ P5a: numeric/anchor", "# ============ P5b: extraction count faces", NEW_P5A, "P5a")

# ---------- 7) P5b direct (pre-chain) ----------
NEW_P5B = r'''# ============ P5b: extraction count faces (frozen W258 prereg sec.3 mandate) ============
# estate 69 (W138..W206) UNCHANGED; kept W211..W239 (29); dropped W240..W256
# (17); fresh W240..W257 (18); total parity 116 rows; legs segment
# W211..W256 (46). NEW FACE this generation (disclosed): the kept/dropped
# split boundary MOVES 239->240 per the frozen W258 prereg sec.3 mandate
# (kept W211..W239 29 legs -- the W258 block parity list enumerates W211..W257
# with NO gap, so W239 moves from the dropped set into the kept set); four
# m239->m240 code faces + kept/dropped range faces + fresh-loop lower bounds
# are count-asserted direct reps (pre-flight: m239=4 / range(239,257)=2 /
# kept-28=1 / dropped-17=1).
rep(age("# block's own W239..W255 legs (17 rows) do NOT enter the estate path;"),
    "# block's own W240..W256 legs (17 rows) do NOT enter the estate path;", 1, "P5b-hdr-ownlegs")
rep(age("# after extraction, fresh W239..W256 legs (18 rows) are added,"),
    "# after extraction, fresh W240..W257 legs (18 rows) are added,", 1, "P5b-hdr-freshlegs")
rep(age("# parity = 115 rows (W138..W206 + W211..W256). Zero assumption zero risk."),
    "# parity = 116 rows (W138..W206 + W211..W257). Zero assumption zero risk.", 1, "P5b-hdr-parity-count")
rep(age("# block's own W239..W255 legs (17) are EXCLUDED from the estate path per the"),
    "# block's own W240..W256 legs (17) are EXCLUDED from the estate path per the", 1, "P5b-ext-excl")
rep(age("# prereg mandate; the W257 block appends fresh W239..W256 legs (18,"),
    "# prereg mandate; the W258 block appends fresh W240..W257 legs (18,", 1, "P5b-ext-fresh")
rep(age("# machine-derived from the LIVE pf registry at freeze time) -> 115 parity"),
    "# machine-derived from the LIVE pf registry at freeze time) -> 116 parity", 1, "P5b-ext-parcount")
'''
sect("# ============ P5b: extraction count faces", "_PARFULL_W255 = ", NEW_P5B, "P5b-direct")

# ---------- 8) P5b chains: extend 4 families ----------
extend_family("_PARFULL_W256", "rep", "P5b-parfull",
    '\n        ("== 114", "== 115", 1),\n        ("!= 114 (69 estate + W211..W255 legs 45)", "!= 115 (69 estate + W211..W256 legs 46)", 1),')
extend_family("_LEGS_W256", "rep", "P5b-legs-assert",
    '\n        ("== 45", "== 46", 1),\n        ("legs segment not W211..W255 forty-five legs", "legs segment not W211..W256 forty-six legs", 1),')
extend_family("_DROP_W256", "rep", "P5b-dropped-assert",
    '\n        ("list(range(239, 257))", "list(range(240, 257))", 1),\n        ("dropped segment not W239..W255 seventeen legs", "dropped segment not W240..W256 seventeen legs", 1),')
extend_family("_RCPTNOTE_W256", "rep", "P5b-rcpt-note",
    '\n        ("own W239..W255 legs (17) EXCLUDED", "own W240..W256 legs (17) EXCLUDED", 1),\n        ("fresh W239..W257 legs (18) machine-derived", "fresh W240..W257 legs (18) machine-derived", 1),\n        ("W258 block = 115 rows", "W258 block = 116 rows", 1),\n        ("E63 9th-gen", "E63 10th-gen", 1),\n        ("W211..W238 legs (28)", "W211..W239 legs (29)", 1),\n        ("list(range(211,257))/list(range(211,239))/list(range(239,257))", "list(range(211,257))/list(range(211,240))/list(range(240,257))", 1),')

# ---------- 9) P5b late (split/boundary/mat/rcpt-identity reps) ----------
NEW_P5B_LATE = r"""# NEW-FACE split-boundary reps (239 -> 240, frozen W258 prereg sec.3 mandate):
rep(age("# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W256\n# block's own W239..W255 legs (17) are excluded from the estate path"),
    "# prereg sec.3 mandate split: keep W211..W239 verbatim (29 legs); the W257\n# block's own W240..W256 legs (17) are excluded from the estate path", 1, "P5b-split-cmt")
rep(r'm239 = re.search(r" *assert pf\.N1_BANDS\[239\] ==", legs_sec)',
    r'm240 = re.search(r" *assert pf\.N1_BANDS\[240\] ==", legs_sec)', 1, "P5b-split-mvar")
rep('assert m239, "W239 leg boundary not found inside W258 legs segment (prereg sec.3 split face)"',
    'assert m240, "W240 leg boundary not found inside W258 legs segment (prereg sec.3 split face)"', 1, "P5b-split-assert")
rep("legs_kept = legs_sec[:m239.start()]", "legs_kept = legs_sec[:m240.start()]", 1, "P5b-split-kept")
rep("legs_dropped = legs_sec[m239.start():]", "legs_dropped = legs_sec[m240.start():]", 1, "P5b-split-dropped")
# kept assert moves 28/range(211,239) -> 29/range(211,240) (NEW face, pre-flight raw count 1):
_KEPT_W257 = '''assert legs_kept.count("assert pf.N1_BANDS[") == 28 \\
    and [int(w) for w in _kept_ws] == list(range(211, 239)), \\
    f"kept segment not W211..W238 twenty-eight legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"'''
rep(_KEPT_W257, '''assert legs_kept.count("assert pf.N1_BANDS[") == 29 \\
    and [int(w) for w in _kept_ws] == list(range(211, 240)), \\
    f"kept segment not W211..W239 twenty-nine legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"''', 1, "P5b-kept-assert")
# fresh-loop + leg-count-loop lower bounds + fresh first-line assert (NEW face):
rep(age("for _w in range(239, 257):"), "for _w in range(240, 258):", 1, "P5b-fresh-loop")
rep(age("for _lw in range(239, 257):"), "for _lw in range(240, 258):", 1, "P5b-legcount-loop")
rep("assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[239] == {\"a\": (')",
    "assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[240] == {\"a\": (')", 1, "P5b-fresh-firstline")
# receipt count faces: fresh stays 18 this generation = identity count-asserts (disclosed):
rep(age('"fresh_legs_row_asserts": 18,'), '"fresh_legs_row_asserts": 18,', 1, "P5b-rcpt-fresh18-identity")
rep(age('+ legs_kept.count("assert pf.N1_BANDS[") + 18,'), '+ legs_kept.count("assert pf.N1_BANDS[") + 18,', 1, "P5b-rcpt-total18-identity")
# materializer hdr comment faces:
rep(age('"    #     W211..W238 legs (28) extracted verbatim from the OWN W256 block",'),
    '"    #     W211..W239 legs (29) extracted verbatim from the OWN W257 block",', 1, "P5b-hdr-kept-mat")
rep(age('"    #     physical bytes; the W256 block\'s own W239..W255 legs (17) are",'),
    '"    #     physical bytes; the W258 block\'s own W240..W256 legs (17) are",', 1, "P5b-hdr-ownlegs-mat")
rep(age('"    #     W239..W256 legs (18) added, machine-derived from the live pf",'),
    '"    #     W240..W257 legs (18) added, machine-derived from the live pf",', 1, "P5b-hdr-freshlegs-mat")
rep(age('"    #     registry at freeze time -> 115 parity rows (W138..W206+W211..W256).",'),
    '"    #     registry at freeze time -> 116 parity rows (W138..W206+W211..W257).",', 1, "P5b-hdr-parcount-mat")

"""
sect('rep(age("# prereg sec.3 mandate split:', '# receipt note (single big face: counts + generation stamp)', NEW_P5B_LATE, "P5b-late")

# ---------- 10) P5c ----------
NEW_P5C = r'''# ============ P5c: band literals (probe ADMIT receipt bands) ============
rep(age('assert (a_lo, a_hi) == (580_701, 582_700) and (b_lo, b_hi) == (582_701, 582_900), \\'),
    'assert (a_lo, a_hi) == (582_901, 584_900) and (b_lo, b_hi) == (584_901, 585_100), \\', 1, "P5c-band-drift")

'''
sect("# ============ P5c: band literals", "# ============ P5d: ordinal/leg0", NEW_P5C, "P5c")

# ---------- 11) P5d ----------
NEW_P5D = r'''# ============ P5d: ordinal/leg0/deps faces ============
rep(age('assert len(owner_rows_live) == 246 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 76, \\'),
    'assert len(owner_rows_live) == 247 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 77, \\', 1, "P5d-ord-gate")
# needle narrowed to the pre-registration numeric face: the trailing "78th own
# wave" inside this line was ALREADY rewritten by the P5a-77th-ownwave rep
# (order-sensitive face, W257 editor canon -- its P5d needle was likewise the
# post-P5a form); disclosed needle heal, evidence = pre-flight n=1 raw face.
rep(age("(expect 246/129/76 PRE-splice post-W256 registration"),
    "(expect 247/129/77 PRE-splice post-W257 registration", 1, "P5d-ord-err")
# needle narrowed likewise: the trailing "bmc_ordinal=78" on this line was
# already rewritten by the P5a-ordinal77 rep (one of its 7 faces).
rep(age('# receipt leg0 face owner_rows=246 / bmc_rows=76 /'),
    '# receipt leg0 face owner_rows=247 / bmc_rows=77 /', 1, "P5d-leg0-prose")
rep(age("-> owner rows 246 + candidate = 247th EXACT; bm-c rows 76 +"),
    "-> owner rows 247 + candidate = 248th EXACT; bm-c rows 77 +", 1, "P5d-ord-owner-prose")
rep(age("# candidate = 77th EXACT -- bm-c own-seat continuity face (bm-c published the"),
    "# candidate = 78th EXACT -- bm-c own-seat continuity face (bm-c published the", 1, "P5d-ord-bmc-prose")
rep(age("freeze-time live face owner rows 246 + candidate = 247th EXACT"),
    "freeze-time live face owner rows 247 + candidate = 248th EXACT", 1, "P5d-rcpt-247th")
rep(age("freeze-time live derive bmc rows 76 + candidate 77th EXACT per r587/r359"),
    "freeze-time live derive bmc rows 77 + candidate 78th EXACT per r587/r359", 1, "P5d-bundle-77th")
rep(age("post-W256 registration: bm-c rows 76 + candidate = 77th owned"),
    "post-W257 registration: bm-c rows 77 + candidate = 78th owned", 1, "P5d-rcpt-77th-owned")
rep(age('"probe_receipt_bmc_ordinal_face": 77,'), '"probe_receipt_bmc_ordinal_face": 78,', 1, "P5d-rcpt-ordface")
rep(age('f"W257+W252..W243 finalize products present "'), 'f"W258+W253..W244 finalize products present "', 1, "P5d-print-deps")

'''
sect("# ============ P5d: ordinal/leg0", "# ============ P5e: A/B face structural", NEW_P5D, "P5d")

# ---------- 12) P5e families (extend; new final subs = W258 facts) ----------
extend_family("_HDR_W256", "chunk", "P5e-hdr",
    '\n          ("SEVENTH consecutive\\n# above-own-A", "EIGHTH consecutive\\n# above-own-A", 1),\n          ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 1),\n          ("580_701..582_700", "582_901..584_900", 2),\n          ("582_701..582_900", "584_901..585_100", 1),\n          ("580_501..582_500", "582_701..584_700", 1),\n          ("580_501..580_700", "582_701..582_900", 1),\n          ("580_701..580_900", "582_901..583_100", 1),\n          ("580_700", "582_900", 2),\n          ("582_700", "584_900", 2),')
extend_family("_BANDFACTS_W256", "chunk", "P5e-bandfacts",
    '\n          ("SEVENTH consecutive above-own-A landing", "EIGHTH consecutive above-own-A landing", 1),\n          ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 2),')
extend_family("_A_BASE_W256", "rep", "P5e-a-base",
    ' ("sixth consecutive A-hop", "seventh consecutive A-hop", 1),')
extend_family("_A_FLOOR_W256", "rep", "P5e-a-floor",
    ' ("sixth consecutive A-hop", "seventh consecutive A-hop", 1),')
extend_family("_B_BASE_W256", "rep", "P5e-b-base",
    ' ("seventh consecutive above-own-A", "eighth consecutive above-own-A", 1),')
extend_family("_RA_GATE_W256", "rep", "P5e-ra-gate",
    '\n        ("W254_W255_W257_bands_respected_A", "W255_W256_W257_bands_respected_A", 1),\n        ("W254_W255_W257_bands_respected_B", "W255_W256_W257_bands_respected_B", 1),')
extend_family("_PFCMT_W256", "chunk", "P5e-pfcmt",
    '\n          ("SEVENTH consecutive above-own-A;", "EIGHTH consecutive above-own-A;", 1),\n          ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 1),\n          ("hops=1 -- FIFTH", "hops=1 -- SIXTH", 1),')
extend_family("_PRE_W256", "chunk", "P5e-pre",
    '\n          ("SEVENTH consecutive above-own-A", "EIGHTH consecutive above-own-A", 1),\n          ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 2),')
extend_family("_MEM_A_W256", "rep", "P5e-mem-a",
    '\n        ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 1),\n        ("sixth consecutive A-hop", "seventh consecutive A-hop", 1),')
extend_family("_MEM_B_W256", "rep", "P5e-mem-b",
    ' ("seventh consecutive above-own-A", "eighth consecutive above-own-A", 1),')
extend_family("_TAILCMT_W256", "chunk", "P5e-tailcmt",
    '\n          ("SEVENTH consecutive", "EIGHTH consecutive", 1),\n          ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 2),')
extend_family("_TAIL_AMSG_W256", "rep", "P5e-tail-amsg",
    ' ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 2),')
extend_family("_EXCL_W256", "rep", "P5e-tail-excl",
    ' ("seventh consecutive above-own-A", "eighth consecutive above-own-A", 1),')
extend_family("_PRCHUNK_W256", "chunk", "P5e-pr",
    '\n          ("SEVENTH consecutive above-own-A landing", "EIGHTH consecutive above-own-A landing", 1),\n          ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 1),')
extend_family("_SEM_A_W256", "rep", "P5e-rcpt-semantics-A",
    '\n        ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 2),\n        ("580_501..582_500 refused", "582_701..584_700 refused", 1),\n        ("580_501..580_700 sits", "582_701..582_900 sits", 1),\n        ("B tail 580_700 -> A first-clean 580_701..582_700", "B tail 582_900 -> A first-clean 582_901..584_900", 1),\n        ("(580_700+1) EXACT)", "(582_900+1) EXACT)", 1),')
extend_family("_SEM_B_W256", "rep", "P5e-rcpt-semantics-B",
    '\n        ("SEVENTH consecutive above-own-A landing", "EIGHTH consecutive above-own-A landing", 1),\n        ("580_701..580_900 is refused", "582_901..583_100 is refused", 1),\n        ("A first-clean window 580_701..582_700 (own-A", "A first-clean window 582_901..584_900 (own-A", 1),\n        ("own-A tail 582_700 -> B landing 582_701..582_900;", "own-A tail 584_900 -> B landing 584_901..585_100;", 1),\n        ("(582_700+1) EXACT)", "(584_900+1) EXACT)", 1),')
extend_family("_DOWNSTREAM_W256", "rep", "P5e-rcpt-downstream",
    '\n        ("A naive 582701..584700 CLEAN", "A naive 584901..586900 CLEAN", 1),\n        ("B naive 582901..583100 hops=0 CLEAN at naive, first-clean 582901..583100 BUT", "B naive 585101..585300 hops=0 CLEAN at naive, first-clean 585101..585300 BUT", 1),\n        ("naive A window start 582_701 lands INSIDE the registered W258 B band 582_701..582_900", "naive A window start 584_901 lands INSIDE the registered W258 B band 584_901..585_100", 1),')

# identity reps: THREE-level inline chain -> FOUR-level (age_prev2 inserted):
# identity reps: THREE-level inline chain -> FOUR-level (age_prev2 inserted;
# full-block replace keeps paren balance, disclosed):
rep("""rep(age(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')),
    ), age(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "'))), 1, "P5e-tail-bassert2")""",
    """rep(age(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')),
    )), age(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')))), 1, "P5e-tail-bassert2")""",
    1, "identity-4level-bassert2")
rep("""rep(age(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"')),
    ), age(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"'))), 1, "P5e-tail-bclean")""",
    """rep(age(age_prev2(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"')),
    )), age(age_prev2(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"')))), 1, "P5e-tail-bclean")""",
    1, "identity-4level-bclean")

# family-section comment roll:
rep("# downstream W258+ projection face (probe leg4 verbatim numbers)",
    "# downstream W259+ projection face (probe leg4 verbatim numbers)", 1, "downstream-cmt-roll")

# ---------- 13) P5f ----------
NEW_P5F = r'''# ============ P5f: probe-receipt date face (DATE-STABLE this generation) ============
# disclosed date-stable face: the W258 probe receipt basename keeps the SAME
# date AGAIN (20261017 == 20261017, second consecutive date-stable
# generation) -- the blanket P3 already rolled the basename to
# _w258bmc_20261017_probe_receipt.json which IS the correct on-disk name;
# this rep is an identity count-assert (10x), zero heal needed (vs the W256
# editor's 10x date-roll rep 20261016->20261017). Position stays POST-P5e
# (the pfcmt chunk needle embeds the pre-replacement basename face).
rep(age("_w257bmc_20261017_probe_receipt.json"), "_w258bmc_20261017_probe_receipt.json", 10, "P5f-probe-receipt-date-stable")

'''
sect("# ============ P5f: probe-receipt date face", "# ============ structural output gates", NEW_P5F, "P5f")

# ---------- 14) output gates ----------
NEW_GATES = r'''# ============ structural output gates ============
for needle, want in [
    ("# --- W258 materializer face", 2),
    ("# --- W257 materializer face", 1),
    ('"+ W258 materializer face', 2),
    ("range(16, 258)", 2),
    ("range(17, 258)", 3),
    ("range(240, 258)", 2),
    ("range(239, 258)", 0),
    ("list(range(211, 257)),", 1),
    ("list(range(211, 240))", 1),
    ("list(range(211, 239))", 0),
    ("list(range(240, 257)),", 1),
    ("range(209, 259)", 2),
    ("if w < 258)", 5),
    ("if w < 257)", 1),
    ("m240", 4),
    ("m239", 0),
    ("_w258bmc_20261017_probe_receipt.json", 10),
    ("_w258bmc_freeze_receipt.json", 1),
    ("MSG-20261017-0517-bmc-w258-seat", 7),
    ("d0d0d04a4", 2),
    ("989_735", 1),
    ("563_320", 1),
    ("(582_901, 584_900)", 1),
    ("(584_901, 585_100)", 1),
    ("W255_W256_W257_bands_respected_A", 1),
    ("W255_W256_W257_bands_respected_B", 1),
    ("B_base_above_W257_tail", 2),
    ("A_staircase_hop_past_W257_B", None),
    ("W259p_A_naive", 5),
    ("W259p_B_first_clean", 2),
    ("arith_a258", 6),
    ("arith_b258", 6),
    ('"PERPETUAL-N1-W258-SHARD-0"', 1),
    ("n1_w258_results.json", 2),
    ("n1_w258", 4),
    ("n1w258", 2),
    ("PERPETUAL-N1-W258", 7),
    ("_w258bmc", 11),
    ("w244_a", 12),
    ("SEVENTY-EIGHTH", 3),
    ("TWO HUNDRED AND FIFTY-EIGHTH", 3),
    ("forty-sixth consecutive", 2),
    ("bmc_ordinal=78", 7),
    ("78th own wave", 3),
    ("r1060 splice window", 3),
    ("r1060", 23),
    ("r1061", 7),
    ("r1062 freeze window", 1),
    ("estate 69", 1),
    ("= 116 rows", 2),
    ("116 parity", 2),
    ("hops=1", None),
    ("1-HOP", None),
    ("SEVENTH consecutive A-hop", None),
    ("EIGHTH consecutive above-own-A", None),
    # anti-gates: stale faces must be zero
    ("r1058", 0),
    ("r1059", 0),
    ("27ee6e95a", 0),
    ("c7fbc443c", 0),
    ("987,535", 0),
    ("561,120", 0),
    ("987_535", 0),
    ("561_120", 0),
    ("SEVENTY-SEVENTH", 0),
    ("TWO HUNDRED AND FIFTY-SEVENTH", 0),
    ("forty-fifth consecutive", 0),
    ("MSG-20261017-03xx", 0),
    ("authored 04:1x", 0),
    ("bmc_ordinal=77", 0),
    ("77th own wave", 0),
    ("247th", 0),
    ("246/129/76", 0),
    ("SEVENTH consecutive above-own-A", 0),
    ("FIRST A-hop", 0),
    ("seed-gap face ENDS", 0),
    ("580_501..582_500", 0),
    ("580_501..580_700", 0),
    ("580_701..580_900", 0),
    ("580_701..582_700", 0),
    ("580_700", 0),
    ("582_700", 0),
    ("580_501", 0),
    ("580_701", 0),
    ("~577_901..577_900", 0),
    ("(580_701, 582_700)", 0),
    ("(582_701, 582_900)", 0),
    ("== 114", 0),
    ("forty-five legs", 0),
    ("sixteen legs", 0),
    ("115 parity", 0),
    ("list(range(239, 256))", 0),
]:
    n = t.count(needle)
    if want is not None:
        assert n == want, f"OUTPUT-GATE {needle!r}: {n} != {want}"
    log.append(f"OUT {needle!r} = {n}")

'''
sect("# ============ structural output gates", 'io.open(DST, "w", encoding="utf-8", newline="").write(t)',
     NEW_GATES, "gates")

io.open(DST, "w", encoding="utf-8", newline="").write(t)
import py_compile
py_compile.compile(DST, doraise=True)
io.open(LOG, "w", encoding="utf-8").write("\n".join(log) + "\n")
print(f"BUILD OK -> {DST} ({len(t)} chars); {len(log)} log rows")
print("\n".join(log[-8:]))
