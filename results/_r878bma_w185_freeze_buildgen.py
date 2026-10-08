# -*- coding: utf-8 -*-
"""r878 bm-a generator: builds results/_r878bma_w185_freeze_edits.py by
AST-extracting the r874 W184 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W185 pairs as (new874, S84(new874), cnt) -- old side =
the physical W184 face fragment (probed to dumps this window by
_r878bma_w185_face_probe.py), new side = the S84 W185 fact map applied
to that W184 fragment.  Special-case: the mat parity-chain append pair
is constructed explicitly (historical rows carry, W184 row appended).
Every derived pair old-side is verified against the physical dumps
BEFORE emission (count == cnt); S84 negatives verified after.

S84 = the W184->W185 ordered fact map.  S84 ORDER LAW (r735 substring-
order law + r877 needle dual-face law): projections consumed BEFORE the
band rolls that re-create their strings (proj-A before W184-B roll,
proj-B before naive-B roll); W184 B/A rolls BEFORE the prior-wave
reference rolls that re-create them (W183-B-ref -> W184-B AFTER
W184-B -> W185-B); the tail+1 pair order kept (own-A-tail then
prior-B-tail); composite assert pairs BEFORE the bare == rolls they
contain; wave-word cascade (W185 first, then downward) BEFORE the
wave-quirk literal pairs (wave N-1 label / _set_wave) so their
products are terminal.

S84 LINEAGE CONSTANTS (r795/r845/r849/r852/r863/r867/r869/r874
precedent, passed through):
  (a) the "wave N-1 = first free number" mat-header label rolls forward
  with its off-by-one quirk (since W165 r795);
  (b) "law sec.4 W185 row, r795" band-facts template stamp keeps its
  r795 (rolls to W185 row, keeps r795);
  (c) "single-window derive (r812 merged the gate legs INTO the
  pre-seat probe...)" stays (historical merge citation);
  (d) the bm-a-owned ordinal word rolls one-hundredth -> one-hundred-
  first (rows 100 + candidate = 101st owned per probe leg0);
  (e) mat parity-chain rows W138..W183 keep their historical stamps
  and tuples; the W184 row (the current registered tail) is APPENDED
  with its frozen values (419_604, 421_603)/(421_604, 421_803);
  (f) the "W184 finalize landed same-window r827" citation rolls its
  wave-word with the stale r827 session stamp riding (off-by-one
  wave-word + stale-session lineage quirk inherited; head/K values
  roll machine-correct to 812,128/402,720 this window);
  (g) the self-ack archive move citation rolls to the bm-a r876
  window (self window consume b0ce85956 at 12:5x -- machine-read git
  history this window; the W185 seat MSG sits in
  fleet/inbox/processed/ at freeze time, live-verified).

r587 machine-derived facts (every displayed value read from on-disk
receipts / git history this window):
  - pre-seat probe results/_r875bma_w185_probe_receipt.json rc0 ADMIT
    (leg0 registry 182 rows tail W184 ordinal 175 / bma_ordinal 101;
    leg1 naive A 421_604..423_603 REFUSED at its own start by the
    registered W184 B band 421_604..421_803; honest forward walk
    1 hop lands A 421_804..423_803 staircase FORTY-FIFTH instance
    E36 -- receipt A_semantics machine-cites 'r870 W184 probe leg4 +
    W184 seat MSG leg4 + W184 prereg sec5.5/sec8 anticipated and
    MANDATED this re-derive' (projection and receipt ordinals MATCH);
    B 423_804..424_003 own-A mutual exclusion hops=1, naive
    421_804..422_003; leg2 conflicts 0; leg3 origin vacancy True;
    leg4 W186+ projection A 423_804..425_803 / B 424_004..424_203,
    B inside A);
  - face probe results/_r878bma_w185_probe_stage1.json rc0 (all four
    W184 faces dumped; this TOK is built from the PHYSICAL probe-dumped
    shapes, r776 law);
  - seat MSG-2026-10-08-1032-bma-w185-seat published on origin at
    304909e0e (r875 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- bm-a r876-window
    self-ack move (b0ce85956, same-machine consume, live-verified);
  - registered W184 freeze sha machine-derived = 7e791a87f (git log
    origin/main --grep "W184 FREEZE"); W184 finalize landed r875
    one-pass SAME-window: ledger head 812,128, merged pool K=402,720
    (n1_w184_results.json machine-read); W184 sec7/sec8 backfill
    landed the r875 SAME window (r864 lesson 3rd consecutive);
  - per-wave prereg research/PERPETUAL_N1_W185_PREREG.md built r877
    (buildgen r872-bloodline 3-heal; banned gate ADMIT 0 verified at
    prereg build; frozen+pushed ad4eded99 r877; on origin, verified
    live below).

DRY discipline (r833 law 2): zero writes until every gate green -- the
emitted freeze-edits script is the ONLY writer, and it re-asserts
everything live (--dry first)."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r874 pairs --------------------------------
src = io.open(r"results\_r874bma_w184_freeze_edits.py", encoding="utf-8").read()
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

# ---------- 2. S84 = W184->W185 ordered fact map ---------------------------
S84 = [
    # -- session / finalize / sha composites (longest first) --
    ("W183 finalize one-pass bm-a r870, net chain head 808,918, ",
     "W184 finalize one-pass bm-a r875, net chain head 812,128, "),
    ("finalize one-pass bm-a r870", "finalize one-pass bm-a r875"),
    ("bm-a r870 one-pass", "bm-a r875 one-pass"),
    ("on origin since r870, not re-shipped", "on origin since r875, not re-shipped"),
    ("already on origin since r870,", "already on origin since r875,"),
    ("(gate-derived r870)", "(gate-derived r875)"),
    ("r868 probe leg4", "r870 probe leg4"),
    ("projection + r868 probe", "projection + r870 probe"),
    ("r870 sec8 same-window succession", "r875 sec8 same-window succession"),
    ("probe leg4 + r870 sec8", "probe leg4 + r875 sec8"),
    ("at fetch (r870 pre-seat", "at fetch (r875 pre-seat"),
    ("r565 law (r870 pre-seat", "r565 law (r875 pre-seat"),
    ("bm-c r745-window self-ack move", "bm-a r876-window self-ack move"),
    ("bm-a r869 freeze ", "bm-a r874 freeze "),
    ("(r307; bm-a r869)", "(r307; bm-a r874)"),
    ("bm-a r874 freeze,", "bm-a r878 freeze,"),
    ("r874 bm-a freeze", "r878 bm-a freeze"),
    ("r874 bm-a] ", "r878 bm-a] "),
    ("r870 receipt machine-read", "r875 receipt machine-read"),
    ("MSG-2026-10-08-0826-bma-w184-seat", "MSG-2026-10-08-1032-bma-w185-seat"),
    ("seat MSG-0826 tail,", "seat MSG-1032 tail,"),
    ("_r870bma_w184_probe_receipt.json", "_r875bma_w185_probe_receipt.json"),
    ("481da4d78", "7e791a87f"),
    ("d1f15ebf9", "304909e0e"),
    # -- band geometry (projections FIRST, then the new-band rolls, then
    #    the prior-wave reference rolls that re-create the consumed
    #    strings -- order law: proj consumed before the rolls re-create
    #    them; W184-B -> W185-B BEFORE W183-B-ref -> W184-B-ref;
    #    naive rolls AFTER both -- every product lands in a slot the
    #    earlier pairs have already vacated) --
    ("421_604..423_603", "423_804..425_803"),
    ("421_804..422_003", "424_004..424_203"),
    ("421_604..421_803", "423_804..424_003"),
    ("419_604..421_603", "421_804..423_803"),
    ("419_404..421_403", "421_604..423_603"),
    ("419_604..419_803", "421_804..422_003"),
    ("419_404..419_603", "421_604..421_803"),
    ("417_404..419_403", "419_604..421_603"),
    ("417_204..419_203", "419_404..421_403"),
    ("417_204..417_403", "419_404..419_603"),
    ("417_404..417_603", "419_604..419_803"),
    # tail+1 pairs (own-A-tail first then prior-B-tail, S75/S76/S77/
    # S79/S80F/S81f/S82f/S83/S84 order kept; tail roll = staircase
    # geometry: prior B tail 421_803 / own-A tail 423_803 --
    # machine-checked at runtime by the asserts)
    ("421_603+1", "423_803+1"),
    ("419_603+1", "421_803+1"),
    ('assert WAVE_CONFIGS[184]["a_seed_base"] == 419_604 == 419_603 + 1, (',
     'assert WAVE_CONFIGS[185]["a_seed_base"] == 421_804 == 421_803 + 1, ('),
    ('assert WAVE_CONFIGS[184]["b_exit_seed_base"] == 421_604 == 421_603 + 1, (',
     'assert WAVE_CONFIGS[185]["b_exit_seed_base"] == 423_804 == 423_803 + 1, ('),
    ("== 419_604 == 419_603 + 1", "== 421_804 == 421_803 + 1"),
    ("== 421_604 == 421_603 + 1", "== 423_804 == 423_803 + 1"),
    ("arith_a183", "arith_a184"),
    ("arith_b183", "arith_b184"),
    ("set(range(419_604, 421_604))", "set(range(421_804, 423_804))"),
    ("set(range(421_604, 421_804))", "set(range(423_804, 424_004))"),
    ('"a_seed_base": 419_604,', '"a_seed_base": 421_804,'),
    ('"b_exit_seed_base": 421_604,', '"b_exit_seed_base": 423_804,'),
    ('184: {"a": (419_604, 421_603), "b_exit": (421_604, 421_803),',
     '185: {"a": (421_804, 423_803), "b_exit": (423_804, 424_003),'),
    # jump phrases (physical fragment shapes, r869 bloodline; all three
    # rolled one generation)
    ("jumps to 421_604, first-clean ", "jumps to 423_804, first-clean "),
    ("jumps to 421_604 -> ", "jumps to 423_804 -> "),
    ("421_604 and lands ", "423_804 and lands "),
    # -- wave-word cascade (W185 first, then downward) --
    ("W185", "W186"),
    ("W184", "W185"),
    ("W183", "W184"),
    ("W182", "W183"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SEVENTY-FOURTH", "ONE HUNDRED-AND-SEVENTY-FIFTH"),
    ("engine_owner rows 173", "engine_owner rows 174"),
    ("rows 99 + candidate", "rows 100 + candidate"),
    ("one-hundredth", "one-hundred-first"),
    ("FORTY-FOURTH", "FORTY-FIFTH"),
    ("forty-fourth", "forty-fifth"),
    ("808,918", "812,128"),
    ("400,520", "402,720"),
    ("range(17, 184)", "range(17, 185)"),
    ("range(16, 184)", "range(16, 185)"),
    ("below 184 composes", "below 185 composes"),
    ("WAVE_CONFIGS if w < 184)", "WAVE_CONFIGS if w < 185)"),
    ("WAVE_CONFIGS[183]", "WAVE_CONFIGS[184]"),
    ('== pf.N1_BANDS[183]["a"][0]', '== pf.N1_BANDS[184]["a"][0]'),
    ('pf.N1_BANDS[183]["b_exit"][0]', 'pf.N1_BANDS[184]["b_exit"][0]'),
    ('pf.N1_BANDS[183].get("engine_owner")', 'pf.N1_BANDS[184].get("engine_owner")'),
    ("w183_a", "w184_a"),
    ("w183_b", "w184_b"),
    ("n3r1_used183", "n3r1_used184"),
    ('184: {"batch"', '185: {"batch"'),
    ("PERPETUAL_N1_W184_PREREG.md", "PERPETUAL_N1_W185_PREREG.md"),
    ("PERPETUAL-N1-W184", "PERPETUAL-N1-W185"),
    ('"n1_w184"', '"n1_w185"'),
    ('"n1_w184_results.json"', '"n1_w185_results.json"'),
    ("n1w184", "n1w185"),
    ("engine_owner=bm-a, wave 183: ", "engine_owner=bm-a, wave 184: "),
    ("wave 183 = first free number after", "wave 184 = first free number after"),
    ("_set_wave(184)", "_set_wave(185)"),
]


def s84(t):
    for old, new in S84:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W185 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r878bma_w185_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r878bma_w185_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r878bma_w185_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r878bma_w185_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD_R874 = '"registered W182 row parity drift (r307; bm-a r867)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if face == "MAT" and old == APPEND_OLD_R874:
            # special-case: chain append pair (historical rows carry; the
            # W184 row -- the current registered tail -- gets appended).
            n_old = '"registered W183 row parity drift (r307; bm-a r869)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[184] == {"a": (419_604, 421_603),' + NL +
                     '                                    "b_exit": (421_604, 421_803),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W184 row parity drift (r307; bm-a r874)"')
            if dump.count(n_old) != 1:
                fails.append("MAT append-pair old-side count %d != 1: %r" %
                             (dump.count(n_old), n_old))
            out.append((n_old, n_new, 1))
            continue
        n_old, n_new = new, s84(new)
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

# spot-check the S84 rolls before emission (fail loud, zero emission)
blk_probe = s84(DUMPS["PF"])
assert '185: {"a": (421_804, 423_803), "b_exit": (423_804, 424_003),' in blk_probe
assert "# W185 (bm-a r878 freeze" in blk_probe
assert "FORTY-FIFTH instance" in blk_probe
assert "# 423_804..425_803 CLEAN hops=0 / B first-clean 424_004..424_203" in blk_probe
assert "W186 A window; W186 freezer MUST re-derive on the post-W185" in blk_probe
entry_probe = s84(DUMPS["EN"])
assert '"a_seed_base": 421_804,' in entry_probe and '"b_exit_seed_base": 423_804,' in entry_probe
assert '"batch": "PERPETUAL-N1-W185",' in entry_probe
print("S84 spot-checks: PASS (pf block + entry seed rolls)")

# ---------- 4. NEG lists (mechanical: every consumed old side is a
# tripwire; append-pair old side excluded -- it legitimately remains
# as the prefix of the chain append) --------------------------------------
NEG = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    toks = []
    for n_old, n_new, _cnt in derived[key]:
        if face == "MAT" and n_old.startswith('"registered W183 row parity drift'):
            continue
        # skip no-op pairs (s84 found no roll -- wave-neutral prose that
        # legitimately remains) and partial-persistence shapes
        if n_new == n_old or n_old in n_new:
            continue
        if n_old not in toks:
            toks.append(n_old)
    # defense-in-depth extras (hand additions from the r874 NEG lists,
    # rolled one generation; harmless if absent)
    extra = {
        "PF": ["d1f15ebf9", "r868 probe", "r870 sec8", "r870 pre-seat",
               "_r870bma", "MSG-2026-10-08-0826", "481da4d78",
               "808,918", "400,520", "FORTY-FOURTH", "ONE HUNDRED-AND-SEVENTY-FOURTH"],
        "EN": ["481da4d78", "d1f15ebf9", "808,918", "400,520",
               "ONE HUNDRED-AND-SEVENTY-FOURTH", "rows 173", "r868 probe",
               "_r870bma", "MSG-2026-10-08-0826", "n1w184", "n1_w184",
               "PERPETUAL-N1-W184", "PERPETUAL_N1_W184", "FORTY-FOURTH",
               "bm-a r869 freeze", "421_604, first-clean"],
        "MAT": ["w183_", "arith_a183", "arith_b183", "n3r1_used183",
                "r868 probe", "r870 pre-seat", "481da4d78",
                "ONE HUNDRED-AND-SEVENTY-FOURTH", "one-hundredth", "rows 173",
                "rows 99 ", "range(17, 184)", "range(16, 184)",
                "PERPETUAL_N1_W184", "PERPETUAL-N1-W184", "MSG-0826",
                "_r870bma", "bm-c r745-window", "n1w184", "n1_w184",
                "808,918", "400,520"],
        "CL": ["808,918", "400,520", "ONE HUNDRED-AND-SEVENTY-FOURTH",
               "one-hundredth", "rows 173", "rows 99 ", "FORTY-FOURTH",
               "_r870bma", "r874 bm-a] "],
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


# ---------- 5. emit the W185 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r878 bm-a W185 freeze edits: four insertions (pf N1_BANDS[185] row +
n1 WAVE_CONFIGS[185] entry + n1 W185 materializer block + n1 W185
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845/r849/
r852/r863/r867/r869/r874 dry-run precedent: full stale+prose+AST asserts
in memory BEFORE any write).

Bloodline: r819/r822/r826/r830/r834/r843/r845/r849/r852/r863/r867/r869/
r874 freeze-edits machinery (r773 pit law freeze-editor compliance +
r776 fragment-needle law + r781 verify-separation law), W185 facts
live-registry-driven (built by _r878bma_w185_freeze_buildgen.py: old
sides = the PHYSICAL W184 face fragments probed to dumps this window,
new sides = the S84 W185 fact map, counts verified pre-emission):
  - pre-seat probe results/_r875bma_w185_probe_receipt.json rc0 ADMIT
    (naive A 421_604..423_603 refused at its own start by the
    registered W184 B band 421_604..421_803; honest forward walk
    1 hop lands A 421_804..423_803 staircase FORTY-FIFTH instance
    E36 -- receipt A_semantics machine-cites the W184 seat MSG leg4 +
    r870 W184 probe leg4 + W184 prereg sec5.5/sec8 anticipated +
    MANDATED this re-derive (projection and receipt ordinals MATCH,
    no divergence this wave); B 423_804..424_003 own-A mutual
    exclusion hops=1, naive 421_804..422_003);
  - face probe results/_r878bma_w185_probe_stage1.json rc0 (all four
    W184 faces dumped; this TOK is built from the PHYSICAL probe-dumped
    shapes, r776 law);
  - seat MSG-2026-10-08-1032-bma-w185-seat published on origin at
    304909e0e (r875 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- bm-a r876-window
    self-ack move (b0ce85956, same-machine consume; the W185 seat
    MSG sits in fleet/inbox/processed/ at freeze time, live-verified);
  - per-wave prereg research/PERPETUAL_N1_W185_PREREG.md built r877
    (buildgen r872-bloodline 3-heal; banned gate ADMIT 0 verified at
    prereg build; frozen+pushed ad4eded99 r877; on origin, verified
    live below);
  - W184 freeze registered sha machine-derived = 7e791a87f (git log
    origin/main --grep "W184 FREEZE"); W184 finalize landed r875
    one-pass same-window: ledger head 812,128, merged pool K=402,720
    (n1_w184_results.json machine-read); W184 sec7/sec8 settle
    backfill landed the r875 SAME window (r864 lesson 3rd
    consecutive);
  - lineage constants disclosed (r795/r845/r849/r852/r863/r867/r869/
    r874 precedent, passed through): (a) the "wave N-1 = first free
    number" mat-header label rolls forward with its off-by-one quirk
    (since W165 r795); (b) "law sec.4 W185 row, r795" band-facts
    template stamp keeps its r795; (c) "single-window derive (r812
    merged the gate legs INTO the pre-seat probe...)" stays
    (historical merge citation); (d) the bm-a-owned ordinal word
    rolls one-hundredth -> one-hundred-first (rows 100 + candidate =
    101st owned per probe leg0, machine-chosen word form, disclosed);
    (e) mat parity-chain rows W138..W183 keep their historical stamps
    and tuples; the W184 row (the current registered tail) is APPENDED
    with its frozen values (419_604, 421_603)/(421_604, 421_803);
    (f) the "W184 finalize landed same-window r827" citation rolls
    its wave-word with the stale r827 session stamp riding (off-by-one
    wave-word + stale-session lineage quirk inherited; head/K values
    roll machine-correct to 812,128/402,720 this window).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r878bma_w185_face_probe.py -- four face dumps + stage-1
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
      (r530/r687: fetch + origin carries no W185 registration before
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
probe = json.load(open(r"results\\_r875bma_w185_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "421804_423803", "B": "423804_424003"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [421804, 423803], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [423804, 424003], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 182 and probe["legs"]["leg0"]["tail"] == "W184",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 175 and probe["legs"]["leg0"]["bma_ordinal"] == 101,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W186p_A"] == "423804..425803"
      and probe["legs"]["leg4"]["W186p_B"] == "424004..424203",
      "leg4 W186+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('185: {"a": (421_804' not in pf_o, "origin pf already carries W185 row")
check("W185 (bm-a r878 freeze" not in pf_o, "origin pf carries W185 block")
check('185: {"batch"' not in n1_o, "origin n1 already carries W185 entry")
check("# --- W185 materializer face" not in n1_o, "origin n1 carries W185 mat")
check('"r878 bm-a] "' not in n1_o, "origin n1 carries W185 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-1032-bma-w185-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "304909e0e", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-1032-bma-w185-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w184_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W184 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w184_freeze_sha == "7e791a87f", "W184 freeze sha mismatch: " + w184_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 182, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[184] == {"a": (419_604, 421_603),
                              "b_exit": (421_604, 421_803),
                              "engine_owner": "bm-a"}, "live W184 row drift")
check(185 not in pfmod.N1_BANDS, "live N1_BANDS already has 185")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W185_PREREG.md")),
      "W185 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W185_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W185 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r878bma_w185_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r878bma_w185_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r878bma_w185_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r878bma_w185_probe_n1_claim.txt", encoding="utf-8",
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
blk185 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry185 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat185 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim185 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W185 block after the W184 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk185 + NL + "}", 1)

# n1 entry: after the W184 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry185 + NL + IND23 + "}", 1)

# n1 mat: insert the W185 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat185 + NL + seg, 1)

# n1 claim: insert the W185 attribution after the W184 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r874 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r874 bm-a] "' + NL + claim185 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W185 presence + W184 anti-vanish (r560 law)
checks = [
    (pfnew, '185: {"a": (421_804, 423_803), "b_exit": (423_804, 424_003),', 1),
    (pfnew, '184: {"a": (419_604, 421_603), "b_exit": (421_604, 421_803),', 1),
    (pfnew, "# W185 (bm-a r878 freeze", 1),
    (pfnew, "# W184 (bm-a r874 freeze", 1),
    (n1new, '185: {"batch": "PERPETUAL-N1-W185",', 1),
    (n1new, '184: {"batch": "PERPETUAL-N1-W184",', 1),
    (n1new, "# --- W185 materializer face", 1),
    (n1new, "# --- W184 materializer face", 1),
    (n1new, '"r878 bm-a] "', 1),
    (n1new, '"r874 bm-a] "', 1),
    (n1new, '"a_seed_base": 421_804,', 1),
    (n1new, '"b_exit_seed_base": 423_804,', 1),
    (n1new, "n1_w185", 4),
    (n1new, "PERPETUAL_N1_W185_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W186+ projection prose present in the new W185 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W185+ per r845 precedent, n1 fragment =
# next-wave W186+)
check("# W185+ projection (gate-derived r875)" in pfnew,
      "pf W185+ projection head missing")
check('probe_receipt.json; W186+ projection "' in n1new,
      "n1 W186+ projection head fragment missing")
check("# 423_804..425_803 CLEAN hops=0 / B first-clean 424_004..424_203" in pfnew,
      "pf W186p prose missing")
check("W186 A window; W186 freezer MUST re-derive on the post-W185" in pfnew,
      "pf W186 freezer prose missing")
check('"W186 A window; W186 freezer MUST re-derive on the "' in n1new,
      "n1 W186 freezer fragment missing")
check('"W185 B band 423_804..424_003 will refuse the naive "' in n1new,
      "n1 W185-band refuse fragment missing")

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
check('185: {"a": (421_804' not in pf_o2, "write-time: origin pf carries W185")
check('185: {"batch"' not in n1_o2, "write-time: origin n1 carries W185")
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
io.open(r"results\_r878bma_w185_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r878bma_w185_freeze_edits.py", len(out), "bytes")
