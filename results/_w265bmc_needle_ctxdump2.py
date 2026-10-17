# -*- coding: utf-8 -*-
# r1084 bm-c: W265 derive SUPPLEMENTARY needle ctxdump (r1076 ctxdump-family law:
# every derive needle count measured on the committed canon BEFORE the derive
# script is authored; phase-3 needles measured on POST-D-swap simulation text
# per r1076 preflight postD/preD law). Output = results/_w265bmc_needle_ctxdump2.txt
import io, subprocess, sys, os

CANON = "results/_w264bmc_freeze_edits.py"
OUT = "results/_w265bmc_needle_ctxdump2.txt"
L = []

def gsha(ref):
    r = subprocess.run(["git", "rev-parse", ref], capture_output=True, text=True)
    return r.stdout.strip()

def gts(ref):
    r = subprocess.run(["git", "log", "-1", "--format=%ci", ref], capture_output=True, text=True)
    return r.stdout.strip()

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = gsha("HEAD:results/_w264bmc_freeze_edits.py")
assert blob_wt == blob_head and len(blob_wt) == 40, f"canon drift {blob_wt} vs {blob_head}"
t = io.open(CANON, encoding="utf-8", newline="").read()
L.append("canon blob %s bytes %d HEAD-verified" % (blob_wt[:16], len(t.encode("utf-8"))))

# narrative stamp inputs (machine-read, zero hand-transcription)
for ref in ("216b578b0", "e57215a2c", "7343e3650", "3917a974e", "f4ffdb34e", "dd5fd438e"):
    L.append("GIT %s ts=%s full=%s" % (ref[:10], gts(ref)[:16], gsha(ref)[:12]))
L.append("receipt W265 exists=%s" % os.path.exists("results/_w265bmc_20261017_probe_receipt.json"))
L.append("seat MSG W265 exists=%s" % os.path.exists("fleet/inbox/MSG-20261017-2241-bmc-w265-seat.md"))
L.append("w264 finalize exists=%s" % os.path.exists("results/perpetual_faces/n1_w264_results.json"))

L.append("")
L.append("=== A. RAW composition faces ===")
for k in ["W264", "W263", "W264p", "W265p", "W265", "_w264bmc_", "n1_w264_results",
          "n1_w263_results", "n1_w264_", "n1_w263_", "n1_w264/", "n1_w263/",
          "PERPETUAL_N1_W264_PREREG", "PERPETUAL-N1-W264", "PERPETUAL_N1_W265", "PERPETUAL-N1-W265",
          "w264_", "w263_", "w262_", "n1_w262", "w244_a", "w244_b", "n3r1_used245",
          "m245", "m244", "_c263", "_c262", "arith_a264", "arith_b264",
          "block = 122 rows", "122 parity rows", "block = 121 rows", "121 parity rows",
          "!= 121", "!= 122", 'N1_BANDS[") == 121,', 'N1_BANDS[") == 122,',
          'N1_BANDS[") == 52', 'N1_BANDS[") == 34', 'N1_BANDS[") == 53', 'N1_BANDS[") == 35',
          "range(211, 263)", "range(211, 264)", "range(211, 262)",
          "keep W211..W244 verbatim (34 legs)", "W211..W244 thirty-four legs",
          "W245..W263 legs (19", "W244..W263 legs (19", "W245..W264 legs (19",
          "W211..W262 fifty-two legs", "W211..W263 fifty-two legs",
          "W262.get(", "W263.get(", 'W263.get("engine_owner") == "bm-a"',
          'N1_BANDS[263].get("engine_owner") == "bm-a"', 'N1_BANDS[262].get("engine_owner")',
          '"engine_owner": "bm-c"}', '"engine_owner": "bm-a"}',
          "wave 264 engine_owner", '"wave 264: "', "wave 264 = first free number",
          "wave 265 engine_owner", '"wave 265: "', "wave 265 = first free number",
          "r1075", "r1076", "r1077", "r1081", "authored 20:1x", "authored 22:4x",
          "bm-c r1076 window", "bm-c r1081 window", "r1076 window", "r1075 window",
          "itself r1075", "(r1075,", "r1075 BEFORE", "r1076 commit", "# r1076 window",
          "(r1075 MSG-", "r1075,", "r1077,",
          "FOURTEENTH", "THIRTEENTH", "FIFTEENTH", "fourteenth", "thirteenth", "fifteenth",
          "fifty-second", "fifty-third", "TWO HUNDRED AND SIXTY-FOURTH", "TWO HUNDRED AND SIXTY-FIFTH",
          "EIGHTY-THIRD", "EIGHTY-FOURTH", "83rd own", "84th own", "83rd owned", "84th owned",
          "253/130/82", "254/130/83", "bmc_rows=82", "bmc_rows=83",
          "owner_rows=253 / bma_rows=130", "rows 253 + candidate = 254th", "rows 254 + candidate = 255th",
          "bm-c rows 82 + candidate", "bm-c rows 83 + candidate", "# candidate = 83rd EXACT",
          "len(owner_rows_live) == 253", "len(bma_rows_live) == 130", "len(bmc_rows_live) == 82",
          "bm-c's 83rd own wave", "(bm-c published the", "bm-c own-seat continuity",
          '"probe_receipt_bmc_ordinal_face": 82', '"bmc_own_ordinal"',
          "W261_W262_W263_bands_respected", "W262_W263_W264_bands_respected",
          "216b578b0", "f499817fa", "f499817fac26786ca3c8b0726aa54c0aa31c2bd2",
          "1,005,135", "578,720", "1_005_135", "578_720",
          "598_101", "600_301", "600_501", "602_300", "600_100",
          "arith_a263", "arith_b263", "arith_a265",
          "(260, 259, 258, 257, 256, 255, 254, 253, 252, 251)",
          "(261, 260, 259, 258, 257, 256, 255, 254, 253, 252)",
          "W251..W260", "W252..W261",
          "was published AFTER", "was published BEFORE", "W264 FREEZE UNBLOCKED",
          "W265 FREEZE UNBLOCKED", "PENDING at seat", "waits-upstream face disclosed honest",
          "if w < 264)", "if w < 263)", "if w < 265)", "264 - _lw", "265 - _lw",
          "range(211, 245)", "range(246, 264)", "range(245, 263)", "range(245, 264)",
          "range(16, 264)", "range(17, 264)", "range(209, 265)",
          "N1_BANDS\\[245\\]", "N1_BANDS[245] == {", "WAVE_CONFIGS[263]", "WAVE_CONFIGS[264]",
          "N1_BANDS[263]", "N1_BANDS[264]", "get(263)", "get(264)",
          '264: {"batch"', '265: {"batch"', '263: {"batch"', '264: {{"batch"', '265: {{"batch"',
          '264: {{"a"', '265: {{"a"', '264: {"a"', '263: {"a"',
          "W211..W244 legs (34)", "W211..W245 legs (35)", "W211..W262 legs (52)", "W211..W263 legs (53)",
          "W245..W262 legs (18)", "W246..W263 legs (18)", "own W245..W262", "own W246..W263",
          "W245..W262 eighteen legs", "W246..W263 eighteen legs",
          "W211..W264 legs 52", "W211..W264 legs 53", "W211..W263 legs 52",
          "1,002,935", "576,520", "1_002_935", "576_520"]:
    L.append("RAW %-55r = %d" % (k[:55], t.count(k)))

L.append("")
L.append("=== B. context dumps (derive-author inputs) ===")
def dump_lines(needles, label, maxlen=190):
    L.append("--- %s ---" % label)
    for i, ln in enumerate(t.split("\n")):
        if any(n in ln for n in needles):
            L.append("L%d: %s" % (i + 1, ln.strip()[:maxlen]))

dump_lines(["r1075"], "lines containing r1075")
dump_lines(["r1076"], "lines containing r1076")
dump_lines(["authored 20:1x"], "lines containing authored 20:1x")
dump_lines(["bm-c r1076", "bm-a r1038"], "upstream-cycle narrative lines")
dump_lines(["MSG-20261017-1950-bmc-w264-seat"], "seat MSG narrative lines")
dump_lines(["five-face", "five faces", "io.open(", "FACES"], "face-write structure lines")

# ---------- C. phase-1 + phase-2 simulation (assert preflight-measured counts) ----------
L.append("")
L.append("=== C. phase-1/2 simulation ===")
s = t
def rep(old, new, expect, tag, dynamic=False):
    global s
    n = s.count(old)
    if dynamic:
        L.append("REP-DYN %-28s %dx  %r -> %r" % (tag, n, old[:48], new[:36]))
    else:
        L.append("REP %-30s %dx%s %r" % (tag, n, "" if n == expect else " **EXPECT %d**" % expect, old[:48]))
        assert n == expect, f"[{tag}] SIM count {n} != {expect}: {old[:80]!r}"
    s = s.replace(old, new)

rep("W265p", "W266p", 13, "p1_proj_prefix")
rep("W265", "W266", 13, "p1_proj_plain")
rep("598_101", "600_301", 5, "p1_band_Blo")
rep("598_300", "600_500", 4, "p1_band_Bhi")
rep("596_101", "598_301", 8, "p1_band_Alo")
rep("598_100", "600_300", 9, "p1_band_Ahi")
rep("596_300", "598_500", 2, "p1_band_Bnaivehi")
rep("597_900", "600_100", 2, "p1_band_naiveAhi")
rep("595_901", "598_101", 4, "p1_band_priorBlo")
rep("596_100", "598_300", 6, "p1_band_priorBhi")
rep("1,002,935", "1,005,135", 5, "p1_ledger_prose")
rep("576,520", "578,720", 5, "p1_k_prose")
rep("1_002_935", "1_005_135", 1, "p1_ledger_code")
rep("576_520", "578_720", 1, "p1_k_code")
rep("n1_w264", "n1_w265", 4, "p1_n1w264")
rep("n1w264-", "n1w265-", 2, "p1_n1w264dash")
rep("w264_", "w265_", 10, "p1_lc_w264_", dynamic=True)  # measured: 12 raw - n1_w264_ inside
rep("n1_w263", "n1_w264", 4, "p1_n1w263")
rep("w263_", "w264_", 91, "p1_lc_w263_", dynamic=True)  # measured: 93 raw - n1_w263_ inside
rep("_w264bmc_", "_w265bmc_", 11, "p1_receiptpath")
rep("MSG-20261017-1950-bmc-w264-seat", "MSG-20261017-2241-bmc-w265-seat", 7, "p1_seat_msg")
rep("dd5fd438e", "7343e3650", 2, "p1_seat_origin")
rep("f499817fa", "216b578b0", 1, "p1_lineage_sha")
rep("f4ffdb34e", "e57215a2c", 1, "p1_prereg_sha_ref")
rep('W263.get("engine_owner") == "bm-a"', 'W263.get("engine_owner") == "bm-c"', 1, "p1_gate05_owner")
rep('N1_BANDS[263].get("engine_owner") == "bm-a"', 'N1_BANDS[263].get("engine_owner") == "bm-c"', 1, "p1_mirror_owner")

L.append("post-phase1: W264=%d W263=%d" % (s.count("W264"), s.count("W263")))
rep("W264", "W265", 81, "p2_own_wave", dynamic=True)   # measured post-phase1 count governs
rep("W263", "W264", 162, "p2_upstream_wave", dynamic=True)
L.append("post-phase2 residual checks: W263=%d W264-in-projection=%d" % (s.count("W263"), s.count("W266")))

# ---------- D. phase-3 old-value measurement on the POST-D simulation text ----------
L.append("")
L.append("=== D. phase-3 POST-D old-value counts (bake into derive asserts) ===")
P3 = [
 ("W261_W262_W264_bands_respected", "relkey postD"),
 ("W211..W244 legs (34)", "kept_narr"),
 ("W211..W262 legs (52)", "legs_narr"),
 ("W245..W262 legs (18)", "dropped_narr"),
 ("own W245..W262", "dropped_split_hdr"),
 ("W245..W262 eighteen legs", "dropped_fstring"),
 ("W211..W264 legs 52", "fullspan_fstring postD"),
 ("W211..W263 legs 52", "fullspan preD remnant check"),
 ("range(211, 263)", "legs_range_assert"),
 ("W211..W262 fifty-two legs", "legs_fstring"),
 ("keep W211..W244 verbatim (34 legs)", "kept_comment"),
 ("W211..W244 thirty-four legs", "kept_fstring"),
 ("W245..W264 legs (19", "fresh_narr postD"),
 ("block = 122 rows", "block122"),
 ("122 parity rows", "parity122"),
 ('N1_BANDS[") == 121,', "count121"),
 ("!= 121", "fstring121"),
 ('N1_BANDS[") == 52', "count52"),
 ('N1_BANDS[") == 34', "count34"),
 ("range(211, 245)", "range_kept"),
 ("range(245, 263)", "range_dropped"),
 ("range(245, 264)", "range_fresh"),
 ("range(16, 264)", "range16"),
 ("range(17, 264)", "range17"),
 ("range(209, 265)", "range209"),
 ("if w < 264)", "wlt264"),
 ("if w < 263)", "wlt263_antigate"),
 ("264 - _lw", "legcount"),
 ("N1_BANDS\\[245\\]", "regex245"),
 ("m245", "m245"),
 ("N1_BANDS[245] == {", "startswith245"),
 ("WAVE_CONFIGS[263]", "wavecfg263"),
 ("N1_BANDS[263]", "n1bands263"),
 ('"engine_owner": "bm-c"}', "ownowner_bm_c"),
 ("get(263)", "get263"),
 ("_c263", "c263var"),
 ('264: {"batch"', "cfg264 plain"),
 ('264: {{"batch"', "cfg264 fstring"),
 ('263: {"batch"', "cfg263 plain"),
 ('264: {{"a"', "row264 fstring"),
 ('264: {"a"', "row264 postgate"),
 ('263: {"a"', "row263"),
 ("arith_a264", "arith_a"),
 ("arith_b264", "arith_b"),
 ("(260, 259, 258, 257, 256, 255, 254, 253, 252, 251)", "transitive_list"),
 ("W251..W260", "transitive_window"),
 ("len(owner_rows_live) == 253 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 82", "ordinal_assert full"),
 ("253/130/82", "ordinal_expect"),
 ("owner_rows=253 / bma_rows=130 / bmc_rows=82", "leg0_face full"),
 ("rows 253 + candidate = 254th", "owner254"),
 ("bm-c rows 82 + candidate", "bmc82"),
 ("bm-c rows 83", "bmc83_check"),
 ("EIGHTY-THIRD owned", "83rd_caps"),
 ("EIGHTY-FOURTH", "84th_check"),
 ("83rd own wave", "83rd_own"),
 ("84th own", "84th_own_check"),
 ("# candidate = 83rd EXACT", "comment_83rd"),
 ("bm-c rows 82 + candidate = 83rd owned", "receipt_83owned"),
 ("engine_owner==bm-c rows 82 + candidate", "pr_eo83"),
 ("engine_owner==bm-c rows \"", "pre_eo_fstring"),
 ("{len(bmc_rows_live)} + candidate; probe receipt leg0", "pre_len_fstring"),
 ("rows {len(bmc_rows_live)} + candidate; own-seat face", "mhdr_len_fstring"),
 ("bm-c rows {len(bmc_rows_live)} + candidate (83rd own wave", "gate0_5_print"),
 ("bm-c's 83rd own wave", "83rd_own_wave"),
 ("bm-c own-seat continuity", "ownseat_cont"),
 ("(bm-c published the", "published_by"),
 ("continuity, zero waits-upstream face", "ordnote_waits"),
 ("TWO HUNDRED AND SIXTY-FOURTH", "wave264_caps"),
 ("TWO HUNDRED AND SIXTY-FIFTH", "wave265_check"),
 ("FOURTEENTH", "14_caps"),
 ("THIRTEENTH", "13_caps"),
 ("FIFTEENTH", "15_check"),
 ("fourteenth", "14_lc"),
 ("thirteenth", "13_lc"),
 ("fifteenth", "15_lc_check"),
 ("fifty-second", "52nd"),
 ("fifty-third", "53rd_check"),
 ("255th", "255th_check"),
 ("254th", "254th"),
 ("bmc_rows=82", "bmc_rows82"),
 ('"probe_receipt_bmc_ordinal_face": 82', "probe_face_key"),
 ('"bmc_own_ordinal": len(bmc_rows_live) + 1', "own_ordinal_key"),
 ("wave 264 engine_owner", "receipt_waveface"),
 ('"wave 264: "', "cfg_waveface"),
 ("wave 264 = first free number", "mhdr_waveface"),
 ("wave 265", "wave265_check"),
 ("bm-c five-face freeze upstream seat", "freshmsg_owner"),
 ("bm-a five-face freeze upstream seat", "freshmsg_owner_bma_check"),
 ('"machine": "bm-c"', "receipt_machine"),
 ('"machine": "bm-a"', "receipt_machine_bma_check"),
 ("bm-c own-seat freeze window", "phase"),
 ("bm-c loop five-face freeze splice", "loop_owner"),
 ("bm-c loop CEO fill-order", "ceo_owner"),
 ("bm-c OWN-SEAT face", "ownseat_caps"),
 ("bm-c loop freeze window", "exec_window"),
 ("published=reserved by bm-c itself", "pub_reserved"),
 ("published by bm-c itself", "pub_by"),
 ("bm-c (upstream seat honored)", "upstream_honored"),
 ("owner=bm-c seat honored", "gate05_print_owner"),
 ("bm-a seat owner expected", "gate05_declared_bma_check"),
 ("bm-c seat owner expected", "gate05_declared_check"),
 ("(R262: ", "repick"),
 ("derived from the committed W263 freeze-edits template", "lineage_wording"),
 ("bm-c own seat executed at", "pre_ownseat_split"),
 ("finalize one-pass bm-c r1077", "finpass_new_check"),
 ("finalize one-pass bm-a r1039", "finpass_r1039"),
 ("cycle COMPLETE bm-a r1038+r1040 closeout 19:2x", "hdr_complete"),
 ("W263 bm-a own-wave full cycle r1038", "repair_note"),
 ("r1038 splice window", "lineage_window"),
 ("(bm-a r1038", "extract_gen_note"),
 ("splice generation r1038 window", "parity_source_note"),
 ("verified r1039/r1040", "lineage_verified"),
 ("authored 20:1x", "authored_stamp"),
 ("bm-c r1076 window", "r1076_window_bmc"),
 ("r1076 window", "r1076_window"),
 ("r1075", "r1075_refs"),
 ("r1081", "r1081_check"),
 ("r1084", "r1084_check"),
 ("W265 FREEZE UNBLOCKED", "unblocked_W265 postD"),
 ("W266p", "proj_prefix new"),
 ("W266", "proj_plain new"),
 ("_w265bmc_", "receiptpath new"),
 ("MSG-20261017-2241-bmc-w265-seat", "seat_msg new"),
 ("7343e3650", "seat_origin new"),
 ("216b578b0", "lineage_sha new"),
 ("e57215a2c", "prereg_sha new"),
 ("1,005,135", "ledger new"),
 ("578,720", "k new"),
 ("600_301", "band B_lo new"),
 ("598_301", "band A_lo new"),
 ("600_300", "band A_hi new"),
 ("600_500", "band B_hi new"),
 ("n1_w265", "n1w265 new"),
 ("w244_a", "aging w244_a"),
 ("w244_b", "aging w244_b"),
 ("n3r1_used245", "aging n3r1_used245"),
]
for old, tag in P3:
    L.append("P3 %-42s %3d  %r" % (tag, s.count(old), old[:60]))

io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(L) + "\n")
print("CTDUMP2 DONE ->", OUT, "lines", len(L))
print("post-phase1 W264=%d W263=%d" % (t.count("W264"), 0) if False else "")
print("KEY: post-phase1 W264 swap count see log; raw W264=%d W263=%d" % (t.count("W264"), t.count("W263")))
