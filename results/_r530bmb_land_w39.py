from pathlib import Path

# r500 byte-level lesson: target files are PURE-LF on disk; read_text/
# write_text (universal newlines) round-trips them to CRLF = whole-file
# diff. Byte-level edit with explicit LF normalization only.

def patch(path, old, new):
    p = Path(path)
    data = p.read_bytes().decode("utf-8")
    old = old.replace("\r\n", "\n")
    new = new.replace("\r\n", "\n")
    assert data.count(old) == 1, f"anchor not unique in {path}"
    p.write_bytes(data.replace(old, new).encode("utf-8"))
    print(f"patched {path}")

# --- 1. scripts/perpetual_faces.py: N1_BANDS W39 row ----------------------
patch(
    r"scripts/perpetual_faces.py",
    '''    38: {"a": (119_004, 121_003), "b_exit": (42_601, 42_800),
         "engine_owner": "bm-b"},
}''',
    '''    38: {"a": (119_004, 121_003), "b_exit": (42_601, 42_800),
         "engine_owner": "bm-b"},
    # W39 (r530 bm-b, own-series continuation per CEO de-throttle
    # order O-20261001-2355 sec.2 -- bm-b's THIRTEENTH owned wave after
    # W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/W36/W38; follows the W38
    # 12/12 burn this same window (r530: products delivered origin via
    # surgical 840df662a; W38 finalize chain-blocked on bm-c's W37
    # block per r543 chain order, MSG-20261002-012x sent) -> zero-gap
    # relay, wave number 39 = first free number after W38's landed
    # claim (bm-b r529). SIDES INDEPENDENTLY ADJUDICATED per the W38
    # row's W39+ WARNING: A tail ARITHMETIC continuation NO SKIP
    # (121_004..123_003 == W38 A end + 1); B tail FORCED SKIP past
    # 43_000 (arithmetic 42_801..43_000 REFUSED, tail point 43_000 =
    # SEED_REGISTRY p4_folk hit; jump to first clean window 43_001..
    # 43_200 per r307 tail-law precedent -- forced not a free pick).
    # Machine-verified at prereg time (results/_r530bmb_w39_band_gate.
    # py ADMIT receipt vs the 36-row pre-W39 table incl. W34/W35/W36/
    # W37/W38 + SEED_REGISTRY values + probe-seed cluster 95_000..
    # 95_003 r335 discovery leg + N3-R1 used-seed band 70_000..70_005
    # MSG-183x r529 mandatory leg; B-side refusal facts [43_000
    # p4_folk] machine-verified; origin slot vacancy machine-checked).
    # TWENTY-EIGHTH ENGINE-OWNED WAVE, engine_owner=bm-b
    # (SATURATION_ENGINE_LAW sec.1/2 same contract as W10..W38, local
    # queue, no pool entry). NOT a re-pick (R250: W39 bands were never
    # assigned; the measurement face has no result to fish).
    # W40+ WARNING: A +2_000 tail 123_004..125_003 and B +200 tail
    # 43_201..43_400 projection per the r530 gate receipt -- verify at
    # the next freeze's prereg (own-series: verify against the live
    # table tail + all published projections at that time).
    39: {"a": (121_004, 123_003), "b_exit": (43_001, 43_200),
          "engine_owner": "bm-b"},
}''')
print("N1_BANDS W39 row landed (byte-level LF)")
