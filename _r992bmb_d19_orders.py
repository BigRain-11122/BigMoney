# -*- coding: utf-8 -*-
# r992 bm-b: D-19 orders watermark delta consumption probe (watermark moved:
# 1df82bab -> e0dcbd80 on origin/main). Writes analysis face for the round to
# read (console CJK is mojibake-unreliable per GBK wrapper law).
import subprocess, sys, re
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
GRP = r'C:\Fluxgroup\FluxGroup'
r = subprocess.run(['git', '-C', GRP, 'show', 'origin/main:docs/orders.md'],
                  capture_output=True, timeout=120)
text = r.stdout.decode('utf-8', 'replace')
lines = text.splitlines()
recent = [l for l in lines if re.search(r'2026-10-17', l)]
bmb = [l for l in lines if ('bm-b' in l) and re.search(r'2026-10-17', l)]
out = []
out.append('total_lines=%d rows_2026_10_17=%d bmb_rows_today=%d' % (len(lines), len(recent), len(bmb)))
out.append('--- tail 40 lines of orders.md ---')
out.extend(lines[-40:])
out.append('--- bm-b rows dated 2026-10-17 (last 15) ---')
out.extend(bmb[-15:])
with open(r'C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r992bmb_d19_orders_delta.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(out))
print('ORDERS_DELTA_ANALYZED rows_today=%d bmb_today=%d' % (len(recent), len(bmb)))
