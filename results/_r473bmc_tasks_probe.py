import json, glob, os, io
out = io.open(r'results\_r473bmc_tasks.txt', 'w', encoding='utf-8')
opens, claimed = [], []
for f in glob.glob(r'fleet/tasks/*.json'):
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        out.write(f'SKIP {f}: parse error {e}\n')
        continue
    s = d.get('status', '')
    t = os.path.basename(f)
    if s == 'open':
        opens.append(t)
    if s in ('claimed', 'in_progress'):
        claimed.append((t, s, d.get('claimed_by', '')))
    out.write(f'{t}: status={s} claimed_by={d.get("claimed_by","")}\n')
out.write(f'SUMMARY open_count={len(opens)} claimed_count={len(claimed)}\n')
out.close()
