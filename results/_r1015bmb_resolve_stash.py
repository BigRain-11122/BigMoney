"""r1015 stash-pop conflict resolution (3 daemon faces, per-machine law)."""
import io
import json
import os
import re

os.chdir(r'C:\Fluxgroup\FluxGroup\quant\bigmoney')
CON = re.compile(r'<<<<<<< Updated upstream\r?\n(.*?)=======\r?\n(.*?)>>>>>>> Stashed changes\r?\n', re.S)


def blocks(t):
    return CON.findall(t)


# 1. machine-health.json: origin (Updated upstream) blocks = newer bm-c rows
p = r'fleet\machine-health.json'
t = io.open(p, encoding='utf-8', errors='replace').read()
n = len(blocks(t))
t2 = CON.sub(lambda m: m.group(1), t)  # keep origin side
io.open(p, 'w', encoding='utf-8', newline='').write(t2)
print('machine-health: %d conflict blocks -> origin-wins; bm-b rows present: %d' % (
    n, t2.count('"bm-b"')))
try:
    json.loads(io.open(p, encoding='utf-8').read())
    print('machine-health JSON-OK')
except Exception as e:
    print('machine-health JSON-FAIL', str(e)[:100])

# 2. token_usage.json: whole-file conflict -> per-machine union
p = r'results\token_usage.json'
t = io.open(p, encoding='utf-8', errors='replace').read()
bl = blocks(t)
o_txt, m_txt = bl[0] if bl else (t, t)
try:
    o = json.loads(o_txt)
    m = json.loads(m_txt)
    merged = m if (m.get('generated', '') or '') >= (o.get('generated', '') or '') else o
    machines = dict(o.get('machines', {}))
    machines.update(m.get('machines', {}))  # my side (bm-b) rows win for keys I carry
    merged['machines'] = machines
    # l2_local_llm union (by_cmd additive)
    l2o = o.get('l2_local_llm', {})
    l2m = m.get('l2_local_llm', {})
    if l2o and l2m:
        merged_l2 = dict(l2m)
        for k, v in l2o.items():
            if k == 'by_cmd':
                bc = dict(merged_l2.get('by_cmd', {}))
                for kk, vv in v.items():
                    bc[kk] = bc.get(kk, 0) + (vv if kk not in merged_l2.get('by_cmd', {}) else 0)
                merged_l2['by_cmd'] = bc
            elif isinstance(v, (int, float)) and k in ('legs_total', 'tokens_est_total'):
                merged_l2[k] = max(merged_l2.get(k, v), v)
        merged['l2_local_llm'] = merged_l2
    io.open(p, 'w', encoding='utf-8', newline='').write(json.dumps(merged, ensure_ascii=False, indent=2))
    print('token_usage: union OK, machines keys:', sorted(merged.get('machines', {}).keys()))
except Exception as e:
    print('token_usage union FAILED, keep origin side:', str(e)[:120])
    t2 = CON.sub(lambda mm: mm.group(1), t)
    io.open(p, 'w', encoding='utf-8', newline='').write(t2)

# 3. watermark_red.json: single face, mine (03:55 bm-b) newer than origin (03:42 bm-c)
p = r'results\watermark_red.json'
t = io.open(p, encoding='utf-8', errors='replace').read()
t2 = CON.sub(lambda m: m.group(2), t)  # keep stashed (mine)
io.open(p, 'w', encoding='utf-8', newline='').write(t2)
print('watermark_red: mine-wins; JSON-OK' if (lambda x: (json.loads(x), True)[1])(io.open(p, encoding='utf-8').read()) else 'JSON-FAIL')
