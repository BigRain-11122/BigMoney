"""r804 bm-b rebase pick-4 resolver (churn-absorb-2 vs origin).

Recipes per bigmoney-conflict-resolve SKILL.md:
- results/p1d_gates.json: S6 regenerable face -> deep-ts newer-wins, tie->ours(origin)
- results/saturation_engine/history_bm-b.jsonl: bm-b daemon-owned append-only -> line-union zero-loss
Receipt: results/_r804bmb_rebase_resolve2.json
"""
import subprocess, json, re, os

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(ROOT)

def git_bytes(*args):
    r = subprocess.run(['git'] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} rc={r.returncode}: {r.stderr.decode('utf-8','replace')[:300]}")
    return r.stdout

TS = re.compile(rb'20\d\d-\d\d-\d\d[ T]\d\d:\d\d:\d\d')

def ts_max(raw):
    m = TS.findall(raw)
    return max(m) if m else None

out = git_bytes('ls-files', '-u').decode('utf-8', 'replace')
entries = {}
for line in out.strip().splitlines():
    meta, path = line.split('\t', 1)
    mode, sha, stage = meta.split()
    entries.setdefault(path, {})[int(stage)] = sha

receipt = {'round': 'r804', 'pick': 'churn-absorb-2 17d634d61', 'faces': [], 'asserts': []}

for path, shas in sorted(entries.items()):
    b2 = git_bytes('cat-file', 'blob', shas[2]) if 2 in shas else None  # ours=origin
    b3 = git_bytes('cat-file', 'blob', shas[3]) if 3 in shas else None  # theirs=local
    face = {'path': path}
    if path.endswith('.jsonl'):
        lines2 = [l for l in (b2 or b'').split(b'\n') if l.strip()]
        lines3 = [l for l in (b3 or b'').split(b'\n') if l.strip()]
        set2 = set(lines2)
        union = list(lines2) + [l for l in lines3 if l not in set2]
        assert len(union) == len(set(union)), f"dup in {path}"
        assert len(union) >= max(len(lines2), len(lines3)), f"loss in {path}"
        raw = b'\n'.join(union) + b'\n'
        face['recipe'] = 'line-union'
        face['counts'] = [len(lines2), len(lines3), len(union)]
        receipt['asserts'].append(f"{path}: |A|={len(lines2)} |B|={len(lines3)} |AuB|={len(union)} zero-loss")
    else:
        t2, t3 = ts_max(b2 or b''), ts_max(b3 or b'')
        if t3 and (not t2 or t3 > t2):
            chosen, side = b3, 'theirs(local)'
        else:
            chosen, side = b2, 'ours(origin)'
        if path.endswith('.json'):
            try:
                json.loads(chosen.decode('utf-8'))
            except Exception as e:
                raise RuntimeError(f"{path}: chosen side unparseable: {e}")
        face['recipe'] = 'ts-newer-wins'
        face['ts'] = [t2.decode() if t2 else None, t3.decode() if t3 else None]
        face['took'] = side
        raw = chosen
    with open(path, 'wb') as f:
        f.write(raw)
    face['bytes_written'] = len(raw)
    receipt['faces'].append(face)
    print(f"  {path}: {face['recipe']} -> {face.get('took', face.get('counts'))}")

with open('results/_r804bmb_rebase_resolve2.json', 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("resolved:", len(receipt['faces']))
