# -*- coding: utf-8 -*-
"""r743 bm-a close-window merge resolver (17-UU): r742 bloodline extended.
Rules: ts-newer-wins with format normalization (r709/r711) + compute_audit
rolling union + token per-key max-union + twin bytes-follow-same-side
(r708 law: js/md twins take their json twin's side, bytes verbatim r710 law).
Stage blobs read via ls-files -u sha + cat-file (r710 law: python bytes face).
Post-write re-read assertions (r704 law). Receipt -> results/_r743bma_merge_resolve.json"""
import subprocess, json, io, os
from datetime import datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def stages(p):
    r = subprocess.run(["git", "ls-files", "-u", "--", p], capture_output=True, cwd=ROOT)
    out = {}
    for ln in r.stdout.decode().splitlines():
        parts = ln.split()
        if len(parts) >= 4:
            out[parts[2]] = parts[1]
    return out

def blob(sha):
    return subprocess.run(["git", "cat-file", "-p", sha], capture_output=True, cwd=ROOT).stdout

def norm_ts(s):
    if not isinstance(s, str):
        return None
    try:
        return datetime.fromisoformat(s.replace(" ", "T").replace("Z", "+00:00"))
    except Exception:
        return None

def get_ts(d, extra=()):
    for k in tuple(extra) + ("generated", "updated", "ts", "generated_at", "last_run", "now"):
        if isinstance(d, dict) and k in d:
            t = norm_ts(d[k])
            if t:
                return k, t
    # nested deep audit (r720 law: no-top-level-ts faces anchor meta.generated_at)
    m = d.get("meta") if isinstance(d, dict) else None
    if isinstance(m, dict) and "generated_at" in m:
        t = norm_ts(m["generated_at"])
        if t:
            return "meta.generated_at", t
    return None, None

receipt = {"ts": "2026-10-05T21:3x+08:00", "ours": "HEAD r743 close (bm-a)",
           "theirs": "origin/main (bm-c r572 same-window wave)",
           "faces": {}}

def resolve_ts_face(p, ts_keys=()):
    st = stages(p)
    o = json.loads(blob(st["2"]))
    t = json.loads(blob(st["3"]))
    ko, to_ = get_ts(o, ts_keys)
    kt, tt = get_ts(t, ts_keys)
    assert to_ or tt, f"{p}: no ts key found on either side"
    side = "ours" if (to_ and (not tt or to_ >= tt)) else "theirs"
    data = o if side == "ours" else t
    body = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n").write(body)
    chk = json.load(io.open(os.path.join(ROOT, p), encoding="utf-8"))
    kchk, tchk = get_ts(chk, ts_keys)
    want = to_ if side == "ours" else tt
    assert tchk == want, f"{p}: re-read ts drift {tchk} != {want} (r704 law)"
    receipt["faces"][p] = {"rule": "ts-newer-wins", "key": ko, "ours": str(to_), "theirs": str(tt), "side": side}
    print(f"{p}: side={side} (ours {to_} vs theirs {tt})")
    return side

# ---------- 1. ts-newer-wins faces ----------
ts_faces = [
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/regime_state.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/update_status.json",
    "results/dashboard_status.json",
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-latest.json",
]
sides = {}
for p in ts_faces:
    sides[p] = resolve_ts_face(p)

# ---------- 2. twin bytes-follow-same-side (r708 law) ----------
twin_map = {
    "results/dashboard_status.js": "results/dashboard_status.json",
    "docs/daily_report/REPORT-2026-10-05.md": "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md": "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}
for twin, main in twin_map.items():
    st = stages(twin)
    stage_no = "2" if sides[main] == "ours" else "3"
    data = blob(st[stage_no])
    io.open(os.path.join(ROOT, twin), "wb").write(data)
    receipt["faces"][twin] = {"rule": "twin-bytes-follow", "follows": main, "side": sides[main]}
    print(f"{twin}: bytes from {sides[main]} side (follows {main})")

# ---------- 3. compute_audit rolling union ----------
p = "results/compute_audit.json"
st = stages(p)
o = json.loads(blob(st["2"]))
t = json.loads(blob(st["3"]))
oidx = {e.get("ts"): e for e in o["history"]}
tidx = {e.get("ts"): e for e in t["history"]}
merged_hist = {**oidx, **tidx}
merged = sorted(merged_hist.values(), key=lambda e: e.get("ts"))
latest = max(merged, key=lambda e: e.get("ts"))
out = {"latest": latest, "history": merged}
io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
chk = json.load(io.open(os.path.join(ROOT, p), encoding="utf-8"))
assert all(isinstance(e, dict) for e in chk["history"]), "union rows all dict (r522 law)"
receipt["faces"][p] = {"rule": "rolling-union", "ours": len(o["history"]), "theirs": len(t["history"]),
                       "union": len(merged), "latest_ts": latest.get("ts")}
print(f"compute_audit: union {len(o['history'])}+{len(t['history'])} -> {len(merged)} latest {latest.get('ts')}")

# ---------- 4. token_usage per-key max-union ----------
p = "results/token_usage.json"
st = stages(p)
o = json.loads(blob(st["2"]))
t = json.loads(blob(st["3"]))
base, other = (o, t) if (norm_ts(o.get("generated", "")) or datetime.min.replace(tzinfo=None)) >= (norm_ts(t.get("generated", "")) or datetime.min) else (t, o)

def maxmerge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            out[k] = maxmerge(out[k], v) if k in out else v
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return max(a, b)
    if isinstance(a, list) and isinstance(b, list):
        return a + [x for x in b if x not in a]
    return a  # strings: keep base (newer generated side)

merged_t = maxmerge(base, other)
io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n").write(json.dumps(merged_t, ensure_ascii=False, indent=1) + "\n")
receipt["faces"][p] = {"rule": "per-key max-union", "base_generated": base.get("generated")}
print(f"token_usage: per-key max-union (base generated {base.get('generated')})")

# ---------- 5. write receipt, THEN verify zero UU after git-add (r742 precedent: ----------
# ----------    resolver asserts pre-add; receipt-first so it always lands)      ----------
io.open(os.path.join(ROOT, "results", "_r743bma_merge_resolve.json"), "w", encoding="utf-8", newline="\n").write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + "\n")
subprocess.run(["git", "add"] + list(receipt["faces"].keys()) + ["results/_r743bma_merge_resolve.json"], cwd=ROOT)
r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, cwd=ROOT)
assert not r.stdout.decode().strip(), f"UU left after add: {r.stdout.decode()}"
print(f"ALL {len(receipt['faces'])} FACE OPS RESOLVED + staged, zero UU left, receipt written")
