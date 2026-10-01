# r531 bm-b W40 freeze landing part 2: selftest W40 materializer face + canon law row.
from pathlib import Path

def patch(path, old, new):
    p = Path(path)
    data = p.read_bytes().decode("utf-8")
    old = old.replace("\r\n", "\n")
    new = new.replace("\r\n", "\n")
    assert data.count(old) == 1, f"anchor not unique in {path} (count={data.count(old)})"
    p.write_bytes(data.replace(old, new).encode("utf-8"))
    print(f"patched {path}")

# --- 3. scripts/perpetual_faces_n1.py: selftest W40 materializer face -------
# (insert after the W39 materializer face block, before the T-141 s2 lane face)
patch(
    r"scripts/perpetual_faces_n1.py",
    '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''',
    '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- W40 materializer face (r531 bm-b freeze, own-series law
    #     O-20261001-2355 sec.2 -- bm-b's THIRTEENTH owned wave after
    #     W10/W11/W13/W16/W19/W22/W25/W28/W31/W34/W36/W38; zero-gap relay
    #     after the W38 FULL CLOSEOUT r530: finalize one-pass K=81,520,
    #     ledger 446,140 chain head; W39 = bm-c lineage, finalize pending
    #     at this freeze -- in-flight coexists by band disjointness) ---
    _set_wave(40)
    try:
        assert WAVE_CONFIGS[40]["a_seed_base"] == pf.N1_BANDS[40]["a"][0], \\
            "W40 A band drift vs law mirror"
        assert WAVE_CONFIGS[40]["b_exit_seed_base"] == \\
            pf.N1_BANDS[40]["b_exit"][0], "W40 B band drift vs law mirror"
        assert WAVE_CONFIGS[40].get("engine_owner") == \\
            pf.N1_BANDS[40].get("engine_owner") == "bm-b", \\
            "W40 engine_owner drift (law mirror parity)"
        w40_a = {A_SEED_BASE + j for j in range(A_N)}
        w40_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w40_a & w40_b), "W40 A/B band overlap"
        assert not (w40_a & reg_ints) and not (w40_b & reg_ints), \\
            "W40 hits SEED_REGISTRY"
        for nm, band in (("A", w40_a), ("B", w40_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W40 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W40 {nm} hits W1"
            assert not (band & probes), f"W40 {nm} hits probe seeds"
        # prior-wave disjointness incl. W38 (bm-b, closed FULL-LIFECYCLE
        # r530: finalize one-pass K=81,520, ledger 446,140) and W39
        # (bm-c, registered + burned 12/12 + finalize pending at this
        # freeze -- in-flight coexists by band disjointness per r531 law).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39):
            assert not (w40_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W40 A hits W{wprev}"
            assert not (w40_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W40 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory: R1=70_000..70_005,
        # r529 bm-a adjudication row) -- W40 bands must clear it.
        n3r1_used40 = set(range(70_000, 70_006))
        assert not (w40_a & n3r1_used40) and not (w40_b & n3r1_used40), \\
            "W40 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w40_a & lfc_actual12) and not (w40_b & lfc_actual12), \\
            "W40 bands must clear the lfc actual draw range"
        assert not (w40_a & options_actual12) and \\
            not (w40_b & options_actual12), \\
            "W40 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W40 row, r531): A = arithmetic continuation
        # clean exactly as the W39 row's W40+ WARNING projected; B =
        # arithmetic continuation clean (BOTH sides zero-skip -- the W39
        # warning projected both CLEAN; candidate == machine-derived).
        assert WAVE_CONFIGS[40]["a_seed_base"] == 123_004 == 123_003 + 1, \\
            "W40 A must start at the W39 A end + 1 (arithmetic continuation)"
        assert WAVE_CONFIGS[40]["b_exit_seed_base"] == 43_201 == 43_200 + 1, \\
            "W40 B must start at the W39 B end + 1 (arithmetic continuation)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W40-SHARD-0",
                                          "n1w40-0of12"), "W40 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W40-SHARD-11",
                                           "n1w40-11of12")
        assert SHARD_DIR.endswith("n1_w40") and OUT.endswith(
            "n1_w40_results.json"), "W40 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W40 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W40_PREREG.md")), \\
            "W40 per-wave prereg missing (materializer requirement)"
        # W40 finalize cumulative deps: W17..W38 outputs ALL PRESENT
        # (W34 finalize r528 bm-b K=72,720; W35 finalize bm-a r546
        # K=74,920; W36 finalize bm-b r529 K=77,120; W37 finalize bm-c
        # r342 K=79,320 -- ledger 443,940; W38 finalize bm-b r530
        # K=81,520 -- net ledger head 446,140); W39 (bm-c, burned
        # 12/12 + finalize pending at this freeze) -- the dep pin
        # carries the two-state honest note per the r541 W30 precedent
        # (finalize runtime composes every registry key below 40 =
        # FAIL-CLOSED honest wait for the W39 output once it lands).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W40 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 40 (no 15; W39
        # in-flight = runtime FAIL-CLOSED guard).
        assert sorted(w for w in WAVE_CONFIGS if w < 40) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39], \\
            "W40 prior-wave set must derive from registry keys (no 15, incl. 39)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
print("selftest W40 materializer face landed (byte-level LF)")

# --- 4. research/PERPETUAL_FACES.md: sec.4 law table W40 row ----------------
p = Path(r"research/PERPETUAL_FACES.md")
data = p.read_bytes().decode("utf-8")
anchor = "\n## §5 计账（跨波累计 N_eff 恒不重置）"
assert data.count(anchor) == 1, "sec.5 heading anchor not unique"

w40_row = (
    "- N1 波40（r531 bm-b 冻·prereg 时展行）：**第三十枚引擎波·bm-b 第十三自有波**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W39 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·"
    "【本机上波=W38 同窗全生命周期收官 r530（finalize one-pass K=81,520·账本链头 446,140·prereg s7/s8 回填齐）·W39=bm-c r342 lineage（已注册+12/12 烧录·finalize 待落本机车道）→零隔接力·波号 40=W39 行落账后首个自由号·r511 表尾锁例冻结前 fetch 实核表尾时 W40 号位净空·first-free-number 法】·"
    "【never-dry 供给律常设步·r531 实况=引擎活·status exit 0·队列空·W39 12/12 在册·池面 LOWAMP-P3 族 bm-a 认领在飞·车道负怠已披露禁空转禁等 CEO 提醒】·A-ext seed=**123_004..125_003**"
    "（**A 面算术顺延**·=W39 A 尾 123_003+1·步长逐字·**零跳位**·【机证净空**registry-derive**——候选位注册表 derive 非散布带间·leg1-A/leg2-A 机证==W39 行公示投影 CLEAN==候选**】·"
    "扫描面=pre-W40 三十七行 N1 带表【含 W34 行 111_004..113_003/41_801..42_000（r527 bm-b·finalize 实落账 K=72,720）·W35 行 113_004..115_003/42_001..42_200（r545 bm-a·finalize 实落账 K=74,920）·W36 行 115_004..117_003/42_201..42_400（r528 bm-b·finalize 实落账 K=77,120·链头 441,740）·W37 行 117_004..119_003/42_401..42_600（r341 bm-c·finalize 实落账 K=79,320）·"
    "W38 行 119_004..121_003/42_601..42_800（r529 bm-b·finalize 实落账 K=81,520·链头 446,140）·W39 行 121_004..123_003/43_001..43_200（r342 bm-c·12/12 烧录在册·finalize 待落）】·带域不相交·异带共存 r531 律·W1 ext·v1 在用带·SEED_REGISTRY 全集**161 值·起扫窗实证**·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际抽带 30_000..30_099·options_wave2 实际抽带 63_000..63_049·leg-3e 实际流避让**】·"
    "**ADMIT 回执=results/_r531bmb_w40_band_gate.py**·r531 bm-b 起草窗实跑【leg0 三十七行+候选注册面校验+leg0b W39 行 W40+ 警示 prose 在场校验+leg1-A registry-derive 算术面 CLEAN 机证+leg1-B 算术面 CLEAN 机证+leg2-A 首净窗=候选**零跳位**·leg2-B 首净窗=候选**零跳位**·leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验**非重挑 R250**·W40 带从未指派·测量面零结果可钓**】·"
    "B-ext exit seed=**43_201..43_400**（**B 面算术顺延**·=W39 B 尾 43_200+1·步长逐字·**零跳位**·【机证净空**registry-derive**——leg1-B/leg2-B 机证==W39 行公示投影 CLEAN==候选·两侧独立裁定如实披露·A/B 双侧零跳位】）。**N2/N4 让位注记**：本波 A 带 123_004..125_003——N2/N4 波级 prereg 冻结时按本表防撞律回避该域。"
    "**W41+ 警示**：A +2_000 算术位（125_004..127_003）与 B +200 算术位（43_401..43_600）投影以 r531 带闸回执 W41+ 投影腿机证为准（机闸 derive 非 prose 转抄·r535 律·去节流令下=首个自由号法·无座位指派）。"
)
w40_row = w40_row.replace("\r\n", "\n")
t = data.replace(anchor, "\n" + w40_row + anchor[1:])
p.write_bytes(t.encode("utf-8"))
print("W40 law row landed in research/PERPETUAL_FACES.md sec.4 (byte-level LF)")
