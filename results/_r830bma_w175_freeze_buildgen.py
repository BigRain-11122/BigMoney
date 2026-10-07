# -*- coding: utf-8 -*-
"""r830 bm-a generator: builds results/_r830bma_w175_freeze_edits.py by
AST-extracting the r826 W174 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W175 pairs as (new174, S74(new174), cnt) -- old side =
the physical W174 face fragment (already probed to dumps this window
by _r830bma_w175_face_probe.py), new side = the W175 fact map applied
to that fragment.  Special-case: the mat parity-chain append pair is
constructed explicitly (historical rows carry, W174 row appended).
Every derived pair old-side is verified against the physical dumps
BEFORE emission (count == cnt); S74 negatives verified after."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r826 pairs --------------------------------
src = io.open(r"results\_r826bma_w174_freeze_edits.py", encoding="utf-8").read()
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
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and \
       node.targets[0].id in ("PF_NEG", "EN_NEG", "MAT_NEG", "CL_NEG") and \
       isinstance(node.value, ast.List):
        PAIRS[node.targets[0].id] = [ev(e) for e in node.value.elts]

for k in ("PF_PAIRS", "EN_PAIRS", "MAT_PAIRS", "CL_PAIRS"):
    assert k in PAIRS, k + " not extracted"
print("extracted: PF", len(PAIRS["PF_PAIRS"]), "EN", len(PAIRS["EN_PAIRS"]),
      "MAT", len(PAIRS["MAT_PAIRS"]), "CL", len(PAIRS["CL_PAIRS"]))

# ---------- 2. S74 = W174->W175 ordered fact map ---------------------------
S74 = [
    # -- session / finalize / sha composites (longest first) --
    ("W173 finalize landed same-window r823, ledger ",
     "W174 finalize landed same-window r827, ledger "),
    ("W173 finalize one-pass bm-a r823, net chain head 786,012, ",
     "W174 finalize one-pass bm-a r827, net chain head 788,212, "),
    ("finalize one-pass bm-a r823", "finalize one-pass bm-a r827"),
    ("bm-a r823 one-pass", "bm-a r827 one-pass"),
    ("on origin since r823, not re-shipped", "on origin since r827, not re-shipped"),
    ("already on origin since r823,", "already on origin since r827,"),
    ("(gate-derived r823)", "(gate-derived r828)"),
    ("r820 probe leg4", "r823 probe leg4"),
    ("projection + r820 probe", "projection + r823 probe"),
    ("r823 sec8 succession", "r826 sec8 succession"),
    ("probe leg4 + r823 sec8", "probe leg4 + r826 sec8"),
    ("at fetch (r823 pre-seat", "at fetch (r828 pre-seat"),
    ("r565 law (r823 pre-seat", "r565 law (r828 pre-seat"),
    ("r823 same-window self-ack move", "r828 same-window self-ack move"),
    ("bm-a r822 freeze ", "bm-a r826 freeze "),
    ("(r307; bm-a r822)", "(r307; bm-a r826)"),
    ("bm-a r826 freeze,", "bm-a r830 freeze,"),
    ("r826 bm-a freeze", "r830 bm-a freeze"),
    ("r826 bm-a] ", "r830 bm-a] "),
    ("r823 receipt machine-read", "r828 receipt machine-read"),
    ("MSG-2026-10-07-1247-bma-w174-seat", "MSG-2026-10-07-1434-bma-w175-seat"),
    ("seat MSG-1247 tail,", "seat MSG-1434 tail,"),
    ("_r823bma_w174_probe_receipt.json", "_r828bma_w175_probe_receipt.json"),
    ("04e95748a", "db42a0d46"),
    ("9b0e1cb29", "25c414e95"),
    # -- band geometry (projections first, then bands, naives, prior-B) --
    ("399_604..401_603", "401_804..403_803"),
    ("399_804..400_003", "402_004..402_203"),
    ("397_604..399_603", "399_804..401_803"),
    ("399_604..399_803", "401_804..402_003"),
    ("397_404..399_403", "399_604..401_603"),
    ("397_604..397_803", "399_804..400_003"),
    ("397_404..397_603", "399_604..399_803"),
    ("jumps to 399_604, first-clean ", "jumps to 401_804, first-clean "),
    ("jumps to 399_604 -> ", "jumps to 401_804 -> "),
    ("399_604 and lands ", "401_804 and lands "),
    ('174: {"a": (397_604, 399_603), "b_exit": (399_604, 399_803),',
     '175: {"a": (399_804, 401_803), "b_exit": (401_804, 402_003),'),
    ("397_603+1", "399_803+1"),
    ("399_603+1", "401_803+1"),
    ('assert WAVE_CONFIGS[174]["a_seed_base"] == 397_604 == 397_603 + 1, (',
     'assert WAVE_CONFIGS[175]["a_seed_base"] == 399_804 == 399_803 + 1, ('),
    ('assert WAVE_CONFIGS[174]["b_exit_seed_base"] == 399_604 == 399_603 + 1, (',
     'assert WAVE_CONFIGS[175]["b_exit_seed_base"] == 401_804 == 401_803 + 1, ('),
    ("== 397_604 == 397_603 + 1", "== 399_804 == 399_803 + 1"),
    ("== 399_604 == 399_603 + 1", "== 401_804 == 401_803 + 1"),
    ("arith_a173", "arith_a174"),
    ("arith_b173", "arith_b174"),
    ("set(range(397_604, 399_604))", "set(range(399_804, 401_804))"),
    ("set(range(399_604, 399_804))", "set(range(401_804, 402_004))"),
    ('"a_seed_base": 397_604,', '"a_seed_base": 399_804,'),
    ('"b_exit_seed_base": 399_604,', '"b_exit_seed_base": 401_804,'),
    # -- wave-word cascade (W175 first, then downward) --
    ("W175", "W176"),
    ("W174", "W175"),
    ("W173", "W174"),
    ("W172", "W173"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SIXTY-FOURTH", "ONE HUNDRED-AND-SIXTY-FIFTH"),
    ("engine_owner rows 163", "engine_owner rows 164"),
    ("rows 89 + candidate", "rows 90 + candidate"),
    ("ninetieth", "ninety-first"),
    ("THIRTY-FOURTH", "THIRTY-FIFTH"),
    ("thirty-fourth", "thirty-fifth"),
    ("786,012", "788,212"),
    ("378,520", "380,720"),
    ("range(17, 174)", "range(17, 175)"),
    ("range(16, 174)", "range(16, 175)"),
    ("below 174 composes", "below 175 composes"),
    ("WAVE_CONFIGS if w < 174)", "WAVE_CONFIGS if w < 175)"),
    ("WAVE_CONFIGS[173]", "WAVE_CONFIGS[174]"),
    ('== pf.N1_BANDS[173]["a"][0]', '== pf.N1_BANDS[174]["a"][0]'),
    ('pf.N1_BANDS[173]["b_exit"][0]', 'pf.N1_BANDS[174]["b_exit"][0]'),
    ('pf.N1_BANDS[173].get("engine_owner")', 'pf.N1_BANDS[174].get("engine_owner")'),
    ("w173_a", "w174_a"),
    ("w173_b", "w174_b"),
    ("n3r1_used173", "n3r1_used174"),
    ('174: {"batch"', '175: {"batch"'),
    ("PERPETUAL_N1_W174_PREREG.md", "PERPETUAL_N1_W175_PREREG.md"),
    ("PERPETUAL-N1-W174", "PERPETUAL-N1-W175"),
    ('"n1_w174"', '"n1_w175"'),
    ('"n1_w174_results.json"', '"n1_w175_results.json"'),
    ("n1w174", "n1w175"),
    ("engine_owner=bm-a, wave 173: ", "engine_owner=bm-a, wave 174: "),
    ("wave 173 = first free number after", "wave 174 = first free number after"),
    ("_set_wave(174)", "_set_wave(175)"),
]


def s74(t):
    for old, new in S74:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W175 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r830bma_w175_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r830bma_w175_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r830bma_w175_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r830bma_w175_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD = '"registered W172 row parity drift (r307; bm-a r819)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if old == APPEND_OLD:
            # special-case: chain append pair (historical rows carry; the
            # W174 row -- the current registered tail -- gets appended).
            # The old side is the W174 block's chain tail line (one
            # generation back from r826's old side -- constructed
            # explicitly, then count-verified against the dump below).
            n_old = '"registered W173 row parity drift (r307; bm-a r822)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[174] == {"a": (397_604, 399_603),' + NL +
                     '                                    "b_exit": (399_604, 399_803),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W174 row parity drift (r307; bm-a r826)"')
            if dump.count(n_old) != 1:
                fails.append("MAT append-pair old-side count %d != 1: %r" %
                             (dump.count(n_old), n_old))
            out.append((n_old, n_new, 1))
            continue
        n_old, n_new = new, s74(new)
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

# ---------- 4. NEG lists (W174-era stale-token tripwires) -----------------
NEG = {
    "PF_NEG": ["9b0e1cb29", "r820 probe", "r823 sec8", "r823 pre-seat",
               "_r823bma", "MSG-2026-10-07-1247", "r823 same-window",
               "397_404", "397_604", "397_803", "397_603+1", "399_603+1",
               "W173", "W174 (bm-a", "INSIDE the W174", "THIRTY-FOURTH",
               "W174+ projection (", "R250: W174", "W174 bands were",
               "786,012", "378,520", "the W174 seat MSG sits in",
               "since r823,", "r826 freeze"],
    "EN_NEG": ["9b0e1cb29", "04e95748a", "786,012", "378,520", "SIXTY-FOURTH",
               "rows 163", "r820 probe", "_r823bma", "r823 pre-seat",
               "r823 sec8", "MSG-2026-10-07-1247", "n1_w174", "n1w174",
               "PERPETUAL-N1-W174", "PERPETUAL_N1_W174", "W173 finalize",
               "thirty-fourth", "THIRTY-FOURTH", "bm-a r822 freeze",
               "wave 173: ", "W174 A band", "INSIDE the W174",
               "W174+ projection", "397_404", "397_604",
               "399_604, first-clean", "W1..W173", "W173 B band", "R250"],
    "MAT_NEG": ["w173_", "arith_a173", "arith_b173", "n3r1_used173",
                "r820 probe", "r823 sec8", "r823 pre-seat", "9b0e1cb29",
                "04e95748a", "SIXTY-FOURTH", "ninetieth", "rows 163",
                "rows 89 ", "range(17, 174)", "range(16, 174)", "W1..W173",
                "wave 173 =", "PERPETUAL_N1_W174", "PERPETUAL-N1-W174",
                "MSG-1247", "_r823bma", "the W174 seat MSG sits in",
                "r823 same-window", "W174 materializer", "INSIDE the W174",
                "THIRTY-FOURTH", "W174 bands", "W174 A band", "W174 A window",
                "W174 B window", "W174 A/B", "W174 hits",
                "W174 entry identity", "W174 path drift", "W174 shard dir",
                "W174 finalize cumulative", "W174 prior-wave",
                "W174 per-wave", "W174 engine_owner drift",
                "W174 A band drift", "W174 B band drift", "the W173 seat",
                "W173 B band", "W173 finalize", "bm-a r822 freeze",
                "post-W173", "seat MSG-1247", "n1w174", "n1_w174"],
    "CL_NEG": ["W174 materializer", "786,012", "378,520", "SIXTY-FOURTH",
               "ninetieth", "rows 163", "rows 89 ", "THIRTY-FOURTH",
               "W173 B band", "_r823bma", "W174 row,", "r826 bm-a] "],
}


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


# ---------- 5. emit the W175 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r830 bm-a W175 freeze edits: four insertions (pf N1_BANDS[175] row +
n1 WAVE_CONFIGS[175] entry + n1 W175 materializer block + n1 W175
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826 dry-run precedent: full
stale+prose+AST asserts in memory BEFORE any write).

Bloodline: r819/r822/r826 freeze-edits machinery (r773 pit law freeze-editor
compliance + r776 fragment-needle law + r781 verify-separation law),
W175 facts live-registry-driven (built by _r830bma_w175_freeze_buildgen.py:
old sides = the PHYSICAL W174 face fragments probed to dumps this window,
new sides = the S74 W175 fact map, counts verified pre-emission):
  - pre-seat probe results/_r828bma_w175_probe_receipt.json rc0 ADMIT
    (A 399_804..401_803 staircase THIRTY-FIFTH instance E36 hops=1
    past the registered W174 B band 399_604..399_803; naive
    399_604..401_603 refused at its own start by the W174 B band --
    receipt A_semantics machine-cites 'W174 prereg sec5 item5 + W174
    seat MSG leg4 + r823 probe leg4' anticipation + MANDATE; B
    401_804..402_003 own-A mutual exclusion hops=1, naive
    399_804..400_003);
  - ordinal convergence: W174 sec5.5 prose anticipated 35th, r828
    receipt machine-read THIRTY-FIFTH -- no divergence this wave;
  - face probe results/_r830bma_w175_face_probe_receipt.json rc0 (all
    four W174 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-07-1434-bma-w175-seat published on origin at
    25c414e95 (r828 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- r828 same-window
    self-ack move (the seat MSG sits in fleet/inbox/processed/ at
    freeze time, honest archived);
  - per-wave prereg research/PERPETUAL_N1_W175_PREREG.md frozen at
    origin 7510a8acf (r829 build, banned gate ADMIT 0 re-verified at
    freeze this window);
  - W174 freeze registered sha machine-derived = db42a0d46 (git log
    origin/main --grep "W174 FREEZE"); W174 finalize one-pass landed
    r827: ledger head 788,212, merged pool K=380,720
    (n1_w174_results.json machine-read);
  - lineage constants disclosed (r795 precedent, passed through):
    (a) the "wave N-1 = first free number" mat-header label rides the
    vmap verbatim (off-by-one lineage quirk since W165 r795);
    (b) "law sec.4 W175 row, r795" band-facts template stamp keeps
    its r795;
    (c) "single-window derive (r812 merged the gate legs INTO the
    pre-seat probe...)" stays (historical merge citation);
    (d) the bm-a-owned ordinal word rolls ninetieth -> ninety-first
    (rows 90 + candidate = 91st owned per probe leg0);
    (e) mat parity-chain rows W138..W173 keep their historical stamps
    and tuples; the W174 row (the current registered tail) is APPENDED
    with its frozen values (397_604, 399_603)/(399_604, 399_803).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r830bma_w175_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W175 registration before
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
probe = json.load(open(r"results\\_r828bma_w175_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "399804_401803", "B": "401804_402003"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [399804, 401803], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [401804, 402003], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 172 and probe["legs"]["leg0"]["tail"] == "W174",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 165 and probe["legs"]["leg0"]["bma_ordinal"] == 91,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W176p_A"] == "401804..403803"
      and probe["legs"]["leg4"]["W176p_B"] == "402004..402203",
      "leg4 W176+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('175: {"a": (399_804' not in pf_o, "origin pf already carries W175 row")
check("W175 (bm-a r830 freeze" not in pf_o, "origin pf carries W175 block")
check('175: {"batch"' not in n1_o, "origin n1 already carries W175 entry")
check("# --- W175 materializer face" not in n1_o, "origin n1 carries W175 mat")
check('"r830 bm-a] "' not in n1_o, "origin n1 carries W175 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-07-1434-bma-w175-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "25c414e95", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-07-1434-bma-w175-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w174_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W174 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w174_freeze_sha == "db42a0d46", "W174 freeze sha mismatch: " + w174_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 172, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[174] == {"a": (397_604, 399_603),
                              "b_exit": (399_604, 399_803),
                              "engine_owner": "bm-a"}, "live W174 row drift")
check(175 not in pfmod.N1_BANDS, "live N1_BANDS already has 175")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W175_PREREG.md")),
      "W175 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W175_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W175 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r830bma_w175_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r830bma_w175_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r830bma_w175_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r830bma_w175_probe_n1_claim.txt", encoding="utf-8",
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
blk175 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry175 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat175 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim175 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W175 block after the W174 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk175 + NL + "}", 1)

# n1 entry: after the W174 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry175 + NL + IND23 + "}", 1)

# n1 mat: insert the W175 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat175 + NL + seg, 1)

# n1 claim: insert the W175 attribution after the W174 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r826 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r826 bm-a] "' + NL + claim175 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W175 presence + W174 anti-vanish (r560 law)
checks = [
    (pfnew, '175: {"a": (399_804, 401_803), "b_exit": (401_804, 402_003),', 1),
    (pfnew, '174: {"a": (397_604, 399_603), "b_exit": (399_604, 399_803),', 1),
    (pfnew, "# W175 (bm-a r830 freeze", 1),
    (pfnew, "# W174 (bm-a r826 freeze", 1),
    (n1new, '175: {"batch": "PERPETUAL-N1-W175",', 1),
    (n1new, '174: {"batch": "PERPETUAL-N1-W174",', 1),
    (n1new, "# --- W175 materializer face", 1),
    (n1new, "# --- W174 materializer face", 1),
    (n1new, '"r830 bm-a] "', 1),
    (n1new, '"r826 bm-a] "', 1),
    (n1new, '"a_seed_base": 399_804,', 1),
    (n1new, '"b_exit_seed_base": 401_804,', 1),
    (n1new, "n1_w175", 4),
    (n1new, "PERPETUAL_N1_W175_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W176 projection prose present in the new W175 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law)
check("# W175+ projection (gate-derived r828)" in pfnew,
      "pf W175+ projection head missing")
check('probe_receipt.json; W176+ projection "' in n1new,
      "n1 W176+ projection head fragment missing")
check("# 401_804..403_803 CLEAN hops=0 / B first-clean 402_004..402_203" in pfnew,
      "pf W176p prose missing")
check("W176 A window; W176 freezer MUST re-derive on the post-W175" in pfnew,
      "pf W176 freezer prose missing")
check('"W176 A window; W176 freezer MUST re-derive on the "' in n1new,
      "n1 W176 freezer fragment missing")
check('"W175 B band 401_804..402_003 will refuse the naive "' in n1new,
      "n1 W175-band refuse fragment missing")

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
check('175: {"a": (399_804' not in pf_o2, "write-time: origin pf carries W175")
check('175: {"batch"' not in n1_o2, "write-time: origin n1 carries W175")
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
io.open(r"results\_r830bma_w175_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out.replace('NL = "\\r\\n"', 'NL = "\\r\\n"'))
print("emitted: results/_r830bma_w175_freeze_edits.py", len(out), "bytes")
