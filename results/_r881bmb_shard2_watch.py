import os, glob, time, subprocess
for f in sorted(glob.glob('results/alphagen_rg/shard_*of12.json')):
    print(os.path.basename(f), os.path.getsize(f),
          time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(f))))
print('now:', time.strftime('%H:%M:%S'))
r = subprocess.run(['tasklist', '/FI', 'PID eq 28920'],
                   capture_output=True, text=True)
print('pid28920:', 'RUNNING' if '28920' in r.stdout else 'DEAD')
tail = open('logs/autofill_E16-ALPHAGEN-RG-SHARD-2OF12.log',
            encoding='utf-8', errors='replace').read().splitlines()
for line in tail[-2:]:
    print('LOG:', line[:150])
