import subprocess, json
GIT = r'C:\Program Files\Git\cmd\git.exe'
def blob(stage):
    return subprocess.run([GIT,'cat-file','blob',stage+'results/x2_watch_log.jsonl'],capture_output=True).stdout.decode('utf-8','replace').splitlines()
base, o, loc = blob(':1:'), blob(':2:'), blob(':3:')
print('base lines:', len(base), 'origin:', len(o), 'local:', len(loc))
joined_marker = '}' + '{"ts"'
print('legacy joined-line in base?', joined_marker in '\n'.join(base[:3]))
print('legacy joined-line count base/origin/local:', '\n'.join(base).count(joined_marker), '\n'.join(o).count(joined_marker), '\n'.join(loc).count(joined_marker))
so, sl = set(o), set(loc)
only_o, only_l = so-sl, sl-so
print('origin-only lines:', len(only_o), '| local-only lines:', len(only_l))
for l in sorted(only_o)[:4]: print(' O:', l[:130])
for l in sorted(only_l)[:4]: print(' L:', l[:130])
base_only = set(base)-so-sl
print('base-only (dropped by both)?', len(base_only))
for l in sorted(base_only)[:4]: print(' B:', l[:130])
