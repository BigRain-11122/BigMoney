# -*- coding: utf-8 -*-
# r1083 bm-c: W265 five-face splice PREFLIGHT needle probe (r787 law).
# Measures every planned W265-derive needle's count on the committed canon
# results/_w264bmc_freeze_edits.py (bm-c W264 splice window r1076/r1077,
# proven live-fire: W264 CYCLE COMPLETE + W265 seat published @ 7343e3650,
# finalize ledger 1,005,135 / K=578,720 landed) BEFORE the derive script is
# authored. Zero transcription: counts printed, derive asserts against these
# measured values. Expected values (where noted) = r1076 derive rep counts
# (the W264 canon was written by that derive, so token counts are its
# NEW-value counts). Phase-3 needles are measured RAW here; the derive author
# must apply D-swaps (W264->W265 x87, W263->W264 x167) FIRST and re-derive
# the post-D needle forms (r1076 preflight postD/preD_check law).
import io, subprocess, sys, re

CANON = "results/_w264bmc_freeze_edits.py"
OUT = "results/_w265bmc_splice_needle_counts.txt"
blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w264bmc_freeze_edits.py"], capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head and len(blob_wt) == 40, f"canon blob drift wt={blob_wt} head={blob_head}"
t = io.open(CANON, encoding="utf-8", newline="").read()
lines = ["canon blob %s bytes %d (HEAD twin verified)" % (blob_wt[:16], len(t.encode('utf-8')))]

# (needle, tag, expected_or_None)  expected = r1076 NEW-value count when known
NEEDLES = [
 # phase 1: projections first (W265->W266 before own-wave W264->W265 D-swap)
 ("W265p", "p1_proj_prefix", 13),
 ("W265", "p1_proj_plain_raw_incl_p", 26),  # 13 pure + 13 inside W265p
 # bands (mapped for W265: A 598_301..600_300 / B 600_301..600_500;
 # naive A 598_101..600_100 refused at registered W264 B 598_101..598_300;
 # B naive 598_301..598_500 inside own-A reservation)
 ("598_101", "p1_band_Blo_naiveAlo", 5),
 ("598_300", "p1_band_Bhi", 4),
 ("596_101", "p1_band_Alo_Bnaivelo", 8),
 ("598_100", "p1_band_Ahi", 9),
 ("596_300", "p1_band_Bnaivehi", 2),
 ("597_900", "p1_band_naiveAhi", 2),
 ("595_901", "p1_band_priorBlo_W263", 4),
 ("596_100", "p1_band_priorBhi_W263", 6),
 # ledger/K anchors (W263 finalize -> W264 finalize facts)
 ("1,002,935", "p1_ledger_prose_W263fin", 5),
 ("576,520", "p1_k_prose_W263fin", 5),
 ("1_002_935", "p1_ledger_code", 1),
 ("576_520", "p1_k_code", 1),
 ("1,005,135", "p1_ledger_W264fin_present_check", None),
 ("578,720", "p1_k_W264fin_present_check", None),
 # lowercase machine-file tokens
 ("n1_w264", "p1_n1w264", 4),
 ("n1w264-", "p1_n1w264dash", 2),
 ("n1_w263", "p1_n1w263", 4),
 ("w264_", "p1_lc_w264_raw", 12),  # 10 pure + 2 inside n1_w264_results.json
 ("w263_", "p1_lc_w263_", 89),
 ("_w264bmc_", "p1_receiptpath", 11),
 ("MSG-20261017-1950-bmc-w264-seat", "p1_seat_msg", 7),
 ("MSG-20261017-2241-bmc-w265-seat", "p1_seat_msg_next_present_check", None),
 ("dd5fd438e", "p1_seat_origin_W264", 2),
 ("7343e3650", "p1_seat_origin_W265_present_check", None),
 ("f499817fa", "p1_lineage_sha_W263splice", 1),
 ("e57215a2c", "p1_prereg_sha_W265_present_check", None),
 ("f4ffdb34e", "p1_prereg_sha_W264", 1),
 # phase 2: D-swaps
 ("W264", "p2_own_wave_raw_incl_paths", 98),  # 87 own + 11 inside _w264bmc_ paths (paths consumed phase-1 first)
 ("W263", "p2_upstream_wave_raw", 167),  # + relkey/faces noted postD below
 # phase 3: contextual (RAW canon counts; post-D forms recomputed by derive author)
 ("W261_W262_W263_bands_respected", "p3_relkey", 2),
 ("W211..W244 legs (34)", "p3_kept_narr", 2),
 ("W211..W262 legs (52)", "p3_legs_narr", 1),
 ("W245..W262 legs (18)", "p3_dropped_narr", 4),
 ("own W245..W262", "p3_dropped_split_hdr", 1),
 ("W245..W262 eighteen legs", "p3_dropped_fstring", 1),
 ("W211..W263 legs 52", "p3_fullspan_fstring", 1),
 ("range(211, 245)", "p3_range_kept", 1),
 ("range(245, 263)", "p3_range_dropped", 1),
 ("range(245, 264)", "p3_range_fresh", 2),
 ("range(16, 264)", "p3_range16", 2),
 ("range(17, 264)", "p3_range17", 3),
 ("range(209, 265)", "p3_range209", 2),
 ("if w < 264)", "p3_wlt264", 5),
 ("if w < 263)", "p3_wlt263_antigate", 1),
 ("264 - _lw", "p3_legcount", 2),
 ("N1_BANDS\\[245\\]", "p3_regex245", 1),
 ("m245", "p3_m245", 4),
 ("N1_BANDS[245] == {", "p3_startswith245", 1),
 ("WAVE_CONFIGS[263]", "p3_wavecfg263", 3),
 ("N1_BANDS[263]", "p3_n1bands263", 5),
 ("get(263)", "p3_get263", 1),
 ("_c263", "p3_c263var", 5),
 ('264: {"batch"', "p3_cfg264", 2),
 ('264: {{"batch"', "p3_cfg264_fstring", 1),
 ('263: {"batch"', "p3_cfg263", 2),
 ('264: {{"a"', "p3_row264_fstring", 2),
 ('264: {"a"', "p3_row264_postgate", 1),
 ('263: {"a"', "p3_row263", 3),
 ("arith_a264", "p3_arith_a", 6),
 ("arith_b264", "p3_arith_b", 6),
 ("(260, 259, 258, 257, 256, 255, 254, 253, 252, 251)", "p3_transitive_list", 2),
 ("W251..W260", "p3_transitive_window", 1),
 ("len(owner_rows_live) == 253 and len(bma_rows_live) == 130", "p3_ordinal_assert", 1),
 ("253/130/82", "p3_ordinal_expect", 1),
 ("owner_rows=253 / bma_rows=130", "p3_leg0_face", 1),
 ("rows 253 + candidate = 254th", "p3_owner254", 2),
 ("bm-c rows 82 + candidate", "p3_bmc82", None),
 ("bm-c rows 83", "p3_bmc83_check", None),
 ("EIGHTY-THIRD owned", "p3_83rd_caps", 3),
 ("EIGHTY-FOURTH", "p3_84th_check", None),
 ("83rd own wave", "p3_83rd_own", 2),
 ("84th own", "p3_84th_own_check", None),
 ("TWO HUNDRED AND SIXTY-FOURTH", "p3_wave264_caps", 3),
 ("TWO HUNDRED AND SIXTY-FIFTH", "p3_wave265_caps_check", None),
 ("FOURTEENTH", "p3_14_caps_B_ordinal", None),
 ("THIRTEENTH", "p3_13_caps_A_ordinal", 7),
 ("FIFTEENTH", "p3_15_check", None),
 ("fourteenth", "p3_14_lc", None),
 ("thirteenth", "p3_13_lc", 4),
 ("fifteenth", "p3_15_lc_check", None),
 ("fifty-second", "p3_52nd", 2),
 ("fifty-third", "p3_53rd_check", None),
 ("255th", "p3_255th_check", None),
 ("254th", "p3_254th", None),
 # machine/narrative ownership faces (raw; derive author re-checks post-D)
 ('"engine_owner": "bm-c"}', "p3_ownowner_bm_c", 3),
 ('W262.get("engine_owner") == "bm-a"', "p3_gate05_owner_W262_bma", 1),
 ('N1_BANDS[262].get("engine_owner") == "bm-a"', "p3_mirror_owner_W262_bma", 1),
 ('W263.get("engine_owner")', "p3_gate05_W263_check", None),
 ('N1_BANDS[263].get("engine_owner")', "p3_mirror_W263_check", None),
 ("waits-upstream face disclosed honest", "p3_waits_honest_resid", 0),
 ("W264 FREEZE UNBLOCKED", "p3_unblocked_narr", None),
 ("W265 FREEZE UNBLOCKED", "p3_unblocked_W265_check", None),
 ("was published AFTER", "p3_pub_after", None),
 ("authored 20:1x", "p3_authored_stamp", 2),
 ("r1076 window", "p3_r1076_window", None),
 ("r1075", "p3_r1075_refs", None),
 ("r1083", "p3_r1083_check", 0),
 ("f499817fac26786ca3c8b0726aa54c0aa31c2bd2", "p1_lineage_sha_full", 1),
 ("29276fbfb30abcfd0e3edff0941e0d145789fabe", "p1_w264_origin_base", None),
 ("7343e3650", "p1_w265_seat_origin_ref", None),
]
for old, tag, exp in NEEDLES:
    c = t.count(old)
    mark = ""
    if exp is not None:
        mark = " OK" if c == exp else " **EXPECT %d**" % exp
    lines.append("%s\t%d%s\t%r" % (tag, c, mark, old[:70]))

# ctxdumps for the ambiguous faces (derive author inputs)
lines.append("")
lines.append("=== CTDUMP: engine_owner gate/mirror/owner lines ===")
for i, ln in enumerate(t.split("\n")):
    if "engine_owner" in ln:
        lines.append("L%d: %s" % (i + 1, ln.strip()[:200]))
lines.append("")
lines.append("=== CTDUMP: authored/stamp lines ===")
for i, ln in enumerate(t.split("\n")):
    if "authored" in ln or "20:1x" in ln or "22:4x" in ln:
        lines.append("L%d: %s" % (i + 1, ln.strip()[:200]))
lines.append("")
lines.append("=== CTDUMP: rows/ordinal assert lines ===")
for i, ln in enumerate(t.split("\n")):
    if re.search(r"(owner_rows|rows_live|candidate = |own wave|ordinal)", ln):
        lines.append("L%d: %s" % (i + 1, ln.strip()[:200]))
lines.append("")
lines.append("=== CTDUMP: 40-hex sha tokens in canon ===")
for m in sorted(set(re.findall(r"\b[0-9a-f]{40}\b", t))):
    lines.append("SHA: %s (x%d)" % (m, t.count(m)))
lines.append("")
lines.append("=== CTDUMP: UNBLOCKED/waits narrative lines ===")
for i, ln in enumerate(t.split("\n")):
    if "UNBLOCKED" in ln or "waits-upstream" in ln or "PENDING at seat" in ln:
        lines.append("L%d: %s" % (i + 1, ln.strip()[:200]))
lines.append("PREFLIGHT DONE (r1083 splice-prep; counts measured, derive asserts against these)")
io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
print("\n".join(lines[:14]))
print("...")
print("\n".join(lines[-6:]))
print("WROTE", OUT, "total lines", len(lines))
