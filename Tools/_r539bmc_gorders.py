# r539 bm-c group-orders watermark probe (r537 algorithm pin: SHA-1 40hex uppercase)
import hashlib, subprocess
CREATE_NO_WINDOW = 0x08000000
G = r"K:\Fluxgroup\FluxGroup"
subprocess.run(['git', '-C', G, 'fetch', 'origin'], capture_output=True, creationflags=CREATE_NO_WINDOW)
r = subprocess.run(['git', '-C', G, 'show', 'origin/main:docs/orders.md'], capture_output=True, creationflags=CREATE_NO_WINDOW)
if r.returncode != 0 or not r.stdout:
    print('GORDERS_READ_FAIL rc=%d' % r.returncode)
    raise SystemExit(2)
h = hashlib.sha1(r.stdout).hexdigest().upper()
print('GROUP_ORDERS_SHA1=' + h)
print('MATCH_3BF0F16E=' + str(h.startswith('3BF0F16E')).lower())
