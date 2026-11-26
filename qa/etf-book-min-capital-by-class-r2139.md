# QA 证据包 · ETF 书按书种拆开的最小可执行资本（r2139 bm-c）

- 面：`results/etf_book_min_capital_by_class.json`
- 页：`research/ETF_BOOK_MIN_CAPITAL_BY_CLASS.md`
- 生成器：`scripts/etf_book_min_capital_by_class.py`
- 输入（只读消费）：`results/etf_nobond_vt.json`（去债生产候选，票面日 2026-11-25）、
  `results/etf_composite_pf.json`（带债书，票面日 2026-11-06）、面板收盘价（`etf_composite_pf._load_prices`）
- 轮次：2026-11-26 r2139（bm-c，竞争窗：只落新增文件面）

## 一、三腿验收（实跑输出）

| 腿 | 命令 | 结果 |
|---|---|---|
| 离线自检 | `python scripts/etf_book_min_capital_by_class.py selftest` | **14/14 PASS**，rc=0 |
| 出件 | `python scripts/etf_book_min_capital_by_class.py run` | rc=0，两件落盘 |
| 复算 | `python scripts/etf_book_min_capital_by_class.py check` | `check ok: 2 books, cheapest bond_free_production at 10000 CNY, ratio 5.71x`，rc=0 |

## 二、判据（跑前冻结，写进脚本 `judge()`）

- 规则：五只各一手（100 份），券商佣金 `max(5 元, 10bp)`/票（与 `etf_book_lot_ladder` 同口径）。
- 票底判据：每票佣金 ≤ 其自身切片（资本/5）的 **25bp** → `C ≥ 5×5/0.0025 = 10,000`。
- 整手判据：`C ≥ 5 × max(价×100)`。
- 最小资本 = 两道墙取大；`EXECUTABLE_FROM_SMALL_ACCOUNT` 当且仅当 ≤10,000 元。

## 三、读数（本轮实产）

| 书 | 票面日 | 最小资本 | 卡在哪道墙 | 整手墙 | 票底墙 |
|---|---|---:|---|---:|---:|
| bond_free_production（生产候选） | 2026-11-25 | **10,000 元** | FEE_FLOOR_BOUND | 851.50 元 | 10,000 元 |
| with_bond | 2026-11-06 | **57,076 元** | LOT_BOUND | 57,076 元 | 10,000 元 |

比值 5.71 倍。带债书在 10,000/20,000/50,000 档只填满 1/5 只（现金 84-90%）；100,000 档仍留
36.5% 现金。去债书 10,000 档即 5/5 填满、现金 2.55%、最大权重偏离 1.27pp。

## 四、本轮自捕（两枚，均已焊进自检）

1. **阶梯算出负现金**：`ladder` 首版按 `floor(切片/一手价)` 分配后只检查「notional+fee ≤ 资本」的
   单票条件，满仓档位（1,000,000）五票 notional 已近乎吃满，再付 25 元票费就透支 →
   `cash_pct=-0.0007`。`check` 的「spends more than its capital」腿当场抓出。
   正法=`allocate()`：先按等切片取整手，再循环从最大持仓减一手直到含费可付。
2. **拿「佣金占资本单调递减」当不变量**：大资本档 10bp 比例费接管后占比会从 0.0998% 微升到
   0.0999%（notional/资本 比值差），腿假红。正法=只在票底仍占优的档位断言递减，大资本档改为
   断言落在 [9bp, 11bp]。

## 五、未做（如实登记）

- **未接 S6 链腿与冒烟腿**：本轮处竞争窗（`repo_write_contention` rc=3，对端 interactive 宿主
  16:11:45 仍在写 `research/ARBITER-BOARD.md`），`Tools/s6_chain_bmc.py` 与 `smoke_test.py` 属共享面，
  按 r1907 同树多宿主律不动。接线列为下一干净窗首项。
- **未写轮报/心跳**：`fleet/round_reports-bm-c.md` 与 `fleet/machines/bm-c.json` 同属共享面，
  本窗对端持有（16:10:02 写过心跳）。本面走新增文件面落地，简报见轮末对话呈报。
- 带债书票面日 2026-11-06 落后于去债书 2026-11-25：两本书各按自己最近一次选票定价，
  页内已如实标注，不做同日伪对齐。
