# -*- coding: utf-8 -*-
# r1102 bm-c splice window: W273 needle preflight (r1077 measured-counts law)
# Measures EVERY needle count on the canon (results/_w272bmc_freeze_edits.py,
# proven live-fire W272 splice editor, committed c99ee20a4) that the W273
# derive editor (_w273bmc_derive_editor.py) will consume, BEFORE the transform
# asserts those counts. Receipt: results/_r1102bmc_needle_preflight.json
# Canon face: 62,222B sha256_16 3deda21aa3e96ed9 wt==HEAD==origin (triple).
# Payload faces: PERPETUAL_N1_W273_PREREG.md 23,449B sha256_16 2f289446a93fa102
# (frozen b6bbb69e92 -> surgery-delivered origin 839441a547 + receipts
# eeb3bf07ad, r1102 window); probe receipt 5,254B sha256_16 283807958c1bf019
# (committed with the seat @ 39e1bb32f1 r1101).
# EOL face (r1093): canon read raw with newline=''; counts are on the raw
# bytes (CRLF-smudged disk form, norm-eq to the LF origin blob).
import hashlib, io, json, subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = "results/_w272bmc_freeze_edits.py"
OUT = "results/_r1102bmc_needle_preflight.json"

def gh(*a):
    r = subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True)
    return r.stdout.strip()

blob_wt = gh("hash-object", CANON)
blob_head = gh("rev-parse", "HEAD:" + CANON)
blob_origin = gh("rev-parse", "origin/main:" + CANON)
assert blob_wt == blob_head == blob_origin and len(blob_wt) == 40, \
    f"canon blob drift wt={blob_wt} head={blob_head} origin={blob_origin}"
payload_faces = {}
for p in ("research/PERPETUAL_N1_W273_PREREG.md",
          "results/_w273bmc_20261018_probe_receipt.json"):
    bw = gh("hash-object", p); bh = gh("rev-parse", "HEAD:" + p); bo = gh("rev-parse", "origin/main:" + p)
    bb = open(REPO + "\\" + p.replace("/", "\\"), "rb").read()
    assert bw == bh == bo and len(bw) == 40, f"payload triple fail {p}"
    payload_faces[p] = {"bytes": len(bb), "sha256_16": hashlib.sha256(bb).hexdigest()[:16]}

t = io.open(REPO + "\\" + CANON.replace("/", "\\"), encoding="utf-8", newline="").read()
NEEDLES = [
    # --- projections (phase 1) ---
    "W273p", "W273", "W274p", "W274",
    # --- band tokens (phase 1) ---
    "613_501", "613_700", "613_701", "613_900",
    "615_500", "615_700", "615_701", "615_900",
    "615_901", "616_100", "617_700", "617_900", "617_901", "618_100",
    # --- ledger/K anchors ---
    "1,020,535", "594,120", "1_020_535", "594_120",
    "1,022,735", "596,320", "1_022_735", "596_320",
    # --- lowercase machine-file tokens ---
    "n1_w272", "n1_w271", "n1w272-", "n1w271-",
    "w272_", "w271_", "n1_w273", "w273_",
    # --- receipt / lineage / seat ---
    "_w272bmc_", "_w271bmc_", "_w273bmc_",
    "MSG-20261018-191x-bmc-w272-seat", "MSG-20261018-211x-bmc-w273-seat",
    "f608ff1cee", 'SEAT_ORIGIN = "f608ff1cee"', "39e1bb32f1",
    "7dd091eef1", "c99ee20a4", "c049a57623",
    "b6bbb69e92", "839441a547", "eeb3bf07ad",
    # --- window stamps ---
    "2026-10-18 20:2x bm-c r1100 freeze window",
    "r1097", "r1098", "r1099", "r1100", "r1101", "r1102",
    "bm-c r1097 splice window", "cycle COMPLETE bm-c r1097 closeout 18:4x",
    "own-wave full cycle r1097", "bm-c splice generation r1097 window",
    "verified r1097", "# r1097 splice window", "(bm-c r1097",
    "finalize one-pass bm-c r1097 closeout, ledger",
    "finalize one-pass bm-c r1097 closeout ledger",
    "(r1098 MSG-", "r1098 BEFORE this freeze", "seat itself r1098; queue-head",
    "(r1098, queue-head seat-first supply",
    "bm-c r1099 window", "# r1099 window", "r1099 commit",
    "authored 19:2x", "committed+pushed same window c049a57623",
    "18:4x", "20:2x", "20:4x", "17:3x", "19:2x",
    # --- receipt wave field ---
    '"wave": 271', '"wave": 272',
    # --- relkeys ---
    "W269_W270_W271_bands_respected", "W270_W271_W272_bands_respected",
    # --- legs / dropped / fresh / block counts ---
    "W211..W270 legs (60)", "W211..W270 sixty legs", "range(211, 271)",
    "own W248..W270 legs (23)", "own W248..W270", "W248..W270 twenty-three legs",
    'N1_BANDS[") == 23', "W211..W271 legs 60", "W248..W272 legs (24",
    "block = 130 rows", "130 parity rows", "block parity = 130 rows",
    'N1_BANDS[") == 129,', '!= 129', 'N1_BANDS[") == 60',
    '"fresh_legs_row_asserts": 24', '+ 24,',
    "W211..W271 legs (61)", "W211..W271 sixty-one legs", "own W248..W271 legs (24)",
    "W211..W272 legs 61", "W248..W273 legs (25", "block = 131 rows", "131 parity rows",
    # --- ranges ---
    "range(248, 272)", "range(248, 271)", "range(16, 272)", "range(17, 272)",
    "range(209, 273)", "range(248, 273)", "range(16, 273)", "range(17, 273)",
    "range(209, 274)",
    # --- wave-number gates ---
    "if w < 272)", "if w < 271)", "272 - _lw", "_w == 271",
    "if w < 273)", "273 - _lw", "_w == 272",
    # --- cfg/row faces ---
    "WAVE_CONFIGS[272]", "WAVE_CONFIGS[271]", "N1_BANDS[271]", "get(271)",
    "_c271", '272: {"batch"', '272: {{"batch"', '272: {"a"', '272: {{"a"',
    '271: {"batch"', '271: {"a"', '273: {"batch"', '273: {"a"',
    "arith_a272", "arith_b272", "arith_a271", "arith_b271",
    "arith_a273", "arith_b273",
    "(268, 267, 266, 265, 264, 263, 262, 261, 260, 259)",
    "(269, 268, 267, 266, 265, 264, 263, 262, 261, 260)",
    "W259..W268", "W260..W269",
    # --- ordinal faces ---
    "len(owner_rows_live) == 261 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 90",
    "len(owner_rows_live) == 262 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 91",
    "261/130/90", "262/130/91",
    "owner_rows=261 / bma_rows=130 / bmc_rows=90",
    "owner_rows=262 / bma_rows=130 / bmc_rows=91",
    "rows 261 + candidate = 262nd", "rows 262 + candidate = 263rd",
    "; bm-c rows 90 +", "; bm-c rows 91 +",
    "bm-c rows 90 + candidate = 91st owned", "bm-c rows 91 + candidate = 92nd owned",
    "# candidate = 91st EXACT", "# candidate = 92nd EXACT",
    "engine_owner==bm-c rows 90 + candidate", "engine_owner==bm-c rows 91 + candidate",
    "bm-c rows {len(bmc_rows_live)} + candidate (91st own wave",
    "bm-c rows {len(bmc_rows_live)} + candidate (92nd own wave",
    "bm-c's 91st own wave", "bm-c's 92nd own wave",
    "NINETY-FIRST owned", "NINETY-SECOND owned",
    "TWO HUNDRED AND SEVENTY-SECOND", "TWO HUNDRED AND SEVENTY-THIRD",
    "bmc_rows=90", "bmc_rows=91",
    '"probe_receipt_bmc_ordinal_face": 90', '"probe_receipt_bmc_ordinal_face": 91',
    "TWENTY-SECOND", "TWENTY-FIRST", "twenty-second", "twenty-first",
    "TWENTY-THIRD", "twenty-third",
    "sixtieth", "sixty legs", "sixty-first", "sixty-one legs",
    "sixtieth consecutive",
    # --- wave-number narrative ---
    "wave 272 engine_owner=bm-c", "wave 273 engine_owner=bm-c",
    '"wave 272: "', '"wave 273: "',
    "wave 272 = first free number", "wave 273 = first free number",
    # --- stale bm-a authoring faces (heal candidates) ---
    "engine_owner=bm-a (bm-c OWN-SEAT face",
    "bm-a's NINETY-FIRST owned claim",
    "engine_owner=bm-c (bm-c OWN-SEAT face",
    "bm-c's NINETY-SECOND owned claim",
    # --- frozen / carried faces (phase 4 anti-drift) ---
    "w244_a", "w244_b", "n3r1_used245",
    "w244_a holds wave-263 bands", "m211", "593901",
    "bma rows 129 + candidate 130th",
    "registered wave below 263 composes", "registered wave below 264 composes",
    "bm-c own-seat continuity",
    "W211..W247 legs (37)", "W211..W247 verbatim (37 legs)",
    "W211..W247 thirty-seven legs", 'N1_BANDS[") == 37',
    "range(211, 248)", "range(138, 207)",
    "fourteen-wave", "dual-window parity", '"machine": "bm-c"',
    "derived by the bm-c", "was published AFTER", "physical bytes",
    "m248", "W272 FREEZE UNBLOCKED", "PRE-W272-splice", "post-W271 registration",
    "expect 261/130/90",
    "anchors W271 1,020,535 / K=594,120 at draft",
    "_set_wave(272)", "_set_wave(271)", "_set_wave(2)",
    "N1_BANDS[248] ==", "N1_BANDS\\[248\\]",
    "post-W271-REGISTERED",
    # --- W273-free canon check (new wave must be absent pre-transform) ---
    "PERPETUAL-N1-W273", "PERPETUAL_N1_W273",
    "W274p",
]
counts = {}
for n in NEEDLES:
    counts[n] = t.count(n)
receipt = {
  "tool": "w273 needle preflight (r1077 measured-counts law, r1102 splice window)",
  "canon": {"path": CANON, "blob": blob_wt, "bytes": len(t.encode("utf-8")),
             "sha256_16": hashlib.sha256(t.encode("utf-8")).hexdigest()[:16],
             "triple": "wt==HEAD==origin verified"},
  "payloads": payload_faces,
  "counts": counts,
}
with open(REPO + "\\" + OUT.replace("/", "\\"), "w", encoding="utf-8", newline="") as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)
print(json.dumps(receipt["canon"], indent=1))
print(json.dumps(payload_faces, indent=1))
for k, v in counts.items():
    print("%5d  %r" % (v, k))
print("PREFLIGHT-OK ->", OUT)
