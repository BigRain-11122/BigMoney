# -*- coding: utf-8 -*-
# r1123 bm-c splice window: W279 editor NEEDLE PREFLIGHT (r1077 measured-counts law)
# Measures every needle count on the committed W278 freeze-edits canon
# (results/_w278bmc_freeze_edits.py, bm-c r1118 splice window b6f486af35,
# proven live-fire: W278 five-face splice + engine self-burn 12/12 + finalize
# one-pass ledger 1,035,935 / K=609,520 EXACT, machine-verified by the r1119
# closeout 0a92fcc28f) BEFORE the W279 editor is authored.
# Table = the r1118 preflight table rolled ONE generation (W278 canon faces);
# any first-run mismatch = preflight-table heal (measured governs, disclosed).
# W279 FACTS (probe receipt results/_w279bmc_20261019_probe_receipt.json,
# committed with the seat @ 900c23fe7d r1119, ADMIT): bands A 629_101..631_100
# (TWENTY-EIGHTH consecutive A-hop, staircase-affects-A, hops=1; naive A
# 628_901..630_900 refused at the registered W278 B band 628_901..629_100) /
# B 631_101..631_300 (TWENTY-NINTH consecutive above-own-A, own-A reservation
# cascade, hops=1; naive B 629_101..629_300 lands inside the own-A window
# 629_101..631_100); seed_admit FREE x2 (base=629101 span=2000 / base=631101
# span=200); ordinals owner 268 + candidate = 269th / bm-c rows 97 + candidate
# = 98th; W278 finalize anchors 1,035,935 / K=609,520 (chain +2,200/+2,200
# EXACT); leg4 W280p projections naive A 631_101..633_100 / naive B
# 631_301..631_500 (hops 0/0; W280p_B_lands_inside_W280p_A_naive staircase face
# continuing since W251).
import io, subprocess, hashlib, json

CANON = "results/_w278bmc_freeze_edits.py"
CRLF = "\r\n"

blob_wt = subprocess.run(["git", "hash-object", CANON], capture_output=True, text=True).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:" + CANON], capture_output=True, text=True).stdout.strip()
blob_origin = subprocess.run(["git", "rev-parse", "origin/main:" + CANON], capture_output=True, text=True).stdout.strip()
assert blob_wt == blob_head == blob_origin and len(blob_wt) == 40, \
    f"canon blob drift wt={blob_wt} head={blob_head} origin={blob_origin}"

t = io.open(CANON, encoding="utf-8", newline="").read()
assert t.count(CRLF) > t.count("\n") - t.count(CRLF), "canon EOL face drift (CRLF expected)"
receipt = {
 "tool": "r1123 needle preflight",
 "canon": CANON,
 "canon_blob": blob_wt,
 "canon_sha256_16": hashlib.sha256(t.encode("utf-8")).hexdigest()[:16],
 "canon_bytes": len(t.encode("utf-8")),
 "eol": "CRLF",
}

RAW = {
 # phase-1 projections + bands + ints + ledger/lc/seat (src faces, rolled one gen)
 "W279p": 13, "W279": 26,
 "628_901": 5, "629_100": 4, "628_900": 9, "628_700": 2,
 "626_901": 8, "627_100": 2, "626_701": 4, "626_900": 6,
 "628901": 1, "630900": 1, "629101": 2, "629300": 2,
 "1,033,735": 6, "607,320": 6, "1_033_735": 1, "607_320": 1,
 "n1_w278": 4, "n1w278-": 2, "w278_": 13, "n1_w277": 4, "w277_": 93,
 "_w278bmc_": 11, "_w277bmc_freeze_edits.py template": 1,
 "MSG-20261019-102x-bmc-w278-seat": 7,
 'SEAT_ORIGIN = "b187aa6214"': 1, "b187aa6214 r1114-continuation": 1,
 "b187aa6214": 2, "9e53371814": 1, "99001d3d3f337942": 2, "df1aaba72a": 1,
 "(E63 canon-clone builder _r1116bmc_build_w278_derive.py)": 1,
 "2026-10-19 13:3x bm-c r1118 splice window": 1,
 '"wave": 277': 1,
 "frozen sha16 99001d3d3f337942": 1, "frozen 99001d3d3f337942": 1,
 "push-race-": 2, "authored 12:2x": 2,  # push-race- x2 = BOTH delivery prose forms (hdr CRLF-split + note compound); preflight-table heal run-1 (expected 1, measured governs)
 # phase-2 blankets
 "W278": 96, "W277": 158,
 # phase-3 pre/post forms (measured on RAW; post-blanket forms simulated below)
 "W275_W276_W277_bands_respected": 2,
 "W211..W276 legs (66)": 1, "W211..W276 sixty-six legs": 1, "range(211, 277)": 1,
 "own W248..W276 legs (29)": 4,
 "W248..W276 twenty-nine legs": 1,
 'N1_BANDS[") == 29': 1,
 "W211..W277 legs 66": 1,
 "W248..W278 legs (30": 4,
 "block = 136 rows": 1, "136 parity rows": 1, "block parity = 136 rows": 1,
 'N1_BANDS[") == 135,': 1, "!= 135": 1, 'N1_BANDS[") == 66': 1,
 '"fresh_legs_row_asserts": 30': 1, "+ 30,": 1,
 "range(248, 278)": 2, "range(248, 277)": 1, "range(16, 278)": 2,
 "range(17, 278)": 3, "range(209, 279)": 2,
 "if w < 278)": 5, "if w < 277)": 1, "278 - _lw": 2, "_w == 277": 1,
 "WAVE_CONFIGS[278]": 2, "WAVE_CONFIGS[277]": 3, "N1_BANDS[277]": 5,
 "get(277)": 1, "_c277": 5,
 '278: {"batch"': 2, '278: {{"batch"': 1, '278: {"a"': 1, '278: {{"a"': 2,
 '277: {"batch"': 2, '277: {"a"': 3,
 "arith_a278": 6, "arith_b278": 6,
 "(274, 273, 272, 271, 270, 269, 268, 267, 266, 265)": 2, "W265..W274": 1,
 "len(owner_rows_live) == 267 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 96": 1,
 "267/130/96": 1, "owner_rows=267 / bma_rows=130 / bmc_rows=96": 1,
 "rows 267 + candidate = 268th": 2, "; bm-c rows 96 +": 1,
 "bm-c rows 96 + candidate = 97th owned": 1, "# candidate = 97th EXACT": 1,
 "engine_owner==bm-c rows 96 + candidate": 1,
 "bm-c rows {len(bmc_rows_live)} + candidate (97th own wave": 1,
 "bm-c's 97th own wave": 2, "NINETY-SEVENTH owned": 3,
 "TWO HUNDRED AND SEVENTY-EIGHTH": 3, "bmc_rows=96": 7,
 '"probe_receipt_bmc_ordinal_face": 96': 1,
 "bmc rows 96 + candidate 97th": 1,
 "TWENTY-EIGHTH": 7, "TWENTY-SEVENTH": 15, "twenty-eighth": 4, "twenty-seventh": 3,
 "sixty-sixth": 2, "sixty-six legs": 1,
 "wave 278 engine_owner=bm-c": 1, '"wave 278: "': 1, "wave 278 = first free number": 1,
 "cycle COMPLETE bm-c r1114-continuation closeout 10:4x": 1,
 "bm-c r1114-continuation splice window": 2, "own-wave full cycle r1114-continuation": 1,
 "bm-c splice generation r1114-continuation window": 1, "verified r1114-continuation": 1,
 "# r1114-continuation splice window": 1, "(bm-c r1114-continuation": 1,
 "finalize one-pass bm-c r1114-continuation closeout, ledger": 1,
 "finalize one-pass bm-c r1114-continuation closeout ledger": 1,
 "(r1114-continuation MSG-": 1, "r1114-continuation BEFORE this freeze": 1,
 "seat itself r1114-continuation; queue-head": 1, "(r1114-continuation, queue-head seat-first supply": 1,
 "bm-c r1116 window": 4, "# r1116 window": 1,
 "(R277: ": 1, "_set_wave(278)": 1,
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
 "W278 FREEZE UNBLOCKED": 4, "PRE-W278-splice": 1, "post-W277 registration": 2,
 "post-W277-REGISTERED": 8,
 "anchors W277 1,033,735 / K=607,320 at draft": 1,
 "PERPETUAL_N1_W278_PREREG": 8, "PERPETUAL_N1_W277_PREREG": 2, "PERPETUAL-N1-W278": 7,
 "W278 materializer face": 4, "W277 materializer face": 1,
 "W277 finalize product": 4, "W279 walk": 1,
 "expect 267/130/96": 1, "sixty-sixth consecutive": 2,
 "bm-c five-face freeze upstream seat": 1, "bm-c (upstream seat honored)": 1,
 "owner=bm-c seat honored": 1,
 "N1_BANDS[248] ==": 1, "N1_BANDS\\[248\\]": 1,
 # date-roll face (expect count 0 again this generation)
 "20261018": 0, "2026-10-18": 0,
 # residual probes (faces that must NOT exist in canon)
 "c2fc7c34d0e41a68": 0, "ba5c725b42": 0, "900c23fe7d": 0, "b6f486af35": 0,
 "MSG-20261019-145x": 0, "_w279bmc_": 0, "n1_w279": 0, "w279_": 0, "n1w279-": 0,
 "631_101": 0, "631101": 0, "631_300": 0, "631_301": 0, "631301": 0,
 "633_100": 0, "633100": 0, "631_500": 0, "631500": 0,
 "1,035,935": 0, "609,520": 0, "1_035_935": 0, "609_520": 0,
 "TWENTY-NINTH": 0, "twenty-ninth": 0, "NINETY-EIGHTH owned": 0,
 "TWO HUNDRED AND SEVENTY-NINTH": 0,
 "W280p": 0, "W280": 0, "r1119": 0, "r1122": 0, "r1123": 0,
 "18:5x": 0, "19:2x": 0, "sixty-seventh": 0,
 "rows 268 + candidate": 0, "bmc_rows=97": 0, "268/130/97": 0,
 "range(248, 279)": 0, "range(16, 279)": 0, "if w < 279)": 0, '"wave": 278': 0,
 "arith_a279": 0, "PERPETUAL-N1-W279": 0,
 "W276_W277_W278_bands_respected": 0, "W274_W275_W276_bands_respected": 0,
 "0a92fcc28f": 0, "efc4a1c1bb": 0, "60e630918f": 0, "b965e2ecf0": 0,
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
r("W279p", "W280p", 13, "proj_prefix")
r("W279", "W280", 13, "proj_plain")
r("628_901", "631_101", 5, "Blo"); r("629_100", "631_300", 4, "Bhi")
r("628_900", "631_100", 9, "Ahi"); r("628_700", "630_900", 2, "naiveAhi")
r("626_901", "629_101", 8, "Alo"); r("627_100", "629_300", 2, "Bnaivehi")
r("626_701", "628_901", 4, "naiveAlo_priorBlo"); r("626_900", "629_100", 6, "priorBhi")
r("628901", "631101", 1, "iAlo"); r("630900", "633100", 1, "iAhi")
r("629101", "631301", 2, "iBlo"); r("629300", "631500", 2, "iBhi")
r("1,033,735", "1,035,935", 6, "led"); r("607,320", "609,520", 6, "k")
r("1_033_735", "1_035_935", 1, "ledcode"); r("607_320", "609_520", 1, "kcode")
r("(E63 canon-clone builder _r1116bmc_build_w278_derive.py)",
  "(E63 canon-clone builder _r1122bmc_build_w279_derive.py)", 1, "builder")
r("n1_w278", "n1_w279", 4, "n1own"); r("n1w278-", "n1w279-", 2, "n1dash")
r("w278_", "w279_", 10, "lcown")
r("n1_w277", "n1_w278", 4, "n1up"); r("w277_", "w278_", 89, "lcup")
r("_w278bmc_", "_w279bmc_", 11, "rcpt")
r("_w277bmc_freeze_edits.py template", "_w278bmc_freeze_edits.py template", 1, "templ")
r("MSG-20261019-102x-bmc-w278-seat", "MSG-20261019-145x-bmc-w279-seat", 7, "seatmsg")
r('SEAT_ORIGIN = "b187aa6214"', 'SEAT_ORIGIN = "900c23fe7d"', 1, "seatconst")
r("b187aa6214 r1114-continuation", "900c23fe7d r1119", 1, "seathdr")
r("9e53371814", "b6f486af35", 1, "lineagesha")
r("(authored 12:2x, banned_direction_gate ADMIT rc0, frozen sha16 99001d3d3f337942 + push-race-" + CRLF +
    "# healed landed to origin df1aaba72a, r1116 window).",
  "(authored 18:5x, banned_direction_gate ADMIT rc0, frozen sha16 c2fc7c34d0e41a68 + pushed first-try-post-" + CRLF +
    "# rebase landed to origin ba5c725b42, r1122 window).",
  1, "prereg_delivery_hdr")
r("(authored 12:2x, banned gate ADMIT rc0, frozen 99001d3d3f337942 -> push-race-healed r1116 origin ",
  "(authored 18:5x, banned gate ADMIT rc0, frozen c2fc7c34d0e41a68 -> pushed-first-try-post-rebase r1122 origin ",
  1, "prereg_delivery_note")
r("2026-10-19 13:3x bm-c r1118 splice window", "2026-10-19 19:2x bm-c r1123 splice window", 1, "hdrstamp")
r('"wave": 277', '"wave": 278', 1, "rwave")
r("W278", "W279", 96, "ownD")
r("W277", "W278", 158, "upD")
POST = {
 "W275_W276_W278_bands_respected": 2,
 "W211..W278 legs 66": 1,
 "W248..W279 legs (30": 4,
 "range(248, 278)": 2, "range(16, 278)": 2, "range(17, 278)": 3, "range(209, 279)": 2,
 "range(211, 277)": 1,
 "if w < 277)": 1,
}
post_out = {k: s.count(k) for k, v in POST.items()}
receipt["post_blanket_forms"] = post_out
receipt["post_blanket_mismatches"] = [(k, c, v) for k, c, v in
                                      [(k, post_out[k], POST[k]) for k in POST] if c != v]
for m in receipt["post_blanket_mismatches"]:
    mismatch.append(("post:" + m[0], m[1], m[2]))

# ---- extract prereg-delivery prose lines VERBATIM (CRLF-aware) ----
lines = t.split("\r\n")
prose = [ln for ln in lines if "authored 12:2x" in ln]
receipt["prereg_delivery_lines"] = prose
receipt["prereg_delivery_context"] = []
for i, ln in enumerate(lines):
    if "authored 12:2x" in ln or "healed landed to origin df1aaba72a" in ln or "push-race-healed r1116 origin" in ln:
        receipt["prereg_delivery_context"].append({"idx": i, "line": ln})

receipt["verdict"] = "PASS" if not mismatch else "MISMATCH"
io.open("results/_r1123bmc_needle_preflight.json", "w", encoding="utf-8", newline="\r\n").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("canon", receipt["canon_sha256_16"], receipt["canon_bytes"], "B")
print("raw mismatches:", [m for m in mismatch if not str(m[0]).startswith(("sim[", "post:"))])
print("sim mismatches:", [m for m in mismatch if str(m[0]).startswith("sim[")])
print("post mismatches:", receipt["post_blanket_mismatches"])
for p in prose:
    print("PROSE:", p[:170])
print("VERDICT", receipt["verdict"])
