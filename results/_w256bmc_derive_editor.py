# -*- coding: utf-8 -*-
# r1058 bm-c: derive results/_w256bmc_freeze_edits.py from the committed W255
# freeze-edits script (results/_w255bmc_freeze_edits.py, proven live-fire W255
# splice bm-c r1057 window: splice e166afc6c + engine self-burn 12/12 + finalize
# one-pass ledger 985,335 / K=558,920 five-key 6/6 by the r1057 continuation
# closeout fd48643c9) via COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage,
# 8th-gen pass ordering: P1 structural outputs BLANKET-IMMUNE; the W256
# extraction faces stay structurally identical to the W255 estate mandate --
# estate 69 rows W138..W206 full-span ONLY + kept W211..W238 (28) + dropped
# W239..W254 (16) + fresh W239..W255 (17) = 114 parity rows per the frozen
# W256 prereg sec.3 mandate -- only the count faces move 16->17 / 113->114 /
# 43->44 / 15->16).
# W256 facts (machine-read from the probe receipt, never transcribed):
# bands A 578_501..580_500 (1-HOP STAIRCASE-AFFECTS-A walk, FIFTH
# consecutive A-hop -- the naive continuation 578_301..580_300 is REFUSED at
# its own start: the registered W255 B band 578_301..578_500 sits INSIDE the
# naive A window = staircase CONTINUES to affect A, the W255 prereg sec.5
# item5 post-W255-REGISTERED pre-disclosure MATERIALIZED as projected; the
# walk hops past the W255 B tail 578_500 -> A first-clean 578_501..580_500,
# hops=1; A base == registered prior-wave B tail+1 (578_500+1) EXACT) /
# B 580_501..580_700 (1-HOP own-A RESERVATION CASCADE above own-A, SIXTH
# consecutive -- the naive continuation 578_501..578_700 is REFUSED at its
# own start: the naive window lands INSIDE the own-wave W256 A first-clean
# window 578_501..580_500; the walk hops past the own-A tail 580_500 -> B
# landing 580_501..580_700, hops=1; B base == own-A tail+1 (580_500+1) EXACT),
# upstream W255 = bm-c own chain, seat MSG-20261017-023x-bmc-w256-seat @
# origin fd48643c9 r1057 closeout, prereg 5996e2c93 derived bm-c r1058
# (authored 03:01 by the dead 02:5x window; freeze landed by it, absorb
# generation = prereg window == splice window r1058).
# Needle law this generation: ALL chunk/repp needles are machine-derived via
# age() = the exact blanket composition (P2 W256->W257, P3 255->256,
# P4 254->255) applied to the W255-script-era literals, which were verified
# count==1 against the live committed script by the r1058 pre-flight probe
# results/_w256bmc_needle_preflight.py (raw + blanket-simulated counts).
import io, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w255bmc_freeze_edits.py")
DST = os.path.join(REPO, "results", "_w256bmc_freeze_edits.py")
LOG = os.path.join(REPO, "results", "_w256bmc_derive_editor_log.txt")
PY = sys.executable

# S0: SRC worktree == committed HEAD blob (r609 origin-verbatim base law)
blob_wt = subprocess.run(["git", "hash-object", SRC], capture_output=True, text=True, cwd=REPO).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w255bmc_freeze_edits.py"], capture_output=True, text=True, cwd=REPO).stdout.strip()
assert blob_wt == blob_head and len(blob_wt) == 40, f"SRC blob drift: wt={blob_wt} head={blob_head}"
assert blob_wt == "6c6397d375d7f5a475b7579ef320c280d6d4d4f7", f"SRC blob face drift: {blob_wt}"

t = io.open(SRC, encoding="utf-8").read()
log = [f"S0 src blob verified {blob_wt[:16]} == HEAD twin (worktree clean face)"]

# age_prev(): the PRIOR generation's blanket composition (W255 editor) -- used
# ONLY to reconstruct the W255-script chunk faces from the W254-era literals
# (the needles the r1057 editor itself consumed).
def age_prev(s):
    s = s.replace("W255", "W256")
    s = s.replace("254", "255")
    s = s.replace("253", "254")
    return s

# age(): EXACT composition of MY blanket passes (P2 downstream, P3 self,
# P4 upstream) -- derives post-pass needles from W255-script-era literals
# WITHOUT hand-derivation (zero mental-derivation risk).
def age(s):
    s = s.replace("W256", "W257")
    s = s.replace("255", "256")
    s = s.replace("254", "255")
    return s

def rep(old, new, expect=None, tag=""):
    global t
    n = t.count(old)
    if expect is not None:
        assert n == expect, f"[{tag}] count {n} != {expect} for: {old[:70]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x {old[:48]!r}")

# mk255(): rebuild the W255-script chunk from the W254-era literal (asserts
# the prev subs exactly as the r1057 editor ran them).
def mk255(needle, repls, tag):
    s = needle
    for old, new, cnt in repls:
        n = s.count(old)
        assert n == cnt, f"[{tag}.{s.count(old)}] sub {old[:56]!r}: {n} != {cnt}"
        s = s.replace(old, new)
    return s

# mk(): build a chunk NEW text from its (post-blanket) needle via ordered
# count-asserted fact replacements -- W256 facts from the probe receipt.
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
rep("(251, 250, 249, 248, 247, 246, 245, 244, 243, 242)",
    "(252, 251, 250, 249, 248, 247, 246, 245, 244, 243)", 2, "P1-transitive-deps")
rep("range(209, 256)", "range(209, 257)", 2, "P1-liveness-range")
rep('def fmt(n):  # 576301 -> "576_301"', 'def fmt(n):  # 578501 -> "578_501"', 1, "P1-fmt-comment")

# ============ P2: downstream shift W256 -> W257 (incl. W256p_* receipt keys) ============
rep("W256", "W257", None, "P2-downstream")
assert "W256" not in t, "P2 leftover W256"

# ============ P3: self shift 255 -> 256 ============
n255 = t.count("255")
rep("255", "256", None, "P3-self")
log.append(f"P3 consumed {n255} '255' substrings")

# ============ P4: upstream shift 254 -> 255 ============
n254 = t.count("254")
rep("254", "255", None, "P4-upstream")
log.append(f"P4 consumed {n254} '254' substrings")

# ============ P5a: numeric/anchor/ordinal/window faces (post-blanket forms) ============
rep(age("983_135"), "985_335", 1, "P5a-ledger-int")
rep(age("556_720"), "558_920", 1, "P5a-k-int")
rep(age("983,135"), "985,335", 8, "P5a-ledger-prose")
rep(age("556,720"), "558,920", 8, "P5a-k-prose")
rep(age("bmc_ordinal=75"), "bmc_ordinal=76", 7, "P5a-ordinal75")
rep(age("SEVENTY-FIFTH"), "SEVENTY-SIXTH", 3, "P5a-seventyfifth")
rep(age("TWO HUNDRED AND FIFTY-FIFTH"), "TWO HUNDRED AND FIFTY-SIXTH", 3, "P5a-250th")
rep(age("forty-third consecutive"), "forty-fourth consecutive", 2, "P5a-finface")
rep(age("75th own wave"), "76th own wave", 3, "P5a-75th-ownwave")
rep(age("MSG-20261016-22xx-bmc-w255-seat"), "MSG-20261017-023x-bmc-w256-seat", 7, "P5a-seat-msg")
# NOTE: the probe-receipt DATE roll rep is deferred to POST-P5e (see the
# P5a-probe-receipt-date rep below) -- the pfcmt chunk needle embeds the
# blanket-aged basename + raw date face, so the date rep must run after all
# P5e chunk replacements (ordering heal disclosed, same heal #3).
rep(age("cb79242ed"), "fd48643c9", 2, "P5a-seat-origin")
rep(age("72d292ea3"), "5996e2c93", 1, "P5a-prereg-commit")
# r-window faces: upstream W255 chain = splice r1057 window (dead window
# estate, landed e166afc6c) + finalize r1057 (closeout 02:3x, ledger
# 985,335/K=558,920); W256 prereg derive window = r1058 (authored 03:01 by
# the dead 02:5x window); this freeze = r1058 continuation (absorb
# generation: prereg window == splice window).
rep(age("2026-10-17 02:0x bm-c r1057 freeze window"), "2026-10-17 03:2x bm-c r1058 freeze window", 1, "P5a-header-window")
rep(age("W254 finalize one-pass bm-c r1055 window closeout 21:3x"),
    "W255 finalize one-pass bm-c r1057 window closeout 02:3x", 1, "P5a-closeout-window")
rep(age("r1055 splice window"), "r1057 splice window", 3, "P5a-splice-window")
rep(age("r1055"), "r1057", 19, "P5a-splice-window-rest")
rep(age("r1056"), "r1058", 7, "P5a-prereg-window")
rep(age("authored 01:14"), "authored 03:01", 2, "P5a-authored-time")
# aging-face needle heals (same-window disclosed, r1045/r1047/r1050/r1055/r1057 precedent family):
rep(age("transitive window W242..W251 checked"), "transitive window W243..W252 checked", 1, "P5a-aging-deps-cmt")
rep(age("engine_owner==bm-c rows 74 + candidate"), "engine_owner==bm-c rows 75 + candidate", 1, "P5a-aging-rows-heal")

# ============ P5b: extraction count faces (frozen W256 prereg sec.3 mandate) ============
# estate 69 (W138..W206) + kept W211..W238 (28) UNCHANGED; dropped W239..W254 (16);
# fresh W239..W255 (17); total parity 114 rows; legs segment W211..W254 (44).
rep(age("# block's own W239..W253 legs (15 rows) do NOT enter the estate path;"),
    "# block's own W239..W254 legs (16 rows) do NOT enter the estate path;", 1, "P5b-hdr-ownlegs")
rep(age("# after extraction, fresh W239..W254 legs (16 rows) are added,"),
    "# after extraction, fresh W239..W255 legs (17 rows) are added,", 1, "P5b-hdr-freshlegs")
rep(age("# parity = 113 rows (W138..W206 + W211..W254). Zero assumption zero risk."),
    "# parity = 114 rows (W138..W206 + W211..W255). Zero assumption zero risk.", 1, "P5b-hdr-parity-count")
rep(age("# block's own W239..W253 legs (15) are EXCLUDED from the estate path per the"),
    "# block's own W239..W254 legs (16) are EXCLUDED from the estate path per the", 1, "P5b-ext-excl")
rep(age("# prereg mandate; the W255 block appends fresh W239..W254 legs (16,"),
    "# prereg mandate; the W256 block appends fresh W239..W255 legs (17,", 1, "P5b-ext-fresh")
rep(age("# machine-derived from the LIVE pf registry at freeze time) -> 113 parity"),
    "# machine-derived from the LIVE pf registry at freeze time) -> 114 parity", 1, "P5b-ext-parcount")

_PARFULL_W255 = '''assert par_full.count("assert pf.N1_BANDS[") == 112, \\
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 112 (69 estate + W211..W253 legs 43)"'''
_LEGS_W255 = '''assert legs_sec.count("assert pf.N1_BANDS[") == 43 \\
    and [int(w) for w in _legs_ws] == list(range(211, 254)), \\
    f"legs segment not W211..W253 forty-three legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}"'''
_DROP_W255 = '''assert legs_dropped.count("assert pf.N1_BANDS[") == 15 \\
    and [int(w) for w in _dropped_ws] == list(range(239, 254)), \\
    f"dropped segment not W239..W253 fifteen legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}"'''
rep(age(_PARFULL_W255),
    mk(age(_PARFULL_W255), [("== 112", "== 113", 1),
                            ("!= 112 (69 estate + W211..W253 legs 43)", "!= 113 (69 estate + W211..W254 legs 44)", 1)], "P5b-parfull"),
    1, "P5b-parfull")
rep(age(_LEGS_W255),
    mk(age(_LEGS_W255), [("== 43", "== 44", 1),
                          ("legs segment not W211..W253 forty-three legs", "legs segment not W211..W254 forty-four legs", 1)], "P5b-legs-assert"),
    1, "P5b-legs-assert")
rep(age(_DROP_W255),
    mk(age(_DROP_W255), [("== 15", "== 16", 1),
                          ("dropped segment not W239..W253 fifteen legs", "dropped segment not W239..W254 sixteen legs", 1)], "P5b-dropped-assert"),
    1, "P5b-dropped-assert")
rep(age("# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W254\n# block's own W239..W253 legs (15) are excluded from the estate path"),
    "# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W255\n# block's own W239..W254 legs (16) are excluded from the estate path", 1, "P5b-split-cmt")
rep(age('"fresh_legs_row_asserts": 16,'), '"fresh_legs_row_asserts": 17,', 1, "P5b-rcpt-fresh16")
rep(age('+ legs_kept.count("assert pf.N1_BANDS[") + 16,'), '+ legs_kept.count("assert pf.N1_BANDS[") + 17,', 1, "P5b-rcpt-total16")
rep(age('"    #     physical bytes; the W254 block\'s own W239..W253 legs (15) are",'),
    '"    #     physical bytes; the W255 block\'s own W239..W254 legs (16) are",', 1, "P5b-hdr-ownlegs-mat")
rep(age('"    #     W239..W254 legs (16) added, machine-derived from the live pf",'),
    '"    #     W239..W255 legs (17) added, machine-derived from the live pf",', 1, "P5b-hdr-freshlegs-mat")
rep(age('"    #     registry at freeze time -> 113 parity rows (W138..W206+W211..W254).",'),
    '"    #     registry at freeze time -> 114 parity rows (W138..W206+W211..W255).",', 1, "P5b-hdr-parcount-mat")

# receipt note (single big face: counts + generation stamp)
# (d) face ranges: prev P4 blanket already aged the raw 211,253/239,253 forms
# to 211,254/239,254 inside the W255 note (blanket-duplication class,
# disclosed needle heal #1: literal re-transcribed from the aged face).
_RCPTNOTE_W255 = '''                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W238 legs (28) extracted verbatim per the frozen W255 prereg sec.3 mandate; the W254 block's own W239..W253 legs (15) EXCLUDED from the estate path per the same mandate; fresh W239..W254 legs (16) machine-derived from the live pf registry -> W255 block = 113 rows (W138..W206 + W211..W254); disclosed: (a) inherited W213 leg error-string face preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-255 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 7th-gen prevention this window: the W255 derive editor kept the P1-blanket-immune pass ordering and the extraction-restructure legs/kept/dropped wave-identity asserts fixed post-blanket (list(range(211,254))/list(range(211,239))/list(range(239,254)) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},'''
rep(age(_RCPTNOTE_W255),
    mk(age(_RCPTNOTE_W255), [
        ("own W239..W253 legs (15) EXCLUDED", "own W239..W254 legs (16) EXCLUDED", 1),
        ("fresh W239..W255 legs (16) machine-derived", "fresh W239..W255 legs (17) machine-derived", 1),
        ("W256 block = 113 rows", "W256 block = 114 rows", 1),
        ("E63 7th-gen", "E63 8th-gen", 1),
    ], "P5b-rcpt-note"),
    1, "P5b-rcpt-note")

# ============ P5c: band literals (probe ADMIT receipt bands) ============
rep(age('assert (a_lo, a_hi) == (576_301, 578_300) and (b_lo, b_hi) == (578_301, 578_500), \\'),
    'assert (a_lo, a_hi) == (578_501, 580_500) and (b_lo, b_hi) == (580_501, 580_700), \\', 1, "P5c-band-drift")

# ============ P5d: ordinal/leg0/deps faces ============
rep(age('assert len(owner_rows_live) == 244 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 74, \\'),
    'assert len(owner_rows_live) == 245 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 75, \\', 1, "P5d-ord-gate")
# needle narrowed to the pre-registration numeric face: the trailing "76th own
# wave" inside this line was ALREADY rewritten by the P5a-75th-ownwave rep
# (order-sensitive face, W255 editor canon -- its P5d needle was likewise the
# post-P5a form); disclosed needle heal, evidence = pre-flight n=1 raw face.
rep(age("(expect 244/129/74 PRE-splice post-W254 registration"),
    "(expect 245/129/75 PRE-splice post-W255 registration", 1, "P5d-ord-err")
# needle narrowed likewise: the trailing "bmc_ordinal=76" on this line was
# already rewritten to 76 by the P5a-ordinal75 rep (one of its 7 faces).
rep(age('# receipt leg0 face owner_rows=244 / bmc_rows=74 /'),
    '# receipt leg0 face owner_rows=245 / bmc_rows=75 /', 1, "P5d-leg0-prose")
rep(age("-> owner rows 244 + candidate = 245th EXACT; bm-c rows 74 +"),
    "-> owner rows 245 + candidate = 246th EXACT; bm-c rows 75 +", 1, "P5d-ord-owner-prose")
rep(age("# candidate = 75th EXACT -- bm-c own-seat continuity face (bm-c published the"),
    "# candidate = 76th EXACT -- bm-c own-seat continuity face (bm-c published the", 1, "P5d-ord-bmc-prose")
rep(age("freeze-time live face owner rows 244 + candidate = 245th EXACT"),
    "freeze-time live face owner rows 245 + candidate = 246th EXACT", 1, "P5d-rcpt-244th")
rep(age("freeze-time live derive bmc rows 74 + candidate 75th EXACT per r587/r359"),
    "freeze-time live derive bmc rows 75 + candidate 76th EXACT per r587/r359", 1, "P5d-bundle-75th")
rep(age("post-W254 registration: bm-c rows 74 + candidate = 75th owned"),
    "post-W255 registration: bm-c rows 75 + candidate = 76th owned", 1, "P5d-rcpt-75th-owned")
rep(age('"probe_receipt_bmc_ordinal_face": 75,'), '"probe_receipt_bmc_ordinal_face": 76,', 1, "P5d-rcpt-ordface")
rep(age('f"W255+W250..W241 finalize products present "'), 'f"W256+W251..W242 finalize products present "', 1, "P5d-print-deps")

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
_HDR_W255 = mk255(age_prev(_HDR_W254), [
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
chunk(age(_HDR_W255),
      mk(age(_HDR_W255), [
          ("FIFTH consecutive\n# above-own-A", "SIXTH consecutive\n# above-own-A", 1),
          ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 1),
          ("576_301..578_300", "578_501..580_500", 2),
          ("578_301..578_500", "580_501..580_700", 1),
          ("576_101..578_100", "578_301..580_300", 1),
          ("576_101..576_300", "578_301..578_500", 1),
          ("576_301..576_500", "578_501..578_700", 1),
          ("576_300", "578_500", 2),
          ("578_300", "580_500", 2),
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
_BANDFACTS_W255 = mk255(age_prev(_BANDFACTS_W254), [
    ("FOURTH consecutive above-own-A landing", "FIFTH consecutive above-own-A landing", 1),
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2),
], "P5e-bandfacts-prev")
chunk(age(_BANDFACTS_W255),
      mk(age(_BANDFACTS_W255), [
          ("FIFTH consecutive above-own-A landing", "SIXTH consecutive above-own-A landing", 1),
          ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 2),
      ], "P5e-bandfacts"), "P5e-bandfacts")

_A_BASE_W254 = '''assert w253_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1 EXACT -- the 1-hop walk past the registered W253 B band; third consecutive A-hop of the staircase era; A_staircase_hop_past_W253_B=true)"'''
_A_BASE_W255 = mk255(age_prev(_A_BASE_W254), [("third consecutive A-hop", "fourth consecutive A-hop", 1)], "P5e-a-base-prev")
rep(age(_A_BASE_W255),
    mk(age(_A_BASE_W255), [("fourth consecutive A-hop", "fifth consecutive A-hop", 1)], "P5e-a-base"),
    1, "P5e-a-base")
_A_FLOOR_W254 = '''assert a_lo >= w253_b_tail + 1, "A staircase landing floor relation (A base >= registered prior-wave B tail+1; the fourteen-wave seed-gap face ENDED at W252 -- third consecutive A-hop of the staircase era, A base == prior-B tail+1 EXACT this window per the prereg floor-relation mandate)"'''
_A_FLOOR_W255 = mk255(age_prev(_A_FLOOR_W254), [("third consecutive A-hop", "fourth consecutive A-hop", 1)], "P5e-a-floor-prev")
rep(age(_A_FLOOR_W255),
    mk(age(_A_FLOOR_W255), [("fourth consecutive A-hop", "fifth consecutive A-hop", 1)], "P5e-a-floor"),
    1, "P5e-a-floor")
_B_BASE_W254 = '''assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation cascade lands ABOVE own-A -- fourth consecutive above-own-A; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"'''
_B_BASE_W255 = mk255(age_prev(_B_BASE_W254), [("fourth consecutive above-own-A", "fifth consecutive above-own-A", 1)], "P5e-b-base-prev")
rep(age(_B_BASE_W255),
    mk(age(_B_BASE_W255), [("fifth consecutive above-own-A", "sixth consecutive above-own-A", 1)], "P5e-b-base"),
    1, "P5e-b-base")

# relation_asserts gate (W252_W254 rsv-key fix lineage -- the P4 blanket
# produces the W252_W253_W255 hybrid face; the probe receipt leg1 keys are
# W253_W254_W255)
_RA_GATE_W254 = '''ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") is False and ra.get("A_staircase_hop_past_W253_B") \\
    and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_clean_at_naive_start") is False and ra.get("B_base_above_W253_tail") \\
    and ra.get("AB_mutual_exclusion") and ra.get("B_hop_lands_inside_A") is False \\
    and ra.get("B_lands_above_own_A") and ra.get("W251_W252_W253_bands_respected_A") and ra.get("W251_W252_W253_bands_respected_B"), \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"'''
_RA_GATE_W255 = mk255(age_prev(_RA_GATE_W254), [
    ("W251_W252_W254_bands_respected_A", "W252_W253_W254_bands_respected_A", 1),
    ("W251_W252_W254_bands_respected_B", "W252_W253_W254_bands_respected_B", 1),
], "P5e-ra-gate-prev")
rep(age(_RA_GATE_W255),
    mk(age(_RA_GATE_W255), [
        ("W252_W253_W255_bands_respected_A", "W253_W254_W255_bands_respected_A", 1),
        ("W252_W253_W255_bands_respected_B", "W253_W254_W255_bands_respected_B", 1),
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
_PFCMT_W255 = mk255(age_prev(_PFCMT_W254), [
    ("FOURTH consecutive above-own-A;", "FIFTH consecutive above-own-A;", 1),
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 1),
    ("hops=1 -- SECOND", "hops=1 -- THIRD", 1),
    # ENDED-at face: the prev P4 blanket already aged the raw "ENDED at W253;"
    # to "ENDED at W254;" inside the needle -- mechanical aging face,
    # zero sub needed (blanket-duplication class, r1057 precedent)
], "P5e-pfcmt-prev")
chunk(age(_PFCMT_W255),
      mk(age(_PFCMT_W255), [
          ("FIFTH consecutive above-own-A;", "SIXTH consecutive above-own-A;", 1),
          ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 1),
          ("hops=1 -- THIRD", "hops=1 -- FOURTH", 1),
          # ENDED-at face: MY P4 blanket already aged "ENDED at W254;" to
          # "ENDED at W255;" inside the needle -- mechanical aging face,
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
_PRE_W255 = mk255(age_prev(_PRE_W254), [
    ("FOURTH consecutive above-own-A", "FIFTH consecutive above-own-A", 1),
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2),
], "P5e-pre-prev")
chunk(age(_PRE_W255),
      mk(age(_PRE_W255), [
          ("FIFTH consecutive above-own-A", "SIXTH consecutive above-own-A", 1),
          ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 2),
      ], "P5e-pre"), "P5e-pre")

# MEM_I comment lines (A + B faces)
_MEM_A_W254 = ''' f\'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W254 A: {fmt(a_lo)}..{fmt(a_hi)} (1-HOP STAIRCASE-AFFECTS-A walk THIRD consecutive A-hop; naive {fmt(w253_a_tail + 1)}..{fmt(w253_a_tail + 2_000)} REFUSED at start -- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; registered W253 B band inside the naive A window; third consecutive A-hop of the staircase era -- seed-gap face ENDED at W252; A base == registered prior-wave B tail+1)\','''
_MEM_A_W255 = mk255(age_prev(_MEM_A_W254), [
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 1),
    ("third consecutive A-hop", "fourth consecutive A-hop", 1),
], "P5e-mem-a-prev")
rep(age(_MEM_A_W255),
    mk(age(_MEM_A_W255), [
        ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 1),
        ("fourth consecutive A-hop", "fifth consecutive A-hop", 1),
    ], "P5e-mem-a"),
    1, "P5e-mem-a")
_MEM_B_W254 = ''' f\'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W254 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION CASCADE above own-A; naive {fmt(w253_b_tail + 1)}..{fmt(w253_b_tail + 200)} REFUSED at start -- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; naive window lands inside the own-wave A first-clean window -> own-A reservation cascade; B lands ABOVE own-A at tail+1 EXACT -- fourth consecutive above-own-A; B base == own-A tail+1)\','''
_MEM_B_W255 = mk255(age_prev(_MEM_B_W254), [("fourth consecutive above-own-A", "fifth consecutive above-own-A", 1)], "P5e-mem-b-prev")
rep(age(_MEM_B_W255),
    mk(age(_MEM_B_W255), [("fifth consecutive above-own-A", "sixth consecutive above-own-A", 1)], "P5e-mem-b"),
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
_TAILCMT_W255 = mk255(age_prev(_TAILCMT_W254), [
    ("FOURTH consecutive", "FIFTH consecutive", 1),
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2),
], "P5e-tailcmt-prev")
chunk(age(_TAILCMT_W255),
      mk(age(_TAILCMT_W255), [
          ("FIFTH consecutive", "SIXTH consecutive", 1),
          ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 2),
      ], "P5e-tailcmt"), "P5e-tailcmt")

# tail assert block (A face message)
_TAIL_AMSG_W254 = '''            "W254 A staircase-affects-A walk THIRD consecutive A-hop: the naive "',
'            "continuation is REFUSED at its own start (the registered W253 B band sits INSIDE "',
'            "the naive A window -- staircase re-emergence continues; hops=1, A_hop_chain verbatim in the probe receipt, "',
'            "A_clean_at_naive_start=false, A_staircase_hop_past_W253_B=true; the walk hops past "',
'            "the W253 B tail -> A first-clean -- THIRD consecutive A-hop of the staircase era, "',
'            "the fourteen-wave seed-gap face ENDED at W252; A base == registered prior-wave B "',
'            "tail+1 machine-checkable, floor relation honored)"'''
_TAIL_AMSG_W255 = mk255(age_prev(_TAIL_AMSG_W254), [("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2)], "P5e-tail-amsg-prev")
rep(age(_TAIL_AMSG_W255),
    mk(age(_TAIL_AMSG_W255), [("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 2)], "P5e-tail-amsg"),
    1, "P5e-tail-amsg")

# tail assert block (B face messages; identity count-asserts per W255 canon)
rep(age(age_prev('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')),
    age(age_prev('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "')), 1, "P5e-tail-bassert2")
rep(age(age_prev('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"')),
    age(age_prev('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"')), 1, "P5e-tail-bclean")
rep(age(mk255(age_prev('            "W254 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- fourth consecutive above-own-A; zero overlap)"'),
              [("fourth consecutive above-own-A", "fifth consecutive above-own-A", 1)], "P5e-tail-excl-prev")),
    mk(age(mk255(age_prev('            "W254 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- fourth consecutive above-own-A; zero overlap)"'),
                 [("fourth consecutive above-own-A", "fifth consecutive above-own-A", 1)], "P5e-tail-excl-prev")),
       [("fifth consecutive above-own-A", "sixth consecutive above-own-A", 1)], "P5e-tail-excl"),
    1, "P5e-tail-excl")

# pr print A/B lines
_PRCHUNK_W254 = ''' '          "A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, "',
 '          "registered W253 B band inside the naive A window, THIRD consecutive A-hop of the staircase era, "',
 '          "the fourteen-wave seed-gap face ENDED at W252) "',
 '          "+ B=1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, "',
 '          "B_hop_chain verbatim, naive window lands inside the own-wave A window -> own-A reservation cascade, "',
 '          "B base == own-A tail+1 EXACT, B_lands_above_own_A=true, "',
 '          "FOURTH consecutive above-own-A landing), chain-order splice from the "'''
_PRCHUNK_W255 = mk255(age_prev(_PRCHUNK_W254), [
    ("FOURTH consecutive above-own-A landing", "FIFTH consecutive above-own-A landing", 1),
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 1),
], "P5e-pr-prev")
chunk(age(_PRCHUNK_W255),
      mk(age(_PRCHUNK_W255), [
          ("FIFTH consecutive above-own-A landing", "SIXTH consecutive above-own-A landing", 1),
          ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 1),
      ], "P5e-pr"), "P5e-pr")

# receipt band_semantics A + B values
_SEM_A_W254 = '''"A": "1-HOP STAIRCASE-AFFECTS-A walk THIRD consecutive A-hop (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 573_901..575_900 refused at start -- the registered W253 B band 573_901..574_100 sits INSIDE the naive A window (staircase re-emergence continues; the W253 prereg sec.5 item5 A-CLEAN-at-naive projection superseded live r587, divergence disclosed); the walk hops past the W253 B tail 574_100 -> A first-clean 574_101..576_100 -- THIRD consecutive A-hop of the staircase era, the fourteen-wave seed-gap face ENDED at W252; A_clean_at_naive_start=false; A_staircase_hop_past_W253_B=true; A base == registered prior-wave B tail+1 (574_100+1) EXACT)"'''
_SEM_A_W255 = mk255(age_prev(_SEM_A_W254), [
    ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2),
    ("573_901..575_900 refused", "576_101..578_100 refused", 1),
    ("573_901..574_100 sits", "576_101..576_300 sits", 1),
    ("B tail 574_100 -> A first-clean 574_101..576_100", "B tail 576_300 -> A first-clean 576_301..578_300", 1),
    ("(574_100+1) EXACT)", "(576_300+1) EXACT)", 1),
], "P5e-rcpt-semantics-A-prev")
rep(age(_SEM_A_W255),
    mk(age(_SEM_A_W255), [
        ("FOURTH consecutive A-hop", "FIFTH consecutive A-hop", 2),
        ("576_101..578_100 refused", "578_301..580_300 refused", 1),
        ("576_101..576_300 sits", "578_301..578_500 sits", 1),
        ("B tail 576_300 -> A first-clean 576_301..578_300", "B tail 578_500 -> A first-clean 578_501..580_500", 1),
        ("(576_300+1) EXACT)", "(578_500+1) EXACT)", 1),
    ], "P5e-rcpt-semantics-A"),
    1, "P5e-rcpt-semantics-A")
_SEM_B_W254 = '''"B": "1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the naive continuation 574_101..574_300 is refused at start -- the naive window lands INSIDE the own-wave W254 A first-clean window 574_101..576_100 (own-A reservation cascade standard leg; the W253 prereg sec.5 item5 + probe leg4 projected landing superseded live -- the A face itself moved, divergence disclosed per r587); the walk hops past the own-A tail 576_100 -> B landing 576_101..576_300; B lands ABOVE own-A -- FOURTH consecutive above-own-A landing; B_lands_above_own_A=true; B_hop_lands_inside_A=false; B base == own-A tail+1 (576_100+1) EXACT)"'''
_SEM_B_W255 = mk255(age_prev(_SEM_B_W254), [
    ("FOURTH consecutive above-own-A landing", "FIFTH consecutive above-own-A landing", 1),
    ("574_101..574_300 is refused", "576_301..576_500 is refused", 1),
    ("A first-clean window 574_101..576_100 (own-A", "A first-clean window 576_301..578_300 (own-A", 1),
    ("own-A tail 576_100 -> B landing 576_101..576_300;", "own-A tail 578_300 -> B landing 578_301..578_500;", 1),
    ("(576_100+1) EXACT)", "(578_300+1) EXACT)", 1),
], "P5e-rcpt-semantics-B-prev")
rep(age(_SEM_B_W255),
    mk(age(_SEM_B_W255), [
        ("FIFTH consecutive above-own-A landing", "SIXTH consecutive above-own-A landing", 1),
        ("576_301..576_500 is refused", "578_501..578_700 is refused", 1),
        ("A first-clean window 576_301..578_300 (own-A", "A first-clean window 578_501..580_500 (own-A", 1),
        ("own-A tail 578_300 -> B landing 578_301..578_500;", "own-A tail 580_500 -> B landing 580_501..580_700;", 1),
        ("(578_300+1) EXACT)", "(580_500+1) EXACT)", 1),
    ], "P5e-rcpt-semantics-B"),
    1, "P5e-rcpt-semantics-B")

# downstream W257+ projection face (probe leg4 verbatim numbers)
# disclosed needle heal #2 (transcription class): the prev editor's literal
# reads "-- pre-W254-universe face" (NOT pre-W255); age_prev P3 ages it to the
# W255-script "pre-W255-universe" face, MY P3 ages that to the post-blanket
# "pre-W256-universe" form -- verified against the live committed script.
_DOWNSTREAM_W254 = '''W255 = next free number, next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W255 freezer MUST re-derive live on the post-W254 universe + reserve the own-wave A window when deriving B per the W254 seat leg4 mandate, never transcribe r587 -- W255p face per this window's probe leg4 (pre-W254 universe): A naive 576101..578100 CLEAN (hops=0, zero live refusers -- pre-W254-universe face) / B naive 576301..576500 hops=0 CLEAN at naive, first-clean 576301..576500 BUT lands INSIDE the W255 projection A window (W255p_B_lands_inside_W255p_A_naive=true staircase face continuation since W252: A hops over prior B, B lands above own-A; on the post-W254 universe the W255 naive A window start 576_101 lands INSIDE the registered W254 B band 576_101..576_300 -- staircase affects A inherited, the A first-clean and the B own-A reservation cascade landing both move up, live re-derive governs); re-read the live trace at W255 derive time, do NOT assume the staircase A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities'''
_DOWNSTREAM_W255 = mk255(age_prev(_DOWNSTREAM_W254), [
    ("A naive 576101..578100 CLEAN", "A naive 578301..580300 CLEAN", 1),
    ("B naive 576301..576500 hops=0 CLEAN at naive, first-clean 576301..576500 BUT", "B naive 578501..578700 hops=0 CLEAN at naive, first-clean 578501..578700 BUT", 1),
    ("naive A window start 576_101 lands INSIDE the registered W255 B band 576_101..576_300", "naive A window start 578_301 lands INSIDE the registered W255 B band 578_301..578_500", 1),
    ("staircase face continuation since W252", "staircase face continuation since W251", 1),
], "P5e-rcpt-downstream-prev")
rep(age(_DOWNSTREAM_W255),
    mk(age(_DOWNSTREAM_W255), [
        ("A naive 578301..580300 CLEAN", "A naive 580501..582500 CLEAN", 1),
        ("B naive 578501..578700 hops=0 CLEAN at naive, first-clean 578501..578700 BUT", "B naive 580701..580900 hops=0 CLEAN at naive, first-clean 580701..580900 BUT", 1),
        ("naive A window start 578_301 lands INSIDE the registered W256 B band 578_301..578_500", "naive A window start 580_501 lands INSIDE the registered W256 B band 580_501..580_700", 1),
    ], "P5e-rcpt-downstream"),
    1, "P5e-rcpt-downstream")

# ============ P5f: probe-receipt date roll (post-P5e ordering) ============
# disclosed needle heal #3 (generation-structural): this generation the probe
# receipt DATE rolls (20261016 -> 20261017) -- the prev generation inherited
# its date so no such rep existed in the W255 editor; the blanket P3 ages the
# basename only, leaving the stale date. MUST run AFTER the P5e chunks (the
# pfcmt chunk needle embeds the pre-replacement date face); verified 10x.
rep(age("_w255bmc_20261016_probe_receipt.json"), "_w256bmc_20261017_probe_receipt.json", 10, "P5a-probe-receipt-date")

# ============ structural output gates ============
for needle, want in [
    ("# --- W256 materializer face", 2),
    ("# --- W255 materializer face", 1),
    ('"+ W256 materializer face', 2),
    ("range(16, 256)", 2),
    ("range(17, 256)", 3),
    ("range(239, 256)", 2),
    ("list(range(211, 255)),", 1),
    ("list(range(211, 239))", 1),
    ("list(range(239, 255)),", 1),
    ("range(209, 257)", 2),
    ("if w < 256)", 5),
    ("if w < 255)", 1),
    ("_w256bmc_20261017_probe_receipt.json", 10),
    ("_w256bmc_freeze_receipt.json", 1),
    ("MSG-20261017-023x-bmc-w256-seat", 7),
    ("fd48643c9", 2),
    ("985_335", 1),
    ("558_920", 1),
    ("(578_501, 580_500)", 1),
    ("(580_501, 580_700)", 1),
    ("W253_W254_W255_bands_respected_A", 1),
    ("W253_W254_W255_bands_respected_B", 1),
    ("B_base_above_W255_tail", 2),
    ("A_staircase_hop_past_W255_B", None),
    ("W257p_A_naive", 5),
    ("W257p_B_first_clean", 2),
    ("arith_a256", 6),
    ("arith_b256", 6),
    ('"PERPETUAL-N1-W256-SHARD-0"', 1),
    ("n1_w256_results.json", 2),
    ("n1_w256", 4),
    ("n1w256", 2),
    ("PERPETUAL-N1-W256", 7),
    ("_w256bmc", 11),
    ("w244_a", 12),
    ("SEVENTY-SIXTH", 3),
    ("TWO HUNDRED AND FIFTY-SIXTH", 3),
    ("forty-fourth consecutive", 2),
    ("bmc_ordinal=76", 7),
    ("76th own wave", 3),
    ("r1057 splice window", 3),
    ("r1057", 23),
    ("r1058", 8),
    ("r1058 freeze window", 1),
    ("estate 69", 1),
    ("= 114 rows", 2),
    ("114 parity", 2),
    ("hops=1", None),
    ("1-HOP", None),
    ("FIFTH consecutive A-hop", None),
    ("SIXTH consecutive above-own-A", None),
    # anti-gates: stale faces must be zero
    ("r1055", 0),
    ("r1056", 0),
    ("cb79242ed", 0),
    ("72d292ea3", 0),
    ("983,135", 0),
    ("556,720", 0),
    ("983_135", 0),
    ("556_720", 0),
    ("SEVENTY-FIFTH", 0),
    ("TWO HUNDRED AND FIFTY-FIFTH", 0),
    ("forty-third consecutive", 0),
    ("MSG-20261016-22xx", 0),
    ("authored 01:14", 0),
    ("bmc_ordinal=75", 0),
    ("75th own wave", 0),
    ("245th", 0),
    ("244/129/74", 0),
    ("FIFTH consecutive above-own-A", 0),
    ("FIRST A-hop", 0),
    ("seed-gap face ENDS", 0),
    ("576_101..578_100", 0),
    ("576_101..576_300", 0),
    ("576_301..576_500", 0),
    ("576_301..578_300", 0),
    ("576_300", 0),
    ("578_300", 0),
    ("576_101", 0),
    ("576_301", 0),
    ("~575_901..575_900", 0),
    ("(576_301, 578_300)", 0),
    ("(578_301, 578_500)", 0),
    ("== 112", 0),
    ("forty-three legs", 0),
    ("fifteen legs", 0),
    ("113 parity", 0),
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
