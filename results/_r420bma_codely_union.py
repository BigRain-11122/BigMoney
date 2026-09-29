# r420 bm-a CODELY.md memory-union resolver (r327/r329 entry-level law)
# theirs(:3:)=bm-c r204 water-level integrated version; ours(:2:)=base+1 entry (r419 九十一批)
# collision: theirs' new 九十一批/九十二批 vs ours' 九十一批 -> ours yields, renumber 91->93
import subprocess, sys

def blob(spec):
    return subprocess.run(["git", "show", spec], capture_output=True).stdout

theirs = blob(":3:CODELY.md").decode("utf-8")
ours = blob(":2:CODELY.md").decode("utf-8")
base = blob(":1:CODELY.md").decode("utf-8")
archive = blob("origin/main:research/memory-archive/202609.md").decode("utf-8")

# extract my single appended entry (ours suffix after base prefix)
assert ours.startswith(base), "ours must be base+suffix (prefix law)"
my_entry = ours[len(base):].lstrip("\n")
assert my_entry.startswith("- [2026-09-29 07:5x r419 bm-a] 坑律九十一批"), repr(my_entry[:60])

# renumber: 九十一批 -> 九十三批 (batch-71 yield law; theirs owns 91+92 on origin)
old_h = "坑律九十一批（merge-back 破活锁两步式"
new_h = "坑律九十三批（merge-back 破活锁两步式"
assert old_h in my_entry
my_entry_renum = my_entry.replace(old_h, new_h, 1)
assert "九十一批" not in my_entry_renum

final = theirs.rstrip("\n") + "\n\n" + my_entry_renum.strip() + "\n"
open("CODELY.md", "w", encoding="utf-8", newline="").write(final)

# ---- r327 bidirectional coverage verification ----
final_lines = set(l for l in final.splitlines() if l.strip())
base_lines = [l for l in base.splitlines() if l.strip()]
missing = []
for l in base_lines:
    if l in final_lines:
        continue
    # allow: archived (verbatim in archive), or pointer dedup/consolidation (its batches covered by final pointer lines)
    if l in archive:
        continue
    missing.append(l)
print("base lines not in final and not verbatim in archive (expect only deduped/repointed POINTER lines):")
for l in missing:
    print("  MISS:", l[:90])
print(f"sizes: base={len(base.encode())}B ours={len(ours.encode())}B theirs={len(theirs.encode())}B final={len(final.encode())}B (hard-line 10240B)")
print("final under 10KB hard line:", len(final.encode()) < 10240)
print("renumber entry present:", "坑律九十三批（merge-back 破活锁两步式" in final)
print("collision残留 91 dup:", final.count("坑律九十一批（"), "(expect 1 = bm-c r204's)")
