# r630 bm-a second-loop resolver: lane faces (sens.jsonl/history = line-union; face/state snapshot = local-side)
import json, subprocess

def stage_lines(path, stage):
    b = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True).stdout
    return b

# append-log union (zero loss; count = |A u B|)
for p in ['results/fund_divlowvol_p1/sens.jsonl', 'results/saturation_engine/history_bm-a.jsonl']:
    b2, b3 = stage_lines(p, 2), stage_lines(p, 3)
    s2 = {ln for ln in b2.split(b'\n') if ln.strip()}
    s3 = {ln for ln in b3.split(b'\n') if ln.strip()}
    union = s2 | s3
    # preserve order: origin rows first, then local-only rows (stable append semantics)
    out = []
    for ln in b2.split(b'\n'):
        if ln.strip() and ln in union:
            out.append(ln); union.discard(ln)
    for ln in b3.split(b'\n'):
        if ln.strip() and ln in union:
            out.append(ln); union.discard(ln)
    data = b'\n'.join(out) + b'\n'
    with open(p, 'wb') as f:
        f.write(data)
    n2, n3 = len({ln for ln in b2.split(b'\n') if ln.strip()}), len({ln for ln in b3.split(b'\n') if ln.strip()})
    print(f'{p}: union {len(out)} rows (origin {n2} / local {n3})')

# lane snapshots: bm-a-owned in-flight daemon faces, local side is live truth
for p in ['results/saturation_engine/face_bm-a.json', 'results/saturation_engine/state_bm-a.json']:
    b3 = stage_lines(p, 3)
    json.loads(b3)
    with open(p, 'wb') as f:
        f.write(b3)
    print(f'{p}: take :3: (bm-a lane live truth)')
