"""r636 bm-a: value-nulls claim release on shared pool face (origin-visible release).

Origin still carries the 18:16:08 bm-a claim (01302cc2d reached origin). Release
it surgically (r509 byte law, CRLF-preserving) + append release note; verify;
the caller commits+pushes immediately (settle respects origin truth per r628).
"""
import json
import subprocess
import sys

REL = (" | rel-bm-a-r636 18:4x: 5th double-burn containment closeout -- 18:16 autofill claim "
       "(stale-sha pin auto-clear per r617 boundary), burn killed 18:52 tree-sweep r618, "
       "50 illegal rows discarded, file restored origin-verbatim; divlowvol 18:38 ghost claim "
       "never reached origin (rebase take-ours); bm-b canonical trio burn in flight -- "
       "do NOT claim, fuse division pins armed both faces")

fp = r'results\runnable_pool.json'
data = open(fp, 'rb').read()
crlf = data.count(b'\r\n')
lf = data.count(b'\n')
eol = b'\r\n' if crlf * 2 > lf else b'\n'
KEY = b'"key": "fund-value-p1-nulls-0of1"'
i = data.find(KEY)
assert i > 0, 'value shard not found'
end = data.find(b'}' + eol, i)
block = data[i:end]
print('value shard: owner-bm-a:', b'"owner": "bm-a"' in block,
      '| 18:16:08:', b'18:16:08' in block,
      '| r636 note already:', b'rel-bm-a-r636' in block)

if b'"owner": "bm-a"' in block and b'18:16:08' in block and b'rel-bm-a-r636' not in block:
    nb = block.replace(b'"owner": "bm-a"', b'"owner": null')
    nb = nb.replace(b'"owner_since": "2026-10-03 18:16:08"', b'"owner_since": null')
    anchor = b'keep-block note on crash_fuse",'
    assert anchor in nb, 'note anchor missing'
    nb = nb.replace(anchor, b'keep-block note on crash_fuse' + REL.encode() + b'",', 1)
    nd = data[:i] + nb + data[end:]
    json.loads(nd.decode('utf-8'))
    open(fp, 'wb').write(nd)
    after = open(fp, 'rb').read()
    json.loads(after.decode('utf-8'))
    print('released; bare-LF delta:', (after.count(b'\n') - after.count(b'\r\n')) - (lf - crlf))
else:
    print('no action needed (already released or unexpected state)')

# also verify divlowvol shard is claim-free and fuse pins present post-rebase
i2 = data.find(b'"key": "fund-divlowvol-p1-nulls-0of1"')
end2 = data.find(b'}' + eol, i2)
blk2 = data[i2:end2]
print('divlowvol shard: claim present:', b'"owner": "bm-a"' in blk2)
for f in (r'results\crash_fuse.json', r'results\crash_fuse.bm-a.json'):
    cf = json.load(open(f, encoding='utf-8'))
    d = cf['sigs'].get('scripts/fund_divlowvol_p1.py|run,--nulls', {})
    v = cf['sigs'].get('scripts/fund_value_p1.py|run,--nulls', {})
    print(f.split(chr(92))[-1], '| div pin sha:', d.get('code_sha256'),
          '| div refusals:', d.get('refusals'), '| value pin sha:', v.get('code_sha256'),
          '| value refusals:', v.get('refusals'), '| value note r636:',
          'r636' in (v.get('note') or ''))
r = subprocess.run(['git', 'diff', '--numstat', '--', fp], capture_output=True,
                   text=True, encoding='utf-8', errors='replace')
print('pool numstat:', r.stdout.strip())
sys.exit(0)
