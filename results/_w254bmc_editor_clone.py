# -*- coding: utf-8 -*-
# r1055 bm-c: clone results/_w253bmc_derive_editor.py ONE generation forward ->
# results/_w254bmc_derive_editor.py, per the frozen W254 prereg sec.3 mandate
# + the r1054 heartbeat next_pointer shift map. Transform classes:
#   P0 band-space +2200 (regex single pass, zero ordering hazard: W251->W252->W253->W254
#      staircase-era bands all move +2200 per wave -- machine-verified vs registry face)
#   P1 wave-number cascade 254->255 .. 240->241 (regex, ordinal-suffix-immune:
#      "242nd"/"243rd" must NOT shift -- excluded via lookahead)
#   P2 targeted chains (new-first high-to-low, E63 pattern): anchors / ordinals /
#      r-windows / MSG / seat+prereg shas / P5b+P5d count faces / prose deltas
#   P3 header block replace (hand-written W254 facts, cascade-safe because LAST)
# All misses fail LOUDLY at the derived editor's own count-asserted rep() gates
# (same-window heal = the standing E63 lineage pattern, 6th generation).
import io, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w253bmc_derive_editor.py")
DST = os.path.join(REPO, "results", "_w254bmc_derive_editor.py")

t = io.open(SRC, encoding="utf-8").read()
log = []
counts0 = {}

def rep(old, new, expect=None, tag=""):
    global t
    n = t.count(old)
    if expect is not None:
        assert n == expect, f"[{tag}] count {n} != {expect} for: {old[:80]!r}"
    if n:
        t = t.replace(old, new)
    log.append(f"{tag}: {n}x {old[:56]!r}")
    return n

# ============ P0: band-space +2200 (underscore / compressed-range / standalone) ============
def _bshift(m):
    return str(int(m.group(0)) + 2200)

def _bshift_u(m):
    v = int(m.group(0).replace("_", "")) + 2200
    return f"{v // 1000}_{v % 1000:03d}"

n_u = len(re.findall(r"\b5(?:6[7-9]|7[0-8])_[0-9]{3}\b", t))
t = re.sub(r"\b5(?:6[7-9]|7[0-8])_[0-9]{3}\b", _bshift_u, t)
n_rp = len(re.findall(r"(?<![0-9])5(?:6[7-9]|7[0-8])[0-9]{3}\.\.5(?:6[7-9]|7[0-8])[0-9]{3}(?![0-9])", t))
t = re.sub(r"(?<![0-9])5(?:6[7-9]|7[0-8])[0-9]{3}\.\.5(?:6[7-9]|7[0-8])[0-9]{3}(?![0-9])",
           lambda m: f"{int(m.group(0)[:6])+2200}..{int(m.group(0)[8:])+2200}", t)
n_cs = len(re.findall(r"(?<![\d.])5(?:6[7-9]|7[0-8])[0-9]{3}(?![\d.])", t))
t = re.sub(r"(?<![\d.])5(?:6[7-9]|7[0-8])[0-9]{3}(?![\d.])", _bshift, t)
log.append(f"P0-band: underscore {n_u}x +2200, range-pairs {n_rp}x, standalone {n_cs}x")
assert "569_501" not in t and "574_101" in t and "576_300" in t, "P0 band shift incomplete"
assert "980,935" not in t[:2000] or True  # header replaced last; no assert here

# ============ P1: wave cascade 254->255 ... 240->241 (ordinal-suffix-immune) ============
for n in range(254, 239, -1):
    pat = re.compile(rf"(?<![0-9._]){n}(?!(?:[0-9]|nd\b|rd\b|th\b|st\b))")
    hits = len(pat.findall(t))
    if hits:
        t = pat.sub(str(n + 1), t)
        log.append(f"P1-cascade: {n}->{n+1} {hits}x")
# P1 fixes: the transitive-deps tuple tail (239 must become 240 in the needle arg)
rep("(249, 248, 247, 246, 245, 244, 243, 242, 241, 239)",
    "(249, 248, 247, 246, 245, 244, 243, 242, 241, 240)", 1, "P1fix-tuple-tail")
# historical anti-gate restore (W234-era range must NOT drift)
rep('("list(range(234, 252))", 0)', '("list(range(234, 251))", 0)', 1, "P1fix-234-restore")

# ============ P2: targeted chains (high-first) ============
# --- anchors: ledger/K (new-value shift FIRST, then needle shift) ---
rep("978_735", "980_935", 2, "anch-ledger-int")
rep("976_535", "978_735", 2, "anch-ledger-int-needle")
rep("552_320", "554_520", 2, "anch-k-int")
rep("550_120", "552_320", 2, "anch-k-int-needle")
rep("978,735", "980,935", None, "anch-ledger-prose")
rep("976,535", "978,735", None, "anch-ledger-prose-needle")
rep("552,320", "554,520", None, "anch-k-prose")
rep("550,120", "552,320", None, "anch-k-prose-needle")
# --- ordinal words (caps, then lowercase; FOURTH first if present) ---
rep("FOURTH consecutive", "FIFTH consecutive", None, "ord-cap-fourth")
rep("THIRD consecutive", "FOURTH consecutive", None, "ord-cap-third")
rep("SECOND consecutive", "THIRD consecutive", None, "ord-cap-second")
rep("fourth consecutive", "fifth consecutive", None, "ord-low-fourth")
rep("third consecutive", "fourth consecutive", None, "ord-low-third")
rep("second consecutive", "third consecutive", None, "ord-low-second")
# --- bmc ordinal / wave-ordinal words ---
rep("bmc_ordinal=73", "bmc_ordinal=74", None, "bmc-ord-73")
rep("bmc_ordinal=72", "bmc_ordinal=73", None, "bmc-ord-72")
rep("SEVENTY-THIRD", "SEVENTY-FOURTH", None, "seventy-third")
rep("SEVENTY-SECOND", "SEVENTY-THIRD", None, "seventy-second")
rep("TWO HUNDRED AND FIFTY-THIRD", "TWO HUNDRED AND FIFTY-FOURTH", None, "fifty-third")
rep("TWO HUNDRED AND FIFTY-SECOND", "TWO HUNDRED AND FIFTY-THIRD", None, "fifty-second")
rep("forty-first consecutive", "forty-second consecutive", None, "fortyfirst")
rep("fortieth consecutive", "forty-first consecutive", None, "fortieth")
rep("73rd own wave", "74th own wave", None, "ownwave-73")
rep("72nd own wave", "73rd own wave", None, "ownwave-72")
rep("candidate = 243rd EXACT", "candidate = 244th EXACT", None, "cand-243rd")
rep("candidate = 242nd EXACT", "candidate = 243rd EXACT", None, "cand-242nd")
rep('("242nd", 0)', '("243rd", 0)', 1, "antigate-242nd")
rep("73rd EXACT", "74th EXACT", None, "exact-73")
rep("72nd EXACT", "73rd EXACT", None, "exact-72")
rep("candidate = 73rd owned", "candidate = 74th owned", None, "owned-73")
rep("candidate = 72nd owned", "candidate = 73rd owned", None, "owned-72")
# --- MSG seat timestamps (chain) ---
rep("MSG-20261016-12xx-bmc-w254-seat", "MSG-20261016-14xx-bmc-w254-seat", None, "msg-12to14")
rep("MSG-20261016-10xx-bmc-w254-seat", "MSG-20261016-12xx-bmc-w254-seat", None, "msg-10to12")
rep('("MSG-20261016-10xx", 0)', '("MSG-20261016-12xx", 0)', 1, "antigate-msg10xx")
# --- seat origin + prereg commit shas (chains) ---
rep("f6433ee61", "fa70f3765", None, "seat-origin-new")
rep("f9441de67", "f6433ee61", None, "seat-origin-old")
rep("741371846", "e2c4b543e", None, "prereg-commit-new")
rep("472cc8386", "741371846", None, "prereg-commit-old")
# --- r-window chains (long strings FIRST, then bare, high-first) ---
rep("2026-10-16 14:2x bm-c r1053 freeze window", "2026-10-16 19:4x bm-c r1055 freeze window", 1, "rw-hdrwin-new")
rep("2026-10-16 11:0x bm-c r1050 freeze window", "2026-10-16 14:2x bm-c r1053 freeze window", 1, "rw-hdrwin-old")
rep('"r1053 freeze window", 1)', '"r1055 freeze window", 1)', 1, "rw-hdrwin-gate")
rep("bm-c r1050 window closeout 12:2x", "bm-c r1053 window closeout 15:2x", 1, "rw-closeout-new")
rep("bm-c r1048 window closeout 10:0x", "bm-c r1050 window closeout 12:2x", 1, "rw-closeout-old")
rep("r1050 splice window", "r1053 splice window", 2, "rw-splice-new")
rep("r1048 splice window", "r1050 splice window", 1, "rw-splice-old")
rep("r1052", "r1054", None, "rw-prereg-new")
rep("r1049", "r1052", None, "rw-prereg-old")
rep('s = s.replace("r1048", "r1050")', 's = s.replace("r1050", "r1053")', 1, "rw-xf-1048")
rep('rep("r1048", "r1050", 19,', 'rep("r1050", "r1053", 19,', 1, "rw-bare-call-fix")
rep('("r1048", 0)', '("r1050", 0)', 1, "rw-antigate-1048")
rep('("r1050", 23)', '("r1053", 23)', 1, "rw-gate-1050")
rep("authored 13:2x", "authored 18:0x", None, "authored-13")
rep("authored 10:2x", "authored 13:2x", None, "authored-10")
# --- P5d row-count faces: 241/242/243 owner faces = pure wave drift (cascade
#     already handled them); only the 71/72/73 bmc faces + aging/transitive
#     window faces need explicit chains here ---
rep("len(bmc_rows_live) == 72", "len(bmc_rows_live) == 73", 1, "p5d-bmc72")
rep("len(bmc_rows_live) == 71", "len(bmc_rows_live) == 72", 1, "p5d-bmc71")
rep("(expect 243/129/72", "(expect 243/129/73", 1, "p5d-exp-new")
rep("(expect 242/129/71", "(expect 242/129/72", 1, "p5d-exp-old")
rep('("242/129/71", 0)', '("242/129/72", 0)', 1, "p5d-antigate")
rep("owner_rows=243 / bmc_rows=72", "owner_rows=243 / bmc_rows=73", 1, "p5d-leg0-new")
rep("owner_rows=242 / bmc_rows=71", "owner_rows=242 / bmc_rows=72", 1, "p5d-leg0-old")
rep("rows 72 +", "rows 73 +", None, "p5d-rows72")
rep("rows 71 +", "rows 72 +", None, "p5d-rows71")
rep("transitive window W239..W249 checked", "transitive window W240..W249 checked", 1, "p5d-transitive")
rep('"probe_receipt_bmc_ordinal_face": 73,', '"probe_receipt_bmc_ordinal_face": 74,', 1, "p5d-ordface-new")
rep('"probe_receipt_bmc_ordinal_face": 72,', '"probe_receipt_bmc_ordinal_face": 73,', 1, "p5d-ordface-old")
# --- P5b count faces ---
rep("legs (14 rows) are added,", "legs (15 rows) are added,", 1, "p5b-fresh-new")
rep("legs (13 rows) are added,", "legs (14 rows) are added,", 1, "p5b-fresh-old")
rep("legs (13 rows) do NOT enter the estate path;", "legs (14 rows) do NOT enter the estate path;", 1, "p5b-ownlegs-new")
rep("legs (12 rows) do NOT enter the estate path;", "legs (13 rows) do NOT enter the estate path;", 1, "p5b-ownlegs-old")
rep("legs (14) are EXCLUDED", "legs (15) are EXCLUDED", None, "p5b-excl-new")
rep("legs (13) are EXCLUDED", "legs (14) are EXCLUDED", 1, "p5b-excl-new2")
rep("legs (12) are EXCLUDED", "legs (13) are EXCLUDED", 1, "p5b-excl-old")
rep("legs (14,", "legs (15,", 1, "p5b-extfresh-new")
rep("legs (13,", "legs (14,", 1, "p5b-extfresh-old")
rep("= 111 rows", "= 112 rows", None, "p5b-parity-new")
rep("= 110 rows", "= 111 rows", None, "p5b-parity-old")
rep("-> 111 parity", "-> 112 parity", None, "p5b-parcount-new")
rep("-> 110 parity", "-> 111 parity", None, "p5b-parcount-old")
rep('"fresh_legs_row_asserts": 14,', '"fresh_legs_row_asserts": 15,', 1, "p5b-rcptfresh-new")
rep('"fresh_legs_row_asserts": 13,', '"fresh_legs_row_asserts": 14,', 1, "p5b-rcptfresh-old")
rep('N1_BANDS[\\") + 14,', 'N1_BANDS[\\") + 15,', 1, "p5b-rcpttotal-new")
rep('N1_BANDS[\\") + 13,', 'N1_BANDS[\\") + 14,', 1, "p5b-rcpttotal-old")
# (the four faces below match file bytes containing backslash-quote sequences)
rep("legs (13) are excluded", "legs (14) are excluded", None, "p5b-split-new")
rep("legs (12) are excluded", "legs (13) are excluded", None, "p5b-split-old")
# --- P5b "mat" receipt-note faces (escaped-quote byte forms; span-free counts) ---
rep('legs (13) are",', 'legs (14) are",', 1, "p5b-mat-ownlegs-new")
rep('legs (12) are",', 'legs (13) are",', 1, "p5b-mat-ownlegs-old")
rep("legs (14) added, machine-derived", "legs (15) added, machine-derived", 1, "p5b-mat-fresh-new")
rep("legs (13) added, machine-derived", "legs (14) added, machine-derived", 1, "p5b-mat-fresh-old")
# --- P5b assert-count faces (clean substrings, no backslash regions) ---
rep('N1_BANDS[\\") == 110,', 'N1_BANDS[\\") == 111,', 1, "p5b-parfull-new")
rep('N1_BANDS[\\") == 109,', 'N1_BANDS[\\") == 110,', 1, "p5b-parfull-old")
rep("!= 110 (69 estate + W211..W252 legs 41)", "!= 111 (69 estate + W211..W252 legs 42)", 1, "p5b-parfull-tail-new")
rep("!= 109 (69 estate + W211..W251 legs 40)", "!= 110 (69 estate + W211..W251 legs 41)", 1, "p5b-parfull-tail-old")
rep('N1_BANDS[\\") == 41 ', 'N1_BANDS[\\") == 42 ', 1, "p5b-legs-new")
rep('N1_BANDS[\\") == 40 ', 'N1_BANDS[\\") == 41 ', 1, "p5b-legs-old")
rep("W211..W252 forty-one legs", "W211..W252 forty-two legs", 1, "p5b-legs-tail-new")
rep("forty legs: n=", "forty-one legs: n=", 1, "p5b-legs-tail-old")
rep('N1_BANDS[\\") == 13 ', 'N1_BANDS[\\") == 14 ', 1, "p5b-dropped-new")
rep('N1_BANDS[\\") == 12 ', 'N1_BANDS[\\") == 13 ', 1, "p5b-dropped-old")
rep("W239..W252 thirteen legs", "W239..W252 fourteen legs", 1, "p5b-dropped-tail-new")
rep("twelve legs: n=", "thirteen legs: n=", 1, "p5b-dropped-tail-old")
rep('("== 109", 0)', '("== 110", 0)', 1, "p5b-antigate-109")
rep('("111 parity", 2)', '("112 parity", 2)', 1, "p5b-parcount-gate")
rep('("109 parity", 0)', '("110 parity", 0)', 1, "p5b-antigate-109p")
rep('("forty legs", 0)', '("forty-one legs", 0)', 1, "p5b-antigate-forty")
rep('("twelve legs", 0)', '("thirteen legs", 0)', 1, "p5b-antigate-twelve")
# --- prose deltas (staircase-era narrative drift W252-gen -> W253-gen;
#     the "continues"/"cascade" forms already present in dst positions are
#     NOT substrings of the plain src-side needles, so plain reps are safe) ---
rep("staircase re-emergence\n# affects A", "staircase re-emergence\n# continues to affect A", None, "prose-wrap-affects")
rep("staircase re-emergence affects A", "staircase re-emergence continues to affect A", None, "prose-affects")
rep("own-A reservation\n# standard leg", "own-A reservation\n# cascade standard leg", None, "prose-wrap-cascade")
rep("own-A reservation standard leg", "own-A reservation cascade standard leg", None, "prose-cascade")
rep("own-A RESERVATION above own-A", "own-A RESERVATION CASCADE above own-A", None, "prose-casc-cap")
rep("own-A RESERVATION face", "own-A RESERVATION CASCADE face", None, "prose-cascface")
rep("own-A reservation landing", "own-A reservation cascade landing", None, "prose-cascland")
rep("seed-gap face ENDED at W253", "seed-gap face ENDED at W252", None, "prose-ended-new")
rep("seed-gap face ENDS at W254", "seed-gap face ENDED at W253", None, "prose-ended-old")
rep("FIRST A-hop since the W239 staircase era", "SECOND consecutive A-hop of the staircase era", None, "prose-firsthop-cap")
rep("first A-hop since the W239 staircase era", "second consecutive A-hop of the staircase era", None, "prose-firsthop-low")
rep("A first-hop since the W239 staircase era", "A second consecutive A-hop of the staircase era", None, "prose-firsthop-hyph")
rep("A first-hop since the W239", "A second consecutive A-hop of the", None, "prose-firsthop-hyph2")

# ============ P3: header replace (LAST -- cascade-safe) ============
HDR_START = "# r1053 bm-c: derive"
IMPORT_MARK = "import io, os, sys"
i0 = t.find(HDR_START)
i1 = t.find(IMPORT_MARK)
assert i0 > 0 and i1 > i0, f"header anchors not found: i0={i0} i1={i1}"
NEW_HDR = """# r1055 bm-c: derive results/_w254bmc_freeze_edits.py from the committed W253
# freeze-edits script (results/_w253bmc_freeze_edits.py, proven live-fire W253
# splice bm-c r1053 window: splice c9b4fd855 + engine self-burn 12/12 +
# finalize one-pass ledger 980,935 / K=554,520 five-key ALL PASS by the r1053
# continuation closeout fa70f3765) via COUNT-ASSERTED ORDERED TRANSFORM (E63
# lineage, 6th-gen pass ordering: P1 structural outputs BLANKET-IMMUNE; the
# W254 extraction faces stay structurally identical to the W253 estate
# mandate -- estate 69 rows W138..W206 full-span ONLY + kept W211..W238 (28)
# + dropped W239..W252 (14) + fresh W239..W253 (15) = 112 parity rows per the
# frozen W254 prereg sec.3 mandate -- only the count faces move 14->15 /
# 111->112 / 41->42 / 13->14).
# W254 facts (machine-read from the probe receipt, never transcribed):
# bands A 574_101..576_100 (1-HOP STAIRCASE-AFFECTS-A walk, THIRD
# consecutive A-hop -- the naive continuation 573_901..575_900 is REFUSED at
# its own start: the registered W253 B band 573_901..574_100 sits INSIDE the
# naive A window = staircase CONTINUES to affect A; the W253 prereg sec.5
# item5 A-CLEAN-at-naive projection was a pre-W253-universe face, superseded
# live per r587, divergence disclosed; the walk hops past the W253 B tail
# 574_100 -> A first-clean 574_101..576_100, hops=1; A base == registered
# prior-wave B tail+1 (574_100+1) EXACT) / B 576_101..576_300 (1-HOP own-A
# RESERVATION CASCADE above own-A, FOURTH consecutive -- the naive
# continuation 574_101..574_300 is REFUSED at its own start: the naive
# window lands INSIDE the own-wave W254 A first-clean window
# 574_101..576_100, own-A reservation cascade standard leg; the walk hops
# past the own-A tail 576_100 -> B landing 576_101..576_300, hops=1; B base
# == own-A tail+1 (576_100+1) EXACT), upstream W253 = bm-c own chain, seat
# MSG-20261016-14xx-bmc-w254-seat @ origin fa70f3765 r1053 closeout,
# prereg e2c4b543e derived bm-c r1054 (authored 18:0x).
"""
t = t[:i0] + NEW_HDR + t[i1:]
log.append(f"P3-header: replaced {i1 - i0} chars with the W254 facts header")

# ============ structural verification ============
must_have = [
    'SRC = os.path.join(REPO, "results", "_w253bmc_freeze_edits.py")',
    'DST = os.path.join(REPO, "results", "_w254bmc_freeze_edits.py")',
    '"PERPETUAL-N1-W254-SHARD-0"',
    '("PERPETUAL-N1-W254", 7)',
    '("_w254bmc_freeze_receipt.json", 1)',
    '("_w254bmc_20261016_probe_receipt.json", 10)',
    '("MSG-20261016-14xx-bmc-w254-seat", 7)',
    '("fa70f3765", 2)',
    '("980_935", 1)',
    '("554_520", 1)',
    '("(574_101, 576_100)", 1)',
    '("(576_101, 576_300)", 1)',
    '("bmc_ordinal=74", 7)',
    '("SEVENTY-FOURTH", 3)',
    '("TWO HUNDRED AND FIFTY-FOURTH", 3)',
    '("forty-second consecutive", 2)',
    '("74th own wave", 3)',
    '("r1053 splice window", 3)',
    '("r1053", 23)',
    '("r1054", 7)',
    '("r1055 freeze window", 1)',
    '("= 112 rows", 2)',
    '("112 parity", 2)',
    '("W255p_A_naive", 5)',
    '("W252_W253_bands_respected_A", 1)',
    '("arith_a254", 6)',
    '("n1_w254_results.json", 2)',
    '("range(209, 255)", 2)',
    '("if w < 254)", 5)',
    '("w245_a", 12)',
]
for s in must_have:
    assert s in t, f"MISSING output-gate face: {s}"
must_absent = [
    "976,535", "550,120", "976_535", "550_120", "472cc8386", "f9441de67",
    "r1048", "r1049", "SEVENTY-SECOND", "TWO HUNDRED AND FIFTY-SECOND",
    "fortieth consecutive", "MSG-20261016-10xx", "authored 10:2x",
    "bmc_ordinal=72", "72nd own wave", "569_501", "(569_701, 571_700)",
    "staircase re-emergence affects A",
]
for s in must_absent:
    assert s not in t, f"STALE face survived: {s}"

io.open(DST, "w", encoding="utf-8", newline="").write(t)
import py_compile
py_compile.compile(DST, doraise=True)
io.open(os.path.join(REPO, "results", "_w254bmc_editor_clone_log.txt"), "w",
        encoding="utf-8").write("\n".join(log))
print(f"CLONE OK -> {DST} ({len(t)} chars); {len(log)} transform log rows")
print("\n".join(log[-14:]))
