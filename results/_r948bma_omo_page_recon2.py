import urllib.request, re

url = "https://data.eastmoney.com/cjsj/gksccz.html"
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://data.eastmoney.com/",
})
with urllib.request.urlopen(req, timeout=45) as r:
    html = r.read().decode("utf-8", errors="replace")

# dump all http(s) urls and script srcs
urls = sorted(set(re.findall(r'https?://[A-Za-z0-9.\-/_?=&%]+', html)))
for u in urls[:40]:
    print('U:', u[:150])

# find any api-ish fragments
for kw in ['api', 'datacenter', 'RPT_', 'gksccz', 'json', 'ajax']:
    idxs = [m.start() for m in re.finditer(kw, html, re.I)][:3]
    for i in idxs:
        seg = html[max(0, i-120):i+180].replace('\n', ' ')
        print(f'KW[{kw}] CTX:', seg[:300])
