# -*- coding: utf-8 -*-
# r1063 bm-c: BUILD results/_w259bmc_derive_editor.py from the committed W258
# derive-editor canon (results/_w258bmc_derive_editor.py @ HEAD, blob
# 3367a967daff5bc93ecd50cffef37a6ff189846e) by machine splice (E63 11th-gen
# zero-transcription law: every replay-chain family literal + every replay
# sublist is spliced VERBATIM from the committed canon bytes; only the
# new-generation section texts are hand-authored here and every count is
# floor-asserted). Builder receipt: results/_r1063bmc_build_editor_log.txt.
import io, subprocess, sys

CANON = "results/_w258bmc_derive_editor.py"
DST = "results/_w259bmc_derive_editor.py"
LOG = "results/_r1063bmc_build_editor_log.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w258bmc_derive_editor.py"], capture_output=True, text=True).stdout.strip()
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
    """E258 final call  ->  E259: _X_W258 reconstruction line + NEW final call.
    The E258 final sublist text is extracted VERBATIM from the canon bytes."""
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
    nv = var[:-1] + "8"                       # _X_W257 -> _X_W258
    recon = (f"{nv} = mk258(age_prev3({var}), [{sublist}], \"{tag}-prev4\")")
    if kind == "rep":
        new_final = (f"rep(age({nv}),\n    mk(age({nv}), [{new_subs}\n    ], \"{tag}\"),\n    1, \"{tag}\")")
    else:
        new_final = (f"chunk(age({nv}),\n      mk(age({nv}), [{new_subs}\n      ], \"{tag}\"), \"{tag}\")")
    t = t[:i] + recon + "\n" + new_final + t[j:]
    log.append(f"extend {var}: final -> recon+final (sublist {len(sublist)}B spliced verbatim)")

# ---------- 1) header ----------
NEW_HEADER = r'''# -*- coding: utf-8 -*-
# r1063 bm-c: derive results/_w259bmc_freeze_edits.py from the committed W258
# freeze-edits script (results/_w258bmc_freeze_edits.py, proven live-fire W258
# splice bm-c r1062 window: splice 37ccebffd + engine self-burn 12/12
# [ledger appends 122485949 + cc72046d7] + finalize one-pass ledger 991,935 /
# K=565,520 five-key 6/6 by the r1062 closeout 16dba0e70)
# via COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage, 11th-gen pass ordering:
# P1 structural outputs BLANKET-IMMUNE; the W259 extraction faces move ONE
# structural face vs the W258 estate mandate -- the kept/dropped split
# boundary MOVES 240->241 per the frozen W259 prereg sec.3 mandate [kept
# W211..W240 (30) + dropped W241..W257 (17) + fresh W241..W258 (18) = 117
# parity rows W138..W206+W211..W258, the W259 block parity list enumerates
# W211..W258 with NO gap]; the boundary move = NEW-face direct-rep class
# this generation: four m240->m241 code faces + kept assert 29/range(211,240)
# -> 30/range(211,241) + dropped range lower bound + fresh-loop/leg-count
# lower bounds + the mat-hdr kept line, all pre-flight count-asserted).
# W259 facts (machine-read from the probe receipt _w259bmc_20261017, never
# transcribed):
# bands A 585_101..587_100 (1-HOP STAIRCASE-AFFECTS-A walk, EIGHTH
# consecutive A-hop -- the naive continuation 584_901..586_900 is REFUSED at
# its own start: the registered W258 B band 584_901..585_100 sits INSIDE the
# naive A window = staircase re-emergence continues to affect A, the W258
# prereg sec.5.5 item5 A-naive-CLEAN pre-W258-universe projection superseded
# live per r587, divergence disclosed; the walk hops past the W258 B tail
# 585_100 -> A first-clean 585_101..587_100, hops=1; A base == registered
# prior-wave B tail+1 (585_100+1) EXACT this window; A_clean_at_naive_start=
# false; A_staircase_hop_past_W258_B=true) /
# B 587_101..587_300 (1-HOP own-A RESERVATION CASCADE above own-A, NINTH
# consecutive above-own-A -- the naive continuation 585_101..585_300 is
# REFUSED at its own start -- the naive window lands INSIDE the own-wave
# W259 A first-clean window 585_101..587_100, own-A reservation cascade
# standard leg; the walk hops past the own-A tail 587_100 -> B landing
# 587_101..587_300, hops=1; B lands ABOVE own-A; B base == own-A tail+1
# (587_100+1) EXACT; B_naive_refused_at_start=true; B_lands_above_own_A=true;
# B_hop_lands_inside_A=false; hops=1), upstream W258 = bm-c own chain, seat
# MSG-20261017-0704-bmc-w259-seat @ origin 16dba0e70 (r1062 closeout, W259
# SEAT published post-W258-chain -- queue-head FREEZE-UNBLOCKED supply, zero
# waits-upstream), prereg b709bc2cc derived bm-c dead-r1063 window (authored
# 07:2x, banned_direction_gate ADMIT rc0, committed+pushed 07:39:54; splice
# window = r1063-continuation THIS window -- prereg window != splice window
# this generation, disclosed; W259 prereg freeze landed 07:39:54 by
# dead-r1063, estate machine-verified by this absorb window BEFORE splice).
# Needle law this generation: ALL chunk/repp needles are machine-derived via
# age() = the exact blanket composition (P2 W259->W260, P3 258->259,
# P4 257->258) applied to the W258-script-era literals; the era chunk faces
# are reconstructed by the FIVE-LEVEL chain mk255(age_prev255(W254 literal))
# -> mk256(age_prev(...)) -> mk257(age_prev2(...)) -> mk258(age_prev3(...))
# -> age() needle (E63 11th-gen, disclosed; needle pre-flight probe
# results/_w259bmc_editor_needle_preflight.py ALL PASS -- faces measured
# on the committed W258 freeze-edits script; this editor itself was built by
# the machine-splice builder results/_r1063bmc_build_editor.py -- family
# literals + replay sublists spliced verbatim from the committed E258 canon
# bytes, zero hand-transcription).
# Date-stable face this generation: the probe receipt basename date does NOT
# roll AGAIN (20261017 == 20261017, third consecutive date-stable
# generation) -- the P5f rep is an identity count-assert (10x), zero heal
# needed (disclosed).
'''
sect(t.split("\n", 1)[0], "import io, os, subprocess, sys", NEW_HEADER, "hdr")

# ---------- 2) path faces + blob sha (order: DST/LOG first, then SRC) ----------
rep('"_w258bmc_freeze_edits.py"', '"_w259bmc_freeze_edits.py"', 1, "dst-path")
rep('"_w258bmc_derive_editor_log.txt"', '"_w259bmc_derive_editor_log.txt"', 1, "log-path")
rep('"_w257bmc_freeze_edits.py"', '"_w258bmc_freeze_edits.py"', 1, "src-path")
rep('HEAD:results/_w257bmc_freeze_edits.py', 'HEAD:results/_w258bmc_freeze_edits.py', 1, "src-blob-path")
rep('assert blob_wt == "8889dc881a075f0332dd268bb760a960f2974e59"',
    'assert blob_wt == "aa9ae1bf918593902cfd90b301edcfac390d2d50"', 1, "src-blob-sha")

# ---------- 3) era functions (five-level era chain this generation) ----------
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
# the W256-era faces.
def age_prev2(s):
    s = s.replace("W257", "W258")
    s = s.replace("256", "257")
    s = s.replace("255", "256")
    return s

# age_prev3(): the W258 editor's blanket composition (P2 W258->W259,
# P3 257->258, P4 256->257) -- reconstructs the W258-script chunk faces from
# the W257-era faces (NEW level this generation, disclosed; body = the W258
# editor's age() verbatim).
def age_prev3(s):
    s = s.replace("W258", "W259")
    s = s.replace("257", "258")
    s = s.replace("256", "257")
    return s

# age(): EXACT composition of MY blanket passes (P2 downstream W259->W260,
# P3 self 258->259, P4 upstream 257->258) -- derives post-pass needles from
# W258-script-era literals WITHOUT hand-derivation.
def age(s):
    s = s.replace("W259", "W260")
    s = s.replace("258", "259")
    s = s.replace("257", "258")
    return s

'''
sect("# age_prev255(): the W255 editor", "def rep(old, new, expect=None, tag=", NEW_ERAS, "eras")

# ---------- 4) mk258 def insert + mk() comment roll ----------
NEW_MK258 = r'''# mk258(): rebuild the W258-script chunk from the W257-era face (asserts
# the W258 editor's fact subs exactly as the r1062 editor ran them; NEW
# level this generation, disclosed).
def mk258(needle, repls, tag):
    s = needle
    for old, new, cnt in repls:
        n = s.count(old)
        assert n == cnt, f"[{tag}.{s.count(old)}] sub {old[:56]!r}: {n} != {cnt}"
        s = s.replace(old, new)
    return s

'''
sect("# mk(): build a chunk NEW text", "def mk(needle, repls, tag):",
     NEW_MK258 + '# mk(): build a chunk NEW text from its (post-blanket) needle via ordered\n# count-asserted fact replacements -- W259 facts from the probe receipt.\n\n', "mk258")
# mk-comment-roll: NOT owed this generation (disclosed) -- the r1062-era second
# "W2xx facts from the probe receipt" occurrence rode inside a region the r1062
# builder's own later sects consumed; the canon W258 editor carries exactly ONE
# occurrence (the mk comment) and THIS sect already rolls it to the W259 form,
# zero leftover face (grep evidence: 1 hit @ L152 pre-sect).

# ---------- 5) P1..P4x ----------
NEW_P1_P4X = r'''# ============ P1: structural faces, BLANKET-IMMUNE outputs ============
rep("(254, 253, 252, 251, 250, 249, 248, 247, 246, 245)",
    "(255, 254, 253, 252, 251, 250, 249, 248, 247, 246)", 2, "P1-transitive-deps")
rep("range(209, 259)", "range(209, 260)", 2, "P1-liveness-range")
rep('def fmt(n):  # 582901 -> "582_901"', 'def fmt(n):  # 585101 -> "585_101"', 1, "P1-fmt-comment")

# ============ P2: downstream shift W259 -> W260 ============
rep("W259", "W260", None, "P2-downstream")
assert "W259" not in t, "P2 leftover W259"

# ============ P3: self shift 258 -> 259 ============
n258 = t.count("258")
rep("258", "259", None, "P3-self")
log.append(f"P3 consumed {n258} '258' substrings")

# ============ P4: upstream shift 257 -> 258 ============
n257 = t.count("257")
rep("257", "258", None, "P4-upstream")
log.append(f"P4 consumed {n257} '257' substrings")

# ============ P4x: blanket-exemption heal (NONE this generation, disclosed) ============
# the MY-blanket upstream shift rep("257","258") does NOT hit the FOUR
# "hashlib.sha256" API-name occurrences inside the source (sha256 contains
# "256" but NOT "257"/"258"; vs the r1062 editor whose 256->257 upstream
# shift DID hit it) -- zero heal needed this generation, the canon's
# P4x sha256-heal code face is retired with this section replace (pre-flight
# evidence: sha256=4 / sha257=0 / sha258=0 on the committed W258 script).

'''
sect("# ============ P1: structural faces", "# ============ P5a: numeric/anchor", NEW_P1_P4X, "P1-P4x")

# ---------- 6) P5a ----------
NEW_P5A = r'''# ============ P5a: numeric/anchor/ordinal/window faces (post-blanket forms) ============
# r-window ORDER DISCLOSURE (needle-heal family, vs the W258 editor order):
# the source's own prereg-window refs are r1061 (7x) AND its freeze stamp is
# "r1062 freeze window" (1x header) -- the E259 chain reps CREATE new "r1062"
# strings (from the 23 "r1060" refs), so the header-window rep runs FIRST
# (consumes the unique full-stamp needle BEFORE any r1060->r1062 creation
# lands), prereg-window second, closeout/splice/rest after. Counts
# pre-flight-verified on the committed W258 script: r1061=7 / r1060=23
# (1 closeout + 3 splice-window + 19 rest) / r1062=1 (header stamp only).
rep(age("2026-10-17 06:2x bm-c r1062 freeze window"), "2026-10-17 07:3x bm-c r1063 freeze window", 1, "P5a-header-window")
rep(age("r1061"), "r1063", 7, "P5a-prereg-window")
rep(age("W257 finalize one-pass bm-c r1060 window closeout 05:1x"),
    "W258 finalize one-pass bm-c r1062 window closeout 07:0x", 1, "P5a-closeout-window")
rep(age("r1060 splice window"), "r1062 splice window", 3, "P5a-splice-window")
rep(age("r1060"), "r1062", 19, "P5a-splice-window-rest")
rep(age("authored 05:5x"), "authored 07:3x", 2, "P5a-authored-time")
rep(age("989_735"), "991_935", 1, "P5a-ledger-int")
rep(age("563_320"), "565_520", 1, "P5a-k-int")
rep(age("989,735"), "991,935", 8, "P5a-ledger-prose")
rep(age("563,320"), "565,520", 8, "P5a-k-prose")
rep(age("bmc_ordinal=78"), "bmc_ordinal=79", 7, "P5a-ordinal77")
rep(age("SEVENTY-EIGHTH"), "SEVENTY-NINTH", 3, "P5a-seventyseventh")
rep(age("TWO HUNDRED AND FIFTY-EIGHTH"), "TWO HUNDRED AND FIFTY-NINTH", 3, "P5a-250th")
rep(age("forty-sixth consecutive"), "forty-seventh consecutive", 2, "P5a-finface")
rep(age("78th own wave"), "79th own wave", 3, "P5a-77th-ownwave")
rep(age("MSG-20261017-0517-bmc-w258-seat"), "MSG-20261017-0704-bmc-w259-seat", 7, "P5a-seat-msg")
rep(age("d0d0d04a4"), "16dba0e70", 2, "P5a-seat-origin")
rep(age("824b46d31"), "b709bc2cc", 1, "P5a-prereg-commit")
# aging-face needle heals (same-window disclosed, r1045/r1047/r1050/r1055/r1057/r1058/r1062 precedent family):
rep(age("transitive window W245..W254 checked"), "transitive window W246..W255 checked", 1, "P5a-aging-deps-cmt")
rep(age("engine_owner==bm-c rows 77 + candidate"), "engine_owner==bm-c rows 78 + candidate", 1, "P5a-aging-rows-heal")

'''
sect("# ============ P5a: numeric/anchor", "# ============ P5b: extraction count faces", NEW_P5A, "P5a")

# ---------- 7) P5b direct (pre-chain) ----------
NEW_P5B = r'''# ============ P5b: extraction count faces (frozen W259 prereg sec.3 mandate) ============
# estate 69 (W138..W206) UNCHANGED; kept W211..W240 (30); dropped W241..W257
# (17); fresh W241..W258 (18); total parity 117 rows; legs segment
# W211..W257 (47). NEW FACE this generation (disclosed): the kept/dropped
# split boundary MOVES 240->241 per the frozen W259 prereg sec.3 mandate
# (kept W211..W240 30 legs -- the W259 block parity list enumerates W211..W258
# with NO gap, so W240 moves from the dropped set into the kept set); four
# m240->m241 code faces + kept/dropped range faces + fresh-loop lower bounds
# are count-asserted direct reps (pre-flight: m240=4 / range(240,258)=2 /
# kept-29=1 / dropped-17=1).
rep(age("# block's own W240..W256 legs (17 rows) do NOT enter the estate path;"),
    "# block's own W241..W257 legs (17 rows) do NOT enter the estate path;", 1, "P5b-hdr-ownlegs")
rep(age("# after extraction, fresh W240..W257 legs (18 rows) are added,"),
    "# after extraction, fresh W241..W258 legs (18 rows) are added,", 1, "P5b-hdr-freshlegs")
rep(age("# parity = 116 rows (W138..W206 + W211..W257). Zero assumption zero risk."),
    "# parity = 117 rows (W138..W206 + W211..W258). Zero assumption zero risk.", 1, "P5b-hdr-parity-count")
rep(age("# block's own W240..W256 legs (17) are EXCLUDED from the estate path per the"),
    "# block's own W241..W257 legs (17) are EXCLUDED from the estate path per the", 1, "P5b-ext-excl")
rep(age("# prereg mandate; the W258 block appends fresh W240..W257 legs (18,"),
    "# prereg mandate; the W259 block appends fresh W241..W258 legs (18,", 1, "P5b-ext-fresh")
rep(age("# machine-derived from the LIVE pf registry at freeze time) -> 116 parity"),
    "# machine-derived from the LIVE pf registry at freeze time) -> 117 parity", 1, "P5b-ext-parcount")
'''
sect("# ============ P5b: extraction count faces", "_PARFULL_W255 = ", NEW_P5B, "P5b-direct")

# ---------- 8) P5b chains: extend 4 families ----------
extend_family("_PARFULL_W257", "rep", "P5b-parfull",
    '\n        ("== 115", "== 116", 1),\n        ("!= 115 (69 estate + W211..W256 legs 46)", "!= 116 (69 estate + W211..W257 legs 47)", 1),')
extend_family("_LEGS_W257", "rep", "P5b-legs-assert",
    '\n        ("== 46", "== 47", 1),\n        ("legs segment not W211..W256 forty-six legs", "legs segment not W211..W257 forty-seven legs", 1),')
extend_family("_DROP_W257", "rep", "P5b-dropped-assert",
    '\n        ("list(range(240, 258))", "list(range(241, 258))", 1),\n        ("dropped segment not W240..W256 seventeen legs", "dropped segment not W241..W257 seventeen legs", 1),')
extend_family("_RCPTNOTE_W257", "rep", "P5b-rcpt-note",
    '\n        ("own W240..W256 legs (17) EXCLUDED", "own W241..W257 legs (17) EXCLUDED", 1),\n        ("fresh W240..W258 legs (18) machine-derived", "fresh W241..W258 legs (18) machine-derived", 1),\n        ("W259 block = 116 rows", "W259 block = 117 rows", 1),\n        ("E63 10th-gen", "E63 11th-gen", 1),\n        ("W211..W239 legs (29)", "W211..W240 legs (30)", 1),\n        ("list(range(211,258))/list(range(211,240))/list(range(240,258))", "list(range(211,258))/list(range(211,241))/list(range(241,258))", 1),')

# ---------- 9) P5b late (split/boundary/mat/rcpt-identity reps) ----------
NEW_P5B_LATE = r"""# NEW-FACE split-boundary reps (240 -> 241, frozen W259 prereg sec.3 mandate):
rep(age("# prereg sec.3 mandate split: keep W211..W239 verbatim (29 legs); the W257\n# block's own W240..W256 legs (17) are excluded from the estate path"),
    "# prereg sec.3 mandate split: keep W211..W240 verbatim (30 legs); the W258\n# block's own W241..W257 legs (17) are excluded from the estate path", 1, "P5b-split-cmt")
rep(r'm240 = re.search(r" *assert pf\.N1_BANDS\[240\] ==", legs_sec)',
    r'm241 = re.search(r" *assert pf\.N1_BANDS\[241\] ==", legs_sec)', 1, "P5b-split-mvar")
rep('assert m240, "W240 leg boundary not found inside W259 legs segment (prereg sec.3 split face)"',
    'assert m241, "W241 leg boundary not found inside W259 legs segment (prereg sec.3 split face)"', 1, "P5b-split-assert")
rep("legs_kept = legs_sec[:m240.start()]", "legs_kept = legs_sec[:m241.start()]", 1, "P5b-split-kept")
rep("legs_dropped = legs_sec[m240.start():]", "legs_dropped = legs_sec[m241.start():]", 1, "P5b-split-dropped")
# kept assert moves 29/range(211,240) -> 30/range(211,241) (NEW face, pre-flight raw count 1):
_KEPT_W258 = '''assert legs_kept.count("assert pf.N1_BANDS[") == 29 \\
    and [int(w) for w in _kept_ws] == list(range(211, 240)), \\
    f"kept segment not W211..W239 twenty-nine legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"'''
rep(_KEPT_W258, '''assert legs_kept.count("assert pf.N1_BANDS[") == 30 \\
    and [int(w) for w in _kept_ws] == list(range(211, 241)), \\
    f"kept segment not W211..W240 thirty legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"''', 1, "P5b-kept-assert")
# fresh-loop + leg-count-loop lower bounds + fresh first-line assert (NEW face):
rep(age("for _w in range(240, 258):"), "for _w in range(241, 259):", 1, "P5b-fresh-loop")
rep(age("for _lw in range(240, 258):"), "for _lw in range(241, 259):", 1, "P5b-legcount-loop")
rep("assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[240] == {\"a\": (')",
    "assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[241] == {\"a\": (')", 1, "P5b-fresh-firstline")
# receipt count faces: fresh stays 18 this generation = identity count-asserts (disclosed):
rep(age('"fresh_legs_row_asserts": 18,'), '"fresh_legs_row_asserts": 18,', 1, "P5b-rcpt-fresh18-identity")
rep(age('+ legs_kept.count("assert pf.N1_BANDS[") + 18,'), '+ legs_kept.count("assert pf.N1_BANDS[") + 18,', 1, "P5b-rcpt-total18-identity")
# materializer hdr comment faces:
rep(age('"    #     W211..W239 legs (29) extracted verbatim from the OWN W257 block",'),
    '"    #     W211..W240 legs (30) extracted verbatim from the OWN W258 block",', 1, "P5b-hdr-kept-mat")
rep(age('"    #     physical bytes; the W258 block\'s own W240..W256 legs (17) are",'),
    '"    #     physical bytes; the W259 block\'s own W241..W257 legs (17) are",', 1, "P5b-hdr-ownlegs-mat")
rep(age('"    #     W240..W257 legs (18) added, machine-derived from the live pf",'),
    '"    #     W241..W258 legs (18) added, machine-derived from the live pf",', 1, "P5b-hdr-freshlegs-mat")
rep(age('"    #     registry at freeze time -> 116 parity rows (W138..W206+W211..W257).",'),
    '"    #     registry at freeze time -> 117 parity rows (W138..W206+W211..W258).",', 1, "P5b-hdr-parcount-mat")

"""
sect('rep(age("# prereg sec.3 mandate split:', '# receipt note (single big face: counts + generation stamp)', NEW_P5B_LATE, "P5b-late")

# ---------- 10) P5c ----------
NEW_P5C = r'''# ============ P5c: band literals (probe ADMIT receipt bands) ============
rep(age('assert (a_lo, a_hi) == (582_901, 584_900) and (b_lo, b_hi) == (584_901, 585_100), \\'),
    'assert (a_lo, a_hi) == (585_101, 587_100) and (b_lo, b_hi) == (587_101, 587_300), \\', 1, "P5c-band-drift")

'''
sect("# ============ P5c: band literals", "# ============ P5d: ordinal/leg0", NEW_P5C, "P5c")

# ---------- 11) P5d ----------
NEW_P5D = r'''# ============ P5d: ordinal/leg0/deps faces ============
rep(age('assert len(owner_rows_live) == 247 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 77, \\'),
    'assert len(owner_rows_live) == 248 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 78, \\', 1, "P5d-ord-gate")
# needle narrowed to the pre-registration numeric face: the trailing "79th own
# wave" inside this line was ALREADY rewritten by the P5a-78th-ownwave rep
# (order-sensitive face, W258 editor canon -- its P5d needle was likewise the
# post-P5a form); disclosed needle heal, evidence = pre-flight n=1 raw face.
rep(age("(expect 247/129/77 PRE-splice post-W257 registration"),
    "(expect 248/129/78 PRE-splice post-W258 registration", 1, "P5d-ord-err")
# needle narrowed likewise: the trailing "bmc_ordinal=79" on this line was
# already rewritten by the P5a-ordinal78 rep (one of its 7 faces).
rep(age('# receipt leg0 face owner_rows=247 / bmc_rows=77 /'),
    '# receipt leg0 face owner_rows=248 / bmc_rows=78 /', 1, "P5d-leg0-prose")
rep(age("-> owner rows 247 + candidate = 248th EXACT; bm-c rows 77 +"),
    "-> owner rows 248 + candidate = 249th EXACT; bm-c rows 78 +", 1, "P5d-ord-owner-prose")
rep(age("# candidate = 78th EXACT -- bm-c own-seat continuity face (bm-c published the"),
    "# candidate = 79th EXACT -- bm-c own-seat continuity face (bm-c published the", 1, "P5d-ord-bmc-prose")
rep(age("freeze-time live face owner rows 247 + candidate = 248th EXACT"),
    "freeze-time live face owner rows 248 + candidate = 249th EXACT", 1, "P5d-rcpt-247th")
rep(age("freeze-time live derive bmc rows 77 + candidate 78th EXACT per r587/r359"),
    "freeze-time live derive bmc rows 78 + candidate 79th EXACT per r587/r359", 1, "P5d-bundle-77th")
rep(age("post-W257 registration: bm-c rows 77 + candidate = 78th owned"),
    "post-W258 registration: bm-c rows 78 + candidate = 79th owned", 1, "P5d-rcpt-77th-owned")
rep(age('"probe_receipt_bmc_ordinal_face": 78,'), '"probe_receipt_bmc_ordinal_face": 79,', 1, "P5d-rcpt-ordface")
rep(age('f"W258+W253..W244 finalize products present "'), 'f"W259+W254..W245 finalize products present "', 1, "P5d-print-deps")

'''
sect("# ============ P5d: ordinal/leg0", "# ============ P5e: A/B face structural", NEW_P5D, "P5d")

# ---------- 12) P5e families (extend; new final subs = W259 facts) ----------
extend_family("_HDR_W257", "chunk", "P5e-hdr",
    '\n          ("EIGHTH consecutive\\n# above-own-A", "NINTH consecutive\\n# above-own-A", 1),\n          ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 1),\n          ("582_901..584_900", "585_101..587_100", 2),\n          ("584_901..585_100", "587_101..587_300", 1),\n          ("582_701..584_700", "584_901..586_900", 1),\n          ("582_701..582_900", "584_901..585_100", 1),\n          ("582_901..583_100", "585_101..585_300", 1),\n          ("582_900", "585_100", 2),\n          ("584_900", "587_100", 2),')
extend_family("_BANDFACTS_W257", "chunk", "P5e-bandfacts",
    '\n          ("EIGHTH consecutive above-own-A landing", "NINTH consecutive above-own-A landing", 1),\n          ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 2),')
extend_family("_A_BASE_W257", "rep", "P5e-a-base",
    ' ("seventh consecutive A-hop", "eighth consecutive A-hop", 1),')
extend_family("_A_FLOOR_W257", "rep", "P5e-a-floor",
    ' ("seventh consecutive A-hop", "eighth consecutive A-hop", 1),')
extend_family("_B_BASE_W257", "rep", "P5e-b-base",
    ' ("eighth consecutive above-own-A", "ninth consecutive above-own-A", 1),')
extend_family("_RA_GATE_W257", "rep", "P5e-ra-gate",
    '\n        ("W255_W256_W258_bands_respected_A", "W256_W257_W258_bands_respected_A", 1),\n        ("W255_W256_W258_bands_respected_B", "W256_W257_W258_bands_respected_B", 1),')
extend_family("_PFCMT_W257", "chunk", "P5e-pfcmt",
    '\n          ("EIGHTH consecutive above-own-A;", "NINTH consecutive above-own-A;", 1),\n          ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 1),\n          ("hops=1 -- SIXTH", "hops=1 -- SEVENTH", 1),')
extend_family("_PRE_W257", "chunk", "P5e-pre",
    '\n          ("EIGHTH consecutive above-own-A", "NINTH consecutive above-own-A", 1),\n          ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 2),')
extend_family("_MEM_A_W257", "rep", "P5e-mem-a",
    '\n        ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 1),\n        ("seventh consecutive A-hop", "eighth consecutive A-hop", 1),')
extend_family("_MEM_B_W257", "rep", "P5e-mem-b",
    ' ("eighth consecutive above-own-A", "ninth consecutive above-own-A", 1),')
extend_family("_TAILCMT_W257", "chunk", "P5e-tailcmt",
    '\n          ("EIGHTH consecutive", "NINTH consecutive", 1),\n          ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 2),')
extend_family("_TAIL_AMSG_W257", "rep", "P5e-tail-amsg",
    ' ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 2),')
extend_family("_EXCL_W257", "rep", "P5e-tail-excl",
    ' ("eighth consecutive above-own-A", "ninth consecutive above-own-A", 1),')
extend_family("_PRCHUNK_W257", "chunk", "P5e-pr",
    '\n          ("EIGHTH consecutive above-own-A landing", "NINTH consecutive above-own-A landing", 1),\n          ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 1),')
extend_family("_SEM_A_W257", "rep", "P5e-rcpt-semantics-A",
    '\n        ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 2),\n        ("582_701..584_700 refused", "584_901..586_900 refused", 1),\n        ("582_701..582_900 sits", "584_901..585_100 sits", 1),\n        ("B tail 582_900 -> A first-clean 582_901..584_900", "B tail 585_100 -> A first-clean 585_101..587_100", 1),\n        ("(582_900+1) EXACT)", "(585_100+1) EXACT)", 1),')
extend_family("_SEM_B_W257", "rep", "P5e-rcpt-semantics-B",
    '\n        ("EIGHTH consecutive above-own-A landing", "NINTH consecutive above-own-A landing", 1),\n        ("582_901..583_100 is refused", "585_101..585_300 is refused", 1),\n        ("A first-clean window 582_901..584_900 (own-A", "A first-clean window 585_101..587_100 (own-A", 1),\n        ("own-A tail 584_900 -> B landing 584_901..585_100;", "own-A tail 587_100 -> B landing 587_101..587_300;", 1),\n        ("(584_900+1) EXACT)", "(587_100+1) EXACT)", 1),')
extend_family("_DOWNSTREAM_W257", "rep", "P5e-rcpt-downstream",
    '\n        ("A naive 584901..586900 CLEAN", "A naive 587101..589100 CLEAN", 1),\n        ("B naive 585101..585300 hops=0 CLEAN at naive, first-clean 585101..585300 BUT", "B naive 587301..587500 hops=0 CLEAN at naive, first-clean 587301..587500 BUT", 1),\n        ("naive A window start 584_901 lands INSIDE the registered W259 B band 584_901..585_100", "naive A window start 587_101 lands INSIDE the registered W259 B band 587_101..587_300", 1),')

# identity reps: FOUR-level inline chain -> FIVE-level (age_prev3 inserted;
# full-block replace keeps paren balance, disclosed):
rep("""rep(age(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')),
    )), age(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')))), 1, "P5e-tail-bassert2")""",
    """rep(age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')),
    ))), age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "'))))), 1, "P5e-tail-bassert2")""",
    1, "identity-5level-bassert2")
rep("""rep(age(age_prev2(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"')),
    )), age(age_prev2(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"')))), 1, "P5e-tail-bclean")""",
    """rep(age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"')),
    ))), age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"'))))), 1, "P5e-tail-bclean")""",
    1, "identity-5level-bclean")

# family-section comment roll:
rep("# downstream W259+ projection face (probe leg4 verbatim numbers)",
    "# downstream W260+ projection face (probe leg4 verbatim numbers)", 1, "downstream-cmt-roll")

# ---------- 13) P5f ----------
NEW_P5F = r'''# ============ P5f: probe-receipt date face (DATE-STABLE this generation) ============
# disclosed date-stable face: the W259 probe receipt basename keeps the SAME
# date AGAIN (20261017 == 20261017, third consecutive date-stable
# generation) -- the blanket P3 already rolled the basename to
# _w259bmc_20261017_probe_receipt.json which IS the correct on-disk name;
# this rep is an identity count-assert (10x), zero heal needed (vs the W256
# editor's 10x date-roll rep 20261016->20261017). Position stays POST-P5e
# (the pfcmt chunk needle embeds the pre-replacement basename face).
rep(age("_w258bmc_20261017_probe_receipt.json"), "_w259bmc_20261017_probe_receipt.json", 10, "P5f-probe-receipt-date-stable")

'''
sect("# ============ P5f: probe-receipt date face", "# ============ structural output gates", NEW_P5F, "P5f")

# ---------- 14) output gates ----------
NEW_GATES = r'''# ============ structural output gates ============
for needle, want in [
    ("# --- W259 materializer face", 2),
    ("# --- W258 materializer face", 1),
    ('"+ W259 materializer face', 2),
    ("range(16, 259)", 2),
    ("range(17, 259)", 3),
    ("range(241, 259)", 2),
    ("range(240, 259)", 0),
    ("list(range(211, 258)),", 1),
    ("list(range(211, 241))", 1),
    ("list(range(211, 240))", 0),
    ("list(range(241, 258)),", 1),
    ("range(209, 260)", 2),
    ("if w < 259)", 5),
    ("if w < 258)", 1),
    ("m241", 4),
    ("m240", 0),
    ("_w259bmc_20261017_probe_receipt.json", 10),
    ("_w259bmc_freeze_receipt.json", 1),
    ("MSG-20261017-0704-bmc-w259-seat", 7),
    ("16dba0e70", 2),
    ("991_935", 1),
    ("565_520", 1),
    ("(585_101, 587_100)", 1),
    ("(587_101, 587_300)", 1),
    ("W256_W257_W258_bands_respected_A", 1),
    ("W256_W257_W258_bands_respected_B", 1),
    ("B_base_above_W258_tail", 2),
    ("A_staircase_hop_past_W258_B", None),
    ("W260p_A_naive", 5),
    ("W260p_B_first_clean", 2),
    ("arith_a259", 6),
    ("arith_b259", 6),
    ('"PERPETUAL-N1-W259-SHARD-0"', 1),
    ("n1_w259_results.json", 2),
    ("n1_w259", 4),
    ("n1w259", 2),
    ("PERPETUAL-N1-W259", 7),
    ("_w259bmc", 11),
    ("w245_a", 12),
    ("SEVENTY-NINTH", 3),
    ("TWO HUNDRED AND FIFTY-NINTH", 3),
    ("forty-seventh consecutive", 2),
    ("bmc_ordinal=79", 7),
    ("79th own wave", 3),
    ("r1062 splice window", 3),
    ("r1062", 23),
    ("r1063", 7),
    ("r1063 freeze window", 1),
    ("estate 69", 1),
    ("= 117 rows", 2),
    ("117 parity", 2),
    ("hops=1", None),
    ("1-HOP", None),
    ("EIGHTH consecutive A-hop", None),
    ("NINTH consecutive above-own-A", None),
    # anti-gates: stale faces must be zero
    ("r1060", 0),
    ("r1061", 0),
    ("d0d0d04a4", 0),
    ("824b46d31", 0),
    ("989,735", 0),
    ("563,320", 0),
    ("989_735", 0),
    ("563_320", 0),
    ("SEVENTY-EIGHTH", 0),
    ("TWO HUNDRED AND FIFTY-EIGHTH", 0),
    ("forty-sixth consecutive", 0),
    ("MSG-20261017-0517", 0),
    ("authored 05:5x", 0),
    ("bmc_ordinal=78", 0),
    ("78th own wave", 0),
    ("249th", 0),
    ("248/129/78", 0),
    ("EIGHTH consecutive above-own-A", 0),
    ("FIRST A-hop", 0),
    ("seed-gap face ENDS", 0),
    ("582_701..584_700", 0),
    ("582_701..582_900", 0),
    ("582_901..583_100", 0),
    ("582_901..584_900", 0),
    ("582_900", 0),
    ("584_900", 0),
    ("582_701", 0),
    ("582_901", 0),
    ("~577_901..577_900", 0),
    ("(582_901, 584_900)", 0),
    ("(584_901, 585_100)", 0),
    ("== 115", 0),
    ("forty-six legs", 0),
    ("sixteen legs", 0),
    ("116 parity", 0),
    ("list(range(240, 257))", 0),
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
