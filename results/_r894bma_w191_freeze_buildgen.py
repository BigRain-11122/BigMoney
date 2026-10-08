# -*- coding: utf-8 -*-
"""r894 bm-a S90 buildgen: derives results/_r894bma_w191_freeze_edits.py by
AST-extracting the r892 EMITTED freeze-edits tool's PF/EN/MAT/CL pairs
(extraction-from-emission law, zero exec of its live writes), then rolling
each pair ONE generation: my OLD side = the r892 tool's NEW column (= the
live W190 faces, physically probe-dumped by the r893 window to
results/_r893bma_w191_probe_*.txt, re-verified against the LIVE files this
window), my NEW side = s90(old) where S90 = the W190->W191 ordered fact
map (r735 substring-order law: projections consumed before the naive rolls
re-create them; own-B before prior-B; cascade high-first so the parity
quirk chain cannot double-roll).

Machine-derived facts (r587, read from on-disk receipts this lineage):
  - pre-seat probe results/_r892bma_w191_probe_receipt.json rc0 ADMIT:
    naive A 434_804..436_803 refused at its own start by the registered
    W190 B band 434_804..435_003 -> honest forward walk 1 hop lands A
    435_004..437_003 staircase FIFTY-FIRST instance E36; naive B
    435_004..435_203 lands inside own-wave A -> reserved walk 1 hop lands
    B 437_004..437_203 (W141 leg2); leg2 conflicts 0; leg3 origin vacancy
    True; leg4 W192+ projection A 437_004..439_003 hops=0 / B
    437_204..437_403 hops=0, B inside A (re-derive-MANDATORY rides).
  - W190 finalize landed r892-continuation one-pass: ledger head 825,328,
    merged pool K=415,920 (n1_w190_results.json machine-read in the r893
    buildgen asserts); W190 sec7/sec8 settle backfill landed the r893
    window (first-leg) -- so the W191 block's sec8 succession citation
    rolls r892 -> r893 (NOT the +2 session shift; factual roll,
    disclosed).
  - W191 seat MSG-2026-10-08-2130-bma-w191-seat pushed r892-continuation
    1c28dd21d (r565 law held at freeze time); archive landed the r892
    ROUND-CLOSEOUT window (adeaab565) -- same-round cross-window archive:
    the archive-move prose rolls "bm-a r892-window" ->
    "bm-a r892-closeout-window" (NOT r894; disclosed, mirrors the r893
    buildgen's seat-face disclosure).
  - W190 five-face registration sha machine-derived = 0cce3c47e
    (content-anchored git log -S '190: {"a": (432_804');
    W191 per-wave prereg frozen+pushed ea42ee94a r893 (r511 tail-lock:
    origin carries no W191 five-face freeze yet, re-checked live).
  - ordinal words: "ONE HUNDRED-AND-NINETIETH" -> "ONE HUNDRED-AND-
    NINETY-FIRST" and "one-hundred-sixth" -> "one-hundred-seventh"
    continue the r892-established wave-number ordinal convention
    (W190 block says 190th with rows 179+candidate; W191 probe leg0:
    rows 188 / tail W190 / ordinal 181 / bma_ordinal 107 / owner_rows
    180 / bma_rows 106 -- matches the frozen prereg 第 181 波 +
    第一百零七枚自有波 + 行 106+本候选 exactly).
  - deep-history dotted bands (430_*/428_*) verified ZERO occurrences
    in the r892 pairs' NEW sides this window -> dropped from S90 (the
    mat parity assert's TUPLE forms (426_204, 428_203) ride verbatim per
    quirk (e); the [186]-row stamp session r882 rides STALE per quirk
    (f) -- cascade high-first W191..W188 keeps both quirks intact).
"""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"

# ---- 1. AST-extract the r892 EMITTED tool's pairs ------------------------
src892 = io.open(r"results/_r892bma_w190_freeze_edits.py",
                 encoding="utf-8", newline="").read()
tree = ast.parse(src892)


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
       node.targets[0].id in ("PF_PAIRS", "EN_PAIRS", "MAT_PAIRS",
                              "CL_PAIRS") and isinstance(node.value,
                                                          ast.List):
        out = []
        for el in node.value.elts:
            assert isinstance(el, ast.Tuple) and len(el.elts) == 3, "pair shape"
            out.append((ev(el.elts[0]), ev(el.elts[1]), ev(el.elts[2])))
        PAIRS[node.targets[0].id] = out

for k in ("PF_PAIRS", "EN_PAIRS", "MAT_PAIRS", "CL_PAIRS"):
    assert k in PAIRS, k + " not extracted"
print("extracted: PF", len(PAIRS["PF_PAIRS"]), "EN", len(PAIRS["EN_PAIRS"]),
      "MAT", len(PAIRS["MAT_PAIRS"]), "CL", len(PAIRS["CL_PAIRS"]))

# ---- 2. S90 = W190->W191 ordered fact map --------------------------------
S90 = [
    # -- session / finalize / sha composites (longest first) --
    ("W189 finalize one-pass bm-a r891, net chain head 823,128, ",
     "W190 finalize one-pass bm-a r892, net chain head 825,328, "),
    ("finalize one-pass bm-a r891", "finalize one-pass bm-a r892"),
    ("bm-a r891 one-pass", "bm-a r892 one-pass"),
    ("on origin since r890, not re-shipped", "on origin since r892, not re-shipped"),
    ("already on origin since r890,", "already on origin since r892,"),
    ("(gate-derived r891)", "(gate-derived r892)"),
    ("r891 probe leg4", "r892 probe leg4"),
    ("projection + r891 probe", "projection + r892 probe"),
    ("r892 sec8 回填窗 succession", "r893 sec8 回填窗 succession"),
    ("probe leg4 + r892 sec8", "probe leg4 + r893 sec8"),
    ("at fetch (r891 pre-seat", "at fetch (r892 pre-seat"),
    ("r565 law (r891 pre-seat", "r565 law (r892 pre-seat"),
    ("bm-a r892-window archive move", "bm-a r892-closeout-window archive move"),
    ("bm-a r890 freeze ", "bm-a r892 freeze "),
    ("(r307; bm-a r890)", "(r307; bm-a r892)"),
    ("bm-a r892 freeze,", "bm-a r894 freeze,"),
    ("r892 bm-a freeze", "r894 bm-a freeze"),
    ("r892 bm-a] ", "r894 bm-a] "),
    ("r891 receipt machine-read", "r892 receipt machine-read"),
    ("MSG-2026-10-08-2035-bma-w190-seat", "MSG-2026-10-08-2130-bma-w191-seat"),
    ("seat MSG-2035 tail,", "seat MSG-2130 tail,"),
    ("_r891bma_w190_probe_receipt.json", "_r892bma_w191_probe_receipt.json"),
    ("8addea3eb", "0cce3c47e"),
    ("c177bf73b", "1c28dd21d"),
    # -- band geometry (projections FIRST, then own bands, then the
    #    prior-wave reference rolls that re-create the consumed strings;
    #    deep-history 430_*/428_* entries dropped -- verified 0 hits) --
    ("434_804..436_803", "437_004..439_003"),      # proj-A (W192+)
    ("435_004..435_203", "437_204..437_403"),      # proj-B (W192+)
    ("434_804..435_003", "437_004..437_203"),      # own-B (W191 B)
    ("432_804..434_803", "435_004..437_003"),      # own-A (W191 A)
    ("432_604..432_803", "434_804..435_003"),      # prior-B (W190 B)
    ("432_604..434_603", "434_804..436_803"),      # naive-A (W191)
    ("432_804..433_003", "435_004..435_203"),      # naive-B (W191)
    # tail+1 pairs (prior-B-tail first then own-A-tail; staircase geometry:
    # prior B tail 435_003 / own-A tail 437_003 -- runtime-asserted)
    ("432_803+1", "435_003+1"),
    ("434_803+1", "437_003+1"),
    ('assert WAVE_CONFIGS[190]["a_seed_base"] == 432_804 == 432_803 + 1, (',
     'assert WAVE_CONFIGS[191]["a_seed_base"] == 435_004 == 435_003 + 1, ('),
    ('assert WAVE_CONFIGS[190]["b_exit_seed_base"] == 434_804 == 434_803 + 1, (',
     'assert WAVE_CONFIGS[191]["b_exit_seed_base"] == 437_004 == 437_003 + 1, ('),
    ("== 432_804 == 432_803 + 1", "== 435_004 == 435_003 + 1"),
    ("== 434_804 == 434_803 + 1", "== 437_004 == 437_003 + 1"),
    ("arith_a189", "arith_a190"),
    ("arith_b189", "arith_b190"),
    ("set(range(432_804, 434_804))", "set(range(435_004, 437_004))"),
    ("set(range(434_804, 435_004))", "set(range(437_004, 437_204))"),
    ('"a_seed_base": 432_804,', '"a_seed_base": 435_004,'),
    ('"b_exit_seed_base": 434_804,', '"b_exit_seed_base": 437_004,'),
    ('190: {"a": (432_804, 434_803), "b_exit": (434_804, 435_003),',
     '191: {"a": (435_004, 437_003), "b_exit": (437_004, 437_203),'),
    # jump phrases (physical fragment shapes, all three rolled one gen)
    ("jumps to 434_804, first-clean ", "jumps to 437_004, first-clean "),
    ("jumps to 434_804 -> ", "jumps to 437_004 -> "),
    ("434_804 and lands ", "437_004 and lands "),
    # -- wave-word cascade (high first; depth 4 = deepest ref W188) --
    ("W191", "W192"),
    ("W190", "W191"),
    ("W189", "W190"),
    ("W188", "W189"),
    # -- ordinals / counts / vars / filenames --
    ("ONE HUNDRED-AND-NINETIETH", "ONE HUNDRED-AND-NINETY-FIRST"),
    ("engine_owner rows 179", "engine_owner rows 180"),
    ("rows 105 + candidate", "rows 106 + candidate"),
    ("one-hundred-sixth", "one-hundred-seventh"),
    ("FIFTIETH", "FIFTY-FIRST"),
    ("fiftieth", "fifty-first"),
    ("823,128", "825,328"),
    ("413,720", "415,920"),
    ("range(17, 190)", "range(17, 191)"),
    ("range(16, 190)", "range(16, 191)"),
    ("below 190 composes", "below 191 composes"),
    ("WAVE_CONFIGS if w < 190)", "WAVE_CONFIGS if w < 191)"),
    ("WAVE_CONFIGS[189]", "WAVE_CONFIGS[190]"),
    ('== pf.N1_BANDS[189]["a"][0]', '== pf.N1_BANDS[190]["a"][0]'),
    ('pf.N1_BANDS[189]["b_exit"][0]', 'pf.N1_BANDS[190]["b_exit"][0]'),
    ('pf.N1_BANDS[189].get("engine_owner")', 'pf.N1_BANDS[190].get("engine_owner")'),
    ("w189_a", "w190_a"),
    ("w189_b", "w190_b"),
    ("n3r1_used189", "n3r1_used190"),
    ('190: {"batch"', '191: {"batch"'),
    ("PERPETUAL_N1_W190_PREREG.md", "PERPETUAL_N1_W191_PREREG.md"),
    ("PERPETUAL-N1-W190", "PERPETUAL-N1-W191"),
    ('"n1_w190"', '"n1_w191"'),
    ('"n1_w190_results.json"', '"n1_w191_results.json"'),
    ("n1w190", "n1w191"),
    ("engine_owner=bm-a, wave 189: ", "engine_owner=bm-a, wave 190: "),
    ("wave 189 = first free number after", "wave 190 = first free number after"),
    ("_set_wave(190)", "_set_wave(191)"),
]


def s90(t):
    for old, new in S90:
        t = t.replace(old, new)
    return t


# ---- 3. derive W191 pairs; verify old sides on physical dumps ------------
DUMPS = {
    "PF": io.open(r"results/_r893bma_w191_probe_pf_block.txt",
                  encoding="utf-8", newline="").read(),
    "EN": io.open(r"results/_r893bma_w191_probe_n1_entry.txt",
                  encoding="utf-8", newline="").read(),
    "MAT": io.open(r"results/_r893bma_w191_probe_n1_mat.txt",
                   encoding="utf-8", newline="").read(),
    "CL": io.open(r"results/_r893bma_w191_probe_n1_claim.txt",
                  encoding="utf-8", newline="").read(),
}
fails = []
derived = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"),
                  ("MAT", "MAT_PAIRS"), ("CL", "CL_PAIRS")):
    dump = DUMPS[face]
    out = []
    for old, new, cnt in PAIRS[key]:
        n_old, n_new = new, s90(new)
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

# ---- spot-check the S90 rolls before emission (fail loud, zero emission)
blk_probe = s90(DUMPS["PF"])
assert '191: {"a": (435_004, 437_003), "b_exit": (437_004, 437_203),' \
    in blk_probe, "pf row roll"
assert "# W191 (bm-a r894 freeze" in blk_probe, "pf header roll"
assert "FIFTY-FIRST instance" in blk_probe, "pf staircase roll"
assert "# 437_004..439_003 CLEAN hops=0 / B first-clean 437_204..437_403" \
    in blk_probe, "pf W192+ projection roll"
assert "W192 A window; W192 freezer MUST re-derive on the post-W191" \
    in blk_probe, "pf freezer prose roll"
assert "bm-a r892-closeout-window archive move (the W191" in blk_probe and \
    "seat MSG sits in fleet/inbox/processed/ at freeze time" in blk_probe, \
    "pf archive prose roll"
assert "r893 sec8" in blk_probe and "r892 sec8" not in blk_probe, \
    "pf sec8 window roll"
entry_probe = s90(DUMPS["EN"])
assert '"a_seed_base": 435_004,' in entry_probe \
    and '"b_exit_seed_base": 437_004,' in entry_probe, "entry seed rolls"
assert '"batch": "PERPETUAL-N1-W191",' in entry_probe, "entry batch roll"
assert "ONE HUNDRED-AND-NINETY-FIRST ENGINE-OWNED WAVE" in entry_probe, \
    "entry ordinal word roll"
assert "engine_owner rows 180 + candidate" in entry_probe, "rows roll"
assert "W1..W190 finalize ALL LANDED (W190 " in entry_probe \
    and "finalize one-pass bm-a r892, net chain head 825,328, " in entry_probe, \
    "entry finalize citation roll"
assert "W192+ projection " in entry_probe, "entry next-wave projection roll"
mat_probe = s90(DUMPS["MAT"])
assert '"registered W190 row parity drift (r307; bm-a r892)"' in mat_probe, \
    "mat last parity stamp roll"
assert '"registered W189 row parity drift (r307; bm-a r882)"' in mat_probe, \
    "mat stale quirk stamp rides"
assert 'assert pf.N1_BANDS[187] == {"a": (426_204, 428_203),' in mat_probe, \
    "mat parity tuple rides"
assert "_set_wave(191)" in mat_probe and "_set_wave(190)" not in mat_probe, \
    "mat set_wave roll"
assert "arith_a190 = set(range(435_004, 437_004))" in mat_probe, "mat arith A"
assert "arith_b190 = set(range(437_004, 437_204))" in mat_probe, "mat arith B"
assert "range(17, 191)" in mat_probe, "mat dep range roll"
claim_probe = s90(DUMPS["CL"])
assert '"r894 bm-a] "' in claim_probe, "claim stamp roll"
assert "one-hundred-seventh owned claim" in claim_probe, "claim ordinal roll"
print("S90 spot-checks: PASS (pf/entry/mat/claim composites)")

# ---- 4. NEG lists (mechanical: every consumed old side is a tripwire) ----
NEG = {}
for face, key in (("PF", "PF_PAIRS"), ("EN", "EN_PAIRS"),
                  ("MAT", "MAT_PAIRS"), ("CL", "CL_PAIRS")):
    toks = []
    for n_old, n_new, _cnt in derived[key]:
        if n_new == n_old or n_old in n_new:
            continue
        if n_old not in toks:
            toks.append(n_old)
    extra = {
        "PF": ["c177bf73b", "r891 probe", "r892 sec8", "r891 pre-seat",
               "_r891bma", "MSG-2026-10-08-2035", "8addea3eb",
               "823,128", "413,720", "FIFTIETH",
               "ONE HUNDRED-AND-NINETIETH"],
        "EN": ["8addea3eb", "c177bf73b", "823,128", "413,720",
               "ONE HUNDRED-AND-NINETIETH", "rows 179", "r891 probe",
               "_r891bma", "MSG-2026-10-08-2035", "n1w190", "n1_w190",
               "PERPETUAL-N1-W190", "PERPETUAL_N1_W190", "FIFTIETH",
               "bm-a r890 freeze", "434_804, first-clean"],
        "MAT": ["w189_", "arith_a189", "arith_b189", "n3r1_used189",
                "r891 probe", "r891 pre-seat", "8addea3eb",
                "ONE HUNDRED-AND-NINETIETH", "one-hundred-sixth",
                "rows 179", "rows 105 ", "range(17, 190)",
                "range(16, 190)", "PERPETUAL_N1_W190", "PERPETUAL-N1-W190",
                "MSG-2035", "_r891bma", "bm-a r892-window", "n1w190",
                "n1_w190", "823,128", "413,720"],
        "CL": ["823,128", "413,720", "ONE HUNDRED-AND-NINETIETH",
               "one-hundred-sixth", "rows 179", "rows 105 ", "FIFTIETH",
               "_r891bma", "r892 bm-a] "],
    }[face]
    for t in extra:
        if t not in toks:
            toks.append(t)
    NEG[key] = toks
print("NEG lists:", {k: len(v) for k, v in NEG.items()})

# ---- 5. emit the W191 freeze-edits tool ------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r894 bm-a W191 freeze edits: four insertions (pf N1_BANDS[191] row +
n1 WAVE_CONFIGS[191] entry + n1 W191 materializer block + n1 W191
PASS-claim attribution). DRY flag: --dry = zero-write simulation
(r781 verify-separation law + freeze-edits dry-run precedent: full
stale+prose+AST asserts in memory BEFORE any write).

Bloodline: freeze-edits machinery (r773 pit law freeze-editor compliance +
r776 fragment-needle law + r781 verify-separation law), W191 facts
live-registry-driven (built by _r894bma_w191_freeze_buildgen.py: old
sides = the PHYSICAL W190 face fragments probed by the r893 window
(results/_r893bma_w191_probe_*.txt, re-verified against the live files
this window), new sides = the S90 W191 fact map, counts verified
pre-emission; extraction-from-EMISSION law: pairs AST-carried from the
r892 emitted tool -- the ground truth that produced the live faces).
Factual rolls disclosed in the buildgen docstring: sec8 succession
citation r892 -> r893 (the W190 sec7/sec8 backfill landed the r893
window, NOT a +2 session shift); archive-move prose r892-window ->
r892-closeout-window (the W191 seat MSG archive landed the r892 ROUND-
CLOSEOUT window adeaab565, same-round cross-window); ordinal words
continue the r892-established wave-number convention (NINETIETH ->
NINETY-FIRST, rows 180 + candidate per probe leg0 = 181st wave / 107th
bm-a-owned, matches the frozen prereg sec.0 exactly); deep-history
430_*/428_* dotted bands verified ZERO in the pair space -> S90 drops
them (mat parity tuples + the [186]-row r882 stale stamp ride verbatim
per quirks (e)/(f), cascade high-first keeps them intact).

r773 pit law compliance:
  (1) full string-face inventory empirically probed BEFORE TOK
      (r893 window four face dumps + stage-1 receipt, rc0; re-verified
      against the live files this window, count==1 each);
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
      (r530/r687: fetch + origin carries no W191 registration before
      this freeze);
  (7) AST gate after every edit batch (r580/r781)."""
import ast
import io
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, "scripts")
DRY = "--dry" in sys.argv
PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
EO = \'"engine_owner": "bm-a"},\'
NL = "\\r\\n"
IND23 = " " * 23
IND10 = " " * 10

fail = []


def check(cond, msg):
    if not cond:
        fail.append(msg)
        print("FAIL:", msg)


# ---- receipts / machine-derived facts --------------------------------
probe = json.load(open(r"results\\_r892bma_w191_probe_receipt.json",
                       encoding="utf-8"))
check(probe["verdict"] == "ADMIT", "pre-seat probe not ADMIT")
check(probe["bands"] == {"A": "435004_437003", "B": "437004_437203"},
      "probe band shape mismatch")
check(probe["legs"]["leg1"]["A"] == [435004, 437003], "A band mismatch")
check(probe["legs"]["leg1"]["B"] == [437004, 437203], "B band mismatch")
check(probe["legs"]["leg1"]["hops_A"] == 1 and probe["legs"]["leg1"]["hops_B"] == 1,
      "hops mismatch")
check(probe["legs"]["leg0"]["rows"] == 188 and probe["legs"]["leg0"]["tail"] == "W190",
      "leg0 registry tail mismatch")
check(probe["legs"]["leg0"]["ordinal"] == 181 and probe["legs"]["leg0"]["bma_ordinal"] == 107,
      "leg0 ordinal mismatch")
check(probe["legs"]["leg2"]["conflicts"] == 0, "leg2 conflicts nonzero")
check(probe["legs"]["leg3"]["origin_vacancy"] is True, "leg3 origin not vacant")
check(probe["legs"]["leg4"]["W192p_A"] == "437004..439003"
      and probe["legs"]["leg4"]["W192p_B"] == "437204..437403",
      "leg4 W192+ projection mismatch")

# origin anti-collision pre-check (r511 tail-lock / r687 write-time gate)
subprocess.run(["git", "fetch", "origin"], capture_output=True)
pf_o = subprocess.run(["git", "show", "origin/main:" + PF],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:" + N1],
                      capture_output=True).stdout.decode("utf-8", "replace")
check(\'191: {"a": (435_004\' not in pf_o, "origin pf already carries W191 row")
check("# W191 (bm-a r894 freeze" not in pf_o, "origin pf carries W191 block")
check(\'191: {"batch"\' not in n1_o, "origin n1 already carries W191 entry")
check("# --- W191 materializer face" not in n1_o, "origin n1 carries W191 mat")
check(\'"r894 bm-a] "\' not in n1_o, "origin n1 carries W191 claim")

# machine-derived shas (r587 / r812 path-derived precedent)
seat_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
     "--", "fleet/inbox/MSG-2026-10-08-2130-bma-w191-seat.md"],
    capture_output=True).stdout.decode().strip()
check(seat_sha == "1c28dd21d", "seat sha path-derived mismatch: " + seat_sha)
check(os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-2130-bma-w191-seat.md")),
    "seat MSG not in on-disk processed/ at freeze time (r892-closeout archive)")
w190_freeze_sha = subprocess.run(
    ["git", "log", "origin/main", "--format=%h", "-n", "1",
     "-S", \'190: {"a": (432_804\', "--", "scripts/perpetual_faces.py"],
    capture_output=True).stdout.decode().strip()
check(w190_freeze_sha == "0cce3c47e",
      "W190 five-face registration sha mismatch (content-anchored): "
      + w190_freeze_sha)

# ---- live-registry parity pre-check (edit-gate: never edit a drifted file)
sys.path.insert(0, ".")
import perpetual_faces as pfmod  # noqa: E402
check(len(pfmod.N1_BANDS) == 188, "live N1_BANDS row count drift: %d" % len(pfmod.N1_BANDS))
check(pfmod.N1_BANDS[190] == {"a": (432_804, 434_803),
                              "b_exit": (434_804, 435_003),
                              "engine_owner": "bm-a"}, "live W190 row drift")
check(191 not in pfmod.N1_BANDS, "live N1_BANDS already has 191")
check(os.path.exists(os.path.join("research", "PERPETUAL_N1_W191_PREREG.md")),
      "W191 per-wave prereg missing (materializer gate)")
prereg_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W191_PREREG.md"],
                          capture_output=True)
check(prereg_o.returncode == 0, "W191 prereg absent on origin")

# ---- physical face dumps (r776 law; r893 window probes) ------------------
pfblk = io.open(r"results\\_r893bma_w191_probe_pf_block.txt", encoding="utf-8",
                newline="").read()
entry = io.open(r"results\\_r893bma_w191_probe_n1_entry.txt", encoding="utf-8",
                newline="").read()
mat = io.open(r"results\\_r893bma_w191_probe_n1_mat.txt", encoding="utf-8",
              newline="").read()
claim = io.open(r"results\\_r893bma_w191_probe_n1_claim.txt", encoding="utf-8",
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

TAIL = '''
blk191 = vmap(pfblk, PF_PAIRS, PF_NEG, "pf")
entry191 = IND23 + vmap(entry, EN_PAIRS, EN_NEG, "entry")
mat191 = "    " + vmap(mat, MAT_PAIRS, MAT_NEG, "mat")
claim191 = IND10 + vmap(claim, CL_PAIRS, CL_NEG, "claim")

# ---- apply insertions (in-memory) ---------------------------------------
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# pf: insert W191 block after the W190 row (last registered), before the
# dict close -- r560 insert-after-last-registered-row + post-anchor gate
seg = EO + NL + "}"
check(pfsrc.count(seg) == 1, "pf row-close segment not unique")
pfnew = pfsrc.replace(seg, EO + NL + blk191 + NL + "}", 1)

# n1 entry: after the W190 entry, before the WAVE_CONFIGS close
seg = EO + NL + IND23 + "}"
check(n1src.count(seg) == 1, "n1 entry-close segment not unique")
n1new = n1src.replace(seg, EO + NL + entry191 + NL + IND23 + "}", 1)

# n1 mat: insert the W191 block before the T-141 s2 lane face header
seg = "    # --- T-141 s2 lane face"
check(n1new.count(seg) == 1, "n1 T-141 mat anchor not unique")
n1new = n1new.replace(seg, mat191 + NL + seg, 1)

# n1 claim: insert the W191 attribution after the W190 claim tail line
# (r581 law: anchor = tail single-line literal + post-anchor guard)
seg = \'"r892 bm-a] "\' + NL + IND10 + \'"+ T-141 s2 "\'
check(n1new.count(seg) == 1, "n1 claim anchor not unique")
n1new = n1new.replace(seg, \'"r892 bm-a] "\' + NL + claim191 + NL + IND10 +
                      \'"+ T-141 s2 "\', 1)

# ---- gates (r780/r781/r560/r815 lineage) --------------------------------
ast.parse(pfnew)
ast.parse(n1new)
print("AST gate: both files parse OK")

# W191 presence + W190 anti-vanish (r560 law)
checks = [
    (pfnew, \'191: {"a": (435_004, 437_003), "b_exit": (437_004, 437_203),\', 1),
    (pfnew, \'190: {"a": (432_804, 434_803), "b_exit": (434_804, 435_003),\', 1),
    (pfnew, "# W191 (bm-a r894 freeze", 1),
    (pfnew, "# W190 (bm-a r892 freeze", 1),
    (n1new, \'191: {"batch": "PERPETUAL-N1-W191",\', 1),
    (n1new, \'190: {"batch": "PERPETUAL-N1-W190",\', 1),
    (n1new, "# --- W191 materializer face", 1),
    (n1new, "# --- W190 materializer face", 1),
    (n1new, \'"r894 bm-a] "\', 1),
    (n1new, \'"r892 bm-a] "\', 1),
    (n1new, \'"a_seed_base": 435_004,\', 1),
    (n1new, \'"b_exit_seed_base": 437_004,\', 1),
    (n1new, "n1_w191", 4),
    (n1new, "PERPETUAL_N1_W191_PREREG.md", 2),
]
for src, needle, cnt in checks:
    got = src.count(needle)
    check(got == cnt, "post-edit needle %r count %d != %d" % (needle[:50], got, cnt))

# W192+ projection prose present in the new W191 blocks (probe leg4
# verbatim; r819 post-edit assert bloodline + r776 fragment-needle law;
# pf header = self-wave W191+ per r845 precedent, n1 fragment =
# next-wave W192+)
check("# W191+ projection (gate-derived r892)" in pfnew,
      "pf W191+ projection head missing")
check(\'probe_receipt.json; W192+ projection "\' in n1new,
      "n1 W192+ projection head fragment missing")
check("# 437_004..439_003 CLEAN hops=0 / B first-clean 437_204..437_403" in pfnew,
      "pf W192p prose missing")
check("W192 A window; W192 freezer MUST re-derive on the post-W191" in pfnew,
      "pf W192 freezer prose missing")
check(\'"W192 A window; W192 freezer MUST re-derive on the "\' in n1new,
      "n1 W192 freezer fragment missing")
check(\'"W191 B band 437_004..437_203 will refuse the naive "\' in n1new,
      "n1 W191-band refuse fragment missing")

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
check(\'191: {"a": (435_004\' not in pf_o2, "write-time: origin pf carries W191")
check(\'191: {"batch"\' not in n1_o2, "write-time: origin n1 carries W191")
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

# assemble the pair literals (order preserved, counts carried)
pair_lit = []
for key in ("PF_PAIRS", "EN_PAIRS", "MAT_PAIRS", "CL_PAIRS"):
    pair_lit.append(key + " = " + repr([(a, b, c) for a, b, c in derived[key]]))
neg_lit = []
for key in ("PF_NEG", "EN_NEG", "MAT_NEG", "CL_NEG"):
    src_key = key.replace("_NEG", "_PAIRS")
    neg_lit.append(key + " = " + repr(NEG[src_key]))

out = HDR + "\n" + "\n\n".join(pair_lit) + "\n\n" + "\n\n".join(neg_lit) + TAIL
io.open(r"results/_r894bma_w191_freeze_edits.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r894bma_w191_freeze_edits.py", len(out), "bytes")
