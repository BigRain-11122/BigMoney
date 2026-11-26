# QA · 那条「绝对 ≥4%」的线是技能线还是杠杆线（r2152 · bm-c）

## 1. 主张（可判真假）

1. 每张 bench 面的臂都在**各自的实现波动**上印年化，实现波动跨度 4.45%–14.68%（3.3 倍），
   而面自己声明的目标波动只有 6% 和 8%（个别 10%）。
2. 把所有臂按常数杠杆重定价到面自己的目标波动后，`H1_full_ge >= 4.0%` 的过线集合从 15 条变 11 条
   （5 条下降、1 条上升），**GO 集合不变（4 → 4）**。
3. 基准侧的尺寸同样没落位：17 张面里 16 张的基准实现波动大于声明目标；
   按自己的目标重定价后，原本「持有就能过 4%」的 4 张面只剩 1 张（trend_single_AU_long）。
4. r2145 的 `benchmark_aligned_ann_pct` 与 `benchmark_published_ann_pct` 在 **17/17** 张面上逐位相同，
   其中 13 张面换了目标波动标签而收益数没变——「对齐」是对了标签，不是对了仓位。

## 2. 证据

| 项 | 位置 |
|---|---|
| 面（JSON，含全部逐臂行与计数） | `results/bench_size_normalized_h1.json` |
| 页（人读） | `research/BENCH_SIZE_NORMALIZED_H1.md` |
| 工具 | `scripts/bench_size_normalized_h1.py` |
| 输入面 | `results/bench_*.json`（51 份，排除本面自身）+ `results/bench_go_ruler_audit.json` |

复现（全部本地、零网络）：

```
python scripts/bench_size_normalized_h1.py --selftest   # 10/10 PASS
python scripts/bench_size_normalized_h1.py              # faces 17 · arms 59
python scripts/bench_size_normalized_h1.py --check      # rc0，inputs_digest 71aa8d97cbecc9a6
```

幂等：连续两次运行，除 `generated` 戳外**逐字节相同**（body digest 相等）。

## 3. 判据与算术（冻结在脚本里，先于读数）

- 常数杠杆重定价：`mu = g + s^2/2`，`g(k) = k*mu - (k*s)^2/2`，`k = target_vol / realised_vol`。
- 臂波动取 `common_window.vol_pct`；面不印时由已公布 MDE 反推（`mde = 1.96*vol/sqrt(n/252)`，
  与 `bench_generic.run_arm` L143 同式），反推容差 0.5pp，自检腿 `derive_reproduces_published_vol` 钉死。
- 偏离带：`|realised/target - 1| > 10%` 才算 off-target。
- `H1_FULL_PCT = 4.0` 复制自 `bench_generic.run_arm`（L153），不另立阈值。

## 4. 自检腿（10/10）

`identity_k1` · `synthetic_half_size`（手算 10%/20% → k=0.5 → 5.5%）· `same_print_different_size` ·
`known_arm_flips_down`（5.50@12.21 → 8% = 3.77 < 4）· `known_arm_flips_up`（3.09@4.45 → 6% = 4.12 > 4）·
`bond_hold_loses_h1_at_target`（4.86@7.87 → 6% = 3.76 < 4）· `mde_round_trip` · `derive_reproduces_published_vol` ·
`no_ann_no_rescale` · `zero_vol_is_missing`。

## 5. 自捕缺陷（本轮内修，未发布前拦下）

1. **digest 自包含**：首版 `input_paths()` 用 `results/bench_*.json` 通配，把自己的产物
   `results/bench_size_normalized_h1.json` 也算了进去 → 每次运行 `--check` 立刻报 STALE（实测 rc3）。
   修法=按 basename 排除自身，并在注释里写清为什么。
2. **自检腿前提错**：初版第 3 腿假设「放大再缩小不等于原值」，但按同一套 vol-drag 算术往返是恒等的
   （自检 FAIL 当场暴露），换成有意义的腿：同一个印出来的 4.5%，在 14.68% 与 4.45% 波动下
   归一后差 1pp 以上。

## 6. 局限（不宣称）

- 只碰 H1 一轴。H2/H3/H4/H5 未重算，故本页**不重发任何 verdict**，GO 数=已公布值，仅核 H1 是否仍过。
- 未建模融资成本：`k < 1` 时归一后的数略偏乐观，`k > 1` 时略偏保守。
- 常数杠杆不含再平衡摩擦；与面内 `vol_weighted_positions` 的实现差异未量化。
- 未改 `bench_generic.py`（共享面；本轮竞争窗 rc=3 禁改），修法写进页面的「建议」节。

## 7. 缺陷留档（给无竞争轮修的）

1. `scripts/bench_generic.py::run_arm` 的 H1 判在原始年化上 → 臂的实现波动一漂，判词跟着漂。
   修法：改用 `rescale(ann, vol, target/vol)` 后的年化。
2. 面的 `benchmark_sizing.same_yardstick` 是布尔声明，不是实测断言 → 基准跑在 14.18%（目标 8%）时
   它仍印 `true`。修法：加 `|bench_vol/target-1| <= 10%` 的实测断言，不满足就打 `false` 并点名。
3. `results/bench_go_ruler_audit.json` 的 `benchmark_aligned_*` 三个字段与 `benchmark_published_*`
   装同一个数 → 要么真重算，要么改名回 `published`（r1639 律：同一测量不许在一页上印两遍）。
