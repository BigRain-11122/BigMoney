# -*- coding: utf-8 -*-
# r1123 bm-c splice window: derive results/_w279bmc_freeze_edits.py from the
# committed W278 freeze-edits canon (results/_w278bmc_freeze_edits.py, bm-c
# r1118 splice window b6f486af35, proven live-fire: W278 five-face splice +
# engine self-burn 12/12 + finalize one-pass ledger 1,035,935 / K=609,520
# EXACT, machine-verified by the r1119 closeout 0a92fcc28f)
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 23rd-gen lineage, zero
# transcription: every needle count MEASURED on the canon blob by
# results/_r1123bmc_needle_preflight.py (receipt
# results/_r1123bmc_needle_preflight.json, canon sha256-16 362636ece2e1fbe5,
# 62,582B, wt==HEAD==origin triple-verified; sim + post-blanket phase-3 forms
# measured; FIRST-RUN ONE preflight-table heal: 'push-race-' x2 = BOTH
# delivery prose forms [hdr CRLF-split + note compound], expected 1, measured
# governs). r1077 measured-counts law.
# DISCLOSED CANON EOL FACE (benign, carried): core.autocrlf=true re-smudge
# (r1093 pit entry) -- canon read raw with newline='' (CRLF form); multi-line
# needles use the physical CRLF bytes (r775 law).
# W279 FACTS (probe receipt results/_w279bmc_20261019_probe_receipt.json,
# committed with the seat @ 900c23fe7d r1119, ADMIT): bands A
# 629_101..631_100 (TWENTY-EIGHTH consecutive A-hop, staircase-affects-A,
# hops=1; naive A 628_901..630_900 refused at the registered W278 B band
# 628_901..629_100) / B 631_101..631_300 (TWENTY-NINTH consecutive
# above-own-A, own-A reservation cascade, hops=1; naive B 629_101..629_300
# lands inside the own-A window 629_101..631_100); seed_admit FREE x2 (base=
# 629101 span=2000 / base=631101 span=200); ordinals owner 268 + candidate =
# 269th / bm-c rows 97 + candidate = 98th; W278 finalize anchors 1,035,935 /
# K=609,520 (chain +2,200/+2,200 EXACT); leg4 W280p projections naive A
# 631_101..633_100 / naive B 631_301..631_500 (pre-W279 universe; hops 0/0;
# W280p_B_lands_inside_W280p_A_naive staircase face continuing since W251
# per the frozen W279 prereg sec.5 item5).
# W279 PREREG: research/PERPETUAL_N1_W279_PREREG.md 23,681B sha256_16
# c2fc7c34d0e41a68 (authored 18:5x bm-c r1122 window via E63 canon-clone
# builder _r1122bmc_build_w279_derive.py; frozen + pushed first-try-post-
# rebase landed to origin ba5c725b42, r1122 window).
# AGING-TOKEN LAW (E63 anti-drift, carried): frozen faces w244_a/w244_b /
# n3r1_used245 / m211 / m248 / "w244_a holds wave-263 bands" /
# "registered wave below 263 composes" do NOT roll (measured 12/8/3/4/4/2
# in canon; carried verbatim, anti-drift asserted). Band order law:
# CONSUMERS before PRODUCERS (628_901/629_100 consumed BEFORE 626_701/626_900
# recreate them). Projections first (W280p -> rolled before plain W279 ->
# W280), then D-swaps (own W278 -> W279 first, then upstream W277 -> W278).
# Ordinal caps: B (TWENTY-EIGHTH -> TWENTY-NINTH) before A
# (TWENTY-SEVENTH -> TWENTY-EIGHTH). lc blankets: own w278_ (10, after
# n1_w278_results.json x2 + builder x1 carve-outs) before upstream w277_
# (89, after n1_w277_results.json x4 carve-outs).
# SETWAVE +1 AGING LAW (r1076-family root cure, carried): _set_wave(278) ->
# _set_wave(279); presence gates 279:1 / 278:0 / 277:0.
# DATE-ROLL FACE (count 0 this generation, DISCLOSED): canon receipts already
# dated 20261019 and the W279 seat/probe/prereg receipts are same-date -- no
# date-roll rep this generation (zero 20261018 faces in canon,
# preflight-measured); the "20261019" x17 gate carries verbatim.
# Window-stamp disambiguation (measured): SEAT faces -> r1119 (W279 seat
# 900c23fe7d 15:0x); SPLICE/FINALIZE/CYCLE-COMPLETE faces -> r1118/r1119
# (W278 splice b6f486af35 13:5x + finalize one-pass + cycle-complete closeout
# 0a92fcc28f 15:1x -- the whole W278 chain is labeled r1118/r1119 per the
# frozen W279 prereg usage); PREREG faces -> r1122 (W279 prereg ba5c725b42);
# THIS splice window -> r1123.
import io, subprocess, sys

CANON = "results/_w278bmc_freeze_edits.py"
DST = "results/_w279bmc_freeze_edits.py"
LOG = "results/_r1123bmc_derive_editor_log.txt"
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
       f"(preflight-measured sha256-16 362636ece2e1fbe5, 62,582B)",
       f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:110]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W279p", "W280p", 13, "p1_proj_prefix")
rep("W279", "W280", 13, "p1_proj_plain")
# bands (CONSUMERS FIRST: 628_901/629_100 consumed before 626_701/626_900
# recreate them -- band-order law; all 8 rep targets measured 5/4/9/2/8/2/4/6)
rep("628_901", "631_101", 5, "p1_band_Blo")
rep("629_100", "631_300", 4, "p1_band_Bhi")
rep("628_900", "631_100", 9, "p1_band_Ahi")
rep("628_700", "630_900", 2, "p1_band_naiveAhi")
rep("626_901", "629_101", 8, "p1_band_Alo_Bnaivelo")
rep("627_100", "629_300", 2, "p1_band_Bnaivehi")
rep("626_701", "628_901", 4, "p1_band_naiveAlo_priorBlo")
rep("626_900", "629_100", 6, "p1_band_priorBhi")
# int-form leg4 projections in the receipt downstream_seat note (probe-measured)
rep("628901", "631101", 1, "p1_int_projAlo")
rep("630900", "633100", 1, "p1_int_projAhi")
rep("629101", "631301", 2, "p1_int_projBlo")
rep("629300", "631500", 2, "p1_int_projBhi")
# ledger/K anchors: W277 finalize facts -> W278 finalize facts (1,035,935/609,520)
rep("1,033,735", "1,035,935", 6, "p1_ledger_prose")
rep("607,320", "609,520", 6, "p1_k_prose")
rep("1_033_735", "1_035_935", 1, "p1_ledger_code")
rep("607_320", "609_520", 1, "p1_k_code")
# builder filename FIRST (consumes its embedded w278_ before the lc blanket)
rep("(E63 canon-clone builder _r1116bmc_build_w278_derive.py)",
    "(E63 canon-clone builder _r1122bmc_build_w279_derive.py)", 1, "p1_builder_method")
# lowercase machine-file tokens (own first, then upstream; the w278_ blanket
# ALSO rolls the current-wave pickaxe vars w278_prereg_sha/w278_receipt_sha ->
# w279_* AFTER the n1_w278_results.json x2 + builder x1 carve-outs; the
# w277_ blanket rolls ALL upstream w277_* variables -> w278_* after the
# n1_w277_results.json x4 carve-out)
rep("n1_w278", "n1_w279", 4, "p1_n1w278_own")
rep("n1w278-", "n1w279-", 2, "p1_n1w278dash")
rep("w278_", "w279_", 10, "p1_lc_w278_")
rep("n1_w277", "n1_w278", 4, "p1_n1w277_upstream")
rep("w277_", "w278_", 89, "p1_lc_w277_")
# receipt/lineage/seat faces
rep("_w278bmc_", "_w279bmc_", 11, "p1_receiptpath")
rep("_w277bmc_freeze_edits.py template", "_w278bmc_freeze_edits.py template", 1, "p1_lineage_template")
rep("MSG-20261019-102x-bmc-w278-seat", "MSG-20261019-145x-bmc-w279-seat", 7, "p1_seat_msg")
rep('SEAT_ORIGIN = "b187aa6214"', 'SEAT_ORIGIN = "900c23fe7d"', 1, "p1_seat_origin_const")
rep("b187aa6214 r1114-continuation", "900c23fe7d r1119", 1, "p1_seat_origin_hdr")
rep("9e53371814", "b6f486af35", 1, "p1_lineage_sha")
# prereg delivery prose (r1122 first-try-post-rebase landing + E63 builder
# method; CRLF-joined needle per the preflight verbatim extraction)
rep("(authored 12:2x, banned_direction_gate ADMIT rc0, frozen sha16 99001d3d3f337942 + push-race-" + CRLF +
    "# healed landed to origin df1aaba72a, r1116 window).",
    "(authored 18:5x, banned_direction_gate ADMIT rc0, frozen sha16 c2fc7c34d0e41a68 + pushed first-try-post-" + CRLF +
    "# rebase landed to origin ba5c725b42, r1122 window).",
    1, "p1_prereg_delivery_hdr")
rep("(authored 12:2x, banned gate ADMIT rc0, frozen 99001d3d3f337942 -> push-race-healed r1116 origin ",
    "(authored 18:5x, banned gate ADMIT rc0, frozen c2fc7c34d0e41a68 -> pushed-first-try-post-rebase r1122 origin ",
    1, "p1_prereg_delivery_note")
# header window stamp
rep("2026-10-19 13:3x bm-c r1118 splice window", "2026-10-19 19:2x bm-c r1123 splice window", 1, "p1_hdr_stamp")
# receipt wave field (mechanical +1): 277->278
rep('"wave": 277', '"wave": 278', 1, "p1_receipt_wave")
# DATE ROLL: DROPPED this generation (20261019 == 20261019, count-0 face,
# preflight-measured zero 20261018 in canon; disclosed in header)

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W278", "W279", 96, "p2_own_wave")
rep("W277", "W278", 158, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
# relkey = POST-BLANKET form (the upstream blanket rolled the W277 inside
# "W275_W276_W277_bands_respected" -> "W275_W276_W278"; this rep rolls the
# first two positions +1 to the W279 probe receipt's relation keys)
rep("W275_W276_W278_bands_respected", "W276_W277_W278_bands_respected", 2, "p3_relkey")
# legs_sec prose + message (W279 extraction: legs W211..W277 = 67)
rep("W211..W276 legs (66)", "W211..W277 legs (67)", 1, "p3_legs_prose")
rep("W211..W276 sixty-six legs", "W211..W277 sixty-seven legs", 1, "p3_legs_msg")
rep("range(211, 277)", "range(211, 278)", 1, "p3_range_legs")
# dropped faces (W279 extraction drops the W278 block's own W248..W277 = 30 legs)
rep("own W248..W276 legs (29)", "own W248..W277 legs (30)", 4, "p3_dropped_narr")
rep("own W248..W276" + CRLF + "# legs (29 rows) do NOT enter the estate path",
    "own W248..W277" + CRLF + "# legs (30 rows) do NOT enter the estate path", 1, "p3_dropped_split_hdr")
rep("W248..W276 twenty-nine legs", "W248..W277 thirty legs", 1, "p3_dropped_fstring")
rep('N1_BANDS[") == 29', 'N1_BANDS[") == 30', 1, "p3_dropped_count")
# fullspan error-string (POST-BLANKET wave face rolled by the upstream
# blanket: "W211..W277 legs 66" -> "W211..W278 legs 66"; count 66->67)
rep("W211..W278 legs 66", "W211..W278 legs 67", 1, "p3_fullspan_fstring")
# fresh legs (W279 block appends fresh W248..W278 = 31 legs; POST-OWN-BLANKET
# form -- the own blanket rolled the hi face to the new range end 279;
# count-only roll 30->31, hi rides the blanket = range(248, 279) END EXACT)
rep("W248..W279 legs (30", "W248..W279 legs (31", 4, "p3_fresh_narr")
# block/parity counts: W279 block = 70 estate + 37 kept + 31 fresh = 138
rep("block = 136 rows", "block = 137 rows", 1, "p3_block131")
rep("136 parity rows", "137 parity rows", 1, "p3_parity131")
rep("block parity = 136 rows", "block parity = 137 rows", 1, "p3_blockparity131")
rep('N1_BANDS[") == 135,', 'N1_BANDS[") == 136,', 1, "p3_count130")
rep('!= 135', '!= 136', 1, "p3_fstring130")
rep('N1_BANDS[") == 66', 'N1_BANDS[") == 67', 1, "p3_count61")
rep('"fresh_legs_row_asserts": 30', '"fresh_legs_row_asserts": 31', 1, "p3_receipt_fresh")
rep('+ 30,', '+ 31,', 1, "p3_receipt_total")
# ranges (fresh FIRST then dropped-producer, then the cumulative/registry faces)
rep("range(248, 278)", "range(248, 279)", 2, "p3_range_fresh")
rep("range(248, 277)", "range(248, 278)", 1, "p3_range_dropped")
rep("range(16, 278)", "range(16, 279)", 2, "p3_range16")
rep("range(17, 278)", "range(17, 279)", 3, "p3_range17")
rep("range(209, 279)", "range(209, 280)", 2, "p3_range209")
# wave-number gates (own 278->279 FIRST, then anti-gate 277->278)
rep("if w < 278)", "if w < 279)", 5, "p3_wlt278")
rep("if w < 277)", "if w < 278)", 1, "p3_wlt277_antigate")
rep("278 - _lw", "279 - _lw", 2, "p3_legcount")
rep("_w == 277", "_w == 278", 1, "p3_freshmsg_cond")
# cfg/row faces: own 278->279 FIRST, then upstream 277->278
rep("WAVE_CONFIGS[278]", "WAVE_CONFIGS[279]", 2, "p3_wavecfg278_own")
rep("WAVE_CONFIGS[277]", "WAVE_CONFIGS[278]", 3, "p3_wavecfg277")
rep("N1_BANDS[277]", "N1_BANDS[278]", 5, "p3_n1bands277")
rep("get(277)", "get(278)", 1, "p3_get277")
rep("_c277", "_c278", 5, "p3_c277var")
rep('278: {"batch"', '279: {"batch"', 2, "p3_cfg278")
rep('278: {{"batch"', '279: {{"batch"', 1, "p3_cfg278_fstring")
rep('278: {"a"', '279: {"a"', 1, "p3_row278")
rep('278: {{"a"', '279: {{"a"', 2, "p3_row278_fstring")
rep('277: {"batch"', '278: {"batch"', 2, "p3_cfg277")
rep('277: {"a"', '278: {"a"', 3, "p3_row277")
rep("arith_a278", "arith_a279", 6, "p3_arith_a")
rep("arith_b278", "arith_b279", 6, "p3_arith_b")
rep("(274, 273, 272, 271, 270, 269, 268, 267, 266, 265)",
    "(275, 274, 273, 272, 271, 270, 269, 268, 267, 266)", 2, "p3_transitive_list")
rep("W265..W274", "W266..W275", 1, "p3_transitive_window")
# ordinal faces: owner 267->268, bma 130 held, bmc 96->97 (W279 = 269th candidate, bm-c 98th own)
rep("len(owner_rows_live) == 267 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 96",
    "len(owner_rows_live) == 268 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 97", 1, "p3_ordinal_assert")
rep("267/130/96", "268/130/97", 1, "p3_ordinal_expect")
rep("owner_rows=267 / bma_rows=130 / bmc_rows=96",
    "owner_rows=268 / bma_rows=130 / bmc_rows=97", 1, "p3_leg0_face")
rep("rows 267 + candidate = 268th", "rows 268 + candidate = 269th", 2, "p3_owner267")
rep("; bm-c rows 96 +", "; bm-c rows 97 +", 1, "p3_comment_split")
rep("bm-c rows 96 + candidate = 97th owned", "bm-c rows 97 + candidate = 98th owned", 1, "p3_receipt_owned")
rep("# candidate = 97th EXACT", "# candidate = 98th EXACT", 1, "p3_comment_97th")
rep("engine_owner==bm-c rows 96 + candidate", "engine_owner==bm-c rows 97 + candidate", 1, "p3_pr_eo")
rep("bm-c rows {len(bmc_rows_live)} + candidate (97th own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (98th own wave", 1, "p3_gate05_print")
rep("bm-c's 97th own wave", "bm-c's 98th own wave", 2, "p3_97th_own")
rep("NINETY-SEVENTH owned", "NINETY-EIGHTH owned", 3, "p3_97th_caps")
rep("TWO HUNDRED AND SEVENTY-EIGHTH", "TWO HUNDRED AND SEVENTY-NINTH", 3, "p3_wave_caps")
# 7 raw bmc_rows=96 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=96", "bmc_rows=97", 6, "p3_bmc_rows96")
rep('"probe_receipt_bmc_ordinal_face": 96', '"probe_receipt_bmc_ordinal_face": 97', 1, "p3_probe_face_key")
rep("bmc rows 96 + candidate 97th", "bmc rows 97 + candidate 98th", 1, "p3_hdr_ordinal")
# ordinal narrative: B-ordinal TWENTY-EIGHTH->TWENTY-NINTH FIRST, then A-ordinal TWENTY-SEVENTH->TWENTY-EIGHTH
rep("TWENTY-EIGHTH", "TWENTY-NINTH", 7, "p3_28_caps")
rep("TWENTY-SEVENTH", "TWENTY-EIGHTH", 15, "p3_27_caps")
rep("twenty-eighth", "twenty-ninth", 4, "p3_28_lc")
rep("twenty-seventh", "twenty-eighth", 3, "p3_27_lc")
rep("sixty-sixth", "sixty-seventh", 2, "p3_66rd")
# wave-number narrative faces
rep("wave 278 engine_owner=bm-c", "wave 279 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 278: "', '"wave 279: "', 1, "p3_cfg_waveface")
rep("wave 278 = first free number", "wave 279 = first free number", 1, "p3_mhdr_waveface")
# cycle/lineage window stamps (SEAT->r1119 / SPLICE->r1118 / FINALIZE+
# CYCLE-COMPLETE->r1119 / PREREG->r1122; contexts measured)
rep("cycle COMPLETE bm-c r1114-continuation closeout 10:4x", "cycle COMPLETE bm-c r1119 closeout 15:1x", 1, "p3_hdr_complete")
rep("bm-c r1114-continuation splice window", "bm-c r1118 splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1114-continuation", "own-wave full cycle r1119", 1, "p3_repair_note")
rep("bm-c splice generation r1114-continuation window", "bm-c splice generation r1118 window", 1, "p3_parity_source")
rep("verified r1114-continuation", "verified r1119", 1, "p3_lineage_verified")
rep("# r1114-continuation splice window", "# r1118 splice window", 1, "p3_lineage_r")
rep("(bm-c r1114-continuation", "(bm-c r1118", 1, "p3_parity_comment")
rep("finalize one-pass bm-c r1114-continuation closeout, ledger", "finalize one-pass bm-c r1119 closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1114-continuation closeout ledger", "finalize one-pass bm-c r1119 closeout ledger", 1, "p3_finpass_hdr")
rep("(r1114-continuation MSG-", "(r1119 MSG-", 1, "p3_hdr_msgline")
rep("r1114-continuation BEFORE this freeze", "r1119 BEFORE this freeze", 1, "p3_receipt_seatnote")
rep("seat itself r1114-continuation; queue-head", "seat itself r1119; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1114-continuation, queue-head seat-first supply", "(r1119, queue-head seat-first supply", 1, "p3_pfcomment_seat")
# prereg window map (W278 prereg r1116 window -> W279 prereg r1122 window)
rep("bm-c r1116 window", "bm-c r1122 window", 4, "p3_prereg_window")
rep("# r1116 window", "# r1122 window", 1, "p3_hdr_prereg_window")
# not-a-re-pick face
rep("(R277: ", "(R278: ", 1, "p3_repick")
# r1076-family ROOT CURE +1 aging law (NOT the mechanical form)
rep("_set_wave(278)", "_set_wave(279)", 1, "p3_setwave_rootcure")

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
# residual sweep (r1091 law: self-produced faces EXCLUDED -- 628_901/629_100
# fresh prior-B-band faces x4/x6, "W279" inside the fresh relkeys, "_w278bmc_"
# lineage-template face, "if w < 278)" anti-gate needle, "range(248, 278)"
# fresh dropped-range assert, n1_w278/w278_ fresh upstream tokens,
# PERPETUAL_N1_W278_PREREG upstream refs; the bare-r1118 face lives ONLY
# inside the produced r1118 compounds and is NOT sweepable)
for gone in ("r1114-continuation", "r1116", "12:2x", "13:3x", "10:4x",
             "b187aa6214", "9e53371814",
             "99001d3d3f337942", "df1aaba72a",
             "MSG-20261019-102x", "_w277bmc_",
             "n1_w277", "w277_", "n1w278-",
             "628_900", "628_700", "626_901", "627_100",
             "628901", "630900", "629101", "629300",
             "1,033,735", "607,320", "1_033_735", "607_320",
             "W279p", "W278p", "W277p", "W276p", "W275p", "W274p",
             "W275_W276_W278_bands_respected",
             "rows 267 + candidate", "bmc_rows=96", "267/130/96",
             "NINETY-SEVENTH owned", "TWO HUNDRED AND SEVENTY-EIGHTH",
             "TWENTY-SEVENTH", "twenty-seventh", "sixty-sixth", "sixty-six legs",
             "wave 278 engine_owner=bm-c", '"wave 278: "', "wave 278 = first free number",
             '"wave": 277',
             "arith_a278", "arith_b278",
             "range(16, 278)", "range(17, 278)", "range(209, 279)",
             "range(248, 277)", "range(211, 277)", "if w < 277)",
             "278 - _lw", "_w == 277",
             "PERPETUAL-N1-W278", "20261018", "2026-10-18"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
  'MSG-20261019-145x-bmc-w279-seat': 7, "900c23fe7d": 2, "_w279bmc_": 11, "_w278bmc_": 1,
  "20261019": 17, "b6f486af35": 1,
  "c2fc7c34d0e41a68": 2, "ba5c725b42": 1,
  "631_101": 5, "631_300": 4, "631_100": 9, "630_900": 2,
  "629_101": 8, "629_300": 2, "628_901": 4, "629_100": 6,
  "631101": 1, "633100": 1, "631301": 2, "631500": 2,
  "1,035,935": 6, "609,520": 6, "1_035_935": 1, "609_520": 1,
  "n1_w279": 4, "n1_w278": 4, "n1w279-": 2,
  "n1_w279_results.json": 2, "n1_w278_results.json": 4,
  '279: {"batch"': 2, '278: {"batch"': 2, '277: {"batch"': 0,
  '279: {{"batch"': 1, '279: {"a"': 1, '278: {"a"': 3, '279: {{"a"': 2, '277: {{"a"': 0,
  "range(248, 279)": 2, "range(248, 278)": 1, "range(16, 279)": 2, "range(17, 279)": 3,
  "range(209, 280)": 2, "range(211, 278)": 1, "range(211, 248)": 1, "range(138, 207)": 1,
  "if w < 279)": 5, "if w < 278)": 1, "279 - _lw": 2,
  "m248": 4, "m211": 4, "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
  "WAVE_CONFIGS[279]": 2, "WAVE_CONFIGS[278]": 3, "N1_BANDS[278]": 5,
  "get(278)": 1, "_c278": 5,
  "arith_a279": 6, "arith_b279": 6,
  "(275, 274, 273, 272, 271, 270, 269, 268, 267, 266)": 2, "W266..W275": 1,
  "len(owner_rows_live) == 268": 1, "268/130/97": 1, "bmc_rows=97": 7,
  "rows 268 + candidate = 269th": 2, "bm-c rows 97 + candidate = 98th owned": 1,
  "NINETY-EIGHTH owned": 3, "TWO HUNDRED AND SEVENTY-NINTH": 3,
  "TWENTY-NINTH": 7, "TWENTY-EIGHTH": 15, "twenty-ninth": 4, "twenty-eighth": 3,
  "W276_W277_W278_bands_respected": 2, "W280p": 13, "W280": 26,
  "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
  "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
  "W279 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
  "2026-10-19 19:2x bm-c r1123 splice window": 1,
  "finalize one-pass bm-c r1119": 2,
  "authored 18:5x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
  "cycle COMPLETE bm-c r1119 closeout 15:1x": 1,
  "verified r1119": 1, "(R278: ": 1, "_w == 278": 1,
  "wave 279 engine_owner=bm-c": 1, '"wave 279: "': 1,
  "wave 279 = first free number": 1, "sixty-seventh": 2, "sixty-seven legs": 1,
  'N1_BANDS[") == 136,': 1, '!= 136': 1, 'N1_BANDS[") == 67': 1,
  'N1_BANDS[") == 37': 1, 'N1_BANDS[") == 30': 1,
  "W211..W277 legs (67)": 1, "W211..W278 legs 67": 1,
  "own W248..W277 legs (30)": 4, "own W248..W277": 5, "W248..W279 legs (31": 4,
  "block = 137 rows": 1, "137 parity rows": 1, "block parity = 137 rows": 1,
  "bm-c r1122 window": 4, "# r1122 window": 1,
  "bm-c splice generation r1118 window": 1, "(bm-c r1118": 1,
  "_w278bmc_freeze_edits.py template": 1,
  "PERPETUAL_N1_W279_PREREG": 8, "PERPETUAL_N1_W278_PREREG": 2, "PERPETUAL-N1-W279": 7,
  "W279 materializer face": 4, "W278 materializer face": 1,
  "W277 finalize product": 0, "W278 finalize product": 4,
  "engine_owner==bm-c rows 97 + candidate": 1, "# candidate = 98th EXACT": 1, "; bm-c rows 97 +": 1,
  "bm-c rows {len(bmc_rows_live)} + candidate (98th own wave": 1,
  "bm-c's 98th own wave": 2, "owner_rows=268 / bma_rows=130 / bmc_rows=97": 1,
  '"probe_receipt_bmc_ordinal_face": 97': 1,
  "fourteen-wave": 8, "post-W278-REGISTERED": 8,
  "anchors W278 1,035,935 / K=609,520 at draft": 1,
  "dual-window parity": 1, "W280 walk": 1,
  "sixty-seventh consecutive": 2, '"wave": 278': 1,
  "registered wave below 263 composes": 2,
  "PRE-W279-splice": 1, "post-W278 registration": 2,
  "expect 268/130/97": 1,
  "_set_wave(279)": 1, "_set_wave(278)": 0, "_set_wave(277)": 0, "_set_wave(2)": 1,
  "derived by the bm-c": 2,
  "bm-c own-seat continuity": 2,
  "physical bytes": 6,
  "own-wave full cycle r1119": 1,
  "r1119 BEFORE this freeze": 1, "seat itself r1119; queue-head": 1,
  "(r1119, queue-head seat-first supply": 1, "(r1119 MSG-": 1,
  "bm-c r1118 splice window": 2,
  "# r1118 splice window": 1,
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
