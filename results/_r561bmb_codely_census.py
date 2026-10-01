import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

c = open('CODELY.md', encoding='utf-8').read()
pos = [(m.start(), m.group(0)) for m in re.finditer(r'^(?:#+ .*|- \[2026-.*|\- \[2026-.*)$', c, re.M)]
entries = []
for i, (p, head) in enumerate(pos):
    if head.startswith('-'):
        end = pos[i+1][0] if i+1 < len(pos) else len(c)
        entries.append((p, end, c[p:end]))

KEEP_MARK = ('How to apply', 'how to apply', '红线', '铁律', '预防律')
for p, e, t in entries:
    first = t.splitlines()[0][:110]
    size = len(t.encode('utf-8'))
    keep = any(m in t for m in KEEP_MARK)
    print(f"{size:6d}B {'KEEP' if keep else 'ARCH'} {first}")
print('total', len(entries), 'entries')
