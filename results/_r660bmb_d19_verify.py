# r660 bm-b S0.5: D-19 raw-blob subprocess re-verify (PS-pipe artifact dispel, r660 bm-a law)
import subprocess, hashlib, sys, os

clone = sys.argv[1]
def blob_sha(path):
    p = subprocess.run(['git', '-C', clone, 'show', 'origin/main:' + path],
                       capture_output=True)
    if p.returncode != 0:
        return None, p.stderr.decode('utf-8', 'replace')[:200]
    return hashlib.sha256(p.stdout).hexdigest().upper(), None

dsha, derr = blob_sha('docs/decisions.md')
osha, oerr = blob_sha('docs/orders.md')
out = []
out.append(f'decisions_blob_sha256: {dsha} {derr or ""}')
out.append(f'orders_blob_sha256: {osha} {oerr or ""}')
wm_dec = 'EB14B510D304A1D0A30175447CF9360D6BAB6DC20972CEEBCE35D47EF8935BFA'
wm_ord = '82A0CEF99F147C6F6D14A0C2233A44309768C548312F9069F7C33CF6A2AA311A'
out.append(f'decisions MATCH={dsha == wm_dec}  orders MATCH={osha == wm_ord}')

# if changed, extract recent rows relevant to BigMoney/quant for consumption
import re
p = subprocess.run(['git', '-C', clone, 'show', 'origin/main:docs/decisions.md'],
                   capture_output=True)
text = p.stdout.decode('utf-8', errors='replace')
lines = text.splitlines()
out.append(f'decisions lines: {len(lines)}')
if dsha != wm_dec:
    rel = [(i, ln) for i, ln in enumerate(lines) if re.search(r'(?i)bigmoney|quant|bm-[abc]', ln)]
    out.append(f'RELEVANT: {len(rel)}')
    for i, ln in rel:
        out.append(f'L{i+1}: {ln[:500]}')
    out.append('---TAIL 25---')
    for i, ln in enumerate(lines[-25:], start=len(lines)-25+1):
        out.append(f'L{i}: {ln[:500]}')
# CEO orders.md physical-items section relevant lines (always check per protocol)
p2 = subprocess.run(['git', '-C', clone, 'show', 'origin/main:docs/orders.md'], capture_output=True)
ot = p2.stdout.decode('utf-8', errors='replace')
for i, ln in enumerate(ot.splitlines(), 1):
    if re.search(r'(?i)bigmoney|quant|bm-b', ln):
        out.append(f'ORDERS L{i}: {ln[:500]}')

with open('results/_r660bmb_d19_out.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('WROTE results/_r660bmb_d19_out.txt lines:', len(out))
