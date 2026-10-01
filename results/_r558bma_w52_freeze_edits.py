# -*- coding: utf-8 -*-
"""r558 bm-a W52 freeze: land N1_BANDS/WAVE_CONFIGS/selftest-leg/canon-row edits.

Bytes-safe (r530): decode utf-8, exact-anchor str replace, encode back.
Every anchor asserted UNIQUE before replace. Inserted text EOL-normalized
to each file's dominant ending.
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

# ---------------- edit 1: perpetual_faces.py N1_BANDS[52] -------------------
FP1 = r"scripts\perpetual_faces.py"
t1, eol1 = load(FP1)
if '52: {"a": (147_004' in t1:
    print("edit1 already landed (idempotent skip)")
else:
    A1 = ('    51: {"a": (145_004, 147_003), "b_exit": (46_001, 46_200),\n'
          '         "engine_owner": "bm-c"},\n}')
NEW52_BANDS = ('    51: {"a": (145_004, 147_003), "b_exit": (46_001, 46_200),\n'
              '         "engine_owner": "bm-c"},\n'
              '    52: {"a": (147_004, 149_003), "b_exit": (46_201, 46_400),\n'
              '         "engine_owner": "bm-a"},\n}')
    t1 = rep(t1, A1, NEW52_BANDS, eol1, "pf-bands")
    save(FP1, t1, eol1)
    print("edit1 perpetual_faces.py N1_BANDS[52] landed")

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[52] --------------
FP2 = r"scripts\perpetual_faces_n1.py"
t2, eol2 = load(FP2)
if '52: {"batch": "PERPETUAL-N1-W52"' in t2:
    print("edit2 already landed (idempotent skip)")
else:
    A2 = ('                            "engine_owner": "bm-c"},\n'
          '                       }')
ENTRY52 = '''                            "engine_owner": "bm-c"},
                       52: {"batch": "PERPETUAL-N1-W52",
                            "prereg": ("research/PERPETUAL_N1_W52_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; FORTY-FIRST ENGINE-OWNED WAVE, "
                                       "own-series continuation per O-20261001-2355 sec.2 "
                                       "(first-free-number law), engine_owner=bm-a, wave 52 = "
                                       "next free number after the registered W51 row, BOTH "
                                       "ARITHMETIC CONTINUATION no skip (A 147_004..149_003, "
                                       "B 46_201..46_400, both CLEAN machine-derived == the "
                                       "W51 row W52+ published projection verbatim; ADMIT "
                                       "receipt results/_r558bma_w52_band_gate.py); upstream "
                                       "W48/W49 finalizes LANDED (W48 bm-a r558 seat-loss "
                                       "re-derive prev=470,148 total=472,348 K=103,520; W49 "
                                       "bm-b r556 ledger 470,148), W50/W51 registered with "
                                       "finalizes NOT landed at this freeze = in-flight chain "
                                       "seats honest note, finalize merge loop derives the "
                                       "wave set from registry keys at run time and stays "
                                       "FAIL-CLOSED on any not-yet-finalized upstream seat, "
                                       "r307 two-state law)"),
                            "a_seed_base": 147_004,        # law sec.4 W52 A: 147_004..149_003 (arithmetic continuation)
                            "b_exit_seed_base": 46_201,    # law sec.4 W52 B: 46_201..46_400 (arithmetic continuation)
                            "shard_subdir": "n1_w52", "out_name": "n1_w52_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    t2 = rep(t2, A2, ENTRY52, eol2, "n1-configs")
    save(FP2, t2, eol2)
    print("edit2 WAVE_CONFIGS[52] landed")

# ---------------- edit 3: perpetual_faces_n1.py selftest W52 leg --------------
LEG52 = '''
    # --- W52 materializer face (r558 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-a's TWELFTH owned wave; wave 52 = next free number
    #     after the registered W51 row (zero-gap relay after the
    #     W48 full closeout this same window -- seat-loss
    #     re-derive finalize landed prev=470,148 total=472,348;
    #     W50/W51 bm-c registered with finalizes chain-pending --
    #     two in-flight upstream seats at this freeze, finalize
    #     merge loop FAIL-CLOSED at run time per r307 two-state
    #     law). BOTH SIDES ARITHMETIC CONTINUATION from the W51
    #     tail no skip (A 147_004..149_003 / B 46_201..46_400,
    #     both CLEAN == the W51 row W52+ published projection
    #     verbatim; ADMIT receipt results/_r558bma_w52_band_gate.py;
    #     not a re-pick -- R250: W52 bands were never assigned) --
    _set_wave(52)
    try:
        assert WAVE_CONFIGS[52]["a_seed_base"] == pf.N1_BANDS[52]["a"][0], \\
            "W52 A band drift vs law mirror"
        assert WAVE_CONFIGS[52]["b_exit_seed_base"] == \\
            pf.N1_BANDS[52]["b_exit"][0], "W52 B band drift vs law mirror"
        assert WAVE_CONFIGS[52].get("engine_owner") == \\
            pf.N1_BANDS[52].get("engine_owner") == "bm-a", \\
            "W52 engine_owner drift (law mirror parity)"
        w52_a = {A_SEED_BASE + j for j in range(A_N)}
        w52_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w52_a & w52_b), "W52 A/B band overlap"
        assert not (w52_a & reg_ints) and not (w52_b & reg_ints), \\
            "W52 hits SEED_REGISTRY"
        for nm, band in (("A", w52_a), ("B", w52_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W52 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W52 {nm} hits W1"
            assert not (band & probes), f"W52 {nm} hits probe seeds"
        # prior-wave disjointness incl. W48/W49/W50/W51 (all
        # registered; W50/W51 finalizes in flight -- coexist by
        # band disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51):
            assert not (w52_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W52 A hits W{wprev}"
            assert not (w52_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W52 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W52 clears it.
        n3r1_used52 = set(range(70_000, 70_006))
        assert not (w52_a & n3r1_used52) and not (w52_b & n3r1_used52), \\
            "W52 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w52_a & lfc_actual12) and not (w52_b & lfc_actual12), \\
            "W52 bands must clear the lfc actual draw range"
        assert not (w52_a & options_actual12) and \\
            not (w52_b & options_actual12), \\
            "W52 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W52 row, r558): BOTH SIDES
        # ARITHMETIC CONTINUATION (A 147_004 = W51 A end + 1; B
        # 46_201 = W51 B end + 1; both windows CLEAN -- zero-skip
        # wave, first both-sides arithmetic since W51's A-side /
        # W48's both-sides).
        assert WAVE_CONFIGS[52]["a_seed_base"] == 147_004 == 147_003 + 1, \\
            "W52 A must start at the registered W51 A end + 1 " \\
            "(arithmetic continuation window 147_004..149_003 CLEAN -- " \\
            "no skip family)"
        assert WAVE_CONFIGS[52]["b_exit_seed_base"] == 46_201 == 46_200 + 1, \\
            "W52 B must start at the registered W51 B end + 1 " \\
            "(arithmetic continuation window 46_201..46_400 CLEAN -- " \\
            "no skip family)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W52-SHARD-0",
                                          "n1w52-0of12"), "W52 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W52-SHARD-11",
                                          "n1w52-11of12")
        assert SHARD_DIR.endswith("n1_w52") and OUT.endswith(
            "n1_w52_results.json"), "W52 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W52 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W52_PREREG.md")), \\
            "W52 per-wave prereg missing (materializer requirement)"
        # W52 finalize cumulative deps: W17..W49 outputs ALL PRESENT
        # (static landed seats -- W48 landed r558 bm-a seat-loss
        # re-derive, W49 landed r556 bm-b); W50/W51 = REGISTERED
        # with finalizes NOT landed at this freeze (two in-flight
        # chain seats -- the finalize merge loop derives the wave
        # set from registry keys at run time and stays FAIL-CLOSED
        # on any not-yet-finalized upstream seat, r307 two-state
        # law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W52 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 52 (no 15; incl. 48/49/50/51
        # -- all registered, W50/W51 finalizes in flight, FAIL-CLOSED at
        # run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 52) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51], \\
            "W52 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48/49/50/51)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
# reload after edit 2
t2b, eol2b = load(FP2)
if "W52 materializer face" in t2b:
    print("edit3 already landed (idempotent skip)")
else:
    A3 = "\n    # --- T-141 s2 lane face"
    LEG52X = LEG52.replace("\n", eol2b)
    A3X = A3.replace("\n", eol2b)
    assert t2b.count(A3X) == 1, f"selftest anchor not unique: {t2b.count(A3X)}"
    t2b = t2b.replace(A3X, LEG52X + A3X)
    save(FP2, t2b, eol2b)
    print("edit3 selftest W52 leg landed")

# ---------------- edit 4: PERPETUAL_FACES.md canon W52 row -------------------
ROW52 = """
- N1 波52（r558 bm-a 冻·prereg 时展行）：**第四十一枚引擎波·bm-a 第十二枚自有波**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W51 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启·W44/W45/W48 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**零隔接力：本机上波 W48 本窗已全链交付**（r557 冻结→tick 12/12 烧毕→**落账序让路-重derive finalize one-pass 终稿**〔首跑 prev=467,948 撞 bm-b W49 同窗先落账=r518 同 prev 双头·S0 让路二次 finalize prev=470,148 derive·total 472,348·K=103,520==冻结 §0 投影逐位·r518 净路 bm-a 首例〕）→**波号 52=注册表 W51 行后首个自由号**·r511 表尾锁例冻结前 fetch 实核表尾时 W52 号位净空】·**分面 derive（r535 机闸 derive 律·r307 波带尾律）**：W51 行 W52+ 警示投影 **A 147_004..149_003 CLEAN／B 46_201..46_400 CLEAN**→本波 **A-ext seed=147_004..149_003**（**A 面算术续带零跳位**==W51 A 尾 147_003+1·步长逐字）·**B-ext exit seed=46_201..46_400**（**B 面算术续带零跳位**==W51 B 尾 46_200+1·步长逐字·双侧零跳位=W51 行公示投影逐位）·【机证净空——leg1-A/leg1-B 双侧算术 CLEAN 机证+leg2 双侧首净窗==候选逐位**·ADMIT 回执=results/_r558bma_w52_band_gate.py**·r558 bm-a 起草窗实跑【leg0 五十键（49 注册行+候选）+leg0b W51 行 W52+ 警示 prose 在场校验+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·测量面零结果可钓】】·扫描面=pre-W52 四十九行 N1 带表【含 **W49 行 141_004..143_003/45_401..45_600（r556 bm-b·finalize 已落账 K=103,520 ledger 470,148）·W50 行 143_004..145_003/45_601..45_800（r350 bm-c·12/12 烧毕·finalize 在飞·异带共存 r531 律）·W51 行 145_004..147_003/46_001..46_200（r350 bm-c·12/12 烧毕·finalize 在飞·异带共存 r531 律）**】·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键 161（int 值 160·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际抽带 30_000..30_099·options_wave2 实际抽带 63_000..63_049·leg-3e 实际流避让。**N2/N4 让位注记**：本波 A 带 147_004..149_003——N2/N4 波级 prereg 冻结时按本表防撞律回避该域。**W53+ 警示**：A +2_000 算术位（149_004..151_003）投影 CLEAN；B +200 算术位（46_401..46_600）投影 CLEAN（r558 带闸回执 W53+ 投影腿机证为准·机闸 derive 非 prose 转抄·r535 律·去节流令下=首个自由号法·无座位指派——W53 prereg 仍照例带闸复核；**本波 finalize 链序前置=W50→W51 双 finalize 落账**〔两席位注册在飞·finalize 波集按 registry 键运行时 derive·FAIL-CLOSED·r307 两态律·W48/W49 已落账=本波 ordinal 组分基 110,120 实锚〕）。
"""
FP4 = r"research\PERPETUAL_FACES.md"
t4, eol4 = load(FP4)
if "- N1 波52（r558 bm-a" in t4:
    print("edit4 already landed (idempotent skip)")
else:
    A4 = "\n- 每波 finalize 后：`science_gates.append_ledger` 落行"
    A4X = A4.replace("\n", eol4)
    assert t4.count(A4X) == 1, f"canon anchor not unique: {t4.count(A4X)}"
    ROW52X = ROW52.replace("\n", eol4)
    t4 = t4.replace(A4X, ROW52X + A4X)
    save(FP4, t4, eol4)
    print("edit4 canon W52 row landed")
print("FREEZE_EDITS_OK")
