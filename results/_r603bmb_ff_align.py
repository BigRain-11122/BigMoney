import subprocess, sys

def git(args, **kw):
    r = subprocess.run(['git'] + args, capture_output=True, text=True,
                       encoding='utf-8', errors='replace', **kw)
    return r.returncode, r.stdout, r.stderr

# 1. drop the two unpushed appender commits (content stays on disk)
rc, out, err = git(['reset', '--mixed', '0210dfff6'])
print('reset', rc, err.strip()[:200])

# 2. dirty set after reset
rc, out, err = git(['status', '--porcelain'])
assert rc == 0
dirty = []
for line in out.splitlines():
    if not line.strip():
        continue
    st, path = line[:2], line[3:]
    if '?' in st:
        continue
    dirty.append(path)

# 3. origin new files merge-base..origin/main
rc, out2, err = git(['diff', '--name-only', '0210dfff6', 'origin/main'])
assert rc == 0
origin_new = [l for l in out2.splitlines() if l.strip()]

overlap = [p for p in origin_new if p in dirty]
print('dirty=', len(dirty), 'origin_new=', len(origin_new), 'overlap=', len(overlap))

# 4. restore overlap faces to HEAD (merge-base) so FF is unobstructed;
#    FF then brings them to origin content = origin-verbatim by construction.
rc, out, err = git(['restore', '--'] + overlap)
print('restore', rc, err.strip()[:300])
assert rc == 0, err

# 5. fast-forward to origin/main
rc, out, err = git(['merge', '--ff-only', 'origin/main'])
print('merge-ff', rc, (out + err).strip()[:300])
assert rc == 0, out + err

# 6. verify
rc, out, err = git(['rev-parse', 'HEAD', 'origin/main'])
print(out.split())
rc, out, err = git(['status', '--porcelain'])
mods = [l for l in out.splitlines() if l.strip() and '?' not in l[:2]]
print('post-FF dirty tracked count =', len(mods))
for l in mods[:60]:
    print(l)
