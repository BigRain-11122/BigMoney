# T-35 纸盘每日导出面 — 城侧/总部只读消费契约 · schema `t35_paper_export_v1`

> O-20260924-2045 s3 · 票 T-2026-09-24-35 d3 · D-20260925-05 数据面前置（M2 09-29 依赖）：HQ P-78 v5 量化区与硅基城交易员实况面在 09-29 真数据窗前即可按本契约开发联调。
> 消费纪律：**只读探针，禁写本目录**；schema 字段增补=append-only（新字段可加，既有字段不删不改义）；消费稳定锚=顶层 `schema` 字段。

## 1. 文件面

- `latest.json` — 最新日快照（与当日 `export-YYYY-MM-DD.json` 字节恒等）。
- `export-YYYY-MM-DD.json` — 逐日历史快照，append 不改写。
- 刷新节律：每交易日 15:00 收盘 bar 落地后的维护链跑一次（`scripts/t35_paper_export.py run`）；确定性幂等零网络（重跑字节恒等，无墙钟字段）；非交易日无新快照。

## 2. 顶层字段

`schema / ticket / deliverable / law_ref / export_date / evidence_cutoff / generated_from_state_updated / traders[6] / marks_face / summary / prior_diff_source / prospect_note / display_law / no_future_data / missing_faces / audit`

- `export_date`＝数据面日期（=evidence_cutoff）；`generated_from_state_updated`＝纸盘 state 最后写入时刻。

## 3. traders[]（6 在册交易员，每人 100 万 CNY 纸盘本金·O-2045 s1）

- `trader` — 交易员 ID（=firm 注册件成员号，如 `COMPOSITE-CE-01`）。
- `capital_cny` — `{initial:1,000,000.0, equity, positions_value, cash, denomination:"CNY"}`。
- `open_positions[]` — `{symbol, quantity, cost_price, last_close, hold_days, market_value_cny, unrealized_pnl_cny}`（symbol=ETF 代码）。
- `positions_count` — 持仓数。
- `operations_today[]` — `{action:"entry"/"exit", symbol, quantity, cost_price}`；来源见 `operations_source`：次日起=前日导出差分链（`prior_diff_source` 指向前件），首日快照=hold_days≤1 入场派生、出场不可派生（summary `exits_not_derivable_first_snapshot` 诚实旗）。
- `metrics` — `{paper_start, bars, months_tracked, current_dd, num_trades_window, win_rate}`（纸盘计分面，10-01 首检后逐月累积）。
- `regime_guard` — `{mode, active_from}`（锚定门禁态；enforce 激活=2026-10-01，CEO 令 T0 日界，勿手改）。
- `state_cutoff / state_updated` — 引擎 state 截止与写入时刻。

## 4. marks_face（盘中道末次 tick 摘要）

`{file, ticks, last_tick_ts, last_tick_kind, source, per_trader_equity_mark_cny{trader: equity_mark}}` — 盘中道本体 `results/paper/marks/marks-YYYYMMDD.jsonl` 为 **gitignored 本地道**（09:25-15:00 工作日 10min tick + 15:00 settle），跨机消费以本摘要字段为准，勿直读本地 jsonl。

## 5. summary / 边界条款

- `summary` — `{traders, total_equity_cny, total_positions, entries_today, exits_today, exits_not_derivable_first_snapshot}`。
- `prospect_note` — PROSPECT 观察员（22 员，allocation_pct==0）构造性排除（O-2045 观察仓 0；晋升即自动带 100 万）。
- `no_future_data` — 闭式 bar 信号（T 收盘→T+1 开盘成交）；marks 仅估值用途，永不作信号输入。
- `display_law` — 呈现中性化归渲染侧（CEO 2026-09-23 敏感面律：公开面不放涨跌%/K线/汇率）；本数据层带金额 CNY 全量，渲染层自行决定显隐；CEO 一句话可改直显。
- `audit` — `{engine_runs:0, ledger_trials_added:0, network:"zero"}`（纯本地 state 读，零引擎零网络）。

## 6. 变更记录

- v1（2026-09-25）：D-20260925-05 前置契约发布（R94 d3 导出机制基础上冻结字段面；BM-A R106）。
