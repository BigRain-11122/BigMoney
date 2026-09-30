import subprocess, re
r = subprocess.run(['rg', '-n', '--encoding', 'utf-8', '2029410[0-9]|2029411[0-4]',
                    'scripts', 'results', 'research', 'fleet'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
print('rg band scan:', r.stdout[:800] or 'CLEAN (no hits)')

src = open('scripts/etf_ops_bp1.py', encoding='utf-8').read()
print('runner size', len(src))
for m in re.finditer(r'^(def |class )([A-Za-z_0-9]+)', src, re.M):
    print(m.group(1).strip(), m.group(2))
