# r1080 bm-c run-state pass v2: positional parse (col0=taskname, col1=next, col2=state)
import subprocess, json, csv, io

r = subprocess.run(['schtasks', '/query', '/fo', 'CSV'], capture_output=True)
txt = r.stdout.decode('gbk', 'replace')
rows = list(csv.reader(io.StringIO(txt)))
m = {}
for row in rows[1:]:
    if len(row) >= 3:
        m[row[0].lstrip('\\')] = row[2]

with open(r'results\_r1080bmc_taskaudit.json', encoding='utf-8') as f:
    audit = json.load(f)
for e in audit['rows']:
    e['run_state'] = m.get(e['task'], 'MISSING')
with open(r'results\_r1080bmc_taskaudit.json', 'w', encoding='utf-8') as f:
    json.dump(audit, f, ensure_ascii=False, indent=1)
print('RUN-STATE-PASS-V2')
for e in audit['rows']:
    print('%s :: run_state=%s' % (e['task'], e.get('run_state')))
