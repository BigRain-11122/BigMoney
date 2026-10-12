import subprocess, json, hashlib
r = subprocess.run(['git', '-C', 'K:/Fluxgroup/FluxGroup', 'show', 'origin/main:docs/orders.md'], capture_output=True)
txt = r.stdout.decode('utf-8', errors='replace')
d = json.load(open('state-bm-c.json', encoding='utf-8'))
state_sha = d.get('last_orders_sha')
cur_sha = hashlib.sha256(r.stdout).hexdigest()
lines = txt.splitlines()
out = []
out.append('state_orders_sha: %s' % state_sha)
out.append('current_sha: %s' % cur_sha)
out.append('match: %s' % (state_sha == cur_sha))
# find dispatch board rows addressed to bm-c / BigMoney / quant
hits = []
for i, ln in enumerate(lines):
    if ('bm-c' in ln or 'BigMoney' in ln or 'quant' in ln or '回测' in ln or '满载' in ln) and ln.strip().startswith('|'):
        hits.append('L%d: %s' % (i + 1, ln[:400]))
out.append('--- bm-c/BigMoney-relevant rows (%d) ---' % len(hits))
out.extend(hits[-30:])
# tail timestamps scan: rows added today after 15:00
recent = [ln[:200] for ln in lines if ln.strip().startswith('|') and ('10-12 1' in ln or '10-12 2' in ln)]
out.append('--- today 1x-2x rows (%d) ---' % len(recent))
out.extend(recent[-25:])
open('results/_r940bmc_ord_delta_view.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written', len(out), 'lines')
