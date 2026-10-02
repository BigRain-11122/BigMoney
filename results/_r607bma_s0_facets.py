"""r607 bm-a S0 faceted checkout: post pure-FF reset --mixed, classify M/D rows.

Law refs: r585 (pure FF + faceted checkout), r595 (D-row restore, no blind add),
r570/r600 (pool_core_samples union in bytes space), r380 (no whole-output strip).
Discriminator: working-tree blob vs old-HEAD(8a76ca653) blob — equal means the
"M" state is purely origin's advance (stale local, take origin); different
means a local daemon wrote it (keep local if bm-a-owned/hosted, union if
shared append-only).
"""
import subprocess, sys, os

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
OLD_HEAD = "8a76ca653"  # pre-FF local head (r606 bm-a)

def git(*args, **kw):
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True)
    return r.returncode, r.stdout, r.stderr

# 1) porcelain, per-line processing (r380: no whole-output strip)
rc, out, err = git("status", "--porcelain")
if rc != 0:
    print("FAIL status rc", rc, err.decode("utf-8", "replace")); sys.exit(1)
lines = out.decode("utf-8", "replace").splitlines()
d_restore, m_rows, other = [], [], []
for ln in lines:
    if not ln.strip():
        continue
    xy, path = ln[:2], ln[3:]
    if "D" in xy:
        d_restore.append((xy, path))
    elif "M" in xy:
        m_rows.append((xy, path))
    else:
        other.append((xy, path))

print(f"rows: D={len(d_restore)} M={len(m_rows)} other={len(other)}")
for xy, p in other:
    print(f"OTHER {xy} {p}")

# 2) restore D rows (origin additions missing on disk = post-reset artifact)
if d_restore:
    paths = [p for _, p in d_restore]
    rc, out, err = git("checkout", "--", *paths)
    print("checkout D rows:", "OK" if rc == 0 else f"FAIL {err.decode('utf-8','replace')}")
    if rc != 0:
        sys.exit(1)
    for _, p in d_restore:
        print(f"  restored {p}")

# 3) classify M rows by blob comparison vs old HEAD
keep_local, take_origin, investigate = [], [], []
for _, path in m_rows:
    # working tree blob
    wt = open(os.path.join(REPO, path), "rb").read() if os.path.exists(os.path.join(REPO, path)) else None
    rc2, o2, e2 = git("rev-parse", f"{OLD_HEAD}:{path}")
    old_sha = o2.decode().strip() if rc2 == 0 else None
    if old_sha is None:
        # not in old HEAD: origin-new file, local stale/absent -> take origin
        take_origin.append(path); continue
    rc3, o3, e3 = git("show", old_sha)
    old_blob = o3 if rc3 == 0 else None
    if wt == old_blob:
        take_origin.append(path)
    else:
        keep_local.append(path)

print("\nTAKE_ORIGIN (stale local, origin advanced):")
for p in take_origin: print(" ", p)
print("\nKEEP_LOCAL (local daemon write / bm-a owned):")
for p in keep_local: print(" ", p)

# 4) take origin for stale faces
if take_origin:
    rc, out, err = git("checkout", "--", *take_origin)
    print("\ntake_origin checkout:", "OK" if rc == 0 else f"FAIL {err.decode('utf-8','replace')}")
    if rc != 0: sys.exit(1)

# 5) shared append-only faces with local writes -> union (bytes space, r600)
APPEND_ONLY = ["results/pool_core_samples.jsonl", "results/x2_watch_log.jsonl"]
for path in APPEND_ONLY:
    if path in keep_local:
        keep_local.remove(path)
        rc4, o4, e4 = git("show", f"origin/main:{path}")
        origin_blob = o4  # bytes
        # blob EOL probe (r600/r373)
        crlf = origin_blob.count(b"\r\n"); lf = origin_blob.count(b"\n")
        eol = b"\r\n" if crlf * 2 > lf else b"\n"
        # normalize both sides to line sets (rstrip trailing \r)
        olines = [l.rstrip(b"\r") for l in origin_blob.split(b"\n") if l.strip()]
        with open(os.path.join(REPO, path), "rb") as f:
            wt = f.read()
        wlines = [l.rstrip(b"\r") for l in wt.split(b"\n") if l.strip()]
        oset = set(olines); local_only = [l for l in wlines if l not in oset]
        # sanity: all lines must be valid json dicts (r570 type gate)
        import json as _json
        bad = []
        for l in olines + local_only:
            try:
                obj = _json.loads(l.decode("utf-8", "replace"))
                if not isinstance(obj, dict):
                    bad.append(l[:60])
            except Exception:
                bad.append(l[:60])
        if bad:
            print(f"UNION ABORT {path}: non-dict/parse-fail lines {len(bad)}"); sys.exit(1)
        merged = olines + local_only
        data = eol.join(merged) + eol
        with open(os.path.join(REPO, path), "wb") as f:
            f.write(data)
        print(f"UNION {path}: origin={len(olines)} local_only={len(local_only)} merged={len(merged)} eol={'CRLF' if eol==b'\r\n' else 'LF'}")

print("\nKEEP_LOCAL final (rides next batched commit):")
for p in keep_local: print(" ", p)
print("\nDONE")
