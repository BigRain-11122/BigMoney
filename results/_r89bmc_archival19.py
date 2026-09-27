# -*- coding: utf-8 -*-
"""r89 bm-c 19th-batch in-window archival (CODELY 12633B > 10240 hard line, watermark law:
in-window immediate, no waiting). Moves 5 full-text pitlaw entries to
research/memory-archive/202609.md '坑律归档 2026-09-27 十九批' section verbatim
(line-level zero-loss), replaces each with a pointer line (十九批外迁·指针),
adds one batch-note line. Python authoritative (PS Char-trap law r88)."""
import io, re

MOVE_PREFIXES = [
    "- [2026-09-27 15:5x r332 bm-a] 坑律：**",
    "- [2026-09-27 15:5x r331 bm-b] 坑律：**",
    "- [2026-09-27 16:0x r334 bm-a] 坑律：**",
    "- [2026-09-27 15:2x r87 bm-c] 坑律：**",
    "- [2026-09-27 15:5x r88 bm-c] 坑律：**",
]

codely = io.open("CODELY.md", encoding="utf-8").read()
lines = codely.splitlines(keepends=False)
nb = "\r\n" if "\r\n" in codely else "\n"

moved, kept = [], []
for l in lines:
    if any(l.startswith(p) for p in MOVE_PREFIXES):
        moved.append(l)
    else:
        kept.append(l)
assert len(moved) == 5, f"expected 5 full entries, got {len(moved)}: {[m[:60] for m in moved]}"

def pointer_for(entry):
    hdr_end = entry.index("坑律：**") + len("坑律：**")
    # summary = bold clause up to first —— or first 。（ whichever first, capped
    rest = entry[hdr_end:]
    cut = len(rest)
    for stopper in ("——", "。"):
        i = rest.find(stopper)
        if i != -1 and i < cut:
            cut = i
    summary = rest[:cut].strip()
    if len(summary) > 90:
        summary = summary[:90]
    head = entry[:entry.index("坑律：**")]
    return f"{head}坑律（十九批外迁·指针）：{summary}——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 十九批』节。"

pointers = [pointer_for(m) for m in moved]
batch_note = ("- 十九批外迁（r89 bm-c·2026-09-27·水位律当窗整编·行级零丢失）：r332 bma commit 演练脏树律/r331 bmb tick 竞态窗律/"
              "r334 bma max-ts 毒化律/r87 bmc union 键探律/r88 bmc 身份律五条目外迁=归档十九批节"
              "（12633B 破 ≤10KB 硬线=律触发当窗办勿等月）。")

# insert pointers at the positions of the moved entries (order-preserving), batch note at EOF
final = []
mi = 0
for l in lines:
    if any(l.startswith(p) for p in MOVE_PREFIXES):
        final.append(pointers[mi])
        mi += 1
    else:
        final.append(l)
final.append(batch_note)
new_codely = nb.join(final) + nb

# zero-loss check 1: every moved line lands in archive verbatim
arch = io.open("research/memory-archive/202609.md", encoding="utf-8").read()
section = "\n## 坑律归档 2026-09-27 十九批（r89 bm-c·超线当窗整编·行级零丢失）\n" + nb.join(moved) + nb
assert all(m in section for m in moved)
new_arch = arch + ("\r\n" if arch.endswith("\r\n") else "\n" if arch.endswith("\n") else nb) + section.lstrip("\r\n")
for m in moved:
    assert m in new_arch, f"archive lost: {m[:60]}"

# zero-loss check 2: CODELY side accounting (orig lines == final ∪ moved, set-level)
orig_set = set(l for l in lines if l.strip())
final_set = set(final)
for l in orig_set:
    assert l in final_set or l in moved or any(l in mm for mm in moved), f"CODELY lost line: {l[:70]}"
# pointers superset discipline: no strict-subset dup among canon lines
canons = [l for l in final if l.startswith("- 坑律正典全量归档")]
for i, a in enumerate(canons):
    for b in canons:
        if a != b and b.startswith(a):
            raise SystemExit(f"canon strict-subset dup exists: {a[:60]}")

bad = [l for l in final if re.match(r"^(<{7}|>{7}|={7})\s", l)]
assert not bad, f"markers leaked: {bad[:2]}"

io.open("CODELY.md", "w", encoding="utf-8", newline="").write(new_codely)
io.open("research/memory-archive/202609.md", "w", encoding="utf-8", newline="").write(new_arch)

sz = len(new_codely.encode("utf-8"))
assert sz < 10240, f"CODELY still {sz}B over 10KB"
back = io.open("CODELY.md", encoding="utf-8").read()
assert all(p in back for p in pointers)
print(f"19th-batch archival OK: CODELY {len(codely.encode('utf-8'))}B -> {sz}B; moved x{len(moved)} verbatim; archive +{len(new_arch)-len(arch)}B")
print("ARCHIVE19-R89-OK")
