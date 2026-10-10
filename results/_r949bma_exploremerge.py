"""r949 bm-a explore.md conflict union: E6=ours(closed) + E7=theirs(claimed@bm-b)."""
import re

REL = "state/queue/explore.md"
raw = open(REL, encoding="utf-8", errors="replace").read()

pat = re.compile(
    r"<<<<<<< HEAD\r?\n(.*?)\r?\n?=======\r?\n(.*?)\r?\n?>>>>>>> [^\r\n]*\r?\n?",
    re.S)
m = pat.search(raw)
assert m, "conflict block not found"
head_lines = [l for l in m.group(1).splitlines() if l.strip()]
mine_lines = [l for l in m.group(2).splitlines() if l.strip()]

e6 = [l for l in mine_lines if l.startswith("| E6")]
e7 = [l for l in head_lines if l.startswith("| E7")]
extra_head = [l for l in head_lines if not l.startswith("| E7")]
assert len(e6) == 1 and len(e7) == 1, (len(e6), len(e7))

# order: any extra head lines (none expected) then E6 then E7
merged = extra_head + e6 + e7
new = raw[:m.start()] + "\n".join(merged) + "\n" + raw[m.end():]
open(REL, "w", encoding="utf-8", newline="").write(new)
print("explore.md union: E6 closed (ours) + E7 claimed@bm-b (origin); extra_head=%d" % len(extra_head))
