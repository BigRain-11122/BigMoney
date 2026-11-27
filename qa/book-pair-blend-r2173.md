# QA —— two books, one wallet (r2173 · bm-c)

产物：`scripts/book_pair_blend.py` · `results/book_pair_blend.json` · `results/book_pair_blend.md` · `research/BOOK_PAIR_BLEND.md`

## 1. 自检

```
python scripts/book_pair_blend.py selftest
selftest: 19/19 PASS
```

腿清单（每条都问一个会失败的问题）：

| 腿 | 问的问题 |
|---|---|
| L1 | 统计能跑出数（没有静默空面） |
| L2 / L2b | 两本独立的书 50/50，夏普必须高于各自，波动必须低于各自 |
| L3 / L3b | 同一本书配两次＝零增益，且判词必须是 NO_FREE_LUNCH（不是 DIVERSIFICATION_PAYS） |
| L4 | 完全反向的两本书混合成平线（波动 0） |
| L5 / L5b | w=0 与 w=1 必须逐位复现两个父面 |
| L6 / L6b | 对齐只取交集，空交集必须拒绝而不是编日期 |
| L7 / L7b | 相关在 [-1,1]，自身相关必须为 1 |
| L8 / L8b | 加一本亏钱的书，混合必须低于那本好书，且判词不许叫增益 |
| L9 | 短切片拒绝年化（不出荒谬数） |
| L10 | 父面内的成本必须压低 CAGR，不许被丢掉 |
| L11 / L11b / L11c | 契约词：戳一致→ok 且不含 STALE；戳动一格→STALE+rc3；面缺→STALE+face missing |

L2 的首版用抽样序列，实际均值偏离设定值 3.5 个标准误，腿红了 —— 改成「先标准化再指定均值/标准差」的构造，腿才有意义。这是自检抓到的真问题，不是调参。

## 2. 真面读数（重叠窗 2020-01-03 → 2026-11-26，1671 bar）

- 全 ETF 9.87% / SR 0.969 / MDD -10.1% / vol 10.47%
- 全转债 6.30% / SR 0.532 / MDD -22.6% / vol 12.93%（同窗；全史 7.35%/0.758）
- 30/70 → 9.07% / **SR 1.066** / **MDD -9.3%** / **vol 8.59%**
- 相关：日 0.0899，月 0.1435，19/82 月同跌
- 判词 **DIVERSIFICATION_PAYS**（SR 增益 +0.108）

## 3. 父面复现（这是本面不许出错的一条）

| 父面 | 面公布 | 本面复算 | 差 |
|---|---|---|---|
| cb N20/R20/10bp | 7.3548% / 0.7581 / -22.588% | 7.3548% / 0.7581 / -22.588% | 0.0 / 0.0 / 0.0 pp |
| etf nobond_vt08 lag1 | 9.86% / 0.973 / -10.11% | 9.86% / 0.973 / -10.11% | 0.0 / 0.0 / 0.0 pp |

端点对账（reconciliation）：w=0 → 9.87% vs etf 9.86%（match）；w=1 → 6.30% vs cb 6.29%（match）。

## 4. 契约（链只给 STALE 付钱）

毒化实证：

```
# 把面里 etf 面板的 size 加 1
STALE: etf panel bytes moved since this face was written (102429B@… -> 102428B@…)
CHECK_RC=3
# 跑 run 重写
{"ok": true, "problems": [], "window": "2026-11-26", "verdict": "DIVERSIFICATION_PAYS"}
CHECK_RC=0
```

重算一致性：两次 run 除 `generated_at` 外 JSON 逐字段相同（浮点已 round 到 10 位，抖动 ~1e-15 不落面）。

## 5. 接线

- `Tools/s6_chain_bmc.py` 新腿 `book_pair_blend`（check 0.1s / run ~55s）
- `python Tools/s6_chain_bmc.py --only=book_pair_blend` → `0 book_pair_blend 0.1s {ok:true…}` rc0
- 加腿后契约词面重生成：`n_legs 397 / n_writer_legs 140 / n_candidates 13 / n_permanent_red 0`，`--check` ok:true
- 写者审计：`chain has 397 legs` → 重生成 → `4 faces checked, 4 known check-only, 0 newly paired` rc0

## 6. 未验证（如实）

1. 两个钱包之间的调仓成本未建模。
2. 重叠窗 6.9 年 ≠ 转债书 19.4 年，属近年结论。
3. 最优权重样本内挑选（乐观偏差）。
4. 父面各自未验证清单照旧。
5. 本窗未跑全量冒烟（r2172 的分离冒烟已完结：793/794，唯一 FAIL 是契约词假红，本轮复跑 ok:true）。
