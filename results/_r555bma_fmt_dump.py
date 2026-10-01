"""r555 helper: dump N1_BANDS[45]/[46] and WAVE_CONFIGS[45] verbatim for W47 adaptation."""
import subprocess

pf = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces.py']).decode('utf-8')
for w in (45, 46):
    i = pf.find('%d: {' % w)
    if i < 0:
        print('N1_BANDS[%d] not found' % w)
        continue
    k = pf.rfind('\n\n', 0, i)
    j = pf.find('\n    },', i)
    print('==== N1_BANDS[%d] ====' % w)
    print(pf[max(k, i - 700):j + 8])
    print()

n1 = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces_n1.py']).decode('utf-8')
i = n1.find('45: {"batch"')
j = n1.find('46: {"batch"')
print('==== WAVE_CONFIGS[45] verbatim ====')
print(n1[i - 900:j])
