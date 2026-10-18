# -*- coding: utf-8 -*-
# r1093 bm-c: W269 five-face splice editor -- MEASURED needle preflight
# (r1077 measured-counts law; canon = results/_w268bmc_freeze_edits.py,
# committed by the r1091 splice window 8bc7ac759e; this probe re-measures
# EVERY candidate needle at authoring time + dumps ambiguous-face contexts
# (r-window numbers / seat shas / parity counts) for precise editor design.
# Read-only. Zero mutation. Receipt -> results/_r1093bmc_needle_preflight.json
import hashlib, io, json, subprocess, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = REPO + r"\results\_w268bmc_freeze_edits.py"

def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, encoding="utf-8", errors="replace")

blob_wt = git("hash-object", CANON).stdout.strip()
blob_head = git("rev-parse", "HEAD:results/_w268bmc_freeze_edits.py").stdout.strip()
blob_origin = git("rev-parse", "origin/main:results/_w268bmc_freeze_edits.py").stdout.strip()
sha256_full = hashlib.sha256(open(CANON, "rb").read()).hexdigest()

t = io.open(CANON, encoding="utf-8", newline="").read()
lines = t.split("\n")

faces = [
    # ---- projections (phase1) ----
    "W269p", "W269", "W270p", "W270", "W271", "W268p",
    # ---- bands (phase1, consumers then producers) ----
    "606_901", "607_100", "604_901", "606_900", "605_100", "606_700",
    "604_701", "604_900", "602_501", "602_700", "602_701", "602_900",
    "604_500", "609_101", "609_300", "607_101", "609_100", "607_300",
    "608_900", "611_100", "611100", "609_301", "609_500",
    "600_301", "600_500", "600_700", "602_300", "600_501", "602_500",
    "598_101", "598_300", "598_301", "600_300", "598_500", "600_100", "593901",
    # ---- ledger/K anchors (phase1) ----
    "1,011,735", "585,320", "1_011_735", "585_320", "1,013,935", "587,520",
    "1,009,535", "583,120", "1_009_535", "583_120",
    "1,007,335", "580,920", "1_007_335", "580_920",
    # ---- lowercase machine tokens (phase1) ----
    "n1_w268", "n1_w267", "n1w268-", "n1w267-", "w268_", "w267_",
    "n1_w269", "w269_", "_w268bmc_", "_w269bmc_", "_w267bmc_",
    "n1_w268_results.json", "n1_w267_results.json", "n1_w266",
    # ---- seat/sha faces (phase1) ----
    "MSG-20261018-1229-bmc-w268-seat", "MSG-20261018-1407-bmc-w269-seat",
    "b9ad2f1119", "d630d043b9", "7b9e9377", "8bc7ac759e", "f1ec8231c7",
    "67fe12710c", '"wave": 267', '"wave": 268', '"wave": 269',
    "b9ad2f1119 r1089", "origin b9ad2f1119", "b9ad2f1119 BEFORE",
    # ---- setwave aging faces ----
    "_set_wave(268)", "_set_wave(267)", "_set_wave(266)", "_set_wave(269)",
    "_set_wave(2)",
    # ---- phase2 blanket raws ----
    "W268", "W267", "W266", "W265",
    # ---- relation-assert / bands-respected ----
    "W264_W265_W267_bands_respected", "W265_W266_W267_bands_respected",
    "W266_W267_W268_bands_respected",
    "A_staircase_hop_past_W267_B", "B_base_above_W267_tail",
    "A_staircase_hop_past_W268_B", "B_base_above_W268_tail",
    # ---- parity/legs faces ----
    "W211..W247 legs (37)", "W211..W247 verbatim (37 legs)",
    "W211..W247 thirty-seven legs", "W211..W266 legs (56)",
    "W211..W267 legs 56", "W211..W267 legs 57", "own W248..W266 legs (19)",
    "own W248..W266", "W248..W266 nineteen legs", "W248..W267 legs (20",
    "W248..W268 legs", "W249..W268", "block = 126 rows", "126 parity rows",
    "block parity = 126 rows", "block parity = 121 rows", "block parity = 127 rows",
    "121 rows", "125 rows", "127 rows",
    "fifty-six legs", "fifty-seven legs", "fifty-sixth", "fifty-seventh",
    "fifty-fifth", "fifty-five legs",
    '"fresh_legs_row_asserts": 20', '"fresh_legs_row_asserts": 21',
    "+ 20,", "+ 21,", "+ 19,",
    # ---- count-gate numerals ----
    'N1_BANDS[") == 125,', 'N1_BANDS[") == 126,', '!= 125', '!= 126',
    'N1_BANDS[") == 56', 'N1_BANDS[") == 57', 'N1_BANDS[") == 37',
    "== 124", "!= 124", "== 123", "!= 123",
    # ---- ranges ----
    "range(248, 268)", "range(248, 267)", "range(248, 269)",
    "range(211, 248)", "range(211, 267)", "range(211, 268)",
    "range(16, 268)", "range(16, 269)", "range(17, 268)", "range(17, 269)",
    "range(209, 269)", "range(209, 270)", "range(138, 207)",
    "if w < 268)", "if w < 267)", "if w < 269)",
    "268 - _lw", "269 - _lw", "m248", "m247", "m211",
    "N1_BANDS[248] ==", "N1_BANDS\\[248\\]",
    # ---- cfg/dict faces ----
    'WAVE_CONFIGS[268]', 'WAVE_CONFIGS[267]', 'WAVE_CONFIGS[269]',
    'N1_BANDS[267]', 'N1_BANDS[268]', 'get(267)', 'get(268)',
    '_c267', '_c268',
    '268: {"batch"', '267: {"batch"', '269: {"batch"',
    '268: {{"batch"', '269: {{"batch"', '268: {"a"', '267: {"a"',
    '269: {"a"', '268: {{"a"', '269: {{"a"', '266: {"batch"',
    "arith_a268", "arith_b268", "arith_a269", "arith_b269",
    "(263, 262, 261, 260, 259, 258, 257, 256, 255, 254)",
    "(264, 263, 262, 261, 260, 259, 258, 257, 256, 255)",
    "(265, 264, 263, 262, 261, 260, 259, 258, 257, 256)",
    "W254..W263", "W255..W264", "W256..W265",
    # ---- ordinals ----
    "len(owner_rows_live) == 257", "len(owner_rows_live) == 258",
    "257/130/86", "258/130/87", "bmc_rows=86", "bmc_rows=87",
    "rows 257 + candidate = 258th", "rows 258 + candidate = 259th",
    "owner_rows=257 / bma_rows=130 / bmc_rows=86",
    "owner_rows=258 / bma_rows=130 / bmc_rows=87",
    "; bm-c rows 86 +", "bm-c rows 86 + candidate = 87th owned",
    "bm-c rows 87 + candidate = 88th owned",
    "# candidate = 87th EXACT", "# candidate = 88th EXACT",
    "engine_owner==bm-c rows 86 + candidate",
    "engine_owner==bm-c rows 87 + candidate",
    "(87th own wave", "(88th own wave",
    "bm-c's 87th own wave", "bm-c's 88th own wave",
    "EIGHTY-SEVENTH owned", "EIGHTY-EIGHTH owned",
    "TWO HUNDRED AND SIXTY-EIGHTH", "TWO HUNDRED AND SIXTY-NINTH",
    "SEVENTEENTH", "EIGHTEENTH", "NINETEENTH",
    "seventeenth", "eighteenth", "nineteenth", "fifty-fourth",
    "bma rows 129 + candidate 130th",
    '"probe_receipt_bmc_ordinal_face": 86', '"probe_receipt_bmc_ordinal_face": 87',
    # ---- wave-number narrative ----
    "wave 268 engine_owner=bm-c", '"wave 268: "', "wave 268 = first free number",
    "wave 269 engine_owner=bm-c", '"wave 269: "', "wave 269 = first free number",
    # ---- prereg/commitment faces ----
    "PERPETUAL_N1_W268_PREREG", "PERPETUAL_N1_W269_PREREG",
    "PERPETUAL-N1-W268", "PERPETUAL-N1-W269",
    "bm-c r1090 window", "bm-a r1090 window", "# r1090 window", "r1090 commit",
    "bm-c r1092 window", "authored 13:1x", "authored 14:4x", "authored 10:5x",
    "2026-10-18 13:4x bm-c r1091 freeze window",
    # ---- cycle/lineage window stamps ----
    "r1088", "r1089", "r1090", "r1091", "r1092", "r1093",
    "12:3x", "13:1x", "13:4x", "13:5x", "14:0x", "14:1x", "14:4x",
    "cycle COMPLETE bm-c r1088+r1089 closeout 12:3x",
    "cycle COMPLETE bm-c r1091 closeout 14:1x",
    "the bm-c r1088 splice window", "bm-c r1088 splice window",
    "own-wave full cycle r1088+r1089", "own-wave full cycle r1091",
    "bm-c splice generation r1088 window", "bm-c splice generation r1091 window",
    "r1088, pre-seat probe", "verified r1089", "verified r1091",
    "# r1088 splice window", "# r1091 splice window",
    "(bm-c r1088", "(bm-c r1091", "r1089 BEFORE this freeze",
    "r1091 BEFORE this freeze", "r1089 MSG-", "r1091 MSG-",
    "finalize one-pass bm-c r1089 closeout, ledger",
    "finalize one-pass bm-c r1089 closeout ledger",
    "finalize one-pass bm-c r1089", "finalize one-pass bm-c r1091",
    "(R267: ", "(R268: ", "_w == 267", "_w == 268",
    "_w267bmc_freeze_edits.py template", "_w268bmc_freeze_edits.py template",
    "W268 FREEZE UNBLOCKED", "W269 FREEZE UNBLOCKED",
    "was published AFTER", "bm-a own-seat continuity",
    "bm-c own-seat continuity", "registered wave below 263 composes",
    "w244_a holds wave-263 bands", "w244_a", "w244_b", "n3r1_used245",
    "PENDING at seat", "waits-upstream face disclosed honest",
    "20261017", "20261018", "editor template",
]
counts = {f: t.count(f) for f in faces}

# ---- context dumps for ambiguous faces ----
def ctx(needle, maxhits=40):
    out = []
    for i, ln in enumerate(lines, 1):
        if needle in ln:
            out.append({"line": i, "text": ln.strip()[:220]})
    return out[:maxhits]

contexts = {}
for needle in ("r1088", "r1089", "r1090", "b9ad2f1119", "own W248..W266",
               "block parity", "fresh_legs", "+ 20,", "authored 13:1x",
               "r1089 MSG-", "pre-seat probe", "121 rows", "126 rows",
               "nineteen legs", "twenty legs", "bm-a r1090", "13:5x",
               "14:0x", "W269p", "W269 ", "cycle COMPLETE"):
    contexts[needle] = ctx(needle)

# ---- W269 prereg commit timestamp (authored-stamp basis) ----
prereg_ci = git("show", "-s", "--format=%ci", "67fe12710c").stdout.strip()
prereg_cf = git("show", "-s", "--format=%cI", "67fe12710c").stdout.strip()

# ---- W269 prereg on-disk vs origin blob identity (freeze-input verification) ----
preg = REPO + r"\research\PERPETUAL_N1_W269_PREREG.md"
preg_bytes = open(preg, "rb").read()
preg_sha256 = hashlib.sha256(preg_bytes).hexdigest()
preg_origin = git("show", "67fe12710c:research/PERPETUAL_N1_W269_PREREG.md").stdout

receipt = {
    "probe": "r1093 bm-c W269 editor needle preflight (r1077 measured-counts law, authoring-time re-measure)",
    "canon": {"path": "results/_w268bmc_freeze_edits.py", "blob_wt": blob_wt,
              "blob_head": blob_head, "blob_origin": blob_origin,
              "sha256_full": sha256_full, "sha16": sha256_full[:16],
              "bytes": len(t.encode("utf-8")),
              "wt_eq_head": blob_wt == blob_head, "wt_eq_origin": blob_wt == blob_origin},
    "w269_prereg": {"commit": "67fe12710c", "ci": prereg_ci, "cI": prereg_cf,
                    "disk_bytes": len(preg_bytes), "disk_sha256_16": preg_sha256[:16],
                    "expect_sha256_16": "cc13880752beb39e", "expect_bytes": 23207,
                    "disk_eq_expect": preg_sha256[:16] == "cc13880752beb39e" and len(preg_bytes) == 23207},
    "counts": counts,
    "contexts": contexts,
    "verdict": "MEASURED",
}
io.open(REPO + r"\results\_r1093bmc_needle_preflight.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print(json.dumps({"wt_eq_head": blob_wt == blob_head, "wt_eq_origin": blob_wt == blob_origin,
                  "sha16": sha256_full[:16], "bytes": len(t.encode("utf-8")),
                  "prereg_ci": prereg_ci, "prereg_ok": receipt["w269_prereg"]["disk_eq_expect"]}, indent=1))
print("KEY COUNTS:", json.dumps({k: counts.get(k, "MISSING") for k in (
    "W269p", "W269", "W268", "W267", "W266", "606_901", "607_100", "604_901",
    "606_900", "605_100", "606_700", "604_701", "604_900", "n1_w268", "n1_w267",
    "w268_", "w267_", "_w268bmc_", "r1088", "r1089", "r1090", "r1091", "r1092",
    "b9ad2f1119", "EIGHTEENTH", "SEVENTEENTH", "eighteenth", "seventeenth",
    "NINETEENTH", "W270p", "W270", "_set_wave(268)", "1,011,735", "585,320",
    "W265_W266_W267_bands_respected", "block = 126 rows", "authored 13:1x")}, indent=1))
