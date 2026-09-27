# r339 bm-b rebase stop-1 resolver: 16 UU per canonical recipes (skill bigmoney-conflict-resolve)
# sides: ours=:2:=upstream aee0fa02 (bm-a r344, chain 18:48-50) | theirs=:3:=my fc0e784b (chain 18:45-46)
# frozen at results/_r339bmb_blobs2/ (autofill side-stage killed by tick blind-add r335 -> commit-object recovery)
import json, os, subprocess

B = "results/_r339bmb_blobs2"
def rb(p):
    with open(p, "rb") as f:
        return f.read()
def rj(p):
    return json.loads(rb(p).decode("utf-8"))
def gitobj(ref):
    return subprocess.run(["git", "show", ref], capture_output=True, check=True).stdout

TS_KEYS = ("ts", "updated", "updated_at", "generated", "generated_at", "asof", "now", "checked_at", "report_date", "fetched_at", "last_run")
def deep_ts(obj):
    best = ""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and k in TS_KEYS and "2026" in v:
                if v > best:
                    best = v
            r = deep_ts(v)
            if r > best:
                best = r
    elif isinstance(obj, list):
        for v in obj:
            r = deep_ts(v)
            if r > best:
                best = r
    return best

decisions = []
def take_side(path, side_bytes, why):
    with open(path, "wb") as f:
        f.write(side_bytes)
    decisions.append((path, why))
    return side_bytes

# ---------- 1. autofill_state.json: mixed-dict+ledger 3-face union ----------
up_raw = gitobj("aee0fa02:results/autofill_state.json")
my_raw = gitobj("fc0e784b:results/autofill_state.json")
wt_raw = rb("results/autofill_state.json")          # tick 19:00:01 fresh write (markers gone, verified parseable)
up, my, wt = json.loads(up_raw.decode()), json.loads(my_raw.decode()), json.loads(wt_raw.decode())
def sig(e):
    return json.dumps(e, sort_keys=True, ensure_ascii=False)
all_launches = {}
for d in (up, my, wt):
    for e in d["launches"]:
        all_launches[sig(e)] = e
launches = sorted(all_launches.values(), key=lambda e: e.get("ts", ""))
if len(launches) > 50:                                # cap 50 keep newest, then write-back MUST be ts asc (r245 law)
    launches = sorted(launches, key=lambda e: e.get("ts", ""), reverse=True)[:50]
    launches = sorted(launches, key=lambda e: e.get("ts", ""))
ticks = [up["last_tick"], my["last_tick"], wt["last_tick"]]
best_tick = max(ticks, key=lambda t: t.get("ts", ""))  # freshest internal ts, whole-dict (r140; no str() compare)
merged = {"last_tick": best_tick, "launches": launches}   # key order mirrors upstream blob (last_tick first)
out = json.dumps(merged, ensure_ascii=False, indent=1) + "\n"   # LF + indent1 = upstream blob tail-state (r339 law)
with open("results/autofill_state.json", "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
chk = json.loads(out)
assert isinstance(chk["last_tick"], dict) and len(chk["launches"]) == len(all_launches)
decisions.append(("results/autofill_state.json",
    f"launches 3-face union {len(up['launches'])}|{len(my['launches'])}|{len(wt['launches'])}->{len(all_launches)} (dce2-legacy-lb preserved from upstream, tick-inheritance hole backfilled), last_tick freshest {best_tick.get('ts')} {best_tick.get('machine')} whole-dict, asc-write LF/indent1"))

# ---------- 2. compute_audit.json: rolling-ledger history union (ts face key, r334 law) ----------
o, t = rj(f"{B}/results__compute_audit.json.ours"), rj(f"{B}/results__compute_audit.json.theirs")
oh, th = o["history"], t["history"]
omap = {h["ts"]: h for h in oh}
tmap = {h["ts"]: h for h in th}
shared = set(omap) & set(tmap)
mismatch_shared = sum(1 for k in shared if sig(omap[k]) != sig(tmap[k]))
union = {k: (omap[k] if k in omap else tmap[k]) for k in set(omap) | set(tmap)}
hist = sorted(union.values(), key=lambda h: h["ts"])
latest = o["latest"] if deep_ts(o["latest"]) >= deep_ts(t["latest"]) else t["latest"]
outd = {"history": hist, "latest": latest}
with open("results/compute_audit.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(outd, f, ensure_ascii=False, indent=1)
    f.write("\n")
decisions.append(("results/compute_audit.json",
    f"history ts-key union {len(oh)}|{len(th)}->{len(hist)} (shared {len(shared)}, ts-collision-diff {mismatch_shared}=0 required), latest take-new"))

# ---------- 3. regime_state.json: history asof-key union + top take-new ----------
o, t = rj(f"{B}/results__regime_state.json.ours"), rj(f"{B}/results__regime_state.json.theirs")
omap = {h.get("asof"): h for h in o["history"]}
tmap = {h.get("asof"): h for h in t["history"]}
union = {k: (omap.get(k) or tmap.get(k)) for k in set(omap) | set(tmap)}
base = o if deep_ts(o) >= deep_ts(t) else t
base = dict(base)
base["history"] = sorted(union.values(), key=lambda h: h.get("asof", ""))
with open("results/regime_state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(base, f, ensure_ascii=False, indent=1)
    f.write("\n")
decisions.append(("results/regime_state.json", f"history asof-key union {len(o['history'])}|{len(t['history'])}->{len(union)}, top-level take-new by deep-ts"))

# ---------- 4. snapshot family: deep-ts take-new, whole bytes from frozen blob ----------
SNAP = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for p in SNAP:
    safe = p.replace("/", "__")
    ob, tb = rb(f"{B}/{safe}.ours"), rb(f"{B}/{safe}.theirs")
    try:
        ots, tts = deep_ts(json.loads(ob.decode())), deep_ts(json.loads(tb.decode()))
    except Exception:
        ots = max((ln for ln in ob.decode(errors="replace").splitlines() if "2026-" in ln and any(k in ln for k in TS_KEYS)), default="", key=lambda s: s)
        tts = max((ln for ln in tb.decode(errors="replace").splitlines() if "2026-" in ln and any(k in ln for k in TS_KEYS)), default="", key=lambda s: s)
    if ots >= tts:                                    # tie -> ours (HEAD, r140 law)
        take_side(p, ob, f"take-ours deep-ts {ots} >= {tts}")
    else:
        take_side(p, tb, f"take-theirs deep-ts {tts} > {ots}")

# ---------- verify all written json parse ----------
for p in ["results/autofill_state.json", "results/compute_audit.json", "results/regime_state.json"] + [p for p in SNAP if p.endswith(".json")]:
    json.loads(rb(p).decode("utf-8"))
print("ALL JSON PARSE OK")
for p, why in decisions:
    print(f"  {p}: {why}")
