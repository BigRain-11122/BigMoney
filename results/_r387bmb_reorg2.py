# r387 bm-b reorg batch-54 (post-storm-union): CODELY.md 10,519B > 10KB
# -> move my two r387 pitlaw entries verbatim to archive 202609.md batch 54,
# leave two pointer lines. bm-c r169 entry stays in place (their fresh law).
import io, os

C = "CODELY.md"
A = r"research\memory-archive\202609.md"

ctext = io.open(C, encoding="utf-8").read()
lines = ctext.split("\n")

e1_mark = "- [2026-09-28 14:3 r387 bm-b] 坑律补章"
e2_mark = "- [2026-09-28 14:3 r387 bm-b] 坑律：**心跳/资源快照字段换算"
i1 = [i for i, ln in enumerate(lines) if ln.startswith(e1_mark)]
i2 = [i for i, ln in enumerate(lines) if ln.startswith(e2_mark)]
assert len(i1) == 1 and len(i2) == 1, (i1, i2)
assert i2[0] == i1[0] + 1, (i1, i2)  # adjacent
e1, e2 = lines[i1[0]], lines[i2[0]]

ptr1 = (
    "冷层指针：坑律正典 2026-09-28 五十四批（r387 bm-b 窗·水位律当窗整编："
    "push-storm 并集后 10,519B 复超 ≤10KB 硬线）：r387 judge-finalize 同链"
    "串行律 一条全文 verbatim=archive 202609.md『坑律归档 2026-09-28 五十四"
    "批』节（行级零丢失校验）。"
)
ptr2 = (
    "冷层指针：坑律正典 2026-09-28 五十四批（续）：r387 资源快照换算复用律"
    " 一条全文 verbatim=archive 202609.md『坑律归档 2026-09-28 五十四批』节"
    "（行级零丢失校验）。"
)

header = (
    "\n\n## 坑律归档 2026-09-28 五十四批（r387 bm-b 窗·水位律当窗整编："
    "push-storm 并集后 10,519B 复超 ≤10KB 硬线）：r387 judge-finalize 同链串"
    "行律 / r387 资源快照换算复用律 两条全文 verbatim（行级零丢失校验）。\n"
)

atext = io.open(A, encoding="utf-8").read()
assert "五十四批" not in atext, "batch collision"
if not atext.endswith("\n"):
    atext += "\n"
new_archive = atext + header + e1 + "\n" + e2 + "\n"

new_lines = lines[:i1[0]] + [ptr1, ptr2] + lines[i2[0] + 1:]
new_code = "\n".join(new_lines)
if not new_code.endswith("\n"):
    new_code += "\n"

assert e1 not in new_code and e2 not in new_code
for ln in (e1, e2):
    assert new_archive.count(ln) == 1, "verbatim count != 1 in archive"

with io.open(A, "w", encoding="utf-8", newline="\n") as f:
    f.write(new_archive)
with io.open(C, "w", encoding="utf-8", newline="\n") as f:
    f.write(new_code)

a2 = io.open(A, encoding="utf-8").read()
c2 = io.open(C, encoding="utf-8").read()
assert a2.count(e1) == 1 and a2.count(e2) == 1
assert e1 not in c2 and e2 not in c2
print("batch-54 reorg OK: CODELY.md =", os.path.getsize(C),
      "B | archive =", os.path.getsize(A), "B")
