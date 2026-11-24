# 报价翻转普查：r2046 那笔修正到底该走多远

- artifact: `cash_shelf_flip_census`（`--check` 可复算，`--selftest` 可离线自检）
- generated: 2026-11-24T14:02:35+0800 ｜ evidence_cutoff: 2026-11-20
- 窗口: 2020-07-16 .. 2026-11-20 ｜ 家族 111 只（money/bond/convertible），可定价 108 只

## 问题

across every money / bond / convertible ETF in the panel: which carry a print that is both r2046's flip shape and large against that instrument's own daily movement, what does neutralising those do to its annualised return, and does r2046's repair stay inside the one shelf that earned it。

## 为什么需要第二把尺

r2046 冻结的翻转形状是**绝对**的：单 bar 跌 50bp、3 bar 内回到原价 5bp 内。
对一只日波动 4bp 的货币 ETF，这是 12 个自身 sigma；对一只日波动 65bp 的转债 ETF，
这是普通的一天。只按形状修，会把 511380 的 23 次正常波动一起中和掉，
把它的年化往**反方向**推动一个多百分点。

所以本面把形状原样保留，只加一把尺：每一对都按**该标的自己的日收益标准差**记账，
`sigma >= 4` 才算异常打印（这是可读性下限，不是显著性检验；每一对的 sigma 都印出来）。

## 读数

<!-- FLIP-CENSUS:BEGIN -->
**Verdict: `ANOMALIES_ARE_NAMED_NOT_SYSTEMATIC`**  
**Tags: `THE_GEOMETRY_OVERREACHES`, `R2046_REPAIR_IS_CONFIRMED_BY_ITS_OWN_SIGMA`, `THE_FLIP_OUTWEIGHS_THE_MARGIN`, `MONEY_CLASS_MATCHES_A_FACTOR_FUND`, `MONEY_SERIES_CARRIES_UNCAUGHT_JUMPS`**  

Window 2020-07-16 .. 2026-11-20. Family 111 instruments, **108 priced** (>= 250 bars), of which **69 clean** and **39 labelled** (see the last table). The frozen flip shape fires on **12 clean instruments / 56 pairs**; the sigma ruler (>= 4 own daily sigmas) calls **6 instruments / 6 pairs** anomalous. Panel repair applied first: 169 prints above 35%.

| class | priced | shape fires | anomalous | shape pairs | anomaly pairs |
|---|---|---|---|---|---|
| bond | 50 | 9 | 4 | 18 | 4 |
| convertible | 2 | 2 | 1 | 37 | 1 |
| money | 17 | 1 | 1 | 1 | 1 |

### Anomalous prints (>= 4 own sigmas)

| code | name | class | anomalous pairs | biggest sigma | daily sigma (bp) | effect on its own CAGR (pp/yr) |
|---|---|---|---|---|---|---|
| 511360 | 短融ETF海富通 | money | 1 | 32.58 | 3.21 | -0.167677 |
| 551580 | 科创债ETF泰康 | bond | 1 | 7.48 | 6.92 | -0.017312 |
| 551900 | 科创债ETF招商 | bond | 1 | 6.98 | 7.65 | -0.028908 |
| 551030 | 科创债ETF鹏华 | bond | 1 | 6.52 | 8.03 | 0.199014 |
| 511260 | 十年国债ETF国泰 | bond | 1 | 4.50 | 14.50 | 0.053430 |
| 511180 | 可转债ETF海富通 | convertible | 1 | 4.23 | 48.91 | 0.314746 |

Shape-only (normal moves this ruler keeps out): `511270`, `511380`, `511520`, `511030`, `511090`, `511130`

### The five shelves r2046 prices

| code | effect (pp/yr) | effect (CNY/yr) | share of its yearly extra | r2046 published (days) | on this line (days) | delta (days) | margin left (days) |
|---|---|---|---|---|---|---|---|
| 511360 | -0.167677 | -947.79 | 44.4% | 13.09 | 18.89 | 5.80 | 1.11 |

- `511380`: no pair on either ruler
- `511880`: no pair on either ruler
- `511010`: no pair on either ruler

### Labelled rows (kept out of every verdict)

| code | name | labelled | daily sigma (bp) | why |
|---|---|---|---|---|
| 159201 | 自由现金流ETF华夏 | suspect_class | 65.0 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 159221 | 现金流ETF嘉实 | suspect_class | 62.2 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 159222 | 自由现金流ETF易方达 | suspect_class | 62.9 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 159223 | 现金流ETF永赢 | suspect_class | 66.7 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 159225 | 现金流ETF银华 | suspect_class | 68.1 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 159229 | 自由现金流ETF广发 | suspect_class | 65.3 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 159232 | 自由现金流ETF南方 | suspect_class | 62.4 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 159233 | 自由现金流ETF平安 | suspect_class | 60.4 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 159235 | 中证现金流ETF大成 | suspect_class | 62.1 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 159236 | 自由现金流ETF工银 | suspect_class | 60.5 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 159276 | 现金流ETF汇添富 | suspect_class | 66.5 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 159399 | 现金流ETF国泰 | suspect_class | 60.8 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 511600 | 华安日日鑫ETF | suspect_series | 25.6 | a money-market fund whose own series jumps this wide |
| 511620 | 货币ETF国泰 | suspect_series | 27.3 | a money-market fund whose own series jumps this wide |
| 511670 | 华泰天天金ETF | suspect_series | 40.4 | a money-market fund whose own series jumps this wide |
| 511770 | 金鹰增益货币ETF | suspect_series | 54.7 | a money-market fund whose own series jumps this wide |
| 511820 | 鹏华添利ETF | suspect_series | 29.5 | a money-market fund whose own series jumps this wide |
| 511910 | 融通货币ETF | suspect_series | 30.5 | a money-market fund whose own series jumps this wide |
| 511920 | 货币ETF广发 | suspect_series | 36.9 | a money-market fund whose own series jumps this wide |
| 511930 | 货币ETF国联 | suspect_series | 39.2 | a money-market fund whose own series jumps this wide |
| 511950 | 添利货币ETF广发 | suspect_series | 34.8 | a money-market fund whose own series jumps this wide |
| 511960 | 货币ETF嘉实 | suspect_series | 35.0 | a money-market fund whose own series jumps this wide |
| 511970 | 国寿货币ETF | suspect_series | 45.2 | a money-market fund whose own series jumps this wide |
| 512130 | 全指现金流ETF鹏华 | suspect_class | 64.8 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 516460 | 现金流ETF800鹏华 | suspect_class | 63.7 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 560120 | 中证500现金流ETF华夏 | suspect_class | 76.9 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 561080 | 全指现金流ETF华安 | suspect_class | 62.2 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 561870 | 现金流全指ETF华富 | suspect_class | 60.9 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 562080 | 300现金流ETF华宝 | suspect_class | 62.1 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 563390 | 全指现金流ETF华泰柏瑞 | suspect_class | 60.4 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 563580 | 自由现金流800ETF万家 | suspect_class | 64.5 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 563620 | 全指现金流ETF兴业 | suspect_class | 62.0 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 563680 | 800现金流ETF汇添富 | suspect_class | 65.1 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 563760 | 全指现金流ETF中银 | suspect_class | 61.4 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 563770 | 全指现金流ETF招商 | suspect_class | 60.3 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 563780 | 现金流全指ETF方正富邦 | suspect_class | 61.7 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 563830 | 全指现金流ETF博时 | suspect_class | 65.6 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 563900 | 300自由现金流ETF摩根 | suspect_class | 57.3 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
| 563990 | 800现金流ETF富国 | suspect_class | 65.7 | the classifier's name rule matched 现金 in a free-cash-flow equity ETF |
<!-- FLIP-CENSUS:END -->

## 怎么读

- `shape` = r2046 几何形状命中数；`anomalous` = 其中 >= 4 个自身 sigma 的。
  两者差距就是「只按形状修」会误伤多少正常波动。
- `effect on its own CAGR` = 只中性化异常对之后的年化 − 原样年化。
  这是**该不该修**的读数：非异常对的修正不是修正，是篡改。
- `effect in days` 把修正换算成该货架自己每天的超额，再和 r2046 留下的余量比。

## 不宣称

1. 不解释翻转成因（份额折算 / 做市报价 / 数据源 amend 都可能）；
2. 只覆盖一种形状：单 bar 深跌 + 3 bar 内回到原价 5bp 内；
3. sigma 是窗口内的常数，不做时变波动率；
4. 家族外品种不在射程（权益类的 35% 翻转另有其规则）。
