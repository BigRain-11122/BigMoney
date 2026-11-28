"""r2209 (g): record the full sweep in the QA card and state, then stop editing.

The first repair only fixed the newest broken row. A file-wide check says the
same writer leaked 13 table rows (8 heads reading "| %s |", one "%d" round
column, and slots inside prose), 55 double-percent escapes, and 7 rows that had
also lost their leading pipe. All are now repaired without inventing a value:
a lost timestamp reads "(ts-lost · 行由 <sha> 落盘)" with the sha taken from git
blame of the committed line, a lost round reads "(round-lost)" and names the two
neighbouring rounds when it can, anything else reads "(值丢失)".
"""
import io
import json

QA = "qa/fix-broken-close-script-r2209.md"
ADD = """
## 4. 同一缺陷的其余 36 行：一个写者漏了 `%` 一遍

第 2 节只修了最新那行。全文件复查（`grep "%s" / "%d" / "%%"`）发现同一个写者还漏了：
**13 张表行**（8 个表头是 `| %s |`、1 个轮号列是 `%d`、其余是正文里的槽位）、**55 处 `%%`**（
读者看到的是 `8%% vol`、`13.53%%/yr` 这种多一个百分号）、以及 **7 行连行首竖线也丢了**。

修法与第 2 节同一纪律——**不编数字**：

| 缺失项 | 落成什么 | 依据 |
|---|---|---|
| 时间戳 | `(ts-lost · 行由 <sha7> 落盘)` | `git blame --porcelain HEAD` 对该**已提交行**取 commit；工作树版本 blame 会给 `0000000`，故必须对 HEAD 取 |
| 轮号 | `(round-lost)`
 | 无法还原就不猜；1905 行的 `(round-lost · 位于 r1682 与 r1683b 之间)` 把推断依据印出来，不当作结论 |
| 正文里的槽位 | `(值丢失)` | 原文没有可还原的值 |
| `%%` | `%` | 格式串转义泄漏，不是数据 |

脚本链（都在 `results/`，已入 git）：`_r2209bmc_fix_close.py` → `_r2209bmc_fix_report_row.py` →
`_r2209bmc_fix_own_row.py` → `_r2209bmc_fix_all_templates.py` → `_r2209bmc_fix_templates_sweep.py` →
`_r2209bmc_fix_wording.py` → `_r2209bmc_fix_templates_global.py` → `_r2209bmc_fix_heads.py`。

**验证（终态，全文件）**：

```
file lines still carrying a placeholder: []          # %s / %d / %% 全无
表格行以占位符开头的行:                []          # 无 "| %s" 残头
竖线丢失的残头:                        []          # 无 "(值丢失) |" 起头
进度：36 行被改（55 处 %% 还原 + 15 处槽位标记丢失）+ 8 行补回行首竖线与来源
```

**为什么值得做**：这份文件是机队读轮次进展的地方（`round_reports-<id>.md`），
破行没有任何守卫会红——`smoke_test` 不读它，`import_git_coverage` 也不读它。
它坏着，只能靠人一眼看见。这正是 r1609「面只有检查腿没有写者就会永远绿」的反面：
**没有检查腿的面，坏了也没人知道**。
"""

s = io.open(QA, encoding="utf-8", newline="").read()
if "## 4. 同一缺陷的其余" not in s:
    s = s.rstrip("\n") + "\n" + ADD
    io.open(QA, "w", encoding="utf-8", newline="").write(s)
    print("QA card extended")
else:
    print("QA card already extended")

sot = json.load(io.open("state-bm-c.json", encoding="utf-8"))
sot["report_sweep_r2209"] = (
    "The r2208 row was one instance, not the defect: a file-wide sweep of round_reports-bm-c.md found "
    "13 table rows with literal %s/%d slots (8 of them heads), 55 double-percent escapes, and 7 rows that "
    "had also lost their leading pipe. Repaired mechanically without inventing values: lost timestamp -> "
    "'(ts-lost · 行由 <sha> 落盘)' with the sha from git blame HEAD (working-tree blame returns 0000000), "
    "lost round -> '(round-lost)' (line 1905 names the bracketing rounds r1682/r1683b instead of guessing "
    "1683), other slots -> '(值丢失)', '%%' -> '%'. Final check: zero placeholders in the file. 8 scripts "
    "results/_r2209bmc_fix_*.py, all committed."
)
sot["carrier_debt_r2209"] = (
    "paid: repair-or-retire of Tools/_r820bmc_close.py (carried since r2200/r2203), the unformatted r2208 "
    "report row, and the 36 other rows the same writer leaked. still owed: live_book_section_bars 36-section "
    "drift (waits for the flying chain to land), full smoke, and the S4U re-register of Bigmoney-LoopWatchdog "
    "(physical item, needs elevation)."
)
io.open("state-bm-c.json", "w", encoding="utf-8", newline="\n").write(
    json.dumps(sot, ensure_ascii=False, indent=1) + "\n")
print("state annotated")
