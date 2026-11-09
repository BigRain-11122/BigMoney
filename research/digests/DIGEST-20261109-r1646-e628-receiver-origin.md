# DIGEST-20261109-r1646-e628-receiver-origin

窗口：r1646 bm-b（2026-11-09 23:2x-23:5x）
卡片：knowledge/METHODOLOGY_ASSETS.md E628
产物：scripts/e628_receiver_origin.py（selftest 27/27）+ results/state_tilt/RECEIVERORIGIN.json
      + receiverorigin_latest.json + scripts/run_e628_smoke_leg.py（1/1 PASS / --doctor 1/1 红 / 面字节还原）
      + smoke_test.py leg E628 + Tools/s6_chain_bmb.py leg `receiver_origin`

## 一句话

E625-E627 都在持死行那个函数的体内工作；这张把"接收者从函数外面来"这条边界定价——34 条活死行里
参数 10 / 体内绑定 21 / 外面来的容器 1 / 体内容器 2，4 条重复读里 **2 条的对象出生点早于区间**，
但这两个名字在本模块内**没有被任何别的站点在同一把键上写过**，所以 4 survive / 0 stored / 0 undecided 维持。

## 读数表

| 项 | 值 |
| --- | --- |
| 可解析模块 | 1,099（14 个 py2 残留 SyntaxError 如实跳过） |
| 活死面键行 | 34 |
| 同对象重复行 | 4 |
| 参数 / 体内绑定 / 外面容器 / 体内容器 | 10 / 21 / 1 / 2 |
| 模块级 / import 别名 / 解析不到 | 0 / 0 / 0 |
| 重复行中出生点早于区间 | **2**（cn_mkneutral_p1:507 `P`、ew6_portfolio:393 `ports`） |
| 其中被别处同键写过 | **0** |
| 36 行层面被别处写过 | 0 |
| 判决 | `2_of_the_4_duplicate_receivers_arrive_from_outside_the_interval_but_no_other_site_in_the_module_writes_that_name_at_that_key` |

## 属主行明细（4 条重复读）

- `cn_core_ddctl_p1.py:367` key `days`，`P` 体内绑定（由 `build_dd_axis` 造）→ 出生点在区间内
- `cn_mkneutral_p1.py:507` key `slip_exec`，`P` 是参数 → 出生点在区间外
- `e590_cash_silence.py:364` key `bar`，`r` 体内绑定（循环目标）→ 出生点在区间内
- `ew6_portfolio.py:393` key `x1`，`ports` 是参数 → 出生点在区间外

## 三条教训

1. **"区间覆盖出生点"要单列三值字段**（true/false/null），别让读者从来源类目自己推；null 必须存在，
   否则"解析不到"会被读成"体内绑定"（false）。
2. **模块级名字与 import 别名分成两类**：前者本模块可改名、后者是别人的对象——本母体两者皆 0，
   但合并会丢掉这条区分。
3. **写入臂只在出生点早于区间时跑**，否则把区间内已扫过的写再数一遍；并且**只到名字级**——
   同名不同对象（E206/E207 族）随时可能让计数骗人，所以发布站点清单而不只是一个数。
4. 性能：14k 行的 `perpetual_faces_n1.py` 会让"每行重扫每函数"变成分钟级；按模块缓存函数 scope
   与模块绑定表后，构建 >7min → 约 4min（E442 族）。

## 交叉核验

- E627 面逐行重解析：34 行、重复类差 0，已出版 split 4/0/0 随件
- S6 leg `receiver_origin`：rc=0 0.06s problems=[]
- 独立 smoke 腿：1/1 PASS；`--doctor` 翻 verdict 后 1/1 红，面 sha 前后相同