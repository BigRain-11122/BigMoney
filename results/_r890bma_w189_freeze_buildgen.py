# -*- coding: utf-8 -*-
"""r890 bm-a generator: builds results/_r890bma_w189_freeze_edits.py by
AST-extracting the r888 W188 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W189 pairs as (new888, S88(new888), cnt) -- old side =
the physical W188 face fragment (probed to dumps by
_r890bma_w189_face_probe.py first-leg r890, stage-1 rc0), new side =
the S88 W189 fact map applied to that W188 fragment.  Special-case:
the mat parity-chain append pair is constructed explicitly
(historical rows carry, the W188 row appended with its frozen values
(428_404, 430_403)/(430_404, 430_603) and its freeze-run session
stamp (r307; bm-a r888)).  Every derived pair old-side is verified
against the physical dumps BEFORE emission (count == cnt); S88
negatives verified after.

S88 = the W188->W189 ordered fact map (S87 rolled one generation,
r735 substring-order law + r877 needle dual-face law preserved:
projections consumed BEFORE the band rolls that re-create their
strings; the self-band rolls BEFORE the prior-wave reference rolls;
the tail+1 pair order kept; composite assert pairs BEFORE the bare ==
rolls they contain; wave-word cascade (W189 first, then downward)
BEFORE the wave-quirk literal pairs).

S88 LINEAGE CONSTANTS (r795/r845/r849/r852/r863/r867/r869/r874/r878/
r882/r885/r888 precedent, passed through):
  (a) the "wave N-1 = first free number" mat-header label rolls
  forward with its off-by-one quirk (since W165 r795);
  (b) "law sec.4 W189 row, r795" band-facts template stamp keeps its
  r795;
  (c) "single-window derive (r812 merged the gate legs INTO the
  pre-seat probe...)" stays (historical merge citation);
  (d) the bm-a-owned ordinal word rolls one-hundred-fourth ->
  one-hundred-fifth (rows 104 + candidate = 105th owned per probe
  leg0);
  (e) mat parity-chain rows W138..W187 keep their historical stamps
  and tuples; the W188 row (the current registered tail) is APPENDED
  with its frozen values (428_404, 430_403)/(430_404, 430_603) and
  its freeze-run session stamp (r307; bm-a r888);
  (f) the "W188 finalize landed one-pass r889" citation rolls its
  wave-word with the values rolling machine-correct to 820,928/
  411,520 this window;
  (g) the sec8 succession-notes window citation rolls r888 ->
  r890 回填窗 (the W188 sec8 succession notes landed the r890
  backfill window -- commit 43322a984 pre-rebase sha, first-leg
  family form, disclosed);
  (h) seat-face semantic change disclosed: the W189 seat self-ack
  archive move = bm-a r889-window archive move (cross-window consume
  by the r889 finalize window -- r889 round commit 0061ab8c7 'W189
  seat inbox processed'; the r888 generation's same-window self-ack
  pattern does NOT hold this wave, honest form);
  (i) the W189 prereg freeze landed this window (r890, commit
  632761894 post-rebase; the prereg buildgen + build + DRY 50/50
  green same window; on origin verified live below).

r587 machine-derived facts (every displayed value read from on-disk
receipts / git history this window):
  - pre-seat probe results/_r888bma_w189_probe_receipt.json rc0 ADMIT
    (leg0 registry 186 rows tail W188 ordinal 179 / bma_ordinal 105;
    leg1 naive A 430_404..432_403 REFUSED at its own start by the
    registered W188 B band 430_404..430_603; honest forward walk 1
    hop lands A 430_604..432_603 staircase FORTY-NINTH instance E36
    -- receipt A_semantics machine-cites 'r887 W188 probe leg4 +
    W188 materializer W189+ projection anticipated and MANDATED this
    re-derive' (projection and receipt ordinals MATCH); B
    432_604..432_803 own-A mutual exclusion hops=1, naive
    430_604..430_803; leg2 conflicts 0; leg3 origin vacancy True;
    leg4 W190+ projection A 432_604..434_603 / B 432_804..433_003,
    B inside A);
  - face probe results/_r890bma_w189_probe_stage1.json rc0 (all four
    W188 faces dumped first-leg r890; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-1815-bma-w189-seat published on origin at
    744de26ef (r888 seat push); r565 law: on origin BEFORE this
    freeze commit; self-ack archive landed the r889 window
    (cross-window consume, live-verified: the seat MSG sits in
    fleet/inbox/processed/ at freeze time);
  - registered W188 freeze sha machine-derived = b66117659 (git log
    origin/main --grep "^W188 five-face freeze" -- anchored, the
    r888 round commit a9ab260f6 also carries the unanchored phrase);
    W188 finalize landed r889 one-pass SAME-chain: ledger head
    820,928, merged pool K=411,520 (n1_w188_results.json
    machine-read); W188 sec7/sec8 settle backfill landed the r890
    window (this window, first-leg, commit 43322a984 pre-rebase);
  - per-wave prereg research/PERPETUAL_N1_W189_PREREG.md built r890
    (buildgen r888-bloodline; DRY 50/50; frozen+pushed 632761894 r890
    post-rebase; on origin, verified live below).

DRY discipline (r833 law 2): zero writes until every gate green -- the
emitted freeze-edits script is the ONLY writer, and it re-asserts
everything live (--dry first)."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r888 pairs --------------------------------
src = io.open(r"results\_r888bma_w188_freeze_edits.py", encoding="utf-8").read()
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

# ---------- 2. S88 = W188->W189 ordered fact map ---------------------------
S88 = [
    # -- session / finalize / sha composites (longest first) --
    ("W187 finalize one-pass bm-a r887, net chain head 818,728, ",
     "W188 finalize one-pass bm-a r889, net chain head 820,928, "),
    ("finalize one-pass bm-a r887", "finalize one-pass bm-a r889"),
    ("bm-a r887 one-pass", "bm-a r889 one-pass"),
    ("on origin since r887, not re-shipped", "on origin since r888, not re-shipped"),
    ("already on origin since r887,", "already on origin since r888,"),
    ("(gate-derived r887)", "(gate-derived r888)"),
    ("r885 probe leg4", "r888 probe leg4"),
    ("projection + r885 probe", "projection + r888 probe"),
    ("r888 sec8 \u56de\u586b\u7a97 succession", "r890 sec8 \u56de\u586b\u7a97 succession"),
    ("probe leg4 + r888 sec8", "probe leg4 + r890 sec8"),
    ("at fetch (r887 pre-seat", "at fetch (r888 pre-seat"),
    ("r565 law (r887 pre-seat", "r565 law (r888 pre-seat"),
    ("bm-a r887-window self-ack move", "bm-a r889-window archive move"),
    ("bm-a r886 freeze ", "bm-a r888 freeze "),
    ("(r307; bm-a r886)", "(r307; bm-a r888)"),
    ("bm-a r888 freeze,", "bm-a r890 freeze,"),
    ("r888 bm-a freeze", "r890 bm-a freeze"),
    ("r888 bm-a] ", "r890 bm-a] "),
    ("r887 receipt machine-read", "r888 receipt machine-read"),
    ("MSG-2026-10-08-1717-bma-w188-seat", "MSG-2026-10-08-1815-bma-w189-seat"),
    ("seat MSG-1717 tail,", "seat MSG-1815 tail,"),
    ("_r887bma_w188_probe_receipt.json", "_r888bma_w189_probe_receipt.json"),
    ("79c9a567c", "b66117659"),
    ("943967370", "744de26ef"),
    # -- band geometry (projections FIRST, then the new-band rolls, then
    #    the prior-wave reference rolls that re-create the consumed
    #    strings -- order law preserved from S87) --
    ("430_404..432_403", "432_604..434_603"),
    ("430_604..430_803", "432_804..433_003"),
    ("430_404..430_603", "432_604..432_803"),
    ("428_404..430_403", "430_604..432_603"),
    ("428_204..430_203", "430_404..432_403"),
    ("428_404..428_603", "430_604..430_803"),
    ("428_204..428_403", "430_404..430_603"),
    ("426_204..428_203", "428_404..430_403"),
    ("426_004..428_003", "428_204..430_203"),
    ("426_204..426_403", "428_404..428_603"),
    ("426_004..426_203", "428_204..428_403"),
    # tail+1 pairs (own-A-tail first then prior-B-tail, order kept;
    # tail roll = staircase geometry: prior B tail 430_603 / own-A
    # tail 432_603 -- machine-checked at runtime by the asserts)
    ("428_403+1", "430_603+1"),
    ("430_403+1", "432_603+1"),
    ('assert WAVE_CONFIGS[188]["a_seed_base"] == 428_404 == 428_403 + 1, (',
     'assert WAVE_CONFIGS[189]["a_seed_base"] == 430_604 == 430_603 + 1, ('),
    ('assert WAVE_CONFIGS[188]["b_exit_seed_base"] == 430_404 == 430_403 + 1, (',
     'assert WAVE_CONFIGS[189]["b_exit_seed_base"] == 432_604 == 432_603 + 1, ('),
    ("== 428_404 == 428_403 + 1", "== 430_604 == 430_603 + 1"),
    ("== 430_404 == 430_403 + 1", "== 432_604 == 432_603 + 1"),
    ("arith_a187", "arith_a188"),
    ("arith_b187", "arith_b188"),
    ("set(range(428_404, 430_404))", "set(range(430_604, 432_604))"),
    ("set(range(430_404, 430_604))", "set(range(432_604, 432_804))"),
    ('"a_seed_base": 428_404,', '"a_seed_base": 430_604,'),
    ('"b_exit_seed_base": 430_404,', '"b_exit_seed_base": 432_604,'),
    ('188: {"a": (428_404, 430_403), "b_exit": (430_404, 430_603),',
     '189: {"a": (430_604, 432_603), "b_exit": (432_604, 432_803),'),
    # jump phrases (physical fragment shapes, r869 bloodline; all three
    # rolled one generation)
    ("jumps to 430_404, first-clean ", "jumps to 432_604, first-clean "),
    ("jumps to 430_404 -> ", "jumps to 432_604 -> "),
    ("430_404 and lands ", "432_604 and lands "),
    # -- wave-word cascade (W189 first, then downward) --
    ("W189", "W190"),
    ("W188", "W189"),
    ("W187", "W188"),
    ("W186", "W187"),
    ("W185", "W186"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SEVENTY-EIGHTH", "ONE HUNDRED-AND-SEVENTY-NINTH"),
    ("engine_owner rows 177", "engine_owner rows 178"),
    ("rows 103 + candidate", "rows 104 + candidate"),
    ("one-hundred-fourth", "one-hundred-fifth"),
    ("FORTY-EIGHTH", "FORTY-NINTH"),
    ("forty-eighth", "forty-ninth"),
    ("818,728", "820,928"),
    ("409,320", "411,520"),
    ("range(17, 188)", "range(17, 189)"),
    ("range(16, 188)", "range(16, 189)"),
    ("below 188 composes", "below 189 composes"),
    ("WAVE_CONFIGS if w < 188)", "WAVE_CONFIGS if w < 189)"),
    ("WAVE_CONFIGS[187]", "WAVE_CONFIGS[188]"),
    ('== pf.N1_BANDS[187]["a"][0]', '== pf.N1_BANDS[188]["a"][0]'),
    ('pf.N1_BANDS[187]["b_exit"][0]', 'pf.N1_BANDS[188]["b_exit"][0]'),
    ('pf.N1_BANDS[187].get("engine_owner")', 'pf.N1_BANDS[188].get("engine_owner")'),
    ("w187_a", "w188_a"),
    ("w187_b", "w188_b"),
    ("n3r1_used187", "n3r1_used188"),
    ('188: {"batch"', '189: {"batch"'),
    ("PERPETUAL_N1_W188_PREREG.md", "PERPETUAL_N1_W189_PREREG.md"),
    ("PERPETUAL-N1-W188", "PERPETUAL-N1-W189"),
    ('"n1_w188"', '"n1_w189"'),
    ('"n1_w188_results.json"', '"n1_w189_results.json"'),
    ("n1w188", "n1w189"),
    ("engine_owner=bm-a, wave 187: ", "engine_owner=bm-a, wave 188: "),
    ("wave 187 = first free number after", "wave 188 = first free number after"),
    ("_set_wave(188)", "_set_wave(189)"),
]


def s88(t):
    for old, new in S88:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W189 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r890bma_w189_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r890bma_w189_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r890bma_w189_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r890bma_w189_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD_R888 = '"registered W187 row parity drift (r307; bm-a r886)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if face == "MAT" and old == APPEND_OLD_R888:
            # special-case: chain append pair (historical rows carry; the
            # W188 row -- the current registered tail -- gets appended).
            n_old = '"registered W187 row parity drift (r307; bm-a r886)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[188] == {"a": (428_404, 430_403),' + NL +
                     '                                    "b_exit": (430_404, 430_603),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W188 row parity drift (r307; bm-a r888)"')
            if dump.count(n_old) != 1:
                fails.append("MAT append-pair old-side count %d != 1: %r" %
                             (dump.count(n_old), n_old))
            out.append((n_old, n_new, 1))
            continue
        n_old, n_new = new, s88(new)
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

# spot-check the S88 rolls before emission (fail loud, zero emission)
blk_probe = s88(DUMPS["PF"])
assert '189: {"a": (430_604, 432_603), "b_exit": (432_604, 432_803),' in blk_probe
assert "# W189 (bm-a r890 freeze" in blk_probe
assert "FORTY-NINTH instance" in blk_probe
assert "# 432_604..434_603 CLEAN hops=0 / B first-clean 432_804..433_003" in blk_probe
assert "W190 A window; W190 freezer MUST re-derive on the post-W189" in blk_probe
entry_probe = s88(DUMPS["EN"])
assert '"a_seed_base": 430_604,' in entry_probe and '"b_exit_seed_base": 432_604,' in entry_probe
assert '"batch": "PERPETUAL-N1-W189",' in entry_probe
print("S88 spot-checks: PASS (pf block + entry seed rolls)")

# ---------- 4. NEG lists (mechanical: every consumed old side is a
# tripwire; append-pair old side excluded -- it legitimately remains
# as the prefix of the chain append) --------------------------------------
NEG = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    toks = []
    for n_old, n_new, _cnt in derived[key]:
        if face == "MAT" and n_old.startswith('"registered W187 row parity drift'):
            continue
        # skip no-op pairs (s88 found no roll -- wave-neutral prose that
        # legitimately remains) and partial-persistence shapes
        if n_new == n_old or n_old in n_new:
            continue
        if n_old not in toks:
            toks.append(n_old)
    # defense-in-depth extras (hand additions from the r888 NEG lists,
    # rolled one generation; harmless if absent)
    extra = {
        "PF": ["943967370", "r885 probe", "r888 sec8", "r887 pre-seat",
               "_r887bma", "MSG-2026-10-08-1717", "79c9a567c",
               "818,728", "409,320", "FORTY-EIGHTH", "ONE HUNDRED-AND-SEVENTY-EIGHTH"],
        "EN": ["79c9a567c", "943967370", "818,728", "409,320",
               "ONE HUNDRED-AND-SEVENTY-EIGHTH", "rows 177", "r885 probe",
               "_r887bma", "MSG-2026-10-08-1717", "n1w188", "n1_w188",
               "PERPETUAL-N1-W188", "PERPETUAL_N1_W188", "FORTY-EIGHTH",
               "bm-a r886 freeze", "430_404, first-clean"],
        "MAT": ["w187_", "arith_a187", "arith_b187", "n3r1_used187",
                "r885 probe", "r887 pre-seat", "79c9a567c",
                "ONE HUNDRED-AND-SEVENTY-EIGHTH", "one-hundred-fourth", "rows 177",
                "rows 103 ", "range(17, 188)", "range(16, 188)",
                "PERPETUAL_N1_W188", "PERPETUAL-N1-W188", "MSG-1717",
                "_r887bma", "bm-a r887-window", "n1w188", "n1_w188",
                "818,728", "409,320"],
        "CL": ["818,728", "409,320", "ONE HUNDRED-AND-SEVENTY-EIGHTH",
               "one-hundred-fourth", "rows 177", "rows 103 ", "FORTY-EIGHTH",
               "_r887bma", "r888 bm-a] "],
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


# ---------- 5. emit the W189 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r890 bm-a W189 freeze edits: four insertions (pf N1_BANDS[189] row +
n1 WAVE_CONFIGS[189] entry + n1 W189 materializer block + n1 W189
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + freeze-edits dry-run precedent: full
stale+prose+AST asserts in memory BEFORE any write).

Bloodline: freeze-edits machinery (r773 pit law freeze-editor compliance +
r776 fragment-needle law + r781 verify-separation law), W189 facts
live-registry-driven (built by _r890bma_w189_freeze_buildgen.py: old
sides = the PHYSICAL W188 face fragments probed to dumps first-leg
r890, new sides = the S88 W189 fact map, counts verified pre-emission):
  - pre-seat probe results/_r888bma_w189_probe_receipt.json rc0 ADMIT
    (naive A 430_404..432_403 refused at its own start by the
    registered W188 B band 430_404..430_603; honest forward walk
    1 hop lands A 430_604..432_603 staircase FORTY-NINTH instance
    E36 -- receipt A_semantics machine-cites r887 W188 probe leg4 +
    W188 materializer W189+ projection anticipated + MANDATED this
    re-derive (projection and receipt ordinals MATCH, no divergence
    this wave); B 432_604..432_803 own-A mutual exclusion hops=1,
    naive 430_604..430_803);
  - face probe results/_r890bma_w189_probe_stage1.json rc0 (all four
    W188 faces dumped first-leg r890; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-1815-bma-w189-seat published on origin at
    744de26ef (r888 seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED -- bm-a r889-window archive
    move (cross-window consume by the r889 finalize window,
    disclosed; the W189 seat MSG sits in fleet/inbox/processed/ at
    freeze time, live-verified);
  - per-wave prereg research/PERPETUAL_N1_W189_PREREG.md built r890
    (buildgen r888-bloodline; DRY 50/50 green; frozen+pushed
    632761894 r890 post-rebase; on origin, verified live below);
  - W188 freeze registered sha machine-derived = b66117659 (git log
    origin/main --grep "^W188 five-face freeze" -- anchored: the
    r888 round commit a9ab260f6 also carries the unanchored phrase);
    W188 finalize landed r889 one-pass same-chain: ledger head
    820,928, merged pool K=411,520 (n1_w188_results.json
    machine-read); W188 sec7/sec8 settle backfill landed the r890
    window (this window, first-leg, 43322a984 pre-rebase sha);
  - lineage constants disclosed (r795/r845/r849/r852/r863/r867/
    r869/r874/r878/r882/r885/r888 precedent, passed through):
    (a) the "wave N-1 = first free number" mat-header label rolls
    forward with its off-by-one quirk (since W165 r795);
    (b) "law sec.4 W189 row, r795" band-facts template stamp keeps
    its r795; (c) "single-window derive (r812 merged the gate legs
    INTO the pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls one-hundred-fourth ->
    one-hundred-fifth (rows 104 + candidate = 105th owned per probe
    leg0, machine-chosen word form, disclosed); (e) mat parity-chain
    rows W138..W187 keep their historical stamps and tuples; the
    W188 row (the current registered tail) is APPENDED with its
    frozen values (428_404, 430_403)/(430_404, 430_603) and its
    freeze-run session stamp (r307; bm-a r888); (f) the "W188
    finalize landed one-pass r889" citation rolls its wave-word with
    the values rolling machine-correct to 820,928/411,520 this
    window; (g) the sec8 succession-notes window citation rolls
    r888 -> r890 回填窗 (the W188 sec8 notes landed the r890
    backfill window, honest next-window form, disclosed).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r890bma_w189_face_probe.py first-leg r890 -- four face
      dumps + stage-1 receipt, rc0);
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
      (r530/r687: fetch + origin carries no W189 registration before
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
probe = json.load(open(r"results\\_r888bma_w189_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "430604_432603", "B": "432604_432803"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [430604, 432603], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [432604, 432803], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 186 and probe["legs"]["leg0"]["tail"] == "W188",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 179 and probe["legs"]["leg0"]["bma_ordinal"] == 105,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W190p_A"] == "432604..434603"
      and probe["legs"]["leg4"]["W190p_B"] == "432804..433003",
      "leg4 W190+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('189: {"a": (430_604' not in pf_o, "origin pf already carries W189 row")
check("W189 (bm-a r890 freeze" not in pf_o, "origin pf carries W189 block")
check('189: {"batch"' not in n1_o, "origin n1 already carries W189 entry")
check("# --- W189 materializer face" not in n1_o, "origin n1 carries W189 mat")
check('"r890 bm-a] "' not in n1_o, "origin n1 carries W189 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-1815-bma-w189-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "744de26ef", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-1815-bma-w189-seat.md")),
    "seat MSG not in processed/ at freeze time (r889-window archive)")
w188_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=^W188 five-face freeze"],
    capture_output=True).stdout.decode().strip()
check(w188_freeze_sha == "b66117659", "W188 freeze sha mismatch: " + w188_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 186, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[188] == {"a": (428_404, 430_403),
                              "b_exit": (430_404, 430_603),
                              "engine_owner": "bm-a"}, "live W188 row drift")
check(189 not in pfmod.N1_BANDS, "live N1_BANDS already has 189")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W189_PREREG.md")),
      "W189 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W189_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W189 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r890bma_w189_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r890bma_w189_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r890bma_w189_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r890bma_w189_probe_n1_claim.txt", encoding="utf-8",
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
blk189 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry189 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat189 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim189 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W189 block after the W188 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk189 + NL + "}", 1)

# n1 entry: after the W188 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry189 + NL + IND23 + "}", 1)

# n1 mat: insert the W189 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat189 + NL + seg, 1)

# n1 claim: insert the W189 attribution after the W188 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r888 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r888 bm-a] "' + NL + claim189 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W189 presence + W188 anti-vanish (r560 law)
checks = [
    (pfnew, '189: {"a": (430_604, 432_603), "b_exit": (432_604, 432_803),', 1),
    (pfnew, '188: {"a": (428_404, 430_403), "b_exit": (430_404, 430_603),', 1),
    (pfnew, "# W189 (bm-a r890 freeze", 1),
    (pfnew, "# W188 (bm-a r888 freeze", 1),
    (n1new, '189: {"batch": "PERPETUAL-N1-W189",', 1),
    (n1new, '188: {"batch": "PERPETUAL-N1-W188",', 1),
    (n1new, "# --- W189 materializer face", 1),
    (n1new, "# --- W188 materializer face", 1),
    (n1new, '"r890 bm-a] "', 1),
    (n1new, '"r888 bm-a] "', 1),
    (n1new, '"a_seed_base": 430_604,', 1),
    (n1new, '"b_exit_seed_base": 432_604,', 1),
    (n1new, "n1_w189", 4),
    (n1new, "PERPETUAL_N1_W189_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W190+ projection prose present in the new W189 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W189+ per r845 precedent, n1 fragment =
# next-wave W190+)
check("# W189+ projection (gate-derived r888)" in pfnew,
      "pf W189+ projection head missing")
check('probe_receipt.json; W190+ projection "' in n1new,
      "n1 W190+ projection head fragment missing")
check("# 432_604..434_603 CLEAN hops=0 / B first-clean 432_804..433_003" in pfnew,
      "pf W190p prose missing")
check("W190 A window; W190 freezer MUST re-derive on the post-W189" in pfnew,
      "pf W190 freezer prose missing")
check('"W190 A window; W190 freezer MUST re-derive on the "' in n1new,
      "n1 W190 freezer fragment missing")
check('"W189 B band 432_604..432_803 will refuse the naive "' in n1new,
      "n1 W189-band refuse fragment missing")

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
check('189: {"a": (430_604' not in pf_o2, "write-time: origin pf carries W189")
check('189: {"batch"' not in n1_o2, "write-time: origin n1 carries W189")
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
io.open(r"results\_r890bma_w189_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r890bma_w189_freeze_edits.py", len(out), "bytes")
