# -*- coding: utf-8 -*-
# r937 verify: key payload sections in derived W224 editor (zero writes)
import io
t = io.open(r"results\_w224bmc_freeze_edits.py", encoding="utf-8").read()
toks = [
    "(a_lo, a_hi) == (507_604, 509_603)",
    "(b_lo, b_hi) == (509_604, 509_803)",
    "SEAT_MSG = ",
    "SEAT_ORIGIN = ",
    "PERPETUAL_N1_W224_PREREG",
    "MSG-20261012-175x-bmc-w224-seat.md",
    "n1_w223_results.json",
    'rec["legs"]["leg4"]["W224p_A"]',
    "== 213 and len(bmc_rows_live) == 53",
    "rows 53 + candidate",
    '"probe_receipt_bmc_ordinal_face": 54',
    "914,389",
    "488,520",
    "EIGHTY-FIFTH instance anticipated",
    "r934 splice (dead-window estate, landed by own commit)",
    "r935 finalize one-pass 17:2x (six-gate PRE-FINALIZE all-green 17:24:44, 3rd consecutive correct-phase)",
]
for tok in toks:
    i = t.find(tok)
    print(("OK  " if i >= 0 else "MISS"), tok[:70])
print()
i = t.find("(a_lo, a_hi) == (507_604")
print("band ctx:", repr(t[i - 90:i + 160]))
print()
i = t.find("SEAT_MSG")
print("seat ctx:", repr(t[i - 60:i + 260]))
print()
i = t.find('["W224p_A"]')
print("leg4 ctx:", repr(t[i - 120:i + 120]))
