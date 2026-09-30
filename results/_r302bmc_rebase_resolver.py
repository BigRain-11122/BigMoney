# r302 bm-c rebase conflict resolver (canon: r415 deep-ts take-new / r373+r500 key-union / r294 union-domain)
# Resolves the 19 UU faces of round 302 rebase onto bm-a r502 same-window S6 outputs.
import subprocess, json, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def show_raw(spec):
    return subprocess.check_output(["git", "show", spec])

def uu_list():
    out = subprocess.check_output(["git", "diff", "--name-only", "--diff-filter=U"], cwd=ROOT).decode("utf-8")
    return [l for l in out.splitlines() if l.strip()]

TS_RE = re.compile(r"2026-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?(\.\d+)?")

def json_ts(d):
    for k in ("ts", "updated", "generated", "updated_at", "asof", "now"):
        v = d.get(k) if isinstance(d, dict) else None
        if isinstance(v, str) and TS_RE.search(v):
            return TS_RE.search(v).group(0)
    return None

def text_ts(b):
    ms = TS_RE.findall(b.decode("utf-8", "replace")) if False else [m.group(0) for m in TS_RE.finditer(b.decode("utf-8", "replace"))]
    return max(ms) if ms else None

def probe(path, b):
    if path.endswith(".json"):
        try:
            return json_ts(json.loads(b.decode("utf-8")))
        except Exception:
            return text_ts(b)
    return text_ts(b)

def take_new(path, b2, b3):
    t2, t3 = probe(path, b2), probe(path, b3)
    if t2 and t3:
        return (b3, "mine(newer)") if t3 >= t2 else (b2, "origin(newer)")
    if t3:
        return (b3, "mine(only-ts)")
    return (b2, "origin(fallback)")

resolved = []
for path in uu_list():
    b2 = show_raw(":2:" + path)   # ours = origin/main side (bm-a r502)
    b3 = show_raw(":3:" + path)   # theirs = my round 302 side
    if path == "CODELY.md":
        o = b2.decode("utf-8")
        marker = "r302 bm-c"
        if marker in o:
            data, how = b2, "origin(already-contains-r302)"
        else:
            nl = "\r\n" if b"\r\n" in b2[:2000] else "\n"
            mine_line = [l for l in b3.decode("utf-8").splitlines() if marker in l]
            data = b2
            for l in mine_line:
                data = (data.decode("utf-8") + nl + l).encode("utf-8")
            how = "union(origin+%d r302 lines)" % len(mine_line)
    elif path == "results/compute_audit.json":
        d2, d3 = json.loads(b2), json.loads(b3)
        m = dict(d2)
        lt2, lt3 = json_ts(d2.get("latest", {})), json_ts(d3.get("latest", {}))
        m["latest"] = d3["latest"] if (lt3 and (not lt2 or lt3 >= lt2)) else d2["latest"]
        h2, h3 = d2.get("history", []), d3.get("history", [])
        by_ts = {}
        for r in h2 + h3:
            k = r.get("ts") or json.dumps(r, sort_keys=True)[:80]
            by_ts[k] = r  # later assignment wins ties -> stable
        keys = sorted(by_ts)
        m["history"] = [by_ts[k] for k in keys][-max(len(h2), len(h3)):]
        data = json.dumps(m, ensure_ascii=False, indent=2).encode("utf-8")
        how = "union(latest take-new ts, history key-union %d+%d->%d)" % (len(h2), len(h3), len(m["history"]))
    elif path == "results/token_usage.json":
        d2, d3 = json.loads(b2), json.loads(b3)
        g2, g3 = d2.get("generated", ""), d3.get("generated", "")
        base = d3 if g3 >= g2 else d2  # fresher run face
        m2, m3 = d2.get("machines", {}), d3.get("machines", {})
        merged = dict(m2)
        for k, v in m3.items():
            if k not in merged:
                merged[k] = v
            else:
                t2x, t3x = None, None
                for kk in ("ts", "updated", "generated", "last_seen"):
                    if isinstance(v, dict) and kk in v: t3x = v[kk]; break
                    if isinstance(merged[k], dict) and kk in merged[k]: t2x = merged[k][kk]; break
                if t3x and (not t2x or t3x >= t2x):
                    merged[k] = v
        base["machines"] = merged
        data = json.dumps(base, ensure_ascii=False, indent=2).encode("utf-8")
        how = "hybrid(generated take-new + machines per-key ts-union %d keys)" % len(merged)
    else:
        data, how = take_new(path, b2, b3)
    with open(os.path.join(ROOT, path), "wb") as f:
        f.write(data)
    resolved.append((path, how))

for p, h in resolved:
    print("RESOLVED %s :: %s" % (p, h))
print("total %d faces resolved" % len(resolved))
