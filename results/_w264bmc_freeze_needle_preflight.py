# -*- coding: utf-8 -*-
# r1076 bm-c: W264 freeze-edits derive PREFLIGHT needle probe (r787 law).
# Measures every planned needle's count on the committed canon
# results/_w263bma_freeze_edits.py (bm-a W263 freeze window, proven live-fire
# splice f499817fa) BEFORE the derive script is authored. Zero transcription:
# counts printed, derive asserts against these measured values.
import io, subprocess, sys

CANON = "results/_w263bma_freeze_edits.py"
blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w263bma_freeze_edits.py"], capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head and len(blob_wt) == 40, f"canon blob drift wt={blob_wt} head={blob_head}"
t = io.open(CANON, encoding="utf-8", newline="").read()
print("canon blob", blob_wt[:16], "bytes", len(t.encode('utf-8')))

# planned application order (old, tag) -- phase 1 lowercase/prefixed/band/anchor
NEEDLES = [
 # phase 1: projections first (W264->W265 before own-wave W263->W264)
 ("W264p", "p1_proj_prefix"),
 ("W264", "p1_proj_plain"),
 # band tokens (ordered: consumed values before producers)
 ("595_901", "p1_band_Blo"),
 ("596_100", "p1_band_Bhi"),
 ("593_701", "p1_band_W262Blo_naiveAlo"),
 ("593_900", "p1_band_W262Bhi"),
 ("595_700", "p1_band_naiveAhi"),
 ("593_901", "p1_band_Alo_Bnaivelo"),
 ("594_100", "p1_band_Bnaivehi"),
 ("595_900", "p1_band_Ahi"),
 # ledger anchors
 ("1,000,735", "p1_ledger_prose"),
 ("574,320", "p1_k_prose"),
 ("1_000_735", "p1_ledger_code"),
 ("574_320", "p1_k_code"),
 # lowercase machine-file tokens
 ("n1_w263", "p1_n1w263"),
 ("n1_w262", "p1_n1w262"),
 ("n1w263-", "p1_n1w263dash"),
 ("w263_", "p1_lc_w263_"),
 ("w262_", "p1_lc_w262_"),
 ("_w263bma_", "p1_receiptpath"),
 ("MSG-20261017-1740-bma-w263-seat", "p1_seat_msg"),
 ("fb0c962b5", "p1_seat_origin"),
 # phase 2: D-swaps
 ("W263", "p2_own_wave"),
 ("W262", "p2_upstream_wave"),
 # phase 3: post-D contextual (source text as it exists AFTER D-swaps)
 ("W260_W261_W263_bands_respected", "p3_relkey_postD"),
 ("W211..W243 legs (33)", "p3_kept_narr"),
 ("W211..W243 legs", "p3_kept_narr_alt"),
 ("W211..W261 legs (51)", "p3_legs_narr"),
 ("W244..W261 legs (18)", "p3_dropped_narr"),
 ("W244..W263 legs (19", "p3_fresh_narr_postD"),
 ("fresh W244..W262 legs", "p3_fresh_narr_preD_check"),
 ("block = 121 rows", "p3_block121"),
 ("121 parity rows", "p3_parity121"),
 ("== 120,", "p3_count120_assert"),
 ("!= 120", "p3_count120_fstring"),
 ("N1_BANDS[\") == 51", "p3_count51"),
 ("N1_BANDS[\") == 33", "p3_count33"),
 ("range(211, 244)", "p3_range_kept"),
 ("range(244, 262)", "p3_range_dropped"),
 ("range(244, 263)", "p3_range_fresh"),
 ("range(16, 263)", "p3_range16"),
 ("range(17, 263)", "p3_range17"),
 ("range(209, 264)", "p3_range209"),
 ("if w < 263)", "p3_wlt263"),
 ("if w < 262)", "p3_wlt262"),
 ("263 - _lw", "p3_legcount"),
 ("N1_BANDS\\[244\\]", "p3_regex244"),
 ("m244", "p3_m244"),
 ("N1_BANDS[244] == {", "p3_startswith244"),
 ("WAVE_CONFIGS[262]", "p3_wavecfg262"),
 ("N1_BANDS[262]", "p3_n1bands262"),
 ("get(262)", "p3_get262"),
 ("263: {\"batch\"", "p3_cfg263"),
 ("262: {\"batch\"", "p3_cfg262"),
 ("263: {\"a\"", "p3_row263"),
 ("262: {\"a\"", "p3_row262"),
 ("== 252 and len(bma_rows_live) == 129", "p3_ordinal_assert"),
 ("252/129/82", "p3_ordinal_expect"),
 ("owner_rows=252 / bma_rows=129", "p3_leg0_face"),
 ("rows 252 + candidate = 253rd", "p3_owner253"),
 ("bm-a rows 129 + candidate", "p3_bma129"),
 ("bm-a's 130th own wave", "p3_130th"),
 ("130th owned claim", "p3_130th_claim"),
 ("ONE HUNDRED AND THIRTIETH owned", "p3_130th_caps"),
 ("ONE HUNDRED AND THIRTIETH", "p3_130th_caps_any"),
 ("bma_ordinal=130", "p3_bma_ordinal130"),
 ("bma_ordinal", "p3_bma_ordinal"),
 ("THIRTEENTH", "p3_13_caps"),
 ("TWELFTH", "p3_12_caps"),
 ("thirteenth", "p3_13_lc"),
 ("twelfth", "p3_12_lc"),
 ("fifty-first", "p3_51st"),
 ("fifty-second", "p3_52nd_check"),
 ("\"engine_owner\": \"bm-a\"}", "p3_ownbm_a"),
 ("W263.get(\"engine_owner\") == \"bm-c\"", "p3_gate05_owner"),
 ("N1_BANDS[263].get(\"engine_owner\") == \"bm-c\"", "p3_mirror_owner"),
 ("bm-c five-face freeze upstream seat", "p3_freshmsg_bmc"),
 ("_w == 262", "p3_w_eq262"),
 ("\"machine\": \"bm-a\"", "p3_receipt_machine"),
 ("bm-a own-seat freeze window", "p3_phase_bma"),
 ("bm-a loop five-face freeze splice", "p3_loop_bma"),
 ("bm-a loop CEO fill-order", "p3_ceo_bma"),
 ("bm-a r1037 window", "p3_r1037"),
 ("bm-a own-seat continuity", "p3_owncont_bma"),
 ("engine_owner==bm-a rows", "p3_eo_bma"),
 ("bm-a OWN-SEAT face", "p3_ownseat_bma"),
 ("(R262: ", "p3_r262"),
 ("W263 bm-c own-wave full cycle r1068", "p3_repair_note"),
 ("bm-c (upstream seat honored)", "p3_upstream_honored"),
 ("W250..W259", "p3_transitive_window"),
 ("(259, 258, 257, 256, 255, 254, 253, 252, 251, 250)", "p3_transitive_list"),
 ("arith_a263", "p3_arith_a"),
 ("arith_b263", "p3_arith_b"),
 ("bm-c W263 five-face", "p3_bmc_w263_upstream"),
 ("\"engine_owner\": \"bm-c\"' in w263_own_line", "p3_ownline_assert"),
 ("\"bma_own_ordinal\"", "p3_bma_own_ordinal_key"),
 ("\"probe_receipt_bma_ordinal_face\": 130", "p3_probe_face_key"),
 ("W262 finalize PENDING at seat", "p3_pending_at_seat"),
 ("waits-upstream face disclosed honest", "p3_waits_honest"),
 ("published BEFORE this freeze", "p3_pub_before"),
 ("2026-10-17 18:2x bm-a r1038 freeze window", "p3_hdr_stamp"),
 ("bm-a's ONE HUNDRED", "p3_bma_onehundred"),
 ("bm-a's", "p3_bma_apostrophe"),
 ("bm-c's", "p3_bmc_apostrophe_check"),
 ("probe leg0 bmc_ordinal", "p3_leg0_bmc_check"),
 ("bm-a's 130th", "p3_bma130th"),
 ("131", "p3_131_check"),
 ("129 + candidate", "p3_129cand"),
 ("82 + candidate", "p3_82cand_check"),
 ("bm-c rows 82", "p3_bmc82_check"),
]

for old, tag in NEEDLES:
    print(f"{tag}\t{t.count(old)}\t{old[:70]!r}")
print("PREFLIGHT DONE")
