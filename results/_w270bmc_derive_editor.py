# -*- coding: utf-8 -*-
# r1095 bm-c: derive results/_w270bmc_freeze_edits.py from the committed W269
# freeze-edits canon (results/_w269bmc_freeze_edits.py, bm-c r1093 splice
# window 440b07c94b, proven live-fire: W269 five-face splice + engine
# self-burn 12/12 appends 32cbe26a1c+f59af28e77 + finalize one-pass ledger
# 1,016,135 / K=589,720 + W270 seat published @ origin 9f480646f4 r1094
# dead-window absorbed per bm-c lineage, machine-verified r1094 closeout)
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 14th-gen lineage, zero
# transcription: every needle count MEASURED on the canon blob by
# results/_r1095bmc_needle_preflight.py (receipt
# results/_r1095bmc_needle_preflight.json, canon sha256_16 2e867a8f822ca715,
# 62,157B, wt==HEAD==origin triple-verified) + final missing-needle sweep in
# the phase-4 residual gates -- r1077 measured-counts law.
# DISCLOSED CANON EOL FACE (benign, carried): core.autocrlf=true re-smudge
# (r1093 pit entry) -- canon + W270 payload files (prereg/probe receipt)
# on disk are the CRLF-smudged forms of their LF origin blobs (norm-eq
# TRUE, prereg disk 23,259B sha256_16 3aa0b98239369608 verified in
# preflight); the editor reads canon raw with newline='' and the executor
# reads text-mode or git-object-level -- zero content impact.
# AGING-TOKEN LAW (E63 anti-drift): frozen faces w244_a/w244_b and
# n3r1_used245 do NOT roll (measured 12/8/3 in canon; carried verbatim,
# anti-drift asserted here; "w244_a holds wave-263 bands" disclosure text
# carries verbatim, measured 4). Band order law: consumers before producers
# (609_101/609_300/607_101/609_100/607_300/608_900 consumed BEFORE the
# 606_901/607_100 producers, else the fresh prior-wave B tokens
# double-transform). Own-first law at every level (W269 before W268;
# 269: {"batch" before 268: {"batch"; WAVE_CONFIGS[269] before [268];
# if w < 269) before if w < 268); ordinal order law: TWENTIETH (B,
# above-own-A) caps roll before NINETEENTH (A, A-hop) -- B-ordinal caps
# first, then A-ordinal caps, else double-transform.
# SETWAVE +1 AGING LAW (r1076-family ROOT CURE, held since r1088): the canon
# carries _set_wave(269) (the healed W269 block face); this editor ages it
# rep('_set_wave(269)','_set_wave(270)',1) -- presence gates
# _set_wave(270):1 / _set_wave(269):0 / _set_wave(268):0 / _set_wave(267):0.
# W270 FACTS (probe receipt results/_w270bmc_20261018_probe_receipt.json,
# committed with the seat @ 9f480646f4 r1094): bands A 609_301..611_300
# (NINETEENTH consecutive A-hop, staircase-affects-A, hops=1; naive A
# 609_101..611_100 refused at registered W269 B 609_101..609_300) /
# B 611_301..611_500 (TWENTIETH consecutive above-own-A, own-A reservation
# cascade, hops=1; naive B 609_301..609_500 inside own-A window
# 609_301..611_300); seed_admit FREE x2 (base=609301 span=2000 /
# base=611301 span=200); ordinals owner 259 + candidate = 260th /
# bm-c rows 88 + candidate = 89th; W269 finalize anchors 1,016,135 /
# K=589,720 (chain +2,200/+2,200 EXACT).
# Window-stamp disambiguation (all r1091 x15 / r1092 x6 / r1093 x1
# contexts measured in the preflight receipt): SEAT faces -> r1094 (W270
# seat MSG-20261018-1605-bmc-w270-seat @ origin 9f480646f4, dead r1094
# seat window absorbed per bm-c lineage); SPLICE faces -> r1093 (W269
# splice 440b07c94b); FINALIZE faces -> r1093 (W269 finalize one-pass
# 15:4x); PREREG faces -> r1094 (W270 prereg 3bb8b9308e authored 16:3x);
# cycle face -> r1093 closeout 15:4x.
# r1091 W268 出稿双坑预检 honored (W269+ editor authoring law): (a) gone
# 清单禁收裸波号/生产面 token -- 609_101/609_300 (producer-news),
# range(248, 269) (dropped-range news), "if w < 269)" (anti-gate news),
# r1093/NINETEENTH/W271p/n1_w270/w270_/n1w270-/_w270bmc_ all EXCLUDED from
# the gone list (live produced faces); (b) 折行断言形拆短 needle -- all
# count needles kept short-form (no cross-continuation long strings).
import io, subprocess, sys

CANON = "results/_w269bmc_freeze_edits.py"
DST = "results/_w270bmc_freeze_edits.py"
LOG = "results/_r1095bmc_derive_editor_log.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w269bmc_freeze_edits.py"],
                           capture_output=True, text=True).stdout.strip()
blob_origin = subprocess.run(["git", "rev-parse", "origin/main:results/_w269bmc_freeze_edits.py"],
                             capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head == blob_origin and len(blob_wt) == 40, \
    f"canon blob drift wt={blob_wt} head={blob_head} origin={blob_origin}"

t = io.open(CANON, encoding="utf-8", newline="").read()
log = [f"S0 canon blob verified {blob_wt[:16]} == HEAD == origin twin (preflight-measured sha256_16 2e867a8f822ca715, 62,157B)",
       f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:100]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W270p", "W271p", 13, "p1_proj_prefix")
rep("W270", "W271", 13, "p1_proj_plain")
# bands: W270 registered A 609_301..611_300 (19th A-hop) / B 611_301..611_500
# (20th above-own-A); naive A 609_101..611_100 refused at registered W269 B
# 609_101..609_300; naive B 609_301..609_500 inside own-A reservation.
# CONSUMERS FIRST (band-order law):
rep("609_101", "611_301", 5, "p1_band_Blo_naiveAlo")
rep("609_300", "611_500", 4, "p1_band_Bhi")
rep("607_101", "609_301", 8, "p1_band_Alo_Bnaivelo")
rep("609_100", "611_300", 9, "p1_band_Ahi")
rep("607_300", "609_500", 2, "p1_band_Bnaivehi")
rep("608_900", "611_100", 2, "p1_band_naiveAhi")
# PRODUCERS LAST (else the fresh 609_101/609_300 tokens double-transform):
rep("606_901", "609_101", 4, "p1_band_priorBlo")
rep("607_100", "609_300", 6, "p1_band_priorBhi")
# ledger/K anchors: W268 finalize facts -> W269 finalize facts (1,016,135/589,720)
rep("1,013,935", "1,016,135", 6, "p1_ledger_prose")
rep("587,520", "589,720", 6, "p1_k_prose")
rep("1_013_935", "1_016_135", 1, "p1_ledger_code")
rep("587_520", "589_720", 1, "p1_k_code")
# lowercase machine-file tokens (own wave first, then upstream wave)
rep("n1_w269", "n1_w270", 4, "p1_n1w269")
rep("n1w269-", "n1w270-", 2, "p1_n1w269dash")
# 12 raw w269_ minus 2 consumed by the n1_w269 rep (n1_w269_results x2)
rep("w269_", "w270_", 10, "p1_lc_w269_")
rep("n1_w268", "n1_w269", 4, "p1_n1w268")
# 93 raw w268_ minus 4 consumed by the n1_w268 rep (n1_w268_results x4)
rep("w268_", "w269_", 89, "p1_lc_w268_")
rep("_w269bmc_", "_w270bmc_", 11, "p1_receiptpath")
rep("MSG-20261018-1407-bmc-w269-seat", "MSG-20261018-1605-bmc-w270-seat", 7, "p1_seat_msg")
rep("d630d043b9 r1091", "9f480646f4 r1094", 1, "p1_seat_origin_hdr")
rep('SEAT_ORIGIN = "d630d043b9"', 'SEAT_ORIGIN = "9f480646f4"', 1, "p1_seat_origin_const")
rep("8bc7ac759e", "440b07c94b", 1, "p1_lineage_sha")
rep("67fe12710c", "3bb8b9308e", 1, "p1_prereg_sha_ref")
# stale-carried receipt wave field (mechanical +1): 268->269
rep('"wave": 268', '"wave": 269', 1, "p1_receipt_wave")
# header window stamp: this r1095 freeze window
rep("2026-10-18 15:2x bm-c r1093 freeze window", "2026-10-18 17:0x bm-c r1095 freeze window", 1, "p1_hdr_stamp")

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W269", "W270", 96, "p2_own_wave")
rep("W268", "W269", 159, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
# relkey = POST-BLANKET form (the upstream blanket rolled the W268 inside
# "W266_W267_W268_bands_respected" -> "W266_W267_W269"; this rep rolls all
# three positions +1 wave to the W270 probe receipt's relation keys)
rep("W266_W267_W269_bands_respected", "W267_W268_W269_bands_respected", 2, "p3_relkey")
# legs_sec prose + message (W270 extraction: legs W211..W268 = 58)
rep("W211..W267 legs (57)", "W211..W268 legs (58)", 1, "p3_legs_prose")
rep("W211..W267 fifty-seven legs", "W211..W268 fifty-eight legs", 1, "p3_legs_msg")
# legs_sec wave-list range (the count itself rides the p3_count57 short needle
# below -- the assert is line-wrapped in the canon, CRLF continuation)
rep("range(211, 268)", "range(211, 269)", 1, "p3_range_legs")
# dropped faces (W270 extraction drops the W269 block's own W248..W268 = 21 legs)
rep("own W248..W267 legs (20)", "own W248..W268 legs (21)", 4, "p3_dropped_narr")
rep("own W248..W267", "own W248..W268", 1, "p3_dropped_split_hdr")
rep("W248..W267 twenty legs", "W248..W268 twenty-one legs", 1, "p3_dropped_fstring")
rep('N1_BANDS[") == 20', 'N1_BANDS[") == 21', 1, "p3_dropped_count")
# fullspan error-string (POST-BLANKET wave face rolled by the upstream
# blanket: "W211..W268 legs 57" -> "W211..W269 legs 57"; count 57->58)
rep("W211..W269 legs 57", "W211..W269 legs 58", 1, "p3_fullspan_fstring")
# fresh legs (W270 block appends fresh W248..W269 = 22 legs; POST-BLANKET
# form -- the own blanket rolled the hi face to the new range end 270;
# count-only roll 21->22, hi rides the blanket = range(248, 270) END EXACT)
rep("W248..W270 legs (21", "W248..W270 legs (22", 4, "p3_fresh_narr")
# block/parity counts: W270 block = 69 estate + 37 kept + 22 fresh = 128
rep("block = 127 rows", "block = 128 rows", 1, "p3_block127")
rep("127 parity rows", "128 parity rows", 1, "p3_parity127")
rep("block parity = 127 rows", "block parity = 128 rows", 1, "p3_blockparity_hdr")
rep('N1_BANDS[") == 126,', 'N1_BANDS[") == 127,', 1, "p3_count126")
rep('!= 126', '!= 127', 1, "p3_fstring126")
rep('N1_BANDS[") == 57', 'N1_BANDS[") == 58', 1, "p3_count57")
rep('"fresh_legs_row_asserts": 21', '"fresh_legs_row_asserts": 22', 1, "p3_receipt_fresh21")
rep('+ 21,', '+ 22,', 1, "p3_receipt_total21")
# ranges (fresh FIRST then dropped-producer, then the cumulative/registry faces)
rep("range(248, 269)", "range(248, 270)", 2, "p3_range_fresh")
rep("range(248, 268)", "range(248, 269)", 1, "p3_range_dropped")
rep("range(16, 269)", "range(16, 270)", 2, "p3_range16")
rep("range(17, 269)", "range(17, 270)", 3, "p3_range17")
rep("range(209, 270)", "range(209, 271)", 2, "p3_range209")
# wave-number gates (own 269->270 FIRST, then anti-gate 268->269)
rep("if w < 269)", "if w < 270)", 5, "p3_wlt269")
rep("if w < 268)", "if w < 269)", 1, "p3_wlt268_antigate")
rep("269 - _lw", "270 - _lw", 2, "p3_legcount")
# fresh-legs loop boundary (number face, blankets do not touch bare numbers)
rep("_w == 268", "_w == 269", 1, "p3_freshmsg_cond")
# cfg/row faces: own 269->270 FIRST (band-faces own-first law), then upstream 268->269
rep("WAVE_CONFIGS[269]", "WAVE_CONFIGS[270]", 2, "p3_wavecfg269_own")
rep("WAVE_CONFIGS[268]", "WAVE_CONFIGS[269]", 3, "p3_wavecfg268")
rep("N1_BANDS[268]", "N1_BANDS[269]", 5, "p3_n1bands268")
rep("get(268)", "get(269)", 1, "p3_get268")
rep("_c268", "_c269", 5, "p3_c268var")
rep('269: {"batch"', '270: {"batch"', 2, "p3_cfg269")
rep('269: {{"batch"', '270: {{"batch"', 1, "p3_cfg269_fstring")
rep('269: {"a"', '270: {"a"', 1, "p3_row269_postgate")
rep('269: {{"a"', '270: {{"a"', 2, "p3_row269_fstring")
rep('268: {"batch"', '269: {"batch"', 2, "p3_cfg268")
rep('268: {"a"', '269: {"a"', 3, "p3_row268")
rep("arith_a269", "arith_a270", 6, "p3_arith_a")
rep("arith_b269", "arith_b270", 6, "p3_arith_b")
rep("(265, 264, 263, 262, 261, 260, 259, 258, 257, 256)",
    "(266, 265, 264, 263, 262, 261, 260, 259, 258, 257)", 2, "p3_transitive_list")
rep("W256..W265", "W257..W266", 1, "p3_transitive_window")
# ordinal faces: owner 258->259, bma 130 held, bmc 87->88 (W270 = 260th candidate, bm-c 89th own)
rep("len(owner_rows_live) == 258 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 87",
    "len(owner_rows_live) == 259 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 88", 1, "p3_ordinal_assert")
rep("258/130/87", "259/130/88", 1, "p3_ordinal_expect")
rep("owner_rows=258 / bma_rows=130 / bmc_rows=87", "owner_rows=259 / bma_rows=130 / bmc_rows=88", 1, "p3_leg0_face")
rep("rows 258 + candidate = 259th", "rows 259 + candidate = 260th", 2, "p3_owner258")
rep("; bm-c rows 87 +", "; bm-c rows 88 +", 1, "p3_comment_87split")
rep("bm-c rows 87 + candidate = 88th owned", "bm-c rows 88 + candidate = 89th owned", 1, "p3_receipt_88owned")
rep("# candidate = 88th EXACT", "# candidate = 89th EXACT", 1, "p3_comment_88th")
rep("engine_owner==bm-c rows 87 + candidate", "engine_owner==bm-c rows 88 + candidate", 1, "p3_pr_eo87")
rep("bm-c rows {len(bmc_rows_live)} + candidate (88th own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (89th own wave", 1, "p3_gate0_5_print")
rep("bm-c's 88th own wave", "bm-c's 89th own wave", 2, "p3_88th_own_wave")
rep("EIGHTY-EIGHTH owned", "EIGHTY-NINTH owned", 3, "p3_88th_caps")
rep("TWO HUNDRED AND SIXTY-NINTH", "TWO HUNDRED AND SEVENTIETH", 3, "p3_wave_caps")
# 7 raw bmc_rows=87 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=87", "bmc_rows=88", 6, "p3_bmc_rows87")
rep('"probe_receipt_bmc_ordinal_face": 87', '"probe_receipt_bmc_ordinal_face": 88', 1, "p3_probe_face_key")
# ordinal narrative: B-ordinal NINETEENTH->TWENTIETH FIRST, then A-ordinal EIGHTEENTH->NINETEENTH
rep("NINETEENTH", "TWENTIETH", 7, "p3_19_caps")
rep("EIGHTEENTH", "NINETEENTH", 15, "p3_18_caps")
rep("nineteenth", "twentieth", 4, "p3_19_lc")
rep("eighteenth", "nineteenth", 3, "p3_18_lc")
rep("fifty-seventh", "fifty-eighth", 2, "p3_57th")
# wave-number narrative faces
rep("wave 269 engine_owner=bm-c", "wave 270 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 269: "', '"wave 270: "', 1, "p3_cfg_waveface")
rep("wave 269 = first free number", "wave 270 = first free number", 1, "p3_mhdr_waveface")
# cycle/lineage window stamps (SEAT->r1094 / SPLICE->r1093 / FINALIZE->r1093, contexts measured)
rep("cycle COMPLETE bm-c r1091 closeout 14:1x", "cycle COMPLETE bm-c r1093 closeout 15:4x", 1, "p3_hdr_complete")
rep("the bm-c r1091 splice window", "the bm-c r1093 splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1091", "own-wave full cycle r1093", 1, "p3_repair_note")
rep("bm-c splice generation r1091 window", "bm-c splice generation r1093 window", 1, "p3_parity_source_note")
rep("verified r1091", "verified r1093", 1, "p3_lineage_verified")
rep("# r1091 splice window", "# r1093 splice window", 1, "p3_lineage_r1091")
rep("(bm-c r1091", "(bm-c r1093", 1, "p3_parity_comment")
rep("finalize one-pass bm-c r1091 closeout, ledger", "finalize one-pass bm-c r1093 closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1091 closeout ledger", "finalize one-pass bm-c r1093 closeout ledger", 1, "p3_finpass_hdr")
rep("(r1091 MSG-", "(r1094 MSG-", 1, "p3_hdr_msgline")
rep("r1091 BEFORE this freeze", "r1094 BEFORE this freeze", 1, "p3_receipt_seatnote")
rep("seat itself r1091; queue-head", "seat itself r1094; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1091, queue-head seat-first supply", "(r1094, queue-head seat-first supply", 1, "p3_pfcomment_seat")
# prereg window map (W269 prereg r1092 window -> W270 prereg r1094 window)
rep("bm-c r1092 window", "bm-c r1094 window", 4, "p3_prereg_window")
rep("# r1092 window", "# r1094 window", 1, "p3_hdr_prereg_window")
rep("r1092 commit", "r1094 commit", 1, "p3_receipt_commit")
# authored stamp (W270 prereg derived 16:3x, committed 3bb8b9308e 16:30:49)
rep("authored 14:4x", "authored 16:3x", 2, "p3_authored_stamp")
# lineage header: canon template identity rolls to the W269 canon
rep("_w268bmc_freeze_edits.py template", "_w269bmc_freeze_edits.py template", 1, "p3_lineage_template")
rep("(R268: ", "(R269: ", 1, "p3_repick")
# r1076-family ROOT CURE +1 aging law (NOT the mechanical 268->270 form)
rep("_set_wave(269)", "_set_wave(270)", 1, "p3_setwave_rootcure")

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
for gone in ("r1088", "r1089", "r1090", "r1091", "r1092",
             "12:3x", "13:1x", "authored 13:1x", "14:1x", "14:4x", "authored 14:4x",
             "13:4x", "14:0x", "15:2x",
             "df55e3fab9", "942ebd5885", "dc71ecc3f9", "7b9e9377", "f1ec8231c7",
             "d630d043b9", "8bc7ac759e", "67fe12710c", "d630d043b9 r1091",
             "MSG-20261018-1025-bmc-w267-seat", "MSG-20261018-1229-bmc-w268-seat",
             "MSG-20261018-1407-bmc-w269-seat",
             "_w266bmc_", "_w267bmc_", "_w268bmc_",
             "w266_", "w267_", "w268_", "n1_w266", "n1_w267", "n1_w268",
             "n1w267-", "n1w268-", "n1w269-",
             "604_901", "606_900", "605_100", "606_700",
             "604_701", "604_900", "606_901", "607_100",
             "607_101", "609_100", "607_300", "608_900",
             "602_501", "602_700", "602_701", "602_900", "604_500",
             "600_301", "600_500", "600_700", "602_300", "600_501", "602_500",
             "598_101", "598_300", "598_301", "600_300", "598_500", "600_100",
             "1,007,335", "580,920", "1_007_335", "580_920",
             "1,009,535", "583,120", "1_009_535", "583_120",
             "1,011,735", "585,320", "1_011_735", "585_320",
             "1,013,935", "587,520", "1_013_935", "587_520",
             "20261017", "W268p", "W269p", "W270p",
             "W211..W246", "W211..W264", "W247..W264", "own W247..W264",
             "thirty-six", "fifty-fourth", "fifty-three", "fifty-fifth",
             "fifty-five legs", "fifty-six legs", "fifty-sixth", "fifty-seven legs", "fifty-seventh",
             "PENDING at seat", "waits-upstream face disclosed honest",
             "bma_ordinal", "ONE HUNDRED AND THIRTIETH", "EIGHTY-FIFTH owned",
             "EIGHTY-SIXTH owned", "EIGHTY-SEVENTH owned", "83rd", "84th", "87th", "88th",
             "TWO HUNDRED AND SIXTY-SIXTH", "TWO HUNDRED AND SIXTY-SEVENTH",
             "TWO HUNDRED AND SIXTY-EIGHTH", "TWO HUNDRED AND SIXTY-NINTH",
             "== 123", "!= 123", 'N1_BANDS[") == 124,', '!= 124',
             'N1_BANDS[") == 125,', '!= 125', 'N1_BANDS[") == 56',
             'N1_BANDS[") == 19', 'N1_BANDS[") == 20',
             'N1_BANDS[") == 126,', '!= 126', 'N1_BANDS[") == 57',
             "N1_BANDS[246] ==", "N1_BANDS\\[246\\]", "m246",
             "N1_BANDS[247] ==", "N1_BANDS\\[247\\]", "m247",
             "FOURTEENTH", "fourteenth", "fifteenth", "FIFTEENTH",
             "rows 255 + candidate", "bmc_rows=84", "bmc_rows=85", "rows 254 + candidate",
             "rows 257 + candidate", "bmc_rows=86", "bmc_rows=87", "254/130/83", "owner_rows=254",
             "len(owner_rows_live) == 254", "len(owner_rows_live) == 256",
             "len(owner_rows_live) == 257", "len(owner_rows_live) == 258", "256/130/85",
             "owner_rows=256 / bma_rows=130 / bmc_rows=85",
             "owner_rows=257 / bma_rows=130 / bmc_rows=86",
             "owner_rows=258 / bma_rows=130 / bmc_rows=87", "257/130/86", "258/130/87",
             "rows 258 + candidate",
             '(R265: ', '(R266: ', "(R267: ", "(R268: ", "_w == 265", "_w == 266", "_w == 267", "_w == 268",
             "bm-a five-face freeze upstream seat", "bm-a (upstream seat honored)",
             "owner=bm-a seat honored", "(bm-a seat owner expected)",
             "18:2x", "19:2x", "20:5x", "22:4x", "10:2x", "11:2x",
             "editor template", "authored 09:0x", "authored 10:5x",
             "W263_W264_W265_bands_respected", "W264_W265_W267_bands_respected",
             "W265_W266_W267_bands_respected", "W266_W267_W268_bands_respected",
             "W266_W267_W269_bands_respected",
             "range(211, 247)", "range(211, 265)", "range(247, 265)",
             "range(247, 266)", "range(16, 266)", "range(17, 266)", "range(209, 268)",
             "range(211, 266)", "range(248, 266)", "range(16, 267)", "range(17, 267)",
             "range(211, 267)", "range(248, 267)", "range(16, 268)", "range(17, 268)",
             "range(209, 269)", "range(211, 268)", "range(248, 268)",
             "range(16, 269)", "range(17, 269)", "range(209, 270)",
             "if w < 265)", "if w < 266)", "if w < 267)", "if w < 268)",
             '"wave": 265', '"wave": 266', '"wave": 267', '"wave": 268',
             "SIXTEENTH", "sixteenth", "SEVENTEENTH", "seventeenth", "EIGHTEENTH", "eighteenth",
             "arith_a267", "arith_b267", "arith_a268", "arith_b268", "arith_a269", "arith_b269",
             "block = 125 rows", "125 parity rows", "block parity = 121 rows",
             "block = 126 rows", "126 parity rows", "block parity = 126 rows",
             "block = 127 rows", "127 parity rows", "block parity = 127 rows",
             '"fresh_legs_row_asserts": 19', '"fresh_legs_row_asserts": 20', '"fresh_legs_row_asserts": 21',
             "+ 19,", "+ 20,", "+ 21,",
             "own W248..W265", "own W248..W266", "own W248..W267", "W248..W265 eighteen legs",
             "W248..W266 nineteen legs", "W248..W267 twenty legs",
             "W211..W265 legs (55)", "W211..W266 legs (56)",
             "W211..W267 legs 56", "W211..W267 legs (57)", "W211..W267 fifty-seven legs",
             "W211..W268 legs 57", "W211..W269 legs 57", "W248..W269 legs (21",
             "len(bmc_rows_live)} + candidate (87th own wave",
             "len(bmc_rows_live)} + candidate (88th own wave",
             "EIGHTY-EIGHTH owned", "bm-c's 87th own wave", "bm-c's 88th own wave",
             "engine_owner==bm-c rows 86 + candidate", "engine_owner==bm-c rows 87 + candidate",
             "268 - _lw", "269 - _lw", "_set_wave(268)", "_set_wave(267)", "_set_wave(266)", "_set_wave(269)",
             "942ebd5885 r1089"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
    'MSG-20261018-1605-bmc-w270-seat': 7, "9f480646f4": 2, "_w270bmc_": 11,
    "20261018": 17, "3bb8b9308e": 1, "440b07c94b": 1,
    "611_301": 5, "611_500": 4, "609_301": 8, "611_300": 9,
    "609_500": 2, "611_100": 2, "609_101": 4, "609_300": 6,
    "1,016,135": 6, "589,720": 6, "1_016_135": 1, "589_720": 1,
    '270: {"batch"': 2, '269: {"batch"': 2, '268: {"batch"': 0,
    '270: {{"batch"': 1, '270: {"a"': 1, '269: {"a"': 3, '270: {{"a"': 2,
    "range(248, 270)": 2, "range(209, 271)": 2, "range(16, 270)": 2,
    "range(17, 270)": 3, "range(211, 248)": 1, "range(211, 269)": 1,
    "range(248, 269)": 1, "range(138, 207)": 1,
    "if w < 270)": 5, "if w < 269)": 1, "270 - _lw": 2,
    "m248": 4, "m211": 4, "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
    "WAVE_CONFIGS[270]": 2, "WAVE_CONFIGS[269]": 3, "N1_BANDS[269]": 5,
    "get(269)": 1, "_c269": 5,
    "arith_a270": 6, "arith_b270": 6,
    "(266, 265, 264, 263, 262, 261, 260, 259, 258, 257)": 2, "W257..W266": 1,
    "len(owner_rows_live) == 259": 1, "259/130/88": 1, "bmc_rows=88": 7,
    "rows 259 + candidate = 260th": 2, "bm-c rows 88 + candidate = 89th owned": 1,
    "EIGHTY-NINTH owned": 3, "TWO HUNDRED AND SEVENTIETH": 3,
    "TWENTIETH": 7, "NINETEENTH": 15, "twentieth": 4, "nineteenth": 3,
    "W267_W268_W269_bands_respected": 2, "W271p": 13, "W271": 26,
    "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
    "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
    "W270 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
    "the bm-c r1093 splice window": 2,
    "bm-c own seat executed at the bm-c r1093 splice window": 1,
    "finalize one-pass bm-c r1093": 2,
    "authored 16:3x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
    "cycle COMPLETE bm-c r1093 closeout 15:4x": 1,
    "verified r1093": 1, "(R269: ": 1, "_w == 269": 1,
    "wave 270 engine_owner=bm-c": 1, '"wave 270: "': 1,
    "wave 270 = first free number": 1, "fifty-eighth": 2, "fifty-eight legs": 1,
    'N1_BANDS[") == 127,': 1, '!= 127': 1, 'N1_BANDS[") == 58': 1,
    'N1_BANDS[") == 37': 1, 'N1_BANDS[") == 21': 1,
    "W211..W268 legs (58)": 1, "W211..W269 legs 58": 1,
    "own W248..W268 legs (21)": 4, "own W248..W268": 5, "W248..W270 legs (22": 4,
    "block = 128 rows": 1, "128 parity rows": 1, "block parity = 128 rows": 1,
    "bm-c r1094 window": 4, "# r1094 window": 1, "r1094 commit": 1,
    "bm-c splice generation r1093 window": 1, "(bm-c r1093": 1,
    "_w269bmc_freeze_edits.py template": 1,
    "PERPETUAL_N1_W270_PREREG": 8, "PERPETUAL-N1-W270": 7,
    "n1_w270": 4, "n1_w269": 4, "n1w270-": 2,
    "n1_w270_results.json": 2, "n1_w269_results.json": 4,
    "W270 materializer face": 4, "W269 materializer face": 1,
    "W269 finalize product": 4, "W270 block": 4,
    "engine_owner==bm-c rows 88 + candidate": 1,
    "# candidate = 89th EXACT": 1, "; bm-c rows 88 +": 1,
    "bm-c rows {len(bmc_rows_live)} + candidate (89th own wave": 1,
    "bm-c's 89th own wave": 2, "owner_rows=259 / bma_rows=130 / bmc_rows=88": 1,
    '"probe_receipt_bmc_ordinal_face": 88': 1,
    "fourteen-wave": 8, "post-W269-REGISTERED": 8,
    "anchors W269 1,016,135 / K=589,720 at draft": 1,
    "dual-window parity": 1, "W271 walk": 1,
    "fifty-eighth consecutive": 2, '"wave": 269': 1,
    "bma rows 129 + candidate 130th": 1,
    "registered wave below 263 composes": 2,
    "PRE-W270-splice": 1, "post-W269 registration": 2,
    "expect 259/130/88": 1,
    "_set_wave(270)": 1, "_set_wave(269)": 0, "_set_wave(268)": 0, "_set_wave(267)": 0,
    "_set_wave(2)": 1,
    "2026-10-18 17:0x bm-c r1095 freeze window": 1,
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
