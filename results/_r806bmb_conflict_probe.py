import subprocess, json, re, sys

def stage_blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", errors="replace")

# deep-scan nested ts (r311 law): find keys matching ts-like patterns, collect max value
def deep_ts(obj, path=""):
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            kk = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str):
                if ("ts" in kk or "time" in kk or "generated" in kk or "updated" in kk) and re.match(r"^20\d{2}-", v):
                    found.append((f"{path}.{k}", v))
                else:
                    found.extend(deep_ts(v, f"{path}.{k}"))
            else:
                found.extend(deep_ts(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:3]):
            found.extend(deep_ts(v, f"{path}[{i}]"))
    return found

probes = {
    "docs/daily_report/REPORT-2026-10-07.json": "json",
    "docs/daily_report/REPORT-2026-10-07.md": "md",
    "docs/live_usage/LIVE-2026-10-07.json": "json",
    "docs/live_usage/LIVE-2026-10-07.md": "md",
    "docs/live_usage/LIVE-latest.json": "json",
    "docs/live_usage/LIVE-latest.md": "md",
    "results/fundamental_b_layer_filter.json": "json",
    "results/futures_update_status.json": "json",
    "results/lhb_update_status.json": "json",
    "results/token_usage.json": "json",
    "results/_attrition_guard_scan.json": "json",
}

for path, kind in probes.items():
    o = stage_blob(2, path)
    t = stage_blob(3, path)
    print(f"=== {path}")
    for label, raw in (("ours(origin)", o), ("theirs(r805)", t)):
        if raw is None:
            print(f"  {label}: <no blob>")
            continue
        if kind == "json":
            try:
                obj = json.loads(raw)
                ts = deep_ts(obj)
                ts.sort(key=lambda x: x[1])
                # show top-3 newest ts keys
                for k, v in ts[-3:]:
                    print(f"  {label}: {k} = {v}")
                if not ts:
                    keys = list(obj.keys())[:12] if isinstance(obj, dict) else f"list len {len(obj)}"
                    print(f"  {label}: NO ts keys; top keys: {keys}")
            except Exception as e:
                print(f"  {label}: parse fail {e}; head: {raw[:120]!r}")
        else:
            m = re.findall(r"20\d{2}-\d{2}-\d{2}[T ][\d:]+", raw)
            print(f"  {label}: ts candidates: {m[:6]}")

# compute_audit + attrition: structural probe
for path in ("results/compute_audit.json", "results/_attrition_guard_scan.json"):
    print(f"=== structure {path}")
    for stage, label in ((2, "ours(origin)"), (3, "theirs(r805)")):
        raw = stage_blob(stage, path)
        if raw is None:
            print(f"  {label}: <no blob>")
            continue
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict):
                info = {}
                for k, v in obj.items():
                    if isinstance(v, list):
                        info[k] = f"list[{len(v)}]"
                    elif isinstance(v, dict):
                        info[k] = f"dict[{len(v)}]"
                    else:
                        info[k] = repr(v)[:60]
                print(f"  {label}: {info}")
            else:
                print(f"  {label}: type={type(obj).__name__}")
        except Exception as e:
            print(f"  {label}: parse fail {e}")
