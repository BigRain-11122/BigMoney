# QA · etf_book_flip_reach（r2147 · bm-c）

面 `results/etf_book_flip_reach.json` · 脚本 `scripts/etf_book_flip_reach.py` · 文档 `research/ETF-BOOK-FLIP-REACH.md`

## 一、可复现

| 动作 | 命令 | 结果 |
|---|---|---|
| 自检 | `python scripts\etf_book_flip_reach.py selftest` | **5/5 PASS** |
| 实跑 | `python scripts\etf_book_flip_reach.py run` | rc0，54.3s，写面 |
| 复核 | `python scripts\etf_book_flip_reach.py check` | **ok**：verdict=FLIP_REACHES_MONEY universe 1532->1532 class_moves=0 dcagr=-1.1500pp dsharpe=-0.1240 max_flip_top5=0 |

`check` 不从盘上重算任何一本书：它只把面里两臂的 `stats` 相减，验证 `money.*` 是减出来的（不是手抄的）、`max_flip_top5_dates` 等于逐标的表的最大值、判词由自身数字推出。

## 二、自检五腿

1. `repair_flips` 的契约：修复后没有任何 >35% 单日（本例最差 0.0），**尾巴仍是原始成交价**（tail ratio = 1.0），而**历史被重写**（head ratio < 0.5）——这条腿同时钉住了「修的是历史、不是最后一笔」。
2. 损坏真的会炸实现波动（raw vol > 3 × fixed vol），这正是「价格笔误 → 席位改变」的机制。
3. 判词阶梯三态各一条：干净面→`FLIP_STAYS_IN_THE_DATA`、只动宇宙/分档→`FLIP_REACHES_MANDATE`、动钱→`FLIP_REACHES_MONEY`。
4. 反例腿：一个把 10pp 缺口藏在 `FLIP_STAYS_IN_THE_DATA` 下的面必须被拒。
5. 反例腿：`cagr_pp` 是手打进去、两臂不支持的值必须被拒。

## 三、本轮自捕（两枚，均已修）

1. **把净值当收益算**：`R.open_to_open_equity` 返回的是**净值曲线**，首版拿它去做 `(1+r).prod()` 算逐年和「最差日」，得出 worst_year = **3.69e76**、最差日 +221%——两个都是把净值当收益的产物。正法：逐年按 `last/first − 1`、日收益按 `pct_change()`，并在代码里把这句写成注释（`stats2` 也是这么算的）。
2. **「列出暴露」不等于「暴露进钱」**：首版把「被持有的翻转窗」当因果结论发布，读数是 2 次暴露 → 但逐年只有 2025 动、2022 一位不动。真因是 2022 那个窗口引擎给的权重≈0。已把这条写进文档「读数二」，不让 2 次的计数冒充 2 次的钱。

## 四、边界（本轮没做的）

- 未改任何共享面（竞争窗 `repo_write_contention` rc=3，对端 interactive 宿主在跑），因此**没有**把 `repair_flips` 升成库级读取契约。
- 未跑全网格（3/5/8 只 × 10/20/40 日），只测生产候选那一格。
- 未跑全量冒烟套件（上一轮已知 771/783 PASS·11 FAIL，唯一红族仍是面代差 + CEO 页确定性腿，与本件无交集）。
- 未写 S6 链腿（改了共享链文件就违反竞争窗约束）；因此本面目前**只发布、未接线**——记为下轮欠账，与 r1934 同族。
