# -*- coding: utf-8 -*-
# r1093 bm-c: derive results/_w269bmc_freeze_edits.py from the committed W268
# freeze-edits canon (results/_w268bmc_freeze_edits.py, bm-c r1091 splice
# window 8bc7ac759e, proven live-fire: W268 five-face splice + engine
# self-burn 12/12 appends 8d0e7bdb1/78af85566 + finalize one-pass ledger
# 1,013,935 / K=587,520 + W269 seat published @ origin d630d043b9 r1091,
# machine-verified r1091 closeout) by COUNT-ASSERTED ORDERED TRANSFORM
# (E63 13th-gen lineage, zero transcription: every needle count MEASURED on
# the canon blob by results/_r1093bmc_needle_preflight.py (receipt
# results/_r1093bmc_needle_preflight.json) + final missing-needle pass
# results/_r1093bmc_final_measure.py -- r1077 measured-counts law;
# canon blob wt==HEAD==origin twin verified in-preflight (hash-object
# check-in-normalized identity; sha256_16 a0c5f9209bddc179, 62,187B).
# DISCLOSED CANON EOL FACE (benign): core.autocrlf=true re-smudge -- the
# canon + W269 payload files (prereg/probe receipt/facts) on disk are the
# CRLF-smudged forms of their LF origin blobs (norm-eq TRUE, content
# identical, 7-file sweep evidence in the preflight receipt); the editor
# reads canon raw with newline='' and the executor reads text-mode or
# git-object-level -- zero content impact, carried as-is, no heal needed.
# AGING-TOKEN LAW (E63 anti-drift): frozen faces w244_a/w244_b and
# n3r1_used245 do NOT roll (measured 12/8/3 in canon; carried verbatim,
# anti-drift asserted here; "w244_a holds wave-263 bands" disclosure text
# carries verbatim, measured 4). Band order law: consumers before producers
# (606_901/607_100/604_901/606_900/605_100/606_700 consumed BEFORE the
# 604_701/604_900 producers, else the fresh prior-wave B tokens
# double-transform). Own-first law at every level (W268 before W267; 268:
# {"batch" before 267: {"batch"; WAVE_CONFIGS[268] before [267]; if w < 268)
# before if w < 267); ordinal order law: EIGHTEENTH (B, above-own-A) rolls
# before SEVENTEENTH (A, A-hop) -- B-ordinal caps first, then A-ordinal,
# else double-transform.
# SETWAVE +1 AGING LAW (r1076-family ROOT CURE, held since r1088): the canon
# carries _set_wave(268) (the healed W268 block face); this editor ages it
# rep('_set_wave(268)','_set_wave(269)',1) -- presence gates
# _set_wave(269):1 / _set_wave(268):0 / _set_wave(267):0 / _set_wave(266):0.
# W269 FACTS (probe receipt results/_w269bmc_20261018_probe_receipt.json,
# committed with the seat @ d630d043b9): bands A 607_101..609_100
# (EIGHTEENTH consecutive A-hop, staircase-affects-A, hops=1; naive A
# 606_901..608_900 refused at registered W268 B 606_901..607_100) /
# B 609_101..609_300 (NINETEENTH consecutive above-own-A, own-A reservation
# cascade, hops=1; naive B 607_101..607_300 inside own-A window
# 607_101..609_100); seed_admit FREE x2 (base=607101 span=2000 /
# base=609101 span=200); ordinals owner 258 + candidate = 259th /
# bm-c rows 87 + candidate = 88th; W268 finalize anchors 1,013,935 /
# K=587,520 (chain +2,200/+2,200 EXACT).
# Window-stamp disambiguation (all r1088 x7 / r1089 x10 / r1090 x6 / r1091 x1
# contexts measured in the preflight receipt): SEAT faces -> r1091 (W269 seat
# MSG-20261018-1407-bmc-w269-seat @ origin d630d043b9); SPLICE faces ->
# r1091 (W268 splice 8bc7ac759e); FINALIZE faces -> r1091 (W268 finalize
# one-pass 14:0x); PREREG faces -> r1092 (W269 prereg 67fe12710c 14:45);
# cycle face -> r1091 closeout 14:1x.
# Ordinals: owner 258 / bma 130 / bmc 87 live at freeze (probe receipt leg0
# rows=266 post-W268-REGISTERED+FINALIZED); W269 candidate = 259th
# engine-owned, bm-c 88th own wave.
import io, subprocess, sys

CANON = "results/_w268bmc_freeze_edits.py"
DST = "results/_w269bmc_freeze_edits.py"
LOG = "results/_r1093bmc_derive_editor_log.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w268bmc_freeze_edits.py"],
                           capture_output=True, text=True).stdout.strip()
blob_origin = subprocess.run(["git", "rev-parse", "origin/main:results/_w268bmc_freeze_edits.py"],
                             capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head == blob_origin and len(blob_wt) == 40, \
    f"canon blob drift wt={blob_wt} head={blob_head} origin={blob_origin}"

t = io.open(CANON, encoding="utf-8", newline="").read()
log = [f"S0 canon blob verified {blob_wt[:16]} == HEAD == origin twin (preflight-measured sha256_16 a0c5f9209bddc179, 62,187B)",
       f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:100]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W269p", "W270p", 13, "p1_proj_prefix")
rep("W269", "W270", 13, "p1_proj_plain")
# bands: W269 registered A 607_101..609_100 (18th A-hop) / B 609_101..609_300
# (19th above-own-A); naive A 606_901..608_900 refused at registered W268 B
# 606_901..607_100; naive B 607_101..607_300 inside own-A reservation.
# CONSUMERS FIRST (band-order law):
rep("606_901", "609_101", 5, "p1_band_Blo_naiveAlo")
rep("607_100", "609_300", 4, "p1_band_Bhi")
rep("604_901", "607_101", 8, "p1_band_Alo_Bnaivelo")
rep("606_900", "609_100", 9, "p1_band_Ahi")
rep("605_100", "607_300", 2, "p1_band_Bnaivehi")
rep("606_700", "608_900", 2, "p1_band_naiveAhi")
# PRODUCERS LAST (else the fresh 606_901/607_100 tokens double-transform):
rep("604_701", "606_901", 4, "p1_band_priorBlo")
rep("604_900", "607_100", 6, "p1_band_priorBhi")
# ledger/K anchors: W267 finalize facts -> W268 finalize facts (1,013,935/587,520)
rep("1,011,735", "1,013,935", 6, "p1_ledger_prose")
rep("585,320", "587,520", 6, "p1_k_prose")
rep("1_011_735", "1_013_935", 1, "p1_ledger_code")
rep("585_320", "587_520", 1, "p1_k_code")
# lowercase machine-file tokens (own wave first, then upstream wave)
rep("n1_w268", "n1_w269", 4, "p1_n1w268")
rep("n1w268-", "n1w269-", 2, "p1_n1w268dash")
# 12 raw w268_ minus 2 consumed by the n1_w268 rep (n1_w268_results x2)
rep("w268_", "w269_", 10, "p1_lc_w268_")
rep("n1_w267", "n1_w268", 4, "p1_n1w267")
# 93 raw w267_ minus 4 consumed by the n1_w267 rep (n1_w267_results x4)
rep("w267_", "w268_", 89, "p1_lc_w267_")
rep("_w268bmc_", "_w269bmc_", 11, "p1_receiptpath")
rep("MSG-20261018-1229-bmc-w268-seat", "MSG-20261018-1407-bmc-w269-seat", 7, "p1_seat_msg")
rep("b9ad2f1119 r1089", "d630d043b9 r1091", 1, "p1_seat_origin_hdr")
rep('SEAT_ORIGIN = "b9ad2f1119"', 'SEAT_ORIGIN = "d630d043b9"', 1, "p1_seat_origin_const")
rep("7b9e9377", "8bc7ac759e", 1, "p1_lineage_sha")
rep("f1ec8231c7", "67fe12710c", 1, "p1_prereg_sha_ref")
# stale-carried receipt wave field (mechanical +1): 267->268
rep('"wave": 267', '"wave": 268', 1, "p1_receipt_wave")
# header window stamp: this r1093 freeze window
rep("2026-10-18 13:4x bm-c r1091 freeze window", "2026-10-18 15:2x bm-c r1093 freeze window", 1, "p1_hdr_stamp")

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W268", "W269", 92, "p2_own_wave")
rep("W267", "W268", 163, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
# relkey = POST-BLANKET form (the upstream blanket rolled the W267 inside
# "W265_W266_W267_bands_respected" -> "W265_W266_W268"; this rep rolls all
# three positions +1 wave to the W269 probe receipt's relation keys)
rep("W265_W266_W268_bands_respected", "W266_W267_W268_bands_respected", 2, "p3_relkey")
# legs_sec prose + message (W269 extraction: legs W211..W267 = 57)
rep("W211..W266 legs (56)", "W211..W267 legs (57)", 1, "p3_legs_prose")
rep("W211..W266 fifty-six legs", "W211..W267 fifty-seven legs", 1, "p3_legs_msg")
# legs_sec wave-list range (the count itself rides the p3_count56 short needle
# below -- the assert is line-wrapped in the canon, CRLF continuation)
rep("range(211, 267)", "range(211, 268)", 1, "p3_range_legs")
# dropped faces (W269 extraction drops the W268 block's own W248..W267 = 20 legs)
rep("own W248..W266 legs (19)", "own W248..W267 legs (20)", 4, "p3_dropped_narr")
rep("own W248..W266", "own W248..W267", 1, "p3_dropped_split_hdr")
rep("W248..W266 nineteen legs", "W248..W267 twenty legs", 1, "p3_dropped_fstring")
rep('N1_BANDS[") == 19', 'N1_BANDS[") == 20', 1, "p3_dropped_count")
# fullspan error-string (POST-BLANKET wave face rolled by the upstream
# blanket: "W211..W267 legs 56" -> "W211..W268 legs 56"; count 56->57)
rep("W211..W268 legs 56", "W211..W268 legs 57", 1, "p3_fullspan_fstring")
# fresh legs (W269 block appends fresh W248..W268 = 21 legs; POST-BLANKET form)
rep("W248..W268 legs (20", "W248..W269 legs (21", 4, "p3_fresh_narr")
# block/parity counts: W269 block = 69 estate + 37 kept + 21 fresh = 127
rep("block = 126 rows", "block = 127 rows", 1, "p3_block125")
rep("126 parity rows", "127 parity rows", 1, "p3_parity125")
rep("block parity = 126 rows", "block parity = 127 rows", 1, "p3_blockparity_hdr")
rep('N1_BANDS[") == 125,', 'N1_BANDS[") == 126,', 1, "p3_count124")
rep('!= 125', '!= 126', 1, "p3_fstring124")
rep('N1_BANDS[") == 56', 'N1_BANDS[") == 57', 1, "p3_count55")
rep('"fresh_legs_row_asserts": 20', '"fresh_legs_row_asserts": 21', 1, "p3_receipt_fresh19")
rep('+ 20,', '+ 21,', 1, "p3_receipt_total19")
# ranges (fresh FIRST then dropped-producer, then the cumulative/registry faces)
rep("range(248, 268)", "range(248, 269)", 2, "p3_range_fresh")
rep("range(248, 267)", "range(248, 268)", 1, "p3_range_dropped")
rep("range(16, 268)", "range(16, 269)", 2, "p3_range16")
rep("range(17, 268)", "range(17, 269)", 3, "p3_range17")
rep("range(209, 269)", "range(209, 270)", 2, "p3_range209")
# wave-number gates (own 268->269 FIRST, then anti-gate 267->268)
rep("if w < 268)", "if w < 269)", 5, "p3_wlt268")
rep("if w < 267)", "if w < 268)", 1, "p3_wlt267_antigate")
rep("268 - _lw", "269 - _lw", 2, "p3_legcount")
# fresh-legs loop boundary (number face, blankets do not touch bare numbers)
rep("_w == 267", "_w == 268", 1, "p3_freshmsg_cond")
# cfg/row faces: own 268->269 FIRST (band-faces own-first law), then upstream 267->268
rep("WAVE_CONFIGS[268]", "WAVE_CONFIGS[269]", 2, "p3_wavecfg268_own")
rep("WAVE_CONFIGS[267]", "WAVE_CONFIGS[268]", 3, "p3_wavecfg267")
rep("N1_BANDS[267]", "N1_BANDS[268]", 5, "p3_n1bands267")
rep("get(267)", "get(268)", 1, "p3_get267")
rep("_c267", "_c268", 5, "p3_c267var")
rep('268: {"batch"', '269: {"batch"', 2, "p3_cfg268")
rep('268: {{"batch"', '269: {{"batch"', 1, "p3_cfg268_fstring")
rep('268: {"a"', '269: {"a"', 1, "p3_row268_postgate")
rep('268: {{"a"', '269: {{"a"', 2, "p3_row268_fstring")
rep('267: {"batch"', '268: {"batch"', 2, "p3_cfg267")
rep('267: {"a"', '268: {"a"', 3, "p3_row267")
rep("arith_a268", "arith_a269", 6, "p3_arith_a")
rep("arith_b268", "arith_b269", 6, "p3_arith_b")
rep("(264, 263, 262, 261, 260, 259, 258, 257, 256, 255)",
    "(265, 264, 263, 262, 261, 260, 259, 258, 257, 256)", 2, "p3_transitive_list")
rep("W255..W264", "W256..W265", 1, "p3_transitive_window")
# ordinal faces: owner 257->258, bma 130 held, bmc 86->87 (W269 = 259th candidate, bm-c 88th own)
rep("len(owner_rows_live) == 257 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 86",
    "len(owner_rows_live) == 258 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 87", 1, "p3_ordinal_assert")
rep("257/130/86", "258/130/87", 1, "p3_ordinal_expect")
rep("owner_rows=257 / bma_rows=130 / bmc_rows=86", "owner_rows=258 / bma_rows=130 / bmc_rows=87", 1, "p3_leg0_face")
rep("rows 257 + candidate = 258th", "rows 258 + candidate = 259th", 2, "p3_owner256")
rep("; bm-c rows 86 +", "; bm-c rows 87 +", 1, "p3_comment_85split")
rep("bm-c rows 86 + candidate = 87th owned", "bm-c rows 87 + candidate = 88th owned", 1, "p3_receipt_86owned")
rep("# candidate = 87th EXACT", "# candidate = 88th EXACT", 1, "p3_comment_86th")
rep("engine_owner==bm-c rows 86 + candidate", "engine_owner==bm-c rows 87 + candidate", 1, "p3_pr_eo85")
rep("bm-c rows {len(bmc_rows_live)} + candidate (87th own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (88th own wave", 1, "p3_gate0_5_print")
rep("bm-c's 87th own wave", "bm-c's 88th own wave", 2, "p3_86th_own_wave")
rep("EIGHTY-SEVENTH owned", "EIGHTY-EIGHTH owned", 3, "p3_86th_caps")
rep("TWO HUNDRED AND SIXTY-EIGHTH", "TWO HUNDRED AND SIXTY-NINTH", 3, "p3_wave_caps")
# 7 raw bmc_rows=86 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=86", "bmc_rows=87", 6, "p3_bmc_rows85")
rep('"probe_receipt_bmc_ordinal_face": 86', '"probe_receipt_bmc_ordinal_face": 87', 1, "p3_probe_face_key")
# ordinal narrative: B-ordinal EIGHTEENTH->NINETEENTH FIRST, then A-ordinal SEVENTEENTH->EIGHTEENTH
rep("EIGHTEENTH", "NINETEENTH", 7, "p3_17_caps")
rep("SEVENTEENTH", "EIGHTEENTH", 15, "p3_16_caps")
rep("eighteenth", "nineteenth", 4, "p3_17_lc")
rep("seventeenth", "eighteenth", 3, "p3_16_lc")
rep("fifty-sixth", "fifty-seventh", 2, "p3_55th")
# wave-number narrative faces
rep("wave 268 engine_owner=bm-c", "wave 269 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 268: "', '"wave 269: "', 1, "p3_cfg_waveface")
rep("wave 268 = first free number", "wave 269 = first free number", 1, "p3_mhdr_waveface")
# cycle/lineage window stamps (SEAT->r1091 / SPLICE->r1091 / FINALIZE->r1091, contexts measured)
rep("cycle COMPLETE bm-c r1088+r1089 closeout 12:3x", "cycle COMPLETE bm-c r1091 closeout 14:1x", 1, "p3_hdr_complete")
rep("the bm-c r1088 splice window", "the bm-c r1091 splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1088+r1089", "own-wave full cycle r1091", 1, "p3_repair_note")
rep("bm-c splice generation r1088 window", "bm-c splice generation r1091 window", 1, "p3_parity_source_note")
rep("verified r1089", "verified r1091", 1, "p3_lineage_verified")
rep("# r1088 splice window", "# r1091 splice window", 1, "p3_lineage_r1086")
rep("(bm-c r1088", "(bm-c r1091", 1, "p3_parity_comment")
rep("finalize one-pass bm-c r1089 closeout, ledger", "finalize one-pass bm-c r1091 closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1089 closeout ledger", "finalize one-pass bm-c r1091 closeout ledger", 1, "p3_finpass_hdr")
rep("(r1089 MSG-", "(r1091 MSG-", 1, "p3_hdr_msgline")
rep("r1089 BEFORE this freeze", "r1091 BEFORE this freeze", 1, "p3_receipt_seatnote")
rep("seat itself r1089; queue-head", "seat itself r1091; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1089, queue-head seat-first supply", "(r1091, queue-head seat-first supply", 1, "p3_pfcomment_seat")
# prereg window map (W268 prereg r1090 window -> W269 prereg r1092 window)
rep("bm-c r1090 window", "bm-c r1092 window", 4, "p3_prereg_window")
rep("# r1090 window", "# r1092 window", 1, "p3_hdr_prereg_window")
rep("r1090 commit", "r1092 commit", 1, "p3_receipt_commit")
# authored stamp (W269 prereg committed 67fe12710c @ 14:45:22)
rep("authored 13:1x", "authored 14:4x", 2, "p3_authored_stamp")
# lineage header: canon template identity rolls to the W268 canon
rep("_w267bmc_freeze_edits.py template", "_w268bmc_freeze_edits.py template", 1, "p3_lineage_template")
rep("(R267: ", "(R268: ", 1, "p3_repick")
# r1076-family ROOT CURE +1 aging law (NOT the mechanical 267->269 form)
rep("_set_wave(268)", "_set_wave(269)", 1, "p3_setwave_rootcure")

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
for gone in ("r1088", "r1089", "r1090", "12:3x", "13:1x", "authored 13:1x",
            "df55e3fab9", "942ebd5885", "dc71ecc3f9", "7b9e9377", "f1ec8231c7",
            "MSG-20261018-1025-bmc-w267-seat", "MSG-20261018-1229-bmc-w268-seat",
            "_w266bmc_", "_w267bmc_", "w266_", "n1_w266", "n1_w267", "n1w267-",
            "n1w268-", "w267_",
            "604_901", "606_900", "605_100", "606_700",
            "604_701", "604_900",
            "602_501", "602_700", "602_701", "602_900", "604_500",
            "600_301", "600_500", "600_700", "602_300", "600_501", "602_500",
            "598_101", "598_300", "598_301", "600_300", "598_500", "600_100",
            "1,007,335", "580,920", "1_007_335", "580_920",
            "1,009,535", "583,120", "1_009_535", "583_120",
            "1,011,735", "585,320", "1_011_735", "585_320",
            "20261017", "W268p", "W269p",
            "W211..W246", "W211..W264", "W247..W264", "own W247..W264",
            "thirty-six", "fifty-fourth", "fifty-three", "fifty-fifth",
            "fifty-five legs", "fifty-six legs", "fifty-sixth",
            "PENDING at seat", "waits-upstream face disclosed honest",
            "bma_ordinal", "ONE HUNDRED AND THIRTIETH", "EIGHTY-FIFTH owned",
            "EIGHTY-SIXTH owned", "83rd", "84th", "87th",
            "TWO HUNDRED AND SIXTY-SIXTH", "TWO HUNDRED AND SIXTY-SEVENTH",
            "TWO HUNDRED AND SIXTY-EIGHTH",
            "== 123", "!= 123", 'N1_BANDS[") == 124,', '!= 124',
            'N1_BANDS[") == 125,', '!= 125', 'N1_BANDS[") == 56',
            'N1_BANDS[") == 19',
            "N1_BANDS[246] ==", "N1_BANDS\\[246\\]", "m246",
            "N1_BANDS[247] ==", "N1_BANDS\\[247\\]", "m247",
            "FOURTEENTH", "fourteenth", "fifteenth", "FIFTEENTH",
            "rows 255 + candidate", "bmc_rows=84", "bmc_rows=85", "rows 254 + candidate",
            "rows 257 + candidate", "bmc_rows=86", "254/130/83", "owner_rows=254",
            "len(owner_rows_live) == 254", "len(owner_rows_live) == 256",
            "len(owner_rows_live) == 257", "256/130/85",
            "owner_rows=256 / bma_rows=130 / bmc_rows=85",
            "owner_rows=257 / bma_rows=130 / bmc_rows=86", "257/130/86",
            '(R265: ', '(R266: ', "(R267: ", "_w == 265", "_w == 266", "_w == 267",
            "bm-a five-face freeze upstream seat", "bm-a (upstream seat honored)",
            "owner=bm-a seat honored", "(bm-a seat owner expected)",
            "18:2x", "19:2x", "20:5x", "22:4x", "10:2x", "11:2x",
            "editor template", "authored 09:0x", "authored 10:5x",
            "W263_W264_W265_bands_respected", "W264_W265_W267_bands_respected",
            "W265_W266_W267_bands_respected",
            "range(211, 247)", "range(211, 265)", "range(247, 265)",
            "range(247, 266)", "range(16, 266)", "range(17, 266)", "range(209, 268)",
            "range(211, 266)", "range(248, 266)", "range(16, 267)", "range(17, 267)",
            "range(211, 267)", "range(248, 267)", "range(16, 268)", "range(17, 268)",
            "range(209, 269)",
            "if w < 265)", "if w < 266)", "if w < 267)",
            '"wave": 265', '"wave": 266', '"wave": 267',
            "SIXTEENTH", "sixteenth", "SEVENTEENTH", "seventeenth",
            "arith_a267", "arith_b267", "arith_a268", "arith_b268",
            "block = 125 rows", "125 parity rows", "block parity = 121 rows",
            "block = 126 rows", "126 parity rows", "block parity = 126 rows",
            '"fresh_legs_row_asserts": 19', '"fresh_legs_row_asserts": 20',
            "+ 19,", "+ 20,",
            "own W248..W265", "own W248..W266", "W248..W265 eighteen legs",
            "W248..W266 nineteen legs", "W211..W265 legs (55)", "W211..W266 legs (56)",
            "W211..W267 legs 56",
            "len(bmc_rows_live)} + candidate (87th own wave",
            "EIGHTY-SEVENTH owned", "bm-c's 87th own wave",
            "engine_owner==bm-c rows 86 + candidate",
            "268 - _lw", "_set_wave(268)", "_set_wave(267)", "_set_wave(266)",
            "942ebd5885 r1089"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
    'MSG-20261018-1407-bmc-w269-seat': 7, "d630d043b9": 2, "_w269bmc_": 11,
    "20261018": 17, "67fe12710c": 1, "8bc7ac759e": 1,
    "609_101": 5, "609_300": 4, "607_101": 8, "609_100": 9,
    "607_300": 2, "608_900": 2, "606_901": 4, "607_100": 6,
    "1,013,935": 6, "587,520": 6, "1_013_935": 1, "587_520": 1,
    '269: {"batch"': 2, '268: {"batch"': 2, '267: {"batch"': 0,
    '269: {{"batch"': 1, '269: {"a"': 1, '268: {"a"': 3, '269: {{"a"': 2,
    "range(248, 269)": 2, "range(209, 270)": 2, "range(16, 269)": 2,
    "range(17, 269)": 3, "range(211, 248)": 1, "range(211, 268)": 1,
    "range(248, 268)": 1, "range(138, 207)": 1,
    "if w < 269)": 5, "if w < 268)": 1, "269 - _lw": 2,
    "m248": 4, "m211": 4, "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
    "WAVE_CONFIGS[269]": 2, "WAVE_CONFIGS[268]": 3, "N1_BANDS[268]": 5,
    "get(268)": 1, "_c268": 5,
    "arith_a269": 6, "arith_b269": 6,
    "(265, 264, 263, 262, 261, 260, 259, 258, 257, 256)": 2, "W256..W265": 1,
    "len(owner_rows_live) == 258": 1, "258/130/87": 1, "bmc_rows=87": 7,
    "rows 258 + candidate = 259th": 2, "bm-c rows 87 + candidate = 88th owned": 1,
    "EIGHTY-EIGHTH owned": 3, "TWO HUNDRED AND SIXTY-NINTH": 3,
    "NINETEENTH": 7, "EIGHTEENTH": 15, "nineteenth": 4, "eighteenth": 3,
    "W266_W267_W268_bands_respected": 2, "W270p": 13, "W270": 26,
    "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
    "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
    "W269 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
    "the bm-c r1091 splice window": 2,
    "bm-c own seat executed at the bm-c r1091 splice window": 1,
    "finalize one-pass bm-c r1091": 2,
    "authored 14:4x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
    "cycle COMPLETE bm-c r1091 closeout 14:1x": 1,
    "verified r1091": 1, "(R268: ": 1, "_w == 268": 1,
    "wave 269 engine_owner=bm-c": 1, '"wave 269: "': 1,
    "wave 269 = first free number": 1, "fifty-seventh": 2, "fifty-seven legs": 1,
    'N1_BANDS[") == 126,': 1, '!= 126': 1, 'N1_BANDS[") == 57': 1,
    'N1_BANDS[") == 37': 1, 'N1_BANDS[") == 20': 1,
    "W211..W267 legs (57)": 1, "W211..W268 legs 57": 1,
    "own W248..W267 legs (20)": 4, "own W248..W267": 5, "W248..W269 legs (21": 4,
    "block = 127 rows": 1, "127 parity rows": 1, "block parity = 127 rows": 1,
    "bm-c r1092 window": 4, "# r1092 window": 1, "r1092 commit": 1,
    "bm-c splice generation r1091 window": 1, "(bm-c r1091": 1,
    "_w268bmc_freeze_edits.py template": 1,
    "PERPETUAL_N1_W269_PREREG": 8, "PERPETUAL-N1-W269": 7,
    "n1_w269": 4, "n1_w268": 4, "n1w269-": 2,
    "n1_w269_results.json": 2, "n1_w268_results.json": 4,
    "W269 materializer face": 4, "W268 materializer face": 1,
    "W268 finalize product": 4, "W269 block": 4,
    "engine_owner==bm-c rows 87 + candidate": 1,
    "# candidate = 88th EXACT": 1, "; bm-c rows 87 +": 1,
    "bm-c rows {len(bmc_rows_live)} + candidate (88th own wave": 1,
    "bm-c's 88th own wave": 2, "owner_rows=258 / bma_rows=130 / bmc_rows=87": 1,
    '"probe_receipt_bmc_ordinal_face": 87': 1,
    "fourteen-wave": 8, "post-W268-REGISTERED": 8,
    "anchors W268 1,013,935 / K=587,520 at draft": 1,
    "dual-window parity": 1, "W270 walk": 1,
    "fifty-seventh consecutive": 2, '"wave": 268': 1,
    "bma rows 129 + candidate 130th": 1,
    "registered wave below 263 composes": 2,
    "PRE-W269-splice": 1, "post-W268 registration": 2,
    "expect 258/130/87": 1,
    "_set_wave(269)": 1, "_set_wave(268)": 0, "_set_wave(267)": 0, "_set_wave(266)": 0,
    "_set_wave(2)": 1,
    "2026-10-18 15:2x bm-c r1093 freeze window": 1,
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
