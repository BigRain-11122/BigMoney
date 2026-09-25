import io, json

def sides(f):
    t = io.open(f, encoding='utf-8').read()
    lines = t.split('\n')
    head_lines, ours_lines = [], []
    state = 'common'
    for ln in lines:
        if ln.startswith('<<<<<<<'): state='head'; continue
        if ln.startswith('======='): state='ours'; continue
        if ln.startswith('>>>>>>>'): state='common'; continue
        if state=='head': head_lines.append(ln); continue
        if state=='ours': ours_lines.append(ln); continue
        head_lines.append(ln); ours_lines.append(ln)
    return '\n'.join(head_lines), '\n'.join(ours_lines)

h, o = sides('results/autofill_state.json')
hj, oj = json.loads(h), json.loads(o)
print('=== autofill_state keys:', list(hj))
for k in hj:
    hv, ov = hj[k], oj[k]
    print(' key:', k, '| head type:', type(hv).__name__, 'n=', len(hv) if isinstance(hv,(list,dict)) else hv, '| ours n=', len(ov) if isinstance(ov,(list,dict)) else ov)
lt_h, lt_o = hj.get('last_tick'), oj.get('last_tick')
print(' head last_tick:', json.dumps(lt_h, ensure_ascii=False)[:220])
print(' ours last_tick:', json.dumps(lt_o, ensure_ascii=False)[:220])
print(' head launches tail:', json.dumps(hj.get('launches', [])[-2:], ensure_ascii=False)[:300])
print(' ours launches tail:', json.dumps(oj.get('launches', [])[-2:], ensure_ascii=False)[:300])

h, o = sides('results/token_usage.json')
hj, oj = json.loads(h), json.loads(o)
print('=== token_usage keys:', list(hj))
for k in hj:
    hv, ov = hj[k], oj[k]
    print(' key:', k, '| head:', json.dumps(hv, ensure_ascii=False)[:100])
    print('        ours:', json.dumps(ov, ensure_ascii=False)[:100])
