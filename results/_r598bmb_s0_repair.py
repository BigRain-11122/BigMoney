"""r598 bm-b S0 repair pass: restore all delta files from old base e3b3f8d9b to origin/main (intersection with my-dirty was verified empty)."""
import subprocess, os

def git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout, r.stderr

OLD = "e3b3f8d9b"
rc, new_head, _ = git("rev-parse", "origin/main")
new_head = new_head.strip()

rc, out, err = git("diff", "--name-status", OLD, new_head)
assert rc == 0, err
delta, renames = [], []
for line in out.splitlines():
    parts = line.split("\t")
    if parts[0].startswith("R"):
        delta.append(parts[2]); renames.append((parts[1], parts[2]))
    else:
        delta.append(parts[-1])
print("delta:", len(delta), "renames:", renames)

# current status map
rc, out, _ = git("status", "--porcelain")
st_map = {}
for line in out.splitlines():
    if line.strip():
        st_map[line[3:]] = line[:2]

restored = 0
for f in delta:
    st = st_map.get(f)
    if st in (" M", " D", "MM", None):
        rc, _, err = git("checkout", "--", f)
        if rc != 0:
            print("FAIL:", f, err.strip())
        else:
            restored += 1
print("restored:", restored)

# rename residue: old-path worktree file now untracked -> blob-verify vs new path then remove (r586)
for old_p, new_p in renames:
    if os.path.exists(old_p):
        _, sha_new, _ = git("rev-parse", new_head + ":" + new_p)
        _, sha_local, _ = git("hash-object", old_p)
        if sha_new.strip() and sha_local.strip() == sha_new.strip():
            os.remove(old_p)
            print("removed blob-identical rename residue:", old_p)
        else:
            print("RESIDUE MISMATCH kept:", old_p)

# verify: no D rows, no M rows on delta files
rc, out, _ = git("status", "--porcelain")
bad = [l for l in out.splitlines() if l.strip() and ("D" in l[:2] and "?" not in l[:2])]
m_delta = [l[3:] for l in out.splitlines() if l.strip() and l[:2] == " M" and l[3:] in delta]
print("D rows now (expect []):", bad)
print("still-M delta files (expect []):", m_delta)
print("REPAIR OK" if not bad and not m_delta else "REPAIR INCOMPLETE")
