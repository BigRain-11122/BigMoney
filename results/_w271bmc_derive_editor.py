# -*- coding: utf-8 -*-
# r1097 bm-c: derive results/_w271bmc_freeze_edits.py from the committed W270
# freeze-edits canon (results/_w270bmc_freeze_edits.py, bm-c r1095 splice
# window 1c814343ed, proven live-fire: W270 five-face splice + engine
# self-burn 12/12 appends 6c1aee751d+ae98b97a10 + finalize one-pass ledger
# 1,018,335 / K=591,920 + W271 seat published @ origin 87d2697cdc r1095
# dead-window absorbed per bm-c lineage, machine-verified r1096 closeout)
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 15th-gen lineage, zero
# transcription: every needle count MEASURED on the canon blob by
# results/_r1097bmc_needle_preflight.py (receipt
# results/_r1097bmc_needle_preflight.json, canon sha256_16 fbbcc7d68a9afcbf,
# 62,142B, wt==HEAD==origin triple-verified) + final missing-needle sweep in
# the phase-4 residual gates -- r1077 measured-counts law.
# DISCLOSED CANON EOL FACE (benign, carried): core.autocrlf=true re-smudge
# (r1093 pit entry) -- canon + W271 payload files (prereg/probe receipt)
# on disk are the CRLF-smudged forms of their LF origin blobs (norm-eq
# TRUE, prereg blob 23,336B sha256_16 f8b4a755d81bfbe5 git-object-verified
# in preflight, disk 23,399B CRLF form, raw disk-vs-blob compare FORBIDDEN);
# the editor reads canon raw with newline='' and the executor reads
# text-mode or git-object-level -- zero content impact.
# AGING-TOKEN LAW (E63 anti-drift): frozen faces w244_a/w244_b and
# n3r1_used245 do NOT roll (measured 12/8/3 in canon; carried verbatim,
# anti-drift asserted here; "w244_a holds wave-263 bands" disclosure text
# carries verbatim, measured 4). Band order law: consumers before producers
# (611_301/611_500/609_301/611_300/609_500/611_100 consumed BEFORE the
# 609_101/609_300 producers, else the fresh prior-wave B tokens
# double-transform). Own-first law at every level (W270 before W269;
# 270: {"batch" before 269: {"batch"; WAVE_CONFIGS[270] before [269];
# if w < 270) before if w < 269); ordinal order law: TWENTY-FIRST (B,
# above-own-A) caps roll before TWENTIETH (A, A-hop) -- B-ordinal caps
# first, then A-ordinal caps, else double-transform.
# SETWAVE +1 AGING LAW (r1076-family ROOT CURE, held since r1088): the canon
# carries _set_wave(270) (the healed W270 block face); this editor ages it
# rep('_set_wave(270)','_set_wave(271)',1) -- presence gates
# _set_wave(271):1 / _set_wave(270):0 / _set_wave(269):0 / _set_wave(268):0.
# W271 FACTS (probe receipt results/_w271bmc_20261018_probe_receipt.json,
# committed with the seat @ 87d2697cdc r1095): bands A 611_501..613_500
# (TWENTIETH consecutive A-hop, staircase-affects-A, hops=1; naive A
# 611_301..613_300 refused at registered W270 B 611_301..611_500) /
# B 613_501..613_700 (TWENTY-FIRST consecutive above-own-A, own-A
# reservation cascade, hops=1; naive B 611_501..611_700 inside own-A
# window 611_501..613_500); seed_admit FREE x2 (base=611501 span=2000 /
# base=613501 span=200); ordinals owner 260 + candidate = 261st /
# bm-c rows 89 + candidate = 90th; W270 finalize anchors 1,018,335 /
# K=591,920 (chain +2,200/+2,200 EXACT).
# Window-stamp disambiguation (all r1093 x10 / r1094 x11 contexts measured
# in the preflight receipt): SEAT faces -> r1095 (W271 seat
# MSG-20261018-175x-bmc-w271-seat @ origin 87d2697cdc, r1095 seat window);
# SPLICE faces -> r1095 (W270 splice 1c814343ed); FINALIZE faces -> r1095
# (W270 finalize one-pass 17:3x); PREREG faces -> r1096 (W271 prereg
# f75b18c862 authored 17:5x); cycle face -> r1095 closeout 17:3x.
# r1091 W268 出稿双坑预检 honored (W271+ editor authoring law): (a) gone
# 清单禁收裸波号/生产面 token -- 611_301/611_500 (producer-news),
# range(248, 270) (dropped-range news), "if w < 270)" (anti-gate news),
# r1095/TWENTIETH/W272p/n1_w271/w271_/n1w271-/_w271bmc_ all EXCLUDED from
# the gone list (live produced faces); (b) 折行断言形拆短 needle -- all
# count needles kept short-form (no cross-continuation long strings).
import io, subprocess, sys

CANON = "results/_w270bmc_freeze_edits.py"
DST = "results/_w271bmc_freeze_edits.py"
LOG = "results/_r1097bmc_derive_editor_log.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w270bmc_freeze_edits.py"],
                           capture_output=True, text=True).stdout.strip()
blob_origin = subprocess.run(["git", "rev-parse", "origin/main:results/_w270bmc_freeze_edits.py"],
                             capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head == blob_origin and len(blob_wt) == 40, \
    f"canon blob drift wt={blob_wt} head={blob_head} origin={blob_origin}"

t = io.open(CANON, encoding="utf-8", newline="").read()
log = [f"S0 canon blob verified {blob_wt[:16]} == HEAD == origin twin (preflight-measured sha256_16 fbbcc7d68a9afcbf, 62,142B)",
       f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:100]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W271p", "W272p", 13, "p1_proj_prefix")
rep("W271", "W272", 13, "p1_proj_plain")
# bands: W271 registered A 611_501..613_500 (20th A-hop) / B 613_501..613_700
# (21st above-own-A); naive A 611_301..613_300 refused at registered W270 B
# 611_301..611_500; naive B 611_501..611_700 inside own-A reservation.
# CONSUMERS FIRST (band-order law):
rep("611_301", "613_501", 5, "p1_band_Blo_naiveAlo")
rep("611_500", "613_700", 4, "p1_band_Bhi")
rep("609_301", "611_501", 8, "p1_band_Alo_Bnaivelo")
rep("611_300", "613_500", 9, "p1_band_Ahi")
rep("609_500", "611_700", 2, "p1_band_Bnaivehi")
rep("611_100", "613_300", 2, "p1_band_naiveAhi")
# PRODUCERS LAST (else the fresh 611_301/611_500 tokens double-transform):
rep("609_101", "611_301", 4, "p1_band_priorBlo")
rep("609_300", "611_500", 6, "p1_band_priorBhi")
# ledger/K anchors: W269 finalize facts -> W270 finalize facts (1,018,335/591,920)
rep("1,016,135", "1,018,335", 6, "p1_ledger_prose")
rep("589,720", "591,920", 6, "p1_k_prose")
rep("1_016_135", "1_018_335", 1, "p1_ledger_code")
rep("589_720", "591_920", 1, "p1_k_code")
# lowercase machine-file tokens (own wave first, then upstream wave)
rep("n1_w270", "n1_w271", 4, "p1_n1w270")
rep("n1w270-", "n1w271-", 2, "p1_n1w270dash")
# 12 raw w270_ minus 2 consumed by the n1_w270 rep (n1_w270_results x2)
rep("w270_", "w271_", 10, "p1_lc_w270_")
rep("n1_w269", "n1_w270", 4, "p1_n1w269")
# 93 raw w269_ minus 4 consumed by the n1_w269 rep (n1_w269_results x4)
rep("w269_", "w270_", 89, "p1_lc_w269_")
rep("_w270bmc_", "_w271bmc_", 11, "p1_receiptpath")
rep("MSG-20261018-1605-bmc-w270-seat", "MSG-20261018-175x-bmc-w271-seat", 7, "p1_seat_msg")
rep("9f480646f4 r1094", "87d2697cdc r1095", 1, "p1_seat_origin_hdr")
rep('SEAT_ORIGIN = "9f480646f4"', 'SEAT_ORIGIN = "87d2697cdc"', 1, "p1_seat_origin_const")
rep("440b07c94b", "1c814343ed", 1, "p1_lineage_sha")
rep("3bb8b9308e", "f75b18c862", 1, "p1_prereg_sha_ref")
# stale-carried receipt wave field (mechanical +1): 269->270
rep('"wave": 269', '"wave": 270', 1, "p1_receipt_wave")
# header window stamp: this r1097 freeze window
rep("2026-10-18 17:0x bm-c r1095 freeze window", "2026-10-18 18:2x bm-c r1097 freeze window", 1, "p1_hdr_stamp")

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W270", "W271", 96, "p2_own_wave")
rep("W269", "W270", 159, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
# relkey = POST-BLANKET form (the upstream blanket rolled the W269 inside
# "W267_W268_W269_bands_respected" -> "W267_W268_W270"; this rep rolls all
# three positions +1 wave to the W271 probe receipt's relation keys)
rep("W267_W268_W270_bands_respected", "W268_W269_W270_bands_respected", 2, "p3_relkey")
# legs_sec prose + message (W271 extraction: legs W211..W269 = 59)
rep("W211..W268 legs (58)", "W211..W269 legs (59)", 1, "p3_legs_prose")
rep("W211..W268 fifty-eight legs", "W211..W269 fifty-nine legs", 1, "p3_legs_msg")
# legs_sec wave-list range (the count itself rides the p3_count58 short needle
# below -- the assert is line-wrapped in the canon, CRLF continuation)
rep("range(211, 269)", "range(211, 270)", 1, "p3_range_legs")
# dropped faces (W271 extraction drops the W270 block's own W248..W269 = 22 legs)
rep("own W248..W268 legs (21)", "own W248..W269 legs (22)", 4, "p3_dropped_narr")
rep("own W248..W268", "own W248..W269", 1, "p3_dropped_split_hdr")
rep("W248..W268 twenty-one legs", "W248..W269 twenty-two legs", 1, "p3_dropped_fstring")
rep('N1_BANDS[") == 21', 'N1_BANDS[") == 22', 1, "p3_dropped_count")
# fullspan error-string (POST-BLANKET wave face rolled by the upstream
# blanket: "W211..W269 legs 58" -> "W211..W270 legs 58"; count 58->59)
rep("W211..W270 legs 58", "W211..W270 legs 59", 1, "p3_fullspan_fstring")
# fresh legs (W271 block appends fresh W248..W270 = 23 legs; POST-BLANKET
# form -- the own blanket rolled the hi face to the new range end 271;
# count-only roll 22->23, hi rides the blanket = range(248, 271) END EXACT)
rep("W248..W271 legs (22", "W248..W271 legs (23", 4, "p3_fresh_narr")
# block/parity counts: W271 block = 69 estate + 37 kept + 23 fresh = 129
rep("block = 128 rows", "block = 129 rows", 1, "p3_block127")
rep("128 parity rows", "129 parity rows", 1, "p3_parity127")
rep("block parity = 128 rows", "block parity = 129 rows", 1, "p3_blockparity_hdr")
rep('N1_BANDS[") == 127,', 'N1_BANDS[") == 128,', 1, "p3_count126")
rep('!= 127', '!= 128', 1, "p3_fstring126")
rep('N1_BANDS[") == 58', 'N1_BANDS[") == 59', 1, "p3_count57")
rep('"fresh_legs_row_asserts": 22', '"fresh_legs_row_asserts": 23', 1, "p3_receipt_fresh21")
rep('+ 22,', '+ 23,', 1, "p3_receipt_total21")
# ranges (fresh FIRST then dropped-producer, then the cumulative/registry faces)
rep("range(248, 270)", "range(248, 271)", 2, "p3_range_fresh")
rep("range(248, 269)", "range(248, 270)", 1, "p3_range_dropped")
rep("range(16, 270)", "range(16, 271)", 2, "p3_range16")
rep("range(17, 270)", "range(17, 271)", 3, "p3_range17")
rep("range(209, 271)", "range(209, 272)", 2, "p3_range209")
# wave-number gates (own 270->271 FIRST, then anti-gate 269->270)
rep("if w < 270)", "if w < 271)", 5, "p3_wlt269")
rep("if w < 269)", "if w < 270)", 1, "p3_wlt268_antigate")
rep("270 - _lw", "271 - _lw", 2, "p3_legcount")
# fresh-legs loop boundary (number face, blankets do not touch bare numbers)
rep("_w == 269", "_w == 270", 1, "p3_freshmsg_cond")
# cfg/row faces: own 270->271 FIRST (band-faces own-first law), then upstream 269->270
rep("WAVE_CONFIGS[270]", "WAVE_CONFIGS[271]", 2, "p3_wavecfg269_own")
rep("WAVE_CONFIGS[269]", "WAVE_CONFIGS[270]", 3, "p3_wavecfg268")
rep("N1_BANDS[269]", "N1_BANDS[270]", 5, "p3_n1bands268")
rep("get(269)", "get(270)", 1, "p3_get268")
rep("_c269", "_c270", 5, "p3_c268var")
rep('270: {"batch"', '271: {"batch"', 2, "p3_cfg269")
rep('270: {{"batch"', '271: {{"batch"', 1, "p3_cfg269_fstring")
rep('270: {"a"', '271: {"a"', 1, "p3_row269_postgate")
rep('270: {{"a"', '271: {{"a"', 2, "p3_row269_fstring")
rep('269: {"batch"', '270: {"batch"', 2, "p3_cfg268")
rep('269: {"a"', '270: {"a"', 3, "p3_row268")
rep("arith_a270", "arith_a271", 6, "p3_arith_a")
rep("arith_b270", "arith_b271", 6, "p3_arith_b")
rep("(266, 265, 264, 263, 262, 261, 260, 259, 258, 257)",
    "(267, 266, 265, 264, 263, 262, 261, 260, 259, 258)", 2, "p3_transitive_list")
rep("W257..W266", "W258..W267", 1, "p3_transitive_window")
# ordinal faces: owner 259->260, bma 130 held, bmc 88->89 (W271 = 261st candidate, bm-c 90th own)
rep("len(owner_rows_live) == 259 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 88",
    "len(owner_rows_live) == 260 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 89", 1, "p3_ordinal_assert")
rep("259/130/88", "260/130/89", 1, "p3_ordinal_expect")
rep("owner_rows=259 / bma_rows=130 / bmc_rows=88", "owner_rows=260 / bma_rows=130 / bmc_rows=89", 1, "p3_leg0_face")
rep("rows 259 + candidate = 260th", "rows 260 + candidate = 261st", 2, "p3_owner258")
rep("; bm-c rows 88 +", "; bm-c rows 89 +", 1, "p3_comment_87split")
rep("bm-c rows 88 + candidate = 89th owned", "bm-c rows 89 + candidate = 90th owned", 1, "p3_receipt_88owned")
rep("# candidate = 89th EXACT", "# candidate = 90th EXACT", 1, "p3_comment_88th")
rep("engine_owner==bm-c rows 88 + candidate", "engine_owner==bm-c rows 89 + candidate", 1, "p3_pr_eo87")
rep("bm-c rows {len(bmc_rows_live)} + candidate (89th own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (90th own wave", 1, "p3_gate0_5_print")
rep("bm-c's 89th own wave", "bm-c's 90th own wave", 2, "p3_88th_own_wave")
rep("EIGHTY-NINTH owned", "NINETIETH owned", 3, "p3_88th_caps")
rep("TWO HUNDRED AND SEVENTIETH", "TWO HUNDRED AND SEVENTY-FIRST", 3, "p3_wave_caps")
# 7 raw bmc_rows=88 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=88", "bmc_rows=89", 6, "p3_bmc_rows87")
rep('"probe_receipt_bmc_ordinal_face": 88', '"probe_receipt_bmc_ordinal_face": 89', 1, "p3_probe_face_key")
# ordinal narrative: B-ordinal TWENTIETH->TWENTY-FIRST FIRST, then A-ordinal NINETEENTH->TWENTIETH
rep("TWENTIETH", "TWENTY-FIRST", 7, "p3_19_caps")
rep("NINETEENTH", "TWENTIETH", 15, "p3_18_caps")
rep("twentieth", "twenty-first", 4, "p3_19_lc")
rep("nineteenth", "twentieth", 3, "p3_18_lc")
rep("fifty-eighth", "fifty-ninth", 2, "p3_57th")
# wave-number narrative faces
rep("wave 270 engine_owner=bm-c", "wave 271 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 270: "', '"wave 271: "', 1, "p3_cfg_waveface")
rep("wave 270 = first free number", "wave 271 = first free number", 1, "p3_mhdr_waveface")
# cycle/lineage window stamps (SEAT->r1095 / SPLICE->r1095 / FINALIZE->r1095, contexts measured)
rep("cycle COMPLETE bm-c r1093 closeout 15:4x", "cycle COMPLETE bm-c r1095 closeout 17:3x", 1, "p3_hdr_complete")
rep("the bm-c r1093 splice window", "the bm-c r1095 splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1093", "own-wave full cycle r1095", 1, "p3_repair_note")
rep("bm-c splice generation r1093 window", "bm-c splice generation r1095 window", 1, "p3_parity_source_note")
rep("verified r1093", "verified r1095", 1, "p3_lineage_verified")
rep("# r1093 splice window", "# r1095 splice window", 1, "p3_lineage_r1091")
rep("(bm-c r1093", "(bm-c r1095", 1, "p3_parity_comment")
rep("finalize one-pass bm-c r1093 closeout, ledger", "finalize one-pass bm-c r1095 closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1093 closeout ledger", "finalize one-pass bm-c r1095 closeout ledger", 1, "p3_finpass_hdr")
rep("(r1094 MSG-", "(r1095 MSG-", 1, "p3_hdr_msgline")
rep("r1094 BEFORE this freeze", "r1095 BEFORE this freeze", 1, "p3_receipt_seatnote")
rep("seat itself r1094; queue-head", "seat itself r1095; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1094, queue-head seat-first supply", "(r1095, queue-head seat-first supply", 1, "p3_pfcomment_seat")
# prereg window map (W270 prereg r1094 window -> W271 prereg r1096 window)
rep("bm-c r1094 window", "bm-c r1096 window", 4, "p3_prereg_window")
rep("# r1094 window", "# r1096 window", 1, "p3_hdr_prereg_window")
rep("r1094 commit", "r1096 commit", 1, "p3_receipt_commit")
# authored stamp (W271 prereg derived 17:5x, committed f75b18c862 r1096)
rep("authored 16:3x", "authored 17:5x", 2, "p3_authored_stamp")
# lineage header: canon template identity rolls to the W270 canon
rep("_w269bmc_freeze_edits.py template", "_w270bmc_freeze_edits.py template", 1, "p3_lineage_template")
rep("(R269: ", "(R270: ", 1, "p3_repick")
# r1076-family ROOT CURE +1 aging law (NOT the mechanical 269->271 form)
rep("_set_wave(270)", "_set_wave(271)", 1, "p3_setwave_rootcure")

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
for gone in ("r1088", "r1089", "r1090", "r1091", "r1092", "r1093", "r1094",
             "12:3x", "13:1x", "authored 13:1x", "14:1x", "14:4x", "authored 14:4x",
             "13:4x", "14:0x", "15:2x", "15:4x", "16:3x", "authored 16:3x", "17:0x",
             "df55e3fab9", "942ebd5885", "dc71ecc3f9", "7b9e9377", "f1ec8231c7",
             "d630d043b9", "8bc7ac759e", "67fe12710c", "d630d043b9 r1091",
             "9f480646f4", "440b07c94b", "3bb8b9308e",
             "MSG-20261018-1025-bmc-w267-seat", "MSG-20261018-1229-bmc-w268-seat",
             "MSG-20261018-1407-bmc-w269-seat", "MSG-20261018-1605-bmc-w270-seat",
             "_w266bmc_", "_w267bmc_", "_w268bmc_", "_w269bmc_",
             "w266_", "w267_", "w268_", "w269_", "n1_w266", "n1_w267", "n1_w268", "n1_w269",
             "n1w267-", "n1w268-", "n1w269-", "n1w270-",
             "604_901", "606_900", "605_100", "606_700",
             "604_701", "604_900", "606_901", "607_100",
             "607_101", "609_100", "607_300", "608_900",
             "609_101", "609_300", "609_301", "611_300", "609_500", "611_100",
             "602_501", "602_700", "602_701", "602_900", "604_500",
             "600_301", "600_500", "600_700", "602_300", "600_501", "602_500",
             "598_101", "598_300", "598_301", "600_300", "598_500", "600_100",
             "1,007,335", "580,920", "1_007_335", "580_920",
             "1,009,535", "583,120", "1_009_535", "583_120",
             "1,011,735", "585,320", "1_011_735", "585_320",
             "1,013,935", "587,520", "1_013_935", "587_520",
             "1,016,135", "589,720", "1_016_135", "589_720",
             "20261017", "W268p", "W269p", "W270p", "W271p",
             "W211..W246", "W211..W264", "W247..W264", "own W247..W264",
             "thirty-six", "fifty-fourth", "fifty-three", "fifty-fifth",
             "fifty-five legs", "fifty-six legs", "fifty-sixth", "fifty-seven legs", "fifty-seventh",
             "fifty-eight legs", "fifty-eighth",
             "PENDING at seat", "waits-upstream face disclosed honest",
             "bma_ordinal", "ONE HUNDRED AND THIRTIETH", "EIGHTY-FIFTH owned",
             "EIGHTY-SIXTH owned", "EIGHTY-SEVENTH owned", "EIGHTY-NINTH owned",
             "83rd", "84th", "87th", "88th", "89th",
             "TWO HUNDRED AND SIXTY-SIXTH", "TWO HUNDRED AND SIXTY-SEVENTH",
             "TWO HUNDRED AND SIXTY-EIGHTH", "TWO HUNDRED AND SIXTY-NINTH",
             "TWO HUNDRED AND SEVENTIETH",
             "== 123", "!= 123", 'N1_BANDS[") == 124,', '!= 124',
             'N1_BANDS[") == 125,', '!= 125', 'N1_BANDS[") == 56',
             'N1_BANDS[") == 19', 'N1_BANDS[") == 20',
             'N1_BANDS[") == 126,', '!= 126', 'N1_BANDS[") == 57',
             'N1_BANDS[") == 127,', '!= 127', 'N1_BANDS[") == 58', 'N1_BANDS[") == 21',
             "N1_BANDS[246] ==", "N1_BANDS\\[246\\]", "m246",
             "N1_BANDS[247] ==", "N1_BANDS\\[247\\]", "m247",
             "FOURTEENTH", "fourteenth", "fifteenth", "FIFTEENTH",
             "rows 255 + candidate", "bmc_rows=84", "bmc_rows=85", "rows 254 + candidate",
             "rows 257 + candidate", "bmc_rows=86", "bmc_rows=87", "bmc_rows=88", "254/130/83", "owner_rows=254",
             "len(owner_rows_live) == 254", "len(owner_rows_live) == 256",
             "len(owner_rows_live) == 257", "len(owner_rows_live) == 258", "256/130/85",
             "owner_rows=256 / bma_rows=130 / bmc_rows=85",
             "owner_rows=257 / bma_rows=130 / bmc_rows=86",
             "owner_rows=258 / bma_rows=130 / bmc_rows=87", "257/130/86", "258/130/87",
             "rows 258 + candidate", "rows 259 + candidate = 260th",
             "len(owner_rows_live) == 259", "259/130/88",
             "owner_rows=259 / bma_rows=130 / bmc_rows=88",
             "(R265: ", '(R266: ', "(R267: ", "(R268: ", "(R269: ",
             "_w == 265", "_w == 266", "_w == 267", "_w == 268", "_w == 269",
             "bm-a five-face freeze upstream seat", "bm-a (upstream seat honored)",
             "owner=bm-a seat honored", "(bm-a seat owner expected)",
             "19:2x", "20:5x", "22:4x", "10:2x", "11:2x",
             "editor template", "authored 09:0x", "authored 10:5x",
             "W263_W264_W265_bands_respected", "W264_W265_W267_bands_respected",
             "W265_W266_W267_bands_respected", "W266_W267_W268_bands_respected",
             "W266_W267_W269_bands_respected", "W267_W268_W269_bands_respected",
             "range(211, 247)", "range(211, 265)", "range(247, 265)",
             "range(247, 266)", "range(16, 266)", "range(17, 266)", "range(209, 268)",
             "range(211, 266)", "range(248, 266)", "range(16, 267)", "range(17, 267)",
             "range(211, 267)", "range(248, 267)", "range(16, 268)", "range(17, 268)",
             "range(209, 269)", "range(211, 268)", "range(248, 268)",
             "range(16, 269)", "range(17, 269)", "range(209, 270)",
             "range(211, 269)", "range(248, 269)", "range(16, 270)", "range(17, 270)",
             "range(209, 271)",
             "if w < 265)", "if w < 266)", "if w < 267)", "if w < 268)", "if w < 269)",
             '"wave": 265', '"wave": 266', '"wave": 267', '"wave": 268', '"wave": 269',
             "SIXTEENTH", "sixteenth", "SEVENTEENTH", "seventeenth", "EIGHTEENTH", "eighteenth",
             "NINETEENTH", "nineteenth",
             "arith_a267", "arith_b267", "arith_a268", "arith_b268", "arith_a269", "arith_b269",
             "arith_a270", "arith_b270",
             "block = 125 rows", "125 parity rows", "block parity = 121 rows",
             "block = 126 rows", "126 parity rows", "block parity = 126 rows",
             "block = 127 rows", "127 parity rows", "block parity = 127 rows",
             "block = 128 rows", "128 parity rows", "block parity = 128 rows",
             '"fresh_legs_row_asserts": 19', '"fresh_legs_row_asserts": 20', '"fresh_legs_row_asserts": 21',
             '"fresh_legs_row_asserts": 22',
             "+ 19,", "+ 20,", "+ 21,", "+ 22,",
             "own W248..W265", "own W248..W266", "own W248..W267", "own W248..W268",
             "W248..W265 eighteen legs",
             "W248..W266 nineteen legs", "W248..W267 twenty legs",
             "W248..W268 twenty-one legs", "own W248..W268 legs (21)",
             "W211..W265 legs (55)", "W211..W266 legs (56)",
             "W211..W267 legs 56", "W211..W267 legs (57)", "W211..W267 fifty-seven legs",
             "W211..W268 legs 57", "W211..W269 legs 57", "W248..W269 legs (21",
             "W211..W268 legs (58)", "W211..W268 fifty-eight legs", "W211..W269 legs 58",
             "W248..W270 legs (22",
             "len(bmc_rows_live)} + candidate (87th own wave",
             "len(bmc_rows_live)} + candidate (88th own wave",
             "len(bmc_rows_live)} + candidate (89th own wave",
             "EIGHTY-EIGHTH owned", "bm-c's 87th own wave", "bm-c's 88th own wave", "bm-c's 89th own wave",
             "engine_owner==bm-c rows 86 + candidate", "engine_owner==bm-c rows 87 + candidate",
             "engine_owner==bm-c rows 88 + candidate",
             "268 - _lw", "269 - _lw", "270 - _lw",
             "_set_wave(268)", "_set_wave(267)", "_set_wave(266)", "_set_wave(269)", "_set_wave(270)",
             "942ebd5885 r1089"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
    'MSG-20261018-175x-bmc-w271-seat': 7, "87d2697cdc": 2, "_w271bmc_": 11,
    "20261018": 17, "f75b18c862": 1, "1c814343ed": 1,
    "613_501": 5, "613_700": 4, "611_501": 8, "613_500": 9,
    "611_700": 2, "613_300": 2, "611_301": 4, "611_500": 6,
    "1,018,335": 6, "591,920": 6, "1_018_335": 1, "591_920": 1,
    '271: {"batch"': 2, '270: {"batch"': 2, '269: {"batch"': 0,
    '271: {{"batch"': 1, '271: {"a"': 1, '270: {"a"': 3, '271: {{"a"': 2,
    "range(248, 271)": 2, "range(209, 272)": 2, "range(16, 271)": 2,
    "range(17, 271)": 3, "range(211, 248)": 1, "range(211, 270)": 1,
    "range(248, 270)": 1, "range(138, 207)": 1,
    "if w < 271)": 5, "if w < 270)": 1, "271 - _lw": 2,
    "m248": 4, "m211": 4, "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
    "WAVE_CONFIGS[271]": 2, "WAVE_CONFIGS[270]": 3, "N1_BANDS[270]": 5,
    "get(270)": 1, "_c270": 5,
    "arith_a271": 6, "arith_b271": 6,
    "(267, 266, 265, 264, 263, 262, 261, 260, 259, 258)": 2, "W258..W267": 1,
    "len(owner_rows_live) == 260": 1, "260/130/89": 1, "bmc_rows=89": 7,
    "rows 260 + candidate = 261st": 2, "bm-c rows 89 + candidate = 90th owned": 1,
    "NINETIETH owned": 3, "TWO HUNDRED AND SEVENTY-FIRST": 3,
    "TWENTY-FIRST": 7, "TWENTIETH": 15, "twenty-first": 4, "twentieth": 3,
    "W268_W269_W270_bands_respected": 2, "W272p": 13, "W272": 26,
    "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
    "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
    "W271 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
    "the bm-c r1095 splice window": 2,
    "bm-c own seat executed at the bm-c r1095 splice window": 1,
    "finalize one-pass bm-c r1095": 2,
    "authored 17:5x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
    "cycle COMPLETE bm-c r1095 closeout 17:3x": 1,
    "verified r1095": 1, "(R270: ": 1, "_w == 270": 1,
    "wave 271 engine_owner=bm-c": 1, '"wave 271: "': 1,
    "wave 271 = first free number": 1, "fifty-ninth": 2, "fifty-nine legs": 1,
    'N1_BANDS[") == 128,': 1, '!= 128': 1, 'N1_BANDS[") == 59': 1,
    'N1_BANDS[") == 37': 1, 'N1_BANDS[") == 22': 1,
    "W211..W269 legs (59)": 1, "W211..W270 legs 59": 1,
    "own W248..W269 legs (22)": 4, "own W248..W269": 5, "W248..W271 legs (23": 4,
    "block = 129 rows": 1, "129 parity rows": 1, "block parity = 129 rows": 1,
    "bm-c r1096 window": 4, "# r1096 window": 1, "r1096 commit": 1,
    "bm-c splice generation r1095 window": 1, "(bm-c r1095": 1,
    "_w270bmc_freeze_edits.py template": 1,
    "PERPETUAL_N1_W271_PREREG": 8, "PERPETUAL-N1-W271": 7,
    "n1_w271": 4, "n1_w270": 4, "n1w271-": 2,
    "n1_w271_results.json": 2, "n1_w270_results.json": 4,
    "W271 materializer face": 4, "W270 materializer face": 1,
    "W269 finalize product": 0, "W270 finalize product": 4, "W271 block": 4,
    "engine_owner==bm-c rows 89 + candidate": 1,
    "# candidate = 90th EXACT": 1, "; bm-c rows 89 +": 1,
    "bm-c rows {len(bmc_rows_live)} + candidate (90th own wave": 1,
    "bm-c's 90th own wave": 2, "owner_rows=260 / bma_rows=130 / bmc_rows=89": 1,
    '"probe_receipt_bmc_ordinal_face": 89': 1,
    "fourteen-wave": 8, "post-W270-REGISTERED": 8,
    "anchors W270 1,018,335 / K=591,920 at draft": 1,
    "dual-window parity": 1, "W272 walk": 1,
    "fifty-ninth consecutive": 2, '"wave": 270': 1,
    "bma rows 129 + candidate 130th": 1,
    "registered wave below 263 composes": 2,
    "PRE-W271-splice": 1, "post-W270 registration": 2,
    "expect 260/130/89": 1,
    "_set_wave(271)": 1, "_set_wave(270)": 0, "_set_wave(269)": 0, "_set_wave(268)": 0,
    "_set_wave(2)": 1,
    "2026-10-18 18:2x bm-c r1097 freeze window": 1,
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
