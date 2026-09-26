"""r268 bm-a resolver fix-up (v1 line-set union collapsed structural blank lines and
re-inserted my own archived morning batch into hot; this v2 does section-tail append).

Archive: both sides share the r273-committed base (common prefix 648 lines); :2 tail =
bm-b r274 block (4 lines, contains the 20:46 Project line they archived); :3 tail =
my r268 block (29 lines, 26 morning entries + header). Correct merge = prefix + A-tail
+ B-tail (chronological). Multiplicity-verified zero loss.

CODELY.md: base = :3 (my recompiled hot face) - 20:46 line (preserved in their cold
block) + their single new pit-law entry (A-only minus my 26 archived lines).
"""
import subprocess, sys, re

def blob(s, p):
    r = subprocess.run(["git", "show", f":{s}:{p}"], capture_output=True)
    if r.returncode != 0: sys.exit(f"blob fail {s}:{p}")
    return r.stdout.decode("utf-8")

def die(m):
    print("FIXUP-DIE:", m); sys.exit(1)

# ---------- archive: prefix + both tails ----------
arc_a = blob(2, "research/memory-archive/202609.md").split("\n")
arc_b = blob(3, "research/memory-archive/202609.md").split("\n")
i = 0
while i < min(len(arc_a), len(arc_b)) and arc_a[i] == arc_b[i]: i += 1
prefix, a_tail, b_tail = arc_a[:i], arc_a[i:], arc_b[i:]
final = prefix + a_tail + b_tail
txt = "\n".join(final)
# multiplicity zero-loss: every raw line of both parents present with >= same count
from collections import Counter
fa, fb, ff = Counter(arc_a), Counter(arc_b), Counter(final)
for L, c in list(fa.items()) + list(fb.items()):
    if ff[L] < c: die(f"archive multiplicity loss: {L[:50]!r} have {ff[L]} need {c}")
if not any("r274" in L[:30] for L in final): die("r274 block missing")
if not any("r268" in L[:30] for L in final): die("r268 block missing")
if not any("2026-09-26 20:46" in L[:40] for L in final): die("20:46 line lost from cold")
open("research/memory-archive/202609.md", "wb").write(txt.encode("utf-8"))
print(f"archive: prefix {len(prefix)} + A-tail {len(a_tail)} + B-tail {len(b_tail)} = {len(final)} lines")

# ---------- CODELY.md ----------
ca = blob(2, "CODELY.md").split("\n")
cb = blob(3, "CODELY.md").split("\n")
a_only = [L for L in ca if L not in cb]
pat = re.compile(r"\[2026-09-26 (09|1[0-4]):")
archived_mine = [L for L in a_only if pat.search(L[:40])]
new_theirs = [L for L in a_only if not pat.search(L[:40]) and L.strip()]
print(f"CODELY: a_only={len(a_only)} -> archived_mine={len(archived_mine)} new_theirs={len(new_theirs)}")
if len(archived_mine) != 26: die(f"expected 26 archived-mine lines, got {len(archived_mine)}")
if len(new_theirs) != 1: die(f"expected 1 new-theirs line, got {len(new_theirs)}: {[L[:50] for L in new_theirs]}")
# verify my 26 archived lines exist in merged cold (my r268 block)
cold_txt = txt
for L in archived_mine:
    if L not in cold_txt: die(f"my archived line missing from cold: {L[:50]}")
drop2046 = [L for L in cb if "2026-09-26 20:46" in L[:40]]
if len(drop2046) != 1: die(f"20:46 line count in :3 = {len(drop2046)}")
out = [L for L in cb if L not in drop2046]
# insert their new entry after the last existing Reference-section entry (before EOF keeps list order stable)
insert_at = len(out)
for idx in range(len(out) - 1, -1, -1):
    if out[idx].strip().startswith("- [") or out[idx].strip().startswith("["):
        insert_at = idx + 1; break
for L in new_theirs:
    out.insert(insert_at, L); insert_at += 1
# multiset verification: out == cb - drop2046 + new_theirs
exp = [L for L in cb if L not in drop2046] + new_theirs
if sorted(out) != sorted(exp): die("CODELY multiset verification FAILED")
hot_b = ("\n".join(out)).encode("utf-8")
open("CODELY.md", "wb").write(hot_b)
size = len(hot_b)
if size > 51200: die(f"hot CODELY still over line: {size}")
# final content gates
final_txt = hot_b.decode("utf-8")
if "2026-09-26 20:46" in final_txt: die("20:46 line still in hot")
for L in archived_mine:
    if L in final_txt: die(f"archived line back in hot: {L[:50]}")
for L in new_theirs + [L for L in cb if "R268" in L[:30]]:
    if L not in final_txt: die(f"required line missing from hot: {L[:60]}")
print(f"CODELY.md: {len(cb)} -> {len(out)} lines, {size} bytes ({round(size/1024,1)} KiB) - under 50KiB line")
print("FIXUP COMPLETE")
