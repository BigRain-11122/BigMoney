import io

raw = open('CODELY.md', 'rb').read()
print('bytes:', len(raw), 'CRLF:', raw.count(b'\r\n'), 'LF-only:', raw.count(b'\n') - raw.count(b'\r\n'), 'tail:', repr(raw[-40:]))
t = raw.decode('utf-8')
lines = t.splitlines()
print('total lines:', len(lines))
for i, l in enumerate(lines):
    if '坑律正典全量归档' in l:
        print('== archive-canon line at', i, 'len', len(l.encode('utf-8')))
        print(l[:500])
        print('...')
print('== last 6 lines:')
for l in lines[-6:]:
    print(' ', l[:120])
# archive file EOL
ar = open('research/memory-archive/202609.md', 'rb').read()
print('archive bytes:', len(ar), 'CRLF:', ar.count(b'\r\n'), 'LF-only:', ar.count(b'\n') - ar.count(b'\r\n'), 'tail:', repr(ar[-40:]))
