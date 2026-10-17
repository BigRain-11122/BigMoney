# -*- coding: utf-8 -*-
# r1065 bm-c: W260 splice-editor needle-count pre-flight probe (canon-clone of _w259bmc_editor_needle_preflight.py).
# Measures every candidate needle face on T0 = the COMMITTED W259 freeze-edits script
# (results/_w259bmc_freeze_edits.py @ HEAD, blob 601de02f483acb8a0dfbf048cce200607f3a6fb2). Output: results/_w260bmc_editor_needle_counts.txt
# ("count<TAB>needle" per line). E260 rep()/chunk() floors must equal these measured counts. Zero transcription.
import io, subprocess

SRC = "results/_w259bmc_freeze_edits.py"
OUT = "results/_w260bmc_editor_needle_counts.txt"
blob_wt = subprocess.run(["git", "hash-object", SRC], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w259bmc_freeze_edits.py"], capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head == "601de02f483acb8a0dfbf048cce200607f3a6fb2", f"SRC blob drift: wt={blob_wt} head={blob_head}"
T0 = io.open(SRC, encoding="utf-8", newline="").read()

NEEDLES = [
    # ---- P1 structural ----
    "(255, 254, 253, 252, 251, 250, 249, 248, 247, 246)",
    "range(209, 260)",
    'def fmt(n):  # 585101 -> "585_101"',
    # ---- P5a r-window / ledger / ordinal faces (S259 true forms) ----
    "2026-10-17 08:4x bm-c r1064 freeze window",
    "r1063", "r1062", "r1064",
    "W258 finalize one-pass bm-c r1062 window closeout 07:0x",
    "r1062 splice window",
    "authored 07:3x",
    "991_935", "565_520", "991,935", "565,520",
    "bmc_ordinal=79", "SEVENTY-NINTH", "TWO HUNDRED AND FIFTY-NINTH",
    "forty-seventh consecutive", "79th own wave",
    "MSG-20261017-0704-bmc-w259-seat", "16dba0e70", "b709bc2cc",
    "transitive window W246..W255 checked",
    "engine_owner==bm-c rows 78 + candidate",
    "saturation_engine.py status live-read r1063",
    # ---- P5b extraction count faces ----
    "# block's own W241..W257 legs (17 rows) do NOT enter the estate path;",
    "# after extraction, fresh W241..W258 legs (18 rows) are added,",
    "# parity = 117 rows (W138..W206 + W211..W258). Zero assumption zero risk.",
    "# block's own W241..W257 legs (17) are EXCLUDED from the estate path per the",
    "# prereg mandate; the W259 block appends fresh W241..W258 legs (18,",
    "# machine-derived from the LIVE pf registry at freeze time) -> 117 parity",
    "m241", "W241 leg boundary",
    "range(241, 259)",
    '"    #     physical bytes; the W259 block\'s own W241..W257 legs (17) are",',
    '"    #     W241..W258 legs (18) added, machine-derived from the live pf",',
    '"    #     registry at freeze time -> 117 parity rows (W138..W206+W211..W258).",',
    '"    #     W211..W240 legs (30) extracted verbatim from the OWN W258 block",',
    "kept segment not W211..W240 thirty legs",
    "dropped segment not W241..W257 seventeen legs",
    "legs segment not W211..W257 forty-seven legs",
    "!= 116 (69 estate + W211..W257 legs 47)",
    "!= 115 (69 estate + W211..W256 legs 46)",
    "fresh_legs_row_asserts", '+ legs_kept.count("assert pf.N1_BANDS[") + 18,',
    '"fresh_legs_row_asserts": 18,',
    # ---- P5c band literal ----
    'assert (a_lo, a_hi) == (585_101, 587_100) and (b_lo, b_hi) == (587_101, 587_300), \\',
    # ---- P5d ordinal/leg0 faces ----
    'assert len(owner_rows_live) == 248 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 78, \\',
    "(expect 248/129/78 PRE-splice post-W258 registration",
    '# receipt leg0 face owner_rows=248 / bmc_rows=78 /',
    "-> owner rows 248 + candidate = 249th EXACT; bm-c rows 78 +",
    "# candidate = 79th EXACT -- bm-c own-seat continuity face (bm-c published the",
    "freeze-time live face owner rows 248 + candidate = 249th EXACT",
    "freeze-time live derive bmc rows 78 + candidate 79th EXACT per r587/r359",
    "post-W258 registration: bm-c rows 78 + candidate = 79th owned",
    '"probe_receipt_bmc_ordinal_face": 79,',
    'f"W259+W254..W245 finalize products present "',
    # ---- P5f date face ----
    "_w259bmc_20261017_probe_receipt.json",
    "_w260bmc_20261017_probe_receipt.json",
    # ---- output-gate faces (raw T0 forms; post-blanket they roll one era) ----
    "range(16, 259)", "range(17, 259)", "if w < 259)", "if w < 258)",
    "list(range(211, 258)),", "list(range(211, 241))", "list(range(241, 258)),",
    "arith_a259", "arith_b259", "n1_w259", "n1w259", "PERPETUAL-N1-W259",
    '_w259bmc', "w245_a", "estate 69", "= 117 rows", "117 parity",
    "EIGHTH consecutive above-own-A", "SEVENTH consecutive A-hop",
    "NINTH consecutive above-own-A", "EIGHTH consecutive A-hop",
    "W260p_A_naive", "W260p_B_first_clean", "W261p_A_naive",
    "W256_W257_W258_bands_respected_A", "W257_W258_W259_bands_respected_A",
    "B_base_above_W258_tail", "B_base_above_W259_tail",
    "A_staircase_hop_past_W258_B", "A_staircase_hop_past_W259_B",
    "hashlib.sha256", "hashlib.sha258", "hashlib.sha259",
    "SEVENTY-NINTH", "TWO HUNDRED AND FIFTY-NINTH", "bmc_ordinal=79", "79th own wave",
    "249th", "250th", "248/129/78", "249/129/79",
    "994,135", "567,720", "994_135", "567_720",
    "9fa2c8aed", "0f33f9abc", "MSG-20261017-0910-bmc-w260-seat",
    "118 parity", "= 118 rows",
    "m242", "list(range(211, 242))", "list(range(242, 259)),", "range(242, 260)",
    "kept segment not W211..W241 thirty-one legs",
    "dropped segment not W242..W258 seventeen legs",
    "legs segment not W211..W258 forty-eight legs",
    "!= 117 (69 estate + W211..W258 legs 48)",
    # ---- band-window faces (S259 true forms) ----
    "585_101..587_100", "587_101..587_300", "584_901..586_900", "584_901..585_100",
    "585_101..585_300", "585_100", "587_100",
    "587_301..589_300", "589_301..589_500", "587_101..589_100", "587_301..587_500",
    "587_300", "589_300",
    "A naive 587101..589100 CLEAN", "B naive 587301..587500 hops=0 CLEAN at naive, first-clean 587301..587500 BUT",
    "naive A window start 587_101 lands INSIDE the registered W259 B band 587_101..587_300",
    "A naive 589301..591300 CLEAN", "B naive 589501..589700 hops=0 CLEAN at naive, first-clean 589501..589700 BUT",
    "naive A window start 589_301 lands INSIDE the registered W260 B band 589_301..589_500",
]

rows = []
for n in NEEDLES:
    rows.append("%d\t%s" % (T0.count(n), n))
io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(rows) + "\n")
print("needle preflight: counted %d faces -> %s" % (len(NEEDLES), OUT))
