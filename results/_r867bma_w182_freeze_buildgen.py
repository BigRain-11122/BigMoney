# -*- coding: utf-8 -*-
"""r867 bm-a generator: builds results/_r867bma_w182_freeze_edits.py by
AST-extracting the r863 W181 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W182 pairs as (new863, S82f(new863), cnt) -- old side =
the physical W181 face fragment (probed to dumps this window by
_r867bma_w182_face_probe.py), new side = the S82f W182 fact map applied
to that W181 fragment.  Special-case: the mat parity-chain append pair
is constructed explicitly (historical rows carry, W181 row appended).
Every derived pair old-side is verified against the physical dumps
BEFORE emission (count == cnt); S82f negatives verified after.

S82f ORDER LAW (r735 substring-order law): projections consumed BEFORE
the naive rolls that re-create their strings (proj-A before arith-A,
proj-B before naive-B, own-B consumed before prior-B); the tail+1 pair
order kept from S75/S76/S77/S79/S80F/S81f (A-tail then B-tail);
composite WAVE_CONFIGS assert pairs BEFORE the bare == rolls they
contain.

S82f LINEAGE CONSTANTS (r795/r845/r849/r852/r863 precedent, passed
through):
  (a) the "wave N-1 = first free number" mat-header label rolls forward
  with its off-by-one quirk (since W165 r795);
  (b) "law sec.4 W182 row, r795" band-facts template stamp keeps its
  r795 (rolls to W182 row, keeps r795);
  (c) "single-window derive (r812 merged the gate legs INTO the
  pre-seat probe...)" stays (historical merge citation);
  (d) the bm-a-owned ordinal word rolls ninety-seventh -> ninety-eighth
  (rows 97 + candidate = 98th owned per probe leg0);
  (e) mat parity-chain rows W138..W180 keep their historical stamps
  and tuples; the W181 row (the current registered tail) is APPENDED
  with its frozen values (413_004, 415_003)/(415_004, 415_203);
  (f) the "W181 finalize landed same-window r827" citation rolls its
  wave-word with the stale r827 session stamp riding (off-by-one
  wave-word + stale-session lineage quirk inherited; head/K values
  roll machine-correct to 804,518/396,120 this window);
  (g) the self-ack archive move citation rolls to the bm-c r737
  window (cross-machine consume 71a40c102; the r866 bm-a session
  raced the same move the same second -- git fact on origin is the
  bm-c add; honest cross-machine face disclosed).

r587 machine-derived facts (every displayed value read from on-disk
receipts this window):
  - pre-seat probe results/_r865bma_w182_probe_receipt.json rc0 ADMIT
    (leg0 registry 179 rows tail W181 ordinal 172 / bma_ordinal 98;
    leg1 A 415_204..417_203 staircase FORTY-SECOND instance E36 hops=1
    past the registered W181 B band 415_004..415_203 (W181 seat leg4
    + r862 probe leg4 anticipated 42nd -- projection and receipt
    ordinals MATCH); naive 415_004..417_003 refused at its own start
    by the W181 B band; B 417_204..417_403 own-A mutual exclusion
    hops=1, naive 415_204..415_403; leg2 conflicts 0; leg3 origin
    vacancy True; leg4 W183+ projection A 417_204..419_203 hops=0 / B
    417_404..417_603 hops=0, B inside A);
  - W181 finalize landed r864 one-pass same-window, three-gate
    verified (results/perpetual_faces/n1_w181_results.json: merged
    K=396,120, ledger head 804,518); W181 sec7/sec8 settle backfill
    landed the r867 HEAL window (r864 finalize-window miss disclosed,
    W159/W168/W169/W180 delayed-window precedent family);
  - W181 freeze registered sha machine-derived = de699e8cd (git log
    origin/main --grep "W181 FREEZE"); W182 seat push sha
    machine-derived = df062c5c1 (git log --diff-filter=A on the seat
    MSG inbox path); seat self-ack archive landed via bm-c r737
    (71a40c102, processed/ path live-asserted this window);
  - per-wave prereg research/PERPETUAL_N1_W182_PREREG.md built +
    banned gate ADMIT 0 verified this window (r867; push pending).

DRY discipline (r833 law 2): zero writes until every gate green -- the
emitted freeze-edits script is the ONLY writer, and it re-asserts
everything live (--dry first)."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r863 pairs --------------------------------
src = io.open(r"results\_r863bma_w181_freeze_edits.py", encoding="utf-8").read()
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

# ---------- 2. S82f = W181->W182 ordered fact map ---------------------------
S82F = [
    # -- session / finalize / sha composites (longest first) --
    ("W180 finalize one-pass bm-a r854, net chain head 801,905, ",
     "W181 finalize one-pass bm-a r864, net chain head 804,518, "),
    ("finalize one-pass bm-a r854", "finalize one-pass bm-a r864"),
    ("bm-a r854 one-pass", "bm-a r864 one-pass"),
    ("on origin since r854, not re-shipped", "on origin since r864, not re-shipped"),
    ("already on origin since r854,", "already on origin since r864,"),
    ("(gate-derived r862)", "(gate-derived r865)"),
    ("r851 probe leg4", "r862 probe leg4"),
    ("projection + r851 probe", "projection + r862 probe"),
    ("r854 sec8 succession", "r867 sec8 heal succession"),
    ("probe leg4 + r854 sec8", "probe leg4 + r867 sec8"),
    ("at fetch (r862 pre-seat", "at fetch (r865 pre-seat"),
    ("r565 law (r862 pre-seat", "r565 law (r865 pre-seat"),
    ("r863 same-window self-ack move", "bm-c r737-window self-ack move"),
    ("bm-a r852 freeze ", "bm-a r863 freeze "),
    ("(r307; bm-a r852)", "(r307; bm-a r863)"),
    ("bm-a r863 freeze,", "bm-a r867 freeze,"),
    ("r863 bm-a freeze", "r867 bm-a freeze"),
    ("r863 bm-a] ", "r867 bm-a] "),
    ("r862 receipt machine-read", "r865 receipt machine-read"),
    ("MSG-2026-10-08-0505-bma-w181-seat", "MSG-2026-10-08-0603-bma-w182-seat"),
    ("seat MSG-0505 tail,", "seat MSG-0603 tail,"),
    ("_r862bma_w181_probe_receipt.json", "_r865bma_w182_probe_receipt.json"),
    ("568848aa4", "de699e8cd"),
    ("971316069", "df062c5c1"),
    # -- band geometry (projections FIRST, then bands, arith, prior-B,
    #    naive-B -- order law: proj consumed before the naive rolls
    #    re-create them; own-B consumed before prior-B re-creates it) --
    ("415_004..417_003", "417_204..419_203"),
    ("415_204..415_403", "417_404..417_603"),
    ("415_004..415_203", "417_204..417_403"),
    ("413_004..415_003", "415_204..417_203"),
    ("412_804..414_803", "415_004..417_003"),
    ("412_804..413_003", "415_004..415_203"),
    ("413_004..413_203", "415_204..415_403"),
    ("jumps to 415_004, first-clean ", "jumps to 417_204, first-clean "),
    ("jumps to 415_004 -> ", "jumps to 417_204 -> "),
    ("415_004 and lands ", "417_204 and lands "),
    ('181: {"a": (413_004, 415_003), "b_exit": (415_004, 415_203),',
     '182: {"a": (415_204, 417_203), "b_exit": (417_204, 417_403),'),
    # tail+1 pairs (A-tail first then B-tail, S75/S76/S77/S79/S80F/S81f
    # order kept; tail roll = staircase geometry: prior B tail 415_203 /
    # own-A tail 417_203 -- machine-checked at runtime by the asserts)
    ("415_003+1", "417_203+1"),
    ("413_003+1", "415_203+1"),
    ('assert WAVE_CONFIGS[181]["a_seed_base"] == 413_004 == 413_003 + 1, (',
     'assert WAVE_CONFIGS[182]["a_seed_base"] == 415_204 == 415_203 + 1, ('),
    ('assert WAVE_CONFIGS[181]["b_exit_seed_base"] == 415_004 == 415_003 + 1, (',
     'assert WAVE_CONFIGS[182]["b_exit_seed_base"] == 417_204 == 417_203 + 1, ('),
    ("== 413_004 == 413_003 + 1", "== 415_204 == 415_203 + 1"),
    ("== 415_004 == 415_003 + 1", "== 417_204 == 417_203 + 1"),
    ("arith_a180", "arith_a181"),
    ("arith_b180", "arith_b181"),
    ("set(range(413_004, 415_004))", "set(range(415_204, 417_204))"),
    ("set(range(415_004, 415_204))", "set(range(417_204, 417_404))"),
    ('"a_seed_base": 413_004,', '"a_seed_base": 415_204,'),
    ('"b_exit_seed_base": 415_004,', '"b_exit_seed_base": 417_204,'),
    # -- wave-word cascade (W182 first, then downward) --
    ("W182", "W183"),
    ("W181", "W182"),
    ("W180", "W181"),
    ("W179", "W180"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SEVENTY-FIRST", "ONE HUNDRED-AND-SEVENTY-SECOND"),
    ("engine_owner rows 170", "engine_owner rows 171"),
    ("rows 96 + candidate", "rows 97 + candidate"),
    ("ninety-seventh", "ninety-eighth"),
    ("FORTY-FIRST", "FORTY-SECOND"),
    ("forty-first", "forty-second"),
    ("801,905", "804,518"),
    ("393,920", "396,120"),
    ("range(17, 181)", "range(17, 182)"),
    ("range(16, 181)", "range(16, 182)"),
    ("below 181 composes", "below 182 composes"),
    ("WAVE_CONFIGS if w < 181)", "WAVE_CONFIGS if w < 182)"),
    ("WAVE_CONFIGS[180]", "WAVE_CONFIGS[181]"),
    ('== pf.N1_BANDS[180]["a"][0]', '== pf.N1_BANDS[181]["a"][0]'),
    ('pf.N1_BANDS[180]["b_exit"][0]', 'pf.N1_BANDS[181]["b_exit"][0]'),
    ('pf.N1_BANDS[180].get("engine_owner")', 'pf.N1_BANDS[181].get("engine_owner")'),
    ("w180_a", "w181_a"),
    ("w180_b", "w181_b"),
    ("n3r1_used180", "n3r1_used181"),
    ('181: {"batch"', '182: {"batch"'),
    ("PERPETUAL_N1_W181_PREREG.md", "PERPETUAL_N1_W182_PREREG.md"),
    ("PERPETUAL-N1-W181", "PERPETUAL-N1-W182"),
    ('"n1_w181"', '"n1_w182"'),
    ('"n1_w181_results.json"', '"n1_w182_results.json"'),
    ("n1w181", "n1w182"),
    ("engine_owner=bm-a, wave 180: ", "engine_owner=bm-a, wave 181: "),
    ("wave 180 = first free number after", "wave 181 = first free number after"),
    ("_set_wave(181)", "_set_wave(182)"),
]


def s82f(t):
    for old, new in S82F:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W182 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r867bma_w182_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r867bma_w182_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r867bma_w182_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r867bma_w182_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD_R863 = '"registered W179 row parity drift (r307; bm-a r849)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if face == "MAT" and old == APPEND_OLD_R863:
            # special-case: chain append pair (historical rows carry; the
            # W181 row -- the current registered tail -- gets appended).
            n_old = '"registered W180 row parity drift (r307; bm-a r852)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[181] == {"a": (413_004, 415_003),' + NL +
                     '                                    "b_exit": (415_004, 415_203),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W181 row parity drift (r307; bm-a r863)"')
            if dump.count(n_old) != 1:
                fails.append("MAT append-pair old-side count %d != 1: %r" %
                             (dump.count(n_old), n_old))
            out.append((n_old, n_new, 1))
            continue
        n_old, n_new = new, s82f(new)
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

# spot-check the S82f rolls before emission (fail loud, zero emission)
blk_probe = s82f(DUMPS["PF"])
assert '182: {"a": (415_204, 417_203), "b_exit": (417_204, 417_403),' in blk_probe
assert "# W182 (bm-a r867 freeze" in blk_probe
assert "FORTY-SECOND instance" in blk_probe
assert "# 417_204..419_203 CLEAN hops=0 / B first-clean 417_404..417_603" in blk_probe
assert "W183 A window; W183 freezer MUST re-derive on the post-W182" in blk_probe
entry_probe = s82f(DUMPS["EN"])
assert '"a_seed_base": 415_204,' in entry_probe and '"b_exit_seed_base": 417_204,' in entry_probe
assert '"batch": "PERPETUAL-N1-W182",' in entry_probe
print("S82f spot-checks: PASS (pf block + entry seed rolls)")

# ---------- 4. NEG lists (mechanical: every consumed old side is a
# tripwire; append-pair old side excluded -- it legitimately remains
# as the prefix of the chain append) --------------------------------------
NEG = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    toks = []
    for n_old, n_new, _cnt in derived[key]:
        if face == "MAT" and n_old.startswith('"registered W180 row parity drift'):
            continue
        # skip no-op pairs (s82f found no roll -- wave-neutral prose that
        # legitimately remains) and partial-persistence shapes
        if n_new == n_old or n_old in n_new:
            continue
        if n_old not in toks:
            toks.append(n_old)
    # defense-in-depth extras (hand additions from the r863 NEG lists,
    # rolled one generation; harmless if absent)
    extra = {
        "PF": ["971316069", "r851 probe", "r854 sec8", "r862 pre-seat",
               "_r862bma", "MSG-2026-10-08-0505", "568848aa4",
               "801,905", "393,920", "FORTY-FIRST", "ONE HUNDRED-AND-SEVENTY-FIRST"],
        "EN": ["568848aa4", "971316069", "801,905", "393,920",
               "ONE HUNDRED-AND-SEVENTY-FIRST", "rows 170", "r851 probe",
               "_r862bma", "MSG-2026-10-08-0505", "n1w181", "n1_w181",
               "PERPETUAL-N1-W181", "PERPETUAL_N1_W181", "FORTY-FIRST",
               "bm-a r852 freeze", "415_004, first-clean"],
        "MAT": ["w180_", "arith_a180", "arith_b180", "n3r1_used180",
                "r851 probe", "r862 pre-seat", "568848aa4",
                "ONE HUNDRED-AND-SEVENTY-FIRST", "ninety-seventh", "rows 170",
                "rows 96 ", "range(17, 181)", "range(16, 181)",
                "PERPETUAL_N1_W181", "PERPETUAL-N1-W181", "MSG-0505",
                "_r862bma", "r863 same-window", "n1w181", "n1_w181",
                "801,905", "393,920"],
        "CL": ["801,905", "393,920", "ONE HUNDRED-AND-SEVENTY-FIRST",
               "ninety-seventh", "rows 170", "rows 96 ", "FORTY-FIRST",
               "_r862bma", "r852 bm-a] "],
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


# ---------- 5. emit the W182 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r867 bm-a W182 freeze edits: four insertions (pf N1_BANDS[182] row +
n1 WAVE_CONFIGS[182] entry + n1 W182 materializer block + n1 W182
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845/r849/
r852/r863 dry-run precedent: full stale+prose+AST asserts in memory
BEFORE any write).

Bloodline: r819/r822/r826/r830/r834/r843/r845/r849/r852/r863 freeze-edits
machinery (r773 pit law freeze-editor compliance + r776 fragment-needle
law + r781 verify-separation law), W182 facts live-registry-driven
(built by _r867bma_w182_freeze_buildgen.py: old sides = the PHYSICAL
W181 face fragments probed to dumps this window, new sides = the S82f
W182 fact map, counts verified pre-emission):
  - pre-seat probe results/_r865bma_w182_probe_receipt.json rc0 ADMIT
    (A 415_204..417_203 staircase FORTY-SECOND instance E36 hops=1
    past the registered W181 B band 415_004..415_203; naive
    415_004..417_003 refused at its own start by the W181 B band --
    receipt A_semantics machine-cites the W181 seat MSG leg4 + r862
    probe leg4 anticipated + MANDATED this re-derive (W181 sec5.5
    prose anticipated 42nd -- projection and receipt ordinals MATCH,
    no divergence this wave); B 417_204..417_403 own-A mutual
    exclusion hops=1, naive 415_204..415_403);
  - face probe results/_r867bma_w182_face_probe_receipt.json rc0 (all
    four W181 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-0603-bma-w182-seat published on origin at
    df062c5c1 (r865 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- bm-c r737-window
    self-ack move (cross-machine consume, 71a40c102; the r866 bm-a
    session raced the same move the same second -- the git fact on
    origin is the bm-c add, honest); the W182 seat MSG sits in
    fleet/inbox/processed/ at freeze time, honest archived;
  - per-wave prereg research/PERPETUAL_N1_W182_PREREG.md built this
    window (r867 buildgen r863-bloodline; banned gate ADMIT 0
    verified at prereg build; prereg-freeze push this window);
  - W181 freeze registered sha machine-derived = de699e8cd (git log
    origin/main --grep "W181 FREEZE"); W181 finalize landed r864
    one-pass same-window: ledger head 804,518, merged pool
    K=396,120 (n1_w181_results.json machine-read); W181 sec7/sec8
    settle backfill landed the r867 HEAL window (r864 finalize-window
    miss disclosed, W159/W168/W169/W180 delayed-window precedent
    family -- same-window, honest);
  - lineage constants disclosed (r795/r845/r849/r852/r863 precedent,
    passed through): (a) the "wave N-1 = first free number" mat-header
    label rolls forward with its off-by-one quirk (since W165 r795);
    (b) "law sec.4 W182 row, r795" band-facts template stamp keeps its
    r795; (c) "single-window derive (r812 merged the gate legs INTO
    the pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls ninety-seventh ->
    ninety-eighth (rows 97 + candidate = 98th owned per probe leg0);
    (e) mat parity-chain rows W138..W180 keep their historical stamps
    and tuples; the W181 row (the current registered tail) is
    APPENDED with its frozen values (413_004, 415_003)/(415_004,
    415_203); (f) the "W181 finalize landed same-window r827"
    citation rolls its wave-word with the stale r827 session stamp
    riding (off-by-one wave-word + stale-session lineage quirk
    inherited; head/K values roll machine-correct to 804,518/396,120
    this window).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r867bma_w182_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W182 registration before
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
probe = json.load(open(r"results\\_r865bma_w182_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "415204_417203", "B": "417204_417403"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [415204, 417203], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [417204, 417403], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 179 and probe["legs"]["leg0"]["tail"] == "W181",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 172 and probe["legs"]["leg0"]["bma_ordinal"] == 98,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W183p_A"] == "417204..419203"
      and probe["legs"]["leg4"]["W183p_B"] == "417404..417603",
      "leg4 W183+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('182: {"a": (415_204' not in pf_o, "origin pf already carries W182 row")
check("W182 (bm-a r867 freeze" not in pf_o, "origin pf carries W182 block")
check('182: {"batch"' not in n1_o, "origin n1 already carries W182 entry")
check("# --- W182 materializer face" not in n1_o, "origin n1 carries W182 mat")
check('"r867 bm-a] "' not in n1_o, "origin n1 carries W182 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-0603-bma-w182-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "df062c5c1", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-0603-bma-w182-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w181_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W181 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w181_freeze_sha == "de699e8cd", "W181 freeze sha mismatch: " + w181_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 179, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[181] == {"a": (413_004, 415_003),
                              "b_exit": (415_004, 415_203),
                              "engine_owner": "bm-a"}, "live W181 row drift")
check(182 not in pfmod.N1_BANDS, "live N1_BANDS already has 182")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W182_PREREG.md")),
      "W182 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W182_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W182 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r867bma_w182_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r867bma_w182_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r867bma_w182_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r867bma_w182_probe_n1_claim.txt", encoding="utf-8",
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
blk182 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry182 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat182 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim182 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W182 block after the W181 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk182 + NL + "}", 1)

# n1 entry: after the W181 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry182 + NL + IND23 + "}", 1)

# n1 mat: insert the W182 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat182 + NL + seg, 1)

# n1 claim: insert the W182 attribution after the W181 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r863 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r863 bm-a] "' + NL + claim182 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W182 presence + W181 anti-vanish (r560 law)
checks = [
    (pfnew, '182: {"a": (415_204, 417_203), "b_exit": (417_204, 417_403),', 1),
    (pfnew, '181: {"a": (413_004, 415_003), "b_exit": (415_004, 415_203),', 1),
    (pfnew, "# W182 (bm-a r867 freeze", 1),
    (pfnew, "# W181 (bm-a r863 freeze", 1),
    (n1new, '182: {"batch": "PERPETUAL-N1-W182",', 1),
    (n1new, '181: {"batch": "PERPETUAL-N1-W181",', 1),
    (n1new, "# --- W182 materializer face", 1),
    (n1new, "# --- W181 materializer face", 1),
    (n1new, '"r867 bm-a] "', 1),
    (n1new, '"r863 bm-a] "', 1),
    (n1new, '"a_seed_base": 415_204,', 1),
    (n1new, '"b_exit_seed_base": 417_204,', 1),
    (n1new, "n1_w182", 4),
    (n1new, "PERPETUAL_N1_W182_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W183+ projection prose present in the new W182 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W182+ per r845 precedent, n1 fragment =
# next-wave W183+)
check("# W182+ projection (gate-derived r865)" in pfnew,
      "pf W182+ projection head missing")
check('probe_receipt.json; W183+ projection "' in n1new,
      "n1 W183+ projection head fragment missing")
check("# 417_204..419_203 CLEAN hops=0 / B first-clean 417_404..417_603" in pfnew,
      "pf W183p prose missing")
check("W183 A window; W183 freezer MUST re-derive on the post-W182" in pfnew,
      "pf W183 freezer prose missing")
check('"W183 A window; W183 freezer MUST re-derive on the "' in n1new,
      "n1 W183 freezer fragment missing")
check('"W182 B band 417_204..417_403 will refuse the naive "' in n1new,
      "n1 W182-band refuse fragment missing")

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
check('182: {"a": (415_204' not in pf_o2, "write-time: origin pf carries W182")
check('182: {"batch"' not in n1_o2, "write-time: origin n1 carries W182")
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
io.open(r"results\_r867bma_w182_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r867bma_w182_freeze_edits.py", len(out), "bytes")
