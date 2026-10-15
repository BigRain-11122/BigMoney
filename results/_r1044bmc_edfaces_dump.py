import io, re
src = io.open(r'results\_w249bmc_derive_editor.py', encoding='utf-8').read()
out = []
for m in re.finditer(r'freeze 窗', src):
    out.append(repr(src[m.start()-80:m.start()+140]))
for m in re.finditer(r'live-read', src):
    out.append('LIVEREAD ' + repr(src[m.start()-100:m.start()+80]))
io.open(r'results\_r1044bmc_edfaces.txt', 'w', encoding='utf-8').write('\n\n'.join(out))
print('hits', len(out))
