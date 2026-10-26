# MACHINE-PROFILE-bm-a — bm-a 模型槽位适配（SLOT-POLICY-v1·机器腿）

- 交付机：**bm-a**（dev-machine / 量化+集团中枢）
- 法令：CEO 2026-10-27 00:40「把机队每个机器的大模型都针对本机配置做完美的适配…要实际产出」
- 承接：MSG-20261027-0035-bmb-modelslots（委员会牵头 / CPH4 Labs 汇总）
- 实测件：`results/model_slots/bench-bm-a-<ts>.json`（+ `bench-bm-a-latest.json`）
- 实测命令：`python scripts/model_slot_bench_bma.py run`
- 上次实测：**2026-10-27 01:45:57 +08:00**（每轮可复跑，同一脚本同一 prompt）

## 一、硬件

| 项 | 读数 |
|---|---|
| GPU | NVIDIA GeForce RTX 4070 SUPER，**12,282 MiB** 显存 |
| RAM | 93.6 GB 总（本轮空闲 22.8 GB / 24.3%） |
| CPU | 32 逻辑核（CEO 同机办公，留 10% 余量律） |
| 盘 | C: 938 GB 空闲 / D: 3,313 GB 空闲 |
| 角色 | 无双模烧制车道；GPU 现役 = 本地 LLM 常驻（非生成车道） |

## 二、显存底数与实测占用（判据 4：idle 基线）

```
bench 调用前 -> used 11,257 MiB / free 741 MiB / util 22%
bench 调用后 -> used 11,257 MiB / free 741 MiB / util 96%
```

**关键事实（本轮新测得出）**：`ollama ps` 显示 `qwen3:4b-instruct` 以 **7.5 GB / 100% GPU / ctx 16384 / UNTIL=Forever** 常驻，权重仅 2.5 GB —— 4B 模型在 16K 上下文下吃掉 7.5 GB，且 keep_alive 被固定为永久。12 GB 卡因此**只剩 741 MiB 余量**，任何第二个模型的默认结局是**驱逐现役模型**，不是共存。

> 附带勘正（诚实面）：先前心跳/状态里的「35B :8090 常驻 GPU-offload」是**陈旧表述**。本轮实测 `llama-server.exe` 只有**一个**进程，端口 50630，命令行指向 `C:\Users\sjs20\.ollama\models\blobs\sha256-85e4a5b7...`=**ollama 自己的 4B runner 子进程**，不是独立的 35B 服务。`D:\AI\models\qwen36-35b\Qwen3.6-35B-A3B-UD-IQ4_XS.gguf` Test-Path=**False**（与 D-20261026-27 一致）。**禁再宣称 35B 在位。**

## 三、模型实测表（本机实测·同 prompt·temperature=0·n_predict=128）

| 模型 | 首载 | 解码 tok/s（3 跑中位） | 预填 tok/s | 驻留显存 | 结论 |
|---|---|---|---|---|---|
| `qwen3:4b-instruct`（磁盘唯一在册） | **未测**（见下注） | **94.72**（90.76 / 94.72 / 95.07） | 950 / 2,455 / 2,078 | 7.5 GB @ ctx16384 | 本机唯一可用本地档；速度富余，**是槽位占用者而非槽位问题** |
| 35B-A3B（qwen36-35b IQ4_XS） | — | — | — | — | **不在盘上**，无法测；恢复前一切「35B 档」只能是计划档 |
| 其余（7B / 14B / bge-m3 / 视觉） | — | — | — | — | **不在本机 `ollama list`**（本机只有 1 个模型），不估数 |

**首载为何未测**：测首载必须卸载现役模型，而现役模型是生产服务（`Forever` 常驻 + CEO 同机可能在用）。为拿一个数字打断在用服务不符合机队纪律，故如实记 **NOT MEASURED**，不推算、不套用 bm-b 的数字。

**同模型双通道一致性（本轮副产物）**：同一 4B 经 ollama API 测得 94.72 tok/s，经其底层 llama-server `/completion` 测得 91.67 tok/s —— 差 3.3%（HTTP 层与计时口径差）。此后本机报速一律注明通道。

## 四、槽位表（bm-a 现状 + 可用态）

| 槽位 | 内容 | 驻留预算 | 现状 | 预检闸 |
|---|---|---|---|---|
| `text-fast` | `qwen3:4b-instruct` ctx 16384 | 7.5 GB | **在役（Forever 固定）** | 需先 `ollama stop` 其它模型；本槽即默认，无需动作 |
| `text-standard` | 7B 级 | ~6 GB | 空槽（模型未下载） | 入册前须 `ollama ps` 确认无他模型占卡，否则 REFUSE |
| `text-quality` | 35B-A3B（夜间档） | ≤ 11 GB（4B 须先退出） | **缺件**（GGUF 不在盘） | 三件硬门：①落盘校验 sha ②`ollama ps` 空卡 ③RAM 预检 ≥25 GB |
| `image` / `audio` | 生成/语音 | — | 本机**无此车道**（生成在 bm-c/bm-b） | 不建槽，避免空门 |
| `idle` | 全卸 | 0 | — | 与 bm-b `model_slot.py` 同语义，本机缺该脚本（见五） |

## 五、任务 → 槽位映射（覆盖本机真实在跑的活，非模板照抄）

| 本机真实任务 | 走哪个模型 | 槽位 | 备注 |
|---|---|---|---|
| `scripts/llm_assist.py`（本地化路由 L2 摘要/一审） | qwen3:4b | `text-fast` | 高频低险，4B 足够，**禁止**为它上云 |
| BigMoney 轮（S0~S7 循环） | 无 LLM | — | 纯脚本链，零模型依赖 |
| S6 数据/面板链（46 腿） | 无 LLM | — | 零网络派生为主 |
| `solidify`/记忆桶/轮报告 | qwen3:4b（可选） | `text-fast` | 与 llm_assist 同槽 |
| 游戏/看板面（Tuanjie Hub/Editor） | 无 LLM | — | 占 CPU/GPU 但与模型槽无关（实测同窗 GPU util 22-96%） |
| 35B 判断档 | **不可用** | `text-quality`（缺件） | 恢复前禁在天花板位上宣称能力 |

**缺口如实登记**：本机**无** `Tools/model_slot.py` 切换器（bm-b 侧件未下放到 bigmoney 仓）。本轮替代品 = `scripts/model_slot_bench_bma.py`（只做**测量与预检**，不做切换），切换动作在缺件期以显式命令行为准：
```
ollama stop <model>            # 释放槽位（预检：ollama ps 应空）
ollama run qwen3:4b-instruct   # 装回 text-fast
```
不建一个只能切 1 个模型的假切换器。

## 六、白天 / 夜里两套 profile（MSG §三 对 @bm-a 的专项要求）

| 档 | 时段 | 槽位编排 | 依据 |
|---|---|---|---|
| **day**（工作日 09:00-19:00） | CEO 同机办公，GPU 让路 | 仅 `text-fast`（4B @ 16K，7.5 GB）；**不载第二模型**；不跑 35B | AutoYield 让路律 + 10% CPU 余量律；本轮实测「第二个模型的默认结局是驱逐现役」 |
| **night**（19:00-09:00） | CEO 离机 | ① `text-fast` 保留（哨兵/轮用）→ ② 需要判断档时 `ollama stop qwen3:4b` → ③ 载 35B-A3B（≤11 GB，须先落盘 + sha 校验）→ ④ 收工回 `text-fast` | 35B 与 4B **不能共存**（12 GB 卡）；夜间窗也是 35B GGUF 取件的法定窗（D-20261026-27） |

**何时允许 35B 常驻**：仅夜间档，且必须 ①GGUF 落盘校验通过 ②4B 已 stop（`ollama ps` 空）③空闲 RAM ≥25 GB ④当轮无 GPU 生成批在飞。四门任一不过 = 不载。

## 七、下一步（本机自驱，非等派工）

1. 35B-A3B GGUF 取件走夜间窗（D-20261026-27 派 @bm-a 72h）：盘位充足（D: 3,313 GB），来源 hf-mirror / GitHub release，落盘后 sha 校验 → 再实测三数补进本表第三行。
2. 每周一复测：把 `python scripts/model_slot_bench_bma.py run` 挂机（当前为手动腿，接 S6 前先坐实 ≥3 轮漂移 <20%）。
3. 4B 的 `keep_alive=Forever` 是显存黑洞（2.5 GB 权重占 7.5 GB）：候选改 ctx 8192 或 keep_alive=1h，可释放约 3 GB 给夜间 35B —— 需先证 8K 上下文不损 llm_assist 质量，故本轮**只登记不改**。