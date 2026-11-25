# QA — carry 暂停规则价格面（r2104 · bm-c · 竞争窗轮）

| 项 | 结果 | 证据 |
|---|---|---|
| 脚本可跑 | PASS | `python scripts/idx_fut_carry_pause_price.py run` → 写 JSON+MD，exit 0 |
| 幂等 / 自检 | PASS | `--selftest` **14/14 OK**；`check` → `OK … verdict=WRITTEN_LINE_IS_THE_EXPENSIVE_ONE` |
| 行为腿（不是自洽腿） | PASS | selftest leg 4：停牌必须落在触发日的**下一根**（look-ahead 会落在同一根）；selftest leg 8：手改一位数字 → `CHECK FAILED` 且不出现 `STALE` 字样（r1850/r1934 合同） |
| 负控 / 正控 | PASS | `python results/_r2104bmc_pause_price_negative.py` → **5/5 ALL_CONTROLS_PASS**（C1 真坏腿会触发且省钱 +5.17pp；C2 关规则=恒等；C3 always-paused 天花板；C4 恢复条款；C5 从面上两个数独立重算 cost） |
| 跨面口径一致 | PASS | 本面 IC 8.6423% / IM 9.9648% vs `results/idx_fut_carry_risk.json` 8.642% / 9.965%（差 ≤0.0003pp）。首版用 252 天/年，读成 8.94%，被对照抓出——已改为 import `idx_fut_basis.TRADING_DAYS`（244） |
| 无未来数据 | PASS | 决策窗口止于 close t，暴露作用于 t+1；触发日列表逐日落盘可复核 |
| 无网络 | PASS | 只用本地面板 + 既有面（`product_spread` 走缓存） |
| 无共享面写入 | PASS | 竞争窗纪律：只新增 4 个文件面，未动 state/心跳/STRATEGY 文档/引擎/链 |

## 本轮自捕两枚

1. **单位错**：`rolling_cum` 用小数累加，却拿去和写作 `-2pp` 的线比较 → 首版 6 个阈值全是「0 次停牌」，空表格就是症状。改为在累加后 ×100 硬算，selftest 三条腿的阈值同步换成 pp 量纲。
2. **两把尺子**：年化分母写死 252（本部惯例是 244），同一序列本面 8.94% / risk 面 8.64%。改为 import 权威常量，并把「跨面对照」写成面上的一行永久字段（`cross_face`）。

## 交付件

- `scripts/idx_fut_carry_pause_price.py`（run / check / selftest）
- `results/idx_fut_carry_pause_price.json`
- `research/IDX_FUT_CARRY_PAUSE_PRICE.md`
- `results/_r2104bmc_pause_price_negative.py` + `results/_r2104bmc_pause_price_negative.json`

## 未完成（如实记）

- 未接进 `Tools/s6_chain_bmc.py`（竞争窗禁改共享面；且该文件本轮被别宿主改动）。
- 未把「连续 N 根确认」写进 `research/STRATEGY-20261125.md` / `scripts/policy_engine.py`（同为共享面，等独占窗）。
