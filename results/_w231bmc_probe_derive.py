# -*- coding: utf-8 -*-
"""r963 bm-c: W231 pre-seat probe derive (bloodline = _w230bmc_probe_derive.py
verbatim machinery, W231 facts live-registry-driven; r587 never-transcribe law).
Order: bare 230->231 then 229->230 FIRST (mangling soon-discarded narrative blocks),
then leg4 ordinal NINETY-FIRST->NINETY-SECOND, then NINETIETH->NINETY-FIRST x3,
then block swaps (docstring / receipt-probe / leg0 anchor) with FINAL literals,
then explicit numeric pairs with count asserts, residual asserts, py_compile gate."""
import io, re, py_compile

SRC = "results/_w230bmc_20261013_probe.py"
DST = "results/_w231bmc_20261013_probe.py"
t = io.open(SRC, encoding="utf-8").read()

def pair(old, new, expect=1):
    global t
    n = t.count(old)
    assert n == expect, f"pair count {n} != {expect}: {old[:80]!r}"
    t = t.replace(old, new)

# --- 1: bare wave-number passes (230->231 first, then 229->230) -------------------
n230 = t.count("230"); t = t.replace("230", "231")
n229 = t.count("229"); t = t.replace("229", "230")

# --- 2: ordinal chains (leg4-instance pair FIRST: post-swap safety, r955 law) ------
pair("A-hops-prior-B NINETY-FIRST instance ",
     "A-hops-prior-B NINETY-SECOND instance ", 1)
pair("NINETIETH ", "NINETY-FIRST ", 3)  # docstring + assert + A_semantics

# --- 3: docstring swap (coding-header prefix preserved; close-anchor i+3, r955 fix) --
i = t.find('"""'); j = t.find('"""', i + 3) + 3
DOC = '''"""W231 pre-seat probe (bm-c loop window r963 continuation, 2026-10-13 11:5x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law + never-dry supply line). Upstream face = W230 FULL CYCLE
LANDED (r962 seat 6cfe285e3 + r963-window prereg derive 91de0ae83 (fourteen-level
lineage replay 46/46, committed by the dead r963 window itself) + dead-r963
five-face freeze splice (estate machine-verified + landed by r963 continuation
24e12fa5e) + engine self-burn 12/12 batched ledger appends 0ef11a120/aec41c57c
self-committed + six-gate PRE-FINALIZE 11:5x correct phase per W217-debt standing law
(fifth consecutive correct-phase wave, W212-pattern zero recurrence) + finalize
one-pass 11:5x: ledger 927,589+2,200=929,789 EXACT, merged pool K=503,920,
results/perpetual_faces/n1_w230_results.json machine-read + five-key ALL PASS
_r963bmc_w230_fivekey_receipt.json + sec.7/8 machine-read backfilled into
PERPETUAL_N1_W230_PREREG.md placeholders=0) -- SINGLE
STATE: W2..W230 ALL REGISTERED, zero in-flight declared seats. This probe IS
the W231 re-derive on the post-W230-REGISTERED universe mandated by the W230
probe leg4 + W230 prereg sec.8 projection (r587: never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W230-REGISTERED
universe (all upstream bands in N1_BANDS live import; no declared-injection
needed -- W209..W230 twenty-two faces all registered bm-c continuous).
Derivation faces (STAIRCASE GEOMETRY NINETY-FIRST instance expected, W141
leg2 law + E36 card; the W230 probe leg4 + W230 prereg sec.8 anticipated
W231+ -- this probe IS that re-derive):
  A  arithmetic continuation from the registered W230 A tail -- expected
     REFUSED at its own start by the registered W230 B band (staircase
     A-hops-prior-B 91st); honest forward walk -> first-clean; A base ==
     prior-wave B tail+1 machine-checkable relation.
  B  arithmetic continuation from the registered W230 B tail -- naive lands
     INSIDE the W231 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base ==
     own-wave A tail+1 machine-checkable relation.
Anchor face: W230 finalize LANDED (ledger head 929,789 = prev 927,589 + 2,200;
merged pool K=503,920 machine-read in leg0; five-key ALL PASS
_r963bmc_w230_fivekey_receipt.json landed by the r963 window).
W231 freeze is GATED on nothing in-flight -- upstream fully landed, clean
chain-order window.
Bloodline: _w230bmc_20261013_probe.py derive machinery verbatim, W231 facts
live-registry-driven; single-state universe (no declared-injection legs)."""'''
t = t[:i] + DOC + t[j:]

# --- 4: receipt probe string ----------------------------------------------------------
NEW_PROBE_STR = ('receipt = {"probe": "W231 pre-seat probe (bm-c loop r963 continuation window, 2026-10-13 11:5x, '
                 'CEO fill-order standing + seat-first law + never-dry supply line; post-W230-REGISTERED '
                 'single-state universe, upstream W230 full cycle landed r962 seat 6cfe285e3/r963-window prereg '
                 '91de0ae83/dead-r963 splice landed by r963 continuation 24e12fa5e+engine self-burn 0ef11a120+aec41c57c/six-gate PRE-FINALIZE '
                 '11:5x+finalize 11:5x/fivekey _r963bmc_w230_fivekey_receipt.json)", "legs": {}}')
m = re.search(r'receipt = \{"probe": "[^"]*", "legs": \{\}\}', t)
assert m, "receipt probe string not found"
t = t[:m.start()] + NEW_PROBE_STR + t[m.end():]

# --- 5: leg0 anchor tuple --------------------------------------------------------------
i = t.find('("W230 finalize LANDED')
assert i >= 0, "anchor start not found"
END = 'zero in-flight declared seats")'
j = t.find(END, i) + len(END)
NEW_ANCHOR = ('("W230 finalize LANDED (ledger 929,789 = prev 927,589 + 2,200, "\n'
              '                                     "K=503,920, mu=-0.09269 sigma=0.24505 machine-read; dead-r963-window body "\n'
              '                                     "(prereg+splice+burn) landed by r963 continuation splice commit 24e12fa5e; six-gate "\n'
              '                                     "PRE-FINALIZE 11:5x correct phase per W217-debt standing law -- W231 burn window = "\n'
              '                                     "PRE-FINALIZE standing law; upstream W2..W230 ALL REGISTERED single state -- W231 "\n'
              '                                     "freeze = clean chain-order window, zero in-flight declared seats")')
t = t[:i] + NEW_ANCHOR + t[j:]

# --- 6: explicit numeric / ordinal pairs (targets = post-bare-pass text) --------------
pair("owner_total == 219 and len(bmc_rows) == 59", "owner_total == 220 and len(bmc_rows) == 60", 1)
pair("(expect 219/59 post-W230-splice per the r962 splice receipt ordinal faces)",
     "(expect 220/60 post-W230-splice per the r963 splice receipt ordinal faces)", 1)
pair('led.get("total") == 927_589 and led.get("prev_total") == 925_389',
     'led.get("total") == 929_789 and led.get("prev_total") == 927_589', 1)
pair("(518_604, 520_603)", "(520_804, 522_803)", 1)
pair("(520_604, 520_803)", "(522_804, 523_003)", 1)
pair('"leg0 failed: W230 row drift (bm-c r962 splice face)"',
     '"leg0 failed: W230 row drift (bm-c r963 splice face)"', 1)
pair("501_720", "503_920", 1)
pair("-> 219th wave, bm-c 60th owned", "-> 220th wave, bm-c 61st owned", 1)
pair('"ordinal": 220,', '"ordinal": 221,', 1)
pair('"bmc_ordinal": 60,', '"bmc_ordinal": 61,', 1)
pair("W230 freeze receipt = 59th owned", "W230 freeze receipt = 60th owned", 1)
pair("(58 live rows + W230 candidate at r962 splice)", "(59 live rows + W230 candidate at r963 splice)", 1)
pair("candidate = 60th per the same continuity", "candidate = 61st per the same continuity", 1)
# NB: receipt filename needs NO explicit pair -- bare pass 230->231 already
# yields _w231bmc_20261013_probe_receipt.json (date 20261013 unchanged, today);
# presence asserted in the need-list below.

# --- 7: residual + required asserts ------------------------------------------------------
for bad in ("c9e9e83b8", "e485a0b3f", "2ae8553e6", "e3665b334", "b5d62792d",
            "W228", "NINETIETH", "925_389", "501_720", "r959", "r960",
            "_r962bmc_w230_fivekey_receipt", "20261012_probe_receipt"):
    assert bad not in t, f"residual face {bad!r} still present"
for need in ("N1_BANDS[230]", "range(16, 231)", "n1_w230_results.json", "929_789", "503_920",
             "_w231bmc_20261013_probe_receipt.json", "NINETY-FIRST", "NINETY-SECOND",
             "PERPETUAL-N1-W231", "'231: {\"a\": ('"):
    assert need in t, f"required face {need!r} missing"

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print(f"DERIVE OK: {DST} ({len(t)} bytes; bare230={n230} bare229={n229}; py_compile green)")
