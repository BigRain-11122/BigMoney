# -*- coding: utf-8 -*-
"""r845 bm-a generator: builds results/_r845bma_w178_freeze_edits.py by
AST-extracting the r843 W177 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W178 pairs as (new843, S77(new843), cnt) -- old side =
the physical W177 face fragment (probed to dumps this window by
_r845bma_w178_face_probe.py), new side = the S77 W178 fact map applied
to that W177 fragment.  Special-case: the mat parity-chain append pair
is constructed explicitly (historical rows carry, W177 row appended).
Every derived pair old-side is verified against the physical dumps
BEFORE emission (count == cnt); S77 negatives verified after.

S77 ORDER LAW (r735 substring-order law): projections consumed BEFORE
the naive rolls that re-create their strings (proj-A before arith-A,
proj-B before naive-B, B-band before prior-B); the tail+1 pair order
kept from S75/S76 (B-tail before A-tail).

S77 LINEAGE CONSTANTS (r795 precedent, passed through):
  (a) the "wave N-1 = first free number" mat-header label rides the
  vmap verbatim (off-by-one lineage quirk since W165 r795);
  (b) "law sec.4 W178 row, r795" band-facts template stamp keeps its
  r795;
  (c) "single-window derive (r812 merged the gate legs INTO the
  pre-seat probe...)" stays (historical merge citation);
  (d) the bm-a-owned ordinal word rolls ninety-third -> ninety-fourth
  (rows 93 + candidate = 94th owned per probe leg0);
  (e) mat parity-chain rows W138..W176 keep their historical stamps
  and tuples; the W177 row (the current registered tail) is APPENDED
  with its frozen values (404_204, 406_203)/(406_204, 406_403);
  (f) the entry "W176 finalize landed same-window r827" citation
  rides the vmap verbatim (off-by-one wave-word + stale-session
  lineage quirk inherited from the r830/r834/r843 generations; the
  head/K values roll machine-correct to 795,305/387,320 this window
  -- prose session stamp stays per frozen-lineage discipline,
  disclosed here).

r587 machine-derived facts (every displayed value read from on-disk
receipts this window):
  - pre-seat probe results/_r844bma_w178_probe_receipt.json rc0 ADMIT
    (leg0 registry 175 rows tail W177 ordinal 168 / bma_ordinal 94;
    leg1 A 406_404..408_403 staircase THIRTY-EIGHTH instance E36
    hops=1 past the registered W177 B band 406_204..406_403 (W177
    sec5.5 anticipated 38th -- projection and receipt ordinals MATCH);
    naive 406_204..408_203 refused at its own start by the registered
    W177 B band; B 408_404..408_603 own-A mutual exclusion hops=1,
    naive 406_404..406_603; leg2 conflicts 0; leg3 origin vacancy
    True; leg4 W179+ projection A 408_404..410_403 hops=0 / B
    408_604..408_803 hops=0, B inside A);
  - W177 finalize landed r844 dead-tail adopted, three-gate verified
    (results/perpetual_faces/n1_w177_results.json: merged K=387,320,
    ledger head 795,305; sec7/sec8 backfill landed r845 window);
  - W177 freeze registered sha machine-derived = c06cc230f (git log
    origin/main --grep "W177 FREEZE"); W178 seat push sha
    machine-derived = 5b9284c79 (git log --diff-filter=A on the seat
    MSG inbox path); seat self-ack archive move landed r845 same
    window (processed/ path live-asserted this window);
  - per-wave prereg research/PERPETUAL_N1_W178_PREREG.md frozen at
    origin a15c62683 (r845 build, banned gate ADMIT 0 re-verified at
    freeze this window).
"""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r843 pairs --------------------------------
src = io.open(r"results\_r843bma_w177_freeze_edits.py", encoding="utf-8").read()
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

# ---------- 2. S77 = W177->W178 ordered fact map ---------------------------
S77 = [
    # -- session / finalize / sha composites (longest first) --
    ("W176 finalize one-pass bm-a r839, net chain head 793,105, ",
     "W177 finalize one-pass bm-a r844, net chain head 795,305, "),
    ("finalize one-pass bm-a r839", "finalize one-pass bm-a r844"),
    ("bm-a r839 one-pass", "bm-a r844 one-pass"),
    ("on origin since r839, not re-shipped", "on origin since r844, not re-shipped"),
    ("already on origin since r839,", "already on origin since r844,"),
    ("(gate-derived r841)", "(gate-derived r844)"),
    ("r832 probe leg4", "r841 probe leg4"),
    ("projection + r832 probe", "projection + r841 probe"),
    ("r839 sec8 succession", "r844 sec8 succession"),
    ("probe leg4 + r839 sec8", "probe leg4 + r844 sec8"),
    ("at fetch (r841 pre-seat", "at fetch (r844 pre-seat"),
    ("r565 law (r841 pre-seat", "r565 law (r844 pre-seat"),
    ("r841 same-window self-ack move", "r845 same-window self-ack move"),
    ("bm-a r834 freeze ", "bm-a r843 freeze "),
    ("(r307; bm-a r834)", "(r307; bm-a r843)"),
    ("bm-a r843 freeze,", "bm-a r845 freeze,"),
    ("r843 bm-a freeze", "r845 bm-a freeze"),
    ("r843 bm-a] ", "r845 bm-a] "),
    ("r841 receipt machine-read", "r844 receipt machine-read"),
    ("MSG-2026-10-07-2031-bma-w177-seat", "MSG-2026-10-07-2157-bma-w178-seat"),
    ("seat MSG-2030 tail,", "seat MSG-2150 tail,"),
    ("_r841bma_w177_probe_receipt.json", "_r844bma_w178_probe_receipt.json"),
    ("15ec44ea6", "c06cc230f"),
    ("780a0cd30", "5b9284c79"),
    # -- band geometry (projections FIRST, then bands, arith, prior-B,
    #    naive-B -- order law: proj consumed before the naive rolls
    #    re-create them; B-band consumed before prior-B re-creates it) --
    ("406_204..408_203", "408_404..410_403"),
    ("406_404..406_603", "408_604..408_803"),
    ("406_204..406_403", "408_404..408_603"),
    ("404_204..406_203", "406_404..408_403"),
    ("404_004..406_003", "406_204..408_203"),
    ("404_004..404_203", "406_204..406_403"),
    ("404_204..404_403", "406_404..406_603"),
    ("jumps to 406_204, first-clean ", "jumps to 408_404, first-clean "),
    ("jumps to 406_204 -> ", "jumps to 408_404 -> "),
    ("406_204 and lands ", "408_404 and lands "),
    ('177: {"a": (404_204, 406_203), "b_exit": (406_204, 406_403),',
     '178: {"a": (406_404, 408_403), "b_exit": (408_404, 408_603),'),
    # tail+1 pairs (B-tail first then A-tail, S75/S76 order kept; tail
    # roll = staircase geometry: prior B tail 406_403 / own-A tail
    # 408_403 -- machine-checked at runtime by the assert rolls)
    ("406_203+1", "408_403+1"),
    ("404_203+1", "406_403+1"),
    ('assert WAVE_CONFIGS[177]["a_seed_base"] == 404_204 == 404_203 + 1, (',
     'assert WAVE_CONFIGS[178]["a_seed_base"] == 406_404 == 406_403 + 1, ('),
    ('assert WAVE_CONFIGS[177]["b_exit_seed_base"] == 406_204 == 406_203 + 1, (',
     'assert WAVE_CONFIGS[178]["b_exit_seed_base"] == 408_404 == 408_403 + 1, ('),
    ("== 404_204 == 404_203 + 1", "== 406_404 == 406_403 + 1"),
    ("== 406_204 == 406_203 + 1", "== 408_404 == 408_403 + 1"),
    ("arith_a176", "arith_a177"),
    ("arith_b176", "arith_b177"),
    ("set(range(404_204, 406_204))", "set(range(406_404, 408_404))"),
    ("set(range(406_204, 406_404))", "set(range(408_404, 408_604))"),
    ('"a_seed_base": 404_204,', '"a_seed_base": 406_404,'),
    ('"b_exit_seed_base": 406_204,', '"b_exit_seed_base": 408_404,'),
    # -- wave-word cascade (W178 first, then downward) --
    ("W178", "W179"),
    ("W177", "W178"),
    ("W176", "W177"),
    ("W175", "W176"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SIXTY-SEVENTH", "ONE HUNDRED-AND-SIXTY-EIGHTH"),
    ("engine_owner rows 166", "engine_owner rows 167"),
    ("rows 92 + candidate", "rows 93 + candidate"),
    ("ninety-third", "ninety-fourth"),
    ("THIRTY-SEVENTH", "THIRTY-EIGHTH"),
    ("thirty-seventh", "thirty-eighth"),
    ("793,105", "795,305"),
    ("385,120", "387,320"),
    ("range(17, 177)", "range(17, 178)"),
    ("range(16, 177)", "range(16, 178)"),
    ("below 177 composes", "below 178 composes"),
    ("WAVE_CONFIGS if w < 177)", "WAVE_CONFIGS if w < 178)"),
    ("WAVE_CONFIGS[176]", "WAVE_CONFIGS[177]"),
    ('== pf.N1_BANDS[176]["a"][0]', '== pf.N1_BANDS[177]["a"][0]'),
    ('pf.N1_BANDS[176]["b_exit"][0]', 'pf.N1_BANDS[177]["b_exit"][0]'),
    ('pf.N1_BANDS[176].get("engine_owner")', 'pf.N1_BANDS[177].get("engine_owner")'),
    ("w176_a", "w177_a"),
    ("w176_b", "w177_b"),
    ("n3r1_used176", "n3r1_used177"),
    ('177: {"batch"', '178: {"batch"'),
    ("PERPETUAL_N1_W177_PREREG.md", "PERPETUAL_N1_W178_PREREG.md"),
    ("PERPETUAL-N1-W177", "PERPETUAL-N1-W178"),
    ('"n1_w177"', '"n1_w178"'),
    ('"n1_w177_results.json"', '"n1_w178_results.json"'),
    ("n1w177", "n1w178"),
    ("engine_owner=bm-a, wave 176: ", "engine_owner=bm-a, wave 177: "),
    ("wave 176 = first free number after", "wave 177 = first free number after"),
    ("_set_wave(177)", "_set_wave(178)"),
]


def s77(t):
    for old, new in S77:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W178 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r845bma_w178_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r845bma_w178_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r845bma_w178_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r845bma_w178_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD_R843 = '"registered W175 row parity drift (r307; bm-a r830)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if face == "MAT" and old == APPEND_OLD_R843:
            # special-case: chain append pair (historical rows carry; the
            # W177 row -- the current registered tail -- gets appended).
            # The old side is the W177 block's chain tail line (one
            # generation back from r843's old side -- constructed
            # explicitly, then count-verified against the dump below).
            n_old = '"registered W176 row parity drift (r307; bm-a r834)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[177] == {"a": (404_204, 406_203),' + NL +
                     '                                    "b_exit": (406_204, 406_403),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W177 row parity drift (r307; bm-a r843)"')
            if dump.count(n_old) != 1:
                fails.append("MAT append-pair old-side count %d != 1: %r" %
                             (dump.count(n_old), n_old))
            out.append((n_old, n_new, 1))
            continue
        n_old, n_new = new, s77(new)
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

# spot-check the S77 rolls before emission (fail loud, zero emission)
blk_probe = s77(DUMPS["PF"])
assert '178: {"a": (406_404, 408_403), "b_exit": (408_404, 408_603),' in blk_probe
assert "# W178 (bm-a r845 freeze" in blk_probe
assert "THIRTY-EIGHTH instance" in blk_probe
assert "# 408_404..410_403 CLEAN hops=0 / B first-clean 408_604..408_803" in blk_probe
assert "W179 A window; W179 freezer MUST re-derive on the post-W178" in blk_probe
entry_probe = s77(DUMPS["EN"])
assert '"a_seed_base": 406_404,' in entry_probe and '"b_exit_seed_base": 408_404,' in entry_probe
assert '"batch": "PERPETUAL-N1-W178",' in entry_probe
print("S77 spot-checks: PASS (pf block + mat seed rolls)")

# ---------- 4. NEG lists (mechanical: every consumed old side is a
# tripwire; append-pair old side excluded -- it legitimately remains
# as the prefix of the chain append) --------------------------------------
NEG = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    toks = []
    for n_old, n_new, _cnt in derived[key]:
        if face == "MAT" and n_old.startswith('"registered W176 row parity drift'):
            continue
        # skip no-op pairs (s77 found no roll -- wave-neutral prose that
        # legitimately remains) and partial-persistence shapes
        if n_new == n_old or n_old in n_new:
            continue
        if n_old not in toks:
            toks.append(n_old)
    # defense-in-depth extras (hand additions from the r843 NEG lists,
    # rolled one generation; harmless if absent)
    extra = {
        "PF": ["780a0cd30", "r832 probe", "r839 sec8", "r841 pre-seat",
               "_r841bma", "MSG-2026-10-07-2031", "15ec44ea6",
               "793,105", "385,120", "THIRTY-SEVENTH", "ONE HUNDRED-AND-SIXTY-SEVENTH"],
        "EN": ["15ec44ea6", "780a0cd30", "793,105", "385,120",
               "ONE HUNDRED-AND-SIXTY-SEVENTH", "rows 166", "r832 probe",
               "_r841bma", "MSG-2026-10-07-2031", "n1w177", "n1_w177",
               "PERPETUAL-N1-W177", "PERPETUAL_N1_W177", "THIRTY-SEVENTH",
               "bm-a r834 freeze", "406_204, first-clean"],
        "MAT": ["w176_", "arith_a176", "arith_b176", "n3r1_used176",
                "r832 probe", "r841 pre-seat", "15ec44ea6",
                "ONE HUNDRED-AND-SIXTY-SEVENTH", "ninety-third", "rows 166",
                "rows 92 ", "range(17, 177)", "range(16, 177)",
                "PERPETUAL_N1_W177", "PERPETUAL-N1-W177", "MSG-2030",
                "_r841bma", "r841 same-window", "n1w177", "n1_w177",
                "793,105", "385,120"],
        "CL": ["793,105", "385,120", "ONE HUNDRED-AND-SIXTY-SEVENTH",
               "ninety-third", "rows 166", "rows 92 ", "THIRTY-SEVENTH",
               "_r841bma", "r834 bm-a] "],
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


# ---------- 5. emit the W178 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r845 bm-a W178 freeze edits: four insertions (pf N1_BANDS[178] row +
n1 WAVE_CONFIGS[178] entry + n1 W178 materializer block + n1 W178
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843 dry-run
precedent: full stale+prose+AST asserts in memory BEFORE any write).

Bloodline: r819/r822/r826/r830/r834/r843 freeze-edits machinery (r773 pit
law freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W178 facts live-registry-driven (built by
_r845bma_w178_freeze_buildgen.py: old sides = the PHYSICAL W177 face
fragments probed to dumps this window, new sides = the S77 W178 fact
map, counts verified pre-emission):
  - pre-seat probe results/_r844bma_w178_probe_receipt.json rc0 ADMIT
    (A 406_404..408_403 staircase THIRTY-EIGHTH instance E36 hops=1
    past the registered W177 B band 406_204..406_403; naive
    406_204..408_203 refused at its own start by the W177 B band --
    receipt A_semantics machine-cites the W177 seat MSG leg4 + r841
    probe leg4 anticipated + MANDATED this re-derive (W177 sec5.5
    prose anticipated 38th -- projection and receipt ordinals MATCH,
    no divergence this wave); B 408_404..408_603 own-A mutual
    exclusion hops=1, naive 406_404..406_603);
  - face probe results/_r845bma_w178_face_probe_receipt.json rc0 (all
    four W177 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-07-2157-bma-w178-seat published on origin at
    5b9284c79 (r845 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- r845 same-window
    self-ack move (the W178 seat MSG sits in fleet/inbox/processed/ at
    freeze time, honest archived);
  - per-wave prereg research/PERPETUAL_N1_W178_PREREG.md frozen at
    origin a15c62683 (r845 build, banned gate ADMIT 0 re-verified at
    freeze this window);
  - W177 freeze registered sha machine-derived = c06cc230f (git log
    origin/main --grep "W177 FREEZE"); W177 finalize landed r844
    dead-tail adopted: ledger head 795,305, merged pool K=387,320
    (n1_w177_results.json machine-read; sec7/sec8 backfill landed the
    r845 window -- delayed-window precedent, honest);
  - lineage constants disclosed (r795 precedent, passed through):
    (a) the "wave N-1 = first free number" mat-header label rides the
    vmap verbatim (off-by-one lineage quirk since W165 r795);
    (b) "law sec.4 W178 row, r795" band-facts template stamp keeps its
    r795;
    (c) "single-window derive (r812 merged the gate legs INTO the
    pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls ninety-third ->
    ninety-fourth (rows 93 + candidate = 94th owned per probe leg0);
    (e) mat parity-chain rows W138..W176 keep their historical stamps
    and tuples; the W177 row (the current registered tail) is
    APPENDED with its frozen values (404_204, 406_203)/(406_204,
    406_403);
    (f) the entry "W176 finalize landed same-window r827" citation
    rides the vmap verbatim (off-by-one wave-word + stale-session
    lineage quirk inherited from the r830/r834/r843 generations; head/K
    values roll machine-correct to 795,305/387,320 this window --
    prose session stamp stays per frozen-lineage discipline).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r845bma_w178_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W178 registration before
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
probe = json.load(open(r"results\\_r844bma_w178_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "406404_408403", "B": "408404_408603"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [406404, 408403], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [408404, 408603], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 175 and probe["legs"]["leg0"]["tail"] == "W177",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 168 and probe["legs"]["leg0"]["bma_ordinal"] == 94,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W179p_A"] == "408404..410403"
      and probe["legs"]["leg4"]["W179p_B"] == "408604..408803",
      "leg4 W179+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('178: {"a": (406_404' not in pf_o, "origin pf already carries W178 row")
check("W178 (bm-a r845 freeze" not in pf_o, "origin pf carries W178 block")
check('178: {"batch"' not in n1_o, "origin n1 already carries W178 entry")
check("# --- W178 materializer face" not in n1_o, "origin n1 carries W178 mat")
check('"r845 bm-a] "' not in n1_o, "origin n1 carries W178 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-07-2157-bma-w178-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "5b9284c79", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-07-2157-bma-w178-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w177_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W177 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w177_freeze_sha == "c06cc230f", "W177 freeze sha mismatch: " + w177_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 175, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[177] == {"a": (404_204, 406_203),
                              "b_exit": (406_204, 406_403),
                              "engine_owner": "bm-a"}, "live W177 row drift")
check(178 not in pfmod.N1_BANDS, "live N1_BANDS already has 178")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W178_PREREG.md")),
      "W178 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W178_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W178 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r845bma_w178_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r845bma_w178_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r845bma_w178_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r845bma_w178_probe_n1_claim.txt", encoding="utf-8",
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
blk178 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry178 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat178 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim178 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W178 block after the W177 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk178 + NL + "}", 1)

# n1 entry: after the W177 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry178 + NL + IND23 + "}", 1)

# n1 mat: insert the W178 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat178 + NL + seg, 1)

# n1 claim: insert the W178 attribution after the W177 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r843 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r843 bm-a] "' + NL + claim178 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W178 presence + W177 anti-vanish (r560 law)
checks = [
    (pfnew, '178: {"a": (406_404, 408_403), "b_exit": (408_404, 408_603),', 1),
    (pfnew, '177: {"a": (404_204, 406_203), "b_exit": (406_204, 406_403),', 1),
    (pfnew, "# W178 (bm-a r845 freeze", 1),
    (pfnew, "# W177 (bm-a r843 freeze", 1),
    (n1new, '178: {"batch": "PERPETUAL-N1-W178",', 1),
    (n1new, '177: {"batch": "PERPETUAL-N1-W177",', 1),
    (n1new, "# --- W178 materializer face", 1),
    (n1new, "# --- W177 materializer face", 1),
    (n1new, '"r845 bm-a] "', 1),
    (n1new, '"r843 bm-a] "', 1),
    (n1new, '"a_seed_base": 406_404,', 1),
    (n1new, '"b_exit_seed_base": 408_404,', 1),
    (n1new, "n1_w178", 4),
    (n1new, "PERPETUAL_N1_W178_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W179+ projection prose present in the new W178 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law)
check("# W178+ projection (gate-derived r844)" in pfnew,
      "pf W178+ projection head missing")
check('probe_receipt.json; W179+ projection "' in n1new,
      "n1 W179+ projection head fragment missing")
check("# 408_404..410_403 CLEAN hops=0 / B first-clean 408_604..408_803" in pfnew,
      "pf W179p prose missing")
check("W179 A window; W179 freezer MUST re-derive on the post-W178" in pfnew,
      "pf W179 freezer prose missing")
check('"W179 A window; W179 freezer MUST re-derive on the "' in n1new,
      "n1 W179 freezer fragment missing")
check('"W178 B band 408_404..408_603 will refuse the naive "' in n1new,
      "n1 W178-band refuse fragment missing")

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
check('178: {"a": (406_404' not in pf_o2, "write-time: origin pf carries W178")
check('178: {"batch"' not in n1_o2, "write-time: origin n1 carries W178")
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
io.open(r"results\_r845bma_w178_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r845bma_w178_freeze_edits.py", len(out), "bytes")
