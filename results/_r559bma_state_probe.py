import json, time, datetime

def roundtrip_ok(path):
    b = open(path, 'rb').read()
    t = b.decode('utf-8')
    obj = json.loads(t)
    re = json.dumps(obj, indent=2, ensure_ascii=False)
    return t == re, t, obj

for p in ('state-bm-a.json', 'fleet/machines/bm-a.json'):
    ok, t, obj = roundtrip_ok(p)
    print(p, 'roundtrip-identical:', ok, '| bytes', len(b if (b := t.encode("utf-8")) else 0))
