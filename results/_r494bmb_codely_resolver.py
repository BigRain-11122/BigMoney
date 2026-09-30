"""r494 CODELY.md conflict-marker ER (expedited): the failed resolver left
raw <<<<<<< / ======= / >>>>>>> markers committed+pushed; correct union =
ours(origin: r302 + r503 + bm-c r303 single-source entry) + mine(r494
entry, the only unique content on the theirs side)."""
import re

p = "CODELY.md"
src = open(p, encoding="utf-8").read()
m = re.search(r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]+\n",
              src, re.S)
assert m, "conflict region not found"
ours, theirs = m.group(1), m.group(2)
# my r494 entry = the theirs-side line(s) not present in ours
mine = [ln for ln in theirs.splitlines()
        if ln.startswith("- [2026-10-01 05:5x r494 bm-b]")]
assert len(mine) == 1, f"expected exactly one r494 entry, got {len(mine)}"
out = src[:m.start()] + ours + "\n\n" + mine[0] + "\n" + src[m.end():]
for marker in ("<<<<<<<", "=======", ">>>>>>>"):
    assert marker not in out, f"marker {marker} still present"
open(p, "w", encoding="utf-8", newline="").write(out)
print(f"ER ok: ours={len(ours.splitlines())} lines + r494 entry "
      f"({len(mine[0])} chars); markers cleared; total "
      f"{len(out.splitlines())} lines")
