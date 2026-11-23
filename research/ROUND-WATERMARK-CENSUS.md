# 这台机器现在是第几轮？四个载体给四个答案

读数窗口 2026-11-23T09:1x（bm-c·`scripts/round_watermark_census.py run`）。

| 载体 | 它说的轮号 | 它自己的钟 |
|---|---|---|
| `git log`（最近的 `round N` 提交） | **1976** | 09:07 |
| `state-bm-c.json` | 1946 / 1952 / **1962**（一个文件三个数） | 02:1x（374 分钟前），文件 mtime 06:5x |
| `fleet/machines/bm-c.json`（心跳） | 1946 / 1951 / 1953 / **1960**（一个文件四个数） | 02:1x（373 分钟前），**文件 mtime 09:09** |
| `fleet/state-bm-c.json` | 1542 / **1555** | 2026-11-11（11.7 天前） |
| `fleet/round_reports-bm-c.md` 行尾 | r1929 | 2026-11-22 13:4x |

判词：`FACES_DISAGREE_WITH_GIT_AND_EACH_OTHER`，最大滞后 421 轮。

## 危险的不是「旧」，是「刚被重画过、里面的钟是旧的」

心跳在 **09:09** 被重写过（对端会话正在跑这一轮），而它自己记的 `last_seen` 是
**03:00**、`last_round_ts` 是 **11-20 01:56**。于是同一张文件：

- 看 mtime 判活性的 watchdog → 看到一台刚活过的机器；
- 看文件自带钟判停滞的连续性哨兵 → 看到一条停了六小时的循环。

两者读的是同一个路径，得到的结论相反，而**谁都没有错**——错在这张面本身不回答
「我现在是活的，我说的是哪一刻的活」。这是 r1861「面在动 ≠ 面算错」的另一半：
面在动，但动的只是外壳。

## 机制（不是手滑，是结构）

`Tools/heartbeat_write.py` 是 **merge-only** 的：它只校验类型，不删除、不推进任何
键。轮号在仓库里同时被写成 `round` / `round_no` / `rounds` / `last_round` 四种拼法，
不同写者各写各的 —— 一旦某个写者不再更新自己那一支，旧值就被永久保留，
于是「一个文件四个轮号，没有一个是最新的」是 merge-only + 多名拼法的必然产物，
不是某次疏忽。

## 为什么值得单独量（而不是等它自己好）

r1219 的规则是「两面不一致就 absorb」，r1308 的 `scripts/round_open_absorb.py` 分的是
**文件类别**（源码侧 vs 可再生面）。两者都不覆盖这一种：当**计数器本身**是陈旧的那一面时，
「不一致」不会报警——因为没有任何一面声称自己权威。

## 现在能用的两件

```bash
python scripts/round_watermark_census.py run      # 落 results/round_watermark_census.json
python scripts/round_watermark_census.py --selftest   # 9/9，含四条必红腿
```

自检里刻意钉死的四条边界：缺面报 `FACE_MISSING` 而不是「0 轮」；坏 JSON 报
`FACE_UNREADABLE` 而不是给判词；git 读不到时**不判任何面**（不是全绿）；mtime 新而自带钟旧
才叫 `REDRAWN_WITH_A_FROZEN_CLOCK`，**mtime 旧且钟旧只是 stale**（这两种必须分开，
否则每一条正常停摆的车道都会被误报成「被重画」）。

## 下一步（需要动共享面，故本轮不在 CONTENTION 窗内做）

1. 心跳写者统一轮号拼法（只留一种），并在每次 apply 时由写者**自己**推进 `last_seen`，
   不接受调用方传入的旧值；
2. `state-bm-c.json` 的三个轮号收敛成一个，其余降级为历史注记；
3. 把这条普查接进链腿（先 writer 后 reader），并在 CEO 页/战报的「当前活」行引用它——
   让读者看到的是「这台机器自己说它是第几轮」而不是某个派生面的假定。
