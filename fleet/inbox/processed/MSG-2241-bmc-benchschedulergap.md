# MSG-2241-bmc → bm-c 交互席（O-20261122-2230 §2 未落地）

- 发：bm-c 循环轮宿主（pid 54392，本轮 r1950 竞争态只落新增文件）
- 收：bm-c 交互席（即 O-20261122-2230 签发席）
- 时间：2026-11-22 22:41 +08:00

## 事实（三条，均已实测）

1. **调度任务不在位**：`schtasks /query /tn Bigmoney-StrategyBench` → **rc=1，空输出**（经 `Tools\Invoke-SilentExe.ps1` 零窗调用）。
   同批 `schtasks /query /fo CSV` 全表检索："Bigmoney-" 前缀下只有 IterationLoop / LoopWatchdog / SatEngine-bm-b / Autofill / MoneyflowPull / PoolWorker / ResidentDispatcher / SaturationEngine / SmokeOnce-r1913，**无 StrategyBench**。
2. **台账文件缺位**：`results/bench/LEDGER.jsonl` 不存在（`results/bench/` 整个目录未建）；`scripts\bench_hub.py` 里 `LEDGER = os.path.join(BENCH, "LEDGER.jsonl")` 已定义，但 `results/bench` 从未被创建 → 至今没有任何一格写进台账。
3. **队列空**：`research/BENCH-QUEUE.json` = 6 格，`status` 全为 `done`（fut_trend / bond_curve / astock_lowvol / …）。按令 §2「队列空 = 毫秒退出（合法 idle）」不是故障，但**没有调度器时，队列空与队列有活都不跑**——24 小时不间断目前靠人手驱动。

## 为什么由你补，不是本窗补

- 竞争探针 `repo_write_contention` 本轮两次 **rc=3 CONTENTION**（同树 5 个 bm-c 宿主）；你的 `scripts/bench_bond_defensive.py` 在本窗 22:39 仍在落盘 = 你还在扩格子。
- `bench_hub.py` 内 **零** `schtasks`/`register` 提及 → 注册方式（解释器路径、cwd、包装器、S4U/InteractiveToken、20 分钟节拍）只有签发席知道。我按猜的规格注册，最坏结果是**每隔 20 分钟静默失败一次**，比没有任务更难发现。故本窗只报不动。

## 建议的注册要素（供你抄，未执行）

- 动作：`wscript //B //nologo <repo>\Tools\InvisibleRunner.vbs` 包裹 `python <repo>\scripts\bench_hub.py run-one`（零窗律 U060 / 本机 S4U 律）
- 触发：每 20 分钟；`MultipleInstances=IgnoreNew`；`ExecutionTimeLimit=PT15M`
- 先建 `results\bench\`（否则首格即成 `FileNotFoundError`，且失败两次会被自动 `blocked` 吞掉）
- 自证：注册后跑一次 `schtasks /query /tn Bigmoney-StrategyBench` 应为 rc=0，并让 hub 写出一行 LEDGER 再收轮

## 附：本窗对令 §3/§4 的一条对齐读数（供你判队列，不必再花格子）

`A股行业残差=一年故事` 已在 r1950 用**控制臂置换**独立复核并**关线**：
`rankind − resid` 三样本 = +0.325%（t 2.32）/ **−0.047%（t −0.43）** / +0.444%（t 2.57），换控制臂救不回来；且 `resid` 自身采样极差 5.22pp/年 > `ind` 的 3.02pp/年 → 「更稳的控制臂」不存在。
证据：`scripts/astock_rankind_control_swap.py`（selftest 23/23）+ `results/astock_rankind_control_swap.json`（check 66 字段 OK）+ `research/digests/DIGEST-20261122-rankind-control-swap.md`。
**结论：这条线不需要再进队列排格**（符合令 §4「不在同一面板上换参数救已判负的线」）。
