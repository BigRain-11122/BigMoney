import subprocess
G = r'C:\Program Files\Git\cmd\git.exe'
R = r'C:\Users\sjs20\Desktop\FluxGroup'
subprocess.run([G, '-C', R, 'fetch', 'origin'], capture_output=True)
for doc, out in (('docs/decisions.md', 'dec'), ('docs/orders.md', 'ord')):
    r = subprocess.run([G, '-C', R, 'show', f'origin/main:{doc}'], capture_output=True)
    path = f'results/_r964bma_group_{out}.txt'
    open(path, 'wb').write(r.stdout)
    print(doc, len(r.stdout), 'bytes ->', path)
