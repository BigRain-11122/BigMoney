import re


def n(s):
    return int(s.replace('_', ''))


src = open('scripts/perpetual_faces.py', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'\s{4}(1[3-6][0-9]): \{"a": \((\d_\d{3}|\d+), (\d_\d{3}|\d+)\), "b_exit": \((\d_\d{3}|\d+), (\d_\d{3}|\d+)\)')
for i, l in enumerate(src):
    m = pat.match(l)
    if m:
        print(f"W{m.group(1)}: A={n(m.group(2))}..{n(m.group(3))} B={n(m.group(4))}..{n(m.group(5))}")
