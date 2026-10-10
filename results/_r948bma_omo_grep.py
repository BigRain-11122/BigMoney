import akshare, os, re
d = os.path.dirname(akshare.__file__)
hits = []
for root, dirs, files in os.walk(d):
    for f in files:
        if not f.endswith('.py'):
            continue
        p = os.path.join(root, f)
        try:
            t = open(p, encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        rel = os.path.relpath(p, d)
        for m in re.finditer(r'def\s+(\w*omo\w*)', t, re.I):
            hits.append((rel, m.group(1)))
        if 'gksccz' in t:
            hits.append((rel, 'GKSCCZ-URL-HIT'))
        for m in re.finditer(r'https?://[^\s"\']*gksccz[^\s"\']*', t):
            hits.append((rel, 'URL:' + m.group(0)[:120]))
        for m in re.finditer(r'reportName=([A-Z_0-9]+)', t):
            if 'OMO' in m.group(1) or 'OPEN' in m.group(1):
                hits.append((rel, 'REPORT:' + m.group(1)))
print(hits[:20] if hits else 'NO-OMO-HITS-IN-AKSHARE-SOURCE')
