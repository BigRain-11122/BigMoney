# -*- coding: utf-8 -*-
# r1065 bm-c: BUILD results/_w260bmc_derive_editor.py from the committed W259
# derive-editor canon (results/_w259bmc_derive_editor.py @ HEAD) by machine
# splice (E63 12th-gen zero-transcription law: every replay-chain family
# literal + every replay sublist is spliced VERBATIM from the committed canon
# bytes; only the new-generation section texts are hand-authored here and every
# count is floor-asserted). Builder receipt: results/_r1065bmc_build_editor_log.txt.
# Pre-flight evidence: results/_w260bmc_editor_needle_counts.txt (measured on the
# committed W259 freeze-edits T0 blob 601de02f483acb8a0dfbf048cce200607f3a6fb2).
import io, subprocess, sys

CANON = "results/_w259bmc_derive_editor.py"
DST = "results/_w260bmc_derive_editor.py"
LOG = "results/_r1065bmc_build_editor_log.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w259bmc_derive_editor.py"], capture_output=True, text=True).stdout.strip()
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
    """E259 final call  ->  E260: _X_W259 reconstruction line + NEW final call.
    The E259 final sublist text is extracted VERBATIM from the canon bytes."""
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
    nv = var[:-1] + "9"                       # _X_W258 -> _X_W259
    recon = (f"{nv} = mk259(age_prev4({var}), [{sublist}], \"{tag}-prev5\")")
    if kind == "rep":
        new_final = (f"rep(age({nv}),\n    mk(age({nv}), [{new_subs}\n    ], \"{tag}\"),\n    1, \"{tag}\")")
    else:
        new_final = (f"chunk(age({nv}),\n      mk(age({nv}), [{new_subs}\n      ], \"{tag}\"), \"{tag}\")")
    t = t[:i] + recon + "\n" + new_final + t[j:]
    log.append(f"extend {var}: final -> recon+final (sublist {len(sublist)}B spliced verbatim)")

# ---------- 1) header ----------
NEW_HEADER = r'''# -*- coding: utf-8 -*-
# r1065 bm-c: derive results/_w260bmc_freeze_edits.py from the committed W259
# freeze-edits script (results/_w259bmc_freeze_edits.py, proven live-fire W259
# splice bm-c r1064 window: splice 89aeea31b + engine self-burn 12/12
# [ledger appends 85e44f6a6 + 778bd1c04 + ceeb47cda] + finalize one-pass
# ledger 994,135 / K=567,720 five-key 6/6 + sec.7/8 backfilled by the r1064
# closeout 09:19:26)
# via COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage, 12th-gen pass ordering:
# P1 structural outputs BLANKET-IMMUNE; the W260 extraction faces move ONE
# structural face vs the W259 estate mandate -- the kept/dropped split
# boundary MOVES 241->242 per the frozen W260 prereg sec.3 mandate [kept
# W211..W241 (31) + dropped W242..W258 (17) + fresh W242..W259 (18) = 118
# parity rows W138..W206+W211..W259, the W260 block parity list enumerates
# W211..W259 with NO gap]; the boundary move = NEW-face direct-rep class
# this generation: five m241->m242 code faces + kept assert 30/range(211,241)
# -> 31/range(211,242) + dropped range lower bound + fresh-loop/leg-count
# lower bounds + the mat-hdr kept line, all pre-flight count-asserted).
# W260 facts (machine-read from the probe receipt _w260bmc_20261017, never
# transcribed):
# bands A 587_301..589_300 (1-HOP STAIRCASE-AFFECTS-A walk, NINTH
# consecutive A-hop -- the naive continuation 587_101..589_100 is REFUSED at
# its own start: the registered W259 B band 587_101..587_300 sits INSIDE the
# naive A window = staircase re-emergence continues to affect A, the W259
# prereg sec.5.5 item5 A-naive-CLEAN pre-W259-universe projection superseded
# live per r587, divergence disclosed; the walk hops past the W259 B tail
# 587_300 -> A first-clean 587_301..589_300, hops=1; A base == registered
# prior-wave B tail+1 (587_300+1) EXACT this window; A_clean_at_naive_start=
# false; A_staircase_hop_past_W259_B=true) /
# B 589_301..589_500 (1-HOP own-A RESERVATION CASCADE above own-A, TENTH
# consecutive above-own-A -- the naive continuation 587_301..587_500 is
# REFUSED at its own start -- the naive window lands INSIDE the own-wave
# W260 A first-clean window 587_301..589_300, own-A reservation cascade
# standard leg; the walk hops past the own-A tail 589_300 -> B landing
# 589_301..589_500, hops=1; B lands ABOVE own-A; B base == own-A tail+1
# (589_300+1) EXACT; B_naive_refused_at_start=true; B_lands_above_own_A=true;
# B_hop_lands_inside_A=false; hops=1), upstream W259 = bm-c own chain, seat
# MSG-20261017-0910-bmc-w260-seat @ origin 9fa2c8aed (r1064 closeout, W260
# SEAT published post-W259-chain -- queue-head FREEZE-UNBLOCKED supply, zero
# waits-upstream), prereg 0f33f9abc derived bm-c dead-r1065 window (authored
# 10:2x, banned_direction_gate ADMIT rc0, committed+pushed ~10:2x; splice
# window = r1065-continuation THIS window -- prereg window == splice window
# r-number this generation, disclosed).
# Needle law this generation: ALL chunk/repp needles are machine-derived via
# age() = the exact blanket composition (P2 W260->W261, P3 259->260,
# P4 258->259) applied to the W259-script-era literals; the era chunk faces
# are reconstructed by the SIX-LEVEL chain mk255(age_prev255(W254 literal))
# -> mk256 -> mk257 -> mk258 -> mk259(age_prev4(...)) -> age() needle
# (E63 12th-gen, disclosed; needle pre-flight probe
# results/_w260bmc_editor_needle_preflight.py RUN 10:56 by the dead-r1065
# window -- faces measured on the committed W259 freeze-edits script; this
# editor itself was built by the machine-splice builder
# results/_r1065bmc_build_editor.py -- family literals + replay sublists
# spliced verbatim from the committed E259 canon bytes, zero
# hand-transcription).
# Date-stable face this generation: the probe receipt basename date does NOT
# roll AGAIN (20261017 == 20261017, fourth consecutive date-stable
# generation) -- the P5f rep is an identity count-assert (10x), zero heal
# needed (disclosed).
'''
sect(t.split("\n", 1)[0], "import io, os, subprocess, sys", NEW_HEADER, "hdr")

# ---------- 2) path faces + blob sha (order: DST/LOG first, then SRC) ----------
rep('"_w259bmc_freeze_edits.py"', '"_w260bmc_freeze_edits.py"', 1, "dst-path")
rep('"_w259bmc_derive_editor_log.txt"', '"_w260bmc_derive_editor_log.txt"', 1, "log-path")
rep('"_w258bmc_freeze_edits.py"', '"_w259bmc_freeze_edits.py"', 1, "src-path")
rep('HEAD:results/_w258bmc_freeze_edits.py', 'HEAD:results/_w259bmc_freeze_edits.py', 1, "src-blob-path")
rep('assert blob_wt == "aa9ae1bf918593902cfd90b301edcfac390d2d50"',
    'assert blob_wt == "601de02f483acb8a0dfbf048cce200607f3a6fb2"', 1, "src-blob-sha")

# ---------- 3) era functions (six-level era chain this generation) ----------
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
# the W257-era faces.
def age_prev3(s):
    s = s.replace("W258", "W259")
    s = s.replace("257", "258")
    s = s.replace("256", "257")
    return s

# age_prev4(): the W259 editor's blanket composition (P2 W259->W260,
# P3 258->259, P4 257->258) -- reconstructs the W259-script chunk faces from
# the W258-era faces (NEW level this generation, disclosed; body = the W259
# editor's age() verbatim).
def age_prev4(s):
    s = s.replace("W259", "W260")
    s = s.replace("258", "259")
    s = s.replace("257", "258")
    return s

# age(): EXACT composition of MY blanket passes (P2 downstream W260->W261,
# P3 self 259->260, P4 upstream 258->259) -- derives post-pass needles from
# W259-script-era literals WITHOUT hand-derivation.
def age(s):
    s = s.replace("W260", "W261")
    s = s.replace("259", "260")
    s = s.replace("258", "259")
    return s

'''
sect("# age_prev255(): the W255 editor", "def rep(old, new, expect=None, tag=", NEW_ERAS, "eras")

# ---------- 4) mk259 def insert + mk() comment roll ----------
NEW_MK259 = r'''# mk259(): rebuild the W259-script chunk from the W258-era face (asserts
# the W259 editor's fact subs exactly as the r1064-era editor ran them; NEW
# level this generation, disclosed).
def mk259(needle, repls, tag):
    s = needle
    for old, new, cnt in repls:
        n = s.count(old)
        assert n == cnt, f"[{tag}.{s.count(old)}] sub {old[:56]!r}: {n} != {cnt}"
        s = s.replace(old, new)
    return s

'''
sect("# mk(): build a chunk NEW text", "def mk(needle, repls, tag):",
     NEW_MK259 + '# mk(): build a chunk NEW text from its (post-blanket) needle via ordered\n# count-asserted fact replacements -- W260 facts from the probe receipt.\n\n', "mk259")

# ---------- 5) P1..P4x ----------
NEW_P1_P4X = r'''# ============ P1: structural faces, BLANKET-IMMUNE outputs ============
rep("(255, 254, 253, 252, 251, 250, 249, 248, 247, 246)",
    "(256, 255, 254, 253, 252, 251, 250, 249, 248, 247)", 2, "P1-transitive-deps")
rep("range(209, 260)", "range(209, 261)", 2, "P1-liveness-range")
rep('def fmt(n):  # 585101 -> "585_101"', 'def fmt(n):  # 587301 -> "587_301"', 1, "P1-fmt-comment")

# ============ P2: downstream shift W260 -> W261 ============
rep("W260", "W261", None, "P2-downstream")
assert "W260" not in t, "P2 leftover W260"

# ============ P3: self shift 259 -> 260 ============
n259 = t.count("259")
rep("259", "260", None, "P3-self")
log.append(f"P3 consumed {n259} '259' substrings")

# ============ P4: upstream shift 258 -> 259 ============
n258 = t.count("258")
rep("258", "259", None, "P4-upstream")
log.append(f"P4 consumed {n258} '258' substrings")

# ============ P4x: blanket-exemption heal (NONE this generation, disclosed) ============
# the MY-blanket shifts do NOT hit the FOUR "hashlib.sha256" API-name
# occurrences inside the source (sha256 contains "256" but NOT "258"/"259";
# pre-flight evidence: hashlib.sha256=4 / sha258=0 / sha259=0 on the
# committed W259 script) -- zero heal needed again this generation.

'''
sect("# ============ P1: structural faces", "# ============ P5a: numeric/anchor", NEW_P1_P4X, "P1-P4x")

# ---------- 6) P5a ----------
NEW_P5A = r'''# ============ P5a: numeric/anchor/ordinal/window faces (post-blanket forms) ============
# r-window ORDER DISCLOSURE (needle-heal family, vs the W259 editor order):
# the source's own prereg-window refs are r1063 (7x) AND its freeze stamp is
# "r1064 freeze window" (1x header) -- the E260 chain reps CREATE new "r1064"
# strings (from the 23 "r1062" refs), so the header-window rep runs FIRST
# (consumes the unique full-stamp needle BEFORE any r1062->r1064 creation
# lands), prereg-window second, closeout/splice/rest after. Counts
# pre-flight-verified on the committed W259 script: r1063=7 / r1062=23
# (1 closeout + 3 splice-window + 19 rest) / r1064=1 (header stamp only).
# Coincidence disclosure this generation: the W260 prereg window (dead-r1065
# prereg) and the splice window (r1065-continuation THIS window) share the
# SAME r-number -- the prereg refs (r1065 x7) and the freeze stamp
# ("11:3x bm-c r1065 freeze window") are distinct needles, zero collision
# (the full-stamp needle is consumed first), disclosed.
rep(age("2026-10-17 08:4x bm-c r1064 freeze window"), "2026-10-17 11:3x bm-c r1065 freeze window", 1, "P5a-header-window")
rep(age("r1063"), "r1065", 7, "P5a-prereg-window")
rep(age("W258 finalize one-pass bm-c r1062 window closeout 07:0x"),
    "W259 finalize one-pass bm-c r1064 window closeout 09:1x", 1, "P5a-closeout-window")
rep(age("r1062 splice window"), "r1064 splice window", 3, "P5a-splice-window")
rep(age("r1062"), "r1064", 19, "P5a-splice-window-rest")
rep(age("authored 07:3x"), "authored 10:2x", 2, "P5a-authored-time")
rep(age("991_935"), "994_135", 1, "P5a-ledger-int")
rep(age("565_520"), "567_720", 1, "P5a-k-int")
rep(age("991,935"), "994,135", 8, "P5a-ledger-prose")
rep(age("565,520"), "567,720", 8, "P5a-k-prose")
rep(age("bmc_ordinal=79"), "bmc_ordinal=80", 7, "P5a-ordinal78")
rep(age("SEVENTY-NINTH"), "EIGHTIETH", 3, "P5a-seventyeighth")
rep(age("TWO HUNDRED AND FIFTY-NINTH"), "TWO HUNDRED AND SIXTIETH", 3, "P5a-260th")
rep(age("forty-seventh consecutive"), "forty-eighth consecutive", 2, "P5a-finface")
rep(age("79th own wave"), "80th own wave", 3, "P5a-79th-ownwave")
rep(age("MSG-20261017-0704-bmc-w259-seat"), "MSG-20261017-0910-bmc-w260-seat", 7, "P5a-seat-msg")
rep(age("16dba0e70"), "9fa2c8aed", 2, "P5a-seat-origin")
rep(age("b709bc2cc"), "0f33f9abc", 1, "P5a-prereg-commit")
# aging-face needle heals (same-window disclosed, r1045/r1047/r1050/r1055/r1057/r1058/r1062 precedent family):
rep(age("transitive window W246..W255 checked"), "transitive window W247..W256 checked", 1, "P5a-aging-deps-cmt")
rep(age("engine_owner==bm-c rows 78 + candidate"), "engine_owner==bm-c rows 79 + candidate", 1, "P5a-aging-rows-heal")

'''
sect("# ============ P5a: numeric/anchor", "# ============ P5b: extraction count faces", NEW_P5A, "P5a")

# ---------- 7) P5b direct (pre-chain) ----------
NEW_P5B = r'''# ============ P5b: extraction count faces (frozen W260 prereg sec.3 mandate) ============
# estate 69 (W138..W206) UNCHANGED; kept W211..W241 (31); dropped W242..W258
# (17); fresh W242..W259 (18); total parity 118 rows; legs segment
# W211..W258 (48). NEW FACE this generation (disclosed): the kept/dropped
# split boundary MOVES 241->242 per the frozen W260 prereg sec.3 mandate
# (kept W211..W241 31 legs -- the W260 block parity list enumerates W211..W259
# with NO gap, so W241 moves from the dropped set into the kept set); five
# m241->m242 code faces + kept/dropped range faces + fresh-loop lower bounds
# are count-asserted direct reps (pre-flight: m241=4 / range(241,259)=2 /
# kept-30=1 / dropped-17=1).
rep(age("# block's own W241..W257 legs (17 rows) do NOT enter the estate path;"),
    "# block's own W242..W258 legs (17 rows) do NOT enter the estate path;", 1, "P5b-hdr-ownlegs")
rep(age("# after extraction, fresh W241..W258 legs (18 rows) are added,"),
    "# after extraction, fresh W242..W259 legs (18 rows) are added,", 1, "P5b-hdr-freshlegs")
rep(age("# parity = 117 rows (W138..W206 + W211..W258). Zero assumption zero risk."),
    "# parity = 118 rows (W138..W206 + W211..W259). Zero assumption zero risk.", 1, "P5b-hdr-parity-count")
rep(age("# block's own W241..W257 legs (17) are EXCLUDED from the estate path per the"),
    "# block's own W242..W258 legs (17) are EXCLUDED from the estate path per the", 1, "P5b-ext-excl")
rep(age("# prereg mandate; the W259 block appends fresh W241..W258 legs (18,"),
    "# prereg mandate; the W260 block appends fresh W242..W259 legs (18,", 1, "P5b-ext-fresh")
rep(age("# machine-derived from the LIVE pf registry at freeze time) -> 117 parity"),
    "# machine-derived from the LIVE pf registry at freeze time) -> 118 parity", 1, "P5b-ext-parcount")
'''
sect("# ============ P5b: extraction count faces", "_PARFULL_W255 = ", NEW_P5B, "P5b-direct")

# ---------- 8) P5b chains: extend 4 families ----------
extend_family("_PARFULL_W258", "rep", "P5b-parfull",
    '\n        ("== 116", "== 117", 1),\n        ("!= 116 (69 estate + W211..W257 legs 47)", "!= 117 (69 estate + W211..W258 legs 48)", 1),')
extend_family("_LEGS_W258", "rep", "P5b-legs-assert",
    '\n        ("== 47", "== 48", 1),\n        ("legs segment not W211..W257 forty-seven legs", "legs segment not W211..W258 forty-eight legs", 1),')
extend_family("_DROP_W258", "rep", "P5b-dropped-assert",
    '\n        ("list(range(241, 259))", "list(range(242, 259))", 1),\n        ("dropped segment not W241..W257 seventeen legs", "dropped segment not W242..W258 seventeen legs", 1),')
extend_family("_RCPTNOTE_W258", "rep", "P5b-rcpt-note",
    '\n        ("own W241..W257 legs (17) EXCLUDED", "own W242..W258 legs (17) EXCLUDED", 1),\n        ("fresh W241..W259 legs (18) machine-derived", "fresh W242..W259 legs (18) machine-derived", 1),\n        ("W260 block = 117 rows", "W260 block = 118 rows", 1),\n        ("E63 11th-gen", "E63 12th-gen", 1),\n        ("W211..W240 legs (30)", "W211..W241 legs (31)", 1),\n        ("list(range(211,259))/list(range(211,241))/list(range(241,259))", "list(range(211,259))/list(range(211,242))/list(range(242,259))", 1),')

# ---------- 9) P5b late (split/boundary/mat/rcpt-identity reps) ----------
NEW_P5B_LATE = r"""# NEW-FACE split-boundary reps (241 -> 242, frozen W260 prereg sec.3 mandate):
rep(age("# prereg sec.3 mandate split: keep W211..W240 verbatim (30 legs); the W258\n# block's own W241..W257 legs (17) are excluded from the estate path"),
    "# prereg sec.3 mandate split: keep W211..W241 verbatim (31 legs); the W259\n# block's own W242..W258 legs (17) are excluded from the estate path", 1, "P5b-split-cmt")
rep(r'm241 = re.search(r" *assert pf\.N1_BANDS\[241\] ==", legs_sec)',
    r'm242 = re.search(r" *assert pf\.N1_BANDS\[242\] ==", legs_sec)', 1, "P5b-split-mvar")
rep(age('assert m241, "W241 leg boundary not found inside W259 legs segment (prereg sec.3 split face)"'),
    'assert m242, "W242 leg boundary not found inside W260 legs segment (prereg sec.3 split face)"', 1, "P5b-split-assert")
rep("legs_kept = legs_sec[:m241.start()]", "legs_kept = legs_sec[:m242.start()]", 1, "P5b-split-kept")
rep("legs_dropped = legs_sec[m241.start():]", "legs_dropped = legs_sec[m242.start():]", 1, "P5b-split-dropped")
# kept assert moves 30/range(211,241) -> 31/range(211,242) (NEW face, pre-flight raw count 1):
_KEPT_W259 = '''assert legs_kept.count("assert pf.N1_BANDS[") == 30 \\
    and [int(w) for w in _kept_ws] == list(range(211, 241)), \\
    f"kept segment not W211..W240 thirty legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"'''
rep(_KEPT_W259, '''assert legs_kept.count("assert pf.N1_BANDS[") == 31 \\
    and [int(w) for w in _kept_ws] == list(range(211, 242)), \\
    f"kept segment not W211..W241 thirty-one legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"''', 1, "P5b-kept-assert")
# fresh-loop + leg-count-loop lower bounds + fresh first-line assert (NEW face):
rep(age("for _w in range(241, 259):"), "for _w in range(242, 260):", 1, "P5b-fresh-loop")
rep(age("for _lw in range(241, 259):"), "for _lw in range(242, 260):", 1, "P5b-legcount-loop")
rep("assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[241] == {\"a\": (')",
    "assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[242] == {\"a\": (')", 1, "P5b-fresh-firstline")
# receipt count faces: fresh stays 18 this generation = identity count-asserts (disclosed):
rep(age('"fresh_legs_row_asserts": 18,'), '"fresh_legs_row_asserts": 18,', 1, "P5b-rcpt-fresh18-identity")
rep(age('+ legs_kept.count("assert pf.N1_BANDS[") + 18,'), '+ legs_kept.count("assert pf.N1_BANDS[") + 18,', 1, "P5b-rcpt-total18-identity")
# materializer hdr comment faces:
rep(age('"    #     W211..W240 legs (30) extracted verbatim from the OWN W258 block",'),
    '"    #     W211..W241 legs (31) extracted verbatim from the OWN W259 block",', 1, "P5b-hdr-kept-mat")
rep(age('"    #     physical bytes; the W259 block\'s own W241..W257 legs (17) are",'),
    '"    #     physical bytes; the W260 block\'s own W242..W258 legs (17) are",', 1, "P5b-hdr-ownlegs-mat")
rep(age('"    #     W241..W258 legs (18) added, machine-derived from the live pf",'),
    '"    #     W242..W259 legs (18) added, machine-derived from the live pf",', 1, "P5b-hdr-freshlegs-mat")
rep(age('"    #     registry at freeze time -> 117 parity rows (W138..W206+W211..W258).",'),
    '"    #     registry at freeze time -> 118 parity rows (W138..W206+W211..W259).",', 1, "P5b-hdr-parcount-mat")

"""
sect('rep(age("# prereg sec.3 mandate split:', '# receipt note (single big face: counts + generation stamp)', NEW_P5B_LATE, "P5b-late")

# ---------- 10) P5c ----------
NEW_P5C = r'''# ============ P5c: band literals (probe ADMIT receipt bands) ============
rep(age('assert (a_lo, a_hi) == (585_101, 587_100) and (b_lo, b_hi) == (587_101, 587_300), \\'),
    'assert (a_lo, a_hi) == (587_301, 589_300) and (b_lo, b_hi) == (589_301, 589_500), \\', 1, "P5c-band-drift")

'''
sect("# ============ P5c: band literals", "# ============ P5d: ordinal/leg0", NEW_P5C, "P5c")

# ---------- 11) P5d ----------
NEW_P5D = r'''# ============ P5d: ordinal/leg0/deps faces ============
rep(age('assert len(owner_rows_live) == 248 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 78, \\'),
    'assert len(owner_rows_live) == 249 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 79, \\', 1, "P5d-ord-gate")
# needle narrowed to the pre-registration numeric face: the trailing "80th own
# wave" inside this line was ALREADY rewritten by the P5a-79th-ownwave rep
# (order-sensitive face, W259 editor canon -- its P5d needle was likewise the
# post-P5a form); disclosed needle heal, evidence = pre-flight n=1 raw face.
rep(age("(expect 248/129/78 PRE-splice post-W258 registration"),
    "(expect 249/129/79 PRE-splice post-W259 registration", 1, "P5d-ord-err")
# needle narrowed likewise: the trailing "bmc_ordinal=80" on this line was
# already rewritten by the P5a-ordinal79 rep (one of its 7 faces).
rep(age('# receipt leg0 face owner_rows=248 / bmc_rows=78 /'),
    '# receipt leg0 face owner_rows=249 / bmc_rows=79 /', 1, "P5d-leg0-prose")
rep(age("-> owner rows 248 + candidate = 249th EXACT; bm-c rows 78 +"),
    "-> owner rows 249 + candidate = 250th EXACT; bm-c rows 79 +", 1, "P5d-ord-owner-prose")
rep(age("# candidate = 79th EXACT -- bm-c own-seat continuity face (bm-c published the"),
    "# candidate = 80th EXACT -- bm-c own-seat continuity face (bm-c published the", 1, "P5d-ord-bmc-prose")
rep(age("freeze-time live face owner rows 248 + candidate = 249th EXACT"),
    "freeze-time live face owner rows 249 + candidate = 250th EXACT", 1, "P5d-rcpt-249th")
rep(age("freeze-time live derive bmc rows 78 + candidate 79th EXACT per r587/r359"),
    "freeze-time live derive bmc rows 79 + candidate 80th EXACT per r587/r359", 1, "P5d-bundle-79th")
rep(age("post-W258 registration: bm-c rows 78 + candidate = 79th owned"),
    "post-W259 registration: bm-c rows 79 + candidate = 80th owned", 1, "P5d-rcpt-79th-owned")
rep(age('"probe_receipt_bmc_ordinal_face": 79,'), '"probe_receipt_bmc_ordinal_face": 80,', 1, "P5d-rcpt-ordface")
rep(age('f"W259+W254..W245 finalize products present "'), 'f"W260+W255..W246 finalize products present "', 1, "P5d-print-deps")

'''
sect("# ============ P5d: ordinal/leg0", "# ============ P5e: A/B face structural", NEW_P5D, "P5d")

# ---------- 12) P5e families (extend; new final subs = W260 facts) ----------
extend_family("_HDR_W258", "chunk", "P5e-hdr",
    '\n          ("NINTH consecutive\\n# above-own-A", "TENTH consecutive\\n# above-own-A", 1),\n          ("EIGHTH consecutive A-hop", "NINTH consecutive A-hop", 1),\n          ("585_101..587_100", "587_301..589_300", 2),\n          ("587_101..587_300", "589_301..589_500", 1),\n          ("584_901..586_900", "587_101..589_100", 1),\n          ("584_901..585_100", "587_101..587_300", 1),\n          ("585_101..585_300", "587_301..587_500", 1),\n          ("585_100", "587_300", 2),\n          ("587_100", "589_300", 2),')
extend_family("_BANDFACTS_W258", "chunk", "P5e-bandfacts",
    '\n          ("NINTH consecutive above-own-A landing", "TENTH consecutive above-own-A landing", 1),\n          ("EIGHTH consecutive A-hop", "NINTH consecutive A-hop", 2),')
extend_family("_A_BASE_W258", "rep", "P5e-a-base",
    ' ("eighth consecutive A-hop", "ninth consecutive A-hop", 1),')
extend_family("_A_FLOOR_W258", "rep", "P5e-a-floor",
    ' ("eighth consecutive A-hop", "ninth consecutive A-hop", 1),')
extend_family("_B_BASE_W258", "rep", "P5e-b-base",
    ' ("ninth consecutive above-own-A", "tenth consecutive above-own-A", 1),')
extend_family("_RA_GATE_W258", "rep", "P5e-ra-gate",
    '\n        ("W256_W257_W259_bands_respected_A", "W257_W258_W259_bands_respected_A", 1),\n        ("W256_W257_W259_bands_respected_B", "W257_W258_W259_bands_respected_B", 1),')
extend_family("_PFCMT_W258", "chunk", "P5e-pfcmt",
    '\n          ("NINTH consecutive above-own-A;", "TENTH consecutive above-own-A;", 1),\n          ("EIGHTH consecutive A-hop", "NINTH consecutive A-hop", 1),\n          ("hops=1 -- SEVENTH", "hops=1 -- EIGHTH", 1),')
extend_family("_PRE_W258", "chunk", "P5e-pre",
    '\n          ("NINTH consecutive above-own-A", "TENTH consecutive above-own-A", 1),\n          ("EIGHTH consecutive A-hop", "NINTH consecutive A-hop", 2),')
extend_family("_MEM_A_W258", "rep", "P5e-mem-a",
    '\n        ("EIGHTH consecutive A-hop", "NINTH consecutive A-hop", 1),\n        ("eighth consecutive A-hop", "ninth consecutive A-hop", 1),')
extend_family("_MEM_B_W258", "rep", "P5e-mem-b",
    ' ("ninth consecutive above-own-A", "tenth consecutive above-own-A", 1),')
extend_family("_TAILCMT_W258", "chunk", "P5e-tailcmt",
    '\n          ("NINTH consecutive", "TENTH consecutive", 1),\n          ("EIGHTH consecutive A-hop", "NINTH consecutive A-hop", 2),')
extend_family("_TAIL_AMSG_W258", "rep", "P5e-tail-amsg",
    ' ("EIGHTH consecutive A-hop", "NINTH consecutive A-hop", 2),')
extend_family("_EXCL_W258", "rep", "P5e-tail-excl",
    ' ("ninth consecutive above-own-A", "tenth consecutive above-own-A", 1),')
extend_family("_PRCHUNK_W258", "chunk", "P5e-pr",
    '\n          ("NINTH consecutive above-own-A landing", "TENTH consecutive above-own-A landing", 1),\n          ("EIGHTH consecutive A-hop", "NINTH consecutive A-hop", 1),')
extend_family("_SEM_A_W258", "rep", "P5e-rcpt-semantics-A",
    '\n        ("EIGHTH consecutive A-hop", "NINTH consecutive A-hop", 2),\n        ("584_901..586_900 refused", "587_101..589_100 refused", 1),\n        ("584_901..585_100 sits", "587_101..587_300 sits", 1),\n        ("B tail 585_100 -> A first-clean 585_101..587_100", "B tail 587_300 -> A first-clean 587_301..589_300", 1),\n        ("(585_100+1) EXACT)", "(587_300+1) EXACT)", 1),')
extend_family("_SEM_B_W258", "rep", "P5e-rcpt-semantics-B",
    '\n        ("NINTH consecutive above-own-A landing", "TENTH consecutive above-own-A landing", 1),\n        ("585_101..585_300 is refused", "587_301..587_500 is refused", 1),\n        ("A first-clean window 585_101..587_100 (own-A", "A first-clean window 587_301..589_300 (own-A", 1),\n        ("own-A tail 587_100 -> B landing 587_101..587_300;", "own-A tail 589_300 -> B landing 589_301..589_500;", 1),\n        ("(587_100+1) EXACT)", "(589_300+1) EXACT)", 1),')
extend_family("_DOWNSTREAM_W258", "rep", "P5e-rcpt-downstream",
    '\n        ("A naive 587101..589100 CLEAN", "A naive 589301..591300 CLEAN", 1),\n        ("B naive 587301..587500 hops=0 CLEAN at naive, first-clean 587301..587500 BUT", "B naive 589501..589700 hops=0 CLEAN at naive, first-clean 589501..589700 BUT", 1),\n        ("naive A window start 587_101 lands INSIDE the registered W260 B band 587_101..587_300", "naive A window start 589_301 lands INSIDE the registered W260 B band 589_301..589_500", 1),')

# identity reps: FIVE-level inline chain -> SIX-level (age_prev4 inserted;
# full-block replace keeps paren balance, disclosed):
rep("""rep(age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')),
    ))), age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "'))))), 1, "P5e-tail-bassert2")""",
    """rep(age(age_prev4(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')),
    )))), age(age_prev4(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')))))), 1, "P5e-tail-bassert2")""",
    1, "identity-6level-bassert2")
rep("""rep(age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"')),
    ))), age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"'))))), 1, "P5e-tail-bclean")""",
    """rep(age(age_prev4(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"')),
    )))), age(age_prev4(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"')))))), 1, "P5e-tail-bclean")""",
    1, "identity-6level-bclean")

# family-section comment roll:
rep("# downstream W260+ projection face (probe leg4 verbatim numbers)",
    "# downstream W261+ projection face (probe leg4 verbatim numbers)", 1, "downstream-cmt-roll")

# ---------- 13) P5f ----------
NEW_P5F = r'''# ============ P5f: probe-receipt date face (DATE-STABLE this generation) ============
# disclosed date-stable face: the W260 probe receipt basename keeps the SAME
# date AGAIN (20261017 == 20261017, fourth consecutive date-stable
# generation) -- the blanket P3 already rolled the basename to
# _w260bmc_20261017_probe_receipt.json which IS the correct on-disk name;
# this rep is an identity count-assert (10x), zero heal needed. Position
# stays POST-P5e (the pfcmt chunk needle embeds the pre-replacement basename
# face).
rep(age("_w259bmc_20261017_probe_receipt.json"), "_w260bmc_20261017_probe_receipt.json", 10, "P5f-probe-receipt-date-stable")

'''
sect("# ============ P5f: probe-receipt date face", "# ============ structural output gates", NEW_P5F, "P5f")

# ---------- 14) output gates ----------
NEW_GATES = r'''# ============ structural output gates ============
for needle, want in [
    ("# --- W260 materializer face", 2),
    ("# --- W259 materializer face", 1),
    ('"+ W260 materializer face', 2),
    ("range(16, 260)", 2),
    ("range(17, 260)", 3),
    ("range(242, 260)", 2),
    ("range(241, 260)", 0),
    ("list(range(211, 259)),", 1),
    ("list(range(211, 242))", 1),
    ("list(range(211, 241))", 0),
    ("list(range(242, 259)),", 1),
    ("list(range(241, 259)),", 0),
    ("range(209, 261)", 2),
    ("if w < 260)", 5),
    ("if w < 259)", 1),
    ("m242", 4),
    ("m241", 0),
    ("_w260bmc_20261017_probe_receipt.json", 10),
    ("_w260bmc_freeze_receipt.json", 1),
    ("MSG-20261017-0910-bmc-w260-seat", 7),
    ("9fa2c8aed", 2),
    ("0f33f9abc", 1),
    ("994_135", 1),
    ("567_720", 1),
    ("994,135", 8),
    ("567,720", 8),
    ("(587_301, 589_300)", 1),
    ("(589_301, 589_500)", 1),
    ("W257_W258_W259_bands_respected_A", 1),
    ("W257_W258_W259_bands_respected_B", 1),
    ("B_base_above_W259_tail", 2),
    ("A_staircase_hop_past_W259_B", 8),
    ("W261p_A_naive", 5),
    ("W261p_B_first_clean", 2),
    ("arith_a260", 6),
    ("arith_b260", 6),
    ('"PERPETUAL-N1-W260-SHARD-0"', 1),
    ("n1_w260_results.json", 2),
    ("n1_w260", 4),
    ("n1w260", 2),
    ("PERPETUAL-N1-W260", 7),
    ("_w260bmc", 11),
    ("w245_a", 1),
    ("EIGHTIETH", 3),
    ("TWO HUNDRED AND SIXTIETH", 3),
    ("forty-eighth consecutive", 2),
    ("bmc_ordinal=80", 7),
    ("80th own wave", 3),
    ("r1064 splice window", 3),
    ("r1064", 23),
    ("r1065", 8),
    ("r1065 freeze window", 1),
    ("W259 finalize one-pass bm-c r1064 window closeout 09:1x", 1),
    ("authored 10:2x", 2),
    ("estate 69", 1),
    ("= 118 rows", 2),
    ("118 parity", 2),
    ("hops=1", None),
    ("1-HOP", None),
    ("NINTH consecutive A-hop", None),
    ("TENTH consecutive above-own-A", None),
    ("249/129/79", 1),
    ("250th", 2),
    ("80th EXACT", 2),
    ("thirty-one legs", 1),
    ("forty-eight legs", 1),
    ("== 48", 1),
    # anti-gates: stale faces must be zero
    ("r1062", 0),
    ("r1063", 0),
    ("16dba0e70", 0),
    ("b709bc2cc", 0),
    ("991,935", 0),
    ("565,520", 0),
    ("991_935", 0),
    ("565_520", 0),
    ("SEVENTY-NINTH", 0),
    ("TWO HUNDRED AND FIFTY-NINTH", 0),
    ("forty-seventh consecutive", 0),
    ("MSG-20261017-0704", 0),
    ("authored 07:3x", 0),
    ("08:4x", 0),
    ("bmc_ordinal=79", 0),
    ("79th own wave", 0),
    ("249th", 0),
    ("248/129/78", 0),
    ("NINTH consecutive above-own-A", 0),
    ("FIRST A-hop", 0),
    ("seed-gap face ENDS", 0),
    ("584_901..586_900", 0),
    ("584_901..585_100", 0),
    ("585_101..585_300", 0),
    ("585_101..587_100", 0),
    ("585_100", 0),
    ("587_100", 0),
    ("584_901", 0),
    ("585_101", 0),
    ("~587_301..587_900", 0),
    ("(585_101, 587_100)", 0),
    ("(587_101, 587_300)", 0),
    ("== 116", 0),
    ("forty-seven legs", 0),
    ("116 parity", 0),
    ("117 parity", 0),
    ("list(range(241, 257))", 0),
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
