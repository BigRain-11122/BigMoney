"""r1495 closeout: E472 -> done with result_ref, seed E473 to hold the supply floor at 3."""
import io
import json

P = "results/runnable_pool.json"
raw = io.open(P, encoding="utf-8", newline="").read()
d = json.loads(raw)

for entry in d["entries"]:
    if entry.get("id", "").startswith("E472"):
        entry["status"] = "done"
        entry["owner"] = "bm-b"
        entry["result_ref"] = ("results/state_tilt/VINTAGEREAD-2026-11-06.json "
                               "(study E472; scripts/e472_vintage_read.py)")
        entry["closed_at"] = "2026-11-06T22:5x+08:00"
        entry["closed_by"] = "bm-b r1495"
        entry["close_note"] = ("97 vintage families / 571 files / 28.5 MB, 0 opened by a study that "
                              "does not write it (17 named-only, 7 leg-only, 73 producer-only); "
                              "36 carry a _latest pointer and none is opened")
        break

NEW = {
    "id": "E473-DO-THE-UNREAD-VINTAGE-FAMILIES-COME-FROM-PRODUCERS-WHOSE-OTHER-FACES-A-STUDY-DOES-OPEN",
    "title": ("E472 found all 97 vintage families under results/ unread by any study. Some of their "
              "producers also publish faces that ARE consumed. If a producer's studied output and its "
              "unread output come from the same script, the unread part is spillover that can be "
              "pruned at source; if the unread part is a producer's only output, the producer itself "
              "is the question."),
    "question": ("Join the E472 rows' producer sites with the E466/E470 reader map: for each producer "
                 "site, how many families does it write, how many of those have a study consumer, and "
                 "how many bytes per cutoff does it emit that nothing reads? Publish the producers "
                 "ranked by unread emission, and split them into 'emits both studied and unread' "
                 "versus 'emits only unread'."),
    "deliverable": "results/state_tilt/PRODUCERSPILL-<cutoff>.json",
    "lane": "cpu-only",
    "lane_note": ("static: reads the published E472 rows plus the E470 opener map; no face is "
                  "rewritten outside results/state_tilt"),
    "priority": "normal",
    "status": "ready",
    "owner": None,
    "source": "E472 (r1495 bm-b): 0 of 97 vintage families are opened by a study that does not write them",
    "entered_at": "2026-11-06T23:0+0800",
    "entered_by": "bm-b r1495 (supply floor refill after E472)",
}
if not any(e.get("id") == NEW["id"] for e in d["entries"]):
    d["entries"].append(NEW)

d["updated_at"] = "2026-11-06T23:0+08:00"
io.open(P, "w", encoding="utf-8", newline="\n").write(
    json.dumps(d, ensure_ascii=False, indent=1) + "\n")
ready = [e for e in d["entries"] if e.get("status") == "ready"]
print("entries", len(d["entries"]), "ready", len(ready))
for e in ready:
    print("  ready:", e["id"][:60])