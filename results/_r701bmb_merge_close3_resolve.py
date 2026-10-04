# r701 part-2 merge resolver (merge-state: :2:=ours, :3:=theirs per r701 lesson)
# Recipes per bigmoney-conflict-resolve SKILL.md: CODELY=memory-union(+bullet heal variant 5),
# compute_audit/regime_state=rolling-ledger union zero-loss + state take-new,
# rest=snapshot take-new by internal ts (tie->theirs=origin shared truth)
import json, re, subprocess, sys, io

def stage(idx, path):
    return subprocess.run(["git","show",f":{idx}:{path}"],capture_output=True).stdout

def pick_ts(obj, depth=0, best=""):
    if depth > 4: return best
    if isinstance(obj, dict):
        for k,v in obj.items():
            if isinstance(v,str) and k.lower() in ("ts","generated","updated","as_of","asof","scan_ts","last_scan","generated_at","updated_at","evidence_cutoff","cutoff","date","last_run","time") and re.match(r"2026-\d\d-\d\d", v):
                if v > best: best = v
            else:
                best = pick_ts(v, depth+1, best)
    elif isinstance(obj, list):
        for it in obj[:50]:
            best = pick_ts(it, depth+1, best)
    return best

LEDGERS = {}
decisions = []
def resolve(path, ledger_keys=()):
    ours_b, theirs_b = stage(2,path), stage(3,path)
    if not ledger_keys:
        # ts compare
        try:
            o_ts = pick_ts(json.loads(ours_b))
            t_ts = pick_ts(json.loads(theirs_b))
        except Exception:
            o_ts = t_ts = ""
        side = "theirs" if t_ts >= o_ts else "ours"   # tie->theirs(origin)
        out = theirs_b if side=="theirs" else ours_b
        decisions.append((path, "snapshot", f"ours={o_ts or 'NOTS'} theirs={t_ts or 'NOTS'} -> {side}"))
        return out
    o, t = json.loads(ours_b), json.loads(theirs_b)
    for key in ledger_keys:
        ol, tl = o.get(key, []), t.get(key, [])
        seen, merged = set(), []
        for e in ol + tl:
            sig = json.dumps(e, sort_keys=True, ensure_ascii=False)
            if sig not in seen:
                seen.add(sig); merged.append(e)
        merged.sort(key=lambda e: str(pick_ts(e)) or "")
        o[key] = merged
    for k in t:
        if k not in ledger_keys:
            o[k] = t[k]
    decisions.append((path, "ledger-union", f"keys={ledger_keys} merged counts " + ",".join(f"{k}:{len(o[k])}" for k in ledger_keys)))
    return (json.dumps(o, ensure_ascii=False, indent=1) + "\n").encode()

# 1. CODELY.md manual union (both entries appended at same anchor; ts order r503(23:5x) < r701(00:1x); heal bullet variant 5)
ours_c, theirs_c = stage(2,"CODELY.md").decode("utf-8"), stage(3,"CODELY.md").decode("utf-8")
o_line = [l for l in ours_c.splitlines() if l.startswith("- [2026-10-05 00:1x r701 bm-b]")]
t_line = [l for l in theirs_c.splitlines() if re.match(r"^-?\[?2026-10-04 23:5x r503 bm-c", l)]
assert len(o_line)==1 and len(t_line)==1, (len(o_line),len(t_line))
tl = t_line[0]
if not tl.startswith("- "): tl = "- " + tl  # variant 5 bullet heal (2B)
base_anchor = "- [2026-10-04 23:3x r700 bm-b]"  # last common anchor line present in both
# rebuild: ours text, insert theirs entry before our r701 entry (chronological)
r701 = o_line[0]
codely_out = ours_c.replace(r701, tl + "\n" + r701, 1)
assert tl in codely_out and r701 in codely_out
with io.open("CODELY.md","w",encoding="utf-8",newline="") as f: f.write(codely_out)
decisions.append(("CODELY.md","memory-union",f"both entries kept; r503 bullet-healed={not t_line[0].startswith('- ')}; order r503->r701"))

# 2. LIVE-latest.md (text snapshot: pick by ts regex)
o_ts = str(max(re.findall(r"2026-10-0\dT\d\d:\d\d:\d\d", stage(2,"docs/live_usage/LIVE-latest.md").decode("utf-8","replace")) or [""]))
t_ts = str(max(re.findall(r"2026-10-0\dT\d\d:\d\d:\d\d", stage(3,"docs/live_usage/LIVE-latest.md").decode("utf-8","replace")) or [""]))
side = "theirs" if t_ts >= o_ts else "ours"
with io.open("docs/live_usage/LIVE-latest.md","wb") as f: f.write(stage(3 if side=="theirs" else 2, "docs/live_usage/LIVE-latest.md"))
decisions.append(("docs/live_usage/LIVE-latest.md","snapshot(text)",f"ours={o_ts} theirs={t_ts} -> {side}"))

# 3. dashboard_status.js (js-wrapper: take-side whole bytes by inner ts)
o_js, t_js = stage(2,"results/dashboard_status.js").decode("utf-8","replace"), stage(3,"results/dashboard_status.js").decode("utf-8","replace")
o_ts = str(max(re.findall(r"2026-10-0\dT\d\d:\d\d:\d\d", o_js) or [""]))
t_ts = str(max(re.findall(r"2026-10-0\dT\d\d:\d\d:\d\d", t_js) or [""]))
side = "theirs" if t_ts >= o_ts else "ours"
with io.open("results/dashboard_status.js","wb") as f: f.write((t_js if side=="theirs" else o_js).encode("utf-8"))
decisions.append(("results/dashboard_status.js","js-wrapper take-side",f"ours={o_ts} theirs={t_ts} -> {side}"))

# 4. JSON faces
snaps = ["docs/live_usage/LIVE-latest.json","results/_attrition_guard_scan.json","results/dashboard_status.json",
         "results/fundamental_b_layer_filter.json","results/futures_update_status.json","results/lhb_update_status.json",
         "results/scorecard_v1.json","results/strategy_scorecard.json","results/token_usage.json","results/update_status.json"]
for p in snaps:
    out = resolve(p)
    json.loads(out)  # parse-verify gate before write
    with io.open(p,"wb") as f: f.write(out)
for p, keys in [("results/compute_audit.json",("history","launches")),("results/regime_state.json",("launches","transitions","history"))]:
    out = resolve(p, keys)
    json.loads(out)
    with io.open(p,"wb") as f: f.write(out)

for p, cls, note in decisions:
    print(f"{cls:22s} {p:45s} {note}")
print("RESOLVER OK", len(decisions), "files")
