# -*- coding: utf-8 -*-
"""r957 bm-c: W228 pre-seat probe derive (bloodline = _w227bmc_probe_derive.py
verbatim machinery, W228 facts live-registry-driven; r587 never-transcribe law).
Order: bare 227->228 then 226->227 FIRST (mangling soon-discarded narrative blocks),
then leg4 ordinal EIGHTY-EIGHTH->EIGHTY-NINTH, then EIGHTY-SEVENTH->EIGHTY-EIGHTH x3,
then block swaps (docstring / receipt-probe / leg0 anchor) with FINAL literals,
then explicit numeric pairs with count asserts, residual asserts, py_compile gate."""
import io, re, py_compile

SRC = "results/_w227bmc_20261012_probe.py"
DST = "results/_w228bmc_20261013_probe.py"
t = io.open(SRC, encoding="utf-8").read()

def pair(old, new, expect=1):
    global t
    n = t.count(old)
    assert n == expect, f"pair count {n} != {expect}: {old[:80]!r}"
    t = t.replace(old, new)

# --- 1: bare wave-number passes (227->228 first, then 226->227) -------------------
n227 = t.count("227"); t = t.replace("227", "228")
n226 = t.count("226"); t = t.replace("226", "227")

# --- 2: ordinal chains (leg4-instance pair FIRST: post-swap safety, r955 law) ------
pair("A-hops-prior-B EIGHTY-EIGHTH instance ",
     "A-hops-prior-B EIGHTY-NINTH instance ", 1)
pair("EIGHTY-SEVENTH ", "EIGHTY-EIGHTH ", 3)  # 3rd hit rides in the soon-discarded docstring

# --- 3: docstring swap (coding-header prefix preserved; close-anchor i+3, r955 fix) --
i = t.find('"""'); j = t.find('"""', i + 3) + 3
DOC = '''"""W228 pre-seat probe (bm-c loop window r957, 2026-10-13 07:2x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law). Upstream face = W227 FULL CYCLE LANDED (r955 seat
10781c2f8 + dead-r956 prereg 0d0c63c6e + five-face freeze splice 48c321706
(dead window, landed by r956-absorb closeout 1e5ed3326) + engine self-burn 12/12
batched ledger appends 20720d04f/dba434a41 self-committed + six-gate
PRE-FINALIZE 06:49:23 correct phase per W217-debt standing law (W212-pattern
zero recurrence) + finalize one-pass 06:53:09: ledger 920,989+2,200=923,189
EXACT, merged pool K=497,320, results/perpetual_faces/n1_w227_results.json
machine-read + five-key ALL PASS _r956bmc_w227_fivekey_receipt.json +
sec.7/8 machine-read backfilled into PERPETUAL_N1_W227_PREREG.md
placeholders=0) -- SINGLE STATE: W2..W227 ALL REGISTERED, zero in-flight
declared seats. This probe IS the W228 re-derive on the post-W227-REGISTERED
universe mandated by the W227 probe leg4 + W227 seat MSG projection (r587:
never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W227-REGISTERED
universe (all upstream bands in N1_BANDS live import; no declared-injection
needed -- W209..W227 nineteen faces all registered bm-c continuous).
Derivation faces (STAIRCASE GEOMETRY EIGHTY-EIGHTH instance expected, W141
leg2 law + E36 card; the W227 seat MSG leg4 projection anticipated W228+ --
this probe IS that re-derive):
  A  arithmetic continuation from the registered W227 A tail -- expected
     REFUSED at its own start by the registered W227 B band (staircase
     A-hops-prior-B 88th); honest forward walk -> first-clean; A base ==
     prior-wave B tail+1 machine-checkable relation.
  B  arithmetic continuation from the registered W227 B tail -- naive lands
     INSIDE the W228 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base ==
     own-wave A tail+1 machine-checkable relation.
Anchor face: W227 finalize LANDED (ledger head 923,189 = prev 920,989 + 2,200;
merged pool K=497,320 machine-read in leg0; five-key ALL PASS
_r956bmc_w227_fivekey_receipt.json landed by the r956-absorb window). W228
freeze is GATED on nothing in-flight -- upstream fully landed, clean
chain-order window.
Bloodline: _w227bmc_20261012_probe.py derive machinery verbatim, W228 facts
live-registry-driven; single-state universe (no declared-injection legs)."""'''
t = t[:i] + DOC + t[j:]

# --- 4: receipt probe string ----------------------------------------------------------
NEW_PROBE_STR = ('receipt = {"probe": "W228 pre-seat probe (bm-c loop r957 window, 2026-10-13 07:2x, '
                 'CEO fill-order standing + seat-first law + never-dry supply line; post-W227-REGISTERED '
                 'single-state universe, upstream W227 full cycle landed r955 seat 10781c2f8/r956 prereg '
                 '0d0c63c6e/r956 splice 48c321706+engine self-burn 20720d04f+dba434a41/finalize 06:53:09/'
                 'six-gate PRE-FINALIZE 06:49:23 correct-phase+fivekey landed by r956-absorb closeout '
                 '1e5ed3326)", "legs": {}}')
m = re.search(r'receipt = \{"probe": "[^"]*", "legs": \{\}\}', t)
assert m, "receipt probe string not found"
t = t[:m.start()] + NEW_PROBE_STR + t[m.end():]

# --- 5: leg0 anchor tuple --------------------------------------------------------------
i = t.find('("W227 finalize LANDED')
assert i >= 0, "anchor start not found"
END = 'zero in-flight declared seats")'
j = t.find(END, i) + len(END)
NEW_ANCHOR = ('("W227 finalize LANDED (ledger 923,189 = prev 920,989 + 2,200, "\n'
              '                                     "K=497,320, mu=-0.09276 sigma=0.24508 machine-read; dead-r956-window body "\n'
              '                                     "(prereg+splice+burn+finalize) landed by r956-absorb closeout 1e5ed3326; six-gate "\n'
              '                                     "PRE-FINALIZE 06:49:23 correct phase per W217-debt standing law -- W228 burn window = "\n'
              '                                     "PRE-FINALIZE standing law; upstream W2..W227 ALL REGISTERED single state -- W228 "\n'
              '                                     "freeze = clean chain-order window, zero in-flight declared seats")')
t = t[:i] + NEW_ANCHOR + t[j:]

# --- 6: explicit numeric / ordinal pairs ------------------------------------------------
pair("owner_total == 216 and len(bmc_rows) == 56", "owner_total == 217 and len(bmc_rows) == 57", 1)
pair("(expect 216/56 post-W227-splice per the r943 splice receipt ordinal faces)",
     "(expect 217/57 post-W227-splice per the r956 splice receipt ordinal faces)", 1)
pair('led.get("total") == 920_989 and led.get("prev_total") == 918_789',
     'led.get("total") == 923_189 and led.get("prev_total") == 920_989', 1)
pair("(512_004, 514_003)", "(514_204, 516_203)", 1)
pair("(514_004, 514_203)", "(516_204, 516_403)", 1)
pair('"leg0 failed: W227 row drift (bm-c r943 splice face)"',
     '"leg0 failed: W227 row drift (bm-c r956 splice face)"', 1)
pair("495_120", "497_320", 1)
pair("-> 216th wave, bm-c 57th owned", "-> 217th wave, bm-c 58th owned", 1)
pair('"ordinal": 217,', '"ordinal": 218,', 1)
pair('"bmc_ordinal": 57,', '"bmc_ordinal": 58,', 1)
pair("W227 freeze receipt = 56th owned", "W227 freeze receipt = 57th owned", 1)
pair("(55 live rows + W227 candidate at r943 splice)", "(56 live rows + W227 candidate at r956 splice)", 1)
pair("candidate = 57th per the same continuity", "candidate = 58th per the same continuity", 1)
pair("_w228bmc_20261012_probe_receipt.json", "_w228bmc_20261013_probe_receipt.json", 1)

# --- 7: residual + required asserts ------------------------------------------------------
for bad in ("d7d270752", "f65d886cb", "9b44d37d1", "9f41cf5be", "eed45a825", "bd50be730",
            "W226", "EIGHTY-SEVENTH", "216", "495_120", "918_789", "r943 splice",
            "(512_004", "r945 window", "23:4x", "22:41:33", "20261012_probe_receipt"):
    assert bad not in t, f"residual face {bad!r} still present"
for need in ("N1_BANDS[227]", "range(16, 228)", "n1_w227_results.json", "923_189", "497_320",
             "_w228bmc_20261013_probe_receipt.json", "EIGHTY-EIGHTH", "EIGHTY-NINTH",
             "PERPETUAL-N1-W228", "'228: {\"a\": ('"):
    assert need in t, f"required face {need!r} missing"

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print(f"DERIVE OK: {DST} ({len(t)} bytes; bare227={n227} bare226={n226}; py_compile green)")
