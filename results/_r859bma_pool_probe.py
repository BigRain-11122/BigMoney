import json

RAW = r'results/runnable_pool.json'
b = open(RAW, 'rb').read()
crlf = b.count(b'\r\n'); lf = b.count(b'\n') - crlf
print('bytes:', len(b), '| CRLF:', crlf, '| bare-LF:', lf)
print('endswith-newline:', b.endswith(b'\n'), '| tail-20:', b[-20:])

# roundtrip probe (r678)
txt = b.decode('utf-8')
d = json.loads(txt)
rt = json.dumps(d, ensure_ascii=False, indent=2)
print('roundtrip-identical(indent2):', rt.encode('utf-8') == b)

# entries count + W16-GENERATE anchor region
es = d.get('entries', [])
print('entries:', len(es))
idx = next(i for i, e in enumerate(es) if e.get('id') == 'TRIAL-LABOR-W16-GENERATE')
print('W16-GENERATE at entry index:', idx, 'of', len(es)-1, '(last:', es[-1].get('id'), ')')

# exact raw text at end of W16-GENERATE entry (anchor candidate)
pos = txt.find('"id": "TRIAL-LABOR-W16-GENERATE"')
print('id-needle-pos:', pos)
hpos = txt.find('"harvest_claim": "main.bm-c.json"', pos)
print('harvest-needle-rel:', hpos - pos)
seg = txt[hpos:hpos+80]
print('anchor-segment-repr:', repr(seg[:80]))
