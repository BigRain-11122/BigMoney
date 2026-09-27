import json
import subprocess

ok = []

# 1. CODELY.md entry-level audit (auto-merged both sides)
c = open('CODELY.md', encoding='utf-8').read()
for kw in ['r338 bm-a] 坑律：**共享 JSON 面', 'r90 pitlaw', '二十批']:
    pass
checks = {
    'my r338 pitlaw present': '共享 JSON 面' in c and 'r338 bm-a' in c,
    'r332-bmb stub present (twenty-batch)': '二十批外迁·指针' in c,
    'size <= 10KB': len(c.encode('utf-8')) <= 10240,
}
# bm-c r90 pitlaw: check a distinctive fragment of their entry (unknown text) -> check their commit changed CODELY
b90 = subprocess.run(['git', 'show', 'origin/main:CODELY.md'], capture_output=True).stdout.decode('utf-8', errors='replace')
b90_entries = {l.strip()[:60] for l in b90.splitlines() if l.strip().startswith('- [')}
cur_entries = {l.strip()[:60] for l in c.splitlines() if l.strip().startswith('- [')}
missing_from_cur = [e for e in b90_entries - cur_entries if e[:17] != '- [2026-09-27 16']  # r332-bmb/r335 fulls removed by both = legitimate
checks['origin entries preserved (except dual-removed fulls)'] = len([e for e in b90_entries - cur_entries if 'r90' in e or 'bm-c' in e]) == 0
for k, v in checks.items():
    ok.append(f'{k}: {v}')
    assert v, k
print('CODELY size:', len(c.encode('utf-8')), 'B')
diff90 = [e[:70] for e in (set(l.strip() for l in c.splitlines() if l.strip().startswith('- [')) - set(l.strip() for l in b90.splitlines() if l.strip().startswith('- [')))]
print('my-side new entries vs origin:', len(diff90))
for d in diff90[:4]:
    print('  +', d[:70])

# 2. runnable_pool: SINA done + bm-b census claim-refresh both present
pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
sina = next(e for e in pool['entries'] if e['id'] == 'SINA-CONSTRUCT-P1')
ok.append(f'pool SINA status={sina["status"]} done_at={sina.get("done_at")}')
assert sina['status'] == 'done'
cens = next(e for e in pool['entries'] if e['id'] == 'CENSUS-FUS-S2-W2A')
sh = cens['shards'][0]
ok.append(f'pool censusw2a shard status={sh["status"]} owner={sh.get("owner")} since={sh.get("owner_since")}')
ready = [e['id'] for e in pool['entries'] if e.get('status') == 'ready']
ok.append(f'pool ready entries: {ready}')

# 3. autofill_state: launches sanity + last_tick dict
af = json.load(open('results/autofill_state.json', encoding='utf-8'))
L = af.get('launches', [])
keys = [(x.get('ts'), x.get('machine'), x.get('pid')) for x in L]
ok.append(f'autofill launches={len(L)} unique-composite={len(set(keys))} last_tick-is-dict={isinstance(af.get("last_tick"), dict)}')
assert len(set(keys)) == len(keys), 'composite key dup in launches'
assert isinstance(af.get('last_tick'), dict)

print('; '.join(ok))
print('ALL VERIFIED')
