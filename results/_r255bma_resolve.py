# -*- coding: utf-8 -*-
"""R255 bm-a rebase-replay conflict resolver (13-UU batch, 15th run of the
snapshot family). Classifier: 12 classified + 2 UNKNOWN (daily_report pair =
r242 same-day-regen precedent: json twin generated_at decides, md twin same
side whole bytes). Recipes per skill bigmoney-conflict-resolve:
- take-new snapshots (ts probe from both blobs, fail-closed on missing ts):
  futures/heat/lhb/update_status/fundamental_blf/token_usage/dashboard
  json+js twins (js follows json side, R209/R253 law)/daily_report pair
- rolling-ledger unions: compute_audit history (201|201->202 zero loss),
  regime_state transitions+history union + state fields take-new
- mixed-dict+ledger: autofill_state launches union -> cap 50 by ts desc ->
  re-sort ts ASC before write-back (r245 ORDER law) + last_tick by inner ts
  (:2 15:50:01 vs :3 15:50:02 -> :3 newer, whole dict)
- memory-union: CODELY.md line-level union (ours order + theirs-only lines)
Commit-time order: bm-b fa6c0f31 15:55:05 < bm-a 70f29342 15:59:55 (replay
legal, no yield). All JSON parse-verified before write-back (r185 law).
"""
import json
import subprocess
import io

def blob(side, path):
    b = subprocess.run(["git", "show", f":{side}:{path}"],
                       capture_output=True).stdout
    if not b:
        raise RuntimeError(f"empty blob :{side}:{path}")
    return b

def jload(side, path):
    return json.loads(blob(side, path))

def ts_of(d, keys):
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v:
            return v
    return None

TS_KEYS = ["updated", "generated", "generated_at", "last_attempt", "ts",
           "updated_at", "as_of"]

def take_new(path, ts_keys=TS_KEYS, extra=None):
    """Snapshot take-new: both sides parsed, ts probed from both, newer side
    whole raw bytes written. Fail-closed if either side lacks a ts."""
    a2, a3 = jload(2, path), jload(3, path)
    keys = ts_keys + (extra or [])
    t2 = ts_of(a2, keys)
    t3 = ts_of(a3, keys)
    assert t2 and t3, f"{path}: ts probe missing (t2={t2} t3={t3}) -- UNKNOWN"
    side = 3 if t3 >= t2 else 2
    raw = blob(side, path)
    json.loads(raw)                      # parse-verify before write
    with io.open(path, "wb") as fh:
        fh.write(raw)
    print(f"  {path}: take :{side} (t2={t2} t3={t3})", flush=True)

def union_rows(rows2, rows3, sort_key):
    seen = set()
    out = []
    for r in rows2 + rows3:
        k = json.dumps(r, ensure_ascii=False, sort_keys=True)
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    out.sort(key=lambda r: r.get(sort_key) or "")
    return out

def mirror_fmt_write(path, obj, base_side=2):
    """Write obj mirroring base-side blob format faces (EOL/indent/ascii)."""
    base = blob(base_side, path)
    indent = 1
    for ln in base.decode("utf-8").splitlines()[1:3]:
        if ln.startswith(" "):
            indent = len(ln) - len(ln.lstrip(" "))
            break
    nl = "\r\n" if b"\r\n" in base else "\n"
    ensure_ascii = b"\\u" in base
    s = json.dumps(obj, ensure_ascii=ensure_ascii, indent=indent)
    if s.endswith("\n"):
        s = s[:-1]
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(s + nl)

# ---------------- snapshots (take-new)
for p in ["results/futures_update_status.json", "results/heat_update_status.json",
          "results/lhb_update_status.json", "results/update_status.json",
          "results/fundamental_b_layer_filter.json", "results/token_usage.json"]:
    take_new(p)

# dashboard pair: json decides by meta.generated_at, js twin same side whole
d2, d3 = jload(2, "results/dashboard_status.json"), jload(3, "results/dashboard_status.json")
t2, t3 = d2["meta"]["generated_at"], d3["meta"]["generated_at"]
side = 3 if t3 >= t2 else 2
for p in ["results/dashboard_status.json", "results/dashboard_status.js"]:
    raw = blob(side, p)
    if p.endswith(".json"):
        json.loads(raw)
    else:
        assert raw.decode("utf-8").lstrip().startswith("window."), \
            f"{p}: js wrapper stripped (R209 law)"
    with io.open(p, "wb") as fh:
        fh.write(raw)
print(f"  dashboard pair: take :{side} (t2={t2} t3={t3})", flush=True)

# daily_report pair (UNKNOWN->r242 precedent): json generated_at decides,
# md twin same side whole bytes
r2 = jload(2, "docs/daily_report/REPORT-2026-09-26.json")
r3 = jload(3, "docs/daily_report/REPORT-2026-09-26.json")
t2, t3 = r2["generated_at"], r3["generated_at"]
side = 3 if t3 >= t2 else 2
for p in ["docs/daily_report/REPORT-2026-09-26.json",
          "docs/daily_report/REPORT-2026-09-26.md"]:
    raw = blob(side, p)
    if p.endswith(".json"):
        json.loads(raw)
    with io.open(p, "wb") as fh:
        fh.write(raw)
print(f"  daily_report pair: take :{side} (t2={t2} t3={t3})", flush=True)

# ---------------- compute_audit (rolling-ledger)
c2, c3 = jload(2, "results/compute_audit.json"), jload(3, "results/compute_audit.json")
uh = union_rows(c2["history"], c3["history"], "ts")
assert len(uh) == len(c2["history"]) + len(set(
    json.dumps(r, sort_keys=True, ensure_ascii=False) for r in c3["history"])
    - set(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in c2["history"])), \
    "union row-loss check failed"
merged = {"latest": c3["latest"] if c3["latest"]["ts"] >= c2["latest"]["ts"]
          else c2["latest"], "history": uh}
mirror_fmt_write("results/compute_audit.json", merged)
print(f"  compute_audit: history {len(c2['history'])}|{len(c3['history'])}"
      f"->{len(uh)} union, latest take-new ts="
      f"{merged['latest']['ts']}", flush=True)

# ---------------- regime_state (rolling-ledger + state take-new)
g2, g3 = jload(2, "results/regime_state.json"), jload(3, "results/regime_state.json")
out = dict(g3 if g3["updated"] >= g2["updated"] else g2)     # state take-new
for k in ("transitions", "history"):
    if k in g2 or k in g3:
        out[k] = union_rows(g2.get(k, []), g3.get(k, []), "ts" if k == "history"
                            else "updated")
mirror_fmt_write("results/regime_state.json", out)
print(f"  regime_state: state take-new updated={out['updated']}, "
      f"transitions={len(out.get('transitions', []))} "
      f"history={len(out.get('history', []))}", flush=True)

# ---------------- autofill_state (mixed-dict+ledger)
a2, a3 = jload(2, "results/autofill_state.json"), jload(3, "results/autofill_state.json")
launches = union_rows(a2["launches"], a3["launches"], "ts")
launches.sort(key=lambda r: r["ts"], reverse=True)
launches = launches[:50]                       # cap 50 = keep newest (R215)
launches.sort(key=lambda r: r["ts"])           # write-back = producer ASC (r245)
lt2, lt3 = a2["last_tick"], a3["last_tick"]
last_tick = lt3 if lt3.get("ts", "") >= lt2.get("ts", "") else lt2
assert isinstance(last_tick, dict), "last_tick must stay a dict (r220 law)"
af = {"launches": launches, "last_tick": last_tick}
mirror_fmt_write("results/autofill_state.json", af)
json.loads(io.open("results/autofill_state.json", encoding="utf-8").read())
assert isinstance(json.loads(io.open("results/autofill_state.json",
        encoding="utf-8").read())["last_tick"], dict)
print(f"  autofill_state: launches union {len(a2['launches'])}|"
      f"{len(a3['launches'])}->50 cap ASC, last_tick ts={last_tick['ts']}",
      flush=True)

# ---------------- CODELY.md (memory-union)
l2 = blob(2, "CODELY.md").decode("utf-8").splitlines()
l3 = blob(3, "CODELY.md").decode("utf-8").splitlines()
seen = set(l2)
extra = [ln for ln in l3 if ln not in seen and ln.strip()]
merged_lines = l2 + [ln for ln in extra]
# keep trailing-blank structure sane: dedupe blank-line runs at end
while merged_lines and not merged_lines[-1].strip():
    merged_lines.pop()
nl2 = "\r\n" if b"\r\n" in blob(2, "CODELY.md") else "\n"
with io.open("CODELY.md", "w", encoding="utf-8", newline="") as fh:
    fh.write(nl2.join(merged_lines) + nl2)
print(f"  CODELY.md: union {len(l2)}|{len(l3)} lines, +{len(extra)} "
      f"theirs-only entries kept", flush=True)

print("RESOLVER DONE -- verify + add + rebase --continue next", flush=True)
