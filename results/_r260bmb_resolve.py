"""r260 bm-b push-collision 12-UU resolver (skill recipes, classify-first law).

Sides in rebase UU: :2 = bm-a upstream (round 256 close, S6 legs 16:19-16:20),
:3 = bm-b replay (this round 260, S6 legs 16:27-16:29). Probe verdict: bm-b
newer on every snapshot face. Recipes per classify_conflicts.py output:
  snapshot x7 (dashboard .json/.js pair, fundamental, futures, heat, lhb,
  token, update_status, daily_report json+md pair) -> take :3 whole
  rolling-ledger x2 (compute_audit history, regime_state transitions/history)
  -> identity-union zero-loss + newest snapshot fields from :3
Fail-closed: every write parse-verified; union row-count asserted == |A u B|.
"""
import json
import subprocess

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%s:%s" % (stage, path)], capture_output=True)
    assert r.returncode == 0, (stage, path)
    return r.stdout

def load(stage, path):
    return json.loads(blob(stage, path).decode("utf-8-sig"))

def ident(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False)

def union_rows(a, b):
    """identity-union preserving first-seen order (a first, then b-new), zero loss"""
    seen, out = set(), []
    for row in list(a) + list(b):
        k = ident(row)
        if k not in seen:
            seen.add(k)
            out.append(row)
    return out, len(out), len(seen)

def write_mirror(path, obj, base_raw):
    """probe base blob EOL+indent, write back mirrored (r223/r234 law)"""
    txt = base_raw.decode("utf-8-sig")
    crlf = "\r\n" in txt
    lines = txt.split("\n")
    indent = 0
    for ln in lines[1:]:
        if ln.strip():
            indent = len(ln) - len(ln.lstrip())
            break
    body = json.dumps(obj, ensure_ascii=False, indent=indent or None)
    if indent == 0:
        body = json.dumps(obj, ensure_ascii=False)
    nl = "\r\n" if crlf else "\n"
    if txt.endswith("\n"):
        body += nl
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(body)

TAKE3_WHOLE = [
    "docs/daily_report/REPORT-2026-09-26.json",
    "docs/daily_report/REPORT-2026-09-26.md",   # md same side as json twin (r242)
    "results/dashboard_status.js",             # js-wrapper: whole-byte take (R209)
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
]

for p in TAKE3_WHOLE:
    raw3 = blob("3", p)
    with open(p, "wb") as f:
        f.write(raw3)
    if p.endswith(".json"):
        json.loads(raw3.decode("utf-8-sig"))   # parse-verify (r185)
    print("take-3 whole: %s (%dB)" % (p, len(raw3)))

# --- compute_audit.json: history union + latest take-3 ---
p = "results/compute_audit.json"
a, b = load("2", p), load("3", p)
rows, n_union, n_seen = union_rows(a["history"], b["history"])
assert n_union == n_seen == len({ident(r) for r in list(a["history"]) + list(b["history"])})
merged = dict(a)                      # base = upstream face
merged.update({k: v for k, v in b.items() if k != "history"})   # newest fields
merged["history"] = rows
write_mirror(p, merged, blob("2", p))
json.loads(open(p, encoding="utf-8-sig").read())
print("compute_audit: history union %d+%d -> %d rows; latest.ts=%s" %
      (len(a["history"]), len(b["history"]), n_union, merged["latest"]["ts"]))

# --- regime_state.json: transitions/history union + state fields take-3 ---
p = "results/regime_state.json"
a, b = load("2", p), load("3", p)
for key in ("transitions", "history", "triggers"):
    if key in a or key in b:
        rows, n_union, n_seen = union_rows(a.get(key, []), b.get(key, []))
        assert n_union == n_seen
        a[key] = rows
        print("regime_state %s: union -> %d rows" % (key, n_union))
merged = dict(a)
merged.update({k: v for k, v in b.items() if k not in ("transitions", "history", "triggers")})
write_mirror(p, merged, blob("2", p))
json.loads(open(p, encoding="utf-8-sig").read())
print("regime_state: state fields take-3 (updated=%s, state=%s)" %
      (merged.get("updated"), merged.get("state")))

print("resolver done: 12/12")
