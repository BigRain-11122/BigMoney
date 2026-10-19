# r1080 stage-2 UU resolver (rebase retry onto 8578dcadff; 9 transient faces, r1078/r1080 recipes)
import json, subprocess, sys

MINE = "d3b7a70a2a"  # my r1080 commit (replayed once) being replayed again

def blob(rev, path):
    r = subprocess.run(["git", "show", rev + ":" + path], capture_output=True, text=True, encoding="utf-8")
    return r.stdout if r.returncode == 0 else None

def jload(rev, path):
    try:
        return json.loads(blob(rev, path))
    except Exception:
        return None

def jwrite(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    json.load(open(path, encoding="utf-8"))
    print("resolved", path)

def ts_of(d, *keys):
    for k in keys:
        if isinstance(d, dict) and k in d:
            return str(d[k])
    return ""

bad = 0

# history-union faces (r965 recipe)
for path, hkey in (("results/compute_audit.json", ("ts", "time")), ("results/regime_state.json", ("asof", "ts"))):
    o, m = jload("HEAD", path), jload(MINE, path)
    hist = {json.dumps(h, sort_keys=True, ensure_ascii=False): h for h in (o.get("history") or [])}
    for h in (m.get("history") or []):
        hist.setdefault(json.dumps(h, sort_keys=True, ensure_ascii=False), h)
    merged = sorted(hist.values(), key=lambda h: str(h.get(hkey[0], h.get(hkey[-1], ""))))
    lk = ("updated", "ts") if path.endswith("regime_state.json") else ("ts",)
    latest = m.get("latest", m) if ts_of(m, *lk) >= ts_of(o, *lk) else o.get("latest", o)
    jwrite(path, {"latest": latest, "history": merged} if path.endswith("compute_audit.json") else dict(latest, history=merged))
    print(path, "union hist=", len(merged))

# transient newer-ts faces
for path, keys in (
    ("results/update_status.json", ("updated", "ts")),
    ("results/_attrition_guard_scan.json", ("ts",)),
    ("results/fundamental_b_layer_filter.json", ("updated", "ts")),
    ("results/_r686bmb_d19_check.json", ("ts",)),
    ("results/d19_watermark.json", ("ts",)),
    ("results/scorecard_v1.json", ("generated", "generated_at", "ts", "updated")),
    ("results/strategy_scorecard.json", ("generated", "generated_at", "ts", "updated")),
):
    o, m = jload("HEAD", path), jload(MINE, path)
    win = m if ts_of(m, *keys) >= ts_of(o, *keys) else o
    print(path, "winner=%s ts=%s/%s" % ("MINE" if win is m else "HEAD", ts_of(m, *keys), ts_of(o, *keys)))
    jwrite(path, win)

for p in ("results/compute_audit.json", "results/regime_state.json", "results/update_status.json",
          "results/_attrition_guard_scan.json", "results/fundamental_b_layer_filter.json",
          "results/_r686bmb_d19_check.json", "results/d19_watermark.json",
          "results/scorecard_v1.json", "results/strategy_scorecard.json"):
    r = subprocess.run(["git", "add", "--", p], capture_output=True, text=True)
    if r.returncode != 0:
        print("ADD-FAIL", p, r.stderr[:150])
        bad += 1
print("STAGED-OK" if bad == 0 else "BAD=%d" % bad)
sys.exit(1 if bad else 0)
