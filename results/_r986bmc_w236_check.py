import json, subprocess, re

# engine queue_next + burns_active from status json
r = subprocess.run(['python', 'Tools/saturation_engine.py', 'status'], capture_output=True, text=True, encoding='utf-8', errors='replace')
d = json.loads(r.stdout)
print('alive:', d.get('alive_flag'), '| burns_active:', d.get('burns_active'), '| queue_next:', json.dumps(d.get('queue_next'), ensure_ascii=False)[:500])

# origin tip: recent commits touching engine faces (W236 lineage)
K = 'K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney'
r2 = subprocess.run(['git', 'log', '--oneline', '-15', 'origin/main'], capture_output=True, text=True, encoding='utf-8', errors='replace')
print('--- origin/main last 15 commits ---')
print(r2.stdout)

# search recent commits for W236 mentions
r3 = subprocess.run(['git', 'log', '--oneline', '--all', '-20', '--grep=236'], capture_output=True, text=True, encoding='utf-8', errors='replace')
print('--- commits matching 236 ---')
print(r3.stdout)
