import subprocess

r = subprocess.run(['git', '-C', r'C:\Fluxgroup\FluxGroup', 'show', 'origin/main:docs/orders.md'],
                   capture_output=True, timeout=60)
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')[-200:]
new_bytes = r.stdout
with open(r'results\_r975bmb_orders_fresh.md', 'wb') as f:
    f.write(new_bytes)

with open(r'results\_r973bmb_orders_fresh.md', 'rb') as f:
    old_bytes = f.read()

old_lines = old_bytes.splitlines()
new_lines = new_bytes.splitlines()
old_set = set(old_lines)
new_set = set(new_lines)
added = [l for l in new_lines if l not in old_set]
removed = [l for l in old_lines if l not in new_set]

out = []
out.append('old_sha1_view_bytes %d new_bytes %d' % (len(old_bytes), len(new_bytes)))
out.append('added_lines %d removed_lines %d' % (len(added), len(removed)))
out.append('--- ADDED (verbatim) ---')
for l in added:
    out.append(l.decode('utf-8', 'replace'))
out.append('--- REMOVED (verbatim) ---')
for l in removed:
    out.append(l.decode('utf-8', 'replace'))
with open(r'results\_r975bmb_orders_delta.txt', 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(out))
print('ASCII_OK added=%d removed=%d written=results/_r975bmb_orders_delta.txt' % (len(added), len(removed)))
