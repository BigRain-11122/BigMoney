import io

b = io.open(r'results\_r1110bmc_build_w276_derive.py', encoding='utf-8').read()

# force RAM + GPU from argv (before gpu_face assignment)
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
b = b.replace(anchor, patch)
io.open(r'results\_r1110bmc_build_probe.py', 'w', encoding='utf-8', newline='').write(b)
print('2D sweep probe written')
