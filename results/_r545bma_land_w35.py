# -*- coding: utf-8 -*-
"""r545 bm-a: land N1_BANDS[35] (W35 engine wave registration, de-throttle law
O-20261001-2355 sec.2 first bm-a wave under own-continuous-series)."""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = "scripts/perpetual_faces.py"
raw = open(p, "rb").read()
eol = b"\r\n" if raw.count(b"\r\n") > (raw.count(b"\n") - raw.count(b"\r\n")) else b"\n"
E = eol.decode("ascii")
src = open(p, encoding="utf-8", newline="").read()

old = E.join([
    '    33: {"a": (109_004, 111_003), "b_exit": (41_601, 41_800),',
    '         "engine_owner": "bm-a"},',
    '}',
])
new = E.join([
    '    33: {"a": (109_004, 111_003), "b_exit": (41_601, 41_800),',
    '         "engine_owner": "bm-a"},',
    "    # W35 (r545 bm-a, engine de-throttle law O-20261001-2355 sec.2:",
    "    # per-machine self-owned continuous series, zero-gap relay after the",
    "    # machine's previous wave closes -- W33 finalize landed bm-a r544,",
    "    # K=70,520, ledger 437,148 chain-linear). NOT a re-pick (R250: W35",
    "    # bands were never assigned; the measurement face has no result to",
    "    # fish). Wave number 35 = next free number after W34's published",
    "    # claim (bm-b pre-scan ADMIT-READY receipt r527: A 111_004..113_003",
    "    # / B 41_801..42_000, freeze pending at the bm-b seat under the new",
    "    # de-throttle law -- published projection = reserved face per r518;",
    "    # wave numbers are first-free-number allocation, no seat waiting).",
    "    # Forced skip over the published W34 projection windows, machine-",
    "    # proven by results/_r545bma_w35_band_gate.py refusal facts (the",
    "    # skip is forced, not a free choice -- r518 execution face).",
    "    # W36+ WARNING: A +2_000 tail 115_004..117_003 and B +200 tail",
    "    # 42_201..42_400 projection per the r545 gate receipt -- verify at",
    "    # W36 prereg (first-free-number law under O-2355 de-throttle).",
    '    35: {"a": (113_004, 115_003), "b_exit": (42_001, 42_200),',
    '         "engine_owner": "bm-a"},',
    '}',
])
assert src.count(old) == 1, f"anchor not unique: {src.count(old)}"
open(p, "w", encoding="utf-8", newline="").write(src.replace(old, new))
print("N1_BANDS[35] landed")
