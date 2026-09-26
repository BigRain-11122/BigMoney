"""r283 bm-b S7 rebase resolver (16 UU vs bm-a R280 03058dad).

Direction: :2 = origin base (bm-a side), :3 = bm-b replayed side (mine).
S6 dual-producer same-window race: my chain ran 00:34-00:36, bm-a's
00:27-00:29 -> take-new = bm-b verified per-file by real ts keys
(recursive probe r277 law; daily_scorecard post_review_latest data-
freshness key = legal comparison face).

Resolution map:
- whole-byte take :3 (bm-b newer, verified): 11 snapshot/json-twin files
  + dashboard_status.js (js-wrapper, byte-exact) + daily_report md (json
  twin governs, same-side whole bytes r265) + regime_state.json (only
  'updated' differs, newer = mine)
- compute_audit.json: history = union by ts (zero-loss), latest = take
  newer ts; byte-face mirror from :3 blob
- autofill_state.json: launches identical both sides; last_tick = take
  newer inner ts (r140 tie->HEAD); byte-face mirror from :3 blob
Post-write: json.loads pass on every resolved file before git add.
"""
import io
import json
import subprocess


def blob(rev):
    r = subprocess.run(["git", "show", rev], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {rev}: rc={r.returncode}")
    return r.stdout


TAKE_MINE = [
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.js",
    "results/regime_state.json",
]

# ---- whole-byte take-side files
for p in TAKE_MINE:
    b = blob(f":3:{p}")
    with io.open(p, "wb") as f:
        f.write(b)
    if p.endswith(".json"):
        json.loads(b.decode("utf-8-sig"))  # parse gate before add
    print(f"take-mine(bytes): {p} ({len(b)}B)")

# ---- compute_audit.json: history union by ts + latest take-new
a = json.loads(blob(":2:results/compute_audit.json").decode("utf-8-sig"))
b = json.loads(blob(":3:results/compute_audit.json").decode("utf-8-sig"))
ha = {r.get("ts"): r for r in a["history"] if isinstance(r, dict) and r.get("ts")}
hb = {r.get("ts"): r for r in b["history"] if isinstance(r, dict) and r.get("ts")}
union = dict(ha)
union.update(hb)
hist = sorted(union.values(), key=lambda r: r["ts"])
la, lb = a.get("latest", {}), b.get("latest", {})
latest = lb if str(lb.get("ts", "")) >= str(la.get("ts", "")) else la
out = {"latest": latest, "history": hist}
raw3 = blob(":3:results/compute_audit.json")
indent = 1
eol = b"\r\n" if b"\r\n" in raw3 else b"\n"
text = json.dumps(out, ensure_ascii=False, indent=indent)
if not raw3.endswith(b"\n"):
    text = text.rstrip("\n")
with io.open("results/compute_audit.json", "wb") as f:
    f.write(text.encode("utf-8").replace(b"\n", eol) if eol == b"\r\n"
            else text.encode("utf-8"))
json.loads(io.open("results/compute_audit.json", encoding="utf-8-sig").read())
print(f"compute_audit: history union {len(ha)}|{len(hb)} -> {len(hist)} "
      f"(zero-loss), latest ts={latest.get('ts')} "
      f"(a={la.get('ts')} b={lb.get('ts')})")

# ---- autofill_state.json: launches identical; last_tick newer-inner-ts
a = json.loads(blob(":2:results/autofill_state.json").decode("utf-8-sig"))
b = json.loads(blob(":3:results/autofill_state.json").decode("utf-8-sig"))
assert a["launches"] == b["launches"], "launches diverged: union needed"
ta, tb = str(a["last_tick"].get("ts", "")), str(b["last_tick"].get("ts", ""))
last_tick = b["last_tick"] if tb >= ta else a["last_tick"]   # tie -> base side per r140
out = {"launches": b["launches"], "last_tick": last_tick}
raw3 = blob(":3:results/autofill_state.json")
eol = b"\r\n" if b"\r\n" in raw3 else b"\n"
text = json.dumps(out, ensure_ascii=False, indent=1)
if not raw3.endswith(b"\n"):
    text = text.rstrip("\n")
data = text.encode("utf-8")
if eol == b"\r\n":
    data = data.replace(b"\n", b"\r\n")
with io.open("results/autofill_state.json", "wb") as f:
    f.write(data)
d2 = json.loads(io.open("results/autofill_state.json", encoding="utf-8-sig").read())
assert isinstance(d2["last_tick"], dict), "last_tick must stay dict"
print(f"autofill_state: launches identical ({len(b['launches'])}), "
      f"last_tick ts a={ta} b={tb} -> kept {last_tick.get('ts')}")

print("RESOLVE_OK all 16 files written + parse-gated")
