# DIGEST 2026-11-08 r1549 bm-b — E522: 静默默认只有被真正读到才算活着

出处：`scripts/e522_silent_arm_caller.py` → `results/state_tilt/SILENTARMREAD-2026-11-08.json`
（`silentarmread_latest.json` 同源）；上游=`results/state_tilt/LITERALGUARD-2026-11-08.json`（sha256 钉死）。

## 一句话

E518 的 402 条"静默不可分辨"字面量臂里，**只有 12 条真的被生产调用者无卫读取且任何形状测试都分不出**；
另外 37 条被无卫读取但形状本可分辨，136 条每个生产站点都测过，**206 条只是被转发给别处的读者**，
2 条结果始终被丢，9 条没有任何调用者。

## 站点面（640 个生产站点）

| 结果去哪了 | 站点 |
|---|---|
| 有终止型卫语句点名结果 / 结果本身就是测试操作数 | 206 |
| 绑定后无卫直接被读（下标/属性/方法） | 63 |
| 被解包（只查元数） | 15 |
| 继续往下传（本面不跟第二跳） | 351 |
| 当语句丢掉或绑定后从此不读 | 83 |

## 三枚可复用

1. **"被传下去"不是"被读"**。`return f()` / `g(f())` 是把结果交给下一个栈帧的读者；把它们算成"从不被读"
   会让 277 条臂被误记成休眠（首版实况），按 binding 分类后只剩 2 条真丢弃、206 条是转发。
2. **就地读没有名字**。`f()[0]` / `f().items()` 没有可查绑定名，首版 `first_reads` 找不到就发布
   `never_read_again`——把"就地读了"印成"没读"。正法＝问父节点要读法，并把闸写成「无卫读必须带读法」。
3. **解包只证明元数**。`a, b = f()` 解包成功不代表元素不是 None；给它单独的读法，
   否则它会混进"绑定后不读"那一桶。

## 头牌例子（24 条不可分辨且被无卫读取中的一部分）

- `engine/futures_runner.yearly_returns`（`return 'out'`）→ `scripts/cn_mkneutral_p1.py:675`：
  `yr.items()` 直接当字典用，`'out'` 是字符串，`.items` 会炸在运行时。
- `scripts/e471_dead_copy._subject`（`return ''`）→ 同文件 220 `if subj:` 真值测试——空串被静默跳过。
- `scripts/im_ic_pair._resume`（`return 'done'`）→ 858 `r.keys()`：把哨兵当 dict。
- `scripts/grid_p1_screen.load_rows`（`return 'rows'`）→ 573 `rows[f'grid|...']`：把哨兵当 dict 下标。

## 未做（不宣称）

- 351 个"转发"站点没有跟第二跳；"136 条每站点都测过"只覆盖**本站点**。
- 全量 smoke 套件、其余 S6 链腿、采集器族、行情/纸盘链均未跑。

## 指针

- 卡：`knowledge/METHODOLOGY_ASSETS.md` E522
- 链腿：`Tools/s6_chain_bmb.py::silent_arm_read`
- smoke：`smoke_test.py::# E522`
- 池：E522 done → 后继卡 E523（转发出去的结果谁在读）