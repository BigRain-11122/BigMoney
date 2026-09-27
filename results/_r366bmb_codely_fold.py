"""r366 bm-b hot-cold archival (watermark law: CODELY 10,052B > 10KB hard
line after the r366 pitlaw append -> same-window fold).

Moves the four 07:1x hot pitlaw entries (r389 CRLF / r365 resolver /
r389 reconcile / r143 Start-Process) verbatim to
research/memory-archive/202609.md as batch 三十五, leaves the r366 entry
hot, adds one cold-pointer line. Binary face, LF blood, atomic single
write per file, line-level zero-loss check (r365/r389 pitlaws).
"""
import io

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

cb = io.open(CODELY, "rb").read()
ab = io.open(ARCHIVE, "rb").read()
assert cb.endswith(b"\n") and ab.endswith(b"\n")

lines = cb.split(b"\n")
keep, moved = [], []
for ln in lines:
    s = ln.decode("utf-8", errors="strict")
    if s.startswith("- [2026-09-28 07:1x ") and not s.startswith(
            "- [2026-09-28 07:1x r366"):
        moved.append(s)
    else:
        keep.append(s)
assert len(moved) == 4, f"expected 4 hot entries to move, got {len(moved)}"
assert any("r366 bm-b" in s for s in keep), "r366 entry must stay hot"

pointer = (
    "冷层指针：坑律正典 2026-09-28 三十五批（r366 bm-b 窗·水位律当窗整编："
    "r366 新坑律 append 后 10,052B 超 ≤10KB 硬线）：r389 文本读回字节恒等假象"
    "CRLF / r365 resolver 先截断后组装 / r389 tick auto-clear reconcile 漂移 / "
    "r143 Start-Process 无回显批法 四条全文 verbatim=archive 202609.md"
    "『坑律归档 2026-09-28 三十五批』节（行级零丢失校验）。")

# insert pointer line after the 三十四批 pointer line (block order kept)
out_lines = []
inserted = False
for s in keep:
    out_lines.append(s)
    if s.startswith("冷层指针：坑律正典 2026-09-28 三十四批"):
        out_lines.append(pointer)
        inserted = True
assert inserted, "三十四批 pointer line not found"

new_codely = ("\n".join(out_lines)).encode("utf-8")
assert b"\r" not in new_codely

header = (
    "\n## 坑律归档 2026-09-28 三十五批（r366 bm-b 窗·水位律当窗整编："
    "CODELY 10,052B 超 ≤10KB 硬线）\n\n")
sec = "".join("- " + m[2:] + "\n\n" if False else m + "\n\n" for m in moved)
new_archive = ab + header.encode("utf-8") + sec.encode("utf-8")

# line-level zero-loss check: every moved line byte-present in archive
for m in moved:
    assert m.encode("utf-8") in new_archive, "verbatim loss: " + m[:40]
    assert m.encode("utf-8") not in new_codely, "not removed from hot"

io.open(CODELY, "wb").write(new_codely)
io.open(ARCHIVE, "wb").write(new_archive)
print("moved", len(moved), "entries; codely",
      len(new_codely), "B; archive", len(new_archive), "B")
for m in moved:
    print("  -", m[:60])
