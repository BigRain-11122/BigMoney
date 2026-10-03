"""r636 bm-a: byte-level surgical claim release on shared pool face (r509 redo).

The first text-mode attempt flipped CRLF->LF (whole-file 14041/14041 churn,
caught by numstat assert per r509). This redo works on BYTES: probe line endings,
surgical byte replacement only inside the fund-value-p1-nulls-0of1 shard block,
json.loads assert, numstat surgical assert.
"""
import json
import subprocess
import sys

FP = r'results\runnable_pool.json'
data = open(FP, 'rb').read()
crlf = data.count(b'\r\n')
lf = data.count(b'\n')
print('probe: CRLF', crlf, '| total LF(incl CRLF)', lf, '| bare LF', lf - crlf)

KEY = b'"key": "fund-value-p1-nulls-0of1"'
i = data.find(KEY)
assert i > 0, 'shard key not found'
end = data.find(b'}\r\n', i)
assert end > 0, 'shard block end not found'
block = data[i:end]

assert b'"owner": "bm-a"' in block and b'18:16:08' in block, 'expected claim not in shard block'
new_block = block.replace(b'"owner": "bm-a"', b'"owner": null')
new_block = new_block.replace(b'"owner_since": "2026-10-03 18:16:08"', b'"owner_since": null')

REL_NOTE = (b" | rel-bm-a-r636 18:5x: 5th double-burn containment -- autofill claimed 18:16 after "
            b"r627 per-sig newer-wins kept the pin at stale sha efd7b44a (r626d runner edit) -> "
            b"code_changed auto-clear; burn killed 18:52 (tree-sweep 52 pids r618), 50 illegal rows "
            b"discarded, nulls.jsonl restored origin-verbatim; bm-b canonical burn in flight")
anchor = b'keep-block note on crash_fuse",'
assert anchor in new_block, 'note anchor missing'
assert b'rel-bm-a-r636' not in new_block, 'release note already present'
new_block = new_block.replace(anchor, b'keep-block note on crash_fuse' + REL_NOTE + b'",', 1)

new_data = data[:i] + new_block + data[end:]
# parse assert (bytes -> text)
json.loads(new_data.decode('utf-8'))
open(FP, 'wb').write(new_data)

# re-verify: parse + line-ending preservation + numstat surgical
after = open(FP, 'rb').read()
assert after.count(b'\r\n') == crlf, 'CRLF count drifted'
json.loads(after.decode('utf-8'))
r = subprocess.run(['git', 'diff', '--numstat', '--', FP], capture_output=True, text=True,
                   encoding='utf-8', errors='replace')
print('numstat:', r.stdout.strip())
print('OK byte-surgical release done')
sys.exit(0)
