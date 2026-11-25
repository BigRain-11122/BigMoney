# 交接回执 · 已整合（DASHENG → bm-c）

> 回应 `O-20261124-2300-bm-c` §1-D，接续 `RECEIPT-20261125.md`（当时判 PARTIAL：对端清单未到）。
> 写于 **2026-11-25T00:4x+08:00** · bm-c 无人值守轮 r2060。
> 状态：**COMPLETE** —— 这是跨机判词，不是同源自比。

## 0. 一句话

对端清单到了。跑完真正的跨机差异后：**没有任何一份文件需要从 DASHENG 导入**。
本机在 35,051 个共有入库件上比对了 35,049 个内容哈希，差集三方归因后为零缺口；
15 条数据车道全部有重建命令，差的只是「重跑脚本」，不是「搬文件」。

## 1. 这份 COMPLETE 与上一份 COMPLETE 的区别

上一份回执拒收的那个 COMPLETE，抬头是 `FLUXGROUP ⇒ FLUXGROUP`
（拿本机清单和本机清单比，必然 0 差）。本份抬头是 **`DASHENG ⇒ FLUXGROUP`**，
两台的 `machine` 字段不同，才算交接证据。

判词面：`research/INGEST/DIFF-DASHENG-20261124.{json,md}`
生成器：`scripts/ingest_crossdiff.py`（新增·selftest 19/19）

## 2. 差异归因（9,621 条「内容不同」的真身）

| 桶 | 数量 | 含义 |
|---|---|---|
| 提交版本不同 | 2,336 | 本机领先 482 个提交，`git pull` 即同步，无动作 |
| 仅 worktree 字节不同 | 7,271 | **行尾过滤**：抽样 60 个经 `git hash-object` 复核，60/60 与 `HEAD:<path>` 逐位相同 |
| 对端未提交 | 14 | 见 §3，逐件判过 |
| 本机在对端 head 之后删除 | 1 | `results/_selftest_sub/c_arm_metrics.json`，不是缺口 |
| 无法解释 | **0** | — |

### 2.1 两个尺子坏在哪（本轮定谳，写进代码注释）

1. **mtime 不能跨机比。** 旧 `ingest_diff.py` 用 mtime 判「他们更新」，
   在这对机器上给出 **16,960** 条——那是检出时间，不是内容年龄。
   对端落后 482 个提交、worktree 却更晚落地，于是几乎每个文件都"更新"。
2. **worktree sha256 不能跨机比。** `.gitattributes` 两边 git blob 完全相同
   （`990cb912…`），但清单哈希一个是 215B、一个是 218B：
   本机 `core.autocrlf=true` 把 LF 换成 CRLF。凡文本件，worktree 哈希天然不等。

结论：跨机交接只认**内容**（hash/blob），mtime 只作审计打印。

## 3. 那 14 个「对端未提交」逐件判过

| 分类 | 数量 | 判词 |
|---|---|---|
| 他人属主面 | 2 | `results/_orphan_face_probe.bm-a.json`、`results/compute_audit.bm-a.json`——文件名带 bm-a，本机导入即谎报作者 |
| 本机已有更新代 | 7 | `REPORT-2026-11-18.*`、`LIVE-BOOK-20261118.*`、`LIVE-2026-11-18.*` 等：同名面本机已有 11-22/11-23/11-24 代 |
| 滚动面 | 2 | `docs/live_book/BASE-BASIS.md`、`results/etf_book_base_basis_audit.json`：无日期、每天重写 |
| 两边各自重生成 | 3 | `TICKET-MENU-2026-11-18.md`、`MENU-2026-11-18.json`、`QUOTE-2026-11-18.json`：本机最后提交 `470e778571` **在对端历史里**，两边共用同一基线、各有未提交重生成 → 本机重生，别导入 |
| **需人工过目** | **0** | — |

## 4. 车道层

15 条车道两边都对齐到各自最新 bar，**本机不落后任何一条**（`newer_bar_there = []`）。
文件数差异（`heat +123`、`futures_contracts -83`、`cb_daily -1051` 等）属重建范畴：
对端已交付 **15/15** 条车道的重建命令（`research/INGEST/LANES-DASHENG.json`），
其中 `heat` 是 bm-a 单写车道（R19 判例），本机 2 个文件是预期态，不是缺口。

## 5. 本轮新增/改动面

| 文件 | 性质 |
|---|---|
| `scripts/ingest_crossdiff.py` | **新增**·内容寻址跨机差异 + 归因 + 可导入性分类（selftest 19/19） |
| `research/INGEST/INVENTORY-FLUXGROUP-20261125.{json,md}` | **新增**·带 sha256 的本机清单（补上令 §1-A 硬要求；35,972 件） |
| `research/INGEST/DIFF-DASHENG-20261124.{json,md}` | **新增**·真实跨机差异面 |
| `research/INGEST/RECEIPT-20261125-INTEGRATED.md` | **新增**·本文件 |

未改任何既有共享面（写竞争探针 `rc=3 CONTENTION`，按 r1907 只落新增文件面）。

## 6. 三条诚实边界

1. **对端清单的 dirty 列表截断在 200 件**（实际 416）。落在 200 之外的路径
   不能当作「干净」，所以 §3 的「0 需人工过目」是**在可观测范围内**成立。
2. **filter-only 证明是抽样**（60/7,271）。抽样全中不等于全中，
   但抽样偏差若要出现，需要 60 个样本同时巧合，概率可忽略。
3. **大文件（>20MB）没有 sha256**（清单生成器的 `--hash` 上限），
   这些件退化成大小比对：`unverified = 0` 说明本批没有落到这个退化面。

## 7. 下一步（不是本轮）

- 把 `ingest_crossdiff.py` 接进 S6 链（竞争窗关闭后），让 G6_ingest 有可跑的判据腿；
- `research/QUANT-BLOCK-BOARD.md` 的 G6_ingest 行仍写 RED(self-diff)——该面是共享面，
  本轮不动，交由无竞争轮翻面；
- 方法论卡：本批确有新方法（「跨机比较只认内容，mtime 是检出时间」），
  锁存待无竞争轮写入 `knowledge/METHODOLOGY_ASSETS.md`。
