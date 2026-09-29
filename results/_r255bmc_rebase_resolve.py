# -*- coding: utf-8 -*-
# r255 bm-c rebase conflict resolver (idempotent per r457 law):
# - CODELY.md: dual hot-cold reorg collision (bm-a r459 window batch-2
#   vs my r255 window batch) -> keep HEAD (origin/bm-a) side per
#   later-yields commit-order law: bm-a r458 pointer + new fill_ladder
#   pit + r446 verbatim stays-hot (explicit W13-adopter binding) +
#   r252 pointer. My duplicate r458/r446 pointers and my r252 verbatim
#   drop (verbatim preserved in BOTH archive sections = zero loss).
# - research/memory-archive/202609.md: both-add append collision ->
#   UNION: keep bm-a's 'r459 bm-a window batch two' section AND my
#   'r255 bm-c window batch' section (both hold verbatim entries).
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def resolve(path, mode):
    text = io.open(path, encoding="utf-8").read()
    if "<<<<<<<" not in text:
        print(path, ": no markers, skip (idempotent)")
        return
    pat = re.compile(
        r"<<<<<<< HEAD\r?\n(.*?)\|\|\|\|\|\|\|.*?\r?\n(.*?)=======\r?\n(.*?)>>>>>>> [^\n]*\r?\n?",
        re.S,
    )

    def repl(m):
        head, mine = m.group(1), m.group(3)
        if mode == "head":
            return head
        if mode == "union":
            return head + mine
        raise AssertionError(mode)

    out, n = pat.subn(repl, text)
    left = [ln for ln in out.splitlines()
            if ln.startswith(("<<<<<<<", ">>>>>>>", "|||||||"))
            or ln.rstrip() == "======="]
    assert not left, f"unresolved markers remain: {left[:3]}"
    io.open(path, "w", encoding="utf-8", newline="").write(out)
    print(path, ": resolved", n, "hunk(s) mode=", mode)


resolve("CODELY.md", "head")
resolve("research/memory-archive/202609.md", "union")

# zero-loss assertions
codely = io.open("CODELY.md", encoding="utf-8").read()
arch = io.open("research/memory-archive/202609.md", encoding="utf-8").read()
assert "fill_ladder" in codely, "bm-a new pit law lost from hot"
assert "泊位族选双面核验坑" in codely, "r458 law lost from hot"
assert "手术过继残漏三连坑" in codely, "r446 law lost from hot"
assert "inbox 零未读腿坑" in codely, "r252 law lost from hot"
assert "stale-tree" in codely, "my new pit lost"
assert "实战出真知" in codely, "user meta-law lost"
assert "热冷整编 2026-09-30 r255 bm-c 窗批" in arch, "my archive section lost"
assert "热冷整编 2026-09-30 r459 bm-a 窗批二" in arch.replace(" ", "") or \
    "r459 bm-a 窗批二" in arch, "bm-a archive section lost"
print("ALL ASSERTIONS PASS; CODELY bytes:", len(codely.encode("utf-8")))
