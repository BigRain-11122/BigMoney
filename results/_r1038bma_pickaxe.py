import subprocess
REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
G = r'C:\Program Files\Git\cmd\git.exe'
for s in ('262: {"a"', '261: {"a"'):
    r = subprocess.run([G, '-C', REPO, 'log', '--format=%H', '-S', s,
                        '--', 'scripts/perpetual_faces.py'],
                       capture_output=True, text=True)
    print(s, '->', r.stdout.strip()[:12], 'rc', r.returncode)
r = subprocess.run([G, '-C', REPO, 'log', '--diff-filter=A', '--format=%H',
                    '--', 'research/PERPETUAL_N1_W263_PREREG.md'],
                   capture_output=True, text=True)
print('w263 prereg add:', r.stdout.strip()[:12])
r = subprocess.run([G, '-C', REPO, 'log', '--diff-filter=A', '--format=%H',
                    '--', 'results/_w263bma_20261017_probe_receipt.json'],
                   capture_output=True, text=True)
print('w263 receipt add:', r.stdout.strip()[:12])
r = subprocess.run([G, '-C', REPO, 'log', '--diff-filter=A', '--format=%H',
                    '--', 'research/PERPETUAL_N1_W262_PREREG.md'],
                   capture_output=True, text=True)
print('w262 prereg add:', r.stdout.strip()[:12])
