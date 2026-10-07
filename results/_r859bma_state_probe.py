import json

for p in (r'state-bm-a.json', r'fleet/machines/bm-a.json'):
    b = open(p, 'rb').read()
    crlf = b.count(b'\r\n'); lf = b.count(b'\n') - crlf
    t = b.decode('utf-8', errors='replace')
    d = json.loads(t)
    rt1 = json.dumps(d, ensure_ascii=False, indent=1).encode('utf-8')
    rt2 = json.dumps(d, ensure_ascii=False, indent=1).replace('\n', '\r\n').encode('utf-8')
    print(p, '| bytes:', len(b), '| CRLF:', crlf, '| LF:', lf,
          '| rt1-ident:', rt1 == b, '| rt2-ident:', rt2 == b,
          '| ends-nl:', b.endswith(b'\n'))
