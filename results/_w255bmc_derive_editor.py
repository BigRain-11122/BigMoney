# -*- coding: utf-8 -*-
# r1057 bm-c: derive results/_w255bmc_freeze_edits.py from the committed W254
# freeze-edits script (results/_w254bmc_freeze_edits.py, proven live-fire W254
# splice bm-c r1055 window: splice 3eb691575 + engine self-burn 12/12 + finalize
# one-pass ledger 983,135 / K=556,720 five-key ALL PASS by the r1055
# continuation closeout cb79242ed) via COUNT-ASSERTED ORDERED TRANSFORM (E63
# lineage, 7th-gen pass ordering: P1 structural outputs BLANKET-IMMUNE; the
# W255 extraction faces stay structurally identical to the W254 estate
# mandate -- estate 69 rows W138..W206 full-span ONLY + kept W211..W238 (28)
# + dropped W239..W253 (15) + fresh W239..W254 (16) = 113 parity rows per the
# frozen W255 prereg sec.3 mandate -- only the count faces move 15->16 /
# 112->113 / 42->43 / 14->15).
# W255 facts (machine-read from the probe receipt, never transcribed):
# bands A 576_301..578_300 (1-HOP STAIRCASE-AFFECTS-A walk, FOURTH
# consecutive A-hop -- the naive continuation 576_101..578_100 is REFUSED at
# its own start: the registered W254 B band 576_101..576_300 sits INSIDE the
# naive A window = staircase CONTINUES to affect A; the walk hops past the
# W254 B tail 576_300 -> A first-clean 576_301..578_300, hops=1; A base ==
# registered prior-wave B tail+1 (576_300+1) EXACT) / B 578_301..578_500
# (1-HOP own-A RESERVATION CASCADE above own-A, FIFTH consecutive -- the
# naive continuation 576_301..576_500 is REFUSED at its own start: the naive
# window lands INSIDE the own-wave W255 A first-clean window
# 576_301..578_300; the walk hops past the own-A tail 578_300 -> B landing
# 578_301..578_500, hops=1; B base == own-A tail+1 (578_300+1) EXACT),
# upstream W254 = bm-c own chain, seat MSG-20261016-22xx-bmc-w255-seat @
# origin cb79242ed r1055 closeout, prereg 72d292ea3 derived bm-c r1056
# (authored 01:14).
# Needle law this generation: ALL chunk/repp needles are machine-derived via
# age() = the exact blanket composition (P2 W255->W256, P3 254->255,
# P4 253->254) applied to the W254-script-era literals, which were verified
# count==1 against the live committed script by the r1057 pre-flight probes
# (results/_r1057bmc_needle_preflight.py + _r1057bmc_needle_preflight2.py,
# 82+20 faces ALL PASS; MEM trailing-space face healed from live bytes).
import io, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w254bmc_freeze_edits.py")
DST = os.path.join(REPO, "results", "_w255bmc_freeze_edits.py")
LOG = os.path.join(REPO, "results", "_w255bmc_derive_editor_log.txt")
PY = sys.executable

# S0: SRC worktree == committed HEAD blob (r609 origin-verbatim base law)
blob_wt = subprocess.run(["git", "hash-object", SRC], capture_output=True, text=True, cwd=REPO).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w254bmc_freeze_edits.py"], capture_output=True, text=True, cwd=REPO).stdout.strip()
assert blob_wt == blob_head and len(blob_wt) == 40, f"SRC blob drift: wt={blob_wt} head={blob_head}"

t = io.open(SRC, encoding="utf-8").read()
log = [f"S0 src blob verified {blob_wt[:16]} == HEAD twin (worktree clean face)"]

# age(): EXACT composition of the blanket passes (P2 downstream, P3 self,
# P4 upstream) -- used to derive post-pass needles from W254-script-era
# literals WITHOUT hand-derivation (zero mental-derivation risk).
def age(s):
    s = s.replace("W255", "W256")
    s = s.replace("254", "255")
    s = s.replace("253", "254")
    return s

def rep(old, new, expect=None, tag=""):
    global t
    n = t.count(old)
    if expect is not None:
        assert n == expect, f"[{tag}] count {n} != {expect} for: {old[:70]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x {old[:48]!r}")

# mk(): build a chunk NEW text from its (post-blanket) needle via ordered
# count-asserted fact replacements -- W255 facts from the probe receipt.
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
rep("(250, 249, 248, 247, 246, 245, 244, 243, 242, 241)",
    "(251, 250, 249, 248, 247, 246, 245, 244, 243, 242)", 2, "P1-transitive-deps")
rep("range(209, 255)", "range(209, 256)", 2, "P1-liveness-range")
rep('def fmt(n):  # 574101 -> "574_101"', 'def fmt(n):  # 576301 -> "576_301"', 1, "P1-fmt-comment")

# ============ P2: downstream shift W255 -> W256 (incl. W255p_* receipt keys) ============
rep("W255", "W256", None, "P2-downstream")
assert "W255" not in t, "P2 leftover W255"

# ============ P3: self shift 254 -> 255 ============
n254 = t.count("254")
rep("254", "255", None, "P3-self")
log.append(f"P3 consumed {n254} '254' substrings")

# ============ P4: upstream shift 253 -> 254 ============
n253 = t.count("253")
rep("253", "254", None, "P4-upstream")
log.append(f"P4 consumed {n253} '253' substrings")

# ============ P5a: numeric/anchor/ordinal/window faces (post-blanket forms) ============
rep(age("980_935"), "983_135", 1, "P5a-ledger-int")
rep(age("554_520"), "556_720", 1, "P5a-k-int")
rep(age("980,935"), "983,135", 8, "P5a-ledger-prose")
rep(age("554,520"), "556,720", 8, "P5a-k-prose")
rep(age("bmc_ordinal=74"), "bmc_ordinal=75", 7, "P5a-ordinal74")
rep(age("SEVENTY-FOURTH"), "SEVENTY-FIFTH", 3, "P5a-seventyfourth")
rep(age("TWO HUNDRED AND FIFTY-FOURTH"), "TWO HUNDRED AND FIFTY-FIFTH", 3, "P5a-250th")
rep(age("forty-second consecutive"), "forty-third consecutive", 2, "P5a-finface")
rep(age("74th own wave"), "75th own wave", 3, "P5a-74th-ownwave")
rep(age("MSG-20261016-14xx-bmc-w254-seat"), "MSG-20261016-22xx-bmc-w255-seat", 7, "P5a-seat-msg")
rep(age("fa70f3765"), "cb79242ed", 2, "P5a-seat-origin")
rep(age("e2c4b543e"), "72d292ea3", 1, "P5a-prereg-commit")
# r-window faces: upstream W254 chain = splice r1055 window (dead window B
# estate, landed 3eb691575) + finalize r1055 (closeout 21:3x, ledger
# 983,135/K=556,720); W255 prereg derive window = r1056 (authored 01:14 by
# the dead 00:50 window); this freeze = r1057.
rep(age("2026-10-16 20:2x bm-c r1055 freeze window"), "2026-10-17 02:0x bm-c r1057 freeze window", 1, "P5a-header-window")
rep(age("W253 finalize one-pass bm-c r1053 window closeout 15:2x"),
    "W254 finalize one-pass bm-c r1055 window closeout 21:3x", 1, "P5a-closeout-window")
rep(age("r1053 splice window"), "r1055 splice window", 3, "P5a-splice-window")
rep(age("r1053"), "r1055", 19, "P5a-splice-window-rest")
rep(age("r1054"), "r1056", 7, "P5a-prereg-window")
rep(age("authored 18:0x"), "authored 01:14", 2, "P5a-authored-time")
# aging-face needle heals (same-window disclosed, r1045/r1047/r1050/r1055 precedent family):
rep(age("transitive window W241..W250 checked"), "transitive window W242..W251 checked", 1, "P5a-aging-deps-cmt")
rep(age("engine_owner==bm-c rows 73 + candidate"), "engine_owner==bm-c rows 74 + candidate", 1, "P5a-aging-rows-heal")

# ============ P5b: extraction count faces (frozen W255 prereg sec.3 mandate) ============
# estate 69 (W138..W206) + kept W211..W238 (28) UNCHANGED; dropped W239..W253 (15);
# fresh W239..W254 (16); total parity 113 rows; legs segment W211..W253 (43).
rep(age("# block's own W239..W252 legs (14 rows) do NOT enter the estate path;"),
    "# block's own W239..W253 legs (15 rows) do NOT enter the estate path;", 1, "P5b-hdr-ownlegs")
rep(age("# after extraction, fresh W239..W253 legs (15 rows) are added,"),
    "# after extraction, fresh W239..W254 legs (16 rows) are added,", 1, "P5b-hdr-freshlegs")
rep(age("# parity = 112 rows (W138..W206 + W211..W253). Zero assumption zero risk."),
    "# parity = 113 rows (W138..W206 + W211..W254). Zero assumption zero risk.", 1, "P5b-hdr-parity-count")
rep(age("# block's own W239..W252 legs (14) are EXCLUDED from the estate path per the"),
    "# block's own W239..W253 legs (15) are EXCLUDED from the estate path per the", 1, "P5b-ext-excl")
rep(age("# prereg mandate; the W254 block appends fresh W239..W253 legs (15,"),
    "# prereg mandate; the W255 block appends fresh W239..W254 legs (16,", 1, "P5b-ext-fresh")
rep(age("# machine-derived from the LIVE pf registry at freeze time) -> 112 parity"),
    "# machine-derived from the LIVE pf registry at freeze time) -> 113 parity", 1, "P5b-ext-parcount")

_PARFULL_W254 = '''assert par_full.count("assert pf.N1_BANDS[") == 111, \\
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 111 (69 estate + W211..W252 legs 42)"'''
_LEGS_W254 = '''assert legs_sec.count("assert pf.N1_BANDS[") == 42 \\
    and [int(w) for w in _legs_ws] == list(range(211, 253)), \\
    f"legs segment not W211..W252 forty-two legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}"'''
_DROP_W254 = '''assert legs_dropped.count("assert pf.N1_BANDS[") == 14 \\
    and [int(w) for w in _dropped_ws] == list(range(239, 253)), \\
    f"dropped segment not W239..W252 fourteen legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}"'''
rep(age(_PARFULL_W254),
    mk(age(_PARFULL_W254), [("== 111", "== 112", 1),
                            ("!= 111 (69 estate + W211..W252 legs 42)", "!= 112 (69 estate + W211..W253 legs 43)", 1)], "P5b-parfull"),
    1, "P5b-parfull")
rep(age(_LEGS_W254),
    mk(age(_LEGS_W254), [("== 42", "== 43", 1),
                          ("legs segment not W211..W252 forty-two legs", "legs segment not W211..W253 forty-three legs", 1)], "P5b-legs-assert"),
    1, "P5b-legs-assert")
rep(age(_DROP_W254),
    mk(age(_DROP_W254), [("== 14", "== 15", 1),
                          ("dropped segment not W239..W252 fourteen legs", "dropped segment not W239..W253 fifteen legs", 1)], "P5b-dropped-assert"),
    1, "P5b-dropped-assert")
rep(age("# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W253\n# block's own W239..W252 legs (14) are excluded from the estate path"),
    "# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W254\n# block's own W239..W253 legs (15) are excluded from the estate path", 1, "P5b-split-cmt")
rep(age('"fresh_legs_row_asserts": 15,'), '"fresh_legs_row_asserts": 16,', 1, "P5b-rcpt-fresh15")
rep(age('+ legs_kept.count("assert pf.N1_BANDS[") + 15,'), '+ legs_kept.count("assert pf.N1_BANDS[") + 16,', 1, "P5b-rcpt-total15")
rep(age('"    #     physical bytes; the W253 block\'s own W239..W252 legs (14) are",'),
    '"    #     physical bytes; the W254 block\'s own W239..W253 legs (15) are",', 1, "P5b-hdr-ownlegs-mat")
rep(age('"    #     W239..W253 legs (15) added, machine-derived from the live pf",'),
    '"    #     W239..W254 legs (16) added, machine-derived from the live pf",', 1, "P5b-hdr-freshlegs-mat")
rep(age('"    #     registry at freeze time -> 112 parity rows (W138..W206+W211..W253).",'),
    '"    #     registry at freeze time -> 113 parity rows (W138..W206+W211..W254).",', 1, "P5b-hdr-parcount-mat")

# receipt note (single big face: counts + generation stamp)
_RCPTNOTE_W254 = '''                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W238 legs (28) extracted verbatim per the frozen W254 prereg sec.3 mandate; the W253 block's own W239..W252 legs (14) EXCLUDED from the estate path per the same mandate; fresh W239..W253 legs (15) machine-derived from the live pf registry -> W254 block = 112 rows (W138..W206 + W211..W253); disclosed: (a) inherited W213 leg error-string face preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-254 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 6th-gen prevention this window: the W254 derive editor kept the P1-blanket-immune pass ordering and the extraction-restructure legs/kept/dropped wave-identity asserts fixed post-blanket (list(range(211,253))/list(range(211,239))/list(range(239,253)) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},'''
rep(age(_RCPTNOTE_W254),
    mk(age(_RCPTNOTE_W254), [
        ("own W239..W252 legs (14) EXCLUDED", "own W239..W253 legs (15) EXCLUDED", 1),
        ("fresh W239..W254 legs (15) machine-derived", "fresh W239..W254 legs (16) machine-derived", 1),
        ("W255 block = 112 rows", "W255 block = 113 rows", 1),
        ("E63 6th-gen", "E63 7th-gen", 1),
    ], "P5b-rcpt-note"),
    1, "P5b-rcpt-note")

# ============ P5c: band literals (probe ADMIT receipt bands) ============
rep(age('assert (a_lo, a_hi) == (574_101, 576_100) and (b_lo, b_hi) == (576_101, 576_300), \\'),
    'assert (a_lo, a_hi) == (576_301, 578_300) and (b_lo, b_hi) == (578_301, 578_500), \\', 1, "P5c-band-drift")

# ============ P5d: ordinal/leg0/deps faces ============
rep(age('assert len(owner_rows_live) == 243 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 73, \\'),
    'assert len(owner_rows_live) == 244 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 74, \\', 1, "P5d-ord-gate")
# needle narrowed to the pre-registration numeric face: the trailing "75th own
# wave" inside this line was ALREADY rewritten by the P5a-74th-ownwave rep
# (order-sensitive face, W254 editor canon -- its P5d needle was likewise the
# post-P5a form); disclosed needle heal, evidence = pre-flight n=1 raw face.
rep(age("(expect 243/129/73 PRE-splice post-W253 registration"),
    "(expect 244/129/74 PRE-splice post-W254 registration", 1, "P5d-ord-err")
# needle narrowed likewise: the trailing "bmc_ordinal=74" on this line was
# already rewritten to 75 by the P5a-ordinal74 rep (one of its 7 faces).
rep(age('# receipt leg0 face owner_rows=243 / bmc_rows=73 /'),
    '# receipt leg0 face owner_rows=244 / bmc_rows=74 /', 1, "P5d-leg0-prose")
rep(age("-> owner rows 243 + candidate = 244th EXACT; bm-c rows 73 +"),
    "-> owner rows 244 + candidate = 245th EXACT; bm-c rows 74 +", 1, "P5d-ord-owner-prose")
rep(age("# candidate = 74th EXACT -- bm-c own-seat continuity face (bm-c published the"),
    "# candidate = 75th EXACT -- bm-c own-seat continuity face (bm-c published the", 1, "P5d-ord-bmc-prose")
rep(age("freeze-time live face owner rows 243 + candidate = 244th EXACT"),
    "freeze-time live face owner rows 244 + candidate = 245th EXACT", 1, "P5d-rcpt-243rd")
rep(age("freeze-time live derive bmc rows 73 + candidate 74th EXACT per r587/r359"),
    "freeze-time live derive bmc rows 74 + candidate 75th EXACT per r587/r359", 1, "P5d-bundle-73rd")
rep(age("post-W253 registration: bm-c rows 73 + candidate = 74th owned"),
    "post-W254 registration: bm-c rows 74 + candidate = 75th owned", 1, "P5d-rcpt-73rd-owned")
rep(age('"probe_receipt_bmc_ordinal_face": 74,'), '"probe_receipt_bmc_ordinal_face": 75,', 1, "P5d-rcpt-ordface")
rep(age('f"W254+W249..W240 finalize products present "'), 'f"W255+W250..W241 finalize products present "', 1, "P5d-print-deps")

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
chunk(age(_HDR_W254),
      mk(age(_HDR_W254), [
          ("FOURTH consecutive\n# above-own-A", "FIFTH consecutive\n# above-own-A", 1),
          ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 1),
          ("576_101..576_300", "578_301..578_500", 1),
          ("573_901..575_900", "576_101..578_100", 1),
          ("573_901..574_100", "576_101..576_300", 1),
          ("574_101..576_100", "576_301..578_300", 2),
          ("574_101..574_300", "576_301..576_500", 1),
          ("574_100", "576_300", 2),
          ("576_100", "578_300", 2),
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
chunk(age(_BANDFACTS_W254),
      mk(age(_BANDFACTS_W254), [
          ("FOURTH consecutive above-own-A landing", "FIFTH consecutive above-own-A landing", 1),
          ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2),
      ], "P5e-bandfacts"), "P5e-bandfacts")

_A_BASE_W254 = '''assert w253_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1 EXACT -- the 1-hop walk past the registered W253 B band; third consecutive A-hop of the staircase era; A_staircase_hop_past_W253_B=true)"'''
rep(age(_A_BASE_W254),
    mk(age(_A_BASE_W254), [("third consecutive A-hop", "fourth consecutive A-hop", 1)], "P5e-a-base"),
    1, "P5e-a-base")
_A_FLOOR_W254 = '''assert a_lo >= w253_b_tail + 1, "A staircase landing floor relation (A base >= registered prior-wave B tail+1; the fourteen-wave seed-gap face ENDED at W252 -- third consecutive A-hop of the staircase era, A base == prior-B tail+1 EXACT this window per the prereg floor-relation mandate)"'''
rep(age(_A_FLOOR_W254),
    mk(age(_A_FLOOR_W254), [("third consecutive A-hop", "fourth consecutive A-hop", 1)], "P5e-a-floor"),
    1, "P5e-a-floor")
_B_BASE_W254 = '''assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation cascade lands ABOVE own-A -- fourth consecutive above-own-A; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"'''
rep(age(_B_BASE_W254),
    mk(age(_B_BASE_W254), [("fourth consecutive above-own-A", "fifth consecutive above-own-A", 1)], "P5e-b-base"),
    1, "P5e-b-base")

# relation_asserts gate (W251_W253 rsv-key fix -- the P4 blanket produces the
# W251_W252_W254 hybrid face; the probe receipt leg1 keys are W252_W253_W254)
_RA_GATE_W254 = '''ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") is False and ra.get("A_staircase_hop_past_W253_B") \\
    and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_clean_at_naive_start") is False and ra.get("B_base_above_W253_tail") \\
    and ra.get("AB_mutual_exclusion") and ra.get("B_hop_lands_inside_A") is False \\
    and ra.get("B_lands_above_own_A") and ra.get("W251_W252_W253_bands_respected_A") and ra.get("W251_W252_W253_bands_respected_B"), \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"'''
rep(age(_RA_GATE_W254),
    mk(age(_RA_GATE_W254), [
        ("W251_W252_W254_bands_respected_A", "W252_W253_W254_bands_respected_A", 1),
        ("W251_W252_W254_bands_respected_B", "W252_W253_W254_bands_respected_B", 1),
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
chunk(age(_PFCMT_W254),
      mk(age(_PFCMT_W254), [
          ("FOURTH consecutive above-own-A;", "FIFTH consecutive above-own-A;", 1),
          ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 1),
          ("hops=1 -- SECOND", "hops=1 -- THIRD", 1),
          # ENDED-at face: the P4 blanket already aged the raw "ENDED at W253;"
          # to "ENDED at W254;" inside the needle -- mechanical aging face,
          # zero sub needed (needle heal disclosed, blanket-duplication class)
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
chunk(age(_PRE_W254),
      mk(age(_PRE_W254), [
          ("FOURTH consecutive above-own-A", "FIFTH consecutive above-own-A", 1),
          ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2),
      ], "P5e-pre"), "P5e-pre")

# MEM_I comment lines (A + B faces)
_MEM_A_W254 = ''' f\'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W254 A: {fmt(a_lo)}..{fmt(a_hi)} (1-HOP STAIRCASE-AFFECTS-A walk THIRD consecutive A-hop; naive {fmt(w253_a_tail + 1)}..{fmt(w253_a_tail + 2_000)} REFUSED at start -- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; registered W253 B band inside the naive A window; third consecutive A-hop of the staircase era -- seed-gap face ENDED at W252; A base == registered prior-wave B tail+1)\','''
rep(age(_MEM_A_W254),
    mk(age(_MEM_A_W254), [
        ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 1),
        ("third consecutive A-hop", "fourth consecutive A-hop", 1),
    ], "P5e-mem-a"),
    1, "P5e-mem-a")
_MEM_B_W254 = ''' f\'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W254 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION CASCADE above own-A; naive {fmt(w253_b_tail + 1)}..{fmt(w253_b_tail + 200)} REFUSED at start -- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; naive window lands inside the own-wave A first-clean window -> own-A reservation cascade; B lands ABOVE own-A at tail+1 EXACT -- fourth consecutive above-own-A; B base == own-A tail+1)\','''
rep(age(_MEM_B_W254),
    mk(age(_MEM_B_W254), [("fourth consecutive above-own-A", "fifth consecutive above-own-A", 1)], "P5e-mem-b"),
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
chunk(age(_TAILCMT_W254),
      mk(age(_TAILCMT_W254), [
          ("FOURTH consecutive", "FIFTH consecutive", 1),
          ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2),
      ], "P5e-tailcmt"), "P5e-tailcmt")

# tail assert block (A face message)
_TAIL_AMSG_W254 = '''            "W254 A staircase-affects-A walk THIRD consecutive A-hop: the naive "',
'            "continuation is REFUSED at its own start (the registered W253 B band sits INSIDE "',
'            "the naive A window -- staircase re-emergence continues; hops=1, A_hop_chain verbatim in the probe receipt, "',
'            "A_clean_at_naive_start=false, A_staircase_hop_past_W253_B=true; the walk hops past "',
'            "the W253 B tail -> A first-clean -- THIRD consecutive A-hop of the staircase era, "',
'            "the fourteen-wave seed-gap face ENDED at W252; A base == registered prior-wave B "',
'            "tail+1 machine-checkable, floor relation honored)"'''
rep(age(_TAIL_AMSG_W254),
    mk(age(_TAIL_AMSG_W254), [("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2)], "P5e-tail-amsg"),
    1, "P5e-tail-amsg")

# tail assert block (B face messages; identity count-asserts per W254 canon)
rep(age('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "'),
    age('            "W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "'), 1, "P5e-tail-bassert2")
rep(age('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"'),
    age('            "W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"'), 1, "P5e-tail-bclean")
rep(age('            "W254 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- fourth consecutive above-own-A; zero overlap)"'),
    mk(age('            "W254 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- fourth consecutive above-own-A; zero overlap)"'),
       [("fourth consecutive above-own-A", "fifth consecutive above-own-A", 1)], "P5e-tail-excl"),
    1, "P5e-tail-excl")

# pr print A/B lines
_PRCHUNK_W254 = ''' '          "A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, "',
 '          "registered W253 B band inside the naive A window, THIRD consecutive A-hop of the staircase era, "',
 '          "the fourteen-wave seed-gap face ENDED at W252) "',
 '          "+ B=1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, "',
 '          "B_hop_chain verbatim, naive window lands inside the own-wave A window -> own-A reservation cascade, "',
 '          "B base == own-A tail+1 EXACT, B_lands_above_own_A=true, "',
 '          "FOURTH consecutive above-own-A landing), chain-order splice from the "'''
chunk(age(_PRCHUNK_W254),
      mk(age(_PRCHUNK_W254), [
          ("FOURTH consecutive above-own-A landing", "FIFTH consecutive above-own-A landing", 1),
          ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 1),
      ], "P5e-pr"), "P5e-pr")

# receipt band_semantics A + B values
_SEM_A_W254 = '''"A": "1-HOP STAIRCASE-AFFECTS-A walk THIRD consecutive A-hop (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 573_901..575_900 refused at start -- the registered W253 B band 573_901..574_100 sits INSIDE the naive A window (staircase re-emergence continues; the W253 prereg sec.5 item5 A-CLEAN-at-naive projection superseded live r587, divergence disclosed); the walk hops past the W253 B tail 574_100 -> A first-clean 574_101..576_100 -- THIRD consecutive A-hop of the staircase era, the fourteen-wave seed-gap face ENDED at W252; A_clean_at_naive_start=false; A_staircase_hop_past_W253_B=true; A base == registered prior-wave B tail+1 (574_100+1) EXACT)"'''
rep(age(_SEM_A_W254),
    mk(age(_SEM_A_W254), [
        ("THIRD consecutive A-hop", "FOURTH consecutive A-hop", 2),
        ("573_901..575_900 refused", "576_101..578_100 refused", 1),
        ("573_901..574_100 sits", "576_101..576_300 sits", 1),
        ("B tail 574_100 -> A first-clean 574_101..576_100", "B tail 576_300 -> A first-clean 576_301..578_300", 1),
        ("(574_100+1) EXACT)", "(576_300+1) EXACT)", 1),
    ], "P5e-rcpt-semantics-A"),
    1, "P5e-rcpt-semantics-A")
_SEM_B_W254 = '''"B": "1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the naive continuation 574_101..574_300 is refused at start -- the naive window lands INSIDE the own-wave W254 A first-clean window 574_101..576_100 (own-A reservation cascade standard leg; the W253 prereg sec.5 item5 + probe leg4 projected landing superseded live -- the A face itself moved, divergence disclosed per r587); the walk hops past the own-A tail 576_100 -> B landing 576_101..576_300; B lands ABOVE own-A -- FOURTH consecutive above-own-A landing; B_lands_above_own_A=true; B_hop_lands_inside_A=false; B base == own-A tail+1 (576_100+1) EXACT)"'''
rep(age(_SEM_B_W254),
    mk(age(_SEM_B_W254), [
        ("FOURTH consecutive above-own-A landing", "FIFTH consecutive above-own-A landing", 1),
        ("574_101..574_300 is refused", "576_301..576_500 is refused", 1),
        ("A first-clean window 574_101..576_100 (own-A", "A first-clean window 576_301..578_300 (own-A", 1),
        ("own-A tail 576_100 -> B landing 576_101..576_300;", "own-A tail 578_300 -> B landing 578_301..578_500;", 1),
        ("(576_100+1) EXACT)", "(578_300+1) EXACT)", 1),
    ], "P5e-rcpt-semantics-B"),
    1, "P5e-rcpt-semantics-B")

# downstream W256+ projection face (probe leg4 verbatim numbers)
_DOWNSTREAM_W254 = '''W255 = next free number, next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W255 freezer MUST re-derive live on the post-W254 universe + reserve the own-wave A window when deriving B per the W254 seat leg4 mandate, never transcribe r587 -- W255p face per this window's probe leg4 (pre-W254 universe): A naive 576101..578100 CLEAN (hops=0, zero live refusers -- pre-W254-universe face) / B naive 576301..576500 hops=0 CLEAN at naive, first-clean 576301..576500 BUT lands INSIDE the W255 projection A window (W255p_B_lands_inside_W255p_A_naive=true staircase face continuation since W252: A hops over prior B, B lands above own-A; on the post-W254 universe the W255 naive A window start 576_101 lands INSIDE the registered W254 B band 576_101..576_300 -- staircase affects A inherited, the A first-clean and the B own-A reservation cascade landing both move up, live re-derive governs); re-read the live trace at W255 derive time, do NOT assume the staircase A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities'''
rep(age(_DOWNSTREAM_W254),
    mk(age(_DOWNSTREAM_W254), [
        ("A naive 576101..578100 CLEAN", "A naive 578301..580300 CLEAN", 1),
        # pre-universe + W-ref faces: the P2/P3 blankets already aged the raw
        # "pre-W254-universe" -> "pre-W255-universe" and "registered W254 B band"
        # -> "registered W255 B band" inside the needle -- only the numeric
        # faces need sub-replacement (blanket-duplication class, disclosed)
        ("B naive 576301..576500 hops=0 CLEAN at naive, first-clean 576301..576500 BUT", "B naive 578501..578700 hops=0 CLEAN at naive, first-clean 578501..578700 BUT", 1),
        ("naive A window start 576_101 lands INSIDE the registered W255 B band 576_101..576_300", "naive A window start 578_301 lands INSIDE the registered W255 B band 578_301..578_500", 1),
        ("staircase face continuation since W252", "staircase face continuation since W251", 1),
    ], "P5e-rcpt-downstream"),
    1, "P5e-rcpt-downstream")

# ============ structural output gates ============
for needle, want in [
    ("# --- W255 materializer face", 2),
    ("# --- W254 materializer face", 1),
    ('"+ W255 materializer face', 2),
    ("range(16, 255)", 2),
    ("range(17, 255)", 3),
    ("range(239, 255)", 2),
    ("list(range(211, 254)),", 1),
    ("list(range(211, 239))", 1),
    ("list(range(239, 254)),", 1),
    ("range(209, 256)", 2),
    ("if w < 255)", 5),
    ("if w < 254)", 1),
    ("_w255bmc_20261016_probe_receipt.json", 10),
    ("_w255bmc_freeze_receipt.json", 1),
    ("MSG-20261016-22xx-bmc-w255-seat", 7),
    ("cb79242ed", 2),
    ("983_135", 1),
    ("556_720", 1),
    ("(576_301, 578_300)", 1),
    ("(578_301, 578_500)", 1),
    ("W252_W253_W254_bands_respected_A", 1),
    ("W252_W253_W254_bands_respected_B", 1),
    ("B_base_above_W254_tail", 2),
    ("A_staircase_hop_past_W254_B", None),
    ("W256p_A_naive", 5),
    ("W256p_B_first_clean", 2),
    ("arith_a255", 6),
    ("arith_b255", 6),
    ('"PERPETUAL-N1-W255-SHARD-0"', 1),
    ("n1_w255_results.json", 2),
    ("n1_w255", 4),
    ("n1w255", 2),
    ("PERPETUAL-N1-W255", 7),
    ("_w255bmc", 11),
    ("w244_a", 12),
    ("SEVENTY-FIFTH", 3),
    ("TWO HUNDRED AND FIFTY-FIFTH", 3),
    ("forty-third consecutive", 2),
    ("bmc_ordinal=75", 7),
    ("75th own wave", 3),
    ("r1055 splice window", 3),
    ("r1055", 23),
    ("r1056", 7),
    ("r1057 freeze window", 1),
    ("estate 69", 1),
    ("= 113 rows", 2),
    ("113 parity", 2),
    ("hops=1", None),
    ("1-HOP", None),
    ("FOURTH consecutive A-hop", None),
    ("FIFTH consecutive above-own-A", None),
    # anti-gates: stale faces must be zero
    ("r1053", 0),
    ("r1054", 0),
    ("fa70f3765", 0),
    ("e2c4b543e", 0),
    ("980,935", 0),
    ("554,520", 0),
    ("980_935", 0),
    ("554_520", 0),
    ("SEVENTY-FOURTH", 0),
    ("TWO HUNDRED AND FIFTY-FOURTH", 0),
    ("forty-second consecutive", 0),
    ("MSG-20261016-14xx", 0),
    ("authored 18:0x", 0),
    ("bmc_ordinal=74", 0),
    ("74th own wave", 0),
    ("244th", 0),
    ("243/129/73", 0),
    ("FOURTH consecutive above-own-A", 0),
    ("FIRST A-hop", 0),
    ("seed-gap face ENDS", 0),
    ("573_901..575_900", 0),
    ("573_901..574_100", 0),
    ("574_101..574_300", 0),
    ("574_101..576_100", 0),
    ("574_100", 0),
    ("576_100", 0),
    ("573_901", 0),
    ("574_101", 0),
    ("~575_901..575_900", 0),
    ("(574_101, 576_100)", 0),
    ("(576_101, 576_300)", 0),
    ("== 111", 0),
    ("forty-two legs", 0),
    ("fourteen legs", 0),
    ("112 parity", 0),
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
