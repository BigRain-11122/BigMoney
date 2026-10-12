# -*- coding: utf-8 -*-
# r934 bm-c: W223 editor derive PREFLIGHT (r787 zero-write law + r909 physical-byte law).
# Count-verify every candidate old-needle in the committed W222 template
# (_w222bmc_freeze_edits.py) BEFORE constructing the W223 derive table.
# Zero writes. Print repr of narrative anchors.
import io, json

SRC = r"results\_w222bmc_freeze_edits.py"
t = io.open(SRC, encoding="utf-8").read()
out = {}

def cnt(key, s):
    out[key] = {"needle": s[:80], "count": t.count(s)}

# ---- protect-region candidates (W222-template face = W222-derive restore values) ----
cnt("P3_old", "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg")
cnt("P2_old", "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg")
cnt("P1_old", "W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219 legs")
cnt("P8_old", "69 estate + W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219)")
cnt("P9_old", "own W211 leg + own W212 leg + own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg + own W218 leg + own W219 leg + own W220 leg")
cnt("P4_old", "int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76]), int(_estate_ws[77])")
cnt("P5_old", "[211, 212, 213, 214, 215, 216, 217, 218, 219]")
cnt("P6_old_keeps", "assert n1_t4.count('    # --- W220 materializer face') == 1  # prior block kept (W220 splice landed r923 window)")
cnt("P6_old_full", "assert n1_t4.count('    # --- W216 materializer face') == 1  # prior block kept (W216 splice landed r914 window)\nassert n1_t4.count('    # --- W217 materializer face') == 1  # prior block kept (W217 splice landed r916 window)\nassert n1_t4.count('    # --- W218 materializer face') == 1  # prior block kept (W218 splice landed r918 window)\nassert n1_t4.count('    # --- W219 materializer face') == 1  # prior block kept (W219 splice landed r920 window)\nassert n1_t4.count('    # --- W220 materializer face') == 1  # prior block kept (W220 splice landed r923 window)\nassert n1_t4.count('    # --- W221 materializer face') == 1  # prior block kept (W221 splice landed r927 window)")
cnt("P7_old", '"w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1')

# ---- next-wave + cascade counters ----
cnt("W223_next", "W223")
cnt("w223_lower", "w223")
cnt("W224", "W224")
cnt("W222_self", "W222")
cnt("W221_up", "W221")
cnt("w222_self_lower", "w222")

# ---- bare token forms ----
cnt("bare_cfgkey_f", '222: {{"batch"')
cnt("bare_cfgkey", '222: {"batch"')
cnt("bare_cfgkey_up", '221: {"batch"')
cnt("bare_rowkey_f", '222: {{"a"')
cnt("bare_rowkey", '222: {"a"')
cnt("bare_rowkey_up", '221: {"a"')
cnt("bare_nb221", "N1_BANDS[221]")
cnt("bare_nb220", "N1_BANDS[220]")
cnt("bare_nb220_re", "N1_BANDS\\[220\\]")
cnt("bare_wc222", "WAVE_CONFIGS[222]")
cnt("bare_wc221", "WAVE_CONFIGS[221]")
cnt("bare_r17", "range(17, 222)")
cnt("bare_r16", "range(16, 222)")
cnt("bare_wlt222", "w < 222")
cnt("bare_wlt221", "w < 221")
cnt("bare_setwave", "_set_wave(222)")
cnt("bare_waverc", '"wave": 222')
cnt("bare_get221", "get(221)")
cnt("bare_wave222c", "wave 222: ")
cnt("bare_wave222eq", "wave 222 = ")

# ---- W223-fact anchors ----
cnt("ledger_head_comma", "909,989")
cnt("merged_k_comma", "484,120")
cnt("ledger_head_us", "909_989")
cnt("merged_k_us", "484_120")
cnt("eleventh", "eleventh consecutive")
cnt("ord_third_anticipated", "EIGHTY-THIRD instance anticipated")
cnt("ord_second", "EIGHTY-SECOND")
cnt("ord_wave_no", "TWO HUNDRED AND TWENTY-SECOND")
cnt("band_a", "(503_204, 505_203)")
cnt("band_b", "(505_204, 505_403)")
cnt("ord_owner_bmc", "== 211 and len(bmc_rows_live) == 51")
cnt("ord_expect", "expect 211/51")
cnt("ord_precedent", "precedent 210/50")
cnt("ord_splice", "splice 211/51")
cnt("rows51", "rows 51 + candidate")
cnt("rows211", "rows 209 + candidate")
cnt("rows212", "rows 211 + candidate")
cnt("fifty_second", "fifty-second")
cnt("fiftysecond_short", "52nd")
cnt("ord_face_rc", '"probe_receipt_bmc_ordinal_face": 52')
cnt("bmc_ordinal", "bmc_ordinal=52")
cnt("seat_msg_w222", "MSG-20261012-1430-bmc-w222-seat")
cnt("seat_origin", "87ee1055d")
cnt("upstream_seat_msg", "MSG-20261012-1225")
cnt("arith_a", "arith_a222")
cnt("arith_b", "arith_b222")
cnt("n3r1", "n3r1_used222")
cnt("c221var", "_c221")
cnt("m220var", "m220")
cnt("ws_tail", "_estate_ws[-9:]")
cnt("cut78", "the 78-row cut")
cnt("ne79", "!= 79 (69 estate")
cnt("eq79", "== 79,")
cnt("eq78", "== 78")
cnt("rows80", "79 rows")
cnt("rows81", "80 rows")
cnt("trans_w220", "ledger 907,789 / K=481,920")
cnt("trans_w219", "ledger 905,589 / K=479,720")
cnt("trans_w218", "ledger 903,389 / K=477,520")
cnt("trans_w217", "ledger 901,189 / K=475,320")
cnt("trans_w216", "ledger 898,989 / K=473,120")
cnt("trans_w222", "ledger 912,189 / K=486,320")

# ---- narrative anchors (dump repr) ----
import re
narr = {}
for tag, pat in [
    ("hdr1", r"# 2026-10-12[^\n]*freeze[^\n]*"),
    ("fin_time", r"14:1x"),
    ("chain_honest", r"dead-window splice \+ POST-HOC[^\n]*"),
    ("prereg_bundle_note", r"in the r930 window[^\n]*"),
    ("repair_note", r"r927 splice \(dead-window[^\n]*"),
    ("r931_freeze", r"r931 freeze window"),
    ("r931_editor", r"r931 window editor"),
    ("phase_r934", r"\(r931 freeze window[^\n]*\)"),
    ("selftest_comment", r"range\(17, 22[0-9]\) at selftest time"),
    ("below221", r"below 22[0-9]"),
    ("w221_freeze_receipt", r"_w222bmc_freeze_receipt\.json"),
    ("w222_finalize_ts", r"15:4[0-9]"),
]:
    ms = re.findall(pat, t)
    narrr = [m[:160] for m in ms[:6]]
    narr[tag] = {"matches": len(ms), "samples": narrr}
out["_narrative"] = narr

# W222 finalize product timestamp + anchors machine-read
w222_out = json.load(open(r"results\perpetual_faces\n1_w222_results.json", encoding="utf-8"))
led = (w222_out.get("science_gates") or {}).get("ledger") or {}
merged_n = w222_out.get("null_pool_cumulative", {}).get("merged", {}).get("n_values")
out["w222_finalize"] = {"ledger_total": led.get("total"), "merged_n": merged_n}
rec = json.load(open(r"results\_w223bmc_20261012_probe_receipt.json", encoding="utf-8"))
out["w223_bands"] = rec["bands"]
out["w223_verdict"] = rec["verdict"]

io.open(r"results\_r934bmc_w223_edpreflight.json", "w", encoding="utf-8").write(
    json.dumps(out, indent=1, ensure_ascii=False))
for k, v in out.items():
    if k == "_narrative":
        continue
    if isinstance(v, dict) and "count" in v:
        print(f"{k:28s} count={v['count']:3d}  {v['needle'][:60]!r}")
print("w222_finalize:", out["w222_finalize"], "w223_bands:", out["w223_bands"])
print("--- narrative samples ---")
for k, v in narr.items():
    print(f"{k:24s} n={v['matches']}  {v['samples'][:2]}")
