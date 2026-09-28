"""r404 bm-b S0 pull--rebase resolver: 11-UU vs origin/main (bm-a r408 + bm-c autofill ticks).

Classifier 7/11 + 4 UNKNOWN manually classified as snapshot (same-day idempotent regen docs:
daily_report.py / ceo_live_usage.py regenerate REPORT/LIVE-2026-09-29 in place every run).
Recipes: rolling-ledger union (compute_audit by (ts,host); regime_state by asof) + latest
take-new by deep wallclock ts; snapshots take-new by blob ts (batch-72 law: side by BLOB ts,
never identity). MD doc twins take the same side as their JSON twin.
"""
import json
import re
import subprocess

TS_RE = re.compile(r"^20\d{2}-")
CLOCK_RE = re.compile(r"[T ]\d{2}:\d{2}")


def blob(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True).stdout


def deep_wallclock(obj):
    best = None

    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    nk = k.replace("_", "").replace("-", "").lower()
                    if any(nk.startswith(p) for p in ("asof", "updated", "generated", "ts", "last")):
                        if TS_RE.match(v) and CLOCK_RE.search(v):
                            if best is None or v > best:
                                best = v
                walk(v)
        elif isinstance(o, list):
            for it in o:
                walk(it)

    walk(obj)
    return best


def dump_conv(raw):
    obj = json.loads(raw)
    text = raw.decode("utf-8")
    for indent in (1, 2, 3, 4):
        for ea in (False, True):
            for trail in ("", "\n"):
                cand = json.dumps(obj, ensure_ascii=ea, indent=indent) + trail
                if cand == text:
                    return obj, dict(indent=indent, ensure_ascii=ea, trail=trail)
    return obj, dict(indent=2, ensure_ascii=False, trail="\n")


report = []


def snapshot_take_new(path):
    o2, o3 = blob(2, path), blob(3, path)
    t2 = deep_wallclock(json.loads(o2)) if o2.strip() else None
    t3 = deep_wallclock(json.loads(o3)) if o3.strip() else None
    side = "theirs" if (t3 or "") > (t2 or "") else "ours"  # take-NEW by blob ts; tie -> ours (r140)
    raw = o3 if side == "theirs" else o2
    obj, conv = dump_conv(raw)
    text = json.dumps(obj, ensure_ascii=conv["ensure_ascii"], indent=conv["indent"]) + conv["trail"]
    open(path, "w", encoding="utf-8", newline="").write(text)
    json.loads(open(path, encoding="utf-8").read())
    report.append(f"{path}: snapshot side={side} ts2={t2} ts3={t3}")
    return side


# ---- 1) plain snapshots ----
for p in [
    "results/update_status.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/fundamental_b_layer_filter.json",
]:
    snapshot_take_new(p)

# ---- 2) same-day regen docs: decide side on json twin, apply to md too ----
for jpath, mpath in [
    ("docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md"),
    ("docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md"),
]:
    side = snapshot_take_new(jpath)
    raw = blob(3 if side == "theirs" else 2, mpath)
    open(mpath, "wb").write(raw)
    report.append(f"{mpath}: took {side} (twin decided)")

# ---- 3) compute_audit.json rolling-ledger ----
p = "results/compute_audit.json"
o2, o3 = blob(2, p), blob(3, p)
a, b = json.loads(o2), json.loads(o3)
conv = dump_conv(o2)[1]


def ident(e):
    return (e.get("ts"), e.get("host"))


h2 = {ident(e): e for e in a.get("history", [])}
h3 = {ident(e): e for e in b.get("history", [])}
union = list(h2.values()) + [e for k, e in h3.items() if k not in h2]
union.sort(key=lambda e: e.get("ts", ""))
assert len(union) == len(set(map(ident, union))), "union identity collision"
la, lb = a.get("latest", {}), b.get("latest", {})
ta = deep_wallclock(la) or ""
tb = deep_wallclock(lb) or ""
merged = dict(b if tb > ta else a)  # newer latest wins; tie -> ours(=base, r140)
merged["history"] = union
text = json.dumps(merged, ensure_ascii=conv["ensure_ascii"], indent=conv["indent"]) + conv["trail"]
open(p, "w", encoding="utf-8", newline="").write(text)
json.loads(open(p, encoding="utf-8").read())
report.append(f"{p}: union={len(union)} (|A|={len(h2)} |B|={len(h3)} inter={len(set(h2) & set(h3))}) latest_side={'theirs' if tb > ta else 'ours'}")

# ---- 4) regime_state.json rolling-ledger (history by asof, transitions by ts) ----
p = "results/regime_state.json"
o2, o3 = blob(2, p), blob(3, p)
a, b = json.loads(o2), json.loads(o3)
conv = dump_conv(o2)[1]
hk = "asof"
h2 = {e.get(hk): e for e in a.get("history", [])}
h3 = {e.get(hk): e for e in b.get("history", [])}
uh = list(h2.values()) + [e for k, e in h3.items() if k not in h2]
uh.sort(key=lambda e: e.get(hk, ""))
t2 = {json.dumps(e, sort_keys=True): e for e in a.get("transitions", [])}
t3 = {json.dumps(e, sort_keys=True): e for e in b.get("transitions", [])}
ut = list(t2.values()) + [e for k, e in t3.items() if k not in t2]
merged = dict(b if (b.get("updated") or "") > (a.get("updated") or "") else a)
merged["history"] = uh
merged["transitions"] = ut
text = json.dumps(merged, ensure_ascii=conv["ensure_ascii"], indent=conv["indent"]) + conv["trail"]
open(p, "w", encoding="utf-8", newline="").write(text)
json.loads(open(p, encoding="utf-8").read())
report.append(f"{p}: hist_union={len(uh)} (|A|={len(h2)} |B|={len(h3)}) trans_union={len(ut)} updated_side={'theirs' if (b.get('updated') or '') > (a.get('updated') or '') else 'ours'}")

print("\n".join(report))
print("RESOLVE-OK all 11 files written+parsed")
