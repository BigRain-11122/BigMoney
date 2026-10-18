# -*- coding: utf-8 -*-
# r1097 bm-c: W271 five-face splice editor -- MEASURED needle preflight
# (r1077 measured-counts law; canon = results/_w270bmc_freeze_edits.py,
# committed by the r1095 splice window 1c814343ed; this probe re-measures
# EVERY candidate needle at authoring time + dumps ambiguous-face contexts
# (r-window numbers / seat shas / parity counts / stamps) for precise
# editor design. Read-only. Zero mutation.
# Receipt -> results/_r1097bmc_needle_preflight.json
# EOL LAW (r1093 autocrlf pit): the W271 prereg on DISK is the CRLF-smudged
# form of its LF origin blob (23,399B disk vs 23,336B blob) -- the prereg
# identity check below is git-object-level (HEAD blob sha256) + normalized
# disk compare ONLY; raw disk-bytes-vs-blob direct compare is FORBIDDEN
# (fake-DRIFT face, r1093 law).
import hashlib, io, json, subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = REPO + r"\results\_w270bmc_freeze_edits.py"

def git_bytes(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True).stdout

blob_wt = git_bytes("hash-object", CANON).decode().strip()
blob_head = git_bytes("rev-parse", "HEAD:results/_w270bmc_freeze_edits.py").decode().strip()
blob_origin = git_bytes("rev-parse", "origin/main:results/_w270bmc_freeze_edits.py").decode().strip()
sha256_full = hashlib.sha256(open(CANON, "rb").read()).hexdigest()

t = io.open(CANON, encoding="utf-8", newline="").read()
lines = t.split("\n")

faces = [
    # ---- projections ----
    "W272p", "W272", "W271p", "W271", "W270p", "W270", "W269p", "W269",
    # ---- blankets raw ----
    "W268", "W267", "W266", "W265",
    # ---- bands: own W270 + prior W269 + producers + next-gen W271 ----
    "611_301", "611_500", "609_301", "611_300", "609_500", "611_100",
    "609_101", "609_300",
    "611_501", "611_700", "613_300", "613_500", "613_501", "613_700",
    "607_101", "609_100", "607_300", "608_900",
    "606_901", "607_100",
    "602_501", "602_700", "602_701", "602_900", "604_500",
    "600_301", "600_500", "600_700", "602_300", "600_501", "602_500",
    "598_101", "598_300", "598_301", "600_300", "598_500", "600_100",
    "593901", "595901", "597900", "596101", "596300",
    # ---- ledger/K anchors ----
    "1,016,135", "589,720", "1_016_135", "589_720",
    "1,018,335", "591,920", "1,013,935", "587,520", "1_013_935", "587_520",
    "1,011,735", "585,320", "1,009,535", "583,120", "996,335",
    # ---- lowercase machine tokens ----
    "n1_w270", "n1_w269", "n1w270-", "n1w269-", "w270_", "w269_", "w271_",
    "n1_w271", "_w270bmc_", "_w271bmc_", "_w269bmc_",
    "n1_w270_results.json", "n1_w269_results.json",
    # ---- seat/sha faces ----
    "MSG-20261018-1605-bmc-w270-seat", "MSG-20261018-175x-bmc-w271-seat",
    "9f480646f4", "87d2697cdc", "440b07c94b", "1c814343ed",
    "3bb8b9308e", "f75b18c862", "d630d043b9", "67fe12710c",
    '"wave": 269', '"wave": 270', '"wave": 271',
    # ---- setwave aging faces ----
    "_set_wave(270)", "_set_wave(269)", "_set_wave(268)", "_set_wave(267)",
    "_set_wave(271)", "_set_wave(2)",
    # ---- relation-assert / bands-respected ----
    "W267_W268_W269_bands_respected", "W268_W269_W270_bands_respected",
    "W266_W267_W268_bands_respected",
    "A_staircase_hop_past_W270_B", "B_base_above_W270_tail",
    # ---- legs/parity faces ----
    "W211..W268 legs (58)", "W211..W268 fifty-eight legs",
    "W211..W269 legs 58", "own W248..W268 legs (21)", "own W248..W268",
    "W248..W268 twenty-one legs", 'N1_BANDS[") == 21',
    "W248..W270 legs (22", "block = 128 rows", "128 parity rows",
    "block parity = 128 rows", '"fresh_legs_row_asserts": 22', "+ 22,",
    "fifty-eighth", "fifty-eight legs", "fifty-ninth",
    "W211..W247 legs (37)", "W211..W247 verbatim (37 legs)",
    "W211..W247 thirty-seven legs", 'N1_BANDS[") == 37',
    # ---- count-gate numerals ----
    'N1_BANDS[") == 127,', '!= 127', 'N1_BANDS[") == 58',
    'N1_BANDS[") == 126,', '!= 126', 'N1_BANDS[") == 57',
    # ---- ranges ----
    "range(248, 270)", "range(248, 269)", "range(248, 271)",
    "range(211, 248)", "range(211, 269)", "range(211, 270)",
    "range(16, 270)", "range(16, 271)", "range(17, 270)", "range(17, 271)",
    "range(209, 271)", "range(209, 272)", "range(138, 207)",
    "if w < 270)", "if w < 269)", "if w < 271)",
    "270 - _lw", "271 - _lw", "m248", "m247", "m211",
    "N1_BANDS[248] ==", "N1_BANDS\\[248\\]",
    # ---- cfg/dict faces ----
    'WAVE_CONFIGS[270]', 'WAVE_CONFIGS[269]', 'WAVE_CONFIGS[271]',
    'N1_BANDS[269]', 'N1_BANDS[270]', 'get(269)', 'get(270)',
    '_c269', '_c270',
    '270: {"batch"', '269: {"batch"', '271: {"batch"',
    '270: {{"batch"', '271: {{"batch"', '270: {"a"', '269: {"a"',
    '271: {"a"', '270: {{"a"', '269: {{"a"', '271: {{"a"',
    "arith_a270", "arith_b270", "arith_a271", "arith_b271",
    "(266, 265, 264, 263, 262, 261, 260, 259, 258, 257)",
    "(267, 266, 265, 264, 263, 262, 261, 260, 259, 258)",
    "W257..W266", "W258..W267",
    # ---- ordinals ----
    "len(owner_rows_live) == 259", "len(owner_rows_live) == 260",
    "259/130/88", "260/130/89", "bmc_rows=88", "bmc_rows=89",
    "rows 259 + candidate = 260th", "rows 260 + candidate = 261st",
    "owner_rows=259 / bma_rows=130 / bmc_rows=88",
    "owner_rows=260 / bma_rows=130 / bmc_rows=89",
    "; bm-c rows 88 +", "bm-c rows 88 + candidate = 89th owned",
    "bm-c rows 89 + candidate = 90th owned",
    "# candidate = 89th EXACT", "# candidate = 90th EXACT",
    "engine_owner==bm-c rows 88 + candidate",
    "engine_owner==bm-c rows 89 + candidate",
    "(89th own wave", "(90th own wave",
    "bm-c's 89th own wave", "bm-c's 90th own wave",
    "EIGHTY-NINTH owned", "NINETIETH owned",
    "TWO HUNDRED AND SEVENTIETH", "TWO HUNDRED AND SEVENTY-FIRST",
    "NINETEENTH", "TWENTIETH", "TWENTY-FIRST", "nineteenth", "twentieth",
    "twenty-first", "fifty-eighth consecutive",
    "bma rows 129 + candidate 130th",
    '"probe_receipt_bmc_ordinal_face": 88', '"probe_receipt_bmc_ordinal_face": 89',
    # ---- wave-number narrative ----
    "wave 270 engine_owner=bm-c", '"wave 270: "',
    "wave 270 = first free number", "wave 271 engine_owner=bm-c",
    # ---- prereg/commitment faces ----
    "PERPETUAL_N1_W270_PREREG", "PERPETUAL_N1_W271_PREREG",
    "PERPETUAL-N1-W270", "PERPETUAL-N1-W271",
    "bm-c r1094 window", "# r1094 window", "r1094 commit",
    "bm-c r1096 window", "r1096 commit",
    "authored 16:3x", "authored 17:5x",
    "2026-10-18 17:0x bm-c r1095 freeze window",
    "W270 materializer face", "W271 materializer face",
    "W269 materializer face", "W270 block", "W271 block",
    "post-W269-REGISTERED", "post-W270-REGISTERED",
    "W270 FREEZE UNBLOCKED", "W271 FREEZE UNBLOCKED",
    "anchors W269 1,016,135 / K=589,720 at draft",
    "dual-window parity", "W271 walk", "W272 walk",
    # ---- cycle/lineage window stamps ----
    "r1091", "r1092", "r1093", "r1094", "r1095", "r1096", "r1097",
    "14:1x", "15:2x", "15:4x", "16:2x", "16:3x", "17:0x", "17:3x", "17:5x",
    "cycle COMPLETE bm-c r1093 closeout 15:4x",
    "the bm-c r1093 splice window", "own-wave full cycle r1093",
    "bm-c splice generation r1093 window", "verified r1093",
    "# r1093 splice window", "(bm-c r1093", "r1093 MSG-",
    "finalize one-pass bm-c r1093 closeout, ledger",
    "finalize one-pass bm-c r1093 closeout ledger",
    "finalize one-pass bm-c r1093",
    "seat itself r1094; queue-head",
    "(r1094, queue-head seat-first supply",
    "(R269: ", "(R270: ", "_w == 269", "_w == 270",
    "_w269bmc_freeze_edits.py template", "_w270bmc_freeze_edits.py template",
    "bm-c own-seat continuity", "registered wave below 263 composes",
    "w244_a", "w244_b", "n3r1_used245",
    "PENDING at seat", "waits-upstream face disclosed honest",
    "20261017", "20261018", "editor template", "pre-W270-universe",
    "fourteen-wave", "PRE-W270-splice", "PRE-W271-splice",
    "post-W269 registration", "post-W270 registration",
    "bm-c five-face freeze upstream seat", "bm-c (upstream seat honored)",
    "owner=bm-c seat honored", "was published AFTER",
    "expect 259/130/88", "expect 260/130/89",
    "bm-a's EIGHTY-NINTH owned claim",
    "W269 finalize product", "W270 finalize product",
    "594 rows", "physical bytes",
]
counts = {f: t.count(f) for f in faces}

def ctx(needle, maxhits=40):
    out = []
    for i, ln in enumerate(lines, 1):
        if needle in ln:
            out.append({"line": i, "text": ln.strip()[:230]})
    return out[:maxhits]

contexts = {}
for needle in ("r1093", "r1094", "r1095", "r1096", "W271p", "W271 ", "authored",
               "pre-W270", "595901", "RAM", "free RAM", "bmc_rows=88",
               "n1_w270", "n1_w269", "w270_", "w269_", "17:0x", "17:5x",
               "W270 FREEZE", "wave 270", "own W248..W268", "block parity",
               "_set_wave(", "fifty-eighth", "dual-window", "PRE-W270",
               "W271 walk", "W272 walk", "EIGHTY-NINTH"):
    contexts[needle] = ctx(needle)

# ---- W271 prereg frozen-face identity (git-object-level, r1093 EOL law) ----
preg_path = "research/PERPETUAL_N1_W271_PREREG.md"
preg_blob_head = git_bytes("show", "HEAD:" + preg_path)
preg_blob_origin = git_bytes("show", "origin/main:" + preg_path)
preg_disk = open(REPO + r"\research\PERPETUAL_N1_W271_PREREG.md", "rb").read()
norm_eq_head = (preg_disk.decode("utf-8", errors="replace").replace("\r\n", "\n")
               == preg_blob_head.decode("utf-8", errors="replace").replace("\r\n", "\n"))
receipt = {
    "probe": "r1097 bm-c W271 editor needle preflight (r1077 measured-counts law, authoring-time re-measure)",
    "canon": {"path": "results/_w270bmc_freeze_edits.py", "blob_wt": blob_wt,
              "blob_head": blob_head, "blob_origin": blob_origin,
              "sha256_full": sha256_full, "sha16": sha256_full[:16],
              "bytes": len(t.encode("utf-8")),
              "wt_eq_head": blob_wt == blob_head, "wt_eq_origin": blob_wt == blob_origin},
    "w271_prereg": {
        "frozen_face_commit": "f75b18c862 (r1096, pre-backfill -- sec.7/8 placeholders still unfilled)",
        "head_blob_sha256_16": hashlib.sha256(preg_blob_head).hexdigest()[:16],
        "head_blob_bytes": len(preg_blob_head),
        "expect_sha256_16": "f8b4a755d81bfbe5", "expect_bytes": 23336,
        "head_eq_expect": (hashlib.sha256(preg_blob_head).hexdigest()[:16] == "f8b4a755d81bfbe5"
                           and len(preg_blob_head) == 23336),
        "head_eq_origin_blob": preg_blob_head == preg_blob_origin,
        "disk_bytes_crlf_smudged": len(preg_disk),
        "disk_norm_eq_head_blob": norm_eq_head,
        "eol_law_note": "disk = CRLF re-smudge of the LF blob (autocrlf); raw disk-vs-blob compare FORBIDDEN per r1093 pit law; norm-eq governs"},
    "counts": counts,
    "contexts": contexts,
    "verdict": "MEASURED",
}
io.open(REPO + r"\results\_r1097bmc_needle_preflight.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print(json.dumps({"wt_eq_head": blob_wt == blob_head, "wt_eq_origin": blob_wt == blob_origin,
                  "sha16": sha256_full[:16], "bytes": len(t.encode("utf-8")),
                  "prereg_ok": receipt["w271_prereg"]["head_eq_expect"],
                  "prereg_norm_eq": norm_eq_head,
                  "prereg_origin_eq": preg_blob_head == preg_blob_origin}, indent=1))
print("KEY COUNTS:", json.dumps({k: counts.get(k, "MISSING") for k in (
    "W271p", "W271", "W272p", "W270", "W269", "W268", "W267",
    "611_301", "611_500", "609_301", "611_300", "609_500", "611_100",
    "609_101", "609_300", "611_501", "613_500", "613_501", "613_700",
    "1,016,135", "589,720", "1,018,335", "n1_w270", "n1_w269",
    "w270_", "w269_", "w271_", "_w270bmc_", "_w271bmc_",
    "r1093", "r1094", "r1095", "r1096", "87d2697cdc", "f75b18c862",
    "1c814343ed", "9f480646f4", "3bb8b9308e",
    "TWENTIETH", "NINETEENTH", "TWENTY-FIRST", "twentieth", "nineteenth",
    "W272p", "_set_wave(270)", "996,335", "pre-W270-universe",
    "bmc_rows=88", "bmc_rows=89", "EIGHTY-NINTH owned",
    "W267_W268_W269_bands_respected", "block = 128 rows", "authored 17:5x",
    "bm-c r1096 window", "17:0x", "MSG-20261018-175x-bmc-w271-seat",
    "W271 FREEZE UNBLOCKED", "PRE-W270-splice", "PRE-W271-splice",
    "W270 FREEZE UNBLOCKED", "own W248..W268 legs (21", "W248..W270 legs (22",
    "W211..W268 legs (58", "W211..W269 legs 58", "fifty-eighth",
    "len(owner_rows_live) == 259", "len(owner_rows_live) == 260",
    "range(248, 270)", "range(209, 271)", "if w < 270)", "270 - _lw",
    "arith_a270", "arith_a271", "W271 walk", "W272 walk",
    "W270 materializer face", "W271 materializer face",
    "W269 finalize product", "W270 finalize product",
    "post-W269-REGISTERED", "post-W270-REGISTERED",
    "PERPETUAL_N1_W271_PREREG", "PERPETUAL_N1_W270_PREREG")}, indent=1))
