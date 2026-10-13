# -*- coding: utf-8 -*-
"""r962 bm-c: W230 pre-seat probe derive (bloodline = _w229bmc_probe_derive.py
verbatim machinery, W230 facts live-registry-driven; r587 never-transcribe law).
Order: bare 229->230 then 228->229 FIRST (mangling soon-discarded narrative blocks),
then leg4 ordinal NINETIETH->NINETY-FIRST, then EIGHTY-NINTH->NINETIETH x3,
then block swaps (docstring / receipt-probe / leg0 anchor) with FINAL literals,
then explicit numeric pairs with count asserts, residual asserts, py_compile gate."""
import io, re, py_compile

SRC = "results/_w229bmc_20261013_probe.py"
DST = "results/_w230bmc_20261013_probe.py"
t = io.open(SRC, encoding="utf-8").read()

def pair(old, new, expect=1):
    global t
    n = t.count(old)
    assert n == expect, f"pair count {n} != {expect}: {old[:80]!r}"
    t = t.replace(old, new)

# --- 1: bare wave-number passes (229->230 first, then 228->229) -------------------
n229 = t.count("229"); t = t.replace("229", "230")
n228 = t.count("228"); t = t.replace("228", "229")

# --- 2: ordinal chains (leg4-instance pair FIRST: post-swap safety, r955 law) ------
pair("A-hops-prior-B NINETIETH instance ",
     "A-hops-prior-B NINETY-FIRST instance ", 1)
pair("EIGHTY-NINTH ", "NINETIETH ", 3)  # 3rd hit rides in the soon-discarded docstring

# --- 3: docstring swap (coding-header prefix preserved; close-anchor i+3, r955 fix) --
i = t.find('"""'); j = t.find('"""', i + 3) + 3
DOC = '''"""W230 pre-seat probe (bm-c loop window r962 continuation, 2026-10-13 10:2x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law + CEO full-mobilization O-20261013-0930 same-window
receipt). Upstream face = W229 FULL CYCLE LANDED (r959 seat
c9e9e83b8 + r960 prereg e485a0b3f + dead-r961 five-face freeze splice (estate
machine-verified + landed by r962 continuation 2ae8553e6) + engine self-burn 12/12
batched ledger appends e3665b334/b5d62792d self-committed + six-gate
PRE-FINALIZE 10:0x correct phase per W217-debt standing law (W212-pattern
zero recurrence, fourth consecutive correct-phase wave) + finalize one-pass
10:1x: ledger 925,389+2,200=927,589 EXACT, merged pool K=501,720,
results/perpetual_faces/n1_w229_results.json machine-read + five-key ALL PASS
_r962bmc_w229_fivekey_receipt.json + sec.7/8 machine-read backfilled into
PERPETUAL_N1_W229_PREREG.md placeholders=0) -- SINGLE
STATE: W2..W229 ALL REGISTERED, zero in-flight declared seats. This probe IS
the W230 re-derive on the post-W229-REGISTERED universe mandated by the W229
probe leg4 + W229 prereg sec.8 projection (r587: never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W229-REGISTERED
universe (all upstream bands in N1_BANDS live import; no declared-injection
needed -- W209..W229 twenty-one faces all registered bm-c continuous).
Derivation faces (STAIRCASE GEOMETRY NINETIETH instance expected, W141
leg2 law + E36 card; the W229 probe leg4 + W229 prereg sec.8 anticipated
W230+ -- this probe IS that re-derive):
  A  arithmetic continuation from the registered W229 A tail -- expected
     REFUSED at its own start by the registered W229 B band (staircase
     A-hops-prior-B 90th); honest forward walk -> first-clean; A base ==
     prior-wave B tail+1 machine-checkable relation.
  B  arithmetic continuation from the registered W229 B tail -- naive lands
     INSIDE the W230 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base ==
     own-wave A tail+1 machine-checkable relation.
Anchor face: W229 finalize LANDED (ledger head 927,589 = prev 925,389 + 2,200;
merged pool K=501,720 machine-read in leg0; five-key ALL PASS
_r962bmc_w229_fivekey_receipt.json landed by the r962 window).
W230 freeze is GATED on nothing in-flight -- upstream fully landed, clean
chain-order window.
Bloodline: _w229bmc_20261013_probe.py derive machinery verbatim, W230 facts
live-registry-driven; single-state universe (no declared-injection legs)."""'''
t = t[:i] + DOC + t[j:]

# --- 4: receipt probe string ----------------------------------------------------------
NEW_PROBE_STR = ('receipt = {"probe": "W230 pre-seat probe (bm-c loop r962 continuation window, 2026-10-13 10:2x, '
                 'CEO fill-order standing + seat-first law + never-dry supply line + full-mobilization O-20261013-0930 receipt same-window; post-W229-REGISTERED '
                 'single-state universe, upstream W229 full cycle landed r959 seat c9e9e83b8/r960 prereg '
                 'e485a0b3f/dead-r961 splice landed by r962 continuation 2ae8553e6+engine self-burn e3665b334+b5d62792d/six-gate PRE-FINALIZE '
                 '10:0x+finalize 10:1x/fivekey _r962bmc_w229_fivekey_receipt.json)", "legs": {}}')
m = re.search(r'receipt = \{"probe": "[^"]*", "legs": \{\}\}', t)
assert m, "receipt probe string not found"
t = t[:m.start()] + NEW_PROBE_STR + t[m.end():]

# --- 5: leg0 anchor tuple --------------------------------------------------------------
i = t.find('("W229 finalize LANDED')
assert i >= 0, "anchor start not found"
END = 'zero in-flight declared seats")'
j = t.find(END, i) + len(END)
NEW_ANCHOR = ('("W229 finalize LANDED (ledger 927,589 = prev 925,389 + 2,200, "\n'
              '                                     "K=501,720, mu=-0.09270 sigma=0.24508 machine-read; dead-r961-window body "\n'
              '                                     "(prereg r960+splice+burn) landed by r962 continuation splice commit 2ae8553e6; six-gate "\n'
              '                                     "PRE-FINALIZE 10:0x correct phase per W217-debt standing law -- W230 burn window = "\n'
              '                                     "PRE-FINALIZE standing law; upstream W2..W229 ALL REGISTERED single state -- W230 "\n'
              '                                     "freeze = clean chain-order window, zero in-flight declared seats")')
t = t[:i] + NEW_ANCHOR + t[j:]

# --- 6: explicit numeric / ordinal pairs (targets = post-bare-pass text) --------------
pair("owner_total == 218 and len(bmc_rows) == 58", "owner_total == 219 and len(bmc_rows) == 59", 1)
pair("(expect 218/58 post-W229-splice per the r959 splice receipt ordinal faces)",
     "(expect 219/59 post-W229-splice per the r962 splice receipt ordinal faces)", 1)
pair('led.get("total") == 925_389 and led.get("prev_total") == 923_189',
     'led.get("total") == 927_589 and led.get("prev_total") == 925_389', 1)
pair("(516_404, 518_403)", "(518_604, 520_603)", 1)
pair("(518_404, 518_603)", "(520_604, 520_803)", 1)
pair('"leg0 failed: W229 row drift (bm-c r959 splice face)"',
     '"leg0 failed: W229 row drift (bm-c r962 splice face)"', 1)
pair("499_520", "501_720", 1)
pair("-> 218th wave, bm-c 59th owned", "-> 219th wave, bm-c 60th owned", 1)
pair('"ordinal": 219,', '"ordinal": 220,', 1)
pair('"bmc_ordinal": 59,', '"bmc_ordinal": 60,', 1)
pair("W229 freeze receipt = 58th owned", "W229 freeze receipt = 59th owned", 1)
pair("(57 live rows + W229 candidate at r959 splice)", "(58 live rows + W229 candidate at r962 splice)", 1)
pair("candidate = 59th per the same continuity", "candidate = 60th per the same continuity", 1)
# NB: receipt filename needs NO explicit pair -- bare pass 229->230 already
# yields _w230bmc_20261013_probe_receipt.json (date 20261013 unchanged, today);
# presence asserted in the need-list below.

# --- 7: residual + required asserts ------------------------------------------------------
for bad in ("4e30ddf69", "e6c8441aa", "842f817ad", "03bca8089", "95e210be1", "6744db794",
            "W228", "EIGHTY-NINTH", "EIGHTY-EIGHTH", "923_189", "499_520", "r957", "r958",
            "_r959bmc_w229_fivekey_receipt", "20261012_probe_receipt"):
    assert bad not in t, f"residual face {bad!r} still present"
for need in ("N1_BANDS[229]", "range(16, 230)", "n1_w229_results.json", "927_589", "501_720",
             "_w230bmc_20261013_probe_receipt.json", "NINETIETH", "NINETY-FIRST",
             "PERPETUAL-N1-W230", "'230: {\"a\": ('"):
    assert need in t, f"required face {need!r} missing"

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print(f"DERIVE OK: {DST} ({len(t)} bytes; bare229={n229} bare228={n228}; py_compile green)")
