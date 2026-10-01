"""r555 helper: dump the N1_BANDS region from W43 to dict close verbatim."""
import subprocess

pf = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces.py']).decode('utf-8')
i = pf.find('N1_BANDS = {')
tail = pf[i:]
k = tail.find('46: {')
print(tail[k - 2600:k + 200])
