# QA · r2209 · 一个自提交起就跑不了的文件 + 一行没被格式化的轮报行

机器：bm-c（`fleet/machine.json` → `machine_id=bm-c`）｜日期：2026-11-28｜轮号：2209

## 1. `Tools/_r820bmc_close.py` 自提交起不可解析

**发现来源**：r2203 的 `import_git_coverage` 面（`EVERY_IMPORTED_MODULE_AND_EVERY_NAMED_LEG_IS_IN_GIT`）报了
「committed files that cannot be parsed: 1 broken」。r2200/r2203 两轮把它记为 repair-or-retire 欠账，一直挂着。

**根因**：第 130 行的字符串字面量漏了闭合引号（第 131 行才是它的下一段），所以 `py_compile` 直接 SyntaxError。
这不是运行期 bug，是**从来没能被导入过**。

| 步骤 | 证据 |
|---|---|
| 修前编译 | `python -m py_compile Tools\_r820bmc_close.py` → `SyntaxError: unterminated string literal (detected at line 130)`，rc=1 |
| 隔离区预扫（TREASURE_PROTECTION_LAW §2） | `python Tools\treasure_guard.py prescan Tools\_r820bmc_close.py` → `zero hits over 1 path(s)`，rc=0（可再生工件，放行） |
| 引用面核查 | `rg -l "_r820bmc_close"` 命中只在 `knowledge/METHODOLOGY_ASSETS.md` / `state-bm-c.json` / `round_reports-bm-c.md` / `fleet/machines/bm-c.json` / `qa/import-git-coverage-r2203.md` —— **没有任何代码 import 它**，改它零行为风险 |
| 修法 | 结果脚本 `results/_r2209bmc_fix_close.py`：L130 末尾补 `"`、L131 行首补 `"`（相邻字面量拼接，语义不变；保留各行的 CRLF 原状） |
| 修后编译 | `py_compile` → rc=0 |

**面复核**（同一轮重 derive，非手工改面）：

```
python scripts/import_git_coverage.py run
headline EVERY_IMPORTED_MODULE_AND_EVERY_NAMED_LEG_IS_IN_GIT
scanned 2953 files / 21055 imports / 3569 local edges (parse errors 1)
imports missing in git: 0
committed files that cannot be parsed: 0 broken / 1 generator templates   <- 原 "1 broken"
chain named scripts 345: missing on disk 0 / missing in git 0
```

0 broken = 这条腿的红项清零；`1 generator templates` 是 `@@SUB_BLOCK@@` 模板按内容分类的正常项（r2203 已判读），不是缺陷。

## 2. 轮报告最后一行是没被格式化的模板

**症状**：`round_reports-bm-c.md` 第 2895 行（r2208 那行）字面以 `| %s | %d |` 开头，正文里还有 `%%`。
写轮报的代码构造了格式串却没 `%` 一遍，读者看到的是破行。

**修法**：`results/_r2209bmc_fix_report_row.py` —— 时间戳取该文件自己的写入时刻 `2026-11-28T08:06+08:00`、
轮号 2208，替换后再把 `%%` 还原成 `%`。**不重写任何正文**。

| 验证 | 结果 |
|---|---|
| 行首 | `\| 2026-11-28T08:06+08:00 \| 2208 \| 修红闭环：...` |
| 残留 `%s` | False |
| 残留 `%%` | False |
| 其余行 | 未触碰（只改命中行索引） |

## 3. 本轮未做（如实）

- **全量冒烟未跑**：另一条分离的全链（pid 33880，`python -u Tools\s6_chain_bmc.py 2209`，09:04:54 起）正在
  同一工作树上跑 415 腿，跑到第 102 腿（`etf_book_spanning`，09:20:49 完成）后进入 `etf_book_pre2020.py refresh`
  已 21 分钟且 CPU 单核持续满载（8 秒采样 +7.98s）= 活性正常、不是死锁。按 r1907「同树多宿主禁改共享面、
  禁重跑 S6 链」，本轮**不重跑链、不动它正在写的面**，因此也不宣称红数下降。
  进度实据：`results/_s6chain_progress.bm-c.jsonl`（round=2209，leg_done=106，非零腿仅 `capital_marginal_road rc=3`）。
- **`live_book_section_bars` 的 36 节代差未由本轮关闭**：`check` 输出 `CHECK_OK verdict=PAGE_MIXES_BARS
  headline=2026-11-27 off=36 unknown=4`，其中 lag=1（停在 11-26）的 30 节由在飞链负责（`etf_book_spanning`
  已被它刷到 11-27 实证），本轮只读不抢。

## 判词

`A_FILE_THAT_NEVER_PARSED_IS_NOW_PARSEABLE`——两处修复都是「面说自己错，而不是我猜它错」，
证据在产物里（`results/import_git_coverage.json`、`round_reports-bm-c.md` L2895）。
