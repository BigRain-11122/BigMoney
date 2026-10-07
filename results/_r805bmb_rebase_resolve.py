# r805 rebase-window conflict resolver (13 UU vs bm-c r681 concurrent S6 chains)
# Laws: r640 two-way (S6 regen newer-wins / own daemon live-wins), r773 ts-duel direction law,
# r803 precedent (compute_audit history row-union + md twin same-side), r680 token_usage recursive max-union.
# ASCII only (pit-encoding). Writes stage bytes verbatim for side-picks (no re-serialization drift).
import subprocess, json, io, os, re

def stage_bytes(n, p):
    return subprocess.run(["git", "show", ":%d:%s" % (n, p)], capture_output=True).stdout

def get_ts(d):
    for k in ("ts", "generated", "generated_at", "updated", "scan_time", "asof"):
        v = d.get(k)
        if isinstance(v, str):
            return v
    return ""

TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?")

def rmax(a, b, prefer_newer_generated=True):
    if isinstance(a, dict) and isinstance(b, dict):
        out = {}
        for k in set(a) | set(b):
            if k in a and k in b:
                out[k] = rmax(a[k], b[k], prefer_newer_generated)
            else:
                out[k] = a.get(k, b.get(k))
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return max(a, b)
    if isinstance(a, str) and isinstance(b, str):
        if a == b:
            return a
        if TS_RE.match(a) and TS_RE.match(b):
            return a if a > b else b  # ISO-ish lexical == chronological
        return a  # non-ts strings: keep upstream side (order/method prose identical or canonical)
    if a is None:
        return b
    if b is None:
        return a
    return a

TS_DUEL = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]
TWIN_FOLLOW = {
    "docs/daily_report/REPORT-2026-10-07.md": "docs/daily_report/REPORT-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md": "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}
receipt = {"round": "r805", "window": "rebase 13-UU vs bm-c r681 concurrent chains", "faces": {}}

# 1) ts-duel faces
for p in TS_DUEL:
    b2, b3 = stage_bytes(2, p), stage_bytes(3, p)
    d2, d3 = json.loads(b2.decode("utf-8", "replace")), json.loads(b3.decode("utf-8", "replace"))
    t2, t3 = get_ts(d2), get_ts(d3)
    win = 3 if t3 >= t2 else 2
    data = b3 if win == 3 else b2
    with io.open(p, "wb") as f:
        f.write(data)
    receipt["faces"][p] = {"rule": "ts-duel", "ours_ts": t2, "theirs_ts": t3, "winner": "theirs(r805)" if win == 3 else "ours(bm-c-r681)"}

# 2) md twins follow their json twin side
for p, jp in TWIN_FOLLOW.items():
    win = receipt["faces"][jp]["winner"]
    data = stage_bytes(3, p) if win.startswith("theirs") else stage_bytes(2, p)
    with io.open(p, "wb") as f:
        f.write(data)
    receipt["faces"][p] = {"rule": "twin-follow", "winner": win}

# 3) compute_audit: latest ts-duel + history row-union (r803 law)
p = "results/compute_audit.json"
d2, d3 = json.loads(stage_bytes(2, p).decode("utf-8", "replace")), json.loads(stage_bytes(3, p).decode("utf-8", "replace"))
t2, t3 = get_ts(d2.get("latest", {})), get_ts(d3.get("latest", {}))
latest = d3["latest"] if t3 >= t2 else d2["latest"]
h2, h3 = d2.get("history", []), d3.get("history", [])
seen = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in h2}
hist = list(h2)
added = 0
for r in h3:
    k = json.dumps(r, sort_keys=True, ensure_ascii=False)
    if k not in seen:
        seen.add(k)
        hist.append(r)
        added += 1
out = {"latest": latest, "history": hist}
with io.open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
receipt["faces"][p] = {"rule": "latest-tsduel+history-union", "ours_latest_ts": t2, "theirs_latest_ts": t3,
                       "latest_winner": "theirs(r805)" if t3 >= t2 else "ours(bm-c-r681)",
                       "history_ours": len(h2), "history_theirs": len(h3), "union": len(hist), "added_from_theirs": added}

# 4) token_usage: recursive max-union (r680 law)
p = "results/token_usage.json"
d2, d3 = json.loads(stage_bytes(2, p).decode("utf-8", "replace")), json.loads(stage_bytes(3, p).decode("utf-8", "replace"))
merged = rmax(d2, d3)
with io.open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
receipt["faces"][p] = {"rule": "recursive-max-union", "ours_generated": get_ts(d2), "theirs_generated": get_ts(d3)}

# 5) validate all resolved JSON faces parse (md twins are prose, excluded)
jsonn = 0
for p in list(receipt["faces"]):
    if p.endswith(".json"):
        json.load(io.open(p, encoding="utf-8"))
        jsonn += 1
receipt["validate"] = "all %d JSON faces parse OK (md twins excluded)" % jsonn

with io.open("results/_r805bmb_rebase_resolve.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print(receipt["validate"])
for p, v in receipt["faces"].items():
    print(p, "->", v.get("rule"), "| winner:", v.get("winner") or v.get("latest_winner") or "")
