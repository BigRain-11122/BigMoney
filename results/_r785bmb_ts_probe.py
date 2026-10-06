# r785 bm-b pre-resolve ts probe: verify dead-session r784 resolver evidence claims.
# Law R350: probe staged blobs (stage2=ours / stage3=theirs), never working tree.
import subprocess, json, re

def blob(stage, path):
    h = subprocess.run(["git", "rev-parse", "-q", "--verify", f":{stage}:{path}"],
                       capture_output=True, text=True).stdout.strip()
    if not h:
        return None
    return subprocess.run(["git", "cat-file", "blob", h],
                          capture_output=True).stdout.decode("utf-8", "replace")

def scan_ts(d, prefix=""):
    """deep-scan for ts-like keys (R350: no key-exclude lists; wall-clock values need time-of-day)."""
    hits = []
    if isinstance(d, dict):
        for k, v in d.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if (("ts" in nk or "time" in nk or "generated" in nk or "updated" in nk or "date" in nk)
                    and isinstance(v, str) and re.match(r"^20\d{2}-", v) and re.search(r"\d{2}:\d{2}", v)):
                hits.append((prefix + str(k), v))
            hits.extend(scan_ts(v, prefix + str(k) + "."))
    elif isinstance(d, list):
        for i, v in enumerate(d[:50]):
            hits.extend(scan_ts(v, prefix + f"[{i}]."))
    return hits

faces = ["results/lhb_update_status.json", "results/regime_state.json",
         "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
         "docs/daily_report/REPORT-2026-10-06.json", "docs/live_usage/LIVE-2026-10-06.json",
         "docs/live_usage/LIVE-latest.json", "results/dashboard_status.json",
         "results/token_usage.json"]
report = {}
for p in faces:
    o, t = blob(2, p), blob(3, p)
    try:
        jo, jt = json.loads(o), json.loads(t)
    except Exception as e:
        report[p] = {"error": str(e)}
        continue
    report[p] = {
        "ours_ts": scan_ts(jo)[:6],
        "theirs_ts": scan_ts(jt)[:6],
        "ours_bytes": len(o), "theirs_bytes": len(t),
    }

# dashboard host probe (single-writer law r378)
dj = json.loads(blob(3, "results/dashboard_status.json"))
report["dashboard_host_theirs"] = dj.get("host") or dj.get("machine") or [k for k in dj if "host" in k or "machine" in k][:5]
do = json.loads(blob(2, "results/dashboard_status.json"))
report["dashboard_host_ours"] = do.get("host") or do.get("machine") or [k for k in do if "host" in k or "machine" in k][:5]

# regime_state history rows both sides (rolling-ledger union check)
ro, rt = json.loads(blob(2, "results/regime_state.json")), json.loads(blob(3, "results/regime_state.json"))
for k in set(ro) | set(rt):
    v = ro.get(k, None) if isinstance(ro.get(k), list) else None
    if isinstance(ro.get(k), list) or isinstance(rt.get(k), list):
        report[f"regime_list:{k}"] = {"ours_len": len(ro.get(k) or []), "theirs_len": len(rt.get(k) or [])}

with open("results/_r785bmb_ts_probe.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print(json.dumps(report, ensure_ascii=False, indent=1)[:3000])
