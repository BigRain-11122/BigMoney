"""R267 bm-a push-replay 15-UU resolver (skill recipes, classifier 11+4 UNKNOWN hand-adjudicated).

Rebase face: :2 = origin (bm-b r271 19:57 chain + bm-c O-2000), :3 = my r267 (20:02-20:03 chain).
Facts probed before writing this file:
- snapshots/scorecards: :3 ts newer on EVERY probed face (bm-b ran 19:57 chain, mine 20:02-20:03);
  scorecard_v1 diff = /generated only; strategy_scorecard diff = /generated + /audit.elapsed_sec
  (volatile) -> deterministic content equal, take-new legal;
- REPORT json: real run-time-derived face diffs (rd counters) -> r242 precedent generated_at governs
  (mine 20:02:52 > 19:57:47), md same-side whole bytes;
- dashboard_status.js: wrapper face, meta.generated_at mine 20:03:00 > 19:57:49 -> whole-byte take :3;
- compute_audit: history 201|201 -> whole-row-identity union (parent 200 + bm-b 19:57:02 + bm-a 20:01:54
  = 202 expected), latest take-new;
- regime_state: history rows identical both sides, scalars take-new by updated ts;
- autofill_state: launches union cap-50 (r245: cap desc then write-back ASC), last_tick inner-ts compare
  (bm-a 20:00:02 > bm-b 19:50:01) whole-dict assign, tie->HEAD; isinstance(dict) assert.
"""
import subprocess, json, re

def blob(stage, f):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, f)], capture_output=True)
    assert r.returncode == 0, (stage, f, r.stderr[:200])
    return r.stdout

TAKE3 = [
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "docs/daily_report/REPORT-2026-09-26.json",
    "docs/daily_report/REPORT-2026-09-26.md",
    "results/regime_state.json",
]

def probe_face(b):
    lines = b.split(b"\n")
    indent = 0
    for ln in lines[1:6]:
        m = re.match(rb"^( +)", ln)
        if m:
            indent = len(m.group(1)); break
    has_raw_cjk = any(c >= 0x80 for c in b)
    has_uesc = b"\\u" in b
    return {
        "indent": indent,
        "ensure_ascii": (not has_raw_cjk) and has_uesc,
        "tail_nl": b.endswith(b"\n"),
        "crlf": b"\r\n" in b,
    }

def emit(obj, face):
    s = json.dumps(obj, indent=face["indent"], ensure_ascii=face["ensure_ascii"])
    b = s.encode("utf-8")
    if face["crlf"]:
        b = b.replace(b"\n", b"\r\n")
    if face["tail_nl"] and not b.endswith(b"\n"):
        b += b"\n"
    if not face["tail_nl"] and b.endswith(b"\n"):
        b = b[:-1]
    return b

# ---- 1. whole-byte take-:3 (snapshots + equal-content regen faces) ---------
for f in TAKE3:
    b3 = blob(3, f)
    if f.endswith(".json") or f.endswith(".js") and False:
        pass
    if f.endswith(".json"):
        json.loads(b3.decode("utf-8-sig"))  # parse-verify before write (r185)
    open(f, "wb").write(b3)
    print("take3 whole:", f, len(b3))

# js wrapper parse-verify
js = open("results/dashboard_status.js", "rb").read().decode("utf-8-sig")
m = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$", js, re.S)
assert m and json.loads(m.group(1)), "js wrapper verify"
print("js wrapper parse OK")

# ---- 2. compute_audit: history union + latest take-new ---------------------
f = "results/compute_audit.json"
b2, b3 = blob(2, f), blob(3, f)
d2, d3 = json.loads(b2.decode("utf-8-sig")), json.loads(b3.decode("utf-8-sig"))
h2, h3 = d2["history"], d3["history"]
seen, rows = set(), []
for r in h2 + h3:
    k = json.dumps(r, sort_keys=True)
    if k not in seen:
        seen.add(k); rows.append(r)
rows.sort(key=lambda r: r.get("ts", ""))
print("compute_audit history union:", len(h2), "|", len(h3), "->", len(rows))
assert len(rows) == len(seen) and len(rows) >= max(len(h2), len(h3))
face = probe_face(b2)
out = {"latest": d3["latest"], "history": rows}
open(f, "wb").write(emit(out, face))
json.loads(open(f, "rb").read().decode("utf-8-sig"))
print("compute_audit resolved, face:", face)

# ---- 3. autofill_state: launches union cap50 asc + last_tick ts compare ----
f = "results/autofill_state.json"
b2, b3 = blob(2, f), blob(3, f)
d2, d3 = json.loads(b2.decode("utf-8-sig")), json.loads(b3.decode("utf-8-sig"))
seen, rows = set(), []
for r in d2["launches"] + d3["launches"]:
    k = json.dumps(r, sort_keys=True)
    if k not in seen:
        seen.add(k); rows.append(r)
print("autofill launches union pre-cap:", len(rows))
rows.sort(key=lambda r: r.get("ts", ""), reverse=True)
rows = rows[:50]                      # cap semantics = keep newest 50 (r215)
rows.sort(key=lambda r: r.get("ts", ""))  # write-back order = producer append order (bm-b r245 law)
lt2, lt3 = d2["last_tick"], d3["last_tick"]
assert isinstance(lt2, dict) and isinstance(lt3, dict)
last_tick = lt3 if lt3.get("ts", "") > lt2.get("ts", "") else lt2   # inner-ts compare, tie->HEAD(:2)
open(f, "wb").write(emit({"launches": rows, "last_tick": last_tick}, probe_face(b2)))
chk = json.loads(open(f, "rb").read().decode("utf-8-sig"))
assert isinstance(chk["last_tick"], dict)
print("autofill resolved: launches", len(chk["launches"]), "last_tick.ts", chk["last_tick"]["ts"], chk["last_tick"]["machine"])

# ---- 4. re-verify every resolved file parses -------------------------------
for f in TAKE3:
    if f.endswith(".json"):
        json.loads(open(f, "rb").read().decode("utf-8-sig"))
print("ALL RESOLVED FILES PARSE-VERIFIED")
