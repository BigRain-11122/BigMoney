"""r483 bm-b CODELY.md hot-cold reorg (10KB hard line, same-window law).
r444 pointer-merge paradigm: two cold full-text lines -> archive verbatim,
pointer lines stay. Plus r483 hash-remap clarification on own line."""
import os

repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cp = os.path.join(repo, "CODELY.md")
ap = os.path.join(repo, "research", "memory-archive", "202609.md")

lines = open(cp, encoding="utf-8").read().splitlines(keepends=False)
out, archived, replaced = [], [], 0
KEEP_PREFIXES = ("- [2026-09-30 r492 bm-a]", "- [2026-09-30 r292 bm-c] O-2026-09-30-2230")
POINTER = {
 "- [2026-09-30 r492 bm-a]":
  "- 冷层指针（r483 bm-b 合并·r444 范式）：r492 bm-a Start-Process 长命令引号吞没坑——全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r483 bm-b 窗批』节。",
 "- [2026-09-30 r292 bm-c] O-2026-09-30-2230":
  "- 冷层指针（r483 bm-b 合并·r444 范式）：r292 bm-c O-2230 潜力关注令回执流水行——全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r483 bm-b 窗批』节；正典=令件 fleet/orders/O-2026-09-30-2230-bm-a.md。",
}
for ln in lines:
    hit = next((p for p in KEEP_PREFIXES if ln.startswith(p)), None)
    if hit:
        archived.append(ln)
        out.append(POINTER[hit])
        replaced += 1
    elif ln.startswith("- [2026-09-30 23:4x r483 bm-b] LOWAMP-P1 s1 冻结交付"):
        # hash-remap clarification on own line (zero-burn clarification, r251/r280 precedent)
        out.append(ln.replace("预注册冻结 0c100400f", "预注册冻结 0c100400f·rebase 后 5074b5102"))
    else:
        out.append(ln)

assert replaced == 2, f"expected 2 archives, got {replaced}"
assert len(archived) == 2
open(cp, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")

with open(ap, "a", encoding="utf-8", newline="\n") as fh:
    fh.write("\n## 热冷整编 2026-09-30 r483 bm-b 窗批（CODELY 超 10KB 硬线当窗即办·行级零丢失）\n\n")
    for ln in archived:
        fh.write(ln + "\n")

# zero-loss verification: archived lines verbatim present in archive
a = open(ap, encoding="utf-8").read()
for ln in archived:
    assert ln in a, "zero-loss check FAILED"
print(f"REORG OK | archived={replaced} | CODELY size={os.path.getsize(cp)} | zero-loss verified")
