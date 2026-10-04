import subprocess, json, os, re

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
GEN_RE = re.compile(r"generated[^\d]{0,20}(20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})", re.I)

def show(rev, path):
    r = subprocess.run(["git", "show", rev + ":" + path], capture_output=True, cwd=R, timeout=60)
    if r.returncode != 0:
        raise RuntimeError("git show %s:%s failed: %s" % (rev, path, r.stderr.decode("utf-8", "replace")[:300]))
    return r.stdout

def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False)

def tskey(d):
    for k in ("generated", "ts", "updated", "updated_at", "generated_at", "as_of"):
        if k in d:
            return str(d[k])
    return ""

def ts_text(raw):
    m = GEN_RE.search(raw) or TS_RE.search(raw)
    return m.group(0) if m else ""

def resolve_ts_newer(path):
    """regen snapshot face: honest-ts newer wins, json or text."""
    o_raw = show("HEAD", path)
    t_raw = show("MERGE_HEAD", path)
    o_txt, t_txt = None, None
    try:
        ours = json.loads(o_raw.decode("utf-8"))
        theirs = json.loads(t_raw.decode("utf-8"))
        o, t = tskey(ours), tskey(theirs)
        if not o:
            o = ts_text(o_raw.decode("utf-8"))
        if not t:
            t = ts_text(t_raw.decode("utf-8"))
        if not o and not t:
            merged, pick = theirs, "theirs(no-ts-fallback)"
        elif o and (not t or o >= t):
            merged, pick = ours, "ours"
        else:
            merged, pick = theirs, "theirs"
        with open(os.path.join(R, path), "w", encoding="utf-8", newline="\n") as f:
            if path.endswith(".json"):
                json.dump(merged, f, indent=1, ensure_ascii=False)
                json.loads(open(os.path.join(R, path), "rb").read().decode("utf-8"))
            else:
                pick = "TEXT:" + pick
                merged_bytes = o_raw if pick.endswith("ours") else t_raw
                with open(os.path.join(R, path), "wb") as f:
                    f.write(merged_bytes)
        return "%s pick=%s (ours=%s theirs=%s)" % (path, pick, o or "?", t or "?")
    except (ValueError, UnicodeDecodeError):
        # text face (md/js): byte-level honest ts
        o = ts_text(o_raw.decode("utf-8", "replace"))
        t = ts_text(t_raw.decode("utf-8", "replace"))
        if o and (not t or o >= t):
            pick = "ours"
            data = o_raw
        else:
            pick = "theirs" if t else "theirs(no-ts-fallback)"
            data = t_raw
        with open(os.path.join(R, path), "wb") as f:
            f.write(data)
        return "%s TEXT pick=%s (ours=%s theirs=%s)" % (path, pick, o or "?", t or "?")

# --- compute_audit.json: cross-machine union (v2 recipe) ---
P = "results/compute_audit.json"
ours_ca = json.loads(show("HEAD", P).decode("utf-8"))
theirs_ca = json.loads(show("MERGE_HEAD", P).decode("utf-8"))
oh, th = ours_ca["history"], theirs_ca["history"]
seen = set()
merged_hist = []
for row in oh + th:
    k = canon(row)
    if k not in seen:
        seen.add(k)
        merged_hist.append(row)
assert all(canon(r) in seen for r in oh) and all(canon(r) in seen for r in th), "zero-loss FAILED"
latest = ours_ca["latest"] if ours_ca["latest"]["ts"] >= theirs_ca["latest"]["ts"] else theirs_ca["latest"]
with open(os.path.join(R, P), "w", encoding="utf-8", newline="\n") as f:
    json.dump({"latest": latest, "history": merged_hist}, f, indent=1, ensure_ascii=False)
d = json.loads(open(os.path.join(R, P), "rb").read().decode("utf-8"))
assert len(d["history"]) == len(seen)
print("compute_audit union: latest=%s ours_hist=%d theirs_hist=%d merged=%d zero-loss PASS" %
      (latest["ts"], len(oh), len(th), len(seen)))

FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
]
for f in FACES:
    print(resolve_ts_newer(f))
print("RESOLVE DONE")
