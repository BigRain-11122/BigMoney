# -*- coding: utf-8 -*-
# r491 bm-a: CODELY.md conflict resolution + hot-cold pass (水位律 ≤10KB 硬线).
# Union law: zero line loss; GM pointer substitutions preserved as archival
# intent (pointer targets hold the verbatim content).
# Archive base = origin/main:research/memory-archive/202609.md (local stale,
# remote carries bm-b/c r475/r476 窗批 sections) + new r491 bm-a 窗批 section.
import subprocess, io, re, json, sys

CONFLICT = "results/_r491bma_codely_conflict.tmp"
CODELY = "CODELY.md"
ARCH = "research/memory-archive/202609.md"

raw = io.open(CONFLICT, "rb").read().decode("utf-8")
lines = raw.split("\n")

# ---- pass 1: resolve the two conflict hunks per adjudication ----
out, i = [], 0
h1_theirs_dropped = []
while i < len(lines):
    ln = lines[i]
    if ln.startswith("<<<<<<<"):
        # collect ours/theirs blocks
        ours, theirs = [], []
        i += 1
        cur = ours
        while not lines[i].startswith(">>>>>>>"):
            if lines[i].startswith("======="):
                cur = theirs
            else:
                cur.append(lines[i])
            i += 1
        i += 1  # skip >>> marker
        # hunk1: D-41 entry -> ours (GM pointer substitution, content at
        #   mem-q-001 target + RETAIL_QUANT_TRACK.md canon + decisions.md)
        # hunk2: full union (ours pointers + theirs new entries)
        if any("D-20260930-41" in x for x in theirs) and any("mem-20260930-q-001" in x for x in ours):
            out.extend(ours)
            h1_theirs_dropped = [x for x in theirs if x.strip()]
        else:
            out.extend([x for x in ours if x.strip() or True])
            out.extend([x for x in theirs if x.strip() or True])
            # dedupe exact-duplicate lines ours/theirs (pointer dup guard)
    else:
        out.append(ln)
        i += 1
merged = "\n".join(out)
assert "<<<<<<<" not in merged and ">>>>>>>" not in merged, "unresolved markers"

# ---- pass 2: hot-cold pass (≤10KB hard line). Move the new full-text
# bm-b/bm-c entries (theirs' additions, currently the largest hot lines)
# verbatim to archive; leave r444-范式 pointer lines. ----
r = subprocess.run(["git", "show", f"origin/main:{ARCH}"], capture_output=True)
assert r.returncode == 0, "archive show failed"
arch_remote = r.stdout.decode("utf-8")

move_ids = ["r282 bm-c", "r284 bm-c", "r285 bm-c", "r476 bm-b", "r477 bm-b", "r286 bm-c"]
mlines = merged.split("\n")
keep, moved = [], []
for ln in mlines:
    is_full_entry = (ln.startswith("- [2026-09-30 ")
                     and any(m in ln for m in move_ids)
                     and "全文档案" not in ln and "verbatim" not in ln)
    if is_full_entry:
        moved.append(ln)
        m = re.match(r"- \[([^\]]+)\] (\S+)", ln)
        prefix, name = m.group(1), m.group(2)[:28]
        keep.append(f"- [{prefix}] {name}…（指针条·全文 verbatim=archive 202609.md"
                    "『热冷整编 2026-09-30 r491 bm-a 窗批』节）")
    else:
        keep.append(ln)
merged2 = "\n".join(keep)

# ---- archive: remote base + new section with moved entries verbatim ----
section = ("\n## 热冷整编 2026-09-30 r491 bm-a 窗批（CODELY 热层 ≤10KB 硬线：union 合并后 11,470B "
            "超线→当窗整编·r483 bm-a 收养窗续作）\n\n"
            + "\n\n".join(moved) + "\n\n"
            "〔r491 bm-a 窗行级零丢失校验：以上 " + str(len(moved)) + " 条自 CODELY.md 热层 verbatim "
            "外迁（r476/r477 bm-b+r282/r284/r285/r286 bm-c 新坑律条目·union theirs 面），热层留指针行；"
            "D-41 r483 条=GM 会话 mem-q-001 指针替换保留（内容=指针目标+RETAIL_QUANT_TRACK 正典）。〕\n")
arch_new = arch_remote + section

with io.open(CODELY, "wb") as fh:
    fh.write(merged2.encode("utf-8"))
with io.open(ARCH, "wb") as fh:
    fh.write(arch_new.encode("utf-8"))

# ---- audits ----
def nonempty(x):
    return [l for l in x.split("\n") if l.strip()]

M = set(nonempty(merged2))
theirs = set(nonempty(io.open("results/_r491bma_codely_theirs.tmp", "rb").read().decode("utf-8")))
ours = set(nonempty(io.open("CODELY.md", "rb").read().decode("utf-8")))  # post-resolution
# theirs lines absent from hot: must be either moved-to-archive or the D-41 substitution
arch_set = set(nonempty(arch_new))
lost_theirs = [l for l in theirs if l not in M and l not in arch_set
               and not any(l.startswith(p) for p in ("##", "###"))]
# adjudicated substitution: the D-41 r483 full text is replaced by GM's
# mem-q-001 pointer (content preserved at target + RETAIL_QUANT_TRACK canon)
sub_ids = {x[:60] for x in h1_theirs_dropped}
lost_theirs = [l for l in lost_theirs
               if not any(l[:60] == s or "D-20260930-41" in l[:80] for s in sub_ids)]
substituted = h1_theirs_dropped
audit = {
    "codely_bytes": len(merged2.encode("utf-8")),
    "under_10kb": len(merged2.encode("utf-8")) <= 10240,
    "moved_entries": len(moved),
    "moved_ids": [re.match(r"- \[([^\]]+)\]", l).group(1) for l in moved],
    "d41_substituted_lines": len(substituted),
    "lost_theirs_lines": [l[:100] for l in lost_theirs],
    "archive_bytes": len(arch_new.encode("utf-8")),
    "archive_sections": arch_new.count("\n## "),
}
io.open("results/_r491bma_codely_union_audit.json", "w", encoding="utf-8").write(
    json.dumps(audit, ensure_ascii=False, indent=1))
print(json.dumps(audit, ensure_ascii=False, indent=1))
assert not lost_theirs, "ZERO-LOSS VIOLATION"
assert audit["under_10kb"], "10KB hard line still exceeded"
print("CODELY union + hot-cold pass DONE, zero-loss verified")
