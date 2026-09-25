import sys, io, re
sys.stdout.reconfigure(encoding='utf-8')
raw = io.open('results/jisilu_cnreits.html', encoding='utf-8').read()
pats = [
    r'"(/[^"]*cnreits[^"]*)"',
    r"'(/[^']*cnreits[^']*)'",
    r'url[:\s]+["\']([^"\']+)["\']',
    r'ajax[^"\']*["\']([^"\']+/[^"\']+)["\']',
    r'jsonp',
]
for pat in pats:
    hits = sorted(set(re.findall(pat, raw)))
    if hits:
        print('PAT', pat[:36], '=>')
        for h in hits[:10]:
            print('   ', h[:100])
