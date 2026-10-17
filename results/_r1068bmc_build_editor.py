# -*- coding: utf-8 -*-
# r1068 bm-c: BUILD results/_w262bmc_derive_editor.py from the committed W261
# derive-editor canon (results/_w261bmc_derive_editor.py @ HEAD) by machine
# splice (E63 14th-gen zero-transcription law: every replay-chain family
# literal + every replay sublist is spliced VERBATIM from the committed canon
# bytes; only the new-generation section texts are hand-authored here and every
# count is floor-asserted). Builder receipt: results/_r1068bmc_build_editor_log.txt.
# Pre-flight evidence: results/_w262bmc_editor_needle_counts.txt (measured on the
# committed W261 freeze-edits T0 blob 36cccfb736c7d56ca3dceac5d85651eef6da993d;
# probe results/_w262bmc_editor_needle_preflight.py 148 faces, run 16:3x this window).
# AGING-TOKEN LAW (E63, 3rd-instance prevention; r1064+r1065 healed the first two):
# the frozen aging-face token w244_a does NOT roll -- canon-editor count 2 carried,
# T0 count 12 carried, anti-gate w245_a==0 enforced in the output gates.
import io, subprocess, sys

CANON = "results/_w261bmc_derive_editor.py"
DST = "results/_w262bmc_derive_editor.py"
LOG = "results/_r1068bmc_build_editor_log.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w261bmc_derive_editor.py"], capture_output=True, text=True).stdout.strip()
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
    """E261 final call  ->  E262: _X_W261 reconstruction line + NEW final call.
    The E261 final sublist text is extracted VERBATIM from the canon bytes."""
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
    nv = var[:-1] + "0"                       # _X_W250 -> _X_W251
    recon = (f"{nv} = mk261(age_prev6({var}), [{sublist}], \"{tag}-prev7\")")
    if kind == "rep":
        new_final = (f"rep(age({nv}),\n    mk(age({nv}), [{new_subs}\n    ], \"{tag}\"),\n    1, \"{tag}\")")
    else:
        new_final = (f"chunk(age({nv}),\n      mk(age({nv}), [{new_subs}\n      ], \"{tag}\"), \"{tag}\")")
    t = t[:i] + recon + "\n" + new_final + t[j:]
    log.append(f"extend {var}: final -> recon+final (sublist {len(sublist)}B spliced verbatim)")

# ---------- 1) header ----------
NEW_HEADER = r'''# -*- coding: utf-8 -*-
# r1068 bm-c: derive results/_w262bmc_freeze_edits.py from the committed W261
# freeze-edits script (results/_w261bmc_freeze_edits.py, proven live-fire W261
# splice bm-c r1067 window: splice 89aeea31b + engine self-burn 12/12
# [ledger appends 85e44f6a6 + 778bd1c04 + ceeb47cda] + finalize one-pass
# ledger 998,535 / K=572,120 five-key 6/6 + sec.7/8 backfilled by the r1067
# closeout 15:55:57)
# via COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage, 14th-gen pass ordering:
# P1 structural outputs BLANKET-IMMUNE; the W262 extraction faces move ONE
# structural face vs the W261 estate mandate -- the kept/dropped split
# boundary MOVES 243->244 per the frozen W262 prereg sec.3 mandate [kept
# W211..W243 (33) + dropped W244..W260 (17) + fresh W244..W261 (18) = 120
# parity rows W138..W206+W211..W261, the W262 block parity list enumerates
# W211..W261 with NO gap]; the boundary move = NEW-face direct-rep class
# this generation: five m243->m244 code faces + kept assert 32/range(211,243)
# -> 33/range(211,244) + dropped range lower bound + fresh-loop/leg-count-loop
# lower bounds + the mat-hdr kept line, all pre-flight count-asserted).
# W262 facts (machine-read from the probe receipt _w262bmc_20261017, never
# transcribed):
# bands A 591_701..593_700 (1-HOP STAIRCASE-AFFECTS-A walk, ELEVENTH
# consecutive A-hop -- the naive continuation 591_501..593_500 is REFUSED at
# its own start: the registered W261 B band 591_501..591_700 sits INSIDE the
# naive A window = staircase re-emergence continues to affect A, the W261
# prereg sec.5 item5 A-naive-CLEAN pre-W261-universe projection superseded
# live per r587, divergence disclosed; the walk hops past the W261 B tail
# 591_700 -> A first-clean 591_701..593_700, hops=1; A base == registered
# prior-wave B tail+1 (591_700+1) EXACT this window; A_clean_at_naive_start=
# false; A_staircase_hop_past_W261_B=true) /
# B 593_701..593_900 (1-HOP own-A RESERVATION CASCADE above own-A, TWELFTH
# consecutive above-own-A -- the naive continuation 591_701..591_900 is
# REFUSED at its own start -- the naive window lands INSIDE the own-wave
# W262 A first-clean window 591_701..593_700, own-A reservation cascade
# standard leg; the walk hops past the own-A tail 593_700 -> B landing
# 593_701..593_900, hops=1; B lands ABOVE own-A; B base == own-A tail+1
# (593_700+1) EXACT; B_naive_refused_at_start=true; B_lands_above_own_A=true;
# B_hop_lands_inside_A=false; hops=1), upstream W261 = bm-c own chain, seat
# MSG-20261017-1425-bmc-w262-seat @ origin 693e926b1 (r1067 window, W262
# SEAT published post-W261-chain -- queue-head FREEZE-UNBLOCKED supply, zero
# waits-upstream), prereg 32d28ffb3 derived bm-c dead-ACP-window (authored
# 15:2x, banned_direction_gate ADMIT rc0, committed+pushed by the r1067
# continuation session 15:5x; splice window = r1068 THIS window -- prereg
# window != splice window r-number this generation, disclosed).
# Needle law this generation: ALL chunk/repp needles are machine-derived via
# age() = the exact blanket composition (P2 W262->W263, P3 261->262,
# P4 260->261) applied to the W261-script-era literals; the era chunk faces
# are reconstructed by the EIGHT-LEVEL chain mk255(age_prev255(W254 literal))
# -> mk256 -> mk257 -> mk258 -> mk259 -> mk260 -> mk261(age_prev6(...)) -> age()
# needle (E63 14th-gen, disclosed; needle pre-flight probe
# results/_w262bmc_editor_needle_preflight.py RUN 16:3x by the r1068 window
# -- 148 faces measured on the committed W261 freeze-edits script; this
# editor itself was built by the machine-splice builder
# results/_r1068bmc_build_editor.py -- family literals + replay sublists
# spliced verbatim from the committed E261 canon bytes, zero
# hand-transcription).
# AGING-TOKEN LAW (E63): the frozen aging-face token w244_a does NOT roll
# this generation (canon-editor count 2 carried verbatim; the r1065 builder
# defect that rolled it twice is law -- do NOT produce w245_a).
# Date-stable face this generation: the probe receipt basename date does NOT
# roll AGAIN (20261017 == 20261017, sixth consecutive date-stable
# generation) -- the P5f rep is an identity count-assert (10x), zero heal
# needed (disclosed).
'''
sect(t.split("\n", 1)[0], "import io, os, subprocess, sys", NEW_HEADER, "hdr")

# ---------- 2) path faces + blob sha (order: DST/LOG first, then SRC) ----------
rep('"_w261bmc_freeze_edits.py"', '"_w262bmc_freeze_edits.py"', 1, "dst-path")
rep('"_w261bmc_derive_editor_log.txt"', '"_w262bmc_derive_editor_log.txt"', 1, "log-path")
rep('"_w260bmc_freeze_edits.py"', '"_w261bmc_freeze_edits.py"', 1, "src-path")
rep('HEAD:results/_w260bmc_freeze_edits.py', 'HEAD:results/_w261bmc_freeze_edits.py', 1, "src-blob-path")
rep('assert blob_wt == "d15b53af21cff0ec34271e9a24eab731750a3b07"',
    'assert blob_wt == "36cccfb736c7d56ca3dceac5d85651eef6da993d"', 1, "src-blob-sha")

# ---------- 3) era functions (eight-level era chain this generation) ----------
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
# the W258-era faces (added 12th-gen; body = the W259 editor's age() verbatim).
def age_prev4(s):
    s = s.replace("W259", "W260")
    s = s.replace("258", "259")
    s = s.replace("257", "258")
    return s

# age_prev5(): the W260 editor's blanket composition (P2 W260->W261,
# P3 259->260, P4 258->259) -- reconstructs the W260-script chunk faces from
# the W259-era faces (added 13th-gen; body = the W260 editor's age() verbatim).
def age_prev5(s):
    s = s.replace("W260", "W261")
    s = s.replace("259", "260")
    s = s.replace("258", "259")
    return s

# age_prev6(): the W261 editor's blanket composition (P2 W261->W262,
# P3 260->261, P4 259->260) -- reconstructs the W261-script chunk faces from
# the W260-era faces (NEW level this generation, disclosed; body = the W261
# editor's age() verbatim).
def age_prev6(s):
    s = s.replace("W261", "W262")
    s = s.replace("260", "261")
    s = s.replace("259", "260")
    return s

# age(): EXACT composition of MY blanket passes (P2 downstream W262->W263,
# P3 self 261->262, P4 upstream 260->261) -- derives post-pass needles from
# W261-script-era literals WITHOUT hand-derivation.
def age(s):
    s = s.replace("W262", "W263")
    s = s.replace("261", "262")
    s = s.replace("260", "261")
    return s

'''
sect("# age_prev255(): the W255 editor", "def rep(old, new, expect=None, tag=", NEW_ERAS, "eras")

# ---------- 4) mk261 def insert + mk() comment roll ----------
NEW_MK261 = r'''# mk261(): rebuild the W261-script chunk from the W260-era face (asserts
# the W261 editor's fact subs exactly as the r1067-era editor ran them; NEW
# level this generation, disclosed).
def mk261(needle, repls, tag):
    s = needle
    for old, new, cnt in repls:
        n = s.count(old)
        assert n == cnt, f"[{tag}.{s.count(old)}] sub {old[:56]!r}: {n} != {cnt}"
        s = s.replace(old, new)
    return s

'''
sect("# mk(): build a chunk NEW text", "def mk(needle, repls, tag):",
     NEW_MK261 + '# mk(): build a chunk NEW text from its (post-blanket) needle via ordered\n# count-asserted fact replacements -- W262 facts from the probe receipt.\n\n', "mk261")

# ---------- 5) P1..P4x ----------
NEW_P1_P4X = r'''# ============ P1: structural faces, BLANKET-IMMUNE outputs ============
rep("(257, 256, 255, 254, 253, 252, 251, 250, 249, 248)",
    "(258, 257, 256, 255, 254, 253, 252, 251, 250, 249)", 2, "P1-transitive-deps")
rep("range(209, 262)", "range(209, 263)", 2, "P1-liveness-range")
rep('def fmt(n):  # 589501 -> "589_501"', 'def fmt(n):  # 591701 -> "591_701"', 1, "P1-fmt-comment")

# ============ P2: downstream shift W262 -> W263 ============
rep("W262", "W263", None, "P2-downstream")
assert "W262" not in t, "P2 leftover W262"

# ============ P3: self shift 261 -> 262 ============
n261 = t.count("261")
rep("261", "262", None, "P3-self")
log.append(f"P3 consumed {n261} '261' substrings")

# ============ P4: upstream shift 260 -> 261 ============
n260 = t.count("260")
rep("260", "261", None, "P4-upstream")
log.append(f"P4 consumed {n260} '260' substrings")

# ============ P4x: blanket-exemption heal (NONE this generation, disclosed) ============
# the MY-blanket shifts do NOT hit the FOUR "hashlib.sha256" API-name
# occurrences inside the source (sha256 contains "256" but NOT "260"/"261";
# pre-flight evidence: hashlib.sha256=4 / sha260=0 / sha261=0 on the
# committed W261 script) -- zero heal needed again this generation.

'''
sect("# ============ P1: structural faces", "# ============ P5a: numeric/anchor", NEW_P1_P4X, "P1-P4x")

# ---------- 6) P5a ----------
NEW_P5A = r'''# ============ P5a: numeric/anchor/ordinal/window faces (post-blanket forms) ============
# r-window ORDER DISCLOSURE (needle-heal family, vs the W261 editor order):
# the source's own prereg-window refs are r1066 (7x) AND its closeout line is
# the W260-finalize ref -- the E262 chain reps CREATE new "r1067" strings
# (from the 23 "r1065" refs), so the header-window rep runs FIRST (consumes
# the unique full-stamp needle BEFORE any r1065->r1067 creation lands),
# prereg-window second, closeout/splice/rest after. Counts
# pre-flight-verified on the committed W261 script: r1066=7 (prereg) /
# r1065=23 (3 splice-window + 1 closeout + 19 rest) / r1067=1 (stamp) /
# r1064=0 / r1063=0.
# Coincidence disclosure this generation: the W262 prereg window (dead-ACP
# r1067 derive) and the splice window (r1068 THIS window) DIFFER by one
# r-number -- the prereg rep writes r1067 while the freeze stamp writes
# r1068, distinct needles, zero collision (the full-stamp needle is consumed
# first), disclosed.
rep(age("2026-10-17 13:4x bm-c r1067 freeze window"), "2026-10-17 16:4x bm-c r1068 freeze window", 1, "P5a-header-window")
rep(age("r1066"), "r1067", 7, "P5a-prereg-window")
rep(age("W260 finalize one-pass bm-c r1065 window closeout 12:2x"),
    "W261 finalize one-pass bm-c r1067 window closeout 15:5x", 1, "P5a-closeout-window")
rep(age("r1065 splice window"), "r1067 splice window", 3, "P5a-splice-window")
rep(age("r1065"), "r1067", 19, "P5a-splice-window-rest")
rep(age("authored 12:5x"), "authored 15:2x", 2, "P5a-authored-time")
rep(age("996_335"), "998_535", 1, "P5a-ledger-int")
rep(age("569_920"), "572_120", 1, "P5a-k-int")
rep(age("996,335"), "998,535", 8, "P5a-ledger-prose")
rep(age("569,920"), "572,120", 8, "P5a-k-prose")
rep(age("bmc_ordinal=81"), "bmc_ordinal=82", 7, "P5a-ordinal81")
rep(age("EIGHTY-FIRST"), "EIGHTY-SECOND", 3, "P5a-eighty-first")
rep(age("TWO HUNDRED AND SIXTY-FIRST"), "TWO HUNDRED AND SIXTY-SECOND", 3, "P5a-262nd")
rep(age("forty-ninth consecutive"), "fiftieth consecutive", 2, "P5a-finface")
rep(age("81st own wave"), "82nd own wave", 3, "P5a-81st-ownwave")
rep(age("MSG-20261017-1225-bmc-w261-seat"), "MSG-20261017-1425-bmc-w262-seat", 7, "P5a-seat-msg")
rep(age("cf23c4553"), "693e926b1", 2, "P5a-seat-origin")
rep(age("03ab504d7"), "32d28ffb3", 1, "P5a-prereg-commit")
# aging-face needle heals (same-window disclosed, r1045/r1047/r1050/r1055/r1057/r1058/r1062/r1065/r1067 precedent family):
rep(age("transitive window W248..W257 checked"), "transitive window W249..W258 checked", 1, "P5a-aging-deps-cmt")
rep(age("engine_owner==bm-c rows 80 + candidate"), "engine_owner==bm-c rows 81 + candidate", 1, "P5a-aging-rows-heal")

'''
sect("# ============ P5a: numeric/anchor", "# ============ P5b: extraction count faces", NEW_P5A, "P5a")

# ---------- 7) P5b direct (pre-chain) ----------
NEW_P5B = r'''# ============ P5b: extraction count faces (frozen W262 prereg sec.3 mandate) ============
# estate 69 (W138..W206) UNCHANGED; kept W211..W243 (33); dropped W244..W260
# (17); fresh W244..W261 (18); total parity 120 rows; legs segment
# W211..W260 (50). NEW FACE this generation (disclosed): the kept/dropped
# split boundary MOVES 243->244 per the frozen W262 prereg sec.3 mandate
# (kept W211..W243 33 legs -- the W262 block parity list enumerates W211..W261
# with NO gap, so W243 moves from the dropped set into the kept set); five
# m243->m244 code faces + kept/dropped range faces + fresh-loop lower bounds
# are count-asserted direct reps (pre-flight: m243=4 / range(243,261)=2 /
# kept-32=1 / dropped-17=1).
rep(age("# block's own W243..W259 legs (17 rows) do NOT enter the estate path;"),
    "# block's own W244..W260 legs (17 rows) do NOT enter the estate path;", 1, "P5b-hdr-ownlegs")
rep(age("# after extraction, fresh W243..W260 legs (18 rows) are added,"),
    "# after extraction, fresh W244..W261 legs (18 rows) are added,", 1, "P5b-hdr-freshlegs")
rep(age("# parity = 119 rows (W138..W206 + W211..W260). Zero assumption zero risk."),
    "# parity = 120 rows (W138..W206 + W211..W261). Zero assumption zero risk.", 1, "P5b-hdr-parity-count")
rep(age("# block's own W243..W259 legs (17) are EXCLUDED from the estate path per the"),
    "# block's own W244..W260 legs (17) are EXCLUDED from the estate path per the", 1, "P5b-ext-excl")
rep(age("# prereg mandate; the W261 block appends fresh W243..W260 legs (18,"),
    "# prereg mandate; the W262 block appends fresh W244..W261 legs (18,", 1, "P5b-ext-fresh")
rep(age("# machine-derived from the LIVE pf registry at freeze time) -> 119 parity"),
    "# machine-derived from the LIVE pf registry at freeze time) -> 120 parity", 1, "P5b-ext-parcount")
'''
sect("# ============ P5b: extraction count faces", "_PARFULL_W255 = ", NEW_P5B, "P5b-direct")

# ---------- 8) P5b chains: extend 4 families ----------
extend_family("_PARFULL_W250", "rep", "P5b-parfull",
    '\n        ("== 118", "== 119", 1),\n        ("!= 118 (69 estate + W211..W259 legs 49)", "!= 119 (69 estate + W211..W260 legs 50)", 1),')
extend_family("_LEGS_W250", "rep", "P5b-legs-assert",
    '\n        ("== 49", "== 50", 1),\n        ("legs segment not W211..W259 forty-nine legs", "legs segment not W211..W260 fifty legs", 1),')
extend_family("_DROP_W250", "rep", "P5b-dropped-assert",
    '\n        ("list(range(243, 261))", "list(range(244, 261))", 1),\n        ("dropped segment not W243..W259 seventeen legs", "dropped segment not W244..W260 seventeen legs", 1),')
extend_family("_RCPTNOTE_W250", "rep", "P5b-rcpt-note",
    '\n        ("own W243..W259 legs (17) EXCLUDED", "own W244..W260 legs (17) EXCLUDED", 1),\n        ("fresh W243..W261 legs (18) machine-derived", "fresh W244..W261 legs (18) machine-derived", 1),\n        ("W262 block = 119 rows", "W262 block = 120 rows", 1),\n        ("E63 13th-gen", "E63 14th-gen", 1),\n        ("W211..W242 legs (32)", "W211..W243 legs (33)", 1),\n        ("list(range(211,261))/list(range(211,243))/list(range(243,261))", "list(range(211,261))/list(range(211,244))/list(range(244,261))", 1),')

# ---------- 9) P5b late (split/boundary/mat/rcpt-identity reps) ----------
NEW_P5B_LATE = r"""# NEW-FACE split-boundary reps (243 -> 244, frozen W262 prereg sec.3 mandate):
rep(age("# prereg sec.3 mandate split: keep W211..W242 verbatim (32 legs); the W260\n# block's own W243..W259 legs (17) are excluded from the estate path"),
    "# prereg sec.3 mandate split: keep W211..W243 verbatim (33 legs); the W261\n# block's own W244..W260 legs (17) are excluded from the estate path", 1, "P5b-split-cmt")
rep(r'm243 = re.search(r" *assert pf\.N1_BANDS\[243\] ==", legs_sec)',
    r'm244 = re.search(r" *assert pf\.N1_BANDS\[244\] ==", legs_sec)', 1, "P5b-split-mvar")
rep(age('assert m243, "W243 leg boundary not found inside W261 legs segment (prereg sec.3 split face)"'),
    'assert m244, "W244 leg boundary not found inside W262 legs segment (prereg sec.3 split face)"', 1, "P5b-split-assert")
rep("legs_kept = legs_sec[:m243.start()]", "legs_kept = legs_sec[:m244.start()]", 1, "P5b-split-kept")
rep("legs_dropped = legs_sec[m243.start():]", "legs_dropped = legs_sec[m244.start():]", 1, "P5b-split-dropped")
# kept assert moves 32/range(211,243) -> 33/range(211,244) (NEW face, pre-flight raw count 1):
_KEPT_W261 = '''assert legs_kept.count("assert pf.N1_BANDS[") == 32 \\
    and [int(w) for w in _kept_ws] == list(range(211, 243)), \\
    f"kept segment not W211..W242 thirty-two legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"'''
rep(_KEPT_W261, '''assert legs_kept.count("assert pf.N1_BANDS[") == 33 \\
    and [int(w) for w in _kept_ws] == list(range(211, 244)), \\
    f"kept segment not W211..W243 thirty-three legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"''', 1, "P5b-kept-assert")
# fresh-loop + leg-count-loop lower bounds + fresh first-line assert (NEW face):
rep(age("for _w in range(243, 261):"), "for _w in range(244, 262):", 1, "P5b-fresh-loop")
rep(age("for _lw in range(243, 261):"), "for _lw in range(244, 262):", 1, "P5b-legcount-loop")
rep("assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[243] == {\"a\": (')",
    "assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[244] == {\"a\": (')", 1, "P5b-fresh-firstline")
# receipt count faces: fresh stays 18 this generation = identity count-asserts (disclosed):
rep(age('"fresh_legs_row_asserts": 18,'), '"fresh_legs_row_asserts": 18,', 1, "P5b-rcpt-fresh18-identity")
rep(age('+ legs_kept.count("assert pf.N1_BANDS[") + 18,'), '+ legs_kept.count("assert pf.N1_BANDS[") + 18,', 1, "P5b-rcpt-total18-identity")
# materializer hdr comment faces:
rep(age('"    #     W211..W242 legs (32) extracted verbatim from the OWN W260 block",'),
    '"    #     W211..W243 legs (33) extracted verbatim from the OWN W261 block",', 1, "P5b-hdr-kept-mat")
rep(age('"    #     physical bytes; the W261 block\'s own W243..W259 legs (17) are",'),
    '"    #     physical bytes; the W262 block\'s own W244..W260 legs (17) are",', 1, "P5b-hdr-ownlegs-mat")
rep(age('"    #     W243..W260 legs (18) added, machine-derived from the live pf",'),
    '"    #     W244..W261 legs (18) added, machine-derived from the live pf",', 1, "P5b-hdr-freshlegs-mat")
rep(age('"    #     registry at freeze time -> 119 parity rows (W138..W206+W211..W260).",'),
    '"    #     registry at freeze time -> 120 parity rows (W138..W206+W211..W261).",', 1, "P5b-hdr-parcount-mat")

"""
sect('rep(age("# prereg sec.3 mandate split:', '# receipt note (single big face: counts + generation stamp)', NEW_P5B_LATE, "P5b-late")

# ---------- 10) P5c ----------
NEW_P5C = r'''# ============ P5c: band literals (probe ADMIT receipt bands) ============
rep(age('assert (a_lo, a_hi) == (589_501, 591_500) and (b_lo, b_hi) == (591_501, 591_700), \\'),
    'assert (a_lo, a_hi) == (591_701, 593_700) and (b_lo, b_hi) == (593_701, 593_900), \\', 1, "P5c-band-drift")

'''
sect("# ============ P5c: band literals", "# ============ P5d: ordinal/leg0", NEW_P5C, "P5c")

# ---------- 11) P5d ----------
NEW_P5D = r'''# ============ P5d: ordinal/leg0/deps faces ============
rep(age('assert len(owner_rows_live) == 250 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 80, \\'),
    'assert len(owner_rows_live) == 251 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 81, \\', 1, "P5d-ord-gate")
# needle narrowed to the pre-registration numeric face: the trailing "82nd own
# wave" inside this line was ALREADY rewritten by the P5a-81st-ownwave rep
# (order-sensitive face, W261 editor canon -- its P5d needle was likewise the
# post-P5a form); disclosed needle heal, evidence = pre-flight n=1 raw face.
rep(age("(expect 250/129/80 PRE-splice post-W260 registration"),
    "(expect 251/129/81 PRE-splice post-W261 registration", 1, "P5d-ord-err")
# needle narrowed likewise: the trailing "bmc_ordinal=82" on this line was
# already rewritten by the P5a-ordinal81 rep (one of its 7 faces).
rep(age('# receipt leg0 face owner_rows=250 / bmc_rows=80 /'),
    '# receipt leg0 face owner_rows=251 / bmc_rows=81 /', 1, "P5d-leg0-prose")
rep(age("-> owner rows 250 + candidate = 251st EXACT; bm-c rows 80 +"),
    "-> owner rows 251 + candidate = 252nd EXACT; bm-c rows 81 +", 1, "P5d-ord-owner-prose")
rep(age("# candidate = 81st EXACT -- bm-c own-seat continuity face (bm-c published the"),
    "# candidate = 82nd EXACT -- bm-c own-seat continuity face (bm-c published the", 1, "P5d-ord-bmc-prose")
rep(age("freeze-time live face owner rows 250 + candidate = 251st EXACT"),
    "freeze-time live face owner rows 251 + candidate = 252nd EXACT", 1, "P5d-rcpt-252nd")
rep(age("freeze-time live derive bmc rows 80 + candidate 81st EXACT per r587/r359"),
    "freeze-time live derive bmc rows 81 + candidate 82nd EXACT per r587/r359", 1, "P5d-bundle-82nd")
rep(age("post-W260 registration: bm-c rows 80 + candidate = 81st owned"),
    "post-W261 registration: bm-c rows 81 + candidate = 82nd owned", 1, "P5d-rcpt-82nd-owned")
rep(age('"probe_receipt_bmc_ordinal_face": 81,'), '"probe_receipt_bmc_ordinal_face": 82,', 1, "P5d-rcpt-ordface")
rep(age('f"W261+W256..W247 finalize products present "'), 'f"W262+W257..W248 finalize products present "', 1, "P5d-print-deps")

'''
sect("# ============ P5d: ordinal/leg0", "# ============ P5e: A/B face structural", NEW_P5D, "P5d")

# ---------- 12) P5e families (extend; new final subs = W262 facts) ----------
extend_family("_HDR_W250", "chunk", "P5e-hdr",
    '\n          ("ELEVENTH consecutive\\n# above-own-A", "TWELFTH consecutive\\n# above-own-A", 1),\n          ("TENTH consecutive A-hop", "ELEVENTH consecutive A-hop", 1),\n          ("589_501..591_500", "591_701..593_700", 2),\n          ("591_501..591_700", "593_701..593_900", 1),\n          ("589_301..591_300", "591_501..593_500", 1),\n          ("589_301..589_500", "591_501..591_700", 1),\n          ("589_501..589_700", "591_701..591_900", 1),\n          ("589_500", "591_700", 2),\n          ("591_500", "593_700", 2),')
extend_family("_BANDFACTS_W250", "chunk", "P5e-bandfacts",
    '\n          ("ELEVENTH consecutive above-own-A landing", "TWELFTH consecutive above-own-A landing", 1),\n          ("TENTH consecutive A-hop", "ELEVENTH consecutive A-hop", 2),')
extend_family("_A_BASE_W250", "rep", "P5e-a-base",
    ' ("tenth consecutive A-hop", "eleventh consecutive A-hop", 1),')
extend_family("_A_FLOOR_W250", "rep", "P5e-a-floor",
    ' ("tenth consecutive A-hop", "eleventh consecutive A-hop", 1),')
extend_family("_B_BASE_W250", "rep", "P5e-b-base",
    ' ("eleventh consecutive above-own-A", "twelfth consecutive above-own-A", 1),')
extend_family("_RA_GATE_W250", "rep", "P5e-ra-gate",
    '\n        ("W258_W259_W261_bands_respected_A", "W259_W260_W262_bands_respected_A", 1),\n        ("W258_W259_W261_bands_respected_B", "W259_W260_W262_bands_respected_B", 1),')
extend_family("_PFCMT_W250", "chunk", "P5e-pfcmt",
    '\n          ("ELEVENTH consecutive above-own-A;", "TWELFTH consecutive above-own-A;", 1),\n          ("TENTH consecutive A-hop", "ELEVENTH consecutive A-hop", 1),\n          ("hops=1 -- NINTH", "hops=1 -- TENTH", 1),')
extend_family("_PRE_W250", "chunk", "P5e-pre",
    '\n          ("ELEVENTH consecutive above-own-A", "TWELFTH consecutive above-own-A", 1),\n          ("TENTH consecutive A-hop", "ELEVENTH consecutive A-hop", 2),')
extend_family("_MEM_A_W250", "rep", "P5e-mem-a",
    '\n        ("TENTH consecutive A-hop", "ELEVENTH consecutive A-hop", 1),\n        ("tenth consecutive A-hop", "eleventh consecutive A-hop", 1),')
extend_family("_MEM_B_W250", "rep", "P5e-mem-b",
    ' ("eleventh consecutive above-own-A", "twelfth consecutive above-own-A", 1),')
extend_family("_TAILCMT_W250", "chunk", "P5e-tailcmt",
    '\n          ("ELEVENTH consecutive", "TWELFTH consecutive", 1),\n          ("TENTH consecutive A-hop", "ELEVENTH consecutive A-hop", 2),')
extend_family("_TAIL_AMSG_W250", "rep", "P5e-tail-amsg",
    ' ("TENTH consecutive A-hop", "ELEVENTH consecutive A-hop", 2),')
extend_family("_EXCL_W250", "rep", "P5e-tail-excl",
    ' ("eleventh consecutive above-own-A", "twelfth consecutive above-own-A", 1),')
extend_family("_PRCHUNK_W250", "chunk", "P5e-pr",
    '\n          ("ELEVENTH consecutive above-own-A landing", "TWELFTH consecutive above-own-A landing", 1),\n          ("TENTH consecutive A-hop", "ELEVENTH consecutive A-hop", 1),')
extend_family("_SEM_A_W250", "rep", "P5e-rcpt-semantics-A",
    '\n        ("TENTH consecutive A-hop", "ELEVENTH consecutive A-hop", 2),\n        ("589_301..591_300 refused", "591_501..593_500 refused", 1),\n        ("589_301..589_500 sits", "591_501..591_700 sits", 1),\n        ("B tail 589_500 -> A first-clean 589_501..591_500", "B tail 591_700 -> A first-clean 591_701..593_700", 1),\n        ("(589_500+1) EXACT)", "(591_700+1) EXACT)", 1),')
extend_family("_SEM_B_W250", "rep", "P5e-rcpt-semantics-B",
    '\n        ("ELEVENTH consecutive above-own-A landing", "TWELFTH consecutive above-own-A landing", 1),\n        ("589_501..589_700 is refused", "591_701..591_900 is refused", 1),\n        ("A first-clean window 589_501..591_500 (own-A", "A first-clean window 591_701..593_700 (own-A", 1),\n        ("own-A tail 591_500 -> B landing 591_501..591_700;", "own-A tail 593_700 -> B landing 593_701..593_900;", 1),\n        ("(591_500+1) EXACT)", "(593_700+1) EXACT)", 1),')
extend_family("_DOWNSTREAM_W250", "rep", "P5e-rcpt-downstream",
    '\n        ("A naive 591501..593500 CLEAN", "A naive 593701..595700 CLEAN", 1),\n        ("B naive 591701..591900 hops=0 CLEAN at naive, first-clean 591701..591900 BUT", "B naive 593901..594100 hops=0 CLEAN at naive, first-clean 593901..594100 BUT", 1),\n        ("naive A window start 591_501 lands INSIDE the registered W262 B band 591_501..591_700", "naive A window start 593_701 lands INSIDE the registered W262 B band 593_701..593_900", 1),')

# identity reps: SEVEN-level inline chain -> EIGHT-LEVEL (age_prev6 inserted;
# computed string surgery keeps paren balance, disclosed; the literal faces
# are era-stable W254 needles):
for _itag in ("P5e-tail-bassert2", "P5e-tail-bclean"):
    i = t.index("rep(age(age_prev5(")
    j = t.index(f', 1, "{_itag}")', i) + len(f', 1, "{_itag}")')
    stmt = t[i:j]
    assert stmt.count("age(age_prev5(") == 2, f"identity face drift [{_itag}]: {stmt.count('age(age_prev5(')} != 2"
    new_stmt = stmt.replace("age(age_prev5(", "age(age_prev6(age_prev5(")
    new_stmt = new_stmt.replace(")),\n    ))))), age(", ")),\n    )))))), age(")
    new_stmt = new_stmt.replace("'))))))), 1,", "')))))))), 1,")
    t = t[:i] + new_stmt + t[j:]
    log.append(f"identity-8level-{_itag}: 7-level -> 8-level chain (age_prev6 inserted)")

# family-section comment roll:
rep("# downstream W262+ projection face (probe leg4 verbatim numbers)",
    "# downstream W263+ projection face (probe leg4 verbatim numbers)", 1, "downstream-cmt-roll")

# ---------- 13) P5f ----------
NEW_P5F = r'''# ============ P5f: probe-receipt date face (DATE-STABLE this generation) ============
# disclosed date-stable face: the W262 probe receipt basename keeps the SAME
# date AGAIN (20261017 == 20261017, sixth consecutive date-stable
# generation) -- the blanket P3 already rolled the basename to
# _w262bmc_20261017_probe_receipt.json which IS the correct on-disk name;
# this rep is an identity count-assert (10x), zero heal needed. Position
# stays POST-P5e (the pfcmt chunk needle embeds the pre-replacement basename
# face).
rep(age("_w261bmc_20261017_probe_receipt.json"), "_w262bmc_20261017_probe_receipt.json", 10, "P5f-probe-receipt-date-stable")

'''
sect("# ============ P5f: probe-receipt date face", "# ============ structural output gates", NEW_P5F, "P5f")

# ---------- 14) output gates ----------
NEW_GATES = r'''# ============ structural output gates ============
for needle, want in [
    ("# --- W262 materializer face", 2),
    ("# --- W261 materializer face", 1),
    ('"+ W262 materializer face', 2),
    ("range(16, 262)", 2),
    ("range(17, 262)", 3),
    ("range(244, 262)", 2),
    ("range(243, 262)", 0),
    ("list(range(211, 261)),", 1),
    ("list(range(211, 244))", 1),
    ("list(range(211, 243))", 0),
    ("list(range(244, 261)),", 1),
    ("list(range(243, 261)),", 0),
    ("range(209, 263)", 2),
    ("if w < 262)", 5),
    ("if w < 261)", 1),
    ("m244", 4),
    ("m243", 0),
    ("_w262bmc_20261017_probe_receipt.json", 10),
    ("_w262bmc_freeze_receipt.json", 1),
    ("MSG-20261017-1425-bmc-w262-seat", 7),
    ("693e926b1", 2),
    ("32d28ffb3", 1),
    ("998_535", 1),
    ("572_120", 1),
    ("998,535", 8),
    ("572,120", 8),
    ("(591_701, 593_700)", 1),
    ("(593_701, 593_900)", 1),
    ("W259_W260_W261_bands_respected_A", 1),
    ("W259_W260_W261_bands_respected_B", 1),
    ("B_base_above_W261_tail", 2),
    ("A_staircase_hop_past_W261_B", 8),
    ("W263p_A_naive", 5),
    ("W263p_B_first_clean", 2),
    ("arith_a262", 6),
    ("arith_b262", 6),
    ('"PERPETUAL-N1-W262-SHARD-0"', 1),
    ("n1_w262_results.json", 2),
    ("n1_w262", 4),
    ("n1w262", 2),
    ("PERPETUAL-N1-W262", 7),
    ("_w262bmc", 11),
    ("w244_a", 12),
    ("EIGHTY-SECOND", 3),
    ("TWO HUNDRED AND SIXTY-SECOND", 3),
    ("fiftieth consecutive", 2),
    ("bmc_ordinal=82", 7),
    ("82nd own wave", 3),
    ("r1067 splice window", 3),
    ("r1067", 30),
    ("r1068 freeze window", 1),
    ("W261 finalize one-pass bm-c r1067 window closeout 15:5x", 1),
    ("authored 15:2x", 2),
    ("estate 69", 1),
    ("= 120 rows", 2),
    ("120 parity", 2),
    ("hops=1", None),
    ("1-HOP", None),
    ("ELEVENTH consecutive A-hop", None),
    ("TWELFTH consecutive above-own-A", None),
    ("251/129/81", 1),
    ("252nd", 2),
    ("82nd EXACT", 2),
    ("thirty-three legs", 1),
    ("fifty legs", 1),
    ("== 50", 1),
    # anti-gates: stale faces must be zero
    ("r1065", 0),
    ("r1066", 0),
    ("cf23c4553", 0),
    ("03ab504d7", 0),
    ("996,335", 0),
    ("569,920", 0),
    ("996_335", 0),
    ("569_920", 0),
    ("EIGHTY-FIRST", 0),
    ("TWO HUNDRED AND SIXTY-FIRST", 0),
    ("forty-ninth consecutive", 0),
    ("MSG-20261017-1225", 0),
    ("authored 12:5x", 0),
    ("13:4x", 0),
    ("bmc_ordinal=81", 0),
    ("81st own wave", 0),
    ("251st", 0),
    ("250/129/80", 0),
    ("ELEVENTH consecutive above-own-A", 0),
    ("FIRST A-hop", 0),
    ("seed-gap face ENDS", 0),
    ("589_501..591_500", 0),
    ("591_501..591_700", 2),
    ("589_301..591_300", 0),
    ("589_501..589_700", 0),
    ("589_500", 0),
    ("591_500", 0),
    ("589_301..589_500", 0),
    ("587_301..589_300", 0),
    ("587_101..589_100", 0),
    ("587_301..587_500", 0),
    ("587_300", 0),
    ("589_300", 0),
    ("587_101..587_300", 0),
    ("585_101..587_100", 0),
    ("585_100", 0),
    ("587_100", 0),
    ("584_901", 0),
    ("585_101", 0),
    ("~589_301..589_900", 0),
    ("~591_501..593_500", 0),
    ("(589_501, 591_500)", 0),
    ("(591_501, 591_700)", 0),
    ("== 118", 0),
    ("forty-nine legs", 0),
    ("117 parity", 0),
    ("118 parity", 0),
    ("119 parity", 0),
    ("list(range(242, 258))", 0),
    ("list(range(243, 259))", 0),
    ("w245_a", 0),
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
print("\n".join(log[-10:]))
