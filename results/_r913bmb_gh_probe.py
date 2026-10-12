# r913 bm-b: fetch MiniMax-AI GitHub org repo list (read-only public API), filter speech/audio/music faces
# Usage: python results/_r913bmb_gh_probe.py
import json
import urllib.request

URL = "https://api.github.com/orgs/MiniMax-AI/repos?per_page=100&sort=updated"
req = urllib.request.Request(URL, headers={"User-Agent": "bm-b-fleet-probe", "Accept": "application/vnd.github+json"})
with urllib.request.urlopen(req, timeout=45) as r:
    repos = json.load(r)

out = []
for rp in repos:
    name = rp.get("full_name", "")
    desc = (rp.get("description") or "")[:120]
    lic = (rp.get("license") or {}).get("spdx_id")
    out.append({"name": name, "license": lic, "updated": rp.get("updated_at"), "desc": desc})

with open("results/_r913bmb_gh_minimax_repos.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("total", len(out))
for o in out:
    low = (o["name"] + " " + o["desc"]).lower()
    if any(k in low for k in ("speech", "tts", "audio", "music", "voice")):
        print("HIT", o["name"], "|", o["license"], "|", o["desc"])
