# -*- coding: utf-8 -*-
# normalize +0800 -> +08:00 in r592-written state.json + heartbeat (precedent-format alignment)
import json, re

def fix(path):
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    t = raw.decode('utf-8')
    t2 = re.sub(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\+0800', r'\1+08:00', t)
    if t2 != t:
        if crlf:
            pass  # already CRLF in text, just write back
        open(path, 'wb').write(t2.encode('utf-8'))
        print(path, 'normalized', t.count('+0800'), '->', t2.count('+0800'), 'remaining')
    else:
        print(path, 'no +0800 form found (already +08:00 or absent)')

fix('state.json')
fix(r'fleet\machines\bm-b.json')

# re-verify json parse + epoch int after edit
for p in ['state.json', r'fleet\machines\bm-b.json']:
    d = json.load(open(p, encoding='utf-8'))
    e = d.get('heartbeat_epoch_utc')
    if e is not None:
        assert isinstance(e, int) and not isinstance(e, bool), p
    print(p, 'json OK; clock fields:', {k: v for k, v in d.items() if 'clock' in k or k in ('last_seen','last_round_ts','ts','updated','updated_at','last_round_at')})
