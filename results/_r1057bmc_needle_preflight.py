# -*- coding: utf-8 -*-
# r1057 bm-c needle pre-flight: count every planned W255-editor needle face (W254-era form) in the
# live _w254bmc_freeze_edits.py before authoring the editor (count-asserted pre-flight law, r1056 precedent).
import io
t = io.open(r'results\_w254bmc_freeze_edits.py', encoding='utf-8').read()

P1 = [
    ("(250, 249, 248, 247, 246, 245, 244, 243, 242, 241)", 2),
    ("range(209, 255)", 2),
    ('def fmt(n):  # 574101 -> "574_101"', 1),
]
P5a = [
    ("980_935", 1), ("554_520", 1),
    ("980,935", 8), ("554,520", 8),
    ("bmc_ordinal=74", 7),
    ("SEVENTY-FOURTH", 3),
    ("TWO HUNDRED AND FIFTY-FOURTH", 3),
    ("forty-second consecutive", 2),
    ("74th own wave", 3),
    ("MSG-20261016-14xx-bmc-w254-seat", 7),
    ("fa70f3765", 2),
    ("e2c4b543e", 1),
    ("2026-10-16 20:2x bm-c r1055 freeze window", 1),
    ("W253 finalize one-pass bm-c r1053 window closeout 15:2x", 1),
    ("r1053 splice window", 3),
    ("r1053", 23),
    ("r1054", 7),
    ("authored 18:0x", 2),
    ("transitive window W241..W250 checked", 1),
    ("engine_owner==bm-c rows 73 + candidate", 1),
]
P5b = [
    ("# block's own W239..W252 legs (14 rows) do NOT enter the estate path;", 1),
    ("# after extraction, fresh W239..W253 legs (15 rows) are added,", 1),
    ("# parity = 112 rows (W138..W206 + W211..W253). Zero assumption zero risk.", 1),
    ("# block's own W239..W252 legs (14) are EXCLUDED from the estate path per the", 1),
    ("# prereg mandate; the W254 block appends fresh W239..W253 legs (15,", 1),
    ("# machine-derived from the LIVE pf registry at freeze time) -> 112 parity", 1),
    ('assert par_full.count("assert pf.N1_BANDS[") == 111', 1),
    ('!= 111 (69 estate + W211..W252 legs 42)"', 1),
    ('assert legs_sec.count("assert pf.N1_BANDS[") == 42', 1),
    ('legs segment not W211..W252 forty-two legs', 1),
    ("list(range(211, 253)),", 1),
    ("# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W253", 1),
    ("# block's own W239..W252 legs (14) are excluded from the estate path", 1),
    ('assert legs_dropped.count("assert pf.N1_BANDS[") == 14', 1),
    ("list(range(239, 253)),", 1),
    ('dropped segment not W239..W252 fourteen legs', 1),
    ('"fresh_legs_row_asserts": 15,', 1),
    ('+ legs_kept.count("assert pf.N1_BANDS[") + 15,', 1),
    ('"    #     physical bytes; the W253 block\'s own W239..W252 legs (14) are",', 1),
    ('"    #     W239..W253 legs (15) added, machine-derived from the live pf",', 1),
    ('"    #     registry at freeze time -> 112 parity rows (W138..W206+W211..W253).",', 1),
]
P5c = [
    ("assert (a_lo, a_hi) == (574_101, 576_100) and (b_lo, b_hi) == (576_101, 576_300),", 1),
]
P5d = [
    ("assert len(owner_rows_live) == 243 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 73,", 1),
    ("(expect 243/129/73 PRE-splice post-W253 registration; this candidate = bm-c's 74th own wave per the same live-derive law, r587/r359)", 1),
    ("# receipt leg0 face owner_rows=243 / bmc_rows=73 / bmc_ordinal=74", 1),
    ("-> owner rows 243 + candidate = 244th EXACT; bm-c rows 73 +", 1),
    ("# candidate = 74th EXACT -- bm-c own-seat continuity face (bm-c published the", 1),
    ("freeze-time live face owner rows 243 + candidate = 244th EXACT", 1),
    ("freeze-time live derive bmc rows 73 + candidate 74th EXACT per r587/r359", 1),
    ("post-W253 registration: bm-c rows 73 + candidate = 74th owned", 1),
    ('"probe_receipt_bmc_ordinal_face": 74,', 1),
    ('f"W254+W249..W240 finalize products present "', 1),
]
chunks = [
    ("# NEW FACE vs the W253 editor (honest disclosure, frozen W254 prereg sec.3", 1),
    ("# W254 FACE (probe receipt leg1 relation_asserts):", 1),
    ('"    # band gate ADMIT results/_w254bmc_20261016_probe_receipt.json: A = 1-HOP",', 1),
    ('"wave 254: ",', 1),
    ('"        # band facts (law sec.4 W254 row): A = 1-HOP STAIRCASE-AFFECTS-A",', 1),
    ('"note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W238 legs (28) extracted verbatim per the frozen W254 prereg sec.3 mandate;', 1),
]
P5e_reps = [
    ('assert w253_b_tail + 1 == a_lo, "A staircase-hop landing base relation', 1),
    ('assert a_lo >= w253_b_tail + 1, "A staircase landing floor relation', 1),
    ('assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation cascade lands ABOVE own-A -- fourth consecutive above-own-A;', 1),
    ('and ra.get("W251_W252_W253_bands_respected_A") and ra.get("W251_W252_W253_bands_respected_B"),', 1),
    ('# law sec.4 W254 A: {fmt(a_lo)}..{fmt(a_hi)} (1-HOP STAIRCASE-AFFECTS-A walk THIRD consecutive A-hop;', 1),
    ('# law sec.4 W254 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION CASCADE above own-A; naive {fmt(w253_b_tail + 1)}..{fmt(w253_b_tail + 200)} REFUSED at start', 1),
    ('W255p face per this window\'s probe leg4 (pre-W254 universe): A naive 576101..578100 CLEAN', 1),
    ('"W254 A staircase-affects-A walk THIRD consecutive A-hop: the naive "', 1),
    ('"W254 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "', 1),
    ('"W254 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- fourth consecutive above-own-A; zero overlap)"', 1),
    ('"W254 A window must be CLEAN (first-clean ADMIT face, staircase walk landing)"', 1),
    ('"W254 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"', 1),
    ('"A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, "', 1),
]
structural = [
    ("range(16, 254)", 2), ("range(17, 254)", 3), ("range(239, 254)", 2),
    ("if w < 254)", 5), ("if w < 253)", 1),
    ("list(range(211,253))", None), ("list(range(239,253))", None),
    ("arith_a254", 6), ("arith_b254", 6),
    ('"PERPETUAL-N1-W254-SHARD-0"', 1), ("n1_w254_results.json", 2), ("n1_w254", None),
    ("n1w254", 2), ("PERPETUAL-N1-W254", 7), ("_w254bmc", 11), ("w244_a", 12),
    ("# --- W254 materializer face", 2), ("# --- W253 materializer face", 1),
    ('"+ W254 materializer face', 2),
    ("list(range(211, 239))", 1),
]

fails = 0
for name, probes in [("P1", P1), ("P5a", P5a), ("P5b", P5b), ("P5c", P5c), ("P5d", P5d), ("chunks", chunks), ("P5e", P5e_reps), ("structural", structural)]:
    print("===", name)
    for needle, want in probes:
        n = t.count(needle)
        ok = "OK " if (want is None or n == want) else "FAIL"
        if ok == "FAIL": fails += 1
        print(f"{ok} n={n} want={want} :: {needle[:96]}")
print("TOTAL FAILS:", fails)
