import subprocess
out = subprocess.run(['git', 'cat-file', 'blob', 'HEAD:fleet/tasks/T-2026-09-26-76-P1.json'], capture_output=True)
raw = out.stdout
print('BOM:', raw[:3] == b'\xef\xbb\xbf')
print('CRLF:', b'\r\n' in raw)
sig = 'utf-8-sig' if raw[:3] == b'\xef\xbb\xbf' else 'utf-8'
txt = raw.decode(sig)
lines = txt.splitlines()
for l in lines[:4]:
    print(repr(l[:70]))
key = '"progress_r260"'
for l in lines:
    if key in l:
        print('progress line head:', repr(l[:130]))
        print('indent spaces:', len(l) - len(l.lstrip(' ')))
        print('ensure_ascii check (raw backslash-u in bytes):', b'\\u' in raw[:2000])
        break
