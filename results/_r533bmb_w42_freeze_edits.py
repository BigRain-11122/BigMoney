"""W42 FREEZE working-tree edits (r533 bm-b, bytes-safe per r530 law).

Inserts (exact-anchor, assert-found-once):
  A. scripts/perpetual_faces.py        -> N1_BANDS row 42 (+comment block)
  B. scripts/perpetual_faces_n1.py     -> WAVE_CONFIGS[42] (+comment block)
  C. scripts/perpetual_faces_n1.py     -> selftest W42 materializer face leg
  D. scripts/perpetual_faces_n1.py     -> selftest print W42 face desc
  E. research/PERPETUAL_FACES.md       -> law sec.4 W42 row (after W41 row)

Prereg + band-gate scripts are separate files (write_file direct).
"""
import io, sys

def edit(path, old, new, tag):
    b = open(path, "rb").read().decode("utf-8")
    n = b.count(old)
    assert n == 1, f"{tag}: anchor count {n} != 1"
    open(path, "wb").write(b.replace(old, new).encode("utf-8"))
    print(f"{tag}: OK")

# ---------- A. N1_BANDS row 42 (scripts/perpetual_faces.py) ----------
ROW42 = (
    "    # W42 (r533 bm-b, own-series continuation per O-20261001-2355\n"
    "    # sec.2 -- bm-b's FOURTEENTH owned wave; zero-gap relay after\n"
    "    # the W40 FULL CLOSEOUT (freeze r531 -> 12/12 burn -> finalize\n"
    "    # r532 one-pass K=85,920, ledger 450,540 chain head; products\n"
    "    # delivered origin db5110d55). Wave 42 = first free number\n"
    "    # after bm-c's W41 landed claim (r344, burn in flight at this\n"
    "    # freeze). SIDES INDEPENDENTLY ADJUDICATED per the W41 row's\n"
    "    # W42+ WARNING: A tail arithmetic continuation no skip\n"
    "    # (127_004..129_003 == W41 A end + 1); B tail arithmetic\n"
    "    # continuation no skip (43_601..43_800 == W41 B end + 1).\n"
    "    # Machine-verified at prereg time (results/_r533bmb_w42_band_gate.py\n"
    "    # ADMIT receipt vs the 39-row pre-W42 table + live SEED_REGISTRY\n"
    "    # values + probe-seed cluster 95_000..95_003 r335 discovery leg +\n"
    "    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 mandatory\n"
    "    # leg; origin slot vacancy machine-checked). THIRTY-SECOND\n"
    "    # ENGINE-OWNED WAVE, engine_owner=bm-b (local queue, no pool\n"
    "    # entry). NOT a re-pick (R250: W42 bands never assigned).\n"
    "    42: {\"a\": (127_004, 129_003), \"b_exit\": (43_601, 43_800),\n"
    "         \"engine_owner\": \"bm-b\"},\n"
)
edit(
    "scripts/perpetual_faces.py",
    "    41: {\"a\": (125_004, 127_003), \"b_exit\": (43_401, 43_600),\n"
    "         \"engine_owner\": \"bm-c\"},\n}",
    "    41: {\"a\": (125_004, 127_003), \"b_exit\": (43_401, 43_600),\n"
    "         \"engine_owner\": \"bm-c\"},\n" + ROW42 + "}",
    "A registry row 42",
)

# ---------- B. WAVE_CONFIGS[42] (scripts/perpetual_faces_n1.py) ----------
CFG42 = (
    "                  # W42 (r533 bm-b, own-series continuation per O-20261001-2355\n"
    "                  # sec.2 -- bm-b's FOURTEENTH owned wave; zero-gap relay after\n"
    "                  # the W40 FULL CLOSEOUT (freeze r531 -> 12/12 burn ->\n"
    "                  # finalize r532 one-pass K=85,920, ledger 450,540; prereg\n"
    "                  # s7/s8 backfilled r532). Wave 42 = first free number\n"
    "                  # after bm-c's W41 landed claim (r344, burn in flight at\n"
    "                  # this freeze). SIDES INDEPENDENTLY ADJUDICATED per the\n"
    "                  # W41 row's W42+ WARNING: A tail arithmetic continuation\n"
    "                  # no skip (127_004..129_003 == W41 A end + 1); B tail\n"
    "                  # arithmetic continuation no skip (43_601..43_800 == W41\n"
    "                  # B end + 1). Machine-verified at prereg time\n"
    "                  # (results/_r533bmb_w42_band_gate.py ADMIT receipt vs the\n"
    "                  # 39-row pre-W42 table + live SEED_REGISTRY values +\n"
    "                  # probe-seed cluster 95_000..95_003 r335 discovery leg +\n"
    "                  # N3-R1 used-seed band 70_000..70_005 MSG-183x r529\n"
    "                  # mandatory leg; origin slot vacancy machine-checked).\n"
    "                  # THIRTY-SECOND ENGINE-OWNED WAVE, engine_owner=bm-b\n"
    "                  # (local queue, no pool entry). NOT a re-pick (R250: W42\n"
    "                  # bands were never assigned).\n"
    "                  42: {\"batch\": \"PERPETUAL-N1-W42\",\n"
    "                       \"prereg\": (\"research/PERPETUAL_N1_W42_PREREG.md (wave-level frozen \"\n"
    "                                  \"pre-run; design = frozen v1 null calibration verbatim, \"\n"
    "                                  \"new seed bands only; THIRTY-SECOND ENGINE-OWNED WAVE, \"\n"
    "                                  \"own-series continuation per O-20261001-2355 sec.2 \"\n"
    "                                  \"(seat system terminated, first-free-number law), \"\n"
    "                                  \"engine_owner=bm-b, A tail arithmetic continuation \"\n"
    "                                  \"from the registered W41 row no skip, B tail \"\n"
    "                                  \"arithmetic continuation from the registered W41 \"\n"
    "                                  \"row no skip per the W41 row W42+ WARNING projection \"\n"
    "                                  \"(both sides CLEAN, machine-derived at this freeze))\"),\n"
    "                       \"a_seed_base\": 127_004,        # law sec.4 W42 A: 127_004..129_003 (arithmetic)\n"
    "                       \"b_exit_seed_base\": 43_601,    # law sec.4 W42 B: 43_601..43_800 (arithmetic)\n"
    "                       \"shard_subdir\": \"n1_w42\", \"out_name\": \"n1_w42_results.json\",\n"
    "                       \"engine_owner\": \"bm-b\"},\n"
)
edit(
    "scripts/perpetual_faces_n1.py",
    "                       \"engine_owner\": \"bm-c\"},\n"
    "                 }",
    "                       \"engine_owner\": \"bm-c\"},\n" + CFG42 + "                 }",
    "B WAVE_CONFIGS 42",
)

# ---------- C. selftest W42 materializer face leg ----------
LEG42 = (
    "    # --- W42 materializer face (r533 bm-b freeze, own-series law\n"
    "    #     O-20261001-2355 sec.2 -- bm-b's FOURTEENTH owned wave after\n"
    "    #     W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/W36/W38/W40;\n"
    "    #     zero-gap relay after the W40 FULL CLOSEOUT: freeze r531 ->\n"
    "    #     12/12 burn -> finalize r532 one-pass K=85,920, ledger\n"
    "    #     450,540 chain head; W41 = bm-c lineage, burn in flight at\n"
    "    #     this freeze -- in-flight coexists by band disjointness) ---\n"
    "    _set_wave(42)\n"
    "    try:\n"
    "        assert WAVE_CONFIGS[42][\"a_seed_base\"] == pf.N1_BANDS[42][\"a\"][0], \\\n"
    "            \"W42 A band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[42][\"b_exit_seed_base\"] == \\\n"
    "            pf.N1_BANDS[42][\"b_exit\"][0], \"W42 B band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[42].get(\"engine_owner\") == \\\n"
    "            pf.N1_BANDS[42].get(\"engine_owner\") == \"bm-b\", \\\n"
    "            \"W42 engine_owner drift (law mirror parity)\"\n"
    "        w42_a = {A_SEED_BASE + j for j in range(A_N)}\n"
    "        w42_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}\n"
    "        assert not (w42_a & w42_b), \"W42 A/B band overlap\"\n"
    "        assert not (w42_a & reg_ints) and not (w42_b & reg_ints), \\\n"
    "            \"W42 hits SEED_REGISTRY\"\n"
    "        for nm, band in ((\"A\", w42_a), (\"B\", w42_b)):\n"
    "            assert not (band & v1_a) and not (band & v1_b), f\"W42 {nm} hits v1\"\n"
    "            assert not (band & w1_a) and not (band & w1_b), f\"W42 {nm} hits W1\"\n"
    "            assert not (band & probes), f\"W42 {nm} hits probe seeds\"\n"
    "        # prior-wave disjointness incl. W39 (bm-c, closed FULL-LIFECYCLE\n"
    "        # r342/r343: finalize one-pass K=83,720, ledger 448,340), W40\n"
    "        # (bm-b, closed FULL-LIFECYCLE r532: finalize one-pass K=85,920,\n"
    "        # ledger 450,540) and W41 (bm-c, registered + burn in flight\n"
    "        # at this freeze -- in-flight coexists by band disjointness).\n"
    "        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,\n"
    "                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,\n"
    "                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41):\n"
    "            assert not (w42_a & {WAVE_CONFIGS[wprev][\"a_seed_base\"] + j\n"
    "                                 for j in range(A_N)}), f\"W42 A hits W{wprev}\"\n"
    "            assert not (w42_b & {WAVE_CONFIGS[wprev][\"b_exit_seed_base\"] + j\n"
    "                                  for j in range(B_N)}), f\"W42 B hits W{wprev}\"\n"
    "        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,\n"
    "        # r529 bm-a adjudication row) -- W42 bands must clear it.\n"
    "        n3r1_used42 = set(range(70_000, 70_006))\n"
    "        assert not (w42_a & n3r1_used42) and not (w42_b & n3r1_used42), \\\n"
    "            \"W42 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)\"\n"
    "        # actual-draw-range avoidance (leg-3e family)\n"
    "        assert not (w42_a & lfc_actual12) and not (w42_b & lfc_actual12), \\\n"
    "            \"W42 bands must clear the lfc actual draw range\"\n"
    "        assert not (w42_a & options_actual12) and \\\n"
    "            not (w42_b & options_actual12), \\\n"
    "            \"W42 bands must clear the options_wave2 actual draw range\"\n"
    "        # band facts (law sec.4 W42 row, r533): BOTH tails arithmetic\n"
    "        # continuation clean exactly as the W41 row's W42+ WARNING\n"
    "        # projected (BOTH sides zero-skip; candidate == machine-derived\n"
    "        # per results/_r533bmb_w42_band_gate.py).\n"
    "        assert WAVE_CONFIGS[42][\"a_seed_base\"] == 127_004 == 127_003 + 1, \\\n"
    "            \"W42 A must start at the W41 A end + 1 (arithmetic continuation)\"\n"
    "        assert WAVE_CONFIGS[42][\"b_exit_seed_base\"] == 43_601 == 43_600 + 1, \\\n"
    "            \"W42 B must start at the W41 B end + 1 (arithmetic continuation)\"\n"
    "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W42-SHARD-0\",\n"
    "                                          \"n1w42-0of12\"), \"W42 entry identity\"\n"
    "        assert _entry_shard_of(11, 12) == (\"PERPETUAL-N1-W42-SHARD-11\",\n"
    "                                           \"n1w42-11of12\")\n"
    "        assert SHARD_DIR.endswith(\"n1_w42\") and OUT.endswith(\n"
    "            \"n1_w42_results.json\"), \"W42 path drift\"\n"
    "        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,\n"
    "                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,\n"
    "                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41):\n"
    "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(\n"
    "                PATHS.results_dir, \"p2cal_ext\",\n"
    "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\\n"
    "                f\"W42 shard dir collides with W{wprev}\"\n"
    "        assert os.path.exists(os.path.join(\n"
    "            PATHS.root, \"research\", \"PERPETUAL_N1_W42_PREREG.md\")), \\\n"
    "            \"W42 per-wave prereg missing (materializer requirement)\"\n"
    "        # W42 finalize cumulative deps: W17..W40 outputs ALL PRESENT\n"
    "        # (W37 finalize bm-c r342 K=79,320; W38 finalize bm-b r530\n"
    "        # K=81,520; W39 finalize bm-c r343 K=83,720; W40 finalize\n"
    "        # bm-b r532 K=85,920 -- net ledger head 450,540); W41 (bm-c,\n"
    "        # burn in flight at this freeze) -- the dep pin carries the\n"
    "        # two-state honest note per the r541 W30 precedent (finalize\n"
    "        # runtime composes every registry key below 42 = FAIL-CLOSED\n"
    "        # honest wait for the W41 output once it lands).\n"
    "        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,\n"
    "                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40):\n"
    "            assert os.path.exists(os.path.join(\n"
    "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\\n"
    "                f\"W42 finalize cumulative dep (W{_depw} output) missing\"\n"
    "        # finalize wave-set derivation face (r511 derive law): prior-wave\n"
    "        # set derives from registry keys below 42 (no 15; W41\n"
    "        # in-flight = runtime FAIL-CLOSED guard).\n"
    "        assert sorted(w for w in WAVE_CONFIGS if w < 42) == \\\n"
    "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,\n"
    "             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,\n"
    "             35, 36, 37, 38, 39, 40, 41], \\\n"
    "            \"W42 prior-wave set must derive from registry keys (no 15, incl. 41)\"\n"
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"\n"
    "    finally:\n"
    "        _set_wave(2)\n"
)
edit(
    "scripts/perpetual_faces_n1.py",
    "            \"W41 prior-wave set must derive from registry keys (no 15, incl. 40)\"\n"
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"\n"
    "    finally:\n"
    "        _set_wave(2)\n"
    "    # --- T-141 s2 lane face",
    "            \"W41 prior-wave set must derive from registry keys (no 15, incl. 40)\"\n"
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"\n"
    "    finally:\n"
    "        _set_wave(2)\n" + LEG42 + "    # --- T-141 s2 lane face",
    "C selftest W42 leg",
)

# ---------- D. selftest print W42 face desc ----------
DESC42 = (
    "          \"+ W42 materializer face [same guard set, dep=W17..W40 ALL \"\n"
    "          \"present (W40 finalize bm-b r532 K=85,920, ledger 450,540 \"\n"
    "          \"chain-linear; W41 bm-c burn-in-flight two-state dep -- \"\n"
    "          \"finalize runtime FAIL-CLOSED composes every registry key \"\n"
    "          \"below 42), BOTH tails arithmetic continuation clean per \"\n"
    "          \"law sec.4 W42 row 127_004..129_003 / 43_601..43_800 (W41 \"\n"
    "          \"row W42+ WARNING projection verified machine-side, zero \"\n"
    "          \"skip both sides, ADMIT receipt \"\n"
    "          \"results/_r533bmb_w42_band_gate.py), THIRTY-SECOND \"\n"
    "          \"ENGINE-OWNED WAVE engine_owner=bm-b per engine de-throttle \"\n"
    "          \"law O-20261001-2355 sec.2 own-continuous-series (zero-gap \"\n"
    "          \"relay after the W40 full closeout, wave 42 = first free \"\n"
    "          \"number after bm-c's W41 claim), r533 bm-b] \"\n"
)
edit(
    "scripts/perpetual_faces_n1.py",
    "          \"+ T-141 s2 \"",
    DESC42 + "          \"+ T-141 s2 \"",
    "D selftest print W42 desc",
)

# ---------- E. canon law row 42 (research/PERPETUAL_FACES.md) ----------
ROW42MD = (
    "- N1 波42·r533 bm-b 冻结窗展开行。**第三十二枚引擎波·bm-b 第十四枚自有波**"
    "（W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/W36/W38/W40 后第十四枚）"
    "·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W41 原样适用"
    "（本地队列烧录·免预注册·免预认领·cmd_supply 拒绝投放）。"
    "**引擎去节流令 O-20261001-2355 §二执行=座位系已废**"
    "——上游收口=W40 同窗全生命周期收口"
    "（r531 冻结→12/12 烧录→r532 finalize one-pass K=85,920·链头 450,540·"
    "prereg s7/s8 已回填）→本行 42=W41 公示认领后首个自由号"
    "（r511 表尾锁律：冻结前 fetch 实核表尾时 W42 号位净空·first-free-number 法·"
    "never-dry 供给律常设步·r533 实况=引擎活〔status exit 0〕）。"
    "W39/W40 12/12 在库·W41 bm-c 注册在飞（r344·带域不相交=异带共存 r531 律）·"
    "同窗 LOWAMP-P3 bm-a 池批在飞=池面勿扰如实披露·资源现状转不拖 CEO 审批。"
    "A-ext seed=**127_004..129_003**（**A 尾算术顺延**·==W41 A 尾 127_003+1·"
    "无跳位·**净空**机器验证·**registry-derive**）·"
    "扫描面=pre-W42 三十九行 N1 带表"
    "（含 W37 行 117_004..119_003/42_401..42_600〔r341 bm-c·finalize 已落账 K=79,320〕·"
    "W38 行 119_004..121_003/42_601..42_800〔r529 bm-b·finalize 已落账 K=81,520〕·"
    "W39 行 121_004..123_003/43_001..43_200〔r342 bm-c·finalize 已落账 K=83,720·链头 448,340〕·"
    "W40 行 123_004..125_003/43_201..43_400〔r531 bm-b·finalize 已落账 K=85,920·链头 450,540〕·"
    "W41 行 125_004..127_003/43_401..43_600〔r344 bm-c·注册在飞=注册在用面·带域不相交=异带共存 r531 律〕）"
    "＋W1 ext＋v1 在用带＋SEED_REGISTRY 全值〔161 值·扫描机验证〕＋"
    "**N3-R1 实际种子带 70_000..70_005**〔r529 裁定强制腿〕＋"
    "**runner 探针种子簇 95_000..95_003**〔r335 发现腿·W26 起强制〕＋"
    "N2/N4 设计探针保留点 40_000/40_001＋N2-W15 草案探针点 31_000/31_500/32_000＋"
    "lfc 实际流 30_000..30_099＋options_wave2 实际流 63_000..63_049〔leg-3e 实际流避让腿〕·"
    "**ADMIT 回执=results/_r533bmb_w42_band_gate.py**〔r533 bm-b 起草窗实跑·"
    "leg0 三十九行+候选注册面校验+leg0b W41 行 W42+ 警示 prose 在场校验+"
    "leg1-A/leg1-B registry-derive 算术窗==公示投影==候选+"
    "leg2 首净窗==候选双带零跳位+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验〕·"
    "**律 R250**·W42 带从未指派·非重挑。"
    "B-ext exit seed=**43_601..43_800**（**B 尾算术顺延**·==W41 B 尾 43_600+1·无跳位·"
    "**净空**机器验证·**registry-derive**·leg1-B/leg2-B 验证==W41 行公示投影 CLEAN==候选·"
    "双侧独立裁定如实披露）·**N2/N4 号位注记**：未来 A 带 127_004..129_003·"
    "N2/N4 未来 prereg 展行时须扫描此带不可回归。"
    "**W43+ 警示**：A +2_000 算术位 129_004..131_003；B +200 算术位 43_801..44_000·"
    "为 r533 带闸投影**跨示警窗以带闸 derive 为准（带闸 derive 非 prose 转抄·r535 律）**·"
    "去节流令下号位=本波全生命周期收口后首个自由号。〔§5 跨波累计 N_eff 恒不重置〕\n"
)
p = "research/PERPETUAL_FACES.md"
b = open(p, "rb").read().decode("utf-8")
lines = b.split("\n")
idx = None
for i, l in enumerate(lines):
    if l.startswith("- N1 ") and "125_004..127_003" in l and "127_004..129_003" in l:
        idx = i
        break
assert idx is not None, "E: W41 canon row not found"
lines.insert(idx + 1, ROW42MD.rstrip("\n"))
open(p, "wb").write("\n".join(lines).encode("utf-8"))
print("E canon W42 row: OK (inserted after line %d)" % (idx + 1))

print("ALL EDITS DONE")
