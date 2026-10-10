import subprocess, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GIT = r"C:\Program Files\Git\cmd\git.exe"

def run(*a, binary=False):
    r = subprocess.run([GIT] + list(a), capture_output=True)
    return r.stdout if binary else r.stdout.decode('utf-8', errors='replace')

# 1. post_review.jsonl: append-only union (dedup identical lines, keep order: ours then theirs)
base = run('show', ':1:results/post_review.jsonl', binary=True).decode('utf-8', errors='replace').splitlines()
ours = run('show', ':2:results/post_review.jsonl', binary=True).decode('utf-8', errors='replace').splitlines()
theirs = run('show', ':3:results/post_review.jsonl', binary=True).decode('utf-8', errors='replace').splitlines()
seen = set()
out = []
for ln in ours + theirs:
    k = ln.strip()
    if not k:
        continue
    if k in seen:
        continue
    # validate json line
    try:
        json.loads(k)
    except Exception:
        continue
    seen.add(k)
    out.append(k)
with open('results/post_review.jsonl', 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(out) + '\n')
print(f"post_review.jsonl union: base={len(base)} ours={len(ours)} theirs={len(theirs)} -> merged={len(out)}")

# 2. REPORT-20261011.md: add/add, origin (theirs, bm-b r850 vote-complete 00:27) is NEWER -> take theirs
theirs_md = run('show', ':3:results/post_review/REPORT-20261011.md', binary=True)
with open('results/post_review/REPORT-20261011.md', 'wb') as f:
    f.write(theirs_md)
print(f"REPORT-20261011.md take-theirs bytes={len(theirs_md)}")
