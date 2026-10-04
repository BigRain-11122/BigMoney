"""r683 bm-a board scan: open/claimed tickets + G2 stage-2 shortlist context (PS5.1 ConvertFrom-Json parse failures workaround)."""
import json
import glob

out = {"round": 683, "machine": "bm-a", "open": [], "claimed_in_progress": []}
for p in sorted(glob.glob("fleet/tasks/*.json")):
    try:
        t = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        out.setdefault("parse_fail", []).append({"file": p, "err": str(e)[:120]})
        continue
    st = t.get("status")
    tid = t.get("id") or p
    if st == "open":
        out["open"].append({"id": tid, "title": (t.get("title") or t.get("type") or "")[:100], "priority": t.get("priority")})
    elif st in ("claimed", "in_progress"):
        out["claimed_in_progress"].append({"id": tid, "status": st, "claimed_by": t.get("claimed_by")})
json.dump(out, open("results/_r683bma_board_scan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({"open": len(out["open"]), "claimed": len(out["claimed_in_progress"]), "parse_fail": len(out.get("parse_fail", []))}))
for o in out["open"]:
    print("OPEN:", o["priority"], o["id"], o["title"])
