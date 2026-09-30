"""r487 bm-b rebase conflict resolver: results/crash_fuse.json UU nested union zero-loss.

Sides: stage2 (ours, replayed crashed-session runtime-sync blob, 27 sigs/19 cleared)
       stage3 (theirs, origin newer bm-a fire-fighting blob, 27 sigs/19 cleared)
Facts (probe _r487bmb_probe_fuse.py): 23 common sigs identical, 19 cleared identical,
4 only-in-2 (stale n1 shard crash rows), 4 only-in-3 (lowamp cell rows).
Canon: r446/r442 append-only monotonic family -> nested union zero-loss
(same as r484bmb resolver intent: union, no key dropped). No same-key content
conflicts exist, so no tie-break needed. EOL/indent mirrored from stage3 producer.
"""
import subprocess, json

P = 'results/crash_fuse.json'

def raw_stage(n):
    return subprocess.check_output(['git', 'show', ':%d:%s' % (n, P)])

a = json.loads(raw_stage(2).decode('utf-8'))
b = json.loads(raw_stage(3).decode('utf-8'))

sigs = dict(a.get('sigs', {}))
for k, v in b.get('sigs', {}).items():
    if k not in sigs:
        sigs[k] = v
    else:
        # same key both sides -> keep fresher by max(last_crash_ts, last_refusal_ts); tie -> HEAD side (r140)
        def freshest(r):
            return max(r.get('last_crash_ts') or '', r.get('last_refusal_ts') or '')
        if freshest(v) > freshest(sigs[k]):
            sigs[k] = v
cleared = dict(a.get('cleared', {}))
for k, v in b.get('cleared', {}).items():
    if k not in cleared or (v.get('cleared_ts') or '') > (cleared[k].get('cleared_ts') or ''):
        cleared[k] = v

out = {'sigs': sigs, 'cleared': cleared}
# zero-loss assertions (union counts)
assert len(sigs) == len(set(a.get('sigs', {})) | set(b.get('sigs', {}))), 'sigs union loss'
assert len(cleared) == len(set(a.get('cleared', {})) | set(b.get('cleared', {}))), 'cleared union loss'
assert set(sigs) >= set(a.get('sigs', {})) and set(sigs) >= set(b.get('sigs', {}))
for k in set(a.get('sigs', {})) & set(b.get('sigs', {})):
    # all common rows were probe-verified identical; assert content preserved from stage2
    assert sigs[k] == a['sigs'][k] or sigs[k] == b['sigs'][k]

# EOL/indent mirror: probe stage3 producer bytes (newer producer format is the live one)
ref = raw_stage(3)
crlf = ref.count(b'\r\n')
use_crlf = crlf * 2 >= ref.count(b'\n')
txt = json.dumps(out, ensure_ascii=False, indent=2)
if use_crlf:
    txt = txt.replace('\n', '\r\n')
open(P, 'w', encoding='utf-8', newline='').write(txt)
# parse-validate before add (r185 law)
chk = json.loads(open(P, 'rb').read().decode('utf-8'))
assert len(chk['sigs']) == len(sigs) and len(chk['cleared']) == len(cleared)
print('resolved: sigs %d + cleared %d = %d rows (union of %d/%d + %d/%d), eol=%s'
      % (len(sigs), len(cleared), len(sigs) + len(cleared),
         len(a['sigs']), len(b['sigs']), len(a['cleared']), len(b['cleared']),
         'CRLF' if use_crlf else 'LF'))
