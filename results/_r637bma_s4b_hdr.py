"""r637 bm-a S4b: insert header direct-write line (idempotent; entry already appended)."""
import hashlib, re

p = 'research/pit-pool.md'
raw = open(p, 'rb').read()
crlf = raw.count(b'\r\n')
lf_only = len(re.findall(rb'(?<!\r)\n', raw))
E = b'\r\n' if crlf > lf_only else b'\n'
print('file EOL:', 'CRLF' if E == b'\r\n' else 'LF', 'crlf=', crlf, 'lfo=', lf_only)

entry_bytes = 1072
md5 = 'b7dbc4a1b589113869b833ab103cea1e'
hdr = ('> 直写行（r637 bm-a·整面回退吞活认领坑落件）：r637 双烧止损窗条 1 条直入本件（非迁移·域内 direct-write·r401/r417/r628 范式）'
       '·追加核 %d B（LF blob 面·md5=%s）。' % (entry_bytes, md5)).encode('utf-8')

if hdr in raw:
    print('header already present -- no-op')
else:
    anchor = '·追加核 671 B（LF blob 面·md5=61a76e32be78b5dd2c23d129700421d1）。'.encode('utf-8')
    n = raw.count(anchor)
    assert n == 1, 'anchor count=%d' % n
    raw2 = raw.replace(anchor, anchor + E + hdr)
    with open(p, 'wb') as f:
        f.write(raw2)
    print('header line inserted')
import subprocess
print(subprocess.run(['git', 'diff', '--stat', '--', 'research/pit-pool.md'], capture_output=True, text=True).stdout)
