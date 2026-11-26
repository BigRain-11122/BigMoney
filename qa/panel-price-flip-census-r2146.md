# QA — 全数据面价格翻转普查 r2146

- 件：`scripts/panel_price_flip_census.py` / `results/panel_price_flip_census.json` / `research/PANEL-PRICE-FLIP-CENSUS.md`
- 时间：2026-11-26T19:2x+08:00
- 性质：纯新增文件面（同宿主竞争 rc=3，未改共享代码/数据、未跑 S6 链）

## 一、验证记录

| 项 | 命令 | 结果 |
|---|---|---|
| 自检 | `python scripts\panel_price_flip_census.py selftest` | **PASS (25/25)**, rc=0 |
| 全量跑 | `python scripts\panel_price_flip_census.py run` | rc=0，耗时 82s，7 面板 / 8,043 文件 / 1,939 万 bar |
| 一致性 | `python scripts\panel_price_flip_census.py check` | **OK verdict=FLIP_CONFIRMED panels=7**, rc=0 |
| 判词 | verdict.code | `FLIP_CONFIRMED`（价格面既有无解释跳变、又有被证实的翻转） |

## 二、自检覆盖的十一条行为（selftest 内）

1. 干净斜坡：0 跳、0 翻转
2. 单向大跳：计 35% 档、不记翻转
3. -50% → +100%：记 1 个翻转对、35%/50% 各 2 格
4. 窗口外缓慢回升：不算翻转
5. NaN / 空 / 非数字 / 非正值行被丢弃
6. 乱序输入先按日期排序再判翻转
7. 利率面板（kind=rate）不进入污染判词
8. 有翻转的面板判 `FLIP_CONFIRMED`
9. 只有跳变无翻转判 `PRICE_JUMPS_UNEXPLAINED`
10. 走回（60 根内反向 ≥70%）也判 `FLIP_CONFIRMED`
11. 分档为累计口径：-90% 的 bar 在 35/50/80 三档各计 1

## 三、本轮自捕（已修，留判例）

1. **`n < 3` 的保护把两根 bar 的序列整段跳过**——自检「-90% 单跳」腿当场红（`deep.35 got 0 want 1`）。两个点就能算一个收益，门槛应为 `n < 2`。这是「自检要覆盖边界形态」价值的直接证据。
2. **分档计数写了 `break`，50%/80% 档永远为 0**——`flip.50 got 0 want 1`。改为累计口径（80% 是 50% 的子集、50% 是 35% 的子集），读者一眼能看出分布厚度；同时把「互斥」断言改成「累计」断言。
3. **selftest 计数写死 `(11/11)`**——加了 3 条腿后仍印 11/11，等于自检在撒谎。改为动态计数（本轮终值 25/25）。
4. **`_panel_files` 只扫一层目录，A 股面板整块漏扫**——`files=0`。改 `os.walk` 递归后 5,221 文件 / 1,684 万 bar 才进来，这直接决定了「A 股个股面当代窗只有 46 格」这条读数是否存在。

## 四、未覆盖（与 research 件 §七 一致）

- 逐格成因未核（只判「不可能是正常价格」）
- 消费脚本数为源码字面匹配上界
- 不重算任何收益、不改判词
- `_panel_cache_v1.parquet` 未扫描
