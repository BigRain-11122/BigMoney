"""r444 bm-a CODELY mini re-arch #2: move superseded r433 pit verbatim to archive (10,781 -> under 10KB)."""
import io, sys, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
src = open("CODELY.md", encoding="utf-8").read()
lines = src.splitlines()
target = None
for ln in lines:
    if ln.startswith("- [2026-09-29 15:1x r433 bm-a]"):
        target = ln
        break
assert target, "r433 entry not found"
lines = [ln for ln in lines if ln != target]
out = "\n".join(lines) + "\n"
open("CODELY.md", "w", encoding="utf-8", newline="").write(out)
with open("research/memory-archive/202609.md", "a", encoding="utf-8", newline="") as f:
    f.write("\n## 热冷整编 2026-09-29 r444 bm-a 窗批补刀（CODELY 10,781B 复超线·r433 判负流水坑律条 verbatim 迁入·行级零丢失）\n\n" + target + "\n")
nb = len(out.encode("utf-8"))
print(f"moved r433 entry ({len(target.encode('utf-8'))}B); CODELY now {nb}B")
assert nb <= 10240, f"still over: {nb}B"
print("UNDER 10KB LINE OK")
