"""W44 FREEZE working-tree edits (r533 bm-b, bytes-safe per r530 law).

Inserts (exact-anchor, assert-found-once):
  A. scripts/perpetual_faces.py        -> N1_BANDS row 44 (+comment block)
  B. scripts/perpetual_faces_n1.py     -> WAVE_CONFIGS[44] (+comment block)
  C. scripts/perpetual_faces_n1.py     -> selftest W44 materializer face leg
  D. scripts/perpetual_faces_n1.py     -> selftest print W44 face desc
  E. research/PERPETUAL_FACES.md       -> law sec.4 W44 row (after W43 row)

Prereg (research/PERPETUAL_N1_W44_PREREG.md) + band gate
(results/_r533bmb_w44_band_gate.py) are separate files (already written).
"""
import io, sys

def edit(path, old, new, tag):
    b = open(path, "rb").read().decode("utf-8")
    n = b.count(old)
    assert n == 1, f"{tag}: anchor count {n} != 1"
    open(path, "wb").write(b.replace(old, new).encode("utf-8"))
    print(f"{tag}: OK")

# ---------- A. N1_BANDS row 44 (scripts/perpetual_faces.py) ----------
ROW44 = (
    "    # W44 (r533 bm-b, own-series continuation per O-20261001-2355\n"
    "    # sec.2 -- bm-b's FOURTEENTH owned wave; zero-gap relay after\n"
    "    # the W40 FULL CLOSEOUT (freeze r531 -> 12/12 burn -> finalize\n"
    "    # r532 one-pass K=85,920, ledger 450,540 chain head; products\n"
    "    # delivered origin db5110d55). Wave 44 = first free number\n"
    "    # after bm-c's W43 landed claim (r346, burn in flight at this\n"
    "    # freeze -- in-flight coexists by band disjointness r531 law).\n"
    "    # SIDES INDEPENDENTLY ADJUDICATED per the W43 row's\n"
    "    # W44+ WARNING: A tail arithmetic continuation no skip\n"
    "    # (131_004..133_003 == W43 A end + 1); B tail arithmetic\n"
    "    # continuation no skip (44_201..44_400 == W43 B end + 1).\n"
    "    # Machine-verified at prereg time (results/_r533bmb_w44_band_gate.py\n"
    "    # ADMIT receipt vs the 42-row pre-W44 table + live SEED_REGISTRY\n"
    "    # values + probe-seed cluster 95_000..95_003 r335 discovery leg +\n"
    "    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 mandatory\n"
    "    # leg; origin slot vacancy machine-checked). THIRTY-FOURTH\n"
    "    # ENGINE-OWNED WAVE, engine_owner=bm-b (local queue, no pool\n"
    "    # entry). NOT a re-pick (R250: W44 bands never assigned).\n"
    "    44: {\"a\": (131_004, 133_003), \"b_exit\": (44_201, 44_400),\n"
    "         \"engine_owner\": \"bm-b\"},\n"
)
edit(
    "scripts/perpetual_faces.py",
    "    43: {\"a\": (129_004, 131_003), \"b_exit\": (44_001, 44_200),\n"
    "         \"engine_owner\": \"bm-c\"},\n}",
    "    43: {\"a\": (129_004, 131_003), \"b_exit\": (44_001, 44_200),\n"
    "         \"engine_owner\": \"bm-c\"},\n" + ROW44 + "}",
    "A registry row 44",
)

# ---------- B. WAVE_CONFIGS[44] (scripts/perpetual_faces_n1.py) ----------
CFG44 = (
    "                  # W44 (r533 bm-b, own-series continuation per O-20261001-2355\n"
    "                  # sec.2 -- bm-b's FOURTEENTH owned wave; zero-gap relay after\n"
    "                  # the W40 FULL CLOSEOUT (freeze r531 -> 12/12 burn ->\n"
    "                  # finalize r532 one-pass K=85,920, ledger 450,540; prereg\n"
    "                  # s7/s8 backfilled r532). Wave 44 = first free number\n"
    "                  # after bm-c's W43 landed claim (r346, burn in flight at\n"
    "                  # this freeze -- in-flight coexists by band disjointness\n"
    "                  # r531 law). SIDES INDEPENDENTLY ADJUDICATED per the\n"
    "                  # W43 row's W44+ WARNING: A tail arithmetic continuation\n"
    "                  # no skip (131_004..133_003 == W43 A end + 1); B tail\n"
    "                  # arithmetic continuation no skip (44_201..44_400 == W43\n"
    "                  # B end + 1). Machine-verified at prereg time\n"
    "                  # (results/_r533bmb_w44_band_gate.py ADMIT receipt vs the\n"
    "                  # 42-row pre-W44 table + live SEED_REGISTRY values +\n"
    "                  # probe-seed cluster 95_000..95_003 r335 discovery leg +\n"
    "                  # N3-R1 used-seed band 70_000..70_005 MSG-183x r529\n"
    "                  # mandatory leg; origin slot vacancy machine-checked).\n"
    "                  # THIRTY-FOURTH ENGINE-OWNED WAVE, engine_owner=bm-b\n"
    "                  # (local queue, no pool entry). NOT a re-pick (R250: W44\n"
    "                  # bands were never assigned).\n"
    "                  44: {\"batch\": \"PERPETUAL-N1-W44\",\n"
    "                       \"prereg\": (\"research/PERPETUAL_N1_W44_PREREG.md (wave-level frozen \"\n"
    "                                  \"pre-run; design = frozen v1 null calibration verbatim, \"\n"
    "                                  \"new seed bands only; THIRTY-FOURTH ENGINE-OWNED WAVE, \"\n"
    "                                  \"own-series continuation per O-20261001-2355 sec.2 \"\n"
    "                                  \"(seat system terminated, first-free-number law), \"\n"
    "                                  \"engine_owner=bm-b, A tail arithmetic continuation \"\n"
    "                                  \"from the registered W43 row no skip, B tail \"\n"
    "                                  \"arithmetic continuation from the registered W43 \"\n"
    "                                  \"row no skip per the W43 row W44+ WARNING projection \"\n"
    "                                  \"(both sides CLEAN, machine-derived at this freeze)\"),\n"
    "                       \"a_seed_base\": 131_004,        # law sec.4 W44 A: 131_004..133_003 (arithmetic)\n"
    "                       \"b_exit_seed_base\": 44_201,    # law sec.4 W44 B: 44_201..44_400 (arithmetic)\n"
    "                       \"shard_subdir\": \"n1_w44\", \"out_name\": \"n1_w44_results.json\",\n"
    "                       \"engine_owner\": \"bm-b\"},\n"
)
edit(
    "scripts/perpetual_faces_n1.py",
    "                       \"engine_owner\": \"bm-c\"},\n"
    "                 }",
    "                       \"engine_owner\": \"bm-c\"},\n" + CFG44 + "                 }",
    "B WAVE_CONFIGS 44",
)

# ---------- C. selftest W44 materializer face leg ----------
PREV44 = "(2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,\n" \
         "                      20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,\n" \
         "                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41,\n" \
         "                      42, 43)"
LEG44 = (
    "    # --- W44 materializer face (r533 bm-b freeze, own-series law\n"
    "    #     O-20261001-2355 sec.2 -- bm-b's FOURTEENTH owned wave after\n"
    "    #     W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/W36/W38/W40;\n"
    "    #     zero-gap relay after the W40 FULL CLOSEOUT: freeze r531 ->\n"
    "    #     12/12 burn -> finalize r532 one-pass K=85,920, ledger\n"
    "    #     450,540 chain head; W41/W42 = bm-c lineage finalized\n"
    "    #     (K=88,120 head 452,740 / K=90,320 head 454,940); W43 =\n"
    "    #     bm-c lineage burn in flight at this freeze -- in-flight\n"
    "    #     coexists by band disjointness) ---\n"
    "    _set_wave(44)\n"
    "    try:\n"
    "        assert WAVE_CONFIGS[44][\"a_seed_base\"] == pf.N1_BANDS[44][\"a\"][0], \\\n"
    "            \"W44 A band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[44][\"b_exit_seed_base\"] == \\\n"
    "            pf.N1_BANDS[44][\"b_exit\"][0], \"W44 B band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[44].get(\"engine_owner\") == \\\n"
    "            pf.N1_BANDS[44].get(\"engine_owner\") == \"bm-b\", \\\n"
    "            \"W44 engine_owner drift (law mirror parity)\"\n"
    "        w44_a = {A_SEED_BASE + j for j in range(A_N)}\n"
    "        w44_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}\n"
    "        assert not (w44_a & w44_b), \"W44 A/B band overlap\"\n"
    "        assert not (w44_a & reg_ints) and not (w44_b & reg_ints), \\\n"
    "            \"W44 hits SEED_REGISTRY\"\n"
    "        for nm, band in ((\"A\", w44_a), (\"B\", w44_b)):\n"
    "            assert not (band & v1_a) and not (band & v1_b), f\"W44 {nm} hits v1\"\n"
    "            assert not (band & w1_a) and not (band & w1_b), f\"W44 {nm} hits W1\"\n"
    "            assert not (band & probes), f\"W44 {nm} hits probe seeds\"\n"
    "        # prior-wave disjointness incl. W39/W40 (closed FULL-LIFECYCLE\n"
    "        # r343/r532: K=83,720 / K=85,920), W41/W42 (bm-c, finalized\n"
    "        # K=88,120 head 452,740 / K=90,320 head 454,940) and W43\n"
    "        # (bm-c, registered + burn in flight at this freeze --\n"
    "        # in-flight coexists by band disjointness).\n"
    "        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,\n"
    "                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,\n"
    "                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43):\n"
    "            assert not (w44_a & {WAVE_CONFIGS[wprev][\"a_seed_base\"] + j\n"
    "                                 for j in range(A_N)}), f\"W44 A hits W{wprev}\"\n"
    "            assert not (w44_b & {WAVE_CONFIGS[wprev][\"b_exit_seed_base\"] + j\n"
    "                                  for j in range(B_N)}), f\"W44 B hits W{wprev}\"\n"
    "        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,\n"
    "        # r529 bm-a adjudication row) -- W44 bands must clear it.\n"
    "        n3r1_used44 = set(range(70_000, 70_006))\n"
    "        assert not (w44_a & n3r1_used44) and not (w44_b & n3r1_used44), \\\n"
    "            \"W44 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)\"\n"
    "        # actual-draw-range avoidance (leg-3e family)\n"
    "        assert not (w44_a & lfc_actual12) and not (w44_b & lfc_actual12), \\\n"
    "            \"W44 bands must clear the lfc actual draw range\"\n"
    "        assert not (w44_a & options_actual12) and \\\n"
    "            not (w44_b & options_actual12), \\\n"
    "            \"W44 bands must clear the options_wave2 actual draw range\"\n"
    "        # band facts (law sec.4 W44 row, r533): BOTH tails arithmetic\n"
    "        # continuation clean exactly as the W43 row's W44+ WARNING\n"
    "        # projected (BOTH sides zero-skip; candidate == machine-derived\n"
    "        # per results/_r533bmb_w44_band_gate.py).\n"
    "        assert WAVE_CONFIGS[44][\"a_seed_base\"] == 131_004 == 131_003 + 1, \\\n"
    "            \"W44 A must start at the W43 A end + 1 (arithmetic continuation)\"\n"
    "        assert WAVE_CONFIGS[44][\"b_exit_seed_base\"] == 44_201 == 44_200 + 1, \\\n"
    "            \"W44 B must start at the W43 B end + 1 (arithmetic continuation)\"\n"
    "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W44-SHARD-0\",\n"
    "                                          \"n1w44-0of12\"), \"W44 entry identity\"\n"
    "        assert _entry_shard_of(11, 12) == (\"PERPETUAL-N1-W44-SHARD-11\",\n"
    "                                           \"n1w44-11of12\")\n"
    "        assert SHARD_DIR.endswith(\"n1_w44\") and OUT.endswith(\n"
    "            \"n1_w44_results.json\"), \"W44 path drift\"\n"
    "        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,\n"
    "                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,\n"
    "                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43):\n"
    "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(\n"
    "                PATHS.results_dir, \"p2cal_ext\",\n"
    "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\\n"
    "                f\"W44 shard dir collides with W{wprev}\"\n"
    "        assert os.path.exists(os.path.join(\n"
    "            PATHS.root, \"research\", \"PERPETUAL_N1_W44_PREREG.md\")), \\\n"
    "            \"W44 per-wave prereg missing (materializer requirement)\"\n"
    "        # W44 finalize cumulative deps: W17..W42 outputs ALL PRESENT\n"
    "        # (W40 finalize bm-b r532 K=85,920; W41 finalize bm-c r345\n"
    "        # K=88,120; W42 finalize bm-c r345 K=90,320 -- net ledger head\n"
    "        # 454,940); W43 (bm-c, burn in flight at this freeze) -- the\n"
    "        # dep pin carries the two-state honest note per the r541 W30\n"
    "        # precedent (finalize runtime composes every registry key\n"
    "        # below 44 = FAIL-CLOSED honest wait for the W43 output once\n"
    "        # it lands).\n"
    "        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,\n"
    "                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42):\n"
    "            assert os.path.exists(os.path.join(\n"
    "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\\n"
    "                f\"W44 finalize cumulative dep (W{_depw} output) missing\"\n"
    "        # finalize wave-set derivation face (r511 derive law): prior-wave\n"
    "        # set derives from registry keys below 44 (no 15; W43\n"
    "        # in-flight = runtime FAIL-CLOSED guard).\n"
    "        assert sorted(w for w in WAVE_CONFIGS if w < 44) == \\\n"
    "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,\n"
    "             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,\n"
    "             35, 36, 37, 38, 39, 40, 41, 42, 43], \\\n"
    "            \"W44 prior-wave set must derive from registry keys (no 15, incl. 43)\"\n"
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"\n"
    "    finally:\n"
    "        _set_wave(2)\n"
)
edit(
    "scripts/perpetual_faces_n1.py",
    "            \"W43 prior-wave set must derive from registry keys (no 15, incl. 42)\"\n"
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"\n"
    "    finally:\n"
    "        _set_wave(2)\n"
    "    # --- T-141 s2 lane face",
    "            \"W43 prior-wave set must derive from registry keys (no 15, incl. 42)\"\n"
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"\n"
    "    finally:\n"
    "        _set_wave(2)\n" + LEG44 + "    # --- T-141 s2 lane face",
    "C selftest W44 leg",
)

# ---------- D. selftest print W44 face desc ----------
DESC44 = (
    "          \"+ W44 materializer face [same guard set, dep=W17..W42 ALL \"\n"
    "          \"present (W40 finalize bm-b r532 K=85,920, ledger 450,540; \"\n"
    "          \"W41 finalize bm-c r345 K=88,120 ledger 452,740; W42 finalize \"\n"
    "          \"bm-c r345 K=90,320 ledger 454,940 -- chain head at freeze; \"\n"
    "          \"W43 bm-c burn-in-flight two-state dep -- finalize runtime \"\n"
    "          \"FAIL-CLOSED composes every registry key below 44), BOTH \"\n"
    "          \"tails arithmetic continuation clean per law sec.4 W44 \"\n"
    "          \"row 131_004..133_003 / 44_201..44_400 (W43 row W44+ WARNING \"\n"
    "          \"projection verified machine-side, zero skip both sides, \"\n"
    "          \"ADMIT receipt results/_r533bmb_w44_band_gate.py), THIRTY-\"\n"
    "          \"FOURTH ENGINE-OWNED WAVE engine_owner=bm-b per engine \"\n"
    "          \"de-throttle law O-20261001-2355 sec.2 own-continuous-series \"\n"
    "          \"(zero-gap relay after the W40 full closeout, wave 44 = first \"\n"
    "          \"free number after bm-c's W43 claim), r533 bm-b] \"\n"
)
edit(
    "scripts/perpetual_faces_n1.py",
    "          \"+ T-141 s2 \"",
    DESC44 + "          \"+ T-141 s2 \"",
    "D selftest print W44 desc",
)

# ---------- E. canon law row 44 (research/PERPETUAL_FACES.md) ----------
ROW44MD = (
    "- N1 波44（r533 bm-b 冻·prereg 时展行）：**第三十四枚引擎波·bm-b 第十四枚自有波**"
    "（W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/W36/W38/W40 后第十四枚）"
    "·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W43 合同"
    "·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**"
    "·【本机上波=W40 同窗全生命周期收官 r532（finalize one-pass K=85,920·账本链头 450,540·"
    "prereg s7/s8 回填齐）·W41/W42=bm-c 已收官（K=88,120·链头 452,740／K=90,320·链头 454,940）·"
    "W43=bm-c r346 冻结·烧录在飞（finalize 待落·带域不相交=异带共存 r531 律）"
    "→零隔接力·波号 44=W43 行落账后首个自由号·r511 表尾锁例冻结前 fetch 实核表尾时 W44 号位净空·"
    "first-free-number 法】·【never-dry 供给律常设步·r533 实况=引擎活·status exit 0·"
    "队列空（W40 收口后 02:59 起 idle）·同窗 LOWAMP-P3-NULLS 池批在飞（bm-b daemon 认领·"
    "r532 律禁手工翻池）·禁空转禁等 CEO 提醒】·"
    "A-ext seed=**131_004..133_003**（**A 面算术顺延**·=W43 A 尾 131_003+1·步长逐字·**零跳位**·"
    "【机证净空**registry-derive**——候选位注册表 derive 非散布带间·leg1-A/leg2-A 机证"
    "==W43 行公示投影 CLEAN==候选】·扫描面=pre-W44 四十二行 N1 带表"
    "【含 W39 行 121_004..123_003/43_001..43_200（r342 bm-c·finalize 实落账 K=83,720）·"
    "W40 行 123_004..125_003/43_201..43_400（r531 bm-b·finalize 实落账 K=85,920·链头 450,540）·"
    "W41 行 125_004..127_003/43_401..43_600（r344 bm-c·finalize 实落账 K=88,120·链头 452,740）·"
    "W42 行 127_004..129_003/43_601..43_800（r345 bm-c·finalize 实落账 K=90,320·链头 454,940）·"
    "W43 行 129_004..131_003/44_001..44_200（r346 bm-c·烧录在飞=注册在用面·带域不相交=异带共存 r531 律）】"
    "·W1 ext·v1 在用带·SEED_REGISTRY 全集·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·"
    "**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·"
    "N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·"
    "lfc 实际抽带 30_000..30_099·options_wave2 实际抽带 63_000..63_049·leg-3e 实际流避让】·"
    "**ADMIT 回执=results/_r533bmb_w44_band_gate.py**·r533 bm-b 起草窗实跑"
    "【leg0 四十二行+候选注册面校验+leg0b W43 行 W44+ 警示 prose 在场校验+"
    "leg1-A registry-derive 算术面 CLEAN 机证+leg1-B 算术面 CLEAN 机证+"
    "leg2-A 首净窗=候选**零跳位**·leg2-B 首净窗=候选**零跳位**·"
    "leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验**非重挑 R250·"
    "W44 带从未指派·测量面零结果可钓**】·"
    "B-ext exit seed=**44_201..44_400**（**B 面算术顺延**·=W43 B 尾 44_200+1·步长逐字·**零跳位**·"
    "【机证净空**registry-derive**——leg1-B/leg2-B 机证==W43 行公示投影 CLEAN==候选·"
    "两侧独立裁定如实披露·A/B 双侧零跳位】）。"
    "**N2/N4 让位注记**：本波 A 带 131_004..133_003——N2/N4 波级 prereg 冻结时按本表防撞律回避该域。"
    "**W45+ 警示**：A +2_000 算术位（133_004..135_003）与 B +200 算术位（44_401..44_600）"
    "投影以 r533 带闸回执 W45+ 投影腿机证为准（机闸 derive 非 prose 转抄·r535 律·"
    "去节流令下号位=上枚行落账后首个自由号·见§5 账本·跨波累计 N_eff 恒不重置）。\n"
)
p = "research/PERPETUAL_FACES.md"
b = open(p, "rb").read().decode("utf-8")
lines = b.split("\n")
idx = None
for i, l in enumerate(lines):
    if l.startswith("- N1 ") and "129_004..131_003" in l and "44_001..44_200" in l:
        idx = i
        break
assert idx is not None, "E: W43 canon row not found"
lines.insert(idx + 1, ROW44MD.rstrip("\n"))
open(p, "wb").write("\n".join(lines).encode("utf-8"))
print("E canon W44 row: OK (inserted after line %d)" % (idx + 1))

print("ALL EDITS DONE")
