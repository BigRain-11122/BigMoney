import json, numpy as np
z = np.load(r'data\census_w2b\w2b_d8_faces.npz', allow_pickle=False)
npz_keys = sorted(z.files)
print('npz keys (', len(npz_keys), '):')
for k in npz_keys:
    print('  ', k, z[k].shape, z[k].dtype)
m = json.load(open(r'results\census_fusion_s2\w2b_d8_manifest.json', encoding='utf-8'))
print()
print('manifest keys:', list(m.keys()))
print('manifest faces:', json.dumps(m.get('faces', m.get('face_names', m.get('artifact_faces', 'NO-FACES-KEY'))), ensure_ascii=False)[:400])
r = json.load(open(r'results\census_fusion_s2\w2b_roster.json', encoding='utf-8'))
rf = [f['face'] for f in r['w2b']['faces']]
print('roster 8 faces:', rf)
print()
print('in roster missing from npz:', [f for f in rf if f not in npz_keys])
print('in npz not in roster:', [k for k in npz_keys if k not in rf])
