# DIGEST r1613 bm-b — E585：票面上的现金腿是「整窗均值」，不是它旁边那根 bar 的利率

**卡号** E585 · **面** `results/state_tilt/CASHLEGPRICE-2026-11-06.json` + `cashlegprice_latest.json`
**脚本** `scripts/e585_cash_leg_pricing.py`（selftest 28/28 · build/check/verify 全绿）
**接线** S6 腿 `cash_leg_pricing`（rc0 0.04s）· smoke 块 `# E585` · 本窗腿检 `_r1613_legcheck.py`（PASS）

## 问的是什么

E583 量的是票上的**股数**腿按哪根 bar 定价（4/5 张票按 2026-10-14 决策 bar 定价，而文件名写 10-23..10-28）。
每张票还带一个现金腿块，长这样：

```
{"source": "data/repo_daily/GC001.csv", "mean_accrual_ann_pct": 2.09, "missing_bar_steps": 0}
```

它读起来像一个利率。本轮问：这个数是不是它旁边那根 bar 上的 GC001 报价？

## 读数

- 生产者把它算成 `BW.repo_daily_cash(idx, rates).mean() * 252 * 100`，`idx` 是**整个 2020-01-01..cutoff 的活窗**。
  所以公布的是**扩窗均值**，不是任何一根 bar 的报价。
- 5 张带块的票印着 **2.079%..2.090%/yr**（跨窗只动 **1.1bp**，因为它只是窗口变长）；
  而这 5 张票命名的那几根 bar 上，GC001 收盘是 **1.015%..1.090%**（**7.5bp** 跨度）——
  印出来的数是它旁边那一刻利率的**最高 2.06 倍**。
- 3/5 张的命名 bar 在回购面板上有报价（10-23/10-26/10-27）；另 2 张（10-28、11-06）**命名 bar 已超出回购面板**
  （面板末 bar 2026-10-27，bm-a 车道的 `update_repo` 落后 ETF 面板 7 根）。
- `repo_daily_cash` 对没有报价的步子**计 0 且只记数**，于是 11-06 那张票在窗口末 **7 步现金一分不计**，
  按最后一次报价折算的上界是 **160.19 CNY**（cash_amount 529,072 × 1.09%/252 × 7）。
- 分类：`the_number_is_the_whole_window_mean` 3 · `named_bar_not_on_the_repo_panel` 2 · `no_cash_leg_block` 1（10-28-card 的 cash_leg 是字符串标签）·
  `the_number_is_the_bar_it_names` **0**。

## 三条可复用教训

1. **名字像利率不等于它是利率。** `mean_accrual_ann_pct` 里的 "mean" 是它唯一的线索，而它关于的是一整段窗口；
   同一张票上「股数用哪根 bar」和「现金用哪段窗口」是两根轴，E583 查了前者，后者没人查过。
   判据必须落在「这个数等于哪根 bar 的报价」这种可比事实，而不是字段名。
2. **跨票差异可能只反映窗口长度，而不是票的差别。** 2.090→2.079 单调下行看着像「利率在跌」，实际只是
   后 10 根低利率 bar 被并进分母。任何「同一字段跨文件小幅漂移」的读法，先问漂移量是不是窗口效应：
   本面给出 `window_mean_spread_bp`（1.05bp）与 `bar_rate_spread_bp`（7.5bp）并排，两者相差 7 倍。
3. **「缺报价计 0」是一条会静默吃钱的记账规则。** 它把数据延迟伪装成零收益；本轮把缺步数与它的人民币上界
   一起公布（上界不是测量，点名 disclosure）。只要上游面板落后，每张新票都会在末段少计。

## 边界

只读票文件 + `data/repo_daily/GC001.csv`；不改任何票、不改 `etf_book_order` 的现金腿算法、不记 ledger 行。
「现金腿该印成 bar 报价还是窗口均值」是产品决策（另一轮的 prereg），本轮只测事实。
`window` 起点 2020-01-01 是从生产者代码读出来的（`idx` 起于引擎网格），不是猜的——重算值与已发布值逐张吻合到 3 位小数
（2.090/2.090/2.089/2.088/2.079）即为该起点的证据。