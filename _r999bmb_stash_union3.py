# r999: line-union post_review.jsonl + REPORT-20261018.md: HEAD (origin tip incl bm-c r1081 rows)
# union stash-extra rows (r998/dead-r999 appends). Blind stash-restore would revert bm-c rows (claw law).
# ASCII-only per iteration_loop.ps1 encoding law.
import subprocess, io

def blob(spec, path):
    return subprocess.check_output(['git', 'show', spec + ':' + path]).decode('utf-8', errors='replace')

sha = subprocess.check_output(['git', 'rev-parse', 'refs/stash']).decode().strip()
targets = ['results/post_review.jsonl', 'results/post_review/REPORT-20261018.md']
for p in targets:
    head = blob('HEAD', p).splitlines()
    stashed = blob(sha, p).splitlines()
    hset = set(l.rstrip('\r') for l in head)
    extra = [l for l in stashed if l.rstrip('\r') not in hset]
    merged = head + extra
    with io.open(p, 'w', encoding='utf-8', newline='') as f:
        if merged:
            f.write('\n'.join(merged) + '\n')
    print('UNION %s head=%d stash=%d extra=%d' % (p, len(head), len(stashed), len(extra)))
