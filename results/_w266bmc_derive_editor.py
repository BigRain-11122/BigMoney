# -*- coding: utf-8 -*-
# r1086 bm-c: derive results/_w266bmc_freeze_edits.py from the committed W265
# freeze-edits canon (results/_w265bmc_freeze_edits_TOL.py, bm-c r1084 splice
# window a47517f79, proven live-fire: W265 five-face splice + engine self-burn
# 12/12 + W265 CYCLE COMPLETE finalize one-pass ledger 1,007,335 / K=580,920
# + W266 seat published @ origin ace19ba85b, machine-verified r1085) by
# COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage, zero transcription: every
# needle count pre-measured on the canon blob by
# results/_w266bmc_editor_needle_preflight.py + _w266bmc_needle_gaps2.py +
# _w266bmc_needle_gaps3.py -- r1077 measured-counts law; heal#8 fresh family
# instance disclosed: counts MEASURED not pattern-assumed; overlap
# adjudication: 4-of-5 own-prefix faces carry the legs suffix -> legs-rep
# FIRST (4) then own-rep residual (1)).
# AGING-TOKEN LAW (E63 anti-drift): frozen faces w244_a/w244_b and
# n3r1_used245 do NOT roll (measured 12/8/3 in canon; carried verbatim,
# anti-drift asserted here; "w244_a holds wave-263 bands" disclosure text
# carries verbatim, measured 4). Band order law: consumers before producers;
# ordinal order law: SIXTEENTH (B, above-own-A) before FIFTEENTH (A, A-hop).
import io, subprocess, sys

CANON = "results/_w265bmc_freeze_edits_TOL.py"
DST = "results/_w266bmc_freeze_edits.py"
LOG = "results/_r1086bmc_derive_editor_log.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w265bmc_freeze_edits_TOL.py"],
                           capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head and len(blob_wt) == 40, f"canon blob drift wt={blob_wt} head={blob_head}"

t = io.open(CANON, encoding="utf-8", newline="").read()
log = [f"S0 canon blob verified {blob_wt[:16]} == HEAD twin", f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:100]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W266p", "W267p", 13, "p1_proj_prefix")
rep("W266", "W267", 13, "p1_proj_plain")
# bands: W266 registered A 600_501..602_500 (15th A-hop) / B 602_501..602_700
# (16th above-own-A); naive A 600_301..602_300 refused at registered W265 B
# 600_301..600_500; naive B 600_501..600_700 inside own-A reservation.
# CONSUMERS FIRST (band-order law):
rep("600_301", "602_501", 5, "p1_band_Blo_naiveAlo")
rep("600_500", "602_700", 4, "p1_band_Bhi")
rep("598_301", "600_501", 8, "p1_band_Alo_Bnaivelo")
rep("600_300", "602_500", 9, "p1_band_Ahi")
rep("598_500", "600_700", 2, "p1_band_Bnaivehi")
rep("600_100", "602_300", 2, "p1_band_naiveAhi")
# PRODUCERS LAST (else the fresh 600_301/600_500 tokens double-transform):
rep("598_101", "600_301", 4, "p1_band_priorBlo")
rep("598_300", "600_500", 6, "p1_band_priorBhi")
# ledger/K anchors: W264 finalize facts -> W265 finalize facts (1,007,335/580,920)
rep("1,005,135", "1,007,335", 5, "p1_ledger_prose")
rep("578,720", "580,920", 5, "p1_k_prose")
rep("1_005_135", "1_007_335", 1, "p1_ledger_code")
rep("578_720", "580_920", 1, "p1_k_code")
# lowercase machine-file tokens (order law: own wave first, then upstream)
rep("n1_w265", "n1_w266", 4, "p1_n1w265")
rep("n1w265-", "n1w266-", 2, "p1_n1w265dash")
# 12 raw w265_ minus 2 consumed by the n1_w265 rep (n1_w265_results x2)
rep("w265_", "w266_", 10, "p1_lc_w265_")
rep("n1_w264", "n1_w265", 4, "p1_n1w264")
# 93 raw w264_ minus 4 consumed by the n1_w264 rep (n1_w264_results x4)
rep("w264_", "w265_", 89, "p1_lc_w264_")
rep("_w265bmc_", "_w266bmc_", 11, "p1_receiptpath")
rep("MSG-20261017-2241-bmc-w265-seat", "MSG-20261018-0719-bmc-w266-seat", 7, "p1_seat_msg")
rep("7343e3650", "ace19ba85b", 2, "p1_seat_origin")
rep("216b578b0", "a47517f79", 1, "p1_lineage_sha")
rep("e57215a2c", "595433d63c", 1, "p1_prereg_sha_ref")
# 17 raw 20261017 minus 7 consumed by the seat-msg rep -> 10 probe-receipt dates
rep("20261017", "20261018", 10, "p1_probe_date")
# header window stamp: this r1086 freeze window
rep("2026-10-17 20:5x bm-c r1076 freeze window", "2026-10-18 10:2x bm-c r1086 freeze window", 1, "p1_hdr_stamp")

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W265", "W266", 92, "p2_own_wave")
rep("W264", "W265", 162, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
rep("W262_W263_W265_bands_respected", "W263_W264_W265_bands_respected", 2, "p3_relkey")
rep("W211..W245 legs (35)", "W211..W246 legs (36)", 2, "p3_kept_narr")
rep("W211..W263 legs (53)", "W211..W264 legs (54)", 1, "p3_legs_narr")
# overlap law (measured: 4-of-5 own-prefix faces carry legs suffix):
# legs-rep FIRST, then the own-prefix residual (1)
rep("W246..W263 legs (18)", "W247..W264 legs (18)", 4, "p3_dropped_narr")
rep("own W246..W263", "own W247..W264", 1, "p3_dropped_split_hdr")
rep("W246..W263 eighteen legs", "W247..W264 eighteen legs", 1, "p3_dropped_fstring")
# fullspan error-string: post-D wave face held at one-behind value, count rolls
rep("W211..W265 legs 53", "W211..W265 legs 54", 1, "p3_fullspan_fstring")
rep("W211..W263 fifty-three legs", "W211..W264 fifty-four legs", 1, "p3_legs_fstring")
rep("keep W211..W245 verbatim (35 legs)", "keep W211..W246 verbatim (36 legs)", 1, "p3_kept_comment")
rep("W211..W245 thirty-five legs", "W211..W246 thirty-six legs", 1, "p3_kept_fstring")
# fresh legs: post-D form (W264->W265 rolled the hi wave)
rep("W246..W265 legs (19", "W247..W265 legs (19", 4, "p3_fresh_narr")
rep("block = 123 rows", "block = 124 rows", 1, "p3_block123")
rep("123 parity rows", "124 parity rows", 1, "p3_parity123")
rep('N1_BANDS[") == 122,', 'N1_BANDS[") == 123,', 1, "p3_count122")
rep("!= 122", "!= 123", 1, "p3_fstring122")
rep('N1_BANDS[") == 53', 'N1_BANDS[") == 54', 1, "p3_count53")
rep('N1_BANDS[") == 35', 'N1_BANDS[") == 36', 1, "p3_count35")
rep("range(211, 246)", "range(211, 247)", 1, "p3_range_kept")
rep("range(211, 264)", "range(211, 265)", 1, "p3_range_legs")
rep("range(246, 264)", "range(247, 265)", 1, "p3_range_dropped")
rep("range(246, 265)", "range(247, 266)", 2, "p3_range_fresh")
rep("range(16, 265)", "range(16, 266)", 2, "p3_range16")
rep("range(17, 265)", "range(17, 266)", 3, "p3_range17")
rep("range(209, 266)", "range(209, 267)", 2, "p3_range209")
# wave-number gates (own 265->266 FIRST, then anti-gate 264->265)
rep("if w < 265)", "if w < 266)", 5, "p3_wlt265")
rep("if w < 264)", "if w < 265)", 1, "p3_wlt264_antigate")
rep("265 - _lw", "266 - _lw", 2, "p3_legcount")
rep("N1_BANDS\\[246\\]", "N1_BANDS\\[247\\]", 1, "p3_regex246")
rep("m246", "m247", 4, "p3_m246")
rep("N1_BANDS[246] ==", "N1_BANDS[247] ==", 1, "p3_startswith246")
# own-wave cfg band asserts roll 265->266 FIRST (band-faces own-first law),
# then the upstream mirror 264->265 (else the fresh [265] tokens double-transform)
rep("WAVE_CONFIGS[265]", "WAVE_CONFIGS[266]", 2, "p3_wavecfg265_own")
rep("WAVE_CONFIGS[264]", "WAVE_CONFIGS[265]", 3, "p3_wavecfg264")
rep("N1_BANDS[264]", "N1_BANDS[265]", 5, "p3_n1bands264")
rep("get(264)", "get(265)", 1, "p3_get264")
rep("_c264", "_c265", 5, "p3_c264var")
# cfg/row dict faces: own 265->266 FIRST, then upstream 264->265 (template order law)
rep('265: {"batch"', '266: {"batch"', 2, "p3_cfg265")
rep('265: {{"batch"', '266: {{"batch"', 1, "p3_cfg265_fstring")
rep('265: {"a"', '266: {"a"', 1, "p3_row265_postgate")
rep('265: {{"a"', '266: {{"a"', 2, "p3_row265_fstring")
rep('264: {"batch"', '265: {"batch"', 2, "p3_cfg264")
rep('264: {"a"', '265: {"a"', 3, "p3_row264")
rep("arith_a265", "arith_a266", 6, "p3_arith_a")
rep("arith_b265", "arith_b266", 6, "p3_arith_b")
rep("(261, 260, 259, 258, 257, 256, 255, 254, 253, 252)",
    "(262, 261, 260, 259, 258, 257, 256, 255, 254, 253)", 2, "p3_transitive_list")
rep("W252..W261", "W253..W262", 1, "p3_transitive_window")
# ordinal faces: owner 254->255, bma 130 held, bmc 83->84 (W266 = 256th candidate, bm-c 85th own)
rep("len(owner_rows_live) == 254 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 83",
    "len(owner_rows_live) == 255 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 84", 1, "p3_ordinal_assert")
rep("254/130/83", "255/130/84", 1, "p3_ordinal_expect")
rep("owner_rows=254 / bma_rows=130 / bmc_rows=83", "owner_rows=255 / bma_rows=130 / bmc_rows=84", 1, "p3_leg0_face")
rep("rows 254 + candidate = 255th", "rows 255 + candidate = 256th", 2, "p3_owner255")
rep("; bm-c rows 83 +", "; bm-c rows 84 +", 1, "p3_comment_83split")
rep("bm-c rows 83 + candidate = 84th owned", "bm-c rows 84 + candidate = 85th owned", 1, "p3_receipt_84owned")
rep("# candidate = 84th EXACT", "# candidate = 85th EXACT", 1, "p3_comment_84th")
rep("engine_owner==bm-c rows 83 + candidate", "engine_owner==bm-c rows 84 + candidate", 1, "p3_pr_eo84")
rep("bm-c rows {len(bmc_rows_live)} + candidate (84th own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (85th own wave", 1, "p3_gate0_5_print")
rep("bm-c's 84th own wave", "bm-c's 85th own wave", 2, "p3_84th_own_wave")
rep("EIGHTY-FOURTH owned", "EIGHTY-FIFTH owned", 3, "p3_84th_caps")
rep("TWO HUNDRED AND SIXTY-FIFTH", "TWO HUNDRED AND SIXTY-SIXTH", 3, "p3_wave_caps")
# 7 raw bmc_rows=83 minus 1 consumed by the p3_leg0_face rep above
rep("bmc_rows=83", "bmc_rows=84", 6, "p3_bmc_rows83")
rep('"probe_receipt_bmc_ordinal_face": 83', '"probe_receipt_bmc_ordinal_face": 84', 1, "p3_probe_face_key")
# ordinal narrative: B-ordinal FIFTEENTH->SIXTEENTH FIRST, then A-ordinal FOURTEENTH->FIFTEENTH
rep("FIFTEENTH", "SIXTEENTH", 7, "p3_15_caps")
rep("FOURTEENTH", "FIFTEENTH", 15, "p3_14_caps")
rep("fifteenth", "sixteenth", 4, "p3_15_lc")
rep("fourteenth", "fifteenth", 3, "p3_14_lc")
rep("fifty-third", "fifty-fourth", 2, "p3_53rd")
# wave-number narrative faces
rep("wave 265 engine_owner=bm-c", "wave 266 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 265: "', '"wave 266: "', 1, "p3_cfg_waveface")
rep("wave 265 = first free number", "wave 266 = first free number", 1, "p3_mhdr_waveface")
# upstream-cycle lineage (W265 cycle: prereg r1081 / splice r1084 / finalize r1084 07:0x / seat r1084)
rep("cycle COMPLETE bm-c r1076+r1077 closeout 22:4x", "cycle COMPLETE bm-c r1081+r1084 closeout 07:0x", 1, "p3_hdr_complete")
rep("the bm-c r1076 splice window", "the bm-c r1084 splice window", 2, "p3_splice_window")
rep("own-wave full cycle r1076", "own-wave full cycle r1084", 1, "p3_repair_note")
rep("bm-c splice generation r1076 window", "bm-c splice generation r1084 window", 1, "p3_parity_source_note")
rep("bm-c r1076", "bm-c r1084", 1, "p3_residual_r1076")
rep("r1077, pre-seat probe", "r1084, pre-seat probe", 1, "p3_hdr_seatstamp")
rep("verified r1077", "verified r1085", 1, "p3_lineage_verified")
rep("seat itself r1077; queue-head", "seat itself r1084; queue-head", 1, "p3_gate05_seatsplit")
rep("(r1077, queue-head seat-first supply", "(r1084, queue-head seat-first supply", 1, "p3_pfcomment_seat")
rep("finalize one-pass bm-c r1077 closeout, ledger", "finalize one-pass bm-c r1084 closeout, ledger", 1, "p3_finpass_pre")
rep("finalize one-pass bm-c r1077 closeout ledger", "finalize one-pass bm-c r1084 closeout ledger", 1, "p3_finpass_hdr")
rep("(r1077 MSG-", "(r1084 MSG-", 1, "p3_hdr_msgline")
rep("r1077 BEFORE this freeze", "r1084 BEFORE this freeze", 1, "p3_receipt_seatnote")
# prereg window map (r1081 prereg window -> r1085, the W266 prereg freeze window)
rep("bm-c r1081 window", "bm-c r1085 window", 4, "p3_prereg_window")
rep("# r1081 window", "# r1085 window", 1, "p3_hdr_prereg_window")
rep("r1081 commit", "r1085 commit", 1, "p3_receipt_commit")
rep("authored 04:0x", "authored 09:0x", 2, "p3_authored_stamp")
# lineage header: canon template identity rolls to the W265 canon
rep("_w262bmc_freeze_edits.py template", "_w265bmc_freeze_edits_TOL.py template", 1, "p3_lineage_template")
rep("r1038 splice window", "r1084 splice window", 1, "p3_lineage_r1038")
rep("(R264: ", "(R265: ", 1, "p3_repick")
rep("_w == 264", "_w == 265", 1, "p3_freshmsg_cond")
# prereg-bundle note heal (honest roll): W266 prereg draft anchors = W265 finalize
rep("anchors W261 998,535 / K=572,120 at draft (W265 finalize pending disclosed honest)",
    "anchors W265 1,007,335 / K=580,920 at draft (upstream W265 complete at draft, disclosed honest)", 1, "p3_prereg_note_heal")

# ---------- phase 4: frozen-face anti-drift + residual sweeps ----------
assert t.count("w244_a") == 12 and t.count("w244_b") == 8, "aging tokens w244_a/b drift"
assert t.count("n3r1_used245") == 3, "frozen face n3r1_used245 drift"
assert t.count("w244_a holds wave-263 bands") == 4, "aging disclosure text drift"
for gone in ("r1076", "r1077", "r1038", "216b578b0", "e57215a2c",
            "7343e3650", "_w262bmc_", "w264_", "n1_w264", "598_101", "598_300",
            "598_301", "600_300", "598_500", "600_100",
            "1,005,135", "578,720", "1_005_135", "578_720", "20261017",
            "W211..W245", "W211..W263", "W246..W263", "own W246..W263",
            "thirty-five", "fifty-three", "fifty-third",
            "PENDING at seat", "waits-upstream face disclosed honest",
            "bma_ordinal", "ONE HUNDRED AND THIRTIETH", "EIGHTY-FOURTH owned",
            "83rd", "84th", "TWO HUNDRED AND SIXTY-FIFTH", "== 122", "!= 122",
            "N1_BANDS[245]", "m245", "rows {len(bma_rows_live)}", "wave 264",
            "was published BEFORE", "W245..W262", "W211..W262", "fifty-two",
            "range(211, 246)", "range(211, 264)", "range(246, 264)",
            "range(246, 265)", "range(16, 265)", "range(17, 265)", "range(209, 266)",
            "if w < 264)", "m246", "N1_BANDS[246] ==", "N1_BANDS\\[246\\]",
            "FOURTEENTH", "fourteenth", "rows 254 + candidate",
            "bmc_rows=83", "rows 253 + candidate", "254/130/83", "owner_rows=254",
            "len(owner_rows_live) == 254", "(R264: ",
            "bm-a five-face freeze upstream seat", "bm-a (upstream seat honored)",
            "owner=bm-a seat honored", "(bm-a seat owner expected)",
            "18:2x", "19:2x", "20:5x", "22:4x", "editor template",
            "block = 123 rows", "123 parity rows", "authored 04:0x"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: 70 faces zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
    'MSG-20261018-0719-bmc-w266-seat': 7, "ace19ba85b": 2, "_w266bmc_": 11,
    "20261018": 17, "595433d63c": 1, "a47517f79": 1,
    "602_501": 5, "602_700": 4, "600_501": 8, "602_500": 9,
    "600_700": 2, "602_300": 2, "600_301": 4, "600_500": 6,
    "1,007,335": 6, "580,920": 6, "1_007_335": 1, "580_920": 1,
    '266: {"batch"': 2, '265: {"batch"': 2, '264: {"batch"': 0,
    '266: {{"batch"': 1, '266: {"a"': 1, '265: {"a"': 3, '266: {{"a"': 2,
    "range(247, 266)": 2, "range(209, 267)": 2, "range(16, 266)": 2,
    "range(17, 266)": 3, "range(211, 247)": 1, "range(211, 265)": 1,
    "range(247, 265)": 1, "range(138, 207)": 1,
    "if w < 266)": 5, "if w < 265)": 1, "266 - _lw": 2,
    "m247": 4, "m211": 4, "N1_BANDS[247] ==": 1, "N1_BANDS\\[247\\]": 1,
    "WAVE_CONFIGS[266]": 2, "WAVE_CONFIGS[265]": 3, "N1_BANDS[265]": 5, "get(265)": 1, "_c265": 5,
    "arith_a266": 6, "arith_b266": 6,
    "(262, 261, 260, 259, 258, 257, 256, 255, 254, 253)": 2, "W253..W262": 1,
    "len(owner_rows_live) == 255": 1, "255/130/84": 1, "bmc_rows=84": 7,
    "rows 255 + candidate = 256th": 2, "bm-c rows 84 + candidate = 85th owned": 1,
    "EIGHTY-FIFTH owned": 3, "TWO HUNDRED AND SIXTY-SIXTH": 3,
    "SIXTEENTH": 7, "FIFTEENTH": 15, "sixteenth": 4, "fifteenth": 3,
    "W263_W264_W265_bands_respected": 2, "W267p": 13, "W267": 26,
    "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
    "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
    "W266 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
    "the bm-c r1084 splice window": 2,
    "bm-c own seat executed at the bm-c r1084 splice window": 1,
    "finalize one-pass bm-c r1084": 2,
    "authored 09:0x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
    "cycle COMPLETE bm-c r1081+r1084 closeout 07:0x": 1,
    "verified r1085": 1, "(R265: ": 1, "_w == 265": 1,
    "wave 266 engine_owner=bm-c": 1, '"wave 266: "': 1,
    "wave 266 = first free number": 1, "fifty-fourth": 2, "fifty-four legs": 1,
    'N1_BANDS[") == 123,': 1, '!= 123': 1, 'N1_BANDS[") == 54': 1,
    'N1_BANDS[") == 36': 1,
    "W211..W246 legs (36)": 2, "W211..W264 legs (54)": 1,
    "W247..W264 legs (18)": 4, "own W247..W264": 5, "W247..W265 legs (19": 4,
    "block = 124 rows": 1, "124 parity rows": 1,
    "bm-c r1085 window": 4, "# r1085 window": 1, "r1085 commit": 1,
    "bm-c splice generation r1084 window": 1, "(bm-c r1084": 1,
    "_w265bmc_freeze_edits_TOL.py template": 1,
    "PERPETUAL_N1_W266_PREREG": 8, "PERPETUAL-N1-W266": 7,
    "n1_w266": 4, "n1_w265": 4, "n1w266-": 2,
    "W266 materializer face": 4, "W265 materializer face": 1,
    "W266 block parity = 121 rows": 1,
    "engine_owner==bm-c rows 84 + candidate": 1,
    "# candidate = 85th EXACT": 1, "; bm-c rows 84 +": 1,
    "bm-c rows {len(bmc_rows_live)} + candidate (85th own wave": 1,
    "bm-c's 85th own wave": 2, "owner_rows=255 / bma_rows=130 / bmc_rows=84": 1,
    '"probe_receipt_bmc_ordinal_face": 84': 1,
    "fourteen-wave": 8, "post-W265-REGISTERED": 8,
    "anchors W265 1,007,335 / K=580,920 at draft": 1,
    "dual-window parity": 1, "W267 walk": 1,
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
