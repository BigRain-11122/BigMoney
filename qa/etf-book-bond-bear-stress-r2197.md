# QA · etf-book-bond-bear-stress · r2197 (bm-c)

日期：2026-11-28 01:2x +0800 · 审判面：`results/etf_book_bond_bear_stress.json`
页面：`research/ETF_BOOK_BOND_STRESS.md` · 脚本：`scripts/etf_book_bond_bear_stress.py`

本轮受同宿主竞争约束（`results/_repo_write_contention.bm-c.json` rc=3 CONTENTION，对端 interactive pid 30500 自 21:54:41 存活）：只落新增文件面，未改 `Tools/s6_chain_bmc.py` / `smoke_test.py` / `ceo_live_usage.py` / `CODELY.md` / 共享看板，未跑 S6 链与全量冒烟。

## 判据清单

| # | 判据 | 证据 | 结果 |
|---|---|---|---|
| 1 | 面可生成（rc0） | `python scripts\etf_book_bond_bear_stress.py run` → 四臂 cagr 8.95/7.72/5.53/3.38，rc0 | PASS |
| 2 | 自检全绿 | `selftest` → **11/11 PASS** | PASS |
| 3 | 漂移守卫可用 | `check` → `check ok: 4 arms, base 8.95% -> flat 7.72%, gate 0.0` rc0 | PASS |
| 4 | **等价闸（本面最重要的门）** | base 臂由逐 bar 分类 P&L 重建后与已发布曲线逐点比对，`max_abs_deviation = 0.0`（<1e-12 才放行，否则 `SystemExit`） | PASS |
| 5 | **父面锚（外部，不自洽）** | base 臂 = `results/etf_equity_alpha.json` `all_classes`：8.95% / 0.913 / -12.54%（本面 8.95% / 0.912 / -12.54%，同轮内 sharpe 4 位小差=父面早一根 bar，明写在面里不隐藏） | MATCH |
| 6 | 分类权重与引擎同源 | 每 bar 的债+货币权重取 `etf_book_defense_spells.mix_timeline` 指派的 mix，不自造权重 | PASS |
| 7 | 冲击只作用在持仓权重上 | selftest 腿：0.252/yr 冲击 × 50% 权重 = 该 bar -0.05%；权重 0 时冲击为零 | PASS |
| 8 | 成本先于收益 | selftest 腿：cost 1% 后接 +10% → 1.089（非 1.10） | PASS |
| 9 | 单调性 | `check` 断言 600bp ≤ 300bp ≤ flat ≤ base 的 cagr 序列有序（3.38 ≤ 5.53 ≤ 7.72 ≤ 8.95） | PASS |
| 10 | 空债腿不冒充结论 | `check` 断言 `sleeve_log_total` 不得为 0（空分类会静默印 0%） | PASS |
| 11 | 债市普查不把空篮子印成平年 | 普查从**首个有合格债/货币标的的 bar（2013-10-10）**起算，2005-2012 的 0.00% 年已剔除并在面里写明理由 | PASS |
| 12 | 窗口口径不混淆 | 滚动一年按**窗口起点**标注（key=`worst_window_start`），不写成"结束日" | PASS |
| 13 | 两个读数并列不折中 | `rule_aware_reading` 印两条拒债路线（无波动目标 14.84%/0.962/-16.04% 与带 8% 目标 10.89%/1.076/-10.56%），并写明二者差在波动目标上，不能当作"拒债值多少" | PASS |
| 14 | 压力臂自称性质 | 面与页面均写明 `level shock`：崩盘发生在买入之后，评分看不到；且 -300/-600bp 是样本未发生的深度，是界不是预测 | PASS |
| 15 | 零网络零重测 | 只读本地面板 + 已发布面 | PASS |
| 16 | 不改已发布面 | 只写 `results/etf_book_bond_bear_stress.json` + `research/ETF_BOOK_BOND_STRESS.md`（均为新件） | PASS |
| 17 | 未做的部分如实记 | 链腿/冒烟腿/CEO 页小节/CODELY 判例卡=共享面，本轮 CONTENTION 未动，记入 state 的 `carrier_debt_r2197` | 如实留账 |

## 本轮读数（cutoff 2026-11-27 · 无波动目标的全类别书 · 1,672 bar）

| 臂 | cagr | sharpe | maxdd | worst year | OOS 2024+ | 100 万终值 |
|---|---:|---:|---:|---:|---:|---:|
| base | 8.95% | 0.912 | -12.54% | -1.17% | 14.55% | 1,825,345 |
| bond_flat | 7.72% | 0.802 | -12.54% | -1.85% | 12.52% | 1,687,912 |
| bond_bear_300bp | 5.53% | 0.594 | -12.54% | -4.28% | 10.27% | 1,464,619 |
| bond_bear_600bp | 3.38% | 0.387 | -14.94% | -6.64% | 8.07% | 1,270,847 |

- 无权益 bar 912/1672 = **54.5%**；债+货币占半数以上的 bar **73.7%**（权重中位 80%）
- 债+货币腿对全书净 log 收益的贡献只有 **13.08%**（78,706 元 / 100 万票）
- 债类等权（2013-10-10 起）最差滚动一年 **-1.00%**（窗口起 2025-11-11），14.7% 的滚动年为负，跌年为 2013 / 2017 / 2026（共 3/14 年）
- 今天（2026-11-27）：债+货币 100%，权益 0% → 书在防守档

## 自捕（本窗实弹）

1. **`check` 里 `(x or 1.0) > 1e-12` 把合法的 0.0 判成失败**（等价闸偏差为 0 时 `0.0 or 1.0 → 1.0`）→ 首跑假红；改成显式 `is None` 判断。falsy-zero 族。
2. **普查首版把 2005-2012 的 0.00% 当成"债市八年不涨"**：那八年根本没有合格的债/货币标的（净值曲线是空篮子）。已改为从首个活跃 bar 起算并印出理由——沉默读成"平"和 r1315 族同病。
3. **`rolling_worst` 的 `worst_end` 实际是窗口起点**，标签与语义反了；已改名 `worst_window_start` 并同步页面措辞。
4. **"腿贡献 11%" 与 "净收益" 混用**：首版用毛 log（未扣 20bp 单边成本）当分母，读到 11.12%；改为净 log 分母（13.08%）并把两个数都写进面。
5. **差点把"拒债 10.89%" 当成本面压力臂的对读**：那条带 8% 波动目标，与本面 base（无波动目标）差了两个变量；已补无波动目标的 `no_bond_equity_mix`（14.84%）并写明二者不可互代。
6. 页面首版有重复半句（"占了半数以上 bar" 连印两遍）与 `%d/-%d` 误印成负号，已修。
