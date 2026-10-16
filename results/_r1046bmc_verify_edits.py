# -*- coding: utf-8 -*-
# r1046 bm-c: W250 freeze-edits pre-splice key-face verification
import io
t = io.open(r"results\_w250bmc_freeze_edits.py", encoding="utf-8").read()
checks = [
 ("estate 91", 'assert par_sec.count("assert pf.N1_BANDS[") == 91'),
 ("estate decomp 232", "and int(_estate_ws[90]) == 232"),
 ("m233 def", "m233 = re.search"),
 ("m238 def", "m238 = re.search"),
 ("kept list", "[233, 234, 235, 236, 237]"),
 ("kept count 5", 'assert legs_kept.count("assert pf.N1_BANDS[") == 5'),
 ("legs range", "list(range(233, 249))"),
 ("dropped range", "list(range(238, 249))"),
 ("fresh loop", "for _w in range(238, 250):"),
 ("parfull 107", "== 107"),
 ("ledger int", "w249_total == 972_135 and w249_merged_n == 545_720"),
 ("band drift A", "(565_501, 567_500)"),
 ("band drift B", "(545_101, 545_300)"),
 ("ord gate", "== 239 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 69"),
 ("rsv keys", "W248_W249_bands_respected_A"),
 ("bbase key", "B_base_above_W249_tail"),
 ("receipt in", 'RECEIPT_IN = os.path.join(REPO, "results", "_w250bmc_20261016_probe_receipt.json")'),
 ("receipt out", "_w250bmc_freeze_receipt.json"),
 ("seat msg", 'SEAT_MSG = "MSG-20261016-055x-bmc-w250-seat.md"'),
 ("seat origin", 'SEAT_ORIGIN = "cc06f1f4a"'),
 ("transitive", "(246, 245, 244, 243, 242, 241, 240, 239, 238, 237)"),
 ("liveness", "range(209, 251)"),
 ("leg4 first_clean ref", "W251p_B_first_clean"),
 ("family6", "if w < 250)"),
 ("materializer hdr", "# --- W250 materializer face"),
 ("batch", "PERPETUAL-N1-W250"),
 ("arith", "arith_a250"),
 ("leg count loop", "for _lw in range(238, 250):"),
 ("n1 out path", 'n1_w249_results.json"'),
 ("w249 row pickaxe", '-S\', \'249: {"a"\''),
]
bad = 0
for name, needle in checks:
    n = t.count(needle)
    print("%d | %s" % (n, name))
    if n == 0:
        bad += 1
print("BAD =", bad, "| total chars", len(t))
