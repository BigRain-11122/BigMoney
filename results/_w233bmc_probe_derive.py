# -*- coding: utf-8 -*-
"""r968 bm-c: W233 pre-seat probe derive (bloodline = _w232bmc_probe_derive.py
verbatim machinery, W233 facts live-registry-driven; r587 never-transcribe law;
E63 law: pair targets are CENSUS-verified post-bare-pass faces, zero hand-guess).
Census evidence = results/_r968bmc_w233derive_census.py (this window):
231=59 / 232=47 / 230=0 / r966=14 (all inside wholesale-swap blocks) / r963=2
(DOC+receipt historical seat faces) / NINETY-SECOND=4 (DOC x1 + body x3) /
NINETY-THIRD=1 (leg4) / fivekey-receipt x3 (DOC+anchor+receipt-str) /
931_989=1 / 929_789=1 / 506_120=1 / band-tuples x1 each / 20261012=0.
Order: bare 232->233 then 231->232 FIRST (mangling soon-discarded narrative
blocks), then leg4 ordinal NINETY-THIRD->NINETY-FOURTH, then NINETY-SECOND->
NINETY-THIRD x3, then block swaps (docstring / receipt-probe / leg0 anchor)
with FINAL literals, then explicit numeric pairs with count asserts, residual
asserts, py_compile gate."""
import io, re, py_compile

SRC = "results/_w232bmc_20261013_probe.py"
DST = "results/_w233bmc_20261013_probe.py"
t = io.open(SRC, encoding="utf-8").read()

def pair(old, new, expect=1):
    global t
    n = t.count(old)
    assert n == expect, f"pair count {n} != {expect}: {old[:80]!r}"
    t = t.replace(old, new)

# --- 1: bare wave-number passes (232->233 first, then 231->232) -------------------
n232 = t.count("232"); t = t.replace("232", "233")
n231 = t.count("231"); t = t.replace("231", "232")

# --- 2: ordinal chains (leg4-instance pair FIRST: post-swap safety, r955 law) ------
pair("A-hops-prior-B NINETY-THIRD instance ",
     "A-hops-prior-B NINETY-FOURTH instance ", 1)
pair("NINETY-SECOND ", "NINETY-THIRD ", 3)  # body faces (DOC copy discarded by swap below)

# --- 3: docstring swap (coding-header prefix preserved; close-anchor i+3, r955 fix) --
i = t.find('"""'); j = t.find('"""', i + 3) + 3
DOC = '''"""W233 pre-seat probe (bm-c loop window r968, 2026-10-13 15:3x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law + never-dry supply line). Upstream face = W232 FULL CYCLE
LANDED (r966 seat 8d3a1b78a + r967-window prereg derive a3a7aa632 (SIXTEEN-level
lineage replay 46/46, committed by r967 itself) + dead-r968-window editor derive
(_w232bmc_derive_editor.py E63-healed at runtime by the r968 window: hand-transcribed
ASM face carried a spurious '+ EOL' -> anchored index extraction, 3rd instance) +
r968-window five-face freeze splice executed+landed e58dbcda3 + engine self-burn 12/12
batched ledger appends 5c90051e0/776b15270 self-committed + six-gate PRE-FINALIZE
15:1x correct phase per W217-debt standing law (seventh consecutive correct-phase
wave, W212-pattern zero recurrence) + finalize one-pass 15:2x: ledger
931,989+2,200=934,189 EXACT, merged pool K=508,320,
results/perpetual_faces/n1_w232_results.json machine-read + five-key ALL PASS
_r968bmc_w232_fivekey_receipt.json + sec.7/8 machine-read backfilled into
PERPETUAL_N1_W232_PREREG.md placeholders=0) -- SINGLE
STATE: W2..W232 ALL REGISTERED, zero in-flight declared seats. This probe IS
the W233 re-derive on the post-W232-REGISTERED universe mandated by the W232
probe leg4 + W232 prereg sec.8 projection (r587: never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W232-REGISTERED
universe (all upstream bands in N1_BANDS live import; no declared-injection
needed -- W210..W232 twenty-three faces all registered bm-c continuous).
Derivation faces (STAIRCASE GEOMETRY NINETY-THIRD instance expected, W141
leg2 law + E36 card; the W232 probe leg4 + W232 prereg sec.8 anticipated
W233+ -- this probe IS that re-derive):
  A  arithmetic continuation from the registered W232 A tail -- expected
     REFUSED at its own start by the registered W232 B band (staircase
     A-hops-prior-B NINETY-THIRD); honest forward walk -> first-clean; A base ==
     prior-wave B tail+1 machine-checkable relation.
  B  arithmetic continuation from the registered W232 B tail -- naive lands
     INSIDE the W233 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base ==
     own-wave A tail+1 machine-checkable relation.
Anchor face: W232 finalize LANDED (ledger head 934,189 = prev 931,989 + 2,200;
merged pool K=508,320 machine-read in leg0; five-key ALL PASS
_r968bmc_w232_fivekey_receipt.json landed by the r968 window).
W233 freeze is GATED on nothing in-flight -- upstream fully landed, clean
chain-order window.
Bloodline: _w232bmc_20261013_probe.py derive machinery verbatim, W233 facts
live-registry-driven; single-state universe (no declared-injection legs)."""'''
t = t[:i] + DOC + t[j:]

# --- 4: receipt probe string ----------------------------------------------------------
NEW_PROBE_STR = ('receipt = {"probe": "W233 pre-seat probe (bm-c loop r968 window, 2026-10-13 15:3x, '
                 'CEO fill-order standing + seat-first law + never-dry supply line; post-W232-REGISTERED '
                 'single-state universe, upstream W232 full cycle landed r966 seat 8d3a1b78a/r967-window prereg '
                 'a3a7aa632/r968-window splice landed e58dbcda3+engine self-burn 5c90051e0+776b15270/six-gate PRE-FINALIZE '
                 '15:1x+finalize 15:2x/fivekey _r968bmc_w232_fivekey_receipt.json)", "legs": {}}')
m = re.search(r'receipt = \{"probe": "[^"]*", "legs": \{\}\}', t)
assert m, "receipt probe string not found"
t = t[:m.start()] + NEW_PROBE_STR + t[m.end():]

# --- 5: leg0 anchor tuple --------------------------------------------------------------
i = t.find('("W232 finalize LANDED')
assert i >= 0, "anchor start not found"
END = 'zero in-flight declared seats")'
j = t.find(END, i) + len(END)
NEW_ANCHOR = ('("W232 finalize LANDED (ledger 934,189 = prev 931,989 + 2,200, "\n'
              '                                     "K=508,320, mu=-0.0927 sigma=0.2451 machine-read; r968-window body "\n'
              '                                     "(prereg a3a7aa632 by r967 + splice e58dbcda3 by r968 + burn by engine "\n'
              '                                     "self-commits 5c90051e0/776b15270); six-gate PRE-FINALIZE 15:1x correct phase "\n'
              '                                     "per W217-debt standing law -- W233 burn window = PRE-FINALIZE standing law; "\n'
              '                                     "upstream W2..W232 ALL REGISTERED single state -- W233 "\n'
              '                                     "freeze = clean chain-order window, zero in-flight declared seats")')
t = t[:i] + NEW_ANCHOR + t[j:]

# --- 6: explicit numeric / ordinal pairs (targets = post-bare-pass text) --------------
pair("owner_total == 221 and len(bmc_rows) == 61", "owner_total == 222 and len(bmc_rows) == 62", 1)
pair("(expect 221/61 post-W232-splice per the r966 splice receipt ordinal faces)",
     "(expect 222/62 post-W232-splice per the r968 splice receipt ordinal faces)", 1)
pair('led.get("total") == 931_989 and led.get("prev_total") == 929_789',
     'led.get("total") == 934_189 and led.get("prev_total") == 931_989', 1)
pair("(523_004, 525_003)", "(525_204, 527_203)", 1)
pair("(525_004, 525_203)", "(527_204, 527_403)", 1)
pair('"leg0 failed: W232 row drift (bm-c r966 splice face)"',
     '"leg0 failed: W232 row drift (bm-c r968 splice face)"', 1)
pair("506_120", "508_320", 1)
pair("-> 221st wave, bm-c 62nd owned", "-> 222nd wave, bm-c 63rd owned", 1)
pair('"ordinal": 222,', '"ordinal": 223,', 1)
pair('"bmc_ordinal": 62,', '"bmc_ordinal": 63,', 1)
pair("W232 freeze receipt = 61st owned", "W232 freeze receipt = 62nd owned", 1)
pair("(60 live rows + W232 candidate at r966 splice)", "(61 live rows + W232 candidate at r968 splice)", 1)
pair("candidate = 62nd per the same continuity", "candidate = 63rd per the same continuity", 1)
# NB: receipt filename needs NO explicit pair -- bare pass 232->233 already
# yields _w233bmc_20261013_probe_receipt.json (date 20261013 unchanged, today);
# presence asserted in the need-list below.

# --- 7: residual + required asserts ------------------------------------------------------
for bad in ("6638ddf9f", "aebe0a5ac", "aee0bd9fa", "492972ee7", "4e373b743",
            "r963", "r964", "r965", "W231 finalize", "NINETY-SECOND", "929_789",
            "506_120", "_r966bmc_w232_fivekey_receipt", "20261012_probe_receipt"):
    if bad in t:
        k = t.find(bad)
        raise AssertionError(f"residual face {bad!r} still present near: {t[max(0,k-120):k+120]!r}")
# r966: exactly TWO legit historical faces remain (new-DOC + receipt-str
# "r966 seat 8d3a1b78a" = the W232 seat publication window, upstream lineage
# fact) -- all stale prose-leg mentions were fixed by the block swaps + pairs;
# anything beyond the two historical seat faces = unhandled stale reference.
n_r966 = t.count("r966")
assert n_r966 == 2, f"r966 count {n_r966} != 2 (expected DOC + receipt-str historical seat faces): " + \
    "; ".join(repr(t[max(0, k - 60):k + 60]) for k in
              [m for m in range(len(t)) if t.startswith("r966", m)])
for need in ("N1_BANDS[232]", "range(16, 233)", "n1_w232_results.json", "934_189", "508_320",
             "_w233bmc_20261013_probe_receipt.json", "NINETY-THIRD", "NINETY-FOURTH",
             "PERPETUAL-N1-W233", "'233: {\"a\": ('", "(525_204, 527_203)",
             "(527_204, 527_403)", "_r968bmc_w232_fivekey_receipt"):
    assert need in t, f"required face {need!r} missing"

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print(f"DERIVE OK: {DST} ({len(t)} bytes; bare232={n232} bare231={n231}; py_compile green)")
