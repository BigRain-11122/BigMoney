import hashlib, subprocess
raw = subprocess.check_output(['git','-C','K:/Fluxgroup/FluxGroup','show','origin/main:docs/decisions.md'])
print('DEC_SHA=' + hashlib.sha256(raw).hexdigest())
raw_o = subprocess.check_output(['git','-C','K:/Fluxgroup/FluxGroup','show','origin/main:docs/orders.md']).decode('utf-8','replace')
lines = raw_o.splitlines()
print('ORDERS_FILE_LINES=' + str(len(lines)))
ceo = [l for l in lines if 'bm-c' in l and ('\u5f85' in l or '\u7269\u7406' in l)]
print('CEO_PHYS_LINES_MATCHING_BMC=' + str(len(ceo)))
for l in ceo[-10:]:
    print('CEO_ROW: ' + l[:200])
