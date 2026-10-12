# -*- coding: utf-8 -*-
# r927 bm-c: W221 five-face freeze editor derivation (transform-gen).
# Source template = results/_w220bmc_freeze_edits.py (committed, proven live-fire
# r923). Method = ordered count-asserted replacements (r787 preflight law) with
# placeholder-protected regions whose preserved text must NOT wave-shift
# (kept-list / liveness / receipt-transitive / prereg-note / estate-extension
# comments). Find strings are written against POST-BLANKET text where the
# wave-shift passes produce the intermediate (r925 editor_gen fix law).
# Output = results/_w221bmc_freeze_edits.py. Zero transcription of preserved
# template bytes (r909 physical-byte law); every pair fails LOUD on count drift.
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SRC = open(r"results\_w220bmc_freeze_edits.py", encoding="utf-8").read()
out = SRC
fails = []

def rep(tag, old, new, n=1):
    global out
    c = out.count(old)
    if c != n:
        print("FAIL[%s] count %d != %d: %r" % (tag, c, n, old[:90]))
        fails.append(tag)
        return
    out = out.replace(old, new)
    print("ok[%s] x%d" % (tag, n))

def grab(tag, start, end):
    """Cut [start..start+len) .. [end..end+len) segment out into PROTECT[tag]; leave @@tag@@."""
    global out
    i = out.find(start)
    assert i >= 0, "grab[%s] start miss: %r" % (tag, start[:60])
    j = out.find(end, i)
    assert j >= 0, "grab[%s] end miss: %r" % (tag, end[:60])
    j += len(end)
    PROTECT[tag] = out[i:j]
    out = out[:i] + "@@%s@@" % tag + out[j:]
    print("grab[%s] %dB" % (tag, len(PROTECT[tag])))

PROTECT = {}

# ---- protected region extraction (pre-pass) ----
# P1 kept-list count gates (W209..W219 block faces; extend with W220, no shift)
grab("KEPTLIST", "assert n1_t4.count('    # --- W209 materializer face')", "(W219 splice landed r920 window)")
# P2 receipt liveness anchors (extend with w220_block_kept, no shift)
grab("LIVENESS", '"liveness_anchors": {"t141_marker_kept": 1', '"w219_block_kept": 1},')
# P3 receipt transitive entries (w218/w217/w216/w215 -> keep w218..w216, add w219, drop w215)
grab("TRANSITIVE", '"w218_transitive": {"finalize_product"', 'ledger 896,789 / K=470,920)"}')
# P4 receipt prereg_bundle note (full rewrite)
grab("PREREGNOTE", '"note": "r923 freeze-window bundle (absorb:', 'placeholder class-guard"')
# P5 receipt parity_section note (extend legs to W218, W220 block, 79 rows)
grab("PARITYNOTE", 'full-span estate W138..W206 (69 rows, r858 absorb generation) + W211 + W212 + W213 + W214 + W215 + W216 + W217 legs -> W220 block = 78 rows ending at W219',
     'W220 block = 78 rows ending at W219')
# P6 header STRUCTURAL CHOICE rows-parens (78->79 rows, legs W211..W220)
grab("STRUCTROWS", "(78 rows: estate 69", "W219 leg).")
# P7 par_full count assert block (77->78, error legs extended by W219)
grab("PARFULL", 'assert par_full.count("assert pf.N1_BANDS[") == 77, \\', 'W218 leg)"')
# P8 extraction-comment leg list (own W211..W218 -> own W211..W219)
grab("OWNLEGS", "+ own W211 leg + own W212 leg", "own W218 leg)")
# P9 par_sec count assert block (76->77, list +218, error legs +W218, -8 tail)
grab("PARSEC", 'assert par_sec.count("assert pf.N1_BANDS[") == 76 \\', "_estate_ws[-7:])}\"")
# P10 header extraction self-assert prose (76-row cut -> 77-row cut + W218)
grab("CUT76", "Extraction self-asserts the 76-row cut", "+ W212 + W213 + W214 + W215 + W216 + W217)")

print("--- protections done: %d regions ---" % len(PROTECT))
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
# PART 3 of derive: protected-region restoration + postchecks + write. Concatenate after p2.

# ---- restore protected regions with programmatic transforms ----
seg = PROTECT["KEPTLIST"]
last = seg[seg.rfind("assert n1_t4.count('    # --- W219 materializer face')"):]
w220line = last.replace("W219", "W220").replace("r920 window", "r923 window")
out = out.replace("@@KEPTLIST@@", seg + "\n" + w220line)

seg = PROTECT["LIVENESS"]
assert '"w219_block_kept": 1}' in seg
out = out.replace("@@LIVENESS@@", seg.replace('"w219_block_kept": 1}', '"w219_block_kept": 1, "w220_block_kept": 1}'))

seg = PROTECT["TRANSITIVE"]
lines = [l for l in seg.split("\n") if '"w215_transitive"' not in l]
w218line = [l for l in lines if '"w218_transitive"' in l][0]
w219line = w218line.replace("w218_transitive", "w219_transitive").replace("n1_w218_results.json", "n1_w219_results.json").replace("903,389 / K=477,520", "905,589 / K=479,720")
idx = lines.index(w218line)
lines.insert(idx, w219line)
new_tr = "\n".join(lines)
if new_tr.endswith(","):
    new_tr = new_tr[:-1]  # the file kept the block's trailing comma after the placeholder
out = out.replace("@@TRANSITIVE@@", new_tr)

seg = PROTECT["PREREGNOTE"]
new_note = ('"note": "prereg derived+committed in the r925 dead window (2e251d084, five-level lineage replay '
            '+ editor_gen fix replay, preflight 46/46; anchor-verification scratch from the r926 zero-commit '
            'dead window absorbed); splice editor derived from the committed W220 editor template by '
            'count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this r927 '
            'absorb window; upstream W220 already landed (clean-precondition tenth consecutive window); '
            'zero transcription"')
out = out.replace("@@PREREGNOTE@@", new_note)

seg = PROTECT["PARITYNOTE"]
out = out.replace("@@PARITYNOTE@@", seg.replace(
    "+ W215 + W216 + W217 legs -> W220 block = 78 rows ending at W219",
    "+ W215 + W216 + W217 + W218 legs -> W221 block = 79 rows ending at W220"))

out = out.replace("@@STRUCTROWS@@",
    "(79 rows: estate 69 + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg).")

out = out.replace("@@PARFULL@@",
    'assert par_full.count("assert pf.N1_BANDS[") == 78, \\\n'
    "    f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 78 (69 estate + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg)\"")

out = out.replace("@@OWNLEGS@@",
    "+ own W211 leg + own W212 leg + own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg + own W218 leg + own W219 leg)")

out = out.replace("@@PARSEC@@",
    'assert par_sec.count("assert pf.N1_BANDS[") == 77 \\\n'
    "    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \\\n"
    "    and [int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76])] == [211, 212, 213, 214, 215, 216, 217, 218], \\\n"
    "    f\"estate segment not W138..W206 full-span 69 rows + W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 legs: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-8:])}\"")

out = out.replace("@@CUT76@@",
    "Extraction self-asserts the 77-row cut (69 estate + W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218)")

# ---- postchecks ----
def want(tag, s, n):
    c = out.count(s)
    ok = (c == n) if isinstance(n, int) else (n[0] <= c <= n[1])
    print(("POST-OK " if ok else "POST-FAIL ") + "[%s] %r count=%d want=%s" % (tag, s[:50], c, n))
    if not ok:
        fails.append("post:" + tag)

want("no-placeholder", "@@", 0)
want("no-EIGHTIETH", "EIGHTIETH", 0)
want("no-w220-probe-residue", "_w220bmc_20261012", 0)
want("EIGHTY-FIRST", "EIGHTY-FIRST", (5, 9))
want("EIGHTY-SECOND", "EIGHTY-SECOND instance anticipated", 2)
want("no-905_589", "905_589", 0)
want("no-479_720", "479_720", 0)
want("907_789", "907_789", 1)
want("481_920", "481_920", 1)
want("907,789", "907,789", 2)
want("receipt-w219-ledger", "905,589 / K=479,720", 1)
want("no-r922", "r922", 0)
want("r920-only-keptlist", "r920", 1)
want("no-w218_leg", "w218_leg", 0)
want("no-w215_transitive", "w215_transitive", 0)
want("w220_leg", "w220_leg", (1, 6))
want("no-W221p", "W221p_", 0)
want("w220-seat-msg-refs", "MSG-20261012-1025", 2)
want("no-fiftieth", "fiftieth", 0)
want("no-TWENTIETH-bare", "TWENTIETH ", 0)
want("221-receipt", "_w221bmc_20261012_probe_receipt.json", 9)
want("221-freeze-receipt", "_w221bmc_freeze_receipt.json", 1)
want("221-prereg", "PERPETUAL_N1_W221_PREREG.md", 5)
want("220-prereg-upstream", "PERPETUAL_N1_W220_PREREG.md", 3)
want("batch221", '"batch": "PERPETUAL-N1-W221"', 4)
want("n1w221", "n1_w221", (4, 6))
want("no-n1_w220", "n1_w220\"", 0)
want("kept220", "'    # --- W220 materializer face') == 1  # prior block kept (W220 splice landed r923 window)", 1)
want("liveness220", '"w220_block_kept": 1', 1)

if fails:
    print("DERIVE FAILED:", fails)
    sys.exit(1)

open(r"results\_w221bmc_freeze_edits.py", "w", encoding="utf-8", newline="").write(out)
import py_compile
py_compile.compile(r"results\_w221bmc_freeze_edits.py", doraise=True)
print("DERIVE OK -- wrote results/_w221bmc_freeze_edits.py (%d bytes, py_compile green)" % len(out))
