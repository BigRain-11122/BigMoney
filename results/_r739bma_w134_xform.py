# -*- coding: utf-8 -*-
"""r739 bm-a W134 lineage transform: _r738bma_w133_probe.py -> _r739bma_w134_probe.py
(r735 needle-count law: ordered pairs, each count-asserted; r738 substring-order
law: longest needles first, overlaps impossible by construction)."""
import py_compile

SRC = "results/_r738bma_w133_probe.py"
DST = "results/_r739bma_w134_probe.py"

pairs = [
 ('r738 bm-a W133 pre-seat probe', 'r739 bm-a W134 pre-seat probe', 1),
 ('W133 candidate = first FREE number after the REGISTERED W132 row (bm-a\nr737 freeze 37c3925ad; W132 finalize landed same-window r738, ledger head\n686,411, merged pool K=288,320). Derivation faces:',
  'W134 candidate = first FREE number after the REGISTERED W133 row (bm-a\nr738 freeze a869ad2ee; W133 finalize landed same-window r739, ledger head\n688,611, merged pool K=290,520). Derivation faces:', 1),
 ('A  arithmetic continuation from the registered W132 A tail 309_003 + 1,\n     stride 2_000 -> 309_004..311_003, honest forward walk to first clean.',
  'A  arithmetic continuation from the registered W133 A tail 311_003 + 1,\n     stride 2_000 -> 311_004..313_003, honest forward walk to first clean.', 1),
 ('B  arithmetic continuation from the registered W132 B tail 69_101 + 1,\n     stride 200 -> 69_102..69_301, honest forward walk (r737 seat MSG-1755\n     tail projection: A 309_004..311_003 CLEAN hops=0 / B 69_102..69_301\n     CLEAN hops=0 -- double-CLEAN window, re-derived never transcribed\n     r587).',
  'B  arithmetic continuation from the registered W133 B tail 69_301 + 1,\n     stride 200 -> 69_302..69_501, honest forward walk (r738 seat MSG-1824\n     tail projection: A 311_004..313_003 CLEAN hops=0 / B 69_302..69_501\n     CLEAN hops=0 -- double-CLEAN window, re-derived never transcribed\n     r587).', 1),
 ('(W2..W14, W16..W132),', '(W2..W14, W16..W133),', 1),
 ('Bloodline: r737 _r737bma_w132_probe.py verbatim + W133 facts\n(double-CLEAN arithmetic continuation window from the registered W132 tails).',
  'Bloodline: r738 _r738bma_w133_probe.py verbatim + W134 facts\n(double-CLEAN arithmetic continuation window from the registered W133 tails).', 1),
 ('W132_A_TAIL = 309_003', 'W133_A_TAIL = 311_003', 1),
 ('W132_B_TAIL = 69_101', 'W133_B_TAIL = 69_301', 1),
 ('list(range(16, 133))', 'list(range(16, 134))', 1),
 ('assert N1_BANDS[130]["a"] == (303_004, 305_003) and \\\n    N1_BANDS[130]["b_exit"] == (68_502, 68_701) and \\\n    N1_BANDS[130].get("engine_owner") == "bm-a", "leg0 failed: W130 row drift"',
  'assert N1_BANDS[133]["a"] == (309_004, W133_A_TAIL) and \\\n    N1_BANDS[133]["b_exit"] == (69_102, W133_B_TAIL) and \\\n    N1_BANDS[133].get("engine_owner") == "bm-a", "leg0 failed: W133 row drift"', 1),
 ('assert N1_BANDS[132]["a"] == (307_004, W132_A_TAIL) and \\\n    N1_BANDS[132]["b_exit"] == (68_902, W132_B_TAIL) and \\\n    N1_BANDS[132].get("engine_owner") == "bm-a", "leg0 failed: W132 row drift"',
  'assert N1_BANDS[132]["a"] == (307_004, 309_003) and \\\n    N1_BANDS[132]["b_exit"] == (68_902, 69_101) and \\\n    N1_BANDS[132].get("engine_owner") == "bm-a", "leg0 failed: W132 row drift"', 1),
 ('MODE = "B133 (registered W132, bm-a r737 freeze 37c3925ad; W132 finalize landed r738)"',
  'MODE = "B134 (registered W133, bm-a r738 freeze a869ad2ee; W133 finalize landed r739)"', 1),
 ('f"rows={len(bma_rows)} -> W133 = bm-a "\n      f"{len(bma_rows) + 1}th owned; W133 ordinal = "',
  'f"rows={len(bma_rows)} -> W134 = bm-a "\n      f"{len(bma_rows) + 1}th owned; W134 ordinal = "', 1),
 ('assert len(owner_rows) == 122 and len(bma_rows) == 48, "leg0 ordinal drift"',
  'assert len(owner_rows) == 123 and len(bma_rows) == 49, "leg0 ordinal drift"', 1),
 ('(single state: W132 registered, tail=W132)', '(single state: W133 registered, tail=W133)', 1),
 ('honest forward walk from the registered W132 tails', 'honest forward walk from the registered W133 tails', 1),
 ('ARITH_A = (W132_A_TAIL + 1, W132_A_TAIL + WIDTH_A)', 'ARITH_A = (W133_A_TAIL + 1, W133_A_TAIL + WIDTH_A)', 1),
 ('ARITH_B = (W132_B_TAIL + 1, W132_B_TAIL + WIDTH_B)', 'ARITH_B = (W133_B_TAIL + 1, W133_B_TAIL + WIDTH_B)', 1),
 ('assert ARITH_A == (309_004, 311_003), f"leg1-A drift: {ARITH_A}"', 'assert ARITH_A == (311_004, 313_003), f"leg1-A drift: {ARITH_A}"', 1),
 ('assert ARITH_B == (69_102, 69_301), f"leg1-B drift: {ARITH_B}"', 'assert ARITH_B == (69_302, 69_501), f"leg1-B drift: {ARITH_B}"', 1),
 ('W133_A = fc_a\nW133_B = fc_b', 'W134_A = fc_a\nW134_B = fc_b', 1),
 ('convergence with the r737 seat MSG-1755 projection (r587) --', 'convergence with the r738 seat MSG-1824 projection (r587) --', 1),
 ('assert W133_A == (309_004, 311_003) and hops_a == 0, \\\n    f"leg1b failed: A fork vs W132 gate-tail projection: {W133_A}"',
  'assert W134_A == (311_004, 313_003) and hops_a == 0, \\\n    f"leg1b failed: A fork vs W133 gate-tail projection: {W134_A}"', 1),
 ('assert W133_B == (69_102, 69_301) and hops_b == 0, \\\n    f"leg1b failed: B fork vs W132 gate-tail projection: {W133_B}"',
  'assert W134_B == (69_302, 69_501) and hops_b == 0, \\\n    f"leg1b failed: B fork vs W133 gate-tail projection: {W134_B}"', 1),
 ('print("leg1b: derive converges bit-for-bit with the r737 W132 seat MSG-1755 "\n      "W133+ projection (r587 re-derive-never-transcribe law held); "',
  'print("leg1b: derive converges bit-for-bit with the r738 W133 seat MSG-1824 "\n      "W134+ projection (r587 re-derive-never-transcribe law held); "', 1),
 ('("A", W133_A), ("B", W133_B)', '("A", W134_A), ("B", W134_B)', 1),
 ('x W133-{tag} (MSG-183x leg)")', 'x W134-{tag} (MSG-183x leg)")', 1),
 ('inside W133-{tag} (r602 leg)")', 'inside W134-{tag} (r602 leg)")', 1),
 ('inside W133-{tag} (r335 leg)")', 'inside W134-{tag} (r335 leg)")', 1),
 ('x W133-{tag}")', 'x W134-{tag}")', 3),
 ('inside W133-{tag}")', 'inside W134-{tag}")', 3),
 ("assert '133: {\"a\": (309_004' not in out, \\\n    \"leg2 failed: W133 row ALREADY on origin (slot not vacant, r511 tail-lock)\"",
  "assert '134: {\"a\": (311_004' not in out, \\\n    \"leg2 failed: W134 row ALREADY on origin (slot not vacant, r511 tail-lock)\"", 1),
 ('"batch": "PERPETUAL-N1-W133"', '"batch": "PERPETUAL-N1-W134"', 1),
 ('"leg2 failed: W133 WAVE_CONFIGS ALREADY on origin"', '"leg2 failed: W134 WAVE_CONFIGS ALREADY on origin"', 1),
 ('research/PERPETUAL_N1_W133_PREREG.md', 'research/PERPETUAL_N1_W134_PREREG.md', 1),
 ('"leg2 failed: W133 per-wave prereg ALREADY on origin"', '"leg2 failed: W134 per-wave prereg ALREADY on origin"', 1),
 ('w133_seats', 'w134_seats', 3),
 ('"w133" in ln.lower()', '"w134" in ln.lower()', 1),
 ('"leg2 failed: W133 seat already published: {w134_seats}"', '"leg2 failed: W134 seat already published: {w134_seats}"', 1),
 ('print("W133 REFUSED:")', 'print("W134 REFUSED:")', 1),
 ('print(f"W133 ADMIT-derive: A {W133_A[0]}..{W133_A[1]} hops={hops_a} + "\n      f"B {W133_B[0]}..{W133_B[1]} hops={hops_b} "',
  'print(f"W134 ADMIT-derive: A {W134_A[0]}..{W134_A[1]} hops={hops_a} + "\n      f"B {W134_B[0]}..{W134_B[1]} hops={hops_b} "', 1),
 ('# --- W134+ projection (warning text for the law table row) --------------------', '# --- W135+ projection (warning text for the law table row) --------------------', 1),
 ('(fc134_a, h134a) = first_clean(W133_A[1] + 1, WIDTH_A)', '(fc135_a, h135a) = first_clean(W134_A[1] + 1, WIDTH_A)', 1),
 ('(fc134_b, h134b) = first_clean(W133_B[1] + 1, WIDTH_B)', '(fc135_b, h135b) = first_clean(W134_B[1] + 1, WIDTH_B)', 1),
 ('f134a = refusal_facts(fc134_a)', 'f135a = refusal_facts(fc135_a)', 1),
 ('f134b = refusal_facts(fc134_b)', 'f135b = refusal_facts(fc135_b)', 1),
 ("print(f\"W134+ projection: A first-clean {fc134_a[0]}..{fc134_a[1]} hops={h134a} \"\n      f\"-> {'CLEAN (verify at W134 prereg)' if not f134a else 'REFUSED ' + str(f134a)}; \"\n      f\"B first-clean {fc134_b[0]}..{fc134_b[1]} hops={h134b} \"\n      f\"-> {'CLEAN (verify at W134 prereg)' if not f134b else 'REFUSED ' + str(f134b)}\")",
  "print(f\"W135+ projection: A first-clean {fc135_a[0]}..{fc135_a[1]} hops={h135a} \"\n      f\"-> {'CLEAN (verify at W135 prereg)' if not f135a else 'REFUSED ' + str(f135a)}; \"\n      f\"B first-clean {fc135_b[0]}..{fc135_b[1]} hops={h135b} \"\n      f\"-> {'CLEAN (verify at W135 prereg)' if not f135b else 'REFUSED ' + str(f135b)}\")", 1),
]

src = open(SRC, encoding='utf-8', newline='').read()
for old, new, expect in pairs:
    n = src.count(old)
    assert n == expect, 'needle count mismatch (%d != %d): %r' % (n, expect, old[:60])
    src = src.replace(old, new)
leftover = [ln for ln in src.splitlines()
            if 'W133' in ln and 'W133_A_TAIL' not in ln and 'W133_B_TAIL' not in ln
            and 'N1_BANDS[133]' not in ln and 'leg0 failed: W133 row drift' not in ln]
print('leftover W133 lines (expect registered-tail refs only):')
for ln in leftover:
    print('  ', ln.strip()[:110])
open(DST, 'w', encoding='utf-8', newline='').write(src)
py_compile.compile(DST, doraise=True)
print('WRITTEN + COMPILED OK:', DST)
