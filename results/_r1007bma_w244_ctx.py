# -*- coding: utf-8 -*-
# r1007: context dump of every mechanical-bump pattern occurrence (pre-gen evidence)
import io
t = io.open(r"results/_w243bma_freeze_edits.py", encoding="utf-8").read()
lines = t.split("\n")
pats = [
    "range(16,243)", "range(17,243)", "range(16, 243)", "range(17, 243)",
    "below-243", "below 243", "w<243", "w<242", "if w < 243)", "if w < 242)",
    "WAVE_CONFIGS[243]", "WAVE_CONFIGS[242]", "N1_BANDS[242]", "N1_BANDS[241]",
    "N1_BANDS[240]", "N1_BANDS[239]", "N1_BANDS[238]", "N1_BANDS[237]",
    "N1_BANDS[236]", "N1_BANDS[235]", "n3r1_used243", "arith_a243", "arith_b243",
    "_set_wave(243)", "n1_w242", "n1w242", "PERPETUAL-N1-W243", "PERPETUAL_N1_W242",
    "PERPETUAL_N1_W243", "242: {\"batch\"", "243: {\"batch\"", "242: {\"a\"",
    "243: {\"a\"", "243: {{\"a\"", "(241, 240", "range(232, 242)", "range(209, 244)",
    "range(17, 243)", "range(16, 243)", "for _depw in range(17, 243)",
    "for wprev in sorted(w for w in WAVE_CONFIGS if w < 243)",
    "for wprev in sorted(w for w in WAVE_CONFIGS if w < 242)",
    "232 + candidate = 233rd", "bma_ordinal=125", "125th", "124 + candidate",
    "one hundred and twenty-fifth", "ONE HUNDRED AND TWENTY-FIFTH",
    "TWO HUNDRED AND FORTY-THIRD", "FORTY-THIRD", "twenty-fifth",
    "thirty-second consecutive", "fourth consecutive seed-gap", "gap face fifth",
    "fifth consecutive", "rows 232", "== 232", "== 124", "232/124/67",
    "233rd", "541_501", "541_700", "551_501", "553_500",
    "MSG-20261014-2107", "20261014", "6207e60e9", "4574bfeca", "70141bc22",
    "r998", "r999", "r1000", "r1001", "r1002", "20:4x", "01:0x",
    "W244", "w242_leg", "w242_own_line", "w242_row_start", "_c242",
    "w242_a", "w242_b", "W242 = dict", "w242_out", "w242_total", "w242_merged_n",
    "w242_freeze_sha", "w242_prereg_sha", "w242_a_tail", "w242_b_tail",
    "a22 = ", "m232", "par_sec", "legs_sec", "101 parity rows", "== 100",
    "estate 90", "legs 10", "W232..W241", "W241/W240",
    "W243 block = 101 rows", "101 rows ending at W242", "hops=1",
]
for p in pats:
    c = t.count(p)
    print("### %r  count=%d" % (p, c))
    if 0 < c <= 14:
        for i, l in enumerate(lines, 1):
            if p in l:
                print("   %4d| %s" % (i, l.strip()[:150]))
