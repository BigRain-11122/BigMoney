# -*- coding: utf-8 -*-
# r856 bm-b: pool EOL drift forensics -- walk history to find CRLF->LF transition
import subprocess

def run(*a, binary=False):
    r = subprocess.run(list(a), capture_output=True)
    return r.stdout if binary else r.stdout.decode('utf-8', errors='replace')

rows = run('git', 'log', '--format=%h|%ad', '--date=format:%m-%d-%H:%M',
           '--', 'results/runnable_pool.json').strip().splitlines()
print(f"total commits touching pool: {len(rows)}")
for row in rows[:40]:
    h, d = row.split('|')
    b = run('git', 'cat-file', 'blob', h + ':results/runnable_pool.json', binary=True)
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n') - crlf
    tag = 'CRLF' if crlf > 0 and crlf >= lf else ('LF' if lf > 0 else '?')
    print(f"{h} {d} crlf={crlf} lf_only={lf} -> {tag}")
    if tag == 'CRLF':
        print("^^^ TRANSITION FOUND (first CRLF commit walking back)")
        break
