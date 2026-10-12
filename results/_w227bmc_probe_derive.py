# -*- coding: utf-8 -*-
"""r945 bm-c: W227 pre-seat probe derive (bloodline = _w226bmc_20261012_probe.py
verbatim machinery, W227 facts live-registry-driven; r587 never-transcribe law).
Order: bare 226->227 then 225->226 FIRST (mangling soon-discarded narrative blocks),
then leg4 ordinal SEVENTH->EIGHTH, then EIGHTY-SIXTH->EIGHTY-SEVENTH x2,
then block swaps (docstring / receipt-probe / leg0 anchor) with FINAL literals,
then explicit numeric pairs with count asserts, residual asserts, py_compile gate."""
import io, re, py_compile

SRC = "results/_w226bmc_20261012_probe.py"
DST = "results/_w227bmc_20261012_probe.py"
t = io.open(SRC, encoding="utf-8").read()

def pair(old, new, expect=1):
    global t
    n = t.count(old)
    assert n == expect, f"pair count {n} != {expect}: {old[:80]!r}"
    t = t.replace(old, new)

# --- 1: bare wave-number passes (226->227 first, then 225->226) -------------------
n226 = t.count("226"); t = t.replace("226", "227")
n225 = t.count("225"); t = t.replace("225", "226")

# --- 2: ordinal chains -------------------------------------------------------------
pair("A-hops-prior-B EIGHTY-SEVENTH instance ",
     "A-hops-prior-B EIGHTY-EIGHTH instance ", 1)
pair("EIGHTY-SIXTH ", "EIGHTY-SEVENTH ", 3)  # 3rd hit rides in the soon-discarded docstring

# --- 3: docstring swap ---------------------------------------------------------------
# r955 fix: W226 template carries a coding-header line before its docstring
# (generation shape change) -- closing-quote search must anchor AFTER the opening
# quotes (i+3), and the pre-docstring prefix (coding line) must be preserved.
i = t.find('"""'); j = t.find('"""', i + 3) + 3
DOC = '''"""W227 pre-seat probe (bm-c loop window r945, 2026-10-12 23:4x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law). Upstream face = W226 FULL CYCLE LANDED (r940 seat
d7d270752 + r941 per-wave prereg derive f65d886cb + r943 five-face freeze splice
9b44d37d1 (dead window, landed) + engine self-burn 12/12 batched ledger appends
9f41cf5be/eed45a825 self-committed + finalize one-pass 22:41:33: ledger
918,789+2,200=920,989 EXACT, merged pool K=495,120,
results/perpetual_faces/n1_w226_results.json machine-read; six-gate
POST-FINALIZE heal receipt _r944bmc_w226_sixgate_receipt.json [W212-pattern
phase-miss #3 disclosed; W227 burn window = PRE-FINALIZE standing law] +
five-key ALL PASS _r944bmc_w226_fivekey_receipt.json independently re-verified
r945 + closeout estate absorbed bd50be730) -- SINGLE STATE: W2..W226 ALL
REGISTERED, zero in-flight declared seats. This probe IS the W227 re-derive on
the post-W226-REGISTERED universe mandated by the W226 probe leg4 + W226 seat
MSG projection (r587: never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W226-REGISTERED
universe (all upstream bands in N1_BANDS live import; no declared-injection
needed -- W209..W226 eighteen faces all registered bm-c continuous).
Derivation faces (STAIRCASE GEOMETRY EIGHTY-SEVENTH instance expected, W141
leg2 law + E36 card; the W226 seat MSG leg4 projection anticipated W227+ --
this probe IS that re-derive):
  A  arithmetic continuation from the registered W226 A tail -- expected
     REFUSED at its own start by the registered W226 B band (staircase
     A-hops-prior-B 87th); honest forward walk -> first-clean; A base ==
     prior-wave B tail+1 machine-checkable relation.
  B  arithmetic continuation from the registered W226 B tail -- naive lands
     INSIDE the W227 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base ==
     own-wave A tail+1 machine-checkable relation.
Anchor face: W226 finalize LANDED (ledger head 920,989 = prev 918,789 + 2,200;
merged pool K=495,120 machine-read in leg0; five-key ALL PASS
_r944bmc_w226_fivekey_receipt.json re-verified r945). W227 freeze is GATED on
nothing in-flight -- upstream fully landed, clean chain-order window.
Bloodline: _w226bmc_20261012_probe.py derive machinery verbatim, W227 facts
live-registry-driven; single-state universe (no declared-injection legs)."""'''
t = t[:i] + DOC + t[j:]

# --- 4: receipt probe string ----------------------------------------------------------
NEW_PROBE_STR = ('receipt = {"probe": "W227 pre-seat probe (bm-c loop r945 window, 2026-10-12 23:4x, '
                 'CEO fill-order standing + seat-first law + never-dry supply line; post-W226-REGISTERED '
                 'single-state universe, upstream W226 full cycle landed r940 seat d7d270752/r941 prereg '
                 'f65d886cb/r943 splice 9b44d37d1+engine self-burn 9f41cf5be+eed45a825/finalize 22:41:33/'
                 'six-gate heal+fivekey landed by r944 receipts, closeout estate absorbed bd50be730 r945)", '
                 '"legs": {}}')
m = re.search(r'receipt = \{"probe": "[^"]*", "legs": \{\}\}', t)
assert m, "receipt probe string not found"
t = t[:m.start()] + NEW_PROBE_STR + t[m.end():]

# --- 5: leg0 anchor tuple --------------------------------------------------------------
i = t.find('("W226 finalize LANDED')
assert i >= 0, "anchor start not found"
END = 'zero in-flight declared seats")'
j = t.find(END, i) + len(END)
NEW_ANCHOR = ('("W226 finalize LANDED (ledger 920,989 = prev 918,789 + 2,200, "\n'
              '                                     "K=495,120, mu=-0.0928 sigma=0.2451 machine-read; r943-dead-window body "\n'
              '                                     "(splice+burn+finalize) landed by r945 closeout bd50be730; six-gate POST-FINALIZE "\n'
              '                                     "heal W212-pattern #3 disclosed -- W227 burn window = PRE-FINALIZE standing law); upstream "\n'
              '                                     "W2..W226 ALL REGISTERED single state -- W227 freeze = clean "\n'
              '                                     "chain-order window, zero in-flight declared seats")')
t = t[:i] + NEW_ANCHOR + t[j:]

# --- 6: explicit numeric / ordinal pairs ------------------------------------------------
pair("owner_total == 215 and len(bmc_rows) == 55", "owner_total == 216 and len(bmc_rows) == 56", 1)
pair("(expect 215/55 post-W226-splice per the r939 splice receipt ordinal faces)",
     "(expect 216/56 post-W226-splice per the r943 splice receipt ordinal faces)", 1)
pair('led.get("total") == 918_789 and led.get("prev_total") == 916_589',
     'led.get("total") == 920_989 and led.get("prev_total") == 918_789', 1)
pair("(509_804, 511_803)", "(512_004, 514_003)", 1)
pair("(511_804, 512_003)", "(514_004, 514_203)", 1)
pair('"leg0 failed: W226 row drift (bm-c r939 splice face)"',
     '"leg0 failed: W226 row drift (bm-c r943 splice face)"', 1)
pair("492_920", "495_120", 1)
pair("-> 215th wave, bm-c 56th owned", "-> 216th wave, bm-c 57th owned", 1)
pair('"ordinal": 216,', '"ordinal": 217,', 1)
pair('"bmc_ordinal": 56,', '"bmc_ordinal": 57,', 1)
pair("W226 freeze receipt = 55th owned", "W226 freeze receipt = 56th owned", 1)
pair("(54 live rows + W226 candidate at r939 splice)", "(55 live rows + W226 candidate at r943 splice)", 1)
pair("candidate = 56th per the same continuity", "candidate = 57th per the same continuity", 1)

# --- 7: residual + required asserts ------------------------------------------------------
for bad in ("84ecb3a3a", "4b22941a7", "c78dd1a44", "8b12ace73", "W225", "EIGHTY-SIXTH",
            "215", "492_920", "r939 splice", "(509_804", "r940 window", "20:3x"):
    assert bad not in t, f"residual face {bad!r} still present"
for need in ("N1_BANDS[226]", "range(16, 227)", "n1_w226_results.json", "920_989", "495_120",
             "_w227bmc_20261012_probe_receipt.json", "EIGHTY-SEVENTH", "EIGHTY-EIGHTH",
             "PERPETUAL-N1-W227", "'227: {\"a\": ('"):
    assert need in t, f"required face {need!r} missing"

io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print(f"DERIVE OK: {DST} ({len(t)} bytes; bare226={n226} bare225={n225}; py_compile green)")
