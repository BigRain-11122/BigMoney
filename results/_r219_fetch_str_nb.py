# r219: fetch STR notebook via gh-proxy (r218 channel recipe: percent-encode CJK, direct urllib)
# Mechanism/parameter extraction only (no-license repo -> code structurally forbidden to copy).
import urllib.request, urllib.parse, os, json

BASE = "https://gh-proxy.com/https://raw.githubusercontent.com/hugo2046/QuantsPlaybook/master/"
path = "B-因子构建类/凸显理论STR因子/凸显度因子.ipynb"
url = BASE + urllib.parse.quote(path)
out = os.path.join(os.environ.get("TEMP", "."), "str_salience_nb.ipynb")
print("url:", url)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=60) as r:
    data = r.read()
print("bytes:", len(data))
with open(out, "wb") as f:
    f.write(data)
nb = json.loads(data.decode("utf-8"))
print("cells:", len(nb.get("cells", [])))
# dump code cells to a temp txt for reading
lines = []
for i, c in enumerate(nb["cells"]):
    src = "".join(c.get("source", []))
    lines.append(f"===== cell {i} [{c.get('cell_type')}] =====\n{src}\n")
dump = out + ".txt"
with open(dump, "w", encoding="utf-8") as f:
    f.write("".join(lines))
print("dump:", dump)
