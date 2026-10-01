# -*- coding: utf-8 -*-
"""r545 bm-a: land WAVE_CONFIGS[35] + W35 materializer selftest leg in
scripts/perpetual_faces_n1.py (de-throttle law O-20261001-2355 sec.2 first
bm-a wave). EOL-probe anchored edits (r289 law)."""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = "scripts/perpetual_faces_n1.py"
raw = open(p, "rb").read()
eol = b"\r\n" if raw.count(b"\r\n") > (raw.count(b"\n") - raw.count(b"\r\n")) else b"\n"
E = eol.decode("ascii")
src = open(p, encoding="utf-8", newline="").read()

# --- face 1: WAVE_CONFIGS[35] row (append after the W33 row) --------------
old_cfg = E.join([
    '                 "shard_subdir": "n1_w33", "out_name": "n1_w33_results.json",',
    '                 "engine_owner": "bm-a"},',
    "         }",
])
new_cfg = E.join([
    '                 "shard_subdir": "n1_w33", "out_name": "n1_w33_results.json",',
    '                 "engine_owner": "bm-a"},',
    "            # W35 (r545 bm-a, engine de-throttle law O-20261001-2355",
    "            # sec.2 -- per-machine self-owned continuous series,",
    "            # zero-gap relay after W33 full closeout (finalize landed",
    "            # bm-a r544, K=70,520, ledger 437,148 chain-linear); seat",
    "            # system retired by the same order). Wave 35 = next free",
    "            # number after W34's published claim (bm-b pre-scan",
    "            # ADMIT-READY r527, freeze pending at the bm-b seat --",
    "            # published projection = reserved face per r518). Forced",
    "            # skip over the published W34 projection windows",
    "            # machine-proven by results/_r545bma_w35_band_gate.py",
    "            # refusal facts. TWENTY-FOURTH engine-owned wave, bm-a's",
    "            # EIGHTH owned wave after W12/W18/W21/W24/W27/W30/W33.",
    "            # NOT a re-pick (R250: W35 bands were never assigned; the",
    "            # measurement face has no result to fish).",
    '            35: {"batch": "PERPETUAL-N1-W35",',
    '                 "prereg": ("research/PERPETUAL_N1_W35_PREREG.md (wave-level frozen "',
    '                            "pre-run; design = frozen v1 null calibration verbatim, "',
    '                            "new seed bands only; TWENTY-FOURTH ENGINE-OWNED WAVE, "',
    '                            "engine de-throttle law O-20261001-2355 sec.2 "',
    '                            "own-continuous-series, engine_owner=bm-a, forced skip "',
    '                            "over W34 published projection, wave 35 = first free "',
    '                            "number after W34\'s claim)"),',
    '                 "a_seed_base": 113_004,        # law sec.4 W35 A: 113_004..115_003 (post-projection)',
    '                 "b_exit_seed_base": 42_001,    # law sec.4 W35 B: 42_001..42_200 (post-projection)',
    '                 "shard_subdir": "n1_w35", "out_name": "n1_w35_results.json",',
    '                 "engine_owner": "bm-a"},',
    "          }",
])
assert src.count(old_cfg) == 1, f"cfg anchor not unique: {src.count(old_cfg)}"
src = src.replace(old_cfg, new_cfg)
print("WAVE_CONFIGS[35] landed")

# --- face 2: W35 materializer selftest leg (insert after the W33 leg) -----
w33_leg_tail = E.join([
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
    "    finally:",
    "        _set_wave(2)",
    "    # --- T-141 s2 lane face",
])
w35_leg = E.join([
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
    "    finally:",
    "        _set_wave(2)",
    "    # --- W35 materializer face (r545 bm-a freeze, de-throttle law",
    "    #     O-20261001-2355 sec.2 own-continuous-series) -----------------",
    "    _set_wave(35)",
    "    try:",
    "        assert WAVE_CONFIGS[35][\"a_seed_base\"] == pf.N1_BANDS[35][\"a\"][0], \\",
    "            \"W35 A band drift vs law mirror\"",
    "        assert WAVE_CONFIGS[35][\"b_exit_seed_base\"] == \\",
    "            pf.N1_BANDS[35][\"b_exit\"][0], \"W35 B band drift vs law mirror\"",
    "        assert WAVE_CONFIGS[35].get(\"engine_owner\") == \\",
    "            pf.N1_BANDS[35].get(\"engine_owner\") == \"bm-a\", \\",
    "            \"W35 engine_owner drift (law mirror parity)\"",
    "        w35_a = {A_SEED_BASE + j for j in range(A_N)}",
    "        w35_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
    "        assert not (w35_a & w35_b), \"W35 A/B band overlap\"",
    "        assert not (w35_a & reg_ints) and not (w35_b & reg_ints), \\",
    "            \"W35 hits SEED_REGISTRY\"",
    "        for nm, band in ((\"A\", w35_a), (\"B\", w35_b)):",
    "            assert not (band & v1_a) and not (band & v1_b), f\"W35 {nm} hits v1\"",
    "            assert not (band & w1_a) and not (band & w1_b), f\"W35 {nm} hits W1\"",
    "            assert not (band & probes), f\"W35 {nm} hits probe seeds\"",
    "        # prior-wave disjointness incl. W30/W31/W32/W33 (all registered;",
    "        # W34 has NO registry row yet -- bm-b pre-scan ADMIT-READY r527,",
    "        # freeze pending at the bm-b seat; its published projection is",
    "        # asserted disjoint from W35 by the band-gate PUBLISHED leg and",
    "        # the arithmetic-continuation facts below).",
    "        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,",
    "                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,",
    "                      31, 32, 33):",
    "            assert not (w35_a & {WAVE_CONFIGS[wprev][\"a_seed_base\"] + j",
    "                                 for j in range(A_N)}), f\"W35 A hits W{wprev}\"",
    "            assert not (w35_b & {WAVE_CONFIGS[wprev][\"b_exit_seed_base\"] + j",
    "                                 for j in range(B_N)}), f\"W35 B hits W{wprev}\"",
    "        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,",
    "        # r529 bm-a adjudication row) -- W35 bands must clear it.",
    "        n3r1_used35 = set(range(70_000, 70_006))",
    "        assert not (w35_a & n3r1_used35) and not (w35_b & n3r1_used35), \\",
    "            \"W35 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)\"",
    "        # actual-draw-range avoidance (leg-3e family)",
    "        assert not (w35_a & lfc_actual12) and not (w35_b & lfc_actual12), \\",
    "            \"W35 bands must clear the lfc actual draw range\"",
    "        assert not (w35_a & options_actual12) and \\",
    "            not (w35_b & options_actual12), \\",
    "            \"W35 bands must clear the options_wave2 actual draw range\"",
    "        # forced-skip facts (law sec.4 W35 row, r545): the arithmetic",
    "        # continuation from W33 IS the published W34 projection",
    "        # (A 111_004..113_003 / B 41_801..42_000, bm-b pre-scan",
    "        # ADMIT-READY r527) -> reserved face per r518; W35 starts at",
    "        # the published projection end + 1 on both sides (machine-",
    "        # proven forced skip, gate refusal facts).",
    "        assert WAVE_CONFIGS[35][\"a_seed_base\"] == 113_004 == 113_003 + 1, \\",
    "            \"W35 A must start at the W34 published projection end + 1\"",
    "        assert WAVE_CONFIGS[35][\"b_exit_seed_base\"] == 42_001 == 42_000 + 1, \\",
    "            \"W35 B must start at the W34 published projection end + 1\"",
    "        w34_proj_a = set(range(111_004, 113_004))",
    "        w34_proj_b = set(range(41_801, 42_001))",
    "        assert not (w35_a & w34_proj_a) and not (w35_b & w34_proj_b), \\",
    "            \"W35 bands hit the published W34 projection (r518 reserved face)\"",
    "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W35-SHARD-0\",",
    "                                          \"n1w35-0of12\"), \"W35 entry identity\"",
    "        assert _entry_shard_of(11, 12) == (\"PERPETUAL-N1-W35-SHARD-11\",",
    "                                           \"n1w35-11of12\")",
    "        assert SHARD_DIR.endswith(\"n1_w35\") and OUT.endswith(",
    "            \"n1_w35_results.json\"), \"W35 path drift\"",
    "        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,",
    "                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,",
    "                      31, 32, 33):",
    "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
    "                PATHS.results_dir, \"p2cal_ext\",",
    "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
    "                f\"W35 shard dir collides with W{wprev}\"",
    "        assert os.path.exists(os.path.join(",
    "            PATHS.root, \"research\", \"PERPETUAL_N1_W35_PREREG.md\")), \\",
    "            \"W35 per-wave prereg missing (materializer requirement)\"",
    "        # W35 finalize cumulative deps: W17..W33 outputs ALL PRESENT;",
    "        # W34 has no registry row at this freeze (bm-b pre-scan pending",
    "        # at their seat) -- when bm-b lands the W34 freeze+finalize,",
    "        # the dep pin auto-joins +34 per the r531-1/r541 minimal-amendment",
    "        # precedent (finalize runtime composes every registry key below",
    "        # 35 = FAIL-CLOSED honest wait for the W34 output once registered).",
    "        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,",
    "                      30, 31, 32, 33):",
    "            assert os.path.exists(os.path.join(",
    "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
    "                f\"W35 finalize cumulative dep (W{_depw} output) missing\"",
    "        # finalize wave-set derivation face (r511 derive law): prior-wave",
    "        # set derives from registry keys below 35 (no 15, no 34 until",
    "        # bm-b registers W34 -- then the runtime FAIL-CLOSED compose",
    "        # consumes it automatically).",
    "        assert sorted(w for w in WAVE_CONFIGS if w < 35) == \\",
    "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,",
    "             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33], \\",
    "            \"W35 prior-wave set must derive from registry keys (no 15, no 34)\"",
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
    "    finally:",
    "        _set_wave(2)",
    "    # --- T-141 s2 lane face",
])
assert src.count(w33_leg_tail) == 1, f"leg anchor not unique: {src.count(w33_leg_tail)}"
src = src.replace(w33_leg_tail, w35_leg)
print("W35 materializer selftest leg landed")

open(p, "w", encoding="utf-8", newline="").write(src)
import ast
ast.parse(src)
print("AST parse OK")
