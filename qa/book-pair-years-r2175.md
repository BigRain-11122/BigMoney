# QA —— 钱包的每一年：三列同起点、部分年、防守那一半 (r2175 · bm-c)

产物：`scripts/book_pair_years.py` · `results/book_pair_years.json` · `results/book_pair_years.md`
接线：`Tools/s6_chain_bmc.py`（新腿 `book_pair_years`，紧跟 `book_pair_blend`）

## 1. 这一面要解决的问题

父面 `results/book_pair_blend.json` 有逐年字段（`best.yearly`、`parents.*.in_window.yearly`），
但三列的 2020 起点不同：转债/ETF 从 2020-01-03，组合从 2020-01-06。并排读者会把
「+10.76% vs +7.29%」读成 3.5pp 的业绩，而共同起点上是 +9.96% 对 +7.29%（0.80pp 的差是
被剪掉的 01-03 那天两本书各跌约 0.8% 造成的）。

## 2. 自检

```
python scripts/book_pair_years.py selftest
selftest: 23/23 PASS
```

| 腿 | 问的问题（答错就红） |
|---|---|
| L1 | 一年只出一行 |
| L2 | 共同起点取三列中最后那个首 bar |
| L3 | raw 保留各列自己起点（构造 +21% 的年） |
| L4 | 共同起点切掉首 bar（+10%） |
| L5 | gap = common − raw，单位 pp |
| L6 | cushion 是 blend − cb 的 pp |
| L7 | 全部 cb 负年都被托住 → 判词 DIVERSIFICATION_CUSHIONS_CB_DOWN_YEARS |
| L8 | ETF 无负年 → untested 旗为 True |
| L9 | **blend 在 cb 负年更差时，判词不得是「托住」**（predicate 会返 False） |
| L10 | ETF 有负年 → untested 旗清掉 |
| L11 | 部分托住 → CUSHION_PARTIAL |
| L12 | 跨两年的构造都出行（防止只测了一年） |
| L13 | 短年（60 bar vs 243）判 partial |
| L14 | 折算年化 == `(1+r)^(244/bars)−1` |
| L15 | 完整年不带折算年化 |
| L16 | w=1 端点上 blend 年收益 == 转债年收益 |
| L17 | w=0 端点上 blend 年收益 == ETF 年收益 |
| L18 | 年平均是平均不是合计 |
| L19 | 对账容差 1e-6 能拒掉 1e-3 的差 |
| L20 | 父面依赖的两个数没变 → 不报问题 |
| L21 | **父面权重从 0.30 变 0.35 → 必须 STALE** |
| L22 | **父面窗口末日变 → 必须 STALE** |

L20-L22 是这一面最容易被写错的地方：父面每轮重跑，时间戳每次都动。若按时间戳判依赖，
这条腿会每轮付一次完整重建（~60s），为一个没变的东西（r1935 同族）。所以依赖改成记两个数
（`best.w_cb` 与 `window.last`），并用三条腿钉死「数字没变不报、数字变了必报」。

## 3. 契约实测（现场锚，不是宣称）

```
python scripts/book_pair_years.py check       -> ok rc0（0.1s，只 stat 两个面板字节 + 读两个数）
python scripts/book_pair_years.py run         -> 7 年 / verdict DIVERSIFICATION_CUSHIONS_CB_DOWN_YEARS / mismatch 0
python scripts/book_pair_years.py run         -> 再跑一次（除 generated_at 外逐字段相同）
毒化 data/cb_panel.csv.gz 的 mtime −7min
python scripts/book_pair_years.py check       -> STALE rc3（点名 25433554B@11:34:31 -> @11:27:31）
还原 mtime
python scripts/book_pair_years.py check       -> ok rc0
```

## 4. 与父面的对账

`raw_*` 必须逐字等于父面已发布的逐年（`parents.cb/etf.in_window.yearly` 与 `best.yearly`），
容差 1e-6。本轮三列 × 7 年 = 21 个点，**不一致 0 处**。

这一条不是装饰：它证明本面读的是父面发布的那两本书，而不是自己另建了一本。

## 5. 链与审计

```
python Tools/s6_chain_bmc.py --round 2175 --only=book_pair_years
0 book_pair_years  0.1s  ok rc0
chain: 1/1 rc0

python scripts/chain_contract_word_audit.py        -> n_legs 400 / n_writer_legs 143 / n_candidates 13 / n_permanent_red 0
python scripts/chain_contract_word_audit.py --check -> ok:true problems:[] n_current 13
python Tools/chain_writer_audit.py --check          -> 4 faces checked, 4 known check-only, 0 newly paired
```

链腿 check 实测 **0.1s**：这正是设计要的——数据没动时只花两次 stat 加一次读两个数。

## 6. 未验证（如实）

1. 两袖之间的调仓成本未建模（各自 10bp 已在父面）。
2. 重叠窗只占转债书 19.4 年里的 6.9 年。
3. 30/70 是父面样本内最优，本面继承这份乐观。
4. **ETF 书在这 7 年里没有负年**，所以「组合能扛 ETF 的坏年」是未观测的——这是本面最重要的
   诚实项，写在判词句子里而不只在未验证清单里。
5. 只读最后一根 bar 的名单，换仓后需重跑父面与本面。
