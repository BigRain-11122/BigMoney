# probe nulls.jsonl key-level structure (read-only)
import json, subprocess

def blob(stage, path):
    return subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True).stdout.decode('utf-8')

def keys_of(text):
    out = {}
    dup_lines = 0
    for l in text.splitlines():
        if not l.strip():
            continue
        d = json.loads(l)
        k = d.get('key') or d.get('k')
        if k in out:
            dup_lines += 1
            if out[k] != l:
                out[k] = ('DIFFER', out[k][:80], l[:80])
        else:
            out[k] = l
    return out, dup_lines

o, odup = keys_of(blob(2, 'results/fund_divlowvol_p1/nulls.jsonl'))
t, tdup = keys_of(blob(3, 'results/fund_divlowvol_p1/nulls.jsonl'))
print('OURS unique-keys', len(o), 'intra-dup-lines', odup)
print('THEIRS unique-keys', len(t), 'intra-dup-lines', tdup)
only_o = set(o) - set(t)
only_t = set(t) - set(o)
print('keys only in OURS:', len(only_o), sorted(list(only_o))[:8])
print('keys only in THEIRS:', len(only_t), sorted(list(only_t))[:8])
diffs = [k for k in (set(o) & set(t)) if isinstance(o[k], tuple)]
print('same-key-different-content:', len(diffs), diffs[:4])
# key universe coverage
ko = sorted({d for d in o})
kt = sorted({d for d in t})
print('OURS k-range', ko[0], ko[-1] if ko else None, 'THEIRS k-range', kt[0], kt[-1] if kt else None)
