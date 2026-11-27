# QA — r2164 bm-c：换票的「看下一次」时钟学会说过期

## 结论

两条链腿（`swap_trigger` / `swap_toll`）从「输入一动就永久红 / 从不看外面」改成「输入动了说
STALE 并付一次重生、同输入下数字不符仍说 CHECK_FAIL」。契约词审计面的候选数 **19 → 17**。

**已过**：两脚本 selftest（33/33、27/27）；两面真实字节探针 4/4；链 `--only=swap_trigger,swap_toll`
2/2 rc0；毒化后 `+refresh(rc=0,1.3s)` 自愈实证；审计面 `--check ok:true`。

**未过/未做（如实）**：
* 全量 `smoke_test` **未跑完**（06:17 启动，本轮收口时仍在跑），故**不宣称套件总数**。已观测 3 红：
  ①`product: etf_book_permission_persistence` ×2 = `SyntaxError: invalid syntax`，手跑同一命令
  `19/19 PASS`（同树另一执行体在写该文件，属并发编辑瞬态，非缺陷）②`product: chain contract-word
  audit` = `n_candidates re-derives to 17, face says 19`，即本轮的改动本身，已重推导转绿。
* 未跑完整 S6 链（同树另有执行体在飞）。
* 本轮新增的两条冒烟腿（`product: swap trigger …` / `product: swap toll …`）**未在整批里被跑到**
  ——上面的 33/33 与 27/27 是手跑这两条腿的同一命令。

## S0 / S0.5 / S7

* `fleet/machine.json` = **bm-c**。
* `repo_write_contention --lookback-min 45` = **rc 0 CLEAN**（「fewer than two codely hosts alive」）。
  但轮中实证同树**另有执行体在飞**：`Bigmoney-IterationLoop` = Running，python pid 9016（06:23:32 起），
  `state-bm-c.json` 仍是 `round_no=2162`，而工作树上已有 `scripts/etf_book_premium_phases.py` /
  `scripts/etf_book_year_caliber.py` 的未提交改动 + `qa/stale-contract-premium-year-r2163.md`（未跟踪）
  + 方法论卡已追加 r2163 卡。**结论：那个执行体占了 2163，本窗后到让号 → 本窗记 2164**（撞号让路律）。
  竞争探针看不见它是因为它按计划任务跑、不是 codely 宿主 —— 探针口径的已知盲区，逐条写入本轮报告。
* `orphan_face_probe`：`py_faces=3, orphans=0, resident_servers=1`。
* 集团 `origin/main:docs/decisions.md` 原生字节 250,586B / sha256 `79e3083b…` == 自持水位 → 零新决策零动作。
* `fleet/orders`：117 件 / 心跳 `orders_ack` 332 → 未回执差集 0（余为 2026-10-26 前他机 lane 广播，r2066 判例）。
  `fleet/inbox` 空。
* S7：`attrition_ledger_guard scan`、钩子比对、任务存续核验见轮报告（竞争窗只读核验）。

## 改了什么（逐件）

| 文件 | 改动 |
|---|---|
| `scripts/etf_book_swap_trigger.py` | `_digest/_pin/recorded_inputs/drift`；`build()` 写 `inputs.gap`；`check()` 先 `drift()` → `CHECK_STALE` rc3（不重生），再逐字段 → `CHECK_FAIL` rc1；selftest +6 腿（含 2 条端到端） |
| `scripts/etf_book_swap_toll.py` | 同上，锚 `stack` + `trigger` 两份；`run()` 写 `inputs`；`main(["check"])` 三态；selftest +6 腿，`leg()` 支持 detail（仅 FAIL 时打印） |
| `smoke_test.py` | +2 条 product 腿（两脚本 `selftest`，离线） |
| `results/_r2163bmc_swap_stale_probe.py` | 真面探针（钉 sha → 问 check → 恢复并断言字节恒等）。按 `.gitignore:257 _r[0-9]*` 的既有规矩**留在盘上不入 git**（新轮脚本 birth gate），副本输出 `results/_r2163bmc_swap_stale_probe.json` 同律；下文所有读数是本轮实跑值 |
| `results/chain_contract_word_audit.json` | 重推导：19 → 17 候选 |

## 自捕（本轮）

1. `replace` 工具两次把 `old_string` 的结尾换行吃掉，导致 `def _refuse(face, why):    face[...]` 行内合并、
   以及 `print(...)    for n, v in legs:` 粘行 —— 都是紧接的读取立刻发现并修。教训：单行锚不要带尾随换行；
   每次替换后立刻读回受影响区域（已在两份脚本上照做）。
2. 首版 `leg(name, cond, detail)` 与消费端 `for _, v in legs` 的二元解包不匹配，自检路径当场暴露 → 改成三元并
   只在 FAIL 时打印 detail。
