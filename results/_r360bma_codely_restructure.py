# -*- coding: utf-8 -*-
"""r360 bm-a CODELY.md in-window hot-cold restructure (O-20260927-0230 <=10KB hard line):
current 10,254B already 14B over; new r360 pit-law row (+~400B) requires fold.
Fold pick = r110 bm-c row (hot full-text ~500B, verbatim NOT yet in archive):
1) append verbatim to archive 202609.md as batch-32 section (zero-loss first)
2) replace hot row with pointer line
3) append new r360 resolver-cap pit-law row (passes four-question gate:
   lasting value / not already canon / lesson-first / one-thing)
4) verify: archive verbatim byte-equal, CODELY <= 10,240B, line-count sane."""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CP = "CODELY.md"
AP = "research/memory-archive/202609.md"
LIMIT = 10240

clines = io.open(CP, encoding="utf-8").read().split("\n")
# normalize trailing newline handling: keep exact structure
raw = io.open(CP, encoding="utf-8").read()
assert raw.endswith("\n"), "CODELY must end with newline"
clines = raw[:-1].split("\n") if raw[:-1] else []

# locate r110 row
idx = [i for i, l in enumerate(clines) if l.startswith("- [2026-09-27 22:1x r110 bm-c] 坑律：孪生面单腿")]
assert len(idx) == 1, f"r110 row count {len(idx)}"
i110 = idx[0]
r110_row = clines[i110]

NEW_ROW = ("- [2026-09-27 22:3x r360 bm-a] 坑律：rolling-ledger union 解方禁自造 cap 截留（r360 实弹：resolver "
           "发明 cap=max(len) 把 201+201 截成 201 静默丢最老行 vs 正典 |A∪B|=202——r85 生产者滚动窗律=反假丢旗 "
           "adjudication 非截留许可、r344 先例 236 全留；修正窗=推前 amend 补行+resolver 去 cap；滚动窗归生产者"
           "写回面非 resolver）——指针=results/_r360bma_resolve.py。")

PTR_ROW = ("- [2026-09-27 22:1x r110 bm-c] 坑律（三十二批外迁·指针）：孪生面单腿 UU 的 :3: 探针空串险（resolver "
           "git show 必验 rc==0 且非空；非 UU 腿禁起 :2:/:3: 探针；误写恢复=git checkout -- <path>）——全文 "
           "verbatim=archive 202609.md『坑律归档 2026-09-27 三十二批』节。")

# 1) archive verbatim FIRST (zero-loss before fold)
araw = io.open(AP, encoding="utf-8").read()
assert "三十二批" not in araw, "batch-32 already exists"
batch = ("\n## 坑律归档 2026-09-27 三十二批（r360 bm-a·CODELY 超线当窗整编·行级零丢失）\n"
         "- r110 bm-c 原行 verbatim：" + r110_row + "\n")
io.open(AP, "a", encoding="utf-8", newline="\n").write(batch)

# 2+3) CODELY: fold r110 -> pointer, append new r360 row at tail
clines[i110] = PTR_ROW
clines.append(NEW_ROW)
out = "\n".join(clines) + "\n"
io.open(CP, "w", encoding="utf-8", newline="\n").write(out)

# 4) verify
nb = len(io.open(CP, "rb").read())
achk = io.open(AP, encoding="utf-8").read()
assert r110_row in achk, "archive verbatim lost"
assert r110_row not in io.open(CP, encoding="utf-8").read(), "hot full row still present"
cchk = io.open(CP, encoding="utf-8").read()
assert NEW_ROW in cchk and PTR_ROW in cchk
print(f"CODELY {10_254}B -> {nb}B (limit {LIMIT}) {'OK' if nb <= LIMIT else 'STILL OVER'}")
print(f"r110 row bytes folded: {len(r110_row.encode('utf-8'))} -> pointer {len(PTR_ROW.encode('utf-8'))}, "
      f"new row {len(NEW_ROW.encode('utf-8'))}B")
assert nb <= LIMIT, f"still over hard line: {nb}"
print("zero-loss: r110 verbatim in archive batch-32 OK")
