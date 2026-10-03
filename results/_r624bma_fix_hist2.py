import io, json
p = 'results/saturation_engine/history_bm-a.jsonl'
t = io.open(p, encoding='utf-8', errors='replace').read()
dec = json.JSONDecoder()
out_lines = []
bad = 0
for line in t.splitlines():
    s = line.strip()
    if not s:
        continue
    objs = []
    i = 0
    while i < len(s):
        # skip whitespace between objects
        while i < len(s) and s[i] in ' \t':
            i += 1
        if i >= len(s):
            break
        try:
            obj, end = dec.raw_decode(s, i)
        except json.JSONDecodeError:
            bad += 1
            break
        objs.append(obj)
        i = end
    if not objs:
        bad += 1
        continue
    for o in objs:
        out_lines.append(json.dumps(o, ensure_ascii=False))
print('objects:', len(out_lines), 'bad-lines:', bad, 'all-dict:', all(isinstance(o, dict) for o in out_lines))
io.open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(out_lines) + '\n')
