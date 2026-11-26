# QA — 两条 cadence 面接链（r2161）

轮次：bm-c r2161 ｜ 时间：2026-11-27 05:0x +0800 ｜ 起因：r2160 收尾时点名的欠账 (a)
「两条无链腿的 cadence 面接链或退役」

## 1. 缺陷（不是猜的，是可查的零命中）

两张已发布面 `results/etf_book_cadence_comparable.json`（r2128 建）与
`results/etf_book_cadence_start_dates.json`（r2126/r2147 建）在**两处**都查不到引用：

    Select-String -Path Tools\s6_chain_bmc.py -Pattern "cadence_comparable|cadence_start_dates"   -> 0 命中
    Select-String -Path smoke_test.py        -Pattern "cadence_comparable|cadence_start_dates"   -> 0 命中

即 r1282 孤儿类的教科书形状：**面发得出来，但没有任何东西会在它的输入前进时重算它**。
后果不是「红」，而是**绿着停在上一条 bar**——r2160 就是在查另一条面时撞见它们报 STALE 才发现。

## 2. 修法（两处，最小面）

1. `Tools/s6_chain_bmc.py`：LEGS 尾部新增两腿 `cadence_comparable` / `cadence_start_dates`，
   形如 `(check, run)`。两条脚本的 `check()` **本来就**用
   `STALE face missing:` / `STALE input panel bytes moved:` / `STALE panel could not be rebuilt:`
   三个句子报告漂移，符 r1934 契约（链只在探针自己说 STALE 时才付一次写）。
   放在 LEGS 尾部的理由：它们读的是本轮前面那批 `results/*.json` 面板，写者在前、读者在后。
2. `smoke_test.py`：新增两条 product 腿跑各自的 `selftest`（离线、零面板依赖），
   钉住「输入动一格必须读成 STALE 而不是读成错答案」这半边——
   若改用 `check`，S1 会在每个面板前进的轮次先红一次（链在 S6 才会补），那是自己造永久红。

## 3. 验证（逐条实跑，不是宣称）

| 检查 | 命令 | 结果 |
|---|---|---|
| 语法 | `python -c "ast.parse(...)"` 两文件 | AST OK |
| 面 1 自检 | `scripts\etf_book_cadence_comparable.py selftest` | `{"legs": 17, "passed": 17, "failed": []}` rc0 0.2s |
| 面 2 自检 | `scripts\etf_book_cadence_start_dates.py selftest` | `{"legs": 24, "passed": 24, "failed": []}` rc0 0.1s |
| 面 1 check | `python scripts\etf_book_cadence_comparable.py check` | `CHECK OK 5 rungs, 200 matched pairs, word=MATCHED_SIGN_HOLDS \| MATCHED_SEPARATION_FAILS \| CROSS_SET_OVERSTATES_BY_3.05x \| CALENDAR_TERM_EXCEEDS_CADENCE_GAP` rc0 |
| 面 2 check | `python scripts\etf_book_cadence_start_dates.py check` | `CHECK OK 42 cells, 22 starts, to_cutoff median -2.630 pp, one-year median -0.210 pp` rc0 |
| 链腿实跑 | `python Tools\s6_chain_bmc.py 2161 --only=cadence_comparable,cadence_start_dates` | `2/2 rc0` 47.1s（腿内 0.2s + 46.7s）→ `results/_r2161bmc_s6_chain.only-cadence_comparable-cadence_start_dates.json` |

## 4. 量出来的代价（写进事实，不藏）

`cadence_start_dates` 的 `check()` 每次要**重建面板**才能按 sha1 判漂移，实测 **46.7s / 轮**；
`cadence_comparable` 的 check 只比字节指纹，**0.2s**。46.7s 在 390 腿的全链里是可接受但不是免费，
若日后收紧，正当方向是让 check 只读已写进面的指纹（r1850 的「新鲜度问外部锚」同族），
不是把这条腿摘掉——摘掉就是回到「绿着停在旧 bar」。

## 5. 未验证（如实）

- **全量 `smoke_test` 未跑完**：本窗 04:57 起跑、至 05:0x 仍在跑（日志 `results\_smoke_bmc_r2161.log`），
  已见 1 条红 `etf_book_supply_gate_decision | STALE 9/10 moved=ticket_permission`，
  该腿在链里是 run-only（每轮无条件重生），已单腿实跑清除（rc0, 0.1s）。
  故本件**不宣称套件总数**，只对新增两腿与实跑过的腿负责。
- 只覆盖 `Tools/s6_chain_bmc.py` 的 LEGS 与 `smoke_test.py` 的产品腿表；
  `scripts/` 下其他已发布面无既有孤儿审计器（本仓没有 `chain_orphan_audit`），因此**「还剩多少孤儿」不可数**。
