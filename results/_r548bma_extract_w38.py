import subprocess, json
raw = subprocess.check_output(['git', 'show', 'origin/main:results/perpetual_faces/n1_w38_results.json'])
d = json.loads(raw.decode('utf-8'))

def find_p95(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "p95" in str(k).lower():
                print(path + "/" + str(k), "=", v)
            find_p95(v, path + "/" + str(k))
    elif isinstance(obj, list):
        pass

find_p95(d)
print('families keys:', list(d.get('families', {}).keys()) if isinstance(d.get('families'), dict) else type(d.get('families')).__name__)
