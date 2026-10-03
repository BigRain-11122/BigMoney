import json, subprocess, sys
RB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
UU = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
CREATE = 0x08000000

def blob(rev, path):
    p = subprocess.run(["git", "-C", RB, "show", "%s:%s" % (rev, path)],
                       capture_output=True, creationflags=CREATE)
    return p.stdout

def ts_of(data, is_md):
    if is_md:
        for line in data.decode("utf-8", "replace").splitlines()[:8]:
            if "2026-" in line and ("生成" in line or "generated" in line.lower()):
                import re
                m = re.search(r"2026-\d{2}-\d{2} \d{2}:\d{2}(:\d{2})?", line)
                if m:
                    return m.group(0)
        return None
    try:
        d = json.loads(data.decode("utf-8"))
    except Exception:
        return None
    if not isinstance(d, dict):
        return None
    for k in ("ts", "generated", "updated", "updated_at", "asof", "scan_ts", "generated_at"):
        v = d.get(k)
        if isinstance(v, str) and v:
            return v
    # nested latest block
    lat = d.get("latest")
    if isinstance(lat, dict):
        for k in ("ts", "generated"):
            v = lat.get(k)
            if isinstance(v, str) and v:
                return v
    return None

for path in UU:
    is_md = path.endswith(".md")
    ours = blob(":2", path)
    theirs = blob(":3", path)
    o_ts = ts_of(ours, is_md)
    t_ts = ts_of(theirs, is_md)
    print("%s | OURS_TS=%s | THEIRS_TS=%s" % (path, o_ts, t_ts))

# shapes for the union faces
for path in ("results/compute_audit.json", "results/token_usage.json"):
    for rev, name in ((":2", "OURS"), (":3", "THEIRS")):
        try:
            d = json.loads(blob(rev, path).decode("utf-8"))
            top = sorted(d.keys()) if isinstance(d, dict) else type(d).__name__
            print("%s %s top-keys=%s" % (path, name, top[:14]))
            if isinstance(d, dict):
                for probe in ("history", "machines", "rows", "ledger"):
                    if probe in d:
                        v = d[probe]
                        print("   %s: %s len=%s" % (probe, type(v).__name__,
                              len(v) if hasattr(v, "__len__") else "?"))
        except Exception as e:
            print("%s %s PARSE_ERR %r" % (path, name, e))
