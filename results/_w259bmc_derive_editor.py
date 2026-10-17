# -*- coding: utf-8 -*-
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
import io, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w258bmc_freeze_edits.py")
DST = os.path.join(REPO, "results", "_w259bmc_freeze_edits.py")
LOG = os.path.join(REPO, "results", "_w259bmc_derive_editor_log.txt")
PY = sys.executable

# S0: SRC worktree == committed HEAD blob (r609 origin-verbatim base law)
blob_wt = subprocess.run(["git", "hash-object", SRC], capture_output=True, text=True, cwd=REPO).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w258bmc_freeze_edits.py"], capture_output=True, text=True, cwd=REPO).stdout.strip()
assert blob_wt == blob_head and len(blob_wt) == 40, f"SRC blob drift: wt={blob_wt} head={blob_head}"
assert blob_wt == "aa9ae1bf918593902cfd90b301edcfac390d2d50", f"SRC blob face drift: {blob_wt}"

t = io.open(SRC, encoding="utf-8").read()
log = [f"S0 src blob verified {blob_wt[:16]} == HEAD twin (worktree clean face)"]

# age_prev255(): the W255 editor's blanket composition -- used ONLY to
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

def rep(old, new, expect=None, tag=""):
    global t
    n = t.count(old)
    if expect is not None:
        assert n == expect, f"[{tag}] count {n} != {expect} for: {old[:70]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x {old[:48]!r}")

# mk255(): rebuild the W255-script chunk from the W254-era literal (asserts
# the prev subs exactly as the r1057 editor ran them; canon-verbatim).
def mk255(needle, repls, tag):
    s = needle
    for old, new, cnt in repls:
        n = s.count(old)
        assert n == cnt, f"[{tag}.{s.count(old)}] sub {old[:56]!r}: {n} != {cnt}"
        s = s.replace(old, new)
    return s

# mk256(): rebuild the W256-script chunk from the W255-era face (asserts the
# W256 editor's fact subs exactly as the r1058 editor ran them; NEW level
# this generation, disclosed).
def mk256(needle, repls, tag):
    s = needle
    for old, new, cnt in repls:
        n = s.count(old)
        assert n == cnt, f"[{tag}.{s.count(old)}] sub {old[:56]!r}: {n} != {cnt}"
        s = s.replace(old, new)
    return s

# mk257(): rebuild the W257-script chunk from the W256-era face (asserts
# the W257 editor's fact subs exactly as the r1060 editor ran them; NEW
# level this generation, disclosed).
def mk257(needle, repls, tag):
    s = needle
    for old, new, cnt in repls:
        n = s.count(old)
        assert n == cnt, f"[{tag}.{s.count(old)}] sub {old[:56]!r}: {n} != {cnt}"
        s = s.replace(old, new)
    return s

# mk258(): rebuild the W258-script chunk from the W257-era face (asserts
# the W258 editor's fact subs exactly as the r1062 editor ran them; NEW
# level this generation, disclosed).
def mk258(needle, repls, tag):
    s = needle
    for old, new, cnt in repls:
        n = s.count(old)
        assert n == cnt, f"[{tag}.{s.count(old)}] sub {old[:56]!r}: {n} != {cnt}"
        s = s.replace(old, new)
    return s

# mk(): build a chunk NEW text from its (post-blanket) needle via ordered
# count-asserted fact replacements -- W259 facts from the probe receipt.

def mk(needle, repls, tag):
    s = needle
    for old, new, cnt in repls:
        n = s.count(old)
        assert n == cnt, f"[{tag}.{s.count(old)}] sub {old[:56]!r}: {n} != {cnt}"
        s = s.replace(old, new)
    return s

def chunk(needle, new, tag):
    global t
    n = t.count(needle)
    assert n == 1, f"[{tag}] chunk needle count {n} != 1 (needle head: {needle[:80]!r})"
    t = t.replace(needle, new)
    log.append(f"{tag}: chunk 1x ({len(needle)} -> {len(new)} chars)")

# ============ P1: structural faces, BLANKET-IMMUNE outputs ============
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

# ============ P5a: numeric/anchor/ordinal/window faces (post-blanket forms) ============
# r-window ORDER DISCLOSURE (needle-heal family, vs the W258 editor order):
# the source's own prereg-window refs are r1061 (7x) AND its freeze stamp is
# "r1062 freeze window" (1x header) -- the E259 chain reps CREATE new "r1062"
# strings (from the 23 "r1060" refs), so the header-window rep runs FIRST
# (consumes the unique full-stamp needle BEFORE any r1060->r1062 creation
# lands), prereg-window second, closeout/splice/rest after. Counts
# pre-flight-verified on the committed W258 script: r1061=7 / r1060=23
# (1 closeout + 3 splice-window + 19 rest) / r1062=1 (header stamp only).
# needle-heal r1064: freeze-window stamp healed r1063->r1064 (actual splice window;
# the build_editor collapsed prereg-window refs AND the freeze stamp onto r1063,
# an internally-inconsistent gate pair [7+1=8 vs gate 7]; per exec-grounded honesty
# law + state next_pointer (splice = r1064 FIRST ACTION) the stamp names the window
# that actually runs the freeze -- prereg refs stay r1063 x7, disclosed)
rep(age("2026-10-17 06:2x bm-c r1062 freeze window"), "2026-10-17 08:4x bm-c r1064 freeze window", 1, "P5a-header-window")
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

# ============ P5b: extraction count faces (frozen W259 prereg sec.3 mandate) ============
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
_PARFULL_W255 = '''assert par_full.count("assert pf.N1_BANDS[") == 112, \\
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 112 (69 estate + W211..W253 legs 43)"'''
_PARFULL_W256 = mk256(age_prev(_PARFULL_W255), [("== 112", "== 113", 1),
                        ("!= 112 (69 estate + W211..W253 legs 43)", "!= 113 (69 estate + W211..W254 legs 44)", 1)], "P5b-parfull-prev")
_PARFULL_W257 = mk257(age_prev2(_PARFULL_W256), [("== 113", "== 114", 1),
                            ("!= 113 (69 estate + W211..W254 legs 44)", "!= 114 (69 estate + W211..W255 legs 45)", 1)], "P5b-parfull-prev3")
_PARFULL_W258 = mk258(age_prev3(_PARFULL_W257), [
        ("== 114", "== 115", 1),
        ("!= 114 (69 estate + W211..W255 legs 45)", "!= 115 (69 estate + W211..W256 legs 46)", 1),
    ], "P5b-parfull-prev4")
rep(age(_PARFULL_W258),
    mk(age(_PARFULL_W258), [
        ("== 115", "== 116", 1),
        ("!= 115 (69 estate + W211..W256 legs 46)", "!= 116 (69 estate + W211..W257 legs 47)", 1),
    ], "P5b-parfull"),
    1, "P5b-parfull")
_LEGS_W255 = '''assert legs_sec.count("assert pf.N1_BANDS[") == 43 \\
    and [int(w) for w in _legs_ws] == list(range(211, 254)), \\
    f"legs segment not W211..W253 forty-three legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}"'''
_LEGS_W256 = mk256(age_prev(_LEGS_W255), [("== 43", "== 44", 1),
                      ("legs segment not W211..W253 forty-three legs", "legs segment not W211..W254 forty-four legs", 1)], "P5b-legs-prev")
_LEGS_W257 = mk257(age_prev2(_LEGS_W256), [("== 44", "== 45", 1),
                          ("legs segment not W211..W254 forty-four legs", "legs segment not W211..W255 forty-five legs", 1)], "P5b-legs-assert-prev3")
_LEGS_W258 = mk258(age_prev3(_LEGS_W257), [
        ("== 45", "== 46", 1),
        ("legs segment not W211..W255 forty-five legs", "legs segment not W211..W256 forty-six legs", 1),
    ], "P5b-legs-assert-prev4")
rep(age(_LEGS_W258),
    mk(age(_LEGS_W258), [
        ("== 46", "== 47", 1),
        ("legs segment not W211..W256 forty-six legs", "legs segment not W211..W257 forty-seven legs", 1),
    ], "P5b-legs-assert"),
    1, "P5b-legs-assert")
_DROP_W255 = '''assert legs_dropped.count("assert pf.N1_BANDS[") == 15 \\
    and [int(w) for w in _dropped_ws] == list(range(239, 254)), \\
    f"dropped segment not W239..W253 fifteen legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}"'''
_DROP_W256 = mk256(age_prev(_DROP_W255), [("== 15", "== 16", 1),
                      ("dropped segment not W239..W253 fifteen legs", "dropped segment not W239..W254 sixteen legs", 1)], "P5b-dropped-prev")
_DROP_W257 = mk257(age_prev2(_DROP_W256), [("== 16", "== 17", 1),
                          ("dropped segment not W239..W254 sixteen legs", "dropped segment not W239..W255 seventeen legs", 1)], "P5b-dropped-assert-prev3")
_DROP_W258 = mk258(age_prev3(_DROP_W257), [
        ("list(range(239, 257))", "list(range(240, 257))", 1),
        ("dropped segment not W239..W255 seventeen legs", "dropped segment not W240..W256 seventeen legs", 1),
    ], "P5b-dropped-assert-prev4")
rep(age(_DROP_W258),
    mk(age(_DROP_W258), [
        ("list(range(240, 258))", "list(range(241, 258))", 1),
        ("dropped segment not W240..W256 seventeen legs", "dropped segment not W241..W257 seventeen legs", 1),
    ], "P5b-dropped-assert"),
    1, "P5b-dropped-assert")
# NEW-FACE split-boundary reps (239 -> 240, frozen W258 prereg sec.3 mandate):
# NEW-FACE split-boundary reps (240 -> 241, frozen W259 prereg sec.3 mandate):
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

# receipt note (single big face: counts + generation stamp)
_RCPTNOTE_W255 = '''                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W238 legs (28) extracted verbatim per the frozen W255 prereg sec.3 mandate; the W254 block's own W239..W253 legs (15) EXCLUDED from the estate path per the same mandate; fresh W239..W254 legs (16) machine-derived from the live pf registry -> W255 block = 113 rows (W138..W206 + W211..W254); disclosed: (a) inherited W213 leg error-string face preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-255 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 7th-gen prevention this window: the W255 derive editor kept the P1-blanket-immune pass ordering and the extraction-restructure legs/kept/dropped wave-identity asserts fixed post-blanket (list(range(211,254))/list(range(211,239))/list(range(239,254)) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},'''
_RCPTNOTE_W256 = mk256(age_prev(_RCPTNOTE_W255), [
    ("own W239..W253 legs (15) EXCLUDED", "own W239..W254 legs (16) EXCLUDED", 1),
    ("fresh W239..W255 legs (16) machine-derived", "fresh W239..W255 legs (17) machine-derived", 1),
    ("W256 block = 113 rows", "W256 block = 114 rows", 1),
    ("E63 7th-gen", "E63 8th-gen", 1),
], "P5b-rcpt-note-prev")
_RCPTNOTE_W257 = mk257(age_prev2(_RCPTNOTE_W256), [
        ("own W239..W254 legs (16) EXCLUDED", "own W239..W255 legs (17) EXCLUDED", 1),
        ("fresh W239..W256 legs (17) machine-derived", "fresh W239..W256 legs (18) machine-derived", 1),
        ("W257 block = 114 rows", "W257 block = 115 rows", 1),
        ("E63 8th-gen", "E63 9th-gen", 1),
    ], "P5b-rcpt-note-prev3")
_RCPTNOTE_W258 = mk258(age_prev3(_RCPTNOTE_W257), [
        ("own W239..W255 legs (17) EXCLUDED", "own W240..W256 legs (17) EXCLUDED", 1),
        ("fresh W239..W257 legs (18) machine-derived", "fresh W240..W257 legs (18) machine-derived", 1),
        ("W258 block = 115 rows", "W258 block = 116 rows", 1),
        ("E63 9th-gen", "E63 10th-gen", 1),
        ("W211..W238 legs (28)", "W211..W239 legs (29)", 1),
        ("list(range(211,257))/list(range(211,239))/list(range(239,257))", "list(range(211,257))/list(range(211,240))/list(range(240,257))", 1),
    ], "P5b-rcpt-note-prev4")
rep(age(_RCPTNOTE_W258),
    mk(age(_RCPTNOTE_W258), [
        ("own W240..W256 legs (17) EXCLUDED", "own W241..W257 legs (17) EXCLUDED", 1),
        ("fresh W240..W258 legs (18) machine-derived", "fresh W241..W258 legs (18) machine-derived", 1),
        ("W259 block = 116 rows", "W259 block = 117 rows", 1),
        ("E63 10th-gen", "E63 11th-gen", 1),
        ("W211..W239 legs (29)", "W211..W240 legs (30)", 1),
        ("list(range(211,258))/list(range(211,240))/list(range(240,258))", "list(range(211,258))/list(range(211,241))/list(range(241,258))", 1),
    ], "P5b-rcpt-note"),
    1, "P5b-rcpt-note")

# ============ P5c: band literals (probe ADMIT receipt bands) ============
rep(age('assert (a_lo, a_hi) == (582_901, 584_900) and (b_lo, b_hi) == (584_901, 585_100), \\'),
    'assert (a_lo, a_hi) == (585_101, 587_100) and (b_lo, b_hi) == (587_101, 587_300), \\', 1, "P5c-band-drift")

# ============ P5d: ordinal/leg0/deps faces ============
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

# ============ P5e: A/B face structural rewrites (staircase + cascade CONTINUE) ============
_HDR_W254 = '''# NEW FACE vs the W253 editor (honest disclosure, frozen W254 prereg sec.3
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
# B_hop_lands_inside_A=false; hops=1).'''
_HDR_W255 = mk255(age_prev255(_HDR_W254), [
    ("FOURTH consecutive\n# above-own-A", "FIFTH consecutive\n# above-own-A", 1),
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 1),
    ("576_101..576_300", "578_301..578_500", 1),
    ("573_901..575_900", "576_101..578_100", 1),
    ("573_901..574_100", "576_101..576_300", 1),
    ("574_101..576_100", "576_301..578_300", 2),
    ("574_101..574_300", "576_301..576_500", 1),
    ("574_100", "576_300", 2),
    ("576_100", "578_300", 2),
], "P5e-hdr-prev")
_HDR_W256 = mk256(age_prev(_HDR_W255), [
    ("FIFTH consecutive\n# above-own-A", "SIXTH consecutive\n# above-own-A", 1),
    ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 1),
    ("576_301..578_300", "578_501..580_500", 2),
    ("578_301..578_500", "580_501..580_700", 1),
    ("576_101..578_100", "578_301..580_300", 1),
    ("576_101..576_300", "578_301..578_500", 1),
    ("576_301..576_500", "578_501..578_700", 1),
    ("576_300", "578_500", 2),
    ("578_300", "580_500", 2),
], "P5e-hdr-prev2")
_HDR_W257 = mk257(age_prev2(_HDR_W256), [
          ("SIXTH consecutive\n# above-own-A", "SEVENTH consecutive\n# above-own-A", 1),
          ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 1),
          ("578_501..580_500", "580_701..582_700", 2),
          ("580_501..580_700", "582_701..582_900", 1),
          ("578_301..580_300", "580_501..582_500", 1),
          ("578_301..578_500", "580_501..580_700", 1),
          ("578_501..578_700", "580_701..580_900", 1),
          ("578_500", "580_700", 2),
          ("580_500", "582_700", 2),
      ], "P5e-hdr-prev3")
_HDR_W258 = mk258(age_prev3(_HDR_W257), [
          ("SEVENTH consecutive\n# above-own-A", "EIGHTH consecutive\n# above-own-A", 1),
          ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 1),
          ("580_701..582_700", "582_901..584_900", 2),
          ("582_701..582_900", "584_901..585_100", 1),
          ("580_501..582_500", "582_701..584_700", 1),
          ("580_501..580_700", "582_701..582_900", 1),
          ("580_701..580_900", "582_901..583_100", 1),
          ("580_700", "582_900", 2),
          ("582_700", "584_900", 2),
      ], "P5e-hdr-prev4")
chunk(age(_HDR_W258),
      mk(age(_HDR_W258), [
          ("EIGHTH consecutive\n# above-own-A", "NINTH consecutive\n# above-own-A", 1),
          ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 1),
          ("582_901..584_900", "585_101..587_100", 2),
          ("584_901..585_100", "587_101..587_300", 1),
          ("582_701..584_700", "584_901..586_900", 1),
          ("582_701..582_900", "584_901..585_100", 1),
          ("582_901..583_100", "585_101..585_300", 1),
          ("582_900", "585_100", 2),
          ("584_900", "587_100", 2),
      ], "P5e-hdr"), "P5e-hdr")

_BANDFACTS_W254 = '''# W254 FACE (probe receipt leg1 relation_asserts):
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
# machine-derived from the LIVE registered row, never transcribed.'''
_BANDFACTS_W255 = mk255(age_prev255(_BANDFACTS_W254), [
    ("FOURTH consecutive above-own-A landing", "FIFTH consecutive above-own-A landing", 1),
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2),
], "P5e-bandfacts-prev")
_BANDFACTS_W256 = mk256(age_prev(_BANDFACTS_W255), [
    ("FIFTH consecutive above-own-A landing", "SIXTH consecutive above-own-A landing", 1),
    ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 2),
], "P5e-bandfacts-prev2")
_BANDFACTS_W257 = mk257(age_prev2(_BANDFACTS_W256), [
          ("SIXTH consecutive above-own-A landing", "SEVENTH consecutive above-own-A landing", 1),
          ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 2),
      ], "P5e-bandfacts-prev3")
_BANDFACTS_W258 = mk258(age_prev3(_BANDFACTS_W257), [
          ("SEVENTH consecutive above-own-A landing", "EIGHTH consecutive above-own-A landing", 1),
          ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 2),
      ], "P5e-bandfacts-prev4")
chunk(age(_BANDFACTS_W258),
      mk(age(_BANDFACTS_W258), [
          ("EIGHTH consecutive above-own-A landing", "NINTH consecutive above-own-A landing", 1),
          ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 2),
      ], "P5e-bandfacts"), "P5e-bandfacts")

_A_BASE_W254 = '''assert w253_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1 EXACT -- the 1-hop walk past the registered W253 B band; third consecutive A-hop of the staircase era; A_staircase_hop_past_W253_B=true)"'''
_A_BASE_W255 = mk255(age_prev255(_A_BASE_W254), [("third consecutive A-hop", "fourth consecutive A-hop", 1)], "P5e-a-base-prev")
_A_BASE_W256 = mk256(age_prev(_A_BASE_W255), [("fourth consecutive A-hop", "fifth consecutive A-hop", 1)], "P5e-a-base-prev2")
_A_BASE_W257 = mk257(age_prev2(_A_BASE_W256), [("fifth consecutive A-hop", "sixth consecutive A-hop", 1)], "P5e-a-base-prev3")
_A_BASE_W258 = mk258(age_prev3(_A_BASE_W257), [ ("sixth consecutive A-hop", "seventh consecutive A-hop", 1),
    ], "P5e-a-base-prev4")
rep(age(_A_BASE_W258),
    mk(age(_A_BASE_W258), [ ("seventh consecutive A-hop", "eighth consecutive A-hop", 1),
    ], "P5e-a-base"),
    1, "P5e-a-base")
_A_FLOOR_W254 = '''assert a_lo >= w253_b_tail + 1, "A staircase landing floor relation (A base >= registered prior-wave B tail+1; the fourteen-wave seed-gap face ENDED at W252 -- third consecutive A-hop of the staircase era, A base == prior-B tail+1 EXACT this window per the prereg floor-relation mandate)"'''
_A_FLOOR_W255 = mk255(age_prev255(_A_FLOOR_W254), [("third consecutive A-hop", "fourth consecutive A-hop", 1)], "P5e-a-floor-prev")
_A_FLOOR_W256 = mk256(age_prev(_A_FLOOR_W255), [("fourth consecutive A-hop", "fifth consecutive A-hop", 1)], "P5e-a-floor-prev2")
_A_FLOOR_W257 = mk257(age_prev2(_A_FLOOR_W256), [("fifth consecutive A-hop", "sixth consecutive A-hop", 1)], "P5e-a-floor-prev3")
_A_FLOOR_W258 = mk258(age_prev3(_A_FLOOR_W257), [ ("sixth consecutive A-hop", "seventh consecutive A-hop", 1),
    ], "P5e-a-floor-prev4")
rep(age(_A_FLOOR_W258),
    mk(age(_A_FLOOR_W258), [ ("seventh consecutive A-hop", "eighth consecutive A-hop", 1),
    ], "P5e-a-floor"),
    1, "P5e-a-floor")
_B_BASE_W254 = '''assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation cascade lands ABOVE own-A -- fourth consecutive above-own-A; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"'''
_B_BASE_W255 = mk255(age_prev255(_B_BASE_W254), [("fourth consecutive above-own-A", "fifth consecutive above-own-A", 1)], "P5e-b-base-prev")
_B_BASE_W256 = mk256(age_prev(_B_BASE_W255), [("fifth consecutive above-own-A", "sixth consecutive above-own-A", 1)], "P5e-b-base-prev2")
_B_BASE_W257 = mk257(age_prev2(_B_BASE_W256), [("sixth consecutive above-own-A", "seventh consecutive above-own-A", 1)], "P5e-b-base-prev3")
_B_BASE_W258 = mk258(age_prev3(_B_BASE_W257), [ ("seventh consecutive above-own-A", "eighth consecutive above-own-A", 1),
    ], "P5e-b-base-prev4")
rep(age(_B_BASE_W258),
    mk(age(_B_BASE_W258), [ ("eighth consecutive above-own-A", "ninth consecutive above-own-A", 1),
    ], "P5e-b-base"),
    1, "P5e-b-base")

# relation_asserts gate (W252_W254 rsv-key fix lineage -- the P4 blanket
# produces the W253_W254_W256 hybrid face; the probe receipt leg1 keys are
# W254_W255_W256)
_RA_GATE_W254 = '''ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") is False and ra.get("A_staircase_hop_past_W253_B") \\
    and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_clean_at_naive_start") is False and ra.get("B_base_above_W253_tail") \\
    and ra.get("AB_mutual_exclusion") and ra.get("B_hop_lands_inside_A") is False \\
    and ra.get("B_lands_above_own_A") and ra.get("W251_W252_W253_bands_respected_A") and ra.get("W251_W252_W253_bands_respected_B"), \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"'''
_RA_GATE_W255 = mk255(age_prev255(_RA_GATE_W254), [
    ("W251_W252_W254_bands_respected_A", "W252_W253_W254_bands_respected_A", 1),
    ("W251_W252_W254_bands_respected_B", "W252_W253_W254_bands_respected_B", 1),
], "P5e-ra-gate-prev")
_RA_GATE_W256 = mk256(age_prev(_RA_GATE_W255), [
    ("W252_W253_W255_bands_respected_A", "W253_W254_W255_bands_respected_A", 1),
    ("W252_W253_W255_bands_respected_B", "W253_W254_W255_bands_respected_B", 1),
], "P5e-ra-gate-prev2")
_RA_GATE_W257 = mk257(age_prev2(_RA_GATE_W256), [
        ("W253_W254_W256_bands_respected_A", "W254_W255_W256_bands_respected_A", 1),
        ("W253_W254_W256_bands_respected_B", "W254_W255_W256_bands_respected_B", 1),
    ], "P5e-ra-gate-prev3")
_RA_GATE_W258 = mk258(age_prev3(_RA_GATE_W257), [
        ("W254_W255_W257_bands_respected_A", "W255_W256_W257_bands_respected_A", 1),
        ("W254_W255_W257_bands_respected_B", "W255_W256_W257_bands_respected_B", 1),
    ], "P5e-ra-gate-prev4")
rep(age(_RA_GATE_W258),
    mk(age(_RA_GATE_W258), [
        ("W255_W256_W258_bands_respected_A", "W256_W257_W258_bands_respected_A", 1),
        ("W255_W256_W258_bands_respected_B", "W256_W257_W258_bands_respected_B", 1),
    ], "P5e-ra-gate"),
    1, "P5e-ra-gate")

# pf_comment A/B lines
_PFCMT_W254 = '''"    # band gate ADMIT results/_w254bmc_20261016_probe_receipt.json: A = 1-HOP",
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
"    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)",'''
_PFCMT_W255 = mk255(age_prev255(_PFCMT_W254), [
    ("FOURTH consecutive above-own-A;", "FIFTH consecutive above-own-A;", 1),
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 1),
    ("hops=1 -- SECOND", "hops=1 -- THIRD", 1),
    # ENDED-at face: the prev P4 blanket already aged the raw "ENDED at W253;"
    # to "ENDED at W254;" inside the needle -- mechanical aging face,
    # zero sub needed (blanket-duplication class, r1057 precedent)
], "P5e-pfcmt-prev")
_PFCMT_W256 = mk256(age_prev(_PFCMT_W255), [
    ("FIFTH consecutive above-own-A;", "SIXTH consecutive above-own-A;", 1),
    ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 1),
    ("hops=1 -- THIRD", "hops=1 -- FOURTH", 1),
    # ENDED-at face: MY P4 blanket already ages "ENDED at W255;" to
    # "ENDED at W256;" inside the needle -- mechanical aging face,
    # zero sub needed (blanket-duplication class, disclosed)
    # disclosed needle heal #1 (date-roll reconstruction class): the W256
    # editor's own post-P5e date-roll rep FIXED the basename date inside the
    # landed W256 script's pfcmt chunk (20261016 -> 20261017) -- the plain
    # age_prev() blanket leaves the STALE date in the reconstruction, so the
    # W256-editor date-roll sub is replayed here verbatim (1x, evidence =
    # pre-flight raw source count 10 for the FIXED name).
    ("_w256bmc_20261016_probe_receipt.json", "_w256bmc_20261017_probe_receipt.json", 1),
], "P5e-pfcmt-prev2")
_PFCMT_W257 = mk257(age_prev2(_PFCMT_W256), [
          ("SIXTH consecutive above-own-A;", "SEVENTH consecutive above-own-A;", 1),
          ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 1),
          ("hops=1 -- FOURTH", "hops=1 -- FIFTH", 1),
          # ENDED-at face: MY P4 blanket already aged "ENDED at W256;" to
          # "ENDED at W257;" inside the needle -- mechanical aging face,
          # zero sub needed (blanket-duplication class, disclosed)
      ], "P5e-pfcmt-prev3")
_PFCMT_W258 = mk258(age_prev3(_PFCMT_W257), [
          ("SEVENTH consecutive above-own-A;", "EIGHTH consecutive above-own-A;", 1),
          ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 1),
          ("hops=1 -- FIFTH", "hops=1 -- SIXTH", 1),
      ], "P5e-pfcmt-prev4")
chunk(age(_PFCMT_W258),
      mk(age(_PFCMT_W258), [
          ("EIGHTH consecutive above-own-A;", "NINTH consecutive above-own-A;", 1),
          ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 1),
          ("hops=1 -- SIXTH", "hops=1 -- SEVENTH", 1),
      ], "P5e-pfcmt"), "P5e-pfcmt")

# PRE block A/B lines
_PRE_W254 = '''"wave 254: ",
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
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt "'''
_PRE_W255 = mk255(age_prev255(_PRE_W254), [
    ("FOURTH consecutive above-own-A", "FIFTH consecutive above-own-A", 1),
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2),
], "P5e-pre-prev")
_PRE_W256 = mk256(age_prev(_PRE_W255), [
    ("FIFTH consecutive above-own-A", "SIXTH consecutive above-own-A", 1),
    ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 2),
], "P5e-pre-prev2")
_PRE_W257 = mk257(age_prev2(_PRE_W256), [
          ("SIXTH consecutive above-own-A", "SEVENTH consecutive above-own-A", 1),
          ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 2),
      ], "P5e-pre-prev3")
_PRE_W258 = mk258(age_prev3(_PRE_W257), [
          ("SEVENTH consecutive above-own-A", "EIGHTH consecutive above-own-A", 1),
          ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 2),
      ], "P5e-pre-prev4")
chunk(age(_PRE_W258),
      mk(age(_PRE_W258), [
          ("EIGHTH consecutive above-own-A", "NINTH consecutive above-own-A", 1),
          ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 2),
      ], "P5e-pre"), "P5e-pre")

# MEM_I comment lines (A + B faces)
_MEM_A_W254 = ''' f\'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W254 A: {fmt(a_lo)}..{fmt(a_hi)} (1-HOP STAIRCASE-AFFECTS-A walk THIRD consecutive A-hop; naive {fmt(w253_a_tail + 1)}..{fmt(w253_a_tail + 2_000)} REFUSED at start -- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; registered W253 B band inside the naive A window; third consecutive A-hop of the staircase era -- seed-gap face ENDED at W252; A base == registered prior-wave B tail+1)\','''
_MEM_A_W255 = mk255(age_prev255(_MEM_A_W254), [
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 1),
    ("third consecutive A-hop", "fourth consecutive A-hop", 1),
], "P5e-mem-a-prev")
_MEM_A_W256 = mk256(age_prev(_MEM_A_W255), [
    ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 1),
    ("fourth consecutive A-hop", "fifth consecutive A-hop", 1),
], "P5e-mem-a-prev2")
_MEM_A_W257 = mk257(age_prev2(_MEM_A_W256), [
        ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 1),
        ("fifth consecutive A-hop", "sixth consecutive A-hop", 1),
    ], "P5e-mem-a-prev3")
_MEM_A_W258 = mk258(age_prev3(_MEM_A_W257), [
        ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 1),
        ("sixth consecutive A-hop", "seventh consecutive A-hop", 1),
    ], "P5e-mem-a-prev4")
rep(age(_MEM_A_W258),
    mk(age(_MEM_A_W258), [
        ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 1),
        ("seventh consecutive A-hop", "eighth consecutive A-hop", 1),
    ], "P5e-mem-a"),
    1, "P5e-mem-a")
_MEM_B_W254 = ''' f\'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W254 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION CASCADE above own-A; naive {fmt(w253_b_tail + 1)}..{fmt(w253_b_tail + 200)} REFUSED at start -- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; naive window lands inside the own-wave A first-clean window -> own-A reservation cascade; B lands ABOVE own-A at tail+1 EXACT -- fourth consecutive above-own-A; B base == own-A tail+1)\','''
_MEM_B_W255 = mk255(age_prev255(_MEM_B_W254), [("fourth consecutive above-own-A", "fifth consecutive above-own-A", 1)], "P5e-mem-b-prev")
_MEM_B_W256 = mk256(age_prev(_MEM_B_W255), [("fifth consecutive above-own-A", "sixth consecutive above-own-A", 1)], "P5e-mem-b-prev2")
_MEM_B_W257 = mk257(age_prev2(_MEM_B_W256), [("sixth consecutive above-own-A", "seventh consecutive above-own-A", 1)], "P5e-mem-b-prev3")
_MEM_B_W258 = mk258(age_prev3(_MEM_B_W257), [ ("seventh consecutive above-own-A", "eighth consecutive above-own-A", 1),
    ], "P5e-mem-b-prev4")
rep(age(_MEM_B_W258),
    mk(age(_MEM_B_W258), [ ("eighth consecutive above-own-A", "ninth consecutive above-own-A", 1),
    ], "P5e-mem-b"),
    1, "P5e-mem-b")

# tail band-facts comments (A + B lines)
_TAILCMT_W254 = '''"        # band facts (law sec.4 W254 row): A = 1-HOP STAIRCASE-AFFECTS-A",
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
"        # re-derive + live-trace re-read, no staircase-equality assumption);",'''
_TAILCMT_W255 = mk255(age_prev255(_TAILCMT_W254), [
    ("FOURTH consecutive", "FIFTH consecutive", 1),
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2),
], "P5e-tailcmt-prev")
_TAILCMT_W256 = mk256(age_prev(_TAILCMT_W255), [
    ("FIFTH consecutive", "SIXTH consecutive", 1),
    ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 2),
], "P5e-tailcmt-prev2")
_TAILCMT_W257 = mk257(age_prev2(_TAILCMT_W256), [
          ("SIXTH consecutive", "SEVENTH consecutive", 1),
          ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 2),
      ], "P5e-tailcmt-prev3")
_TAILCMT_W258 = mk258(age_prev3(_TAILCMT_W257), [
          ("SEVENTH consecutive", "EIGHTH consecutive", 1),
          ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 2),
      ], "P5e-tailcmt-prev4")
chunk(age(_TAILCMT_W258),
      mk(age(_TAILCMT_W258), [
          ("EIGHTH consecutive", "NINTH consecutive", 1),
          ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 2),
      ], "P5e-tailcmt"), "P5e-tailcmt")

# tail assert block (A face message)
_TAIL_AMSG_W254 = '''            "W254 A staircase-affects-A walk THIRD consecutive A-hop: the naive "',
'            "continuation is REFUSED at its own start (the registered W253 B band sits INSIDE "',
'            "the naive A window -- staircase re-emergence continues; hops=1, A_hop_chain verbatim in the probe receipt, "',
'            "A_clean_at_naive_start=false, A_staircase_hop_past_W253_B=true; the walk hops past "',
'            "the W253 B tail -> A first-clean -- THIRD consecutive A-hop of the staircase era, "',
'            "the fourteen-wave seed-gap face ENDED at W252; A base == registered prior-wave B "',
'            "tail+1 machine-checkable, floor relation honored)"'''
_TAIL_AMSG_W255 = mk255(age_prev255(_TAIL_AMSG_W254), [("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2)], "P5e-tail-amsg-prev")
_TAIL_AMSG_W256 = mk256(age_prev(_TAIL_AMSG_W255), [("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 2)], "P5e-tail-amsg-prev2")
_TAIL_AMSG_W257 = mk257(age_prev2(_TAIL_AMSG_W256), [("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 2)], "P5e-tail-amsg-prev3")
_TAIL_AMSG_W258 = mk258(age_prev3(_TAIL_AMSG_W257), [ ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 2),
    ], "P5e-tail-amsg-prev4")
rep(age(_TAIL_AMSG_W258),
    mk(age(_TAIL_AMSG_W258), [ ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 2),
    ], "P5e-tail-amsg"),
    1, "P5e-tail-amsg")

# tail assert block (B face messages; identity count-asserts per W256 canon)
rep(age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')),
    ))), age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "'))))), 1, "P5e-tail-bassert2")
rep(age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"')),
    ))), age(age_prev3(age_prev2(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"'))))), 1, "P5e-tail-bclean")
_EXCL_W254 = '            "W254 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- fourth consecutive above-own-A; zero overlap)"'
_EXCL_W255 = mk255(age_prev255(_EXCL_W254), [("fourth consecutive above-own-A", "fifth consecutive above-own-A", 1)], "P5e-tail-excl-prev")
_EXCL_W256 = mk256(age_prev(_EXCL_W255), [("fifth consecutive above-own-A", "sixth consecutive above-own-A", 1)], "P5e-tail-excl-prev2")
_EXCL_W257 = mk257(age_prev2(_EXCL_W256), [("sixth consecutive above-own-A", "seventh consecutive above-own-A", 1)], "P5e-tail-excl-prev3")
_EXCL_W258 = mk258(age_prev3(_EXCL_W257), [ ("seventh consecutive above-own-A", "eighth consecutive above-own-A", 1),
    ], "P5e-tail-excl-prev4")
rep(age(_EXCL_W258),
    mk(age(_EXCL_W258), [ ("eighth consecutive above-own-A", "ninth consecutive above-own-A", 1),
    ], "P5e-tail-excl"),
    1, "P5e-tail-excl")

# pr print A/B lines
_PRCHUNK_W254 = ''' '          "A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, "',
 '          "registered W253 B band inside the naive A window, THIRD consecutive A-hop of the staircase era, "',
 '          "the fourteen-wave seed-gap face ENDED at W252) "',
 '          "+ B=1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, "',
 '          "B_hop_chain verbatim, naive window lands inside the own-wave A window -> own-A reservation cascade, "',
 '          "B base == own-A tail+1 EXACT, B_lands_above_own_A=true, "',
 '          "FOURTH consecutive above-own-A landing), chain-order splice from the "'''
_PRCHUNK_W255 = mk255(age_prev255(_PRCHUNK_W254), [
    ("FOURTH consecutive above-own-A landing", "FIFTH consecutive above-own-A landing", 1),
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 1),
], "P5e-pr-prev")
_PRCHUNK_W256 = mk256(age_prev(_PRCHUNK_W255), [
    ("FIFTH consecutive above-own-A landing", "SIXTH consecutive above-own-A landing", 1),
    ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 1),
], "P5e-pr-prev2")
_PRCHUNK_W257 = mk257(age_prev2(_PRCHUNK_W256), [
          ("SIXTH consecutive above-own-A landing", "SEVENTH consecutive above-own-A landing", 1),
          ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 1),
      ], "P5e-pr-prev3")
_PRCHUNK_W258 = mk258(age_prev3(_PRCHUNK_W257), [
          ("SEVENTH consecutive above-own-A landing", "EIGHTH consecutive above-own-A landing", 1),
          ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 1),
      ], "P5e-pr-prev4")
chunk(age(_PRCHUNK_W258),
      mk(age(_PRCHUNK_W258), [
          ("EIGHTH consecutive above-own-A landing", "NINTH consecutive above-own-A landing", 1),
          ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 1),
      ], "P5e-pr"), "P5e-pr")

# receipt band_semantics A + B values
_SEM_A_W254 = '''"A": "1-HOP STAIRCASE-AFFECTS-A walk THIRD consecutive A-hop (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 573_901..575_900 refused at start -- the registered W253 B band 573_901..574_100 sits INSIDE the naive A window (staircase re-emergence continues; the W253 prereg sec.5 item5 A-CLEAN-at-naive projection superseded live r587, divergence disclosed); the walk hops past the W253 B tail 574_100 -> A first-clean 574_101..576_100 -- THIRD consecutive A-hop of the staircase era, the fourteen-wave seed-gap face ENDED at W252; A_clean_at_naive_start=false; A_staircase_hop_past_W253_B=true; A base == registered prior-wave B tail+1 (574_100+1) EXACT)"'''
_SEM_A_W255 = mk255(age_prev255(_SEM_A_W254), [
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2),
    ("573_901..575_900 refused", "576_101..578_100 refused", 1),
    ("573_901..574_100 sits", "576_101..576_300 sits", 1),
    ("B tail 574_100 -> A first-clean 574_101..576_100", "B tail 576_300 -> A first-clean 576_301..578_300", 1),
    ("(574_100+1) EXACT)", "(576_300+1) EXACT)", 1),
], "P5e-rcpt-semantics-A-prev")
_SEM_A_W256 = mk256(age_prev(_SEM_A_W255), [
    ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 2),
    ("576_101..578_100 refused", "578_301..580_300 refused", 1),
    ("576_101..576_300 sits", "578_301..578_500 sits", 1),
    ("B tail 576_300 -> A first-clean 576_301..578_300", "B tail 578_500 -> A first-clean 578_501..580_500", 1),
    ("(576_300+1) EXACT)", "(578_500+1) EXACT)", 1),
], "P5e-rcpt-semantics-A-prev2")
_SEM_A_W257 = mk257(age_prev2(_SEM_A_W256), [
        ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 2),
        ("578_301..580_300 refused", "580_501..582_500 refused", 1),
        ("578_301..578_500 sits", "580_501..580_700 sits", 1),
        ("B tail 578_500 -> A first-clean 578_501..580_500", "B tail 580_700 -> A first-clean 580_701..582_700", 1),
        ("(578_500+1) EXACT)", "(580_700+1) EXACT)", 1),
    ], "P5e-rcpt-semantics-A-prev3")
_SEM_A_W258 = mk258(age_prev3(_SEM_A_W257), [
        ("SIXTH consecutive A-hop", "SEVENTH consecutive A-hop", 2),
        ("580_501..582_500 refused", "582_701..584_700 refused", 1),
        ("580_501..580_700 sits", "582_701..582_900 sits", 1),
        ("B tail 580_700 -> A first-clean 580_701..582_700", "B tail 582_900 -> A first-clean 582_901..584_900", 1),
        ("(580_700+1) EXACT)", "(582_900+1) EXACT)", 1),
    ], "P5e-rcpt-semantics-A-prev4")
rep(age(_SEM_A_W258),
    mk(age(_SEM_A_W258), [
        ("SEVENTH consecutive A-hop", "EIGHTH consecutive A-hop", 2),
        ("582_701..584_700 refused", "584_901..586_900 refused", 1),
        ("582_701..582_900 sits", "584_901..585_100 sits", 1),
        ("B tail 582_900 -> A first-clean 582_901..584_900", "B tail 585_100 -> A first-clean 585_101..587_100", 1),
        ("(582_900+1) EXACT)", "(585_100+1) EXACT)", 1),
    ], "P5e-rcpt-semantics-A"),
    1, "P5e-rcpt-semantics-A")
_SEM_B_W254 = '''"B": "1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the naive continuation 574_101..574_300 is refused at start -- the naive window lands INSIDE the own-wave W254 A first-clean window 574_101..576_100 (own-A reservation cascade standard leg; the W253 prereg sec.5 item5 + probe leg4 projected landing superseded live -- the A face itself moved, divergence disclosed per r587); the walk hops past the own-A tail 576_100 -> B landing 576_101..576_300; B lands ABOVE own-A -- FOURTH consecutive above-own-A landing; B_lands_above_own_A=true; B_hop_lands_inside_A=false; B base == own-A tail+1 (576_100+1) EXACT)"'''
_SEM_B_W255 = mk255(age_prev255(_SEM_B_W254), [
    ("FOURTH consecutive above-own-A landing", "FIFTH consecutive above-own-A landing", 1),
    ("574_101..574_300 is refused", "576_301..576_500 is refused", 1),
    ("A first-clean window 574_101..576_100 (own-A", "A first-clean window 576_301..578_300 (own-A", 1),
    ("own-A tail 576_100 -> B landing 576_101..576_300;", "own-A tail 578_300 -> B landing 578_301..578_500;", 1),
    ("(576_100+1) EXACT)", "(578_300+1) EXACT)", 1),
], "P5e-rcpt-semantics-B-prev")
_SEM_B_W256 = mk256(age_prev(_SEM_B_W255), [
    ("FIFTH consecutive above-own-A landing", "SIXTH consecutive above-own-A landing", 1),
    ("576_301..576_500 is refused", "578_501..578_700 is refused", 1),
    ("A first-clean window 576_301..578_300 (own-A", "A first-clean window 578_501..580_500 (own-A", 1),
    ("own-A tail 578_300 -> B landing 578_301..578_500;", "own-A tail 580_500 -> B landing 580_501..580_700;", 1),
    ("(578_300+1) EXACT)", "(580_500+1) EXACT)", 1),
], "P5e-rcpt-semantics-B-prev2")
_SEM_B_W257 = mk257(age_prev2(_SEM_B_W256), [
        ("SIXTH consecutive above-own-A landing", "SEVENTH consecutive above-own-A landing", 1),
        ("578_501..578_700 is refused", "580_701..580_900 is refused", 1),
        ("A first-clean window 578_501..580_500 (own-A", "A first-clean window 580_701..582_700 (own-A", 1),
        ("own-A tail 580_500 -> B landing 580_501..580_700;", "own-A tail 582_700 -> B landing 582_701..582_900;", 1),
        ("(580_500+1) EXACT)", "(582_700+1) EXACT)", 1),
    ], "P5e-rcpt-semantics-B-prev3")
_SEM_B_W258 = mk258(age_prev3(_SEM_B_W257), [
        ("SEVENTH consecutive above-own-A landing", "EIGHTH consecutive above-own-A landing", 1),
        ("580_701..580_900 is refused", "582_901..583_100 is refused", 1),
        ("A first-clean window 580_701..582_700 (own-A", "A first-clean window 582_901..584_900 (own-A", 1),
        ("own-A tail 582_700 -> B landing 582_701..582_900;", "own-A tail 584_900 -> B landing 584_901..585_100;", 1),
        ("(582_700+1) EXACT)", "(584_900+1) EXACT)", 1),
    ], "P5e-rcpt-semantics-B-prev4")
rep(age(_SEM_B_W258),
    mk(age(_SEM_B_W258), [
        ("EIGHTH consecutive above-own-A landing", "NINTH consecutive above-own-A landing", 1),
        ("582_901..583_100 is refused", "585_101..585_300 is refused", 1),
        ("A first-clean window 582_901..584_900 (own-A", "A first-clean window 585_101..587_100 (own-A", 1),
        ("own-A tail 584_900 -> B landing 584_901..585_100;", "own-A tail 587_100 -> B landing 587_101..587_300;", 1),
        ("(584_900+1) EXACT)", "(587_100+1) EXACT)", 1),
    ], "P5e-rcpt-semantics-B"),
    1, "P5e-rcpt-semantics-B")

# downstream W260+ projection face (probe leg4 verbatim numbers)
_DOWNSTREAM_W254 = '''W255 = next free number, next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W255 freezer MUST re-derive live on the post-W254 universe + reserve the own-wave A window when deriving B per the W254 seat leg4 mandate, never transcribe r587 -- W255p face per this window's probe leg4 (pre-W254 universe): A naive 576101..578100 CLEAN (hops=0, zero live refusers -- pre-W254-universe face) / B naive 576301..576500 hops=0 CLEAN at naive, first-clean 576301..576500 BUT lands INSIDE the W255 projection A window (W255p_B_lands_inside_W255p_A_naive=true staircase face continuation since W252: A hops over prior B, B lands above own-A; on the post-W254 universe the W255 naive A window start 576_101 lands INSIDE the registered W254 B band 576_101..576_300 -- staircase affects A inherited, the A first-clean and the B own-A reservation cascade landing both move up, live re-derive governs); re-read the live trace at W255 derive time, do NOT assume the staircase A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities'''
_DOWNSTREAM_W255 = mk255(age_prev255(_DOWNSTREAM_W254), [
    ("A naive 576101..578100 CLEAN", "A naive 578301..580300 CLEAN", 1),
    ("B naive 576301..576500 hops=0 CLEAN at naive, first-clean 576301..576500 BUT", "B naive 578501..578700 hops=0 CLEAN at naive, first-clean 578501..578700 BUT", 1),
    ("naive A window start 576_101 lands INSIDE the registered W255 B band 576_101..576_300", "naive A window start 578_301 lands INSIDE the registered W255 B band 578_301..578_500", 1),
    ("staircase face continuation since W252", "staircase face continuation since W251", 1),
], "P5e-rcpt-downstream-prev")
_DOWNSTREAM_W256 = mk256(age_prev(_DOWNSTREAM_W255), [
    ("A naive 578301..580300 CLEAN", "A naive 580501..582500 CLEAN", 1),
    ("B naive 578501..578700 hops=0 CLEAN at naive, first-clean 578501..578700 BUT", "B naive 580701..580900 hops=0 CLEAN at naive, first-clean 580701..580900 BUT", 1),
    ("naive A window start 578_301 lands INSIDE the registered W256 B band 578_301..578_500", "naive A window start 580_501 lands INSIDE the registered W256 B band 580_501..580_700", 1),
], "P5e-rcpt-downstream-prev2")
_DOWNSTREAM_W257 = mk257(age_prev2(_DOWNSTREAM_W256), [
        ("A naive 580501..582500 CLEAN", "A naive 582701..584700 CLEAN", 1),
        ("B naive 580701..580900 hops=0 CLEAN at naive, first-clean 580701..580900 BUT", "B naive 582901..583100 hops=0 CLEAN at naive, first-clean 582901..583100 BUT", 1),
        ("naive A window start 580_501 lands INSIDE the registered W257 B band 580_501..580_700", "naive A window start 582_701 lands INSIDE the registered W257 B band 582_701..582_900", 1),
    ], "P5e-rcpt-downstream-prev3")
_DOWNSTREAM_W258 = mk258(age_prev3(_DOWNSTREAM_W257), [
        ("A naive 582701..584700 CLEAN", "A naive 584901..586900 CLEAN", 1),
        ("B naive 582901..583100 hops=0 CLEAN at naive, first-clean 582901..583100 BUT", "B naive 585101..585300 hops=0 CLEAN at naive, first-clean 585101..585300 BUT", 1),
        ("naive A window start 582_701 lands INSIDE the registered W258 B band 582_701..582_900", "naive A window start 584_901 lands INSIDE the registered W258 B band 584_901..585_100", 1),
    ], "P5e-rcpt-downstream-prev4")
rep(age(_DOWNSTREAM_W258),
    mk(age(_DOWNSTREAM_W258), [
        ("A naive 584901..586900 CLEAN", "A naive 587101..589100 CLEAN", 1),
        ("B naive 585101..585300 hops=0 CLEAN at naive, first-clean 585101..585300 BUT", "B naive 587301..587500 hops=0 CLEAN at naive, first-clean 587301..587500 BUT", 1),
        ("naive A window start 584_901 lands INSIDE the registered W259 B band 584_901..585_100", "naive A window start 587_101 lands INSIDE the registered W259 B band 587_101..587_300", 1),
    ], "P5e-rcpt-downstream"),
    1, "P5e-rcpt-downstream")

# ============ P5f: probe-receipt date face (DATE-STABLE this generation) ============
# disclosed date-stable face: the W259 probe receipt basename keeps the SAME
# date AGAIN (20261017 == 20261017, third consecutive date-stable
# generation) -- the blanket P3 already rolled the basename to
# _w259bmc_20261017_probe_receipt.json which IS the correct on-disk name;
# this rep is an identity count-assert (10x), zero heal needed (vs the W256
# editor's 10x date-roll rep 20261016->20261017). Position stays POST-P5e
# (the pfcmt chunk needle embeds the pre-replacement basename face).
rep(age("_w258bmc_20261017_probe_receipt.json"), "_w259bmc_20261017_probe_receipt.json", 10, "P5f-probe-receipt-date-stable")

# ============ structural output gates ============
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
    ("w244_a", 12),  # needle-heal r1064: band-set var is FROZEN-verbatim lineage (W255..W258 4-gen canon, "one-behind naming face, zero functional impact" per W255 receipt note); the build_editor gate-list composition wrongly rolled this frozen token +1 -> healed back, disclosed
    ("SEVENTY-NINTH", 3),
    ("TWO HUNDRED AND FIFTY-NINTH", 3),
    ("forty-seventh consecutive", 2),
    ("bmc_ordinal=79", 7),
    ("79th own wave", 3),
    ("r1062 splice window", 3),
    ("r1062", 23),
    ("r1063", 7),
    ("r1064 freeze window", 1),  # needle-heal r1064: stamp = actual freeze window (see P5a-header-window heal)
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
    ("248th", 0),  # needle-heal r1064: anti-gate must target the CONSUMED old ordinal face (W258 canon precedent: anti-gate "247th"); the build_editor wrongly rolled the anti-gate onto the NEW face that P5d-ord-owner-prose reps legitimately create x2
    ("247/129/77", 0),  # needle-heal r1064: anti-gate must target the CONSUMED old error-string face (P5d-ord-err rep legitimately creates "248/129/78 PRE-splice post-W258" x1 as the CURRENT face); build_editor wrongly rolled the anti-gate onto the new face
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

io.open(DST, "w", encoding="utf-8", newline="").write(t)
import py_compile
py_compile.compile(DST, doraise=True)
io.open(LOG, "w", encoding="utf-8").write("\n".join(log))
print(f"DERIVE OK -> {DST} ({len(t)} chars); {len(log)} transform log rows")
print("\n".join(log[-12:]))
