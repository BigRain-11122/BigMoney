# QA —— 两书之间搬钱的成本：多久搬一次、成本吃不吃得掉 (r2176 · bm-c)

产物：`scripts/book_pair_rebalance.py` · `results/book_pair_rebalance.json` ·
`results/book_pair_rebalance.md`
接线：`Tools/s6_chain_bmc.py`（新腿 `book_pair_rebalance`，紧跟 `book_pair_blend` /
`book_pair_years`）· `smoke_test.py`（腿：moving money between the books is priced）

## 1. 这一面要解决的问题

`book_pair_blend` 的 caliber 行自己承认：两本书之间搬钱的成本没有建模（"a reader who moves
money between them pays it"）。于是父面印出的 1.066 是一个「免费每日再平衡」的数，读者无法
照着执行。本面把这项成本定价：六种日历节拍 × 每边 5/10/20bp × 0.1-0.9 权重网格。

## 2. 自检

```
python scripts/book_pair_rebalance.py selftest
selftest: 23/23 PASS
```

| 腿 | 问的问题（答错就红） |
|---|---|
| A1 | 不搬时，涨得快的那本书权重必须上升 |
| A2 | 不搬的臂不得声称搬过钱（moves/turnover 双零） |
| B1 | 单根 bar 的漂移是精确解析值 0.33/1.03 |
| B2 | 首根 bar 不得触发 every20 |
| C1 | 同一节拍下，付费版的年化必须低于免费版 |
| C2 | 付费版与免费版的搬运次数相同（成本不改变路径） |
| C3 | 费率翻倍 → 拖累约翻倍（容差 0.5pp，二阶效应在内） |
| D1 | 摆动序列上，每 20 bar 的换手多于年度（路径变差随采样频率增长） |
| D1b | 且这笔换手真的降年化 |
| D2 | 季频的搬运次数多于年频 |
| E1 | 月频恰好每次换月触发一次 |
| E2 | 净值路径有限且为正 |
| F1 | 两本同一本书时漂移恒为零 |
| G1 | 无节拍优于持有时判词 HOLDING_IS_ENOUGH |
| G2 | 只有免费才赢 → COST_EATS_THE_GAIN |
| G3 | 真赢 → REBALANCE_PAYS |
| G4 | 赢在 tie 带内 → REBALANCE_PAYS_A_LITTLE |
| H1 | 面板戳与目标数都对 → rc0 且不印 STALE |
| H2 | 父面板字节动 → STALE + rc3 |
| H3 | **父面目标权重从 0.30 变 0.40 → STALE**（不许静默沿用） |
| H4 | 面缺失 → STALE + face missing |
| I1 | 每根 bar 免费搬回目标 ≡ 静态权重 blend（对账的算术基础，容差 1e-6） |
| I2 | 且它每根 bar 都搬一次 |

H3 是这条面最容易写错的地方：目标权重是从另一张面读来的数字。若按那张面的**字节**判依赖，
父面每轮重跑（generated_at 变）都会让我们付一次 60s 重建；若完全不判，父面改了权重我们会
静默沿用旧目标。所以判据是**数字**：`best.w_cb` 与 `window.last` 变了才 STALE（r1935 同族）。

## 3. 契约实测（现场锚，不是宣称）

```
$ python scripts/book_pair_rebalance.py check
{"ok": true, "problems": [], "target_w_cb": 0.3, "verdict": "REBALANCE_PAYS"}   # rc0

$ python scripts/book_pair_rebalance.py run
  hold       moves  0  turn/yr 0.00  CAGR 8.87% SR 1.043 MDD -8.9% drift 8.9pp
  quarterly  moves 27  turn/yr 0.05  CAGR 9.12% SR 1.065 MDD -9.3% drift 5.3pp
  VERDICT REBALANCE_PAYS (best paid quarterly, SR vs holding +0.022)
  daily zero-cost arm SR 1.0662 vs blend page 1.0662 (diff +0.0000)
```

对账腿（I1 + 面内 `reconciliation`）：本面每日免费臂 1.0662 与父面 30/70 的 1.0662 差 0.0000，
证明两张面读的是同两本书；`recovery` 字段把「付费节拍拿回的只是纸面数」写成一句话并带两个数。

## 4. 已知缺口（如实）

- 节拍是 in-sample 挑的（同一窗口选同一窗口评）→ 面内 `unverified` 第一条；
- 搬钱按 bar 收盘计价，读者实际下一开盘搬；
- 税 / 底层买卖价差 / 整手网格不在成本里（整手见 `cb_book_ticket_floor`、
  `paired_book_ticket`）；
- 2x 每边是下限，真账户搬大额更贵；
- 父两书的未验证项照旧（ETF 池幸存者、转债收盘成交、2026 单一 regime）。

## 5. 交付面

- `results/book_pair_rebalance.json` / `.md`（读者面，含表格、漂移故事、敏感度、权重网格）
- `research/BOOK_PAIR_REBALANCE.md`（判读）
- 链腿：`book_pair_rebalance`（check 0.1s / run ~65s，只在面板或目标数变了才付）
- 冒烟腿：`product: moving money between the books is priced, and a tie is not a gain (r2176)`
