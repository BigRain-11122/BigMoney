# -*- coding: utf-8 -*-
# r1068 bm-c: W262 splice-editor needle-count pre-flight probe (canon-clone of _w261bmc_editor_needle_preflight.py).
# Measures every candidate needle face on T0 = the COMMITTED W261 freeze-edits script
# (results/_w261bmc_freeze_edits.py @ HEAD, blob 36cccfb736c7d56ca3dceac5d85651eef6da993d). Output: results/_w262bmc_editor_needle_counts.txt
# ("count<TAB>needle" per line). E262 rep()/chunk() floors must equal these measured counts. Zero transcription.
import io, subprocess

SRC = "results/_w261bmc_freeze_edits.py"
OUT = "results/_w262bmc_editor_needle_counts.txt"
blob_wt = subprocess.run(["git", "hash-object", SRC], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w261bmc_freeze_edits.py"], capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head == "36cccfb736c7d56ca3dceac5d85651eef6da993d", f"SRC blob drift: wt={blob_wt} head={blob_head}"
T0 = io.open(SRC, encoding="utf-8", newline="").read()

NEEDLES = [
    # ---- P1 structural ----
    "(257, 256, 255, 254, 253, 252, 251, 250, 249, 248)",
    "range(209, 262)",
    'def fmt(n):  # 589501 -> "589_501"',
    # ---- P5a r-window / ledger / ordinal faces (S261 true forms) ----
    "2026-10-17 13:4x bm-c r1067 freeze window",
    "r1066", "r1065", "r1067", "r1064", "r1063",
    "W260 finalize one-pass bm-c r1065 window closeout 12:2x",
    "r1065 splice window",
    "authored 12:5x",
    "996_335", "569_920", "996,335", "569,920",
    "bmc_ordinal=81", "EIGHTY-FIRST", "TWO HUNDRED AND SIXTY-FIRST",
    "forty-ninth consecutive", "81st own wave",
    "MSG-20261017-1225-bmc-w261-seat", "cf23c4553", "03ab504d7",
    "transitive window W248..W257 checked",
    "engine_owner==bm-c rows 80 + candidate",
    "saturation_engine.py status live-read r1066",
    # ---- P5b extraction count faces ----
    "# block's own W243..W259 legs (17 rows) do NOT enter the estate path;",
    "# after extraction, fresh W243..W260 legs (18 rows) are added,",
    "# parity = 119 rows (W138..W206 + W211..W260). Zero assumption zero risk.",
    "# block's own W243..W259 legs (17) are EXCLUDED from the estate path per the",
    "# prereg mandate; the W261 block appends fresh W243..W260 legs (18,",
    "# machine-derived from the LIVE pf registry at freeze time) -> 119 parity",
    "m243", "W243 leg boundary",
    "range(243, 261)",
    '"    #     physical bytes; the W261 block\'s own W243..W259 legs (17) are",',
    '"    #     W243..W260 legs (18) added, machine-derived from the live pf",',
    '"    #     registry at freeze time -> 119 parity rows (W138..W206+W211..W260).",',
    '"    #     W211..W242 legs (32) extracted verbatim from the OWN W260 block",',
    "kept segment not W211..W242 thirty-two legs",
    "dropped segment not W243..W259 seventeen legs",
    "legs segment not W211..W259 forty-nine legs",
    "!= 118 (69 estate + W211..W259 legs 49)",
    "!= 117 (69 estate + W211..W258 legs 48)",
    "fresh_legs_row_asserts", '+ legs_kept.count("assert pf.N1_BANDS[") + 18,',
    '"fresh_legs_row_asserts": 18,',
    # ---- P5c band literal ----
    'assert (a_lo, a_hi) == (589_501, 591_500) and (b_lo, b_hi) == (591_501, 591_700), \\',
    # ---- P5d ordinal/leg0 faces ----
    'assert len(owner_rows_live) == 250 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 80, \\',
    "(expect 250/129/80 PRE-splice post-W260 registration",
    '# receipt leg0 face owner_rows=250 / bmc_rows=80 /',
    "-> owner rows 250 + candidate = 251st EXACT; bm-c rows 80 +",
    "# candidate = 81st EXACT -- bm-c own-seat continuity face (bm-c published the",
    "freeze-time live face owner rows 250 + candidate = 251st EXACT",
    "freeze-time live derive bmc rows 80 + candidate 81st EXACT per r587/r359",
    "post-W260 registration: bm-c rows 80 + candidate = 81st owned",
    '"probe_receipt_bmc_ordinal_face": 81,',
    'f"W261+W256..W247 finalize products present "',
    # ---- P5f date face ----
    "_w261bmc_20261017_probe_receipt.json",
    "_w262bmc_20261017_probe_receipt.json",
    # ---- output-gate faces (raw T0 forms; post-blanket they roll one era) ----
    "range(16, 261)", "range(17, 261)", "if w < 261)", "if w < 260)",
    "list(range(211, 260)),", "list(range(211, 243))", "list(range(243, 260)),",
    "arith_a261", "arith_b261", "n1_w261", "n1w261", "PERPETUAL-N1-W261",
    '_w261bmc', "w244_a", "w245_a", "estate 69", "= 119 rows", "119 parity",
    "TENTH consecutive above-own-A", "NINTH consecutive A-hop",
    "ELEVENTH consecutive above-own-A", "TENTH consecutive A-hop",
    "W262p_A_naive", "W263p_A_naive", "W261p_A_naive",
    "W258_W259_W260_bands_respected_A", "W259_W260_W261_bands_respected_A",
    "B_base_above_W260_tail", "B_base_above_W261_tail",
    "A_staircase_hop_past_W260_B", "A_staircase_hop_past_W261_B",
    "hashlib.sha256", "hashlib.sha260", "hashlib.sha261",
    "EIGHTY-FIRST", "TWO HUNDRED AND SIXTY-FIRST", "bmc_ordinal=81", "81st own wave",
    "251st", "252nd", "250/129/80", "251/129/81",
    "998,535", "572,120", "998_535", "572_120",
    "693e926b1", "32d28ffb3", "MSG-20261017-1425-bmc-w262-seat",
    "120 parity", "= 120 rows",
    "m244", "list(range(211, 244))", "list(range(244, 261)),", "range(244, 262)",
    "kept segment not W211..W243 thirty-three legs",
    "dropped segment not W244..W260 seventeen legs",
    "legs segment not W211..W260 fifty legs",
    "!= 119 (69 estate + W211..W260 legs 50)",
    # ---- band-window faces (S261 true forms + prior-era leftovers + new-era) ----
    "589_501..591_500", "591_501..591_700", "589_301..591_300", "589_501..589_700",
    "589_500", "591_500",
    "587_301..589_300", "589_301..589_500", "585_101..587_100", "587_301..587_500",
    "587_300", "589_300", "587_101..589_100", "587_101..587_300",
    "591_701..593_700", "593_701..593_900", "591_701..591_900", "591_700", "593_700",
    "A naive 591501..593500 CLEAN", "B naive 591701..591900 hops=0 CLEAN at naive, first-clean 591701..591900 BUT",
    "naive A window start 591_501 lands INSIDE the registered W261 B band 591_501..591_700",
    "A naive 589301..591300 CLEAN", "B naive 589501..589700 hops=0 CLEAN at naive, first-clean 589501..589700 BUT",
    "naive A window start 589_301 lands INSIDE the registered W260 B band 589_301..589_500",
    "A naive 593701..595700 CLEAN", "B naive 593901..594100 hops=0 CLEAN at naive, first-clean 593901..594100 BUT",
    "naive A window start 593_701 lands INSIDE the registered W262 B band 593_701..593_900",
]

rows = []
for n in NEEDLES:
    rows.append("%d\t%s" % (T0.count(n), n))
io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(rows) + "\n")
print("needle preflight: counted %d faces -> %s" % (len(NEEDLES), OUT))
