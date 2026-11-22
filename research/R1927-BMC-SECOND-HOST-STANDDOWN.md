# r1927 窗口｜bm-c 第二宿主退避记录（只读轮）

生成：2026-11-22T11:44+08:00 ｜ 机器：bm-c ｜ state round_no 保持 **1926**（不递增，见下）

## 结论（一句话）

本仓同一时刻已有另一个执行体在跑（另一个 `codely.exe` 交互会话，pid 44248，起于 11:02:50），
故本宿主本轮**只做只读核对与新增文件面**，不跑 S6 链、不改共享面、不递增轮号、不写心跳、不追加轮账本行。

## 证据

- `results/_repo_write_contention.bm-c.json`：`verdict=CONTENTION`（rc3），2 宿主并存在盘；
  我=pid 38148（起 11:40:03，非豁免），对端=pid 44248（interactive，起 11:02:50，cap_exempt）；
  对端独占写 **20** 个共享面（含 `Tools/repo_write_contention.py`、`docs/live_usage/*`、`docs/data_lanes/FRESHNESS.md`、`fleet/machine-health.json`）。
- 探针本身即 r1927 sidecar，基线提交 `9aa4736258`（11:36:37）。
- 本机 `ahead/behind origin = 0/0`。

## 未提交面清单（归对端在飞轮所有，勿"恢复"、勿重放）

轮首 `git status --porcelain` = **30 件全为 `M`、0 件未跟踪**：
docs 5 / fleet 2 / research 2 / results 20 / source 1（`Tools/repo_write_contention.py`）。

含义：这些是对端本轮（r1927）已写盘、尚未提交的派生面与一件工具面。
第二轮/第三轮执行体若按"陈旧面"整文件重放，就会把对端的推进 revert（r1783 / r1907 同族）。
本宿主一件未碰（唯一触碰=`results/_repo_write_contention.bm-c.json`，由协议规定探针自己覆写）。

## 只读核对（本轮已完成，全部零动作）

| 项 | 读数 | 判定 |
|---|---|---|
| 孤儿面 `Tools/orphan_face_probe.py` | py_faces 3 / orphans 0 / resident_servers 0（11:40:56） | 绿；另见两个 ComfyUI 服务（8188/8189）空闲，非本车道 |
| 集团 `docs/decisions.md` 水位 | 原字节 sha256 `79e3083b…`（cat-file 直取）与 state `last_decisions_sha` 逐位相等 | 零新决策行 |
| 集团 `docs/orders.md` 水位 | `aad2632e…` 与 state `last_orders_sha` 逐位相等 | 零新令 |
| `results/orders_ack_scan.bm-c.json` | unacked **0** / ack 327 / face_divergence 空 | 无未回执令 |
| `results/watermark_red.json` | red=false，next_pick=moneyflow IC reference batch（status=claimed） | 无可领活 |
| state `chain_verdict` | "in flight (about 90/317 legs at close, rc 0 on every printed leg)" | 链在飞 |

## 故意未做（及理由）

1. **S6 链**：对端驱动已在跑 317 腿（约 90 腿处）。第二个驱动=同面双写（r1907）。
2. **冒烟全量套件**：链正在重写面，比对必然读到半写的面→假红（r1861「面在动」族）。故本轮无套件结论，不宣称绿也不宣称红。
3. **state round_no++ / 心跳 / 轮账本追加**：state 与心跳是对端本轮的面（心跳 11:38:21 刚写）；同机双宿主递增会跳号，轮账本追加会与对端 read-modify-write 抢写。轮号递增权与收口权留在对端 r1927。
4. **任何共享面改写**：按竞争律只落新增文件面。

## 附带取证（只读）：两条「链判定」面都是错的

本窗口顺手核对链进度日志，得到一条比退避更重要的事实（取证面 = 本地 `results/_r1927_bmc_chain_forensics.json`；`results/_*` 被 gitignore 属约定，故关键读数全文引在下面，他机无需该文件）：

- **链其实已经跑完**：`results/_s6chain_progress.bm-c.jsonl` 末三行 = `leg_done i=339/341`、`i=340/341`、`i=341/341`，随后 `chain_done round=1923 n_legs=341 nonzero=[]`，收于 **2026-11-22T10:37:14**。
- 但 fleet 读的两张面都还在说反话：
  - `state-bm-c.json` 的 `chain_verdict`（10:46:09 写，round 1926）=「in flight (about 90/317 legs at close, rc 0 on every printed leg)」——既说"在飞"，腿数 317 也与 341 不符。
  - `fleet/machines/bm-c.json` 的 `chain_note`（ts 10:46:22，落盘于 HEAD）=「the r1923 driver (pid 35980) is still alive and wedged inside regime_thermo_build since 09:54」——而该驱动 **10:37:14 已经正常收工**，`pid 35980` 现已不存在。
  - 同机轮号漂移（HEAD 内即如此）：state `round_no=1926` vs 心跳 `round_no=1923`。
- 代价：下一轮若照这两张面办事，会得出「链没跑完/驱动还卡着」，于是重烧 341 腿（实测本轮整链 ~2h 量级）；而实际该做的是**把已绿产物发布出去**。
- 顺带量出遗留：29 件未提交派生面里，**9 件在链收工前写定**（10:14–10:31，属链产物）、**20 件在链收工后写**（10:44–11:40，属对端本轮工作 + 调度器面）。

故下轮（单宿主时）的正确顺序：**先发布 9 件已定链产物 → 修正两张链判定面 → 再考虑是否需要重跑链**，而不是反过来。

## 下轮指针

对端 r1927 收口后（链已确认 341/341 rc0、套件重跑一次）再恢复常规轮：单宿主前提下补跑套件、修正 `chain_verdict`/`chain_note` 两处误述、逐件判定并发布遗留派生面。
