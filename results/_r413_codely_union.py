"""CODELY.md memory-union resolve (r413 window vs bm-c r198 batch-84 append).

Merged = my :3: (archival applied + pointer + batch-83) + their :3:-missing new entry
appended at file bottom (commit-time order: their r198 landed origin-first, both
entries kept verbatim, zero line-level loss; my 3 archived entries live in
research/memory-archive/202609.md per entry-in-tree-OR-archive law r327).
If merged > 10240B, archive one more aged entry (r412 bm-a batch-81) same-window.
"""
import io
import subprocess


def blob(s):
    return subprocess.run(["git", "show", f":{s}:CODELY.md"], capture_output=True).stdout.decode("utf-8")


COLD = "research/memory-archive/202609.md"
SECTION_MARKER = "## 坑律归档 2026-09-29 r413 bm-a 窗批"
EXTRA_SECTION = "\n## 坑律归档 2026-09-29 r413 bm-a 窗批补（水位律二次整编·行级零丢失校验）\n\n"

mine = blob("3")
theirs = blob("2")
ml, tl = mine.splitlines(), theirs.splitlines()
ms = set(ml)
their_new = [ln for ln in tl if ln not in ms and ln not in blob("1").splitlines()]
assert len(their_new) == 1, f"expected exactly 1 their-new line, got {len(their_new)}"

merged = mine.rstrip("\n") + "\n" + their_new[0] + "\n"
size = len(merged.encode("utf-8"))
print(f"merged={size}B their-new appended")

if size > 10240:
    # same-window second archival: r412 bm-a batch-81 entry (aged 1 round, archivable)
    # locate by unique prefix
    prefix = "- [2026-09-29 03:5x] r412 bm-a 坑律八十一批"
    cand = [ln for ln in merged.splitlines() if ln.startswith(prefix)]
    assert len(cand) == 1, "aged entry not uniquely found"
    entry = cand[0]
    merged = merged.replace(entry + "\n", "", 1)
    cold = io.open(COLD, encoding="utf-8").read()
    assert EXTRA_SECTION.strip() not in cold
    cold = cold.rstrip("\n") + "\n" + EXTRA_SECTION + entry + "\n"
    io.open(COLD, "w", encoding="utf-8", newline="\n").write(cold)
    # pointer amendment: extend the existing r413-window pointer line
    old_ptr_marker = "冷层指针：坑律正典 2026-09-29 r407 bm-b 八十一批"
    idx = merged.find(old_ptr_marker)
    assert idx >= 0
    eol = merged.find("\n", idx)
    merged = merged[:eol] + "+r412 bm-a 八十一批（advisory 候选注记陈旧陷阱）" + merged[eol:]
    size2 = len(merged.encode("utf-8"))
    assert size2 <= 10240, f"still over line: {size2}"
    assert entry not in merged and entry in io.open(COLD, encoding="utf-8").read()
    print(f"second archival applied -> {size2}B (aged entry verbatim in archive)")

io.open("CODELY.md", "w", encoding="utf-8", newline="\n").write(merged)
final = io.open("CODELY.md", encoding="utf-8").read()
assert their_new[0] in final
print(f"CODELY.md resolved: {len(final.encode('utf-8'))}B, their-new verbatim kept, parse=markdown-line-level OK")
