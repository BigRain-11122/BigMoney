import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
t = open(r'logs/iteration-loop/round_reports.md', 'rb').read().decode('utf-8', errors='replace')
lines = t.splitlines()
pat = re.compile(r'round 6(4[1-9])\s*\(bm-b|round 641 addendum|round 645 addendum|round 646 addendum')
hits = [l for l in lines if pat.search(l)]
for l in hits:
    print(l[:420])
    print('---')
