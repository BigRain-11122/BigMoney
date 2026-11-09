# DIGEST-20261110-r1647-e629-caller-write

窗口：r1647 bm-b（2026-11-10 00:0x-00:5x）· 卡片：knowledge/METHODOLOGY_ASSETS.md E629
产物：scripts/e629_caller_write.py（selftest 28/28）+ results/state_tilt/CALLERWRITE.json
      + callerwrite_latest.json + scripts/run_e629_smoke_leg.py（1/1 PASS / --doctor 1/1 红 / 面字节还原）
      + smoke_test.py leg E629 + Tools/s6_chain_bmb.py leg `caller_write`

## 一句话

E628 把写入臂限定在"模块内、函数外、按名字拼写"的地方，两条接收者是参数的重复行因此一处写都没找到；
这张把那一跳往上游走了一层——**9 个调用点里没有任何调用方在参数对象上写那把键**，而 6 个调用点把
对象又交给了调用方自己的另一个函数（写可能在那里，本跳看不到），所以调用方臂 **关闭 0 条**：
1 条留开、1 条本跳不可追踪。

## 读数表

| 项 | 值 |
| --- | --- |
| 母体（E628 面中出生点早于区间的重复行） | 2 |
| 模块解析失败 | 0 |
| 参数经核实 | 2 |
| 至少有 1 个调用点的行 | 2 |
| 调用点总数 | 9 |
| 以名字传参的调用点 | 7 |
| 调用前写该键的调用点 | **0** |
| 只在调用后写的调用点 | 0 |
| 把参数再交给别的调用 | 6 |
| 参数不可追踪（非名字表达式） | 2 |
| 行级：全调用点都不写 | 1（cn_mkneutral_p1.simulate） |
| 行级：调用点不可追踪 | 1（ew6_portfolio.write_outputs） |
| **调用方臂关闭的重复行** | **0** |
| 判决 | `none_of_the_2_outside_origin_rows_has_a_caller_that_writes_the_key_and_1_of_them_cannot_be_traced_at_this_hop_so_the_caller_arm_closes_none_of_them` |

## 行明细

- `scripts/cn_mkneutral_p1.py:507`（`simulate` 参数 `P`，键 `slip_exec`）：6 个调用点（null_draw /
  run_sobol / cmd_run / cmd_selftest ×3）都以 `P` 传参，且调用前又把 `P` 交给别的函数 → 本跳不可判定。
- `scripts/ew6_portfolio.py:393`（`write_outputs` 参数 `ports`，键 `x1`）：3 个调用点，两处传字面量
  `None`（参数走默认/空值），一处传 `ports` 且调用方无该键写入 → 留开。

## 四条教训

1. **"找到了写者"不等于"关闭了重复读"**——调用方的写在进入被调函数之前就发生了，死行和它的兄弟读
   看到的是同一个（写后的）值。所以这张把 `rows_closed_by_the_caller_arm` 冻结成 0 并由闸重算，
   避免下一轮有人把"找到一个写站点"读成"这条重复读解决了"。
2. **一跳就是一跳**：`P` 被再交给别的调用（6 处），写可能在那里面；本跳只能报"不可判定"，不能报
   "没有写"。残差必须与"确认没有写"分成两个类目（这是下一张卡的母体）。
3. **字面量 `None` 与"没有传参"是两件事**：`write_outputs(..., None, ...)` 把参数绑到 `None`，
   不是默认值路径；把两者混成一个 missing 会把一个真实调用点读数抹掉。
4. **人口从上游发布面机读、不当场重算**：母体是 E628 面里 `origin_before_the_e627_interval_start`
   为 true 的重复行，本张不再重新判定"哪些是重复"，只在那一层上加一跳。

## 交叉核验

- `e628_cross_check`：读 E628 已发布面 2 行，`e628_verdict` 随件发布；0 模块解析失败。
- selftest 28/28（含：写在前 / 写在后 / 不写 / 非名字 / 无调用点 / 缺参数 六类夹具，
  以及"把某处调用点加上调用前写"必须令 `face_problems` 非空）。
- `run_e629_smoke_leg.py`：1/1 PASS；`--doctor` 1/1 红；面 sha 前后恒等。