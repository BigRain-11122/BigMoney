import json, subprocess, datetime

RAW = r'results/runnable_pool.json'
# rollback the broken insert
subprocess.run(['git', 'checkout', '--', RAW], check=True)
raw0 = open(RAW, encoding='utf-8', newline='').read()
d0 = json.loads(raw0)
assert len(d0['entries']) == 406
print('rolled back clean, entries=406')

entry = json.load(open(r'results/_r859bma_w16_entry.json', encoding='utf-8'))

def ser(v):
    return json.dumps(v, ensure_ascii=False)

lines = ['   ' + ser(k) + ': ' + ser(v) + ',' for k, v in entry.items()]
lines[-1] = lines[-1].rstrip(',')
block = '  {\r\n' + '\r\n'.join(lines) + '\r\n  }'

tail_anchor = '\r\n  }\r\n ]\r\n}'
assert raw0.endswith(tail_anchor) and raw0.count(tail_anchor) == 1
# original last-entry close becomes "...}," then my block, then array/root close
new = (raw0[:-len(tail_anchor)]
       + '\r\n  },\r\n' + block
       + '\r\n ]\r\n}')

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
old_u = '"updated_at": "2026-10-07T23:21:00+08:00"'
assert new.count(old_u) == 1
new = new.replace(old_u, '"updated_at": "%s"' % now)

with open(RAW, 'w', encoding='utf-8', newline='') as fh:
    fh.write(new)

d = json.load(open(RAW, encoding='utf-8'))
assert len(d['entries']) == 407, 'count gate'
e = next(x for x in d['entries'] if x.get('id') == 'TRIAL-LABOR-W16-SCREEN')
assert e['status'] == 'ready' and e['shards'][0]['key'] == 'w16-screen-0of1'
assert e['shards'][0]['status'] == 'ready'
# reparse of pre-existing entries integrity: first+last-minus-one ids unchanged
assert d['entries'][0]['id'] == d0['entries'][0]['id']
assert d['entries'][404]['id'] == d0['entries'][404]['id']
print('INSERTED OK | entries=407 | tail: ...block } + array close | updated_at', now)
