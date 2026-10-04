# r660 bm-b S0.5: consume D-19 decisions.md change (origin blob) + CEO orders.md physical-items check
import hashlib, sys, re

d = open(sys.argv[1] + '/docs/decisions.md', 'rb').read()
o = open(sys.argv[1] + '/docs/orders.md', 'rb').read()
print('decisions_sha256:', hashlib.sha256(d).hexdigest())
print('orders_sha256:', hashlib.sha256(o).hexdigest())
text = d.decode('utf-8', errors='replace')
lines = text.splitlines()
print('decisions total lines:', len(lines))
# relevance: BigMoney / quant / bm-b / bm-a / bm-c rows
rel = [(i, ln) for i, ln in enumerate(lines) if re.search(r'(?i)bigmoney|quant|bm-[abc]', ln)]
print('RELEVANT LINES:', len(rel))
for i, ln in rel:
    print(f'L{i+1}: {ln[:400]}')
print('---TAIL 40---')
for i, ln in enumerate(lines[-40:], start=len(lines)-40+1):
    print(f'L{i}: {ln[:400]}')
print('---ORDERS.MD RELEVANT---')
ot = o.decode('utf-8', errors='replace')
for i, ln in enumerate(ot.splitlines(), 1):
    if re.search(r'(?i)bigmoney|quant|bm-b', ln):
        print(f'L{i}: {ln[:400]}')
