# -*- coding: utf-8 -*-
# r410 bm-c: resolve CODELY.md rebase conflict (union law) -- HEAD carries bm-a r619
# tail-appended pit entry, our side carries r410 fusion pit entry; keep BOTH.
# Must strip diff3 base marker ||||||| (pre-commit claw does not know it, r511).
import sys

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"

with open(P, "rb") as f:
    raw = f.read()
bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")
nl = "\r\n" if "\r\n" in text else "\n"
lines = text.split(nl)

i_start = None
i_pipe = None
i_eq = None
i_end = None
for i, ln in enumerate(lines):
    if ln.startswith("<<<<<<<") and i_start is None:
        i_start = i
    elif ln.startswith("|||||||") and i_start is not None and i_pipe is None:
        i_pipe = i
    elif ln == "=======" and i_start is not None and i_pipe is not None and i_eq is None:
        i_eq = i
    elif ln.startswith(">>>>>>>") and i_eq is not None and i_end is None:
        i_end = i
if None in (i_start, i_pipe, i_eq, i_end):
    print("ABORT conflict markers not fully located: %s" % ([i_start, i_pipe, i_eq, i_end]))
    sys.exit(2)

head_side = lines[i_start + 1:i_pipe]     # expected: [blank, r619 entry]
ours_side = lines[i_eq + 1:i_end]        # expected: [r410 entry]
if len(head_side) != 2 or head_side[0] != "" or not head_side[1].startswith("- [2026-10-03 10:3x r619 bm-a]"):
    print("ABORT head_side shape: %d lines, first80=%r" % (len(head_side), (head_side[0] if head_side else "")[:80]))
    sys.exit(2)
if len(ours_side) != 1 or not ours_side[0].startswith("- [2026-10-03 10:4x r410 bm-c]"):
    print("ABORT ours_side shape: %d lines" % len(ours_side))
    sys.exit(2)

resolved = head_side + [""] + ours_side   # [blank, r619, blank, r410]
lines[i_start:i_end + 1] = resolved
new_text = nl.join(lines)

# no markers remain anywhere (incl. diff3 base marker)
for bad in ("<<<<<<<", "=======", ">>>>>>>", "|||||||"):
    if any(ln.startswith(bad) for ln in lines):
        print("ABORT residual marker %s" % bad)
        sys.exit(2)
if new_text.count("- [2026-10-03 10:3x r619 bm-a]") != 1 or new_text.count("- [2026-10-03 10:4x r410 bm-c]") != 1:
    print("ABORT union entries not both present exactly once")
    sys.exit(2)
if "???" in head_side[1] or "???" in ours_side[0]:
    print("ABORT mojibake run in union content")
    sys.exit(2)

data = new_text.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as f:
    f.write(data)
print("RESOLVED union: r619 + r410 both kept, markers stripped (incl. diff3 base), bom=%s nl=%r" % (bom, nl))
print("tail=%r" % (new_text[-80:]))
