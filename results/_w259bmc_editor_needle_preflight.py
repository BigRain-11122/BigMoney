# -*- coding: utf-8 -*-
# r1063 bm-c: W259 splice-editor needle-count pre-flight probe (canon-clone of _w258bmc_editor_needle_preflight.py).
# Measures every candidate needle face on T0 = the COMMITTED W258 freeze-edits script
# (results/_w258bmc_freeze_edits.py @ HEAD, blob aa9ae1bf918593902cfd90b301edcfac390d2d50). Output: results/_w259bmc_editor_needle_counts.txt
# ("count<TAB>needle" per line). E259 rep()/chunk() floors must equal these measured counts. Zero transcription.
import io

SRC = "results/_w258bmc_freeze_edits.py"
OUT = "results/_w259bmc_editor_needle_counts.txt"
T0 = io.open(SRC, encoding="utf-8", newline="").read()

NEEDLES = [
    # ---- P1 structural ----
    "(254, 253, 252, 251, 250, 249, 248, 247, 246, 245)",
    "range(209, 259)",
    'def fmt(n):  # 582901 -> "582_901"',
    # ---- P5a r-window / ledger / ordinal faces (S258 true forms) ----
    "2026-10-17 06:2x bm-c r1062 freeze window",
    "r1061", "r1060", "r1062",
    "W257 finalize one-pass bm-c r1060 window closeout 05:1x",
    "r1060 splice window",
    "authored 05:5x",
    "989_735", "563_320", "989,735", "563,320",
    "bmc_ordinal=78", "SEVENTY-EIGHTH", "TWO HUNDRED AND FIFTY-EIGHTH",
    "forty-sixth consecutive", "78th own wave",
    "MSG-20261017-0517-bmc-w258-seat", "d0d0d04a4", "824b46d31",
    "transitive window W245..W254 checked",
    "engine_owner==bm-c rows 77 + candidate",
    "saturation_engine.py status live-read r1061",
    # ---- P5b extraction count faces ----
    "# block's own W240..W256 legs (17 rows) do NOT enter the estate path;",
    "# after extraction, fresh W240..W257 legs (18 rows) are added,",
    "# parity = 116 rows (W138..W206 + W211..W257). Zero assumption zero risk.",
    "# block's own W240..W256 legs (17) are EXCLUDED from the estate path per the",
    "# prereg mandate; the W258 block appends fresh W240..W257 legs (18,",
    "# machine-derived from the LIVE pf registry at freeze time) -> 116 parity",
    "m240", "W240 leg boundary",
    "range(240, 258)",
    '"    #     physical bytes; the W258 block\'s own W240..W256 legs (17) are",',
    '"    #     W240..W257 legs (18) added, machine-derived from the live pf",',
    '"    #     registry at freeze time -> 116 parity rows (W138..W206+W211..W257).",',
    '"    #     W211..W239 legs (29) extracted verbatim from the OWN W257 block",',
    # ---- P5c band literal ----
    'assert (a_lo, a_hi) == (582_901, 584_900) and (b_lo, b_hi) == (584_901, 585_100), \\',
    # ---- P5d ordinal/leg0 faces ----
    'assert len(owner_rows_live) == 247 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 77, \\',
    "(expect 247/129/77 PRE-splice post-W257 registration",
    '# receipt leg0 face owner_rows=247 / bmc_rows=77 /',
    "-> owner rows 247 + candidate = 248th EXACT; bm-c rows 77 +",
    "# candidate = 78th EXACT -- bm-c own-seat continuity face (bm-c published the",
    "freeze-time live face owner rows 247 + candidate = 248th EXACT",
    "freeze-time live derive bmc rows 77 + candidate 78th EXACT per r587/r359",
    "post-W257 registration: bm-c rows 77 + candidate = 78th owned",
    '"probe_receipt_bmc_ordinal_face": 78,',
    'f"W258+W253..W244 finalize products present "',
    # ---- P5f date face ----
    "_w258bmc_20261017_probe_receipt.json",
    "_w259bmc_20261017_probe_receipt.json",
    # ---- output-gate faces (post-transform expectations rolled one era) ----
    "range(16, 259)", "range(17, 259)", "if w < 259)", "if w < 258)",
    "list(range(211, 258)),", "list(range(211, 240))", "list(range(240, 257)),",
    "arith_a258", "arith_b258", "n1_w258", "n1w258", "PERPETUAL-N1-W258",
    "_w258bmc", "w245_a", "estate 69", "= 116 rows", "116 parity",
    "EIGHTH consecutive above-own-A", "SEVENTH consecutive A-hop",
    "NINTH consecutive above-own-A", "EIGHTH consecutive A-hop",
    "W259p_A_naive", "W259p_B_first_clean", "W260p_A_naive",
    "W255_W256_W257_bands_respected_A", "W256_W257_W258_bands_respected_A",
    "B_base_above_W257_tail", "B_base_above_W258_tail",
    "A_staircase_hop_past_W257_B", "A_staircase_hop_past_W258_B",
    "hashlib.sha256", "hashlib.sha257", "hashlib.sha258",
    "SEVENTY-NINTH", "TWO HUNDRED AND FIFTY-NINTH", "bmc_ordinal=79", "79th own wave",
    "248th", "249th", "247/129/77", "248/129/78",
    "991,935", "565,520", "991_935", "563_520",
    "16dba0e70", "b709bc2cc", "MSG-20261017-0704-bmc-w259-seat",
    "117 parity", "= 117 rows", "117 rows",
    "m241", "list(range(211, 241))", "list(range(241, 258)),", "range(241, 259)",
    "kept segment not W211..W239 twenty-nine legs",
    "kept segment not W211..W240 thirty legs",
    "dropped segment not W240..W256 seventeen legs",
    "dropped segment not W241..W257 seventeen legs",
    "legs segment not W211..W256 forty-six legs",
    "legs segment not W211..W257 forty-seven legs",
    "full parity span", "!= 115 (69 estate + W211..W256 legs 46)",
    "!= 116 (69 estate + W211..W257 legs 47)",
    "fresh_legs_row_asserts", "+ legs_kept.count(",
    # ---- band-window faces (S258 true forms) ----
    "582_901..584_900", "584_901..585_100", "582_701..584_700", "582_701..582_900",
    "582_901..583_100", "582_900", "584_900",
    "585_101..587_100", "587_101..587_300", "584_901..586_900", "585_101..585_300",
    "585_100", "587_100",
    "A naive 584901..586900 CLEAN", "B naive 585101..585300 hops=0 CLEAN at naive, first-clean 585101..585300 BUT",
    "naive A window start 584_901 lands INSIDE the registered W258 B band 584_901..585_100",
    "A naive 587101..589100 CLEAN", "B naive 587301..587500 hops=0 CLEAN at naive, first-clean 587301..587500 BUT",
    "naive A window start 587_101 lands INSIDE the registered W259 B band 587_101..587_300",
]

rows = []
for n in NEEDLES:
    rows.append("%d\t%s" % (T0.count(n), n))
io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(rows) + "\n")
print("needle preflight: counted %d faces -> %s" % (len(NEEDLES), OUT))
