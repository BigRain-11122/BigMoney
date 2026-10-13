# -*- coding: utf-8 -*-
"""r959 bm-c: W229 pre-seat probe derive (bloodline = _w228bmc_probe_derive.py
verbatim machinery, W229 facts live-registry-driven; r587 never-transcribe law).
Order: bare 228->229 then 227->228 FIRST (mangling soon-discarded narrative blocks),
then leg4 ordinal EIGHTY-NINTH->NINETIETH, then EIGHTY-EIGHTH->EIGHTY-NINTH x3,
then block swaps (docstring / receipt-probe / leg0 anchor) with FINAL literals,
then explicit numeric pairs with count asserts, residual asserts, py_compile gate."""
import io, re, py_compile

SRC = "results/_w228bmc_20261013_probe.py"
DST = "results/_w229bmc_20261013_probe.py"
t = io.open(SRC, encoding="utf-8").read()

def pair(old, new, expect=1):
    global t
    n = t.count(old)
    assert n == expect, f"pair count {n} != {expect}: {old[:80]!r}"
    t = t.replace(old, new)

# --- 1: bare wave-number passes (228->229 first, then 227->228) -------------------
n228 = t.count("228"); t = t.replace("228", "229")
n227 = t.count("227"); t = t.replace("227", "228")

# --- 2: ordinal chains (leg4-instance pair FIRST: post-swap safety, r955 law) ------
pair("A-hops-prior-B EIGHTY-NINTH instance ",
     "A-hops-prior-B NINETIETH instance ", 1)
pair("EIGHTY-EIGHTH ", "EIGHTY-NINTH ", 3)  # 3rd hit rides in the soon-discarded docstring

# --- 3: docstring swap (coding-header prefix preserved; close-anchor i+3, r955 fix) --
i = t.find('"""'); j = t.find('"""', i + 3) + 3
DOC = '''"""W229 pre-seat probe (bm-c loop window r959 continuation, 2026-10-13 08:5x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law). Upstream face = W228 FULL CYCLE LANDED (r957 seat
4e30ddf69 + r958 prereg e6c8441aa + dead-r959 five-face freeze splice 842f817ad
(estate machine-verified + landed by r959-continuation) + engine self-burn 12/12
batched ledger appends 03bca8089/95e210be1 self-committed + six-gate
PRE-FINALIZE 08:3x correct phase per W217-debt standing law (W212-pattern
zero recurrence, third consecutive correct-phase wave) + finalize one-pass
08:3x: ledger 923,189+2,200=925,389 EXACT, merged pool K=499,520,
results/perpetual_faces/n1_w228_results.json machine-read + five-key ALL PASS
_r959bmc_w228_fivekey_receipt.json + sec.7/8 machine-read backfilled into
PERPETUAL_N1_W228_PREREG.md placeholders=0, closeout 6744db794) -- SINGLE
STATE: W2..W228 ALL REGISTERED, zero in-flight declared seats. This probe IS
the W229 re-derive on the post-W228-REGISTERED universe mandated by the W228
probe leg4 + W228 prereg sec.8 projection (r587: never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W228-REGISTERED
universe (all upstream bands in N1_BANDS live import; no declared-injection
needed -- W209..W228 twenty faces all registered bm-c continuous).
Derivation faces (STAIRCASE GEOMETRY EIGHTY-NINTH instance expected, W141
leg2 law + E36 card; the W228 probe leg4 + W228 prereg sec.8 anticipated
W229+ -- this probe IS that re-derive):
  A  arithmetic continuation from the registered W228 A tail -- expected
     REFUSED at its own start by the registered W228 B band (staircase
     A-hops-prior-B 89th); honest forward walk -> first-clean; A base ==
     prior-wave B tail+1 machine-checkable relation.
  B  arithmetic continuation from the registered W228 B tail -- naive lands
     INSIDE the W229 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base ==
     own-wave A tail+1 machine-checkable relation.
Anchor face: W228 finalize LANDED (ledger head 925,389 = prev 923,189 + 2,200;
merged pool K=499,520 machine-read in leg0; five-key ALL PASS
_r959bmc_w228_fivekey_receipt.json landed by the r959-continuation window).
W229 freeze is GATED on nothing in-flight -- upstream fully landed, clean
chain-order window.
Bloodline: _w228bmc_20261013_probe.py derive machinery verbatim, W229 facts
live-registry-driven; single-state universe (no declared-injection legs)."""'''
t = t[:i] + DOC + t[j:]

# --- 4: receipt probe string ----------------------------------------------------------
NEW_PROBE_STR = ('receipt = {"probe": "W229 pre-seat probe (bm-c loop r959 continuation window, 2026-10-13 08:5x, '
                 'CEO fill-order standing + seat-first law + never-dry supply line; post-W228-REGISTERED '
                 'single-state universe, upstream W228 full cycle landed r957 seat 4e30ddf69/r958 prereg '
                 'e6c8441aa/r959 splice 842f817ad+engine self-burn 03bca8089+95e210be1/six-gate PRE-FINALIZE '
                 '08:3x+finalize 08:3x/fivekey landed by r959-continuation closeout 6744db794)", "legs": {}}')
m = re.search(r'receipt = \{"probe": "[^"]*", "legs": \{\}\}', t)
assert m, "receipt probe string not found"
t = t[:m.start()] + NEW_PROBE_STR + t[m.end():]

# --- 5: leg0 anchor tuple --------------------------------------------------------------
i = t.find('("W228 finalize LANDED')
assert i >= 0, "anchor start not found"
END = 'zero in-flight declared seats")'
j = t.find(END, i) + len(END)
NEW_ANCHOR = ('("W228 finalize LANDED (ledger 925,389 = prev 923,189 + 2,200, "\n'
              '                                     "K=499,520, mu=-0.09272 sigma=0.24508 machine-read; dead-r959-window body "\n'
              '                                     "(prereg+splice+burn) landed by r959-continuation splice commit 842f817ad; six-gate "\n'
              '                                     "PRE-FINALIZE 08:3x correct phase per W217-debt standing law -- W229 burn window = "\n'
              '                                     "PRE-FINALIZE standing law; upstream W2..W228 ALL REGISTERED single state -- W229 "\n'
              '                                     "freeze = clean chain-order window, zero in-flight declared seats")')
t = t[:i] + NEW_ANCHOR + t[j:]

# --- 6: explicit numeric / ordinal pairs (targets = post-bare-pass text) --------------
pair("owner_total == 217 and len(bmc_rows) == 57", "owner_total == 218 and len(bmc_rows) == 58", 1)
pair("(expect 217/57 post-W228-splice per the r956 splice receipt ordinal faces)",
     "(expect 218/58 post-W228-splice per the r959 splice receipt ordinal faces)", 1)
pair('led.get("total") == 923_189 and led.get("prev_total") == 920_989',
     'led.get("total") == 925_389 and led.get("prev_total") == 923_189', 1)
pair("(514_204, 516_203)", "(516_404, 518_403)", 1)
pair("(516_204, 516_403)", "(518_404, 518_603)", 1)
pair('"leg0 failed: W228 row drift (bm-c r956 splice face)"',
     '"leg0 failed: W228 row drift (bm-c r959 splice face)"', 1)
pair("497_320", "499_520", 1)
pair("-> 217th wave, bm-c 58th owned", "-> 218th wave, bm-c 59th owned", 1)
pair('"ordinal": 218,', '"ordinal": 219,', 1)
pair('"bmc_ordinal": 58,', '"bmc_ordinal": 59,', 1)
pair("W228 freeze receipt = 57th owned", "W228 freeze receipt = 58th owned", 1)
pair("(56 live rows + W228 candidate at r956 splice)", "(57 live rows + W228 candidate at r959 splice)", 1)
pair("candidate = 58th per the same continuity", "candidate = 59th per the same continuity", 1)
# NB: receipt filename needs NO explicit pair -- bare pass 228->229 already
# yields _w229bmc_20261013_probe_receipt.json (date 20261013 unchanged, today);
# presence asserted in the need-list below (unlike the W227->W228 derive whose
# source carried the stale 20261012 date).

# --- 7: residual + required asserts ------------------------------------------------------
for bad in ("10781c2f8", "0d0c63c6e", "48c321706", "20720d04f", "dba434a41", "1e5ed3326",
            "W227", "EIGHTY-EIGHTH", "920_989", "497_320", "r956", "06:49:23",
            "06:53:09", "20261012_probe_receipt", "r955 window", "r957 window"):
    assert bad not in t, f"residual face {bad!r} still present"
for need in ("N1_BANDS[228]", "range(16, 229)", "n1_w228_results.json", "925_389", "499_520",
             "_w229bmc_20261013_probe_receipt.json", "EIGHTY-NINTH", "NINETIETH",
             "PERPETUAL-N1-W229", "'229: {\"a\": ('"):
    assert need in t, f"required face {need!r} missing"

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print(f"DERIVE OK: {DST} ({len(t)} bytes; bare228={n228} bare227={n227}; py_compile green)")
