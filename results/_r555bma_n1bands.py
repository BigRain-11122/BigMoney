"""r555 helper: locate N1_BANDS dict in scripts/perpetual_faces.py and dump W44-46 entries."""
import subprocess

pf = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces.py']).decode('utf-8')
i = pf.find('N1_BANDS')
print('N1_BANDS def at char', i)
print('---- window around N1_BANDS ----')
print(pf[i - 300:i + 2500])
