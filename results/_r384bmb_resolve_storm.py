# -*- coding: utf-8 -*-
# r384 storm resolver: 26 UU faces per canonical recipes (r383 resolver probe core reused verbatim).
# Probe STAGED blobs (:2: = origin side [bm-c r164 first-land], :3: = local side, r351 rebase law);
# tie -> origin side (r140/R208). Classes: 21 snapshot take-new (deep-ts hardened r100/R350)
# + 1 js-wrapper + REPORT twins coupled + 2 rolling-ledger union (r188/R208) + 1 append-log union (r188/r217).
# Write winner bytes to working tree; parse-verify before add (r185 law).
import json, re, subprocess

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"

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
def write_win(path, win, verify="json"):
    full = path.replace("/", "\\")
    with open(f"{ROOT}\\{full}", "wb") as f:
        f.write(win)
    if verify == "json":
        json.loads(win.decode("utf-8-sig"))
    elif verify == "js":
        assert re.search(rb"window\.DASH_DATA\s*=\s*\{.*\}\s*;?", win, re.S), "js wrapper lost"
    assert b"<<<<<<<" not in win and b">>>>>>>" not in win, f"conflict marker: {path}"

# --- REPORT twins: decide side ONCE from .json face, both files same side (r327/r329) ---
pj = "docs/daily_report/REPORT-2026-09-28.json"
pm = "docs/daily_report/REPORT-2026-09-28.md"
t2, t3 = probe_json(blob("2", pj)), probe_json(blob("3", pj))
if t3 and (t2 is None or t3[0] > t2[0]):
    twin_side = 3
elif t2 is None and t3 is None:
    twin_side = 2
else:
    twin_side = 2
for p in (pj, pm):
    win = blob(str(twin_side), p)
    write_win(p, win, verify="json" if p.endswith(".json") else "raw")
    if p.endswith(".md"):
        assert b"<<<<<<<" not in win and b">>>>>>>" not in win, f"marker: {p}"
    results.append((p, f"twin take-:{twin_side}:", f"probe2={t2[0] if t2 else None} probe3={t3[0] if t3 else None}"))

# --- snapshot faces (incl. paper_export twin pair, single-writer takeover re-derives) ---
SNAP_JSON = [
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for p in SNAP_JSON:
    b2, b3 = blob("2", p), blob("3", p)
    assert b2 is not None and b3 is not None, p
    t2, t3 = probe_json(b2), probe_json(b3)
    side = 3 if (t3 and (t2 is None or t3[0] > t2[0])) else 2
    win = b3 if side == 3 else b2
    write_win(p, win)
    results.append((p, f"take-:{side}:", f"probe2={t2[0] if t2 else 'no-ts'} probe3={t3[0] if t3 else 'no-ts'}"))

# js-wrapper
p = "results/dashboard_status.js"
b2, b3 = blob("2", p), blob("3", p)
t2, _ = probe_js_wrapper(b2)
t3, _ = probe_js_wrapper(b3)
side = 3 if (t3 and (t2 is None or t3[0] > t2[0])) else 2
write_win(p, b3 if side == 3 else b2, verify="js")
results.append((p, f"take-:{side}:", f"probe2={t2[0] if t2 else 'no-ts'} probe3={t3[0] if t3 else 'no-ts'}"))

# --- rolling-ledger unions ---
# compute_audit.json: union history by ts (zero loss), latest take-new
p = "results/compute_audit.json"
d2 = json.loads(blob("2", p).decode("utf-8-sig"))
d3 = json.loads(blob("3", p).decode("utf-8-sig"))
h2 = {e["ts"]: e for e in d2["history"]}
h3 = {e["ts"]: e for e in d3["history"]}
union = sorted({**h2, **h3}.values(), key=lambda e: e["ts"])
latest_src = d3 if deep_ts(d3["latest"])[0] > deep_ts(d2["latest"])[0] else d2
merged = {"latest": latest_src["latest"], "history": union}
out = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
write_win(p, out)
n2, n3 = len(h2), len(h3)
assert len(union) == len(set(list(h2) + list(h3))), "union count mismatch"
results.append((p, "ledger-union", f"history {n2}+{n3}->{len(union)} zero-loss | latest take-{'3' if latest_src is d3 else '2'} ({latest_src['latest']['ts']})"))

# regime_state.json: union transitions (dedupe), state fields take-new by 'updated'
p = "results/regime_state.json"
d2 = json.loads(blob("2", p).decode("utf-8-sig"))
d3 = json.loads(blob("3", p).decode("utf-8-sig"))
def entry_key(e):
    if isinstance(e, dict):
        return json.dumps(e, ensure_ascii=False, sort_keys=True)
    return str(e)
t2set = {entry_key(e) for e in d2.get("transitions", [])}
tr_union = list(d2.get("transitions", [])) + [e for e in d3.get("transitions", []) if entry_key(e) not in t2set]
newer = d3 if (d3.get("updated", "") > d2.get("updated", "")) else d2
merged = dict(newer)
merged["transitions"] = tr_union
out = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
write_win(p, out)
results.append((p, "ledger-union", f"transitions {len(d2.get('transitions', []))}+{len(d3.get('transitions', []))}->{len(tr_union)} | state take-{'3' if newer is d3 else '2'} (updated={merged.get('updated')})"))

# --- append-log union: x2_watch_log.jsonl ---
p = "results/x2_watch_log.jsonl"
l2 = blob("2", p).decode("utf-8-sig").splitlines()
l3 = blob("3", p).decode("utf-8-sig").splitlines()
seen = set(l2)
union_lines = l2 + [x for x in l3 if x not in seen]
win = ("\n".join(union_lines) + "\n").encode("utf-8")
write_win(p, win, verify="raw")
assert b"<<<<<<<" not in win and b">>>>>>>" not in win
results.append((p, "append-union", f"lines {len(l2)}+{len(l3)}->{len(union_lines)} zero-loss"))

print("RESOLVED", len(results), "faces")
for r in results:
    print(" | ".join(str(x) for x in r))
