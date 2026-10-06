# -*- coding: utf-8 -*-
"""r794 bm-a W165 freeze toolset deriver v2 (anchored-uniform design).

Supersedes the dead-session _r794bma_w165_deriv_all.py (composite+singles
sequential replace = structurally unsound: single-value rules re-mapped
composite outputs (double-advance), tuple forms lacked anchored rules;
derived face_probe was mixed-era corrupted).

v2 design (r793 _r793bma_w165_deriv.py bloodline, generalized):
  P0  anchored composites: receipt paths, seat/registration shas, MSG ids,
      underscore band pairs, frozen-source byte length (run FIRST; needles
      carry old-era values that P1 must not corrupt).
  P1  uniform +2,200 arithmetic on ALL wave-advancing numbers (dotted
      3xx_xxx band values; 3,3 comma K/ledger forms; bare 6-digit values
      >= 300000 -- float fragments 0.0004xx/0.088xxx/0.245xxx/1.18xx are
      below the gate and protected). Staircase is uniform: every band/K/
      ledger value advances exactly +2,200 per wave (verified W163->W164
      ->W165 against N1_BANDS and gate receipts).
  P2  W-token blanket advance, DESCENDING (W165->W166 first). W155 floor:
      the se_mu chain head W141..W160 and the W136.. delta chain are
      historical prose in the SOURCE (pass-through), never in the tool.
  P3  session advance, DESCENDING (r792->r794 first). TOK-side entries
      advance to the prior BACK verbatim; BACK-side entries advance to
      the current window (r794).
  P4  3-digit site composites, DESCENDING (row keys, --wave, N1_BANDS[],
      WAVE_CONFIGS[], range(), 波号, ordinals-in-prose).
  P5  ordinal advance, DESCENDING (EN + ZH).
  P6  prereg_build ONLY: live-fact surgicals (post-pass anchored needles;
      W164 finalize facts live-derived from n1_w164_results.json, r587)
      + EXPECT empirical rebuild from the frozen W164 prereg source.

Every surgical carries a pre-check assert (fail-loud on needle drift).
Derived tools carry their own anchor/residue asserts + AST gate.
"""
import ast
import io
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def read(p):
    return io.open(p, encoding="utf-8", newline="").read()


def write(p, s):
    io.open(p, "w", encoding="utf-8", newline="").write(s)


def die(msg):
    raise SystemExit(f"DERIVER FAIL: {msg}")


# ---------------------------------------------------------------- P0
P0 = [
    # receipt paths (W165 gate/probe receipts were made by r793)
    ("_r792bma_w164_band_gate.json", "_r793bma_w165_band_gate.json"),
    ("_r792bma_w164_probe_receipt.json", "_r793bma_w165_probe_receipt.json"),
    # seat/registration shas, DESCENDING (newest first; created forms stay)
    ("469d40896", "4bdf63090"),      # W164 seat sha -> W165 seat sha (r793)
    ("189157de8", "469d40896"),      # W163 seat sha -> W164 seat sha
    ("18231a529", "f7d34e5a7"),      # W163 freeze sha -> W164 freeze sha
    ("764cd882a", "18231a529"),      # W162 freeze sha -> W163 freeze sha
    # MSG ids (full forms + seat-tail short form), DESCENDING
    ("MSG-2026-10-06-194x", "MSG-2026-10-06-205x"),
    ("seat MSG-194x tail", "seat MSG-205x tail"),
    ("MSG-2026-10-06-183x", "MSG-2026-10-06-194x"),
    ("seat MSG-183x tail", "seat MSG-194x tail"),
    # underscore band pairs (invisible to P1 regexes: no word boundaries)
    ("377604_377803", "379804_380003"),
    ("375604_377603", "377804_379803"),
    ("373404_375403", "375604_377603"),
    ("371204_373203", "373404_375403"),
    # frozen-source byte length (W164 prereg = 19071 bytes at f7d34e5a7)
    ("assert len(raw) == 19021", "assert len(raw) == 19071"),
]

# ---------------------------------------------------------------- P1
def _dot(m):
    v = int(m.group(0).replace("_", "")) + 2200
    return f"{v // 1000}_{v % 1000:03d}"


def _com(m):
    v = int(m.group(0).replace(",", ""))
    return f"{v + 2200:,}" if v >= 300000 else m.group(0)


def _bare(m):
    v = int(m.group(0))
    return str(v + 2200) if v >= 300000 else m.group(0)


def pass_values(s):
    # lookaround boundaries (not \b): K356,520 / se_mu_at_k356520 /
    # line_merged_356520 carry letter/underscore prefixes that kill \b;
    # (?<![\d,]) keeps 8+-digit runs (seeds/timestamps) and 3,3-substrings
    # of longer comma forms unsplit; the >=300000 gate protects float
    # fragments (0.0004xx / 0.088xxx / 0.245xxx / 0.2505xx all below it).
    # r794 takeover fix: trailing guard was (?![\d,]) which KILLED tuple
    # first-elements and list-comma forms (375_604, / 764,012, -> never
    # advanced -> mixed-era tuples + freeze_edits 764,012 residue). New
    # trailing guard (?!(?:\d|,\d)) only rejects digit continuation and
    # 3,3-substrings of longer comma forms (6,772,211,712 inner parts),
    # letting comma-followed values advance uniformly.
    s = re.sub(r"(?<![\d,])3\d{2}_\d{3}(?!(?:\d|,\d))", _dot, s)
    s = re.sub(r"(?<![\d,])\d{3},\d{3}(?!(?:\d|,\d))", _com, s)
    s = re.sub(r"(?<![\d,])\d{6}(?!(?:\d|,\d))", _bare, s)
    return s


# ---------------------------------------------------------------- P2
W_TOK = [
    ("W165", "W166"), ("W164", "W165"), ("W163", "W164"), ("W162", "W163"),
    ("W161", "W162"), ("W160", "W161"), ("W159", "W160"), ("W158", "W159"),
    ("W157", "W158"), ("W156", "W157"), ("W155", "W156"),
    ("w164", "w165"), ("w163", "w164"), ("w162", "w163"),
]

# ---------------------------------------------------------------- P3
R_TOK = [
    ("r792", "r794"), ("r790", "r793"), ("r789", "r792"), ("r788", "r790"),
    ("r787", "r789"),
]

# ---------------------------------------------------------------- P4
P4 = [
    # r794 takeover: bare-16X composites found by scanning the W164 verify
    # source (no other rule covered them; dead session's anchor list
    # expected the advanced forms but lacked the producing rules)
    ("[-1] == 164 and len(pf.N1_BANDS) == 162",
     "[-1] == 165 and len(pf.N1_BANDS) == 163"),
    ("N1_BANDS 162 rows", "N1_BANDS 163 rows"),
    ('"164"', '"165"'), ('"163"', '"164"'),
    ('164: {"batch"', '165: {"batch"'), ('164: {"a": (', '165: {"a": ('),
    ('163: {"batch"', '164: {"batch"'), ("163: {", "164: {"),
    ("--wave 164", "--wave 165"), ("--wave 163", "--wave 164"),
    ("N1_BANDS[164]", "N1_BANDS[165]"), ("N1_BANDS[163]", "N1_BANDS[164]"),
    ("N1_BANDS[162]", "N1_BANDS[163]"),
    ("WAVE_CONFIGS[164]", "WAVE_CONFIGS[165]"),
    ("WAVE_CONFIGS[163]", "WAVE_CONFIGS[164]"),
    ("range(138, 164)", "range(138, 165)"), ("range(138, 163)", "range(138, 164)"),
    ("range(16, 164)", "range(16, 165)"), ("range(16, 163)", "range(16, 164)"),
    ("_set_wave(164)", "_set_wave(165)"), ("_set_wave(163)", "_set_wave(164)"),
    ("波号 164=", "波号 165="), ("波号 163=", "波号 164="),
    ("第 155 波", "第 156 波"), ("第 154 波", "第 155 波"), ("第 153 波", "第 154 波"),
    ("第 164 枚", "第 165 枚"), ("第 163 枚", "第 164 枚"),
    ("第 162 枚", "第 163 枚"), ("第 161 枚", "第 162 枚"),
    ("行 153+本候选", "行 154+本候选"), ("行 152+本候选", "行 153+本候选"),
    ("engine_owner rows 153", "engine_owner rows 154"),
    ("engine_owner rows 152", "engine_owner rows 153"),
    ("engine_owner 行 153", "engine_owner 行 154"),
    ("engine_owner 行 152", "engine_owner 行 153"),
    ("rows 79 + candidate", "rows 80 + candidate"),
    ("rows 78 + candidate", "rows 79 + candidate"),
    ("rows 77 + candidate", "rows 78 + candidate"),
    ("行 79+本候选", "行 80+本候选"), ("行 78+本候选", "行 79+本候选"),
    ("79 行注册", "80 行注册"), ("78 行注册", "79 行注册"),
    ("机证 161 行", "机证 162 行"), ("机证 160 行", "机证 161 行"),
    ('["ordinal"] == 154', '["ordinal"] == 155'),
    ('["bma_ordinal"] == 80', '["bma_ordinal"] == 81'),
    ('"ordinal": 154', '"ordinal": 155'),
    ("154th wave, bm-a 80th", "155th wave, bm-a 81st"),
    ("len(owner_rows) == 154 and len(bma_rows) == 80",
     "len(owner_rows) == 155 and len(bma_rows) == 81"),
    ("len(owner_rows) == 153 and len(bma_rows) == 79",
     "len(owner_rows) == 154 and len(bma_rows) == 80"),
]

# ---------------------------------------------------------------- P5
P5 = [
    ("TWENTY-FIFTH", "TWENTY-SIXTH"), ("TWENTY-FOURTH", "TWENTY-FIFTH"),
    ("TWENTY-THIRD", "TWENTY-FOURTH"), ("TWENTY-SECOND", "TWENTY-THIRD"),
    ("twenty-FIFTH", "twenty-SIXTH"), ("twenty-FOURTH", "twenty-FIFTH"),
    ("twenty-THIRD", "twenty-FOURTH"), ("twenty-SECOND", "twenty-THIRD"),
    ("twenty-fifth", "twenty-sixth"), ("twenty-fourth", "twenty-fifth"),
    ("twenty-third", "twenty-fourth"), ("twenty-second", "twenty-third"),
    ("第二十七例", "第二十八例"), ("第二十六例", "第二十七例"),
    ("第二十五例", "第二十六例"), ("第二十四例", "第二十五例"),
    ("第二十三例", "第二十四例"), ("第二十二例", "第二十三例"),
    ("第八十三枚", "第八十四枚"), ("第八十二枚", "第八十三枚"),
    ("第八十一枚", "第八十二枚"), ("第八十枚", "第八十一枚"),
    ("第七十九枚", "第八十枚"),
    ("一百六十五面", "一百六十六面"), ("一百六十四面", "一百六十五面"),
    ("一百六十三面", "一百六十四面"), ("一百六十二面", "一百六十三面"),
    ("一百六十一面", "一百六十二面"),
    ("一百六十四行", "一百六十五行"), ("一百六十三行", "一百六十四行"),
    ("一百六十二行", "一百六十三行"), ("一百六十一行", "一百六十二行"),
    ("一百六十行", "一百六十一行"),
    ("ONE HUNDRED-AND-FIFTY-FIFTH", "ONE HUNDRED-AND-FIFTY-SIXTH"),
    ("ONE HUNDRED-AND-FIFTY-FOURTH", "ONE HUNDRED-AND-FIFTY-FIFTH"),
    ("ONE HUNDRED-AND-FIFTY-THIRD", "ONE HUNDRED-AND-FIFTY-FOURTH"),
    ("ONE HUNDRED-AND-FIFTY-SECOND", "ONE HUNDRED-AND-FIFTY-THIRD"),
]


def common(s):
    for a, b in P0:
        s = s.replace(a, b)
    s = pass_values(s)
    for a, b in W_TOK:
        s = s.replace(a, b)
    for a, b in R_TOK:
        s = s.replace(a, b)
    for a, b in P4:
        s = s.replace(a, b)
    for a, b in P5:
        s = s.replace(a, b)
    return s


# ================================================================ tool 1
s = read(r"results/_r792bma_w164_face_probe.py")
s = common(s)
# bloodline cites the SOURCE tool (r792/_r792bma_w164) -- protect it from
# the self-reference name advance, then advance remaining self-refs
s = s.replace("_r792bma_w164_face_probe.py", "@BLFILE@")
s = s.replace("_r792bma_w164", "_r794bma_w165")
s = s.replace("@BLFILE@", "_r792bma_w164_face_probe.py")
for needle in ('    # W164 (bm-a r792 freeze', '164: {"a": (375_604',
               '# --- W164 materializer face', '"+ W164 materializer face',
               '"r792 bm-a] "', r"results\_r794bma_w165_probe_pf_block.txt",
               "Bloodline: r792 _r792bma_w164_face_probe.py machinery verbatim."):
    if needle not in s:
        die(f"face_probe anchor missing: {needle!r}")
for bad in ("_r792bma_w164_probe", "W165p", "373_204..375_203", "189157de8",
            "369_004"):
    if bad in s:
        die(f"face_probe residue: {bad!r}")
ast.parse(s)
write(r"results/_r794bma_w165_face_probe.py", s)
print("derived face_probe OK")

# ================================================================ tool 2
s = read(r"results/_r792bma_w164_prereg_build.py")
s = common(s)
s = s.replace("_r792bma_w164", "_r794bma_w165")

# --- P6: live-fact surgicals (post-common needles; ordered, BACK first) ---
SURG = [
    # @SEC@ se_mu chain: needle := prior BACK tail (2-term, chain GROWS,
    # r794 v2 fix: dead session's 3-term needle would have swallowed the
    # W161 term = sliding-window corruption; history chain W141-head grows)
    (r'("W162 0.000413\u2192W163 **0.000412**", "@SEC@")',
     r'("W162 0.000412\u2192W163 **0.000411**", "@SEC@")'),
    (r'("@SEC@", "W162 0.000413\u2192W163 0.000412\u2192W164 **0.000411**")',
     r'("@SEC@", "W162 0.000412\u2192W163 0.000411\u2192W164 **0.000409**")'),
    # @KLC@ current key: needle EXTENDED through line_pre (W163/W164
    # line_pre diverge 1.1829 -> 1.1832; r792 pass-through luck ended)
    (r'("K-lift **\u22120.0001**【line_merged@K356,520 **1.1828**", "@KLC@")',
     r'("K-lift **+0.0002**【line_merged@K356,520 **1.1831**·line_pre 1.1829", "@KLC@")'),
    (r'("@KLC@", "K-lift **+0.0002**【line_merged@K358,720 **1.1831**")',
     r'("@KLC@", "K-lift **+0.0001**【line_merged@K358,720 **1.1833**·line_pre 1.1832")'),
    # @SIGC@ sigma site (4dp W163==W164 coincidence 0.2452; 6dp live)
    (r'("0.2451**=W163 合并池实测 0.245130", "@SIGC@")',
     r'("0.2452**=W163 合并池实测 0.245163", "@SIGC@")'),
    (r'("@SIGC@", "0.2452**=W164 合并池实测 0.245163")',
     r'("@SIGC@", "0.2452**=W164 合并池实测 0.245172")'),
    # @OWMU@ own-mu (BACK first: new \u22120.088982 must not be re-mapped)
    (r'("@OWMU@", "\u22120.088982")', r'("@OWMU@", "\u22120.096332")'),
    (r'("\u22120.095597", "@OWMU@")', r'("\u22120.088982", "@OWMU@")'),
    # @AP95@ A p95
    (r'("@AP95@", "0.3259")', r'("@AP95@", "0.3106")'),
    (r'("0.3093", "@AP95@")', r'("0.3259", "@AP95@")'),
    # machine-facts asserts (live W164 finalize facts, r587)
    ('round(own["mu"], 6) == -0.088982', 'round(own["mu"], 6) == -0.096332'),
    ('m["sigma"] == 0.2451632693353447', 'm["sigma"] == 0.2451720171066556'),
    ('own["sigma"] == 0.250561227901671', 'own["sigma"] == 0.24661726077929613'),
    ('full_sharpe_p95"] == 0.3259', 'full_sharpe_p95"] == 0.3106'),
    ('line_merged_358720"] == 1.1831', 'line_merged_358720"] == 1.1833'),
    ('line_pre_w164"] == 1.1829', 'line_pre_w164"] == 1.1832'),
    ('line_delta_k_lift"] == 0.0002', 'line_delta_k_lift"] == 0.0001'),
    ('se_mu_at_k358720"] == 0.000411', 'se_mu_at_k358720"] == 0.000409'),
    # output-checks float entries
    (r'("\u22120.088982", 1)', r'("\u22120.096332", 1)'),
    (r'("\u22120.095597", 0)', r'("\u22120.088982", 0)'),
    ('("0.3259", 1)', '("0.3106", 1)'),
    ('("0.3093", 0)', '("0.3259", 0)'),
    ('("0.245163", 1)', '("0.245172", 1)'),
    ('("0.245130", 0)', '("0.245163", 0)'),
    ('("1.1831", 1)', '("1.1833", 1)'),
    ('("1.1828", 0)', '("1.1831", 0)'),
]
for needle, repl in SURG:
    if needle not in s:
        die(f"prereg_build surgical needle missing: {needle[:70]!r}")
    s = s.replace(needle, repl)

# --- EXPECT empirical rebuild from the frozen W164 prereg source ----------
raw_src = subprocess.run(
    ["git", "show", "f7d34e5a7:research/PERPETUAL_N1_W164_PREREG.md"],
    capture_output=True).stdout
if len(raw_src) != 19071:
    die(f"frozen W164 prereg bytes {len(raw_src)} != 19071")
src_txt = raw_src.decode("utf-8")
m = re.search(r"EXPECT = \{.*?\n\}", s, re.S)
if not m:
    die("EXPECT block not found")
pairs = re.findall(r'"([^"]+)": (\d+)', m.group(0))
rebuilt = ["EXPECT = {  # exact per-token source counts (empirically rebuilt)"]
zeros = []
for k, _old in pairs:
    cnt = src_txt.count(k)
    if cnt == 0:
        zeros.append(k)
    rebuilt.append(f'    "{k}": {cnt},')
rebuilt.append("}")
if zeros:
    die(f"EXPECT zero-count needles (derivation drift): {zeros}")
s = s[:m.start()] + "\n".join(rebuilt) + s[m.end():]

for needle in (r'("W162 0.000412\u2192W163 **0.000411**", "@SEC@")',
               r'("@SEC@", "W162 0.000412\u2192W163 0.000411\u2192W164 **0.000409**")',
               r'("K-lift **+0.0002**【line_merged@K356,520 **1.1831**·line_pre 1.1829", "@KLC@")',
               r'("@KLC@", "K-lift **+0.0001**【line_merged@K358,720 **1.1833**·line_pre 1.1832")',
               'f7d34e5a7:research/PERPETUAL_N1_W164_PREREG.md',
               'n1_w164_results.json',
               'PERPETUAL_N1_W165_PREREG.md'):
    if needle not in s:
        die(f"prereg_build anchor missing: {needle[:70]!r}")
for bad in ("_r792bma_w164_probe", "189157de8", "764cd882a",
            "0.245130", "0.250561227901671", "-0.088982", "0.000411\")",
            "373_404..375_403"):
    if bad in s:
        die(f"prereg_build residue: {bad!r}")
ast.parse(s)
write(r"results/_r794bma_w165_prereg_build.py", s)
print("derived prereg_build OK (EXPECT rebuilt empirically, zero-counts CLEAN)")

# ================================================================ tool 3
s = read(r"results/_r792bma_w164_freeze_edits.py")
s = common(s)
# bloodline protection (same law as tool 1), then self-ref name advance
s = s.replace("_r792bma_w164_freeze_edits.py", "@BLFILE@")
s = s.replace("_r792bma_w164", "_r794bma_w165")
s = s.replace("@BLFILE@", "_r792bma_w164_freeze_edits.py")
s = s.replace("bm-a r792 freeze, seat", "bm-a r794 freeze, seat")
for needle in ('    # W164 (bm-a r792 freeze', "'164: {\"a\": (375_604",
               '164: {"batch"', '# --- W164 materializer face',
               '"+ W164 materializer face', '"r792 bm-a] "',
               r"results\_r794bma_w165_probe_pf_block.txt",
               "N1_BANDS[164]", "range(138, 164)",
               'assert W166p_A == "379_804..381_803"',
               "bm-a r792 freeze f7d34e5a7",
               "f7d34e5a7, SINGLE STATE zero seat gap W2..W164 all",
               'Bloodline: r792 _r792bma_w164_freeze_edits.py machinery'):
    if needle not in s:
        die(f"freeze_edits anchor missing: {needle!r}")
for bad in ("_r792bma_w164_probe", "189157de8", "764cd882a",
            "373_404..375_403", "ledger head 764,012",
            "chain head 764,012", "TWENTY-THIRD instance"):
    if bad in s:
        die(f"freeze_edits residue: {bad!r}")
# bare 764,012 is NOT a residue in the derived W165 tool: it legitimately
# appears as (a) the BACK vmap entry ('764,012', "@LEDG@") = the old W164
# ledger head the W165 prereg derivation replaces, and (b) the stale-values
# list entry (source 761,812 advanced +2,200) = old faces the new prereg
# must NOT carry. True misses are only the advanceable prose/assert sites
# (ledger head / chain head), guarded above. Pins below catch the opposite
# failure mode (over-advance of the legit faces).
for pin in ("('764,012', \"@LEDG@\")",
            '"377_403", "764,012", "356,520"'):
    if pin not in s:
        die(f"freeze_edits legit-764,012 pin missing: {pin!r}")
ast.parse(s)
write(r"results/_r794bma_w165_freeze_edits.py", s)
print("derived freeze_edits OK")

# ================================================================ tool 4
s = read(r"results/_r792bma_w164_freeze_verify.py")
s = common(s)
s = s.replace("_r792bma_w164", "_r794bma_w165")
s = s.replace("bm-a r792 freeze, seat", "bm-a r794 freeze, seat")
for needle in ('assert sorted(pf.N1_BANDS)[-1] == 165',
               'N1_BANDS[165] == {"a": (377_804, 379_803)',
               'N1_BANDS[164] == {"a": (375_604, 377_603)',
               'N1_BANDS[163] == {"a": (373_404, 375_403)',
               'range(138, 165)', '_set_wave(165)',
               'W166p_A, W166p_B = "379_804..381_803", "380_004..380_203"',
               'leg3["W166p_A"] == "379804..381803"',
               '"r794 bm-a] "', '155th wave, bm-a 81st',
               '"f7d34e5a7, SINGLE STATE zero seat gap W2..W164 all "',
               '"number law after the REGISTERED W164 row bm-a r792 freeze "',
               'MSG-2026-10-06-205x-bma-w165-seat.md'):
    if needle not in s:
        die(f"freeze_verify anchor missing: {needle!r}")
for bad in ("_r792bma_w164_probe", "189157de8", "W165p_A, W165p_B",
            "chain head 764,012", '"764,012" in n2',
            "373_404..375_403"):
    if bad in s:
        die(f"freeze_verify residue: {bad!r}")
# same law as freeze_edits: bare 764,012 in the stale-values list is the
# legit advanced face (source 761,812+2,200); pin it to catch over-advance
if '"377_403", "764,012", "356,520"' not in s:
    die('freeze_verify legit-764,012 pin missing')
ast.parse(s)
write(r"results/_r794bma_w165_freeze_verify.py", s)
print("derived freeze_verify OK")
print("r794 bm-a W165 deriv v2: ALL FOUR TOOLS DERIVED + AST PASS")
