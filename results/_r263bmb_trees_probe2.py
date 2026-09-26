"""r263 bm-b: trees probe step2 (#96 volume bimodal path discovery)."""
import json
import sys
import urllib.request

URL = "https://api.github.com/repos/hugo2046/QuantsPlaybook/git/trees/master?recursive=1"
req = urllib.request.Request(URL, headers={"User-Agent": "bm-b-research", "Accept": "application/vnd.github+json"})
with urllib.request.urlopen(req, timeout=60) as r:
    data = json.load(r)
tree = data.get("tree", [])
keys = ["特征分布", "成交量", "量能", "华创", "distribution"]
for t in tree:
    p = t["path"]
    if any(k in p for k in keys) and ("择时" in p or "timing" in p.lower() or "分布" in p):
        print("HIT:", p, "|", t.get("type"), "|", t.get("size", ""))
