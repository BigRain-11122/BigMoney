# r219: fetch STR notebook vendored scr/core.py (calc_sigma/calc_weight impl position)
import urllib.request, urllib.parse, os

BASE = "https://gh-proxy.com/https://raw.githubusercontent.com/hugo2046/QuantsPlaybook/master/"
path = "B-因子构建类/凸显理论STR因子/scr/core.py"
url = BASE + urllib.parse.quote(path)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=60) as r:
    data = r.read()
out = os.path.join(os.environ.get("TEMP", "."), "str_core.py")
open(out, "wb").write(data)
print("bytes:", len(data), "->", out)
