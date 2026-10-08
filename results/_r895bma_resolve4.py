# r895 bm-a fix leg 2: pool_core_samples.jsonl was emptied by resolve3 (stage refs :2:/:3: died
# with the concluded rebase). Rebuild the canonical union from durable blobs:
#   stage2 (ours at conflict time) == d6c540f8c:POOL
#   stage3 (theirs)               == 2d87d21b:POOL
# Cross-check against the doubled 4386-line blob in dangling 79c7e7740 (pre-amend).
import json, subprocess, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
POOL = "results/pool_core_samples.jsonl"

def norm_lines(rev):
    raw = subprocess.run([GIT, "show", rev], capture_output=True).stdout
    out = []
    for l in raw.split(b"\n"):
        l = l.rstrip(b"\r")
        if l:
            out.append(l)
    return out

s2 = norm_lines("d6c540f8c:" + POOL)          # ours side at conflict (2190 expected)
s3 = norm_lines("2d87d21b:" + POOL)           # theirs side (2191 expected)
dup = norm_lines("79c7e7740:" + POOL)         # doubled blob from resolve1 bug (4386 expected)

seen, union = set(), []
for l in s2 + s3:
    if l not in seen:
        seen.add(l); union.append(l)

facts = {
    "s2_lines": len(s2), "s3_lines": len(s3), "dup_blob_lines": len(dup),
    "union_lines": len(union),
    "union_eq_set": len(union) == len(set(s2) | set(s3)),
    "union_matches_dup_blob_content": set(union) == set(dup),
    "dup_superset_of_sides": (set(s2) | set(s3)) <= set(dup),
}
if not facts["union_eq_set"] or not facts["union_matches_dup_blob_content"]:
    facts["verdict"] = "ASSERT_FAIL"
    print(json.dumps(facts))
    sys.exit(2)

for i, l in enumerate(union):
    try:
        json.loads(l.decode("utf-8").strip())
    except Exception as e:
        print(json.dumps({"verdict": "PARSE_FAIL", "line": i, "err": str(e)[:200]}))
        sys.exit(2)

with open(POOL, "wb") as f:
    f.write(b"\n".join(union) + b"\n")
facts["verdict"] = "POOL_REBUILD2_OK"
facts["bytes_out"] = len(b"\n".join(union) + b"\n")
print(json.dumps(facts))
