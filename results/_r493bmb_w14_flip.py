import json, subprocess, os

PATH = 'results/runnable_pool.json'
raw = open(PATH, 'rb').read()
crlf = raw.count(b'\r\n'); lf = raw.count(b'\n') - crlf
print('line endings: CRLF x', crlf, '| bare LF x', lf)
text = raw.decode('utf-8')
pool = json.loads(text)

flipped = []
for e in pool.get('entries', []):
    if e.get('id') == 'TRIAL-LABOR-W14-GENERATE':
        for sh in e.get('shards', []):
            if sh.get('key') == 'generate-0of1' and sh.get('status') == 'waiting':
                sh['status'] = 'ready'
                sh['park_note'] = (sh.get('park_note', '') +
                    ' | re-armed ready r493 bm-b session 2026-10-01 ~05:2x: park was dead-r472-session '
                    'pre-burn hold; runner landed+selftest 53/53 at r472 adoption; trial-labor standing '
                    'line O-2026-09-27-2250 (禁空转禁等 CEO 提醒); evidence_cutoff=2026-09-22 read face '
                    'unaffected by in-flight 09-30 panel append; deliverable = w14_candidates.json '
                    '(FB-004 fire-declared)')
                flipped.append('shard generate-0of1')
        if e.get('status') == 'waiting':
            e['status'] = 'ready'
            flipped.append('entry')
print('flipped:', flipped)

if flipped:
    out = json.dumps(pool, ensure_ascii=False, indent=2)
    if crlf > 0 and lf == 0:
        out = out.replace('\n', '\r\n')
    with open(PATH, 'w', encoding='utf-8', newline='') as f:
        f.write(out)
    print('written')
else:
    print('nothing to flip (state changed?)')
