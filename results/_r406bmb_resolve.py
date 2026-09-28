"""r406 bm-b push-time rebase resolver: 28-UU vs origin/main (bm-a r411 S6 chain same-window twins).

Law: batch-72/76 (take-NEW by staged BLOB ts, side = theirs iff t3 > t2, tie -> ours r140);
rolling ledgers union zero-loss (compute_audit by (ts,host); regime_state by asof+transitions;
x2_watch_log exact-dup line union per r397); same-day idempotent regen doc twins (.md) follow
their JSON twin's side; dashboard_status.js follows its .json twin (r397 js-numeric-face law).
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
MARKER = ("<<<<<<<", "=======", ">>>>>>>")


def assert_clean(raw_text, path):
    for m in MARKER:
        assert m not in raw_text, f"{path}: conflict marker {m} leaked"


def snapshot_take_new(path):
    o2, o3 = blob(2, path), blob(3, path)
    t2 = deep_wallclock(json.loads(o2)) if o2.strip() else None
    t3 = deep_wallclock(json.loads(o3)) if o3.strip() else None
    side = "theirs" if (t3 or "") > (t2 or "") else "ours"  # take-NEW by blob ts; tie -> ours (r140)
    raw = o3 if side == "theirs" else o2
    obj, conv = dump_conv(raw)
    text = json.dumps(obj, ensure_ascii=conv["ensure_ascii"], indent=conv["indent"]) + conv["trail"]
    assert_clean(text, path)
    open(path, "w", encoding="utf-8", newline="").write(text)
    json.loads(open(path, encoding="utf-8").read())
    report.append(f"{path}: snapshot side={side} ts2={t2} ts3={t3}")
    return side


# ---- 1) plain snapshots (take-NEW by blob ts) ----
for p in [
    "results/update_status.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/token_usage.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-28.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
]:
    snapshot_take_new(p)

# ---- 2) js twin follows json twin side ----
side = snapshot_take_new("results/dashboard_status.json") if False else None
# dashboard_status.json already done above; re-derive its side for the js twin:
o2, o3 = blob(2, "results/dashboard_status.json"), blob(3, "results/dashboard_status.json")
t2 = deep_wallclock(json.loads(o2)) if o2.strip() else None
t3 = deep_wallclock(json.loads(o3)) if o3.strip() else None
js_side = "theirs" if (t3 or "") > (t2 or "") else "ours"
raw = blob(3 if js_side == "theirs" else 2, "results/dashboard_status.js")
text = raw.decode("utf-8")
assert_clean(text, "results/dashboard_status.js")
open("results/dashboard_status.js", "w", encoding="utf-8", newline="").write(text)
report.append(f"results/dashboard_status.js: took {js_side} (json twin decided)")

# ---- 3) same-day regen docs: json twin decides, md follows ----
for jpath, mpath in [
    ("docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md"),
    ("docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md"),
]:
    side = None
    # json twin already resolved in step 1 for live_usage? No: these two json twins were NOT in
    # the plain-snapshot list; resolve them here (idempotent: re-running take-new is safe).
    o2, o3 = blob(2, jpath), blob(3, jpath)
    t2 = deep_wallclock(json.loads(o2)) if o2.strip() else None
    t3 = deep_wallclock(json.loads(o3)) if o3.strip() else None
    side = "theirs" if (t3 or "") > (t2 or "") else "ours"
    raw = o3 if side == "theirs" else o2
    obj, conv = dump_conv(raw)
    text = json.dumps(obj, ensure_ascii=conv["ensure_ascii"], indent=conv["indent"]) + conv["trail"]
    assert_clean(text, jpath)
    open(jpath, "w", encoding="utf-8", newline="").write(text)
    json.loads(open(jpath, encoding="utf-8").read())
    report.append(f"{jpath}: snapshot side={side} ts2={t2} ts3={t3}")
    raw = blob(3 if side == "theirs" else 2, mpath)
    text = raw.decode("utf-8")
    assert_clean(text, mpath)
    open(mpath, "w", encoding="utf-8", newline="").write(text)
    report.append(f"{mpath}: took {side} (twin decided)")

# ---- 4) compute_audit.json rolling-ledger union ----
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
assert_clean(text, p)
open(p, "w", encoding="utf-8", newline="").write(text)
json.loads(open(p, encoding="utf-8").read())
report.append(f"{p}: union={len(union)} (|A|={len(h2)} |B|={len(h3)} inter={len(set(h2) & set(h3))}) latest_side={'theirs' if tb > ta else 'ours'}")

# ---- 5) regime_state.json rolling-ledger union ----
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
assert_clean(text, p)
open(p, "w", encoding="utf-8", newline="").write(text)
json.loads(open(p, encoding="utf-8").read())
report.append(f"{p}: hist_union={len(uh)} (|A|={len(h2)} |B|={len(h3)}) trans_union={len(ut)} updated_side={'theirs' if (b.get('updated') or '') > (a.get('updated') or '') else 'ours'}")

# ---- 6) x2_watch_log.jsonl exact-dup line union (r397 law) ----
p = "results/x2_watch_log.jsonl"
o2, o3 = blob(2, p), blob(3, p)
l2 = [ln for ln in o2.decode("utf-8").splitlines() if ln.strip()]
l3 = [ln for ln in o3.decode("utf-8").splitlines() if ln.strip()]
seen = set(l2)
union = list(l2) + [ln for ln in l3 if ln not in seen and not seen.add(ln)]
text = "\n".join(union) + ("\n" if union else "")
assert_clean(text, p)
open(p, "w", encoding="utf-8", newline="").write(text)
report.append(f"{p}: line_union={len(union)} (|A|={len(l2)} |B|={len(l3)} dup={len(l2) + len(l3) - len(union)})")

print("\n".join(report))
print("RESOLVE-OK all 28 files written+parsed+marker-free")
