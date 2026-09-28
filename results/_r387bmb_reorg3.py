# r387 bm-b reorg batch-55: CODELY.md 10,575B > 10KB -> move the r387
# storm/lane dual-face-sync entry verbatim to archive batch 55, pointer stays.
import io, os

C = "CODELY.md"
A = r"research\memory-archive\202609.md"

ctext = io.open(C, encoding="utf-8").read()
lines = ctext.split("\n")
mark = "- [2026-09-28 14:4 r387 bm-b] 坑律：**池记账 status 类修复必须双面同步"
idx = [i for i, ln in enumerate(lines) if ln.startswith(mark)]
assert len(idx) == 1, idx
entry = lines[idx[0]]

ptr = (
    "冷层指针：坑律正典 2026-09-28 五十五批（r387 bm-b 窗·水位律当窗整编："
    "storm 条 append 后 10,575B 复超 ≤10KB 硬线）：r387 池修复双面同步律"
    "（shared+lane）+轮尾 add -A 前 reload 断言 一条全文 verbatim=archive "
    "202609.md『坑律归档 2026-09-28 五十五批』节（行级零丢失校验）。"
)
header = (
    "\n\n## 坑律归档 2026-09-28 五十五批（r387 bm-b 窗·水位律当窗整编："
    "storm 条 append 后 10,575B 复超 ≤10KB 硬线）：r387 池修复双面同步律+"
    "add -A reload 断言 一条全文 verbatim（行级零丢失校验）。\n"
)

atext = io.open(A, encoding="utf-8").read()
assert "五十五批" not in atext, "batch collision"
if not atext.endswith("\n"):
    atext += "\n"
new_archive = atext + header + entry + "\n"
new_lines = lines[:idx[0]] + [ptr] + lines[idx[0] + 1:]
new_code = "\n".join(new_lines)
if not new_code.endswith("\n"):
    new_code += "\n"

assert new_archive.count(entry) == 1 and entry not in new_code
with io.open(A, "w", encoding="utf-8", newline="\n") as f:
    f.write(new_archive)
with io.open(C, "w", encoding="utf-8", newline="\n") as f:
    f.write(new_code)

a2 = io.open(A, encoding="utf-8").read()
c2 = io.open(C, encoding="utf-8").read()
assert a2.count(entry) == 1 and entry not in c2
print("batch-55 reorg OK: CODELY.md =", os.path.getsize(C),
      "B | archive =", os.path.getsize(A), "B")
