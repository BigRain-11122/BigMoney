"""r304 bm-c rebase conflict resolver v2 (line-based state machine).

Union ruling (r303 dual-fix precedent):
  - region 1 (marker test): take bm-a r504 head (equivalent predicate +
    their shared-face authority law below is strictly more complete).
  - region 2 (selftest 5d): union BOTH blocks; bm-c primary check renamed
    -bmc to avoid the name collision.
"""
import sys

P = "scripts/merge_lane_views.py"
lines = open(P, encoding="utf-8").read().split("\n")

regions, i = [], 0
while i < len(lines):
    if lines[i].startswith("<<<<<<< "):
        head, base, mine, st = [], [], [], 0
        i += 1
        while i < len(lines) and not lines[i].startswith(("|||||||", "=======", ">>>>>>> ")):
            head.append(lines[i]); i += 1
        if i < len(lines) and lines[i].startswith("|||||||"):
            st = 1; i += 1
            while i < len(lines) and not lines[i].startswith(">>>>>>> "):
                if lines[i].startswith("======="):
                    st = 2; i += 1; continue
                (mine if st == 2 else base).append(lines[i]); i += 1
        if i < len(lines) and lines[i].startswith(">>>>>>> "):
            i += 1
        regions.append((head, base, mine))
    else:
        i += 1

assert len(regions) == 2, f"expected 2 regions, got {len(regions)}"

out, pos, ri, skip = [], 0, 0, False
for idx, ln in enumerate(lines):
    if ln.startswith("<<<<<<< "):
        head, base, mine = regions[ri]
        if ri == 0:
            out.extend(head)
        else:
            mine_renamed = [l.replace('check("pool:park-marker-beats-stale-ready",',
                                      'check("pool:park-marker-beats-stale-ready-bmc",')
                            for l in mine]
            out.extend(head)
            out.append("")
            out.extend(mine_renamed)
        ri += 1
        # skip through the end marker line
        skip = True
        continue
    if skip:
        if ln.startswith(">>>>>>> "):
            skip = False
        continue
    out.append(ln)

resolved = "\n".join(out)
assert "<<<<<<<" not in resolved and ">>>>>>>" not in resolved, "markers remain"
assert "shared-face verdict kept" in resolved, "bm-a authority law lost"
assert "done-absorb shards" in resolved, "bm-c done-absorb fix lost"
assert "_union_shard_rows(sa, sb)" in resolved, "shard key-union lost"
assert "park-marker-beats-stale-ready-bmc" in resolved, "bm-c legs lost"
assert "park-authority-survives-multi-lane" in resolved, "bm-a legs lost"

open(P, "w", encoding="utf-8", newline="").write(resolved)
print("resolved: 2 regions union-ruled, both fixes verified present")
