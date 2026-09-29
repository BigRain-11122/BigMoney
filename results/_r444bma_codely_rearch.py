"""r444 bm-a CODELY in-window re-arch: pure pointer lines verbatim -> archive, per r225 precedent."""
import io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
src = open("CODELY.md", encoding="utf-8").read()
lines = src.splitlines()

moved, kept = [], []
for ln in lines:
    is_ptr = ln.startswith("- 冷层指针：") or ln.startswith("冷层指针：")
    is_proj_ptr = ln.startswith("（W8 收口定案流水条")
    if is_ptr or is_proj_ptr:
        moved.append(ln)
    else:
        kept.append(ln)

# keep the two standing law lines (they contain 冷层指针/坑律归-archive mentions but are LAWS)
law_snippets = ("流水型条目", "≤10KB 硬线")
final_moved = []
recheck = []
for ln in moved:
    if any(s in ln for s in law_snippets) and ("按 D-20260924-01" in ln or "O-20260927-0230" in ln):
        recheck.append(ln)
    else:
        final_moved.append(ln)

out_lines = []
for ln in kept + recheck:
    if ln.strip() == "" and out_lines and out_lines[-1].strip() == "":
        continue  # collapse consecutive blanks
    out_lines.append(ln)

moved_bytes = sum(len(l.encode("utf-8")) for l in final_moved)
new_ptr = ("- 冷层指针：坑律一〇九~一一六批+流水整编/指针合并历史指针行（含 W8/W9/W10 冻结收口+A158 择时判决收口"
           "+r225/r434/r435/r437/r442 窗批指针）共 %d 行全文 verbatim=archive 202609.md『指针合并归档 2026-09-29 "
           "r444 bm-a 窗批』节（r444 bm-a 窗水位 12,711B 超 ≤10KB 硬线当窗即办·行级零丢失校验·活律行与坑律条目"
           "全数留热）。" % len(final_moved))
# insert consolidated pointer at end of Reference section (file end)
out_lines.append(new_ptr)
out = "\n".join(out_lines) + "\n"

sec = "\n## 指针合并归档 2026-09-29 r444 bm-a 窗批（CODELY 热层指针行 verbatim 迁入·水位 12,711B 超线当窗即办）\n\n"
sec += "\n\n".join(final_moved) + "\n"
with open("research/memory-archive/202609.md", "a", encoding="utf-8", newline="") as f:
    f.write(sec)

open("CODELY.md", "w", encoding="utf-8", newline="").write(out)
nb = len(out.encode("utf-8"))
print(f"moved {len(final_moved)} pointer lines ({moved_bytes}B) to archive; CODELY now {nb}B")
assert nb <= 10240, f"still over line: {nb}B"
print("UNDER 10KB LINE OK")
