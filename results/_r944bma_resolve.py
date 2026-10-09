# r944 bm-a S0 rebase storm resolver (remaining 8 faces)
# _attrition_guard_scan.json + fundamental_b_layer_filter.json = snapshot take-new by deep-ts probe
# docs twins = twin-side coupling: ts-diffpick json side, md byte-copy SAME side
# law: r185 parse-verify before write; r319 probe existence first; r351 stage mapping (:2:=origin base, :3:=ours replay)
import json, subprocess, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"

def stage_blob(path, stage):
    r = subprocess.run([GIT, "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {stage} missing for {path}: {r.stderr[:200]}")
    return r.stdout

def deep_ts(obj, keys=("updated", "generated", "generated_at", "ts")):
    """recursive first-hit wall-clock probe (r311 deep-scan; r319 existence-first)"""
    import re
    best = None
    stack = [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for k, v in cur.items():
                if isinstance(v, str):
                    nk = k.lower().replace("_", "").replace("-", "")
                    for kk in keys:
                        if nk == kk.lower().replace("_", "").replace("-", "") and re.match(r"^20\d{2}-", v):
                            if best is None or v > best:
                                best = v
                elif isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(cur, list):
            stack.extend(x for x in cur if isinstance(x, (dict, list)))
    return best

def resolve_snapshot(path, probe_keys):
    b2 = stage_blob(path, 2)  # origin/base side
    b3 = stage_blob(path, 3)  # ours/replay side
    j2, j3 = json.loads(b2), json.loads(b3)
    t2, t3 = deep_ts(j2, probe_keys), deep_ts(j3, probe_keys)
    print(f"[{path}] ts base-side={t2!r} replay-side={t3!r}")
    if t3 is not None and (t2 is None or t3 >= t2):
        side, blob, tag = 3, b3, "replay-side"
    elif t2 is not None:
        side, blob, tag = 2, b2, "base-side"
    else:
        raise RuntimeError(f"{path}: no ts on either side, fail-closed manual")
    print(f"[{path}] take {tag}")
    with open(path, "wb") as f:
        f.write(blob)
    json.loads(open(path, "rb").read())  # parse-verify (r185)
    return side

def resolve_twin(json_path, md_path):
    side = resolve_snapshot(json_path, ("generated", "generated_at", "ts"))
    blob = stage_blob(md_path, side)
    with open(md_path, "wb") as f:
        f.write(blob)
    print(f"[{md_path}] byte-copied from same side :{side} (twin coupling r329)")

if __name__ == "__main__":
    resolve_snapshot("results/_attrition_guard_scan.json", ("ts", "generated"))
    resolve_snapshot("results/fundamental_b_layer_filter.json", ("updated", "ts"))
    resolve_twin("docs/daily_report/REPORT-2026-10-10.json", "docs/daily_report/REPORT-2026-10-10.md")
    # all LIVE-* twins must take the SAME side: probe dated json first, apply to all 4
    side = resolve_snapshot("docs/live_usage/LIVE-2026-10-10.json", ("generated", "generated_at", "ts"))
    for p in ["docs/live_usage/LIVE-2026-10-10.md", "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"]:
        blob = stage_blob(p, side)
        with open(p, "wb") as f:
            f.write(blob)
        if p.endswith(".json"):
            json.loads(open(p, "rb").read())
        print(f"[{p}] byte-copied from same side :{side}")
    print("ALL 8 REMAINING FACES RESOLVED")
