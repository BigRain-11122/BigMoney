# -*- coding: utf-8 -*-
"""r834 bm-a generator: builds results/_r834bma_w176_freeze_edits.py by
AST-extracting the r830 W175 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W176 pairs as (new175, S75(new175), cnt) -- old side =
the physical W175 face fragment (probed to dumps this window by
_r834bma_w176_face_probe.py), new side = the W176 fact map applied to
that W175 fragment.  Special-case: the mat parity-chain append pair is
constructed explicitly (historical rows carry, W175 row appended).
Every derived pair old-side is verified against the physical dumps
BEFORE emission (count == cnt); S75 negatives verified after.

r587 machine-derived facts (every displayed value read from on-disk
receipts this window):
  - pre-seat probe results/_r832bma_w176_probe_receipt.json rc0 ADMIT
    (leg0 registry 173 rows tail W175 ordinal 166 / bma_ordinal 92 /
    owner_rows 165 / bma_rows 91 / w175_ledger_head 790,412; leg1
    A 402_004..404_003 hops=1 / B 404_004..404_203 hops=1 / naive A
    401_804..403_803 refused at its own start by the registered W175 B
    band 401_804..402_003 (staircase THIRTY-SIXTH instance E36 per
    receipt A_semantics; W175 sec5.5 anticipated 36th -- projection
    and receipt ordinals MATCH, no divergence face this wave); naive B
    402_004..402_203 lands inside own-A 402_004..404_003; leg2
    conflicts 0; leg3 origin vacancy True; leg4 W177+ projection A
    404_004..406_003 hops=0 / B 404_204..404_403 hops=0, B inside A);
  - W175 finalize one-pass landed r831
    (results/perpetual_faces/n1_w175_results.json: merged K=382,920,
    ledger head 790,412);
  - W175 freeze registered sha machine-derived = f3fca4055 (git log
    origin/main --grep "W175 FREEZE"); W176 seat push sha
    machine-derived = 16a8ea982 (git log --diff-filter=A on the seat
    MSG inbox path); seat self-ack archive move landed r833 same
    window (commit 8d1fa8e9f on origin, processed/ path live-asserted
    this window);
  - per-wave prereg research/PERPETUAL_N1_W176_PREREG.md frozen at
    origin 21534ad82 (r833 build, banned gate ADMIT 0 re-verified at
    freeze this window).

S75 ORDER LAW (r735 substring-order law): projections consumed BEFORE
the naive rolls that re-create their strings (proj-A before naive-A,
proj-B before naive-B, B-band before prior-B-band); the tail+1 pair
FLIPPED vs S74 (B-tail "401_803+1"->"403_803+1" runs BEFORE A-tail
"399_803+1"->"401_803+1" because the A-tail roll re-creates the
B-tail source string -- first S75-generation interaction, flagged
here per the honest-disclosure face).
"""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r830 pairs --------------------------------
src = io.open(r"results\_r830bma_w175_freeze_edits.py", encoding="utf-8").read()
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

# ---------- 2. S75 = W175->W176 ordered fact map ---------------------------
S75 = [
    # -- session / finalize / sha composites (longest first) --
    ("W174 finalize landed same-window r827, ledger ",
     "W175 finalize landed same-window r831, ledger "),
    ("W174 finalize one-pass bm-a r827, net chain head 788,212, ",
     "W175 finalize one-pass bm-a r831, net chain head 790,412, "),
    ("finalize one-pass bm-a r827", "finalize one-pass bm-a r831"),
    ("bm-a r827 one-pass", "bm-a r831 one-pass"),
    ("on origin since r827, not re-shipped", "on origin since r831, not re-shipped"),
    ("already on origin since r827,", "already on origin since r831,"),
    ("(gate-derived r828)", "(gate-derived r832)"),
    ("r823 probe leg4", "r828 probe leg4"),
    ("projection + r823 probe", "projection + r828 probe"),
    ("r826 sec8 succession", "r831 sec8 succession"),
    ("probe leg4 + r826 sec8", "probe leg4 + r831 sec8"),
    ("at fetch (r828 pre-seat", "at fetch (r832 pre-seat"),
    ("r565 law (r828 pre-seat", "r565 law (r832 pre-seat"),
    ("r828 same-window self-ack move", "r833 same-window self-ack move"),
    ("bm-a r826 freeze ", "bm-a r830 freeze "),
    ("(r307; bm-a r826)", "(r307; bm-a r830)"),
    ("bm-a r830 freeze,", "bm-a r834 freeze,"),
    ("r830 bm-a freeze", "r834 bm-a freeze"),
    ("r830 bm-a] ", "r834 bm-a] "),
    ("r828 receipt machine-read", "r832 receipt machine-read"),
    ("MSG-2026-10-07-1434-bma-w175-seat", "MSG-2026-10-07-1630-bma-w176-seat"),
    ("seat MSG-1434 tail,", "seat MSG-1630 tail,"),
    ("_r828bma_w175_probe_receipt.json", "_r832bma_w176_probe_receipt.json"),
    ("db42a0d46", "f3fca4055"),
    ("25c414e95", "16a8ea982"),
    # -- band geometry (projections FIRST, then bands, naives, prior-B --
    # order law: proj consumed before the naive rolls re-create them)
    ("401_804..403_803", "404_004..406_003"),
    ("402_004..402_203", "404_204..404_403"),
    ("399_804..401_803", "402_004..404_003"),
    ("401_804..402_003", "404_004..404_203"),
    ("399_604..401_603", "401_804..403_803"),
    ("399_804..400_003", "402_004..402_203"),
    ("399_604..399_803", "401_804..402_003"),
    ("jumps to 401_804, first-clean ", "jumps to 404_004, first-clean "),
    ("jumps to 401_804 -> ", "jumps to 404_004 -> "),
    ("401_804 and lands ", "404_004 and lands "),
    ('175: {"a": (399_804, 401_803), "b_exit": (401_804, 402_003),',
     '176: {"a": (402_004, 404_003), "b_exit": (404_004, 404_203),'),
    # tail+1 pairs FLIPPED vs S74 (B-tail consumed BEFORE the A-tail
    # roll re-creates the B-tail source string); tail roll = +2,200
    # (band staircase geometry: prior B tail 402_003 / own-A tail
    # 404_003 -- NOT the naive +2,000 shift; first-pass selftest red
    # item caught the wrong roll, fixed pre-commit zero origin harm)
    ("401_803+1", "404_003+1"),
    ("399_803+1", "402_003+1"),
    ('assert WAVE_CONFIGS[175]["a_seed_base"] == 399_804 == 399_803 + 1, (',
     'assert WAVE_CONFIGS[176]["a_seed_base"] == 402_004 == 402_003 + 1, ('),
    ('assert WAVE_CONFIGS[175]["b_exit_seed_base"] == 401_804 == 401_803 + 1, (',
     'assert WAVE_CONFIGS[176]["b_exit_seed_base"] == 404_004 == 404_003 + 1, ('),
    ("== 399_804 == 399_803 + 1", "== 402_004 == 402_003 + 1"),
    ("== 401_804 == 401_803 + 1", "== 404_004 == 404_003 + 1"),
    ("arith_a174", "arith_a175"),
    ("arith_b174", "arith_b175"),
    ("set(range(399_804, 401_804))", "set(range(402_004, 404_004))"),
    ("set(range(401_804, 402_004))", "set(range(404_004, 404_204))"),
    ('"a_seed_base": 399_804,', '"a_seed_base": 402_004,'),
    ('"b_exit_seed_base": 401_804,', '"b_exit_seed_base": 404_004,'),
    # -- wave-word cascade (W177 first, then downward) --
    ("W176", "W177"),
    ("W175", "W176"),
    ("W174", "W175"),
    ("W173", "W174"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SIXTY-FIFTH", "ONE HUNDRED-AND-SIXTY-SIXTH"),
    ("engine_owner rows 164", "engine_owner rows 165"),
    ("rows 90 + candidate", "rows 91 + candidate"),
    ("ninety-first", "ninety-second"),
    ("THIRTY-FIFTH", "THIRTY-SIXTH"),
    ("thirty-fifth", "thirty-sixth"),
    ("788,212", "790,412"),
    ("380,720", "382,920"),
    ("range(17, 175)", "range(17, 176)"),
    ("range(16, 175)", "range(16, 176)"),
    ("below 175 composes", "below 176 composes"),
    ("WAVE_CONFIGS if w < 175)", "WAVE_CONFIGS if w < 176)"),
    ("WAVE_CONFIGS[174]", "WAVE_CONFIGS[175]"),
    ('== pf.N1_BANDS[174]["a"][0]', '== pf.N1_BANDS[175]["a"][0]'),
    ('pf.N1_BANDS[174]["b_exit"][0]', 'pf.N1_BANDS[175]["b_exit"][0]'),
    ('pf.N1_BANDS[174].get("engine_owner")', 'pf.N1_BANDS[175].get("engine_owner")'),
    ("w174_a", "w175_a"),
    ("w174_b", "w175_b"),
    ("n3r1_used174", "n3r1_used175"),
    ('175: {"batch"', '176: {"batch"'),
    ("PERPETUAL_N1_W175_PREREG.md", "PERPETUAL_N1_W176_PREREG.md"),
    ("PERPETUAL-N1-W175", "PERPETUAL-N1-W176"),
    ('"n1_w175"', '"n1_w176"'),
    ('"n1_w175_results.json"', '"n1_w176_results.json"'),
    ("n1w175", "n1w176"),
    ("engine_owner=bm-a, wave 174: ", "engine_owner=bm-a, wave 175: "),
    ("wave 174 = first free number after", "wave 175 = first free number after"),
    ("_set_wave(175)", "_set_wave(176)"),
]


def s75(t):
    for old, new in S75:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W176 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r834bma_w176_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r834bma_w176_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r834bma_w176_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r834bma_w176_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD_R830 = '"registered W173 row parity drift (r307; bm-a r822)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if face == "MAT" and old == APPEND_OLD_R830:
            # special-case: chain append pair (historical rows carry; the
            # W175 row -- the current registered tail -- gets appended).
            # The old side is the W175 block's chain tail line (one
            # generation back from r830's old side -- constructed
            # explicitly, then count-verified against the dump below).
            n_old = '"registered W174 row parity drift (r307; bm-a r826)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[175] == {"a": (399_804, 401_803),' + NL +
                     '                                    "b_exit": (401_804, 402_003),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W175 row parity drift (r307; bm-a r830)"')
            if dump.count(n_old) != 1:
                fails.append("MAT append-pair old-side count %d != 1: %r" %
                             (dump.count(n_old), n_old))
            out.append((n_old, n_new, 1))
            continue
        n_old, n_new = new, s75(new)
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

# ---------- 4. NEG lists (W175-era stale-token tripwires) -----------------
NEG = {
    "PF_NEG": ["25c414e95", "r823 probe", "r826 sec8", "r828 pre-seat",
               "_r828bma", "MSG-2026-10-07-1434", "r828 same-window",
               "399_604..401_603", "399_804..400_003", "399_804..401_803",
               "399_604..399_803", "399_803+1", "W174", "W175 (bm-a",
               "INSIDE the W175", "THIRTY-FIFTH", "W175+ projection (",
               "R250: W175", "W175 bands were", "788,212", "380,720",
               "the W175 seat MSG sits in", "since r827,", "r830 freeze"],
    "EN_NEG": ["25c414e95", "db42a0d46", "788,212", "380,720",
               "SIXTY-FIFTH", "rows 164", "r823 probe", "_r828bma",
               "r828 pre-seat", "r826 sec8", "MSG-2026-10-07-1434",
               "n1_w175", "n1w175", "PERPETUAL-N1-W175", "PERPETUAL_N1_W175",
               "W174 finalize", "thirty-fifth", "THIRTY-FIFTH",
               "bm-a r826 freeze", "wave 174: ", "W175 A band",
               "INSIDE the W175", "W174+ projection", "399_604",
               "401_804, first-clean", "W1..W174", "W174 B band", "R250"],
    "MAT_NEG": ["w174_", "arith_a174", "arith_b174", "n3r1_used174",
                "r823 probe", "r826 sec8", "r828 pre-seat", "25c414e95",
                "db42a0d46", "SIXTY-FIFTH", "ninety-first", "rows 164",
                "rows 90 ", "range(17, 175)", "range(16, 175)", "W1..W174",
                "wave 174 =", "PERPETUAL_N1_W175", "PERPETUAL-N1-W175",
                "MSG-1434", "_r828bma", "the W175 seat MSG sits in",
                "r828 same-window", "W175 materializer", "INSIDE the W175",
                "THIRTY-FIFTH", "W175 bands", "W175 A band", "W175 A window",
                "W175 B window", "W175 A/B", "W175 hits",
                "W175 entry identity", "W175 path drift", "W175 shard dir",
                "W175 finalize cumulative", "W175 prior-wave",
                "W175 per-wave", "W175 engine_owner drift",
                "W175 A band drift", "W175 B band drift", "the W174 seat",
                "W174 B band", "W174 finalize", "bm-a r826 freeze",
                "post-W174", "seat MSG-1434", "n1w175", "n1_w175",
                "788,212", "380,720"],
    "CL_NEG": ["W175 materializer", "788,212", "380,720", "SIXTY-FIFTH",
               "ninety-first", "rows 164", "rows 90 ", "THIRTY-FIFTH",
               "W174 B band", "_r828bma", "W175 row,", "r830 bm-a] "],
}

# NEG sanity (buildgen-side): every NEG token must be present in the
# W175-era dump (meaningful tripwire) -- informational only, zero-fail
for face, key in (("PF", "PF_NEG"), ("EN", "EN_NEG"), ("MAT", "MAT_NEG"),
                  ("CL", "CL_NEG")):
    dead = [t for t in NEG[key] if t not in DUMPS[face]]
    if dead:
        print("NEG warn (%s): tokens absent from W175 dump (kept, "
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


# ---------- 5. emit the W176 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r834 bm-a W176 freeze edits: four insertions (pf N1_BANDS[176] row +
n1 WAVE_CONFIGS[176] entry + n1 W176 materializer block + n1 W176
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830 dry-run precedent:
full stale+prose+AST asserts in memory BEFORE any write).

Bloodline: r819/r822/r826/r830 freeze-edits machinery (r773 pit law
freeze-editor compliance + r776 fragment-needle law + r781
verify-separation law), W176 facts live-registry-driven (built by
_r834bma_w176_freeze_buildgen.py: old sides = the PHYSICAL W175 face
fragments probed to dumps this window, new sides = the S75 W176 fact
map, counts verified pre-emission):
  - pre-seat probe results/_r832bma_w176_probe_receipt.json rc0 ADMIT
    (A 402_004..404_003 staircase THIRTY-SIXTH instance E36 hops=1
    past the registered W175 B band 401_804..402_003; naive
    401_804..403_803 refused at its own start by the W175 B band --
    receipt A_semantics machine-cites 'W175 sec5.5 anticipated 36th'
    (projection and receipt ordinals MATCH, no divergence this wave);
    B 404_004..404_203 own-A mutual exclusion hops=1, naive
    402_004..402_203);
  - face probe results/_r834bma_w176_face_probe_receipt.json rc0 (all
    four W175 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-07-1630-bma-w176-seat published on origin at
    16a8ea982 (r832 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- r833 same-window
    self-ack move (the seat MSG sits in fleet/inbox/processed/ at
    freeze time, honest archived);
  - per-wave prereg research/PERPETUAL_N1_W176_PREREG.md frozen at
    origin 21534ad82 (r833 build, banned gate ADMIT 0 re-verified at
    freeze this window);
  - W175 freeze registered sha machine-derived = f3fca4055 (git log
    origin/main --grep "W175 FREEZE"); W175 finalize one-pass landed
    r831: ledger head 790,412, merged pool K=382,920
    (n1_w175_results.json machine-read);
  - lineage constants disclosed (r795 precedent, passed through):
    (a) the "wave N-1 = first free number" mat-header label rides the
    vmap verbatim (off-by-one lineage quirk since W165 r795);
    (b) "law sec.4 W176 row, r795" band-facts template stamp keeps
    its r795;
    (c) "single-window derive (r812 merged the gate legs INTO the
    pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls ninety-first ->
    ninety-second (rows 91 + candidate = 92nd owned per probe leg0);
    (e) mat parity-chain rows W138..W174 keep their historical stamps
    and tuples; the W175 row (the current registered tail) is APPENDED
    with its frozen values (399_804, 401_803)/(401_804, 402_003).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r834bma_w176_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W176 registration before
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
probe = json.load(open(r"results\\_r832bma_w176_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "402004_404003", "B": "404004_404203"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [402004, 404003], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [404004, 404203], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 173 and probe["legs"]["leg0"]["tail"] == "W175",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 166 and probe["legs"]["leg0"]["bma_ordinal"] == 92,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W177p_A"] == "404004..406003"
      and probe["legs"]["leg4"]["W177p_B"] == "404204..404403",
      "leg4 W177+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('176: {"a": (402_004' not in pf_o, "origin pf already carries W176 row")
check("W176 (bm-a r834 freeze" not in pf_o, "origin pf carries W176 block")
check('176: {"batch"' not in n1_o, "origin n1 already carries W176 entry")
check("# --- W176 materializer face" not in n1_o, "origin n1 carries W176 mat")
check('"r834 bm-a] "' not in n1_o, "origin n1 carries W176 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-07-1630-bma-w176-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "16a8ea982", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-07-1630-bma-w176-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w175_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W175 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w175_freeze_sha == "f3fca4055", "W175 freeze sha mismatch: " + w175_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 173, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[175] == {"a": (399_804, 401_803),
                              "b_exit": (401_804, 402_003),
                              "engine_owner": "bm-a"}, "live W175 row drift")
check(176 not in pfmod.N1_BANDS, "live N1_BANDS already has 176")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W176_PREREG.md")),
      "W176 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W176_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W176 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r834bma_w176_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r834bma_w176_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r834bma_w176_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r834bma_w176_probe_n1_claim.txt", encoding="utf-8",
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
blk176 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry176 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat176 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim176 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W176 block after the W175 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk176 + NL + "}", 1)

# n1 entry: after the W175 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry176 + NL + IND23 + "}", 1)

# n1 mat: insert the W176 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat176 + NL + seg, 1)

# n1 claim: insert the W176 attribution after the W175 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r830 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r830 bm-a] "' + NL + claim176 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W176 presence + W175 anti-vanish (r560 law)
checks = [
    (pfnew, '176: {"a": (402_004, 404_003), "b_exit": (404_004, 404_203),', 1),
    (pfnew, '175: {"a": (399_804, 401_803), "b_exit": (401_804, 402_003),', 1),
    (pfnew, "# W176 (bm-a r834 freeze", 1),
    (pfnew, "# W175 (bm-a r830 freeze", 1),
    (n1new, '176: {"batch": "PERPETUAL-N1-W176",', 1),
    (n1new, '175: {"batch": "PERPETUAL-N1-W175",', 1),
    (n1new, "# --- W176 materializer face", 1),
    (n1new, "# --- W175 materializer face", 1),
    (n1new, '"r834 bm-a] "', 1),
    (n1new, '"r830 bm-a] "', 1),
    (n1new, '"a_seed_base": 402_004,', 1),
    (n1new, '"b_exit_seed_base": 404_004,', 1),
    (n1new, "n1_w176", 4),
    (n1new, "PERPETUAL_N1_W176_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W177 projection prose present in the new W176 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law)
check("# W176+ projection (gate-derived r832)" in pfnew,
      "pf W176+ projection head missing")
check('probe_receipt.json; W177+ projection "' in n1new,
      "n1 W177+ projection head fragment missing")
check("# 404_004..406_003 CLEAN hops=0 / B first-clean 404_204..404_403" in pfnew,
      "pf W177p prose missing")
check("W177 A window; W177 freezer MUST re-derive on the post-W176" in pfnew,
      "pf W177 freezer prose missing")
check('"W177 A window; W177 freezer MUST re-derive on the "' in n1new,
      "n1 W177 freezer fragment missing")
check('"W176 B band 404_004..404_203 will refuse the naive "' in n1new,
      "n1 W176-band refuse fragment missing")

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
check('176: {"a": (402_004' not in pf_o2, "write-time: origin pf carries W176")
check('176: {"batch"' not in n1_o2, "write-time: origin n1 carries W176")
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
io.open(r"results\_r834bma_w176_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r834bma_w176_freeze_edits.py", len(out), "bytes")
