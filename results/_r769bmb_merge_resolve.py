# _r769bmb_merge_resolve.py -- r769 bm-b merge conflict resolver (r758/r668 family recipes)
# recipes: take-freshest(r756 ts-normalized) / rolling-ledger-union / twin-copy / host-owned->origin
import subprocess, json, re, sys, os
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(args):
    return subprocess.run(args, capture_output=True, cwd=REPO)

def blob(stage, path):
    r = run(["git", "show", ":%s:%s" % (stage, path)])
    return r.stdout if r.returncode == 0 else None

TS_PATTERNS = [
    ("generated_at",), ("updated",), ("ts",), ("generated",), ("last_run",), ("cutoff",),
]
TS_FORMATS = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S+08:00"]

def probe_ts(b):
    if b is None:
        return None
    try:
        j = json.loads(b.decode("utf-8"))
    except Exception:
        m = re.search(rb'"(generated_at|updated|ts)"\s*:\s*"([^"]+)"', b)
        return m.group(2).decode("utf-8") if m else None
    for key in ("generated_at", "updated", "ts", "generated", "last_run"):
        v = j.get(key) if isinstance(j, dict) else None
        if isinstance(v, str) and len(v) >= 10:
            s = v.replace("T", " ")[:19]
            try:
                return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                return v
        if isinstance(v, dict):
            for k2 in ("generated_at", "updated", "ts"):
                v2 = v.get(k2)
                if isinstance(v2, str) and len(v2) >= 10:
                    s = v2.replace("T", " ")[:19]
                    try:
                        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        return v2
    return None

def write(path, data):
    full = os.path.join(REPO, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "wb").write(data)

def take_fresh(path):
    a, b = blob("2", path), blob("3", path)
    ta, tb = probe_ts(a), probe_ts(b)
    if ta is None and tb is None:
        side, data = "theirs(origin)", b if b is not None else a
    elif tb is None or (ta is not None and ta >= tb):
        side, data = "ours", a
    else:
        side, data = "theirs(origin)", b
    write(path, data)
    print(json.dumps({"path": path, "recipe": "take-freshest", "side": side, "ours_ts": ta, "theirs_ts": tb}))

def take_side(path, stage, why):
    data = blob(stage, path)
    assert data is not None, path
    write(path, data)
    print(json.dumps({"path": path, "recipe": "take-%s" % stage, "why": why}))

def ledger_union(path):
    a, b = blob("2", path), blob("3", path)
    ja, jb = json.loads(a.decode("utf-8")), json.loads(b.decode("utf-8"))
    out = dict(jb if probe_ts(b) and probe_ts(a) and probe_ts(b) > probe_ts(a) else ja)
    for coll in ("history", "transitions"):
        if coll in ja or coll in jb:
            A = ja.get(coll, []); B = jb.get(coll, [])
            seen = set(); merged = []
            for row in A + B:
                key = json.dumps(row, sort_keys=True)
                if key not in seen:
                    seen.add(key); merged.append(row)
            def tsr(row):
                for k in ("ts", "time", "generated_at", "updated"):
                    if isinstance(row, dict) and k in row:
                        s = str(row[k]).replace("T", " ")[:19]
                        try:
                            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").isoformat()
                        except Exception:
                            return str(row[k])
                return ""
            merged.sort(key=tsr)
            out[coll] = merged
            print(json.dumps({"path": path + "#" + coll, "recipe": "union+ts-stable-sort", "ours": len(A), "theirs": len(B), "union": len(merged)}))
    write(path, json.dumps(out, indent=2, ensure_ascii=False).encode("utf-8") + b"\n")
    print(json.dumps({"path": path, "recipe": "ledger-union+state-take-freshest"}))

# --- freshest-class (deterministic regen snapshots) ---
for p in ["docs/daily_report/REPORT-2026-10-06.json",
          "docs/live_usage/LIVE-2026-10-06.json",
          "docs/live_usage/LIVE-latest.json",
          "results/_attrition_guard_scan.json",
          "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json",
          "results/lhb_update_status.json",
          "results/update_status.json",
          "results/token_usage.json"]:
    take_fresh(p)

# --- md twins follow json twins ---
for jp, mp in [("docs/daily_report/REPORT-2026-10-06.json", "docs/daily_report/REPORT-2026-10-06.md"),
               ("docs/live_usage/LIVE-2026-10-06.json", "docs/live_usage/LIVE-2026-10-06.md"),
               ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md")]:
    jb = open(os.path.join(REPO, jp), "rb").read()
    ja = json.loads(jb.decode("utf-8"))
    gen = ja.get("generated_at") or probe_ts(jb)
    for st, name in (("2", "ours"), ("3", "theirs")):
        sb = blob(st, mp)
        if sb is None: continue
        try:
            sj = re.search(rb"(generated_at|updated)\s*[\"':]+\s*([\d\-T :]+)", sb)
            s_ts = sj.group(2).decode("utf-8").replace("T", " ")[:19] if sj else None
        except Exception:
            s_ts = None
        if s_ts and gen and s_ts[:19] == str(gen).replace("T", " ")[:19]:
            write(mp, sb)
            print(json.dumps({"path": mp, "recipe": "twin-follow-json", "side": name}))
            break
    else:
        take_fresh(mp)

# --- ledger unions ---
ledger_union("results/compute_audit.json")
ledger_union("results/regime_state.json")

# --- host=bm-a single-writer faces -> origin verbatim ---
take_side("results/dashboard_status.json", "3", "host=bm-a single-writer (r378) -> origin")
dash = open(os.path.join(REPO, "results/dashboard_status.json"), "rb").read()
write("results/dashboard_status.js", b"var dashboardStatus = " + dash.rstrip(b"\n") + b";\n")
print(json.dumps({"path": "results/dashboard_status.js", "recipe": "js-wrapper twin byte-copy (R209)"}))

# --- scorecard twins: host=bm-a -> origin strategy_scorecard bytes, twin-copy v1 ---
take_side("results/strategy_scorecard.json", "3", "host=bm-a writer -> origin")
sc = open(os.path.join(REPO, "results/strategy_scorecard.json"), "rb").read()
write("results/scorecard_v1.json", sc)
print(json.dumps({"path": "results/scorecard_v1.json", "recipe": "twin-byte-copy", "bytes": len(sc)}))

# finalize: stage all resolved
r = run(["git", "add", "-A"])
uu = run(["git", "diff", "--name-only", "--diff-filter=U"]).stdout.decode().strip()
print("staged_unmerged_after:", len(uu.splitlines()))
assert len(uu.splitlines()) == 0, "unmerged remain: " + uu
print("RESOLVE PASS")
