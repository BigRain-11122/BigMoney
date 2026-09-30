import re
draft = open('results/_r464bma_w13_runner_draft.py', encoding='utf-8').read()
# all w12-prefixed identifiers and strings
pats = sorted(set(re.findall(r'[\'"]?w12[A-Za-z0-9_.]*[\'"]?', draft)))
for p in pats:
    print(repr(p), draft.count(p))
