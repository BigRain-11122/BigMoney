# -*- coding: utf-8 -*-
# r1086 bm-c: W266 splice-editor needle preflight -- MEASURED counts (r1077 law)
# on the committed W265 freeze-edits canon (results/_w265bmc_freeze_edits_TOL.py)
# before authoring results/_w266bmc_derive_editor.py. Zero mutation: read-only.
import io, subprocess

CANON = "results/_w265bmc_freeze_edits_TOL.py"
OUT = "results/_w266bmc_editor_needle_counts.txt"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:results/_w265bmc_freeze_edits_TOL.py"],
                           capture_output=True, text=True).stdout.strip()
t = io.open(CANON, encoding="utf-8", newline="").read()
lines = ["canon blob wt=%s head=%s identical=%s" % (blob_wt[:16], blob_head[:16], blob_wt == blob_head),
         "bytes %d lines %d" % (len(t.encode("utf-8")), t.count("\n"))]

NEEDLES = [
    # phase-1 projections
    "W266p", "W267p", "W266", "W265p",
    # phase-1 bands (consumers then producers)
    "600_301", "600_500", "598_301", "600_300", "598_500", "600_100",
    "598_101", "598_300", "602_501", "602_500", "602_700", "600_501", "602_300", "600_700", "604_500", "602_900", "602_701",
    # ledger/K anchors
    "1,005,135", "578,720", "1_005_135", "578_720", "1,007,335", "580,920", "1_007_335", "580_920",
    # lowercase machine tokens
    "n1_w265", "n1_w264", "n1w265-", "n1w264-", "w265_", "w264_", "w263_", "_w265bmc_", "_w266bmc_",
    "_w262bmc_", "20261017", "20261018",
    # seat / shas
    "MSG-20261017-2241-bmc-w265-seat", "MSG-20261018-0719-bmc-w266-seat",
    "7343e3650", "ace19ba85b", "216b578b0", "a47517f79", "e57215a2c", "595433d63c", "f4ffdb34e",
    # gate0.5 upstream owner faces
    'W264.get("engine_owner") == "bm-c"', 'N1_BANDS[264].get("engine_owner") == "bm-c"',
    # phase-2 D-swaps
    "W265", "W264", "W263", "W262", "W261",
    # phase-3 relkey
    "W262_W263_W264_bands_respected",
    # kept/dropped/fresh ranges + counts
    "W211..W245 legs (35)", "W211..W263 legs (53)", "W246..W263 legs (18)", "own W246..W263",
    "W246..W263 eighteen legs", "W211..W264 legs 53", "W211..W263 fifty-three legs",
    "keep W211..W245 verbatim (35 legs)", "W211..W245 thirty-five legs",
    "W246..W264 legs (19", "W211..W264 legs (52", "fifty-three legs", "fifty-third", "fifty-second",
    "range(211, 246)", "range(211, 264)", "range(246, 264)", "range(246, 265)",
    "range(16, 265)", "range(17, 265)", "range(209, 266)", "range(138, 207)",
    "if w < 265)", "if w < 264)", "if w < 263)", "265 - _lw", "264 - _lw",
    "N1_BANDS\\[246\\]", "m246", "m211", "N1_BANDS[246] ==", "N1_BANDS[211] ==",
    "WAVE_CONFIGS[264]", "N1_BANDS[264]", "get(264)", "_c264", "_c265",
    '265: {"batch"', '264: {"batch"', '265: {{"batch"', '264: {{"batch"',
    '265: {"a"', '264: {"a"', '265: {{"a"', '264: {{"a"',
    "arith_a265", "arith_b265", "arith_a264", "arith_b264",
    "(261, 260, 259, 258, 257, 256, 255, 254, 253, 252)",
    "W252..W261", "W253..W262",
    # ordinals
    "len(owner_rows_live) == 254", "len(bma_rows_live) == 130", "len(bmc_rows_live) == 83",
    "254/130/83", "owner_rows=254 / bma_rows=130 / bmc_rows=83",
    "rows 254 + candidate = 255th", "; bm-c rows 83 +", "bm-c rows 83 + candidate = 84th owned",
    "# candidate = 84th EXACT", "engine_owner==bm-c rows 83 + candidate",
    "bm-c rows {len(bmc_rows_live)} + candidate (84th own wave",
    "bm-c's 84th own wave", "EIGHTY-FOURTH owned", "EIGHTY-FOURTH", "EIGHTY-FIFTH",
    "TWO HUNDRED AND SIXTY-FIFTH", "TWO HUNDRED AND SIXTY-SIXTH",
    "bmc_rows=83", "bmc_rows=84", '"probe_receipt_bmc_ordinal_face": 83',
    "FIFTEENTH", "FOURTEENTH", "SIXTEENTH", "fifteenth", "fourteenth", "sixteenth",
    "fourteen-wave",
    # upstream owner narrative faces (stale-carried vs rolled)
    "bm-c five-face freeze upstream seat", "bm-a five-face freeze upstream seat",
    "bm-c (upstream seat honored)", "bm-a (upstream seat honored)",
    "owner=bm-c seat honored", "owner=bm-a seat honored",
    "(bm-c seat owner expected)", "(bm-a seat owner expected)",
    "_w == 264", "_w == 265", "bm-a's EIGHTY-FOURTH", "engine_owner==bm-a",
    # wave-number narrative
    "wave 265 engine_owner=bm-c", '"wave 265: "', "wave 265 = first free number",
    "wave 264 engine_owner", '"wave 264: "', "wave 264 = first free number",
    # cycle lineage stamps
    "bm-c r1076", "bm-c r1077", "bm-a r1038", "r1038", "r1076", "r1077", "r1081", "r1075",
    "bm-c r1081 window", "bm-c r1085 window", "r1081 commit", "# r1081 window",
    "authored 04:0x", "authored 09:0x", "20:5x bm-c r1076 freeze window", "22:4x", "07:0x",
    "(bm-c r1076", "bm-c splice generation r1076 window", "the bm-c r1076 splice window",
    "cycle COMPLETE bm-c r1076+r1077 closeout 22:4x",
    "W264 bm-c own-wave full cycle r1076", "verified r1077", "(R264: ", "(R265: ",
    "fifty-third consecutive", "fifty-fourth consecutive",
    "clean precondition (fifty-third", "fifty-third consecutive fully-clean",
    # misc
    "PERPETUAL_N1_W265_PREREG", "PERPETUAL_N1_W266_PREREG", "PERPETUAL_N1_W264_PREREG",
    "PERPETUAL-N1-W265", "PERPETUAL-N1-W266", "n1_w265_results.json", "n1_w264_results.json",
    "n1_w266", "shard_subdir", "TOL", "_w265bmc_freeze_edits_TOL",
    "W265 materializer face", "W266 materializer face", '"--- W265 materializer', '"--- W266 materializer',
    "a22 = '    # --- W264 materializer face'", "a22 = '    # --- W265 materializer face'",
    "T-141 s2 lane face", "w244_a", "w244_b", "n3r1_used245",
    "W265 FREEZE UNBLOCKED", "W266 FREEZE UNBLOCKED", "was published AFTER", "was published BEFORE",
    "PENDING at seat", "waits-upstream face disclosed honest",
]
for n in NEEDLES:
    lines.append("%4d  %r" % (t.count(n), n))

# context dumps for adjudication faces
def ctx(needle, tag, maxn=14):
    lines.append("--- CTX %s %r ---" % (tag, needle))
    start = 0
    for i in range(maxn):
        j = t.find(needle, start)
        if j < 0:
            break
        ls = t.rfind("\n", 0, j) + 1
        le = t.find("\n", j)
        lines.append("  %s" % t[ls:le if le > 0 else len(t)].strip()[:200])
        start = j + 1
    if t.find(needle, start) >= 0:
        lines.append("  ...more")

ctx("r1076", "r1076")
ctx("r1077", "r1077")
ctx("r1081", "r1081")
ctx("r1038", "r1038")
ctx("r1075", "r1075")
ctx("bm-a", "bm-a-narrative", 40)
ctx("W266", "plain-W266", 40)
ctx("W267", "W267-any", 10)
ctx("20261017", "date17", 20)
ctx("04:0x", "authored-stamp")
ctx("22:4x", "closeout-stamp")
ctx("20:5x", "window-stamp")
ctx("fifty-third", "fiftythird")
ctx("216b578b0", "w264-splice-sha")
ctx("e57215a2c", "w265-prereg-sha")
ctx("7343e3650", "w265-seat-origin")
ctx("_w == 264", "freshmsg-cond")
ctx("w244_a", "aging-face", 6)
ctx("TOL", "TOL-face", 6)
ctx("W262", "W262-any", 16)
ctx("W261", "W261-any", 12)
ctx("W263", "W263-any", 30)

io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
print("preflight written", OUT, "lines", len(lines))
print("canon blob identical:", blob_wt == blob_head)
