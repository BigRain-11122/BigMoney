# r163 storm resolver: 7 non-ALL_FACES UU faces per canonical recipes (r327 twin-coupling / R209 js-wrapper / r100+R350 hardened deep-ts probe).
# Probe STAGED blobs (:2: = origin side, :3: = local side, r351 rebase law); tie -> origin/HEAD side (r140/R208).
# Write winner bytes to working tree; parse-verify before add (r185 law).
import json, re, subprocess, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout  # bytes

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

def norm(k):
    return k.replace("_", "").replace("-", "").lower()

PREFIXES = ("asof", "updated", "generated", "lastseen", "ts", "clockread", "timestamp")

def deep_ts(obj, path=""):
    """Hardened probe (r100/R350): recursive walk, normalized-key prefix match, value must be
    timestamp-shaped WITH time-of-day to feed wall-clock max; no key-EXCLUDE lists."""
    best = None
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}"
            if isinstance(v, str) and TS_RE.match(v) and norm(k).startswith(PREFIXES):
                if best is None or v > best[0]:
                    best = (v, p)
            sub = deep_ts(v, p)
            if sub and (best is None or sub[0] > best[0]):
                best = sub
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            sub = deep_ts(v, f"{path}[{i}]")
            if sub and (best is None or sub[0] > best[0]):
                best = sub
    return best

def probe_json(b):
    d = json.loads(b.decode("utf-8-sig"))
    return deep_ts(d)

def probe_js_wrapper(b):
    m = re.search(rb"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?", b, re.S)
    if not m:
        return None, None
    d = json.loads(m.group(1).decode("utf-8-sig"))
    return deep_ts(d), d

results = []
def resolve_snapshot(path, mode="json"):
    b2, b3 = blob("2", path), blob("3", path)
    if b2 is None and b3 is None:
        results.append((path, "ERROR", "both stages missing"))
        return
    if b2 is None:
        side, win = 3, b3
    elif b3 is None:
        side, win = 2, b2
    else:
        if mode == "js":
            t2, _ = probe_js_wrapper(b2) or (None, None)
            t3, _ = probe_js_wrapper(b3) or (None, None)
        else:
            t2 = probe_json(b2)
            t3 = probe_json(b3)
        if t2 is None and t3 is None:
            side = 2  # no ts anywhere: HEAD/origin (r140)
        elif t3 is None:
            side = 2
        elif t2 is None:
            side = 3
        else:
            side = 3 if t3[0] > t2[0] else 2  # tie -> origin/HEAD side
        win = b2 if side == 2 else b3
    full = path if "/" in path else path
    with open(f"{ROOT}\\{full}", "wb") as f:
        f.write(win)
    # parse-verify (r185)
    if mode == "js":
        ok = re.search(rb"window\.DASH_DATA\s*=\s*\{.*\}\s*;?", win, re.S) is not None
    else:
        try:
            json.loads(win.decode("utf-8-sig"))
            ok = True
        except Exception:
            ok = False
    assert ok, f"parse-verify failed: {path}"
    assert b"<<<<<<<" not in win and b">>>>>>>" not in win, f"conflict marker in winner: {path}"
    results.append((full, "take-:2:" if (b2 is not None and win is b2) else "take-:3:", f"probe2={probe_summary(path,'2',mode)} probe3={probe_summary(path,'3',mode)}"))

def probe_summary(path, stage, mode):
    b = blob(stage, path)
    if b is None:
        return "MISSING"
    try:
        t = probe_js_wrapper(b)[0] if mode == "js" else probe_json(b)
        return t[0] if t else "no-ts"
    except Exception as e:
        return f"parse-err:{type(e).__name__}"

# --- REPORT twins: decide side ONCE from the .json face, both files take same side (r327/r329) ---
pj = "docs/daily_report/REPORT-2026-09-28.json"
pm = "docs/daily_report/REPORT-2026-09-28.md"
bj2, bj3 = blob("2", pj), blob("3", pj)
t2, t3 = probe_json(bj2), probe_json(bj3)
if t3 and (t2 is None or t3[0] > t2[0]):
    twin_side = 3
elif t2 is None and t3 is None:
    twin_side = 2
else:
    twin_side = 2  # tie or t2 newer -> origin/HEAD
for p in (pj, pm):
    win = bj2 if p == pj and twin_side == 2 else (bj3 if p == pj and twin_side == 3 else blob(str(twin_side), p))
    with open(f"{ROOT}\\{p}", "wb") as f:
        f.write(win)
    if p.endswith(".json"):
        json.loads(win.decode("utf-8-sig"))
    assert b"<<<<<<<" not in win, f"conflict marker: {p}"
    results.append((p, f"twin take-:{twin_side}:", f"json-probe2={t2} probe3={t3}"))

# --- remaining 5 snapshot/js faces ---
resolve_snapshot("results/dashboard_status.js", mode="js")
resolve_snapshot("results/dashboard_status.json")
resolve_snapshot("results/fundamental_b_layer_filter.json")
resolve_snapshot("results/scorecard_v1.json")
resolve_snapshot("results/strategy_scorecard.json")

for r in results:
    print(" | ".join(str(x) for x in r))
print(f"RESOLVED {len(results)} faces, all parse-verified, zero conflict markers")
