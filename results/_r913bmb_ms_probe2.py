# r913 bm-b: final ModelScope namespace probe for Speech-02 weight faces (read-only GET)
# Usage: python results/_r913bmb_ms_probe2.py
import json
import urllib.request
import urllib.error

CANDIDATES = [
    "MiniMax-Audio/MiniMax-Speech-02-HD",
    "MiniMax-Audio/MiniMax-Speech-02-Turbo",
    "MiniMax-Audio/Speech-02-HD",
    "MiniMax/MiniMax-Speech-02-hd",
    "MiniMax/Speech-02",
    "MiniMax/MiniMax-Audio",
    "MiniMax/MiniMax-Speech",
    "MiniMaxAI/MiniMax-Speech",
]

for cand in CANDIDATES:
    url = "https://modelscope.cn/api/v1/models/" + cand
    req = urllib.request.Request(url, headers={"User-Agent": "bm-b-fleet-probe"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)
        d = data.get("Data") or {}
        print("HIT", cand, "| name:", d.get("Name"), "| lic:", d.get("License"))
    except urllib.error.HTTPError as e:
        print("MISS", cand, e.code)
    except Exception as e:
        print("ERR", cand, str(e)[:60])
