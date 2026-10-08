# -*- coding: utf-8 -*-
"""r892 bm-a generator: builds results/_r892bma_w190_freeze_edits.py by
AST-extracting the r890 EMITTED freeze-edits tool's PAIRS
(PF/EN/MAT/CL -- the ground truth that produced the live W189 faces;
the r890 buildgen source diverged from its emission in the MAT
append-pair shape, extraction-from-emission law applied) and deriving
the W190 pairs as (new890, S89(new890), cnt) -- old side = the physical
W189 face fragment (probed to dumps by _r892bma_w190_face_probe.py
first-leg r892, stage-1 rc0), new side = the S89 W190 fact map applied
to that W189 fragment.

S89 = the W189->W190 ordered fact map (S88 rolled one generation,
r735 substring-order law + r877 needle dual-face law preserved:
projections consumed BEFORE the naive rolls that re-create their
strings; own-B before prior-B; the tail+1 pair order kept; composite
assert pairs BEFORE the bare == rolls they contain; wave-word cascade
(W190 first, then downward); append-pair rides the GENERIC roll (the
r890-emitted tool's append pair is a full-tail composite -- no
special-case needed this generation; the [186]-row stamp session r882
rides STALE per quirk (f), the last stamp session rolls r888 -> r890).

S89 LINEAGE CONSTANTS (r795/r845/r849/r852/r863/r867/r869/r874/r878/
r882/r885/r888/r890 precedent, passed through):
  (a) the "wave N-1 = first free number" mat-header label rolls
  forward with its off-by-one quirk (since W165 r795);
  (b) "law sec.4 W190 row, r795" band-facts template stamp keeps its
  r795;
  (c) "single-window derive (r812 merged the gate legs INTO the
  pre-seat probe...)" stays (historical merge citation);
  (d) the bm-a-owned ordinal word rolls one-hundred-fifth ->
  one-hundred-sixth (rows 105 + candidate = 106th owned per probe
  leg0);
  (e) mat parity-chain rows W138..W187 keep their historical stamps
  and tuples; the tail stamps re-label +1 (W187->W188 riding stale
  r882, W188->W189 taking the r890 session) per the r890-emitted
  shape;
  (f) the "W189 finalize landed one-pass r891" citation rolls its
  wave-word with the values rolling machine-correct to 823,128/
  413,720 this window;
  (g) the sec8 succession-notes window citation rolls r890 ->
  r892 回填窗 (the W189 sec8 succession notes landed the r892
  backfill window -- this window, first-leg family form, disclosed);
  (h) seat-face semantic change disclosed: the W190 seat archive move
  = bm-a r892-window (this window, on-disk live-verified at freeze
  time; origin face = the r891 inbox path per r565, dual-path union
  per r374 law).

r587 machine-derived facts (every displayed value read from on-disk
receipts / git history this window):
  - pre-seat probe results/_r891bma_w190_probe_receipt.json rc0 ADMIT
    (leg0 registry 187 rows tail W189 ordinal 180 / bma_ordinal 106;
    leg1 naive A 432_604..434_603 REFUSED at its own start by the
    registered W189 B band 432_604..432_803; honest forward walk 1
    hop lands A 432_804..434_803 staircase FIFTIETH instance E36 --
    receipt A_semantics machine-cites 'r891 W189 probe leg4 + W189
    materializer W190+ projection anticipated and MANDATED this
    re-derive' (projection and receipt ordinals MATCH); B
    434_804..435_003 own-A mutual exclusion hops=1, naive
    432_804..433_003; leg2 conflicts 0; leg3 origin vacancy True;
    leg4 W191+ projection A 434_804..436_803 / B 435_004..435_203,
    B inside A);
  - face probe results/_r892bma_w190_probe_stage1.json rc0 (all four
    W189 faces dumped first-leg r892; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-2035-bma-w190-seat published on origin at
    c177bf73b (r891 seat push; r565 law: on origin BEFORE this freeze
    commit); self-ack archive landed the r892 window (on-disk
    processed/ live-verified; cross-window consume, disclosed);
  - registered W189 five-face registration sha machine-derived =
    8addea3eb (GENERATION FACT CHANGE: no standalone anchored 'W189
    five-face freeze' subject exists -- the W189 pf/n1 insertions
    rode the r890 round closeout commit; content-anchored via git log
    -S '189: {"a": (430_604' -- scripts/perpetual_faces.py, r812
    path-derived precedent);
    W189 finalize landed r891 one-pass SAME-chain: ledger head
    823,128, merged pool K=413,720 (n1_w189_results.json
    machine-read); W189 sec7/sec8 settle backfill landed the r892
    window (this window, first-leg);
  - per-wave prereg research/PERPETUAL_N1_W190_PREREG.md built r892
    (buildgen r890-bloodline; DRY 50/50; frozen+pushed 8394b75ea r892;
    on origin, verified live below).

DRY discipline (r833 law 2): zero writes until every gate green -- the
emitted freeze-edits script is the ONLY writer, and it re-asserts
everything live (--dry first)."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r890 EMITTED tool's pairs -------------------
src = io.open(r"results\_r890bma_w189_freeze_edits.py", encoding="utf-8").read()
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

# ---------- 2. S89 = W189->W190 ordered fact map ---------------------------
S89 = [
    # -- session / finalize / sha composites (longest first) --
    ("W188 finalize one-pass bm-a r889, net chain head 820,928, ",
     "W189 finalize one-pass bm-a r891, net chain head 823,128, "),
    ("finalize one-pass bm-a r889", "finalize one-pass bm-a r891"),
    ("bm-a r889 one-pass", "bm-a r891 one-pass"),
    ("on origin since r888, not re-shipped", "on origin since r890, not re-shipped"),
    ("already on origin since r888,", "already on origin since r890,"),
    ("(gate-derived r888)", "(gate-derived r891)"),
    ("r888 probe leg4", "r891 probe leg4"),
    ("projection + r888 probe", "projection + r891 probe"),
    ("r890 sec8 \u56de\u586b\u7a97 succession", "r892 sec8 \u56de\u586b\u7a97 succession"),
    ("probe leg4 + r890 sec8", "probe leg4 + r892 sec8"),
    ("at fetch (r888 pre-seat", "at fetch (r891 pre-seat"),
    ("r565 law (r888 pre-seat", "r565 law (r891 pre-seat"),
    ("bm-a r889-window archive move", "bm-a r892-window archive move"),
    ("bm-a r888 freeze ", "bm-a r890 freeze "),
    ("(r307; bm-a r888)", "(r307; bm-a r890)"),
    ("bm-a r890 freeze,", "bm-a r892 freeze,"),
    ("r890 bm-a freeze", "r892 bm-a freeze"),
    ("r890 bm-a] ", "r892 bm-a] "),
    ("r888 receipt machine-read", "r891 receipt machine-read"),
    ("MSG-2026-10-08-1815-bma-w189-seat", "MSG-2026-10-08-2035-bma-w190-seat"),
    ("seat MSG-1815 tail,", "seat MSG-2035 tail,"),
    ("_r888bma_w189_probe_receipt.json", "_r891bma_w190_probe_receipt.json"),
    ("b66117659", "8addea3eb"),
    ("744de26ef", "c177bf73b"),
    # -- band geometry (projections FIRST, then the new-band rolls, then
    #    the prior-wave reference rolls that re-create the consumed
    #    strings -- order law preserved from S88) --
    ("432_604..434_603", "434_804..436_803"),
    ("432_804..433_003", "435_004..435_203"),
    ("432_604..432_803", "434_804..435_003"),
    ("430_604..432_603", "432_804..434_803"),
    ("430_404..432_403", "432_604..434_603"),
    ("430_604..430_803", "432_804..433_003"),
    ("430_404..430_603", "432_604..432_803"),
    ("428_404..430_403", "430_604..432_603"),
    ("428_204..430_203", "430_404..432_403"),
    ("428_404..428_603", "430_604..430_803"),
    ("428_204..428_403", "430_404..430_603"),
    # tail+1 pairs (prior-B-tail first then own-A-tail, order kept;
    # tail roll = staircase geometry: prior B tail 432_803 / own-A
    # tail 434_803 -- machine-checked at runtime by the asserts)
    ("430_603+1", "432_803+1"),
    ("432_603+1", "434_803+1"),
    ('assert WAVE_CONFIGS[189]["a_seed_base"] == 430_604 == 430_603 + 1, (',
     'assert WAVE_CONFIGS[190]["a_seed_base"] == 432_804 == 432_803 + 1, ('),
    ('assert WAVE_CONFIGS[189]["b_exit_seed_base"] == 432_604 == 432_603 + 1, (',
     'assert WAVE_CONFIGS[190]["b_exit_seed_base"] == 434_804 == 434_803 + 1, ('),
    ("== 430_604 == 430_603 + 1", "== 432_804 == 432_803 + 1"),
    ("== 432_604 == 432_603 + 1", "== 434_804 == 434_803 + 1"),
    ("arith_a188", "arith_a189"),
    ("arith_b188", "arith_b189"),
    ("set(range(430_604, 432_604))", "set(range(432_804, 434_804))"),
    ("set(range(432_604, 432_804))", "set(range(434_804, 435_004))"),
    ('"a_seed_base": 430_604,', '"a_seed_base": 432_804,'),
    ('"b_exit_seed_base": 432_604,', '"b_exit_seed_base": 434_804,'),
    ('189: {"a": (430_604, 432_603), "b_exit": (432_604, 432_803),',
     '190: {"a": (432_804, 434_803), "b_exit": (434_804, 435_003),'),
    # jump phrases (physical fragment shapes, r869 bloodline; all three
    # rolled one generation)
    ("jumps to 432_604, first-clean ", "jumps to 434_804, first-clean "),
    ("jumps to 432_604 -> ", "jumps to 434_804 -> "),
    ("432_604 and lands ", "434_804 and lands "),
    # -- wave-word cascade (W190 first, then downward) --
    ("W190", "W191"),
    ("W189", "W190"),
    ("W188", "W189"),
    ("W187", "W188"),
    ("W186", "W187"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SEVENTY-NINTH", "ONE HUNDRED-AND-NINETIETH"),
    ("engine_owner rows 178", "engine_owner rows 179"),
    ("rows 104 + candidate", "rows 105 + candidate"),
    ("one-hundred-fifth", "one-hundred-sixth"),
    ("FORTY-NINTH", "FIFTIETH"),
    ("forty-ninth", "fiftieth"),
    ("820,928", "823,128"),
    ("411,520", "413,720"),
    ("range(17, 189)", "range(17, 190)"),
    ("range(16, 189)", "range(16, 190)"),
    ("below 189 composes", "below 190 composes"),
    ("WAVE_CONFIGS if w < 189)", "WAVE_CONFIGS if w < 190)"),
    ("WAVE_CONFIGS[188]", "WAVE_CONFIGS[189]"),
    ('== pf.N1_BANDS[188]["a"][0]', '== pf.N1_BANDS[189]["a"][0]'),
    ('pf.N1_BANDS[188]["b_exit"][0]', 'pf.N1_BANDS[189]["b_exit"][0]'),
    ('pf.N1_BANDS[188].get("engine_owner")', 'pf.N1_BANDS[189].get("engine_owner")'),
    ("w188_a", "w189_a"),
    ("w188_b", "w189_b"),
    ("n3r1_used188", "n3r1_used189"),
    ('189: {"batch"', '190: {"batch"'),
    ("PERPETUAL_N1_W189_PREREG.md", "PERPETUAL_N1_W190_PREREG.md"),
    ("PERPETUAL-N1-W189", "PERPETUAL-N1-W190"),
    ('"n1_w189"', '"n1_w190"'),
    ('"n1_w189_results.json"', '"n1_w190_results.json"'),
    ("n1w189", "n1w190"),
    ("engine_owner=bm-a, wave 188: ", "engine_owner=bm-a, wave 189: "),
    ("wave 188 = first free number after", "wave 189 = first free number after"),
    ("_set_wave(189)", "_set_wave(190)"),
]


def s89(t):
    for old, new in S89:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W190 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r892bma_w190_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r892bma_w190_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r892bma_w190_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r892bma_w190_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        n_old, n_new = new, s89(new)
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

# spot-check the S89 rolls before emission (fail loud, zero emission)
blk_probe = s89(DUMPS["PF"])
assert '190: {"a": (432_804, 434_803), "b_exit": (434_804, 435_003),' in blk_probe
assert "# W190 (bm-a r892 freeze" in blk_probe
assert "FIFTIETH instance" in blk_probe
assert "# 434_804..436_803 CLEAN hops=0 / B first-clean 435_004..435_203" in blk_probe
assert "W191 A window; W191 freezer MUST re-derive on the post-W190" in blk_probe
entry_probe = s89(DUMPS["EN"])
assert '"a_seed_base": 432_804,' in entry_probe and '"b_exit_seed_base": 434_804,' in entry_probe
assert '"batch": "PERPETUAL-N1-W190",' in entry_probe
mat_probe = s89(DUMPS["MAT"])
assert '"registered W189 row parity drift (r307; bm-a r890)"' in mat_probe
assert '"registered W188 row parity drift (r307; bm-a r882)"' in mat_probe
assert "assert pf.N1_BANDS[187] == {\"a\": (426_204, 428_203)," in mat_probe
print("S89 spot-checks: PASS (pf block + entry seed rolls + mat tail re-label)")

# ---------- 4. NEG lists (mechanical: every consumed old side is a
# tripwire; no-op pairs and prefix-persistence shapes skipped) --------------
NEG = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    toks = []
    for n_old, n_new, _cnt in derived[key]:
        if n_new == n_old or n_old in n_new:
            continue
        if n_old not in toks:
            toks.append(n_old)
    # defense-in-depth extras (hand additions from the r890 NEG lists,
    # rolled one generation; harmless if absent)
    extra = {
        "PF": ["744de26ef", "r888 probe", "r890 sec8", "r888 pre-seat",
               "_r888bma", "MSG-2026-10-08-1815", "b66117659",
               "820,928", "411,520", "FORTY-NINTH", "ONE HUNDRED-AND-SEVENTY-NINTH"],
        "EN": ["b66117659", "744de26ef", "820,928", "411,520",
               "ONE HUNDRED-AND-SEVENTY-NINTH", "rows 178", "r888 probe",
               "_r888bma", "MSG-2026-10-08-1815", "n1w189", "n1_w189",
               "PERPETUAL-N1-W189", "PERPETUAL_N1_W189", "FORTY-NINTH",
               "bm-a r888 freeze", "432_604, first-clean"],
        "MAT": ["w188_", "arith_a188", "arith_b188", "n3r1_used188",
                "r888 probe", "r888 pre-seat", "b66117659",
                "ONE HUNDRED-AND-SEVENTY-NINTH", "one-hundred-fifth", "rows 178",
                "rows 104 ", "range(17, 189)", "range(16, 189)",
                "PERPETUAL_N1_W189", "PERPETUAL-N1-W189", "MSG-1815",
                "_r888bma", "bm-a r889-window", "n1w189", "n1_w189",
                "820,928", "411,520"],
        "CL": ["820,928", "411,520", "ONE HUNDRED-AND-SEVENTY-NINTH",
               "one-hundred-fifth", "rows 178", "rows 104 ", "FORTY-NINTH",
               "_r888bma", "r890 bm-a] "],
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


# ---------- 5. emit the W190 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r892 bm-a W190 freeze edits: four insertions (pf N1_BANDS[190] row +
n1 WAVE_CONFIGS[190] entry + n1 W190 materializer block + n1 W190
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + freeze-edits dry-run precedent: full
stale+prose+AST asserts in memory BEFORE any write).

Bloodline: freeze-edits machinery (r773 pit law freeze-editor compliance +
r776 fragment-needle law + r781 verify-separation law), W190 facts
live-registry-driven (built by _r892bma_w190_freeze_buildgen.py: old
sides = the PHYSICAL W189 face fragments probed to dumps first-leg
r892, new sides = the S89 W190 fact map, counts verified pre-emission;
extraction-from-EMISSION law: pairs AST-carried from the r890 emitted
tool -- the ground truth that produced the live faces, the r890
buildgen source having diverged in the MAT append-pair shape):
  - pre-seat probe results/_r891bma_w190_probe_receipt.json rc0 ADMIT
    (naive A 432_604..434_603 refused at its own start by the
    registered W189 B band 432_604..432_803; honest forward walk
    1 hop lands A 432_804..434_803 staircase FIFTIETH instance
    E36 -- receipt A_semantics machine-cites r891 W189 probe leg4 +
    W189 materializer W190+ projection anticipated + MANDATED this
    re-derive (projection and receipt ordinals MATCH, no divergence
    this wave); B 434_804..435_003 own-A mutual exclusion hops=1,
    naive 432_804..433_003);
  - face probe results/_r892bma_w190_probe_stage1.json rc0 (all four
    W189 faces dumped first-leg r892; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-2035-bma-w190-seat published on origin at
    c177bf73b (r891 seat push; r565 law: on origin BEFORE this freeze
    commit); self-ack archive ALREADY LANDED -- bm-a r892-window
    archive move (this window, on-disk processed/ live-verified at
    freeze time; origin face = the r891 inbox path, dual-path union
    per r374 law);
  - per-wave prereg research/PERPETUAL_N1_W190_PREREG.md built r892
    (buildgen r890-bloodline; DRY 50/50 green; frozen+pushed 8394b75ea
    r892; on origin, verified live below);
  - W190 freeze registered sha machine-derived = 8addea3eb
    (GENERATION FACT CHANGE disclosed: no standalone anchored 'W189
    five-face freeze' subject -- the W189 insertions rode the r890
    round closeout commit; content-anchored git log -S '189: {"a":
    (430_604' -- scripts/perpetual_faces.py, r812 path-derived
    precedent); W189 finalize landed r891 one-pass same-chain: ledger
    head 823,128, merged pool K=413,720 (n1_w189_results.json
    machine-read); W189 sec7/sec8 settle backfill landed the r892
    window (this window, first-leg);
  - lineage constants disclosed (r795/r845/r849/r852/r863/r867/
    r869/r874/r878/r882/r885/r888/r890 precedent, passed through):
    (a) the "wave N-1 = first free number" mat-header label rolls
    forward with its off-by-one quirk (since W165 r795);
    (b) "law sec.4 W190 row, r795" band-facts template stamp keeps
    its r795; (c) "single-window derive (r812 merged the gate legs
    INTO the pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls one-hundred-fifth ->
    one-hundred-sixth (rows 105 + candidate = 106th owned per probe
    leg0, machine-chosen word form, disclosed); (e) mat parity-chain
    rows W138..W187 keep their historical stamps and tuples; the tail
    stamps re-label +1 per the r890-emitted shape (the [186]-row stamp
    session r882 rides STALE per quirk (f); the last stamp session
    rolls r888 -> r890); (f) the "W189 finalize landed one-pass r891"
    citation rolls its wave-word with the values rolling
    machine-correct to 823,128/413,720 this window; (g) the sec8
    succession-notes window citation rolls r890 -> r892 回填窗 (the
    W189 sec8 notes landed the r892 backfill window, honest
    next-window form, disclosed).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r892bma_w190_face_probe.py first-leg r892 -- four face
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
      (r530/r687: fetch + origin carries no W190 registration before
      this freeze);
  (7) AST gate after every edit batch (r580/r781)."""
import ast
import io
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, "scripts")
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
probe = json.load(open(r"results\\_r891bma_w190_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "432804_434803", "B": "434804_435003"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [432804, 434803], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [434804, 435003], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 187 and probe["legs"]["leg0"]["tail"] == "W189",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 180 and probe["legs"]["leg0"]["bma_ordinal"] == 106,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W191p_A"] == "434804..436803"
      and probe["legs"]["leg4"]["W191p_B"] == "435004..435203",
      "leg4 W191+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('190: {"a": (432_804' not in pf_o, "origin pf already carries W190 row")
check("W190 (bm-a r892 freeze" not in pf_o, "origin pf carries W190 block")
check('190: {"batch"' not in n1_o, "origin n1 already carries W190 entry")
check("# --- W190 materializer face" not in n1_o, "origin n1 carries W190 mat")
check('"r892 bm-a] "' not in n1_o, "origin n1 carries W190 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-2035-bma-w190-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "c177bf73b", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-2035-bma-w190-seat.md")),
    "seat MSG not in on-disk processed/ at freeze time (r892-window archive)")
w189_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1",
     "-S", '189: {"a": (430_604', "--", "scripts/perpetual_faces.py"],
    capture_output=True).stdout.decode().strip()
check(w189_freeze_sha == "8addea3eb",
      "W190 five-face registration sha mismatch (content-anchored): "
      + w189_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, ".")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 187, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[189] == {"a": (430_604, 432_603),
                              "b_exit": (432_604, 432_803),
                              "engine_owner": "bm-a"}, "live W189 row drift")
check(190 not in pfmod.N1_BANDS, "live N1_BANDS already has 190")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W190_PREREG.md")),
      "W190 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W190_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W190 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r892bma_w190_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r892bma_w190_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r892bma_w190_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r892bma_w190_probe_n1_claim.txt", encoding="utf-8",
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
blk190 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry190 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat190 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim190 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W190 block after the W189 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk190 + NL + "}", 1)

# n1 entry: after the W189 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry190 + NL + IND23 + "}", 1)

# n1 mat: insert the W190 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat190 + NL + seg, 1)

# n1 claim: insert the W190 attribution after the W189 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r890 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r890 bm-a] "' + NL + claim190 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W190 presence + W189 anti-vanish (r560 law)
checks = [
    (pfnew, '190: {"a": (432_804, 434_803), "b_exit": (434_804, 435_003),', 1),
    (pfnew, '189: {"a": (430_604, 432_603), "b_exit": (432_604, 432_803),', 1),
    (pfnew, "# W190 (bm-a r892 freeze", 1),
    (pfnew, "# W189 (bm-a r890 freeze", 1),
    (n1new, '190: {"batch": "PERPETUAL-N1-W190",', 1),
    (n1new, '189: {"batch": "PERPETUAL-N1-W189",', 1),
    (n1new, "# --- W190 materializer face", 1),
    (n1new, "# --- W189 materializer face", 1),
    (n1new, '"r892 bm-a] "', 1),
    (n1new, '"r890 bm-a] "', 1),
    (n1new, '"a_seed_base": 432_804,', 1),
    (n1new, '"b_exit_seed_base": 434_804,', 1),
    (n1new, "n1_w190", 4),
    (n1new, "PERPETUAL_N1_W190_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W191+ projection prose present in the new W190 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W190+ per r845 precedent, n1 fragment =
# next-wave W191+)
check("# W190+ projection (gate-derived r891)" in pfnew,
      "pf W190+ projection head missing")
check('probe_receipt.json; W191+ projection "' in n1new,
      "n1 W191+ projection head fragment missing")
check("# 434_804..436_803 CLEAN hops=0 / B first-clean 435_004..435_203" in pfnew,
      "pf W191p prose missing")
check("W191 A window; W191 freezer MUST re-derive on the post-W190" in pfnew,
      "pf W191 freezer prose missing")
check('"W191 A window; W191 freezer MUST re-derive on the "' in n1new,
      "n1 W191 freezer fragment missing")
check('"W190 B band 434_804..435_003 will refuse the naive "' in n1new,
      "n1 W190-band refuse fragment missing")

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
check('190: {"a": (432_804' not in pf_o2, "write-time: origin pf carries W190")
check('190: {"batch"' not in n1_o2, "write-time: origin n1 carries W190")
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
io.open(r"results\_r892bma_w190_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r892bma_w190_freeze_edits.py", len(out), "bytes")
