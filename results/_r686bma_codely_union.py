import subprocess, sys, os
# r479 canon: CODELY append-only union = origin full text + my truly-new lines appended in order
# with byte-containment filter (my line substring of origin line = drop, avoid dup-variant)
repo = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
path = "CODELY.md"

def show(ref):
    r = subprocess.run(["git", "-C", repo, "show", f"{ref}:{path}"], capture_output=True)
    assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')
    return r.stdout  # bytes

ours = show("HEAD")     # bm-a r685 side
theirs = show("origin/main")  # r483 bm-c side

ours_lines = ours.split(b"\n")
theirs_lines_set = set(theirs.split(b"\n"))
theirs_blob = theirs

# find lines in ours that origin lacks entirely (truly new)
missing = []
origin_line_starts = set()
for ln in theirs.split(b"\n"):
    origin_line_starts.add(ln.strip())

for ln in ours_lines:
    s = ln.strip()
    if not s:
        continue
    if ln in theirs_lines_set:
        continue
    if s in origin_line_starts:
        continue  # same content, whitespace-normalized present in origin
    # byte-containment filter: my line is a substring of the origin blob (defect variant of an origin line)
    if ln in theirs_blob:
        continue
    missing.append(ln)

print("missing lines (ours not in origin):", len(missing))
for m in missing[:10]:
    print("  -", m[:120])

# union = origin full text + missing lines appended at the tail (after origin's tail content, before final blank)
out = theirs
if missing:
    # ensure origin ends with newline structure
    if not out.endswith(b"\n"):
        out += b"\n"
    # detect if origin ends with blank lines; append a separator blank line then our lines
    out += b"\n"
    for m in missing:
        out += m + b"\n"

with open(os.path.join(repo, path), "wb") as f:
    f.write(out)

# self-verify: origin prefix identity
assert out.startswith(theirs[:len(theirs)]), "origin prefix identity FAILED"
# marker count check (line-start, not substring)
import re
def marker_count(blob, marker):
    cnt = 0
    for ln in blob.split(b"\n"):
        if ln.startswith(marker.encode()):
            cnt += 1
    return cnt
for mk in ["<<<<<<<", "=======", ">>>>>>>"]:
    c = marker_count(out, mk)
    assert c == 0, f"marker {mk} count={c} nonzero"
print("origin prefix identity: OK")
print("marker zero: OK")
print("union bytes:", len(out), " origin bytes:", len(theirs), " ours bytes:", len(ours))
