# -*- coding: utf-8 -*-
# r1102 bm-c splice window: derive results/_w273bmc_freeze_edits.py from the
# committed W272 freeze-edits canon (results/_w272bmc_freeze_edits.py, bm-c
# r1100 splice window c99ee20a4, proven live-fire: W272 five-face splice +
# engine self-burn 12/12 + finalize one-pass ledger 1,022,735 / K=596,320,
# W273 seat published @ origin 39e1bb32f1 r1101, machine-verified)
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 17th-gen lineage, zero
# transcription: every needle count MEASURED on the canon blob by
# results/_r1102bmc_needle_preflight.py (receipt
# results/_r1102bmc_needle_preflight.json, canon sha256_16 3deda21aa3e96ed9,
# 62,222B, wt==HEAD==origin triple-verified) + probe2 escape-form/int-form
# face measurements. r1077 measured-counts law.
# DISCLOSED CANON EOL FACE (benign, carried): core.autocrlf=true re-smudge
# (r1093 pit entry) -- canon read raw with newline='' (CRLF form); the
# multi-line needles use the physical CRLF bytes (r775 physical-fragment law).
# W273 FACTS (probe receipt results/_w273bmc_20261018_probe_receipt.json,
# committed with the seat @ 39e1bb32f1 r1101, sha256_16 283807958c1bf019):
# bands A 615_901..617_900 (TWENTY-SECOND consecutive A-hop,
# staircase-affects-A, hops=1; naive A 615_701..617_700 refused at the
# registered W272 B band 615_701..615_900) / B 617_901..618_100
# (TWENTY-THIRD consecutive above-own-A, own-A reservation cascade, hops=1;
# naive B 615_901..616_100 inside the own-A window 615_901..617_900);
# seed_admit FREE x2 (base=615901 span=2000 / base=617901 span=200);
# ordinals owner 262 + candidate = 263rd / bm-c rows 91 + candidate = 92nd;
# W272 finalize anchors 1,022,735 / K=596,320 (chain +2,200/+2,200 EXACT).
# W273 PREREG: research/PERPETUAL_N1_W273_PREREG.md 23,449B sha256_16
# 2f289446a93fa102 (authored 22:4x bm-c r1102 window via E63 canon-clone
# builder _r1102bmc_build_w273_derive.py; frozen b6bbb69e92 local ->
# SURGERY-DELIVERED to origin 839441a547 + receipts eeb3bf07ad, r1102).
# AGING-TOKEN LAW (E63 anti-drift, carried): frozen faces w244_a/w244_b /
# n3r1_used245 / m211 / m248 / "w244_a holds wave-263 bands" /
# "registered wave below 263 composes" do NOT roll (measured 12/8/3/4/4/2/2
# in canon; carried verbatim, anti-drift asserted). Band order law:
# CONSUMERS before PRODUCERS (615_701/615_900 consumed BEFORE 613_501/613_700
# recreate them, else double-transform). Projections first (W273p -> W274p
# before plain W273 -> W274), then D-swaps (own W272 -> W273 first, then
# upstream W271 -> W272). Ordinal caps: B (TWENTY-SECOND -> TWENTY-THIRD)
# before A (TWENTY-FIRST -> TWENTY-SECOND).
# SETWAVE +1 AGING LAW (r1076-family root cure, carried): _set_wave(272) ->
# _set_wave(273); presence gates 273:1 / 272:0 / 271:0 / 270:0.
# r1091 W268 gone-list law honored: self-produced faces EXCLUDED from the
# residual sweep (615_701/615_900 fresh prior-wave-band faces; "W270" inside
# the fresh relkeys W270_W271_W272_bands_respected; "_w272bmc_" lineage-
# template face count 1; "if w < 272)" anti-gate needle; "range(248, 272)"
# fresh dropped-range assert; n1_w272/w272_ fresh upstream tokens).
# AUTHORING HEALS this window (9 sites, all stale prose faces of the
# bm-c-own-seat era disclosed honest, zero functional impact):
#  (1) cfg PRE "engine_owner=bm-a (bm-c OWN-SEAT face -- bm-a's NINETY-FIRST
#      owned claim" -> bm-c/bm-c's;
#  (2) materializer hdr comment "bm-a's NINETY-FIRST owned per machine-
#      derive (engine_owner==bm-a" -> bm-c/bm-c;
#  (3) print line escaped "bm-a\'s NINETY-FIRST owned claim per " -> bm-c\'s;
#  (4) PRE "-- bm-a own-seat continuity" -> "-- bm-c own-seat";
#  (5) prereg-bundle note "bma rows 129 + candidate 130th" (stale draft-time
#      ordinal face) -> "bmc rows 91 + candidate 92nd" (W273 prereg's own
#      freeze-time live derive per its sec.0);
#  (6) header split "(18 rows)" aging-face count heal -> "(24 rows)"
#      (the W272 block's own W248..W271 legs = 24);
#  (7) "machine-SUB from the frozen W271 template" -> "E63 canon-clone
#      builder _r1102bmc_build_w273_derive.py" (W273 prereg derive method);
#  (8) header "(authored 19:2x, ... committed+pushed same window c049a57623)"
#      -> surgery-delivery prose (b6bbb69e92 + 839441a547 + eeb3bf07ad);
#  (9) receipt note "(authored 19:2x, ... committed+pushed r1099 commit"
#      -> W273 frozen+surgery-delivered prose.
# Window-stamp disambiguation (measured): SEAT faces -> r1101 (W273 seat
# 39e1bb32f1); SPLICE/FINALIZE faces -> r1100 (W272 splice c99ee20a4,
# finalize 20:4x); PREREG faces -> r1102 (W273 prereg b6bbb69e92/839441a547).
import io, subprocess, sys

CANON = "results/_w272bmc_freeze_edits.py"
DST = "results/_w273bmc_freeze_edits.py"
LOG = "results/_r1102bmc_derive_editor_log.txt"
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
       f"(preflight-measured sha256_16 3deda21aa3e96ed9, 62,222B)",
       f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:110]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W273p", "W274p", 13, "p1_proj_prefix")
rep("W273", "W274", 13, "p1_proj_plain")
# bands (CONSUMERS FIRST: 615_701/615_900 consumed before 613_501/613_700
# recreate them -- band-order law; all 8 rep targets measured 5/4/9/2/8/2/4/6)
rep("615_701", "617_901", 5, "p1_band_Blo")
rep("615_900", "618_100", 4, "p1_band_Bhi")
rep("615_700", "617_900", 9, "p1_band_Ahi")
rep("615_500", "617_700", 2, "p1_band_naiveAhi")
rep("613_701", "615_901", 8, "p1_band_Alo_Bnaivelo")
rep("613_900", "616_100", 2, "p1_band_Bnaivehi")
rep("613_501", "615_701", 4, "p1_band_naiveAlo_priorBlo")
rep("613_700", "615_900", 6, "p1_band_priorBhi")
# int-form leg4 projections in the receipt downstream_seat note (probe-measured)
rep("615701", "617901", 1, "p1_int_projAlo")
rep("617700", "619900", 1, "p1_int_projAhi")
rep("615901", "618101", 2, "p1_int_projBlo")
rep("616100", "618300", 2, "p1_int_projBhi")
# ledger/K anchors: W271 finalize facts -> W272 finalize facts (1,022,735/596,320)
rep("1,020,535", "1,022,735", 6, "p1_ledger_prose")
rep("594,120", "596,320", 6, "p1_k_prose")
rep("1_020_535", "1_022_735", 1, "p1_ledger_code")
rep("594_120", "596_320", 1, "p1_k_code")
# lowercase machine-file tokens (own first, then upstream; the w272_ blanket
# ALSO rolls the current-wave pickaxe vars w272_prereg_sha/w272_receipt_sha ->
# w273_*, and the w271_ blanket rolls ALL upstream w271_* variables -> w272_*)
rep("n1_w272", "n1_w273", 4, "p1_n1w272_own")
rep("n1w272-", "n1w273-", 2, "p1_n1w272dash")
rep("w272_", "w273_", 10, "p1_lc_w272_")   # 12 raw minus 2 inside n1_w272_results.json (consumed above)
rep("n1_w271", "n1_w272", 4, "p1_n1w271_upstream")
rep("w271_", "w272_", 89, "p1_lc_w271_")   # 93 raw minus 4 inside n1_w271_results.json (consumed above)
# receipt/lineage/seat faces
rep("_w272bmc_", "_w273bmc_", 11, "p1_receiptpath")
rep("_w271bmc_freeze_edits.py template", "_w272bmc_freeze_edits.py template", 1, "p1_lineage_template")
rep("MSG-20261018-191x-bmc-w272-seat", "MSG-20261018-211x-bmc-w273-seat", 7, "p1_seat_msg")
rep('SEAT_ORIGIN = "f608ff1cee"', 'SEAT_ORIGIN = "39e1bb32f1"', 1, "p1_seat_origin_const")
rep("f608ff1cee r1098", "39e1bb32f1 r1101", 1, "p1_seat_origin_hdr")
rep("7dd091eef1", "c99ee20a4", 1, "p1_lineage_sha")
# prereg delivery prose (heals 8+9+7: surgery-delivery + E63 builder method)
rep("(authored 19:2x, banned_direction_gate ADMIT rc0, committed+pushed same" + CRLF +
    "# window c049a57623).",
    "(authored 22:4x, banned_direction_gate ADMIT rc0, frozen b6bbb69e92 + surgery-" + CRLF +
    "# delivered to origin 839441a547 + receipts eeb3bf07ad, r1102 window).",
    1, "p1_prereg_delivery_hdr")
rep("(machine-SUB from the frozen W271 template)",
    "(E63 canon-clone builder _r1102bmc_build_w273_derive.py)", 1, "p1_prereg_method_hdr")
rep("machine-SUB derive landed pre-freeze",
    "E63 canon-clone builder derive landed pre-freeze", 2, "p1_prereg_method")
rep("(authored 19:2x, banned gate ADMIT rc0, committed+pushed r1099 commit ",
    "(authored 22:4x, banned gate ADMIT rc0, frozen b6bbb69e92 -> surgery-delivered r1102 origin ",
    1, "p1_prereg_delivery_note")
# header window stamp
rep("2026-10-18 20:2x bm-c r1100 freeze window", "2026-10-18 23:5x bm-c r1102 splice window", 1, "p1_hdr_stamp")
# receipt wave field (mechanical +1): 271->272
rep('"wave": 271', '"wave": 272', 1, "p1_receipt_wave")
# stale bm-a authoring heals (1-5, disclosed in the header)
rep("engine_owner=bm-a (bm-c OWN-SEAT face -- bm-a's NINETY-FIRST owned claim",
    "engine_owner=bm-c (bm-c OWN-SEAT face -- bm-c's NINETY-FIRST owned claim", 1, "p1_heal_cfg_owner")
rep("bm-a's NINETY-FIRST owned per machine-derive (engine_owner==bm-a",
    "bm-c's NINETY-FIRST owned per machine-derive (engine_owner==bm-c", 1, "p1_heal_hdr_owner")
rep("bm-a\\'s NINETY-FIRST owned claim per ", "bm-c\\'s NINETY-FIRST owned claim per ", 1, "p1_heal_print_owner")
rep("bm-a own-seat", "bm-c own-seat", 1, "p1_heal_pre_continuity")
rep("bma rows 129 + candidate 130th", "bmc rows 91 + candidate 92nd", 1, "p1_heal_draft_ordinal")

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W272", "W273", 96, "p2_own_wave")
# 159 raw W271 minus 1 consumed by p1_prereg_method_hdr (its needle carried
# "frozen W271 template"); the heal's replacement has no W-face
rep("W271", "W272", 158, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
# relkey = POST-BLANKET form (the upstream blanket rolled the W271 inside
# "W269_W270_W271_bands_respected" -> "W269_W270_W272"; this rep rolls the
# first two positions +1 to the W273 probe receipt's relation keys)
rep("W269_W270_W272_bands_respected", "W270_W271_W272_bands_respected", 2, "p3_relkey")
# legs_sec prose + message (W273 extraction: legs W211..W271 = 61)
rep("W211..W270 legs (60)", "W211..W271 legs (61)", 1, "p3_legs_prose")
rep("W211..W270 sixty legs", "W211..W271 sixty-one legs", 1, "p3_legs_msg")
rep("range(211, 271)", "range(211, 272)", 1, "p3_range_legs")
# dropped faces (W273 extraction drops the W272 block's own W248..W271 = 24 legs)
rep("own W248..W270 legs (23)", "own W248..W271 legs (24)", 4, "p3_dropped_narr")
rep("own W248..W270" + CRLF + "# legs (18 rows) do NOT enter the estate path",
    "own W248..W271" + CRLF + "# legs (24 rows) do NOT enter the estate path", 1, "p3_dropped_split_hdr")
rep("W248..W270 twenty-three legs", "W248..W271 twenty-four legs", 1, "p3_dropped_fstring")
rep('N1_BANDS[") == 23', 'N1_BANDS[") == 24', 1, "p3_dropped_count")
# fullspan error-string (POST-BLANKET wave face rolled by the upstream
# blanket: "W211..W271 legs 60" -> "W211..W272 legs 60"; count 60->61)
rep("W211..W272 legs 60", "W211..W272 legs 61", 1, "p3_fullspan_fstring")
# fresh legs (W273 block appends fresh W248..W272 = 25 legs; POST-OWN-BLANKET
# form -- the own blanket rolled the hi face to the new range end 273;
# count-only roll 24->25, hi rides the blanket = range(248, 273) END EXACT)
rep("W248..W273 legs (24", "W248..W273 legs (25", 4, "p3_fresh_narr")
# block/parity counts: W273 block = 69 estate + 37 kept + 25 fresh = 131
rep("block = 130 rows", "block = 131 rows", 1, "p3_block130")
rep("130 parity rows", "131 parity rows", 1, "p3_parity130")
rep("block parity = 130 rows", "block parity = 131 rows", 1, "p3_blockparity130")
rep('N1_BANDS[") == 129,', 'N1_BANDS[") == 130,', 1, "p3_count129")
rep('!= 129', '!= 130', 1, "p3_fstring129")
rep('N1_BANDS[") == 60', 'N1_BANDS[") == 61', 1, "p3_count60")
rep('"fresh_legs_row_asserts": 24', '"fresh_legs_row_asserts": 25', 1, "p3_receipt_fresh")
rep('+ 24,', '+ 25,', 1, "p3_receipt_total")
# ranges (fresh FIRST then dropped-producer, then the cumulative/registry faces)
rep("range(248, 272)", "range(248, 273)", 2, "p3_range_fresh")
rep("range(248, 271)", "range(248, 272)", 1, "p3_range_dropped")
rep("range(16, 272)", "range(16, 273)", 2, "p3_range16")
rep("range(17, 272)", "range(17, 273)", 3, "p3_range17")
rep("range(209, 273)", "range(209, 274)", 2, "p3_range209")
# wave-number gates (own 272->273 FIRST, then anti-gate 271->272)
rep("if w < 272)", "if w < 273)", 5, "p3_wlt272")
rep("if w < 271)", "if w < 272)", 1, "p3_wlt271_antigate")
rep("272 - _lw", "273 - _lw", 2, "p3_legcount")
rep("_w == 271", "_w == 272", 1, "p3_freshmsg_cond")
# cfg/row faces: own 272->273 FIRST, then upstream 271->272
rep("WAVE_CONFIGS[272]", "WAVE_CONFIGS[273]", 2, "p3_wavecfg272_own")
rep("WAVE_CONFIGS[271]", "WAVE_CONFIGS[272]", 3, "p3_wavecfg271")
rep("N1_BANDS[271]", "N1_BANDS[272]", 5, "p3_n1bands271")
rep("get(271)", "get(272)", 1, "p3_get271")
rep("_c271", "_c272", 5, "p3_c271var")
rep('272: {"batch"', '273: {"batch"', 2, "p3_cfg272")
rep('272: {{"batch"', '273: {{"batch"', 1, "p3_cfg272_fstring")
rep('272: {"a"', '273: {"a"', 1, "p3_row272")
rep('272: {{"a"', '273: {{"a"', 2, "p3_row272_fstring")
rep('271: {"batch"', '272: {"batch"', 2, "p3_cfg271")
rep('271: {"a"', '272: {"a"', 3, "p3_row271")
rep("arith_a272", "arith_a273", 6, "p3_arith_a")
rep("arith_b272", "arith_b273", 6, "p3_arith_b")
rep("(268, 267, 266, 265, 264, 263, 262, 261, 260, 259)",
    "(269, 268, 267, 266, 265, 264, 263, 262, 261, 260)", 2, "p3_transitive_list")
rep("W259..W268", "W260..W269", 1, "p3_transitive_window")
# ordinal faces: owner 261->262, bma 130 held, bmc 90->91 (W273 = 263rd candidate, bm-c 92nd own)
rep("len(owner_rows_live) == 261 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 90",
    "len(owner_rows_live) == 262 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 91", 1, "p3_ordinal_assert")
rep("261/130/90", "262/130/91", 1, "p3_ordinal_expect")
rep("owner_rows=261 / bma_rows=130 / bmc_rows=90",
    "owner_rows=262 / bma_rows=130 / bmc_rows=91", 1, "p3_leg0_face")
rep("rows 261 + candidate = 262nd", "rows 262 + candidate = 263rd", 2, "p3_owner261")
rep("; bm-c rows 90 +", "; bm-c rows 91 +", 1, "p3_comment_split")
rep("bm-c rows 90 + candidate = 91st owned", "bm-c rows 91 + candidate = 92nd owned", 1, "p3_receipt_owned")
rep("# candidate = 91st EXACT", "# candidate = 92nd EXACT", 1, "p3_comment_91st")
rep("engine_owner==bm-c rows 90 + candidate", "engine_owner==bm-c rows 91 + candidate", 1, "p3_pr_eo")
rep("bm-c rows {len(bmc_rows_live)} + candidate (91st own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (92nd own wave", 1, "p3_gate05_print")
rep("bm-c's 91st own wave", "bm-c's 92nd own wave", 2, "p3_91st_own")
rep("NINETY-FIRST owned", "NINETY-SECOND owned", 3, "p3_91st_caps")
rep("TWO HUNDRED AND SEVENTY-SECOND", "TWO HUNDRED AND SEVENTY-THIRD", 3, "p3_wave_caps")
# 7 raw bmc_rows=90 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=90", "bmc_rows=91", 6, "p3_bmc_rows90")
rep('"probe_receipt_bmc_ordinal_face": 90', '"probe_receipt_bmc_ordinal_face": 91', 1, "p3_probe_face_key")
# ordinal narrative: B-ordinal TWENTY-SECOND->TWENTY-THIRD FIRST, then A-ordinal TWENTY-FIRST->TWENTY-SECOND
rep("TWENTY-SECOND", "TWENTY-THIRD", 7, "p3_22_caps")
rep("TWENTY-FIRST", "TWENTY-SECOND", 15, "p3_21_caps")
rep("twenty-second", "twenty-third", 4, "p3_22_lc")
rep("twenty-first", "twenty-second", 3, "p3_21_lc")
rep("sixtieth", "sixty-first", 2, "p3_60th")
# wave-number narrative faces
rep("wave 272 engine_owner=bm-c", "wave 273 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 272: "', '"wave 273: "', 1, "p3_cfg_waveface")
rep("wave 272 = first free number", "wave 273 = first free number", 1, "p3_mhdr_waveface")
# cycle/lineage window stamps (SEAT->r1101 / SPLICE->r1100 / FINALIZE->r1100, contexts measured)
rep("cycle COMPLETE bm-c r1097 closeout 18:4x", "cycle COMPLETE bm-c r1100 closeout 20:4x", 1, "p3_hdr_complete")
rep("bm-c r1097 splice window", "bm-c r1100 splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1097", "own-wave full cycle r1100", 1, "p3_repair_note")
rep("bm-c splice generation r1097 window", "bm-c splice generation r1100 window", 1, "p3_parity_source")
rep("verified r1097", "verified r1100", 1, "p3_lineage_verified")
rep("# r1097 splice window", "# r1100 splice window", 1, "p3_lineage_r")
rep("(bm-c r1097", "(bm-c r1100", 1, "p3_parity_comment")
rep("finalize one-pass bm-c r1097 closeout, ledger", "finalize one-pass bm-c r1100 closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1097 closeout ledger", "finalize one-pass bm-c r1100 closeout ledger", 1, "p3_finpass_hdr")
rep("(r1098 MSG-", "(r1101 MSG-", 1, "p3_hdr_msgline")
rep("r1098 BEFORE this freeze", "r1101 BEFORE this freeze", 1, "p3_receipt_seatnote")
rep("seat itself r1098; queue-head", "seat itself r1101; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1098, queue-head seat-first supply", "(r1101, queue-head seat-first supply", 1, "p3_pfcomment_seat")
# prereg window map (W272 prereg r1099 window -> W273 prereg r1102 window; 4 raw
# bm-c r1099 window minus 2 whose tails were consumed by p1_prereg_method)
rep("bm-c r1099 window", "bm-c r1102 window", 4, "p3_prereg_window")
rep("# r1099 window", "# r1102 window", 1, "p3_hdr_prereg_window")
# lineage header: canon template identity rolls to the W272 canon
# (p1_lineage_template already handled _w271bmc_ -> _w272bmc_)
# not-a-re-pick face
rep("(R271: ", "(R272: ", 1, "p3_repick")
# r1076-family ROOT CURE +1 aging law (NOT the mechanical form)
rep("_set_wave(272)", "_set_wave(273)", 1, "p3_setwave_rootcure")

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
assert t.count("20261018") == 17, "carried date face drift"
# healed faces present
assert t.count("engine_owner=bm-c (bm-c OWN-SEAT face") == 1, "heal-1 face missing"
assert t.count("bm-c's NINETY-SECOND owned per machine-derive (engine_owner==bm-c") == 1, "heal-2 face missing"
assert t.count("bm-c\\'s NINETY-SECOND owned claim per ") == 1, "heal-3 face missing"
assert t.count("bmc rows 91 + candidate 92nd") == 1, "heal-5 face missing"
assert t.count("E63 canon-clone builder derive landed pre-freeze") == 2, "heal-7 face missing"
assert t.count("_r1102bmc_build_w273_derive.py") == 1, "heal-7 header face missing"
assert t.count("legs (24 rows) do NOT enter the estate path") == 1, "heal-6 face missing"
assert t.count("bm-a") == 5, "residual bm-a faces (expect 5: bma_rows_live code + 4 ADMIT-convention law names)"
# residual sweep (r1091 law: self-produced faces EXCLUDED -- 615_701/615_900
# fresh prior-band faces, "W270" inside the fresh relkeys, "_w272bmc_"
# lineage-template face, "if w < 272)" anti-gate needle, "range(248, 272)"
# fresh dropped-range assert, n1_w272/n1w272- absent but w272_/n1_w272 fresh upstream)
for gone in ("r1097", "r1098", "r1099", "18:4x", "19:2x", "20:2x", "17:3x",
             "c049a57623", "7dd091eef1", "f608ff1cee",
             "1c814343ed", "f75b18c862", "87d2697cdc",
             "MSG-20261018-191x-bmc-w272-seat", "_w271bmc_",
             "n1_w271", "n1w271-", "w271_", "n1w272-",
             "613_501", "613_700", "613_701", "613_900", "615_500", "615_700",
             "611_301", "611_500", "611_501", "611_700", "613_300",
             "615701", "617700", "615901", "616100",
             "1,020,535", "594,120", "1_020_535", "594_120",
             "1,007,335", "580,920", "1_007_335", "580_920",
             "1,009,535", "583,120", "1_009_535", "583_120",
             "1,011,735", "585,320", "1_011_735", "585_320",
             "1,013,935", "587,520", "1_013_935", "587_520",
             "1,016,135", "589,720", "1_016_135", "589_720",
             "1,018,335", "591,920", "1_018_335", "591_920",
             "W273p", "W272p", "W271p", "W270p", "W269p",
             "W269_W270_W271_bands_respected", "W268_W269_W270_bands_respected",
             "rows 261 + candidate", "bmc_rows=90", "261/130/90",
             "NINETY-FIRST owned", "TWO HUNDRED AND SEVENTY-SECOND",
             "TWENTY-FIRST", "twenty-first", "sixtieth", "sixty legs",
             "wave 272 engine_owner=bm-c", '"wave 272: "', "wave 272 = first free number",
             '"wave": 271',
             "engine_owner=bm-a (bm-c OWN-SEAT face", "bm-a own-seat",
             "bma rows 129 + candidate 130th", "machine-SUB", "committed+pushed",
             "arith_a272", "arith_b272",
             "range(16, 272)", "range(17, 272)", "range(209, 273)",
             "range(248, 271)", "range(211, 271)", "if w < 271)",
             "272 - _lw", "_w == 271",
             "PERPETUAL-N1-W271", "PERPETUAL_N1_W271"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
  'MSG-20261018-211x-bmc-w273-seat': 7, "39e1bb32f1": 2, "_w273bmc_": 11, "_w272bmc_": 1,
  "20261018": 17, "c99ee20a4": 1,
  "b6bbb69e92": 2, "839441a547": 1, "eeb3bf07ad": 1,
  "615_701": 4, "615_900": 6, "615_901": 8, "616_100": 2,
  "617_700": 2, "617_900": 9, "617_901": 5, "618_100": 4,
  "617901": 1, "619900": 1, "618101": 2, "618300": 2,
  "1,022,735": 6, "596,320": 6, "1_022_735": 1, "596_320": 1,
  "n1_w273": 4, "n1_w272": 4, "n1w273-": 2,
  "n1_w273_results.json": 2, "n1_w272_results.json": 4,
  '273: {"batch"': 2, '272: {"batch"': 2, '271: {"batch"': 0,
  '273: {{"batch"': 1, '273: {"a"': 1, '272: {"a"': 3, '273: {{"a"': 2, '272: {{"a"': 0,
  "range(248, 273)": 2, "range(248, 272)": 1, "range(16, 273)": 2, "range(17, 273)": 3,
  "range(209, 274)": 2, "range(211, 272)": 1, "range(211, 248)": 1, "range(138, 207)": 1,
  "if w < 273)": 5, "if w < 272)": 1, "273 - _lw": 2,
  "m248": 4, "m211": 4, "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
  "WAVE_CONFIGS[273]": 2, "WAVE_CONFIGS[272]": 3, "N1_BANDS[272]": 5,
  "get(272)": 1, "_c272": 5,
  "arith_a273": 6, "arith_b273": 6,
  "(269, 268, 267, 266, 265, 264, 263, 262, 261, 260)": 2, "W260..W269": 1,
  "len(owner_rows_live) == 262": 1, "262/130/91": 1, "bmc_rows=91": 7,
  "rows 262 + candidate = 263rd": 2, "bm-c rows 91 + candidate = 92nd owned": 1,
  "NINETY-SECOND owned": 3, "TWO HUNDRED AND SEVENTY-THIRD": 3,
  "TWENTY-THIRD": 7, "TWENTY-SECOND": 15, "twenty-third": 4, "twenty-second": 3,
  "W270_W271_W272_bands_respected": 2, "W274p": 13, "W274": 26,
  "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
  "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
  "W273 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
  "the bm-c r1100 splice window": 2,
  "bm-c own seat executed at the bm-c r1100 splice window": 1,
  "finalize one-pass bm-c r1100": 2,
  "authored 22:4x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
  "cycle COMPLETE bm-c r1100 closeout 20:4x": 1,
  "verified r1100": 1, "(R272: ": 1, "_w == 272": 1,
  "wave 273 engine_owner=bm-c": 1, '"wave 273: "': 1,
  "wave 273 = first free number": 1, "sixty-first": 2, "sixty-one legs": 1,
  'N1_BANDS[") == 130,': 1, '!= 130': 1, 'N1_BANDS[") == 61': 1,
  'N1_BANDS[") == 37': 1, 'N1_BANDS[") == 24': 1,
  "W211..W271 legs (61)": 1, "W211..W272 legs 61": 1,
  "own W248..W271 legs (24)": 4, "own W248..W271": 5, "W248..W273 legs (25": 4,
  "block = 131 rows": 1, "131 parity rows": 1, "block parity = 131 rows": 1,
  "bm-c r1102 window": 4, "# r1102 window": 1,
  "bm-c splice generation r1100 window": 1, "(bm-c r1100": 1,
  "_w272bmc_freeze_edits.py template": 1,
  "PERPETUAL_N1_W273_PREREG": 8, "PERPETUAL_N1_W272_PREREG": 2, "PERPETUAL-N1-W273": 7,
  "W273 materializer face": 4, "W272 materializer face": 1,
  "W271 finalize product": 0, "W272 finalize product": 4,
  "engine_owner==bm-c rows 91 + candidate": 1, "# candidate = 92nd EXACT": 1, "; bm-c rows 91 +": 1,
  "bm-c rows {len(bmc_rows_live)} + candidate (92nd own wave": 1,
  "bm-c's 92nd own wave": 2, "owner_rows=262 / bma_rows=130 / bmc_rows=91": 1,
  '"probe_receipt_bmc_ordinal_face": 91': 1,
  "fourteen-wave": 8, "post-W272-REGISTERED": 8,
  "anchors W272 1,022,735 / K=596,320 at draft": 1,
  "dual-window parity": 1, "W274 walk": 1,
  "sixty-first consecutive": 2, '"wave": 272': 1,
  "registered wave below 263 composes": 2,
  "PRE-W273-splice": 1, "post-W272 registration": 2,
  "expect 262/130/91": 1,
  "_set_wave(273)": 1, "_set_wave(272)": 0, "_set_wave(271)": 0, "_set_wave(270)": 0, "_set_wave(2)": 1,
  "2026-10-18 23:5x bm-c r1102 splice window": 1,
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
