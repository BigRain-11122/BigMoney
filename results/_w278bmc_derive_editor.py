# -*- coding: utf-8 -*-
# r1118 bm-c splice window: derive results/_w278bmc_freeze_edits.py from the
# committed W277 freeze-edits canon (results/_w277bmc_freeze_edits.py, bm-c
# r1114 splice window 9e53371814, proven live-fire: W277 five-face splice +
# engine self-burn 12/12 + finalize one-pass ledger 1,033,735 / K=607,320
# EXACT, machine-verified by the r1114-continuation closeout efc4a1c1bb)
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 22nd-gen lineage, zero
# transcription: every needle count MEASURED on the canon blob by
# results/_r1118bmc_needle_preflight.py (receipt
# results/_r1118bmc_needle_preflight.json, canon sha256-16 d4913e4ad111fd85,
# 62,353B, wt==HEAD==origin triple-verified; sim + post-blanket phase-3 forms
# measured; FIRST-RUN zero-mismatch = the rolled table measured exact, zero
# preflight-table heals needed this generation). r1077 measured-counts law.
# DISCLOSED CANON EOL FACE (benign, carried): core.autocrlf=true re-smudge
# (r1093 pit entry) -- canon read raw with newline='' (CRLF form); multi-line
# needles use the physical CRLF bytes (r775 law).
# W278 FACTS (probe receipt results/_w278bmc_20261019_probe_receipt.json,
# committed with the seat @ b187aa6214 r1114-continuation, ADMIT): bands A
# 626_901..628_900 (TWENTY-SEVENTH consecutive A-hop, staircase-affects-A,
# hops=1; naive A 626_701..628_700 refused at the registered W277 B band
# 626_701..626_900) / B 628_901..629_100 (TWENTY-EIGHTH consecutive
# above-own-A, own-A reservation cascade, hops=1; naive B 626_901..627_100
# inside the own-A window 626_901..628_900); seed_admit FREE x2 (base=626901
# span=2000 / base=628901 span=200); ordinals owner 267 + candidate = 268th /
# bm-c rows 96 + candidate = 97th; W277 finalize anchors 1,033,735 / K=607,320
# (chain +2,200/+2,200 EXACT); leg4 W279+ projection naive A 628_901..630_900 /
# naive B 629_101..629_300 (pre-W278 universe; W279p_B_lands_inside_W279p_A_naive
# staircase face per the frozen W278 prereg sec.5 item5).
# W278 PREREG: research/PERPETUAL_N1_W278_PREREG.md 23,814B sha256_16
# 99001d3d3f337942 (authored 12:2x bm-c r1116 window via E63 canon-clone
# builder _r1116bmc_build_w278_derive.py; frozen + push-race healed over bm-a
# x3 -> landed origin df1aaba72a, r1116 window).
# AGING-TOKEN LAW (E63 anti-drift, carried): frozen faces w244_a/w244_b /
# n3r1_used245 / m211 / m248 / "w244_a holds wave-263 bands" /
# "registered wave below 263 composes" do NOT roll (measured 12/8/3/4/4/2
# in canon; carried verbatim, anti-drift asserted). Band order law:
# CONSUMERS before PRODUCERS (626_701/626_900 consumed BEFORE 624_501/624_700
# recreate them). Projections first (W279p -> W278p-order mirror: canon
# W278p rolls to W279p before plain W278 -> W279), then D-swaps (own W277 ->
# W278 first, then upstream W276 -> W277). Ordinal caps: B
# (TWENTY-SEVENTH -> TWENTY-EIGHTH) before A (TWENTY-SIXTH -> TWENTY-SEVENTH).
# lc blankets: own w277_ (10, after n1_w277_results.json x2 + builder x1
# carve-outs) before upstream w276_ (89, after n1_w276_results.json x4
# carve-outs).
# SETWAVE +1 AGING LAW (r1076-family root cure, carried): _set_wave(277) ->
# _set_wave(278); presence gates 278:1 / 277:0 / 276:0.
# DATE-ROLL FACE (count 0 this generation, DISCLOSED): canon receipts already
# dated 20261019 and the W278 seat/probe/prereg receipts are same-date -- no
# date-roll rep this generation (zero 20261018 faces in canon,
# preflight-measured); the "20261019" x17 gate carries verbatim.
# Window-stamp disambiguation (measured): SEAT faces -> r1114-continuation
# (W278 seat b187aa6214 10:3x); SPLICE/FINALIZE/CYCLE-COMPLETE faces ->
# r1114-continuation (W277 splice 9e53371814 09:5x + finalize one-pass 10:3x +
# cycle-complete closeout efc4a1c1bb 10:4x -- the whole W277 chain is labeled
# r1114-continuation per the frozen W278 prereg usage; the bare-r1114 face
# lives ONLY inside the r1114-continuation compound, never standalone);
# PREREG faces -> r1116 (W278 prereg df1aaba72a); THIS splice window -> r1118.
import io, subprocess, sys

CANON = "results/_w277bmc_freeze_edits.py"
DST = "results/_w278bmc_freeze_edits.py"
LOG = "results/_r1118bmc_derive_editor_log.txt"
CRLF = "\r\n"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:" + CANON],
                           capture_output=True, text=True).stdout.strip()
blob_origin = subprocess.run(["git", "rev-parse", "origin/main:" + CANON],
                              capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head == blob_origin and len(blob_wt) == 40, \
    f"canon blob drift wt={blob_wt} head={blob_head} origin={blob_origin}"

t = io.open(CANON, encoding="utf-8", newline="").read()
assert t.count(CRLF) > t.count("\n") - t.count(CRLF), "canon EOL face drift (CRLF expected)"
log = [f"S0 canon blob verified {blob_wt[:16]} == HEAD == origin twin "
       f"(preflight-measured sha256-16 d4913e4ad111fd85, 62,353B)",
       f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:110]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W278p", "W279p", 13, "p1_proj_prefix")
rep("W278", "W279", 13, "p1_proj_plain")
# bands (CONSUMERS FIRST: 626_701/626_900 consumed before 624_501/624_700
# recreate them -- band-order law; all 8 rep targets measured 5/4/9/2/8/2/4/6)
rep("626_701", "628_901", 5, "p1_band_Blo")
rep("626_900", "629_100", 4, "p1_band_Bhi")
rep("626_700", "628_900", 9, "p1_band_Ahi")
rep("626_500", "628_700", 2, "p1_band_naiveAhi")
rep("624_701", "626_901", 8, "p1_band_Alo_Bnaivelo")
rep("624_900", "627_100", 2, "p1_band_Bnaivehi")
rep("624_501", "626_701", 4, "p1_band_naiveAlo_priorBlo")
rep("624_700", "626_900", 6, "p1_band_priorBhi")
# int-form leg4 projections in the receipt downstream_seat note (probe-measured)
rep("626701", "628901", 1, "p1_int_projAlo")
rep("628700", "630900", 1, "p1_int_projAhi")
rep("626901", "629101", 2, "p1_int_projBlo")
rep("627100", "629300", 2, "p1_int_projBhi")
# ledger/K anchors: W276 finalize facts -> W277 finalize facts (1,033,735/607,320)
rep("1,031,535", "1,033,735", 6, "p1_ledger_prose")
rep("605,120", "607,320", 6, "p1_k_prose")
rep("1_031_535", "1_033_735", 1, "p1_ledger_code")
rep("605_120", "607_320", 1, "p1_k_code")
# builder filename FIRST (consumes its embedded w277_ before the lc blanket)
rep("(E63 canon-clone builder _r1113bmc_build_w277_derive.py)",
    "(E63 canon-clone builder _r1116bmc_build_w278_derive.py)", 1, "p1_builder_method")
# lowercase machine-file tokens (own first, then upstream; the w277_ blanket
# ALSO rolls the current-wave pickaxe vars w277_prereg_sha/w277_receipt_sha ->
# w278_* AFTER the n1_w277_results.json x2 + builder x1 carve-outs; the
# w276_ blanket rolls ALL upstream w276_* variables -> w277_* after the
# n1_w276_results.json x4 carve-out)
rep("n1_w277", "n1_w278", 4, "p1_n1w277_own")
rep("n1w277-", "n1w278-", 2, "p1_n1w277dash")
rep("w277_", "w278_", 10, "p1_lc_w277_")
rep("n1_w276", "n1_w277", 4, "p1_n1w276_upstream")
rep("w276_", "w277_", 89, "p1_lc_w276_")
# receipt/lineage/seat faces
rep("_w277bmc_", "_w278bmc_", 11, "p1_receiptpath")
rep("_w276bmc_freeze_edits.py template", "_w277bmc_freeze_edits.py template", 1, "p1_lineage_template")
rep("MSG-20261019-080x-bmc-w277-seat", "MSG-20261019-102x-bmc-w278-seat", 7, "p1_seat_msg")
rep('SEAT_ORIGIN = "c5f8b88f91"', 'SEAT_ORIGIN = "b187aa6214"', 1, "p1_seat_origin_const")
rep("c5f8b88f91 r1112", "b187aa6214 r1114-continuation", 1, "p1_seat_origin_hdr")
rep("354a645155", "9e53371814", 1, "p1_lineage_sha")
# prereg delivery prose (r1116 push-race-healed landing + E63 builder method;
# CRLF-joined needle per the preflight verbatim extraction)
rep("(authored 09:0x, banned_direction_gate ADMIT rc0, frozen sha16 45ee1de94c7d36fd + CAS-" + CRLF +
    "# surgical-pushed to origin e0bc4a0ddd, r1113 window).",
    "(authored 12:2x, banned_direction_gate ADMIT rc0, frozen sha16 99001d3d3f337942 + push-race-" + CRLF +
    "# healed landed to origin df1aaba72a, r1116 window).",
    1, "p1_prereg_delivery_hdr")
rep("(authored 09:0x, banned gate ADMIT rc0, frozen 45ee1de94c7d36fd -> CAS-surgical r1113 origin ",
    "(authored 12:2x, banned gate ADMIT rc0, frozen 99001d3d3f337942 -> push-race-healed r1116 origin ",
    1, "p1_prereg_delivery_note")
# header window stamp
rep("2026-10-19 09:3x bm-c r1114 splice window", "2026-10-19 13:3x bm-c r1118 splice window", 1, "p1_hdr_stamp")
# receipt wave field (mechanical +1): 276->277
rep('"wave": 276', '"wave": 277', 1, "p1_receipt_wave")
# DATE ROLL: DROPPED this generation (20261019 == 20261019, count-0 face,
# preflight-measured zero 20261018 in canon; disclosed in header)

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W277", "W278", 96, "p2_own_wave")
rep("W276", "W277", 158, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
# relkey = POST-BLANKET form (the upstream blanket rolled the W276 inside
# "W274_W275_W276_bands_respected" -> "W274_W275_W277"; this rep rolls the
# first two positions +1 to the W278 probe receipt's relation keys)
rep("W274_W275_W277_bands_respected", "W275_W276_W277_bands_respected", 2, "p3_relkey")
# legs_sec prose + message (W278 extraction: legs W211..W276 = 66)
rep("W211..W275 legs (65)", "W211..W276 legs (66)", 1, "p3_legs_prose")
rep("W211..W275 sixty-five legs", "W211..W276 sixty-six legs", 1, "p3_legs_msg")
rep("range(211, 276)", "range(211, 277)", 1, "p3_range_legs")
# dropped faces (W278 extraction drops the W277 block's own W248..W276 = 29 legs)
rep("own W248..W275 legs (28)", "own W248..W276 legs (29)", 4, "p3_dropped_narr")
rep("own W248..W275" + CRLF + "# legs (28 rows) do NOT enter the estate path",
    "own W248..W276" + CRLF + "# legs (29 rows) do NOT enter the estate path", 1, "p3_dropped_split_hdr")
rep("W248..W275 twenty-eight legs", "W248..W276 twenty-nine legs", 1, "p3_dropped_fstring")
rep('N1_BANDS[") == 28', 'N1_BANDS[") == 29', 1, "p3_dropped_count")
# fullspan error-string (POST-BLANKET wave face rolled by the upstream
# blanket: "W211..W276 legs 65" -> "W211..W277 legs 65"; count 65->66)
rep("W211..W277 legs 65", "W211..W277 legs 66", 1, "p3_fullspan_fstring")
# fresh legs (W278 block appends fresh W248..W277 = 30 legs; POST-OWN-BLANKET
# form -- the own blanket rolled the hi face to the new range end 278;
# count-only roll 29->30, hi rides the blanket = range(248, 278) END EXACT)
rep("W248..W278 legs (29", "W248..W278 legs (30", 4, "p3_fresh_narr")
# block/parity counts: W278 block = 69 estate + 37 kept + 30 fresh = 136
rep("block = 135 rows", "block = 136 rows", 1, "p3_block131")
rep("135 parity rows", "136 parity rows", 1, "p3_parity131")
rep("block parity = 135 rows", "block parity = 136 rows", 1, "p3_blockparity131")
rep('N1_BANDS[") == 134,', 'N1_BANDS[") == 135,', 1, "p3_count130")
rep('!= 134', '!= 135', 1, "p3_fstring130")
rep('N1_BANDS[") == 65', 'N1_BANDS[") == 66', 1, "p3_count61")
rep('"fresh_legs_row_asserts": 29', '"fresh_legs_row_asserts": 30', 1, "p3_receipt_fresh")
rep('+ 29,', '+ 30,', 1, "p3_receipt_total")
# ranges (fresh FIRST then dropped-producer, then the cumulative/registry faces)
rep("range(248, 277)", "range(248, 278)", 2, "p3_range_fresh")
rep("range(248, 276)", "range(248, 277)", 1, "p3_range_dropped")
rep("range(16, 277)", "range(16, 278)", 2, "p3_range16")
rep("range(17, 277)", "range(17, 278)", 3, "p3_range17")
rep("range(209, 278)", "range(209, 279)", 2, "p3_range209")
# wave-number gates (own 277->278 FIRST, then anti-gate 276->277)
rep("if w < 277)", "if w < 278)", 5, "p3_wlt277")
rep("if w < 276)", "if w < 277)", 1, "p3_wlt276_antigate")
rep("277 - _lw", "278 - _lw", 2, "p3_legcount")
rep("_w == 276", "_w == 277", 1, "p3_freshmsg_cond")
# cfg/row faces: own 277->278 FIRST, then upstream 276->277
rep("WAVE_CONFIGS[277]", "WAVE_CONFIGS[278]", 2, "p3_wavecfg277_own")
rep("WAVE_CONFIGS[276]", "WAVE_CONFIGS[277]", 3, "p3_wavecfg276")
rep("N1_BANDS[276]", "N1_BANDS[277]", 5, "p3_n1bands276")
rep("get(276)", "get(277)", 1, "p3_get276")
rep("_c276", "_c277", 5, "p3_c276var")
rep('277: {"batch"', '278: {"batch"', 2, "p3_cfg277")
rep('277: {{"batch"', '278: {{"batch"', 1, "p3_cfg277_fstring")
rep('277: {"a"', '278: {"a"', 1, "p3_row277")
rep('277: {{"a"', '278: {{"a"', 2, "p3_row277_fstring")
rep('276: {"batch"', '277: {"batch"', 2, "p3_cfg276")
rep('276: {"a"', '277: {"a"', 3, "p3_row276")
rep("arith_a277", "arith_a278", 6, "p3_arith_a")
rep("arith_b277", "arith_b278", 6, "p3_arith_b")
rep("(273, 272, 271, 270, 269, 268, 267, 266, 265, 264)",
    "(274, 273, 272, 271, 270, 269, 268, 267, 266, 265)", 2, "p3_transitive_list")
rep("W264..W273", "W265..W274", 1, "p3_transitive_window")
# ordinal faces: owner 266->267, bma 130 held, bmc 95->96 (W278 = 268th candidate, bm-c 97th own)
rep("len(owner_rows_live) == 266 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 95",
    "len(owner_rows_live) == 267 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 96", 1, "p3_ordinal_assert")
rep("266/130/95", "267/130/96", 1, "p3_ordinal_expect")
rep("owner_rows=266 / bma_rows=130 / bmc_rows=95",
    "owner_rows=267 / bma_rows=130 / bmc_rows=96", 1, "p3_leg0_face")
rep("rows 266 + candidate = 267th", "rows 267 + candidate = 268th", 2, "p3_owner266")
rep("; bm-c rows 95 +", "; bm-c rows 96 +", 1, "p3_comment_split")
rep("bm-c rows 95 + candidate = 96th owned", "bm-c rows 96 + candidate = 97th owned", 1, "p3_receipt_owned")
rep("# candidate = 96th EXACT", "# candidate = 97th EXACT", 1, "p3_comment_96th")
rep("engine_owner==bm-c rows 95 + candidate", "engine_owner==bm-c rows 96 + candidate", 1, "p3_pr_eo")
rep("bm-c rows {len(bmc_rows_live)} + candidate (96th own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (97th own wave", 1, "p3_gate05_print")
rep("bm-c's 96th own wave", "bm-c's 97th own wave", 2, "p3_96th_own")
rep("NINETY-SIXTH owned", "NINETY-SEVENTH owned", 3, "p3_96th_caps")
rep("TWO HUNDRED AND SEVENTY-SEVENTH", "TWO HUNDRED AND SEVENTY-EIGHTH", 3, "p3_wave_caps")
# 7 raw bmc_rows=95 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=95", "bmc_rows=96", 6, "p3_bmc_rows95")
rep('"probe_receipt_bmc_ordinal_face": 95', '"probe_receipt_bmc_ordinal_face": 96', 1, "p3_probe_face_key")
rep("bmc rows 95 + candidate 96th", "bmc rows 96 + candidate 97th", 1, "p3_hdr_ordinal")
# ordinal narrative: B-ordinal TWENTY-SEVENTH->TWENTY-EIGHTH FIRST, then A-ordinal TWENTY-SIXTH->TWENTY-SEVENTH
rep("TWENTY-SEVENTH", "TWENTY-EIGHTH", 7, "p3_27_caps")
rep("TWENTY-SIXTH", "TWENTY-SEVENTH", 15, "p3_26_caps")
rep("twenty-seventh", "twenty-eighth", 4, "p3_27_lc")
rep("twenty-sixth", "twenty-seventh", 3, "p3_26_lc")
rep("sixty-fifth", "sixty-sixth", 2, "p3_65rd")
# wave-number narrative faces
rep("wave 277 engine_owner=bm-c", "wave 278 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 277: "', '"wave 278: "', 1, "p3_cfg_waveface")
rep("wave 277 = first free number", "wave 278 = first free number", 1, "p3_mhdr_waveface")
# cycle/lineage window stamps (SEAT->r1114-continuation / SPLICE+FINALIZE+
# CYCLE-COMPLETE->r1114-continuation / PREREG->r1116; contexts measured)
rep("cycle COMPLETE bm-c r1113 closeout 09:1x", "cycle COMPLETE bm-c r1114-continuation closeout 10:4x", 1, "p3_hdr_complete")
rep("bm-c r1111 splice window", "bm-c r1114-continuation splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1111", "own-wave full cycle r1114-continuation", 1, "p3_repair_note")
rep("bm-c splice generation r1111 window", "bm-c splice generation r1114-continuation window", 1, "p3_parity_source")
rep("verified r1111", "verified r1114-continuation", 1, "p3_lineage_verified")
rep("# r1111 splice window", "# r1114-continuation splice window", 1, "p3_lineage_r")
rep("(bm-c r1111", "(bm-c r1114-continuation", 1, "p3_parity_comment")
rep("finalize one-pass bm-c r1111 closeout, ledger", "finalize one-pass bm-c r1114-continuation closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1111 closeout ledger", "finalize one-pass bm-c r1114-continuation closeout ledger", 1, "p3_finpass_hdr")
rep("(r1112 MSG-", "(r1114-continuation MSG-", 1, "p3_hdr_msgline")
rep("r1112 BEFORE this freeze", "r1114-continuation BEFORE this freeze", 1, "p3_receipt_seatnote")
rep("seat itself r1112; queue-head", "seat itself r1114-continuation; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1112, queue-head seat-first supply", "(r1114-continuation, queue-head seat-first supply", 1, "p3_pfcomment_seat")
# prereg window map (W277 prereg r1113 window -> W278 prereg r1116 window)
rep("bm-c r1113 window", "bm-c r1116 window", 4, "p3_prereg_window")
rep("# r1113 window", "# r1116 window", 1, "p3_hdr_prereg_window")
# not-a-re-pick face
rep("(R276: ", "(R277: ", 1, "p3_repick")
# r1076-family ROOT CURE +1 aging law (NOT the mechanical form)
rep("_set_wave(277)", "_set_wave(278)", 1, "p3_setwave_rootcure")

# ---------- phase 4: frozen-face anti-drift + residual sweeps ----------
assert t.count("w244_a") == 12 and t.count("w244_b") == 8, "aging tokens w244_a/b drift"
assert t.count("n3r1_used245") == 3, "frozen face n3r1_used245 drift"
assert t.count("w244_a holds wave-263 bands") == 4, "aging disclosure text drift"
assert t.count("m211") == 4, "frozen estate boundary marker m211 drift"
assert t.count("593901") == 1, "fmt doc example face drift"
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
assert t.count("m248") == 4, "frozen split marker m248 drift"
assert t.count("N1_BANDS[248] ==") == 1 and t.count("N1_BANDS\\[248\\]") == 1, "W248 face drift"
assert t.count("_set_wave(2)") == 1, "carried _set_wave(2) face drift"
assert t.count("zero skip-claim") == 1, "carried zero-skip-claim face drift"
assert t.count("banned gate ADMIT 0 (re-run at freeze window)") == 1, "carried banned-gate face drift"
assert t.count("20261019") == 17, "date face drift (17 carried, date-roll count 0 this generation)"
assert t.count("~23:5x") == 4, "carried CEO fill-order ~23:5x face drift"
assert t.count("bm-a") == 5, "residual bm-a faces (expect 5: bma_rows_live code + 4 ADMIT-convention law names)"
# residual sweep (r1091 law: self-produced faces EXCLUDED -- 626_701/626_900
# fresh prior-B-band faces x4/x6, "W278" inside the fresh relkeys, "_w277bmc_"
# lineage-template face, "if w < 277)" anti-gate needle, "range(248, 277)"
# fresh dropped-range assert, n1_w277/w277_ fresh upstream tokens,
# PERPETUAL_N1_W277_PREREG upstream refs; the bare-r1114 face lives ONLY
# inside r1114-continuation compounds and is NOT sweepable)
for gone in ("r1111", "r1112", "r1113", "09:0x", "09:1x", "09:3x",
             "c5f8b88f91", "354a645155",
             "45ee1de94c7d36fd", "e0bc4a0ddd",
             "MSG-20261019-080x", "_w276bmc_",
             "n1_w276", "w276_", "n1w277-",
             "626_700", "626_500", "624_701", "624_900",
             "626701", "628700", "626901", "627100",
             "1,031,535", "605,120", "1_031_535", "605_120",
             "W278p", "W277p", "W276p", "W275p", "W274p", "W273p",
             "W274_W275_W277_bands_respected",
             "rows 266 + candidate", "bmc_rows=95", "266/130/95",
             "NINETY-SIXTH owned", "TWO HUNDRED AND SEVENTY-SEVENTH",
             "TWENTY-SIXTH", "twenty-sixth", "sixty-fifth", "sixty-five legs",
             "wave 277 engine_owner=bm-c", '"wave 277: "', "wave 277 = first free number",
             '"wave": 276',
             "arith_a277", "arith_b277",
             "range(16, 277)", "range(17, 277)", "range(209, 278)",
             "range(248, 276)", "range(211, 276)", "if w < 276)",
             "277 - _lw", "_w == 276",
             "PERPETUAL-N1-W277", "20261018", "2026-10-18"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
  'MSG-20261019-102x-bmc-w278-seat': 7, "b187aa6214": 2, "_w278bmc_": 11, "_w277bmc_": 1,
  "20261019": 17, "9e53371814": 1,
  "99001d3d3f337942": 2, "df1aaba72a": 1,
  "628_901": 5, "629_100": 4, "628_900": 9, "628_700": 2,
  "626_901": 8, "627_100": 2, "626_701": 4, "626_900": 6,
  "628901": 1, "630900": 1, "629101": 2, "629300": 2,
  "1,033,735": 6, "607,320": 6, "1_033_735": 1, "607_320": 1,
  "n1_w278": 4, "n1_w277": 4, "n1w278-": 2,
  "n1_w278_results.json": 2, "n1_w277_results.json": 4,
  '278: {"batch"': 2, '277: {"batch"': 2, '276: {"batch"': 0,
  '278: {{"batch"': 1, '278: {"a"': 1, '277: {"a"': 3, '278: {{"a"': 2, '276: {{"a"': 0,
  "range(248, 278)": 2, "range(248, 277)": 1, "range(16, 278)": 2, "range(17, 278)": 3,
  "range(209, 279)": 2, "range(211, 277)": 1, "range(211, 248)": 1, "range(138, 207)": 1,
  "if w < 278)": 5, "if w < 277)": 1, "278 - _lw": 2,
  "m248": 4, "m211": 4, "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
  "WAVE_CONFIGS[278]": 2, "WAVE_CONFIGS[277]": 3, "N1_BANDS[277]": 5,
  "get(277)": 1, "_c277": 5,
  "arith_a278": 6, "arith_b278": 6,
  "(274, 273, 272, 271, 270, 269, 268, 267, 266, 265)": 2, "W265..W274": 1,
  "len(owner_rows_live) == 267": 1, "267/130/96": 1, "bmc_rows=96": 7,
  "rows 267 + candidate = 268th": 2, "bm-c rows 96 + candidate = 97th owned": 1,
  "NINETY-SEVENTH owned": 3, "TWO HUNDRED AND SEVENTY-EIGHTH": 3,
  "TWENTY-EIGHTH": 7, "TWENTY-SEVENTH": 15, "twenty-eighth": 4, "twenty-seventh": 3,
  "W275_W276_W277_bands_respected": 2, "W279p": 13, "W279": 26,
  "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
  "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
  "W278 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
  "2026-10-19 13:3x bm-c r1118 splice window": 1,
  "finalize one-pass bm-c r1114-continuation": 2,
  "authored 12:2x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
  "cycle COMPLETE bm-c r1114-continuation closeout 10:4x": 1,
  "verified r1114-continuation": 1, "(R277: ": 1, "_w == 277": 1,
  "wave 278 engine_owner=bm-c": 1, '"wave 278: "': 1,
  "wave 278 = first free number": 1, "sixty-sixth": 2, "sixty-six legs": 1,
  'N1_BANDS[") == 135,': 1, '!= 135': 1, 'N1_BANDS[") == 66': 1,
  'N1_BANDS[") == 37': 1, 'N1_BANDS[") == 29': 1,
  "W211..W276 legs (66)": 1, "W211..W277 legs 66": 1,
  "own W248..W276 legs (29)": 4, "own W248..W276": 5, "W248..W278 legs (30": 4,
  "block = 136 rows": 1, "136 parity rows": 1, "block parity = 136 rows": 1,
  "bm-c r1116 window": 4, "# r1116 window": 1,
  "bm-c splice generation r1114-continuation window": 1, "(bm-c r1114-continuation": 1,
  "_w277bmc_freeze_edits.py template": 1,
  "PERPETUAL_N1_W278_PREREG": 8, "PERPETUAL_N1_W277_PREREG": 2, "PERPETUAL-N1-W278": 7,
  "W278 materializer face": 4, "W277 materializer face": 1,
  "W276 finalize product": 0, "W277 finalize product": 4,
  "engine_owner==bm-c rows 96 + candidate": 1, "# candidate = 97th EXACT": 1, "; bm-c rows 96 +": 1,
  "bm-c rows {len(bmc_rows_live)} + candidate (97th own wave": 1,
  "bm-c's 97th own wave": 2, "owner_rows=267 / bma_rows=130 / bmc_rows=96": 1,
  '"probe_receipt_bmc_ordinal_face": 96': 1,
  "fourteen-wave": 8, "post-W277-REGISTERED": 8,
  "anchors W277 1,033,735 / K=607,320 at draft": 1,
  "dual-window parity": 1, "W279 walk": 1,
  "sixty-sixth consecutive": 2, '"wave": 277': 1,
  "registered wave below 263 composes": 2,
  "PRE-W278-splice": 1, "post-W277 registration": 2,
  "expect 267/130/96": 1,
  "_set_wave(278)": 1, "_set_wave(277)": 0, "_set_wave(276)": 0, "_set_wave(2)": 1,
  "derived by the bm-c": 2,
  "bm-c own-seat continuity": 2,
  "physical bytes": 6,
  "own-wave full cycle r1114-continuation": 1,
  "r1114-continuation BEFORE this freeze": 1, "seat itself r1114-continuation; queue-head": 1,
  "(r1114-continuation, queue-head seat-first supply": 1, "(r1114-continuation MSG-": 1,
  "bm-c r1114-continuation splice window": 2,
  "# r1114-continuation splice window": 1,
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
