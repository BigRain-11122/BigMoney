"""r159 bm-c rebase resolve: 13-UU S6 snapshot family (canon r155/r158 paradigm).

Sides: stage2=ours (bm-c HEAD, S6 ran 11:21-11:23), stage3=theirs (origin bm-b
r378 S6 ran ~11:0x + autofill self-commit). Rules:
  - generated/asof ts probe -> take-newer face
  - no-probe face -> theirs (landed-side default, r155 precedent)
  - update_status / lhb / futures -> max-cutoff take-new
  - compute_audit -> latest ts-newer + history ts-key union
  - token_usage -> max-cutoff
  - REPORT md twin -> same side as json (coupled-twin law)
"""
import json
import subprocess

def side(path, stage):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

def probe(obj, keys=("generated", "generated_at", "asof", "updated_at", "updated", "ts", "last_run", "run_ts")):
    out = {}
    def walk(o, pfx=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and any(x in k.lower() for x in ("generated", "asof", "updated_at", "last_run", "run_ts")) and len(v) >= 10:
                    out[pfx + k] = v
                elif isinstance(v, (dict, list)):
                    walk(v, pfx + k + ".")
        elif isinstance(o, list):
            for i, v in enumerate(o[:8]):
                walk(v, pfx + str(i) + ".")
    walk(obj)
    return out

UU = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
MAX_CUTOFF = ["results/update_status.json", "results/lhb_update_status.json",
              "results/futures_update_status.json", "results/token_usage.json"]
TS_NEW = ["docs/daily_report/REPORT-2026-09-28.json", "results/dashboard_status.json",
          "results/fundamental_b_layer_filter.json", "results/regime_state.json",
          "results/scorecard_v1.json", "results/strategy_scorecard.json"]
TWIN = {"docs/daily_report/REPORT-2026-09-28.md": "docs/daily_report/REPORT-2026-09-28.json",
        "results/dashboard_status.js": "results/dashboard_status.json"}
decisions = {}

def jload(txt):
    try:
        return json.loads(txt)
    except Exception:
        return None

for f in UU:
    ours, theirs = side(f, 2), side(f, 3)
    jo, jt = jload(ours), jload(theirs)
    if f in MAX_CUTOFF:
        # max cutoff: latest data cutoff / latest ts wins
        def cut(j):
            if not isinstance(j, dict):
                return ""
            cands = []
            for k in ("cutoff", "data_cutoff", "last_cutoff", "cutoff_date"):
                v = j.get(k)
                if isinstance(v, str):
                    cands.append(v)
            for k in ("last_run", "updated_at", "ts"):
                v = j.get(k)
                if isinstance(v, str):
                    cands.append(v)
            return max(cands) if cands else ""
        co, ct = cut(jo), cut(jt)
        win = "ours" if co >= ct else "theirs"
        decisions[f] = "max-cutoff ours=%s theirs=%s -> %s" % (co, ct, win)
    elif f == "results/compute_audit.json":
        lo, lt = jo.get("latest", {}), jt.get("latest", {})
        to = lo.get("ts", ""); tt = lt.get("ts", "")
        latest = lo if to >= tt else lt
        ho = {h.get("ts"): h for h in jo.get("history", [])}
        ht = {h.get("ts"): h for h in jt.get("history", [])}
        merged = dict(ho); merged.update(ht)
        newj = {"latest": latest, "history": sorted(merged.values(), key=lambda h: h.get("ts", ""))}
        for k, v in jo.items():
            if k not in ("latest", "history"):
                newj[k] = v
        with open(f, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(newj, fh, ensure_ascii=False, indent=1)
        decisions[f] = "audit latest %s>=%s ->%s + history union %d+%d->%d" % (
            to, tt, "ours" if to >= tt else "theirs", len(ho), len(ht), len(merged))
        continue
    elif f in TS_NEW:
        po, pt = probe(jo), probe(jt)
        so = sorted(po.values()); st = sorted(pt.values())
        win = "ours" if (so and (not st or so[-1] >= st[-1])) else ("theirs" if st else "theirs")
        decisions[f] = "ts-probe ours_top=%s theirs_top=%s -> %s" % (
            so[-1] if so else "NONE", st[-1] if st else "NONE", win)
    elif f in TWIN:
        continue  # handled after json side decided
    else:
        win = "theirs"
        decisions[f] = "no-probe default theirs"
    if f in TWIN or f in MAX_CUTOFF or f in TS_NEW:
        if f in TWIN:
            continue
        content = ours if win == "ours" else theirs
        with open(f, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)

# twins follow their json side (coupled-twin law)
for twin, main_f in TWIN.items():
    win = "theirs"
    d = decisions.get(main_f, "")
    if "-> ours" in d:
        win = "ours"
    content = side(twin, 2) if win == "ours" else side(twin, 3)
    with open(twin, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    decisions[twin] = "twin-same-side as %s (%s)" % (main_f, win)

print("=== resolve decisions ===")
for f in UU:
    print(f, "|", decisions.get(f, "?"))
# verify all parseable (json faces)
bad = []
for f in UU:
    if f.endswith(".json"):
        if jload(open(f, encoding="utf-8").read()) is None:
            bad.append(f)
print("parse-verify:", "ALL OK" if not bad else "BAD=%s" % bad)
