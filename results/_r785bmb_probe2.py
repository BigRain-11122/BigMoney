# r785 bm-b resolver-2 probe: 16 UU faces from second absorb (origin r796/r797).
# R350: probe STAGED blobs (:2: ours / :3: theirs), never working tree.
import subprocess, json, re

def blob(stage, path):
    h = subprocess.run(["git", "rev-parse", "-q", "--verify", f":{stage}:{path}"],
                       capture_output=True, text=True).stdout.strip()
    if not h:
        return None
    return subprocess.run(["git", "cat-file", "blob", h],
                          capture_output=True).stdout.decode("utf-8", "replace")

def scan_ts(d, prefix=""):
    hits = []
    if isinstance(d, dict):
        for k, v in d.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if (("ts" in nk or "time" in nk or "generated" in nk or "updated" in nk)
                    and isinstance(v, str) and re.match(r"^20\d{2}-", v) and re.search(r"\d{2}:\d{2}", v)):
                hits.append((prefix + str(k), v))
            hits.extend(scan_ts(v, prefix + str(k) + "."))
    elif isinstance(d, list):
        for i, v in enumerate(d[:80]):
            hits.extend(scan_ts(v, prefix + f"[{i}]."))
    return hits

FACES = ["docs/daily_report/REPORT-2026-10-06.json", "docs/live_usage/LIVE-2026-10-06.json",
         "docs/live_usage/LIVE-latest.json", "results/_attrition_guard_scan.json",
         "results/compute_audit.json", "results/fundamental_b_layer_filter.json",
         "results/futures_update_status.json", "results/lhb_update_status.json",
         "results/regime_state.json", "results/scorecard_v1.json",
         "results/strategy_scorecard.json", "results/token_usage.json",
         "results/update_status.json"]

report = {}
for p in FACES:
    o, t = blob(2, p), blob(3, p)
    try:
        jo, jt = json.loads(o), json.loads(t)
    except Exception as e:
        report[p] = {"error": repr(e), "ours_head": o[:120], "theirs_head": t[:120]}
        continue
    report[p] = {"ours_ts": scan_ts(jo)[:4], "theirs_ts": scan_ts(jt)[:4],
                 "ours_bytes": len(o), "theirs_bytes": len(t)}

# ledger keys inventory (union candidates)
for p in ("results/compute_audit.json", "results/regime_state.json", "results/_attrition_guard_scan.json"):
    jo, jt = json.loads(blob(2, p)), json.loads(blob(3, p))
    lists = {k: [len(x) if isinstance(x, list) else None for x in (jo.get(k), jt.get(k))]
             for k in set(jo) | set(jt) if isinstance(jo.get(k), list) or isinstance(jt.get(k), list)}
    report[p + "::list_keys"] = lists
    top_o = list(jo.keys())[:14]
    report[p + "::top_keys_ours"] = top_o

with open("results/_r785bmb_probe2.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print(json.dumps(report, ensure_ascii=False, indent=1)[:4200])
