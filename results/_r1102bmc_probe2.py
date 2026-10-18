# -*- coding: utf-8 -*-
"""batch-2 needle probe: escape-form variants, variable names, multi-line
sentence needles for the W273 derive editor (r1077 measured-counts law)."""
import io

t = io.open("results/_w272bmc_freeze_edits.py", encoding="utf-8", newline="").read()
CRLF = "\r\n"
N = [
    # --- escape-form variants (r1091: file BYTES differ) ---
    "engine_owner=bm-a (bm-c OWN-SEAT face -- bm-a's NINETY-FIRST owned claim",
    "bm-a's NINETY-FIRST owned per machine-derive (engine_owner==bm-a",
    "bm-a\\'s NINETY-FIRST owned claim per ",
    "bm-a\\'s NINETY-FIRST owned per machine-derive (engine_owner==bm-a",
    # --- variables (upstream w271_* -> w272_*; current w272_prereg/receipt -> w273_*) ---
    "w271_freeze_sha", "w271_prereg_sha", "w272_prereg_sha", "w272_receipt_sha",
    "w271_out_path", "w271_total", "w271_merged_n", "w271_led", "w271_b_tail",
    "w271_a_tail", "w271_own_line", "w271_row_start", "W271 = dict",
    "'271: {\"a\"'", "w271_out = json.load",
    # --- prereg/batch name faces ---
    "PERPETUAL_N1_W272_PREREG", "PERPETUAL_N1_W271_PREREG",
    "PERPETUAL-N1-W272", "PERPETUAL-N1-W271",
    "n1_w271_results.json", "n1_w272_results.json",
    # --- multi-line header sentence (CRLF physical form) ---
    "committed+pushed same" + CRLF + "# window c049a57623).",
    "(machine-SUB from the frozen W271 template)",
    "(authored 19:2x, banned gate ADMIT rc0, committed+pushed r1099 commit ",
    "(authored 19:2x, banned_direction_gate ADMIT rc0, committed+pushed same",
    # --- more probes ---
    "engine_owner==bm-a", "engine_owner==bm-c",
    "W271 = dict(pf_mod.N1_BANDS.get(271)",
    "bm-c r1099 window machine-SUB derive landed pre-freeze",
    "W272 = bm-c OWN WAVE complete chain (finalize ledger",
    "W271 bm-c own-wave full cycle r1097 (five-face splice",
    "zero skip-claim",
    "W272 FREEZE UNBLOCKED at seat time",
    "banned gate ADMIT 0 (re-run at freeze window)",
    "2026-10-18 21:1x",
]
for n in N:
    print("%5d  %r" % (t.count(n), n))
print("PROBE2-OK")
