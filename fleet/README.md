# Bigmoney 机队协议 v1.0（fleet/）

> 2026-09-23 建。机制模式移植自 Biggame 08号多机分治协议（本生态多机实战淬炼版：坑#45/#48/#85/X104/U067/U080 全部教训已吸收）。
> **适用**：任何加入 Bigmoney 的机器（用户开发机 / 回测算力节点 / 未来扩容机）。多机并行开发、传资料、共享算力、分配任务，全部以 git 为唯一通道。

## 1. 机器身份与心跳

- **本机身份 = `fleet/machine.json`（本地私有，不入库）**——tracked 身份文件会被跨机合并静默覆写（Biggame X104 实证教训），故只入模板 `fleet/_machine.json.template`。新机接入=拷模板改名填本机 id。
- **每机心跳 = `fleet/machines/<id>.json`，每机只写自己的文件**（零跨机合并冲突，git 同步全机队可读）。每轮循环收尾更新：
  `last_seen / current_task / cpu_cores / ram_free_gb / gpu_vram_free_mb / verdict`
- **verdict 语义**（算力档位，判定永远 INFO 非门禁）：`CPU_BACKTEST_OK`（回测可跑）｜`GPU_ML_READY`（GPU 空闲 ≥6GB，ML 可开）｜`GPU_SHARED_LOW`（GPU 空闲 <6GB，仅小模型/共享态）｜后缀 `|RAM_LOW`（空闲 RAM<15% 本轮禁新开重活）。

## 2. 互相通信

| 通道 | 用途 | 纪律 |
|---|---|---|
| commit message | 每轮一句话成果 | 已成惯例 |
| `CODELY.md` | 共享记忆（全机队共读共写） | **行级追加面**：只追加条目；真冲突按时间序后到让路重锚 |
| `research/` 报告 | 预注册与实证 | 实验前写死、跑后回填 |
| `fleet/inbox/` | 定向消息 | 文件名=`MSG-<时间>-<收件机id|ALL>-<主题>.md`；收件机下一轮拉到后处理，处理完移入 `inbox/processed/` 并在轮报告回复；消息头注明紧急度 |

## 3. 传资料

- **铁律 = git clone（禁文件夹直接复制）**——防携带锁文件/临时态/被忽略物（Biggame 08号传输铁律同源）。
- 库内 ≈105MB（代码+数据+成果+规则+记忆）随 clone 全通；**大资产不入库**：`Money02/`（7.7GB 前代 A 股资产）按需一次性通道拷贝/移动硬盘，各机局部。
- **机队公网互传机制 = `fleet/TRANSFER.md`**（v1.0·2026-09-23 用户令）：git=方案A / croc 公网直传=方案B2 / Tailscale 组网=方案B1（装机须用户授权）/ 云中转=方案C / 离线摆渡=方案D；选型矩阵+编排协议+校验工具 `Tools/transfer_manifest.ps1`（manifest 双侧一致才算交付）。
- 派生文件（`results/dashboard_status.*` 等）**冲突解法=重新生成**（`python -m monitor.build_status`），禁手工合并。

## 4. 任务分配（fleet/tasks/ 认领制）

- **任务单** = `T-<日期>-<序号>-<优先级>.json`，字段：
  `{id, priority(P0修红/P1用户指定/P2回测计划/P3维护), type, spec(预注册引用或参数), status(open|claimed|done|failed), claimed_by, claimed_at, result_ref, created_by, created_at, note}`
- **认领 = 改 `status=claimed` + `claimed_by=本机id` + `claimed_at` 并 commit push——commit 即锁**（U067 同制）。两机同窗撞认领 = 行级手术按 commit 时间序**后到让路**，让路方在轮报告注明。
- **超时释放**：claimed 超 24h 无进展（claimed_at 未刷新）= 任何机器可改回 open 并注明；**failed 必须写死因**；done 必须带 `result_ref`（指向 results/ 或 research/ 产物）+ 按账本纪律记录试验总数 N（BACKTEST_PLAN 三铁律照走）。
- 任务单来源：用户（开发机手写或让 AI 代写）/ 回测计划派生 / 任何机器提案（P2 以下优先级，P1 须用户署名）。

## 5. 共享算力

- **CPU 回测 = 主战力**：各机自跑批量（`python -m tasks.local_runner` / 预注册实验脚本），或用 §4 任务单把大批次拆给多机分跑；每机 worker 上限 = `min(12, 空闲GB/0.5)`。
- **GPU = ML 阶段专用**（BACKTEST_PLAN §四 G 门未过不开）。开 ML 后启用**借算协议**（U080 同制）：任务单标 `🤝借算@机id` → GPU 闲机（心跳 `gpu_vram_free` 达档且无高优自产）按 §4 认领制接单 → 产出落 results/ 随 git 回流 → 借算机批末**当场清本地临时件**（权威副本唯一=git 库内）。
- **本地 LLM（Ollama）各机自装自用**（E:\Minigame\Tools\Ollama 范式）；模型路径/密钥一律本地化、环境变量，禁入库。

## 6. 写域分治（防冲突的根）

| 面 | 写权 | 冲突规则 |
|---|---|---|
| `fleet/machines/<id>.json` | 每机只写自己 | 无冲突（设计使然） |
| `fleet/tasks/*.json` | 认领者 | 撞认领=时间序后到让路 |
| `CODELY.md` | 全机队 | 行级追加，rebase 多数自动合并；真冲突后到让路 |
| `logs/iteration-loop/`（轮账本） | 各机循环 | **多机跑循环时分文件**：`round_reports-<id>.md`（当前单机=`round_reports.md` 沿用）；`state.json` 各机自分（`state-<id>.json`，沿用当前单机名） |
| 根级文档（README/PLAN/HANDOVER） | 低频编辑 | **用户侧为准**，节点侧只读避让 |
| 派生产物 | 谁跑谁写 | 冲突=重新生成 |

## 7. 新机接入（5 步）

```powershell
# 1. 克隆（唯一合法传输通道）
git clone git@github.com:BigRain-11122/bigmoney.git && cd bigmoney
# 2. 本机身份：拷模板并填本机 id（如 bm-a / bm-c）
copy fleet\_machine.json.template fleet\machine.json   # 编辑 machine_id 字段
# 3. 自举（依赖自装+20项自检+总控数据）
python bootstrap.py
# 4. （Windows，可选）装 10 分钟 AI 循环（路径自适应零改动）
powershell -NoProfile -ExecutionPolicy Bypass -File Tools\register_loop_task.ps1
# 5. 首轮自证：fleet\machines\<id>.json 生成 + commit push 成功 = 接入完成
```
- 新机 48h 内向 `CODELY.md` 交首条接入踩坑记录（Biggame U039 义务制）。
- SSH 通用钥匙三件套拷贝法（`~/.ssh/id_ed25519_bigmin` + `.pub` + config 的 github.com 块）= 同生态既定方式，私钥永不入 git。

## 8. 推送规则（X128-lite）

- 默认**直推 main**：S7 `git push`；被拒 → `git pull --rebase` 重试一次 → **再被拒 = 推本机分支 `origin machine/<本机id>`**（成果永不丢，下轮重试 main 或用户机 fold）。
- **禁 force-push**（历史重写须用户逐次确认）；机器分支由用户机或空闲节点 fold 入 main。

## 9. 版本

v1.0（2026-09-23）——首版由 bm-b 建立；修订走 CODELY.md 记录变更理由与日期。

## 10. 集团并联条款（与 Biggame 工程并联管理 · 2026-09-23 用户令）

- **集团 = 两公司并行**：**Biggame**（游戏公司 · 治理 = E:\Minigame\MiniGame 仓库体系：AI总控接口/登记簿/快照/08号分治协议）∥ **Bigmoney**（金融公司 · 治理 = 本仓库：PLAN.md / fleet/README / CODELY.md）。
- **互不越权**：两公司各自仓库各自治理，**互不写对方仓库**（唯一例外=用户直接指令）。
- **互见层**：Bigmoney 总控面板「集团产线」实时读兄弟工程心跳（三游戏循环 + 本机回测循环，`monitor/build_status.py _group()`；兄弟路径不存在=远端机器自动隐藏，可移植性不破）。Biggame 侧对 Bigmoney 的可见性=其全局记忆 + 本机 fleet 心跳。
- **共享机纪律（bm-b 双公司同机并行）**：①任一公司开重活前查空闲 RAM（<4GB 禁新开重活）②GPU 作业走 keepwarm.pause 释放阀（Biggame U020 同源礼仪）③CPU 并行两公司合计 ≤ 物理核-2（Bigmoney 回测 worker ≤12 已限幅，游戏 batchmode 各自限幅为既定配置）④全静默零弹窗铁律两公司通用。
- **协议同源**：本 fleet 协议移植自 Biggame 08 号（坑#45/#48/#85/X104/U067/U080 已吸收）；修订单边各自演进，重大变更经用户互通。
