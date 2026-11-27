# QA · carry-first-rung-vol-ruler · r2193 (bm-c)

日期：2026-11-28 00:1x +08:00 · 审判面：`results/carry_first_rung_vol_ruler.json`
页面：`results/carry_first_rung_vol_ruler.md` + `research/CARRY_FIRST_RUNG_VOL_RULER.md`
脚本：`scripts/carry_first_rung_vol_ruler.py`

## 判据清单

| # | 判据 | 证据 | 结果 |
|---|---|---|---|
| 1 | 面可生成（rc0） | `python scripts\carry_first_rung_vol_ruler.py` → `THE_FIRST_RUNG_IS_A_VOLATILITY_READ_NOT_A_CAPITAL_THRESHOLD` / `THE_EIGHT_PERCENT_CAP_IS_BREACHED_ABOUT_ONE_YEAR_IN_FOUR`，rc0 | PASS |
| 2 | 自检全绿 | `--selftest` → **26/26 PASS** | PASS |
| 3 | 漂移守卫可用 | `--check` → `{"ok": true, "notes": []}` rc0 | PASS |
| 4 | **复现腿：已发布的尺** | 最近 242 收益日重算 → **91,029.00**，逐位 = `open_capital.accounts.IC.per_lot_vol_cny_hedged` | MATCH |
| 5 | **复现腿：已发布的门槛** | 91,029.0 / 8% → **1,137,862.50**，逐位 = `book.cheapest_to_open.funding_cny` | MATCH |
| 6 | 复现失败即不发布 | 主程序遇 `reproduction.verdict != MATCH` → 判词 `UNREADABLE`、exit 2、不写面 | PASS |
| 7 | 漂移会说 STALE（行为腿） | selftest：把 `published_vol_cny` 改 1% → rc3 且含 `STALE` | PASS |
| 8 | 自相矛盾不带 STALE（行为腿） | selftest：改判词 token → rc3 含 `CHECK FAILED`、**无** `STALE` | PASS |
| 9 | 门槛↔波动恒等式有守卫 | selftest：把 `first_rung_today_cny` 改 1.0 → rc3 含 `CHECK FAILED` | PASS |
| 10 | 判词有冻结边界腿 | selftest：p90/60%（边界）→ A；89.9/60% → C；70/39.9% → B | PASS |
| 11 | 越限判词有边界腿 | selftest：9.9 → HOLDS；20 → ONE_YEAR_IN_FOUR；33.1 → HALF_THE_TIME | PASS |
| 12 | 缺数不编判词 | selftest：`judge(None, 50)` → `UNREADABLE` | PASS |
| 13 | 分布自洽 | 今日读数落在滚动分布 min..max 内；`share_allowing_one_lot` ∈ [0,100] 且 ≤ `share_at_or_below_budget` | PASS |
| 14 | 门槛区间不倒挂 | `range_of_the_first_rung_cny` = [837,496.51, 1,137,862.5]，los ≤ hi | PASS |
| 15 | 十进制一致 | 表内所有下游数从 2dp 波动派生；未舍入值只用于 Sharpe。修前 1,137,862.55 vs 1,137,862.5 的 5 分钱假差异已消除 | PASS |
| 16 | 点数→钱不造分母 | 乘数 200 元/点取自已发布 `idx_fut_carry_one_lot_ruler::rule.precision_tick_basis`（原文 "200 x 0.0001 = 0.02"），读不到则标 fallback | PASS |
| 17 | 零网络零回测 | 仅本地面板重放（`CP.position_series` / `CP.per_lot_daily` / `BASE.load_index`） | PASS |
| 18 | 不改任何已发布面 | 只写 `results/carry_first_rung_vol_ruler.{json,md}`；未碰 `open_capital` / `SIZING` / `sizing_spec` | PASS |

## 本轮读数（cutoff 2026-11-26 · IC · 100 万 · 8% 目标）

| 窗口 | bar | 每手年化波动（元） | 手数 | 第一手门槛（元） |
|---|---:|---:|---:|---:|
| 最近 1 年 | 242 | 91,029 | **0** | 1,137,862.5 |
| 最近 2 年 | 484 | 75,810 | 1 | 947,620 |
| 最近 3 年 | 726 | 83,956 | 0 | 1,049,453 |
| 最近 5 年 | 1210 | 72,418 | 1 | 905,220 |
| 全样本 | 1965 | 71,149 | 1 | 889,367 |

- 滚动一年窗 1724 个：min 32,495 / 中位 67,000 / p90 89,037 / max 98,400；**今日 91,029 = 93.79 分位**（107 个窗更热）
- 历史买得起率（100 万 ≥ 1 手）：**78.13%**
- 越限检验：1482 对（1246 对上年 ≥1 手），**越限 346 = 27.77%**；手数翻转率 42.24%
- 下年/上年波动比：p50 1.0192 / p90 1.7882 / p95 2.5818 / max 3.0279

## 结论（四条）

1. **1,137,862.5 是波动读数，不是资本门槛**：它是「最近 242 天 91,029 ÷ 8%」的今日值，
   同一条算术在中位年份给 837,497。
2. 「100 万今天买 0 手」仍然对（尺是最近一年），但同一规则在历史上 78.13% 的年份会买 1 手
   —— 票面收回不需要新钱，波动降 12.12% 就自动还回。
3. 五把已发布尺里两把说 0 手、三把说 1 手 —— 门槛是尺的属性，不是这本书的属性。
4. **8% 上限四年破一次（27.77%）**；要成为 p90 上限，尺要乘 1.7882。

## 已知未覆盖（如实）

1. **无链腿、无冒烟腿** —— 本轮 `repo_write_contention --lookback-min 45` **rc=3 CONTENTION**
   （对端 interactive pid 30500 自 21:54 存活、peer 先写 22 张共享面），按 r1907/r1927 禁改
   `Tools/s6_chain_bmc.py` / `smoke_test.py`、禁跑 S6 链；挂账进 carrier_debt。
2. 前向检验是**重叠样本**，独立样本远少于 1482 对 —— 频率是描述性，不是显著性检验。
3. 未对下一年波动建模（EWMA/GARCH 均未做）。
4. IM 账户未同做（每手波动 93,259.93 同出 242 天窗，腿长与主力不同）。
5. `idx_fut_carry_open_capital` 的那句 "To open this book at all needs 1,137,862 CNY of
   capital" 仍是旧措辞 —— 共享面，本轮未改。
