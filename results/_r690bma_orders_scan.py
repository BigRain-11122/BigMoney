import json, os, subprocess, sys
# r690 bm-a S0.5 orders diff probe (same-form set compare per r477/r646)
repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # results/ -> repo root
orders_dir = os.path.join(repo, 'fleet', 'orders')
# live set from origin blob (D-19 style, avoid stale tree faces where cheap): use working tree (just merged/verified)
orders_files = sorted(f for f in os.listdir(orders_dir) if f.startswith('O-') and f.endswith('.md'))
hb_path = os.path.join(repo, 'fleet', 'machines', 'bm-a.json')
with open(hb_path, 'r', encoding='utf-8') as fh:
    hb = json.load(fh)
acked = set(hb.get('orders_ack', []))
unacked = [f for f in orders_files if f not in acked]
extra = [a for a in acked if a not in orders_files and a != 'README.md']
print(json.dumps({
    'orders_total': len(orders_files),
    'acked_total': len(acked),
    'unacked': unacked,
    'ack_extra_nonexistent': extra,
    'round_no_state': None,
}, ensure_ascii=False, indent=1))
# state round_no
sp = os.path.join(repo, 'state-bm-a.json')
if os.path.exists(sp):
    with open(sp, 'r', encoding='utf-8') as fh:
        st = json.load(fh)
    print('state_round_no:', st.get('round_no'), 'next:', st.get('next_task_hint', st.get('next')))
