"""r893 bm-a: locate scripts that WRITE bare-code data/daily CSVs (core48 maintainer)."""
import io, os, re

hits = []
for root, dirs, files in os.walk('scripts'):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if not f.endswith('.py'):
            continue
        p = os.path.join(root, f)
        t = io.open(p, encoding='utf-8', errors='replace').read()
        # find any mention of daily dir join/write patterns
        for m in re.finditer(r'(?i)(open\([^)]*daily|daily[^"\']*\.\s*csv|join\([^)]*daily)', t):
            ctx = t[max(0, m.start()-100):m.end()+140].replace('\n', ' | ')
            if re.search(r'(?i)("w|write|to_csv|daily)', ctx):
                hits.append(p + ' :: ' + ctx[:220])
                break

seen = set()
out = []
for h in hits:
    k = h.split(' :: ')[0]
    if k not in seen:
        seen.add(k)
        out.append(h)
io.open('results/_r893bma_daily_writers.txt', 'w', encoding='utf-8').write('\n\n'.join(out))
print('files', len(out))
