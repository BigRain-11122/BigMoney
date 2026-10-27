import os
import subprocess

ROOT = r'K:\Fluxgroup\FluxGroup'
STAGE = r'K:\Fluxgroup\.codely-cli\tmp-oversight-deploy-bmc'
os.makedirs(STAGE, exist_ok=True)
for name in ('oversight_deploy.ps1', 'fleet-oversight.ps1'):
    blob = subprocess.run(['git', '-C', ROOT, 'show', 'origin/main:Tools/' + name],
                          capture_output=True).stdout
    with open(os.path.join(STAGE, name), 'wb') as fh:
        fh.write(blob)
    print(name, len(blob), 'bytes')