# -*- coding: utf-8 -*-
# r1060 bm-c: W257 editor needle pre-flight probe (count-verify every planned
# needle on the live committed source _w256bmc_freeze_edits.py BEFORE the
# derive editor runs; r1059 200-needle probe law).
import io

t = io.open(r"results\_w256bmc_freeze_edits.py", encoding="utf-8").read()

# my age() composition (W257 editor blanket): P2 W257->W258, P3 256->257, P4 255->256
def age(s):
    s = s.replace("W257", "W258")
    s = s.replace("256", "257")
    s = s.replace("255", "256")
    return s

needles = [
    # P1 structural (pre-blanket)
    ("(252, 251, 250, 249, 248, 247, 246, 245, 244, 243)", 2),
    ("range(209, 257)", 2),
    ('def fmt(n):  # 578501 -> "578_501"', 1),
    # P5a (post-blanket needles via age() of source-era literals)
    ("2026-10-17 03:2x bm-c r1058 freeze window", 1),
    ("r1058", 8),
    ("W255 finalize one-pass bm-c r1057 window closeout 02:3x", None),  # aged -> W256 face
    ("W256 finalize one-pass bm-c r1057 window closeout 02:3x", None),  # post-blanket probe
    ("r1057 splice window", 3),
    ("r1057", 23),
    ("authored 03:01", 2),
    ("985_335", 1),
    ("558_920", 1),
    ("985,335", 8),
    ("558,920", 8),
    ("bmc_ordinal=76", 7),
    ("SEVENTY-SIXTH", 3),
    ("TWO HUNDRED AND FIFTY-SIXTH", 3),
    ("forty-fourth consecutive", 2),
    ("76th own wave", 3),
    ("MSG-20261017-023x-bmc-w256-seat", 7),
    ("fd48643c9", 2),
    ("5996e2c93", 1),
    ("transitive window W243..W252 checked", 1),
    ("engine_owner==bm-c rows 75 + candidate", 1),
    # P5b
    ("# block's own W239..W254 legs (16 rows) do NOT enter the estate path;", None),
    ("# block's own W239..W254 legs (16 rows) do NOT enter the estate path;".replace("W239..W254", "W239..W254"), None),
    ("# after extraction, fresh W239..W255 legs (17 rows) are added,", None),
    ("# parity = 114 rows (W138..W206 + W211..W255). Zero assumption zero risk.", None),
    ("# block's own W239..W254 legs (16) are EXCLUDED from the estate path per the", None),
    ("# prereg mandate; the W256 block appends fresh W239..W255 legs (17,", None),
    ("# machine-derived from the LIVE pf registry at freeze time) -> 114 parity", 1),
    ('"fresh_legs_row_asserts": 17,', 1),
    ('+ legs_kept.count("assert pf.N1_BANDS[") + 17,', 1),
    ('"    #     physical bytes; the W255 block\'s own W239..W254 legs (16) are",', None),
    ('"    #     W239..W255 legs (17) added, machine-derived from the live pf",', None),
    ('"    #     registry at freeze time -> 114 parity rows (W138..W206+W211..W255).",', None),
    ("# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W255\n# block's own W239..W254 legs (16) are excluded from the estate path", None),
    # P5c
    ("assert (a_lo, a_hi) == (578_501, 580_500) and (b_lo, b_hi) == (580_501, 580_700), \\", None),
    # P5d
    ("assert len(owner_rows_live) == 245 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 75, \\", None),
    ("(expect 245/129/75 PRE-splice post-W255 registration", None),
    ("(expect 245/129/75 PRE-splice post-W256 registration", None),
    ("# receipt leg0 face owner_rows=245 / bmc_rows=75 /", 1),
    ("-> owner rows 245 + candidate = 246th EXACT; bm-c rows 75 +", 1),
    ("# candidate = 76th EXACT -- bm-c own-seat continuity face (bm-c published the", 1),
    ("freeze-time live face owner rows 245 + candidate = 246th EXACT", 1),
    ("freeze-time live derive bmc rows 75 + candidate 76th EXACT per r587/r359", 1),
    ("post-W255 registration: bm-c rows 75 + candidate = 76th owned", None),
    ("post-W256 registration: bm-c rows 75 + candidate = 76th owned", None),
    ('"probe_receipt_bmc_ordinal_face": 76,', 1),
    ('f"W256+W251..W242 finalize products present "', 1),
    # receipt-note + chunk family presence probes (post-blanket face via age)
    ("w244_a holds wave-256 bands", None),
    ("E63 8th-gen", None),
    ("hops=1 -- FOURTH", 1),
    ("hops=1 -- THIRD", 0),
    ("FIFTH consecutive A-hop", 14),
    ("SIXTH consecutive above-own-A", 5),
    ("fifth consecutive A-hop", 3),
    ("fifth consecutive above-own-A", 0),
    ("W257p_A_naive", 5),
    ("W257p_B_first_clean", 2),
    ("W253_W254_W255_bands_respected", 2),
    ("B_base_above_W255_tail", 2),
    ("A_staircase_hop_past_W255_B", 8),
    ("arith_a256", 6),
    ("arith_b256", 6),
    ("_w256bmc_20261017_probe_receipt", 10),
    ("_w256bmc_freeze_receipt.json", 1),
    ('"PERPETUAL-N1-W256-SHARD-0"', 1),
    ("n1_w256_results.json", 2),
    ("n1_w256", 4),
    ("n1w256", 2),
    ("PERPETUAL-N1-W256", 7),
    ("_w256bmc", 11),
    ("w244_a", 12),
    ("W256 materializer face", 4),
    ("W255 materializer face", 1),
    ("range(16, 256)", 2),
    ("range(17, 256)", 3),
    ("range(239, 256)", 2),
    ("list(range(211, 255)),", 1),
    ("list(range(211, 239))", 1),
    ("list(range(239, 255)),", 1),
    ("if w < 256)", 5),
    ("if w < 255)", 1),
    ("estate 69", 1),
    ("= 114 rows", 2),
    ("114 parity", 2),
    # aged forms that my editor will actually consume (spot checks)
    (age("# block's own W239..W254 legs (16 rows) do NOT enter the estate path;"), None),
    (age("# after extraction, fresh W239..W255 legs (17 rows) are added,"), None),
    (age("# parity = 114 rows (W138..W206 + W211..W255). Zero assumption zero risk."), None),
    (age("# prereg mandate; the W256 block appends fresh W239..W255 legs (17,"), None),
    (age('"    #     physical bytes; the W255 block\'s own W239..W254 legs (16) are",'), None),
    (age('"    #     W239..W255 legs (17) added, machine-derived from the live pf",'), None),
    (age('"    #     registry at freeze time -> 114 parity rows (W138..W206+W211..W255).",'), None),
    (age("# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W255\n# block's own W239..W254 legs (16) are excluded from the estate path"), None),
    (age("(expect 245/129/75 PRE-splice post-W255 registration"), None),
    (age("post-W255 registration: bm-c rows 75 + candidate = 76th owned"), None),
    (age('f"W256+W251..W242 finalize products present "'), None),
    (age("assert (a_lo, a_hi) == (578_501, 580_500) and (b_lo, b_hi) == (580_501, 580_700), \\"), None),
    (age("assert len(owner_rows_live) == 245 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 75, \\"), None),
]

fails = 0
for needle, want in needles:
    n = t.count(needle)
    mark = "OK " if (want is None or n == want) else "FAIL"
    if mark == "FAIL":
        fails += 1
    print(f"{mark} {n:3d} (want {want}) {needle[:76]!r}")
print("PRE-FLIGHT", "PASS" if fails == 0 else f"FAIL ({fails})")
