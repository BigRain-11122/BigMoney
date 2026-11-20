# 流动性筛选面：同一批分数，去掉装不下名额的名字

证据截止 2026-11-19 · 门 100 万口径 · 每名需要 ADV 2000.0万 · 槽位 5 · 调仓 20 日

## 判词：SUBSTITUTION_NOT_SEPARABLE

15/84 次调仓里，在印书的五个名字有一个装不下每名 20.0万 的名额；加闸后容量最薄日从 27.8万 抬到 100.1万，低于透镜的调仓从 17% 降到 0%；但收益差读不出（B-A 0.0015 pp/月 t=0.076，B-R 0.0183 pp/月 t=0.442）——容量是机械买到的，收益是中性的，别把它当 alpha 卖。

| 臂 | 年化 | 夏普 | 回撤 | 容量中位 | 容量最薄 | 容量低于门槛的比例 |
|---|---|---|---|---|---|---|
| A 在印书 | 11.38% | 1.122 | -10.56% | 133.9万 | 27.8万 | 16.7% |
| B 加流动性闸 | 11.40% | 1.126 | -10.56% | 145.0万 | 100.1万 | 0.0% |
| R 随机换同样多 | 11.15% | 1.105 | -10.56% | 138.5万 | 27.8万 | 13.1% |

## 配对读数

- B-A 月度：0.0015 pp/月，t=0.076（82 个月）
- B-R 月度：0.0183 pp/月，t=0.442（82 个月）
- 闸触发：15/84 次调仓发生了替换，共换 20 个名字

## 诚实边界

- capacity is bought MECHANICALLY by B: every floored pick clears the need by construction, so the uplift ratio is not evidence -- the open number is what the substitution costs (paired B-A) and whether it beats random (paired B-R)
- the panel is a survivors sweep (r1319/r1874): names the source never served could not have been ranked, so they cannot appear in any arm
- entry_lag=0 is the published behaviour, kept so arm A reproduces every printed face; the same one-bar gift applies to all three arms
- the fallback dates are listed, not hidden: a book that could not fill five deep slots is a different animal from a wide one
- nothing here is adopted: this face prices the rule
