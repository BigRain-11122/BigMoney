# -*- coding: utf-8 -*-
"""bm-a r595 S0 pure-FF integration (dead-session estate adoption window).
Laws: r593 (execution-time rev-parse), r578 (update-ref then reset --mixed + per-face checkout),
r585/r580 (union the two dual-side files), r373 (blob-space union, disk EOL), r530 (bytes in/out).
"""
import json, subprocess, sys

def git(*a, binary=False):
    r = subprocess.run(["git"] + list(a), capture_output=True)
    if binary:
        return r.returncode, r.stdout, r.stderr
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")

rc, out, err = git("fetch", "origin")
assert rc == 0, err
rc, old, _ = git("rev-parse", "HEAD")
rc, new, _ = git("rev-parse", "origin/main")
old, new = old.strip(), new.strip()
if old == new:
    print("ALREADY-INTEGRATED", old[:9])
    sys.exit(0)
rc, mb, _ = git("merge-base", old, new)
assert mb.strip() == old, "NOT-FF: abort (need surgical path)"
print("FF", old[:9], "->", new[:9])

# 1. CAS update-ref (execution-time value, r593 law)
rc, _, err = git("update-ref", "refs/heads/main", new, old)
assert rc == 0, err
# 2. reset --mixed re-anchors index, keeps working tree (r578 law)
rc, _, err = git("reset", "--mixed", new)
assert rc == 0, err

# 3. per-face checkout: every incoming file EXCEPT the two union faces
UNION = {"CODELY.md", "fleet/tasks/T-2026-10-02-145-P1.json"}
rc, out, _ = git("diff", "--name-only", "-z", old, new)
targets = [f for f in out.split("\0") if f and f not in UNION]
if targets:
    rc, _, err = git("checkout", "--", *targets)
    assert rc == 0, err
print("checkout origin-verbatim:", len(targets), "faces")

# 4. union CODELY.md: origin blob + my local tail additions (r585 law)
_, old_blob, _ = git("show", f"{old}:CODELY.md", binary=True)
_, new_blob, _ = git("show", f"{new}:CODELY.md", binary=True)
local = open("CODELY.md", "rb").read()
lb, ob = local.replace(b"\r\n", b"\n"), old_blob.replace(b"\r\n", b"\n")
assert lb.startswith(ob), "CODELY local not a superset of old blob - ABORT"
mine = lb[len(ob):]
nb = new_blob.replace(b"\r\n", b"\n")
assert nb.startswith(ob), "origin CODELY not a superset of old blob - ABORT"
merged = nb + mine
open("CODELY.md", "wb").write(merged.replace(b"\n", b"\r\n"))
print("CODELY union: origin", len(nb), "+ mine", len(mine), "bytes")

# 5. union T-145 ticket: local (base+my3keys) + origin's new keys (r571 key-level union)
tp = "fleet/tasks/T-2026-10-02-145-P1.json"
_, tk_old, _ = git("show", f"{old}:{tp}", binary=True)
_, tk_new, _ = git("show", f"{new}:{tp}", binary=True)
tk_loc = open(tp, "rb").read()
j_old = json.loads(tk_old.decode("utf-8"))
j_new = json.loads(tk_new.decode("utf-8"))
j_loc = json.loads(tk_loc.decode("utf-8"))
added_local = {k: v for k, v in j_loc.items() if k not in j_old}
added_origin = {k: v for k, v in j_new.items() if k not in j_old}
for k, v in added_origin.items():
    if k in j_loc:
        assert j_loc[k] == v, f"conflicting value on key {k}"
    j_loc[k] = v
merged_tk = json.dumps(j_loc, ensure_ascii=False, indent=1).encode("utf-8")
open(tp, "wb").write(merged_tk)
print("T-145 union: local keys", sorted(added_local), "+ origin keys", sorted(added_origin))

# 6. verify
rc, out, _ = git("rev-parse", "HEAD")
assert out.strip() == new, "HEAD not moved"
rc, st, _ = git("status", "--porcelain")
print("--- post-FF status (kept-dirty faces) ---")
print(st)
print("FF-OK")
