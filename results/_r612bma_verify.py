import json, subprocess

# 1) X2 product integrity
rows = 0
bad = 0
with open('results/fund_quality_p1/cells_QUALITY-ROE_x2.jsonl', 'rb') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        rows += 1
        try:
            r = json.loads(line)
            if not isinstance(r, dict):
                bad += 1
        except Exception:
            bad += 1
cont = json.load(open('results/fund_quality_p1/cont_QUALITY-ROE_x2.json', encoding='utf-8'))
print('cells_x2 rows=%d bad=%d cont_keys=%s' % (rows, bad, sorted(cont.keys())[:8]))

# 2) origin vs local ts for shared regen faces
for path in ('results/compute_audit.json', 'results/regime_state.json', 'docs/daily_report/REPORT-2026-10-03.md'):
    try:
        o = subprocess.run(['git', 'show', 'origin/main:' + path], capture_output=True)
        ot = o.stdout.decode('utf-8', errors='replace')
        l = open(path, encoding='utf-8', errors='replace').read()
        import re
        mo = re.search(r'"ts": "([^"]+)"', ot) or re.search(r'2026-10-03T[0-9:]+', ot)
        ml = re.search(r'"ts": "([^"]+)"', l) or re.search(r'2026-10-03T[0-9:]+', l)
        print('%s | origin_ts=%s local_ts=%s' % (path, mo.group(1) if mo else '?', ml.group(1) if ml else '?'))
    except Exception as e:
        print(path, 'err', e)
