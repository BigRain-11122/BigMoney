import subprocess, json
def show(ref, path):
    return subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True).stdout
# 1) origin pool N2 shard entries?
pool = json.loads(show('origin/main', 'results/runnable_pool.json'))
n2 = [e for e in pool['entries'] if 'N2-W15' in str(e.get('id', ''))]
out = []
for e in n2:
    out.append({'id': e['id'], 'status': e.get('status'),
                'shards': [{'key': s.get('key'), 'status': s.get('status'),
                            'owner': s.get('owner'), 'owner_since': s.get('owner_since'),
                            'done_at': s.get('done_at')} for s in e.get('shards', [])]})
print("origin N2 entries:", json.dumps(out, ensure_ascii=False, indent=1))
gen = [e for e in pool['entries'] if e.get('id') == 'PERPETUAL-N2-W15-GENERATE'][0]
print("GENERATE ticket_ref head:", str(gen.get('ticket_ref'))[:200])
# 2) runner diff HEAD vs origin
r = subprocess.run(['git', 'diff', 'HEAD', 'origin/main', '--', 'scripts/perpetual_faces_n2.py'],
                    capture_output=True)
print("=== runner diff (HEAD vs origin) ===")
print(r.stdout.decode('utf-8', errors='replace')[:4000])
print("=== diff stat ===")
r2 = subprocess.run(['git', 'diff', '--stat', 'HEAD', 'origin/main', '--', 'scripts/perpetual_faces_n2.py'],
                     capture_output=True)
print(r2.stdout.decode())
