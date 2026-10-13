import subprocess, json, re, os

def rg(pat, path):
    r = subprocess.run(['rg', '-n', pat, path], capture_output=True, text=True, encoding='utf-8', errors='replace')
    return [l for l in r.stdout.strip().splitlines() if l]

# 1) W236 row presence in the five faces
pf = rg(r'236', 'scripts/perpetual_faces.py')
print('perpetual_faces.py 236 raw hits:', len(pf))
for l in pf[:4]:
    print('  ', l[:170])

pfn = rg(r'WAVE_CONFIGS|W236', 'scripts/perpetual_faces_n1.py')
print('perpetual_faces_n1.py WAVE_CONFIGS/W236 hits:', len(pfn))
for l in pfn[:8]:
    print('  ', l[:170])

# 2) W235 row format reference (how a registered wave looks)
w235 = rg(r'W235', 'scripts/perpetual_faces.py')
print('perpetual_faces.py W235 hits:', len(w235))
for l in w235[:5]:
    print('  ', l[:170])

# 3) probe receipt for W236 (ADMIT evidence)
for p in ['results/_w236bma_20261014_probe_receipt.json',
          'results/_w236bma_20261014_probe.py']:
    print(p, 'exists:', os.path.exists(p))

# 4) law band registry location hints: search for where band rows live
lb = rg(r'law band row|N1_BANDS|SEED_REGISTRY', 'scripts/perpetual_faces.py')
print('band registry hints:', len(lb))
for l in lb[:6]:
    print('  ', l[:170])
