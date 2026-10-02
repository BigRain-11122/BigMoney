import subprocess
o = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces.py'], text=True, encoding='utf-8')
print('W68 N1_BANDS row on origin:', '68: {"a": (179_004' in o)
c = subprocess.check_output(['git', 'show', 'origin/main:research/PERPETUAL_FACES.md'], text=True, encoding='utf-8')
print('W68 canon row on origin:', 'N1 \u6ce268\uff08' in c)
n1 = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces_n1.py'], text=True, encoding='utf-8')
print('W68 WAVE_CONFIGS on origin:', '68: {"batch": "PERPETUAL-N1-W68"' in n1)
print('W68 selftest leg on origin:', 'W68 materializer face' in n1)
