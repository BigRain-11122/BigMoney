import hashlib
import subprocess

# r706 law: byte-precise hash via python subprocess capture - no PS pipeline
repo = r'C:\Users\sjs20\AppData\Local\Temp\d19_r707'
out = subprocess.run(['git', '-C', repo, 'show', 'origin/main:docs/decisions.md'],
                     capture_output=True).stdout
print('decisions.md sha256:', hashlib.sha256(out).hexdigest())
with open(r'C:\Users\sjs20\AppData\Local\Temp\d19_decisions_raw.md', 'wb') as f:
    f.write(out)
out2 = subprocess.run(['git', '-C', repo, 'show', 'origin/main:docs/orders.md'],
                      capture_output=True).stdout
print('orders.md sha256:', hashlib.sha256(out2).hexdigest())
with open(r'C:\Users\sjs20\AppData\Local\Temp\d19_orders_raw.md', 'wb') as f:
    f.write(out2)
