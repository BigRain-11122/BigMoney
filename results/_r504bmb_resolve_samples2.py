"""r504 bm-b: pool_core_samples.jsonl conflict union (r503 recipe, reusable)."""
import re, json

p = r'results/pool_core_samples.jsonl'
raw = open(p, 'rb').read().decode('utf-8')
blocks = re.findall(r'(?ms)^<<<<<<< HEAD\n(.*?)\n?=======\n(.*?)\n?>>>>>>> [^\n]*\n', raw)
print('n_blocks', len(blocks))
out = []
for ours, theirs in blocks:
    lines = [l for l in (ours + '\n' + theirs).split('\n') if l.strip()]
    seen, kept = set(), []
    for l in lines:
        if l not in seen:
            seen.add(l)
            kept.append(l)
    kept.sort(key=lambda l: re.search(r'"ts": "([^"]+)"', l).group(1))
    out.extend(kept)
res = re.sub(r'(?ms)^<<<<<<< HEAD\n.*?\n?>>>>>>> [^\n]*\n',
             lambda m: '\n'.join(out) + '\n', raw, count=0)
ls = [l for l in res.splitlines() if l.strip()]
for l in ls:
    json.loads(l)
assert not re.findall(r'<<<<<<<|>>>>>>>', res)
open(p, 'wb').write(res.encode('utf-8'))
print('resolved_lines', len(out), 'total_lines', len(ls), 'PARSE_OK')
