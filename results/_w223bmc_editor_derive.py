# -*- coding: utf-8 -*-
# r934 bm-c: W223 five-face freeze splice editor derive -- count-asserted
# ordered transform from the committed W222 template (_w222bmc_freeze_edits.py,
# proven live-fire splice: executed r931 dead-window, absorbed+landed r932
# 4167d791d). Protect-restore regions + fail-closed pair law (r927/r931
# precedent; W222 sec.8 standing law). Preflight round1/round2 receipts:
# results/_r934bmc_w223_edpreflight.json + _r934bmc_w223_edpreflight2 output
# (all counts machine-verified on the physical template bytes, r909 law).
# W223 facts (machine-derived, never transcribed): bands A 505_404..507_403 /
# B 507_404..507_603 from ADMIT receipt _w223bmc_20261012_probe_receipt.json;
# W222 finalize anchors 912,189 / K=486,320 (n1_w222_results.json machine-read,
# generated 2026-10-12 15:46:37 -> face "15:4x"); W223 seat MSG-20261012-160x
# origin 8f2d79147 (r932 publish); W222 chain = dead-window splice (r931
# executed, r932 absorbed) + POST-HOC six-gate heal (W212-family 4th instance);
# W223 prereg = r933 b7d46427d seven-level lineage replay.
import io, json, hashlib, py_compile

SRC = r"results\_w222bmc_freeze_edits.py"
DST = r"results\_w223bmc_freeze_edits.py"
REC = r"results\_w223bmc_editor_derive_receipt.json"
t = io.open(SRC, encoding="utf-8").read()
counts = {}

def rep(old, new, n, what):
    global t
    c = t.count(old)
    assert c == n, f"[{what}] count {c} != {n} for {old[:70]!r}"
    t = t.replace(old, new)
    assert t.count(old) == 0, f"[{what}] leftover {old[:50]!r}"
    counts[what] = c

def casc(old, new, what):
    global t
    c = t.count(old)
    assert c > 0, f"[{what}] cascade token absent: {old[:50]!r}"
    t = t.replace(old, new)
    assert t.count(old) == 0, f"[{what}] cascade leftover {old[:50]!r}"
    counts[what] = c

PH = {}
def protect(key, s, n, restore):
    global t
    c = t.count(s)
    assert c == n, f"[protect {key}] count {c} != {n}"
    ph = f"\x00{key}\x00"
    t = t.replace(s, ph)
    PH[key] = (restore, n)

# ---------- P0: protect exception regions (order: longest-first P3 > P2) ----------
protect("P3", "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg", 1,
        "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg + W222 leg")
protect("P2", "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg", 1,
        "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg")
protect("P1", "W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219 legs", 2,
        "W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219 + W220 legs")
protect("P8", "69 estate + W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219)", 1,
        "69 estate + W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219 + W220)")
protect("P9", "own W211 leg + own W212 leg + own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg + own W218 leg + own W219 leg + own W220 leg", 1,
        "own W211 leg + own W212 leg + own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg + own W218 leg + own W219 leg + own W220 leg + own W221 leg")
protect("P4", "int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76]), int(_estate_ws[77])", 1,
        "int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76]), int(_estate_ws[77]), int(_estate_ws[78])")
protect("P5", "[211, 212, 213, 214, 215, 216, 217, 218, 219]", 1,
        "[211, 212, 213, 214, 215, 216, 217, 218, 219, 220]")
_keeps = ("assert n1_t4.count('    # --- W216 materializer face') == 1  # prior block kept (W216 splice landed r914 window)\n"
          "assert n1_t4.count('    # --- W217 materializer face') == 1  # prior block kept (W217 splice landed r916 window)\n"
          "assert n1_t4.count('    # --- W218 materializer face') == 1  # prior block kept (W218 splice landed r918 window)\n"
          "assert n1_t4.count('    # --- W219 materializer face') == 1  # prior block kept (W219 splice landed r920 window)\n"
          "assert n1_t4.count('    # --- W220 materializer face') == 1  # prior block kept (W220 splice landed r923 window)\n"
          "assert n1_t4.count('    # --- W221 materializer face') == 1  # prior block kept (W221 splice landed r927 window)")
protect("P6", _keeps, 1, _keeps + "\nassert n1_t4.count('    # --- W222 materializer face') == 1  # prior block kept (W222 splice landed r931 window)")
protect("P7", '"w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1', 1,
        '"w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1')

# ---------- next-wave projection tokens: template W223 (its own next-wave face)
# MUST shift to W224 BEFORE the self-cascade creates fresh W223 tokens ----------
rep("W223", "W224", 11, "w223_next")

# ---------- cascade (descending: self 222->223 first, upstream 221->222, ...) ----------
casc("W222", "W223", "casc_W222")
casc("W221", "W222", "casc_W221")
casc("W220", "W221", "casc_W220")
casc("W219", "W220", "casc_W219")
casc("W218", "W219", "casc_W218")
casc("W217", "W218", "casc_W217")   # cascade floor W217: every W216/w216 live hit
# inside protect regions (P1x2/P3/P8/P9/P6x2 + P7), machine-counted r934 preflight
casc("w222", "w223", "casc_w222")
casc("w221", "w222", "casc_w221")
casc("w220", "w221", "casc_w220")
casc("w219", "w220", "casc_w219")
casc("w218", "w219", "casc_w218")
casc("w217", "w218", "casc_w217")   # small-case floor w217 (gate0.5 transitive vars)

# bare token forms (descending)
rep('222: {{"batch"', '223: {{"batch"', 1, "bare_cfgkey_f")
rep('222: {"batch"', '223: {"batch"', 2, "bare_cfgkey")
rep('221: {"batch"', '222: {"batch"', 2, "bare_cfgkey_up")
rep('222: {{"a"', '223: {{"a"', 2, "bare_rowkey_f")
rep('222: {"a"', '223: {"a"', 1, "bare_rowkey")
rep('221: {"a"', '222: {"a"', 3, "bare_rowkey_up")
rep("N1_BANDS[221]", "N1_BANDS[222]", 11, "bare_nb221")
rep("N1_BANDS[220]", "N1_BANDS[221]", 5, "bare_nb220")
rep("N1_BANDS\\[220\\]", "N1_BANDS\\[221\\]", 1, "bare_nb220_re")
rep("WAVE_CONFIGS[222]", "WAVE_CONFIGS[223]", 2, "bare_wc222")
rep("WAVE_CONFIGS[221]", "WAVE_CONFIGS[222]", 3, "bare_wc221")
rep("range(17, 222)", "range(17, 223)", 2, "bare_r17")
rep("range(16, 222)", "range(16, 223)", 1, "bare_r16")
rep("w < 222", "w < 223", 2, "bare_wlt222")
rep("w < 221", "w < 222", 1, "bare_wlt221")
rep("_set_wave(222)", "_set_wave(223)", 1, "bare_setwave")
rep('"wave": 222', '"wave": 223', 1, "bare_waverc")
rep("get(221)", "get(222)", 1, "bare_get221")
rep("wave 222: ", "wave 223: ", 1, "bare_wave222c")
rep("wave 222 = ", "wave 223 = ", 1, "bare_wave222eq")

# ---------- manual fixes (wave-223 facts; order-sensitive pairs marked) ----------
rep("2026-10-12 15:2x bm-c r931 freeze window (upstream W1..W222 ALL LANDED, clean precondition): W223 five-face freeze splice editor.",
    "2026-10-12 17:3x bm-c r934 freeze window (upstream W1..W222 ALL LANDED, clean precondition): W223 five-face freeze splice editor.",
    1, "hdr_line1")
rep("(r931 freeze window, upstream ALL LANDED clean precondition)",
    "(r934 freeze window, upstream ALL LANDED clean precondition)",
    1, "phase_r934")
rep("in this r931 freeze window", "in this r934 freeze window", 1, "prereg_bundle_w")
# upstream wave-chain narrative rolls (W221 chain -> W222 chain facts)
rep("r927 splice (dead-window continuation)", "r931 splice (dead-window continuation)", 1, "chain_splice")
rep("r928 finalize one-pass", "r932 finalize one-pass", 1, "chain_fin")
rep("r927 freeze window", "r931 freeze window", 2, "r927_freeze")
rep("r927 window editor", "r931 window editor", 1, "r927_editor")
rep("r924 seat window", "r929 seat window", 1, "r924_seat")
rep("r929 window", "r932 window", 2, "r929_probe")
rep("r929 seat-time", "r932 seat-time", 1, "r929_seattime")
rep("r930 prereg derived + r931 freeze-window bundle, probe",
    "r933 prereg derived + r934 freeze-window bundle, probe", 1, "r925_line")
rep("r931 freeze-window bundle", "r934 freeze-window bundle", 2, "r927_bundle")
rep("in the r930 window (58f82fd63, six-level lineage replay chain",
    "in the r933 window (b7d46427d, SEVEN-level lineage replay chain", 1, "prereg_note")
# W223 facts
rep("14:1x", "15:4x", 4, "fin_time")   # all 4 = hdr note + pf_row + n1 comment + repair_chain_note
rep("909,989", "912,189", 2, "ledger_head_comma")
rep("484,120", "486,320", 2, "merged_k_comma")
rep("909_989", "912_189", 1, "ledger_head_us")
rep("484_120", "486_320", 1, "merged_k_us")
rep("eleventh consecutive", "twelfth consecutive", 2, "twelfth")
rep("EIGHTY-THIRD instance anticipated", "EIGHTY-FOURTH instance anticipated", 2, "ord_fourth_anticipated")
rep("EIGHTY-SECOND", "EIGHTY-THIRD", 7, "ord_third")
rep("TWO HUNDRED AND TWENTY-SECOND", "TWO HUNDRED AND TWENTY-THIRD", 3, "ord_wave_no")
rep("(503_204, 505_203)", "(505_404, 507_403)", 1, "band_a")
rep("(505_204, 505_403)", "(507_404, 507_603)", 1, "band_b")
rep("== 211 and len(bmc_rows_live) == 51", "== 212 and len(bmc_rows_live) == 52", 1, "ord_owner_bmc")
rep("expect 211/51", "expect 212/52", 1, "ord_expect")
rep("precedent 210/50", "precedent 211/51", 1, "ord_precedent")
rep("splice 211/51", "splice 212/52", 1, "ord_splice")
rep("rows 51 + candidate", "rows 52 + candidate", 3, "rows52")
rep("rows 211 + candidate", "rows 212 + candidate", 1, "rows212")
rep("fifty-second", "fifty-third", 2, "fifty_second")
rep("52nd", "53rd", 5, "fiftysecond_short")
rep('"probe_receipt_bmc_ordinal_face": 52', '"probe_receipt_bmc_ordinal_face": 53', 1, "ord_face_rc")
rep("bmc_ordinal=52", "bmc_ordinal=53", 2, "bmc_ordinal")
rep("MSG-20261012-1225", "MSG-20261012-1430", 2, "upstream_seat_msg")
rep("MSG-20261012-1430-bmc-w223-seat", "MSG-20261012-160x-bmc-w223-seat", 4, "seat_msg_160x")
rep("87ee1055d", "8f2d79147", 1, "seat_origin")
rep("below 221", "below 222", 1, "below222")
# transitive ledger chain (descending order -- longest-value shifts first)
rep("ledger 907,789 / K=481,920", "ledger 909,989 / K=484,120", 1, "trans_w221")
rep("ledger 905,589 / K=479,720", "ledger 907,789 / K=481,920", 1, "trans_w220")
rep("ledger 903,389 / K=477,520", "ledger 905,589 / K=479,720", 1, "trans_w219")
rep("ledger 901,189 / K=475,320", "ledger 903,389 / K=477,520", 1, "trans_w218")
rep("arith_a222", "arith_a223", 3, "arith_a")
rep("arith_b222", "arith_b223", 3, "arith_b")
rep("n3r1_used222", "n3r1_used223", 3, "n3r1")
rep("_c221", "_c222", 5, "c221var")
rep("m220", "m221", 3, "m220var")
rep("_estate_ws[-9:]", "_estate_ws[-10:]", 1, "ws_tail")
rep("the 78-row cut", "the 79-row cut", 1, "cut79")
rep("!= 79 (69 estate", "!= 80 (69 estate", 1, "ne80")      # BEFORE eq80
rep("== 79,", "== 80,", 1, "eq80")                            # BEFORE eq79
rep("== 78", "== 79", 1, "eq79")                              # AFTER eq80
rep("80 rows", "81 rows", 2, "rows81")

# ---------- restore protected regions ----------
for key, (restore, n) in PH.items():
    ph = f"\x00{key}\x00"
    c = t.count(ph)
    assert c == n, f"restore[{key}] placeholder count {c} != {n}"
    t = t.replace(ph, restore)

# ---------- post-conditions ----------
assert "\x00" not in t, "placeholder bytes leaked"
assert t.count("W223") > 60 and t.count("PERPETUAL-N1-W223") >= 3
assert t.count("505_404") >= 1 and t.count("507_404") >= 1
assert t.count("912,189") == 2 and t.count("486,320") == 2
assert t.count("EIGHTY-FOURTH instance anticipated") == 2
assert t.count("EIGHTY-THIRD instance") == 5 or t.count("EIGHTY-THIRD") == 7
assert t.count("MSG-20261012-160x-bmc-w223-seat") == 4
assert t.count("8f2d79147") == 1
assert t.count("== 212 and len(bmc_rows_live) == 52") == 1
assert t.count("w < 223") == 2 and t.count("w < 222") == 1
assert t.count("range(17, 223)") == 2 and t.count("range(16, 223)") == 1  # code line + selftest comment
assert t.count("W222 materializer face") == 2  # a15 estate-source marker + restored keep-list line
assert t.count("W216 materializer face") == 1  # restored keep-list
assert t.count("W222 splice landed r931 window") == 1
assert t.count("W224p_A") == 2 and t.count("W224p_B") == 2 and t.count("W223p_") == 0
assert t.count("15:4x") == 4   # 4x fin_time (hdr + pf_row + n1 comment + repair_chain_note)
assert t.count("14:1x") == 0

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
rec = {"machine": "bm-c", "derive": "W223 freeze editor (ordered count-asserted transform from committed W222 template)",
       "src": SRC, "dst": DST, "counts": counts,
       "src_sha16": hashlib.sha256(io.open(SRC, "rb").read()).hexdigest()[:16],
       "dst_sha16": hashlib.sha256(t.encode("utf-8")).hexdigest()[:16],
       "protect_restore_keys": sorted(PH)}
io.open(REC, "w", encoding="utf-8").write(json.dumps(rec, indent=1, ensure_ascii=False))
print("DERIVE OK:", json.dumps(counts, ensure_ascii=False)[:500])
print("dst sha16:", rec["dst_sha16"])
