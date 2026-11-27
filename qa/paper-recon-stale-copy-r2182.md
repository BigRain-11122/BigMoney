# QA · 纸盘对账面 R3「BREACH」实为一根 bar 的搬运时差（r2182）

## 触发

风控块 **C5_paper_recon** 长期 RED：`results/paper_equity_recheck.json` 判词 `BREACH`，
detail=`verdict=BREACH != PASS`，on_red=「账面不可信」。四名交易员各差 3.3k–7.9k 元。

## 诊断（机检，非推测）

| 交易员 | 账本 equity | 记分卡搬运值 | 差 | 用**上一根 bar** 收盘重算 |
|---|---|---|---|---|
| COMPOSITE-CE-01 | 982,830.47 | 975,414.18 | −7,416.29 | **975,414.18**（差 0.00） |
| COMPOSITE-CE-02 | 977,953.38 | 970,377.70 | −7,575.68 | **970,391.47**（差 −13.77，rel 1.42e-05） |
| ENGULF-CE-01 | 988,834.31 | 980,892.81 | −7,941.50 | **980,892.80**（差 +0.01） |
| VOLATILITY-CE-01 | 990,675.40 | 987,413.72 | −3,261.68 | **987,413.71**（差 +0.01） |

`results/strategy_scorecard.json` 的 `generated = 2026-11-27T02:29:56`，而账本
`cutoff = 2026-11-27`（该 bar 15:30 才完整）。**02:29 写的搬运面不可能包含 11-27 的收盘**，
四张卡全都逐位等于「11-26 收盘 + 今天的现金」→ 这不是账面算错，是复制件比账本老一根 bar。

## 修法（判据，不是放宽）

`scripts/paper_equity_recheck.py` 的 R3 由「一律字面等账本」改为三态：

1. `bar_copyable(generated, cutoff)`：记分卡生成时刻 ≥ 该 bar 日 15:30 → 可搬运，字面比对不变（真违约照红）。
2. 生成时刻早于收盘 → 允许「差一根 bar」，但**必须自证**：用 `data/daily` 中同一文件族的上一根 bar
   逐名重算（`prior_bar_equity`），相对差 ≤ `1e-4` 才记为 `STALE_BY_GENERATION`；
   一根 bar 的波动是 1e-3~1e-2，1e-4 把「同一根 bar」与「另一个数」分开。
3. **老于收盘却连上一根 bar 都对不上 → 仍然 BREACH**（它既不是今天也不是昨天）。
4. 面里逐员印 `scorecard_cny / ledger_cny / prior_bar_equity_cny / 两个差 / rel`，
   stdout 也逐行印 `STALE-COPY`——沉默会被读成干净（r1852 族）。

缺失 `generated` 或缺 `cutoff` 时 `bar_copyable` 返回 None，**回到严格字面比对**（不发明陈旧性）。

## 证据

- `python scripts\paper_equity_recheck.py selftest` → **19/19**（新增 R3b/R3c/R3d 三条行为腿：
  收盘前旧件=披露不判死 / 旧件又对不上上一根 bar=仍判死 / 收盘后旧件=按当日账本判）
- `python scripts\paper_equity_recheck.py run` → `verdict=PASS traders=6 problems=0 reader_stale=4`，rc0
- `python scripts\block_board.py` → **green 23 / red 3**，`red_blocks=[W1_supply, G6_ingest, P1_cpu_fill]`（C5 已出红）
- 冒烟覆盖本面的两条腿（`--selftest` / `run`）本轮直接执行同命令，均 rc0；全量套件未跑（约 1,142s，见轮报告）

## 未处置（如实）

- 记分卡本身仍是 **bm-a 单写面**（r378 单机执笔守卫），本机无法缩短它到 1 根 bar 以内的滞后；
  本面现在的职责是**把滞后说清楚**而不是把它算成违约。
- COMPOSITE-CE-02 有 13.77 元残差（rel 1.42e-05）：小于一根 bar、大于分位舍入，面里原样留数未解释；
  它落在 1e-4 容差内，但它不是零——下轮若要追，从该员今日的成交/现金变动查。
