import urllib.request, re, json

url = "https://data.eastmoney.com/cjsj/gksccz.html"
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://data.eastmoney.com/",
})
try:
    with urllib.request.urlopen(req, timeout=45) as r:
        html = r.read().decode("utf-8", errors="replace")
    print("LEN", len(html))
    for pat in [r'reportName[\"\x27:=\s]+([A-Za-z0-9_]+)',
                r'https?://datacenter[^\"\x27\s]+',
                r'https?://[a-z0-9.\-]*eastmoney[^\"\x27\s]*api[^\"\x27\s]*']:
        hits = sorted(set(re.findall(pat, html)))
        print(pat[:40], '->', hits[:8])
    i = html.find('reportName')
    if i > 0:
        print('CTX:', html[max(0, i-300):i+400].replace('\n', ' ')[:700])
except Exception as e:
    print('FETCH-ERR', type(e).__name__, str(e)[:200])
