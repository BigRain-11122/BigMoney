# QA 卡 · 节奏差「起跑日 vs 行情段」分离面（r2130）

**实物**
- `scripts/etf_book_cadence_regime_split.py`
- `results/etf_book_cadence_regime_split.json`
- `research/ETF_BOOK_CADENCE_REGIME_SPLIT.md`

## 验收项

| # | 项 | 证据 | 结果 |
|---|---|---|---|
| 1 | 离线自检全绿 | `... selftest` | **18/18 PASS** |
| 2 | 面自洽 + 外部锚（面板 sha1） | `... check` ×2 | **CHECK_OK REGIME_SPLIT_CONSISTENT cells=142 holes=50**（rc0 ×2） |
| 3 | 幂等 | run → sha256 → run → sha256 | **字节恒等 True** |
| 4 | 零重实现 | import `etf_book_cadence_start_dates.build_inputs` + `etf_variants_null_rolling.fast_next_open` | 引擎与面板均从家族导入，无复制 |
| 5 | 薄格具名不充零 | `holes` 50 条（2 本书以下季度 + 3 季度以下书 + 薄切片） | 全部点名；`excluded_thin_segments` / `excluded_thin_starts` 双列 |
| 6 | 双成本档一致 | 8bp 与 1bp | 两档同为 `REGIME_DOMINATES | BOTH_CHANNELS_READ` |
| 7 | 自检夹具能双向证伪 | 腿 4/5（路径主导/行情主导）、腿 6/7（薄格排除）、腿 8（缺通道不可分） | 修过一次：初版夹具 3 点几何 < 四分位最小 4 点 → 判 `NOT_SEPARABLE`，已改为 4×4 真实几何并补第 4 条腿 |

## 已知限制（不掩盖）

- 通道样本量不对称（路径 11 季 vs 行情 6 本），极端季度会拉偏中位；
- 2025H2 段内极差 5–10 pp 大于全年中位，本面明确不宣称"起跑日不重要"；
- 幸存者 / 无波动目标 / 2020 冬天不在本面射程——三项在面内 `honest` 与本卡同时印出。

## 未做（如实）

- 未接 S6 链腿与 smoke 腿（本轮竞争窗 rc=3 CONTENTION，`Tools/s6_chain_bmc.py` 与 `smoke_test.py` 属禁改共享面）；
- 未跑全量冒烟，不宣称套件总数。
