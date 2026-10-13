# -*- coding: utf-8 -*-
# r961 bm-c census: token counts in the committed _w228bmc_freeze_edits.py (the W229
# derive editor template), with the 4 sentinel regions (KEPT/LIVE/LEG227/ASM) extracted
# first exactly as the derive editor will do. Census evidence for count-asserted pairs.
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(HERE, "_w228bmc_freeze_edits.py"), "r", encoding="utf-8", newline="").read()
print("TEMPLATE_CHARS", len(t))

KEPT = t[t.find("assert n1_t4.count('    # --- W209 materializer face')"):]
KEPT = KEPT[:KEPT.find('assert n1_t4.count(''    # --- W227 materializer face'') == 1')]
# sentinel regions verbatim (the derive editor replaces each with @@X@@ BEFORE shifts)
KEPT_ORIG = t[t.find("assert n1_t4.count('    # --- W209 materializer face') == 1"):]
KEPT_ORIG = KEPT_ORIG[:KEPT_ORIG.find("\n", KEPT_ORIG.find("W227 materializer face') == 1  # prior block kept (W227 splice landed r956 dead window, estate absorbed by r956-absorb 1e5ed3326)")) + 1]
LIVE_ORIG = t[t.find('  "liveness_anchors"'):]
LIVE_ORIG = LIVE_ORIG[:LIVE_ORIG.find("\n", LIVE_ORIG.find('"w227_block_kept": 1},')) + 1]
LEG227_ORIG = t[t.find("w227_leg = ["):]
LEG227_ORIG = LEG227_ORIG[:LEG227_ORIG.find("]\n", LEG227_ORIG.find("registered W227 row parity drift")) + 2]
ASM_ORIG = "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w225_leg) + EOL + EOL.join(w226_leg) + EOL + EOL.join(w227_leg) + EOL + EOL.join(tail) + EOL"

s = t
for name, reg in (("KEPT", KEPT_ORIG), ("LIVE", LIVE_ORIG), ("LEG227", LEG227_ORIG), ("ASM", ASM_ORIG)):
    c = s.count(reg)
    print(f"SENTINEL_{name}_COUNT {c}")
    assert c == 1, f"sentinel {name} count {c} != 1"
    s = s.replace(reg, f"@@{name}@@")

TOK = [
 "n1_w228", "w228_", "n1w228", "W228", "W227", "w227_", "m225", "N1_BANDS\\[225\\]",
 "_c227", "arith_a228", "arith_b228", "n3r1_used228", "_set_wave(228)",
 "'227: {\"batch\"'", "'227: {\"a\"'", "'    227: {\"a\"'", "f'{CFG_I}228: ", "f'{ROW_I}228: ",
 "f'228: {{\"a\":", "ROW_I + '228: {\"a\"'", "N1_BANDS.get(227)", "WAVE_CONFIGS[228]",
 "WAVE_CONFIGS[227]", "pf.N1_BANDS[227]", "wave 228 = first free number", "wave 228: ",
 "if w < 228)", "if w < 227", "w<227 leaked", "w<228 count", "range(16, 228)",
 "range(16,228)", "range(17, 228)", "registered wave below 228 composes",
 "seat MSG-1228 tail", '"wave": 228,', "EIGHTY-NINTH instance anticipated",
 "EIGHTY-EIGHTH instance", "TWO HUNDRED AND TWENTY-EIGHTH", "fifty-eighth", "58th",
 "bmc_ordinal=58", "rows 57 + candidate", "rows 217 + candidate",
 "== 217 and len(bmc_rows_live) == 57", "expect 217/57", "precedent 216/56 pre-splice",
 "splice 217/57", "r957 probe leg0", "r957 seat-time live face",
 "probe receipt @ r957 window", "r959 freeze window", "r959 freeze-window bundle",
 "r958 prereg derived", "seventeenth consecutive", "e6c8441aa", "TWELVE-level",
 "MSG-20261013-0720-bmc", "MSG-20261013-0645-bmc", "4e30ddf69",
 "_w228bmc_20261013_probe_receipt.json", "_w228bmc_freeze_receipt.json",
 "(516_404, 518_403)", "(518_404, 518_603)", "923_189", "497_320",
 "(expect 923,189 / 497,320)", "48c321706", "1e5ed3326", "r956 06:5x",
 "W229+ projection", "naive W229 A window", "W229 freezer", "W229+ freezer",
 "downstream W229 seat NOT yet published", "downstream W229 seat publication pending",
 "W226/W225/W224/W223 finalize are transitive deps",
 "w225_leg", "w226_leg", "w227_leg", "w226_out_path", "w227_out_path",
 "n1_w227_results", "n1_w226_results", "n1_w228_results",
 "227: {\"batch\"", "227: {\"a\"", "228: {\"batch\"", "228: {\"a\"",
 "PERPETUAL-N1-W228", "PERPETUAL_N1_W228", "PERPETUAL-N1-W227", "PERPETUAL_N1_W227",
 "W226", "w226_", "W225", "w225_", "W224", "W223", "W222", "r956", "r958", "r959",
 "r957", "EIGHTY-SEVENTH", "EIGHTY-SIXTH", "57th", "216/56", "217/57", "56 + candidate",
 "ordinal machine-read EIGHTY-SEVENTH per probe receipt",
 "W211..W223 legs + W224 leg", "W211..W224 legs", "83-row cut", "the 82-row cut",
 "== 83 \\", "== 85, \\", "!= 85 (69 estate", "!= 84 (69 estate",
 "int(_estate_ws[82]) == 224", "int(_estate_ws[81]) == 223",
 "assert m225, \"upstream W225 row leg not found inside W227 parity span\"",
 "W228 block = 86 rows ending at W227", "86 rows",
 "fifty-eighth owned", "58th own wave", "58th owned", "n1w228-0of12", "n1w228-11of12",
 "PERPETUAL-N1-W228-SHARD-0", "prereg derived+committed in the r958 window",
 "post-W228 registration: bm-c rows 57 + candidate = 58th owned",
 "probe_receipt_bmc_ordinal_face\": 58", "eighteenth", "seventeenth",
 "seventeenth consecutive window", "third consecutive",
 "@@KEPT@@", "@@LIVE@@", "@@LEG227@@", "@@ASM@@",
]
res = {}
for tok in TOK:
    res[tok] = s.count(tok)
print(json.dumps(res, indent=0, ensure_ascii=False))
open("_r961bmc_editor_census.json", "w", encoding="utf-8").write(json.dumps(res, indent=1, ensure_ascii=False))
print("CENSUS OK -> _r961bmc_editor_census.json")
