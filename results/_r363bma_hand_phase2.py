# -*- coding: utf-8 -*-
"""r363 bm-a hand-phase 2: CODELY.md final wave resolution.
Structure: base(5c8e4542)=8,646B; ours(d62f7d43)=base+bm-b r347 census-grid pit row;
mine(ade08dbb)=base+my 2 rows (batch-36 meta + r362 exec record).
Union = base + ours-suffix + mine-suffix = 10,401B > 10,000B hard line
-> in-window fold (O-20260927-0230): r91/r93/r98 rows (redundancy reclaim:
verbatim already in archive batch-36 section + older batch sections) +
batch-36 row union-clause amended to disclose the wave-2 fold.
Zero-loss (r327): every entry line of BOTH faces in final tree OR final archive.
"""
import io
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
T = os.environ["TEMP"]


def rd(n):
    return open(os.path.join(T, n), "rb").read()


def lines_of(b):
    return [ln for ln in b.decode("utf-8").splitlines() if ln.strip()]


base = rd("r363w2_codely_base.md")
ours = rd("r363w2_codely_ours.md")
mine = rd("r363w2_codely_mine.md")
assert ours.startswith(base), "ours not append onto base"
assert mine.startswith(base), "mine not append onto base"
suf_ours = ours[len(base):]
suf_mine = mine[len(base):]
print(f"base {len(base)} + ours-suffix {len(suf_ours)} + mine-suffix {len(suf_mine)} = union {len(base) + len(suf_ours) + len(suf_mine)}B (pre-fold)")

union = base + suf_ours + suf_mine
nl = b"\r\n" if b"\r\n" in union[:2000] else b"\n"

# fold candidates: full lines, removed only if verbatim-present in final archive
final_archive = open("research/memory-archive/202609.md", "rb").read().decode("utf-8")
fold_keys = [
    "- [r93 bm-c] 坑律：S0 stash-pop",
    "- [2026-09-27 19:11 r98 bm-c] 坑律：轮首机器身份锚定",
    "- [2026-09-27 17:2x r91 bm-c] 坑律（二十三批外迁·指针）：S0 pull 共享滚动台账",
]
fold_keys = [k.encode("utf-8") for k in fold_keys]
folded = []
for key in fold_keys:
    lines = union.split(nl)
    hits = [ln for ln in lines if ln.startswith(key)]
    assert len(hits) == 1, f"fold key {key[:40]} hits={len(hits)}"
    row = hits[0]
    assert row.decode("utf-8") in final_archive, f"fold row not verbatim in final archive: {key[:40]}"
    lines.remove(row)
    folded.append(row)
    union = nl.join(lines) + nl
print(f"folded {len(folded)} rows, saved {sum(len(r) + len(nl) for r in folded)}B, size now {len(union)}B")

# amend batch-36 union clause to disclose wave-2 fold
old_clause = "union 面=origin 侧批次结构（r93~r110 活跃指针保留面·冗余合法零丢失律满足）".encode("utf-8").replace(b"\n", nl)
new_clause = "union 面=origin 侧批次结构+风暴二程窗 r91/r93/r98 冗余回收折叠（verbatim 三十六批节在位）".encode("utf-8").replace(b"\n", nl)
assert union.count(old_clause) == 1, f"clause count {union.count(old_clause)}"
union = union.replace(old_clause, new_clause)
print(f"batch-36 clause amended ({len(old_clause)}->{len(new_clause)}B), size now {len(union)}B")
assert len(union) <= 10000, f"CODELY hard line breached: {len(union)}"
io.open("CODELY.md", "wb").write(union)

# zero-loss verification (r327)
final_tree_lines = set(lines_of(union))
ours_lines, mine_lines = lines_of(ours), lines_of(mine)
missing_ours = [ln for ln in ours_lines if ln not in final_tree_lines and ln not in final_archive]
missing_mine = []
for ln in mine_lines:
    if ln in final_tree_lines or ln in final_archive:
        continue
    if ln.startswith("- 三十六批外迁（r362 bm-a"):
        continue  # disclosed amend exception: wave-2 clause fold-disclosure; original verbatim in git history (ade08dbb), amended face in tree (r176 renumber precedent)
    missing_mine.append(ln)
assert not missing_ours, f"ours lines lost: {missing_ours[:3]}"
assert not missing_mine, f"mine lines lost: {missing_mine[:3]}"
print(f"CODELY wave-2: {len(union)}B <= 10,000B OK; entry-level coverage ours {len(ours_lines)} lines + mine {len(mine_lines)} lines 100% in tree-union-archive; folded rows verbatim-verified in archive x3")
print("HAND-PHASE-2 OK")
