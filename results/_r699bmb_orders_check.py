# r699 bm-b S0.5 orders full-set diff (r477 full-name caliber, r696 tree-ish form)
import json, subprocess, sys
out = subprocess.run(['git','ls-tree','--name-only','HEAD:fleet/orders'], capture_output=True, cwd=r'C:\Fluxgroup\FluxGroup\quant\bigmoney')
files = [l for l in out.stdout.decode('utf-8').splitlines() if l.strip().endswith('.md') and l.strip().startswith('O-')]
hb = json.load(open(r'C:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-b.json', encoding='utf-8'))
ack = set(hb.get('orders_ack', []))
fs = set(files)
unacked = sorted(fs - ack)
extra = sorted(ack - fs)
print('orders_in_git=%d ack=%d unacked=%d ack_extra=%d' % (len(fs), len(ack), len(unacked), len(extra)))
for u in unacked: print('UNACKED:', u)
for e in extra: print('ACK_EXTRA:', e)
