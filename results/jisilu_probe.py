import sys, io, re, html, urllib.request
sys.stdout.reconfigure(encoding='utf-8')


def pull(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    r = op.open(req, timeout=30)
    return r.read().decode('utf-8', 'ignore')


if sys.argv[1] == 'cats':
    raw = pull('https://www.jisilu.cn/question/')
    print('size:', len(raw))
    for m in re.finditer(r'href="([^"]*category[^"]*)"[^>]*>([^<]*)', raw):
        print(m.group(1), '|', html.unescape(m.group(2)).strip()[:40])
elif sys.argv[1] == 'links':
    raw = pull(sys.argv[2])
    print('size:', len(raw))
    for m in re.finditer(r'href="([^"]+)"[^>]*>([^<]{0,80})', raw):
        h, t = m.group(1), html.unescape(m.group(2)).strip()
        if 'question' in h or 'REIT' in t or 'reit' in t.lower():
            print(h[:90], '|', t[:60])
