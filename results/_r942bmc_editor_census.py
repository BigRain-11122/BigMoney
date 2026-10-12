# -*- coding: utf-8 -*-
# r942 bm-c read-only token census for the W225->W226 freeze-editor derive
# (count-asserted ordered transform preflight; zero writes)
import io, os, sys
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_w225bmc_freeze_edits.py")
t = open(BASE, "r", encoding="utf-8", newline="").read()
toks = [
 "W226", "W225", "W224", "W223", "W222", "W221", "W220",
 "w225_", "w224_", "w223_leg", "w223_out_path", "w222_out_path",
 "w221_out_path", "w220_out_path",
 "WAVE_CONFIGS[225]", "WAVE_CONFIGS[224]", "N1_BANDS[224]", "N1_BANDS[223]",
 "n3r1_used225", "m223", "_c224", "arith_a225", "arith_b225",
 '224: {"batch"', '224: {"a"', '    224: {"a"',
 "n1_w225", "n1w225", "n1_w224_results", "n1_w223_results", "n1_w222_results",
 "n1_w221_results", "n1_w220_results",
 "PERPETUAL-N1-W225", "EIGHTY-FIFTH", "EIGHTY-SIXTH instance anticipated",
 "TWO HUNDRED AND TWENTY-FIFTH", "fifty-fifth", "rows 54 + candidate",
 "rows 214 + candidate", "bmc_ordinal=55", "== 214 and len(bmc_rows_live) == 54",
 "expect 214/54", "213/53", "55th own wave",
 "MSG-20261012-1943-bmc-w225-seat", "c78dd1a44",
 "_w225bmc_20261012_probe_receipt.json", "_w225bmc_freeze_receipt.json",
 "PERPETUAL_N1_W225_PREREG", "PERPETUAL_N1_W224_PREREG",
 "PERPETUAL_N1_W223_PREREG",
 "916_589", "490_720", "916,589", "490,720",
 "(509_804, 511_803)", "(511_804, 512_003)",
 "r938 window", "r939 freeze-window bundle", "r939 freeze window",
 "r937 dead-window splice landed by r937 absorb",
 "r937 freeze window", "r937 dead window",
 "fourteenth consecutive", "fifteenth",
 "@ r938", "19:1x", "MSG-20261012-175x",
 "w224 block", "W224 block", "own W222 leg", "own W223 leg",
 "int(_estate_ws[80]) == 222", "== 81 \\", "== 82,",
 "!= 82 (69 estate",
 "W225 block parity", "81-row cut", "83 rows",
 "w225p_A", "W225p_B",
 "if w < 225)", "if w < 224", "range(16, 225)", "range(17, 225)",
 "registered wave below 225 composes",
 "w224_freeze_sha", "w224_prereg_sha", "w225_prereg_sha", "w225_receipt_sha",
 "W225 (bm-c loop", "W226 (bm-c loop",
 "wave 225 =", "wave 225:", '"wave": 225',
 "W225 entry identity", "W225 path drift", "n1_w225_results.json",
 "W225 finalize cumulative dep", "W225 prior-wave set",
 "W225 per-wave prereg missing", "W225 A/B band overlap",
 "W225 hits SEED_REGISTRY", "W225 A hits", "W225 B hits",
 "W225 shard dir collides", "W225 A window must", "W225 B window must",
 "W225 A must be", "W225 B must be",
 "W225 A/B same-freeze", "PERPETUAL-N1-W225-SHARD",
 "MSG-1225 tail",
 "w224_block_kept\": 1},",
 "    # --- W224 materializer face') == 1  # prior block kept",
 "fifty-sixth", "EIGHTY-SIXTH instance, E36 card",
]
for tk in toks:
    print(f"{t.count(tk):3d}  {tk!r}")
print("LEN", len(t))
