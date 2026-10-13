# -*- coding: utf-8 -*-
"""r966 bm-c: W232 pre-seat probe derive (bloodline = _w231bmc_probe_derive.py
verbatim machinery, W232 facts live-registry-driven; r587 never-transcribe law).
Order: bare 231->232 then 230->231 FIRST (mangling soon-discarded narrative blocks),
then leg4 ordinal NINETY-SECOND->NINETY-THIRD, then NINETY-FIRST->NINETY-SECOND x3,
then block swaps (docstring / receipt-probe / leg0 anchor) with FINAL literals,
then explicit numeric pairs with count asserts, residual asserts, py_compile gate.
Census-driven pair set (results/_r966bmc_w232derive_census.py): no dangerous
numeric substrings (523004/525004 absent from file face -- runtime-derived)."""
import io, re, py_compile

SRC = "results/_w231bmc_20261013_probe.py"
DST = "results/_w232bmc_20261013_probe.py"
t = io.open(SRC, encoding="utf-8").read()

def pair(old, new, expect=1):
    global t
    n = t.count(old)
    assert n == expect, f"pair count {n} != {expect}: {old[:80]!r}"
    t = t.replace(old, new)

# --- 1: bare wave-number passes (231->232 first, then 230->231) -------------------
n231 = t.count("231"); t = t.replace("231", "232")
n230 = t.count("230"); t = t.replace("230", "231")

# --- 2: ordinal chains (leg4-instance pair FIRST: post-swap safety, r955 law) ------
pair("A-hops-prior-B NINETY-SECOND instance ",
     "A-hops-prior-B NINETY-THIRD instance ", 1)
pair("NINETY-FIRST ", "NINETY-SECOND ", 3)  # docstring + assert + A_semantics

# --- 3: docstring swap (coding-header prefix preserved; close-anchor i+3, r955 fix) --
i = t.find('"""'); j = t.find('"""', i + 3) + 3
DOC = '''"""W232 pre-seat probe (bm-c loop window r966, 2026-10-13 13:4x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law + never-dry supply line). Upstream face = W231 FULL CYCLE
LANDED (r963 seat 6638ddf9f + dead-r964-window prereg derive aebe0a5ac (FIFTEEN-level
lineage replay 46/46, committed by the dead r964 window itself) + dead-12:5x-window
editor derive absorbed by r966 + r966-window five-face freeze splice executed+landed
aee0bd9fa + engine self-burn 12/12 batched ledger appends 492972ee7/4e373b743
self-committed + six-gate PRE-FINALIZE 13:3x correct phase per W217-debt standing law
(sixth consecutive correct-phase wave, W212-pattern zero recurrence) + finalize
one-pass 13:3x: ledger 929,789+2,200=931,989 EXACT, merged pool K=506,120,
results/perpetual_faces/n1_w231_results.json machine-read + five-key ALL PASS
_r966bmc_w231_fivekey_receipt.json + sec.7/8 machine-read backfilled into
PERPETUAL_N1_W231_PREREG.md placeholders=0) -- SINGLE
STATE: W2..W231 ALL REGISTERED, zero in-flight declared seats. This probe IS
the W232 re-derive on the post-W231-REGISTERED universe mandated by the W231
probe leg4 + W231 prereg sec.8 projection (r587: never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W231-REGISTERED
universe (all upstream bands in N1_BANDS live import; no declared-injection
needed -- W210..W231 twenty-two faces all registered bm-c continuous).
Derivation faces (STAIRCASE GEOMETRY NINETY-SECOND instance expected, W141
leg2 law + E36 card; the W231 probe leg4 + W231 prereg sec.8 anticipated
W232+ -- this probe IS that re-derive):
  A  arithmetic continuation from the registered W231 A tail -- expected
     REFUSED at its own start by the registered W231 B band (staircase
     A-hops-prior-B NINETY-SECOND); honest forward walk -> first-clean; A base ==
     prior-wave B tail+1 machine-checkable relation.
  B  arithmetic continuation from the registered W231 B tail -- naive lands
     INSIDE the W232 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base ==
     own-wave A tail+1 machine-checkable relation.
Anchor face: W231 finalize LANDED (ledger head 931,989 = prev 929,789 + 2,200;
merged pool K=506,120 machine-read in leg0; five-key ALL PASS
_r966bmc_w231_fivekey_receipt.json landed by the r966 window).
W232 freeze is GATED on nothing in-flight -- upstream fully landed, clean
chain-order window.
Bloodline: _w231bmc_20261013_probe.py derive machinery verbatim, W232 facts
live-registry-driven; single-state universe (no declared-injection legs)."""'''
t = t[:i] + DOC + t[j:]

# --- 4: receipt probe string ----------------------------------------------------------
NEW_PROBE_STR = ('receipt = {"probe": "W232 pre-seat probe (bm-c loop r966 window, 2026-10-13 13:4x, '
                 'CEO fill-order standing + seat-first law + never-dry supply line; post-W231-REGISTERED '
                 'single-state universe, upstream W231 full cycle landed r963 seat 6638ddf9f/dead-r964-window prereg '
                 'aebe0a5ac/r966-window splice landed aee0bd9fa+engine self-burn 492972ee7+4e373b743/six-gate PRE-FINALIZE '
                 '13:3x+finalize 13:3x/fivekey _r966bmc_w231_fivekey_receipt.json)", "legs": {}}')
m = re.search(r'receipt = \{"probe": "[^"]*", "legs": \{\}\}', t)
assert m, "receipt probe string not found"
t = t[:m.start()] + NEW_PROBE_STR + t[m.end():]

# --- 5: leg0 anchor tuple --------------------------------------------------------------
i = t.find('("W231 finalize LANDED')
assert i >= 0, "anchor start not found"
END = 'zero in-flight declared seats")'
j = t.find(END, i) + len(END)
NEW_ANCHOR = ('("W231 finalize LANDED (ledger 931,989 = prev 929,789 + 2,200, "\n'
              '                                     "K=506,120, mu=-0.0927 sigma=0.2451 machine-read; r966-window body "\n'
              '                                     "(prereg aebe0a5ac by dead r964 + splice aee0bd9fa by r966 + burn by engine "\n'
              '                                     "self-commits 492972ee7/4e373b743); six-gate PRE-FINALIZE 13:3x correct phase "\n'
              '                                     "per W217-debt standing law -- W232 burn window = PRE-FINALIZE standing law; "\n'
              '                                     "upstream W2..W231 ALL REGISTERED single state -- W232 "\n'
              '                                     "freeze = clean chain-order window, zero in-flight declared seats")')
t = t[:i] + NEW_ANCHOR + t[j:]

# --- 6: explicit numeric / ordinal pairs (targets = post-bare-pass text) --------------
pair("owner_total == 220 and len(bmc_rows) == 60", "owner_total == 221 and len(bmc_rows) == 61", 1)
pair("(expect 220/60 post-W231-splice per the r963 splice receipt ordinal faces)",
     "(expect 221/61 post-W231-splice per the r966 splice receipt ordinal faces)", 1)
pair('led.get("total") == 929_789 and led.get("prev_total") == 927_589',
     'led.get("total") == 931_989 and led.get("prev_total") == 929_789', 1)
pair("(520_804, 522_803)", "(523_004, 525_003)", 1)
pair("(522_804, 523_003)", "(525_004, 525_203)", 1)
pair('"leg0 failed: W231 row drift (bm-c r963 splice face)"',
     '"leg0 failed: W231 row drift (bm-c r966 splice face)"', 1)
pair("503_920", "506_120", 1)
pair("-> 220th wave, bm-c 61st owned", "-> 221st wave, bm-c 62nd owned", 1)
pair('"ordinal": 221,', '"ordinal": 222,', 1)
pair('"bmc_ordinal": 61,', '"bmc_ordinal": 62,', 1)
pair("W231 freeze receipt = 60th owned", "W231 freeze receipt = 61st owned", 1)
pair("(59 live rows + W231 candidate at r963 splice)", "(60 live rows + W231 candidate at r966 splice)", 1)
pair("candidate = 61st per the same continuity", "candidate = 62nd per the same continuity", 1)
# NB: receipt filename needs NO explicit pair -- bare pass 231->232 already
# yields _w232bmc_20261013_probe_receipt.json (date 20261013 unchanged, today);
# presence asserted in the need-list below.

# --- 7: residual + required asserts ------------------------------------------------------
for bad in ("6cfe285e3", "91de0ae83", "24e12fa5e", "0ef11a120", "aec41c57c",
            "W230", "NINETY-FIRST", "927_589", "503_920", "r962",
            "_r963bmc_w231_fivekey_receipt", "20261012_probe_receipt"):
    if bad in t:
        k = t.find(bad)
        raise AssertionError(f"residual face {bad!r} still present near: {t[max(0,k-120):k+120]!r}")
# r963: exactly TWO legit historical faces remain (new-DOC + receipt-str
# "r963 seat 6638ddf9f" = the W231 seat publication window, upstream lineage
# fact) -- all stale prose-leg mentions were fixed by the explicit pairs;
# anything beyond the two historical seat faces = unhandled stale reference.
n_r963 = t.count("r963")
assert n_r963 == 2, f"r963 count {n_r963} != 2 (expected DOC + receipt-str historical seat faces): " + \
    "; ".join(repr(t[max(0, k - 60):k + 60]) for k in
              [m for m in range(len(t)) if t.startswith("r963", m)])
for need in ("N1_BANDS[231]", "range(16, 232)", "n1_w231_results.json", "931_989", "506_120",
             "_w232bmc_20261013_probe_receipt.json", "NINETY-SECOND", "NINETY-THIRD",
             "PERPETUAL-N1-W232", "'232: {\"a\": ('", "_r966bmc_w231_fivekey_receipt"):
    assert need in t, f"required face {need!r} missing"

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print(f"DERIVE OK: {DST} ({len(t)} bytes; bare231={n231} bare230={n230}; py_compile green)")
