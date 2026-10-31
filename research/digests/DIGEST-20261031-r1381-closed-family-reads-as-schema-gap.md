# DIGEST 2026-10-31 r1381 (bm-c) — 供给阶梯读错了它自己那条阻断行

## 一句话

池空 169 分钟、供给地板 0<3 的现场，唯一一条阻断写的是「缺 consumer_plan」；
可这条目的预注册状态行写的是**已判决关单（judged-negative 0/3）**。照着这行
补字段，就是把一个已判负的家族按原参数再烧一遍。闸现在按状态行拒，理由是
「已关单」。

## 现场读数（本轮实取）

```
[ladder] machine=bm-c compatible_ready=0 floor=3
[ladder] no lawful supply candidate passed gates -- honest no-op
[ladder]   blocked: INNOVATION-QUOTA-SLOT-3 (consumer_plan missing ...)
```

`compute_audit` 同窗：`pool_ready_count=0`、`supply_streak=169.1min`、
`flags=[pool_starvation, supply_floor]`。

## 两个缺陷

1. **闸通过的理由不对**。`prereg_frozen:` 只看「文件在」+「头部没有草稿标记」。
   关单/撤回是**结论**，不是草稿态，于是「冻结」被当作「可烧」。唯一挡住
   SLOT-3 的是 `consumer_plan` ——一个跟科学无关的 schema 字段。谁想「修」这条
   阻断，只要补一句消费面声明，一个判负家族就复活了。
2. 同一窗口的 smoke 红项（`fleet: GPU face self-consistent on heartbeat`）不是
   陈旧读数，而是**写手没接管嵌套块**：`gpu_chokepoint` 的扁平正则看不见
   `{"gpu": {"free_gb": 14.4, ...}}`，调用方自己的采样直接进心跳并被 merge-only
   永久保留，于是 `gpu.free_gb 14.4` 与 `gpu_free_vram_gb 14.3` 并存，spread
   102.4 MiB，而 `gpu_face_ts` 还是新的——写手跑过了，只是这块不归它。

## 修法

- `Tools/fill_ladder.py`：状态行（r189 权威面）命中 `已判决/关单/RETRACTED/
  撤回/判负终局` → 拒，理由 `prereg closed (已判决)`；叙述里提到「曾撤回」而
  状态为 FROZEN 的照旧放行（历史不是状态）。无状态行时按整头扫。
- `Tools/heartbeat_write.py`：新增 `_nested_is_gpu` / `_owned_nested`，
  一级嵌套 GPU 块由**同一次探针**重述（free/used/total 族 + util），探针失败
  则连同扁平键一起丢弃并留 warning。

## 可证伪

- `Tools/fill_ladder.py selftest`：新增四条腿（已判决拒 / RETRACTED 拒 /
  FROZEN+叙述含撤回仍过 / 真实 W3 prereg 以「关单」为理由被拒）；现场跑一次，
  阻断行字面从「缺字段」变成「已关单」。
- `Tools/heartbeat_write.py selftest` 12→**14/14**：L13 嵌套块必须被探针重述
  （且未知子键 vendor 保留）、L14 探针失败必须丢掉调用方块并保留旧面。

## 未做（写明）

供给地板仍然是 0<3。本轮的产出不是「补上供给」，而是**让下一次补供给不会补错**：
catalog 23 条已全部被消费，唯一未入池的那条是已关单家族。真正的补货要写新的
冻结预注册 + 新 runner（W21 及以后），那是另一轮的量，不能靠改 schema 假装。