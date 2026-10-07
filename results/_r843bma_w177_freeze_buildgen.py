# -*- coding: utf-8 -*-
"""r843 bm-a generator: builds results/_r843bma_w177_freeze_edits.py by
AST-extracting the r834 W176 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W177 pairs as (new176, S76(new176), cnt) -- old side =
the physical W176 face fragment (probed to dumps this window by
_r843bma_w177_face_probe.py), new side = the S76 W177 fact map applied
to that W176 fragment.  Special-case: the mat parity-chain append pair
is constructed explicitly (historical rows carry, W176 row appended).
Every derived pair old-side is verified against the physical dumps
BEFORE emission (count == cnt); S76 negatives verified after.

r587 machine-derived facts (every displayed value read from on-disk
receipts this window):
  - pre-seat probe results/_r841bma_w177_probe_receipt.json rc0 ADMIT
    (leg0 registry 174 rows tail W176 ordinal 167 / bma_ordinal 93;
    leg1 A 404_204..406_203 hops=1 / B 406_204..406_403 hops=1 / naive
    A 404_004..406_003 refused at its own start by the registered W176
    B band 404_004..404_203 (staircase THIRTY-SEVENTH instance E36 per
    receipt A_semantics; W176 sec5.5 prose anticipated 37th --
    projection and receipt ordinals MATCH, no divergence face this
    wave); naive B 404_204..404_403 lands inside own-A
    404_204..406_203; leg2 conflicts 0; leg3 origin vacancy True;
    leg4 W178+ projection A 406_204..408_203 hops=0 / B
    406_404..406_603 hops=0, B inside A);
  - W176 finalize one-pass landed r839
    (results/perpetual_faces/n1_w176_results.json: merged K=385,120,
    ledger head 793,105);
  - W176 freeze registered sha machine-derived = 15ec44ea6 (git log
    origin/main --grep "W176 FREEZE"); W177 seat push sha
    machine-derived = 780a0cd30 (git log --diff-filter=A on the seat
    MSG inbox path); seat self-ack archive move landed r841 same
    window (processed/ path live-asserted this window);
  - per-wave prereg research/PERPETUAL_N1_W177_PREREG.md frozen at
    origin 821a03feb (r842 build, banned gate ADMIT 0 re-verified at
    freeze this window).

S76 ORDER LAW (r735 substring-order law): projections consumed BEFORE
the naive rolls that re-create their strings (proj-A before naive-A,
proj-B before naive-B, B-band before prior-B-band); the tail+1 pair
order kept from S75 (B-tail before A-tail; no cross-recreation this
generation -- counts gate proves).

S76 LINEAGE CONSTANTS (r795 precedent, passed through):
  (a) the "wave N-1 = first free number" mat-header label rides the
  vmap verbatim (off-by-one lineage quirk since W165 r795);
  (b) "law sec.4 W177 row, r795" band-facts template stamp keeps its
  r795;
  (c) "single-window derive (r812 merged the gate legs INTO the
  pre-seat probe...)" stays (historical merge citation);
  (d) the bm-a-owned ordinal word rolls ninety-second -> ninety-third
  (rows 92 + candidate = 93rd owned per probe leg0);
  (e) mat parity-chain rows W138..W175 keep their historical stamps
  and tuples; the W176 row (the current registered tail) is APPENDED
  with its frozen values (402_004, 404_003)/(404_004, 404_203);
  (f) the entry "W176 finalize landed same-window r827" citation
  rides the vmap verbatim (off-by-one wave-word + stale-session
  lineage quirk inherited from the r830/r834 generations; the
  head/K values roll machine-correct to 793,105/385,120 this window
  -- prose session stamp stays r827 per frozen-lineage discipline,
  disclosed here).
"""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r834 pairs --------------------------------
src = io.open(r"results\_r834bma_w176_freeze_edits.py", encoding="utf-8").read()
tree = ast.parse(src)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        return ev(n.left) + ev(n.right)
    if isinstance(n, ast.Name) and n.id == "NL":
        return NL
    raise AssertionError("unsupported node %r" % (n,))


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

# ---------- 2. S76 = W176->W177 ordered fact map ---------------------------
S76 = [
    # -- session / finalize / sha composites (longest first) --
    ("W175 finalize one-pass bm-a r831, net chain head 790,412, ",
     "W176 finalize one-pass bm-a r839, net chain head 793,105, "),
    ("finalize one-pass bm-a r831", "finalize one-pass bm-a r839"),
    ("bm-a r831 one-pass", "bm-a r839 one-pass"),
    ("on origin since r831, not re-shipped", "on origin since r839, not re-shipped"),
    ("already on origin since r831,", "already on origin since r839,"),
    ("(gate-derived r832)", "(gate-derived r841)"),
    ("r828 probe leg4", "r832 probe leg4"),
    ("projection + r828 probe", "projection + r832 probe"),
    ("r831 sec8 succession", "r839 sec8 succession"),
    ("probe leg4 + r831 sec8", "probe leg4 + r839 sec8"),
    ("at fetch (r832 pre-seat", "at fetch (r841 pre-seat"),
    ("r565 law (r832 pre-seat", "r565 law (r841 pre-seat"),
    ("r833 same-window self-ack move", "r841 same-window self-ack move"),
    ("bm-a r830 freeze ", "bm-a r834 freeze "),
    ("(r307; bm-a r830)", "(r307; bm-a r834)"),
    ("bm-a r834 freeze,", "bm-a r843 freeze,"),
    ("r834 bm-a freeze", "r843 bm-a freeze"),
    ("r834 bm-a] ", "r843 bm-a] "),
    ("r832 receipt machine-read", "r841 receipt machine-read"),
    ("MSG-2026-10-07-1630-bma-w176-seat", "MSG-2026-10-07-2031-bma-w177-seat"),
    ("seat MSG-1630 tail,", "seat MSG-2030 tail,"),
    ("_r832bma_w176_probe_receipt.json", "_r841bma_w177_probe_receipt.json"),
    ("f3fca4055", "15ec44ea6"),
    ("16a8ea982", "780a0cd30"),
    # -- band geometry (projections FIRST, then bands, naives, prior-B --
    # order law: proj consumed before the naive rolls re-create them;
    # B-band consumed before prior-B re-creates the B-band source)
    ("404_004..406_003", "406_204..408_203"),
    ("404_204..404_403", "406_404..406_603"),
    ("402_004..404_003", "404_204..406_203"),
    ("404_004..404_203", "406_204..406_403"),
    ("401_804..403_803", "404_004..406_003"),
    ("402_004..402_203", "404_204..404_403"),
    ("401_804..402_003", "404_004..404_203"),
    ("jumps to 404_004, first-clean ", "jumps to 406_204, first-clean "),
    ("jumps to 404_004 -> ", "jumps to 406_204 -> "),
    ("404_004 and lands ", "406_204 and lands "),
    ('176: {"a": (402_004, 404_003), "b_exit": (404_004, 404_203),',
     '177: {"a": (404_204, 406_203), "b_exit": (406_204, 406_403),'),
    # tail+1 pairs (B-tail first then A-tail, S75 order kept; tail
    # roll = staircase geometry: prior B tail 404_203 / own-A tail
    # 406_203 -- machine-checked at runtime by the assert rolls)
    ("404_003+1", "406_203+1"),
    ("402_003+1", "404_203+1"),
    ('assert WAVE_CONFIGS[176]["a_seed_base"] == 402_004 == 402_003 + 1, (',
     'assert WAVE_CONFIGS[177]["a_seed_base"] == 404_204 == 404_203 + 1, ('),
    ('assert WAVE_CONFIGS[176]["b_exit_seed_base"] == 404_004 == 404_003 + 1, (',
     'assert WAVE_CONFIGS[177]["b_exit_seed_base"] == 406_204 == 406_203 + 1, ('),
    ("== 402_004 == 402_003 + 1", "== 404_204 == 404_203 + 1"),
    ("== 404_004 == 404_003 + 1", "== 406_204 == 406_203 + 1"),
    ("arith_a175", "arith_a176"),
    ("arith_b175", "arith_b176"),
    ("set(range(402_004, 404_004))", "set(range(404_204, 406_204))"),
    ("set(range(404_004, 404_204))", "set(range(406_204, 406_404))"),
    ('"a_seed_base": 402_004,', '"a_seed_base": 404_204,'),
    ('"b_exit_seed_base": 404_004,', '"b_exit_seed_base": 406_204,'),
    # -- wave-word cascade (W178 first, then downward) --
    ("W177", "W178"),
    ("W176", "W177"),
    ("W175", "W176"),
    ("W174", "W175"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SIXTY-SIXTH", "ONE HUNDRED-AND-SIXTY-SEVENTH"),
    ("engine_owner rows 165", "engine_owner rows 166"),
    ("rows 91 + candidate", "rows 92 + candidate"),
    ("ninety-second", "ninety-third"),
    ("THIRTY-SIXTH", "THIRTY-SEVENTH"),
    ("thirty-sixth", "thirty-seventh"),
    ("790,412", "793,105"),
    ("382,920", "385,120"),
    ("range(17, 176)", "range(17, 177)"),
    ("range(16, 176)", "range(16, 177)"),
    ("below 176 composes", "below 177 composes"),
    ("WAVE_CONFIGS if w < 176)", "WAVE_CONFIGS if w < 177)"),
    ("WAVE_CONFIGS[175]", "WAVE_CONFIGS[176]"),
    ('== pf.N1_BANDS[175]["a"][0]', '== pf.N1_BANDS[176]["a"][0]'),
    ('pf.N1_BANDS[175]["b_exit"][0]', 'pf.N1_BANDS[176]["b_exit"][0]'),
    ('pf.N1_BANDS[175].get("engine_owner")', 'pf.N1_BANDS[176].get("engine_owner")'),
    ("w175_a", "w176_a"),
    ("w175_b", "w176_b"),
    ("n3r1_used175", "n3r1_used176"),
    ('176: {"batch"', '177: {"batch"'),
    ("PERPETUAL_N1_W176_PREREG.md", "PERPETUAL_N1_W177_PREREG.md"),
    ("PERPETUAL-N1-W176", "PERPETUAL-N1-W177"),
    ('"n1_w176"', '"n1_w177"'),
    ('"n1_w176_results.json"', '"n1_w177_results.json"'),
    ("n1w176", "n1w177"),
    ("engine_owner=bm-a, wave 175: ", "engine_owner=bm-a, wave 176: "),
    ("wave 175 = first free number after", "wave 176 = first free number after"),
    ("_set_wave(176)", "_set_wave(177)"),
]


def s76(t):
    for old, new in S76:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W177 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r843bma_w177_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r843bma_w177_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r843bma_w177_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r843bma_w177_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD_R834 = '"registered W174 row parity drift (r307; bm-a r826)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if face == "MAT" and old == APPEND_OLD_R834:
            # special-case: chain append pair (historical rows carry; the
            # W176 row -- the current registered tail -- gets appended).
            # The old side is the W176 block's chain tail line (one
            # generation back from r834's old side -- constructed
            # explicitly, then count-verified against the dump below).
            n_old = '"registered W175 row parity drift (r307; bm-a r830)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[176] == {"a": (402_004, 404_003),' + NL +
                     '                                    "b_exit": (404_004, 404_203),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W176 row parity drift (r307; bm-a r834)"')
            if dump.count(n_old) != 1:
                fails.append("MAT append-pair old-side count %d != 1: %r" %
                             (dump.count(n_old), n_old))
            out.append((n_old, n_new, 1))
            continue
        n_old, n_new = new, s76(new)
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

# ---------- 4. NEG lists (W176-era stale-token tripwires) -----------------
NEG = {
    "PF_NEG": ["16a8ea982", "r828 probe", "r831 sec8", "r832 pre-seat",
               "_r832bma", "MSG-2026-10-07-1630", "r833 same-window",
               "401_804..403_803", "402_004..402_203", "402_004..404_003",
               "401_804..402_003", "402_003+1", "W175", "W176 (bm-a",
               "INSIDE the W176", "THIRTY-SIXTH", "W176+ projection (",
               "R250: W176", "W176 bands were", "790,412", "382,920",
               "the W176 seat MSG sits in", "since r831,", "r834 freeze"],
    "EN_NEG": ["16a8ea982", "f3fca4055", "790,412", "382,920",
               "SIXTY-SIXTH", "rows 165", "r828 probe", "_r832bma",
               "r832 pre-seat", "r831 sec8", "MSG-2026-10-07-1630",
               "n1_w176", "n1w176", "PERPETUAL-N1-W176", "PERPETUAL_N1_W176",
               "W175 finalize", "thirty-sixth", "THIRTY-SIXTH",
               "bm-a r830 freeze", "wave 175: ", "W176 A band",
               "INSIDE the W176", "W175+ projection", "401_804",
               "404_004, first-clean", "W1..W175", "W175 B band", "R250"],
    "MAT_NEG": ["w175_", "arith_a175", "arith_b175", "n3r1_used175",
                "r828 probe", "r831 sec8", "r832 pre-seat", "16a8ea982",
                "f3fca4055", "SIXTY-SIXTH", "ninety-second", "rows 165",
                "rows 91 ", "range(17, 176)", "range(16, 176)", "W1..W175",
                "wave 175 =", "PERPETUAL_N1_W176", "PERPETUAL-N1-W176",
                "MSG-1630", "_r832bma", "the W175 seat MSG sits in",
                "r833 same-window", "W176 materializer", "INSIDE the W176",
                "THIRTY-SIXTH", "W176 bands", "W176 A band", "W176 A window",
                "W176 B window", "W176 A/B", "W176 hits",
                "W176 entry identity", "W176 path drift", "W176 shard dir",
                "W176 finalize cumulative", "W176 prior-wave",
                "W176 per-wave", "W176 engine_owner drift",
                "W176 A band drift", "W176 B band drift", "the W175 seat",
                "W175 B band", "W175 finalize", "bm-a r830 freeze",
                "post-W175", "seat MSG-1630", "n1w176", "n1_w176",
                "790,412", "382,920"],
    "CL_NEG": ["W176 materializer", "790,412", "382,920", "SIXTY-SIXTH",
               "ninety-second", "rows 165", "rows 91 ", "THIRTY-SIXTH",
               "W175 B band", "_r832bma", "W176 row,", "r834 bm-a] "],
}

# NEG sanity (buildgen-side): every NEG token must be present in the
# W176-era dump (meaningful tripwire) -- informational only, zero-fail
for face, key in (("PF", "PF_NEG"), ("EN", "EN_NEG"), ("MAT", "MAT_NEG"),
                  ("CL", "CL_NEG")):
    dead = [t for t in NEG[key] if t not in DUMPS[face]]
    if dead:
        print("NEG warn (%s): tokens absent from W176 dump (kept, "
              "defense-in-depth harmless): %r" % (face, dead))


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


# ---------- 5. emit the W177 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r843 bm-a W177 freeze edits: four insertions (pf N1_BANDS[177] row +
n1 WAVE_CONFIGS[177] entry + n1 W177 materializer block + n1 W177
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834 dry-run
precedent: full stale+prose+AST asserts in memory BEFORE any write).

Bloodline: r819/r822/r826/r830/r834 freeze-edits machinery (r773 pit
law freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W177 facts live-registry-driven (built by
_r843bma_w177_freeze_buildgen.py: old sides = the PHYSICAL W176 face
fragments probed to dumps this window, new sides = the S76 W177 fact
map, counts verified pre-emission):
  - pre-seat probe results/_r841bma_w177_probe_receipt.json rc0 ADMIT
    (A 404_204..406_203 staircase THIRTY-SEVENTH instance E36 hops=1
    past the registered W176 B band 404_004..404_203; naive
    404_004..406_003 refused at its own start by the W176 B band --
    receipt A_semantics machine-cites the W176 seat MSG leg4 + r832
    probe leg4 anticipated + MANDATED this re-derive (W176 sec5.5
    prose anticipated 37th -- projection and receipt ordinals MATCH,
    no divergence this wave); B 406_204..406_403 own-A mutual
    exclusion hops=1, naive 404_204..404_403);
  - face probe results/_r843bma_w177_face_probe_receipt.json rc0 (all
    four W176 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-07-2031-bma-w177-seat published on origin at
    780a0cd30 (r841 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- r841 same-window
    self-ack move (the W177 seat MSG sits in fleet/inbox/processed/ at
    freeze time, honest archived);
  - per-wave prereg research/PERPETUAL_N1_W177_PREREG.md frozen at
    origin 821a03feb (r842 build, banned gate ADMIT 0 re-verified at
    freeze this window);
  - W176 freeze registered sha machine-derived = 15ec44ea6 (git log
    origin/main --grep "W176 FREEZE"); W176 finalize one-pass landed
    r839: ledger head 793,105, merged pool K=385,120
    (n1_w176_results.json machine-read);
  - lineage constants disclosed (r795 precedent, passed through):
    (a) the "wave N-1 = first free number" mat-header label rides the
    vmap verbatim (off-by-one lineage quirk since W165 r795);
    (b) "law sec.4 W177 row, r795" band-facts template stamp keeps
    its r795;
    (c) "single-window derive (r812 merged the gate legs INTO the
    pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls ninety-second ->
    ninety-third (rows 92 + candidate = 93rd owned per probe leg0);
    (e) mat parity-chain rows W138..W175 keep their historical stamps
    and tuples; the W176 row (the current registered tail) is
    APPENDED with its frozen values (402_004, 404_003)/(404_004,
    404_203);
    (f) the entry "W176 finalize landed same-window r827" citation
    rides the vmap verbatim (off-by-one wave-word + stale-session
    lineage quirk inherited from the r830/r834 generations; head/K
    values roll machine-correct to 793,105/385,120 this window --
    prose session stamp stays r827 per frozen-lineage discipline).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r843bma_w177_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W177 registration before
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
probe = json.load(open(r"results\\_r841bma_w177_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "404204_406203", "B": "406204_406403"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [404204, 406203], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [406204, 406403], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 174 and probe["legs"]["leg0"]["tail"] == "W176",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 167 and probe["legs"]["leg0"]["bma_ordinal"] == 93,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W178p_A"] == "406204..408203"
      and probe["legs"]["leg4"]["W178p_B"] == "406404..406603",
      "leg4 W178+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('177: {"a": (404_204' not in pf_o, "origin pf already carries W177 row")
check("W177 (bm-a r843 freeze" not in pf_o, "origin pf carries W177 block")
check('177: {"batch"' not in n1_o, "origin n1 already carries W177 entry")
check("# --- W177 materializer face" not in n1_o, "origin n1 carries W177 mat")
check('"r843 bm-a] "' not in n1_o, "origin n1 carries W177 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-07-2031-bma-w177-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "780a0cd30", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-07-2031-bma-w177-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w176_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W176 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w176_freeze_sha == "15ec44ea6", "W176 freeze sha mismatch: " + w176_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 174, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[176] == {"a": (402_004, 404_003),
                              "b_exit": (404_004, 404_203),
                              "engine_owner": "bm-a"}, "live W176 row drift")
check(177 not in pfmod.N1_BANDS, "live N1_BANDS already has 177")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W177_PREREG.md")),
      "W177 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W177_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W177 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r843bma_w177_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r843bma_w177_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r843bma_w177_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r843bma_w177_probe_n1_claim.txt", encoding="utf-8",
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
blk177 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry177 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat177 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim177 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W177 block after the W176 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk177 + NL + "}", 1)

# n1 entry: after the W176 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry177 + NL + IND23 + "}", 1)

# n1 mat: insert the W177 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat177 + NL + seg, 1)

# n1 claim: insert the W177 attribution after the W176 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r834 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r834 bm-a] "' + NL + claim177 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W177 presence + W176 anti-vanish (r560 law)
checks = [
    (pfnew, '177: {"a": (404_204, 406_203), "b_exit": (406_204, 406_403),', 1),
    (pfnew, '176: {"a": (402_004, 404_003), "b_exit": (404_004, 404_203),', 1),
    (pfnew, "# W177 (bm-a r843 freeze", 1),
    (pfnew, "# W176 (bm-a r834 freeze", 1),
    (n1new, '177: {"batch": "PERPETUAL-N1-W177",', 1),
    (n1new, '176: {"batch": "PERPETUAL-N1-W176",', 1),
    (n1new, "# --- W177 materializer face", 1),
    (n1new, "# --- W176 materializer face", 1),
    (n1new, '"r843 bm-a] "', 1),
    (n1new, '"r834 bm-a] "', 1),
    (n1new, '"a_seed_base": 404_204,', 1),
    (n1new, '"b_exit_seed_base": 406_204,', 1),
    (n1new, "n1_w177", 4),
    (n1new, "PERPETUAL_N1_W177_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W178 projection prose present in the new W177 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law)
check("# W177+ projection (gate-derived r841)" in pfnew,
      "pf W177+ projection head missing")
check('probe_receipt.json; W178+ projection "' in n1new,
      "n1 W178+ projection head fragment missing")
check("# 406_204..408_203 CLEAN hops=0 / B first-clean 406_404..406_603" in pfnew,
      "pf W178p prose missing")
check("W178 A window; W178 freezer MUST re-derive on the post-W177" in pfnew,
      "pf W178 freezer prose missing")
check('"W178 A window; W178 freezer MUST re-derive on the "' in n1new,
      "n1 W178 freezer fragment missing")
check('"W177 B band 406_204..406_403 will refuse the naive "' in n1new,
      "n1 W177-band refuse fragment missing")

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
check('177: {"a": (404_204' not in pf_o2, "write-time: origin pf carries W177")
check('177: {"batch"' not in n1_o2, "write-time: origin n1 carries W177")
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
io.open(r"results\_r843bma_w177_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r843bma_w177_freeze_edits.py", len(out), "bytes")
