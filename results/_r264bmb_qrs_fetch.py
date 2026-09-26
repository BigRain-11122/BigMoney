# r264 bm-b: T-76 wave-10 QRS deep-read recheck fetch (r263 channel recipe: gh-proxy +
# percent-encode CJK + ProxyHandler({})). Mechanism/parameter extraction only
# (no-license repo -> code structurally forbidden to copy). Serial pacing (R109).
import json
import os
import urllib.parse
import urllib.request

BASE = "https://gh-proxy.com/https://raw.githubusercontent.com/hugo2046/QuantsPlaybook/master/"
TMP = os.environ.get("TEMP", ".")
TARGETS = [
    ("C-择时类/QRS择时信号/QRS.ipynb", "qrs_nb.ipynb"),
]
for path, name in TARGETS:
    url = BASE + urllib.parse.quote(path)
    out = os.path.join(TMP, name)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=90) as r:
            data = r.read()
    except Exception as e:  # noqa: BLE001
        print(f"FETCH_FAIL {name}: {type(e).__name__} {str(e)[:120]}")
        continue
    with open(out, "wb") as f:
        f.write(data)
    print(f"OK {name}: {len(data)} bytes")
    if name.endswith(".ipynb"):
        nb = json.loads(data.decode("utf-8"))
        lines = []
        for i, c in enumerate(nb.get("cells", [])):
            src = "".join(c.get("source", []))
            lines.append(f"===== cell {i} [{c.get('cell_type')}] =====\n{src}\n")
        dump = out + ".txt"
        with open(dump, "w", encoding="utf-8") as f:
            f.write("".join(lines))
        print(f"  cells: {len(nb.get('cells', []))} -> dump {dump}")
