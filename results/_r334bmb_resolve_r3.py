# -*- coding: utf-8 -*-
"""r334 bm-b round-3 resolver v2 (post self-inflicted staged-markers recovery).

v1 bug: drop-in-place None poisoned 2nd anchor scan -> crash before writes; the
follow-up `git add` staged marker-laden CODELY/archive. Stages now gone -> read
ours=HEAD:, theirs=6ab7aefb: directly (r90 empty-blob law: never fall back to
worktree for a UU face mid-recovery; fail-closed instead).
Laws: r176 renumber (mine 二十批->二十一, entries not in bm-a's kept), r89
stub-drop full-form anchoring, r185 byte-verify.
"""
import io
import subprocess


def rev_show(rev, path):
    b = subprocess.run(["git", "show", f"{rev}:{path}"],
                       capture_output=True).stdout
    assert b, f"fail-closed: empty blob {rev}:{path} (no worktree fallback)"
    return b.decode("utf-8")


CODY, ARCH = "CODELY.md", "research/memory-archive/202609.md"  # git paths: forward slashes
oc = rev_show("HEAD", CODY)
tc = rev_show("6ab7aefb", CODY)
oa = rev_show("HEAD", ARCH)
ol = oc.splitlines()

DROP_ANCHORS = [
    "- [2026-09-27 16:2x r335 bm-a] 坑律：**PowerShell ConvertFrom-Json",
    "- [2026-09-27 16:3x r333 bm-b] 坑律：**tick 的 git 危险窗",
]
idx = {}
for a in DROP_ANCHORS:                                   # scan ALL first (v1 bug)
    hits = [i for i, l in enumerate(ol) if l.startswith(a) and "坑律：**" in l]
    assert len(hits) == 1, f"anchor not exactly-once in ours: {a} -> {hits}"
    idx[a] = hits[0]
fulls = {a: ol[i] for a, i in idx.items()}
for i in idx.values():
    ol[i] = None                                         # drop after scans

PTR_335 = ("- [2026-09-27 16:2x r335 bm-a] 坑律（二十一批外迁·指针）：PowerShell ConvertFrom-Json "
           "假红/权威解析一律 python——全文 verbatim=research/memory-archive/202609.md"
           "『坑律归档 2026-09-27 二十一』节。")
PTR_333 = ("- [2026-09-27 16:3x r333 bm-b] 坑律（二十一批外迁·指针）：tick git 危险窗扩至 :X3 后"
           "（post-commit fetch+push 对账尾）——全文 verbatim=research/memory-archive/202609.md"
           "『坑律归档 2026-09-27 二十一』节。")
for p in (PTR_335, PTR_333):
    assert p not in ol
    ol.append(p)

r334 = [l for l in tc.splitlines() if l.startswith("- [2026-09-27 17:3x r334 bm-b]")]
assert len(r334) == 1, f"r334 entry not exactly-once in mine: {len(r334)}"
assert r334[0] not in ol
ol.append(r334[0])

ol = [l for l in ol if l is not None]
new_c = "\n".join(ol) + "\n"
assert "<<<<<<<" not in new_c and ">>>>>>>" not in new_c, "markers leaked"
with io.open(CODY, "w", encoding="utf-8", newline="") as f:
    f.write(new_c)
cb = len(new_c.encode("utf-8"))
print(f"CODELY: -> {cb}B (<=10240: {cb <= 10240})")
assert cb <= 10240

SEC21_HDR = ("## 坑律归档 2026-09-27 二十一（r334 bm-b·水位律当窗整编·行级零丢失·r176 让号律："
             "bm-a 二十批同窗先落，本节自二十批重编；r332 bm-b/r89 bm-c 两目已由 bm-a 二十批节收录不重复）")
my_section = SEC21_HDR + "\n" + fulls[DROP_ANCHORS[0]] + "\n" + fulls[DROP_ANCHORS[1]] + "\n"
# archive prose legitimately quotes marker syntax (7 long-standing hits, r113/R133/
# r176/r235/R293/R294 lessons); assert only: ours preserved verbatim + my tail has no
# REAL conflict-form lines (line-anchored delimiters, not substring)
for ml in my_section.splitlines():
    assert not (ml.startswith("<<<<<<<") or ml.startswith(">>>>>>>")
                or ml.strip() == "======="), f"real conflict form in my tail: {ml[:60]}"
new_a = oa.rstrip("\n") + "\n\n" + my_section
assert new_a.startswith(oa.rstrip("\n")), "ours archive prefix not preserved"
with io.open(ARCH, "w", encoding="utf-8", newline="") as f:
    f.write(new_a)

a2 = io.open(ARCH, encoding="utf-8").read()
c2 = io.open(CODY, encoding="utf-8").read()
for a in DROP_ANCHORS:
    assert fulls[a] in a2, f"verbatim lost in archive: {a[:40]}"
    assert fulls[a] not in c2, f"full still in CODELY: {a[:40]}"
assert SEC21_HDR in a2 and "## 坑律归档 2026-09-27 二十批" in a2
assert r334[0] in c2 and "二十一" in c2
for probe in ("r332 bm-b] 坑律：**tick 自提交落点", "r89 bm-c] 坑律：**stub-drop",
              "r335 bm-a] 坑律：**PowerShell", "r333 bm-b] 坑律：**tick 的 git 危险窗"):
    assert probe in a2, f"originally-archived entry missing: {probe[:40]}"
print(f"ARCHIVE: -> {len(a2.encode('utf-8'))}B (+21st section, 2 entries, 4/4 findable)")
print("R3-CODELY-ARCHIVE-OK")
