import json, os, hashlib, subprocess

# S0.5: orders diff-set + D-19 decisions watermark check (bm-b r800)
h = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
acks = set(h.get('orders_ack', []))
all_orders = set(f for f in os.listdir('fleet/orders') if f.startswith('O-') and f.endswith('.md'))
unacked = sorted(all_orders - acks)
print('orders unacked:', unacked if unacked else 'NONE - full sweep MATCH')

state = json.load(open('state.json', encoding='utf-8'))
prev_sha = state.get('last_decisions_sha')

# fresh read from group tree (D-20260930-13: origin blob, zero tree touch)
r = subprocess.run(['git', '-C', 'K:/Fluxgroup/FluxGroup', 'show', 'origin/main:docs/decisions.md'],
                   capture_output=True)
if r.returncode != 0:
    subprocess.run(['git', '-C', 'K:/Fluxgroup/FluxGroup', 'fetch', 'origin'], capture_output=True)
    r = subprocess.run(['git', '-C', 'K:/Fluxgroup/FluxGroup', 'show', 'origin/main:docs/decisions.md'],
                       capture_output=True)
if r.returncode != 0:
    print('D-19: group tree unavailable (S4U window) - fallback local repo probe')
    r2 = subprocess.run(['git', 'show', 'origin/main:docs/decisions.md'], capture_output=True)
    print('local-repo decisions read rc:', r2.returncode)
    doc = r2.stdout if r2.returncode == 0 else None
else:
    doc = r.stdout
if doc:
    cur_sha = hashlib.sha256(doc).hexdigest()
    print('D-19 watermark:', 'MATCH (zero action)' if cur_sha == prev_sha else f'CHANGED prev={str(prev_sha)[:12]} cur={cur_sha[:12]}')
    if cur_sha != prev_sha:
        text = doc.decode('utf-8', errors='replace')
        # emit tail block (dispatch board) for consumption
        print('--- decisions tail (last 60 lines) ---')
        print('\n'.join(text.splitlines()[-60:]))
else:
    print('D-19: unreadable - honest skip, non-blocking')
