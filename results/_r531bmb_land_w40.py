# r531 bm-b W40 freeze landing (canon three-file, byte-level LF per r500/r530 lesson)
# W40 = THIRTIETH ENGINE-OWNED WAVE, bm-b's THIRTEENTH owned wave.
# A = 123_004..125_003 (arithmetic continuation from bm-c's W39 row, no skip)
# B = 43_201..43_400  (arithmetic continuation, no skip -- W39 row W40+ WARNING
#     projected both sides CLEAN; machine-derived at this freeze, not prose-copied)
from pathlib import Path

def patch(path, old, new):
    p = Path(path)
    data = p.read_bytes().decode("utf-8")
    old = old.replace("\r\n", "\n")
    new = new.replace("\r\n", "\n")
    assert data.count(old) == 1, f"anchor not unique in {path} (count={data.count(old)})"
    p.write_bytes(data.replace(old, new).encode("utf-8"))
    print(f"patched {path}")

# --- 1. scripts/perpetual_faces.py: N1_BANDS W40 row ------------------------
patch(
    r"scripts/perpetual_faces.py",
    '''    39: {"a": (121_004, 123_003), "b_exit": (43_001, 43_200),
         "engine_owner": "bm-c"},
}''',
    '''    39: {"a": (121_004, 123_003), "b_exit": (43_001, 43_200),
         "engine_owner": "bm-c"},
    # W40 (r531 bm-b, own-series continuation per CEO de-throttle
    # order O-20261001-2355 sec.2 -- bm-b's THIRTEENTH owned wave after
    # W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/W36/W38; zero-gap relay
    # after the W38 FULL CLOSEOUT (r530: finalize one-pass K=81,520,
    # ledger head 446,140; W39 registered+burned by bm-c r342, finalize
    # pending on the bm-c lane) -> wave number 40 = FIRST FREE NUMBER
    # after bm-c's W39 landed claim. SIDES INDEPENDENTLY ADJUDICATED
    # per the W39 row's W40+ WARNING: A tail ARITHMETIC continuation
    # NO SKIP (123_004..125_003 == W39 A end + 1); B tail ARITHMETIC
    # continuation NO SKIP (43_201..43_400 == W39 B end + 1) -- both
    # sides projected CLEAN by the W39 row warning AND machine-derived
    # at this freeze (results/_r531bmb_w40_band_gate.py ADMIT receipt
    # vs the 37-row pre-W40 table incl. W35/W36/W37/W38/W39 + live
    # SEED_REGISTRY values + probe-seed cluster 95_000..95_003 r335
    # discovery leg + N3-R1 used-seed band 70_000..70_005 MSG-183x
    # r529 mandatory leg; origin slot vacancy machine-checked).
    # TWENTY-NINTH->THIRTIETH ENGINE-OWNED WAVE, engine_owner=bm-b
    # (SATURATION_ENGINE_LAW sec.1/2 same contract as W10..W39, local
    # queue, no pool entry). NOT a re-pick (R250: W40 bands were never
    # assigned; the measurement face has no result to fish).
    40: {"a": (123_004, 125_003), "b_exit": (43_201, 43_400),
         "engine_owner": "bm-b"},
}''')
print("N1_BANDS W40 row landed (byte-level LF)")

# --- 2. scripts/perpetual_faces_n1.py: WAVE_CONFIGS[40] ---------------------
patch(
    r"scripts/perpetual_faces_n1.py",
    '''                       "shard_subdir": "n1_w39", "out_name": "n1_w39_results.json",
                       "engine_owner": "bm-c"},
                 }''',
    '''                       "shard_subdir": "n1_w39", "out_name": "n1_w39_results.json",
                       "engine_owner": "bm-c"},
                  # W40 (r531 bm-b, own-series continuation per O-20261001-2355
                  # sec.2 -- bm-b's THIRTEENTH owned wave; zero-gap relay after
                  # the W38 FULL CLOSEOUT r530 (finalize one-pass K=81,520,
                  # ledger head 446,140). Wave 40 = first free number after
                  # bm-c's W39 landed claim. SIDES INDEPENDENTLY ADJUDICATED
                  # per the W39 row's W40+ WARNING: A tail arithmetic
                  # continuation no skip (123_004..125_003 == W39 A end + 1);
                  # B tail arithmetic continuation no skip (43_201..43_400 ==
                  # W39 B end + 1). Machine-verified at prereg time
                  # (results/_r531bmb_w40_band_gate.py ADMIT receipt vs the
                  # 37-row pre-W40 table + live SEED_REGISTRY values +
                  # probe-seed cluster 95_000..95_003 r335 discovery leg +
                  # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 mandatory
                  # leg; origin slot vacancy machine-checked). THIRTIETH
                  # ENGINE-OWNED WAVE, engine_owner=bm-b (local queue, no
                  # pool entry). NOT a re-pick (R250: W40 bands never assigned).
                  40: {"batch": "PERPETUAL-N1-W40",
                       "prereg": ("research/PERPETUAL_N1_W40_PREREG.md (wave-level frozen "
                                  "pre-run; design = frozen v1 null calibration verbatim, "
                                  "new seed bands only; THIRTIETH ENGINE-OWNED WAVE, "
                                  "own-series continuation per O-20261001-2355 sec.2 "
                                  "(seat system terminated, first-free-number law), "
                                  "engine_owner=bm-b, A tail arithmetic continuation "
                                  "from the registered W39 row no skip, B tail "
                                  "arithmetic continuation from the registered W39 "
                                  "row no skip per the W39 row W40+ WARNING projection "
                                  "(both sides CLEAN, machine-derived at this freeze))"),
                       "a_seed_base": 123_004,        # law sec.4 W40 A: 123_004..125_003 (arithmetic)
                       "b_exit_seed_base": 43_201,    # law sec.4 W40 B: 43_201..43_400 (arithmetic)
                       "shard_subdir": "n1_w40", "out_name": "n1_w40_results.json",
                       "engine_owner": "bm-b"},
                 }''')
print("WAVE_CONFIGS W40 row landed (byte-level LF)")
