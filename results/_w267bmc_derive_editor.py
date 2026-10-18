# -*- coding: utf-8 -*-
# r1088 bm-c: derive results/_w267bmc_freeze_edits.py from the committed W266
# freeze-edits canon (results/_w266bmc_freeze_edits.py, bm-c r1086 splice
# window dc71ecc3f9, proven live-fire: W266 five-face splice + engine
# self-burn 12/12 + finalize one-pass ledger 1,009,535 / K=583,120 + W267
# seat published @ origin 942ebd5885, machine-verified r1087) by
# COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage, zero transcription: every
# needle count MEASURED on the canon blob by
# results/_r1088bmc_needle_preflight.py + results/_r1088bmc_needle_probe2.py
# -- r1077 measured-counts law; canon blob e875d40c497536f4 == HEAD twin
# verified in-preflight).
# AGING-TOKEN LAW (E63 anti-drift): frozen faces w244_a/w244_b and
# n3r1_used245 do NOT roll (measured 12/8/3 in canon; carried verbatim,
# anti-drift asserted here; "w244_a holds wave-263 bands" disclosure text
# carries verbatim, measured 4). Band order law: consumers before producers
# (602_501/602_700 consumed BEFORE the 600_301/600_500 producers, else the
# fresh prior-wave B tokens double-transform); own-first law at every level
# (n1_w266 before n1_w265; w266_ before w265_; W266 blanket before W265
# blanket; '266: {"batch"' before '265: {"batch"'; WAVE_CONFIGS[266] before
# [265]; SIXTEENTH before FIFTEENTH).
# DISCLOSED SAME-WINDOW HEALS (2, zero content impact):
# (1) receipt "wave" field 265->266: stale-carried face since the W265 TOL
#     canon (W265 TOL receipt wave field = 265 measured via git show; the
#     W266 editor had no rep for it); rolled here to the upstream-finalized
#     semantics (W266 finalized at the W267 splice), mechanical +1.
# (2) authored stamp 09:0x -> 10:5x: the W267 prereg derive script mtime
#     10:58:26 measured (research/PERPETUAL_N1_W267_PREREG.md frozen 10:5x
#     per r1087 closeout), W267 prereg window = bm-c r1087 (4x) + r1087
#     commit (1x) per the same closeout face.
# Ordinals: owner 256 / bma 130 / bmc 85 live at freeze (probe leg0 rows=256
# bmc_rows=85, W267 candidate = 257th engine-owned, bm-c 86th own wave).
# Ordinal order law: SEVENTEENTH (B, above-own-A) before SIXTEENTH (A, A-hop).
import io, subprocess, sys

CANON = "results/_w266bmc_freeze_edits.py"
DST = "results/_w267bmc_freeze_edits.py"
LOG = "results/_r1088bmc_derive_editor_log.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w266bmc_freeze_edits.py"],
                           capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head and len(blob_wt) == 40, f"canon blob drift wt={blob_wt} head={blob_head}"
assert blob_wt.startswith("e875d40c497536f4"), f"canon face drift vs preflight-measured blob: {blob_wt[:16]}"

t = io.open(CANON, encoding="utf-8", newline="").read()
log = [f"S0 canon blob verified {blob_wt[:16]} == HEAD twin (preflight-measured face)",
       f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:100]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W267p", "W268p", 13, "p1_proj_prefix")
rep("W267", "W268", 13, "p1_proj_plain")
# bands: W267 registered A 602_701..604_700 (16th A-hop) / B 604_701..604_900
# (17th above-own-A); naive A 602_501..604_500 refused at registered W266 B
# 602_501..602_700; naive B 602_701..602_900 inside own-A reservation.
# CONSUMERS FIRST (band-order law):
rep("602_501", "604_701", 5, "p1_band_Blo_naiveAlo")
rep("602_700", "604_900", 4, "p1_band_Bhi")
rep("600_501", "602_701", 8, "p1_band_Alo_Bnaivelo")
rep("602_500", "604_700", 9, "p1_band_Ahi")
rep("600_700", "602_900", 2, "p1_band_Bnaivehi")
rep("602_300", "604_500", 2, "p1_band_naiveAhi")
# PRODUCERS LAST (else the fresh 602_501/602_700 tokens double-transform):
rep("600_301", "602_501", 4, "p1_band_priorBlo")
rep("600_500", "602_700", 6, "p1_band_priorBhi")
# ledger/K anchors: W265 finalize facts -> W266 finalize facts (1,009,535/583,120)
rep("1,007,335", "1,009,535", 6, "p1_ledger_prose")
rep("580,920", "583,120", 6, "p1_k_prose")
rep("1_007_335", "1_009_535", 1, "p1_ledger_code")
rep("580_920", "583_120", 1, "p1_k_code")
# lowercase machine-file tokens (own wave first, then upstream wave)
rep("n1_w266", "n1_w267", 4, "p1_n1w266")
rep("n1w266-", "n1w267-", 2, "p1_n1w266dash")
# 12 raw w266_ minus 2 consumed by the n1_w266 rep (n1_w266_results x2)
rep("w266_", "w267_", 10, "p1_lc_w266_")
rep("n1_w265", "n1_w266", 4, "p1_n1w265")
# 93 raw w265_ minus 4 consumed by the n1_w265 rep (n1_w265_results x4)
rep("w265_", "w266_", 89, "p1_lc_w265_")
rep("_w266bmc_", "_w267bmc_", 11, "p1_receiptpath")
rep("MSG-20261018-0719-bmc-w266-seat", "MSG-20261018-1025-bmc-w267-seat", 7, "p1_seat_msg")
rep("ace19ba85b", "942ebd5885", 2, "p1_seat_origin")
rep("a47517f79", "dc71ecc3f9", 1, "p1_lineage_sha")
rep("595433d63c", "df55e3fab9", 1, "p1_prereg_sha_ref")
# stale-carried receipt wave field (heal #1, disclosed in header): 265->266
rep('"wave": 265', '"wave": 266', 1, "p1_receipt_wave")
# header window stamp: this r1088 freeze window
rep("2026-10-18 10:2x bm-c r1086 freeze window", "2026-10-18 11:2x bm-c r1088 freeze window", 1, "p1_hdr_stamp")

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W266", "W267", 92, "p2_own_wave")
rep("W265", "W266", 163, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
rep("W263_W264_W266_bands_respected", "W264_W265_W266_bands_respected", 2, "p3_relkey")
rep("W211..W246 legs (36)", "W211..W247 legs (37)", 2, "p3_kept_narr")
rep("W211..W264 legs (54)", "W211..W265 legs (55)", 1, "p3_legs_narr")
# overlap law (measured: all 4 own-prefix dropped forms carry the legs suffix):
# own-forms FIRST, then the residual own-prefix (1), then the fstring
rep("own W247..W264 legs (18)", "own W248..W265 legs (18)", 4, "p3_dropped_narr")
rep("own W247..W264", "own W248..W265", 1, "p3_dropped_split_hdr")
rep("W247..W264 eighteen legs", "W248..W265 eighteen legs", 1, "p3_dropped_fstring")
# fullspan error-string: post-D wave face held at one-behind value, count rolls
rep("W211..W266 legs 54", "W211..W266 legs 55", 1, "p3_fullspan_fstring")
rep("W211..W264 fifty-four legs", "W211..W265 fifty-five legs", 1, "p3_legs_fstring")
rep("keep W211..W246 verbatim (36 legs)", "keep W211..W247 verbatim (37 legs)", 1, "p3_kept_comment")
rep("W211..W246 thirty-six legs", "W211..W247 thirty-seven legs", 1, "p3_kept_fstring")
# fresh legs: post-D form (W265->W266 rolled the hi wave)
rep("W247..W266 legs (19", "W248..W266 legs (19", 4, "p3_fresh_narr")
rep("block = 124 rows", "block = 125 rows", 1, "p3_block124")
rep("124 parity rows", "125 parity rows", 1, "p3_parity124")
rep('N1_BANDS[") == 123,', 'N1_BANDS[") == 124,', 1, "p3_count123")
rep("!= 123", "!= 124", 1, "p3_fstring123")
rep('N1_BANDS[") == 54', 'N1_BANDS[") == 55', 1, "p3_count54")
rep('N1_BANDS[") == 36', 'N1_BANDS[") == 37', 1, "p3_count36")
rep("range(211, 247)", "range(211, 248)", 1, "p3_range_kept")
rep("range(211, 265)", "range(211, 266)", 1, "p3_range_legs")
rep("range(247, 265)", "range(248, 266)", 1, "p3_range_dropped")
rep("range(247, 266)", "range(248, 267)", 2, "p3_range_fresh")
rep("range(16, 266)", "range(16, 267)", 2, "p3_range16")
rep("range(17, 266)", "range(17, 267)", 3, "p3_range17")
rep("range(209, 267)", "range(209, 268)", 2, "p3_range209")
# wave-number gates (own 266->267 FIRST, then anti-gate 265->266)
rep("if w < 266)", "if w < 267)", 5, "p3_wlt266")
rep("if w < 265)", "if w < 266)", 1, "p3_wlt265_antigate")
rep("266 - _lw", "267 - _lw", 2, "p3_legcount")
rep("N1_BANDS\\[247\\]", "N1_BANDS\\[248\\]", 1, "p3_regex247")
rep("m247", "m248", 4, "p3_m247")
rep("N1_BANDS[247] ==", "N1_BANDS[248] ==", 1, "p3_startswith247")
# own-wave cfg band asserts roll 266->267 FIRST (band-faces own-first law),
# then the upstream mirror 265->266 (else the fresh [266] tokens double-transform)
rep("WAVE_CONFIGS[266]", "WAVE_CONFIGS[267]", 2, "p3_wavecfg266_own")
rep("WAVE_CONFIGS[265]", "WAVE_CONFIGS[266]", 3, "p3_wavecfg265")
rep("N1_BANDS[265]", "N1_BANDS[266]", 5, "p3_n1bands265")
rep("get(265)", "get(266)", 1, "p3_get265")
rep("_c265", "_c266", 5, "p3_c265var")
# cfg/row dict faces: own 266->267 FIRST, then upstream 265->266 (template order law)
rep('266: {"batch"', '267: {"batch"', 2, "p3_cfg266")
rep('266: {{"batch"', '267: {{"batch"', 1, "p3_cfg266_fstring")
rep('266: {"a"', '267: {"a"', 1, "p3_row266_postgate")
rep('266: {{"a"', '267: {{"a"', 2, "p3_row266_fstring")
rep('265: {"batch"', '266: {"batch"', 2, "p3_cfg265")
rep('265: {"a"', '266: {"a"', 3, "p3_row265")
rep("arith_a266", "arith_a267", 6, "p3_arith_a")
rep("arith_b266", "arith_b267", 6, "p3_arith_b")
rep("(262, 261, 260, 259, 258, 257, 256, 255, 254, 253)",
    "(263, 262, 261, 260, 259, 258, 257, 256, 255, 254)", 2, "p3_transitive_list")
rep("W253..W262", "W254..W263", 1, "p3_transitive_window")
# ordinal faces: owner 255->256, bma 130 held, bmc 84->85 (W267 = 257th candidate, bm-c 86th own)
rep("len(owner_rows_live) == 255 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 84",
    "len(owner_rows_live) == 256 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 85", 1, "p3_ordinal_assert")
rep("255/130/84", "256/130/85", 1, "p3_ordinal_expect")
rep("owner_rows=255 / bma_rows=130 / bmc_rows=84", "owner_rows=256 / bma_rows=130 / bmc_rows=85", 1, "p3_leg0_face")
rep("rows 255 + candidate = 256th", "rows 256 + candidate = 257th", 2, "p3_owner255")
rep("; bm-c rows 84 +", "; bm-c rows 85 +", 1, "p3_comment_84split")
rep("bm-c rows 84 + candidate = 85th owned", "bm-c rows 85 + candidate = 86th owned", 1, "p3_receipt_85owned")
rep("# candidate = 85th EXACT", "# candidate = 86th EXACT", 1, "p3_comment_85th")
rep("engine_owner==bm-c rows 84 + candidate", "engine_owner==bm-c rows 85 + candidate", 1, "p3_pr_eo84")
rep("bm-c rows {len(bmc_rows_live)} + candidate (85th own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (86th own wave", 1, "p3_gate0_5_print")
rep("bm-c's 85th own wave", "bm-c's 86th own wave", 2, "p3_85th_own_wave")
rep("EIGHTY-FIFTH owned", "EIGHTY-SIXTH owned", 3, "p3_85th_caps")
rep("TWO HUNDRED AND SIXTY-SIXTH", "TWO HUNDRED AND SIXTY-SEVENTH", 3, "p3_wave_caps")
# 7 raw bmc_rows=84 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=84", "bmc_rows=85", 6, "p3_bmc_rows84")
rep('"probe_receipt_bmc_ordinal_face": 84', '"probe_receipt_bmc_ordinal_face": 85', 1, "p3_probe_face_key")
# ordinal narrative: B-ordinal SIXTEENTH->SEVENTEENTH FIRST, then A-ordinal FIFTEENTH->SIXTEENTH
rep("SIXTEENTH", "SEVENTEENTH", 7, "p3_16_caps")
rep("FIFTEENTH", "SIXTEENTH", 15, "p3_15_caps")
rep("sixteenth", "seventeenth", 4, "p3_16_lc")
rep("fifteenth", "sixteenth", 3, "p3_15_lc")
rep("fifty-fourth", "fifty-fifth", 2, "p3_54th")
# wave-number narrative faces
rep("wave 266 engine_owner=bm-c", "wave 267 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 266: "', '"wave 267: "', 1, "p3_cfg_waveface")
rep("wave 266 = first free number", "wave 267 = first free number", 1, "p3_mhdr_waveface")
# upstream-cycle lineage (W266 cycle: prereg r1085 / splice r1086 / finalize r1086 10:2x / seat r1086)
rep("cycle COMPLETE bm-c r1081+r1084 closeout 07:0x", "cycle COMPLETE bm-c r1085+r1086 closeout 10:5x", 1, "p3_hdr_complete")
rep("the bm-c r1084 splice window", "the bm-c r1086 splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1084", "own-wave full cycle r1086", 1, "p3_repair_note")
rep("bm-c splice generation r1084 window", "bm-c splice generation r1086 window", 1, "p3_parity_source_note")
rep("r1084, pre-seat probe", "r1086, pre-seat probe", 1, "p3_hdr_seatstamp")
rep("verified r1085", "verified r1087", 1, "p3_lineage_verified")
rep("# r1084 splice window", "# r1086 splice window", 1, "p3_lineage_r1084")
rep("(bm-c r1084", "(bm-c r1086", 1, "p3_parity_comment")
rep("seat itself r1084; queue-head", "seat itself r1086; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1084, queue-head seat-first supply", "(r1086, queue-head seat-first supply", 1, "p3_pfcomment_seat")
rep("finalize one-pass bm-c r1084 closeout, ledger", "finalize one-pass bm-c r1086 closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1084 closeout ledger", "finalize one-pass bm-c r1086 closeout ledger", 1, "p3_finpass_hdr")
rep("(r1084 MSG-", "(r1086 MSG-", 1, "p3_hdr_msgline")
rep("r1084 BEFORE this freeze", "r1086 BEFORE this freeze", 1, "p3_receipt_seatnote")
# prereg window map (r1085 prereg window -> r1087, the W267 prereg freeze window)
rep("bm-c r1085 window", "bm-c r1087 window", 4, "p3_prereg_window")
rep("# r1085 window", "# r1087 window", 1, "p3_hdr_prereg_window")
rep("r1085 commit", "r1087 commit", 1, "p3_receipt_commit")
# heal #2 (disclosed in header): authored stamp per the W267 prereg derive mtime 10:58:26
rep("authored 09:0x", "authored 10:5x", 2, "p3_authored_stamp")
# lineage header: canon template identity rolls to the W266 canon
rep("_w265bmc_freeze_edits_TOL.py template", "_w266bmc_freeze_edits.py template", 1, "p3_lineage_template")
rep("(R265: ", "(R266: ", 1, "p3_repick")
rep("_w == 265", "_w == 266", 1, "p3_freshmsg_cond")
# r1076-family 4th-recurrence ROOT CURE (welded at the birth station per the
# 2026-10-16 CEO defect-birthplace law): the canon hdr "_set_wave(<n>)" face
# is digit-only (no W prefix) so no blanket rep ever rolled it -- the W266
# canon carried the 2-stale form _set_wave(265) into the W267 splice (selftest
# FAIL "W267 A hits W265" caught it, prereheal evidence preserved in the tool
# log). Cured here to the own-wave form; the W268 editor MUST age this needle
# to ('_set_wave(267)', '_set_wave(268)') per the +1 aging law -- NOT the
# mechanical (266->268) form (the canon it reads carries 267, the healed face).
rep("_set_wave(265)", "_set_wave(267)", 1, "p3_setwave_rootcure")

# ---------- phase 4: frozen-face anti-drift + residual sweeps ----------
assert t.count("w244_a") == 12 and t.count("w244_b") == 8, "aging tokens w244_a/b drift"
assert t.count("n3r1_used245") == 3, "frozen face n3r1_used245 drift"
assert t.count("w244_a holds wave-263 bands") == 4, "aging disclosure text drift"
assert t.count("m211") == 4, "frozen estate boundary marker m211 drift"
assert t.count("593901") == 1, "fmt doc example face drift"
assert t.count("bma rows 129 + candidate 130th") == 1, "carried bma-ordinal note drift"
assert t.count("registered wave below 263 composes") == 2, "carried family-6 comment face drift"
assert t.count("bm-c own-seat continuity") == 2, "carried own-seat continuity face drift"
for gone in ("r1081", "r1084", "a47517f79", "595433d63c", "ace19ba85b",
            "MSG-20261018-0719-bmc-w266-seat", "_w265bmc_", "w265_", "n1_w265",
            "n1w266-", "600_301", "600_500", "600_700", "602_300", "600_501",
            "602_500", "598_101", "598_300", "598_301", "600_300", "598_500",
            "600_100", "1,007,335", "580,920", "1_007_335", "580_920",
            "20261017", "W267p", "W211..W246", "W211..W264", "W247..W264",
            "own W247..W264", "thirty-six", "fifty-fourth", "fifty-three",
            "PENDING at seat", "waits-upstream face disclosed honest",
            "bma_ordinal", "ONE HUNDRED AND THIRTIETH", "EIGHTY-FIFTH owned",
            "83rd", "84th", "TWO HUNDRED AND SIXTY-SIXTH", "== 123", "!= 123",
            "N1_BANDS[246] ==", "N1_BANDS\\[246\\]", "m246",
            "FOURTEENTH", "fourteenth", "fifteenth", "FIFTEENTH",
            "rows 255 + candidate", "bmc_rows=84", "rows 254 + candidate",
            "254/130/83", "owner_rows=254", "len(owner_rows_live) == 254",
            "(R265: ", "_w == 265",
            "bm-a five-face freeze upstream seat", "bm-a (upstream seat honored)",
            "owner=bm-a seat honored", "(bm-a seat owner expected)",
            "18:2x", "19:2x", "20:5x", "22:4x", "editor template",
            "block = 124 rows", "124 parity rows", "authored 09:0x",
            "W263_W264_W265_bands_respected",
            "range(211, 247)", "range(211, 265)", "range(247, 265)",
            "range(247, 266)", "range(16, 266)", "range(17, 266)", "range(209, 267)",
            "if w < 265)", "m247", "N1_BANDS[247] ==", "N1_BANDS\\[247\\]",
            '"wave": 265'):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: 70 faces zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
    'MSG-20261018-1025-bmc-w267-seat': 7, "942ebd5885": 2, "_w267bmc_": 11,
    "20261018": 17, "df55e3fab9": 1, "dc71ecc3f9": 1,
    "604_701": 5, "604_900": 4, "602_701": 8, "604_700": 9,
    "602_900": 2, "604_500": 2, "602_501": 4, "602_700": 6,
    "1,009,535": 6, "583,120": 6, "1_009_535": 1, "583_120": 1,
    '267: {"batch"': 2, '266: {"batch"': 2, '265: {"batch"': 0,
    '267: {{"batch"': 1, '267: {"a"': 1, '266: {"a"': 3, '267: {{"a"': 2,
    "range(248, 267)": 2, "range(209, 268)": 2, "range(16, 267)": 2,
    "range(17, 267)": 3, "range(211, 248)": 1, "range(211, 266)": 1,
    "range(248, 266)": 1, "range(138, 207)": 1,
    "if w < 267)": 5, "if w < 266)": 1, "267 - _lw": 2,
    "m248": 4, "m211": 4, "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
    "WAVE_CONFIGS[267]": 2, "WAVE_CONFIGS[266]": 3, "N1_BANDS[266]": 5, "get(266)": 1, "_c266": 5,
    "arith_a267": 6, "arith_b267": 6,
    "(263, 262, 261, 260, 259, 258, 257, 256, 255, 254)": 2, "W254..W263": 1,
    "len(owner_rows_live) == 256": 1, "256/130/85": 1, "bmc_rows=85": 7,
    "rows 256 + candidate = 257th": 2, "bm-c rows 85 + candidate = 86th owned": 1,
    "EIGHTY-SIXTH owned": 3, "TWO HUNDRED AND SIXTY-SEVENTH": 3,
    "SEVENTEENTH": 7, "SIXTEENTH": 15, "seventeenth": 4, "sixteenth": 3,
    "W264_W265_W266_bands_respected": 2, "W268p": 13, "W268": 26,
    "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
    "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
    "W267 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
    "the bm-c r1086 splice window": 2,
    "bm-c own seat executed at the bm-c r1086 splice window": 1,
    "finalize one-pass bm-c r1086": 2,
    "authored 10:5x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
    "cycle COMPLETE bm-c r1085+r1086 closeout 10:5x": 1,
    "verified r1087": 1, "(R266: ": 1, "_w == 266": 1,
    "wave 267 engine_owner=bm-c": 1, '"wave 267: "': 1,
    "wave 267 = first free number": 1, "fifty-fifth": 2, "fifty-five legs": 1,
    'N1_BANDS[") == 124,': 1, '!= 124': 1, 'N1_BANDS[") == 55': 1,
    'N1_BANDS[") == 37': 1,
    "W211..W247 legs (37)": 2, "W211..W265 legs (55)": 1, "W211..W266 legs 55": 1,
    "own W248..W265 legs (18)": 4, "own W248..W265": 5, "W248..W266 legs (19": 4,
    "block = 125 rows": 1, "125 parity rows": 1,
    "bm-c r1087 window": 4, "# r1087 window": 1, "r1087 commit": 1,
    "bm-c splice generation r1086 window": 1, "(bm-c r1086": 1,
    "_w266bmc_freeze_edits.py template": 1,
    "PERPETUAL_N1_W267_PREREG": 8, "PERPETUAL-N1-W267": 7,
    "n1_w267": 4, "n1_w266": 4, "n1w267-": 2,
    "W267 materializer face": 4, "W266 materializer face": 1,
    "W267 block parity = 121 rows": 1,
    "engine_owner==bm-c rows 85 + candidate": 1,
    "# candidate = 86th EXACT": 1, "; bm-c rows 85 +": 1,
    "bm-c rows {len(bmc_rows_live)} + candidate (86th own wave": 1,
    "bm-c's 86th own wave": 2, "owner_rows=256 / bma_rows=130 / bmc_rows=85": 1,
    '"probe_receipt_bmc_ordinal_face": 85': 1,
    "fourteen-wave": 8, "post-W266-REGISTERED": 8,
    "anchors W266 1,009,535 / K=583,120 at draft": 1,
    "dual-window parity": 1, "W268 walk": 1,
    "fifty-fifth consecutive": 2, '"wave": 266': 1,
    "bma rows 129 + candidate 130th": 1,
    "registered wave below 263 composes": 2,
    "n1_w266_results.json": 4, "n1_w267_results.json": 2,
    "W266 finalize product": 4,
    "PRE-W267-splice": 1, "post-W266 registration": 2,
    "expect 256/130/85": 1, "_set_wave(267)": 1, "_set_wave(265)": 0,
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
