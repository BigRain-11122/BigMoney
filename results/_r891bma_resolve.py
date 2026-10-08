# r891 bm-a rebase-conflict manual resolver (skill bigmoney-conflict-resolve; fail-closed UNKNOWNs)
# Recipes: snapshot take-new by deep-ts probe (R208/R216/r100/R350); twins ts-diffpick
# whole-byte SAME side (r98/r99/r100/r327/r329); probe staged blobs not working tree.
# Stages during rebase: :2: = origin-side (bm-c tip), :3: = local replay side (bm-a r891).
import subprocess, json, sys, re

def stage(stage_n, path):
    r = subprocess.run(["git", "show", f":{stage_n}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def deep_ts(obj, depth=0):
    """Deep-scan for a wall-clock ts value; probe path existence first (r319). Return best (key, str)."""
    best = None
    KEYPAT = re.compile(r"^(generated|generated_at|updated|ts|time|scan_ts|asof|as_of)", re.I)
    def rec(o, path):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                nk = str(k).strip("_-").lower()
                if isinstance(v, str) and PAT.match(nk) and re.match(r"^20\d{2}-", v):
                    if best is None or v > best[1]:
                        best = (path + "/" + str(k), v)
                else:
                    rec(v, path + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o[:50]):
                rec(v, f"{path}[{i}]")
    PAT = KEYPAT
    rec(obj, "")
    return best

def resolve_snapshot(path):
    a2, a3 = stage(2, path), stage(3, path)
    assert a2 is not None and a3 is not None, f"{path}: stage read fail"
    try:
        j2, j3 = json.loads(a2), json.loads(a3)
        t2, t3 = deep_ts(j2), deep_ts(j3)
        assert t2 and t3, f"{path}: ts probe miss ({t2} vs {t3})"
        side = 3 if t3[1] >= t2[1] else 2
        ts_win = t3[1] if side == 3 else t2[1]
    except (json.JSONDecodeError, AssertionError):
        # non-JSON face: fall back to byte-length + raw ts regex probe
        m2 = re.findall(rb"20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", a2)
        m3 = re.findall(rb"20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", a3)
        t2s = max(m2).decode() if m2 else ""
        t3s = max(m3).decode() if m3 else ""
        assert t2s or t3s, f"{path}: raw ts probe miss"
        side = 3 if t3s >= t2s else 2
        ts_win = t3s if side == 3 else t2s
    data = a3 if side == 3 else a2
    with open(path, "wb") as f:
        f.write(data)
    # parse-verify if json
    if path.endswith(".json"):
        json.loads(open(path, "rb").read())
    print(f"[resolve] {path}: side=:{side}: ({'bm-a r891' if side==3 else 'origin bm-c'}) ts={ts_win} -> written+verified")
    return side

def resolve_twin(json_path, md_paths):
    side = resolve_snapshot(json_path)
    data = stage(side, json_path)  # already written
    for md in md_paths:
        b = stage(side, md)
        assert b is not None, f"{md}: stage {side} read fail"
        with open(md, "wb") as f:
            f.write(b)
        print(f"[resolve-twin] {md}: byte-copied from :{side}: (same-side law r329)")

# 1) snapshot take-new
resolve_snapshot("results/fundamental_b_layer_filter.json")
resolve_snapshot("results/_attrition_guard_scan.json")
# 2) twins: json picks side by ts; md byte-copied same side (r98/r99/r100/r327/r329)
resolve_twin("docs/daily_report/REPORT-2026-10-08.json",
             ["docs/daily_report/REPORT-2026-10-08.md"])
resolve_twin("docs/live_usage/LIVE-2026-10-08.json",
             ["docs/live_usage/LIVE-2026-10-08.md",
              "docs/live_usage/LIVE-latest.json",
              "docs/live_usage/LIVE-latest.md"])
print("manual resolve complete: 7 files (2 snapshot + 5 twin faces)")
