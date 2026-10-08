# -*- coding: utf-8 -*-
"""r882 bm-a generator: builds results/_r882bma_w186_freeze_edits.py by
AST-extracting the r878 W185 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W186 pairs as (new878, S85(new878), cnt) -- old side =
the physical W185 face fragment (probed to dumps this window by
_r881bma_w186_face_probe.py, dead r881 session tail adopted this
window), new side = the S85 W186 fact map applied to that W185
fragment.  Special-case: the mat parity-chain append pair is
constructed explicitly (historical rows carry, the W185 row appended).
Every derived pair old-side is verified against the physical dumps
BEFORE emission (count == cnt); S85 negatives verified after.

S85 = the W185->W186 ordered fact map.  S85 ORDER LAW (r735 substring-
order law + r877 needle dual-face law): projections consumed BEFORE the
band rolls that re-create their strings (proj-A before naive-A roll,
proj-B before naive-B roll); the self-band rolls BEFORE the prior-wave
reference rolls that re-create them; the tail+1 pair order kept
(own-A-tail then prior-B-tail); composite assert pairs BEFORE the bare
== rolls they contain; wave-word cascade (W186 first, then downward)
BEFORE the wave-quirk literal pairs (wave N-1 label / _set_wave) so
their products are terminal.

S85 LINEAGE CONSTANTS (r795/r845/r849/r852/r863/r867/r869/r874/r878
precedent, passed through):
  (a) the "wave N-1 = first free number" mat-header label rolls forward
  with its off-by-one quirk (since W165 r795);
  (b) "law sec.4 W186 row, r795" band-facts template stamp keeps its
  r795 (rolls to W186 row, keeps r795);
  (c) "single-window derive (r812 merged the gate legs INTO the
  pre-seat probe...)" stays (historical merge citation);
  (d) the bm-a-owned ordinal word rolls one-hundred-first ->
  one-hundred-second (rows 101 + candidate = 102nd owned per probe
  leg0);
  (e) mat parity-chain rows W138..W184 keep their historical stamps
  and tuples; the W185 row (the current registered tail) is APPENDED
  with its frozen values (421_804, 423_803)/(423_804, 424_003);
  (f) the "W185 finalize landed same-window r827" citation rolls its
  wave-word with the stale r827 session stamp riding (off-by-one
  wave-word + stale-session lineage quirk inherited; head/K values
  roll machine-correct to 814,328/404,920 this window);
  (g) the self-ack archive move citation rolls to the bm-a r880
  window (self window consume 4c0cfabc3 at 14:1x -- machine-read git
  history this window; the W186 seat MSG sits in
  fleet/inbox/processed/ at freeze time, live-verified).

r587 machine-derived facts (every displayed value read from on-disk
receipts / git history this window):
  - pre-seat probe results/_r880bma_w186_probe_receipt.json rc0 ADMIT
    (leg0 registry 183 rows tail W185 ordinal 176 / bma_ordinal 102;
    leg1 naive A 423_804..425_803 REFUSED at its own start by the
    registered W185 B band 423_804..424_003; honest forward walk
    1 hop lands A 424_004..426_003 staircase FORTY-SIXTH instance
    E36 -- receipt A_semantics machine-cites 'r875 W185 probe leg4 +
    W185 seat MSG leg4 + W185 prereg succession notes anticipated and
    MANDATED this re-derive' (projection and receipt ordinals MATCH);
    B 426_004..426_203 own-A mutual exclusion hops=1, naive
    424_004..424_203; leg2 conflicts 0; leg3 origin vacancy True;
    leg4 W187+ projection A 426_004..428_003 / B 426_204..426_403,
    B inside A);
  - face probe results/_r881bma_w186_probe_stage1.json rc0 (all four
    W185 faces dumped; this TOK is built from the PHYSICAL probe-dumped
    shapes, r776 law; dead r881 session tail adopted r882 zero-loss);
  - seat MSG-2026-10-08-1354-bma-w186-seat published on origin at
    dd362c690 (r880 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- bm-a r880-window
    self-ack move (4c0cfabc3, same-machine consume, live-verified);
  - registered W185 freeze sha machine-derived = beb4b5abd (git log
    origin/main --grep "W185 FREEZE"); W185 finalize landed r879
    one-pass SAME-window: ledger head 814,328, merged pool K=404,920
    (n1_w185_results.json machine-read); W185 sec7/sec8 backfill
    landed the r879 SAME window (r864 lesson);
  - per-wave prereg research/PERPETUAL_N1_W186_PREREG.md built r881
    (buildgen r877-bloodline; banned gate ADMIT 0 verified at
    prereg build; frozen+pushed 2ca2f640b r881; on origin, verified
    live below).

DRY discipline (r833 law 2): zero writes until every gate green -- the
emitted freeze-edits script is the ONLY writer, and it re-asserts
everything live (--dry first)."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r878 pairs --------------------------------
src = io.open(r"results\_r878bma_w185_freeze_edits.py", encoding="utf-8").read()
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

# ---------- 2. S85 = W185->W186 ordered fact map ---------------------------
S85 = [
    # -- session / finalize / sha composites (longest first) --
    ("W184 finalize one-pass bm-a r875, net chain head 812,128, ",
     "W185 finalize one-pass bm-a r879, net chain head 814,328, "),
    ("finalize one-pass bm-a r875", "finalize one-pass bm-a r879"),
    ("bm-a r875 one-pass", "bm-a r879 one-pass"),
    ("on origin since r875, not re-shipped", "on origin since r879, not re-shipped"),
    ("already on origin since r875,", "already on origin since r879,"),
    ("(gate-derived r875)", "(gate-derived r880)"),
    ("r870 probe leg4", "r875 probe leg4"),
    ("projection + r870 probe", "projection + r875 probe"),
    ("r875 sec8 same-window succession", "r879 sec8 same-window succession"),
    ("probe leg4 + r875 sec8", "probe leg4 + r879 sec8"),
    ("at fetch (r875 pre-seat", "at fetch (r880 pre-seat"),
    ("r565 law (r875 pre-seat", "r565 law (r880 pre-seat"),
    ("bm-a r876-window self-ack move", "bm-a r880-window self-ack move"),
    ("bm-a r874 freeze ", "bm-a r878 freeze "),
    ("(r307; bm-a r874)", "(r307; bm-a r878)"),
    ("bm-a r878 freeze,", "bm-a r882 freeze,"),
    ("r878 bm-a freeze", "r882 bm-a freeze"),
    ("r878 bm-a] ", "r882 bm-a] "),
    ("r875 receipt machine-read", "r880 receipt machine-read"),
    ("MSG-2026-10-08-1032-bma-w185-seat", "MSG-2026-10-08-1354-bma-w186-seat"),
    ("seat MSG-1032 tail,", "seat MSG-1354 tail,"),
    ("_r875bma_w185_probe_receipt.json", "_r880bma_w186_probe_receipt.json"),
    ("7e791a87f", "beb4b5abd"),
    ("304909e0e", "dd362c690"),
    # -- band geometry (projections FIRST, then the new-band rolls, then
    #    the prior-wave reference rolls that re-create the consumed
    #    strings -- order law: proj consumed before the rolls re-create
    #    them; W185-B -> W186-B BEFORE the W184-B-ref -> W185-B-ref;
    #    naive rolls AFTER both -- every product lands in a slot the
    #    earlier pairs have already vacated) --
    ("423_804..425_803", "426_004..428_003"),
    ("424_004..424_203", "426_204..426_403"),
    ("423_804..424_003", "426_004..426_203"),
    ("421_804..423_803", "424_004..426_003"),
    ("421_604..423_603", "423_804..425_803"),
    ("421_804..422_003", "424_004..424_203"),
    ("421_604..421_803", "423_804..424_003"),
    ("419_604..421_603", "421_804..423_803"),
    ("419_404..421_403", "421_604..423_603"),
    ("419_404..419_603", "421_604..421_803"),
    ("419_604..419_803", "421_804..422_003"),
    # tail+1 pairs (own-A-tail first then prior-B-tail, S76/S77/S79/
    # S80F/S81f/S82f/S83/S84/S85 order kept; tail roll = staircase
    # geometry: prior B tail 424_003 / own-A tail 426_003 --
    # machine-checked at runtime by the asserts)
    ("423_803+1", "426_003+1"),
    ("421_803+1", "424_003+1"),
    ('assert WAVE_CONFIGS[185]["a_seed_base"] == 421_804 == 421_803 + 1, (',
     'assert WAVE_CONFIGS[186]["a_seed_base"] == 424_004 == 424_003 + 1, ('),
    ('assert WAVE_CONFIGS[185]["b_exit_seed_base"] == 423_804 == 423_803 + 1, (',
     'assert WAVE_CONFIGS[186]["b_exit_seed_base"] == 426_004 == 426_003 + 1, ('),
    ("== 421_804 == 421_803 + 1", "== 424_004 == 424_003 + 1"),
    ("== 423_804 == 423_803 + 1", "== 426_004 == 426_003 + 1"),
    ("arith_a184", "arith_a185"),
    ("arith_b184", "arith_b185"),
    ("set(range(421_804, 423_804))", "set(range(424_004, 426_004))"),
    ("set(range(423_804, 424_004))", "set(range(426_004, 426_204))"),
    ('"a_seed_base": 421_804,', '"a_seed_base": 424_004,'),
    ('"b_exit_seed_base": 423_804,', '"b_exit_seed_base": 426_004,'),
    ('185: {"a": (421_804, 423_803), "b_exit": (423_804, 424_003),',
     '186: {"a": (424_004, 426_003), "b_exit": (426_004, 426_203),'),
    # jump phrases (physical fragment shapes, r869 bloodline; all three
    # rolled one generation)
    ("jumps to 423_804, first-clean ", "jumps to 426_004, first-clean "),
    ("jumps to 423_804 -> ", "jumps to 426_004 -> "),
    ("423_804 and lands ", "426_004 and lands "),
    # -- wave-word cascade (W186 first, then downward) --
    ("W186", "W187"),
    ("W185", "W186"),
    ("W184", "W185"),
    ("W183", "W184"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SEVENTY-FIFTH", "ONE HUNDRED-AND-SEVENTY-SIXTH"),
    ("engine_owner rows 174", "engine_owner rows 175"),
    ("rows 100 + candidate", "rows 101 + candidate"),
    ("one-hundred-first", "one-hundred-second"),
    ("FORTY-FIFTH", "FORTY-SIXTH"),
    ("forty-fifth", "forty-sixth"),
    ("812,128", "814,328"),
    ("402,720", "404,920"),
    ("range(17, 185)", "range(17, 186)"),
    ("range(16, 185)", "range(16, 186)"),
    ("below 185 composes", "below 186 composes"),
    ("WAVE_CONFIGS if w < 185)", "WAVE_CONFIGS if w < 186)"),
    ("WAVE_CONFIGS[184]", "WAVE_CONFIGS[185]"),
    ('== pf.N1_BANDS[184]["a"][0]', '== pf.N1_BANDS[185]["a"][0]'),
    ('pf.N1_BANDS[184]["b_exit"][0]', 'pf.N1_BANDS[185]["b_exit"][0]'),
    ('pf.N1_BANDS[184].get("engine_owner")', 'pf.N1_BANDS[185].get("engine_owner")'),
    ("w184_a", "w185_a"),
    ("w184_b", "w185_b"),
    ("n3r1_used184", "n3r1_used185"),
    ('185: {"batch"', '186: {"batch"'),
    ("PERPETUAL_N1_W185_PREREG.md", "PERPETUAL_N1_W186_PREREG.md"),
    ("PERPETUAL-N1-W185", "PERPETUAL-N1-W186"),
    ('"n1_w185"', '"n1_w186"'),
    ('"n1_w185_results.json"', '"n1_w186_results.json"'),
    ("n1w185", "n1w186"),
    ("engine_owner=bm-a, wave 184: ", "engine_owner=bm-a, wave 185: "),
    ("wave 184 = first free number after", "wave 185 = first free number after"),
    ("_set_wave(185)", "_set_wave(186)"),
]


def s85(t):
    for old, new in S85:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W186 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r881bma_w186_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r881bma_w186_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r881bma_w186_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r881bma_w186_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD_R878 = '"registered W183 row parity drift (r307; bm-a r869)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if face == "MAT" and old == APPEND_OLD_R878:
            # special-case: chain append pair (historical rows carry; the
            # W185 row -- the current registered tail -- gets appended).
            n_old = '"registered W184 row parity drift (r307; bm-a r874)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[185] == {"a": (421_804, 423_803),' + NL +
                     '                                    "b_exit": (423_804, 424_003),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W185 row parity drift (r307; bm-a r878)"')
            if dump.count(n_old) != 1:
                fails.append("MAT append-pair old-side count %d != 1: %r" %
                             (dump.count(n_old), n_old))
            out.append((n_old, n_new, 1))
            continue
        n_old, n_new = new, s85(new)
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

# spot-check the S85 rolls before emission (fail loud, zero emission)
blk_probe = s85(DUMPS["PF"])
assert '186: {"a": (424_004, 426_003), "b_exit": (426_004, 426_203),' in blk_probe
assert "# W186 (bm-a r882 freeze" in blk_probe
assert "FORTY-SIXTH instance" in blk_probe
assert "# 426_004..428_003 CLEAN hops=0 / B first-clean 426_204..426_403" in blk_probe
assert "W187 A window; W187 freezer MUST re-derive on the post-W186" in blk_probe
entry_probe = s85(DUMPS["EN"])
assert '"a_seed_base": 424_004,' in entry_probe and '"b_exit_seed_base": 426_004,' in entry_probe
assert '"batch": "PERPETUAL-N1-W186",' in entry_probe
print("S85 spot-checks: PASS (pf block + entry seed rolls)")

# ---------- 4. NEG lists (mechanical: every consumed old side is a
# tripwire; append-pair old side excluded -- it legitimately remains
# as the prefix of the chain append) --------------------------------------
NEG = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    toks = []
    for n_old, n_new, _cnt in derived[key]:
        if face == "MAT" and n_old.startswith('"registered W184 row parity drift'):
            continue
        # skip no-op pairs (s85 found no roll -- wave-neutral prose that
        # legitimately remains) and partial-persistence shapes
        if n_new == n_old or n_old in n_new:
            continue
        if n_old not in toks:
            toks.append(n_old)
    # defense-in-depth extras (hand additions from the r878 NEG lists,
    # rolled one generation; harmless if absent)
    extra = {
        "PF": ["304909e0e", "r870 probe", "r875 sec8", "r875 pre-seat",
               "_r875bma", "MSG-2026-10-08-1032", "7e791a87f",
               "812,128", "402,720", "FORTY-FIFTH", "ONE HUNDRED-AND-SEVENTY-FIFTH"],
        "EN": ["7e791a87f", "304909e0e", "812,128", "402,720",
               "ONE HUNDRED-AND-SEVENTY-FIFTH", "rows 174", "r870 probe",
               "_r875bma", "MSG-2026-10-08-1032", "n1w185", "n1_w185",
               "PERPETUAL-N1-W185", "PERPETUAL_N1_W185", "FORTY-FIFTH",
               "bm-a r874 freeze", "423_804, first-clean"],
        "MAT": ["w184_", "arith_a184", "arith_b184", "n3r1_used184",
                "r870 probe", "r875 pre-seat", "7e791a87f",
                "ONE HUNDRED-AND-SEVENTY-FIFTH", "one-hundred-first", "rows 174",
                "rows 100 ", "range(17, 185)", "range(16, 185)",
                "PERPETUAL_N1_W185", "PERPETUAL-N1-W185", "MSG-1032",
                "_r875bma", "bm-a r876-window", "n1w185", "n1_w185",
                "812,128", "402,720"],
        "CL": ["812,128", "402,720", "ONE HUNDRED-AND-SEVENTY-FIFTH",
               "one-hundred-first", "rows 174", "rows 100 ", "FORTY-FIFTH",
               "_r875bma", "r878 bm-a] "],
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


# ---------- 5. emit the W186 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r882 bm-a W186 freeze edits: four insertions (pf N1_BANDS[186] row +
n1 WAVE_CONFIGS[186] entry + n1 W186 materializer block + n1 W186
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845/r849/
r852/r863/r867/r869/r874/r878 dry-run precedent: full stale+prose+AST
asserts in memory BEFORE any write).

Bloodline: r819/r822/r826/r830/r834/r843/r845/r849/r852/r863/r867/r869/
r874/r878 freeze-edits machinery (r773 pit law freeze-editor compliance +
r776 fragment-needle law + r781 verify-separation law), W186 facts
live-registry-driven (built by _r882bma_w186_freeze_buildgen.py: old
sides = the PHYSICAL W185 face fragments probed to dumps this window,
new sides = the S85 W186 fact map, counts verified pre-emission):
  - pre-seat probe results/_r880bma_w186_probe_receipt.json rc0 ADMIT
    (naive A 423_804..425_803 refused at its own start by the
    registered W185 B band 423_804..424_003; honest forward walk
    1 hop lands A 424_004..426_003 staircase FORTY-SIXTH instance
    E36 -- receipt A_semantics machine-cites r875 W185 probe leg4 +
    W185 seat MSG leg4 + W185 prereg succession notes anticipated +
    MANDATED this re-derive (projection and receipt ordinals MATCH,
    no divergence this wave); B 426_004..426_203 own-A mutual
    exclusion hops=1, naive 424_004..424_203);
  - face probe results/_r881bma_w186_probe_stage1.json rc0 (all four
    W185 faces dumped; this TOK is built from the PHYSICAL probe-dumped
    shapes, r776 law; dead r881 session tail adopted r882 zero-loss);
  - seat MSG-2026-10-08-1354-bma-w186-seat published on origin at
    dd362c690 (r880 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- bm-a r880-window
    self-ack move (4c0cfabc3, same-machine consume; the W186 seat
    MSG sits in fleet/inbox/processed/ at freeze time, live-verified);
  - per-wave prereg research/PERPETUAL_N1_W186_PREREG.md built r881
    (buildgen r877-bloodline; banned gate ADMIT 0 verified at
    prereg build; frozen+pushed 2ca2f640b r881; on origin, verified
    live below);
  - W185 freeze registered sha machine-derived = beb4b5abd (git log
    origin/main --grep "W185 FREEZE"); W185 finalize landed r879
    one-pass same-window: ledger head 814,328, merged pool K=404,920
    (n1_w185_results.json machine-read); W185 sec7/sec8 settle
    backfill landed the r879 SAME window (r864 lesson);
  - lineage constants disclosed (r795/r845/r849/r852/r863/r867/r869/
    r874/r878 precedent, passed through): (a) the "wave N-1 = first
    free number" mat-header label rolls forward with its off-by-one
    quirk (since W165 r795); (b) "law sec.4 W186 row, r795" band-facts
    template stamp keeps its r795; (c) "single-window derive (r812
    merged the gate legs INTO the pre-seat probe...)" stays (historical
    merge citation); (d) the bm-a-owned ordinal word rolls
    one-hundred-first -> one-hundred-second (rows 101 + candidate =
    102nd owned per probe leg0, machine-chosen word form, disclosed);
    (e) mat parity-chain rows W138..W184 keep their historical stamps
    and tuples; the W185 row (the current registered tail) is APPENDED
    with its frozen values (421_804, 423_803)/(423_804, 424_003);
    (f) the "W185 finalize landed same-window r827" citation rolls
    its wave-word with the stale r827 session stamp riding (off-by-one
    wave-word + stale-session lineage quirk inherited; head/K values
    roll machine-correct to 814,328/404,920 this window).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r881bma_w186_face_probe.py -- four face dumps + stage-1
      receipt, rc0; dead r881 tail adopted r882);
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
      (r530/r687: fetch + origin carries no W186 registration before
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
probe = json.load(open(r"results\\_r880bma_w186_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "424004_426003", "B": "426004_426203"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [424004, 426003], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [426004, 426203], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 183 and probe["legs"]["leg0"]["tail"] == "W185",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 176 and probe["legs"]["leg0"]["bma_ordinal"] == 102,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W187p_A"] == "426004..428003"
      and probe["legs"]["leg4"]["W187p_B"] == "426204..426403",
      "leg4 W187+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('186: {"a": (424_004' not in pf_o, "origin pf already carries W186 row")
check("W186 (bm-a r882 freeze" not in pf_o, "origin pf carries W186 block")
check('186: {"batch"' not in n1_o, "origin n1 already carries W186 entry")
check("# --- W186 materializer face" not in n1_o, "origin n1 carries W186 mat")
check('"r882 bm-a] "' not in n1_o, "origin n1 carries W186 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-1354-bma-w186-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "dd362c690", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-1354-bma-w186-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w185_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W185 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w185_freeze_sha == "beb4b5abd", "W185 freeze sha mismatch: " + w185_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 183, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[185] == {"a": (421_804, 423_803),
                              "b_exit": (423_804, 424_003),
                              "engine_owner": "bm-a"}, "live W185 row drift")
check(186 not in pfmod.N1_BANDS, "live N1_BANDS already has 186")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W186_PREREG.md")),
      "W186 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W186_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W186 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r881bma_w186_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r881bma_w186_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r881bma_w186_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r881bma_w186_probe_n1_claim.txt", encoding="utf-8",
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
blk186 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry186 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat186 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim186 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W186 block after the W185 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk186 + NL + "}", 1)

# n1 entry: after the W185 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry186 + NL + IND23 + "}", 1)

# n1 mat: insert the W186 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat186 + NL + seg, 1)

# n1 claim: insert the W186 attribution after the W185 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r878 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r878 bm-a] "' + NL + claim186 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W186 presence + W185 anti-vanish (r560 law)
checks = [
    (pfnew, '186: {"a": (424_004, 426_003), "b_exit": (426_004, 426_203),', 1),
    (pfnew, '185: {"a": (421_804, 423_803), "b_exit": (423_804, 424_003),', 1),
    (pfnew, "# W186 (bm-a r882 freeze", 1),
    (pfnew, "# W185 (bm-a r878 freeze", 1),
    (n1new, '186: {"batch": "PERPETUAL-N1-W186",', 1),
    (n1new, '185: {"batch": "PERPETUAL-N1-W185",', 1),
    (n1new, "# --- W186 materializer face", 1),
    (n1new, "# --- W185 materializer face", 1),
    (n1new, '"r882 bm-a] "', 1),
    (n1new, '"r878 bm-a] "', 1),
    (n1new, '"a_seed_base": 424_004,', 1),
    (n1new, '"b_exit_seed_base": 426_004,', 1),
    (n1new, "n1_w186", 4),
    (n1new, "PERPETUAL_N1_W186_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W187+ projection prose present in the new W186 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W186+ per r845 precedent, n1 fragment =
# next-wave W187+)
check("# W186+ projection (gate-derived r880)" in pfnew,
      "pf W186+ projection head missing")
check('probe_receipt.json; W187+ projection "' in n1new,
      "n1 W187+ projection head fragment missing")
check("# 426_004..428_003 CLEAN hops=0 / B first-clean 426_204..426_403" in pfnew,
      "pf W187p prose missing")
check("W187 A window; W187 freezer MUST re-derive on the post-W186" in pfnew,
      "pf W187 freezer prose missing")
check('"W187 A window; W187 freezer MUST re-derive on the "' in n1new,
      "n1 W187 freezer fragment missing")
check('"W186 B band 426_004..426_203 will refuse the naive "' in n1new,
      "n1 W186-band refuse fragment missing")

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
check('186: {"a": (424_004' not in pf_o2, "write-time: origin pf carries W186")
check('186: {"batch"' not in n1_o2, "write-time: origin n1 carries W186")
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
io.open(r"results\_r882bma_w186_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r882bma_w186_freeze_edits.py", len(out), "bytes")
