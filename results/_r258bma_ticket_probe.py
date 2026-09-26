import json, subprocess, sys

path = r'fleet\tasks\T-2026-09-26-73-P1.json'
# raw bytes via git cat-file (PS redirect re-encodes -- r255 law)
blob = subprocess.run(['git', 'show', 'HEAD:' + path.replace('\\', '/')],
                      capture_output=True).stdout
raw = blob
print('size:', len(raw))
print('BOM:', raw[:3] == b'\xef\xbb\xbf')
body = raw[3:] if raw[:3] == b'\xef\xbb\xbf' else raw
crlf = body.count(b'\r\n')
lf = body.count(b'\n') - crlf
print('EOL: CRLF lines', crlf, '/ bare LF lines', lf)
txt = body.decode('utf-8-sig')
print('ascii-escaped present:', '\\u' in txt[:5000])
lines = txt.split('\r\n' if crlf > lf else '\n')
second = lines[1] if len(lines) > 1 else ''
print('indent depth (line2 leading spaces):', len(second) - len(second.lstrip(' ')))
print('trailing newline:', raw.endswith(b'\n'))
d = json.loads(txt)
print('status:', d.get('status'))
print('progress keys:', list((d.get('progress') or {}).keys())[-3:])
