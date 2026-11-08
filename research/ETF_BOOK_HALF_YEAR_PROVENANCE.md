# 这「2 年」是哪两年：把一句被读了三十九轮的拒因拆开

**结论（一句话）**：供给梯板上的 `years_for_half median 2 vs line 3` 从来没有说过「前置」——
尺子把各年净值**降序**累加到一半，它按定义分不出前后。拆开后看到的是：桌上三本被拒的书，
最大的那一年都是 **2025**（7 年表里最新一个完整年），一本书一半的钱由**一年**供给。
所以「钱早就赚完了」这句话方向反了；真正要问的是「这一年还能不能复现」。

## 1. 被拆的那句话

- 供给日历面（`scripts/supply_calendar_face.py`）每轮印：`nobond_vt08_adopted refused at
  years_for_half median 2 vs line 3 (FAIL)`。
- 阶梯板（`Tools/fill_ladder.py`）把同一句印在 `EXHAUSTED_NO_LAWFUL_SUPPLY` 旁边。
- 桌面的解读（r1429/r1432/r1433 的研究笔记）是「front-loading / 钱早就赚完 / 花钱买宽度」。
- 三十九轮供给地板红（`ready 0 < floor 3`），每一次处置讨论都从这句话出发。

## 2. 尺子到底怎么算（`etf_book_year_caliber.calibers`）

```
vals = 各年净值
half = 0.5 * sum(vals)
k = 0; run = 0
while run < half: run += 降序第 k 年; k += 1
years_for_half = k
```

排序把年份信息**抹掉**了。它量的是「这堆年里有几年能凑够一半」= 集中度，不是「钱是不是早赚的」。
r1426 把这两件事并列写成 "broad (effective years) and front-loaded (half its return from two
years)"——第二半是读法，不是尺子的话。

## 3. 本轮做的事（`scripts/etf_book_half_year_provenance.py`）

对 r1425/r1426 已发布的同一批 **3 本书 × 5 个相位 = 15 格**，用同一个引擎包装
（`candidate_year_gate_phases.arm`，import 不重写）、同一把尺子（`calibers`，import 不重写），
把 `years_for_half` 拆成「是哪几年」：

| 字段 | 含义 |
|---|---|
| `members` | 凑够一半的那几年，**按日历顺序**列出（含各自净值、占比、日历位置） |
| `direction` | `one_year` / `early` / `late` / `interleaved`（判据冻结在 `RULE`） |
| `dominant_year` | 单年最大净值及其占整表净额的比例 |
| `partial_years` / `half_from_partial` | 表里的残年（2026 只有 3/4 个 cohort），以及一半里是否含残年 |

方向判据是**结构性**的（位置阈值 mid±0.5），不是收益阈值——它不可能被"调线"变成一张通行证。
`net <= 0` 印 `no_half`，绝不印「一年解释它」（r1426 同族）。

## 4. 读数

| 书 | 方向（5 相位） | 一半由谁供给 | 主年占净额 |
|---|---|---|---|
| `nobond_vt08_adopted` | `one_year` 2/5 | 2025 单年 +43.06pp（净额 +81.06pp） | 53.1% |
| `nobond_base` | `interleaved` 4/5 | 2020 +22.19pp 与 2025 +53.73pp | 48.8% |
| `nobond_vt08_floor_050` | `one_year` 2/5 | 2025 单年 +42.65pp（净额 +84.99pp） | 50.2% |

`all_classes_published` 没有相位集，按 r1432 口径诚实印「尺子未复读」，不继承别人的句子。

**三件事因此改变**：

1. **没有任何一本是「早期前置」的**：`early` 在 15 格里 0 次。桌面对这个词的用法是错的。
2. **主年是窗口最新一个完整年**：2020 → 2026 的 7 年表里，2025 = 第 6 行，2026 是残年。
   集中度在**末尾**，不是开头。把「集中」读成「花完了」把结论反了个方向。
3. **真正的问题是单年异常值**：一本书一半的钱来自一年，那一年能不能复现是另一个问题
   （2025 的商品袖 +17.6pp 是既有归因面 `etf_book_year_attribution.json` 的读数）。
   这需要自己的预注册批——不是拿 `years_for_half` 的线去砍这本书。

## 5. 接线（读的人真的会看到）

- `supply_calendar_face.half_year()`：从本轮收据纯派生一句，**尺子名不写死**（取当选尺子，
  r1431 口径），书选「梯板上真的有这本候选」的那一本（`book_is_a_candidate` 显式标注），
  收据缺席印 `absent` 不印猜测，无当选尺子则整块不印（r1434 同族守卫）。
- `summary_line()` 与 `write_md()` 都带上这句；`Tools/fill_ladder.py` 把同一句接在
  `window:` 之后——操作员读的是那块板。
- `--check` 逐块重 derive（本轮 `supply_calendar_face` 自检 49→**58/58**），手写即红。
- S6 腿 `half_year_provenance`（0.9s，纯 JSON check）排在 `supply_calendar` **之前**：
  先证明这句话能从它自己的年表重建，再让面去消费它。

## 6. 判决词零变化

4 候选 4 拒 → `NO_CANDIDATE_PASSES_CALENDAR` 不变；梯板 `EXHAUSTED_NO_LAWFUL_SUPPLY` 不变。
本轮只改**拒因的解释**，不改拒本身（r1431 A2：报告变更只能更严，不能放松）。准入规则的任何
改动仍要走它自己的采纳轮（预注册 + 相位自判 + calendar_admitted 闸）。

## 7. 身份腿与复现

- 15/15 格 `years_for_half` 与已发布相位闸收据逐格相同；`net_top2_share` max|d| = **0.0**。
- 收据自洽：每个 `provenance` 块都从**已发布年表**（6 位小数）重算，`check` 0 problem
  （首版从全精度行算 provenance，`check` 在第六位小数上炸——已改成从发布表算，见 `run()`）。
- selftest 15/15：方向读的是成员不是全年（L5）、一半边界 `>=` 与尺子一致（L7）、
  残年随句子走（L8/L15）、净值非正印 `no_half`（L6）、行序无关（L10）、
  规则块里不许有准入线（L12）。

## 复跑

```
python scripts/etf_book_half_year_provenance.py run      # 约 60s，重定价 15 格
python scripts/etf_book_half_year_provenance.py check    # 纯 JSON，<1s
python scripts/etf_book_half_year_provenance.py selftest
python scripts/supply_calendar_face.py run && python scripts/supply_calendar_face.py --check
python Tools/fill_ladder.py explain --dry-run
```