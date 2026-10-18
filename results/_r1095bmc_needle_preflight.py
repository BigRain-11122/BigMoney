# -*- coding: utf-8 -*-
# r1095 bm-c: W270 five-face splice editor -- MEASURED needle preflight
# (r1077 measured-counts law; canon = results/_w269bmc_freeze_edits.py,
# committed by the r1093 splice window 440b07c94b; this probe re-measures
# EVERY candidate needle at authoring time + dumps ambiguous-face contexts
# (r-window numbers / seat shas / parity counts / stamps) for precise
# editor design. Read-only. Zero mutation.
# Receipt -> results/_r1095bmc_needle_preflight.json
import hashlib, io, json, subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = REPO + r"\results\_w269bmc_freeze_edits.py"

def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, encoding="utf-8", errors="replace")

blob_wt = git("hash-object", CANON).stdout.strip()
blob_head = git("rev-parse", "HEAD:results/_w269bmc_freeze_edits.py").stdout.strip()
blob_origin = git("rev-parse", "origin/main:results/_w269bmc_freeze_edits.py").stdout.strip()
sha256_full = hashlib.sha256(open(CANON, "rb").read()).hexdigest()

t = io.open(CANON, encoding="utf-8", newline="").read()
lines = t.split("\n")

faces = [
    # ---- projections ----
    "W270p", "W270", "W271p", "W271", "W269p", "W269", "W268p",
    # ---- blankets raw ----
    "W268", "W267", "W266", "W265",
    # ---- bands: current W269 + prior W268 + producers + next-gen ----
    "609_101", "609_300", "607_101", "609_100", "607_300", "608_900",
    "606_901", "607_100", "604_901", "606_900", "605_100", "606_700",
    "604_701", "604_900",
    "611_301", "611_500", "609_301", "611_300", "609_500", "611_100",
    "611_501", "611_700", "613_300",
    "602_501", "602_700", "602_701", "602_900", "604_500",
    "600_301", "600_500", "600_700", "602_300", "600_501", "602_500",
    "598_101", "598_300", "598_301", "600_300", "598_500", "600_100",
    "593901", "595901", "597900", "596101", "596300",
    # ---- ledger/K anchors ----
    "1,013,935", "587,520", "1_013_935", "587_520",
    "1,016,135", "589,720", "1,011,735", "585,320", "1_009_535", "583_120",
    "996,335",
    # ---- lowercase machine tokens ----
    "n1_w269", "n1_w268", "n1w269-", "n1w268-", "w269_", "w268_", "w270_",
    "n1_w270", "_w269bmc_", "_w270bmc_", "_w268bmc_",
    "n1_w269_results.json", "n1_w268_results.json",
    # ---- seat/sha faces ----
    "MSG-20261018-1407-bmc-w269-seat", "MSG-20261018-1605-bmc-w270-seat",
    "d630d043b9", "9f480646f4", "8bc7ac759e", "440b07c94b",
    "67fe12710c", "3bb8b9308e", '"wave": 268', '"wave": 269', '"wave": 270',
    # ---- setwave aging faces ----
    "_set_wave(269)", "_set_wave(268)", "_set_wave(267)", "_set_wave(266)",
    "_set_wave(270)", "_set_wave(2)",
    # ---- relation-assert / bands-respected ----
    "W266_W267_W268_bands_respected", "W267_W268_W269_bands_respected",
    "W265_W266_W267_bands_respected",
    "A_staircase_hop_past_W269_B", "B_base_above_W269_tail",
    # ---- legs/parity faces ----
    "W211..W267 legs (57)", "W211..W267 fifty-seven legs",
    "W211..W268 legs 57", "own W248..W267 legs (20)", "own W248..W267",
    "W248..W267 twenty legs", 'N1_BANDS[") == 20',
    "W248..W269 legs (21", "block = 127 rows", "127 parity rows",
    "block parity = 127 rows", '"fresh_legs_row_asserts": 21', "+ 21,",
    "fifty-seventh", "fifty-seven legs", "fifty-eighth",
    "W211..W247 legs (37)", "W211..W247 verbatim (37 legs)",
    "W211..W247 thirty-seven legs", 'N1_BANDS[") == 37',
    # ---- count-gate numerals ----
    'N1_BANDS[") == 126,', '!= 126', 'N1_BANDS[") == 57',
    'N1_BANDS[") == 125,', '!= 125', 'N1_BANDS[") == 56',
    # ---- ranges ----
    "range(248, 269)", "range(248, 268)", "range(248, 270)",
    "range(211, 248)", "range(211, 268)", "range(211, 269)",
    "range(16, 269)", "range(16, 270)", "range(17, 269)", "range(17, 270)",
    "range(209, 270)", "range(209, 271)", "range(138, 207)",
    "if w < 269)", "if w < 268)", "if w < 270)",
    "269 - _lw", "270 - _lw", "m248", "m247", "m211",
    "N1_BANDS[248] ==", "N1_BANDS\\[248\\]",
    # ---- cfg/dict faces ----
    'WAVE_CONFIGS[269]', 'WAVE_CONFIGS[268]', 'WAVE_CONFIGS[270]',
    'N1_BANDS[268]', 'N1_BANDS[269]', 'get(268)', 'get(269)',
    '_c268', '_c269',
    '269: {"batch"', '268: {"batch"', '270: {"batch"',
    '269: {{"batch"', '270: {{"batch"', '269: {"a"', '268: {"a"',
    '270: {"a"', '269: {{"a"', '268: {{"a"', '270: {{"a"',
    "arith_a269", "arith_b269", "arith_a270", "arith_b270",
    "(264, 263, 262, 261, 260, 259, 258, 257, 256, 255)",
    "(265, 264, 263, 262, 261, 260, 259, 258, 257, 256)",
    "(266, 265, 264, 263, 262, 261, 260, 259, 258, 257)",
    "W256..W265", "W257..W266",
    # ---- ordinals ----
    "len(owner_rows_live) == 258", "len(owner_rows_live) == 259",
    "258/130/87", "259/130/88", "bmc_rows=87", "bmc_rows=88",
    "rows 258 + candidate = 259th", "rows 259 + candidate = 260th",
    "owner_rows=258 / bma_rows=130 / bmc_rows=87",
    "owner_rows=259 / bma_rows=130 / bmc_rows=88",
    "; bm-c rows 87 +", "bm-c rows 87 + candidate = 88th owned",
    "bm-c rows 88 + candidate = 89th owned",
    "# candidate = 88th EXACT", "# candidate = 89th EXACT",
    "engine_owner==bm-c rows 87 + candidate",
    "engine_owner==bm-c rows 88 + candidate",
    "(88th own wave", "(89th own wave",
    "bm-c's 88th own wave", "bm-c's 89th own wave",
    "EIGHTY-EIGHTH owned", "EIGHTY-NINTH owned",
    "TWO HUNDRED AND SIXTY-NINTH", "TWO HUNDRED AND SEVENTIETH",
    "NINETEENTH", "EIGHTEENTH", "TWENTIETH", "nineteenth", "eighteenth",
    "twentieth", "fifty-seventh consecutive",
    "bma rows 129 + candidate 130th",
    '"probe_receipt_bmc_ordinal_face": 87', '"probe_receipt_bmc_ordinal_face": 88',
    # ---- wave-number narrative ----
    "wave 269 engine_owner=bm-c", '"wave 269: "',
    "wave 269 = first free number", "wave 270 engine_owner=bm-c",
    # ---- prereg/commitment faces ----
    "PERPETUAL_N1_W269_PREREG", "PERPETUAL_N1_W270_PREREG",
    "PERPETUAL-N1-W269", "PERPETUAL-N1-W270",
    "bm-c r1092 window", "# r1092 window", "r1092 commit",
    "bm-c r1094 window", "authored 14:4x", "authored 16:3x", "authored 16:2x",
    "2026-10-18 15:2x bm-c r1093 freeze window",
    "W269 materializer face", "W270 materializer face",
    "W268 materializer face", "W269 block", "W270 block",
    "post-W268-REGISTERED", "post-W269-REGISTERED",
    "W269 FREEZE UNBLOCKED", "W270 FREEZE UNBLOCKED",
    "anchors W268 1,013,935 / K=587,520 at draft",
    "dual-window parity", "W270 walk", "W271 walk",
    # ---- cycle/lineage window stamps ----
    "r1091", "r1092", "r1093", "r1094", "r1095",
    "12:3x", "13:1x", "14:0x", "14:1x", "14:4x", "15:2x", "15:4x", "16:2x",
    "cycle COMPLETE bm-c r1091 closeout 14:1x",
    "the bm-c r1091 splice window", "own-wave full cycle r1091",
    "bm-c splice generation r1091 window", "verified r1091",
    "# r1091 splice window", "(bm-c r1091", "r1091 BEFORE this freeze",
    "r1091 MSG-", "finalize one-pass bm-c r1091 closeout, ledger",
    "finalize one-pass bm-c r1091 closeout ledger",
    "finalize one-pass bm-c r1091", "finalize one-pass bm-c r1093",
    "seat itself r1091; queue-head",
    "(r1091, queue-head seat-first supply",
    "(R268: ", "(R269: ", "_w == 268", "_w == 269",
    "_w268bmc_freeze_edits.py template", "_w269bmc_freeze_edits.py template",
    "bm-c own-seat continuity", "registered wave below 263 composes",
    "w244_a holds wave-263 bands", "w244_a", "w244_b", "n3r1_used245",
    "PENDING at seat", "waits-upstream face disclosed honest",
    "20261017", "20261018", "editor template", "pre-W269-universe",
    "fourteen-wave",
]
counts = {f: t.count(f) for f in faces}

def ctx(needle, maxhits=40):
    out = []
    for i, ln in enumerate(lines, 1):
        if needle in ln:
            out.append({"line": i, "text": ln.strip()[:230]})
    return out[:maxhits]

contexts = {}
for needle in ("r1091", "r1092", "r1093", "r1094", "W270p", "W270 ", "authored",
               "pre-W269", "595901", "RAM", "free RAM", "bmc_rows=87",
               "n1_w269", "n1_w268", "w269_", "w268_", "14:4x", "15:2x",
               "W269 FREEZE", "wave 269", "own W248..W267", "block parity",
               "_set_wave(", "16:2x", "fifty-seventh", "dual-window"):
    contexts[needle] = ctx(needle)

# ---- W270 prereg on-disk vs committed blob identity (freeze-input verification) ----
preg = REPO + r"\research\PERPETUAL_N1_W270_PREREG.md"
preg_bytes = open(preg, "rb").read()
preg_sha256 = hashlib.sha256(preg_bytes).hexdigest()
preg_head_blob = git("show", "HEAD:research/PERPETUAL_N1_W270_PREREG.md").stdout
preg_origin_blob = git("show", "origin/main:research/PERPETUAL_N1_W270_PREREG.md").stdout
norm_eq_head = preg_head_blob.replace("\r\n", "\n") == preg_bytes.decode("utf-8", errors="replace").replace("\r\n", "\n")

receipt = {
    "probe": "r1095 bm-c W270 editor needle preflight (r1077 measured-counts law, authoring-time re-measure)",
    "canon": {"path": "results/_w269bmc_freeze_edits.py", "blob_wt": blob_wt,
              "blob_head": blob_head, "blob_origin": blob_origin,
              "sha256_full": sha256_full, "sha16": sha256_full[:16],
              "bytes": len(t.encode("utf-8")),
              "wt_eq_head": blob_wt == blob_head, "wt_eq_origin": blob_wt == blob_origin},
    "w270_prereg": {"commit": "3bb8b9308e", "disk_bytes": len(preg_bytes),
                    "disk_sha256_16": preg_sha256[:16],
                    "expect_sha256_16": "3aa0b98239369608", "expect_bytes": 23259,
                    "disk_eq_expect": preg_sha256[:16] == "3aa0b98239369608" and len(preg_bytes) == 23259,
                    "norm_eq_head_blob": norm_eq_head,
                    "head_eq_origin_blob": preg_head_blob == preg_origin_blob},
    "counts": counts,
    "contexts": contexts,
    "verdict": "MEASURED",
}
io.open(REPO + r"\results\_r1095bmc_needle_preflight.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print(json.dumps({"wt_eq_head": blob_wt == blob_head, "wt_eq_origin": blob_wt == blob_origin,
                  "sha16": sha256_full[:16], "bytes": len(t.encode("utf-8")),
                  "prereg_ok": receipt["w270_prereg"]["disk_eq_expect"],
                  "prereg_norm_eq": norm_eq_head}, indent=1))
print("KEY COUNTS:", json.dumps({k: counts.get(k, "MISSING") for k in (
    "W270p", "W270", "W269", "W268", "W267", "609_101", "609_300", "607_101",
    "609_100", "607_300", "608_900", "606_901", "607_100", "n1_w269", "n1_w268",
    "w269_", "w268_", "_w269bmc_", "r1091", "r1092", "r1093", "r1094",
    "d630d043b9", "NINETEENTH", "EIGHTEENTH", "nineteenth", "eighteenth",
    "W271p", "_set_wave(269)", "1,013,935", "587,520",
    "W266_W267_W268_bands_respected", "block = 127 rows", "authored 14:4x",
    "bmc_rows=87", "996,335", "pre-W269-universe")}, indent=1))
