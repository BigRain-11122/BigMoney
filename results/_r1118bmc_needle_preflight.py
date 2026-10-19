# -*- coding: utf-8 -*-
# r1118 bm-c splice window: W278 editor NEEDLE PREFLIGHT (r1077 measured-counts law)
# Measures every needle count on the committed W277 freeze-edits canon
# (results/_w277bmc_freeze_edits.py, bm-c r1114 splice window 9e53371814,
# proven live-fire: W277 five-face splice + engine self-burn 12/12 + finalize
# one-pass ledger 1,033,735 / K=607,320 EXACT, machine-verified by the
# r1114-continuation closeout efc4a1c1bb) BEFORE the W278 editor is authored.
# Also extracts the multi-line prereg-delivery prose forms VERBATIM (zero
# transcription for the CRLF-joined needles).
# Table = the r1114 preflight table rolled ONE generation (W277 canon faces);
# any first-run mismatch = preflight-table heal (measured governs, disclosed).
import io, subprocess, hashlib, json

CANON = "results/_w277bmc_freeze_edits.py"
CRLF = "\r\n"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:" + CANON], capture_output=True, text=True).stdout.strip()
blob_origin = subprocess.run(["git", "rev-parse", "origin/main:" + CANON], capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head == blob_origin and len(blob_wt) == 40, \
    f"canon blob drift wt={blob_wt} head={blob_head} origin={blob_origin}"

t = io.open(CANON, encoding="utf-8", newline="").read()
assert t.count(CRLF) > t.count("\n") - t.count(CRLF), "canon EOL face drift (CRLF expected)"
receipt = {
 "tool": "r1118 needle preflight",
 "canon": CANON,
 "canon_blob": blob_wt,
 "canon_sha256_16": hashlib.sha256(t.encode("utf-8")).hexdigest()[:16],
 "canon_bytes": len(t.encode("utf-8")),
 "eol": "CRLF",
}

RAW = {
 # phase-1 projections + bands + ints + ledger/lc/seat (src faces, rolled one gen)
 "W278p": 13, "W278": 26,
 "626_701": 5, "626_900": 4, "626_700": 9, "626_500": 2,
 "624_701": 8, "624_900": 2, "624_501": 4, "624_700": 6,
 "626701": 1, "628700": 1, "626901": 2, "627100": 2,
 "1,031,535": 6, "605,120": 6, "1_031_535": 1, "605_120": 1,
 "n1_w277": 4, "n1w277-": 2, "w277_": 13, "n1_w276": 4, "w276_": 93,
 "_w277bmc_": 11, "_w276bmc_freeze_edits.py template": 1,
 "MSG-20261019-080x-bmc-w277-seat": 7,
 'SEAT_ORIGIN = "c5f8b88f91"': 1, "c5f8b88f91 r1112": 1,
 "c5f8b88f91": 2, "354a645155": 1, "45ee1de94c7d36fd": 2, "e0bc4a0ddd": 1,
 "(E63 canon-clone builder _r1113bmc_build_w277_derive.py)": 1,
 "2026-10-19 09:3x bm-c r1114 splice window": 1,
 '"wave": 276': 1,
 "frozen sha16 45ee1de94c7d36fd": 1, "frozen 45ee1de94c7d36fd": 1,
 "CAS-surgical": 1, "authored 09:0x": 2,
 # phase-2 blankets
 "W277": 96, "W276": 158,
 # phase-3 pre/post forms (measured on RAW; post-blanket forms simulated below)
 "W274_W275_W276_bands_respected": 2,
 "W211..W275 legs (65)": 1, "W211..W275 sixty-five legs": 1, "range(211, 276)": 1,
 "own W248..W275 legs (28)": 4,
 "W248..W275 twenty-eight legs": 1,
 'N1_BANDS[") == 28': 1,
 "W211..W276 legs 65": 1,
 "W248..W277 legs (29": 4,
 "block = 135 rows": 1, "135 parity rows": 1, "block parity = 135 rows": 1,
 'N1_BANDS[") == 134,': 1, "!= 134": 1, 'N1_BANDS[") == 65': 1,
 '"fresh_legs_row_asserts": 29': 1, "+ 29,": 1,
 "range(248, 277)": 2, "range(248, 276)": 1, "range(16, 277)": 2,
 "range(17, 277)": 3, "range(209, 278)": 2,
 "if w < 277)": 5, "if w < 276)": 1, "277 - _lw": 2, "_w == 276": 1,
 "WAVE_CONFIGS[277]": 2, "WAVE_CONFIGS[276]": 3, "N1_BANDS[276]": 5,
 "get(276)": 1, "_c276": 5,
 '277: {"batch"': 2, '277: {{"batch"': 1, '277: {"a"': 1, '277: {{"a"': 2,
 '276: {"batch"': 2, '276: {"a"': 3,
 "arith_a277": 6, "arith_b277": 6,
 "(273, 272, 271, 270, 269, 268, 267, 266, 265, 264)": 2, "W264..W273": 1,
 "len(owner_rows_live) == 266 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 95": 1,
 "266/130/95": 1, "owner_rows=266 / bma_rows=130 / bmc_rows=95": 1,
 "rows 266 + candidate = 267th": 2, "; bm-c rows 95 +": 1,
 "bm-c rows 95 + candidate = 96th owned": 1, "# candidate = 96th EXACT": 1,
 "engine_owner==bm-c rows 95 + candidate": 1,
 "bm-c rows {len(bmc_rows_live)} + candidate (96th own wave": 1,
 "bm-c's 96th own wave": 2, "NINETY-SIXTH owned": 3,
 "TWO HUNDRED AND SEVENTY-SEVENTH": 3, "bmc_rows=95": 7,
 '"probe_receipt_bmc_ordinal_face": 95': 1,
 "bmc rows 95 + candidate 96th": 1,
 "TWENTY-SEVENTH": 7, "TWENTY-SIXTH": 15, "twenty-seventh": 4, "twenty-sixth": 3,
 "sixty-fifth": 2, "sixty-five legs": 1,
 "wave 277 engine_owner=bm-c": 1, '"wave 277: "': 1, "wave 277 = first free number": 1,
 "cycle COMPLETE bm-c r1113 closeout 09:1x": 1,
 "bm-c r1111 splice window": 2, "own-wave full cycle r1111": 1,
 "bm-c splice generation r1111 window": 1, "verified r1111": 1,
 "# r1111 splice window": 1, "(bm-c r1111": 1,
 "finalize one-pass bm-c r1111 closeout, ledger": 1,
 "finalize one-pass bm-c r1111 closeout ledger": 1,
 "(r1112 MSG-": 1, "r1112 BEFORE this freeze": 1,
 "seat itself r1112; queue-head": 1, "(r1112, queue-head seat-first supply": 1,
 "bm-c r1113 window": 4, "# r1113 window": 1,
 "(R276: ": 1, "_set_wave(277)": 1,
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
 "W277 FREEZE UNBLOCKED": 4, "PRE-W277-splice": 1, "post-W276 registration": 2,
 "post-W276-REGISTERED": 8,
 "anchors W276 1,031,535 / K=605,120 at draft": 1,
 "PERPETUAL_N1_W277_PREREG": 8, "PERPETUAL_N1_W276_PREREG": 2, "PERPETUAL-N1-W277": 7,
 "W277 materializer face": 4, "W276 materializer face": 1,
 "W276 finalize product": 4, "W278 walk": 1,
 "expect 266/130/95": 1, "sixty-fifth consecutive": 2,
 "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
 "owner=bm-c seat honored": 1,
 "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
 # date-roll face (expect count 0 again this generation)
 "20261018": 0, "2026-10-18": 0,
 # residual probes (faces that must NOT exist in canon)
 "r1108": 0, "r1109": 0, "r1110": 0, "05:3x": 0, "06:5x": 0, "07:1x": 0,
 "bf4bbbde1": 0, "ec907d164": 0, "e4e1ce44f5afd03b": 0, "1fcc0bc30f": 0,
 "MSG-20261019-055x": 0, "MSG-20261019-034x": 0, "_w275bmc_": 0, "n1_w275": 0, "w275_": 0, "n1w276-": 0,
 "622_300": 0, "622_100": 0, "620_301": 0, "620_500": 0, "620_101": 0, "620_300": 0,
 "622301": 0, "624300": 0, "622501": 0, "622700": 0, "624501": 0, "626500": 0, "624701": 0, "624900": 0,
 "1,029,335": 0, "602,920": 0, "1_029_335": 0, "602_920": 0,
 "1,027,135": 0, "600,720": 0, "1_027_135": 0, "600_720": 0,
 "W279p": 0, "W277p": 0, "W276p": 0, "W275p": 0, "W274p": 0, "W273p": 0,
 "NINETY-FIFTH owned": 0, "TWO HUNDRED AND SEVENTY-SIXTH": 0,
 "TWENTY-FIFTH": 0, "twenty-fifth": 0, "sixty-fourth": 0, "sixty-four legs": 0,
 "rows 265 + candidate": 0, "bmc_rows=94": 0, "265/130/94": 0,
 "W273_W274_W276_bands_respected": 0,
 "_w274bmc_": 0, "n1_w274": 0, "w274_": 0, "n1_w273": 0, "w273_": 0,
 "21b51a102": 0, "018782314d": 0, "5352c7cf343fc5e5": 0, "770a47fa1f": 0,
 "arith_a276": 0, "arith_b276": 0,
 "PERPETUAL-N1-W276": 0,
 "range(16, 276)": 0, "range(17, 276)": 0, "range(209, 277)": 0,
 "range(248, 275)": 0, "range(211, 275)": 0, "if w < 275)": 0,
 "276 - _lw": 0, "_w == 275": 0, '"wave": 275': 0,
 "0df07c846b": 0, "644b4f8459": 0, "d7b732c9e8": 0, "efc4a1c1bb": 0, "b187aa6214": 0,
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
    receipt.setdefault("sim_counts", {})[tag] = n
    if n != expect:
        mismatch.append((f"sim[{tag}]", n, expect))
    s = s.replace(old, new)
r("W278p", "W279p", 13, "proj_prefix")
r("W278", "W279", 13, "proj_plain")
r("626_701", "628_901", 5, "Blo"); r("626_900", "629_100", 4, "Bhi")
r("626_700", "628_900", 9, "Ahi"); r("626_500", "628_700", 2, "naiveAhi")
r("624_701", "626_901", 8, "Alo"); r("624_900", "627_100", 2, "Bnaivehi")
r("624_501", "626_701", 4, "naiveAlo_priorBlo"); r("624_700", "626_900", 6, "priorBhi")
r("626701", "628901", 1, "iAlo"); r("628700", "630900", 1, "iAhi")
r("626901", "629101", 2, "iBlo"); r("627100", "629300", 2, "iBhi")
r("1,031,535", "1,033,735", 6, "led"); r("605,120", "607,320", 6, "k")
r("1_031_535", "1_033_735", 1, "ledcode"); r("605_120", "607_320", 1, "kcode")
r("(E63 canon-clone builder _r1113bmc_build_w277_derive.py)",
  "(E63 canon-clone builder _r1116bmc_build_w278_derive.py)", 1, "builder")
r("n1_w277", "n1_w278", 4, "n1own"); r("n1w277-", "n1w278-", 2, "n1dash")
r("w277_", "w278_", 10, "lcown")
r("n1_w276", "n1_w277", 4, "n1up"); r("w276_", "w277_", 89, "lcup")
r("_w277bmc_", "_w278bmc_", 11, "rcpt")
r("_w276bmc_freeze_edits.py template", "_w277bmc_freeze_edits.py template", 1, "templ")
r("MSG-20261019-080x-bmc-w277-seat", "MSG-20261019-102x-bmc-w278-seat", 7, "seatmsg")
r('SEAT_ORIGIN = "c5f8b88f91"', 'SEAT_ORIGIN = "b187aa6214"', 1, "seatconst")
r("c5f8b88f91 r1112", "b187aa6214 r1114-continuation", 1, "seathdr")
r("354a645155", "9e53371814", 1, "lineagesha")
r("(authored 09:0x, banned_direction_gate ADMIT rc0, frozen sha16 45ee1de94c7d36fd + CAS-" + CRLF +
    "# surgical-pushed to origin e0bc4a0ddd, r1113 window).",
  "(authored 12:2x, banned_direction_gate ADMIT rc0, frozen sha16 99001d3d3f337942 + push-race-" + CRLF +
    "# healed landed to origin df1aaba72a, r1116 window).",
  1, "prereg_delivery_hdr")
r("(authored 09:0x, banned gate ADMIT rc0, frozen 45ee1de94c7d36fd -> CAS-surgical r1113 origin ",
  "(authored 12:2x, banned gate ADMIT rc0, frozen 99001d3d3f337942 -> push-race-healed r1116 origin ",
  1, "prereg_delivery_note")
r("2026-10-19 09:3x bm-c r1114 splice window", "2026-10-19 13:3x bm-c r1118 splice window", 1, "hdrstamp")
r('"wave": 276', '"wave": 277', 1, "rwave")
r("W277", "W278", 96, "ownD")
r("W276", "W277", 158, "upD")
POST = {
 "W274_W275_W277_bands_respected": 2,
 "W211..W277 legs 65": 1,
 "W248..W278 legs (29": 4,
 "range(248, 277)": 2, "range(16, 277)": 2, "range(17, 277)": 3, "range(209, 278)": 2,
 "range(211, 276)": 1,
 "if w < 276)": 1,
}
post_out = {k: s.count(k) for k, v in POST.items()}
receipt["post_blanket_forms"] = post_out
receipt["post_blanket_mismatches"] = [(k, c, v) for k, c, v in
                                      [(k, post_out[k], POST[k]) for k in POST] if c != v]
for m in receipt["post_blanket_mismatches"]:
    mismatch.append(("post:" + m[0], m[1], m[2]))

# ---- extract prereg-delivery prose lines VERBATIM (CRLF-aware) ----
lines = t.split("\r\n")
prose = [ln for ln in lines if "authored 09:0x" in ln]
receipt["prereg_delivery_lines"] = prose
receipt["prereg_delivery_context"] = []
for i, ln in enumerate(lines):
    if "authored 09:0x" in ln or "surgical-pushed to origin e0bc4a0ddd" in ln or "CAS-surgical r1113 origin" in ln:
        receipt["prereg_delivery_context"].append({"idx": i, "line": ln})

receipt["verdict"] = "PASS" if not mismatch else "MISMATCH"
io.open("results/_r1118bmc_needle_preflight.json", "w", encoding="utf-8", newline="\r\n").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("canon", receipt["canon_sha256_16"], receipt["canon_bytes"], "B")
print("raw mismatches:", [m for m in mismatch if not str(m[0]).startswith(("sim[", "post:"))])
print("sim mismatches:", [m for m in mismatch if str(m[0]).startswith("sim[")])
print("post mismatches:", receipt["post_blanket_mismatches"])
for p in prose:
    print("PROSE:", p[:170])
print("VERDICT", receipt["verdict"])
