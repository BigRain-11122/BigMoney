import json, datetime

RAW = r'results/runnable_pool.json'
entry = json.load(open(r'results/_r859bma_w16_entry.json', encoding='utf-8'))

raw = open(RAW, encoding='utf-8', newline='').read()
assert '\r\n' in raw and raw.count('\\u6267') == 0  # CRLF host, raw-CJK face

def ser(v):
    return json.dumps(v, ensure_ascii=False)

# build entry block in the file's observed format:
# entry open "  {", fields 3-space, shards 4/5-space, close "  }"
fields = list(entry.items())
lines = []
for k, v in fields:
    lines.append('   ' + ser(k) + ': ' + ser(v))
body = '\r\n'.join(lines)
block = '  {\r\n' + body + '\r\n  }'

# insertion anchor: the file tail = last entry close + array close + root close
tail_anchor = '\r\n  }\r\n ]\r\n}'
assert raw.endswith(tail_anchor), 'tail anchor drift'
assert raw.count(tail_anchor) == 1, 'tail anchor not unique'

new = raw[:-len(tail_anchor)] + '\r\n  },\r\n' + block + tail_anchor

# updated_at line surgical replace (original ISO+offset form)
now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
old_u = '"updated_at": "2026-10-07T23:21:00+08:00"'
assert new.count(old_u) == 1, 'updated_at anchor not unique'
new = new.replace(old_u, '"updated_at": "%s"' % now)

with open(RAW, 'w', encoding='utf-8', newline='') as fh:
    fh.write(new)

# post gates
d = json.load(open(RAW, encoding='utf-8'))
assert len(d['entries']) == 407, 'entry count gate'
e = next(x for x in d['entries'] if x.get('id') == 'TRIAL-LABOR-W16-SCREEN')
assert e['status'] == 'ready' and e['shards'][0]['key'] == 'w16-screen-0of1'
assert e['shards'][0]['status'] == 'ready'
print('INSERTED OK | entries=407 | shard w16-screen-0of1 ready | updated_at ->', now)
