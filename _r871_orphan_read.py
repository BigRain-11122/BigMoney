import json
d = json.load(open('results/_orphan_face_probe.bm-c.json', encoding='utf-8'))
for f in d.get('orphan_details', []):
    print(json.dumps(f, ensure_ascii=False)[:400])
for f in d.get('faces', []):
    print('FACE:', json.dumps(f, ensure_ascii=False)[:260])
