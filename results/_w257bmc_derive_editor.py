# -*- coding: utf-8 -*-
# r1060 bm-c: derive results/_w257bmc_freeze_edits.py from the committed W256
# freeze-edits script (results/_w256bmc_freeze_edits.py, proven live-fire W256
# splice bm-c r1058 window: splice aa6102e35 + engine self-burn 12/12 + finalize
# one-pass ledger 987,535 / K=561,120 five-key 6/6 by the r1058 continuation
# closeout 27ee6e95a) via COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage,
# 9th-gen pass ordering: P1 structural outputs BLANKET-IMMUNE; the W257
# extraction faces stay structurally identical to the W256 estate mandate --
# estate 69 rows W138..W206 full-span ONLY + kept W211..W238 (28) + dropped
# W239..W255 (17) + fresh W239..W256 (18) = 115 parity rows per the frozen
# W257 prereg sec.3 mandate -- only the count faces move 17->18 / 114->115 /
# 44->45 / 16->17).
# W257 facts (machine-read from the probe receipt _w257bmc_20261017, never
# transcribed):
# bands A 580_701..582_700 (1-HOP STAIRCASE-AFFECTS-A walk, SIXTH
# consecutive A-hop -- the naive continuation 580_501..582_500 is REFUSED at
# its own start: the registered W256 B band 580_501..580_700 sits INSIDE the
# naive A window = staircase CONTINUES to affect A, the W256 prereg sec.5
# item5 post-W256-REGISTERED pre-disclosure MATERIALIZED as projected; the
# walk hops past the W256 B tail 580_700 -> A first-clean 580_701..582_700,
# hops=1; A base == registered prior-wave B tail+1 (580_700+1) EXACT) /
# B 582_701..582_900 (1-HOP own-A RESERVATION CASCADE above own-A, SEVENTH
# consecutive -- the naive continuation 580_701..580_900 is REFUSED at its
# own start: the naive window lands INSIDE the own-wave W257 A first-clean
# window 580_701..582_700; the walk hops past the own-A tail 582_700 -> B
# landing 582_701..582_900, hops=1; B base == own-A tail+1 (582_700+1) EXACT),
# upstream W256 = bm-c own chain, seat MSG-20261017-03xx-bmc-w257-seat @
# origin 27ee6e95a r1058 closeout, prereg c7fbc443c derived bm-c r1059
# (authored 04:1x by the r1059 window; freeze landed 04:17 by it; splice
# window = r1060 THIS window -- prereg window != splice window this
# generation, disclosed; 2026-10-16/17 chains diverge from the W256
# prereg==splice same-window face).
# Needle law this generation: ALL chunk/repp needles are machine-derived via
# age() = the exact blanket composition (P2 W257->W258, P3 256->257,
# P4 255->256) applied to the W256-script-era literals; the W255-era chunk
# faces are reconstructed by the THREE-LEVEL chain mk255(age_prev255(W254
# literal)) -> mk256(age_prev(...)) -> age() needle (E63 9th-gen, disclosed;
# needle pre-flight probe results/_w257bmc_needle_preflight.py ALL PASS).
# Date-stable face this generation: the probe receipt basename date does NOT
# roll (20261017 == 20261017) -- the P5f rep is an identity count-assert
# (10x), zero heal needed (disclosed, vs the W256 editor's 10x date-roll).
import io, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w256bmc_freeze_edits.py")
DST = os.path.join(REPO, "results", "_w257bmc_freeze_edits.py")
LOG = os.path.join(REPO, "results", "_w257bmc_derive_editor_log.txt")
PY = sys.executable

# S0: SRC worktree == committed HEAD blob (r609 origin-verbatim base law)
blob_wt = subprocess.run(["git", "hash-object", SRC], capture_output=True, text=True, cwd=REPO).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w256bmc_freeze_edits.py"], capture_output=True, text=True, cwd=REPO).stdout.strip()
assert blob_wt == blob_head and len(blob_wt) == 40, f"SRC blob drift: wt={blob_wt} head={blob_head}"
assert blob_wt == "ba18d525d40b20c3a151c17c7933812deaf414f2", f"SRC blob face drift: {blob_wt}"

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

# age(): EXACT composition of MY blanket passes (P2 downstream W257->W258,
# P3 self 256->257, P4 upstream 255->256) -- derives post-pass needles from
# W256-script-era literals WITHOUT hand-derivation.
def age(s):
    s = s.replace("W257", "W258")
    s = s.replace("256", "257")
    s = s.replace("255", "256")
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

# mk(): build a chunk NEW text from its (post-blanket) needle via ordered
# count-asserted fact replacements -- W257 facts from the probe receipt.
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
rep("(252, 251, 250, 249, 248, 247, 246, 245, 244, 243)",
    "(253, 252, 251, 250, 249, 248, 247, 246, 245, 244)", 2, "P1-transitive-deps")
rep("range(209, 257)", "range(209, 258)", 2, "P1-liveness-range")
rep('def fmt(n):  # 578501 -> "578_501"', 'def fmt(n):  # 580701 -> "580_701"', 1, "P1-fmt-comment")

# ============ P2: downstream shift W257 -> W258 ============
rep("W257", "W258", None, "P2-downstream")
assert "W257" not in t, "P2 leftover W257"

# ============ P3: self shift 256 -> 257 ============
n256 = t.count("256")
rep("256", "257", None, "P3-self")
log.append(f"P3 consumed {n256} '256' substrings")

# ============ P4: upstream shift 255 -> 256 ============
n255 = t.count("255")
rep("255", "256", None, "P4-upstream")
log.append(f"P4 consumed {n255} '255' substrings")

# ============ P4x: blanket-exemption heal (API-name face, disclosed) ============
# disclosed needle heal #2 (blanket-exemption class, NEW face this generation):
# the P3 self-shift rep("256","257") also hit the FOUR "hashlib.sha256"
# API-name occurrences inside the source (sha256 is an ALGORITHM name, not a
# wave face) -- restored verbatim immediately post-blanket, count-asserted 4x.
# Prior generations' P3 needles (254->255, 255->256) never collided with an
# API name ("sha255"/"sha254" do not exist), so this exemption face is new
# to the 256->257 generation; evidence = token scans (source sha256=4, all
# other 256-tokens verified wave faces; all 255-tokens verified wave faces).
rep("hashlib.sha257", "hashlib.sha256", 4, "P4x-sha256-api-heal")

# ============ P5a: numeric/anchor/ordinal/window faces (post-blanket forms) ============
# r-window ORDER DISCLOSURE (needle heal this generation, vs the W256 editor
# order): the source's own prereg-window refs are r1058 (7x) AND its freeze
# stamp is r1058 (1x) -- the W257 chain ALSO lands on r1058 windows (W256
# splice r1058), so the chain reps below CREATE new "r1058" strings. The
# prereg rep must therefore run BEFORE the chain reps (header-window first
# consumes the freeze stamp; prereg rep consumes the 7 own-window refs;
# closeout/splice/rest then create the new r1058 chain refs). W256 editor
# order ran prereg LAST -- inapplicable here (its prereg refs were r1056, a
# number no other rep creates or consumes). Disclosed, count-asserted.
rep(age("2026-10-17 03:2x bm-c r1058 freeze window"), "2026-10-17 04:4x bm-c r1060 freeze window", 1, "P5a-header-window")
rep(age("r1058"), "r1059", 7, "P5a-prereg-window")
rep(age("W255 finalize one-pass bm-c r1057 window closeout 02:3x"),
    "W256 finalize one-pass bm-c r1058 window closeout 04:0x", 1, "P5a-closeout-window")
rep(age("r1057 splice window"), "r1058 splice window", 3, "P5a-splice-window")
rep(age("r1057"), "r1058", 19, "P5a-splice-window-rest")
rep(age("authored 03:01"), "authored 04:1x", 2, "P5a-authored-time")
rep(age("985_335"), "987_535", 1, "P5a-ledger-int")
rep(age("558_920"), "561_120", 1, "P5a-k-int")
rep(age("985,335"), "987,535", 8, "P5a-ledger-prose")
rep(age("558,920"), "561,120", 8, "P5a-k-prose")
rep(age("bmc_ordinal=76"), "bmc_ordinal=77", 7, "P5a-ordinal76")
rep(age("SEVENTY-SIXTH"), "SEVENTY-SEVENTH", 3, "P5a-seventysixth")
rep(age("TWO HUNDRED AND FIFTY-SIXTH"), "TWO HUNDRED AND FIFTY-SEVENTH", 3, "P5a-250th")
rep(age("forty-fourth consecutive"), "forty-fifth consecutive", 2, "P5a-finface")
rep(age("76th own wave"), "77th own wave", 3, "P5a-76th-ownwave")
rep(age("MSG-20261017-023x-bmc-w256-seat"), "MSG-20261017-03xx-bmc-w257-seat", 7, "P5a-seat-msg")
rep(age("fd48643c9"), "27ee6e95a", 2, "P5a-seat-origin")
rep(age("5996e2c93"), "c7fbc443c", 1, "P5a-prereg-commit")
# aging-face needle heals (same-window disclosed, r1045/r1047/r1050/r1055/r1057/r1058 precedent family):
rep(age("transitive window W243..W252 checked"), "transitive window W244..W253 checked", 1, "P5a-aging-deps-cmt")
rep(age("engine_owner==bm-c rows 75 + candidate"), "engine_owner==bm-c rows 76 + candidate", 1, "P5a-aging-rows-heal")

# ============ P5b: extraction count faces (frozen W257 prereg sec.3 mandate) ============
# estate 69 (W138..W206) + kept W211..W238 (28) UNCHANGED; dropped W239..W255 (17);
# fresh W239..W256 (18); total parity 115 rows; legs segment W211..W255 (45).
rep(age("# block's own W239..W254 legs (16 rows) do NOT enter the estate path;"),
    "# block's own W239..W255 legs (17 rows) do NOT enter the estate path;", 1, "P5b-hdr-ownlegs")
rep(age("# after extraction, fresh W239..W255 legs (17 rows) are added,"),
    "# after extraction, fresh W239..W256 legs (18 rows) are added,", 1, "P5b-hdr-freshlegs")
rep(age("# parity = 114 rows (W138..W206 + W211..W255). Zero assumption zero risk."),
    "# parity = 115 rows (W138..W206 + W211..W256). Zero assumption zero risk.", 1, "P5b-hdr-parity-count")
rep(age("# block's own W239..W254 legs (16) are EXCLUDED from the estate path per the"),
    "# block's own W239..W255 legs (17) are EXCLUDED from the estate path per the", 1, "P5b-ext-excl")
rep(age("# prereg mandate; the W256 block appends fresh W239..W255 legs (17,"),
    "# prereg mandate; the W257 block appends fresh W239..W256 legs (18,", 1, "P5b-ext-fresh")
rep(age("# machine-derived from the LIVE pf registry at freeze time) -> 114 parity"),
    "# machine-derived from the LIVE pf registry at freeze time) -> 115 parity", 1, "P5b-ext-parcount")

_PARFULL_W255 = '''assert par_full.count("assert pf.N1_BANDS[") == 112, \\
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 112 (69 estate + W211..W253 legs 43)"'''
_PARFULL_W256 = mk256(age_prev(_PARFULL_W255), [("== 112", "== 113", 1),
                        ("!= 112 (69 estate + W211..W253 legs 43)", "!= 113 (69 estate + W211..W254 legs 44)", 1)], "P5b-parfull-prev")
rep(age(_PARFULL_W256),
    mk(age(_PARFULL_W256), [("== 113", "== 114", 1),
                            ("!= 113 (69 estate + W211..W254 legs 44)", "!= 114 (69 estate + W211..W255 legs 45)", 1)], "P5b-parfull"),
    1, "P5b-parfull")
_LEGS_W255 = '''assert legs_sec.count("assert pf.N1_BANDS[") == 43 \\
    and [int(w) for w in _legs_ws] == list(range(211, 254)), \\
    f"legs segment not W211..W253 forty-three legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}"'''
_LEGS_W256 = mk256(age_prev(_LEGS_W255), [("== 43", "== 44", 1),
                      ("legs segment not W211..W253 forty-three legs", "legs segment not W211..W254 forty-four legs", 1)], "P5b-legs-prev")
rep(age(_LEGS_W256),
    mk(age(_LEGS_W256), [("== 44", "== 45", 1),
                          ("legs segment not W211..W254 forty-four legs", "legs segment not W211..W255 forty-five legs", 1)], "P5b-legs-assert"),
    1, "P5b-legs-assert")
_DROP_W255 = '''assert legs_dropped.count("assert pf.N1_BANDS[") == 15 \\
    and [int(w) for w in _dropped_ws] == list(range(239, 254)), \\
    f"dropped segment not W239..W253 fifteen legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}"'''
_DROP_W256 = mk256(age_prev(_DROP_W255), [("== 15", "== 16", 1),
                      ("dropped segment not W239..W253 fifteen legs", "dropped segment not W239..W254 sixteen legs", 1)], "P5b-dropped-prev")
rep(age(_DROP_W256),
    mk(age(_DROP_W256), [("== 16", "== 17", 1),
                          ("dropped segment not W239..W254 sixteen legs", "dropped segment not W239..W255 seventeen legs", 1)], "P5b-dropped-assert"),
    1, "P5b-dropped-assert")
rep(age("# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W255\n# block's own W239..W254 legs (16) are excluded from the estate path"),
    "# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W256\n# block's own W239..W255 legs (17) are excluded from the estate path", 1, "P5b-split-cmt")
rep(age('"fresh_legs_row_asserts": 17,'), '"fresh_legs_row_asserts": 18,', 1, "P5b-rcpt-fresh17")
rep(age('+ legs_kept.count("assert pf.N1_BANDS[") + 17,'), '+ legs_kept.count("assert pf.N1_BANDS[") + 18,', 1, "P5b-rcpt-total17")
rep(age('"    #     physical bytes; the W255 block\'s own W239..W254 legs (16) are",'),
    '"    #     physical bytes; the W256 block\'s own W239..W255 legs (17) are",', 1, "P5b-hdr-ownlegs-mat")
rep(age('"    #     W239..W255 legs (17) added, machine-derived from the live pf",'),
    '"    #     W239..W256 legs (18) added, machine-derived from the live pf",', 1, "P5b-hdr-freshlegs-mat")
rep(age('"    #     registry at freeze time -> 114 parity rows (W138..W206+W211..W255).",'),
    '"    #     registry at freeze time -> 115 parity rows (W138..W206+W211..W256).",', 1, "P5b-hdr-parcount-mat")

# receipt note (single big face: counts + generation stamp)
_RCPTNOTE_W255 = '''                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W238 legs (28) extracted verbatim per the frozen W255 prereg sec.3 mandate; the W254 block's own W239..W253 legs (15) EXCLUDED from the estate path per the same mandate; fresh W239..W254 legs (16) machine-derived from the live pf registry -> W255 block = 113 rows (W138..W206 + W211..W254); disclosed: (a) inherited W213 leg error-string face preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-255 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 7th-gen prevention this window: the W255 derive editor kept the P1-blanket-immune pass ordering and the extraction-restructure legs/kept/dropped wave-identity asserts fixed post-blanket (list(range(211,254))/list(range(211,239))/list(range(239,254)) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},'''
_RCPTNOTE_W256 = mk256(age_prev(_RCPTNOTE_W255), [
    ("own W239..W253 legs (15) EXCLUDED", "own W239..W254 legs (16) EXCLUDED", 1),
    ("fresh W239..W255 legs (16) machine-derived", "fresh W239..W255 legs (17) machine-derived", 1),
    ("W256 block = 113 rows", "W256 block = 114 rows", 1),
    ("E63 7th-gen", "E63 8th-gen", 1),
], "P5b-rcpt-note-prev")
rep(age(_RCPTNOTE_W256),
    mk(age(_RCPTNOTE_W256), [
        ("own W239..W254 legs (16) EXCLUDED", "own W239..W255 legs (17) EXCLUDED", 1),
        ("fresh W239..W256 legs (17) machine-derived", "fresh W239..W256 legs (18) machine-derived", 1),
        ("W257 block = 114 rows", "W257 block = 115 rows", 1),
        ("E63 8th-gen", "E63 9th-gen", 1),
    ], "P5b-rcpt-note"),
    1, "P5b-rcpt-note")

# ============ P5c: band literals (probe ADMIT receipt bands) ============
rep(age('assert (a_lo, a_hi) == (578_501, 580_500) and (b_lo, b_hi) == (580_501, 580_700), \\'),
    'assert (a_lo, a_hi) == (580_701, 582_700) and (b_lo, b_hi) == (582_701, 582_900), \\', 1, "P5c-band-drift")

# ============ P5d: ordinal/leg0/deps faces ============
rep(age('assert len(owner_rows_live) == 245 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 75, \\'),
    'assert len(owner_rows_live) == 246 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 76, \\', 1, "P5d-ord-gate")
# needle narrowed to the pre-registration numeric face: the trailing "77th own
# wave" inside this line was ALREADY rewritten by the P5a-76th-ownwave rep
# (order-sensitive face, W256 editor canon -- its P5d needle was likewise the
# post-P5a form); disclosed needle heal, evidence = pre-flight n=1 raw face.
rep(age("(expect 245/129/75 PRE-splice post-W255 registration"),
    "(expect 246/129/76 PRE-splice post-W256 registration", 1, "P5d-ord-err")
# needle narrowed likewise: the trailing "bmc_ordinal=77" on this line was
# already rewritten by the P5a-ordinal76 rep (one of its 7 faces).
rep(age('# receipt leg0 face owner_rows=245 / bmc_rows=75 /'),
    '# receipt leg0 face owner_rows=246 / bmc_rows=76 /', 1, "P5d-leg0-prose")
rep(age("-> owner rows 245 + candidate = 246th EXACT; bm-c rows 75 +"),
    "-> owner rows 246 + candidate = 247th EXACT; bm-c rows 76 +", 1, "P5d-ord-owner-prose")
rep(age("# candidate = 76th EXACT -- bm-c own-seat continuity face (bm-c published the"),
    "# candidate = 77th EXACT -- bm-c own-seat continuity face (bm-c published the", 1, "P5d-ord-bmc-prose")
rep(age("freeze-time live face owner rows 245 + candidate = 246th EXACT"),
    "freeze-time live face owner rows 246 + candidate = 247th EXACT", 1, "P5d-rcpt-246th")
rep(age("freeze-time live derive bmc rows 75 + candidate 76th EXACT per r587/r359"),
    "freeze-time live derive bmc rows 76 + candidate 77th EXACT per r587/r359", 1, "P5d-bundle-76th")
rep(age("post-W255 registration: bm-c rows 75 + candidate = 76th owned"),
    "post-W256 registration: bm-c rows 76 + candidate = 77th owned", 1, "P5d-rcpt-76th-owned")
rep(age('"probe_receipt_bmc_ordinal_face": 76,'), '"probe_receipt_bmc_ordinal_face": 77,', 1, "P5d-rcpt-ordface")
rep(age('f"W256+W251..W242 finalize products present "'), 'f"W257+W252..W243 finalize products present "', 1, "P5d-print-deps")

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
chunk(age(_HDR_W256),
      mk(age(_HDR_W256), [
          ("SIXTH consecutive\n# above-own-A", "SEVENTH consecutive\n# above-own-A", 1),
          ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 1),
          ("578_501..580_500", "580_701..582_700", 2),
          ("580_501..580_700", "582_701..582_900", 1),
          ("578_301..580_300", "580_501..582_500", 1),
          ("578_301..578_500", "580_501..580_700", 1),
          ("578_501..578_700", "580_701..580_900", 1),
          ("578_500", "580_700", 2),
          ("580_500", "582_700", 2),
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
chunk(age(_BANDFACTS_W256),
      mk(age(_BANDFACTS_W256), [
          ("SIXTH consecutive above-own-A landing", "SEVENTH consecutive above-own-A landing", 1),
          ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 2),
      ], "P5e-bandfacts"), "P5e-bandfacts")

_A_BASE_W254 = '''assert w253_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1 EXACT -- the 1-hop walk past the registered W253 B band; third consecutive A-hop of the staircase era; A_staircase_hop_past_W253_B=true)"'''
_A_BASE_W255 = mk255(age_prev255(_A_BASE_W254), [("third consecutive A-hop", "fourth consecutive A-hop", 1)], "P5e-a-base-prev")
_A_BASE_W256 = mk256(age_prev(_A_BASE_W255), [("fourth consecutive A-hop", "fifth consecutive A-hop", 1)], "P5e-a-base-prev2")
rep(age(_A_BASE_W256),
    mk(age(_A_BASE_W256), [("fifth consecutive A-hop", "sixth consecutive A-hop", 1)], "P5e-a-base"),
    1, "P5e-a-base")
_A_FLOOR_W254 = '''assert a_lo >= w253_b_tail + 1, "A staircase landing floor relation (A base >= registered prior-wave B tail+1; the fourteen-wave seed-gap face ENDED at W252 -- third consecutive A-hop of the staircase era, A base == prior-B tail+1 EXACT this window per the prereg floor-relation mandate)"'''
_A_FLOOR_W255 = mk255(age_prev255(_A_FLOOR_W254), [("third consecutive A-hop", "fourth consecutive A-hop", 1)], "P5e-a-floor-prev")
_A_FLOOR_W256 = mk256(age_prev(_A_FLOOR_W255), [("fourth consecutive A-hop", "fifth consecutive A-hop", 1)], "P5e-a-floor-prev2")
rep(age(_A_FLOOR_W256),
    mk(age(_A_FLOOR_W256), [("fifth consecutive A-hop", "sixth consecutive A-hop", 1)], "P5e-a-floor"),
    1, "P5e-a-floor")
_B_BASE_W254 = '''assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation cascade lands ABOVE own-A -- fourth consecutive above-own-A; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"'''
_B_BASE_W255 = mk255(age_prev255(_B_BASE_W254), [("fourth consecutive above-own-A", "fifth consecutive above-own-A", 1)], "P5e-b-base-prev")
_B_BASE_W256 = mk256(age_prev(_B_BASE_W255), [("fifth consecutive above-own-A", "sixth consecutive above-own-A", 1)], "P5e-b-base-prev2")
rep(age(_B_BASE_W256),
    mk(age(_B_BASE_W256), [("sixth consecutive above-own-A", "seventh consecutive above-own-A", 1)], "P5e-b-base"),
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
rep(age(_RA_GATE_W256),
    mk(age(_RA_GATE_W256), [
        ("W253_W254_W256_bands_respected_A", "W254_W255_W256_bands_respected_A", 1),
        ("W253_W254_W256_bands_respected_B", "W254_W255_W256_bands_respected_B", 1),
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
chunk(age(_PFCMT_W256),
      mk(age(_PFCMT_W256), [
          ("SIXTH consecutive above-own-A;", "SEVENTH consecutive above-own-A;", 1),
          ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 1),
          ("hops=1 -- FOURTH", "hops=1 -- FIFTH", 1),
          # ENDED-at face: MY P4 blanket already aged "ENDED at W256;" to
          # "ENDED at W257;" inside the needle -- mechanical aging face,
          # zero sub needed (blanket-duplication class, disclosed)
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
chunk(age(_PRE_W256),
      mk(age(_PRE_W256), [
          ("SIXTH consecutive above-own-A", "SEVENTH consecutive above-own-A", 1),
          ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 2),
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
rep(age(_MEM_A_W256),
    mk(age(_MEM_A_W256), [
        ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 1),
        ("fifth consecutive A-hop", "sixth consecutive A-hop", 1),
    ], "P5e-mem-a"),
    1, "P5e-mem-a")
_MEM_B_W254 = ''' f\'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W254 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION CASCADE above own-A; naive {fmt(w253_b_tail + 1)}..{fmt(w253_b_tail + 200)} REFUSED at start -- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; naive window lands inside the own-wave A first-clean window -> own-A reservation cascade; B lands ABOVE own-A at tail+1 EXACT -- fourth consecutive above-own-A; B base == own-A tail+1)\','''
_MEM_B_W255 = mk255(age_prev255(_MEM_B_W254), [("fourth consecutive above-own-A", "fifth consecutive above-own-A", 1)], "P5e-mem-b-prev")
_MEM_B_W256 = mk256(age_prev(_MEM_B_W255), [("fifth consecutive above-own-A", "sixth consecutive above-own-A", 1)], "P5e-mem-b-prev2")
rep(age(_MEM_B_W256),
    mk(age(_MEM_B_W256), [("sixth consecutive above-own-A", "seventh consecutive above-own-A", 1)], "P5e-mem-b"),
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
chunk(age(_TAILCMT_W256),
      mk(age(_TAILCMT_W256), [
          ("SIXTH consecutive", "SEVENTH consecutive", 1),
          ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 2),
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
rep(age(_TAIL_AMSG_W256),
    mk(age(_TAIL_AMSG_W256), [("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 2)], "P5e-tail-amsg"),
    1, "P5e-tail-amsg")

# tail assert block (B face messages; identity count-asserts per W256 canon)
rep(age(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')),
    ), age(age_prev(age_prev255('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "'))), 1, "P5e-tail-bassert2")
rep(age(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"')),
    ), age(age_prev(age_prev255('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"'))), 1, "P5e-tail-bclean")
_EXCL_W254 = '            "W254 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- fourth consecutive above-own-A; zero overlap)"'
_EXCL_W255 = mk255(age_prev255(_EXCL_W254), [("fourth consecutive above-own-A", "fifth consecutive above-own-A", 1)], "P5e-tail-excl-prev")
_EXCL_W256 = mk256(age_prev(_EXCL_W255), [("fifth consecutive above-own-A", "sixth consecutive above-own-A", 1)], "P5e-tail-excl-prev2")
rep(age(_EXCL_W256),
    mk(age(_EXCL_W256), [("sixth consecutive above-own-A", "seventh consecutive above-own-A", 1)], "P5e-tail-excl"),
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
chunk(age(_PRCHUNK_W256),
      mk(age(_PRCHUNK_W256), [
          ("SIXTH consecutive above-own-A landing", "SEVENTH consecutive above-own-A landing", 1),
          ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 1),
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
rep(age(_SEM_A_W256),
    mk(age(_SEM_A_W256), [
        ("FIFTH consecutive A-hop", "SIXTH consecutive A-hop", 2),
        ("578_301..580_300 refused", "580_501..582_500 refused", 1),
        ("578_301..578_500 sits", "580_501..580_700 sits", 1),
        ("B tail 578_500 -> A first-clean 578_501..580_500", "B tail 580_700 -> A first-clean 580_701..582_700", 1),
        ("(578_500+1) EXACT)", "(580_700+1) EXACT)", 1),
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
rep(age(_SEM_B_W256),
    mk(age(_SEM_B_W256), [
        ("SIXTH consecutive above-own-A landing", "SEVENTH consecutive above-own-A landing", 1),
        ("578_501..578_700 is refused", "580_701..580_900 is refused", 1),
        ("A first-clean window 578_501..580_500 (own-A", "A first-clean window 580_701..582_700 (own-A", 1),
        ("own-A tail 580_500 -> B landing 580_501..580_700;", "own-A tail 582_700 -> B landing 582_701..582_900;", 1),
        ("(580_500+1) EXACT)", "(582_700+1) EXACT)", 1),
    ], "P5e-rcpt-semantics-B"),
    1, "P5e-rcpt-semantics-B")

# downstream W258+ projection face (probe leg4 verbatim numbers)
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
rep(age(_DOWNSTREAM_W256),
    mk(age(_DOWNSTREAM_W256), [
        ("A naive 580501..582500 CLEAN", "A naive 582701..584700 CLEAN", 1),
        ("B naive 580701..580900 hops=0 CLEAN at naive, first-clean 580701..580900 BUT", "B naive 582901..583100 hops=0 CLEAN at naive, first-clean 582901..583100 BUT", 1),
        ("naive A window start 580_501 lands INSIDE the registered W257 B band 580_501..580_700", "naive A window start 582_701 lands INSIDE the registered W257 B band 582_701..582_900", 1),
    ], "P5e-rcpt-downstream"),
    1, "P5e-rcpt-downstream")

# ============ P5f: probe-receipt date face (DATE-STABLE this generation) ============
# disclosed date-stable face: the W257 probe receipt basename keeps the SAME
# date (20261017 == 20261017) -- the blanket P3 already rolled the basename
# to _w257bmc_20261017_probe_receipt.json which IS the correct on-disk name;
# this rep is an identity count-assert (10x), zero heal needed (vs the W256
# editor's 10x date-roll rep 20261016->20261017). Position stays POST-P5e
# (the pfcmt chunk needle embeds the pre-replacement basename face).
rep(age("_w256bmc_20261017_probe_receipt.json"), "_w257bmc_20261017_probe_receipt.json", 10, "P5f-probe-receipt-date-stable")

# ============ structural output gates ============
for needle, want in [
    ("# --- W257 materializer face", 2),
    ("# --- W256 materializer face", 1),
    ('"+ W257 materializer face', 2),
    ("range(16, 257)", 2),
    ("range(17, 257)", 3),
    ("range(239, 257)", 2),
    ("list(range(211, 256)),", 1),
    ("list(range(211, 239))", 1),
    ("list(range(239, 256)),", 1),
    ("range(209, 258)", 2),
    ("if w < 257)", 5),
    ("if w < 256)", 1),
    ("_w257bmc_20261017_probe_receipt.json", 10),
    ("_w257bmc_freeze_receipt.json", 1),
    ("MSG-20261017-03xx-bmc-w257-seat", 7),
    ("27ee6e95a", 2),
    ("987_535", 1),
    ("561_120", 1),
    ("(580_701, 582_700)", 1),
    ("(582_701, 582_900)", 1),
    ("W254_W255_W256_bands_respected_A", 1),
    ("W254_W255_W256_bands_respected_B", 1),
    ("B_base_above_W256_tail", 2),
    ("A_staircase_hop_past_W256_B", None),
    ("W258p_A_naive", 5),
    ("W258p_B_first_clean", 2),
    ("arith_a257", 6),
    ("arith_b257", 6),
    ('"PERPETUAL-N1-W257-SHARD-0"', 1),
    ("n1_w257_results.json", 2),
    ("n1_w257", 4),
    ("n1w257", 2),
    ("PERPETUAL-N1-W257", 7),
    ("_w257bmc", 11),
    ("w244_a", 12),
    ("SEVENTY-SEVENTH", 3),
    ("TWO HUNDRED AND FIFTY-SEVENTH", 3),
    ("forty-fifth consecutive", 2),
    ("bmc_ordinal=77", 7),
    ("77th own wave", 3),
    ("r1058 splice window", 3),
    ("r1058", 23),
    ("r1059", 7),
    ("r1060 freeze window", 1),
    ("estate 69", 1),
    ("= 115 rows", 2),
    ("115 parity", 2),
    ("hops=1", None),
    ("1-HOP", None),
    ("SIXTH consecutive A-hop", None),
    ("SEVENTH consecutive above-own-A", None),
    # anti-gates: stale faces must be zero
    ("r1057", 0),
    ("fd48643c9", 0),
    ("5996e2c93", 0),
    ("985,335", 0),
    ("558,920", 0),
    ("985_335", 0),
    ("558_920", 0),
    ("SEVENTY-SIXTH", 0),
    ("TWO HUNDRED AND FIFTY-SIXTH", 0),
    ("forty-fourth consecutive", 0),
    ("MSG-20261017-023x", 0),
    ("authored 03:01", 0),
    ("bmc_ordinal=76", 0),
    ("76th own wave", 0),
    ("246th", 0),
    ("245/129/75", 0),
    ("SIXTH consecutive above-own-A", 0),
    ("FIRST A-hop", 0),
    ("seed-gap face ENDS", 0),
    ("578_301..580_300", 0),
    ("578_301..578_500", 0),
    ("578_501..578_700", 0),
    ("578_501..580_500", 0),
    ("578_500", 0),
    ("580_500", 0),
    ("578_301", 0),
    ("578_501", 0),
    ("~575_901..575_900", 0),
    ("(578_501, 580_500)", 0),
    ("(580_501, 580_700)", 0),
    ("== 113", 0),
    ("forty-four legs", 0),
    ("sixteen legs", 0),
    ("114 parity", 0),
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
io.open(LOG, "w", encoding="utf-8").write("\n".join(log))
print(f"DERIVE OK -> {DST} ({len(t)} chars); {len(log)} transform log rows")
print("\n".join(log[-12:]))
