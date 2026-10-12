# r913 bm-b: probe ModelScope for MiniMax Speech-02 / Music3 repo faces (read-only GET)
# Usage: python results/_r913bmb_ms_probe.py
import json
import urllib.request
import urllib.error

CANDIDATES = [
    "MiniMax/MiniMax-Speech-02-HD",
    "MiniMax/MiniMax-Speech-02-Turbo",
    "MiniMax/MiniMax-Speech-02",
    "MiniMaxAI/MiniMax-Speech-02-HD",
    "MiniMaxAI/MiniMax-Speech-02-Turbo",
    "MiniMax/MiniMax-Music3",
    "MiniMaxAI/MiniMax-Music3",
    "MiniMax/MiniMax-Speech-2.5",
]

results = {}
for cand in CANDIDATES:
    url = "https://modelscope.cn/api/v1/models/" + cand
    req = urllib.request.Request(url, headers={"User-Agent": "bm-b-fleet-probe"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.load(r)
        code = data.get("Code")
        d = data.get("Data") or {}
        results[cand] = {
            "code": code,
            "name": d.get("Name"),
            "license": (d.get("License") or ""),
            "downloads": d.get("DownloadsCount"),
            "tasks": d.get("Tasks"),
        }
        print("HIT", cand, "| lic:", d.get("License"), "| dl:", d.get("DownloadsCount"))
    except urllib.error.HTTPError as e:
        results[cand] = {"http": e.code}
        print("MISS", cand, e.code)
    except Exception as e:
        results[cand] = {"err": str(e)[:80]}
        print("ERR", cand, str(e)[:80])

with open("results/_r913bmb_ms_probe.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
