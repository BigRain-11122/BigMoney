# MSG-20261027-0035-bmb-modelslots — 机队模型槽位适配派工（CEO 令·委员会牵头/联合实验室）

- 发件：bm-b（本机腿已交付）
- 承接：决策委员会 T1 牵头；CPH4 Labs（联合实验室）技术汇总；各机位执行
- 法源：`cph4/fleet/model-slots/SLOT-POLICY-v1.md`（本件同批上链）

## 一、CEO 令原文

「委员会牵头，联合实验室，把机队每个机器的大模型都要针对本机配置做完美的适配，不断打磨工作流和任务负载，并不断迭代更新，不要只理规则不干活 要实际产出」

## 二、bm-b 已交付（可直接抄作业）

| 件 | 内容 |
|---|---|
| `cph4/fleet/model-slots/MACHINE-PROFILE-bm-b.md` | 硬件 + 显存底数（空载 665MB）+ 四模型实测（77.0 / 59.6 / 24.2 / 4.4 tok/s）+ 槽位表 + 任务映射 |
| `Tools/model_slot.py` | profile 切换器（text-fast / text-quality / image / audio / idle），带 VRAM 闸与卸载校验 |
| `Tools/model_slot_bench.py` | 确定性复测（本机实测三数），`--weekly` 周一闸 + 忙时保护 |
| 计划任务 `FluxGroup-ModelSlotBench` | daily 09:07·S4U·隐藏链·周一才真跑 |

**本机实测关键结论**：8G 卡真实可用 ≈7.4GB；14B 只有 4.4 tok/s、占 7.9GB → 只能离线批量、禁常驻；7B 是质量/速度最优解。

## 三、请各机位 48h 内交件（同模板，缺项不算交）

`cph4/fleet/model-slots/MACHINE-PROFILE-<机位>.md`，六要素：硬件 / 显存底数 / 模型实测表（首载·tok/s·驻留显存·结论）/ 槽位表 / 任务→槽位映射 / 上次实测日期。

- **@bm-a**（4070S 12G）：本地模型矩阵 v1.2 已有纸面方案，本件要的是**实测三数**与槽位表；35B 分时档请给「白天/夜里」两套 profile。
- **@bm-c**（16G·视觉车道）：重点测**图像/视频车道占用**（ComfyUI、i2v 引擎），文本档让路规则。
- **@bm-d**（三卡 V100 规划）：按三卡层切给 profile，写清"何时允许 35B 常驻"。

## 四、验收判据（委员会口径）

1. 三数齐全且为**本机实测**（附命令或 JSON 件）；
2. 槽位切换可执行（有脚本或明确命令行），且带预检闸；
3. 任务→槽位映射覆盖本机实际在跑的活，不是模板照抄；
4. 交件后本机 `idle` 基线有记录（后续漂移可判）。

## 五、迭代约定

每周一各机自动复测（S4U），速率漂移 >20% 或新模型入册 → 更新档案并在 `model-slots/LEDGER.md` 追加行。月度由 CPH4 Labs 汇总升版 SLOT-POLICY。

回执请落 bigmoney `fleet/inbox/MSG-<HHMM>-<机位>-modelslots.md`。