"""r453 bm-c CODELY dedup: remove exact-duplicate '- [' entries created by the
2nd-iter union concat (bm-b r655 lines existed on BOTH merge sides via the
first-iter union). Keep-first, zero-loss, assert-driven."""
import sys

P = "CODELY.md"
txt = open(P, encoding="utf-8", newline="").read()
lines = txt.split("\n")
seen = set()
out = []
removed = []
for l in lines:
    if l.startswith("- ["):
        if l in seen:
            removed.append(l[:60])
            continue
        seen.add(l)
    out.append(l)

assert len(removed) == 2, f"expected exactly 2 dups, got {len(removed)}: {removed}"
body = "\n".join(out)
assert body.count("r453 bm-c") == 1, "r453 line lost"
assert body.count("r656 bm-b") == 1, "r656 line lost"
assert body.count("r655 bm-b") == 2, "r655 lines must remain exactly 2 (one each)"
assert not any(l.startswith("<<<<<<<") or l.startswith(">>>>>>>") for l in out), "line-start markers present"
with open(P, "w", encoding="utf-8", newline="") as f:
    f.write(body)
print("DEDUP_OK removed=" + str(len(removed)))
for r in removed:
    print("REMOVED| " + r)
