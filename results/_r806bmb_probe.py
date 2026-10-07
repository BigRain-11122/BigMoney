import subprocess

r = subprocess.run(['git','show',':2:results/p1d_gates.json'], capture_output=True)
print('rc', r.returncode)
print('stdout len', len(r.stdout))
print('stderr:', r.stderr.decode('utf-8', errors='replace')[:500])
r2 = subprocess.run(['git','show','HEAD:results/p1d_gates.json'], capture_output=True)
print('HEAD rc', r2.returncode, 'len', len(r2.stdout), 'err', r2.stderr.decode('utf-8',errors='replace')[:200])
