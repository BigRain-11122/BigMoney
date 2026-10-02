"""r598 bm-b S0 pure-FF integration (r578/r585/r580 laws: reset --mixed + classified checkout via python subprocess argv)."""
import subprocess, json, sys

def git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout, r.stderr

# 1. capture my-dirty set (worktree-modified files before reset)
rc, out, err = git("status", "--porcelain")
assert rc == 0, err
my_dirty = set()
untracked = set()
for line in out.splitlines():
    if not line.strip():
        continue
    st, path = line[:2], line[3:]
    if st == "??":
        untracked.add(path)
    else:
        my_dirty.add(path)
print("my_dirty count:", len(my_dirty))

old_head = git("rev-parse", "HEAD")[1].strip()

# 2. fresh rev-parse at execution time (r593 law)
rc, new_head, err = git("rev-parse", "origin/main")
assert rc == 0, err
new_head = new_head.strip()

# 3. reset --mixed to origin (pure FF: old HEAD is ancestor)
rc, out, err = git("reset", "--mixed", new_head)
assert rc == 0, err
print("reset ->", new_head[:12])

# 4. delta files old..new
rc, out, err = git("diff", "--name-status", old_head, new_head)
assert rc == 0, err
delta = []
rename_pairs = []
for line in out.splitlines():
    parts = line.split("\t")
    if parts[0].startswith("R"):
        delta.append(parts[2])  # new path only exists in new tree
        rename_pairs.append((parts[1], parts[2]))
    else:
        delta.append(parts[-1])
print("delta files:", len(delta), "renames:", len(rename_pairs))

# rename old-path residue: after reset, old path is untracked dup in worktree -> verify blob identity then remove (r586 law)
import os
for old_p, new_p in rename_pairs:
    if os.path.exists(old_p) and old_p not in my_dirty:
        rc, sha_new, _ = git("rev-parse", new_head + ":" + new_p)
        rc2, sha_local, _ = git("hash-object", old_p)
        if rc == 0 and rc2 == 0 and sha_new.strip() == sha_local.strip():
            os.remove(old_p)
            print("removed rename residue (blob-identical):", old_p)
        else:
            print("RENAME RESIDUE MISMATCH (kept):", old_p, sha_new.strip()[:12], sha_local.strip()[:12])

# 5. classified checkout: delta files not locally dirty -> restore origin version
to_restore = [f for f in delta if f not in my_dirty and f not in untracked]
skipped = [f for f in delta if f in my_dirty or f in untracked]
if skipped:
    print("SKIP (locally dirty/untracked, keep mine):", skipped)
# batch checkout
for i in range(0, len(to_restore), 20):
    batch = to_restore[i:i+20]
    rc, out, err = git("checkout", "--", *batch)
    if rc != 0:
        print("CHECKOUT FAIL batch:", err)
        sys.exit(1)
print("restored:", len(to_restore))

# 6. verify: remaining dirty should be superset of my_dirty (subset is ok if origin touched same file)
rc, out, err = git("status", "--porcelain")
now_dirty = {}
for line in out.splitlines():
    if not line.strip():
        continue
    st, path = line[:2], line[3:]
    now_dirty[path] = st
missing = [f for f in my_dirty if f not in now_dirty]
if missing:
    print("WARN my-dirty file vanished from status:", missing)
restored_ok = all(f not in now_dirty or now_dirty[f] == "??" for f in to_restore if f not in my_dirty)
# delta files not mine should now be clean
still_dirty_delta = [f for f in to_restore if f in now_dirty]
print("still-dirty delta files after restore (expect []):", still_dirty_delta)
d_rows = [f for f, st in now_dirty.items() if "D" in st]
print("D-face rows (expect []):", d_rows)
print("INTEGRATION OK" if not still_dirty_delta and not d_rows else "INTEGRATION CHECK NEEDED")
