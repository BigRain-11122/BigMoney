# -*- coding: utf-8 -*-
# r937 bm-c: W224 five-face freeze splice editor derive -- count-asserted
# ordered transform from the committed W223 template (_w223bmc_freeze_edits.py
# @ 448c4d8c2, proven live-fire splice: executed r934 window, landed by own
# commit 448c4d8c2). Protect-restore regions + fail-closed pair law (r927/r931
# precedent; W222 sec.8 standing law). Preflight receipts:
# results/_r937bmc_w224_edpreflight.json + _r937bmc_w224_edpreflight2 output
# (all counts machine-verified on the physical template bytes, r909 law).
# W224 facts (machine-derived, never transcribed): bands A 507_604..509_603 /
# B 509_604..509_803 from ADMIT receipt _w224bmc_20261012_probe_receipt.json;
# W223 finalize anchors 914,389 / K=488,520 (n1_w223_results.json machine-read,
# generated 2026-10-12 17:28:52 -> face "17:2x"); W224 seat MSG
# MSG-20261012-175x-bmc-w224-seat origin e2676c8eb (r935 publish); W223 chain
# = r934 splice (dead-window estate, landed by own commit) + engine self-burn
# 12/12 + r935 finalize (six-gate PRE-FINALIZE all-green 17:24:44, 3rd
# consecutive correct-phase); W224 prereg = r936 ac1b1de64 EIGHT-level lineage
# replay chain; W225+ projection EIGHTY-FIFTH anticipated.
import io, json, hashlib, py_compile

SRC = r"results\_w223bmc_freeze_edits.py"
DST = r"results\_w224bmc_freeze_edits.py"
REC = r"results\_w224bmc_editor_derive_receipt.json"
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
protect("P3", "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg + W222 leg", 1,
        "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg + W222 leg + W223 leg")
protect("P2", "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg", 1,
        "W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg + W221 leg + W222 leg")
protect("P1", "W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219 + W220 legs", 2,
        "W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219 + W220 + W221 legs")
protect("P8", "69 estate + W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219 + W220)", 1,
        "69 estate + W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 + W219 + W220 + W221)")
protect("P9", "own W211 leg + own W212 leg + own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg + own W218 leg + own W219 leg + own W220 leg + own W221 leg", 1,
        "own W211 leg + own W212 leg + own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg + own W218 leg + own W219 leg + own W220 leg + own W221 leg + own W222 leg")
protect("P4", "int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76]), int(_estate_ws[77]), int(_estate_ws[78])", 1,
        "int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76]), int(_estate_ws[77]), int(_estate_ws[78]), int(_estate_ws[79])")
protect("P5", "[211, 212, 213, 214, 215, 216, 217, 218, 219, 220]", 1,
        "[211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221]")
_keeps = ("assert n1_t4.count('    # --- W216 materializer face') == 1  # prior block kept (W216 splice landed r914 window)\n"
          "assert n1_t4.count('    # --- W217 materializer face') == 1  # prior block kept (W217 splice landed r916 window)\n"
          "assert n1_t4.count('    # --- W218 materializer face') == 1  # prior block kept (W218 splice landed r918 window)\n"
          "assert n1_t4.count('    # --- W219 materializer face') == 1  # prior block kept (W219 splice landed r920 window)\n"
          "assert n1_t4.count('    # --- W220 materializer face') == 1  # prior block kept (W220 splice landed r923 window)\n"
          "assert n1_t4.count('    # --- W221 materializer face') == 1  # prior block kept (W221 splice landed r927 window)\n"
          "assert n1_t4.count('    # --- W222 materializer face') == 1  # prior block kept (W222 splice landed r931 window)")
protect("P6", _keeps, 1, _keeps + "\nassert n1_t4.count('    # --- W223 materializer face') == 1  # prior block kept (W223 splice landed r934 window)")
protect("P7", '"w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1', 1,
        '"w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1, "w223_block_kept": 1')

# ---------- next-wave projection tokens: template W224 (its own next-wave face)
# MUST shift to W225 BEFORE the self-cascade creates fresh W224 tokens ----------
rep("W224", "W225", 7, "w224_next")

# ---------- cascade (descending: self 223->224 first, upstream 222->223, ...) ----------
casc("W223", "W224", "casc_W223")
casc("W222", "W223", "casc_W222")
casc("W221", "W222", "casc_W221")
casc("W220", "W221", "casc_W220")
casc("W219", "W220", "casc_W219")
casc("W218", "W219", "casc_W218")   # cascade floor W218: every W217/w217 live hit
# inside protect regions (P6 keeps + P3/P2/P1/P8/P9 chain restores), machine-counted r937 preflight
casc("w223", "w224", "casc_w223")
casc("w222", "w223", "casc_w222")
casc("w221", "w222", "casc_w221")
casc("w220", "w221", "casc_w220")
casc("w219", "w220", "casc_w219")
casc("w218", "w219", "casc_w218")   # small-case floor w218 (gate0.5 transitive vars)

# bare token forms (self first, then upstream)
rep('223: {{"batch"', '224: {{"batch"', 1, "bare_cfgkey_f")
rep('223: {"batch"', '224: {"batch"', 2, "bare_cfgkey")
rep('222: {"batch"', '223: {"batch"', 2, "bare_cfgkey_up")
rep('223: {{"a"', '224: {{"a"', 2, "bare_rowkey_f")
rep('223: {"a"', '224: {"a"', 1, "bare_rowkey")
rep('222: {"a"', '223: {"a"', 3, "bare_rowkey_up")
rep("N1_BANDS[222]", "N1_BANDS[223]", 11, "bare_nb222")
rep("N1_BANDS[221]", "N1_BANDS[222]", 5, "bare_nb221")
rep("N1_BANDS\\[221\\]", "N1_BANDS\\[222\\]", 1, "bare_nb221_re")
rep("WAVE_CONFIGS[223]", "WAVE_CONFIGS[224]", 2, "bare_wc223")
rep("WAVE_CONFIGS[222]", "WAVE_CONFIGS[223]", 3, "bare_wc222")
rep("range(17, 223)", "range(17, 224)", 2, "bare_r17")
rep("range(16, 223)", "range(16, 224)", 1, "bare_r16")
rep("w < 223", "w < 224", 2, "bare_wlt223")
rep("w < 222", "w < 223", 1, "bare_wlt222")
rep("_set_wave(223)", "_set_wave(224)", 1, "bare_setwave")
rep('"wave": 223', '"wave": 224', 1, "bare_waverc")
rep("get(222)", "get(223)", 1, "bare_get222")
rep("wave 223: ", "wave 224: ", 1, "bare_wave223c")
rep("wave 223 = ", "wave 224 = ", 1, "bare_wave223eq")

# ---------- manual fixes (wave-224 facts; order-sensitive pairs marked) ----------
rep("2026-10-12 17:3x bm-c r934 freeze window", "2026-10-12 18:4x bm-c r937 freeze window", 1, "hdr_line1")
rep("(r934 freeze window, upstream ALL LANDED clean precondition)",
    "(r937 freeze window, upstream ALL LANDED clean precondition)", 1, "phase_r937")
rep("in this r934 freeze window", "in this r937 freeze window", 1, "prereg_bundle_w")
# W223 finalize face (n1_w223_results.json generated 17:28:52 machine-read) BEFORE chain lines
rep("15:4x", "17:2x", 4, "fin_time")   # all 4 = hdr note + upstream-freeze note + n1 comment + chain line
# upstream wave-chain narrative rolls (W222 chain -> W223 chain facts, honest six-gate phase)
rep("r931 splice (dead-window continuation)", "r934 splice (dead-window estate, landed by own commit)", 1, "chain_splice")
rep("r932 finalize one-pass 17:2x (six-gate POST-HOC heal, W212-family 4th instance disclosed)",
    "r935 finalize one-pass 17:2x (six-gate PRE-FINALIZE all-green 17:24:44, 3rd consecutive correct-phase)", 1, "chain_line1")
rep("finalize one-pass 17:2x dead-window splice + POST-HOC six-gate heal chain, honest note",
    "finalize one-pass 17:2x dead-window splice estate + PRE-FINALIZE six-gate all-green chain, honest note", 1, "chain_line2")
rep("r931 freeze window", "r934 freeze window", 2, "r931_freeze")
rep("r931 window editor", "r934 window editor", 1, "r931_editor")
rep("r929 seat window", "r932 seat window", 1, "r929_seat")
rep("r932 window", "r935 window", 2, "r932_probe")
rep("r932 seat-time", "r935 seat-time", 1, "r932_seattime")
rep("r933 prereg derived + r934 freeze-window bundle, probe",
    "r936 prereg derived + r937 freeze-window bundle, probe", 1, "r933_line")
rep("r934 freeze-window bundle", "r937 freeze-window bundle", 2, "r934_bundle")
rep("in the r933 window (b7d46427d, SEVEN-level lineage replay chain",
    "in the r936 window (ac1b1de64, EIGHT-level lineage replay chain", 1, "prereg_note")
# W224 facts (all machine-read: n1_w223_results.json + W224 probe receipt + seat MSG git log)
rep("912,189", "914,389", 2, "ledger_head_comma")
rep("486,320", "488,520", 2, "merged_k_comma")
rep("912_189", "914_389", 1, "ledger_head_us")
rep("486_320", "488_520", 1, "merged_k_us")
rep("twelfth consecutive", "thirteenth consecutive", 2, "thirteenth")
rep("EIGHTY-FOURTH instance anticipated", "EIGHTY-FIFTH instance anticipated", 2, "ord_fifth_anticipated")
rep("EIGHTY-THIRD", "EIGHTY-FOURTH", 7, "ord_fourth")
rep("TWO HUNDRED AND TWENTY-THIRD", "TWO HUNDRED AND TWENTY-FOURTH", 3, "ord_wave_no")
rep("(505_404, 507_403)", "(507_604, 509_603)", 1, "band_a")
rep("(507_404, 507_603)", "(509_604, 509_803)", 1, "band_b")
rep("== 212 and len(bmc_rows_live) == 52", "== 213 and len(bmc_rows_live) == 53", 1, "ord_owner_bmc")
rep("expect 212/52", "expect 213/53", 1, "ord_expect")
rep("precedent 211/51", "precedent 212/52", 1, "ord_precedent")
rep("splice 212/52", "splice 213/53", 1, "ord_splice")
rep("rows 52 + candidate", "rows 53 + candidate", 3, "rows53")
rep("rows 212 + candidate", "rows 213 + candidate", 1, "rows213")
rep("fifty-third", "fifty-fourth", 2, "fifty_fourth")
rep("53rd", "54th", 5, "fiftythird_short")
rep('"probe_receipt_bmc_ordinal_face": 53', '"probe_receipt_bmc_ordinal_face": 54', 1, "ord_face_rc")
rep("bmc_ordinal=53", "bmc_ordinal=54", 2, "bmc_ordinal")
rep("MSG-20261012-1430", "MSG-20261012-160x", 2, "upstream_seat_msg")
rep("MSG-20261012-160x-bmc-w224-seat", "MSG-20261012-175x-bmc-w224-seat", 4, "seat_msg_175x")
rep("8f2d79147", "e2676c8eb", 1, "seat_origin")
rep("below 222", "below 223", 1, "below223")
# transitive ledger chain (descending order -- highest-value shifts first)
rep("ledger 909,989 / K=484,120", "ledger 912,189 / K=486,320", 1, "trans_w222")
rep("ledger 907,789 / K=481,920", "ledger 909,989 / K=484,120", 1, "trans_w221")
rep("ledger 905,589 / K=479,720", "ledger 907,789 / K=481,920", 1, "trans_w220")
rep("ledger 903,389 / K=477,520", "ledger 905,589 / K=479,720", 1, "trans_w219")
rep("arith_a223", "arith_a224", 3, "arith_a")
rep("arith_b223", "arith_b224", 3, "arith_b")
rep("n3r1_used223", "n3r1_used224", 3, "n3r1")
rep("_c222", "_c223", 5, "c222var")
rep("m221", "m222", 3, "m221var")
rep("_estate_ws[-10:]", "_estate_ws[-11:]", 1, "ws_tail")
rep("the 79-row cut", "the 80-row cut", 1, "cut80")
rep("!= 80 (69 estate", "!= 81 (69 estate", 1, "ne81")      # BEFORE eq81
rep("== 80,", "== 81,", 1, "eq81")                           # BEFORE eq80
rep("== 79", "== 80", 1, "eq80")                             # AFTER eq81
rep("81 rows", "82 rows", 2, "rows82")

# ---------- restore protected regions ----------
for key, (restore, n) in PH.items():
    ph = f"\x00{key}\x00"
    c = t.count(ph)
    assert c == n, f"restore[{key}] placeholder count {c} != {n}"
    t = t.replace(ph, restore)

# ---------- machine-read fact gates (never transcribed; r934 receipt-key alignment law) ----------
probe = json.load(open(r"results\_w224bmc_20261012_probe_receipt.json", encoding="utf-8"))
leg4 = probe["legs"]["leg4"]
assert "W224p_A" in leg4 and "W224p_B" in leg4, f"W224 probe receipt leg4 keys {list(leg4)[:6]} do not match editor key tokens"
assert probe["bands"]["A"] == "507604_509603" and probe["bands"]["B"] == "509604_509803", "W224 probe bands drift vs derive"
assert probe["verdict"] == "ADMIT", "W224 probe verdict != ADMIT"
fin = json.load(open(r"results\perpetual_faces\n1_w223_results.json", encoding="utf-8"))
led_total = (fin.get("science_gates") or {}).get("ledger", {}).get("total")
merged_n = fin.get("null_pool_cumulative", {}).get("merged", {}).get("n_values")
assert led_total == 914389 and merged_n == 488520, f"W223 finalize anchors drift: {led_total}/{merged_n}"

# ---------- post-conditions ----------
assert "\x00" not in t, "placeholder bytes leaked"
assert t.count("W224") > 60 and t.count("PERPETUAL-N1-W224") >= 3
assert t.count("507_604") >= 1 and t.count("509_604") >= 1
assert t.count("914,389") == 2 and t.count("488,520") == 2
assert t.count("912,189") == 1 and t.count("486,320") == 1   # transitive chain W222 entry only
assert t.count("EIGHTY-FIFTH instance anticipated") == 2
assert t.count("EIGHTY-FOURTH instance anticipated") == 0
assert t.count("EIGHTY-FOURTH instance") == 5 or t.count("EIGHTY-FOURTH") == 7
assert t.count("TWO HUNDRED AND TWENTY-FOURTH") == 3
assert t.count("MSG-20261012-175x-bmc-w224-seat") == 4
assert t.count("MSG-20261012-160x") == 2                    # upstream bare refs
assert t.count("e2676c8eb") == 1
assert t.count("== 213 and len(bmc_rows_live) == 53") == 1
assert t.count("w < 224") == 2 and t.count("w < 223") == 1
assert t.count("range(17, 224)") == 2 and t.count("range(16, 224)") == 1  # code line + selftest comment
assert t.count("W223 materializer face") == 2  # a15 estate-source marker + restored keep-list line
assert t.count("W216 materializer face") == 1  # restored keep-list
assert t.count("W223 splice landed r934 window") == 1
assert t.count("W224p_A") == 2 and t.count("W224p_B") == 2 and t.count("W223p_") == 0
assert t.count("17:2x") == 4   # 4x fin_time (hdr + upstream-freeze + n1 comment + chain line)
assert t.count("15:4x") == 0
assert t.count("thirteenth consecutive") == 2 and t.count("twelfth consecutive") == 0
assert t.count("PRE-FINALIZE") == 2 and t.count("POST-HOC") == 0
assert t.count("r931 splice") == 0 and t.count("r934 splice (dead-window estate, landed by own commit)") == 1
assert t.count("r935 finalize one-pass 17:2x") == 1 and t.count("r932 finalize one-pass") == 0
assert t.count("below 223") == 1 and t.count("below 222") == 0

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
rec = {"machine": "bm-c", "derive": "W224 freeze editor (ordered count-asserted transform from committed W223 template 448c4d8c2)",
       "src": SRC, "dst": DST, "counts": counts,
       "src_sha16": hashlib.sha256(io.open(SRC, "rb").read()).hexdigest()[:16],
       "dst_sha16": hashlib.sha256(t.encode("utf-8")).hexdigest()[:16],
       "protect_restore_keys": sorted(PH),
       "receipt_key_gate": "W224 probe leg4 keys W224p_A/W224p_B match editor tokens (pre-execution hard gate)",
       "anchor_gate": "n1_w223_results.json ledger 914,389 / merged 488,520 machine-read"}
io.open(REC, "w", encoding="utf-8").write(json.dumps(rec, indent=1, ensure_ascii=False))
print("DERIVE OK:", json.dumps(counts, ensure_ascii=False)[:600])
print("dst sha16:", rec["dst_sha16"])
