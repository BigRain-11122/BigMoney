import subprocess, json

def show_blobs(rev, path):
    out = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True).stdout
    return out

# 1) attribution check on the W20 finalize product at e772def0d
blob = show_blobs('e772def0d', 'results/perpetual_faces/n1_w20_results.json')
d = json.loads(blob)
print('audit.machine =', d.get('audit', {}).get('machine'))
print('K merged =', d['null_pool_cumulative']['merged']['n_values'])
print('ledger total =', d['science_gates']['ledger']['total'], 'prev =',
      d['science_gates']['ledger']['prev_total'])
print('batch =', d['batch'])
print('blob sha16 =', subprocess.run(
    ['git', 'rev-parse', 'e772def0d:results/perpetual_faces/n1_w20_results.json'],
    capture_output=True, text=True).stdout.strip()[:16])

# 2) what c209aa962 did to the W20 prereg: diff vs its parent
diff = subprocess.run(['git', 'show', 'c209aa962', '--', 'research/PERPETUAL_N1_W20_PREREG.md'],
                      capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
print('=== prereg diff lines (c209aa962) ===')
for ln in diff.splitlines():
    if ln.startswith('+') or ln.startswith('-'):
        print(ln[:170])
