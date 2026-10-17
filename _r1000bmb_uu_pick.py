# r1000 resolve d19 probe UU by ts newer-wins (ASCII only)
import subprocess, re

def ts_of(rev):
    out = subprocess.run(['git', 'show', rev + ':results/_r686bmb_d19_check.json'],
                         capture_output=True).stdout.decode('utf-8', errors='replace')
    m = re.search(r'"ts"\s*:\s*"([^"]+)"', out)
    if not m:
        m = re.search(r'"probe_ts"\s*:\s*"([^"]+)"', out)
    return (m.group(1) if m else 'NO-TS'), len(out)

t_bm_c = ts_of('a27af4d09')
t_mine = ts_of('53a8568cd')
print('bm-c side (a27af4d09):', t_bm_c)
print('my side (53a8568cd):', t_mine)
winner = 'theirs' if t_mine[0] > t_bm_c[0] else 'ours'
print('newer-wins side =', winner, '(rebase theirs=my commit, ours=bm-c tip)')
