import sys, io, re, html, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')


def ddg(query, n=12):
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    r = op.open(req, timeout=30)
    raw = r.read().decode('utf-8', 'ignore')
    links = re.findall(r'result__a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', raw)
    if not links:
        print('RAW len:', len(raw), '| links regex miss; anchors:', len(re.findall(r'<a [^>]*href=', raw)))
        m2 = re.findall(r'href="(https?://(?:www\.)?jisilu\.cn/question/[^"]+)"[^>]*>([^<]*)', raw)
        for h, t in m2[:12]:
            print('alt:', h[-30:], '|', t[:70])
        print('---')
        i = raw.find('jisilu')
        print(raw[max(0, i - 200):i + 300].replace('\n', ' '))
        return
    seen = []
    for href, txt in links:
        t = html.unescape(re.sub(r'<[^>]+>', '', txt))
        m = re.search(r'jisilu\.cn/question/(\d+)', href) or re.search(r'question%3D(\d+)', href) or re.search(r'question/(\d+)', href)
        if m:
            qid = m.group(1)
            if qid not in [s[0] for s in seen]:
                seen.append((qid, t))
    for s in seen[:n]:
        print(s[0], '|', s[1][:75])
    print('total:', len(seen))


if __name__ == '__main__':
    ddg(sys.argv[1])
