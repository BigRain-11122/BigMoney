import io, re
t = io.open(r'scripts\perpetual_faces_n1.py', encoding='utf-8').read()
lines = t.split('\n')
print('LINES', len(lines))
hits = []
for i, ln in enumerate(lines):
    if ('results.json' in ln) or ('argparse' in ln) or ('def main' in ln) or ('materialize' in ln.lower() and 'def ' in ln):
        hits.append((i+1, ln.strip()[:150]))
for h in hits[:60]:
    print(h[0], '|', h[1])
