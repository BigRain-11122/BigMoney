import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
t = io.open('research/PERPETUAL_N1_W213_PREREG.md', encoding='utf-8').read()
for kw in ['六门', 'six', '五键', 'five-key']:
    hits = [m.start() for m in re.finditer(re.escape(kw), t)]
    print(kw, '->', len(hits), 'hits')
    for h in hits[:3]:
        s = max(0, h-200)
        print('   ...', t[s:h+300].replace('\n', ' | ')[:500])
        print()
