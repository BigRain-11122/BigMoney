"""r637 bm-a: verify local 3of4 artifact vs bm-c delivered origin blob (byte identity)."""
import subprocess, hashlib, os

local = open('results/mass_trial/w2_judge_shard_3of4.jsonl', 'rb').read()
r = subprocess.run(['git', 'show', 'origin/main:results/mass_trial/w2_judge_shard_3of4.jsonl'],
                   capture_output=True)
origin = r.stdout
print('local bytes:', len(local), 'sha256:', hashlib.sha256(local).hexdigest()[:16])
print('origin bytes:', len(origin), 'sha256:', hashlib.sha256(origin).hexdigest()[:16])
print('BYTE-IDENTICAL:', local == origin)
if local != origin:
    # count differing rows by cell_id for diagnosis
    import json
    def rows(b):
        out = {}
        for line in b.decode('utf-8').splitlines():
            line = line.strip()
            if line:
                d = json.loads(line)
                out[d['cell_id']] = json.dumps(d, sort_keys=True)
        return out
    L, O = rows(local), rows(origin)
    print('rows local/origin:', len(L), len(O))
    diff = [k for k in set(L) | set(O) if L.get(k) != O.get(k)]
    print('differing cell_ids:', len(diff), diff[:5])
    if diff:
        k = diff[0]
        print('SAMPLE local :', L.get(k, 'MISSING')[:300])
        print('SAMPLE origin:', O.get(k, 'MISSING')[:300])
