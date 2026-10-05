# -*- coding: utf-8 -*-
"""r739 bm-a W134 band-gate lineage transform: _r738bma_w133_band_gate.py ->
_r739bma_w134_band_gate.py (r735 needle-count law)."""
import py_compile

SRC = "results/_r738bma_w133_band_gate.py"
DST = "results/_r739bma_w134_band_gate.py"

pairs = [
 ('r738 bm-a W133 freeze-window band gate', 'r739 bm-a W134 freeze-window band gate', 1),
 ('Bloodline: r737 _r737bma_w132_band_gate.py verbatim + W133 facts',
  'Bloodline: r738 _r738bma_w133_band_gate.py verbatim + W134 facts', 1),
 ('(double-CLEAN window: A = arithmetic continuation from the registered\nW132 A tail 309_003+1 CLEAN hops=0; B = arithmetic continuation from\nthe registered W132 B tail 69_101+1 CLEAN hops=0).',
  '(double-CLEAN window: A = arithmetic continuation from the registered\nW133 A tail 311_003+1 CLEAN hops=0; B = arithmetic continuation from\nthe registered W133 B tail 69_301+1 CLEAN hops=0).', 1),
 ('Receipt -> results/_r738bma_w133_band_gate.json', 'Receipt -> results/_r739bma_w134_band_gate.json', 1),
 ('SEAT_PATH = "fleet/inbox/MSG-2026-10-05-1824-bma-w133-seat.md"',
  'SEAT_PATH = "fleet/inbox/MSG-2026-10-05-1857-bma-w134-seat.md"', 1),
 ('W132_A, W132_B = (307_004, 309_003), (68_902, 69_101)',
  'W133_A, W133_B = (309_004, 311_003), (69_102, 69_301)', 1),
 ('receipt = {"probe": "r738 W133 freeze-window band gate", "legs": {}}',
  'receipt = {"probe": "r739 W134 freeze-window band gate", "legs": {}}', 1),
 ('list(range(16, 133))', 'list(range(16, 134))', 1),
 ('assert N1_BANDS[132]["a"] == W132_A and N1_BANDS[132]["b_exit"] == W132_B \\\n    and N1_BANDS[132].get("engine_owner") == "bm-a", "leg0 W132 row drift"',
  'assert N1_BANDS[133]["a"] == W133_A and N1_BANDS[133]["b_exit"] == W133_B \\\n    and N1_BANDS[133].get("engine_owner") == "bm-a", "leg0 W133 row drift"', 1),
 ('assert len(owner_rows) == 122 and len(bma_rows) == 48, "leg0 ordinal drift"',
  'assert len(owner_rows) == 123 and len(bma_rows) == 49, "leg0 ordinal drift"', 1),
 ('receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W132",\n                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),\n                           "ordinal": 123, "bma_ordinal": 49}',
  'receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W133",\n                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),\n                           "ordinal": 124, "bma_ordinal": 50}', 1),
 ('print(f"leg0: {len(N1_BANDS)} rows tail=W132, owner=122 -> 123rd wave, bm-a 49th owned")',
  'print(f"leg0: {len(N1_BANDS)} rows tail=W133, owner=123 -> 124th wave, bm-a 50th owned")', 1),
 ('assert r.returncode == 0, "leg0b failed: own W133 seat MSG NOT on origin (r565)"',
  'assert r.returncode == 0, "leg0b failed: own W134 seat MSG NOT on origin (r565)"', 1),
 ('assert "A 309_004..311_003" in seat_txt and "B 69_102..69_301" in seat_txt, \\\n    "leg0b failed: seat bands mismatch"',
  'assert "A 311_004..313_003" in seat_txt and "B 69_302..69_501" in seat_txt, \\\n    "leg0b failed: seat bands mismatch"', 1),
 ('if "w133" in ln.lower() and "seat" in ln.lower()', 'if "w134" in ln.lower() and "seat" in ln.lower()', 1),
 ('assert seats == [SEAT_PATH], f"leg0b failed: unexpected W133 seats: {seats}"',
  'assert seats == [SEAT_PATH], f"leg0b failed: unexpected W134 seats: {seats}"', 1),
 ('print("leg0b: own seat on origin, zero other W133 seats (r374 dual-dir scan)")',
  'print("leg0b: own seat on origin, zero other W134 seats (r374 dual-dir scan)")', 1),
 ('ARITH_A = (W132_A[1] + 1, W132_A[1] + WIDTH_A)', 'ARITH_A = (W133_A[1] + 1, W133_A[1] + WIDTH_A)', 1),
 ('ARITH_B = (W132_B[1] + 1, W132_B[1] + WIDTH_B)', 'ARITH_B = (W133_B[1] + 1, W133_B[1] + WIDTH_B)', 1),
 ('assert ARITH_A == (309_004, 311_003) and ARITH_B == (69_102, 69_301), "leg1 drift"',
  'assert ARITH_A == (311_004, 313_003) and ARITH_B == (69_302, 69_501), "leg1 drift"', 1),
 ('assert (fc_a, hops_a) == ((309_004, 311_003), 0), f"leg1 A derive fork: {fc_a}"',
  'assert (fc_a, hops_a) == ((311_004, 313_003), 0), f"leg1 A derive fork: {fc_a}"', 1),
 ('assert (fc_b, hops_b) == ((69_102, 69_301), 0), f"leg1 B derive fork: {fc_b}"',
  'assert (fc_b, hops_b) == ((69_302, 69_501), 0), f"leg1 B derive fork: {fc_b}"', 1),
 ('receipt["legs"]["leg1"] = {"A": "309_004..311_003", "hops_A": 0,\n                           "B": "69_102..69_301", "hops_B": 0,',
  'receipt["legs"]["leg1"] = {"A": "311_004..313_003", "hops_A": 0,\n                           "B": "69_302..69_501", "hops_B": 0,', 1),
 ('"arithmetic continuations from the registered W132 "\n                           "tails, hops=0, zero refusal points in either "\n                           "window; dual-window derive parity with the "\n                           "pre-seat probe, cross-window convergence with "\n                           "the W132 seat MSG-1755 tail projection (r737)",',
  '"arithmetic continuations from the registered W133 "\n                           "tails, hops=0, zero refusal points in either "\n                           "window; dual-window derive parity with the "\n                           "pre-seat probe, cross-window convergence with "\n                           "the W133 seat MSG-1824 tail projection (r738)",', 1),
 ('print("leg1: A 309_004..311_003 hops=0 + B 69_102..69_301 hops=0 "',
  'print("leg1: A 311_004..313_003 hops=0 + B 69_302..69_501 hops=0 "', 1),
 ('x W133-{tag} (MSG-183x)")', 'x W134-{tag} (MSG-183x)")', 1),
 ('x W133-{tag}")', 'x W134-{tag}")', 3),
 ('inside W133-{tag}")', 'inside W134-{tag}")', 2),
 ('assert not conflicts, f"leg2 failed: W133 conflicts {conflicts}"',
  'assert not conflicts, f"leg2 failed: W134 conflicts {conflicts}"', 1),
 ('assert not overlaps(fc_a, fc_b), "leg2 failed: W133 A/B overlap"',
  'assert not overlaps(fc_a, fc_b), "leg2 failed: W134 A/B overlap"', 1),
 ("assert '133: {\"a\": (309_004' not in out, \\\n    \"leg2 failed: W133 row ALREADY on origin (r511 tail-lock)\"",
  "assert '134: {\"a\": (311_004' not in out, \\\n    \"leg2 failed: W134 row ALREADY on origin (r511 tail-lock)\"", 1),
 ('assert \'"batch": "PERPETUAL-N1-W133"\' not in outn1, \\\n    "leg2 failed: W133 WAVE_CONFIGS ALREADY on origin"',
  'assert \'"batch": "PERPETUAL-N1-W134"\' not in outn1, \\\n    "leg2 failed: W134 WAVE_CONFIGS ALREADY on origin"', 1),
 ('research/PERPETUAL_N1_W133_PREREG.md', 'research/PERPETUAL_N1_W134_PREREG.md', 1),
 ('assert not outpre, "leg2 failed: W133 per-wave prereg ALREADY on origin"',
  'assert not outpre, "leg2 failed: W134 per-wave prereg ALREADY on origin"', 1),
 ('2d717cc03 (pre-freeze, r565)', '5f3d9fcfc (pre-freeze, r565; delivered via merge ad07612e7)', 2),
 ('# --- leg 3: W134+ projection (gate tail, next freezer re-derives) -----------------',
  '# --- leg 3: W135+ projection (gate tail, next freezer re-derives) -----------------', 1),
 ('(fc134_a, h134a) = first_clean(fc_a[1] + 1, WIDTH_A)', '(fc135_a, h135a) = first_clean(fc_a[1] + 1, WIDTH_A)', 1),
 ('(fc134_b, h134b) = first_clean(fc_b[1] + 1, WIDTH_B)', '(fc135_b, h135b) = first_clean(fc_b[1] + 1, WIDTH_B)', 1),
 ('receipt["legs"]["leg3"] = {"W134p_A": f"{fc134_a[0]}..{fc134_a[1]}",\n                           "hops_A": h134a,\n                           "W134p_B": f"{fc134_b[0]}..{fc134_b[1]}",\n                           "hops_B": h134b}',
  'receipt["legs"]["leg3"] = {"W135p_A": f"{fc135_a[0]}..{fc135_a[1]}",\n                           "hops_A": h135a,\n                           "W135p_B": f"{fc135_b[0]}..{fc135_b[1]}",\n                           "hops_B": h135b}', 1),
 ('print(f"leg3: W134+ projection A {fc134_a[0]}..{fc134_a[1]} hops={h134a} / "\n      f"B {fc134_b[0]}..{fc134_b[1]} hops={h134b} (next freezer re-derives)")',
  'print(f"leg3: W135+ projection A {fc135_a[0]}..{fc135_a[1]} hops={h135a} / "\n      f"B {fc135_b[0]}..{fc135_b[1]} hops={h135b} (next freezer re-derives)")', 1),
 ('"_r738bma_w133_band_gate.json"), "w",', '"_r739bma_w134_band_gate.json"), "w",', 1),
 ('print("W133 BAND GATE rc0 ADMIT: A 309_004..311_003 + B 69_102..69_301 "',
  'print("W134 BAND GATE rc0 ADMIT: A 311_004..313_003 + B 69_302..69_501 "', 1),
]

src = open(SRC, encoding='utf-8', newline='').read()
for old, new, expect in pairs:
    n = src.count(old)
    assert n == expect, 'needle count mismatch (%d != %d): %r' % (n, expect, old[:60])
    src = src.replace(old, new)
leftover = [ln for ln in src.splitlines() if 'W133' in ln and 'W133_A' not in ln and 'W133_B' not in ln
            and 'N1_BANDS[133]' not in ln and 'leg0 W133 row drift' not in ln]
print('leftover W133 lines (expect registered-tail refs only):')
for ln in leftover:
    print('  ', ln.strip()[:110])
open(DST, 'w', encoding='utf-8', newline='').write(src)
py_compile.compile(DST, doraise=True)
print('WRITTEN + COMPILED OK:', DST)
