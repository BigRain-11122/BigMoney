# 移仓的代价：这本书一年能吞下多少执行成本

判决 **DECAY_DOES_NOT_BITE** —— execution cost is not what sizes this book -- at the desk rung the roll keeps almost all of the carry

证据截止 2026-11-25 ｜ 面 `results/idx_fut_carry_impact_decay.json`

## 一句话

carry 是一年挣多少；移仓成本是每次换月要付多少。这两件事从来没在同一行里出现过，所以 41.785%（六手）这种数字下面没有任何执行成本。本面只回答一件事：**一侧最多能花多少 bp，超过它这本书就不值钱**，并把一个声明过的冲击模型放在旁边做对照。

## 预算（纯算术，用已发布的面）

| 品种 | 尺子 | carry 元/手·年 | carry 占名义 | 预算 bp/侧 | 预算 bp/整次移仓 | 冲击交叉点数 | 桌面上手数处的保留率 |
|---|---|---|---|---|---|---|---|
| IC | published | 31844.9 | 2.76% | 32.9 | 65.7 | 35573.5 | 99.3% |
| IC | calendar | 111341.7 | 9.65% | 114.9 | 229.8 | 434873.2 | 99.8% |
| IC | strictest | 111687.8 | 9.68% | 115.2 | 230.5 | 437581.3 | 99.8% |
| IM | published | 62386.9 | 5.74% | 68.3 | 136.7 | 197466.9 | 99.7% |
| IM | calendar | 129990.9 | 11.96% | 142.4 | 284.8 | 857300.3 | 99.8% |
| IM | strictest | 124991.2 | 11.50% | 136.9 | 273.8 | 792622.3 | 99.8% |

绑定读数是每个品种**最差的那把尺子**（账不能只在自己最好那本上活）。

## 先撞哪道墙（按手数排序）

按手数从小到大排列四个关卡——谁排第一，谁才是今天真正决定这本书能做多大的东西。（本表在首个 `run` 之后补入；上面三个判决令牌未变，令牌仍按原规则计算。）

| 品种 | 排序 | 关卡 | 手数 | 出处 |
|---|---|---|---|---|
| IC | 1 | `capital_at_the_desk_rung` | 2.0 | results/idx_fut_carry_sizing_spec.json via the capacity face |
| IC | 2 | `one_percent_adv_line` | 468.4 | results/idx_fut_carry_capacity_lots.json |
| IC | 3 | `standing_open_interest_at_one_percent` | 1706.5 | results/idx_fut_carry_capacity_lots.json (a position bound, not a trade) |
| IC | 4 | `rule_impact_equals_budget` | 35573.5 | this face: declared square-root rule, worst ruler |
| IM | 1 | `capital_at_the_desk_rung` | 2.0 | results/idx_fut_carry_sizing_spec.json via the capacity face |
| IM | 2 | `one_percent_adv_line` | 752.1 | results/idx_fut_carry_capacity_lots.json |
| IM | 3 | `standing_open_interest_at_one_percent` | 2798.6 | results/idx_fut_carry_capacity_lots.json (a position bound, not a trade) |
| IM | 4 | `rule_impact_equals_budget` | 197466.9 | this face: declared square-root rule, worst ruler |

- **IC**：执行成本要等到 **35573 手** 才和 carry 打平（1% 线的 76 倍、standing OI 的 20.8 倍、桌面档位的 17787 倍）；也就是说，桌面上那个大数字不是被成本否掉的，是被资本与名义上限否掉的。
- **IM**：执行成本要等到 **197467 手** 才和 carry 打平（1% 线的 263 倍、standing OI 的 70.6 倍、桌面档位的 98733 倍）；也就是说，桌面上那个大数字不是被成本否掉的，是被资本与名义上限否掉的。

## 已测量的两个数

- IC：窗口 2026-08-26→2026-11-25（60 个交易日）内移仓 **1 次 → 4.20 次/年**；剔除移仓日后的日波动 **194.3 bp**（用 58 个干净收益算）
- IM：窗口 2026-08-26→2026-11-25（60 个交易日）内移仓 **1 次 → 4.20 次/年**；剔除移仓日后的日波动 **215.1 bp**（用 58 个干净收益算）

## 手数阶梯（绑定尺子 = IC:published、IM:published）

**IC**（ADV 103615 手/日，容量 468.4 手 @1%，桌面档位 2.0 手）

| 手数 | 占 ADV%/日 | 规则冲击 bp/侧 | 预算 bp/侧 | 保留率 |
|---|---|---|---|---|
| 1 | 0.0003% | 0.2 | 32.9 | 99.5% |
| 2 | 0.0006% | 0.2 | 32.9 | 99.3% |
| 5 | 0.0016% | 0.4 | 32.9 | 98.8% |
| 10 | 0.0032% | 0.6 | 32.9 | 98.3% |
| 25 | 0.0080% | 0.9 | 32.9 | 97.3% |
| 50 | 0.0161% | 1.2 | 32.9 | 96.3% |
| 100 | 0.0322% | 1.7 | 32.9 | 94.7% |
| 200 | 0.0643% | 2.5 | 32.9 | 92.5% |
| 400 | 0.1287% | 3.5 | 32.9 | 89.4% |
| 468 | 0.1507% | 3.8 | 32.9 | 88.5% |

**IM**（ADV 163010 手/日，容量 752.1 手 @1%，桌面档位 2.0 手）

| 手数 | 占 ADV%/日 | 规则冲击 bp/侧 | 预算 bp/侧 | 保留率 |
|---|---|---|---|---|
| 1 | 0.0002% | 0.2 | 68.3 | 99.8% |
| 2 | 0.0004% | 0.2 | 68.3 | 99.7% |
| 5 | 0.0010% | 0.3 | 68.3 | 99.5% |
| 10 | 0.0020% | 0.5 | 68.3 | 99.3% |
| 25 | 0.0051% | 0.8 | 68.3 | 98.9% |
| 50 | 0.0102% | 1.1 | 68.3 | 98.4% |
| 100 | 0.0204% | 1.5 | 68.3 | 97.7% |
| 200 | 0.0409% | 2.2 | 68.3 | 96.8% |
| 400 | 0.0818% | 3.1 | 68.3 | 95.5% |
| 752 | 0.1538% | 4.2 | 68.3 | 93.8% |

## 这个面拒绝打印什么

- actual market impact: daily bars carry no depth (r2095 refused the same number)
- whether the published carry already deducts a spread line: printed as-is, per ruler
- fill probability beyond the 1% ADV line: a share above 1% is a rule breach, not a price

## 规则（声明在先，不是结果）

- `impact_k` = 0.5
- `impact_model` = bp = k * sigma_daily_bp * sqrt(lots / (adv * roll_days)) -- RULE, not measurement
- `roll_days` = 3
- `sessions_per_year` = 252
- `budget` = carry_cny / (rolls_per_year * 2 * notional) -- one roll = two sides of one notional
- `binding_ruler` = the worst ruler per product, because a book must survive its worst accounting
- `sigma_excludes_roll_sessions` = True
- `lot_ladder` = [1, 2, 5, 10, 25, 50, 100, 200, 400]
