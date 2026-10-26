# MACHINE-PROFILE-bm-c — bm-c 模型槽位画像（SLOT-POLICY-v1·实测优先）

- 机器身份：**bm-c**（compute-node / GPU 生产节点）
- 承接：MSG-20261027-0100-bmc-modelslots（委员会牵头 / CPH4 Labs 统筹）
- 实测产物：`results/model_slots/bench-bm-c-latest.json` 与同批时间戳件
- 实测命令：`python scripts/model_slot_bench_bmc.py run`
- 上次实测：**2026-10-27T02:15:10+0800**（本文件由 `scripts/model_slot_profile_bmc.py run` 从该件逐字派生，禁手抄）
- 本轮 bench 标签：`r1294-27b`

## 一、硬件（实测）

| 项 | 实测 |
|---|---|
| GPU | NVIDIA GeForce RTX 3070，**16384 MiB** 显存（bench 前 used 1276 / free 14902，util 0%） |
| RAM | 23.9 GB 总，bench 前可用 **1.57 GB**（留存闸 0.60 GB） |
| bench 后 GPU | used 1267 MiB / free 14911 MiB / util 97% |

**本机关键约束：RAM 只剩 1.57 GB 可用。** bm-c 的 16 GB 显卡装得下 13 GB 级模型，但系统内存装不下「模型常驻 + 桌面/ComfyUI 应用」的叠加，任何 keep_alive=Forever 的大模型常驻都会把本机推向 OOM 或整机卡死。结论：**bm-c 的槽位策略只能是「用完即卸、单模型串行」，禁止常驻。**

## 二、本机模型清单（ollama 实盘）

| 模型 | 权重 |
|---|---|
| `qwen3.8:27b` | 12.24 GB |

## 三、实测吞吐（同一脚本、同一 prompt、temperature=0、n_predict=128）

| 模型 | 状态 | 解码 tok/s（3 次中位） | 预填充 tok/s | 首次加载 | 权重 |
|---|---|---|---|---|---|
| `qwen3.8:27b` | measured | **27.73**（27.80 / 27.68 / 27.73） | 106.36 | 18.16 s | 12.24 GB |

口径：decode tok/s = eval_count / eval_duration from /api/generate. bm-c has NO resident production model (Ollama automation cleared 2026-10-17), so the first-load cost IS measured here (median_first_load_s) and each model is unloaded with keep_alive=0 immediately after. bm-a's bench deliberately cannot do this on its host.

闸门判定（脚本逐模型记录，非人工）：
- `qwen3.8:27b`：vram 14.55GB >= weights 12.24+0.5 and ram 1.57GB >= reserve 0.6

## 四、槽位策略（由上面三节推得，禁凭感觉）

| 槽位 | 用途 | 模型 | 常驻 |
|---|---|---|---|
| slot-1 | 本地推理主力（llm_assist / 轮报告摘要 / 代码一审） | 见上表实测件 | **否**（use-and-evict） |
| slot-2 | 图像/批量生成（ComfyUI 独立占用显存） | 非 ollama | 否 |
| 禁用 | 常驻大模型（keep_alive=Forever） | — | **禁止**：RAM 可用仅 1.57 GB |

实测后常驻列表：[]（空=bench 按 keep_alive=0 卸载，符合本机策略）

## 五、复现与更新

```
python scripts/model_slot_bench_bmc.py run     # 重新测量，写 results/model_slots/
python scripts/model_slot_profile_bmc.py run   # 从最新实测件重派生本文件
python scripts/model_slot_profile_bmc.py selftest
```

