# -*- coding: utf-8 -*-
# r1067 bm-c: W261 splice-editor needle-count pre-flight probe (canon-clone of _w260bmc_editor_needle_preflight.py).
# Measures every candidate needle face on T0 = the COMMITTED W260 freeze-edits script
# (results/_w260bmc_freeze_edits.py @ HEAD, blob d15b53af21cff0ec34271e9a24eab731750a3b07). Output: results/_w261bmc_editor_needle_counts.txt
# ("count<TAB>needle" per line). E261 rep()/chunk() floors must equal these measured counts. Zero transcription.
import io, subprocess

SRC = "results/_w260bmc_freeze_edits.py"
OUT = "results/_w261bmc_editor_needle_counts.txt"
blob_wt = subprocess.run(["git", "hash-object", SRC], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w260bmc_freeze_edits.py"], capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head == "d15b53af21cff0ec34271e9a24eab731750a3b07", f"SRC blob drift: wt={blob_wt} head={blob_head}"
T0 = io.open(SRC, encoding="utf-8", newline="").read()

NEEDLES = [
    # ---- P1 structural ----
    "(256, 255, 254, 253, 252, 251, 250, 249, 248, 247)",
    "range(209, 261)",
    'def fmt(n):  # 587301 -> "587_301"',
    # ---- P5a r-window / ledger / ordinal faces (S260 true forms) ----
    "2026-10-17 11:3x bm-c r1065 freeze window",
    "r1065", "r1064", "r1066", "r1063", "r1062",
    "W259 finalize one-pass bm-c r1064 window closeout 09:1x",
    "r1064 splice window",
    "authored 10:2x",
    "994_135", "567_720", "994,135", "567,720",
    "bmc_ordinal=80", "EIGHTIETH", "TWO HUNDRED AND SIXTIETH",
    "forty-eighth consecutive", "80th own wave",
    "MSG-20261017-0910-bmc-w260-seat", "9fa2c8aed", "0f33f9abc",
    "transitive window W247..W256 checked",
    "engine_owner==bm-c rows 79 + candidate",
    "saturation_engine.py status live-read r1065",
    # ---- P5b extraction count faces ----
    "# block's own W242..W258 legs (17 rows) do NOT enter the estate path;",
    "# after extraction, fresh W242..W259 legs (18 rows) are added,",
    "# parity = 118 rows (W138..W206 + W211..W259). Zero assumption zero risk.",
    "# block's own W242..W258 legs (17) are EXCLUDED from the estate path per the",
    "# prereg mandate; the W260 block appends fresh W242..W259 legs (18,",
    "# machine-derived from the LIVE pf registry at freeze time) -> 118 parity",
    "m242", "W242 leg boundary",
    "range(242, 260)",
    '"    #     physical bytes; the W260 block\'s own W242..W258 legs (17) are",',
    '"    #     W242..W259 legs (18) added, machine-derived from the live pf",',
    '"    #     registry at freeze time -> 118 parity rows (W138..W206+W211..W259).",',
    '"    #     W211..W241 legs (31) extracted verbatim from the OWN W259 block",',
    "kept segment not W211..W241 thirty-one legs",
    "dropped segment not W242..W258 seventeen legs",
    "legs segment not W211..W258 forty-eight legs",
    "!= 117 (69 estate + W211..W258 legs 48)",
    "!= 116 (69 estate + W211..W257 legs 47)",
    "fresh_legs_row_asserts", '+ legs_kept.count("assert pf.N1_BANDS[") + 18,',
    '"fresh_legs_row_asserts": 18,',
    # ---- P5c band literal ----
    'assert (a_lo, a_hi) == (587_301, 589_300) and (b_lo, b_hi) == (589_301, 589_500), \\',
    # ---- P5d ordinal/leg0 faces ----
    'assert len(owner_rows_live) == 249 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 79, \\',
    "(expect 249/129/79 PRE-splice post-W259 registration",
    '# receipt leg0 face owner_rows=249 / bmc_rows=79 /',
    "-> owner rows 249 + candidate = 250th EXACT; bm-c rows 79 +",
    "# candidate = 80th EXACT -- bm-c own-seat continuity face (bm-c published the",
    "freeze-time live face owner rows 249 + candidate = 250th EXACT",
    "freeze-time live derive bmc rows 79 + candidate 80th EXACT per r587/r359",
    "post-W259 registration: bm-c rows 79 + candidate = 80th owned",
    '"probe_receipt_bmc_ordinal_face": 80,',
    'f"W260+W255..W246 finalize products present "',
    # ---- P5f date face ----
    "_w260bmc_20261017_probe_receipt.json",
    "_w261bmc_20261017_probe_receipt.json",
    # ---- output-gate faces (raw T0 forms; post-blanket they roll one era) ----
    "range(16, 260)", "range(17, 260)", "if w < 260)", "if w < 259)",
    "list(range(211, 259)),", "list(range(211, 242))", "list(range(242, 259)),",
    "arith_a260", "arith_b260", "n1_w260", "n1w260", "PERPETUAL-N1-W260",
    '_w260bmc', "w244_a", "w245_a", "estate 69", "= 118 rows", "118 parity",
    "TENTH consecutive above-own-A", "NINTH consecutive A-hop",
    "ELEVENTH consecutive above-own-A", "TENTH consecutive A-hop",
    "W261p_A_naive", "W261p_B_first_clean", "W262p_A_naive",
    "W257_W258_W259_bands_respected_A", "W258_W259_W260_bands_respected_A",
    "B_base_above_W259_tail", "B_base_above_W260_tail",
    "A_staircase_hop_past_W259_B", "A_staircase_hop_past_W260_B",
    "hashlib.sha256", "hashlib.sha259", "hashlib.sha260",
    "EIGHTIETH", "TWO HUNDRED AND SIXTIETH", "bmc_ordinal=80", "80th own wave",
    "250th", "251st", "249/129/79", "250/129/80",
    "996,335", "569,920", "996_335", "569_920",
    "cf23c4553", "03ab504d7", "MSG-20261017-1225-bmc-w261-seat",
    "119 parity", "= 119 rows",
    "m243", "list(range(211, 243))", "list(range(243, 260)),", "range(243, 261)",
    "kept segment not W211..W242 thirty-two legs",
    "dropped segment not W243..W259 seventeen legs",
    "legs segment not W211..W259 forty-nine legs",
    "!= 118 (69 estate + W211..W259 legs 49)",
    # ---- band-window faces (S260 true forms + prior-era leftovers + new-era) ----
    "587_301..589_300", "589_301..589_500", "587_101..589_100", "587_301..587_500",
    "587_300", "589_300",
    "585_101..587_100", "587_101..587_300", "584_901..586_900", "584_901..585_100",
    "585_101..585_300", "585_100", "587_100", "584_901", "585_101",
    "589_501..591_500", "591_501..591_700", "589_501..589_700", "589_500", "591_500",
    "A naive 589301..591300 CLEAN", "B naive 589501..589700 hops=0 CLEAN at naive, first-clean 589501..589700 BUT",
    "naive A window start 589_301 lands INSIDE the registered W260 B band 589_301..589_500",
    "A naive 587101..589100 CLEAN", "B naive 587301..587500 hops=0 CLEAN at naive, first-clean 587301..587500 BUT",
    "naive A window start 587_101 lands INSIDE the registered W259 B band 587_101..587_300",
    "A naive 591501..593500 CLEAN", "B naive 591701..591900 hops=0 CLEAN at naive, first-clean 591701..591900 BUT",
    "naive A window start 591_501 lands INSIDE the registered W261 B band 591_501..591_700",
]

rows = []
for n in NEEDLES:
    rows.append("%d\t%s" % (T0.count(n), n))
io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(rows) + "\n")
print("needle preflight: counted %d faces -> %s" % (len(NEEDLES), OUT))
