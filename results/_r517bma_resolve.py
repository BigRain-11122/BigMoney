# r517 bm-a: resolve pool_core_samples.jsonl UU from crashed r516 rebase (pick 95cff39e7 onto e84755867)
# Recipe: append-log line-level union (r188) -- :2: (origin side) full + :3: (pick side) lines not in :2:
# Zero-loss assertion: every line of both blobs present in result. Parse-verify all lines (r185).
import subprocess, sys, json

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
PATH = "results/pool_core_samples.jsonl"

def blob(spec):
    return subprocess.check_output(["git", "-C", REPO, "show", spec], )  # raw bytes, no PS pipe (r292)

b2 = blob(f":2:{PATH}")  # origin side (e84755867)
b3 = blob(f":3:{PATH}")  # pick side (95cff39e7)

nl2 = b"\r\n" in b2
nl3 = b"\r\n" in b3
print("stage2 CRLF:", nl2, "stage3 CRLF:", nl3)
print("stage2 bytes:", len(b2), "lines:", len(b2.splitlines()))
print("stage3 bytes:", len(b3), "lines:", len(b3.splitlines()))

# line-level identity on normalized (strip CR) basis
l2 = [ln.rstrip(b"\r") for ln in b2.split(b"\n") if ln.rstrip(b"\r") != b""]
l3 = [ln.rstrip(b"\r") for ln in b3.split(b"\n") if ln.rstrip(b"\r") != b""]
set2 = set(l2)
suffix3 = [ln for ln in l3 if ln not in set2]  # :3:-only lines (dedup domain = suffix set, r294 domain law)
print("s2 lines:", len(l2), "s3 lines:", len(l3), "s3-only:", len(suffix3))

merged = l2 + suffix3
setm = set(merged)
# zero-loss check: every line of both blobs present
lost2 = [ln for ln in l2 if ln not in setm]
lost3 = [ln for ln in l3 if ln not in setm]
print("lost2:", len(lost2), "lost3:", len(lost3))
assert not lost2 and not lost3, "ZERO-LOSS FAILED"
# dedup sanity: result may legitimately contain duplicate lines (r294: id dup is legal multi-row state)
print("merged lines:", len(merged))

# parse-verify every line (r185)
for i, ln in enumerate(merged):
    obj = json.loads(ln.decode("utf-8"))
    assert "ts" in obj and "machine_id" in obj, f"line {i} missing keys"
print("parse-verify: all", len(merged), "lines valid JSON")

# trailing newline mirrors stage2 shape; use stage2's line ending (detect per-line)
# write back: preserve each original line's bytes; join with detected separator
sep = b"\r\n" if nl2 else b"\n"
out = sep.join(merged) + sep
p = REPO + "\\" + PATH.replace("/", "\\")
with open(p, "wb") as f:
    f.write(out)
print("written:", len(out), "bytes, sep CRLF" if nl2 else "sep LF")
