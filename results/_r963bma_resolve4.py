# r963 estate-continuation rebase resolver: 13 manual faces (twins + js wrapper + snapshots + 2 hand-classified receipts)
# Probe laws: r311 deep-scan, r319 path existence, r100/R350 key-normalize + wall-clock shape + no exclude-lists,
# E52: mixed ts-format lexicographic poison -> normalize (space->T, strip tz) BEFORE max-compare.
# Staged blob probing (:2: origin / :3: replay), never working tree (R350).
import subprocess, json, re, sys, os

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def stage_bytes(path, stage):
    r = subprocess.run([GIT, "-C", REPO, "show", ":%s:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

WALL_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?\s*$")

def e52_norm(s):
    # space -> T at position 10; strip tz suffix -> comparable canonical
    s = s.strip()
    if len(s) >= 11 and s[10] == " ":
        s = s[:10] + "T" + s[11:]
    s = re.sub(r"(Z|[+-]\d{2}:?\d{2})$", "", s)
    return s

def norm(k):
    return k.replace("_", "").replace("-", "").lower()

PREFIXES = ("generated", "updated", "ts", "asof", "cutoff")

def deep_ts(obj):
    best_pref, best_any = None, None
    def rec(o):
        nonlocal best_pref, best_any
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and WALL_RE.match(v):
                    nv = e52_norm(v)
                    if best_any is None or nv > best_any:
                        best_any = nv
                    if norm(k).startswith(PREFIXES) and (best_pref is None or nv > best_pref):
                        best_pref = nv
                if isinstance(v, (dict, list)):
                    rec(v)
        elif isinstance(o, list):
            for it in o:
                rec(it)
    rec(obj)
    return best_pref, best_any

def probe(path, stage):
    b = stage_bytes(path, stage)
    if b is None:
        return None, None
    obj = json.loads(b.decode("utf-8-sig"))
    return deep_ts(obj)

def pick(path):
    op, oa = probe(path, 2)
    tp, ta = probe(path, 3)
    o_key = op or oa
    t_key = tp or ta
    print("  probe[%s] origin=%s replay=%s" % (os.path.basename(path), o_key, t_key))
    if o_key is None and t_key is None:
        sys.exit("no ts either side: " + path)
    if t_key is None:
        return 2, o_key
    if o_key is None:
        return 3, t_key
    if t_key > o_key:
        return 3, t_key
    if o_key > t_key:
        return 2, o_key
    print("  TIE -> origin/HEAD per r140")
    return 2, o_key

def write_side(path, side):
    b = stage_bytes(path, side)
    if b is None:
        sys.exit("missing stage blob :%s:%s" % (side, path))
    if b"<<<<<<<" in b:
        sys.exit("markers in staged blob: " + path)
    with open(os.path.join(REPO, path), "wb") as f:
        f.write(b)
    print("  wrote %s <- :%s: (%d bytes)" % (path, side, len(b)))

def verify_json(path):
    raw = open(os.path.join(REPO, path), "rb").read()
    if b"<<<<<<<" in raw:
        sys.exit("marker in " + path)
    json.loads(raw.decode("utf-8-sig"))
    print("  parse-verify OK: %s" % path)

summary = []

# 1-2. REPORT twin (json decides, md same side, byte copy)
side, ts = pick("docs/daily_report/REPORT-2026-10-11.json")
summary.append("REPORT twins <- :%s: (%s)" % (side, ts))
write_side("docs/daily_report/REPORT-2026-10-11.json", side)
write_side("docs/daily_report/REPORT-2026-10-11.md", side)
verify_json("docs/daily_report/REPORT-2026-10-11.json")

# 3-6. LIVE family (dated json decides, all 4 same side)
side, ts = pick("docs/live_usage/LIVE-2026-10-11.json")
summary.append("LIVE family <- :%s: (%s)" % (side, ts))
for p in ["docs/live_usage/LIVE-2026-10-11.json", "docs/live_usage/LIVE-2026-10-11.md",
          "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"]:
    write_side(p, side)
verify_json("docs/live_usage/LIVE-2026-10-11.json")
verify_json("docs/live_usage/LIVE-latest.json")

# 7-8. dashboard pair: json snapshot decides side; js wrapper byte-copy same side (R209: whole bytes, no json.dumps)
side, ts = pick("results/dashboard_status.json")
summary.append("dashboard pair <- :%s: (%s)" % (side, ts))
write_side("results/dashboard_status.json", side)
write_side("results/dashboard_status.js", side)
verify_json("results/dashboard_status.json")
js = open(os.path.join(REPO, "results/dashboard_status.js"), "rb").read()
assert b"window.DASH_DATA" in js, "js wrapper stripped?!"
print("  js wrapper integrity OK (window.DASH_DATA present)")

# 9-12. plain snapshots take-new
for p in ["results/fundamental_b_layer_filter.json", "results/scorecard_v1.json",
          "results/strategy_scorecard.json"]:
    side, ts = pick(p)
    summary.append("%s <- :%s: (%s)" % (os.path.basename(p), side, ts))
    write_side(p, side)
    verify_json(p)

# 13-14. hand-classified receipts (UNKNOWN->snapshot per-run scan outputs, take-new by ts)
for p in ["results/_attrition_guard_scan.json", "results/_r686bmb_d19_check.json"]:
    side, ts = pick(p)
    summary.append("%s <- :%s: (%s)" % (os.path.basename(p), side, ts))
    write_side(p, side)
    verify_json(p)

print("=== RESOLUTION SUMMARY ===")
for l in summary:
    print(l)
print("ALL 13 MANUAL FACES RESOLVED (E52-normalized probes)")
