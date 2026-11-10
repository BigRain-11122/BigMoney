# 同一根 bar，两本账（2026-11-10）

这一根 bar 上只有一本账，不是有账读不出：估值面自报 NO_NEW_BAR、from_bar=2026-11-10 与本 bar 相同、last 为空 —— 执行行已经占了这根 bar，accrual 只在执行行之后的 bar 估值，所以「同一根 bar 两个 k」这个前提当前不成立。

- 这条腿量的是缺陷不是资产：前提消失时它应当说自己不适用，而不是一直报「读不出」。
- 若某天估值行又落到执行 bar 上（paired-row 复发），status 会退回 uncorroborated 并重新出表报警。
