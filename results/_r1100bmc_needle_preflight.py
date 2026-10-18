# -*- coding: utf-8 -*-
# r1100 bm-c: W272 five-face splice editor -- MEASURED needle preflight
# (r1077 measured-counts law; canon = results/_w271bmc_freeze_edits.py,
# committed by the r1097 splice window 7dd091eef1; this probe re-measures
# EVERY candidate needle at authoring time + dumps ambiguous-face contexts
# (r-window numbers / seat shas / parity counts / stamps) for precise
# editor design. Read-only. Zero mutation.
# Receipt -> results/_r1100bmc_needle_preflight.json
# EOL LAW (r1093 autocrlf pit): the W272 prereg on DISK is the CRLF-smudged
# form of its LF origin blob (disk vs 23,409B blob) -- the prereg identity
# check below is git-object-level (HEAD blob sha256) + normalized disk
# compare ONLY; raw disk-bytes-vs-blob direct compare is FORBIDDEN
# (fake-DRIFT face, r1093 law).
import hashlib, io, json, subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = REPO + r"\results\_w271bmc_freeze_edits.py"

def git_bytes(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True).stdout

blob_wt = git_bytes("hash-object", CANON).decode().strip()
blob_head = git_bytes("rev-parse", "HEAD:results/_w271bmc_freeze_edits.py").decode().strip()
blob_origin = git_bytes("rev-parse", "origin/main:results/_w271bmc_freeze_edits.py").decode().strip()
sha256_full = hashlib.sha256(open(CANON, "rb").read()).hexdigest()

t = io.open(CANON, encoding="utf-8", newline="").read()
lines = t.split("\n")

faces = [
    # ---- projections ----
    "W273p", "W273", "W272p", "W272", "W271p", "W271", "W270p", "W270",
    # ---- blankets raw ----
    "W269", "W268", "W267", "W266",
    # ---- bands: own W271 + prior W270 + producers + next-gen W272 ----
    "613_501", "613_700", "611_501", "613_500", "611_700", "613_300",
    "611_301", "611_500",
    "613_701", "615_500", "613_900", "615_700", "615_701", "615_900",
    "609_101", "611_100", "609_300", "610_900",
    "608_901", "609_100",
    "604_501", "604_700", "604_701", "604_900", "606_500",
    "602_301", "602_500", "602_700", "604_300", "602_501", "604_500",
    "600_101", "600_300", "600_301", "602_300", "600_500", "602_100",
    "595901", "597901", "599900", "598101", "598300",
    # ---- ledger/K anchors ----
    "1,018,335", "591,920", "1_018_335", "591_920",
    "1,020,535", "594,120", "1_020_535", "594_120",
    "1,013,935", "587,520", "1_013_935", "587_520",
    "1,016,135", "589,720", "996,335",
    # ---- lowercase machine tokens ----
    "n1_w271", "n1_w270", "n1w271-", "n1w270-", "w271_", "w270_", "w272_",
    "n1_w272", "_w271bmc_", "_w272bmc_", "_w270bmc_",
    "n1_w271_results.json", "n1_w270_results.json",
    # ---- seat/sha faces ----
    "MSG-20261018-175x-bmc-w271-seat", "MSG-20261018-191x-bmc-w272-seat",
    "87d2697cdc", "f608ff1cee", "1c814343ed", "7dd091eef1",
    "f75b18c862", "c049a57623", "d630d043b9", "67fe12710c",
    "9f480646f4", "3bb8b9308e", "440b07c94b",
    '"wave": 270', '"wave": 271', '"wave": 272',
    # ---- setwave aging faces ----
    "_set_wave(271)", "_set_wave(270)", "_set_wave(269)", "_set_wave(268)",
    "_set_wave(272)", "_set_wave(2)",
    # ---- relation-assert / bands-respected ----
    "W268_W269_W270_bands_respected", "W269_W270_W271_bands_respected",
    "W267_W268_W269_bands_respected",
    "A_staircase_hop_past_W271_B", "B_base_above_W271_tail",
    # ---- legs/parity faces ----
    "W211..W269 legs (59)", "W211..W269 fifty-nine legs",
    "W211..W270 legs 59", "own W248..W269 legs (22)", "own W248..W269",
    "W248..W269 twenty-two legs", 'N1_BANDS[") == 22',
    "W248..W271 legs (23", "block = 129 rows", "129 parity rows",
    "block parity = 129 rows", '"fresh_legs_row_asserts": 23', "+ 23,",
    "fifty-ninth", "fifty-nine legs", "sixtieth",
    "W211..W247 legs (37)", "W211..W247 verbatim (37 legs)",
    "W211..W247 thirty-seven legs", 'N1_BANDS[") == 37',
    # ---- count-gate numerals ----
    'N1_BANDS[") == 128,', '!= 128', 'N1_BANDS[") == 59',
    'N1_BANDS[") == 129,', '!= 129', 'N1_BANDS[") == 60',
    # ---- ranges ----
    "range(248, 271)", "range(248, 270)", "range(248, 272)",
    "range(211, 248)", "range(211, 270)", "range(211, 271)",
    "range(16, 271)", "range(16, 272)", "range(17, 271)", "range(17, 272)",
    "range(209, 272)", "range(209, 273)", "range(138, 207)",
    "if w < 271)", "if w < 270)", "if w < 272)",
    "271 - _lw", "272 - _lw", "m248", "m247", "m211",
    "N1_BANDS[248] ==", "N1_BANDS\\[248\\]",
    # ---- cfg/dict faces ----
    'WAVE_CONFIGS[271]', 'WAVE_CONFIGS[270]', 'WAVE_CONFIGS[272]',
    'N1_BANDS[270]', 'N1_BANDS[271]', 'get(270)', 'get(271)',
    '_c270', '_c271',
    '271: {"batch"', '270: {"batch"', '272: {"batch"',
    '271: {{"batch"', '272: {{"batch"', '271: {"a"', '270: {"a"',
    '272: {"a"', '270: {{"a"', '271: {{"a"', '272: {{"a"',
    "arith_a271", "arith_b271", "arith_a272", "arith_b272",
    "(267, 266, 265, 264, 263, 262, 261, 260, 259, 258)",
    "(268, 267, 266, 265, 264, 263, 262, 261, 260, 259)",
    "W258..W267", "W259..W268",
    # ---- ordinals ----
    "len(owner_rows_live) == 260", "len(owner_rows_live) == 261",
    "260/130/89", "261/130/90", "bmc_rows=89", "bmc_rows=90",
    "rows 260 + candidate = 261st", "rows 261 + candidate = 262nd",
    "owner_rows=260 / bma_rows=130 / bmc_rows=89",
    "owner_rows=261 / bma_rows=130 / bmc_rows=90",
    "; bm-c rows 89 +", "bm-c rows 89 + candidate = 90th owned",
    "bm-c rows 90 + candidate = 91st owned",
    "# candidate = 90th EXACT", "# candidate = 91st EXACT",
    "engine_owner==bm-c rows 89 + candidate",
    "engine_owner==bm-c rows 90 + candidate",
    "(90th own wave", "(91st own wave",
    "bm-c's 90th own wave", "bm-c's 91st own wave",
    "NINETIETH owned", "NINETY-FIRST owned",
    "TWO HUNDRED AND SEVENTY-FIRST", "TWO HUNDRED AND SEVENTY-SECOND",
    "TWENTIETH", "TWENTY-FIRST", "TWENTY-SECOND", "twentieth", "twenty-first",
    "twenty-second", "fifty-ninth consecutive",
    "bma rows 129 + candidate 130th",
    '"probe_receipt_bmc_ordinal_face": 89', '"probe_receipt_bmc_ordinal_face": 90',
    # ---- wave-number narrative ----
    "wave 271 engine_owner=bm-c", '"wave 271: "',
    "wave 271 = first free number", "wave 272 engine_owner=bm-c",
    # ---- prereg/commitment faces ----
    "PERPETUAL_N1_W271_PREREG", "PERPETUAL_N1_W272_PREREG",
    "PERPETUAL-N1-W271", "PERPETUAL-N1-W272",
    "bm-c r1096 window", "# r1096 window", "r1096 commit",
    "bm-c r1099 window", "r1099 commit",
    "authored 17:5x", "authored 19:2x",
    "2026-10-18 18:2x bm-c r1097 freeze window",
    "W271 materializer face", "W272 materializer face",
    "W270 materializer face", "W271 block", "W272 block",
    "post-W270-REGISTERED", "post-W271-REGISTERED",
    "W271 FREEZE UNBLOCKED", "W272 FREEZE UNBLOCKED",
    "anchors W271 1,020,535 / K=594,120 at draft",
    "dual-window parity", "W272 walk", "W273 walk",
    # ---- cycle/lineage window stamps ----
    "r1094", "r1095", "r1096", "r1097", "r1098", "r1099", "r1100",
    "16:2x", "16:3x", "17:0x", "17:3x", "17:5x", "18:2x", "18:4x", "19:1x", "19:2x",
    "cycle COMPLETE bm-c r1095 closeout 17:3x",
    "the bm-c r1095 splice window", "own-wave full cycle r1095",
    "bm-c splice generation r1095 window", "verified r1095",
    "# r1095 splice window", "(bm-c r1095", "r1095 MSG-",
    "finalize one-pass bm-c r1095 closeout, ledger",
    "finalize one-pass bm-c r1095 closeout ledger",
    "finalize one-pass bm-c r1095",
    "seat itself r1096; queue-head",
    "(r1096, queue-head seat-first supply",
    "(R270: ", "(R271: ", "_w == 270", "_w == 271",
    "_w270bmc_freeze_edits.py template", "_w271bmc_freeze_edits.py template",
    "bm-c own-seat continuity", "registered wave below 263 composes",
    "w244_a", "w244_b", "n3r1_used245",
    "PENDING at seat", "waits-upstream face disclosed honest",
    "20261017", "20261018", "editor template", "pre-W271-universe",
    "fourteen-wave", "PRE-W271-splice", "PRE-W272-splice",
    "post-W270 registration", "post-W271 registration",
    "bm-c five-face freeze upstream seat", "bm-c (upstream seat honored)",
    "owner=bm-c seat honored", "was published AFTER",
    "expect 260/130/89", "expect 261/130/90",
    "bm-a's NINETIETH owned claim",
    "W270 finalize product", "W271 finalize product",
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
for needle in ("r1095", "r1096", "r1097", "r1098", "W272p", "W272 ", "authored",
               "pre-W271", "611_501", "RAM", "free RAM", "bmc_rows=89",
               "n1_w271", "n1_w270", "w270_", "w271_", "18:2x", "19:2x",
               "W271 FREEZE", "wave 271", "own W248..W269", "block parity",
               "_set_wave(", "fifty-ninth", "dual-window", "PRE-W271",
               "W272 walk", "W273 walk", "NINETIETH"):
    contexts[needle] = ctx(needle)

# ---- W272 prereg frozen-face identity (git-object-level, r1093 EOL law) ----
preg_path = "research/PERPETUAL_N1_W272_PREREG.md"
preg_blob_head = git_bytes("show", "HEAD:" + preg_path)
preg_blob_origin = git_bytes("show", "origin/main:" + preg_path)
preg_disk = open(REPO + r"\research\PERPETUAL_N1_W272_PREREG.md", "rb").read()
norm_eq_head = (preg_disk.decode("utf-8", errors="replace").replace("\r\n", "\n")
               == preg_blob_head.decode("utf-8", errors="replace").replace("\r\n", "\n"))
receipt = {
    "probe": "r1100 bm-c W272 editor needle preflight (r1077 measured-counts law, authoring-time re-measure)",
    "canon": {"path": "results/_w271bmc_freeze_edits.py", "blob_wt": blob_wt,
              "blob_head": blob_head, "blob_origin": blob_origin,
              "sha256_full": sha256_full, "sha16": sha256_full[:16],
              "bytes": len(t.encode("utf-8")),
              "wt_eq_head": blob_wt == blob_head, "wt_eq_origin": blob_wt == blob_origin},
    "w272_prereg": {
        "frozen_face_commit": "c049a57623 (r1099, pre-backfill -- sec.7/8 placeholders still unfilled)",
        "head_blob_sha256_16": hashlib.sha256(preg_blob_head).hexdigest()[:16],
        "head_blob_bytes": len(preg_blob_head),
        "expect_sha256_16": "b023511eba80a9bf", "expect_bytes": 23409,
        "head_eq_expect": (hashlib.sha256(preg_blob_head).hexdigest()[:16] == "b023511eba80a9bf"
                           and len(preg_blob_head) == 23409),
        "head_eq_origin_blob": preg_blob_head == preg_blob_origin,
        "disk_bytes_crlf_smudged": len(preg_disk),
        "disk_norm_eq_head_blob": norm_eq_head,
        "eol_law_note": "disk = CRLF re-smudge of the LF blob (autocrlf); raw disk-vs-blob compare FORBIDDEN per r1093 pit law; norm-eq governs"},
    "counts": counts,
    "contexts": contexts,
    "verdict": "MEASURED",
}
io.open(REPO + r"\results\_r1100bmc_needle_preflight.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print(json.dumps({"wt_eq_head": blob_wt == blob_head, "wt_eq_origin": blob_wt == blob_origin,
                  "sha16": sha256_full[:16], "bytes": len(t.encode("utf-8")),
                  "prereg_ok": receipt["w272_prereg"]["head_eq_expect"],
                  "prereg_norm_eq": norm_eq_head,
                  "prereg_origin_eq": preg_blob_head == preg_blob_origin}, indent=1))
print("KEY COUNTS:", json.dumps({k: counts.get(k, "MISSING") for k in (
    "W272p", "W272", "W273p", "W271", "W270", "W269", "W268", "W267",
    "613_501", "613_700", "611_501", "613_500", "611_700", "613_300",
    "611_301", "611_500", "613_701", "615_500", "613_900", "615_700",
    "615_701", "615_900",
    "1,018,335", "591,920", "1,020,535", "n1_w271", "n1_w270",
    "w270_", "w271_", "w272_", "_w271bmc_", "_w272bmc_",
    "r1095", "r1096", "r1097", "r1098", "f608ff1cee", "c049a57623",
    "7dd091eef1", "87d2697cdc", "f75b18c862",
    "TWENTY-FIRST", "TWENTIETH", "TWENTY-SECOND", "twentieth", "twenty-first",
    "W273p", "_set_wave(271)", "996,335", "pre-W271-universe",
    "bmc_rows=89", "bmc_rows=90", "NINETIETH owned",
    "W268_W269_W270_bands_respected", "block = 129 rows", "authored 17:5x",
    "bm-c r1099 window", "18:2x", "MSG-20261018-191x-bmc-w272-seat",
    "W272 FREEZE UNBLOCKED", "PRE-W271-splice", "PRE-W272-splice",
    "W271 FREEZE UNBLOCKED", "own W248..W269 legs (22", "W248..W271 legs (23",
    "W211..W269 legs (59", "W211..W270 legs 59", "fifty-ninth",
    "len(owner_rows_live) == 260", "len(owner_rows_live) == 261",
    "range(248, 271)", "range(209, 272)", "if w < 271)", "271 - _lw",
    "arith_a271", "arith_a272", "W272 walk", "W273 walk",
    "W271 materializer face", "W272 materializer face",
    "W270 finalize product", "W271 finalize product",
    "post-W270-REGISTERED", "post-W271-REGISTERED",
    "PERPETUAL_N1_W272_PREREG", "PERPETUAL_N1_W271_PREREG")}, indent=1))
