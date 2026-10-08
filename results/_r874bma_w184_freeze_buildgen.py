# -*- coding: utf-8 -*-
"""r874 bm-a generator: builds results/_r874bma_w184_freeze_edits.py by
AST-extracting the r869 W183 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W184 pairs as (new869, S83(new869), cnt) -- old side =
the physical W183 face fragment (probed to dumps this window by
_r874bma_w184_face_probe.py), new side = the S83 W184 fact map applied
to that W183 fragment.  Special-case: the mat parity-chain append pair
is constructed explicitly (historical rows carry, W183 row appended).
Every derived pair old-side is verified against the physical dumps
BEFORE emission (count == cnt); S83 negatives verified after.

S83 ORDER LAW (r735 substring-order law): projections consumed BEFORE
the naive rolls that re-create their strings (proj-A before naive-A,
proj-B before naive-B, prior-B consumed before naive-B re-creates it);
the tail+1 pair order kept from S75/S76/S77/S79/S80F/S81f/S82f/S83
(own-A-tail then prior-B-tail); composite WAVE_CONFIGS assert pairs
BEFORE the bare == rolls they contain.

S83 LINEAGE CONSTANTS (r795/r845/r849/r852/r863/r867/r869 precedent,
passed through):
  (a) the "wave N-1 = first free number" mat-header label rolls forward
  with its off-by-one quirk (since W165 r795);
  (b) "law sec.4 W184 row, r795" band-facts template stamp keeps its
  r795 (rolls to W184 row, keeps r795);
  (c) "single-window derive (r812 merged the gate legs INTO the
  pre-seat probe...)" stays (historical merge citation);
  (d) the bm-a-owned ordinal word rolls ninety-ninth -> one-hundredth
  (rows 99 + candidate = 100th owned per probe leg0 -- first
  triple-digit crossing, word form machine-chosen "one-hundredth",
  disclosed);
  (e) mat parity-chain rows W138..W182 keep their historical stamps
  and tuples; the W183 row (the current registered tail) is APPENDED
  with its frozen values (417_404, 419_403)/(419_404, 419_603);
  (f) the "W183 finalize landed same-window r827" citation rolls its
  wave-word with the stale r827 session stamp riding (off-by-one
  wave-word + stale-session lineage quirk inherited; head/K values
  roll machine-correct to 808,918/400,520 this window);
  (g) the self-ack archive move citation rolls to the bm-c r745
  window (cross-machine consume 1ec9800ae at 08:24:24 -- machine-read
  git history this window; the W184 prereg's "bm-c r741" citation is
  a STALE SESSION NUMBER superseded by machine-read, honest
  disclosure; the W184 seat MSG sits in fleet/inbox/processed/ at
  freeze time, live-verified).

r587 machine-derived facts (every displayed value read from on-disk
receipts / git history this window):
  - pre-seat probe results/_r870bma_w184_probe_receipt.json rc0 ADMIT
    (leg0 registry 181 rows tail W183 ordinal 174 / bma_ordinal 100;
    leg1 naive A 419_404..421_403 REFUSED at its own start by the
    registered W183 B band 419_404..419_603; honest forward walk
    1 hop lands A 419_604..421_603 staircase FORTY-FOURTH instance
    E36 -- receipt A_semantics machine-cites 'r868 W183 probe leg4 +
    W183 seat MSG leg4 + W183 prereg sec5.5/sec8 anticipated and
    MANDATED this re-derive' (projection and receipt ordinals MATCH);
    B 421_604..421_803 own-A mutual exclusion hops=1, naive
    419_604..419_803; leg2 conflicts 0; leg3 origin vacancy True;
    leg4 W185+ projection A 421_604..423_603 / B 421_804..422_003,
    B inside A);
  - face probe results/_r874bma_w184_face_probe_receipt.json rc0 (all
    four W183 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-0826-bma-w184-seat published on origin at
    d1f15ebf9 (r870 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- bm-c r745-window
    self-ack move (cross-machine consume, 1ec9800ae);
  - registered W183 freeze sha machine-derived = 481da4d78 (git log
    origin/main --grep "W183 FREEZE"); W183 finalize landed r870
    one-pass SAME-window: ledger head 808,918, merged pool K=400,520
    (n1_w183_results.json machine-read); W183 sec7/sec8 backfill
    landed the r870 SAME window (r864 lesson 2nd consecutive);
  - per-wave prereg research/PERPETUAL_N1_W184_PREREG.md built +
    frozen+pushed f908433c4 at r872 (banned gate ADMIT 0 verified at
    prereg build; on origin, verified live below).

DRY discipline (r833 law 2): zero writes until every gate green -- the
emitted freeze-edits script is the ONLY writer, and it re-asserts
everything live (--dry first)."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r869 pairs --------------------------------
src = io.open(r"results\_r869bma_w183_freeze_edits.py", encoding="utf-8").read()
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

# ---------- 2. S83 = W183->W184 ordered fact map ---------------------------
S83 = [
    # -- session / finalize / sha composites (longest first) --
    ("W182 finalize one-pass bm-a r868, net chain head 806,718, ",
     "W183 finalize one-pass bm-a r870, net chain head 808,918, "),
    ("finalize one-pass bm-a r868", "finalize one-pass bm-a r870"),
    ("bm-a r868 one-pass", "bm-a r870 one-pass"),
    ("on origin since r868, not re-shipped", "on origin since r870, not re-shipped"),
    ("already on origin since r868,", "already on origin since r870,"),
    ("(gate-derived r868)", "(gate-derived r870)"),
    ("r865 probe leg4", "r868 probe leg4"),
    ("projection + r865 probe", "projection + r868 probe"),
    ("r868 sec8 same-window succession", "r870 sec8 same-window succession"),
    ("probe leg4 + r868 sec8", "probe leg4 + r870 sec8"),
    ("at fetch (r868 pre-seat", "at fetch (r870 pre-seat"),
    ("r565 law (r868 pre-seat", "r565 law (r870 pre-seat"),
    ("bm-c r741-window self-ack move", "bm-c r745-window self-ack move"),
    ("bm-a r867 freeze ", "bm-a r869 freeze "),
    ("(r307; bm-a r867)", "(r307; bm-a r869)"),
    ("bm-a r869 freeze,", "bm-a r874 freeze,"),
    ("r869 bm-a freeze", "r874 bm-a freeze"),
    ("r869 bm-a] ", "r874 bm-a] "),
    ("r868 receipt machine-read", "r870 receipt machine-read"),
    ("MSG-2026-10-08-0741-bma-w183-seat", "MSG-2026-10-08-0826-bma-w184-seat"),
    ("seat MSG-0741 tail,", "seat MSG-0826 tail,"),
    ("_r868bma_w183_probe_receipt.json", "_r870bma_w184_probe_receipt.json"),
    ("385dbafd8", "481da4d78"),
    ("ccd18034e", "d1f15ebf9"),
    # -- band geometry (projections FIRST, then registered bands, then
    #    naive rolls -- order law: proj consumed before the naive rolls
    #    re-create them; prior-B consumed before naive-B re-creates it) --
    ("419_404..421_403", "421_604..423_603"),
    ("419_604..419_803", "421_804..422_003"),
    ("419_404..419_603", "421_604..421_803"),
    ("417_404..419_403", "419_604..421_603"),
    ("417_204..419_203", "419_404..421_403"),
    ("417_204..417_403", "419_404..419_603"),
    ("417_404..417_603", "419_604..419_803"),
    # tail+1 pairs (own-A-tail first then prior-B-tail, S75/S76/S77/
    # S79/S80F/S81f/S82f/S83 order kept; tail roll = staircase
    # geometry: prior B tail 419_603 / own-A tail 421_603 --
    # machine-checked at runtime by the asserts)
    ("419_403+1", "421_603+1"),
    ("417_403+1", "419_603+1"),
    ('assert WAVE_CONFIGS[183]["a_seed_base"] == 417_404 == 417_403 + 1, (',
     'assert WAVE_CONFIGS[184]["a_seed_base"] == 419_604 == 419_603 + 1, ('),
    ('assert WAVE_CONFIGS[183]["b_exit_seed_base"] == 419_404 == 419_403 + 1, (',
     'assert WAVE_CONFIGS[184]["b_exit_seed_base"] == 421_604 == 421_603 + 1, ('),
    ("== 417_404 == 417_403 + 1", "== 419_604 == 419_603 + 1"),
    ("== 419_404 == 419_403 + 1", "== 421_604 == 421_603 + 1"),
    ("arith_a182", "arith_a183"),
    ("arith_b182", "arith_b183"),
    ("set(range(417_404, 419_404))", "set(range(419_604, 421_604))"),
    ("set(range(419_404, 419_604))", "set(range(421_604, 421_804))"),
    ('"a_seed_base": 417_404,', '"a_seed_base": 419_604,'),
    ('"b_exit_seed_base": 419_404,', '"b_exit_seed_base": 421_604,'),
    ('183: {"a": (417_404, 419_403), "b_exit": (419_404, 419_603),',
     '184: {"a": (419_604, 421_603), "b_exit": (421_604, 421_803),'),
    # jump phrases (physical fragment shapes, r869 bloodline; the
    # W183-era dry run caught the missing trio via the EN stale-token
    # tripwire -- all three now rolled)
    ("jumps to 419_404, first-clean ", "jumps to 421_604, first-clean "),
    ("jumps to 419_404 -> ", "jumps to 421_604 -> "),
    ("419_404 and lands ", "421_604 and lands "),
    # -- wave-word cascade (W184 first, then downward) --
    ("W184", "W185"),
    ("W183", "W184"),
    ("W182", "W183"),
    ("W181", "W182"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SEVENTY-THIRD", "ONE HUNDRED-AND-SEVENTY-FOURTH"),
    ("engine_owner rows 172", "engine_owner rows 173"),
    ("rows 98 + candidate", "rows 99 + candidate"),
    ("ninety-ninth", "one-hundredth"),
    ("FORTY-THIRD", "FORTY-FOURTH"),
    ("forty-third", "forty-fourth"),
    ("806,718", "808,918"),
    ("398,320", "400,520"),
    ("range(17, 183)", "range(17, 184)"),
    ("range(16, 183)", "range(16, 184)"),
    ("below 183 composes", "below 184 composes"),
    ("WAVE_CONFIGS if w < 183)", "WAVE_CONFIGS if w < 184)"),
    ("WAVE_CONFIGS[182]", "WAVE_CONFIGS[183]"),
    ('== pf.N1_BANDS[182]["a"][0]', '== pf.N1_BANDS[183]["a"][0]'),
    ('pf.N1_BANDS[182]["b_exit"][0]', 'pf.N1_BANDS[183]["b_exit"][0]'),
    ('pf.N1_BANDS[182].get("engine_owner")', 'pf.N1_BANDS[183].get("engine_owner")'),
    ("w182_a", "w183_a"),
    ("w182_b", "w183_b"),
    ("n3r1_used182", "n3r1_used183"),
    ('183: {"batch"', '184: {"batch"'),
    ("PERPETUAL_N1_W183_PREREG.md", "PERPETUAL_N1_W184_PREREG.md"),
    ("PERPETUAL-N1-W183", "PERPETUAL-N1-W184"),
    ('"n1_w183"', '"n1_w184"'),
    ('"n1_w183_results.json"', '"n1_w184_results.json"'),
    ("n1w183", "n1w184"),
    ("engine_owner=bm-a, wave 182: ", "engine_owner=bm-a, wave 183: "),
    ("wave 182 = first free number after", "wave 183 = first free number after"),
    ("_set_wave(183)", "_set_wave(184)"),
]


def s83(t):
    for old, new in S83:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W184 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r874bma_w184_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r874bma_w184_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r874bma_w184_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r874bma_w184_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD_R869 = '"registered W181 row parity drift (r307; bm-a r863)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if face == "MAT" and old == APPEND_OLD_R869:
            # special-case: chain append pair (historical rows carry; the
            # W183 row -- the current registered tail -- gets appended).
            n_old = '"registered W182 row parity drift (r307; bm-a r867)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[183] == {"a": (417_404, 419_403),' + NL +
                     '                                    "b_exit": (419_404, 419_603),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W183 row parity drift (r307; bm-a r869)"')
            if dump.count(n_old) != 1:
                fails.append("MAT append-pair old-side count %d != 1: %r" %
                             (dump.count(n_old), n_old))
            out.append((n_old, n_new, 1))
            continue
        n_old, n_new = new, s83(new)
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

# spot-check the S83 rolls before emission (fail loud, zero emission)
blk_probe = s83(DUMPS["PF"])
assert '184: {"a": (419_604, 421_603), "b_exit": (421_604, 421_803),' in blk_probe
assert "# W184 (bm-a r874 freeze" in blk_probe
assert "FORTY-FOURTH instance" in blk_probe
assert "# 421_604..423_603 CLEAN hops=0 / B first-clean 421_804..422_003" in blk_probe
assert "W185 A window; W185 freezer MUST re-derive on the post-W184" in blk_probe
entry_probe = s83(DUMPS["EN"])
assert '"a_seed_base": 419_604,' in entry_probe and '"b_exit_seed_base": 421_604,' in entry_probe
assert '"batch": "PERPETUAL-N1-W184",' in entry_probe
print("S83 spot-checks: PASS (pf block + entry seed rolls)")

# ---------- 4. NEG lists (mechanical: every consumed old side is a
# tripwire; append-pair old side excluded -- it legitimately remains
# as the prefix of the chain append) --------------------------------------
NEG = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    toks = []
    for n_old, n_new, _cnt in derived[key]:
        if face == "MAT" and n_old.startswith('"registered W182 row parity drift'):
            continue
        # skip no-op pairs (s83 found no roll -- wave-neutral prose that
        # legitimately remains) and partial-persistence shapes
        if n_new == n_old or n_old in n_new:
            continue
        if n_old not in toks:
            toks.append(n_old)
    # defense-in-depth extras (hand additions from the r869 NEG lists,
    # rolled one generation; harmless if absent)
    extra = {
        "PF": ["ccd18034e", "r865 probe", "r868 sec8", "r868 pre-seat",
               "_r868bma", "MSG-2026-10-08-0741", "385dbafd8",
               "806,718", "398,320", "FORTY-THIRD", "ONE HUNDRED-AND-SEVENTY-THIRD"],
        "EN": ["385dbafd8", "ccd18034e", "806,718", "398,320",
               "ONE HUNDRED-AND-SEVENTY-THIRD", "rows 172", "r865 probe",
               "_r868bma", "MSG-2026-10-08-0741", "n1w183", "n1_w183",
               "PERPETUAL-N1-W183", "PERPETUAL_N1_W183", "FORTY-THIRD",
               "bm-a r867 freeze", "419_404, first-clean"],
        "MAT": ["w182_", "arith_a182", "arith_b182", "n3r1_used182",
                "r865 probe", "r868 pre-seat", "385dbafd8",
                "ONE HUNDRED-AND-SEVENTY-THIRD", "ninety-ninth", "rows 172",
                "rows 98 ", "range(17, 183)", "range(16, 183)",
                "PERPETUAL_N1_W183", "PERPETUAL-N1-W183", "MSG-0741",
                "_r868bma", "bm-c r741-window", "n1w183", "n1_w183",
                "806,718", "398,320"],
        "CL": ["806,718", "398,320", "ONE HUNDRED-AND-SEVENTY-THIRD",
               "ninety-ninth", "rows 172", "rows 98 ", "FORTY-THIRD",
               "_r868bma", "r869 bm-a] "],
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


# ---------- 5. emit the W184 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r874 bm-a W184 freeze edits: four insertions (pf N1_BANDS[184] row +
n1 WAVE_CONFIGS[184] entry + n1 W184 materializer block + n1 W184
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845/r849/
r852/r863/r867/r869 dry-run precedent: full stale+prose+AST asserts
in memory BEFORE any write).

Bloodline: r819/r822/r826/r830/r834/r843/r845/r849/r852/r863/r867/r869
freeze-edits machinery (r773 pit law freeze-editor compliance + r776
fragment-needle law + r781 verify-separation law), W184 facts
live-registry-driven (built by _r874bma_w184_freeze_buildgen.py: old
sides = the PHYSICAL W183 face fragments probed to dumps this window,
new sides = the S83 W184 fact map, counts verified pre-emission):
  - pre-seat probe results/_r870bma_w184_probe_receipt.json rc0 ADMIT
    (naive A 419_404..421_403 refused at its own start by the
    registered W183 B band 419_404..419_603; honest forward walk
    1 hop lands A 419_604..421_603 staircase FORTY-FOURTH instance
    E36 -- receipt A_semantics machine-cites the W183 seat MSG leg4 +
    r868 W183 probe leg4 + W183 prereg sec5.5/sec8 anticipated +
    MANDATED this re-derive (projection and receipt ordinals MATCH,
    no divergence this wave); B 421_604..421_803 own-A mutual
    exclusion hops=1, naive 419_604..419_803);
  - face probe results/_r874bma_w184_face_probe_receipt.json rc0 (all
    four W183 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-0826-bma-w184-seat published on origin at
    d1f15ebf9 (r870 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- bm-c r745-window
    self-ack move (cross-machine consume, 1ec9800ae; machine-read git
    history this window -- the W184 prereg's "bm-c r741" citation is a
    stale session number superseded by machine-read, honest); the W184
    seat MSG sits in fleet/inbox/processed/ at freeze time, honest
    archived;
  - per-wave prereg research/PERPETUAL_N1_W184_PREREG.md built r872
    (buildgen r869-bloodline; banned gate ADMIT 0 verified at prereg
    build; frozen+pushed f908433c4 r872; on origin verified live
    below);
  - W183 freeze registered sha machine-derived = 481da4d78 (git log
    origin/main --grep "W183 FREEZE"); W183 finalize landed r870
    one-pass same-window: ledger head 808,918, merged pool K=400,520
    (n1_w183_results.json machine-read); W183 sec7/sec8 settle
    backfill landed the r870 SAME window (r864 lesson 2nd
    consecutive);
  - lineage constants disclosed (r795/r845/r849/r852/r863/r867/r869
    precedent, passed through): (a) the "wave N-1 = first free number"
    mat-header label rolls forward with its off-by-one quirk (since
    W165 r795); (b) "law sec.4 W184 row, r795" band-facts template
    stamp keeps its r795; (c) "single-window derive (r812 merged the
    gate legs INTO the pre-seat probe...)" stays (historical merge
    citation); (d) the bm-a-owned ordinal word rolls ninety-ninth ->
    one-hundredth (rows 99 + candidate = 100th owned per probe leg0 --
    first triple-digit crossing, word form machine-chosen
    "one-hundredth", disclosed); (e) mat parity-chain rows W138..W182
    keep their historical stamps and tuples; the W183 row (the
    current registered tail) is APPENDED with its frozen values
    (417_404, 419_403)/(419_404, 419_603); (f) the "W183 finalize
    landed same-window r827" citation rolls its wave-word with the
    stale r827 session stamp riding (off-by-one wave-word +
    stale-session lineage quirk inherited; head/K values roll
    machine-correct to 808,918/400,520 this window).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r874bma_w184_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W184 registration before
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
probe = json.load(open(r"results\\_r870bma_w184_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "419604_421603", "B": "421604_421803"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [419604, 421603], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [421604, 421803], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 181 and probe["legs"]["leg0"]["tail"] == "W183",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 174 and probe["legs"]["leg0"]["bma_ordinal"] == 100,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W185p_A"] == "421604..423603"
      and probe["legs"]["leg4"]["W185p_B"] == "421804..422003",
      "leg4 W185+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('184: {"a": (419_604' not in pf_o, "origin pf already carries W184 row")
check("W184 (bm-a r874 freeze" not in pf_o, "origin pf carries W184 block")
check('184: {"batch"' not in n1_o, "origin n1 already carries W184 entry")
check("# --- W184 materializer face" not in n1_o, "origin n1 carries W184 mat")
check('"r874 bm-a] "' not in n1_o, "origin n1 carries W184 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-0826-bma-w184-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "d1f15ebf9", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-0826-bma-w184-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w183_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W183 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w183_freeze_sha == "481da4d78", "W183 freeze sha mismatch: " + w183_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 181, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[183] == {"a": (417_404, 419_403),
                              "b_exit": (419_404, 419_603),
                              "engine_owner": "bm-a"}, "live W183 row drift")
check(184 not in pfmod.N1_BANDS, "live N1_BANDS already has 184")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W184_PREREG.md")),
      "W184 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W184_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W184 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r874bma_w184_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r874bma_w184_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r874bma_w184_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r874bma_w184_probe_n1_claim.txt", encoding="utf-8",
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
blk184 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry184 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat184 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim184 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W184 block after the W183 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk184 + NL + "}", 1)

# n1 entry: after the W183 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry184 + NL + IND23 + "}", 1)

# n1 mat: insert the W184 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat184 + NL + seg, 1)

# n1 claim: insert the W184 attribution after the W183 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r869 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r869 bm-a] "' + NL + claim184 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W184 presence + W183 anti-vanish (r560 law)
checks = [
    (pfnew, '184: {"a": (419_604, 421_603), "b_exit": (421_604, 421_803),', 1),
    (pfnew, '183: {"a": (417_404, 419_403), "b_exit": (419_404, 419_603),', 1),
    (pfnew, "# W184 (bm-a r874 freeze", 1),
    (pfnew, "# W183 (bm-a r869 freeze", 1),
    (n1new, '184: {"batch": "PERPETUAL-N1-W184",', 1),
    (n1new, '183: {"batch": "PERPETUAL-N1-W183",', 1),
    (n1new, "# --- W184 materializer face", 1),
    (n1new, "# --- W183 materializer face", 1),
    (n1new, '"r874 bm-a] "', 1),
    (n1new, '"r869 bm-a] "', 1),
    (n1new, '"a_seed_base": 419_604,', 1),
    (n1new, '"b_exit_seed_base": 421_604,', 1),
    (n1new, "n1_w184", 4),
    (n1new, "PERPETUAL_N1_W184_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W185+ projection prose present in the new W184 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W184+ per r845 precedent, n1 fragment =
# next-wave W185+)
check("# W184+ projection (gate-derived r870)" in pfnew,
      "pf W184+ projection head missing")
check('probe_receipt.json; W185+ projection "' in n1new,
      "n1 W185+ projection head fragment missing")
check("# 421_604..423_603 CLEAN hops=0 / B first-clean 421_804..422_003" in pfnew,
      "pf W185p prose missing")
check("W185 A window; W185 freezer MUST re-derive on the post-W184" in pfnew,
      "pf W185 freezer prose missing")
check('"W185 A window; W185 freezer MUST re-derive on the "' in n1new,
      "n1 W185 freezer fragment missing")
check('"W184 B band 421_604..421_803 will refuse the naive "' in n1new,
      "n1 W184-band refuse fragment missing")

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
check('184: {"a": (419_604' not in pf_o2, "write-time: origin pf carries W184")
check('184: {"batch"' not in n1_o2, "write-time: origin n1 carries W184")
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
io.open(r"results\_r874bma_w184_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r874bma_w184_freeze_edits.py", len(out), "bytes")
