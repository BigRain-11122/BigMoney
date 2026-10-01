import re, io
t = io.open('scripts/perpetual_faces.py', encoding='utf-8').read()
for w in (38, 39, 40, 41, 42, 43):
    m = re.search(
        str(w) + r': \{"a": \(([\d_]+), ([\d_]+)\), "b_exit": \(([\d_]+), ([\d_]+)\),\s*\n\s*"engine_owner": "(\w+)"\}',
        t)
    print(w, m.groups() if m else 'NOT FOUND')
