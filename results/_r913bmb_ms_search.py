# r913 bm-b: ModelScope dolphin search for Speech-02 / MiniMax TTS faces (read-only POST search)
# Usage: python results/_r913bmb_ms_search.py
import json
import urllib.request

BASE = "https://modelscope.cn/api/v1/dolphin/models"


def search(name, page_size=20):
    body = json.dumps({"Name": name, "PageSize": page_size, "PageNumber": 1}).encode()
    req = urllib.request.Request(
        BASE, data=body, method="PUT",
        headers={"Content-Type": "application/json", "User-Agent": "bm-b-fleet-probe"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
        rows = ((data.get("Data") or {}).get("Model")) or {}
        items = rows.get("Models") or []
        print("QUERY:", name, "hits:", rows.get("TotalCount"))
        for it in items:
            print("  ", it.get("Path", "?"), "/", it.get("Name", "?"), "| tasks:", it.get("Tasks"), "| dl:", it.get("DownloadsCount"))
        return items
    except Exception as e:
        print("ERR", name, str(e)[:100])
        return []


all_hits = {}
for q in ("Speech-02", "MiniMax Speech", "MiniMax-Music3"):
    all_hits[q] = [ {"id": it.get("Path") + "/" + it.get("Name")} for it in search(q) ]

with open("results/_r913bmb_ms_search.json", "w", encoding="utf-8") as f:
    json.dump(all_hits, f, ensure_ascii=False, indent=1)
