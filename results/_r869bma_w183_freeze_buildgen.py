# -*- coding: utf-8 -*-
"""r869 bm-a generator: builds results/_r869bma_w183_freeze_edits.py by
AST-extracting the r867 W182 freeze-edits PAIRS (PF/EN/MAT/CL) and
deriving the W183 pairs as (new867, S82f(new867), cnt) -- old side =
the physical W182 face fragment (probed to dumps this window by
_r869bma_w183_face_probe.py), new side = the S82f W183 fact map applied
to that W182 fragment.  Special-case: the mat parity-chain append pair
is constructed explicitly (historical rows carry, W182 row appended).
Every derived pair old-side is verified against the physical dumps
BEFORE emission (count == cnt); S82f negatives verified after.

S82f ORDER LAW (r735 substring-order law): projections consumed BEFORE
the naive rolls that re-create their strings (proj-A before arith-A,
proj-B before naive-B, own-B consumed before prior-B); the tail+1 pair
order kept from S75/S76/S77/S79/S80F/S81f/S82f (A-tail then B-tail);
composite WAVE_CONFIGS assert pairs BEFORE the bare == rolls they
contain.

S82f LINEAGE CONSTANTS (r795/r845/r849/r852/r863/r867 precedent, passed
through):
  (a) the "wave N-1 = first free number" mat-header label rolls forward
  with its off-by-one quirk (since W165 r795);
  (b) "law sec.4 W183 row, r795" band-facts template stamp keeps its
  r795 (rolls to W183 row, keeps r795);
  (c) "single-window derive (r812 merged the gate legs INTO the
  pre-seat probe...)" stays (historical merge citation);
  (d) the bm-a-owned ordinal word rolls ninety-eighth -> ninety-ninth
  (rows 98 + candidate = 99th owned per probe leg0);
  (e) mat parity-chain rows W138..W181 keep their historical stamps
  and tuples; the W182 row (the current registered tail) is APPENDED
  with its frozen values (415_204, 417_203)/(417_204, 417_403);
  (f) the "W182 finalize landed same-window r827" citation rolls its
  wave-word with the stale r827 session stamp riding (off-by-one
  wave-word + stale-session lineage quirk inherited; head/K values
  roll machine-correct to 806,718/398,320 this window);
  (g) the self-ack archive move citation rolls to the bm-c r741
  window (cross-machine consume a79ceeb9b; the W183 seat MSG sits in
  fleet/inbox/processed/ at freeze time, honest archived).

r587 machine-derived facts (every displayed value read from on-disk
receipts this window):
  - pre-seat probe results/_r868bma_w183_probe_receipt.json rc0 ADMIT
    (leg0 registry 180 rows tail W182 ordinal 173 / bma_ordinal 99;
    leg1 naive A 417_204..419_203 REFUSED at its own start by the
    registered W182 B band 417_204..417_403 -> honest forward walk
    1 hop lands A 417_404..419_403 (staircase FORTY-THIRD instance E36;
    W182 seat leg4 + r865 probe leg4 + W182 prereg sec5.5/sec8
    anticipated and MANDATED this re-derive -- projection and receipt
    ordinals MATCH, no divergence face); naive B 417_404..417_603
    lands inside own-A 417_404..419_403 -> W141 mutual exclusion ->
    reserved walk 1 hop lands B 419_404..419_603; leg2 conflicts 0;
    leg3 origin vacancy True; leg4 W184+ projection A 419_404..421_403
    hops=0 / B 419_604..419_803 hops=0, B inside A);
  - W182 finalize landed r868 one-pass SAME-WINDOW, three-gate
    verified (results/perpetual_faces/n1_w182_results.json: merged
    K=398,320, ledger head 806,718); W182 sec7/sec8 settle backfill
    landed the r868 SAME window (r864 lesson welded into process --
    no heal window needed this wave);
  - W182 freeze registered sha machine-derived = 385dbafd8 (git log
    origin/main --grep "W182 FREEZE"); W183 seat push sha
    machine-derived = ccd18034e (git log --diff-filter=A on the seat
    MSG inbox path); seat self-ack archive landed via bm-c r741
    (a79ceeb9b, processed/ path live-asserted this window);
  - per-wave prereg research/PERPETUAL_N1_W183_PREREG.md built +
    banned gate ADMIT 0 verified this window (r869; push pending).

DRY discipline (r833 law 2): zero writes until every gate green -- the
emitted freeze-edits script is the ONLY writer, and it re-asserts
everything live (--dry first)."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---------- 1. AST-extract the r867 pairs --------------------------------
src = io.open(r"results\_r867bma_w182_freeze_edits.py", encoding="utf-8").read()
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

# ---------- 2. S82f = W182->W183 ordered fact map ---------------------------
S82F = [
    # -- session / finalize / sha composites (longest first) --
    ("W181 finalize one-pass bm-a r864, net chain head 804,518, ",
     "W182 finalize one-pass bm-a r868, net chain head 806,718, "),
    ("finalize one-pass bm-a r864", "finalize one-pass bm-a r868"),
    ("bm-a r864 one-pass", "bm-a r868 one-pass"),
    ("on origin since r864, not re-shipped", "on origin since r868, not re-shipped"),
    ("already on origin since r864,", "already on origin since r868,"),
    ("(gate-derived r865)", "(gate-derived r868)"),
    ("r862 probe leg4", "r865 probe leg4"),
    ("projection + r862 probe", "projection + r865 probe"),
    ("r867 sec8 heal succession", "r868 sec8 same-window succession"),
    ("probe leg4 + r867 sec8", "probe leg4 + r868 sec8"),
    ("at fetch (r865 pre-seat", "at fetch (r868 pre-seat"),
    ("r565 law (r865 pre-seat", "r565 law (r868 pre-seat"),
    ("bm-c r737-window self-ack move", "bm-c r741-window self-ack move"),
    ("bm-a r863 freeze ", "bm-a r867 freeze "),
    ("(r307; bm-a r863)", "(r307; bm-a r867)"),
    ("bm-a r867 freeze,", "bm-a r869 freeze,"),
    ("r867 bm-a freeze", "r869 bm-a freeze"),
    ("r867 bm-a] ", "r869 bm-a] "),
    ("r865 receipt machine-read", "r868 receipt machine-read"),
    ("MSG-2026-10-08-0603-bma-w182-seat", "MSG-2026-10-08-0741-bma-w183-seat"),
    ("seat MSG-0603 tail,", "seat MSG-0741 tail,"),
    ("_r865bma_w182_probe_receipt.json", "_r868bma_w183_probe_receipt.json"),
    ("de699e8cd", "385dbafd8"),
    ("df062c5c1", "ccd18034e"),
    # -- band geometry (projections FIRST, then bands, arith, prior-B,
    #    naive-B -- order law: proj consumed before the naive rolls
    #    re-create them; own-B consumed before prior-B re-creates it) --
    ("417_204..419_203", "419_404..421_403"),
    ("417_404..417_603", "419_604..419_803"),
    ("417_204..417_403", "419_404..419_603"),
    ("415_204..417_203", "417_404..419_403"),
    ("415_004..417_003", "417_204..419_203"),
    ("415_004..415_203", "417_204..417_403"),
    ("415_204..415_403", "417_404..417_603"),
    ("jumps to 417_204, first-clean ", "jumps to 419_404, first-clean "),
    ("jumps to 417_204 -> ", "jumps to 419_404 -> "),
    ("417_204 and lands ", "419_404 and lands "),
    ('182: {"a": (415_204, 417_203), "b_exit": (417_204, 417_403),',
     '183: {"a": (417_404, 419_403), "b_exit": (419_404, 419_603),'),
    # tail+1 pairs (A-tail first then B-tail, S75/S76/S77/S79/S80F/S81f/
    # S82f order kept; tail roll = staircase geometry: prior B tail
    # 417_403 / own-A tail 419_403 -- machine-checked at runtime by the
    # asserts)
    ("417_203+1", "419_403+1"),
    ("415_203+1", "417_403+1"),
    ('assert WAVE_CONFIGS[182]["a_seed_base"] == 415_204 == 415_203 + 1, (',
     'assert WAVE_CONFIGS[183]["a_seed_base"] == 417_404 == 417_403 + 1, ('),
    ('assert WAVE_CONFIGS[182]["b_exit_seed_base"] == 417_204 == 417_203 + 1, (',
     'assert WAVE_CONFIGS[183]["b_exit_seed_base"] == 419_404 == 419_403 + 1, ('),
    ("== 415_204 == 415_203 + 1", "== 417_404 == 417_403 + 1"),
    ("== 417_204 == 417_203 + 1", "== 419_404 == 419_403 + 1"),
    ("arith_a181", "arith_a182"),
    ("arith_b181", "arith_b182"),
    ("set(range(415_204, 417_204))", "set(range(417_404, 419_404))"),
    ("set(range(417_204, 417_404))", "set(range(419_404, 419_604))"),
    ('"a_seed_base": 415_204,', '"a_seed_base": 417_404,'),
    ('"b_exit_seed_base": 417_204,', '"b_exit_seed_base": 419_404,'),
    # -- wave-word cascade (W183 first, then downward) --
    ("W183", "W184"),
    ("W182", "W183"),
    ("W181", "W182"),
    ("W180", "W181"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-SEVENTY-SECOND", "ONE HUNDRED-AND-SEVENTY-THIRD"),
    ("engine_owner rows 171", "engine_owner rows 172"),
    ("rows 97 + candidate", "rows 98 + candidate"),
    ("ninety-eighth", "ninety-ninth"),
    ("FORTY-SECOND", "FORTY-THIRD"),
    ("forty-second", "forty-third"),
    ("804,518", "806,718"),
    ("396,120", "398,320"),
    ("range(17, 182)", "range(17, 183)"),
    ("range(16, 182)", "range(16, 183)"),
    ("below 182 composes", "below 183 composes"),
    ("WAVE_CONFIGS if w < 182)", "WAVE_CONFIGS if w < 183)"),
    ("WAVE_CONFIGS[181]", "WAVE_CONFIGS[182]"),
    ('== pf.N1_BANDS[181]["a"][0]', '== pf.N1_BANDS[182]["a"][0]'),
    ('pf.N1_BANDS[181]["b_exit"][0]', 'pf.N1_BANDS[182]["b_exit"][0]'),
    ('pf.N1_BANDS[181].get("engine_owner")', 'pf.N1_BANDS[182].get("engine_owner")'),
    ("w181_a", "w182_a"),
    ("w181_b", "w182_b"),
    ("n3r1_used181", "n3r1_used182"),
    ('182: {"batch"', '183: {"batch"'),
    ("PERPETUAL_N1_W182_PREREG.md", "PERPETUAL_N1_W183_PREREG.md"),
    ("PERPETUAL-N1-W182", "PERPETUAL-N1-W183"),
    ('"n1_w182"', '"n1_w183"'),
    ('"n1_w182_results.json"', '"n1_w183_results.json"'),
    ("n1w182", "n1w183"),
    ("engine_owner=bm-a, wave 181: ", "engine_owner=bm-a, wave 182: "),
    ("wave 181 = first free number after", "wave 182 = first free number after"),
    ("_set_wave(182)", "_set_wave(183)"),
]


def s82f(t):
    for old, new in S82F:
        t = t.replace(old, new)
    return t


# ---------- 3. derive W183 pairs; verify old sides on physical dumps -------
DUMPS = {
    "PF": io.open(r"results\_r869bma_w183_probe_pf_block.txt", encoding="utf-8",
                  newline="").read(),
    "EN": io.open(r"results\_r869bma_w183_probe_n1_entry.txt", encoding="utf-8",
                  newline="").read(),
    "MAT": io.open(r"results\_r869bma_w183_probe_n1_mat.txt", encoding="utf-8",
                   newline="").read(),
    "CL": io.open(r"results\_r869bma_w183_probe_n1_claim.txt", encoding="utf-8",
                  newline="").read(),
}
APPEND_OLD_R867 = '"registered W180 row parity drift (r307; bm-a r852)"'
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        if face == "MAT" and old == APPEND_OLD_R867:
            # special-case: chain append pair (historical rows carry; the
            # W182 row -- the current registered tail -- gets appended).
            n_old = '"registered W181 row parity drift (r307; bm-a r863)"'
            n_new = (n_old + NL +
                     '        assert pf.N1_BANDS[182] == {"a": (415_204, 417_203),' + NL +
                     '                                    "b_exit": (417_204, 417_403),' + NL +
                     '                                    "engine_owner": "bm-a"}, \\' + NL +
                     '            "registered W182 row parity drift (r307; bm-a r867)"')
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
assert '183: {"a": (417_404, 419_403), "b_exit": (419_404, 419_603),' in blk_probe
assert "# W183 (bm-a r869 freeze" in blk_probe
assert "FORTY-THIRD instance" in blk_probe
assert "# 419_404..421_403 CLEAN hops=0 / B first-clean 419_604..419_803" in blk_probe
assert "W184 A window; W184 freezer MUST re-derive on the post-W183" in blk_probe
entry_probe = s82f(DUMPS["EN"])
assert '"a_seed_base": 417_404,' in entry_probe and '"b_exit_seed_base": 419_404,' in entry_probe
assert '"batch": "PERPETUAL-N1-W183",' in entry_probe
print("S82f spot-checks: PASS (pf block + entry seed rolls)")

# ---------- 4. NEG lists (mechanical: every consumed old side is a
# tripwire; append-pair old side excluded -- it legitimately remains
# as the prefix of the chain append) --------------------------------------
NEG = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"), ("MAT", "MAT_PAIRS"),
                  ("CL", "CL_PAIRS")):
    toks = []
    for n_old, n_new, _cnt in derived[key]:
        if face == "MAT" and n_old.startswith('"registered W181 row parity drift'):
            continue
        # skip no-op pairs (s82f found no roll -- wave-neutral prose that
        # legitimately remains) and partial-persistence shapes
        if n_new == n_old or n_old in n_new:
            continue
        if n_old not in toks:
            toks.append(n_old)
    # defense-in-depth extras (hand additions from the r867 NEG lists,
    # rolled one generation; harmless if absent)
    extra = {
        "PF": ["df062c5c1", "r862 probe", "r867 sec8", "r865 pre-seat",
               "_r865bma", "MSG-2026-10-08-0603", "de699e8cd",
               "804,518", "396,120", "FORTY-SECOND", "ONE HUNDRED-AND-SEVENTY-SECOND"],
        "EN": ["de699e8cd", "df062c5c1", "804,518", "396,120",
               "ONE HUNDRED-AND-SEVENTY-SECOND", "rows 171", "r862 probe",
               "_r865bma", "MSG-2026-10-08-0603", "n1w182", "n1_w182",
               "PERPETUAL-N1-W182", "PERPETUAL_N1_W182", "FORTY-SECOND",
               "bm-a r863 freeze", "417_204, first-clean"],
        "MAT": ["w181_", "arith_a181", "arith_b181", "n3r1_used181",
                "r862 probe", "r865 pre-seat", "de699e8cd",
                "ONE HUNDRED-AND-SEVENTY-SECOND", "ninety-eighth", "rows 171",
                "rows 97 ", "range(17, 182)", "range(16, 182)",
                "PERPETUAL_N1_W182", "PERPETUAL-N1-W182", "MSG-0603",
                "_r865bma", "bm-c r737-window", "n1w182", "n1_w182",
                "804,518", "396,120"],
        "CL": ["804,518", "396,120", "ONE HUNDRED-AND-SEVENTY-SECOND",
               "ninety-eighth", "rows 171", "rows 97 ", "FORTY-SECOND",
               "_r865bma", "r867 bm-a] "],
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


# ---------- 5. emit the W183 freeze script --------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r869 bm-a W183 freeze edits: four insertions (pf N1_BANDS[183] row +
n1 WAVE_CONFIGS[183] entry + n1 W183 materializer block + n1 W183
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + r811/r822/r826/r830/r834/r843/r845/r849/
r852/r863/r867 dry-run precedent: full stale+prose+AST asserts in memory
BEFORE any write).

Bloodline: r819/r822/r826/r830/r834/r843/r845/r849/r852/r863/r867
freeze-edits machinery (r773 pit law freeze-editor compliance + r776
fragment-needle law + r781 verify-separation law), W183 facts
live-registry-driven (built by _r869bma_w183_freeze_buildgen.py: old
sides = the PHYSICAL W182 face fragments probed to dumps this window,
new sides = the S82f W183 fact map, counts verified pre-emission):
  - pre-seat probe results/_r868bma_w183_probe_receipt.json rc0 ADMIT
    (naive A 417_204..419_203 refused at its own start by the
    registered W182 B band 417_204..417_403; honest forward walk
    1 hop lands A 417_404..419_403 staircase FORTY-THIRD instance E36
    -- receipt A_semantics machine-cites the W182 seat MSG leg4 + r865
    probe leg4 anticipated + MANDATED this re-derive (W182 sec5.5
    prose anticipated 43rd -- projection and receipt ordinals MATCH,
    no divergence this wave); B 419_404..419_603 own-A mutual exclusion
    hops=1, naive 417_404..417_603);
  - face probe results/_r869bma_w183_face_probe_receipt.json rc0 (all
    four W182 faces dumped + needle counts; this TOK is built from the
    PHYSICAL probe-dumped shapes, r776 law);
  - seat MSG-2026-10-08-0741-bma-w183-seat published on origin at
    ccd18034e (r868 pre-seat push, path-derived TRUE sha per r812
    precedent); r565 law: on origin BEFORE this freeze commit;
    self-ack archive ALREADY LANDED pre-freeze -- bm-c r741-window
    self-ack move (cross-machine consume, a79ceeb9b); the W183 seat
    MSG sits in fleet/inbox/processed/ at freeze time, honest archived;
  - per-wave prereg research/PERPETUAL_N1_W183_PREREG.md built this
    window (r869 buildgen r867-bloodline; banned gate ADMIT 0
    verified at prereg build; prereg-freeze push this window);
  - W182 freeze registered sha machine-derived = 385dbafd8 (git log
    origin/main --grep "W182 FREEZE"); W182 finalize landed r868
    one-pass same-window: ledger head 806,718, merged pool K=398,320
    (n1_w182_results.json machine-read); W182 sec7/sec8 settle
    backfill landed the r868 SAME window (r864 lesson welded into
    process -- no heal window needed, honest);
  - lineage constants disclosed (r795/r845/r849/r852/r863/r867
    precedent, passed through): (a) the "wave N-1 = first free number"
    mat-header label rolls forward with its off-by-one quirk (since
    W165 r795); (b) "law sec.4 W183 row, r795" band-facts template
    stamp keeps its r795; (c) "single-window derive (r812 merged the
    gate legs INTO the pre-seat probe...)" stays (historical merge
    citation); (d) the bm-a-owned ordinal word rolls ninety-eighth ->
    ninety-ninth (rows 98 + candidate = 99th owned per probe leg0);
    (e) mat parity-chain rows W138..W181 keep their historical stamps
    and tuples; the W182 row (the current registered tail) is APPENDED
    with its frozen values (415_204, 417_203)/(417_204, 417_403);
    (f) the "W182 finalize landed same-window r827" citation rolls its
    wave-word with the stale r827 session stamp riding (off-by-one
    wave-word + stale-session lineage quirk inherited; head/K values
    roll machine-correct to 806,718/398,320 this window).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (_r869bma_w183_face_probe.py -- four face dumps + needle-count
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
      (r530/r687: fetch + origin carries no W183 registration before
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
probe = json.load(open(r"results\\_r868bma_w183_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "417404_419403", "B": "419404_419603"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [417404, 419403], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [419404, 419603], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 180 and probe["legs"]["leg0"]["tail"] == "W182",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 173 and probe["legs"]["leg0"]["bma_ordinal"] == 99,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W184p_A"] == "419404..421403"
      and probe["legs"]["leg4"]["W184p_B"] == "419604..419803",
      "leg4 W184+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check('183: {"a": (417_404' not in pf_o, "origin pf already carries W183 row")
check("W183 (bm-a r869 freeze" not in pf_o, "origin pf carries W183 block")
check('183: {"batch"' not in n1_o, "origin n1 already carries W183 entry")
check("# --- W183 materializer face" not in n1_o, "origin n1 carries W183 mat")
check('"r869 bm-a] "' not in n1_o, "origin n1 carries W183 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-0741-bma-w183-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "ccd18034e", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-0741-bma-w183-seat.md")),
    "seat MSG not in processed/ at freeze time (self-ack archive)")
w182_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--grep=W182 FREEZE"],
    capture_output=True).stdout.decode().strip()
check(w182_freeze_sha == "385dbafd8", "W182 freeze sha mismatch: " + w182_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, "scripts")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 180, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[182] == {"a": (415_204, 417_203),
                              "b_exit": (417_204, 417_403),
                              "engine_owner": "bm-a"}, "live W182 row drift")
check(183 not in pfmod.N1_BANDS, "live N1_BANDS already has 183")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W183_PREREG.md")),
      "W183 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W183_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W183 prereg absent on origin")

# ---- physical face dumps (r776 law) -----------------------------------
pfblk = io.open(r"results\\_r869bma_w183_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r869bma_w183_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r869bma_w183_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r869bma_w183_probe_n1_claim.txt", encoding="utf-8",
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
blk183 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry183 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat183 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim183 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W183 block after the W182 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk183 + NL + "}", 1)

# n1 entry: after the W182 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry183 + NL + IND23 + "}", 1)

# n1 mat: insert the W183 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat183 + NL + seg, 1)

# n1 claim: insert the W183 attribution after the W182 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = '"r867 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, '"r867 bm-a] "' + NL + claim183 + NL + IND10 +
                      '"+ T-141 s2 "', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W183 presence + W182 anti-vanish (r560 law)
checks = [
    (pfnew, '183: {"a": (417_404, 419_403), "b_exit": (419_404, 419_603),', 1),
    (pfnew, '182: {"a": (415_204, 417_203), "b_exit": (417_204, 417_403),', 1),
    (pfnew, "# W183 (bm-a r869 freeze", 1),
    (pfnew, "# W182 (bm-a r867 freeze", 1),
    (n1new, '183: {"batch": "PERPETUAL-N1-W183",', 1),
    (n1new, '182: {"batch": "PERPETUAL-N1-W182",', 1),
    (n1new, "# --- W183 materializer face", 1),
    (n1new, "# --- W182 materializer face", 1),
    (n1new, '"r869 bm-a] "', 1),
    (n1new, '"r867 bm-a] "', 1),
    (n1new, '"a_seed_base": 417_404,', 1),
    (n1new, '"b_exit_seed_base": 419_404,', 1),
    (n1new, "n1_w183", 4),
    (n1new, "PERPETUAL_N1_W183_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W184+ projection prose present in the new W183 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W183+ per r845 precedent, n1 fragment =
# next-wave W184+)
check("# W183+ projection (gate-derived r868)" in pfnew,
      "pf W183+ projection head missing")
check('probe_receipt.json; W184+ projection "' in n1new,
      "n1 W184+ projection head fragment missing")
check("# 419_404..421_403 CLEAN hops=0 / B first-clean 419_604..419_803" in pfnew,
      "pf W184p prose missing")
check("W184 A window; W184 freezer MUST re-derive on the post-W183" in pfnew,
      "pf W184 freezer prose missing")
check('"W184 A window; W184 freezer MUST re-derive on the "' in n1new,
      "n1 W184 freezer fragment missing")
check('"W183 B band 419_404..419_603 will refuse the naive "' in n1new,
      "n1 W183-band refuse fragment missing")

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
check('183: {"a": (417_404' not in pf_o2, "write-time: origin pf carries W183")
check('183: {"batch"' not in n1_o2, "write-time: origin n1 carries W183")
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
io.open(r"results\_r869bma_w183_freeze_edits.py", "w", encoding="utf-8",
        newline="").write(out)
ast.parse(out)
print("emitted: results/_r869bma_w183_freeze_edits.py", len(out), "bytes")
