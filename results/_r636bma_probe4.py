import subprocess

# What did the daemon's 18:38 commit actually change in runnable_pool.json?
r = subprocess.run(['git', 'show', '31d004d68', '--numstat', '--format=%h %ci %s'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
print(r.stdout[:800])
print('=' * 60)
# The diff hunks touching the two nulls shards
r2 = subprocess.run(['git', 'show', '31d004d68', '--', 'results/runnable_pool.json'],
                    capture_output=True, text=True, encoding='utf-8', errors='replace')
txt = r2.stdout
lines = txt.splitlines()
for i, l in enumerate(lines):
    if 'fund-value-p1-nulls' in l or 'fund-divlowvol-p1-nulls' in l or 'owner' in l.lower() and 'since' in ''.join(lines[max(0,i-1):i+2]).lower():
        for j in range(max(0, i - 2), min(len(lines), i + 6)):
            print(lines[j][:160])
        print('---')
print('=' * 60)
# Full recent log with both dates
r3 = subprocess.run(['git', 'log', '-6', '--format=%h | a:%ai | c:%ci | %s'],
                    capture_output=True, text=True, encoding='utf-8', errors='replace')
print(r3.stdout)
