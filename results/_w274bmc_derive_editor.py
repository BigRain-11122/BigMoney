# -*- coding: utf-8 -*-
# r1105 bm-c splice window: derive results/_w274bmc_freeze_edits.py from the
# committed W273 freeze-edits canon (results/_w273bmc_freeze_edits.py, bm-c
# r1102 splice window 04f2127db, proven live-fire: W273 five-face splice +
# engine self-burn 12/12 + finalize one-pass 6659a0e36 ledger 1,024,935 /
# K=598,520 EXACT, machine-verified by the r1102-continuation absorb window)
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 18th-gen lineage, zero
# transcription: every needle count MEASURED on the canon blob by
# results/_r1105bmc_needle_preflight.py (receipt
# results/_r1105bmc_needle_preflight.json, canon sha256-16 61f31841f61a0809,
# 62,350B, wt==HEAD==origin triple-verified; post-blanket phase-3 forms
# measured on the phase-1+2 simulated text). r1077 measured-counts law.
# DISCLOSED CANON EOL FACE (benign, carried): core.autocrlf=true re-smudge
# (r1093 pit entry) -- canon read raw with newline='' (CRLF form, 800/0
# measured); multi-line needles use the physical CRLF bytes (r775 law).
# W274 FACTS (probe receipt results/_w274bmc_20261019_probe_receipt.json,
# committed with the seat @ 70b21a0264 r1102, ADMIT): bands A 618_101..620_100
# (TWENTY-THIRD consecutive A-hop, staircase-affects-A, hops=1; naive A
# 617_901..619_900 refused at the registered W273 B band 617_901..618_100) /
# B 620_101..620_300 (TWENTY-FOURTH consecutive above-own-A, own-A reservation
# cascade, hops=1; naive B 618_101..618_300 inside the own-A window
# 618_101..620_100); seed_admit FREE x2 (base=618101 span=2000 /
# base=620101 span=200); ordinals owner 263 + candidate = 264th / bm-c rows
# 92 + candidate = 93rd; W273 finalize anchors 1,024,935 / K=598,520 (chain
# +2,200/+2,200 EXACT).
# W274 PREREG: research/PERPETUAL_N1_W274_PREREG.md 23,550B sha256_16
# ddc158b5047596ea (authored 02:2x bm-c r1104 window via E63 canon-clone
# builder _r1104bmc_build_w274_derive.py; frozen + CAS-graft-delivered to
# origin 6f31f6e073 after push#1 non-FF, r1104 window).
# AGING-TOKEN LAW (E63 anti-drift, carried): frozen faces w244_a/w244_b /
# n3r1_used245 / m211 / m248 / "w244_a holds wave-263 bands" /
# "registered wave below 263 composes" do NOT roll (measured 12/8/3/4/4/2
# in canon; carried verbatim, anti-drift asserted). Band order law:
# CONSUMERS before PRODUCERS (617_901/618_100 consumed BEFORE 615_701/615_900
# recreate them). Projections first (W274p -> W275p before plain W274 ->
# W275), then D-swaps (own W273 -> W274 first, then upstream W272 -> W273).
# Ordinal caps: B (TWENTY-THIRD -> TWENTY-FOURTH) before A (TWENTY-SECOND ->
# TWENTY-THIRD). lc blankets: own w273_ (10, after n1_w273 x2 + builder x1
# carve-outs) before upstream w272_ (89, after n1_w272 x4 carve-outs).
# SETWAVE +1 AGING LAW (r1076-family root cure, carried): _set_wave(273) ->
# _set_wave(274); presence gates 274:1 / 273:0 / 272:0.
# r1091 W268 gone-list law honored: self-produced faces EXCLUDED from the
# residual sweep (617_901/618_100 fresh prior-wave-band faces x4/x6; "W270"
# inside the fresh relkeys W271_W272_W273_bands_respected; "_w273bmc_"
# lineage-template face count 1; "if w < 273)" anti-gate needle;
# "range(248, 273)" fresh dropped-range assert; n1_w273/w273_ fresh upstream
# tokens; "~23:5x" CEO fill-order standing faces x4 carried verbatim).
# DATE-ROLL FACE (new this generation): canon receipt paths carry the
# 20261018 date -> W274 probe receipt is dated 20261019; seat-msg rep
# consumes its 7 embedded dates first, then the remaining 10 roll
# 20261018->20261019 (17 total, phase-4 gate 20261019==17).
# Window-stamp disambiguation (measured): SEAT faces -> r1102 (W274 seat
# 70b21a0264); SPLICE/FINALIZE faces -> r1102 (W273 splice 04f2127db +
# finalize 6659a0e36, dead r1102 window; closeout 01:0x r1102-continuation);
# PREREG faces -> r1104 (W274 prereg 6f31f6e073); THIS splice window -> r1105.
import io, subprocess, sys

CANON = "results/_w273bmc_freeze_edits.py"
DST = "results/_w274bmc_freeze_edits.py"
LOG = "results/_r1105bmc_derive_editor_log.txt"
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
       f"(preflight-measured sha256_16 61f31841f61a0809, 62,350B)",
       f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:110]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W274p", "W275p", 13, "p1_proj_prefix")
rep("W274", "W275", 13, "p1_proj_plain")
# bands (CONSUMERS FIRST: 617_901/618_100 consumed before 615_701/615_900
# recreate them -- band-order law; all 8 rep targets measured 5/4/9/2/8/2/4/6)
rep("617_901", "620_101", 5, "p1_band_Blo")
rep("618_100", "620_300", 4, "p1_band_Bhi")
rep("617_900", "620_100", 9, "p1_band_Ahi")
rep("617_700", "619_900", 2, "p1_band_naiveAhi")
rep("615_901", "618_101", 8, "p1_band_Alo_Bnaivelo")
rep("616_100", "618_300", 2, "p1_band_Bnaivehi")
rep("615_701", "617_901", 4, "p1_band_naiveAlo_priorBlo")
rep("615_900", "618_100", 6, "p1_band_priorBhi")
# int-form leg4 projections in the receipt downstream_seat note (probe-measured)
rep("617901", "620101", 1, "p1_int_projAlo")
rep("619900", "622100", 1, "p1_int_projAhi")
rep("618101", "620301", 2, "p1_int_projBlo")
rep("618300", "620500", 2, "p1_int_projBhi")
# ledger/K anchors: W272 finalize facts -> W273 finalize facts (1,024,935/598,520)
rep("1,022,735", "1,024,935", 6, "p1_ledger_prose")
rep("596,320", "598,520", 6, "p1_k_prose")
rep("1_022_735", "1_024_935", 1, "p1_ledger_code")
rep("596_320", "598_520", 1, "p1_k_code")
# builder filename FIRST (consumes its embedded w273_ before the lc blanket)
rep("(E63 canon-clone builder _r1102bmc_build_w273_derive.py)",
    "(E63 canon-clone builder _r1104bmc_build_w274_derive.py)", 1, "p1_builder_method")
# lowercase machine-file tokens (own first, then upstream; the w273_ blanket
# ALSO rolls the current-wave pickaxe vars w273_prereg_sha/w273_receipt_sha ->
# w274_* AFTER the n1_w273 x2 + builder x1 carve-outs; the w272_ blanket rolls
# ALL upstream w272_* variables -> w273_* after the n1_w272 x4 carve-out)
rep("n1_w273", "n1_w274", 4, "p1_n1w273_own")
rep("n1w273-", "n1w274-", 2, "p1_n1w273dash")
rep("w273_", "w274_", 10, "p1_lc_w273_")
rep("n1_w272", "n1_w273", 4, "p1_n1w272_upstream")
rep("w272_", "w273_", 89, "p1_lc_w272_")
# receipt/lineage/seat faces
rep("_w273bmc_", "_w274bmc_", 11, "p1_receiptpath")
rep("_w272bmc_freeze_edits.py template", "_w273bmc_freeze_edits.py template", 1, "p1_lineage_template")
rep("MSG-20261018-211x-bmc-w273-seat", "MSG-20261019-012x-bmc-w274-seat", 7, "p1_seat_msg")
rep('SEAT_ORIGIN = "39e1bb32f1"', 'SEAT_ORIGIN = "70b21a0264"', 1, "p1_seat_origin_const")
rep("39e1bb32f1 r1101", "70b21a0264 r1102", 1, "p1_seat_origin_hdr")
rep("c99ee20a4", "04f2127db", 1, "p1_lineage_sha")
# prereg delivery prose (r1104 CAS-graft delivery + E63 builder method)
rep("(authored 22:4x, banned_direction_gate ADMIT rc0, frozen b6bbb69e92 + surgery-" + CRLF +
    "# delivered to origin 839441a547 + receipts eeb3bf07ad, r1102 window).",
    "(authored 02:2x, banned_direction_gate ADMIT rc0, frozen sha16 ddc158b5047596ea + CAS-" + CRLF +
    "# graft-delivered to origin 6f31f6e073, r1104 window).",
    1, "p1_prereg_delivery_hdr")
rep("(authored 22:4x, banned gate ADMIT rc0, frozen b6bbb69e92 -> surgery-delivered r1102 origin ",
    "(authored 02:2x, banned gate ADMIT rc0, frozen ddc158b5047596ea -> CAS-graft-delivered r1104 origin ",
    1, "p1_prereg_delivery_note")
# header window stamp
rep("2026-10-18 23:5x bm-c r1102 splice window", "2026-10-19 02:5x bm-c r1105 splice window", 1, "p1_hdr_stamp")
# receipt wave field (mechanical +1): 272->273
rep('"wave": 272', '"wave": 273', 1, "p1_receipt_wave")
# date roll (remaining after the seat-msg rep consumed its 7 embedded dates)
rep("20261018", "20261019", 10, "p1_date_roll")

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W273", "W274", 96, "p2_own_wave")
rep("W272", "W273", 158, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
# relkey = POST-BLANKET form (the upstream blanket rolled the W272 inside
# "W270_W271_W272_bands_respected" -> "W270_W271_W273"; this rep rolls the
# first two positions +1 to the W274 probe receipt's relation keys)
rep("W270_W271_W273_bands_respected", "W271_W272_W273_bands_respected", 2, "p3_relkey")
# legs_sec prose + message (W274 extraction: legs W211..W272 = 62)
rep("W211..W271 legs (61)", "W211..W272 legs (62)", 1, "p3_legs_prose")
rep("W211..W271 sixty-one legs", "W211..W272 sixty-two legs", 1, "p3_legs_msg")
rep("range(211, 272)", "range(211, 273)", 1, "p3_range_legs")
# dropped faces (W274 extraction drops the W273 block's own W248..W272 = 25 legs)
rep("own W248..W271 legs (24)", "own W248..W272 legs (25)", 4, "p3_dropped_narr")
rep("own W248..W271" + CRLF + "# legs (24 rows) do NOT enter the estate path",
    "own W248..W272" + CRLF + "# legs (25 rows) do NOT enter the estate path", 1, "p3_dropped_split_hdr")
rep("W248..W271 twenty-four legs", "W248..W272 twenty-five legs", 1, "p3_dropped_fstring")
rep('N1_BANDS[") == 24', 'N1_BANDS[") == 25', 1, "p3_dropped_count")
# fullspan error-string (POST-BLANKET wave face rolled by the upstream
# blanket: "W211..W272 legs 61" -> "W211..W273 legs 61"; count 61->62)
rep("W211..W273 legs 61", "W211..W273 legs 62", 1, "p3_fullspan_fstring")
# fresh legs (W274 block appends fresh W248..W273 = 26 legs; POST-OWN-BLANKET
# form -- the own blanket rolled the hi face to the new range end 274;
# count-only roll 25->26, hi rides the blanket = range(248, 274) END EXACT)
rep("W248..W274 legs (25", "W248..W274 legs (26", 4, "p3_fresh_narr")
# block/parity counts: W274 block = 69 estate + 37 kept + 26 fresh = 132
rep("block = 131 rows", "block = 132 rows", 1, "p3_block131")
rep("131 parity rows", "132 parity rows", 1, "p3_parity131")
rep("block parity = 131 rows", "block parity = 132 rows", 1, "p3_blockparity131")
rep('N1_BANDS[") == 130,', 'N1_BANDS[") == 131,', 1, "p3_count130")
rep('!= 130', '!= 131', 1, "p3_fstring130")
rep('N1_BANDS[") == 61', 'N1_BANDS[") == 62', 1, "p3_count61")
rep('"fresh_legs_row_asserts": 25', '"fresh_legs_row_asserts": 26', 1, "p3_receipt_fresh")
rep('+ 25,', '+ 26,', 1, "p3_receipt_total")
# ranges (fresh FIRST then dropped-producer, then the cumulative/registry faces)
rep("range(248, 273)", "range(248, 274)", 2, "p3_range_fresh")
rep("range(248, 272)", "range(248, 273)", 1, "p3_range_dropped")
rep("range(16, 273)", "range(16, 274)", 2, "p3_range16")
rep("range(17, 273)", "range(17, 274)", 3, "p3_range17")
rep("range(209, 274)", "range(209, 275)", 2, "p3_range209")
# wave-number gates (own 273->274 FIRST, then anti-gate 272->273)
rep("if w < 273)", "if w < 274)", 5, "p3_wlt273")
rep("if w < 272)", "if w < 273)", 1, "p3_wlt272_antigate")
rep("273 - _lw", "274 - _lw", 2, "p3_legcount")
rep("_w == 272", "_w == 273", 1, "p3_freshmsg_cond")
# cfg/row faces: own 273->274 FIRST, then upstream 272->273
rep("WAVE_CONFIGS[273]", "WAVE_CONFIGS[274]", 2, "p3_wavecfg273_own")
rep("WAVE_CONFIGS[272]", "WAVE_CONFIGS[273]", 3, "p3_wavecfg272")
rep("N1_BANDS[272]", "N1_BANDS[273]", 5, "p3_n1bands272")
rep("get(272)", "get(273)", 1, "p3_get272")
rep("_c272", "_c273", 5, "p3_c272var")
rep('273: {"batch"', '274: {"batch"', 2, "p3_cfg273")
rep('273: {{"batch"', '274: {{"batch"', 1, "p3_cfg273_fstring")
rep('273: {"a"', '274: {"a"', 1, "p3_row273")
rep('273: {{"a"', '274: {{"a"', 2, "p3_row273_fstring")
rep('272: {"batch"', '273: {"batch"', 2, "p3_cfg272")
rep('272: {"a"', '273: {"a"', 3, "p3_row272")
rep("arith_a273", "arith_a274", 6, "p3_arith_a")
rep("arith_b273", "arith_b274", 6, "p3_arith_b")
rep("(269, 268, 267, 266, 265, 264, 263, 262, 261, 260)",
    "(270, 269, 268, 267, 266, 265, 264, 263, 262, 261)", 2, "p3_transitive_list")
rep("W260..W269", "W261..W270", 1, "p3_transitive_window")
# ordinal faces: owner 262->263, bma 130 held, bmc 91->92 (W274 = 264th candidate, bm-c 93rd own)
rep("len(owner_rows_live) == 262 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 91",
    "len(owner_rows_live) == 263 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 92", 1, "p3_ordinal_assert")
rep("262/130/91", "263/130/92", 1, "p3_ordinal_expect")
rep("owner_rows=262 / bma_rows=130 / bmc_rows=91",
    "owner_rows=263 / bma_rows=130 / bmc_rows=92", 1, "p3_leg0_face")
rep("rows 262 + candidate = 263rd", "rows 263 + candidate = 264th", 2, "p3_owner262")
rep("; bm-c rows 91 +", "; bm-c rows 92 +", 1, "p3_comment_split")
rep("bm-c rows 91 + candidate = 92nd owned", "bm-c rows 92 + candidate = 93rd owned", 1, "p3_receipt_owned")
rep("# candidate = 92nd EXACT", "# candidate = 93rd EXACT", 1, "p3_comment_93rd")
rep("engine_owner==bm-c rows 91 + candidate", "engine_owner==bm-c rows 92 + candidate", 1, "p3_pr_eo")
rep("bm-c rows {len(bmc_rows_live)} + candidate (92nd own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (93rd own wave", 1, "p3_gate05_print")
rep("bm-c's 92nd own wave", "bm-c's 93rd own wave", 2, "p3_92nd_own")
rep("NINETY-SECOND owned", "NINETY-THIRD owned", 3, "p3_92nd_caps")
rep("TWO HUNDRED AND SEVENTY-THIRD", "TWO HUNDRED AND SEVENTY-FOURTH", 3, "p3_wave_caps")
# 7 raw bmc_rows=91 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=91", "bmc_rows=92", 6, "p3_bmc_rows91")
rep('"probe_receipt_bmc_ordinal_face": 91', '"probe_receipt_bmc_ordinal_face": 92', 1, "p3_probe_face_key")
rep("bmc rows 91 + candidate 92nd", "bmc rows 92 + candidate 93rd", 1, "p3_hdr_ordinal")
# ordinal narrative: B-ordinal TWENTY-THIRD->TWENTY-FOURTH FIRST, then A-ordinal TWENTY-SECOND->TWENTY-THIRD
rep("TWENTY-THIRD", "TWENTY-FOURTH", 7, "p3_23_caps")
rep("TWENTY-SECOND", "TWENTY-THIRD", 15, "p3_22_caps")
rep("twenty-third", "twenty-fourth", 4, "p3_23_lc")
rep("twenty-second", "twenty-third", 3, "p3_22_lc")
rep("sixty-first", "sixty-second", 2, "p3_61st")
# wave-number narrative faces
rep("wave 273 engine_owner=bm-c", "wave 274 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 273: "', '"wave 274: "', 1, "p3_cfg_waveface")
rep("wave 273 = first free number", "wave 274 = first free number", 1, "p3_mhdr_waveface")
# cycle/lineage window stamps (SEAT->r1102 / SPLICE->r1102 / FINALIZE->r1102
# closeout 01:0x r1102-continuation / PREREG->r1104; contexts measured)
rep("cycle COMPLETE bm-c r1100 closeout 20:4x", "cycle COMPLETE bm-c r1102 closeout 01:0x", 1, "p3_hdr_complete")
rep("bm-c r1100 splice window", "bm-c r1102 splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1100", "own-wave full cycle r1102", 1, "p3_repair_note")
rep("bm-c splice generation r1100 window", "bm-c splice generation r1102 window", 1, "p3_parity_source")
rep("verified r1100", "verified r1102", 1, "p3_lineage_verified")
rep("# r1100 splice window", "# r1102 splice window", 1, "p3_lineage_r")
rep("(bm-c r1100", "(bm-c r1102", 1, "p3_parity_comment")
rep("finalize one-pass bm-c r1100 closeout, ledger", "finalize one-pass bm-c r1102 closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1100 closeout ledger", "finalize one-pass bm-c r1102 closeout ledger", 1, "p3_finpass_hdr")
rep("(r1101 MSG-", "(r1102 MSG-", 1, "p3_hdr_msgline")
rep("r1101 BEFORE this freeze", "r1102 BEFORE this freeze", 1, "p3_receipt_seatnote")
rep("seat itself r1101; queue-head", "seat itself r1102; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1101, queue-head seat-first supply", "(r1102, queue-head seat-first supply", 1, "p3_pfcomment_seat")
# prereg window map (W273 prereg r1102 window -> W274 prereg r1104 window)
rep("bm-c r1102 window", "bm-c r1104 window", 4, "p3_prereg_window")
rep("# r1102 window", "# r1104 window", 1, "p3_hdr_prereg_window")
# not-a-re-pick face
rep("(R272: ", "(R273: ", 1, "p3_repick")
# r1076-family ROOT CURE +1 aging law (NOT the mechanical form)
rep("_set_wave(273)", "_set_wave(274)", 1, "p3_setwave_rootcure")

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
assert t.count("20261019") == 17, "new date face drift (17 expected post-roll)"
assert t.count("~23:5x") == 4, "carried CEO fill-order ~23:5x face drift"
assert t.count("bm-a") == 5, "residual bm-a faces (expect 5: bma_rows_live code + 4 ADMIT-convention law names)"
# residual sweep (r1091 law: self-produced faces EXCLUDED -- 617_901/618_100
# fresh prior-band faces x4/x6, "W270" inside the fresh relkeys, "_w273bmc_"
# lineage-template face, "if w < 273)" anti-gate needle, "range(248, 273)"
# fresh dropped-range assert, n1_w273/w273_ fresh upstream tokens, PERPETUAL_N1_W273_PREREG upstream refs)
for gone in ("r1100", "r1101", "20:4x", "22:4x",
             "c99ee20a4", "39e1bb32f1",
             "b6bbb69e92", "839441a547", "eeb3bf07ad",
             "MSG-20261018-211x", "_w272bmc_",
             "n1_w272", "w272_", "n1w272-",
             "615_901", "616_100", "617_700", "617_900", "615_701", "615_900",
             "617901", "619900", "618101", "618300",
             "1,022,735", "596,320", "1_022_735", "596_320",
             "W274p", "W273p", "W272p", "W271p",
             "W270_W271_W273_bands_respected",
             "rows 262 + candidate", "bmc_rows=91", "262/130/91",
             "NINETY-SECOND owned", "TWO HUNDRED AND SEVENTY-THIRD",
             "TWENTY-SECOND", "twenty-second", "sixty-first", "sixty-one legs",
             "wave 273 engine_owner=bm-c", '"wave 273: "', "wave 273 = first free number",
             '"wave": 272',
             "arith_a273", "arith_b273",
             "range(16, 273)", "range(17, 273)", "range(209, 274)",
             "range(248, 272)", "range(211, 272)", "if w < 272)",
             "273 - _lw", "_w == 272",
             "PERPETUAL-N1-W273", "20261018", "2026-10-18"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
  'MSG-20261019-012x-bmc-w274-seat': 7, "70b21a0264": 2, "_w274bmc_": 11, "_w273bmc_": 1,
  "20261019": 17, "04f2127db": 1,
  "ddc158b5047596ea": 2, "6f31f6e073": 1,
  "620_101": 5, "620_300": 4, "620_100": 9, "619_900": 2,
  "618_101": 8, "618_300": 2, "617_901": 4, "618_100": 6,
  "620101": 1, "622100": 1, "620301": 2, "620500": 2,
  "1,024,935": 6, "598,520": 6, "1_024_935": 1, "598_520": 1,
  "n1_w274": 4, "n1_w273": 4, "n1w274-": 2,
  "n1_w274_results.json": 2, "n1_w273_results.json": 4,
  '274: {"batch"': 2, '273: {"batch"': 2, '272: {"batch"': 0,
  '274: {{"batch"': 1, '274: {"a"': 1, '273: {"a"': 3, '274: {{"a"': 2, '273: {{"a"': 0,
  "range(248, 274)": 2, "range(248, 273)": 1, "range(16, 274)": 2, "range(17, 274)": 3,
  "range(209, 275)": 2, "range(211, 273)": 1, "range(211, 248)": 1, "range(138, 207)": 1,
  "if w < 274)": 5, "if w < 273)": 1, "274 - _lw": 2,
  "m248": 4, "m211": 4, "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
  "WAVE_CONFIGS[274]": 2, "WAVE_CONFIGS[273]": 3, "N1_BANDS[273]": 5,
  "get(273)": 1, "_c273": 5,
  "arith_a274": 6, "arith_b274": 6,
  "(270, 269, 268, 267, 266, 265, 264, 263, 262, 261)": 2, "W261..W270": 1,
  "len(owner_rows_live) == 263": 1, "263/130/92": 1, "bmc_rows=92": 7,
  "rows 263 + candidate = 264th": 2, "bm-c rows 92 + candidate = 93rd owned": 1,
  "NINETY-THIRD owned": 3, "TWO HUNDRED AND SEVENTY-FOURTH": 3,
  "TWENTY-FOURTH": 7, "TWENTY-THIRD": 15, "twenty-fourth": 4, "twenty-third": 3,
  "W271_W272_W273_bands_respected": 2, "W275p": 13, "W275": 26,
  "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
  "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
  "W274 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
  "the bm-c r1102 splice window": 2,
  "bm-c own seat executed at the bm-c r1102 splice window": 1,
  "finalize one-pass bm-c r1102": 2,
  "authored 02:2x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
  "cycle COMPLETE bm-c r1102 closeout 01:0x": 1,
  "verified r1102": 1, "(R273: ": 1, "_w == 273": 1,
  "wave 274 engine_owner=bm-c": 1, '"wave 274: "': 1,
  "wave 274 = first free number": 1, "sixty-second": 2, "sixty-two legs": 1,
  'N1_BANDS[") == 131,': 1, '!= 131': 1, 'N1_BANDS[") == 62': 1,
  'N1_BANDS[") == 37': 1, 'N1_BANDS[") == 25': 1,
  "W211..W272 legs (62)": 1, "W211..W273 legs 62": 1,
  "own W248..W272 legs (25)": 4, "own W248..W272": 5, "W248..W274 legs (26": 4,
  "block = 132 rows": 1, "132 parity rows": 1, "block parity = 132 rows": 1,
  "bm-c r1104 window": 4, "# r1104 window": 1,
  "bm-c splice generation r1102 window": 1, "(bm-c r1102": 1,
  "_w273bmc_freeze_edits.py template": 1,
  "PERPETUAL_N1_W274_PREREG": 8, "PERPETUAL_N1_W273_PREREG": 2, "PERPETUAL-N1-W274": 7,
  "W274 materializer face": 4, "W273 materializer face": 1,
  "W272 finalize product": 0, "W273 finalize product": 4,
  "engine_owner==bm-c rows 92 + candidate": 1, "# candidate = 93rd EXACT": 1, "; bm-c rows 92 +": 1,
  "bm-c rows {len(bmc_rows_live)} + candidate (93rd own wave": 1,
  "bm-c's 93rd own wave": 2, "owner_rows=263 / bma_rows=130 / bmc_rows=92": 1,
  '"probe_receipt_bmc_ordinal_face": 92': 1,
  "fourteen-wave": 8, "post-W273-REGISTERED": 8,
  "anchors W273 1,024,935 / K=598,520 at draft": 1,
  "dual-window parity": 1, "W275 walk": 1,
  "sixty-second consecutive": 2, '"wave": 273': 1,
  "registered wave below 263 composes": 2,
  "PRE-W274-splice": 1, "post-W273 registration": 2,
  "expect 263/130/92": 1,
  "_set_wave(274)": 1, "_set_wave(273)": 0, "_set_wave(272)": 0, "_set_wave(2)": 1,
  "2026-10-19 02:5x bm-c r1105 splice window": 1,
  "derived by the bm-c": 2,
  "bm-c own-seat continuity": 2,
  "physical bytes": 6,
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
