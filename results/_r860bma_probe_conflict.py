import re
raw = open(r'results\_orphan_face_probe.json', encoding='utf-8').read()
print('has markers:', '<<<<<<<' in raw)
parts = re.split(r'<<<<<<< HEAD\r?\n|=======\r?\n|>>>>>>> [^\r\n]+\r?\n', raw)
print('parts:', len(parts))
for i, p in enumerate(parts):
    t = re.search(r'"ts": "([^"]+)"', p)
    py = re.search(r'"py_faces_seen": (\d+)', p)
    o = re.search(r'"orphans": (\d+)', p)
    mid = re.search(r'"machine_id": "([^"]+)"', p)
    print(i, '| ts:', t.group(1) if t else None,
          '| faces:', py.group(1) if py else None,
          '| orphans:', o.group(1) if o else None,
          '| mid:', mid.group(1) if mid else None,
          '| bytes:', len(p))
