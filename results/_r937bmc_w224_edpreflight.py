# -*- coding: utf-8 -*-
# r937 bm-c: W224 editor derive PREFLIGHT (r787 zero-write law + r909 physical-byte law).
# Count-verify every candidate old-needle in the committed W223 template
# (_w223bmc_freeze_edits.py @ 448c4d8c2) BEFORE constructing the W224 derive table.
# Zero writes to repo files. Dump repr of narrative anchors + machine-read W224 facts.
import io, json, re, hashlib, subprocess

SRC = r"results\_w223bmc_freeze_edits.py"
t = io.open(SRC, encoding="utf-8").read()
out = {}

# ---- physical-byte law: on-disk file must equal committed blob ----
blob = subprocess.run(["git", "show", "448c4d8c2:results/_w223bmc_freeze_edits.py"],
                      capture_output=True).stdout
disk = open(SRC, "rb").read()
out["physical_byte_check"] = {
    "blob_len": len(blob), "disk_len": len(disk),
    "identical": blob == disk,
    "disk_sha16": hashlib.sha256(disk).hexdigest()[:16],
}

def cnt(key, s):
    out[key] = {"needle": s[:80], "count": t.count(s)}

# ---- protect-region candidates (W223-template face = r934 restore values) ----
cnt("P3_old", "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg + W222 leg")
cnt("P2_old", "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg")
cnt("P1_old", "W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219 + W220 legs")
cnt("P8_old", "69 estate + W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219 + W220)")
cnt("P9_old", "own W211 leg + own W212 leg + own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg + own W218 leg + own W219 leg + own W220 leg + own W221 leg")
cnt("P4_old", "int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76]), int(_estate_ws[77]), int(_estate_ws[78])")
cnt("P5_old", "[211, 212, 213, 214, 215, 216, 217, 218, 219, 220]")
P6_full = ("assert n1_t4.count('    # --- W216 materializer face') == 1  # prior block kept (W216 splice landed r914 window)\n"
           "assert n1_t4.count('    # --- W217 materializer face') == 1  # prior block kept (W217 splice landed r916 window)\n"
           "assert n1_t4.count('    # --- W218 materializer face') == 1  # prior block kept (W218 splice landed r918 window)\n"
           "assert n1_t4.count('    # --- W219 materializer face') == 1  # prior block kept (W219 splice landed r920 window)\n"
           "assert n1_t4.count('    # --- W220 materializer face') == 1  # prior block kept (W220 splice landed r923 window)\n"
           "assert n1_t4.count('    # --- W221 materializer face') == 1  # prior block kept (W221 splice landed r927 window)\n"
           "assert n1_t4.count('    # --- W222 materializer face') == 1  # prior block kept (W222 splice landed r931 window)")
cnt("P6_old_full", P6_full)
cnt("P7_old", '"w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1')

# ---- live-hit floor detection: apply protect placeholders, then count cascade tokens ----
t2 = t
for s in [
    out["P3_old"]["needle"], out["P2_old"]["needle"], out["P1_old"]["needle"],
    out["P8_old"]["needle"], out["P9_old"]["needle"], out["P4_old"]["needle"],
    out["P5_old"]["needle"], P6_full, out["P7_old"]["needle"],
]:
    t2 = t2.replace(s, "\x00PH\x00")
live = {}
for w in range(210, 226):
    live[f"W{w}"] = t2.count(f"W{w}")
    live[f"w{w}_lower"] = t2.count(f"w{w}")
out["live_after_protect"] = live

# ---- next-wave + cascade counters (raw) ----
cnt("W224_next", "W224")
cnt("w224_lower", "w224")
cnt("W223_self", "W223")
cnt("W222_up", "W222")
cnt("w223_self_lower", "w223")
cnt("w222_lower", "w222")

# ---- bare token forms (shifted +1 from r934 table) ----
cnt("bare_cfgkey_f", '223: {{"batch"')
cnt("bare_cfgkey", '223: {"batch"')
cnt("bare_cfgkey_up", '222: {"batch"')
cnt("bare_rowkey_f", '223: {{"a"')
cnt("bare_rowkey", '223: {"a"')
cnt("bare_rowkey_up", '222: {"a"')
cnt("bare_nb222", "N1_BANDS[222]")
cnt("bare_nb221", "N1_BANDS[221]")
cnt("bare_nb221_re", "N1_BANDS\\[221\\]")
cnt("bare_wc223", "WAVE_CONFIGS[223]")
cnt("bare_wc222", "WAVE_CONFIGS[222]")
cnt("bare_r17", "range(17, 223)")
cnt("bare_r16", "range(16, 223)")
cnt("bare_wlt223", "w < 223")
cnt("bare_wlt222", "w < 222")
cnt("bare_setwave", "_set_wave(223)")
cnt("bare_waverc", '"wave": 223')
cnt("bare_get222", "get(222)")
cnt("bare_wave223c", "wave 223: ")
cnt("bare_wave223eq", "wave 223 = ")
cnt("below222", "below 222")

# ---- W224-fact anchors (template = W223 facts, shift to W224 facts) ----
cnt("ledger_head_comma", "912,189")
cnt("merged_k_comma", "486,320")
cnt("ledger_head_us", "912_189")
cnt("merged_k_us", "486_320")
cnt("twelfth", "twelfth consecutive")
cnt("ord_fourth_anticipated", "EIGHTY-FOURTH instance anticipated")
cnt("ord_third", "EIGHTY-THIRD")
cnt("ord_wave_no", "TWO HUNDRED AND TWENTY-THIRD")
cnt("band_a", "(505_404, 507_403)")
cnt("band_b", "(507_404, 507_603)")
cnt("ord_owner_bmc", "== 212 and len(bmc_rows_live) == 52")
cnt("ord_expect", "expect 212/52")
cnt("ord_precedent", "precedent 211/51")
cnt("ord_splice", "splice 212/52")
cnt("rows52", "rows 52 + candidate")
cnt("rows211", "rows 211 + candidate")
cnt("rows212", "rows 212 + candidate")
cnt("fifty_third", "fifty-third")
cnt("fiftythird_short", "53rd")
cnt("ord_face_rc", '"probe_receipt_bmc_ordinal_face": 53')
cnt("bmc_ordinal", "bmc_ordinal=53")
cnt("seat_msg_160x", "MSG-20261012-160x-bmc-w223-seat")
cnt("seat_origin", "8f2d79147")
cnt("upstream_seat_msg", "MSG-20261012-1430")
cnt("arith_a", "arith_a223")
cnt("arith_b", "arith_b223")
cnt("n3r1", "n3r1_used223")
cnt("c222var", "_c222")
cnt("m221var", "m221")
cnt("ws_tail", "_estate_ws[-10:]")
cnt("cut79", "the 79-row cut")
cnt("ne80", "!= 80 (69 estate")
cnt("eq80c", "== 80,")
cnt("eq79", "== 79")
cnt("rows81", "81 rows")
cnt("trans_w222", "ledger 912,189 / K=486,320")
cnt("trans_w221", "ledger 909,989 / K=484,120")
cnt("trans_w220", "ledger 907,789 / K=481,920")
cnt("trans_w219", "ledger 905,589 / K=479,720")
cnt("trans_w218", "ledger 903,389 / K=477,520")
cnt("trans_w217", "ledger 901,189 / K=475,320")

# ---- narrative anchors (dump repr contexts) ----
narr = {}
for tag, pat in [
    ("hdr1", r"# 2026-10-12[^\n]*freeze[^\n]*"),
    ("fin_time", r"15:4x"),
    ("chain_splice", r"r931 splice \(dead-window continuation\)[^\n]*"),
    ("phase_r934", r"\(r934 freeze window[^\n]*\)"),
    ("this_r934", r"in this r934 freeze window[^\n]*"),
    ("r931_freeze", r"r931 freeze window"),
    ("r931_editor", r"r931 window editor"),
    ("r929_seat", r"r929 seat window"),
    ("r932_window", r"r932 window"),
    ("r932_seattime", r"r932 seat-time"),
    ("r933_prereg", r"r933 prereg derived[^\n]*"),
    ("r934_bundle", r"r934 freeze-window bundle"),
    ("prereg_note", r"in the r933 window[^\n]*"),
    ("below222c", r"below 222"),
    ("w222_receipt", r"_w222bmc_freeze_receipt\.json"),
    ("w223_receipt", r"_w223bmc_freeze_receipt\.json"),
    ("selftest_cmt", r"range\(17, 22[0-9]\) at selftest time"),
]:
    ms = re.findall(pat, t)
    narr[tag] = {"matches": len(ms), "samples": [m[:200] for m in ms[:6]]}
out["_narrative"] = narr

# ---- machine-read facts (never transcribed) ----
w223 = json.load(open(r"results\perpetual_faces\n1_w223_results.json", encoding="utf-8"))
led = (w223.get("science_gates") or {}).get("ledger") or {}
merged_n = w223.get("null_pool_cumulative", {}).get("merged", {}).get("n_values")
out["w223_finalize"] = {
    "ledger_total": led.get("total"), "merged_n": merged_n,
    "keys": [k for k in w223.keys()][:12],
    "generated": w223.get("generated"), "ts": w223.get("ts"),
}
rec = json.load(open(r"results\_w224bmc_20261012_probe_receipt.json", encoding="utf-8"))
out["w224_bands"] = rec["bands"]; out["w224_verdict"] = rec["verdict"]

io.open(r"results\_r937bmc_w224_edpreflight.json", "w", encoding="utf-8").write(
    json.dumps(out, indent=1, ensure_ascii=False))
for k, v in out.items():
    if k in ("_narrative", "live_after_protect", "w223_finalize", "w224_bands", "w224_verdict", "physical_byte_check"):
        continue
    if isinstance(v, dict) and "count" in v:
        print(f"{k:26s} count={v['count']:3d}  {v['needle'][:58]!r}")
print("physical_byte:", out["physical_byte_check"])
print("live_after_protect:", {k: v for k, v in live.items() if v})
print("w223_finalize:", {k: v for k, v in out["w223_finalize"].items() if v})
print("w224_bands:", out["w224_bands"], out["w224_verdict"])
print("--- narrative ---")
for k, v in narr.items():
    print(f"{k:16s} n={v['matches']}  {[s[:110] for s in v['samples'][:2]]}")
