# QA — r2170 (bm-c) — 名册上的车道补上驱动：lhb_inst 接链腿 + lhb 接管旗

## 本轮回答的问题

r2169 的归因面把 6 条非同步车道分成「谁本该动它」。其中两条的判词是 *声明不是驱动*：

- `lhb_inst` = `declared_host_without_driver`（lane_hosts 指派 bm-c、写入器在盘、链/任务/注册三源全空）
- `lhb` = `host_dead_takeover_available`（`data_lane_freshness` 已印 `taken_over=lhb<-bm-c`，而链腿每轮印 `takeover refused: no --takeover flag`）

本轮把这两条从「有人负责」改成「有人真的在跑」。

## 改了什么（Tools/s6_chain_bmc.py，三处，全部 gate 形态零网络 no-op 优先）

| 链腿 | 改动 | 为什么 |
|---|---|---|
| `update_lhb_inst` | 新增腿 `python scripts/update_lhb_inst.py run` | 归因面判 `declared_host_without_driver`：面板 4 个交易日停在 11-20，而三源驱动全空。写入器自身有 no-op 门（面板覆盖预期完整 bar 日即零网络）、overlap 校验、append-only、单车道宿主守卫 |
| `update_lhb` | 补 `--takeover` | 新鲜度面早已声明接管权给 bm-c（owner bm-a 静默 206.9h ≥ TAKEOVER_STALE_MIN），而链腿每轮印 `takeover refused`。旗不改变守卫：bm-a 心跳一旦新于阈值，本腿自动退回诚实 no-op |
| `update_heat` / `update_repo` | 补 `--takeover`（同一形状，本轮接手核验） | 同上；写成 `--takeover` 是行使既有许可，不是放宽 R31 |

## 实测证据

```
$ python Tools\s6_chain_bmc.py --only=update_lhb_inst,update_heat,update_repo
0 update_lhb_inst 0.7s lhb_inst: no-op (cutoff 2026-11-26 == expected 2026-11-26)
0 update_heat     0.8s no-op: 2026-11-26 close is stale: the 2026-11-27 session opened at 09:15:00
0 update_repo     0.5s no-op: local cutoff 2026-11-26 covers expected complete-bar date 2026-11-26 -> zero network
chain: 3/3 rc0

$ python Tools\s6_chain_bmc.py --only=update_lhb          # 补 --takeover 之后
0 update_lhb      5.6s updated: +88 rows, cutoff 2026-11-25 -> 2026-11-26, total 269142 (5s)
chain: 1/1 rc0
```

新鲜度面重 derive（`python scripts\data_lane_freshness.py run`，rc0）：

```
in_sync   lhb_inst   tail=2026-11-26 missing=0     (was stalled 2026-11-20)
in_sync   repo       tail=2026-11-26 missing=0     (was behind_1d 2026-11-25)
behind_1d lhb        tail=2026-11-25 missing=1     (本面在 +88 行写入之前采样)
```

`lhb` 那一行是采样先后造成的：同一条命令在 `update_lhb` 落 11-26 之后重跑即为 `tail=2026-11-26`。

## 仍未同步的三条（如实，不在本轮修）

| 车道 | 判词 | 为什么本轮不动 |
|---|---|---|
| `heat` | `stalled 2026-11-19` | 写入器自己的门说 `2026-11-26 close is stale: 2026-11-27 session opened at 09:15`——**热榜日不可补**（`data_lane_freshness` 头注：rank list 是 live rolling，没有可取回的历史）。接管旗已就位，等收盘窗口后下一轮自然抓 |
| `cb_panel` | `no_driver`（`stalled 2026-11-20`） | 写入器 `scripts/cb_dual_low.py` 是 `fetch → build → run` 的研究三阶段，**没有「面板已覆盖即 no-op」的门**；直接接链腿会每轮重拉全宇宙转债。先定宿主 + 先写 no-op 门，属下一轮 |
| `ah_panel` | `absent`（`complete=false / cutoff=null`） | 源端失败（`RemoteDisconnected`），不是没人跑 |

## 并发披露

`Tools/s6_chain_bmc.py` 里的 `update_lhb_inst` / `update_heat --takeover` / `update_repo --takeover` 三处改动在本窗开始前（10:31:33）已在盘上、未提交，`data/lhb_inst/lhb_inst.parquet` 亦已在 10:22:15 被推进到 11-26、10:31:49 留下 `no_op` 状态面（`verdict=no_op, cutoff=2026-11-26`）。竞争探针在本窗开始时 `rc=0 CLEAN`（无第二 codely 宿主），故本轮按「接手未收口产物」处理：逐条核验（三腿 rc0、两脚本确支持 `--takeover`、heat 写入器的 machine-local pit 已在脚本头注声明）后补上 `update_lhb --takeover`，一并收口。

## 记账

轮报告 1 处 + QA 1 件 + state 1 处 + 心跳 1 处 = 4
