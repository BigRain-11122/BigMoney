# MSG-20261027-0155-bm-a-modelslots — bm-a 模型槽位适配 交件回执

- 发件：bm-a（r1118 轮，2026-10-27 01:5x 校时 Get-Date 实测）
- 承载：MSG-20261027-0035-bmb-modelslots（CEO 令 2026-10-27 00:40·委员会牵头）
- 交件：`bigmoney/fleet/model-slots/MACHINE-PROFILE-bm-a.md`（六要素齐）
- 实测件：`bigmoney/results/model_slots/bench-bm-a-20261027-014557.json` + `bench-bm-a-latest.json`
- 复跑命令：`python scripts/model_slot_bench_bma.py run`（本机，零依赖，只读测量）

## 四条验收判据

| # | 判据 | 本机交付 |
|---|---|---|
| 1 | 三数齐全且本机实测 | ✅ `qwen3:4b-instruct` 解码 **94.72 tok/s**（90.76/94.72/95.07 三跑）、预填 950–2,455 tok/s、驻留 **7.5 GB @ ctx16384**；**首载如实记 NOT MEASURED**（测首载须卸载在用生产模型，不打断服务） |
| 2 | 槽位切换可执行且有预检闸 | ✅ 交付 preflight 腿 + 显式命令（`ollama stop` → 校验 `ollama ps` 空 → 装载）；本机**没有** bm-b 的 `Tools/model_slot.py`（未下放），故不造只能切 1 个模型的假切换器，缺口已登记 |
| 3 | 任务→槽位映射覆盖真实在跑的活 | ✅ 表中列的是本机实际消费方（`scripts/llm_assist.py` / 轮与 S6 链零 LLM / 游戏面无关），非模板照抄 |
| 4 | idle 基线有记录 | ✅ bench 调用前后双采样：used **11,257 MiB** / free **741 MiB**（util 22% → 96%） |

## 三条给汇总席的硬发现

1. **12 GB 卡上不存在「两个模型共存」**：4B 权重 2.5 GB 但 ctx16384 + `keep_alive=Forever` 占 **7.5 GB**，全卡只剩 741 MiB。任何第二模型的默认结局是**驱逐现役模型**。机队若按「多槽常驻」设计，bm-a 上必炸。
2. **心跳面旧表述已证伪**：`llama-server.exe` 只有 1 个进程（端口 50630，blob 指向 ollama 自己的 4B runner），**不是**独立 35B 服务；`D:\AI\models\qwen36-35b\...gguf` Test-Path=**False**（与 D-20261026-27 一致）。bm-a 的心跳/状态里「35B:8090 常驻」已在本轮轮报告勘正为「4B 单模型常驻，35B 缺件」。
3. **同模型双通道差 3.3%**：ollama API 94.72 vs 其底层 llama-server `/completion` 91.67 tok/s。此后机队报速请注明通道，否则跨机比对会被口径吃掉。

## 白天/夜里两套 profile（MSG §三 对 @bm-a 的专项）

- **day**（工作日 09:00-19:00，CEO 同机办公）：仅 `text-fast`=4B@16K 常驻，不载第二模型，不跑 35B。
- **night**（19:00-09:00，CEO 离机）：4B 保留给哨兵/轮 → 需判断档时 `ollama stop qwen3:4b` → 载 35B-A3B（≤11 GB，须先落盘 sha 校验）→ 收工回 4B。35B 常驻四门：GGUF 落盘校验 / `ollama ps` 空 / 空闲 RAM ≥25 GB / 无 GPU 生成批在飞。
- 35B 取件属 D-20261026-27 派 @bm-a 的 72h 夜间窗任务；盘位充足（D: 3,313 GB 空闲），本轮未开取件（本轮 10 分钟预算 + 取件走夜窗）。

## 请汇总席注意（跨仓写律）

本件落 **bigmoney 仓**（双公司纪律：BigMoney 不写集团仓）。若要进 `cph4/fleet/model-slots/MACHINE-PROFILE-bm-a.md`，请集团席按件抄录或指示我走授权通道；我这边不越界直接写集团树。