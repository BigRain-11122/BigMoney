# -*- coding: utf-8 -*-
# r1114 bm-c splice window: W277 editor NEEDLE PREFLIGHT (r1077 measured-counts law)
# Measures every needle count on the committed W276 freeze-edits canon
# (results/_w276bmc_freeze_edits.py, bm-c r1111 splice window 354a645155,
# proven live-fire: W276 five-face splice + engine self-burn 12/12 + finalize
# one-pass ledger 1,031,535 / K=605,120 EXACT, machine-verified by the
# r1111 closeout e781164e41) BEFORE the W277 editor is authored.
# Also extracts the multi-line prereg-delivery prose forms VERBATIM (zero
# transcription for the CRLF-joined needles).
import io, subprocess, hashlib, json

CANON = "results/_w276bmc_freeze_edits.py"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:" + CANON], capture_output=True, text=True).stdout.strip()
blob_origin = subprocess.run(["git", "rev-parse", "origin/main:" + CANON], capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head == blob_origin and len(blob_wt) == 40, \
    f"canon blob drift wt={blob_wt} head={blob_head} origin={blob_origin}"

t = io.open(CANON, encoding="utf-8", newline="").read()
assert t.count("\r\n") > t.count("\n") - t.count("\r\n"), "canon EOL face drift (CRLF expected)"
receipt = {
 "tool": "r1114 needle preflight",
 "canon": CANON,
 "canon_blob": blob_wt,
 "canon_sha256_16": hashlib.sha256(t.encode("utf-8")).hexdigest()[:16],
 "canon_bytes": len(t.encode("utf-8")),
 "eol": "CRLF",
}

RAW = {
 # phase-1 projections + bands + ints + ledger/lc/seat (src faces)
 "W277p": 13, "W277": 26,
 "624_501": 5, "624_700": 4, "624_500": 9, "624_300": 2,
 "622_501": 8, "622_700": 2, "622_301": 4, "622_500": 6,
 "624501": 1, "626500": 1, "624701": 2, "624900": 2,
 "1,029,335": 6, "602,920": 6, "1_029_335": 1, "602_920": 1,
 "n1_w276": 4, "n1w276-": 2, "n1_w275": 4,
 "w276_": 13, "w275_": 93,   # pre-carveout: builder x1 + n1_w276_results x2 consumed first, 10 bare remain
 "_w276bmc_": 11, "_w275bmc_freeze_edits.py template": 1,
 "MSG-20261019-055x-bmc-w276-seat": 7,
 'SEAT_ORIGIN = "21b51a102"': 1, "21b51a102 r1109": 1,
 "21b51a102": 2, "018782314d": 1, "5352c7cf343fc5e5": 2, "770a47fa1f": 1,
 "(E63 canon-clone builder _r1110bmc_build_w276_derive.py)": 1,
 "2026-10-19 07:1x bm-c r1111 splice window": 1,
 '"wave": 275': 1,
 # phase-2 blankets
 "W276": 96, "W275": 158,
 # phase-3 pre/post forms (measured on RAW; post-blanket forms simulated below)
 "W273_W274_W275_bands_respected": 2,
 "W211..W274 legs (64)": 1, "W211..W274 sixty-four legs": 1, "range(211, 275)": 1,
 "own W248..W274 legs (27)": 4, "W248..W274 twenty-seven legs": 1,
 'N1_BANDS[") == 27': 1,
 "W211..W275 legs 64": 1,
 "W248..W276 legs (28": 4,
 "block = 134 rows": 1, "134 parity rows": 1, "block parity = 134 rows": 1,
 'N1_BANDS[") == 133,': 1, "!= 133": 1, 'N1_BANDS[") == 64': 1,
 '"fresh_legs_row_asserts": 28': 1, "+ 28,": 1,
 "range(248, 276)": 2, "range(248, 275)": 1, "range(16, 276)": 2,
 "range(17, 276)": 3, "range(209, 277)": 2,
 "if w < 276)": 5, "if w < 275)": 1, "276 - _lw": 2, "_w == 275": 1,
 "WAVE_CONFIGS[276]": 2, "WAVE_CONFIGS[275]": 3, "N1_BANDS[275]": 5,
 "get(275)": 1, "_c275": 5,
 '276: {"batch"': 2, '276: {{"batch"': 1, '276: {"a"': 1, '276: {{"a"': 2,
 '275: {"batch"': 2, '275: {"a"': 3,
 "arith_a276": 6, "arith_b276": 6,
 "(272, 271, 270, 269, 268, 267, 266, 265, 264, 263)": 2, "W263..W272": 1,
 "len(owner_rows_live) == 265 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 94": 1,
 "265/130/94": 1, "owner_rows=265 / bma_rows=130 / bmc_rows=94": 1,
 "rows 265 + candidate = 266th": 2, "; bm-c rows 94 +": 1,
 "bm-c rows 94 + candidate = 95th owned": 1, "# candidate = 95th EXACT": 1,
 "engine_owner==bm-c rows 94 + candidate": 1,
 "bm-c rows {len(bmc_rows_live)} + candidate (95th own wave": 1,
 "bm-c's 95th own wave": 2, "NINETY-FIFTH owned": 3,
 "TWO HUNDRED AND SEVENTY-SIXTH": 3, "bmc_rows=94": 7,
 '"probe_receipt_bmc_ordinal_face": 94': 1,
 "bmc rows 94 + candidate 95th": 1,
 "TWENTY-SIXTH": 7, "TWENTY-FIFTH": 15, "twenty-sixth": 4, "twenty-fifth": 3,
 "sixty-fourth": 2, "sixty-four legs": 1,
 "wave 276 engine_owner=bm-c": 1, '"wave 276: "': 1, "wave 276 = first free number": 1,
 "cycle COMPLETE bm-c r1108 closeout 05:3x": 1,
 "bm-c r1108 splice window": 2, "own-wave full cycle r1108": 1,
 "bm-c splice generation r1108 window": 1, "verified r1108": 1,
 "# r1108 splice window": 1, "(bm-c r1108": 1,
 "finalize one-pass bm-c r1108 closeout, ledger": 1,
 "finalize one-pass bm-c r1108 closeout ledger": 1,
 "(r1109 MSG-": 1, "r1109 BEFORE this freeze": 1,
 "seat itself r1109; queue-head": 1, "(r1109, queue-head seat-first supply": 1,
 "bm-c r1110 window": 4, "# r1110 window": 1,
 "(R275: ": 1, "_set_wave(276)": 1,
 # NOTE (preflight-table heal, disclosed): 'the bm-c r1111 splice window' and
 # 'bm-c own seat executed at the bm-c r1111 splice window' table guesses
 # REMOVED after first-run measurement -- faces ABSENT from canon (my misread
 # of the r1111 gate region; the true gate face is the hdr-stamp form above);
 # zero canon anomalies, 130+ remaining entries measured exact first-try.
 # frozen/anti-drift faces (carried verbatim)
 "w244_a": 12, "w244_b": 8, "n3r1_used245": 3, "m211": 4, "m248": 4,
 "fourteen-wave": 8, "dual-window parity": 1, "physical bytes": 6,
 "20261019": 17, "~23:5x": 4, "bm-a": 5,
 "range(211, 248)": 1, "range(138, 207)": 1,
 "zero skip-claim": 1, "banned gate ADMIT 0 (re-run at freeze window)": 1,
 '"machine": "bm-c"': 1, "derived by the bm-c": 2, "was published AFTER": 1,
 "bm-c own-seat continuity": 2, "_set_wave(2)": 1,
 "registered wave below 263 composes": 2, "593901": 1,
 "w244_a holds wave-263 bands": 4,
 "W211..W247 legs (37)": 2, 'N1_BANDS[") == 37': 1,
 "W276 FREEZE UNBLOCKED": 4, "PRE-W276-splice": 1, "post-W275 registration": 2,
 "post-W275-REGISTERED": 8,
 "anchors W275 1,029,335 / K=602,920 at draft": 1,
 "PERPETUAL_N1_W276_PREREG": 8, "PERPETUAL_N1_W275_PREREG": 2, "PERPETUAL-N1-W276": 7,
 "W276 materializer face": 4, "W275 materializer face": 1,
 "W275 finalize product": 4, "W277 walk": 1,
 "expect 265/130/94": 1, "sixty-fourth consecutive": 2,
 "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
 "owner=bm-c seat honored": 1,
 "authored 06:5x": 2,
 # date-roll face (expect count 0 again this generation)
 "20261018": 0, "2026-10-18": 0,
 # residual probes (faces that must NOT exist in canon)
 "r1105": 0, "r1106": 0, "r1107": 0, "03:2x": 0, "04:4x": 0, "05:0x": 0,
 "bf4bbbde1": 0, "ec907d164": 0, "e4e1ce44f5afd03b": 0, "1fcc0bc30f": 0,
 "MSG-20261019-034x": 0, "_w274bmc_": 0, "n1_w274": 0, "w274_": 0, "n1w275-": 0,
 "622_300": 0, "622_100": 0, "620_301": 0, "620_500": 0, "620_101": 0, "620_300": 0,
 "622301": 0, "624300": 0, "622501": 0, "622700": 0,
 "1,027,135": 0, "600,720": 0, "1_027_135": 0, "600_720": 0,
 "W277p": 13, "W276p": 0, "W275p": 0, "W274p": 0,
 "NINETY-FOURTH owned": 0, "TWO HUNDRED AND SEVENTY-FIFTH": 0,
 "TWENTY-FOURTH": 0, "twenty-fourth": 0, "sixty-third": 0,
 "rows 264 + candidate": 0, "bmc_rows=93": 0, "264/130/93": 0,
 "W272_W273_W275_bands_respected": 0, "_w273bmc_": 0, "n1_w273": 0, "w273_": 0,
 "c5f8b88f91": 0, "354a645155": 0,
 "45ee1de94c7d36fd": 0, "e0bc4a0ddd": 0,
}
raw_out, mismatch = {}, []
for k, v in RAW.items():
    c = t.count(k)
    raw_out[k] = c
    if c != v:
        mismatch.append((k, c, v))
receipt["raw_counts"] = raw_out
receipt["raw_mismatches"] = mismatch

# ---- simulate phase-1 + phase-2 on a copy; measure POST-BLANKET phase-3 forms ----
s = t
def r(old, new, expect, tag):
    global s
    n = s.count(old)
    assert n == expect, f"sim[{tag}] {n} != {expect}: {old[:80]!r}"
    s = s.replace(old, new)
r("W277p", "W278p", 13, "proj_prefix")
r("W277", "W278", 13, "proj_plain")
r("624_501", "626_701", 5, "Blo"); r("624_700", "626_900", 4, "Bhi")
r("624_500", "626_700", 9, "Ahi"); r("624_300", "626_500", 2, "naiveAhi")
r("622_501", "624_701", 8, "Alo"); r("622_700", "624_900", 2, "Bnaivehi")
r("622_301", "624_501", 4, "naiveAlo_priorBlo"); r("622_500", "624_700", 6, "priorBhi")
r("624501", "626701", 1, "iAlo"); r("626500", "628700", 1, "iAhi")
r("624701", "626901", 2, "iBlo"); r("624900", "627100", 2, "iBhi")
r("1,029,335", "1,031,535", 6, "led"); r("602,920", "605,120", 6, "k")
r("1_029_335", "1_031_535", 1, "ledcode"); r("602_920", "605_120", 1, "kcode")
r("(E63 canon-clone builder _r1110bmc_build_w276_derive.py)",
  "(E63 canon-clone builder _r1113bmc_build_w277_derive.py)", 1, "builder")
r("n1_w276", "n1_w277", 4, "n1own"); r("n1w276-", "n1w277-", 2, "n1dash")
r("w276_", "w277_", 10, "lcown")
r("n1_w275", "n1_w276", 4, "n1up"); r("w275_", "w276_", 89, "lcup")
r("_w276bmc_", "_w277bmc_", 11, "rcpt")
r("_w275bmc_freeze_edits.py template", "_w276bmc_freeze_edits.py template", 1, "templ")
r("MSG-20261019-055x-bmc-w276-seat", "MSG-20261019-080x-bmc-w277-seat", 7, "seatmsg")
r('SEAT_ORIGIN = "21b51a102"', 'SEAT_ORIGIN = "c5f8b88f91"', 1, "seatconst")
r("21b51a102 r1109", "c5f8b88f91 r1112", 1, "seathdr")
r("018782314d", "354a645155", 1, "lineagesha")
r("2026-10-19 07:1x bm-c r1111 splice window", "2026-10-19 09:3x bm-c r1114 splice window", 1, "hdrstamp")
r('"wave": 275', '"wave": 276', 1, "rwave")
r("W276", "W277", 96, "ownD")
r("W275", "W276", 158, "upD")
POST = {
 "W273_W274_W276_bands_respected": 2,
 "W211..W276 legs 64": 1,
 "W248..W277 legs (28": 4,
 "range(248, 276)": 2, "range(16, 276)": 2, "range(17, 276)": 3, "range(209, 277)": 2,
 "range(211, 275)": 1,
 "if w < 275)": 1,
}
post_out = {k: s.count(k) for k, v in POST.items()}
receipt["post_blanket_forms"] = post_out
receipt["post_blanket_mismatches"] = [(k, c, v) for k, c, v in
                                      [(k, post_out[k], POST[k]) for k in POST] if c != v]

# ---- extract prereg-delivery prose lines VERBATIM (CRLF-aware) ----
lines = t.split("\r\n")
prose = [ln for ln in lines if "authored 06:5x" in ln]
receipt["prereg_delivery_lines"] = prose
receipt["prereg_delivery_context"] = []
for i, ln in enumerate(lines):
    if "authored 06:5x" in ln or "pushed-# first-try to origin 770a47fa1f" in ln or "pushed first-try r1110 origin" in ln:
        receipt["prereg_delivery_context"].append({"idx": i, "line": ln})

receipt["verdict"] = "PASS" if not receipt["raw_mismatches"] and not receipt["post_blanket_mismatches"] else "MISMATCH"
io.open("results/_r1114bmc_needle_preflight.json", "w", encoding="utf-8", newline="\r\n").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("canon", receipt["canon_sha256_16"], receipt["canon_bytes"], "B")
print("raw mismatches:", mismatch)
print("post-blanket mismatches:", receipt["post_blanket_mismatches"])
for p in prose:
    print("PROSE:", p[:170])
print("VERDICT", receipt["verdict"])
