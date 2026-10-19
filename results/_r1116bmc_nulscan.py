# r1116 closeout NUL scan (r1077 law: no NUL-corroded face may ride a commit)
import subprocess, sys

files = subprocess.run(['git', '-C', r'K:\Fluxgroup\FluxGroup\quant\bigmoney', 'status', '--porcelain'],
                       capture_output=True).stdout.decode('utf-8', 'replace').splitlines()
targets = []
for row in files:
    st, path = row[:2], row[3:].strip()
    if st.strip() == 'D':  # staged deletion face (watermark_red) -- no bytes to scan
        continue
    targets.append(path)
bad = []
for p in targets:
    try:
        with open(r'K:\Fluxgroup\FluxGroup\quant\bigmoney' + '\\' + p.replace('/', '\\'), 'rb') as f:
            data = f.read()
        if b'\x00' in data:
            bad.append(p)
    except OSError:
        pass
print('scanned=%d nul_bad=%d' % (len(targets), len(bad)))
for p in bad:
    print('NUL-CORRODED:', p)
sys.exit(1 if bad else 0)
