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
