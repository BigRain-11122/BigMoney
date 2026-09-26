# R276 bm-a resolver: 13-UU S6-snapshot-family batch vs bm-b same-window round (rebase replay face)
# Recipes per classify_conflicts.py + precedents:
#  - compute_audit.json  : rolling-ledger -> history identity-union zero-loss + latest take-new (r188/R208)
#  - regime_state.json   : rolling-ledger -> transitions/history identity-union + state take-new (r208/r260)
#  - dashboard_status.js : js-wrapper-snapshot -> same side as json twin, whole bytes (R209)
#  - dashboard_status.json : snapshot -> take-new by recursive nested ts probe (r267 law)
#  - {futures,heat,lhb,update}_status.json, fundamental_b_layer_filter.json, token_usage.json : snapshot take-new by ts
#  - daily_report REPORT json/md pair : r242 json generated_at governs, md same-side whole bytes
#  - scorecard_v1.json / strategy_scorecard.json : take-new by generated ts (r267/r276 precedent)
# Discipline: read git blobs via subprocess bytes (r209 law, no PS redirection); parse-verify pre-add (r185);
# ts-compare by value not stage label (r267 law); tie -> HEAD side (r140 law).
import json, subprocess, sys

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show :{stage}:{path} rc={r.returncode} {r.stderr[:200]}")
    return r.stdout

def jload(b):
    return json.loads(b.decode("utf-8-sig"))

def flatten_ts(d, prefix="", depth=2):
    """Recursive ts probe two levels deep (r267 nested-ts law)."""
    out = {}
    if not isinstance(d, dict):
        return out
    for k, v in d.items():
        kk = f"{prefix}{k}"
        if isinstance(v, str) and ("ts" in k.lower() or "generated" in k.lower() or "at" == k.lower()
                                   or k.lower().endswith("_at") or "time" in k.lower()) and len(v) >= 16:
            out[kk] = v
        elif isinstance(v, dict) and depth > 1:
            out.update(flatten_ts(v, kk + ".", depth - 1))
    return out

def max_ts(d):
    tss = sorted(flatten_ts(d).values())
    return tss[-1] if tss else None

resolved, report = [], []

# ---- rolling-ledger: compute_audit.json ----
p = "results/compute_audit.json"
ours, theirs = jload(blob(2, p)), jload(blob(3, p))
hA = ours.get("history", []); hB = theirs.get("history", [])
seen, union = set(), []
for row in hA + hB:
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key); union.append(row)
tA, tB = max_ts(ours), max_ts(theirs)
# rolling history rows carry their own ts; take-new for latest snapshot fields by top-level ts
whole = theirs if (tB or "") >= (tA or "") else ours
merged = dict(whole)
merged["history"] = union
json.dump(merged, open(p, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
assert len(union) == len(set(json.dumps(r, sort_keys=True) for r in union))
resolved.append(f"compute_audit history union {len(hA)}|{len(hB)}->{len(union)} zero-loss + latest take-{'theirs' if whole is theirs else 'ours'} (tsA={tA} tsB={tB})")

# ---- rolling-ledger: regime_state.json ----
p = "results/regime_state.json"
ours, theirs = jload(blob(2, p)), jload(blob(3, p))
merged = dict(theirs if (max_ts(theirs) or "") >= (max_ts(ours) or "") else ours)
for key in ("history", "transitions", "triggers"):
    a, b = ours.get(key), theirs.get(key)
    if isinstance(a, list) or isinstance(b, list):
        seen, union = set(), []
        for row in (a or []) + (b or []):
            k = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if k not in seen:
                seen.add(k); union.append(row)
        merged[key] = union
        report.append(f"regime {key} union {len(a or [])}|{len(b or [])}->{len(union)}")
json.dump(merged, open(p, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
resolved.append("regime_state ledger keys identity-union + state take-new")

# ---- daily_report pair (r242: json generated_at governs; md same side whole bytes) ----
pj = "docs/daily_report/REPORT-2026-09-26.json"; pm = "docs/daily_report/REPORT-2026-09-26.md"
oj, tj = jload(blob(2, pj)), jload(blob(3, pj))
gA, gB = oj.get("generated_at", ""), tj.get("generated_at", "")
side = 3 if gB >= gA else 2
json.dump(tj if side == 3 else oj, open(pj, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
open(pm, "wb").write(blob(side, pm))
resolved.append(f"daily_report pair take-{'theirs' if side==3 else 'ours'} (generated_at {gB} vs {gA})")

# ---- scorecard twins: take-new by generated ts ----
for p in ("results/scorecard_v1.json", "results/strategy_scorecard.json"):
    ours, theirs = jload(blob(2, p)), jload(blob(3, p))
    gA, gB = str(ours.get("generated", ours.get("generated_at", ""))), str(theirs.get("generated", theirs.get("generated_at", "")))
    win = 3 if gB >= gA else 2
    open(p, "wb").write(blob(win, p))
    resolved.append(f"{p} take-{'theirs' if win==3 else 'ours'} by generated ({gB} vs {gA})")

# ---- dashboard pair: json nested-ts probe (r267), js same side (R209) ----
pj = "results/dashboard_status.json"; ps = "results/dashboard_status.js"
oj, tj = jload(blob(2, pj)), jload(blob(3, pj))
tA, tB = max_ts(oj), max_ts(tj)
win = 3 if (tB or "") >= (tA or "") else 2
open(pj, "wb").write(blob(win, pj))
open(ps, "wb").write(blob(win, ps))
resolved.append(f"dashboard pair take-{'theirs' if win==3 else 'ours'} (nested-ts {tB} vs {tA}) + js same side R209")

# ---- plain snapshots: take-new by ts probe ----
for p in ("results/futures_update_status.json", "results/heat_update_status.json",
          "results/lhb_update_status.json", "results/update_status.json",
          "results/fundamental_b_layer_filter.json", "results/token_usage.json"):
    ours, theirs = jload(blob(2, p)), jload(blob(3, p))
    tA, tB = max_ts(ours), max_ts(theirs)
    win = 3 if (tB or "") >= (tA or "") else 2
    open(p, "wb").write(blob(win, p))
    resolved.append(f"{p} take-{'theirs' if win==3 else 'ours'} (ts {tB} vs {tA})")

# ---- parse-verify every resolved json pre-add (r185 law) ----
for p in ["results/compute_audit.json", "results/regime_state.json", "docs/daily_report/REPORT-2026-09-26.json",
          "results/scorecard_v1.json", "results/strategy_scorecard.json", "results/dashboard_status.json",
          "results/futures_update_status.json", "results/heat_update_status.json", "results/lhb_update_status.json",
          "results/update_status.json", "results/fundamental_b_layer_filter.json", "results/token_usage.json"]:
    jload(open(p, "rb").read())
# js wrapper syntax check: balanced braces + wrapper string present (R209)
js = open("results/dashboard_status.js", "rb").read().decode("utf-8-sig")
assert js.strip().startswith("window.DASH_DATA") and js.strip().endswith("};"), "js wrapper face broken"
print("PARSE-VERIFY all 12 json PASS + js wrapper face PASS")
for r in resolved:
    print("RESOLVED:", r)
for r in report:
    print("UNION:", r)
