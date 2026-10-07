# -*- coding: utf-8 -*-
"""r852 bm-a generator: builds results/_r852bma_w180_freeze_edits.py by
AST-extracting the r849 W179 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W180 pairs as (new849, S80f(new849), cnt) -- old side =
the physical W179 face fragment (probed to dumps this window by
_r852bma_w180_face_probe.py), new side = the S80f W180 fact map applied
to that W179 fragment.  Special-case: the mat parity-chain append pair
is constructed explicitly (historical rows carry, W179 row appended).
Every derived pair old-side is verified against the physical dumps
BEFORE emission (count == cnt); S80f negatives verified after.

S80f ORDER LAW (r735 substring-order law): projections consumed BEFORE
the naive rolls that re-create their strings (proj-A before arith-A,
proj-B before naive-B, own-B before prior-B); the tail+1 pair order
kept from S75/S76/S77/S79 (B-tail before A-tail); composite WAVE_CONFIGS
assert pairs BEFORE the bare == rolls they contain.

S80f LINEAGE CONSTANTS (r795/r845/r849 precedent, passed through):
  (a) the "wave N-1 = first free number" mat-header label rides the
  vmap verbatim (off-by-one lineage quirk since W165 r795);
  (b) "law sec.4 W180 row, r795" band-facts template stamp keeps its
  r795;
  (c) "single-window derive (r812 merged the gate legs INTO the
  pre-seat probe...)" stays (historical merge citation);
  (d) the bm-a-owned ordinal word rolls ninety-fifth -> ninety-sixth
  (rows 95 + candidate = 96th owned per probe leg0);
  (e) mat parity-chain rows W138..W178 keep their historical stamps
  and tuples; the W179 row (the current registered tail) is APPENDED
  with its frozen values (408_604, 410_603)/(410_604, 410_803);
  (f) the "W179 finalize landed same-window r827" citation rides the
  vmap verbatim (off-by-one wave-word + stale-session lineage quirk
  inherited from the r830/r834/r843/r845/r849 generations; the head/K
  values roll machine-correct to 799,705/391,720 this window --
  prose session stamp stays per frozen-lineage discipline,
  disclosed here).

r587 machine-derived facts (every displayed value read from on-disk
receipts this window):
  - pre-seat probe results/_r851bma_w180_probe_receipt.json rc0 ADMIT
    (leg0 registry 177 rows tail W179 ordinal 170 / bma_ordinal 96;
    leg1 A 410_804..412_803 staircase FORTIETH instance E36 hops=1
    past the registered W179 B band 410_604..410_803 (W179 sec5.5
    anticipated 40th -- projection and receipt ordinals MATCH);
    naive 410_604..412_603 refused at its own start by the registered
    W179 B band; B 412_804..413_003 own-A mutual exclusion hops=1,
    naive 410_804..411_003; leg2 conflicts 0; leg3 origin vacancy
    True; leg4 W181+ projection A 412_804..414_803 hops=0 / B
    413_004..413_203 hops=0, B inside A);
  - W179 finalize landed r850 one-pass adoption closeout, three-gate
    verified (results/perpetual_faces/n1_w179_results.json: merged
    K=391,720, ledger head 799,705; sec7/sec8 backfill landed the
    r850 same window);
  - W179 freeze registered sha machine-derived = ef540bf8f (git log
    origin/main --grep "W179 FREEZE"); W180 seat push sha
    machine-derived = d3b0737fe (git log --diff-filter=A on the seat
    MSG inbox path); seat self-ack archive move landed r851 same
    window (e069782f7, processed/ path live-asserted this window);
  - per-wave prereg research/PERPETUAL_N1_W180_PREREG.md built this
    window (r852 buildgen S80 transform; banned gate ADMIT 0 verified;
    frozen at origin BEFORE this freeze commit per r565 law).
"""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r849 pairs --------------------------------
src = io.open(r"results\_r849bma_w179_freeze_edits.py", encoding="utf-8").read()
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

# ---------- 2. S80f = W179->W180 ordered fact map ---------------------------
S80F = [
    # -- session / finalize / sha composites (longest first) --
    ("W178 finalize one-pass bm-a r846, net chain head 797,505, ",
     "W179 finalize one-pass bm-a r850, net chain head 799,705, "),
    ("finalize one-pass bm-a r846", "finalize one-pass bm-a r850"),
    ("bm-a r846 one-pass", "bm-a r850 one-pass"),
    ("on origin since r846, not re-shipped", "on origin since r850, not re-shipped"),
    ("already on origin since r846,", "already on origin since r850,"),
    ("(gate-derived r848)", "(gate-derived r851)"),
    ("r844 probe leg4", "r848 probe leg4"),
    ("projection + r844 probe", "projection + r848 probe"),
    ("r846 sec8 succession", "r850 sec8 succession"),
    ("probe leg4 + r846 sec8", "probe leg4 + r850 sec8"),
    ("at fetch (r848 pre-seat", "at fetch (r851 pre-seat"),
    ("r565 law (r848 pre-seat", "r565 law (r851 pre-seat"),
    ("r848 same-window self-ack move", "r851 same-window self-ack move"),
    ("bm-a r845 freeze ", "bm-a r849 freeze "),
    ("(r307; bm-a r845)", "(r307; bm-a r849)"),
    ("bm-a r849 freeze,", "bm-a r852 freeze,"),
    ("r849 bm-a freeze", "r852 bm-a freeze"),
    ("r849 bm-a] ", "r852 bm-a] "),
    ("r848 receipt machine-read", "r851 receipt machine-read"),
    ("MSG-2026-10-07-2320-bma-w179-seat", "MSG-2026-10-08-0030-bma-w180-seat"),
    ("seat MSG-2320 tail,", "seat MSG-0030 tail,"),
    ("_r848bma_w179_probe_receipt.json", "_r851bma_w180_probe_receipt.json"),
    ("de4716da2", "ef540bf8f"),
    ("4c645c95f", "d3b0737fe"),
    # -- band geometry (projections FIRST, then bands, arith, prior-B,
    #    naive-B -- order law: proj consumed before the naive rolls
    #    re-create them; own-B consumed before prior-B re-creates it) --
    ("410_604..412_603", "412_804..414_803"),
    ("410_804..411_003", "413_004..413_203"),
    ("410_604..410_803", "412_804..413_003"),
    ("408_604..410_603", "410_804..412_803"),
    ("408_404..410_403", "410_604..412_603"),
    ("408_404..408_603", "410_604..410_803"),
    ("408_604..408_803", "410_804..411_003"),
    ("jumps to 410_604, first-clean ", "jumps to 412_804, first-clean "),
    ("jumps to 410_604 -> ", "jumps to 412_804 -> "),
    ("410_604 and lands ", "412_804 and lands "),
    ('179: {"a": (408_604, 410_603), "b_exit": (410_604, 410_803),',
     '180: {"a": (410_804, 412_803), "b_exit": (412_804, 413_003),'),
    # tail+1 pairs (B-tail first then A-tail, S75/S76/S77/S79 order kept;
    # tail roll = staircase geometry: prior B tail 410_803 / own-A tail
    # 412_803 -- machine-checked at runtime by the assert rolls)
    ("410_603+1", "412_803+1"),
    ("408_603+1", "410_803+1"),
    ('assert WAVE_CONFIGS[179]["a_seed_base"] == 408_604 == 408_603 + 1, (',
     'assert WAVE_CONFIGS[180]["a_seed_base"] == 410_804 == 410_803 + 1, ('),
    ('assert WAVE_CONFIGS[179]["b_exit_seed_base"] == 410_604 == 410_603 + 1, (',
     'assert WAVE_CONFIGS[180]["b_exit_seed_base"] == 412_804 == 412_803 + 1, ('),
    ("== 408_604 == 408_603 + 1", "== 410_804 == 410_803 + 1"),
    ("== 410_604 == 410_603 + 1", "== 412_804 == 412_803 + 1"),
    ("arith_a178", "arith_a179"),
    ("arith_b178", "arith_b179"),
    ("set(range(408_604, 410_604))", "set(range(410_804, 412_804))"),
    ("set(range(410_604, 410_804))", "set(range(412_804, 413_004))"),
    ('"a_seed_base": 408_604,', '"a_seed_base": 410_804,'),
    ('"b_exit_seed_base": 410_604,', '"b_exit_seed_base": 412_804,'),
    # -- wave-word cascade (W180 first, then downward) --
    ("W180", "W181"),
    ("W179", "W180"),
    ("W178", "W179"),
    ("W177", "W178"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SIXTY-NINTH", "ONE HUNDRED-AND-SEVENTIETH"),
    ("engine_owner rows 168", "engine_owner rows 169"),
    ("rows 94 + candidate", "rows 95 + candidate"),
    ("ninety-fifth", "ninety-sixth"),
    ("THIRTY-NINTH", "FORTIETH"),
    ("thirty-ninth", "fortieth"),
    ("797,505", "799,705"),
    ("389,520", "391,720"),
    ("range(17, 179)", "range(17, 180)"),
    ("range(16, 179)", "range(16, 180)"),
    ("below 179 composes", "below 180 composes"),
    ("WAVE_CONFIGS if w < 179)", "WAVE_CONFIGS if w < 180)"),
    ("WAVE_CONFIGS[178]", "WAVE_CONFIGS[179]"),
    ('== pf.N1_BANDS[178]["a"][0]', '== pf.N1_BANDS[179]["a"][0]'),
    ('pf.N1_BANDS[178]["b_exit"][0]', 'pf.N1_BANDS[179]["b_exit"][0]'),
    ('pf.N1_BANDS[178].get("engine_owner")', 'pf.N1_BANDS[179].get("engine_owner")'),
    ("w178_a", "w179_a"),
    ("w178_b", "w179_b"),
    ("n3r1_used178", "n3r1_used179"),
    ('179: {"batch"', '180: {"batch"'),
    ("PERPETUAL_N1_W179_PREREG.md", "PERPETUAL_N1_W180_PREREG.md"),
    ("PERPETUAL-N1-W179", "PERPETUAL-N1-W180"),
    ('"n1_w179"', '"n1_w180"'),
    ('"n1_w179_results.json"', '"n1_w180_results.json"'),
    ("n1w179", "n1w180"),
    ("engine_owner=bm-a, wave 178: ", "engine_owner=bm-a, wave 179: "),
    ("wave 178 = first free number after", "wave 179 = first free number after"),
    ("_set_wave(179)", "_set_wave(180)"),
]


def s80f(t):
    for old, new in S80F:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W180 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r852bma_w180_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r852bma_w180_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r852bma_w180_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r852bma_w180_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD_R849 = '"registered W177 row parity drift (r307; bm-a r843)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if face == "MAT" and old == APPEND_OLD_R849:
            # special-case: chain append pair (historical rows carry; the
            # W179 row -- the current registered tail -- gets appended).
            # The old side is the W180 block's chain tail line (one
            # generation back from r849's old side -- constructed
            # explicitly, then count-verified against the dump below).
            n_old = '"registered W178 row parity drift (r307; bm-a r845)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[179] == {"a": (408_604, 410_603),' + NL +
                     '                                    "b_exit": (410_604, 410_803),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W179 row parity drift (r307; bm-a r849)"')
            if dump.count(n_old) != 1:
                fails.append("MAT append-pair old-side count %d != 1: %r" %
                             (dump.count(n_old), n_old))
            out.append((n_old, n_new, 1))
            continue
        n_old, n_new = new, s80f(new)
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

# spot-check the S80f rolls before emission (fail loud, zero emission)
blk_probe = s80f(DUMPS["PF"])
assert '180: {"a": (410_804, 412_803), "b_exit": (412_804, 413_003),' in blk_probe
assert "# W180 (bm-a r852 freeze" in blk_probe
assert "FORTIETH instance" in blk_probe
assert "# 412_804..414_803 CLEAN hops=0 / B first-clean 413_004..413_203" in blk_probe
assert "W181 A window; W181 freezer MUST re-derive on the post-W180" in blk_probe
entry_probe = s80f(DUMPS["EN"])
assert '"a_seed_base": 410_804,' in entry_probe and '"b_exit_seed_base": 412_804,' in entry_probe
assert '"batch": "PERPETUAL-N1-W180",' in entry_probe
print("S80f spot-checks: PASS (pf block + mat seed rolls)")

# ---------- 4. NEG lists (mechanical: every consumed old side is a
# tripwire; append-pair old side excluded -- it legitimately remains
# as the prefix of the chain append) --------------------------------------
NEG = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    toks = []
    for n_old, n_new, _cnt in derived[key]:
        if face == "MAT" and n_old.startswith('"registered W178 row parity drift'):
            continue
        # skip no-op pairs (s80f found no roll -- wave-neutral prose that
        # legitimately remains) and partial-persistence shapes
        if n_new == n_old or n_old in n_new:
            continue
        if n_old not in toks:
            toks.append(n_old)
    # defense-in-depth extras (hand additions from the r849 NEG lists,
    # rolled one generation; harmless if absent)
    extra = {
        "PF": ["4c645c95f", "r844 probe", "r846 sec8", "r848 pre-seat",
               "_r848bma", "MSG-2026-10-07-2320", "de4716da2",
               "797,505", "389,520", "THIRTY-NINTH", "ONE HUNDRED-AND-SIXTY-NINTH"],
        "EN": ["de4716da2", "4c645c95f", "797,505", "389,520",
               "ONE HUNDRED-AND-SIXTY-NINTH", "rows 168", "r844 probe",
               "_r848bma", "MSG-2026-10-07-2320", "n1w179", "n1_w179",
               "PERPETUAL-N1-W179", "PERPETUAL_N1_W179", "THIRTY-NINTH",
               "bm-a r845 freeze", "410_604, first-clean"],
        "MAT": ["w178_", "arith_a178", "arith_b178", "n3r1_used178",
                "r844 probe", "r848 pre-seat", "de4716da2",
                "ONE HUNDRED-AND-SIXTY-NINTH", "ninety-fifth", "rows 168",
                "rows 94 ", "range(17, 179)", "range(16, 179)",
                "PERPETUAL_N1_W179", "PERPETUAL-N1-W179", "MSG-2320",
                "_r848bma", "r848 same-window", "n1w179", "n1_w179",
                "797,505", "389,520"],
        "CL": ["797,505", "389,520", "ONE HUNDRED-AND-SIXTY-NINTH",
               "ninety-fifth", "rows 168", "rows 94 ", "THIRTY-NINTH",
               "_r848bma", "r845 bm-a] "],
    }[face]
    for t in extra:
        if t not in toks:
            toks.append(t)
    NEG[face + "_NEG"] = toks

# NEG sanity (buildgen-side): every mechanical NEG token is present in
# the dump by construction (count == cnt > 0 verified above); the hand
# extras are defense-in-depth and may legitimately be absent
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


# ---------- 5. emit the W180 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r852 bm-a W180 freeze edits: four insertions (pf N1_BANDS[180] row +
n1 WAVE_CONFIGS[180] entry + n1 W180 materializer block + n1 W180
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845/r849
dry-run precedent: full stale+prose+AST asserts in memory BEFORE any
write).

Bloodline: r819/r822/r826/r830/r834/r843/r845/r849 freeze-edits machinery
(r773 pit law freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W180 facts live-registry-driven (built by
_r852bma_w180_freeze_buildgen.py: old sides = the PHYSICAL W179 face
fragments probed to dumps this window, new sides = the S80f W180 fact
map, counts verified pre-emission):
  - pre-seat probe results/_r851bma_w180_probe_receipt.json rc0 ADMIT
    (A 410_804..412_803 staircase FORTIETH instance E36 hops=1
    past the registered W179 B band 410_604..410_803; naive
    410_604..412_603 refused at its own start by the W179 B band --
    receipt A_semantics machine-cites the W179 seat MSG leg4 + r848
    probe leg4 anticipated + MANDATED this re-derive (W179 sec5.5
    prose anticipated 40th -- projection and receipt ordinals MATCH,
    no divergence this wave); B 412_804..413_003 own-A mutual
    exclusion hops=1, naive 410_804..411_003);
  - face probe results/_r852bma_w180_face_probe_receipt.json rc0 (all
    four W179 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-0030-bma-w180-seat published on origin at
    d3b0737fe (r851 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- r851 same-window
    self-ack move (the W180 seat MSG sits in fleet/inbox/processed/ at
    freeze time, honest archived; e069782f7);
  - per-wave prereg research/PERPETUAL_N1_W180_PREREG.md frozen at
    origin (r852 prereg-freeze push; banned gate ADMIT 0 re-verified
    at prereg freeze);
  - W179 freeze registered sha machine-derived = ef540bf8f (git log
    origin/main --grep "W179 FREEZE"); W179 finalize landed r850
    one-pass adoption closeout: ledger head 799,705, merged pool
    K=391,720 (n1_w179_results.json machine-read; sec7/sec8 backfill
    landed the r850 same window -- same-window, honest);
  - lineage constants disclosed (r795/r845/r849 precedent, passed
    through): (a) the "wave N-1 = first free number" mat-header label
    rides the vmap verbatim (off-by-one lineage quirk since W165
    r795); (b) "law sec.4 W180 row, r795" band-facts template stamp
    keeps its r795; (c) "single-window derive (r812 merged the gate
    legs INTO the pre-seat probe...)" stays (historical merge
    citation); (d) the bm-a-owned ordinal word rolls ninety-fifth ->
    ninety-sixth (rows 95 + candidate = 96th owned per probe leg0);
    (e) mat parity-chain rows W138..W178 keep their historical stamps
    and tuples; the W179 row (the current registered tail) is
    APPENDED with its frozen values (408_604, 410_603)/(410_604,
    410_803); (f) the "W179 finalize landed same-window r827"
    citation rides the vmap verbatim (off-by-one wave-word +
    stale-session lineage quirk inherited; head/K values roll
    machine-correct to 799,705/391,720 this window).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r852bma_w180_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W180 registration before
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
probe = json.load(open(r"results\\_r851bma_w180_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "410804_412803", "B": "412804_413003"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [410804, 412803], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [412804, 413003], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 177 and probe["legs"]["leg0"]["tail"] == "W179",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 170 and probe["legs"]["leg0"]["bma_ordinal"] == 96,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W181p_A"] == "412804..414803"
      and probe["legs"]["leg4"]["W181p_B"] == "413004..413203",
      "leg4 W181+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('180: {"a": (410_804' not in pf_o, "origin pf already carries W180 row")
check("W180 (bm-a r852 freeze" not in pf_o, "origin pf carries W180 block")
check('180: {"batch"' not in n1_o, "origin n1 already carries W180 entry")
check("# --- W180 materializer face" not in n1_o, "origin n1 carries W180 mat")
check('"r852 bm-a] "' not in n1_o, "origin n1 carries W180 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-0030-bma-w180-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "d3b0737fe", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-0030-bma-w180-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w179_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W179 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w179_freeze_sha == "ef540bf8f", "W179 freeze sha mismatch: " + w179_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 177, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[179] == {"a": (408_604, 410_603),
                              "b_exit": (410_604, 410_803),
                              "engine_owner": "bm-a"}, "live W179 row drift")
check(180 not in pfmod.N1_BANDS, "live N1_BANDS already has 180")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W180_PREREG.md")),
      "W180 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W180_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W180 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r852bma_w180_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r852bma_w180_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r852bma_w180_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r852bma_w180_probe_n1_claim.txt", encoding="utf-8",
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
blk180 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry180 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat180 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim180 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W180 block after the W179 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk180 + NL + "}", 1)

# n1 entry: after the W179 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry180 + NL + IND23 + "}", 1)

# n1 mat: insert the W180 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat180 + NL + seg, 1)

# n1 claim: insert the W180 attribution after the W179 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r849 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r849 bm-a] "' + NL + claim180 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W180 presence + W179 anti-vanish (r560 law)
checks = [
    (pfnew, '180: {"a": (410_804, 412_803), "b_exit": (412_804, 413_003),', 1),
    (pfnew, '179: {"a": (408_604, 410_603), "b_exit": (410_604, 410_803),', 1),
    (pfnew, "# W180 (bm-a r852 freeze", 1),
    (pfnew, "# W179 (bm-a r849 freeze", 1),
    (n1new, '180: {"batch": "PERPETUAL-N1-W180",', 1),
    (n1new, '179: {"batch": "PERPETUAL-N1-W179",', 1),
    (n1new, "# --- W180 materializer face", 1),
    (n1new, "# --- W179 materializer face", 1),
    (n1new, '"r852 bm-a] "', 1),
    (n1new, '"r849 bm-a] "', 1),
    (n1new, '"a_seed_base": 410_804,', 1),
    (n1new, '"b_exit_seed_base": 412_804,', 1),
    (n1new, "n1_w180", 4),
    (n1new, "PERPETUAL_N1_W180_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W181+ projection prose present in the new W180 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W180+ per r845 precedent, n1 fragment = next-wave
# W181+)
check("# W180+ projection (gate-derived r851)" in pfnew,
      "pf W180+ projection head missing")
check('probe_receipt.json; W181+ projection "' in n1new,
      "n1 W181+ projection head fragment missing")
check("# 412_804..414_803 CLEAN hops=0 / B first-clean 413_004..413_203" in pfnew,
      "pf W181p prose missing")
check("W181 A window; W181 freezer MUST re-derive on the post-W180" in pfnew,
      "pf W181 freezer prose missing")
check('"W181 A window; W181 freezer MUST re-derive on the "' in n1new,
      "n1 W181 freezer fragment missing")
check('"W180 B band 412_804..413_003 will refuse the naive "' in n1new,
      "n1 W180-band refuse fragment missing")

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
check('180: {"a": (410_804' not in pf_o2, "write-time: origin pf carries W180")
check('180: {"batch"' not in n1_o2, "write-time: origin n1 carries W180")
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
io.open(r"results\_r852bma_w180_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r852bma_w180_freeze_edits.py", len(out), "bytes")
