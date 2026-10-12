# -*- coding: utf-8 -*-
# r931 bm-c: W222 five-face freeze splice editor derive -- count-asserted
# ordered transform from the committed W221 template (_w221bmc_freeze_edits.py,
# proven live-fire freeze r928 window). Protect-restore regions + fail-closed
# pair law (r927 precedent; W221 sec.8 standing law: conditional boundary
# pairs transformed atomically -- LHS w< and RHS range() shift together).
import io, json, hashlib, py_compile

SRC = r"results\_w221bmc_freeze_edits.py"
DST = r"results\_w222bmc_freeze_edits.py"
REC = r"results\_w222bmc_editor_derive_receipt.json"
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
protect("P3", "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg", 1,
        "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg")
protect("P2", "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg", 1,
        "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg")
protect("P1", "W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 legs", 2,
        "W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219 legs")
protect("P8", "69 estate + W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218)", 1,
        "69 estate + W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219)")
protect("P9", "own W211 leg + own W212 leg + own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg + own W218 leg + own W219 leg", 1,
        "own W211 leg + own W212 leg + own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg + own W218 leg + own W219 leg + own W220 leg")
protect("P4", "int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76])", 1,
        "int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76]), int(_estate_ws[77])")
protect("P5", "[211, 212, 213, 214, 215, 216, 217, 218]", 1,
        "[211, 212, 213, 214, 215, 216, 217, 218, 219]")
_keeps = ("assert n1_t4.count('    # --- W216 materializer face') == 1  # prior block kept (W216 splice landed r914 window)\n"
          "assert n1_t4.count('    # --- W217 materializer face') == 1  # prior block kept (W217 splice landed r916 window)\n"
          "assert n1_t4.count('    # --- W218 materializer face') == 1  # prior block kept (W218 splice landed r918 window)\n"
          "assert n1_t4.count('    # --- W219 materializer face') == 1  # prior block kept (W219 splice landed r920 window)\n"
          "assert n1_t4.count('    # --- W220 materializer face') == 1  # prior block kept (W220 splice landed r923 window)")
protect("P6", _keeps, 1, _keeps + "\nassert n1_t4.count('    # --- W221 materializer face') == 1  # prior block kept (W221 splice landed r927 window)")
protect("P7", '"w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1', 1,
        '"w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1')

# ---------- next-wave projection tokens: template W222 (its own next-wave face)
# MUST shift to W223 BEFORE the self-cascade creates fresh W222 tokens ----------
rep("W222", "W223", 11, "w222_next")

# ---------- cascade (descending: self 221->222 first, upstream 220->221, ...) ----------
casc("W221", "W222", "casc_W221")
casc("W220", "W221", "casc_W220")
casc("W219", "W220", "casc_W219")
casc("W218", "W219", "casc_W218")
casc("W217", "W218", "casc_W217")
casc("W216", "W217", "casc_W216")
casc("w221", "w222", "casc_w221")
casc("w220", "w221", "casc_w220")
casc("w219", "w220", "casc_w219")
casc("w218", "w219", "casc_w218")
casc("w217", "w218", "casc_w217")
casc("w216", "w217", "casc_w216")
# bare token forms (descending)
rep('221: {{"batch"', '222: {{"batch"', 1, "bare_cfgkey_f")
rep('221: {"batch"', '222: {"batch"', 2, "bare_cfgkey")
rep('220: {"batch"', '221: {"batch"', 2, "bare_cfgkey_up")
rep('221: {{"a"', '222: {{"a"', 2, "bare_rowkey_f")
rep('221: {"a"', '222: {"a"', 1, "bare_rowkey")
rep('220: {"a"', '221: {"a"', 3, "bare_rowkey_up")
rep("N1_BANDS[220]", "N1_BANDS[221]", 11, "bare_nb220")
rep("N1_BANDS[219]", "N1_BANDS[220]", 5, "bare_nb219")
rep("N1_BANDS\\[219\\]", "N1_BANDS\\[220\\]", 1, "bare_nb219_re")
rep("WAVE_CONFIGS[221]", "WAVE_CONFIGS[222]", 2, "bare_wc221")
rep("WAVE_CONFIGS[220]", "WAVE_CONFIGS[221]", 3, "bare_wc220")
rep("range(17, 221)", "range(17, 222)", 1, "bare_r17")
rep("range(16, 221)", "range(16, 222)", 1, "bare_r16")
rep("w < 221", "w < 222", 2, "bare_wlt221")
rep("w < 220", "w < 221", 1, "bare_wlt220")
rep("_set_wave(221)", "_set_wave(222)", 1, "bare_setwave")
rep('"wave": 221', '"wave": 222', 1, "bare_waverc")
rep("get(220)", "get(221)", 1, "bare_get220")
rep("wave 221: ", "wave 222: ", 1, "bare_wave221c")
rep("wave 221 = ", "wave 222 = ", 1, "bare_wave221eq")

# ---------- manual fixes (wave-222 facts; order-sensitive pairs marked) ----------
rep("2026-10-12 14:0x bm-c r927 freeze (absorb r925 committed prereg estate + r926 zero-commit scratch estate): W222 five-face freeze splice editor.",
    "2026-10-12 15:2x bm-c r931 freeze window (upstream W1..W221 ALL LANDED, clean precondition): W222 five-face freeze splice editor.",
    1, "hdr_line1")
rep("12:0x", "14:1x", 4, "fin_time")
rep("907,789", "909,989", 2, "ledger_head_comma")
rep("481,920", "484,120", 2, "merged_k_comma")
rep("907_789", "909_989", 1, "ledger_head_us")
rep("481_920", "484_120", 1, "merged_k_us")
rep("tenth consecutive", "eleventh consecutive", 2, "eleventh")
rep("EIGHTY-SECOND instance anticipated", "EIGHTY-THIRD instance anticipated", 2, "ord_third")   # BEFORE ord_second
rep("EIGHTY-FIRST", "EIGHTY-SECOND", 7, "ord_second")
rep("TWO HUNDRED AND TWENTY-FIRST", "TWO HUNDRED AND TWENTY-SECOND", 3, "ord_wave_no")
rep("501_004, 503_003", "503_204, 505_203", 1, "band_a")
rep("503_004, 503_203", "505_204, 505_403", 1, "band_b")
rep("== 210 and len(bmc_rows_live) == 50", "== 211 and len(bmc_rows_live) == 51", 1, "ord_owner_bmc")
rep("expect 210/50", "expect 211/51", 1, "ord_expect")
rep("precedent 209/49", "precedent 210/50", 1, "ord_precedent")
rep("splice 210/50", "splice 211/51", 1, "ord_splice")
rep("rows 50 + candidate", "rows 51 + candidate", 3, "rows51")
rep("rows 209 + candidate", "rows 211 + candidate", 1, "rows211")
rep("fifty-first", "fifty-second", 2, "fifty_second")
rep("51st", "52nd", 5, "fiftysecond_short")
rep('"probe_receipt_bmc_ordinal_face": 51', '"probe_receipt_bmc_ordinal_face": 52', 1, "ord_face_rc")
rep("bmc_ordinal=51", "bmc_ordinal=52", 2, "bmc_ordinal")
rep("MSG-20261012-1025", "MSG-20261012-1225", 2, "upstream_seat_msg")
rep("MSG-20261012-1225-bmc-w222-seat", "MSG-20261012-1430-bmc-w222-seat", 4, "seat_msg_1430")
rep("063bb5a77", "87ee1055d", 1, "seat_origin")
rep("r923 freeze window", "r927 freeze window", 1, "r923_freeze")
rep("r923 window editor", "r927 window editor", 1, "r923_editor")
# (keep-list r923->r927 line fix is handled by the P6 restore: W221 line appended
#  with its own comment; the W220 line's historical comment stays verbatim)
rep("r921 seat window", "r924 seat window", 1, "r921_seat")
rep("r924 window", "r929 window", 2, "r924_probe")
rep("r924 seat-time", "r929 seat-time", 1, "r924_seattime")
rep("r925 prereg derived + r927 freeze-window bundle", "r930 prereg derived + r931 freeze-window bundle", 1, "r925_line")
rep("r927 freeze-window bundle", "r931 freeze-window bundle", 2, "r927_bundle")
rep("r927 absorb window", "r931 freeze window", 1, "r927_absorb")
rep("repair-free chain honest note", "dead-window splice + POST-HOC six-gate heal chain, honest note", 1, "chain_honest")
rep("r923 freeze + engine self-burn 12/12 + r923 finalize one-pass 14:1x (repair-free chain)",
    "r927 splice (dead-window continuation) + engine self-burn 12/12 + r928 finalize one-pass 14:1x (six-gate POST-HOC heal, W212-family 4th instance disclosed)",
    1, "repair_note")
rep("in the r925 dead window (2e251d084, five-level lineage replay + editor_gen fix replay, preflight 46/46; anchor-verification scratch from the r926 zero-commit dead window absorbed); splice editor derived from the committed W221 editor template",
    "in the r930 window (58f82fd63, six-level lineage replay chain, preflight 46/46); splice editor derived from the committed W221 editor template",
    1, "prereg_bundle_note")
rep("range(17, 220) at selftest time", "range(17, 222) at selftest time", 1, "selftest_comment")
rep("below 220", "below 221", 1, "below221")
rep("ledger 905,589 / K=479,720", "ledger 907,789 / K=481,920", 1, "trans_w220")   # descending order
rep("ledger 903,389 / K=477,520", "ledger 905,589 / K=479,720", 1, "trans_w219")
rep("ledger 901,189 / K=475,320", "ledger 903,389 / K=477,520", 1, "trans_w218")
rep("ledger 898,989 / K=473,120", "ledger 901,189 / K=475,320", 1, "trans_w217")
rep("arith_a221", "arith_a222", 3, "arith_a")
rep("arith_b221", "arith_b222", 3, "arith_b")
rep("n3r1_used221", "n3r1_used222", 3, "n3r1")
rep("_c220", "_c221", 5, "c220var")
rep("m219", "m220", 3, "m219var")
rep("_estate_ws[-8:]", "_estate_ws[-9:]", 1, "ws_tail")
rep("the 77-row cut", "the 78-row cut", 1, "cut78")
rep("!= 78 (69 estate", "!= 79 (69 estate", 1, "ne79")      # BEFORE eq78
rep("== 78,", "== 79,", 1, "eq79")
rep("== 77", "== 78", 1, "eq78")                              # AFTER eq79
rep("79 rows", "80 rows", 2, "rows80")
rep("(r927 freeze window, upstream ALL LANDED clean precondition)",
    "(r931 freeze window, upstream ALL LANDED clean precondition)", 1, "phase_r931")

# ---------- restore protected regions ----------
for key, (restore, n) in PH.items():
    ph = f"\x00{key}\x00"
    c = t.count(ph)
    assert c == n, f"restore[{key}] placeholder count {c} != {n}"
    t = t.replace(ph, restore)

# ---------- post-conditions ----------
assert "\x00" not in t, "placeholder bytes leaked"
assert t.count("W222") > 60 and t.count("PERPETUAL-N1-W222") >= 3
assert t.count("503_204") >= 1 and t.count("505_204") >= 1
assert t.count("909,989") == 2 and t.count("484,120") == 2
assert t.count("EIGHTY-THIRD instance anticipated") == 2
assert t.count("EIGHTY-SECOND instance") == 5 or t.count("EIGHTY-SECOND") == 7
assert t.count("MSG-20261012-1430-bmc-w222-seat") == 4
assert t.count("87ee1055d") == 1
assert t.count("== 211 and len(bmc_rows_live) == 51") == 1
assert t.count("w < 222") == 2 and t.count("w < 221") == 1
assert t.count("range(17, 222)") == 2 and t.count("range(16, 222)") == 1  # code line + selftest comment
assert t.count("W221 materializer face") == 2  # a15 estate-source marker + restored keep-list line
assert t.count("W216 materializer face") == 1  # restored keep-list
assert t.count("W221 splice landed r927 window") == 1
assert t.count("W223p_A") == 2 and t.count("W223p_B") == 2 and t.count("W222p_") == 0

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
rec = {"machine": "bm-c", "derive": "W222 freeze editor (ordered count-asserted transform from committed W221 template)",
       "src": SRC, "dst": DST, "counts": counts,
       "src_sha16": hashlib.sha256(io.open(SRC, "rb").read()).hexdigest()[:16],
       "dst_sha16": hashlib.sha256(t.encode("utf-8")).hexdigest()[:16],
       "protect_restore_keys": sorted(PH)}
io.open(REC, "w", encoding="utf-8").write(json.dumps(rec, indent=1, ensure_ascii=False))
print("DERIVE OK:", json.dumps(counts, ensure_ascii=False)[:400])
print("dst sha16:", rec["dst_sha16"])
