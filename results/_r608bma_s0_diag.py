# -*- coding: utf-8 -*-
# r608 S0 diagnose: classify porcelain rows for faceted restore (r595/r607 laws)
import subprocess, sys, io

def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout, r.stderr

rc, out, err = git(["status", "--porcelain"])
if rc != 0:
    print("STATUS FAIL", err); sys.exit(1)

d_rows, m_rows, other = [], [], []
for line in out.split("\n"):
    if not line.strip():
        continue
    xy = line[:2]
    path = line[3:]
    if "D" in xy:
        d_rows.append(path)
    elif "M" in xy:
        m_rows.append(path)
    else:
        other.append((xy, path))

print("=== D rows (%d) ===" % len(d_rows))
for p in d_rows: print("  D", p)
print("=== M rows (%d) ===" % len(m_rows))
for p in m_rows: print("  M", p)
print("=== other (%d) ===" % len(other))
for xy, p in other: print(" ", xy, p)

# shared-face line analysis: local vs HEAD blob (bytes space, r600 law)
def blob_lines(path):
    rc, o, e = git(["show", "HEAD:" + path])
    if rc != 0:
        return None, e.strip()
    return [l.rstrip(b"\r").decode("utf-8", "replace") for l in o.encode("latin-1", "replace").split(b"\n") if l.strip()] if False else None, None

for path in ["CODELY.md", "research/HANDOVER.md", "results/pool_core_samples.jsonl", "results/p1d_gates.json", "results/prospect_promotion/_summary.json"]:
    rc, o, e = git(["show", "HEAD:" + path])
    if rc != 0:
        print("HEAD-BLOB-FAIL", path, e.strip()[:120]); continue
    # blob is CRLF or LF; normalize per r600: strip trailing \r
    blob_ls = [l.rstrip(b"\r") for l in o.encode("utf-8", "surrogateescape").split(b"\n") if l.strip()]
    with open(path, "rb") as f:
        disk_ls = [l.rstrip(b"\r") for l in f.read().split(b"\n") if l.strip()]
    only_disk = [l for l in disk_ls if l not in set(blob_ls)]
    only_blob = [l for l in blob_ls if l not in set(disk_ls)]
    print("SHARED %s: blob_lines=%d disk_lines=%d only_disk=%d only_blob=%d" % (path, len(blob_ls), len(disk_ls), len(only_disk), len(only_blob)))
    for l in only_disk[:3]:
        print("   disk-only:", l[:150])
    for l in only_blob[:3]:
        print("   blob-only:", l[:150])
