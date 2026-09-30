# -*- coding: utf-8 -*-
"""r283 bm-c same-window hot-cold archival: CODELY over-line 10,411B -> compact per O-20260927-0230 law.
Moves 4 verbose entries (r474 bm-b / r486 bm-a / r475 bm-b x2) verbatim to archive 202609.md,
replaces with one compact pointer line. Zero-loss asserted line-by-line.
"""
import io, sys

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

MARKERS = [
    "- [2026-09-30 r474 bm-b] \u53cc\u5b9e\u73b0\u4e92\u8bc1\u5171\u56e0\u76f2\u533a\u5751",
    "- [2026-09-30 18:5x r486 bm-a] \u810f\u6811\u5e76\u53d1\u7a97\u53cc\u540c\u6b65\u5751\u5f8b",
    "- [2026-09-30 r475 bm-b] rebase continue AD \u6001\u5751",
    "- [2026-09-30 19:2x r475 bm-b] O-20260930-1901 \u56de\u6267",
]

POINTER = (
    "- \u51b7\u5c42\u6307\u9488\uff08r283 \u5408\u5e76\u00b7\u6307\u9488\u5408\u5e76\u5f52\u6863 r444 \u8303\u5f0f\uff09\uff1ar474 bm-b \u53cc\u5b9e\u73b0\u4e92\u8bc1\u5171\u56e0\u76f2\u533a\u5751\uff08\u6210\u672c\u4e58\u5b50\u5fc5\u52a0\u624b\u7b97\u503c\u817f+\u5148 append \u540e dump\uff09"
    "+r486 bm-a \u810f\u6811\u5e76\u53d1\u7a97\u53cc\u540c\u6b65\u5751\u5f8b\uff08ff-only \u7b49\u4ef7+pathspec \u504f\u63d0\u4ea4+ISO \u504f\u79fb strftime\uff09"
    "+r475 bm-b rebase continue AD \u6001\u5751\uff08AD=\u56de\u79fb add \u968f\u884c+C \u65cf\u5171\u4eab\u9762\u4e09\u6001\u8bed\u4e49\u5148\u8bfb\u540e\u5224\uff09"
    "+r475 bm-b O-20260930-1901 \u56de\u6267\uff08\u56db\u786c\u95ee\u5408\u89c4\u81ea\u67e5\u5168\u8fc7\uff09\u2014\u2014\u56db\u6761\u5168\u6587 verbatim=archive 202609.md\u300e\u70ed\u51b7\u6574\u7f16 2026-09-30 r283 bm-c \u7a97\u6279\u300f\u8282\u3002"
)

SECTION_HEADER = "\n## \u70ed\u51b7\u6574\u7f16 2026-09-30 r283 bm-c \u7a97\u6279\uff08\u540c\u7a97 CODELY \u8d85\u7ebf\u5373\u529e\u00b710,411B\u2192\u786c\u7ebf 10,240B\u00b7\u96f6\u4e22\u5931\u65ad\u8a00\u8fc7\uff09\n"

with io.open(CODELY, "r", encoding="utf-8") as f:
    lines = f.read().splitlines(keepends=True)

moved = []
out = []
for line in lines:
    stripped = line.rstrip("\r\n")
    if any(stripped.startswith(m) for m in MARKERS):
        moved.append(stripped)
    else:
        out.append(line)

assert len(moved) == 4, "expected 4 entries, got %d" % len(moved)
# pointer goes where the first moved entry was; simplest: append pointer at end (entries were tail-adjacent)
codely_new = "".join(out)
if not codely_new.endswith("\n"):
    codely_new += "\n"
codely_new += POINTER + "\n"

with io.open(ARCHIVE, "r", encoding="utf-8") as f:
    arch = f.read()
arch_new = arch + SECTION_HEADER + "\n".join(moved) + ("\n" if not arch.endswith("\n") else "\n")

# zero-loss assertions
for m in moved:
    assert m in arch_new, "verbatim missing in archive: %s..." % m[:60]
    assert m not in codely_new, "leftover in CODELY: %s..." % m[:60]

with io.open(CODELY, "w", encoding="utf-8", newline="") as f:
    f.write(codely_new)
with io.open(ARCHIVE, "a", encoding="utf-8", newline="") as f:
    pass  # already rewritten below
with io.open(ARCHIVE, "w", encoding="utf-8", newline="") as f:
    f.write(arch_new)

print("moved=%d" % len(moved))
print("all verbatim in archive: PASS")
print("all removed from CODELY: PASS")
