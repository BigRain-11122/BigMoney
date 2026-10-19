# -*- coding: utf-8 -*-
# r1114 bm-c splice window: derive results/_w277bmc_freeze_edits.py from the
# committed W276 freeze-edits canon (results/_w276bmc_freeze_edits.py, bm-c
# r1111 splice window 354a645155, proven live-fire: W276 five-face splice +
# engine self-burn 12/12 + finalize one-pass ledger 1,031,535 / K=605,120
# EXACT, machine-verified by the r1111 closeout e781164e41)
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 21st-gen lineage, zero
# transcription: every needle count MEASURED on the canon blob by
# results/_r1114bmc_needle_preflight.py (receipt
# results/_r1114bmc_needle_preflight.json, canon sha256-16 ee852bc2721f3862,
# 62,326B, wt==HEAD==origin triple-verified; post-blanket phase-3 forms
# measured on the phase-1+2 simulated text; 2 preflight-table self-heals
# disclosed: 'the bm-c r1111 splice window'/'bm-c own seat executed at the
# bm-c r1111 splice window' table guesses REMOVED = faces absent from canon,
# my misread of the r1111 gate region, zero canon anomalies). r1077
# measured-counts law.
# DISCLOSED CANON EOL FACE (benign, carried): core.autocrlf=true re-smudge
# (r1093 pit entry) -- canon read raw with newline='' (CRLF form); multi-line
# needles use the physical CRLF bytes (r775 law).
# W277 FACTS (probe receipt results/_w277bmc_20261019_probe_receipt.json,
# committed with the seat @ c5f8b88f91 r1112, ADMIT): bands A 624_701..626_700
# (TWENTY-SIXTH consecutive A-hop, staircase-affects-A, hops=1; naive A
# 624_501..626_500 refused at the registered W276 B band 624_501..624_700) /
# B 626_701..626_900 (TWENTY-SEVENTH consecutive above-own-A, own-A
# reservation cascade, hops=1; naive B 624_701..624_900 inside the own-A
# window 624_701..626_700); seed_admit FREE x2 (base=624701 span=2000 /
# base=626701 span=200); ordinals owner 266 + candidate = 267th / bm-c rows
# 95 + candidate = 96th; W276 finalize anchors 1,031,535 / K=605,120 (chain
# +2,200/+2,200 EXACT); leg4 W278+ projection naive A 626_701..628_700 /
# naive B 626_901..627_100 (own-A reservation face).
# W277 PREREG: research/PERPETUAL_N1_W277_PREREG.md 23,593B sha256_16
# 45ee1de94c7d36fd (authored 09:0x bm-c r1113 window via E63 canon-clone
# builder _r1113bmc_build_w277_derive.py; CAS-surgical-pushed to origin
# e0bc4a0ddd -- the 11-file surgical first-try + local convergence 11/11
# landed same-window per the r1113 closeout 5b2b2950f1).
# AGING-TOKEN LAW (E63 anti-drift, carried): frozen faces w244_a/w244_b /
# n3r1_used245 / m211 / m248 / "w244_a holds wave-263 bands" /
# "registered wave below 263 composes" do NOT roll (measured 12/8/3/4/4/2
# in canon; carried verbatim, anti-drift asserted). Band order law:
# CONSUMERS before PRODUCERS (624_501/624_700 consumed BEFORE 622_301/622_500
# recreate them). Projections first (W278p -> W277p-order mirror: canon
# W277p rolls to W278p before plain W277 -> W278), then D-swaps (own W276 ->
# W277 first, then upstream W275 -> W276). Ordinal caps: B
# (TWENTY-SIXTH -> TWENTY-SEVENTH) before A (TWENTY-FIFTH -> TWENTY-SIXTH).
# lc blankets: own w276_ (10, after n1_w276_results.json x2 + builder x1
# carve-outs) before upstream w275_ (89, after n1_w275_results.json x4
# carve-outs).
# SETWAVE +1 AGING LAW (r1076-family root cure, carried): _set_wave(276) ->
# _set_wave(277); presence gates 277:1 / 276:0 / 275:0.
# DATE-ROLL FACE (count 0 this generation, DISCLOSED): canon receipts already
# dated 20261019 and the W277 seat/probe/prereg receipts are same-date -- no
# date-roll rep this generation (zero 20261018 faces in canon,
# preflight-measured); the "20261019" x17 gate carries verbatim.
# Window-stamp disambiguation (measured): SEAT faces -> r1112 (W277 seat
# c5f8b88f91); SPLICE/FINALIZE/CLOSEOUT faces -> r1111 (W276 splice
# 354a645155 + finalize one-pass 07:4x + closeout e781164e41);
# PREREG faces -> r1113 (W277 prereg e0bc4a0ddd); upstream cycle COMPLETE ->
# r1113 closeout 09:1x (5b2b2950f1); THIS splice window -> r1114.
import io, subprocess, sys

CANON = "results/_w276bmc_freeze_edits.py"
DST = "results/_w277bmc_freeze_edits.py"
LOG = "results/_r1114bmc_derive_editor_log.txt"
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
       f"(preflight-measured sha256-16 ee852bc2721f3862, 62,326B)",
       f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:110]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W277p", "W278p", 13, "p1_proj_prefix")
rep("W277", "W278", 13, "p1_proj_plain")
# bands (CONSUMERS FIRST: 624_501/624_700 consumed before 622_301/622_500
# recreate them -- band-order law; all 8 rep targets measured 5/4/9/2/8/2/4/6)
rep("624_501", "626_701", 5, "p1_band_Blo")
rep("624_700", "626_900", 4, "p1_band_Bhi")
rep("624_500", "626_700", 9, "p1_band_Ahi")
rep("624_300", "626_500", 2, "p1_band_naiveAhi")
rep("622_501", "624_701", 8, "p1_band_Alo_Bnaivelo")
rep("622_700", "624_900", 2, "p1_band_Bnaivehi")
rep("622_301", "624_501", 4, "p1_band_naiveAlo_priorBlo")
rep("622_500", "624_700", 6, "p1_band_priorBhi")
# int-form leg4 projections in the receipt downstream_seat note (probe-measured)
rep("624501", "626701", 1, "p1_int_projAlo")
rep("626500", "628700", 1, "p1_int_projAhi")
rep("624701", "626901", 2, "p1_int_projBlo")
rep("624900", "627100", 2, "p1_int_projBhi")
# ledger/K anchors: W275 finalize facts -> W276 finalize facts (1,031,535/605,120)
rep("1,029,335", "1,031,535", 6, "p1_ledger_prose")
rep("602,920", "605,120", 6, "p1_k_prose")
rep("1_029_335", "1_031_535", 1, "p1_ledger_code")
rep("602_920", "605_120", 1, "p1_k_code")
# builder filename FIRST (consumes its embedded w276_ before the lc blanket)
rep("(E63 canon-clone builder _r1110bmc_build_w276_derive.py)",
    "(E63 canon-clone builder _r1113bmc_build_w277_derive.py)", 1, "p1_builder_method")
# lowercase machine-file tokens (own first, then upstream; the w276_ blanket
# ALSO rolls the current-wave pickaxe vars w276_prereg_sha/w276_receipt_sha ->
# w277_* AFTER the n1_w276_results.json x2 + builder x1 carve-outs; the
# w275_ blanket rolls ALL upstream w275_* variables -> w276_* after the
# n1_w275_results.json x4 carve-out)
rep("n1_w276", "n1_w277", 4, "p1_n1w276_own")
rep("n1w276-", "n1w277-", 2, "p1_n1w276dash")
rep("w276_", "w277_", 10, "p1_lc_w276_")
rep("n1_w275", "n1_w276", 4, "p1_n1w275_upstream")
rep("w275_", "w276_", 89, "p1_lc_w275_")
# receipt/lineage/seat faces
rep("_w276bmc_", "_w277bmc_", 11, "p1_receiptpath")
rep("_w275bmc_freeze_edits.py template", "_w276bmc_freeze_edits.py template", 1, "p1_lineage_template")
rep("MSG-20261019-055x-bmc-w276-seat", "MSG-20261019-080x-bmc-w277-seat", 7, "p1_seat_msg")
rep('SEAT_ORIGIN = "21b51a102"', 'SEAT_ORIGIN = "c5f8b88f91"', 1, "p1_seat_origin_const")
rep("21b51a102 r1109", "c5f8b88f91 r1112", 1, "p1_seat_origin_hdr")
rep("018782314d", "354a645155", 1, "p1_lineage_sha")
# prereg delivery prose (r1113 CAS-surgical push + E63 builder method;
# CRLF-joined needle per the preflight verbatim extraction)
rep("(authored 06:5x, banned_direction_gate ADMIT rc0, frozen sha16 5352c7cf343fc5e5 + pushed-" + CRLF +
    "# first-try to origin 770a47fa1f, r1110 window).",
    "(authored 09:0x, banned_direction_gate ADMIT rc0, frozen sha16 45ee1de94c7d36fd + CAS-" + CRLF +
    "# surgical-pushed to origin e0bc4a0ddd, r1113 window).",
    1, "p1_prereg_delivery_hdr")
rep("(authored 06:5x, banned gate ADMIT rc0, frozen 5352c7cf343fc5e5 -> pushed first-try r1110 origin ",
    "(authored 09:0x, banned gate ADMIT rc0, frozen 45ee1de94c7d36fd -> CAS-surgical r1113 origin ",
    1, "p1_prereg_delivery_note")
# header window stamp
rep("2026-10-19 07:1x bm-c r1111 splice window", "2026-10-19 09:3x bm-c r1114 splice window", 1, "p1_hdr_stamp")
# receipt wave field (mechanical +1): 275->276
rep('"wave": 275', '"wave": 276', 1, "p1_receipt_wave")
# DATE ROLL: DROPPED this generation (20261019 == 20261019, count-0 face,
# preflight-measured zero 20261018 in canon; disclosed in header)

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W276", "W277", 96, "p2_own_wave")
rep("W275", "W276", 158, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
# relkey = POST-BLANKET form (the upstream blanket rolled the W275 inside
# "W273_W274_W275_bands_respected" -> "W273_W274_W276"; this rep rolls the
# first two positions +1 to the W277 probe receipt's relation keys)
rep("W273_W274_W276_bands_respected", "W274_W275_W276_bands_respected", 2, "p3_relkey")
# legs_sec prose + message (W277 extraction: legs W211..W275 = 65)
rep("W211..W274 legs (64)", "W211..W275 legs (65)", 1, "p3_legs_prose")
rep("W211..W274 sixty-four legs", "W211..W275 sixty-five legs", 1, "p3_legs_msg")
rep("range(211, 275)", "range(211, 276)", 1, "p3_range_legs")
# dropped faces (W277 extraction drops the W276 block's own W248..W275 = 28 legs)
rep("own W248..W274 legs (27)", "own W248..W275 legs (28)", 4, "p3_dropped_narr")
rep("own W248..W274" + CRLF + "# legs (27 rows) do NOT enter the estate path",
    "own W248..W275" + CRLF + "# legs (28 rows) do NOT enter the estate path", 1, "p3_dropped_split_hdr")
rep("W248..W274 twenty-seven legs", "W248..W275 twenty-eight legs", 1, "p3_dropped_fstring")
rep('N1_BANDS[") == 27', 'N1_BANDS[") == 28', 1, "p3_dropped_count")
# fullspan error-string (POST-BLANKET wave face rolled by the upstream
# blanket: "W211..W275 legs 64" -> "W211..W276 legs 64"; count 64->65)
rep("W211..W276 legs 64", "W211..W276 legs 65", 1, "p3_fullspan_fstring")
# fresh legs (W277 block appends fresh W248..W276 = 29 legs; POST-OWN-BLANKET
# form -- the own blanket rolled the hi face to the new range end 277;
# count-only roll 28->29, hi rides the blanket = range(248, 277) END EXACT)
rep("W248..W277 legs (28", "W248..W277 legs (29", 4, "p3_fresh_narr")
# block/parity counts: W277 block = 69 estate + 37 kept + 29 fresh = 135
rep("block = 134 rows", "block = 135 rows", 1, "p3_block131")
rep("134 parity rows", "135 parity rows", 1, "p3_parity131")
rep("block parity = 134 rows", "block parity = 135 rows", 1, "p3_blockparity131")
rep('N1_BANDS[") == 133,', 'N1_BANDS[") == 134,', 1, "p3_count130")
rep('!= 133', '!= 134', 1, "p3_fstring130")
rep('N1_BANDS[") == 64', 'N1_BANDS[") == 65', 1, "p3_count61")
rep('"fresh_legs_row_asserts": 28', '"fresh_legs_row_asserts": 29', 1, "p3_receipt_fresh")
rep('+ 28,', '+ 29,', 1, "p3_receipt_total")
# ranges (fresh FIRST then dropped-producer, then the cumulative/registry faces)
rep("range(248, 276)", "range(248, 277)", 2, "p3_range_fresh")
rep("range(248, 275)", "range(248, 276)", 1, "p3_range_dropped")
rep("range(16, 276)", "range(16, 277)", 2, "p3_range16")
rep("range(17, 276)", "range(17, 277)", 3, "p3_range17")
rep("range(209, 277)", "range(209, 278)", 2, "p3_range209")
# wave-number gates (own 276->277 FIRST, then anti-gate 275->276)
rep("if w < 276)", "if w < 277)", 5, "p3_wlt276")
rep("if w < 275)", "if w < 276)", 1, "p3_wlt275_antigate")
rep("276 - _lw", "277 - _lw", 2, "p3_legcount")
rep("_w == 275", "_w == 276", 1, "p3_freshmsg_cond")
# cfg/row faces: own 276->277 FIRST, then upstream 275->276
rep("WAVE_CONFIGS[276]", "WAVE_CONFIGS[277]", 2, "p3_wavecfg276_own")
rep("WAVE_CONFIGS[275]", "WAVE_CONFIGS[276]", 3, "p3_wavecfg275")
rep("N1_BANDS[275]", "N1_BANDS[276]", 5, "p3_n1bands275")
rep("get(275)", "get(276)", 1, "p3_get275")
rep("_c275", "_c276", 5, "p3_c275var")
rep('276: {"batch"', '277: {"batch"', 2, "p3_cfg276")
rep('276: {{"batch"', '277: {{"batch"', 1, "p3_cfg276_fstring")
rep('276: {"a"', '277: {"a"', 1, "p3_row276")
rep('276: {{"a"', '277: {{"a"', 2, "p3_row276_fstring")
rep('275: {"batch"', '276: {"batch"', 2, "p3_cfg275")
rep('275: {"a"', '276: {"a"', 3, "p3_row275")
rep("arith_a276", "arith_a277", 6, "p3_arith_a")
rep("arith_b276", "arith_b277", 6, "p3_arith_b")
rep("(272, 271, 270, 269, 268, 267, 266, 265, 264, 263)",
    "(273, 272, 271, 270, 269, 268, 267, 266, 265, 264)", 2, "p3_transitive_list")
rep("W263..W272", "W264..W273", 1, "p3_transitive_window")
# ordinal faces: owner 265->266, bma 130 held, bmc 94->95 (W277 = 267th candidate, bm-c 96th own)
rep("len(owner_rows_live) == 265 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 94",
    "len(owner_rows_live) == 266 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 95", 1, "p3_ordinal_assert")
rep("265/130/94", "266/130/95", 1, "p3_ordinal_expect")
rep("owner_rows=265 / bma_rows=130 / bmc_rows=94",
    "owner_rows=266 / bma_rows=130 / bmc_rows=95", 1, "p3_leg0_face")
rep("rows 265 + candidate = 266th", "rows 266 + candidate = 267th", 2, "p3_owner265")
rep("; bm-c rows 94 +", "; bm-c rows 95 +", 1, "p3_comment_split")
rep("bm-c rows 94 + candidate = 95th owned", "bm-c rows 95 + candidate = 96th owned", 1, "p3_receipt_owned")
rep("# candidate = 95th EXACT", "# candidate = 96th EXACT", 1, "p3_comment_95th")
rep("engine_owner==bm-c rows 94 + candidate", "engine_owner==bm-c rows 95 + candidate", 1, "p3_pr_eo")
rep("bm-c rows {len(bmc_rows_live)} + candidate (95th own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (96th own wave", 1, "p3_gate05_print")
rep("bm-c's 95th own wave", "bm-c's 96th own wave", 2, "p3_95th_own")
rep("NINETY-FIFTH owned", "NINETY-SIXTH owned", 3, "p3_95th_caps")
rep("TWO HUNDRED AND SEVENTY-SIXTH", "TWO HUNDRED AND SEVENTY-SEVENTH", 3, "p3_wave_caps")
# 7 raw bmc_rows=94 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=94", "bmc_rows=95", 6, "p3_bmc_rows94")
rep('"probe_receipt_bmc_ordinal_face": 94', '"probe_receipt_bmc_ordinal_face": 95', 1, "p3_probe_face_key")
rep("bmc rows 94 + candidate 95th", "bmc rows 95 + candidate 96th", 1, "p3_hdr_ordinal")
# ordinal narrative: B-ordinal TWENTY-SIXTH->TWENTY-SEVENTH FIRST, then A-ordinal TWENTY-FIFTH->TWENTY-SIXTH
rep("TWENTY-SIXTH", "TWENTY-SEVENTH", 7, "p3_26_caps")
rep("TWENTY-FIFTH", "TWENTY-SIXTH", 15, "p3_25_caps")
rep("twenty-sixth", "twenty-seventh", 4, "p3_26_lc")
rep("twenty-fifth", "twenty-sixth", 3, "p3_25_lc")
rep("sixty-fourth", "sixty-fifth", 2, "p3_64rd")
# wave-number narrative faces
rep("wave 276 engine_owner=bm-c", "wave 277 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 276: "', '"wave 277: "', 1, "p3_cfg_waveface")
rep("wave 276 = first free number", "wave 277 = first free number", 1, "p3_mhdr_waveface")
# cycle/lineage window stamps (SEAT->r1112 / SPLICE+FINALIZE+CLOSEOUT->r1111 /
# PREREG->r1113 / upstream cycle COMPLETE->r1113 closeout 09:1x; contexts measured)
rep("cycle COMPLETE bm-c r1108 closeout 05:3x", "cycle COMPLETE bm-c r1113 closeout 09:1x", 1, "p3_hdr_complete")
rep("bm-c r1108 splice window", "bm-c r1111 splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1108", "own-wave full cycle r1111", 1, "p3_repair_note")
rep("bm-c splice generation r1108 window", "bm-c splice generation r1111 window", 1, "p3_parity_source")
rep("verified r1108", "verified r1111", 1, "p3_lineage_verified")
rep("# r1108 splice window", "# r1111 splice window", 1, "p3_lineage_r")
rep("(bm-c r1108", "(bm-c r1111", 1, "p3_parity_comment")
rep("finalize one-pass bm-c r1108 closeout, ledger", "finalize one-pass bm-c r1111 closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1108 closeout ledger", "finalize one-pass bm-c r1111 closeout ledger", 1, "p3_finpass_hdr")
rep("(r1109 MSG-", "(r1112 MSG-", 1, "p3_hdr_msgline")
rep("r1109 BEFORE this freeze", "r1112 BEFORE this freeze", 1, "p3_receipt_seatnote")
rep("seat itself r1109; queue-head", "seat itself r1112; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1109, queue-head seat-first supply", "(r1112, queue-head seat-first supply", 1, "p3_pfcomment_seat")
# prereg window map (W276 prereg r1110 window -> W277 prereg r1113 window)
rep("bm-c r1110 window", "bm-c r1113 window", 4, "p3_prereg_window")
rep("# r1110 window", "# r1113 window", 1, "p3_hdr_prereg_window")
# not-a-re-pick face
rep("(R275: ", "(R276: ", 1, "p3_repick")
# r1076-family ROOT CURE +1 aging law (NOT the mechanical form)
rep("_set_wave(276)", "_set_wave(277)", 1, "p3_setwave_rootcure")

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
# residual sweep (r1091 law: self-produced faces EXCLUDED -- 624_501/624_700
# fresh prior-B-band faces x4/x6, "W277" inside the fresh relkeys, "_w276bmc_"
# lineage-template face, "if w < 276)" anti-gate needle, "range(248, 276)"
# fresh dropped-range assert, n1_w276/w276_ fresh upstream tokens,
# PERPETUAL_N1_W276_PREREG upstream refs)
for gone in ("r1108", "r1109", "r1110", "05:3x", "06:5x", "07:1x",
             "21b51a102", "018782314d",
             "5352c7cf343fc5e5", "770a47fa1f",
             "MSG-20261019-055x", "_w275bmc_",
             "n1_w275", "w275_", "n1w276-",
             "624_500", "624_300", "622_501", "622_700",
             "624501", "626500", "624701", "624900",
             "1,029,335", "602,920", "1_029_335", "602_920",
             "W277p", "W276p", "W275p", "W274p", "W273p",
             "W273_W274_W276_bands_respected",
             "rows 265 + candidate", "bmc_rows=94", "265/130/94",
             "NINETY-FIFTH owned", "TWO HUNDRED AND SEVENTY-SIXTH",
             "TWENTY-FIFTH", "twenty-fifth", "sixty-fourth", "sixty-four legs",
             "wave 276 engine_owner=bm-c", '"wave 276: "', "wave 276 = first free number",
             '"wave": 275',
             "arith_a276", "arith_b276",
             "range(16, 276)", "range(17, 276)", "range(209, 277)",
             "range(248, 275)", "range(211, 275)", "if w < 275)",
             "276 - _lw", "_w == 275",
             "PERPETUAL-N1-W276", "20261018", "2026-10-18"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
  'MSG-20261019-080x-bmc-w277-seat': 7, "c5f8b88f91": 2, "_w277bmc_": 11, "_w276bmc_": 1,
  "20261019": 17, "354a645155": 1,
  "45ee1de94c7d36fd": 2, "e0bc4a0ddd": 1,
  "626_701": 5, "626_900": 4, "626_700": 9, "626_500": 2,
  "624_701": 8, "624_900": 2, "624_501": 4, "624_700": 6,
  "626701": 1, "628700": 1, "626901": 2, "627100": 2,
  "1,031,535": 6, "605,120": 6, "1_031_535": 1, "605_120": 1,
  "n1_w277": 4, "n1_w276": 4, "n1w277-": 2,
  "n1_w277_results.json": 2, "n1_w276_results.json": 4,
  '277: {"batch"': 2, '276: {"batch"': 2, '275: {"batch"': 0,
  '277: {{"batch"': 1, '277: {"a"': 1, '276: {"a"': 3, '277: {{"a"': 2, '276: {{"a"': 0,
  "range(248, 277)": 2, "range(248, 276)": 1, "range(16, 277)": 2, "range(17, 277)": 3,
  "range(209, 278)": 2, "range(211, 276)": 1, "range(211, 248)": 1, "range(138, 207)": 1,
  "if w < 277)": 5, "if w < 276)": 1, "277 - _lw": 2,
  "m248": 4, "m211": 4, "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
  "WAVE_CONFIGS[277]": 2, "WAVE_CONFIGS[276]": 3, "N1_BANDS[276]": 5,
  "get(276)": 1, "_c276": 5,
  "arith_a277": 6, "arith_b277": 6,
  "(273, 272, 271, 270, 269, 268, 267, 266, 265, 264)": 2, "W264..W273": 1,
  "len(owner_rows_live) == 266": 1, "266/130/95": 1, "bmc_rows=95": 7,
  "rows 266 + candidate = 267th": 2, "bm-c rows 95 + candidate = 96th owned": 1,
  "NINETY-SIXTH owned": 3, "TWO HUNDRED AND SEVENTY-SEVENTH": 3,
  "TWENTY-SEVENTH": 7, "TWENTY-SIXTH": 15, "twenty-seventh": 4, "twenty-sixth": 3,
  "W274_W275_W276_bands_respected": 2, "W278p": 13, "W278": 26,
  "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
  "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
  "W277 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
  "2026-10-19 09:3x bm-c r1114 splice window": 1,
  "finalize one-pass bm-c r1111": 2,
  "authored 09:0x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
  "cycle COMPLETE bm-c r1113 closeout 09:1x": 1,
  "verified r1111": 1, "(R276: ": 1, "_w == 276": 1,
  "wave 277 engine_owner=bm-c": 1, '"wave 277: "': 1,
  "wave 277 = first free number": 1, "sixty-fifth": 2, "sixty-five legs": 1,
  'N1_BANDS[") == 134,': 1, '!= 134': 1, 'N1_BANDS[") == 65': 1,
  'N1_BANDS[") == 37': 1, 'N1_BANDS[") == 28': 1,
  "W211..W275 legs (65)": 1, "W211..W276 legs 65": 1,
  "own W248..W275 legs (28)": 4, "own W248..W275": 5, "W248..W277 legs (29": 4,
  "block = 135 rows": 1, "135 parity rows": 1, "block parity = 135 rows": 1,
  "bm-c r1113 window": 4, "# r1113 window": 1,
  "bm-c splice generation r1111 window": 1, "(bm-c r1111": 1,
  "_w276bmc_freeze_edits.py template": 1,
  "PERPETUAL_N1_W277_PREREG": 8, "PERPETUAL_N1_W276_PREREG": 2, "PERPETUAL-N1-W277": 7,
  "W277 materializer face": 4, "W276 materializer face": 1,
  "W275 finalize product": 0, "W276 finalize product": 4,
  "engine_owner==bm-c rows 95 + candidate": 1, "# candidate = 96th EXACT": 1, "; bm-c rows 95 +": 1,
  "bm-c rows {len(bmc_rows_live)} + candidate (96th own wave": 1,
  "bm-c's 96th own wave": 2, "owner_rows=266 / bma_rows=130 / bmc_rows=95": 1,
  '"probe_receipt_bmc_ordinal_face": 95': 1,
  "fourteen-wave": 8, "post-W276-REGISTERED": 8,
  "anchors W276 1,031,535 / K=605,120 at draft": 1,
  "dual-window parity": 1, "W278 walk": 1,
  "sixty-fifth consecutive": 2, '"wave": 276': 1,
  "registered wave below 263 composes": 2,
  "PRE-W277-splice": 1, "post-W276 registration": 2,
  "expect 266/130/95": 1,
  "_set_wave(277)": 1, "_set_wave(276)": 0, "_set_wave(275)": 0, "_set_wave(2)": 1,
  "derived by the bm-c": 2,
  "bm-c own-seat continuity": 2,
  "physical bytes": 6,
  "own-wave full cycle r1111": 1,
  "r1112 BEFORE this freeze": 1, "seat itself r1112; queue-head": 1,
  "(r1112, queue-head seat-first supply": 1, "(r1112 MSG-": 1,
  "bm-c r1111 splice window": 2,
  "# r1111 splice window": 1,
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
