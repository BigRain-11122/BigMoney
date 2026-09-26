# r273 bm-b migration discovery (O-20260926-2000-bm-c step-1 face, read-only)
# Dumps ALL scheduled-task XMLs, finds every task whose definition references
# either old-root literal; also probes PATH/env faces. No mutation.
import subprocess, os, json

OLD_BM = r'C:\Users\Administrator\Desktop\Bigmoney'
OLD_MG = r'E:\Minigame'
OUT = r'results\_r273bmb_migration_discovery.json'

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True)
    return r.stdout.decode('gbk', errors='replace')

names = []
csv = sh('schtasks /query /fo csv /nh')
for line in csv.splitlines():
    if not line.strip():
        continue
    name = line.split(',')[0].strip('"').lstrip('\\')
    if name:
        names.append(name)
names = sorted(set(names))

hits_bm, hits_mg, fails = [], [], []
tmp = os.path.join(os.environ['TEMP'], 'fgtask.xml')
for n in names:
    if os.path.exists(tmp):
        os.remove(tmp)
    subprocess.run(f'schtasks /query /tn "{n}" /xml > "{tmp}"', shell=True, capture_output=True)
    xml = ''
    for enc in ('utf-16', 'utf-8-sig'):
        try:
            xml = open(tmp, encoding=enc).read()
            break
        except Exception:
            continue
    if not xml.strip():
        xml = open(tmp, encoding='utf-8', errors='replace').read()
    if not xml.strip():
        fails.append(n)
        continue
    variants = []
    for pat in (OLD_MG.replace('\\', '/'), OLD_MG.replace('\\', r'\\'),
                OLD_BM.replace('\\', '/')):
        if pat in xml:
            variants.append(pat)
    if OLD_BM in xml:
        hits_bm.append({'task': n, 'bm_literal': True, 'mg_literal': OLD_MG in xml, 'variants': variants})
    elif OLD_MG in xml:
        hits_mg.append({'task': n, 'bm_literal': False, 'mg_literal': True, 'variants': variants})

env_faces = {}
import winreg
try:
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment')
    for var in ('Path', 'OLLAMA_MODELS', 'OLLAMA_HOST', 'OLLAMA_KEEP_ALIVE'):
        try:
            env_faces[var] = winreg.QueryValueEx(k, var)[0]
        except Exception:
            env_faces[var] = None
except Exception as e:
    env_faces['ERR'] = str(e)

res = {
    'total_tasks': len(names),
    'hits_bigmoney_root': hits_bm,
    'hits_minigame_root': hits_mg,
    'xml_dump_failures': fails,
    'env_faces': env_faces,
    'env_contains_minigame': {k: (OLD_MG in (v or '')) for k, v in env_faces.items() if isinstance(v, str)},
}
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('total_tasks', len(names))
print('BM-root hits:', [h['task'] for h in hits_bm])
print('MG-root hits:', [h['task'] for h in hits_mg])
print('failures:', fails)
print('env contains E:\\Minigame:', res['env_contains_minigame'])
print('OLLAMA_MODELS:', env_faces.get('OLLAMA_MODELS'))
