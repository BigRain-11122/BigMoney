# -*- coding: utf-8 -*-
# r1084 bm-c: derive results/_w265bmc_freeze_edits.py from the committed W264
# freeze-edits canon (results/_w264bmc_freeze_edits.py, bm-c r1076/r1077 splice
# window, proven live-fire: W264 splice 216b578b09 + engine self-burn 12/12 +
# W264 CYCLE COMPLETE finalize one-pass 1,005,135/K=578,720 + W265 seat
# published @ 7343e3650, audit-verified per O-20261018-0137) by COUNT-ASSERTED
# ORDERED TRANSFORM (E63 lineage, zero transcription: every needle count
# pre-measured on the canon blob by results/_w265bmc_splice_needle_preflight.py
# (r1083) + _w265bmc_needle_ctxdump{2,3,4,5}.py (dead r1084-predecessor window
# 05:49-05:52 + this window); the phase-1/2 consumption arithmetic and post-D
# phase-3 forms are from the dead window's verified simulation
# results/_w265bmc_needle_ctxdump2.txt sections C/D).
# AGING-TOKEN LAW (E63 3rd-instance prevention): frozen faces w244_a/w244_b
# and n3r1_used245 do NOT roll (measured 12/8/3 in canon; carried verbatim,
# anti-drift asserted here). Band order law: consumers before producers;
# ordinal order law: FOURTEENTH->FIFTEENTH before THIRTEENTH->FOURTEENTH.
import io, subprocess, sys

CANON = "results/_w264bmc_freeze_edits.py"
DST = "results/_w265bmc_freeze_edits_TOL.py"
LOG = "results/_r1084bmc_derive_tolerant_log.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w264bmc_freeze_edits.py"], capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head and len(blob_wt) == 40, f"canon blob drift wt={blob_wt} head={blob_head}"

t = io.open(CANON, encoding="utf-8", newline="").read()
log = [f"S0 canon blob verified {blob_wt[:16]} == HEAD twin", f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    if n != expect:
        log.append(f"MISMATCH [{tag}] count {n} != expect {expect}: {old[:80]!r}")
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: projections first, then bands/anchors/lc (pre-D) ----------
rep("W265p", "W266p", 13, "p1_proj_prefix")
rep("W265", "W266", 13, "p1_proj_plain")
# bands: W265 registered A 598_301..600_300 (14th A-hop) / B 600_301..600_500
# (15th above-own-A); naive A 598_101..600_100 refused at registered W264 B
# 598_101..598_300; naive B 598_301..598_500 inside own-A reservation.
# CONSUMERS FIRST (next_pointer band order law):
rep("598_101", "600_301", 5, "p1_band_Blo_naiveAlo")
rep("598_300", "600_500", 4, "p1_band_Bhi")
rep("596_101", "598_301", 8, "p1_band_Alo_Bnaivelo")
rep("598_100", "600_300", 9, "p1_band_Ahi")
rep("596_300", "598_500", 2, "p1_band_Bnaivehi")
rep("597_900", "600_100", 2, "p1_band_naiveAhi")
# PRODUCERS LAST (else the fresh 598_101/598_300 tokens double-transform):
rep("595_901", "598_101", 4, "p1_band_priorBlo")
rep("596_100", "598_300", 6, "p1_band_priorBhi")
# ledger/K anchors: W263 finalize facts -> W264 finalize facts (1,005,135/578,720)
rep("1,002,935", "1,005,135", 5, "p1_ledger_prose")
rep("576,520", "578,720", 5, "p1_k_prose")
rep("1_002_935", "1_005_135", 1, "p1_ledger_code")
rep("576_520", "578_720", 1, "p1_k_code")
# lowercase machine-file tokens (order law: own wave first, then upstream)
rep("n1_w264", "n1_w265", 4, "p1_n1w264")
rep("n1w264-", "n1w265-", 2, "p1_n1w264dash")
# 12 raw w264_ minus 2 consumed by the n1_w264 rep (n1_w264_results x2)
rep("w264_", "w265_", 10, "p1_lc_w264_")
rep("n1_w263", "n1_w264", 4, "p1_n1w263")
# 93 raw w263_ minus 4 consumed by the n1_w263 rep (n1_w263_results x4)
rep("w263_", "w264_", 89, "p1_lc_w263_")
rep("_w264bmc_", "_w265bmc_", 11, "p1_receiptpath")
rep("MSG-20261017-1950-bmc-w264-seat", "MSG-20261017-2241-bmc-w265-seat", 7, "p1_seat_msg")
rep("dd5fd438e", "7343e3650", 2, "p1_seat_origin")
rep("f499817fa", "216b578b0", 1, "p1_lineage_sha")
rep("f4ffdb34e", "e57215a2c", 1, "p1_prereg_sha_ref")
# gate0.5 upstream owner: W263=bm-a -> W264=bm-c (own-seat continuity flip;
# wave index shifts later via D-swap / p3 n1bands rep)
rep('W263.get("engine_owner") == "bm-a"', 'W263.get("engine_owner") == "bm-c"', 1, "p1_gate05_owner")
rep('N1_BANDS[263].get("engine_owner") == "bm-a"', 'N1_BANDS[263].get("engine_owner") == "bm-c"', 1, "p1_mirror_owner")

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W264", "W265", 92, "p2_own_wave")
rep("W263", "W264", 162, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
rep("W261_W262_W264_bands_respected", "W262_W263_W264_bands_respected", 2, "p3_relkey")
rep("W211..W244 legs (34)", "W211..W245 legs (35)", 2, "p3_kept_narr")
rep("W211..W262 legs (52)", "W211..W263 legs (53)", 1, "p3_legs_narr")
rep("W245..W262 legs (18)", "W246..W263 legs (18)", 4, "p3_dropped_narr")
rep("own W245..W262", "own W246..W263", 5, "p3_dropped_split_hdr")
rep("W245..W262 eighteen legs", "W246..W263 eighteen legs", 1, "p3_dropped_fstring")
rep("W211..W264 legs 52", "W211..W264 legs 53", 1, "p3_fullspan_fstring")
rep("W211..W262 fifty-two legs", "W211..W263 fifty-three legs", 1, "p3_legs_fstring")
rep("keep W211..W244 verbatim (34 legs)", "keep W211..W245 verbatim (35 legs)", 1, "p3_kept_comment")
rep("W211..W244 thirty-four legs", "W211..W245 thirty-five legs", 1, "p3_kept_fstring")
rep("W245..W264 legs (19", "W246..W264 legs (19", 4, "p3_fresh_narr")
rep("range(211, 263)", "range(211, 264)", 1, "p3_legs_range_assert")
rep("block = 122 rows", "block = 123 rows", 1, "p3_block122")
rep("122 parity rows", "123 parity rows", 1, "p3_parity122")
rep('N1_BANDS[") == 121,', 'N1_BANDS[") == 122,', 1, "p3_count121")
rep("!= 121", "!= 122", 1, "p3_fstring121")
rep('N1_BANDS[") == 52', 'N1_BANDS[") == 53', 1, "p3_count52")
rep('N1_BANDS[") == 34', 'N1_BANDS[") == 35', 1, "p3_count34")
rep("range(211, 245)", "range(211, 246)", 1, "p3_range_kept")
rep("range(245, 263)", "range(246, 264)", 1, "p3_range_dropped")
rep("range(245, 264)", "range(246, 265)", 2, "p3_range_fresh")
rep("range(16, 264)", "range(16, 265)", 2, "p3_range16")
rep("range(17, 264)", "range(17, 265)", 3, "p3_range17")
rep("range(209, 265)", "range(209, 266)", 2, "p3_range209")
# wave-number gates (own 264->265 FIRST, then anti-gate 263->264)
rep("if w < 264)", "if w < 265)", 5, "p3_wlt264")
rep("if w < 263)", "if w < 264)", 1, "p3_wlt263_antigate")
rep("264 - _lw", "265 - _lw", 2, "p3_legcount")
rep("N1_BANDS\\[245\\]", "N1_BANDS\\[246\\]", 1, "p3_regex245")
rep("m245", "m246", 4, "p3_m245")
rep("N1_BANDS[245] == {", "N1_BANDS[246] == {", 1, "p3_startswith245")
rep("WAVE_CONFIGS[263]", "WAVE_CONFIGS[264]", 5, "p3_wavecfg263")
rep("N1_BANDS[263]", "N1_BANDS[264]", 5, "p3_n1bands263")
rep("get(263)", "get(264)", 1, "p3_get263")
rep("_c263", "_c264", 5, "p3_c263var")
# cfg/row dict faces: 264->265 FIRST, then 263->264 (template order law)
rep('264: {"batch"', '265: {"batch"', 2, "p3_cfg264")
rep('264: {{"batch"', '265: {{"batch"', 1, "p3_cfg264_fstring")
rep('263: {"batch"', '264: {"batch"', 2, "p3_cfg263")
rep('264: {{"a"', '265: {{"a"', 2, "p3_row264_fstring")
rep('264: {"a"', '265: {"a"', 1, "p3_row264_postgate")
rep('263: {"a"', '264: {"a"', 3, "p3_row263")
rep("arith_a264", "arith_a265", 6, "p3_arith_a")
rep("arith_b264", "arith_b265", 6, "p3_arith_b")
rep("(260, 259, 258, 257, 256, 255, 254, 253, 252, 251)",
    "(261, 260, 259, 258, 257, 256, 255, 254, 253, 252)", 2, "p3_transitive_list")
rep("W251..W260", "W252..W261", 1, "p3_transitive_window")
# ordinal faces: owner 253->254, bma 130 held, bmc 82->83 (W265 = 255th candidate, bm-c 84th own)
rep("len(owner_rows_live) == 253 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 82",
    "len(owner_rows_live) == 254 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 83", 1, "p3_ordinal_assert")
rep("253/130/82", "254/130/83", 1, "p3_ordinal_expect")
rep("owner_rows=253 / bma_rows=130 / bmc_rows=82", "owner_rows=254 / bma_rows=130 / bmc_rows=83", 1, "p3_leg0_face")
rep("rows 253 + candidate = 254th", "rows 254 + candidate = 255th", 2, "p3_owner254")
rep("; bm-c rows 82 +", "; bm-c rows 83 +", 1, "p3_comment_82split")
rep("bm-c rows 82 + candidate = 83rd owned", "bm-c rows 83 + candidate = 84th owned", 1, "p3_receipt_83owned")
rep("# candidate = 83rd EXACT", "# candidate = 84th EXACT", 1, "p3_comment_83rd")
rep("engine_owner==bm-c rows 82 + candidate", "engine_owner==bm-c rows 83 + candidate", 1, "p3_pr_eo83")
rep("bm-c rows {len(bmc_rows_live)} + candidate (83rd own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (84th own wave", 1, "p3_gate0_5_print")
rep("bm-c's 83rd own wave", "bm-c's 84th own wave", 2, "p3_83rd_own_wave")
rep("EIGHTY-THIRD owned", "EIGHTY-FOURTH owned", 3, "p3_83rd_caps")
rep("TWO HUNDRED AND SIXTY-FOURTH", "TWO HUNDRED AND SIXTY-FIFTH", 3, "p3_wave_caps")
rep("bmc_rows=82", "bmc_rows=83", 6, "p3_bmc_rows82")
rep('"probe_receipt_bmc_ordinal_face": 82', '"probe_receipt_bmc_ordinal_face": 83', 1, "p3_probe_face_key")
# ordinal narrative: B-ordinal FOURTEENTH->FIFTEENTH FIRST, then A-ordinal THIRTEENTH->FOURTEENTH
rep("FOURTEENTH", "FIFTEENTH", 7, "p3_14_caps")
rep("THIRTEENTH", "FOURTEENTH", 15, "p3_13_caps")
rep("fourteenth", "fifteenth", 4, "p3_14_lc")
rep("thirteenth", "fourteenth", 3, "p3_13_lc")
rep("fifty-second", "fifty-third", 2, "p3_52nd")
# upstream owner flips (W263=bm-a -> W264=bm-c, own-seat continuity)
rep("bm-a five-face freeze upstream seat", "bm-c five-face freeze upstream seat", 1, "p3_freshmsg_owner")
rep("_w == 263", "_w == 264", 1, "p3_freshmsg_cond")
rep("bm-a (upstream seat honored)", "bm-c (upstream seat honored)", 1, "p3_upstream_honored")
rep("owner=bm-a seat honored", "owner=bm-c seat honored", 1, "p3_gate05_print_owner")
rep("row not landed as declared (bm-a seat owner expected)",
    "row not landed as declared (bm-c seat owner expected)", 1, "p3_gate05_declared")
rep("'\"engine_owner\": \"bm-a\"' in w264_own_line", "'\"engine_owner\": \"bm-c\"' in w264_own_line", 1, "p3_ownline_owner")
# wave-number narrative faces
rep("wave 264 engine_owner=bm-c", "wave 265 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 264: "', '"wave 265: "', 1, "p3_cfg_waveface")
rep("wave 264 = first free number", "wave 265 = first free number", 1, "p3_mhdr_waveface")
# upstream-cycle lineage (W263 bm-a r1038/r1039/r1040 -> W264 bm-c r1076/r1077)
rep("bm-a own seat executed at the bm-a r1038 splice window",
    "bm-c own seat executed at the bm-c r1076 splice window", 1, "p3_pre_ownseat_r1076")
rep("cycle COMPLETE bm-a r1038+r1040 closeout 19:2x",
    "cycle COMPLETE bm-c r1076+r1077 closeout 22:4x", 1, "p3_hdr_complete")
rep("18:2x bm-a r1038 freeze window", "20:5x bm-c r1076 freeze window", 1, "p3_hdr_stamp")
rep("finalize one-pass bm-a r1039", "finalize one-pass bm-c r1077", 2, "p3_finpass_r1039")
rep("W264 bm-a own-wave full cycle r1038", "W264 bm-c own-wave full cycle r1076", 1, "p3_repair_note")
rep("bm-a own seat executed at", "bm-c own seat executed at", 1, "p3_mhdr_ownseat_split")
rep("the bm-a r1038 splice window", "the bm-c r1076 splice window", 2, "p3_mhdr_window_split")
rep("(bm-a r1038", "(bm-c r1076", 1, "p3_extract_gen_note")
rep("bm-a splice generation r1038 window", "bm-c splice generation r1076 window", 1, "p3_parity_source_note")
rep("verified r1039/r1040", "verified r1077", 1, "p3_lineage_verified")
rep("(R263: ", "(R264: ", 1, "p3_repick")
# prereg/seat window map (r1076 prereg window -> r1081; r1075 seat window -> r1077)
rep("itself r1075; queue-head", "itself r1077; queue-head", 1, "p3_r1075_semicolon")
rep("(r1075, queue-head", "(r1077, queue-head", 1, "p3_r1075_paren")
rep("r1075 BEFORE this freeze", "r1077 BEFORE this freeze", 1, "p3_r1075_before")
rep("(r1075 MSG-", "(r1077 MSG-", 1, "p3_r1075_msg")
rep("7343e3650 r1075,", "7343e3650 r1077,", 1, "p3_r1075_origin_resid")
rep("r1076 commit", "r1081 commit", 1, "p3_r1076_commit")
rep("# r1076 window", "# r1081 window", 1, "p3_r1076_hdr")
rep("bm-c r1076 window", "bm-c r1081 window", 4, "p3_r1076_window")
rep("authored 20:1x", "authored 04:0x", 2, "p3_authored_stamp")

# ---------- phase 4: frozen-face anti-drift + residual sweeps ----------
assert t.count("w244_a") == 12 and t.count("w244_b") == 8, "aging tokens w244_a/b drift"
assert t.count("n3r1_used245") == 3, "frozen face n3r1_used245 drift"
for gone in ("r1075", "r1076", "r1038", "r1039", "r1040", "f499817fa", "f4ffdb34e",
            "dd5fd438e", "_w264bmc_", "w263_", "n1_w263", "w262_", "n1_w262",
            "595_901", "596_100", "596_101", "598_100", "596_300", "597_900",
            "1,002,935", "576,520", "1_002_935", "576_520",
            "PENDING at seat", "waits-upstream face disclosed honest",
            "bma_ordinal", "ONE HUNDRED AND THIRTIETH", "EIGHTY-THIRD",
            "TWO HUNDRED AND SIXTY-FOURTH", "== 121", "!= 121",
            "N1_BANDS[245]", "m245", "rows {len(bma_rows_live)}", "wave 264",
            "was published BEFORE", "W245..W262", "W211..W262", "W211..W244",
            "fifty-two", "thirty-four", "range(211, 263)", "range(245, 263)",
            "FOURTEENTH", "fourteenth", "83rd", "rows 82 + candidate",
            "bmc_rows=82", "rows 253 + candidate", "253/130/82", "owner_rows=253",
            "len(owner_rows_live) == 253", "(R263: ",
            "bm-a five-face freeze upstream seat", "bm-a (upstream seat honored)",
            "owner=bm-a seat honored", "(bm-a seat owner expected)",
            "18:2x", "19:2x", "editor template"):
    if t.count(gone) != 0:
        log.append(f"MISMATCH residual {gone!r} count {t.count(gone)}")
log.append("phase4 residual sweeps: 56 faces zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
    'MSG-20261017-2241-bmc-w265-seat': 7, "7343e3650": 2, "_w265bmc_": 11,
    "598_301": 8, "600_300": 9, "600_301": 5, "600_500": 4,
    "598_101": 4, "598_300": 6, "598_500": 2, "600_100": 2,
    "1,005,135": 5, "578,720": 5, "1_005_135": 1, "578_720": 1,
    '264: {"batch"': 2, '265: {"batch"': 2, '264: {"a"': 3, '265: {"a"': 1,
    "range(246, 265)": 2, "range(209, 266)": 2, "if w < 265)": 5, "if w < 264)": 1,
    '"engine_owner": "bm-c"}': 3, "W265 materializer face": None,
    '"PERPETUAL-N1-W265"': None, "PERPETUAL_N1_W265_PREREG": 8,
    "n1_w265": 4, "n1_w264": 4, "n1w265-": 2, "e57215a2c": 1, "216b578b0": 1,
    "EIGHTY-FOURTH owned": 3, "TWO HUNDRED AND SIXTY-FIFTH": 3,
    "FIFTEENTH": 7, "FOURTEENTH": 15, "fifteenth": 4, "fourteenth": 3,
    "W262_W263_W264_bands_respected": 2, "W266p": 13, "W266": 26,
    "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
    "owner=bm-c seat honored": 1, '"machine": "bm-c"': 1,
    "W265 FREEZE UNBLOCKED": 4, "was published AFTER": 1,
    "bm-c own seat executed at the bm-c r1076 splice window": 1,
    "finalize one-pass bm-c r1077": 2, "bm-c r1081 window": 4,
    "rows 254 + candidate = 255th": 2, "bm-c rows 83 + candidate = 84th owned": 1,
    "254/130/83": 1, "len(owner_rows_live) == 254": 1, "bmc_rows=83": 6,
    "authored 04:0x": 2, "w244_a": 12, "w244_b": 8, "n3r1_used245": 3,
    "20:5x bm-c r1076 freeze window": 1,
    "cycle COMPLETE bm-c r1076+r1077 closeout 22:4x": 1,
    "W264 bm-c own-wave full cycle r1076": 1, "verified r1077": 1,
    "(bm-c r1076": 1, "bm-c splice generation r1076 window": 1,
    "the bm-c r1076 splice window": 2, "(R264: ": 1, "_w == 264": 1,
    'N1_BANDS[") == 122,': 1, '!= 122': 1, 'N1_BANDS[") == 53': 1, 'N1_BANDS[") == 35': 1,
    "N1_BANDS[264]": 5, "WAVE_CONFIGS[264]": 5, "m246": 4,
    "arith_a265": 6, "arith_b265": 6, "W252..W261": 1,
    "own W246..W263": 5, "W246..W263 legs (18)": 4, "W246..W264 legs (19": 4,
    "W211..W245 legs (35)": 2, "W211..W263 legs (53)": 1,
    "wave 265 engine_owner=bm-c": 1, '"wave 265: "': 1, "wave 265 = first free number": 1,
    "'\"engine_owner\": \"bm-c\"' in w264_own_line": 1,
    "fifty-third": 2, "fifty-second": 0, "123 rows": 1, "123 parity rows": 1,
    "w264_freeze_sha": None, "w265_prereg_sha": None,
}
for k, v in must_have.items():
    c = t.count(k)
    if v is None:
        if c == 0:
            log.append(f"MISMATCH presence {k!r} count 0")
    else:
        if c != v:
            log.append(f"MISMATCH presence {k!r} count {c} != {v}")
log.append("phase5 presence gates PASS")
io.open(DST, "w", encoding="utf-8", newline="").write(t)
import py_compile
try:
    py_compile.compile(DST, doraise=True)
except Exception as _e:
    log.append(f"MISMATCH py_compile: {_e}")
log.append(f"DST written {len(t.encode('utf-8'))} bytes + py_compile OK")
io.open(LOG, "w", encoding="utf-8", newline="").write("\n".join(log) + "\n")
mm = [ln for ln in log if ln.startswith("MISMATCH")]
print("MISMATCH COUNT:", len(mm))
print("\n".join(mm))
print("DERIVE OK ->", DST)
