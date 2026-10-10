# r963 storm-2 resolver: 9 manual faces (second rebase, onto d771dc969)
# r648 law: stage read via ls-files -u sha -> cat-file (fallback when :N: empty-read rc0)
# E52: normalize ts before compare; r100/R350 probe laws; staged blob probing only.
import subprocess, json, re, sys, os

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def stage_bytes(path, stage):
    r = subprocess.run([GIT, "-C", REPO, "show", ":%s:%s" % (stage, path)], capture_output=True)
    if r.returncode == 0 and r.stdout:
        return r.stdout
    # r648 fallback: sha channel
    u = subprocess.run([GIT, "-C", REPO, "ls-files", "-u", "--", path], capture_output=True)
    for line in u.stdout.decode("utf-8", "replace").splitlines():
        parts = line.split("\t", 1)
        meta = parts[0].split()
        if len(meta) >= 2 and meta[2] == str(stage):
            sha = meta[1]
            c = subprocess.run([GIT, "-C", REPO, "cat-file", "-p", sha], capture_output=True)
            if c.returncode == 0 and c.stdout:
                return c.stdout
    if r.returncode == 0:
        return None  # stage exists but empty? treat missing
    return None

WALL_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?\s*$")

def e52_norm(s):
    s = s.strip()
    if len(s) >= 11 and s[10] == " ":
        s = s[:10] + "T" + s[11:]
    return re.sub(r"(Z|[+-]\d{2}:?\d{2})$", "", s)

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
    o_key, t_key = op or oa, tp or ta
    print("  probe[%s] origin=%s replay=%s" % (os.path.basename(path), o_key, t_key))
    if o_key is None and t_key is None:
        sys.exit("no ts either side: " + path)
    if t_key is None: return 2, o_key
    if o_key is None: return 3, t_key
    if t_key > o_key: return 3, t_key
    if o_key > t_key: return 2, o_key
    print("  TIE -> origin per r140")
    return 2, o_key

def write_side(path, side):
    b = stage_bytes(path, side)
    if b is None: sys.exit("missing stage blob :%s:%s" % (side, path))
    if b"<<<<<<<" in b: sys.exit("markers in staged blob: " + path)
    open(os.path.join(REPO, path), "wb").write(b)
    print("  wrote %s <- :%s: (%d bytes)" % (path, side, len(b)))

def vj(path):
    raw = open(os.path.join(REPO, path), "rb").read()
    if b"<<<<<<<" in raw: sys.exit("marker in " + path)
    json.loads(raw.decode("utf-8-sig"))
    print("  parse-verify OK: %s" % path)

summary = []
side, ts = pick("docs/daily_report/REPORT-2026-10-11.json")
summary.append("REPORT twins <- :%s: (%s)" % (side, ts))
write_side("docs/daily_report/REPORT-2026-10-11.json", side)
write_side("docs/daily_report/REPORT-2026-10-11.md", side)
vj("docs/daily_report/REPORT-2026-10-11.json")

side, ts = pick("docs/live_usage/LIVE-2026-10-11.json")
summary.append("LIVE family <- :%s: (%s)" % (side, ts))
for p in ["docs/live_usage/LIVE-2026-10-11.json", "docs/live_usage/LIVE-2026-10-11.md",
          "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"]:
    write_side(p, side)
vj("docs/live_usage/LIVE-2026-10-11.json")
vj("docs/live_usage/LIVE-latest.json")

for p in ["results/fundamental_b_layer_filter.json",
          "results/_attrition_guard_scan.json", "results/_r686bmb_d19_check.json"]:
    side, ts = pick(p)
    summary.append("%s <- :%s: (%s)" % (os.path.basename(p), side, ts))
    write_side(p, side)
    vj(p)

print("=== SUMMARY ===")
for l in summary: print(l)
print("9 MANUAL FACES RESOLVED (storm-2)")
