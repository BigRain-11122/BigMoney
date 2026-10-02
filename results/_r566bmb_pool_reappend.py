"""r566 bm-b: re-append saved pool_core_samples rows onto post-ff origin version (r530 bytes law)."""
import os
p = r'C:\Fluxgroup\FluxGroup\quant\bigmoney\results\pool_core_samples.jsonl'
tmp = os.path.join(os.environ['TEMP'], '_r566bmb_pool_rows.tmp')
cur = open(p, 'rb').read()
rows = [r for r in open(tmp, 'rb').read().splitlines(keepends=True) if r.strip()]
existing = set(cur.splitlines())
new = [r for r in rows if r not in existing]
if not cur.endswith(b'\n'):
    cur += b'\n'
open(p, 'wb').write(cur + b''.join(new))
print('re-appended rows:', len(new), 'of', len(rows), 'saved; dupes skipped:', len(rows) - len(new))
