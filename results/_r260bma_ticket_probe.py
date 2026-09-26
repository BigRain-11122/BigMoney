# five-face byte probe of ticket JSON before write-back (R254/R255/R257 law)
import subprocess, json

PATH = 'fleet/tasks/T-2026-09-26-82-P1.json'
r = subprocess.run(['git', 'show', f'HEAD:{PATH}'], capture_output=True)
raw = r.stdout
print('bytes', len(raw))
print('BOM', raw.startswith(b'\xef\xbb\xbf'))
print('CRLF_count', raw.count(b'\r\n'), 'LF_count', raw.replace(b'\r\n', b'').count(b'\n'))
print('trailing_newline', raw.endswith(b'\n'))
lines = raw.split(b'\n')
print('first_line', lines[0][:40])
# indent probe: first indented line leading spaces
for ln in lines:
    if ln.startswith((b' ', b'\t')):
        print('indent_len', len(ln) - len(ln.lstrip()), 'sample', ln[:30])
        break
# ensure_ascii face: any raw multibyte utf-8 sequences?
try:
    raw.decode('ascii')
    print('ascii_face', True)
except UnicodeDecodeError:
    print('ascii_face', False, '(raw utf-8 multibyte present)')
# key order as loaded
d = json.loads(raw.decode('utf-8-sig'))
print('keys', list(d.keys()))
