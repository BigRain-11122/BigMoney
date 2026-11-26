# QA — 分红面学会说过期（r2165 / bm-c）

日期：2026-11-27 06:5x–07:0x
执行体：bm-c 交互会话（single host；`repo_write_contention --lookback-min 45` rc=0 CLEAN）

## 问题（出生地：check 层）

`scripts/etf_book_dividend_credit.py` 的 `--check` 过去只做一件事：**从自己发布的 arms 重算
`dividend_credit` 的减法**。于是面板滚了两根 bar（面停 2026-11-24、面板 2026-11-26），
check 仍打印 `check ok: lag1 credit +0.33 pp/yr` —— 它定价的那本书已经没人持有，
而链腿看到的是一张「绿着冻住」的面（r1935 族：只会重算自己的守卫没有「我过期了」这个状态）。

## 修法

1. 面里记下自己定价的那根 bar：`inputs.panel_last_bar`（写者自己声明，r1311 字节级身份的极简版）。
2. 新增廉价外部锚 `panel_bar()`：读冻结 core48 的 48 个 CSV 尾行取最大日期（**0.004 s**；
   `E.build_panel()` 同口径要 **42.5 s**，不能每轮付）。
3. `drift()` + `check(payload=None, live="disk")`：
   - 面板 bar 变了 → `check STALE: …` + 逐行点名，**rc3**（链只为 STALE 付写者，r1850）；
   - 面里没记锚 / 锚读不出 → 同样 rc3（「不知道在跟谁比」≠「我很好」）；
   - 锚一致但自家减法不符 → `check FAIL` **rc1**，**不带 STALE 字样**（r1934 双词钉死）。

## 证据（全部实跑）

| 腿 | 结果 |
|---|---|
| `selftest`（原 5 腿 + 新 4 腿） | **9/9 PASS** |
| 真面探针 `results/_r2165bmc_dividend_stale_probe.py --json` | **4/4 PASS**（同锚 rc0 / 未来锚 rc3+STALE / 探针后字节恒等 / 面记 bar==evidence_cutoff） |
| 重建后 `--check` | `check ok: lag1 credit +0.33 pp/yr, coverage 26.6%` **rc0**（1.6 s） |
| 链单腿（fresh） | `etf_book_dividend_credit 1.5s check ok …` **1/1 rc0** |
| **自愈付钱实证** | 把 `inputs.panel_last_bar` 毒化到 `2026-11-24` → 同一条链腿 `69.9s … +refresh(rc=0, 67.0s)` **rc0** |
| 重建确定性 | arms / dividend_credit / coverage / verdict / per_name / records / live_picks / inputs / evidence_cutoff **逐块与毒化前备份恒等**（仅 `generated` 变） |
| 契约词审计面复算 | `n_candidates 17 → 16`，`--check {"ok": true, "problems": []}` |

## 数字（重建后，bar 2026-11-26）

- lag1 分红信用 **+0.33 pp/年**（lag0 +0.35），覆盖 26.6%
- lag1 执行罚 **1.03 pp/年**；分红/执行 = **0.32**
- 判词 **DIVIDENDS_ARE_NOISE**（与上一代一致：分红不是这本书的钱）

## 未做/未验证（如实）

- 全量冒烟本轮两次启动均未跑完（06:47 起一次、07:03 起一次；无汇总行），**不宣称套件总数**；
  已观测两条红均为本面改动引起的审计面代差，重算后 `--check` 转绿。
- `ah_panel` 采样尾条（`fleet: a panel tail read by sample is certified against a full scan`）
  = r2159 起就记下的欠账，本轮未动。
- `etf_book_voltarget_phase` 等剩余 16 条结构风险腿只在审计面 rows 里点名，本轮未动。
