# -*- coding: utf-8 -*-
# r1111 bm-c splice window: W276 editor NEEDLE PREFLIGHT (r1077 measured-counts law)
# Measures every needle count on the committed W275 freeze-edits canon
# (results/_w275bmc_freeze_edits.py, bm-c r1108 splice window 018782314d,
# proven live-fire: W275 five-face splice + engine self-burn 12/12 + finalize
# one-pass 0bcd555b79 ledger 1,029,335 / K=602,920 EXACT, machine-verified by
# the r1108 closeout c77ee358f5) BEFORE the W276 editor is authored.
# Also extracts the multi-line prereg-delivery prose forms VERBATIM (zero
# transcription for the CRLF-joined needles).
import io, subprocess, hashlib, json

CANON = "results/_w275bmc_freeze_edits.py"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:" + CANON], capture_output=True, text=True).stdout.strip()
blob_origin = subprocess.run(["git", "rev-parse", "origin/main:" + CANON], capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head == blob_origin and len(blob_wt) == 40, \
    f"canon blob drift wt={blob_wt} head={blob_head} origin={blob_origin}"

t = io.open(CANON, encoding="utf-8", newline="").read()
assert t.count("\r\n") > t.count("\n") - t.count("\r\n"), "canon EOL face drift (CRLF expected)"
receipt = {
 "tool": "r1111 needle preflight",
 "canon": CANON,
 "canon_blob": blob_wt,
 "canon_sha256_16": hashlib.sha256(t.encode("utf-8")).hexdigest()[:16],
 "canon_bytes": len(t.encode("utf-8")),
 "eol": "CRLF",
}

RAW = {
 # phase-1 projections + bands + ints + ledger/lc/seat (src faces)
 "W276p": 13, "W276": 26,   # 26 = 13 plain + 13 inside W276p (substring face)
 "622_301": 5, "622_500": 4, "622_300": 9, "622_100": 2,
 "620_301": 8, "620_500": 2, "620_101": 4, "620_300": 6,
 "622301": 1, "624300": 1, "622501": 2, "622700": 2,
 "1,027,135": 6, "600,720": 6, "1_027_135": 1, "600_720": 1,
 "n1_w275": 4, "n1w275-": 2, "n1_w274": 4,
 "w275_": 13, "w274_": 93,   # pre-carveout: builder x1 + n1_w275_results x2 consumed first, 10 bare remain
 "_w275bmc_": 11, "_w274bmc_freeze_edits.py template": 1,
 "MSG-20261019-034x-bmc-w275-seat": 7,
 'SEAT_ORIGIN = "bf4bbbde1"': 1, "bf4bbbde1 r1106": 1,
 "bf4bbbde1": 2, "ec907d164": 1, "e4e1ce44f5afd03b": 2, "1fcc0bc30f": 1,
 "(E63 canon-clone builder _r1107bmc_build_w275_derive.py)": 1,
 "2026-10-19 05:0x bm-c r1108 splice window": 1,
 '"wave": 274': 1,
 # phase-2 blankets
 "W275": 96, "W274": 158,
 # phase-3 pre/post forms (measured on RAW; post-blanket forms simulated below)
 "W272_W273_W274_bands_respected": 2,
 "W211..W273 legs (63)": 1, "W211..W273 sixty-three legs": 1, "range(211, 274)": 1,
 "own W248..W273 legs (26)": 4, "W248..W273 twenty-six legs": 1,
 'N1_BANDS[") == 26': 1,
 "W211..W274 legs 63": 1,
 "W248..W275 legs (27": 4,
 "block = 133 rows": 1, "133 parity rows": 1, "block parity = 133 rows": 1,
 'N1_BANDS[") == 132,': 1, "!= 132": 1, 'N1_BANDS[") == 63': 1,
 '"fresh_legs_row_asserts": 27': 1, "+ 27,": 1,
 "range(248, 275)": 2, "range(248, 274)": 1, "range(16, 275)": 2,
 "range(17, 275)": 3, "range(209, 276)": 2,
 "if w < 275)": 5, "if w < 274)": 1, "275 - _lw": 2, "_w == 274": 1,
 "WAVE_CONFIGS[275]": 2, "WAVE_CONFIGS[274]": 3, "N1_BANDS[274]": 5,
 "get(274)": 1, "_c274": 5,
 '275: {"batch"': 2, '275: {{"batch"': 1, '275: {"a"': 1, '275: {{"a"': 2,
 '274: {"batch"': 2, '274: {"a"': 3,
 "arith_a275": 6, "arith_b275": 6,
 "(271, 270, 269, 268, 267, 266, 265, 264, 263, 262)": 2, "W262..W271": 1,
 "len(owner_rows_live) == 264 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 93": 1,
 "264/130/93": 1, "owner_rows=264 / bma_rows=130 / bmc_rows=93": 1,
 "rows 264 + candidate = 265th": 2, "; bm-c rows 93 +": 1,
 "bm-c rows 93 + candidate = 94th owned": 1, "# candidate = 94th EXACT": 1,
 "engine_owner==bm-c rows 93 + candidate": 1,
 "bm-c rows {len(bmc_rows_live)} + candidate (94th own wave": 1,
 "bm-c's 94th own wave": 2, "NINETY-FOURTH owned": 3,
 "TWO HUNDRED AND SEVENTY-FIFTH": 3, "bmc_rows=93": 7,
 '"probe_receipt_bmc_ordinal_face": 93': 1,
 "bmc rows 93 + candidate 94th": 1,
 "TWENTY-FIFTH": 7, "TWENTY-FOURTH": 15, "twenty-fifth": 4, "twenty-fourth": 3,
 "sixty-third": 2, "sixty-three legs": 1,
 "wave 275 engine_owner=bm-c": 1, '"wave 275: "': 1, "wave 275 = first free number": 1,
 "cycle COMPLETE bm-c r1105 closeout 03:2x": 1,
 "bm-c r1105 splice window": 2, "own-wave full cycle r1105": 1,
 "bm-c splice generation r1105 window": 1, "verified r1105": 1,
 "# r1105 splice window": 1, "(bm-c r1105": 1,
 "finalize one-pass bm-c r1105 closeout, ledger": 1,
 "finalize one-pass bm-c r1105 closeout ledger": 1,
 "(r1106 MSG-": 1, "r1106 BEFORE this freeze": 1,
 "seat itself r1106; queue-head": 1, "(r1106, queue-head seat-first supply": 1,
 "bm-c r1107 window": 4, "# r1107 window": 1,
 "(R274: ": 1, "_set_wave(275)": 1,
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
 "W275 FREEZE UNBLOCKED": 4, "PRE-W275-splice": 1, "post-W274 registration": 2,
 "post-W274-REGISTERED": 8,
 "anchors W274 1,027,135 / K=600,720 at draft": 1,
 "PERPETUAL_N1_W275_PREREG": 8, "PERPETUAL_N1_W274_PREREG": 2, "PERPETUAL-N1-W275": 7,
 "W275 materializer face": 4, "W274 materializer face": 1,
 "W274 finalize product": 4, "W276 walk": 1,
 "expect 264/130/93": 1, "sixty-third consecutive": 2,
 "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
 "owner=bm-c seat honored": 1,
 "authored 04:4x": 2,
 # date-roll face (expect count 0 again this generation)
 "20261018": 0, "2026-10-18": 0,
 # residual probes (faces that must NOT exist in canon)
 "r1102": 0, "r1104": 0, "01:0x": 0, "02:2x": 0, "03:2x": 1, "04:4x": 2,
 "620_100": 0, "619_900": 0, "618_101": 0, "618_300": 0, "617_901": 0, "618_100": 0,
 "1,024,935": 0, "598,520": 0, "1_024_935": 0, "598_520": 0,
 "W275p": 0, "W274p": 0, "W273p": 0,
 "NINETY-THIRD owned": 0, "TWO HUNDRED AND SEVENTY-FOURTH": 0,
 "TWENTY-THIRD": 0, "twenty-third": 0, "sixty-second": 0,
 "rows 263 + candidate": 0, "bmc_rows=92": 0, "263/130/92": 0,
 "W271_W272_W274_bands_respected": 0, "_w273bmc_": 0, "n1_w273": 0, "w273_": 0,
 "21b51a102": 0, "018782314d": 0,
 "5352c7cf343fc5e5": 0, "770a47fa1f": 0,
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
r("W276p", "W277p", 13, "proj_prefix")
r("W276", "W277", 13, "proj_plain")
r("622_301", "624_501", 5, "Blo"); r("622_500", "624_700", 4, "Bhi")
r("622_300", "624_500", 9, "Ahi"); r("622_100", "624_300", 2, "naiveAhi")
r("620_301", "622_501", 8, "Alo"); r("620_500", "622_700", 2, "Bnaivehi")
r("620_101", "622_301", 4, "naiveAlo_priorBlo"); r("620_300", "622_500", 6, "priorBhi")
r("622301", "624501", 1, "iAlo"); r("624300", "626500", 1, "iAhi")
r("622501", "624701", 2, "iBlo"); r("622700", "624900", 2, "iBhi")
r("1,027,135", "1,029,335", 6, "led"); r("600,720", "602,920", 6, "k")
r("1_027_135", "1_029_335", 1, "ledcode"); r("600_720", "602_920", 1, "kcode")
r("(E63 canon-clone builder _r1107bmc_build_w275_derive.py)",
  "(E63 canon-clone builder _r1110bmc_build_w276_derive.py)", 1, "builder")
r("n1_w275", "n1_w276", 4, "n1own"); r("n1w275-", "n1w276-", 2, "n1dash")
r("w275_", "w276_", 10, "lcown")
r("n1_w274", "n1_w275", 4, "n1up"); r("w274_", "w275_", 89, "lcup")
r("_w275bmc_", "_w276bmc_", 11, "rcpt")
r("_w274bmc_freeze_edits.py template", "_w275bmc_freeze_edits.py template", 1, "templ")
r("MSG-20261019-034x-bmc-w275-seat", "MSG-20261019-055x-bmc-w276-seat", 7, "seatmsg")
r('SEAT_ORIGIN = "bf4bbbde1"', 'SEAT_ORIGIN = "21b51a102"', 1, "seatconst")
r("bf4bbbde1 r1106", "21b51a102 r1109", 1, "seathdr")
r("ec907d164", "018782314d", 1, "lineagesha")
r("2026-10-19 05:0x bm-c r1108 splice window", "2026-10-19 07:1x bm-c r1111 splice window", 1, "hdrstamp")
r('"wave": 274', '"wave": 275', 1, "rwave")
r("W275", "W276", 96, "ownD")
r("W274", "W275", 158, "upD")
POST = {
 "W272_W273_W275_bands_respected": 2,
 "W211..W275 legs 63": 1,
 "W248..W276 legs (27": 4,
 "range(248, 275)": 2, "range(16, 275)": 2, "range(17, 275)": 3, "range(209, 276)": 2,
 "range(211, 274)": 1,
 "if w < 274)": 1,
}
post_out = {k: s.count(k) for k, v in POST.items()}
receipt["post_blanket_forms"] = post_out
receipt["post_blanket_mismatches"] = [(k, c, v) for k, c, v in
                                      [(k, post_out[k], POST[k]) for k in POST] if c != v]

# ---- extract prereg-delivery prose lines VERBATIM (CRLF-aware) ----
lines = t.split("\r\n")
prose = [ln for ln in lines if "authored 04:4x" in ln]
receipt["prereg_delivery_lines"] = prose
receipt["prereg_delivery_context"] = []
for i, ln in enumerate(lines):
    if "authored 04:4x" in ln or "pushed-first-try to origin 1fcc0bc30f" in ln or "pushed first-try r1107 origin" in ln:
        receipt["prereg_delivery_context"].append({"idx": i, "line": ln})

receipt["verdict"] = "PASS" if not receipt["raw_mismatches"] and not receipt["post_blanket_mismatches"] else "MISMATCH"
io.open("results/_r1111bmc_needle_preflight.json", "w", encoding="utf-8", newline="\r\n").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("canon", receipt["canon_sha256_16"], receipt["canon_bytes"], "B")
print("raw mismatches:", mismatch)
print("post-blanket mismatches:", receipt["post_blanket_mismatches"])
for p in prose:
    print("PROSE:", p[:170])
print("VERDICT", receipt["verdict"])
