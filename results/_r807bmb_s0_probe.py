# find the malformed jsonl line (read-only probe)
import json, subprocess

REPO = r'C:\\Fluxgroup\\FluxGroup\\quant\\bigmoney'
def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True, cwd=REPO)
    return r.stdout

for p in ['results/t24_prospect_paper_cells.jsonl', 'results/x2_watch_log.jsonl']:
    for stage in (2, 3):
        b = blob(stage, p)
        lines = [l for l in b.decode('utf-8', errors='replace').splitlines() if l.strip()]
        bad = []
        for i, l in enumerate(lines):
            try:
                json.loads(l)
            except Exception:
                bad.append((i, l))
        print(p, 'stage', stage, 'lines', len(lines), 'bad', len(bad))
        for i, l in bad[:3]:
            print('  BAD idx', i, repr(l[:250]))
