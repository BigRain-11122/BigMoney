# -*- coding: utf-8 -*-
"""r794 bm-a W165 freeze toolset deriver: token-advance the r792 W164 four-tool
bloodline (face_probe / prereg_build / freeze_edits / freeze_verify) into the
W165 freeze window.

Laws: r631 ordered single-pass advance; r632 count-reconcile; r637 value
anchors belong to the run window; r587 live-derived; r773 composite-first
(band strings whole, bare numerals LAST, DESCENDING wave/session order);
r776 fragment-needle. Non-uniform faces (growing chains, per-wave stats,
role-split sessions) get surgical composites; everything else is a pure
+1-wave shift. EXPECT counts are rebuilt EMPIRICALLY from the frozen W164
prereg (zero hand-transcription).
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


# ---- phase 0: receipts + role-protected composites (before every bare pass)
PH0 = [
    ("_r792bma_w164_band_gate.json", "_r793bma_w165_band_gate.json"),
    ("_r792bma_w164_probe_receipt.json", "_r793bma_w165_probe_receipt.json"),
    ("r792 pre-seat", "r793 pre-seat"),          # W165 seat pushed by r793
    ("gate-derived r792", "gate-derived r793"),  # W165 gate ran at r793
    ("r792 gate leg3", "r793 gate leg3"),
    ("the r792 gate + probe receipts", "the r793 gate + probe receipts"),
    ("469d40896", "4bdf63090"),                  # W164 seat sha -> W165 seat sha
    ("MSG-2026-10-06-194x", "MSG-2026-10-06-205x"),
    ("seat MSG-194x tail", "seat MSG-205x tail"),
]

# ---- phase 1: wave tokens, DESCENDING (next-wave refs W165->W166 first)
PH1 = [
    ("W165", "W166"), ("W164", "W165"), ("W163", "W164"), ("W162", "W163"),
    ("W161", "W162"), ("W160", "W161"), ("W159", "W160"), ("W158", "W159"),
    ("W157", "W158"), ("W156", "W157"), ("W155", "W156"),
    ("w164", "w165"), ("w163", "w164"), ("w162", "w163"),
]

# ---- phase 2: session tokens, DESCENDING (r785/r786 sentinels stay)
PH2 = [
    ("r792", "r794"), ("r790", "r793"), ("r789", "r792"),
    ("r788", "r790"), ("r787", "r789"),
]

# ---- phase 3: numeric/value anchors -- composites first, singles DESCENDING
PH3 = [
    # jump phrases (physical single-line fragments)
    ("jumps to 375_404, first-clean 375_404..375_603 hops=1",
     "jumps to 377_604, first-clean 377_604..377_803 hops=1"),
    ("jumps to 375_404 -> 375_404..375_603,",
     "jumps to 377_604 -> 377_604..377_803,"),
    ("375_404 and lands 375_404..375_603", "377_604 and lands 377_604..377_803"),
    ("own-wave A window reserved jumps to 375_404, first-clean ",
     "own-wave A window reserved jumps to 377_604, first-clean "),
    # assert composites
    ("== 373_404 == 373_403 + 1", "== 375_604 == 375_603 + 1"),
    ("== 375_404 == 375_403 + 1", "== 377_604 == 377_603 + 1"),
    ("set(range(373_404, 375_404))", "set(range(375_604, 377_604))"),
    ("set(range(375_404, 375_604))", "set(range(377_604, 377_804))"),
    # projection literals (W165p values -> W166p values) BEFORE needle advance
    ("377_604..379_603", "379_804..381_803"),
    ("377_804..378_003", "380_004..380_203"),
    # dotted windows (needle advance)
    ("375_404..377_403", "377_604..379_603"),
    ("375_604..375_803", "377_804..378_003"),
    ("375_604..377_603", "377_804..379_803"),
    ("375_404..375_603", "377_604..377_803"),
    ("373_404..375_403", "375_604..377_603"),
    ("373_404..373_603", "375_604..375_803"),
    ("373_204..375_203", "375_404..377_403"),
    ("373_204..373_403", "375_404..375_603"),
    # seed-base composites
    ("373_404+j", "375_604+j"),
    ("375_404+j", "377_604+j"),
    # base relations
    ("373_403+1", "375_603+1"),
    ("375_403+1", "377_603+1"),
    # registration shas, DESCENDING (W163 reg -> W164 reg is the new cite)
    ("18231a529", "f7d34e5a7"),
    ("189157de8", "469d40896"),
    ("764cd882a", "18231a529"),
    # seat MSG needle advance (BACK side already done in PH0)
    ("MSG-2026-10-06-183x", "MSG-2026-10-06-194x"),
    ("seat MSG-183x tail", "seat MSG-194x tail"),
    # ledger / K dotted
    ("766,212", "768,412"),
    ("764,012", "766,212"),
    ("761,812", "764,012"),
    ("n_eff 759,612", "n_eff 761,812"),
    ("358,720", "360,920"),
    ("356,520", "358,720"),
    ("354,320", "356,520"),
    # exact float stats (W163 finalize -> W164 finalize)
    ("0.2451632693353447", "0.2451720171066556"),
    ("0.250561227901671", "0.24661726077929613"),
    ("0.245163", "0.245172"),
    ("0.245130", "0.245163"),
    ("\\u22120.088982", "\\u22120.096332"),
    ("\\u22120.095597", "\\u22120.088982"),
    ("-0.088982", "-0.096332"),
    ("0.3259", "0.3106"),
    ("0.3093", "0.3259"),
    # skill-line values (machine facts + prose)
    ("1.1831", "1.1833"),
    ("1.1829", "1.1832"),
    ("1.1828", "1.1829"),
    # ordinals EN, DESCENDING
    ("TWENTY-THIRD", "TWENTY-FOURTH"),
    ("TWENTY-SECOND", "TWENTY-THIRD"),
    ("twenty-third", "twenty-fourth"),
    ("twenty-second", "twenty-third"),
    ("twenty-THIRD", "twenty-FOURTH"),
    ("twenty-SECOND", "twenty-THIRD"),
    ("ONE HUNDRED-AND-FIFTY-FOURTH", "ONE HUNDRED-AND-FIFTY-FIFTH"),
    ("ONE HUNDRED-AND-FIFTY-THIRD", "ONE HUNDRED-AND-FIFTY-FOURTH"),
    ("ONE HUNDRED-AND-FIFTY-SECOND", "ONE HUNDRED-AND-FIFTY-THIRD"),
    ("eighty-first", "eighty-second"),
    ("eightieth", "eighty-first"),
    ("seventy-ninth", "eightieth"),
    ("seventy-eighth", "seventy-ninth"),
    ("seventy-seventh", "seventy-eighth"),
    # ordinals ZH, DESCENDING
    ("第二十五例", "第二十六例"),
    ("第二十四例", "第二十五例"),
    ("第二十三例", "第二十四例"),
    ("第二十二例", "第二十三例"),
    ("第八十一枚", "第八十二枚"),
    ("第八十枚", "第八十一枚"),
    ("第七十九枚", "第八十枚"),
    ("一百六十三面", "一百六十四面"),
    ("一百六十二面", "一百六十三面"),
    ("一百六十一面", "一百六十二面"),
    ("一百六十二行", "一百六十三行"),
    ("一百六十一行", "一百六十二行"),
    ("一百六十行", "一百六十一行"),
    ("第 163 枚", "第 164 枚"),
    ("第 162 枚", "第 163 枚"),
    ("第 161 枚", "第 162 枚"),
    ("第 155 波", "第 156 波"),
    ("第 154 波", "第 155 波"),
    ("第 153 波", "第 154 波"),
    ("161 行）", "162 行）"),
    ("160 行）", "161 行）"),
    ("波号 164=", "波号 165="),
    ("波号 163=", "波号 164="),
    # row-count / ordinal composites, DESCENDING
    ("rows 79 + candidate", "rows 80 + candidate"),
    ("rows 78 + candidate", "rows 79 + candidate"),
    ("rows 77 + candidate", "rows 78 + candidate"),
    ("engine_owner rows 153", "engine_owner rows 154"),
    ("engine_owner rows 152", "engine_owner rows 153"),
    ("engine_owner 行 153", "engine_owner 行 154"),
    ("engine_owner 行 152", "engine_owner 行 153"),
    ("行 79+本候选", "行 80+本候选"),
    ("行 78+本候选", "行 79+本候选"),
    ("79 行注册", "80 行注册"),
    ("78 行注册", "79 行注册"),
    ("range(138, 164)", "range(138, 165)"),
    ("range(138, 163)", "range(138, 164)"),
    ("range(16, 164)", "range(16, 165)"),
    ("range(16, 163)", "range(16, 164)"),
    ("N1_BANDS[164]", "N1_BANDS[165]"),
    ("N1_BANDS[163]", "N1_BANDS[164]"),
    ("N1_BANDS[162]", "N1_BANDS[163]"),
    ("WAVE_CONFIGS[164]", "WAVE_CONFIGS[165]"),
    ("--wave 164", "--wave 165"),
    ("--wave 163", "--wave 164"),
    ("_set_wave(164)", "_set_wave(165)"),
    ("[-1] == 164 and len(pf.N1_BANDS) == 162",
     "[-1] == 165 and len(pf.N1_BANDS) == 163"),
    ("len(pf.N1_BANDS) == 162", "len(pf.N1_BANDS) == 163"),
    ('["ordinal"] == 154', '["ordinal"] == 155'),
    ('["bma_ordinal"] == 80', '["bma_ordinal"] == 81'),
    ("154th wave, bm-a 80th", "155th wave, bm-a 81st"),
    # row-key prefixes: BACK/new-face carriers FIRST (specific forms), then
    # the needle/sentinel advance (bare '163: {' last -- no bare '164: {'
    # rule: it would double-map the just-created needle forms)
    ('164: {"batch"', '165: {"batch"'),
    ('164: {"a": (', '165: {"a": ('),
    ('163: {"batch"', '164: {"batch"'),
    ("163: {", "164: {"),
    # single dotted values, DESCENDING
    ("379_603", "381_803"),
    ("378_003", "380_203"),
    ("377_804", "380_004"),
    ("377_803", "380_003"),
    ("377_604", "379_804"),
    ("377_603", "379_803"),
    ("377_403", "379_603"),
    ("375_803", "378_003"),
    ("375_604", "377_804"),
    ("375_603", "377_803"),
    ("375_404", "377_604"),
    ("375_203", "377_403"),
    ("373_603", "375_803"),
    ("373_404", "375_604"),
    ("373_403", "375_603"),
    ("373_204", "375_404"),
    ("373_203", "375_403"),
    ("371_204", "373_404"),
    # undotted, DESCENDING
    ("360920", "363120"),
    ("358720", "360920"),
    ("356520", "358720"),
    ("354320", "356520"),
    ("768412", "770612"),
    ("766212", "768412"),
    ("764012", "766212"),
    ("761812", "764012"),
    ("375604_377603", "377804_379803"),
    ("377604_377803", "379804_380003"),
    ("377604..379603", "379804..381803"),
    ("377804..378003", "380004..380203"),
    ("375604, 377603", "377804, 379803"),
    ("377604, 377803", "379804, 380003"),
    ("375404, 377403", "377604, 379603"),
    ("375604, 375803", "377804, 378003"),
    ("373404, 375403", "375604, 377603"),
    ("375404, 375603", "377604, 377803"),
    ("371204, 373203", "373404, 375403"),
    ("373204, 373403", "375404, 375603"),
    ("375604", "377804"),
    ("377603", "379803"),
    ("377604", "379804"),
    ("377803", "380003"),
    ("375404", "377604"),
    ("377403", "379603"),
    ("373404", "375604"),
    ("375403", "377603"),
    ("375603", "377803"),
]


def generic(s):
    for a, b in PH0:
        s = s.replace(a, b)
    for a, b in PH1:
        s = s.replace(a, b)
    for a, b in PH2:
        s = s.replace(a, b)
    for a, b in PH3:
        s = s.replace(a, b)
    return s


# ---- shared non-uniform surgical composites (post-generic) ------------------
SURG = [
    # se_mu machine fact: W164 se_mu = 0.000409 (NOT a shift of 0.000411)
    ('["se_mu_at_k358720"] == 0.000411', '["se_mu_at_k358720"] == 0.000409'),
    # K-lift delta machine fact: W164 delta = 0.0001
    ('["line_delta_k_lift"] == 0.0002', '["line_delta_k_lift"] == 0.0001'),
    # @KLC@ prose BACK delta (W164 K-lift +0.0001)
    ('+0.0002**【line_merged@K358,720 **1.1833**',
     '+0.0001**【line_merged@K358,720 **1.1833**'),
    # @KLC@ prose needle := old BACK verbatim (W164 prereg's K-lift face)
    ('K-lift **\\u22120.0001**【line_merged@K356,520 **1.1829**',
     'K-lift **+0.0002**【line_merged@K356,520 **1.1831**'),
    # bare-digit tuple faces (prereg_build @BARE@; freeze_edits @IDX@/@IDX2@)
    ("'163', \"@BARE@\"", "'164', \"@BARE@\""),
    ("\"@BARE@\", \"164\"", "\"@BARE@\", \"165\""),
    ("'163', \"@IDX@\"", "'164', \"@IDX@\""),
    ("\"@IDX@\", \"164\"", "\"@IDX@\", \"165\""),
    ("'162', \"@IDX2@\"", "'163', \"@IDX2@\""),
    ("\"@IDX2@\", \"163\"", "\"@IDX2@\", \"164\""),
    # print/prose faces with bare numerals
    ("N1_BANDS 162 rows tail", "N1_BANDS 163 rows tail"),
    ("chain 138..163 n=26", "chain 138..164 n=27"),
    # face_probe inventory bare-digit advance (needle-list tail fragment)
    ('"W164", "W163", "163", "162",', '"W164", "W163", "164", "163",'),
]


def apply_surg(s):
    for a, b in SURG:
        s = s.replace(a, b)
    return s


# =========================================================================
# tool 1: face_probe
# =========================================================================
s = read(r"results/_r792bma_w164_face_probe.py")
s = generic(s)
s = apply_surg(s)
s = s.replace("_r792bma_w164_face_probe.py", "@BLFILE@")
s = s.replace("_r792bma_w164", "_r794bma_w165")
s = s.replace("@BLFILE@", "_r792bma_w164_face_probe.py")
for needle in ('    # W164 (bm-a r792 freeze', '164: {"a": (375_604',
               '# --- W164 materializer face', '"+ W164 materializer face',
               '"r792 bm-a] "', r"results\_r794bma_w165_probe_pf_block.txt",
               'Bloodline: r792 _r792bma_w164_face_probe.py machinery verbatim.'):
    assert needle in s, f"face_probe anchor missing: {needle!r}"
for bad in ("_r792bma_w164_probe", "W165p", "373_204..375_203", "189157de8"):
    assert bad not in s, f"face_probe residue: {bad!r}"
ast.parse(s)
write(r"results/_r794bma_w165_face_probe.py", s)
print("derived face_probe OK")

# =========================================================================
# tool 2: prereg_build
# =========================================================================
s = read(r"results/_r792bma_w164_prereg_build.py")
s = generic(s)
s = apply_surg(s)
# frozen source commit + byte length
s = s.replace("18231a529:research/PERPETUAL_N1_W164_PREREG.md",
              "f7d34e5a7:research/PERPETUAL_N1_W164_PREREG.md")
s = s.replace("git show 18231a529:research/PERPETUAL_N1_W165_PREREG.md",
              "git show f7d34e5a7:research/PERPETUAL_N1_W164_PREREG.md")
s = s.replace("assert len(raw) == 19021", "assert len(raw) == 19071")
# source-read variable family: w164 (results json of the PRIOR finalize)
s = s.replace('w165 = json.load(open("results/perpetual_faces/n1_w165_results.json"',
              'w164 = json.load(open("results/perpetual_faces/n1_w164_results.json"')
s = s.replace('w164 = json.load(open("results/perpetual_faces/n1_w165_results.json"',
              'w164 = json.load(open("results/perpetual_faces/n1_w164_results.json"')
s = re.sub(r"\bw165\[", "w164[", s)
s = s.replace('"w165_only"', '"w164_only"')
s = s.replace('"line_pre_w165"', '"line_pre_w164"')
# --- growing-chain surgicals ------------------------------------------------
# @SEC@: needle := old BACK (3-term chain); BACK := drop-oldest + W164 value
s = s.replace(
    '("W162 0.000413\\u2192W163 **0.000412**", "@SEC@")',
    '("W161 0.000413\\u2192W162 0.000412\\u2192W163 **0.000411**", "@SEC@")')
s = s.replace(
    '("@SEC@", "W162 0.000413\\u2192W163 0.000412\\u2192W164 **0.000411**")',
    '("@SEC@", "W162 0.000412\\u2192W163 0.000411\\u2192W164 **0.000409**")')
# @TAIL@: needle := old BACK verbatim (2-row tail, historical sessions
# r787/r789 intact); BACK already uniform-grown by the generic pass
s = s.replace(
    '("W163=bm-a r789 freeze（18231a529·表尾）；**均已注册**（表尾 W163 行）",\n     "@TAIL@")',
    '("W162=bm-a r787 freeze（764cd882a）；W163=bm-a r789 freeze（18231a529·表尾）；**均已注册**（表尾 W163 行）",\n     "@TAIL@")')
# W155L special-case list already uniform-advanced by PH1
# --- EXPECT empirical rebuild ----------------------------------------------
raw_src = subprocess.run(
    ["git", "show", "f7d34e5a7:research/PERPETUAL_N1_W164_PREREG.md"],
    capture_output=True).stdout
assert len(raw_src) == 19071, f"frozen source bytes {len(raw_src)} != 19071"
src_txt = raw_src.decode("utf-8")
m = re.search(r"EXPECT = \{.*?\n\}", s, re.S)
assert m, "EXPECT block not found"
pairs = re.findall(r'"([^"]+)": (\d+)', m.group(0))
rebuilt = ["EXPECT = {  # exact per-token source counts (empirically rebuilt)"]
for k, _old in pairs:
    if k == "163":          # @BARE@ needle advanced by SURG; key follows
        k = "164"
    cnt = src_txt.count(k)
    rebuilt.append(f'    "{k}": {cnt},')
rebuilt.append("}")
s = s[:m.start()] + "\n".join(rebuilt) + s[m.end():]
m2 = re.search(r"EXPECT = \{(.*?)\}", s, re.S)
zeros = [k for k, _ in re.findall(r'"([^"]+)": (0)[,}]', m2.group(1))]
for z in zeros:
    assert z in ("r788", "r787"), f"unexpected zero-count EXPECT needle: {z!r}"
# key structural anchors
for needle in ('("W161 0.000413\\u2192W162 0.000412\\u2192W163 **0.000411**", "@SEC@")',
               '("@SEC@", "W162 0.000412\\u2192W163 0.000411\\u2192W164 **0.000409**")',
               '("@TAIL@", "W163=bm-a r789 freeze（18231a529）；W164=bm-a r792 freeze（f7d34e5a7·表尾）；**均已注册**（表尾 W164 行）")',
               'git show f7d34e5a7:research/PERPETUAL_N1_W164_PREREG.md',
               'n1_w164_results.json',
               '"K-lift **+0.0002**【line_merged@K356,520 **1.1831**"'):
    assert needle in s, f"prereg_build anchor missing: {needle!r}"
ast.parse(s)
write(r"results/_r794bma_w165_prereg_build.py", s)
print("derived prereg_build OK (EXPECT rebuilt empirically)")

# =========================================================================
# tool 3: freeze_edits
# =========================================================================
s = read(r"results/_r792bma_w164_freeze_edits.py")
s = generic(s)
s = apply_surg(s)
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
    assert needle in s, f"freeze_edits anchor missing: {needle!r}"
for bad in ("_r792bma_w164_probe", "189157de8", "18231a529",
            "373_404..375_403", "764,012", "TWENTY-THIRD instance"):
    assert bad not in s, f"freeze_edits residue: {bad!r}"
ast.parse(s)
write(r"results/_r794bma_w165_freeze_edits.py", s)
print("derived freeze_edits OK")

# =========================================================================
# tool 4: freeze_verify
# =========================================================================
s = read(r"results/_r792bma_w164_freeze_verify.py")
s = generic(s)
s = apply_surg(s)
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
               '"number law after the REGISTERED W164 row bm-a r792 freeze "'):
    assert needle in s, f"freeze_verify anchor missing: {needle!r}"
for bad in ("_r792bma_w164_probe", "189157de8", "W165p_A, W165p_B",
            "764,012", "373_404..375_403"):
    assert bad not in s, f"freeze_verify residue: {bad!r}"
ast.parse(s)
write(r"results/_r794bma_w165_freeze_verify.py", s)
print("derived freeze_verify OK")
print("r794 bm-a W165 deriv: ALL FOUR TOOLS DERIVED + AST PASS")
