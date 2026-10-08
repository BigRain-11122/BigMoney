# -*- coding: utf-8 -*-
"""r888 bm-a generator: builds results/_r888bma_w188_freeze_edits.py by
AST-extracting the r885 W187 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W188 pairs as (new885, S87(new885), cnt) -- old side =
the physical W187 face fragment (probed to dumps this window by
_r888bma_w188_face_probe.py, stage-1 rc0), new side = the S87 W188
fact map applied to that W187 fragment.  Special-case: the mat
parity-chain append pair is constructed explicitly (historical rows
carry, the W187 row appended).  Every derived pair old-side is
verified against the physical dumps BEFORE emission (count == cnt);
S87 negatives verified after.

S87 = the W187->W188 ordered fact map (S86 rolled one generation,
r735 substring-order law + r877 needle dual-face law preserved:
projections consumed BEFORE the band rolls that re-create their
strings; the self-band rolls BEFORE the prior-wave reference rolls
that re-create them; the tail+1 pair order kept (own-A-tail then
prior-B-tail); composite assert pairs BEFORE the bare == rolls they
contain; wave-word cascade (W188 first, then downward) BEFORE the
wave-quirk literal pairs).

S87 LINEAGE CONSTANTS (r795/r845/r849/r852/r863/r867/r869/r874/r878/
r882/r885 precedent, passed through):
  (a) the "wave N-1 = first free number" mat-header label rolls
  forward with its off-by-one quirk (since W165 r795);
  (b) "law sec.4 W188 row, r795" band-facts template stamp keeps its
  r795 (rolls to W188 row, keeps r795);
  (c) "single-window derive (r812 merged the gate legs INTO the
  pre-seat probe...)" stays (historical merge citation);
  (d) the bm-a-owned ordinal word rolls one-hundred-third ->
  one-hundred-fourth (rows 103 + candidate = 104th owned per probe
  leg0);
  (e) mat parity-chain rows W138..W186 keep their historical stamps
  and tuples; the W187 row (the current registered tail) is APPENDED
  with its frozen values (426_204, 428_203)/(428_204, 428_403) and
  its freeze-run session stamp (r307; bm-a r886);
  (f) the "W187 finalize landed one-pass r887" citation rolls its
  wave-word with the values rolling machine-correct to 818,728/
  409,320 this window;
  (g) the sec8 succession-notes window citation rolls r885 ->
  r888 回填窗 (the W187 sec8 succession notes landed the r888
  backfill window -- the honest next-window form, disclosed).

r587 machine-derived facts (every displayed value read from on-disk
receipts / git history this window):
  - pre-seat probe results/_r887bma_w188_probe_receipt.json rc0 ADMIT
    (leg0 registry 185 rows tail W187 ordinal 178 / bma_ordinal 104;
    leg1 naive A 428_204..430_203 REFUSED at its own start by the
    registered W187 B band 428_204..428_403; honest forward walk
    1 hop lands A 428_404..430_403 staircase FORTY-EIGHTH instance
    E36 -- receipt A_semantics machine-cites 'r885 W187 probe leg4 +
    W187 seat MSG leg4 + W187 prereg sec5.5 succession notes
    anticipated and MANDATED this re-derive' (projection and receipt
    ordinals MATCH); B 430_404..430_603 own-A mutual exclusion
    hops=1, naive 428_404..428_603; leg2 conflicts 0; leg3 origin
    vacancy True; leg4 W189+ projection A 430_404..432_403 /
    B 430_604..430_803, B inside A);
  - face probe results/_r888bma_w188_probe_stage1.json rc0 (all four
    W187 faces dumped; this TOK is built from the PHYSICAL probe-
    dumped shapes, r776 law);
  - seat MSG-2026-10-08-1717-bma-w188-seat published on origin at
    943967370 (r887 seat push); r565 law: on origin BEFORE this
    freeze commit; self-ack archive landed the r887 window
    (same-machine consume, live-verified: the seat MSG sits in
    fleet/inbox/processed/ at freeze time);
  - registered W187 freeze sha machine-derived = 79c9a567c (git log
    origin/main --grep "W187 five-face freeze"); W187 finalize landed
    r887 one-pass SAME-chain: ledger head 818,728, merged pool
    K=409,320 (n1_w187_results.json machine-read); W187 sec7/sec8
    settle backfill landed the r888 window (this window, first-leg
    next-window note; the W187 prereg on-disk/origin face
    machine-verified by the prereg buildgen this window);
  - per-wave prereg research/PERPETUAL_N1_W188_PREREG.md built r888
    (buildgen r885-bloodline; banned gate ADMIT 0 verified at
    prereg build; frozen+pushed edec49746 r888; on origin, verified
    live below).

DRY discipline (r833 law 2): zero writes until every gate green -- the
emitted freeze-edits script is the ONLY writer, and it re-asserts
everything live (--dry first)."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r885 pairs --------------------------------
src = io.open(r"results\_r885bma_w187_freeze_edits.py", encoding="utf-8").read()
tree = ast.parse(src)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        return ev(n.left) + ev(n.right)
    if isinstance(n, ast.Name) and n.id == "NL":
        return NL
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


PAIRS = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
       isinstance(node.targets[0], ast.Name) and \
       node.targets[0].id in ("PF_PAIRS", "EN_PAIRS", "MAT_PAIRS", "CL_PAIRS") and \
       isinstance(node.value, ast.List):
        out = []
        for el in node.value.elts:
            assert isinstance(el, ast.Tuple) and len(el.elts) == 3, "pair shape"
            out.append((ev(el.elts[0]), ev(el.elts[1]), ev(el.elts[2])))
        PAIRS[node.targets[0].id] = out

for k in ("PF_PAIRS", "EN_PAIRS", "MAT_PAIRS", "CL_PAIRS"):
    assert k in PAIRS, k + " not extracted"
print("extracted: PF", len(PAIRS["PF_PAIRS"]), "EN", len(PAIRS["EN_PAIRS"]),
      "MAT", len(PAIRS["MAT_PAIRS"]), "CL", len(PAIRS["CL_PAIRS"]))

# ---------- 2. S87 = W187->W188 ordered fact map ---------------------------
S87 = [
    # -- session / finalize / sha composites (longest first) --
    ("W186 finalize one-pass bm-a r884, net chain head 816,528, ",
     "W187 finalize one-pass bm-a r887, net chain head 818,728, "),
    ("finalize one-pass bm-a r884", "finalize one-pass bm-a r887"),
    ("bm-a r884 one-pass", "bm-a r887 one-pass"),
    ("on origin since r884, not re-shipped", "on origin since r887, not re-shipped"),
    ("already on origin since r884,", "already on origin since r887,"),
    ("(gate-derived r885)", "(gate-derived r887)"),
    ("r880 probe leg4", "r885 probe leg4"),
    ("projection + r880 probe", "projection + r885 probe"),
    ("r885 sec8 \u56de\u586b\u7a97 succession", "r888 sec8 \u56de\u586b\u7a97 succession"),
    ("probe leg4 + r885 sec8", "probe leg4 + r888 sec8"),
    ("at fetch (r885 pre-seat", "at fetch (r887 pre-seat"),
    ("r565 law (r885 pre-seat", "r565 law (r887 pre-seat"),
    ("bm-a r885-window self-ack move", "bm-a r887-window self-ack move"),
    ("bm-a r882 freeze ", "bm-a r886 freeze "),
    ("(r307; bm-a r882)", "(r307; bm-a r886)"),
    ("bm-a r885 freeze,", "bm-a r888 freeze,"),
    ("r885 bm-a freeze", "r888 bm-a freeze"),
    ("r885 bm-a] ", "r888 bm-a] "),
    ("r885 receipt machine-read", "r887 receipt machine-read"),
    ("MSG-2026-10-08-1626-bma-w187-seat", "MSG-2026-10-08-1717-bma-w188-seat"),
    ("seat MSG-1626 tail,", "seat MSG-1717 tail,"),
    ("_r885bma_w187_probe_receipt.json", "_r887bma_w188_probe_receipt.json"),
    ("14177b161", "79c9a567c"),
    ("d176af598", "943967370"),
    # -- band geometry (projections FIRST, then the new-band rolls, then
    #    the prior-wave reference rolls that re-create the consumed
    #    strings -- order law: proj consumed before the rolls re-create
    #    them; W187-B -> W188-B BEFORE the W186-B-ref -> W187-B-ref;
    #    naive rolls AFTER both -- every product lands in a slot the
    #    earlier pairs have already vacated) --
    ("428_204..430_203", "430_404..432_403"),
    ("428_404..428_603", "430_604..430_803"),
    ("428_204..428_403", "430_404..430_603"),
    ("426_204..428_203", "428_404..430_403"),
    ("426_004..428_003", "428_204..430_203"),
    ("426_204..426_403", "428_404..428_603"),
    ("426_004..426_203", "428_204..428_403"),
    ("424_004..426_003", "426_204..428_203"),
    ("423_804..425_803", "426_004..428_003"),
    ("424_004..424_203", "426_204..426_403"),
    ("423_804..424_003", "426_004..426_203"),
    # tail+1 pairs (own-A-tail first then prior-B-tail, S76/S77/S79/
    # S80F/S81f/S82f/S83/S84/S85/S86/S87 order kept; tail roll =
    # staircase geometry: prior B tail 428_403 / own-A tail 430_403 --
    # machine-checked at runtime by the asserts)
    ("426_203+1", "428_403+1"),
    ("428_203+1", "430_403+1"),
    ('assert WAVE_CONFIGS[187]["a_seed_base"] == 426_204 == 426_203 + 1, (',
     'assert WAVE_CONFIGS[188]["a_seed_base"] == 428_404 == 428_403 + 1, ('),
    ('assert WAVE_CONFIGS[187]["b_exit_seed_base"] == 428_204 == 428_203 + 1, (',
     'assert WAVE_CONFIGS[188]["b_exit_seed_base"] == 430_404 == 430_403 + 1, ('),
    ("== 426_204 == 426_203 + 1", "== 428_404 == 428_403 + 1"),
    ("== 428_204 == 428_203 + 1", "== 430_404 == 430_403 + 1"),
    ("arith_a186", "arith_a187"),
    ("arith_b186", "arith_b187"),
    ("set(range(426_204, 428_204))", "set(range(428_404, 430_404))"),
    ("set(range(428_204, 428_404))", "set(range(430_404, 430_604))"),
    ('"a_seed_base": 426_204,', '"a_seed_base": 428_404,'),
    ('"b_exit_seed_base": 428_204,', '"b_exit_seed_base": 430_404,'),
    ('187: {"a": (426_204, 428_203), "b_exit": (428_204, 428_403),',
     '188: {"a": (428_404, 430_403), "b_exit": (430_404, 430_603),'),
    # jump phrases (physical fragment shapes, r869 bloodline; all three
    # rolled one generation)
    ("jumps to 428_204, first-clean ", "jumps to 430_404, first-clean "),
    ("jumps to 428_204 -> ", "jumps to 430_404 -> "),
    ("428_204 and lands ", "430_404 and lands "),
    # -- wave-word cascade (W188 first, then downward) --
    ("W188", "W189"),
    ("W187", "W188"),
    ("W186", "W187"),
    ("W185", "W186"),
    ("W184", "W185"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SEVENTY-SEVENTH", "ONE HUNDRED-AND-SEVENTY-EIGHTH"),
    ("engine_owner rows 176", "engine_owner rows 177"),
    ("rows 102 + candidate", "rows 103 + candidate"),
    ("one-hundred-third", "one-hundred-fourth"),
    ("FORTY-SEVENTH", "FORTY-EIGHTH"),
    ("forty-seventh", "forty-eighth"),
    ("816,528", "818,728"),
    ("407,120", "409,320"),
    ("range(17, 187)", "range(17, 188)"),
    ("range(16, 187)", "range(16, 188)"),
    ("below 187 composes", "below 188 composes"),
    ("WAVE_CONFIGS if w < 187)", "WAVE_CONFIGS if w < 188)"),
    ("WAVE_CONFIGS[186]", "WAVE_CONFIGS[187]"),
    ('== pf.N1_BANDS[186]["a"][0]', '== pf.N1_BANDS[187]["a"][0]'),
    ('pf.N1_BANDS[186]["b_exit"][0]', 'pf.N1_BANDS[187]["b_exit"][0]'),
    ('pf.N1_BANDS[186].get("engine_owner")', 'pf.N1_BANDS[187].get("engine_owner")'),
    ("w186_a", "w187_a"),
    ("w186_b", "w187_b"),
    ("n3r1_used186", "n3r1_used187"),
    ('187: {"batch"', '188: {"batch"'),
    ("PERPETUAL_N1_W187_PREREG.md", "PERPETUAL_N1_W188_PREREG.md"),
    ("PERPETUAL-N1-W187", "PERPETUAL-N1-W188"),
    ('"n1_w187"', '"n1_w188"'),
    ('"n1_w187_results.json"', '"n1_w188_results.json"'),
    ("n1w187", "n1w188"),
    ("engine_owner=bm-a, wave 186: ", "engine_owner=bm-a, wave 187: "),
    ("wave 186 = first free number after", "wave 187 = first free number after"),
    ("_set_wave(187)", "_set_wave(188)"),
]


def s87(t):
    for old, new in S87:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W188 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r888bma_w188_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r888bma_w188_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r888bma_w188_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r888bma_w188_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD_R885 = '"registered W185 row parity drift (r307; bm-a r878)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if face == "MAT" and old == APPEND_OLD_R885:
            # special-case: chain append pair (historical rows carry; the
            # W187 row -- the current registered tail -- gets appended).
            n_old = '"registered W186 row parity drift (r307; bm-a r882)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[187] == {"a": (426_204, 428_203),' + NL +
                     '                                    "b_exit": (428_204, 428_403),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W187 row parity drift (r307; bm-a r886)"')
            if dump.count(n_old) != 1:
                fails.append("MAT append-pair old-side count %d != 1: %r" %
                             (dump.count(n_old), n_old))
            out.append((n_old, n_new, 1))
            continue
        n_old, n_new = new, s87(new)
        got = dump.count(n_old)
        if got != cnt:
            fails.append("%s pair old-side count %d != %d: %r" %
                         (face, got, cnt, n_old[:70]))
            continue
        out.append((n_old, n_new, cnt))
    derived[key] = out

if fails:
    print("BUILDGEN FAIL (%d):" % len(fails))
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("pairs derived + verified against physical dumps:",
      {k: len(v) for k, v in derived.items()})

# spot-check the S87 rolls before emission (fail loud, zero emission)
blk_probe = s87(DUMPS["PF"])
assert '188: {"a": (428_404, 430_403), "b_exit": (430_404, 430_603),' in blk_probe
assert "# W188 (bm-a r888 freeze" in blk_probe
assert "FORTY-EIGHTH instance" in blk_probe
assert "# 430_404..432_403 CLEAN hops=0 / B first-clean 430_604..430_803" in blk_probe
assert "W189 A window; W189 freezer MUST re-derive on the post-W188" in blk_probe
entry_probe = s87(DUMPS["EN"])
assert '"a_seed_base": 428_404,' in entry_probe and '"b_exit_seed_base": 430_404,' in entry_probe
assert '"batch": "PERPETUAL-N1-W188",' in entry_probe
print("S87 spot-checks: PASS (pf block + entry seed rolls)")

# ---------- 4. NEG lists (mechanical: every consumed old side is a
# tripwire; append-pair old side excluded -- it legitimately remains
# as the prefix of the chain append) --------------------------------------
NEG = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    toks = []
    for n_old, n_new, _cnt in derived[key]:
        if face == "MAT" and n_old.startswith('"registered W186 row parity drift'):
            continue
        # skip no-op pairs (s87 found no roll -- wave-neutral prose that
        # legitimately remains) and partial-persistence shapes
        if n_new == n_old or n_old in n_new:
            continue
        if n_old not in toks:
            toks.append(n_old)
    # defense-in-depth extras (hand additions from the r885 NEG lists,
    # rolled one generation; harmless if absent)
    extra = {
        "PF": ["d176af598", "r880 probe", "r885 sec8", "r885 pre-seat",
               "_r885bma", "MSG-2026-10-08-1626", "14177b161",
               "816,528", "407,120", "FORTY-SEVENTH", "ONE HUNDRED-AND-SEVENTY-SEVENTH"],
        "EN": ["14177b161", "d176af598", "816,528", "407,120",
               "ONE HUNDRED-AND-SEVENTY-SEVENTH", "rows 176", "r880 probe",
               "_r885bma", "MSG-2026-10-08-1626", "n1w187", "n1_w187",
               "PERPETUAL-N1-W187", "PERPETUAL_N1_W187", "FORTY-SEVENTH",
               "bm-a r882 freeze", "428_204, first-clean"],
        "MAT": ["w186_", "arith_a186", "arith_b186", "n3r1_used186",
                "r880 probe", "r885 pre-seat", "14177b161",
                "ONE HUNDRED-AND-SEVENTY-SEVENTH", "one-hundred-third", "rows 176",
                "rows 102 ", "range(17, 187)", "range(16, 187)",
                "PERPETUAL_N1_W187", "PERPETUAL-N1-W187", "MSG-1626",
                "_r885bma", "bm-a r885-window", "n1w187", "n1_w187",
                "816,528", "407,120"],
        "CL": ["816,528", "407,120", "ONE HUNDRED-AND-SEVENTY-SEVENTH",
               "one-hundred-third", "rows 176", "rows 102 ", "FORTY-SEVENTH",
               "_r885bma", "r885 bm-a] "],
    }[face]
    for t in extra:
        if t not in toks:
            toks.append(t)
    NEG[face + "_NEG"] = toks

print("NEG lists built:", {k: len(v) for k, v in NEG.items()})


def pyrepr(x):
    return repr(x)


def pairs_lit(name, rows):
    lines = [name + " = ["]
    for old, new, cnt in rows:
        lines.append("    (%s, %s, %d)," % (pyrepr(old), pyrepr(new), cnt))
    lines.append("]")
    return NL.join(lines)


def neg_lit(name, toks):
    return name + " = [" + ", ".join(pyrepr(t) for t in toks) + "]"


# ---------- 5. emit the W188 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r888 bm-a W188 freeze edits: four insertions (pf N1_BANDS[188] row +
n1 WAVE_CONFIGS[188] entry + n1 W188 materializer block + n1 W188
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845/r849/
r852/r863/r867/r869/r874/r878/r882/r885/r886 dry-run precedent: full
stale+prose+AST asserts in memory BEFORE any write).

Bloodline: r819/r822/r826/r830/r834/r843/r845/r849/r852/r863/r867/r869/
r874/r878/r882/r885 freeze-edits machinery (r773 pit law freeze-editor compliance +
r776 fragment-needle law + r781 verify-separation law), W188 facts
live-registry-driven (built by _r888bma_w188_freeze_buildgen.py: old
sides = the PHYSICAL W187 face fragments probed to dumps this window,
new sides = the S87 W188 fact map, counts verified pre-emission):
  - pre-seat probe results/_r887bma_w188_probe_receipt.json rc0 ADMIT
    (naive A 428_204..430_203 refused at its own start by the
    registered W187 B band 428_204..428_403; honest forward walk
    1 hop lands A 428_404..430_403 staircase FORTY-EIGHTH instance
    E36 -- receipt A_semantics machine-cites r885 W187 probe leg4 +
    W187 seat MSG leg4 + W187 prereg sec5.5 succession notes anticipated +
    MANDATED this re-derive (projection and receipt ordinals MATCH,
    no divergence this wave); B 430_404..430_603 own-A mutual
    exclusion hops=1, naive 428_404..428_603);
  - face probe results/_r888bma_w188_probe_stage1.json rc0 (all four
    W187 faces dumped; this TOK is built from the PHYSICAL probe-dumped
    shapes, r776 law);
  - seat MSG-2026-10-08-1717-bma-w188-seat published on origin at
    943967370 (r887 seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED -- bm-a r887-window self-ack
    move (same-machine consume; the W188 seat MSG sits in
    fleet/inbox/processed/ at freeze time, live-verified);
  - per-wave prereg research/PERPETUAL_N1_W188_PREREG.md built r888
    (buildgen r885-bloodline; banned gate ADMIT 0 verified at
    prereg build; frozen+pushed edec49746 r888; on origin, verified
    live below);
  - W187 freeze registered sha machine-derived = 79c9a567c (git log
    origin/main --grep "W187 five-face freeze"); W187 finalize landed
    r887 one-pass same-chain: ledger head 818,728, merged pool
    K=409,320 (n1_w187_results.json machine-read); W187 sec7/sec8
    settle backfill landed the r888 window (same window as this
    freeze, first-leg next-window note);
  - lineage constants disclosed (r795/r845/r849/r852/r863/r867/r869/
    r874/r878/r882/r885 precedent, passed through): (a) the "wave N-1 =
    first free number" mat-header label rolls forward with its
    off-by-one quirk (since W165 r795); (b) "law sec.4 W188 row,
    r795" band-facts template stamp keeps its r795; (c) "single-window
    derive (r812 merged the gate legs INTO the pre-seat probe...)"
    stays (historical merge citation); (d) the bm-a-owned ordinal word
    rolls one-hundred-third -> one-hundred-fourth (rows 103 +
    candidate = 104th owned per probe leg0, machine-chosen word form,
    disclosed); (e) mat parity-chain rows W138..W186 keep their
    historical stamps and tuples; the W187 row (the current registered
    tail) is APPENDED with its frozen values
    (426_204, 428_203)/(428_204, 428_403) and its freeze-run session
    stamp (r307; bm-a r886); (f) the "W187 finalize landed one-pass
    r887" citation rolls its wave-word with the values rolling
    machine-correct to 818,728/409,320 this window; (g) the sec8
    succession-notes window citation rolls r885 -> r888 回填窗
    (the W187 sec8 notes landed the r888 backfill window, honest
    next-window form, disclosed).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r888bma_w188_face_probe.py -- four face dumps + stage-1
      receipt, rc0);
  (2) composite band strings tokenized WHOLE (every dotted band /
      seed-base row / jump phrase / projection pair is a single token;
      bare numerals run LAST);
  (3) post-edit full-file start>end malformed-window regex scan on BOTH
      touched files + double-CR scan;
  (4) every projection value re-derived FROM the on-disk probe receipt
      (r587 never-transcribe law);
  (5) r776 fragment-needle law: all needles taken from the PHYSICAL
      probe-dumped shapes;
  (6) r560 insert-after-last-registered-row + pre-edit live registry
      parity + origin anti-collision pre-check + write-time re-check
      (r530/r687: fetch + origin carries no W188 registration before
      this freeze);
  (7) AST gate after every edit batch (r580/r781)."""
import ast
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DRY = "--dry" in sys.argv
PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = '"engine_owner": "bm-a"},'
NL = "\\r\\n"
IND23 = " " * 23
IND10 = " " * 10

fail = []


def check(cond, msg):
    if not cond:
        fail.append(msg)
        print("FAIL:", msg)


# ---- receipts / machine-derived facts --------------------------------
probe = json.load(open(r"results\\_r887bma_w188_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "428404_430403", "B": "430404_430603"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [428404, 430403], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [430404, 430603], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 185 and probe["legs"]["leg0"]["tail"] == "W187",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 178 and probe["legs"]["leg0"]["bma_ordinal"] == 104,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W189p_A"] == "430404..432403"
      and probe["legs"]["leg4"]["W189p_B"] == "430604..430803",
      "leg4 W189+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('188: {"a": (428_404' not in pf_o, "origin pf already carries W188 row")
check("W188 (bm-a r888 freeze" not in pf_o, "origin pf carries W188 block")
check('188: {"batch"' not in n1_o, "origin n1 already carries W188 entry")
check("# --- W188 materializer face" not in n1_o, "origin n1 carries W188 mat")
check('"r888 bm-a] "' not in n1_o, "origin n1 carries W188 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-1717-bma-w188-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "943967370", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-1717-bma-w188-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w187_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W187 five-face freeze"],
    capture_output=True).stdout.decode().strip()
check(w187_freeze_sha == "79c9a567c", "W187 freeze sha mismatch: " + w187_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 185, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[187] == {"a": (426_204, 428_203),
                              "b_exit": (428_204, 428_403),
                              "engine_owner": "bm-a"}, "live W187 row drift")
check(188 not in pfmod.N1_BANDS, "live N1_BANDS already has 188")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W188_PREREG.md")),
      "W188 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W188_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W188 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r888bma_w188_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r888bma_w188_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r888bma_w188_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r888bma_w188_probe_n1_claim.txt", encoding="utf-8",
                newline="").read()
check(mat.endswith("_set_wave(2)" + NL + "    "), "mat dump tail unexpected")
mat = mat[: -len(NL + "    ")]  # strip the T-141 line indent ride-along
check(mat.endswith("_set_wave(2)"), "mat core tail unexpected")


def vmap(src, pairs, negatives, name):
    for old, new, cnt in pairs:
        got = src.count(old)
        if got != cnt:
            check(False, "%s pair count %d != %d: %r" % (name, got, cnt, old[:60]))
            continue
        src = src.replace(old, new)
    for neg in negatives:
        check(neg not in src, "%s stale token remains: %r" % (name, neg[:60]))
    return src

'''

BLOCKS = '''
blk188 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry188 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat188 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim188 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W188 block after the W187 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk188 + NL + "}", 1)

# n1 entry: after the W187 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry188 + NL + IND23 + "}", 1)

# n1 mat: insert the W188 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat188 + NL + seg, 1)

# n1 claim: insert the W188 attribution after the W187 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r885 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r885 bm-a] "' + NL + claim188 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W188 presence + W187 anti-vanish (r560 law)
checks = [
    (pfnew, '188: {"a": (428_404, 430_403), "b_exit": (430_404, 430_603),', 1),
    (pfnew, '187: {"a": (426_204, 428_203), "b_exit": (428_204, 428_403),', 1),
    (pfnew, "# W188 (bm-a r888 freeze", 1),
    (pfnew, "# W187 (bm-a r885 freeze", 1),
    (n1new, '188: {"batch": "PERPETUAL-N1-W188",', 1),
    (n1new, '187: {"batch": "PERPETUAL-N1-W187",', 1),
    (n1new, "# --- W188 materializer face", 1),
    (n1new, "# --- W187 materializer face", 1),
    (n1new, '"r888 bm-a] "', 1),
    (n1new, '"r885 bm-a] "', 1),
    (n1new, '"a_seed_base": 428_404,', 1),
    (n1new, '"b_exit_seed_base": 430_404,', 1),
    (n1new, "n1_w188", 4),
    (n1new, "PERPETUAL_N1_W188_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W189+ projection prose present in the new W188 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W188+ per r845 precedent, n1 fragment =
# next-wave W189+)
check("# W188+ projection (gate-derived r887)" in pfnew,
      "pf W188+ projection head missing")
check('probe_receipt.json; W189+ projection "' in n1new,
      "n1 W189+ projection head fragment missing")
check("# 430_404..432_403 CLEAN hops=0 / B first-clean 430_604..430_803" in pfnew,
      "pf W189p prose missing")
check("W189 A window; W189 freezer MUST re-derive on the post-W188" in pfnew,
      "pf W189 freezer prose missing")
check('"W189 A window; W189 freezer MUST re-derive on the "' in n1new,
      "n1 W189 freezer fragment missing")
check('"W188 B band 430_404..430_603 will refuse the naive "' in n1new,
      "n1 W188-band refuse fragment missing")

# malformed-window scans (r819 bloodline regex: the XXX_YYY..XXX_YYY
# 3-digit-triplet window shape, first-triplet comparison -- the proven
# scan; broader shapes hit pre-existing prose false positives) +
# double-CR / triple-LF scans
pat = re.compile(r"(\\d{3})_(\\d{3})\\.\\.(\\d{3})_(\\d{3})")
for name, txt in (("pf", pfnew), ("n1", n1new)):
    bad = [mm.group() for mm in pat.finditer(txt)
           if int(mm.group(3)) < int(mm.group(1))]
    check(not bad, "%s malformed windows: %s" % (name, bad[:5]))
    check("\\r\\r" not in txt, "%s double-CR present" % name)
    check("\\n\\n\\n" not in txt, "%s triple-LF present" % name)
print("malformed-window scans: CLEAN both files")

if fail:
    print("RESULT: FAIL (%d) -- zero writes" % len(fail))
    for f in fail:
        print("  -", f)
    sys.exit(1)

if DRY:
    print("DRY-RUN PASS: all gates green, zero writes "
          "(pf %d->%d B, n1 %d->%d B)" % (len(pfsrc), len(pfnew),
                                          len(n1src), len(n1new)))
    sys.exit(0)

# ---- write-time re-check (r687 law): re-fetch + origin vacancy re-verify
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o2 = subprocess.run(["git", "show", "origin/main:" + PF],
                       capture_output=True).stdout.decode("utf-8", "replace")
n1_o2 = subprocess.run(["git", "show", "origin/main:" + N1],
                       capture_output=True).stdout.decode("utf-8", "replace")
check('188: {"a": (428_404' not in pf_o2, "write-time: origin pf carries W188")
check('188: {"batch"' not in n1_o2, "write-time: origin n1 carries W188")
if fail:
    print("RESULT: FAIL at write-time re-check (%d) -- zero writes" % len(fail))
    for f in fail:
        print("  -", f)
    sys.exit(1)

# ---- live writes: n1 FIRST then pf (engine queue derive keys off the
# pf N1_BANDS row -- a row without a WAVE_CONFIGS entry would be a dead
# face for one tick; an entry without a row never ignites (safe order) --
# r666 law window face) ----------------------------------------------------
io.open(N1, "w", encoding="utf-8", newline="").write(n1new)
io.open(PF, "w", encoding="utf-8", newline="").write(pfnew)
print("LIVE WRITES DONE: pf %d->%d B, n1 %d->%d B" %
      (len(pfsrc), len(pfnew), len(n1src), len(n1new)))
print("freeze edits rc0: 4 insertions landed (pf row + n1 entry + mat + claim)")
'''

parts = [HDR,
         pairs_lit("PF_PAIRS", derived["PF_PAIRS"]), "",
         pairs_lit("EN_PAIRS", derived["EN_PAIRS"]), "",
         pairs_lit("MAT_PAIRS", derived["MAT_PAIRS"]), "",
         pairs_lit("CL_PAIRS", derived["CL_PAIRS"]), "",
         neg_lit("PF_NEG", NEG["PF_NEG"]), "",
         neg_lit("EN_NEG", NEG["EN_NEG"]), "",
         neg_lit("MAT_NEG", NEG["MAT_NEG"]), "",
         neg_lit("CL_NEG", NEG["CL_NEG"]),
         BLOCKS]
out = NL.join(parts)
io.open(r"results\_r888bma_w188_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r888bma_w188_freeze_edits.py", len(out), "bytes")
