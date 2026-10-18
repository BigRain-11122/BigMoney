# -*- coding: utf-8 -*-
# r1108 bm-c splice window: derive results/_w275bmc_freeze_edits.py from the
# committed W274 freeze-edits canon (results/_w274bmc_freeze_edits.py, bm-c
# r1105 splice window ec907d164, proven live-fire: W274 five-face splice +
# engine self-burn 12/12 + finalize one-pass acf37937ec ledger 1,027,135 /
# K=600,720 EXACT, machine-verified by the r1105 closeout c4e752d682)
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 19th-gen lineage, zero
# transcription: every needle count MEASURED on the canon blob by
# results/_r1108bmc_needle_preflight.py (receipt
# results/_r1108bmc_needle_preflight.json, canon sha256-16 11fbcfbb16b8f96d,
# 62,345B, wt==HEAD==origin triple-verified; post-blanket phase-3 forms
# measured on the phase-1+2 simulated text). r1077 measured-counts law.
# DISCLOSED CANON EOL FACE (benign, carried): core.autocrlf=true re-smudge
# (r1093 pit entry) -- canon read raw with newline='' (CRLF form); multi-line
# needles use the physical CRLF bytes (r775 law).
# W275 FACTS (probe receipt results/_w275bmc_20261019_probe_receipt.json,
# committed with the seat @ bf4bbbde1 r1106, ADMIT): bands A 620_301..622_300
# (TWENTY-FOURTH consecutive A-hop, staircase-affects-A, hops=1; naive A
# 620_101..622_100 refused at the registered W274 B band 620_101..620_300) /
# B 622_301..622_500 (TWENTY-FIFTH consecutive above-own-A, own-A reservation
# cascade, hops=1; naive B 620_301..620_500 inside the own-A window
# 620_301..622_300); seed_admit FREE x2 (base=620301 span=2000 /
# base=622301 span=200); ordinals owner 264 + candidate = 265th / bm-c rows
# 93 + candidate = 94th; W274 finalize anchors 1,027,135 / K=600,720 (chain
# +2,200/+2,200 EXACT); leg4 W276+ projection naive A 622_301..624_300 /
# naive B 622_501..622_700 (own-A reservation face).
# W275 PREREG: research/PERPETUAL_N1_W275_PREREG.md 23,551B sha256_16
# e4e1ce44f5afd03b (authored 04:4x bm-c r1107 window via E63 canon-clone
# builder _r1107bmc_build_w275_derive.py; pushed FIRST-TRY to origin
# 1fcc0bc30f -- NO CAS graft this generation, disclosed).
# AGING-TOKEN LAW (E63 anti-drift, carried): frozen faces w244_a/w244_b /
# n3r1_used245 / m211 / m248 / "w244_a holds wave-263 bands" /
# "registered wave below 263 composes" do NOT roll (measured 12/8/3/4/4/2
# in canon; carried verbatim, anti-drift asserted). Band order law:
# CONSUMERS before PRODUCERS (620_101/620_300 consumed BEFORE 617_901/618_100
# recreate them). Projections first (W276p -> W275p-order mirror: canon
# W275p rolls to W276p before plain W275 -> W276), then D-swaps (own W274 ->
# W275 first, then upstream W273 -> W274). Ordinal caps: B
# (TWENTY-FOURTH -> TWENTY-FIFTH) before A (TWENTY-THIRD -> TWENTY-FOURTH).
# lc blankets: own w274_ (10, after n1_w274_results.json x2 + builder x1
# carve-outs) before upstream w273_ (89, after n1_w273_results.json x4
# carve-outs).
# SETWAVE +1 AGING LAW (r1076-family root cure, carried): _set_wave(274) ->
# _set_wave(275); presence gates 275:1 / 274:0 / 273:0.
# DATE-ROLL FACE (count 0 this generation, DISCLOSED): canon receipts already
# dated 20261019 and the W275 seat/probe receipts are same-date -- the W274
# editor's p1_date_roll rep is DROPPED this generation (zero 20261018 faces
# in canon, preflight-measured); the "20261019" x17 gate carries verbatim.
# Window-stamp disambiguation (measured): SEAT faces -> r1106 (W275 seat
# bf4bbbde1); SPLICE/FINALIZE/CLOSEOUT faces -> r1105 (W274 splice
# ec907d164 + finalize acf37937ec + closeout c4e752d682 03:21:34);
# PREREG faces -> r1107 (W275 prereg 1fcc0bc30f); THIS splice window -> r1108.
import io, subprocess, sys

CANON = "results/_w274bmc_freeze_edits.py"
DST = "results/_w275bmc_freeze_edits.py"
LOG = "results/_r1108bmc_derive_editor_log.txt"
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
       f"(preflight-measured sha256_16 11fbcfbb16b8f96d, 62,345B)",
       f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:110]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W275p", "W276p", 13, "p1_proj_prefix")
rep("W275", "W276", 13, "p1_proj_plain")
# bands (CONSUMERS FIRST: 620_101/620_300 consumed before 617_901/618_100
# recreate them -- band-order law; all 8 rep targets measured 5/4/9/2/8/2/4/6)
rep("620_101", "622_301", 5, "p1_band_Blo")
rep("620_300", "622_500", 4, "p1_band_Bhi")
rep("620_100", "622_300", 9, "p1_band_Ahi")
rep("619_900", "622_100", 2, "p1_band_naiveAhi")
rep("618_101", "620_301", 8, "p1_band_Alo_Bnaivelo")
rep("618_300", "620_500", 2, "p1_band_Bnaivehi")
rep("617_901", "620_101", 4, "p1_band_naiveAlo_priorBlo")
rep("618_100", "620_300", 6, "p1_band_priorBhi")
# int-form leg4 projections in the receipt downstream_seat note (probe-measured)
rep("620101", "622301", 1, "p1_int_projAlo")
rep("622100", "624300", 1, "p1_int_projAhi")
rep("620301", "622501", 2, "p1_int_projBlo")
rep("620500", "622700", 2, "p1_int_projBhi")
# ledger/K anchors: W273 finalize facts -> W274 finalize facts (1,027,135/600,720)
rep("1,024,935", "1,027,135", 6, "p1_ledger_prose")
rep("598,520", "600,720", 6, "p1_k_prose")
rep("1_024_935", "1_027_135", 1, "p1_ledger_code")
rep("598_520", "600_720", 1, "p1_k_code")
# builder filename FIRST (consumes its embedded w274_ before the lc blanket)
rep("(E63 canon-clone builder _r1104bmc_build_w274_derive.py)",
    "(E63 canon-clone builder _r1107bmc_build_w275_derive.py)", 1, "p1_builder_method")
# lowercase machine-file tokens (own first, then upstream; the w274_ blanket
# ALSO rolls the current-wave pickaxe vars w274_prereg_sha/w274_receipt_sha ->
# w275_* AFTER the n1_w274_results.json x2 + builder x1 carve-outs; the
# w273_ blanket rolls ALL upstream w273_* variables -> w274_* after the
# n1_w273_results.json x4 carve-out)
rep("n1_w274", "n1_w275", 4, "p1_n1w274_own")
rep("n1w274-", "n1w275-", 2, "p1_n1w274dash")
rep("w274_", "w275_", 10, "p1_lc_w274_")
rep("n1_w273", "n1_w274", 4, "p1_n1w273_upstream")
rep("w273_", "w274_", 89, "p1_lc_w273_")
# receipt/lineage/seat faces
rep("_w274bmc_", "_w275bmc_", 11, "p1_receiptpath")
rep("_w273bmc_freeze_edits.py template", "_w274bmc_freeze_edits.py template", 1, "p1_lineage_template")
rep("MSG-20261019-012x-bmc-w274-seat", "MSG-20261019-034x-bmc-w275-seat", 7, "p1_seat_msg")
rep('SEAT_ORIGIN = "70b21a0264"', 'SEAT_ORIGIN = "bf4bbbde1"', 1, "p1_seat_origin_const")
rep("70b21a0264 r1102", "bf4bbbde1 r1106", 1, "p1_seat_origin_hdr")
rep("04f2127db", "ec907d164", 1, "p1_lineage_sha")
# prereg delivery prose (r1107 first-try push + E63 builder method)
rep("(authored 02:2x, banned_direction_gate ADMIT rc0, frozen sha16 ddc158b5047596ea + CAS-" + CRLF +
    "# graft-delivered to origin 6f31f6e073, r1104 window).",
    "(authored 04:4x, banned_direction_gate ADMIT rc0, frozen sha16 e4e1ce44f5afd03b + pushed-" + CRLF +
    "# first-try to origin 1fcc0bc30f, r1107 window).",
    1, "p1_prereg_delivery_hdr")
rep("(authored 02:2x, banned gate ADMIT rc0, frozen ddc158b5047596ea -> CAS-graft-delivered r1104 origin ",
    "(authored 04:4x, banned gate ADMIT rc0, frozen e4e1ce44f5afd03b -> pushed first-try r1107 origin ",
    1, "p1_prereg_delivery_note")
# header window stamp
rep("2026-10-19 02:5x bm-c r1105 splice window", "2026-10-19 05:0x bm-c r1108 splice window", 1, "p1_hdr_stamp")
# receipt wave field (mechanical +1): 273->274
rep('"wave": 273', '"wave": 274', 1, "p1_receipt_wave")
# DATE ROLL: DROPPED this generation (20261019 == 20261019, count-0 face,
# preflight-measured zero 20261018 in canon; disclosed in header)

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W274", "W275", 96, "p2_own_wave")
rep("W273", "W274", 158, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
# relkey = POST-BLANKET form (the upstream blanket rolled the W273 inside
# "W271_W272_W273_bands_respected" -> "W271_W272_W274"; this rep rolls the
# first two positions +1 to the W275 probe receipt's relation keys)
rep("W271_W272_W274_bands_respected", "W272_W273_W274_bands_respected", 2, "p3_relkey")
# legs_sec prose + message (W275 extraction: legs W211..W273 = 63)
rep("W211..W272 legs (62)", "W211..W273 legs (63)", 1, "p3_legs_prose")
rep("W211..W272 sixty-two legs", "W211..W273 sixty-three legs", 1, "p3_legs_msg")
rep("range(211, 273)", "range(211, 274)", 1, "p3_range_legs")
# dropped faces (W275 extraction drops the W274 block's own W248..W273 = 26 legs)
rep("own W248..W272 legs (25)", "own W248..W273 legs (26)", 4, "p3_dropped_narr")
rep("own W248..W272" + CRLF + "# legs (25 rows) do NOT enter the estate path",
    "own W248..W273" + CRLF + "# legs (26 rows) do NOT enter the estate path", 1, "p3_dropped_split_hdr")
rep("W248..W272 twenty-five legs", "W248..W273 twenty-six legs", 1, "p3_dropped_fstring")
rep('N1_BANDS[") == 25', 'N1_BANDS[") == 26', 1, "p3_dropped_count")
# fullspan error-string (POST-BLANKET wave face rolled by the upstream
# blanket: "W211..W273 legs 62" -> "W211..W274 legs 62"; count 62->63)
rep("W211..W274 legs 62", "W211..W274 legs 63", 1, "p3_fullspan_fstring")
# fresh legs (W275 block appends fresh W248..W274 = 27 legs; POST-OWN-BLANKET
# form -- the own blanket rolled the hi face to the new range end 275;
# count-only roll 26->27, hi rides the blanket = range(248, 275) END EXACT)
rep("W248..W275 legs (26", "W248..W275 legs (27", 4, "p3_fresh_narr")
# block/parity counts: W275 block = 69 estate + 37 kept + 27 fresh = 133
rep("block = 132 rows", "block = 133 rows", 1, "p3_block131")
rep("132 parity rows", "133 parity rows", 1, "p3_parity131")
rep("block parity = 132 rows", "block parity = 133 rows", 1, "p3_blockparity131")
rep('N1_BANDS[") == 131,', 'N1_BANDS[") == 132,', 1, "p3_count130")
rep('!= 131', '!= 132', 1, "p3_fstring130")
rep('N1_BANDS[") == 62', 'N1_BANDS[") == 63', 1, "p3_count61")
rep('"fresh_legs_row_asserts": 26', '"fresh_legs_row_asserts": 27', 1, "p3_receipt_fresh")
rep('+ 26,', '+ 27,', 1, "p3_receipt_total")
# ranges (fresh FIRST then dropped-producer, then the cumulative/registry faces)
rep("range(248, 274)", "range(248, 275)", 2, "p3_range_fresh")
rep("range(248, 273)", "range(248, 274)", 1, "p3_range_dropped")
rep("range(16, 274)", "range(16, 275)", 2, "p3_range16")
rep("range(17, 274)", "range(17, 275)", 3, "p3_range17")
rep("range(209, 275)", "range(209, 276)", 2, "p3_range209")
# wave-number gates (own 274->275 FIRST, then anti-gate 273->274)
rep("if w < 274)", "if w < 275)", 5, "p3_wlt274")
rep("if w < 273)", "if w < 274)", 1, "p3_wlt273_antigate")
rep("274 - _lw", "275 - _lw", 2, "p3_legcount")
rep("_w == 273", "_w == 274", 1, "p3_freshmsg_cond")
# cfg/row faces: own 274->275 FIRST, then upstream 273->274
rep("WAVE_CONFIGS[274]", "WAVE_CONFIGS[275]", 2, "p3_wavecfg274_own")
rep("WAVE_CONFIGS[273]", "WAVE_CONFIGS[274]", 3, "p3_wavecfg273")
rep("N1_BANDS[273]", "N1_BANDS[274]", 5, "p3_n1bands273")
rep("get(273)", "get(274)", 1, "p3_get273")
rep("_c273", "_c274", 5, "p3_c273var")
rep('274: {"batch"', '275: {"batch"', 2, "p3_cfg274")
rep('274: {{"batch"', '275: {{"batch"', 1, "p3_cfg274_fstring")
rep('274: {"a"', '275: {"a"', 1, "p3_row274")
rep('274: {{"a"', '275: {{"a"', 2, "p3_row274_fstring")
rep('273: {"batch"', '274: {"batch"', 2, "p3_cfg273")
rep('273: {"a"', '274: {"a"', 3, "p3_row273")
rep("arith_a274", "arith_a275", 6, "p3_arith_a")
rep("arith_b274", "arith_b275", 6, "p3_arith_b")
rep("(270, 269, 268, 267, 266, 265, 264, 263, 262, 261)",
    "(271, 270, 269, 268, 267, 266, 265, 264, 263, 262)", 2, "p3_transitive_list")
rep("W261..W270", "W262..W271", 1, "p3_transitive_window")
# ordinal faces: owner 263->264, bma 130 held, bmc 92->93 (W275 = 265th candidate, bm-c 94th own)
rep("len(owner_rows_live) == 263 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 92",
    "len(owner_rows_live) == 264 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 93", 1, "p3_ordinal_assert")
rep("263/130/92", "264/130/93", 1, "p3_ordinal_expect")
rep("owner_rows=263 / bma_rows=130 / bmc_rows=92",
    "owner_rows=264 / bma_rows=130 / bmc_rows=93", 1, "p3_leg0_face")
rep("rows 263 + candidate = 264th", "rows 264 + candidate = 265th", 2, "p3_owner263")
rep("; bm-c rows 92 +", "; bm-c rows 93 +", 1, "p3_comment_split")
rep("bm-c rows 92 + candidate = 93rd owned", "bm-c rows 93 + candidate = 94th owned", 1, "p3_receipt_owned")
rep("# candidate = 93rd EXACT", "# candidate = 94th EXACT", 1, "p3_comment_93rd")
rep("engine_owner==bm-c rows 92 + candidate", "engine_owner==bm-c rows 93 + candidate", 1, "p3_pr_eo")
rep("bm-c rows {len(bmc_rows_live)} + candidate (93rd own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (94th own wave", 1, "p3_gate05_print")
rep("bm-c's 93rd own wave", "bm-c's 94th own wave", 2, "p3_93rd_own")
rep("NINETY-THIRD owned", "NINETY-FOURTH owned", 3, "p3_93rd_caps")
rep("TWO HUNDRED AND SEVENTY-FOURTH", "TWO HUNDRED AND SEVENTY-FIFTH", 3, "p3_wave_caps")
# 7 raw bmc_rows=92 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=92", "bmc_rows=93", 6, "p3_bmc_rows92")
rep('"probe_receipt_bmc_ordinal_face": 92', '"probe_receipt_bmc_ordinal_face": 93', 1, "p3_probe_face_key")
rep("bmc rows 92 + candidate 93rd", "bmc rows 93 + candidate 94th", 1, "p3_hdr_ordinal")
# ordinal narrative: B-ordinal TWENTY-FOURTH->TWENTY-FIFTH FIRST, then A-ordinal TWENTY-THIRD->TWENTY-FOURTH
rep("TWENTY-FOURTH", "TWENTY-FIFTH", 7, "p3_24_caps")
rep("TWENTY-THIRD", "TWENTY-FOURTH", 15, "p3_23_caps")
rep("twenty-fourth", "twenty-fifth", 4, "p3_24_lc")
rep("twenty-third", "twenty-fourth", 3, "p3_23_lc")
rep("sixty-second", "sixty-third", 2, "p3_62nd")
# wave-number narrative faces
rep("wave 274 engine_owner=bm-c", "wave 275 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 274: "', '"wave 275: "', 1, "p3_cfg_waveface")
rep("wave 274 = first free number", "wave 275 = first free number", 1, "p3_mhdr_waveface")
# cycle/lineage window stamps (SEAT->r1106 / SPLICE+FINALIZE+CLOSEOUT->r1105 /
# PREREG->r1107; contexts measured)
rep("cycle COMPLETE bm-c r1102 closeout 01:0x", "cycle COMPLETE bm-c r1105 closeout 03:2x", 1, "p3_hdr_complete")
rep("bm-c r1102 splice window", "bm-c r1105 splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1102", "own-wave full cycle r1105", 1, "p3_repair_note")
rep("bm-c splice generation r1102 window", "bm-c splice generation r1105 window", 1, "p3_parity_source")
rep("verified r1102", "verified r1105", 1, "p3_lineage_verified")
rep("# r1102 splice window", "# r1105 splice window", 1, "p3_lineage_r")
rep("(bm-c r1102", "(bm-c r1105", 1, "p3_parity_comment")
rep("finalize one-pass bm-c r1102 closeout, ledger", "finalize one-pass bm-c r1105 closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1102 closeout ledger", "finalize one-pass bm-c r1105 closeout ledger", 1, "p3_finpass_hdr")
rep("(r1102 MSG-", "(r1106 MSG-", 1, "p3_hdr_msgline")
rep("r1102 BEFORE this freeze", "r1106 BEFORE this freeze", 1, "p3_receipt_seatnote")
rep("seat itself r1102; queue-head", "seat itself r1106; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1102, queue-head seat-first supply", "(r1106, queue-head seat-first supply", 1, "p3_pfcomment_seat")
# prereg window map (W274 prereg r1104 window -> W275 prereg r1107 window)
rep("bm-c r1104 window", "bm-c r1107 window", 4, "p3_prereg_window")
rep("# r1104 window", "# r1107 window", 1, "p3_hdr_prereg_window")
# not-a-re-pick face
rep("(R273: ", "(R274: ", 1, "p3_repick")
# r1076-family ROOT CURE +1 aging law (NOT the mechanical form)
rep("_set_wave(274)", "_set_wave(275)", 1, "p3_setwave_rootcure")

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
# residual sweep (r1091 law: self-produced faces EXCLUDED -- 620_101/620_300
# fresh refusal-band faces x5/x4, "W275" inside the fresh relkeys, "_w274bmc_"
# lineage-template face, "if w < 274)" anti-gate needle, "range(248, 274)"
# fresh dropped-range assert, n1_w274/w274_ fresh upstream tokens,
# PERPETUAL_N1_W274_PREREG upstream refs)
for gone in ("r1102", "r1104", "01:0x", "02:2x",
             "04f2127db", "70b21a0264",
             "ddc158b5047596ea", "6f31f6e073",
             "MSG-20261019-012x", "_w273bmc_",
             "n1_w273", "w273_", "n1w273-",
             "620_100", "619_900", "618_101", "618_300", "617_901", "618_100",
             "620101", "622100", "620301", "620500",
             "1,024,935", "598,520", "1_024_935", "598_520",
             "W275p", "W274p", "W273p", "W272p",
             "W271_W272_W274_bands_respected",
             "rows 263 + candidate", "bmc_rows=92", "263/130/92",
             "NINETY-THIRD owned", "TWO HUNDRED AND SEVENTY-FOURTH",
             "TWENTY-THIRD", "twenty-third", "sixty-second", "sixty-two legs",
             "wave 274 engine_owner=bm-c", '"wave 274: "', "wave 274 = first free number",
             '"wave": 273',
             "arith_a274", "arith_b274",
             "range(16, 274)", "range(17, 274)", "range(209, 275)",
             "range(248, 273)", "range(211, 273)", "if w < 273)",
             "274 - _lw", "_w == 273",
             "PERPETUAL-N1-W274", "20261018", "2026-10-18"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
  'MSG-20261019-034x-bmc-w275-seat': 7, "bf4bbbde1": 2, "_w275bmc_": 11, "_w274bmc_": 1,
  "20261019": 17, "ec907d164": 1,
  "e4e1ce44f5afd03b": 2, "1fcc0bc30f": 1,
  "622_301": 5, "622_500": 4, "622_300": 9, "622_100": 2,
  "620_301": 8, "620_500": 2, "620_101": 4, "620_300": 6,
  "622301": 1, "624300": 1, "622501": 2, "622700": 2,
  "1,027,135": 6, "600,720": 6, "1_027_135": 1, "600_720": 1,
  "n1_w275": 4, "n1_w274": 4, "n1w275-": 2,
  "n1_w275_results.json": 2, "n1_w274_results.json": 4,
  '275: {"batch"': 2, '274: {"batch"': 2, '273: {"batch"': 0,
  '275: {{"batch"': 1, '275: {"a"': 1, '274: {"a"': 3, '275: {{"a"': 2, '274: {{"a"': 0,
  "range(248, 275)": 2, "range(248, 274)": 1, "range(16, 275)": 2, "range(17, 275)": 3,
  "range(209, 276)": 2, "range(211, 274)": 1, "range(211, 248)": 1, "range(138, 207)": 1,
  "if w < 275)": 5, "if w < 274)": 1, "275 - _lw": 2,
  "m248": 4, "m211": 4, "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
  "WAVE_CONFIGS[275]": 2, "WAVE_CONFIGS[274]": 3, "N1_BANDS[274]": 5,
  "get(274)": 1, "_c274": 5,
  "arith_a275": 6, "arith_b275": 6,
  "(271, 270, 269, 268, 267, 266, 265, 264, 263, 262)": 2, "W262..W271": 1,
  "len(owner_rows_live) == 264": 1, "264/130/93": 1, "bmc_rows=93": 7,
  "rows 264 + candidate = 265th": 2, "bm-c rows 93 + candidate = 94th owned": 1,
  "NINETY-FOURTH owned": 3, "TWO HUNDRED AND SEVENTY-FIFTH": 3,
  "TWENTY-FIFTH": 7, "TWENTY-FOURTH": 15, "twenty-fifth": 4, "twenty-fourth": 3,
  "W272_W273_W274_bands_respected": 2, "W276p": 13, "W276": 26,
  "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
  "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
  "W275 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
  "the bm-c r1105 splice window": 2,
  "bm-c own seat executed at the bm-c r1105 splice window": 1,
  "finalize one-pass bm-c r1105": 2,
  "authored 04:4x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
  "cycle COMPLETE bm-c r1105 closeout 03:2x": 1,
  "verified r1105": 1, "(R274: ": 1, "_w == 274": 1,
  "wave 275 engine_owner=bm-c": 1, '"wave 275: "': 1,
  "wave 275 = first free number": 1, "sixty-third": 2, "sixty-three legs": 1,
  'N1_BANDS[") == 132,': 1, '!= 132': 1, 'N1_BANDS[") == 63': 1,
  'N1_BANDS[") == 37': 1, 'N1_BANDS[") == 26': 1,
  "W211..W273 legs (63)": 1, "W211..W274 legs 63": 1,
  "own W248..W273 legs (26)": 4, "own W248..W273": 5, "W248..W275 legs (27": 4,
  "block = 133 rows": 1, "133 parity rows": 1, "block parity = 133 rows": 1,
  "bm-c r1107 window": 4, "# r1107 window": 1,
  "bm-c splice generation r1105 window": 1, "(bm-c r1105": 1,
  "_w274bmc_freeze_edits.py template": 1,
  "PERPETUAL_N1_W275_PREREG": 8, "PERPETUAL_N1_W274_PREREG": 2, "PERPETUAL-N1-W275": 7,
  "W275 materializer face": 4, "W274 materializer face": 1,
  "W273 finalize product": 0, "W274 finalize product": 4,
  "engine_owner==bm-c rows 93 + candidate": 1, "# candidate = 94th EXACT": 1, "; bm-c rows 93 +": 1,
  "bm-c rows {len(bmc_rows_live)} + candidate (94th own wave": 1,
  "bm-c's 94th own wave": 2, "owner_rows=264 / bma_rows=130 / bmc_rows=93": 1,
  '"probe_receipt_bmc_ordinal_face": 93': 1,
  "fourteen-wave": 8, "post-W274-REGISTERED": 8,
  "anchors W274 1,027,135 / K=600,720 at draft": 1,
  "dual-window parity": 1, "W276 walk": 1,
  "sixty-third consecutive": 2, '"wave": 274': 1,
  "registered wave below 263 composes": 2,
  "PRE-W275-splice": 1, "post-W274 registration": 2,
  "expect 264/130/93": 1,
  "_set_wave(275)": 1, "_set_wave(274)": 0, "_set_wave(273)": 0, "_set_wave(2)": 1,
  "2026-10-19 05:0x bm-c r1108 splice window": 1,
  "derived by the bm-c": 2,
  "bm-c own-seat continuity": 2,
  "physical bytes": 6,
  "own-wave full cycle r1105": 1,
  "r1106 BEFORE this freeze": 1, "seat itself r1106; queue-head": 1,
  "(r1106, queue-head seat-first supply": 1, "(r1106 MSG-": 1,
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
