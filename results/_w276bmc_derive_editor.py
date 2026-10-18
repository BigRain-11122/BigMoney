# -*- coding: utf-8 -*-
# r1111 bm-c splice window: derive results/_w276bmc_freeze_edits.py from the
# committed W275 freeze-edits canon (results/_w275bmc_freeze_edits.py, bm-c
# r1108 splice window 018782314d, proven live-fire: W275 five-face splice +
# engine self-burn 12/12 + finalize one-pass 0bcd555b79 ledger 1,029,335 /
# K=602,920 EXACT, machine-verified by the r1108 closeout c77ee358f5)
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 20th-gen lineage, zero
# transcription: every needle count MEASURED on the canon blob by
# results/_r1111bmc_needle_preflight.py (receipt
# results/_r1111bmc_needle_preflight.json, canon sha256-16 ac3ab907638e191a,
# 62,343B, wt==HEAD==origin triple-verified; post-blanket phase-3 forms
# measured on the phase-1+2 simulated text). r1077 measured-counts law.
# DISCLOSED CANON EOL FACE (benign, carried): core.autocrlf=true re-smudge
# (r1093 pit entry) -- canon read raw with newline='' (CRLF form); multi-line
# needles use the physical CRLF bytes (r775 law).
# W276 FACTS (probe receipt results/_w276bmc_20261019_probe_receipt.json,
# committed with the seat @ 21b51a102 r1109, ADMIT): bands A 622_501..624_500
# (TWENTY-FIFTH consecutive A-hop, staircase-affects-A, hops=1; naive A
# 622_301..624_300 refused at the registered W275 B band 622_301..622_500) /
# B 624_501..624_700 (TWENTY-SIXTH consecutive above-own-A, own-A reservation
# cascade, hops=1; naive B 622_501..622_700 inside the own-A window
# 622_501..624_500); seed_admit FREE x2 (base=622501 span=2000 /
# base=624501 span=200); ordinals owner 265 + candidate = 266th / bm-c rows
# 94 + candidate = 95th; W275 finalize anchors 1,029,335 / K=602,920 (chain
# +2,200/+2,200 EXACT); leg4 W277+ projection naive A 624_501..626_500 /
# naive B 624_701..624_900 (own-A reservation face).
# W276 PREREG: research/PERPETUAL_N1_W276_PREREG.md 23,554B sha256_16
# 5352c7cf343fc5e5 (authored 06:5x bm-c r1110 window via E63 canon-clone
# builder _r1110bmc_build_w276_derive.py; pushed FIRST-TRY to origin
# 770a47fa1f -- NO CAS graft this generation, disclosed).
# AGING-TOKEN LAW (E63 anti-drift, carried): frozen faces w244_a/w244_b /
# n3r1_used245 / m211 / m248 / "w244_a holds wave-263 bands" /
# "registered wave below 263 composes" do NOT roll (measured 12/8/3/4/4/2
# in canon; carried verbatim, anti-drift asserted). Band order law:
# CONSUMERS before PRODUCERS (622_301/622_500 consumed BEFORE 620_101/620_300
# recreate them). Projections first (W277p -> W276p-order mirror: canon
# W276p rolls to W277p before plain W276 -> W277), then D-swaps (own W275 ->
# W276 first, then upstream W274 -> W275). Ordinal caps: B
# (TWENTY-FIFTH -> TWENTY-SIXTH) before A (TWENTY-FOURTH -> TWENTY-FIFTH).
# lc blankets: own w275_ (10, after n1_w275_results.json x2 + builder x1
# carve-outs) before upstream w274_ (89, after n1_w274_results.json x4
# carve-outs).
# SETWAVE +1 AGING LAW (r1076-family root cure, carried): _set_wave(275) ->
# _set_wave(276); presence gates 276:1 / 275:0 / 274:0.
# DATE-ROLL FACE (count 0 this generation, DISCLOSED): canon receipts already
# dated 20261019 and the W276 seat/probe receipts are same-date -- the W275
# editor's p1_date_roll rep is DROPPED this generation (zero 20261018 faces
# in canon, preflight-measured); the "20261019" x17 gate carries verbatim.
# Window-stamp disambiguation (measured): SEAT faces -> r1109 (W276 seat
# 21b51a102); SPLICE/FINALIZE/CLOSEOUT faces -> r1108 (W275 splice
# 018782314d + finalize 0bcd555b79 + closeout c77ee358f5 05:35);
# PREREG faces -> r1110 (W276 prereg 770a47fa1f); THIS splice window -> r1111.
import io, subprocess, sys

CANON = "results/_w275bmc_freeze_edits.py"
DST = "results/_w276bmc_freeze_edits.py"
LOG = "results/_r1111bmc_derive_editor_log.txt"
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
       f"(preflight-measured sha256_16 ac3ab907638e191a, 62,343B)",
       f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:110]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W276p", "W277p", 13, "p1_proj_prefix")
rep("W276", "W277", 13, "p1_proj_plain")
# bands (CONSUMERS FIRST: 622_301/622_500 consumed before 620_101/620_300
# recreate them -- band-order law; all 8 rep targets measured 5/4/9/2/8/2/4/6)
rep("622_301", "624_501", 5, "p1_band_Blo")
rep("622_500", "624_700", 4, "p1_band_Bhi")
rep("622_300", "624_500", 9, "p1_band_Ahi")
rep("622_100", "624_300", 2, "p1_band_naiveAhi")
rep("620_301", "622_501", 8, "p1_band_Alo_Bnaivelo")
rep("620_500", "622_700", 2, "p1_band_Bnaivehi")
rep("620_101", "622_301", 4, "p1_band_naiveAlo_priorBlo")
rep("620_300", "622_500", 6, "p1_band_priorBhi")
# int-form leg4 projections in the receipt downstream_seat note (probe-measured)
rep("622301", "624501", 1, "p1_int_projAlo")
rep("624300", "626500", 1, "p1_int_projAhi")
rep("622501", "624701", 2, "p1_int_projBlo")
rep("622700", "624900", 2, "p1_int_projBhi")
# ledger/K anchors: W274 finalize facts -> W275 finalize facts (1,029,335/602,920)
rep("1,027,135", "1,029,335", 6, "p1_ledger_prose")
rep("600,720", "602,920", 6, "p1_k_prose")
rep("1_027_135", "1_029_335", 1, "p1_ledger_code")
rep("600_720", "602_920", 1, "p1_k_code")
# builder filename FIRST (consumes its embedded w275_ before the lc blanket)
rep("(E63 canon-clone builder _r1107bmc_build_w275_derive.py)",
    "(E63 canon-clone builder _r1110bmc_build_w276_derive.py)", 1, "p1_builder_method")
# lowercase machine-file tokens (own first, then upstream; the w275_ blanket
# ALSO rolls the current-wave pickaxe vars w275_prereg_sha/w275_receipt_sha ->
# w276_* AFTER the n1_w275_results.json x2 + builder x1 carve-outs; the
# w274_ blanket rolls ALL upstream w274_* variables -> w275_* after the
# n1_w274_results.json x4 carve-out)
rep("n1_w275", "n1_w276", 4, "p1_n1w275_own")
rep("n1w275-", "n1w276-", 2, "p1_n1w275dash")
rep("w275_", "w276_", 10, "p1_lc_w275_")
rep("n1_w274", "n1_w275", 4, "p1_n1w274_upstream")
rep("w274_", "w275_", 89, "p1_lc_w274_")
# receipt/lineage/seat faces
rep("_w275bmc_", "_w276bmc_", 11, "p1_receiptpath")
rep("_w274bmc_freeze_edits.py template", "_w275bmc_freeze_edits.py template", 1, "p1_lineage_template")
rep("MSG-20261019-034x-bmc-w275-seat", "MSG-20261019-055x-bmc-w276-seat", 7, "p1_seat_msg")
rep('SEAT_ORIGIN = "bf4bbbde1"', 'SEAT_ORIGIN = "21b51a102"', 1, "p1_seat_origin_const")
rep("bf4bbbde1 r1106", "21b51a102 r1109", 1, "p1_seat_origin_hdr")
rep("ec907d164", "018782314d", 1, "p1_lineage_sha")
# prereg delivery prose (r1110 first-try push + E63 builder method)
rep("(authored 04:4x, banned_direction_gate ADMIT rc0, frozen sha16 e4e1ce44f5afd03b + pushed-" + CRLF +
    "# first-try to origin 1fcc0bc30f, r1107 window).",
    "(authored 06:5x, banned_direction_gate ADMIT rc0, frozen sha16 5352c7cf343fc5e5 + pushed-" + CRLF +
    "# first-try to origin 770a47fa1f, r1110 window).",
    1, "p1_prereg_delivery_hdr")
rep("(authored 04:4x, banned gate ADMIT rc0, frozen e4e1ce44f5afd03b -> pushed first-try r1107 origin ",
    "(authored 06:5x, banned gate ADMIT rc0, frozen 5352c7cf343fc5e5 -> pushed first-try r1110 origin ",
    1, "p1_prereg_delivery_note")
# header window stamp
rep("2026-10-19 05:0x bm-c r1108 splice window", "2026-10-19 07:1x bm-c r1111 splice window", 1, "p1_hdr_stamp")
# receipt wave field (mechanical +1): 274->275
rep('"wave": 274', '"wave": 275', 1, "p1_receipt_wave")
# DATE ROLL: DROPPED this generation (20261019 == 20261019, count-0 face,
# preflight-measured zero 20261018 in canon; disclosed in header)

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W275", "W276", 96, "p2_own_wave")
rep("W274", "W275", 158, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
# relkey = POST-BLANKET form (the upstream blanket rolled the W274 inside
# "W272_W273_W274_bands_respected" -> "W272_W273_W275"; this rep rolls the
# first two positions +1 to the W276 probe receipt's relation keys)
rep("W272_W273_W275_bands_respected", "W273_W274_W275_bands_respected", 2, "p3_relkey")
# legs_sec prose + message (W276 extraction: legs W211..W274 = 64)
rep("W211..W273 legs (63)", "W211..W274 legs (64)", 1, "p3_legs_prose")
rep("W211..W273 sixty-three legs", "W211..W274 sixty-four legs", 1, "p3_legs_msg")
rep("range(211, 274)", "range(211, 275)", 1, "p3_range_legs")
# dropped faces (W276 extraction drops the W275 block's own W248..W274 = 27 legs)
rep("own W248..W273 legs (26)", "own W248..W274 legs (27)", 4, "p3_dropped_narr")
rep("own W248..W273" + CRLF + "# legs (26 rows) do NOT enter the estate path",
    "own W248..W274" + CRLF + "# legs (27 rows) do NOT enter the estate path", 1, "p3_dropped_split_hdr")
rep("W248..W273 twenty-six legs", "W248..W274 twenty-seven legs", 1, "p3_dropped_fstring")
rep('N1_BANDS[") == 26', 'N1_BANDS[") == 27', 1, "p3_dropped_count")
# fullspan error-string (POST-BLANKET wave face rolled by the upstream
# blanket: "W211..W274 legs 63" -> "W211..W275 legs 63"; count 63->64)
rep("W211..W275 legs 63", "W211..W275 legs 64", 1, "p3_fullspan_fstring")
# fresh legs (W276 block appends fresh W248..W275 = 28 legs; POST-OWN-BLANKET
# form -- the own blanket rolled the hi face to the new range end 276;
# count-only roll 27->28, hi rides the blanket = range(248, 276) END EXACT)
rep("W248..W276 legs (27", "W248..W276 legs (28", 4, "p3_fresh_narr")
# block/parity counts: W276 block = 70 estate + 37 kept + 28 fresh = 134
rep("block = 133 rows", "block = 134 rows", 1, "p3_block131")
rep("133 parity rows", "134 parity rows", 1, "p3_parity131")
rep("block parity = 133 rows", "block parity = 134 rows", 1, "p3_blockparity131")
rep('N1_BANDS[") == 132,', 'N1_BANDS[") == 133,', 1, "p3_count130")
rep('!= 132', '!= 133', 1, "p3_fstring130")
rep('N1_BANDS[") == 63', 'N1_BANDS[") == 64', 1, "p3_count61")
rep('"fresh_legs_row_asserts": 27', '"fresh_legs_row_asserts": 28', 1, "p3_receipt_fresh")
rep('+ 27,', '+ 28,', 1, "p3_receipt_total")
# ranges (fresh FIRST then dropped-producer, then the cumulative/registry faces)
rep("range(248, 275)", "range(248, 276)", 2, "p3_range_fresh")
rep("range(248, 274)", "range(248, 275)", 1, "p3_range_dropped")
rep("range(16, 275)", "range(16, 276)", 2, "p3_range16")
rep("range(17, 275)", "range(17, 276)", 3, "p3_range17")
rep("range(209, 276)", "range(209, 277)", 2, "p3_range209")
# wave-number gates (own 275->276 FIRST, then anti-gate 274->275)
rep("if w < 275)", "if w < 276)", 5, "p3_wlt275")
rep("if w < 274)", "if w < 275)", 1, "p3_wlt274_antigate")
rep("275 - _lw", "276 - _lw", 2, "p3_legcount")
rep("_w == 274", "_w == 275", 1, "p3_freshmsg_cond")
# cfg/row faces: own 275->276 FIRST, then upstream 274->275
rep("WAVE_CONFIGS[275]", "WAVE_CONFIGS[276]", 2, "p3_wavecfg275_own")
rep("WAVE_CONFIGS[274]", "WAVE_CONFIGS[275]", 3, "p3_wavecfg274")
rep("N1_BANDS[274]", "N1_BANDS[275]", 5, "p3_n1bands274")
rep("get(274)", "get(275)", 1, "p3_get274")
rep("_c274", "_c275", 5, "p3_c274var")
rep('275: {"batch"', '276: {"batch"', 2, "p3_cfg275")
rep('275: {{"batch"', '276: {{"batch"', 1, "p3_cfg275_fstring")
rep('275: {"a"', '276: {"a"', 1, "p3_row275")
rep('275: {{"a"', '276: {{"a"', 2, "p3_row275_fstring")
rep('274: {"batch"', '275: {"batch"', 2, "p3_cfg274")
rep('274: {"a"', '275: {"a"', 3, "p3_row274")
rep("arith_a275", "arith_a276", 6, "p3_arith_a")
rep("arith_b275", "arith_b276", 6, "p3_arith_b")
rep("(271, 270, 269, 268, 267, 266, 265, 264, 263, 262)",
    "(272, 271, 270, 269, 268, 267, 266, 265, 264, 263)", 2, "p3_transitive_list")
rep("W262..W271", "W263..W272", 1, "p3_transitive_window")
# ordinal faces: owner 264->265, bma 130 held, bmc 93->94 (W276 = 266th candidate, bm-c 95th own)
rep("len(owner_rows_live) == 264 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 93",
    "len(owner_rows_live) == 265 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 94", 1, "p3_ordinal_assert")
rep("264/130/93", "265/130/94", 1, "p3_ordinal_expect")
rep("owner_rows=264 / bma_rows=130 / bmc_rows=93",
    "owner_rows=265 / bma_rows=130 / bmc_rows=94", 1, "p3_leg0_face")
rep("rows 264 + candidate = 265th", "rows 265 + candidate = 266th", 2, "p3_owner264")
rep("; bm-c rows 93 +", "; bm-c rows 94 +", 1, "p3_comment_split")
rep("bm-c rows 93 + candidate = 94th owned", "bm-c rows 94 + candidate = 95th owned", 1, "p3_receipt_owned")
rep("# candidate = 94th EXACT", "# candidate = 95th EXACT", 1, "p3_comment_94th")
rep("engine_owner==bm-c rows 93 + candidate", "engine_owner==bm-c rows 94 + candidate", 1, "p3_pr_eo")
rep("bm-c rows {len(bmc_rows_live)} + candidate (94th own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (95th own wave", 1, "p3_gate05_print")
rep("bm-c's 94th own wave", "bm-c's 95th own wave", 2, "p3_94th_own")
rep("NINETY-FOURTH owned", "NINETY-FIFTH owned", 3, "p3_94th_caps")
rep("TWO HUNDRED AND SEVENTY-FIFTH", "TWO HUNDRED AND SEVENTY-SIXTH", 3, "p3_wave_caps")
# 7 raw bmc_rows=93 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=93", "bmc_rows=94", 6, "p3_bmc_rows93")
rep('"probe_receipt_bmc_ordinal_face": 93', '"probe_receipt_bmc_ordinal_face": 94', 1, "p3_probe_face_key")
rep("bmc rows 93 + candidate 94th", "bmc rows 94 + candidate 95th", 1, "p3_hdr_ordinal")
# ordinal narrative: B-ordinal TWENTY-FIFTH->TWENTY-SIXTH FIRST, then A-ordinal TWENTY-FOURTH->TWENTY-FIFTH
rep("TWENTY-FIFTH", "TWENTY-SIXTH", 7, "p3_25_caps")
rep("TWENTY-FOURTH", "TWENTY-FIFTH", 15, "p3_24_caps")
rep("twenty-fifth", "twenty-sixth", 4, "p3_25_lc")
rep("twenty-fourth", "twenty-fifth", 3, "p3_24_lc")
rep("sixty-third", "sixty-fourth", 2, "p3_63rd")
# wave-number narrative faces
rep("wave 275 engine_owner=bm-c", "wave 276 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 275: "', '"wave 276: "', 1, "p3_cfg_waveface")
rep("wave 275 = first free number", "wave 276 = first free number", 1, "p3_mhdr_waveface")
# cycle/lineage window stamps (SEAT->r1109 / SPLICE+FINALIZE+CLOSEOUT->r1108 /
# PREREG->r1110; contexts measured)
rep("cycle COMPLETE bm-c r1105 closeout 03:2x", "cycle COMPLETE bm-c r1108 closeout 05:3x", 1, "p3_hdr_complete")
rep("bm-c r1105 splice window", "bm-c r1108 splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1105", "own-wave full cycle r1108", 1, "p3_repair_note")
rep("bm-c splice generation r1105 window", "bm-c splice generation r1108 window", 1, "p3_parity_source")
rep("verified r1105", "verified r1108", 1, "p3_lineage_verified")
rep("# r1105 splice window", "# r1108 splice window", 1, "p3_lineage_r")
rep("(bm-c r1105", "(bm-c r1108", 1, "p3_parity_comment")
rep("finalize one-pass bm-c r1105 closeout, ledger", "finalize one-pass bm-c r1108 closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1105 closeout ledger", "finalize one-pass bm-c r1108 closeout ledger", 1, "p3_finpass_hdr")
rep("(r1106 MSG-", "(r1109 MSG-", 1, "p3_hdr_msgline")
rep("r1106 BEFORE this freeze", "r1109 BEFORE this freeze", 1, "p3_receipt_seatnote")
rep("seat itself r1106; queue-head", "seat itself r1109; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1106, queue-head seat-first supply", "(r1109, queue-head seat-first supply", 1, "p3_pfcomment_seat")
# prereg window map (W275 prereg r1107 window -> W276 prereg r1110 window)
rep("bm-c r1107 window", "bm-c r1110 window", 4, "p3_prereg_window")
rep("# r1107 window", "# r1110 window", 1, "p3_hdr_prereg_window")
# not-a-re-pick face
rep("(R274: ", "(R275: ", 1, "p3_repick")
# r1076-family ROOT CURE +1 aging law (NOT the mechanical form)
rep("_set_wave(275)", "_set_wave(276)", 1, "p3_setwave_rootcure")

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
# residual sweep (r1091 law: self-produced faces EXCLUDED -- 622_301/622_500
# fresh refusal-band faces x5/x4, "W276" inside the fresh relkeys, "_w275bmc_"
# lineage-template face, "if w < 275)" anti-gate needle, "range(248, 275)"
# fresh dropped-range assert, n1_w275/w275_ fresh upstream tokens,
# PERPETUAL_N1_W275_PREREG upstream refs)
for gone in ("r1105", "r1106", "r1107", "03:2x", "04:4x", "05:0x",
             "bf4bbbde1", "ec907d164",
             "e4e1ce44f5afd03b", "1fcc0bc30f",
             "MSG-20261019-034x", "_w274bmc_",
             "n1_w274", "w274_", "n1w275-",
             "622_300", "622_100", "620_301", "620_500",
             "622301", "624300", "622501", "622700",
             "1,027,135", "600,720", "1_027_135", "600_720",
             "W276p", "W275p", "W274p", "W273p", "W272p",
             "W272_W273_W275_bands_respected",
             "rows 264 + candidate", "bmc_rows=93", "264/130/93",
             "NINETY-FOURTH owned", "TWO HUNDRED AND SEVENTY-FIFTH",
             "TWENTY-FOURTH", "twenty-fourth", "sixty-third", "sixty-three legs",
             "wave 275 engine_owner=bm-c", '"wave 275: "', "wave 275 = first free number",
             '"wave": 274',
             "arith_a275", "arith_b275",
             "range(16, 275)", "range(17, 275)", "range(209, 276)",
             "range(248, 274)", "range(211, 274)", "if w < 274)",
             "275 - _lw", "_w == 274",
             "PERPETUAL-N1-W275", "20261018", "2026-10-18"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
  'MSG-20261019-055x-bmc-w276-seat': 7, "21b51a102": 2, "_w276bmc_": 11, "_w275bmc_": 1,
  "20261019": 17, "018782314d": 1,
  "5352c7cf343fc5e5": 2, "770a47fa1f": 1,
  "624_501": 5, "624_700": 4, "624_500": 9, "624_300": 2,
  "622_501": 8, "622_700": 2, "622_301": 4, "622_500": 6,
  "624501": 1, "626500": 1, "624701": 2, "624900": 2,
  "1,029,335": 6, "602,920": 6, "1_029_335": 1, "602_920": 1,
  "n1_w276": 4, "n1_w275": 4, "n1w276-": 2,
  "n1_w276_results.json": 2, "n1_w275_results.json": 4,
  '276: {"batch"': 2, '275: {"batch"': 2, '274: {"batch"': 0,
  '276: {{"batch"': 1, '276: {"a"': 1, '275: {"a"': 3, '276: {{"a"': 2, '275: {{"a"': 0,
  "range(248, 276)": 2, "range(248, 275)": 1, "range(16, 276)": 2, "range(17, 276)": 3,
  "range(209, 277)": 2, "range(211, 275)": 1, "range(211, 248)": 1, "range(138, 207)": 1,
  "if w < 276)": 5, "if w < 275)": 1, "276 - _lw": 2,
  "m248": 4, "m211": 4, "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
  "WAVE_CONFIGS[276]": 2, "WAVE_CONFIGS[275]": 3, "N1_BANDS[275]": 5,
  "get(275)": 1, "_c275": 5,
  "arith_a276": 6, "arith_b276": 6,
  "(272, 271, 270, 269, 268, 267, 266, 265, 264, 263)": 2, "W263..W272": 1,
  "len(owner_rows_live) == 265": 1, "265/130/94": 1, "bmc_rows=94": 7,
  "rows 265 + candidate = 266th": 2, "bm-c rows 94 + candidate = 95th owned": 1,
  "NINETY-FIFTH owned": 3, "TWO HUNDRED AND SEVENTY-SIXTH": 3,
  "TWENTY-SIXTH": 7, "TWENTY-FIFTH": 15, "twenty-sixth": 4, "twenty-fifth": 3,
  "W273_W274_W275_bands_respected": 2, "W277p": 13, "W277": 26,
  "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
  "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
  "W276 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
  "the bm-c r1108 splice window": 2,
  "bm-c own seat executed at the bm-c r1108 splice window": 1,
  "finalize one-pass bm-c r1108": 2,
  "authored 06:5x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
  "cycle COMPLETE bm-c r1108 closeout 05:3x": 1,
  "verified r1108": 1, "(R275: ": 1, "_w == 275": 1,
  "wave 276 engine_owner=bm-c": 1, '"wave 276: "': 1,
  "wave 276 = first free number": 1, "sixty-fourth": 2, "sixty-four legs": 1,
  'N1_BANDS[") == 133,': 1, '!= 133': 1, 'N1_BANDS[") == 64': 1,
  'N1_BANDS[") == 37': 1, 'N1_BANDS[") == 27': 1,
  "W211..W274 legs (64)": 1, "W211..W275 legs 64": 1,
  "own W248..W274 legs (27)": 4, "own W248..W274": 5, "W248..W276 legs (28": 4,
  "block = 134 rows": 1, "134 parity rows": 1, "block parity = 134 rows": 1,
  "bm-c r1110 window": 4, "# r1110 window": 1,
  "bm-c splice generation r1108 window": 1, "(bm-c r1108": 1,
  "_w275bmc_freeze_edits.py template": 1,
  "PERPETUAL_N1_W276_PREREG": 8, "PERPETUAL_N1_W275_PREREG": 2, "PERPETUAL-N1-W276": 7,
  "W276 materializer face": 4, "W275 materializer face": 1,
  "W274 finalize product": 0, "W275 finalize product": 4,
  "engine_owner==bm-c rows 94 + candidate": 1, "# candidate = 95th EXACT": 1, "; bm-c rows 94 +": 1,
  "bm-c rows {len(bmc_rows_live)} + candidate (95th own wave": 1,
  "bm-c's 95th own wave": 2, "owner_rows=265 / bma_rows=130 / bmc_rows=94": 1,
  '"probe_receipt_bmc_ordinal_face": 94': 1,
  "fourteen-wave": 8, "post-W275-REGISTERED": 8,
  "anchors W275 1,029,335 / K=602,920 at draft": 1,
  "dual-window parity": 1, "W277 walk": 1,
  "sixty-fourth consecutive": 2, '"wave": 275': 1,
  "registered wave below 263 composes": 2,
  "PRE-W276-splice": 1, "post-W275 registration": 2,
  "expect 265/130/94": 1,
  "_set_wave(276)": 1, "_set_wave(275)": 0, "_set_wave(274)": 0, "_set_wave(2)": 1,
  "2026-10-19 07:1x bm-c r1111 splice window": 1,
  "derived by the bm-c": 2,
  "bm-c own-seat continuity": 2,
  "physical bytes": 6,
  "own-wave full cycle r1108": 1,
  "r1109 BEFORE this freeze": 1, "seat itself r1109; queue-head": 1,
  "(r1109, queue-head seat-first supply": 1, "(r1109 MSG-": 1,
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
