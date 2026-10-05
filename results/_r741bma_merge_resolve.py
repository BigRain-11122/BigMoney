# -*- coding: utf-8 -*-
"""r741 bm-a close-window merge resolver (19-UU): r742 bloodline.
Rules: CODELY block-union (r706) + twin-same-side (r708) + ts-newer-wins
with format normalization (r709/r711) + compute_audit rolling union +
token per-key max-union. Stage blobs read via ls-files -u sha + cat-file
(r710 law: python bytes face; r516: git show :N: syntax dead on this box).
Post-write re-read assertions (r704 law). Receipt -> results/_r741bma_merge_resolve.json
"""
import subprocess, json, io, os
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__)) and r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

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

receipt = {"ts": "2026-10-05T20:0x+08:00", "ours": "HEAD r741 close (bm-a)",
           "theirs": "origin/main (bm-b r743 + bm-c r567/r568 + autofill keepalives)",
           "faces": {}}

# ---------- 1. CODELY.md block-union (r706) ----------
p = "CODELY.md"
st = stages(p)
ours_b = blob(st["2"]).decode("utf-8")
theirs_b = blob(st["3"]).decode("utf-8")

def blocks(text):
    lines = text.split("\n")
    cur = []
    out = []
    for ln in lines:
        if ln.lstrip().startswith("- ["):
            if cur:
                out.append("\n".join(cur))
            cur = [ln]
        elif cur is not None:
            cur.append(ln)
    if cur:
        out.append("\n".join(cur))
    # header = text before first block
    first = text.find("\n- [")
    header = text[: first + 1] if first >= 0 else text
    return header, out

h_ours, b_ours = blocks(ours_b)
h_theirs, b_theirs = blocks(theirs_b)
seen = set()
union = []
for b in b_ours:
    key = b[:80]
    union.append(b)
    seen.add(key)
added_theirs = 0
for b in b_theirs:
    key = b[:80]
    if key not in seen:
        union.append(b)
        seen.add(key)
        added_theirs += 1
merged = h_ours + "\n".join([""] + [b for b in union]) if not h_ours.endswith("\n") else h_ours + "\n".join(union)
io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n").write(merged if merged.endswith("\n") else merged + "\n")
receipt["faces"][p] = {"rule": "block-union r706", "ours_blocks": len(b_ours),
                       "theirs_blocks": len(b_theirs), "theirs_appended": added_theirs,
                       "union_total": len(union)}
print(f"CODELY: block-union ours={len(b_ours)} theirs={len(b_theirs)} appended={added_theirs} total={len(union)}")

# ---------- 2. ts-newer-wins faces + twins ----------
def resolve_ts_face(p, ts_keys=(), side_expect=None):
    st = stages(p)
    o = json.loads(blob(st["2"]))
    t = json.loads(blob(st["3"]))
    ko, to_ = get_ts(o, ts_keys)
    kt, tt = get_ts(t, ts_keys)
    side = "ours" if (to_ and (not tt or to_ >= tt)) else "theirs"
    if side_expect and side != side_expect and not (to_ and tt and to_ == tt):
        print(f"  WARN {p}: derived {side} != expect {side_expect} (ours {to_} vs theirs {tt})")
    data = o if side == "ours" else t
    body = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n").write(body)
    # r704 re-read assertion
    chk = json.load(io.open(os.path.join(ROOT, p), encoding="utf-8"))
    kchk, tchk = get_ts(chk, ts_keys)
    want = to_ if side == "ours" else tt
    assert tchk == want, f"{p}: re-read ts drift {tchk} != {want}"
    receipt["faces"][p] = {"rule": "ts-newer-wins", "key": ko, "ours": str(to_), "theirs": str(tt), "side": side}
    return side

twins = {
    "docs/daily_report/REPORT-2026-10-05.json": ["docs/daily_report/REPORT-2026-10-05.md"],
    "docs/live_usage/LIVE-2026-10-05.json": ["docs/live_usage/LIVE-2026-10-05.md"],
    "docs/live_usage/LIVE-latest.json": ["docs/live_usage/LIVE-latest.md"],
    "results/dashboard_status.json": ["results/dashboard_status.js"],
}
for jp, twn in twins.items():
    side = resolve_ts_face(jp)
    st = stages(jp)
    src = blob(st["2"] if side == "ours" else st["3"])
    for tp in twn:
        # raw bytes copy for twins (md/js follow json decision, r708)
        io.open(os.path.join(ROOT, tp), "wb").write(src if tp.endswith(".json") else blob(stages(tp)["2" if side == "ours" else "3"]))
        receipt["faces"][tp] = {"rule": "twin-follows-json r708", "side": side}
    print(f"{jp}: side={side} twins synced ({len(twn)})")

for p in ["results/_attrition_guard_scan.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/lhb_update_status.json",
          "results/scorecard_v1.json", "results/strategy_scorecard.json",
          "results/update_status.json", "results/regime_state.json"]:
    side = resolve_ts_face(p)
    print(f"{p}: side={side}")

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
receipt["faces"][p] = {"rule": "rolling-union", "ours": len(o["history"]), "theirs": len(t["history"]),
                       "union": len(merged), "latest_ts": latest.get("ts")}
print(f"compute_audit: union {len(o['history'])}+{len(t['history'])} -> {len(merged)} latest {latest.get('ts')}")

# ---------- 4. token_usage per-key max-union ----------
p = "results/token_usage.json"
st = stages(p)
o = json.loads(blob(st["2"]))
t = json.loads(blob(st["3"]))
base, other = (o, t) if norm_ts(o.get("generated", "")) >= norm_ts(t.get("generated", "")) else (t, o)

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

# ---------- 5. verify zero UU left, write receipt ----------
r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, cwd=ROOT)
assert not r.stdout.decode().strip(), f"UU left: {r.stdout.decode()}"
io.open(os.path.join(ROOT, "results", "_r741bma_merge_resolve.json"), "w", encoding="utf-8", newline="\n").write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + "\n")
print("ALL 19 FACES RESOLVED, zero UU left, receipt written")
