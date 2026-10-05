# -*- coding: utf-8 -*-
"""r742 bm-a close-window merge resolver (5-UU): r741 bloodline subset.
Rules: ts-newer-wins with format normalization (r709/r711) + compute_audit
rolling union + token per-key max-union. Stage blobs read via ls-files -u sha
+ cat-file (r710 law: python bytes face). Post-write re-read assertions
(r704 law). Receipt -> results/_r742bma_merge_resolve.json"""
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
    return None, None

receipt = {"ts": "2026-10-05T20:4x+08:00", "ours": "HEAD r742 close (bm-a)",
           "theirs": "origin/main (bm-b/bm-c same-window waves)",
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
for p in ["results/_attrition_guard_scan.json", "results/fundamental_b_layer_filter.json",
          "results/regime_state.json"]:
    resolve_ts_face(p)

# ---------- 2. compute_audit rolling union ----------
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

# ---------- 3. token_usage per-key max-union ----------
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

# ---------- 4. verify zero UU left (file-level, r561 law), write receipt ----------
r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, cwd=ROOT)
assert not r.stdout.decode().strip(), f"UU left: {r.stdout.decode()}"
io.open(os.path.join(ROOT, "results", "_r742bma_merge_resolve.json"), "w", encoding="utf-8", newline="\n").write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + "\n")
print("ALL 5 FACES RESOLVED, zero UU left, receipt written")
