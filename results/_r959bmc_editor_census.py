# -*- coding: utf-8 -*-
# r959 bm-c editor-derive census: exact token counts in the committed W227 editor template
# (results/_w227bmc_freeze_edits.py) for the W228 derive script's count assertions.
import subprocess, os

HERE = os.path.dirname(os.path.abspath(__file__))
T = open(os.path.join(HERE, "_w227bmc_freeze_edits.py"), "r", encoding="utf-8", newline="").read()
print("template_len:", len(T))

TOKENS = [
 # global shift candidates
 "w227_", "w226_", "W227", "W226", "n1w227", "m224", "_c226", "arith_a227", "arith_b227",
 "n3r1_used227", "_set_wave(227)", "if w < 227)", "if w < 226", "w<226 leaked",
 "range(16, 227)", "range(17, 227)", "registered wave below 227 composes",
 "seat MSG-1227 tail", '"wave": 227,',
 "'226: {\"batch\"'", "'226: {\"a\"'", "'    226: {\"a\"'",
 "f'{CFG_I}227: ", "f'{ROW_I}227: ", "f'227: {{\"a\":", "ROW_I + '227: {\"a\"'",
 "N1_BANDS.get(226)", "WAVE_CONFIGS[226]", "wave 227 = first free number", "wave 227: ",
 "EIGHTY-EIGHTH instance anticipated", "EIGHTY-SEVENTH instance", "TWO HUNDRED AND TWENTY-SEVENTH",
 "fifty-seventh", "57th own wave", "57th owned", "57th EXACT", "bmc_ordinal=57",
 "rows 56 + candidate", "rows 216 + candidate", "== 216 and len(bmc_rows_live) == 56",
 "expect 216/56", "precedent 215/55 pre-splice", "splice 216/56",
 "57th = r955 probe leg0", "r955 seat-time live face", "r955 window",
 "r956 freeze window", "r956 freeze-window bundle", "r956 prereg derived", "r956 window",
 "sixteenth consecutive", "0d0c63c6e", "ELEVEN-level",
 "MSG-20261013-0645-bmc", "MSG-20261013-0645-bmc.md", "MSG-20261012-2040", "10781c2f8",
 "_w227bmc_20261012_probe_receipt.json", "_w227bmc_freeze_receipt.json",
 "(514_204, 516_203)", "(516_204, 516_403)", "920_989", "495_120",
 "(expect 920,989 / 495,120)", "9b44d37d1", "bd50be730", "r943 22:4x", "r945",
 "W228+ projection", "naive W228 A window", "W228 freezer", "W228+ freezer",
 "downstream W228 seat NOT yet published", "downstream W228 seat publication pending",
 "W225/W224/W223/W222", "W226+W225+W224+W223+W222",
 "w224_leg", "w225_leg", "w226_leg", "per-wave prereg +",
 "freeze splice script landed in the r956 freeze-window bundle",
 "probe receipt @ r955 window",
 # estate/parity
 '== 82 \\', '== 84, \\', '!= 84 (69 estate', 'and int(_estate_ws[81]) == 223, \\',
 'and int(_estate_ws[80]) == 222 \\',
 "legs + W223 leg: n=", "full-span 69 rows + W211..W222 legs + W223 leg",
 "(85 rows: estate 69", "the 82-row cut", "+ W224 leg + W225 leg).", "own W224 leg)",
 "upstream W224 row leg not found inside W226 parity span",
 'N1_BANDS\\[224\\]',
 # mirror / post-gate pairs
 'WAVE_CONFIGS[226]["a_seed_base"]', 'WAVE_CONFIGS[226]\\"b_exit_seed_base\\"',
 'WAVE_CONFIGS[226].get', 'pf.N1_BANDS[226]\\"a\\"[0]', 'pf.N1_BANDS[226]\\"b_exit\\"[0]',
 'pf.N1_BANDS[226].get(\\"engine_owner\\")',
 "n1_t4.count(f'assert pf.N1_BANDS[226]",
 "assert pf.N1_BANDS[226] ==",
 # receipt
 '"w226_upstream"', '"w225_transitive"', '"w224_transitive"', '"w223_transitive"', '"w222_transitive"',
 "w222_out_path", '"probe_receipt_bmc_ordinal_face": 57,',
 "legs + W224 leg + W225 leg + W226 leg -> W227 block = 85 rows ending at W226",
 "family-6 gate carried forward", '"w226_block_kept": 1}',
 # misc / naming
 "PERPETUAL-N1-W227", "PERPETUAL_N1_W227", "n1_w227", "n1_w226", "n1_w225_results",
 "n1_w224_results", "n1_w223_results", "n1_w222_results",
 "r957", "r958", "e6c8441aa", "48c321706", "1e5ed3326",
 "results/_w227bmc_20261012_probe_receipt.json",
 "W2..W226 all registered", "W2..W227 all registered",
 "post-W227 registration: bm-c rows 56 + candidate = 57th owned",
 "probe leg0 bmc_ordinal=57 = r955 seat-time",
 "vs the W225 editor", "own splice generation",
 "r812 merged the gate", "deletion-set EMPTY; delivery window = chain-order splice ",
 "seat-time live face 57th disclosed",
]
for tok in TOKENS:
    print(f"{T.count(tok):4d}  {tok!r}")

# pickaxe the W228 prereg add-commit (prose historical sha verification)
r = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--",
                    "research/PERPETUAL_N1_W228_PREREG.md"],
                   capture_output=True, text=True)
print("prereg_add_commit:", (r.stdout.strip().splitlines() or ["n/a"])[0])
r = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--",
                    "results/_w228bmc_20261013_probe_receipt.json"],
                   capture_output=True, text=True)
print("probe_receipt_add_commit:", (r.stdout.strip().splitlines() or ["n/a"])[0])
r = subprocess.run(["git", "log", "--format=%H", "-S", '227: {"a"', "--",
                    "scripts/perpetual_faces.py"], capture_output=True, text=True)
print("w227_freeze_pickaxe:", (r.stdout.strip().splitlines() or ["n/a"])[0][:12])
