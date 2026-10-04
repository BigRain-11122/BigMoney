"""r709 bm-a rebase-window resolver: results/pool_core_samples.jsonl (append-log UU)

Law chain: r188/r217 line-level union zero-loss + r707bmb residual-tolerance
(final residual set MUST be subset of source residual set; residual lines preserved
verbatim) + r223/r234 EOL-mirror-base (base is LF) + r185 parse-verify before add.
Rebase 3-stage semantics per r351: :2:=origin side, :3:=local(replay) side.
"""
import subprocess, json, sys

PATH = "results/pool_core_samples.jsonl"

def blob(rev):
    r = subprocess.run(["git", "show", rev], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"git show {rev} failed: {r.stderr[:200]!r}")
    return r.stdout

base_b = blob(f":1:{PATH}")
s2_b = blob(f":2:{PATH}")   # origin side
s3_b = blob(f":3:{PATH}")   # local/replay side

def lns(b):
    return [l for l in b.decode("utf-8").splitlines() if l.strip()]

def resid(lines):
    bad = []
    for l in lines:
        try:
            json.loads(l)
        except Exception:
            bad.append(l)
    return bad

L_base, L2, L3 = lns(base_b), lns(s2_b), lns(s3_b)
src_resid = set(resid(L_base)) | set(resid(L2)) | set(resid(L3))
set2, set3 = set(L2), set(L3)
union_set = set2 | set3

# ts-ascending check on each source; union re-sorted by embedded ts only if both sources sorted
def ts_of(l):
    return json.loads(l).get("ts", "")
def is_sorted(L):
    tss = [ts_of(l) for l in L]
    return tss == sorted(tss)
if is_sorted(L2) and is_sorted(L3):
    out_lines = sorted(union_set, key=ts_of)
    mode = "ts-sorted"
else:
    # preserve base order, then origin-only additions, then local-only additions
    base_order = [l for l in L_base]
    seen = set(base_order)
    for l in L2:
        if l not in seen:
            base_order.append(l); seen.add(l)
    for l in L3:
        if l not in seen:
            base_order.append(l); seen.add(l)
    out_lines = base_order
    mode = "encounter-order"

payload = ("\n".join(out_lines) + "\n").encode("utf-8")  # LF mirror base (base ends LF, LF-only)

# === assertions before write (r185) ===
assert len(out_lines) == len(union_set), "dup lines after union"
assert len(union_set) == len(set2) + len(set3) - len(set2 & set3), "union cardinality"
assert set(out_lines) >= set2, "origin-side loss"
assert set(out_lines) >= set3, "local-side loss"
final_resid = resid(out_lines)
assert set(final_resid) <= src_resid, f"new residual lines appeared: {set(final_resid)-src_resid}"
for l in out_lines:
    json.loads(l)  # every kept line parseable (all sources were clean, so this holds)

with open(PATH, "wb") as f:
    f.write(payload)

# post-write readback verify
rb = open(PATH, "rb").read()
rb_lines = lns(rb)
assert set(rb_lines) == union_set, "readback mismatch"
assert rb.endswith(b"\n") and b"\r\n" not in rb, "EOL violation (LF-only expected)"

print(json.dumps({
    "receipt": "r709 bm-a rebase resolver pool_core_samples.jsonl",
    "mode": mode,
    "base_lines": len(L_base),
    "origin_side_s2": len(L2),
    "local_side_s3": len(L3),
    "union_lines": len(out_lines),
    "origin_only": sorted(set2 - set3),
    "local_only": len(set3 - set2),
    "src_residual": len(src_resid),
    "final_residual": len(final_resid),
    "zero_loss": True,
}, ensure_ascii=False, indent=1))
