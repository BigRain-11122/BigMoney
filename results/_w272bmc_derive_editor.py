# -*- coding: utf-8 -*-
# r1100 bm-c: derive results/_w272bmc_freeze_edits.py from the committed W271
# freeze-edits canon (results/_w271bmc_freeze_edits.py, bm-c r1097 splice
# window 7dd091eef1, proven live-fire: W271 five-face splice + engine
# self-burn 12/12 appends a035552321+037445477b + finalize one-pass ledger
# 1,020,535 / K=594,120 + W272 seat published @ origin f608ff1cee r1098,
# machine-verified r1097 closeout e0a21b817d)
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 16th-gen lineage, zero
# transcription: every needle count MEASURED on the canon blob by
# results/_r1100bmc_needle_preflight.py (receipt
# results/_r1100bmc_needle_preflight.json, canon sha256_16 fa19684b280f468c,
# 62,154B, wt==HEAD==origin triple-verified) + final missing-needle sweep in
# the phase-4 residual gates -- r1077 measured-counts law.
# DISCLOSED CANON EOL FACE (benign, carried): core.autocrlf=true re-smudge
# (r1093 pit entry) -- canon + W272 payload files (prereg/probe receipt)
# on disk are the CRLF-smudged forms of their LF origin blobs (norm-eq
# TRUE, prereg blob 23,409B sha256_16 b023511eba80a9bf git-object-verified
# in preflight, disk 23,409B face, raw disk-vs-blob compare FORBIDDEN);
# the editor reads canon raw with newline='' and the executor reads
# text-mode or git-object-level -- zero content impact.
# AGING-TOKEN LAW (E63 anti-drift): frozen faces w244_a/w244_b and
# n3r1_used245 do NOT roll (measured 12/8/3 in canon; carried verbatim,
# anti-drift asserted here; "w244_a holds wave-263 bands" disclosure text
# carries verbatim, measured 4). Band order law: consumers before producers
# (613_501/613_700/611_501/613_500/611_700/613_300 consumed BEFORE the
# 611_301/611_500 producers, else the fresh prior-wave B tokens
# double-transform). Own-first law at every level (W271 before W270;
# 271: {"batch" before 270: {"batch"; WAVE_CONFIGS[271] before [270];
# if w < 271) before if w < 270); ordinal order law: TWENTY-SECOND (B,
# above-own-A) caps roll before TWENTY-FIRST (A, A-hop) -- B-ordinal caps
# first, then A-ordinal caps, else double-transform.
# SETWAVE +1 AGING LAW (r1076-family ROOT CURE, held since r1088): the canon
# carries _set_wave(271) (the healed W271 block face); this editor ages it
# rep('_set_wave(271)','_set_wave(272)',1) -- presence gates
# _set_wave(272):1 / _set_wave(271):0 / _set_wave(270):0 / _set_wave(269):0.
# W272 FACTS (probe receipt results/_w272bmc_20261018_probe_receipt.json,
# committed with the seat @ f608ff1cee r1098): bands A 613_701..615_700
# (TWENTY-FIRST consecutive A-hop, staircase-affects-A, hops=1; naive A
# 613_501..615_500 refused at registered W271 B 613_501..613_700) /
# B 615_701..615_900 (TWENTY-SECOND consecutive above-own-A, own-A
# reservation cascade, hops=1; naive B 613_701..613_900 inside own-A
# window 613_701..615_700); seed_admit FREE x2 (base=613701 span=2000 /
# base=615701 span=200); ordinals owner 261 + candidate = 262nd /
# bm-c rows 90 + candidate = 91st; W271 finalize anchors 1,020,535 /
# K=594,120 (chain +2,200/+2,200 EXACT).
# Window-stamp disambiguation (all r1095 x15 / r1096 x6 contexts measured
# in the preflight receipt): SEAT faces -> r1098 (W272 seat
# MSG-20261018-191x-bmc-w272-seat @ origin f608ff1cee, r1098 seat window);
# SPLICE faces -> r1097 (W271 splice 7dd091eef1); FINALIZE faces -> r1097
# (W271 finalize one-pass 18:4x); PREREG faces -> r1099 (W272 prereg
# c049a57623 authored 19:2x); cycle face -> r1097 closeout 18:4x.
# r1091 W268 出稿双坑预检 honored (W272+ editor authoring law): (a) gone
# 清单禁收裸波号/生产面 token -- 613_501/613_700 (producer-news),
# range(248, 271) (dropped-range news), "if w < 271)" (anti-gate news),
# r1097/TWENTY-FIRST/W273p/n1_w271/w271_/_w271bmc_ (lineage-template
# produced face, count 1)/_w272bmc_/19:2x/authored 19:2x all
# EXCLUDED from the gone list (live produced faces); (b) 折行断言形拆短
# needle -- all count needles kept short-form (no cross-continuation long
# strings).
import io, subprocess, sys

CANON = "results/_w271bmc_freeze_edits.py"
DST = "results/_w272bmc_freeze_edits.py"
LOG = "results/_r1100bmc_derive_editor_log.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w271bmc_freeze_edits.py"],
                           capture_output=True, text=True).stdout.strip()
blob_origin = subprocess.run(["git", "rev-parse", "origin/main:results/_w271bmc_freeze_edits.py"],
                             capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head == blob_origin and len(blob_wt) == 40, \
    f"canon blob drift wt={blob_wt} head={blob_head} origin={blob_origin}"

t = io.open(CANON, encoding="utf-8", newline="").read()
log = [f"S0 canon blob verified {blob_wt[:16]} == HEAD == origin twin (preflight-measured sha256_16 fa19684b280f468c, 62,154B)",
       f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:100]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W272p", "W273p", 13, "p1_proj_prefix")
rep("W272", "W273", 13, "p1_proj_plain")
# bands: W272 registered A 613_701..615_700 (21st A-hop) / B 615_701..615_900
# (22nd above-own-A); naive A 613_501..615_500 refused at registered W271 B
# 613_501..613_700; naive B 613_701..613_900 inside own-A reservation.
# CONSUMERS FIRST (band-order law):
rep("613_501", "615_701", 5, "p1_band_Blo_naiveAlo")
rep("613_700", "615_900", 4, "p1_band_Bhi")
rep("611_501", "613_701", 8, "p1_band_Alo_Bnaivelo")
rep("613_500", "615_700", 9, "p1_band_Ahi")
rep("611_700", "613_900", 2, "p1_band_Bnaivehi")
rep("613_300", "615_500", 2, "p1_band_naiveAhi")
# PRODUCERS LAST (else the fresh 613_501/613_700 tokens double-transform):
rep("611_301", "613_501", 4, "p1_band_priorBlo")
rep("611_500", "613_700", 6, "p1_band_priorBhi")
# ledger/K anchors: W270 finalize facts -> W271 finalize facts (1,020,535/594,120)
rep("1,018,335", "1,020,535", 6, "p1_ledger_prose")
rep("591,920", "594,120", 6, "p1_k_prose")
rep("1_018_335", "1_020_535", 1, "p1_ledger_code")
rep("591_920", "594_120", 1, "p1_k_code")
# lowercase machine-file tokens (own wave first, then upstream wave)
rep("n1_w271", "n1_w272", 4, "p1_n1w271")
rep("n1w271-", "n1w272-", 2, "p1_n1w271dash")
# 12 raw w271_ minus 2 consumed by the n1_w271 rep (n1_w271_results x2)
rep("w271_", "w272_", 10, "p1_lc_w271_")
rep("n1_w270", "n1_w271", 4, "p1_n1w270")
# 93 raw w270_ minus 4 consumed by the n1_w270 rep (n1_w270_results x4)
rep("w270_", "w271_", 89, "p1_lc_w270_")
rep("_w271bmc_", "_w272bmc_", 11, "p1_receiptpath")
rep("MSG-20261018-175x-bmc-w271-seat", "MSG-20261018-191x-bmc-w272-seat", 7, "p1_seat_msg")
rep("87d2697cdc r1095", "f608ff1cee r1098", 1, "p1_seat_origin_hdr")
rep('SEAT_ORIGIN = "87d2697cdc"', 'SEAT_ORIGIN = "f608ff1cee"', 1, "p1_seat_origin_const")
rep("1c814343ed", "7dd091eef1", 1, "p1_lineage_sha")
rep("f75b18c862", "c049a57623", 1, "p1_prereg_sha_ref")
# stale-carried receipt wave field (mechanical +1): 270->271
rep('"wave": 270', '"wave": 271', 1, "p1_receipt_wave")
# header window stamp: this r1100 freeze window
rep("2026-10-18 18:2x bm-c r1097 freeze window", "2026-10-18 20:2x bm-c r1100 freeze window", 1, "p1_hdr_stamp")

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W271", "W272", 96, "p2_own_wave")
rep("W270", "W271", 159, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
# relkey = POST-BLANKET form (the upstream blanket rolled the W270 inside
# "W268_W269_W270_bands_respected" -> "W268_W269_W271"; this rep rolls all
# three positions +1 wave to the W272 probe receipt's relation keys)
rep("W268_W269_W271_bands_respected", "W269_W270_W271_bands_respected", 2, "p3_relkey")
# legs_sec prose + message (W272 extraction: legs W211..W270 = 60)
rep("W211..W269 legs (59)", "W211..W270 legs (60)", 1, "p3_legs_prose")
rep("W211..W269 fifty-nine legs", "W211..W270 sixty legs", 1, "p3_legs_msg")
# legs_sec wave-list range (the count itself rides the p3_count59 short needle
# below -- the assert is line-wrapped in the canon, CRLF continuation)
rep("range(211, 270)", "range(211, 271)", 1, "p3_range_legs")
# dropped faces (W272 extraction drops the W271 block's own W248..W270 = 23 legs)
rep("own W248..W269 legs (22)", "own W248..W270 legs (23)", 4, "p3_dropped_narr")
rep("own W248..W269", "own W248..W270", 1, "p3_dropped_split_hdr")
rep("W248..W269 twenty-two legs", "W248..W270 twenty-three legs", 1, "p3_dropped_fstring")
rep('N1_BANDS[") == 22', 'N1_BANDS[") == 23', 1, "p3_dropped_count")
# fullspan error-string (POST-BLANKET wave face rolled by the upstream
# blanket: "W211..W270 legs 59" -> "W211..W271 legs 59"; count 59->60)
rep("W211..W271 legs 59", "W211..W271 legs 60", 1, "p3_fullspan_fstring")
# fresh legs (W272 block appends fresh W248..W271 = 24 legs; POST-BLANKET
# form -- the own blanket rolled the hi face to the new range end 272;
# count-only roll 23->24, hi rides the blanket = range(248, 272) END EXACT)
rep("W248..W272 legs (23", "W248..W272 legs (24", 4, "p3_fresh_narr")
# block/parity counts: W272 block = 69 estate + 37 kept + 24 fresh = 130
rep("block = 129 rows", "block = 130 rows", 1, "p3_block128")
rep("129 parity rows", "130 parity rows", 1, "p3_parity128")
rep("block parity = 129 rows", "block parity = 130 rows", 1, "p3_blockparity_hdr")
rep('N1_BANDS[") == 128,', 'N1_BANDS[") == 129,', 1, "p3_count127")
rep('!= 128', '!= 129', 1, "p3_fstring127")
rep('N1_BANDS[") == 59', 'N1_BANDS[") == 60', 1, "p3_count58")
rep('"fresh_legs_row_asserts": 23', '"fresh_legs_row_asserts": 24', 1, "p3_receipt_fresh22")
rep('+ 23,', '+ 24,', 1, "p3_receipt_total22")
# ranges (fresh FIRST then dropped-producer, then the cumulative/registry faces)
rep("range(248, 271)", "range(248, 272)", 2, "p3_range_fresh")
rep("range(248, 270)", "range(248, 271)", 1, "p3_range_dropped")
rep("range(16, 271)", "range(16, 272)", 2, "p3_range16")
rep("range(17, 271)", "range(17, 272)", 3, "p3_range17")
rep("range(209, 272)", "range(209, 273)", 2, "p3_range209")
# wave-number gates (own 271->272 FIRST, then anti-gate 270->271)
rep("if w < 271)", "if w < 272)", 5, "p3_wlt270")
rep("if w < 270)", "if w < 271)", 1, "p3_wlt269_antigate")
rep("271 - _lw", "272 - _lw", 2, "p3_legcount")
# fresh-legs loop boundary (number face, blankets do not touch bare numbers)
rep("_w == 270", "_w == 271", 1, "p3_freshmsg_cond")
# cfg/row faces: own 271->272 FIRST (band-faces own-first law), then upstream 270->271
rep("WAVE_CONFIGS[271]", "WAVE_CONFIGS[272]", 2, "p3_wavecfg270_own")
rep("WAVE_CONFIGS[270]", "WAVE_CONFIGS[271]", 3, "p3_wavecfg269")
rep("N1_BANDS[270]", "N1_BANDS[271]", 5, "p3_n1bands269")
rep("get(270)", "get(271)", 1, "p3_get269")
rep("_c270", "_c271", 5, "p3_c269var")
rep('271: {"batch"', '272: {"batch"', 2, "p3_cfg270")
rep('271: {{"batch"', '272: {{"batch"', 1, "p3_cfg270_fstring")
rep('271: {"a"', '272: {"a"', 1, "p3_row270_postgate")
rep('271: {{"a"', '272: {{"a"', 2, "p3_row270_fstring")
rep('270: {"batch"', '271: {"batch"', 2, "p3_cfg269")
rep('270: {"a"', '271: {"a"', 3, "p3_row269")
rep("arith_a271", "arith_a272", 6, "p3_arith_a")
rep("arith_b271", "arith_b272", 6, "p3_arith_b")
rep("(267, 266, 265, 264, 263, 262, 261, 260, 259, 258)",
    "(268, 267, 266, 265, 264, 263, 262, 261, 260, 259)", 2, "p3_transitive_list")
rep("W258..W267", "W259..W268", 1, "p3_transitive_window")
# ordinal faces: owner 260->261, bma 130 held, bmc 89->90 (W272 = 262nd candidate, bm-c 91st own)
rep("len(owner_rows_live) == 260 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 89",
    "len(owner_rows_live) == 261 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 90", 1, "p3_ordinal_assert")
rep("260/130/89", "261/130/90", 1, "p3_ordinal_expect")
rep("owner_rows=260 / bma_rows=130 / bmc_rows=89", "owner_rows=261 / bma_rows=130 / bmc_rows=90", 1, "p3_leg0_face")
rep("rows 260 + candidate = 261st", "rows 261 + candidate = 262nd", 2, "p3_owner259")
rep("; bm-c rows 89 +", "; bm-c rows 90 +", 1, "p3_comment_88split")
rep("bm-c rows 89 + candidate = 90th owned", "bm-c rows 90 + candidate = 91st owned", 1, "p3_receipt_89owned")
rep("# candidate = 90th EXACT", "# candidate = 91st EXACT", 1, "p3_comment_89th")
rep("engine_owner==bm-c rows 89 + candidate", "engine_owner==bm-c rows 90 + candidate", 1, "p3_pr_eo88")
rep("bm-c rows {len(bmc_rows_live)} + candidate (90th own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (91st own wave", 1, "p3_gate0_5_print")
rep("bm-c's 90th own wave", "bm-c's 91st own wave", 2, "p3_89th_own_wave")
rep("NINETIETH owned", "NINETY-FIRST owned", 3, "p3_89th_caps")
rep("TWO HUNDRED AND SEVENTY-FIRST", "TWO HUNDRED AND SEVENTY-SECOND", 3, "p3_wave_caps")
# 7 raw bmc_rows=89 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=89", "bmc_rows=90", 6, "p3_bmc_rows88")
rep('"probe_receipt_bmc_ordinal_face": 89', '"probe_receipt_bmc_ordinal_face": 90', 1, "p3_probe_face_key")
# ordinal narrative: B-ordinal TWENTY-FIRST->TWENTY-SECOND FIRST, then A-ordinal TWENTIETH->TWENTY-FIRST
rep("TWENTY-FIRST", "TWENTY-SECOND", 7, "p3_20_caps")
rep("TWENTIETH", "TWENTY-FIRST", 15, "p3_19_caps")
rep("twenty-first", "twenty-second", 4, "p3_20_lc")
rep("twentieth", "twenty-first", 3, "p3_19_lc")
rep("fifty-ninth", "sixtieth", 2, "p3_58th")
# wave-number narrative faces
rep("wave 271 engine_owner=bm-c", "wave 272 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 271: "', '"wave 272: "', 1, "p3_cfg_waveface")
rep("wave 271 = first free number", "wave 272 = first free number", 1, "p3_mhdr_waveface")
# cycle/lineage window stamps (SEAT->r1098 / SPLICE->r1097 / FINALIZE->r1097, contexts measured)
rep("cycle COMPLETE bm-c r1095 closeout 17:3x", "cycle COMPLETE bm-c r1097 closeout 18:4x", 1, "p3_hdr_complete")
rep("the bm-c r1095 splice window", "the bm-c r1097 splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1095", "own-wave full cycle r1097", 1, "p3_repair_note")
rep("bm-c splice generation r1095 window", "bm-c splice generation r1097 window", 1, "p3_parity_source_note")
rep("verified r1095", "verified r1097", 1, "p3_lineage_verified")
rep("# r1095 splice window", "# r1097 splice window", 1, "p3_lineage_r1093")
rep("(bm-c r1095", "(bm-c r1097", 1, "p3_parity_comment")
rep("finalize one-pass bm-c r1095 closeout, ledger", "finalize one-pass bm-c r1097 closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1095 closeout ledger", "finalize one-pass bm-c r1097 closeout ledger", 1, "p3_finpass_hdr")
rep("(r1095 MSG-", "(r1098 MSG-", 1, "p3_hdr_msgline")
rep("r1095 BEFORE this freeze", "r1098 BEFORE this freeze", 1, "p3_receipt_seatnote")
rep("seat itself r1095; queue-head", "seat itself r1098; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1095, queue-head seat-first supply", "(r1098, queue-head seat-first supply", 1, "p3_pfcomment_seat")
# prereg window map (W271 prereg r1096 window -> W272 prereg r1099 window)
rep("bm-c r1096 window", "bm-c r1099 window", 4, "p3_prereg_window")
rep("# r1096 window", "# r1099 window", 1, "p3_hdr_prereg_window")
rep("r1096 commit", "r1099 commit", 1, "p3_receipt_commit")
# authored stamp (W272 prereg derived 19:2x, committed c049a57623 r1099)
rep("authored 17:5x", "authored 19:2x", 2, "p3_authored_stamp")
# lineage header: canon template identity rolls to the W271 canon
rep("_w270bmc_freeze_edits.py template", "_w271bmc_freeze_edits.py template", 1, "p3_lineage_template")
rep("(R270: ", "(R271: ", 1, "p3_repick")
# r1076-family ROOT CURE +1 aging law (NOT the mechanical 270->272 form)
rep("_set_wave(271)", "_set_wave(272)", 1, "p3_setwave_rootcure")

# ---------- phase 4: frozen-face anti-drift + residual sweeps ----------
assert t.count("w244_a") == 12 and t.count("w244_b") == 8, "aging tokens w244_a/b drift"
assert t.count("n3r1_used245") == 3, "frozen face n3r1_used245 drift"
assert t.count("w244_a holds wave-263 bands") == 4, "aging disclosure text drift"
assert t.count("m211") == 4, "frozen estate boundary marker m211 drift"
assert t.count("593901") == 1, "fmt doc example face drift"
assert t.count("bma rows 129 + candidate 130th") == 1, "carried bma-ordinal note drift"
assert t.count("registered wave below 263 composes") == 2, "carried family-6 comment face drift"
assert t.count("bm-c own-seat continuity") == 2, "carried own-seat continuity face drift"
# kept-legs faces carry verbatim (template split boundary stays W248)
assert t.count("W211..W247 legs (37)") == 2, "kept-legs narr drift"
assert t.count("W211..W247 verbatim (37 legs)") == 1, "kept-legs comment drift"
assert t.count("W211..W247 thirty-seven legs") == 1, "kept-legs fstring drift"
assert t.count('N1_BANDS[") == 37') == 1, "kept count gate drift"
assert t.count("range(211, 248)") == 1 and t.count("range(138, 207)") == 1, "kept/estate range drift"
assert t.count("fourteen-wave") == 8, "carried fourteen-wave seed-gap face drift"
assert t.count("dual-window parity") == 1, "carried dual-window parity face drift"
assert t.count('"machine": "bm-c"') == 1, "carried machine face drift"
assert t.count("derived by the bm-c") == 2, "carried derived-by face drift"
assert t.count("was published AFTER") == 1, "carried published-after face drift"
assert t.count("physical bytes") == 6, "carried physical-bytes face drift"
for gone in ("r1088", "r1089", "r1090", "r1091", "r1092", "r1093", "r1094", "r1095", "r1096",
             "12:3x", "13:1x", "authored 13:1x", "14:1x", "14:4x", "authored 14:4x",
             "13:4x", "14:0x", "15:2x", "15:4x", "16:3x", "authored 16:3x", "17:0x",
             "17:3x", "17:5x", "authored 17:5x", "18:2x",
             "df55e3fab9", "942ebd5885", "dc71ecc3f9", "7b9e9377", "f1ec8231c7",
             "d630d043b9", "8bc7ac759e", "67fe12710c", "d630d043b9 r1091",
             "9f480646f4", "440b07c94b", "3bb8b9308e", "87d2697cdc", "1c814343ed", "f75b18c862",
             "MSG-20261018-1025-bmc-w267-seat", "MSG-20261018-1229-bmc-w268-seat",
             "MSG-20261018-1407-bmc-w269-seat", "MSG-20261018-1605-bmc-w270-seat",
             "MSG-20261018-175x-bmc-w271-seat",
             "_w266bmc_", "_w267bmc_", "_w268bmc_", "_w269bmc_", "_w270bmc_",
             "w266_", "w267_", "w268_", "w269_", "w270_",
             "n1_w266", "n1_w267", "n1_w268", "n1_w269", "n1_w270",
             "n1w267-", "n1w268-", "n1w269-", "n1w270-", "n1w271-",
             "604_901", "606_900", "605_100", "606_700",
             "604_701", "604_900", "606_901", "607_100",
             "607_101", "609_100", "607_300", "608_900",
             "609_101", "609_300", "609_301", "611_300", "609_500", "611_100",
             "611_301", "611_500", "611_501", "611_700", "613_300", "613_500",
             "602_501", "602_700", "602_701", "602_900", "604_500",
             "600_301", "600_500", "600_700", "602_300", "600_501", "602_500",
             "598_101", "598_300", "598_301", "600_300", "598_500", "600_100",
             "1,007,335", "580,920", "1_007_335", "580_920",
             "1,009,535", "583,120", "1_009_535", "583_120",
             "1,011,735", "585,320", "1_011_735", "585_320",
             "1,013,935", "587,520", "1_013_935", "587_520",
             "1,016,135", "589,720", "1_016_135", "589_720",
             "1,018,335", "591,920", "1_018_335", "591_920",
             "20261017", "W268p", "W269p", "W270p", "W271p", "W272p",
             "W211..W246", "W211..W264", "W247..W264", "own W247..W264",
             "thirty-six", "fifty-fourth", "fifty-three", "fifty-fifth",
             "fifty-five legs", "fifty-six legs", "fifty-sixth", "fifty-seven legs", "fifty-seventh",
             "fifty-eight legs", "fifty-eighth", "fifty-nine legs", "fifty-ninth",
             "PENDING at seat", "waits-upstream face disclosed honest",
             "bma_ordinal", "ONE HUNDRED AND THIRTIETH", "EIGHTY-FIFTH owned",
             "EIGHTY-SIXTH owned", "EIGHTY-SEVENTH owned", "EIGHTY-NINTH owned", "NINETIETH owned",
             "83rd", "84th", "87th", "88th", "89th", "90th",
             "TWO HUNDRED AND SIXTY-SIXTH", "TWO HUNDRED AND SIXTY-SEVENTH",
             "TWO HUNDRED AND SIXTY-EIGHTH", "TWO HUNDRED AND SIXTY-NINTH",
             "TWO HUNDRED AND SEVENTIETH", "TWO HUNDRED AND SEVENTY-FIRST",
             "== 123", "!= 123", 'N1_BANDS[") == 124,', '!= 124',
             'N1_BANDS[") == 125,', '!= 125', 'N1_BANDS[") == 56',
             'N1_BANDS[") == 19', 'N1_BANDS[") == 20',
             'N1_BANDS[") == 126,', '!= 126', 'N1_BANDS[") == 57',
             'N1_BANDS[") == 127,', '!= 127', 'N1_BANDS[") == 58', 'N1_BANDS[") == 21',
             'N1_BANDS[") == 128,', '!= 128', 'N1_BANDS[") == 59', 'N1_BANDS[") == 22',
             "N1_BANDS[246] ==", "N1_BANDS\\[246\\]", "m246",
             "N1_BANDS[247] ==", "N1_BANDS\\[247\\]", "m247",
             "FOURTEENTH", "fourteenth", "fifteenth", "FIFTEENTH",
             "rows 255 + candidate", "bmc_rows=84", "bmc_rows=85", "rows 254 + candidate",
             "rows 257 + candidate", "bmc_rows=86", "bmc_rows=87", "bmc_rows=88", "bmc_rows=89",
             "254/130/83", "owner_rows=254",
             "len(owner_rows_live) == 254", "len(owner_rows_live) == 256",
             "len(owner_rows_live) == 257", "len(owner_rows_live) == 258", "256/130/85",
             "owner_rows=256 / bma_rows=130 / bmc_rows=85",
             "owner_rows=257 / bma_rows=130 / bmc_rows=86",
             "owner_rows=258 / bma_rows=130 / bmc_rows=87", "257/130/86", "258/130/87",
             "rows 258 + candidate", "rows 259 + candidate = 260th",
             "len(owner_rows_live) == 259", "259/130/88",
             "owner_rows=259 / bma_rows=130 / bmc_rows=88",
             "rows 260 + candidate = 261st", "len(owner_rows_live) == 260", "260/130/89",
             "owner_rows=260 / bma_rows=130 / bmc_rows=89", "expect 260/130/89",
             "(R265: ", "(R266: ", "(R267: ", "(R268: ", "(R269: ", "(R270: ",
             "_w == 265", "_w == 266", "_w == 267", "_w == 268", "_w == 269", "_w == 270",
             "bm-a five-face freeze upstream seat", "bm-a (upstream seat honored)",
             "owner=bm-a seat honored", "(bm-a seat owner expected)",
             "20:5x", "22:4x", "10:2x", "11:2x",
             "editor template", "authored 09:0x", "authored 10:5x",
             "W263_W264_W265_bands_respected", "W264_W265_W267_bands_respected",
             "W265_W266_W267_bands_respected", "W266_W267_W268_bands_respected",
             "W266_W267_W269_bands_respected", "W267_W268_W269_bands_respected",
             "W268_W269_W270_bands_respected",
             "range(211, 247)", "range(211, 265)", "range(247, 265)",
             "range(247, 266)", "range(16, 266)", "range(17, 266)", "range(209, 268)",
             "range(211, 266)", "range(248, 266)", "range(16, 267)", "range(17, 267)",
             "range(211, 267)", "range(248, 267)", "range(16, 268)", "range(17, 268)",
             "range(209, 269)", "range(211, 268)", "range(248, 268)",
             "range(16, 269)", "range(17, 269)", "range(209, 270)",
             "range(211, 269)", "range(248, 269)", "range(16, 270)", "range(17, 270)",
             "range(209, 271)", "range(211, 270)", "range(248, 270)",
             "range(16, 271)", "range(17, 271)", "range(209, 272)",
             "if w < 265)", "if w < 266)", "if w < 267)", "if w < 268)", "if w < 269)", "if w < 270)",
             '"wave": 265', '"wave": 266', '"wave": 267', '"wave": 268', '"wave": 269', '"wave": 270',
             "SIXTEENTH", "sixteenth", "SEVENTEENTH", "seventeenth", "EIGHTEENTH", "eighteenth",
             "NINETEENTH", "nineteenth", "TWENTIETH", "twentieth",
             "arith_a267", "arith_b267", "arith_a268", "arith_b268", "arith_a269", "arith_b269",
             "arith_a270", "arith_b270", "arith_a271", "arith_b271",
             "block = 125 rows", "125 parity rows", "block parity = 121 rows",
             "block = 126 rows", "126 parity rows", "block parity = 126 rows",
             "block = 127 rows", "127 parity rows", "block parity = 127 rows",
             "block = 128 rows", "128 parity rows", "block parity = 128 rows",
             "block = 129 rows", "129 parity rows", "block parity = 129 rows",
             '"fresh_legs_row_asserts": 19', '"fresh_legs_row_asserts": 20', '"fresh_legs_row_asserts": 21',
             '"fresh_legs_row_asserts": 22', '"fresh_legs_row_asserts": 23',
             "+ 19,", "+ 20,", "+ 21,", "+ 22,", "+ 23,",
             "own W248..W265", "own W248..W266", "own W248..W267", "own W248..W268", "own W248..W269",
             "W248..W265 eighteen legs",
             "W248..W266 nineteen legs", "W248..W267 twenty legs",
             "W248..W268 twenty-one legs", "own W248..W268 legs (21)",
             "W211..W265 legs (55)", "W211..W266 legs (56)",
             "W211..W267 legs 56", "W211..W267 legs (57)", "W211..W267 fifty-seven legs",
             "W211..W268 legs 57", "W211..W269 legs 57", "W248..W269 legs (21",
             "W211..W268 legs (58)", "W211..W268 fifty-eight legs", "W211..W269 legs 58",
             "W211..W269 legs (59)", "W211..W269 fifty-nine legs", "W211..W270 legs 59",
             "W248..W270 legs (22", "W248..W271 legs (23",
             "len(bmc_rows_live)} + candidate (87th own wave",
             "len(bmc_rows_live)} + candidate (88th own wave",
             "len(bmc_rows_live)} + candidate (89th own wave",
             "len(bmc_rows_live)} + candidate (90th own wave",
             "EIGHTY-EIGHTH owned", "bm-c's 87th own wave", "bm-c's 88th own wave", "bm-c's 89th own wave",
             "bm-c's 90th own wave",
             "engine_owner==bm-c rows 86 + candidate", "engine_owner==bm-c rows 87 + candidate",
             "engine_owner==bm-c rows 88 + candidate", "engine_owner==bm-c rows 89 + candidate",
             "268 - _lw", "269 - _lw", "270 - _lw", "271 - _lw",
             "_set_wave(268)", "_set_wave(267)", "_set_wave(266)", "_set_wave(269)", "_set_wave(270)",
             "_set_wave(271)",
             "942ebd5885 r1089"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
    'MSG-20261018-191x-bmc-w272-seat': 7, "f608ff1cee": 2, "_w272bmc_": 11,
    "20261018": 17, "c049a57623": 1, "7dd091eef1": 1,
    "615_701": 5, "615_900": 4, "613_701": 8, "615_700": 9,
    "613_900": 2, "615_500": 2, "613_501": 4, "613_700": 6,
    "1,020,535": 6, "594,120": 6, "1_020_535": 1, "594_120": 1,
    '272: {"batch"': 2, '271: {"batch"': 2, '270: {"batch"': 0,
    '272: {{"batch"': 1, '272: {"a"': 1, '271: {"a"': 3, '272: {{"a"': 2,
    "range(248, 272)": 2, "range(209, 273)": 2, "range(16, 272)": 2,
    "range(17, 272)": 3, "range(211, 248)": 1, "range(211, 271)": 1,
    "range(248, 271)": 1, "range(138, 207)": 1,
    "if w < 272)": 5, "if w < 271)": 1, "272 - _lw": 2,
    "m248": 4, "m211": 4, "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
    "WAVE_CONFIGS[272]": 2, "WAVE_CONFIGS[271]": 3, "N1_BANDS[271]": 5,
    "get(271)": 1, "_c271": 5,
    "arith_a272": 6, "arith_b272": 6,
    "(268, 267, 266, 265, 264, 263, 262, 261, 260, 259)": 2, "W259..W268": 1,
    "len(owner_rows_live) == 261": 1, "261/130/90": 1, "bmc_rows=90": 7,
    "rows 261 + candidate = 262nd": 2, "bm-c rows 90 + candidate = 91st owned": 1,
    "NINETY-FIRST owned": 3, "TWO HUNDRED AND SEVENTY-SECOND": 3,
    "TWENTY-SECOND": 7, "TWENTY-FIRST": 15, "twenty-second": 4, "twenty-first": 3,
    "W269_W270_W271_bands_respected": 2, "W273p": 13, "W273": 26,
    "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
    "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
    "W272 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
    "the bm-c r1097 splice window": 2,
    "bm-c own seat executed at the bm-c r1097 splice window": 1,
    "finalize one-pass bm-c r1097": 2,
    "authored 19:2x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
    "cycle COMPLETE bm-c r1097 closeout 18:4x": 1,
    "verified r1097": 1, "(R271: ": 1, "_w == 271": 1,
    "wave 272 engine_owner=bm-c": 1, '"wave 272: "': 1,
    "wave 272 = first free number": 1, "sixtieth": 2, "sixty legs": 1,
    'N1_BANDS[") == 129,': 1, '!= 129': 1, 'N1_BANDS[") == 60': 1,
    'N1_BANDS[") == 37': 1, 'N1_BANDS[") == 23': 1,
    "W211..W270 legs (60)": 1, "W211..W271 legs 60": 1,
    "own W248..W270 legs (23)": 4, "own W248..W270": 5, "W248..W272 legs (24": 4,
    "block = 130 rows": 1, "130 parity rows": 1, "block parity = 130 rows": 1,
    "bm-c r1099 window": 4, "# r1099 window": 1, "r1099 commit": 1,
    "bm-c splice generation r1097 window": 1, "(bm-c r1097": 1,
    "_w271bmc_freeze_edits.py template": 1,
    "PERPETUAL_N1_W272_PREREG": 8, "PERPETUAL-N1-W272": 7,
    "n1_w272": 4, "n1_w271": 4, "n1w272-": 2,
    "n1_w272_results.json": 2, "n1_w271_results.json": 4,
    "W272 materializer face": 4, "W271 materializer face": 1,
    "W270 finalize product": 0, "W271 finalize product": 4, "W272 block": 4,
    "engine_owner==bm-c rows 90 + candidate": 1,
    "# candidate = 91st EXACT": 1, "; bm-c rows 90 +": 1,
    "bm-c rows {len(bmc_rows_live)} + candidate (91st own wave": 1,
    "bm-c's 91st own wave": 2, "owner_rows=261 / bma_rows=130 / bmc_rows=90": 1,
    '"probe_receipt_bmc_ordinal_face": 90': 1,
    "fourteen-wave": 8, "post-W271-REGISTERED": 8,
    "anchors W271 1,020,535 / K=594,120 at draft": 1,
    "dual-window parity": 1, "W273 walk": 1,
    "sixtieth consecutive": 2, '"wave": 271': 1,
    "bma rows 129 + candidate 130th": 1,
    "registered wave below 263 composes": 2,
    "PRE-W272-splice": 1, "post-W271 registration": 2,
    "expect 261/130/90": 1,
    "_set_wave(272)": 1, "_set_wave(271)": 0, "_set_wave(270)": 0, "_set_wave(269)": 0,
    "_set_wave(2)": 1,
    "2026-10-18 20:2x bm-c r1100 freeze window": 1,
    "derived by the bm-c": 2,
}
for k, v in must_have.items():
    c = t.count(k)
    assert c == v, f"presence gate FAIL: {k!r} count {c} != {v}"
log.append("phase5 presence gates PASS")
io.open(DST, "w", encoding="utf-8", newline="").write(t)
import py_compile
py_compile.compile(DST, doraise=True)
log.append(f"DST written {len(t.encode('utf-8'))} bytes + py_compile OK")
io.open(LOG, "w", encoding="utf-8", newline="").write("\n".join(log) + "\n")
print("\n".join(log[-4:]))
print("DERIVE OK ->", DST)
