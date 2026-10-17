# -*- coding: utf-8 -*-
# r1076 bm-c: derive results/_w264bmc_freeze_edits.py from the committed W263
# freeze-edits canon (results/_w263bma_freeze_edits.py, bm-a r1038 splice
# window, proven live-fire f499817fa + engine self-burn 12/12 + finalize
# one-pass 1,002,935/K=576,520 verified r1039/r1040) by COUNT-ASSERTED
# ORDERED TRANSFORM (E63 lineage, zero transcription: every needle count
# pre-measured on the canon blob by results/_w264bmc_freeze_needle_preflight.py
# + _w264bmc_freeze_needle_ctxdump{,2,3,4}.py this window; the new-generation
# narrative replacement values are full-line surgical swaps).
# AGING-TOKEN LAW (E63 3rd-instance prevention): frozen faces w244_a/w244_b
# and n3r1_used245 do NOT roll (W262 canon carries the identical tokens --
# measured 12/8/3 there; carried verbatim, anti-drift asserted here).
import io, subprocess, sys

CANON = "results/_w263bma_freeze_edits.py"
DST = "results/_w264bmc_freeze_edits.py"
LOG = "results/_r1076bmc_derive_freeze_log.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w263bma_freeze_edits.py"], capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head and len(blob_wt) == 40, f"canon blob drift wt={blob_wt} head={blob_head}"

t = io.open(CANON, encoding="utf-8", newline="").read()
log = [f"S0 canon blob verified {blob_wt[:16]} == HEAD twin", f"bytes {len(t.encode('utf-8'))}"]

def rep(old, new, expect, tag):
    global t
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:100]!r}"
    t = t.replace(old, new)
    log.append(f"{tag}: {n}x")

# ---------- phase 1: prefixed/lowercase/band/anchor/projection needles ----------
rep("W264p", "W265p", 13, "p1_proj_prefix")
rep("W264", "W265", 13, "p1_proj_plain")
rep("595_901", "598_101", 5, "p1_band_Blo")
rep("596_100", "598_300", 4, "p1_band_Bhi")
rep("593_701", "595_901", 4, "p1_band_priorBlo_naiveAlo")
rep("593_900", "596_100", 6, "p1_band_priorBhi")
rep("595_700", "597_900", 2, "p1_band_naiveAhi")
rep("593_901", "596_101", 8, "p1_band_Alo_Bnaivelo")
rep("594_100", "596_300", 2, "p1_band_Bnaivehi")
rep("595_900", "598_100", 9, "p1_band_Ahi")
rep("1,000,735", "1,002,935", 5, "p1_ledger_prose")
rep("574,320", "576,520", 5, "p1_k_prose")
rep("1_000_735", "1_002_935", 1, "p1_ledger_code")
rep("574_320", "576_520", 1, "p1_k_code")
rep("n1_w263", "n1_w264", 4, "p1_n1w263")
rep("n1w263-", "n1w264-", 2, "p1_n1w263dash")
# order law: w263_->w264_ MUST run before n1_w262_->n1_w263_ (else the 2 new
# n1_w263_results.json tokens get mis-aged; A above already consumed the 2
# canon n1_w263_results tokens -> expect 10 = 12 measured minus 2)
rep("w263_", "w264_", 10, "p1_lc_w263_")
rep("n1_w262", "n1_w263", 4, "p1_n1w262")
rep("w262_", "w263_", 89, "p1_lc_w262_")
rep("_w263bma_", "_w264bmc_", 11, "p1_receiptpath")
rep("MSG-20261017-1740-bma-w263-seat", "MSG-20261017-1950-bmc-w264-seat", 7, "p1_seat_msg")
rep("fb0c962b5", "dd5fd438e", 2, "p1_seat_origin")
rep("e1a94b335", "f499817fa", 1, "p1_lineage_sha")
rep("b32f6bf1c", "f4ffdb34e", 1, "p1_prereg_sha_ref")
rep('W262.get("engine_owner") == "bm-c"', 'W262.get("engine_owner") == "bm-a"', 1, "p1_gate05_owner")
rep('N1_BANDS[262].get("engine_owner") == "bm-c"', 'N1_BANDS[262].get("engine_owner") == "bm-a"', 1, "p1_mirror_owner")

# ---------- phase 2: D-swaps (own wave first, then upstream wave) ----------
rep("W263", "W264", 87, "p2_own_wave")
rep("W262", "W263", 167, "p2_upstream_wave")

# ---------- phase 3: post-D contextual needles ----------
rep("W260_W261_W263_bands_respected", "W261_W262_W263_bands_respected", 2, "p3_relkey")
rep("W211..W243 legs (33)", "W211..W244 legs (34)", 2, "p3_kept_narr")
rep("W211..W261 legs (51)", "W211..W262 legs (52)", 1, "p3_legs_narr")
rep("W244..W261 legs (18)", "W245..W262 legs (18)", 4, "p3_dropped_narr")
rep("own W244..W261", "own W245..W262", 1, "p3_dropped_split_hdr")
rep("W244..W261 eighteen legs", "W245..W262 eighteen legs", 1, "p3_dropped_fstring")
rep("W211..W263 legs 51", "W211..W263 legs 52", 1, "p3_fullspan_fstring")
rep("range(211, 262)", "range(211, 263)", 1, "p3_legs_range_assert")
rep("W211..W261 fifty-one legs", "W211..W262 fifty-two legs", 1, "p3_legs_fstring")
rep("keep W211..W243 verbatim (33 legs)", "keep W211..W244 verbatim (34 legs)", 1, "p3_kept_comment")
rep("W211..W243 thirty-three legs", "W211..W244 thirty-four legs", 1, "p3_kept_fstring")
rep("W244..W263 legs (19", "W245..W263 legs (19", 4, "p3_fresh_narr")
rep("block = 121 rows", "block = 122 rows", 1, "p3_block121")
rep("121 parity rows", "122 parity rows", 1, "p3_parity121")
rep('N1_BANDS[") == 120,', 'N1_BANDS[") == 121,', 1, "p3_count120")
rep("!= 120", "!= 121", 1, "p3_fstring120")
rep('N1_BANDS[") == 51', 'N1_BANDS[") == 52', 1, "p3_count51")
rep('N1_BANDS[") == 33', 'N1_BANDS[") == 34', 1, "p3_count33")
rep("range(211, 244)", "range(211, 245)", 1, "p3_range_kept")
rep("range(244, 262)", "range(245, 263)", 1, "p3_range_dropped")
rep("range(244, 263)", "range(245, 264)", 2, "p3_range_fresh")
rep("range(16, 263)", "range(16, 264)", 2, "p3_range16")
rep("range(17, 263)", "range(17, 264)", 3, "p3_range17")
rep("range(209, 264)", "range(209, 265)", 2, "p3_range209")
rep("if w < 263)", "if w < 264)", 5, "p3_wlt263")
rep("if w < 262)", "if w < 263)", 1, "p3_wlt262_antigate")
rep("263 - _lw", "264 - _lw", 2, "p3_legcount")
rep("N1_BANDS\\[244\\]", "N1_BANDS\\[245\\]", 1, "p3_regex244")
rep("m244", "m245", 4, "p3_m244")
rep("N1_BANDS[244] == {", "N1_BANDS[245] == {", 1, "p3_startswith244")
rep("WAVE_CONFIGS[262]", "WAVE_CONFIGS[263]", 3, "p3_wavecfg262")
rep("N1_BANDS[262]", "N1_BANDS[263]", 5, "p3_n1bands262")
rep("'\"engine_owner\": \"bm-c\"' in w263_own_line", "'\"engine_owner\": \"bm-a\"' in w263_own_line", 1, "p3_ownline_owner")
rep("get(262)", "get(263)", 1, "p3_get262")
rep("_c262", "_c263", 5, "p3_c262var")
rep('263: {"batch"', '264: {"batch"', 2, "p3_cfg263")
rep('263: {{"batch"', '264: {{"batch"', 1, "p3_cfg263_fstring")
rep('262: {"batch"', '263: {"batch"', 2, "p3_cfg262")
rep('263: {{"a"', '264: {{"a"', 2, "p3_row263_fstring")
rep('263: {"a"', '264: {"a"', 1, "p3_row263_postgate")
rep('262: {"a"', '263: {"a"', 3, "p3_row262")
rep("arith_a263", "arith_a264", 6, "p3_arith_a")
rep("arith_b263", "arith_b264", 6, "p3_arith_b")
rep("(259, 258, 257, 256, 255, 254, 253, 252, 251, 250)",
    "(260, 259, 258, 257, 256, 255, 254, 253, 252, 251)", 2, "p3_transitive_list")
rep("W250..W259", "W251..W260", 1, "p3_transitive_window")
# ordinal faces
rep("len(owner_rows_live) == 252 and len(bma_rows_live) == 129",
    "len(owner_rows_live) == 253 and len(bma_rows_live) == 130", 1, "p3_ordinal_assert")
rep("252/129/82", "253/130/82", 1, "p3_ordinal_expect")
rep("owner_rows=252 / bma_rows=129 / bma_ordinal=130",
    "owner_rows=253 / bma_rows=130 / bmc_rows=82", 1, "p3_leg0_face")
rep("rows 252 + candidate = 253rd", "rows 253 + candidate = 254th", 2, "p3_owner253")
rep("; bm-a rows 129 +", "; bm-c rows 82 +", 1, "p3_comment_129split")
rep("# candidate = 130th EXACT", "# candidate = 83rd EXACT", 1, "p3_comment_130th")
rep("bm-a rows 129 + candidate = 130th owned", "bm-c rows 82 + candidate = 83rd owned", 1, "p3_receipt_129owned")
rep("engine_owner==bm-a rows 129 + candidate", "engine_owner==bm-c rows 82 + candidate", 1, "p3_pr_eo129")
rep('engine_owner==bm-a rows "', 'engine_owner==bm-c rows "', 1, "p3_pre_eo_fstring")
rep("{len(bma_rows_live)} + candidate; probe receipt leg0",
    "{len(bmc_rows_live)} + candidate; probe receipt leg0", 1, "p3_pre_len_fstring")
rep("rows {len(bma_rows_live)} + candidate; own-seat face",
    "rows {len(bmc_rows_live)} + candidate; own-seat face", 1, "p3_mhdr_len_fstring")
rep("bm-a rows {len(bma_rows_live)} + candidate (130th own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (83rd own wave", 1, "p3_gate0_5_print")
rep("bm-a's 130th own wave", "bm-c's 83rd own wave", 2, "p3_130th_own_wave")
rep("bm-a own-seat continuity", "bm-c own-seat continuity", 2, "p3_ownseat_cont")
rep('continuity, waits-upstream face disclosed honest)"}', 'continuity, zero waits-upstream face)"}', 1, "p3_ordnote_waits_resid")
rep("(bm-a published the", "(bm-c published the", 1, "p3_published_by")
rep('ONE HUNDRED AND THIRTIETH owned', 'EIGHTY-THIRD owned', 3, "p3_130th_caps")
rep("TWO HUNDRED AND SIXTY-THIRD", "TWO HUNDRED AND SIXTY-FOURTH", 3, "p3_wave_caps")
rep("bma_ordinal=130", "bmc_rows=82", 6, "p3_bma_ordinal130")
rep('"probe_receipt_bma_ordinal_face": 130', '"probe_receipt_bmc_ordinal_face": 82', 1, "p3_probe_face_key")
rep('"bma_own_ordinal": len(bma_rows_live) + 1', '"bmc_own_ordinal": len(bmc_rows_live) + 1', 1, "p3_own_ordinal_key")
rep("THIRTEENTH", "FOURTEENTH", 7, "p3_13_caps")
rep("TWELFTH", "THIRTEENTH", 15, "p3_12_caps")
rep("thirteenth", "fourteenth", 4, "p3_13_lc")
rep("twelfth", "thirteenth", 3, "p3_12_lc")
rep("fifty-first", "fifty-second", 2, "p3_51st")
# machine/narrative ownership faces
rep('"engine_owner": "bm-a"}', '"engine_owner": "bm-c"}', 3, "p3_ownowner")
rep("bm-c five-face freeze upstream seat", "bm-a five-face freeze upstream seat", 1, "p3_freshmsg_owner")
rep("_w == 262", "_w == 263", 1, "p3_freshmsg_cond")
rep('"machine": "bm-a"', '"machine": "bm-c"', 1, "p3_receipt_machine")
rep("bm-a own-seat freeze window", "bm-c own-seat freeze window", 1, "p3_phase")
rep("bm-a loop five-face freeze splice", "bm-c loop five-face freeze splice", 2, "p3_loop_owner")
rep("bm-a loop CEO fill-order", "bm-c loop CEO fill-order", 1, "p3_ceo_owner")
rep("bm-a OWN-SEAT face", "bm-c OWN-SEAT face", 2, "p3_ownseat_caps")
rep("bm-a loop freeze window", "bm-c loop freeze window", 1, "p3_exec_window")
rep("published=reserved by bm-a itself", "published=reserved by bm-c itself", 4, "p3_pub_reserved")
rep("published by bm-a itself", "published by bm-c itself", 1, "p3_pub_by")
rep("bm-c (upstream seat honored)", "bm-a (upstream seat honored)", 1, "p3_upstream_honored")
rep("owner=bm-c seat honored", "owner=bm-a seat honored", 1, "p3_gate05_print_owner")
rep("row not landed as declared (bm-c seat owner expected)",
    "row not landed as declared (bm-a seat owner expected)", 1, "p3_gate05_declared")
rep("(R262: ", "(R263: ", 1, "p3_repick")
rep("derived from the committed W263 editor template",
    "derived from the committed W263 freeze-edits template", 3, "p3_lineage_wording")
rep("bm-c own seat executed at the bm-c r1068 splice window",
    "bm-a own seat executed at the bm-a r1038 splice window", 1, "p3_pre_ownseat_r1068")
rep("finalize one-pass bm-c r1068", "finalize one-pass bm-a r1039", 2, "p3_finpass_r1068")
rep("cycle COMPLETE bm-c r1068 closeout 17:4x", "cycle COMPLETE bm-a r1038+r1040 closeout 19:2x", 1, "p3_hdr_complete")
rep("W263 bm-c own-wave full cycle r1068", "W263 bm-a own-wave full cycle r1038", 1, "p3_repair_note")
rep("r1068 splice window", "r1038 splice window", 2, "p3_lineage_window")
rep("bm-c own seat executed at", "bm-a own seat executed at", 1, "p3_mhdr_ownseat_split")
rep("the bm-c r1038 splice window", "the bm-a r1038 splice window", 1, "p3_mhdr_window_split")
rep("(bm-c r1068", "(bm-a r1038", 1, "p3_extract_gen_note")
rep("bm-c splice generation r1068 window", "bm-a splice generation r1038 window", 1, "p3_parity_source_note")
rep("verified r1068", "verified r1039/r1040", 1, "p3_lineage_verified")
rep("authored 17:4x", "authored 20:1x", 2, "p3_authored_stamp")
# r1037 eleven-face map (4 subsumed by bm-a r1037 window + 5 explicit + L6 rides fb0c962b5 needle)
rep("bm-a r1037 window", "bm-c r1076 window", 4, "p3_r1037_window")
rep("itself r1037; queue-head", "itself r1075; queue-head", 1, "p3_r1037_semicolon")
rep("(r1037, queue-head", "(r1075, queue-head", 1, "p3_r1037_paren")
rep("r1037 BEFORE this freeze", "r1075 BEFORE this freeze", 1, "p3_r1037_before")
rep("r1037 commit", "r1076 commit", 1, "p3_r1037_commit")
rep("# r1037 window", "# r1076 window", 1, "p3_r1037_hdr")
rep("(r1037 MSG-", "(r1075 MSG-", 1, "p3_r1037_msg")
rep("dd5fd438e r1037,", "dd5fd438e r1075,", 1, "p3_r1037_origin_resid")
# waits-upstream -> unblocked narrative (hdr split lines + four PENDING spots)
rep("was published BEFORE the W263 finalize landing (waits-upstream",
    "was published AFTER the W263 finalize landing (W264 FREEZE", 1, "p3_hdr_before_l8")
rep("face disclosed honest -- seat-first law O-20261010-2350 sec.2 seats never",
    "UNBLOCKED at seat time, zero waits-upstream face -- seat-first law", 1, "p3_hdr_before_l9")
rep("queue behind freeze windows; the SPLICE was GATED on the W263 finalize per",
    "O-20261010-2350 sec.2; the SPLICE gate0.5 = GREEN at seat: W263 row +", 1, "p3_hdr_before_l10")
rep("gate0.5, now GREEN: W263 row + W263 finalize file both in-place); zero DRAFT",
    "W263 finalize file both in-place); zero DRAFT", 1, "p3_hdr_before_l11")
rep("W263 finalize PENDING at seat -- waits-upstream face disclosed honest);",
    "W263 finalize LANDED at seat -- W264 FREEZE UNBLOCKED at seat time (zero waits-upstream face);", 1, "p3_pending_gate05")
rep("#     W263 finalize PENDING at seat -- waits-upstream face disclosed honest;",
    "#     W263 finalize LANDED at seat -- W264 FREEZE UNBLOCKED at seat time, zero waits-upstream face;", 1, "p3_pending_hdr_block")
rep("splice GATED per gate0.5 until the W263 finalize landed, zero skip-claim);",
    "splice gate0.5 = GREEN at seat (W263 finalize landed pre-seat), zero skip-claim);", 1, "p3_mhdr_gated_line")
rep("W263 registered + self-burn 12/12 at publish, W263 finalize PENDING at seat time (waits-upstream face disclosed honest; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE was GATED on the W263 finalize landing per gate0.5 -- now GREEN, W263 five-face + finalize product both in-place",
    "W263 registered+FINALIZED complete at publish, W264 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W263 five-face + finalize product both in-place", 1, "p3_pending_pfcomment")
rep("W263 registered + 12/12 burned at publish, W263 finalize PENDING at seat (waits-upstream face disclosed honest; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE was GATED on the W263 finalize landing per gate0.5, now GREEN (W263 row + n1_w263_results.json both in-place)",
    "W263 registered+FINALIZED complete at publish, W264 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W263 row + n1_w263_results.json both in-place)", 1, "p3_pending_receipt_note")
rep("wave 263 engine_owner=bm-a", "wave 264 engine_owner=bm-c", 1, "p3_receipt_waveface")
rep('"wave 263: "', '"wave 264: "', 1, "p3_cfg_waveface")
rep("wave 263 = first free number", "wave 264 = first free number", 1, "p3_mhdr_waveface")

# ---------- phase 4: frozen-face anti-drift + residual sweeps ----------
assert t.count("w244_a") == 12 and t.count("w244_b") == 8, "aging tokens w244_a/b drift"
assert t.count("n3r1_used245") == 3, "frozen face n3r1_used245 drift"
for gone in ("r1037", "r1068", "e1a94b335", "b32f6bf1c", "fb0c962b5", "_w263bma_",
            "w262_", "n1_w262", "593_", "594_100", "595_700", "595_900",
            "1,000,735", "574,320", "1_000_735", "574_320",
            "PENDING at seat", "waits-upstream face disclosed honest",
            "bma_ordinal", "bm-a r1037", "ONE HUNDRED AND THIRTIETH",
            "TWO HUNDRED AND SIXTY-THIRD", "== 120", "!= 120",
            "rows {len(bma_rows_live)}", "wave 263", "was published BEFORE",
            "W244..W261", "W211..W261", "W211..W243", "fifty-one",
            "thirty-three", "range(211, 262)"):
    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"
log.append("phase4 residual sweeps: 23 faces zero-residual PASS")

# ---------- phase 5: new-generation face presence gates + write ----------
must_have = {
    'MSG-20261017-1950-bmc-w264-seat': 7, "dd5fd438e": 2, "_w264bmc_": 11,
    "596_101": 8, "598_100": 9, "598_101": 5, "598_300": 4, "595_901": 4,
    "596_100": 6, "597_900": 2, "1,002,935": 5, "576,520": 5,
    '263: {"batch"': 2, '264: {"batch"': 2, '263: {"a"': 3, '264: {"a"': 1,
    "range(245, 264)": 2, "range(209, 265)": 2, "if w < 264)": 5,
    '"engine_owner": "bm-c"}': 3, "W264 materializer face": None,
    '"PERPETUAL-N1-W264"': None, "n1_w264": 4, "EIGHTY-THIRD": 3,
    "f499817fa": 1, "r1076": None, "r1075": None, "122 rows": 1, "122 parity rows": 1,
}
for k, v in must_have.items():
    c = t.count(k)
    if v is None:
        assert c > 0, f"presence gate FAIL: {k!r} count 0"
    else:
        assert c == v, f"presence gate FAIL: {k!r} count {c} != {v}"
log.append("phase5 presence gates PASS")
io.open(DST, "w", encoding="utf-8", newline="").write(t)
import py_compile
py_compile.compile(DST, doraise=True)
log.append(f"DST written {len(t.encode('utf-8'))} bytes + py_compile OK")
io.open(LOG, "w", encoding="utf-8", newline="").write("\n".join(log) + "\n")
print("\n".join(log[-4:]))
print("DERIVE OK ->", DST)
