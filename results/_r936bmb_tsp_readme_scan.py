import io, re
txt = io.open(r'results/_r936bmb_tsp_readme.md', encoding='utf-8').read()
lines = txt.splitlines()
out = io.open(r'results/_r936bmb_tsp_readme_hits.txt', 'w', encoding='utf-8')
# find strategy-list sections: lines with strategy names/numbers or 策略 headers
keep = False
for i, l in enumerate(lines):
    if re.search(r'(?i)strateg|策略|内置|信号', l):
        out.write('%d: %s\n' % (i + 1, l[:300]))
out.close()
print('hits written')
