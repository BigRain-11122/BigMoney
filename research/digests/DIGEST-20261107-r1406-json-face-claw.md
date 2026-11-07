# DIGEST r1406 bm-c · 一个没人看得见的缺陷类：提交面里的逗号与重复键

**触发**：r1404 的前向账本 `results/etf_book_forward/LEDGER.json` 以两个缺陷被提交（2026-11-07）——
`drift.settled_bars` 两个元素之间漏逗号，`drift` 块里 `faces`/`max_abs` 各出现两次。
当天没有任何闸报警：pre-commit 爪只找冲突标记，`git diff --cached --check` 也只找标记，而这两处一个标记都没有。

**为什么第二个缺陷更贵**：`json.loads` 接受重复键并静默保留**最后**一个。即使把逗号修好，文件也会把
旧测量值当成当前值发布——读者拿到的不是「打不开」，而是「打开了一个错的数」。这比崩溃更难发现。

## 本轮落地

1. `Tools/json_face_guard.py` 增加 `--staged`：枚举 `git diff --cached --diff-filter=ACMR` 的 `<path>.json`，
   用 `git show :<path>` 读**索引 blob**（不是它旁边的 worktree 副本），走同一个 `judge_bytes()`。
   干净时一行不出；有发现时点名文件与键。
2. `Tools/git-hooks/pre-commit` 增加 r1406 腿：每次提交调用上面的 `--staged`，发现即 exit 1（附 `--no-verify` 逃生口）。
3. `smoke_test.py` 两条腿：全量已发布 JSON 面必须解析且无重复键；爪自身的 18 条腿必须通过。

## 验证（实弹，非宣称）

- 守卫 selftest **18/18**（新增 5 腿：暂存合法面干净 / 暂存重复键拦下 / 被拦文件点名 / **工作区修好但索引仍坏仍拦** / 删除与非 JSON 不计）。
- 全量扫描 `results/**.json`：**9,782 面解析、0 发现**（4 面超 4MB 跳过）。
- 真提交拦截：暂存一个带重复键的 `results/_stagedprobe.json` → `git commit` 被爪拦下（rc=1），清理后恢复 rc=0。
- 顺带发现：`results/e25_cash_leg/TREND-a0653f-20261021.json` 在 HEAD 里是 UTF-16 BOM（读者一律 `encoding='utf-8'` 打开），
  worktree 已是 UTF-8——这类「对我能开、对读者打不开」的面从此也会被爪拦下。

## 边界（诚实）

- 爪只判**暂存范围内的 JSON**；`--all` 全库审计（13,327 blob / 1.1GB）未在本轮跑（逐 blob `git show` 会拖死窗口，需 `git cat-file --batch` 流式实现，留作下一切片）。
- 本轮不覆盖「已挂在历史里的坏面」——历史面由发布者自己的重写-披露机制管（E289/E371 族），爪只管出生地。
- 守卫不判业务语义：一个能解析、无重复键但**值写错**的面仍然是错的，那要靠各面自己的 selftest/复现腿。