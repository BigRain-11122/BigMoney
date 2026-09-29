# -*- coding: utf-8 -*-
"""r229 bm-c CODELY.md waterline reorg (hot->cold migration, zero-loss verified).

Trigger: append pushed CODELY.md to 10,067B > 10,000B hard line (pit-canon law:
append-then-over = same-window reorg, never wait for month-end).
Migration: the two bm-c-authored numbered pit batches (113 r223 API-crash legacy
absorb law / 114 r225 PS param string-shred) move verbatim to
research/memory-archive/202609.md under a dated section; one compact pointer
row replaces them in the hot layer (109/110/111 pointer-row precedent).
"""
import sys

P_CODELY = "CODELY.md"
P_ARCH = "research/memory-archive/202609.md"

raw = open(P_CODELY, "rb").read().decode("utf-8")
nl = "\r\n" if "\r\n" in raw else "\n"
lines = raw.splitlines()  # handles mixed \r\n / \n tails byte-safely

key1 = "- [2026-09-29 15:4x r223 bm-c]"
key2 = "- [2026-09-29 16:2x r225 bm-c]"
idx1 = [i for i, l in enumerate(lines) if l.startswith(key1)]
idx2 = [i for i, l in enumerate(lines) if l.startswith(key2)]
assert len(idx1) == 1 and len(idx2) == 1, (idx1, idx2)
e1, e2 = lines[idx1[0]], lines[idx2[0]]
assert e1.rstrip().endswith("（本窗实弹）。"), e1[-30:]
assert e2.rstrip().endswith("PS 隐式类型转换吞噬面）。"), e2[-30:]

# remove both (reverse order)
for i in sorted([idx1[0], idx2[0]], reverse=True):
    del lines[i]

ptr = ("- 冷层指针：坑律一百一十三批（r223 bm-c·API 猝死遗产先落地律=S0 遗产吸收 commit+push 先行/"
       "轮首脏 mtime+进程表归因/orders 差集 README 误计禁令/5min 零输出自旋禁令四件）"
       "+一百一十四批（r225 bm-c·PS 跑批循环参数字串拆散坑=多腿跑批显式参数直跑正解·每腿 $LASTEXITCODE 检查）"
       "全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r229 bm-c 窗批』节"
       "（r229 bm-c 窗水位 10,067B 超 ≤10KB 硬线当窗即办·行级零丢失校验；"
       "注=r435 bm-a 件自号「一一三批」与本 113 批撞号·寻址以机id+日期为准）。")

first_dated = next(i for i, l in enumerate(lines) if l.startswith("- [2026-09-29 15:1x r433 bm-a]"))
lines.insert(first_dated, ptr)
open(P_CODELY, "wb").write(nl.join(lines).encode("utf-8"))

# archive append: verbatim lines
araw = open(P_ARCH, "rb").read().decode("utf-8")
anl = "\r\n" if "\r\n" in araw else "\n"
if not araw.endswith("\n"):
    araw += anl
sec_lines = [
    "## 坑律归档 2026-09-29 r229 bm-c 窗批（水位 10,067B 超 ≤10KB 硬线当窗即办·行级零丢失校验）",
    "（自 CODELY.md Reference 节迁入 verbatim 两行：一百一十三批 r223 bm-c API 猝死遗产先落地律 "
    "+ 一百一十四批 r225 bm-c PS 跑批循环参数字串拆散坑。编号撞号注记：r435 bm-a 件自号「一一三批」"
    "与本批 113 同数=历史编号撞号，检索以 机id+日期 寻址为准。）",
    "",
    e1,
    e2,
    "",
]
araw += anl.join(sec_lines)
open(P_ARCH, "wb").write(araw.encode("utf-8"))

# verify
acheck = open(P_ARCH, "rb").read().decode("utf-8")
newcheck = open(P_CODELY, "rb").read().decode("utf-8")
ok1 = e1 in acheck
ok2 = e2 in acheck
gone1 = e1 not in newcheck
gone2 = e2 not in newcheck
size = len(newcheck.encode("utf-8"))
dated = [l[:42] for l in newcheck.splitlines() if l.startswith("- [2026-09-29")]
print("verbatim e1 in archive:", ok1)
print("verbatim e2 in archive:", ok2)
print("removed from CODELY:", gone1 and gone2)
print("CODELY new size:", size, "B; under 10000:", size < 10000)
print("remaining dated entries:", len(dated))
for d in dated:
    print("  -", d)
if not (ok1 and ok2 and gone1 and gone2 and size < 10000):
    print("VERIFY FAIL")
    sys.exit(2)
print("REORG PASS")
