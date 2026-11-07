# DIGEST-20261108-r1554 — E525: what happens to the values the second reader still forwards?

**轮次**：r1554 bm-b ｜ **日期**：2026-11-08 ｜ **卡**：E525 ｜ **正身**：`scripts/e525_onward_residue.py`

## 一句话

E524 用两个名字结案了第二跳的残差；本轮把两个都打开：**23/23「离开树」是 `sys.exit(main())` 进程退出码（不是库边界）**，6 个「仍转发」全部停在容器/不跟形式（未测量），另外去重后 6 个第二跳 parcel 是自递归——链在同一函数体内闭合，却被 E524 记成了 unresolved。

## 上游

`results/state_tilt/readeronward_latest.json`（E524，r1551）：
- 23 处 `the_value_left_the_corpus_at_the_second_hop`
- 6 处 `the_second_reader_hands_it_on_again_so_the_chain_is_still_unmeasured`

## 方法

对每个残差站点，取 E524 发布的第二跳 parcel（同一次 hop 计算），回到 parcel 的 `source:line`，只读该行 AST：
- 行的调用名命中 `sys.exit` / `SystemExit` / `exit` / `quit` / `os._exit` → 进程退出
- parcel verdict 是 `stored` / `form_not_followed` → 容器或不跟形式
- callee 等于所在函数且同模块 → 自递归
- callee_module 是 `.py` → 本仓另一个具名函数
- 其余外部名 → 外部库或不解析

两类上游残差**始终分开计数**；parcel 统计按 `(source, line, callee)` 去重。

## 读数

| 项 | 值 |
|---|---|
| 残差站点 | 29（left-tree 23 + still-forwarded 6）|
| 进程退出边界 | 23（全部 left-tree）|
| 外部库 / 本仓具名 / 不解析 | 0 / 0 / 0 |
| 容器或不跟形式（未测量） | 6（全部 still-forwarded）|
| 去重第二跳 parcel | 56 行桶 → 独立 parcel 若干；其中自递归 6 |
| 共享 parcel（多行同一跳点） | 有，已发布 `rows_that_share_this_parcel` |

**判决**：`every_value_E524_said_left_the_corpus_at_the_second_hop_is_the_process_exit_status_and_not_a_library_boundary`

## 三枚可复用判例

1. **类名不是测量**——`argument_to_a_callee_outside_the_corpus` 的实际 callee 是 corpus 内的 `main`，真正的接收者是 `sys.exit`。凡「离开/外部/未知」类必须回到接收那一行重新命名。
2. **一个物理跳点会被多行共享**——按行累加会把 1 个 parcel 数成 5 个；parcel 统计必须去重并发布共享计数。
3. **check 只需解析被引用的 29 个文件**（0.86s），前提是边界从源码行重推，而不是重跑上游全树。

## 验证

- `build` rc0 / `check` problems=0 / `verify` problems=0 / `selftest` clean
- S6 腿 `onward_residue` rc0（0.86s）
- smoke 腿 `# E525` 1/1 绿；`--doctor` 1/1 红，面字节还原 sha `b307c8ff0dfe`
- face：`results/state_tilt/ONWARDRESIDUE-2026-11-08.json` + `onwardresidue_latest.json`