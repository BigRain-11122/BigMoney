"""R222 bm-a rebase resolver (S7 push collision, dogfood #3 of conflict skill).

Collision: bm-b r225 close (14dae719) + autofill tick claim (bea3bae7) vs my
R222 commit (bda2d43f) — 12 UU, all S6-mirror family + CODELY.md.
Rebase layout: stage2 (ours)   = origin/main (bm-b side)
              stage3 (theirs) = my R222 commit being replayed.
Recipes per classifier (12/12 GREEN, 0 UNKNOWN):
  memory-union / mixed-dict+ledger (launches union cap50, last_tick whole-dict
  by inner ts, tie->HEAD=stage2) / rolling-ledger union / js-wrapper-snapshot
  take-side whole bytes / snapshot take-new by ts.
Laws: r185 parse-verify before write-back; r140 same-second tie -> HEAD;
R208 union zero-loss; R209 wrapper byte fidelity; bm-b r223 CRLF mirror;
r209 subprocess-bytes reads (no PS redirection).
"""
import io
import json
import subprocess
import sys

def blob(spec):
    out = subprocess.run(["git", "cat-file", "-p", spec], capture_output=True, check=True)
    return out.stdout  # bytes

def detect_crlf(b):
    first_nl = b.find(b"\n")
    if first_nl == -1:
        return False
    return b[first_nl - 1:first_nl] == b"\r"

def write_mirror(path, text, base_bytes):
    nl = "\r\n" if detect_crlf(base_bytes) else "\n"
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\r\n", "\n").replace("\n", nl) if nl == "\r\n" else text)

def side_ts(obj, keys):
    for k in keys:
        v = obj.get(k) if isinstance(obj, dict) else None
        if isinstance(v, str):
            return v
    return ""

report = []

# ---- 1) CODELY.md: memory-union (stage2 lines + stage3's non-dup lines)
b2 = blob(":2:CODELY.md").decode("utf-8")
b3 = blob(":3:CODELY.md").decode("utf-8")
l2 = b2.splitlines()
set2 = set(l2)
merged = l2 + [l for l in b3.splitlines() if l not in set2]
lost = [l for l in b3.splitlines() if l in set2]  # dups are shared lines, not losses
base1 = blob(":1:CODELY.md")
write_mirror("CODELY.md", "\n".join(merged) + "\n", base1)
json.loads  # noop touch
report.append(f"CODELY.md union: {len(l2)}+{len(b3.splitlines())} -> {len(merged)} lines (dups {len(lost)} shared)")

# ---- 2) autofill_state.json: mixed-dict+ledger
a2 = json.loads(blob(":2:results/autofill_state.json").decode("utf-8"))
a3 = json.loads(blob(":3:results/autofill_state.json").decode("utf-8"))
assert isinstance(a2["last_tick"], dict) and isinstance(a3["last_tick"], dict)
la2, la3 = a2.get("launches", []), a3.get("launches", [])
uniq = {json.dumps(x, sort_keys=True, ensure_ascii=False): x for x in (la2 + la3)}
launches = sorted(uniq.values(), key=lambda x: str(x.get("ts", "")))
cap = launches[-50:]  # rolling window, R215 law
t2, t3 = str(a2["last_tick"].get("ts", "")), str(a3["last_tick"].get("ts", ""))
last_tick = a2["last_tick"] if t2 >= t3 else a3["last_tick"]  # tie -> HEAD(stage2), r140
assert isinstance(last_tick, dict)
res = {k: v for k, v in a2.items() if k not in ("launches", "last_tick")}
res["launches"] = cap
res["last_tick"] = last_tick
json.loads(json.dumps(res))  # parse-verify
write_mirror("results/autofill_state.json",
             json.dumps(res, ensure_ascii=False, indent=2) + "\n",
             blob(":1:results/autofill_state.json"))
report.append(f"autofill launches union {len(la2)}+{len(la3)} -> {len(uniq)} -> cap {len(cap)}; last_tick ts {t2} vs {t3} -> {'HEAD/bm-b' if t2 >= t3 else 'mine'}")

# ---- 3) compute_audit.json: rolling-ledger (history union + take-new fields)
c2 = json.loads(blob(":2:results/compute_audit.json").decode("utf-8"))
c3 = json.loads(blob(":3:results/compute_audit.json").decode("utf-8"))
h2, h3 = c2.get("history", []), c3.get("history", [])
seen, hist = set(), []
for row in (h2 + h3):
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        hist.append(row)
hist.sort(key=lambda r: str(r.get("ts", "")))
newer, older = (c2, c3) if str(c2.get("latest", {}).get("ts", "")) >= str(c3.get("latest", {}).get("ts", "")) else (c3, c2)
res = {k: v for k, v in newer.items() if k != "history"}
res["history"] = hist
json.loads(json.dumps(res))
write_mirror("results/compute_audit.json",
             json.dumps(res, ensure_ascii=False, indent=2) + "\n",
             blob(":1:results/compute_audit.json"))
report.append(f"compute_audit history union {len(h2)}+{len(h3)} -> {len(hist)}; fields from ts {newer.get('ts')}")

# ---- 4) regime_state.json: rolling-ledger (history+transitions union)
r2 = json.loads(blob(":2:results/regime_state.json").decode("utf-8"))
r3 = json.loads(blob(":3:results/regime_state.json").decode("utf-8"))
for key in ("history", "transitions"):
    x2, x3 = r2.get(key, []), r3.get(key, [])
    seen, merged_rows = set(), []
    for row in (x2 + x3):
        kj = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if kj not in seen:
            seen.add(kj)
            merged_rows.append(row)
    merged_rows.sort(key=lambda r: str(r.get("ts", r.get("date", ""))))
    r2[key] = merged_rows
newer = r2 if str(r2.get("asof", r2.get("ts", ""))) >= str(r3.get("asof", r3.get("ts", ""))) else r3
for k, v in newer.items():
    if k not in ("history", "transitions"):
        r2[k] = v  # state fields take-new
res = r2
json.loads(json.dumps(res))
write_mirror("results/regime_state.json",
             json.dumps(res, ensure_ascii=False, indent=2) + "\n",
             blob(":1:results/regime_state.json"))
report.append(f"regime_state union; state fields from asof {res.get('asof')}")

# ---- 5) dashboard_status.js: js-wrapper-snapshot, take-side WHOLE bytes by generated_at
j2b, j3b = blob(":2:results/dashboard_status.js"), blob(":3:results/dashboard_status.js")
for cand in (j2b, j3b):
    assert cand.startswith(b"window.DASH_DATA = {") and cand.rstrip().endswith(b"};"), "wrapper fidelity"
def dash_obj(b):
    txt = b.decode("utf-8").rstrip()
    body = txt[len("window.DASH_DATA = "):-1]  # drop trailing ';' only
    return json.loads(body)
g2 = dash_obj(j2b)["meta"]["generated_at"]
g3 = dash_obj(j3b)["meta"]["generated_at"]
win = j3b if str(g3) > str(g2) else j2b
with io.open("results/dashboard_status.js", "wb") as f:
    f.write(win)
report.append(f"dashboard_status.js take-side whole bytes: {g2} vs {g3} -> {'mine(stage3)' if win is j3b else 'bm-b(stage2)'}")

# ---- 6) plain snapshots: take-new by ts
SNAP_TS_KEYS = {
    "results/dashboard_status.json": ["meta.generated_at"],
    "results/futures_update_status.json": ["ts", "updated", "last_attempt"],
    "results/heat_update_status.json": ["ts", "updated", "l1_updated"],
    "results/lhb_update_status.json": ["ts", "updated"],
    "results/fundamental_b_layer_filter.json": ["ts", "updated", "generated"],
    "results/token_usage.json": ["generated", "ts"],
    "results/update_status.json": ["ts", "updated", "last_run"],
}
def get_nested(obj, dotted):
    cur = obj
    for part in dotted.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return ""
    return str(cur) if isinstance(cur, str) else ""

for path, keys in SNAP_TS_KEYS.items():
    s2 = json.loads(blob(f":2:{path}").decode("utf-8"))
    s3 = json.loads(blob(f":3:{path}").decode("utf-8"))
    t2 = next((get_nested(s2, k) for k in keys if get_nested(s2, k)), "")
    t3 = next((get_nested(s3, k) for k in keys if get_nested(s3, k)), "")
    win_obj = s3 if t3 > t2 else s2  # tie -> HEAD(stage2)
    json.loads(json.dumps(win_obj))
    write_mirror(path, json.dumps(win_obj, ensure_ascii=False, indent=2) + "\n",
                 blob(f":1:{path}"))
    report.append(f"{path} take-new: {t2} vs {t3} -> {'mine' if win_obj is s3 else 'bm-b/HEAD'}")

print("\n".join(report))
print("RESOLVE-OK")
