# -*- coding: utf-8 -*-
# r1091 bm-c: derive results/_w268bmc_freeze_edits.py from the committed W267
# freeze-edits canon (results/_w267bmc_freeze_edits.py, bm-c r1088 splice
# window 7b9e937737, proven live-fire: W267 five-face splice + engine
# self-burn 12/12 + finalize one-pass ledger 1,011,735 / K=585,320 + W268
# seat published @ origin b9ad2f1119, machine-verified r1089) by
# COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage, zero transcription: every
# needle count MEASURED on the canon blob by
# results/_r1091bmc_needle_preflight.py (receipt
# results/_r1091bmc_needle_preflight.json) + the r1089 handoff baseline
# results/_r1089bmc_w268_editor_handoff.json -- r1077 measured-counts law;
# canon blob 05ae8eeb2c8a0e2d... (sha16 0b39fb0f20c8aa6e) == HEAD twin
# verified in-preflight; canon EOL = pure CRLF 800/0, needles are
# newline-free per the r1088 split_hdr law).
# AGING-TOKEN LAW (E63 anti-drift): frozen faces w244_a/w244_b and
# n3r1_used245 do NOT roll (measured 12/8/3 in canon; carried verbatim,
# anti-drift asserted here; "w244_a holds wave-263 bands" disclosure text
# carries verbatim, measured 4). Band order law: consumers before producers
# (604_701/604_900 consumed BEFORE the 602_501/602_700 producers, else the
# fresh prior-wave B tokens double-transform). Own-first law at every level
# (n1_w267 before n1_w266; w267_ before w266_; W267 blanket before W266
# blanket; '267: {"batch"' before '266: {"batch"'; WAVE_CONFIGS[267] before
# [266]; if w < 267) before if w < 266); ordinal order law: EIGHTEENTH (B,
# above-own-A) rolls before SEVENTEENTH (A, A-hop) -- B-ordinal caps first,
# then A-ordinal, else double-transform.
# SETWAVE +1 AGING LAW (r1076-family ROOT CURE, r1089 handoff): the canon
# carries _set_wave(267) (the healed face); this editor ages it
# rep('_set_wave(267)','_set_wave(268)',1) -- NOT the mechanical 266->268
# form; presence gates _set_wave(268):1 / _set_wave(267):0 / _set_wave(266):0
# / _set_wave(265):0.
# DISCLOSED SAME-WINDOW HEALS (2, zero functional impact):
# (1) stale block-parity header count "W267 block parity = 121 rows" (stale
#     carried since the W263-era 15-fresh-leg structure; machine-true for
#     this generation = 69 estate + 37 kept + 20 fresh = 126) healed at the
#     birth station per the CEO defect-birthplace law 2026-10-16.
# (2) canon header prereg attribution "derived by the bm-a r1087 window"
#     (stale bm-a face carried since the bm-a prereg era) healed to the
#     live fact: the W268 prereg was derived by the bm-c r1090 window
#     (commit f1ec8231c7 13:10:06).
# Window-stamp disambiguation (all 14 r1086 + 7 r1087 measured with
# contexts in the preflight receipt): SEAT faces -> r1089 (W268 seat
# published r1089 @ origin b9ad2f1119); SPLICE faces -> r1088 (W267 splice
# 7b9e937737); FINALIZE faces -> r1089 (W267 finalize one-pass r1089);
# PREREG faces -> r1090 (W268 prereg f1ec8231c7); cycle face -> r1088+r1089.
# Ordinals: owner 257 / bma 130 / bmc 86 live at freeze (probe receipt leg0
# rows=265?? NO -- measured leg0 owner_rows=257 bmc_rows=86; W268 candidate =
# 258th engine-owned, bm-c 87th own wave).
import io, subprocess, sys

CANON = "results/_w267bmc_freeze_edits.py"
DST = "results/_w268bmc_freeze_edits.py"
LOG = "results/_r1091bmc_derive_editor_log.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w267bmc_freeze_edits.py"],
                           capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head and len(blob_wt) == 40, f"canon blob drift wt={blob_wt} head={blob_head}"
assert blob_wt.startswith("05ae8eeb2c8a0e2d"), f"canon face drift vs preflight-measured blob: {blob_wt[:16]}"

t = io.open(CANON, encoding="utf-8", newline="").read()
log = [f"S0 canon blob verified {blob_wt[:16]} == HEAD twin (preflight-measured face 0b39fb0f20c8aa6e)",
       f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:100]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W268p", "W269p", 13, "p1_proj_prefix")
rep("W268", "W269", 13, "p1_proj_plain")
# bands: W268 registered A 604_901..606_900 (17th A-hop) / B 606_901..607_100
# (18th above-own-A); naive A 604_701..606_700 refused at registered W267 B
# 604_701..604_900; naive B 604_901..605_100 inside own-A reservation.
# CONSUMERS FIRST (band-order law):
rep("604_701", "606_901", 5, "p1_band_Blo_naiveAlo")
rep("604_900", "607_100", 4, "p1_band_Bhi")
rep("602_701", "604_901", 8, "p1_band_Alo_Bnaivelo")
rep("604_700", "606_900", 9, "p1_band_Ahi")
rep("602_900", "605_100", 2, "p1_band_Bnaivehi")
rep("604_500", "606_700", 2, "p1_band_naiveAhi")
# PRODUCERS LAST (else the fresh 604_701/604_900 tokens double-transform):
rep("602_501", "604_701", 4, "p1_band_priorBlo")
rep("602_700", "604_900", 6, "p1_band_priorBhi")
# ledger/K anchors: W266 finalize facts -> W267 finalize facts (1,011,735/585,320)
rep("1,009,535", "1,011,735", 6, "p1_ledger_prose")
rep("583,120", "585,320", 6, "p1_k_prose")
rep("1_009_535", "1_011_735", 1, "p1_ledger_code")
rep("583_120", "585_320", 1, "p1_k_code")
# lowercase machine-file tokens (own wave first, then upstream wave)
rep("n1_w267", "n1_w268", 4, "p1_n1w267")
rep("n1w267-", "n1w268-", 2, "p1_n1w267dash")
# 12 raw w267_ minus 2 consumed by the n1_w267 rep (n1_w267_results x2)
rep("w267_", "w268_", 10, "p1_lc_w267_")
rep("n1_w266", "n1_w267", 4, "p1_n1w266")
# 93 raw w266_ minus 4 consumed by the n1_w266 rep (n1_w266_results x4)
rep("w266_", "w267_", 89, "p1_lc_w266_")
rep("_w267bmc_", "_w268bmc_", 11, "p1_receiptpath")
rep("MSG-20261018-1025-bmc-w267-seat", "MSG-20261018-1229-bmc-w268-seat", 7, "p1_seat_msg")
rep("942ebd5885 r1086", "b9ad2f1119 r1089", 1, "p1_seat_origin_hdr")
rep('SEAT_ORIGIN = "942ebd5885"', 'SEAT_ORIGIN = "b9ad2f1119"', 1, "p1_seat_origin_const")
rep("dc71ecc3f9", "7b9e9377", 1, "p1_lineage_sha")
rep("df55e3fab9", "f1ec8231c7", 1, "p1_prereg_sha_ref")
# stale-carried receipt wave field (heal lineage, mechanical +1): 266->267
rep('"wave": 266', '"wave": 267', 1, "p1_receipt_wave")
# header window stamp: this r1091 freeze window
rep("2026-10-18 11:2x bm-c r1088 freeze window", "2026-10-18 13:4x bm-c r1091 freeze window", 1, "p1_hdr_stamp")

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W267", "W268", 92, "p2_own_wave")
rep("W266", "W267", 163, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
rep("W264_W265_W267_bands_respected", "W265_W266_W267_bands_respected", 2, "p3_relkey")
# legs_sec prose + message (W268 extraction: legs W211..W266 = 56)
rep("W211..W265 legs (55)", "W211..W266 legs (56)", 1, "p3_legs_prose")
rep("W211..W265 fifty-five legs", "W211..W266 fifty-six legs", 1, "p3_legs_msg")
# legs_sec wave-list range (the count itself rides the p3_count55 short needle
# below -- the assert is line-wrapped in the canon, CRLF continuation)
rep("range(211, 266)", "range(211, 267)", 1, "p3_range_legs")
# dropped faces (W268 extraction drops the W267 block's own W248..W266 = 19 legs)
rep("own W248..W265 legs (18)", "own W248..W266 legs (19)", 4, "p3_dropped_narr")
rep("own W248..W265", "own W248..W266", 1, "p3_dropped_split_hdr")
rep("W248..W265 eighteen legs", "W248..W266 nineteen legs", 1, "p3_dropped_fstring")
rep('N1_BANDS[") == 18', 'N1_BANDS[") == 19', 1, "p3_dropped_count")
# fullspan error-string (post-D wave face rolled by the blanket): count 55->56
rep("W211..W267 legs 55", "W211..W267 legs 56", 1, "p3_fullspan_fstring")
# fresh legs (W268 block appends fresh W248..W267 = 20 legs; post-D form)
rep("W248..W267 legs (19", "W248..W267 legs (20", 4, "p3_fresh_narr")
# block/parity counts: W268 block = 69 estate + 37 kept + 20 fresh = 126
rep("block = 125 rows", "block = 126 rows", 1, "p3_block125")
rep("125 parity rows", "126 parity rows", 1, "p3_parity125")
rep('N1_BANDS[") == 124,', 'N1_BANDS[") == 125,', 1, "p3_count124")
rep('!= 124', '!= 125', 1, "p3_fstring124")
rep('N1_BANDS[") == 55', 'N1_BANDS[") == 56', 1, "p3_count55")
rep('"fresh_legs_row_asserts": 19', '"fresh_legs_row_asserts": 20', 1, "p3_receipt_fresh19")
rep('+ 19,', '+ 20,', 1, "p3_receipt_total19")
# DISCLOSED HEAL #1 (see header): stale block-parity header count 121 -> 126
rep("block parity = 121 rows", "block parity = 126 rows", 1, "p3_blockparity_heal")
# ranges (fresh FIRST then dropped-producer, then the cumulative/registry faces)
rep("range(248, 267)", "range(248, 268)", 2, "p3_range_fresh")
rep("range(248, 266)", "range(248, 267)", 1, "p3_range_dropped")
rep("range(16, 267)", "range(16, 268)", 2, "p3_range16")
rep("range(17, 267)", "range(17, 268)", 3, "p3_range17")
rep("range(209, 268)", "range(209, 269)", 2, "p3_range209")
# wave-number gates (own 267->268 FIRST, then anti-gate 266->267)
rep("if w < 267)", "if w < 268)", 5, "p3_wlt267")
rep("if w < 266)", "if w < 267)", 1, "p3_wlt266_antigate")
rep("267 - _lw", "268 - _lw", 2, "p3_legcount")
# cfg/row faces: own 267->268 FIRST (band-faces own-first law), then upstream 266->267
rep("WAVE_CONFIGS[267]", "WAVE_CONFIGS[268]", 2, "p3_wavecfg267_own")
rep("WAVE_CONFIGS[266]", "WAVE_CONFIGS[267]", 3, "p3_wavecfg266")
rep("N1_BANDS[266]", "N1_BANDS[267]", 5, "p3_n1bands266")
rep("get(266)", "get(267)", 1, "p3_get266")
rep("_c266", "_c267", 5, "p3_c266var")
rep('267: {"batch"', '268: {"batch"', 2, "p3_cfg267")
rep('267: {{"batch"', '268: {{"batch"', 1, "p3_cfg267_fstring")
rep('267: {"a"', '268: {"a"', 1, "p3_row267_postgate")
rep('267: {{"a"', '268: {{"a"', 2, "p3_row267_fstring")
rep('266: {"batch"', '267: {"batch"', 2, "p3_cfg266")
rep('266: {"a"', '267: {"a"', 3, "p3_row266")
rep("arith_a267", "arith_a268", 6, "p3_arith_a")
rep("arith_b267", "arith_b268", 6, "p3_arith_b")
rep("(263, 262, 261, 260, 259, 258, 257, 256, 255, 254)",
    "(264, 263, 262, 261, 260, 259, 258, 257, 256, 255)", 2, "p3_transitive_list")
rep("W254..W263", "W255..W264", 1, "p3_transitive_window")
# ordinal faces: owner 256->257, bma 130 held, bmc 85->86 (W268 = 258th candidate, bm-c 87th own)
rep("len(owner_rows_live) == 256 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 85",
    "len(owner_rows_live) == 257 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 86", 1, "p3_ordinal_assert")
rep("256/130/85", "257/130/86", 1, "p3_ordinal_expect")
rep("owner_rows=256 / bma_rows=130 / bmc_rows=85", "owner_rows=257 / bma_rows=130 / bmc_rows=86", 1, "p3_leg0_face")
rep("rows 256 + candidate = 257th", "rows 257 + candidate = 258th", 2, "p3_owner256")
rep("; bm-c rows 85 +", "; bm-c rows 86 +", 1, "p3_comment_85split")
rep("bm-c rows 85 + candidate = 86th owned", "bm-c rows 86 + candidate = 87th owned", 1, "p3_receipt_86owned")
rep("# candidate = 86th EXACT", "# candidate = 87th EXACT", 1, "p3_comment_86th")
rep("engine_owner==bm-c rows 85 + candidate", "engine_owner==bm-c rows 86 + candidate", 1, "p3_pr_eo85")
rep("bm-c rows {len(bmc_rows_live)} + candidate (86th own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (87th own wave", 1, "p3_gate0_5_print")
rep("bm-c's 86th own wave", "bm-c's 87th own wave", 2, "p3_86th_own_wave")
rep("EIGHTY-SIXTH owned", "EIGHTY-SEVENTH owned", 3, "p3_86th_caps")
rep("TWO HUNDRED AND SIXTY-SEVENTH", "TWO HUNDRED AND SIXTY-EIGHTH", 3, "p3_wave_caps")
# 7 raw bmc_rows=85 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=85", "bmc_rows=86", 6, "p3_bmc_rows85")
rep('"probe_receipt_bmc_ordinal_face": 85', '"probe_receipt_bmc_ordinal_face": 86', 1, "p3_probe_face_key")
# ordinal narrative: B-ordinal SEVENTEENTH->EIGHTEENTH FIRST, then A-ordinal SIXTEENTH->SEVENTEENTH
rep("SEVENTEENTH", "EIGHTEENTH", 7, "p3_17_caps")
rep("SIXTEENTH", "SEVENTEENTH", 15, "p3_16_caps")
rep("seventeenth", "eighteenth", 4, "p3_17_lc")
rep("sixteenth", "seventeenth", 3, "p3_16_lc")
rep("fifty-fifth", "fifty-sixth", 2, "p3_55th")
# wave-number narrative faces
rep("wave 267 engine_owner=bm-c", "wave 268 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 267: "', '"wave 268: "', 1, "p3_cfg_waveface")
rep("wave 267 = first free number", "wave 268 = first free number", 1, "p3_mhdr_waveface")
# cycle/lineage window stamps (SEAT->r1089 / SPLICE->r1088 / FINALIZE->r1089, contexts measured)
rep("cycle COMPLETE bm-c r1085+r1086 closeout 10:5x", "cycle COMPLETE bm-c r1088+r1089 closeout 12:3x", 1, "p3_hdr_complete")
rep("the bm-c r1086 splice window", "the bm-c r1088 splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1086", "own-wave full cycle r1088+r1089", 1, "p3_repair_note")
rep("bm-c splice generation r1086 window", "bm-c splice generation r1088 window", 1, "p3_parity_source_note")
rep("verified r1087", "verified r1089", 1, "p3_lineage_verified")
rep("# r1086 splice window", "# r1088 splice window", 1, "p3_lineage_r1086")
rep("(bm-c r1086", "(bm-c r1088", 1, "p3_parity_comment")
rep("finalize one-pass bm-c r1086 closeout, ledger", "finalize one-pass bm-c r1089 closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1086 closeout ledger", "finalize one-pass bm-c r1089 closeout ledger", 1, "p3_finpass_hdr")
rep("(r1086 MSG-", "(r1089 MSG-", 1, "p3_hdr_msgline")
rep("r1086 BEFORE this freeze", "r1089 BEFORE this freeze", 1, "p3_receipt_seatnote")
rep("seat itself r1086; queue-head", "seat itself r1089; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1086, queue-head seat-first supply", "(r1089, queue-head seat-first supply", 1, "p3_pfcomment_seat")
# prereg window map (W267 prereg r1087 window -> W268 prereg r1090 window)
rep("bm-c r1087 window", "bm-c r1090 window", 4, "p3_prereg_window")
rep("# r1087 window", "# r1090 window", 1, "p3_hdr_prereg_window")
rep("r1087 commit", "r1090 commit", 1, "p3_receipt_commit")
# DISCLOSED HEAL #2 (see header): stale bm-a prereg attribution -> live fact bm-c
rep("derived by the bm-a", "derived by the bm-c", 1, "p3_hdr_attr_heal")
# authored stamp (W268 prereg committed f1ec8231c7 @ 13:10:06)
rep("authored 10:5x", "authored 13:1x", 2, "p3_authored_stamp")
# lineage header: canon template identity rolls to the W267 canon
rep("_w266bmc_freeze_edits.py template", "_w267bmc_freeze_edits.py template", 1, "p3_lineage_template")
rep("(R266: ", "(R267: ", 1, "p3_repick")
rep("_w == 266", "_w == 267", 1, "p3_freshmsg_cond")
# r1076-family ROOT CURE +1 aging law (r1089 handoff; NOT the mechanical 266->268 form)
rep("_set_wave(267)", "_set_wave(268)", 1, "p3_setwave_rootcure")

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
for gone in ("r1085", "r1086", "r1087", "df55e3fab9", "942ebd5885", "dc71ecc3f9",
            "MSG-20261018-1025-bmc-w267-seat", "_w266bmc_", "w265_", "n1_w265",
            "n1_w266", "n1w266-", "w266_",
            "602_501", "602_700", "602_701", "602_900", "604_500", "604_700",
            "600_301", "600_500", "600_700", "602_300", "600_501", "602_500",
            "598_101", "598_300", "598_301", "600_300", "598_500", "600_100",
            "1,007,335", "580,920", "1_007_335", "580_920",
            "1,009,535", "583,120", "1_009_535", "583_120",
            "20261017", "W267p", "W268p",
            "W211..W246", "W211..W264", "W247..W264", "own W247..W264",
            "thirty-six", "fifty-fourth", "fifty-three",
            "PENDING at seat", "waits-upstream face disclosed honest",
            "bma_ordinal", "ONE HUNDRED AND THIRTIETH", "EIGHTY-FIFTH owned",
            "EIGHTY-SIXTH owned", "83rd", "84th", "86th",
            "TWO HUNDRED AND SIXTY-SIXTH", "TWO HUNDRED AND SIXTY-SEVENTH",
            "== 123", "!= 123", 'N1_BANDS[") == 124,', '!= 124',
            "N1_BANDS[246] ==", "N1_BANDS\\[246\\]", "m246",
            "FOURTEENTH", "fourteenth", "fifteenth", "FIFTEENTH",
            "rows 255 + candidate", "bmc_rows=84", "bmc_rows=85", "rows 254 + candidate",
            "rows 256 + candidate", "254/130/83", "owner_rows=254",
            "len(owner_rows_live) == 254", "len(owner_rows_live) == 256",
            "256/130/85", "owner_rows=256 / bma_rows=130 / bmc_rows=85",
            "(R265: ", "(R266: ", "_w == 265", "_w == 266",
            "bm-a five-face freeze upstream seat", "bm-a (upstream seat honored)",
            "owner=bm-a seat honored", "(bm-a seat owner expected)",
            "18:2x", "19:2x", "20:5x", "22:4x", "10:2x", "11:2x",
            "editor template", "authored 09:0x", "authored 10:5x",
            "W263_W264_W265_bands_respected", "W264_W265_W267_bands_respected",
            "range(211, 247)", "range(211, 265)", "range(247, 265)",
            "range(247, 266)", "range(16, 266)", "range(17, 266)", "range(209, 267)",
            "range(211, 266)", "range(248, 266)", "range(16, 267)", "range(17, 267)",
            "range(209, 268)",
            "if w < 265)", "if w < 266)",
            "m247", "N1_BANDS[247] ==", "N1_BANDS\\[247\\]",
            '"wave": 265', '"wave": 266',
            "SIXTEENTH", "sixteenth", "fifty-fifth", "fifty-five legs",
            "arith_a267", "arith_b267",
            "block = 125 rows", "125 parity rows", "block parity = 121 rows",
            '"fresh_legs_row_asserts": 19', "+ 19,",
            "own W248..W265", "W248..W265 eighteen legs"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
    'MSG-20261018-1229-bmc-w268-seat': 7, "b9ad2f1119": 2, "_w268bmc_": 11,
    "20261018": 17, "f1ec8231c7": 1, "7b9e9377": 1,
    "606_901": 5, "607_100": 4, "604_901": 8, "606_900": 9,
    "605_100": 2, "606_700": 2, "604_701": 4, "604_900": 6,
    "1,011,735": 6, "585,320": 6, "1_011_735": 1, "585_320": 1,
    '268: {"batch"': 2, '267: {"batch"': 2, '266: {"batch"': 0,
    '268: {{"batch"': 1, '268: {"a"': 1, '267: {"a"': 3, '268: {{"a"': 2,
    "range(248, 268)": 2, "range(209, 269)": 2, "range(16, 268)": 2,
    "range(17, 268)": 3, "range(211, 248)": 1, "range(211, 267)": 1,
    "range(248, 267)": 1, "range(138, 207)": 1,
    "if w < 268)": 5, "if w < 267)": 1, "268 - _lw": 2,
    "m248": 4, "m211": 4, "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
    "WAVE_CONFIGS[268]": 2, "WAVE_CONFIGS[267]": 3, "N1_BANDS[267]": 5,
    "get(267)": 1, "_c267": 5,
    "arith_a268": 6, "arith_b268": 6,
    "(264, 263, 262, 261, 260, 259, 258, 257, 256, 255)": 2, "W255..W264": 1,
    "len(owner_rows_live) == 257": 1, "257/130/86": 1, "bmc_rows=86": 7,
    "rows 257 + candidate = 258th": 2, "bm-c rows 86 + candidate = 87th owned": 1,
    "EIGHTY-SEVENTH owned": 3, "TWO HUNDRED AND SIXTY-EIGHTH": 3,
    "EIGHTEENTH": 7, "SEVENTEENTH": 15, "eighteenth": 4, "seventeenth": 3,
    "W265_W266_W267_bands_respected": 2, "W269p": 13, "W269": 26,
    "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
    "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
    "W268 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
    "the bm-c r1088 splice window": 2,
    "bm-c own seat executed at the bm-c r1088 splice window": 1,
    "finalize one-pass bm-c r1089": 2,
    "authored 13:1x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
    "cycle COMPLETE bm-c r1088+r1089 closeout 12:3x": 1,
    "verified r1089": 1, "(R267: ": 1, "_w == 267": 1,
    "wave 268 engine_owner=bm-c": 1, '"wave 268: "': 1,
    "wave 268 = first free number": 1, "fifty-sixth": 2, "fifty-six legs": 1,
    'N1_BANDS[") == 125,': 1, '!= 125': 1, 'N1_BANDS[") == 56': 1,
    'N1_BANDS[") == 37': 1,
    "W211..W266 legs (56)": 1, "W211..W267 legs 56": 1,
    "own W248..W266 legs (19)": 4, "own W248..W266": 5, "W248..W267 legs (20": 4,
    "block = 126 rows": 1, "126 parity rows": 1, "block parity = 126 rows": 1,
    "bm-c r1090 window": 4, "# r1090 window": 1, "r1090 commit": 1,
    "bm-c splice generation r1088 window": 1, "(bm-c r1088": 1,
    "_w267bmc_freeze_edits.py template": 1,
    "PERPETUAL_N1_W268_PREREG": 8, "PERPETUAL-N1-W268": 7,
    "n1_w268": 4, "n1_w267": 4, "n1w268-": 2,
    "n1_w267_results.json": 4, "n1_w268_results.json": 2,
    "W268 materializer face": 4, "W267 materializer face": 1,
    "W267 finalize product": 4, "W268 block": 4,
    "engine_owner==bm-c rows 86 + candidate": 1,
    "# candidate = 87th EXACT": 1, "; bm-c rows 86 +": 1,
    "bm-c rows {len(bmc_rows_live)} + candidate (87th own wave": 1,
    "bm-c's 87th own wave": 2, "owner_rows=257 / bma_rows=130 / bmc_rows=86": 1,
    '"probe_receipt_bmc_ordinal_face": 86': 1,
    "fourteen-wave": 8, "post-W267-REGISTERED": 8,
    "anchors W267 1,011,735 / K=585,320 at draft": 1,
    "dual-window parity": 1, "W269 walk": 1,
    "fifty-sixth consecutive": 2, '"wave": 267': 1,
    "bma rows 129 + candidate 130th": 1,
    "registered wave below 263 composes": 2,
    "PRE-W268-splice": 1, "post-W267 registration": 2,
    "expect 257/130/86": 1,
    "_set_wave(268)": 1, "_set_wave(267)": 0, "_set_wave(266)": 0, "_set_wave(265)": 0,
    "_set_wave(2)": 1,
    "2026-10-18 13:4x bm-c r1091 freeze window": 1,
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
