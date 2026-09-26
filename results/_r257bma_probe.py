import json, subprocess, sys

P = 'fleet/tasks/T-2026-09-26-73-P1.json'
raw = subprocess.run(['git', 'show', 'HEAD:' + P], capture_output=True).stdout
print('len', len(raw))
print('BOM:', raw[:3] == b'\xef\xbb\xbf')
print('CRLF:', b'\r\n' in raw, 'LF count:', raw.count(b'\n'), 'CRLF count:', raw.count(b'\r\n'))
head = raw[:400]
print('ascii_escaped_unicode:', b'\\u' in raw)
# indent: second line leading spaces
lines = raw.split(b'\n')
for i, ln in enumerate(lines[1:6], start=1):
    n = len(ln) - len(ln.lstrip(b' '))
    print(f'line{i} indent={n}', ln[:60])
