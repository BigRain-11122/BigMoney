# -*- coding: utf-8 -*-
"""r732 bm-a W127 freeze-chain generator: derive _r732bma_w127_probe.py and
_r732bma_w127_band_gate.py from the r731 W126 bloodline by ordered literal
replacement, with per-needle count==1 assertions (r420 needle-furniture law).
Every replacement must fire exactly once -- zero silent no-ops."""
import io, sys

SEAT = "MSG-2026-10-05-1548-bma-w127-seat.md"
SEAT_COMMIT = "PENDING"  # seat commit sha filled after push; gate leg0b edited then

def transform(src, pairs, tag):
    for old, new in pairs:
        n = src.count(old)
        assert n == 1, f"{tag}: needle count={n} (expect 1): {old[:70]!r}"
        src = src.replace(old, new)
    return src

# ---------------- probe ----------------
p = io.open(r"results\_r731bma_w126_probe.py", encoding="utf-8").read()
probe_pairs = [
    ("r731 bm-a W126 pre-seat probe", "r732 bm-a W127 pre-seat probe"),
    ("""W126 candidate = first FREE number after the REGISTERED W125 row (bm-a
r730 freeze 77cd1f6ee; W125 finalize landed same-window r731, ledger
head 671,011, merged pool K=272,920). Derivation faces:""",
     """W127 candidate = first FREE number after the REGISTERED W126 row (bm-a
r731 freeze db9da0e92; W126 finalize landed same-window r732, ledger
head 673,211, merged pool K=275,120). Derivation faces:"""),
    ("""  A  arithmetic continuation from the registered W125 A tail 295_003 + 1,
     stride 2_000 -> 295_004..297_003, honest forward walk to first clean.
  B  arithmetic continuation from the registered W125 B tail 67_400 + 1,
     stride 200 -> 67_401..67_600, honest forward walk (W125 gate-tail
     projection CLEAN hops=0 both sides, re-derived never transcribed r587).""",
     """  A  arithmetic continuation from the registered W126 A tail 297_003 + 1,
     stride 2_000 -> 297_004..299_003, honest forward walk to first clean.
  B  arithmetic continuation from the registered W126 B tail 67_600 + 1,
     stride 200 -> 67_601..67_800, honest forward walk (W126 gate-tail
     projection CLEAN hops=0 both sides, re-derived never transcribed r587)."""),
    ("(W2..W14, W16..W125)", "(W2..W14, W16..W126)"),
    ("W125_A_TAIL = 295_003", "W126_A_TAIL = 297_003"),
    ("W125_B_TAIL = 67_400", "W126_B_TAIL = 67_600"),
    ("""assert N1_BANDS[123]["a"] == (289_004, 291_003) and \\
    N1_BANDS[123]["b_exit"] == (66_401, 66_600) and \\
    N1_BANDS[123].get("engine_owner") == "bm-a", "leg0 failed: W123 row drift"
assert N1_BANDS[124]["a"] == (291_004, 293_003) and \\
    N1_BANDS[124]["b_exit"] == (66_601, 66_800) and \\
    N1_BANDS[124].get("engine_owner") == "bm-a", "leg0 failed: W124 row drift"
assert N1_BANDS[125]["a"] == (293_004, W125_A_TAIL) and \\
    N1_BANDS[125]["b_exit"] == (67_201, W125_B_TAIL) and \\
    N1_BANDS[125].get("engine_owner") == "bm-a", "leg0 failed: W125 row drift\"""",
     """assert N1_BANDS[124]["a"] == (291_004, 293_003) and \\
    N1_BANDS[124]["b_exit"] == (66_601, 66_800) and \\
    N1_BANDS[124].get("engine_owner") == "bm-a", "leg0 failed: W124 row drift"
assert N1_BANDS[125]["a"] == (293_004, 295_003) and \\
    N1_BANDS[125]["b_exit"] == (67_201, 67_400) and \\
    N1_BANDS[125].get("engine_owner") == "bm-a", "leg0 failed: W125 row drift"
assert N1_BANDS[126]["a"] == (295_004, W126_A_TAIL) and \\
    N1_BANDS[126]["b_exit"] == (67_401, W126_B_TAIL) and \\
    N1_BANDS[126].get("engine_owner") == "bm-a", "leg0 failed: W126 row drift\""""),
    ("list(range(16, 126))", "list(range(16, 127))"),
    ('MODE = "B126 (registered W125, bm-a r730 freeze 77cd1f6ee; W125 finalize landed r731)"',
     'MODE = "B127 (registered W126, bm-a r731 freeze db9da0e92; W126 finalize landed r732)"'),
    ('f"rows={len(bma_rows)} -> W126 = bm-a "', 'f"rows={len(bma_rows)} -> W127 = bm-a "'),
    ('th owned; W126 ordinal = "', 'th owned; W127 ordinal = "'),
    ("assert len(owner_rows) == 115 and len(bma_rows) == 41, \"leg0 ordinal drift\"",
     "assert len(owner_rows) == 116 and len(bma_rows) == 42, \"leg0 ordinal drift\""),
    ("ARITH_A = (W125_A_TAIL + 1, W125_A_TAIL + WIDTH_A)", "ARITH_A = (W126_A_TAIL + 1, W126_A_TAIL + WIDTH_A)"),
    ("ARITH_B = (W125_B_TAIL + 1, W125_B_TAIL + WIDTH_B)", "ARITH_B = (W126_B_TAIL + 1, W126_B_TAIL + WIDTH_B)"),
    ("assert ARITH_A == (295_004, 297_003), f\"leg1-A drift: {ARITH_A}\"", "assert ARITH_A == (297_004, 299_003), f\"leg1-A drift: {ARITH_A}\""),
    ("assert ARITH_B == (67_401, 67_600), f\"leg1-B drift: {ARITH_B}\"", "assert ARITH_B == (67_601, 67_800), f\"leg1-B drift: {ARITH_B}\""),
    ("W126_A = fc_a\nW126_B = fc_b", "W127_A = fc_a\nW127_B = fc_b"),
    ('for tag, band in (("A", W126_A), ("B", W126_B)):', 'for tag, band in (("A", W127_A), ("B", W127_B)):'),
    ('conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W126-{tag}")', 'conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W127-{tag}")'),
    ('conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W126-{tag}")', 'conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W127-{tag}")'),
    ('conflicts.append(f"{nm} actual x W126-{tag}")', 'conflicts.append(f"{nm} actual x W127-{tag}")'),
    ('conflicts.append(f"N2/N4 probe point {p} inside W126-{tag}")', 'conflicts.append(f"N2/N4 probe point {p} inside W127-{tag}")'),
    ('conflicts.append(f"N2-W15 probe point {p} inside W126-{tag}")', 'conflicts.append(f"N2-W15 probe point {p} inside W127-{tag}")'),
    ('conflicts.append(f"cross-face probe point {p} inside W126-{tag} (r602 leg)")', 'conflicts.append(f"cross-face probe point {p} inside W127-{tag} (r602 leg)")'),
    ('conflicts.append(f"{nm} x W126-{tag}")', 'conflicts.append(f"{nm} x W127-{tag}")'),
    ('conflicts.append(f"N3-R1 used-seed band x W126-{tag} (MSG-183x leg)")', 'conflicts.append(f"N3-R1 used-seed band x W127-{tag} (MSG-183x leg)")'),
    ('conflicts.append(f"probe seed {p} inside W126-{tag} (r335 leg)")', 'conflicts.append(f"probe seed {p} inside W127-{tag} (r335 leg)")'),
    ("assert '126: {\"a\": (295_004' not in out, \\", "assert '127: {\"a\": (297_004' not in out, \\"),
    ('"leg2 failed: W126 row ALREADY on origin (slot not vacant, r511 tail-lock)"', '"leg2 failed: W127 row ALREADY on origin (slot not vacant, r511 tail-lock)"'),
    ("'\"batch\": \"PERPETUAL-N1-W126\"' not in outn1", "'\"batch\": \"PERPETUAL-N1-W127\"' not in outn1"),
    ('"leg2 failed: W126 WAVE_CONFIGS ALREADY on origin"', '"leg2 failed: W127 WAVE_CONFIGS ALREADY on origin"'),
    ('"research/PERPETUAL_N1_W126_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()', '"research/PERPETUAL_N1_W127_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()'),
    ('assert not outpre, "leg2 failed: W126 per-wave prereg ALREADY on origin"', 'assert not outpre, "leg2 failed: W127 per-wave prereg ALREADY on origin"'),
    ('if "w126" in ln.lower() and "seat" in ln.lower()]', 'if "w127" in ln.lower() and "seat" in ln.lower()]'),
    ('assert not w126_seats, f"leg2 failed: W126 seat already published: {w126_seats}"', 'assert not w127_seats, f"leg2 failed: W127 seat already published: {w127_seats}"'),
    ('w126_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()', 'w127_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()'),
    ('print("W126 REFUSED:")', 'print("W127 REFUSED:")'),
    ('print(f"W126 ADMIT-derive: A {W126_A[0]}..{W126_A[1]} hops={hops_a} + "', 'print(f"W127 ADMIT-derive: A {W127_A[0]}..{W127_A[1]} hops={hops_a} + "'),
    ('f"B {W126_B[0]}..{W126_B[1]} hops={hops_b} "', 'f"B {W127_B[0]}..{W127_B[1]} hops={hops_b} "'),
    ('"(mode={MODE}; both sides = arithmetic continuation from the registered "\n      "W125 tails; refusal facts machine-disclosed) -- clean vs all "', '"(mode={MODE}; both sides = arithmetic continuation from the registered "\n      "W126 tails; refusal facts machine-disclosed) -- clean vs all "'),
    ("# --- W127+ projection (warning text for the law table row) ---------------------", "# --- W128+ projection (warning text for the law table row) ---------------------"),
    ("(fc127_a, h127a) = first_clean(W126_A[1] + 1, WIDTH_A)", "(fc128_a, h128a) = first_clean(W127_A[1] + 1, WIDTH_A)"),
    ("(fc127_b, h127b) = first_clean(W126_B[1] + 1, WIDTH_B)", "(fc128_b, h128b) = first_clean(W127_B[1] + 1, WIDTH_B)"),
    ("f127a = refusal_facts(fc127_a)", "f128a = refusal_facts(fc128_a)"),
    ("f127b = refusal_facts(fc127_b)", "f128b = refusal_facts(fc128_b)"),
    ('print(f"W127+ projection: A first-clean {fc127_a[0]}..{fc127_a[1]} hops={h127a} "\n      f"-> {\'CLEAN (verify at W127 prereg)\' if not f127a else \'REFUSED \' + str(f127a)}; "\n      f"B first-clean {fc127_b[0]}..{fc127_b[1]} hops={h127b} "\n      f"-> {\'CLEAN (verify at W127 prereg)\' if not f127b else \'REFUSED \' + str(f127b)}")',
     'print(f"W128+ projection: A first-clean {fc128_a[0]}..{fc128_a[1]} hops={h128a} "\n      f"-> {\'CLEAN (verify at W128 prereg)\' if not f128a else \'REFUSED \' + str(f128a)}; "\n      f"B first-clean {fc128_b[0]}..{fc128_b[1]} hops={h128b} "\n      f"-> {\'CLEAN (verify at W128 prereg)\' if not f128b else \'REFUSED \' + str(f128b)}")'),
]
probe = transform(p, probe_pairs, "probe")
io.open(r"results\_r732bma_w127_probe.py", "w", encoding="utf-8", newline="\n").write(probe)
print("probe written:", len(probe), "bytes")

# ---------------- band gate ----------------
g = io.open(r"results\_r731bma_w126_band_gate.py", encoding="utf-8").read()
gate_pairs = [
    ("r731 bm-a W126 freeze-window band gate", "r732 bm-a W127 freeze-window band gate"),
    ("Receipt -> results/_r731bma_w126_band_gate.json", "Receipt -> results/_r732bma_w127_band_gate.json"),
    ('SEAT_PATH = "fleet/inbox/MSG-2026-10-05-1528-bma-w126-seat.md"', f'SEAT_PATH = "fleet/inbox/{SEAT}"'),
    ("W125_A, W125_B = (293_004, 295_003), (67_201, 67_400)", "W126_A, W126_B = (295_004, 297_003), (67_401, 67_600)"),
    ('receipt = {"probe": "r731 W126 freeze-window band gate", "legs": {}}', 'receipt = {"probe": "r732 W127 freeze-window band gate", "legs": {}}'),
    ("assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 126)), \\", "assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 127)), \\"),
    ('assert N1_BANDS[125]["a"] == W125_A and N1_BANDS[125]["b_exit"] == W125_B \\\n    and N1_BANDS[125].get("engine_owner") == "bm-a", "leg0 W125 row drift"',
     'assert N1_BANDS[126]["a"] == W126_A and N1_BANDS[126]["b_exit"] == W126_B \\\n    and N1_BANDS[126].get("engine_owner") == "bm-a", "leg0 W126 row drift"'),
    ('assert len(owner_rows) == 115 and len(bma_rows) == 41, "leg0 ordinal drift"', 'assert len(owner_rows) == 116 and len(bma_rows) == 42, "leg0 ordinal drift"'),
    ('receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W125",\n                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),\n                           "ordinal": 116, "bma_ordinal": 42}',
     'receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W126",\n                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),\n                           "ordinal": 117, "bma_ordinal": 43}'),
    ('print(f"leg0: {len(N1_BANDS)} rows tail=W125, owner=115 -> 116th wave, bm-a 42nd owned")', 'print(f"leg0: {len(N1_BANDS)} rows tail=W126, owner=116 -> 117th wave, bm-a 43rd owned")'),
    ('assert r.returncode == 0, "leg0b failed: own W126 seat MSG NOT on origin (r565)"', 'assert r.returncode == 0, "leg0b failed: own W127 seat MSG NOT on origin (r565)"'),
    ('assert "A 295_004..297_003" in seat_txt and "B 67_401..67_600" in seat_txt, \\\n    "leg0b failed: seat bands mismatch"', 'assert "A 297_004..299_003" in seat_txt and "B 67_601..67_800" in seat_txt, \\\n    "leg0b failed: seat bands mismatch"'),
    ('if "w126" in ln.lower() and "seat" in ln.lower()]', 'if "w127" in ln.lower() and "seat" in ln.lower()]'),
    ('assert seats == [SEAT_PATH], f"leg0b failed: unexpected W126 seats: {seats}"', 'assert seats == [SEAT_PATH], f"leg0b failed: unexpected W127 seats: {seats}"'),
    ('"seat_commit": "7d70b01fd (pre-freeze, r565)"}', '"seat_commit": "' + SEAT_COMMIT + ' (pre-freeze, r565)"}'),
    ('print("leg0b: own seat on origin, zero other W126 seats (r374 dual-dir scan)")', 'print("leg0b: own seat on origin, zero other W127 seats (r374 dual-dir scan)")'),
    ("ARITH_A = (W125_A[1] + 1, W125_A[1] + WIDTH_A)", "ARITH_A = (W126_A[1] + 1, W126_A[1] + WIDTH_A)"),
    ("ARITH_B = (W125_B[1] + 1, W125_B[1] + WIDTH_B)", "ARITH_B = (W126_B[1] + 1, W126_B[1] + WIDTH_B)"),
    ('assert ARITH_A == (295_004, 297_003) and ARITH_B == (67_401, 67_600), "leg1 drift"', 'assert ARITH_A == (297_004, 299_003) and ARITH_B == (67_601, 67_800), "leg1 drift"'),
    ('assert (fc_a, hops_a) == ((295_004, 297_003), 0), f"leg1 A derive fork: {fc_a}"', 'assert (fc_a, hops_a) == ((297_004, 299_003), 0), f"leg1 A derive fork: {fc_a}"'),
    ('assert (fc_b, hops_b) == ((67_401, 67_600), 0), f"leg1 B derive fork: {fc_b}"', 'assert (fc_b, hops_b) == ((67_601, 67_800), 0), f"leg1 B derive fork: {fc_b}"'),
    ('receipt["legs"]["leg1"] = {"A": "295_004..297_003", "hops_A": 0,\n                           "B": "67_401..67_600", "hops_B": 0,', 'receipt["legs"]["leg1"] = {"A": "297_004..299_003", "hops_A": 0,\n                           "B": "67_601..67_800", "hops_B": 0,'),
    ('"registered W125 B tail 67_400+1 CLEAN zero "\n                           "refusal points; dual-window derive parity with "\n                           "the pre-seat probe, cross-window convergence with "\n                           "the W125 gate-tail projection (r730)",', '"registered W126 B tail 67_600+1 CLEAN zero "\n                           "refusal points; dual-window derive parity with "\n                           "the pre-seat probe, cross-window convergence with "\n                           "the W126 gate-tail projection (r731)",'),
    ('print("leg1: A 295_004..297_003 hops=0 + B 67_401..67_600 hops=0 "', 'print("leg1: A 297_004..299_003 hops=0 + B 67_601..67_800 hops=0 "'),
    ('conflicts.append(f"N1_BANDS W{wname}.{key} x W126-{tag}")', 'conflicts.append(f"N1_BANDS W{wname}.{key} x W127-{tag}")'),
    ('conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W126-{tag}")', 'conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W127-{tag}")'),
    ('conflicts.append(f"{nm} actual x W126-{tag}")', 'conflicts.append(f"{nm} actual x W127-{tag}")'),
    ('conflicts.append(f"{nm} probe point {p} inside W126-{tag}")', 'conflicts.append(f"{nm} probe point {p} inside W127-{tag}")'),
    ('conflicts.append(f"N3-R1 used-seed band x W126-{tag} (MSG-183x)")', 'conflicts.append(f"N3-R1 used-seed band x W127-{tag} (MSG-183x)")'),
    ('conflicts.append(f"{nm} x W126-{tag}")', 'conflicts.append(f"{nm} x W127-{tag}")'),
    ('assert not conflicts, f"leg2 failed: W126 conflicts {conflicts}"', 'assert not conflicts, f"leg2 failed: W127 conflicts {conflicts}"'),
    ('assert not overlaps(fc_a, fc_b), "leg2 failed: W126 A/B overlap"', 'assert not overlaps(fc_a, fc_b), "leg2 failed: W127 A/B overlap"'),
    ("assert '126: {\"a\": (295_004' not in out, \\", "assert '127: {\"a\": (297_004' not in out, \\"),
    ('"leg2 failed: W126 row ALREADY on origin (r511 tail-lock)"', '"leg2 failed: W127 row ALREADY on origin (r511 tail-lock)"'),
    ("'\"batch\": \"PERPETUAL-N1-W126\"' not in outn1", "'\"batch\": \"PERPETUAL-N1-W127\"' not in outn1"),
    ('"leg2 failed: W126 WAVE_CONFIGS ALREADY on origin"', '"leg2 failed: W127 WAVE_CONFIGS ALREADY on origin"'),
    ('"research/PERPETUAL_N1_W126_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()', '"research/PERPETUAL_N1_W127_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()'),
    ('assert not outpre, "leg2 failed: W126 per-wave prereg ALREADY on origin"', 'assert not outpre, "leg2 failed: W127 per-wave prereg ALREADY on origin"'),
    ('receipt["legs"]["leg2"] = {"conflicts": 0, "origin_vacancy": True,\n                          "seat": SEAT_PATH, "push": "7d70b01fd (pre-freeze, r565)"}', 'receipt["legs"]["leg2"] = {"conflicts": 0, "origin_vacancy": True,\n                          "seat": SEAT_PATH, "push": "SEATSHA (pre-freeze, r565)"}'),
    ("# --- leg 3: W127+ projection (gate tail, next freezer re-derives) -----------------", "# --- leg 3: W128+ projection (gate tail, next freezer re-derives) -----------------"),
    ("(fc127_a, h127a) = first_clean(fc_a[1] + 1, WIDTH_A)", "(fc128_a, h128a) = first_clean(fc_a[1] + 1, WIDTH_A)"),
    ("(fc127_b, h127b) = first_clean(fc_b[1] + 1, WIDTH_B)", "(fc128_b, h128b) = first_clean(fc_b[1] + 1, WIDTH_B)"),
    ('receipt["legs"]["leg3"] = {"W127p_A": f"{fc127_a[0]}..{fc127_a[1]}",\n                           "hops_A": h127a,\n                           "W127p_B": f"{fc127_b[0]}..{fc127_b[1]}",\n                           "hops_B": h127b,',
     'receipt["legs"]["leg3"] = {"W128p_A": f"{fc128_a[0]}..{fc128_a[1]}",\n                           "hops_A": h128a,\n                           "W128p_B": f"{fc128_b[0]}..{fc128_b[1]}",\n                           "hops_B": h128b,'),
    ('print(f"leg3: W127+ projection A {fc127_a[0]}..{fc127_a[1]} hops={h127a} / "\n      f"B {fc127_b[0]}..{fc127_b[1]} hops={h127b} (next freezer re-derives)")',
     'print(f"leg3: W128+ projection A {fc128_a[0]}..{fc128_a[1]} hops={h128a} / "\n      f"B {fc128_b[0]}..{fc128_b[1]} hops={h128b} (next freezer re-derives)")'),
    ('"_r731bma_w126_band_gate.json"), "w",', '"_r732bma_w127_band_gate.json"), "w",'),
    ('print("W126 BAND GATE rc0 ADMIT: A 295_004..297_003 + B 67_401..67_600 "', 'print("W127 BAND GATE rc0 ADMIT: A 297_004..299_003 + B 67_601..67_800 "'),
]
gate = transform(g, gate_pairs, "gate")
io.open(r"results\_r732bma_w127_band_gate.py", "w", encoding="utf-8", newline="\n").write(gate)
print("gate written:", len(gate), "bytes")
