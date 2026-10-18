import subprocess, sys, io

# regenerate probe from the FIXED builder
b = io.open(r'results\_r1110bmc_build_w276_derive.py', encoding='utf-8').read()
anchor = 'try:\n    _nvs = subprocess.run(["nvidia-smi"'
assert b.count(anchor) == 1
patch = '''import sys as _sys
RAM = float(_sys.argv[1]) if len(_sys.argv) > 1 else RAM
ram_face = "~%.1fGB" % RAM
ram_anchor = "~%.1fG" % RAM
if len(_sys.argv) > 3:
    _util, _vram = _sys.argv[2], _sys.argv[3]
    vram_g = "%.1fG" % (int(_vram) / 1024.0)
    gpu_face = "nvidia-smi \\u5b9e\\u8bfb %s%%\\u00b7%s VRAM \\u5360\\u7528\\u00b7MV \\u8f66\\u9053\\u5df2\\u6536\\u5b98 GPU idle \\u56de\\u91ca" % (_util, vram_g)
''' + anchor
io.open(r'results\_r1110bmc_build_probe.py', 'w', encoding='utf-8', newline='').write(b.replace(anchor, patch))
print('probe regenerated from fixed builder')

results = []
vals = ['0.05', '0.5', '1.4', '2.1', '3.2', '3.25', '3.3', '3.35', '3.5', '3.6', '3.9',
        '3.95', '4.0', '4.05', '4.2', '4.35', '4.4', '4.44', '4.45', '5.0', '5.9']
for ram in vals:
    p = subprocess.run([sys.executable, r'results\_r1110bmc_build_probe.py', ram],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    tail = (p.stdout + p.stderr).strip().splitlines()
    status = 'PASS' if any('BUILD OK' in ln for ln in tail) else 'FAIL'
    err = ''
    for ln in tail:
        if 'SIM' in ln and ('missing' in ln or 'present' in ln or 'FAIL' in ln):
            err = ln.strip()[:130]
            break
    if not err and status == 'FAIL':
        err = (tail[-1].strip()[:130] if tail else '')
    results.append('RAM=%-5s -> %s %s' % (ram, status, err))
io.open(r'results\_r1110bmc_sweep.txt', 'w', encoding='utf-8').write('\n'.join(results))
print('\n'.join(results))
fails = [r for r in results if 'FAIL' in r]
print('SWEEP RESULT: %d/%d PASS' % (len(results) - len(fails), len(results)))
