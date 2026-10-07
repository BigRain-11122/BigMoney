"""r690 bm-c boards probe (read-only facts for S2/S3): fleet tasks status
census, runnable pool entry summary, watermark red flag + verdict tail,
latest panel bar (golden-week no-bar face check). No writes."""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
facts = {"probe": "r690bmc_boards"}


def load(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


# -- fleet tasks census --
census = {}
open_list = []
for f in sorted(glob.glob(os.path.join(ROOT, "fleet", "tasks", "*.json"))):
    try:
        t = load(f)
    except Exception:
        census["read_error"] = census.get("read_error", 0) + 1
        continue
    s = str(t.get("status", "?"))
    census[s] = census.get(s, 0) + 1
    if s == "open":
        open_list.append({"file": os.path.basename(f),
                          "title": str(t.get("title", ""))[:80]})
facts["tasks_census"] = census
facts["tasks_open"] = open_list

# -- runnable pool --
try:
    d = load(os.path.join(ROOT, "results", "runnable_pool.json"))
    if isinstance(d, dict):
        ents = d.get("entries") or d.get("pool") or []
    else:
        ents = d
    summary = []
    for e in ents:
        if not isinstance(e, dict):
            continue
        summary.append({k: e.get(k) for k in
                        ("id", "status", "owner", "owner_since", "claimed_at")
                        if e.get(k) is not None})
    ready = [e for e in summary if e.get("status") == "ready"]
    unclaimed = [e for e in summary if e.get("status") == "ready" and not e.get("owner")]
    facts["pool_total"] = len(summary)
    facts["pool_ready"] = len(ready)
    facts["pool_unclaimed"] = len(unclaimed)
    facts["pool_entries"] = summary
except Exception as ex:
    facts["pool_error"] = repr(ex)[:200]

# -- watermark --
try:
    wr = load(os.path.join(ROOT, "results", "watermark_red.json"))
    facts["wm_red"] = wr.get("red")
    facts["wm_lane"] = wr.get("lane")
    facts["wm_ts"] = wr.get("ts")
    facts["wm_next_pick_status"] = (wr.get("next_pick") or {}).get("status")
except Exception as ex:
    facts["wm_error"] = repr(ex)[:200]

# -- latest panel bar (510300 daily tail) --
try:
    csvp = os.path.join(ROOT, "data", "daily", "510300.csv")
    with open(csvp, encoding="utf-8-sig") as fh:
        lines = [ln for ln in fh.read().splitlines() if ln.strip()]
    facts["latest_panel_bar_510300"] = lines[-1].split(",")[0] if lines else None
except Exception as ex:
    facts["panel_error"] = repr(ex)[:200]

print(json.dumps(facts, ensure_ascii=False, indent=1))
