"""r263 bm-b: T-76 face (d) deep-read trees probe (#95 GF higher-mom / #96 bimodal).

R216 law: trees API authoritative listing, README links stale. R109: serial calls.
Output: filtered paths only, no download (download via gh-proxy raw in next step).
"""
import json
import sys
import urllib.request

URL = "https://api.github.com/repos/hugo2046/QuantsPlaybook/git/trees/master?recursive=1"

req = urllib.request.Request(URL, headers={"User-Agent": "bm-b-research", "Accept": "application/vnd.github+json"})
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
except Exception as e:  # noqa: BLE001
    print("FETCH_FAIL:", type(e).__name__, str(e)[:200])
    sys.exit(2)

tree = data.get("tree", [])
print("entries:", len(tree), "truncated:", data.get("truncated"))
keys = ["高阶矩", "bimodal", "skew", "kurt", "矩择时"]
hits = [t["path"] for t in tree if any(k.lower() in t["path"].lower() for k in keys)]
for p in hits:
    print("HIT:", p)
if not hits:
    # fallback: dump timing-class dirs to eyeball
    dirs = sorted({t["path"] for t in tree if t["path"].count("/") <= 1 and t["type"] == "tree"})
    print("--- top dirs ---")
    for d in dirs:
        print("DIR:", d)
