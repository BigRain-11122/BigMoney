# -*- coding: utf-8 -*-
"""r863 bm-a generator: builds results/_r863bma_w181_freeze_edits.py by
AST-extracting the r852 W180 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W181 pairs as (new852, S81f(new852), cnt) -- old side =
the physical W180 face fragment (probed to dumps this window by
_r863bma_w181_face_probe.py), new side = the S81f W181 fact map applied
to that W180 fragment.  Special-case: the mat parity-chain append pair
is constructed explicitly (historical rows carry, W180 row appended).
Every derived pair old-side is verified against the physical dumps
BEFORE emission (count == cnt); S81f negatives verified after.

S81f ORDER LAW (r735 substring-order law): projections consumed BEFORE
the naive rolls that re-create their strings (proj-A before arith-A,
proj-B before naive-B, own-B consumed before prior-B); the tail+1 pair
order kept from S75/S76/S77/S79/S80F (A-tail then B-tail); composite
WAVE_CONFIGS assert pairs BEFORE the bare == rolls they contain.

S81f LINEAGE CONSTANTS (r795/r845/r849/r852 precedent, passed through):
  (a) the "wave N-1 = first free number" mat-header label rolls forward
  with its off-by-one quirk (since W165 r795);
  (b) "law sec.4 W180 row, r795" band-facts template stamp keeps its
  r795 (rolls to W181 row, keeps r795);
  (c) "single-window derive (r812 merged the gate legs INTO the
  pre-seat probe...)" stays (historical merge citation);
  (d) the bm-a-owned ordinal word rolls ninety-sixth -> ninety-seventh
  (rows 96 + candidate = 97th owned per probe leg0);
  (e) mat parity-chain rows W138..W179 keep their historical stamps
  and tuples; the W180 row (the current registered tail) is APPENDED
  with its frozen values (410_804, 412_803)/(412_804, 413_003);
  (f) the "W180 finalize landed same-window r827" citation rolls its
  wave-word with the stale r827 session stamp riding (off-by-one
  wave-word + stale-session lineage quirk inherited; head/K values
  roll machine-correct to 801,905/393,920 this window).

r587 machine-derived facts (every displayed value read from on-disk
receipts this window):
  - pre-seat probe results/_r862bma_w181_probe_receipt.json rc0 ADMIT
    (leg0 registry 178 rows tail W180 ordinal 171 / bma_ordinal 97;
    leg1 A 413_004..415_003 staircase FORTY-FIRST instance E36 hops=1
    past the registered W180 B band 412_804..413_003 (W180 seat leg4
    + r851 probe leg4 anticipated 41st -- projection and receipt
    ordinals MATCH); naive 412_804..414_803 refused at its own start by
    the W180 B band; B 415_004..415_203 own-A mutual exclusion hops=1,
    naive 413_004..413_203; leg2 conflicts 0; leg3 origin vacancy
    True; leg4 W182+ projection A 415_004..417_003 hops=0 / B
    415_204..415_403 hops=0, B inside A);
  - W180 finalize landed r854 one-pass same-window, three-gate
    verified (results/perpetual_faces/n1_w180_results.json: merged
    K=393,920, ledger head 801,905; sec7/sec8 backfill landed the
    r854 same window);
  - W180 freeze registered sha machine-derived = 568848aa4 (git log
    origin/main --grep "W180 FREEZE"); W181 seat push sha
    machine-derived = 971316069 (git log --diff-filter=A on the seat
    MSG inbox path); seat self-ack archive move landed r863 same
    window (61ab7d60a, processed/ path live-asserted this window);
  - per-wave prereg research/PERPETUAL_N1_W181_PREREG.md built +
    frozen at origin this window (r863 prereg-freeze push ce136b627;
    banned gate ADMIT 0 verified at prereg freeze).

DRY discipline (r833 law 2): zero writes until every gate green -- the
emitted freeze-edits script is the ONLY writer, and it re-asserts
everything live (--dry first)."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r852 pairs --------------------------------
src = io.open(r"results\_r852bma_w180_freeze_edits.py", encoding="utf-8").read()
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

# ---------- 2. S81f = W180->W181 ordered fact map ---------------------------
S81F = [
    # -- session / finalize / sha composites (longest first) --
    ("W179 finalize one-pass bm-a r850, net chain head 799,705, ",
     "W180 finalize one-pass bm-a r854, net chain head 801,905, "),
    ("finalize one-pass bm-a r850", "finalize one-pass bm-a r854"),
    ("bm-a r850 one-pass", "bm-a r854 one-pass"),
    ("on origin since r850, not re-shipped", "on origin since r854, not re-shipped"),
    ("already on origin since r850,", "already on origin since r854,"),
    ("(gate-derived r851)", "(gate-derived r862)"),
    ("r848 probe leg4", "r851 probe leg4"),
    ("projection + r848 probe", "projection + r851 probe"),
    ("r850 sec8 succession", "r854 sec8 succession"),
    ("probe leg4 + r850 sec8", "probe leg4 + r854 sec8"),
    ("at fetch (r851 pre-seat", "at fetch (r862 pre-seat"),
    ("r565 law (r851 pre-seat", "r565 law (r862 pre-seat"),
    ("r851 same-window self-ack move", "r863 same-window self-ack move"),
    ("bm-a r849 freeze ", "bm-a r852 freeze "),
    ("(r307; bm-a r849)", "(r307; bm-a r852)"),
    ("bm-a r852 freeze,", "bm-a r863 freeze,"),
    ("r852 bm-a freeze", "r863 bm-a freeze"),
    ("r852 bm-a] ", "r863 bm-a] "),
    ("r851 receipt machine-read", "r862 receipt machine-read"),
    ("MSG-2026-10-08-0030-bma-w180-seat", "MSG-2026-10-08-0505-bma-w181-seat"),
    ("seat MSG-0030 tail,", "seat MSG-0505 tail,"),
    ("_r851bma_w180_probe_receipt.json", "_r862bma_w181_probe_receipt.json"),
    ("ef540bf8f", "568848aa4"),
    ("d3b0737fe", "971316069"),
    # -- band geometry (projections FIRST, then bands, arith, prior-B,
    #    naive-B -- order law: proj consumed before the naive rolls
    #    re-create them; own-B consumed before prior-B re-creates it) --
    ("412_804..414_803", "415_004..417_003"),
    ("413_004..413_203", "415_204..415_403"),
    ("412_804..413_003", "415_004..415_203"),
    ("410_804..412_803", "413_004..415_003"),
    ("410_604..412_603", "412_804..414_803"),
    ("410_604..410_803", "412_804..413_003"),
    ("410_804..411_003", "413_004..413_203"),
    ("jumps to 412_804, first-clean ", "jumps to 415_004, first-clean "),
    ("jumps to 412_804 -> ", "jumps to 415_004 -> "),
    ("412_804 and lands ", "415_004 and lands "),
    ('180: {"a": (410_804, 412_803), "b_exit": (412_804, 413_003),',
     '181: {"a": (413_004, 415_003), "b_exit": (415_004, 415_203),'),
    # tail+1 pairs (A-tail first then B-tail, S75/S76/S77/S79/S80F order
    # kept; tail roll = staircase geometry: prior B tail 413_003 /
    # own-A tail 415_003 -- machine-checked at runtime by the asserts)
    ("412_803+1", "415_003+1"),
    ("410_803+1", "413_003+1"),
    ('assert WAVE_CONFIGS[180]["a_seed_base"] == 410_804 == 410_803 + 1, (',
     'assert WAVE_CONFIGS[181]["a_seed_base"] == 413_004 == 413_003 + 1, ('),
    ('assert WAVE_CONFIGS[180]["b_exit_seed_base"] == 412_804 == 412_803 + 1, (',
     'assert WAVE_CONFIGS[181]["b_exit_seed_base"] == 415_004 == 415_003 + 1, ('),
    ("== 410_804 == 410_803 + 1", "== 413_004 == 413_003 + 1"),
    ("== 412_804 == 412_803 + 1", "== 415_004 == 415_003 + 1"),
    ("arith_a179", "arith_a180"),
    ("arith_b179", "arith_b180"),
    ("set(range(410_804, 412_804))", "set(range(413_004, 415_004))"),
    ("set(range(412_804, 413_004))", "set(range(415_004, 415_204))"),
    ('"a_seed_base": 410_804,', '"a_seed_base": 413_004,'),
    ('"b_exit_seed_base": 412_804,', '"b_exit_seed_base": 415_004,'),
    # -- wave-word cascade (W181 first, then downward) --
    ("W181", "W182"),
    ("W180", "W181"),
    ("W179", "W180"),
    ("W178", "W179"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SEVENTIETH", "ONE HUNDRED-AND-SEVENTY-FIRST"),
    ("engine_owner rows 169", "engine_owner rows 170"),
    ("rows 95 + candidate", "rows 96 + candidate"),
    ("ninety-sixth", "ninety-seventh"),
    ("FORTIETH", "FORTY-FIRST"),
    ("fortieth", "forty-first"),
    ("799,705", "801,905"),
    ("391,720", "393,920"),
    ("range(17, 180)", "range(17, 181)"),
    ("range(16, 180)", "range(16, 181)"),
    ("below 180 composes", "below 181 composes"),
    ("WAVE_CONFIGS if w < 180)", "WAVE_CONFIGS if w < 181)"),
    ("WAVE_CONFIGS[179]", "WAVE_CONFIGS[180]"),
    ('== pf.N1_BANDS[179]["a"][0]', '== pf.N1_BANDS[180]["a"][0]'),
    ('pf.N1_BANDS[179]["b_exit"][0]', 'pf.N1_BANDS[180]["b_exit"][0]'),
    ('pf.N1_BANDS[179].get("engine_owner")', 'pf.N1_BANDS[180].get("engine_owner")'),
    ("w179_a", "w180_a"),
    ("w179_b", "w180_b"),
    ("n3r1_used179", "n3r1_used180"),
    ('180: {"batch"', '181: {"batch"'),
    ("PERPETUAL_N1_W180_PREREG.md", "PERPETUAL_N1_W181_PREREG.md"),
    ("PERPETUAL-N1-W180", "PERPETUAL-N1-W181"),
    ('"n1_w180"', '"n1_w181"'),
    ('"n1_w180_results.json"', '"n1_w181_results.json"'),
    ("n1w180", "n1w181"),
    ("engine_owner=bm-a, wave 179: ", "engine_owner=bm-a, wave 180: "),
    ("wave 179 = first free number after", "wave 180 = first free number after"),
    ("_set_wave(180)", "_set_wave(181)"),
]


def s81f(t):
    for old, new in S81F:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W181 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r863bma_w181_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r863bma_w181_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r863bma_w181_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r863bma_w181_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD_R852 = '"registered W178 row parity drift (r307; bm-a r845)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if face == "MAT" and old == APPEND_OLD_R852:
            # special-case: chain append pair (historical rows carry; the
            # W180 row -- the current registered tail -- gets appended).
            n_old = '"registered W179 row parity drift (r307; bm-a r849)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[180] == {"a": (410_804, 412_803),' + NL +
                     '                                    "b_exit": (412_804, 413_003),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W180 row parity drift (r307; bm-a r852)"')
            if dump.count(n_old) != 1:
                fails.append("MAT append-pair old-side count %d != 1: %r" %
                             (dump.count(n_old), n_old))
            out.append((n_old, n_new, 1))
            continue
        n_old, n_new = new, s81f(new)
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

# spot-check the S81f rolls before emission (fail loud, zero emission)
blk_probe = s81f(DUMPS["PF"])
assert '181: {"a": (413_004, 415_003), "b_exit": (415_004, 415_203),' in blk_probe
assert "# W181 (bm-a r863 freeze" in blk_probe
assert "FORTY-FIRST instance" in blk_probe
assert "# 415_004..417_003 CLEAN hops=0 / B first-clean 415_204..415_403" in blk_probe
assert "W182 A window; W182 freezer MUST re-derive on the post-W181" in blk_probe
entry_probe = s81f(DUMPS["EN"])
assert '"a_seed_base": 413_004,' in entry_probe and '"b_exit_seed_base": 415_004,' in entry_probe
assert '"batch": "PERPETUAL-N1-W181",' in entry_probe
print("S81f spot-checks: PASS (pf block + entry seed rolls)")

# ---------- 4. NEG lists (mechanical: every consumed old side is a
# tripwire; append-pair old side excluded -- it legitimately remains
# as the prefix of the chain append) --------------------------------------
NEG = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    toks = []
    for n_old, n_new, _cnt in derived[key]:
        if face == "MAT" and n_old.startswith('"registered W179 row parity drift'):
            continue
        # skip no-op pairs (s81f found no roll -- wave-neutral prose that
        # legitimately remains) and partial-persistence shapes
        if n_new == n_old or n_old in n_new:
            continue
        if n_old not in toks:
            toks.append(n_old)
    # defense-in-depth extras (hand additions from the r852 NEG lists,
    # rolled one generation; harmless if absent)
    extra = {
        "PF": ["d3b0737fe", "r848 probe", "r850 sec8", "r851 pre-seat",
               "_r851bma", "MSG-2026-10-08-0030", "ef540bf8f",
               "799,705", "391,720", "FORTIETH", "ONE HUNDRED-AND-SEVENTIETH"],
        "EN": ["ef540bf8f", "d3b0737fe", "799,705", "391,720",
               "ONE HUNDRED-AND-SEVENTIETH", "rows 169", "r848 probe",
               "_r851bma", "MSG-2026-10-08-0030", "n1w180", "n1_w180",
               "PERPETUAL-N1-W180", "PERPETUAL_N1_W180", "FORTIETH",
               "bm-a r849 freeze", "412_804, first-clean"],
        "MAT": ["w179_", "arith_a179", "arith_b179", "n3r1_used179",
                "r848 probe", "r851 pre-seat", "ef540bf8f",
                "ONE HUNDRED-AND-SEVENTIETH", "ninety-sixth", "rows 169",
                "rows 95 ", "range(17, 180)", "range(16, 180)",
                "PERPETUAL_N1_W180", "PERPETUAL-N1-W180", "MSG-0030",
                "_r851bma", "r851 same-window", "n1w180", "n1_w180",
                "799,705", "391,720"],
        "CL": ["799,705", "391,720", "ONE HUNDRED-AND-SEVENTIETH",
               "ninety-sixth", "rows 169", "rows 95 ", "FORTIETH",
               "_r851bma", "r849 bm-a] "],
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


# ---------- 5. emit the W181 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r863 bm-a W181 freeze edits: four insertions (pf N1_BANDS[181] row +
n1 WAVE_CONFIGS[181] entry + n1 W181 materializer block + n1 W181
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845/r849/
r852 dry-run precedent: full stale+prose+AST asserts in memory BEFORE
any write).

Bloodline: r819/r822/r826/r830/r834/r843/r845/r849/r852 freeze-edits
machinery (r773 pit law freeze-editor compliance + r776 fragment-needle
law + r781 verify-separation law), W181 facts live-registry-driven
(built by _r863bma_w181_freeze_buildgen.py: old sides = the PHYSICAL
W180 face fragments probed to dumps this window, new sides = the S81f
W181 fact map, counts verified pre-emission):
  - pre-seat probe results/_r862bma_w181_probe_receipt.json rc0 ADMIT
    (A 413_004..415_003 staircase FORTY-FIRST instance E36 hops=1
    past the registered W180 B band 412_804..413_003; naive
    412_804..414_803 refused at its own start by the W180 B band --
    receipt A_semantics machine-cites the W180 seat MSG leg4 + r851
    probe leg4 anticipated + MANDATED this re-derive (W180 sec5.5
    prose anticipated 41st -- projection and receipt ordinals MATCH,
    no divergence this wave); B 415_004..415_203 own-A mutual
    exclusion hops=1, naive 413_004..413_203);
  - face probe results/_r863bma_w181_face_probe_receipt.json rc0 (all
    four W180 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-0505-bma-w181-seat published on origin at
    971316069 (r862 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- r863 same-window
    self-ack move (the W181 seat MSG sits in fleet/inbox/processed/ at
    freeze time, honest archived; 61ab7d60a);
  - per-wave prereg research/PERPETUAL_N1_W181_PREREG.md frozen at
    origin (r863 prereg-freeze push ce136b627; banned gate ADMIT 0
    re-verified at prereg freeze);
  - W180 freeze registered sha machine-derived = 568848aa4 (git log
    origin/main --grep "W180 FREEZE"); W180 finalize landed r854
    one-pass same-window: ledger head 801,905, merged pool
    K=393,920 (n1_w180_results.json machine-read; sec7/sec8 backfill
    landed the r854 same window -- same-window, honest);
  - lineage constants disclosed (r795/r845/r849/r852 precedent, passed
    through): (a) the "wave N-1 = first free number" mat-header label
    rolls forward with its off-by-one quirk (since W165 r795);
    (b) "law sec.4 W181 row, r795" band-facts template stamp keeps its
    r795; (c) "single-window derive (r812 merged the gate legs INTO
    the pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls ninety-sixth ->
    ninety-seventh (rows 96 + candidate = 97th owned per probe leg0);
    (e) mat parity-chain rows W138..W179 keep their historical stamps
    and tuples; the W180 row (the current registered tail) is
    APPENDED with its frozen values (410_804, 412_803)/(412_804,
    413_003); (f) the "W180 finalize landed same-window r827"
    citation rolls its wave-word with the stale r827 session stamp
    riding (off-by-one wave-word + stale-session lineage quirk
    inherited; head/K values roll machine-correct to 801,905/393,920
    this window).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r863bma_w181_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W181 registration before
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
probe = json.load(open(r"results\\_r862bma_w181_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "413004_415003", "B": "415004_415203"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [413004, 415003], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [415004, 415203], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 178 and probe["legs"]["leg0"]["tail"] == "W180",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 171 and probe["legs"]["leg0"]["bma_ordinal"] == 97,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W182p_A"] == "415004..417003"
      and probe["legs"]["leg4"]["W182p_B"] == "415204..415403",
      "leg4 W182+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('181: {"a": (413_004' not in pf_o, "origin pf already carries W181 row")
check("W181 (bm-a r863 freeze" not in pf_o, "origin pf carries W181 block")
check('181: {"batch"' not in n1_o, "origin n1 already carries W181 entry")
check("# --- W181 materializer face" not in n1_o, "origin n1 carries W181 mat")
check('"r863 bm-a] "' not in n1_o, "origin n1 carries W181 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-0505-bma-w181-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "971316069", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-0505-bma-w181-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w180_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W180 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w180_freeze_sha == "568848aa4", "W180 freeze sha mismatch: " + w180_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 178, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[180] == {"a": (410_804, 412_803),
                              "b_exit": (412_804, 413_003),
                              "engine_owner": "bm-a"}, "live W180 row drift")
check(181 not in pfmod.N1_BANDS, "live N1_BANDS already has 181")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W181_PREREG.md")),
      "W181 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W181_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W181 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r863bma_w181_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r863bma_w181_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r863bma_w181_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r863bma_w181_probe_n1_claim.txt", encoding="utf-8",
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
blk181 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry181 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat181 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim181 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W181 block after the W180 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk181 + NL + "}", 1)

# n1 entry: after the W180 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry181 + NL + IND23 + "}", 1)

# n1 mat: insert the W181 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat181 + NL + seg, 1)

# n1 claim: insert the W181 attribution after the W180 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r852 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r852 bm-a] "' + NL + claim181 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W181 presence + W180 anti-vanish (r560 law)
checks = [
    (pfnew, '181: {"a": (413_004, 415_003), "b_exit": (415_004, 415_203),', 1),
    (pfnew, '180: {"a": (410_804, 412_803), "b_exit": (412_804, 413_003),', 1),
    (pfnew, "# W181 (bm-a r863 freeze", 1),
    (pfnew, "# W180 (bm-a r852 freeze", 1),
    (n1new, '181: {"batch": "PERPETUAL-N1-W181",', 1),
    (n1new, '180: {"batch": "PERPETUAL-N1-W180",', 1),
    (n1new, "# --- W181 materializer face", 1),
    (n1new, "# --- W180 materializer face", 1),
    (n1new, '"r863 bm-a] "', 1),
    (n1new, '"r852 bm-a] "', 1),
    (n1new, '"a_seed_base": 413_004,', 1),
    (n1new, '"b_exit_seed_base": 415_004,', 1),
    (n1new, "n1_w181", 4),
    (n1new, "PERPETUAL_N1_W181_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W182+ projection prose present in the new W181 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W181+ per r845 precedent, n1 fragment =
# next-wave W182+)
check("# W181+ projection (gate-derived r862)" in pfnew,
      "pf W181+ projection head missing")
check('probe_receipt.json; W182+ projection "' in n1new,
      "n1 W182+ projection head fragment missing")
check("# 415_004..417_003 CLEAN hops=0 / B first-clean 415_204..415_403" in pfnew,
      "pf W182p prose missing")
check("W182 A window; W182 freezer MUST re-derive on the post-W181" in pfnew,
      "pf W182 freezer prose missing")
check('"W182 A window; W182 freezer MUST re-derive on the "' in n1new,
      "n1 W182 freezer fragment missing")
check('"W181 B band 415_004..415_203 will refuse the naive "' in n1new,
      "n1 W181-band refuse fragment missing")

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
check('181: {"a": (413_004' not in pf_o2, "write-time: origin pf carries W181")
check('181: {"batch"' not in n1_o2, "write-time: origin n1 carries W181")
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
io.open(r"results\_r863bma_w181_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r863bma_w181_freeze_edits.py", len(out), "bytes")
