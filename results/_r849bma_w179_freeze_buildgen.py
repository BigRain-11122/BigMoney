# -*- coding: utf-8 -*-
"""r849 bm-a generator: builds results/_r849bma_w179_freeze_edits.py by
AST-extracting the r845 W178 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W179 pairs as (new845, S79f(new845), cnt) -- old side =
the physical W178 face fragment (probed to dumps this window by
_r849bma_w179_face_probe.py), new side = the S79f W179 fact map applied
to that W178 fragment.  Special-case: the mat parity-chain append pair
is constructed explicitly (historical rows carry, W178 row appended).
Every derived pair old-side is verified against the physical dumps
BEFORE emission (count == cnt); S79f negatives verified after.

S79f ORDER LAW (r735 substring-order law): projections consumed BEFORE
the naive rolls that re-create their strings (proj-A before arith-A,
proj-B before naive-B, B-band before prior-B); the tail+1 pair order
kept from S75/S76/S77 (B-tail before A-tail).

S79f LINEAGE CONSTANTS (r795/r845 precedent, passed through):
  (a) the "wave N-1 = first free number" mat-header label rides the
  vmap verbatim (off-by-one lineage quirk since W165 r795);
  (b) "law sec.4 W179 row, r795" band-facts template stamp keeps its
  r795;
  (c) "single-window derive (r812 merged the gate legs INTO the
  pre-seat probe...)" stays (historical merge citation);
  (d) the bm-a-owned ordinal word rolls ninety-fourth -> ninety-fifth
  (rows 94 + candidate = 95th owned per probe leg0);
  (e) mat parity-chain rows W138..W177 keep their historical stamps
  and tuples; the W178 row (the current registered tail) is APPENDED
  with its frozen values (406_404, 408_403)/(408_404, 408_603);
  (f) the "W178 finalize landed same-window r827" citation rides the
  vmap verbatim (off-by-one wave-word + stale-session lineage quirk
  inherited from the r830/r834/r843/r845 generations; the head/K
  values roll machine-correct to 797,505/389,520 this window --
  prose session stamp stays per frozen-lineage discipline,
  disclosed here).

r587 machine-derived facts (every displayed value read from on-disk
receipts this window):
  - pre-seat probe results/_r848bma_w179_probe_receipt.json rc0 ADMIT
    (leg0 registry 176 rows tail W178 ordinal 169 / bma_ordinal 95;
    leg1 A 408_604..410_603 staircase THIRTY-NINTH instance E36
    hops=1 past the registered W178 B band 408_404..408_603 (W178
    sec5.5 anticipated 39th -- projection and receipt ordinals MATCH);
    naive 408_404..410_403 refused at its own start by the registered
    W178 B band; B 410_604..410_803 own-A mutual exclusion hops=1,
    naive 408_604..408_803; leg2 conflicts 0; leg3 origin vacancy
    True; leg4 W180+ projection A 410_604..412_603 hops=0 / B
    410_804..411_003 hops=0, B inside A);
  - W178 finalize landed r846 one-pass adoption closeout, three-gate
    verified (results/perpetual_faces/n1_w178_results.json: merged
    K=389,520, ledger head 797,505; sec7/sec8 backfill landed the
    r846 same window);
  - W178 freeze registered sha machine-derived = de4716da2 (git log
    origin/main --grep "W178 FREEZE"); W179 seat push sha
    machine-derived = 4c645c95f (git log --diff-filter=A on the seat
    MSG inbox path); seat self-ack archive move landed r848 same
    window (processed/ path live-asserted this window);
  - per-wave prereg research/PERPETUAL_N1_W179_PREREG.md frozen at
    origin 6f14c35d5 (r849 surgical-path push behind bm-c r706/707
    race, r523 live-daemon law; banned gate ADMIT 0 re-verified at
    prereg freeze this window).
"""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r845 pairs --------------------------------
src = io.open(r"results\_r845bma_w178_freeze_edits.py", encoding="utf-8").read()
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

# ---------- 2. S79f = W178->W179 ordered fact map ---------------------------
S79F = [
    # -- session / finalize / sha composites (longest first) --
    ("W177 finalize one-pass bm-a r844, net chain head 795,305, ",
     "W178 finalize one-pass bm-a r846, net chain head 797,505, "),
    ("finalize one-pass bm-a r844", "finalize one-pass bm-a r846"),
    ("bm-a r844 one-pass", "bm-a r846 one-pass"),
    ("on origin since r844, not re-shipped", "on origin since r846, not re-shipped"),
    ("already on origin since r844,", "already on origin since r846,"),
    ("(gate-derived r844)", "(gate-derived r848)"),
    ("r841 probe leg4", "r844 probe leg4"),
    ("projection + r841 probe", "projection + r844 probe"),
    ("r844 sec8 succession", "r846 sec8 succession"),
    ("probe leg4 + r844 sec8", "probe leg4 + r846 sec8"),
    ("at fetch (r844 pre-seat", "at fetch (r848 pre-seat"),
    ("r565 law (r844 pre-seat", "r565 law (r848 pre-seat"),
    ("r845 same-window self-ack move", "r848 same-window self-ack move"),
    ("bm-a r843 freeze ", "bm-a r845 freeze "),
    ("(r307; bm-a r843)", "(r307; bm-a r845)"),
    ("bm-a r845 freeze,", "bm-a r849 freeze,"),
    ("r845 bm-a freeze", "r849 bm-a freeze"),
    ("r845 bm-a] ", "r849 bm-a] "),
    ("r844 receipt machine-read", "r848 receipt machine-read"),
    ("MSG-2026-10-07-2157-bma-w178-seat", "MSG-2026-10-07-2320-bma-w179-seat"),
    ("seat MSG-2150 tail,", "seat MSG-2320 tail,"),
    ("_r844bma_w178_probe_receipt.json", "_r848bma_w179_probe_receipt.json"),
    ("c06cc230f", "de4716da2"),
    ("5b9284c79", "4c645c95f"),
    # -- band geometry (projections FIRST, then bands, arith, prior-B,
    #    naive-B -- order law: proj consumed before the naive rolls
    #    re-create them; B-band consumed before prior-B re-creates it) --
    ("408_404..410_403", "410_604..412_603"),
    ("408_604..408_803", "410_804..411_003"),
    ("408_404..408_603", "410_604..410_803"),
    ("406_404..408_403", "408_604..410_603"),
    ("406_204..408_203", "408_404..410_403"),
    ("406_204..406_403", "408_404..408_603"),
    ("406_404..406_603", "408_604..408_803"),
    ("jumps to 408_404, first-clean ", "jumps to 410_604, first-clean "),
    ("jumps to 408_404 -> ", "jumps to 410_604 -> "),
    ("408_404 and lands ", "410_604 and lands "),
    ('178: {"a": (406_404, 408_403), "b_exit": (408_404, 408_603),',
     '179: {"a": (408_604, 410_603), "b_exit": (410_604, 410_803),'),
    # tail+1 pairs (B-tail first then A-tail, S75/S76/S77 order kept; tail
    # roll = staircase geometry: prior B tail 408_603 / own-A tail
    # 410_603 -- machine-checked at runtime by the assert rolls)
    ("408_403+1", "410_603+1"),
    ("406_403+1", "408_603+1"),
    ('assert WAVE_CONFIGS[178]["a_seed_base"] == 406_404 == 406_403 + 1, (',
     'assert WAVE_CONFIGS[179]["a_seed_base"] == 408_604 == 408_603 + 1, ('),
    ('assert WAVE_CONFIGS[178]["b_exit_seed_base"] == 408_404 == 408_403 + 1, (',
     'assert WAVE_CONFIGS[179]["b_exit_seed_base"] == 410_604 == 410_603 + 1, ('),
    ("== 406_404 == 406_403 + 1", "== 408_604 == 408_603 + 1"),
    ("== 408_404 == 408_403 + 1", "== 410_604 == 410_603 + 1"),
    ("arith_a177", "arith_a178"),
    ("arith_b177", "arith_b178"),
    ("set(range(406_404, 408_404))", "set(range(408_604, 410_604))"),
    ("set(range(408_404, 408_604))", "set(range(410_604, 410_804))"),
    ('"a_seed_base": 406_404,', '"a_seed_base": 408_604,'),
    ('"b_exit_seed_base": 408_404,', '"b_exit_seed_base": 410_604,'),
    # -- wave-word cascade (W180 first, then downward) --
    ("W179", "W180"),
    ("W178", "W179"),
    ("W177", "W178"),
    ("W176", "W177"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SIXTY-EIGHTH", "ONE HUNDRED-AND-SIXTY-NINTH"),
    ("engine_owner rows 167", "engine_owner rows 168"),
    ("rows 93 + candidate", "rows 94 + candidate"),
    ("ninety-fourth", "ninety-fifth"),
    ("THIRTY-EIGHTH", "THIRTY-NINTH"),
    ("thirty-eighth", "thirty-ninth"),
    ("795,305", "797,505"),
    ("387,320", "389,520"),
    ("range(17, 178)", "range(17, 179)"),
    ("range(16, 178)", "range(16, 179)"),
    ("below 178 composes", "below 179 composes"),
    ("WAVE_CONFIGS if w < 178)", "WAVE_CONFIGS if w < 179)"),
    ("WAVE_CONFIGS[177]", "WAVE_CONFIGS[178]"),
    ('== pf.N1_BANDS[177]["a"][0]', '== pf.N1_BANDS[178]["a"][0]'),
    ('pf.N1_BANDS[177]["b_exit"][0]', 'pf.N1_BANDS[178]["b_exit"][0]'),
    ('pf.N1_BANDS[177].get("engine_owner")', 'pf.N1_BANDS[178].get("engine_owner")'),
    ("w177_a", "w178_a"),
    ("w177_b", "w178_b"),
    ("n3r1_used177", "n3r1_used178"),
    ('178: {"batch"', '179: {"batch"'),
    ("PERPETUAL_N1_W178_PREREG.md", "PERPETUAL_N1_W179_PREREG.md"),
    ("PERPETUAL-N1-W178", "PERPETUAL-N1-W179"),
    ('"n1_w178"', '"n1_w179"'),
    ('"n1_w178_results.json"', '"n1_w179_results.json"'),
    ("n1w178", "n1w179"),
    ("engine_owner=bm-a, wave 177: ", "engine_owner=bm-a, wave 178: "),
    ("wave 177 = first free number after", "wave 178 = first free number after"),
    ("_set_wave(178)", "_set_wave(179)"),
]


def s79f(t):
    for old, new in S79F:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W179 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r849bma_w179_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r849bma_w179_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r849bma_w179_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r849bma_w179_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD_R845 = '"registered W176 row parity drift (r307; bm-a r834)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if face == "MAT" and old == APPEND_OLD_R845:
            # special-case: chain append pair (historical rows carry; the
            # W178 row -- the current registered tail -- gets appended).
            # The old side is the W179 block's chain tail line (one
            # generation back from r845's old side -- constructed
            # explicitly, then count-verified against the dump below).
            n_old = '"registered W177 row parity drift (r307; bm-a r843)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[178] == {"a": (406_404, 408_403),' + NL +
                     '                                    "b_exit": (408_404, 408_603),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W178 row parity drift (r307; bm-a r845)"')
            if dump.count(n_old) != 1:
                fails.append("MAT append-pair old-side count %d != 1: %r" %
                             (dump.count(n_old), n_old))
            out.append((n_old, n_new, 1))
            continue
        n_old, n_new = new, s79f(new)
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

# spot-check the S79f rolls before emission (fail loud, zero emission)
blk_probe = s79f(DUMPS["PF"])
assert '179: {"a": (408_604, 410_603), "b_exit": (410_604, 410_803),' in blk_probe
assert "# W179 (bm-a r849 freeze" in blk_probe
assert "THIRTY-NINTH instance" in blk_probe
assert "# 410_604..412_603 CLEAN hops=0 / B first-clean 410_804..411_003" in blk_probe
assert "W180 A window; W180 freezer MUST re-derive on the post-W179" in blk_probe
entry_probe = s79f(DUMPS["EN"])
assert '"a_seed_base": 408_604,' in entry_probe and '"b_exit_seed_base": 410_604,' in entry_probe
assert '"batch": "PERPETUAL-N1-W179",' in entry_probe
print("S79f spot-checks: PASS (pf block + mat seed rolls)")

# ---------- 4. NEG lists (mechanical: every consumed old side is a
# tripwire; append-pair old side excluded -- it legitimately remains
# as the prefix of the chain append) --------------------------------------
NEG = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    toks = []
    for n_old, n_new, _cnt in derived[key]:
        if face == "MAT" and n_old.startswith('"registered W177 row parity drift'):
            continue
        # skip no-op pairs (s79f found no roll -- wave-neutral prose that
        # legitimately remains) and partial-persistence shapes
        if n_new == n_old or n_old in n_new:
            continue
        if n_old not in toks:
            toks.append(n_old)
    # defense-in-depth extras (hand additions from the r845 NEG lists,
    # rolled one generation; harmless if absent)
    extra = {
        "PF": ["5b9284c79", "r841 probe", "r844 sec8", "r844 pre-seat",
               "_r844bma", "MSG-2026-10-07-2157", "c06cc230f",
               "795,305", "387,320", "THIRTY-EIGHTH", "ONE HUNDRED-AND-SIXTY-EIGHTH"],
        "EN": ["c06cc230f", "5b9284c79", "795,305", "387,320",
               "ONE HUNDRED-AND-SIXTY-EIGHTH", "rows 167", "r841 probe",
               "_r844bma", "MSG-2026-10-07-2157", "n1w178", "n1_w178",
               "PERPETUAL-N1-W178", "PERPETUAL_N1_W178", "THIRTY-EIGHTH",
               "bm-a r843 freeze", "408_404, first-clean"],
        "MAT": ["w177_", "arith_a177", "arith_b177", "n3r1_used177",
                "r841 probe", "r844 pre-seat", "c06cc230f",
                "ONE HUNDRED-AND-SIXTY-EIGHTH", "ninety-fourth", "rows 167",
                "rows 93 ", "range(17, 178)", "range(16, 178)",
                "PERPETUAL_N1_W178", "PERPETUAL-N1-W178", "MSG-2150",
                "_r844bma", "r845 same-window", "n1w178", "n1_w178",
                "795,305", "387,320"],
        "CL": ["795,305", "387,320", "ONE HUNDRED-AND-SIXTY-EIGHTH",
               "ninety-fourth", "rows 167", "rows 93 ", "THIRTY-EIGHTH",
               "_r844bma", "r843 bm-a] "],
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


# ---------- 5. emit the W179 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r849 bm-a W179 freeze edits: four insertions (pf N1_BANDS[179] row +
n1 WAVE_CONFIGS[179] entry + n1 W179 materializer block + n1 W179
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845
dry-run precedent: full stale+prose+AST asserts in memory BEFORE any
write).

Bloodline: r819/r822/r826/r830/r834/r843/r845 freeze-edits machinery (r773 pit
law freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W179 facts live-registry-driven (built by
_r849bma_w179_freeze_buildgen.py: old sides = the PHYSICAL W178 face
fragments probed to dumps this window, new sides = the S79f W179 fact
map, counts verified pre-emission):
  - pre-seat probe results/_r848bma_w179_probe_receipt.json rc0 ADMIT
    (A 408_604..410_603 staircase THIRTY-NINTH instance E36 hops=1
    past the registered W178 B band 408_404..408_603; naive
    408_404..410_403 refused at its own start by the W178 B band --
    receipt A_semantics machine-cites the W178 seat MSG leg4 + r844
    probe leg4 anticipated + MANDATED this re-derive (W178 sec5.5
    prose anticipated 39th -- projection and receipt ordinals MATCH,
    no divergence this wave); B 410_604..410_803 own-A mutual
    exclusion hops=1, naive 408_604..408_803);
  - face probe results/_r849bma_w179_face_probe_receipt.json rc0 (all
    four W178 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-07-2320-bma-w179-seat published on origin at
    4c645c95f (r848 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- r848 same-window
    self-ack move (the W179 seat MSG sits in fleet/inbox/processed/ at
    freeze time, honest archived);
  - per-wave prereg research/PERPETUAL_N1_W179_PREREG.md frozen at
    origin 6f14c35d5 (r849 surgical-path push behind bm-c r706/707
    race; banned gate ADMIT 0 re-verified at prereg freeze);
  - W178 freeze registered sha machine-derived = de4716da2 (git log
    origin/main --grep "W178 FREEZE"); W178 finalize landed r846
    one-pass adoption closeout: ledger head 797,505, merged pool
    K=389,520 (n1_w178_results.json machine-read; sec7/sec8 backfill
    landed the r846 same window -- same-window, honest);
  - lineage constants disclosed (r795/r845 precedent, passed through):
    (a) the "wave N-1 = first free number" mat-header label rides the
    vmap verbatim (off-by-one lineage quirk since W165 r795);
    (b) "law sec.4 W179 row, r795" band-facts template stamp keeps its
    r795;
    (c) "single-window derive (r812 merged the gate legs INTO the
    pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls ninety-fourth ->
    ninety-fifth (rows 94 + candidate = 95th owned per probe leg0);
    (e) mat parity-chain rows W138..W177 keep their historical stamps
    and tuples; the W178 row (the current registered tail) is
    APPENDED with its frozen values (406_404, 408_403)/(408_404,
    408_603);
    (f) the "W178 finalize landed same-window r827" citation rides
    the vmap verbatim (off-by-one wave-word + stale-session lineage
    quirk inherited from the r830/r834/r843/r845 generations; head/K
    values roll machine-correct to 797,505/389,520 this window --
    prose session stamp stays per frozen-lineage discipline).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r849bma_w179_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W179 registration before
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
probe = json.load(open(r"results\\_r848bma_w179_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "408604_410603", "B": "410604_410803"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [408604, 410603], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [410604, 410803], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 176 and probe["legs"]["leg0"]["tail"] == "W178",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 169 and probe["legs"]["leg0"]["bma_ordinal"] == 95,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W180p_A"] == "410604..412603"
      and probe["legs"]["leg4"]["W180p_B"] == "410804..411003",
      "leg4 W180+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('179: {"a": (408_604' not in pf_o, "origin pf already carries W179 row")
check("W179 (bm-a r849 freeze" not in pf_o, "origin pf carries W179 block")
check('179: {"batch"' not in n1_o, "origin n1 already carries W179 entry")
check("# --- W179 materializer face" not in n1_o, "origin n1 carries W179 mat")
check('"r849 bm-a] "' not in n1_o, "origin n1 carries W179 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-07-2320-bma-w179-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "4c645c95f", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-07-2320-bma-w179-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w178_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W178 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w178_freeze_sha == "de4716da2", "W178 freeze sha mismatch: " + w178_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 176, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[178] == {"a": (406_404, 408_403),
                              "b_exit": (408_404, 408_603),
                              "engine_owner": "bm-a"}, "live W178 row drift")
check(179 not in pfmod.N1_BANDS, "live N1_BANDS already has 179")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W179_PREREG.md")),
      "W179 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W179_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W179 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r849bma_w179_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r849bma_w179_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r849bma_w179_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r849bma_w179_probe_n1_claim.txt", encoding="utf-8",
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
blk179 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry179 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat179 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim179 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W179 block after the W178 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk179 + NL + "}", 1)

# n1 entry: after the W178 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry179 + NL + IND23 + "}", 1)

# n1 mat: insert the W179 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat179 + NL + seg, 1)

# n1 claim: insert the W179 attribution after the W178 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r845 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r845 bm-a] "' + NL + claim179 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W179 presence + W178 anti-vanish (r560 law)
checks = [
    (pfnew, '179: {"a": (408_604, 410_603), "b_exit": (410_604, 410_803),', 1),
    (pfnew, '178: {"a": (406_404, 408_403), "b_exit": (408_404, 408_603),', 1),
    (pfnew, "# W179 (bm-a r849 freeze", 1),
    (pfnew, "# W178 (bm-a r845 freeze", 1),
    (n1new, '179: {"batch": "PERPETUAL-N1-W179",', 1),
    (n1new, '178: {"batch": "PERPETUAL-N1-W178",', 1),
    (n1new, "# --- W179 materializer face", 1),
    (n1new, "# --- W178 materializer face", 1),
    (n1new, '"r849 bm-a] "', 1),
    (n1new, '"r845 bm-a] "', 1),
    (n1new, '"a_seed_base": 408_604,', 1),
    (n1new, '"b_exit_seed_base": 410_604,', 1),
    (n1new, "n1_w179", 4),
    (n1new, "PERPETUAL_N1_W179_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W180+ projection prose present in the new W179 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W179+ per r845 precedent, n1 fragment = next-wave
# W180+)
check("# W179+ projection (gate-derived r848)" in pfnew,
      "pf W179+ projection head missing")
check('probe_receipt.json; W180+ projection "' in n1new,
      "n1 W180+ projection head fragment missing")
check("# 410_604..412_603 CLEAN hops=0 / B first-clean 410_804..411_003" in pfnew,
      "pf W180p prose missing")
check("W180 A window; W180 freezer MUST re-derive on the post-W179" in pfnew,
      "pf W180 freezer prose missing")
check('"W180 A window; W180 freezer MUST re-derive on the "' in n1new,
      "n1 W180 freezer fragment missing")
check('"W179 B band 410_604..410_803 will refuse the naive "' in n1new,
      "n1 W179-band refuse fragment missing")

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
check('179: {"a": (408_604' not in pf_o2, "write-time: origin pf carries W179")
check('179: {"batch"' not in n1_o2, "write-time: origin n1 carries W179")
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
io.open(r"results\_r849bma_w179_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r849bma_w179_freeze_edits.py", len(out), "bytes")
