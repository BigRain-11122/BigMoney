# r784 bm-b S7 merge resolver: 14 UU faces per canon recipes.
# Evidence (ts fields from stage2=ours / stage3=theirs blobs):
#   ours 21:44-21:56 (dead-session regen chain products) vs theirs 21:32-21:33 (bm-c r641 chain).
# Recipes:
#   - snapshot status faces (lhb/regime/fundamental/futures): ts-newer-wins -> ALL OURS
#   - REPORT/LIVE json+md twins: json ts decides, md/js twins same-side byte-copy -> OURS
#   - dashboard_status.{json,js}: host=bm-a single-writer law (r378) + bm-a alive (r794/r795
#     landed <60min) -> THEIRS (origin-verbatim), js twin follows json
#   - token_usage.json: per-key max-union (zero-loss; theirs holds fresher bm-a measurements
#     from a newer fetch face, ours holds fresher generated/bm-b face) -> deep union, ours wins
#     non-numeric leaves
import subprocess, json, os

def blob(stage, path):
    h = subprocess.run(["git", "rev-parse", "-q", "--verify", f":{stage}:{path}"],
                       capture_output=True, text=True).stdout.strip()
    if not h:
        return None
    return subprocess.run(["git", "cat-file", "blob", h],
                          capture_output=True).stdout.decode("utf-8", "replace")

def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

receipt = {"round": "r784", "faces": {}, "laws": [
    "ts-newer-wins (snapshot faces)", "md/js twins follow-json same-side (r708)",
    "dashboard host=bm-a origin-verbatim (r378 single-writer, host alive)",
    "token per-key max-union (r781 recipe, direction-agnostic)"]}

OURS = ["results/lhb_update_status.json", "results/regime_state.json",
        "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
        "docs/daily_report/REPORT-2026-10-06.json", "docs/daily_report/REPORT-2026-10-06.md",
        "docs/live_usage/LIVE-2026-10-06.json", "docs/live_usage/LIVE-2026-10-06.md",
        "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"]
THEIRS = ["results/dashboard_status.json", "results/dashboard_status.js"]
UNION = ["results/token_usage.json"]

for p in OURS:
    b = blob(2, p)
    assert b is not None, p
    write(p, b)
    receipt["faces"][p] = {"recipe": "ts-newer-wins OURS (21:44-21:56 > 21:32-21:33)",
                           "sha16": __import__("hashlib").sha256(b.encode()).hexdigest()[:16]}
for p in THEIRS:
    b = blob(3, p)
    assert b is not None, p
    write(p, b)
    receipt["faces"][p] = {"recipe": "host=bm-a origin-verbatim (r378; bm-a r795 alive)",
                           "sha16": __import__("hashlib").sha256(b.encode()).hexdigest()[:16]}

# token_usage deep union: numbers -> max, dicts -> per-key recurse, other -> ours
o = json.loads(blob(2, UNION[0]))
t = json.loads(blob(3, UNION[0]))
def deep_union(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            out[k] = deep_union(a[k], v) if k in a else v
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return max(a, b)
    return a  # ours (newer generated face)
merged = deep_union(o, t)
diff = {k: (o.get(k), t.get(k), merged.get(k)) for k in set(o) | set(t) if o.get(k) != merged.get(k)}
write(UNION[0], json.dumps(merged, ensure_ascii=False, indent=1) + "\n")
receipt["faces"][UNION[0]] = {
    "recipe": "per-key max-union (ours generated 21:56:38 base, theirs bm-a leaves larger=max-wins)",
    "keys_changed_by_union": {k: str(v[2])[:80] for k, v in diff.items()}}

# regime_state history union check (zero-loss law): if a history/transitions key exists on either
# side and the sides differ beyond the chosen base, union it.
ro = json.loads(blob(2, "results/regime_state.json"))
rt = json.loads(blob(3, "results/regime_state.json"))
hist_keys = [k for k in set(ro) | set(rt) if "hist" in k or "transition" in k]
receipt["regime_history_check"] = {k: (ro.get(k), rt.get(k)) for k in hist_keys}
for k in hist_keys:
    vo, vt = ro.get(k), rt.get(k)
    if isinstance(vo, list) and isinstance(vt, list):
        seen, un = set(), []
        for row in vo + vt:
            sig = json.dumps(row, ensure_ascii=False, sort_keys=True)
            if sig not in seen:
                seen.add(sig); un.append(row)
        if un != vo:
            ro[k] = un
            write("results/regime_state.json", json.dumps(ro, ensure_ascii=False, indent=1) + "\n")
            receipt["faces"]["results/regime_state.json"] = {
                "recipe": "base ts-newer-wins OURS + history union appended", "union_rows": len(un)}

with open("results/_r784bmb_merge_resolve.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("resolver done: OURS x%d, THEIRS x%d, UNION x1" % (len(OURS), len(THEIRS)))
print("union keys changed:", list(diff.keys()))
