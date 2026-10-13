# -*- coding: utf-8 -*-
"""r974 bm-c: W234 pre-seat probe derive (bloodline = _w233bmc_probe_derive.py
verbatim machinery, W234 facts live-registry-driven; r587 never-transcribe law;
E63 law: pair targets are CENSUS-verified post-bare-pass faces, zero hand-guess).
Census evidence = results/_r974bmc_w234_census.py (this window):
233=47 / 232=60 / 231=0 / r966=2 / r967=4 / r968=15 / 8d3a1b78a=2 /
a3a7aa632=3 / e58dbcda3=3 / 5c90051e0=3 / 776b15270=3 / 931_989=1 /
508_320=1 / 934_189=1 / _r968bmc_w232_fivekey_receipt=3 / NINETY-THIRD=4 /
NINETY-FOURTH=1 / ordinal-223=1 / 62nd=1 / 63rd-owned=1 / 222nd-wave=1 /
range(16, 233)=1 / N1_BANDS[232]=3 / fc223_a=6 (legacy frozen) / h222a=3
(legacy frozen) / inside223=3 (legacy frozen).
Order: bare 233->234 then 232->233 FIRST, then leg4-instance ordinal
NINETY-FOURTH->NINETY-FIFTH, then NINETY-THIRD->NINETY-FOURTH x4, then block
swaps (docstring / receipt-probe / leg0 anchor) with FINAL literals, then
explicit numeric pairs with count asserts, residual asserts, py_compile gate."""
import io, re, py_compile

SRC = "results/_w233bmc_20261013_probe.py"
DST = "results/_w234bmc_20261013_probe.py"
t = io.open(SRC, encoding="utf-8").read()

def pair(old, new, expect=1):
    global t
    n = t.count(old)
    assert n == expect, f"pair count {n} != {expect}: {old[:80]!r}"
    t = t.replace(old, new)

# --- 1: bare wave-number passes (233->234 first, then 232->233) -------------------
n233 = t.count("233"); t = t.replace("233", "234")
n232 = t.count("232"); t = t.replace("232", "233")

# --- 2: ordinal chains (leg4-instance pair FIRST: post-swap safety, r955 law) ------
pair("A-hops-prior-B NINETY-FOURTH instance ",
     "A-hops-prior-B NINETY-FIFTH instance ", 1)
pair("NINETY-THIRD ", "NINETY-FOURTH ", 3)  # trailing-space faces: DOC x1 + body x2 (the DOC "NINETY-THIRD)" paren face + rest of old DOC removed wholesale by the swap below)

# --- 3: docstring swap (coding-header prefix preserved; close-anchor i+3, r955 fix) --
i = t.find('"""'); j = t.find('"""', i + 3) + 3
DOC = '''"""W234 pre-seat probe (bm-c loop window r974, 2026-10-13 19:5x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law + never-dry supply line). Upstream face = W233 FULL CYCLE
LANDED (r968-window seat dd38a9da8 + dead-r972-window prereg derive 933e3ceea
(R33 authored + subgen m30 + 17-level lineage replay 46/46 + phase-B S-table
3 mis-aged pairs fixed, committed by the dead window itself) + dead-r973-window
census-first editor derive 8-round + five-face freeze splice landed 0ca920362 +
engine self-burn 12/12 batched ledger appends 6c1587483/d4cce3ffe self-committed +
r974-window six-gate PRE-FINALIZE 19:4x correct phase per W217-debt standing law
(eighth consecutive correct-phase wave, W212-pattern zero recurrence) + finalize
one-pass 19:5x: ledger 934,189+2,200=936,389 EXACT, merged pool K=510,520,
results/perpetual_faces/n1_w233_results.json machine-read + five-key ALL PASS
_r974bmc_w233_fivekey_receipt.json + sec.7/8 machine-read backfilled into
PERPETUAL_N1_W233_PREREG.md placeholders=0) -- SINGLE
STATE: W2..W233 ALL REGISTERED, zero in-flight declared seats. This probe IS
the W234 re-derive on the post-W233-REGISTERED universe mandated by the W233
probe leg4 + W233 prereg sec.8 projection (r587: never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W233-REGISTERED
universe (all upstream bands in N1_BANDS live import; no declared-injection
needed -- W210..W233 twenty-four faces all registered bm-c continuous).
Derivation faces (STAIRCASE GEOMETRY NINETY-FOURTH instance expected, W141
leg2 law + E36 card; the W233 probe leg4 + W233 prereg sec.8 anticipated
W234+ -- this probe IS that re-derive):
  A  arithmetic continuation from the registered W233 A tail -- expected
     REFUSED at its own start by the registered W233 B band (staircase
     A-hops-prior-B NINETY-FOURTH); honest forward walk -> first-clean; A base ==
     prior-wave B tail+1 machine-checkable relation.
  B  arithmetic continuation from the registered W233 B tail -- naive lands
     INSIDE the W234 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base ==
     own-wave A tail+1 machine-checkable relation.
Anchor face: W233 finalize LANDED (ledger head 936,389 = prev 934,189 + 2,200;
merged pool K=510,520 machine-read in leg0; five-key ALL PASS
_r974bmc_w233_fivekey_receipt.json landed by the r974 window).
W234 freeze is GATED on nothing in-flight -- upstream fully landed, clean
chain-order window.
Bloodline: _w233bmc_20261013_probe.py derive machinery verbatim, W234 facts
live-registry-driven; single-state universe (no declared-injection legs)."""'''
t = t[:i] + DOC + t[j:]

# --- 4: receipt probe string ----------------------------------------------------------
NEW_PROBE_STR = ('receipt = {"probe": "W234 pre-seat probe (bm-c loop r974 window, 2026-10-13 19:5x, '
                 'CEO fill-order standing + seat-first law + never-dry supply line; post-W233-REGISTERED '
                 'single-state universe, upstream W233 full cycle landed r968-window seat dd38a9da8/dead-r972-window prereg '
                 '933e3ceea/dead-r973-window splice landed 0ca920362+engine self-burn 6c1587483+d4cce3ffe/six-gate PRE-FINALIZE '
                 '19:4x+finalize 19:5x/fivekey _r974bmc_w233_fivekey_receipt.json)", "legs": {}}')
m = re.search(r'receipt = \{"probe": "[^"]*", "legs": \{\}\}', t)
assert m, "receipt probe string not found"
t = t[:m.start()] + NEW_PROBE_STR + t[m.end():]

# --- 5: leg0 anchor tuple --------------------------------------------------------------
i = t.find('("W233 finalize LANDED')
assert i >= 0, "anchor start not found"
END = 'zero in-flight declared seats")'
j = t.find(END, i) + len(END)
NEW_ANCHOR = ('("W233 finalize LANDED (ledger 936,389 = prev 934,189 + 2,200, "\n'
              '                                     "K=510,520, mu=-0.0928 sigma=0.2451 machine-read; dead-window body "\n'
              '                                     "(prereg 933e3ceea by dead r972 + splice 0ca920362 by dead r973 + burn by engine "\n'
              '                                     "self-commits 6c1587483/d4cce3ffe); six-gate PRE-FINALIZE 19:4x correct phase "\n'
              '                                     "per W217-debt standing law -- W234 burn window = PRE-FINALIZE standing law; "\n'
              '                                     "upstream W2..W233 ALL REGISTERED single state -- W234 "\n'
              '                                     "freeze = clean chain-order window, zero in-flight declared seats")')
t = t[:i] + NEW_ANCHOR + t[j:]

# --- 6: explicit numeric / ordinal pairs (targets = post-bare-pass text) --------------
pair("owner_total == 222 and len(bmc_rows) == 62", "owner_total == 223 and len(bmc_rows) == 63", 1)
pair("(expect 222/62 post-W233-splice per the r968 splice receipt ordinal faces)",
     "(expect 223/63 post-W233-splice per the r973 splice receipt ordinal faces)", 1)
pair('led.get("total") == 934_189 and led.get("prev_total") == 931_989',
     'led.get("total") == 936_389 and led.get("prev_total") == 934_189', 1)
pair("(525_204, 527_203)", "(527_404, 529_403)", 1)
pair("(527_204, 527_403)", "(529_404, 529_603)", 1)
pair('"leg0 failed: W233 row drift (bm-c r968 splice face)"',
     '"leg0 failed: W233 row drift (bm-c r973 splice face)"', 1)
pair("508_320", "510_520", 1)
pair("-> 222nd wave, bm-c 63rd owned", "-> 223rd wave, bm-c 64th owned", 1)
pair('"ordinal": 223, "bmc_ordinal": 63,', '"ordinal": 224, "bmc_ordinal": 64,', 1)
pair("W233 freeze receipt = 62nd owned", "W233 freeze receipt = 63rd owned", 1)
pair("(61 live rows + W233 candidate at r968 splice)", "(62 live rows + W233 candidate at r973 splice)", 1)
pair("candidate = 63rd per the same continuity", "candidate = 64th per the same continuity", 1)
# NB: receipt filename needs NO explicit pair -- bare pass 233->234 already
# yields _w234bmc_20261013_probe_receipt.json (date 20261013 unchanged, today);
# presence asserted in the need-list below.

# --- 7: residual + required asserts ------------------------------------------------------
for bad in ("8d3a1b78a", "a3a7aa632", "e58dbcda3", "5c90051e0", "776b15270",
            "r966", "r967", "931_989", "508_320", "_r968bmc", "NINETY-THIRD",
            "934_189 and led", "20261012_probe_receipt"):
    if bad in t:
        k = t.find(bad)
        raise AssertionError(f"residual face {bad!r} still present near: {t[max(0,k-120):k+120]!r}")
# r968: exactly TWO legit historical faces remain (new-DOC + receipt-str
# "r968-window seat dd38a9da8" = the W233 seat publication window, upstream
# lineage fact) -- all stale prose-leg mentions were fixed by the block swaps
# + pairs; anything beyond the two historical seat faces = unhandled stale ref.
n_r968 = t.count("r968")
assert n_r968 == 2, f"r968 count {n_r968} != 2 (expected DOC + receipt-str historical seat faces): " + \
    "; ".join(repr(t[max(0, k - 60):k + 60]) for k in
              [m for m in range(len(t)) if t.startswith("r968", m)])
for need in ("N1_BANDS[233]", "range(16, 234)", "n1_w233_results.json", "936_389", "510_520",
             "_w234bmc_20261013_probe_receipt.json", "NINETY-FOURTH", "NINETY-FIFTH",
             "PERPETUAL-N1-W234", "'234: {\"a\": ('", "(527_404, 529_403)",
             "(529_404, 529_603)", "_r974bmc_w233_fivekey_receipt", "933e3ceea",
             "0ca920362", "dd38a9da8", "6c1587483", "d4cce3ffe"):
    assert need in t, f"required face {need!r} missing"

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print(f"DERIVE OK: {DST} ({len(t)} bytes; bare233={n233} bare232={n232}; py_compile green)")
