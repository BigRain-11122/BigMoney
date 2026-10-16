# -*- coding: utf-8 -*-
# r1062 bm-c: W258 splice-editor needle-count pre-flight probe (canon-clone of _w257bmc_needle_preflight.py).
# Measures every candidate needle face on T0 = the COMMITTED W257 freeze-edits script
# (results/_w257bmc_freeze_edits.py @ HEAD). Output: results/_w258bmc_editor_needle_counts.txt
# ("count<TAB>needle" per line). E258 rep()/chunk() floors must equal these measured counts. Zero transcription.
import io

SRC = "results/_w257bmc_freeze_edits.py"
OUT = "results/_w258bmc_editor_needle_counts.txt"
T0 = io.open(SRC, encoding="utf-8", newline="").read()

NEEDLES = [
    # ---- P1 structural ----
    "(253, 252, 251, 250, 249, 248, 247, 246, 245, 244)",
    "range(209, 258)",
    'def fmt(n):  # 580701 -> "580_701"',
    # ---- P5a r-window / ledger / ordinal faces (S257 true forms) ----
    "2026-10-17 04:4x bm-c r1060 freeze window",
    "r1059", "r1058", "r1060",
    "W256 finalize one-pass bm-c r1058 window closeout 04:0x",
    "r1058 splice window",
    "authored 04:1x",
    "987_535", "561_120", "987,535", "561,120",
    "bmc_ordinal=77", "SEVENTY-SEVENTH", "TWO HUNDRED AND FIFTY-SEVENTH",
    "forty-fifth consecutive", "77th own wave",
    "MSG-20261017-03xx-bmc-w257-seat", "27ee6e95a", "c7fbc443c",
    "transitive window W244..W253 checked",
    "engine_owner==bm-c rows 76 + candidate",
    "saturation_engine.py status live-read r1059",
    # ---- P5b extraction count faces ----
    "# block's own W239..W255 legs (17 rows) do NOT enter the estate path;",
    "# after extraction, fresh W239..W256 legs (18 rows) are added,",
    "# parity = 115 rows (W138..W206 + W211..W256). Zero assumption zero risk.",
    "# block's own W239..W255 legs (17) are EXCLUDED from the estate path per the",
    "# prereg mandate; the W257 block appends fresh W239..W256 legs (18,",
    "# machine-derived from the LIVE pf registry at freeze time) -> 115 parity",
    "m239", "W239 leg boundary",
    "range(239, 257)",
    '"    #     physical bytes; the W257 block\'s own W239..W255 legs (17) are",',
    '"    #     W239..W256 legs (18) added, machine-derived from the live pf",',
    '"    #     registry at freeze time -> 115 parity rows (W138..W206+W211..W256).",',
    # ---- P5c band literal ----
    'assert (a_lo, a_hi) == (580_701, 582_700) and (b_lo, b_hi) == (582_701, 582_900), \\',
    # ---- P5d ordinal/leg0 faces ----
    'assert len(owner_rows_live) == 246 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 76, \\',
    "(expect 246/129/76 PRE-splice post-W256 registration",
    '# receipt leg0 face owner_rows=246 / bmc_rows=76 /',
    "-> owner rows 246 + candidate = 247th EXACT; bm-c rows 76 +",
    "# candidate = 77th EXACT -- bm-c own-seat continuity face (bm-c published the",
    "freeze-time live face owner rows 246 + candidate = 247th EXACT",
    "freeze-time live derive bmc rows 76 + candidate 77th EXACT per r587/r359",
    "post-W256 registration: bm-c rows 76 + candidate = 77th owned",
    '"probe_receipt_bmc_ordinal_face": 77,',
    'f"W257+W252..W243 finalize products present "',
    # ---- P5f date face ----
    "_w257bmc_20261017_probe_receipt.json",
    "_w258bmc_20261017_probe_receipt.json",
    # ---- output-gate faces (post-transform expectations rolled one era) ----
    "range(16, 258)", "range(17, 258)", "if w < 258)", "if w < 257)",
    "list(range(211, 257)),", "list(range(211, 239))", "list(range(239, 256)),",
    "arith_a257", "arith_b257", "n1_w257", "n1w257", "PERPETUAL-N1-W257",
    "_w257bmc", "w244_a", "estate 69", "= 115 rows", "115 parity",
    "SEVENTH consecutive above-own-A", "SIXTH consecutive A-hop",
    "EIGHTH consecutive above-own-A", "SEVENTH consecutive A-hop",
    "W258p_A_naive", "W258p_B_first_clean", "W259p_A_naive",
    "W254_W255_W256_bands_respected_A", "W255_W256_W257_bands_respected_A",
    "B_base_above_W256_tail", "B_base_above_W257_tail",
    "A_staircase_hop_past_W256_B", "A_staircase_hop_past_W257_B",
    "hashlib.sha256", "hashlib.sha257",
    "SEVENTY-EIGHTH", "TWO HUNDRED AND FIFTY-EIGHTH", "bmc_ordinal=78", "78th own wave",
    "247th", "248th", "246/129/76", "247/129/77",
    "989,735", "563,320", "989_735", "563_120",
    "d0d0d04a4", "824b46d31", "MSG-20261017-0517-bmc-w258-seat",
    "116 parity", "= 116 rows", "116 rows",
    "m240", "list(range(211, 240))", "list(range(240, 257)),", "range(240, 258)",
    "kept segment not W211..W238 twenty-eight legs",
    "kept segment not W211..W239 twenty-nine legs",
    "dropped segment not W239..W255 seventeen legs",
    "dropped segment not W240..W256 seventeen legs",
    "legs segment not W211..W255 forty-five legs",
    "legs segment not W211..W256 forty-six legs",
    "full parity span", "!= 114 (69 estate + W211..W255 legs 45)",
    "!= 115 (69 estate + W211..W256 legs 46)",
    "fresh_legs_row_asserts", "+ legs_kept.count(",
    # ---- band-window faces (S257 true forms) ----
    "580_701..582_700", "582_701..582_900", "580_501..582_500", "580_501..580_700",
    "580_701..580_900", "580_700", "582_700",
    "582_901..584_900", "584_901..585_100", "582_701..584_700", "582_901..583_100",
    "582_900", "584_900",
    "A naive 582701..584700 CLEAN", "B naive 582901..583100 hops=0 CLEAN at naive, first-clean 582901..583100 BUT",
    "naive A window start 582_701 lands INSIDE the registered W257 B band 582_701..582_900",
    "A naive 584901..586900 CLEAN", "B naive 585101..585300 hops=0 CLEAN at naive, first-clean 585101..585300 BUT",
    "naive A window start 584_901 lands INSIDE the registered W258 B band 584_901..585_100",
]

rows = []
for n in NEEDLES:
    rows.append("%d\t%s" % (T0.count(n), n))
io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(rows) + "\n")
print("needle preflight: counted %d faces -> %s" % (len(NEEDLES), OUT))
