# -*- coding: utf-8 -*-
# r963 bm-c editor census for the W230 derive (_w229 -> _w230 freeze editor).
# Counts every planned SHIFT old-side token in the committed template
# results/_w229bmc_freeze_edits.py (48,884 chars) -- counts in hand before the
# editor is authored (r961 census precedent).
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "_w229bmc_freeze_edits.py")
t = open(BASE, "r", encoding="utf-8", newline="").read()
assert len(t) == 48884, f"template length drift: {len(t)} != 48884"

# planned W230 SHIFTS (aged from the W229 editor's new sides), order preserved
TOK = [
 "n1_w229", "w229_", "n1w229", "W229", "W228", "w228_",
 "m226", "N1_BANDS\\[226\\]", "_c228", "arith_a229", "arith_b229", "n3r1_used229",
 "_set_wave(229)", "'228: {\"batch\"'", "'228: {\"a\"'", "'    228: {\"a\"'",
 "f'{CFG_I}229: ", "f'{ROW_I}229: ", "f'229: {{\"a\":", "ROW_I + '229: {\"a\"'",
 "N1_BANDS.get(228)", "WAVE_CONFIGS[229]", "WAVE_CONFIGS[228]", "pf.N1_BANDS[228]",
 "wave 229 = first free number", "wave 229: ", "if w < 229)", "if w < 228",
 "w<228 leaked", "w<229 count", "range(16, 229)", "range(17, 229)",
 "registered wave below 229 composes", "seat MSG-1229 tail", '"wave": 229,',
 "NINETIETH instance anticipated", "EIGHTY-NINTH instance",
 "TWO HUNDRED AND TWENTY-NINTH", "fifty-ninth", "59th", "bmc_ordinal=59",
 "rows 58 + candidate", "rows 218 + candidate",
 "== 218 and len(bmc_rows_live) == 58", "expect 218/58",
 "precedent 217/57 pre-splice", "splice 218/58",
 "r959 probe leg0", "r959 seat-time live face", "probe receipt @ r959 window",
 "r961 freeze window", "r961 freeze-window bundle", "r960 prereg derived",
 "eighteenth consecutive", "e485a0b3f", "THIRTEEN-level",
 "MSG-20261013-0855-bmc", "MSG-20261013-0720-bmc", "c9e9e83b8",
 "_w229bmc_20261013_probe_receipt.json", "_w229bmc_freeze_receipt.json",
 "(518_604, 520_603)", "(520_604, 520_803)", "925_389", "499_520",
 "(expect 925,389 / 499,520)", "842f817ad", "r959 08:3x",
 "W230+ projection", "naive W230 A window", "W230 freezer", "W230+ freezer",
 "downstream W230 seat NOT yet published", "downstream W230 seat publication pending",
 "W227/W226/W225/W224 finalize are transitive deps",
]
cal = {s: t.count(s) for s in TOK}
print(json.dumps(cal, indent=0, ensure_ascii=False))
open(os.path.join(HERE, "_r963bmc_editor_census.json"), "w", encoding="utf-8").write(json.dumps(cal, indent=1, ensure_ascii=False))

# sentinel-block faces (phase-0 protect-restore regions + phase-3 additions)
SENT = [
 ("KEPT tail line (W228 materializer kept-assert)", t.count("    # --- W228 materializer face")),
 ("LIVE w228_block_kept", t.count('"w228_block_kept": 1}')),
 ("LEG227 block", t.count("w227_leg = [")),
 ("ASM w228_leg join", t.count("EOL.join(w228_leg)")),
 ("leg defs w226_leg/w227_leg/w228_leg", (t.count("w226_leg = ["), t.count("w227_leg = ["), t.count("w228_leg = ["))),
]
for k, v in SENT:
    print("SENT", k, "=", v)
