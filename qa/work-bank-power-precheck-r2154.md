# QA — 工作银行判据的功效预算（r2154 / bm-c）

## 本轮主张

`research/WORK-BANK.json` 里 14 张带量级判据的卡，**全部**判据小于它自己样本的标准误半宽；3 张 census 卡没有量级判据（无门可判）。
因此按现行判据判出的「H1/H2 不过」不是负结论，而是 `UNINFORMATIVE_AT_TARGET`。新补的 3 张卡按半宽反推判据，全部 POWERED。

## 证据

| 项 | 值 | 来源 |
|---|---|---|
| 公式 | 1.96·vol% / √年数；夏普半宽 1.96/√年数 | `scripts/bench_power.py:mde`（**import**，未手抄） |
| 样本长度 | 逐卡按产品面板**交集**计真实 bar，非全局常数 | `data/futures_daily/*.csv`，cutoff 2026-11-26 |
| OOS 半宽（vol 6%） | 6.93 pp（2.88 年） | `results/work_bank_power_precheck.json` |
| 银行 H2 门 vs 半宽 | 2.0 / 3.0 pp vs 6.93–11.56 pp → 0.22–0.29x | 同上 |
| OOS 夏普门 vs 半宽 | 0.3 / 0.4 vs 1.16 → 0.26–0.34x | 同上 |
| 2pp 边在 6% 波动下需要的 OOS | (1.96·6/2)² = **34.6 年** | 公式代入 |
| 全窗半宽 | 4.0（8.6 年，AU/RB/SC）～7.54（4.32 年，含 IM） | 同上 |
| 新卡判据 | H1 6.0 ≥ 4.0、H2_oos 8.0 ≥ 6.93 → **POWERED** | `research/WORK_BANK_ADDITIONS.json` |

## 复现

```
python scripts/work_bank_power_precheck.py --selftest   # 12/12
python scripts/work_bank_power_precheck.py run --md     # rc0，幂等
python scripts/work_bank_power_precheck.py --check      # {"check":"ok", drifted_items:[]}
```

## 负控（必须会红，否则这条腿是装饰）

1. `bank_h2_2pp_unpowered` —— 把银行自己的 H2=2pp 喂给分类器，在 6%/2.9 年上必须判 UNPOWERED（防止分类器把任何门都判绿）。
2. `sure_thing_powered` —— 反向控制：vol 1%、10 年、门 0.62pp 必须判 POWERED（防止分类器把所有门都判红）。
3. `assess_flags_unpowered` / `assess_powered_when_gate_wide` —— 同一张合成卡的判据从 2.0 改成 20.0，verdict 必须翻转（防止 verdict 是常量）。
4. `at_half_width_is_powered` —— 门恰等于半宽必须判 POWERED（防止 >= 写成 >）。
5. `just_below_band_unpowered` / `inside_band_marginal` —— 0.72x 判红、0.87x 判 MARGINAL（钉死 0.75 带）。

## 诚实边界（未做 / 不成立的地方）

1. **没合进银行**：`research/WORK-BANK.json` 有第二个写手（调度器 materialise cell 时会把 status 翻成 `queued` 并盖 `queued_at`），本轮竞争窗 rc=3，按 r1907 只落新增文件面。合入件已备好（按 id 去重即可），合入是一个字面动作。
2. **没跑全量冒烟、没跑 S6 链**：同树另有宿主在写共享面（88 张共享面已被它先写过），按 r1907 禁重跑链。本轮所有数字来自面板原字节与本脚本，不依赖任何共享面重算。
3. **H4 的窗口归属是假设**：银行未声明 H4（drop-best）在 IS 还是 OOS 上算，本表按**全窗**映射。若实际是 OOS，H4 的 ratio 会更差（半宽更大），不改变任何卡的 UNPOWERED 结论。
4. **不动性假设**：MDE 公式假设日收益独立同分布；真实序列有自相关/波动聚集，有效样本更少，所以真实半宽只会**更大**，结论方向不会因此翻绿。
5. **不是对策略的判断**：本面只判「这张卡的判据能不能被这段样本回答」，不判任何策略好坏，也不改任何 `crit` 的既有卡（既有卡一张未动）。

## 结论口径

- 可以说的：14 张卡的量级判据在本样本上不可判；OOS 夏普门 0.3–0.4 需要 ≥ 1.16 才能自持；2pp 的 OOS 边需要 34.6 年。
- 不可以说的：这些策略「没有边」或「已被证伪」——本面没有算任何策略收益。
