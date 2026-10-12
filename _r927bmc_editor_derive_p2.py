# PART 2 of derive: passes + pairs + restores + postchecks. Concatenate after p1.

# ---- pre-pass special pairs (raw-text anchors) ----
rep("hdr1", "# 2026-10-12 11:4x bm-c r923 freeze (absorb r922 freeze-prep estate): W220 five-face freeze splice editor.",
    "# 2026-10-12 14:0x bm-c r927 freeze (absorb r925 committed prereg estate + r926 zero-commit scratch estate): W221 five-face freeze splice editor.")
rep("hdr2b", "finalize one-pass 10:1x, net chain head 905,589,", "finalize one-pass 12:0x, net chain head 907,789,")
rep("hdr3", "merged pool K=479,720, n1_w219_results.json machine-read) -- ZERO", "merged pool K=481,920, n1_w219_results.json machine-read) -- ZERO")
rep("hdr4", "ninth consecutive", "tenth consecutive")
rep("lin1", "_w219bmc_freeze_edits.py pattern (proven live-fire freeze,", "_w220bmc_freeze_edits.py pattern (proven live-fire freeze,")
rep("lin2", "r920 window executed) + r787", "r923 window executed) + r787")
rep("lin3", "(r920 window editor), structure known.", "(r923 window editor), structure known.")
rep("anc1", "== 905_589 and", "== 907_789 and")
rep("anc2", "== 479_720, ", "== 481_920, ")
rep("anc3", "(expect 905,589 / 479,720)", "(expect 907,789 / 481,920)")
rep("rcpt1", "results/_w220bmc_20261012_probe_receipt.json", "results/_w221bmc_20261012_probe_receipt.json", 8)
rep("rcpt1b", '"_w220bmc_20261012_probe_receipt.json"', '"_w221bmc_20261012_probe_receipt.json"')
rep("rcpt2", '"_w220bmc_freeze_receipt.json"', '"_w221bmc_freeze_receipt.json"')
# (prereg paths shift natively via the W-passes -- prg pairs removed, double-shift bug fixed)
rep("own1", "w220_prereg_sha", "w221_prereg_sha", 5)
rep("own2", "w220_receipt_sha", "w221_receipt_sha", 4)
rep("seatwin1", "@ r921 window; per-wave prereg +", "@ r924 window; per-wave prereg +", 2)
rep("seatwin2a", "MSG-20261012-0916, executed bm-c r920 freeze window; engine self-burn 12/12",
    "MSG-20261012-1025, executed bm-c r923 freeze window; engine self-burn 12/12")
rep("seatwin2b", "MSG-20261012-0916, executed bm-c r919 seat window; engine self-burn 12/12",
    "MSG-20261012-1025, executed bm-c r921 seat window; engine self-burn 12/12")
rep("fin11", "; finalize one-pass 10:1x), ", "; finalize one-pass 12:0x), ")
rep("fin12", "+ finalize one-pass 10:1x repair-free chain honest note)", "+ finalize one-pass 12:0x repair-free chain honest note)")
rep("rep1", '"r920 freeze + engine self-burn 12/12 + r921 finalize one-pass 10:1x (repair-free chain)"',
    '"r923 freeze + engine self-burn 12/12 + r923 finalize one-pass 12:0x (repair-free chain)"')
rep("bnd1", "landed in the r923 freeze-window bundle", "landed in the r927 freeze-window bundle", 2)
rep("bnd2", "# r923 freeze-window bundle, probe", "# r925 prereg derived + r927 freeze-window bundle, probe")
rep("bnd3", "(executed in the bm-c loop r923 freeze window ", "(executed in the bm-c loop r927 freeze window ")
rep("seat1", "MSG-20261012-1025-bmc-w220-seat", "MSG-20261012-1225-bmc-w221-seat", 4)
rep("seat2", "MSG-1025 tail", "MSG-1225 tail")
rep("ord1", "EIGHTY-FIRST instance anticipated", "EIGHTY-SECOND instance anticipated", 2)
rep("ord2", "EIGHTIETH", "EIGHTY-FIRST", 7)
rep("ord3", "fiftieth", "fifty-first", 2)
rep("ord4", "TWO HUNDRED AND TWENTIETH", "TWO HUNDRED AND TWENTY-FIRST", 3)
rep("ord5", "rows 49 + candidate; seat-time live face 50th = r921 probe leg0", "rows 50 + candidate; seat-time live face 51st = r924 probe leg0")
rep("ord6", "machine-derive (engine_owner==bm-c rows 49 + candidate; seat-time live face 50th disclosed, ",
    "machine-derive (engine_owner==bm-c rows 50 + candidate; seat-time live face 51st disclosed, ")
rep("ord7a", "(50th own wave per live derive r587/r359; ",
    "(51st own wave per live derive r587/r359; ")
rep("ord7b", "probe receipt leg0 bmc_ordinal=50 seat-time live face disclosed)",
    "probe receipt leg0 bmc_ordinal=51 seat-time live face disclosed)")
rep("ord8", '"probe_receipt_bmc_ordinal_face": 50,', '"probe_receipt_bmc_ordinal_face": 51,')
rep("ord9", "bm-c rows 49 + candidate = 50th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=50 = r921 seat-time live face -- disclosed honest)",
    "bm-c rows 50 + candidate = 51st owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=51 = r924 seat-time live face -- disclosed honest)")
rep("proj1", "W221p_A", "W222p_A", 2)
rep("proj2", "W221p_B", "W222p_B", 2)
rep("proj3", "will refuse the naive W221 A window", "will refuse the naive W222 A window", 2)
rep("proj4", "W221 freezer", "W222 freezer")
rep("proj5", "W221+ freezer MUST re-derive", "W222+ freezer MUST re-derive")
rep("proj6", "W221+ projection (gate-derived", "W222+ projection (gate-derived")
rep("proj7", "downstream W221 seat NOT yet published", "downstream W222 seat NOT yet published")
rep("proj8", "downstream W221 seat publication pending", "downstream W222 seat publication pending")
rep("prn1", "five-face freeze chain-order splice (r923 freeze window, upstream ALL LANDED clean precondition)",
    "five-face freeze chain-order splice (r927 freeze window, upstream ALL LANDED clean precondition)")
rep("prn2", '"wave": 220,', '"wave": 221,')
rep("org1", 'SEAT_ORIGIN = "13a81d182"', 'SEAT_ORIGIN = "063bb5a77"')
rep("wv1", "wave 220 = first free number after the", "wave 221 = first free number after the")
rep("wv2", "engine_owner=bm-c, wave 220: ", "engine_owner=bm-c, wave 221: ")

rep("band1", 'assert (a_lo, a_hi) == (498_804, 500_803) and (b_lo, b_hi) == (500_804, 501_003), \\',
    'assert (a_lo, a_hi) == (501_004, 503_003) and (b_lo, b_hi) == (503_004, 503_203), \\')
rep("fmt1", '# 498804 -> "498_804"', '# 501004 -> "501_004"')

# ---- bare-number pairs, descending ----
rep("n1", "'220: {\"a\"'", "'221: {\"a\"'")
rep("n2", "220: {{\"a\"", "221: {{\"a\"", 2)
rep("n3", "'    219: {\"a\"'", "'    220: {\"a\"'")
rep("n4", "'219: {\"a\"'", "'220: {\"a\"'", 2)
rep("n5", "'220: {\"batch\"", "'221: {\"batch\"", 2)
rep("n6", "220: {{\"batch\"", "221: {{\"batch\"")
rep("n7", "'219: {\"batch\"'", "'220: {\"batch\"'", 2)
rep("n8", "_c219", "_c220", 5)
rep("n9", "N1_BANDS[219]", "N1_BANDS[220]", 11)
rep("n10", "N1_BANDS[218]", "N1_BANDS[219]", 5)
rep("n11", "N1_BANDS\\[218\\]", "N1_BANDS\\[219\\]")
rep("n12", "N1_BANDS.get(219)", "N1_BANDS.get(220)")
rep("n13", "WAVE_CONFIGS[220]", "WAVE_CONFIGS[221]", 2)
rep("n14", "WAVE_CONFIGS[219]", "WAVE_CONFIGS[220]", 3)
rep("n15", "m218", "m219", 3)
rep("n16", "_set_wave(220)", "_set_wave(221)")
rep("n17", "if w < 220):", "if w < 221):", 2)
rep("n18", "range(17, 220):", "range(17, 221):")
rep("n19", "range(16, 220)", "range(16, 221)")
rep("n20", "arith_a220", "arith_a221", 3)
rep("n21", "arith_b220", "arith_b221", 3)
rep("n22", "n3r1_used220", "n3r1_used221", 3)
rep("n23", "PERPETUAL-N1-W220-SHARD-0", "PERPETUAL-N1-W221-SHARD-0", 2)
rep("n24", "PERPETUAL-N1-W220-SHARD-11", "PERPETUAL-N1-W221-SHARD-11")
rep("n25", "n1w220-0of12", "n1w221-0of12")
rep("n26", "n1w220-11of12", "n1w221-11of12")
rep("n27", '"batch": "PERPETUAL-N1-W220"', '"batch": "PERPETUAL-N1-W221"', 4)
rep("n28", "n1_w220", "n1_w221", 5)

# ---- variable-prefix passes, descending ----
for old, new in (("w219_", "w220_"), ("w218_", "w219_"), ("w217_", "w218_"), ("w216_", "w217_"), ("w215_", "w216_")):
    c = out.count(old)
    print("pass %s -> %s x%d" % (old, new, c))
    assert c > 0, "prefix pass dead: " + old
    out = out.replace(old, new)

# ---- W-token passes, descending ----
for old, new in (("W220", "W221"), ("W219", "W220"), ("W218", "W219"), ("W217", "W218"), ("W216", "W217"), ("W215", "W216")):
    c = out.count(old)
    print("pass %s -> %s x%d" % (old, new, c))
    assert c > 0, "W pass dead: " + old
    out = out.replace(old, new)

# ---- post-pass pair (precedence sentence references must stay W220) ----
rep("prec1",
    "expect 209/49 PRE-splice post-W221 registration; W221 precedent 208/48 pre-splice + W221 splice 209/49; this candidate = 50th own wave",
    "expect 210/50 PRE-splice post-W220 registration; W220 precedent 209/49 pre-splice + W220 splice 210/50; this candidate = 51st own wave")
rep("prec2", "len(owner_rows_live) == 209 and len(bmc_rows_live) == 49", "len(owner_rows_live) == 210 and len(bmc_rows_live) == 50")
