"""r240 bm-c rebase-collision resolver (72-UU vs origin/main bm-a r440 push).

Per r444 canon + bigmoney-conflict-resolve skill sec.2/3 + r238 bm-c precedent:
- A/B-family lane faces (5): scripts/merge_lane_views.py resolve (reads :1:/:2:/:3:
  stages from the active rebase index, union recipes built-in)
- dual-run JSON marks/snapshot faces: deep-ts take-new (probe STAGED blobs
  :2:/:3:, tie -> :2: = onto side per r140)
- twins: json picks side by deep-ts, md byte-copies same side;
  js-wrapper twin (dashboard_status.js) follows the .json side
- t24 cells ledger: (id,cutoff) key-dedupe with later-ts-wins, order preserved
- x2 watch log: line-identity union, ts-sorted when every line carries ts
Probe diagnostics (sizes/ts/equality/line counts) = results/_r240bmc_probe.py.
Trail law: this script is the evidence.
"""
import json, re, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {spec} rc={r.returncode}")
    return r.stdout

WALL = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
KEYP = ("generated", "updated", "asof", "ts", "lastseen", "cutoff", "timestamp")

def deep_ts(obj, best=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if isinstance(v, str) and any(nk.startswith(p) for p in KEYP) and WALL.match(v):
                if v > best:
                    best = v
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best

def probe(side, path):
    try:
        return deep_ts(json.loads(blob(f":{side}:{path}").decode("utf-8")))
    except Exception:
        return ""

def take(side, path):
    data = blob(f":{side}:{path}")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)

def resolve_snapshot(path):
    t2, t3 = probe("2", path), probe("3", path)
    side = "2" if t2 >= t3 else "3"
    n = take(side, path)
    json.loads(open(path, "rb").read().decode("utf-8"))  # parse-verify
    print(f"[snapshot] {path}: :2:={t2 or '(none)'} :3:={t3 or '(none)'} -> side {side} ({n}B)")

def resolve_twin(json_path, md_paths):
    t2, t3 = probe("2", json_path), probe("3", json_path)
    side = "2" if t2 >= t3 else "3"
    for p in [json_path] + md_paths:
        take(side, p)
    json.loads(open(json_path, "rb").read().decode("utf-8"))
    print(f"[twin] {json_path}+{len(md_paths)}md: :2:={t2 or '(none)'} :3:={t3 or '(none)'} -> side {side}")

def resolve_lane(face_path):
    r = subprocess.run([sys.executable, "scripts/merge_lane_views.py", "resolve", face_path],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(f"[lane] {face_path}: rc={r.returncode}")
    for ln in (r.stdout or "").splitlines():
        print(f"    {ln}")
    if r.returncode != 0:
        print(f"    !! stderr: {(r.stderr or '')[:300]}")
        raise RuntimeError(f"merge_lane_views resolve failed for {face_path}")
    json.loads(open(face_path, "rb").read().decode("utf-8"))  # parse-verify

def lines_of(side, path):
    return [l for l in blob(f":{side}:{path}").decode("utf-8").splitlines() if l.strip()]

def resolve_t24_cells(path):
    l2, l3 = lines_of("2", path), lines_of("3", path)
    def key_ts(l):
        d = json.loads(l)
        return ((str(d.get("id")), str(d.get("cutoff"))), str(d.get("ts", "")))
    k3 = {}
    for l in l3:
        k, t = key_ts(l)
        if k not in k3 or t > k3[k][1]:
            k3[k] = (l, t)
    out, seen = [], set()
    replaced = 0
    for l in l2:
        k, t = key_ts(l)
        if k in k3:
            cand, ct = k3[k]
            if k not in seen:
                if ct > t:
                    out.append(cand)  # later-ts variant from replay side
                    replaced += 1
                else:
                    out.append(l)
                seen.add(k)
            # same-key earlier variant dropped
        else:
            out.append(l)
    appended = 0
    for l in l3:
        k, t = key_ts(l)
        if k not in seen and l not in out:
            out.append(l)
            seen.add(k)
            appended += 1
    for l in out:
        json.loads(l)  # parse-verify every ledger line
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(out) + ("\n" if out else ""))
    print(f"[t24-ledger] {path}: :2:={len(l2)} :3:={len(l3)} -> {len(out)} lines "
          f"(later-ts replaced {replaced}, appended {appended})")

def resolve_x2_log(path):
    l2, l3 = lines_of("2", path), lines_of("3", path)
    s2 = set(l2)
    union = list(l2) + [l for l in l3 if l not in s2]
    def ts_of(l):
        m = re.match(r'"ts":\s*"([^"]+)"', l)
        return m.group(1) if m else ""
    if all(ts_of(l) for l in union):
        union.sort(key=ts_of)  # chronological merge of both machines' runs
        mode = "ts-sorted"
    else:
        mode = ":2:-order + only3 append"
    malformed = 0
    for l in union:
        try:
            json.loads(l)
        except Exception:
            malformed += 1  # pre-existing shared defect (15:03:51 concat line,
            # byte-identical on :2:/:3:/base) -- preserve as-is, zero-loss law
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(union) + ("\n" if union else ""))
    print(f"[x2-log] {path}: :2:={len(l2)} :3:={len(l3)} -> {len(union)} lines ({mode}, "
          f"pre-existing malformed preserved={malformed})")

if __name__ == "__main__":
    r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                       capture_output=True, text=True, encoding="utf-8")
    unmerged = sorted(p for p in r.stdout.splitlines() if p.strip())
    print(f"=== resolving {len(unmerged)} unmerged paths ===")
    lane_faces = {"results/compute_audit.json", "results/regime_state.json",
                  "results/update_status.json", "results/lhb_update_status.json",
                  "results/token_usage.json"}
    twins = {"docs/daily_report/REPORT-2026-09-29.json": ["docs/daily_report/REPORT-2026-09-29.md"],
             "docs/live_usage/LIVE-2026-09-29.json": ["docs/live_usage/LIVE-2026-09-29.md"],
             "docs/live_usage/LIVE-latest.json": ["docs/live_usage/LIVE-latest.md"]}
    done = 0
    for p in unmerged:
        if p in lane_faces:
            resolve_lane(p)
        elif p == "results/t24_prospect_paper_cells.jsonl":
            resolve_t24_cells(p)
        elif p == "results/x2_watch_log.jsonl":
            resolve_x2_log(p)
        elif p in twins:
            resolve_twin(p, twins[p])
        elif p.endswith(".md") or p.endswith(".js"):
            continue  # handled as twin/md/js follower of its json side
        else:
            resolve_snapshot(p)
        done += 1
    # js-wrapper twin follows dashboard_status.json side
    t2, t3 = probe("2", "results/dashboard_status.json"), probe("3", "results/dashboard_status.json")
    side = "2" if t2 >= t3 else "3"
    n = take(side, "results/dashboard_status.js")
    print(f"[js-twin] dashboard_status.js follows json side {side} ({n}B)")
    # residual check: every unmerged path now differs from index conflict state
    r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                       capture_output=True, text=True, encoding="utf-8")
    left = [p for p in r.stdout.splitlines() if p.strip()]
    print(f"resolver done: {done+1} faces resolved, residual UU={len(left)}")
    for p in left:
        print(f"  !! STILL UNMERGED: {p}")
    sys.exit(1 if left else 0)
