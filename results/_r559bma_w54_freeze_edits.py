# -*- coding: utf-8 -*-
"""r559 bm-a W54 freeze: land N1_BANDS/WAVE_CONFIGS/selftest-leg/canon-row edits.

Bytes-safe (r530): decode utf-8, exact-anchor str replace, encode back.
Every anchor asserted UNIQUE before replace. Inserted text EOL-normalized
to each file's dominant ending. Idempotent skip per landed marker.
"""
import sys

def load(fp):
    b = open(fp, "rb").read()
    t = b.decode("utf-8")
    eol = "\r\n" if t.count("\r\n") * 2 > t.count("\n") else "\n"
    return t, eol

def save(fp, t, eol):
    open(fp, "wb").write(t.encode("utf-8"))

def rep(t, old, new, eol, tag):
    old = old.replace("\n", eol)
    new = new.replace("\n", eol)
    assert t.count(old) == 1, f"{tag}: anchor not unique ({t.count(old)})"
    return t.replace(old, new)

# ---------------- edit 1: perpetual_faces.py N1_BANDS[54] -------------------
FP1 = r"scripts\perpetual_faces.py"
t1, eol1 = load(FP1)
if '54: {"a": (151_004' in t1:
    print("edit1 already landed (idempotent skip)")
else:
    A1 = ('    53: {"a": (149_004, 151_003), "b_exit": (46_401, 46_600),\n'
          '         "engine_owner": "bm-c"},\n'
          '}')
    NEW54_BANDS = ('    53: {"a": (149_004, 151_003), "b_exit": (46_401, 46_600),\n'
                   '         "engine_owner": "bm-c"},\n'
                   '    # FORTY-THIRD ENGINE-OWNED WAVE (r559 bm-a freeze): bm-a\'s\n'
                   '    # THIRTEENTH owned wave. Wave 54 = next free number after the\n'
                   '    # registered W53 row (own-series continuation under the\n'
                   '    # de-throttle law; bm-a\'s previous wave W48 closed\n'
                   '    # full-lifecycle at r558 -- seat-loss re-derive finalize\n'
                   '    # K=103,520; W53 bm-c registered with finalize in flight --\n'
                   '    # coexist by band disjointness per r531 law).\n'
                   '    # BOTH SIDES = ARITHMETIC CONTINUATION from the W53 row tail,\n'
                   '    # no skip: A 151_004..153_003 (= W53 A end 151_003 + 1) and\n'
                   '    # B 46_601..46_800 (= W53 B end 46_600 + 1) -- both windows\n'
                   '    # CLEAN per the W53 row W54+ WARNING projections\n'
                   '    # (three-machine cross-validation: bm-c r351 freeze gate +\n'
                   '    # bm-b r559 yield-window gate + this freeze\'s machine\n'
                   '    # re-derive, r535 law). Machine-verified at prereg time\n'
                   '    # (results/_r559bma_w54_band_gate.py ADMIT receipt vs the\n'
                   '    # 51-row pre-W54 table + live SEED_REGISTRY values + probe\n'
                   '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
                   '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
                   '    # slot vacancy machine-checked). NOT a re-pick (R250: W54\n'
                   '    # bands were never assigned).\n'
                   '    54: {"a": (151_004, 153_003), "b_exit": (46_601, 46_800),\n'
                   '         "engine_owner": "bm-a"},\n'
                   '}')
    t1 = rep(t1, A1, NEW54_BANDS, eol1, "pf-bands")
    save(FP1, t1, eol1)
    print("edit1 perpetual_faces.py N1_BANDS[54] landed")

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[54] --------------
FP2 = r"scripts\perpetual_faces_n1.py"
t2, eol2 = load(FP2)
if '54: {"batch": "PERPETUAL-N1-W54"' in t2:
    print("edit2 already landed (idempotent skip)")
else:
    A2 = ('                            "shard_subdir": "n1_w53", "out_name": "n1_w53_results.json",\n'
          '                            "engine_owner": "bm-c"},\n'
          '                       }')
    ENTRY54 = ('                            "shard_subdir": "n1_w53", "out_name": "n1_w53_results.json",\n'
               '                            "engine_owner": "bm-c"},\n'
               '                       54: {"batch": "PERPETUAL-N1-W54",\n'
               '                            "prereg": ("research/PERPETUAL_N1_W54_PREREG.md (wave-level frozen "\n'
               '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
               '                                       "new seed bands only; FORTY-THIRD ENGINE-OWNED WAVE, "\n'
               '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
               '                                       "(first-free-number law), engine_owner=bm-a, wave 54 = "\n'
               '                                       "next free number after the registered W53 row, BOTH "\n'
               '                                       "SIDES ARITHMETIC CONTINUATION no skip (A "\n'
               '                                       "151_004..153_003, B 46_601..46_800); W1..W52 finalizes "\n'
               '                                       "ALL LANDED at this freeze (ledger head 478,948), W53 "\n'
               '                                       "registered with finalize NOT landed = ONE in-flight "\n'
               '                                       "upstream seat, finalize merge loop derives the wave "\n'
               '                                       "set from registry keys at run time and stays "\n'
               '                                       "FAIL-CLOSED on any not-yet-finalized upstream seat, "\n'
               '                                       "r307 two-state law)"),\n'
               '                            "a_seed_base": 151_004,        # law sec.4 W54 A: 151_004..153_003 (arithmetic continuation)\n'
               '                            "b_exit_seed_base": 46_601,    # law sec.4 W54 B: 46_601..46_800 (arithmetic continuation)\n'
               '                            "shard_subdir": "n1_w54", "out_name": "n1_w54_results.json",\n'
               '                            "engine_owner": "bm-a"},\n'
               '                       }')
    t2 = rep(t2, A2, ENTRY54, eol2, "n1-configs")
    save(FP2, t2, eol2)
    print("edit2 WAVE_CONFIGS[54] landed")

# ---------------- edit 3: perpetual_faces_n1.py selftest W54 leg --------------
LEG54 = '''
    # --- W54 materializer face (r559 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-a's THIRTEENTH owned wave; wave 54 = next free number
    #     after the registered W53 row (bm-a's previous wave W48
    #     closed full-lifecycle at r558 -- seat-loss re-derive
    #     finalize K=103,520; W53 bm-c registered with finalize
    #     NOT landed at this freeze = ONE in-flight upstream seat,
    #     finalize merge loop FAIL-CLOSED at run time per r307
    #     two-state law). BOTH SIDES ARITHMETIC CONTINUATION from
    #     the W53 tail no skip (A 151_004..153_003 / B
    #     46_601..46_800, both CLEAN == the W53 row W54+ published
    #     projection verbatim -- three-machine cross-validation
    #     (bm-c r351 + bm-b r559 + this gate); ADMIT receipt
    #     results/_r559bma_w54_band_gate.py; not a re-pick -- R250:
    #     W54 bands were never assigned) --
    _set_wave(54)
    try:
        assert WAVE_CONFIGS[54]["a_seed_base"] == pf.N1_BANDS[54]["a"][0], \\
            "W54 A band drift vs law mirror"
        assert WAVE_CONFIGS[54]["b_exit_seed_base"] == \\
            pf.N1_BANDS[54]["b_exit"][0], "W54 B band drift vs law mirror"
        assert WAVE_CONFIGS[54].get("engine_owner") == \\
            pf.N1_BANDS[54].get("engine_owner") == "bm-a", \\
            "W54 engine_owner drift (law mirror parity)"
        w54_a = {A_SEED_BASE + j for j in range(A_N)}
        w54_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w54_a & w54_b), "W54 A/B band overlap"
        assert not (w54_a & reg_ints) and not (w54_b & reg_ints), \\
            "W54 hits SEED_REGISTRY"
        for nm, band in (("A", w54_a), ("B", w54_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W54 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W54 {nm} hits W1"
            assert not (band & probes), f"W54 {nm} hits probe seeds"
        # prior-wave disjointness incl. W48/W49/W50/W51/W52/W53 (all
        # registered; W53 finalize in flight -- coexist by band
        # disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53):
            assert not (w54_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W54 A hits W{wprev}"
            assert not (w54_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W54 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W54 clears it.
        n3r1_used54 = set(range(70_000, 70_006))
        assert not (w54_a & n3r1_used54) and not (w54_b & n3r1_used54), \\
            "W54 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w54_a & lfc_actual12) and not (w54_b & lfc_actual12), \\
            "W54 bands must clear the lfc actual draw range"
        assert not (w54_a & options_actual12) and \\
            not (w54_b & options_actual12), \\
            "W54 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W54 row, r559): BOTH SIDES
        # ARITHMETIC CONTINUATION (A 151_004 = W53 A end 151_003 + 1;
        # B 46_601 = W53 B end 46_600 + 1, both windows CLEAN -- no
        # skip family).
        assert WAVE_CONFIGS[54]["a_seed_base"] == 151_004 == 151_003 + 1, \\
            "W54 A must start at the registered W53 A end + 1 " \\
            "(arithmetic continuation window 151_004..153_003 CLEAN -- " \\
            "no skip family)"
        assert WAVE_CONFIGS[54]["b_exit_seed_base"] == 46_601 == 46_600 + 1, \\
            "W54 B must start at the registered W53 B end + 1 " \\
            "(arithmetic continuation window 46_601..46_800 CLEAN -- " \\
            "no skip family)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W54-SHARD-0",
                                          "n1w54-0of12"), "W54 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W54-SHARD-11",
                                          "n1w54-11of12")
        assert SHARD_DIR.endswith("n1_w54") and OUT.endswith(
            "n1_w54_results.json"), "W54 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W54 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W54_PREREG.md")), \\
            "W54 per-wave prereg missing (materializer requirement)"
        # W54 finalize cumulative deps: W17..W52 outputs ALL PRESENT
        # (static landed seats -- W48 landed r558 bm-a seat-loss
        # re-derive, W49 landed bm-b r558, W50/W51/W52 landed bm-c
        # r351 triple finalize); W53 = REGISTERED with finalize NOT
        # landed at this freeze (ONE in-flight upstream seat -- the
        # finalize merge loop derives the wave set from registry keys
        # at run time and stays FAIL-CLOSED on any not-yet-finalized
        # upstream seat, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W54 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 54 (no 15; incl.
        # 48/49/50/51/52/53 -- all registered, W53 finalize in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 54) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53], \\
            "W54 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48/49/50/51/52/53)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
# reload after edit 2
t2b, eol2b = load(FP2)
if "W54 materializer face" in t2b:
    print("edit3 already landed (idempotent skip)")
else:
    A3 = "\n    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim"
    LEG54X = LEG54.replace("\n", eol2b)
    A3X = A3.replace("\n", eol2b)
    assert t2b.count(A3X) == 1, f"selftest anchor not unique: {t2b.count(A3X)}"
    t2b = t2b.replace(A3X, LEG54X + A3X)
    save(FP2, t2b, eol2b)
    print("edit3 selftest W54 leg landed")

# ---------------- edit 4: PERPETUAL_FACES.md canon W54 row -------------------
ROW54 = """
- N1 波54（r559 bm-a 冻·prereg 时展行）：**第四十三枚引擎波·bm-a 第十三枚自有波**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W53 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启·W44/W45/W48 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**本机上波 W48 已全生命周期收官**（r557 冻结→tick 12/12 烧毕→r558 落账序让路-重derive finalize one-pass prev=470,148·total 472,348·K=103,520·bm-a 首例）→**波号 54=注册表 W53 行后首个自由号**·r511 表尾锁例冻结前 fetch 实核表尾时 W54 号位净空】·**分面 derive（r535 机闸 derive 律·r307 波带尾律）**：W53 行 W54+ 警示投影 **A 151_004..153_003 CLEAN／B 46_601..46_800 CLEAN**（三机互证：bm-c r351 冻结窗 gate 投影腿＋bm-b r559 让路窗 gate 投影腿＋本波 bm-a gate 复核逐字同）→本波 **A-ext seed=151_004..153_003**（**A 面算术续带零跳位**==W53 A 尾 151_003+1·步长逐字）·**B-ext exit seed=46_601..46_800**（**B 面算术续带零跳位**==W53 B 尾 46_600+1·步长逐字·双侧零跳位=W53 行公示投影逐位）·【机证净空——leg1-A/leg1-B 双侧算术 CLEAN 机证+leg2 双侧首净窗==候选逐位·ADMIT 回执=results/_r559bma_w54_band_gate.py·r559 bm-a 起草窗实跑【leg0 五十二键（51 注册行+候选）+leg0b W53 行 W54+ 警示 prose 在场校验+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·测量面零结果可钓】】·扫描面=pre-W54 五十一行 N1 带表【含 W49 行 141_004..143_003/45_401..45_600〔r556 bm-b·finalize 已落账 K=103,520〕·W50 行 143_004..145_003/45_601..45_800〔r350 bm-c·finalize 已落账 K=107,920〕·W51 行 145_004..147_003/46_001..46_200〔r350 bm-c·finalize 已落账 K=110,120〕·W52 行 147_004..149_003/46_201..46_400〔r351 bm-c·finalize 已落账 K=112,320·**净账本链头 478,948**〕·W53 行 149_004..151_003/46_401..46_600〔r351 bm-c·**注册在飞**·分片烧录中·finalize 未落账=本波唯一在飞上游席位·本波 finalize 链序前置=W53 落账·FAIL-CLOSED r307 两态律〕】·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际抽带 30_000..30_099·options_wave2 实际抽带 63_000..63_049·leg-3e 实际流避让。**N2/N4 让位注记**：本波 A 带 151_004..153_003——N2/N4 波级 prereg 冻结时按本表防撞律回避该域。**W55+ 警示**：A +2_000 算术位（153_004..155_003）投影与 B +200 算术位（46_801..47_000）投影均以本波带闸回执 W55+ 投影腿机证为准（机闸 derive 非 prose 转抄·r535 律·去节流令下=首个自由号法·无座位指派——W55 prereg 仍照例带闸复核）。
"""
FP4 = r"research\PERPETUAL_FACES.md"
t4, eol4 = load(FP4)
if "- N1 波54（r559 bm-a" in t4:
    print("edit4 already landed (idempotent skip)")
else:
    A4 = "\n- 每波 finalize 后：`science_gates.append_ledger` 落行"
    A4X = A4.replace("\n", eol4)
    assert t4.count(A4X) == 1, f"canon anchor not unique: {t4.count(A4X)}"
    ROW54X = ROW54.replace("\n", eol4)
    t4 = t4.replace(A4X, ROW54X + A4X)
    save(FP4, t4, eol4)
    print("edit4 canon W54 row landed")
print("FREEZE_EDITS_OK")
