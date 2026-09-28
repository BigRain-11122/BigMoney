# r387 bm-b hot-cold reorg: CODELY.md 10,625B > 10KB hard line ->
# move r386 judge-finalize entry verbatim to archive 202609.md batch 53,
# leave cold-layer pointer. Line-level zero-loss verification.
import io, os

C = "CODELY.md"
A = r"research\memory-archive\202609.md"

ctext = io.open(C, encoding="utf-8").read()
lines = ctext.split("\n")
target_idx = [i for i, ln in enumerate(lines)
              if ln.startswith("- [2026-09-28 14:2 r386 bm-b] 坑律：**judge-finalize")]
assert len(target_idx) == 1, target_idx
i = target_idx[0]
entry = lines[i]
assert entry.endswith("results/_r386bmb_pool_flips.py。"), entry[-60:]

header = (
    "\n\n## 坑律归档 2026-09-28 五十三批（r387 bm-b 窗·水位律当窗整编："
    "r387 新坑律 append 后 10,625B 复超 ≤10KB 硬线）：r386 judge-finalize "
    "5min 内联墙 一条全文 verbatim（行级零丢失校验）。\n"
)
pointer = (
    "冷层指针：坑律正典 2026-09-28 五十三批（r387 bm-b 窗·水位律当窗整编："
    "r387 新坑律 append 后 10,625B 复超 ≤10KB 硬线）：r386 judge-finalize "
    "5min 内联墙 一条全文 verbatim=archive 202609.md『坑律归档 2026-09-28 "
    "五十三批』节（行级零丢失校验）。"
)

atext = io.open(A, encoding="utf-8").read()
assert "五十三批" not in atext, "batch collision"
if not atext.endswith("\n"):
    atext += "\n"
new_archive = atext + header + entry + "\n"

new_code = "\n".join(lines[:i] + [pointer] + lines[i + 1:])
if not new_code.endswith("\n"):
    new_code += "\n"

# zero-loss verification: verbatim entry present in archive exactly once
assert new_archive.count(entry) == 1, "verbatim count != 1"
assert entry not in new_code.replace(pointer, "", 1), "entry residue in CODELY"
assert pointer in new_code

with io.open(A, "w", encoding="utf-8", newline="\n") as f:
    f.write(new_archive)
with io.open(C, "w", encoding="utf-8", newline="\n") as f:
    f.write(new_code)

# post-write byte verification
a2 = io.open(A, encoding="utf-8").read()
c2 = io.open(C, encoding="utf-8").read()
assert a2.count(entry) == 1 and entry in a2
assert entry not in c2
print("reorg OK: entry", len(entry.encode('utf-8')), "B -> archive batch 53")
print("CODELY.md =", os.path.getsize(C), "B | archive =", os.path.getsize(A), "B")
