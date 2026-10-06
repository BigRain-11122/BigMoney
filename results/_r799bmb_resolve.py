# r799 bm-b rebase resolver: 4 UU faces, snapshot take-new-by-ts law (r188/R208 lineage; r798 receipt precedent)
# rebase semantics: stage2=ours=base=origin(bm-c r659), stage3=theirs=own df5ff06d3 replay
import subprocess, json, datetime, hashlib

def git(args, check=True):
    r = subprocess.run(['git'] + args, capture_output=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {args} rc={r.returncode}: {r.stderr.decode('utf-8','replace')[:200]}")
    return r

def blob(stage, path):
    return git(['cat-file', '-p', f':{stage}:{path}']).stdout

# recipes: take-new-by-content-ts
# attrition_guard_scan: own 06:37:34 > bm-c 06:30:12 -> theirs(stage3)
# daily_scorecard: bm-c 06:09:41 > own 05:05:44 stale residue -> ours(stage2)
# paper_export x2: bm-c 06:12:04 > own 05:52:26 dead-r797 residue -> ours(stage2)
RECIPES = [
    ('results/_attrition_guard_scan.json', 'theirs', 'take-new-own 06:37:34 > bm-c 06:30:12'),
    ('results/daily_scorecard.json', 'ours', 'take-new-bm-c 06:09:41 > own 05:05:44 stale residue'),
    ('results/paper_export/export-2026-09-30.json', 'ours', 'take-new-bm-c 06:12:04 > own 05:52:26 dead-r797 residue; regime_guard=enforce per 2026-10-01 date-gate law'),
    ('results/paper_export/latest.json', 'ours', 'take-new-bm-c mirror of export-2026-09-30'),
]

receipt = {"round": "r799", "machine": "bm-b", "law": "snapshot take-new-by-ts (r188/R208; r798 receipt precedent)",
           "rebase_semantics": "stage2=ours=origin base (bm-c r659 absorb), stage3=theirs=own df5ff06d3",
           "faces": [], "ts": datetime.datetime.now().astimezone().isoformat(timespec='seconds')}

for path, side, note in RECIPES:
    git(['checkout', f'--{side}', '--', path])
    chosen = blob(2 if side == 'ours' else 3, path)
    wt = open(path, 'rb').read()
    assert wt == chosen, f'{path}: worktree != chosen stage blob'
    json.loads(wt.decode('utf-8'))  # parse-verify before add (r185 law)
    git(['add', path])
    receipt['faces'].append({"path": path, "recipe": f'take-{side}', "note": note,
                             "sha16": hashlib.sha256(wt).hexdigest()[:16]})
    print(f'resolved {path} -> take-{side} ({note})')

json.dump(receipt, open('results/_r799bmb_rebase_resolve.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
# remaining UU check
u = git(['ls-files', '-u'], check=False).stdout.decode('utf-8', 'replace')
print('remaining UU:', len([l for l in u.splitlines() if l.strip()]))
