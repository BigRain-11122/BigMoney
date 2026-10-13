import subprocess, json


def stage_blob(path, stage):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return json.loads(r.stdout.decode('utf-8'))


o = stage_blob('fleet/machine-health.json', 2)
t = stage_blob('fleet/machine-health.json', 3)
print('outer len OURS:', len(o), 'THEIRS:', len(t))
for i, row in enumerate(o):
    keys = list(row.keys())
    print(f'OURS[{i}] keys:', keys[:4], 'Count' in row and row.get('Count'))
for i, row in enumerate(t):
    keys = list(row.keys())
    print(f'THEIRS[{i}] keys:', keys[:4], 'Count' in row and row.get('Count'))
# check the big first element equality
print('first element identical:', o[0] == t[0])
