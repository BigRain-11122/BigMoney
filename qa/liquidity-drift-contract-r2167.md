# QA — r2167 流动性双面「过期契约」

轮次：r2167（2026-11-27，bm-c）。对象：`scripts/etf_book_liquidity_select.py`、
`scripts/etf_book_liquidity_era.py`、`results/_r2167bmc_liquidity_drift_probe.py`。

## 一、判据（修复前先写死的三条）

1. **漂移必须叫 STALE**：面板滚 bar 或门面改尺 → `check` rc3、stdout 含 `STALE`——
   否则链的 `run_leg` 不会付钱重修（r1850 契约词）。
2. **缺陷不许喊 STALE**：输入没动而发布数字重算不出来 → rc1、stdout **不含** `STALE`
   （r1934 双词判例）。
3. **不知道也要说**：面里没有任何外部锚 → rc3，不许把"无法老化"读成"健康"。

## 二、实测（命令 → 结果）

| 命令 | 结果 |
|---|---|
| `python scripts/etf_book_liquidity_select.py selftest` | 18/18 PASS（新增 L13-L18 六腿） |
| `python scripts/etf_book_liquidity_era.py selftest` | 16/16 PASS（新增 L14-L16 三腿） |
| `python results/_r2167bmc_liquidity_drift_probe.py` | 10/10 PASS，退出码 0 |
| `python scripts/etf_book_liquidity_select.py check` | rc0 `{"ok": true, ...}`（重建后） |
| `python scripts/etf_book_liquidity_era.py check` | rc0 `{"ok": true, ...}`（重建后） |
| `python Tools\s6_chain_bmc.py --only=liquidity_select_write` | rc0，**59.8s 含 +refresh(rc=0,55.1s)**（毒化后自愈实证） |
| `python Tools\s6_chain_bmc.py --only=liquidity_era_write` | rc0，1.5s fresh |
| `python scripts/chain_contract_word_audit.py run` | candidates **16 → 14**，verdict 不变 |
| `python scripts/attrition_ledger_guard.py scan` | CLEAN（4 账本，3 条历史 shrink healed 照录） |
| `python scripts/pool_dualrun_reconcile.py run` | ZERO-DRIFT（747 entries，streak 51） |

## 三、真面探针的十个问题（每张面五问）

- 毒化 `inputs.panel_last_bar=1999-01-01` → rc3、首行 `check STALE: …`；
- 按原字节复原 → 逐位相同**且** rc0；
- 毒化 `inputs.gate.lens_cny=1.0` → rc3、含 STALE（第二个锚真的被读）；
- 毒化一个**发布数字**（select：`share_of_rebalances=0.987`；era：
  `full_window.substitution.rebalances=999`）→ rc1、首行 `check FAIL:`、不含 STALE；
- 收尾断言：两张面回到盘上原字节（`byte-identical`）。

## 四、自捕（三枚，均已修）

1. **探针首版把纪元腿毒在错位置**：写 `full_window.substitution.rebalances`，而
   `check` 当时只比对 `full_window.rebalances` → rc0，探针当场判自己 FAIL。修法不只是
   改探针：两张抄写同一个数的字段，检查必须都看得见（已加一行比对）。
2. **`replace` 又一次吃掉行尾换行**，把
   `doc[...] = 999` 与 `write_face(...)` 并到同一行 → 探针脚本 SyntaxError、静默不产出，
   而 `results/_r2167bmc_liquidity_drift_probe.json` 留着**上一趟**的结果，看起来"跑过了"。
   判据：改完必须回读脚本片段确认行结构（r2164 同族第二次）。
3. **探针写面用临时 `open()` 未显式关闭**：子进程可能在缓冲落盘前读同一文件 →
   判定看见旧内容。改为 `with io.open(...)` 显式关闭。

## 五、未验证（如实）

- **全量冒烟未完成**：CLI 宿主跑会静默死（r2162/r2164/r2165/r2166 同型），本轮另起
  后台分离进程；四条相关腿（两面 selftest + 两面 check）已按**同一条命令**手跑通过，
  但不宣称套件总数。
- 未重跑完整 S6 链（392 腿），只跑点名单腿 + 对账/审计/水位四个固定腿。
- 剩余 14 条结构风险腿未动。
